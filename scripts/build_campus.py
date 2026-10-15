"""Seattle-campus exterior model with official footprints, trees and sampled terrain.
All heights and facade detail are approximate unless an explicit measurement is cited.
"""
from cad_core import *
from transit_architecture import build_uw_station,station_landscape,write_transit_report,BRIDGE_IDS
from alder_block import BLOCK,detail_block,block_building
from husky_stadium import build_husky_stadium
from core_landscape import detail_core,core_plan
from core_architecture import oriented_roofs,core_accents
from architecture_refinement import build_refined,write_report
from neighboring_areas import build_neighbors
from campus_detail import build_ordinary,write_ordinary_report
from shore_detail import detail_shores
from alder_hall import courtyard_from_osm,detail_alder_court,detail_alder_precinct
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
water_frame=[-1090,-1120,1810,1140,160,120]
water_clip=box(*water_frame[:4]).buffer(-water_frame[4],join_style=1).buffer(water_frame[4],quad_segs=24)
water_context=lakewater.intersection(water_clip)
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
    if id=='ALD':p=p.difference(courtyard_from_osm(osm,p)).buffer(0)
    en=t.get('FacName') or 'Campus facility '+id
    if id=='STD':en='Husky Stadium'
    if id=='BRK':en='Burke Museum of Natural History and Culture'
    buildings.append({'id':id,'properties':t,'poly':p,'name':en,'name_zh':chinese(id,en),'zone':zone})
buildings.sort(key=lambda f:(['central','west','south','east'].index(f['zone']),-f['poly'].centroid.y,f['poly'].centroid.x))
# Sound Transit station is outside the UW building inventory. Append its mapped
# surface envelope without renumbering any existing campus building layer.
station_osm=next(f for f in osm if f['properties'].get('osm_id')=='way/325150399')
buildings.append({'id':'LINK_UW','properties':{'FacCode':'LINK_UW','FacName':'University of Washington Station','YearBuilt':2016,'Address':'3720 Montlake Boulevard NE'},'poly':station_osm['poly'],'name':'University of Washington Station','name_zh':'华盛顿大学轻轨站','zone':'east','footprint_source':'https://www.openstreetmap.org/way/325150399'})
footprints=unary_union([f['poly'] for f in buildings]);land_scope=unary_union([campus_boundary,*[f['poly'].buffer(18) for f in buildings]]).intersection(limit).buffer(5).simplify(.6).buffer(0)
# Buffer the land only: buffering cropped water invents a thin land fringe
# around the artificial lake border and produces the pointed edge fragments.
scope=unary_union([land_scope,water_context.intersection(limit)]).buffer(0)
shore_limit=water_clip
shore_parts=[f['poly']for f in osm if f['poly'].geom_type in ['Polygon','MultiPolygon']and(f['properties'].get('leisure')=='nature_reserve'or f['properties'].get('natural')=='wetland'or f['properties'].get('leisure')=='park'and f['poly'].distance(lakewater)<30 or f['properties'].get('natural')=='wood'and f['poly'].distance(lakewater)<30)]
# Wetland/wood polygons often describe a ring around dry island interiors.
# Fill only mapped non-water land inside those outlines, never actual lake holes.
shore_green=unary_union([Polygon(q.exterior)for g in shore_parts for q in polygons(g)]).intersection(shore_limit).difference(lakewater)
scope=unary_union([scope,footprints.buffer(2),shore_green]).buffer(0)
meta=json.loads((ROOT/'sources/terrain_export_metadata.json').read_text());ex=meta['extent'];dem=np.asarray(Image.open(ROOT/'sources/terrain_dem.tif'),dtype=float)
assert dem.shape==(meta['height'],meta['width']) and np.isfinite(dem).all() and dem.min()>-10 and dem.max()<200
xs=np.linspace(ex['xmin'],ex['xmax'],dem.shape[1],endpoint=False)+(ex['xmax']-ex['xmin'])/dem.shape[1]/2-OX
ys=np.linspace(ex['ymin'],ex['ymax'],dem.shape[0],endpoint=False)+(ex['ymax']-ex['ymin'])/dem.shape[0]/2-OY
interpolate=RegularGridInterpolator((ys,xs),dem[::-1],bounds_error=False,fill_value=None)
def raw_ground(x,y):
    x,y=np.broadcast_arrays(x,y);return interpolate(np.column_stack([y.ravel(),x.ravel()])).reshape(x.shape)
