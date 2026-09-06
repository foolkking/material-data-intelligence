import { invalidateProductDirectories, invalidateProjectHistory } from "./planner-api";

const API_BASE = (
  process.env.NEXT_PUBLIC_MDI_API_BASE_URL ||
  (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")
).replace(/\/$/, "");

export type AuthUser = {
  id: string;
  displayName: string;
  email: string;
  roles: string[];
  platformRole?: "USER" | "PLATFORM_ADMIN";
};

export type AuthSession = {
  id: string;
  createdAt: string;
  lastSeenAt: string;
  expiresAt: string;
  isCurrent: boolean;
};

export type PlatformAdminOverview = {
  schemaVersion: string;
  counts: {
    users: number;
    activeUsers: number;
    platformAdmins: number;
    projects: number;
    activeSessions: number;
  };
  operations: {
    status?: string | null;
    capturedAt?: string | null;
    alertSummary?: Record<string, unknown>;
    alertsSchemaVersion?: string | null;
    alerts?: Array<{
      code: string;
      severity: "WARNING" | "CRITICAL";
      component: string;
      observed: unknown;
      threshold: unknown;
      message: string;
      runbook?: {
        id?: string;
        reference?: string;
        operatorAction?: string;
        recheckCommand?: string;
      };
    }>;
    database?: Record<string, unknown>;
    queues?: Record<string, unknown>;
    artifactStorage?: Record<string, unknown>;
    resourceGovernance?: Record<string, unknown>;
  };
};

export type PlatformAdminUser = {
  id: string;
  email: string;
  displayName: string;
  platformRole: "USER" | "PLATFORM_ADMIN";
  isActive: boolean;
  projectCount: number;
  activeSessionCount: number;
  createdAt: string;
  updatedAt: string;
};

export type PlatformAdminAuditItem = {
  id: string;
  actor: {
    id?: string | null;
    email?: string | null;
  };
  action: string;
  targetType: string;
  targetId: string;
  metadata: Record<string, unknown>;
  createdAt: string;
};

export type PlatformAdminProject = {
  id: string;
  name: string;
  description: string;
  owner: {
    id: string;
    email: string;
    displayName: string;
  };
  memberCount: number;
  createdAt: string;
  updatedAt: string;
};

export type PlatformAdminProjectMember = {
  userId: string;
  email: string;
  displayName: string;
  role: "owner" | "admin" | "researcher" | "viewer";
  isActive: boolean;
  createdAt: string;
};

export type PlatformInvitation = {
  id: string;
  email: string;
  displayName: string;
  expiresAt: string;
  activationToken: string;
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
  pinned?: boolean;
  created_at: string;
  updated_at: string;
  messages?: ResearchMessage[];
  runIds?: string[];
  runReferences?: Array<{
    jobId: string;
    createdAt?: string | null;
    researchTurnId?: string | null;
  }>;
  retentionPolicy?: {
    schemaVersion: string;
    automaticPurge: "ENABLED" | "DISABLED";
    referencedProvenance: string;
    unreferencedTrash: string;
    manualPurge: "SERVER_ZERO_DEPENDENCY_ONLY" | "NOT_SUPPORTED_FOR_ENTITY";
    manualPurgeRequiresZeroDependencies: boolean;
  };
};

export type ResearchSessionDependencyImpact = {
  entity: "research_session";
  entityId: string;
  displayName: string;
  canDelete: false;
  dependencyCount: number;
  dependencies: Array<{ kind: string; label: string; count: number }>;
  retentionPolicy?: {
    schemaVersion: string;
    automaticPurge: "ENABLED" | "DISABLED";
    referencedProvenance: string;
    unreferencedTrash: string;
    manualPurge: "SERVER_ZERO_DEPENDENCY_ONLY" | "NOT_SUPPORTED_FOR_ENTITY";
    manualPurgeRequiresZeroDependencies: boolean;
  };
  impact: {
    removedFromActiveDiscovery: boolean;
    historicalProvenanceProtected: boolean;
    historicalResearchRemainsAccessible: boolean;
    scientificSnapshotMutated: false;
  };
};

export const getResearchSessionDependencyImpact = (sessionId: string) =>
  request<ResearchSessionDependencyImpact>(
    `/research-sessions/${encodeURIComponent(sessionId)}/dependency-impact`,
  );

export type ResearchSessionBulkAction =
  | "PIN"
  | "UNPIN"
  | "ARCHIVE"
  | "RESTORE"
  | "TRASH";

export type SavedProductSearchType =
  | "project"
  | "dataset"
  | "scientific_object"
  | "research"
  | "report"
  | "result";

export type SavedProductSearch = {
  id: string;
  name: string;
  query: string;
  type?: SavedProductSearchType | null;
  project?: string | null;
  status: "active" | "archived" | "trashed" | "all";
  createdAt?: string | null;
  updatedAt?: string | null;
};

export type SavedProductSearchExecution = {
  savedSearch: SavedProductSearch;
  query: string;
  count: number;
  truncated?: boolean;
  nextCursor?: string | null;
  items: Array<{
    kind: SavedProductSearchType;
    id: string;
    projectId: string;
    title: string;
    subtitle: string;
    href: string;
    researchTurnId?: string | null;
    status?: string | null;
    updatedAt?: string | null;
  }>;
};

export type NotificationReadState = {
  projectId: string;
  jobId: string;
  read: boolean;
  readAt: string | null;
  notificationUpdatedAt: string | null;
};

export type NotificationReadStateCollection = {
  schemaVersion: "NotificationReadState/1.0";
  items: NotificationReadState[];
  count: number;
};

export type ScopeResolution = {
  status: "READY" | "NEEDS_CLARIFICATION" | "UNSUPPORTED";
  dataset_id?: string;
  profile_id?: string;
  dataset_name?: string;
  scientific_object_ref?: {
    object_id: string;
    version_id: string;
    project_id: string;
    object_type: string;
    display_name?: string;
  };
  dataset_resource_id?: string;
  reason?: string;
  question?: string;
  available_semantics?: string[];
  candidates?: ScopeCandidate[];
};

/**
 * Convert FastAPI/Pydantic detail payloads into a bounded product message.
 * Validation details are frequently arrays/objects; interpolating them
 * directly produces "[object Object]" and leaks implementation-shaped data.
 */
export function safeApiDetail(detail: unknown): string | null {
  if (typeof detail === "string") {
    const value = detail.trim();
    return value || null;
  }
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (!item || typeof item !== "object") return null;
        const candidate = item as Record<string, unknown>;
        return typeof candidate.msg === "string"
          ? candidate.msg.trim()
          : typeof candidate.message === "string"
            ? candidate.message.trim()
            : null;
      })
      .filter((item): item is string => Boolean(item))
      .slice(0, 2);
    return messages.length ? messages.join("；") : "请求输入不完整，请检查后重试。";
  }
  if (detail && typeof detail === "object") {
    const candidate = detail as Record<string, unknown>;
    for (const key of ["message", "error", "reason"]) {
      if (typeof candidate[key] === "string" && candidate[key].trim()) {
        return candidate[key].trim();
      }
    }
  }
  return null;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      credentials: "include",
      headers: {
        ...(init.body ? { "Content-Type": "application/json" } : {}),
        ...(init.headers || {}),
      },
    });
  } catch {
    throw new Error("服务暂时不可用，请检查连接后重试。");
  }
  if (!response.ok) {
    if (response.status === 401) {
      authUserCache = undefined;
      // Read projections are authorized per session.  Never let a cached
      // project/history directory survive an expired session and become
      // visible after another user signs in in the same SPA instance.
      invalidateProductDirectories();
      invalidateProjectHistory();
    }
    if (
      response.status === 401 &&
      typeof window !== "undefined" &&
      !path.startsWith("/auth/")
    ) {
      window.dispatchEvent(new CustomEvent("mdi:session-expired"));
    }
    let message =
      response.status >= 500
        ? "服务暂时不可用，请稍后重试。"
        : `请求失败 (${response.status})`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      const detail = safeApiDetail(body.detail);
      if (response.status < 500 && detail) message = detail;
    } catch {
      // Preserve the HTTP status when a non-JSON error is returned.
    }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

