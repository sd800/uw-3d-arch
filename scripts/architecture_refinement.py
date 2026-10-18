"""Photo-referenced UW exteriors within the public mapped footprints.
Member dimensions, floor datums and secondary roof partitions are approximate.
"""
from cad_core import *
from core_architecture import oriented_roofs
from quad_highlights import frontage as quad_frontage

QUAD={'SAV','RAI','SMI','GWN','MLR','MUS','HUT','THO','JHN','GUG','AND','ROB','HNS'}
RESIDENCES={'MCC','MDR','WLW','OAK','ELM','LAN','ALD','POP','MAH','TEH'}
MODERN={
 'PCAR':(18.8,4,'business','BrickBuff'), 'LAW':(18.6,4,'law','BrickBuff'),
 'CSE':(24.2,5,'academic','BrickRed'), 'CSE2':(25.6,5,'gates','BrickRed'),
 'LSB':(24.8,5,'science','Precast'), 'HRC':(32.8,8,'rosling','Precast'),
 'HSEB':(17.8,4,'health','Precast'), 'IEB':(21.0,5,'engineering','BrickUmber'),
 'OUG':(15.8,3,'odegaard','BrickBuff'), 'KNE':(15.6,3,'lecture','Precast'),
 'MNY':(18.6,3,'theater','BrickUmber'), 'HUB':(20.8,4,'union','BrickBuff'),
 'ALB':(20.2,5,'allen','BrickRed'), 'HAG':(14.2,3,'gallery','Precast'),
 'BIOE':(26.0,6,'academic','BrickBuff'), 'GNOM':(26.0,6,'academic','BrickBuff'),
 'NAN':(23.2,5,'science','Precast'), 'MOL':(21.8,5,'academic','BrickRed'),
 'UWTT':(99.0,22,'tower','Precast'), 'UWTC':(18.2,4,'office','Precast'),
 'UWTO':(17.0,4,'office','Precast'), 'UWTS':(18.2,4,'office','Precast')}
REPORTS=[]

def frame(p):
    c=np.array(p.centroid.coords[0]);corners=np.asarray(p.minimum_rotated_rectangle.exterior.coords)[:4]
    e=np.roll(corners,-1,axis=0)-corners;u=e[np.argmax(np.linalg.norm(e,axis=1))];u=u/np.linalg.norm(u)
    if u[1]<0:u=-u
    v=np.array([-u[1],u[0]])
    world=lambda q:affinity.affine_transform(q,[u[0],v[0],u[1],v[1],*c])
    local=lambda q:affinity.affine_transform(q,[u[0],u[1],v[0],v[1],-c@u,-c@v])
    return world,local,u,v

def window(ms,origin,u,n,z,width,height,pointed=False,trim='Frame',divisions=1):
    if width<.15 or height<.2:return
    if pointed=='round':
        radius=width/2;outline=Polygon([(-width/2,0),(width/2,0),*[(radius*math.cos(a),height-radius+radius*math.sin(a))for a in np.linspace(0,math.pi,13)]])
    elif pointed:
        outline=Polygon([(-width/2,0),(width/2,0),(width/2,height*.76),(width*.28,height*.93),(0,height),(-width*.28,height*.93),(-width/2,height*.76)])
    else:outline=box(-width/2,0,width/2,height)
    def face(q,depth,offset,mat):
        for pp in polygons(q):
            m=extrusion(pp,0,depth);a=m.vertices.copy()
            m.vertices=np.column_stack((origin[0]+a[:,0]*u[0]+(a[:,2]+offset)*n[0],origin[1]+a[:,0]*u[1]+(a[:,2]+offset)*n[1],z+a[:,1]))
            trimesh.repair.fix_normals(m);assert m.is_watertight
            ms[mat].append(m)
    face(outline,.07,.09,'DarkGlass')
    ring=outline.buffer(.07,join_style=2).difference(outline.buffer(-.035,join_style=2))
    face(ring,.10,.16,trim)
    for k in range(1,divisions+1):
        x=-width/2+width*k/(divisions+1)
        face(box(x-.025,.06,x+.025,height*(.75 if pointed else .97)),.055,.25,trim)
    if height>3.4:face(box(-width/2+.03,height*.52,width/2-.03,height*.52+.045),.055,.25,trim)

