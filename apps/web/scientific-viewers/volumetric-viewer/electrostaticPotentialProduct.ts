import type { ValidatedVolumetricBundle, ValidatedVolumetricField, ValidatedVolumetricGrid, ValidatedVolumetricPayload, VolumeMatrix3, VolumeVector3 } from "./volumetricViewerTypes";

export type PotentialGaugeMode = "source_native" | "cell_average_zero" | "selected_point_zero";
export type PotentialAxis = "lattice_axis_0" | "lattice_axis_1" | "lattice_axis_2";
export type PotentialValues = Float32Array | Float64Array;
export type PotentialRawProfiles = readonly [readonly number[],readonly number[],readonly number[]];
export type PotentialSample = Readonly<{ cartesian:VolumeVector3; gridCoordinate:VolumeVector3; fractional:VolumeVector3|null; imageOffset:readonly[number,number,number]; sourceValue:number; displayedValue:number; unit:string; interpolation:"trilinear_periodic"|"trilinear_affine" }>;
export type PotentialProfilePoint = Readonly<{ index:number; fractional:number; pathLengthAngstrom:number; sourceValue:number; displayedValue:number; planeSampleCount:number }>;
export type PotentialProfile = Readonly<{ profileId:string; profileHash:string; axis:PotentialAxis; fieldHash:string; gauge:PotentialGaugeMode; formulaId:"POTENTIAL_PLANAR_AVERAGE_V1"; unit:string; points:readonly PotentialProfilePoint[] }>;
export type PotentialSurfaceLayer = Readonly<{ layerId:string; sourceIsovalue:number; displayedIsovalue:number; gauge:PotentialGaugeMode; fieldHash:string; unit:string }>;
export type PotentialGaugeView = Readonly<{ mode:PotentialGaugeMode; formulaId:"POTENTIAL_SOURCE_NATIVE_V1"|"POTENTIAL_CELL_AVERAGE_ZERO_V1"|"POTENTIAL_SELECTED_POINT_ZERO_V1"; shift:number; unit:string; sourceFieldHash:string; sourceMinimum:number; sourceMaximum:number; sourceMean:number; displayedMinimum:number; displayedMaximum:number; displayedMean:number; shiftedMeanResidual:number; standardDeviation:number; sourceRms:number; displayedRms:number; sourceVolumeIntegral:number; displayedVolumeIntegral:number; cellVolume:number }>;
export type PotentialProductCompatibility = Readonly<{ compatible:boolean; reasons:readonly string[] }>;
export type ElectrostaticPotentialProduct = Readonly<{ status:"ready"|"unavailable"; title:string; fieldId:string|null; quantity:"local_potential"|"electrostatic_potential"|null; unit:string|null; sourceReference:ValidatedVolumetricField["potentialReference"]; compatibility:PotentialProductCompatibility; warnings:readonly string[] }>;

export const POTENTIAL_PROFILE_CAPS = Object.freeze({ maximumProfiles:3, maximumPointsPerProfile:4096, maximumTotalPoints:12288 });
export const POTENTIAL_MAX_ABS_SHIFT = 1_000_000_000;

function potentialCompatibility(item:ValidatedVolumetricBundle["fields"][number],bundle:ValidatedVolumetricBundle):PotentialProductCompatibility{
  const reasons:string[]=[]; const field=item.field;
  if(!item.supported)reasons.push("VOLUME_POTENTIAL_FIELD_UNSUPPORTED");
  if(!["local_potential","electrostatic_potential"].includes(field.quantity))reasons.push("VOLUME_POTENTIAL_QUANTITY_UNSUPPORTED");
  if(field.valueKind!=="real"||field.fieldRank!=="scalar"||field.storedComponentCount!==1)reasons.push("VOLUME_POTENTIAL_SCALAR_REQUIRED");
  if(!field.potentialReference)reasons.push("VOLUME_POTENTIAL_REFERENCE_REQUIRED");
  if(field.quantity==="electrostatic_potential"&&field.potentialReference?.kind==="unknown")reasons.push("VOLUME_ELECTROSTATIC_DEFINITION_REQUIRED");
  if(!["volt","electronvolt","hartree","hartree/elementary_charge"].includes(field.unit))reasons.push("VOLUME_POTENTIAL_UNIT_UNSUPPORTED");
  if(bundle.grid.sampleLocation!=="node")reasons.push("VOLUME_POTENTIAL_NODE_GRID_REQUIRED");
  if(Math.max(...bundle.grid.shape)>POTENTIAL_PROFILE_CAPS.maximumPointsPerProfile||bundle.grid.shape.reduce((total,value)=>total+value,0)>POTENTIAL_PROFILE_CAPS.maximumTotalPoints)reasons.push("VOLUME_POTENTIAL_PROFILE_CAP_EXCEEDED");
  return Object.freeze({compatible:reasons.length===0,reasons:Object.freeze(reasons)});
}

