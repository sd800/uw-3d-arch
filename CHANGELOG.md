# Changelog

## 26.10.15.2 — 2026-10-15

- Replace the Alder block’s coordinate-guessed crosswalks with 20 satellite-reviewed curb-to-curb crossing paths around Brooklyn Avenue, University Way, Campus Parkway and NE 40th Street. Use paired stripes aligned with each actual walking path, and clip every marking to the road while preserving median and sidewalk gaps.

- Rebuild Alder Hall’s north ground-floor frontage from September 2025 Street View and UW HFS entrance photographs: weathered-steel classroom panels and narrow lights, the mapped recessed hall entrance, timber/glass cafe and market frontage, and concrete arcade piers. Remove the misplaced through-passage and floating market sign.
- Replace the oversized building-connected bus canopies with two separate silver-framed glass Metro shelters at the mapped stops; retain a distinct shallow building canopy over the recessed shopfront.
- Refine Campus Parkway’s boarding sidewalk, planted pockets, supported seating edges, carriageway width, concrete road finish and restrained lane/joint markings. Preserve the mapped courtyard, building layer and surrounding transit models.

## 26.10.15.1 — 2026-10-15

- Refine the complete Alder Hall block between Campus Parkway, Brooklyn Avenue, University Way and NE 40th Street, with coherent paving, mapped tree pits, marked crossings, curb openings and connected street edges.
- Add building-integrated Bay 1/Bay 2 bus canopies, supported steel framing, stop flags, benches and timetable displays at mapped stop positions; refine District Market glazing, signs, service entrance and aerial-visible roof PV strips.
- Refine five nearby low-rise teaching/cultural buildings with separate roof profiles and use-specific facades, retaining their mapped footprints.
- Add University of Washington Station's mapped two-level glass headhouse, upper lobby, elevator projection and ground entries; connect the actual curved pedestrian/bicycle bridge graph, ramps, outdoor stairs and ground-reaching supports.
- Rebuild U District Station's south granite entrance/canopy and its north entrance within the Gateway podium; add station approach hover names that follow the neighboring-area visibility switch.
- Preserve existing campus layer codes, hidden initial landmark labels, English default and lossless worker-based model delivery; document source evidence and approximate exterior dimensions.

## 26.10.14.2 — 2026-10-14

- Refine Alder Hall’s four street frontages with graded entry aprons, mapped sidewalk paving/joints, curbs interrupted at pedestrian approaches, source-positioned tree pits and supported benches.
- Rebuild Alder Hall around its mapped open-air light court, adding six-storey gray-brick wings, pale courtyard elevations, paired windows, ground-level approach, continuous parapets and planted courtyard paving informed by UW HFS photos.

- Extend shallow terrain-tile undersides to a shared display datum and softly fade their unlit earth sides downward, removing the exposed faceted wedges in downhill horizontal views. Preserve the original CAD elevations and files.
- Restore terrain side/underside closure and an opaque top-depth barrier so horizontal views cannot see buried building bases through hills, ground pads or lake surfaces; keep road/lawn painting stable.

- Refine 79 mapped facilities across the core, north/west residences and medical precinct with individual masonry, timber, precast and glazing systems.
- Separate Suzzallo’s original reading hall, southeast Gothic wing and lower modern addition; add tall grouped windows, stepped attached buttresses and a grounded portal.
- Replace uninterrupted Quad gables with slate slope perimeters and flat inner roofs interpreted from reviewed aerial imagery. Rebuild Gerberding’s junction tower and Denny’s sandstone roof/cupola silhouette.
- Rebuild Burke’s timber enclosure and shed roof, Intellectual House’s cedar longhouse, McMahon’s separate towers and lower commons, and the atrium roofs of PACCAR, Gates Center and Odegaard.
- Correct Tower C from a spurious 99 m high-rise to a low-rise companion; retain the principal UW Tower separately.
- Distinguish Rosling’s bounded west shading sails, Life Sciences’ south solar fins, the dark-brick IEB and health-sciences glazing. Add source-supported roof PV and Rosling terrace treatments.
- Tighten the initial Core frame around Red Square, the Quad and fountain while retaining its southwest bearing. Keep longhouse overhangs on one continuous plane and separate the lower commons roof in Mary Gates Hall.
- Remove unsupported automatic rooftop equipment boxes, preserve individual roof colors, fit entry supports to terrain and retain the original 29 Quad cherry canopies.

- Refine secondary campus facilities with use-specific windows, floor courses, roof/parapet treatments, grounded entrances and service doors, while retaining public footprint and height evidence.
- Add individually layered neighboring buildings around University Way, Brooklyn Avenue, Roosevelt Way, the station precinct, north-campus housing and the west-campus waterfront, with a subtly muted exterior palette.
- Add the default-checked ⁺Campus neighboring areas row first in All, and prefix neighboring building names with ⁺. Hide/show its buildings, streets and landscape together, frame the neighborhood by clicking its name, and find neighboring buildings through All search; keep campus counts independent. Hide the group row while search text is entered.
- Rebuild University Inn from its official exterior gallery with a recessed arrival/parking floor, three guest-room storeys, paired multi-pane windows, attached folded eaves, rounded end, vertical sign and supported canopy. Distinguish the Neptune Building, University Book Store and prominent neighboring towers using primary references and mapped outlines.
- Add published SDOT street-tree positions, connect interrupted street/sidewalk patches, include mapped Union Bay reserves and wetlands, retain marsh islands and piers, and connect elevated bridge decks continuously to their bank approaches.
- Replace unclassified white neighborhood strips with mapped commercial/service paving, residential forecourts, planted yards and restrained sidewalks. Express the former University Temple parcel as a bounded vacant site rather than inventing the proposed towers.
- Round and soften artificial lake limits, buffer land separately from water and remove ground skins beneath lake water to prevent stray edge fragments, and let opaque water occlude submerged supports correctly. Preserve actual mapped shorelines, fill mapped dry island/bank interiors and soften far-bank landscape edges together with the lake.
- Keep all CAD solids closed and metric, prevent overlapping neighboring footprints, and extend ground-contact checks to neighboring layers. Preserve lossless browser compression and portable offline viewing.

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
