import type { VolumetricSliceWorkerRequest, VolumetricSliceWorkerResponse } from "./volumetricViewerTypes";
import { VolumetricViewerError } from "./volumetricViewerTypes";

export type VolumetricSliceWorkerLike = Pick<Worker, "postMessage" | "terminate" | "addEventListener" | "removeEventListener">;
export type VolumetricSliceWorkerFactory = () => VolumetricSliceWorkerLike;

export const defaultVolumetricSliceWorkerFactory: VolumetricSliceWorkerFactory = () => new Worker(
  new URL("./volumetricSlice.worker.ts", import.meta.url),
  { type: "module", name: "mdi-volumetric-slice" },
);

export class VolumetricSliceWorkerClient {
  private worker: VolumetricSliceWorkerLike | null = null;
  private pending: { requestId: number; cleanup: () => void; reject: (error: unknown) => void } | null = null;
  private revision = 0;
  private disposed = false;

  constructor(private readonly factory: VolumetricSliceWorkerFactory = defaultVolumetricSliceWorkerFactory) {}

  sample(request: Omit<VolumetricSliceWorkerRequest, "requestId">): Promise<Extract<VolumetricSliceWorkerResponse, { type: "success" }>> {
    if (this.disposed) return Promise.reject(new VolumetricViewerError("VOLUME_VIEWER_WORKER_UNAVAILABLE", "Slice client is disposed."));
    // A module Worker cannot preempt a synchronous sampling loop. Replacing the
    // Worker is the bounded cancellation mechanism for an in-flight revision.
    this.cancelPending(true);
    const requestId = ++this.revision;
    let worker: VolumetricSliceWorkerLike;
    try { worker = this.worker ?? this.factory(); } catch { return Promise.reject(new VolumetricViewerError("VOLUME_VIEWER_WORKER_UNAVAILABLE", "Application-owned slice Worker is unavailable.")); }
    this.worker = worker;
    return new Promise((resolve, reject) => {
      const cleanup = () => {
        worker.removeEventListener("message", onMessage as EventListener);
        worker.removeEventListener("error", onError as EventListener);
      };
      const finish = () => { cleanup(); if (this.pending?.requestId === requestId) this.pending = null; };
      const onMessage = (event: MessageEvent<VolumetricSliceWorkerResponse>) => {
        const response = event.data;
        if (response.requestId !== requestId || requestId !== this.revision) return;
        finish();
        if (response.type === "failure") reject(new VolumetricViewerError(response.code, response.message));
        else resolve(response);
      };
      const onError = () => { finish(); worker.terminate(); if (this.worker === worker) this.worker = null; reject(new VolumetricViewerError("VOLUME_VIEWER_WORKER_FAILED", "Slice Worker failed safely.")); };
      worker.addEventListener("message", onMessage as EventListener);
      worker.addEventListener("error", onError as EventListener);
      this.pending = { requestId, cleanup, reject };
      const message = Object.freeze({ ...request, requestId }) as VolumetricSliceWorkerRequest;
      worker.postMessage(message, [message.fieldBuffer]);
    });
  }

  cancel() { this.cancelPending(); this.worker?.terminate(); this.worker = null; }
  dispose() { if (this.disposed) return; this.disposed = true; this.cancel(); }
  snapshot() { return Object.freeze({ activeWorkerCount: this.worker ? 1 : 0, revision: this.revision, disposed: this.disposed }); }

  private cancelPending(terminateWorker = false) {
    this.revision += 1;
    const pending = this.pending;
    this.pending = null;
    if (!pending) return;
    pending.cleanup();
    pending.reject(new VolumetricViewerError("VOLUME_VIEWER_WORKER_FAILED", "Slice request was superseded by a newer revision."));
    if (terminateWorker && this.worker) {
      this.worker.terminate();
      this.worker = null;
    }
  }
}
