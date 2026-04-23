# Michelin Restaurants Content Pack for ForeFlight

**Download:** [Michelin_Restaurants_Pack.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Michelin_Restaurants/Michelin_Restaurants_Pack.zip?raw=true)

A ForeFlight content pack containing every MICHELIN-starred restaurant in the United States (2026 edition), rendered as three independently toggleable map layers — one per star tier. Tap any pin to see the restaurant name, star tier, cuisine, price, clickable phone / website / Apple-Maps address, and the full MICHELIN inspector review.

**Current version:** `2026.04.23` (abbreviation `MR.V2`)
**Restaurants:** 272 (all 13 US states/districts covered by the MICHELIN Guide)
**Pack size:** ~130 KB zipped

## Content Overview

The pack ships **three map layers** — one per star tier — with all per-restaurant detail embedded directly in each placemark's tap popup. No separate waypoint database, no PDFs. (ForeFlight's rich-waypoint PDF feature only works on `navdata/` waypoints, not `layers/` placemarks — see [../PACK_FORMAT.md](../PACK_FORMAT.md). Keeping everything in the layer KMLs means one clean toggle per star tier and no extra entries cluttering the layer selector.)

### Map layers — one per star tier

Each layer is a separate toggle in ForeFlight so you can enable just the very best, or all three for full coverage:

| Layer | Tier | Restaurants | Marker |
|---|---|---|---|
| `Michelin_Three_Stars.kml` | ⭐⭐⭐ Exceptional cuisine — "worth a special journey" | 14 | large red |
| `Michelin_Two_Stars.kml` | ⭐⭐ Excellent cooking — "worth a detour" | 40 | medium orange |
| `Michelin_One_Star.kml` | ⭐ High quality cooking — "worth a stop" | 218 | small yellow |

Icon size and color scale with tier so the hierarchy stays readable when multiple layers are on at once.

### What you get when you tap a pin

Each placemark's popup renders as a formatted HTML card containing:

- Red MICHELIN-style star glyphs and tier label (Three Stars / Two Stars / One Star)
- Star-meaning tagline ("worth a special journey" etc.)
- Restaurant name, cuisine, price tier, reservations status
- **Tappable phone** (opens the dialer)
- **Tappable website** (opens Safari)
- **Tappable address** (opens Apple Maps pinned to the restaurant)
- **Full inspector review** (the complete MICHELIN text, not truncated)
- **Tappable link back to the MICHELIN Guide listing**

### State coverage

California (85), New York (75), Florida (27), Washington DC (22), Illinois (20), Texas (18), Colorado (9), Georgia (8), South Carolina (4), Louisiana (3), Tennessee (3), North Carolina (1), Massachusetts (1).

These are the 13 US states/districts the MICHELIN Guide covers as of the 2025–2026 cycle. Pennsylvania, Nevada, Oregon, Arizona, Washington State, and others are *not* yet rated by MICHELIN and have no restaurants in the pack.

### Why this is useful for pilots