let authUserCache: AuthUser | null | undefined;
let authUserRequest: Promise<AuthUser> | null = null;

export const getAuthUser = () => {
  if (authUserCache) return Promise.resolve(authUserCache);
  if (authUserRequest) return authUserRequest;
  authUserRequest = request<AuthUser>("/auth/me")
    .then((user) => {
      authUserCache = user;
      return user;
    })
    .catch((error) => {
      authUserCache = undefined;
      throw error;
    })
    .finally(() => {
      authUserRequest = null;
    });
  return authUserRequest;
};

export const login = (email: string, password: string) =>
  request<AuthUser>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  }).then((user) => {
    invalidateProductDirectories();
    invalidateProjectHistory();
    authUserCache = user;
    return user;
  });
export const logout = () =>
  request<void>("/auth/logout", { method: "POST" }).finally(() => {
    authUserCache = undefined;
    invalidateProductDirectories();
    invalidateProjectHistory();
  });
export const updateAuthProfile = (displayName: string) =>
  request<AuthUser>("/auth/profile", {
    method: "PATCH",
    body: JSON.stringify({ displayName }),
  }).then((user) => {
    invalidateProductDirectories();
    invalidateProjectHistory();
    authUserCache = user;
    return user;
  });
export const listAuthSessions = () =>
  request<{ items: AuthSession[]; count: number }>("/auth/sessions");
