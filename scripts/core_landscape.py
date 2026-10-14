"""Detailed mapped core spaces; small elements and vertical dimensions are approximate."""
from cad_core import *
from shapely import segmentize

def _frame(p):
    corners=np.asarray(p.minimum_rotated_rectangle.exterior.coords)[:4]
    edges=np.roll(corners,-1,axis=0)-corners;u=edges[np.argmax(np.linalg.norm(edges,axis=1))];u/=np.linalg.norm(u)
    if u[1]<0:u=-u
    v=np.array([-u[1],u[0]]);cx,cy=p.centroid.coords[0]
    world=lambda q:affinity.affine_transform(q,[u[0],v[0],u[1],v[1],cx,cy])
    local=lambda q:affinity.affine_transform(q,[u[0],u[1],v[0],v[1],-cx*u[0]-cy*u[1],-cx*v[0]-cy*v[1]])
    return world,local

def core_plan(red,quad,osm,footprints):
    # OSM supplies one aligned set of walks here. Do not also overlay slightly
    # offset official centre lines: those created tiny triangular lawn slivers.
    mapped=[]
    for f in osm:
        g,t=f['poly'],f['properties']
        if g.geom_type in ['LineString','MultiLineString'] and t.get('highway') in ['footway','path','steps','pedestrian'] and g.intersects(quad):
            width=5.2 if t.get('name')=='Northeast Pierce Lane' else 3.0
            mapped.append(g.buffer(width/2,cap_style=2,join_style=2))
    paths=unary_union(mapped).union(quad.difference(quad.buffer(-1.8,join_style=2))).intersection(quad).difference(footprints.buffer(.25))
    # Follow the mapped Pierce Lane approach and the two mapped three-step
    # flights between Kane, Suzzallo and the southwest end of the Quad.
    approach=LineString([(43.7449,50.3506),(74.6727,86.1270),(76.8016,88.2355),(88.4659,99.7767),(89.7611,101.0665),(109.2188,120.3242)])
    connection=approach.buffer(4.1,cap_style=2,join_style=2).difference(footprints.buffer(.35)).difference(red).difference(quad)
    paths=paths.union(approach.buffer(2.6,cap_style=2,join_style=2).intersection(quad)).buffer(.16,join_style=2).buffer(-.16,join_style=2)
    grass=quad.difference(footprints).difference(paths)
    # Absorb sub-6m² remnants into the contiguous pavement, not extra lawn faces.
    small=unary_union([q for q in polygons(grass) if q.area<6])
    paths=paths.union(small);grass=grass.difference(small)
    steps=[f for f in osm if f['properties'].get('osm_id') in ['way/445396671','way/343612259']]
    return connection,paths,grass,steps

