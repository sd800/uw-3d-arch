"""University Inn: footprint plus official gallery exterior interpretation.
Three guest-room floors over a recessed arrival/parking level; dimensions of
members and glazing remain approximate. No detached fins or rooftop boxes.
"""
from cad_core import *
from architecture_refinement import window,courses

def build_inn(ms,p,z,code,lay,info,ground):
    a,b,c,d=p.bounds;top=13.65
    # The street-facing northern end is open at ground level for vehicle entry.
    upper=p;rear=p.intersection(box(a+4.2,b-1,c+1,d+1));south_lobby=p.intersection(box(a-1,b-1,c+1,b+14));lower=unary_union([rear,south_lobby])
    for q in polygons(upper):
        native_extrude(q,z+3.15,10.28,code+'_GuestroomFloors',lay,'HotelCream',info);ms['HotelCream'].append(extrusion(q,z+3.15,10.28))
        ms['RoofHotel'].append(extrusion(q,z+13.43,.22));courses(ms,q,[z+3.15,z+13.38],'HotelRoofEdge',.15,.10)
        support=extrusion(q,z-1.5,1.52);low=support.vertices[:,2]<z-.7;support.vertices[low,2]=np.minimum(z-1.2,ground(support.vertices[low,0],support.vertices[low,1])-1.3);ms['Foundation'].append(support)
    for q in polygons(lower):
        native_extrude(q,z,3.15,code+'_RecessedGroundFloor',lay,'HotelOchre',info);ms['HotelOchre'].append(extrusion(q,z,3.15))
    for q in polygons(upper):
        cc=np.asarray(q.exterior.coords)
        for aa,bb in zip(cc[:-1],cc[1:]):
            ln=np.linalg.norm(bb-aa)
            if ln<4:continue
            u=(bb-aa)/ln;n=np.array([u[1],-u[0]]);front=n[0]<-.65;count=max(1,int(ln/(3.8 if front else 3.6)));pitch=ln/count
            for j in range(count):
                at=aa+u*(j+.5)*pitch;w=min(2.4,pitch-.65)
                for k in range(3):window(ms,at,u,n,z+3.55+k*3.25,w,2.35,False,'HotelRoofEdge',2 if front else 1)
                if front:
                    # A shallow folded eave is connected to the roof edge at
                    # each bay. It never becomes a vertical floating pole.
                    poly=Polygon([at-u*(w/2+.17)-n*.12,at+u*(w/2+.17)-n*.12,at+u*(w/2+.17)+n*.7,at-u*(w/2+.17)+n*.7])
                    m=extrusion(poly,z+13.50,.16);m.vertices[:,2]+=.35*np.clip((m.vertices[:,:2]-at)@n,0,.7)/.7;ms['HotelRoofEdge'].append(m)
            if front and ln>8:
                for at in [aa+u*.3,bb-u*.3]:ms['HotelOchre'].append(cylinder((*at,z),(*at,z+3.15),.15,8))
    # The darker, rounded northern corner and attached vertical sign form the
    # recognizable mid-century street elevation seen in the official gallery.
    south=p.intersection(box(a-1,d-13,c+1,d+1))
    for q in polygons(south):
        band=q.buffer(.025,join_style=2).difference(q.buffer(-.14,join_style=2));
        for r in polygons(band):ms['HotelOchre'].append(extrusion(r,z+3.18,10.15))
    # Keep the sign panel on the wall, below the roof. Recessed glass and two
    # narrow corner supports preserve the vehicle opening beneath this wing.
    at=np.array([a-.12,d-7]);ms['HotelSign'].append(boxmesh(at[0]-.14,at[1],z+4,.16,1.05,8.9))
    for zz in [z+4.5,z+12.1]:ms['HotelRoofEdge'].append(boxmesh(a-.10,at[1],zz,.38,.20,.12))
    # Small vector glyphs form the attached vertical UNIVERSITY sign.
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    font=FontProperties(fname=str(ROOT/'assets/fonts/Manrope.ttf'))
    for k,ch in enumerate('UNIVERSITY'):
        loops=TextPath((0,0),ch,size=.62,prop=font).to_polygons();glyph=None
        for loop in loops:
            part=Polygon(loop).buffer(0);glyph=part if glyph is None else glyph.symmetric_difference(part)
        if glyph is None:continue
        for q in polygons(glyph):
            m=extrusion(q,0,.026);v=m.vertices.copy();m.vertices=np.column_stack((at[0]-.26-v[:,2],at[1]-.22+v[:,0],z+11.6-k*.73+v[:,1]));trimesh.repair.fix_normals(m);ms['Gold'].append(m)
    # Grounded curved arrival canopy, supported by slim posts.
    entry=p.intersection(box(a-1,d-12,a+6,d-2)).envelope.buffer(1.0,join_style=1)
    for q in polygons(entry):ms['RoofHotel'].append(extrusion(q,z+3.08,.15))
    for y in [d-3,d-10]:ms['HotelRoofEdge'].append(cylinder((a-.65,y,float(ground(a-.65,y))-.3),(a-.65,y,z+3.08),.09,8))
    return {'height_m':13.65,'levels':4,'details':['Official-gallery mid-century hotel elevation','Three guest-room levels over a recessed arrival/parking floor','Paired multi-pane windows, folded attached roof eaves, warm rounded end, wall-mounted sign and supported entry canopy'],'source':'https://www.staypineapple.com/university-inn-seattle-wa/gallery'}
