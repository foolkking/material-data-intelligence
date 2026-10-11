import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { projectCreationDraftKey, useProjectCreation } from "./use-project-creation";
const api = vi.hoisted(() => ({ getAuthUser: vi.fn(), createProject: vi.fn(), updateProject: vi.fn(), listProjects: vi.fn() }));
vi.mock("../../app/lib/planner-api", async (original) => ({ ...await original<typeof import("../../app/lib/planner-api")>(), createProject: api.createProject, updateProject: api.updateProject, listProjects: api.listProjects }));
vi.mock("../../app/lib/product-api", async (original) => ({ ...await original<typeof import("../../app/lib/product-api")>(), getAuthUser: api.getAuthUser }));
const project = { id: "p", projectId: "p", name: "结构研究", description: "", status: "active", role: "owner" };
const flush = () => act(async () => {});
beforeEach(() => {
  vi.useFakeTimers(); vi.resetAllMocks(); sessionStorage.clear();
  api.getAuthUser.mockResolvedValue({ id: "user" }); api.createProject.mockResolvedValue(project);
  api.updateProject.mockImplementation(async (id, change) => ({ ...project, id, projectId: id, ...change })); api.listProjects.mockResolvedValue([]);
});
afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks(); });
async function setup(description = "") {
  const accepted = vi.fn(); const view = renderHook(() => useProjectCreation(accepted)); await flush();
  act(() => { view.result.current.setName("结构研究"); view.result.current.setDescription(description); });
  return { view, accepted };
}

it("publishes creation before a stalled description and retries only that exact project's description", async () => {
  const { view, accepted } = await setup("材料体系说明");
  api.updateProject.mockReturnValueOnce(new Promise(() => {}));
  let pending!: Promise<void>; await act(async () => { pending = view.result.current.submit(); });
  expect(view.result.current.project?.id).toBe("p"); expect(accepted).toHaveBeenCalledWith(project);
  await act(async () => { await vi.advanceTimersByTimeAsync(10_001); await pending; });
  expect(view.result.current).toMatchObject({ mode: "created", needsRead: true, description: "材料体系说明", busy: null });
  api.listProjects.mockResolvedValue([project]); await act(async () => view.result.current.recheck());
  await act(async () => view.result.current.saveDescription());
  expect(api.createProject).toHaveBeenCalledOnce();
  expect(api.updateProject).toHaveBeenCalledTimes(2);
  expect(view.result.current).toMatchObject({ descriptionSaved: true, needsRead: false });
});

it("does not send a second create until a fresh directory read permits retrying the original name", async () => {
  const { view } = await setup(); api.createProject.mockRejectedValueOnce(new Error("network"));
  await act(async () => view.result.current.submit());
  act(() => view.result.current.setName("不可替换原名称"));
  await act(async () => view.result.current.submit()); expect(api.createProject).toHaveBeenCalledOnce();
  await act(async () => view.result.current.recheck());
  expect(view.result.current.retryAllowed).toBe(true);
  await act(async () => view.result.current.submit());
  expect(api.createProject.mock.calls.map((call) => call[0])).toEqual(["结构研究", "结构研究"]);
});

it("does not treat a same-name project as created or write its description without an explicit choice", async () => {
  const { view } = await setup("新的说明"); api.createProject.mockRejectedValueOnce(new Error("network"));
  await act(async () => view.result.current.submit()); api.listProjects.mockResolvedValue([project]);
  await act(async () => view.result.current.recheck());
  expect(view.result.current.project).toBeNull(); expect(view.result.current.matches).toEqual([project]);
  expect(api.updateProject).not.toHaveBeenCalled();
  act(() => view.result.current.useExisting("p"));
  expect(view.result.current.origin).toBe("matched"); expect(api.updateProject).not.toHaveBeenCalled();
  await act(async () => view.result.current.saveDescription());
  expect(api.updateProject).toHaveBeenCalledWith("p", { description: "新的说明" }, expect.any(AbortSignal));
});

it("does not erase an existing description when the creation draft has no optional description", async () => {
  const { view } = await setup(); api.createProject.mockRejectedValueOnce(new Error("network"));
  await act(async () => view.result.current.submit()); api.listProjects.mockResolvedValue([{ ...project, description: "已有说明" }]);
  await act(async () => view.result.current.recheck()); act(() => view.result.current.useExisting("p"));
  expect(view.result.current.descriptionSaved).toBe(true); expect(api.updateProject).not.toHaveBeenCalled();
});

