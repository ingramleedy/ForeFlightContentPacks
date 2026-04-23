# ForeFlight Content Pack Format

Reference for the on-disk layout of a ForeFlight content pack and — more importantly — **what each folder actually does inside ForeFlight**. The official docs ([foreflight.com/support/content-packs](https://foreflight.com/support/content-packs/)) describe the folders; this document adds the behavioral semantics that are easy to get wrong.

> This is a developer-facing reference. If you're contributing a new pack, read this end-to-end before copying another pack's structure, because several packs in this repo predate these conventions and don't all follow them.

---

## 1. Zip layout (the high-level contract)

ForeFlight imports a **zip of the pack folder's contents** — `layers/`, `navdata/`, `byop/`, and `manifest.json` must sit at the **root** of the zip, not inside a parent folder.

```
<pack-name>.zip
├── manifest.json        (optional but recommended)
├── layers/              (optional) display-only map overlays
├── navdata/             (optional) searchable waypoints + optional PDFs
└── byop/                (optional) procedure plate PDFs
```

A pack can include any subset of the three subfolders. None is mandatory. But the one you choose governs what the user *sees* and *interacts with* in ForeFlight — and the three folders behave very differently. That's the core insight most new pack authors miss.

---

## 2. The three subfolders — what they actually do

### 2.1 `layers/` — display-only map overlays

**What goes here:** KML, KMZ, GeoJSON, MBTiles, FBTiles, or geospatial PDFs that render as toggleable map layers.

**How ForeFlight treats the contents:**
- Each file becomes one **separately toggleable map layer** in the Maps view's layer selector.
- Placemarks inside render as icons/shapes/lines/polygons on the map.
- Tapping a placemark shows a popup with the placemark's `<name>` and `<description>` — the description can contain **inline HTML** (headings, bold, links, etc.) and is rendered directly in the popup.

**What this folder does NOT do:**
- **Cannot attach PDFs to placemarks.** There is no mechanism for a `/layers/` KML placemark to open a PDF document when tapped. The rich-waypoint PDF feature is a `navdata/`-only feature (see §3).
- **Cannot link to other files in the pack.** `<a href="file.pdf">` inside a description does *not* resolve to a PDF elsewhere in the pack — there's no addressable URL scheme for pack-local files. External `https://` links will open Safari, but local file references don't work.
- Placemarks here are **not searchable** in the waypoint search bar and don't appear in the waypoint / FPL autocomplete.

**Use this folder when:** you want a visual overlay the pilot can toggle on/off, and every piece of information a pilot might want is either visible on the map (icon, color, label) or embedded as HTML in the placemark description.

**Example in this repo:** [Diners_Drive_Ins_Dives/pack/layers/](Diners_Drive_Ins_Dives/pack/layers/) — one KML, rich HTML descriptions, no `navdata/`.

---

### 2.2 `navdata/` — searchable waypoints (with optional PDF attachment)

**What goes here:** exactly one of (a) a waypoint **CSV** or (b) a waypoint **KML** — plus optional **PDF documents** that ForeFlight will attach to individual waypoints by filename convention.

**CSV format** (4 columns, no header row):
```
WAYPOINT_CODE,Description,Latitude,Longitude
ALINEA,Alinea,41.9133,-87.6489
```
- `WAYPOINT_CODE` must be alphanumeric, typically ≤ 10 chars, unique within the pack.
- Used as the waypoint identifier in ForeFlight's search / FPL entry.

**KML format:** a standard `<Document>` with `<Placemark>` / `<Point>` entries. The placemark `<name>` becomes the waypoint code. Must conform to the KML subset in §5.

**How ForeFlight treats the contents:**
- Each waypoint in the CSV/KML becomes a **searchable user waypoint**. The pilot can type the code (`ALINEA`) in the waypoint search and the pin resolves.
- Waypoints show on the map when the pack's `navdata/` layer is enabled — they typically appear as **one additional layer entry** in the layer selector (labeled with the pack/file name).
- Tapping a waypoint opens the standard waypoint details view, which includes any **attached PDFs** (see next).

**Rich-waypoint PDFs** (the whole reason to use this folder instead of `layers/`):
- PDF filename convention: `<WAYPOINT_CODE><DocumentName>.pdf`
  - e.g. `ALINEAMichelin_Guide.pdf` attaches to waypoint `ALINEA`
  - `ALINEAReservation_Info.pdf` adds a second document to the same waypoint
- PDFs must live in `navdata/` alongside the CSV/KML.
- ForeFlight runs a proprietary indexing pass at import time, matches filenames against waypoint codes, and wires them up. There is no XML, metadata, or manifest entry for this — it's purely filename-based.

**Important constraints:**
- **Pick CSV *or* KML, not both.** Having both creates duplicate waypoint entries and an extra layer in ForeFlight's layer list. They serve the same role.
- **Waypoint counts should stay monotonic across pack updates** with the same abbreviation. If an update publishes fewer waypoints than a previously installed version, ForeFlight can refuse the update. To deliberately reduce the waypoint set, bump the `abbreviation` field in `manifest.json` (treating it as a new pack identity).

**Use this folder when:** you need pins that are (a) searchable by code, (b) attachable to per-waypoint PDF documents, or (c) addable to a flight plan like a normal fix.

**Example in this repo:** [Airport_Restaurants/Airport Restaurants/navdata/](Airport_Restaurants/Airport Restaurants/navdata/) — one KML, no PDFs, no `layers/` folder.

---

### 2.3 `byop/` — "Bring Your Own Plates" procedure PDFs

**What goes here:** individually geo-referenced or ident-linked PDF plates that ForeFlight surfaces in the procedure / plate picker for a specific airport or procedure.

**Behavior:** PDFs in `byop/` appear in the **Plates** tab for whichever airport/procedure they're named for. Filenames follow ForeFlight's BYOP convention (e.g. `KPDK_ILS_Y_20L.pdf`). This is a narrower use case than `layers/` or `navdata/` and most packs in this repo don't use it.

**Official reference:** [ForeFlight BYOP support](https://foreflight.com/support/byop/).

---

## 3. The two "rich document" patterns — choosing between them

Almost every content pack boils down to one question: **do you want per-pin documents, or just pretty popups?**

| You want... | Put content in... | Mechanism |
|---|---|---|
| Toggleable overlay with icon + label + HTML popup (cuisine/phone/address/review excerpt shown when tapped) | `layers/` KML, with HTML in `<description><![CDATA[...]]></description>` | Inline — HTML is embedded in the KML file, rendered directly in the popup |
| A searchable waypoint code the pilot can type into the route builder | `navdata/` CSV or KML | Waypoint is indexed into ForeFlight's nav database |
| A full multi-page PDF document tied to a specific pin (inspector review, restricted-airspace summary, procedure narrative) | `navdata/` CSV/KML + `navdata/<CODE><DocName>.pdf` | ForeFlight indexes the PDF against the waypoint code at import time |

**Why HTML works in layer descriptions but PDFs don't:** the HTML is *embedded text inside the KML file* — ForeFlight's KML renderer parses it and paints it into the popup directly, no external file lookup needed. A PDF is a separate binary file; there's no way to embed a PDF inside a KML. The only way a pack placemark can open a PDF is through ForeFlight's proprietary `navdata/` filename-indexing pass, and that pass only runs on waypoints, not layer placemarks.

**Practical implication:** if all your per-pin info fits in HTML (say, under a few KB per placemark), `layers/` gives you a cleaner UX (one toggle in the layer selector, rich popup on tap, no extra waypoints polluting the search bar). Reach for `navdata/` + PDFs only when you need a full-page document per pin, or when the pin really is a waypoint the pilot will file in a flight plan.

---

## 4. `manifest.json`

Optional, but recommended — ForeFlight uses it to identify the pack for updates and expiration.

```json
{
  "name": "Michelin Restaurants",
  "abbreviation": "MR.V1",
  "version": 202604231530.0,
  "effectiveDate": "20260423T15:30:00Z",
  "expirationDate": "20271231T23:59:59Z",
  "organizationName": "Ingram Leedy"
}
```

- `name` — user-visible name in the Content Packs list.
- `abbreviation` — short identifier; **ForeFlight treats two packs with different abbreviations as distinct** (installing one doesn't replace the other). Bump the abbreviation suffix (`.V1` → `.V2`) when you make a structural change that shouldn't be silently merged with the prior install — especially a waypoint-count reduction.
- `version` — float (e.g. `202604231530.0`). Each build should monotonically increase; most packs in this repo encode UTC `YYYYMMDD.HHMM`.
- `effectiveDate` / `expirationDate` — `YYYYMMDDTHH:MM:SSZ`. Expired packs show a warning banner in ForeFlight.
- `organizationName` — displayed alongside the pack name.

---

## 5. KML subset that actually renders in ForeFlight

ForeFlight supports a restricted subset of the KML 2.2 spec. Stick to these or the pack will silently drop styles/elements:

**Supported:**
- `<Point>`, `<LineString>`, `<Polygon>`
- `<Style>`, `<IconStyle>`, `<LineStyle>`, `<PolyStyle>`
- `<name>`, `<description>` (with CDATA-wrapped HTML)
- `<drawOrder>` for layer z-ordering
- `<tessellate>1</tessellate>` inside `<Polygon>` — required for polygons to render correctly

**Not supported / silently dropped:**
- `<Folder>` nesting — flatten placemarks to the `<Document>` root
- Shared `<Style id="...">` referenced by `<styleUrl>#id>` — **put the `<Style>` inline inside each `<Placemark>` instead**, ForeFlight frequently drops shared style references
- `<BalloonStyle>` — tap popups use the description directly, not balloon templates
- 3D extrusions, time animation, network links, tour elements
- The `earth.google.com` XML namespace for fill/extrude tricks — stick to the OGC namespace `http://www.opengis.net/kml/2.2`

**Known gotchas:**
- Text **outside** `CDATA` (e.g. `<name>` contents, description text not wrapped in `<![CDATA[...]]>`) must be **ASCII** — non-ASCII characters (curly quotes, accented letters) often cause import failures. Inside CDATA, UTF-8 is fine.
- `<PolyStyle>` color uses **AABBGGRR** hex order (alpha-blue-green-red), not RRGGBB. `<fill>1</fill>` is required for the fill to render.
- For layered displays (e.g. polygon zones + point icons on top), set a higher `<drawOrder>` on the points and a low-alpha polygon fill color — see [reference_kml_layer_ordering.md](Indian_Reservations/scripts/build_kml.py) for the pattern in practice.

---

## 6. HTML descriptions — styling that actually reads on iPad

When a `/layers/` KML placemark is tapped, ForeFlight opens a full-width **Description** panel and paints the HTML inside `<description><![CDATA[...]]></description>`. This is your one channel for per-pin detail, so readability matters — and the renderer has one big non-obvious quirk.

**The core finding:** ForeFlight's Description renderer scales inline CSS `px` values **far more aggressively** than a normal WebKit view. A size that looks reasonable in a browser preview comes out roughly 2.5–3× too small on device. Plan on typing much larger numbers than you'd use for a web page.

### Device-tested baseline sizes (iPad, arm's-length reading, no pinch-zoom)

These numbers have been iterated against device screenshots. Use them as defaults.

| Element | Size |
|---|---|
| Body copy — review text, address, phone, meta rows, links | **30px** |
| Primary item title (`<h2>`) — name of the restaurant / airport / zone | **52px** |
| Large decorative glyphs (e.g. ★ stars, large icons at top of card) | **52px** |
| Section label ("INSPECTOR'S REVIEW"-style small caps) | **26px** |
| Supplementary/source footer | **22px** |
| Line-height on multi-line text blocks | **1.5** |
| Margin-bottom between content blocks | **20–22px** |

### Rules of thumb

- **Give every styled element an explicit inline `font-size`.** Do not rely on default heading sizes (`<h1>`/`<h2>`/`<h3>`) or default paragraph text — they render smaller than expected. Inline styles are the only reliable lever.
- **If it looks right in a browser, it's wrong on iPad.** Multiply browser-sized CSS values by ≈2.5–3×.
- **Use `<div style="...">` instead of `<span style="...">` for block-level layout** — `<span>` is less consistently honored.
- **Inline styles only.** `<style>` blocks, external stylesheets, and class-based selectors inside descriptions don't work. Every rule goes in `style="..."` attributes on the element.
- **Test on device, not in a browser preview.** Any round of tuning that skipped this step has produced sizes too small to read.

### Known-good inline tags inside descriptions

- Structure: `<div>`, `<h1>`–`<h6>`, `<p>`, `<br/>`, `<hr/>`
- Text: `<b>`, `<i>`, `<u>`, `<span>`
- Links (all reliably tap-able on iPad): `<a href="tel:+1...">`, `<a href="https://...">`, `<a href="https://maps.apple.com/?q=...&ll=lat,lon">` (opens Apple Maps on iOS/iPadOS, web fallback on desktop)
- Entities: `&rsquo;`, `&middot;`, `&rarr;`, `&ldquo;` / `&rdquo;`, numeric entities like `&#9733;` for ★ when you want to avoid emitting non-ASCII bytes into the KML source
- Inline CSS properties that work: `color`, `font-size`, `font-weight`, `font-style`, `letter-spacing`, `line-height`, `margin`, `margin-top/bottom/left/right`, `text-decoration`

### What does *not* work in descriptions

- `<style>` blocks, `<link>` tags, external CSS, `class=""` selectors
- `<script>` or any JavaScript
- `<iframe>`, `<video>`, `<audio>`, `<img src="local-file.png">` (local pack-relative images do not resolve)
- `<a href="file.pdf">` pointing at a pack-local PDF — there is no pack-local URL scheme, so the link does nothing (see §2.1)
- Background images, CSS gradients, CSS animations, `@media` queries

### Reference implementation

[Michelin_Restaurants/scripts/build_layer_kmls.py](Michelin_Restaurants/scripts/build_layer_kmls.py) — the `describe()` function contains the tested-on-device sizing and the `link()` / `phone_uri()` / `maps_uri()` helpers. Copy the sizing skeleton and re-skin the content for a new pack's data shape.

---

## 7. Common mistakes

1. **Duplicating waypoints in both CSV and KML inside `navdata/`** → shows up as two layers in ForeFlight. Pick one.
2. **Putting PDFs in `layers/`** → does nothing. PDFs must be in `navdata/`.
3. **Expecting `<a href="foo.pdf">` in a layer placemark description to open a local PDF** → doesn't work. Local pack files aren't addressable from KML descriptions.
4. **Wrapping the pack in a parent folder before zipping** → ForeFlight expects `layers/`, `navdata/`, `manifest.json` at the *zip root*, not nested one level deep. Zip the *contents* of the pack folder, not the folder itself.
5. **Reducing waypoint count across an update without bumping the abbreviation** → ForeFlight may refuse the new pack. Either keep counts monotonic or change `MR.V1` → `MR.V2` in `manifest.json`.
6. **Using shared KML styles via `<styleUrl>`** → styles get dropped. Inline the `<Style>` inside every `<Placemark>`.
7. **Non-ASCII characters in `<name>` or un-CDATA'd text** → silent import failure or mangled display.
8. **Oversized zip** → ForeFlight has no hard cap, but pack import/render slows noticeably past ~10 MB on iPad. Simplify geometry (Shapely `.simplify()`), drop unused KML attributes, and quantize coordinates to 5 decimal places (≈1 m precision, plenty for aviation).

---

## 8. The per-pack build pipeline used in this repo

Each pack in this repo follows a common scaffolding (reference: [Indian_Reservations/](Indian_Reservations/)):

```
<Pack_Name>/
├── README.md              end-user description
├── scripts/
│   ├── fetch_*.py         pull raw source data into data/
│   ├── build_*.py         transform source data into pack/ artifacts
│   ├── validate_pack.py   static checks (non-ASCII, bad colors, zip layout)
│   └── package.py         write manifest.json, run validator, zip pack/
├── content/               human-authored Markdown (source for PDFs, if any)
├── data/                  cached source downloads (git-ignored)
├── pack/                  the actual ForeFlight pack — this is what gets zipped
│   ├── manifest.json
│   ├── layers/
│   └── navdata/
└── <Pack_Name>_Pack.zip   the publishable artifact (committed)
```

**Conventions:**
- `scripts/package.py` **must** run `scripts/validate_pack.py` before zipping and fail the build on any validator error. The validator is cheap insurance against silent ForeFlight import failures.
- `<Pack_Name>_Pack.zip` is regenerated by `package.py` and committed so end users can download directly from GitHub.
- `manifest.json` version is auto-bumped to the current UTC timestamp on each build.

---

## 9. References

- [ForeFlight Content Packs — official docs](https://foreflight.com/support/content-packs/)
- [ForeFlight User Content — official docs](https://foreflight.com/support/user-content/)
- [KMZ file support announcement](https://foreflight.com/enhancements/kmz-file-support)
- [BYOP (Bring Your Own Plates) support](https://foreflight.com/support/byop/)
- Reference pack in this repo: [Indian_Reservations/](Indian_Reservations/) (validator + build pipeline)
- Minimal `navdata/`-only pack: [Airport_Restaurants/](Airport_Restaurants/)
- Minimal `layers/`-only pack: [Diners_Drive_Ins_Dives/](Diners_Drive_Ins_Dives/)