for f in buildings:
    c=f['poly'].representative_point();f['ground']=float(raw_ground(c.x,c.y))
# Joined/overlapping mapped wings share one visualization grade. Otherwise two
# pads can project into each other and bury the adjacent building base.
contact_tree=STRtree([f['poly']for f in buildings]);parent=list(range(len(buildings)))
def contact_root(k):
    while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
    return k
for i,f in enumerate(buildings):
    for j in contact_tree.query(f['poly']):
        if j>i and f['poly'].intersection(buildings[j]['poly']).area>.025:parent[contact_root(j)]=contact_root(i)
contact_groups={}
for i,f in enumerate(buildings):contact_groups.setdefault(contact_root(i),[]).append(f)
for group in contact_groups.values():
    if len(group)>1:
        grade=sum(f['ground']*f['poly'].area for f in group)/sum(f['poly'].area for f in group)
        for f in group:f['ground']=grade
pad_tree=STRtree([f['poly'].buffer(.4) for f in buildings]);pad_z=np.array([f['ground'] for f in buildings])
alder_site=next(f for f in buildings if f['id']=='ALD');alder_envelope=Polygon(alder_site['poly'].exterior);alder_grade=alder_site['ground'];alder_bounds=alder_envelope.buffer(2.4).bounds
def ground(x,y):
    x,y=np.broadcast_arrays(x,y);z=np.asarray(raw_ground(x,y));aa,bb=pad_tree.query(points(x.ravel(),y.ravel()),predicate='within');z.ravel()[aa]=pad_z[bb]
    # A narrow, graded entry apron connects the flat hall and court to sampled
    # street terrain; no vertical air slot at the doorway or sidewalk edge.
    ax,ay,bx,by=alder_bounds;xx=x.ravel();yy=y.ravel();zz=z.ravel()
    ids=np.flatnonzero((xx>=ax)&(xx<=bx)&(yy>=ay)&(yy<=by))
    for k in ids:
        pt=Point(xx[k],yy[k]);distance=alder_envelope.distance(pt)
        if distance<2.4:
            blend=np.clip(distance/2.4,0,1);blend=blend*blend*(3-2*blend);zz[k]=alder_grade+(zz[k]-alder_grade)*blend
    return z
