import "@testing-library/jest-dom/vitest";
import { createHash } from "node:crypto";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import fixture from "../../../../tests/fixtures/volumetric_contract/cubic_constant_scalar.json";
import spinFixture from "../../../../tests/fixtures/volumetric_contract/collinear_spin_dataset.json";
import { VolumetricIsosurfaceSurface } from "./VolumetricIsosurfaceSurface";
import type { Artifact } from "../../app/lib/planner-api";

const renderer = vi.hoisted(() => ({ create: vi.fn() }));
const extraction = vi.hoisted(() => vi.fn());
vi.mock("./volumetricRendererEngine", () => ({ createVolumetricRendererEngine: renderer.create }));
vi.mock("./isosurfaceWorkerClient", () => ({ IsosurfaceWorkerClient: class {
  async extract(request: { layers: {layerId: string}[]; computePotentialProfiles?: boolean }) { extraction(request); return { meshes: request.layers.map(layer => ({ ...layer, meshHash: "test-mesh" })), metrics: {vertices: 3, triangles: 1, extractionMs: 1}, potentialProfiles: request.computePotentialProfiles ? { sourceValues: Array.from({length: 3}, () => [2, 2, 2, 2]), calculationMs: 1 } : undefined }; }
  cancel() {}
  dispose() {}
} }));

const artifacts = [
  { id: "dataset", type: "volumetric_dataset_json", content: fixture.raw_dataset },
  { id: "manifest", type: "volumetric_manifest_json", content: fixture.manifest },
  { id: "binary", jobId: "job", type: "volumetric_binary", name: "cubic-constant.f64" },
] as never;
const byteLoader = async () => new Float64Array(64).fill(2).buffer;
const engine = () => Object.fromEntries([
  "setSurfaceVisible", "setLayerVisible", "setStructureVisible", "setCellVisible", "setOpacity", "setProjection",
  "setClipping", "setSelection", "setProfilePlane", "resetCamera", "fitSurface", "dispose", "exportPng",
].map(name => [name, vi.fn()]));

beforeEach(() => {
  renderer.create.mockReset();
  extraction.mockReset();
  vi.stubGlobal("Worker", class {});
  vi.stubGlobal("crypto", { subtle: { digest: async (_algorithm: string, value: BufferSource) => {
    const bytes = new Uint8Array(value instanceof ArrayBuffer ? value : value.buffer, value instanceof ArrayBuffer ? 0 : value.byteOffset, value.byteLength);
    const digest = createHash("sha256").update(bytes).digest();
    return digest.buffer.slice(digest.byteOffset, digest.byteOffset + digest.byteLength);
  } } });
});
afterEach(() => vi.unstubAllGlobals());

it("waits for the selected field's payload before rendering its geometry", async () => {
  renderer.create.mockImplementation(async () => engine());
  const source = [
    {id:"spin-dataset",type:"volumetric_dataset_json",content:{...spinFixture.dataset,relationships:[]}},
    {id:"spin-manifest",type:"volumetric_manifest_json",content:{...fixture.manifest,dataset_id:spinFixture.dataset.dataset_id,dataset_content_hash:spinFixture.dataset.content_hash}},
  ] as Artifact[];
  render(<VolumetricIsosurfaceSurface artifacts={source}/>);
  await waitFor(() => expect(renderer.create).toHaveBeenCalledOnce());
  const original = crypto.subtle.digest.bind(crypto.subtle);
  let finish: (()=>void) | undefined;
  vi.spyOn(crypto.subtle,"digest").mockImplementationOnce(async (algorithm,bytes) => {
    const value = await original(algorithm,bytes);
    return new Promise<ArrayBuffer>(resolve => { finish=()=>resolve(value); });
  });
  const total=spinFixture.dataset.fields.find(field=>field.field_name==="total")!;
  fireEvent.change(screen.getByTestId("volumetric-field-selector"),{target:{value:total.field_id}});
  await waitFor(() => expect(finish).toBeDefined());
  expect(renderer.create).toHaveBeenCalledOnce();
  expect(screen.getByRole("button",{name:"重置视角"})).toBeDisabled();
  await act(async()=>{finish!();});
  await waitFor(() => expect(renderer.create).toHaveBeenCalledTimes(2));
});

