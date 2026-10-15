"""Alder's mapped light court and photo-referenced six-storey exterior.
The official footprint is retained outside; OSM supplies the missing inner ring.
HFS courtyard/exterior photos constrain materials, glazing and ground amenities.
"""
from cad_core import *

def courtyard_from_osm(osm,outer):
    f=next(f for f in osm if f['properties'].get('osm_id')=='relation/6447992')
    courts=unary_union([Polygon(ring)for q in polygons(f['poly'])for ring in q.interiors]).intersection(outer)
    assert 580<courts.area<660 and outer.contains(courts),'Mapped Alder light court must remain inside its official envelope'
    return courts

def build_alder(ms,p,base,code,lay,info,ground):
    from architecture_refinement import window,flat_roof
    courts=unary_union([Polygon(ring)for q in polygons(p)for ring in q.interiors]);assert courts.area>580
    height=19.7;podium=4.25;walltop=19.05;levels=6
    # Open a ground-level approach below the continuous upper north wing.
    passage=box(-334.8,-4.4,-331.1,7.8).intersection(p)
    lower=p.difference(passage)
    volumes=[]
    for plan,z,h,mat in [(lower,base,podium,'AlderBrick'),(p,base+podium,walltop-podium,'AlderBrick')]:
        for q in polygons(plan):
            native_extrude(q,z,h,code+'_Volume',lay,mat,info);ms[mat].append(extrusion(q,z,h));volumes.append({'area_m2':round(q.area,2),'base_offset_m':round(z-base,3),'height_m':round(h,3),'material':mat})
    # Lighter enclosed courtyard elevations, darker street brick, and paired
    # white-framed windows rather than generic full-height vertical fins.
    for q in polygons(p):
        for ri,ring in enumerate([q.exterior,*q.interiors]):
            coords=np.asarray(ring.coords)
            for a,b in zip(coords[:-1],coords[1:]):
                ln=np.linalg.norm(b-a)
                if ln<2.5:continue
                u=(b-a)/ln;n=np.array([u[1],-u[0]])
                if ri:
                    panel=Polygon([a+n*.015,b+n*.015,b+n*.075,a+n*.075])
                    for pp in polygons(panel):ms['AlderPanel'].append(extrusion(pp,base+podium,walltop-podium))
                count=max(1,int((ln-.8)/3.25));pitch=(ln-.8)/count
                for j in range(count):
                    center=a+u*(.4+(j+.5)*pitch)
                    for k in range(5):
                        z=base+podium+k*(walltop-podium)/5+.58
                        # Broad glass beside a narrow operable light; changing
                        # their order makes the paired bay pattern legible.
                        wide=min(1.22,pitch*.44);narrow=.50
                        off=(-.47 if (j+k)%3 else .47)
                        window(ms,center+u*off,u,n,z,wide,1.72,False,'AlderFrame',0)
                        window(ms,center-u*(.63 if off<0 else -.63),u,n,z,narrow,1.72,False,'AlderFrame',0)
                    if ln>8 and not passage.buffer(.25).contains(Point(*center)):
                        window(ms,center,u,n,base+.3,min(2.65,pitch-.20),3.05,False,'Frame',1)
                if ri:
                    # The planted court has a clearly supported covered edge.
                    band=Polygon([a+n*.07,b+n*.07,b+n*.40,a+n*.40])
                    for pp in polygons(band):ms['AlderSoffit'].append(extrusion(pp,base+podium-.18,.16))
    flat_roof(ms,p,base+walltop,'RoofAlder',.40)
    # Flush caps finish both the courtyard and street parapet; no roof boxes.
    for q in polygons(p):
        rim=q.buffer(-.04,join_style=2).difference(q.buffer(-.31,join_style=2))
        for pp in polygons(rim):ms['AlderFrame'].append(extrusion(pp,base+walltop+.58,.075))
    # North street entry and court passage share the same soffit and paving datum.
    for q in polygons(passage):ms['AlderSoffit'].append(extrusion(q,base+podium-.10,.10))
    awning=box(-339.4,4.9,-327.7,6.7).difference(courts)
    for q in polygons(awning):ms['RoofAlder'].append(extrusion(q,base+3.55,.16))
    for x in [-338.7,-328.4]:ms['Frame'].append(cylinder((x,6.25,min(base,float(ground(x,6.25)))-.25),(x,6.25,base+3.55),.085,6))
    for q in polygons(p):
        for ring in [q.exterior,*q.interiors]:model.Objects.AddCurve(rh.PolylineCurve([rh.Point3d(x,y,base)for x,y in ring.coords]),attr(code+'_Footprint',lay,'AlderBrick',info))
    report={'facility_id':'ALD','height_m':height,'levels':levels,'volume_parts':volumes,'court_area_m2':round(courts.area,3),'open_sky':True,'details':['Mapped 618 m² stepped central light court, open from ground to sky','Six-storey charcoal-brick street elevations and pale inner-court panels','Paired white-framed windows, glazed lower storey, covered north passage and supported entry canopy','Continuous parapets and matte gray-green roof; no invented rooftop equipment']}
    return report

