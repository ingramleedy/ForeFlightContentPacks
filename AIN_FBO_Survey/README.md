# AIN FBO Survey 2026 Content Pack for ForeFlight

**Download:** [AIN_FBO_Survey_Pack.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/AIN_FBO_Survey/AIN_FBO_Survey_Pack.zip?raw=true)

A ForeFlight content pack mapping every FBO rated in *Aviation International News*' 45th annual FBO Survey (April 2026 issue, data collected April 2025 – January 2026). Placemarks are color-coded by survey tier so you can instantly see which airports have top-rated FBOs along any route.

**Current version:** `2026.05.18` (abbreviation `AIN26`)
**FBOs mapped:** ~267 (across the Americas and International)
**Pack size:** ~13 KB zipped

## Content Overview

The pack ships **two map layers** — Americas and International. All rating data is embedded in each placemark's tap popup; no separate waypoint database or PDFs.

### Map layers

| Layer | Coverage | FBOs |
|---|---|---|
| `AIN_FBO_Americas.kml` | US, Canada, Caribbean, Brazil | ~228 |
| `AIN_FBO_International.kml` | Europe, Asia-Pacific, Middle East | ~39 |

### Icon color coding by tier

Icons scale in size with tier so the best FBOs are visually prominent when zoomed out:

| Icon | Tier | Meaning |
|---|---|---|
| ⭐ Gold star (large) | Top 5% | Best FBOs worldwide in their segment — consistent excellence across all five categories |
| 🟠 Orange circle | Top 10% | Among the top one-in-ten; strong performers across the board |
| 🟡 Yellow circle | Top 20% | Top quintile; reliably high quality |
| 🔵 Blue circle (small) | Surveyed | Rated but below top 20%; still reported in the survey regional tables |

### What you get when you tap a pin

- **FBO name** and ICAO airport code
- **Score** (out of 5.00)
- **Survey tier** (Top 5% / 10% / 20% / Surveyed)
- **Region** (e.g., Southeast, Rocky Mountain, Europe)
- Source credit: *2026 AIN FBO Survey*

### About the AIN FBO Survey

*Aviation International News* has conducted its annual FBO survey since 1981. For a service provider to reach the highest tier it must demonstrate consistent quality across all five rated categories: line service, passenger amenities, pilot amenities, facilities, and customer service representatives. Only FBOs receiving 20 or more ratings are eligible for published scores. The survey covers roughly 4,500 FBOs worldwide; this pack includes all facilities for which scores appeared in the April 2026 report.

### Why this is useful for pilots

Planning a cross-country? Before you commit to an FBO, check whether there's a top-rated option at your destination or tech-stop airports. The gold-star layer alone covers the 15 highest-rated FBOs in the Americas — pulling up that layer on the route-planning map takes two seconds and can save a frustrating line-service experience.

The "all surveyed" blue layer is equally useful in reverse: if an airport shows a blue pin with a score below 4.0, you know to look at alternates or manage expectations before you arrive.

### Top 5% Americas highlights (2026)

| FBO | Airport | Score |
|---|---|---|
| Pentastar Aviation | KPTK — Oakland County Intl, MI | 4.83 |
| Modern Aviation (formerly American Aero) | KFTW — Fort Worth Meacham, TX | 4.81 |
| Sheltair | KTPA — Tampa Intl, FL | 4.78 |
| Henriksen Jet Center | KEDC — Austin Executive, TX | 4.78 |
| Jet Aviation | KPBI — Palm Beach Intl, FL | 4.78 |
| Banyan Air Service | KFXE — Fort Lauderdale Executive, FL | 4.77 |
| Eagle Aviation | KCAE — Columbia Metropolitan, SC | 4.77 |
| Henriksen Jet Center | KTME — Houston Executive, TX | 4.76 |
| Sheltair | KORL — Orlando Executive, FL | 4.76 |
| Stancraft Jet Center | KCOE — Coeur d'Alene, ID | 4.76 |
| Sun Valley Aviation | KHRL — Valley Intl, TX | 4.75 |
| Sheltair | KDAB — Daytona Beach Intl, FL | 4.74 |
| Galaxy FBO | KCXO — Conroe North Houston Regional, TX | 4.74 |
| Sheltair | KJAX — Jacksonville Intl, FL | 4.73 |

### Top 5% International highlights (2026)

| FBO | Airport | Score |
|---|---|---|
| TAG Aviation Macau | VMMC — Macau Intl | 4.75 (first year eligible) |
| Farnborough Airport | EGLF — Farnborough, UK | 4.69 (19-year reign ended) |

## Build pipeline

```
scripts/
├── build_kml.py        data/fbos_raw.json → pack/layers/*.kml
├── validate_pack.py    pre-zip gate (non-ASCII, color, coordinates, etc.)
└── package.py          manifest bump + validate + zip

data/
└── fbos_raw.json       hand-encoded from the April 2026 AIN FBO Survey PDF
```

To rebuild (e.g., after editing `fbos_raw.json` with new data):

```bash
pip install airportsdata
cd AIN_FBO_Survey
python scripts/build_kml.py
python scripts/package.py     # writes AIN_FBO_Survey_Pack.zip
```

Airport coordinates are looked up at build time from the `airportsdata` package (ICAO database). No external API calls required.

### Source

Data hand-encoded from: *AIN FBO Survey*, Aviation International News, April 2026 issue. Report by Curt Epstein, data by Cam MacPherson. Survey period: April 24, 2025 – January 11, 2026. Source PDF: `2026_ain_fbo_survery.pdf` (root of this pack folder).

All FBO names, scores, and ratings are sourced from AIN's published survey. This pack is provided for personal use by pilots planning trips.

## Importing the Content Pack into ForeFlight

Detailed instructions: [ForeFlight Content Packs Support](https://www.foreflight.com/support/content-packs/).

1. Download the ZIP using the link at the top of this README.
2. On iOS/iPadOS: open in Safari → Downloads → Share → **ForeFlight**.
3. ForeFlight will unpack and install the pack.
4. Restart ForeFlight if layers don't appear immediately.
5. In ForeFlight: **More → Content Packs**, toggle the pack on. On the **Maps** view, enable either or both AIN FBO layers from the layer selector.

*Note: Content packs require manual re-download for updates, unless using the Cloud Storage sync described in the [root README](../README.md#addendum-syncing-content-packs-via-cloud-storage-eg-onedrive).*
