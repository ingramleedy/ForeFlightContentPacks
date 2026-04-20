"""Emit a separate KML layer of clickable centroid points for each reservation.

ForeFlight treats each KML in layers/ as its own toggleable layer, so this one
ships alongside Indian_Reservations.kml and can be turned on/off independently.

Each Placemark is a pure Point (no polygon) with a rich HTML description that
leads with pilot-relevant data (tribal overflight assertion, nearest airports,
overflight courtesy guidance) and follows with demographic / cultural context
from enrichment.json (Census + Wikidata).

Matches the OGC namespace and inline-style-per-placemark pattern from
ForeFlight's UserMapShapesSample.kml.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw_reservations.geojson"
ENRICHMENT = ROOT / "data" / "enrichment.json"
# Points KML lives in navdata/ (matching the SFRA pack pattern) so ForeFlight
# treats it as a waypoint layer rather than a map layer — known to interact
# better with z-ordering over polygon zones in layers/.
OUT = ROOT / "pack" / "navdata" / "Indian_Reservations_Points.kml"

AIANNHCC_LABELS = {
    "D2": "Federal American Indian Reservation",
    "D8": "Tribal Designated Statistical Area",
}

ICON_HREF = "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png"
WARN_ICON_HREF = "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"
ICON_SCALE = 0.9
WARN_ICON_SCALE = 1.1
LABEL_SCALE = 0.9


def sq_meters_to_sq_miles(m2) -> float:
    try:
        return float(m2) / 2_589_988.110336
    except (TypeError, ValueError):
        return 0.0


def fmt_int(n) -> str:
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return ""


def load_enrichment() -> dict:
    if ENRICHMENT.exists():
        return json.loads(ENRICHMENT.read_text(encoding="utf-8"))
    return {}


def describe(props: dict, enrich: dict) -> str:
    """Build the HTML description in pilot-first order."""
    name = props.get("NAME") or "Reservation"
    code = props.get("AIANNHCC") or ""
    type_label = AIANNHCC_LABELS.get(code, code or "Reservation")
    land_mi2 = sq_meters_to_sq_miles(props.get("AREALAND") or 0)

    parts = [f"<h3>{html.escape(name)}</h3>"]

    # 1. TRIBAL OVERFLIGHT ASSERTION (most pilot-relevant — render prominently with ⚠)
    assertion = enrich.get("tribal_overflight_assertion")
    if assertion:
        alt = assertion.get("altitude_ft")
        alt_txt = f"{alt:,} ft" if alt else "see details"
        summary = html.escape(assertion.get("summary", ""))
        parts.append(
            f'<p><b>&#9888; Tribal overflight assertion ({alt_txt}):</b> {summary} '
            f'<i>(See navdata PDF. Not FAA-enforced.)</i></p>'
        )

    # 2. NEAREST AIRPORTS
    airports = enrich.get("nearest_airports") or []
    if airports:
        airport_str = " &middot; ".join(
            f"<b>{html.escape(a['ident'])}</b> {a['nm']:.0f} NM"
            for a in airports[:3]
        )
        parts.append(f"<p><b>Nearest airports:</b> {airport_str}</p>")

    # 3. OVERFLIGHT COURTESY (AC 91-36D) — shown unless an explicit assertion already covers it
    if not assertion:
        parts.append(
            "<p><b>Overflight courtesy:</b> AC 91-36D suggests &ge;2,000 ft AGL over "
            "noise-sensitive tribal lands.</p>"
        )

    # 4. TYPE / STATES / AREA (one compact line)
    states = enrich.get("states") or []
    states_str = ", ".join(states) if states else ""
    meta_bits = [f"<b>Type:</b> {html.escape(type_label)}"]
    if states_str:
        meta_bits.append(f"<b>States:</b> {html.escape(states_str)}")
    meta_bits.append(f"<b>Area:</b> {land_mi2:,.0f} sq mi")
    parts.append("<p>" + " &nbsp; ".join(meta_bits) + "</p>")

    # 5. TRIBAL GOVERNMENT + RECOGNIZED DATE (Wikidata-sourced)
    wd = enrich.get("wikidata") or {}
    gov_bits = []
    if wd.get("label") and wd["label"] != name:
        gov_bits.append(f"<b>Tribal government:</b> {html.escape(wd['label'])}")
    if wd.get("federally_recognized"):
        yr = wd["federally_recognized"][:4]
        gov_bits.append(f"<b>Recognized:</b> {html.escape(yr)}")
    if gov_bits:
        parts.append("<p>" + " &nbsp; ".join(gov_bits) + "</p>")

    # 6. POPULATION / HOUSING / LANGUAGE (Census + Wikidata)
    demo_bits = []
    pop = enrich.get("population_2020")
    if pop is not None and pop > 0:
        demo_bits.append(f"<b>Pop (2020):</b> {fmt_int(pop)}")
    hu = enrich.get("housing_units_2020")
    if hu is not None and hu > 0:
        demo_bits.append(f"<b>Housing:</b> {fmt_int(hu)}")
    if wd.get("languages"):
        demo_bits.append(f"<b>Language:</b> {html.escape(wd['languages'][0])}")
    if demo_bits:
        parts.append("<p>" + " &nbsp; ".join(demo_bits) + "</p>")

    # 7. WEBSITE (Wikidata-sourced)
    if wd.get("website"):
        url = html.escape(wd["website"])
        display = url.replace("https://", "").replace("http://", "").rstrip("/")
        parts.append(f'<p><b>Website:</b> <a href="{url}">{html.escape(display)}</a></p>')

    # 8. FOOTER pointer
    parts.append(
        "<p><i>Full overflight considerations: navdata/Overflight_Considerations.pdf</i></p>"
    )

    return "".join(parts)


def centroid_latlon(props: dict, geom_json: dict) -> tuple[float, float] | None:
    intlat = props.get("INTPTLAT")
    intlon = props.get("INTPTLON")
    try:
        if intlat is not None and intlon is not None:
            return float(intlat), float(intlon)
    except (TypeError, ValueError):
        pass
    try:
        geom = shape(geom_json)
        c = geom.representative_point()
        return c.y, c.x
    except Exception:
        return None


def style_xml(warn: bool = False) -> str:
    href = WARN_ICON_HREF if warn else ICON_HREF
    scale = WARN_ICON_SCALE if warn else ICON_SCALE
    return (
        "<Style>"
        f"<IconStyle><scale>{scale}</scale>"
        f"<Icon><href>{href}</href></Icon></IconStyle>"
        f"<LabelStyle><scale>{LABEL_SCALE}</scale></LabelStyle>"
        "</Style>"
    )


def placemark_xml(name: str, desc_html: str, lat: float, lon: float, warn: bool = False) -> str:
    # drawOrder=10 so points render ABOVE the zone polygons (which use drawOrder=1).
    # ForeFlight may or may not honor <drawOrder>; the translucent polygon fill is
    # also reduced to keep pins visible either way.
    return (
        "<Placemark>"
        f"<name>{html.escape(name)}</name>"
        f"<description><![CDATA[{desc_html}]]></description>"
        "<drawOrder>10</drawOrder>"
        f"{style_xml(warn=warn)}"
        f"<Point><coordinates>{lon:.5f},{lat:.5f},0</coordinates></Point>"
        "</Placemark>"
    )


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    features = data["features"]
    enrichment = load_enrichment()
    print(f"loaded {len(features)} features; enrichment: {len(enrichment)} records")

    blobs: list[str] = []
    skipped = 0
    for feat in features:
        props = feat.get("properties") or {}
        name = props.get("NAME") or props.get("BASENAME")
        if not name:
            skipped += 1
            continue
        pt = centroid_latlon(props, feat.get("geometry"))
        if pt is None:
            skipped += 1
            continue
        lat, lon = pt
        geoid = props.get("GEOID") or props.get("AIANNHNS") or name
        enrich = enrichment.get(geoid) or {}
        warn = bool(enrich.get("tribal_overflight_assertion"))
        blobs.append(placemark_xml(name, describe(props, enrich), lat, lon, warn=warn))

    header = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        "<Document>\n"
        "<name>Indian Reservations - Points</name>\n"
        "<open>1</open>\n"
        "<description>Tappable centroid points for each federal Indian reservation. "
        "Pair with the Indian Reservations zone layer.</description>\n"
    )
    footer = "</Document>\n</kml>\n"
    body = "\n".join(blobs) + "\n"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(header + body + footer, encoding="utf-8")
    size_kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT} ({size_kb:.1f} KB); placemarks={len(blobs)}; skipped={skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
