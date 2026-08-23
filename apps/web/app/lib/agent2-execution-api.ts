const API_BASE = (process.env.NEXT_PUBLIC_MDI_API_BASE_URL || (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")).replace(/\/$/, "");

export type Agent2ExecutionStatus = "PLAN_READY" | "QUEUED" | "RUNNING" | "CANCELING" | "RESULT_PENDING" | "RESULT_READY" | "FAILED" | "CANCELED";
export type Agent2ProgressStep = {
  step_id: string;
  display_name: string;
  status: "PENDING" | "RUNNING" | "SUCCEEDED" | "FAILED" | "SKIPPED" | "CANCELED";
  running_label?: string | null;
  completed_label?: string | null;
  output_available: boolean;
  warning?: string | null;
};
export type Agent2ProgressView = {
  contract_version: "1.0";
  turn_id: string;
  status: Agent2ExecutionStatus;
  plan_title?: string | null;
  steps: Agent2ProgressStep[];
  active_step_ids: string[];
  completed_step_count: number;
  total_step_count: number;
  incremental_outputs: Array<{ output_key: string; step_id: string; display_label: string; artifact_id: string; preview_available: boolean; available_at: string }>;
  warnings: Array<{ code: string; message: string }>;
  execution_outcome?: "SUCCESS" | "PARTIAL" | "FAILED" | "CANCELED" | null;
  result_projection_pending: boolean;
};

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { credentials: "include" });
  if (!response.ok) throw new Error(`执行进度暂时无法读取 (${response.status})`);
  return (await response.json()) as T;
}

async function mutate<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { method: "POST", credentials: "include" });
  if (!response.ok) throw new Error(`取消请求未能提交 (${response.status})`);
  return (await response.json()) as T;
}

export const getAgent2ExecutionProgress = (turnId: string) => request<Agent2ProgressView>(`/api/research/turns/${encodeURIComponent(turnId)}/progress`);
export const cancelAgent2Execution = (turnId: string) => mutate<{ turn_id: string; status: Agent2ExecutionStatus }>(`/api/research/turns/${encodeURIComponent(turnId)}/cancel`);
