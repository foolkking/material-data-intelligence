import { describe, expect, it } from "vitest";

import { buildBandBZLinkModel } from "./bandBZLinkModel";
import { bandBZFixture } from "./bandBZLinkTestFixture";

function bundle() { const value=bandBZFixture();return{band:value.band,bandHash:"a".repeat(64),bz:{reciprocal:value.reciprocal,zone:value.zone,kpath:value.kpath,manifest:value.manifest}}; }

describe("Band-BZ compatibility and mapping",()=>{
  it("builds deterministic point occurrence, segment, sample and branch mappings without label identity",()=>{const first=buildBandBZLinkModel(bundle());const second=buildBandBZLinkModel(bundle());expect(first.ok).toBe(true);expect(second.ok).toBe(true);if(!first.ok||!second.ok)return;expect(first.model.schemaVersion).toBe("phase10i3.reciprocal_band_bz_link.v1");expect(first.model.segments).toHaveLength(first.model.samples.length/2);expect(first.model.pointOccurrences).toHaveLength(first.model.samples.length);expect(first.model.samples.every((item)=>item.t===0||item.t===1)).toBe(true);expect(first.model.pointOccurrences.some((item,index,all)=>all.some((other,otherIndex)=>otherIndex!==index&&other.bzPointId===item.bzPointId&&other.id!==item.id))).toBe(true);expect(first.model.segments.map((item)=>item.bzSegmentId)).toEqual(second.model.segments.map((item)=>item.bzSegmentId));expect(first.model.warnings).toContain("BAND_PATH_PROVIDER_UNDECLARED_EXACT_GEOMETRY_EQUIVALENCE");});
  it.each([
    ["structure",(value:ReturnType<typeof bundle>)=>{value.band.structure_identity="f".repeat(64);},"BAND_BZ_STRUCTURE_MISMATCH"],
    ["primitive",(value:ReturnType<typeof bundle>)=>{value.band.real_space_lattice_angstrom[0][0]+=0.1;},"BAND_BZ_PRIMITIVE_LATTICE_MISMATCH"],
    ["convention",(value:ReturnType<typeof bundle>)=>{value.band.reciprocal_convention="crystallographic_no_2pi";},"BAND_BZ_CONVENTION_MISMATCH"],
    ["path",(value:ReturnType<typeof bundle>)=>{value.band.qpoints[1].coordinates=[.2,.2,.2];},"BAND_BZ_PATH_MISMATCH"],
    ["break",(value:ReturnType<typeof bundle>)=>{value.band.segments[1].discontinuous_from_previous=!value.band.segments[1].discontinuous_from_previous;},"BAND_BZ_DISCONTINUITY_MISMATCH"],
  ])("rejects %s mismatch before linked interaction",(_name,mutate,code)=>{const value=bundle();mutate(value);const result=buildBandBZLinkModel(value);expect(result.ok).toBe(false);if(!result.ok)expect(result.errors).toContain(code);});
  it("maps reversed segments with explicit direction instead of silently treating them as forward",()=>{const value=bundle();const segment=value.band.segments[0];const start=segment.start_qpoint_index,end=segment.end_qpoint_index;[value.band.qpoints[start].coordinates,value.band.qpoints[end].coordinates]=[value.band.qpoints[end].coordinates,value.band.qpoints[start].coordinates];[value.band.qpoints[start].label,value.band.qpoints[end].label]=[value.band.qpoints[end].label,value.band.qpoints[start].label];[value.band.qpoints[start].source_label,value.band.qpoints[end].source_label]=[value.band.qpoints[end].source_label,value.band.qpoints[start].source_label];[segment.start_label,segment.end_label]=[segment.end_label,segment.start_label];const result=buildBandBZLinkModel(value);expect(result.ok).toBe(true);if(result.ok)expect(result.model.segments[0].direction).toBe("reverse");});
});
