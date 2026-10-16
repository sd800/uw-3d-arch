"""UW West Campus housing: photo-specific exteriors, not a shared dorm template.

UW GIS fixes the outer envelopes. Upper courts, facade modules and storey
datums are approximate interpretations of HFS, Mahlum and Mithun photographs.
All protruding members attach to a wall, slab or ground-fitted support.
"""
from cad_core import *
from architecture_refinement import window,flat_roof,frame
from core_architecture import oriented_roofs
from shapely import segmentize

PHASE1='https://www.mahlum.com/projects/west-campus-student-housing-phase-i/'
LANDER='https://mithun.com/project/university-of-washington-lander-hall/'
MAPLE_TERRY='https://mithun.com/project/university-of-washington-terry-and-maple-halls/'
MERCER='https://ankrommoisan.com/projects/uw-mercer-court/'
STEVENS='https://hfs.uw.edu/live/undergraduates/undergraduate-communities/stevens-court/'
PRIMARY={'ELM','POP','LAN','MAH','TEH','CDRE','CDRW'}
REPORT=[]

def is_housing(id):
    return id in PRIMARY or id.startswith(('MRC','SC'))

def add(ms,p,z,h,mat):
    if h<=.015:return
    for q in polygons(p):ms[mat].append(extrusion(q,z,h))

def panel(ms,c,u,n,z,w,h,mat,offset=.025,depth=.045):
    p=Polygon([c-u*w/2+n*offset,c+u*w/2+n*offset,
               c+u*w/2+n*(offset+depth),c-u*w/2+n*(offset+depth)])
    add(ms,p,z,h,mat)

def edges(p):
    for q in polygons(p):
        for ri,ring in enumerate([q.exterior,*q.interiors]):
            cc=np.asarray(ring.coords)
            for a,b in zip(cc[:-1],cc[1:]):
                length=np.linalg.norm(b-a)
                if length<2.5:continue
                u=(b-a)/length
                yield a,b,u,np.array([u[1],-u[0]]),length,ri

def housing_windows(ms,p,z,h,floors,style):
    """Bounded window assemblies and shallow cladding; never roof-height rods."""
    count=0;step=3.35 if style in ['elm','poplar','cedar']else 3.25
    for a,b,u,n,length,ri in edges(p):
        bays=max(1,int((length-.8)/step));pitch=(length-.8)/bays
        for j in range(bays):
            c=a+u*(.4+(j+.5)*pitch)
            for k in range(floors):
                floor=h/floors;zz=z+k*floor+.68
                wh=min(1.85,floor-1.03)
                if style in ['elm','poplar','cedar']:
                    # White-framed paired lights, with irregular opaque infills.
                    off=.43 if (j+k)%3 else -.43
                    window(ms,c+u*off,u,n,zz,.98,wh,False,'HousingFrame',0)
                    window(ms,c-u*(.62 if off>0 else -.62),u,n,zz,.35,wh,False,'HousingFrame',0)
                    if (j+2*k)%4==0:
                        panel(ms,c+u*(pitch*.39),u,n,zz-.10,.26,wh+.22,'HousingPanel')
                elif style=='lander':
                    ww=min(1.58,pitch-.55)
                    off=.24 if (j+k)%2 else -.24
                    window(ms,c+u*off,u,n,zz,ww,wh,False,'HousingFrame',1)
                    # The photographed checkerboard patches are flush spandrels.
                    panel(ms,c-u*(pitch*.35),u,n,zz-.56,.56,min(.48,floor*.2),'HousingUmber')
                elif style in ['maple','terry']:
                    ww=min(pitch-.45,2.04 if (j+2*k)%3==0 else 1.08)
                    wh=min(floor-.90,2.02 if k<2 else 1.72)
                    window(ms,c,u,n,zz,ww,wh,False,'HousingFrame',1 if ww>1.5 else 0)
                    if (j+k)%3==0:
                        mat='HousingBlue'if (j+k)%2 else 'HousingOchre'
                        panel(ms,c+u*(ww/2+.19),u,n,zz,.23,wh,mat,.04,.055)
                elif style=='mercer':
                    ww=min(1.46,pitch-.60);wh=min(2.05,floor-.8)
                    window(ms,c,u,n,zz,ww,wh,False,'HousingUmber',1)
                    # Shallow bay cheek entirely within the window's own storey.
                    panel(ms,c+u*(ww/2+.11),u,n,zz-.05,.13,wh+.10,'HousingSilver',.06,.17)
                else:
                    window(ms,c,u,n,zz,min(1.5,pitch-.65),min(1.62,floor-1.1),False,'HousingFrame',1)
                count+=1
    return count

