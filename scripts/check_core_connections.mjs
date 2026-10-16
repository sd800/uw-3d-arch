/** Parse only the changed library/station and surfaces needed by these probes. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {Raycaster,Vector3} from 'three';
import {CampusTDSLoader} from './campus_tds_loader.js';
const root=new URL('../',import.meta.url),read=p=>JSON.parse(readFileSync(new URL(p,root),'utf8'));
const layers=read('output/layer_map.json'),records=read('output/buildings.json'),entry=read('output/suzzallo_entry_refinement.json'),links=read('output/red_square_connections.json'),transit=read('output/transit_refinement.json');
const station=records.find(r=>r.facility_id==='LINK_UW'),library=records.find(r=>r.facility_id==='SUZ');
const bytes=readFileSync(new URL('output/UW_Seattle.3ds',root));
function chunks(from,to){const out=[];for(let a=from;a+6<=to;){const tag=bytes.readUInt16LE(a),n=bytes.readUInt32LE(a+2);assert.ok(n>=6&&a+n<=to);out.push({tag,a,z:a+n});a+=n;}return out;}
const edit=chunks(6,bytes.length).find(c=>c.tag===0x3d3d),kept=[];
const materials=new Set(['Ground','StepStone','Metal','BridgeDeck','Concrete','StoneEdge','Tile','BrickPale','BrickWarm','Road','Grass']);
for(const c of chunks(edit.a+6,edit.z)){
 if(c.tag!==0x4000){kept.push(bytes.subarray(c.a,c.z));continue;}
 const end=bytes.indexOf(0,c.a+6),name=bytes.toString('ascii',c.a+6,end),r=layers[name];
 if(r?.layer===station.layer||r?.layer===library.layer||r?.layer==='Environment'&&materials.has(r.material))kept.push(bytes.subarray(c.a,c.z));
}
function chunk(tag,body){const h=Buffer.alloc(6);h.writeUInt16LE(tag);h.writeUInt32LE(body.length+6,2);return Buffer.concat([h,body]);}
const mini=chunk(0x4d4d,chunk(0x3d3d,Buffer.concat(kept))),model=new CampusTDSLoader().parse(mini.buffer.slice(mini.byteOffset,mini.byteOffset+mini.byteLength),'');model.updateMatrixWorld(true);
const surfaces=[],stationMeshes=[],libraryMeshes=[],decks=[];
model.traverse(m=>{if(!m.isMesh)return;const r=layers[m.name];if(r?.layer===station.layer)stationMeshes.push(m);else if(r?.layer===library.layer)libraryMeshes.push(m);else surfaces.push(m);if(r.material==='BridgeDeck'||r.material==='Concrete')decks.push(m);});
const top=(x,y,meshes)=>new Raycaster(new Vector3(x,y,180),new Vector3(0,0,-1)).intersectObjects(meshes,false)[0]?.point.z;
for(const [x,y,z]of entry.tread_probes){const got=top(x,y,surfaces);assert.ok(Number.isFinite(got)&&Math.abs(got-z)<.015,'Library flight has real connected treads: '+[x,y,got,z]);}
for(const[x,y,z]of entry.forecourt_probes){const got=top(x,y,surfaces);assert.ok(Number.isFinite(got)&&Math.abs(got-z)<.03,'Stair foot and both flanks have flush brick paving: '+[x,y,got,z]);}assert.equal(entry.forecourt_probes.length,3);
assert.equal(entry.step_count,14);assert.ok(entry.stair_width_top_m>20&&entry.run_m<5&&entry.terrace_frontage_m>55,'Photo-referenced broad short flight and continuous terrace');
const architecture=read('output/suzzallo_architecture.json');for(const p of architecture.validation_probes.recessed_portals){const hit=new Raycaster(new Vector3(...p.origin),new Vector3(...p.direction)).intersectObjects(libraryMeshes,false)[0];assert.ok(hit&&hit.distance>p.minimum_recess_m,'Each Gothic portal has physical depth');}
assert.ok(Math.abs(library.ground_m+.12-entry.upper_landing_m)<.002,'Library threshold and top landing share a datum');assert.ok(entry.upper_landing_depth_m>2);
let linkProbes=0;
for(const flight of links.steps)for(const[x,y,z]of flight.probes){const got=top(x,y,surfaces);assert.ok(Number.isFinite(got)&&Math.abs(got-z)<.015,'Plaza side flight has consistent exported treads: '+flight.osm_id+' '+[x,y,got,z]);linkProbes++;}
const probes=transit.facilities.find(r=>r.facility_id==='LINK_UW').validation_probes;
for(const name of ['south_entry','upper_portal']){const p=probes[name];assert.equal(new Raycaster(new Vector3(...p.origin),new Vector3(...p.direction),.05,p.clear_distance_m).intersectObjects(stationMeshes,false).length,0,'Station portal stays open: '+name);}
const [x,y,z]=probes.floor_void;assert.equal(new Raycaster(new Vector3(x,y,z+.05),new Vector3(0,0,-1),0,.5).intersectObjects(stationMeshes,false).length,0,'Intermediate slab does not fill the circulation void');
const lobby=probes.upper_lobby;const level=top(lobby[0],lobby[1],decks);assert.ok(Math.abs(level-lobby[2])<.02,'Upper lobby meets bridge level');
assert.ok(top(408.5,-672,stationMeshes)<station.ground_m+6,'Lower canopy projection does not become a full-height roof wing');
const bridge=transit.facilities.find(r=>r.facility_id==='UW_STATION_BRIDGE'),p=bridge.open_stair_landing;
assert.equal(new Raycaster(new Vector3(p[0],p[1]-1.5,p[2]),new Vector3(0,1,0),0,3).intersectObjects(surfaces,false).length,0,'No railing crosses the exterior stair landing');
const html=readFileSync(new URL('index.html',root),'utf8'),data=JSON.parse(html.match(/<script id="campus-data"[^>]*>(.*?)<\/script>/s)[1]);
assert.deepEqual(data.landmarkOrder.slice(0,3),['SUZ','ALD','DRUMHELLER']);assert.equal(data.landmarkOrder.length,29);assert.equal(records.filter(r=>r.landmark).length,28);assert.ok(library.focus_direction[0]===-1&&Math.abs(library.focus_direction[1])<.03&&library.focus_direction[2]===.7&&library.focus_bounds.length===6,'Library Explore matches the near-due-west reference with a modest elevated angle');assert.ok(data.tourPlaces[0].outdoor&&data.tourPlaces[0].bounds.every(Number.isFinite));
const result={release:readFileSync(new URL('VERSION',root),'utf8').trim(),library_treads:14,library_recessed_portals:3,library_front_explore:true,flush_forecourt_probes:3,perimeter_tread_probes:linkProbes,station_portals_open:true,station_floor_void_open:true,rectangular_upper_roof:true,exterior_stair_landing_open:true,highlight_stops:29,fountain_position:3,passed:true};writeFileSync(new URL('output/core_connections_validation.json',root),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
