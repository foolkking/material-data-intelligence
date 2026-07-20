import type {
  IsosurfaceExtractionMetrics,
  IsosurfaceLayerRequest,
  IsosurfaceMesh,
  IsosurfaceWorkerRequest,
  ValidatedVolumetricGrid,
  VolumeMatrix3,
  VolumeVector3,
} from "./volumetricViewerTypes";
import { VolumetricViewerError } from "./volumetricViewerTypes";

const CUBE_CORNERS = Object.freeze([
  [0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1],
] as const);
const TETRAHEDRA = Object.freeze([
  [0,5,1,6],[0,1,2,6],[0,2,3,6],[0,3,7,6],[0,7,4,6],[0,4,5,6],
] as const);
const TETRA_EDGES = Object.freeze([[0,1],[1,2],[2,0],[0,3],[1,3],[2,3]] as const);
const TRIANGLE_TABLE: readonly (readonly number[])[] = Object.freeze([
  [],[0,3,2],[0,1,4],[1,4,2,2,4,3],[1,2,5],[0,3,5,0,5,1],[0,2,5,0,5,4],[5,4,3],
  [3,4,5],[4,5,0,5,2,0],[1,5,0,5,3,0],[5,2,1],[3,4,2,2,4,1],[4,1,0],[2,3,0],[],
]);

type MutableLayer = {
  positions: number[];
  gradients: number[];
  fallbackNormals: number[];
  indices: number[];
  edgeVertices: Map<string, number>;
  triangleKeys: Set<string>;
  degenerateRejected: number;
  minimum: [number,number,number];
  maximum: [number,number,number];
};

export async function extractIsosurfaces(request: IsosurfaceWorkerRequest): Promise<Readonly<{
  meshes: readonly IsosurfaceMesh[];
  metrics: IsosurfaceExtractionMetrics;
  warnings: readonly string[];
}>> {
  validateRequest(request);
  const started = now();
  const values = request.dtype === "float32" ? new Float32Array(request.fieldBuffer) : new Float64Array(request.fieldBuffer);
  const [nx,ny,nz] = request.grid.shape;
  if (values.length !== nx*ny*nz) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Worker field count does not match the grid.");
  const cubeShape = request.grid.periodic ? request.grid.shape : Object.freeze([nx-1,ny-1,nz-1] as const);
  const logicalCubeCount = cubeShape[0]*cubeShape[1]*cubeShape[2];
  const inverseSteps = inverse3(request.grid.stepMatrix);
  const layers: { request:IsosurfaceLayerRequest; state:MutableLayer }[] = request.layers.map((layer)=>({request:layer,state:newLayer()}));
  let periodicBoundaryCubes=0;
  let processed=0;
  let normalMs=0;
  let weldingMs=0;

  for(let i=0;i<cubeShape[0];i++)for(let j=0;j<cubeShape[1];j++)for(let k=0;k<cubeShape[2];k++){
    processed+=1;
    if(request.grid.periodic&&(i===nx-1||j===ny-1||k===nz-1))periodicBoundaryCubes+=1;
    if((processed&1023)===0&&elapsed(started)>request.caps.maximumExtractionMs)throw new VolumetricViewerError("VOLUME_VIEWER_MESH_CAP_EXCEEDED","Isosurface extraction exceeded its bounded time budget.");
    const logicalCorners=CUBE_CORNERS.map(([di,dj,dk])=>Object.freeze([i+di,j+dj,k+dk] as const));
    const cornerValues=logicalCorners.map((point)=>sample(values,request.grid,point));
    for(const layer of layers){
      const min=Math.min(...cornerValues),max=Math.max(...cornerValues);
      if(layer.request.isovalue<min||layer.request.isovalue>max||min===max)continue;
      for(const tetra of TETRAHEDRA)polygonizeTetra({tetra,logicalCorners,cornerValues,layer,values,grid:request.grid,inverseSteps,caps:request.caps});
    }
  }

  const meshes:IsosurfaceMesh[]=[];
  let totalVertices=0,totalTriangles=0,totalDegenerate=0;
  for(const layer of layers){
    const normalStarted=now();
    finalizeNormals(layer.state);
    normalMs+=elapsed(normalStarted);
    const vertexCount=layer.state.positions.length/3,triangleCount=layer.state.indices.length/3;
    totalVertices+=vertexCount;totalTriangles+=triangleCount;totalDegenerate+=layer.state.degenerateRejected;
    if(totalVertices>request.caps.maximumTotalVertices||totalTriangles>request.caps.maximumTotalTriangles)throw new VolumetricViewerError("VOLUME_VIEWER_MESH_CAP_EXCEEDED","Combined isosurface mesh exceeds browser caps.");
    const positions=new Float32Array(layer.state.positions),normals=new Float32Array(layer.state.gradients),indices=new Uint32Array(layer.state.indices);
    const meshHash=await meshSha256(request.fieldHash,layer.request,positions,normals,indices,request.grid.periodic);
    const empty=vertexCount===0;
    meshes.push(Object.freeze({layerId:layer.request.layerId,isovalue:layer.request.isovalue,positions,normals,indices,vertexCount,triangleCount,boundingBox:Object.freeze({minimum:Object.freeze(empty?[0,0,0]:layer.state.minimum) as VolumeVector3,maximum:Object.freeze(empty?[0,0,0]:layer.state.maximum) as VolumeVector3}),meshHash,warnings:Object.freeze(empty?["VOLUME_VIEWER_EMPTY_SURFACE"]:[])}));
  }
  const transferBytes=meshes.reduce((sum,mesh)=>sum+mesh.positions.byteLength+mesh.normals.byteLength+mesh.indices.byteLength,0);
  const metrics:IsosurfaceExtractionMetrics=Object.freeze({requestId:request.requestId,voxelCount:values.length,logicalCubeCount,periodicBoundaryCubes,candidateTetrahedra:logicalCubeCount*TETRAHEDRA.length*layers.length,vertices:totalVertices,triangles:totalTriangles,degenerateTrianglesRejected:totalDegenerate,extractionMs:round(elapsed(started)),normalMs:round(normalMs),weldingMs:round(weldingMs),transferBytes,peakWorkingBytesEstimate:request.fieldBuffer.byteLength+transferBytes*2+Math.min(logicalCubeCount*96,64_000_000)});
  return Object.freeze({meshes:Object.freeze(meshes),metrics,warnings:Object.freeze(["ISOSURFACE_ALGORITHM_FIXED_MARCHING_TETRAHEDRA_V1","ISOSURFACE_NORMAL_DIRECTION_INCREASING_FIELD"])});
}

