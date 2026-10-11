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

export class Agent2MemoryError extends Error {
  constructor(message: string, readonly status?: number) { super(message); this.name = "Agent2MemoryError"; }
}

export function validateSessionMemory(value: Agent2SessionMemory, projectId: string, sessionId: string) {
  if (!value || value.project_id !== projectId || value.session_id !== sessionId ||
      !Number.isSafeInteger(value.version) || value.version < 0 ||
      !Array.isArray(value.pinned_result_refs) || value.pinned_result_refs.some((id) => typeof id !== "string" || !id) ||
      !Array.isArray(value.pinned_object_refs) || value.pinned_object_refs.some((ref) => !ref || ref.project_id !== projectId || !ref.object_id || !ref.version_id || !ref.object_type) ||
      !Array.isArray(value.session_constraints) || value.session_constraints.some((item) => !item || typeof item.id !== "string" || typeof item.statement !== "string") ||
      (value.active_research_goal != null && typeof value.active_research_goal !== "string")) {
    throw new Agent2MemoryError("上下文与当前会话不匹配，请重新读取。");
  }
  return value;
}

type RequestOptions = Readonly<{ signal?: AbortSignal }>;

async function memoryRequest(projectId: string, sessionId: string, suffix: string, init: RequestInit, options: RequestOptions) {
  options.signal?.throwIfAborted();
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  let cancel = () => {};
  const interrupted = new Promise<never>((_, reject) => {
    cancel = () => { controller.abort(); reject(new DOMException("Request cancelled", "AbortError")); };
    options.signal?.addEventListener("abort", cancel, { once: true });
    timer = setTimeout(() => { controller.abort(); reject(new Agent2MemoryError("上下文请求超时，请重新读取。")); }, 10_000);
  });
  try {
    return await Promise.race([interrupted, (async () => {
      const response = await fetch(`${API_BASE}/api/projects/${encodeURIComponent(projectId)}/research/sessions/${encodeURIComponent(sessionId)}/memory${suffix}`, {
        ...init, credentials: "include", signal: controller.signal,
      });
      if (response.status === 401 && typeof window !== "undefined") window.dispatchEvent(new CustomEvent("mdi:session-expired"));
      if (!response.ok) throw new Agent2MemoryError(`上下文请求未完成 (${response.status})`, response.status);
      return validateSessionMemory(await response.json(), projectId, sessionId);
    })()]);
  } finally { clearTimeout(timer); options.signal?.removeEventListener("abort", cancel); controller.abort(); }
}

export function getAgent2SessionMemory(projectId: string, sessionId: string, options: RequestOptions = {}) {
  return memoryRequest(projectId, sessionId, "", { cache: "no-store" }, options);
}

async function mutateAgent2SessionMemory(
  projectId: string,
  sessionId: string,
  resultId: string,
  method: "POST" | "DELETE",
  options: RequestOptions,
): Promise<Agent2SessionMemory> {
  return memoryRequest(projectId, sessionId, `/pinned-results/${encodeURIComponent(resultId)}`, { method }, options);
}

export const pinAgent2Result = (projectId: string, sessionId: string, resultId: string, options: RequestOptions = {}) =>
  mutateAgent2SessionMemory(projectId, sessionId, resultId, "POST", options);

export const unpinAgent2Result = (projectId: string, sessionId: string, resultId: string, options: RequestOptions = {}) =>
  mutateAgent2SessionMemory(projectId, sessionId, resultId, "DELETE", options);

export type ScientificObjectMemoryRef = {
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
  options: RequestOptions,
): Promise<Agent2SessionMemory> {
  if (objectRef.project_id !== projectId || !objectRef.object_id || !objectRef.version_id || !objectRef.object_type) throw new Agent2MemoryError("来源与当前项目不匹配。", 400);
  return memoryRequest(projectId, sessionId, "/pinned-objects",
    {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ object_ref: objectRef }),
    }, options,
  );
}

export const pinAgent2Object = (
  projectId: string,
  sessionId: string,
  objectRef: ScientificObjectMemoryRef,
  options: RequestOptions = {},
) => mutateAgent2SessionObjectMemory(projectId, sessionId, objectRef, "POST", options);

export const unpinAgent2Object = (
  projectId: string,
  sessionId: string,
  objectRef: ScientificObjectMemoryRef,
  options: RequestOptions = {},
) => mutateAgent2SessionObjectMemory(projectId, sessionId, objectRef, "DELETE", options);
