"""Write project notes and package the portable Seattle-campus delivery."""
from pathlib import Path
import json,zipfile,hashlib
r=Path(__file__).resolve().parents[1];out=r/'output';s=json.loads((out/'model_summary.json').read_text())
readme=f'''# UW Campus 3D Model

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

The model contains **{s['buildings']} mapped facility/building layers plus one Environment layer**, {s['landmarks']} architectural highlights, **{s['trees']:,} official tree positions** and {s['quad_cherry_trees']} cherry canopies around the Quad. Named wings and disconnected pieces sharing a facility code share a layer. The official facility layer's ponds and helipad belong to the environment, not building volumes. Excluded facilities are recorded in `output/excluded_records.json`.

The initial Core view centers Red Square from the southwest, with north pointing upper-left. Persistent landmark labels start off; hovering a mapped outdoor place or building still shows its name. Reset restores it. Campus shows a wider overview; district and Plan controls provide other views. The East & Athletics preset focuses on Husky Stadium and the adjacent principal athletic facilities. Left-drag pans, right-drag rotates, and the wheel zooms at the pointer. One finger pans; two fingers pan or pinch. Rotate enables one-finger rotation. Camera pivots stay grounded, there is no inertia, and zoom-out remains campus-wide after choosing a landmark.

Search works in both languages and by official code. Buildings can be selected, hidden, isolated or located. Selection retains a clear highlight. Mapped outdoor places have bilingual hover names; smaller pools take priority over enclosing plazas, while buildings retain priority. The viewer includes architectural tours, progress/percentage loading, shadows, metric scale, labels, elevation slicing, 3DS download and PNG export. Roof depth separation, fixed shadow filtering and continuous terrain lighting avoid unstable coplanar surfaces during navigation.

## Sources and measurement limits

- **UW public GIS** supplies georeferenced building footprints and names, tree positions, bench positions and supplemental path routes: https://facilities.uw.edu/services/space/gis-maps . The modeled snapshot includes the 2025 Interdisciplinary Engineering Building and basketball facility shown in the public layer.
- **OpenStreetMap contributors** supply supplementary road, path, plaza, lawn, field and shoreline geometry: https://www.openstreetmap.org/copyright . Some road widths use contributed tags; unrecorded widths are illustrative.
- **USGS 3DEP** supplies bare-earth terrain at about 10m sampling: https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer . Building pads are locally flattened. Lake surfaces use an approximate common level.
- Projection: **EPSG:32610**, with local meter offsets from WGS84 {s['origin_wgs84']}. Z uses the DEM meter elevation datum. The elevation slice is an elevation plane, not building-relative storeys.
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
'''
readme+='\n## Project layout\n\n- `index.html`: website entry; root SEO files and `CNAME` support publishing.\n- `assets/`: browser engine, fonts, icons and local model payload.\n- `config/`: custom site configuration.\n- `docs/`: project decisions and third-party license notices.\n- `scripts/`: model generators, packaging and necessary checks.\n- `sources/`: source snapshots and provenance.\n- `output/`: CAD files, offline edition, reports and delivery archive.\n- Root `VERSION`, `CHANGELOG.md` and package manifests record releases and builds.\n'
web_report=json.loads((out/'web_model_report.json').read_text())
readme+=f'\n## Website model compression\n\nThe initial model transfer is **{web_report["transferBytes"]/1e6:.2f} MB**, down from **{web_report["previousTransferBytes"]/1e6:.2f} MB** ({100*(1-web_report["transferBytes"]/web_report["previousTransferBytes"]):.1f}% smaller). The web stream uses meshoptimizer 1.3.0 lossless vertex/index-sequence coding followed by gzip. No quantization or simplification is applied; its decoded SHA-256 matches the original 3DS. Rhino and original 3DS downloads stay unchanged.\n\nA single browser worker streams gzip decompression, restores small geometry blocks and parses the CAD model. Its compressed input and resulting geometry buffers are transferred rather than copied. The full intermediate archive is never retained. Scene setup yields to rendering between time slices; browsers that block workers use cooperative per-object parsing. Standalone HTML restores the downloadable CAD on demand in a worker. Decoder JavaScript/WebAssembly is bundled locally and requires no CDN. See `output/web_model_report.json` for byte counts, source digest and maximum block size. `npm run build:model` rebuilds the stream; `npm run check:compression` checks lossless restoration and worker behavior.\n'
(r/'README.md').write_text(readme)
(r/'docs/PROJECT_NOTES.md').write_text('''# Project decisions

- University of Washington, Seattle campus; independent public-source exterior model.
- Chinese university name: 华盛顿大学; Seattle: 西雅图. Preserve original English proper names for comparison.
- Individual official facility/building layers plus one Environment layer; unit meters.
- Use established readable typography, selected highlights, grounded navigation, stable rendering, and loading progress. Resize and redraw atomically. No Level toolbar option.
- Default Core bearing matches the southwest reference; persistent labels off, contextual hover names on.
- Red Square, Quad and fountain details are kept on the Environment layer; detailed core building parts remain on their building layers.
- English default regardless of device language; retain manual Chinese switching. Root double-click and single-file offline editions.
- Domain: https://uw.arch.songming.org/ . Repository: https://github.com/sd800/uw-3d-arch . Push on main with the existing sd800 key.
- English title: UW Campus 3D Model. Chinese title: 华盛顿大学 · 三维校区.
- Icon: independent pale-gold W and upright rectangular map on purple.
- Calendar versions, English CHANGELOG, root VERSION and English filenames.
- Necessary, concise checks; avoid unrelated or repeated test runs.

- Building ground contacts use exact footprint holes, flat pads and closed below-grade visualization supports. Overlapping projected wings share an area-weighted pad elevation to avoid contradictory intersecting terrain skins. These simplified supports are not surveyed foundations. The exported 3DS is checked independently against footprint contact samples.


## Outdoor parking references

The source audit reviews each model-scope grouped surface parking polygon against public Esri World Imagery. `sources/parking_satellite_review.json` retains stable export URLs, image extents, observation limits and original lot IDs; no imagery is redistributed. `sources/parking_rows.json` contains explicitly interpreted row paths, not a stripe array fitted to a lot envelope. `sources/parking_paint.geojson`, where present, retains primary CAD dividers or individually observed paint. Bay spacing and depth remain exterior approximations; faded/obscured paint, construction, service areas and unmarked parcels receive no invented grid. Current building footprints and planting override old paint. `output/parking_validation.json` records the rendered paths and clearance policy.
''')
(r/'sources/SOURCES.md').write_text('''# Source notes

Snapshot: 13 October 2026.

| Dataset | Use | Limits |
| --- | --- | --- |
| [UW public building layer](https://gis.maps.uw.edu/federated/rest/services/BaseComponents/UW_Seattle_Buildings_and_Paths/MapServer/1) | Facility codes, names, footprint geometry, year built and gross floor area | Footprint reference, not measured exterior height or BIM; mapped current status can lag changes |
| [UW public data](https://gis.maps.uw.edu/federated/rest/services/PublicData/PublicData/MapServer) | Tree/bench positions and supplemental walk routes | Canopy forms, heights, path widths and furniture details are approximate |
| [OpenStreetMap](https://www.openstreetmap.org/copyright) | Campus boundary, roads, paths, paved squares, landscape, fields and water banks | Contributed map data, estimated widths where no width tag exists; ODbL attribution retained |
| [UW campus highlights](https://www.washington.edu/visit/campus-highlights-guide/) | Red Square brick surface, Quad landscape and Drumheller Fountain | Paving courses, step sections, sculpture forms and jets are approximate |
| [UW cherry map](https://www.washington.edu/cherryblossoms/campus-map-of-cherry-trees/) | Species/landscape context for official tree-position data | The saved GIS has 29 Yoshino positions in the Quad; canopy and branches are illustrative |
| [USGS 3DEP](https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer) | F32 bare-earth terrain in EPSG:32610 | About 10m sampling; flattened building pads; no survey certification |
| [UW Suzzallo history](https://lib.uw.edu/locations-hours/suzzallo-and-allen-libraries-history/) | Reading-room dimensions and exterior-form reference | Published 250 × 52 × 65 ft dimensions are interior, not whole-building extents |
| [Husky Stadium / HOK](https://www.hok.com/projects/view/university-of-washington-husky-stadium-renovation-and-expansion/) | Mapped field axis, opposing metal cantilevers, stepped bowl and west operations building | Playing field uses standard 120 × 53⅓ yd dimensions; stand rows, roof elevations and structures are approximate, not surveyed |

The university already offers its own rendered campus map: https://map.uw.edu/?id=2099 . This project creates an independent layered metric model from public mapping; it does not extract or distribute that map's proprietary rendered assets.

The raw official footprint and public tree/bench files retain coordinates. The normalized OSM source includes data outside the rendered scope for boundary closure; the model clips it to the chosen campus/shore context. `retrieval_manifest.json` records source URLs and hashes. Original raw OSM extracts are compressed. Rebuilding uses saved data, not live APIs.
''')
(r/'sources/TRANSLATION_NOTES.md').write_text('''# Translation notes

华盛顿大学 and 西雅图 are used consistently. Proper-name surnames are transliterated; building functions are translated faithfully. Court in a residential context is a courtyard/residential group, not a law court. Pavilion is translated according to its medical or athletic use. ASUW remains the student association acronym; its Shell House is a rowing boathouse.

- Red Square → 红场; Central Plaza is the official alternate name.
- The Quad → The Quad 庭院; the proper nickname remains identifiable.
- Rainier Vista → 雷尼尔山景观轴线; this is the campus view corridor rather than a building.
- Drumheller Fountain → 德拉姆赫勒喷泉.
- Portage Bay → 波蒂奇湾; Union Bay → 联合湾; Lake Washington → 华盛顿湖.
- Montlake Cut → 蒙特莱克水道; Cut denotes the connecting navigational channel.
- Intellectual House → 原住民文化交流中心; the original English name remains available in building details.

Chinese labels are independent project translations, not claimed as official UW translations. Full English and original GIS names remain available in the building detail and source CSV.
''')
usage=f'''# 华盛顿大学西雅图校区模型使用说明

模型包含{s['buildings']}个建筑／设施图层、1个Environment环境层和{s['landmarks']}处建筑地标，单位为米。

1. 保留根目录index.html与assets、output的相对位置，双击index.html打开；也可使用output/UW_Campus_Offline.html单文件离线版本。
2. 首次打开统一使用英文，不受设备语言影响；页眉按钮可切换语言。
3. 左键拖动平移，右键拖动旋转，滚轮以指针位置缩放。触屏单指平移，双指平移或捏合；开启旋转后可单指旋转。松手后立即停止。
4. 初始核心镜头围绕红场取景；重置恢复该视角。校区鸟瞰、片区和总平面按钮提供其他取景。
5. 点击建筑或左侧列表，查看尺寸、原英文名称与来源，可定位、隐藏或单独查看。3DS下载和保存视图在加载完成后可用。
6. 高程剖切按DEM米制标高切割外部表面，并不表示室内结构或相对楼层。
7. 场所和建筑的鼠标悬停提示独立于常驻地标标签；关闭环境层时不显示室外场所提示。
8. Rhino优先打开output/UW_Seattle_Layered.3dm。导入output/UW_Seattle.3ds时选择米，再运行scripts/apply_layers_rhino.py恢复图层。

建筑平面与树位有公开地图坐标依据；外部高度、屋顶、窗格、树冠与部分道路宽度为估算。地形来自约10米采样的USGS数据，建筑基座局部平整化。模型未经过实测校核，不是校方官方BIM。中文译名保持原义，详情保留英文专名供对照。
'''
(out/'usage_guide.md').write_text(usage)
# Keep the archive independent of local dependencies and discovery diagnostics.
ignored={'.git','node_modules','tmp','__pycache__','.venv'}
files=[p for p in r.rglob('*') if p.is_file() and p.name!='.DS_Store' and not p.name.startswith('._') and not any(part in ignored for part in p.relative_to(r).parts) and p.suffix not in ['.zip','.npz','.xml'] and not p.name.endswith(('_catalog.json','_layer.json','_page.html')) and p.name!='uw_legacy_map.js']
archive=out/'UW_Seattle_Delivery.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(files):z.write(p,p.relative_to(r))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None;assert all(n.isascii() for n in z.namelist())
print('Documentation and delivery ZIP:',len(files),'files,',archive.stat().st_size,'bytes')
