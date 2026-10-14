# Project decisions

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
