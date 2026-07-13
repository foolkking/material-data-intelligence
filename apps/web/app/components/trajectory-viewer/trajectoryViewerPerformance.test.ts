import { describe, expect, it } from "vitest";

import fixed from "../../../../../docs/phase10g/fixtures/trajectory_viewer/fixed_lattice_md_12_frames.json";
import { TrajectoryFrameCache } from "./trajectoryFrameCache";
import { mapTrajectoryFrame, validateTrajectoryForViewer } from "./trajectoryFrameMapper";
import { TRAJECTORY_VIEWER_BUDGETS, trajectoryPerformanceDecision } from "./trajectoryViewerPerformance";
import type { ValidatedTrajectory } from "./trajectoryViewerTypes";

const validated=()=>{const result=validateTrajectoryForViewer(fixed);expect(result.ok).toBe(true);return (result as {ok:true;trajectory:ValidatedTrajectory}).trajectory;};
const shape=(atoms:number,frames:number)=>{const base=validated();return {...base,atoms:{...base.atoms,count:atoms},frames:{length:frames}} as unknown as ValidatedTrajectory;};

describe("trajectory performance policy",()=>{
  it("uses exact desktop instance tiers and fixed cache/fps budgets",()=>{
    expect(trajectoryPerformanceDecision(shape(384,10),[1,1,1],false)).toMatchObject({mode:"interactive",displayedInstances:384,cacheFrames:7,cacheBytes:16_777_216,maxPlaybackFps:30});
    expect(trajectoryPerformanceDecision(shape(385,10),[1,1,1],false)).toMatchObject({mode:"degraded",displayedInstances:385,cacheFrames:4,cacheBytes:8_388_608,maxPlaybackFps:15});
    expect(trajectoryPerformanceDecision(shape(769,10),[1,1,1],false)).toMatchObject({mode:"refused",displayedInstances:769,cacheFrames:0,coordinateValues:23_070});
  });

  it("uses stricter mobile tiers without artifact-controlled overrides",()=>{
    expect(trajectoryPerformanceDecision(shape(192,10),[1,1,1],true)).toMatchObject({mode:"interactive",cacheFrames:3,cacheBytes:4_194_304,maxPlaybackFps:15,mobile:true});
    expect(trajectoryPerformanceDecision(shape(193,10),[1,1,1],true)).toMatchObject({mode:"degraded",cacheFrames:2,cacheBytes:2_097_152,maxPlaybackFps:15,mobile:true});
    expect(trajectoryPerformanceDecision(shape(385,10),[1,1,1],true)).toMatchObject({mode:"refused",displayedInstances:385,mobile:true});
  });

  it("accounts for all canonical coordinate values before renderer initialization",()=>{
    expect(trajectoryPerformanceDecision(shape(10,10_000),[1,1,1],false)).toMatchObject({mode:"interactive",coordinateValues:300_000});
    expect(trajectoryPerformanceDecision(shape(64,10_000),[1,1,1],false)).toMatchObject({mode:"degraded",coordinateValues:1_920_000});
    expect(trajectoryPerformanceDecision(shape(67,10_000),[1,1,1],false)).toMatchObject({mode:"refused",coordinateValues:2_010_000});
  });

  it("applies supercell multiplication and rejects invalid repeats before mapping",()=>{
    expect(trajectoryPerformanceDecision(shape(48,12),[2,2,2],false)).toMatchObject({mode:"interactive",displayedInstances:384});
    expect(trajectoryPerformanceDecision(shape(49,12),[3,3,3],false)).toMatchObject({mode:"refused",displayedInstances:1323});
    expect(trajectoryPerformanceDecision(shape(4,12),[0,1,1] as never,false)).toMatchObject({mode:"refused",displayedInstances:0});
  });

  it("keeps application-owned concurrency and resource caps immutable",()=>{
    expect(TRAJECTORY_VIEWER_BUDGETS).toMatchObject({maxPendingRequests:1,maxPrefetchRequests:0,maxActiveLoops:1,maxCanvasCount:1,maxContextCount:1,maxMeasurementOverlays:1});
    expect(Object.isFrozen(TRAJECTORY_VIEWER_BUDGETS)).toBe(true);
    expect(Object.isFrozen(TRAJECTORY_VIEWER_BUDGETS.mobile)).toBe(true);
  });
});

describe("trajectory frame cache hardening",()=>{
  it("rejects cross-trajectory frames and invalid limits",()=>{
    const trajectory=validated();
    expect(()=>new TrajectoryFrameCache(17,4096,trajectory.trajectory_id)).toThrow("TRAJECTORY_VIEWER_CACHE_LIMIT_EXCEEDED");
    const cache=new TrajectoryFrameCache(2,4096,trajectory.trajectory_id);
    const frame=mapTrajectoryFrame(trajectory,0);
    const wrong={...frame,scene:{...frame.scene,source:{...frame.scene.source,resourceId:"different-trajectory"}}} as typeof frame;
    expect(()=>cache.set(wrong)).toThrow("TRAJECTORY_VIEWER_CACHE_LIMIT_EXCEEDED");
    expect(cache.snapshot()).toMatchObject({size:0,bytes:0,peakFrames:0,peakBytes:0});
  });

  it("never exceeds frame or byte peaks across repeated LRU churn",()=>{
    const trajectory=validated();
    const first=mapTrajectoryFrame(trajectory,0);
    const cache=new TrajectoryFrameCache(2,first.estimatedBytes*2+16,trajectory.trajectory_id);
    for(let index=0;index<trajectory.frames.length;index+=1)cache.set(mapTrajectoryFrame(trajectory,index),Math.max(0,index-1));
    const metrics=cache.snapshot();
    expect(metrics.size).toBeLessThanOrEqual(metrics.maxFrames);
    expect(metrics.bytes).toBeLessThanOrEqual(metrics.maxBytes);
    expect(metrics.peakFrames).toBeLessThanOrEqual(metrics.maxFrames);
    expect(metrics.peakBytes).toBeLessThanOrEqual(metrics.maxBytes);
    expect(metrics.evictions).toBeGreaterThan(0);
  });
});
