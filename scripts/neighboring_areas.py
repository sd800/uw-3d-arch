"""Mapped U District context; separate layers let the viewer restore campus only.
OSM outlines and tagged heights are retained. Unrecorded facade bays, widths,
materials and heights are conservative exterior approximations.
"""
from cad_core import *
from shapely import segmentize,points,get_coordinates
from shapely.strtree import STRtree
from architecture_refinement import window,courses
from university_inn import build_inn
import gzip

# Published project floor counts; metric envelope heights remain estimates except
# The Accolade's architect-published 240 ft. No rooftop equipment is invented.
PROFILES={
 'The Accolade':(21,73.152,'ContextPanel','https://www.weberthompson.com/thought/the-accolade-high-rise-housing-for-the-student-experience/'),
 'The Standard at Seattle':(25,79.5,'ContextPanel','https://ankrommoisan.com/projects/the-standard-at-seattle-high-rises/'),
 'ōLiv Seattle':(25,79.5,'ContextStone','https://www.findorff.com/project/oliv-at-seattle/'),
 'The M':(24,76,'ContextPanel','https://www.openstreetmap.org/way/701970651'),
 'Graduate by Hilton Seattle':(16,55,'ContextBrick','https://www.openstreetmap.org/way/223479986'),
 'Neptune Building':(3,12.4,'ContextBrick','https://web.seattle.gov/DPD/HistoricalSite/QueryResult.aspx?ID=5'),
 'Wilsonian Apartments':(6,20,'ContextBrick','https://www.openstreetmap.org/way/223484924'),
 'University Presbyterian Church':(2,12.5,'ContextBrick','https://www.openstreetmap.org/way/52136493'),
 'U District Station South Entrance':(1,6.1,'ContextStone','https://www.soundtransit.org/ride-with-us/stops-stations/u-district-station'),
 'Gateway Building':(13,48,'ContextPanel','https://perkinswill.com/project/gateway-building/'),
}

