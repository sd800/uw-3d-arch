import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {Raycaster,Vector3} from 'three';
import {CampusTDSLoader} from './campus_tds_loader.js';
const root=new URL('../',import.meta.url),records=JSON.parse(readFileSync(new URL('output/buildings.json',root))),r=records.find(r=>r.facility_id==='ALD'),layers=JSON.parse(readFileSync(new URL('output/layer_map.json',root)));
const bytes=readFileSync(new URL('output/UW_Seattle.3ds',root)),model=new CampusTDSLoader().parse(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');model.updateMatrixWorld(true);const building=[],ground=[];
model.traverse(m=>{if(!m.isMesh)return;if(layers[m.name]?.layer===r.layer)building.push(m);else if((Array.isArray(m.material)?m.material:[m.material]).some(m=>m.name==='Ground'))ground.push(m);});
let skyChecks=0;for(const [x,y]of [[-352,-20],[-341,-18],[-333,-6]]){
 const ray=new Raycaster(new Vector3(x,y,r.ground_m+100),new Vector3(0,0,-1));assert.equal(ray.intersectObjects(building,false).length,0,'No building or roof cap covers the mapped light court');const hits=ray.intersectObjects(ground,false);assert.ok(hits.length,'The court has physical ground');assert.ok(Math.abs(hits[0].point.z-r.ground_m)<.02);skyChecks++;
}
for(const [x,y]of [[-368,-20],[-316,-20],[-350,1],[-341,-38]]){const ray=new Raycaster(new Vector3(x,y,r.ground_m+100),new Vector3(0,0,-1));const hit=ray.intersectObjects(building,false)[0];assert.ok(hit&&hit.point.z>r.ground_m+18,'Each enclosing wing retains its roof');}
console.log('Alder Hall passed: '+skyChecks+' open-sky court rays, 4 surrounding roof wings, and level courtyard ground.');