def storefront(ms,p,base,top,ground,style):
    """Glazing starts above the actual uphill pavement, not the center pad."""
    for a,b,u,n,length,ri in edges(p):
        if length<7:continue
        bays=max(1,int(length/3.1));pitch=length/bays
        for j in range(bays):
            c=a+u*((j+.5)*pitch)
            grade=max(base+.12,float(ground(*(c+n*.45)))+.12)
            h=min(3.25,top-grade-.30)
            if h<1.20:continue
            window(ms,c,u,n,grade,min(2.7,pitch-.33),h,False,'Frame',1)
            # On the downhill frontage, expose intermediate occupied floors
            # above the shopfront rather than leaving a tall opaque podium.
            for zz in np.arange(base+4.05,top-1.4,3.1):
                wh=min(2.05,top-zz-.35)
                if zz>grade+h+.28 and wh>1.2:
                    window(ms,c,u,n,zz,min(1.7,pitch-.55),wh,False,'HousingFrame',1)
        if style in ['elm','poplar','cedar']:
            # Weathered metal/wood fascia over public amenity/shopfronts.
            for along in np.arange(.7,length-.7,3.4):
                c=a+u*along;panel(ms,c,u,n,max(base,top-1.0),.16,.86,'HousingCopper',.035,.10)

def entry(ms,p,base,target,ground,roof_top):
    choices=[(LineString([a,b]).distance(Point(*target)),a,b,u,n,ln)
             for a,b,u,n,ln,ri in edges(p)if not ri and ln>9]
    if not choices:return None
    _,a,b,u,n,ln=min(choices,key=lambda x:x[0]);c=LineString([a,b]).interpolate(LineString([a,b]).project(Point(*target)))
    c=np.array([c.x,c.y]);c=a+u*np.clip((c-a)@u,3.6,ln-3.6)
    z=max(base+.08,float(ground(*(c+n*.6)))+.12)
    z=min(z,roof_top-3.8);w=min(5.5,ln*.6)
    window(ms,c+n*.10,u,n,z,3.1,2.85,False,'HousingFrame',1)
    canopy=Polygon([c-u*w/2-n*.08,c+u*w/2-n*.08,c+u*w/2+n*1.75,c-u*w/2+n*1.75])
    add(ms,canopy,z+3.08,.16,'RoofMetal')
    for side in [-1,1]:
        at=c+u*side*(w/2-.20)+n*1.44;bottom=min(z,float(ground(*at)))
        ms['HousingConcrete'].append(cylinder((*at,bottom-.25),(*at,z+3.08),.12,8))
    apron=Polygon([c-u*(w/2+.25)-n*.20,c+u*(w/2+.25)-n*.20,c+u*(w/2+.25)+n*2.3,c-u*(w/2+.25)+n*2.3])
    for q in polygons(segmentize(apron,.8)):
        m=extrusion(q,z-.48,.55);low=m.vertices[:,2]<z-.20
        m.vertices[low,2]=np.minimum(z-.3,ground(m.vertices[low,0],m.vertices[low,1])-.3)
        xy=m.vertices[~low,:2];t=np.clip(np.array([p.distance(Point(*a))for a in xy])/2.3,0,1)
        m.vertices[~low,2]=z+.07+(ground(xy[:,0],xy[:,1])+.04-z)*t
        trimesh.repair.fix_normals(m);ms['StepStone'].append(m)
    return {'position':[round(float(c[0]),2),round(float(c[1]),2),round(z,2)],'attached_canopy':True,'ground_fitted_threshold':True}

