/** Focused export checks for actual station/bridge/canopy walking surfaces. */
import assert from 'node:assert/strict';
import{readFileSync,writeFileSync}from'node:fs';
import{Raycaster,Vector3}from'three';
import{CampusTDSLoader}from'./campus_tds_loader.js';
import{createOutdoorPicker}from'./outdoor_hover.js';
const root=new URL('../',import.meta.url),read=p=>JSON.parse(readFileSync(new URL(p,root),'utf8'));
const records=read('output/buildings.json'),neighbors=read('output/neighboring_records.json'),report=read('output/transit_refinement.json'),block=read('output/alder_block_refinement.json'),layers=read('output/layer_map.json');
const uw=records.find(r=>r.facility_id==='LINK_UW'),alder=records.find(r=>r.facility_id==='ALD'),ud=neighbors.find(r=>r.name==='U District Station South Entrance');
assert.ok(uw&&alder&&ud);assert.equal(uw.code,'W272');assert.equal(alder.code,'W105');assert.equal(ud.code,'N380');assert.ok(uw.footprint_source.includes('325150399'));assert.equal(uw.levels,2);
assert.ok(report.facilities.some(r=>r.facility_id==='U_DISTRICT_NORTH'&&r.integrated_in==='Gateway Building'));
assert.deepEqual(block.bus_stops.map(r=>r.stop_id).sort(),['9575','9580']);
const bytes=readFileSync(new URL('output/UW_Seattle.3ds',root)),model=new CampusTDSLoader().parse(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');model.updateMatrixWorld(true);
const bridge=[],canopies=[],shelters=[],south=[];model.traverse(m=>{if(!m.isMesh)return;const mat=Array.isArray(m.material)?m.material:[m.material];if(mat.some(r=>r.name==='BridgeDeck')||mat.some(r=>r.name==='Concrete')&&(layers[m.name]?.category==='environment'||layers[m.name]?.layer===uw.layer))bridge.push(m);if(layers[m.name]?.layer===alder.layer)canopies.push(m);if(layers[m.name]?.category==='environment'&&mat.some(r=>r.name==='Glass'))shelters.push(m);if(layers[m.name]?.layer===ud.layer)south.push(m);});
const top=(x,y,meshes)=>new Raycaster(new Vector3(x,y,150),new Vector3(0,0,-1)).intersectObjects(meshes,false)[0]?.point.z;
const level=report.facilities.find(r=>r.facility_id==='UW_STATION_BRIDGE').deck_height_m;let bridgeProbes=0;
for(const[x,y]of [[371.1545,-579.2263],[386.4758,-584.2682],[413.6632,-634.3],[406.1887,-614.1899]])for(const[dx,dy]of [[0,0],[.15,0],[-.15,0],[0,.15],[0,-.15]]){
 const z=top(x+dx,y+dy,bridge);assert.ok(Number.isFinite(z)&&Math.abs(z-level)<.035,`Continuous bridge/stair landing ${x+dx},${y+dy}: ${z}`);bridgeProbes++;
}
for(const stop of block.bus_stops){
 const s=stop.shelter,[x,y]=s.center,z=top(x,y,shelters);
 assert.ok(Number.isFinite(z)&&Math.abs(z-s.roof_elevation_m)<.025,'Each mapped stop has its independent shelter roof');
 const gap=top(x,y+1.4,shelters);assert.equal(gap,undefined,'Shelter does not cover the curb/boarding lane');
}
// Probe the actual recessed north arcade from the street: opaque podium must
// no longer fill the space between the concrete piers and the timber/glass wall.
const front=new Raycaster(new Vector3(-329.3,8,alder.ground_m+2.6),new Vector3(0,-1,0)).intersectObjects(canopies,false)[0];
assert.ok(front&&front.point.y<1.5,'North shopfront is recessed behind the upper wing');
assert.equal(block.architecture.false_passage_removed,true);
const sz=top(-355,459,south);assert.ok(Number.isFinite(sz)&&sz>ud.ground_m+5&&sz<ud.ground_m+7,'South entrance is a low tapered headhouse, not a tall generic office');
const data=JSON.parse(readFileSync(new URL('index.html',root),'utf8').match(/<script id="campus-data"[^>]*>(.*?)<\/script>/s)[1]),picker=createOutdoorPicker(data.places);
const north=picker(-373,552);assert.ok(north?.name.includes('U District'));assert.equal(picker(-373,552,p=>!p.neighbor),null,'Hidden neighboring transit approach has no hover label');assert.ok(picker(-325,9)?.name.includes('Bay 2'));
const result={release:readFileSync(new URL('VERSION',root),'utf8').trim(),station:'University of Washington Station',stable_layer_codes:[uw.code,alder.code,ud.code],bridge_landing_probes:bridgeProbes,independent_bus_shelters:2,north_arcade_recess:true,grounded_south_entrance:true,neighbor_hover_visibility:true,passed:true};writeFileSync(new URL('output/transit_validation.json',root),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
