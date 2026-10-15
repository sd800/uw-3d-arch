"""Alder north street frontage, checked against September 2025 Street View.
The custom Metro shelters are independent of the recessed shopfront arcade.
Coordinates retain the UW GIS envelope; facade/member dimensions are estimates.
"""
from cad_core import *
from transit_architecture import add,letter_sign
from architecture_refinement import window

STREET_VIEW='https://www.google.com/maps/@?api=1&map_action=pano&pano=7XvmFN0PZ18dn7vtSTBACQ&heading=180'
HFS_PHOTO='https://www.flickr.com/photos/90311612@N05/9355693564/'
FRONT_REPORT={}
ARCADE=box(-336.9,.85,-314.15,7.5)
ENTRY=box(-343.7,-.26,-337.25,2.35)

def parkway_width(t,g,default):
    # Two one-way carriageways are separated by the mapped planted median.
    # The 11 m secondary-road fallback had narrowed Alder's boarding pavement.
    return 9.4 if t.get('name')=='Northeast Campus Parkway' and g.intersects(box(-386,10,-298,50)) else default

def north_architecture(ms,p,base,ground):
    deck=base+4.25
    # Western classrooms have weathered steel and narrow punched lights.
    for a,b in [(-374.9,-356.6)]:
        y=5.67;bottom=min(float(ground(a,y)),float(ground(b,y)),base)-.30
        add(ms,box(a,5.46,b,5.73),bottom,deck-bottom-.10,'AlderCorten')
        for x in np.arange(a+1.65,b-1,3.1):
            window(ms,np.array([x,5.74]),np.array([1.,0]),np.array([0.,1]),deck-2.65,.58,1.55,False,'AlderCorten',0)
    # The entry is the real GIS recess, not a new cut through an upper wing.
    window(ms,np.array([-340.50,-.13]),np.array([1.,0]),np.array([0.,1]),base+.16,5.70,3.55,False,'Frame',3)
    add(ms,box(-344.55,-.23,-336.9,6.05),deck-.24,.18,'MarketWood')
    add(ms,box(-344.6,5.96,-336.85,6.12),deck-.12,.15,'AlderCorten')
    letter_sign(ms,'ALDER HALL',(-340.5,.08),np.array([1.,0]),np.array([0.,1]),base+3.1,3.8,.32)
    # Recessed shopfront is set behind the upper brick envelope and its round piers.
    # Broad wood cladding surrounds the cafe window; the corner market remains glazed.
    add(ms,box(-336.9,.72,-314.15,.92),base-.18,4.32,'MarketWood')
    for x,w in [(-332.8,3.4),(-325.8,4.8),(-318.6,3.8)]:
        sill=base+.80 if x<-330 else base+.18
        window(ms,np.array([x,.96]),np.array([1.,0]),np.array([0.,1]),sill,w,deck-.36-sill,False,'MarketFrame',2)
    # Door leaves and service counter: all frames sit outside their opaque backing.
    for x in [-325.8,-316.05]:
        window(ms,np.array([x,1.18]),np.array([1.,0]),np.array([0.,1]),base+.16,1.65,2.75,False,'MarketFrame',1)
    add(ms,box(-334.7,1.10,-331.0,1.64),base+.83,.11,'MarketWood')
    canopy=box(-336.85,.70,-311.35,7.12).difference(box(-314.1,1.1,-311.35,4.05))
    add(ms,canopy,deck-.31,.15,'MarketWood');add(ms,canopy,deck-.16,.12,'AlderCorten')
    columns=[]
    for x,y in [(-334.4,4.4),(-326.1,4.3),(-317.4,4.2),(-312.1,-1.9)]:
        bottom=min(base,float(ground(x,y)))-.35
        ms['AlderConcrete'].append(cylinder((x,y,bottom),(x,y,deck-.31),.245,12));columns.append([x,y])
    # Corner entry and its east return replace the floating DISTRICT MARKET sign slab.
    window(ms,np.array([-311.39,-6.8]),np.array([0.,-1]),np.array([1.,0]),base+.18,7.5,3.5,False,'MarketFrame',4)
    window(ms,np.array([-309.40,-18.4]),np.array([0.,-1]),np.array([1.,0]),base+.20,12.6,3.2,False,'MarketFrame',5)
    # Small round projecting market sign seen in HFS's entrance photograph.
    center=np.array([-314.0,5.36,deck+.65]);ms['MarketFrame'].append(cylinder(center+np.array([0,-.12,0]),center+np.array([0,.12,0]),.64,20))
    letter_sign(ms,'DISTRICT',(-314.,5.49),np.array([1.,0]),np.array([0.,1]),deck+.76,1.03,.17)
    letter_sign(ms,'MARKET',(-314.,5.49),np.array([1.,0]),np.array([0.,1]),deck+.41,.91,.18)
    FRONT_REPORT.update({'reviewed_imagery':'Google Street View, September 2025; UW HFS 2012 exterior photograph','sources':[STREET_VIEW,HFS_PHOTO,'https://www.spectrumdevsolutions.com/projects/alder-hall/'],'north_ground_floor':['Western weathered-steel classrooms with narrow lights','Mapped recessed Alder entrance','Recessed timber/glass cafe and market arcade with concrete piers','Independent silver-framed Metro shelters, separate from the building canopy'],'arcade_columns_local_m':columns,'false_passage_removed':True,'limits':'Photo-interpreted facade bays, canopy projections, grades and members; not measured construction documents.'})