def detail_core(eg,env,red,quad,fountain,ground,footprints,plan):
    connection,paths,grass,steps=plan
    plaza=red.difference(footprints)
    stair_areas=unary_union([f['poly'].buffer(3.7,cap_style=2) for f in steps])
    def paving(q,base_material,offset=.26,cell=(3.6,1.8),tones=('BrickPale','BrickWarm')):
        if q.is_empty:return
        env(q,offset,.055,base_material)
        world,local=_frame(q);a,b,c,d=local(q).bounds;tiles=[[],[]]
        for j,yy in enumerate(np.arange(b,d,cell[1])):
            shift=(j%2)*cell[0]/2
            for k,xx in enumerate(np.arange(a-cell[0],c,cell[0])):
                piece=world(box(xx+shift+.025,yy+.02,xx+shift+cell[0]-.025,yy+cell[1]-.02)).intersection(q)
                if not piece.is_empty:tiles[(j+k)%2].append(piece)
        for material,parts in zip(tones,tiles):
            if parts:env(unary_union(parts),offset+.06,.018,material)
    paving(plaza,'Tile')
    world,local=_frame(plaza);a,b,c,d=local(plaza).bounds
    bands=unary_union([world(box(a-1,y-.10,c+1,y+.10)) for y in np.arange(b+8,d,12)]).intersection(plaza)
    env(bands,.34,.02,'BrickBand')
    env(plaza.difference(plaza.buffer(-.28,join_style=2)),.35,.06,'BrickBand')
    env(grass,.16,.05,'Grass')
    paving(paths.difference(stair_areas),'BrickPath',.29,(2.6,1.3),('BrickPath','BrickPath'))
    paving(connection.difference(stair_areas),'BrickPath',.29,(2.6,1.3),('BrickPath','BrickPath'))
    # Fine flush edging keeps the brick/grass boundary readable without a
    # second broad raised border competing with the mapped walks.
    kerb=paths.buffer(.12,join_style=2).difference(paths).intersection(quad).difference(footprints)
    env(kerb,.29,.035,'StoneEdge')
    for f in steps:
        line=f['poly'];a=np.asarray(line.coords[0]);b=np.asarray(line.coords[-1]);u=(b-a)/np.linalg.norm(b-a);v=np.array([-u[1],u[0]])
        count=int(f['properties'].get('step_count',3));run=np.linalg.norm(b-a)/count
        za=float(ground(*a))+.36;zb=max(za+.36,float(ground(*b))+.36)
        for i in range(count):
            start=a+u*run*i;end=a+u*run*(i+1)
            tread=Polygon([start-v*3.7,end-v*3.7,end+v*3.7,start+v*3.7]).difference(footprints)
            top=za+(zb-za)*(i+1)/count
            for q in polygons(tread):eg['StepStone'].append(extrusion(q,min(za,zb)-.5,top-min(za,zb)+.5))
    # Red Square's three brick monoliths and Broken Obelisk use mapped OSM points.
    for dx,dy,h in [(-2.0,-1.1,17),(1.6,-1.3,19),(.2,2.0,21)]:
        x,y=-40.366+dx,46.589+dy;z=float(ground(x,y));eg['Brick'].append(boxmesh(x,y,z+.2,1.7,1.7,h));eg['StoneEdge'].append(boxmesh(x,y,z+h+.2,1.8,1.8,.16))
    x,y=18.185,32.373;z=float(ground(x,y))+.65
    eg['StoneEdge'].append(boxmesh(x,y,z-.5,4.0,4.0,.45))
    pyramid=trimesh.creation.cone(radius=2.25,height=2.8,sections=4);pyramid.apply_transform(trimesh.transformations.rotation_matrix(math.pi/4,[0,0,1]));pyramid.apply_translation([x,y,z]);eg['Corten'].append(pyramid)
    # Inverted taper with an irregular broken crown, a schematic sculpture.
    bottom=[[x-.07,y-.07,z+2.78],[x+.07,y-.07,z+2.78],[x+.07,y+.07,z+2.78],[x-.07,y+.07,z+2.78]]
    top=[[x-1.1,y-1.1,z+7.6],[x+1.1,y-1.1,z+7.85],[x+1.1,y+1.1,z+7.3],[x-1.1,y+1.1,z+7.65]]
    faces=[[0,2,1],[0,3,2],[4,5,6],[4,6,7]]
    for i in range(4):j=(i+1)%4;faces.extend([[i,j,j+4],[i,j+4,i+4]])
    obelisk=trimesh.Trimesh(vertices=bottom+top,faces=faces,process=True);trimesh.repair.fix_normals(obelisk);assert obelisk.is_watertight;eg['Corten'].append(obelisk)
    # Flat water in the actual approximately 59m mapped basin, with a double rim.
    c=fountain.centroid;cx,cy=c.x,c.y;z=float(ground(cx,cy));basin_radius=math.sqrt(fountain.area/math.pi)
    water=fountain.buffer(-.55);env(water,z+.28,.08,'PoolWater',False)
    for outer,inner,top,h in [(fountain.buffer(.55),fountain.buffer(-.4),.02,.58),(fountain.buffer(.65),fountain.buffer(-.52),.58,.16)]:
        for q in polygons(outer.difference(inner)):eg['StoneEdge'].append(extrusion(segmentize(q,2.5),z+top,h))
    ringwalk=fountain.buffer(3.8).difference(fountain.buffer(.8)).difference(footprints)
    env(ringwalk,.21,.09,'Paving')
    # Radial coping joints are solid edge pieces, avoiding coplanar overlays.
    for angle in np.linspace(0,2*math.pi,72,endpoint=False):
        a=(cx+(basin_radius-.48)*math.cos(angle),cy+(basin_radius-.48)*math.sin(angle),z+.76)
        b=(cx+(basin_radius+.5)*math.cos(angle),cy+(basin_radius+.5)*math.sin(angle),z+.76)
        eg['StoneJoint'].append(cylinder(a,b,.024,4))
    # A readable central plume, surrounding arced jets and restrained splash
    # rings follow the official fountain photo. Static geometry avoids shimmer.
    def tube(coords,radius,material='Spray'):
        for a,b in zip(coords[:-1],coords[1:]):eg[material].append(cylinder(a,b,radius,8))
    def ring(x,y,rad,height,thickness,material='Foam'):
        pts=[(x+rad*math.cos(a),y+rad*math.sin(a),height) for a in np.linspace(0,math.tau,49)]
        tube(pts,thickness,material)
    def jet(start,end,height,thickness):
        coords=[]
        for t in np.linspace(0,1,19):coords.append((start[0]*(1-t)+end[0]*t,start[1]*(1-t)+end[1]*t,z+.42+4*height*t*(1-t)))
        tube(coords,thickness)
    eg['StoneJoint'].append(cylinder((cx,cy,z+.35),(cx,cy,z+.56),1.0,24))
    # Several offset tapering streams give the centre volume and a soft crown
    # instead of a single rigid pole. All remain on the Environment layer.
    # A closed, sculpted water volume gives the centre a legible silhouette
    # in the campus view; fine streams alone disappear at this map scale.
    vertices=[];faces=[];sections=32
    for j,(height,width) in enumerate([(0,1.9),(.8,1.25),(3,1.05),(6,1.12),(9,1.25),(12,1.40),(14.5,1.48),(16,1.27),(17,1.0),(17.7,.62),(18.05,.20)]):
        for k in range(sections):
            a=k*math.tau/sections;w=width*(1+.055*math.sin(a*5+j*.42)+.035*math.cos(a*3-j*.3))
            vertices.append([cx+w*math.cos(a)+.12*math.sin(height*.4),cy+w*math.sin(a),z+.47+height])
    levels=len(vertices)//sections
    for j in range(levels-1):
        for k in range(sections):
            a=j*sections+k;b=j*sections+(k+1)%sections;c=b+sections;d=a+sections
            faces.extend([[a,b,c],[a,c,d]])
    for k in range(1,sections-1):faces.extend([[0,k+1,k],[(levels-1)*sections,(levels-1)*sections+k,(levels-1)*sections+k+1]])
    plume=trimesh.Trimesh(vertices=vertices,faces=faces,process=True);trimesh.repair.fix_normals(plume);assert plume.is_watertight;eg['Foam'].append(plume)
    rng=np.random.default_rng(1909)
    for i in range(8):
        angle=i*math.tau/8;spread=rng.uniform(.95,1.45);height=rng.uniform(12.8,17.5)
        coords=[]
        for t in np.linspace(0,1,15):
            radius=spread*(.45+1.1*t);coords.append((cx+radius*math.cos(angle)+.12*math.sin(t*6+i),cy+radius*math.sin(angle),z+.5+height*t))
        tube(coords,.24 if i%3 else .30,'Foam' if i%3==0 else 'Spray')
    for i in range(12):
        a=i*math.tau/12;nozzle=(cx+6.0*math.cos(a),cy+6.0*math.sin(a));landing=(cx+10.2*math.cos(a),cy+10.2*math.sin(a))
        eg['StoneJoint'].append(cylinder((nozzle[0],nozzle[1],z+.36),(nozzle[0],nozzle[1],z+.72),.12,8))
        jet(nozzle,landing,3.6,.25)
        ring(*landing,.78,z+.50,.12)
    for radius0 in [1.5,2.1,2.9]:ring(cx,cy,radius0,z+.50,.13)
    # A few concentric pale-blue ripples communicate a horizontal water plane.
    for radius0 in [11.8,15.2,19.3]:ring(cx,cy,radius0,z+.40,.028,'Ripple')
    report={'red_square':{'mapped_area_m2':round(plaza.area,2),'details':['axis-aligned brick panels and bands','continuous Pierce Lane approach and two mapped three-step flights','three brick monoliths','Broken Obelisk schematic at mapped point']},'quad':{'mapped_area_m2':round(quad.area,2),'mapped_lawn_panels':len(polygons(grass)),'connection_area_m2':round(connection.area,2),'mapped_step_flights':len(steps),'details':['mapped brick cross/diagonal walks','lawn edges','original simple faceted cherry canopies at mapped Yoshino positions']},'fountain':{'mapped_basin_area_m2':round(fountain.area,2),'mapped_diameter_m':round(2*basin_radius,2),'details':['flat water plane','double coping rim','radial coping joints','volumetric central plume, twelve arced jets, splash rings and ripples'],'central_plume_illustrative_height_m':18,'arc_stream_illustrative_diameter_m':.5,'jet_height_status':'Illustrative water display, not surveyed or an operational prediction'},'accuracy':'Mapped footprints and tree positions; paving panel size, sculpture details, steps, coping sections and jets are exterior approximations.'}
    (OUT/'core_landscape_geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