The $1,000-hamburger list. Pair with [Airport_Restaurants](../Airport_Restaurants/) (dining *at* airports) and [Diners_Drive_Ins_Dives](../Diners_Drive_Ins_Dives/) (Guy Fieri's roadside spots) for a full spectrum of cross-country destinations — MICHELIN covers the upscale end, where reservations matter and most restaurants are an Uber ride from the closest GA airport. Great for destination planning when the flight itself is the excuse.

### Source

Data is scraped from [guide.michelin.com](https://guide.michelin.com/us/en/restaurants/all-starred) — specifically the per-state "all-starred" listings — and pulled out of each restaurant's embedded `<script type="application/ld+json">` schema.org `Restaurant` record, which includes pre-geocoded latitude/longitude (no separate geocoding step). All restaurant names, addresses, and review excerpts are owned by MICHELIN; this pack is provided for personal use by pilots planning trips.

The scrape is bot-walled by Cloudflare with TLS fingerprinting, so the pipeline drives a real Chromium via Playwright to inherit a valid browser session. See `scripts/scrape_michelin.py` for the implementation.

## Build pipeline

```
scripts/
├── scrape_michelin.py       Playwright → data/michelin_us_raw.json
│                            (JSON-LD + full review + external website)
├── build_layer_kmls.py      JSON → pack/layers/*.kml (3 files, rich HTML descriptions)
├── validate_pack.py         pre-zip gate (non-ASCII, color, tessellate, etc.)
└── package.py               manifest bump + validate + zip
```

To rebuild against the current MICHELIN Guide:

```bash
pip install playwright
playwright install chromium
cd Michelin_Restaurants
python scripts/scrape_michelin.py     # ~10 min, 272 detail pages
python scripts/build_layer_kmls.py
python scripts/package.py             # writes Michelin_Restaurants_Pack.zip
```

### About `MR.V2`

This pack bumped its `abbreviation` from `MR.V1` to `MR.V2` when it moved from a layers + navdata + PDFs architecture to layers-only (richer HTML in each placemark's tap popup). The bump is deliberate — dropping 272 `navdata` waypoints from a previously-installed pack can cause ForeFlight to refuse the update, so the change of abbreviation presents `MR.V2` to ForeFlight as a fresh pack identity. If you had `MR.V1` installed, it's safe to leave it in place while installing `MR.V2`, or uninstall `MR.V1` first for a cleaner layer list.

## Importing the Content Pack into ForeFlight

Detailed instructions: [ForeFlight Content Packs Support](https://www.foreflight.com/support/content-packs/).

1. Download the ZIP using the link at the top of this README.
2. On iOS/iPadOS: open in Safari → Downloads → Share → **ForeFlight**.
3. ForeFlight will unpack and install the pack.
4. Restart ForeFlight if layers don't appear immediately.
5. In ForeFlight: **More → Content Packs**, toggle the pack on. On the **Maps** view, enable each of the three Michelin layers independently from the layer selector.

*Note: Content packs require manual re-download for updates, unless using the Cloud Storage sync described below.*

## Addendum: Syncing Content Packs via Cloud Storage (e.g., OneDrive)

For users who want to easily manage and sync content packs across multiple devices, you can integrate a cloud storage service like Microsoft OneDrive with ForeFlight. This setup allows you to host the content pack .zip file in a shared folder, where it can automatically sync across your devices via OneDrive. Once integrated, new or updated .zip files placed in the designated folder will appear in ForeFlight's **More → Downloads** section for import. With ForeFlight's Automatic Content Packs Download setting (enabled by default in recent versions), packs can download automatically, and updates (e.g., replacing the .zip with a newer version) can be handled by re-importing the revised file.

**Note:** This feature requires a ForeFlight Pro or higher subscription plan for Cloud Documents integration. Content packs do not auto-update in-place; you must replace the .zip file with an updated version (ideally including a version number in the optional manifest.json for tracking) and re-import it. However, the cloud sync ensures the latest .zip is available on all linked devices.

### Steps to Integrate OneDrive with ForeFlight

1. **Sign in to ForeFlight Web:** Go to [plan.foreflight.com](https://plan.foreflight.com) and log in with your ForeFlight account (as an administrator if using a multi-pilot account).
2. **Navigate to Documents:** In the sidebar, click on **Documents**.
3. **Add a Cloud Drive:** In the **My Drives** section, click **Add a Cloud Drive**.
4. **Select OneDrive:** From the **Drive Provider** dropdown menu, choose **OneDrive** (supports OneDrive Personal, OneDrive for Business, or SharePoint Online).
5. **Configure the Drive:**
   - Enter a **Drive Name** (e.g., "My OneDrive").
   - Specify the name of an **existing folder** in your OneDrive root level (e.g., "ForeFlightDocs"). If it doesn't exist, create it first in your OneDrive account via the web or app.
6. **Connect and Authorize:** Click **Add Drive**, then sign in with your Microsoft credentials and grant ForeFlight access to the folder.
7. **Verify Integration:** After connecting, the specified OneDrive folder will be linked for hosting documents and content packs. Files added here will sync to ForeFlight.

### Setting Up the "contentpack" Folder for Automatic Sync

1. **Create the Folder:** In your linked OneDrive folder (e.g., "/ForeFlightDocs/"), create a subfolder named exactly **contentpack** (case-sensitive). This is the designated location for content pack .zip files.
   - Full path example: If your linked folder is "ForeFlightDocs", the path would be `/ForeFlightDocs/contentpack/`.
2. **Place the .zip File:** Download the latest content pack .zip from this repository and upload it to the `contentpack` folder in OneDrive. The file will automatically sync across all your devices connected to OneDrive.
3. **Access in ForeFlight:**
   - Open ForeFlight on your iOS/iPadOS device.
   - Go to **More → Downloads**.
   - The content pack should appear automatically under available downloads (thanks to Cloud Documents integration).
   - If Automatic Content Packs Download is enabled (check in ForeFlight Web: Account → Integrations → Cloud Documents), it will download without manual selection.
   - Import the pack as described in the "Importing the Content Pack into ForeFlight" section above.
4. **Handling Updates:**
   - When a new version of the content pack is released, download the new .zip and replace the old one in your OneDrive `/contentpack/` folder.
   - OneDrive will sync the updated file across devices.
   - In ForeFlight, the new version will appear in More → Downloads; import it to apply the update (older versions may show expiration warnings if dates are set in the manifest).

This setup ensures your content pack is always accessible and up-to-date across devices without manual transfers. For more details, refer to ForeFlight's [OneDrive Integration Support](https://support.foreflight.com/hc/en-us/articles/14443946235671-How-can-OneDrive-be-integrated-with-ForeFlight) and [Content Packs Support](https://foreflight.com/support/content-packs/). If using Dropbox instead, the process is similar, with the folder at `~/Dropbox/Apps/ForeFlight/contentpack/`.
