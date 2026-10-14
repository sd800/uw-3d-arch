"""Exterior refinements for mapped Seattle core buildings; elevations are approximate."""
from cad_core import *

def oriented_roofs(ms,p,z,rise):
    corners=np.asarray(p.minimum_rotated_rectangle.exterior.coords)[:4];edges=np.roll(corners,-1,axis=0)-corners;u=edges[np.argmax(np.linalg.norm(edges,axis=1))];u/=np.linalg.norm(u);v=np.array([-u[1],u[0]]);c=p.centroid;cx,cy=c.x,c.y
    local=affinity.affine_transform(p,[u[0],u[1],v[0],v[1],-cx*u[0]-cy*u[1],-cx*v[0]-cy*v[1]])
    a,b,c,d=local.bounds;transform0=np.eye(4);transform0[:2,0]=u;transform0[:2,1]=v;transform0[:2,3]=[cx,cy]
    # Disjoint wing strips preserve courtyard voids and follow the building axis.
    if d-b<=32:pieces=[local]
    else:
        strips=[box(a-1,b-1,c+1,b+16),box(a-1,d-16,c+1,d+1),box(a-1,b+16,a+16,d-16),box(c-16,b+16,c+1,d-16)]
        pieces=[local.intersection(s) for s in strips];pieces.append(local.difference(unary_union(strips)))
    for part in pieces:
        for q in polygons(part):
            # Roof each narrow wing along its own long dimension.
            for mesh in pitched(q,z,rise):mesh.apply_transform(transform0);ms['Slate'].append(mesh)

def core_accents(ms,p,base,bodyheight,height,id,red_center):
    refined={'SUZ','GRB','MGH','SAV','RAI','SMI','GWN','MLR','MUS','HUT','THO','JHN','KNE','OUG','MNY','HUB'}
    if id not in refined:return False
    gothic=id in {'SUZ','GRB','MGH','SAV','RAI','SMI','GWN','MLR','MUS','HUT','THO','JHN'}
    # Stone sill/string courses follow the mapped perimeter, with no invented wing.
    for zz in ([base+bodyheight*.42,base+bodyheight*.72] if gothic else [base+bodyheight*.34,base+bodyheight*.68]):
        belt=p.buffer(.10,join_style=2).difference(p.buffer(-.09,join_style=2))
        for q in polygons(belt):ms['LightStone' if gothic else 'Frame'].append(extrusion(q,zz,.16))
    edges=[]
    for ring in polygons(p):
        for a,b in zip(np.asarray(ring.exterior.coords)[:-1],np.asarray(ring.exterior.coords)[1:]):
            edge=b-a;length=np.linalg.norm(edge)
            if length>9:edges.append((np.linalg.norm((a+b)/2-np.asarray(red_center)),a,b,length))
    if not edges:return True
    _,a,b,length=min(edges,key=lambda e:e[0]);u=(b-a)/length;n=np.array([u[1],-u[0]]);middle=(a+b)/2
    # Entrance identity and recessed doors make each core building readable.
    for offset in [-1.4,0,1.4]:
        c=middle+u*offset+n*.14
        pts=[c-u*.53,c+u*.53,c+u*.53+n*.14,c-u*.53+n*.14]
        ms['DarkGlass'].append(extrusion(Polygon(pts),base+.3,3.2 if gothic else 2.7))
    if gothic:
        for offset in [-2.2,2.2]:
            c=middle+u*offset+n*.22;pts=[c-u*.22-n*.35,c+u*.22-n*.35,c+u*.22+n*.35,c-u*.22+n*.35];ms['LightStone'].append(extrusion(Polygon(pts),base,4.0))
        c=middle+n*.24;pts=[c-u*2.5-n*.4,c+u*2.5-n*.4,c+u*2.5+n*.4,c-u*2.5+n*.4];ms['LightStone'].append(extrusion(Polygon(pts),base+3.7,.3))
    else:
        c=middle+n*1.15;pts=[c-u*5-n*1.6,c+u*5-n*1.6,c+u*5+n*1.6,c-u*5+n*1.6];ms['Metal'].append(extrusion(Polygon(pts),base+3.25,.22))
    if id=='SUZ':
        # Western reading-room front: tall grouped pointed bays over the entry.
        for _,a,b,length in sorted(edges,key=lambda e:e[0])[:2]:
            if length<20:continue
            u=(b-a)/length;n=np.array([u[1],-u[0]])
            for along in np.arange(5,length-3,5.2):
                c=a+u*along+n*.20
                for off in [-.75,0,.75]:
                    center=c+u*off;ww=.62;wh=11.5;outline=[(-ww/2,0),(ww/2,0),(ww/2,wh-1),(0,wh),(-ww/2,wh-1)]
                    m=trimesh.creation.extrude_polygon(Polygon(outline),.11,engine='earcut');vv=m.vertices.copy();m.vertices=np.column_stack((center[0]+vv[:,0]*u[0]+vv[:,2]*n[0],center[1]+vv[:,0]*u[1]+vv[:,2]*n[1],base+9+vv[:,1]));trimesh.repair.fix_normals(m);ms['DarkGlass'].append(m)
                for zz in [base+12,base+16,base+20]:ms['LightStone'].append(cylinder((c[0]-u[0]*1.1,c[1]-u[1]*1.1,zz),(c[0]+u[0]*1.1,c[1]+u[1]*1.1,zz),.055,4))
    if id=='OUG':
        # Shallow glazed atrium roof, clipped to the known plan outline.
        x,y=p.centroid.coords[0];sky=p.buffer(-6).intersection(box(x-10,y-8,x+10,y+8))
        for q in polygons(sky):
            ms['Frame'].append(extrusion(q,base+bodyheight+.23,.5));ms['Glass'].append(extrusion(q.buffer(-.25),base+bodyheight+.74,.12))
            for xx in np.arange(x-9,x+10,3):
                strip=box(xx-.07,y-8,xx+.07,y+8).intersection(q)
                for qq in polygons(strip):ms['Frame'].append(extrusion(qq,base+bodyheight+.87,.10))
    return True
