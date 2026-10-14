# UW Campus 3D Model

An independent, bilingual exterior model of the **University of Washington Seattle campus**. Open `index.html` by double-clicking it with the `assets` and `output` folders beside it, or open the single-file offline edition.

华盛顿大学西雅图校区室外三维模型，覆盖中央校区、西校区、南校区与医学区、东校区与体育区。英文为默认语言；首次打开统一使用英文，可随时切换中英文。

## Deliverables

| File | Purpose |
| --- | --- |
| `index.html` | Root website; works through HTTP and by double-click |
| `output/UW_Campus_Offline.html` | Self-contained offline viewer (generated locally; included in delivery ZIP) |
| `output/UW_Seattle.3ds` | 3DS exterior mesh, 1 unit = 1 meter |
| `output/UW_Seattle_Layered.3dm` | Rhino v7 with native building solids and layers |
| `output/building_dimensions_and_sources.csv` | Mapped dimensions, estimated heights and source notes |
| `output/layer_map.json` | 3DS object names → native building / environment layers |
| `scripts/apply_layers_rhino.py` | Restore layers after importing the 3DS into Rhino |
| `output/campus_aerial.png` | Campus preview and social sharing image |
| `output/usage_guide.md` | Chinese usage notes, with English filenames |
| `output/3ds_validation.json` | Independent 3DS import report |
| `output/rhino_validation.json` | Rhino units, valid geometry and layer report |

## Model and interaction

The model contains **271 mapped facility/building layers plus one Environment layer**, 26 architectural highlights, **8,427 official tree positions** and 29 cherry canopies around the Quad. Named wings and disconnected pieces sharing a facility code share a layer. The official facility layer's ponds and helipad belong to the environment, not building volumes. Excluded facilities are recorded in `output/excluded_records.json`.

The initial Core view centers Red Square from the southwest, with north pointing upper-left. Persistent landmark labels start off; hovering a mapped outdoor place or building still shows its name. Reset restores it. Campus shows a wider overview; district and Plan controls provide other views. The East & Athletics preset focuses on Husky Stadium and the adjacent principal athletic facilities. Left-drag pans, right-drag rotates, and the wheel zooms at the pointer. One finger pans; two fingers pan or pinch. Rotate enables one-finger rotation. Camera pivots stay grounded, there is no inertia, and zoom-out remains campus-wide after choosing a landmark.

Search works in both languages and by official code. Buildings can be selected, hidden, isolated or located. Selection retains a clear highlight. Mapped outdoor places have bilingual hover names; smaller pools take priority over enclosing plazas, while buildings retain priority. The viewer includes architectural tours, progress/percentage loading, shadows, metric scale, labels, elevation slicing, 3DS download and PNG export. Roof depth separation, fixed shadow filtering and continuous terrain lighting avoid unstable coplanar surfaces during navigation.

## Sources and measurement limits

- **UW public GIS** supplies georeferenced building footprints and names, tree positions, bench positions and supplemental path routes: https://facilities.uw.edu/services/space/gis-maps . The modeled snapshot includes the 2025 Interdisciplinary Engineering Building and basketball facility shown in the public layer.
- **OpenStreetMap contributors** supply supplementary road, path, plaza, lawn, field and shoreline geometry: https://www.openstreetmap.org/copyright . Some road widths use contributed tags; unrecorded widths are illustrative.
- **USGS 3DEP** supplies bare-earth terrain at about 10m sampling: https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer . Building pads are locally flattened. Lake surfaces use an approximate common level.
- Projection: **EPSG:32610**, with local meter offsets from WGS84 [-122.3093, 47.6558]. Z uses the DEM meter elevation datum. The elevation slice is an elevation plane, not building-relative storeys.
- Core refinements include aligned Gothic wing roofs, stone courses and entrances, Suzzallo reading-room window groups, Red Square brick courses and approximate monuments, the Quad’s unified mapped brick walks, Pierce Lane connection and 29 mapped Yoshino trees with their original simple canopy style, and Drumheller Fountain’s flat basin, coping, volumetric plume, arced jets, splash rings and restrained ripples. Small details and vertical dimensions remain approximate.
- **All exterior heights, storeys, roof partitions, facade bays, canopies and detailed landscape forms are approximate.** Reported gross floor area can include basements and is not an exterior floor count. UW's published Suzzallo reading-room dimensions are interior dimensions, not the exterior building envelope. No whole-building height is presented as a measured survey.
- The model is an independent exterior study, not official university BIM. Original English names remain available beside faithful independent Chinese translations. Trees around the Quad use illustrative spring cherry color; this does not represent current seasonal conditions.

Sources, retrieval hashes and translation notes are in `sources`. See `docs/THIRD_PARTY_NOTICES.md` for attribution and third-party licenses.

## Website and releases

Canonical domain: https://uw.arch.songming.org/ . Repository: https://github.com/sd800/uw-3d-arch . The website includes bilingual crawlable building names, canonical, Open Graph, Twitter card, sitemap, robots and structured 3DModel metadata. `CNAME` is configured. To serve it with GitHub Pages, publish `main` from `/ (root)` and configure DNS to the Pages host; a CNAME file alone does not activate hosting or certificates.

`VERSION` records the calendar version. `CHANGELOG.md` is English and newest first; commit messages are `Release YY.M.D.NUM` using America/Chicago. Work on `main`; use the existing sd800 SSH key. All project filenames are English.

## Rebuild

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r scripts/requirements.txt
npm ci
python3 scripts/build_campus.py
python3 scripts/render_preview.py
npm run build
npm run check:3ds
python3 scripts/validate_rhino.py
npm run check:interaction
npm run check:seo
npm run check:release
python3 scripts/package_delivery.py
```

Source snapshots are retained; geometry rebuilding needs no live map access. `fetch_sources.py` and `fetch_terrain.py` retrieve public sources when an updated snapshot is explicitly needed. `prepare_sources.py` also accepts the compressed OSM API snapshots. A GPU-exported preview can replace the lightweight footprint preview before the final website build. WebGL 2 and Compression Streams are required for interactive viewing.

## Project layout

- `index.html`: website entry; root SEO files and `CNAME` support publishing.
- `assets/`: browser engine, fonts, icons and local model payload.
- `config/`: custom site configuration.
- `docs/`: project decisions and third-party license notices.
- `scripts/`: model generators, packaging and necessary checks.
- `sources/`: source snapshots and provenance.
- `output/`: CAD files, offline edition, reports and delivery archive.
- Root `VERSION`, `CHANGELOG.md` and package manifests record releases and builds.
