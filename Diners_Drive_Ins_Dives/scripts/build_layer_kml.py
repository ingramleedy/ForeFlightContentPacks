"""Build the single DDD ForeFlight layer KML.

All per-restaurant detail lives in the placemark's HTML description (no
navdata, no PDFs — per PACK_FORMAT.md §2.1 layer placemarks cannot attach
documents). The HTML card shows:

  - Restaurant name (large)
  - City/state meta + Food Network user rating
  - Tappable phone (tel:)
  - Tappable website (https:)
  - Tappable address (maps.apple.com — opens Apple Maps on iPad)
  - "SPECIAL DISHES" Guy featured
  - Food Network blurb (full description)
  - "FEATURED ON" episode titles
  - Link back to Food Network listing

Sizing is tuned for ForeFlight's Description renderer on iPad — the
renderer scales inline CSS px ~2.5–3× smaller than a browser, so body
copy lands at 30px, item names at 52px, section labels at 26px,
footer at 22px (see PACK_FORMAT.md §6 and the reference describe()
in Michelin_Restaurants/scripts/build_layer_kmls.py).

Inline <Style> per Placemark (shared <styleUrl> gets dropped by ForeFlight).
OGC namespace. No <Folder>. CDATA-wrapped descriptions.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "ddd_raw.json"
OUT = ROOT / "pack" / "layers" / "Diners_Drive_Ins_Dives.kml"

# DDD visual brand — bright red pin; color palette for HTML card accents.
ICON_HREF = "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"
ICON_SCALE = 1.0
LABEL_SCALE = 0.8
BRAND_RED = "#D62828"
LINK_BLUE = "#0066CC"
MUTED = "#777777"

# KML <name>/<description> outside CDATA must be ASCII. Description bodies are
# CDATA-wrapped so UTF-8 is fine there, but the <name> (restaurant name in
# the waypoint list) needs ASCII.
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
    # Apple Maps URL scheme — opens Apple Maps on iPad; desktop browsers get
    # a web fallback view.
    q = quote_plus(f"{name}, {address}")
    return f"https://maps.apple.com/?q={q}&ll={lat:.6f},{lon:.6f}"


def link(text: str, href: str, color: str = LINK_BLUE) -> str:
    return (
        f'<a href="{html.escape(href)}" '
        f'style="color:{color};text-decoration:underline;">{text}</a>'
    )


def _rating_line(rating: dict | None) -> str | None:
    if not rating:
        return None
    try:
        val = float(rating.get("ratingValue"))
    except (TypeError, ValueError):
        return None
    count = rating.get("reviewCount")
    try:
        count_n = int(count)
    except (TypeError, ValueError):
        count_n = 0
    # Unicode star + value; count in small muted text.
    if count_n:
        return f"&#9733; {val:.1f} ({count_n} reviews)"
    return f"&#9733; {val:.1f}"


def describe(rec: dict) -> str:
    """HTML description for a single restaurant's tap popup.

    Every styled block gets an explicit inline font-size — ForeFlight's
    Description renderer scales inline CSS px ~2.5–3× smaller than a
    browser, so the device-tested baseline (PACK_FORMAT.md §6) is body
    30px, h2 52px, section labels 26px, footer 22px.
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

    geo = rec.get("geo") or {}
    try:
        lat = float(geo.get("latitude"))
        lon = float(geo.get("longitude"))
    except (TypeError, ValueError):
        lat = lon = 0.0

    phone = rec.get("telephone") or ""
    site_url = rec.get("site_url") or ""
    fn_url = rec.get("url") or ""
    blurb = ascii_safe(rec.get("description") or "")
    dishes = ascii_safe(rec.get("special_dishes") or "")
    episodes = rec.get("episodes") or []

    parts: list[str] = []

    # Header: brand accent + name.
    parts.append(
        f'<div style="color:{BRAND_RED};font-size:26px;font-weight:bold;'
        f'letter-spacing:2px;margin-bottom:6px;">DINERS, DRIVE-INS AND DIVES</div>'
    )
    parts.append(
        f'<h2 style="margin:6px 0 10px 0;font-size:52px;">{html.escape(name)}</h2>'
    )

    # Meta row: city line + rating.
    meta_bits: list[str] = []
    if city_line:
        meta_bits.append(html.escape(city_line))
    rating = _rating_line(rec.get("aggregateRating"))
    if rating:
        meta_bits.append(rating)
    if meta_bits:
        parts.append(
            f'<div style="font-size:30px;margin-bottom:20px;color:{MUTED};">'
            + " &middot; ".join(meta_bits)
            + "</div>"
        )

    # Contact block: clickable phone / website / address.
    contact_rows: list[str] = []
    if phone:
        contact_rows.append(
            f'<div><b>Phone:</b> {link(html.escape(ascii_safe(phone)), phone_uri(phone))}</div>'
        )
    if site_url:
        display = site_url.replace("https://", "").replace("http://", "").rstrip("/")
        contact_rows.append(
            f'<div><b>Web:</b> {link(html.escape(display), site_url)}</div>'
        )
    if full_addr:
        addr_display = html.escape(street)
        if city_line:
            addr_display += "<br/>" + html.escape(city_line)
        contact_rows.append(
            f'<div><b>Address:</b> {link(addr_display, maps_uri(name, lat, lon, full_addr))}</div>'
        )
    if contact_rows:
        parts.append(
            '<div style="font-size:30px;line-height:1.5;margin-bottom:22px;">'
            + "".join(contact_rows)
            + "</div>"
        )

    # Special dishes — what Guy actually featured on the show.
    if dishes:
        parts.append(
            f'<div style="color:{BRAND_RED};font-weight:bold;font-size:26px;'
            f'letter-spacing:1px;margin-bottom:10px;">SPECIAL DISHES</div>'
        )
        parts.append(
            f'<div style="font-size:30px;line-height:1.5;margin-bottom:22px;">'
            f'{html.escape(dishes)}</div>'
        )

    # Food Network blurb.
    if blurb:
        parts.append(
            f'<div style="color:{BRAND_RED};font-weight:bold;font-size:26px;'
            f'letter-spacing:1px;margin-bottom:10px;">ABOUT</div>'
        )
        parts.append(
            f'<div style="font-size:30px;line-height:1.5;margin-bottom:22px;">'
            f'{html.escape(blurb)}</div>'
        )

    # Episodes this restaurant appeared on.
    if episodes:
        eps_clean = [ascii_safe(e) for e in episodes if e]
        eps_clean = [e for e in eps_clean if e]
        if eps_clean:
            parts.append(
                f'<div style="color:{BRAND_RED};font-weight:bold;font-size:26px;'
                f'letter-spacing:1px;margin-bottom:10px;">FEATURED ON</div>'
            )
            eps_html = "<br/>".join(html.escape(e) for e in eps_clean)
            parts.append(
                f'<div style="font-size:30px;line-height:1.5;margin-bottom:22px;">'
                f'{eps_html}</div>'
            )

    # Link back to Food Network listing.
    if fn_url:
        parts.append(
            f'<div style="font-size:30px;">'
            f'{link("View on Food Network &rarr;", fn_url, BRAND_RED)}'
            f"</div>"
        )

    parts.append(
        f'<div style="color:{MUTED};font-size:22px;margin-top:22px;">'
        "Source: Food Network</div>"
    )
    return "".join(parts)


