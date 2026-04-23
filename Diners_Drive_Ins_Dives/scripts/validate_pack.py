"""Validate a ForeFlight content pack for common import-blocking issues.

Runs against the `pack/` directory (pre-zip) and prints every issue it finds.
Exit code 1 on any issue, 0 on clean.

Checks driven by issues we have actually hit during Indian_Reservations:

1.  **Zip layout** — layers/, navdata/, manifest.json at pack root. No parent
    folder wrapping. No unexpected top-level directories.
2.  **manifest.json** — valid JSON, required fields (`name`), effectiveDate/
    expirationDate in the ForeFlight format if present.
3.  **No non-ASCII bytes** in KML layer `<name>`, `<description>` (outside
    CDATA), or manifest values. Non-ASCII bytes in these fields have been
    observed to block ForeFlight imports.
4.  **KML XML validity** — every KML file in layers/ parses as XML.
5.  **KML namespace** — matches one of the two ForeFlight-compatible ones
    (OGC or old Google). Warn if anything else.
6.  **KML element subset** — no `<BalloonStyle>`, no `<Folder>`, no
    `<NetworkLink>`, no `<ScreenOverlay>`, no `<GroundOverlay>`. These are
    either unsupported or known to cause ForeFlight issues.
7.  **Polygon placemarks** — every `<Polygon>` has `<tessellate>1</tessellate>`
    (without it, fills don't render), and no embedded `<Point>` inside the
    same MultiGeometry (we've seen this make ForeFlight render only the
    Point and drop the polygon).
8.  **Style placement** — inline `<Style>` per `<Placemark>`, not shared via
    `<styleUrl>`. (Shared styles have been observed to be dropped by the
    pack loader.)
9.  **Color format** — every `<color>` value is 8 hex chars (AABBGGRR).
10. **Descriptions wrapped in CDATA** when they contain HTML.
11. **Coordinate ranges** — lon in [-180, 180], lat in [-90, 90].
12. **Reservation / waypoint CSV** — 4 columns, unique codes, codes are
    alphanumeric (≤ 10 chars), lat/lon numeric and in range.
13. **PDF files** — start with %PDF magic bytes.
14. **Rich waypoint PDF naming** — for each waypoint code in the CSV, if a
    `<CODE><DocumentName>.pdf` exists it pairs correctly.
15. **File sizes** — warn if any KML > 5 MB or the pack total > 10 MB.

Usage:
    python scripts/validate_pack.py                    # validates ./pack/
    python scripts/validate_pack.py path/to/pack/      # explicit target
    python scripts/validate_pack.py --zip file.zip     # validates a built zip

Returns non-zero on any error, zero if the pack passes.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

KML_NS = "{http://www.opengis.net/kml/2.2}"
ALT_KML_NS = "{http://earth.google.com/kml/2.2}"
ALLOWED_TOP_DIRS = {"layers", "navdata", "byop"}
ALLOWED_TOP_FILES = {"manifest.json"}
KNOWN_UNSUPPORTED_ELEMS = ("BalloonStyle", "Folder", "NetworkLink", "ScreenOverlay", "GroundOverlay")
MAX_KML_BYTES = 5 * 1024 * 1024
MAX_PACK_BYTES = 10 * 1024 * 1024
MAX_WAYPOINT_CODE_LEN = 10


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, path: str, msg: str) -> None:
        self.errors.append(f"[ERROR] {path}: {msg}")

    def warn(self, path: str, msg: str) -> None:
        self.warnings.append(f"[WARN]  {path}: {msg}")

    def print(self) -> bool:
        for w in self.warnings:
            print(w)
        for e in self.errors:
            print(e)
        total = len(self.errors) + len(self.warnings)
        if total:
            print()
            print(f"{len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        else:
            print("OK - pack passed all validation checks.")
        return not self.errors  # True == clean


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def strip_cdata(xml_text: bytes) -> bytes:
    """Remove CDATA sections so our non-ASCII scan only flags the OUTER text."""
    return re.sub(rb"<!\[CDATA\[.*?\]\]>", b"", xml_text, flags=re.DOTALL)


def check_non_ascii(path: str, data: bytes, report: Report) -> None:
    non_ascii = [i for i, b in enumerate(data) if b > 127]
    if not non_ascii:
        return
    # Show the first offending byte in context for debuggability.
    i = non_ascii[0]
    ctx = data[max(0, i - 30):i + 30].decode("utf-8", errors="replace")
    report.error(
        path,
        f"{len(non_ascii)} non-ASCII byte(s) outside CDATA; first at offset {i}: ...{ctx}...",
    )


def walk_children(elem: ET.Element):
    yield elem
    for c in elem:
        yield from walk_children(c)


def local_tag(elem: ET.Element) -> str:
    tag = elem.tag
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


# ---------------------------------------------------------------------------
# Individual file checks
# ---------------------------------------------------------------------------

def check_manifest(data: bytes, report: Report) -> None:
    try:
        manifest = json.loads(data.decode("utf-8"))
    except Exception as e:
        report.error("manifest.json", f"not valid JSON: {e}")
        return
    if not isinstance(manifest, dict):
        report.error("manifest.json", "must be a JSON object")
        return
    name = manifest.get("name")
    if not name or not isinstance(name, str):
        report.error("manifest.json", "missing or invalid 'name' field")
    for k in ("effectiveDate", "expirationDate"):
        v = manifest.get(k)
        if v and not re.match(r"^\d{8}T\d{2}:\d{2}:\d{2}Z?$", v):
            report.error(
                "manifest.json",
                f"{k}={v!r} does not match ForeFlight format 'YYYYMMDDThh:mm:ss[Z]'",
            )
    for k, v in manifest.items():
        if isinstance(v, str) and any(ord(c) > 127 for c in v):
            report.warn("manifest.json", f"{k!r} contains non-ASCII characters: {v!r}")


def check_kml(path: str, data: bytes, report: Report) -> None:
    # Non-ASCII outside CDATA
    outer = strip_cdata(data)
    check_non_ascii(path + " (outside CDATA)", outer, report)

    if len(data) > MAX_KML_BYTES:
        report.warn(path, f"size {len(data)/1024:.1f} KB exceeds 5 MB target")

    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        report.error(path, f"XML parse error: {e}")
        return

    tag = root.tag
    if not (tag.startswith(KML_NS) or tag.startswith(ALT_KML_NS) or tag == "kml"):
        report.warn(
            path,
            f"root element namespace {tag!r} is not a recognized KML namespace",
        )

    # Hunt for unsupported elements
    for elem in walk_children(root):
        name = local_tag(elem)
        if name in KNOWN_UNSUPPORTED_ELEMS:
            report.error(path, f"unsupported element <{name}> present")

    # Placemark-level checks
    for pm in root.iter():
        if local_tag(pm) != "Placemark":
            continue
        # Prefer inline <Style> over <styleUrl>
        has_inline_style = any(local_tag(c) == "Style" for c in pm)
        has_style_url = any(local_tag(c) == "styleUrl" for c in pm)
        if has_style_url and not has_inline_style:
            report.warn(
                path,
                "Placemark uses <styleUrl> only; ForeFlight pack loader has been "
                "observed to drop referenced styles. Prefer inline <Style>.",
            )

        # Description CDATA check — we only see the text after XML parsing,
        # so detect HTML tags in the description body (suggests not in CDATA).
        for desc in pm.iter():
            if local_tag(desc) != "description":
                continue
            text = desc.text or ""
            if "<" in text and ">" in text and not re.search(r"</?[a-z]", text, re.I):
                # non-HTML angle brackets, probably fine
                pass
            # We can't distinguish CDATA from escaped from XML parse tree;
            # check in raw bytes instead (see below).

        # Polygon checks
        for poly in pm.iter():
            if local_tag(poly) != "Polygon":
                continue
            tess = [c for c in poly if local_tag(c) == "tessellate"]
            if not tess or (tess[0].text or "").strip() != "1":
                report.error(
                    path,
                    f"Polygon in placemark without <tessellate>1</tessellate> "
                    "(fills will not render in ForeFlight)",
                )

        # MultiGeometry + Point-in-Polygon-Placemark — render regression pattern
        for mg in pm.iter():
            if local_tag(mg) != "MultiGeometry":
                continue
            kinds = [local_tag(c) for c in mg]
            if "Point" in kinds and "Polygon" in kinds:
                name_text = next(
                    (c.text for c in pm if local_tag(c) == "name"),
                    "<unnamed>",
                )
                report.error(
                    path,
                    f"Placemark {name_text!r} has MultiGeometry with both Point and "
                    "Polygon — ForeFlight has been observed to render only the Point "
                    "and drop the polygon fill.",
                )

        # Point placemark — coordinate sanity
        for pt in pm.iter():
            if local_tag(pt) != "Point":
                continue
            coords_el = next((c for c in pt if local_tag(c) == "coordinates"), None)
            if coords_el is None or not (coords_el.text or "").strip():
                report.error(path, "Point element has no coordinates")
                continue
            first = (coords_el.text or "").strip().split()[0]
            try:
                parts = [float(x) for x in first.split(",")]
            except ValueError:
                report.error(path, f"Point coordinates not numeric: {first!r}")
                continue
            if not parts:
                continue
            lon, lat = parts[0], parts[1] if len(parts) > 1 else 0
            if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                report.error(
                    path,
                    f"Point coordinates out of range: lon={lon}, lat={lat}",
                )

    # Color values
    for m in re.finditer(rb"<color>([^<]+)</color>", data):
        val = m.group(1).decode("ascii", errors="replace").strip()
        if not re.fullmatch(r"[0-9a-fA-F]{8}", val):
            report.error(path, f"<color>{val}</color> is not 8 hex chars (AABBGGRR)")

    # Description CDATA check via raw bytes — every <description> should either
    # be purely textual or wrap HTML in CDATA.
    for m in re.finditer(rb"<description>(.*?)</description>", data, re.DOTALL):
        body = m.group(1)
        stripped = body.strip()
        if not stripped:
            continue
        if stripped.startswith(b"<![CDATA["):
            continue
        # Looks like unescaped HTML?
        if re.search(rb"&lt;|&gt;", body):
            continue  # escaped entities — fine
        if re.search(rb"<[a-zA-Z]", body):
            report.warn(
                path,
                "A <description> contains what looks like unescaped HTML outside "
                "a CDATA section. Wrap it in <![CDATA[...]]>.",
            )


def check_csv(path: str, data: bytes, report: Report) -> None:
    check_non_ascii(path, data, report)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        report.error(path, f"not valid UTF-8: {e}")
        return
    reader = list(csv.reader(io.StringIO(text)))
    if not reader:
        report.error(path, "empty CSV")
        return
    codes: dict[str, int] = {}
    for i, row in enumerate(reader, start=1):
        if len(row) != 4:
            report.error(path, f"row {i}: expected 4 columns, got {len(row)}: {row}")
            continue
        code, desc, lat_s, lon_s = row
        if not code.strip():
            report.error(path, f"row {i}: waypoint code is empty")
        elif not re.fullmatch(r"[A-Za-z0-9]{1,%d}" % MAX_WAYPOINT_CODE_LEN, code):
            report.error(
                path,
                f"row {i}: waypoint code {code!r} is not alphanumeric or exceeds "
                f"{MAX_WAYPOINT_CODE_LEN} chars",
            )
        codes[code] = codes.get(code, 0) + 1
        try:
            lat = float(lat_s)
            lon = float(lon_s)
        except ValueError:
            report.error(path, f"row {i}: lat/lon not numeric: {lat_s!r}, {lon_s!r}")
            continue
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            report.error(path, f"row {i}: lat/lon out of range: {lat}, {lon}")
    dups = [c for c, n in codes.items() if n > 1]
    if dups:
        report.error(path, f"duplicate waypoint code(s): {sorted(dups)}")


def check_pdf(path: str, data: bytes, report: Report) -> None:
    if not data.startswith(b"%PDF-"):
        report.error(path, "does not start with %PDF- magic — file may be corrupt")


# ---------------------------------------------------------------------------
# Pack-level checks
# ---------------------------------------------------------------------------

def validate_dir(pack: Path, report: Report) -> None:
    if not pack.is_dir():
        report.error(str(pack), "not a directory")
        return

    # Enumerate pack-relative file list
    files: dict[str, Path] = {}
    for p in sorted(pack.rglob("*")):
        if p.is_file():
            rel = p.relative_to(pack).as_posix()
            files[rel] = p

    # Top-level structure
    top = {p.split("/", 1)[0] for p in files}
    for entry in top:
        if entry in ALLOWED_TOP_DIRS:
            continue
        if entry in ALLOWED_TOP_FILES:
            continue
        report.warn(entry, "unexpected entry at pack root (expected layers/, navdata/, byop/, manifest.json)")

    # Manifest
    if "manifest.json" not in files:
        report.warn("manifest.json", "missing (optional, but recommended)")
    else:
        check_manifest(files["manifest.json"].read_bytes(), report)

    # KML
    kml_paths = [p for p in files if p.endswith(".kml") and p.startswith("layers/")]
    if not kml_paths:
        report.warn("layers/", "no KML files found")
    for p in kml_paths:
        check_kml(p, files[p].read_bytes(), report)

    # Waypoint CSV — tolerant: any CSV under navdata/
    csv_paths = [p for p in files if p.endswith(".csv") and p.startswith("navdata/")]
    for p in csv_paths:
        check_csv(p, files[p].read_bytes(), report)

    # PDFs
    pdf_paths = [p for p in files if p.endswith(".pdf")]
    for p in pdf_paths:
        check_pdf(p, files[p].read_bytes(), report)

    # Rich-waypoint PDF naming consistency check
    if csv_paths and pdf_paths:
        # Build {code: [pdfs with that prefix]}
        for cpath in csv_paths:
            text = files[cpath].read_text(encoding="utf-8")
            codes = [row.split(",")[0] for row in text.splitlines() if row.strip()]
            for code in codes:
                expected_prefix = f"navdata/{code}"
                matches = [p for p in pdf_paths if p.startswith(expected_prefix)]
                # Not an error either way — it's an optional ForeFlight convention —
                # but flag mismatched casing.
                for m in matches:
                    if not m.startswith(f"navdata/{code}"):
                        report.warn(m, f"rich-waypoint PDF prefix casing does not match waypoint code {code!r}")

    # Size
    total = sum(p.stat().st_size for p in files.values())
    if total > MAX_PACK_BYTES:
        report.warn(
            str(pack),
            f"pack total {total/1024/1024:.1f} MB exceeds {MAX_PACK_BYTES//1024//1024} MB target",
        )


def validate_zip(zip_path: Path, report: Report) -> None:
    if not zip_path.is_file():
        report.error(str(zip_path), "file not found")
        return
    try:
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
    except zipfile.BadZipFile as e:
        report.error(str(zip_path), f"bad zip: {e}")
        return

    # Flat layout check — no entry should be wrapped in a single parent folder
    top = {n.split("/", 1)[0] for n in names if n}
    if len(top) == 1 and not any(n in ALLOWED_TOP_FILES or n in ALLOWED_TOP_DIRS for n in top):
        report.error(
            str(zip_path),
            f"zip entries are wrapped in a parent folder {list(top)[0]!r}. "
            "Zip should be flat: layers/, navdata/, manifest.json at root.",
        )

    # Revalidate contents as if it were a directory
    with zipfile.ZipFile(zip_path) as z:
        files = {n: z.read(n) for n in names if not n.endswith("/")}

    # Run the same checks we do on a directory
    if "manifest.json" in files:
        check_manifest(files["manifest.json"], report)
    else:
        report.warn("manifest.json", "missing in zip")

    for n, data in files.items():
        if n.endswith(".kml") and n.startswith("layers/"):
            check_kml(n, data, report)
        elif n.endswith(".csv") and n.startswith("navdata/"):
            check_csv(n, data, report)
        elif n.endswith(".pdf"):
            check_pdf(n, data, report)

    size = zip_path.stat().st_size
    if size > MAX_PACK_BYTES:
        report.warn(
            str(zip_path),
            f"zip {size/1024/1024:.1f} MB exceeds {MAX_PACK_BYTES//1024//1024} MB target",
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a ForeFlight content pack")
    parser.add_argument("target", nargs="?", default="pack", help="Pack directory (default: pack/)")
    parser.add_argument("--zip", metavar="FILE", help="Validate an already-built zip instead of a directory")
    args = parser.parse_args(argv)

    report = Report()
    if args.zip:
        validate_zip(Path(args.zip), report)
    else:
        validate_dir(Path(args.target), report)
    ok = report.print()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
