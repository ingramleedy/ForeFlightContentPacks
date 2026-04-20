"""Convert the cached GeoJSON of federal reservations into a simplified, styled KML
matching the official ForeFlight sample pattern (UserMapShapesSample.kml).

Structure per placemark: pure <Polygon> (or flat <MultiGeometry> of polygons),
no embedded Point. Each placemark has inline <Style> with <PolyStyle fill=1>.
Centroid waypoints are emitted separately via navdata CSV — the layer KML is
for the zone outline + fill only.

The MultiGeometry-with-hidden-Point approach (used by some community packs)
caused ForeFlight to render only the point label and drop the polygon fill in
our testing, so we follow the official sample shape instead.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw_reservations.geojson"
OUT = ROOT / "pack" / "layers" / "Indian_Reservations.kml"

SIMPLIFY_TOLERANCE = 0.001  # degrees (~110 m at equator)
COORD_DECIMALS = 5

# KML color is AABBGGRR. For a warm orange fill and a vivid contrasting border.
FILL_COLOR = "802060c0"      # translucent warm orange (alpha=50%, R=192 G=96 B=32)
OUTLINE_COLOR = "ff00a0ff"   # opaque bright orange (R=255 G=160 B=0) — stands out from
                             # magenta/purple/blue/green chart overlays
OUTLINE_WIDTH = 2.5
LABEL_SCALE = 1.2

AIANNHCC_LABELS = {
    "D2": "Federal American Indian Reservation",
    "D8": "Tribal Designated Statistical Area",
}


def sq_meters_to_sq_miles(m2) -> float:
    try:
        return float(m2) / 2_589_988.110336
    except (TypeError, ValueError):
        return 0.0


def fmt_coord(x: float, y: float) -> str:
    return f"{x:.{COORD_DECIMALS}f},{y:.{COORD_DECIMALS}f},0"


def ring_coords(ring) -> str:
    return " ".join(fmt_coord(float(x), float(y)) for x, y, *_ in ring.coords)


def polygon_xml(poly: Polygon) -> str:
    outer = ring_coords(poly.exterior)
    inners = "".join(
        f"<innerBoundaryIs><LinearRing><coordinates>{ring_coords(r)}</coordinates></LinearRing></innerBoundaryIs>"
        for r in poly.interiors
    )
    return (
        "<Polygon>"
        "<tessellate>1</tessellate>"
        f"<outerBoundaryIs><LinearRing><coordinates>{outer}</coordinates></LinearRing></outerBoundaryIs>"
        f"{inners}"
        "</Polygon>"
    )


def style_xml() -> str:
    return (
        "<Style>"
        f"<LineStyle><color>{OUTLINE_COLOR}</color><width>{OUTLINE_WIDTH}</width></LineStyle>"
        f"<PolyStyle><color>{FILL_COLOR}</color><fill>1</fill><outline>1</outline></PolyStyle>"
        "</Style>"
    )


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


def placemark_xml(name: str, desc_html: str, polys: list[Polygon]) -> str:
    # Pure polygon placemark, matching the official ForeFlight sample shape.
    # Multi-part reservations get a flat <MultiGeometry> of Polygons — no Point.
    if len(polys) == 1:
        geom = polygon_xml(polys[0])
    else:
        geom = "<MultiGeometry>" + "".join(polygon_xml(p) for p in polys) + "</MultiGeometry>"
    return (
        "<Placemark>"
        f"<name>{html.escape(name)}</name>"
        f"<description><![CDATA[{desc_html}]]></description>"
        f"{style_xml()}"
        f"{geom}"
        "</Placemark>"
    )


def feature_to_xml(feat: dict) -> str | None:
    props = feat.get("properties") or {}
    geom_json = feat.get("geometry")
    if not geom_json:
        return None
    name = props.get("NAME") or props.get("BASENAME") or "Unnamed Reservation"
    try:
        geom = shape(geom_json)
    except Exception as e:
        print(f"  skip {name}: {e}", file=sys.stderr)
        return None
    simplified = geom.simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)
    if simplified.is_empty:
        return None
    if isinstance(simplified, Polygon):
        polys = [simplified]
    elif isinstance(simplified, MultiPolygon):
        polys = [p for p in simplified.geoms if not p.is_empty]
    else:
        return None
    if not polys:
        return None

    return placemark_xml(name, describe(props), polys)


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    features = data["features"]
    print(f"loaded {len(features)} features from {SRC.name}")

    placemark_blobs: list[str] = []
    for feat in features:
        pm = feature_to_xml(feat)
        if pm:
            placemark_blobs.append(pm)

    header = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        "<Document>\n"
        "<name>Indian Reservations</name>\n"
        "<open>1</open>\n"
        "<description>Federal American Indian Reservations (Census TIGER/Line AIANNH). "
        "See the navdata folder for overflight considerations and special airspace notes.</description>\n"
    )
    footer = "</Document>\n</kml>\n"
    body = "\n".join(placemark_blobs) + "\n"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(header + body + footer, encoding="utf-8")
    size_kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT} ({size_kb:.1f} KB); placemarks={len(placemark_blobs)}")
    if size_kb > 5 * 1024:
        print("WARNING: KML over 5 MB target", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
