"""Retrieve UW public GIS and OSM source snapshots. --refresh fetches new data."""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlencode
import json,concurrent.futures,hashlib,datetime,gzip,sys
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'sources';S.mkdir(exist_ok=True)
UW='https://gis.maps.uw.edu/federated/rest/services/';BBOX='-122.325,47.641,-122.285,47.665';refresh='--refresh' in sys.argv
manifest=[]
def record(file,url,raw,**extra):manifest.append({'file':file,'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),**extra})
def gis(path,filename,fields):
    target=S/filename;url=UW+path+'/query'
    if target.exists() and not refresh:
        raw=target.read_bytes();j=json.loads(raw);record(filename,url,raw,features=len(j['features']),retained_snapshot=True);print('Retained',filename,flush=True);return
    p={'where':'1=1','geometry':BBOX,'geometryType':'esriGeometryEnvelope','inSR':4326,'spatialRel':'esriSpatialRelIntersects'}
    ids=json.loads(urlopen(url+'?'+urlencode({**p,'f':'json','returnIdsOnly':'true'}),timeout=60).read()).get('objectIds',[]);features=[]
    for start in range(0,len(ids),200):
        q={'f':'geojson','objectIds':','.join(map(str,ids[start:start+200])),'outFields':fields,'outSR':4326,'returnGeometry':'true'}
        j=json.loads(urlopen(url+'?'+urlencode(q),timeout=60).read());assert not j.get('error'),j;features.extend(j.get('features',[]))
    raw=json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':')).encode();target.write_bytes(raw);record(filename,url,raw,parameters=p,fields=fields,features=len(features));print(filename,len(features),flush=True)
tasks=[('BaseComponents/UW_Seattle_Buildings_and_Paths/MapServer/1','uw_buildings.geojson','OBJECTID,FeatureStatus,FacNum,FacCode,FacName,Site,Address,Ownership,YearBuilt,GSF,BaseMap,Underground'),('BaseComponents/UW_Seattle_Buildings_and_Paths/MapServer/0','uw_linework.geojson','OBJECTID'),('PublicData/PublicData/MapServer/37','uw_trees.geojson','OBJECTID,TreeNumber,TreeType,SpeciesName,CommonName,DSH,Height'),('PublicData/PublicData/MapServer/36','uw_roads.geojson','OBJECTID,RouteType'),('PublicData/PublicData/MapServer/35','uw_walks.geojson','OBJECTID,RouteType'),('PublicData/Public_GroundsBench/MapServer/0','uw_benches.geojson','OBJECTID')]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(lambda t:gis(*t),tasks))
osm={'osm_map_west.xml.gz':'https://api.openstreetmap.org/api/0.6/map?bbox=-122.325,47.641,-122.307,47.665','osm_map_east.xml.gz':'https://api.openstreetmap.org/api/0.6/map?bbox=-122.307,47.641,-122.285,47.665','osm_map_water_2793848.xml.gz':'https://api.openstreetmap.org/api/0.6/relation/2793848/full','osm_map_water_2793830.xml.gz':'https://api.openstreetmap.org/api/0.6/relation/2793830/full'}
def fetch(file,url):
    p=S/file
    if p.exists() and not refresh:raw=p.read_bytes()
    else:
        raw=gzip.compress(urlopen(Request(url,headers={'User-Agent':'CampusGeometry/1.0'}),timeout=60).read(),mtime=0);p.write_bytes(raw)
    record(file,url,raw);print(file,len(raw),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(lambda item:fetch(*item),osm.items()))
(S/'retrieval_manifest.json').write_text(json.dumps(manifest,indent=2))
print('Source snapshots saved; run prepare_sources.py to normalize OSM geometry.')
