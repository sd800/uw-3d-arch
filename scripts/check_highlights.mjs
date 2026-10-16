/** Small export subset: tour order and the geometric details that differ from boxes. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {Raycaster,Vector3} from 'three';
import {CampusTDSLoader} from './campus_tds_loader.js';
const root=new URL('../',import.meta.url),read=p=>JSON.parse(readFileSync(new URL(p,root),'utf8'));
const report=read('output/highlight_refinement.json'),records=read('output/buildings.json'),layers=read('output/layer_map.json'),review=read('sources/highlights_review.json');
const ids=review.audit.filter(x=>x.action==='rebuilt').map(x=>x.facility_id).concat('AVA');
assert.equal(review.highlight_order.length,28);assert.equal(review.highlight_order[1],'ALD');
assert.deepEqual(report.buildings.map(x=>x.facility_id).sort(),ids.sort());assert.equal(report.refined_facilities,16);
assert.equal(records.filter(r=>r.landmark).length,28);assert.ok(records.find(r=>r.facility_id==='ALD').landmark);
assert.deepEqual(records.find(r=>r.facility_id==='HAG').focus_facilities,['HAG','AVA']);
const selected=new Map(records.filter(r=>ids.includes(r.facility_id)).map(r=>[r.layer,r]));
const bytes=readFileSync(new URL('output/UW_Seattle.3ds',root));
function chunks(from,to){const out=[];for(let a=from;a+6<=to;){const tag=bytes.readUInt16LE(a),n=bytes.readUInt32LE(a+2);assert.ok(n>=6&&a+n<=to);out.push({tag,a,z:a+n});a+=n;}return out;}
const edit=chunks(6,bytes.length).find(c=>c.tag===0x3d3d),kept=[];
for(const c of chunks(edit.a+6,edit.z)){
 if(c.tag!==0x4000){kept.push(bytes.subarray(c.a,c.z));continue;}
 const end=bytes.indexOf(0,c.a+6),name=bytes.toString('ascii',c.a+6,end);
 if(selected.has(layers[name]?.layer))kept.push(bytes.subarray(c.a,c.z));
}
function chunk(tag,body){const h=Buffer.alloc(6);h.writeUInt16LE(tag);h.writeUInt32LE(body.length+6,2);return Buffer.concat([h,body]);}
const mini=chunk(0x4d4d,chunk(0x3d3d,Buffer.concat(kept))),model=new CampusTDSLoader().parse(mini.buffer.slice(mini.byteOffset,mini.byteOffset+mini.byteLength),'');model.updateMatrixWorld(true);
const groups=new Map();model.traverse(m=>{if(!m.isMesh)return;const r=selected.get(layers[m.name]?.layer);if(!r)return;if(!groups.has(r.facility_id))groups.set(r.facility_id,[]);groups.get(r.facility_id).push(m);});
const r=id=>records.find(x=>x.facility_id===id),detail=id=>report.buildings.find(x=>x.facility_id===id);
for(const id of ids){
 const b=r(id),meshes=groups.get(id);assert.ok(meshes?.length,id+' exports its own layer');
 let peak=-Infinity;for(const m of meshes){m.geometry.computeBoundingBox();peak=Math.max(peak,m.geometry.boundingBox.max.z);}
 assert.ok(peak<=b.ground_m+b.height+1.0,'No unsupported facade pieces above the roof: '+id);
}
const k=detail('KNE').validation_probes.recessed_portico;
const portico=new Raycaster(new Vector3(...k.origin),new Vector3(...k.direction)).intersectObjects(groups.get('KNE'),false)[0];
assert.ok(portico&&portico.distance>k.minimum_recess_m&&portico.distance<3.6,'Kane glazing is physically recessed behind its piers');
const p=detail('IEB').validation_probes.arrival_passage;
const obstruction=new Raycaster(new Vector3(...p.origin),new Vector3(...p.direction),0,p.length_m).intersectObjects(groups.get('IEB'),false);
assert.equal(obstruction.length,0,'IEB lower arrival remains an open passage beneath the bridge');
const middle=new Vector3(...p.origin).addScaledVector(new Vector3(...p.direction),p.length_m/2);
const bridge=new Raycaster(new Vector3(middle.x,middle.y,180),new Vector3(0,0,-1)).intersectObjects(groups.get('IEB'),false)[0];
assert.ok(bridge&&bridge.point.z>r('IEB').ground_m+15,'An upper building volume spans the IEB passage');
// The library lawn rises above the main building's flat pad; the four
// curbs follow their own raw DEM samples rather than one shared elevation.
let skylights=0;
for(const x of [-128,-113,-98,-83]){
 const hit=new Raycaster(new Vector3(x,367,180),new Vector3(0,0,-1)).intersectObjects(groups.get('LAW'),false)[0];
 assert.ok(hit&&hit.point.z>r('LAW').ground_m&&hit.point.z<r('LAW').ground_m+6,'Library skylight is present at lawn level');skylights++;
}
for(const [x,y,z]of detail('EDP').validation_probes.arena_ridge){
 const hit=new Raycaster(new Vector3(x,y,180),new Vector3(0,0,-1)).intersectObjects(groups.get('EDP'),false)[0];
 assert.ok(hit&&Math.abs(hit.point.z-z)<.03,'Arena ridge stays continuous across the main roof');
}
assert.ok(r('CSH').ground_m>6&&r('CSH').ground_m<8.5,'Conibear lower boat bay uses the lake-facing grade');
const html=readFileSync(new URL('index.html',root),'utf8'),data=JSON.parse(html.match(/<script id="campus-data"[^>]*>(.*?)<\/script>/s)[1]);
assert.deepEqual(data.landmarkOrder,review.highlight_order);
const result={release:readFileSync(new URL('VERSION',root),'utf8').trim(),highlights:28,rebuilt_facilities:16,alder_second:true,kane_recess_m:portico.distance,ieb_arrival_open:true,law_library_skylights:skylights,conibear_lower_grade_m:r('CSH').ground_m,roof_bounds:true,arena_ridge_continuous:true,subset_parse_bytes:mini.length,passed:true};
writeFileSync(new URL('output/highlight_validation.json',root),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
