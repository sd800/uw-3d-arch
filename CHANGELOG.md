# Changelog

## 26.10.14.1 — 2026-10-14

- Add satellite-referenced rows in outdoor parking areas, including E1/E18 and the east-campus lots, with actual university CAD divider geometry for N1.
- Clip paint clear of current buildings and planting, preserve drive aisles and retain all-area imagery source/review records; leave unmarked or obscured areas without invented stripe grids.

## 26.10.13.5 — 2026-10-13

- Fit terrain around exact building footprints, add flat grade pads and closed below-grade supports, and include full perimeter buildings in the ground extent.
- Give overlapping mapped wings a shared visualization grade, avoiding intersecting pads that bury adjoining bases. Use the same grade lookup for camera pivots and hover.
- Stop reading device language; default to English while retaining manual language choices.

All notable changes to UW Campus 3D Model are recorded here. Versions use `YY.M.D.NUM`, with a daily release sequence in America/Chicago.

## 26.10.13.4 — 2026-10-13

- Compress the website model losslessly with vertex/index-stream coding and gzip: 20.72 MB → 10.10 MB (51.2% less model transfer). Keep the original 3DS and layered Rhino files unchanged.
- Stream decompression and geometry restoration in one background worker; transfer the compressed input and decoded geometry buffers instead of copying expanded CAD onto the UI thread.
- Bound temporary decode blocks, yield during scene preparation, and use cooperative object-by-object parsing when workers cannot start. Restore standalone CAD downloads only when requested.
- Cache model payloads by content digest and verify exact source bytes, geometry attributes, material groups and HTTP/local/standalone editions.

## 26.10.13.3 — 2026-10-13

- Default to English regardless of device locale while preserving manual language switching and remembered choices. Ignore Finder metadata in Git and delivery archives without deleting local files.

- Resize and redraw the WebGL canvas in the same animation frame, combining repeated resize notifications and skipping unchanged or hidden dimensions. Preserve navigation scale and framing while avoiding blank flashes and unnecessary shadow redraws.
- Set campus and landmark presets to a southwest oblique view with north pointing about 45 degrees to the upper left. Keep Red Square at the core view center.
- Display Intellectual House’s Chinese name without a parenthetical annotation while retaining its English name in building details.
- Start with landmark-name labels hidden; keep the label toggle available for manual use.

- Remove the Level button from the toolbar and update the interaction guide.

- Focus East & Athletics on the principal waterfront sports cluster. Rebuild Husky Stadium around its mapped field axis with stepped lower/upper stands, two cantilever roofs, west support building and football markings; retain explicit approximate-height notes.

- Group custom configuration under config/ and project/license documentation under docs/; update generators and references while preserving root website, SEO, release and build entry files.

- Add bilingual hover names for mapped outdoor places, with building-first picking, smaller-area priority and drag/touch safeguards. Coalesce pointer moves to one lookup per frame.

- Refine the core landscape with brick paving courses, Red Square monuments, Quad paths and the original simple faceted Yoshino canopies, plus a flat fountain basin, coping, a volumetric central plume, arced jets, splash rings and subtle ripples. Unify the Quad–Red Square approach along mapped Pierce Lane, remove duplicated path overlays and replace the misplaced stair overlay with two mapped three-step flights. Align Gothic roofs to mapped building axes and add core entrances, stone courses and Suzzallo reading-room window groups.

## 26.10.13.2 — 2026-10-13

- Use consistent Chinese labels for The Quad and Red Square across the viewer, offline edition, sharing metadata and translation notes.

## 26.10.13.1 — 2026-10-13

- Add a metric exterior model of the University of Washington Seattle campus, using official building footprints, tree positions, public landscape mapping and sampled USGS terrain. Keep each mapped facility on its own layer and all outdoor environment on one layer.
- Model campus landmarks, courtyards, Red Square, Drumheller Fountain, roads, paths, lawns, cherry canopies and waterfront sports facilities. Distinguish mapped dimensions from approximate heights, roofs, facades and tree forms.
- Add an English/Chinese website with device-language defaults, readable typography, architectural tours, search, layer visibility, selected-building highlights, district views, exact horizontal views and stable pointer-centered pan/zoom. Provide progress indicators and double-click offline editions.
- Deliver layered Rhino and 3DS files, English filenames, source notes, dimensions CSV and a portable archive. Configure canonical, sitemap, social metadata and custom domain `uw.arch.songming.org`.
