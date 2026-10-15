# U District and shoreline references

Accessed 14 October 2026. No reference photography or aerial imagery is redistributed.

## Mapped geometry

- Retained OpenStreetMap API snapshots (`osm_map_west.xml.gz`, normalized `osm_features.geojson`): mapped building outlines, available storeys/heights/material/roof tags, streets, footways, parking, reserves, wetland islands, shorelines, piers and bridge spans. Names from two mapped POIs are joined only to their containing outline: Neptune Theatre (node 31368542) and University Book Store (node 69520605).
- Seattle SDOT in-service trees: https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/SDOT_Trees_CDL/FeatureServer/0 . `neighborhood_tree_provenance.json` records the precise query, snapshot digest and feature count. Canopy shapes and sizes are illustrative, independent of zero/unavailable height fields.
- USGS terrain and the existing UW footprint/tree sources remain unchanged. UW footprint geometry takes priority at tiny contributed-outline overlaps; neighboring outlines are trimmed clear of official buildings and each other.
- Primary aerial review: https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=551220%2C5278430%2C551700%2C5279320&bboxSR=32610&imageSR=32610&size=900%2C1650&format=png&f=image . Observed the Ave/Brooklyn/Roosevelt street blocks, flat commercial roofs and tower/low-rise contrasts. Image date is not asserted; fine paint and obscured details are not fabricated from this overview. A closer hotel export returned an error, so no exact unverified pool placement is added.

## Principal neighborhood buildings

- University Inn, 4140 Roosevelt Way NE: https://www.staypineapple.com/university-inn-seattle-wa/gallery ; https://www.staypineapple.com/university-inn-seattle-wa . Official dusk exterior and pool photographs reviewed. The facade has three rows of guest-room windows over ground-level arrival/parking, large multi-pane groups, a warm rounded end, vertical University Inn sign, folded attached eaves and an arrival canopy. These observations guide the model; 13.65 m overall height and secondary member dimensions are approximate. The pool is confirmed by the operator, but its exact mapped placement is unresolved and is not invented.
- Neptune Building: https://web.seattle.gov/DPD/HistoricalSite/QueryResult.aspx?ID=5 ; https://www.seattle.gov/Documents/Departments/Neighborhoods/HistoricPreservation/Landmarks/RelatedDocuments/neptune-building-designation.pdf . Three storeys, two-tone masonry, paired upper windows and ground-floor storefronts; modeled vertical dimensions remain approximate.
- University Book Store: https://ubookstore.com/pages/about-us . Address and identity; mapped outline retained. Secondary facade bays and height are approximate.
- The Accolade: https://www.weberthompson.com/project/the-accolade/ ; https://www.weberthompson.com/thought/the-accolade-high-rise-housing-for-the-student-experience/ . Architect publishes 21 storeys and 240 ft (73.152 m). Footprint and secondary facade geometry remain mapped/approximate, respectively.
- The Standard: https://ankrommoisan.com/projects/the-standard-at-seattle-high-rises/ . Two high-rise towers, 25 storeys, plus a separate mid-rise; the model retains the mapped project outline. Metric envelope height is estimated.
- ōLiv: https://www.findorff.com/project/oliv-at-seattle/ . Contractor describes a 25-storey mixed-use student housing tower. Metric envelope height is estimated.
- Gateway Building: https://perkinswill.com/project/gateway-building/ ; https://www.gly.com/projects/university-district-station-building . 13-storey office tower above U District Station; metric envelope height estimated.
- U District station entrances: https://www.soundtransit.org/ride-with-us/stops-stations/u-district-station . Only above-ground mapped volumes are modeled, not the underground station.

## Streets and banks

- Seattle U District historic survey: https://www.seattle.gov/documents/departments/neighborhoods/historicpreservation/historicresourcessurvey/context-university-district.pdf . Context for the Ave commercial spine and north-campus residential blocks; not a current construction survey.
- SDOT 43rd Street improvements: https://www.seattle.gov/transportation/projects-and-programs/programs/pedestrian-program/ne-43rd-street-improvements . Pedestrian/transit link between Brooklyn Avenue and 15th Avenue.
- Mapped Union Bay Natural Area, Yesler Swamp, wetland islands, Montlake Cut and Portage Bay parks retain their source geometry. Marsh and bank materials fill formerly unclassified land. Closed quays and approximate elevated bridge profiles replace submerged bare-earth drapes. Bridge elevations, support positions, side rails, pavement widths, facade layouts and untagged roof geometry are illustrative, not engineering or survey measurements.

## Scope and visibility

Neighboring buildings have N-prefixed native layers and a separate Neighboring_Environment layer. Campus remains independently layered. Displayed neighboring names and the All checkbox carry the ⁺ prefix. The checkbox controls only this surrounding group; it does not move the camera or change campus counts. Ordinary buildings have attached openings/trim and bounded roof edges, without automatic rooftop boxes or arbitrary detached full-height rods.

## Vacant parcel and surface review

The mapped brownfield at way/223362698 immediately north of Russell Hall is the former University Temple site (1415 NE 43rd Street). The primary SEPA record identifies proposal 3034224-LU: https://apps.ecology.wa.gov/separ/Main/SEPA/Record.aspx?SEPANumber=202000048 . UW documents the 2021 demolition: https://www.washington.edu/news/2021/09/14/returning-to-the-u-district-recovering-from-the-pandemic-with-more-changes-ahead/ . The retained aerial overview visibly shows a pale, disturbed vacant slab/gravel parcel, not a finished tower. The model therefore adds a subdued site surface and mapped boundary fence, without presenting proposed towers as completed construction. The snapshot date does not certify current site status. Commercial/service paving, sidewalk strips and residential planted forecourts use mapped land-use categories; secondary landscape divisions remain approximate.

Artificial outer lake limits are rounded and shaded into the viewer background using an opaque material, while actual mapped banks remain unchanged. Only land extents receive the small landscape buffer; cropped water extents never generate a false land fringe. Ordinary paved/green skins exclude open lake water. Ground skins beneath open lake water are omitted to avoid projected fringe fragments. Water writes depth so submerged supports remain behind its surface. No transparent overlapping water sheets or navigation-dependent fade are used.

Mapped wetland and wooded-bank rings are completed with the non-water dry land inside their outer outlines. Actual water holes remain excluded. Dedicated shoreline ground/grass/wood materials share the artificial outer-edge fade, preventing empty island interiors and detached green outlines.
