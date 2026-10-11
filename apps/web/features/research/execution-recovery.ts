import { Agent2ExecutionRequestError, cancelAgent2Execution, getAgent2ExecutionProgress, isAgent2ExecutionTerminal, validateExecutionIdentity, type Agent2ProgressView } from "../../app/lib/agent2-execution-api";
import { dispatchAgent2ResearchTurn } from "../../app/lib/agent2-research-api";
import { canCancelResearchTurn as cancelable, RESEARCH_CANCELLING_POLL_INTERVAL_MS as pollInterval } from "../../app/lib/research-status";

export type ExecutionCancelState = "idle" | "submitting" | "confirming";
export type ExecutionReadState = { status: "connected" | "reconnecting" } | { status: "unavailable"; message: string };
type Callbacks = {
  progress: (value: Agent2ProgressView) => void;
  recovery: (value: ExecutionReadState) => void;
  cancellation: (state: ExecutionCancelState, notice: string) => void;
  dispatch: (notice: string, retryable: boolean) => void;
};
const terminalCancelNotice = "分析在取消请求生效前已进入终态；现有科学结果未被覆盖。";
const unavailableMessages: Record<number, string> = {
  401: "登录状态已过期，请重新登录后读取研究进度。",
  403: "当前账号无权读取这项研究，请确认项目访问权限。",
  404: "找不到这项研究记录，请从研究列表确认记录是否仍可访问。",
  410: "这项研究记录已不可用，请从研究列表查看其他记录。",
};

