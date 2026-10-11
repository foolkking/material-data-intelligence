import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useSessionMemory } from "./use-session-memory";
import type { Agent2SessionMemory } from "../../app/lib/agent2-memory-api";

const api = vi.hoisted(() => ({ getAgent2SessionMemory: vi.fn(), pinAgent2Result: vi.fn(), unpinAgent2Result: vi.fn(), pinAgent2Object: vi.fn(), unpinAgent2Object: vi.fn() }));
vi.mock("../../app/lib/agent2-memory-api", async (original) => ({ ...await original<typeof import("../../app/lib/agent2-memory-api")>(), ...api }));
const empty: Agent2SessionMemory = { project_id: "p", session_id: "s", version: 1, pinned_object_refs: [], pinned_result_refs: [], session_constraints: [] };
const source = { project_id: "p", object_id: "o", version_id: "v", object_type: "structure.crystal" };
const other = { ...source, version_id: "v2" };
const flush = () => act(async () => {});
function deferred<T>() { let resolve!: (value: T) => void; const promise = new Promise<T>((done) => { resolve = done; }); return { promise, resolve }; }
beforeEach(() => { vi.useFakeTimers(); vi.resetAllMocks(); api.getAgent2SessionMemory.mockResolvedValue(empty); });
afterEach(() => vi.useRealTimers());

