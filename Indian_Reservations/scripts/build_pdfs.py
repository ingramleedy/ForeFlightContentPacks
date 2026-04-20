"""Render the two pack PDFs from their Markdown sources and duplicate
Special_Airspace_Tribal.pdf under the 5 rich-waypoint naming convention.

This implements a small, purpose-built Markdown subset (H1/H2/H3, bullets,
paragraphs, **bold**, *italic*, [links](url), horizontal rules) rather than
pulling in a full parser. Anything richer than that isn't needed here.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
)
from reportlab.lib.enums import TA_LEFT

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
TRIBES = CONTENT / "tribes"
NAVDATA = ROOT / "pack" / "navdata"
ENRICHMENT = ROOT / "data" / "enrichment.json"

RICH_WAYPOINTS = ["HUALAPAI", "HAVASUPAI", "NAVAJO", "TAOSPUEB", "REDLAKE"]

# Census NAME substrings to match each rich waypoint to an enrichment record.
WAYPOINT_NAME_MATCH = {
    "HUALAPAI": "Hualapai Indian Reservation",
    "HAVASUPAI": "Havasupai Reservation",
    "NAVAJO": "Navajo Nation Reservation",
    "TAOSPUEB": "Taos Pueblo",
    "REDLAKE": "Red Lake Reservation",
}


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()["BodyText"]
    return {
        "h1": ParagraphStyle(
            "h1", parent=base, fontName="Helvetica-Bold", fontSize=18,
            leading=22, spaceAfter=10, textColor=HexColor("#1f3b60"),
        ),
        "h2": ParagraphStyle(
            "h2", parent=base, fontName="Helvetica-Bold", fontSize=13,
            leading=16, spaceBefore=10, spaceAfter=6, textColor=HexColor("#1f3b60"),
        ),
        "h3": ParagraphStyle(
            "h3", parent=base, fontName="Helvetica-Bold", fontSize=11,
            leading=14, spaceBefore=8, spaceAfter=4, textColor=HexColor("#333333"),
        ),
        "body": ParagraphStyle(
            "body", parent=base, fontName="Helvetica", fontSize=10,
            leading=13, alignment=TA_LEFT, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base, fontName="Helvetica", fontSize=10,
            leading=13, leftIndent=12, spaceAfter=2,
        ),
        "em": ParagraphStyle(
            "em", parent=base, fontName="Helvetica-Oblique", fontSize=9,
            leading=12, textColor=HexColor("#555555"), spaceBefore=6,
        ),
    }


def inline_md(text: str) -> str:
    """Convert a subset of inline Markdown to ReportLab's mini-HTML."""
    # Escape & < > first so later insertions of <b>/<i>/<a> aren't double-escaped.
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Links: [text](url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2)}" color="#2b5080">{m.group(1)}</a>',
        text,
    )
    # Bold: **text**
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    # Italic: *text*
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    # Inline code not used in our docs; skip.
    return text


def parse_markdown(md: str, styles: dict[str, ParagraphStyle]) -> list:
    lines = md.splitlines()
    flow: list = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("# "):
            flow.append(Paragraph(inline_md(line[2:].strip()), styles["h1"]))
            i += 1
            continue
        if line.startswith("## "):
            flow.append(Paragraph(inline_md(line[3:].strip()), styles["h2"]))
            i += 1
            continue
        if line.startswith("### "):
            flow.append(Paragraph(inline_md(line[4:].strip()), styles["h3"]))
            i += 1
            continue
        if line.strip() == "---":
            flow.append(Spacer(1, 4))
            flow.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#bbbbbb")))
            flow.append(Spacer(1, 4))
            i += 1
            continue
        # bullet list block
        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i].rstrip()):
                raw = re.sub(r"^\s*[-*]\s+", "", lines[i].rstrip())
                items.append(ListItem(Paragraph(inline_md(raw), styles["bullet"]), leftIndent=12))
                i += 1
            flow.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=14))
            continue
        # numbered list block
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i].rstrip()):
                raw = re.sub(r"^\s*\d+\.\s+", "", lines[i].rstrip())
                items.append(ListItem(Paragraph(inline_md(raw), styles["bullet"]), leftIndent=12))
                i += 1
            flow.append(ListFlowable(items, bulletType="1", leftIndent=18))
            continue
        # paragraph — gather until blank line or block change
        para_lines = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].rstrip()
            if not nxt.strip():
                break
            if nxt.startswith(("#", "---")) or re.match(r"^\s*[-*]\s+", nxt) or re.match(r"^\s*\d+\.\s+", nxt):
                break
            para_lines.append(nxt)
            i += 1
        text = " ".join(para_lines).strip()
        style = styles["em"] if text.startswith("*") and text.endswith("*") and "**" not in text else styles["body"]
        if style is styles["em"]:
            text = text[1:-1]
        flow.append(Paragraph(inline_md(text), style))
    return flow


def render(md_path: Path, pdf_path: Path, title: str) -> None:
    styles = make_styles()
    md = md_path.read_text(encoding="utf-8")
    flow = parse_markdown(md, styles)
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=LETTER,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title=title,
        author="Ingram Leedy",
    )
    doc.build(flow)
    print(f"  wrote {pdf_path.name} ({pdf_path.stat().st_size / 1024:.1f} KB)")


