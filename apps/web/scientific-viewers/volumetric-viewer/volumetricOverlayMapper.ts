import { mapViewerSceneForRenderer } from "../viewer-scene/viewerSceneRendererMapper";
import type { ValidatedVolumetricBundle, VolumetricStructureOverlay, VolumeMatrix3, VolumeVector3 } from "./volumetricViewerTypes";

type JsonRecord = Record<string, unknown>;

const ELEMENTS=["","H","He","Li","Be","B","C","N","O","F","Ne","Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg","Cn","Nh","Fl","Mc","Lv","Ts","Og"] as const;
const PALETTE=["#5b8ff9","#73c0de","#61dDAA","#f6bd16","#e8684a","#9270ca","#ff9d4d","#269a99"] as const;
const SHA=/^[0-9a-f]{64}$/;
const FORBIDDEN=["http://","https://","javascript:","<script","<iframe","file://"];

export function mapVolumetricStructureOverlay(value: unknown, bundle: ValidatedVolumetricBundle): Readonly<{ok:true;overlay:VolumetricStructureOverlay}|{ok:false;errors:readonly string[]}> {
  if(!record(value)||!exactKeys(value,["schema_version","overlay_id","grid_id","grid_content_hash","kind","viewer_scene","atom_records","unavailable_reason","security","content_hash"]))return{ok:false,errors:["VOLUME_OVERLAY_SCHEMA_INVALID"]};
  if(value.schema_version!=="phase10j2.volumetric_structure_overlay.v1"||value.grid_id!==bundle.grid.gridId||value.grid_content_hash!==bundle.grid.contentHash)return{ok:false,errors:["VOLUME_OVERLAY_GRID_MISMATCH"]};
  if(typeof value.content_hash!=="string"||!SHA.test(value.content_hash)||value.overlay_id!==`volume-overlay:${value.content_hash}`||!canonicalSecurity(value.security))return{ok:false,errors:["VOLUME_OVERLAY_SECURITY_INVALID"]};
  const unavailable=typeof value.unavailable_reason==="string"?value.unavailable_reason:null;
  if(value.unavailable_reason!==null&&(unavailable===null||unavailable.length>160||FORBIDDEN.some((marker)=>unavailable.toLowerCase().includes(marker))))return{ok:false,errors:["VOLUME_OVERLAY_SECURITY_INVALID"]};
  if(value.kind==="periodic_viewer_scene"&&value.viewer_scene){
    const mapped=mapViewerSceneForRenderer(value.viewer_scene);
    if(!mapped.ok)return{ok:false,errors:["VOLUME_OVERLAY_VIEWER_SCENE_INVALID",...mapped.validation.errors]};
    const scene=mapped.scene;
    return{ok:true,overlay:Object.freeze({kind:"periodic_viewer_scene",atoms:Object.freeze(scene.atoms.map((atom)=>Object.freeze({siteIndex:atom.siteIndex,species:atom.species,position:atom.position,radius:atom.radius,color:atom.color}))),bonds:Object.freeze(scene.bonds.map((bond)=>Object.freeze({start:bond.start,end:bond.end,id:bond.id}))),lattice:Object.freeze(scene.lattice.matrix) as VolumeMatrix3,unavailableReason:unavailable})};
  }
  if(value.kind!=="non_periodic_atom_context"&&value.kind!=="periodic_viewer_scene")return{ok:false,errors:["VOLUME_OVERLAY_SCHEMA_INVALID"]};
  const records=Array.isArray(value.atom_records)?value.atom_records:[];
  if(records.length>4096)return{ok:false,errors:["VOLUME_OVERLAY_CAP_EXCEEDED"]};
  const atoms=records.map((item,index)=>{if(!record(item)||!Number.isSafeInteger(item.atomic_number)||Number(item.atomic_number)<1||Number(item.atomic_number)>118||!vector3(item.cartesian_angstrom))return null;const atomic=Number(item.atomic_number);return Object.freeze({siteIndex:index,species:ELEMENTS[atomic]||`Z${atomic}`,position:Object.freeze(item.cartesian_angstrom.map(Number) as [number,number,number]),radius:radiusFor(atomic),color:PALETTE[index%PALETTE.length]});});
  if(atoms.some((atom)=>!atom))return{ok:false,errors:["VOLUME_OVERLAY_INVALID"]};
  return{ok:true,overlay:Object.freeze({kind:value.kind as VolumetricStructureOverlay["kind"],atoms:Object.freeze(atoms as VolumetricStructureOverlay["atoms"]),bonds:Object.freeze([]),lattice:null,unavailableReason:unavailable})};
}

function record(value:unknown):value is JsonRecord{return typeof value==="object"&&value!==null&&!Array.isArray(value);}
function exactKeys(value:JsonRecord,keys:readonly string[]){const actual=Object.keys(value).sort(),expected=[...keys].sort();return actual.length===expected.length&&actual.every((item,index)=>item===expected[index]);}
function vector3(value:unknown):value is [number,number,number]{return Array.isArray(value)&&value.length===3&&value.every((item)=>typeof item==="number"&&Number.isFinite(item));}
function radiusFor(atomic:number){return Math.min(.85,Math.max(.28,.32+.008*Math.sqrt(atomic)));}
function canonicalSecurity(value:unknown){return record(value)&&exactKeys(value,["contains_css","contains_executable","contains_html","contains_javascript","contains_shader","external_urls_allowed","renderer_included"])&&Object.values(value).every((item)=>item===false);}
