# Delivery validation

Release 26.10.15.9.

- Rhino v7 uses meter units with 871 nonempty layers, 1012 valid closed native solids and 4928 closed mesh objects. All read-back geometry is valid.
- Independent Three.js 3DS import preserves object names and their campus, neighboring and environment layer mappings.
- All 20 satellite-reviewed Alder-area crosswalk paths have exported paint: 40 direct ray probes passed. Crossings follow their mapped walking paths, use paired stripes and remain clipped inside roadway bounds.
- Alder Hall retains its mapped open-sky courtyard and enclosing roof wings. The north shopfront is recessed behind the column arcade; two independent shelter roofs keep the boarding lane clear. Twenty light-rail bridge/landing probes remain continuous.
- Ground contact: 6181 samples across 869 campus and neighboring buildings; no missing ground samples. Maximum numerical contact gap is below 0.001 m. Opaque terrain is retained at horizontal/low viewing angles.
- Navigation and loading checks cover grounded pivots, pointer-aligned pan/zoom, no inertia, drag/selection safeguards, atomic viewport resize/draw and English default with remembered manual language choices.
- Compressed web, local classic-script and standalone payloads restore the exact source 3DS bytes. Positions, normals, material groups and indices round-trip without geometry loss; worker decode and bounded blocks remain enabled.
- SEO checks cover canonical/domain, the 272-building bilingual directory, local assets, model digest and offline edition.
- Browser review uses the actual local WebGL viewer for Alder’s north frontage, shopfront recess, shelter/street relationship and surrounding crossing layout. Preview images are exported from that viewer.
- West housing: 21 facility layers have individual exterior systems. Focused ray probes retain open courts and recessed decks; all facade members stay within their roof bounds. Lander copper lounge panels remain confined to its northeast exterior corner. Alder and the other 848 unaffected layers have exactly the previous vertex/index/material data.
- Browser review also covers the rebuilt Lander frontage/court and Maple/Terry precinct; the housing preview is exported from the actual WebGL viewer.
- Finder metadata is ignored and retained locally, and excluded from the delivery ZIP.

These checks validate deliverable integrity and interaction, not as-built survey accuracy. External dimensions, grades and detail are public-source approximations. Direct file:// navigation is unavailable in the browser test interface; local/offline loader paths and exact embedded bytes are checked independently.
