import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, afterEach, expect, it, vi } from "vitest";
import { ResearchMaterialPicker } from "./ResearchMaterialPicker";
import { admitResearchMaterial, type ResearchMaterials } from "./research-materials";

const api = vi.hoisted(() => ({ getDatasetResearchSources: vi.fn(), getResearchSourceVersion: vi.fn(), admitDatasetResource: vi.fn(), promoteDatasetTable: vi.fn() }));
vi.mock("../../app/lib/planner-api", () => api);
const source = (datasetId = "si", name = "Si.cif") => ({ datasetId, objectId: `resource-${datasetId}`, objectType: "Structure", objectHash: "a".repeat(64), displayName: name });
const admitted = (datasetId = "si", name = "Si.cif") => ({
  object: { id: `object-${datasetId}`, project_id: "p", object_type: "structure.crystal", display_name: name, current_version_id: "newer-version" },
  version: { id: `exact-${datasetId}`, scientific_object_id: `object-${datasetId}`, semantic_hash: "a".repeat(64), source_resource_refs_json: [{ project_id: "p", dataset_id: datasetId, resource_id: `resource-${datasetId}` }] },
});
const datasets = [{ datasetId: "si", name: "Silicon", status: "profile_ready" }, { datasetId: "cu", name: "Copper", status: "profile_ready" }];
const initial: ResearchMaterials = { items: [], selections: [] };
beforeEach(() => {
  vi.resetAllMocks();
  api.getDatasetResearchSources.mockImplementation(async d => ({ projectId: "p", datasetId: d, resources: [source(d, d === "si" ? "Si.cif" : "Cu.cif")] }));
  api.admitDatasetResource.mockImplementation(async (_p, d, _r, name) => admitted(d, name));
  api.getResearchSourceVersion.mockImplementation(async (objectId, versionId) => ({ id: versionId, scientific_object_id: objectId, object_type: "trajectory.atomic", source_resource_refs_json: [] }));
});
afterEach(() => vi.useRealTimers());
function setup(loadInitial = async () => initial) {
  const onApply = vi.fn(), onClose = vi.fn();
  const view = render(<ResearchMaterialPicker projectId="p" datasets={datasets} loadInitial={loadInitial} onApply={onApply} onClose={onClose} returnFocus={null} />);
  return { ...view, onApply, onClose };
}
it("selects two independent datasets and applies the returned exact versions without following current_version", async () => {
  const view = setup();
  fireEvent.click(await screen.findByRole("checkbox", { name: /Si.cif/ }));
  await screen.findByRole("button", { name: "使用所选材料（1）" });
  fireEvent.change(screen.getByLabelText("数据集"), { target: { value: "cu" } });
  fireEvent.click(await screen.findByRole("checkbox", { name: /Cu.cif/ }));
  const apply = await screen.findByRole("button", { name: "使用所选材料（2）" });
  fireEvent.click(apply);
  expect(view.onApply.mock.calls[0][0].items.map((x: any) => [x.datasetId, x.ref.version_id])).toEqual([["si", "exact-si"], ["cu", "exact-cu"]]);
  expect(api.admitDatasetResource).toHaveBeenCalledTimes(2);
});
it("cancel keeps the original selection unchanged even when an admission finishes late", async () => {
  let finish!: (value: unknown) => void;
  api.admitDatasetResource.mockReturnValue(new Promise(resolve => { finish = resolve; }));
  const view = setup();
  fireEvent.click(await screen.findByRole("checkbox", { name: /Si.cif/ }));
  fireEvent.click(screen.getByRole("button", { name: "取消" }));
  view.unmount();
  await act(async () => finish(admitted()));
  expect(view.onClose).toHaveBeenCalledOnce(); expect(view.onApply).not.toHaveBeenCalled();
  expect(initial).toEqual({ items: [], selections: [] });
});
it("preserves exact scientific point selections only while their material remains selected", async () => {
  const ref = { object_id: "o", version_id: "v", project_id: "p", object_type: "trajectory.atomic", display_name: "AIMD.xyz" };
  const value: ResearchMaterials = { items: [{ ref }], selections: [{ contract_version: "1.0", object_ref: ref, viewer_id: "scientific.trajectory", selection_type: "TRAJECTORY_FRAME", semantic_locator: { frame_index: 5 }, display_label: "帧 6" }] };
  const view = setup(async () => value);
  fireEvent.click(await screen.findByRole("checkbox", { name: /Si.cif/ }));
  fireEvent.click(await screen.findByRole("button", { name: "使用所选材料（2）" }));
  expect(view.onApply.mock.calls[0][0].selections).toEqual(value.selections);
  fireEvent.click(screen.getByRole("button", { name: "移除 AIMD.xyz" }));
  fireEvent.click(screen.getByRole("button", { name: "使用所选材料（1）" }));
  expect(view.onApply.mock.calls[1][0].selections).toEqual([]);
  expect(value.items).toHaveLength(1); expect(value.selections).toHaveLength(1);
});
it("marks inherited exact sources as checked without readmitting or duplicating them", async () => {
  const response = admitted();
  api.getResearchSourceVersion.mockResolvedValue({ ...response.version, object_type: response.object.object_type });
  const value: ResearchMaterials = { items: [{ ref: { project_id: "p", object_id: "object-si", version_id: "exact-si", object_type: "structure.crystal", display_name: "Si.cif" } }], selections: [] };
  setup(async () => value);
  const choice = await screen.findByRole("checkbox", { name: /Si.cif/ });
  expect(choice).toBeChecked(); expect(api.admitDatasetResource).not.toHaveBeenCalled();
  fireEvent.click(choice);
  expect(screen.getByRole("button", { name: "使用所选材料" })).toBeDisabled();
});
it("ignores a previous dataset's late catalog and exposes retry after a catalog failure", async () => {
  let finish!: (value: unknown) => void;
  api.getDatasetResearchSources.mockReturnValueOnce(new Promise(resolve => { finish = resolve; })).mockRejectedValueOnce(new Error("network"));
  setup();
  fireEvent.change(await screen.findByLabelText("数据集"), { target: { value: "cu" } });
  await screen.findByRole("button", { name: "重新读取材料列表" });
  await act(async () => finish({ projectId: "p", datasetId: "si", resources: [source()] }));
  expect(screen.queryByRole("checkbox", { name: /Si.cif/ })).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "重新读取材料列表" }));
  await screen.findByRole("checkbox", { name: /Cu.cif/ });
});
it("shows a bounded failure for a stalled version read, retaining other selections", async () => {
  setup(); await screen.findByRole("checkbox", { name: /Si.cif/ });
  vi.useFakeTimers();
  api.admitDatasetResource.mockReturnValue(new Promise(() => {}));
  fireEvent.click(screen.getByRole("checkbox", { name: /Si.cif/ }));
  await act(async () => { await vi.advanceTimersByTimeAsync(10_001); });
  expect(screen.getByRole("alert")).toHaveTextContent("暂时无法取得此材料的版本");
  expect(screen.getByRole("checkbox")).toBeEnabled();
});
it.each(["hash", "project", "source", "version", "type"])("rejects mismatched %s before adding the source", async problem => {
  const value = admitted();
  if (problem === "hash") value.version.semantic_hash = "b".repeat(64);
  if (problem === "project") value.object.project_id = "other";
  if (problem === "source") value.version.source_resource_refs_json[0].dataset_id = "other";
  if (problem === "version") value.version.scientific_object_id = "other";
  if (problem === "type") value.object.object_type = "materials.table";
  api.admitDatasetResource.mockResolvedValue(value);
  await expect(admitResearchMaterial("p", source(), new AbortController().signal)).rejects.toThrow("来源或版本已变化");
});