export function buildElectrostaticPotentialProduct(bundle:ValidatedVolumetricBundle):ElectrostaticPotentialProduct{
  const candidate=bundle.fields.find((item)=>["local_potential","electrostatic_potential"].includes(item.field.quantity));
  const compatibility=candidate?potentialCompatibility(candidate,bundle):Object.freeze({compatible:false,reasons:Object.freeze(["VOLUME_POTENTIAL_PRODUCT_UNAVAILABLE"])});
  if(!candidate||!compatibility.compatible)return freeze({status:"unavailable",title:"Potential product unavailable",fieldId:null,quantity:null,unit:null,sourceReference:null,compatibility,warnings:Object.freeze(["VOLUME_POTENTIAL_PRODUCT_UNAVAILABLE",...compatibility.reasons])});
  const compatible=candidate;
  const field=compatible.field; const quantity=field.quantity as "local_potential"|"electrostatic_potential";
  const warnings=["Potential zero is source-defined unless the source reference says otherwise.","Absolute potential is not available from this product.","Vacuum level has not been detected.","Work function has not been calculated.","Cross-calculation comparison requires explicit alignment."];
  if(quantity==="local_potential")warnings.push("LOCPOT component semantics depend on the source and parser definition.");
  if(field.potentialReference?.kind==="unknown")warnings.push("The source reference is unknown; reference-dependent claims are disabled.");
  return freeze({status:"ready",title:quantity==="local_potential"?"Local Potential":"Electrostatic Potential",fieldId:field.fieldId,quantity,unit:field.unit,sourceReference:field.potentialReference,compatibility,warnings});
}

export function potentialShift(field:ValidatedVolumetricField,gauge:PotentialGaugeMode,selectedSourceValue:number|null):number{
  if(gauge==="source_native")return 0;
  if(gauge==="cell_average_zero")return boundedShift(-field.mean);
  if(selectedSourceValue===null||!Number.isFinite(selectedSourceValue))throw new Error("POTENTIAL_REFERENCE_POINT_REQUIRED");
  return boundedShift(-selectedSourceValue);
}

export function potentialGaugeView(field:ValidatedVolumetricField,grid:ValidatedVolumetricGrid,gauge:PotentialGaugeMode,selectedSourceValue:number|null):PotentialGaugeView{
  const shift=potentialShift(field,gauge,selectedSourceValue);const voxelVolume=Math.abs(determinant3(grid.stepMatrix));const cellVolume=voxelVolume*grid.shape.reduce((total,value)=>total*value,1);if(!Number.isFinite(cellVolume)||cellVolume<=0)throw new Error("POTENTIAL_GRID_SINGULAR");const displayedMean=field.mean+shift;const displayedRms=Math.sqrt(Math.max(0,field.rms*field.rms+2*shift*field.mean+shift*shift));const formulaId=gauge==="source_native"?"POTENTIAL_SOURCE_NATIVE_V1":gauge==="cell_average_zero"?"POTENTIAL_CELL_AVERAGE_ZERO_V1":"POTENTIAL_SELECTED_POINT_ZERO_V1";return Object.freeze({mode:gauge,formulaId,shift,unit:field.unit,sourceFieldHash:field.contentHash,sourceMinimum:field.minimum,sourceMaximum:field.maximum,sourceMean:field.mean,displayedMinimum:field.minimum+shift,displayedMaximum:field.maximum+shift,displayedMean,shiftedMeanResidual:gauge==="cell_average_zero"?displayedMean:0,standardDeviation:field.standardDeviation,sourceRms:field.rms,displayedRms,sourceVolumeIntegral:field.integral,displayedVolumeIntegral:field.integral+shift*cellVolume,cellVolume});
}

export function shiftedPotentialBuffer(buffer:ArrayBuffer,dtype:"float32"|"float64",shift:number):ArrayBuffer{
  if(!Number.isFinite(shift)||Math.abs(shift)>1e9)throw new Error("POTENTIAL_SHIFT_INVALID");
  const source=dtype==="float32"?new Float32Array(buffer):new Float64Array(buffer); const output=new ArrayBuffer(buffer.byteLength); const target=dtype==="float32"?new Float32Array(output):new Float64Array(output);
  for(let index=0;index<source.length;index++){const value=source[index]+shift;if(!Number.isFinite(value))throw new Error("POTENTIAL_SHIFT_INVALID");target[index]=value;}
  return output;
}

