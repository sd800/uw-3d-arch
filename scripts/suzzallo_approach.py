"""Photo-referenced west terrace and broad entrance stair in mapped metres."""
from cad_core import *
from shapely import segmentize
STAIR_ID='way/1106705315'

def reading_envelope(library):
    return library.intersection(Polygon([(40,-29),(54,43),(72,40),(57,-34)]))

def entry_plan(osm,library,raw_ground):
    feature=next(f for f in osm if f['properties'].get('osm_id')==STAIR_ID)
    line=feature['poly'];a=np.asarray(line.coords[0]);b=np.asarray(line.coords[-1])
    u=(b-a)/np.linalg.norm(b-a);v=np.array([-u[1],u[0]])
    world=lambda p:affinity.affine_transform(p,[u[0],v[0],u[1],v[1],*a])
    local=lambda p:affinity.affine_transform(p,[u[0],u[1],v[0],v[1],-a@u,-a@v])
    reading=reading_envelope(library)
    crossing=reading.intersection(LineString([a,a+u*30]));head=local(crossing).bounds[0]
    # The tagged centreline is a route to the landing, not the entire run or
    # width of the physical stair. Photos show a short broad flight below a
    # continuous terrace spanning the Gothic west front.
    L=line.length;run=4.5;start=L-run;count=int(feature['properties']['step_count'])
    lower=float(raw_ground(*a))+.333;upper=lower+count*.16
    front=[]
    for q in polygons(reading):
        cc=np.asarray(q.exterior.coords)
        for aa,bb in zip(cc[:-1],cc[1:]):
            edge=bb-aa;n=np.array([edge[1],-edge[0]])/np.linalg.norm(edge)
            if n[0]<-.8 and np.linalg.norm(edge)>50:front.extend([aa,bb])
    across=(np.asarray(front)-a)@v;lo=float(across.min()+1.5);hi=float(across.max()-1.5)
    terrace=world(box(L,lo,head+2,hi)).difference(library)
    flight=world(Polygon([(start,-12.2),(start,12.2),(L,10.8),(L,-10.8)]))
    ramp=world(box(L-2.2,11.4,L,hi+2))
    # Resolve the full forecourt, including both stair flanks. Leaving only
    # a narrow rectangular bottom landing exposes unrelated lawn/road skins
    # in the wedges between the flight and the raised terrace.
    apron=world(box(-4,lo-.5,L,hi+2)).difference(unary_union([flight,ramp,terrace])).difference(library)
    domain=unary_union([terrace,flight,apron,ramp]).difference(library)
    return dict(a=a,u=u,v=v,length=L,run=run,start=start,head=head,lower=lower,upper=upper,count=count,world=world,local=local,domain=domain,base=upper-.12,terrace=terrace,flight=flight,apron=apron,span=(lo,hi),ramp=ramp)

def approach_grade(plan,x,y,z):
    xy=np.column_stack((np.asarray(x).ravel(),np.asarray(y).ravel()));zz=np.asarray(z).ravel()
    local=xy-plan['a'];along=local@plan['u'];across=local@plan['v'];lo,hi=plan['span']
    aa,bb,cc,dd=plan['domain'].buffer(2).bounds
    ids=np.flatnonzero((xy[:,0]>=aa)&(xy[:,0]<=cc)&(xy[:,1]>=bb)&(xy[:,1]<=dd))
    for k in ids:
        pt=Point(*xy[k]);distance=plan['domain'].distance(pt)
        if distance>=2:continue
        t=0.0
        # Shared apron/terrace vertices belong to the lower forecourt.
        # Otherwise terrain interpolation lifts the paving into a wedge.
        if plan['apron'].distance(pt)<.08:t=0.0
        elif plan['terrace'].covers(pt):t=1.0
        elif plan['flight'].covers(pt):t=np.clip((along[k]-plan['start'])/plan['run'],0,1)
        elif plan['ramp'].covers(pt):t=np.clip((hi+2-across[k])/(hi+2-11.4),0,1)
        q=plan['lower']+(plan['upper']-plan['lower'])*t-.338
        blend=1-np.clip(distance/2,0,1);blend=blend*blend*(3-2*blend)
        zz[k]=zz[k]*(1-blend)+q*blend
    return zz.reshape(np.asarray(z).shape)

