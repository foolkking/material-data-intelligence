export const artifactTypes = [
  "plotly_json",
  "plotly_html",
  "preview_png",
  "figure_svg",
  "figure_pdf",
  "matterviz_html",
  "matterviz_snapshot_png",
  "structure_json",
  "metrics_json",
  "table_json",
  "table_csv",
  "quality_issues_json",
  "summary_md",
  "report_md",
  "report_html",
  "recipe_json",
  "analysis_plan_json",
] as const;

export type ArtifactType = (typeof artifactTypes)[number];

export type DisplayTarget =
  | "overview"
  | "composition"
  | "structure"
  | "trajectory"
  | "phonon"
  | "ml"
  | "artifacts"
  | "report";

export type ToolCategory = "visualization" | "analysis" | "parser" | "report" | "utility";

export type ToolDomain =
  | "composition"
  | "structure"
  | "trajectory"
  | "phonon"
  | "electronic"
  | "simulation"
  | "ml"
  | "generation"
  | "external";

export type ImplementationSource =
  | "pymatviz"
  | "pymatviz_composed"
  | "matterviz"
  | "plotly_custom"
  | "platform_builtin"
  | "plugin";

export type MaterialObjectType =
  | "Composition"
  | "Structure"
  | "Atoms"
  | "Molecule"
  | "DataFrame"
  | "PhononBand"
  | "PhononDos"
  | "Trajectory"
  | "ElementValueMap"
  | "RawUnsupported";

export type JobStatus =
  | "created"
  | "queued"
  | "running"
  | "partial_success"
  | "completed"
  | "failed"
  | "cancel_requested"
  | "cancelled";

export type JobEventStatus = "info" | "running" | "success" | "warning" | "error";

export type ToolCallStatus = "planned" | "running" | "completed" | "failed" | "skipped";

export type JobEvent = {
  id: string;
  jobId: string;
  seq: number;
  eventType: string;
  status: JobEventStatus;
  message: string;
  progress?: number;
  payload?: Record<string, unknown>;
  createdAt: string;
};

export type ToolInputOption = {
  name: string;
  requiredObjectTypes?: MaterialObjectType[];
  requiredFields?: Array<{ role: string; dtype?: string }>;
  description: string;
};

export type ToolInputSchema = {
  inputOptions: ToolInputOption[];
  periodicity?: "periodic_required" | "non_periodic_allowed" | "any";
};

export type ToolOutputSchema = {
  primaryArtifactType: ArtifactType;
  secondaryArtifactTypes: ArtifactType[];
  displayTarget: DisplayTarget;
};

export type RegisteredTool = {
  toolId: string;
  name: string;
  category: ToolCategory;
  domain: ToolDomain;
  implementationSource: ImplementationSource;
  description: string;
  version: string;
  adapter: string;
  inputSchema: ToolInputSchema;
  paramsSchema: Record<string, unknown>;
  outputSchema: ToolOutputSchema;
  artifactTypes: ArtifactType[];
  costLevel: "low" | "medium" | "high";
  defaultTimeoutSec: number;
  maxTimeoutSec: number;
  cachePolicy: "reuse" | "refresh" | "no_cache";
  permissions: string[];
  resourceLimits: Record<string, number>;
};

export type InputRef = {
  refType: "dataset" | "profile" | "normalized_object" | "dataframe_column" | "artifact";
  ref: string;
  fieldRole?: string;
  columnName?: string;
  objectType?: MaterialObjectType;
};

export type ToolExecutionRequest = {
  jobId: string;
  stepId: string;
  toolId: string;
  inputRefs: InputRef[];
  params: Record<string, unknown>;
  artifactTypes: ArtifactType[];
};

export type ToolCall = {
  id: string;
  jobId: string;
  stepId: string;
  toolId: string;
  status: ToolCallStatus;
  params: Record<string, unknown>;
  artifactIds: string[];
  error?: Record<string, unknown>;
  idempotencyKey?: string;
  attempt?: number;
};

export type ArtifactMetadata = {
  toolId?: string;
  toolVersion?: string;
  adapterVersion?: string;
  inputHashes: string[];
  paramsHash?: string;
  profileId?: string;
  recipeId?: string;
  reportId?: string;
  createdAt: string;
  provenance: Record<string, unknown>;
};

export type Artifact = {
  id: string;
  projectId: string;
  datasetId?: string;
  jobId: string;
  toolCallId?: string;
  type: ArtifactType;
  name: string;
  version: string;
  storageKey: string;
  storageProvider?: "local" | "s3" | "minio";
  bucket?: string;
  previewKey?: string;
  sizeBytes: number;
  contentType?: string;
  contentHash: string;
  sha256?: string;
  createdAt?: string;
  metadata: ArtifactMetadata;
};

export type AnalysisStep = {
  stepId: string;
  toolId: string;
  purpose: string;
  reason: string;
  inputRefs: InputRef[];
  params: Record<string, unknown>;
  output: {
    artifactTypes: ArtifactType[];
    displayTarget: DisplayTarget;
  };
  constraints?: {
    timeoutSec?: number;
    maxRows?: number;
    maxStructures?: number;
    requiresConfirmation?: boolean;
  };
};

export type ExpectedArtifact = {
  name: string;
  type: ArtifactType;
  fromStepId?: string;
};

export type AnalysisPlan = {
  schemaVersion: "0.1";
  goal: string;
  datasetId: string;
  profileId: string;
  toolRegistryVersion: string;
  assumptions: string[];
  warnings: string[];
  steps: AnalysisStep[];
  expectedArtifacts: ExpectedArtifact[];
};

export type DataProfile = {
  schemaVersion: "0.1";
  profileId: string;
  datasetId: string;
  version: string;
  datasetType:
    | "structure_collection"
    | "ml_results"
    | "mixed_material_dataset"
    | "trajectory"
    | "phonon"
    | "unknown";
  files: Array<Record<string, unknown>>;
  objects: Array<Record<string, unknown>>;
  structureSummary?: Record<string, unknown>;
  tableSummary?: Record<string, unknown>;
  phononSummary?: Record<string, unknown>;
  trajectorySummary?: Record<string, unknown>;
  qualityIssues: Array<Record<string, unknown>>;
  recommendedTasks: Array<Record<string, unknown>>;
  createdAt: string;
};

export type VisualizationRecipeStep = {
  stepId: string;
  toolId: string;
  toolVersion: string;
  inputBindings: Record<string, string>;
  params: Record<string, unknown>;
  artifactTypes: ArtifactType[];
};

export type VisualizationRecipe = {
  schemaVersion: "0.1";
  recipeId: string;
  name: string;
  version: string;
  projectId: string;
  sourceJobId?: string;
  sourcePlanId?: string;
  inputRequirements: Array<Record<string, unknown>>;
  steps: VisualizationRecipeStep[];
  environment: Record<string, unknown>;
};
