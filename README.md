# ForeFlight Content Packs

A collection of ForeFlight content packs for general aviation pilots, each built with a reproducible Python pipeline. Every pack is self-contained in its own subfolder with the source data fetch, build scripts, and a pre-built distribution zip ready to AirDrop to an iPad and import into ForeFlight.

## Packs in this repo

| Pack | Description | Size |
|---|---|---|
| [Indian_Reservations](Indian_Reservations/) | U.S. federal American Indian reservation boundaries with searchable centroid waypoints, overflight-considerations PDF, and citation-driven special-airspace PDF covering Grand Canyon SFRA, Taos Pueblo, NPATMA ATMPs, and Red Lake | ~300 KB |

## Install a pack in ForeFlight

1. Grab the `<Pack_Name>_Pack.zip` file from the relevant subfolder (or build your own — each pack's `README.md` has rebuild instructions).
2. AirDrop or email the zip to your iPad.
3. iOS will offer "Copy to ForeFlight" — accept.
4. In ForeFlight: **More → Content Packs** and toggle the pack on.
5. On the map, enable the layers from the layer selector.

## Layout

Each pack is a self-contained subfolder:

```
<Pack_Name>/
├── README.md
├── scripts/        Python build pipeline
├── content/        Markdown sources for PDFs
├── data/           cached source downloads (git-ignored; regenerate with fetch script)
├── pack/           the actual ForeFlight content pack (zipped for import)
└── <Pack_Name>_Pack.zip
```

## Contributing a new pack

1. Create a new subfolder at the repo root.
2. Mirror the layout above: `scripts/`, `content/`, `data/`, `pack/layers/`, `pack/navdata/`.
3. Follow the KML conventions that actually render in ForeFlight — inline `<Style>` per `<Placemark>`, `<tessellate>1</tessellate>` on every `<Polygon>`, no `<Folder>` or `<BalloonStyle>`, `<PolyStyle><fill>1</fill>` with an AABBGGRR color. See `Indian_Reservations/scripts/build_kml.py` for a working reference.
4. Keep the zipped pack under ~10 MB for iPad responsiveness. Simplify geometry with Shapely if needed.
5. Cite your sources. Advisory-circular and CFR references belong in the PDFs; speculation doesn't.

## Disclaimer

These packs are for situational awareness only. They are not a substitute for current FAA publications, sectional charts, the Chart Supplement, or NOTAMs. Always check current sources before flight.
