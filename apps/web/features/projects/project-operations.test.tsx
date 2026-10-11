import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { useProjectOperation, validateProject, validateProjectBatch, validateProjectDirectory } from "./project-operations";
import type { ProjectSummary } from "../../app/lib/planner-api";
const project = { id: "p", projectId: "p", name: "材料项目" } as ProjectSummary;
beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

it("bounds waiting, rejects duplicate submission, and requires rereading uncertain writes", async () => {
  const view = renderHook(() => useProjectOperation());
  const accept = vi.fn(), request = vi.fn(() => new Promise<ProjectSummary>(() => {}));
  let pending!: Promise<boolean>;
  act(() => { pending = view.result.current.run("保存项目", request, accept); });
  await act(async () => { expect(await view.result.current.run("保存项目", request, accept)).toBe(false); await vi.advanceTimersByTimeAsync(10_001); await pending; });
  expect(request).toHaveBeenCalledOnce(); expect(accept).not.toHaveBeenCalled();
  expect(view.result.current).toMatchObject({ pending: false, uncertain: true });
  await act(async () => expect(await view.result.current.run("保存项目", request, accept)).toBe(false));
  act(() => view.result.current.reconciled());
  await act(async () => expect(await view.result.current.run("保存项目", async () => project, accept)).toBe(true));
  expect(accept).toHaveBeenCalledWith(project);
});

it("ignores a canceled dialog's late save even after rereading and opening a new dialog", async () => {
  let resolve!: (value: ProjectSummary) => void;
  const view = renderHook(() => useProjectOperation()), stale = vi.fn(), next = vi.fn();
  let pending!: Promise<boolean>;
  await act(async () => { pending = view.result.current.run("保存项目", () => new Promise((done) => { resolve = done; }), stale); });
  await act(async () => { view.result.current.dismiss(); await pending; });
  expect(view.result.current.uncertain).toBe(true);
  act(() => view.result.current.reconciled());
  await act(async () => view.result.current.run("保存项目", async () => project, next));
  await act(async () => resolve({ ...project, name: "迟到" }));
  expect(stale).not.toHaveBeenCalled(); expect(next).toHaveBeenCalledOnce();
});

it("does not turn a confirmed save into an uncertain operation when its dialog closes", async () => {
  const view = renderHook(() => useProjectOperation());
  await act(async () => view.result.current.run("保存项目", async () => project, () => view.result.current.dismiss()));
  expect(view.result.current).toMatchObject({ pending: false, uncertain: false });
});

it("cancels an in-flight read on unmount and never downloads a late export", async () => {
  let signal!: AbortSignal, resolve!: (value: ProjectSummary) => void;
  const view = renderHook(() => useProjectOperation()), accept = vi.fn();
  await act(async () => { void view.result.current.run("导出项目清单", (s) => { signal = s; return new Promise((done) => { resolve = done; }); }, accept, true); });
  view.unmount(); expect(signal.aborted).toBe(true);
  await act(async () => resolve(project)); expect(accept).not.toHaveBeenCalled();
});

it.each([403, 409, 422])("reports a confirmed rejection %i without requiring reconciliation", async (status) => {
  const view = renderHook(() => useProjectOperation());
  await act(async () => view.result.current.run("保存项目", async () => { throw { status }; }, vi.fn()));
  expect(view.result.current.uncertain).toBe(false); expect(view.result.current.error).toContain("未完成");
});

it("allows retrying failed exports without treating reads as uncertain writes", async () => {
  const view = renderHook(() => useProjectOperation());
  await act(async () => view.result.current.run("导出项目清单", async () => { throw new Error("offline"); }, vi.fn(), true));
  expect(view.result.current.uncertain).toBe(false);
  await act(async () => expect(await view.result.current.run("导出项目清单", async () => project, vi.fn(), true)).toBe(true));
});

it("does not hide local export failures after a successful read", async () => {
  const view = renderHook(() => useProjectOperation());
  await act(async () => view.result.current.run("导出项目清单", async () => project, () => { throw new Error("download unavailable"); }, true));
  expect(view.result.current.error).toContain("暂时无法完成");
});

it("rejects foreign or malformed project identities", () => {
  for (const value of [null, { ...project, id: "other" }, { ...project, projectId: "other" }, { ...project, name: "" }]) {
    expect(() => validateProject(value as ProjectSummary, "p")).toThrow();
  }
  expect(() => validateProjectDirectory([project, project])).toThrow();
  expect(validateProjectDirectory([])).toEqual([]);
});

it("validates every requested batch identity and action before clearing selection", () => {
  for (const value of [{ action: "restore", count: 1, projectIds: ["p"] }, { action: "archive", count: 1, projectIds: ["other"] }, { action: "archive", count: 2, projectIds: ["p", "p"] }]) {
    expect(() => validateProjectBatch(value, "archive", ["p"])).toThrow();
  }
  expect(validateProjectBatch({ action: "archive", count: 1, projectIds: ["p"] }, "archive", ["p"]).count).toBe(1);
});

it("does not report a saved edit or lifecycle change from an unchanged response", () => {
  const unchanged = { ...project, status: "active", pinned: false, description: "原说明" };
  for (const expected of [{ name: "新名称" }, { description: "新说明" }, { archived: true }, { lifecycle: "TRASHED" }, { pinned: true }]) {
    expect(() => validateProject(unchanged, "p", expected)).toThrow("not confirmed");
  }
});
