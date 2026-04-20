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
ENRICHMENT = ROOT / "data" / "enrichment.json"
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


def load_enrichment() -> dict:
    if ENRICHMENT.exists():
        return json.loads(ENRICHMENT.read_text(encoding="utf-8"))
    return {}


def describe(props: dict, enrich: dict) -> str:
    """Concise polygon-popup description — pilot-first, fewer lines than Points layer."""
    name = props.get("NAME") or "Reservation"
    code = props.get("AIANNHCC") or ""
    type_label = AIANNHCC_LABELS.get(code, code or "Reservation")
    land_mi2 = sq_meters_to_sq_miles(props.get("AREALAND") or 0)

    parts = [f"<h3>{html.escape(name)}</h3>"]

    assertion = enrich.get("tribal_overflight_assertion")
    if assertion:
        alt = assertion.get("altitude_ft")
        alt_txt = f"{alt:,} ft" if alt else "see details"
        parts.append(
            f'<p><b>&#9888; Tribal overflight assertion ({alt_txt}).</b> '
            f'Not FAA-enforced. See navdata PDF.</p>'
        )

    airports = enrich.get("nearest_airports") or []
    if airports:
        airport_str = " &middot; ".join(
            f"<b>{html.escape(a['ident'])}</b> {a['nm']:.0f} NM"
            for a in airports[:3]
        )
        parts.append(f"<p><b>Nearest airports:</b> {airport_str}</p>")

    states = enrich.get("states") or []
    states_str = ", ".join(states)
    meta = [f"<b>Type:</b> {html.escape(type_label)}"]
    if states_str:
        meta.append(f"<b>States:</b> {html.escape(states_str)}")
    meta.append(f"<b>Area:</b> {land_mi2:,.0f} sq mi")
    pop = enrich.get("population_2020")
    if pop is not None and pop > 0:
        meta.append(f"<b>Pop:</b> {int(pop):,}")
    parts.append("<p>" + " &nbsp; ".join(meta) + "</p>")

    parts.append(
        "<p><i>Tap the Points layer for tribal government, website, and more detail. "
        "See navdata for overflight considerations.</i></p>"
    )
    return "".join(parts)


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


def feature_to_xml(feat: dict, enrichment: dict) -> str | None:
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

    geoid = props.get("GEOID") or props.get("AIANNHNS") or name
    enrich = enrichment.get(geoid) or {}
    return placemark_xml(name, describe(props, enrich), polys)


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    features = data["features"]
    enrichment = load_enrichment()
    print(f"loaded {len(features)} features; enrichment: {len(enrichment)} records")

    placemark_blobs: list[str] = []
    for feat in features:
        pm = feature_to_xml(feat, enrichment)
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
