import assert from 'node:assert/strict';
import {readFileSync,writeFileSync}from'node:fs';
import{Raycaster,Vector3}from'three';
import{CampusTDSLoader}from'./campus_tds_loader.js';
const root=new URL('../',import.meta.url).pathname;
const read=p=>JSON.parse(readFileSync(root+p,'utf8'));
const records=read('output/buildings.json'),layers=read('output/layer_map.json'),report=read('output/gatehouse_refinement.json'),gate=records.find(r=>r.facility_id==='GH5');
assert.equal(gate.levels,1);assert.equal(gate.height,3.08);assert.ok(report.island_area_m2>40);
const bytes=readFileSync(root+'output/UW_Seattle.3ds');
function chunks(a,z){let out=[];while(a+6<=z){let tag=bytes.readUInt16LE(a),n=bytes.readUInt32LE(a+2);assert.ok(n>=6&&a+n<=z);out.push({tag,a,z:a+n});a+=n;}return out;}
const edit=chunks(6,bytes.length).find(c=>c.tag===0x3d3d),kept=[];
for(const c of chunks(edit.a+6,edit.z)){
 if(c.tag!==0x4000){kept.push(bytes.subarray(c.a,c.z));continue;}
 const e=bytes.indexOf(0,c.a+6),name=bytes.toString('ascii',c.a+6,e),r=layers[name];
 if(r?.layer===gate.layer||r?.layer==='Environment'&&['Road','Paving','Concrete','BrickRed'].includes(r.material))kept.push(bytes.subarray(c.a,c.z));
}
function chunk(t,b){let h=Buffer.alloc(6);h.writeUInt16LE(t);h.writeUInt32LE(b.length+6,2);return Buffer.concat([h,b]);}
const mini=chunk(0x4d4d,chunk(0x3d3d,Buffer.concat(kept))),model=new CampusTDSLoader().parse(mini.buffer.slice(mini.byteOffset,mini.byteOffset+mini.byteLength),'');model.updateMatrixWorld(true);
let materials=new Set(),peak=-Infinity,roads=[],curbs=[];
model.traverse(m=>{if(!m.isMesh)return;let r=layers[m.name];if(r?.layer===gate.layer){materials.add(r.material);m.geometry.computeBoundingBox();peak=Math.max(peak,m.geometry.boundingBox.max.z);}if(r?.layer==='Environment'&&r.material==='Road')roads.push(m);if(r?.layer==='Environment'&&r.material==='Concrete')curbs.push(m);});
for(const m of ['DarkGlass','Purple','HousingCharcoal','RoofMetal'])assert.ok(materials.has(m));
assert.ok(Math.abs(peak-gate.ground_m-3.08)<.01);
const top=(x,y,meshes)=>new Raycaster(new Vector3(x,y,180),new Vector3(0,0,-1)).intersectObjects(meshes,false)[0]?.point.z;
const ring=report.island.coordinates[0];
function inside(x,y){let yes=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){let a=ring[i],b=ring[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes;}
let clear=0;
for(let x=-183;x<-161;x+=1.1)for(let y=-63;y<-53;y+=1.1){if(!inside(x,y))continue;assert.equal(top(x,y,roads),undefined,'Asphalt must not cover traffic island '+[x,y]);clear++;}
for(const p of [[-175,-51],[-175,-59.5]])assert.ok(Number.isFinite(top(...p,roads)),'Both mapped carriageways remain open');
const result={facility:'GH5',height_m:gate.height,glazed_booth:true,low_gabled_roof:true,island_asphalt_clearance_probes:clear,carriageways_retained:2,passed:true};
writeFileSync(root+'output/gatehouse_validation.json',JSON.stringify(result,null,2)+'\n');console.log(result);
