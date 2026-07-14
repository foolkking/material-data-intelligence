import type { ImageOffset, RenderVector3 } from "../viewer-scene/viewerSceneRendererTypes";

export const PHONON_ANIMATION_SCHEMA_VERSION = "phase10h5.phonon_animation.v1" as const;
const PACKAGE_FIELDS=new Set(["schema_version","tool_id","source","structure","band_binding","eigenvector_binding","mode","supercell","display","playback","limits","warnings","security","provenance"]);
const FORBIDDEN=new Set(["html","javascript","script","callback","shader","module","url","uri","texture","iframe","code"]);
export type PhononAnimationValidation=Readonly<{valid:boolean;errors:readonly string[]}>;
export type PhononAnimationPackage=Readonly<Record<string,any>>;

export function validatePhononAnimation(payload:unknown):PhononAnimationValidation{
  const errors=new Set<string>();
  if(!record(payload)||!exact(payload,PACKAGE_FIELDS)||payload.schema_version!==PHONON_ANIMATION_SCHEMA_VERSION||payload.tool_id!=="phonon.animation")return result(["PHONON_ANIMATION_SCHEMA_UNSUPPORTED"]);
  const structure=record(payload.structure)?payload.structure:null;const mode=record(payload.mode)?payload.mode:null;const modeRef=mode&&record(mode.mode)?mode.mode:null;const supercell=record(payload.supercell)?payload.supercell:null;const display=record(payload.display)?payload.display:null;const playback=record(payload.playback)?payload.playback:null;
  const sites=structure&&Array.isArray(structure.sites)?structure.sites:[];const lattice=structure&&Array.isArray(structure.lattice)?structure.lattice:[];const vectors=mode&&Array.isArray(mode.eigenvectors)?mode.eigenvectors:[];
  if(!structure||!sha(structure.structure_identity)||typeof structure.formula!=="string"||lattice.length!==3||!lattice.every(triplet)||!sites.length||sites.length>512)errors.add("PHONON_ANIMATION_STRUCTURE_INVALID");
  sites.forEach((site,index)=>{if(!record(site)||site.site_index!==index||typeof site.species!=="string"||!triplet(site.fractional)||!triplet(site.cartesian))errors.add("PHONON_ANIMATION_ATOM_ORDER_MISMATCH");});
  if(!mode||mode.schema_version!=="phase10h.phonon_eigenvector.v1"||mode.atom_count!==sites.length||!Array.isArray(mode.species)||JSON.stringify(mode.species)!==JSON.stringify(sites.map((site)=>record(site)?site.species:null))||vectors.length!==sites.length)errors.add("PHONON_ANIMATION_EIGENVECTOR_INVALID");
  if(!modeRef||!sha(modeRef.mode_id)||!triplet(modeRef.qpoint_coordinates)||!Number.isSafeInteger(modeRef.qpoint_index)||!Number.isSafeInteger(modeRef.branch_index)||!finite(modeRef.frequency))errors.add("PHONON_ANIMATION_MODE_INVALID");
  vectors.forEach((vector,index)=>{if(!record(vector)||vector.atom_index!==index||!triplet(vector.real)||!triplet(vector.imag))errors.add("PHONON_ANIMATION_EIGENVECTOR_INVALID");});
  const repeat=supercell?.repeat;if(!repeatTuple(repeat)||supercell?.displayed_atom_count!==sites.length*(repeat as number[]).reduce((a,b)=>a*b,1)||supercell?.commensurate!==true||supercell?.renderer_local!==true)errors.add("PHONON_ANIMATION_SUPERCELL_INVALID");
  if(modeRef&&repeatTuple(repeat)&&(repeat as number[]).some((value,index)=>Math.abs(Number(modeRef.qpoint_coordinates[index])*value-Math.round(Number(modeRef.qpoint_coordinates[index])*value))>1e-8))errors.add("PHONON_ANIMATION_NONCOMMENSURATE");
  if(!display||!finite(display.display_scale)||display.display_scale<0.01||display.display_scale>1||typeof display.show_vectors!=="boolean"||typeof display.show_trails!=="boolean")errors.add("PHONON_ANIMATION_DISPLAY_INVALID");
  if(!playback||playback.default_state!=="paused"||playback.reduced_motion_forces_paused!==true||typeof playback.autoplay!=="boolean"||!finite(playback.cycles_per_second)||playback.cycles_per_second<0.05||playback.cycles_per_second>2)errors.add("PHONON_ANIMATION_PLAYBACK_INVALID");
  inert(payload,errors);return result([...errors]);
}

