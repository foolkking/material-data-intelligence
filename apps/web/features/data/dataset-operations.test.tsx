import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { useDatasetOperation, readDatasetDirectory, updateDatasetBatches, validateDataset, validateDatasetHistory } from "./dataset-operations";
import type { DatasetDetail, ProjectHistory } from "../../app/lib/planner-api";
const api = vi.hoisted(() => ({ getProjectHistory: vi.fn(), bulkDatasetAction: vi.fn() }));
vi.mock("../../app/lib/planner-api", () => api);
const dataset = { id: "d", datasetId: "d", projectId: "p", name: "材料数据", status: "profile_ready" };
const history = { project: { id: "p" }, datasets: [{ datasetId: "d", name: "材料数据", status: "profile_ready" }] } as ProjectHistory;
beforeEach(() => { vi.useFakeTimers(); vi.resetAllMocks(); api.getProjectHistory.mockResolvedValue(history); api.bulkDatasetAction.mockImplementation(async (ids: string[], action: string) => ({ datasetIds: ids, action, count: ids.length })); });
afterEach(() => vi.useRealTimers());

it("bounds a write and permits another only after a successful fresh directory read", async () => {
  const view = renderHook(() => useDatasetOperation("p")); const request = vi.fn(() => new Promise(() => {})), accept = vi.fn();
  let pending!: Promise<boolean>;
  act(() => { pending = view.result.current.run("重命名数据集", request, accept); });
  await act(async () => { expect(await view.result.current.run("再次保存", request, accept)).toBe(false); await vi.advanceTimersByTimeAsync(10001); await pending; });
  expect(request).toHaveBeenCalledOnce(); expect(accept).not.toHaveBeenCalled(); expect(view.result.current.uncertain).toBe(true);
  api.getProjectHistory.mockRejectedValueOnce(new Error("offline"));
  await act(async () => { expect(await view.result.current.reconcile(accept)).toBe(false); });
  expect(view.result.current.uncertain).toBe(true);
  await act(async () => { expect(await view.result.current.run("再次保存", request, accept)).toBe(false); expect(await view.result.current.reconcile(accept)).toBe(true); });
  expect(api.getProjectHistory).toHaveBeenCalledWith("p", { forceRefresh: true, signal: expect.any(AbortSignal) });
  await act(async () => { expect(await view.result.current.run("保存", async () => dataset, accept)).toBe(true); });
});
it("does not let a closed editor's late result affect the next editor", async () => {
  let done!: (value: DatasetDetail) => void; const accept = vi.fn(), view = renderHook(() => useDatasetOperation("p"));
  let pending!: Promise<boolean>;
  await act(async () => { pending = view.result.current.run("保存", () => new Promise((resolve) => { done = resolve; }), accept); });
  await act(async () => { view.result.current.dismiss(); await pending; });
  expect(view.result.current.uncertain).toBe(true);
  await act(async () => { await view.result.current.reconcile(vi.fn()); done(dataset); });
  expect(accept).not.toHaveBeenCalled(); expect(view.result.current.pending).toBe(false);
});
it("ignores writes and rereads after navigation to another project", async () => {
  let done!: (value: DatasetDetail) => void; const accept = vi.fn(), view = renderHook(({ id }) => useDatasetOperation(id), { initialProps: { id: "p" } });
  await act(async () => { void view.result.current.run("保存", () => new Promise((resolve) => { done = resolve; }), accept); });
  view.rerender({ id: "other" }); await act(async () => done(dataset));
  expect(accept).not.toHaveBeenCalled(); expect(view.result.current.uncertain).toBe(false);
});
it("rejects a foreign directory without releasing the write lock", async () => {
  const view = renderHook(() => useDatasetOperation("p"));
  await act(async () => { await view.result.current.run("保存", async () => { throw new Error("lost reply"); }, vi.fn()); });
  api.getProjectHistory.mockResolvedValue({ ...history, project: { id: "other" } });
  await act(async () => { expect(await view.result.current.reconcile(vi.fn())).toBe(false); });
  expect(view.result.current.uncertain).toBe(true);
});
it("bounds stalled directory reads and preserves the unresolved operation", async () => {
  const view = renderHook(() => useDatasetOperation("p"));
  await act(async () => { await view.result.current.run("保存", async () => { throw new Error("lost reply"); }, vi.fn()); });
  api.getProjectHistory.mockReturnValue(new Promise(() => {})); let pending!: Promise<boolean>;
  act(() => { pending = view.result.current.reconcile(vi.fn()); });
  await act(async () => { await vi.advanceTimersByTimeAsync(10001); await pending; });
  expect(view.result.current).toMatchObject({ reading: false, uncertain: true });
});
it.each([403, 409, 422])("keeps a rejected %i operation retryable", async (status) => {
  const view = renderHook(() => useDatasetOperation("p"));
  await act(async () => { await view.result.current.run("保存", async () => { throw { status }; }, vi.fn()); });
  expect(view.result.current.uncertain).toBe(false); expect(view.result.current.error).toContain("未完成");
});
it("does not mark a confirmed write uncertain when its success callback closes the dialog", async () => {
  const view = renderHook(() => useDatasetOperation("p"));
  await act(async () => { await view.result.current.run("保存", async () => dataset, view.result.current.dismiss); });
  expect(view.result.current.uncertain).toBe(false);
});
it("validates exact datasets, changed names and lifecycle before applying the response", () => {
  for (const value of [null, { ...dataset, id: "other" }, { ...dataset, datasetId: "other" }, { ...dataset, projectId: "other" }, { ...dataset, name: "" }]) expect(() => validateDataset(value as DatasetDetail, "p", "d", {})).toThrow();
  expect(() => validateDataset(dataset, "p", "d", { name: "new" })).toThrow();
  expect(() => validateDataset(dataset, "p", "d", { archived: true })).toThrow();
  expect(() => validateDatasetHistory({ ...history, datasets: [history.datasets[0], history.datasets[0]] }, "p")).toThrow();
  expect(validateDataset(dataset, "p", "d", { archived: false })).toEqual({ name: dataset.name, status: "profile_ready" });
  expect(validateDataset({ ...dataset, status: "archived" }, "p", "d", { archived: false }, "trashed").status).toBe("archived");
});
it("sends at most 100 datasets and retains acknowledged chunks when a later chunk fails", async () => {
  const ids = Array.from({ length: 205 }, (_, i) => `d${i}`), accept = vi.fn();
  api.bulkDatasetAction.mockResolvedValueOnce({ action: "archive", datasetIds: ids.slice(0, 100), count: 100 }).mockRejectedValueOnce(new Error("second chunk failed"));
  await expect(updateDatasetBatches(ids, "archive", new AbortController().signal, accept)).rejects.toThrow();
  expect(accept).toHaveBeenCalledOnce(); expect(accept).toHaveBeenCalledWith(ids.slice(0, 100)); expect(api.bulkDatasetAction.mock.calls.map((call) => call[0].length)).toEqual([100, 100]);
  api.bulkDatasetAction.mockClear(); await updateDatasetBatches(ids.slice(100), "archive", new AbortController().signal, accept);
  expect(api.bulkDatasetAction.mock.calls.map((call) => call[0].length)).toEqual([100, 5]);
});
it("does not apply mismatched or canceled batch responses", async () => {
  const accept = vi.fn(), controller = new AbortController();
  api.bulkDatasetAction.mockResolvedValueOnce({ action: "trash", datasetIds: ["wrong"], count: 1 });
  await expect(updateDatasetBatches(["d"], "trash", controller.signal, accept)).rejects.toThrow();
  api.bulkDatasetAction.mockImplementationOnce(async () => { controller.abort(); return { action: "trash", datasetIds: ["d"], count: 1 }; });
  await expect(updateDatasetBatches(["d"], "trash", controller.signal, accept)).rejects.toThrow();
  expect(accept).not.toHaveBeenCalled();
});

it("reads every dataset page before reconciling an uncertain change", async () => {
  api.getProjectHistory.mockResolvedValueOnce({ ...history, pagination: { datasets: { nextCursor: "next" } } })
    .mockResolvedValueOnce({ ...history, datasets: [{ datasetId: "later", name: "后续数据", status: "archived" }], pagination: { datasets: { nextCursor: null } } });
  const result = await readDatasetDirectory("p", new AbortController().signal);
  expect(result.datasets.map((item) => item.datasetId)).toEqual(["d", "later"]);
  expect(api.getProjectHistory).toHaveBeenLastCalledWith("p", { forceRefresh: true, datasetsCursor: "next", signal: expect.any(AbortSignal) });
});
it("rejects repeated cursors without publishing an incomplete directory", async () => {
  api.getProjectHistory.mockResolvedValue({ ...history, pagination: { datasets: { nextCursor: "next" } } });
  await expect(readDatasetDirectory("p", new AbortController().signal)).rejects.toThrow("cursor mismatch");
  expect(api.getProjectHistory).toHaveBeenCalledTimes(2);
});
