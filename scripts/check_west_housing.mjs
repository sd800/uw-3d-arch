/** Focused export regression: housing identity, open courts and unchanged Alder. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {Raycaster,Vector3} from 'three';
import {CampusTDSLoader} from './campus_tds_loader.js';
const root=new URL('../',import.meta.url),read=p=>JSON.parse(readFileSync(new URL(p,root),'utf8'));
const report=read('output/west_housing_refinement.json'),records=read('output/buildings.json'),layers=read('output/layer_map.json'),review=read('sources/west_housing_review.json');
const expected=['CDRW','CDRE','ELM','POP','LAN','TEH','MAH','MRCA','MRCB','MRCC','MRCD','MRCE','SCA','SCB','SCC','SCD','SCH','SCJ','SCK','SCL','SCM'].sort();
assert.deepEqual(report.buildings.map(x=>x.facility_id).sort(),expected);
assert.equal(report.alder_unchanged,true);assert.equal(report.automatic_rooftop_boxes,false);
const selected=new Map(records.filter(r=>expected.includes(r.facility_id)||r.facility_id==='ALD').map(r=>[r.layer,r]));
const bytes=readFileSync(new URL('output/UW_Seattle.3ds',root));
const sha=b=>createHash('sha256').update(b).digest('hex');
function chunks(from,to){const out=[];for(let a=from;a+6<=to;){const tag=bytes.readUInt16LE(a),n=bytes.readUInt32LE(a+2);assert.ok(n>=6&&a+n<=to);out.push({tag,a,z:a+n});a+=n;}return out;}
const edit=chunks(6,bytes.length).find(c=>c.tag===0x3d3d),kept=[],hashes=[];let omittedSmoothing=0;
for(const c of chunks(edit.a+6,edit.z)){
 if(c.tag!==0x4000){kept.push(bytes.subarray(c.a,c.z));continue;}
 const end=bytes.indexOf(0,c.a+6),name=bytes.toString('ascii',c.a+6,end),record=selected.get(layers[name]?.layer);
 if(!record)continue;
 kept.push(bytes.subarray(c.a,c.z));const payload=[];
 for(const mesh of chunks(end+1,c.z))if(mesh.tag===0x4100)for(const p of chunks(mesh.a+6,mesh.z)){
  if(p.tag===0x4110)payload.push(bytes.subarray(p.a,p.z));
  else if(p.tag===0x4120){
   const count=bytes.readUInt16LE(p.a+6),faceEnd=p.a+8+8*count;payload.push(bytes.subarray(p.a+6,faceEnd));
   for(const q of chunks(faceEnd,p.z)){if(q.tag===0x4150)omittedSmoothing++;else payload.push(bytes.subarray(q.a,q.z));}
  }
 }
 if(record.facility_id==='ALD')hashes.push([name,sha(Buffer.concat(payload))]);
}
assert.equal(omittedSmoothing,0,'All-zero smoothing groups are omitted without changing geometry');
const canonical='['+hashes.sort((a,b)=>a[0].localeCompare(b[0])).map(x=>'['+JSON.stringify(x[0])+', '+JSON.stringify(x[1])+']').join(', ')+']';
assert.equal(sha(canonical),review.alder_baseline.geometry_sha256,'Alder vertex/index/material data must remain unchanged');
function chunk(tag,body){const h=Buffer.alloc(6);h.writeUInt16LE(tag);h.writeUInt32LE(body.length+6,2);return Buffer.concat([h,body]);}
const mini=chunk(0x4d4d,chunk(0x3d3d,Buffer.concat(kept)));
const model=new CampusTDSLoader().parse(mini.buffer.slice(mini.byteOffset,mini.byteOffset+mini.byteLength),'');model.updateMatrixWorld(true);
const groups=new Map(),materials=new Map();
model.traverse(m=>{if(!m.isMesh)return;const r=selected.get(layers[m.name]?.layer);if(!r)return;if(!groups.has(r.facility_id)){groups.set(r.facility_id,[]);materials.set(r.facility_id,new Set());}groups.get(r.facility_id).push(m);for(const mat of Array.isArray(m.material)?m.material:[m.material])materials.get(r.facility_id).add(mat.name);});
const top=(id,x,y)=>new Raycaster(new Vector3(x,y,180),new Vector3(0,0,-1)).intersectObjects(groups.get(id),false)[0]?.point.z;
const r=id=>records.find(r=>r.facility_id===id);
let rays=0;
for(const[x,y]of [[-352,-20],[-341,-18],[-333,-6]]){assert.equal(top('ALD',x,y),undefined,'Alder court stays open to the sky');rays++;}
assert.equal(top('MAH',-515,-18),undefined,'Maple mapped court stays open');rays++;
assert.equal(top('LAN',-430,-22),undefined,'Lander U-shaped court stays open');rays++;
for(const[id,x,y]of [['CDRW',-524,152],['CDRE',-504,145],['POP',-373.4,80]]){
 const z=top(id,x,y);assert.ok(Number.isFinite(z)&&z>r(id).ground_m+3.8&&z<r(id).ground_m+6,'Recessed court/deck is below the tall surrounding roof: '+id);rays++;
}
for(const id of expected){
 const b=r(id),meshes=groups.get(id);assert.ok(meshes?.length,id+' has its own geometry/layer');
 let peak=-Infinity;for(const m of meshes){m.geometry.computeBoundingBox();peak=Math.max(peak,m.geometry.boundingBox.max.z);}
 assert.ok(peak<=b.ground_m+b.height+1.1,'No facade members project above the roof: '+id);
}
for(const id of ['CDRE','CDRW','ELM','POP'])assert.ok(materials.get(id).has('HousingCharcoal'));
for(const id of ['MAH','TEH'])assert.ok(materials.get(id).has('HousingBrick'));
assert.ok(materials.get('LAN').has('HousingCopper')&&materials.get('LAN').has('HousingPanel'));
// Copper belongs to the photographed northeast lounge, not the U court.
const landerBounds=groups.get('LAN').map(m=>m.geometry.boundingBox),east=Math.max(...landerBounds.map(b=>b.max.x)),north=Math.max(...landerBounds.map(b=>b.max.y));
for(const mesh of groups.get('LAN')){
 const mats=Array.isArray(mesh.material)?mesh.material:[mesh.material],p=mesh.geometry.attributes.position,idx=mesh.geometry.index;
 for(const g of mesh.geometry.groups)if(mats[g.materialIndex]?.name==='HousingCopper')for(let k=g.start;k<g.start+g.count;k++){
  const i=idx.getX(k);assert.ok(p.getX(i)>east-17&&p.getY(i)>north-23,'Lander copper lounge stays at the northeast exterior corner');
 }
}

for(const id of expected.filter(x=>x.startsWith('MRC')))assert.ok(materials.get(id).has('HousingSilver'));
for(const id of expected.filter(x=>x.startsWith('SC')))assert.ok(materials.get(id).has('Slate'));
const result={release:readFileSync(new URL('VERSION',root),'utf8').trim(),facilities:expected.length,alder_geometry_unchanged:true,court_and_deck_rays:rays,distinct_facade_materials:true,roof_member_bounds:true,lander_lounge_confined_to_northeast:true,redundant_smoothing_groups:omittedSmoothing,subset_parse_bytes:mini.length,passed:true};
writeFileSync(new URL('output/west_housing_validation.json',root),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
