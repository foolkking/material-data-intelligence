/// <reference lib="webworker" />

import { sampleVolumetricSlice } from "./volumetricSliceModel";
import type { VolumetricSliceWorkerRequest, VolumetricSliceWorkerResponse } from "./volumetricViewerTypes";
import { VolumetricViewerError } from "./volumetricViewerTypes";

const scope = self as unknown as DedicatedWorkerGlobalScope;

scope.onmessage = (event: MessageEvent<VolumetricSliceWorkerRequest>) => {
  const request = event.data;
  if (request?.type !== "slice") return;
  const started = performance.now();
  void sampleVolumetricSlice({
    datasetHash: request.datasetHash,
    fieldHash: request.fieldHash,
    unit: request.unit,
    grid: request.grid,
    dtype: request.dtype,
    fieldBuffer: request.fieldBuffer,
    axis: request.axis,
    fractionalPosition: request.fractionalPosition,
    maximumOutputValues: request.maximumOutputValues,
  }).then((slice) => {
    const response: VolumetricSliceWorkerResponse = Object.freeze({ type: "success", requestId: request.requestId, slice, calculationMs: Number((performance.now() - started).toFixed(3)) });
    scope.postMessage(response, [slice.values.buffer]);
  }).catch((error: unknown) => {
    const response: VolumetricSliceWorkerResponse = Object.freeze({
      type: "failure",
      requestId: request.requestId,
      code: error instanceof VolumetricViewerError ? error.code : "VOLUME_VIEWER_WORKER_FAILED",
      message: error instanceof VolumetricViewerError ? error.message : "Slice Worker failed without exposing internal diagnostics.",
    });
    scope.postMessage(response);
  });
};

export {};
