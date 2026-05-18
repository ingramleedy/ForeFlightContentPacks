"""Build ForeFlight layer KMLs for the 2026 AIN FBO Survey.

Three layers:
  AIN_FBO_Americas.kml   — all surveyed Americas/Canada/Caribbean FBOs
  AIN_FBO_International.kml — all surveyed Europe/Asia-Pacific/Middle East/Brazil FBOs

Placemarks are colored by tier:
  Top 5%  — gold star icon  (best)
  Top 10% — orange icon
  Top 20% — yellow icon
  Surveyed (below top 20%) — blue icon

Inline Style per Placemark (ForeFlight drops shared styleUrl refs).
OGC KML namespace. No <Folder>. No polygon geometry.
All names/descriptions are ASCII-safe.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import airportsdata
except ImportError:
    print("ERROR: pip install airportsdata", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "fbos_raw.json"
OUT_DIR = ROOT / "pack" / "layers"

AMERICAS_REGIONS = {"Southeast", "South", "Midwest", "Great Lakes", "West",
                    "Northeast", "Rocky Mountain", "Caribbean", "Canada", "Brazil"}
INTL_REGIONS = {"Europe", "Asia-Pacific", "Middle East"}

TIER_CONFIG = {
    "Top 5%":  {"icon": "http://maps.google.com/mapfiles/kml/paddle/ylw-stars.png",
                "scale": 1.4, "label_scale": 1.1, "label": "Top 5% Americas"},
    "Top 10%": {"icon": "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png",
                "scale": 1.2, "label_scale": 0.9, "label": "Top 10% Americas"},
    "Top 20%": {"icon": "http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png",
                "scale": 1.0, "label_scale": 0.8, "label": "Top 20% Americas"},
    "Surveyed": {"icon": "http://maps.google.com/mapfiles/kml/paddle/blu-circle.png",
                 "scale": 0.8, "label_scale": 0.7, "label": "Surveyed"},
}

INTL_TIER_CONFIG = {
    "Top 5%":  {"icon": "http://maps.google.com/mapfiles/kml/paddle/ylw-stars.png",
                "scale": 1.4, "label_scale": 1.1},
    "Top 10%": {"icon": "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png",
                "scale": 1.2, "label_scale": 0.9},
    "Top 20%": {"icon": "http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png",
                "scale": 1.0, "label_scale": 0.8},
    "Surveyed": {"icon": "http://maps.google.com/mapfiles/kml/paddle/purple-circle.png",
                 "scale": 0.8, "label_scale": 0.7},
}

ASCII_MAP = str.maketrans({
    "’": "'", "‘": "'",
    "“": '"', "”": '"',
    "–": "-", "—": "-",
    "…": "...",
    "\xe9": "e", "\xe8": "e", "\xea": "e",
    "\xe0": "a", "\xe1": "a", "\xe2": "a", "\xe4": "a",
    "\xee": "i", "\xef": "i",
    "\xf3": "o", "\xf4": "o", "\xf6": "o",
    "\xfa": "u", "\xfb": "u", "\xfc": "u",
    "\xf1": "n", "\xe7": "c",
})


def to_ascii(s: str) -> str:
    return s.translate(ASCII_MAP).encode("ascii", "replace").decode("ascii")


def placemark_xml(fbo: dict, airport_info: dict, tier_cfg: dict) -> str:
    name = to_ascii(f"{fbo['fbo']} ({fbo['icao']})")
    score_str = f"{fbo['score']:.2f}"
    tier = fbo["tier"]
    region = fbo.get("region", "")
    airport_name = fbo.get("airport", airport_info.get("name", ""))

    desc_html = (
        f"<b>{to_ascii(fbo['fbo'])}</b><br/>"
        f"Airport: {to_ascii(airport_name)} ({fbo['icao']})<br/>"
        f"Score: {score_str} / 5.00<br/>"
        f"Tier: {tier}<br/>"
        f"Region: {region}<br/>"
        f"Source: 2026 AIN FBO Survey (April 2026)"
    )

    lat = airport_info["lat"]
    lon = airport_info["lon"]
    icon_url = tier_cfg["icon"]
    icon_scale = tier_cfg["scale"]
    label_scale = tier_cfg["label_scale"]

    return (
        "<Placemark>"
        f"<name>{name}</name>"
        f"<description><![CDATA[{desc_html}]]></description>"
        "<Style>"
        "<IconStyle>"
        f"<scale>{icon_scale}</scale>"
        f"<Icon><href>{icon_url}</href></Icon>"
        "</IconStyle>"
        "<LabelStyle>"
        f"<scale>{label_scale}</scale>"
        "</LabelStyle>"
        "</Style>"
        "<Point>"
        f"<coordinates>{lon:.6f},{lat:.6f},0</coordinates>"
        "</Point>"
        "</Placemark>\n"
    )


def build_kml(fbos: list[dict], airports_db: dict, title: str, tier_config: dict) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        "<Document>",
        f"<name>{to_ascii(title)}</name>",
    ]

    missing = []
    for fbo in fbos:
        icao = fbo["icao"]
        info = airports_db.get(icao)
        if info is None:
            missing.append(icao)
            continue
        tier = fbo.get("tier", "Surveyed")
        cfg = tier_config.get(tier, tier_config["Surveyed"])
        lines.append(placemark_xml(fbo, info, cfg))

    lines += ["</Document>", "</kml>"]

    if missing:
        unique = sorted(set(missing))
        print(f"  WARNING: {len(unique)} ICAO code(s) not found in airportsdata: {unique}")

    return "\n".join(lines)


def main() -> None:
    fbos = json.loads(SRC.read_text(encoding="utf-8"))
    airports_db = airportsdata.load("ICAO")

    americas = [f for f in fbos if f.get("region") in AMERICAS_REGIONS]
    intl = [f for f in fbos if f.get("region") in INTL_REGIONS]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    out_americas = OUT_DIR / "AIN_FBO_Americas.kml"
    kml_a = build_kml(americas, airports_db, "AIN 2026 FBO Survey - Americas", TIER_CONFIG)
    out_americas.write_text(kml_a, encoding="utf-8")
    print(f"wrote {out_americas} ({len(americas)} FBOs)")

    out_intl = OUT_DIR / "AIN_FBO_International.kml"
    kml_i = build_kml(intl, airports_db, "AIN 2026 FBO Survey - International", INTL_TIER_CONFIG)
    out_intl.write_text(kml_i, encoding="utf-8")
    print(f"wrote {out_intl} ({len(intl)} FBOs)")


if __name__ == "__main__":
    main()
