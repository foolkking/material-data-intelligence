import type { IsosurfaceWorkerRequest, IsosurfaceWorkerResponse } from "./volumetricViewerTypes";
import { VolumetricViewerError } from "./volumetricViewerTypes";

export type IsosurfaceWorkerLike = Pick<Worker,"postMessage"|"terminate"|"addEventListener"|"removeEventListener">;
export type IsosurfaceWorkerFactory = () => IsosurfaceWorkerLike;

export const defaultIsosurfaceWorkerFactory:IsosurfaceWorkerFactory=()=>new Worker(new URL("./isosurface.worker.ts",import.meta.url),{type:"module",name:"mdi-isosurface-extractor"});

export class IsosurfaceWorkerClient {
  private worker:IsosurfaceWorkerLike|null=null;
  private revision=0;
  private disposed=false;
  constructor(private readonly factory:IsosurfaceWorkerFactory=defaultIsosurfaceWorkerFactory){}

  extract(request:Omit<IsosurfaceWorkerRequest,"requestId">):Promise<Extract<IsosurfaceWorkerResponse,{type:"success"}>>{
    if(this.disposed)return Promise.reject(new VolumetricViewerError("VOLUME_VIEWER_WORKER_UNAVAILABLE","Extraction client is disposed."));
    this.cancel();const requestId=++this.revision;let worker:IsosurfaceWorkerLike;
    try{worker=this.factory();}catch{throw new VolumetricViewerError("VOLUME_VIEWER_WORKER_UNAVAILABLE","Application-owned extraction Worker is unavailable.");}
    this.worker=worker;
    return new Promise((resolve,reject)=>{
      const timeout=setTimeout(()=>{cleanup();worker.terminate();if(this.worker===worker)this.worker=null;reject(new VolumetricViewerError("VOLUME_VIEWER_WORKER_FAILED","Extraction exceeded the Worker time budget."));},request.caps.maximumExtractionMs+2_000);
      const cleanup=()=>{clearTimeout(timeout);worker.removeEventListener("message",onMessage as EventListener);worker.removeEventListener("error",onError as EventListener);};
      const onMessage=(event:MessageEvent<IsosurfaceWorkerResponse>)=>{if(event.data.requestId!==requestId||requestId!==this.revision)return;cleanup();worker.terminate();if(this.worker===worker)this.worker=null;if(event.data.type==="failure")reject(new VolumetricViewerError(event.data.code,event.data.message));else resolve(event.data);};
      const onError=()=>{cleanup();worker.terminate();if(this.worker===worker)this.worker=null;reject(new VolumetricViewerError("VOLUME_VIEWER_WORKER_FAILED","Extraction Worker failed without exposing internal diagnostics."));};
      worker.addEventListener("message",onMessage as EventListener);worker.addEventListener("error",onError as EventListener);
      const message=Object.freeze({...request,requestId}) as IsosurfaceWorkerRequest;
      worker.postMessage(message,[message.fieldBuffer]);
    });
  }
  cancel(){this.revision+=1;this.worker?.terminate();this.worker=null;}
  dispose(){if(this.disposed)return;this.disposed=true;this.cancel();}
  snapshot(){return Object.freeze({activeWorkerCount:this.worker?1:0,revision:this.revision,disposed:this.disposed});}
}
