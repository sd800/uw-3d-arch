"""Photo-referenced surface transit architecture; no invented underground BIM."""
from cad_core import *
from shapely import segmentize

UW_STATION='https://lmnarchitects.com/project/university-of-washington-station-sound-transit'
UD_STATION='https://lmnarchitects.com/project/u-district-station-sound-transit'
BRIDGE_IDS={'way/369723298','way/370063488','way/524280882','way/524280883','way/524280884','way/570797482'}
REPORT=[]

def add(ms,g,z,h,mat):
    for q in polygons(g):ms[mat].append(extrusion(q,z,h))

def letter_sign(ms,text,origin,u,n,z,width,height=.5,mat='Marking'):
    # Vector glyph solids remain readable in Rhino/3DS, without bitmap textures.
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fp=FontProperties(fname=str(ROOT/'assets/fonts/Manrope.ttf'))
    path=TextPath((0,0),text,size=1,prop=fp);rings=path.to_polygons()
    if not rings:return
    g=Polygon()
    for ring in rings:
        if len(ring)>3:g=g.symmetric_difference(Polygon(ring).buffer(0))
    g=set_precision(g,.005).simplify(.002,preserve_topology=True).buffer(0)
    if g.is_empty:return
    a,b,c,d=g.bounds;scale=min(width/(c-a),height/(d-b));g=affinity.translate(affinity.scale(g,scale,scale,origin=(a,b)),xoff=-(a+c)/2,yoff=-b)
    # Recenter after scale, retaining counters in glyphs such as A, B and O.
    aa,bb,cc,dd=g.bounds;g=affinity.translate(g,-(aa+cc)/2,-bb)
    g=set_precision(g,.005).simplify(.002,preserve_topology=True).buffer(0)
    for q in ([g]if g.geom_type=='Polygon'else list(g.geoms)):
        if q.geom_type!='Polygon'or q.area<.00001:continue
        m=extrusion(q,0,.045);v=m.vertices.copy();m.vertices=np.column_stack((origin[0]+v[:,0]*u[0]+v[:,2]*n[0],origin[1]+v[:,0]*u[1]+v[:,2]*n[1],z+v[:,1]));trimesh.repair.fix_normals(m);ms[mat].append(m)

def glass_shell(ms,p,base,h,bay=2.7,opening=None,trim='Metal'):
    # Independent thin closed infills and load-bearing posts, not a solid glass box.
    for q in polygons(p):
        cc=np.array(q.exterior.coords)
        for a,b in zip(cc[:-1],cc[1:]):
            length=np.linalg.norm(b-a)
            if length<.5:continue
            u=(b-a)/length;n=np.array([u[1],-u[0]]);count=max(1,math.ceil(length/bay))
            for j in range(count):
                aa=a+u*(j*length/count+.045);bb=a+u*((j+1)*length/count-.045);at=(aa+bb)/2
                if opening and opening.buffer(.05).covers(Point(*at)):continue
                pane=Polygon([aa+n*.015,bb+n*.015,bb+n*.085,aa+n*.085]);add(ms,pane,base+.18,h-.28,'Glass')
                for z in [base+.16,base+h*.51,base+h-.10]:add(ms,pane.buffer(.025,join_style=2),z,.06,trim)
                ms[trim].append(cylinder((a[0]+u[0]*j*length/count,a[1]+u[1]*j*length/count,base),(a[0]+u[0]*j*length/count,a[1]+u[1]*j*length/count,base+h),.045,5))

