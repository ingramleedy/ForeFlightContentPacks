# Diners, Drive-Ins and Dives Content Pack for ForeFlight

**Download:** [Diners_Drive_Ins_Dives_Pack.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Diners_Drive_Ins_Dives/Diners_Drive_Ins_Dives_Pack.zip?raw=true)

A ForeFlight content pack containing every restaurant featured on Guy Fieri's **Diners, Drive-Ins and Dives** (Food Network), scraped from the show's A–Z listing and geocoded for use as a toggleable map layer in ForeFlight. Tap any pin to see the restaurant name, full address, phone number, and Food Network blurb.

**Current version:** `2026.04.23`
**Restaurants:** 939 (all US locations from the [Food Network DDD A–Z listing](https://www.foodnetwork.com/restaurants/shows/diners-drive-ins-and-dives/a-z))
**Pack size:** ~90 KB zipped

## Content Overview

The pack ships a single KML layer: **Diners, Drive-Ins and Dives** — 939 red pins, one per restaurant, with a rich-description popup on tap.

This is the $100-hamburger destination list for pilots who plan their cross-countries around food. It pairs naturally with [Airport_Restaurants](../Airport_Restaurants/) — the Airport Restaurants pack covers restaurants *on or near airports*, while DDD covers restaurants *anywhere in the US that Guy Fieri visited*, which are often well outside walking distance of a runway.

### Source

Restaurants are scraped from the [Food Network's DDD A–Z listing](https://www.foodnetwork.com/restaurants/shows/diners-drive-ins-and-dives/a-z) with a Python pipeline, then geocoded via Nominatim (OpenStreetMap). The upstream scraping tool lives in a separate repo: [ForeFlightDinersDriveInsDives](https://github.com/ingramleedy/ForeFlightDinersDriveInsDives) — it also produces a human-readable Markdown table and an intermediate `restaurants.json` cache for quick re-exports.

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
