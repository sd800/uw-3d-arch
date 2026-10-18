"""Individual Quad highlight frontages; retain aerial-verified flat inner roofs.

UW owner exterior photos and the university library's building history inform the
Tudor bays, entry projections and gable shapes. Sizes remain exterior estimates.
"""
from cad_core import *

REFS={
'SAV':'https://artsci.washington.edu/news/2009-09/extreme-makeover-savery-hall',
'RAI':'https://dxarts.washington.edu/facilities/raitt-hall',
'SMI':'https://history.washington.edu/sites/history/files/documents/smith_hall_fsep_oct_2019.pdf',
'GWN':'https://writing.washington.edu/file/358'}
FEATURES={
'SAV':['warm masonry L-shaped teaching wings','large rectangular stone-mullioned Quad bays','projecting entrance bay with Tudor arch','stepped gables and stone coping','aerial-verified slate margin and flat inner roof'],
'RAI':['broad stone-trimmed Tudor frontage','rectangular paired and triplet window groups','end and central shaped gables','recessed entrance and grounded stone approach','aerial-verified flat inner roof'],
'SMI':['long brick hall with pale stone bay frames','wide Quad-facing rectangular window groups','central gabled entry projection','corner masonry piers and string courses','separate slate roof edges and flat center'],
'GWN':['L-shaped brick teaching/library wings','Tudor-arched wood entrance and stone surround','wide mullioned Quad windows','gable and parapet silhouettes','sloped slate edges retained around flat roof']}

def frontage(ms,p,base,h,ident,ground):
    from architecture_refinement import window,courses
    target=np.array([130.,155.]);candidates=[]
    def add(q,z,height,mat):
        for pp in polygons(q):ms[mat].append(extrusion(pp,z,height))
    def panel(q,c,u,n,z,depth,mat):
        for pp in polygons(q):
            m=extrusion(pp,0,depth);v=m.vertices.copy();m.vertices=np.column_stack([c[0]+u[0]*v[:,0]+n[0]*v[:,2],c[1]+u[1]*v[:,0]+n[1]*v[:,2],z+v[:,1]]);trimesh.repair.fix_normals(m);ms[mat].append(m)
    for q in polygons(p):
        cs=np.asarray(q.exterior.coords)
        for a,b in zip(cs[:-1],cs[1:]):
            v=b-a;ln=np.linalg.norm(v)
            if ln<6:continue
            u=v/ln;n=np.array([u[1],-u[0]]);middle=(a+b)/2
            facing=np.dot(n,target-middle)>0
            if ln>12 and facing:candidates.append((Point(*middle).distance(Point(*target)),a,b,u,n,ln))
            step=5.5 if facing else 4.6;count=max(1,int(ln/step));pitch=ln/count
            for k in range(3):
                for j in range(count):
                    cc=a+u*((j+.5)*pitch);width=min(pitch-.65,3.2 if facing else 2.15);zz=base+k*h/3+.9;hh=min(3.8,h/3-1.6)
                    # The visible Quad elevations have broad rectangular Tudor
                    # window groups, not uniform small pointed heads.
                    window(ms,cc,u,n,zz,width,hh,False,'LightStone',2 if facing else 1)
                    if facing:
                        outer=box(-width/2-.20,0,width/2+.20,hh+.15);inner=box(-width/2+.10,.15,width/2-.10,hh-.10);panel(outer.difference(inner),cc,u,n,zz-.08,.30,'SuzzalloStone')
            if facing:
                for dd in np.linspace(.3,ln-.3,count+1):
                    cc=a+u*dd+n*.11;plan=Polygon([cc-u*.15,cc+u*.15,cc+u*.15+n*.32,cc-u*.15+n*.32]);add(plan,base,.80,'SuzzalloStone');add(plan,base+.80,h-.80,'BrickBuff')
    courses(ms,p,[base+.5,base+h/3-.12,base+2*h/3-.12,base+h-.12],'LightStone',.19,.18)
    if not candidates:return {'features':FEATURES[ident],'reference':REFS[ident]}
    _,a,b,u,n,ln=min(candidates,key=lambda e:e[0]);center=(a+b)/2;ww={'SAV':7.8,'RAI':8.7,'SMI':7.2,'GWN':7.0}[ident]
    # One solid entrance bay is built on the mapped wall. A true recessed
    # Tudor arch below the stone lintel leads to timber double doors.
    center=center+n*.02;outline=box(-ww/2,0,ww/2,h+2.6)
    arch=Polygon([(-1.65,0),(1.65,0),(1.65,3.1),(.9,4.0),(0,4.35),(-.9,4.0),(-1.65,3.1)])
    bay=Polygon([center-u*ww/2,center+u*ww/2,center+u*ww/2+n*.70,center-u*ww/2+n*.70]);add(bay,base,h,'BrickBuff'if ident in ['SAV','RAI']else 'BrickRed')
    front=center+n*.73;panel(box(-ww/2,0,ww/2,5.2).difference(arch),front,u,n,base,.22,'SuzzalloStone')
    panel(arch.buffer(-.10),center+n*.78,u,n,base+.08,.12,'WeatheredWood')
    for xx in [-.58,.58]:panel(box(xx-.035,.3,xx+.035,3.3),center+n*.92,u,n,base,.08,'Frame')
    window(ms,front,u,n,base+6.1,ww-2.0,min(5.1,h-7),False,'LightStone',3)
    # Gables project above the slope margins, with inset stone tracery panels.
    apex={'SAV':3.4,'RAI':3.0,'SMI':3.7,'GWN':3.1}[ident]
    gable=Polygon([(-ww/2,0),(ww/2,0),(ww/2,1.0),(ww*.33,1.0),(0,apex),(-ww*.33,1.0),(-ww/2,1.0)])
    panel(gable,front,u,n,base+h-.15,.32,'SuzzalloStone')
    inner=gable.buffer(-.24,join_style=2);panel(inner,front+n*.34,u,n,base+h-.15,.08,'BrickBuff')
    # Two smaller matched end gables are specific to the long Tudor frontage.
    for sign in [-1,1]:
        cc=(a+b)/2+u*sign*max(0,ln/2-4.5);gw=3.2;gg=Polygon([(-gw/2,0),(gw/2,0),(gw/2,.6),(0,2.2),(-gw/2,.6)])
        panel(gg,cc+n*.1,u,n,base+h-.1,.30,'SuzzalloStone')
    # Short closed stair treads meet both the portal and sampled Quad grade.
    for k in range(7):
        reach=(7-k)*.32;aa=center-u*(ww/2+.4)+n*.65;bb=center+u*(ww/2+.4)+n*.65;q=Polygon([aa,bb,bb+n*reach,aa+n*reach]);mesh=extrusion(q,base-.75,.88+k*.10);bottom=mesh.vertices[:,2]<base-.6
        if ground:mesh.vertices[bottom,2]=np.minimum(base-.75,ground(mesh.vertices[bottom,0],mesh.vertices[bottom,1])-.4)
        ms['StepStone'].append(mesh)
    return {'features':FEATURES[ident],'reference':REFS[ident],'roof_decision':'Retain aerial-verified flat inner roof and sloped slate perimeter','member_dimensions':'Photo interpretation; not surveyed'}