def build_uw_station(ms,p,base,code,lay,info,ground):
    h=10.4;upper=5.6;opening=unary_union([box(405,-692,414,-684),box(408,-636,420,-632),box(420,-663,425,-650)])
    add(ms,p,base,.18,'Concrete');add(ms,p,base+upper-.30,.30,'Concrete')
    glass_shell(ms,p,base,h-.3,2.5,opening,'Metal')
    # Photo-visible upper/lower lobby structure and narrow east elevator projection.
    for y in np.arange(-685,-635,5.4):
        for x in [411.3,417.7]:
            if p.buffer(.4).covers(Point(x,y)):ms['Metal'].append(cylinder((x,y,base-.3),(x,y,base+h-.2),.14,6))
    core=p.intersection(box(418.3,-663,423,-652));add(ms,core,base,upper+.1,'Precast')
    roof=p.buffer(.65,join_style=2)
    add(ms,roof,base+h,.20,'RoofSilver')
    add(ms,roof.boundary.buffer(.09),base+h+.20,.12,'Metal')
    add(ms,p.buffer(-.12).difference(p.buffer(-.38)),base+upper,.48,'Precast')
    for y in np.arange(-684,-638,3.0):
        beam=box(410.5,y-.075,418.3,y+.075).intersection(roof);add(ms,beam,base+h-.3,.25,'Metal')
    # Darkened door portals remain at grade, with individually framed leaves.
    from architecture_refinement import window
    window(ms,np.array([409.1,-690.7]),np.array([1.,0]),np.array([0.,-1]),base+.12,2.6,3.1,False,'Metal',1)
    sa=np.array([411.55,-687.99]);sb=np.array([419.60,-687.77]);su=(sb-sa)/np.linalg.norm(sb-sa);sn=np.array([su[1],-su[0]]);sc=(sa+sb)/2
    window(ms,sc,su,sn,base+3.0,7.6,.70,False,'Metal',0)
    letter_sign(ms,'UNIVERSITY OF WASHINGTON',sc+sn*.265,su,sn,base+3.13,7.4,.42)
    window(ms,np.array([422.8,-657.4]),np.array([0.,1]),np.array([1.,0]),base+3.0,3.6,.9,False,'Metal',0)
    letter_sign(ms,'LINK',(423.065,-657.4),np.array([0.,1]),np.array([1.,0]),base+3.12,3.3,.62)
    for q in polygons(p):native_extrude(q,base,.18,code+'_Plinth',lay,'Concrete',info)
    result={'facility_id':'LINK_UW','height_m':h+.32,'levels':2,'volume_parts':[{'name':'Two-level glazed station headhouse','height_m':h,'area_m2':round(p.area,2)}],'details':['Mapped station footprint with a two-level glazed lobby, steel column/bay structure and thin silver roof','Upper lobby deck meets the mapped Montlake bicycle/pedestrian bridge','Ground entrances, east elevator projection and restrained vector signage','Above-ground exterior only; underground station and railway tunnels are not fabricated'],'reference':UW_STATION}
    REPORT.append(result);return result

def build_ud_south(ms,p,z,code,lay,info,ground):
    # South entrance: a low black granite enclosure inside a broad tapered canopy.
    # The north entrance is integrated in the Gateway building, not a duplicate pavilion.
    h=6.1;core=p.buffer(-2.2,join_style=2).intersection(box(-369,456,-344,475.7));opening=box(-376,451,-365,467)
    add(ms,p,z-.18,.30,'Concrete')
    for q in polygons(segmentize(p,4)):
        support=extrusion(q,z-1.8,1.82);low=support.vertices[:,2]<z-.5;support.vertices[low,2]=np.minimum(z-1.2,ground(support.vertices[low,0],support.vertices[low,1])-1.2);ms['Foundation'].append(support)
    for q in polygons(core):native_extrude(q,z,.12,code+'_Lobby',lay,'Concrete',info)
    wall=core.boundary.buffer(.22,join_style=2).difference(opening)
    add(ms,wall,z+.12,4.75,'Slate')
    glass_shell(ms,p.buffer(-.45,join_style=2),z,4.9,3.2,unary_union([box(-376,451,-363,467),box(-376,450,-340,455.1)]),'Metal')
    canopy=p.buffer(.9,join_style=2);m=extrusion(canopy,z+5.15,.22)
    # A gently rising plane with a deep perimeter edge, as in the architect's photo.
    m.vertices[:,2]+=.85*(m.vertices[:,1]-p.bounds[1])/(p.bounds[3]-p.bounds[1]);ms['RoofSilver'].append(m)
    rim=extrusion(canopy.boundary.buffer(.10),z+5.37,.20);rim.vertices[:,2]+=.85*(rim.vertices[:,1]-p.bounds[1])/(p.bounds[3]-p.bounds[1]);ms['Metal'].append(rim)
    for x in [-371.9,-342.1]:
        for y in [453.3,474.5]:
            top=z+5.15+.85*(y-p.bounds[1])/(p.bounds[3]-p.bounds[1]);ms['Frame'].append(cylinder((x,y,z-.2),(x,y,top),.13,6))
    for y in np.arange(455,474,4):
        top=z+5.1+.85*(y-p.bounds[1])/(p.bounds[3]-p.bounds[1]);add(ms,box(-372,y-.09,-342,y+.09),top,.22,'Frame')
    letter_sign(ms,'U District',(-357.5,454.18),np.array([1.,0]),np.array([0.,-1]),z+1.9,15,1.5)
    # Entrance portal/receding escalator mouth; no underground terrain hole.
    from architecture_refinement import window
    window(ms,np.array([-372.35,462.5]),np.array([0.,1]),np.array([-1.,0]),z+.12,5.3,3.6,False,'Metal',2)
    REPORT.append({'facility_id':'U_DISTRICT_SOUTH','mapped_id':'way/746277336','reference':UD_STATION,'height_m':6.3,'details':['Low granite station enclosure, open entrance recess, tapered silver canopy and exposed supporting steel','Both street approaches and vector U District sign; exterior heights are photo-informed estimates']})

