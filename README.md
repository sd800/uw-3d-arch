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
| `output/neighboring_building_dimensions_and_sources.csv` | Neighboring building dimensions, storeys and sources |
| `output/neighboring_areas.json` | Context scope, grade pads, ground samples and counts |
| `output/UW_Seattle.fbx` | Binary FBX 7.4 mesh model, grouped by building/layer |
| `output/UW_Seattle.glb` | Standard extension-free glTF 2.0 binary model |
| `output/layer_map.json` | 3DS object names → native building / environment layers |
| `scripts/apply_layers_rhino.py` | Restore layers after importing the 3DS into Rhino |
| `output/campus_aerial.png` | Campus preview and social sharing image |
| `output/usage_guide.md` | Chinese usage notes, with English filenames |
| `output/3ds_validation.json` | Independent 3DS import report |
| `output/rhino_validation.json` | Rhino units, valid geometry and layer report |

## Model and interaction

Low-angle views retain a continuous closed terrain mass and occlude buried geometry. Terrain sides fade gently downward at the model boundary; roads, lawns and water retain stable map ordering. The browser derives this display shell without changing the source CAD elevations.

The campus contains **272 mapped facility/building layers plus one Environment layer** (271 UW inventory facilities and the mapped Sound Transit surface station), 28 building highlights plus Drumheller Fountain (29 tour stops), **8,602 official tree positions** and 29 cherry canopies around the Quad. Named wings and disconnected pieces sharing a facility code share a layer. The official facility layer's ponds and helipad belong to the environment, not building volumes. Excluded facilities are recorded in `output/excluded_records.json`.

The surrounding U District adds **597 individually layered buildings** and a separate `Neighboring_Environment` layer. University Way (the Ave), Brooklyn Avenue, the U District station precinct, Roosevelt Way, north-campus residential blocks and the west-campus waterfront are included. Neighboring buildings use a subtly muted palette, with ⁺ prefixed to their displayed names. In **All**, the first row is **⁺Campus neighboring areas**, checked by default. Uncheck it to hide surrounding buildings, streets and landscape together without moving the camera; click its name to frame the area. Searching in All also finds neighboring buildings; while searching, only matching buildings are listed and the group row is hidden. Campus building counts stay separate.

Alder Hall retains its mapped open-air stepped light court, charcoal street brick, pale courtyard elevations and paired white-framed windows. Its four street frontages include graded entry aprons, mapped sidewalk modules, interrupted curbs, tree pits at published tree positions and grounded bench details. Courtyard planting and furnishings are photo-informed approximations.

Suzzallo’s west entrance is modeled from exterior photographs with three recessed pointed portals, thirteen reading-room window bays, a continuous brick/stone terrace and a broad, short central stair with closed stone cheeks and flush brick paving at its foot and flanks. Its Explore view faces the entrance from the west with a slight southern offset. Plaza-side walks connect Kane, Odegaard, Meany and Gerberding through graded entrance shelves; Meany has separate teaching, performance and stage volumes. University of Washington Station has a rectangular upper glass bar, lower canopies, open bridge/ground portals and an intermediate circulation void.

The initial Core view centers Red Square from the southwest, with north pointing upper-left. Persistent landmark labels start off; hovering a mapped outdoor place or building still shows its name. Reset restores it. Campus shows a wider overview; district and Plan controls provide other views. The East & Athletics preset focuses on Husky Stadium and the adjacent principal athletic facilities. Left-drag pans, right-drag rotates, and the wheel zooms at the pointer. One finger pans; move two fingers together up or down to tilt, twist to turn, and pinch to zoom. Two-finger tilt works without enabling Rotate; Rotate also enables one-finger orbit. Camera pivots stay grounded, there is no inertia, and zoom-out remains campus-wide after choosing a landmark.

Search works in both languages and by official code. Buildings can be selected, hidden, isolated or located. Selection retains a clear highlight. Mapped outdoor places have bilingual hover names; smaller pools take priority over enclosing plazas, while buildings retain priority. The viewer includes architectural tours, progress/percentage loading, shadows, metric scale, labels, elevation slicing, 3DS download and PNG export. Roof depth separation, fixed shadow filtering and continuous terrain lighting avoid unstable coplanar surfaces during navigation.

## Sources and measurement limits

