const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export type Agent2SessionConstraint = {
  id: string;
  statement: string;
  structured_constraint?: Record<string, unknown> | null;
};

export type Agent2SessionMemory = {
  session_id: string;
  project_id: string;
  pinned_object_refs: Array<{ display_name?: string | null; object_type: string }>;
  pinned_result_refs: string[];
  session_constraints: Agent2SessionConstraint[];
  active_research_goal?: string | null;
  version: number;
};

export async function getAgent2SessionMemory(projectId: string, sessionId: string): Promise<Agent2SessionMemory> {
  const response = await fetch(
    `${API_BASE}/api/projects/${encodeURIComponent(projectId)}/research/sessions/${encodeURIComponent(sessionId)}/memory`,
    { credentials: "include" },
  );
  if (!response.ok) throw new Error(`Research memory unavailable (${response.status})`);
  return response.json() as Promise<Agent2SessionMemory>;
}
