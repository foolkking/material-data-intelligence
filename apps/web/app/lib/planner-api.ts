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
  intentSchemaVersion?: "1.0";
  intentId?: string;
  selectedResourceIds?: string[];
  selectedTargetIds?: string[];
};

export type AnalysisIntentOption = { value: string; label: string; semanticId: string };
export type AnalysisIntentScientificIntent =
  | "dataset_overview"
  | "composition_analysis"
  | "property_distribution"
  | "dataset_comparison"
  | "composition_space"
  | "structure_analysis"
  | "trajectory_analysis"
  | "phonon_analysis"
  | "reciprocal_space_analysis"
  | "volumetric_analysis"
  | "ml_regression_evaluation"
  | "ml_uncertainty_evaluation"
  | "ml_classification_evaluation"
  | "sample_inspection"
  | "comparison"
  | "anomaly_candidate_review"
  | "visualization"
  | "report_or_export";
export type AnalysisIntentDesiredOutput =
  | "summary"
  | "metrics"
  | "plot"
  | "table"
  | "linked_samples"
  | "three_dimensional_view"
  | "comparison"
  | "warnings"
  | "recipe"
  | "report"
  | "downloadable_artifact";
export type AnalysisIntentCapabilityNeed =
  | "tabular_data"
  | "composition_data"
  | "material_property_data"
  | "comparison_groups"
  | "structure_resource"
  | "trajectory_resource"
  | "phonon_resource"
  | "reciprocal_space_resource"
  | "volumetric_resource"
  | "regression_semantics"
  | "uncertainty_semantics"
  | "classification_semantics"
  | "sample_identity";
export type AnalysisIntentQuestion = {
  questionId: string;
  code: string;
  prompt: string;
  type: "SELECT_ONE" | "SELECT_MANY" | "CONFIRM";
  options: AnalysisIntentOption[];
  required: boolean;
  bindsTo: string;
};
export type AnalysisIntent = {
  schemaVersion: "1.0";
  intentId: string;
  intentHash: string;
  datasetId: string;
  profileId: string;
  rawGoal: string;
  normalizedGoal: string;
  language: "zh" | "en" | "mixed" | "und";
  dataScope: {
    datasetId: string;
    datasetVersion: string;
    profileId: string;
    profileContractVersion: string;
    profileSemanticHash: string;
    resourceRefs: Array<{ objectId: string; objectType: string; objectHash: string; kind: string; origin: string }>;
    sampleIds: string[];
    modelIds: string[];
    groupIds: string[];
    origin: "USER_EXPLICIT" | "PROFILE_EXACT" | "CLARIFICATION_ANSWER";
  };
  scientificIntents: AnalysisIntentScientificIntent[];
  targetSemantics: Array<{ semanticId: string; role: string; objectId: string; column?: string | null; unit?: string | null; groupId?: string | null; seriesId?: string | null; origin: string }>;
  desiredOutputs: AnalysisIntentDesiredOutput[];
  constraints: {
    includeResourceIds: string[];
    excludeResourceIds: string[];
    includeScientificIntents: AnalysisIntentScientificIntent[];
    excludeScientificIntents: AnalysisIntentScientificIntent[];
    targetIds: string[];
    modelIds: string[];
    groupIds: string[];
    outputPreferences: AnalysisIntentDesiredOutput[];
    maxAnalyses?: number | null;
    maxToolCalls?: number | null;
    timePreference?: "FAST" | "BALANCED" | "THOROUGH" | null;
    costPreference?: "LOW" | "BALANCED" | null;
    clarificationAllowed: boolean;
    descriptiveOnly: boolean;
    forbidDerivedInterpretation: boolean;
  };
  requiredCapabilityNeeds: AnalysisIntentCapabilityNeed[];
  optionalCapabilityNeeds: AnalysisIntentCapabilityNeed[];
  ambiguities: Array<{ code: string; field: string; message: string; candidates: AnalysisIntentOption[]; blocking: boolean; source: string }>;
  missingFacts: Array<{ code: string; field: string; message: string; source: string; boundary: string }>;
  unsupportedReasons: Array<{ code: string; field: string; message: string; source: string; boundary: string }>;
  outcome: "READY" | "NEEDS_CLARIFICATION" | "UNSUPPORTED";
  clarification: { round: 0 | 1; maxRounds: 1; maxQuestionsPerRound: 3; questions: AnalysisIntentQuestion[]; answers: Array<{ questionId: string; selectedValues: string[] }> };
  provenance: { provider: "deterministic_mock" | "openai_compatible"; model: string; promptVersion: string; createdAt: string; parentIntentId?: string | null; answerBindings: Array<{ questionId: string; selectedValues: string[] }> };
  warnings: Array<{ code: string; field: string; message: string; source: string; boundary: string }>;
};

