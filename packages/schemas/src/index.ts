export const artifactTypes = [
  "plotly_json",
  "plotly_html",
  "preview_png",
  "figure_svg",
  "figure_pdf",
  "matterviz_html",
  "matterviz_snapshot_png",
  "structure_json",
  "trajectory_json",
  "trajectory_summary_json",
  "trajectory_report_json",
  "trajectory_manifest_json",
  "phonon_band_json",
  "phonon_band_dos_json",
  "phonon_compatibility_json",
  "phonon_dos_json",
  "phonon_summary_json",
  "phonon_report_json",
  "phonon_manifest_json",
  "phonon_animation_json",
  "phonon_animation_summary_json",
  "phonon_animation_manifest_json",
  "reciprocal_lattice_json",
  "brillouin_zone_json",
  "kpath_json",
  "brillouin_zone_manifest_json",
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
  | "dataset"
  | "table"
  | "viz"
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
  | "PhononEigenvector"
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

export type AnalysisIntentOutcome = "READY" | "NEEDS_CLARIFICATION" | "UNSUPPORTED";

export type ScientificIntent =
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

export type AnalysisIntentBindingOrigin = "USER_EXPLICIT" | "PROFILE_EXACT" | "CLARIFICATION_ANSWER";
export type AnalysisIntentAmbiguitySource = "USER_GOAL" | "DATA_PROFILE" | "RESOURCE_SELECTION" | "SEMANTIC_BINDING";

export type AnalysisIntentResourceRef = {
  objectId: string;
  objectType: string;
  objectHash: string;
  kind: string;
  origin: AnalysisIntentBindingOrigin;
};

export type AnalysisIntentDataScope = {
  datasetId: string;
  datasetVersion: string;
  profileId: string;
  profileContractVersion: string;
  profileSemanticHash: string;
  resourceRefs: AnalysisIntentResourceRef[];
  sampleIds: string[];
  groupIds: string[];
  modelIds: string[];
  origin: AnalysisIntentBindingOrigin;
};

export type AnalysisIntentTargetSemantic = {
  semanticId: string;
  role:
    | "material_property"
    | "regression_target"
    | "regression_prediction"
    | "regression_uncertainty"
    | "classification_target"
    | "classification_prediction"
    | "class_probability"
    | "model_identity"
    | "resource_identity"
    | "comparison_group";
  objectId: string;
  column?: string;
  unit?: string;
  groupId?: string;
  seriesId?: string;
  origin: AnalysisIntentBindingOrigin;
};

export type AnalysisIntentCandidate = { value: string; label: string; semanticId: string };

export type AnalysisIntentAmbiguity = {
  code: string;
  field: string;
  message: string;
  candidates: AnalysisIntentCandidate[];
  blocking: boolean;
  source: AnalysisIntentAmbiguitySource;
};

export type AnalysisIntentDiagnostic = {
  code: string;
  field: string;
  message: string;
  source: AnalysisIntentAmbiguitySource;
  boundary: "CURRENT" | "FUTURE_SCOPE" | "NOT_PLANNED" | "EXECUTION_BOUNDARY" | "MISSING_DATA";
};

export type AnalysisIntentClarificationOption = AnalysisIntentCandidate;
export type AnalysisIntentClarificationQuestion = {
  questionId: string;
  code: string;
  prompt: string;
  type: "SELECT_ONE" | "SELECT_MANY" | "CONFIRM";
  options: AnalysisIntentClarificationOption[];
  required: boolean;
  bindsTo: string;
};

export type AnalysisIntentClarificationAnswer = { questionId: string; selectedValues: string[] };

export type AnalysisIntent = {
  schemaVersion: "1.0";
  intentId: string;
  intentHash: string;
  datasetId: string;
  profileId: string;
  rawGoal: string;
  normalizedGoal: string;
  language: "zh" | "en" | "mixed" | "und";
  dataScope: AnalysisIntentDataScope;
  scientificIntents: ScientificIntent[];
  targetSemantics: AnalysisIntentTargetSemantic[];
  desiredOutputs: AnalysisIntentDesiredOutput[];
  constraints: {
    includeResourceIds: string[];
    excludeResourceIds: string[];
    includeScientificIntents: ScientificIntent[];
    excludeScientificIntents: ScientificIntent[];
    targetIds: string[];
    modelIds: string[];
    groupIds: string[];
    outputPreferences: AnalysisIntentDesiredOutput[];
    maxAnalyses?: number;
    maxToolCalls?: number;
    timePreference?: "FAST" | "BALANCED" | "THOROUGH";
    costPreference?: "LOW" | "BALANCED";
    clarificationAllowed: boolean;
    descriptiveOnly: boolean;
    forbidDerivedInterpretation: boolean;
  };
  requiredCapabilityNeeds: AnalysisIntentCapabilityNeed[];
  optionalCapabilityNeeds: AnalysisIntentCapabilityNeed[];
  ambiguities: AnalysisIntentAmbiguity[];
  missingFacts: AnalysisIntentDiagnostic[];
  unsupportedReasons: AnalysisIntentDiagnostic[];
  outcome: AnalysisIntentOutcome;
  clarification: {
    round: 0 | 1;
    maxRounds: 1;
    maxQuestionsPerRound: 3;
    questions: AnalysisIntentClarificationQuestion[];
    answers: AnalysisIntentClarificationAnswer[];
  };
  provenance: {
    provider: "deterministic_mock" | "openai_compatible";
    model: string;
    promptVersion: string;
    createdAt: string;
    parentIntentId?: string | null;
    answerBindings: AnalysisIntentClarificationAnswer[];
  };
  warnings: AnalysisIntentDiagnostic[];
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
    | "volumetric"
    | "table"
    | "unknown";
  files: Array<Record<string, unknown>>;
  objects: Array<Record<string, unknown>>;
  structureSummary?: Record<string, unknown>;
  tableSummary?: Record<string, unknown>;
  phononSummary?: Record<string, unknown>;
  trajectorySummary?: Record<string, unknown>;
  qualityIssues: Array<Record<string, unknown>>;
  recommendedTasks: Array<Record<string, unknown>>;
  profileContractVersion?: "2.0";
  semanticRulesVersion?: string;
  semanticHash?: string;
  semanticColumns?: DataProfileSemanticColumn[];
  semanticGroups?: DataProfileSemanticGroup[];
  resourceSemantics?: DataProfileResourceSemantic[];
  analysisReadiness?: DataProfileAnalysisReadiness[];
  sampleIdentity?: DataProfileSampleIdentity;
  profileCoverage?: DataProfileCoverage;
  createdAt: string;
};

export type DataProfileSemanticAuthority =
  | "explicit_metadata"
  | "user_declared"
  | "canonical_name"
  | "alias_match"
  | "bounded_pattern";

export type DataProfileSemanticColumn = {
  objectId: string;
  column: string;
  dtype: string;
  roles: Array<{
    role: string;
    authority: DataProfileSemanticAuthority;
    groupId?: string;
    details: Record<string, unknown>;
  }>;
  missingCount: number;
  uniqueCount: number;
  finiteCount?: number;
  nonFiniteCount?: number;
  rowsInspected: number;
  totalRows: number;
  unit?: string;
  ambiguities: string[];
};

export type DataProfileSemanticGroup = {
  groupId: string;
  kind: "regression" | "classification" | "class_probability";
  targetColumns: string[];
  predictionColumns: string[];
  uncertaintyColumns: string[];
  probabilityColumns: string[];
  classes: string[];
  seriesBindings: DataProfileSemanticSeriesBinding[];
  status: "COMPLETE" | "INCOMPLETE" | "AMBIGUOUS";
  reasons: string[];
};

export type DataProfileSemanticSeriesBinding = {
  seriesId: string;
  predictionColumn?: string;
  uncertaintyColumns: string[];
};

export type DataProfileResourceSemantic = {
  objectId: string;
  objectType: string;
  objectHash: string;
  kind: string;
  facts: Record<string, unknown>;
  capabilities: string[];
  warnings: string[];
};

export type DataProfileAnalysisReadiness = {
  capability: string;
  dataStatus: "READY" | "MISSING_REQUIRED_DATA" | "AMBIGUOUS" | "UNSUPPORTED_DATA_KIND";
  platformStatus: "AVAILABLE" | "NOT_IMPLEMENTED" | "NOT_EVALUATED";
  reasons: string[];
  requiredSemantics: string[];
  matchingGroups: string[];
};

export type DataProfileSampleIdentity = {
  policy: "explicit_column" | "object_hash_row_index";
  explicitColumn?: string;
  fallbackPolicy: "dataset_version_object_hash_row_index";
  datasetVersion: string;
  objectIds: string[];
};

export type DataProfileCoverage = {
  policy: "complete" | "deterministic_bounded_sample";
  rowsInspected: number;
  totalRows: number;
  columnsInspected: number;
  totalColumns: number;
  limits: Record<string, number>;
  warnings: string[];
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
