import "@testing-library/jest-dom/vitest";
import { createHash } from "node:crypto";
import fixture from "../../../../../tests/fixtures/volumetric_contract/cubic_constant_scalar.json";
import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Artifact } from "../../lib/planner-api";

import { validateVolumetricArtifacts } from "./volumetricValidation";
import { VolumetricPreviewPanel } from "./VolumetricPreviewPanel";
import { VolumetricSliceVolumeSurface } from "./VolumetricSliceVolumeSurface";
import type { VolumetricSliceWorkerLike } from "./volumetricSliceWorkerClient";

const renderer = vi.hoisted(() => ({ create: vi.fn(), volume: vi.fn() }));
vi.mock("../../../scientific-viewers/volumetric-viewer/volumetricSliceRendererEngine", () => ({ createVolumetricSliceRendererEngine: renderer.create }));
vi.mock("../../../scientific-viewers/volumetric-viewer/volumetricVolumeRendererEngine", () => ({ createVolumetricVolumeRendererEngine: renderer.volume }));
function mockSliceEngine() {
  return { setStructureVisible: vi.fn(), setCellVisible: vi.fn(), resetCamera: vi.fn(), render: vi.fn(), exportPng: vi.fn(), dispose: vi.fn() };
}

const rawBytes = new Float64Array(64).fill(2).buffer;
const artifacts = [
  { id: "dataset", type: "volumetric_dataset_json", name: "volumetric_dataset.json", content: fixture.raw_dataset },
  { id: "manifest", type: "volumetric_manifest_json", name: "volumetric_manifest.json", content: fixture.manifest },
  { id: "binary", jobId: "job", type: "volumetric_binary", name: "cubic-constant.f64" },
] as never;
const artifactsWithOverlay = [...(artifacts as Artifact[]), {
  id: "overlay", type: "volumetric_structure_overlay_json", content: {
    schema_version: "phase10j2.volumetric_structure_overlay.v1",
    overlay_id: `volume-overlay:${"a".repeat(64)}`, content_hash: "a".repeat(64),
    grid_id: fixture.grid.grid_id, grid_content_hash: fixture.grid.content_hash,
    kind: "non_periodic_atom_context", viewer_scene: null,
    atom_records: [{ atomic_number: 1, cartesian_angstrom: [1, 1, 1] }],
    unavailable_reason: null, security: fixture.grid.security,
  },
}] as Artifact[];
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
  renderer.create.mockReset();
  renderer.volume.mockReset();
  renderer.create.mockImplementation(async () => mockSliceEngine());
  vi.stubGlobal("Worker", class {});
  vi.stubGlobal("crypto", { subtle: { digest: async (_algorithm: string, value: BufferSource) => { const bytes = new Uint8Array(value instanceof ArrayBuffer ? value : value.buffer, value instanceof ArrayBuffer ? 0 : value.byteOffset, value instanceof ArrayBuffer ? value.byteLength : value.byteLength); const digest = createHash("sha256").update(bytes).digest(); return digest.buffer.slice(digest.byteOffset, digest.byteOffset + digest.byteLength); } } });
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue({ createImageData: (width: number, height: number) => ({ data: new Uint8ClampedArray(width * height * 4) }), putImageData: vi.fn() } as unknown as CanvasRenderingContext2D);
});
afterEach(() => vi.unstubAllGlobals());

