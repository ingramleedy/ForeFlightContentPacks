"""Fetch US ski resort data from Wikipedia and geocode via Nominatim.

Outputs: data/ski_resorts.json
"""
from __future__ import annotations

import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "ski_resorts.json"

WIKI_URL = (
    "https://en.wikipedia.org/wiki/Comparison_of_North_American_ski_resorts"
)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "ForeFlight-SkiResorts-Pack/1.0 (ingram@protectedtrust.com)"


# ---------------------------------------------------------------------------
# Wikipedia table scraper
# ---------------------------------------------------------------------------

class TableParser(HTMLParser):
    """Extract all <table> blocks as raw HTML strings."""

    def __init__(self) -> None:
        super().__init__()
        self.tables: list[str] = []
        self._depth = 0
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "table":
            self._depth += 1
            self._buf.append(self._reconstruct(tag, attrs))
        elif self._depth:
            self._buf.append(self._reconstruct(tag, attrs))

    def handle_endtag(self, tag: str) -> None:
        if self._depth:
            self._buf.append(f"</{tag}>")
            if tag == "table":
                self._depth -= 1
                if self._depth == 0:
                    self.tables.append("".join(self._buf))
                    self._buf = []

    def handle_data(self, data: str) -> None:
        if self._depth:
            self._buf.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._depth:
            self._buf.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self._depth:
            self._buf.append(f"&#{name};")

    @staticmethod
    def _reconstruct(tag: str, attrs: list) -> str:
        parts = [f"<{tag}"]
        for k, v in attrs:
            parts.append(f' {k}="{v}"' if v is not None else f" {k}")
        parts.append(">")
        return "".join(parts)


class RowParser(HTMLParser):
    """Parse <tr> rows from a table HTML fragment into lists of cell text."""

    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self._in_cell = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
            self._in_cell = True
        elif tag == "br" and self._in_cell:
            if self._cell is not None:
                self._cell.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th") and self._in_cell:
            text = " ".join("".join(self._cell or []).split())
            if self._row is not None:
                self._row.append(text)
            self._cell = None
            self._in_cell = False
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None

    def handle_data(self, data: str) -> None:
        if self._in_cell and self._cell is not None:
            self._cell.append(data)


def strip_refs(text: str) -> str:
    """Remove [1], [a], etc. Wikipedia citation marks."""
    return re.sub(r"\[\w+\]", "", text).strip()


def parse_int(text: str) -> int | None:
    """Extract first integer from a string like '3,212' or '3212 ft'."""
    text = strip_refs(text)
    m = re.search(r"[\d,]+", text)
    if not m:
        return None
    try:
        return int(m.group().replace(",", ""))
    except ValueError:
        return None


