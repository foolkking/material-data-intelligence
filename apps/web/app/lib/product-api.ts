const API_BASE = (process.env.NEXT_PUBLIC_MDI_API_BASE_URL || (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")).replace(/\/$/, "");

export type AuthUser = {
  id: string;
  displayName: string;
  email: string;
  roles: string[];
};

export type ResearchMessage = {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  payload?: Record<string, unknown>;
  created_at: string;
};

export type ResearchAssistantProjection = {
  phase: "pre_run" | "clarification" | "unsupported" | "failed" | "post_run";
  datasetName?: string;
  datasetId?: string;
  runId?: string;
  steps?: string[];
  findings?: string[];
  limitations?: string[];
  candidates?: string[];
  failureCode?: string;
  question?: string;
  provider?: string;
  model?: string;
  thinkingMode?: "quick" | "standard" | "deep";
  useProvider?: boolean;
};

export type ScopeCandidate = {
  dataset_id: string;
  profile_id?: string;
  name: string;
  semantics: string[];
};

export type ResearchSession = {
  id: string;
  project_id: string;
  projectId?: string;
  dataset_id?: string | null;
  datasetId?: string | null;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
  messages?: ResearchMessage[];
  runIds?: string[];
  runReferences?: Array<{ jobId: string; createdAt?: string | null }>;
};

export type ScopeResolution = {
  status: "READY" | "NEEDS_CLARIFICATION" | "UNSUPPORTED";
  dataset_id?: string;
  profile_id?: string;
  dataset_name?: string;
  reason?: string;
  question?: string;
  available_semantics?: string[];
  candidates?: ScopeCandidate[];
};

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      credentials: "include",
      headers: {
        ...(init.body ? { "Content-Type": "application/json" } : {}),
        ...(init.headers || {})
      }
    });
  } catch {
    throw new Error("服务暂时不可用，请检查连接后重试。");
  }
  if (!response.ok) {
    if (response.status === 401 && typeof window !== "undefined" && !path.startsWith("/auth/")) {
      window.dispatchEvent(new CustomEvent("mdi:session-expired"));
    }
    let message = response.status >= 500
      ? "服务暂时不可用，请稍后重试。"
      : `请求失败 (${response.status})`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (response.status < 500 && body.detail) message = body.detail;
    } catch {
      // Preserve the HTTP status when a non-JSON error is returned.
    }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const getAuthUser = () => request<AuthUser>("/auth/me");
export const login = (email: string, password: string) =>
  request<AuthUser>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
export const logout = () => request<void>("/auth/logout", { method: "POST" });

export const listResearchSessions = (projectId: string) =>
  request<ResearchSession[]>(`/projects/${encodeURIComponent(projectId)}/research-sessions`);
export const createResearchSession = (projectId: string, title = "新研究") =>
  request<ResearchSession>(`/projects/${encodeURIComponent(projectId)}/research-sessions`, {
    method: "POST",
    body: JSON.stringify({ title })
  });
export const getResearchSession = (sessionId: string) =>
  request<ResearchSession>(`/research-sessions/${encodeURIComponent(sessionId)}`);
export const createResearchMessage = (sessionId: string, content: string, datasetId?: string) =>
  request<ResearchMessage>(`/research-sessions/${encodeURIComponent(sessionId)}/messages`, {
    method: "POST",
    body: JSON.stringify({ content, ...(datasetId ? { datasetId } : {}) })
  });
export const createResearchAssistantProjection = (sessionId: string, projection: ResearchAssistantProjection) =>
  request<ResearchMessage>(`/research-sessions/${encodeURIComponent(sessionId)}/assistant-projections`, {
    method: "POST",
    body: JSON.stringify(projection)
  });
export const resolveResearchScope = async (projectId: string, question: string) => {
  type RawScopeResolution = Omit<ScopeResolution, "candidates"> & {
    datasetId?: string;
    profileId?: string;
    candidates?: Array<Record<string, unknown>>;
  };
  const result = await request<RawScopeResolution>(`/projects/${encodeURIComponent(projectId)}/research-scope`, {
    method: "POST",
    body: JSON.stringify({ question })
  });
  return {
    ...result,
    dataset_id: result.dataset_id || result.datasetId,
    profile_id: result.profile_id || result.profileId,
    candidates: result.candidates?.map((candidate) => ({
      dataset_id: String(candidate.dataset_id || candidate.datasetId || ""),
      profile_id: candidate.profile_id ? String(candidate.profile_id) : candidate.profileId ? String(candidate.profileId) : undefined,
      name: String(candidate.name || candidate.dataset_id || candidate.datasetId || "数据集"),
      semantics: Array.isArray(candidate.semantics) ? candidate.semantics.map(String) : [],
    })),
  } satisfies ScopeResolution;
};
