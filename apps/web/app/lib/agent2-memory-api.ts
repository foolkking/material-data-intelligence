const API_BASE = (
  process.env.NEXT_PUBLIC_MDI_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")
).replace(/\/$/, "");

export type Agent2SessionConstraint = {
  id: string;
  statement: string;
  structured_constraint?: Record<string, unknown> | null;
};

export type Agent2SessionMemory = {
  session_id: string;
  project_id: string;
  pinned_object_refs: Array<{
    object_id: string;
    version_id: string;
    project_id: string;
    display_name?: string | null;
    object_type: string;
  }>;
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

async function mutateAgent2SessionMemory(
  projectId: string,
  sessionId: string,
  resultId: string,
  method: "POST" | "DELETE",
): Promise<Agent2SessionMemory> {
  const response = await fetch(
    `${API_BASE}/api/projects/${encodeURIComponent(projectId)}/research/sessions/${encodeURIComponent(sessionId)}/memory/pinned-results/${encodeURIComponent(resultId)}`,
    { method, credentials: "include" },
  );
  if (!response.ok) throw new Error(`Research memory update failed (${response.status})`);
  return response.json() as Promise<Agent2SessionMemory>;
}

export const pinAgent2Result = (projectId: string, sessionId: string, resultId: string) =>
  mutateAgent2SessionMemory(projectId, sessionId, resultId, "POST");

export const unpinAgent2Result = (projectId: string, sessionId: string, resultId: string) =>
  mutateAgent2SessionMemory(projectId, sessionId, resultId, "DELETE");

type ScientificObjectMemoryRef = {
  object_id: string;
  version_id: string;
  project_id: string;
  object_type: string;
  display_name?: string | null;
};

async function mutateAgent2SessionObjectMemory(
  projectId: string,
  sessionId: string,
  objectRef: ScientificObjectMemoryRef,
  method: "POST" | "DELETE",
): Promise<Agent2SessionMemory> {
  const response = await fetch(
    `${API_BASE}/api/projects/${encodeURIComponent(projectId)}/research/sessions/${encodeURIComponent(sessionId)}/memory/pinned-objects`,
    {
      method,
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ object_ref: objectRef }),
    },
  );
  if (!response.ok) throw new Error(`Research source context update failed (${response.status})`);
  return response.json() as Promise<Agent2SessionMemory>;
}

export const pinAgent2Object = (
  projectId: string,
  sessionId: string,
  objectRef: ScientificObjectMemoryRef,
) => mutateAgent2SessionObjectMemory(projectId, sessionId, objectRef, "POST");

export const unpinAgent2Object = (
  projectId: string,
  sessionId: string,
  objectRef: ScientificObjectMemoryRef,
) => mutateAgent2SessionObjectMemory(projectId, sessionId, objectRef, "DELETE");