def ud_north_portal(ms,p,z,ground):
    from architecture_refinement import window
    x=-371.95;y=551.7;opening=box(-376,547.0,-366.0,558.3)
    # Dark doorway replaces the west podium grid in the retained mixed-use building.
    window(ms,np.array([x-.13,y]),np.array([0.,1]),np.array([-1.,0]),z+.08,8.0,4.65,False,'Metal',2)
    awning=box(x-2.0,y-5,x+.7,y+5);add(ms,awning,z+5.25,.22,'RoofSilver')
    for yy in [y-4.7,y+4.7]:ms['Frame'].append(cylinder((x-1.6,yy,min(z,float(ground(x-1.6,yy)))-.3),(x-1.6,yy,z+5.25),.095,6))
    add(ms,box(x-2.02,y-5,x-1.92,y+5),z+4.62,.84,'Slate')
    letter_sign(ms,'U District',(x-2.045,y),np.array([0.,1]),np.array([-1.,0]),z+4.78,8.6,.45)
    REPORT.append({'facility_id':'U_DISTRICT_NORTH','reference':UD_STATION,'mapped_entrance_node':'10220232278','integrated_in':'Gateway Building','details':['Mapped north entrance retained at the base of the Gateway building; dark portal, framed glazing and supported canopy']})

