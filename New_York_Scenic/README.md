# New-York-Scenic-Content-Pack-for-ForeFlight

**Download:** [New_York_Scenic_Pack.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/New_York_Scenic/New_York_Scenic_Pack.zip?raw=true)

**Hudson River & East River SFRA + Statue of Liberty**  
A ForeFlight Content Pack

Clean, accurate, color-coded reporting points and general navigation waypoints for safely and correctly flying the New York Class B Hudson River and East River Special Flight Rules Area (SFRA), including the exact Statue of Liberty orbit and SFRA exclusion boundaries.

Built for fixed-wing pilots who want to fly the Hudson corridor legally and with complete situational awareness.

### What this pack includes
- All official northbound and southbound Hudson River reporting points  
  (Alpine Tower → Verrazzano-Narrows Bridge)  
- East River reporting points (where fixed-wing remain allowed)  
- Statue of Liberty clockwise orbit waypoints (Liberty 1–9) at the correct 1,100 ft MSL radius  
- General navigation waypoints for common entry/exit routes and transitions  
- Skyline Transition entry/exit waypoints  
- SFRA exclusion boundary as a visible magenta polygon (matches the FAA chart exactly)

All points use the exact names and coordinates published on the current New York TAC and FAA SFRA documentation.

### Download the latest release
[NY Hudson River and East River Exclusion SFRA.zip](https://github.com/ingramleedy/New-York-Scenic-Content-Pack-for-ForeFlight/blob/main/NY%20Hudson%20River%20and%20East%20River%20Exclusion%20SFRA.zip?raw=true)

### Installation instructions
1. Download the file `NY Hudson River and East River Exclusion SFRA.zip` on your iPad or iPhone  
2. Tap the file – ForeFlight will open automatically and recognize the content pack  
3. Tap "Import" (you can preview everything with "View" first)  
4. Turn the layer on: Maps → Layers → Hudson River SFRA (bottom of the right column)

### Updating
When a new version is released (NOTAM changes, updated coordinates, etc.), simply download and import the new ZIP.  
ForeFlight will automatically replace the older version.

### Contributing
Found an error or have an improvement?  
Open an issue or submit a pull request – contributions are always welcome!

### Credits & Inspiration
Inspired by the pioneering work of Forum user “Mark” who, around 2019, created the original “New York Scenic” content pack and generously shared it on Diamond Aviators Net — the first community pack many of us ever installed.  
Original thread: https://www.diamondaviators.net/forum/viewtopic.php?t=6756  
Thank you, Mark.


Fly the corridor right the first time — see you over the Hudson!

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
