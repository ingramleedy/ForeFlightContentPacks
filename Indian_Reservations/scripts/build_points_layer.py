"""Emit a separate KML layer of clickable centroid points for each reservation.

ForeFlight treats each KML in layers/ as its own toggleable layer, so this one
ships alongside Indian_Reservations.kml and can be turned on/off independently.

Each Placemark is a pure Point (no polygon) with the same rich HTML description
used in the zone layer — tapping a point in ForeFlight opens the detail popup.
Uses the same OGC namespace and inline-style-per-placemark pattern as the zone
KML, matching ForeFlight's UserMapShapesSample.kml.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw_reservations.geojson"
OUT = ROOT / "pack" / "layers" / "Indian_Reservations_Points.kml"

AIANNHCC_LABELS = {
    "D2": "Federal American Indian Reservation",
    "D8": "Tribal Designated Statistical Area",
}

# Small, visible orange pin to tie the points layer visually to the zone layer.
ICON_HREF = "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png"
ICON_SCALE = 0.9
LABEL_SCALE = 0.9


def sq_meters_to_sq_miles(m2) -> float:
    try:
        return float(m2) / 2_589_988.110336
    except (TypeError, ValueError):
        return 0.0


def describe(props: dict) -> str:
    code = props.get("AIANNHCC") or ""
    label = AIANNHCC_LABELS.get(code, code or "Reservation")
    land_mi2 = sq_meters_to_sq_miles(props.get("AREALAND") or 0)
    water_mi2 = sq_meters_to_sq_miles(props.get("AREAWATER") or 0)
    geoid = props.get("GEOID") or "n/a"
    lines = [
        f"<h3>{html.escape(props.get('NAME') or 'Reservation')}</h3>",
        f"<p><b>Type:</b> {label}</p>",
        f"<p><b>Land area:</b> {land_mi2:,.1f} sq mi</p>",
    ]
    if water_mi2 > 0.05:
        lines.append(f"<p><b>Water area:</b> {water_mi2:,.1f} sq mi</p>")
    lines.append(f"<p><b>GEOID:</b> {html.escape(str(geoid))}</p>")
    lines.append("<p><i>See navdata for overflight considerations.</i></p>")
    return "".join(lines)


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


def style_xml() -> str:
    return (
        "<Style>"
        f"<IconStyle><scale>{ICON_SCALE}</scale>"
        f"<Icon><href>{ICON_HREF}</href></Icon></IconStyle>"
        f"<LabelStyle><scale>{LABEL_SCALE}</scale></LabelStyle>"
        "</Style>"
    )


def placemark_xml(name: str, desc_html: str, lat: float, lon: float) -> str:
    return (
        "<Placemark>"
        f"<name>{html.escape(name)}</name>"
        f"<description><![CDATA[{desc_html}]]></description>"
        f"{style_xml()}"
        f"<Point><coordinates>{lon:.5f},{lat:.5f},0</coordinates></Point>"
        "</Placemark>"
    )


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    features = data["features"]
    print(f"loaded {len(features)} features")

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
        blobs.append(placemark_xml(name, describe(props), lat, lon))

    header = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        "<Document>\n"
        "<name>Indian Reservations — Points</name>\n"
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
