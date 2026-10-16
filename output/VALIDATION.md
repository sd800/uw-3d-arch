# Delivery validation

Release 26.10.16.4.

- Rhino v7 read-back: meter units, 871 nonempty layers, 1036 valid closed native solids, 4979 closed meshes and 6019 total objects; all geometry is valid.
- Independent Three.js 3DS import: 4979 objects and 5,532,896 triangles; object names and layer mappings are preserved.
- Direct export rays verify all 14 Suzzallo treads, three physically recessed portals, the common entry/terrace datum, the lower brick forecourt at the foot and both flanks, and 28 Red Square perimeter stair samples. Ground terrain is included in the forecourt rays so it cannot pierce the finished paving. Six inner lancets and three supported figure/canopy silhouettes refine the recessed portals. The library Explore direction matches the supplied near-due-west, elevated entrance view.
- Station probes retain open south/bridge portals, an open intermediate circulation void, bridge-level upper lobby and clear outdoor stair landing. The main upper roof remains rectangular; lower canopy projections stay below it.
- Tour order starts Suzzallo, Alder, Drumheller Fountain. The 29 stops comprise 28 building highlights and one outdoor stop; the campus building inventory remains 272.
- Ground contact: 6,181 samples across 869 campus and neighboring buildings, zero missing samples and maximum numerical contact gap below 0.001 m.
- The earlier 26.10.16.2 layer comparison is retained in its versioned report. This follow-up changes the Suzzallo entrance and its Environment approach only; other building generators and source footprints are untouched.
- Navigation/loading regression checks cover grounded pivots, pointer-aligned mouse/touch pan and zoom, no inertia, selection safeguards, horizontal views and viewport resize/reset. Previous loading behavior and English defaults remain intact.
- Compressed HTTP, local classic-script and standalone payloads restore the exact source 3DS SHA-256. Browser parsing remains worker-based with bounded blocks.
- SEO checks cover the canonical domain, bilingual 272-building directory, assets, current model digest and offline edition. Release metadata follows calendar versioning.
- Actual local WebGL follow-up confirms the white triangular terrain exposures are gone and saves the new entrance view in `docs/previews/suzzallo_front.jpg`. The core preview retains the historical 1440 × 975 camera frame. Prior actual local WebGL review covers Suzzallo’s frontal entrance/terrace, brief pan/zoom, UW Station’s roof/entrances and the third fountain stop. A lightweight real-controller fixture verifies wide, Guide-only and wrapped action layouts; a mobile UW check verifies toolbar behavior. No browser errors/warnings were observed.
- Finder metadata is ignored and retained locally, and excluded from the delivery ZIP.

These checks validate deliverable integrity and interaction, not as-built survey accuracy. Exterior dimensions, grades and details are public-source approximations. Direct file:// navigation is unavailable in the browser test interface; local/offline loader paths and exact embedded bytes are checked independently.
