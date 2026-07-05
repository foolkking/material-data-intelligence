export type PlannerJobRequest = {
  userPrompt: string;
  projectId: string;
  datasetId: string;
  profileId?: string;
  enqueue: boolean;
  provider?: string;
  baseUrl?: string;
  model?: string;
  secretId?: string;
  temperature?: number;
  maxTokens?: number;
  timeoutSeconds?: number;
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
    displayTarget?: string;
  };
};

export type AnalysisPlan = {
  schemaVersion?: string;
  goal?: string;
  datasetId?: string;
  profileId?: string;
  toolRegistryVersion?: string;
  assumptions?: string[];
  warnings?: string[];
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
  planner_provider?: string | null;
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
  datasetId?: string;
  projectId?: string;
  name?: string;
  status?: string;
  fileCount?: number;
  objectCount?: number;
  profileId?: string;
};

export type DatasetDetail = DatasetOption & {
  demo?: boolean;
  files?: Array<Record<string, unknown>>;
};

export type DataProfileSummary = {
  id?: string;
  profileId?: string;
  datasetId?: string;
  datasetType?: string;
  version?: string;
  createdAt?: string;
  status?: string;
  profileGenerated?: boolean;
  tableSummary?: {
    nRows?: number;
    nColumns?: number;
    columns?: Array<{ name?: string; inferredRole?: string; dtype?: string }>;
    inferredTask?: string;
  };
  structureSummary?: {
    nStructures?: number;
    elements?: string[];
    formulaStats?: { total?: number; uniqueCount?: number };
  };
  objects?: Array<{ objectType?: string; count?: number }>;
};

export type DemoDatasetResult = DatasetDetail & {
  demo: boolean;
  profile: DataProfileSummary;
};

export type RuntimeHealth = Record<
  "api" | "database" | "redis" | "artifactStorage" | "worker" | "llmProvider",
  { status?: string; reason?: string; provider?: string; model?: string; backend?: string; service?: string }
>;

export type ProviderOption = {
  id: string;
  label: string;
  provider: string;
  baseUrl?: string;
  defaultModel?: string;
  requiresSecret?: boolean;
  description?: string;
};

export type ProviderStatus = {
  ok?: boolean;
  provider?: string;
  model?: string;
  status?: string;
  message?: string;
  redacted?: boolean;
};

export type ProviderResolveRequest = {
  provider: string;
  baseUrl?: string;
  model?: string;
  secretId?: string;
  temperature?: number;
  maxTokens?: number;
  timeoutSeconds?: number;
};

export type ProviderResolveResult = ProviderStatus & {
  willUseLiveProvider?: boolean;
  secretConfigured?: boolean;
  source?: string;
  errorType?: string;
  safeDetails?: string | null;
};

export type ProviderTestRequest = {
  provider: string;
  baseUrl?: string;
  model?: string;
  secretId?: string;
  temperature?: number;
  maxTokens?: number;
  timeoutSeconds?: number;
};

export type ProviderTestResult = {
  ok: boolean;
  provider?: string;
  model?: string;
  latencyMs?: number;
  validated?: boolean;
  message?: string;
  errorType?: string;
  safeDetails?: string;
  suggestions?: string[];
  redacted?: boolean;
};

export type SecretSummary = {
  id: string;
  secret_id?: string;
  alias?: string;
  provider?: string;
  created_at?: string;
  createdAt?: string;
  lastUsedAt?: string | null;
  status?: string;
  maskedPreview?: string;
};

export type CreateSecretRequest = {
  provider: string;
  alias?: string;
  value: string;
  type?: "api_key" | "base_url" | "custom";
};

export type UploadDatasetRequest = {
  projectId: string;
  datasetName: string;
  files: Array<{ fileName: string; content: string }>;
};

export type SafeErrorPayload = {
  ok?: false;
  errorType?: string;
  message?: string;
  safeDetails?: string;
  suggestions?: string[];
  redacted?: boolean;
  detail?: unknown;
};

export class PlannerApiError extends Error {
  status: number;
  details: SafeErrorPayload | unknown;
  errorType?: string;
  safeDetails?: string;
  suggestions: string[];
  redacted?: boolean;

  constructor(message: string, status: number, details: SafeErrorPayload | unknown) {
    super(message);
    this.name = "PlannerApiError";
    this.status = status;
    this.details = details;
    this.errorType = isSafeErrorPayload(details) ? details.errorType : undefined;
    this.safeDetails = isSafeErrorPayload(details) ? details.safeDetails : undefined;
    this.suggestions = isSafeErrorPayload(details) ? details.suggestions || [] : [];
    this.redacted = isSafeErrorPayload(details) ? details.redacted : undefined;
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

export async function getRuntimeHealth(): Promise<RuntimeHealth> {
  return apiFetch<RuntimeHealth>("/health/runtime");
}

export async function listDatasets(): Promise<DatasetOption[]> {
  return apiFetch<DatasetOption[]>("/datasets");
}

export async function getDataset(datasetId: string): Promise<DatasetDetail> {
  return apiFetch<DatasetDetail>(`/datasets/${encodeURIComponent(datasetId)}`);
}

export async function loadDemoDataset(): Promise<DemoDatasetResult> {
  return apiFetch<DemoDatasetResult>("/datasets/demo", { method: "POST" });
}

export async function uploadDataset(payload: UploadDatasetRequest): Promise<DatasetDetail & { profile?: DataProfileSummary }> {
  return apiFetch<DatasetDetail & { profile?: DataProfileSummary }>("/datasets/upload", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function getDatasetProfile(datasetId: string): Promise<DataProfileSummary> {
  return apiFetch<DataProfileSummary>(`/datasets/${encodeURIComponent(datasetId)}/profile`);
}

export async function createDatasetProfile(datasetId: string): Promise<DataProfileSummary> {
  return apiFetch<DataProfileSummary>(`/datasets/${encodeURIComponent(datasetId)}/profile`, { method: "POST" });
}

export async function listPlannerProviders(): Promise<{ providers: ProviderOption[] }> {
  return apiFetch<{ providers: ProviderOption[] }>("/planner/providers");
}

export async function getPlannerProviderStatus(): Promise<ProviderStatus> {
  return apiFetch<ProviderStatus>("/planner/providers/status");
}

export async function resolvePlannerProvider(payload: ProviderResolveRequest): Promise<ProviderResolveResult> {
  return apiFetch<ProviderResolveResult>("/planner/providers/resolve", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function testPlannerProvider(payload: ProviderTestRequest): Promise<ProviderTestResult> {
  return apiFetch<ProviderTestResult>("/planner/providers/test", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function createSecret(payload: CreateSecretRequest): Promise<SecretSummary> {
  return apiFetch<SecretSummary>("/me/secrets", {
    method: "POST",
    body: JSON.stringify({ ...payload, type: payload.type || "api_key" })
  });
}

export async function listSecrets(): Promise<SecretSummary[]> {
  return apiFetch<SecretSummary[]>("/me/secrets");
}

export async function deleteSecret(secretId: string): Promise<boolean> {
  return apiFetch<boolean>(`/me/secrets/${encodeURIComponent(secretId)}`, { method: "DELETE" });
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
  if (isSafeErrorPayload(value)) {
    if (typeof value.message === "string") {
      return value.message;
    }
    const detail = value.detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail) && detail[0] && typeof detail[0] === "object" && "msg" in detail[0]) {
      return String((detail[0] as { msg?: unknown }).msg);
    }
  }
  return null;
}

function isSafeErrorPayload(value: unknown): value is SafeErrorPayload {
  return Boolean(value && typeof value === "object");
}
