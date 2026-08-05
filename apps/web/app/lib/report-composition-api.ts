export type ReportSourceRole =
  | "REPORT_FIGURE_SOURCE"
  | "REPORT_TABLE_SOURCE"
  | "REPORT_FINDING_SOURCE"
  | "REPORT_EVIDENCE_SOURCE"
  | "REPORT_PROVENANCE_SOURCE"
  | "REPORT_DISCLOSURE_ONLY"
  | "REPORT_METADATA_ONLY"
  | "REPORT_UNSUPPORTED";

export type ReportSourceState =
  | "ELIGIBLE"
  | "MANDATORY"
  | "METADATA_ONLY"
  | "UNAVAILABLE"
  | "STALE"
  | "UNSUPPORTED"
  | "SOURCE_INTEGRITY_FAILED";

export type ReportSourceReference = {
  sourceKind: string;
  sourceId: string;
  sourceHash: string | null;
  contract: string | null;
  contractVersion: string | null;
  projectId: string;
  datasetId: string | null;
  datasetVersion: string | null;
  jobId: string;
  toolCallId: string | null;
  stepId: string | null;
  panelId: string | null;
  artifactId: string | null;
  artifactChecksum: string | null;
  interpretationId: string | null;
  claimId: string | null;
  evidenceItemId: string | null;
  role: ReportSourceRole;
  state: ReportSourceState;
  representation: "STATIC_FIGURE" | "BOUNDED_TABLE" | "CLAIM" | "EVIDENCE" | "PROVENANCE" | "DISCLOSURE" | "METADATA" | "NONE";
  fallback: string | null;
  reason: string | null;
};

export type ReportCompositionRequest = {
  schemaVersion: "1.0";
  workspaceId: string;
  expectedWorkspaceRevision: number;
  title: string;
  selectedPanelIds: string[];
  selectedArtifactIds: string[];
  selectedClaimIds: string[];
  selectedEvidenceItemIds: string[];
  itemOrder: string[];
  captions: Array<{ sourceId: string; text: string }>;
  exportFormats: Array<"json" | "markdown">;
};

export type ReportSection = {
  sectionId: string;
  title: string;
  status: "READY" | "LIMITED" | "UNAVAILABLE" | "EMPTY";
  items: string[];
};

export type ReportCompositionSnapshot = {
  schemaVersion: "1.0";
  reportId: string;
  reportHash: string;
  compositionHash: string;
  recipeId: string;
  workspaceId: string;
  workspaceRevision: number;
  projectId: string;
  datasetId: string | null;
  datasetVersion: string | null;
  sourceJobId: string;
  sourcePlanId: string | null;
  sourcePlanHash: string | null;
  sourcePlanSchemaVersion: "0.1" | "0.2" | null;
  title: string;
  analysisGoal: string;
  outcome: string;
  selectedSources: ReportSourceReference[];
  mandatoryDisclosures: ReportSourceReference[];
  sections: ReportSection[];
  warnings: string[];
  limitations: string[];
  executionAuthorized: false;
  scientificAuthority: false;
  createdAt: string;
};

export type RecipeReplayManifest = {
  schemaVersion: "1.0";
  recipeId: string;
  recipeHash: string;
  compositionHash: string;
  sourceReportId: string;
  sourceReportHash: string;
  workspaceId: string;
  workspaceRevision: number;
  projectId: string;
  datasetId: string | null;
  datasetVersion: string | null;
  datasetHash: string | null;
  profileId: string | null;
  profileVersion: string | null;
  profileHash: string | null;
  intentId: string | null;
  intentHash: string | null;
  eligibilityResolutionId: string | null;
  eligibilityResolutionHash: string | null;
  plannerDecisionId: string | null;
  plannerDecisionHash: string | null;
  analysisPlanId: string;
  analysisPlanHash: string;
  planSchemaVersion: "0.1" | "0.2";
  dependencyModel: "NONE_OR_SEQUENTIAL_INDEPENDENT" | "TYPED_ARTIFACT_BINDINGS";
  graphHash: string | null;
  steps: Array<{ stepId: string; toolId: string; toolVersion: string | null; adapterVersion: string | null; params: Record<string, unknown>; inputRefs: Array<Record<string, unknown>>; expectedOutputContracts: string[] }>;
  dependencyBindings: Array<Record<string, unknown>>;
  sourceResourceBindings: Array<Record<string, unknown>>;
  originalArtifacts: ReportSourceReference[];
  executionOutcome: string;
  providerProvenance: Record<string, unknown> | null;
  environmentProvenance: Record<string, unknown>;
  warnings: string[];
  limitations: string[];
  outcome: string;
  executionAuthorized: false;
  planCreated: false;
  jobCreated: false;
  queueMessageCreated: false;
  automaticReplay: false;
  createdAt: string;
};

export type ReportExportManifest = {
  schemaVersion: "1.0";
  exportId: string;
  exportHash: string;
  reportId: string;
  reportHash: string;
  recipeId: string;
  recipeHash: string;
  workspaceId: string;
  projectId: string;
  format: "json" | "markdown";
  rendererContract: "report_export.v1";
  sourceReferences: ReportSourceReference[];
  contentChecksum: string;
  byteSize: number;
  authorizationScope: string;
  omittedPayloadReasons: string[];
  coverage: string;
  executionAuthorized: false;
  generatedAt: string;
};