describe("Phase 10J-6 product surface", () => {
  it("keeps the selected field across surface, slice, volume and metadata, and clears it for a new source", async () => {
    const dataset = structuredClone(fixture.raw_dataset);
    dataset.fields = ["a", "b"].map((id) => ({ ...dataset.fields[0], field_id: `field:${id}`, field_name: `Field ${id}`, payload_id: `payload:${id.repeat(64)}`, payload_logical_sha256: id.repeat(64) }));
    dataset.payloads = ["a", "b"].map((id) => ({ ...dataset.payloads[0], payload_id: `payload:${id.repeat(64)}`, logical_sha256: id.repeat(64) }));
    const validation = validateVolumetricArtifacts(dataset, fixture.manifest);
    expect(validation.ok, JSON.stringify(validation)).toBe(true);
    const source = [{ id: "dataset", type: "volumetric_dataset_json", content: dataset }, { id: "manifest", type: "volumetric_manifest_json", content: fixture.manifest }] as never;
    const { rerender } = render(<VolumetricPreviewPanel artifacts={source} />);
    const selector = await screen.findByTestId("volumetric-field-selector");
    fireEvent.change(selector, { target: { value: "field:b" } });
    fireEvent.click(screen.getByRole("tab", { name: "晶格切片" }));
    await waitFor(() => expect(screen.getByTestId("volumetric-slice-volume-field")).toHaveValue("field:b"));
    fireEvent.click(screen.getByRole("tab", { name: "体渲染" }));
    expect(screen.getByTestId("volumetric-slice-volume-field")).toHaveValue("field:b");
    fireEvent.change(screen.getByTestId("volumetric-slice-volume-field"), { target: { value: "field:a" } });
    fireEvent.click(screen.getByRole("tab", { name: "元数据" }));
    fireEvent.click(screen.getByRole("tab", { name: "等值面" }));
    await waitFor(() => expect(screen.getByTestId("volumetric-field-selector")).toHaveValue("field:a"));
    fireEvent.change(screen.getByTestId("volumetric-field-selector"), { target: { value: "field:b" } });
    const changedDataset = { ...dataset, content_hash: "b".repeat(64) };
    const changedManifest = { ...fixture.manifest, dataset_content_hash: changedDataset.content_hash };
    rerender(<VolumetricPreviewPanel artifacts={[{ id: "dataset", type: "volumetric_dataset_json", content: changedDataset }, { id: "manifest", type: "volumetric_manifest_json", content: changedManifest }] as never} />);
    await waitFor(() => expect(screen.getByTestId("volumetric-field-selector")).toHaveValue("field:a"));
  });

  it("applies the latest volume controls after asynchronous renderer initialization", async () => {
    const engine = { ...mockSliceEngine(), setTransferFunction: vi.fn(), setQuality: vi.fn(), setClipping: vi.fn(), setProjection: vi.fn(), snapshot: vi.fn(() => ({})) };
    let finish!: () => void;
    renderer.volume.mockImplementation(() => new Promise((resolve) => { finish = () => resolve({ engine, capabilities: { webgl2: true } }); }));
    render(<VolumetricSliceVolumeSurface artifacts={artifactsWithOverlay} mode="volume" byteLoader={byteLoader} capabilityOverride="supported" />);
    await waitFor(() => expect(renderer.volume).toHaveBeenCalledOnce());
    fireEvent.click(screen.getByRole("checkbox", { name: "结构" }));
    fireEvent.click(screen.getByRole("checkbox", { name: "晶胞" }));
    fireEvent.change(screen.getByRole("combobox", { name: "投影" }), { target: { value: "orthographic" } });
    fireEvent.change(screen.getByRole("combobox", { name: "质量" }), { target: { value: "high" } });
    finish();
    await waitFor(() => expect(screen.getByTestId("volumetric-slice-volume-state")).toHaveTextContent("已就绪"));
    expect(engine.setStructureVisible).toHaveBeenLastCalledWith(false);
    expect(engine.setCellVisible).toHaveBeenLastCalledWith(false);
    expect(engine.setProjection).toHaveBeenLastCalledWith("orthographic");
    expect(engine.setQuality).toHaveBeenLastCalledWith(expect.objectContaining({ id: "high" }));
  });

  it("retains hidden overlays when color changes recreate the 3D slice", async () => {
    render(<VolumetricSliceVolumeSurface artifacts={artifactsWithOverlay} mode="slice" byteLoader={byteLoader} sliceWorkerFactory={sliceWorker} />);
    await waitFor(() => expect(screen.getByTestId("volumetric-slice-volume-state")).toHaveTextContent("已就绪"));
    fireEvent.click(screen.getByRole("button", { name: "三维切面" }));
    await waitFor(() => expect(renderer.create).toHaveBeenCalledTimes(1));
    const first = await renderer.create.mock.results[0].value;
    fireEvent.click(screen.getByRole("checkbox", { name: "结构" }));
    fireEvent.click(screen.getByRole("checkbox", { name: "晶胞" }));
    expect(first.setStructureVisible).toHaveBeenLastCalledWith(false);
    expect(first.setCellVisible).toHaveBeenLastCalledWith(false);
    fireEvent.click(screen.getByText("色彩与数值窗口"));
    fireEvent.change(screen.getByRole("combobox", { name: "色板" }), { target: { value: "magma" } });
    await waitFor(() => expect(renderer.create).toHaveBeenCalledTimes(2));
    const second = await renderer.create.mock.results[1].value;
    await waitFor(() => expect(second.setCellVisible).toHaveBeenLastCalledWith(false));
    expect(second.setStructureVisible).toHaveBeenLastCalledWith(false);
    expect(first.dispose).toHaveBeenCalled();
    expect(screen.getByRole("checkbox", { name: "晶胞" })).not.toBeChecked();
  });

  it("disposes a late 3D renderer without applying it to the returned 2D view", async () => {
    const late = mockSliceEngine();
    let finish!: (engine: ReturnType<typeof mockSliceEngine>) => void;
    renderer.create.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
    render(<VolumetricSliceVolumeSurface artifacts={artifacts} mode="slice" byteLoader={byteLoader} sliceWorkerFactory={sliceWorker} />);
    await waitFor(() => expect(screen.getByTestId("volumetric-slice-volume-state")).toHaveTextContent("已就绪"));
    fireEvent.click(screen.getByRole("button", { name: "三维切面" }));
    await waitFor(() => expect(renderer.create).toHaveBeenCalledTimes(1));
    fireEvent.click(screen.getByRole("button", { name: "二维热图" }));
    finish(late);
    await waitFor(() => expect(late.dispose).toHaveBeenCalledOnce());
    expect(late.setCellVisible).not.toHaveBeenCalled();
    expect(screen.getByTestId("volumetric-slice-heatmap")).toBeVisible();
  });

  it("loads a validated field and exposes exact Slice metadata with accessible controls", async () => {
    render(<VolumetricSliceVolumeSurface artifacts={artifacts} mode="slice" byteLoader={byteLoader} sliceWorkerFactory={sliceWorker} />);
    await waitFor(() => expect(screen.getByTestId("volumetric-slice-volume-state")).toHaveTextContent("已就绪"));
    expect(screen.getByRole("region", { name: "晶格切片控制" })).toHaveTextContent("二维热图");
    expect(screen.getByText("精确网格切面 · 2.000 Å")).toBeVisible();
    expect(screen.getByTestId("volumetric-slice-axis")).toHaveAccessibleName("轴");
    expect(screen.getByTestId("volumetric-slice-heatmap")).toHaveAccessibleName(/定量二维晶格切片热图/);
    expect(screen.getByTestId("volumetric-display-window")).toHaveTextContent("源数据保持不变");
    expect(screen.getByTestId("volumetric-slice-legend")).toHaveTextContent("电子/Å³");
    expect(screen.getByTestId("volumetric-slice-value-table")).toHaveAccessibleName("切片数值表");
    fireEvent.keyDown(screen.getByTestId("volumetric-slice-heatmap"), { key: "ArrowRight" });
    expect(screen.getByTestId("volumetric-slice-probe")).toHaveTextContent("显示归一化值");
    expect(screen.getByTestId("volumetric-slice-probe")).toHaveTextContent("0.00000, 1.00000, 2.00000 Å");
    const rows = within(screen.getByTestId("volumetric-slice-value-table")).getAllByRole("row");
    expect(rows[4]).toHaveTextContent("0.00000, 3.00000, 2.00000");
    fireEvent.click(within(rows[4]).getByRole("button"));
    expect(screen.getByTestId("volumetric-slice-probe")).toHaveTextContent("行 0，列 3");
    expect(screen.getByTestId("volumetric-slice-probe")).toHaveTextContent("0.00000, 3.00000, 2.00000 Å");
    fireEvent.keyDown(screen.getByTestId("volumetric-slice-heatmap"), { key: "ArrowLeft" });
    expect(screen.getByTestId("volumetric-slice-probe")).toHaveTextContent("行 0，列 2");
    expect(screen.getByTestId("volumetric-slice-probe")).toHaveTextContent("0.00000, 2.00000, 2.00000 Å");
    fireEvent.click(screen.getByText("色彩与数值窗口"));
    fireEvent.change(screen.getByRole("spinbutton", { name: "窗口低值" }), { target: { value: "100" } });
    expect(screen.getByTestId("volumetric-slice-volume-status")).toHaveTextContent("低值必须小于高值");
    expect(screen.getByTestId("volumetric-slice-volume-status")).not.toHaveClass("sr-only");
  });

  it("shows a typed volume fallback without creating a canvas when WebGL2 is unavailable", async () => {
    const { container } = render(<VolumetricSliceVolumeSurface artifacts={artifacts} mode="volume" capabilityOverride="unsupported" byteLoader={byteLoader} sliceWorkerFactory={sliceWorker} />);
    await waitFor(() => expect(screen.getByTestId("volumetric-slice-volume-state")).toHaveTextContent("不支持"));
    expect(screen.queryByRole("checkbox", { name: "结构" })).not.toBeInTheDocument();
    expect(screen.getByTestId("volumetric-slice-volume-status")).toHaveTextContent("仍可查看切片和等值面");
    expect(container.querySelector("canvas, iframe, script")).toBeNull();
    expect(screen.getByTestId("volumetric-volume-metrics")).toHaveTextContent("宽=nz，高=ny，深=nx");
  });

  it("keeps context loss visible after a successful volume render without structural data", async () => {
    const engine = { ...mockSliceEngine(), setTransferFunction: vi.fn(), setQuality: vi.fn(), setClipping: vi.fn(), setProjection: vi.fn(), snapshot: vi.fn(() => ({})) };
    renderer.volume.mockResolvedValue({ engine, capabilities: { webgl2: true } });
    render(<VolumetricSliceVolumeSurface artifacts={artifacts} mode="volume" byteLoader={byteLoader} capabilityOverride="supported" />);
    await waitFor(() => expect(screen.getByTestId("volumetric-slice-volume-state")).toHaveTextContent("已就绪"));
    expect(screen.queryByRole("checkbox", { name: "结构" })).not.toBeInTheDocument();
    expect(screen.getByTestId("volumetric-slice-volume-status")).toHaveClass("sr-only");
    act(() => renderer.volume.mock.lastCall![0].onContextLost());
    await waitFor(() => expect(screen.getByTestId("volumetric-slice-volume-status")).toHaveTextContent("体渲染显示中断"));
    expect(screen.getByTestId("volumetric-slice-volume-status")).not.toHaveClass("sr-only");
    expect(screen.getByRole("button", { name: "下载图片" })).toBeDisabled();
  });
});