export function animationDisplacements(payload:PhononAnimationPackage,phase:number,offset:ImageOffset,displayScale?:number):readonly RenderVector3[]{
  if(!finite(phase)||!repeatOffset(offset))throw new Error("PHONON_DISPLACEMENT_REQUEST_INVALID");
  const mode=payload.mode as Record<string,any>;const masses=mode.atomic_masses.values as number[];const q=mode.mode.qpoint_coordinates as number[];
  const vectors=(mode.eigenvectors as Array<Record<string,any>>).map((value,index)=>(value.real as number[]).map((real,axis)=>({real:real/Math.sqrt(masses[index]),imag:Number(value.imag[axis])/Math.sqrt(masses[index])})));
  const envelope=Math.max(...vectors.map((vector)=>Math.sqrt(vector.reduce((sum,value)=>sum+value.real*value.real+value.imag*value.imag,0))));if(!finite(envelope)||envelope<=1e-12)throw new Error("PHONON_DISPLACEMENT_DEGENERATE");
  const angle=2*Math.PI*(q[0]*offset[0]+q[1]*offset[1]+q[2]*offset[2])+phase;const cos=Math.cos(angle),sin=Math.sin(angle);const scale=(displayScale??Number(payload.display.display_scale))/envelope;
  return Object.freeze(vectors.map((vector)=>tuple(vector.map((value)=>scale*(value.real*cos-value.imag*sin)))));
}

function inert(value:unknown,errors:Set<string>):void{if(record(value)){for(const[key,child]of Object.entries(value)){if(FORBIDDEN.has(key.toLowerCase()))errors.add("PHONON_ANIMATION_EXECUTABLE_CONTENT_FORBIDDEN");inert(child,errors);}}else if(Array.isArray(value))value.forEach((child)=>inert(child,errors));else if(typeof value==="string"&&(/<script/i.test(value)||/javascript:/i.test(value)||/https?:\/\//i.test(value)))errors.add("PHONON_ANIMATION_EXTERNAL_CONTENT_FORBIDDEN");}
function result(errors:string[]):PhononAnimationValidation{return Object.freeze({valid:errors.length===0,errors:Object.freeze([...new Set(errors)].sort())});}
function record(value:unknown):value is Record<string,any>{return Boolean(value)&&typeof value==="object"&&!Array.isArray(value);}
function exact(value:Record<string,any>,fields:Set<string>){return Object.keys(value).length===fields.size&&Object.keys(value).every((key)=>fields.has(key));}
function finite(value:unknown):value is number{return typeof value==="number"&&Number.isFinite(value);}
function triplet(value:unknown):value is number[]{return Array.isArray(value)&&value.length===3&&value.every(finite);}
function repeatTuple(value:unknown):value is number[]{return Array.isArray(value)&&value.length===3&&value.every((item)=>Number.isSafeInteger(item)&&item>=1&&item<=3);}
function repeatOffset(value:unknown):value is ImageOffset{return Array.isArray(value)&&value.length===3&&value.every(Number.isSafeInteger);}
function sha(value:unknown){return typeof value==="string"&&/^[0-9a-f]{64}$/.test(value);}
function tuple(value:number[]):RenderVector3{return Object.freeze([value[0],value[1],value[2]]);}
