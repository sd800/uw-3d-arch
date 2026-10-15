"""Satellite-reviewed Alder crossing paths, never coordinate-guessed directions."""
from cad_core import *

def paint_crosswalks(env,roads,footprints,scope):
    source=json.loads((ROOT/'sources/alder_crosswalks.json').read_text());features=[];report=[]
    road_surface=roads.intersection(scope).difference(footprints.buffer(.10))
    available=road_surface.buffer(-.015)
    for row in source['crossings']:
        line=LineString(row['centerline_local_m']);half=row['width_m']/2
        band=line.buffer(half,cap_style=2,join_style=2).intersection(available)
        assert band.area>5,('Mapped crossing missing its roadway',row['id'])
        bars=[]
        # Start each pair inside the curb approach. Clip every painted face to
        # actual carriageway, so no stripe leaks onto sidewalk/median/building.
        for d in np.arange(.15,line.length,row['pair_pitch_m']):
            for off in [0,row['stripe_width_m']+row['paired_gap_m']]:
                aa=float(d+off);bb=min(aa+row['stripe_width_m'],line.length)
                if bb-aa<.04:continue
                a=np.array(line.interpolate(aa).coords[0]);b=np.array(line.interpolate(bb).coords[0]);u=b-a;u/=np.linalg.norm(u);n=np.array([-u[1],u[0]])
                bar=Polygon([a-n*half,a+n*half,b+n*half,b-n*half]).intersection(band)
                for q in polygons(bar):
                    if q.area>.035:bars.append(q)
        paint=unary_union(bars);env(paint,.126,.014,'Marking')
        assert paint.difference(road_surface.buffer(.003)).area<.001,('Paint outside roadway',row['id'])
        # Preserve the polygon provenance for a direct export/ray comparison.
        ps=[q.representative_point()for q in bars]
        probes=[[round(ps[j].x,4),round(ps[j].y,4)]for j in sorted(set([len(ps)//3,len(ps)*2//3]))]
        features.append({'type':'Feature','properties':{'id':row['id'],'intersection':row['intersection'],'source':row['reference']},'geometry':mapping(paint)})
        report.append({'id':row['id'],'intersection':row['intersection'],'path_length_m':round(line.length,3),'paint_area_m2':round(paint.area,3),'width_m':row['width_m'],'paired_stripe_count':len(bars),'probe_points':probes})
    (OUT/'alder_crosswalk_paint.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},separators=(',',':'))+'\n')
    result={'crossings':report,'count':len(report),'paint_on_road_only':True,'reviewed_source':'sources/alder_crosswalks.json','generation':'Mapped footway crossing paths, visually checked in satellite imagery; paired stripes, road/footprint clipping; no node-coordinate orientation heuristic'}
    (OUT/'alder_crosswalk_review.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
