import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { Agent2ExecutionRequestError, type Agent2ProgressView } from "../../app/lib/agent2-execution-api";
import { watchAgent2Execution } from "./execution-recovery";

const api = vi.hoisted(() => ({ read: vi.fn(), cancel: vi.fn(), dispatch: vi.fn() }));
vi.mock("../../app/lib/agent2-execution-api", async (original) => ({
  ...await original<typeof import("../../app/lib/agent2-execution-api")>(),
  getAgent2ExecutionProgress: api.read, cancelAgent2Execution: api.cancel,
}));
vi.mock("../../app/lib/agent2-research-api", () => ({ dispatchAgent2ResearchTurn: api.dispatch }));
const progress = (status: Agent2ProgressView["status"], turn_id = "exact"): Agent2ProgressView => ({
  contract_version: "1.0", turn_id, status, steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 1,
  warnings: [], incremental_outputs: [], result_projection_pending: false,
});
const deferred = <T,>() => { let resolve!: (value: T) => void; let reject!: (reason: unknown) => void; const promise = new Promise<T>((a, b) => { resolve = a; reject = b; }); return { promise, resolve, reject }; };
let watcher: ReturnType<typeof watchAgent2Execution>;
let callbacks: { progress: ReturnType<typeof vi.fn>; recovery: ReturnType<typeof vi.fn>; cancellation: ReturnType<typeof vi.fn>; dispatch: ReturnType<typeof vi.fn> };
const flush = () => vi.advanceTimersByTimeAsync(0);
beforeEach(() => {
  vi.useFakeTimers(); vi.resetAllMocks();
  callbacks = { progress: vi.fn(), recovery: vi.fn(), cancellation: vi.fn(), dispatch: vi.fn() };
  api.read.mockResolvedValue(progress("RUNNING"));
  api.cancel.mockResolvedValue({ turn_id: "exact", status: "CANCELING" });
  api.dispatch.mockResolvedValue({ turn_id: "exact", status: "QUEUED", queued: true });
});
afterEach(() => { watcher?.dispose(); vi.useRealTimers(); vi.unstubAllGlobals(); });

it("retains known progress when a legacy warning is malformed and recovers a valid terminal response", async () => {
  const original = await vi.importActual<typeof import("../../app/lib/agent2-execution-api")>("../../app/lib/agent2-execution-api");
  api.read.mockImplementation(original.getAgent2ExecutionProgress);
  const terminal = { ...progress("FAILED"), warnings: [{ code: "HISTORICAL_ANALYSIS_PLAN_PAYLOAD_UNAVAILABLE", message: "历史分析的执行计划详情不可用；这里只显示已保存的研究状态。" }] };
  vi.stubGlobal("fetch", vi.fn()
    .mockResolvedValueOnce(Response.json(progress("RUNNING")))
    .mockResolvedValueOnce(Response.json({ ...terminal, warnings: ["HISTORICAL_ANALYSIS_PLAN_PAYLOAD_UNAVAILABLE"] }))
    .mockResolvedValueOnce(Response.json(terminal)));
  watcher = watchAgent2Execution("exact", callbacks);
  await flush();
  await vi.advanceTimersByTimeAsync(1800);
  expect(callbacks.progress).toHaveBeenCalledTimes(1);
  expect(callbacks.progress).toHaveBeenLastCalledWith(progress("RUNNING"));
  expect(callbacks.recovery).toHaveBeenLastCalledWith({ status: "reconnecting" });
  watcher.refresh(); await flush();
  expect(callbacks.progress).toHaveBeenLastCalledWith(terminal);
  expect(callbacks.recovery).toHaveBeenLastCalledWith({ status: "connected" });
  expect(api.dispatch).not.toHaveBeenCalled();
  expect(api.cancel).not.toHaveBeenCalled();
});

