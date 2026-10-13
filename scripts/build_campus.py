"""Seattle-campus exterior model with official footprints, trees and sampled terrain.
All heights and facade detail are approximate unless an explicit measurement is cited.
"""
from cad_core import *
from curation import GIS,MAP,LANDMARKS,GOTHIC,PITCHED,HEIGHTS,REFS,SHORT,chinese
from scipy.interpolate import RegularGridInterpolator
from shapely import segmentize,points
from shapely.strtree import STRtree
from PIL import Image
import re

def project(x,y,z=None):
    a,b=TF.transform(x,y);return np.asarray(a)-OX,np.asarray(b)-OY
def features(file):
    result=[]
    for f in json.loads((ROOT/'sources'/file).read_text())['features']:
        if not f.get('geometry'):continue
        q=transform(project,shape(f['geometry']))
        if not q.is_valid:q=q.buffer(0)
        if q.is_empty:continue
        result.append({'properties':f['properties'],'poly':q})
    return result
osm=features('osm_features.geojson')
campus_boundary=next(f['poly'] for f in osm if f['properties'].get('osm_id')=='relation/5268488')
limit=transform(project,box(-122.325,47.641,-122.285,47.665))
lakewater=unary_union([f['poly'] for f in osm if f['properties'].get('name') in ['Lake Washington','Portage Bay','Montlake Cut'] and f['properties'].get('natural')=='water'])
water_context=lakewater.intersection(box(-980,-1000,1700,1030))
raw=features('uw_buildings.geojson');grouped={};excluded=[]
for f in raw:
    t=f['properties'];id=t.get('FacCode') or str(t['OBJECTID'])
    if id in ['X08','X05'] or t.get('Underground')=='Yes' or t.get('FeatureStatus')=='Inactive' or f['poly'].area<2 or (t.get('Site') not in ['UWS','Seattle Main Campus','SEA_MN'] and not id.startswith('UWT')):
        excluded.append({'id':id,'name':t.get('FacName'),'reason':'Non-building pond or helipad' if id in ['X08','X05'] else 'Outside selected Seattle campus / underground-only / inactive / small unmapped exterior footprint'});continue
    grouped.setdefault(id,[]).append(f)
buildings=[]
for id,fs in grouped.items():
    p=unary_union([f['poly'] for f in fs]).buffer(0);t=fs[0]['properties'];c=p.centroid
    zone='east' if c.x>450 else ('south' if c.y<-440 else ('west' if c.x<-250 else 'central'))
    en=t.get('FacName') or 'Campus facility '+id
    if id=='STD':en='Husky Stadium'
    if id=='BRK':en='Burke Museum of Natural History and Culture'
    buildings.append({'id':id,'properties':t,'poly':p,'name':en,'name_zh':chinese(id,en),'zone':zone})
buildings.sort(key=lambda f:(['central','west','south','east'].index(f['zone']),-f['poly'].centroid.y,f['poly'].centroid.x))
footprints=unary_union([f['poly'] for f in buildings]);scope=unary_union([campus_boundary,water_context,*[f['poly'].buffer(18) for f in buildings]]).intersection(limit).buffer(5).simplify(.6).buffer(0)
meta=json.loads((ROOT/'sources/terrain_export_metadata.json').read_text());ex=meta['extent'];dem=np.asarray(Image.open(ROOT/'sources/terrain_dem.tif'),dtype=float)
assert dem.shape==(meta['height'],meta['width']) and np.isfinite(dem).all() and dem.min()>-10 and dem.max()<200
xs=np.linspace(ex['xmin'],ex['xmax'],dem.shape[1],endpoint=False)+(ex['xmax']-ex['xmin'])/dem.shape[1]/2-OX
ys=np.linspace(ex['ymin'],ex['ymax'],dem.shape[0],endpoint=False)+(ex['ymax']-ex['ymin'])/dem.shape[0]/2-OY
interpolate=RegularGridInterpolator((ys,xs),dem[::-1],bounds_error=False,fill_value=None)
def raw_ground(x,y):
    x,y=np.broadcast_arrays(x,y);return interpolate(np.column_stack([y.ravel(),x.ravel()])).reshape(x.shape)