def placemark_xml(rec: dict) -> str:
    name_ascii = ascii_safe(rec.get("name") or "Restaurant")
    desc_html = describe(rec)
    geo = rec.get("geo") or {}
    lat = float(geo.get("latitude"))
    lon = float(geo.get("longitude"))
    return (
        "<Placemark>"
        f"<name>{html.escape(name_ascii)}</name>"
        f"<description><![CDATA[{desc_html}]]></description>"
        "<drawOrder>10</drawOrder>"
        "<Style>"
        f"<IconStyle><scale>{ICON_SCALE}</scale>"
        f"<Icon><href>{ICON_HREF}</href></Icon></IconStyle>"
        f"<LabelStyle><scale>{LABEL_SCALE}</scale></LabelStyle>"
        "</Style>"
        f"<Point><coordinates>{lon:.5f},{lat:.5f},0</coordinates></Point>"
        "</Placemark>"
    )


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    records = data["restaurants"]
    # Only include records with usable coordinates — ~94% coverage after
    # Nominatim fallback; the unplottable ~6% would land at 0,0 if we let them
    # through.
    usable = []
    dropped = 0
    for r in records:
        geo = r.get("geo") or {}
        try:
            float(geo.get("latitude"))
            float(geo.get("longitude"))
        except (TypeError, ValueError):
            dropped += 1
            continue
        usable.append(r)

    print(f"loaded {len(records)} restaurants, {len(usable)} plottable, {dropped} dropped (no geo)")

    placemarks = [placemark_xml(r) for r in usable]
    kml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        "<Document>\n"
        "<name>Diners, Drive-Ins and Dives</name>\n"
        "<open>1</open>\n"
        f"<description>Restaurants featured on Diners, Drive-Ins and Dives "
        f"(Food Network). {len(placemarks)} US locations.</description>\n"
        + "\n".join(placemarks)
        + "\n</Document>\n</kml>\n"
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(kml, encoding="utf-8")
    size_kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT} ({size_kb:.1f} KB, {len(placemarks)} placemarks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