function polygonizeTetra(args:{tetra:readonly number[];logicalCorners:readonly VolumeVector3[];cornerValues:readonly number[];layer:{request:IsosurfaceLayerRequest;state:MutableLayer};values:Float32Array|Float64Array;grid:ValidatedVolumetricGrid;inverseSteps:VolumeMatrix3;caps:IsosurfaceWorkerRequest["caps"]}){
  const {tetra,logicalCorners,cornerValues,layer,values,grid,inverseSteps,caps}=args;
  let mask=0;for(let index=0;index<4;index++)if(cornerValues[tetra[index]]>=layer.request.isovalue)mask|=1<<index;
  const table=TRIANGLE_TABLE[mask];if(!table.length)return;
  const edgeIndices=new Map<number,number>();
  const vertexForEdge=(edgeIndex:number)=>{
    const cached=edgeIndices.get(edgeIndex);if(cached!==undefined)return cached;
    const [localA,localB]=TETRA_EDGES[edgeIndex];const cubeA=tetra[localA],cubeB=tetra[localB];const pointA=logicalCorners[cubeA],pointB=logicalCorners[cubeB];const valueA=cornerValues[cubeA],valueB=cornerValues[cubeB];
    const interpolation=interpolateIsovalue(pointA,valueA,pointB,valueB,layer.request.isovalue);
    const key=edgeIdentity(pointA,pointB,interpolation.t);
    const existing=layer.state.edgeVertices.get(key);if(existing!==undefined){return existing;}
    const cartesian=gridToCartesian(grid,interpolation.point);
    const gradientIndex=lerp3(gradientAt(values,grid,pointA),gradientAt(values,grid,pointB),interpolation.t);
    const gradientCartesian=matrixVector(inverseSteps,gradientIndex);
    const normal=normalize(gradientCartesian);
    const index=layer.state.positions.length/3;layer.state.edgeVertices.set(key,index);layer.state.positions.push(...cartesian);layer.state.gradients.push(...normal);layer.state.fallbackNormals.push(0,0,0);
    for(let axis=0;axis<3;axis++){layer.state.minimum[axis]=Math.min(layer.state.minimum[axis],cartesian[axis]);layer.state.maximum[axis]=Math.max(layer.state.maximum[axis],cartesian[axis]);}
    edgeIndices.set(edgeIndex,index);return index;
  };
  for(let offset=0;offset<table.length;offset+=3){let a=vertexForEdge(table[offset]),b=vertexForEdge(table[offset+1]),c=vertexForEdge(table[offset+2]);if(a===b||b===c||c===a){layer.state.degenerateRejected+=1;continue;}
    const pa=position(layer.state,a),pb=position(layer.state,b),pc=position(layer.state,c);let face=cross(subtract(pb,pa),subtract(pc,pa));const area2=length(face);if(!Number.isFinite(area2)||area2<=1e-10){layer.state.degenerateRejected+=1;continue;}
    const average=add(add(normalAt(layer.state,a),normalAt(layer.state,b)),normalAt(layer.state,c));if(dot(face,average)<0){[b,c]=[c,b];face=scale(face,-1);}
    const duplicate=[a,b,c].sort((left,right)=>left-right).join(":");if(layer.state.triangleKeys.has(duplicate))continue;layer.state.triangleKeys.add(duplicate);layer.state.indices.push(a,b,c);for(const index of[a,b,c])addFallback(layer.state,index,face);
    if(layer.state.indices.length/3>caps.maximumTrianglesPerLayer||layer.state.positions.length/3>caps.maximumVerticesPerLayer)throw new VolumetricViewerError("VOLUME_VIEWER_MESH_CAP_EXCEEDED","Isosurface layer exceeds mesh caps.");
  }
}

