import "@testing-library/jest-dom/vitest";
import { createHash } from "node:crypto";
import fixture from "../../../../../docs/phase10j/fixtures/volumetric_contract/cubic_constant_scalar.json";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { VolumetricSliceVolumeSurface } from "./VolumetricSliceVolumeSurface";
import type { VolumetricSliceWorkerLike } from "./volumetricSliceWorkerClient";

const rawBytes = new Float64Array(64).fill(2).buffer;
const artifacts = [
  { id: "dataset", type: "volumetric_dataset_json", name: "volumetric_dataset.json", content: fixture.raw_dataset },
  { id: "manifest", type: "volumetric_manifest_json", name: "volumetric_manifest.json", content: fixture.manifest },
  { id: "binary", jobId: "job", type: "volumetric_binary", name: "cubic-constant.f64" },
] as never;
const byteLoader = vi.fn(async () => rawBytes.slice(0));

function sliceWorker(): VolumetricSliceWorkerLike {
  const listeners = new Map<string, EventListener>();
  return {
    postMessage: vi.fn((message: { requestId: number }) => queueMicrotask(() => listeners.get("message")?.({ data: { type: "success", requestId: message.requestId, calculationMs: 1.25, slice: { schemaVersion: "phase10j6.volumetric_slice.v1", sourceDatasetHash: "d".repeat(64), sourceFieldHash: "f".repeat(64), axis: 2, fractionalPosition: 0.5, physicalPosition: 2, samplingMode: "exact_grid_plane", lowerIndex: 2, upperIndex: 2, interpolationFactor: 0, periodicWrap: false, outputShape: [4, 4], plane: { origin: [0, 0, 2], basisU: [0, 4, 0], basisV: [4, 0, 0], normal: [0, 0, -1], horizontalAxis: 1, verticalAxis: 0 }, values: new Float64Array(16).fill(2), unit: "electron/angstrom^3", statistics: { minimum: 2, maximum: 2, mean: 2 }, contentHash: "c".repeat(64), provenance: { algorithm: "phase10j6.lattice_axis_linear.v1", sourceMutated: false } } } } as unknown as Event))),
    terminate: vi.fn(),
    addEventListener: vi.fn((name: string, listener: EventListener) => listeners.set(name, listener)),
    removeEventListener: vi.fn((name: string) => listeners.delete(name)),
  };
}

beforeEach(() => {
  vi.stubGlobal("Worker", class {});
  vi.stubGlobal("crypto", { subtle: { digest: async (_algorithm: string, value: BufferSource) => { const bytes = new Uint8Array(value instanceof ArrayBuffer ? value : value.buffer, value instanceof ArrayBuffer ? 0 : value.byteOffset, value instanceof ArrayBuffer ? value.byteLength : value.byteLength); const digest = createHash("sha256").update(bytes).digest(); return digest.buffer.slice(digest.byteOffset, digest.byteOffset + digest.byteLength); } } });
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue({ createImageData: (width: number, height: number) => ({ data: new Uint8ClampedArray(width * height * 4) }), putImageData: vi.fn() } as unknown as CanvasRenderingContext2D);
});
afterEach(() => vi.unstubAllGlobals());

describe("Phase 10J-6 product surface", () => {
  it("loads a validated field and exposes exact Slice metadata with accessible controls", async () => {
    render(<VolumetricSliceVolumeSurface artifacts={artifacts} mode="slice" byteLoader={byteLoader} sliceWorkerFactory={sliceWorker} />);
    await waitFor(() => expect(screen.getByTestId("volumetric-slice-volume-state")).toHaveTextContent("ready"));
    expect(screen.getByRole("region", { name: "Canonical lattice slice controls" })).toHaveTextContent("exact_grid_plane");
    expect(screen.getByTestId("volumetric-slice-axis")).toHaveAccessibleName("Axis");
    expect(screen.getByTestId("volumetric-slice-heatmap")).toHaveAccessibleName(/Quantitative two-dimensional lattice slice heatmap/);
    expect(screen.getByTestId("volumetric-display-window")).toHaveTextContent("source values unchanged");
    expect(screen.getByTestId("volumetric-slice-legend")).toHaveTextContent("electron/angstrom^3");
    expect(screen.getByTestId("volumetric-slice-value-table")).toHaveAccessibleName("Accessible slice value table");
    fireEvent.keyDown(screen.getByTestId("volumetric-slice-heatmap"), { key: "ArrowRight" });
    expect(screen.getByTestId("volumetric-slice-probe")).toHaveTextContent("display normalized");
  });

  it("shows a typed volume fallback without creating a canvas when WebGL2 is unavailable", async () => {
    const { container } = render(<VolumetricSliceVolumeSurface artifacts={artifacts} mode="volume" capabilityOverride="unsupported" byteLoader={byteLoader} sliceWorkerFactory={sliceWorker} />);
    await waitFor(() => expect(screen.getByTestId("volumetric-slice-volume-state")).toHaveTextContent("unsupported"));
    expect(screen.getByTestId("volumetric-slice-volume-status")).toHaveTextContent("Slice and Isosurface remain available");
    expect(container.querySelector("canvas, iframe, script")).toBeNull();
    expect(screen.getByTestId("volumetric-volume-metrics")).toHaveTextContent("width=nz, height=ny, depth=nx");
  });
});
