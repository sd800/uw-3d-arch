# Project decisions

- University of Washington, Seattle campus; independent public-source exterior model.
- Chinese university name: 华盛顿大学; Seattle: 西雅图. Preserve original English proper names for comparison.
- Individual official facility/building layers plus one Environment layer; unit meters. Additional N-prefixed neighboring building layers and Neighboring_Environment can be toggled together.
- All begins with a default-checked ⁺Campus neighboring areas row; selecting its name frames surrounding streets. Search in All includes neighboring buildings; the campus count remains campus-only.
- Neighboring materials are muted subtly; SDOT supplies published street-tree positions. Mapped reserves, wetlands, quays and continuous road/bridge connections fill the previous gaps.
- Alder Hall has its mapped open-air light court, six-storey street/courtyard facade systems and graded sidewalk approaches.
- Core facilities and West Campus housing have photo/reference-specific profiles; remaining secondary facilities use use-specific details with tagged roof forms. University Inn follows the official exterior gallery.
- See sources/ARCHITECTURE_REFERENCES.md and sources/NEIGHBORHOOD_REFERENCES.md for evidence and approximation limits.
- Retain a closed continuous ground display mass and a separate depth barrier for horizontal/low-angle occlusion; preserve CAD source elevations and stable map paint.
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

## Alder block and surface transit

See `../sources/TRANSIT_AND_ALDER_BLOCK.md` for the university/operator/architect evidence behind the whole Alder street block, custom UW bus canopies, both light-rail stations and the mapped Montlake pedestrian/bicycle bridge. The UW station is appended as LINK_UW, preserving existing layer codes. New public approach labels follow the neighboring-area switch. Closed structural supports and shared bridge/stair datums preserve low-angle continuity. Exterior/member dimensions remain approximate.

## West Campus housing

Five residence halls and the Cedar, Mercer and Stevens apartment groups use independent photo-referenced exterior systems. Alder remains in its existing dedicated builder. See [West housing sources](../sources/WEST_HOUSING_REFERENCES.md) and `output/west_housing_refinement.json` for the 21 facilities, upper courts/decks, wall materials, window modules and ground-fitted thresholds. Public floor-count tags do not certify above-ground storeys at every uphill frontage.


## Highlights review

The 28-stop tour includes Alder Hall second, with no Alder geometry changes. Fifteen tour buildings and the separately mapped AVA gallery addition have independent assemblies, including deep Kane portico voids, supported PACCAR arrival/meeting-room geometry, distinct science/health facade skins, lower boat-bay contact at Conibear and a pitched main Hec Edmundson roof. Existing custom Gothic/core, longhouse, museum, stadium and station models are retained after review. See [reference decisions](../sources/HIGHLIGHTS_REFERENCES.md).
