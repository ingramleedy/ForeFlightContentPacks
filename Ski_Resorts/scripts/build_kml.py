"""Build ForeFlight KML layer from ski_resorts.json.

Color-codes placemarks by vertical drop:
  Gold star  >= 3,000 ft  (big mountain)
  Orange     1,500-2,999 ft
  Yellow       500-1,499 ft
  Blue         < 500 ft  (small / local)

Output: pack/layers/Ski_Resorts.kml
"""
from __future__ import annotations

import json
import math
import unicodedata
from pathlib import Path

try:
    import airportsdata
    _airports = airportsdata.load("ICAO")
    _airports_iata = airportsdata.load("IATA")
except ImportError:
    _airports = {}
    _airports_iata = {}

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "ski_resorts.json"
OUT_KML = ROOT / "pack" / "layers" / "Ski_Resorts.kml"

# ---------------------------------------------------------------------------
# Icon URLs (Google Maps hosted, always available in ForeFlight)
# ---------------------------------------------------------------------------
ICON_GOLD   = "http://maps.google.com/mapfiles/kml/paddle/ylw-stars.png"
ICON_ORANGE = "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png"
ICON_YELLOW = "http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png"
ICON_BLUE   = "http://maps.google.com/mapfiles/kml/paddle/blu-circle.png"

TIER_GOLD   = "Big Mountain (3,000+ ft vertical)"
TIER_ORANGE = "Major Resort (1,500-2,999 ft vertical)"
TIER_YELLOW = "Regional Resort (500-1,499 ft vertical)"
TIER_BLUE   = "Local Hill (< 500 ft vertical)"


def classify(vertical_ft: int | None) -> tuple[str, str]:
    if vertical_ft is None:
        return ICON_BLUE, TIER_BLUE
    if vertical_ft >= 3000:
        return ICON_GOLD, TIER_GOLD
    if vertical_ft >= 1500:
        return ICON_ORANGE, TIER_ORANGE
    if vertical_ft >= 500:
        return ICON_YELLOW, TIER_YELLOW
    return ICON_BLUE, TIER_BLUE


def icon_scale(vertical_ft: int | None) -> float:
    if vertical_ft is None:
        return 0.8
    if vertical_ft >= 3000:
        return 1.4
    if vertical_ft >= 1500:
        return 1.1
    if vertical_ft >= 500:
        return 1.0
    return 0.8


def to_ascii(text: str) -> str:
    """Convert accented and special characters to ASCII equivalents."""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if ord(c) < 128)


# ---------------------------------------------------------------------------
# Nearest airport lookup
# ---------------------------------------------------------------------------

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in statute miles between two lat/lon points."""
    R = 3958.8
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def nearest_airports(lat: float, lon: float, max_dist_nm: float = 75, top_n: int = 3) -> list[dict]:
    results = []
    for icao, ap in _airports.items():
        if ap.get("country") != "US":
            continue
        alat = ap.get("lat")
        alon = ap.get("lon")
        if alat is None or alon is None:
            continue
        dist = haversine(lat, lon, alat, alon)
        if dist <= max_dist_nm:
            results.append({
                "icao": icao,
                "name": ap.get("name", ""),
                "dist_mi": round(dist, 1),
            })
    results.sort(key=lambda x: x["dist_mi"])
    return results[:top_n]


# ---------------------------------------------------------------------------
# KML generation
# ---------------------------------------------------------------------------

def fmt_airports(aps: list[dict]) -> str:
    if not aps:
        return "None within 75 mi"
    parts = []
    for a in aps:
        parts.append(f"{a['icao']} ({a['dist_mi']} mi)")
    return ", ".join(parts)


def placemark_xml(resort: dict) -> str:
    name = to_ascii(resort["name"])
    state = to_ascii(resort.get("state", ""))
    vertical = resort.get("vertical_ft")
    peak = resort.get("peak_ft")
    base = resort.get("base_ft")
    trails = resort.get("trails")
    lifts = resort.get("lifts")
    acres = resort.get("skiable_acres")
    snow = resort.get("avg_snowfall_in")
    lat = resort.get("lat")
    lon = resort.get("lon")

    icon_url, tier_label = classify(vertical)
    scale = icon_scale(vertical)

    aps = nearest_airports(lat, lon) if lat and lon else []
    airports_str = fmt_airports(aps)

    def val(v, suffix="") -> str:
        return f"{v:,}{suffix}" if v is not None else "N/A"

    desc_lines = [
        f"<b>{name}</b>",
        f"<b>State:</b> {state}",
        f"<b>Tier:</b> {tier_label}",
        "",
        f"<b>Vertical Drop:</b> {val(vertical, ' ft')}",
        f"<b>Summit Elevation:</b> {val(peak, ' ft MSL')}",
        f"<b>Base Elevation:</b> {val(base, ' ft MSL')}",
        "",
        f"<b>Trails:</b> {val(trails)}",
        f"<b>Lifts:</b> {val(lifts)}",
        f"<b>Skiable Acreage:</b> {val(acres, ' acres')}",
        f"<b>Avg Annual Snowfall:</b> {val(snow, ' in')}",
        "",
        f"<b>Nearest Airports:</b> {airports_str}",
    ]
    desc_html = "<br/>".join(desc_lines)

    coords = f"{lon},{lat},0" if lat and lon else "0,0,0"

    return f"""  <Placemark>
    <name>{name} ({state})</name>
    <Style>
      <IconStyle>
        <scale>{scale}</scale>
        <Icon><href>{icon_url}</href></Icon>
      </IconStyle>
    </Style>
    <description><![CDATA[{desc_html}]]></description>
    <Point>
      <coordinates>{coords}</coordinates>
    </Point>
  </Placemark>"""


def build_kml(resorts: list[dict]) -> str:
    with_coords = [r for r in resorts if r.get("lat") and r.get("lon")]
    print(f"Building KML: {len(with_coords)} resorts with coordinates (of {len(resorts)} total)")

    tiers = {TIER_GOLD: 0, TIER_ORANGE: 0, TIER_YELLOW: 0, TIER_BLUE: 0}
    for r in with_coords:
        _, t = classify(r.get("vertical_ft"))
        tiers[t] += 1
    for t, n in tiers.items():
        print(f"  {t}: {n}")

    placemarks = "\n".join(placemark_xml(r) for r in with_coords)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Ski Resorts</name>
    <description>US ski resorts color-coded by vertical drop. Gold = 3,000+ ft, Orange = 1,500-2,999 ft, Yellow = 500-1,499 ft, Blue = under 500 ft.</description>
{placemarks}
  </Document>
</kml>"""


def main() -> None:
    if not DATA.exists():
        raise FileNotFoundError(f"Run fetch_resorts.py first: {DATA}")

    resorts = json.loads(DATA.read_text(encoding="utf-8"))
    kml = build_kml(resorts)

    OUT_KML.parent.mkdir(parents=True, exist_ok=True)
    OUT_KML.write_text(kml, encoding="utf-8")
    print(f"Wrote {OUT_KML} ({OUT_KML.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
