"""Photo-referenced Suzzallo west front; closed external study assemblies."""
from cad_core import *
from architecture_refinement import window,flat_roof,courses,facade_style
from core_architecture import oriented_roofs
from suzzallo_approach import reading_envelope

def build_suzzallo(ms,p,base,code,lay,info,ground,plan):
    reading=reading_envelope(p);south=p.intersection(LineString([(48,-42),(103,-18)]).buffer(6.8,cap_style=2)).difference(reading);modern=p.difference(reading).difference(south)
    candidates=[]
    for q in polygons(reading):
        cc=np.asarray(q.exterior.coords)
        for a,b in zip(cc[:-1],cc[1:]):
            u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]])
            if n[0]<-.8:candidates.append((np.linalg.norm(b-a),a,b,u,n))
    length,a,b,u,n=max(candidates,key=lambda x:x[0]);pitch=length/13
    centers=[a+u*(i+.5)*pitch for i in range(13)];portals=[centers[i]for i in [5,6,7]]
    cuts=[Polygon([c-u*2.1+n*.2,c+u*2.1+n*.2,c+u*2.1-n*1.55,c-u*2.1-n*1.55])for c in portals];parts=[]
    def body(q,z,h,mat,name):
        for r in polygons(q):native_extrude(r,z,h,code+'_Volume',lay,mat,info);ms[mat].append(extrusion(r,z,h))
        parts.append({'name':name,'area_m2':round(q.area,2),'height_m':h,'base_offset_m':round(z-base,3)})
    body(reading.difference(unary_union(cuts)),base,8.8,'SuzzalloStone','Stone lower front with three recessed portals')
    body(reading,base+8.8,19.3,'BrickRed','Reading-room brick upper hall')
    roof={k:[]for k in COLORS};oriented_roofs(roof,reading,base+28.1,4.2);ms['RoofPatina'].extend(roof['Slate'])
    body(south,base,21.4,'BrickRed','Southeast Gothic wing');facade_style(ms,south,base,21.4,3);oriented_roofs(ms,south,base+21.4,3.5)
    body(modern,base,18.8,'BrickBuff','Lower modern addition');facade_style(ms,modern,base,18.8,4,'academic');flat_roof(ms,modern,base+18.8)
    def vertical(poly,c,z,offset,depth,mat):
        for q in polygons(poly):
            m=extrusion(q,0,depth);v=m.vertices.copy();m.vertices=np.column_stack((c[0]+v[:,0]*u[0]+(v[:,2]+offset)*n[0],c[1]+v[:,0]*u[1]+(v[:,2]+offset)*n[1],z+v[:,1]));trimesh.repair.fix_normals(m);ms[mat].append(m)
    def arch(w,h):return Polygon([(-w/2,0),(w/2,0),(w/2,h*.66),(w*.35,h*.86),(0,h),(-w*.35,h*.86),(-w/2,h*.66)])
    for i,c in enumerate(centers):
        window(ms,c,u,n,base+10.1,3.55,14.0,True,'LightStone',2)
        if i not in [5,6,7]:window(ms,c,u,n,base+1.0,3.0,6.4,True,'LightStone',1)
    for i in range(14):
        c=a+u*i*pitch
        for zz,hh,ww,dd in [(0,8.8,.70,.60),(8.8,15.7,.52,.45),(24.5,3.7,.40,.34)]:
            q=Polygon([c-u*ww/2-n*.08,c+u*ww/2-n*.08,c+u*ww/2+n*dd,c-u*ww/2+n*dd]);ms['LightStone'].append(extrusion(q,base+zz,hh))
    for c in portals:
        opening=arch(4.2,7.6)
        vertical(box(-2.3,0,2.3,8.8).difference(opening),c,base,-1.5,1.66,'SuzzalloStone')
        for expansion,offset in [(.20,.17),(.36,.29),(.52,.41)]:
            vertical(opening.buffer(expansion,join_style=2).difference(opening.buffer(max(0,expansion-.115),join_style=2)),c,base,offset,.13,'LightStone')
        gable=Polygon([(-2.7,7.1),(0,10.0),(2.7,7.1)])
        vertical(gable.difference(opening),c,base,.10,.18,'SuzzalloStone')
        vertical(LineString([(-2.7,7.1),(0,10.0),(2.7,7.1)]).buffer(.08),c,base,.30,.10,'LightStone')
        vertical(arch(3.9,7.25),c,base+.10,-1.46,.08,'DarkGlass')
        for side in [-1,1]:
            window(ms,c+u*side*.78,u,n,base+.12,1.45,3.0,False,'Frame',0)
            for mat in ['DarkGlass','Frame']:ms[mat][-1].apply_translation([-n[0]*1.52,-n[1]*1.52,0])
        vertical(box(-.12,0,.12,5.55),c,base,.14,.22,'LightStone')
        at=c+n*.34;m=trimesh.creation.cone(radius=.23,height=.9,sections=8);m.apply_translation([*at,base+5.55]);ms['LightStone'].append(m)
        head=trimesh.creation.icosphere(subdivisions=1,radius=.17);head.apply_translation([*at,base+6.62]);ms['LightStone'].append(head)
    for i in [5,6,7,8]:
        c=a+u*i*pitch;vertical(box(-.40,0,.40,2.7),c,base+3.05,.73,.055,'Purple');vertical(box(-.33,2.42,.33,2.58),c,base+3.05,.80,.025,'Gold')
    courses(ms,reading,[base+8.65,base+24.4,base+27.8],'LightStone',.18,.16)
    bb=LineString([a,b]).buffer(8.5,cap_style=2).union(plan['domain']).bounds
    report={'facility_id':'SUZ','height_m':32.5,'levels':3,'volume_parts':parts,'details':['Thirteen Gothic reading-room window bays, brick spandrels, stone piers and patinated pitched roof','Three physically recessed pointed portals with layered archivolts, gables, paired doors and restrained banner/sculpture forms','Continuous west terrace, broad short stone stair, balustrades and north side ramp from UW/GLY photographs','Separate southeast Gothic wing and lower modern library addition'],'reference':'https://www.gly.com/uw-seismic-improvements','focus_bounds':[bb[0],bb[1],plan['lower'],bb[2],bb[3],base+33.0],'focus_direction':[-.96,-.28,.65],'validation_probes':{'recessed_portals':[{'origin':[*map(float,c+u*.8+n*.7),base+2.0],'direction':[-float(n[0]),-float(n[1]),0],'minimum_recess_m':1.7}for c in portals]},'limits':'Mapped envelope retained. Bay organization and portal/terrace forms are photo-referenced; secondary dimensions, grades and sculptural silhouettes are approximate.'}
    (OUT/'suzzallo_architecture.json').write_text(json.dumps(report,indent=2)+'\n');return report