it("preserves uncertain creation across unmount and ignores late responses and follow-on description writes", async () => {
  let resolve!: (value: unknown) => void;
  const { view, accepted } = await setup("保留说明"); api.createProject.mockReturnValueOnce(new Promise((done) => { resolve = done; }));
  await act(async () => { void view.result.current.submit(); }); view.unmount();
  await act(async () => resolve(project)); expect(accepted).not.toHaveBeenCalled(); expect(api.updateProject).not.toHaveBeenCalled();
  const restored = renderHook(() => useProjectCreation(vi.fn())); await flush();
  expect(restored.result.current).toMatchObject({ name: "结构研究", description: "保留说明", mode: "unconfirmed", needsRead: true, retryAllowed: false });
});

it("restores a known created identity and reconciles a previously saved description without another write", async () => {
  const { view } = await setup("说明"); api.updateProject.mockRejectedValueOnce(new Error("network"));
  await act(async () => view.result.current.submit()); view.unmount();
  const restored = renderHook(() => useProjectCreation(vi.fn())); await flush();
  expect(restored.result.current.project?.id).toBe("p"); expect(restored.result.current.needsRead).toBe(true);
  api.listProjects.mockResolvedValue([{ ...project, description: "说明" }]);
  await act(async () => restored.result.current.recheck());
  expect(restored.result.current.descriptionSaved).toBe(true); expect(api.createProject).toHaveBeenCalledOnce(); expect(api.updateProject).toHaveBeenCalledOnce();
});

it("does not expose another account's stored creation draft", async () => {
  const { view } = await setup("账户一说明"); view.unmount(); api.getAuthUser.mockResolvedValue({ id: "other" });
  const other = renderHook(() => useProjectCreation(vi.fn())); await flush();
  expect(other.result.current).toMatchObject({ name: "", description: "", mode: "draft" });
});

it("cancels creation and clears visible content on session expiration", async () => {
  const { view, accepted } = await setup("私人草稿"); let resolve!: (value: unknown) => void;
  api.createProject.mockReturnValueOnce(new Promise((done) => { resolve = done; }));
  await act(async () => { void view.result.current.submit(); });
  act(() => window.dispatchEvent(new Event("mdi:session-expired")));
  await act(async () => resolve(project));
  expect(view.result.current).toMatchObject({ ready: false, name: "", matches: [] }); expect(accepted).not.toHaveBeenCalled(); expect(api.updateProject).not.toHaveBeenCalled();
});

it("bounds account recovery and a stalled directory without enabling another create", async () => {
  api.getAuthUser.mockReturnValueOnce(new Promise(() => {}));
  const view = renderHook(() => useProjectCreation(vi.fn()));
  await act(async () => vi.advanceTimersByTimeAsync(10_001)); expect(view.result.current.authError).toBe(true);
  await act(async () => view.result.current.retryAuth()); expect(view.result.current.ready).toBe(true);
  act(() => view.result.current.setName("结构研究")); api.createProject.mockRejectedValue(new Error("network"));
  await act(async () => view.result.current.submit()); api.listProjects.mockReturnValueOnce(new Promise(() => {}));
  let pending!: Promise<void>; act(() => { pending = view.result.current.recheck(); });
  await act(async () => { await vi.advanceTimersByTimeAsync(10_001); await pending; });
  expect(view.result.current.retryAllowed).toBe(false); expect(view.result.current.error).toContain("暂时无法核对");
});

it.each([{ id: "", name: "结构研究" }, { ...project, projectId: "wrong" }, { ...project, name: "其他项目" }])("rejects a malformed or mismatched creation response", async (value) => {
  const { view, accepted } = await setup("说明"); api.createProject.mockResolvedValue(value);
  await act(async () => view.result.current.submit());
  expect(view.result.current.mode).toBe("unconfirmed"); expect(accepted).not.toHaveBeenCalled(); expect(api.updateProject).not.toHaveBeenCalled();
});

it("blocks read-only existing projects from description writes", async () => {
  const { view } = await setup("说明"); api.createProject.mockRejectedValueOnce(new Error("network"));
  await act(async () => view.result.current.submit()); api.listProjects.mockResolvedValue([{ ...project, role: "viewer" }]);
  await act(async () => view.result.current.recheck()); act(() => view.result.current.useExisting("p"));
  await act(async () => view.result.current.saveDescription()); expect(api.updateProject).not.toHaveBeenCalled();
});

it("clears a completed draft when its dialog is dismissed", async () => {
  const { view } = await setup(); await act(async () => view.result.current.submit());
  act(() => view.result.current.dismiss());
  expect(sessionStorage.getItem(projectCreationDraftKey("user"))).toBeNull();
});