export function decodePotentialValues(buffer:ArrayBuffer,dtype:"float32"|"float64"):PotentialValues{return dtype==="float32"?new Float32Array(buffer):new Float64Array(buffer);}

export function samplePotential(values:ArrayLike<number>,grid:ValidatedVolumetricGrid,field:ValidatedVolumetricField,cartesian:VolumeVector3,shift=0):PotentialSample{
  if(values.length!==grid.shape[0]*grid.shape[1]*grid.shape[2]||!cartesian.every(Number.isFinite)||!Number.isFinite(shift))throw new Error("POTENTIAL_SAMPLE_INVALID");
  const delta=cartesian.map((value,index)=>value-grid.origin[index]) as [number,number,number]; const inverse=invert3(grid.stepMatrix); const raw=multiplyRow(delta,inverse);
  const base=raw.map(Math.floor) as [number,number,number]; const fraction=raw.map((value,index)=>value-base[index]) as [number,number,number]; let sourceValue=0;
  for(let di=0;di<2;di++)for(let dj=0;dj<2;dj++)for(let dk=0;dk<2;dk++){const indices=[base[0]+di,base[1]+dj,base[2]+dk] as [number,number,number];const mapped=indices.map((value,axis)=>grid.periodic?mod(value,grid.shape[axis]):Math.max(0,Math.min(grid.shape[axis]-1,value))) as [number,number,number];const weight=(di?fraction[0]:1-fraction[0])*(dj?fraction[1]:1-fraction[1])*(dk?fraction[2]:1-fraction[2]);sourceValue+=values[(mapped[0]*grid.shape[1]+mapped[1])*grid.shape[2]+mapped[2]]*weight;}
  const normalized=raw.map((value,index)=>value/grid.shape[index]) as [number,number,number]; const image=normalized.map(Math.floor) as [number,number,number]; const fractional=grid.periodic?normalized.map((value)=>value-Math.floor(value)) as [number,number,number]:null;
  return Object.freeze({cartesian:Object.freeze([...cartesian]) as VolumeVector3,gridCoordinate:Object.freeze(raw) as VolumeVector3,fractional:fractional?Object.freeze(fractional):null,imageOffset:Object.freeze(image),sourceValue,displayedValue:sourceValue+shift,unit:field.unit,interpolation:grid.periodic?"trilinear_periodic":"trilinear_affine"});
}

export function planarProfiles(values:ArrayLike<number>,grid:ValidatedVolumetricGrid,field:ValidatedVolumetricField,gauge:PotentialGaugeMode,shift:number):readonly PotentialProfile[]{
  const [nx,ny,nz]=grid.shape; const voxelCount=nx*ny*nz;
  if(values.length!==voxelCount||!Number.isFinite(shift)||grid.sampleLocation!=="node")throw new Error("POTENTIAL_PROFILE_INVALID");
  return profilesFromRaw(computeRawPlanarProfiles(values,grid.shape),grid,field,gauge,shift);
}

export function computeRawPlanarProfiles(values:ArrayLike<number>,shape:readonly[number,number,number]):PotentialRawProfiles{
  const [nx,ny,nz]=shape; const voxelCount=nx*ny*nz;
  if(values.length!==voxelCount)throw new Error("POTENTIAL_PROFILE_INVALID");
  if(Math.max(nx,ny,nz)>POTENTIAL_PROFILE_CAPS.maximumPointsPerProfile||nx+ny+nz>POTENTIAL_PROFILE_CAPS.maximumTotalPoints)throw new Error("POTENTIAL_PROFILE_CAP_EXCEEDED");
  const sums=[new Float64Array(nx),new Float64Array(ny),new Float64Array(nz)];
  for(let i=0;i<nx;i++)for(let j=0;j<ny;j++)for(let k=0;k<nz;k++){const value=values[(i*ny+j)*nz+k];if(!Number.isFinite(value))throw new Error("POTENTIAL_PROFILE_INVALID");sums[0][i]+=value;sums[1][j]+=value;sums[2][k]+=value;}
  return Object.freeze(([0,1,2] as const).map((axis)=>Object.freeze(Array.from(sums[axis],(value)=>value/(voxelCount/shape[axis]))))) as PotentialRawProfiles;
}