anchor=model.Settings.EarthAnchorPoint;anchor.EarthBasepointElevation=0;model.Settings.EarthAnchorPoint=anchor
obuildings=[f for f in osm if f['properties'].get('building')];otree=STRtree([f['poly'] for f in obuildings])
print('Preparing',len(buildings),'campus building/transit layers',flush=True)
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
    if id=='SUZ':mat='Limestone';levels=3
    if id in {'KNE','OUG','MNY','HUB'}:mat='Brick'
    layer(lay,mat);ms={m:[] for m in COLORS};info={'FacilityCode':id,'NameEN':f['name'],'NameZH':f['name_zh'],'FootprintSource':f.get('footprint_source',GIS),'HeightStatus':'Estimated exterior','Units':'meters'}
    # Closed below-grade support joins simplified terrain to the actual building pad.
    for q in polygons(segmentize(p,5)):
        support=extrusion(q,base-1.5,1.51);bottom=support.vertices[:,2]<base-.7
        support.vertices[bottom,2]=np.minimum(base-.2,raw_ground(support.vertices[bottom,0],support.vertices[bottom,1])-1.5)
        ms['Foundation'].append(support)
    refinement=build_uw_station(ms,p,base,code,lay,info,raw_ground)if id=='LINK_UW'else block_building(ms,p,base,id,code,lay,info,raw_ground)if id in {'SGS','ICT','IC2','DSC','EIC'}else build_refined(ms,p,base,id,height,levels,code,lay,info,raw_ground)
    if not refinement and id!='STD':refinement=build_ordinary(ms,p,base,id,height,levels,code,lay,info,raw_ground,ot,f['name'])
    if refinement:
        height=refinement['height_m'];levels=refinement['levels']
    elif id=='STD':
        field=next(o['poly'] for o in osm if o['properties'].get('osm_id')=='way/235758229')
        build_husky_stadium(ms,p,field,base,code,lay,info)
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
                oriented_roofs(ms,q,base+bodyheight,4.2)
                if gothic:
                    for aa,bb in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
                        v=bb-aa;length=np.linalg.norm(v)
                        for dd in np.arange(2,length-1,7.5):
                            pp=aa+v*dd/length;ms['LightStone'].append(boxmesh(pp[0],pp[1],base,1.0,1.0,bodyheight+.6))
            else:
                ms['Metal'].append(extrusion(q,base+bodyheight,.22))
                parapet=q.buffer(-.15,join_style=2).difference(q.buffer(-.5,join_style=2))
                for pp in polygons(parapet):ms['Concrete'].append(extrusion(pp,base+bodyheight+.22,.48))
                # Unverified automatic rooftop equipment boxes are omitted.
        if id in {'DEN','GRB'}:
            tower=box(x-4.8,y-4.8,x+4.8,y+4.8).intersection(p)
            for pp in polygons(tower):
                ms['Brick'].append(extrusion(pp,base+bodyheight,height-bodyheight-2));ms['Slate'].extend(pitched(pp,base+height-2,2));facade(ms,pp,base+bodyheight,height-bodyheight-2,2,True)
        if id=='OBS':
            dome=trimesh.creation.icosphere(subdivisions=2);dome.apply_scale([4.1,4.1,3.5]);dome.apply_translation([x,y,base+height-1.5]);ms['Metal'].append(dome)
        core_accents(ms,p,base,bodyheight,height,id,(-14.3477,16.419))
    for k,(mm,parts) in enumerate(ms.items()):
        if parts:chunk_meshes(code+('D' if mm in ['Glass','DarkGlass','Frame'] else 'M')+f'{k:02d}',parts,mm,lay,info)
    r={'code':code,'facility_id':id,'name':f['name'],'name_zh':f['name_zh'],'official_name':t.get('FacName'),'short':SHORT.get(id,f['name']),'short_zh':f['name_zh'],'aliases_zh':[id,t.get('Address') or ''],'layer':lay,'zone':f['zone'],'landmark':id in LANDMARKS,'height':round(height,3),'height_status':'estimated','levels':levels,'year_built':t.get('YearBuilt'),'reported_gsf_ft2':t.get('GSF'),'area':round(p.area,2),'width':round(c-a,2),'depth':round(d-b,2),'center':[round(x,3),round(y,3)],'ground_m':round(base,3),'bottom_m':round(base,3),'peak_m':round(max((m.bounds[1,2] for parts in ms.values() for m in parts),default=base+height),3),'basis':'平面采用 UW 官方 GIS；外部层数、层高与屋顶高度为估算。GIS 总建筑面积不能视为地上层数。','basis_en':'Official UW footprint; exterior storeys, floor heights and roof elevations are approximate. Reported gross floor area may include basements and does not certify exterior storeys.','partition':'依据映射轮廓保留建筑范围、庭院与翼楼；屋顶、窗格、塔楼和立面构件为简化表达，未经过实测。','partition_en':'Mapped footprint with courtyard voids and wings; roofs, windows, towers and facade members are simplified public-source approximations, not surveyed detail.','source':source,'footprint_source':GIS,'architecture_reference':REFS.get(id),'construction_status':'Active'}
    if refinement:
        r['partition_en']='; '.join(refinement['details'])+'. Exterior dimensions and partitions remain approximate.'
        r['partition']='按公开建筑资料和航拍细化体量、屋顶与立面；保留官方轮廓。外部高度及构件尺寸仍为近似表达。'
        r['volume_parts']=refinement['volume_parts']
        if refinement.get('ordinary'):r['partition']='保留公开映射轮廓和庭院，按建筑用途及已有标记细化窗格、楼层线脚、屋顶与接地入口；外部高度与构件尺寸为近似表达。'
    if id=='STD':
        r['partition']='沿公开球场轮廓的长轴重建下层环形看台、南北上层看台及两片悬挑屋顶；球场按120码×53⅓码表达。看台排数、立面、屋顶标高与支撑结构为简化估算。'
        r['partition_en']='Mapped field axis with stepped lower bowl, north/south upper decks and two cantilever roofs. A 120 by 53 1/3 yard field is shown; row count, exterior elevations, roof heights and supports are illustrative estimates.'
        r['architecture_reference']='https://www.hok.com/projects/view/university-of-washington-husky-stadium-renovation-and-expansion/'
    if id=='ALD':r['basis_en']+=' The missing light-court inner ring is mapped in OpenStreetMap relation 6447992 and corroborated by UW HFS courtyard photos.';r['partition']='依据公开内环轮廓恢复露天天井，细化六层灰砖宿舍楼、浅色内庭立面、成对窗格、底层入口和天井铺装种植；构件尺寸及景观位置为近似表达。'
    if id=='SUZ':r['basis_en']+=' UW documents the reading room as 250 × 52 × 65 ft; these are interior dimensions, not the exterior building envelope.';r['basis']+=' 校方公布的阅览室为250×52×65英尺，属于室内尺寸，不能当作整栋建筑的外部尺寸。'
    if id=='LINK_UW':
        r.update(footprint_source=f['footprint_source'],source='https://lmnarchitects.com/project/university-of-washington-station-sound-transit',architecture_reference='https://lmnarchitects.com/project/university-of-washington-station-sound-transit',basis_en='Mapped OSM surface envelope. Two-level exterior, structural bays and dimensions interpreted from the architect’s photographs; not underground engineering or a surveyed station model.',basis='地面站房范围采用公开映射轮廓；两层玻璃站房及构件依据设计方照片近似表达，不包含地下铁路工程。',partition='两层玻璃站房、钢柱与楼板、入口、电梯突出部分和轻薄金属屋顶；与映射人行桥和室外楼梯连接。')
    if id=='ALD':r['aliases_zh']+=['District Market','Husky Grind','Bay 1','Bay 2','bus stop','公交站','街区'];r['partition_en']+=' Building-integrated bus canopies, market glazing, connected whole-block paving and aerial-visible PV bands.'
    records.append(r);f['record']=r
    if j%40==0:print('Buildings',j,flush=True)