export const revokeAuthSession = (sessionId: string) =>
  request<{ ok: boolean }>(
    `/auth/sessions/${encodeURIComponent(sessionId)}`,
    { method: "DELETE" },
  );
export const revokeOtherAuthSessions = () =>
  request<{ ok: boolean; revokedCount: number }>(
    "/auth/sessions/revoke-others",
    { method: "POST" },
  );
export const changeAuthPassword = (
  currentPassword: string,
  newPassword: string,
) =>
  request<{ ok: boolean; otherSessionsRevoked: number }>(
    "/auth/change-password",
    {
      method: "POST",
      body: JSON.stringify({ currentPassword, newPassword }),
    },
  );
export const deactivateAuthAccount = (
  password: string,
  confirmEmail: string,
) =>
  request<{
    ok: boolean;
    provenanceRetained: boolean;
    retentionPolicy: {
      schemaVersion: string;
      automaticPurge: "ENABLED" | "DISABLED";
      referencedProvenance: string;
      unreferencedTrash: string;
      manualPurge: "SERVER_ZERO_DEPENDENCY_ONLY" | "NOT_SUPPORTED_FOR_ENTITY";
      manualPurgeRequiresZeroDependencies: boolean;
    };
  }>("/auth/deactivate", {
    method: "POST",
    body: JSON.stringify({ password, confirmEmail }),
  }).finally(() => {
    authUserCache = undefined;
    invalidateProductDirectories();
    invalidateProjectHistory();
  });
export const activateAuthAccount = (
  token: string,
  password: string,
  displayName?: string,
) =>
  request<AuthUser>("/auth/activate", {
    method: "POST",
    body: JSON.stringify({
      token,
      password,
      ...(displayName?.trim() ? { displayName: displayName.trim() } : {}),
    }),
  }).then((user) => {
    invalidateProductDirectories();
    invalidateProjectHistory();
    authUserCache = user;
    return user;
  });

export const getPlatformAdminOverview = () =>
  request<PlatformAdminOverview>("/api/admin/overview");
export const createPlatformInvitation = (
  email: string,
  displayName: string,
  expiresInDays = 7,
) =>
  request<PlatformInvitation>("/api/admin/invitations", {
    method: "POST",
    body: JSON.stringify({ email, displayName, expiresInDays }),
  });
export const listPlatformAdminUsers = (options?: Readonly<{
  query?: string;
  status?: "ALL" | "ACTIVE" | "INACTIVE";
  role?: "ALL" | "USER" | "PLATFORM_ADMIN";
  limit?: number;
  offset?: number;
}>) => {
  const params = new URLSearchParams();
  if (options?.query?.trim()) params.set("q", options.query.trim());
  if (options?.status && options.status !== "ALL")
    params.set("status", options.status);
  if (options?.role && options.role !== "ALL")
    params.set("role", options.role);
  if (options?.limit) params.set("limit", String(options.limit));
  if (options?.offset) params.set("offset", String(options.offset));
  const query = params.toString();
  return request<{
    items: PlatformAdminUser[];
    count: number;
    total: number;
    limit: number;
    offset: number;
  }>(`/api/admin/users${query ? `?${query}` : ""}`);
};
export const updatePlatformAdminUser = (
  userId: string,
  changes: Readonly<{
    platformRole?: "USER" | "PLATFORM_ADMIN";
    isActive?: boolean;
  }>,
) =>
  request<PlatformAdminUser>(
    `/api/admin/users/${encodeURIComponent(userId)}`,
    {
      method: "PATCH",
      body: JSON.stringify(changes),
    },
  );
