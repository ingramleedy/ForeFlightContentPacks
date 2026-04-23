# Indian Reservations Content Pack for ForeFlight

**Download:** [Indian_Reservations_Pack.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Indian_Reservations/Indian_Reservations_Pack.zip?raw=true)

This repository provides a **ForeFlight content pack** that overlays all 312 U.S. federal American Indian reservations on your map, plus a separate tappable waypoint layer with per-reservation detail and reference PDFs covering overflight considerations, special airspace, and the legal/operational reality of tribal sovereignty on the ground.

The pack ships two independent layers that toggle separately — a polygon zone layer for spatial awareness, and a points layer for "what is this place, and is there anything I need to know about flying over it?" — plus navdata PDFs and per-tribe rich-waypoint documents for the five reservations with documented tribal overflight assertions (Red Lake, Snoqualmie, Hualapai, Taos Pueblo, Navajo Nation).

**Current version:** `2026.04.20`
**Reservations covered:** 312 (all federal AIANNH types D2 and D8 from the 2024 Census TIGER/Line release)
**Highlighted with red outline/pin:** 5 (documented tribal overflight assertions)
**Pack size:** ~315 KB zipped

## Content Overview

The pack is built from publicly available authoritative sources, stitched together with a reproducible Python pipeline in [`scripts/`](scripts/). Nothing in the pack is hand-fabricated — every airspace claim, demographic number, or tribal citation traces back to a canonical source.

### Layers

| Layer | Type | Purpose |
|---|---|---|
| **Indian Reservations** | KML polygons | All 312 reservations drawn as filled zones. Orange fill with bright-orange outline by default; **red outline + thicker line** for the 5 reservations that have a documented tribal overflight assertion. |
| **Indian Reservations — Points** | KML points | 312 tappable centroid pins, one per reservation, with pilot-first popup detail. Orange pin for most; **red pin** for the same 5 assertion reservations. |

Each layer can be toggled independently in the ForeFlight layer selector.

### Popup detail (per reservation)

Each centroid pin in the Points layer opens a popup with, in order:

1. ⚠ **Tribal overflight assertion** (altitude + summary) — only where documented.
2. **Nearest 3 public airports** with distance in NM.
3. **Overflight courtesy** (AC 91-36D ≥ 2,000 ft AGL) — shown when no specific assertion applies.
4. **Type / States / Area.**
5. **Tribal government / Federal recognition date** — from Wikidata, where available.
6. **Population (2020) / Housing / Language** — from Census ACS 5-year (2022) and Wikidata.
7. **Official tribal website** — from Wikidata.
8. Pointer to `navdata/Overflight_Considerations.pdf` for the full treatment.

### Navdata (PDFs and waypoint CSV)

- **`Overflight_Considerations.pdf`** — the reference document. Covers AC 91-36D, 14 CFR 91.119, NPATMA, FAA Order 1210.20, the airspace-vs-ground legal split (*Montana v. United States*), five documented tribal overflight ordinances, and a full treatment of the October 2025 Red Lake / Smedsmo incident through the March 2026 settlement status.
- **`Special_Airspace_Tribal.pdf`** — Grand Canyon SFRA, Taos Pueblo sectional note, NPATMA ATMPs, and Red Lake context. Generic fallback for the other reservations.
- **`{WAYPOINT}Special_Airspace_Tribal.pdf`** — per-tribe PDFs for the 5 rich waypoints (HUALAPAI, HAVASUPAI, NAVAJO, TAOSPUEB, REDLAKE). Each combines a curated tribe stub (history, government, aviation notes, sources) with the enrichment data (nearest airports, demographics, tribal assertion).
- **`Reservation_Centroids.csv`** — 312 searchable waypoints in ForeFlight's `WAYPOINT_NAME,Description,Lat,Lon` format. Rich waypoints (the 5 above) automatically link to their per-tribe PDF via ForeFlight's `WAYPOINT_NAMEDocumentName.pdf` naming convention.

## Why this pack exists

Tribal lands occupy a surprisingly large footprint in U.S. airspace routes, and a pilot flying over them needs to know three things that are hard to get from any one source:

1. **Where the reservations actually are** — boundaries aren't on sectionals except in rare cases (e.g., Taos Pueblo).
2. **What airspace rules or advisories apply** — most tribal overflight requests are not FAA-codified; the pack separates the ones that ARE (Grand Canyon SFRA, Taos Pueblo MOA) from the ones that are tribal-code assertions only.
3. **What happens if you end up on the ground** — the October 2025 Red Lake / Smedsmo incident made clear that federal airspace preemption does **not** prevent months-long aircraft-recovery disputes when an emergency landing puts a plane on tribal land. The Overflight_Considerations.pdf has a full "If you land on tribal land" section with operational guidance, including contacting AOPA Legal Services before making statements to tribal authorities.

This pack is **situational awareness, not legal advice**, and is explicitly built on citable sources only. Tribes without a documented public overflight assertion are not assigned one.

## Highlighted reservations (red outline + red pin)

These five have documented tribal overflight ordinances or MOAs that pilots should be aware of, beyond the generic AC 91-36D advisory:

