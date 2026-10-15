/** Read back actual painted 3DS faces at the satellite-reviewed crossing paths. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {Raycaster,Vector3,Box3} from 'three';
import {CampusTDSLoader} from './campus_tds_loader.js';
const root=new URL('../',import.meta.url),read=p=>JSON.parse(readFileSync(new URL(p,root)));
const source=read('sources/alder_crosswalks.json'),review=read('output/alder_crosswalk_review.json'),layers=read('output/layer_map.json');
assert.equal(source.crossings.length,20);assert.equal(review.count,20);assert.equal(new Set(review.crossings.map(r=>r.id)).size,20);
const counts=Object.groupBy(source.crossings,r=>r.intersection);assert.deepEqual(Object.values(counts).map(a=>a.length).sort(),[4,4,6,6]);
assert.equal(review.paint_on_road_only,true);
const data=readFileSync(new URL('output/UW_Seattle.3ds',root)),model=new CampusTDSLoader().parse(data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength),'');model.updateMatrixWorld(true);
const paint=[];model.traverse(m=>{if(!m.isMesh||layers[m.name]?.category!=='environment')return;const mats=Array.isArray(m.material)?m.material:[m.material];if(mats.some(a=>a.name==='Marking'))paint.push({mesh:m,box:new Box3().setFromObject(m)});});
let probes=0;
for(const row of review.crossings){
 const ref=source.crossings.find(r=>r.id===row.id);assert.ok(ref&&ref.reference.endsWith('/'+row.id));assert.ok(row.paired_stripe_count>=6);
 for(const [x,y]of row.probe_points){
  const candidates=paint.filter(r=>x>=r.box.min.x&&x<=r.box.max.x&&y>=r.box.min.y&&y<=r.box.max.y).map(r=>r.mesh);
  const hit=new Raycaster(new Vector3(x,y,150),new Vector3(0,0,-1)).intersectObjects(candidates,false)[0];
  assert.ok(hit,'Paint missing at reviewed crossing '+row.id+' / '+x+','+y);probes++;
 }
}
const result={crossings:review.count,intersections:4,exported_paint_probes:probes,paired_stripes:true,road_clipping:true,passed:true};
writeFileSync(new URL('output/alder_crosswalk_validation.json',root),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