it("keeps signed thresholds opposite across edits and switches presets with the selected field", async () => {
  renderer.create.mockImplementation(async () => engine());
  const spinArtifacts = [
    {id:"spin-dataset",type:"volumetric_dataset_json",content:{...spinFixture.dataset,relationships:[]}},
    {id:"spin-manifest",type:"volumetric_manifest_json",content:{...fixture.manifest,dataset_id:spinFixture.dataset.dataset_id,dataset_content_hash:spinFixture.dataset.content_hash}},
  ] as Artifact[];
  render(<VolumetricIsosurfaceSurface artifacts={spinArtifacts}/>);
  await waitFor(() => expect(screen.getByRole("button",{name:"重置视角"})).toBeEnabled());
  fireEvent.change(screen.getByRole("spinbutton",{name:"等值面 1 的等值"}),{target:{value:"-0.5"}});
  expect(screen.getByRole("spinbutton",{name:"等值面 2 的等值"})).toHaveValue(0.5);
  fireEvent.click(screen.getByRole("checkbox",{name:"正负等值同步"}));
  fireEvent.change(screen.getByRole("spinbutton",{name:"等值面 2 的等值"}),{target:{value:"0.8"}});
  expect(screen.getByRole("spinbutton",{name:"等值面 1 的等值"})).toHaveValue(-0.5);
  fireEvent.click(screen.getByRole("checkbox",{name:"正负等值同步"}));
  expect(screen.getByRole("spinbutton",{name:"等值面 2 的等值"})).toHaveValue(0.5);
  const total=spinFixture.dataset.fields.find(field=>field.field_name==="total")!;
  fireEvent.change(screen.getByTestId("volumetric-field-selector"),{target:{value:total.field_id}});
  expect(screen.queryByRole("checkbox",{name:"正负等值同步"})).not.toBeInTheDocument();
  const preset=Number((total.statistics.stored_components[0].maximum*0.25).toPrecision(6));
  fireEvent.click(screen.getByRole("group",{name:"等值预设"}).querySelectorAll("button")[1]);
  expect(screen.getByRole("spinbutton",{name:"等值面 1 的等值"})).toHaveValue(preset);
  expect(screen.queryByTestId("charge-spin-mode")).not.toBeInTheDocument();
});

it("does not start extraction when a replaced source finishes its final hash check late", async () => {
  const digest = crypto.subtle.digest.bind(crypto.subtle);
  let finishHash: (() => void) | undefined;
  let reads = 0;
  vi.spyOn(crypto.subtle, "digest").mockImplementation(async (algorithm, bytes) => {
    const result = await digest(algorithm, bytes);
    if (++reads === 2) return new Promise<ArrayBuffer>(resolve => { finishHash = () => resolve(result); });
    return result;
  });
  renderer.create.mockImplementation(async () => engine());
  const view = render(<VolumetricIsosurfaceSurface artifacts={artifacts} byteLoader={byteLoader} />);
  await waitFor(() => expect(finishHash).toBeDefined());
  view.rerender(<VolumetricIsosurfaceSurface artifacts={(artifacts as Artifact[]).map(artifact => ({ ...artifact, id: `replacement-${artifact.id}` }))} byteLoader={byteLoader} />);
  await waitFor(() => expect(renderer.create).toHaveBeenCalledOnce());
  await act(async () => { finishHash!(); });
  expect(extraction).toHaveBeenCalledOnce();
  expect(screen.getByRole("button", {name: "重置视角"})).toBeEnabled();
});

it("applies the latest display controls after async initialization and mesh replacement", async () => {
  let finish!: () => void;
  let current = engine();
  renderer.create.mockImplementation(() => new Promise(resolve => { const owned = current; finish = () => resolve(owned); }));
  render(<VolumetricIsosurfaceSurface artifacts={artifacts} byteLoader={byteLoader} />);
  await waitFor(() => expect(renderer.create).toHaveBeenCalledOnce());
  fireEvent.click(screen.getByRole("checkbox", {name: "表面", exact: true}));
  fireEvent.click(screen.getByRole("checkbox", {name: "显示等值面 1"}));
  fireEvent.click(screen.getByRole("checkbox", {name: "裁剪", exact: true}));
  fireEvent.change(screen.getByRole("slider", {name: "不透明度"}), {target: {value: "0.4"}});
  finish();
  await waitFor(() => expect(screen.getByRole("button", {name: "重置视角"})).toBeEnabled());
  await waitFor(() => {
    expect(current.setSurfaceVisible).toHaveBeenLastCalledWith(false);
    expect(current.setLayerVisible).toHaveBeenLastCalledWith("surface-1", false);
    expect(current.setClipping).toHaveBeenLastCalledWith(true, 2, 0);
    expect(current.setOpacity).toHaveBeenLastCalledWith(0.4);
  });
  const previous = current;
  current = engine();
  fireEvent.change(screen.getByRole("spinbutton", {name: "等值面 1 的等值"}), {target: {value: "2.1"}});
  await waitFor(() => expect(renderer.create).toHaveBeenCalledTimes(2));
  finish();
  await waitFor(() => expect(current.setLayerVisible).toHaveBeenLastCalledWith("surface-1", false));
  expect(current.setSurfaceVisible).toHaveBeenLastCalledWith(false);
  expect(current.setClipping).toHaveBeenLastCalledWith(true, 2, 0);
  expect(previous.dispose).toHaveBeenCalled();
});

