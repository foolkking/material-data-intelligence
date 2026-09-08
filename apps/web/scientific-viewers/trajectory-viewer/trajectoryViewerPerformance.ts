import type { ImageOffset } from "../viewer-scene/viewerSceneRendererTypes";
import { validSupercellRepeat } from "../viewer-scene/viewerSceneSupercell";
import type { TrajectoryPerformanceDecision, ValidatedTrajectory } from "./trajectoryViewerTypes";

export const TRAJECTORY_VIEWER_BUDGETS = Object.freeze({
  desktop: Object.freeze({interactiveInstances:384,degradedInstances:768,interactiveValues:300_000,degradedValues:2_000_000,interactiveFps:30,degradedFps:15,interactiveCacheFrames:7,degradedCacheFrames:4,interactiveCacheBytes:16_777_216,degradedCacheBytes:8_388_608}),
  mobile: Object.freeze({interactiveInstances:192,degradedInstances:384,interactiveValues:150_000,degradedValues:1_000_000,interactiveFps:15,degradedFps:15,interactiveCacheFrames:3,degradedCacheFrames:2,interactiveCacheBytes:4_194_304,degradedCacheBytes:2_097_152}),
  maxPendingRequests:1,maxPrefetchRequests:0,maxActiveLoops:1,maxCanvasCount:1,maxContextCount:1,maxMeasurementOverlays:1,
});

export function trajectoryPerformanceDecision(trajectory:ValidatedTrajectory,repeat:ImageOffset,mobile:boolean):TrajectoryPerformanceDecision{
  const budget=mobile?TRAJECTORY_VIEWER_BUDGETS.mobile:TRAJECTORY_VIEWER_BUDGETS.desktop;
  const coordinateValues=trajectory.frames.length*trajectory.atoms.count*3;
  if(!validSupercellRepeat(repeat))return refused(0,coordinateValues,mobile,"TRAJECTORY_VIEWER_BUDGET_EXCEEDED");
  const cells=repeat[0]*repeat[1]*repeat[2];
  const displayedInstances=trajectory.atoms.count*cells;
  if(displayedInstances>budget.degradedInstances||coordinateValues>budget.degradedValues)return refused(displayedInstances,coordinateValues,mobile,"TRAJECTORY_VIEWER_BUDGET_EXCEEDED");
  const degraded=displayedInstances>budget.interactiveInstances||coordinateValues>budget.interactiveValues;
  return Object.freeze({
    mode:degraded?"degraded":"interactive",displayedInstances,coordinateValues,mobile,
    cacheFrames:degraded?budget.degradedCacheFrames:budget.interactiveCacheFrames,
    cacheBytes:degraded?budget.degradedCacheBytes:budget.interactiveCacheBytes,
    maxPlaybackFps:degraded?budget.degradedFps:budget.interactiveFps,
    maxPendingRequests:TRAJECTORY_VIEWER_BUDGETS.maxPendingRequests,maxPrefetchRequests:0,
    warnings:Object.freeze(degraded?["TRAJECTORY_VIEWER_DEGRADED_MODE"]:[]),reason:null,
  });
}

function refused(displayedInstances:number,coordinateValues:number,mobile:boolean,reason:string):TrajectoryPerformanceDecision{
  return Object.freeze({mode:"refused",displayedInstances,coordinateValues,mobile,cacheFrames:0,cacheBytes:0,maxPlaybackFps:mobile?15:30,maxPendingRequests:1,maxPrefetchRequests:0,warnings:Object.freeze([]),reason});
}