export const listPlatformAdminAudit = (limit = 30) =>
  request<{ items: PlatformAdminAuditItem[]; count: number }>(
    `/api/admin/audit?limit=${encodeURIComponent(String(limit))}`,
  );
export const listPlatformAdminProjects = (options?: Readonly<{ query?: string; limit?: number; offset?: number }>) => {
  const params = new URLSearchParams();
  if (options?.query?.trim()) params.set("q", options.query.trim());
  if (options?.limit) params.set("limit", String(options.limit));
  if (options?.offset) params.set("offset", String(options.offset));
  const query = params.toString();
  return request<{
    items: PlatformAdminProject[];
    count: number;
    total: number;
    limit: number;
    offset: number;
  }>(`/api/admin/projects${query ? `?${query}` : ""}`);
};
export const listPlatformAdminProjectMembers = (projectId: string) =>
  request<{
    project: { id: string; name: string; ownerId: string };
    items: PlatformAdminProjectMember[];
    count: number;
  }>(`/api/admin/projects/${encodeURIComponent(projectId)}/members`);
export const updatePlatformAdminProjectMember = (
  projectId: string,
  userId: string,
  role: PlatformAdminProjectMember["role"],
) =>
  request<{ projectId: string; userId: string; role: PlatformAdminProjectMember["role"] }>(
    `/api/admin/projects/${encodeURIComponent(projectId)}/members/${encodeURIComponent(userId)}`,
    { method: "PUT", body: JSON.stringify({ role }) },
  );
export const removePlatformAdminProjectMember = (projectId: string, userId: string) =>
  request<{ projectId: string; userId: string; removed: boolean }>(
    `/api/admin/projects/${encodeURIComponent(projectId)}/members/${encodeURIComponent(userId)}`,
    { method: "DELETE" },
  );

// Session mutations invalidate this cache. A 30-second read window lets Data,
// Viewer, History and Research share the same authorized session inventory
// during normal product navigation without making lifecycle updates stale.
const RESEARCH_SESSION_LIST_WARM_TTL_MS = 30_000;
const researchSessionListRequests = new Map<
  string,
  { expiresAt: number; promise: Promise<ResearchSession[]> }
>();

export const invalidateResearchSessionList = (projectId?: string) => {
  if (projectId) researchSessionListRequests.delete(projectId);
  else researchSessionListRequests.clear();
};

export const listResearchSessions = (projectId: string) => {
  const cached = researchSessionListRequests.get(projectId);
  if (cached && cached.expiresAt > Date.now()) return cached.promise;
  const promise = request<ResearchSession[]>(
    `/projects/${encodeURIComponent(projectId)}/research-sessions`,
  ).catch((error) => {
    researchSessionListRequests.delete(projectId);
    throw error;
  });
  researchSessionListRequests.set(projectId, {
    expiresAt: Date.now() + RESEARCH_SESSION_LIST_WARM_TTL_MS,
    promise,
  });
  return promise;
};
export const createResearchSession = (
  projectId: string,
  title = "新研究",
  datasetId?: string,
) =>
  request<ResearchSession>(
    `/projects/${encodeURIComponent(projectId)}/research-sessions`,
    {
      method: "POST",
      body: JSON.stringify({ title, ...(datasetId ? { datasetId } : {}) }),
    },
  ).then((session) => {
    invalidateResearchSessionList(projectId);
    return session;
  });
export const getResearchSession = (sessionId: string) =>
  request<ResearchSession>(
    `/research-sessions/${encodeURIComponent(sessionId)}`,
  );
export const updateResearchSession = (
  sessionId: string,
  changes: Readonly<{
    title?: string;
    pinned?: boolean;
    lifecycle?: "ACTIVE" | "ARCHIVED" | "TRASHED";
  }>,
) =>
  request<ResearchSession>(
    `/research-sessions/${encodeURIComponent(sessionId)}`,
    {
      method: "PATCH",
      body: JSON.stringify(changes),
    },
  ).then((session) => {
    invalidateResearchSessionList();
    return session;
  });