function newLayer():MutableLayer{return{positions:[],gradients:[],fallbackNormals:[],indices:[],edgeVertices:new Map(),triangleKeys:new Set(),degenerateRejected:0,minimum:[Infinity,Infinity,Infinity],maximum:[-Infinity,-Infinity,-Infinity]};}
export function canonicalGridOffset(index:VolumeVector3,shape:readonly[number,number,number]){const[i,j,k]=index;return(i*shape[1]+j)*shape[2]+k;}
export function gridToCartesian(grid:Pick<ValidatedVolumetricGrid,"origin"|"stepMatrix">,point:VolumeVector3):VolumeVector3{const translated:VolumeVector3=[point[0]*grid.stepMatrix[0][0]+point[1]*grid.stepMatrix[1][0]+point[2]*grid.stepMatrix[2][0],point[0]*grid.stepMatrix[0][1]+point[1]*grid.stepMatrix[1][1]+point[2]*grid.stepMatrix[2][1],point[0]*grid.stepMatrix[0][2]+point[1]*grid.stepMatrix[1][2]+point[2]*grid.stepMatrix[2][2]];return Object.freeze([grid.origin[0]+translated[0],grid.origin[1]+translated[1],grid.origin[2]+translated[2]]);}
export function interpolateIsovalue(pointA:VolumeVector3,valueA:number,pointB:VolumeVector3,valueB:number,isovalue:number):Readonly<{point:VolumeVector3;t:number}>{if(![valueA,valueB,isovalue,...pointA,...pointB].every(Number.isFinite))throw new VolumetricViewerError("VOLUME_VIEWER_WORKER_FAILED","Interpolation requires finite values.");const denominator=valueB-valueA;if(Math.abs(denominator)<=1e-15)throw new VolumetricViewerError("VOLUME_VIEWER_WORKER_FAILED","Degenerate isosurface edge cannot be interpolated.");let t=(isovalue-valueA)/denominator;if(t< -1e-10||t>1+1e-10)throw new VolumetricViewerError("VOLUME_VIEWER_WORKER_FAILED","Isovalue lies outside the intersected edge.");t=Math.min(1,Math.max(0,t));const point=Object.freeze(pointA.map((value,index)=>clean(value+t*(pointB[index]-value))) as [number,number,number]);return Object.freeze({point,t:clean(t)});}
export function sampleTrilinear(values:Float32Array|Float64Array,grid:ValidatedVolumetricGrid,point:VolumeVector3):number{const base=point.map(Math.floor) as [number,number,number],fraction=point.map((value,index)=>value-base[index]) as [number,number,number];let result=0;for(let di=0;di<=1;di++)for(let dj=0;dj<=1;dj++)for(let dk=0;dk<=1;dk++){const weight=(di?fraction[0]:1-fraction[0])*(dj?fraction[1]:1-fraction[1])*(dk?fraction[2]:1-fraction[2]);result+=weight*sample(values,grid,[base[0]+di,base[1]+dj,base[2]+dk]);}return clean(result);}

