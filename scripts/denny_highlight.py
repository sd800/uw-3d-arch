"""Denny Hall roof, dormers and open copper cupola from UW's historic addendum.
The GIS plan is retained; section levels and member sizes are exterior estimates.
"""
from cad_core import *
REFERENCE='https://facilities.uw.edu/files/media/denny-hall-hra.pdf'
FEATURES=['high hipped slate roofs on the main block and rear ell','separate low semi-elliptical side wings','three stone wall dormers and central clock','twin conical entrance towers','three open entrance porch arches and connected stairs','open copper cupola with domed crown and small lantern']
def build_denny(ms,p,base,body,ground):
 from architecture_refinement import window,courses,supported_entry
 u=np.array([.712,.702]);u/=np.linalg.norm(u);v=np.array([-u[1],u[0]]);o=np.array(p.centroid.coords[0])
 world=lambda q:affinity.affine_transform(q,[u[0],v[0],u[1],v[1],*o])
 local=lambda q:affinity.affine_transform(q,[*u,*v,-o@u,-o@v])
 lp=local(p);main=lp.intersection(box(-26.5,-30,26.8,6.15));rear=lp.intersection(box(-9.2,6.15,9.3,34));sides=lp.difference(unary_union([main,rear]))
 def add(q,z,h,mat):
  for pp in polygons(world(q)):ms[mat].append(extrusion(pp,base+z,h))
 def hip(q,z,rise,mat='RoofSlate'):
  for pp in polygons(q):
   a,b,c,d=pp.bounds;rx=min((c-a)/2,(d-b)/2);ym=(b+d)/2;xm=(a+c)/2
   # Rotate a tall rear wing locally so the ridge follows the wing axis.
   turn=d-b>c-a
   if turn:pp=affinity.rotate(pp,90,origin=(xm,ym));a,b,c,d=pp.bounds
   ym=(b+d)/2;rx=min((c-a)/2,(d-b)/2)
   faces=[[(a,b),(c,b),(c-rx,ym),(a+rx,ym)],[(a,d),(a+rx,ym),(c-rx,ym),(c,d)],[(a,b),(a+rx,ym),(a,d)],[(c,b),(c,d),(c-rx,ym)]]
   for face in faces:
    for part in polygons(pp.intersection(Polygon(face))):
     m=extrusion(part,base+z,.16);top=m.vertices[:,2]>base+z+.08;vv=m.vertices[top];m.vertices[top,2]+=rise*np.clip(np.minimum(1-np.abs(vv[:,1]-ym)/max((d-b)/2,.1),np.minimum(vv[:,0]-a,c-vv[:,0])/max(rx,.1)),0,1)
     if turn:m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[0,0,1],point=[xm,(b+d)/2,0]))
     xy=m.vertices[:,:2];m.vertices[:,:2]=o+xy[:,0,None]*u+xy[:,1,None]*v;trimesh.repair.fix_normals(m);ms[mat].append(m)
 def profile(q,c,zz,depth,mat):
  for pp in polygons(q):
   m=extrusion(pp,0,depth);vv=m.vertices.copy();cc=o+u*c[0]+v*c[1];m.vertices=np.column_stack([cc[0]+u[0]*vv[:,0]-v[0]*vv[:,2],cc[1]+u[1]*vv[:,0]-v[1]*vv[:,2],base+zz+vv[:,1]]);trimesh.repair.fix_normals(m);ms[mat].append(m)
 body(world(main),14.2,'DennySandstone',3,'denny');body(world(rear),14.2,'DennySandstone',3,'denny');body(world(sides),7.2,'DennySandstone',1,'denny')
 hip(main,14.2,5.8);hip(rear,14.2,5.8);hip(sides,7.2,1.2)
 for xx in [-11.7,11.7]:
  q=Point(xx,-17.1).buffer(3.25,quad_segs=24).intersection(lp.buffer(.05));add(q,14.2,2.0,'DennySandstone');at=o+u*xx+v*-17.1
  cone=trimesh.creation.cone(radius=3.3,height=5.0,sections=32);cone.apply_translation([*at,base+16.2]);ms['RoofSlate'].append(cone)
 # Three attached masonry dormers pierce the high main roof.
 for xx,ww,hh in [(-20,4.5,4.2),(0,5.4,5.4),(20,4.5,4.2)]:
  cap=Polygon([(-ww/2,0),(ww/2,0),(ww/2,hh*.57),(ww*.28,hh*.86),(0,hh),(-ww*.28,hh*.86),(-ww/2,hh*.57)])
  profile(cap,(xx,-16.4),14.0,.9,'DennySandstone');cc=o+u*xx+v*-16.55
  if xx:window(ms,cc,u,-v,base+14.55,1.9,2.8,'round','LightStone',1)
  else:
   disk=Point(0,0).buffer(1.25,quad_segs=32);profile(disk,(xx,-17.35),16.7,.10,'DarkGlass')
   ring=disk.difference(Point(0,0).buffer(1.15,quad_segs=32));profile(ring,(xx,-17.49),16.7,.10,'LightStone')
   for end in [(0,.86),(-.71,.39)]:profile(LineString([(0,0),end]).buffer(.055,cap_style=2),(0,-17.61),16.7,.07,'LightStone')
 # Three true open porch arches stand ahead of the recessed doors.
 outer=box(-8.9,0,8.9,4.5);holes=[]
 for xx in [-5.7,0,5.7]:holes.append(unary_union([box(xx-2.15,0,xx+2.15,2.0),Point(xx,2.0).buffer(2.15,quad_segs=20)]))
 profile(outer.difference(unary_union(holes)),(0,-19.0),.98,.65,'DennySandstone');add(box(-8.9,-19,-8.25,-16.3),.98,4.5,'DennySandstone');add(box(8.25,-19,8.9,-16.3),.98,4.5,'DennySandstone');add(box(-8.9,-19.1,8.9,-16.0),5.48,.23,'LightStone')
 for k in range(7):add(box(-9.0,-22.0+k*.36,9.0,-18.25),-.10,(k+1)*.14+.10,'LightStone')
 # Copper observation platform, open colonnade, domed crown and lantern.
 cx,cy=0,-5.2;cp=o+u*cx+v*cy;add(Point(cx,cy).buffer(3.35,quad_segs=2),20.05,.22,'RoofPatina')
 for angle in np.arange(8)*math.tau/8:
  at=cp+np.array([math.cos(angle),math.sin(angle)])*2.12
  ms['RoofPatina'].append(cylinder((*at,base+20.28),(*at,base+22.55),.13,8))
  ms['RoofPatina'].append(cylinder((*at,base+20.28),(*at,base+20.58),.24,8))
 # A revolved closed cap replaces the old slate cone.
 dome=trimesh.creation.revolve(np.array([[0,0],[2.55,0],[2.48,.50],[2.15,1.1],[1.5,1.65],[.62,1.88],[0,1.93]]),sections=40);dome.apply_translation([*cp,base+22.55]);ms['RoofPatina'].append(dome)
 for angle in np.arange(6)*math.tau/6:
  at=cp+np.array([math.cos(angle),math.sin(angle)])*.48;ms['RoofPatina'].append(cylinder((*at,base+24.48),(*at,base+25.35),.06,6))
 cap=trimesh.creation.cone(radius=.72,height=.72,sections=24);cap.apply_translation([*cp,base+25.35]);ms['RoofPatina'].append(cap)
 ms['RoofPatina'].append(cylinder((*cp,base+26.07),(*cp,base+26.18),.035,6))
 return FEATURES
