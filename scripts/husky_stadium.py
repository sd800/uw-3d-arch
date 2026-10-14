"""Mapped Husky Stadium field axis with approximate exterior stand/roof geometry."""
from cad_core import *

FIELD_LENGTH=109.728  # 120 yards, including both end zones
FIELD_WIDTH=48.768   # 53 1/3 yards


def build_husky_stadium(ms,footprint,field,base,code,lay,info):
    corners=np.asarray(field.minimum_rotated_rectangle.exterior.coords)[:4]
    edges=np.roll(corners,-1,axis=0)-corners
    u=edges[np.argmax(np.linalg.norm(edges,axis=1))];u=u/np.linalg.norm(u)
    if u[0]<0:u=-u
    v=np.array([-u[1],u[0]]);cx,cy=field.centroid.coords[0]
    def world(q):return affinity.affine_transform(q,[u[0],v[0],u[1],v[1],cx,cy])
    def xyz(x,y,z):return (cx+x*u[0]+y*v[0],cy+x*u[1]+y*v[1],z)
    def solid(q,z,h,material,native=False,name='Part'):
        for part in polygons(world(q)):
            ms[material].append(extrusion(part,z,h))
            if native:native_extrude(part,z,h,code+'_'+name,lay,material,info)
    def beam(a,b,r=.22):ms['Frame'].append(cylinder(xyz(*a),xyz(*b),r,6))
    def rounded(a,b,r):return box(-a+r,-b+r,a-r,b-r).buffer(r,quad_segs=8)
    def canopy(sign):
        # Two distinct trapezoidal cantilevers, aligned with the real field.
        local=[(-91,sign*44), (91,sign*44), (82,sign*104), (-82,sign*104)]
        tops=[base+37.7,base+37.7,base+40.8,base+40.8]
        vertices=[xyz(x,y,z) for (x,y),z in zip(local,tops)]+[xyz(x,y,z-.65) for (x,y),z in zip(local,tops)]
        faces=[[0,1,2],[0,2,3],[4,6,5],[4,7,6]]
        for j in range(4):k=(j+1)%4;faces.extend([[j,k,k+4],[j,k+4,j+4]])
        mesh=trimesh.Trimesh(vertices=vertices,faces=faces,process=True);trimesh.repair.fix_normals(mesh)
        assert mesh.is_watertight;ms['Metal'].append(mesh)
        for x in np.arange(-76,77,19):
            beam((x,sign*96,base+.3),(x,sign*96,base+36),.55)
            beam((x,sign*97,base+36),(x,sign*44,base+37.05),.24)
            beam((x,sign*97,base+31),(x,sign*44,base+37.05),.24)
            for yy in [57,70,83]:
                beam((x,sign*yy,base+31+(97-yy)*6.05/53),(x,sign*yy,base+36+(97-yy)*1.05/53),.15)
    # A full field surface, independent of the hollow building-outline polygons.
    solid(box(-61,-29,61,29),base+.12,.16,'Grass')
    hx,hy=FIELD_LENGTH/2,FIELD_WIDTH/2
    for sign in [-1,1]:solid(box(sign*hx-9.144 if sign>0 else -hx,-hy,hx if sign>0 else -hx+9.144,hy),base+.29,.055,'Purple')
    # Boundary, five-yard stripes, hashes and restrained central W.
    boundary=box(-hx-.13,-hy-.13,hx+.13,hy+.13).difference(box(-hx+.02,-hy+.02,hx-.02,hy-.02))
    solid(boundary,base+.36,.025,'Marking')
    for x in np.linspace(-45.72,45.72,21):solid(box(x-.055,-hy,x+.055,hy),base+.36,.025,'Marking')
    for x in np.arange(-44.8056,45.72,.9144):
        for yy in [-hy+1,hy-1,-6.096,6.096]:solid(box(x-.045,yy-.24,x+.045,yy+.24),base+.36,.025,'Marking')
    w=Polygon([(-8,6),(-4.8,-6),(-1.7,-6),(0,1.7),(1.7,-6),(4.8,-6),(8,6),(5.4,6),(3.2,-2.8),(1,6),(-1,6),(-3.2,-2.8),(-5.4,6)])
    solid(w.buffer(.18,join_style=2),base+.40,.025,'Purple');solid(w,base+.43,.025,'Gold')
    # Stepped lower bowl. Seat caps are physically separated from concrete below.
    aisle=unary_union([box(x-.7,-120,x+.7,120) for x in [-54,-32,0,32,54]]+[box(-125,y-.75,125,y+.75) for y in [-14,14]])
    lower_outer=None
    for k in range(28):
        inner=rounded(63+k*.86,31+k*.78,10+k*.65)
        outer=rounded(63+(k+1)*.86,31+(k+1)*.78,10+(k+1)*.65)
        tread=outer.difference(inner);z=base+.6+k*.38
        solid(tread,base+.15,z-base-.15,'Concrete',True,'Lower'+str(k+1))
        # Most real bleachers are neutral; purple blocks are localized.
        cap=tread.difference(aisle);purple=cap.intersection(box(-62,-70,62,70)) if 6<=k<=14 else Polygon()
        solid(cap.difference(purple),z+.03,.12,'Seat');solid(purple,z+.03,.12,'Purple');lower_outer=outer
    # Separate north/south upper decks, leaving both end views open above the bowl.
    for sign in [-1,1]:
        for k in range(28):
            near=55+k*1.12;far=near+1.12;half=73+k*.20
            row=box(-half,min(sign*near,sign*far),half,max(sign*near,sign*far));z=base+14+k*.50
            solid(row,base+12,z-base-12,'Concrete',True,'Upper'+str(sign)+'_'+str(k+1))
            cap=row.difference(aisle);solid(cap,z+.03,.12,'Seat')
        canopy(sign)
        solid(box(-67,min(sign*88,sign*97),67,max(sign*88,sign*97)),base+19.5,6.1,'Concrete',True,'Club')
        solid(box(-66,min(sign*87.7,sign*88),66,max(sign*87.7,sign*88)),base+21,3.4,'DarkGlass')
    # Connected west football-operations volume and low end-zone displays.
    inverse=[u[0],u[1],v[0],v[1],-cx*u[0]-cy*u[1],-cx*v[0]-cy*v[1]]
    local=affinity.affine_transform(footprint,inverse)
    west=local.intersection(box(-128,-62,-88,62))
    solid(west,base,16.8,'Concrete',True,'WestOperations');solid(west,base+16.8,.35,'Metal')
    solid(box(-90,-29,-89,29),base+7,4.7,'DarkGlass')
    for x in [-89,85]:
        solid(box(x-.7,-18,x+.7,18),base+12.0,7.3,'Frame')
        solid(box(x-.78,-17,x-.68,17),base+12.6,5.9,'DarkGlass')
    for sign in [-1,1]:
        xx=sign*(hx+1.2)
        beam((xx,0,base+.4),(xx,0,base+3.05),.12)
        beam((xx,-2.82,base+3.05),(xx,2.82,base+3.05),.11)
        beam((xx,-2.82,base+3.05),(xx,-2.82,base+8.5),.10)
        beam((xx,2.82,base+3.05),(xx,2.82,base+8.5),.10)
    for q in polygons(footprint):model.Objects.AddCurve(rh.PolylineCurve([rh.Point3d(x,y,base) for x,y in q.exterior.coords]),attr(code+'_Footprint',lay,'Concrete',info))
    report={'field_source':'OpenStreetMap way/235758229','axis_east_north':u.tolist(),'mapped_field_center_m':[cx,cy],'playing_field_m':[FIELD_LENGTH,FIELD_WIDTH],'lower_rows':28,'upper_rows_each_side':28,'canopy_count':2,'modeled_roof_height_m':40.8,'height_status':'Approximate exterior, not surveyed','reference':'https://www.hok.com/projects/view/university-of-washington-husky-stadium-renovation-and-expansion/'}
    (OUT/'stadium_geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
