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
        # Paired inner lancets and stone tracery sit in front of the recessed
        # doors. The central trumeau carries a small figure and canopy, rather
        # than the earlier needle-like post standing across plain dark glass.
        for side in [-1,1]:
            inner=affinity.translate(arch(1.78,5.72),xoff=side*.99)
            vertical(inner.buffer(.105,join_style=2).difference(inner),c,base+.12,-.55,.18,'LightStone')
            vertical(box(side*.99-.73,3.18,side*.99+.73,3.28),c,base,-.62,.14,'LightStone')
            for dx in [-.43,.43]:
                vertical(box(side*.99+dx-.035,3.28,side*.99+dx+.035,4.45),c,base,-.61,.11,'LightStone')
            # Bronze-colored door frames, kick panels and attached handles.
            for dx in [-.38,.38]:
                at=c+u*(side*.78+dx)-n*1.37
                ms['Cedar'].append(cylinder((*at,base+.24),(*at,base+2.86),.035,5))
            vertical(box(side*.78-.65,.16,side*.78+.65,.38),c,base,-1.34,.045,'Cedar')
            at=c+u*(side*.78-side*.20)-n*1.28
            ms['Gold'].append(cylinder((*at,base+1.05),(*at,base+1.42),.027,6))
        for side in [-1,1]:
            rosette=Point(side*.65,6.27).buffer(.28,quad_segs=10)
            vertical(rosette.buffer(.07).difference(rosette),c,base,-.44,.12,'LightStone')
        vertical(box(-.16,0,.16,4.45),c,base,-.35,.44,'LightStone')
        vertical(box(-.34,4.28,.34,4.45),c,base,-.38,.56,'SuzzalloStone')
        at=c+n*.02
        robe=trimesh.creation.cone(radius=.23,height=.87,sections=8);robe.apply_translation([*at,base+4.45]);ms['LightStone'].append(robe)
        ms['LightStone'].append(cylinder((*at,base+4.96),(*at,base+5.46),.16,8))
        head=trimesh.creation.icosphere(subdivisions=1,radius=.16);head.apply_translation([*at,base+5.62]);ms['LightStone'].append(head)
        for side in [-1,1]:
            arm=at+u*side*.20;hand=at+u*side*.13+n*.13
            ms['LightStone'].append(cylinder((*arm,base+5.28),(*hand,base+4.98),.065,6))
        canopy=Polygon([(-.40,5.92),(0,6.53),(.40,5.92)])
        vertical(canopy,c,base,-.30,.62,'SuzzalloStone')
        vertical(LineString([(-.40,5.92),(0,6.53),(.40,5.92)]).buffer(.055),c,base,.34,.08,'LightStone')
        # A flush stone threshold joins the brick terrace to each door recess.
        threshold=Polygon([c-u*1.96+n*.30,c+u*1.96+n*.30,c+u*1.96-n*1.50,c-u*1.96-n*1.50])
        ms['SuzzalloStone'].append(extrusion(threshold,base-.04,.16))
    for i in [5,6,7,8]:
        c=a+u*i*pitch;vertical(box(-.40,0,.40,2.7),c,base+3.05,.73,.055,'Purple');vertical(box(-.33,2.42,.33,2.58),c,base+3.05,.80,.025,'Gold')
    courses(ms,reading,[base+8.65,base+24.4,base+27.8],'LightStone',.18,.16)
    bb=LineString([a,b]).buffer(8.5,cap_style=2).union(plan['domain']).bounds
    report={'facility_id':'SUZ','height_m':32.5,'levels':3,'volume_parts':parts,'details':['Thirteen Gothic reading-room window bays, brick spandrels, stone piers and patinated pitched roof','Three physically recessed pointed portals with layered archivolts, gables, paired inner lancets, inset doors, bronze handles, stone tracery and supported figure/canopy silhouettes','Continuous west terrace, broad short stone stair, balustrades and north side ramp from UW/GLY photographs','Separate southeast Gothic wing and lower modern library addition'],'reference':'https://www.gly.com/uw-seismic-improvements','focus_bounds':[bb[0],bb[1],plan['lower'],bb[2],bb[3],base+33.0],'focus_direction':[-1.0,-.015,.50],'focus_padding':1.72,'validation_probes':{'recessed_portals':[{'origin':[*map(float,c+u*.8+n*.7),base+2.0],'direction':[-float(n[0]),-float(n[1]),0],'minimum_recess_m':1.7}for c in portals]},'entrance_detail':{'paired_inner_lancets':6,'recessed_door_pairs':3,'supported_statue_silhouettes':3,'flush_thresholds':3},'limits':'Mapped envelope retained. Bay organization and portal/terrace forms are photo-referenced; secondary dimensions, grades and sculptural silhouettes are approximate.'}
    (OUT/'suzzallo_architecture.json').write_text(json.dumps(report,indent=2)+'\n');return report
