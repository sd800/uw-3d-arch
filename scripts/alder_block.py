"""Alder/District Market block: street edges follow the retained public mapping."""
from cad_core import *
from transit_architecture import add,letter_sign
from architecture_refinement import window,flat_roof
from alder_north import bus_shelter,north_landscape,planting_areas,FRONT_REPORT
import gzip

HFS='https://hfs.uw.edu/live/undergraduates/undergraduate-communities/alder-hall/'
MARKET='https://www.washington.edu/news/2012/09/12/groceries-and-more-district-market-opens-in-alder-hall/'
NIGHTRIDE='https://transportation.uw.edu/getting-around/shuttles/nightride'
BLOCK=Polygon([(-379.5,10.85),(-305.2,10.20),(-306.0,-48.8),(-380.65,-48.15)])
BLOCK_REPORT={}

def street_architecture(ms,p,base,ground):
    from alder_north import north_architecture,FRONT_REPORT
    north_architecture(ms,p,base,ground)
    # South loading recess is distinct from the public market/commuter entrance.
    window(ms,np.array([-328.8,-29.68]),np.array([-1.,0]),np.array([0.,-1]),base+.10,3.55,3.05,False,'Metal',0)
    # Aerial-visible perimeter PV bands; no copied equipment blocks on every roof.
    solar=unary_union([box(-372.0,1.6,-352.9,3.9),box(-348.4,1.5,-338.0,3.8),box(-326.0,1.4,-316.0,3.7),box(-372.0,-39.6,-344.7,-37.1)]).intersection(p.buffer(-1.0))
    add(ms,solar,base+19.23,.045,'Metal');add(ms,solar,base+19.275,.055,'Solar')
    for x in np.arange(-372,-315,1.5):add(ms,LineString([(x,-40),(x,5)]).buffer(.018).intersection(solar),base+19.335,.012,'Metal')
    BLOCK_REPORT['architecture']={**FRONT_REPORT,'supported_columns':True,'market_wraparound_glazing':True,'source_observed_pv_area_m2':round(solar.area,2),'reference':[HFS,MARKET]}

def detail_block(eg,env,osm,outer,footprints,roads,walks,trees,ground,places,scope):
    # One coherent pavement domain, with true footprint/court voids and mapped routes.
    court=unary_union([Polygon(r)for r in outer.interiors])if outer.interiors else Polygon()
    building_envelope=Polygon(outer.exterior)
    domain=BLOCK.difference(building_envelope).difference(roads).difference(footprints).buffer(0)
    pits=[]
    for f in trees:
        pt=f['poly']
        if domain.contains(pt)and pt.distance(building_envelope)>.55:
            pits.append(pt.buffer(.63,quad_segs=8).intersection(domain))
    planted=unary_union([*pits,*planting_areas()]).intersection(domain);paved=domain.difference(planted)
    env(paved,.155,.055,'AlderPaving');env(planted,.205,.025,'AlderSoil')
    seams=unary_union([LineString([(x,-50),(x,12)]).buffer(.014)for x in np.arange(-380,-304,2.4)]+[LineString([(-382,y),(-303,y)]).buffer(.014)for y in np.arange(-49,12,2.4)]).intersection(paved)
    env(seams,.212,.008,'StoneJoint')
    # Source nodes also locate stop signs/flags and crossing approaches.
    root=ET.fromstring(gzip.open(ROOT/'sources/osm_map_west.xml.gz','rb').read());crossings=[];stopinfo=[]
    for node in root.findall('node'):
        t={a.attrib['k']:a.attrib['v']for a in node.findall('tag')};xx,yy=TF.transform(float(node.attrib['lon']),float(node.attrib['lat']));x,y=xx-OX,yy-OY;pt=Point(x,y)
        if node.attrib['id']in ['4340397017','4340397018']:
            bay='2'if node.attrib['id']=='4340397017'else'1';z=float(ground(x,y));post_y=min(10.2,y-.45)
            eg['Metal'].append(cylinder((x,post_y,z-.40),(x,post_y,z+3.0),.045,6))
            add(eg,box(x-.27,post_y-.055,x+.27,post_y+.055),z+2.25,.72,'AlderShrub');add(eg,box(x-.27,post_y-.065,x+.27,post_y+.065),z+2.86,.11,'Gold')
            letter_sign(eg,'METRO',(x,post_y+.072),np.array([1.,0]),np.array([0.,1]),z+2.65,.46,.14,'AlderConcrete')
            letter_sign(eg,bay,(x,post_y+.074),np.array([1.,0]),np.array([0.,1]),z+2.31,.30,.26,'AlderConcrete')
            shelter=bus_shelter(eg,x,y,ground)
            # Timetable/arrival display anchored on a closed base clear of boarding space.
            eg['Metal'].append(cylinder((x-1.1,9.5,z-.3),(x-1.1,9.5,z+2.25),.055,6));add(eg,box(x-1.4,9.42,x-.8,9.58),z+1.25,.85,'Frame');add(eg,box(x-1.35,9.59,x-.85,9.63),z+1.32,.70,'WhitePanel')
            add(eg,box(x-4.4,7.3,x-3.85,7.9),z,.82,'Furniture')
            hit=box(x-4.8,6.2,x+2.0,11.8);places.append({'id':'alder-bus-bay-'+bay,'name':'Alder Hall / Campus Parkway · Bay '+bay,'name_zh':'桤木宿舍楼／校园大道公交站 · '+bay+'号站台','position':[x,9.5,z+1.5],'hitArea':mapping(hit),'source':NIGHTRIDE})
            stopinfo.append({'bay':bay,'stop_id':t.get('ref'),'node_id':node.attrib['id'],'position_local_m':[round(x,3),round(y,3)],'shelter':shelter})
    from alder_crosswalks import paint_crosswalks
    crossing_review=paint_crosswalks(env,roads,footprints,scope)
    crossings=[row['id']for row in crossing_review['crossings']]
    # Street curb is open at actual sidewalks/crossings; no solid barrier across the entry.
    curb=roads.boundary.buffer(.11).intersection(BLOCK.buffer(1.8)).difference(roads.buffer(-.02)).difference(walks.buffer(.50)).difference(footprints.buffer(.1));env(curb,.02,.18,'StoneEdge')
    # Compact U-racks occupy the west public paving, clear of corner and door routes.
    for x,y in [(-378.3,-15),(-378.3,-18),(-378.3,-21)]:
        if not paved.buffer(.1).covers(Point(x,y)):continue
        z=float(ground(x,y));eg['Metal'].extend([cylinder((x-.35,y,z-.15),(x-.35,y,z+.78),.035,6),cylinder((x+.35,y,z-.15),(x+.35,y,z+.78),.035,6),cylinder((x-.35,y,z+.78),(x+.35,y,z+.78),.035,6)])
    north_landscape(eg,env,roads,footprints,ground)
    BLOCK_REPORT['architecture'].update(FRONT_REPORT)
    BLOCK_REPORT.update({'bounds_local_m':list(BLOCK.bounds),'block_streets':['NE Campus Parkway','Brooklyn Avenue NE','University Way NE','NE 40th Street'],'paving_area_m2':round(paved.area,2),'mapped_tree_pits':len(pits),'mapped_crossings':crossings,'crosswalk_review':'alder_crosswalk_review.json','bus_stops':stopinfo,'planting_and_paving_connected':True,'references':[NIGHTRIDE,HFS,MARKET],'limits':'Official footprint, mapped stops/crossings/trees and aerial roof arrangement. Member dimensions and secondary furniture positions are approximate; no invented all-area crosswalk or parking grid.'})
    (OUT/'alder_block_refinement.json').write_text(json.dumps(BLOCK_REPORT,indent=2)+'\n')