for f in buildings:
    c=f['poly'].representative_point();f['ground']=float(raw_ground(c.x,c.y))
pad_tree=STRtree([f['poly'].buffer(.4) for f in buildings]);pad_z=np.array([f['ground'] for f in buildings])
def ground(x,y):
    x,y=np.broadcast_arrays(x,y);z=np.asarray(raw_ground(x,y));aa,bb=pad_tree.query(points(x.ravel(),y.ravel()),predicate='within');z.ravel()[aa]=pad_z[bb];return z
anchor=model.Settings.EarthAnchorPoint;anchor.EarthBasepointElevation=0;model.Settings.EarthAnchorPoint=anchor
obuildings=[f for f in osm if f['properties'].get('building')];otree=STRtree([f['poly'] for f in obuildings])
print('Preparing',len(buildings),'official building layers',flush=True)
for j,f in enumerate(buildings,1):
    id,p,t=f['id'],f['poly'],f['properties'];code=f'W{j:03d}';lay=code+'_'+f['name'];gothic=id in GOTHIC;pitched_roof=id in PITCHED;base=f['ground'];a,b,c,d=p.bounds;x,y=p.centroid.x,p.centroid.y
    candidates=otree.query(p);matches=[obuildings[k] for k in candidates if obuildings[k]['poly'].intersection(p).area>p.area*.45]
    ot=max(matches,key=lambda o:o['poly'].intersection(p).area)['properties'] if matches else {}
    residential=any(w in f['name'].lower() for w in ['apartments','court','hall']) and id in {'MCM','HNS','MCC','MDR','WLW','OAK','ELM','LAN','ALD','POP','MAH','TEH','CDRE','CDRW','CDA'} or id.startswith(('SC','MRC','NC'))
    # GSF is total reported floor area, not exterior floor count. This is only a
    # bounded fallback for approximate storeys, including possible basements.
    gross=float(t.get('GSF') or 0)*.092903
    levels=max(1,min(10,round(gross/max(p.area,1)))) if gross else 2
    if str(ot.get('building:levels','')).replace('.','',1).isdigit():levels=max(1,min(20,round(float(ot['building:levels']))))
    if id.startswith(('CY','GH','TL')) or p.area<60:levels=1
    height=HEIGHTS.get(id,max(3.2,levels*(3.05 if residential else 3.75)+.8)+(3.5 if pitched_roof else 0));source=GIS
    if id not in HEIGHTS and re.fullmatch(r'[0-9]+(?:\.[0-9]+)?',ot.get('height','')):
        height=max(3,min(110,float(ot['height'])));source='https://www.openstreetmap.org/'+ot['osm_id']
    height=min(height,110);mat='Brick' if gothic or pitched_roof or residential else ('Glass' if id in {'LSB','CSE2','HRC','PCAR','IEB','BIOE','GNOM','HSEB','NAN'} else 'Limestone')
    layer(lay,mat);ms={m:[] for m in COLORS};info={'FacilityCode':id,'NameEN':f['name'],'NameZH':f['name_zh'],'FootprintSource':GIS,'HeightStatus':'Estimated exterior','Units':'meters'}
    if id=='STD':
        # Bowl with two opposing cantilever-roof silhouettes, open toward the lake.
        inner=affinity.scale(p,xfact=.66,yfact=.55,origin=(x,y));rim=p.difference(inner)
        for q in polygons(rim):
            native_extrude(q,base,8,code+'_Bowl',lay,'Concrete',info);ms['Concrete'].append(extrusion(q,base,8))
        for k in range(14):
            outer=affinity.scale(p,xfact=.67+k*.019,yfact=.56+k*.027,origin=(x,y));inn=affinity.scale(p,xfact=.655+k*.019,yfact=.535+k*.027,origin=(x,y))
            for q in polygons(outer.difference(inn)):ms['Purple' if k%3 else 'Gold'].append(extrusion(q,base+8+k*1.35,.38))
        for sign in [-1,1]:
            roof=box(a+25,y+sign*(d-b)*.29-14,c-25,y+sign*(d-b)*.29+14).intersection(p)
            for q in polygons(roof):ms['Metal'].append(extrusion(q,base+height-3,1.3))
            for xx in np.arange(a+32,c-25,18):ms['Frame'].append(cylinder((xx,y+sign*(d-b)*.34,base+15),(xx,y+sign*(d-b)*.26,base+height-3),.5,6))
        # Field occupies the true inner footprint, with illustrative regulation markings.
        for q in polygons(inner):ms['Grass'].append(extrusion(q,base+.1,.12))
        for xx in np.linspace(x-47,x+47,11):ms['Marking'].append(boxmesh(xx,y,base+.25,.13,48,.035))
        ms['Purple'].append(boxmesh(x-54,y,base+.2,10,49,.07));ms['Purple'].append(boxmesh(x+54,y,base+.2,10,49,.07))
        levels=0
    else:
        bodyheight=height-(4.4 if pitched_roof else .8)
        if id in {'DEN','GRB'}:bodyheight=16.5 if id=='DEN' else 19
        for q in polygons(p):
            native_extrude(q,base,bodyheight,code+'_Volume',lay,mat,info);ms[mat].append(extrusion(q,base,bodyheight))
            for ring in [q.exterior,*q.interiors]:model.Objects.AddCurve(rh.PolylineCurve([rh.Point3d(xx,yy,base) for xx,yy in ring.coords]),attr(code+'_Footprint',lay,mat,info))
            for zz in [base+.5,base+bodyheight-.45]:
                band=q.buffer(.16,join_style=2).difference(q.buffer(-.10,join_style=2))
                for bb in polygons(band):ms['LightStone'].append(extrusion(bb,zz,.32))
            facade(ms,q,base,bodyheight,max(1,levels),gothic=gothic,continuous=mat=='Glass',spacing=4.5)
            if pitched_roof:
                # Roof wings follow clipped strips; courtyards remain open.
                width=min(c-a,d-b);axis='y' if d-b>c-a else 'x'
                if width>38:
                    for strip in [box(a-1,b-1,a+17,d+1),box(c-17,b-1,c+1,d+1),box(a+17,b-1,c-17,b+16),box(a+17,d-16,c-17,d+1)]:
                        for qq in polygons(q.intersection(strip)):ms['Slate'].extend(pitched(qq,base+bodyheight,4.2))
                    core=q.difference(unary_union([box(a-1,b-1,a+17,d+1),box(c-17,b-1,c+1,d+1),box(a+17,b-1,c-17,b+16),box(a+17,d-16,c-17,d+1)]))
                    for qq in polygons(core):ms['Metal'].append(extrusion(qq,base+bodyheight,.16))
                else:ms['Slate'].extend(pitched(q,base+bodyheight,4.2))
                if gothic:
                    for aa,bb in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
                        v=bb-aa;length=np.linalg.norm(v)
                        for dd in np.arange(2,length-1,7.5):
                            pp=aa+v*dd/length;ms['LightStone'].append(boxmesh(pp[0],pp[1],base,1.0,1.0,bodyheight+.6))
            else:
                ms['Metal'].append(extrusion(q,base+bodyheight,.22))
                parapet=q.buffer(-.15,join_style=2).difference(q.buffer(-.5,join_style=2))
                for pp in polygons(parapet):ms['Concrete'].append(extrusion(pp,base+bodyheight+.22,.48))
                if q.area>400:
                    plant=q.buffer(-5).intersection(box(x-6,y-4,x+6,y+4))
                    for pp in polygons(plant):ms['Metal'].append(extrusion(pp,base+bodyheight+.25,.6))
        if id in {'DEN','GRB'}:
            tower=box(x-4.8,y-4.8,x+4.8,y+4.8).intersection(p)
            for pp in polygons(tower):
                ms['Brick'].append(extrusion(pp,base+bodyheight,height-bodyheight-2));ms['Slate'].extend(pitched(pp,base+height-2,2));facade(ms,pp,base+bodyheight,height-bodyheight-2,2,True)
        if id=='OBS':
            dome=trimesh.creation.icosphere(subdivisions=2);dome.apply_scale([4.1,4.1,3.5]);dome.apply_translation([x,y,base+height-1.5]);ms['Metal'].append(dome)
        if id=='SUZ':
            # Reading-room west front: 250ft length, 65ft interior clear height
            # documented by UW; exterior height remains an estimate.
            for xx,yy in [(a+4,b+5),(a+4,d-5),(c-4,b+5),(c-4,d-5)]:ms['LightStone'].append(boxmesh(xx,yy,base+height-4,2.2,2.2,5.0))
    for k,(mm,parts) in enumerate(ms.items()):
        if parts:chunk_meshes(code+('D' if mm in ['Glass','DarkGlass','Frame'] else 'M')+f'{k:02d}',parts,mm,lay,info)
    r={'code':code,'facility_id':id,'name':f['name'],'name_zh':f['name_zh'],'official_name':t.get('FacName'),'short':SHORT.get(id,f['name']),'short_zh':f['name_zh'],'aliases_zh':[id,t.get('Address') or ''],'layer':lay,'zone':f['zone'],'landmark':id in LANDMARKS,'height':round(height,3),'height_status':'estimated','levels':levels,'year_built':t.get('YearBuilt'),'reported_gsf_ft2':t.get('GSF'),'area':round(p.area,2),'width':round(c-a,2),'depth':round(d-b,2),'center':[round(x,3),round(y,3)],'ground_m':round(base,3),'bottom_m':round(base,3),'peak_m':round(max((m.bounds[1,2] for parts in ms.values() for m in parts),default=base+height),3),'basis':'平面采用 UW 官方 GIS；外部层数、层高与屋顶高度为估算。GIS 总建筑面积不能视为地上层数。','basis_en':'Official UW footprint; exterior storeys, floor heights and roof elevations are approximate. Reported gross floor area may include basements and does not certify exterior storeys.','partition':'依据映射轮廓保留建筑范围、庭院与翼楼；屋顶、窗格、塔楼和立面构件为简化表达，未经过实测。','partition_en':'Mapped footprint with courtyard voids and wings; roofs, windows, towers and facade members are simplified public-source approximations, not surveyed detail.','source':source,'footprint_source':GIS,'architecture_reference':REFS.get(id),'construction_status':'Active'}
    if id=='SUZ':r['basis_en']+=' UW documents the reading room as 250 × 52 × 65 ft; these are interior dimensions, not the exterior building envelope.';r['basis']+=' 校方公布的阅览室为250×52×65英尺，属于室内尺寸，不能当作整栋建筑的外部尺寸。'
    records.append(r);f['record']=r
    if j%40==0:print('Buildings',j,flush=True)
