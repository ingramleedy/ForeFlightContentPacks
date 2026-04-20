"""Enrich each reservation feature with Census ACS demographics, nearest public
airports (OurAirports), and Wikidata tribal-government metadata, plus merge the
hand-curated tribal overflight assertions from content/tribal_assertions.json.

Output: data/enrichment.json, keyed by ArcGIS GEOID. Read by build_kml.py,
build_points_layer.py, and build_pdfs.py. Graceful degradation — downstream
builders work without this file, and partial enrichment is OK.

Data sources:
- Census ACS 5-year (2022). Endpoint: api.census.gov/data/2022/acs/acs5.
- OurAirports CSV (public, maintained). URL below.
- Wikidata SPARQL endpoint. Query for U.S. Indian reservations with P17=Q30.
- content/tribal_assertions.json for hand-curated overflight assertions.
"""
from __future__ import annotations

import csv
import io
import json
import math
import sys
import time
from pathlib import Path

import requests
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw_reservations.geojson"
OUT = ROOT / "data" / "enrichment.json"
ASSERTIONS_JSON = ROOT / "content" / "tribal_assertions.json"

CENSUS_URL = "https://api.census.gov/data/2022/acs/acs5"
OURAIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"

USER_AGENT = "ForeFlightContentPacks/1.0 (https://github.com/ingramleedy/ForeFlightContentPacks)"
NEAREST_AIRPORT_COUNT = 3
NEAREST_AIRPORT_MAX_NM = 50.0
STATES_BY_FIPS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    return s


# ---------------------------------------------------------------------------
# Census ACS — population + housing per AIANNH area
# ---------------------------------------------------------------------------

def fetch_census_acs(s: requests.Session) -> dict[str, dict]:
    """Return {AIANNH_code: {pop, housing, name}} from Census ACS 5-year."""
    params = {
        "get": "NAME,B01003_001E,B25001_001E",
        "for": "american indian area/alaska native area/hawaiian home land:*",
    }
    r = s.get(CENSUS_URL, params=params, timeout=60)
    r.raise_for_status()
    rows = r.json()
    header, *records = rows
    idx = {k: i for i, k in enumerate(header)}
    out: dict[str, dict] = {}
    for rec in records:
        aiannh = rec[idx["american indian area/alaska native area/hawaiian home land"]]
        try:
            pop = int(rec[idx["B01003_001E"]])
            hu = int(rec[idx["B25001_001E"]])
        except (TypeError, ValueError):
            pop, hu = None, None
        out[aiannh] = {
            "name": rec[idx["NAME"]],
            "population_2020": pop,
            "housing_units_2020": hu,
        }
    print(f"  Census ACS: {len(out)} AIANNH records")
    return out


# ---------------------------------------------------------------------------
# OurAirports — nearest public airports
# ---------------------------------------------------------------------------

def fetch_airports(s: requests.Session) -> list[dict]:
    r = s.get(OURAIRPORTS_URL, timeout=120)
    r.raise_for_status()
    reader = csv.DictReader(io.StringIO(r.text))
    keep_types = {"large_airport", "medium_airport", "small_airport"}
    out: list[dict] = []
    for row in reader:
        if row.get("iso_country") != "US":
            continue
        if row.get("type") not in keep_types:
            continue
        if (row.get("scheduled_service") or "").lower() in ("closed",):
            continue
        try:
            lat = float(row["latitude_deg"])
            lon = float(row["longitude_deg"])
        except (TypeError, ValueError):
            continue
        ident = (row.get("gps_code") or row.get("ident") or row.get("local_code") or "").strip()
        if not ident:
            continue
        out.append({
            "ident": ident,
            "name": (row.get("name") or "").strip(),
            "lat": lat,
            "lon": lon,
        })
    print(f"  OurAirports: {len(out)} public-use US airports loaded")
    return out


def haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R_NM = 3440.065
    p1 = math.radians(lat1); p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1); dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1) * math.cos(p2) * math.sin(dl/2)**2
    return 2 * R_NM * math.asin(math.sqrt(a))


def nearest_airports(center_lat: float, center_lon: float, airports: list[dict]) -> list[dict]:
    dists: list[tuple[float, dict]] = []
    # Bounding-box prefilter ~ 1 degree ≈ 60 NM; use 1.5 to be safe
    for ap in airports:
        if abs(ap["lat"] - center_lat) > 1.5 or abs(ap["lon"] - center_lon) > 2.0:
            continue
        d = haversine_nm(center_lat, center_lon, ap["lat"], ap["lon"])
        if d <= NEAREST_AIRPORT_MAX_NM:
            dists.append((d, ap))
    dists.sort(key=lambda t: t[0])
    return [
        {"ident": ap["ident"], "name": ap["name"], "nm": round(d, 1)}
        for d, ap in dists[:NEAREST_AIRPORT_COUNT]
    ]


# ---------------------------------------------------------------------------
# Wikidata — tribal government, recognition date, language, website
# ---------------------------------------------------------------------------

