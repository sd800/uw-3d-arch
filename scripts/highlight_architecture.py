"""Individual exterior assemblies for UW's architectural highlights.

Mapped envelopes are retained. Secondary partitions and members are interpreted
from the university, architect and contractor photographs cited in the report.
They are exterior study geometry, not surveyed construction information.
"""
from cad_core import *
from architecture_refinement import window,flat_roof,frame,perimeter_roof,courses,pv_patch
from west_housing import add,panel,edges,entry
from shapely import segmentize

TARGETS={'LAW','PCAR','KNE','HAG','AVA','OUG','HUB','IEB','HRC','CSE','CSE2','LSB','HSEB','UMSA','CSH','EDP'}
REFERENCES={
'LAW':'https://www.kpf.com/project/william-h-gates-hall',
'PCAR':'https://lmnarchitects.com/project/paccar-hall-foster-school-of-business-university-of-washington',
'KNE':'https://www.washington.edu/news/2019/12/17/beauty-in-brutalism-architecture-professor-alex-anderson-reviews-the-uws-bunkerlike-behemoths/',
'HAG':'https://www.gwathmey-siegel.com/2013/08/university-of-washington/',
'AVA':'https://www.gwathmey-siegel.com/2013/08/university-of-washington/',
'OUG':'https://millerhull.com/project/odegaard-library/',
'HUB':'https://www.nwpart.com/projects/university-of-washington-husky-union-building/',
'IEB':'https://www.engr.washington.edu/about/ieb',
'HRC':'https://www.washington.edu/populationhealth/hans-rosling-center-tour/',
'CSE':'https://lazowska.cs.washington.edu/psj.allen.center.html',
'CSE2':'https://lmnarchitects.com/project/bill-melinda-gates-center',
'LSB':'https://perkinswill.com/project/university-of-washington-life-sciences-building/',
'HSEB':'https://millerhull.com/project/health-sciences-education-building/',
'UMSA':'https://www.laminart.com/case-study/montlake-tower-university-washington-medical-center',
'CSH':'https://millerhull.com/project/conibear-shellhouse/',
'EDP':'https://gohuskies.com/news/2013/4/18/208237508',
}
REPORT=[]

def facade(ms,p,z,h,rows,style='academic',where=None):
    """Wall-attached glazing, panel joints and bounded structural bays."""
    total=0
    for a,b,u,n,ln,ri in edges(p):
        if ln<4 or(where and not where(n,(a+b)/2)):continue
        spacing=2.85 if style in ['curtain','metal','medical']else 3.7
        bays=max(1,int((ln-.7)/spacing));pitch=(ln-.7)/bays
        for j in range(bays):
            at=a+u*(.35+(j+.5)*pitch)
            for k in range(rows):
                step=h/rows;sill=.28 if style in ['curtain','medical']else .8
                wh=step-.48 if style in ['curtain','medical']else min(2.65,step-1.15)
                ww=pitch-.18 if style in ['curtain','medical']else min(2.15,pitch-.65)
                trim='Precast'if style in ['medical','classic']else'Frame'
                if style=='metal':ww=.72 if(j+k)%3 else 1.35;wh=step-.82;sill=.44
                if style=='gates':ww=pitch-.75 if(j+k)%3 else pitch-.4;wh=step-.6;sill=.3
                window(ms,at,u,n,z+k*step+sill,ww,wh,style=='classic'and k==rows-1,trim,1 if ww>1.4 else 0)
                if style=='gates':
                    panel(ms,at+u*(pitch*.43),u,n,z+k*step+.10,.32,step-.20,'Corten',.045,.12)
                total+=1
        if style in ['curtain','medical']:
            for k in range(1,rows):panel(ms,(a+b)/2,u,n,z+k*h/rows-.10,ln-.1,.20,'Precast'if style=='medical'else'Frame',.07,.11)
    return total

