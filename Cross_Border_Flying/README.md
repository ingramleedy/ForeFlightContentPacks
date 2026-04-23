# Cross Border Flying ForeFlight Content Pack

**Download:** [Cross_Border_Flying_Pack.zip](https://github.com/ingramleedy/ForeFlightContentPacks/blob/main/Cross_Border_Flying/Cross_Border_Flying_Pack.zip?raw=true) — US CBP Southern Border pack. A separate Bahamas pack is in [`contentpacks/Bahamas.zip`](contentpacks/Bahamas.zip).

This repository is for pilot's travel across the US borders and deal with US Customs and Border Patrol (US CBP), Mexico, Canada, and Bahamas

Many pilot's use ForeFlight as their electronic flight bag (EFB) [ForeFlight](https://www.foreflight.com/) app,
which contains a feature to download and import custom *content packs* that contain  bundles of related 
content that can be accessed in the app, making it easier to adapt ForeFlight to a variety of specialized uses.
See [ForeFlight Content Pack Overview](https://www.foreflight.com/products/foreflight-mobile/user-content/content-packs) and [ForeFlight Content Pack Support](https://foreflight.com/support/content-packs/) 
for more details.


### US Customs Souther Border ###

<p align="center">
  <img width="600" src="docs/imgs/florida-poe-overview (Medium).jpg" />   
</p>

<p align="center">
  <img width="600" src="docs/imgs/waypoint-details (Medium).jpg" />   
</p>

<p align="center">
  <img width="600" src="docs/imgs/example-datasheet (Medium).jpg" />   
</p>

### Bahamas ### 
<p align="center">
  <img width="600" src="docs/imgs/bahamas%20(Medium).jpg" />   
</p>


## Importing the Content Pack into ForeFlight

Detailed instructions: [ForeFlight Content Packs Support](https://www.foreflight.com/support/content-packs/).

1. Download the ZIP using the link at the top of this README.
2. On iOS/iPadOS: open in Safari → Downloads → Share → **ForeFlight**.
3. ForeFlight will unpack and install the pack.
4. Restart ForeFlight if layers don't appear immediately.
5. In ForeFlight: **More → Content Packs**, toggle the pack on. On the **Maps** view, enable the pack's layers from the layer selector.

*Note: Content packs require manual re-download for updates, unless using the Cloud Storage sync described below.*

## Importing Content Packs into ForeFlight for Use 

Detailed instructions about how to import Content Packs into
Foreflight are available at their [support
page](https://www.foreflight.com/support/content-packs/) 

1. In general, **select** each desired file below to download
2. A dialog withh popup, **Do you want to download file.zip?**, select **Download**
3. At the top of the Safari app shows a small **download icon** *(next to the address bar)*, **select** the **download icon**
4. **Select** the file you just downloaded to open the **files** app.
5. In the files app, **Select** and **hold** the respective file and select **Share**
6. **Select** ForeFlight app
7. ForeFlight will show a dialog **Unpacking content**, and then show another dialog **Conent Pack Installed** when completed.
8. Click **OK**
9. **Close** ForeFlight app and **Re-Launch**.  This will refresh the content pack with its associated content.
10. Choose the **Maps** page in ForeFlight and choose **Aero & Category** from maps layers and **select** the associated content pack name to activate the layer.

# US Custom Border (Southern Points of Entry)

This respository maintains a directory of US Custom Border Patrol Ports of Entry for the Southern area of the US viewable as waypoints and also provides the repective datasheets.  This allows you to research and plan your destination around US CBP southen entries.


[US CBP Southern Border](https://raw.githubusercontent.com/ingramleedy/CrossBorderFlyingFFContentPack/main/contentpacks/US-CBP-Southern-Border.zip) download

# Bahamas Customs Ports of Entry 

This respository maintains a directory of Bahamas Custom Ports of Entry viewable as waypoints.  

[Bahamas Customs Ports of Entry](https://raw.githubusercontent.com/ingramleedy/CrossBorderFlyingFFContentPack/main/contentpacks/Bahamas.zip) download

## Version History and Future Ideas

* Version 2023.11.10
  * Added Bahamas Custom Ports of Entry
* Version 2023.11.07 
  * Initial version of Southern Border Port of Entry Airports for US Customs and Border Patrol (US CBP)
     
 ## ForeFlight Feature Request to Automatically Update New Versions

Keeping this *content packs* updated once imported into ForeFlight requires re-downloading
newer content packs and re-importing into ForeFlight.  

#### Feature Request ####

- The ability for content packs to be downloaded and updated from a URL.
  - This would be the simplest method, a link to selected and added to downloads list and ForeFlight would periodically check for new updates. This would function the same way Downloads from ForeFlight work. Client could always delete content pack they no longer want to recieve.  

- Allow concurrent multiple cloud drive providers for Documents
  - The cloud storage feature is only available for *Performance Plus* subscribers of ForeFlight which by adding a folder named *contentpacks* to the root folder, content packs in
the folder are automatically available to download and update. However only one cloud provider is available concurrently. Pilots may need access to multiple resources, companies, flight schools, 
flight clubs, 3rd party content, etc. I envision a subscription service that provided valuable content on various contant that would currate and  keep up-to-date.

Send your support for these request to ForeFlight Support [support@foreflight.com](mailto:support@foreflight.com).

# Legal Disclaimer

All files are provided for educational purposes only. They are not to
be used as a navigation tool. No claim is made regarding the accuracy
of these charts and their contents.

# Other related projects
[Airport Restaurants](https://github.com/ingramleedy/Airport_Restaurants) - ForeFlight content packs for pilot's who love a mission to fly and eat somewhere that is on location of an airport or just nearby walking distance.

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