def courses(ms,p,zs,mat='LightStone',thickness=.12,depth=.10):
    rim=p.buffer(depth,join_style=2).difference(p.buffer(-.035,join_style=2))
    for z in zs:
        for q in polygons(rim):ms[mat].append(extrusion(q,z,thickness))

def facade_style(ms,p,base,h,levels,style='gothic',target=None):
    for part in polygons(p):
        for ring in [part.exterior,*part.interiors]:
            cc=np.asarray(ring.coords)
            for a,b in zip(cc[:-1],cc[1:]):
                ln=np.linalg.norm(b-a)
                if ln<3:continue
                u=(b-a)/ln;n=np.array([u[1],-u[0]])
                Gothic=style in ['gothic','denny'];housing=style=='residence'
                step=4.3 if Gothic else 3.0 if housing else 3.3
                count=max(1,int((ln-.7)/step));pitch=(ln-1.2)/count
                for j in range(count):
                    c=a+u*(.6+(j+.5)*pitch)
                    for k in range(max(1,levels)):
                        floor=h/levels;z=base+k*floor+.78;wh=min(3.15 if Gothic else 2.45,floor-1.3)
                        ww=min(1.45 if Gothic else 1.3 if housing else pitch*.72,pitch-.5)
                        if style in ['rosling','science','gates','health','tower']:
                            ww=pitch-.23;wh=floor-.58;z=base+k*floor+.25
                        elif style=='engineering':
                            ww=min(2.3,pitch-.55)if j%3==0 else .85;wh=floor-1.0
                        elif style in ['lecture','theater']:
                            if k>0 and j%3!=0:continue
                            ww=min(2.1,pitch-.5);wh=min(2.5,floor-1.2)
                        pointed=Gothic and k==levels-1 and style!='denny'
                        trim='LightStone'if Gothic else 'Frame'
                        window(ms,c,u,n,z,ww,wh,pointed,trim,1 if Gothic or housing else 0)
                        if Gothic:
                            sill=Polygon([c-u*(ww/2+.15),c+u*(ww/2+.15),c+u*(ww/2+.15)+n*.26,c-u*(ww/2+.15)+n*.26])
                            ms['LightStone'].append(extrusion(sill,z-.15,.13))
    if style in ['gothic','denny']:
        courses(ms,p,[base+.45,base+h*.36,base+h-.25],thickness=.15)
    elif style in ['rosling','science','gates','health','tower','office']:
        courses(ms,p,[base+k*h/levels for k in range(1,levels)],'Precast'if style=='rosling'else 'Frame',.15,.075)

def flat_roof(ms,p,z,material='RoofMembrane',parapet=.38):
    for q in polygons(p):
        ms[material].append(extrusion(q,z,.18))
        rim=q.buffer(-.10,join_style=2).difference(q.buffer(-.33,join_style=2))
        for r in polygons(rim):ms['Precast'].append(extrusion(r,z+.18,parapet))

def perimeter_roof(ms,p,z,rise=3.1,width=3.0):
    # Mapped aerials show a sloping slate perimeter surrounding a flat inner
    # roof on most Quad buildings, rather than an uninterrupted gabled roof.
    inset=p.buffer(-width,join_style=2)
    if inset.is_empty:
        oriented_roofs(ms,p,z,rise);return
    band=p.difference(inset)
    for q in polygons(band):
        m=extrusion(q,z,.18)
        dist=np.array([p.boundary.distance(Point(x,y))for x,y in m.vertices[:,:2]])
        m.vertices[:,2]+=rise*np.clip(dist/width,0,1);trimesh.repair.fix_normals(m)
        assert m.is_watertight;ms['RoofSlate'].append(m)
    for q in polygons(inset):ms['RoofMembrane'].append(extrusion(q,z+rise,.18))

