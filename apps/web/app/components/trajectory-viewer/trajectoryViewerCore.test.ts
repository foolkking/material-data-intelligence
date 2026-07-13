import { describe, expect, it } from "vitest";

import fixed from "../../../../../docs/phase10g/fixtures/trajectory_viewer/fixed_lattice_md_12_frames.json";
import unwrapped from "../../../../../docs/phase10g/fixtures/trajectory_viewer/unwrapped_diffusion_12_frames.json";
import variable from "../../../../../docs/phase10g/fixtures/trajectory_viewer/variable_lattice_relaxation_6_frames.json";
import { TrajectoryFrameCache } from "./trajectoryFrameCache";
import { classifyTrajectoryViewer, mapTrajectoryFrame, validateTrajectoryForViewer } from "./trajectoryFrameMapper";
import { commitTrajectoryFrame, initialTrajectoryViewerState, nextTrajectoryFrame, requestTrajectoryFrame, setTrajectorySpeed } from "./trajectoryViewerState";
import type { ValidatedTrajectory } from "./trajectoryViewerTypes";

const validated=(payload:unknown)=>{const result=validateTrajectoryForViewer(payload);expect(result.ok).toBe(true);return (result as {ok:true;trajectory:ValidatedTrajectory}).trajectory;};

describe("trajectory viewer core",()=>{
  it("maps fixed fractional frames and preserves stable atom identity",()=>{const trajectory=validated(fixed);const first=mapTrajectoryFrame(trajectory,0);const second=mapTrajectoryFrame(trajectory,1);expect(first.scene.atoms.map((atom)=>atom.siteIndex)).toEqual([0,1,2,3]);expect(second.scene.atoms.map((atom)=>atom.siteIndex)).toEqual([0,1,2,3]);expect(first.scene.atoms[1].position).toEqual([1.25,1.25,1.25]);expect(second.scene.atoms[0].position).toEqual([0.05,0,0]);expect(second.lattice).toEqual(first.lattice);});
  it("uses each variable triclinic lattice without changing coordinates",()=>{const trajectory=validated(variable);const first=mapTrajectoryFrame(trajectory,0);const second=mapTrajectoryFrame(trajectory,1);expect(first.lattice[0][0]).toBe(5.8);expect(second.lattice[0][0]).toBe(5.75);expect(second.scene.atoms[1].position).toEqual([2.875,2.875,2.875]);});
  it("does not wrap unwrapped positions and derives deterministic supercell refs",()=>{const trajectory=validated(unwrapped);const frame=mapTrajectoryFrame(trajectory,2,[2,1,1]);expect(frame.scene.warnings).not.toContain("TRAJECTORY_VIEWER_WRAPPING_UNKNOWN");expect(frame.scene.atoms.some((atom)=>atom.position[0]>frame.lattice[0][0])).toBe(true);expect(frame.scene.atoms.map((atom)=>atom.id)).toEqual([...frame.scene.atoms.map((atom)=>atom.id)]);});
  it("classifies before allocation and refuses derived over-budget display",()=>{const trajectory=validated(fixed);expect(classifyTrajectoryViewer(trajectory).mode).toBe("interactive");const huge={...trajectory,atoms:{...trajectory.atoms,count:1000,records:Array.from({length:1000},(_,atom_id)=>({atom_id,label:`H${atom_id}`,species:"H",occupancy:1}))}} as ValidatedTrajectory;expect(classifyTrajectoryViewer(huge,[3,3,3]).mode).toBe("refused");});
  it("keeps state bounded and rejects stale commits",()=>{let state=initialTrajectoryViewerState(12);state=requestTrajectoryFrame(state,2);const stale=commitTrajectoryFrame(state,2,state.activeGeneration-1);expect(stale.currentFrameIndex).toBe(0);state=commitTrajectoryFrame(state,2,state.activeGeneration);expect(state.currentFrameIndex).toBe(2);expect(setTrajectorySpeed(state,100)).toBe(state);expect(nextTrajectoryFrame({...state,currentFrameIndex:11,loop:false}).ended).toBe(true);expect(nextTrajectoryFrame({...state,currentFrameIndex:11,loop:true}).index).toBe(0);});
  it("evicts mapped frames by deterministic LRU and byte caps",()=>{const trajectory=validated(fixed);const cache=new TrajectoryFrameCache(2,4096);cache.set(mapTrajectoryFrame(trajectory,0));cache.set(mapTrajectoryFrame(trajectory,1));expect(cache.get(0)?.frameIndex).toBe(0);cache.set(mapTrajectoryFrame(trajectory,2));expect(cache.snapshot().indices).toEqual([0,2]);expect(cache.get(1)).toBeUndefined();cache.clear();expect(cache.snapshot().size).toBe(0);});
});