def bus_shelter(eg,x,y,ground):
    # The stop flag is west of each short freestanding shelter in the 2025 views.
    cx=x+3.7;cy=9.22;z=float(ground(cx,cy))+.22;a=cx-3.2;b=cx+3.2
    # Silver portal frames and shallow glazed roof; no legs extend past the roof.
    for xx in [a,b]:
        for yy in [cy-.93,cy+.93]:
            bottom=float(ground(xx,yy))+.13;add(eg,box(xx-.065,yy-.065,xx+.065,yy+.065),bottom,z+2.65-bottom,'AlderConcrete')
        add(eg,box(xx-.08,cy-.99,xx+.08,cy+.99),z+2.65,.13,'AlderConcrete')
    for yy in [cy-.93,cy+.93]:add(eg,box(a-.08,yy-.065,b+.08,yy+.065),z+2.65,.13,'Frame')
    add(eg,box(a+.09,cy-.86,b-.09,cy+.86),z+2.68,.045,'Glass')
    # Back/side screens are closed thin glass infills, open on the boarding side.
    for xx in [a,b]:add(eg,box(xx-.035,cy-.81,xx+.035,cy+.72),z+.20,2.35,'Glass')
    add(eg,box(a+.10,cy-.91,b-.10,cy-.85),z+.20,2.35,'Glass')
    seat(eg,cx,cy-.29,ground,width=4.9)
    return {'center':[round(cx,3),cy],'span_m':6.4,'depth_m':1.86,'roof_elevation_m':round(z+2.725,3),'type':'Independent silver portal frame / glass screen shelter'}

def seat(eg,x,y,ground,width=1.64):
    z=float(ground(x,y))+.14
    add(eg,box(x-width/2,y-.24,x+width/2,y+.24),z+.45,.07,'Cedar')
    for dx in [-width*.37,width*.37]:
        for dy in [-.16,.16]:eg['Furniture'].append(cylinder((x+dx,y+dy,z-.13),(x+dx,y+dy,z+.47),.035,5))
    add(eg,box(x-width/2,y-.25,x+width/2,y-.20),z+.64,.27,'Cedar')

def planting_areas():
    return [box(-373.9,7.35,-355.8,10.12),box(-337.0,7.15,-328.3,10.05),box(-316.7,7.25,-312.5,9.9)]

def north_landscape(eg,env,roads,footprints,ground):
    for p in planting_areas():
        env(p,.22,.07,'AlderSoil')
        # Low massed groundcover leaves door paths and boarding platforms open.
        for q in polygons(p.buffer(-.18)):
            from shapely import segmentize
            m=extrusion(segmentize(q,2),.27,.36);m.vertices[:,2]+=ground(m.vertices[:,0],m.vertices[:,1]);eg['AlderShrub'].append(m)
        x0,y0,x1,y1=p.bounds
        # Dark bench/rail edge is supported by short silver legs, as photographed.
        for a,b in [((x0,y1),(x1,y1)),((x0,y0),(x0,y1))]:
            g=LineString([a,b]);n=max(1,int(g.length/2.1))
            for j in range(n):
                aa=g.interpolate(j*g.length/n);bb=g.interpolate((j+1)*g.length/n)
                z=float(ground((aa.x+bb.x)/2,(aa.y+bb.y)/2))
                add(eg,LineString([aa,bb]).buffer(.17,cap_style=2),z+.58,.08,'Cedar')
                for pt in [aa,bb]:eg['AlderConcrete'].append(cylinder((pt.x,pt.y,float(ground(pt.x,pt.y))+.12),(pt.x,pt.y,z+.60),.04,5))
    # Concrete bus street and restrained lane/joint paint, following both mapped lanes.
    street=roads.intersection(box(-379.5,11.8,-305.2,22.0)).difference(footprints)
    env(street,.102,.018,'ParkwayConcrete')
    for xx in np.arange(-378,-307,4.6):
        yy=16.65-(xx+349.6)*.0153
        env(box(xx,yy-.065,xx+1.9,yy+.065).intersection(street),.125,.012,'Marking')
    joints=unary_union([LineString([(xx,11),(xx,22)]).buffer(.014)for xx in np.arange(-378,-305,4.6)]).intersection(street)
    env(joints,.124,.008,'StoneJoint')
    FRONT_REPORT['north_planting_pockets']=len(planting_areas());FRONT_REPORT['parkway_carriageway_width_m']=9.4