print('Building geometry complete',len(records),flush=True)

# Terrain and mapped outdoor spaces, roads and paths; patching avoids large facets.
eg={k:[] for k in COLORS};counts={}
def env(g,z,hh,mat,drape=True):
    g=g.intersection(scope).buffer(0)
    for q in polygons(g):
        q=q.simplify(.10,preserve_topology=True);aa,bb,cc,dd=q.bounds
        for gx in np.arange(math.floor(aa/60)*60,cc,60):
            for gy in np.arange(math.floor(bb/60)*60,dd,60):
                for pp in polygons(q.intersection(box(gx,gy,gx+60,gy+60))):
                    pp=segmentize(pp,12);m=extrusion(pp,z,hh)
                    if drape:m.vertices[:,2]+=ground(m.vertices[:,0],m.vertices[:,1])
                    eg[mat].append(m)
roadfs=[f for f in osm if f['properties'].get('highway') in ['primary','secondary','tertiary','residential','service','unclassified','living_street'] and f['poly'].geom_type in ['LineString','MultiLineString'] and f['poly'].intersects(scope) and int(f['properties'].get('layer','0').split(';')[0])>=0]
roadparts=[];walkparts=[]
for f in roadfs:
    t=f['properties'];h=t['highway'];width={'primary':14,'secondary':11,'tertiary':9,'residential':7,'unclassified':7,'service':4.5,'living_street':5}[h]
    try:width=float(t.get('width',width))
    except ValueError:pass
    roadparts.append(f['poly'].buffer(width/2,cap_style=2,join_style=2))
