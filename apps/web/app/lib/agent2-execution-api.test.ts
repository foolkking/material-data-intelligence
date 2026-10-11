import { afterEach, describe, expect, it, vi } from "vitest";
import { cancelAgent2Execution, getAgent2ExecutionProgress } from "./agent2-execution-api";
import { dispatchAgent2ResearchTurn } from "./agent2-research-api";

afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });
const operations = [getAgent2ExecutionProgress, cancelAgent2Execution, dispatchAgent2ResearchTurn];
const progress = { turn_id: "turn-exact", status: "RUNNING", steps: [], warnings: [], incremental_outputs: [] };

describe("bounded exact-turn execution requests", () => {
  it.each(operations)("bounds stalled transport and aborts it: %s", async (operation) => {
    vi.useFakeTimers();
    const fetcher = vi.fn(() => new Promise<Response>(() => {}));
    vi.stubGlobal("fetch", fetcher);
    const result = operation("turn-exact").catch((error) => error);
    await vi.advanceTimersByTimeAsync(10_000);
    expect(await result).toMatchObject({ name: "Agent2ExecutionRequestError", uncertain: operation !== getAgent2ExecutionProgress });
    expect((fetcher.mock.calls[0] as unknown as [string, RequestInit])[1].signal?.aborted).toBe(true);
    expect(vi.getTimerCount()).toBe(0);
  });
  it.each(operations)("bounds stalled response bodies: %s", async (operation) => {
    vi.useFakeTimers();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: () => new Promise(() => {}) }));
    const result = operation("turn-exact").catch((error) => error);
    await vi.advanceTimersByTimeAsync(10_000);
    expect(await result).toHaveProperty("name", "Agent2ExecutionRequestError");
  });
  it.each(operations)("honors parent cancellation even when fetch ignores it: %s", async (operation) => {
    vi.useFakeTimers();
    vi.stubGlobal("fetch", vi.fn(() => new Promise(() => {})));
    const parent = new AbortController();
    const result = operation("turn-exact", { signal: parent.signal }).catch((error) => error);
    parent.abort();
    expect(await result).toHaveProperty("name", "AbortError");
    expect(vi.getTimerCount()).toBe(0);
  });
  it.each(operations)("rejects another Turn's valid response: %s", async (operation) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...progress, turn_id: "other", queued: true }))));
    await expect(operation("turn-exact")).rejects.toThrow("不匹配");
  });
  it("rejects malformed progress and dispatch results", async () => {
    const fetcher = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ ...progress, steps: null })))
      .mockResolvedValueOnce(new Response(JSON.stringify(progress)));
    vi.stubGlobal("fetch", fetcher);
    await expect(getAgent2ExecutionProgress("turn-exact")).rejects.toThrow("内容");
    await expect(dispatchAgent2ResearchTurn("turn-exact")).rejects.toThrow("尚未确认");
  });
  it.each([
    ["HISTORICAL_ANALYSIS_PLAN_PAYLOAD_UNAVAILABLE"],
    [null],
    [{ code: null, message: "历史记录提示" }],
    [{ code: "HISTORICAL_ANALYSIS_PLAN_PAYLOAD_UNAVAILABLE", message: {} }],
  ])("rejects unreadable warning entries before they can crash the progress view: %j", async warning => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json({ ...progress, status: "FAILED", warnings: [warning] })));
    await expect(getAgent2ExecutionProgress("turn-exact")).rejects.toThrow("内容");
  });
  it.each([getAgent2ExecutionProgress, cancelAgent2Execution])("notifies shared authentication expiry: %s", async (operation) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("private server detail", { status: 401 })));
    const expired = vi.fn();
    window.addEventListener("mdi:session-expired", expired);
    try {
      await expect(operation("turn-exact")).rejects.toMatchObject({ status: 401, uncertain: false });
      expect(expired).toHaveBeenCalledOnce();
    } finally { window.removeEventListener("mdi:session-expired", expired); }
  });
  it("keeps mutation uncertainty on network loss without exposing transport details", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("private transport detail")));
    await expect(cancelAgent2Execution("turn-exact")).rejects.toMatchObject({ uncertain: true, message: "取消结果尚未确认，请重新读取研究状态。" });
  });
});