def detail_alder_court(eg,court,base):
    # Building ground pad is exported separately; these are flush landscape skins.
    floor=court.buffer(-.08)
    for q in polygons(floor):eg['Paving'].append(extrusion(q,base+.025,.055))
    planters=unary_union([box(-355.8,-29.6,-352.2,-18.9),box(-330.4,-20.8,-328.5,-8.2),box(-344.5,-25.5,-338.6,-23.5)]).intersection(court.buffer(-.7))
    for q in polygons(planters):
        eg['Corten'].append(extrusion(q,base+.08,.62))
        for pp in polygons(q.buffer(-.14)):eg['AlderSoil'].append(extrusion(pp,base+.70,.08))
    for x,y in [(-354.0,-24),(-329.5,-13),(-340.5,-24.5)]:
        if not planters.contains(Point(x,y)):continue
        eg['Trunk'].append(cylinder((x,y,base+.73),(x,y,base+4.1),.11,7));m=trimesh.creation.icosphere(subdivisions=1,radius=1);m.apply_scale([1.8,1.6,2.3]);m.apply_translation([x,y,base+4.0]);eg['Leaves'].append(m)
    # Quiet rectangular paving joints and small seating groups stay in the court.
    for x in np.arange(-356,-328,2.4):
        g=LineString([(x,-33),(x,-3)]).buffer(.018).intersection(floor).difference(planters)
        for q in polygons(g):eg['StoneJoint'].append(extrusion(q,base+.080,.008))
    for y in np.arange(-31,-3,1.2):
        g=LineString([(-358,y),(-326,y)]).buffer(.018).intersection(floor).difference(planters)
        for q in polygons(g):eg['StoneJoint'].append(extrusion(q,base+.080,.008))
    for x,y in [(-350.2,-27.0),(-350.2,-19.2),(-336.1,-15.1),(-333.3,-8.2)]:
        if not floor.buffer(-1.3).contains(Point(x,y))or planters.buffer(1.1).contains(Point(x,y)):continue
        eg['Furniture'].append(cylinder((x,y,base+.13),(x,y,base+.78),.055,6));eg['Furniture'].append(extrusion(Point(x,y).buffer(.66,quad_segs=6),base+.78,.06))
        for dx,dy in [(-1.0,0),(1.0,0),(0,1.0)]:
            seat=box(x+dx-.23,y+dy-.23,x+dx+.23,y+dy+.23);eg['Furniture'].append(extrusion(seat,base+.46,.07))
            for xx,yy in [(x+dx-.16,y+dy-.16),(x+dx+.16,y+dy+.16)]:eg['Furniture'].append(cylinder((xx,yy,base+.08),(xx,yy,base+.46),.028,5))
    return {'court_area_m2':round(court.area,3),'open_sky':True,'ground_m':round(base,3),'mapped_inner_ring':'https://www.openstreetmap.org/relation/6447992','primary_photos':['https://hfs.uw.edu/media/0exdnhvw/alder-district-courtyard.jpg','https://hfs.uw.edu/media/xu0ntwuw/alder-hall.jpg'],'approximation':'Outer envelope is UW GIS; courtyard inner boundary is public mapped geometry. Facade bay dimensions, ground passage and planting/furniture positions are photo-informed exterior approximations.'}


def detail_alder_precinct(eg,env,outer,base,roads,walks,footprints,trees,ground):
    from shapely import segmentize
    domain=outer.buffer(22).difference(outer)
    apron=outer.buffer(2.4,join_style=2).difference(outer).difference(footprints).difference(roads)
    env(apron,.105,.045,'AlderPaving')
    sidewalk=walks.intersection(domain).difference(footprints).difference(roads).union(apron)
    # Only mapped approaches break the curbs; no invented pedestrian crossings.
    curbs=roads.boundary.buffer(.12).intersection(domain).difference(roads.buffer(-.04)).difference(walks.buffer(.55)).difference(footprints.buffer(.3))
    env(curbs,-.065,.245,'StoneEdge')
    joints=unary_union([LineString([(x,domain.bounds[1]),(x,domain.bounds[3])]).buffer(.015)for x in np.arange(domain.bounds[0],domain.bounds[2],2.4)]+[LineString([(domain.bounds[0],y),(domain.bounds[2],y)]).buffer(.015)for y in np.arange(domain.bounds[1],domain.bounds[3],2.4)]).intersection(sidewalk)
    env(joints,.153,.008,'StoneJoint')
    pits=0
    for f in trees:
        at=f['poly']
        if not domain.contains(at)or footprints.buffer(.9).contains(at)or not sidewalk.buffer(.25).contains(at)or roads.contains(at):continue
        x,y=at.x,at.y;pit=box(x-.68,y-.68,x+.68,y+.68).intersection(sidewalk).difference(footprints)
        if pit.area<.6:continue
        env(pit,.164,.022,'AlderSoil');env(pit.buffer(.10).difference(pit),.105,.12,'StoneEdge');pits+=1
    return {'streets':['NE Campus Parkway','Brooklyn Avenue NE','University Way NE','NE 40th Street'],'bounds':list(domain.bounds),'sidewalk_area_m2':round(sidewalk.area,2),'curb_length_m':round(curbs.area/.24,2),'official_tree_pits':pits,'paving_joints':'Within mapped sidewalks and immediately graded entry aprons only','geometry_sources':['UW GIS tree positions and walk routes','OpenStreetMap road/path geometry'],'approximation':'Local curb widths, pavement module sizes and bench detailing are illustrative; retain mapped alignments and source tree/bench positions.'}