def build_housing(ms,p,base,id,height,levels,code,lay,info,ground):
    if not is_housing(id):return None
    volumes=[];windows=0;courts=[];details=[];entries=[]
    def body(plan,start,h,mat):
        for q in polygons(plan):
            native_extrude(q,base+start,h,code+'_Volume',lay,mat,info)
            ms[mat].append(extrusion(q,base+start,h))
            volumes.append({'area_m2':round(q.area,2),'base_offset_m':round(start,3),'height_m':round(h,3),'material':mat})
    a,b,c,d=p.bounds;walltop=height-.62
    if id in ['ELM','POP','CDRE','CDRW']:
        style={'ELM':'elm','POP':'poplar'}.get(id,'cedar');podium=4.25 if id in ['ELM','POP']else 4.7
        upper=p;notch=Polygon()
        if id in ['CDRE','CDRW']:
            # Street-level envelope is UW GIS. Inward-facing upper C courts are
            # read from the reviewed aerial and corroborated by UW PCAD.
            notch=(box(a+(c-a)*.49,b+(d-b)*.26,c+1,b+(d-b)*.75)if id=='CDRW'else
                   box(a-1,b+(d-b)*.25,a+(c-a)*.51,b+(d-b)*.74)).intersection(p)
            upper=p.difference(notch);courts.append({'type':'upper_light_court','area_m2':round(notch.area,2),'deck_offset_m':podium})
        if id=='POP':
            notch=box(a-.2,b+7,a+3.2,d-7).intersection(p)
            upper=p.difference(notch);courts.append({'type':'recessed_west_deck','area_m2':round(notch.area,2),'deck_offset_m':podium})
        body(p,0,podium,'HousingCharcoal');body(upper,podium,walltop-podium,'HousingCharcoal')
        storefront(ms,p,base,base+podium,ground,style)
        windows+=housing_windows(ms,upper,base+podium,walltop-podium,max(1,levels-1),style)
        flat_roof(ms,upper,base+walltop,'RoofHousing',.30)
        if not notch.is_empty:
            add(ms,notch,base+podium+.025,.11,'RoofPaving')
            # Deck rails have a solid supporting parapet below their top rail.
            rim=notch.buffer(-.12,join_style=2).difference(notch.buffer(-.32,join_style=2))
            add(ms,rim,base+podium+.14,.75,'HousingPanel')
        target=((a+c)/2,b-8)if id!='POP'else(a-7,b+12)
        entries.append(entry(ms,p,base,target,ground,base+walltop))
        source=PHASE1;details=['Charcoal masonry and paired pale-framed residential lights','Ground-fitted public/amenity glazing with a restrained weathered-metal fascia','Separate matte roof, attached parapets and bounded deck edges']
        if id.startswith('CDR'):details.append('Opposing C-shaped upper residential wings and lower light-court decks, interpreted from aerial and UW PCAD')
        if id=='POP':details.append('Recessed west-facing communal deck instead of a full-height rectangular wall')
    elif id=='LAN':
        podium=9.5;body(p,0,podium,'HousingConcrete');body(p,podium,walltop-podium,'HousingPanel')
        storefront(ms,p,base,base+podium,ground,'lander')
        windows+=housing_windows(ms,p,base+podium,walltop-podium,5,'lander')
        # The prominent northeast social lounge is copper-clad and glazed,
        # with two-storey gatherings expressed by bounded glazing modules.
        # Select only the nearest exterior north and east faces at the NE
        # corner. The U court has similarly oriented edges, so normals alone
        # would incorrectly repeat the copper lounge on the internal walls.
        corner=Point(c,d);outer=[e for e in edges(p)if not e[5]and e[4]>12]
        for axis in [1,0]:
            candidates=[e for e in outer if e[3][axis]>.7]
            aa,bb,u,n,ln,ri=min(candidates,key=lambda e:LineString(e[:2]).distance(corner))
            along=np.clip(np.dot(np.array([c,d])-aa,u),4.5,ln-4.5);at=aa+u*along
            panel(ms,at,u,n,base+podium-.04,8.0,walltop-podium+.04,'HousingCopper',.31,.10)
            for k in range(3):
                z=base+podium+k*(walltop-podium)/3+.28
                window(ms,at-u*.6+n*.43,u,n,z,5.5,(walltop-podium)/3-.53,False,'Frame',1)
        flat_roof(ms,p,base+walltop,'RoofHousing',.33)
        entries.append(entry(ms,p,base,(c-5,d+4),ground,base+walltop))
        source=LANDER;details=['Pale panel enclosure with shallow checkerboard spandrels','Copper northeast lounge corner with stacked double-height glazed bays','Transparent Local Point/student-services street edge; uphill pavement controls entry level','Mapped U-shaped courtyard and terraced north-to-south approach remain open']
    elif id in ['MAH','TEH']:
        style='maple'if id=='MAH'else'terry';podium=6.6
        upper=p
        if id=='TEH':
            # The terrace is inset into the building, never a floating slab.
            terrace=box(a+2,b+2,c-2,b+12).intersection(p)
            upper=p.difference(terrace)
        body(p,0,podium,'HousingBrick')
        storefront(ms,p,base,base+podium,ground,style)
        if id=='TEH':
            terrace_level=walltop-3.0
            body(p,podium,terrace_level-podium,'HousingBrick')
            body(upper,terrace_level,walltop-terrace_level,'HousingBrick')
            windows+=housing_windows(ms,p,base+podium,terrace_level-podium,levels-3,style)
            windows+=housing_windows(ms,upper,base+terrace_level,walltop-terrace_level,1,style)
        else:
            body(upper,podium,walltop-podium,'HousingBrick')
            windows+=housing_windows(ms,upper,base+podium,walltop-podium,levels-2,style)
        flat_roof(ms,upper,base+walltop,'RoofHousing',.30)
        if id=='TEH':
            add(ms,terrace,base+terrace_level+.025,.12,'RoofPaving')
            rim=terrace.buffer(-.1,join_style=2).difference(terrace.buffer(-.3,join_style=2))
            add(ms,rim,base+terrace_level+.15,.95,'HousingPanel')
            courts.append({'type':'south_roof_terrace','area_m2':round(terrace.area,2),'deck_offset_m':terrace_level})
        entries.append(entry(ms,p,base,(c+4,d-6)if id=='MAH'else(c-5,d+4),ground,base+walltop))
        source=MAPLE_TERRY;details=['Warm red brick, varied window widths and restrained blue/ochre infill panels','Taller street-level public glazing and grounded entrance canopies','Matte roof and continuous attached parapets']
        if id=='MAH':details.append('Existing mapped open-air light court retained; Great Room/Area 01 face the pedestrian plaza')
        else:details.append('Recessed upper south roof terrace and taller HFS office/entry glazing')
    elif id.startswith('MRC'):
        world,local,u,v=frame(p);aa,bb,cc,dd=local(p).bounds
        # A small setback at the lower bay-facing end expresses the stepped
        # waterfront massing without inventing detached roof equipment.
        cuts=[(0,.22,walltop-3.0),(.22,.72,walltop-1.0),(.72,1,walltop)]
        for lo,hi,h in cuts:
            q=world(box(aa+(cc-aa)*lo,bb-1,aa+(cc-aa)*hi,dd+1)).intersection(p)
            if q.is_empty:continue
            n=max(3,round(levels*h/walltop));lower=min(4.4,h*.22)
            body(q,0,lower,'HousingUmber');body(q,lower,h-lower,'HousingSilver')
            windows+=housing_windows(ms,q,base+lower,h-lower,n-1,'mercer');storefront(ms,q,base,base+lower,ground,'mercer')
            flat_roof(ms,q,base+h,'RoofHousing',.25)
        entries.append(entry(ms,p,base,(-635,-125),ground,base+walltop))
        source=MERCER;details=['Five separately mapped finger-like blocks retained','Dark masonry bases and pale silver metal upper enclosures','Tall framed lights with shallow attached flared bay cheeks','Stepped bay-facing roof volumes and ground-fitted plaza entries']
    else:
        # Stevens' smaller brick apartment groups differ from the new halls.
        rise=1.7;h=height-rise-.25;levels=max(3,min(4,levels))
        body(p,0,h,'HousingBrick');windows+=housing_windows(ms,p,base,h,levels,'stevens')
        oriented_roofs(ms,p,base+h,rise)
        for aa,bb,u,n,ln,ri in edges(p):
            if ln<9:continue
            # Fine horizontal cladding courses stay on the upper wall.
            for k in range(1,levels):panel(ms,(aa+bb)/2,u,n,base+k*h/levels-.12,ln-.12,.11,'HousingPanel',.055,.055)
        entries.append(entry(ms,p,base,(-480,-178),ground,base+h))
        source=STEVENS;details=['Low-rise red-brown apartment blocks with narrow domestic window groups','Attached upper-wall courses and slate pitched roofs following each mapped wing','Grounded entrances and continuous support to sampled terrain']
    report={'facility_id':id,'height_m':height,'levels':levels,'volume_parts':volumes,'window_bays':windows,'courts':courts,'entries':[x for x in entries if x],'details':details,'source':source,'accuracy':'UW mapped outer envelope retained. Cladding, upper setbacks, decks, floor datums and member dimensions are approximate public-photo/aerial interpretations, not surveyed as-built geometry.'}
    REPORT.append(report);return report

