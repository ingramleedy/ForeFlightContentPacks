# Indian Reservations — ForeFlight Content Pack

A ForeFlight content pack that shows U.S. federal American Indian reservations as a map layer, with searchable centroid waypoints and two reference PDFs on overflight considerations and special airspace.

## What's in the pack

- **`layers/Indian_Reservations.kml`** — 312 federal reservation polygons, simplified for mobile rendering, tan fill with dark brown outlines. Tap any polygon to see its name, land area, population, and GEOID.
- **`navdata/Reservation_Centroids.csv`** — 312 searchable waypoints at each reservation's interior point. Waypoint codes are up to 10 characters (e.g. `TAOSPUEB`, `NAVAJO`, `HUALAPAI`).
- **`navdata/Overflight_Considerations.pdf`** — one-page summary of AC 91-36D, 14 CFR 91.119, NPATMA, and FAA Order 1210.20 with honest notes on what restrictions are and aren't enforceable.
- **`navdata/Special_Airspace_Tribal.pdf`** — cases where specific, citable airspace rules or sectional-noted overflight requests apply (Grand Canyon SFRA, Taos Pueblo, NPATMA ATMPs, Red Lake).
- **Rich waypoints** — the waypoints `HUALAPAI`, `HAVASUPAI`, `NAVAJO`, `TAOSPUEB`, and `REDLAKE` have a linked copy of `Special_Airspace_Tribal.pdf` that opens when you tap the waypoint in ForeFlight.

## Install in ForeFlight

1. AirDrop or email `Indian_Reservations_Pack.zip` to your iPad.
2. Open the file — iOS will offer "Copy to ForeFlight".
3. In ForeFlight: **More → Content Packs** and toggle the pack on.
4. On the map, enable the **Indian Reservations** layer from the layer selector.

## Rebuild from source

If the Census TIGER data has been updated and you want to refresh the pack:

```bash
python scripts/fetch_reservations.py
python scripts/build_kml.py
python scripts/build_waypoints.py
python scripts/build_pdfs.py
python scripts/package.py
```

Each script is idempotent; running them in order reproduces the full pack. Output lands in `pack/` and the final zip is written alongside it.

### Dependencies

Python 3.11+ and:

```bash
pip install requests shapely simplekml reportlab
```

### Data source

The fetch script pulls from the ArcGIS FeatureServer republish of the Census Bureau's TIGER/Line AIANNH (American Indian / Alaska Native / Native Hawaiian Areas) shapefile, filtered to federal reservations:

https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/Federal_American_Indian_Reservations_v1/FeatureServer

The authoritative source is the Census Bureau at https://www.census.gov/geographies/mapping-files.html — if the ArcGIS republish ever goes dark, point `fetch_reservations.py` at the Census shapefile instead (or convert locally with `ogr2ogr -f GeoJSON out.geojson tl_YYYY_us_aiannh.shp`).

## Scope notes

- **Federal reservations only.** Off-Reservation Trust Lands, Oklahoma Tribal Statistical Areas, State reservations, and Alaska Native Village Statistical Areas are not included. The source ArcGIS layer already filters to federal reservations.
- **Restriction claims are conservative.** The two PDFs cite only regulations, advisory circulars, and sectional-noted advisories. They do not manufacture restrictions where no FAA-citable source exists. Tribes that have issued their own overflight resolutions without FAA codification (e.g., Red Lake) are called out as situational awareness, not as airspace rules.
- **Not a substitute for current FAA products.** Always check current sectionals, the Chart Supplement, and NOTAMs before flight.

## Project layout

```
Indian_Reservations/
├── content/       ← Markdown sources for the two PDFs
├── data/          ← cached GeoJSON download (regenerate with fetch script)
├── pack/          ← the actual ForeFlight content pack (zipped for import)
└── scripts/       ← build pipeline
```
