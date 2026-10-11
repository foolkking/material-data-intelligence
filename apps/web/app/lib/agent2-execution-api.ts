const API_BASE = (process.env.NEXT_PUBLIC_MDI_API_BASE_URL || (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")).replace(/\/$/, "");

export type Agent2ExecutionStatus = "RECEIVED" | "RESOLVING_CONTEXT" | "NEEDS_CLARIFICATION" | "UNSUPPORTED" | "PLAN_REJECTED" | "ORCHESTRATING" | "READY_TO_PLAN" | "PLANNING" | "PLAN_READY" | "QUEUED" | "RUNNING" | "CANCELING" | "RESULT_PENDING" | "RESULT_READY" | "INTERPRETING" | "COMPLETED" | "PARTIAL" | "FAILED" | "CANCELED" | "ANSWERED";
export type Agent2ProgressStep = {
  step_id: string;
  display_name: string;
  status: "PENDING" | "RUNNING" | "SUCCEEDED" | "FAILED" | "SKIPPED" | "CANCELED";
  running_label?: string | null;
  completed_label?: string | null;
  output_available: boolean;
  warning?: string | null;
};
export type Agent2AutonomyProgress = {
  enabled: boolean;
  mode: string;
  cycle_index: number;
  objective?: string | null;
  subgoal?: string | null;
  decision?: {
    outcome?: string | null;
    reason_codes?: string[];
    qualification_level?: string | null;
    limitations?: string[];
    strategy?: {
      action?: string | null;
      evidence_strength?: string | null;
      questions?: Array<{
        question_id?: string | null;
        question_type?: string | null;
        statement?: string | null;
        status?: "OPEN" | "RESOLVED" | "LIMITED" | "CONFLICTING" | string | null;
        evidence_result_ids?: string[];
        evidence_gap_ids?: string[];
      }>;
      evidence_gaps?: Array<{
        gap_id?: string | null;
        question_id?: string | null;
        statement?: string | null;
        gap_type?: string | null;
        satisfied_by_result_ids?: string[];
      }>;
      hypotheses?: Array<{
        hypothesis_id?: string | null;
        question_id?: string | null;
        statement?: string | null;
        status?: string | null;
        supporting_result_ids?: string[];
        contradicting_result_ids?: string[];
        known_assumptions?: string[];
      }>;
      contradictions?: Array<{
        contradiction_id?: string | null;
        predicate?: string | null;
        kind?: string | null;
        resolution?: string | null;
        unresolved?: boolean;
      }>;
      current_question?: {
        question_id?: string | null;
        statement?: string | null;
        status?: string | null;
        evidence_result_ids?: string[];
        evidence_gap_ids?: string[];
      } | null;
      active_evidence_gap?: { gap_id?: string | null; question_id?: string | null; statement?: string | null; gap_type?: string | null } | null;
      active_hypothesis?: {
        hypothesis_id?: string | null;
        question_id?: string | null;
        statement?: string | null;
        status?: string | null;
        supporting_result_ids?: string[];
        contradicting_result_ids?: string[];
        known_assumptions?: string[];
      } | null;
      evidence_value?: string | null;
      comparison_status?: string | null;
    } | null;
  } | null;
  stop?: {
    stopped?: boolean;
    reason?: string | null;
  } | null;
};
export type Agent2ProgressView = {
  contract_version: "1.0";
  turn_id: string;
  status: Agent2ExecutionStatus;
  response_kind?: "DATA_QUERY" | "RESULT_REUSE" | "CONVERSATIONAL" | "SCIENTIFIC_EXECUTION" | null;
  plan_title?: string | null;
  steps: Agent2ProgressStep[];
  active_step_ids: string[];
  completed_step_count: number;
  total_step_count: number;
  incremental_outputs: Array<{ output_key: string; step_id: string; display_label: string; artifact_id: string; preview_available: boolean; available_at: string; content_url?: string }>;
  warnings: Array<{ code: string; message: string }>;
  execution_outcome?: "SUCCESS" | "PARTIAL" | "FAILED" | "CANCELED" | null;
  result_projection_pending: boolean;
  preserved_result_available?: boolean;
  execution_dispatch_pending?: boolean;
  autonomy?: Agent2AutonomyProgress;
};

export const isAgent2ExecutionTerminal = (status?: string) => ["COMPLETED", "PARTIAL", "FAILED", "CANCELED", "ANSWERED", "NEEDS_CLARIFICATION", "UNSUPPORTED", "PLAN_REJECTED"].includes(status || "");
const executionStatuses = new Set(["RECEIVED", "RESOLVING_CONTEXT", "NEEDS_CLARIFICATION", "UNSUPPORTED", "PLAN_REJECTED", "ORCHESTRATING", "READY_TO_PLAN", "PLANNING", "PLAN_READY", "QUEUED", "RUNNING", "CANCELING", "RESULT_PENDING", "RESULT_READY", "INTERPRETING", "COMPLETED", "PARTIAL", "FAILED", "CANCELED", "ANSWERED"]);

export class Agent2ExecutionRequestError extends Error {
  constructor(message: string, readonly status?: number, readonly uncertain = false) {
    super(message);
    this.name = "Agent2ExecutionRequestError";
  }
}

/** Bound receipt of a response, without imposing a deadline on scientific work. */
export async function readExecutionResponse<T>(path: string, operation: "progress" | "cancel" | "dispatch", signal?: AbortSignal): Promise<T> {
  signal?.throwIfAborted();
  const controller = new AbortController();
  const label = operation === "cancel" ? "取消" : "执行";
  let timer: ReturnType<typeof setTimeout> | undefined;
  let cancel = () => {};
  const interrupted = new Promise<never>((_, reject) => {
    cancel = () => { controller.abort(); reject(new DOMException("Request cancelled", "AbortError")); };
    signal?.addEventListener("abort", cancel, { once: true });
    timer = setTimeout(() => {
      controller.abort();
      reject(new Agent2ExecutionRequestError(operation === "progress" ? "进度读取超时，请重试。" : `${label}结果尚未确认，请重新读取研究状态。`, undefined, operation !== "progress"));
    }, 10_000);
  });
  try {
    return await Promise.race([interrupted, (async () => {
      const response = await fetch(`${API_BASE}${path}`, { method: operation === "progress" ? "GET" : "POST", credentials: "include", signal: controller.signal });
      if (response.status === 401 && typeof window !== "undefined") window.dispatchEvent(new CustomEvent("mdi:session-expired"));
      if (!response.ok) throw new Agent2ExecutionRequestError(operation === "progress" ? `执行进度暂时无法读取 (${response.status})` : `${label}请求暂未确认 (${response.status})`, response.status, operation !== "progress" && response.status >= 500);
      return await response.json() as T;
    })()]);
  } catch (reason) {
    if (reason instanceof Agent2ExecutionRequestError || (reason instanceof DOMException && reason.name === "AbortError")) throw reason;
    throw new Agent2ExecutionRequestError(operation === "progress" ? "研究进度暂时无法读取，请重试。" : `${label}结果尚未确认，请重新读取研究状态。`, undefined, operation !== "progress");
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener("abort", cancel);
    controller.abort();
  }
}

export function validateExecutionIdentity(value: { turn_id?: string; status?: string } | null, turnId: string) {
  if (!value || value.turn_id !== turnId || !executionStatuses.has(value.status || "")) throw new Agent2ExecutionRequestError("研究状态与当前请求不匹配，请重新读取。", undefined, true);
}

export async function getAgent2ExecutionProgress(turnId: string, options: Readonly<{ signal?: AbortSignal }> = {}) {
  const value = await readExecutionResponse<Agent2ProgressView>(`/api/research/turns/${encodeURIComponent(turnId)}/progress`, "progress", options.signal);
  validateExecutionIdentity(value, turnId);
  if (!Array.isArray(value.steps) || !Array.isArray(value.incremental_outputs) || !Array.isArray(value.warnings) ||
      value.warnings.some(warning => !warning || typeof warning.code !== "string" || typeof warning.message !== "string")) {
    throw new Agent2ExecutionRequestError("研究进度内容暂时无法读取，请重试。");
  }
  return value;
}

export async function cancelAgent2Execution(turnId: string, options: Readonly<{ signal?: AbortSignal }> = {}) {
  const value = await readExecutionResponse<{ turn_id: string; status: Agent2ExecutionStatus }>(`/api/research/turns/${encodeURIComponent(turnId)}/cancel`, "cancel", options.signal);
  validateExecutionIdentity(value, turnId);
  return value;
}
