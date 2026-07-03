export type PlannerJobRequest = {
  userPrompt: string;
  projectId: string;
  datasetId: string;
  profileId?: string;
  enqueue: boolean;
};

export type ValidationError = {
  code?: string;
  message?: string;
  detail?: unknown;
  field?: string;
  details?: unknown;
};

export type AnalysisStep = {
  stepId: string;
  toolId: string;
  purpose?: string;
  reason?: string;
  inputRefs?: Array<Record<string, unknown>>;
  params?: Record<string, unknown>;
  output?: {
    artifactTypes?: string[];
  };
};

export type AnalysisPlan = {
  schemaVersion?: string;
  goal?: string;
  datasetId?: string;
  profileId?: string;
  toolRegistryVersion?: string;
  steps?: AnalysisStep[];
  expectedArtifacts?: Array<Record<string, unknown>>;
};

export type PlannerJobCreateResult = {
  ok: boolean;
  job_id?: string | null;
  plan_id?: string | null;
  plan_hash?: string | null;
  validation_errors?: ValidationError[];
  plan?: AnalysisPlan | null;
  plan_source?: string;
  enqueued?: boolean;
  executed?: boolean;
};

export type PlannerJobDetail = {
  id?: string;
  jobId?: string;
  projectId?: string;
  datasetId?: string;
  status?: string;
  planId?: string | null;
  planHash?: string | null;
  planSource?: string | null;
  analysisPlan?: AnalysisPlan | null;
  validationStatus?: string | null;
  toolCallCount?: number;
  artifactCount?: number;
  eventCount?: number;
  provenance?: PlanProvenance;
};

export type AnalysisPlanRecord = {
  id?: string;
  planId?: string;
  projectId?: string;
  datasetId?: string;
  profileId?: string;
  jobId?: string | null;
  planSource?: string;
  plannerProvider?: string | null;
  analysisPlan?: AnalysisPlan;
  planHash?: string;
  validationStatus?: string;
  createdAt?: string;
  updatedAt?: string;
};

export type PlanProvenance = {
  planId?: string | null;
  planHash?: string | null;
  planSource?: string | null;
  loadedFrom?: string | null;
  binding?: string | null;
  toolPath?: string | null;
  fallbackUsed?: boolean | null;
};

export type JobEvent = {
  id?: string;
  jobId?: string;
  seq?: number;
  eventType?: string;
  status?: string;
  message?: string;
  progress?: number | null;
  payload?: Record<string, unknown>;
  createdAt?: string;
};

export type ToolCall = {
  id?: string;
  jobId?: string;
  stepId?: string;
  toolId?: string;
  status?: string;
  planId?: string | null;
  planHash?: string | null;
  params?: Record<string, unknown>;
  inputSummary?: string;
  outputSummary?: string;
  error?: unknown;
};

export type Artifact = {
  id?: string;
  artifactId?: string;
  jobId?: string;
  toolCallId?: string;
  type?: string;
  name?: string;
  storageKey?: string;
  storageProvider?: string;
  bucket?: string | null;
  createdAt?: string;
  planId?: string | null;
  planHash?: string | null;
  metadata?: Record<string, unknown>;
  provenance?: PlanProvenance | Record<string, unknown>;
};

export type JobResult = {
  jobId?: string;
  status?: string;
  planId?: string | null;
  planHash?: string | null;
  summary?: string;
  toolCallCount?: number;
  artifactCount?: number;
  artifacts?: Artifact[];
  provenance?: PlanProvenance;
};

export type DatasetOption = {
  id: string;
  projectId?: string;
  name?: string;
  status?: string;
};

export type DataProfileSummary = {
  id?: string;
  profileId?: string;
  datasetId?: string;
  datasetType?: string;
  version?: string;
  createdAt?: string;
};

export class PlannerApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details: unknown) {
    super(message);
    this.name = "PlannerApiError";
    this.status = status;
    this.details = details;
  }
}

const API_BASE = normalizeBaseUrl(process.env.NEXT_PUBLIC_MDI_API_BASE_URL || "http://localhost:8000");

export async function createPlannerJob(payload: PlannerJobRequest): Promise<PlannerJobCreateResult> {
  return apiFetch<PlannerJobCreateResult>("/planner/jobs", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function getPlannerJob(jobId: string): Promise<PlannerJobDetail> {
  return apiFetch<PlannerJobDetail>(`/planner/jobs/${encodeURIComponent(jobId)}`);
}

export async function getPlannerJobEvents(jobId: string, afterSeq = 0): Promise<JobEvent[]> {
  const query = afterSeq > 0 ? `?after_seq=${encodeURIComponent(String(afterSeq))}` : "";
  return apiFetch<JobEvent[]>(`/planner/jobs/${encodeURIComponent(jobId)}/events${query}`);
}

export function getPlannerJobEventsStreamUrl(jobId: string, afterSeq = 0): string {
  const query = afterSeq > 0 ? `?after_seq=${encodeURIComponent(String(afterSeq))}` : "";
  return `${API_BASE}/planner/jobs/${encodeURIComponent(jobId)}/events/stream${query}`;
}

export async function getPlannerJobToolCalls(jobId: string): Promise<ToolCall[]> {
  return apiFetch<ToolCall[]>(`/planner/jobs/${encodeURIComponent(jobId)}/tool-calls`);
}

export async function getPlannerJobArtifacts(jobId: string): Promise<Artifact[]> {
  return apiFetch<Artifact[]>(`/planner/jobs/${encodeURIComponent(jobId)}/artifacts`);
}

export async function getPlannerJobResult(jobId: string): Promise<JobResult> {
  return apiFetch<JobResult>(`/planner/jobs/${encodeURIComponent(jobId)}/result`);
}

export async function getAnalysisPlan(planId: string): Promise<AnalysisPlanRecord> {
  return apiFetch<AnalysisPlanRecord>(`/planner/analysis-plans/${encodeURIComponent(planId)}`);
}

export async function listDatasets(): Promise<DatasetOption[]> {
  return apiFetch<DatasetOption[]>("/datasets");
}

export async function getDatasetProfile(datasetId: string): Promise<DataProfileSummary> {
  return apiFetch<DataProfileSummary>(`/datasets/${encodeURIComponent(datasetId)}/profile`);
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {})
    }
  });
  const text = await response.text();
  const body = text ? safeParseJson(text) : null;
  if (!response.ok) {
    const message = errorMessage(body) || `Request failed with status ${response.status}`;
    throw new PlannerApiError(message, response.status, body);
  }
  return body as T;
}

function normalizeBaseUrl(value: string): string {
  return value.endsWith("/") ? value.slice(0, -1) : value;
}

function safeParseJson(value: string): unknown {
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

function errorMessage(value: unknown): string | null {
  if (value && typeof value === "object" && "detail" in value) {
    const detail = (value as { detail?: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail) && detail[0] && typeof detail[0] === "object" && "msg" in detail[0]) {
      return String((detail[0] as { msg?: unknown }).msg);
    }
  }
  return null;
}