write_report();write_ordinary_report()
print('Building geometry complete',len(records),flush=True)

# Terrain and mapped outdoor spaces, roads and paths; patching avoids large facets.
eg={k:[] for k in COLORS};counts={}
def env(g,z,hh,mat,drape=True):
    g=g.intersection(scope).buffer(0)
    if drape and mat in ['Ground','Grass','Garden','Road','Walk','Paving','Tile','Marking','Court','Track']:g=g.difference(lakewater).buffer(0)
    for q in polygons(g):
        if q.area<10 and q.distance(water_clip.boundary)<5 and mat!='Ground':continue
        q=q if mat=='Ground'else q.simplify(.10,preserve_topology=True);aa,bb,cc,dd=q.bounds
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
bridge_mask=unary_union([f['poly'].buffer(7,cap_style=2,join_style=2)for f in osm if f['properties'].get('bridge')in ['yes','movable','viaduct']and f['properties'].get('highway')in ['primary','secondary','tertiary']and f['poly'].intersects(lakewater.buffer(25))])
roadarea=set_precision(unary_union(roadparts).difference(bridge_mask).difference(footprints).intersection(scope).buffer(0),.01)
for f in osm:
    t=f['properties'];g=f['poly'];h=t.get('highway')
    if h in ['footway','path','steps','cycleway','pedestrian'] and g.geom_type in ['LineString','MultiLineString'] and g.intersects(scope):
        if t.get('tunnel')=='yes' or t.get('layer')=='-1' or t.get('osm_id')in BRIDGE_IDS or t.get('bridge')=='yes'and t.get('highway')=='steps'and g.distance(station_osm['poly'])<100:continue
        width=3 if h in ['footway','steps'] else (4 if h=='cycleway' else 2)
        try:width=float(t.get('width',width))
        except ValueError:pass
        walkparts.append(g.buffer(width/2,cap_style=2,join_style=2))