| Reservation | Claimed altitude | Source |
|---|---|---|
| Red Lake Reservation (MN) | 20,000 ft | Red Lake Band Resolution No. 59-78 (1978); cited in the 2025 Smedsmo incident |
| Snoqualmie Reservation (WA) | 500 ft general / 2,000 ft near Snoqualmie Falls | Snoqualmie Tribal Airspace Protection Act, 2024 |
| Hualapai Indian Reservation (AZ) | 15,000 ft | Asserted after 2009 paraglider incident; settled |
| Taos Pueblo (NM) | 5,000 ft | Taos Pueblo / FAA MOA, 2011 (sectional-cited) |
| Navajo Nation Reservation (AZ/NM/UT) | Park-specific | Navajo Nation Parks & Recreation permitting rules (Monument Valley, Canyon de Chelly, Lake Powell, Little Colorado River Gorge) |

**None of these are enforceable against pilots by the FAA** — airspace is federal jurisdiction. They matter on the ground, where tribal sovereignty applies.

## Sources and credits

The pack stitches data from these authoritative sources:

- **[U.S. Census Bureau TIGER/Line AIANNH](https://www.census.gov/geographies/mapping-files.html)** — reservation boundaries and demographics (population, housing, states). Accessed via the ArcGIS republish at `services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/Federal_American_Indian_Reservations_v1`.
- **[U.S. Census ACS 5-year (2022)](https://api.census.gov/data/2022/acs/acs5)** — population, housing units.
- **[OurAirports](https://ourairports.com/)** — public-use US airports for the nearest-3 calculation. CSV at `davidmegginson.github.io/ourairports-data/airports.csv`.
- **[Wikidata](https://www.wikidata.org/)** — tribal government name, federal-recognition date, languages, official websites. Retrieved via `wbsearchentities` + `wbgetentities` per reservation.
- **[FAA AC 91-36D](https://www.faa.gov/regulations_policies/advisory_circulars)** — Visual Flight Rules (VFR) Flight Near Noise-Sensitive Areas.
- **[14 CFR 93 Subpart U](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-93/subpart-U)** — Grand Canyon Special Flight Rules Area.
- **[AOPA](https://www.aopa.org/)** and **[AVweb](https://avweb.com/aviation-news/aviation-law/pilot-settlement-tribal-aircraft-seizure/)** — reporting on the October 2025 / March 2026 Smedsmo / Red Lake dispute.
- **[Snoqualmie Tribal Airspace Protection Act (PDF)](https://snoqualmietribe.us/wp-content/uploads/TribalCodes/Snoqualmie-Airspace-Protection-Act-6-4-June-27-2024.pdf)** — Snoqualmie overflight ordinance.
- **Haney, *Protecting Tribal Skies*, 40 Am. Indian L. Rev. 1 (2016)** — Hualapai and general tribal airspace legal analysis.
- **[Navajo Nation Parks & Recreation](https://navajonationparks.org/permits/)** — tribal park permitting and flight-plan rules.

Per-tribe markdown stubs live in [`content/tribes/`](content/tribes/) and can be expanded with more detail without changing any code.

## Importing the Content Pack into ForeFlight

Detailed instructions: [ForeFlight Content Packs Support](https://www.foreflight.com/support/content-packs/).

1. Download the ZIP file from the repository (link below).
2. On iOS/iPadOS: Open in Safari → Downloads → Share → ForeFlight.
3. ForeFlight will unpack and install the pack.
4. If you previously imported an earlier version, delete it first (More → Content Packs → swipe to delete) so ForeFlight picks up the new layer styling.
5. On the Maps view, enable both **Indian Reservations** (zones) and **Indian Reservations — Points** (tappable pins) from the layer selector. They are independent.

**Download:** [Indian_Reservations_Pack.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Indian_Reservations/Indian_Reservations_Pack.zip?raw=true)

Contributions welcome: add or refine a per-tribe markdown stub in [`content/tribes/`](content/tribes/), add a documented tribal overflight assertion to [`content/tribal_assertions.json`](content/tribal_assertions.json), or improve the styling.

## Rebuilding from source

If the underlying Census or FAA data has been updated and you want to refresh the pack, run the scripts in this order:

```bash
pip install requests shapely simplekml reportlab

python scripts/fetch_reservations.py      # pull GeoJSON from the ArcGIS republish
python scripts/enrich_reservations.py     # Census + OurAirports + Wikidata (~5 min first run; cached after)
python scripts/build_kml.py               # zone layer
python scripts/build_points_layer.py      # points layer
python scripts/build_waypoints.py         # centroid waypoint CSV
python scripts/build_pdfs.py              # all 8 PDFs
python scripts/package.py                 # writes manifest + zips the pack
```

Each script is idempotent. Intermediate data in `data/` is git-ignored; the built pack in `pack/` and the top-level `Indian_Reservations_Pack.zip` are committed so the zip can be downloaded directly without running the pipeline.

### Pre-zip validation

[`scripts/validate_pack.py`](scripts/validate_pack.py) runs automatically from `scripts/package.py` and the build **fails fast** if anything is wrong with the pack. Checks include:

- Zip layout (flat: `layers/`, `navdata/`, `manifest.json` at root; no parent folder).
- `manifest.json` — valid JSON, required fields, ForeFlight date format.
- **No non-ASCII bytes** in KML `<name>` or outside CDATA — we hit this with an em-dash in a layer name.
- Every KML parses as XML.
- No unsupported elements (`<BalloonStyle>`, `<Folder>`, `<NetworkLink>`, `<GroundOverlay>`).
- Every `<Polygon>` has `<tessellate>1</tessellate>` (without it, ForeFlight will not render the fill).
- No `<Point>` embedded inside a `<MultiGeometry>` alongside `<Polygon>` — that combination makes ForeFlight render only the Point and drop the polygon fill.
- Each Placemark uses inline `<Style>` (shared `<styleUrl>` references are warned, since ForeFlight's pack loader can drop them).
- Every `<color>` is 8-char AABBGGRR.
- Point placemark coordinates in range; descriptions wrapped in CDATA when they contain HTML.
- Waypoint CSV: 4 columns, alphanumeric codes ≤ 10 chars, unique, numeric lat/lon in range.
- PDFs start with `%PDF-` magic bytes.
- Pack total under 10 MB, individual KML under 5 MB.

Run it standalone at any time:

```bash
python scripts/validate_pack.py           # validates ./pack/
python scripts/validate_pack.py --zip Indian_Reservations_Pack.zip
```

### Layer ordering

The pack ships two overlapping map layers. To keep the tappable pins on the Points layer from being obscured by the translucent zone polygons:

- Every zone placemark carries `<drawOrder>1</drawOrder>`.
- Every point placemark carries `<drawOrder>10</drawOrder>` (higher renders on top).
- Zone fill alpha is kept low (0x55, ~33%) so pins are visible even if ForeFlight ignores `<drawOrder>`.

If the polygons still appear to cover the pins in ForeFlight, toggle the Points layer off and back on in the layer selector — that forces it to the top of the render stack.

## Disclaimer

This pack is for situational awareness only. It is **not** a substitute for current FAA publications, sectional charts, the Chart Supplement, or NOTAMs. It is **not** legal advice — consult your insurance carrier and an aviation attorney for specifics. Tribes and reservations evolve; the underlying data and tribal assertions may change between pack releases. Always check current sources before flight.

## Addendum: Syncing Content Packs via Cloud Storage (e.g., OneDrive)

For users who want to easily manage and sync content packs across multiple devices, you can integrate a cloud storage service like Microsoft OneDrive with ForeFlight. This setup allows you to host the content pack .zip file in a shared folder, where it can automatically sync across your devices via OneDrive. Once integrated, new or updated .zip files placed in the designated folder will appear in ForeFlight's More > Downloads section for import. With ForeFlight's Automatic Content Packs Download setting (enabled by default in recent versions), packs can download automatically, and updates (replacing the .zip with a newer version) can be handled by re-importing the revised file.

**Note:** This feature requires a ForeFlight Pro or higher subscription plan for Cloud Documents integration. Content packs do not auto-update in place; you must replace the .zip file with an updated version (ideally including a version number in the manifest.json for tracking) and re-import it. However, the cloud sync ensures the latest .zip is available on all linked devices.

### Steps to Integrate OneDrive with ForeFlight

1. **Sign in to ForeFlight Web:** Go to [plan.foreflight.com](https://plan.foreflight.com) and log in with your ForeFlight account.
2. **Navigate to Documents:** In the sidebar, click on **Documents**.
3. **Add a Cloud Drive:** In the **My Drives** section, click **Add a Cloud Drive**.
4. **Select OneDrive:** From the **Drive Provider** dropdown menu, choose **OneDrive**.
5. **Configure the Drive:** Enter a **Drive Name** (e.g., "My OneDrive") and specify an existing folder in your OneDrive root level (e.g., "ForeFlightDocs").
6. **Connect and Authorize:** Click **Add Drive**, sign in with your Microsoft credentials, and grant ForeFlight access.

### Setting Up the "contentpack" Folder for Automatic Sync

1. **Create the Folder:** In your linked OneDrive folder, create a subfolder named exactly **contentpack** (case-sensitive).
2. **Place the .zip File:** Download `Indian_Reservations_Pack.zip` from this repository and upload it to the `contentpack` folder in OneDrive.
3. **Access in ForeFlight:** Open **More > Downloads** in ForeFlight. The pack should appear automatically under available downloads. With Automatic Content Packs Download enabled, it will download without manual selection.
4. **Handling Updates:** Replace the old .zip with the new version in OneDrive; ForeFlight will offer the update in **More > Downloads**.

See [ForeFlight's OneDrive Integration Support](https://support.foreflight.com/hc/en-us/articles/14443946235671-How-can-OneDrive-be-integrated-with-ForeFlight) and [Content Packs Support](https://foreflight.com/support/content-packs/) for more detail. Dropbox works similarly with the folder at `~/Dropbox/Apps/ForeFlight/contentpack/`.