roadarea=set_precision(unary_union(roadparts).difference(footprints).intersection(scope).buffer(0),.01)
for f in osm:
    t=f['properties'];g=f['poly'];h=t.get('highway')
    if h in ['footway','path','steps','cycleway','pedestrian'] and g.geom_type in ['LineString','MultiLineString'] and g.intersects(scope):
        if t.get('tunnel')=='yes' or t.get('layer')=='-1':continue
        width=3 if h in ['footway','steps'] else (4 if h=='cycleway' else 2)
        try:width=float(t.get('width',width))
        except ValueError:pass
        walkparts.append(g.buffer(width/2,cap_style=2,join_style=2))
# Supplement official walk routes only where OSM lacks the mapped corridor.
for f in features('uw_walks.geojson'):walkparts.append(f['poly'].buffer(1.35,cap_style=2,join_style=2))
walkarea=set_precision(unary_union(walkparts).difference(footprints).difference(roadarea).intersection(scope).buffer(0),.01)
# A neutral site base and campus lawn field; paved and wooded mappings overlay it.
env(scope,-3,3,'Ground');env(campus_boundary.difference(lakewater).difference(footprints).difference(roadarea).difference(walkarea),.10,.065,'Grass');env(roadarea,.03,.07,'Road');env(walkarea,.16,.055,'Walk')
red=next(f for f in osm if f['properties'].get('name')=='Red Square' and f['poly'].geom_type=='Polygon')
quad=next(f for f in osm if f['properties'].get('name')=='The Quad')
fountain=next(f for f in osm if f['properties'].get('name')=='Drumheller Fountain')
places=[]
place_names={'Red Square':'红场（中央广场）','The Quad':'The Quad（文科庭院）','Drumheller Fountain':'德拉姆赫勒喷泉','Rainier Vista':'雷尼尔山景观轴线','Union Bay':'联合湾','Portage Bay':'波蒂奇湾','Lake Washington':'华盛顿湖','Montlake Cut':'蒙特莱克水道'}
seen=set()
for f in osm:
    t=f['properties'];g=f['poly'];name=t.get('name');mat=None
    if g.geom_type not in ['Polygon','MultiPolygon'] or not g.intersects(scope) or t.get('building'):continue
    if name=='Red Square':mat='Tile'
    elif t.get('amenity')=='parking':mat='Road'
    elif t.get('natural')=='water' or t.get('water') or t.get('amenity')=='fountain':mat='Water'
    elif t.get('leisure')=='pitch':mat='Court' if t.get('sport') in ['tennis','basketball'] else 'Grass'
    elif t.get('leisure')=='track':mat='Track'
    elif t.get('highway')=='pedestrian':mat='Paving'
    elif t.get('landuse') in ['forest','grass','meadow','village_green'] or t.get('natural') in ['wood','scrub'] or t.get('leisure') in ['garden','park']:mat='Garden' if t.get('natural') in ['wood','scrub'] or t.get('leisure')=='garden' else 'Grass'
    if mat:
        q=set_precision(g.buffer(0),.01).difference(set_precision(footprints,.01)).difference(roadarea).buffer(0)
        if mat in ['Grass','Garden']:q=q.difference(walkarea)
        if mat=='Water' and name in ['Lake Washington','Portage Bay','Montlake Cut']:
            # Lake Union / Lake Washington are a regulated lake level, not a
            # sloped terrain skin; retain mapped banks and a flat water plane.
            env(q,5.0,.035,mat,False)
        else:env(q,.25 if mat in ['Tile','Paving','Water'] else .13,.035,mat)
    if name in place_names and name not in seen and g.area>100:
        c0=g.intersection(scope).centroid;places.append({'id':'P'+str(len(places)),'name':name,'name_zh':place_names[name],'position':[round(c0.x,2),round(c0.y,2),round(float(raw_ground(c0.x,c0.y))+1,2)]});seen.add(name)