def supported_entry(ms,p,base,target,ground,style='gothic'):
    candidates=[]
    for q in polygons(p):
        for a,b in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
            ln=np.linalg.norm(b-a)
            if ln>7:candidates.append((LineString([a,b]).distance(Point(*target)),a,b,ln))
    if not candidates:return
    _,a,b,ln=min(candidates,key=lambda q:q[0]);u=(b-a)/ln;n=np.array([u[1],-u[0]]);c=(a+b)/2
    width=min(4.0,ln*.65);height=4.4 if style in ['gothic','denny']else 3.1
    window(ms,c+n*.22,u,n,base+.13,width,height,'round'if style=='denny'else style=='gothic','LightStone'if style in ['gothic','denny']else 'Frame',2)
    if style in ['gothic','denny']:
        for side in [-1,1]:
            at=c+u*side*(width/2+.27)+n*.16
            plan=Polygon([at-u*.22-n*.23,at+u*.22-n*.23,at+u*.22+n*.23,at-u*.22+n*.23])
            ms['LightStone'].append(extrusion(plan,base,.9+height))
    else:
        canopy=Polygon([c-u*(width/2+.6)+n*.10,c+u*(width/2+.6)+n*.10,c+u*(width/2+.6)+n*2.0,c-u*(width/2+.6)+n*2.0])
        ms['RoofMetal'].append(extrusion(canopy,base+3.45,.18))
        if style=='timber':ms['Cedar'].append(extrusion(canopy,base+3.31,.14))
        for side in [-1,1]:
            at=c+u*side*(width/2+.35)+n*1.7;bottom=min(base,float(ground(*at))) if ground else base
            ms['Cedar'if style=='timber'else 'Frame'].append(cylinder((*at,bottom-.35),(*at,base+3.45),.12 if style=='timber'else .09,8))
    # A closed ground-fitted threshold has no unsupported horizontal sheet.
    q=Polygon([c-u*(width/2+.4)-n*.2,c+u*(width/2+.4)-n*.2,c+u*(width/2+.4)+n*1.8,c-u*(width/2+.4)+n*1.8])
    m=extrusion(q,base-.5,.62);bottom=m.vertices[:,2]<base-.2
    if ground:
        m.vertices[bottom,2]=np.minimum(base-.5,ground(m.vertices[bottom,0],m.vertices[bottom,1])-.4)
        top=~bottom;xy=m.vertices[top,:2];blend=np.clip(np.array([p.distance(Point(*v))for v in xy])/1.8,0,1)
        m.vertices[top,2]=base+.12+(ground(xy[:,0],xy[:,1])-base)*blend
        trimesh.repair.fix_normals(m)
    ms['StepStone'].append(m)

def shade_panels(ms,p,base,h,levels,which='west',depth=.85,spacing=2.7):
    count=0
    for q in polygons(p):
        for a,b in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
            ln=np.linalg.norm(b-a)
            if ln<9:continue
            u=(b-a)/ln;n=np.array([u[1],-u[0]])
            if (which=='west'and n[0]>-.65)or(which=='south'and n[1]>-.65):continue
            for along in np.arange(1.4,ln-1.0,spacing):
                c=a+u*along+n*.10
                fin=Polygon([c-u*.04,c+u*.04,c+u*.04+n*depth,c-u*.04+n*depth])
                # Each panel is bounded by its own storey and wall's eaves.
                for k in range(1,levels):
                    z=base+k*h/levels+.12;height=h/levels-.28
                    assert z+height<=base+h+.001
                    ms['FinGlass'if which=='south'else 'WhitePanel'].append(extrusion(fin,z,height));count+=1
    return count

