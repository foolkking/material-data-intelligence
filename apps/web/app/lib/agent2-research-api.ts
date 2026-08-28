import type { Artifact, GroundedScientificInterpretation } from "./planner-api";

const API_BASE = (process.env.NEXT_PUBLIC_MDI_API_BASE_URL || (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")).replace(/\/$/, "");

export type Agent2ScientificObjectRef = { object_id: string; version_id: string; project_id: string; object_type: string; display_name?: string };
export type Agent2ScientificSelection = { contract_version: "1.0"; object_ref: Agent2ScientificObjectRef; viewer_id: string; selection_type: string; semantic_locator: Record<string, string | number>; display_label: string; evidence_locator?: Record<string, string | number> | null };
export type Agent2TurnResponse = { turn_id: string; research_session_id: string; project_id: string; sequence_no: number; status: string; user_message: { id: string; role: string; content: string }; created_at: string };
export type Agent2ContextManifestItem = {
  item_id: string;
  kind: string;
  authority_class: string;
  server_side_source_identity: string;
  provider_opaque_ref: string;
  exact_object_id?: string | null;
  exact_object_version_id?: string | null;
  result_ref?: string | null;
  inclusion_reason: string;
  selection_mode: string;
  authorization_checked: boolean;
  estimated_tokens: number;
  was_compacted: boolean;
  was_truncated: boolean;
  superseded_state: string;
};
export type Agent2ContextManifest = {
  context_manifest_id: string;
  operation: string;
  project_id: string;
  research_session_id: string;
  research_turn_id: string;
  policy_version: string;
  included_items: Agent2ContextManifestItem[];
  excluded_items: string[];
  estimated_input_tokens: number;
  input_budget: number;
  reserved_output_tokens: number;
  repair_margin: number;
  compaction_state: string;
  truncation_state: string;
  context_fingerprint: string;
  created_at: string;
};
export type Agent2TurnDetail = Agent2TurnResponse & {
  context?: { manifest?: Agent2ContextManifest | null } | null;
};
export type Agent2ScientificFact = {
  fact_id: string;
  predicate: string;
  subject_ref: string;
  value: unknown;
  unit?: string | null;
  source: { tool_call_id?: string | null; artifact_id?: string | null; artifact_locator?: string | null; scientific_object_ref?: Agent2ScientificObjectRef | null };
};
export type Agent2ScientificEvidence = {
  evidence_id: string;
  evidence_type: string;
  artifact_id?: string | null;
  tool_call_id?: string | null;
  artifact_locator?: string | null;
  scientific_object_refs?: Agent2ScientificObjectRef[];
  supports_fact_refs?: string[];
  supports_result_item_refs?: string[];
};
export type Agent2ResearchTurnResult = {
  result_id: string;
  research_turn_id: string;
  research_question: string;
  execution_status: string;
  relevance_status: "CURRENT" | "STALE" | "SOURCE_MISSING" | "INVALIDATED";
  source_object_refs: Agent2ScientificObjectRef[];
  facts: Agent2ScientificFact[];
  figures: Array<{ figure_id: string; artifact_ids: string[]; title?: string | null }>;
  tables: Array<{ table_id: string; artifact_ids: string[]; title?: string | null }>;
  evidence: Agent2ScientificEvidence[];
  artifacts: Artifact[];
  scientific_selections: Agent2ScientificSelection[];
};
export type Agent2ResearchTurnInterpretation = {
  interpretation_id: string;
  research_turn_id: string;
  status: "VALID" | "REJECTED" | "PENDING" | string;
  title?: string | null;
  message?: string | null;
  execution_status?: string | null;
  interpretation?: GroundedScientificInterpretation | null;
};

async function readAgent2<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { credentials: "include" });
  if (!response.ok) throw new Error(`科学呈现暂时无法读取 (${response.status})`);
  return response.json() as Promise<T>;
}

export async function createAgent2ResearchTurn(projectId: string, sessionId: string, input: {
  message: string;
  ui_context: { active_object_refs: Agent2ScientificObjectRef[]; selection_refs: Agent2ScientificObjectRef[]; scientific_selections: Agent2ScientificSelection[]; explicit_object_refs: Agent2ScientificObjectRef[]; explicit_result_ids: string[]; explicit_finding_refs: string[] };
  reply_to_turn_id?: string;
}): Promise<Agent2TurnResponse> {
  const response = await fetch(`${API_BASE}/api/projects/${encodeURIComponent(projectId)}/research/sessions/${encodeURIComponent(sessionId)}/turns`, {
    method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify(input),
  });
  if (!response.ok) {
    let detail = `研究请求失败 (${response.status})`;
    try { const body = await response.json() as { detail?: string }; if (body.detail) detail = body.detail; } catch { /* bounded product error */ }
    throw new Error(detail);
  }
  return response.json() as Promise<Agent2TurnResponse>;
}

export async function dispatchAgent2ResearchTurn(turnId: string): Promise<{ turn_id: string; status: string; queued: boolean }> {
  const response = await fetch(`${API_BASE}/api/research/turns/${encodeURIComponent(turnId)}/dispatch`, {
    method: "POST",
    credentials: "include",
  });
  if (!response.ok) {
    let detail = `研究执行失败 (${response.status})`;
    try { const body = await response.json() as { detail?: string }; if (body.detail) detail = body.detail; } catch { /* bounded product error */ }
    throw new Error(detail);
  }
  return response.json() as Promise<{ turn_id: string; status: string; queued: boolean }>;
}

export const getAgent2ResearchTurnResult = (turnId: string) =>
  readAgent2<Agent2ResearchTurnResult>(`/api/research/turns/${encodeURIComponent(turnId)}/result`);

export const getAgent2ResearchTurn = (turnId: string) =>
  readAgent2<Agent2TurnDetail>(`/api/research/turns/${encodeURIComponent(turnId)}`);

export const getAgent2ContextManifest = (turnId: string) =>
  readAgent2<{ turn_id: string; manifest: Agent2ContextManifest }>(`/api/research/turns/${encodeURIComponent(turnId)}/context-manifest`);

export const getAgent2ResearchTurnInterpretation = (turnId: string) =>
  readAgent2<Agent2ResearchTurnInterpretation>(`/api/research/turns/${encodeURIComponent(turnId)}/interpretation`);