it("keeps export failure visible while retaining the rendered surface", async () => {
  const current = engine();
  current.exportPng.mockRejectedValue(new Error("test export failure"));
  renderer.create.mockResolvedValue(current);
  render(<VolumetricIsosurfaceSurface artifacts={artifacts} byteLoader={byteLoader} />);
  await waitFor(() => expect(screen.getByRole("button", {name: "下载图片"})).toBeEnabled());
  fireEvent.click(screen.getByRole("button", {name: "下载图片"}));
  await waitFor(() => expect(screen.getByTestId("volumetric-renderer-status")).toHaveTextContent("图片导出"));
  expect(screen.getByTestId("volumetric-renderer-status")).not.toHaveClass("sr-only");
  expect(screen.getByRole("button", {name: "重置视角"})).toBeEnabled();
});

it("keeps one selected target, exposes exact source details on demand and restores focus after clearing", async () => {
  const current = engine(); renderer.create.mockResolvedValue(current);
  render(<VolumetricIsosurfaceSurface artifacts={artifacts} byteLoader={byteLoader} />);
  await waitFor(() => expect(screen.getByRole("button", {name:"重置视角"})).toBeEnabled());
  const callbacks = renderer.create.mock.calls[0][0];
  const pick = { fieldId: "field-exact", layerId: "surface-1", isovalue: 2, triangleIndex: 17,
    cartesianPosition: [1.123456789, 2, 3], meshHash: "a".repeat(64), interpolatedFieldValue: 2 };
  act(() => callbacks.onSurfacePick(pick));
  const inspector = screen.getByTestId("volumetric-surface-inspector");
  expect(inspector).toHaveTextContent("等值面 1");
  const details = inspector.querySelector("details")!;
  expect(details.open).toBe(false);
  fireEvent.click(screen.getByText("精确数值与来源"));
  expect(details).toHaveTextContent("1.123456789, 2, 3");
  expect(details).toHaveTextContent(pick.meshHash);
  act(() => callbacks.onAtomPick(4));
  expect(screen.queryByTestId("volumetric-surface-inspector")).not.toBeInTheDocument();
  expect(screen.getByTestId("volumetric-atom-inspector")).toHaveTextContent("结构位点 4");
  fireEvent.click(screen.getByRole("button", {name:"清除选择",exact:true}));
  expect(screen.queryByTestId("volumetric-atom-inspector")).not.toBeInTheDocument();
  const host = screen.getByTestId("volumetric-renderer-canvas-host");
  expect(host).toHaveFocus();
  act(() => callbacks.onSurfacePick(pick));
  expect(host).toHaveFocus(); fireEvent.keyDown(host, {key:"Escape"});
  expect(screen.queryByTestId("volumetric-surface-inspector")).not.toBeInTheDocument();
  expect(current.setSelection).toHaveBeenLastCalledWith(null);
});

it("clears a selected surface when geometry changes and ignores callbacks from the disposed renderer", async () => {
  renderer.create.mockImplementation(async () => engine());
  render(<VolumetricIsosurfaceSurface artifacts={artifacts} byteLoader={byteLoader} />);
  await waitFor(() => expect(screen.getByRole("button", {name:"重置视角"})).toBeEnabled());
  const old = renderer.create.mock.calls[0][0];
  const pick = { fieldId:"old-field", layerId:"surface-1", isovalue:2, triangleIndex:1, cartesianPosition:[1,2,3], meshHash:"old", interpolatedFieldValue:2 };
  act(() => old.onSurfacePick(pick));
  fireEvent.change(screen.getByRole("spinbutton", {name:"等值面 1 的等值"}), {target:{value:"2.1"}});
  await waitFor(() => expect(renderer.create).toHaveBeenCalledTimes(2));
  expect(screen.queryByTestId("volumetric-surface-inspector")).not.toBeInTheDocument();
  act(() => old.onSurfacePick(pick));
  expect(screen.queryByTestId("volumetric-surface-inspector")).not.toBeInTheDocument();
});