function sample(values:Float32Array|Float64Array,grid:ValidatedVolumetricGrid,logical:VolumeVector3){const canonical=logical.map((value,axis)=>grid.periodic?mod(Math.trunc(value),grid.shape[axis]):Math.trunc(value)) as [number,number,number];if(canonical.some((value,axis)=>value<0||value>=grid.shape[axis]))throw new VolumetricViewerError("VOLUME_VIEWER_WORKER_FAILED","Grid sample is outside a non-periodic domain.");const result=values[canonicalGridOffset(canonical,grid.shape)];if(!Number.isFinite(result))throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH","Field contains non-finite values.");return result;}
function gradientAt(values:Float32Array|Float64Array,grid:ValidatedVolumetricGrid,logical:VolumeVector3):VolumeVector3{const canonical=logical.map((value,axis)=>grid.periodic?mod(Math.trunc(value),grid.shape[axis]):Math.trunc(value)) as [number,number,number];const result:[number,number,number]=[0,0,0];for(let axis=0;axis<3;axis++){const n=grid.shape[axis],left=[...canonical] as[number,number,number],right=[...canonical] as[number,number,number];if(grid.periodic){left[axis]=mod(canonical[axis]-1,n);right[axis]=mod(canonical[axis]+1,n);result[axis]=(sample(values,grid,left)-sample(values,grid,right))*-.5;}else if(canonical[axis]===0){right[axis]=1;result[axis]=sample(values,grid,right)-sample(values,grid,canonical);}else if(canonical[axis]===n-1){left[axis]=n-2;result[axis]=sample(values,grid,canonical)-sample(values,grid,left);}else{left[axis]-=1;right[axis]+=1;result[axis]=(sample(values,grid,right)-sample(values,grid,left))*.5;}}return result;}
function edgeIdentity(a:VolumeVector3,b:VolumeVector3,t:number){if(t<=1e-12)return`v:${a.join(",")}`;if(t>=1-1e-12)return`v:${b.join(",")}`;const left=a.join(","),right=b.join(",");return left<right?`e:${left}|${right}`:`e:${right}|${left}`;}
function finalizeNormals(state:MutableLayer){for(let index=0;index<state.gradients.length;index+=3){let normal=normalize([state.gradients[index],state.gradients[index+1],state.gradients[index+2]]);if(length(normal)<=1e-12)normal=normalize([state.fallbackNormals[index],state.fallbackNormals[index+1],state.fallbackNormals[index+2]]);if(length(normal)<=1e-12)normal=[0,0,1];state.gradients[index]=clean(normal[0]);state.gradients[index+1]=clean(normal[1]);state.gradients[index+2]=clean(normal[2]);}}
function addFallback(state:MutableLayer,index:number,value:VolumeVector3){const offset=index*3;state.fallbackNormals[offset]+=value[0];state.fallbackNormals[offset+1]+=value[1];state.fallbackNormals[offset+2]+=value[2];}
function position(state:MutableLayer,index:number):VolumeVector3{const offset=index*3;return[state.positions[offset],state.positions[offset+1],state.positions[offset+2]];}
function normalAt(state:MutableLayer,index:number):VolumeVector3{const offset=index*3;return[state.gradients[offset],state.gradients[offset+1],state.gradients[offset+2]];}
function validateRequest(request:IsosurfaceWorkerRequest){if(request.type!=="extract"||!Number.isSafeInteger(request.requestId)||request.requestId<1||!request.fieldId||!/^[0-9a-f]{64}$/.test(request.fieldHash)||!request.layers.length||request.layers.length>4||request.layers.some((layer)=>!Number.isFinite(layer.isovalue)||!layer.layerId)||request.caps.maximumVerticesPerLayer<3||request.caps.maximumTrianglesPerLayer<1||request.caps.maximumExtractionMs<100)throw new VolumetricViewerError("VOLUME_VIEWER_WORKER_FAILED","Worker request is invalid.");}
function inverse3(matrix:VolumeMatrix3):VolumeMatrix3{const[a,b,c]=matrix,det=a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]);if(!Number.isFinite(det)||Math.abs(det)<=1e-12)throw new VolumetricViewerError("VOLUME_VIEWER_WORKER_FAILED","Grid step matrix is singular.");return[[ (b[1]*c[2]-b[2]*c[1])/det,(a[2]*c[1]-a[1]*c[2])/det,(a[1]*b[2]-a[2]*b[1])/det],[ (b[2]*c[0]-b[0]*c[2])/det,(a[0]*c[2]-a[2]*c[0])/det,(a[2]*b[0]-a[0]*b[2])/det],[ (b[0]*c[1]-b[1]*c[0])/det,(a[1]*c[0]-a[0]*c[1])/det,(a[0]*b[1]-a[1]*b[0])/det]];}
function matrixVector(matrix:VolumeMatrix3,vector:VolumeVector3):VolumeVector3{return[matrix[0][0]*vector[0]+matrix[0][1]*vector[1]+matrix[0][2]*vector[2],matrix[1][0]*vector[0]+matrix[1][1]*vector[1]+matrix[1][2]*vector[2],matrix[2][0]*vector[0]+matrix[2][1]*vector[1]+matrix[2][2]*vector[2]];}
function lerp3(a:VolumeVector3,b:VolumeVector3,t:number):VolumeVector3{return[a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),a[2]+t*(b[2]-a[2])];}
function subtract(a:VolumeVector3,b:VolumeVector3):VolumeVector3{return[a[0]-b[0],a[1]-b[1],a[2]-b[2]];}
function add(a:VolumeVector3,b:VolumeVector3):VolumeVector3{return[a[0]+b[0],a[1]+b[1],a[2]+b[2]];}
function scale(a:VolumeVector3,value:number):VolumeVector3{return[a[0]*value,a[1]*value,a[2]*value];}
function cross(a:VolumeVector3,b:VolumeVector3):VolumeVector3{return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
function dot(a:VolumeVector3,b:VolumeVector3){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
function length(a:VolumeVector3){return Math.hypot(...a);}
function normalize(a:VolumeVector3):VolumeVector3{const magnitude=length(a);return magnitude>1e-15?[a[0]/magnitude,a[1]/magnitude,a[2]/magnitude]:[0,0,0];}
function mod(value:number,size:number){return((value%size)+size)%size;}
function clean(value:number){return Object.is(value,-0)||Math.abs(value)<1e-15?0:value;}
async function meshSha256(fieldHash:string,layer:IsosurfaceLayerRequest,positions:Float32Array,normals:Float32Array,indices:Uint32Array,periodic:boolean){const metadata=new TextEncoder().encode(JSON.stringify({algorithm:"fixed_marching_tetrahedra_v1",fieldHash,layerId:layer.layerId,isovalue:layer.isovalue,periodic,normal:"increasing_field"}));const bytes=new Uint8Array(metadata.byteLength+positions.byteLength+normals.byteLength+indices.byteLength);bytes.set(metadata);bytes.set(new Uint8Array(positions.buffer,positions.byteOffset,positions.byteLength),metadata.byteLength);bytes.set(new Uint8Array(normals.buffer,normals.byteOffset,normals.byteLength),metadata.byteLength+positions.byteLength);bytes.set(new Uint8Array(indices.buffer,indices.byteOffset,indices.byteLength),metadata.byteLength+positions.byteLength+normals.byteLength);const digest=await crypto.subtle.digest("SHA-256",bytes);return[...new Uint8Array(digest)].map((item)=>item.toString(16).padStart(2,"0")).join("");}
function now(){return typeof performance==="undefined"?Date.now():performance.now();}
function elapsed(start:number){return Math.max(0,now()-start);}
function round(value:number){return Math.round(value*1000)/1000;}