/** Owns one exact Turn. Transport deadlines live in the API; durable state wins races. */
export function watchAgent2Execution(turnId: string, callbacks: Callbacks, options: { observeOnly?: boolean } = {}) {
  const controller = new AbortController();
  let readController: AbortController | undefined;
  let readEpoch = 0;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let last: Agent2ProgressView | undefined;
  let lastStatus: Agent2ProgressView["status"] | undefined;
  let failures = 0;
  let readUnavailable = false;
  let cancelState: ExecutionCancelState = "idle";
  let cancelRequested = false;
  let dispatchPending = false;
  let dispatched = false;
  let dispatchUnconfirmed = false;
  let dispatchBlocked = false;
  let dispatchAttempts = 0;
  let dispatchAfter = 0;
  const active = () => !controller.signal.aborted;

  function setCancellation(state: ExecutionCancelState, notice: string) {
    cancelState = state;
    callbacks.cancellation(state, notice);
  }
  function accept(next: Agent2ProgressView) {
    validateExecutionIdentity(next, turnId);
    // A read started before Stop must not restore an obsolete running state.
    if (isAgent2ExecutionTerminal(lastStatus) && next.status !== lastStatus) return;
    if (lastStatus === "CANCELING" && cancelable(next.status)) return;
    last = next;
    lastStatus = next.status;
    callbacks.progress(next);
    if (isAgent2ExecutionTerminal(next.status)) {
      if (cancelRequested) setCancellation("idle", next.status === "CANCELED" ? "" : terminalCancelNotice);
    } else if (next.status === "CANCELING") {
      setCancellation("confirming", "取消请求已记录，正在等待运行中的科学步骤安全结束。");
    } else if (cancelState === "confirming") {
      setCancellation("idle", "尚未确认取消，已重新读取当前状态；如需停止，可再次取消。");
    }
    if (!["PLAN_READY", "QUEUED"].includes(next.status)) {
      dispatchUnconfirmed = false;
      callbacks.dispatch("", false);
    }
  }
  function schedule(delay: number) {
    clearTimeout(timer);
    if (active() && !readUnavailable) timer = setTimeout(() => { timer = undefined; void refresh(); }, delay);
  }
  async function dispatch() {
    dispatchPending = true;
    dispatchAttempts += 1;
    try {
      const result = await dispatchAgent2ResearchTurn(turnId, { signal: controller.signal });
      if (!active()) return;
      validateExecutionIdentity(result, turnId);
      if (typeof result.queued !== "boolean") throw new Agent2ExecutionRequestError("排队结果尚未确认", undefined, true);
      dispatched = result.queued || !["PLAN_READY", "QUEUED"].includes(result.status);
      if (!dispatched) throw new Agent2ExecutionRequestError("排队结果尚未确认", undefined, true);
      callbacks.dispatch("", false);
    } catch (reason) {
      if (!active()) return;
      if (last && !["PLAN_READY", "QUEUED"].includes(last.status)) return;
      const status = reason instanceof Agent2ExecutionRequestError ? reason.status : undefined;
      dispatchBlocked = status !== undefined && status >= 400 && status < 500 && ![408, 429].includes(status);
      dispatchUnconfirmed = !dispatchBlocked;
      dispatchAfter = Date.now() + Math.min(pollInterval * 2 ** Math.min(dispatchAttempts - 1, 3), 8000);
      callbacks.dispatch(dispatchBlocked ? "暂时无法开始分析，请重新尝试。" : "开始执行的结果尚未确认，正在读取当前状态…", dispatchBlocked);
    } finally {
      dispatchPending = false;
      // Always read before attempting the same idempotent dispatch again.
      if (active()) schedule(pollInterval);
    }
  }
  async function refresh() {
    if (!active() || readController || cancelState === "submitting") return;
    clearTimeout(timer);
    timer = undefined;
    const request = new AbortController();
    readController = request;
    const epoch = ++readEpoch;
    let failed = false;
    try {
      const next = await getAgent2ExecutionProgress(turnId, { signal: request.signal });
      if (!active() || epoch !== readEpoch) return;
      accept(next);
      failures = 0;
      readUnavailable = false;
      callbacks.recovery({ status: "connected" });
      if (!options.observeOnly && cancelState === "idle" && !dispatchPending && !dispatched && !dispatchBlocked && Date.now() >= dispatchAfter &&
          (last?.status === "PLAN_READY" || (last?.status === "QUEUED" && (dispatchUnconfirmed || last.execution_dispatch_pending === true)))) void dispatch();
    } catch (reason) {
      if (!active() || epoch !== readEpoch) return;
      failed = true;
      failures += 1;
      const message = reason instanceof Agent2ExecutionRequestError && reason.status !== undefined
        ? unavailableMessages[reason.status] : undefined;
      readUnavailable = Boolean(message);
      callbacks.recovery(message ? { status: "unavailable", message } : { status: "reconnecting" });
    } finally {
      if (epoch === readEpoch) {
        readController = undefined;
        if (active() && (failed || !last || !isAgent2ExecutionTerminal(lastStatus))) {
          schedule(failed ? Math.min(pollInterval * 2 ** Math.min(failures - 1, 3), 8000) : pollInterval);
        }
      }
    }
  }
  async function cancel() {
    // Public answer deltas can arrive before the first progress read. The
    // server still authorizes Stop for this exact Turn and its current state.
    if (options.observeOnly || !active() || cancelState !== "idle" || (lastStatus && !cancelable(lastStatus))) return;
    cancelRequested = true;
    setCancellation("submitting", "");
    clearTimeout(timer);
    // Supersede the pending read before Stop, even if transport ignores abort.
    readEpoch += 1;
    readController?.abort();
    readController = undefined;
    try {
      const result = await cancelAgent2Execution(turnId, { signal: controller.signal });
      if (!active()) return;
      validateExecutionIdentity(result, turnId);
      setCancellation("confirming", "取消请求已记录，正在等待运行中的科学步骤安全结束。");
      if (last) {
        accept({ ...last, status: result.status });
        if (active()) schedule(pollInterval);
      } else {
        // Fence stale reads using the receipt without inventing progress data.
        lastStatus = result.status;
        void refresh();
      }
    } catch {
      if (!active()) return;
      setCancellation("confirming", "取消结果尚未确认，正在重新读取进度。");
      void refresh();
    }
  }
  const onOnline = () => { void refresh(); };
  const onVisible = () => { if (document.visibilityState === "visible") onOnline(); };
  window.addEventListener("online", onOnline);
  document.addEventListener("visibilitychange", onVisible);
  void refresh();
  return {
    refresh: onOnline,
    cancel,
    retryDispatch: () => { dispatchBlocked = false; dispatchAfter = 0; void refresh(); },
    dispose: () => {
      controller.abort();
      readController?.abort();
      clearTimeout(timer);
      window.removeEventListener("online", onOnline);
      document.removeEventListener("visibilitychange", onVisible);
    },
  };
}
