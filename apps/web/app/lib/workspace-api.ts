export type WorkspaceStatus =
  | "SOURCE_MISSING"
  | "UNSUPPORTED"
  | "LEGACY_READ_ONLY"
  | "STALE"
  | "RUNNING"
  | "PARTIAL_RESULTS"
  | "COMPLETE"
  | "FAILED"
  | "READY"
  | "INITIALIZING";

export type WorkspacePanelKind =
  | "OVERVIEW"
  | "DATA"
  | "PLAN"
  | "EXECUTION"
  | "SCIENTIFIC_RESULT"
  | "FINDINGS"
  | "EVIDENCE"
  | "PROVENANCE"
  | "REPORT";

export type WorkspacePanelState =
  | "NOT_APPLICABLE"
  | "READY_NOT_RUN"
  | "LOADING"
  | "PRODUCED"
  | "PARTIAL"
  | "UNAVAILABLE"
  | "FAILED"
  | "BLOCKED_BY_DEPENDENCY"
  | "STALE"
  | "CAP_EXCEEDED"
  | "CONTRACT_UNSUPPORTED"
  | "SOURCE_DELETED"
  | "PROFILE_AUTHORITY_UNAVAILABLE";

export type WorkspaceSelectionKind =
  | "DATASET_SAMPLE"
  | "MATERIAL_OBJECT"
  | "STRUCTURE"
  | "PERIODIC_SITE"
  | "LOCAL_ENVIRONMENT"
  | "COORDINATION_POLYHEDRON"
  | "POLYHEDRON_VERTEX"
  | "POLYHEDRON_FACE"
  | "TRAJECTORY_ATOM"
  | "TRAJECTORY_FRAME"
  | "PHONON_Q_POINT"
  | "PHONON_BRANCH"
  | "RECIPROCAL_POINT"
  | "VOLUMETRIC_FIELD"
  | "ARTIFACT"
  | "EVIDENCE_ITEM"
  | "CLAIM";

export type WorkspaceSourceKind =
  | "PROJECT"
  | "DATASET"
  | "PROFILE"
  | "INTENT"
  | "ELIGIBILITY_RESOLUTION"
  | "SELECTION_DECISION"
  | "PLAN"
  | "JOB"
  | "TOOL_CALL"
  | "ARTIFACT"
  | "DEPENDENCY_EXECUTION"
  | "INTERPRETATION"
  | "EVIDENCE_BUNDLE"
  | "REPORT"
  | "RECIPE";

export type WorkspaceWarning = {
  code: string;
  message: string;
  sourceId: string | null;
};

export type WorkspaceDurableMetadata = {
  tags: string[];
  note: string | null;
};

export type WorkspaceSourceRef = {
  kind: WorkspaceSourceKind;
  sourceId: string;
  sourceHash: string | null;
  contract: string | null;
  contractVersion: string | null;
  mediaType: string | null;
  projectId: string;
  jobId: string | null;
  toolCallId: string | null;
  stepId: string | null;
};

export type WorkspacePanelLayout = {
  region: "PRIMARY" | "SECONDARY" | "DETAILS" | "HIDDEN";
  order: number;
  width: number;
  height: number;
  collapsed: boolean;
};

export type WorkspacePanelPlacement = WorkspacePanelLayout & {
  panelId: string;
};

export type WorkspaceSelectionRef = {
  selectionSchemaVersion: "1.0";
  kind: WorkspaceSelectionKind;
  sourceScopeHash: string;
  projectId: string;
  datasetId: string | null;
  datasetVersion: string | null;
  jobId: string | null;
  objectId: string | null;
  sampleRef: string | null;
  structureId: string | null;
  siteId: string | null;
  environmentId: string | null;
  polyhedronId: string | null;
  vertexId: string | null;
  faceId: string | null;
  geometryReferenceId: string | null;
  trajectoryId: string | null;
  atomId: string | null;
  frameId: string | null;
  phononArtifactId: string | null;
  qPointId: string | null;
  branchId: string | null;
  reciprocalArtifactId: string | null;
  reciprocalPointId: string | null;
  segmentId: string | null;
  fieldId: string | null;
  regionId: string | null;
  artifactId: string | null;
  artifactChecksum: string | null;
  artifactContract: string | null;
  artifactVersion: string | null;
  toolCallId: string | null;
  bundleId: string | null;
  bundleHash: string | null;
  evidenceItemId: string | null;
  sourceArtifactId: string | null;
  sourceArtifactChecksum: string | null;
  fieldLocator: string | null;
  interpretationId: string | null;
  interpretationHash: string | null;
  claimId: string | null;
};

