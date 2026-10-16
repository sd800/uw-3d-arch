"""Restrained Meany Hall massing/roof correction from UW exterior references."""
from cad_core import *
from architecture_refinement import flat_roof,perimeter_roof,supported_entry,window

def build_meany(ms,p,base,code,lay,info,ground):
    north=p.intersection(box(-140,-29,-50,22))
    stage=p.intersection(box(-120,-71,-58,-52))
    house=p.difference(north).difference(stage)
    parts=[]
    for name,q,h,roof in [('North teaching and lobby wing',north,11.4,'sloped'),('Performance volume',house,13.4,'flat'),('Stage/service volume',stage,17.9,'flat')]:
        for r in polygons(q):
            native_extrude(r,base,h,code+'_Volume',lay,'BrickRed',info)
            ms['BrickRed'].append(extrusion(r,base,h))
            if roof=='sloped':perimeter_roof(ms,r,base+h,2.1,2.8)
            else:flat_roof(ms,r,base+h,'RoofMetal',.25)
        parts.append({'name':name,'height_m':h,'area_m2':round(q.area,2)})
    # Performance enclosures are mostly masonry, not three floors of academic
    # windows. Retain only a ground-level lobby band and sparse service doors.
    for q in polygons(p):
        cc=np.asarray(q.exterior.coords)
        for a,b in zip(cc[:-1],cc[1:]):
            ln=np.linalg.norm(b-a)
            if ln<8:continue
            u=(b-a)/ln;n=np.array([u[1],-u[0]]);mid=(a+b)/2
            if n[0]<-.6 and mid[1]>-40:
                for t in np.arange(3,ln-2,4.0):window(ms,a+u*t,u,n,base+.5,2.65,3.0,False,'Frame',1)
            elif n[0]>.6 and mid[1]>-30:
                for t in np.arange(3,ln-2,6.0):window(ms,a+u*t,u,n,base+.6,1.2,2.8,False,'Frame',0)
    supported_entry(ms,p,base,(-14,16),ground,'modern')
    r={'facility_id':'MNY','height_m':18.6,'levels':3,'volume_parts':parts,'details':['Separate teaching/lobby wing, performance enclosure and taller stage volume','Gray sloping roof perimeter and individual flat metal caps','Mostly opaque brick theater elevations with limited ground-level lobby glazing; no office window grid'],'reference':'https://meanycenter.org/visit/visitor-information','limits':'Mapped envelope retained; exterior partitions, heights and roof sections are approximate. Moderate exterior optimization, not detailed theater BIM.'}
    (OUT/'meany_refinement.json').write_text(json.dumps(r,indent=2)+'\n')
    return r
