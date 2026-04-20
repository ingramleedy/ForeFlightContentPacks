"""Build the ForeFlight waypoint CSV of reservation centroids.

Uses the Census-supplied internal point (INTPTLAT/INTPTLON) which is guaranteed
to fall inside the polygon, falling back to a computed centroid if missing.

Output format per ForeFlight content-pack spec:
    WAYPOINT_NAME,Description,Lat,Lon

Waypoint names are sanitized to uppercase alphanumeric, <= 10 chars, and made
unique across the file. The 5 rich waypoints (HUALAPAI, HAVASUPAI, NAVAJO,
TAOSPUEB, REDLAKE) are forced to fixed codes so their per-tribe PDFs line up
with the ForeFlight `<WAYPOINT_NAME><DocumentName>.pdf` convention.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw_reservations.geojson"
OUT = ROOT / "pack" / "navdata" / "Reservation_Centroids.csv"

# Override map for the 5 reservations that get per-waypoint rich PDFs. Keys are
# case-insensitive substring matches on NAME; value is the forced waypoint code.
RICH_WAYPOINT_OVERRIDES = {
    "hualapai": "HUALAPAI",
    "havasupai": "HAVASUPAI",
    "navajo nation": "NAVAJO",
    "taos pueblo": "TAOSPUEB",
    "red lake": "REDLAKE",
}

MAX_NAME_LEN = 10


def sanitize(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]", "", name).upper()
    if not cleaned:
        cleaned = "RESERVATION"
    return cleaned[:MAX_NAME_LEN]


def unique(code: str, taken: set[str]) -> str:
    if code not in taken:
        taken.add(code)
        return code
    base = code[: MAX_NAME_LEN - 1]
    for i in range(2, 100):
        suffix = str(i)
        candidate = (base[: MAX_NAME_LEN - len(suffix)] + suffix)
        if candidate not in taken:
            taken.add(candidate)
            return candidate
    raise RuntimeError(f"could not generate unique code for {code}")


def override_for(name: str) -> str | None:
    lower = name.lower()
    for needle, code in RICH_WAYPOINT_OVERRIDES.items():
        if needle in lower:
            return code
    return None


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


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    rows: list[tuple[str, str, float, float]] = []
    taken: set[str] = set()

    for feat in data["features"]:
        props = feat.get("properties") or {}
        name = props.get("NAME") or props.get("BASENAME") or ""
        if not name:
            continue
        pt = centroid_latlon(props, feat.get("geometry"))
        if pt is None:
            continue
        lat, lon = pt

        forced = override_for(name)
        if forced and forced not in taken:
            code = forced
            taken.add(code)
        else:
            code = unique(sanitize(name), taken)

        description = name.replace(",", " ").strip()
        rows.append((code, description, lat, lon))

    rows.sort(key=lambda r: r[0])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for code, desc, lat, lon in rows:
            w.writerow([code, desc, f"{lat:.6f}", f"{lon:.6f}"])

    print(f"wrote {len(rows)} waypoints to {OUT} ({OUT.stat().st_size / 1024:.1f} KB)")

    forced_codes = set(RICH_WAYPOINT_OVERRIDES.values())
    present = {r[0] for r in rows} & forced_codes
    missing = forced_codes - present
    if missing:
        print(f"WARNING: rich-waypoint codes not placed: {missing}", file=sys.stderr)
    else:
        print(f"rich waypoint codes placed: {sorted(present)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