def fins(ms,p,z,h,where,depth=.65,spacing=2.4,rows=1,mat='WhitePanel',angled=0):
    count=0
    for a,b,u,n,ln,ri in edges(p):
        if ri or ln<8 or not where(n,(a+b)/2):continue
        for along in np.arange(1.15,ln-1.0,spacing):
            at=a+u*along
            direction=n*math.cos(angled)+u*math.sin(angled)
            q=Polygon([at-u*.045+n*.02,at+u*.045+n*.02,at+u*.045+n*.02+direction*depth,at-u*.045+n*.02+direction*depth])
            for k in range(rows):add(ms,q,z+k*h/rows+.12,h/rows-.24,mat);count+=1
    return count

def skylight(ms,p,z,rise=.65):
    """Closed curb and separate glass cover; no coincident roof surfaces."""
    for q in polygons(p):
        add(ms,q,z,.28,'Frame');add(ms,q.buffer(-.14),z+.29,rise,'RoofGlass')
        world,local,u,v=frame(q);a,b,c,d=local(q).bounds
        for x in np.arange(a+1,c,2.2):add(ms,world(box(x-.045,b,x+.045,d)).intersection(q),z+.30+rise,.08,'Frame')

def warped(ms,p,z,rise,mat='RoofMetal',kind='barrel'):
    """Split at ridges/curvature bands before meshing, keeping each cap planar.

    Warping only polygon boundary vertices lets a triangulator bridge across
    the ridge and produce false diagonal folds across large roof surfaces.
    """
    world,local,u,v=frame(p);lp=local(p);a,b,c,d=lp.bounds
    rows=np.linspace(b,d,3 if kind=='gable'else 17)
    def elevation(y):
        t=np.clip((y-b)/(d-b),0,1)
        return rise*(4*t*(1-t)if kind=='barrel'else 1-abs(2*t-1))
    transform=np.eye(4);transform[:2,0]=u;transform[:2,1]=v;transform[:2,3]=np.array(p.centroid.coords[0])
    for lo,hi in zip(rows[:-1],rows[1:]):
        for q in polygons(lp.intersection(box(a-1,lo,c+1,hi))):
            m=extrusion(q,z,.24);top=m.vertices[:,2]>z+.12
            m.vertices[top,2]+=np.interp(m.vertices[top,1],[lo,hi],[elevation(lo),elevation(hi)])
            m.apply_transform(transform);trimesh.repair.fix_normals(m)
            assert m.is_watertight;ms[mat].append(m)
    return z+rise+.24

def supported_columns(ms,p,z,h,where,spacing=5.0,mat='Precast',width=.48,depth=.50,ground=None):
    for a,b,u,n,ln,ri in edges(p):
        if ri or ln<8 or not where(n,(a+b)/2):continue
        for along in np.arange(.6,ln-.5,spacing):
            at=a+u*along
            bottom=min(z,float(ground(*(at+n*.2)))-.2)if ground else z
            panel(ms,at,u,n,bottom,width,z+h-bottom,mat,-.15,depth)