- **UW public GIS** supplies georeferenced building footprints and names, tree positions, bench positions and supplemental path routes: https://facilities.uw.edu/services/space/gis-maps . The modeled snapshot includes the 2025 Interdisciplinary Engineering Building and basketball facility shown in the public layer.
- **Seattle SDOT** supplies in-service street-tree positions in the neighboring streets: https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/SDOT_Trees_CDL/FeatureServer/0 . The query, retrieval date and digest are retained in `sources/neighborhood_tree_provenance.json`; canopy dimensions are illustrative.
- **OpenStreetMap contributors** supply supplementary road, path, plaza, lawn, field and shoreline geometry: https://www.openstreetmap.org/copyright . Some road widths use contributed tags; unrecorded widths are illustrative.
- **USGS 3DEP** supplies bare-earth terrain at about 10m sampling: https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer . Building pads are locally flattened. Lake surfaces use an approximate common level.
- Projection: **EPSG:32610**, with local meter offsets from WGS84 [-122.3093, 47.6558]. Z uses the DEM meter elevation datum. The elevation slice is an elevation plane, not building-relative storeys.
- Core refinements include aligned Gothic wing roofs, stone courses and entrances, Suzzallo reading-room window groups, Red Square brick courses and approximate monuments, the Quad’s unified mapped brick walks, Pierce Lane connection and 29 mapped Yoshino trees with their original simple canopy style, and Drumheller Fountain’s flat basin, coping, volumetric plume, arced jets, splash rings and restrained ripples. Small details and vertical dimensions remain approximate.
- Architecture refinement distinguishes core facilities and the West Campus housing groups using primary architectural references and reviewed aerial imagery. The remaining secondary facilities now use purpose-specific windows, floor courses, attached roofs/parapets and grounded entries/service doors. Individual roof colors are preserved; unverified equipment boxes are omitted. `output/architecture_refinement.json`, `output/west_housing_refinement.json` and `output/ordinary_architecture.json` distinguish these levels of evidence.
- University Inn is interpreted from the operator’s exterior gallery: three guest-room floors over a recessed arrival/parking level, paired glazing, attached folded eaves, a rounded warm-colored end, a vertical sign and supported canopy. No swimming-pool position is invented where the available map does not establish it.
- Shoreline refinements retain mapped reserve, marsh/island, pier and bank geometry. The Union Bay Natural Area, Yesler Swamp and shoreside parks are included. Commercial/service parcels, residential forecourts and the former University Temple vacant site receive distinct ground materials and a mapped site boundary. Artificial outer lake limits are rounded and softly shaded into the background; ground skins beneath open water are omitted, while actual banks are retained. Closed dock decks stay above lake level, and bridge decks use continuous profiles joining their sampled bank approaches. Bridge elevations and members remain illustrative, not engineering measurements.
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
python3 scripts/ground_contact_samples.py
python3 scripts/render_preview.py
npm run build
npm run check:3ds
npm run check:ground
npm run check:transit
npm run check:core-connections
python3 scripts/validate_rhino.py
npm run check:interaction
npm run check:seo
npm run check:release
python3 scripts/package_delivery.py --archive-only
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

## Website model delivery

The viewer uses standard glTF 2.0 binary (GLB). The lossless complete-model derivative is **11.07 MiB** transferred, from a **71.16 MiB** extension-free download GLB. `EXT_meshopt_compression` and gzip reduce transfer; decompressed position/index accessors match the native GLB byte for byte. No quantization or simplification is introduced by this format conversion.

A worker inflates/decompresses the complete GLB and calculates normals; geometry buffers transfer once to the main thread. Scene creation and no-worker fallback yield between work slices. The meshoptimizer JavaScript/WebAssembly codec is bundled locally. HTTP loads binary assets; double-click `file://` loads classic scripts, and the standalone edition embeds browsing data. WebGL 2, WebAssembly and Compression Streams are required by current delivery.

Downloads are listed **3DM → FBX → GLB**. 3DM retains editable Rhino solids and individual layers. FBX and GLB retain mesh geometry and material assignments, grouped by building/layer. FBX uses meter units and Z up; GLB uses a standard Y-up root transform with the metric source vertices retained below it. The public download GLB requires no optional extensions. Files exceeding the hosting per-file limit are delivered losslessly as `.xz`; extract before importing.

`output/exchange_model_report.json` records native mesh counts/hashes; `output/web_model_report.json` records complete GLB transfer counts/hashes. `npm run check:glb` verifies lossless accessor equality, HTTP/local/offline byte integrity and ordered downloads; `npm run check:exchange` compares every FBX vertex/index against GLB and checks units/normals. Rendering still needs memory for decoded geometry and framebuffers.

## West Campus housing

Elm, Poplar, Lander, Maple and Terry halls now have individual exterior profiles. Cedar East/West, all five Mercer blocks and nine Stevens apartment blocks are also refined (21 facilities total). Alder Hall remains in its existing dedicated builder. See [West housing reference review](sources/WEST_HOUSING_REFERENCES.md) and `output/west_housing_refinement.json`. Upper setbacks, facade and landscape dimensions are photo-informed approximations. The 3DS exporter omits redundant all-zero smoothing groups; vertices, faces, materials and default faceted shading are preserved.


## Architectural highlights

The 28-stop tour now lists Alder Hall second. Fifteen landmark exteriors and Henry’s separately layered AVA addition have individual rebuilt assemblies; other detailed highlights and all housing from the preceding release are retained. See [Highlights reference review](sources/HIGHLIGHTS_REFERENCES.md), `sources/highlights_review.json` and `output/highlight_refinement.json`. The tour frames the two visible Henry gallery wings together.