def housing_landscape(eg,env,buildings,footprints,roads,walks,ground):
    selected=[f for f in buildings if is_housing(f['id'])]
    # Mapped circulation remains dominant. Supplemental paving is confined to
    # narrow building approaches and already enclosed courts, never roads.
    fronts=unary_union([f['poly'].buffer(1.25,join_style=2).difference(f['poly'])for f in selected])
    fronts=fronts.difference(footprints).difference(roads.buffer(.12))
    env(fronts,.27,.045,'AlderPaving')
    places={
      'ELM':box(-427,58,-397,83),
      'LAN':box(-446,-37,-414,-12),
      'MAH':unary_union([Polygon(x)for f in selected if f['id']=='MAH'for q in polygons(f['poly'])for x in q.interiors]),
    }
    count=0
    for id,q in places.items():
        q=q.difference(footprints.buffer(.35)).difference(roads.buffer(.25))
        if q.is_empty:continue
        if id=='ELM':
            # Keep the actual established central planting, not a tiled plaza.
            route=q.boundary.buffer(1.0).intersection(q);env(route,.29,.045,'Paving')
        else:env(q,.29,.045,'Paving')
        for poly in polygons(q):
            aa,bb,cc,dd=poly.bounds
            for x,y in [(aa+2.2,bb+2.4),(cc-2.2,dd-2.4)]:
                planter=box(x-.8,y-1.9,x+.8,y+1.9)
                if not poly.buffer(-.4).covers(planter)or planter.intersects(walks.buffer(.2)):continue
                z=float(ground(x,y))+.34
                add(eg,planter,z,.42,'HousingConcrete');add(eg,planter.buffer(-.14),z+.43,.06,'AlderSoil')
                add(eg,planter.buffer(-.24),z+.49,.26,'AlderShrub')
                for off in [-1.05,1.05]:
                    at=np.array([x+off,y]);seat=box(at[0]-.20,y-1.6,at[0]+.20,y+1.6)
                    add(eg,seat,z+.43,.10,'Cedar')
                    for sy in [-1.2,1.2]:eg['Furniture'].append(cylinder((at[0],y+sy,z),(at[0],y+sy,z+.43),.045,6))
                count+=1
    return {'refined_buildings':len(selected),'courtyard_names':list(places),'supported_planter_benches':count,'roads_preserved':True,'alder_excluded':True}

def write_housing_report(landscape):
    (OUT/'west_housing_refinement.json').write_text(json.dumps({'buildings':REPORT,'count':len(REPORT),'landscape':landscape,'reference_notes':'sources/WEST_HOUSING_REFERENCES.md','alder_unchanged':True,'automatic_rooftop_boxes':False},indent=2)+'\n')