for f in raw:
    if f['properties'].get('FacCode')=='X08':env(f['poly'],.26,.04,'Water')
    if f['properties'].get('FacCode')=='X05':env(f['poly'],.26,.04,'Paving')
# Paving grid and lawn cross in the Quad; Red Square's brick layout is legible.
rc=red['poly'].centroid
for gx in np.arange(red['poly'].bounds[0],red['poly'].bounds[2],8):env(LineString([(gx,red['poly'].bounds[1]),(gx,red['poly'].bounds[3])]).buffer(.045).intersection(red['poly']),.30,.018,'Paving')
fc=fountain['poly'].centroid;fr=math.sqrt(fountain['poly'].area/math.pi);base=float(raw_ground(fc.x,fc.y))
for q in polygons(fountain['poly'].buffer(.4).difference(fountain['poly'].buffer(-.3))):eg['LightStone'].append(extrusion(q,base+.1,.55))
for rad,num,h in [(0,1,6.5),(fr*.52,12,1.8)]:
    for angle in np.linspace(0,2*math.pi,num,endpoint=False):
        xx=fc.x+rad*math.cos(angle);yy=fc.y+rad*math.sin(angle);eg['Water'].append(cylinder((xx,yy,base+.4),(xx,yy,base+h),.10 if num>1 else .20,6))
