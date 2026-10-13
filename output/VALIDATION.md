# Delivery validation

- Rhino v7: meter units, 272 nonempty layers; 285 valid closed native building solids, 1627 closed meshes and 284 footprint curves.
- Independent Three.js 3DS import: 1627 named objects and 2,492,362 triangles; all names preserved and mapped to individual facilities or Environment.
- Representative navigation checks: 8 bearing/view/viewport combinations and 12 low-angle/level cases, including pan, cursor zoom, ground pivots, explicit rotation, no drift and drag/pinch selection safeguards.
- Offline loader checks: HTTP binary, local classic-script path, inline model, error handling and SHA-256 equality with the original 3DS.
- SEO checks: canonical/domain, crawlable bilingual directory, model digest, sharing metadata, local assets and self-contained edition.
- Browser checks: actual progress loading, English/Chinese content, selected landmark detail/highlight, exact Level view, district/overview/reset and a 390px mobile layout. The self-contained edition loaded and rendered through HTTP with no console errors.
- The browser automation policy disallows file:// navigation, so direct double-click browser execution was not tested. The local classic-script loader and unchanged model-byte paths passed independently.
- Preview exported from the actual interactive model; social image dimensions use the PNG’s real dimensions.

These checks validate deliverable integrity and navigation, not as-built survey accuracy. Exterior heights, roofs, facades and canopy forms are estimates.
