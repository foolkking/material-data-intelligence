import { fractionalToCartesian, validateTrajectoryReference } from "../../lib/trajectoryContract";
import type { ImageOffset, RenderAtom, RenderVector3, ValidatedRenderScene } from "../viewer-scene/viewerSceneRendererTypes";
import { supercellOffsets, validSupercellRepeat } from "../viewer-scene/viewerSceneSupercell";
import type { MappedTrajectoryFrame, TrajectoryPerformanceDecision, ValidatedTrajectory } from "./trajectoryViewerTypes";

const PALETTE=["#2f7f8f","#d56a45","#7b61a8","#4f8d58","#c08b28","#476aa3","#a74f6f","#64748b"] as const;
const RADII:Readonly<Record<string,number>>=Object.freeze({H:0.38,C:0.68,N:0.65,O:0.62,Na:0.9,Si:0.78,Cl:0.82});
export type TrajectoryMappingResult={readonly ok:true;readonly trajectory:ValidatedTrajectory}|{readonly ok:false;readonly errors:readonly string[]};

export function validateTrajectoryForViewer(payload:unknown):TrajectoryMappingResult{
  const validation=validateTrajectoryReference(payload);
  return validation.valid?{ok:true,trajectory:payload as ValidatedTrajectory}:{ok:false,errors:Object.freeze(validation.errors.map((error)=>error.replace(/^TRAJECTORY_/,"TRAJECTORY_VIEWER_")))};
}
export function classifyTrajectoryViewer(trajectory:ValidatedTrajectory,repeat:ImageOffset=Object.freeze([1,1,1]),mobile=false):TrajectoryPerformanceDecision{
  if(!validSupercellRepeat(repeat))return Object.freeze({mode:"refused",displayedInstances:0,cacheFrames:0,cacheBytes:0,maxPlaybackFps:15,warnings:Object.freeze([]),reason:"TRAJECTORY_VIEWER_BUDGET_EXCEEDED"});
  const cells=repeat[0]*repeat[1]*repeat[2];const displayedInstances=trajectory.atoms.count*cells;const coordinateValues=trajectory.frames.length*trajectory.atoms.count*3;
  const refused=displayedInstances>768||coordinateValues>2_000_000;const degraded=!refused&&(displayedInstances>384||coordinateValues>300_000);
  return Object.freeze({mode:refused?"refused":degraded?"degraded":"interactive",displayedInstances,cacheFrames:mobile?3:degraded?4:7,cacheBytes:mobile?4_194_304:degraded?8_388_608:16_777_216,maxPlaybackFps:mobile||degraded?15:30,warnings:Object.freeze(degraded?["TRAJECTORY_VIEWER_DEGRADED_MODE"]:[]),reason:refused?"TRAJECTORY_VIEWER_BUDGET_EXCEEDED":null});
}
export function mapTrajectoryFrame(trajectory:ValidatedTrajectory,frameIndex:number,repeat:ImageOffset=Object.freeze([1,1,1])):MappedTrajectoryFrame{
  const started=performance.now();if(!Number.isSafeInteger(frameIndex)||frameIndex<0||frameIndex>=trajectory.frames.length)throw new Error("TRAJECTORY_VIEWER_FRAME_INDEX_INVALID");if(!validSupercellRepeat(repeat))throw new Error("TRAJECTORY_VIEWER_BUDGET_EXCEEDED");
  const frame=trajectory.frames[frameIndex];const lattice=(trajectory.lattice_mode==="fixed"?trajectory.fixed_lattice:frame.lattice);if(!lattice)throw new Error("TRAJECTORY_VIEWER_LATTICE_MISSING");
  const speciesOrder=[...new Set(trajectory.atoms.records.map((atom)=>atom.species))].sort();const offsets=supercellOffsets(repeat);const atoms:RenderAtom[]=[];
  for(const offset of offsets)for(const atom of trajectory.atoms.records){const raw=frame.positions[atom.atom_id];const canonical=trajectory.coordinate_mode==="fractional"?fractionalToCartesian(raw,lattice):[...raw] as RenderVector3;const translation=translate(offset,lattice);const position=tuple(canonical[0]+translation[0],canonical[1]+translation[1],canonical[2]+translation[2]);const ref=Object.freeze({siteIndex:atom.atom_id,imageOffset:Object.freeze([...offset]) as ImageOffset});atoms.push(Object.freeze({id:`atom:${atom.atom_id}@[${offset.join(",")}]`,siteIndex:atom.atom_id,ref,species:atom.species,label:atom.label,element:atom.species,occupancy:atom.occupancy,position,canonicalPosition:tuple(...canonical),fractionalPosition:trajectory.coordinate_mode==="fractional"?tuple(...raw):null,radius:RADII[atom.species]??0.72,color:PALETTE[speciesOrder.indexOf(atom.species)%PALETTE.length]}));}
  const displayMatrix=Object.freeze(lattice.map((row,axis)=>tuple(row[0]*repeat[axis],row[1]*repeat[axis],row[2]*repeat[axis]))) as ValidatedRenderScene["lattice"]["matrix"];
  const scene:ValidatedRenderScene=Object.freeze({contractVersion:"trajectory.v1",schemaVersion:"phase10g.trajectory.v1",atoms:Object.freeze(atoms),bonds:Object.freeze([]),lattice:Object.freeze({matrix:lattice}),displayLattice:Object.freeze({matrix:displayMatrix}),supercellRepeat:Object.freeze([...repeat]) as ImageOffset,source:Object.freeze({resourceId:trajectory.trajectory_id,filename:"trajectory.json",parser:"validated-trajectory"}),formula:speciesOrder.join(""),warnings:Object.freeze(trajectory.position_wrapping==="unknown"?[...trajectory.warnings,"TRAJECTORY_VIEWER_WRAPPING_UNKNOWN"]:trajectory.warnings)});
  return Object.freeze({frameIndex,scene,lattice,rawFrame:frame,mapMs:performance.now()-started,estimatedBytes:atoms.length*160+512});
}
function translate(offset:ImageOffset,lattice:ValidatedRenderScene["lattice"]["matrix"]):RenderVector3{return tuple(offset[0]*lattice[0][0]+offset[1]*lattice[1][0]+offset[2]*lattice[2][0],offset[0]*lattice[0][1]+offset[1]*lattice[1][1]+offset[2]*lattice[2][1],offset[0]*lattice[0][2]+offset[1]*lattice[1][2]+offset[2]*lattice[2][2]);}
function tuple(x:number,y:number,z:number):RenderVector3{return Object.freeze([x,y,z]);}