export type PlannerIntentResult = {
  ok: boolean;
  intent_id?: string | null;
  outcome?: AnalysisIntent["outcome"] | null;
  intent?: AnalysisIntent | null;
  error_code?: string | null;
  errors?: ValidationError[];
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
  intent_id?: string | null;
  intent_outcome?: AnalysisIntent["outcome"] | null;
  intent?: AnalysisIntent | null;
  error_code?: string | null;
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
  intentId?: string | null;
  intentOutcome?: AnalysisIntent["outcome"] | null;
  analysisIntent?: AnalysisIntent | null;
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
  downloadUrl?: string;
  storageKey?: string;
  sizeBytes?: number;
  contentType?: string;
  contentHash?: string;
  sha256?: string | null;
  storageProvider?: string;
  bucket?: string | null;
  createdAt?: string;
  planId?: string | null;
  planHash?: string | null;
  metadata?: Record<string, unknown>;
  provenance?: PlanProvenance | Record<string, unknown>;
  content?: unknown;
  payload?: unknown;
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
  objects?: Array<{ objectType?: string; count?: number; objectHash?: string }>;
  profileContractVersion?: "2.0";
  semanticRulesVersion?: string;
  semanticHash?: string;
  semanticColumns?: Array<{
    objectId?: string;
    column?: string;
    dtype?: string;
    roles?: Array<{ role?: string; authority?: string; groupId?: string; details?: Record<string, unknown> }>;
    ambiguities?: string[];
  }>;
  semanticGroups?: Array<{
    groupId?: string;
    kind?: string;
    status?: "COMPLETE" | "INCOMPLETE" | "AMBIGUOUS";
    targetColumns?: string[];
    predictionColumns?: string[];
    uncertaintyColumns?: string[];
    probabilityColumns?: string[];
    seriesBindings?: Array<{
      seriesId?: string;
      predictionColumn?: string;
      uncertaintyColumns?: string[];
    }>;
    reasons?: string[];
  }>;
  resourceSemantics?: Array<{ kind?: string; capabilities?: string[]; warnings?: string[] }>;
  analysisReadiness?: Array<{
    capability?: string;
    dataStatus?: "READY" | "MISSING_REQUIRED_DATA" | "AMBIGUOUS" | "UNSUPPORTED_DATA_KIND";
    platformStatus?: "AVAILABLE" | "NOT_IMPLEMENTED" | "NOT_EVALUATED";
    reasons?: string[];
  }>;
  profileCoverage?: {
    policy?: "complete" | "deterministic_bounded_sample";
    rowsInspected?: number;
    totalRows?: number;
    columnsInspected?: number;
    totalColumns?: number;
    warnings?: string[];
  };
  qualityIssues?: Array<{ severity?: string; code?: string; message?: string }>;
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

export async function clarifyAnalysisIntent(
  intentId: string,
  expectedProfileSemanticHash: string,
  answers: Array<{ questionId: string; selectedValues: string[] }>,
): Promise<PlannerIntentResult> {
  return apiFetch<PlannerIntentResult>(`/planner/intents/${encodeURIComponent(intentId)}/clarification`, {
    method: "POST",
    body: JSON.stringify({ expectedProfileSemanticHash, answers }),
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

export async function getPlannerArtifactContent(
  jobId: string,
  artifactId: string,
  options: Readonly<{ signal?: AbortSignal; maximumBytes?: number }> = {},
): Promise<ArrayBuffer> {
  const maximumBytes = options.maximumBytes ?? 67_108_864;
  if (!Number.isSafeInteger(maximumBytes) || maximumBytes <= 0 || maximumBytes > 67_108_864) {
    throw new Error("ARTIFACT_CONTENT_LIMIT_INVALID");
  }
  const response = await fetch(
    `${API_BASE}/planner/jobs/${encodeURIComponent(jobId)}/artifacts/${encodeURIComponent(artifactId)}/content`,
    { method: "GET", signal: options.signal, credentials: "omit" },
  );
  if (!response.ok) throw new Error("ARTIFACT_CONTENT_LOAD_FAILED");
  const declared = Number(response.headers.get("content-length") ?? response.headers.get("x-content-length-validated"));
  if (!Number.isSafeInteger(declared) || declared <= 0 || declared > maximumBytes) {
    throw new Error("ARTIFACT_CONTENT_LIMIT_EXCEEDED");
  }
  const content = await response.arrayBuffer();
  if (content.byteLength !== declared || content.byteLength > maximumBytes) {
    throw new Error("ARTIFACT_CONTENT_BYTE_MISMATCH");
  }
  return content;
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
  const result = await apiFetch<DatasetOption[] | { value: DatasetOption[] }>("/datasets");
  return Array.isArray(result) ? result : result.value;
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
  const result = await apiFetch<SecretSummary[] | { value: SecretSummary[] }>("/me/secrets");
  return Array.isArray(result) ? result : result.value;
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
  return unwrapFastApiListResponse(body) as T;
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

function unwrapFastApiListResponse(value: unknown): unknown {
  if (
    value &&
    typeof value === "object" &&
    !Array.isArray(value) &&
    "value" in value &&
    !("ok" in value) &&
    Array.isArray((value as { value?: unknown }).value)
  ) {
    return (value as { value: unknown[] }).value;
  }
  return value;
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