# Trees use official positions; canopy shape and size are illustrative.
clearance=footprints.buffer(.65);trees=0;cherry=0
for f in features('uw_trees.geojson'):
    q=f['poly'];t=f['properties'];xx,yy=q.x,q.y
    if lakewater.contains(q):continue
    if not scope.contains(q) or clearance.contains(q):continue
    rng=np.random.default_rng(int(t['OBJECTID']));species=t.get('SpeciesName') or '';is_cherry='Prunus' in species and q.distance(quad['poly'])<16
    h=8+rng.uniform(-1,5);rad=2.8+rng.uniform(0,2);base=float(ground(xx,yy));conifer=t.get('TreeType')=='Conifer'
    eg['Trunk'].append(cylinder((xx,yy,base+.08),(xx,yy,base+h*.68),.18,5))
    if conifer:m=trimesh.creation.cone(radius=rad,height=h*.9,sections=9);m.apply_translation([xx,yy,base+h*.22])
    else:m=trimesh.creation.icosphere(subdivisions=1);m.apply_scale([rad,rad,h*.4]);m.apply_translation([xx,yy,base+h*.69])
    eg['Blossom' if is_cherry else 'Leaves'].append(m);trees+=1;cherry+=int(is_cherry)
for f in features('uw_benches.geojson'):
    q=f['poly']
    if not scope.contains(q) or clearance.contains(q):continue
    zz=float(ground(q.x,q.y));eg['Furniture'].append(boxmesh(q.x,q.y,zz+.4,1.7,.55,.12))
for k,(mat,parts) in enumerate(eg.items()):
    if parts:chunk_meshes(f'E{k:02d}',parts,mat,'Environment',{'Source':'UW public tree/bench positions, OSM outdoor surfaces and USGS ground samples','Approximation':'Widths, surface thickness, canopy shapes and furniture detail are illustrative','Units':'meters'})
print('Landscape complete:',trees,'trees;',cherry,'Quad cherry canopies',flush=True)
zone_shapes={z:unary_union([f['poly'] for f in buildings if f['zone']==z]).envelope.buffer(25) for z in ['central','west','south','east']}
for name,g in [('Campus',scope),*zone_shapes.items()]:
    aa,bb,cc,dd=g.bounds;xx=(aa+cc)/2;yy=(bb+dd)/2;size=max(cc-aa,dd-bb)*.7
    v=rh.ViewInfo();v.Name=name;v.Viewport.SetCameraLocation(rh.Point3d(xx+size,yy-size,1400));v.Viewport.SetCameraDirection(rh.Vector3d(-size,size,-1300));v.Viewport.SetCameraUp(rh.Vector3d(0,0,1));v.Viewport.TargetPoint=rh.Point3d(xx,yy,50);v.Viewport.ChangeToParallelProjection(True);v.Viewport.SetFrustum(-size,size,-size,size,1,40000);model.NamedViews.Add(v)
