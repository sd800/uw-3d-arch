"""Source-tag-led secondary campus buildings, with restrained attached detail."""
from cad_core import *
from architecture_refinement import courses,supported_entry
from core_architecture import oriented_roofs
from curation import GOTHIC,PITCHED
REPORT=[]
def build_ordinary(ms,p,base,id,height,levels,code,lay,info,ground,tags,name):
    pitched_roof=id in PITCHED or tags.get('roof:shape')in ['gabled','hipped','mansard','half-hipped']
    residence=any(s in name.lower()for s in ['apartments','court','village','residence'])
    utility=p.area<90 or any(s in name.lower()for s in ['container','gatehouse','modular','maintenance'])
    parking='garage'in name.lower()or tags.get('building')=='parking'
    wall='BrickBuff'if residence else 'BrickRed'if tags.get('building:material')=='brick'else 'Precast'
    if id in GOTHIC:wall='BrickRed'
    if tags.get('building:material')in ['wood','timber']:wall='WeatheredWood'
    if utility:wall='Precast'
    levels=max(1,levels);rise=min(3.4,height*.24)if pitched_roof else 0;h=height-rise-.22
    parts=[]
    for q in polygons(p):
        native_extrude(q,base,h,code+'_Volume',lay,wall,info);ms[wall].append(extrusion(q,base,h))
        parts.append({'area_m2':round(q.area,2),'height_m':round(h,2),'material':wall})
        if not utility:
            # Floor-spaced windows stay wholly inside their wall storey. The
            # size/density follows housing, teaching, garage or service use.
            if parking:
                for ring in [q.exterior,*q.interiors]:
                    cc=np.asarray(ring.coords)
                    for a,b in zip(cc[:-1],cc[1:]):
                        ln=np.linalg.norm(b-a)
                        if ln<5:continue
                        u=(b-a)/ln;n=np.array([u[1],-u[0]])
                        for level in range(levels):
                            z=base+(level+.30)*h/levels
                            poly=Polygon([a+u*.45+n*.08,b-u*.45+n*.08,b-u*.45+n*.16,a+u*.45+n*.16])
                            ms['DarkGlass'].append(extrusion(poly,z,min(1.45,h/levels*.45)))
            else:facade(ms,q,base,h,levels,id in GOTHIC,False,3.2 if residence else 4.1)
            courses(ms,q,[base+.20,base+h-.34],'LightStone',.17,.06)
            if levels>2 and not residence:courses(ms,q,[base+k*h/levels-.12 for k in range(1,levels)],'Precast',.13,.035)
        else:
            # Small facilities have one grounded service door, not an office
            # window grid or a giant unsupported decorative canopy.
            a,b=max(zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]),key=lambda ab:np.linalg.norm(ab[1]-ab[0]))
            u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]]);c=(a+b)/2;w=min(1.15,np.linalg.norm(b-a)*.38)
            poly=Polygon([c-u*w/2+n*.06,c+u*w/2+n*.06,c+u*w/2+n*.13,c-u*w/2+n*.13]);ms['Frame'].append(extrusion(poly,base+.03,min(2.1,h-.3)))
        if pitched_roof:oriented_roofs(ms,q,base+h,rise)
        else:
            roof='RoofSilver'if tags.get('roof:colour')in ['white','silver']else 'RoofWarm'if residence else 'RoofMetal'
            ms[roof].append(extrusion(q,base+h,.18))
            rim=q.buffer(-.10,join_style=2).difference(q.buffer(-.38,join_style=2))
            for r in polygons(rim):ms['Precast'].append(extrusion(r,base+h+.18,.25))
    if p.area>160 and h>4.6 and not parking and not utility:supported_entry(ms,p,base,(p.centroid.x+150,p.centroid.y-120),ground,'modern')
    r={'facility_id':id,'height_m':height,'levels':levels,'volume_parts':parts,'ordinary':True,'details':['Mapped footprint and courtyard openings retained','Use-specific window spacing, floor courses, grounded entry or service door','Tagged roof form with discrete roof surface and attached parapet; no automatic equipment boxes'],'accuracy':'Footprint and available tags are mapped; secondary facade, roof and entry dimensions are approximate.'};REPORT.append(r);return r

def write_ordinary_report():
    (OUT/'ordinary_architecture.json').write_text(json.dumps({'facilities':REPORT,'count':len(REPORT)},indent=2)+'\n')