def build_neighbors(osm,campus_scope,campus_footprints,raw_ground,campus_ground,official_trees):
    selection=unary_union([box(-665,-470,-200,1038),box(-200,604,415,1038),box(-975,-600,-200,40)])
    candidates=[]
    for f in osm:
        t=f['properties'];p=f['poly']
        if not t.get('building') or p.geom_type not in ['Polygon','MultiPolygon'] or p.area<18:continue
        if not selection.covers(p.representative_point()) or p.intersection(campus_footprints).area>p.area*.02:continue
        if t.get('location')=='underground' or t.get('building') in ['roof','construction','demolished'] or t.get('demolished:building'):continue
        if p.intersects(campus_footprints):p=p.difference(campus_footprints.buffer(.15)).buffer(0)
        if p.is_empty or p.area<18:continue
        candidates.append({**f,'poly':p})
    # Multipolygon members and outer building ways can duplicate each other.
    accepted=[]
    for f in sorted(candidates,key=lambda q:-q['poly'].area):
        if any(f['poly'].intersection(a['poly']).area>f['poly'].area*.18 for a in accepted if f['poly'].intersects(a['poly'])):continue
        overlaps=unary_union([a['poly'].buffer(.04)for a in accepted if f['poly'].intersects(a['poly'])])
        p=f['poly'].difference(overlaps).buffer(0)
        if not p.is_empty and p.area>18:accepted.append({**f,'poly':p})
    # Join two well-known point-of-interest labels from the retained OSM XML
    # to their containing footprint, rather than labeling every tenant a building.
    poi_names={'Neptune Theatre':'Neptune Building','University Book Store':'University Book Store'}
    with gzip.open(ROOT/'sources/osm_map_west.xml.gz','rb')as source:poi_root=ET.parse(source).getroot()
    for node in poi_root.findall('node'):
        tags={a.attrib['k']:a.attrib['v']for a in node.findall('tag')}
        if tags.get('name')not in poi_names:continue
        x,y=TF.transform(float(node.attrib['lon']),float(node.attrib['lat']));pt=Point(x-OX,y-OY)
        for f in accepted:
            if f['poly'].buffer(.3).covers(pt):f['properties']={**f['properties'],'name':poi_names[tags['name']],'poi_source':'https://www.openstreetmap.org/node/'+node.attrib['id']}
    accepted.sort(key=lambda q:(-q['poly'].centroid.y,q['poly'].centroid.x,q['properties']['osm_id']))
    neighbor_footprints=unary_union([f['poly'] for f in accepted]);all_footprints=unary_union([campus_footprints,neighbor_footprints])
    extent=unary_union([selection,*[f['poly'].buffer(4) for f in accepted]]).buffer(0)
    campus_boundary=next(f['poly']for f in osm if f['properties'].get('osm_id')=='relation/5268488')
    water=unary_union([f['poly']for f in osm if f['properties'].get('natural')=='water'])
    # Fill the west-campus gaps and road joins, including the former pale
    # footprint-buffer islands outside the actual main-campus boundary.
    # Retain a continuous street/land patch between campus-owned islands.
    area=extent.difference(campus_boundary).difference(water).buffer(0)
    # Sample the actual already-exported campus ground triangles, including
    # transitions beside flattened UW pads. Raw DEM alone can be lower than
    # those triangles near a large adjacent building. Supports still reach the
    # underlying DEM, while the neighbor's level floor stays clear of both.
    exported_tri=[]
    for mesh,material in meshdata:
        if material!='Ground':continue
        tri=mesh.vertices[mesh.faces];ab=tri[:,1]-tri[:,0];ac=tri[:,2]-tri[:,0];det=ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0]
        exported_tri.extend(tri[det>1e-7])
    exported_tri=np.asarray(exported_tri);tri_polys=[Polygon(v[:,:2])for v in exported_tri];tri_tree=STRtree(tri_polys)
    for f in accepted:
        p=f['poly'];p0=segmentize(p,5);xy=np.array(p0.exterior.coords) if p0.geom_type=='Polygon' else np.vstack([np.array(q.exterior.coords)for q in p0.geoms])
        # A closed skirt reaches sampled ground on every side. The level floor
        # sits above its highest boundary sample, never floating on a hillside.
        floor=float(np.max(raw_ground(xy[:,0],xy[:,1])))+.25
        for index in tri_tree.query(p):
            q=p.intersection(tri_polys[index]);coords=get_coordinates(q)
            if not len(coords):continue
            a,b,c=exported_tri[index];u=b-a;v=c-a;det=u[0]*v[1]-u[1]*v[0];delta=coords-a[:2];uu=(delta[:,0]*v[1]-delta[:,1]*v[0])/det;vv=(u[0]*delta[:,1]-u[1]*delta[:,0])/det
            floor=max(floor,float(np.max(a[2]+uu*u[2]+vv*v[2]))+.08)
        f['grade']=floor
    pad_shapes=[f['poly'].buffer(.12) for f in accepted];tree=STRtree(pad_shapes);heights=np.array([f['grade'] for f in accepted])
    def ground(x,y):
        x,y=np.broadcast_arrays(x,y);z=np.array(campus_ground(x,y),copy=True)
        aa,bb=tree.query(points(x.ravel(),y.ravel()),predicate='within');z.ravel()[aa]=heights[bb];return z
    roadparts=[];walkparts=[];roadlines=[]
    widths={'primary':14,'secondary':11,'tertiary':9,'residential':7,'unclassified':7,'service':4,'living_street':5,'pedestrian':5}
    for f in osm:
        t=f['properties'];g=f['poly'];h=t.get('highway')
        if g.geom_type not in ['LineString','MultiLineString'] or not g.intersects(extent) or t.get('tunnel')=='yes' or t.get('layer','0').startswith('-'):continue
        if h in widths:
            try:w=float(t.get('width',widths[h]))
            except ValueError:w=widths[h]
            roadparts.append(g.buffer(w/2,cap_style=2,join_style=2));roadlines.append((g,w,t))
        elif h in ['footway','path','steps','cycleway']:
            try:w=float(t.get('width',2.4 if h!='cycleway'else 3))
            except ValueError:w=2.4
            walkparts.append(g.buffer(w/2,cap_style=2,join_style=2))
    bridge_mask=unary_union([f['poly'].buffer(7,cap_style=2,join_style=2)for f in osm if f['properties'].get('bridge')in ['yes','movable','viaduct']and f['properties'].get('highway')in ['primary','secondary','tertiary']and f['poly'].intersects(water.buffer(25))])
    roadarea=unary_union(roadparts).difference(bridge_mask).intersection(area).difference(all_footprints).buffer(0)
    # Joined sidewalks/curbs follow the mapped road corridors rather than
    # free-floating decorative strips. Recorded separate walks join this skin.
    sidewalks=unary_union([g.buffer(w/2+2.7,cap_style=2,join_style=2)for g,w,t in roadlines if t.get('highway')!='service']).difference(unary_union(roadparts))
    walkarea=unary_union([sidewalks,*walkparts]).intersection(area).difference(all_footprints).difference(roadarea).buffer(0)
    street_union=unary_union([g for g,w,t in roadlines]);msenv={m:[]for m in COLORS};context_records=[];pads=[];samples=[];detail_count=0
    for j,f in enumerate(accepted,1):
        p=f['poly'];t=f['properties'];c=p.centroid;z=f['grade'];code=f'N{j:03d}'
        address=' '.join(filter(None,[t.get('addr:housenumber'),t.get('addr:street')]))
        name=t.get('name') or address or 'U District building '+t['osm_id'].split('/')[-1]
        if t['osm_id']=='way/98531546':name=t.get('name',name)
        kind=t.get('building');res=kind in ['house','residential','apartments','detached','dormitory','terrace']
        try:levels=max(1,min(30,int(float(t.get('building:levels','')))))
        except ValueError:levels=2 if kind in ['house','detached','yes','retail'] else 4 if res else 2
        try:h=max(3,min(110,float(t.get('height',''))))
        except ValueError:h=levels*(3.05 if res else 3.65)+.55
        wall='ContextBrick'if t.get('building:material')=='brick' or kind in ['house','dormitory']else 'ContextStone'if kind in ['yes','retail','church']else 'ContextPanel'
        source='https://www.openstreetmap.org/'+t['osm_id'];profile=PROFILES.get(name)
        # Neptune may be named for its tenant in contributed data.
        if 'Neptune' in name:profile=PROFILES['Neptune Building']
        if profile:levels,h,wall,source=profile
        if name=='University Book Store':levels=2;h=8.2;wall='ContextBrick';source='https://ubookstore.com/pages/about-us'
        pitched_roof=t.get('roof:shape')in ['gabled','hipped','half-hipped','mansard'] or kind in ['house','detached'] and p.area<350
        rise=min(3.2,h*.23)if pitched_roof else 0;body=h-rise-.18
        hotel=name=='University Inn'
        if hotel:name='University Inn - A Staypineapple Hotel';h=13.65;levels=4;source='https://www.staypineapple.com/university-inn-seattle-wa/gallery'
        roofmat='RoofContextSlate'if pitched_roof or t.get('roof:colour')in ['black','darkgray','darkgrey']else 'RoofContextWarm'if t.get('roof:colour')in ['white','silver','beige']else 'RoofContext'
        lay=code+'_'+name.replace(':',' ').replace('/',' ');layer(lay,wall)
        ms={m:[]for m in COLORS};info={'NameEN':name,'Source':source,'FootprintSource':'https://www.openstreetmap.org/'+t['osm_id'],'Scope':'Campus neighboring areas','Approximation':'Exterior heights and facade members approximate; see neighboring_records.json','Units':'meters'}
        if hotel:build_inn(ms,p,z,code,lay,info,raw_ground)
        for q in ([]if hotel else polygons(p)):
            native_extrude(q,z,body,code+'_Volume',lay,wall,info)
            ms[wall].append(extrusion(q,z,body))
            support=extrusion(segmentize(q,5),z-1.5,1.51);bottom=support.vertices[:,2]<z-.7
            support.vertices[bottom,2]=np.minimum(z-1,raw_ground(support.vertices[bottom,0],support.vertices[bottom,1])-1.2)
            ms[wall].append(support)
            if pitched_roof:ms[roofmat].extend(pitched(q,z+body,rise))
            else:
                ms[roofmat].append(extrusion(q,z+body,.16))
                courses(ms,q,[z+body+.16],'ContextStone',.28,.02)
            # Real footprint corners, courtyard voids and openings. Party walls
            # have no invented windows; street fronts get finer bay spacing.
            for ring in [q.exterior,*q.interiors]:
                cc=np.asarray(ring.coords)
                for a,b in zip(cc[:-1],cc[1:]):
                    ln=np.linalg.norm(b-a)
                    if ln<3:continue
                    u=(b-a)/ln;n=np.array([u[1],-u[0]]);mid=(a+b)/2
                    outside=Point(*(mid+n*.6))
                    if any(k!=j-1 and pad_shapes[k].contains(outside)for k in tree.query(outside)):continue
                    near=outside.distance(street_union)<22
                    pitch=3.6 if near else 5.2;count=max(1,int((ln-.6)/pitch));spacing=(ln-.8)/count
                    # Thin, closed glass panels are offset from the wall; no
                    # repeated rods, detached fins or copied rooftop boxes.
                    for k in range(levels):
                        floor=body/levels;zz=z+k*floor+.72;wh=min(2.25,floor-1.05)
                        for b0 in range(count):
                            origin=a+u*(.4+(b0+.5)*spacing)
                            width=min(1.45 if res else spacing*.72,spacing-.45)
                            store=k==0 and near and (kind in ['retail','commercial','office','yes']or levels>6)
                            if store:width=spacing-.3;wh=floor-1.0;zz=z+.28
                            # Frame rings only on primary street faces; all
                            # other windows remain closed extruded panes.
                            if near and name in ['Neptune Building','University Book Store','University Presbyterian Church','U District Station South Entrance']:
                                window(ms,origin,u,n,zz,width,wh,False,'ContextStone',0)
                            else:
                                pane=extrusion(box(-width/2,0,width/2,wh),0,.075);vv=pane.vertices.copy()
                                pane.vertices=np.column_stack((origin[0]+vv[:,0]*u[0]+(vv[:,2]+.08)*n[0],origin[1]+vv[:,0]*u[1]+(vv[:,2]+.08)*n[1],zz+vv[:,1]));trimesh.repair.fix_normals(pane);ms['ContextGlass'].append(pane)
                    if near and ln>7:
                        # Low entry recess panel and a shallow attached canopy
                        # limited to the ground floor, rather than tall fins.
                        entry=a+u*(ln*.5);w=min(2.0,ln*.2)
                        window(ms,entry,u,n,z+.08,w,2.4,False,'ContextStone',1)
                        if kind in ['retail','commercial','yes']and not res:
                            canopy=Polygon([entry-u*(w+1)+n*.06,entry+u*(w+1)+n*.06,entry+u*(w+1)+n*.85,entry-u*(w+1)+n*.85])
                            ms['ContextBrick'].append(extrusion(canopy,z+2.85,.12))
            if levels>=8:courses(ms,q,[z+k*body/levels for k in range(1,levels)],'ContextStone',.09,.035)
            elif levels>1:courses(ms,q,[z+.22,z+body-.3],'ContextStone',.15,.055)
        for k,(mat,parts)in enumerate(ms.items()):
            if parts:chunk_meshes(code+('D'if mat in ['DarkGlass','Frame','ContextGlass']else 'M')+f'{k:02d}',parts,mat,lay,info)
        a,b,cx,d=p.bounds
        zh={'University Inn - A Staypineapple Hotel':'University Inn 酒店','University Book Store':'大学书店','Neptune Building':'海王星剧院大楼','University Presbyterian Church':'大学长老会教堂','U District Station South Entrance':'大学区轻轨站南入口','Gateway Building':'门户大楼'}.get(name,name)
        r={'code':code,'facility_id':t['osm_id'],'name':name,'name_zh':zh,'short':name,'short_zh':zh,'layer':lay,'zone':'neighbors','neighbor':True,'landmark':False,'height':round(h,3),'height_status':'estimated','levels':levels,'area':round(p.area,2),'width':round(cx-a,2),'depth':round(d-b,2),'center':[round(p.centroid.x,3),round(p.centroid.y,3)],'ground_m':round(z,3),'peak_m':round(z+h,3),'basis_en':'OSM mapped outline and available height/storey tags; selected project floor counts checked against the linked primary reference. Other exterior elevations are estimates.','basis':'采用OpenStreetMap轮廓及已有高度、层数标记；部分项目层数参照所列一手资料，其余外部标高为估算。','partition_en':'Separate neighboring-area layer with mapped footprint and courtyard holes, attached street-front windows, entry glazing, roof and ground-reaching support. Secondary facade dimensions are approximate.','partition':'周边区域独立图层，保留映射轮廓和庭院，细化临街窗格、入口和屋顶，以闭合基座连接地形；次要构件尺寸为近似表达。','source':source,'footprint_source':'https://www.openstreetmap.org/'+t['osm_id'],'address':address,'roof_shape':t.get('roof:shape','estimated pitched'if pitched_roof else 'flat'),'height_tags':{key:t[key]for key in ['height','building:levels','roof:shape','building:material']if key in t}}
        if hotel:r['partition_en']='Photo-referenced mid-century hotel with three guest-room floors over a recessed arrival/parking level, paired multi-pane windows, folded attached eaves, warm curved end, vertical sign and supported canopy. Member dimensions remain approximate.';r['partition']='参照官方外观照片重建三层客房及底层内凹入口与停车空间，细化成组窗格、折叠式挑檐、暖色转角、立面招牌和带支撑雨棚；构件尺寸为近似表达。'
        context_records.append(r);f['record']=r;pads.append({'code':code,'height':z,'bounds':list(p.bounds),'geometry':mapping(p)})
        for q in polygons(p):
            inner=q.buffer(-.15);inner=q if inner.is_empty else max(polygons(inner),key=lambda g:g.area)
            for pt in [inner.representative_point(),*[inner.exterior.interpolate(inner.exterior.length*k/4)for k in range(4)]]:samples.append({'code':code,'position':[pt.x,pt.y,z]})
        detail_count+=sum(len(mm.faces)for pp in ms.values()for mm in pp)
        if j%100==0:print('Neighboring buildings',j,flush=True)
    def env(g,z,thickness,mat,drape=True):
        g=g.intersection(area).difference(all_footprints).buffer(0)
        for q in polygons(g):
            a,b,c,d=q.bounds
            for xx in np.arange(math.floor(a/60)*60,c,60):
                for yy in np.arange(math.floor(b/60)*60,d,60):
                    for part in polygons(q.intersection(box(xx,yy,xx+60,yy+60))):
                        m=extrusion(segmentize(part,10),z,thickness)
                        if drape:m.vertices[:,2]+=ground(m.vertices[:,0],m.vertices[:,1])
                        msenv[mat].append(m)
    env(area,-3,3,'ContextGround');env(roadarea,.03,.07,'Road');env(walkarea,.16,.055,'ContextWalk')
    # Exact flat footprint pads join body/support to the exported terrain.
    for f in accepted:
        if f['properties'].get('building')in ['house','detached','dormitory','apartments','residential']:
            env(f['poly'].buffer(4.5).difference(roadarea).difference(walkarea),.1,.05,'ContextGrass')
        for q in polygons(f['poly']):msenv['Ground'].append(extrusion(q,f['grade']-.18,.18))
    greens=[]
    for f in osm:
        t=f['properties'];g=f['poly']
        if g.geom_type not in ['Polygon','MultiPolygon']or not g.intersects(area)or t.get('building'):continue
        if t.get('landuse')in ['brownfield','construction']:env(g.difference(roadarea).difference(walkarea),.13,.04,'ContextGravel')
        elif t.get('landuse')in ['retail','commercial','industrial']:env(g.difference(roadarea).difference(walkarea),.12,.035,'ContextLot')
        elif t.get('landuse')in ['residential']:env(g.difference(roadarea).difference(walkarea),.1,.05,'ContextGrass')
        elif t.get('landuse')in ['forest','grass','meadow','village_green']or t.get('natural')in ['wood','scrub']or t.get('leisure')in ['garden','park']:
            greens.append(g);env(g.difference(roadarea).difference(walkarea),.1,.05,'ContextGrass')
        elif t.get('amenity')=='parking':env(g.difference(roadarea),.13,.035,'Road')
        elif t.get('highway')=='pedestrian':env(g.difference(roadarea),.17,.035,'ContextPaving')
    site=next((f['poly']for f in osm if f['properties'].get('osm_id')=='way/223362698'),None)
    if site is not None:
        for ring in polygons(site.intersection(area)):
            fence=LineString(ring.exterior.coords)
            for k in np.arange(0,fence.length,3.5):
                p0=fence.interpolate(k);zz=float(ground(p0.x,p0.y));msenv['Furniture'].append(cylinder((p0.x,p0.y,zz),(p0.x,p0.y,zz+1.65),.035,5))
            rail=fence.buffer(.022,cap_style=2,join_style=2)
            for q in polygons(rail):
                m=extrusion(segmentize(q,4),1.45,.045);m.vertices[:,2]+=ground(m.vertices[:,0],m.vertices[:,1]);msenv['Furniture'].append(m)
    # Map-derived street trees are added only at published UW GIS positions.
    city=[]
    for f in json.loads((ROOT/'sources/seattle_street_trees.geojson').read_text())['features']:
        xx,yy=TF.transform(*f['geometry']['coordinates'][:2]);city.append({'poly':Point(xx-OX,yy-OY),'properties':f['properties']})
    trees=0;used=[];tree_clearance=all_footprints.buffer(.7)
    for f in [*official_trees,*city]:
        p=f['poly']
        if not area.contains(p)or tree_clearance.contains(p)or roadarea.contains(p)or any(p.distance(pt)<2 for pt in used):continue
        used.append(p)
        x,y=p.x,p.y;z=float(ground(x,y));r=2.1
        msenv['Trunk'].append(cylinder([x,y,z],[x,y,z+4],.15,6))
        m=trimesh.creation.icosphere(subdivisions=1);m.apply_scale([r,r,2.7]);m.apply_translation([x,y,z+4.4]);msenv['ContextLeaves'].append(m);trees+=1
    layer('Neighboring_Environment','ContextGrass')
    for k,(mat,parts)in enumerate(msenv.items()):
        if parts:chunk_meshes(f'NE{k:02d}',parts,mat,'Neighboring_Environment',{'Scope':'Campus neighboring areas','Source':'OpenStreetMap / UW trees / USGS terrain','Units':'meters'})
    for entry in layer_map.values():
        if entry['layer']=='Neighboring_Environment':entry['category']='neighbor-environment'
        elif entry['layer'].startswith('N'):entry['category']='neighbor-building'
    (OUT/'neighboring_records.json').write_text(json.dumps(context_records,ensure_ascii=False,indent=2))
    with (OUT/'neighboring_building_dimensions_and_sources.csv').open('w',encoding='utf-8-sig',newline='')as fp:
        writer=csv.DictWriter(fp,fieldnames=list(context_records[0]));writer.writeheader();writer.writerows(context_records)
    (OUT/'neighboring_footprints.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':f['record'],'geometry':mapping(f['poly'])}for f in accepted]},ensure_ascii=False,separators=(',',':')))
    report={'buildings':len(accepted),'trees':trees,'bounds':extent.bounds,'landscape_layer':'Neighboring_Environment','default_visible':True,'street_network':'University Way NE, Brooklyn Avenue NE, Roosevelt Way NE, NE 40th–50th streets and the north-campus residential blocks','building_triangles':detail_count,'pads':pads,'ground_samples':samples,'differentiation':'Muted neutral/brick wall palette, separate context ground; exact mapped footprint positions retained','scope_geometry':mapping(area)}
    (OUT/'neighboring_areas.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')))
    print('Neighboring areas:',len(accepted),'buildings;',trees,'mapped trees;',detail_count,'building triangles',flush=True)
    return report