model.Strings['ModelNotes']='UW Seattle exterior approximation. Metric official footprint coordinates, sampled USGS 3DEP terrain, one layer per mapped facility and one Environment layer. Heights, roofs, facade bays and tree shapes are approximate. Not official university BIM or a measured as-built model.'
assert model.Write(str(OUT/'UW_Seattle_Layered.3dm'),7)
def chunk(tag,data=b''):return struct.pack('<HI',tag,len(data)+6)+data
def zs(s):return s.encode('ascii')+b'\0'
def rgb(c):return chunk(0x0011,bytes(c))
mb=b''
for name,co in COLORS.items():mb+=chunk(0xAFFF,chunk(0xA000,zs(name))+chunk(0xA010,rgb(tuple(int(v*.5) for v in co)))+chunk(0xA020,rgb(co))+chunk(0xA030,rgb((10,10,10))))
ob=b''
for o in objects:
    m=o['mesh'];v=np.asarray(m.vertices,dtype='<f4');ff=np.column_stack((m.faces,np.full(len(m.faces),7))).astype('<u2');fc0=struct.pack('<H',len(ff))+ff.tobytes()+chunk(0x4130,zs(o['mat'])+struct.pack('<H',len(ff))+np.arange(len(ff),dtype='<u2').tobytes())+chunk(0x4150,np.zeros(len(ff),dtype='<u4').tobytes());ob+=chunk(0x4000,zs(o['name'])+chunk(0x4100,chunk(0x4110,struct.pack('<H',len(v))+v.tobytes())+chunk(0x4120,fc0)))
(OUT/'UW_Seattle.3ds').write_bytes(chunk(0x4D4D,chunk(0x0002,struct.pack('<I',3))+chunk(0x3D3D,chunk(0x3D3E,struct.pack('<I',3))+chunk(0x0100,struct.pack('<f',1))+mb+ob)))
for name,data in [('layer_map',layer_map),('palette',COLORS),('buildings',records),('viewer_records',records),('places',places)]:
    (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2))
with (OUT/'building_dimensions_and_sources.csv').open('w',encoding='utf-8-sig',newline='') as fd:
    w=csv.DictWriter(fd,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
(OUT/'footprints_local_meters.geojson').write_text(json.dumps({'type':'FeatureCollection','coordinate_system':{'epsg':32610,'origin_easting':OX,'origin_northing':OY,'origin_wgs84':[LON,LAT],'unit':'m','note':'Local projected meters, not RFC7946 longitude/latitude'},'features':[{'type':'Feature','properties':f['record'],'geometry':mapping(f['poly'])} for f in buildings]},ensure_ascii=False,separators=(',',':')))
av=[];af=[];co=[];offset=0
for m,mat in meshdata:av.append(m.vertices);af.append(m.faces+offset);co.extend([COLORS[mat]]*len(m.faces));offset+=len(m.vertices)
np.savez_compressed(OUT/'preview_mesh_data.npz',vertices=np.vstack(av),faces=np.vstack(af),colors=np.asarray(co,dtype=np.uint8))
summary={'buildings':len(records),'layers':len(model.Layers),'environment_layer':'Environment','native_closed_solids':sum(isinstance(o.Geometry,rh.Extrusion) for o in model.Objects),'objects_3ds':len(objects),'vertices':offset,'triangles':sum(len(m.faces) for m,_ in meshdata),'trees':trees,'quad_cherry_trees':cherry,'landmarks':sum(r['landmark'] for r in records),'unit':'meters','crs':'EPSG:32610 local offsets','origin_wgs84':[LON,LAT],'origin_utm':[OX,OY],'local_z_zero_m':0,'bounds':scope.bounds,'district_bounds':{z:list(g.bounds) for z,g in zone_shapes.items()},'overview_center':[round(rc.x,4),round(rc.y,4)],'terrain':'USGS 3DEP F32 bare-earth DEM sampled at about 10m; landscape patches 60m with 12m edge segmentation and flattened building pads','terrain_source':'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer','sectors':{z:sum(r['zone']==z for r in records) for z in zone_shapes},'accuracy':'Official mapped footprint/tree positions; all exterior heights, roof/facade geometry and tree forms approximate, not surveyed.'}
summary['native_closed_solids']=sum(isinstance(o.Geometry,rh.Extrusion) for o in model.Objects)
(OUT/'model_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(OUT/'excluded_records.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2));print(json.dumps(summary,indent=2),flush=True)
