import { extractIsosurfaces } from "./isosurfaceExtraction";
import type { IsosurfaceWorkerRequest, IsosurfaceWorkerResponse } from "./volumetricViewerTypes";
import { VolumetricViewerError } from "./volumetricViewerTypes";

const scope = self as unknown as {
  onmessage: ((event: MessageEvent<IsosurfaceWorkerRequest>) => void) | null;
  postMessage: (message: IsosurfaceWorkerResponse, transfer?: Transferable[]) => void;
};

scope.onmessage = (event) => {
  const request = event.data;
  void extractIsosurfaces(request).then((result) => {
    const response: IsosurfaceWorkerResponse = Object.freeze({ type:"success", requestId:request.requestId, meshes:result.meshes, metrics:result.metrics, warnings:result.warnings });
    const transfer = result.meshes.flatMap((mesh) => [mesh.positions.buffer, mesh.normals.buffer, mesh.indices.buffer]);
    scope.postMessage(response, transfer);
  }).catch((error:unknown) => {
    const code = error instanceof VolumetricViewerError ? error.code : "VOLUME_VIEWER_WORKER_FAILED";
    const response: IsosurfaceWorkerResponse = Object.freeze({ type:"failure", requestId:request.requestId, code, message:"Isosurface extraction could not complete safely." });
    scope.postMessage(response);
  });
};

export {};
