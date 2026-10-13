# Source notes

Snapshot: 13 October 2026.

| Dataset | Use | Limits |
| --- | --- | --- |
| [UW public building layer](https://gis.maps.uw.edu/federated/rest/services/BaseComponents/UW_Seattle_Buildings_and_Paths/MapServer/1) | Facility codes, names, footprint geometry, year built and gross floor area | Footprint reference, not measured exterior height or BIM; mapped current status can lag changes |
| [UW public data](https://gis.maps.uw.edu/federated/rest/services/PublicData/PublicData/MapServer) | Tree/bench positions and supplemental walk routes | Canopy forms, heights, path widths and furniture details are approximate |
| [OpenStreetMap](https://www.openstreetmap.org/copyright) | Campus boundary, roads, paths, paved squares, landscape, fields and water banks | Contributed map data, estimated widths where no width tag exists; ODbL attribution retained |
| [USGS 3DEP](https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer) | F32 bare-earth terrain in EPSG:32610 | About 10m sampling; flattened building pads; no survey certification |
| [UW Suzzallo history](https://lib.uw.edu/locations-hours/suzzallo-and-allen-libraries-history/) | Reading-room dimensions and exterior-form reference | Published 250 × 52 × 65 ft dimensions are interior, not whole-building extents |
| [Husky Stadium](https://gohuskies.com/sports/2013/7/2/208568068) | Bowl, opposing overhangs and open lake-facing exterior-form reference | Roof, stands and structural members are approximate; no certified stadium height |

The university already offers its own rendered campus map: https://map.uw.edu/?id=2099 . This project creates an independent layered metric model from public mapping; it does not extract or distribute that map's proprietary rendered assets.

The raw official footprint and public tree/bench files retain coordinates. The normalized OSM source includes data outside the rendered scope for boundary closure; the model clips it to the chosen campus/shore context. `retrieval_manifest.json` records source URLs and hashes. Original raw OSM extracts are compressed. Rebuilding uses saved data, not live APIs.
