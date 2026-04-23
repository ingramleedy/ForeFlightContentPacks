"""Build three ForeFlight layer KMLs — one per Michelin star tier.

Each KML in pack/layers/ is a separately-toggleable layer in ForeFlight, so
the pilot can enable just three-star, or all three, etc. Icons are sized and
colored by tier so the hierarchy is visible when multiple layers are on.

Each Placemark carries a full-detail HTML description via CDATA — tapping the
pin shows the entire restaurant page inline: star tier, cuisine/price,
clickable phone (tel:) / website / Apple Maps address, full inspector review,
and a link back to the MICHELIN Guide listing. This is the only channel for
per-pin info in this pack — there are no rich-waypoint PDFs, because layer
placemarks in ForeFlight cannot attach documents (see PACK_FORMAT.md §2.1).

Inline <Style> per Placemark (ForeFlight drops shared styleUrl references).
OGC namespace. No <Folder>.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "michelin_us_raw.json"
OUT_DIR = ROOT / "pack" / "layers"

TIERS = {
    "Three Stars: Exceptional cuisine": {
        "name": "Michelin 3 Stars",
        "file": "Michelin_Three_Stars.kml",
        "icon": "http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
        "scale": 1.3,
        "label_scale": 1.0,
        "stars": 3,
        "star_label": "Three Stars",
        "star_meaning": "Exceptional cuisine — worth a special journey",
    },
    "Two Stars: Excellent cooking": {
        "name": "Michelin 2 Stars",
        "file": "Michelin_Two_Stars.kml",
        "icon": "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png",
        "scale": 1.1,
        "label_scale": 0.9,
        "stars": 2,
        "star_label": "Two Stars",
        "star_meaning": "Excellent cooking — worth a detour",
    },
    "One Star: High quality cooking": {
        "name": "Michelin 1 Star",
        "file": "Michelin_One_Star.kml",
        "icon": "http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png",
        "scale": 0.9,
        "label_scale": 0.8,
        "stars": 1,
        "star_label": "One Star",
        "star_meaning": "High quality cooking — worth a stop",
    },
}

MICHELIN_RED = "#B4161B"
LINK_BLUE = "#0066CC"
MUTED = "#777777"

# ForeFlight KML <name>/<description> outside CDATA must be ASCII. Non-ASCII
# characters (curly quotes, accented names) are replaced with ASCII equivalents
# in the <name>, and any description HTML is CDATA-wrapped so it's unaffected.
ASCII_MAP = str.maketrans({
    "‘": "'", "’": "'",
    "“": '"', "”": '"',
    "–": "-", "—": "-",
    "…": "...",
    "é": "e", "è": "e", "ê": "e", "ë": "e",
    "à": "a", "á": "a", "â": "a", "ä": "a", "å": "a",
    "î": "i", "ï": "i", "í": "i",
    "ó": "o", "ô": "o", "ö": "o", "ø": "o",
    "ú": "u", "û": "u", "ü": "u",
    "ñ": "n", "ç": "c",
    "É": "E", "È": "E",
    "À": "A", "Á": "A",
    "Ó": "O", "Ô": "O",
    "Ü": "U",
})


def ascii_safe(s: str) -> str:
    return (s or "").translate(ASCII_MAP).encode("ascii", errors="ignore").decode("ascii")


def phone_uri(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit() or c == "+")
    return f"tel:{digits}"


def maps_uri(name: str, lat: float, lon: float, address: str) -> str:
    # Apple Maps URL scheme — opens Apple Maps directly on iPad; desktop falls
    # back to a web view.
    q = quote_plus(f"{name}, {address}")
    return f"https://maps.apple.com/?q={q}&ll={lat:.6f},{lon:.6f}"


def link(text: str, href: str, color: str = LINK_BLUE) -> str:
    return (
        f'<a href="{html.escape(href)}" '
        f'style="color:{color};text-decoration:underline;">{text}</a>'
    )


def describe(rec: dict, tier_cfg: dict) -> str:
    """Full-detail HTML description — ASCII-safe, CDATA-wrapped by the caller.

    Everything the pilot needs is here: star tier with meaning, cuisine/price
    metadata, clickable phone/website/address, full inspector review, link
    back to the MICHELIN Guide listing. This is the only per-pin channel —
    layer placemarks cannot attach PDFs.
    """
    name = ascii_safe(rec.get("name") or "Restaurant")

    addr = rec.get("address") or {}
    street = ascii_safe(addr.get("streetAddress") or "")
    city = ascii_safe(addr.get("addressLocality") or "")
    state = ascii_safe(addr.get("addressRegion") or "")
    zip_ = addr.get("postalCode") or ""
    city_line = ", ".join(p for p in [city, state] if p)
    if zip_:
        city_line = f"{city_line} {zip_}".strip()
    full_addr = ", ".join(p for p in [street, city_line] if p)

    lat = float(rec.get("latitude") or 0)
    lon = float(rec.get("longitude") or 0)
    cuisine = ascii_safe(rec.get("servesCuisine") or "")
    price = ascii_safe(rec.get("priceRange") or "")
    phone = rec.get("telephone") or ""
    website = rec.get("external_website") or ""
    michelin_url = rec.get("url") or ""
    reservations = (rec.get("acceptsReservations") or "").lower() == "yes"
    review_text = ascii_safe(
        rec.get("full_review") or (rec.get("review") or {}).get("description") or ""
    )

    stars = tier_cfg["stars"]
    star_label = tier_cfg["star_label"]
    star_meaning = tier_cfg["star_meaning"]

    parts: list[str] = []

    # Header: stars + name + star-meaning tagline.
    # Sizes tuned for ForeFlight's Description view on iPad — the renderer paints
    # our CSS px far smaller than expected, so body copy lands at 30px to read
    # at arm's length without pinch-zoom (verified on device against a zoomed-in
    # reference screenshot).
    star_glyphs = "★" * stars  # ★
    parts.append(
        f'<div style="color:{MICHELIN_RED};font-size:52px;'
        f'font-weight:bold;letter-spacing:2px;">{star_glyphs} '
        f'<span style="color:{MUTED};font-size:30px;letter-spacing:1px;">'
        f'{html.escape(star_label.upper())}</span></div>'
    )
    parts.append(
        f'<h2 style="margin:10px 0 6px 0;font-size:52px;">{html.escape(name)}</h2>'
    )
    parts.append(
        f'<div style="color:{MUTED};font-style:italic;font-size:30px;'
        f'margin-bottom:20px;">{html.escape(star_meaning)}</div>'
    )

    # Meta row: Cuisine · Price · Reservations.
    meta_bits: list[str] = []
    if cuisine:
        meta_bits.append(html.escape(cuisine))
    if price:
        meta_bits.append(html.escape(price))
    if reservations:
        meta_bits.append("Reservations: Yes")
    if meta_bits:
        parts.append(
            f'<div style="font-size:30px;margin-bottom:20px;">'
            + " &middot; ".join(meta_bits)
            + "</div>"
        )

    # Contact block: clickable phone / website / address.
    contact_rows: list[str] = []
    if phone:
        contact_rows.append(
            f'<div><b>Phone:</b> {link(html.escape(ascii_safe(phone)), phone_uri(phone))}</div>'
        )
    if website:
        display = website.replace("https://", "").replace("http://", "").rstrip("/")
        contact_rows.append(
            f'<div><b>Web:</b> {link(html.escape(display), website)}</div>'
        )
    if full_addr:
        addr_display = html.escape(street) + ("<br/>" + html.escape(city_line) if city_line else "")
        contact_rows.append(
            f'<div><b>Address:</b> {link(addr_display, maps_uri(name, lat, lon, full_addr))}</div>'
        )
    if contact_rows:
        parts.append(
            '<div style="font-size:30px;line-height:1.5;margin-bottom:22px;">'
            + "".join(contact_rows)
            + "</div>"
        )

    # Full inspector review.
    if review_text:
        parts.append(
            f'<div style="color:{MICHELIN_RED};font-weight:bold;font-size:26px;'
            f'letter-spacing:1px;margin-bottom:10px;">INSPECTOR&rsquo;S REVIEW</div>'
        )
        parts.append(
            f'<div style="font-size:30px;line-height:1.5;margin-bottom:22px;">'
            f'{html.escape(review_text)}</div>'
        )

    # Link back to MICHELIN Guide.
    if michelin_url:
        parts.append(
            f'<div style="font-size:30px;">'
            f'{link("View on the MICHELIN Guide &rarr;", michelin_url, MICHELIN_RED)}'
            f"</div>"
        )

    parts.append(
        f'<div style="color:{MUTED};font-size:22px;margin-top:22px;">'
        "Source: MICHELIN Guide</div>"
    )
    return "".join(parts)


def placemark_xml(rec: dict, tier_cfg: dict) -> str:
    name_ascii = ascii_safe(rec.get("name") or "Restaurant")
    desc_html = describe(rec, tier_cfg)
    lat = float(rec.get("latitude") or 0)
    lon = float(rec.get("longitude") or 0)
    return (
        "<Placemark>"
        f"<name>{html.escape(name_ascii)}</name>"
        f"<description><![CDATA[{desc_html}]]></description>"
        "<drawOrder>10</drawOrder>"
        "<Style>"
        f"<IconStyle><scale>{tier_cfg['scale']}</scale>"
        f"<Icon><href>{tier_cfg['icon']}</href></Icon></IconStyle>"
        f"<LabelStyle><scale>{tier_cfg['label_scale']}</scale></LabelStyle>"
        "</Style>"
        f"<Point><coordinates>{lon:.5f},{lat:.5f},0</coordinates></Point>"
        "</Placemark>"
    )


def build_layer(name: str, description: str, placemarks: list[str]) -> str:
    header = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        "<Document>\n"
        f"<name>{html.escape(name)}</name>\n"
        "<open>1</open>\n"
        f"<description>{html.escape(description)}</description>\n"
    )
    footer = "</Document>\n</kml>\n"
    return header + "\n".join(placemarks) + "\n" + footer


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    restaurants = data["restaurants"]
    print(f"loaded {len(restaurants)} restaurants from {SRC.name}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for tier_key, cfg in TIERS.items():
        tier_recs = [r for r in restaurants if r.get("starRating") == tier_key]
        placemarks = [placemark_xml(r, cfg) for r in tier_recs
                      if r.get("latitude") and r.get("longitude")]
        kml = build_layer(
            cfg["name"],
            f"MICHELIN {cfg['name'].split()[-2]}-star restaurants ({len(tier_recs)} in US).",
            placemarks,
        )
        out_path = OUT_DIR / cfg["file"]
        out_path.write_text(kml, encoding="utf-8")
        size_kb = out_path.stat().st_size / 1024
        print(f"  {cfg['file']}: {len(placemarks)} placemarks ({size_kb:.1f} KB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
