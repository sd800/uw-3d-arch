"""Mapped shoreline continuity, marsh islands, quays and supported bridge decks."""
from cad_core import *
from shapely import segmentize
from shapely.ops import linemerge

def detail_shores(eg,env,osm,scope,footprints,lakewater,ground):
    wet=unary_union([f['poly']for f in osm if f['properties'].get('natural')=='wetland'and f['poly'].geom_type in ['Polygon','MultiPolygon']]).intersection(scope)
    shore=lakewater.boundary.buffer(24).intersection(scope).difference(lakewater)
    for f in osm:
        t=f['properties'];g=f['poly']
        if g.geom_type not in ['Polygon','MultiPolygon']or not g.intersects(scope):continue
        if t.get('leisure')=='nature_reserve':env(g.difference(lakewater).difference(footprints),.10,.05,'ShoreGrass')
        elif t.get('natural')=='wetland':env(g.difference(footprints),.16,.07,'Wetland')
        elif t.get('natural')in ['beach','sand']or t.get('surface')=='sand':env(g.difference(footprints).difference(lakewater),.12,.04,'ShoreSand')
    piers=0
    for f in osm:
        t=f['properties'];g=f['poly']
        if t.get('man_made')not in ['pier','breakwater']or not g.intersects(scope):continue
        q=g.buffer(1.1,cap_style=2,join_style=2)if g.geom_type in ['LineString','MultiLineString']else g
        q=q.intersection(scope).difference(footprints)
        for p in polygons(q):
            # Closed deck is above the common lake plane, not a submerged
            # bare-earth drape. Existing mapped dock outlines are retained.
            eg['BridgeDeck'].append(extrusion(p,5.45,.32));piers+=1
            if p.area>10:
                for xy in list(p.exterior.coords)[::max(1,len(p.exterior.coords)//6)]:eg['BridgePier'].append(cylinder((*xy,4.2),(*xy,5.72),.13,6))
    bridges=[]
    primary=[f for f in osm if f['properties'].get('bridge')in ['yes','movable','viaduct']and f['properties'].get('highway')in ['primary','secondary','tertiary']and f['poly'].intersects(lakewater.buffer(25))and f['poly'].intersects(scope)]
    for side in ['west','east']:
        lines=[f['poly']for f in primary if (f['poly'].centroid.x<0)==(side=='west')]
        if not lines:continue
        joined=unary_union(lines);joined=linemerge(joined)if joined.geom_type!='LineString'else joined
        chains=[joined]if joined.geom_type=='LineString'else list(joined.geoms)
        for line in chains:
            line=line.intersection(scope.envelope)
            if line.geom_type!='LineString'or line.length<4:continue
            line=segmentize(line,6);ends=np.array([line.coords[0],line.coords[-1]])
            z0,z1=[float(ground(*xy))+.10 for xy in ends];peak=max(18.0 if side=='west'else 20.0,z0,z1)
            def deck_height(xy):
                ratio=np.array([line.project(Point(*v))/line.length for v in xy]);t0=np.clip(ratio/.25,0,1);t1=np.clip((1-ratio)/.25,0,1)
                return np.minimum(z0+(peak-z0)*t0,z1+(peak-z1)*t1)
            def deck(poly,offset,thickness,mat):
                for pp in polygons(poly):
                    m=extrusion(segmentize(pp,5),offset,thickness);m.vertices[:,2]+=deck_height(m.vertices[:,:2]);trimesh.repair.fix_normals(m);assert m.is_watertight;eg[mat].append(m)
            width=14.0;q=line.buffer(width/2,cap_style=2,join_style=2)
            deck(q,-.65,.65,'BridgeDeck')
            for sign in [-1,1]:deck(line.offset_curve(sign*(width/2-.15),join_style=2).buffer(.075,cap_style=2,join_style=2),0,1.0,'BridgePier')
            for ratio in [.13,.87]:
                at=line.interpolate(line.length*ratio);zz=float(deck_height(np.array([[at.x,at.y]]))[0]);bottom=min(5.,float(ground(at.x,at.y)))-1.0
                eg['BridgePier'].append(cylinder((at.x,at.y,bottom),(at.x,at.y,zz-.65),.8,10))
            bridges.append({'side':side,'approximate_peak_deck_elevation_m':peak,'endpoint_elevations_m':[z0,z1],'mapped_span_m':round(line.length,2),'continuous_approach_profile':True})
    report={'mapped_wetland_m2':round(wet.area,1),'mapped_pier_parts':piers,'bridge_segments':bridges,'source':'OpenStreetMap mapped reserve, wetland, pier and bridge geometry; USGS shore terrain','accuracy':'Bridge deck/member heights and quay thicknesses are illustrative; plan geometry is mapped. No submerged bare-earth road decks.'}
    (OUT/'shoreline_refinement.json').write_text(json.dumps(report,indent=2)+'\n')
    return wet