export const bulkUpdateResearchSessions = (
  projectId: string,
  sessionIds: string[],
  action: ResearchSessionBulkAction,
) =>
  request<{
    action: ResearchSessionBulkAction;
    sessionIds: string[];
    count: number;
  }>(
    `/projects/${encodeURIComponent(projectId)}/research-sessions/bulk`,
    {
      method: "POST",
      body: JSON.stringify({ sessionIds, action }),
    },
  ).then((result) => {
    invalidateResearchSessionList(projectId);
    return result;
  });
export const listSavedProductSearches = () =>
  request<SavedProductSearch[]>("/saved-searches");
export const createSavedProductSearch = (
  savedSearch: Readonly<{
    name: string;
    query: string;
    type?: SavedProductSearchType;
    project?: string;
    status?: "active" | "archived" | "trashed" | "all";
  }>,
) =>
  request<SavedProductSearch>("/saved-searches", {
    method: "POST",
    body: JSON.stringify(savedSearch),
  });
export const updateSavedProductSearch = (
  savedSearchId: string,
  changes: Readonly<{
    name?: string;
    query?: string;
    type?: SavedProductSearchType | null;
    project?: string | null;
    status?: "active" | "archived" | "trashed" | "all";
  }>,
) =>
  request<SavedProductSearch>(
    `/saved-searches/${encodeURIComponent(savedSearchId)}`,
    {
      method: "PATCH",
      body: JSON.stringify(changes),
    },
  );
export const deleteSavedProductSearch = (savedSearchId: string) =>
  request<{ id: string; deleted: boolean }>(
    `/saved-searches/${encodeURIComponent(savedSearchId)}`,
    { method: "DELETE" },
  );
export const executeSavedProductSearch = (
  savedSearchId: string,
  limit = 40,
) =>
  request<SavedProductSearchExecution>(
    `/saved-searches/${encodeURIComponent(savedSearchId)}/execute`,
    {
      method: "POST",
      body: JSON.stringify({ limit }),
    },
  );
export const listNotificationReadStates = () =>
  request<NotificationReadStateCollection>("/api/notifications/read-state");
export const updateNotificationReadState = (
  projectId: string,
  jobId: string,
  read: boolean,
) =>
  request<NotificationReadState>(
    `/api/notifications/${encodeURIComponent(projectId)}/${encodeURIComponent(jobId)}/read-state`,
    {
      method: "PATCH",
      body: JSON.stringify({ read }),
    },
  );
export const createResearchMessage = (
  sessionId: string,
  content: string,
  datasetId?: string,
) =>
  request<ResearchMessage>(
    `/research-sessions/${encodeURIComponent(sessionId)}/messages`,
    {
      method: "POST",
      body: JSON.stringify({ content, ...(datasetId ? { datasetId } : {}) }),
    },
  );
export const createResearchAssistantProjection = (
  sessionId: string,
  projection: ResearchAssistantProjection,
) =>
  request<ResearchMessage>(
    `/research-sessions/${encodeURIComponent(sessionId)}/assistant-projections`,
    {
      method: "POST",
      body: JSON.stringify(projection),
    },
  );
export const resolveResearchScope = async (
  projectId: string,
  question: string,
) => {
  type RawScopeResolution = Omit<ScopeResolution, "candidates"> & {
    datasetId?: string;
    profileId?: string;
    candidates?: Array<Record<string, unknown>>;
  };
  const result = await request<RawScopeResolution>(
    `/projects/${encodeURIComponent(projectId)}/research-scope`,
    {
      method: "POST",
      body: JSON.stringify({ question }),
    },
  );
  return {
    ...result,
    dataset_id: result.dataset_id || result.datasetId,
    profile_id: result.profile_id || result.profileId,
    candidates: result.candidates?.map((candidate) => ({
      dataset_id: String(candidate.dataset_id || candidate.datasetId || ""),
      profile_id: candidate.profile_id
        ? String(candidate.profile_id)
        : candidate.profileId
          ? String(candidate.profileId)
          : undefined,
      name: String(
        candidate.name ||
          candidate.dataset_id ||
          candidate.datasetId ||
          "数据集",
      ),
      semantics: Array.isArray(candidate.semantics)
        ? candidate.semantics.map(String)
        : [],
    })),
  } satisfies ScopeResolution;
};