describe("shared session context", () => {
  it("bounds an unread context, retries locally and never treats failure as empty", async () => {
    const stalled = deferred<Agent2SessionMemory>();
    api.getAgent2SessionMemory.mockReturnValueOnce(stalled.promise);
    const { result } = renderHook(() => useSessionMemory("p", "s", true));
    await act(async () => { await vi.advanceTimersByTimeAsync(10_001); });
    expect(result.current).toMatchObject({ reading: false, memory: null, canUpdate: false, needsRefresh: true });
    await act(async () => result.current.refresh());
    expect(result.current).toMatchObject({ canUpdate: true, memory: empty, error: "" });
    await act(async () => stalled.resolve({ ...empty, version: 9, pinned_result_refs: ["late"] }));
    expect(result.current.memory).toEqual(empty);
  });

  it("retains confirmed content when a refresh fails and rejects older versions", async () => {
    const saved = { ...empty, version: 3, pinned_result_refs: ["r"] };
    api.getAgent2SessionMemory.mockResolvedValueOnce(saved).mockRejectedValueOnce(new Error("offline")).mockResolvedValueOnce(empty).mockResolvedValue(saved);
    const { result } = renderHook(() => useSessionMemory("p", "s", true)); await flush();
    await act(async () => result.current.refresh());
    expect(result.current).toMatchObject({ memory: saved, canUpdate: false, needsRefresh: true });
    await act(async () => result.current.refresh());
    expect(result.current).toMatchObject({ memory: saved, canUpdate: false });
    await act(async () => result.current.refresh()); expect(result.current.canUpdate).toBe(true);
  });

  it("reconciles an uncertain pin before permitting another write", async () => {
    api.pinAgent2Result.mockReturnValue(new Promise(() => {}));
    const saved = { ...empty, version: 2, pinned_result_refs: ["r"] };
    const { result } = renderHook(() => useSessionMemory("p", "s", true)); await flush();
    act(() => { void result.current.setResultPinned("r", true); void result.current.setResultPinned("r", true); });
    expect(api.pinAgent2Result).toHaveBeenCalledOnce();
    await act(async () => { await vi.advanceTimersByTimeAsync(10_001); });
    expect(result.current).toMatchObject({ updating: false, needsRefresh: true, canUpdate: false, memory: empty });
    await act(async () => result.current.setResultPinned("r", true)); expect(api.pinAgent2Result).toHaveBeenCalledOnce();
    api.getAgent2SessionMemory.mockResolvedValue(saved);
    await act(async () => result.current.refresh());
    expect(result.current).toMatchObject({ needsRefresh: false, canUpdate: true, memory: saved });
    await act(async () => result.current.setResultPinned("r", true)); expect(api.pinAgent2Result).toHaveBeenCalledOnce();
    api.unpinAgent2Result.mockResolvedValue({ ...empty, version: 3 });
    await act(async () => result.current.setResultPinned("r", false)); expect(result.current.memory?.pinned_result_refs).toEqual([]);
  });

  it("keeps confirmed sources after partial failure and retries only unfinished versions", async () => {
    const partial = { ...empty, version: 2, pinned_object_refs: [source] };
    const complete = { ...empty, version: 3, pinned_object_refs: [source, other] };
    api.pinAgent2Object.mockResolvedValueOnce(partial).mockRejectedValueOnce(new Error("network")) .mockResolvedValueOnce(complete);
    const { result } = renderHook(() => useSessionMemory("p", "s", true)); await flush();
    await act(async () => result.current.setSourcesPinned([source, source, other], true));
    expect(result.current).toMatchObject({ memory: partial, needsRefresh: true });
    api.getAgent2SessionMemory.mockResolvedValue(partial);
    await act(async () => result.current.refresh());
    await act(async () => result.current.setSourcesPinned([source, other], true));
    expect(api.pinAgent2Object.mock.calls.map((call) => call[2].version_id)).toEqual(["v", "v2", "v2"]);
    expect(result.current.memory).toEqual(complete);
  });

  it.each([
    { ...empty, project_id: "foreign", pinned_result_refs: ["r"] },
    { ...empty, session_id: "foreign", pinned_result_refs: ["r"] },
    { ...empty, version: 0, pinned_result_refs: ["r"] },
    { ...empty, version: 2 },
  ])("rejects mismatched or unconfirmed mutation responses without losing saved content", async (response) => {
    api.pinAgent2Result.mockResolvedValue(response);
    const { result } = renderHook(() => useSessionMemory("p", "s", true)); await flush();
    await act(async () => result.current.setResultPinned("r", true));
    expect(result.current).toMatchObject({ memory: empty, needsRefresh: true, canUpdate: false });
  });

  it("allows retry after a definitive rejection while preserving confirmed content", async () => {
    api.pinAgent2Result.mockRejectedValueOnce(Object.assign(new Error("forbidden"), { status: 403 }))
      .mockResolvedValueOnce({ ...empty, version: 2, pinned_result_refs: ["r"] });
    const { result } = renderHook(() => useSessionMemory("p", "s", true)); await flush();
    await act(async () => result.current.setResultPinned("r", true));
    expect(result.current).toMatchObject({ memory: empty, needsRefresh: false, canUpdate: true });
    await act(async () => result.current.setResultPinned("r", true)); expect(result.current.memory?.pinned_result_refs).toEqual(["r"]);
  });

  it("aborts old-session work and ignores its late response", async () => {
    const old = deferred<Agent2SessionMemory>(); api.pinAgent2Result.mockReturnValue(old.promise);
    api.getAgent2SessionMemory.mockImplementation(async (p, s) => ({ ...empty, project_id: p, session_id: s }));
    const { result, rerender } = renderHook(({ session }) => useSessionMemory("p", session, true), { initialProps: { session: "s" } }); await flush();
    act(() => { void result.current.setResultPinned("r", true); });
    const previous = result.current;
    const signal = api.pinAgent2Result.mock.calls[0][3].signal;
    rerender({ session: "new" }); await flush();
    expect(signal.aborted).toBe(true);
    await act(async () => old.resolve({ ...empty, version: 2, pinned_result_refs: ["r"] }));
    expect(result.current).toMatchObject({ updating: false, error: "", memory: { session_id: "new", pinned_result_refs: [] } });
    await act(async () => { await previous.setResultPinned("another", true); await previous.refresh(); });
    expect(api.pinAgent2Result).toHaveBeenCalledOnce();
    expect(api.getAgent2SessionMemory).toHaveBeenCalledTimes(2);
  });

  it("guards permissions at invocation and rejects foreign sources before any write", async () => {
    const { result, rerender } = renderHook(({ allowed }) => useSessionMemory("p", "s", allowed), { initialProps: { allowed: true } }); await flush();
    const previous = result.current;
    rerender({ allowed: false });
    await act(async () => previous.setResultPinned("r", true)); expect(api.pinAgent2Result).not.toHaveBeenCalled();
    rerender({ allowed: true });
    await act(async () => result.current.setSourcesPinned([source, { ...other, project_id: "foreign" }], true));
    expect(api.pinAgent2Object).not.toHaveBeenCalled();
  });
});