export type WorkspaceSelectionContext = {
  schemaVersion: "1.0";
  sourceScopeHash: string;
  primary: WorkspaceSelectionRef | null;
  secondary: WorkspaceSelectionRef[];
  propagation: "EXACT_COMPATIBLE_ONLY";
  compatibility: "EXACT" | "NOT_APPLICABLE" | "STALE" | "UNSUPPORTED";
  cleared: boolean;
};

export type WorkspaceLayoutState = {
  schemaVersion: "1.0";
  activePanelId: string | null;
  panelOrder: string[];
  visiblePanelIds: string[];
  panelLayouts: WorkspacePanelPlacement[];
  durableMetadata: WorkspaceDurableMetadata;
};

export type WorkspaceLayoutRevision = {
  schemaVersion: "1.0";
  workspaceId: string;
  revision: number;
  layout: WorkspaceLayoutState;
  selection: WorkspaceSelectionContext | null;
  semanticHash: string;
  createdBy: string;
  createdAt: string;
};

export type WorkspacePanel = {
  schemaVersion: "1.0";
  panelId: string;
  workspaceId: string;
  panelKind: WorkspacePanelKind;
  title: string;
  ordinal: number;
  visible: boolean;
  sourceRefs: WorkspaceSourceRef[];
  sourceReferenceHash: string;
  rendererContract: string;
  state: WorkspacePanelState;
  acceptedSelectionKinds: WorkspaceSelectionKind[];
  emittedSelectionKinds: WorkspaceSelectionKind[];
  evidenceRefs: string[];
  provenanceRefs: string[];
  capabilityRequirement: string | null;
  layout: WorkspacePanelLayout;
  mobilePresentationMode: "STACKED" | "FULL_WIDTH" | "HIDDEN";
  accessibleName: string;
  unsupportedReason: string | null;
  panelStateHash: string;
  contractProvenance: string;
};

export type ScientificWorkspace = {
  schemaVersion: "1.0";
  workspaceId: string;
  projectId: string;
  sourceJobId: string;
  sourceReferenceHash: string;
  datasetId: string | null;
  datasetVersion: string | null;
  profileId: string | null;
  profileSemanticHash: string | null;
  intentId: string | null;
  intentSemanticHash: string | null;
  planId: string | null;
  planHash: string | null;
  planSchemaVersion: "0.1" | "0.2" | null;
  title: string;
  activePanelId: string | null;
  pinnedSelection: WorkspaceSelectionContext | null;
  durableMetadata: WorkspaceDurableMetadata;
  panelIds: string[];
  currentLayoutRevision: number;
  revision: number;
  projectedStatus: WorkspaceStatus;
  historicalProjection: boolean;
  readOnly: boolean;
  warnings: WorkspaceWarning[];
  diagnostics: WorkspaceWarning[];
  artifactCount: number;
  toolCallCount: number;
  interpretationCount: number;
  reportCount: number;
  recipeCount: number;
  createdByKind: "USER";
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  executionAuthorized: false;
  scientificAuthority: false;
};

export type WorkspaceSourceSummary = {
  jobStatus: string | null;
  analysisPlanSchemaVersion: string | null;
  dependencyOutcome: string | null;
  artifactCount: number;
  toolCallCount: number;
  interpretationCount: number;
  reportCount: number;
  recipeCount: number;
  metadataOnly: true;
};

export type WorkspaceSnapshot = {
  workspace: ScientificWorkspace;
  panels: WorkspacePanel[];
  currentLayoutRevision: WorkspaceLayoutRevision | null;
  sourceSummary: WorkspaceSourceSummary;
  projectionHash: string;
};

export type WorkspaceSummary = {
  workspaceId: string;
  projectId: string;
  sourceJobId: string;
  title: string;
  projectedStatus: WorkspaceStatus;
  readOnly: boolean;
  analysisPlanSchemaVersion: string | null;
  panelCount: number;
  artifactCount: number;
  interpretationCount: number;
  revision: number;
  updatedAt: string;
  projectionHash: string;
};

