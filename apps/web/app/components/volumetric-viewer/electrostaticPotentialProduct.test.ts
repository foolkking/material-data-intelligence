import { describe, expect, it } from "vitest";

import { buildElectrostaticPotentialProduct, computeRawPlanarProfiles, decodePotentialValues, planarProfiles, potentialDifference, potentialGaugeView, potentialShift, potentialSurfaceLayer, samplePotential, shiftedPotentialBuffer } from "./electrostaticPotentialProduct";
import type { ValidatedVolumetricBundle, ValidatedVolumetricField, ValidatedVolumetricGrid } from "./volumetricViewerTypes";

const grid = Object.freeze({
  schemaVersion:"phase10j.volumetric_grid.v1",gridId:"grid",contentHash:"a".repeat(64),shape:[2,2,2],origin:[1,2,3],stepMatrix:[[1,0,0],[0.25,1,0],[0.1,0.2,1]],sampleLocation:"node",boundaryConditions:["periodic","periodic","periodic"],endpointPolicy:"excluded",periodic:true,
  structureBinding:{structureSha256:"b".repeat(64),latticeSha256:"c".repeat(64),latticeMatrix:[[2,0,0],[0.5,2,0],[0.2,0.4,2]]},
} as unknown as ValidatedVolumetricGrid);

const field = Object.freeze({fieldId:"field",fieldName:"local_potential",quantity:"local_potential",valueKind:"real",fieldRank:"scalar",storedComponentCount:1,unit:"electronvolt",sourceUnit:"electronvolt",mean:3.5,minimum:0,maximum:7,standardDeviation:2.291287847,rms:4.183300133,integral:28,contentHash:"d".repeat(64),potentialReference:{kind:"source_defined",referenceValue:0,referenceUnit:"electronvolt",shiftApplied:false,shiftAmount:0,sourceMetadata:"No alignment applied."}} as unknown as ValidatedVolumetricField);