# Supplement official walk routes only where OSM lacks the mapped corridor.
for f in features('uw_walks.geojson'):walkparts.append(f['poly'].buffer(1.35,cap_style=2,join_style=2))
walkarea=set_precision(unary_union(walkparts).difference(footprints).difference(roadarea).intersection(scope).buffer(0),.01)
red=next(f for f in osm if f['properties'].get('name')=='Red Square' and f['poly'].geom_type=='Polygon')
quad=next(f for f in osm if f['properties'].get('name')=='The Quad')
fountain=next(f for f in osm if f['properties'].get('name')=='Drumheller Fountain')
core_layout=core_plan(red['poly'],quad['poly'],osm,footprints)
core_mask=unary_union([red['poly'],quad['poly'],fountain['poly'].buffer(3.8),core_layout[0],BLOCK])
# Dedicated core surfaces replace generic overlapping lawn and path skins.
alder=next(f for f in buildings if f['id']=='ALD');alder_court=courtyard_from_osm(osm,Polygon(alder['poly'].exterior))
alder_apron=alder_envelope.buffer(2.4,join_style=2).difference(alder_envelope).difference(footprints).difference(roadarea)
env(land_scope.difference(footprints).difference(lakewater).difference(alder_court).difference(alder_apron),-3,3,'Ground')
env(alder_apron,-3,3,'Ground')
env(alder_court,alder['ground']-.18,.18,'Ground',False)
env(shore_green.difference(land_scope).difference(footprints),-3,3,'ShoreGround')
env(shore_green.difference(footprints),.10,.045,'ShoreGrass')
for f in buildings:env(f['poly'],f['ground']-.18,.18,'Ground',False)
env(campus_boundary.difference(lakewater).difference(footprints).difference(roadarea).difference(walkarea).difference(core_mask),.10,.065,'Grass');env(roadarea,.03,.07,'Road');env(walkarea.difference(core_mask),.16,.055,'Walk')
places=[]
place_names={'Red Square':'红场','The Quad':'The Quad 庭院','Drumheller Fountain':'德拉姆赫勒喷泉','Rainier Vista':'雷尼尔山景观轴线','Union Bay':'联合湾','Portage Bay':'波蒂奇湾','Lake Washington':'华盛顿湖','Montlake Cut':'蒙特莱克水道'}
seen=set()
for f in osm:
    t=f['properties'];g=f['poly'];name=t.get('name');mat=None
    if g.geom_type not in ['Polygon','MultiPolygon'] or not g.intersects(scope) or t.get('building'):continue
    if name=='Red Square':mat='Tile'
    elif t.get('amenity')=='parking':mat='Road'
    elif t.get('natural')=='water' or t.get('water') or t.get('amenity')=='fountain':mat='Water'
    elif t.get('leisure')=='pitch':mat='Court' if t.get('sport') in ['tennis','basketball'] else 'Grass'
    elif t.get('natural')=='wetland':mat='Wetland'
    elif t.get('natural')in ['beach','sand']:mat='ShoreSand'
    elif t.get('leisure')=='track':mat='Track'
    elif t.get('highway')=='pedestrian':mat='Paving'
    elif t.get('landuse') in ['forest','grass','meadow','village_green'] or t.get('natural') in ['wood','scrub'] or t.get('leisure') in ['garden','park']:mat='Garden' if t.get('natural') in ['wood','scrub'] or t.get('leisure')=='garden' else 'Grass'
    if mat in ['Grass','Garden']and g.distance(lakewater)<30:mat='ShoreWood'if mat=='Garden'else 'ShoreGrass'
    if mat:
        q=set_precision(g.buffer(0),.01).difference(set_precision(footprints,.01)).difference(roadarea).difference(core_mask).buffer(0)
        if mat in ['Grass','Garden','ShoreGrass','ShoreWood']:q=q.difference(walkarea)
        if mat=='Water':q=q.difference(unary_union([o['poly']for o in osm if o['properties'].get('natural')=='wetland'and o['poly'].geom_type in ['Polygon','MultiPolygon']]))
        if mat=='Water' and name in ['Lake Washington','Portage Bay','Montlake Cut']:
            # Lake Union / Lake Washington are a regulated lake level, not a
            # sloped terrain skin; retain mapped banks and a flat water plane.
            env(q.intersection(water_clip),5.0,.035,mat,False)
        else:env(q,.25 if mat in ['Tile','Paving','Water'] else .13,.035,mat)
    if name in place_names and name not in seen and g.area>100:
        c0=g.intersection(scope).centroid;places.append({'id':'P'+str(len(places)),'name':name,'name_zh':place_names[name],'position':[round(c0.x,2),round(c0.y,2),round(float(raw_ground(c0.x,c0.y))+1,2)]});seen.add(name)
from parking_detail import parking_detail
parking_green=unary_union([f['poly']for f in osm if f['poly'].geom_type in ['Polygon','MultiPolygon']and((f['properties'].get('landuse')in ['forest','grass','meadow','village_green'])or f['properties'].get('natural')in ['wood','scrub']or f['properties'].get('leisure')=='garden')])
parking_paint=parking_detail(ROOT,scope,footprints,parking_green)
env(parking_paint,.19,.014,'Marking')
for f in raw:
    if f['properties'].get('FacCode')=='X08':env(f['poly'].difference(core_mask),.26,.04,'Water')
    if f['properties'].get('FacCode')=='X05':env(f['poly'],.26,.04,'Paving')