export type WorkspaceAnalysisJobSummary = {
  jobId: string;
  projectId: string;
  datasetId: string | null;
  jobStatus: string | null;
  workspaceProjectionStatus: WorkspaceStatus;
  analysisPlanSchemaVersion: string | null;
  dependencyOutcome: string | null;
  artifactCount: number;
  interpretationCount: number;
  workspaceId: string | null;
  workspaceExists: boolean;
  createdAt: string | null;
  updatedAt: string | null;
};

export type WorkspacePage<T> = {
  items: T[];
  nextCursor: string | null;
  limit: number;
};

export type WorkspaceCreateRequest = {
  sourceJobId: string;
  title?: string;
};

export type WorkspacePanelVisibilityPatch = {
  panelId: string;
  visible: boolean;
};

export type WorkspacePatchRequest = {
  title?: string;
  activePanelId?: string | null;
  panelVisibility?: WorkspacePanelVisibilityPatch[];
  layout?: WorkspaceLayoutState;
  pinnedSelection?: WorkspaceSelectionContext | null;
};

export type WorkspaceApiResult<T> = {
  data: T | null;
  status: number;
  etag: string | null;
  idempotentReplay: boolean | null;
};

export type WorkspaceApiErrorDetail = {
  code: string;
  message: string;
  retryable: boolean;
};

export class WorkspaceApiError extends Error {
  readonly status: number;
  readonly detail: WorkspaceApiErrorDetail | null;

  constructor(message: string, status: number, detail: WorkspaceApiErrorDetail | null) {
    super(message);
    this.name = "WorkspaceApiError";
    this.status = status;
    this.detail = detail;
  }
}

const API_BASE = normalizeBaseUrl(
  process.env.NEXT_PUBLIC_MDI_API_BASE_URL || "http://localhost:8000",
);

export async function createWorkspace(
  payload: WorkspaceCreateRequest,
  idempotencyKey: string,
  signal?: AbortSignal,
): Promise<WorkspaceApiResult<WorkspaceSnapshot>> {
  return workspaceFetch<WorkspaceSnapshot>("/workspaces", {
    method: "POST",
    body: JSON.stringify(payload),
    signal,
    headers: { "Idempotency-Key": idempotencyKey },
  });
}

export async function getWorkspace(
  workspaceId: string,
  options: { etag?: string; signal?: AbortSignal } = {},
): Promise<WorkspaceApiResult<WorkspaceSnapshot>> {
  return workspaceFetch<WorkspaceSnapshot>(
    `/workspaces/${encodeURIComponent(workspaceId)}`,
    {
      method: "GET",
      signal: options.signal,
      headers: options.etag ? { "If-None-Match": quoteEtag(options.etag) } : undefined,
    },
  );
}

