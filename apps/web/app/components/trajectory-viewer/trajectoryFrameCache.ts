import type { MappedTrajectoryFrame } from "./trajectoryViewerTypes";

export class TrajectoryFrameCache {
  readonly maxFrames:number; readonly maxBytes:number;
  private entries=new Map<number,MappedTrajectoryFrame>(); private bytes=0; hits=0; misses=0;
  constructor(maxFrames:number,maxBytes:number){if(!Number.isSafeInteger(maxFrames)||maxFrames<1||maxFrames>16||!Number.isSafeInteger(maxBytes)||maxBytes<1024||maxBytes>64*1024*1024)throw new Error("TRAJECTORY_VIEWER_CACHE_LIMIT_EXCEEDED");this.maxFrames=maxFrames;this.maxBytes=maxBytes;}
  get(index:number){const value=this.entries.get(index);if(!value){this.misses+=1;return undefined;}this.entries.delete(index);this.entries.set(index,value);this.hits+=1;return value;}
  set(frame:MappedTrajectoryFrame){if(frame.estimatedBytes>this.maxBytes)throw new Error("TRAJECTORY_VIEWER_CACHE_LIMIT_EXCEEDED");const previous=this.entries.get(frame.frameIndex);if(previous){this.bytes-=previous.estimatedBytes;this.entries.delete(frame.frameIndex);}this.entries.set(frame.frameIndex,frame);this.bytes+=frame.estimatedBytes;while(this.entries.size>this.maxFrames||this.bytes>this.maxBytes){const oldest=this.entries.keys().next().value as number|undefined;if(oldest===undefined)break;const removed=this.entries.get(oldest)!;this.entries.delete(oldest);this.bytes-=removed.estimatedBytes;}return frame;}
  clear(){this.entries.clear();this.bytes=0;}
  snapshot(){return Object.freeze({maxFrames:this.maxFrames,maxBytes:this.maxBytes,size:this.entries.size,bytes:this.bytes,hits:this.hits,misses:this.misses,indices:Object.freeze([...this.entries.keys()])});}
}