export function profilesFromRaw(raw:PotentialRawProfiles,grid:ValidatedVolumetricGrid,field:ValidatedVolumetricField,gauge:PotentialGaugeMode,shift:number):readonly PotentialProfile[]{
  if(raw.length!==3||!Number.isFinite(shift)||grid.sampleLocation!=="node")throw new Error("POTENTIAL_PROFILE_INVALID");
  return Object.freeze(([0,1,2] as const).map((axis)=>{const count=grid.shape[axis];if(raw[axis].length!==count)throw new Error("POTENTIAL_PROFILE_INVALID");const samples=grid.shape.reduce((total,value)=>total*value,1)/count;const vector:VolumeVector3=grid.structureBinding?.latticeMatrix[axis]??[grid.stepMatrix[axis][0]*count,grid.stepMatrix[axis][1]*count,grid.stepMatrix[axis][2]*count];const length=Math.hypot(...vector);const points=Object.freeze(Array.from(raw[axis],(sourceValue,index)=>Object.freeze({index,fractional:index/count,pathLengthAngstrom:index/count*length,sourceValue,displayedValue:sourceValue+shift,planeSampleCount:samples})));const profileHash=stableHash([field.contentHash,axis,gauge,shift,...points.flatMap((point)=>[point.index,point.sourceValue,point.displayedValue])]);return Object.freeze({profileId:`${field.contentHash}:${axis}:${gauge}`,profileHash,axis:`lattice_axis_${axis}` as PotentialAxis,fieldHash:field.contentHash,gauge,formulaId:"POTENTIAL_PLANAR_AVERAGE_V1" as const,unit:field.unit,points}); }));
}

export function potentialDifference(a:PotentialSample,b:PotentialSample){if(a.unit!==b.unit)throw new Error("POTENTIAL_UNIT_MISMATCH");const source=b.sourceValue-a.sourceValue;const displayed=b.displayedValue-a.displayedValue;if(Math.abs(source-displayed)>1e-10)throw new Error("POTENTIAL_GAUGE_INVARIANT_FAILED");return Object.freeze({value:source,unit:a.unit,gaugeInvariant:true,sourceField:"same validated field required by caller"});}

export function potentialSurfaceLayer(layerId:string,sourceIsovalue:number,field:ValidatedVolumetricField,gauge:PotentialGaugeMode,shift:number):PotentialSurfaceLayer{
  if(!Number.isFinite(sourceIsovalue)||!Number.isFinite(shift))throw new Error("POTENTIAL_ISOVALUE_INVALID");
  return Object.freeze({layerId,sourceIsovalue,displayedIsovalue:sourceIsovalue+shift,gauge,fieldHash:field.contentHash,unit:field.unit});
}

function invert3(matrix:VolumeMatrix3):VolumeMatrix3{const[a,b,c]=matrix;const det=a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]);if(!Number.isFinite(det)||Math.abs(det)<1e-14)throw new Error("POTENTIAL_GRID_SINGULAR");return Object.freeze([[ (b[1]*c[2]-b[2]*c[1])/det,(a[2]*c[1]-a[1]*c[2])/det,(a[1]*b[2]-a[2]*b[1])/det],[(b[2]*c[0]-b[0]*c[2])/det,(a[0]*c[2]-a[2]*c[0])/det,(a[2]*b[0]-a[0]*b[2])/det],[(b[0]*c[1]-b[1]*c[0])/det,(a[1]*c[0]-a[0]*c[1])/det,(a[0]*b[1]-a[1]*b[0])/det]] as [VolumeVector3,VolumeVector3,VolumeVector3]);}
function determinant3(matrix:VolumeMatrix3):number{const[a,b,c]=matrix;return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]);}
function multiplyRow(vector:VolumeVector3,matrix:VolumeMatrix3):[number,number,number]{return [vector[0]*matrix[0][0]+vector[1]*matrix[1][0]+vector[2]*matrix[2][0],vector[0]*matrix[0][1]+vector[1]*matrix[1][1]+vector[2]*matrix[2][1],vector[0]*matrix[0][2]+vector[1]*matrix[1][2]+vector[2]*matrix[2][2]];}
function mod(value:number,size:number){return((value%size)+size)%size;}
function freeze<T extends ElectrostaticPotentialProduct>(value:T):T{return Object.freeze({...value,warnings:Object.freeze([...value.warnings])}) as T;}
function stableHash(values:readonly(number|string)[]):string{let hash=2166136261;for(const value of values){for(const char of String(value)){hash^=char.charCodeAt(0);hash=Math.imul(hash,16777619)>>>0;}}return hash.toString(16).padStart(8,"0");}
function boundedShift(value:number):number{if(!Number.isFinite(value)||Math.abs(value)>POTENTIAL_MAX_ABS_SHIFT)throw new Error("POTENTIAL_SHIFT_INVALID");return value;}