def build_approach(eg,plan,footprints,env):
    w=plan['world'];L=plan['length'];S=plan['start'];low=plan['lower'];high=plan['upper'];N=plan['count'];head=plan['head'];lo,hi=plan['span']
    def add(g,z,h,mat):
        for q in polygons(g.difference(footprints)):eg[mat].append(extrusion(q,z,h))
    # Separate level assemblies for the terrace and the lower apron. Draped
    # thin skins interpolated across the two datums produced white triangular
    # slab exposures; each finished surface now has one explicit top datum.
    add(plan['terrace'],low-.75,high-low+.67,'SuzzalloStone')
    add(plan['terrace'],high-.08,.08,'BrickWarm')
    threshold=plan['terrace'].intersection(w(box(head-1.0,lo,head+2,hi)))
    add(threshold,high,.035,'SuzzalloStone')
    add(plan['apron'],low-.40,.40,'Tile')
    for region,z in [(plan['apron'],low),(plan['terrace'].difference(threshold),high)]:
        aa,bb,cc,dd=plan['local'](region).bounds;tiles=[[],[]]
        for j,yy in enumerate(np.arange(bb,dd,1.8)):
            for k,xx in enumerate(np.arange(aa-3.6,cc,3.6)):
                shift=(j%2)*1.8
                q=w(box(xx+shift+.025,yy+.02,xx+shift+3.575,yy+1.78)).intersection(region)
                if not q.is_empty:tiles[(j+k)%2].append(q)
        for mat,parts in zip(['BrickPale','BrickWarm'],tiles):
            if parts:add(unary_union(parts),z,.018,mat)
    probes=[]
    for i in range(N):
        x0=S+i*plan['run']/N;x1=S+(i+1)*plan['run']/N;w0=12.2-1.4*i/N;w1=12.2-1.4*(i+1)/N;top=low+(high-low)*(i+1)/N
        add(w(Polygon([(x0,-w0),(x0,w0),(x1,w1),(x1,-w1)])),low-.75,top-low+.75,'Concrete')
        c=plan['a']+plan['u']*((x0+x1)/2);probes.append([*map(float,c),top])
    # Closed stone cheeks follow both flared stair edges and join the
    # terrace balustrades. Their lower sides meet the continuous forecourt.
    for sign in [-1,1]:
        q=w(Polygon([(S,sign*12.2),(L,sign*10.8),(L,sign*11.12),(S,sign*12.52)]))
        for part in polygons(q):
            m=extrusion(part,low-.5,.65);top=m.vertices[:,2]>low
            xx=(m.vertices[:,:2]-plan['a'])@plan['u'];t=np.clip((xx-S)/plan['run'],0,1)
            m.vertices[top,2]+=t[top]*(high-low);trimesh.repair.fix_normals(m);eg['Concrete'].append(m)
    # Slim four-part rail sets divide the flight into three portal lanes.
    for y in [-10,-3.4,3.4,10]:
        aa=plan['a']+plan['u']*(S-.35)+plan['v']*y;bb=plan['a']+plan['u']*(L+.55)+plan['v']*y
        for h in [.62,.96]:eg['Frame'].append(cylinder((*aa,low+h),(*bb,high+h),.035,6))
        for t in np.linspace(0,1,6):
            c=aa+(bb-aa)*t;x=(c-plan['a'])@plan['u']
            step=np.clip(math.floor((x-S)/plan['run']*N)+1,0,N)
            z=low+(high-low)*step/N;rail=low+(high-low)*t+.96
            eg['Frame'].append(cylinder((*c,z-.06),(*c,rail),.035,6))
    # Low open stone balustrade on both terrace wings; central arrival open.
    for y0,y1 in [(lo,-10.96),(10.96,hi)]:
        band=w(box(L-.24,y0,L+.24,y1));add(band,high,.22,'Concrete');add(band,high+.94,.15,'LightStone')
        for yy in np.arange(y0+.35,y1-.2,.43):add(w(box(L-.12,yy-.06,L+.12,yy+.06)),high+.22,.72,'LightStone')
        for yy in [y0,y1]:add(w(box(L-.32,yy-.30,L+.32,yy+.30)),high,1.10,'Concrete')
    # School-documented ramp access to the west terrace. This is a visual
    # interpretation of the side route, not a certified accessibility slope.
    for q in polygons(segmentize(plan['ramp'],1.2)):
        m=extrusion(q,low-.65,.65);top=m.vertices[:,2]>low-.3
        yy=(m.vertices[:,:2]-plan['a'])@plan['v'];t=np.clip((hi+2-yy)/(hi+2-11.4),0,1)
        m.vertices[top,2]+=t[top]*(high-low);trimesh.repair.fix_normals(m);eg['Concrete'].append(m)
    for x in [L-2.05,L-.2]:
        aa=plan['a']+plan['u']*x+plan['v']*(hi+2);bb=plan['a']+plan['u']*x+plan['v']*11.4
        eg['Frame'].append(cylinder((*aa,low+.95),(*bb,high+.95),.034,6))
        for t in np.linspace(0,1,12):
            c=aa+(bb-aa)*t;z=low+(high-low)*t;eg['Frame'].append(cylinder((*c,z-.10),(*c,z+.95),.032,5))
    forecourt_probes=[]
    for x,y in [(S-.45,0),((S+L)/2,-14),((S+L)/2,15)]:
        pt=w(Point(x,y))
        if plan['apron'].covers(pt):forecourt_probes.append([pt.x,pt.y,low])
    result={'forecourt_probes':forecourt_probes,'level_terrace_and_apron':True,'brick_terrace':True,'flush_brick_apron':True,'closed_stair_cheeks':True,'source':'https://www.openstreetmap.org/way/1106705315','photographic_references':['https://www.gly.com/uw-seismic-improvements','https://uw.pressbooks.pub/uwlibrariestour/chapter/suzzallo-library-4/'],'step_count':N,'mapped_route_length_m':round(L,3),'run_m':plan['run'],'stair_width_bottom_m':24.4,'stair_width_top_m':21.6,'terrace_frontage_m':round(hi-lo,3),'estimated_riser_m':.16,'lower_landing_m':round(low,3),'upper_landing_m':round(high,3),'library_grade_m':round(plan['base'],3),'upper_landing_depth_m':round(head-L,3),'tread_probes':probes,'domain':mapping(plan['domain']),'limits':'OSM maps the route and count; its route width is not the full stair/terrace width. Broad stair, continuous brick/stone terrace, balustrade and north side ramp interpreted from photos. Secondary dimensions and grades are approximate, not surveyed.'}
    (OUT/'suzzallo_entry_refinement.json').write_text(json.dumps(result,indent=2)+'\n');return result