export async function patchWorkspace(
  workspaceId: string,
  etag: string,
  payload: WorkspacePatchRequest,
  signal?: AbortSignal,
): Promise<WorkspaceApiResult<WorkspaceSnapshot>> {
  return workspaceFetch<WorkspaceSnapshot>(
    `/workspaces/${encodeURIComponent(workspaceId)}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
      signal,
      headers: { "If-Match": quoteEtag(etag) },
    },
  );
}

export async function listProjectWorkspaces(
  projectId: string,
  options: { limit?: number; cursor?: string; signal?: AbortSignal } = {},
): Promise<WorkspaceApiResult<WorkspacePage<WorkspaceSummary>>> {
  return workspaceFetch<WorkspacePage<WorkspaceSummary>>(
    `/projects/${encodeURIComponent(projectId)}/workspaces${paginationQuery(options)}`,
    { method: "GET", signal: options.signal },
  );
}

export async function listWorkspaceAnalysisJobs(
  projectId: string,
  options: { limit?: number; cursor?: string; signal?: AbortSignal } = {},
): Promise<WorkspaceApiResult<WorkspacePage<WorkspaceAnalysisJobSummary>>> {
  return workspaceFetch<WorkspacePage<WorkspaceAnalysisJobSummary>>(
    `/projects/${encodeURIComponent(projectId)}/analysis-jobs${paginationQuery(options)}`,
    { method: "GET", signal: options.signal },
  );
}

export async function listWorkspacePanels(
  workspaceId: string,
  options: { etag?: string; signal?: AbortSignal } = {},
): Promise<WorkspaceApiResult<{ workspaceId: string; items: WorkspacePanel[] }>> {
  return workspaceFetch<{ workspaceId: string; items: WorkspacePanel[] }>(
    `/workspaces/${encodeURIComponent(workspaceId)}/panels`,
    {
      method: "GET",
      signal: options.signal,
      headers: options.etag ? { "If-None-Match": quoteEtag(options.etag) } : undefined,
    },
  );
}

export async function getWorkspacePanel(
  workspaceId: string,
  panelId: string,
  options: { etag?: string; signal?: AbortSignal } = {},
): Promise<WorkspaceApiResult<WorkspacePanel>> {
  return workspaceFetch<WorkspacePanel>(
    `/workspaces/${encodeURIComponent(workspaceId)}/panels/${encodeURIComponent(panelId)}`,
    {
      method: "GET",
      signal: options.signal,
      headers: options.etag ? { "If-None-Match": quoteEtag(options.etag) } : undefined,
    },
  );
}

export async function listWorkspaceLayoutRevisions(
  workspaceId: string,
  options: { etag?: string; signal?: AbortSignal } = {},
): Promise<WorkspaceApiResult<{ workspaceId: string; items: WorkspaceLayoutRevision[] }>> {
  return workspaceFetch<{ workspaceId: string; items: WorkspaceLayoutRevision[] }>(
    `/workspaces/${encodeURIComponent(workspaceId)}/layout-revisions`,
    {
      method: "GET",
      signal: options.signal,
      headers: options.etag ? { "If-None-Match": quoteEtag(options.etag) } : undefined,
    },
  );
}

export async function getWorkspaceLayoutRevision(
  workspaceId: string,
  revision: number,
  options: { etag?: string; signal?: AbortSignal } = {},
): Promise<WorkspaceApiResult<WorkspaceLayoutRevision>> {
  return workspaceFetch<WorkspaceLayoutRevision>(
    `/workspaces/${encodeURIComponent(workspaceId)}/layout-revisions/${encodeURIComponent(
      String(revision),
    )}`,
    {
      method: "GET",
      signal: options.signal,
      headers: options.etag ? { "If-None-Match": quoteEtag(options.etag) } : undefined,
    },
  );
}

async function workspaceFetch<T>(
  path: string,
  init: RequestInit,
): Promise<WorkspaceApiResult<T>> {
  const headers = new Headers(init.headers);
  if (init.body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "omit",
    headers,
  });
  const etag = response.headers.get("etag");
  const replayHeader = response.headers.get("x-idempotent-replay");
  const idempotentReplay =
    replayHeader === null ? null : replayHeader.toLowerCase() === "true";
  if (response.status === 304) {
    return { data: null, status: response.status, etag, idempotentReplay };
  }
  const text = await response.text();
  const body = text ? safeParseJson(text) : null;
  if (!response.ok) {
    const detail = errorDetail(body);
    throw new WorkspaceApiError(
      detail?.message || `Workspace request failed with status ${response.status}`,
      response.status,
      detail,
    );
  }
  return {
    data: body as T,
    status: response.status,
    etag,
    idempotentReplay,
  };
}

function paginationQuery(options: { limit?: number; cursor?: string }): string {
  const params = new URLSearchParams();
  if (options.limit !== undefined) {
    params.set("limit", String(options.limit));
  }
  if (options.cursor) {
    params.set("cursor", options.cursor);
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}

function normalizeBaseUrl(value: string): string {
  return value.endsWith("/") ? value.slice(0, -1) : value;
}

function quoteEtag(value: string): string {
  const normalized = value.startsWith('"') && value.endsWith('"') ? value.slice(1, -1) : value;
  return `"${normalized}"`;
}

function safeParseJson(value: string): unknown {
  try {
    return JSON.parse(value) as unknown;
  } catch {
    return null;
  }
}

function errorDetail(value: unknown): WorkspaceApiErrorDetail | null {
  if (!value || typeof value !== "object" || !("detail" in value)) {
    return null;
  }
  const detail = (value as { detail?: unknown }).detail;
  if (
    !detail ||
    typeof detail !== "object" ||
    !("code" in detail) ||
    !("message" in detail) ||
    typeof (detail as { code?: unknown }).code !== "string" ||
    typeof (detail as { message?: unknown }).message !== "string"
  ) {
    return null;
  }
  return {
    code: (detail as { code: string }).code,
    message: (detail as { message: string }).message,
    retryable:
      "retryable" in detail && typeof (detail as { retryable?: unknown }).retryable === "boolean"
        ? (detail as { retryable: boolean }).retryable
        : false,
  };
}
