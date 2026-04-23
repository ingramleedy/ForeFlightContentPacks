"""Geocode restaurants whose JSON-LD didn't include lat/lon.

Food Network publishes geo.latitude / geo.longitude inside the Restaurant
schema.org block for most listings, but about 27% of them are missing it.
Those records still carry a full street / city / state / zip — enough to
hit Nominatim (OpenStreetMap) for a free lookup.

Nominatim ToS: max 1 req/sec, requires a descriptive User-Agent, and asks
us not to bulk-batch without caching. We cache results in
data/_geocode_cache.json so re-runs don't re-query already-solved rows.

Reads  data/ddd_raw.json
Writes data/ddd_raw.json in place  (sets geo.latitude / geo.longitude)
Cache  data/_geocode_cache.json
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "ddd_raw.json"
CACHE = ROOT / "data" / "_geocode_cache.json"

USER_AGENT = "ForeFlightContentPacks-DDD-Builder/1.0 (github.com/ingramleedy/ForeFlightContentPacks)"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
RATE_LIMIT_SECONDS = 1.1  # a hair above 1.0 to stay safe


def build_query(address: dict) -> dict:
    return {
        "street": (address.get("streetAddress") or "").strip(),
        "city": (address.get("addressLocality") or "").strip(),
        "state": (address.get("addressRegion") or "").strip(),
        "postalcode": (address.get("postalCode") or "").strip(),
        "country": "US",
        "format": "json",
        "limit": "1",
    }


def geocode(params: dict) -> tuple[float, float] | None:
    url = NOMINATIM + "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v})
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.loads(r.read().decode("utf-8"))
    if not body:
        return None
    top = body[0]
    try:
        return float(top["lat"]), float(top["lon"])
    except (KeyError, ValueError):
        return None


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    records = data["restaurants"]
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

    missing = [r for r in records if not (r.get("geo") or {}).get("latitude")]
    print(f"loaded {len(records)} records, {len(missing)} need geocoding")

    updated = 0
    failed = 0
    for i, r in enumerate(missing, start=1):
        addr = r.get("address") or {}
        if not addr.get("streetAddress") or not addr.get("addressLocality"):
            failed += 1
            continue
        cache_key = "|".join([
            addr.get("streetAddress", ""),
            addr.get("addressLocality", ""),
            addr.get("addressRegion", ""),
            addr.get("postalCode", ""),
        ])
        if cache_key in cache:
            entry = cache[cache_key]
            if entry:
                r["geo"] = {"@type": "GeoCoordinates",
                            "latitude": entry["lat"], "longitude": entry["lon"]}
                updated += 1
            else:
                failed += 1
            continue

        try:
            result = geocode(build_query(addr))
        except Exception as e:
            print(f"  [{i}/{len(missing)}] {r.get('name')}: ERROR {e}", file=sys.stderr)
            time.sleep(RATE_LIMIT_SECONDS)
            failed += 1
            continue

        if result:
            lat, lon = result
            cache[cache_key] = {"lat": lat, "lon": lon}
            r["geo"] = {"@type": "GeoCoordinates", "latitude": str(lat), "longitude": str(lon)}
            updated += 1
            print(f"  [{i}/{len(missing)}] {r.get('name')} -> {lat:.5f},{lon:.5f}")
        else:
            cache[cache_key] = None
            failed += 1
            print(f"  [{i}/{len(missing)}] {r.get('name')}: NOT FOUND")

        # Persist cache every 20 entries for safety across interruptions
        if i % 20 == 0:
            CACHE.write_text(json.dumps(cache, indent=2), encoding="utf-8")

        time.sleep(RATE_LIMIT_SECONDS)

    CACHE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    total_geo = sum(1 for r in records if (r.get("geo") or {}).get("latitude"))
    print(f"\ngeocoded: {updated}, failed: {failed}")
    print(f"records with geo: {total_geo}/{len(records)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
