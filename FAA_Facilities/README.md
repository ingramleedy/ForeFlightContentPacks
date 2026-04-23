# FAA Districts and Facilities Content Pack for ForeFlight

**Download:** [FAA_Facilities_Pack.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/FAA_Facilities/FAA_Facilities_Pack.zip?raw=true) — ~101 MB (delivered via Git LFS).

This repository provides a **ForeFlight content pack** containing custom map overlays for FAA districts, facilities, ARTCC (Air Route Traffic Control Center) sectors, and TRACONs (Terminal Radar Approach Controls). These overlays assist pilots and aviation enthusiasts in visualizing airspace boundaries, control sectors, and key facilities for improved situational awareness and flight planning.

The content pack displays ARTCC sectors and TRACON boundaries as a custom map layer in ForeFlight, integrating seamlessly with airspace, terrain, sectional charts, and other layers for enhanced route planning and navigation.

![FAA Sector US](/img/FF-FAA-Sector-US.png)
![FAA Sector FL](/img/FF-FAA-Sector-Florida.png)

## Important Disclaimer

**This content pack is an unofficial, community-created compilation.** The boundaries and data for ARTCC sectors, TRACON areas, and other facilities have been **cobbled together from various public sources**, including FAA publications, digital charts, third-party interpretations, and community contributions.  

**These sources are unverified and may contain inaccuracies or outdated information.**  

**Official FAA maps exist only for high-level ARTCC boundaries.** There are **no official FAA sector-level detail maps** publicly available for ARTCC low/high sectors or detailed TRACON boundaries.  

This pack is provided **for educational, planning, and situational awareness purposes only**. It is **not for navigation** and should never be used as a substitute for official FAA charts, publications, or NOTAMs. Always cross-reference with current official sources (e.g., FAA Aeronautical Information Manual, sectional charts, and the Air Traffic Control Facilities Directory) and verify with ATC when needed.

Use at your own risk.


## Content Overview

This content pack includes overlays for FAA districts, major facilities, ARTCC sectors across the United States, and associated TRACON areas. It draws from official FAA data sources to provide accurate, up-to-date boundaries and labels.

The pack focuses on high-level airspace structures, supplementing ForeFlight's native FAA data with detailed sector visualizations for better understanding of enroute and terminal airspace.

### Enhanced Usage with ForeFlight Airspace Tools

For optimal use in flight planning, combine this content pack with ForeFlight's **Airspace** and **Profile View** features. Airspace layers highlight class boundaries, while Profile View provides a vertical cross-section of sectors along your route.

- **Activation:** Enable the custom layer in Map Settings > Layers > User Content. Adjust zoom levels to view sector details.  
- **In-Flight Mode:** Use with ADS-B or GPS for real-time position relative to sectors.  
- **Subscription Note:** Custom content packs work with any ForeFlight subscription, but advanced features like Profile View require Pro Plus or higher.

This integration helps in identifying handoff points, frequency changes, and airspace transitions during complex flights.

## Inspiration and Credits

This content pack is inspired by and draws from official FAA resources:

- **Federal Aviation Administration (FAA)** – Primary source for airspace data, ARTCC boundaries, and TRACON definitions.  
- **FAA Aeronautical Information Manual (AIM)** – Guidance on airspace structure and usage.  
- **FAA Air Traffic Control Facilities Directory** – Details on centers and approach controls.  
- **National Airspace System (NAS) Resources** – Including digital charts and sector maps available via FAA websites.

## Included Content

The pack includes overlays for the following key elements, with boundaries, labels, and identifiers derived from FAA sources:

- **ARTCC Sectors:** Boundaries and identifiers for all 22 ARTCCs (e.g., ZDV - Denver, ZLA - Los Angeles), including high/low altitude sectors where applicable.  
- **TRACONs:** Terminal areas for major airports and regions (e.g., SoCal TRACON, Potomac TRACON), with approach/departure boundaries.  
- **FAA Districts and Facilities:** Overlays for Flight Standards District Offices (FSDOs), regional offices, and other key facilities.

*Note: Always verify with current FAA publications and NOTAMs for operational use. This pack is for planning and educational purposes.*

## Importing the Content Pack into ForeFlight

Detailed instructions: [ForeFlight Content Packs Support](https://www.foreflight.com/support/content-packs/).

1. Download the ZIP file from the repository (link below).  
2. On iOS/iPadOS: Open in Safari → Downloads → Share → ForeFlight.  
3. ForeFlight will unpack and install the pack.  
4. Restart ForeFlight.  
5. On Maps view, select layer: Aero & Category → "FAA Facilities" on left and "ARTCC/TRACON Overlays" on right.

**Download:** [FAADistrictsFacilitiesFFContentPack.zip](https://github.com/ingramleedy/FAAFacilitiesFFContentPack/blob/main/FAAFacilitiesFFContentPack.zip?raw=true)  
Note: Content packs require manual re-download for updates.


## Addendum: Syncing Content Packs via Cloud Storage (e.g., OneDrive)

For users who want to easily manage and sync the FAA Districts & Facilities content pack across multiple devices, you can integrate a cloud storage service like Microsoft OneDrive with ForeFlight. This setup allows you to host the content pack .zip file in a shared folder, where it can automatically sync across your devices via OneDrive. Once integrated, new or updated .zip files placed in the designated folder will appear in ForeFlight's More > Downloads section for import. With ForeFlight's Automatic Content Packs Download setting (enabled by default in recent versions), packs can download automatically, and updates (e.g., replacing the .zip with a newer version) can be handled by re-importing the revised file.

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

2. **Place the .zip File:** Download the latest ` FAADistrictsFacilitiesFFContentPack.zip` from this repository and upload it to the `contentpack` folder in OneDrive. The file will automatically sync across all your devices connected to OneDrive.

3. **Access in ForeFlight:**
   - Open ForeFlight on your iOS/iPadOS device.
   - Go to **More > Downloads**.
   - The content pack should appear automatically under available downloads (thanks to Cloud Documents integration).
   - If Automatic Content Packs Download is enabled (check in ForeFlight Web: Account > Integrations > Cloud Documents), it will download without manual selection.
   - Import the pack as described in the "Importing the Content Pack into ForeFlight" section above.

4. **Handling Updates:**
   - When a new version of the content pack is released (e.g., updated waypoints or notes), download the new .zip and replace the old one in your OneDrive `/contentpack/` folder.
   - OneDrive will sync the updated file across devices.
   - In ForeFlight, the new version will appear in More > Downloads; import it to apply the update (older versions may show expiration warnings if dates are set in the manifest).

This setup ensures your content pack is always accessible and up-to-date across devices without manual transfers. For more details, refer to ForeFlight's [OneDrive Integration Support](https://support.foreflight.com/hc/en-us/articles/14443946235671-How-can-OneDrive-be-integrated-with-ForeFlight) and [Content Packs Support](https://foreflight.com/support/content-packs/). If using Dropbox instead, the process is similar, with the folder at `~/Dropbox/Apps/ForeFlight/contentpack/`.






