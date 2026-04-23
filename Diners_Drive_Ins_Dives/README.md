# Diners, Drive-Ins and Dives Content Pack for ForeFlight

**Download:** [Diners_Drive_Ins_Dives_Pack.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Diners_Drive_Ins_Dives/Diners_Drive_Ins_Dives_Pack.zip?raw=true)

A ForeFlight content pack containing every restaurant featured on Guy Fieri's **Diners, Drive-Ins and Dives** (Food Network), as a single toggleable map layer with rich-HTML tap popups. Each pin shows the restaurant name, the dishes Guy actually featured on the show, the full Food Network blurb, every DDD episode it appeared on, and clickable phone / website / Apple-Maps address.

**Current version:** `2026.04.23` (abbreviation `DDD.V1`)
**Restaurants:** 1,149 (US locations from the [Food Network DDD A–Z listing](https://www.foodnetwork.com/restaurants/shows/diners-drive-ins-and-dives/a-z), filtered to those with usable coordinates)
**Pack size:** ~380 KB zipped

## Content Overview

The pack ships a single KML layer in `pack/layers/` — `Diners_Drive_Ins_Dives.kml` — with all per-restaurant detail embedded directly in each placemark's tap popup as inline HTML. No separate waypoint database, no PDFs. (See [../PACK_FORMAT.md](../PACK_FORMAT.md) §2.1 — layer placemarks in ForeFlight cannot attach PDFs; that's a `navdata/`-only feature. Keeping everything in the layer KML means one clean toggle and rich popup content with no extra entries cluttering the layer selector.)

This is the $100-hamburger destination list for pilots who plan their cross-countries around food. It pairs naturally with [Airport_Restaurants](../Airport_Restaurants/) (dining *at* airports), [Michelin_Restaurants](../Michelin_Restaurants/) (the upscale end), and DDD (Guy Fieri's roadside spots, anywhere Guy visited — usually well outside walking distance of a runway).

### What you get when you tap a pin

Each placemark's popup renders as a formatted HTML card containing:

- Restaurant name (large) with a "DINERS, DRIVE-INS AND DIVES" brand header
- City / state and Food Network user rating (where present, e.g. ★ 4.6 from 9 reviews)
- **Tappable phone** (opens the dialer)
- **Tappable website** (opens the restaurant's own site in Safari)
- **Tappable address** (opens Apple Maps pinned to the restaurant)
- **Special Dishes** — the specific items Guy featured on the show
- **About** — Food Network's blurb (Guy's visit, atmosphere, signature stuff)
- **Featured On** — every DDD episode this restaurant appeared on
- Clickable "View on Food Network →" link back to the listing

Sizing is tuned for ForeFlight's Description renderer on iPad — the renderer scales inline CSS px ~2.5–3× smaller than a browser, so device-tested baselines from [../PACK_FORMAT.md](../PACK_FORMAT.md) §6 are used: body 30px, restaurant name 52px, section labels 26px, footer 22px.

### Source

Restaurants are scraped from the [Food Network's DDD A–Z listing](https://www.foodnetwork.com/restaurants/shows/diners-drive-ins-and-dives/a-z) (86 paginated pages → ~1,225 detail URLs). For each restaurant we pull the embedded `<script type="application/ld+json">` schema.org `Restaurant` record (name, description, address, phone, geo, restaurant's own website, image, aggregate rating) plus HTML enrichment for fields not in JSON-LD: the "Special Dishes:" paragraph and the linked DDD episode titles.

About 27% of Food Network's listings don't include `geo.latitude` in their JSON-LD; those records are backfilled with a Nominatim (OpenStreetMap) lookup keyed off the structured address. About 75 restaurants ultimately can't be plotted (Nominatim doesn't find them) and are dropped from the pack — that's why the published count (1,149) is below the harvested count (1,224).

## Build pipeline

```
scripts/
├── scrape_ddd.py          Playwright → data/ddd_raw.json
│                          (JSON-LD + special dishes + episodes per restaurant)
├── geocode_missing.py     Nominatim backfill for records without geo.latitude
├── build_layer_kml.py     JSON → pack/layers/Diners_Drive_Ins_Dives.kml
├── validate_pack.py       pre-zip gate (non-ASCII, color, tessellate, etc.)
└── package.py             manifest bump + validate + zip
```

To rebuild against the current Food Network database:

```bash
pip install playwright
playwright install chromium
cd Diners_Drive_Ins_Dives
python scripts/scrape_ddd.py            # ~20 min, ~1,225 detail pages
python scripts/geocode_missing.py       # ~6 min, fills geo for ~330 records via Nominatim
python scripts/build_layer_kml.py
python scripts/package.py               # writes Diners_Drive_Ins_Dives_Pack.zip
```

## Importing the Content Pack into ForeFlight

Detailed instructions: [ForeFlight Content Packs Support](https://www.foreflight.com/support/content-packs/).

1. Download the ZIP using the link at the top of this README.
2. On iOS/iPadOS: open in Safari → Downloads → Share → **ForeFlight**.
3. ForeFlight will unpack and install the pack.
4. Restart ForeFlight if layers don't appear immediately.
5. In ForeFlight: **More → Content Packs**, toggle the pack on. On the **Maps** view, enable the pack's layers from the layer selector.

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