describe("Phase 10J-4 electrostatic potential product",()=>{
  it("accepts only explicit local/electrostatic potential quantities",()=>{
    const bundle={sourceFormat:"vasp_volumetric",grid,fields:[{supported:true,reasons:[],field,payload:{}}]} as unknown as ValidatedVolumetricBundle;
    expect(buildElectrostaticPotentialProduct(bundle)).toMatchObject({status:"ready",title:"Local Potential",quantity:"local_potential",unit:"electronvolt"});
    const generic={...bundle,fields:[{...bundle.fields[0],field:{...field,quantity:"generic_scalar",potentialReference:null}}]} as unknown as ValidatedVolumetricBundle;
    expect(buildElectrostaticPotentialProduct(generic).status).toBe("unavailable");
    const explicitElectrostatic={...bundle,fields:[{...bundle.fields[0],field:{...field,quantity:"electrostatic_potential"}}]} as unknown as ValidatedVolumetricBundle;
    expect(buildElectrostaticPotentialProduct(explicitElectrostatic)).toMatchObject({status:"ready",quantity:"electrostatic_potential"});
    const unknownElectrostatic={...bundle,fields:[{...bundle.fields[0],field:{...field,quantity:"electrostatic_potential",potentialReference:{...field.potentialReference!,kind:"unknown"}}}]} as unknown as ValidatedVolumetricBundle;
    expect(buildElectrostaticPotentialProduct(unknownElectrostatic)).toMatchObject({status:"unavailable",compatibility:{reasons:["VOLUME_ELECTROSTATIC_DEFINITION_REQUIRED"]}});
  });

  it("applies allowlisted constant gauges without mutating source bytes",()=>{
    expect(potentialShift(field,"source_native",null)).toBe(0);
    expect(potentialShift(field,"cell_average_zero",null)).toBe(-3.5);
    expect(potentialShift(field,"selected_point_zero",2.25)).toBe(-2.25);
    const source=new Float64Array([1,2,3]).buffer;const shifted=shiftedPotentialBuffer(source,"float64",-2);
    expect(Array.from(decodePotentialValues(source,"float64"))).toEqual([1,2,3]);
    expect(Array.from(decodePotentialValues(shifted,"float64"))).toEqual([-1,0,1]);
  });

  it("samples a shifted-origin triclinic periodic grid with trilinear interpolation",()=>{
    const values=[0,1,2,3,4,5,6,7];
    expect(samplePotential(values,grid,field,[1,2,3],0).sourceValue).toBeCloseTo(0);
    const midpoint=samplePotential(values,grid,field,[1.675,2.6,3.5],-3.5);
    expect(midpoint.sourceValue).toBeCloseTo(3.5);
    expect(midpoint.displayedValue).toBeCloseTo(0);
    midpoint.fractional?.forEach((value)=>expect(value).toBeCloseTo(0.25,12));
  });

  it("computes raw lattice-axis planar averages and gauge-invariant point differences",()=>{
    const profiles=planarProfiles([0,1,2,3,4,5,6,7],grid,field,"cell_average_zero",-3.5);
    expect(profiles.map((profile)=>profile.points.map((point)=>point.sourceValue))).toEqual([[1.5,5.5],[2.5,4.5],[3,4]]);
    expect(profiles[0].points[0]).toMatchObject({fractional:0,pathLengthAngstrom:0,displayedValue:-2,planeSampleCount:4});
    const a=samplePotential([0,1,2,3,4,5,6,7],grid,field,[1,2,3],-3.5);const b=samplePotential([0,1,2,3,4,5,6,7],grid,field,[2,2,3],-3.5);
    expect(potentialDifference(a,b)).toMatchObject({value:4,unit:"electronvolt",gaugeInvariant:true});
    expect(planarProfiles([0,1,2,3,4,5,6,7],grid,field,"cell_average_zero",-3.5).map((profile)=>profile.profileHash)).toEqual(profiles.map((profile)=>profile.profileHash));
  });

  it("preserves source contour identity while shifting only the displayed isovalue",()=>{
    expect(potentialSurfaceLayer("surface-1",2.5,field,"source_native",0)).toMatchObject({sourceIsovalue:2.5,displayedIsovalue:2.5});
    expect(potentialSurfaceLayer("surface-1",2.5,field,"cell_average_zero",-3.5)).toMatchObject({sourceIsovalue:2.5,displayedIsovalue:-1});
  });

  it("derives gauge-aware statistics without changing source statistics",()=>{
    const view=potentialGaugeView(field,grid,"cell_average_zero",null);
    expect(view).toMatchObject({formulaId:"POTENTIAL_CELL_AVERAGE_ZERO_V1",shift:-3.5,sourceMean:3.5,displayedMean:0,sourceVolumeIntegral:28,displayedVolumeIntegral:0,cellVolume:8});
    expect(view.displayedRms).toBeCloseTo(field.standardDeviation,8);
    expect(()=>potentialShift({...field,mean:1e10} as ValidatedVolumetricField,"cell_average_zero",null)).toThrow("POTENTIAL_SHIFT_INVALID");
  });

  it("rejects incompatible scalar metadata and over-cap profile axes",()=>{
    const incompatible={sourceFormat:"cube",grid,fields:[{supported:true,reasons:[],field:{...field,valueKind:"complex",storedComponentCount:2},payload:{}}]} as unknown as ValidatedVolumetricBundle;
    expect(buildElectrostaticPotentialProduct(incompatible)).toMatchObject({status:"unavailable",compatibility:{compatible:false,reasons:["VOLUME_POTENTIAL_SCALAR_REQUIRED"]}});
    const longGrid={...grid,shape:[4097,1,1]} as unknown as ValidatedVolumetricGrid;
    expect(()=>planarProfiles(new Float32Array(4097),longGrid,field,"source_native",0)).toThrow("POTENTIAL_PROFILE_CAP_EXCEEDED");
  });

  it("matches constant-field gauge and profile references",()=>{
    const values=new Float64Array(8).fill(4);const constantField={...field,mean:4,minimum:4,maximum:4,rms:4,standardDeviation:0,integral:32} as ValidatedVolumetricField;
    const profiles=planarProfiles(values,grid,constantField,"cell_average_zero",-4);
    expect(profiles.every((profile)=>profile.points.every((point)=>point.sourceValue===4&&point.displayedValue===0))).toBe(true);
    const a=samplePotential(values,grid,constantField,[1,2,3],-4),b=samplePotential(values,grid,constantField,[2,3,4],-4);
    expect(potentialDifference(a,b).value).toBe(0);
  });

  it("matches an independent affine formula on a shifted triclinic grid",()=>{
    const affineGrid={...grid,shape:[3,3,3],periodic:false,boundaryConditions:["non_periodic","non_periodic","non_periodic"],endpointPolicy:"not_applicable",structureBinding:null} as unknown as ValidatedVolumetricGrid;
    const values=Array.from({length:27},(_,index)=>{const i=Math.floor(index/9),j=Math.floor(index/3)%3,k=index%3;return i+2*j+3*k+4;});
    const coordinate:[number,number,number]=[1+0.5+1.25*0.25+1.5*0.1,2+1.25+1.5*0.2,3+1.5];
    const sample=samplePotential(values,affineGrid,field,coordinate,0);
    expect(sample.gridCoordinate).toEqual(expect.arrayContaining([expect.closeTo(.5,10),expect.closeTo(1.25,10),expect.closeTo(1.5,10)]));
    expect(sample.sourceValue).toBeCloseTo(11.5,10);
    expect(sample.interpolation).toBe("trilinear_affine");
  });

  it("matches periodic trigonometric profiles and wraps endpoint-excluded samples",()=>{
    const shape:[number,number,number]=[8,4,4];const periodicGrid={...grid,shape,stepMatrix:[[.25,0,0],[0,.5,0],[0,0,.5]],structureBinding:{...grid.structureBinding!,latticeMatrix:[[2,0,0],[0,2,0],[0,0,2]]}} as unknown as ValidatedVolumetricGrid;
    const values=Array.from({length:shape[0]*shape[1]*shape[2]},(_,index)=>{const i=Math.floor(index/16),j=Math.floor(index/4)%4,k=index%4;return 2*Math.cos(2*Math.PI*i/8)+3*Math.sin(2*Math.PI*j/4)+Math.cos(4*Math.PI*k/4)+5;});
    const profiles=planarProfiles(values,periodicGrid,field,"source_native",0);
    profiles[0].points.forEach((point,index)=>expect(point.sourceValue).toBeCloseTo(2*Math.cos(2*Math.PI*index/8)+5,10));
    expect(samplePotential(values,periodicGrid,field,[3,2,3],0).sourceValue).toBeCloseTo(values[0],10);
  });

  it("rejects singular grid transforms and non-finite source values",()=>{
    const singular={...grid,stepMatrix:[[1,0,0],[2,0,0],[0,0,1]]} as unknown as ValidatedVolumetricGrid;
    expect(()=>samplePotential(new Float64Array(8),singular,field,[1,2,3],0)).toThrow("POTENTIAL_GRID_SINGULAR");
    const invalid=[0,1,2,3,4,5,6,Number.NaN];expect(()=>planarProfiles(invalid,grid,field,"source_native",0)).toThrow("POTENTIAL_PROFILE_INVALID");
  });

  it("reduces a bounded two-million-voxel float64 field without expanding profile storage",()=>{
    const shape:[number,number,number]=[128,128,128];
    const values=new Float64Array(shape[0]*shape[1]*shape[2]);
    for(let index=0;index<values.length;index++)values[index]=(index%257)/257;
    const started=performance.now();const raw=computeRawPlanarProfiles(values,shape);const elapsed=performance.now()-started;
    expect(raw.map((axis)=>axis.length)).toEqual(shape);
    expect(raw.reduce((total,axis)=>total+axis.length,0)).toBe(384);
    expect(raw.every((axis)=>axis.every(Number.isFinite))).toBe(true);
    expect(elapsed).toBeLessThan(15_000);
  });
});
