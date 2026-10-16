"""Coherent mapped pedestrian edges around Central Plaza; exterior approximation."""
from cad_core import *
from shapely import segmentize

FRONTAGES={'KNE','OUG','MNY','GRB'}

def connection_plan(red,osm,footprints,buildings,excluded):
    walks=[];stairs=[];source_ids=[]
    for f in osm:
        g,t=f['poly'],f['properties']
        if g.geom_type!='LineString' or t.get('highway')not in ['footway','path','pedestrian','steps']:continue
        if t.get('tunnel')=='yes' or t.get('layer')=='-1' or g.distance(red)>.7:continue
        if t.get('osm_id')=='way/1106705315':continue
        if t.get('highway')=='steps':
            if g.distance(excluded)<.2:continue
            stairs.append(f)
        try:width=float(t.get('width',3.0))
        except (ValueError,TypeError):width=3.0
        walks.append(g.buffer(width/2,cap_style=2,join_style=2).intersection(red.buffer(14)))
        source_ids.append(t.get('osm_id'))
    # Close the narrow GIS seam at plaza edges, without spreading brick over
    # adjacent lawns or creating another offset network of paths.
    apron=red.buffer(.85,join_style=2).difference(red)
    fronts=[]
    for f in buildings:
        if f['id']not in FRONTAGES:continue
        p=f['poly'];cc=np.asarray(p.exterior.coords)
        for a,b in zip(cc[:-1],cc[1:]):
            edge=LineString([a,b])
            if edge.length>5 and edge.distance(red)<8:
                fronts.append(edge.buffer(2.0,cap_style=2,join_style=2).intersection(red.buffer(10)))
    domain=unary_union([apron,*walks,*fronts]).difference(red).difference(footprints.buffer(.025)).difference(excluded)
    domain=domain.buffer(.12,join_style=2).buffer(-.12,join_style=2)
    domain=unary_union([q for q in polygons(domain)if q.area>.5])
    return {'domain':domain,'stairs':stairs,'source_ids':source_ids}

def frontage_grade(buildings,x,y,z):
    # The original 10 m DEM cannot resolve the short entrance shelves.
    # Blend each existing grade into adjacent paving before meshing it.
    xy=np.column_stack((np.asarray(x).ravel(),np.asarray(y).ravel()));zz=np.asarray(z).ravel()
    for f in buildings:
        if f['id']not in FRONTAGES:continue
        p=f['poly'];aa,bb,cc,dd=p.buffer(2.0).bounds
        ids=np.flatnonzero((xy[:,0]>=aa)&(xy[:,0]<=cc)&(xy[:,1]>=bb)&(xy[:,1]<=dd))
        for k in ids:
            d=p.distance(Point(*xy[k]))
            if d<2:
                t=np.clip(d/2,0,1);t=t*t*(3-2*t)
                zz[k]=f['ground']*(1-t)+zz[k]*t
    return zz.reshape(np.asarray(z).shape)

def build_connections(eg,env,plan,ground,footprints,excluded):
    domain=plan['domain'];flights=[]
    stair_masks=[]
    for f in plan['stairs']:
        line=f['poly'];a=np.asarray(line.coords[0]);b=np.asarray(line.coords[-1]);u=(b-a)/np.linalg.norm(b-a);v=np.array([-u[1],u[0]])
        za=float(ground(*a))+.34;zb=float(ground(*b))+.34
        # If the DEM does not resolve a rise, keep a connected sloped walk,
        # rather than forcing a fictitious step up at the far endpoint.
        if abs(za-zb)<.20:continue
        N=int(f['properties'].get('step_count',max(2,round(abs(zb-za)/.16))))
        width=3.0;mask=line.buffer(width/2,cap_style=2).difference(footprints).difference(excluded)
        stair_masks.append(mask)
        probes=[]
        for i in range(N):
            at=a+(b-a)*i/N;end=a+(b-a)*(i+1)/N
            q=Polygon([at-v*width/2,end-v*width/2,end+v*width/2,at+v*width/2]).intersection(mask)
            top=za+(zb-za)*((i+1)/N if zb>=za else i/N)
            for p in polygons(q):eg['StepStone'].append(extrusion(p,min(za,zb)-.65,top-min(za,zb)+.65))
            probes.append([*map(float,(at+end)/2),top])
        for side in [-1,1]:
            aa=a+v*side*(width/2-.1);bb=b+v*side*(width/2-.1)
            eg['Metal'].append(cylinder((*aa,za+.90),(*bb,zb+.90),.035,5))
            for t in np.linspace(0,1,4):
                at=aa+(bb-aa)*t;z=za+(zb-za)*t
                eg['Metal'].append(cylinder((*at,z-.1),(*at,z+.9),.03,5))
        flights.append({'osm_id':f['properties']['osm_id'],'steps':N,'count_status':'mapped'if f['properties'].get('step_count')else'estimated from graded endpoints','probes':probes})
    pavement=domain.difference(unary_union(stair_masks))
    env(pavement,.29,.055,'BrickPath')
    # Single flush stone margin, clipped clear of walking routes and buildings.
    edge=domain.difference(domain.buffer(-.14,join_style=2)).difference(unary_union(stair_masks))
    env(edge,.35,.025,'StoneEdge')
    report={'source_ids':plan['source_ids'],'mapped_connection_area_m2':round(domain.area,2),'frontages':sorted(FRONTAGES),'steps':flights,'domain':mapping(domain),'details':['Mapped pedestrian corridors retained around all sides of Red Square','Narrow plaza-edge seams closed; tiny slivers and duplicate surface skins removed','Kane, Odegaard, Meany and Gerberding entrance shelves meet surrounding paving','Endpoint-fitted stair flights and grounded handrails'],'limits':'Mapped paths and footprints; paving margins, member dimensions, ground interpolation and untagged stair counts are exterior approximations.'}
    (OUT/'red_square_connections.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