rc=red['poly'].centroid
detail_core(eg,env,red['poly'],quad['poly'],fountain['poly'],ground,footprints,core_layout)
detail_shores(eg,env,osm,scope,footprints,lakewater,ground)
station_landscape(eg,env,osm,next(f for f in buildings if f['id']=='LINK_UW'),ground,footprints,places)
# Trees use official positions; canopy shape and size are illustrative.
clearance=footprints.buffer(.65);trees=0;cherry=0
for f in features('uw_trees.geojson'):
    q=f['poly'];t=f['properties'];xx,yy=q.x,q.y
    if lakewater.contains(q):continue
    if not scope.contains(q) or clearance.contains(q):continue
    rng=np.random.default_rng(int(t['OBJECTID']));species=t.get('SpeciesName') or '';is_cherry='yedoensis' in species and q.distance(quad['poly'])<1
    h=8+rng.uniform(-1,5);rad=2.8+rng.uniform(0,2);base=float(ground(xx,yy));conifer=t.get('TreeType')=='Conifer'
    eg['Trunk'].append(cylinder((xx,yy,base+.08),(xx,yy,base+h*.68),.18,5))
    if conifer:m=trimesh.creation.cone(radius=rad,height=h*.9,sections=9);m.apply_translation([xx,yy,base+h*.22])
    else:m=trimesh.creation.icosphere(subdivisions=1);m.apply_scale([rad,rad,h*.4]);m.apply_translation([xx,yy,base+h*.69])
    eg['Blossom' if is_cherry else 'Leaves'].append(m);trees+=1;cherry+=int(is_cherry)
for f in features('uw_benches.geojson'):
    q=f['poly']
    if not scope.contains(q) or clearance.contains(q):continue
    zz=float(ground(q.x,q.y));eg['Furniture'].append(boxmesh(q.x,q.y,zz+.4,1.7,.55,.12))
    if q.distance(alder_envelope)<25:
        # Keep the published bench position; add its previously missing support.
        for dx in [-.58,.58]:
            for dy in [-.18,.18]:eg['Furniture'].append(cylinder((q.x+dx,q.y+dy,zz-.04),(q.x+dx,q.y+dy,zz+.42),.035,5))
        for dz in [.72,.90]:eg['Cedar'].append(boxmesh(q.x,q.y+.23,zz+dz,1.70,.06,.11))
        for dx in [-.70,.70]:eg['Furniture'].append(cylinder((q.x+dx,q.y+.23,zz+.40),(q.x+dx,q.y+.23,zz+1.0),.035,5))
alder_details=detail_alder_court(eg,alder_court,alder['ground']);alder_details['surroundings']={'replaced_by':'alder_block_refinement.json'}
detail_block(eg,env,osm,alder_envelope,footprints,roadarea,walkarea,features('uw_trees.geojson'),ground,places)
(OUT/'alder_hall_refinement.json').write_text(json.dumps(alder_details,indent=2))
for k,(mat,parts) in enumerate(eg.items()):
    if parts:chunk_meshes(f'E{k:02d}',parts,mat,'Environment',{'Source':'UW public tree/bench positions, OSM outdoor surfaces and USGS ground samples','Approximation':'Widths, surface thickness, canopy shapes and furniture detail are illustrative','Units':'meters'})
print('Landscape complete:',trees,'trees;',cherry,'Quad cherry canopies',flush=True)
neighbors=build_neighbors(osm,scope,footprints,raw_ground,ground,features('uw_trees.geojson'))
places.extend(neighbors.get('transit_places',[]));write_transit_report()
zone_shapes={z:unary_union([f['poly'] for f in buildings if f['zone']==z]).envelope.buffer(25) for z in ['central','west','south','east']}
for name,g in [('Campus',scope),*zone_shapes.items()]:
    aa,bb,cc,dd=g.bounds;xx=(aa+cc)/2;yy=(bb+dd)/2;size=max(cc-aa,dd-bb)*.7
    v=rh.ViewInfo();v.Name=name;v.Viewport.SetCameraLocation(rh.Point3d(xx+size,yy-size,1400));v.Viewport.SetCameraDirection(rh.Vector3d(-size,size,-1300));v.Viewport.SetCameraUp(rh.Vector3d(0,0,1));v.Viewport.TargetPoint=rh.Point3d(xx,yy,50);v.Viewport.ChangeToParallelProjection(True);v.Viewport.SetFrustum(-size,size,-size,size,1,40000);model.NamedViews.Add(v)
