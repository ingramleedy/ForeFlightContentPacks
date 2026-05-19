"""Retry geocoding for resorts that failed the first pass using simplified names."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "ski_resorts.json"
USER_AGENT = "ForeFlight-SkiResorts-Pack/1.0 (ingram@protectedtrust.com)"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

STRIP_SUFFIXES = [
    r"\s+Ski(?:\s+and\s+Snowboard)?\s+Resort$",
    r"\s+Ski\s+Area$",
    r"\s+Ski\s+Park$",
    r"\s+Mountain\s+Resort$",
    r"\s+Ski\s+Lifts?$",
    r"\s+Ski\s+Center$",
    r"\s+Ski\s+and\s+Snowboard\s+Area$",
    r"\s+Ski\s+Bowl$",
    r"\s+Snobowl$",
    r"\s+Summer\s+Ski\s+Area$",
    r"\s+Ski\s+Club$",
    r"\s+Recreation\s+Area$",
    r"\s+Outing\s+Club$",
]

CLEAN_PATTERNS = [
    r"\s+Archived\s+\S+\s+at\s+the\s+Wayback\s+Machine$",
    r"\s*\([^)]+\)\s*$",
]


def clean_name(name: str) -> list[str]:
    """Return a list of progressively simplified name variants to try."""
    variants = [name]

    # Clean Wikipedia artifacts
    cleaned = name
    for pat in CLEAN_PATTERNS:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE).strip()
    if cleaned != name:
        variants.append(cleaned)

    # Strip common suffixes from the cleaned name
    for suffix in STRIP_SUFFIXES:
        stripped = re.sub(suffix, "", cleaned, flags=re.IGNORECASE).strip()
        if stripped and stripped != cleaned:
            variants.append(stripped)
            break

    return list(dict.fromkeys(variants))  # deduplicate preserving order


def geocode(name: str, state: str) -> tuple[float, float] | None:
    query = f"{name}, {state}, USA"
    params = f"q={quote(query)}&format=json&limit=1&addressdetails=0"
    url = f"{NOMINATIM_URL}?{params}"
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=15) as r:
            results = json.loads(r.read())
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as exc:
        print(f"  error: {exc}")
    return None


def main() -> None:
    resorts = json.loads(DATA.read_text(encoding="utf-8"))
    missing = [r for r in resorts if r.get("lat") is None]
    print(f"Retrying {len(missing)} ungeocoded resorts with simplified names...")

    fixed = 0
    for i, r in enumerate(missing):
        name = r["name"]
        state = r["state"]
        variants = clean_name(name)

        coords = None
        used_variant = None
        for variant in variants:
            if variant != name:
                print(f"  [{i+1}/{len(missing)}] trying: '{variant}', {state}")
            coords = geocode(variant, state)
            time.sleep(1.1)
            if coords:
                used_variant = variant
                break

        if coords:
            r["lat"], r["lon"] = coords
            fixed += 1
            label = f"'{used_variant}'" if used_variant != name else "original"
            print(f"  [{i+1}/{len(missing)}] FOUND ({label}): {r['name']} -> {coords[0]:.4f}, {coords[1]:.4f}")
        else:
            print(f"  [{i+1}/{len(missing)}] STILL NOT FOUND: {r['name']}")

    DATA.write_text(json.dumps(resorts, indent=2, ensure_ascii=False), encoding="utf-8")
    total = len(resorts)
    geocoded = sum(1 for r in resorts if r.get("lat") is not None)
    print(f"\nFixed {fixed} additional resorts. Total geocoded: {geocoded}/{total}")
    print(f"Saved -> {DATA}")


if __name__ == "__main__":
    main()