export type ReportSourceInventory = {
  schemaVersion: "1.0";
  workspaceId: string;
  workspaceRevision: number;
  workspaceProjectionHash: string;
  sources: ReportSourceReference[];
  mandatoryDisclosures: ReportSourceReference[];
  sourceCount: number;
  mandatoryDisclosureCount: number;
  artifactContractInventoryCount: number;
  metadataOnly: true;
  heavyArtifactPayloadRequests: 0;
  webglContexts: 0;
};

export type ReportCompositionPreview = {
  report: ReportCompositionSnapshot;
  recipe: RecipeReplayManifest;
  sourceCount: number;
  mandatoryDisclosureCount: number;
  predictedOutcome: string;
  persisted: false;
  noExecution: { planCreated: false; jobCreated: false; toolCallCreated: false; queueMessageCreated: false };
};

export type ReportFinalizeResult = {
  reportId: string;
  reportHash: string;
  recipeId: string;
  recipeHash: string;
  compositionHash: string;
  workspaceId: string;
  workspaceRevision: number;
  outcome: string;
  idempotentReplay: boolean;
  immutable: true;
  noExecution: { planCreated: false; jobCreated: false; toolCallCreated: false; queueMessageCreated: false };
};

export type ReportHistoryItem = {
  reportId: string;
  recipeId: string | null;
  version: string;
  title: string;
  reportHash: string | null;
  recipeHash: string | null;
  compositionHash: string | null;
  workspaceId: string | null;
  workspaceRevision: number | null;
  sourceJobId: string;
  outcome: string | null;
  createdAt: string | null;
  legacyReadOnly: boolean;
  exportFormats: Array<"json" | "markdown">;
};

export class ReportCompositionApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ReportCompositionApiError";
    this.status = status;
    this.code = code;
  }
}

const API_BASE = (process.env.NEXT_PUBLIC_MDI_API_BASE_URL || "http://localhost:8000").replace(/\/$/u, "");

export async function getReportCompositionSources(workspaceId: string, signal?: AbortSignal): Promise<ReportSourceInventory> {
  return requestJson(`/workspaces/${encodeURIComponent(workspaceId)}/report-composition/sources`, { method: "GET", signal });
}

export async function previewReportComposition(workspaceId: string, payload: ReportCompositionRequest, signal?: AbortSignal): Promise<ReportCompositionPreview> {
  return requestJson(`/workspaces/${encodeURIComponent(workspaceId)}/report-compositions/preview`, { method: "POST", body: JSON.stringify(payload), signal });
}

export async function finalizeReportComposition(workspaceId: string, payload: ReportCompositionRequest, idempotencyKey: string, signal?: AbortSignal): Promise<ReportFinalizeResult> {
  return requestJson(`/workspaces/${encodeURIComponent(workspaceId)}/report-compositions`, { method: "POST", body: JSON.stringify(payload), signal, headers: { "Idempotency-Key": idempotencyKey } });
}

export async function listReportCompositions(workspaceId: string, signal?: AbortSignal): Promise<{ workspaceId: string; items: ReportHistoryItem[]; count: number; immutableHistory: true }> {
  return requestJson(`/workspaces/${encodeURIComponent(workspaceId)}/report-compositions`, { method: "GET", signal });
}

export async function getReportComposition(workspaceId: string, reportId: string, signal?: AbortSignal): Promise<{ legacyReadOnly: boolean; report: ReportCompositionSnapshot | Record<string, unknown>; recipeId?: string }> {
  return requestJson(`/workspaces/${encodeURIComponent(workspaceId)}/report-compositions/${encodeURIComponent(reportId)}`, { method: "GET", signal });
}

export async function getReportCompositionRecipe(workspaceId: string, reportId: string, signal?: AbortSignal): Promise<{ legacyReadOnly: false; recipe: RecipeReplayManifest }> {
  return requestJson(`/workspaces/${encodeURIComponent(workspaceId)}/report-compositions/${encodeURIComponent(reportId)}/recipe`, { method: "GET", signal });
}

export async function downloadReportComposition(workspaceId: string, reportId: string, format: "json" | "markdown", signal?: AbortSignal): Promise<{ blob: Blob; filename: string; exportHash: string | null }> {
  const response = await fetch(`${API_BASE}/workspaces/${encodeURIComponent(workspaceId)}/report-compositions/${encodeURIComponent(reportId)}/exports/${format}`, { method: "GET", credentials: "omit", signal });
  if (!response.ok) await throwApiError(response);
  return {
    blob: await response.blob(),
    filename: safeFilename(response.headers.get("content-disposition"), reportId, format),
    exportHash: response.headers.get("x-report-export-hash"),
  };
}

async function requestJson<T>(path: string, init: RequestInit): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body !== undefined) headers.set("Content-Type", "application/json");
  const response = await fetch(`${API_BASE}${path}`, { ...init, credentials: "omit", headers });
  if (!response.ok) await throwApiError(response);
  return await response.json() as T;
}

async function throwApiError(response: Response): Promise<never> {
  let code = "REPORT_REQUEST_FAILED";
  let message = `Report composition request failed with status ${response.status}`;
  try {
    const value = await response.json() as { detail?: { code?: unknown; message?: unknown } };
    if (typeof value.detail?.code === "string") code = value.detail.code;
    if (typeof value.detail?.message === "string") message = value.detail.message;
  } catch {
    // Error bodies are optional and never treated as trusted renderable content.
  }
  throw new ReportCompositionApiError(response.status, code, message);
}

function safeFilename(header: string | null, reportId: string, format: "json" | "markdown"): string {
  const match = header?.match(/filename="([A-Za-z0-9._-]+)"/u);
  return match?.[1] || `scientific-report-${reportId}.${format === "json" ? "json" : "md"}`;
}