def wikidata_search_entity(s: requests.Session, query: str) -> str | None:
    """Find the most likely Wikidata entity for a given name using wbsearchentities."""
    r = s.get(
        WIKIDATA_API,
        params={
            "action": "wbsearchentities",
            "search": query,
            "language": "en",
            "type": "item",
            "limit": 5,
            "format": "json",
        },
        timeout=30,
    )
    r.raise_for_status()
    results = r.json().get("search", [])
    if not results:
        return None
    # Prefer results whose description mentions reservation/tribe/pueblo/nation/rancheria/band
    prefer_words = ("reservation", "tribe", "pueblo", "rancheria", "nation", "band", "native", "indigenous")
    for hit in results:
        desc = (hit.get("description") or "").lower()
        if any(w in desc for w in prefer_words):
            return hit["id"]
    return results[0]["id"]


def wikidata_get_claims(s: requests.Session, qid: str) -> dict:
    """Fetch claims for a Wikidata entity and extract the pilot-relevant properties."""
    r = s.get(
        WIKIDATA_API,
        params={
            "action": "wbgetentities",
            "ids": qid,
            "props": "claims|labels|descriptions",
            "languages": "en",
            "format": "json",
        },
        timeout=30,
    )
    r.raise_for_status()
    entities = r.json().get("entities", {})
    ent = entities.get(qid) or {}
    claims = ent.get("claims") or {}

    def _claim_str(prop: str) -> str | None:
        vals = claims.get(prop) or []
        if not vals:
            return None
        m = vals[0].get("mainsnak", {}).get("datavalue", {}).get("value")
        if isinstance(m, str):
            return m
        if isinstance(m, dict) and "time" in m:
            return m["time"].lstrip("+")[:10]
        if isinstance(m, dict) and "id" in m:
            return m["id"]
        return None

    def _claim_qids(prop: str) -> list[str]:
        vals = claims.get(prop) or []
        out: list[str] = []
        for v in vals:
            m = v.get("mainsnak", {}).get("datavalue", {}).get("value")
            if isinstance(m, dict) and "id" in m:
                out.append(m["id"])
        return out

    return {
        "qid": qid,
        "label": (ent.get("labels", {}).get("en") or {}).get("value") or "",
        "description": (ent.get("descriptions", {}).get("en") or {}).get("value") or "",
        "country_qids": _claim_qids("P17"),
        "website": _claim_str("P856"),
        "inception": _claim_str("P571"),
        "language_qids": _claim_qids("P2936"),
    }


def wikidata_label_for(s: requests.Session, qid: str) -> str:
    r = s.get(
        WIKIDATA_API,
        params={
            "action": "wbgetentities",
            "ids": qid,
            "props": "labels",
            "languages": "en",
            "format": "json",
        },
        timeout=30,
    )
    r.raise_for_status()
    ents = r.json().get("entities", {})
    ent = ents.get(qid) or {}
    return (ent.get("labels", {}).get("en") or {}).get("value") or ""


def fetch_wikidata_for_names(s: requests.Session, names: list[str]) -> dict[str, dict]:
    """Return {reservation_name: enrichment_dict} using per-name search + claims fetch."""
    cache_path = ROOT / "data" / "_wikidata_cache.json"
    cache: dict[str, dict] = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))

    out: dict[str, dict] = {}
    lang_label_cache: dict[str, str] = {}
    total = len(names)
    for i, name in enumerate(names):
        if name in cache:
            out[name] = cache[name]
            continue
        try:
            qid = wikidata_search_entity(s, name)
            if not qid:
                cache[name] = {}
                continue
            claims = wikidata_get_claims(s, qid)
            # Only accept results that are located in the U.S. (P17 = Q30)
            if "Q30" not in claims.get("country_qids", []):
                cache[name] = {}
                continue
            languages = []
            for lqid in claims.get("language_qids", []):
                if lqid not in lang_label_cache:
                    lang_label_cache[lqid] = wikidata_label_for(s, lqid)
                    time.sleep(0.2)
                if lang_label_cache[lqid]:
                    languages.append(lang_label_cache[lqid])
            entry = {
                "qid": claims["qid"],
                "label": claims["label"],
                "website": claims.get("website"),
                "inception": claims.get("inception"),
                "languages": languages,
            }
            out[name] = entry
            cache[name] = entry
        except Exception as e:
            print(f"    wikidata error on {name}: {e}", file=sys.stderr)
            cache[name] = {}
        time.sleep(0.3)  # polite rate limit
        if (i + 1) % 25 == 0:
            print(f"    wikidata progress: {i+1}/{total}")
            cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")

    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    print(f"  Wikidata: {sum(1 for v in out.values() if v)} name-level matches (of {total})")
    return out


def normalize(name: str) -> str:
    n = name.lower()
    for suffix in ("indian reservation", "reservation", "rancheria", "pueblo", "community", "colony",
                   "off-reservation trust land", "nation", "band", "tribe", "tribes", "of"):
        n = n.replace(suffix, "")
    return " ".join(n.split())


