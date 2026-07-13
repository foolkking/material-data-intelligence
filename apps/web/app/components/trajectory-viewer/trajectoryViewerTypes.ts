import type { ImageOffset, RenderVector3, ValidatedRenderScene } from "../viewer-scene/viewerSceneRendererTypes";

export type TrajectoryAtomRecord = Readonly<{ atom_id:number; label:string; species:string; occupancy:number }>;
export type TrajectoryEnergy = Readonly<{ potential:number|null; kinetic:number|null; total:number|null; free:number|null; scope:string; unit:"electronvolt" }>;
export type TrajectoryFrame = Readonly<{
  schema_version:"phase10g.trajectory_frame.v1"; frame_index:number; atom_ids:readonly number[];
  positions:readonly RenderVector3[]; lattice:readonly [RenderVector3,RenderVector3,RenderVector3]|null;
  time:number|null; step:number|null; velocities:readonly RenderVector3[]|null; forces:readonly RenderVector3[]|null;
  energy:TrajectoryEnergy|null; temperature:number|null; metadata:Readonly<Record<string,unknown>>;
}>;
export type ValidatedTrajectory = Readonly<{
  schema_version:"phase10g.trajectory.v1"; trajectory_id:string;
  kind:"molecular_dynamics"|"geometry_optimization"|"structure_sequence"|"unknown_static_sequence";
  atom_identity_mode:"stable_index"; coordinate_mode:"fractional"|"cartesian";
  position_wrapping:"wrapped"|"unwrapped"|"unknown"; lattice_mode:"fixed"|"variable";
  fixed_lattice:readonly [RenderVector3,RenderVector3,RenderVector3]|null; periodic_boundary:readonly [boolean,boolean,boolean];
  atoms:Readonly<{count:number;records:readonly TrajectoryAtomRecord[]}>; frames:readonly TrajectoryFrame[];
  properties:Readonly<{positions:true;velocities:boolean;forces:boolean;energy:boolean;temperature:boolean;stress:false}>;
  time:Readonly<{unit:"femtosecond"|"picosecond"|null}>; units:Readonly<Record<string,unknown>>;
  metadata:Readonly<Record<string,unknown>>; provenance:Readonly<Record<string,unknown>>; warnings:readonly string[];
}>;

export type TrajectoryViewerStatus = "idle"|"loading"|"ready"|"playing"|"paused"|"degraded"|"refused"|"error"|"context_lost";
export type TrajectoryViewerState = Readonly<{
  status:TrajectoryViewerStatus; currentFrameIndex:number; requestedFrameIndex:number; frameCount:number;
  playbackSpeed:0.25|0.5|1|2|4; loop:boolean; isBuffering:boolean; activeGeneration:number;
}>;
export type TrajectoryPeriodicAtomRef = Readonly<{atomIndex:number;imageOffset:ImageOffset}>;
export type MappedTrajectoryFrame = Readonly<{
  frameIndex:number; scene:ValidatedRenderScene; lattice:ValidatedRenderScene["lattice"]["matrix"];
  rawFrame:TrajectoryFrame; mapMs:number; estimatedBytes:number;
}>;
export type TrajectoryPerformanceDecision = Readonly<{
  mode:"interactive"|"degraded"|"refused"; displayedInstances:number; coordinateValues:number; mobile:boolean;
  cacheFrames:number; cacheBytes:number; maxPlaybackFps:15|30; maxPendingRequests:1; maxPrefetchRequests:0;
  warnings:readonly string[]; reason:string|null;
}>;

export const TRAJECTORY_PLAYBACK_SPEEDS = Object.freeze([0.25,0.5,1,2,4] as const);
export const TRAJECTORY_DEFAULT_REPEAT = Object.freeze([1,1,1]) as ImageOffset;
