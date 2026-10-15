"""Sample grade contacts from exported footprint metadata; no rendering dependency."""
from pathlib import Path
import json
from shapely.geometry import shape
root=Path(__file__).resolve().parents[1];samples=[]
files=['footprints_local_meters.geojson','neighboring_footprints.geojson']
features=[f for name in files for f in json.loads((root/'output'/name).read_text())['features']]
for f in features:
    p=shape(f['geometry']);props=f['properties'];z=props.get('ground_m',0)
    for part in [p]if p.geom_type=='Polygon'else p.geoms:
        q=part.buffer(-.15)
        if q.is_empty:q=part
        if q.geom_type!='Polygon':q=max(q.geoms,key=lambda g:g.area)
        pts=[q.representative_point()]+[q.exterior.interpolate(q.exterior.length*k/6)for k in range(6)]
        samples.extend({'code':props['code'],'name':props['name'],'position':[pt.x,pt.y,z]}for pt in pts)
(root/'output/ground_contact_samples.json').write_text(json.dumps(samples,separators=(',',':')))