model.Strings['ModelNotes']='UW Seattle exterior approximation. Official UW building footprints, mapped Sound Transit surface station and OSM neighboring/transit geometry, sampled USGS terrain. Individual campus/neighbor building layers and separate environment layers. Alder block, surface station entries and bridge/stairs interpreted from university/operator/architect sources; exterior heights and member dimensions approximate. No underground railway engineering or measured as-built BIM.'
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
assert (OUT/'UW_Seattle.3ds').stat().st_size<100*1024**2,'3DS must remain below GitHub single-file limit'
# Hover boundaries retain mapped outlines; they are independent of persistent labels.
for place in places:
    if place.get('hitArea'):continue
    candidates=[f['poly'] for f in osm if f['properties'].get('name')==place['name'] and f['poly'].geom_type in ['Polygon','MultiPolygon']]
    q=unary_union(candidates).intersection(scope).simplify(.20,preserve_topology=True)
    # Clipping can leave line-only remnants; hover boundaries must remain polygonal.
    q=unary_union(polygons(q))
    place['hitArea']=mapping(set_precision(q,.01))
    place['source']='https://www.openstreetmap.org/'
for name,data in [('layer_map',layer_map),('palette',COLORS),('buildings',records),('viewer_records',records),('places',places)]:
    (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2))
with (OUT/'building_dimensions_and_sources.csv').open('w',encoding='utf-8-sig',newline='') as fd:
    w=csv.DictWriter(fd,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
(OUT/'footprints_local_meters.geojson').write_text(json.dumps({'type':'FeatureCollection','coordinate_system':{'epsg':32610,'origin_easting':OX,'origin_northing':OY,'origin_wgs84':[LON,LAT],'unit':'m','note':'Local projected meters, not RFC7946 longitude/latitude'},'features':[{'type':'Feature','properties':f['record'],'geometry':mapping(f['poly'])} for f in buildings]},ensure_ascii=False,separators=(',',':')))
av=[];af=[];co=[];offset=0
for m,mat in meshdata:av.append(m.vertices);af.append(m.faces+offset);co.extend([COLORS[mat]]*len(m.faces));offset+=len(m.vertices)
np.savez_compressed(OUT/'preview_mesh_data.npz',vertices=np.vstack(av),faces=np.vstack(af),colors=np.asarray(co,dtype=np.uint8))
summary={'buildings':len(records),'layers':len(model.Layers),'environment_layer':'Environment','native_closed_solids':sum(isinstance(o.Geometry,rh.Extrusion) for o in model.Objects),'objects_3ds':len(objects),'vertices':offset,'triangles':sum(len(m.faces) for m,_ in meshdata),'trees':trees,'quad_cherry_trees':cherry,'landmarks':sum(r['landmark'] for r in records),'unit':'meters','crs':'EPSG:32610 local offsets','origin_wgs84':[LON,LAT],'origin_utm':[OX,OY],'local_z_zero_m':0,'bounds':scope.bounds,'district_bounds':{z:list(g.bounds) for z,g in zone_shapes.items()},'overview_center':[round(rc.x,4),round(rc.y,4)],'terrain':'USGS 3DEP F32 bare-earth DEM sampled at about 10m; landscape patches 60m with 12m edge segmentation and flattened building pads','terrain_source':'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer','sectors':{z:sum(r['zone']==z for r in records) for z in zone_shapes},'accuracy':'Official mapped footprint/tree positions; all exterior heights, roof/facade geometry and tree forms approximate, not surveyed.'}
summary['water_frame']=water_frame
summary['neighboring_areas']={k:v for k,v in neighbors.items() if k in ['buildings','trees','bounds','landscape_layer','street_network','default_visible']}
summary['native_closed_solids']=sum(isinstance(o.Geometry,rh.Extrusion) for o in model.Objects)
(OUT/'model_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(OUT/'excluded_records.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2));print(json.dumps(summary,indent=2),flush=True)
