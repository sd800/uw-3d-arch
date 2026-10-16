"""West gatehouse from UW GIS and Transportation Services' exterior photograph.

Keep the mapped GH5 position. Heights and the small traffic island are
photo-interpreted, not a measured survey. No generic full-storey service box.
"""
from cad_core import *

PHOTO='https://transportation.uw.edu/files/media/west-gatehouse-525x384.jpg'
LANE_WIDTHS={'way/361455661':3.6,'way/361455663':6.2,'way/459082636':6.2}
REPORT={}

def gate_lane_width(tags,default):
    # These are two separate one-way carriageways, not two full 9 m roads.
    return LANE_WIDTHS.get(tags.get('osm_id'),default)

def island_plan(osm,footprint):
    roads={f['properties'].get('osm_id'):f['poly'] for f in osm}
    south=roads['way/361455661'];turn=roads['way/459082636'];north=roads['way/361455663']
    ring=Polygon([*south.coords,*list(turn.coords)[1:],*list(north.coords)[1:]])
    lanes=unary_union([roads[k].buffer(w/2,cap_style=2,join_style=2) for k,w in LANE_WIDTHS.items()])
    clear=ring.difference(lanes).buffer(0)
    # Retain the component containing the surveyed booth; do not scatter tiny
    # residual pieces at the converging ends of the carriageways.
    island=max(polygons(clear),key=lambda q:q.intersection(footprint).area)
    assert island.buffer(.08).covers(footprint), 'Gatehouse must fit its traffic island'
    REPORT['island']=mapping(island);REPORT['island_area_m2']=round(island.area,3)
    return island

def build_gatehouse(ms,p,base,code,lay,info):
    body=2.58;rise=.38
    native_extrude(p,base,body,code+'_Booth',lay,'HousingCharcoal',info)
    ms['HousingCharcoal'].append(extrusion(p,base,body))
    for q in polygons(p.buffer(.12,join_style=2)):
        ms['Precast'].append(extrusion(q,base,.16))
    for ring in [p.exterior]:
        cc=np.asarray(orient(p,1).exterior.coords)
        for a,b in zip(cc[:-1],cc[1:]):
            length=np.linalg.norm(b-a);u=(b-a)/length;n=np.array([u[1],-u[0]])
            def strip(start,end,offset,depth,z,h,mat):
                q=Polygon([a+u*start+n*offset,a+u*end+n*offset,a+u*end+n*(offset+depth),a+u*start+n*(offset+depth)])
                ms[mat].append(extrusion(q,base+z,h))
            # Continuous glass observation/counter band, with real supported
            # corner posts and discrete mullions instead of opaque white walls.
            strip(.12,length-.12,.035,.055,1.08,1.27,'DarkGlass')
            for x in np.linspace(.08,length-.08,max(2,round(length/1.15)+1)):
                strip(max(.005,x-.035),min(length-.005,x+.035),.10,.055,.16,2.39,'HousingCharcoal')
            strip(.05,length-.05,.10,.10,1.00,.08,'Precast')
            strip(.05,length-.05,.10,.10,2.36,.10,'HousingCharcoal')
            strip(.14,length-.14,.105,.035,.69,.25,'Purple')
            if length>2.8:
                # Glazed service door on the long roadside elevation.
                mid=length*.72;strip(mid-.37,mid+.37,.165,.045,.18,2.12,'DarkGlass')
                strip(mid-.41,mid-.35,.215,.045,.16,2.22,'HousingCharcoal')
                strip(mid+.35,mid+.41,.215,.045,.16,2.22,'HousingCharcoal')
                strip(mid-.41,mid+.41,.215,.045,2.32,.06,'HousingCharcoal')
    corners=np.asarray(p.minimum_rotated_rectangle.exterior.coords)[:4]
    edges=np.roll(corners,-1,axis=0)-corners;u=edges[np.argmax(np.linalg.norm(edges,axis=1))];u/=np.linalg.norm(u);v=np.array([-u[1],u[0]]);c=np.array(p.centroid.coords[0])
    local=affinity.affine_transform(p.buffer(.22,join_style=2),[u[0],u[1],v[0],v[1],-c@u,-c@v]);t=np.eye(4);t[:2,0]=u;t[:2,1]=v;t[:2,3]=c
    for m in pitched(local,base+body,rise,'x'):
        m.apply_transform(t);ms['RoofMetal'].append(m)
    details=['Official GH5 footprint and mapped traffic-island location retained','Single-storey dark-framed glazed observation booth, counter sill, roadside doors and purple lower sign bands','Low shallow gabled metal roof; no generic tall service-box parapet']
    REPORT.update({'facility_id':'GH5','height_m':3.08,'body_height_m':body,'source_photo':PHOTO,'lane_widths_m':LANE_WIDTHS,'details':details,'accuracy':'Mapped booth position; exterior heights, lane widths and island curbs are photo-informed approximations.'})
    return {'height_m':3.08,'levels':1,'volume_parts':[{'area_m2':round(p.area,3),'height_m':body,'material':'HousingCharcoal'}],'details':details}

def gatehouse_landscape(eg,env,p,island,ground):
    # A connected curbed island and low brick planter explain why the real
    # booth sits between the two traffic directions.
    env(island.difference(p),.14,.10,'Paving')
    curb=island.difference(island.buffer(-.16,join_style=2)).difference(p)
    env(curb,.24,.11,'Concrete')
    c=np.array(p.centroid.coords[0]);cs=np.asarray(p.minimum_rotated_rectangle.exterior.coords)[:4];es=np.roll(cs,-1,axis=0)-cs;u=es[np.argmax(np.linalg.norm(es,axis=1))];u/=np.linalg.norm(u)
    if u[0]<0:u=-u
    bed=LineString([c-u*2.8,c-u*8.0]).buffer(.74,cap_style=2).intersection(island.buffer(-.28)).difference(p.buffer(.28))
    if not bed.is_empty:
        env(bed,.25,.18,'Garden');wall=bed.buffer(.12,join_style=2).difference(bed.buffer(-.10,join_style=2))
        env(wall,.24,.58,'BrickRed');env(wall.buffer(.045,join_style=2),.82,.09,'RoofSlate')
    (OUT/'gatehouse_refinement.json').write_text(json.dumps(REPORT,indent=2)+'\n')
