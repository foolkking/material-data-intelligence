import { extractIsosurfaces } from "./isosurfaceExtraction";
import { computeRawPlanarProfiles } from "./electrostaticPotentialProduct";
import type { IsosurfaceWorkerRequest, IsosurfaceWorkerResponse } from "./volumetricViewerTypes";
import { VolumetricViewerError } from "./volumetricViewerTypes";

const scope = self as unknown as {
  onmessage: ((event: MessageEvent<IsosurfaceWorkerRequest>) => void) | null;
  postMessage: (message: IsosurfaceWorkerResponse, transfer?: Transferable[]) => void;
};

scope.onmessage = (event) => {
  const request = event.data;
  let potentialProfiles:Extract<IsosurfaceWorkerResponse,{type:"success"}>["potentialProfiles"];
  try{const profileStart=performance.now();potentialProfiles=request.computePotentialProfiles?Object.freeze({sourceValues:computeRawPlanarProfiles(request.dtype==="float32"?new Float32Array(request.fieldBuffer):new Float64Array(request.fieldBuffer),request.grid.shape),calculationMs:performance.now()-profileStart}):undefined;}
  catch{scope.postMessage(Object.freeze({type:"failure",requestId:request.requestId,code:"VOLUME_VIEWER_WORKER_FAILED",message:"Potential profile reduction could not complete safely."}));return;}
  void extractIsosurfaces(request).then((result) => {
    const response: IsosurfaceWorkerResponse = Object.freeze({ type:"success", requestId:request.requestId, meshes:result.meshes, metrics:result.metrics, warnings:result.warnings, potentialProfiles });
    const transfer = result.meshes.flatMap((mesh) => [mesh.positions.buffer, mesh.normals.buffer, mesh.indices.buffer]);
    scope.postMessage(response, transfer);
  }).catch((error:unknown) => {
    const code = error instanceof VolumetricViewerError ? error.code : "VOLUME_VIEWER_WORKER_FAILED";
    const response: IsosurfaceWorkerResponse = Object.freeze({ type:"failure", requestId:request.requestId, code, message:"Isosurface extraction could not complete safely." });
    scope.postMessage(response);
  });
};

export {};
