"""Scrape US restaurants featured on Diners, Drive-Ins and Dives via Playwright.

Food Network's foodnetwork.com doesn't bot-wall the restaurant listing pages
as aggressively as Michelin (no Cloudflare TLS challenge), so a standalone
Playwright session works cleanly. The approach still uses in-page fetch()
calls so the whole scrape runs in a single browser context with consistent
cookies and origin.

Pipeline:
  1. Harvest detail URLs from the paginated A-Z listing (86 pages of ~15
     restaurants each, filtered to US states — the slug structure
     /restaurants/<state>/<slug> or /restaurants/<state>/<city>/<slug>).
  2. For each detail URL, pull the schema.org Restaurant JSON-LD (name,
     description, address, geo, phone, image, rating, restaurant's own
     website) plus HTML enrichment for fields not in JSON-LD:
       - "Special Dishes: ..." paragraph (what Guy featured)
       - Episode titles from anchors pointing at /shows/.../episodes/...
  3. Strip the per-restaurant review array from the payload to keep
     ddd_raw.json small (~3 MB vs ~15+ MB with reviews).

Not all Food Network listings include geo.latitude in their JSON-LD (~27%
miss it). Run `scripts/geocode_missing.py` after this script to backfill
those via Nominatim.

Output: data/ddd_raw.json

Usage:
    pip install playwright
    playwright install chromium
    python scripts/scrape_ddd.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "ddd_raw.json"


def build_scrape_fn() -> str:
    """In-page JS run via page.evaluate(). All network from one browser
    context so cookies / headers stay consistent across the ~1,225 detail
    fetches.
    """
    return r"""
async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const jitter = () => 800 + Math.floor(Math.random() * 600);

  // 1. Harvest detail URLs from the A-Z listing (86 paginated pages).
  const base = "https://www.foodnetwork.com/restaurants/shows/diners-drive-ins-and-dives/a-z";
  const US_STATES = /^(al|ak|az|ar|ca|co|ct|de|fl|ga|hi|id|il|in|ia|ks|ky|la|me|md|ma|mi|mn|ms|mo|mt|ne|nv|nh|nj|nm|ny|nc|nd|oh|ok|or|pa|ri|sc|sd|tn|tx|ut|vt|va|wa|wv|wi|wy|dc|pr)$/;
  const urlSet = new Set();
  for (let p = 1; p <= 86; p++) {
    const u = p === 1 ? base : `${base}/p/${p}`;
    const r = await fetch(u, { credentials: "include" });
    if (!r.ok) continue;
    const doc = new DOMParser().parseFromString(await r.text(), "text/html");
    Array.from(doc.querySelectorAll('a[href*="/restaurants/"]'))
      .map(a => a.getAttribute('href'))
      .forEach(h => {
        if (!h || h.includes('/shows/') || h.includes('/a-z')
            || h.includes('/packages/') || h.includes('/photos/')) return;
        const path = h.startsWith('//') ? h.slice('//www.foodnetwork.com'.length)
          : h.startsWith('/') ? h
          : h.startsWith('http') ? new URL(h).pathname : null;
        if (!path || !path.startsWith('/restaurants/')) return;
        const parts = path.split('/').filter(Boolean);
        // /restaurants/<state>/<slug>  or  /restaurants/<state>/<city>/<slug>
        if (parts.length !== 3 && parts.length !== 4) return;
        if (!US_STATES.test(parts[1].toLowerCase())) return;
        urlSet.add('https://www.foodnetwork.com' + path);
      });
    if (p % 20 === 0) await sleep(600); else await sleep(250);
  }

  const urls = [...urlSet];

  // 2. Scrape each detail page.
  async function fetchDetail(url) {
    const r = await fetch(url, { credentials: "include" });
    if (!r.ok) return { err: `status_${r.status}` };
    const html = await r.text();
    const doc = new DOMParser().parseFromString(html, "text/html");

    // Find the Restaurant JSON-LD (pages often have multiple ld+json blocks).
    let restaurant = null;
    for (const s of doc.querySelectorAll('script[type="application/ld+json"]')) {
      try {
        const data = JSON.parse(s.textContent);
        const arr = Array.isArray(data) ? data : [data];
        for (const d of arr) {
          if (d && d['@type'] === 'Restaurant') { restaurant = d; break; }
        }
      } catch (e) { /* skip bad ld+json */ }
      if (restaurant) break;
    }
    if (!restaurant) return { err: "no_restaurant_jsonld" };

    // HTML enrichment
    const paragraphs = Array.from(doc.querySelectorAll('p'))
      .map(p => p.textContent.trim().replace(/\s+/g, ' '));
    const dishesP = paragraphs.find(t => /^Special Dishes:/i.test(t));
    const special_dishes = dishesP ? dishesP.replace(/^Special Dishes:\s*/i, '').trim() : null;

    const episodes = [...new Set(
      Array.from(doc.querySelectorAll('a[href*="/shows/diners-drive-ins-and-dives/episodes/"]'))
        .map(a => a.textContent.trim())
        .filter(t => t && t.length < 120)
    )].slice(0, 10);

    // Keep only fields we'll render — strip review[] to save space.
    return { data: {
      url,
      name: restaurant.name,
      description: restaurant.description,
      site_url: restaurant.url || null,
      image: restaurant.image || null,
      telephone: restaurant.telephone || null,
      address: restaurant.address || {},
      geo: restaurant.geo || {},
      aggregateRating: restaurant.aggregateRating || null,
      special_dishes,
      episodes
    }};
  }

  const restaurants = [];
  const errors = [];
  for (let i = 0; i < urls.length; i++) {
    const { data, err } = await fetchDetail(urls[i]);
    if (data) restaurants.push(data);
    else errors.push({ url: urls[i], err });
    await sleep(jitter());
    if ((i + 1) % 50 === 0) await sleep(2000);
  }

  return {
    attempted: urls.length,
    success: restaurants.length,
    errors,
    haveSite: restaurants.filter(r => r.site_url).length,
    haveDishes: restaurants.filter(r => r.special_dishes).length,
    haveEpisodes: restaurants.filter(r => r.episodes?.length > 0).length,
    haveGeo: restaurants.filter(r => r.geo?.latitude && r.geo?.longitude).length,
    restaurants
  };
}
"""


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context()
        page = ctx.new_page()

        print("warming session...")
        page.goto(
            "https://www.foodnetwork.com/restaurants/shows/diners-drive-ins-and-dives/a-z",
            wait_until="domcontentloaded",
        )

        print("scraping (this takes ~20 minutes for ~1,225 pages)...")
        result = page.evaluate(build_scrape_fn())
        browser.close()

    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"  attempted: {result['attempted']}")
    print(f"  success:   {result['success']}")
    print(f"  haveSite:  {result['haveSite']}")
    print(f"  haveDishes: {result['haveDishes']}")
    print(f"  haveEpisodes: {result['haveEpisodes']}")
    print(f"  haveGeo:   {result['haveGeo']}  (run geocode_missing.py to backfill the rest)")
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