def block_building(ms,p,base,id,code,lay,info,ground):
    profiles={'SGS':(4.65,1,'Precast'),'ICT':(7.9,1,'BrickUmber'),'IC2':(3.75,1,'BrickRed'),'DSC':(4.85,1,'Precast'),'EIC':(4.60,1,'BrickBuff')}
    if id not in profiles:return None
    height,n,mat=profiles[id];body=height-.4;vols=[]
    for q in polygons(p):
        native_extrude(q,base,body,code+'_Volume',lay,mat,info);add(ms,q,base,body,mat);vols.append({'area_m2':round(q.area,2),'height_m':body})
        if id=='SGS':
            # The small Community Design building has the aerial-visible shallow curved roof.
            m=extrusion(q.buffer(.12),base+body,.16);yy=m.vertices[:,1];cy=q.centroid.y;span=max(1,q.bounds[3]-q.bounds[1]);m.vertices[:,2]+=.65*np.sqrt(np.maximum(0,1-((yy-cy)/(span/2+.15))**2));ms['RoofSilver'].append(m);height+=.65
        else:flat_roof(ms,q,base+body,'RoofWarm',.22)
        for a,b in zip(np.array(q.exterior.coords)[:-1],np.array(q.exterior.coords)[1:]):
            ln=np.linalg.norm(b-a)
            if ln<3:continue
            u=(b-a)/ln;nn=np.array([u[1],-u[0]]);count=max(1,int(ln/(5.2 if id=='ICT'else 3.0)))
            # Theatre stage walls stay largely solid; teaching/office fronts retain grouped windows.
            if id=='ICT'and abs(nn[0])<.5:continue
            for j in range(count):
                at=a+u*(j+.5)*ln/count
                if id=='ICT'and j%3:continue
                window(ms,at,u,nn,base+(.65 if id!='ICT'else 1.15),min(1.7,ln/count-.5),1.8 if id!='ICT'else 2.4,False,'Frame',1)
        add(ms,q.buffer(.10).difference(q.buffer(-.08)),base+.14,.18,'Concrete')
    return {'facility_id':id,'height_m':height,'levels':n,'volume_parts':vols,'details':['Mapped low-rise envelope and use-specific street glazing, without an office-storey grid','Separate roof/parapet profile, grounded service/entry edge and retained footprint','Aerial-informed roof form; heights and facade bay sizes remain approximate'],'reference':'https://www.washington.edu/students/reg/buildings.html'}