def pv_patch(ms,p,z,maximum=.38):
    q=p.buffer(-3.5,join_style=2)
    if q.is_empty:return 0
    world,local,u,v=frame(q);a,b,c,d=local(q).bounds;count=0
    for xx in np.arange(a+1,c-1,2.6):
        for yy in np.arange(b+1,b+(d-b)*maximum,1.55):
            panel=world(box(xx,yy,xx+2.15,yy+1.1))
            if q.covers(panel):
                ms['Solar'].append(extrusion(panel,z+.35,.12));count+=1
                for xy in list(panel.exterior.coords)[:3]:ms['Frame'].append(cylinder((*xy,z+.18),(*xy,z+.36),.035,4))
    return count

def build_refined(ms,p,base,id,default_height,default_levels,code,lay,info,ground):
    if id not in QUAD|RESIDENCES|set(MODERN)|{'SUZ','GRB','DEN','MGH','BRK','INT','MCM'} and not id.startswith(('HS','UM')):return None
    volumes=[];notes=[];shades=0;solar=0
    def body(q,h,material,levels,style='gothic',start=0):
        for r in polygons(q):
            native_extrude(r,base+start,h,code+'_Volume',lay,material,info)
            ms[material].append(extrusion(r,base+start,h))
            if style:facade_style(ms,r,base+start,h,levels,style)
            volumes.append({'area_m2':round(r.area,2),'base_offset_m':start,'height_m':h,'material':material})
    if id=='SUZ':
        reading=p.intersection(Polygon([(40,-29),(54,43),(72,40),(57,-34)]));south=p.intersection(LineString([(48,-42),(103,-18)]).buffer(6.8,cap_style=2)).difference(reading);modern=p.difference(reading).difference(south)
        body(reading,28.1,'SuzzalloStone',1,'lecture');oriented_roofs(ms,reading,base+28.1,4.2)
        # The 1926 west reading-room facade is one tall glazed storey above its
        # lower floors, not three stacked generic Gothic window arrays.
        for q in polygons(reading):
            for a,b in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
                ln=np.linalg.norm(b-a)
                if ln<35:continue
                u=(b-a)/ln;n=np.array([u[1],-u[0]])
                if n[0]>-.6:continue
                for along in np.arange(4,ln-2,4.7):
                    c=a+u*along
                    for off in [-.82,0,.82]:window(ms,c+u*off,u,n,base+9.4,.70,14.2,True,'LightStone',0)
                    for k,(start,height,width,depth)in enumerate([(0,9,.58,.7),(9,11,.46,.54),(20,7.7,.34,.40)]):
                        at=c+u*2.0;plan=Polygon([at-u*width/2-n*.1,at+u*width/2-n*.1,at+u*width/2+n*depth,at-u*width/2+n*depth]);ms['SuzzalloStone'].append(extrusion(plan,base+start,height))
        body(south,21.4,'BrickRed',3);oriented_roofs(ms,south,base+21.4,3.5)
        body(modern,18.8,'BrickBuff',4,'academic');flat_roof(ms,modern,base+18.8)
        courses(ms,reading,[base+8.8,base+24.0,base+27.8],'LightStone',.20,.16)
        supported_entry(ms,reading,base,(-14,16),ground)
        height=32.5;levels=3;notes=['Separate original reading hall, southeast Gothic wing and lower flat-roofed 1963 addition','Tall triplet reading-room windows, stepped wall-attached buttresses and a recessed west portal']
    elif id in QUAD or id=='MGH':
        height=default_height;levels=3 if id!='HNS'else 4;h=height-3.3
        body(p,h,'BrickBuff'if id in {'SAV','RAI'}else 'BrickRed',levels,None if id in {'SAV','RAI','SMI','GWN'}else 'gothic')
        if id=='MGH':
            world,local,u,v=frame(p);a,b,c,d=local(p).bounds
            strips=[box(a-1,b-1,c+1,b+12),box(a-1,d-12,c+1,d+1),box(a-1,b+12,a+12,d-12),box(c-12,b+12,c+1,d-12)]
            outer=unary_union([world(q).intersection(p)for q in strips]);center=p.difference(outer)
            for q in polygons(outer):perimeter_roof(ms,q,base+h,3.05,2.8)
            flat_roof(ms,center,base+h,'RoofWarm',.25)
            commons=world(box((a+c)/2-7,(b+d)/2-5,(a+c)/2+7,(b+d)/2+5)).intersection(center.buffer(-.4))
            for q in polygons(commons):ms['Frame'].append(extrusion(q,base+h+.18,.18));ms['RoofGlass'].append(extrusion(q.buffer(-.12),base+h+.35,.12))
        else:perimeter_roof(ms,p,base+h,3.05,2.8)
        if id in {'SAV','RAI','SMI','GWN'}:
            detail=quad_frontage(ms,p,base,h,id,ground);notes=detail['features']
        else:supported_entry(ms,p,base,(130,155)if id in {'MLR','MUS'}else(120,-50)if id=='MGH'else(80,110),ground)
        if id not in {'SAV','RAI','SMI','GWN'}:notes=['Mapped slate slope perimeter and flat inner roof','Grouped masonry window bays, mullions, stone sills, string courses and grounded entry']
    elif id=='GRB':
        height=35;levels=3;body(p,17.8,'BrickRed',3);perimeter_roof(ms,p,base+17.8,3.2,2.5)
        tower=box(-16.1,-51.8,-7.0,-42.7).intersection(p)
        body(tower,30.3,'BrickRed',5,None);facade_style(ms,tower,base+21.3,9.0,2,'gothic');perimeter_roof(ms,tower,base+30.3,3.7,4.0)
        courses(ms,tower,[base+21,base+25.8,base+30.1],'LightStone',.27,.18)
        for x,y in list(tower.minimum_rotated_rectangle.exterior.coords)[:-1]:
            at=Point(x,y).buffer(.34,quad_segs=1).intersection(p)
            for q in polygons(at):ms['LightStone'].append(extrusion(q,base+29.7,5.0))
        supported_entry(ms,p,base,(-14,16),ground);notes=['Two mapped wings, lower slate perimeter roofs and a separate junction bell tower','Tower louvres, stone courses and corner pinnacles remain attached to its masonry']
    elif id=='DEN':
        from denny_highlight import build_denny
        height=26.2;levels=3;notes=build_denny(ms,p,base,body,ground)
    elif id=='BRK':
        height=17.6;levels=3;body(p,12.5,'WeatheredWood',3,None)
        for q in polygons(p):
            m=extrusion(q,base+12.48,.22);top=m.vertices[:,2]>base+12.55;m.vertices[top,2]+=4.6*(m.vertices[top,1]-p.bounds[1])/(p.bounds[3]-p.bounds[1]);trimesh.repair.fix_normals(m);ms['WeatheredWood'].append(m)
            roof=extrusion(q,base+12.71,.18);roof.vertices[:,2]+=4.6*(roof.vertices[:,1]-p.bounds[1])/(p.bounds[3]-p.bounds[1]);ms['RoofWarm'].append(roof)
            for a,b in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
                ln=np.linalg.norm(b-a)
                if ln<15:continue
                u=(b-a)/ln;n=np.array([u[1],-u[0]])
                for along in np.arange(3,ln-1,4.2):
                    c=a+u*along;window(ms,c,u,n,base+4.35,.78,8.0+4.5*(c[1]-p.bounds[1])/(p.bounds[3]-p.bounds[1]),False,'Frame',0)
                for along in np.arange(3,ln-2,7.5):window(ms,a+u*along,u,n,base+.3,5.6,3.9,False,'Frame',2)
        supported_entry(ms,p,base,(-220,480),ground,'modern');notes=['Weathered timber museum enclosure with a street-aligned shed roof','Tall narrow upper glazing and large ground-level discovery windows']
    elif id=='INT':
        height=10.9;levels=1;world,local,u,v=frame(p);lp=local(p);a,b,c,d=lp.bounds
        body(p,5.3,'CedarSilver',1,'lecture')
        for q in polygons(p):
            wall=extrusion(q,base+5.27,.22);top=wall.vertices[:,2]>base+5.35;across=(wall.vertices[top,:2]-np.array(p.centroid.coords[0]))@v
            wall.vertices[top,2]+=5.1*np.clip((across-b)/(d-b),0,1);trimesh.repair.fix_normals(wall);ms['CedarSilver'].append(wall)
        # Coast Salish longhouse roofs are shed forms; the wing outline and
        # direction follow the mapped hall, with a generous attached eave.
        for q in polygons(p.buffer(.55,join_style=2)):
            m=extrusion(q,base+5.3,.23);uv=local(q)
            along=(m.vertices[:,:2]-np.array(p.centroid.coords[0]))@v
            m.vertices[:,2]+=5.1*(along-b)/(d-b);ms['RoofSilver'].append(m)
        for q in polygons(p):
            for aa,bb in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
                ln=np.linalg.norm(bb-aa)
                if ln<9:continue
                uu=(bb-aa)/ln;nn=np.array([uu[1],-uu[0]])
                for along in np.arange(1.0,ln-1,3.5):
                    at=aa+uu*along+nn*.18;top=base+5.37+5.1*(((at-np.array(p.centroid.coords[0]))@v-b)/(d-b))
                    bottom=min(base,float(ground(*at)));ms['Cedar'].append(cylinder((*at,bottom-.25),(*at,top),.22,8))
        supported_entry(ms,p,base,(322,250),ground,'modern');notes=['Silvered cedar enclosure, sloped longhouse roof and ground-fitted timber posts','Modern Indigenous gathering building, replacing the generic brick/gabled template']
    elif id=='ALD':
        from alder_hall import build_alder
        result=build_alder(ms,p,base,code,lay,info,ground);REPORTS.append(result);return result
    elif id=='MCM':
        height=35.8;levels=11;world,local,u,v=frame(p);a,b,c,d=local(p).bounds
        for lo,hi,h,n in [(0,.34,35.0,11),(.34,.66,10.8,3),(.66,1,35.0,11)]:
            q=world(box(a+(c-a)*lo,b-1,a+(c-a)*hi,d+1)).intersection(p)
            body(q,h,'Precast',n,'residence');flat_roof(ms,q,base+h,'RoofWarm')
            courses(ms,q,[base+k*h/n for k in range(1,n)],'Precast',.22,.32)
        supported_entry(ms,p,base,(390,265),ground,'modern');notes=['Separate north and south residential towers and lower shared central commons','Exposed concrete floor edges and smaller residential window modules']
    else:
        if id in RESIDENCES:height=default_height;levels=default_levels;style='residence';material='BrickRed'if id in {'MCC','MDR','WLW','OAK'}else 'BrickBuff'
        elif id.startswith(('HS','UM'))and id not in MODERN:height=default_height;levels=max(1,default_levels);style='medical';material='Precast'if id.startswith('UM')else 'BrickBuff'
        else:height,levels,style,material=MODERN[id]
        h=height-.7
        body(p,h,material,levels,style)
        flat_roof(ms,p,base+h,'RoofPatina'if id in {'CSE2','CSE'}else 'RoofWarm'if style in ['lecture','theater','medical','office']else 'RoofMembrane')
        # Deliberately different facade systems instead of a campus-wide glass box.
        if style=='rosling':shades=shade_panels(ms,p,base,h,levels,'west',.9,2.7)
        elif id=='LSB':shades=shade_panels(ms,p,base,h,levels,'south',.66,2.5)
        if id in {'PCAR','CSE2','OUG'}:
            world,local,u,v=frame(p);a,b,c,d=local(p).bounds
            spine=world(box((a+c)/2-10,(b+d)/2-5,(a+c)/2+10,(b+d)/2+5)if id=='OUG'else box(a+5,(b+d)/2-2.2,c-5,(b+d)/2+2.2)).intersection(p.buffer(-2.0))
            for q in polygons(spine):ms['Frame'].append(extrusion(q,base+h+.16,.25));ms['RoofGlass'].append(extrusion(q.buffer(-.12),base+h+.40,.12))
            notes.append('Glazed atrium roof spine clipped to the mapped hall')
        if id in {'IEB','LSB'}:solar=pv_patch(ms,p,base+h)
        if id=='HRC':
            world,local,u,v=frame(p);a,b,c,d=local(p).bounds
            for lo,hi in [(.05,.25),(.73,.93)]:
                terrace=world(box(a+(c-a)*lo,b+2.0,a+(c-a)*hi,d-2.0)).intersection(p.buffer(-1.5))
                for q in polygons(terrace):
                    ms['RoofPaving'].append(extrusion(q,base+h+.19,.07))
                    planter=q.buffer(-1.5).intersection(world(box(a-1,b+2,c+1,b+6)))
                    for g in polygons(planter):ms['Garden'].append(extrusion(g,base+h+.26,.38))
            notes.append('Two inset roof garden terraces with low planting and flush paving, interpreted from UW tour photographs')
        if id in {'HSEB','IEB'}:
            # The published entry canopy/colonnade is structurally supported.
            target=(-145,-460)if id=='HSEB'else(362,-86)
            supported_entry(ms,p,base,target,ground,'timber'if id=='HSEB'else 'modern')
            if id=='HSEB':courses(ms,p,[base+k*h/levels-.25 for k in range(1,levels)],'Cedar',.18,.11)
        elif id in MODERN:supported_entry(ms,p,base,(-14,16),ground,'modern')
        notes.extend([{'business':'Four-storey brick teaching hall with an atrium spine','law':'Brick and stone law-school wings with recessed glazing','gates':'Curving brick/glass computer-science elevations and a patinated roof edge','science':'Laboratory glazing and bounded facade modules','rosling':'West solar-shading sails over storey-height glazing, with a quieter precast enclosure','health':'Mass-timber education building expressed by warm structure and large glazing','engineering':'Dark brick teaching wings and deliberately varied tall window groups','residence':'Brick residence with smaller paired window modules','medical':'Separate mapped hospital/research wings with restrained glazing and roof edges','tower':'Primary high-rise tower with repeated structural bays','office':'Low-rise companion office building; not a second 99 m tower','odegaard':'Brick library enclosure and central glazed skylight','lecture':'Lecture-hall masonry and limited upper openings','theater':'Larger opaque performance volumes and restrained openings','union':'Brick student-center elevations and glazed entrances','gallery':'Quiet stone gallery mass with glazed entry','academic':'Warm masonry teaching/research elevations with grouped glazing','allen':'Brick and terra-cotta library wing'} .get(style,'Mapped wing with independent facade modules')])
    report={'facility_id':id,'mapped_footprint_m2':round(p.area,2),'height_m':round(height,2),'levels':levels,'volume_parts':volumes,'bounded_shade_panels':shades,'illustrative_pv_modules':solar,'details':notes,'accuracy':'Official footprint retained; exterior partitions, heights and members are approximate public-photo interpretations.'}
    REPORTS.append(report)
    return report

def write_report():
    (OUT/'architecture_refinement.json').write_text(json.dumps({'buildings':REPORTS,'refined_facilities':len(REPORTS),'automatic_rooftop_boxes':False,'shade_panels_bound_to_own_floor':True,'source_notes':'sources/ARCHITECTURE_REFERENCES.md'},indent=2)+'\n')
