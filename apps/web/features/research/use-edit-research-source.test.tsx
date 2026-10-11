import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useEditResearchSource } from "./use-edit-research-source";
import { Agent2ReadError, type Agent2TurnDetail, type Agent2ResearchTurnResult } from "../../app/lib/agent2-research-api";
import { readBranchTurn, readBranchResult } from "./branch-source";
const api = vi.hoisted(() => ({ getAgent2ResearchTurn: vi.fn(), getAgent2ResearchTurnResult: vi.fn() }));
vi.mock("../../app/lib/agent2-research-api", async (original) => ({ ...await original<typeof import("../../app/lib/agent2-research-api")>(), ...api }));
const ref = { object_id: "o", version_id: "v", project_id: "p", object_type: "structure.crystal" };
const turn = { turn_id: "t", project_id: "p", research_session_id: "s", user_message: { content: "原问题" }, context: { scope: [ref], selection: [], scientific_selection: [] } } as unknown as Agent2TurnDetail;
const result = { research_turn_id: "t", result_id: "r", result_snapshot_id: "snapshot", source_object_refs: [ref], scientific_selections: [] } as unknown as Agent2ResearchTurnResult;
const flush = () => act(async () => {});
beforeEach(() => { vi.useFakeTimers(); vi.resetAllMocks(); api.getAgent2ResearchTurn.mockResolvedValue(turn); api.getAgent2ResearchTurnResult.mockResolvedValue(result); });
afterEach(() => vi.useRealTimers());

describe("edit source recovery", () => {
  it("retains the original question and retries only a failed result read", async () => {
    api.getAgent2ResearchTurnResult.mockRejectedValueOnce(new Agent2ReadError(503)).mockResolvedValue(result);
    const view = renderHook(() => useEditResearchSource("p", "s", "t")); await flush();
    expect(view.result.current).toMatchObject({ turn, result: null, loadState: "error" });
    await act(async () => view.result.current.retry());
    expect(view.result.current).toMatchObject({ turn, result, loadState: "ready" });
    expect(api.getAgent2ResearchTurn).toHaveBeenCalledOnce(); expect(api.getAgent2ResearchTurnResult).toHaveBeenCalledTimes(2);
  });
  it.each(["turn", "result"])("bounds a stalled %s and ignores its late response after recovery", async (part) => {
    let finish!: (value: unknown) => void;
    const request = part === "turn" ? api.getAgent2ResearchTurn : api.getAgent2ResearchTurnResult;
    request.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
    const view = renderHook(() => useEditResearchSource("p", "s", "t"));
    await act(async () => { await vi.advanceTimersByTimeAsync(10_001); });
    expect(view.result.current).toMatchObject({ pending: false, loadState: "error" });
    expect(request.mock.calls[0][1].signal.aborted).toBe(true);
    await act(async () => view.result.current.retry());
    expect(view.result.current).toMatchObject({ turn, result, loadState: "ready" });
    await act(async () => finish(part === "turn" ? { ...turn, turn_id: "late" } : { ...result, result_id: "late" }));
    expect(view.result.current).toMatchObject({ turn, result, loadState: "ready" });
  });
  it("permits a confirmed missing result while retaining the original scientific context", async () => {
    api.getAgent2ResearchTurnResult.mockRejectedValue(new Agent2ReadError(404));
    const view = renderHook(() => useEditResearchSource("p", "s", "t")); await flush();
    expect(view.result.current).toMatchObject({ turn, result: null, loadState: "ready" });
  });
  it.each(["ANSWERED", "NEEDS_CLARIFICATION", "UNSUPPORTED", "PLAN_REJECTED"])("restores %s input when the real result API reports no scientific snapshot", async status => {
    const source = { ...turn, status };
    api.getAgent2ResearchTurn.mockResolvedValue(source);
    api.getAgent2ResearchTurnResult.mockRejectedValue(new Agent2ReadError(409, "SCIENTIFIC_RESULT_NOT_READY"));
    const view = renderHook(() => useEditResearchSource("p", "s", "t")); await flush();
    expect(view.result.current).toMatchObject({ turn: source, result: null, loadState: "ready" });
    expect(view.result.current.turn?.context?.scope).toEqual([ref]);
  });
  it.each(["RUNNING", "RESULT_PENDING", "COMPLETED", "FAILED", "CANCELED"])("does not treat an unready %s scientific result as an empty context", async status => {
    api.getAgent2ResearchTurn.mockResolvedValue({ ...turn, status });
    api.getAgent2ResearchTurnResult.mockRejectedValue(new Agent2ReadError(409, "SCIENTIFIC_RESULT_NOT_READY"));
    await expect(readBranchResult("p", "t", new AbortController().signal)).rejects.toThrow("暂时无法确认");
  });
  it.each([new Agent2ReadError(403), new Agent2ReadError(503), new Agent2ReadError(409), new Agent2ReadError(409, "RESULT_PROJECTION_FAILED")])("preserves an unknown result read failure despite a conversational status", async error => {
    api.getAgent2ResearchTurn.mockResolvedValue({ ...turn, status: "ANSWERED" });
    api.getAgent2ResearchTurnResult.mockRejectedValue(error);
    await expect(readBranchResult("p", "t", new AbortController().signal)).rejects.toThrow("暂时无法确认");
    expect(api.getAgent2ResearchTurn).not.toHaveBeenCalled();
  });
  it("rejects a mismatched source while confirming that no scientific result is expected", async () => {
    api.getAgent2ResearchTurn.mockResolvedValue({ ...turn, status: "ANSWERED", project_id: "foreign" });
    api.getAgent2ResearchTurnResult.mockRejectedValue(new Agent2ReadError(409, "SCIENTIFIC_RESULT_NOT_READY"));
    await expect(readBranchResult("p", "t", new AbortController().signal)).rejects.toThrow("暂时无法确认");
  });
  it("cancels old reads and never exposes another session's source", async () => {
    let finish!: (value: unknown) => void;
    api.getAgent2ResearchTurn.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }))
      .mockResolvedValueOnce({ ...turn, research_session_id: "new" });
    const view = renderHook(({ session }) => useEditResearchSource("p", session, "t"), { initialProps: { session: "s" } });
    view.rerender({ session: "new" }); await flush();
    expect(api.getAgent2ResearchTurn.mock.calls[0][1].signal.aborted).toBe(true);
    await act(async () => finish(turn));
    expect(view.result.current.turn?.research_session_id).toBe("new");
  });
  it.each([{ turn_id: "wrong" }, { project_id: "wrong" }, { research_session_id: "wrong" }, { context: { ...turn.context, scope: [{ ...ref, project_id: "wrong" }] } }])("rejects foreign or malformed original input %j", async (patch) => {
    api.getAgent2ResearchTurn.mockResolvedValue({ ...turn, ...patch });
    await expect(readBranchTurn("p", "s", "t", new AbortController().signal)).rejects.toThrow("暂时无法确认");
  });
  it.each([null, { ...result, research_turn_id: "wrong" }, { ...result, source_object_refs: [{ ...ref, project_id: "wrong" }] }])("does not silently discard unknown or foreign results", async (value) => {
    api.getAgent2ResearchTurnResult.mockResolvedValue(value);
    await expect(readBranchResult("p", "t", new AbortController().signal)).rejects.toThrow("暂时无法确认");
  });
});
