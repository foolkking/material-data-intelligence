import type { MappedTrajectoryFrame } from "./trajectoryViewerTypes";

export class TrajectoryFrameCache {
  readonly maxFrames:number; readonly maxBytes:number; readonly trajectoryId:string;
  private entries=new Map<string,MappedTrajectoryFrame>(); private bytes=0; hits=0; misses=0; evictions=0; peakFrames=0; peakBytes=0;
  constructor(maxFrames:number,maxBytes:number,trajectoryId:string){if(!Number.isSafeInteger(maxFrames)||maxFrames<1||maxFrames>16||!Number.isSafeInteger(maxBytes)||maxBytes<1024||maxBytes>64*1024*1024||!trajectoryId)throw new Error("TRAJECTORY_VIEWER_CACHE_LIMIT_EXCEEDED");this.maxFrames=maxFrames;this.maxBytes=maxBytes;this.trajectoryId=trajectoryId;}
  get(index:number){const key=this.key(index);const value=this.entries.get(key);if(!value){this.misses+=1;return undefined;}this.entries.delete(key);this.entries.set(key,value);this.hits+=1;return value;}
  set(frame:MappedTrajectoryFrame,protectedIndex?:number){if(frame.scene.source.resourceId!==this.trajectoryId||frame.estimatedBytes>this.maxBytes||protectedIndex!==undefined&&(!Number.isSafeInteger(protectedIndex)||protectedIndex<0))throw new Error("TRAJECTORY_VIEWER_CACHE_LIMIT_EXCEEDED");const key=this.key(frame.frameIndex);const previous=this.entries.get(key);if(previous){this.bytes-=previous.estimatedBytes;this.entries.delete(key);}while(this.entries.size>=this.maxFrames||this.bytes+frame.estimatedBytes>this.maxBytes){const oldest=[...this.entries.entries()].find(([,candidate])=>candidate.frameIndex!==protectedIndex);if(!oldest)throw new Error("TRAJECTORY_VIEWER_CACHE_LIMIT_EXCEEDED");this.entries.delete(oldest[0]);this.bytes-=oldest[1].estimatedBytes;this.evictions+=1;}this.entries.set(key,frame);this.bytes+=frame.estimatedBytes;this.peakFrames=Math.max(this.peakFrames,this.entries.size);this.peakBytes=Math.max(this.peakBytes,this.bytes);return frame;}
  clear(){this.entries.clear();this.bytes=0;}
  snapshot(){return Object.freeze({trajectoryId:this.trajectoryId,maxFrames:this.maxFrames,maxBytes:this.maxBytes,size:this.entries.size,bytes:this.bytes,hits:this.hits,misses:this.misses,evictions:this.evictions,peakFrames:this.peakFrames,peakBytes:this.peakBytes,indices:Object.freeze([...this.entries.values()].map(frame=>frame.frameIndex))});}
  private key(index:number){return `${this.trajectoryId}:${index}`;}
}