def build_highlight(ms,p,base,id,height,levels,code,lay,info,ground):
    if id not in TARGETS:return None
    parts=[];details=[];glazing=0;shading=0;entries=[];probes={}
    a,b,c,d=p.bounds;world,local,u,v=frame(p);aa,bb,cc,dd=local(p).bounds
    def plan(x0,y0,x1,y1):return world(box(aa+(cc-aa)*x0,bb+(dd-bb)*y0,aa+(cc-aa)*x1,bb+(dd-bb)*y1)).intersection(p)
    def mass(q,start,h,mat,rows=0,style='academic',where=None):
        nonlocal glazing
        for part in polygons(q):
            if part.area<.05:continue
            native_extrude(part,base+start,h,code+'_Volume',lay,mat,info);add(ms,part,base+start,h,mat)
            if rows:glazing+=facade(ms,part,base+start,h,rows,style,where)
            parts.append({'area_m2':round(part.area,2),'base_offset_m':round(start,3),'height_m':round(h,3),'material':mat})
    def roof(q,h,mat='RoofMembrane',rail=.30):flat_roof(ms,q,base+h,mat,rail)
    def door(target,h):
        e=entry(ms,p,base,target,ground,base+h)
        if e:entries.append(e)
    if id=='KNE':
        height=15.6;levels=3;h=14.9
        # The south portico is a real recessed void, not a dark stripe.
        candidates=[e for e in edges(p)if e[4]>20 and not e[5]]
        ea,eb,eu,en,ln,ri=min(candidates,key=lambda e:LineString(e[:2]).distance(Point(-14,16)))
        front=Polygon([ea,eb,eb-en*2.1,ea-en*2.1]).intersection(p)
        core=p.difference(front);mass(core,0,h,'BrickBuff',3,'academic',lambda n,m:n@en<.5)
        mass(front,h-.65,.65,'Precast');roof(p,h,'RoofWarm',.24)
        for along in np.arange(.75,ln-.5,4.7):
            at=ea+eu*along;panel(ms,at,eu,en,base,.95,h,'Precast',-2.12,2.35)
        for along in np.arange(2.5,ln-2,4.7):
            at=ea+eu*along-en*1.95
            window(ms,at,eu,en,base+4.9,2.7,9.0,False,'Precast',1)
            window(ms,at,eu,en,base+.12,2.7,3.5,False,'Frame',1)
        at=ea+eu*2.5;probes['recessed_portico']={'origin':[float(at[0]+en[0]),float(at[1]+en[1]),base+1.2],'direction':[-float(en[0]),-float(en[1]),0],'minimum_recess_m':2.4}
        details=['Deep south-facing concrete portico with continuous ground-to-beam piers','Tall recessed upper lights and low glazed entrance bays, replacing small stacked template windows','Quiet brick lecture volumes behind a separate matte roof']
    elif id=='LAW':
        height=18.6;levels=4;h=17.9
        mass(p,0,h,'BrickBuff');glazing+=facade(ms,p,base+.25,h-.3,4,'academic',lambda n,m:not(n[1]<-.4 or n[0]>.55))
        glazing+=facade(ms,p,base+.2,h-.3,4,'curtain',lambda n,m:n[1]<-.4 or n[0]>.55)
        roof(p,h,'RoofSilver',.30);courses(ms,p,[base+4.0,base+8.5,base+13],'Precast',.18,.10)
        # Four skylights are visible on the lawn above the lower law library.
        for x in [-128,-113,-98,-83]:
            q=box(x-1.7,363,x+1.7,371);z=float(ground(x,367))+.08
            add(ms,q,z,.15,'Frame');warped(ms,q,z+.15,2.4,'RoofGlass','gable')
        door((c+3,b+17),h)
        details=['Distinct warm-masonry outer L and glazed south/east library-facing elevations','Four grounded roof-lawn library skylights corroborated by KPF photographs and aerial','Separate stone floor edges, recessed entry and a continuous roof cap']
    elif id=='PCAR':
        height=18.8;levels=4;h=18.05
        end=plan(0,.25,.24,.78);spine=plan(0,.38,1,.61).difference(end);wings=p.difference(spine).difference(end)
        mass(wings,0,h,'BrickBuff',4);mass(spine,0,h-.55,'DarkGlass',4,'curtain')
        roof(wings,h,'RoofWarm');skylight(ms,spine.buffer(-.6),base+h-.30,.42)
        # The projecting glazed meeting room is carried by the lower hall and
        # columns; its lower facade remains an open arrival rather than a box.
        lower=end.buffer(-2.4);mass(lower,0,7.5,'DarkGlass',2,'curtain')
        mass(end,7.5,8.8,'DarkGlass',2,'curtain');roof(end,16.3,'RoofMetal',.18)
        supported_columns(ms,end,base,7.5,lambda n,m:True,4.9,'Frame',.34,.48,ground=ground)
        door((c-3,b-3),h)
        details=['Separate brick teaching wings and a glazed longitudinal public atrium','Projecting upper meeting-room enclosure, supported lower arrival bays and thin metal roof edge','Multi-light glazing, masonry reveals and grounded entrance canopy']
    elif id in ['HAG','AVA']:
        if id=='HAG':
            height=12.0;levels=2;mass(p,0,8.2,'BrickBuff',2,'classic')
            perimeter_roof(ms,p,base+8.2,3.25,4.2);courses(ms,p,[base+.55,base+4.2,base+8.0],'LightStone',.24,.15)
            door((c+3,(b+d)/2),8.2)
            details=['Original Gould gallery distinguished from the separate AVA modern addition','Two-storey stone/brick classical enclosure, grouped upper lights and sloping slate roof margins']
        else:
            height=12.8;levels=3;mass(p,0,7.6,'HousingSilver')
            glazing+=facade(ms,p,base+.25,7.1,2,'curtain',lambda n,m:n[0]>.65)
            roof(p,7.6,'RoofSilver',.22)
            # Aerial establishes three long top-lit gallery monitors.
            for fraction in [.23,.47,.71]:
                q=plan(.1,fraction,.84,min(.95,fraction+.12)).buffer(-.35)
                if q.area>4:warped(ms,q,base+7.8,1.15,'RoofGlass')
            rotunda=Point(a+5,b+8).buffer(4.6,quad_segs=24).intersection(p)
            mass(rotunda,7.6,4.5,'HousingSilver',1,'curtain');roof(rotunda,12.1,'RoofSilver',.30)
            for zz in [base+3.6,base+7.35]:courses(ms,p,[zz],'Precast',.18,.10)
            details=['Modern metal/concrete gallery wing kept on its own AVA building layer','Three closed curved roof monitors and a taller round entrance/stair volume','Glazed campus-facing entry and articulated facade bands; no invented exhibition graphics']
    elif id=='OUG':
        height=15.8;levels=3;h=15.1
        mass(p,0,h,'BrickBuff',3,'curtain');roof(p,h,'RoofMembrane')
        supported_columns(ms,p,base+.15,h-.15,lambda n,m:True,3.9,'Precast',.35,.48)
        courses(ms,p,[base+4.9,base+9.9],'Precast',.25,.13)
        q=plan(.30,.30,.69,.69).buffer(-.4);skylight(ms,q,base+h+.19,.48)
        door((c+3,(b+d)/2),h)
        details=['Concrete perimeter bay frame over brick/glass library elevations','Three-storey glazing differentiated from the deep solid piers of adjacent Kane','Large central atrium skylight with closed curb and physically separated mullions']
    elif id=='HUB':
        height=20.8;levels=4;h=20.1
        # Modern glazed arrival volumes cap the north and south circulation.
        north=p.intersection(box(a-1,d-15,c+1,d+1));south=p.intersection(box(a-1,b-1,c+1,b+15));old=p.difference(north.union(south))
        mass(old,0,h-2.5,'BrickRed',3,'academic',lambda n,m:n[0]>=-.65);roof(old,h-2.5,'RoofWarm')
        for q in [north,south]:mass(q,0,h,'DarkGlass',4,'curtain');roof(q,h,'RoofMetal',.20)
        glazing+=facade(ms,old,base+3.0,h-6.0,3,'curtain',lambda n,m:n[0]<-.65)
        courses(ms,old,[base+4.6,base+9.2,base+13.8],'LightStone',.13,.08)
        door(((a+c)/2,b-2),h)
        details=['Restored brick east-front enclosure separated from contemporary north/south glass entrances','Larger west-facing public glazing and lower ballroom/student-service roof volumes','Attached canopy and visible floor/mullion structure rather than a uniform brick box']
    elif id=='HRC':
        height=32.8;levels=8;h=32.1;podium=5.2
        lower=p.buffer(-2.1,join_style=2);mass(lower,0,podium,'DarkGlass',1,'curtain')
        terraces=plan(0,.1,.18,.9).union(plan(.81,.1,1,.9));upper=p.difference(terraces)
        mass(p,podium,h-podium-3.7,'DarkGlass',6,'curtain',lambda n,m:n[0]<=.6)
        mass(upper,h-3.7,3.7,'DarkGlass',1,'curtain',lambda n,m:n[0]<=.6);roof(upper,h,'RoofMembrane',.25)
        roof(terraces,h-3.7,'RoofPaving',.95)
        for q in polygons(terraces.buffer(-1.35)):
            garden=q.intersection(plan(-.1,.1,1.1,.32));add(ms,garden,base+h-3.25,.42,'Garden')
        supported_columns(ms,p,base,podium,lambda n,m:n[0]<-.5,5.2,'Precast',.55,2.5,ground=ground)
        shading+=fins(ms,p,base+podium,h-podium-3.7,lambda n,m:n[0]<-.55,1.0,1.6,6,'WhitePanel',.30)
        shading+=fins(ms,upper,base+h-3.7,3.7,lambda n,m:n[0]<-.55,1.0,1.6,1,'WhitePanel',.30)
        # The quieter service side is pale precast, not an all-glass block.
        for skin,zz,hh,rows in [(p,podium,h-podium-3.7,6),(upper,h-3.7,3.7,1)]:
            for ea,eb,eu,en,ln,ri in edges(skin):
                if not ri and en[0]>.6:
                    panel(ms,(ea+eb)/2,eu,en,base+zz,ln-.15,hh,'Precast',.32,.12)
                    for along in np.arange(1.5,ln-1.0,4.8):
                        for k in range(rows):window(ms,ea+eu*along+en*.5,eu,en,base+zz+k*hh/rows+.5,1.15,min(2.55,hh/rows-.9),False,'Frame',0)
        door((a-2,b+15),h)
        details=['Recessed glass public base with grounded concrete pilotis','West glazed elevation with shallow angled pale solar sails bounded by floor slabs','Two genuinely inset upper roof terraces with supported garden edges; quieter precast service elevation']
    elif id=='HSEB':
        height=17.8;levels=4;h=17.05
        mass(p.buffer(-1.25,join_style=2),0,4.1,'DarkGlass',1,'curtain')
        mass(p,4.1,h-4.1,'HousingSilver',3,'metal',lambda n,m:n[1]<=.65);roof(p,h,'RoofSilver',.25)
        supported_columns(ms,p,base,4.1,lambda n,m:True,5.6,'Precast',.35,.52,ground=ground)
        # The north active edge and corner commons have full-height glazing;
        # the classroom faces retain their photographed opaque metal skin.
        glazing+=facade(ms,p,base+4.1,h-4.1,3,'curtain',lambda n,m:n[1]>.65)
        for ea,eb,eu,en,ln,ri in edges(p):
            if ri or ln<8 or en[1]>.65:continue
            for along in np.arange(.4,ln-.3,.70):panel(ms,ea+eu*along,eu,en,base+4.15,.045,h-4.2,'RoofSilver',.025,.035)
        courses(ms,p,[base+4.0,base+8.35,base+12.70],'Cedar',.18,.10)
        door((c+3,b+14),h)
        details=['Corrugated silver opaque classroom skin with varied tall window openings','Glazed north active edge and a recessed ground commons supported by concrete columns','Warm timber floor edges remain wall-attached; no full-building detached decorative fins']
    elif id=='LSB':
        height=24.8;levels=5;h=24.05;plinth=5.2
        mass(p.buffer(-1.4,join_style=2),0,plinth,'Precast',1,'academic')
        stair=plan(.0,.0,.20,1);lab=p.difference(stair)
        mass(lab,plinth,h-plinth,'DarkGlass',4,'curtain');mass(stair,0,h,'Corten')
        glazing+=facade(ms,stair,base+.3,h-.5,5,'curtain',lambda n,m:n[0]<-.45)
        roof(lab,h,'RoofMembrane');roof(stair,h,'RoofWarm',.26)
        shading+=fins(ms,lab,base+plinth,h-plinth,lambda n,m:n[1]<-.55,.72,1.55,2,'FinGlass',.22)
        supported_columns(ms,p,base,plinth,lambda n,m:n[1]<-.4,5.8,'Precast',.40,.55,ground=ground)
        courses(ms,lab,[base+plinth+2*(h-plinth)/4],'WhitePanel',.28,.15)
        pv_patch(ms,lab,base+h,.42);door((a-2,d-8),h)
        details=['Distinct reddish circulation end, glazed laboratory bar and teaching plinth','South photovoltaic glass fins in two bounded groups, with continuous floor support','Glazed west stair front, offset roof edges, attached columns and referenced rooftop PV']
    elif id=='IEB':
        height=21.0;levels=5;h=20.25
        # Preserve a ground-level walk-through at the covered arrival.
        passage=plan(.62,0,.74,1);piers=p.difference(passage)
        midpoint=world(Point(aa+(cc-aa)*.68,(bb+dd)/2));center=np.array(midpoint.coords[0]);span=dd-bb+4
        probes['arrival_passage']={'origin':[float(center[0]-v[0]*span),float(center[1]-v[1]*span),base+2.0],'direction':[float(v[0]),float(v[1]),0],'length_m':2*span}
        mass(piers,0,4.1,'BrickUmber',1,'curtain');mass(p,4.1,h-4.1,'BrickUmber',4,'metal')
        roof(p,h,'RoofWarm',.28);pv_patch(ms,p,base+h,.32)
        for ea,eb,eu,en,ln,ri in edges(p):
            if ri or ln<9:continue
            for along in np.arange(2,ln-2,5.2):
                at=ea+eu*along;panel(ms,at,eu,en,base+4.25,.24,h-4.4,'Corten',.02,.06)
        door((a-3,d-7),h)
        details=['Dark brick upper teaching wings and a genuine open lower arrival passage','Varied narrow/full-height glazing modules and shallow attached masonry reveals','Thin supported entrance canopy and documented roof PV; completed-building photographs used ahead of renderings']
    elif id in ['CSE','CSE2']:
        if id=='CSE':
            height=24.2;levels=7;h=23.45
            atrium=plan(.17,.33,.87,.57);wings=p.difference(atrium)
            mass(wings,0,h,'BrickRed',7,'academic');mass(atrium,0,h-1.1,'DarkGlass',5,'curtain')
            roof(wings,h,'RoofPatina');skylight(ms,atrium.buffer(-.4),base+h-1.0,.8)
            # Small shallow framed bay cheeks are part of the wall, not poles.
            for ea,eb,eu,en,ln,ri in edges(wings):
                if ri or ln<15:continue
                for along in np.arange(2.0,ln-1.0,3.7):
                    at=ea+eu*along
                    for k in range(7):panel(ms,at,eu,en,base+k*h/7+.75,.15,min(2.65,h/7-.95),'Precast',.08,.35)
            details=['Brick academic wings separated from the glazed circulation atrium','Seven-storey bay rhythm with shallow attached pale surrounds and separate roof glazing','Mapped plan and entrance axis retained; no repeated blank metal cap']
        else:
            height=25.6;levels=5;h=24.85;main=h-3.8
            mass(p,0,main,'BrickUmber',4,'gates')
            event=plan(.69,.13,.95,.81);mass(event,main,3.8,'DarkGlass',1,'curtain')
            roof(p.difference(event),main,'RoofWarm',.95);roof(event,h,'RoofMetal',.20)
            # Existing aerial shows a group of narrow roof lanterns.
            for yy in [.36,.49,.62]:skylight(ms,plan(.32,yy,.64,yy+.055).buffer(-.1),base+main+.19,.38)
            door((a-2,d-4),main)
            details=['Dark brick enclosure with staggered warm terracotta piers and larger glazed bays','Separate recessed upper event pavilion and accessible terrace parapet','Three narrow atrium roof lanterns instead of a single invented broad ridge']
        if id=='CSE':door((c+3,d-5),h)
    elif id=='UMSA':
        height=39.0;levels=8;h=38.25;plinth=9.1
        mass(p,0,plinth,'Precast',2,'curtain')
        tower=plan(.08,.22,.96,.87);service=p.difference(tower)
        mass(tower,plinth,h-plinth,'DarkGlass',6,'medical')
        mass(service,plinth,7.1,'Precast',2,'medical');roof(service,plinth+7.1,'RoofWarm',.30)
        roof(tower,h,'RoofMembrane',.30)
        shading+=fins(ms,tower,base+plinth,h-plinth,lambda n,m:n[1]<-.4,.48,3.0,6,'Precast')
        courses(ms,p,[base+5.2,base+plinth-.2],'Precast',.30,.22)
        door((c+3,b+18),plinth)
        details=['Glazed inpatient tower rises above a lower continuous diagnostic/service podium','Pale projecting patient-room bay edges and repeated turquoise/blue glazing bands','Separate lower companion roofs and ground-connected arrival; no fabricated interior departments']
    elif id=='CSH':
        height=13.0;levels=3;h=12.25;deck=3.3
        upper=p.intersection(box(a-1,b-1,c-9,d+1));terrace=p.difference(upper)
        mass(p,0,deck,'Precast');mass(upper,deck,h-deck,'CedarSilver',2,'academic',lambda n,m:n[0]<=.6)
        roof(upper,h,'RoofSilver',.24);roof(terrace,deck,'RoofPaving',.94)
        cover=terrace.intersection(upper.buffer(2.2,join_style=2));add(ms,cover,base+7.7,.16,'RoofSilver')
        supported_columns(ms,cover,base+deck+.18,7.7-deck-.18,lambda n,m:n[0]>.6,7.0,'Frame',.16,.22)
        glazing+=facade(ms,upper,base+deck+.15,h-deck-.3,2,'curtain',lambda n,m:n[0]>.6)
        # Five shell bays open toward the lake under the dining deck.
        for ea,eb,eu,en,ln,ri in edges(p):
            if ri or ln<18 or en[0]<.6:continue
            count=max(2,round(ln/7));pitch=ln/count
            for j in range(count):window(ms,ea+eu*((j+.5)*pitch),eu,en,base+.18,min(5.4,pitch-.6),2.88,False,'Frame',3)
        for ea,eb,eu,en,ln,ri in edges(upper):
            if ri or ln<8:continue
            for along in np.arange(.35,ln-.3,.6):panel(ms,ea+eu*along,eu,en,base+deck+.08,.035,h-deck-.16,'Cedar',.025,.03)
        door((a-3,b+12),h)
        details=['Separate lower shell-storage bays and upper dining/academic enclosure','Olive silver/wood siding, lake-facing glazed dining edge and flat metal roof','Grounded boat-bay thresholds and a supported deck above the storage volume, with continuous parapets']
    elif id=='EDP':
        height=26.0;levels=2;h=19.5
        hall=p.intersection(Polygon([(a-2,-369),(c+2,-397),(c+2,b-2),(a-2,b-2)]));annex=p.difference(hall)
        mass(hall,0,h,'BrickRed',2,'classic');warped(ms,hall,base+h,5.7,'RoofWarm','gable')
        rw,rl,ru,rv=frame(hall);ra,rb,rc,rd=rl(hall).bounds;ridge=[]
        for t in [.3,.5,.7]:
            q=rw(Point(ra+t*(rc-ra),(rb+rd)/2));ridge.append([q.x,q.y,base+h+5.94])
        probes['arena_ridge']=ridge
        mass(annex,0,12.0,'BrickRed',2,'academic');roof(annex,12.0,'RoofMembrane',.3)
        courses(ms,hall,[base+1.0,base+8.4,base+17.8],'LightStone',.18,.16)
        supported_columns(ms,hall,base+.1,h-.2,lambda n,m:n[0]<-.5,6.5,'BrickRed',.60,.42,ground=ground)
        door((a-4,b+38),h)
        details=['Long pitched main arena roof separated from north gymnasium and east service wings','Brick historic west frontage with tall grouped windows, stone bands and attached pier rhythm','Lower annex roofs and continuous entrance contact; no generic flat roof over the whole complex']
    report={'facility_id':id,'height_m':height,'levels':levels,'volume_parts':parts,'window_bays':glazing,'bounded_shade_panels':shading,'entries':entries,'validation_probes':probes,'details':details,'source':REFERENCES[id],'accuracy':'Official mapped main envelope retained. Secondary massing, storey datums, facade/roof members and landscape details are approximate public-photo/aerial interpretations; no as-built survey accuracy is claimed.'}
    REPORT.append(report);return report

def write_highlight_report():
    (OUT/'highlight_refinement.json').write_text(json.dumps({'buildings':REPORT,'refined_facilities':len(REPORT),'source_notes':'sources/HIGHLIGHTS_REFERENCES.md','alder_geometry_unchanged':True,'automatic_rooftop_boxes':False,'members_wall_or_roof_supported':True},indent=2)+'\n')
