const API_BASE = (process.env.NEXT_PUBLIC_MDI_API_BASE_URL || (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")).replace(/\/$/, "");

export type Agent2ScientificObjectRef = { object_id: string; version_id: string; project_id: string; object_type: string; display_name?: string };
export type Agent2ScientificSelection = { contract_version: "1.0"; object_ref: Agent2ScientificObjectRef; viewer_id: string; selection_type: string; semantic_locator: Record<string, string | number>; display_label: string; evidence_locator?: Record<string, string | number> | null };
export type Agent2TurnResponse = { turn_id: string; research_session_id: string; project_id: string; sequence_no: number; status: string; user_message: { id: string; role: string; content: string }; created_at: string };

export async function createAgent2ResearchTurn(projectId: string, sessionId: string, input: {
  message: string;
  ui_context: { active_object_refs: Agent2ScientificObjectRef[]; selection_refs: Agent2ScientificObjectRef[]; scientific_selections: Agent2ScientificSelection[]; explicit_object_refs: Agent2ScientificObjectRef[]; explicit_result_ids: string[]; explicit_finding_refs: string[] };
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