def load_enrichment_by_name() -> dict[str, dict]:
    if not ENRICHMENT.exists():
        return {}
    data = json.loads(ENRICHMENT.read_text(encoding="utf-8"))
    return {(r.get("name") or ""): r for r in data.values()}


def tribe_enrichment_flow(waypoint: str, enrich: dict, styles: dict[str, ParagraphStyle]) -> list:
    """Render per-tribe facts pulled from enrichment.json into PDF flowables."""
    flow: list = [Paragraph("Quick facts", styles["h2"])]

    rows: list[str] = []
    states = enrich.get("states") or []
    if states:
        rows.append(f"<b>States:</b> {', '.join(states)}")
    if enrich.get("population_2020") is not None and enrich["population_2020"] > 0:
        rows.append(f"<b>Population (2020):</b> {enrich['population_2020']:,}")
    if enrich.get("housing_units_2020") is not None and enrich["housing_units_2020"] > 0:
        rows.append(f"<b>Housing units (2020):</b> {enrich['housing_units_2020']:,}")
    wd = enrich.get("wikidata") or {}
    if wd.get("label") and wd["label"] != enrich.get("name"):
        rows.append(f"<b>Tribal government:</b> {wd['label']}")
    if wd.get("federally_recognized"):
        rows.append(f"<b>Federally recognized:</b> {wd['federally_recognized'][:10]}")
    if wd.get("languages"):
        rows.append(f"<b>Language(s):</b> {', '.join(wd['languages'])}")
    if wd.get("website"):
        url = wd['website']
        rows.append(f'<b>Website:</b> <a href="{url}" color="#2b5080">{url}</a>')

    for r in rows:
        flow.append(Paragraph(r, styles["body"]))

    ap = enrich.get("nearest_airports") or []
    if ap:
        flow.append(Paragraph("Nearest public airports", styles["h3"]))
        for a in ap:
            flow.append(Paragraph(
                f"<b>{a['ident']}</b> &mdash; {a['name']} ({a['nm']:.1f} NM)",
                styles["body"],
            ))

    assertion = enrich.get("tribal_overflight_assertion")
    if assertion:
        flow.append(Paragraph("Tribal overflight assertion", styles["h3"]))
        alt = assertion.get("altitude_ft")
        if alt:
            flow.append(Paragraph(f"<b>Claimed minimum altitude:</b> {alt:,} ft", styles["body"]))
        flow.append(Paragraph(assertion.get("summary", ""), styles["body"]))
        if assertion.get("source"):
            flow.append(Paragraph(f"<i>Source: {assertion['source']}</i>", styles["em"]))

    return flow


def render_tribe_pdf(waypoint: str, enrich_by_name: dict, styles: dict[str, ParagraphStyle], pdf_path: Path) -> None:
    md_path = TRIBES / f"{waypoint}.md"
    if not md_path.exists():
        raise FileNotFoundError(md_path)
    md = md_path.read_text(encoding="utf-8")
    flow = parse_markdown(md, styles)

    census_name = WAYPOINT_NAME_MATCH.get(waypoint)
    enrich = enrich_by_name.get(census_name) if census_name else None
    if enrich:
        flow.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#bbbbbb")))
        flow.append(Spacer(1, 6))
        flow.extend(tribe_enrichment_flow(waypoint, enrich, styles))

    flow.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#bbbbbb")))
    flow.append(Spacer(1, 6))
    flow.append(Paragraph(
        "<i>This PDF ships inside a ForeFlight Content Pack for situational awareness "
        "only. Not a substitute for current FAA publications, sectional charts, "
        "Chart Supplement entries, or NOTAMs. See also "
        "navdata/Overflight_Considerations.pdf.</i>",
        styles["em"],
    ))

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=LETTER,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title=f"{waypoint} — Tribal Overflight",
        author="Ingram Leedy",
    )
    doc.build(flow)
    print(f"  wrote {pdf_path.name} ({pdf_path.stat().st_size / 1024:.1f} KB)")


def main() -> int:
    NAVDATA.mkdir(parents=True, exist_ok=True)
    styles = make_styles()

    overflight = NAVDATA / "Overflight_Considerations.pdf"
    special = NAVDATA / "Special_Airspace_Tribal.pdf"

    render(CONTENT / "overflight_considerations.md", overflight, "Overflight Considerations")
    render(CONTENT / "special_airspace_tribal.md", special, "Special Airspace — Tribal Lands")

    # Per-tribe rich-waypoint PDFs, keyed to waypoint code via ForeFlight's
    # <WAYPOINT_NAME><DocumentName>.pdf naming convention.
    enrich_by_name = load_enrichment_by_name()
    for wp in RICH_WAYPOINTS:
        dest = NAVDATA / f"{wp}Special_Airspace_Tribal.pdf"
        if (TRIBES / f"{wp}.md").exists():
            render_tribe_pdf(wp, enrich_by_name, styles, dest)
        else:
            # Fallback: copy the generic PDF if no per-tribe markdown stub exists.
            shutil.copyfile(special, dest)
            print(f"  fallback copied {dest.name} (no tribe stub)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