it("retains layer visibility when a replacement renderer resolves immediately", async () => {
  let current = engine();
  renderer.create.mockImplementation(async () => current);
  render(<VolumetricIsosurfaceSurface artifacts={artifacts} byteLoader={byteLoader} />);
  await waitFor(() => expect(screen.getByRole("button", {name: "重置视角"})).toBeEnabled());
  fireEvent.click(screen.getByRole("checkbox", {name: "显示等值面 1"}));
  expect(current.setLayerVisible).toHaveBeenLastCalledWith("surface-1", false);
  current = engine();
  fireEvent.change(screen.getByRole("spinbutton", {name: "等值面 1 的等值"}), {target: {value: "2.1"}});
  await waitFor(() => expect(renderer.create).toHaveBeenCalledTimes(2));
  await waitFor(() => expect(current.setLayerVisible).toHaveBeenLastCalledWith("surface-1", false));
});

it("returns keyboard focus to a surviving isovalue after removing a layer", async () => {
  renderer.create.mockImplementation(async () => engine());
  render(<VolumetricIsosurfaceSurface artifacts={artifacts} byteLoader={byteLoader} />);
  await waitFor(() => expect(screen.getByRole("button", {name: "重置视角"})).toBeEnabled());
  fireEvent.click(screen.getByRole("button", {name: "添加等值面"}));
  const remove = screen.getByRole("button", {name: "移除等值面 2"});
  remove.focus();
  fireEvent.click(remove);
  expect(screen.getByRole("spinbutton", {name: "等值面 1 的等值"})).toHaveFocus();
});

it("keeps layer identities distinct when adding after removing the first layer", async () => {
  renderer.create.mockImplementation(async () => engine());
  render(<VolumetricIsosurfaceSurface artifacts={artifacts} byteLoader={byteLoader} />);
  await waitFor(() => expect(screen.getByRole("button", {name: "重置视角"})).toBeEnabled());
  fireEvent.click(screen.getByRole("button", {name: "添加等值面"}));
  fireEvent.click(screen.getByRole("button", {name: "移除等值面 1"}));
  fireEvent.click(screen.getByRole("button", {name: "添加等值面"}));
  await waitFor(() => {
    const meshes = renderer.create.mock.lastCall?.[0].meshes;
    expect(meshes).toHaveLength(2);
    expect(new Set(meshes.map((mesh: {layerId: string}) => mesh.layerId)).size).toBe(2);
  });
});

it("links exact profile selection to the matching 3D axis and retains it across display zero changes", async () => {
  const dataset = structuredClone(fixture.raw_dataset);
  Object.assign(dataset.fields[0], {
    quantity: "local_potential",
    unit: { ...dataset.fields[0].unit, source_unit: "electronvolt", canonical_unit: "electronvolt" },
    potential_reference: { kind: "source_defined", reference_value: 0, reference_unit: "electronvolt", shift_applied: false, shift_amount: 0, source_metadata: "Constant potential fixture" },
  });
  const potentialArtifacts = [
    { id: "dataset", type: "volumetric_dataset_json", content: dataset },
    { id: "manifest", type: "volumetric_manifest_json", content: fixture.manifest },
    { id: "binary", type: "volumetric_binary", name: "cubic-constant.f64" },
  ] as Artifact[];
  const current = engine();
  renderer.create.mockResolvedValue(current);
  const view = render(<VolumetricIsosurfaceSurface artifacts={artifacts} byteLoader={byteLoader} />);
  await waitFor(() => expect(screen.getByRole("button", {name: "重置视角"})).toBeEnabled());
  view.rerender(<VolumetricIsosurfaceSurface artifacts={potentialArtifacts.map(artifact => ({ ...artifact, id: `new-${artifact.id}` }))} byteLoader={byteLoader} />);
  await screen.findByRole("region", {name: "静电势分析"});
  await waitFor(() => expect(screen.getByRole("button", {name: "放大剖面"})).toBeEnabled());
  fireEvent.change(screen.getByRole("combobox", {name: "剖面方向"}), { target: { value: "lattice_axis_1" } });
  fireEvent.keyDown(screen.getByTestId("potential-profile-chart"), { key: "End" });
  await waitFor(() => expect(current.setProfilePlane).toHaveBeenLastCalledWith(1, 3));
  fireEvent.change(screen.getByRole("combobox", {name: "显示零点"}), { target: { value: "cell_average_zero" } });
  expect(screen.getByTestId("potential-profile-selection")).toHaveTextContent("平面 3");
  expect(screen.getByTestId("potential-profile-selection")).toHaveTextContent("源值 2 eV · 显示值 0 eV");
  expect(current.setProfilePlane).toHaveBeenLastCalledWith(1, 3);
});