it.each(["PLAN_READY", "QUEUED"] as const)("observes %s session previews without dispatching or cancelling", async status => {
  api.read.mockResolvedValue({ ...progress(status), execution_dispatch_pending: true });
  watcher = watchAgent2Execution("exact", callbacks, { observeOnly: true });
  await flush();
  await watcher.cancel();
  watcher.retryDispatch();
  await vi.advanceTimersByTimeAsync(4000);
  expect(api.read.mock.calls.length).toBeGreaterThan(1);
  expect(api.dispatch).not.toHaveBeenCalled();
  expect(api.cancel).not.toHaveBeenCalled();
  api.read.mockResolvedValue(progress("COMPLETED"));
  watcher.refresh(); await flush();
  expect(callbacks.progress).toHaveBeenLastCalledWith(progress("COMPLETED"));
});

it.each(["RESULT_PENDING", "RESULT_READY", "CANCELED", "COMPLETED"] as const)("does not request cancellation for %s", async (status) => {
  api.read.mockResolvedValue(progress(status));
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  await watcher.cancel();
  expect(api.cancel).not.toHaveBeenCalled();
});

it.each(["CANCELING", "CANCELED", "ANSWERED"] as const)("can Stop before the first progress read and preserves the %s receipt", async (status) => {
  const initial = deferred<Agent2ProgressView>();
  const terminal = status === "ANSWERED" ? "ANSWERED" : "CANCELED";
  api.read.mockReturnValueOnce(initial.promise)
    .mockResolvedValueOnce(progress("ORCHESTRATING"))
    .mockResolvedValue(progress(terminal));
  api.cancel.mockResolvedValue({ turn_id: "exact", status });
  watcher = watchAgent2Execution("exact", callbacks);
  await watcher.cancel();
  expect(api.cancel).toHaveBeenCalledWith("exact", { signal: expect.any(AbortSignal) });
  expect(api.read.mock.calls[0][1].signal.aborted).toBe(true);
  initial.resolve(progress("PLANNING"));
  await flush();
  expect(callbacks.progress).not.toHaveBeenCalled();
  expect(callbacks.cancellation).toHaveBeenLastCalledWith("confirming", expect.any(String));
  await watcher.cancel();
  expect(api.cancel).toHaveBeenCalledTimes(1);
  await vi.advanceTimersByTimeAsync(1800);
  expect(callbacks.progress).toHaveBeenCalledTimes(1);
  expect(callbacks.progress).toHaveBeenLastCalledWith(progress(terminal));
  expect(callbacks.cancellation).toHaveBeenLastCalledWith("idle", terminal === "CANCELED" ? "" : expect.stringContaining("已进入终态"));
  expect(api.dispatch).not.toHaveBeenCalled();
});

it.each(["observeOnly", "disposed"])("cannot Stop an unread %s Turn", async mode => {
  api.read.mockReturnValue(new Promise(() => {}));
  watcher = watchAgent2Execution("exact", callbacks, { observeOnly: mode === "observeOnly" });
  if (mode === "disposed") watcher.dispose();
  await watcher.cancel();
  expect(api.cancel).not.toHaveBeenCalled();
});

