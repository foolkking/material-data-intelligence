import { describe, expect, it, vi } from "vitest";
import { IsosurfaceWorkerClient, type IsosurfaceWorkerLike } from "./isosurfaceWorkerClient";
import type { IsosurfaceWorkerRequest } from "./volumetricViewerTypes";

class FakeWorker extends EventTarget implements IsosurfaceWorkerLike {
  terminate = vi.fn();
  postMessage(message: IsosurfaceWorkerRequest) { queueMicrotask(() => this.dispatchEvent(new MessageEvent("message", { data: { type: "success", requestId: message.requestId, meshes: [], warnings: [], metrics: { requestId: message.requestId } } }))); }
}

describe("isosurface Worker lifecycle", () => {
  it("terminates the application-owned Worker after a successful transfer", async () => {
    const worker = new FakeWorker(); const client = new IsosurfaceWorkerClient(() => worker);
    const result = await client.extract({ type: "extract", fieldId: "field:test", fieldHash: "a".repeat(64), grid: {} as never, dtype: "float32", fieldBuffer: new ArrayBuffer(4), layers: [], caps: { maximumVerticesPerLayer: 1, maximumTrianglesPerLayer: 1, maximumTotalVertices: 1, maximumTotalTriangles: 1, maximumExtractionMs: 100 } });
    expect(result.requestId).toBeGreaterThan(0); expect(worker.terminate).toHaveBeenCalledOnce(); expect(client.snapshot().activeWorkerCount).toBe(0);
  });

  it("cancels an active worker on disposal", () => {
    const worker = new FakeWorker(); const client = new IsosurfaceWorkerClient(() => worker);
    void client.extract({ type: "extract", fieldId: "field:test", fieldHash: "a".repeat(64), grid: {} as never, dtype: "float32", fieldBuffer: new ArrayBuffer(4), layers: [], caps: { maximumVerticesPerLayer: 1, maximumTrianglesPerLayer: 1, maximumTotalVertices: 1, maximumTotalTriangles: 1, maximumExtractionMs: 100 } });
    client.dispose(); expect(worker.terminate).toHaveBeenCalled(); expect(client.snapshot().disposed).toBe(true);
  });
});
