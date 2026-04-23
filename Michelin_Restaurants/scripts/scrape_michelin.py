"""Scrape US Michelin-starred restaurants via Playwright.

Michelin's guide.michelin.com sits behind Cloudflare with TLS fingerprinting,
so plain `requests` gets 403'd. Playwright drives real Chromium, inherits the
Didomi consent cookie set on the first pageview, then runs all subsequent
HTTP via in-page `fetch()` (which rides the same connection and cookies).

Pipeline:
  1. Enumerate US state listing pages
     (e.g. /us/en/california/restaurants/all-starred)
     — state slugs known to have Michelin coverage.
  2. Harvest detail URLs per state, filtering by path[2] == slug so we skip
     foreign restaurants that land on US-locale pages.
  3. For each detail URL: parse the <script type="application/ld+json">
     Restaurant schema — contains address, phone, lat/lon, cuisine, star.
  4. Detect Cloudflare soft-block responses (fast 202 w/o Restaurant schema
     marker) and retry with backoff.
  5. Drop entries that came back with no starRating (Michelin sometimes lists
     "Plate" entries on all-starred pages by mistake).

Output: data/michelin_us_raw.json with 270-280 records.

Usage:
    pip install playwright
    playwright install chromium
    python scripts/scrape_michelin.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "michelin_us_raw.json"

# US states known to have Michelin coverage (2026). If Michelin expands to new
# states, add slugs here. `pages` is the number of 52-per-page listing pages.
US_STATES = {
    "california": 2,
    "new-york-state": 2,
    "florida": 1,
    "district-of-columbia": 1,
    "illinois": 1,
    "texas": 1,
    "colorado": 1,
    "georgia": 1,
    "south-carolina": 1,
    "louisiana": 1,
    "tennessee": 1,
    "north-carolina": 1,
    "massachusetts": 1,
}


def build_scrape_fn() -> str:
    """In-page JS run via page.evaluate(). All network from one browser context.

    Returned as a string so we can hand it to Playwright's evaluate() without
    loading the page JS bundle ourselves.
    """
    return r"""
async (config) => {
  const { states } = config;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const jitter = () => 1500 + Math.floor(Math.random() * 1000);

  // 1. Harvest detail URLs per state.
  const urlSet = new Set();
  for (const [slug, pages] of Object.entries(states)) {
    for (let p = 1; p <= pages; p++) {
      const listUrl = p === 1
        ? `https://guide.michelin.com/us/en/${slug}/restaurants/all-starred`
        : `https://guide.michelin.com/us/en/${slug}/restaurants/all-starred/page/${p}`;
      const r = await fetch(listUrl, { credentials: "include" });
      if (!r.ok) continue;
      const doc = new DOMParser().parseFromString(await r.text(), "text/html");
      Array.from(doc.querySelectorAll('a[href*="/restaurant/"]'))
        .map(a => a.getAttribute("href"))
        .filter(h => h && h.split('/restaurant/').length === 2)
        .filter(h => h.split("/").filter(Boolean)[2] === slug)
        .forEach(h => urlSet.add("https://guide.michelin.com" + h));
      await sleep(600);
    }
  }

  const urls = [...urlSet];

  // 2. Fetch each detail page. We pull both:
  //    (a) JSON-LD schema.org Restaurant record (machine-readable, structured)
  //    (b) enrichment via CSS selectors on the rendered HTML — full review
  //        text (JSON-LD truncates at ~280 chars) and the restaurant's own
  //        external website (not exposed in JSON-LD at all).
  async function fetchDetail(url, attempt = 1) {
    const r = await fetch(url, { credentials: "include" });
    if (!r.ok) return { err: `status_${r.status}` };
    const html = await r.text();
    // Cloudflare soft-block: 202 with challenge HTML lacking Restaurant schema.
    if (!html.includes('"@type":"Restaurant"') && !html.includes('@type": "Restaurant')) {
      if (attempt < 3) {
        await sleep(5000 + Math.random() * 3000);
        return fetchDetail(url, attempt + 1);
      }
      return { err: "rate_limited_after_retries" };
    }

    // JSON-LD
    const m = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
    if (!m) return { err: "no_jsonld_tag" };
    let record;
    try { record = JSON.parse(m[1]); }
    catch (e) { return { err: "parse_" + e.message }; }

    // HTML-scraped enrichment
    const doc = new DOMParser().parseFromString(html, "text/html");
    record.full_review = doc.querySelector('.data-sheet__description')
      ?.textContent?.trim().replace(/\s+/g, ' ') || null;
    const visitBtn = Array.from(doc.querySelectorAll('a'))
      .find(a => /Visit Website/i.test(a.textContent));
    record.external_website = visitBtn?.getAttribute('href') || null;

    return { data: record };
  }

  const restaurants = [];
  const errors = [];
  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    const { data, err } = await fetchDetail(url);
    if (data) restaurants.push({ url, ...data });
    else errors.push({ url, err });
    await sleep(jitter());
    if ((i + 1) % 25 === 0) await sleep(3000);
  }

  return { harvested: urls.length, success: restaurants.length, errors, restaurants };
}
"""


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context()
        page = ctx.new_page()

        # Warmup: load a page so Cloudflare sets cookies for the origin.
        print("warming Cloudflare session...")
        page.goto("https://guide.michelin.com/us/en/restaurants/all-starred", wait_until="domcontentloaded")

        print(f"scraping {len(US_STATES)} US states...")
        result = page.evaluate(build_scrape_fn(), {"states": US_STATES})
        browser.close()

    # Drop entries missing starRating (Michelin occasionally lists Plate-level
    # entries on all-starred pages — not actually starred).
    kept = [r for r in result["restaurants"] if r.get("starRating")]
    dropped = [{"url": r["url"], "name": r.get("name")}
               for r in result["restaurants"] if not r.get("starRating")]

    output = {
        "attempted": result["harvested"],
        "success": len(kept),
        "dropped_no_star": dropped,
        "errors": result["errors"],
        "restaurants": kept,
    }
    OUT.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"wrote {OUT}")
    print(f"  attempted: {result['harvested']}")
    print(f"  success:   {len(kept)}")
    print(f"  dropped (Plate): {len(dropped)}")
    print(f"  errors:    {len(result['errors'])}")
    return 0 if result["errors"] == [] else 1


if __name__ == "__main__":
    sys.exit(main())
