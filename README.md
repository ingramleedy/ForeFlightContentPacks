# ForeFlight Content Packs

A collection of ForeFlight content packs for general aviation pilots. Every pack is self-contained in its own subfolder with a pre-built distribution zip ready to download and import into ForeFlight. Most packs include the source data fetch and build scripts so they can be rebuilt against fresh source data.

## Packs in this repo

| Pack | Description | Size | Download |
|---|---|---|---|
| [Airport_Restaurants](Airport_Restaurants/) | Pilot-friendly dining at or near airports; includes per-state / per-province subsets in [`contentpacks/`](Airport_Restaurants/contentpacks/). | ~15 KB | [.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Airport_Restaurants/Airport_Restaurants_Pack.zip?raw=true) |
| [Colorado_Mountain_Passes](Colorado_Mountain_Passes/) | 36 Colorado mountain passes as waypoints + custom layer for safer Rocky Mountain crossings. | ~109 KB | [.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Colorado_Mountain_Passes/Colorado_Mountain_Passes_Pack.zip?raw=true) |
| [Cross_Border_Flying](Cross_Border_Flying/) | US Customs southern-border POEs and Bahamas airports with procedures for US↔Canada/Mexico/Bahamas flights. | ~11 MB | [.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Cross_Border_Flying/Cross_Border_Flying_Pack.zip?raw=true) |
| [Diamond_Service_Centers](Diamond_Service_Centers/) | Diamond Aircraft authorized service, sales, and training centers worldwide (~192 locations). | ~25 KB | [.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Diamond_Service_Centers/Diamond_Service_Centers_Pack.zip?raw=true) |
| [Diners_Drive_Ins_Dives](Diners_Drive_Ins_Dives/) | 939 restaurants featured on Guy Fieri's *Diners, Drive-Ins and Dives* (Food Network) as tappable pins with name, address, phone, and blurb. | ~90 KB | [.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Diners_Drive_Ins_Dives/Diners_Drive_Ins_Dives_Pack.zip?raw=true) |
| [FAA_Facilities](FAA_Facilities/) | ARTCC sectors and TRACON boundaries as a map layer for airspace situational awareness. | ~101 MB | [.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/FAA_Facilities/FAA_Facilities_Pack.zip?raw=true) |
| [Indian_Reservations](Indian_Reservations/) | 312 US Indian reservations as tappable zones + points, with overflight-considerations + special-airspace PDFs. | ~315 KB | [.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Indian_Reservations/Indian_Reservations_Pack.zip?raw=true) |
| [New_York_Scenic](New_York_Scenic/) | Hudson River / East River SFRA reporting points + Statue of Liberty orbit waypoints. | ~1.9 MB | [.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/New_York_Scenic/New_York_Scenic_Pack.zip?raw=true) |
| [Timezones](Timezones/) | World time zone boundaries with UTC offsets as a toggleable KML layer. | ~242 KB | [.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Timezones/Timezones_Pack.zip?raw=true) |

## Related projects

Other pilot tools I've built (or helped build) that pair well with ForeFlight. Not content packs — standalone apps and utilities, listed here so this README stays the master of what is featured on the [listing site](https://ingramleedy.github.io/foreflight-content-packs/).

| Project | What it does | Link |
|---|---|---|
| **FlightStreamX** (iOS) | Wirelessly transmits the active ForeFlight (or Garmin Pilot) flight plan to X-Plane over local Wi-Fi — auto-discovers X-Plane on the network, converts the plan to FMS 1100 format, and loads it into the sim, no manual file transfer. By Flying Dragons. $8.99. | [App Store](https://apps.apple.com/us/app/flightstreamx/id6759071019) |
| **SkySkew** (iOS) | Turns Skew-T diagrams into plain-English route insights for turbulence, icing, and winds aloft. AI-assisted interpretation, route-specific atmospheric data, iPad-optimized. By Flying Dragons. 14-day trial, $2.99/mo or $29.99/yr. | [App Store](https://apps.apple.com/us/app/skyskew/id6741827720) |
| **AIRAC Cycle Calendar Generator** | Free web tool + API that generates an iCalendar (`.ics`) of every AIRAC effective date so your Garmin / ForeFlight / Navigraph / Jeppesen database updates never sneak up on you. Optional 7- or 14-day reminder events. | [airac.flyingdragons.world](https://airac.flyingdragons.world/api/airac) · [GitHub](https://github.com/ingramleedy/AIRAC) · [Diamond Aviators forum](https://www.diamondaviators.net/forum/viewtopic.php?t=10041) |

## Other packs referenced on the listing site

These packs are featured on the [public listing site](https://ingramleedy.github.io/foreflight-content-packs/) but are maintained by other authors and are not hosted in this repo. Included here so this README stays the master of what is on the site.

| Pack | Description | Source |
|---|---|---|
| FAA Minimum Vectoring Altitude (MVA) / Minimum IFR Altitude (MIA) Charts as KML | Content pack covering every MVA/MIA chart from the same ATC TRACON facility; pack names encode the map type and the three-character facility identifier. | [github.com/dark/faa-mva-kml](https://github.com/dark/faa-mva-kml) |
| USA Package — landmarks, national parks, monuments, more | Landmarks plus all US national parks, national monuments, national shores, and other scenic destinations packaged for ForeFlight. | [flyingadventuresandmore.blog/foreflight](https://flyingadventuresandmore.blog/foreflight/) |

## Importing the Content Pack into ForeFlight

Detailed instructions: [ForeFlight Content Packs Support](https://www.foreflight.com/support/content-packs/).

1. Click the **.zip** link in the Download column above — on iOS Safari, this offers "Open in… → ForeFlight" directly. On desktop, save the file and AirDrop or email it to your iPad.
2. iOS will offer "Copy to ForeFlight" — accept.
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

## Layout

Each pack is a self-contained subfolder. The target layout for new packs (Indian_Reservations is the current reference) is:

```
<Pack_Name>/
├── README.md
├── scripts/        Python build pipeline
├── content/        Markdown sources for PDFs
├── data/           cached source downloads (git-ignored; regenerate with fetch script)
├── pack/           the actual ForeFlight content pack (zipped for import)
└── <Pack_Name>_Pack.zip
```

Older migrated packs don't all conform yet — see [Indian_Reservations/](Indian_Reservations/) for the reference. Bringing the rest onto this layout is a tracked follow-up.

## Contributing a new pack

1. Create a new subfolder at the repo root.
2. Mirror the layout above: `scripts/`, `content/`, `data/`, `pack/layers/`, `pack/navdata/`.
3. Follow the KML conventions that actually render in ForeFlight — inline `<Style>` per `<Placemark>`, `<tessellate>1</tessellate>` on every `<Polygon>`, no `<Folder>` or `<BalloonStyle>`, `<PolyStyle><fill>1</fill>` with an AABBGGRR color. See `Indian_Reservations/scripts/build_kml.py` for a working reference.
4. Keep the zipped pack under ~10 MB for iPad responsiveness. Simplify geometry with Shapely if needed.
5. Cite your sources. Advisory-circular and CFR references belong in the PDFs; speculation doesn't.

## Disclaimer

These packs are for situational awareness only. They are not a substitute for current FAA publications, sectional charts, the Chart Supplement, or NOTAMs. Always check current sources before flight.
