import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { useScientificObjectOperation, validateManagedObject, validateManagedObjectBatch } from "./scientific-object-operations";
import type { ScientificObjectSummary } from "../../app/lib/scientific-viewer-api";
const api = vi.hoisted(() => ({ bulkUpdateScientificObjects: vi.fn(), getScientificObjectSummary: vi.fn(), updateScientificObject: vi.fn() }));
vi.mock("../../app/lib/scientific-viewer-api", () => api);
const item = (id = "one", lifecycle = "ACTIVE"): ScientificObjectSummary => ({ id, project_id: "p", display_name: id, lifecycle_status: lifecycle, kind: "scientific_object", object_type: "materials.dataset", current_version_id: "v" });
beforeEach(() => { vi.useFakeTimers(); vi.resetAllMocks(); api.getScientificObjectSummary.mockImplementation(async (id) => item(id)); api.updateScientificObject.mockImplementation(async (id, changes) => item(id, changes.lifecycle)); api.bulkUpdateScientificObjects.mockImplementation(async (project_id, ids: string[], lifecycle) => ({ project_id, lifecycle, count: ids.length, items: ids.map((id) => item(id, lifecycle)) })); });
afterEach(() => vi.useRealTimers());

it("bounds a stalled update and shares its lock with every caller until exact state is reread", async () => {
  const view = renderHook(() => useScientificObjectOperation("p"));
  api.updateScientificObject.mockReturnValueOnce(new Promise(() => {})); let pending!: Promise<boolean>;
  act(() => { pending = view.result.current.update(["one"], "ARCHIVED", "viewer"); });
  await act(async () => { expect(await view.result.current.update(["one"], "ARCHIVED", "directory")).toBe(false); await vi.advanceTimersByTimeAsync(10001); await pending; });
  expect(view.result.current).toMatchObject({ pending: false, uncertain: true, targets: ["one"] });
  api.getScientificObjectSummary.mockRejectedValueOnce(new Error("offline"));
  await act(async () => { expect(await view.result.current.recheck("viewer")).toBe(false); });
  expect(view.result.current.uncertain).toBe(true);
  await act(async () => { expect(await view.result.current.update(["other"], "ARCHIVED", "directory")).toBe(false); expect(await view.result.current.recheck("viewer")).toBe(true); });
  await act(async () => { expect(await view.result.current.update(["one"], "ARCHIVED", "directory")).toBe(true); });
  expect(view.result.current.known.one.lifecycle_status).toBe("ARCHIVED"); expect(api.updateScientificObject).toHaveBeenCalledTimes(2);
});
it("cancels only the owning surface and ignores its late response", async () => {
  let done!: (value: ScientificObjectSummary) => void; const view = renderHook(() => useScientificObjectOperation("p"));
  api.updateScientificObject.mockImplementationOnce(() => new Promise((resolve) => { done = resolve; })); let pending!: Promise<boolean>;
  await act(async () => { pending = view.result.current.update(["one"], "ARCHIVED", "viewer"); });
  act(() => view.result.current.dismiss("directory")); expect(view.result.current.pending).toBe(true);
  await act(async () => { view.result.current.dismiss("viewer"); await pending; done(item("one", "ARCHIVED")); });
  expect(view.result.current.known.one).toBeUndefined(); expect(view.result.current.uncertain).toBe(true);
});
it("does not publish old writes after changing projects", async () => {
  let done!: (value: ScientificObjectSummary) => void; const view = renderHook(({ project }) => useScientificObjectOperation(project), { initialProps: { project: "p" } });
  api.updateScientificObject.mockImplementationOnce(() => new Promise((resolve) => { done = resolve; }));
  await act(async () => { void view.result.current.update(["one"], "ARCHIVED", "directory"); });
  view.rerender({ project: "next" }); await act(async () => done(item("one", "ARCHIVED")));
  expect(view.result.current.known).toEqual({}); expect(view.result.current.uncertain).toBe(false);
});
it("retains successful batches and reconciles only the attempted uncertain chunk", async () => {
  const ids = Array.from({ length: 205 }, (_, index) => `id-${index}`), view = renderHook(() => useScientificObjectOperation("p"));
  api.bulkUpdateScientificObjects.mockImplementationOnce(async (project_id, chunk: string[], lifecycle) => ({ project_id, lifecycle, count: chunk.length, items: chunk.map((id) => item(id, lifecycle)) })).mockRejectedValueOnce(new Error("lost response"));
  await act(async () => { expect(await view.result.current.update(ids, "TRASHED", "directory", true)).toBe(false); });
  expect(Object.keys(view.result.current.known)).toEqual(ids.slice(0, 100)); expect(view.result.current.targets).toEqual(ids.slice(100, 200));
  expect(api.bulkUpdateScientificObjects.mock.calls.map((args) => args[1].length)).toEqual([100, 100]);
  await act(async () => { await view.result.current.recheck("directory"); });
  expect(api.getScientificObjectSummary).toHaveBeenCalledTimes(100);
  await act(async () => { expect(await view.result.current.update(ids.slice(100), "TRASHED", "directory", true)).toBe(true); });
  expect(api.bulkUpdateScientificObjects.mock.calls.slice(2).map((args) => args[1].length)).toEqual([100, 5]);
});
it("retries only failed state reads and keeps successes", async () => {
  const view = renderHook(() => useScientificObjectOperation("p"));
  api.bulkUpdateScientificObjects.mockRejectedValueOnce(new Error("unknown"));
  await act(async () => { await view.result.current.update(["one", "two"], "ARCHIVED", "directory", true); });
  api.getScientificObjectSummary.mockImplementationOnce(async () => item("one", "ARCHIVED")).mockRejectedValueOnce(new Error("offline"));
  await act(async () => { await view.result.current.recheck("directory"); });
  expect(view.result.current.known.one.lifecycle_status).toBe("ARCHIVED"); expect(view.result.current.targets).toEqual(["two"]);
  await act(async () => { await view.result.current.recheck("directory"); });
  expect(api.getScientificObjectSummary.mock.calls.map((args) => args[0])).toEqual(["one", "two", "two"]);
});
it("bounds stalled state reads and ignores a mismatched object", async () => {
  const view = renderHook(() => useScientificObjectOperation("p"));
  api.updateScientificObject.mockRejectedValueOnce(new Error("unknown"));
  await act(async () => { await view.result.current.update(["one"], "ARCHIVED", "viewer"); });
  api.getScientificObjectSummary.mockReturnValueOnce(new Promise(() => {})); let pending!: Promise<boolean>;
  act(() => { pending = view.result.current.recheck("viewer"); });
  await act(async () => { await vi.advanceTimersByTimeAsync(10001); await pending; });
  expect(view.result.current).toMatchObject({ reading: false, uncertain: true });
  api.getScientificObjectSummary.mockResolvedValueOnce(item("other"));
  await act(async () => { await view.result.current.recheck("viewer"); });
  expect(view.result.current.known).toEqual({}); expect(view.result.current.uncertain).toBe(true);
});
it.each([403, 409, 422])("makes an explicit rejection %i retryable", async (status) => {
  const view = renderHook(() => useScientificObjectOperation("p")); api.updateScientificObject.mockRejectedValueOnce({ status });
  await act(async () => { await view.result.current.update(["one"], "ARCHIVED", "viewer"); });
  expect(view.result.current.uncertain).toBe(false); expect(view.result.current.error).toContain("修改未完成");
});
it("rejects wrong project, object, lifecycle and batch membership before publishing", () => {
  expect(() => validateManagedObject({ ...item(), project_id: "foreign" }, "p", "one")).toThrow();
  expect(() => validateManagedObject(item("other"), "p", "one")).toThrow();
  expect(() => validateManagedObject(item(), "p", "one", "ARCHIVED")).toThrow();
  expect(() => validateManagedObjectBatch({ project_id: "p", lifecycle: "ARCHIVED", count: 2, items: [item("one", "ARCHIVED"), item("one", "ARCHIVED")] }, "p", ["one", "two"], "ARCHIVED")).toThrow();
});