def fetch_wiki_html() -> str:
    req = Request(WIKI_URL, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def extract_us_resorts(html: str) -> list[dict]:
    """Parse the Wikipedia comparison table into a list of resort dicts."""
    tp = TableParser()
    tp.feed(html)

    # Find the table that has the most rows (likely the comparison table)
    best = max(tp.tables, key=lambda t: t.count("<tr"))

    rp = RowParser()
    rp.feed(best)

    if not rp.rows:
        raise RuntimeError("No rows parsed from table")

    # Determine header row — first row with multiple cells
    header_row = None
    for row in rp.rows[:5]:
        if len(row) >= 8:
            header_row = row
            break

    if header_row is None:
        # Fall back: just print first few rows for debug
        for i, r in enumerate(rp.rows[:5]):
            print(f"  row {i}: {r}")
        raise RuntimeError("Could not find header row with >=8 columns")

    print(f"Header ({len(header_row)} cols): {header_row}")

    # Normalize column names
    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", strip_refs(s).lower())

    headers = [norm(h) for h in header_row]

    def col(name: str) -> int | None:
        for i, h in enumerate(headers):
            if name in h:
                return i
        return None

    idx_name = col("resort") or col("name") or 0
    idx_state = col("state") or col("province") or col("location")
    idx_vertical = col("vertical")
    idx_peak = col("peak") or col("summit") or col("top")
    idx_base = col("base") or col("bottom")
    idx_trails = col("trail") or col("run")
    idx_lifts = col("lift")
    idx_acres = col("skiable") or col("acreage") or col("area")
    idx_snow = col("snowfall") or col("snow")

    print(f"Column indices: name={idx_name}, state={idx_state}, "
          f"vertical={idx_vertical}, peak={idx_peak}, base={idx_base}, "
          f"trails={idx_trails}, lifts={idx_lifts}, acres={idx_acres}, snow={idx_snow}")

    us_states = {
        "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD",
        "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH",
        "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY",
    }

    us_state_names = {
        "alaska", "alabama", "arizona", "arkansas", "california", "colorado",
        "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
        "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
        "maine", "maryland", "massachusetts", "michigan", "minnesota",
        "mississippi", "missouri", "montana", "nebraska", "nevada",
        "new hampshire", "new jersey", "new mexico", "new york",
        "north carolina", "north dakota", "ohio", "oklahoma", "oregon",
        "pennsylvania", "rhode island", "south carolina", "south dakota",
        "tennessee", "texas", "utah", "vermont", "virginia", "washington",
        "west virginia", "wisconsin", "wyoming",
    }

    resorts = []
    data_rows = rp.rows[rp.rows.index(header_row) + 1:]

    for row in data_rows:
        if len(row) < max(filter(None, [idx_name, idx_state, idx_vertical]), default=0) + 1:
            continue

        name = strip_refs(row[idx_name]) if idx_name is not None else ""
        state = strip_refs(row[idx_state]).strip() if idx_state is not None else ""

        if not name or name.lower() in ("resort", "name"):
            continue

        # Filter to US only
        state_up = state.upper()
        state_lo = state.lower()
        if state_up not in us_states and state_lo not in us_state_names:
            continue

        def safe_get(idx: int | None) -> str:
            if idx is None or idx >= len(row):
                return ""
            return row[idx]

        vertical = parse_int(safe_get(idx_vertical))
        peak = parse_int(safe_get(idx_peak))
        base = parse_int(safe_get(idx_base))
        trails = parse_int(safe_get(idx_trails))
        lifts = parse_int(safe_get(idx_lifts))
        acres = parse_int(safe_get(idx_acres))
        snow = parse_int(safe_get(idx_snow))

        resorts.append({
            "name": name,
            "state": state,
            "vertical_ft": vertical,
            "peak_ft": peak,
            "base_ft": base,
            "trails": trails,
            "lifts": lifts,
            "skiable_acres": acres,
            "avg_snowfall_in": snow,
            "lat": None,
            "lon": None,
        })

    return resorts


# ---------------------------------------------------------------------------
# Nominatim geocoding
# ---------------------------------------------------------------------------

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
        print(f"  geocode error for '{name}': {exc}")
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Fetching Wikipedia comparison table...")
    html = fetch_wiki_html()
    print(f"Downloaded {len(html):,} bytes")

    resorts = extract_us_resorts(html)
    print(f"\nFound {len(resorts)} US resorts in table")

    print("\nGeocoding (1.1 s/request)...")
    for i, r in enumerate(resorts):
        if r["lat"] is not None:
            continue
        coords = geocode(r["name"], r["state"])
        if coords:
            r["lat"], r["lon"] = coords
            print(f"  [{i+1}/{len(resorts)}] {r['name']}, {r['state']} -> {coords[0]:.4f}, {coords[1]:.4f}")
        else:
            print(f"  [{i+1}/{len(resorts)}] {r['name']}, {r['state']} -> NOT FOUND")
        time.sleep(1.1)

    geocoded = sum(1 for r in resorts if r["lat"] is not None)
    print(f"\nGeocoded: {geocoded}/{len(resorts)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(resorts, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved -> {OUT}")


if __name__ == "__main__":
    main()
