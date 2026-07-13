import { TRAJECTORY_PLAYBACK_SPEEDS, type TrajectoryViewerState } from "./trajectoryViewerTypes";

export function initialTrajectoryViewerState(frameCount:number, degraded=false):TrajectoryViewerState {
  return Object.freeze({status:degraded?"degraded":"paused",currentFrameIndex:0,requestedFrameIndex:0,frameCount,playbackSpeed:1,loop:false,isBuffering:false,activeGeneration:0});
}
export function requestTrajectoryFrame(state:TrajectoryViewerState,index:number):TrajectoryViewerState {
  if(!Number.isSafeInteger(index)||index<0||index>=state.frameCount) return state;
  return Object.freeze({...state,requestedFrameIndex:index,isBuffering:index!==state.currentFrameIndex,activeGeneration:state.activeGeneration+1});
}
export function commitTrajectoryFrame(state:TrajectoryViewerState,index:number,generation:number):TrajectoryViewerState {
  if(generation!==state.activeGeneration||index!==state.requestedFrameIndex) return state;
  return Object.freeze({...state,currentFrameIndex:index,isBuffering:false});
}
export function setTrajectoryPlaying(state:TrajectoryViewerState,playing:boolean):TrajectoryViewerState {
  if(state.status==="refused"||state.status==="error"||state.status==="context_lost")return state;
  return Object.freeze({...state,status:playing?"playing":"paused",isBuffering:false});
}
export function setTrajectorySpeed(state:TrajectoryViewerState,speed:number):TrajectoryViewerState {
  return TRAJECTORY_PLAYBACK_SPEEDS.includes(speed as never)?Object.freeze({...state,playbackSpeed:speed as TrajectoryViewerState["playbackSpeed"]}):state;
}
export function nextTrajectoryFrame(state:TrajectoryViewerState):Readonly<{index:number;ended:boolean}> {
  if(state.currentFrameIndex<state.frameCount-1)return Object.freeze({index:state.currentFrameIndex+1,ended:false});
  return Object.freeze({index:state.loop?0:state.currentFrameIndex,ended:!state.loop});
}