def station_landscape(eg,env,osm,station,ground,footprints,places):
    p=station['poly'];base=station['ground'];level=base+5.6
    # Select the mapped bridge graph, preserving its curved plan and forked ramps.
    fs=[f for f in osm if f['properties'].get('osm_id')in BRIDGE_IDS]
    lines=[]
    for f in fs:
        line=f['poly'];w=9.144 if f['properties']['osm_id']=='way/524280883'else 4.572 if f['properties']['osm_id']in ['way/369723298','way/524280882']else 4.267
        z0=z1=level
        if f['properties']['osm_id']=='way/524280882':
            z0=float(ground(*line.coords[0]))+.20
        if f['properties']['osm_id']=='way/524280884':
            z1=float(ground(*line.coords[-1]))+.20
        if f['properties']['osm_id']=='way/370063488':z0=float(ground(*line.coords[0]))+.20
        lines.append((line,w,z0,z1))
    plan=unary_union([g.buffer(w/2,cap_style=2,join_style=1)for g,w,_,_ in lines]).buffer(0)
    def z_at(x,y):
        xy=np.column_stack((np.asarray(x).ravel(),np.asarray(y).ravel()));zz=[]
        for xx,yy in xy:
            pt=Point(xx,yy);line,w,z0,z1=min(lines,key=lambda row:row[0].distance(pt));t=line.project(pt)/line.length;zz.append(z0+(z1-z0)*t)
        return np.array(zz)
    for q in polygons(segmentize(plan,2.5)):
        m=extrusion(q,-.48,.48);m.vertices[:,2]+=z_at(m.vertices[:,0],m.vertices[:,1]);trimesh.repair.fix_normals(m);eg['BridgeDeck'].append(m)
    ends=[Point(g.coords[0] if z0<z1 else g.coords[-1])for g,_,z0,z1 in lines if abs(z0-z1)>.1]+[Point(413.66,-634.44)]
    guards=plan.boundary.difference(unary_union([pt.buffer(1.8)for pt in ends]))
    for line in ([guards]if guards.geom_type=='LineString'else list(guards.geoms)):
        if line.geom_type!='LineString':continue
        pts=[line.interpolate(d)for d in np.linspace(0,line.length,max(2,math.ceil(line.length/2)+1))]
        for a,b in zip(pts[:-1],pts[1:]):
            za,zb=z_at([a.x,b.x],[a.y,b.y]);eg['Metal'].append(cylinder((a.x,a.y,za+1.10),(b.x,b.y,zb+1.10),.045,5))
        for at in pts[::2]:
            z=float(z_at([at.x],[at.y])[0]);eg['Metal'].append(cylinder((at.x,at.y,z-.08),(at.x,at.y,z+1.10),.035,5))
    for x,y in [(371.15,-579.23),(386.48,-584.27),(413.3,-620.0)]:
        bottom=float(ground(x,y))-.9;eg['BridgePier'].append(cylinder((x,y,bottom),(x,y,level-.38),.58,10))
    # Fifty-five source-mapped outdoor treads join the upper bridge to station grade.
    stair=next(f['poly']for f in osm if f['properties'].get('osm_id')=='way/393899772');a=np.array(stair.coords[0]);b=np.array(stair.coords[-1]);u=(b-a)/np.linalg.norm(b-a);v=np.array([-u[1],u[0]]);low=float(ground(*a))+.18;N=55
    strip=LineString([a,b]).buffer(1.8,cap_style=2);waist=extrusion(segmentize(strip,1.0),-.30,.30);t=np.clip((waist.vertices[:,:2]-a)@u/np.linalg.norm(b-a),0,1);waist.vertices[:,2]+=low+(level-low)*t;eg['Concrete'].append(waist)
    for i in range(N):
        front=a+(b-a)*i/N;back=a+(b-a)*(i+1)/N;q=Polygon([front-v*1.8,front+v*1.8,back+v*1.8,back-v*1.8]);z=low+(level-low)*(i+1)/N;add(eg,q,z-.16,.16,'StepStone')
    for side in [-1,1]:
        aa=a+v*side*1.73;bb=b+v*side*1.73;eg['Metal'].append(cylinder((*aa,low+1.05),(*bb,level+1.05),.045,6))
        for t in np.linspace(0,1,12):
            at=aa+(bb-aa)*t;z=low+(level-low)*t;eg['Metal'].append(cylinder((*at,z-.12),(*at,z+1.05),.035,5))
    plaza=p.buffer(6.0,join_style=2).difference(footprints).difference(plan).buffer(0);env(plaza,.18,.055,'Paving')
    for x in np.arange(400,430,3):env(LineString([(x,-696),(x,-628)]).buffer(.018).intersection(plaza),.237,.012,'StoneJoint')
    hit=unary_union([p,plan]);places.append({'id':'transit-uw-station','name':'University of Washington Station','name_zh':'华盛顿大学轻轨站','position':[414,-659,base+2],'hitArea':mapping(hit),'source':UW_STATION})
    REPORT.append({'facility_id':'UW_STATION_BRIDGE','source_ids':[f['properties']['osm_id']for f in fs],'deck_height_m':round(level,3),'connected_parts':len(polygons(plan)),'source_stair_treads':N,'plan_area_m2':round(plan.area,2),'note':'Mapped curved surface bridge, descending cycle ramp, outdoor stairs and ground-reaching piers; deck elevations are approximate exterior interpretation.'})

def write_transit_report():
    (OUT/'transit_refinement.json').write_text(json.dumps({'review_date':'2026-10-15','facilities':REPORT,'scope':'Surface exteriors, station entries, public approach and bridge; not underground railway engineering.','limits':'Mapped outlines and entrances are retained; heights, structural bay sizes, signage and furniture dimensions are approximate photo interpretations.'},ensure_ascii=False,indent=2)+'\n')
