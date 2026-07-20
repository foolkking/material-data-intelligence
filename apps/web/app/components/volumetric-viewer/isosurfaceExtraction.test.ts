import { describe, expect, it } from "vitest";

import { canonicalGridOffset, extractIsosurfaces, gridToCartesian, interpolateIsovalue, sampleTrilinear } from "./isosurfaceExtraction";
import type { IsosurfaceWorkerRequest, ValidatedVolumetricGrid, VolumeMatrix3 } from "./volumetricViewerTypes";

describe("Phase 10J-2 isosurface extraction", () => {
  it("uses canonical ijk ordering and full affine coordinate mapping", () => {
    expect(canonicalGridOffset([1,2,3],[2,3,4])).toBe(23);
    const grid=makeGrid([2,3,4],[[2,0,0],[.5,3,0],[.25,.75,4]],[10,-2,5],false);
    expect(gridToCartesian(grid,[1,.5,.25])).toEqual([12.3125,-.3125,6]);
    expect(interpolateIsovalue([0,0,0],-2,[2,4,6],2,0)).toEqual({point:[1,2,3],t:.5});
  });

  it("extracts an affine plane with normals facing increasing field", async () => {
    const grid=makeGrid([3,3,3],[[1,0,0],[.25,1,0],[0,.2,1]],[2,3,4],false);
    const values=valuesFor(grid,([i])=>i);
    const result=await extractIsosurfaces(request(grid,values,[{layerId:"positive",isovalue:1,sign:"positive"}]));
    const mesh=result.meshes[0];
    expect(mesh.triangleCount).toBeGreaterThan(0);
    for(let index=0;index<mesh.positions.length;index+=3){const x=mesh.positions[index]-2,y=mesh.positions[index+1]-3,z=mesh.positions[index+2]-4;expect(x-.25*y+.05*z).toBeCloseTo(1,5);}
    for(let index=0;index<mesh.normals.length;index+=3)expect(mesh.normals[index]).toBeGreaterThan(.8);
    expect(mesh.indices.every((index)=>index<mesh.vertexCount)).toBe(true);
    expect(result.metrics.degenerateTrianglesRejected).toBeGreaterThanOrEqual(0);
  });

  it("includes every periodic boundary cube and produces deterministic seam geometry", async () => {
    const grid=makeGrid([4,4,4],[[1,0,0],[.2,1,0],[.1,.15,1]],[0,0,0],true);
    const values=valuesFor(grid,([i,j,k])=>Math.sin(2*Math.PI*i/4)+.5*Math.sin(2*Math.PI*j/4)+.25*Math.sin(2*Math.PI*k/4));
    const first=await extractIsosurfaces(request(grid,values,[{layerId:"zero",isovalue:0,sign:"neutral"}]));
    const second=await extractIsosurfaces(request(grid,values,[{layerId:"zero",isovalue:0,sign:"neutral"}]));
    expect(first.metrics.logicalCubeCount).toBe(64);
    expect(first.metrics.periodicBoundaryCubes).toBe(37);
    expect(first.meshes[0].triangleCount).toBeGreaterThan(0);
    expect(first.meshes[0].meshHash).toBe(second.meshes[0].meshHash);
    expect([...first.meshes[0].positions]).toEqual([...second.meshes[0].positions]);
  });

  it("supports positive and negative layers without losing sign", async () => {
    const grid=makeGrid([4,4,4],[[1,0,0],[0,1,0],[0,0,1]],[0,0,0],false);
    const values=valuesFor(grid,([i,j,k])=>i+j+k-4.5);
    const result=await extractIsosurfaces(request(grid,values,[{layerId:"positive",isovalue:1,sign:"positive"},{layerId:"negative",isovalue:-1,sign:"negative"}]));
    expect(result.meshes.map((mesh)=>mesh.isovalue)).toEqual([1,-1]);
    expect(result.meshes.every((mesh)=>mesh.triangleCount>0)).toBe(true);
  });

  it("performs bounded trilinear sampling with periodic wrap", () => {
    const grid=makeGrid([2,2,2],[[1,0,0],[0,1,0],[0,0,1]],[0,0,0],true);
    const values=valuesFor(grid,([i,j,k])=>i+2*j+4*k);
    expect(sampleTrilinear(values,grid,[.5,.5,.5])).toBeCloseTo(3.5);
    expect(sampleTrilinear(values,grid,[1.5,.5,.5])).toBeCloseTo(3.5);
  });

  it("rejects a complete layer rather than truncating at mesh caps", async () => {
    const grid=makeGrid([4,4,4],[[1,0,0],[0,1,0],[0,0,1]],[0,0,0],false);
    const values=valuesFor(grid,([i,j,k])=>i+j+k);
    const value=request(grid,values,[{layerId:"limited",isovalue:3,sign:"positive"}]);
    await expect(extractIsosurfaces({...value,caps:{...value.caps,maximumTrianglesPerLayer:1}})).rejects.toMatchObject({code:"VOLUME_VIEWER_MESH_CAP_EXCEEDED"});
  });
});

function makeGrid(shape:readonly[number,number,number],stepMatrix:VolumeMatrix3,origin:readonly[number,number,number],periodic:boolean):ValidatedVolumetricGrid{const boundaryConditions:ValidatedVolumetricGrid["boundaryConditions"]=Object.freeze([periodic?"periodic":"non_periodic",periodic?"periodic":"non_periodic",periodic?"periodic":"non_periodic"]);return Object.freeze({schemaVersion:"phase10j.volumetric_grid.v1",gridId:"grid:"+"a".repeat(64),contentHash:"a".repeat(64),shape:Object.freeze([...shape]) as readonly[number,number,number],origin:Object.freeze([...origin]) as readonly[number,number,number],stepMatrix:Object.freeze(stepMatrix.map((row)=>Object.freeze([...row]))) as VolumeMatrix3,sampleLocation:"node",boundaryConditions,endpointPolicy:periodic?"excluded":"not_applicable",periodic,structureBinding:periodic?Object.freeze({structureSha256:"b".repeat(64),latticeSha256:"c".repeat(64),latticeMatrix:Object.freeze(stepMatrix.map((row,index)=>Object.freeze(row.map((item)=>item*shape[index])))) as VolumeMatrix3}):null});}
function valuesFor(grid:ValidatedVolumetricGrid,evaluate:(index:readonly[number,number,number])=>number){const values=new Float64Array(grid.shape[0]*grid.shape[1]*grid.shape[2]);for(let i=0;i<grid.shape[0];i++)for(let j=0;j<grid.shape[1];j++)for(let k=0;k<grid.shape[2];k++)values[canonicalGridOffset([i,j,k],grid.shape)]=evaluate([i,j,k]);return values;}
function request(grid:ValidatedVolumetricGrid,values:Float64Array,layers:IsosurfaceWorkerRequest["layers"]):IsosurfaceWorkerRequest{const fieldBuffer=new ArrayBuffer(values.byteLength);new Float64Array(fieldBuffer).set(values);return Object.freeze({type:"extract",requestId:1,fieldId:"field:"+"d".repeat(64),fieldHash:"d".repeat(64),grid,dtype:"float64",fieldBuffer,layers,caps:{maximumVerticesPerLayer:100_000,maximumTrianglesPerLayer:100_000,maximumTotalVertices:200_000,maximumTotalTriangles:200_000,maximumExtractionMs:10_000}});}
