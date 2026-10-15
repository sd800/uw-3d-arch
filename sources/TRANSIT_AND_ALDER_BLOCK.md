# Transit surfaces and the Alder Hall block

Reviewed 15 October 2026. This revision models **surface architecture and public outdoor approaches**, not a surveyed station BIM, railway tunnels or underground platforms.

## Alder Hall / District Market

The street block is bounded by NE Campus Parkway, Brooklyn Avenue NE, University Way NE and NE 40th Street. The mapped Alder envelope and 618 m² open light court remain intact. A coordinated pavement domain replaces overlapping generic grass/path skins within the block. Tree pits follow published UW tree positions; crossing paint is restricted to retained mapped crossing nodes and clipped to roads. The model does not scatter generic zebra markings around the block.

- [UW HFS Alder Hall](https://hfs.uw.edu/live/undergraduates/undergraduate-communities/alder-hall/) supplies street/courtyard photographs and confirms the market and related amenities.
- [UW News: District Market opens in Alder Hall](https://www.washington.edu/news/2012/09/12/groceries-and-more-district-market-opens-in-alder-hall/) places District Market at the corner and describes the Campus Parkway café window. Its ground floor receives wrap-around glazing, attached signs and a separate service-door treatment.
- [UW NightRide stop descriptions](https://transportation.uw.edu/getting-around/shuttles/nightride) identify Alder's Bay 2 Metro stop in front of District Market. The retained OSM nodes `4340397017` and `4340397018` locate Bay 2 / stop 9575 and Bay 1 / stop 9580. [Sound Transit's Bay 2 page](https://www.soundtransit.org/ride-with-us/stops-stations/1_9575) corroborates stop 9575.
- [King County Metro transfer-environment work plan](https://aqua.kingcounty.gov/council/clerk/OldOrdsMotions/Motion%2014564.pdf) describes these as **custom UW shelters**, provided/maintained by the university or incorporated in buildings. The September 2025 street panoramas show two independent silver portal-frame shelters, not long canopies attached to Alder Hall. The model now separates those glazed shelters from the shallow building canopy and recessed arcade. It includes grounded supports, stop flags, seating and timetable-display forms. Route/service predictions are not modeled as a live feed.
- Esri World Imagery was inspected for roof/PV arrangement and street/yard layout. The inspected crop was centered at approximately −122.31388, 47.6553 using zoom-19 public imagery tiles. Imagery capture date is not individually certified. Only the observed Alder perimeter PV bands are expressed, with attached supports; arbitrary equipment boxes are not replicated over roofs.
- Five nearby low-rise university facilities retain their official outlines: SGS, ICT, IC2, DSC and EIC. [UW's building directory](https://www.washington.edu/students/reg/buildings.html) identifies the Community Design / University Way facilities, while [UW's ECC theatre page](https://depts.washington.edu/ecc/reservations/ecc-theatre/) identifies the theatre use. Roof form is interpreted from aerials; external heights and secondary facade partitions remain approximate.

## North frontage and Campus Parkway recheck

Two Google Street View panoramas were inspected interactively, both captured **September 2025**:

- [1303 NE Campus Parkway, looking south](https://www.google.com/maps/@?api=1&map_action=pano&pano=eQ-3H8m_P9QtxYhbbaJlwQ&heading=180): western Corten-clad lower facade, narrow lights, planted pockets and supported seating edges; independent glass bus shelter beside the main entry recess. Camera position approximately 47.6559825, -122.3140355.
- [1315 NE Campus Parkway, looking south](https://www.google.com/maps/@?api=1&map_action=pano&pano=7XvmFN0PZ18dn7vtSTBACQ&heading=180): recessed timber-clad cafe/market frontage, solid brick piers between the entrance zones, another separate Metro shelter, broad boarding pavement and concrete street slabs. Camera position approximately 47.6559776, -122.3136239. Views were also rotated along the street in both directions.
- [UW HFS: Outside entrance, District Market](https://www.flickr.com/photos/90311612@N05/9355693564/), photographed 7 September 2012: round concrete columns, recessed market glazing, timber lining, shallow projecting eaves, the round projecting market sign, doors and the east-side grade/railing relationship.
- [Project developer’s completed Alder Hall photographs](https://www.spectrumdevsolutions.com/projects/alder-hall/) and [UW HFS’s market entrance photograph](https://hfs.uw.edu/media/agpdhx3k/alder-district-market.jpg) corroborate the ground-floor materials and entry glazing. Reference images are inspected for geometry; their copyrighted pixels are not redistributed in the model.

The earlier interpretation of the Metro work-plan text as two long building-connected canopy runs was incorrect. A generic repeated storefront grid also obscured the distinctions between western classrooms, the main entry recess and the eastern commercial arcade. These have been replaced. The official north outline already contains the entry recess; an additional invented through-passage is removed. The two mapped stop nodes locate the flags; short shelters sit to their east as seen in the panoramas. Concrete pier diameters, storefront bay widths, planter outlines and the 9.4 m carriageway width are visual approximations, not surveyed dimensions. Original carriageway centerlines and the divided-street layout are retained.

The old HFS floor-plan PDF URL indexed in search returns 404 during this review. Its search snippet is not treated as a verified plan, and no floor heights or room assignments are derived from it. Current street imagery and the linked completed-project photographs control this revision.

## Satellite crosswalk review

[Google Maps satellite imagery](https://www.google.com/maps/@?api=1&map_action=map&center=47.65565,-122.31388&zoom=19&basemap=satellite) was inspected around all four corners and at higher magnification on Campus Parkway. The visible credits identify Airbus / Maxar / Google; the viewer does not certify an individual acquisition date. A georeferenced Esri World Imagery zoom-19 crop was also inspected with the mapped pedestrian crossing paths overlaid. The tile frame and review-image digest are retained in `alder_crosswalks.json`; imagery pixels are not redistributed.

The review retains 20 specific crossing paths: six at each of the two divided Campus Parkway intersections, and four at each NE 40th Street intersection. Each source way is linked in the JSON. Walking directions follow those paths, including angled curb approaches. The earlier node-coordinate heuristic, which omitted some crossings and rotated others incorrectly, is removed. Paired white stripes follow the satellite appearance, with visually estimated paint dimensions. Paint is clipped to the actual modeled roadway and excluded from footprints; central medians and sidewalks stay unpainted. Exported paint polygons and probe locations are retained for verification.

## University of Washington Station

[Sound Transit](https://www.soundtransit.org/ride-with-us/stops-stations/university-washington-station) identifies the station beside Husky Stadium. [LMN's completed-project page](https://lmnarchitects.com/project/university-of-washington-station-sound-transit), with Kevin Scott photography, documents the two-level glass/steel entry structure and its bicycle/pedestrian bridge. Reviewed images include the external north/south views, bridge approach, stairs and aerial `UW-Station_zz`.

The surface footprint is OSM way `325150399`, distinct from the official UW building inventory; it is appended as `LINK_UW` without renumbering the original 271 campus layers. Thin closed glass infills, actual supporting steel bays, intermediate floor, roof, ground doors and an elevator projection replace a generic solid building. The above-ground station is included in the campus display, beside the stadium.

The existing mapped bridge graph is retained: ways `369723298`, `370063488`, `524280882`, `524280883`, `524280884` and `570797482`. Deck polygons are unioned before construction, with shared junction elevations, a connected descending cycle ramp and supports reaching below grade. Mapped outdoor stair way `393899772` supplies its alignment and 55-tread count. Treads sit on a continuous inclined waist and meet the same upper deck datum. Bridge/member heights are estimated from exterior references and sampled grade, not engineering dimensions. Above-grade bridge routes are excluded from the generic ground-walk pass.

## U District Station

[LMN's project](https://lmnarchitects.com/project/u-district-station-sound-transit) and [opening report](https://lmnarchitects.com/lmn-architects-celebrates-the-opening-sound-transit-u-district) distinguish the two Brooklyn Avenue lobbies and describe black granite street cladding. Exterior imagery and the published surface-level plan were reviewed.

The south entrance preserves mapped way `746277336`, rebuilt with a low granite enclosure, tapered canopy, exposed supports and grounded entrance portal. The north entrance is retained at OSM node `10220232278`, integrated in the Gateway building's west podium instead of inventing a second freestanding headhouse. The existing neighboring building layers and codes are retained. Both approach hover areas carry the ⁺ neighboring prefix and disappear when neighboring areas are disabled.

## Geometry and limitations

All structural meshes are closed and metric. New station sign text consists of vector glyph solids on attached sign panels, with tiny contour features regularized to millimeters before CAD conversion. Glass is a schematic material; it is not a photorealistic survey of glazing. Member sizes, canopy spans, furniture positions between mapped stops, exterior elevations and roof partitions are photo-informed interpretations. Source geometry and these limitations are retained in `output/transit_refinement.json`, `output/alder_block_refinement.json` and the building records.
