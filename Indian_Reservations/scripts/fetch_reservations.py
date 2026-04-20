"""Download federal American Indian reservations as GeoJSON from the ArcGIS FeatureServer.

Source: Federal_American_Indian_Reservations_v1 (Census TIGER/Line AIANNH republish).
Pages through results with resultOffset since max record count is 1000 per query.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

BASE = (
    "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/"
    "Federal_American_Indian_Reservations_v1/FeatureServer/0/query"
)
PAGE_SIZE = 1000
OUT = Path(__file__).resolve().parent.parent / "data" / "raw_reservations.geojson"


def fetch_page(offset: int) -> dict:
    params = {
        "where": "1=1",
        "outFields": "*",
        "f": "geojson",
        "resultOffset": offset,
        "resultRecordCount": PAGE_SIZE,
        "outSR": 4326,
    }
    r = requests.get(BASE, params=params, timeout=120)
    r.raise_for_status()
    return r.json()


def main() -> int:
    features: list[dict] = []
    offset = 0
    while True:
        page = fetch_page(offset)
        batch = page.get("features", [])
        if not batch:
            break
        features.extend(batch)
        print(f"  fetched {len(batch)} features (offset {offset}); total {len(features)}")
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    if not features:
        print("ERROR: no features returned", file=sys.stderr)
        return 1

    fc = {"type": "FeatureCollection", "features": features}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(fc), encoding="utf-8")
    print(f"wrote {len(features)} features to {OUT} ({OUT.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