it("retains known progress on failure, reconnects and prevents duplicate manual timers", async () => {
  api.read.mockResolvedValueOnce(progress("RUNNING")).mockRejectedValueOnce(new Error("timeout"));
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  await vi.advanceTimersByTimeAsync(1800);
  expect(callbacks.recovery).toHaveBeenLastCalledWith({ status: "reconnecting" });
  expect(callbacks.progress).toHaveBeenCalledTimes(1);
  window.dispatchEvent(new Event("online")); watcher.refresh(); await flush();
  expect(callbacks.recovery).toHaveBeenLastCalledWith({ status: "connected" });
  expect(api.read).toHaveBeenCalledTimes(3);
  await vi.advanceTimersByTimeAsync(1800);
  expect(api.read).toHaveBeenCalledTimes(4);
});
it.each([401, 403, 404, 410])("pauses automatic reads after HTTP %s without inventing a terminal state", async (status) => {
  api.read.mockRejectedValue(new Agent2ExecutionRequestError("untrusted server detail", status));
  watcher = watchAgent2Execution("exact", callbacks);
  await vi.advanceTimersByTimeAsync(20_000);
  expect(api.read).toHaveBeenCalledTimes(1);
  expect(callbacks.progress).not.toHaveBeenCalled();
  expect(api.dispatch).not.toHaveBeenCalled();
  expect(callbacks.recovery).toHaveBeenLastCalledWith({ status: "unavailable", message: expect.any(String) });
  expect(JSON.stringify(callbacks.recovery.mock.calls)).not.toContain("untrusted server detail");
});
it.each(["manual", "online", "visible"])("recovers an access denial on %s reread using the same Turn and resumes polling", async (trigger) => {
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  api.read.mockRejectedValueOnce(new Agent2ExecutionRequestError("denied", 403));
  watcher.refresh(); await flush();
  expect(callbacks.progress).toHaveBeenCalledTimes(1);
  expect(callbacks.progress).toHaveBeenLastCalledWith(progress("RUNNING"));
  if (trigger === "manual") { watcher.refresh(); watcher.refresh(); }
  else if (trigger === "online") window.dispatchEvent(new Event("online"));
  else document.dispatchEvent(new Event("visibilitychange"));
  await flush();
  expect(api.read).toHaveBeenCalledTimes(3);
  expect(callbacks.recovery).toHaveBeenLastCalledWith({ status: "connected" });
  await vi.advanceTimersByTimeAsync(1800);
  expect(api.read).toHaveBeenCalledTimes(4);
  expect(api.read.mock.calls.every(([id]) => id === "exact")).toBe(true);
  expect(api.dispatch).not.toHaveBeenCalled();
});
it.each([408, 429, 500, 503])("continues automatic recovery after transient HTTP %s", async (status) => {
  api.read.mockRejectedValueOnce(new Agent2ExecutionRequestError("transient", status));
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  expect(callbacks.recovery).toHaveBeenLastCalledWith({ status: "reconnecting" });
  await vi.advanceTimersByTimeAsync(1800);
  expect(callbacks.progress).toHaveBeenLastCalledWith(progress("RUNNING"));
  expect(callbacks.recovery).toHaveBeenLastCalledWith({ status: "connected" });
});
it("does not let a late dispatch receipt restart polling after access was denied", async () => {
  const dispatch = deferred<{ turn_id: string; status: string; queued: boolean }>();
  api.read.mockResolvedValueOnce(progress("PLAN_READY")).mockRejectedValue(new Agent2ExecutionRequestError("denied", 403));
  api.dispatch.mockReturnValueOnce(dispatch.promise);
  watcher = watchAgent2Execution("exact", callbacks); await vi.advanceTimersByTimeAsync(1800);
  expect(api.read).toHaveBeenCalledTimes(2);
  dispatch.resolve({ turn_id: "exact", status: "QUEUED", queued: true });
  await vi.advanceTimersByTimeAsync(20_000);
  expect(api.read).toHaveBeenCalledTimes(2);
  expect(callbacks.recovery).toHaveBeenLastCalledWith({ status: "unavailable", message: expect.any(String) });
});
it("retains cancellation uncertainty when access is lost and ignores recovery events after disposal", async () => {
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  api.cancel.mockRejectedValue(new Agent2ExecutionRequestError("denied", 403));
  api.read.mockRejectedValue(new Agent2ExecutionRequestError("denied", 403));
  await watcher.cancel(); await vi.advanceTimersByTimeAsync(20_000);
  expect(api.read).toHaveBeenCalledTimes(2);
  expect(callbacks.cancellation).toHaveBeenLastCalledWith("confirming", expect.stringContaining("尚未确认"));
  expect(callbacks.progress).toHaveBeenLastCalledWith(progress("RUNNING"));
  watcher.dispose(); watcher.refresh();
  window.dispatchEvent(new Event("online")); document.dispatchEvent(new Event("visibilitychange"));
  await flush();
  expect(api.read).toHaveBeenCalledTimes(2);
});
it("rejects foreign state before it can trigger a dispatch", async () => {
  api.read.mockResolvedValue(progress("PLAN_READY", "foreign"));
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  expect(callbacks.progress).not.toHaveBeenCalled();
  expect(api.dispatch).not.toHaveBeenCalled();
  expect(callbacks.recovery).toHaveBeenLastCalledWith({ status: "reconnecting" });
});
it("recovers a persisted unconfirmed queue publication after reopening with the same Turn", async () => {
  api.read.mockResolvedValue({ ...progress("QUEUED"), execution_dispatch_pending: true });
  api.dispatch.mockRejectedValueOnce(new Agent2ExecutionRequestError("queue unavailable", 503, true));
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  expect(api.dispatch).toHaveBeenCalledTimes(1);
  watcher.dispose();
  // A fresh watcher has no in-memory knowledge of the failed first publish.
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  expect(api.dispatch).toHaveBeenCalledTimes(2);
  expect(api.dispatch.mock.calls.every(([id]) => id === "exact")).toBe(true);
  api.read.mockResolvedValue({ ...progress("QUEUED"), execution_dispatch_pending: false });
  await vi.advanceTimersByTimeAsync(10_000);
  expect(api.dispatch).toHaveBeenCalledTimes(2);
  expect(callbacks.dispatch).toHaveBeenLastCalledWith("", false);
});
it.each(["QUEUED", "RUNNING", "CANCELING", "COMPLETED"] as const)("does not republish confirmed or advanced %s work", async (status) => {
  api.read.mockResolvedValue({ ...progress(status), execution_dispatch_pending: status !== "QUEUED" });
  watcher = watchAgent2Execution("exact", callbacks); await vi.advanceTimersByTimeAsync(8_000);
  expect(api.dispatch).not.toHaveBeenCalled();
});
it("retries uncertain dispatch only after an exact read, with bounded backoff and the same identity", async () => {
  api.read.mockResolvedValue(progress("PLAN_READY"));
  api.dispatch.mockRejectedValueOnce(new Agent2ExecutionRequestError("lost", 503, true));
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  expect(api.dispatch).toHaveBeenCalledTimes(1);
  api.read.mockRejectedValueOnce(new Error("offline"));
  await vi.advanceTimersByTimeAsync(1800);
  expect(api.dispatch).toHaveBeenCalledTimes(1);
  api.read.mockResolvedValue(progress("QUEUED"));
  await vi.advanceTimersByTimeAsync(1800);
  expect(api.dispatch).toHaveBeenCalledTimes(2);
  expect(api.dispatch.mock.calls.every(([id]) => id === "exact")).toBe(true);
  await vi.advanceTimersByTimeAsync(10_000);
  expect(api.dispatch).toHaveBeenCalledTimes(2);
});
it("does not dispatch an unrelated queued Turn", async () => {
  api.read.mockResolvedValue(progress("QUEUED"));
  watcher = watchAgent2Execution("exact", callbacks); await vi.advanceTimersByTimeAsync(12_000);
  expect(api.dispatch).not.toHaveBeenCalled();
});
it("recovers queued:false and stops automatic retries after explicit rejection", async () => {
  api.read.mockResolvedValue(progress("PLAN_READY"));
  api.dispatch.mockResolvedValueOnce({ turn_id: "exact", status: "PLAN_READY", queued: false })
    .mockRejectedValueOnce(new Agent2ExecutionRequestError("denied", 403));
  watcher = watchAgent2Execution("exact", callbacks); await vi.advanceTimersByTimeAsync(10_000);
  expect(api.dispatch).toHaveBeenCalledTimes(2);
  expect(callbacks.dispatch).toHaveBeenLastCalledWith("暂时无法开始分析，请重新尝试。", true);
  watcher.retryDispatch(); await flush();
  expect(api.dispatch).toHaveBeenCalledTimes(3);
});
it("stops dispatch recovery when rereading a terminal Turn", async () => {
  api.read.mockResolvedValueOnce(progress("PLAN_READY")).mockResolvedValue(progress("CANCELED"));
  api.dispatch.mockRejectedValueOnce(new Error("conflict"));
  watcher = watchAgent2Execution("exact", callbacks); await vi.advanceTimersByTimeAsync(10_000);
  expect(api.dispatch).toHaveBeenCalledTimes(1);
  expect(callbacks.progress).toHaveBeenLastCalledWith(progress("CANCELED"));
  expect(callbacks.dispatch).toHaveBeenLastCalledWith("", false);
});
it.each(["RUNNING", "INTERPRETING"] as const)("keeps %s Stop unconfirmed until a successful read and blocks duplicate cancellation", async (status) => {
  api.read.mockResolvedValue(progress(status));
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  api.cancel.mockRejectedValueOnce(new Agent2ExecutionRequestError("timeout", undefined, true));
  api.read.mockRejectedValue(new Error("offline"));
  await watcher.cancel(); await flush(); await watcher.cancel();
  expect(api.cancel).toHaveBeenCalledTimes(1);
  expect(callbacks.cancellation).toHaveBeenLastCalledWith("confirming", expect.stringContaining("尚未确认"));
  api.read.mockResolvedValue(progress(status)); watcher.refresh(); await flush();
  expect(callbacks.cancellation).toHaveBeenLastCalledWith("idle", expect.stringContaining("再次取消"));
  await watcher.cancel();
  expect(api.cancel).toHaveBeenCalledTimes(2);
});
it.each(["RUNNING", "INTERPRETING"] as const)("rejects old %s polling replies after cancellation and cannot regress a known terminal state", async (status) => {
  api.read.mockResolvedValue(progress(status));
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  const old = deferred<Agent2ProgressView>(); api.read.mockReturnValueOnce(old.promise);
  watcher.refresh();
  api.cancel.mockResolvedValueOnce({ turn_id: "exact", status: "CANCELED" });
  await watcher.cancel(); old.resolve(progress(status)); await flush();
  expect(callbacks.progress).toHaveBeenLastCalledWith(progress("CANCELED"));
  watcher.refresh(); await flush();
  expect(callbacks.progress).toHaveBeenLastCalledWith(progress("CANCELED"));
});
it("ignores late cancellation and read replies after navigating to another Turn", async () => {
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  const pending = deferred<{ turn_id: string; status: string }>(); api.cancel.mockReturnValueOnce(pending.promise);
  const cancel = watcher.cancel(); watcher.dispose();
  callbacks.progress.mockClear(); callbacks.cancellation.mockClear();
  pending.resolve({ turn_id: "exact", status: "CANCELED" }); await cancel;
  expect(callbacks.progress).not.toHaveBeenCalled(); expect(callbacks.cancellation).not.toHaveBeenCalled();
  expect(api.cancel.mock.calls[0][1].signal.aborted).toBe(true);
});
it.each(["RUNNING", "INTERPRETING"] as const)("preserves completion that won the %s Stop race", async (status) => {
  api.read.mockResolvedValue(progress(status));
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  api.cancel.mockRejectedValueOnce(new Error("conflict")); api.read.mockResolvedValue(progress("COMPLETED"));
  await watcher.cancel(); await flush();
  expect(callbacks.progress).toHaveBeenLastCalledWith(progress("COMPLETED"));
  expect(callbacks.cancellation).toHaveBeenLastCalledWith("idle", expect.stringContaining("已进入终态"));
});

it.each(["NEEDS_CLARIFICATION", "UNSUPPORTED", "PLAN_REJECTED", "ANSWERED"] as const)("recognizes %s as durable terminal feedback", async (status) => {
  api.read.mockResolvedValue(progress(status));
  watcher = watchAgent2Execution("exact", callbacks); await vi.advanceTimersByTimeAsync(12_000);
  expect(callbacks.progress).toHaveBeenLastCalledWith(progress(status));
  expect(api.read).toHaveBeenCalledTimes(1);
  expect(callbacks.recovery).toHaveBeenLastCalledWith({ status: "connected" });
  expect(api.dispatch).not.toHaveBeenCalled();
});

it("rejects a mismatched cancellation result and reads the original Turn again", async () => {
  watcher = watchAgent2Execution("exact", callbacks); await flush();
  api.cancel.mockResolvedValueOnce({ turn_id: "foreign", status: "CANCELED" });
  await watcher.cancel(); await flush();
  expect(callbacks.progress.mock.calls.every(([value]) => value.turn_id === "exact" && value.status === "RUNNING")).toBe(true);
  expect(api.read).toHaveBeenLastCalledWith("exact", { signal: expect.any(AbortSignal) });
});