# ---------------------------------------------------------------------------
# Main enrichment loop
# ---------------------------------------------------------------------------

def load_assertions() -> dict:
    if not ASSERTIONS_JSON.exists():
        return {}
    data = json.loads(ASSERTIONS_JSON.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def assertion_for(name: str, assertions: dict) -> dict | None:
    lower = name.lower()
    for entry in assertions.values():
        for needle in entry.get("match_substrings", []):
            if needle.lower() in lower:
                return {
                    "summary": entry["summary"],
                    "altitude_ft": entry.get("altitude_ft"),
                    "source": entry["source"],
                }
    return None


def states_from_census_name(census_name: str) -> list[str]:
    """Census NAME like 'Navajo Nation Reservation, AZ--NM--UT' → ['AZ', 'NM', 'UT'].
    Census returns state list as two-letter abbreviations after the final comma,
    joined with '--' when a reservation spans multiple states."""
    if "," not in census_name:
        return []
    tail = census_name.rsplit(",", 1)[1].strip()
    out: list[str] = []
    for token in tail.replace("--", ",").split(","):
        t = token.strip().upper()
        if len(t) == 2 and t.isalpha():
            out.append(t)
    return out


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: {SRC} not found — run fetch_reservations.py first", file=sys.stderr)
        return 1

    s = session()
    print("fetching external data...")
    census = fetch_census_acs(s)
    airports = fetch_airports(s)
    assertions = load_assertions()

    data = json.loads(SRC.read_text(encoding="utf-8"))
    reservation_names = [
        (f.get("properties") or {}).get("NAME")
        for f in data["features"]
        if (f.get("properties") or {}).get("NAME")
    ]
    print(f"looking up {len(reservation_names)} reservations on Wikidata (cached; will be slow on first run)...")
    wikidata = fetch_wikidata_for_names(s, reservation_names)

    enrichment: dict[str, dict] = {}

    census_matches = 0
    airport_matches = 0
    wikidata_matches = 0
    assertion_matches = 0

    for feat in data["features"]:
        props = feat.get("properties") or {}
        name = props.get("NAME") or props.get("BASENAME") or ""
        if not name:
            continue
        geoid = props.get("GEOID") or props.get("AIANNHNS") or name
        aiannh = props.get("AIANNH") or ""

        rec: dict = {"name": name}

        # Census: prefer AIANNH code match, fall back to name substring
        census_hit = None
        if aiannh and aiannh in census:
            census_hit = census[aiannh]
        else:
            # Some AIANNH ids in source vary; try numeric-4 variant
            if aiannh:
                variants = {aiannh.lstrip("0"), aiannh.zfill(4), aiannh.zfill(5)}
                for v in variants:
                    if v in census:
                        census_hit = census[v]
                        break
        if not census_hit:
            for c_name, c in census.items():
                if c["name"].lower().startswith(name.lower() + ","):
                    census_hit = c
                    break
        if census_hit:
            if census_hit.get("population_2020") is not None:
                rec["population_2020"] = census_hit["population_2020"]
            if census_hit.get("housing_units_2020") is not None:
                rec["housing_units_2020"] = census_hit["housing_units_2020"]
            states = states_from_census_name(census_hit["name"])
            if states:
                rec["states"] = states
            census_matches += 1

        # Nearest airports: use Census internal point as centroid
        try:
            lat = float(props.get("INTPTLAT"))
            lon = float(props.get("INTPTLON"))
        except (TypeError, ValueError):
            geom = shape(feat["geometry"])
            rp = geom.representative_point()
            lat, lon = rp.y, rp.x
        ap = nearest_airports(lat, lon, airports)
        if ap:
            rec["nearest_airports"] = ap
            airport_matches += 1

        # Wikidata: per-name lookup result (may be empty dict if no good match)
        wd = wikidata.get(name) or {}
        if wd.get("qid"):
            wd_out: dict = {"qid": wd["qid"], "label": wd.get("label") or name}
            if wd.get("inception"):
                wd_out["federally_recognized"] = wd["inception"]
            if wd.get("website"):
                wd_out["website"] = wd["website"]
            if wd.get("languages"):
                wd_out["languages"] = wd["languages"]
            rec["wikidata"] = wd_out
            wikidata_matches += 1

        # Hand-curated tribal overflight assertion
        a = assertion_for(name, assertions)
        if a:
            rec["tribal_overflight_assertion"] = a
            assertion_matches += 1

        enrichment[geoid] = rec

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(enrichment, indent=2), encoding="utf-8")

    total = len(enrichment)
    print()
    print(f"enrichment.json: {total} reservations ({OUT.stat().st_size / 1024:.1f} KB)")
    print(f"  Census hits:      {census_matches}  ({100*census_matches/total:.0f}%)")
    print(f"  Airport hits:     {airport_matches}  ({100*airport_matches/total:.0f}%)")
    print(f"  Wikidata hits:    {wikidata_matches}  ({100*wikidata_matches/total:.0f}%)")
    print(f"  Assertion hits:   {assertion_matches}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
