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

export type ArtifactCardinality = "EXACTLY_ONE";
export type ArtifactContentTrust = "INERT_DATA";
export type IdentityCompatibility = "EXACT_PLAN_JOB_DATASET_RESOURCE";

export type DependencyDiagnosticCode =
  | "OUTPUT_PORT_NOT_DECLARED"
  | "INPUT_PORT_NOT_DECLARED"
  | "ARTIFACT_KIND_MISMATCH"
  | "CONTRACT_VERSION_MISMATCH"
  | "MEDIA_TYPE_MISMATCH"
  | "CARDINALITY_MISMATCH"
  | "IDENTITY_SCOPE_MISMATCH"
  | "RESOURCE_VERSION_MISMATCH"
  | "ARTIFACT_TOO_LARGE"
  | "NON_DETERMINISTIC_OUTPUT_NOT_ALLOWED"
  | "UNTRUSTED_OR_EXECUTABLE_ARTIFACT"
  | "CONSUMER_REQUIRES_UNAVAILABLE_BASE_RESOURCE"
  | "PORT_NOT_PLANNER_VISIBLE"
  | "DEPENDENCY_COMPOSITION_NOT_ALLOWED"
  | "CYCLE_WOULD_BE_CREATED"
  | "GRAPH_CAP_EXCEEDED"
  | "UNKNOWN_STEP"
  | "DUPLICATE_BINDING"
  | "DUPLICATE_CONSUMER_PORT"
  | "SELECTED_TOOL_MISMATCH"
  | "BINDING_IDENTITY_INVALID"
  | "GRAPH_IDENTITY_INVALID"
  | "EXTERNAL_AUTHORITY_REJECTED";

export type DependencyDiagnostic = {
  code: DependencyDiagnosticCode;
  field: string;
  message: string;
  bindingId?: string | null;
  stepId?: string | null;
};

export type ArtifactOutputPort = {
  portId: string;
  artifactKind: ArtifactType;
  contractFamily: string;
  contractVersions: string[];
  mediaTypes: string[];
  cardinality: ArtifactCardinality;
  maxBytes: number;
  deterministic: boolean;
  requiredProvenanceFields: string[];
  identityPolicy: IdentityCompatibility;
  contentTrust: ArtifactContentTrust;
  plannerVisible: boolean;
};

export type ArtifactInputPort = {
  portId: string;
  acceptedArtifactKinds: ArtifactType[];
  acceptedContractVersions: string[];
  mediaTypes: string[];
  cardinality: ArtifactCardinality;
  maxBytes: number;
  identityPolicy: IdentityCompatibility;
  requiredSemanticRoles: string[];
  materializationPermitted: boolean;
  baseResourceRequired: boolean;
  inputFieldRole: string;
  inputObjectType: string;
  plannerVisible: boolean;
  contentTrust: ArtifactContentTrust;
};

export type ToolArtifactPortMetadata = {
  schemaVersion: "1.1";
  toolId: string;
  toolVersion: string;
  inputPorts: ArtifactInputPort[];
  outputPorts: ArtifactOutputPort[];
  dependencyCompositionAllowed: boolean;
};

export type DependencyBinding = {
  bindingId: string;
  producerStepId: string;
  producerOutputPort: string;
  consumerStepId: string;
  consumerInputPort: string;
  artifactKind: ArtifactType;
  artifactContractVersion: string;
  mediaType: string;
  cardinality: ArtifactCardinality;
};

export type AnalysisPlanV02 = {
  schemaVersion: "0.2";
  goal: string;
  datasetId: string;
  profileId: string;
  toolRegistryVersion: string;
  graphHash: string;
  assumptions: string[];
  warnings: string[];
  steps: AnalysisStep[];
  dependencyBindings: DependencyBinding[];
  expectedArtifacts: ExpectedArtifact[];
};

export type ArtifactPortCompatibility = {
  pairId: string;
  producerToolId: string;
  producerToolVersion: string;
  producerOutputPort: string;
  consumerToolId: string;
  consumerToolVersion: string;
  consumerInputPort: string;
  compatible: boolean;
  artifactKind?: ArtifactType | null;
  artifactContractVersion?: string | null;
  mediaType?: string | null;
  diagnostics: DependencyDiagnostic[];
};

export type DependencyCompositionProposal = {
  schemaVersion: "1.0";
  matrixId: string;
  selectedPairIds: string[];
};

export type ArtifactCompatibilityMatrix = {
  schemaVersion: "1.0";
  matrixId: string;
  matrixHash: string;
  registrySnapshotId: string;
  registrySnapshotHash: string;
  selectedToolIds: string[];
  portMetadataHashes: Record<string, string>;
  pairs: ArtifactPortCompatibility[];
};

export type StepExecutionState =
  | "PENDING"
  | "READY"
  | "RUNNING"
  | "SUCCEEDED"
  | "FAILED"
  | "BLOCKED_DEPENDENCY"
  | "NOT_STARTED";

export type BindingExecutionState =
  | "PENDING"
  | "RESOLVED"
  | "FAILED_PRODUCER"
  | "MISSING_ARTIFACT"
  | "CONTRACT_MISMATCH"
  | "SCOPE_MISMATCH"
  | "CHECKSUM_MISMATCH"
  | "SIZE_REJECTED"
  | "CONSUMER_NOT_RUN";

export type DependencyExecutionOutcome =
  | "ALL_SUCCEEDED"
  | "PARTIAL_RESULTS"
  | "ALL_FAILED"
  | "VALIDATION_ABORTED";

export type DependencyStepExecution = {
  stepId: string;
  toolId: string;
  state: StepExecutionState;
  toolCallId?: string | null;
  artifactIds: string[];
  blockedByStepIds: string[];
  errorCode?: string | null;
  errorMessage?: string | null;
};

export type DependencyBindingExecution = {
  bindingId: string;
  state: BindingExecutionState;
  producerToolCallId?: string | null;
  artifactId?: string | null;
  artifactChecksum?: string | null;
  consumerToolCallId?: string | null;
  errorCode?: string | null;
};

export type DependencyExecutionRecord = {
  schemaVersion: "1.0";
  executionId: string;
  executionHash: string;
  planId: string;
  planHash: string;
  jobId: string;
  graphHash: string;
  topologicalOrder: string[];
  steps: DependencyStepExecution[];
  bindings: DependencyBindingExecution[];
  succeededCount: number;
  failedCount: number;
  blockedCount: number;
  notStartedCount: number;
  partialArtifactIds: string[];
  outcome: DependencyExecutionOutcome;
  runtimeVersion: string;
  createdAt: string;
  updatedAt: string;
};

export type ResolvedArtifactInputRef = {
  schemaVersion: "1.0";
  bindingId: string;
  planId: string;
  planHash: string;
  jobId: string;
  producerStepId: string;
  producerToolCallId: string;
  artifactId: string;
  artifactKind: ArtifactType;
  artifactContractVersion: string;
  mediaType: string;
  sizeBytes: number;
  checksum: string;
  consumerStepId: string;
  consumerInputPort: string;
  materializedObjectRef: string;
};

export type ArtifactLineageRecord = {
  schemaVersion: "1.0";
  lineageId: string;
  lineageHash: string;
  projectId: string;
  datasetId?: string | null;
  datasetVersion?: string | null;
  profileId?: string | null;
  profileSemanticHash?: string | null;
  intentId?: string | null;
  intentHash?: string | null;
  resolutionId?: string | null;
  resolutionHash?: string | null;
  decisionId?: string | null;
  decisionHash?: string | null;
  planId: string;
  planHash: string;
  planSchemaVersion: "0.2";
  graphHash: string;
  jobId: string;
  producerStepId: string;
  producerToolCallId: string;
  producerToolId: string;
  producerToolVersion: string;
  outputPort: string;
  artifactId: string;
  artifactKind: ArtifactType;
  artifactContractVersion: string;
  mediaType: string;
  contentHash: string;
  upstreamArtifactIds: string[];
  upstreamArtifactHashes: string[];
  bindingIds: string[];
  adapterVersion?: string | null;
  runtimeVersion: string;
  warnings: string[];
  caps: Record<string, number>;
  createdAt: string;
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
    provider: "deterministic_mock" | "openai_compatible" | "deepseek";
    model: string;
    promptVersion: string;
    createdAt: string;
    parentIntentId?: string | null;
    answerBindings: AnalysisIntentClarificationAnswer[];
  };
  warnings: AnalysisIntentDiagnostic[];
};

export type CapabilityPlanningOutcome =
  | "PLAN_READY"
  | "NEEDS_CLARIFICATION"
  | "UNSUPPORTED"
  | "CAPABILITY_MISMATCH"
  | "VALIDATION_FAILED";

export type PlannerAvailability = "AVAILABLE" | "DEPLOYMENT_UNAVAILABLE" | "FUTURE" | "NOT_PLANNED";
export type PlannerBindingSource =
  | "RESOURCE_ID"
  | "TARGET_COLUMN"
  | "TARGET_GROUP_IDS"
  | "SEMANTIC_COLUMNS"
  | "PROFILE_ID"
  | "RESOURCE_FACT"
  | "LITERAL";

export type CapabilityDiagnostic = {
  code: string;
  field: string;
  message: string;
  toolId?: string | null;
  repairable: boolean;
};

export type PlannerBindingValue = {
  valueId: string;
  value: string | number | boolean | string[];
  source: PlannerBindingSource;
  sourceIdentity: string;
};

export type PlannerBindingDomain = {
  parameter: string;
  required: boolean;
  values: PlannerBindingValue[];
};

export type PlannerParameterBinding = {
  parameter: string;
  source: PlannerBindingSource;
  required: boolean;
  targetRoles: string[];
  objectTypes: string[];
  factKeys: string[];
  literalValue?: string | number | boolean | string[] | null;
  multiple: boolean;
};

export type ToolPlannerMetadata = {
  schemaVersion: "1.0";
  toolId: string;
  toolName: string;
  toolVersion: string;
  availability: PlannerAvailability;
  scientificIntents: ScientificIntent[];
  capabilityNeeds: AnalysisIntentCapabilityNeed[];
  desiredOutputs: AnalysisIntentDesiredOutput[];
  acceptedObjectTypes: string[];
  inputObjectTypeOptions: string[][];
  requiredProfileCapabilities: string[];
  requiredTargetRoles: string[];
  minInputs: number;
  maxInputs: number;
  minTargets: number;
  maxTargets: number;
  parameterBindings: PlannerParameterBinding[];
  declaredArtifactTypes: string[];
  costClass: 1 | 2 | 3;
  independentComposable: boolean;
  collisionGroup?: string | null;
  executionBoundary: "REGISTERED_ADAPTER_ONLY";
};

export type PlannerResourceIdentity = {
  objectId: string;
  objectType: string;
  objectHash: string;
  kind: string;
};

export type EvaluatedToolCandidate = {
  toolId: string;
  toolName: string;
  toolVersion: string;
  eligible: boolean;
  matchedScientificIntents: ScientificIntent[];
  matchedCapabilityNeeds: AnalysisIntentCapabilityNeed[];
  matchedDesiredOutputs: AnalysisIntentDesiredOutput[];
  acceptedResourceIds: string[];
  satisfiedProfileCapabilities: string[];
  unsatisfiedProfileCapabilities: string[];
  targetSemanticIds: string[];
  bindingDomains: PlannerBindingDomain[];
  reasons: CapabilityDiagnostic[];
  rankFacts: Array<number | string>;
  costClass: 1 | 2 | 3;
  independentComposable: boolean;
  collisionGroup?: string | null;
};

export type EligibilityResolution = {
  schemaVersion: "1.0";
  resolutionId: string;
  resolutionHash: string;
  intentId: string;
  intentHash: string;
  profileId: string;
  profileContractVersion: string;
  profileSemanticHash: string;
  datasetId: string;
  datasetVersion: string;
  registrySnapshotId: string;
  registrySnapshotHash: string;
  resourceIdentities: PlannerResourceIdentity[];
  evaluatedCandidates: EvaluatedToolCandidate[];
  eligibleToolIds: string[];
  rejectedToolIds: string[];
  diagnostics: CapabilityDiagnostic[];
  warnings: CapabilityDiagnostic[];
  provenance: { resolver: "deterministic_eligibility_resolver"; resolverVersion: "1.0" };
};

export type BoundParameter = {
  parameter: string;
  value: string | number | boolean | string[];
  valueId: string;
  source: PlannerBindingSource;
  sourceIdentity: string;
};

export type SelectedCapability = {
  toolId: string;
  toolName: string;
  toolVersion: string;
  coveredScientificIntents: ScientificIntent[];
  coveredCapabilityNeeds: AnalysisIntentCapabilityNeed[];
  coveredDesiredOutputs: AnalysisIntentDesiredOutput[];
  inputResourceIds: string[];
  targetSemanticIds: string[];
  boundParameters: BoundParameter[];
  artifactTypes: string[];
  rankFacts: Array<number | string>;
};

export type CapabilityPlanningDecision = {
  schemaVersion: "1.0";
  decisionId: string;
  decisionHash: string;
  intentId: string;
  intentHash: string;
  profileId: string;
  profileSemanticHash: string;
  registrySnapshotId: string;
  registrySnapshotHash: string;
  resolutionId: string;
  resolutionHash: string;
  outcome: CapabilityPlanningOutcome;
  selections: SelectedCapability[];
  unfulfilledDesiredOutputs: AnalysisIntentDesiredOutput[];
  diagnostics: CapabilityDiagnostic[];
  warnings: CapabilityDiagnostic[];
  provenance: {
    provider: "deterministic_mock" | "openai_compatible" | "deepseek";
    providerContractVersion: "1.0";
    model: string;
    repairCount: 0 | 1;
    initialDecisionHash?: string | null;
    repairDiagnostics: CapabilityDiagnostic[];
  };
};

export type NaturalLanguageEvidenceCase = {
  schemaVersion: "1.0";
  caseSpecId: string;
  caseSpecHash: string;
  title: string;
  userText: string;
  requiredCapabilityNeeds: string[];
  acceptableToolIds: string[];
  requiredOutputs: string[];
  forbiddenFallbacks: string[];
  requiresClarification: boolean;
  requiresDependencyPlan: boolean;
};

export type NaturalLanguageEvidenceRun = {
  schemaVersion: "1.0";
  runId: string;
  runHash: string;
  caseSpecId: string;
  caseSpecHash: string;
  userText: string;
  resourceManifest: Array<{ objectId: string; objectType: string; objectHash: string; kind: string }>;
  provider: { mode: "DETERMINISTIC" | "FAKE_DEEPSEEK" | "REAL_DEEPSEEK"; provider: "deterministic_mock" | "deepseek"; model: string; purposes: string[]; keySource: "NONE" | "DEEPSEEK_KEY"; realCallCount: number; promptHashes: string[]; responseHashes: string[] };
  profile: { recordId: string; recordHash: string; schemaVersion: string };
  intent: { intentId: string; intentHash: string; outcome: "READY" | "NEEDS_CLARIFICATION" | "UNSUPPORTED"; clarificationRound: number };
  eligibility?: { recordId: string; recordHash: string; schemaVersion: string } | null;
  selectedTools: Array<{ toolId: string; toolVersion: string; bindingHash: string }>;
  plan?: { planId: string; planHash: string; schemaVersion: "0.1" | "0.2"; graphHash?: string | null } | null;
  job?: { recordId: string; state: string; semanticHash?: string | null } | null;
  toolCalls: Array<{ recordId: string; state: string; semanticHash?: string | null }>;
  artifacts: Array<{ artifactId: string; artifactType: string; contentHash: string; sizeBytes: number; producerToolCallId: string }>;
  executionOutcome: string;
  lineage: Array<{ recordId: string; state: string; semanticHash?: string | null }>;
  evidenceBundle?: { recordId: string; recordHash: string; schemaVersion: string } | null;
  interpretation?: { recordId: string; recordHash: string; schemaVersion: string } | null;
  claimEvidenceLinks: Array<{ claimId: string; evidenceItemIds: string[] }>;
  apiRefs: string[];
  browserRefs: string[];
  securityMarkers: string[];
  tokenUsage: { promptTokens: number; completionTokens: number; totalTokens: number; estimated: boolean };
  elapsedMs: number;
  verdict: "PASS" | "FAIL" | "BLOCKED";
  createdAt: string;
};

export type DeepSeekVerificationRecord = {
  schemaVersion: "1.0";
  verificationId: string;
  verificationHash: string;
  provider: "deepseek";
  baseUrl: "https://api.deepseek.com";
  keySource: "DEEPSEEK_KEY";
  configured: boolean;
  model: "deepseek-v4-flash" | "deepseek-v4-pro";
  purposes: string[];
  realCallCount: number;
  otherRealProviderCalls: 0;
  runIds: string[];
  outcomes: string[];
  tokenUsage: { promptTokens: number; completionTokens: number; totalTokens: number; estimated: boolean };
  sanitized: true;
  verdict: "PASS" | "FAIL" | "BLOCKED";
  createdAt: string;
};

export type DeepSeekCaseVerificationRef = {
  caseSpecId: string;
  runId: string;
  verificationId: string;
  verificationHash: string;
  realCallCount: number;
  verdict: "PASS";
};

export type DeepSeekVerificationSuite = {
  schemaVersion: "1.0";
  suiteId: string;
  suiteHash: string;
  provider: "deepseek";
  baseUrl: "https://api.deepseek.com";
  keySource: "DEEPSEEK_KEY";
  configured: true;
  model: "deepseek-v4-flash" | "deepseek-v4-pro";
  cases: [DeepSeekCaseVerificationRef, DeepSeekCaseVerificationRef, DeepSeekCaseVerificationRef, DeepSeekCaseVerificationRef, DeepSeekCaseVerificationRef];
  totalRealCallCount: number;
  otherRealProviderCalls: 0;
  tokenUsage: { promptTokens: number; completionTokens: number; totalTokens: number; estimated: boolean };
  sanitized: true;
  verdict: "PASS";
  createdAt: string;
};

export type Phase10LClosureManifest = {
  schemaVersion: "1.0";
  manifestId: string;
  manifestHash: string;
  phase: "10L";
  caseSpecIds: [string, string, string, string, string];
  runIds: [string, string, string, string, string];
  deepSeekVerificationId: string;
  entries: Array<{ path: string; sha256: string; bytes: number }>;
  securityMarkers: string[];
  verdict: "PASS" | "READY_WITH_EXPLICIT_LIMITS" | "FAIL" | "BLOCKED";
  createdAt: string;
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
  profileContractVersion?: "2.0" | "2.1";
  semanticRulesVersion?: string;
  semanticHash?: string;
  semanticColumns?: DataProfileSemanticColumn[];
  semanticGroups?: DataProfileSemanticGroup[];
  resourceSemantics?: DataProfileResourceSemantic[];
  analysisReadiness?: DataProfileAnalysisReadiness[];
  sampleIdentity?: DataProfileSampleIdentity;
  profileCoverage?: DataProfileCoverage;
  coordinationReadiness?: DataProfileCoordinationReadiness;
  createdAt: string;
};

export type DataProfileCoordinationStructureReadiness = {
  objectId: string;
  objectHash: string;
  periodic: boolean;
  latticeStatus: "VALID" | "MISSING" | "INVALID";
  siteCount: number;
  speciesOccupancyStatus: "ORDERED_FULL_OCCUPANCY" | "DISORDERED" | "PARTIAL_OCCUPANCY" | "UNSUPPORTED";
  disorderStatus: "ORDERED" | "DISORDERED" | "UNKNOWN";
  partialOccupancyStatus: "ABSENT" | "PRESENT" | "UNKNOWN";
  coordinationInputStatus: "READY" | "MISSING_REQUIRED_DATA" | "AMBIGUOUS" | "UNSUPPORTED_DATA_KIND";
  reasons: string[];
};

export type DataProfileCoordinationReadiness = {
  contractVersion: "1.0";
  periodicStructurePresent: boolean;
  eligibleStructureCount: number;
  structures: DataProfileCoordinationStructureReadiness[];
  status: "READY" | "MISSING_REQUIRED_DATA" | "AMBIGUOUS" | "UNSUPPORTED_DATA_KIND";
  reasons: string[];
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

export type ScientificEvidenceKind =
  | "SCALAR" | "RANGE" | "CATEGORY" | "COUNT" | "BOOLEAN"
  | "ORDERED_SERIES_SUMMARY" | "TABLE_ROW" | "WARNING" | "LIMITATION"
  | "EXECUTION_STATE" | "PROVENANCE";

export type ScientificEvidenceItem = {
  schemaVersion: "1.0";
  evidenceItemId: string;
  semanticRole: string;
  evidenceKind: ScientificEvidenceKind;
  subjectId: string;
  valueKind: string;
  normalizedValue: {
    scalar?: boolean | number | string | null;
    minimum?: number | null;
    maximum?: number | null;
    values: Array<boolean | number | string>;
  };
  displayValue: string;
  unit?: string | null;
  unitAuthority?: string | null;
  referenceConvention?: string | null;
  sourceArtifactId: string;
  sourceArtifactChecksum: string;
  artifactContract: string;
  artifactContractVersion: string;
  sourceToolId: string;
  sourceToolVersion: string;
  producerStepId: string;
  producerToolCallId: string;
  fieldLocator: { fieldId: string; semanticKey: string; entityId?: string | null };
  datasetId: string;
  datasetVersion: string;
  resourceId?: string | null;
  warnings: string[];
  limitations: string[];
  projectorVersion: string;
  providerSafe: boolean;
};

export type ScientificEvidenceRef = {
  schemaVersion: "1.0";
  evidenceItemId: string;
  role: "SUPPORTING" | "LIMITING" | "CONTRADICTING";
};

export type ScientificEvidenceBundle = {
  schemaVersion: "1.0";
  bundleId: string;
  bundleHash: string;
  projectId: string;
  datasetId: string;
  datasetVersion: string;
  profileId?: string | null;
  profileSemanticHash?: string | null;
  intentId?: string | null;
  intentHash?: string | null;
  eligibilityResolutionId?: string | null;
  eligibilityResolutionHash?: string | null;
  selectionDecisionId?: string | null;
  selectionDecisionHash?: string | null;
  planId: string;
  planHash: string;
  planSchemaVersion: "0.1" | "0.2";
  graphHash?: string | null;
  jobId: string;
  sourceJobTerminalState: "completed" | "failed" | "partial_success";
  executionOutcome: "ALL_SUCCEEDED" | "PARTIAL_RESULTS" | "ALL_FAILED" | "VALIDATION_ABORTED" | "LEGACY_TERMINAL";
  allSucceeded: boolean;
  partialResults: boolean;
  supportedArtifactCount: number;
  unsupportedArtifactCount: number;
  failedStepCount: number;
  blockedStepCount: number;
  bundleCompleteness: "COMPLETE" | "PARTIAL" | "UNSUPPORTED";
  bundleWarnings: string[];
  bundleLimitations: string[];
  sourceArtifactIds: string[];
  projectorVersions: Record<string, string>;
  evidenceItems: ScientificEvidenceItem[];
};

export type ScientificClaim = {
  schemaVersion: "1.0";
  claimId: string;
  claimType: "OBSERVATION" | "COMPARISON" | "ANOMALY" | "WARNING" | "LIMITATION" | "RECOMMENDATION" | "NO_SUPPORTED_CONCLUSION";
  subjectEvidenceIds: string[];
  supportingEvidenceIds: string[];
  limitingEvidenceIds: string[];
  contradictingEvidenceIds: string[];
  semanticPredicate: "HAS_VALUE" | "HAS_RANGE" | "HAS_COUNT" | "HAS_CATEGORY" | "REPORTS_WARNING" | "REPORTS_LIMITATION" | "DIFFERS_FROM" | "EXCEEDS_DECLARED_THRESHOLD" | "IS_MISSING" | "IS_PARTIAL" | "SUGGESTS_FOLLOW_UP" | "NO_SUPPORTED_CONCLUSION";
  qualifiers: string[];
  structuredPayload: Record<string, boolean | number | string>;
  renderedText: string;
  scope: string;
  confidenceClass: "DIRECT" | "QUALIFIED" | "LIMITED";
  groundingStatus: "GROUNDED" | "REJECTED";
  displayOrder: number;
};

export type ScientificRecommendation = {
  recommendationId: string;
  reasonEvidenceIds: string[];
  suggestedGoalCategory: string;
  expectedMissingEvidence: string[];
  limitation: string;
  executionAuthorized: false;
  planCreated: false;
  jobCreated: false;
};

export type InterpretationOutcome =
  | "INTERPRETATION_READY" | "INTERPRETATION_READY_WITH_LIMITS"
  | "NO_SUPPORTED_EVIDENCE" | "SOURCE_NOT_TERMINAL" | "SOURCE_INTEGRITY_FAILED"
  | "EVIDENCE_CAP_EXCEEDED" | "PROVIDER_FAILED" | "VALIDATION_FAILED";

export type GroundedScientificInterpretation = {
  schemaVersion: "1.0";
  interpretationId: string;
  interpretationHash: string;
  sourceBundleId: string;
  sourceBundleHash: string;
  sourceJobId: string;
  sourcePlanId: string;
  sourcePlanHash: string;
  sourceGraphHash?: string | null;
  mode: "DETERMINISTIC" | "STRICT_PROVIDER";
  provider: string;
  providerVersion: string;
  claims: ScientificClaim[];
  globalWarnings: string[];
  globalLimitations: string[];
  recommendations: ScientificRecommendation[];
  completeness: "COMPLETE" | "PARTIAL" | "UNSUPPORTED";
  partialResultState: boolean;
  repairCount: 0 | 1;
  outcome: InterpretationOutcome;
  validationOutcome: "VALID" | "INVALID";
  executionRecordId: string;
  createdAt: string;
};

export type InterpretationExecutionRecord = {
  schemaVersion: "1.0";
  executionRecordId: string;
  executionRecordHash: string;
  sourceJobId: string;
  sourcePlanId: string;
  sourcePlanHash: string;
  sourceGraphHash?: string | null;
  sourceBundleId: string;
  sourceBundleHash: string;
  mode: "DETERMINISTIC" | "STRICT_PROVIDER";
  provider: string;
  providerVersion: string;
  providerModel?: string | null;
  providerConfigHash?: string | null;
  idempotencyKeyHash?: string | null;
  promptProjectionHash?: string | null;
  initialResponseHash?: string | null;
  repairedResponseHash?: string | null;
  responseHash?: string | null;
  repairCount: 0 | 1;
  evidenceItemCount: number;
  claimCount: number;
  warningCount: number;
  limitationCount: number;
  outcome: InterpretationOutcome;
  diagnostics: string[];
  caps: Record<string, number>;
  elapsedMs: number;
  createdAt: string;
};

export const WORKSPACE_SCHEMA_VERSION = "1.0" as const;
export const WORKSPACE_PANEL_SCHEMA_VERSION = "1.0" as const;
export const WORKSPACE_SELECTION_SCHEMA_VERSION = "1.0" as const;
export const WORKSPACE_LAYOUT_SCHEMA_VERSION = "1.0" as const;

export const WORKSPACE_MAX_PANELS = 32 as const;
export const WORKSPACE_MAX_LAYOUT_REVISIONS = 128 as const;
export const WORKSPACE_MAX_SECONDARY_SELECTIONS = 16 as const;
export const WORKSPACE_MAX_SELECTION_URL_BYTES = 2_048 as const;
export const WORKSPACE_MAX_MUTATION_BYTES = 131_072 as const;
export const WORKSPACE_MAX_SNAPSHOT_BYTES = 524_288 as const;
export const WORKSPACE_MAX_JSON_DEPTH = 14 as const;
export const WORKSPACE_MAX_WARNINGS = 64 as const;
export const WORKSPACE_MAX_DIAGNOSTICS = 64 as const;

export const WORKSPACE_RENDERER_CONTRACTS = [
  "workspace.overview/1.0",
  "workspace.data/1.0",
  "workspace.plan/1.0",
  "workspace.execution/1.0",
  "workspace.artifact-metadata/1.0",
  "workspace.findings/1.0",
  "workspace.evidence/1.0",
  "workspace.provenance/1.0",
  "workspace.report/1.0",
  "workspace.inert-fallback/1.0",
] as const;
export type WorkspaceRendererContract = (typeof WORKSPACE_RENDERER_CONTRACTS)[number];

export const WORKSPACE_STATUS_VALUES = [
  "SOURCE_MISSING",
  "UNSUPPORTED",
  "LEGACY_READ_ONLY",
  "STALE",
  "RUNNING",
  "PARTIAL_RESULTS",
  "COMPLETE",
  "FAILED",
  "READY",
  "INITIALIZING",
] as const;
export type WorkspaceStatus = (typeof WORKSPACE_STATUS_VALUES)[number];

export const WORKSPACE_PANEL_STATE_VALUES = [
  "NOT_APPLICABLE",
  "READY_NOT_RUN",
  "LOADING",
  "PRODUCED",
  "PARTIAL",
  "UNAVAILABLE",
  "FAILED",
  "BLOCKED_BY_DEPENDENCY",
  "STALE",
  "CAP_EXCEEDED",
  "CONTRACT_UNSUPPORTED",
  "SOURCE_DELETED",
  "PROFILE_AUTHORITY_UNAVAILABLE",
] as const;
export type WorkspacePanelState = (typeof WORKSPACE_PANEL_STATE_VALUES)[number];

export const WORKSPACE_PANEL_KIND_VALUES = [
  "OVERVIEW",
  "DATA",
  "PLAN",
  "EXECUTION",
  "SCIENTIFIC_RESULT",
  "FINDINGS",
  "EVIDENCE",
  "PROVENANCE",
  "REPORT",
] as const;
export type WorkspacePanelKind = (typeof WORKSPACE_PANEL_KIND_VALUES)[number];

export const WORKSPACE_SELECTION_KIND_VALUES = [
  "DATASET_SAMPLE",
  "MATERIAL_OBJECT",
  "STRUCTURE",
  "PERIODIC_SITE",
  "LOCAL_ENVIRONMENT",
  "COORDINATION_POLYHEDRON",
  "POLYHEDRON_VERTEX",
  "POLYHEDRON_FACE",
  "TRAJECTORY_ATOM",
  "TRAJECTORY_FRAME",
  "PHONON_Q_POINT",
  "PHONON_BRANCH",
  "RECIPROCAL_POINT",
  "VOLUMETRIC_FIELD",
  "ARTIFACT",
  "EVIDENCE_ITEM",
  "CLAIM",
] as const;
export type WorkspaceSelectionKind = (typeof WORKSPACE_SELECTION_KIND_VALUES)[number];

export const WORKSPACE_SOURCE_KIND_VALUES = [
  "PROJECT",
  "DATASET",
  "PROFILE",
  "INTENT",
  "ELIGIBILITY_RESOLUTION",
  "SELECTION_DECISION",
  "PLAN",
  "JOB",
  "TOOL_CALL",
  "ARTIFACT",
  "DEPENDENCY_EXECUTION",
  "INTERPRETATION",
  "EVIDENCE_BUNDLE",
  "REPORT",
  "RECIPE",
] as const;
export type WorkspaceSourceKind = (typeof WORKSPACE_SOURCE_KIND_VALUES)[number];

export type WorkspaceWarning = {
  code: string;
  message: string;
  sourceId?: string | null;
};

export type WorkspaceDurableMetadata = {
  tags: string[];
  note?: string | null;
};

export type WorkspaceSourceRef = {
  kind: WorkspaceSourceKind;
  sourceId: string;
  sourceHash?: string | null;
  contract?: string | null;
  contractVersion?: string | null;
  mediaType?: string | null;
  projectId: string;
  jobId?: string | null;
  toolCallId?: string | null;
  stepId?: string | null;
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
  rendererContract: WorkspaceRendererContract;
  state: WorkspacePanelState;
  acceptedSelectionKinds: WorkspaceSelectionKind[];
  emittedSelectionKinds: WorkspaceSelectionKind[];
  evidenceRefs: string[];
  provenanceRefs: string[];
  capabilityRequirement?: string | null;
  layout: WorkspacePanelLayout;
  mobilePresentationMode: "STACKED" | "FULL_WIDTH" | "HIDDEN";
  accessibleName: string;
  unsupportedReason?: string | null;
  panelStateHash: string;
  contractProvenance: string;
};

type WorkspaceSelectionRefCommon = {
  selectionSchemaVersion: "1.0";
  sourceScopeHash: string;
  projectId: string;
};

type WorkspaceSelectionValueFields = {
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

type WorkspaceSelectionField = keyof WorkspaceSelectionValueFields;
type WorkspaceRequiredSelectionFields<RequiredFields extends WorkspaceSelectionField> = {
  [Field in RequiredFields]-?: Exclude<WorkspaceSelectionValueFields[Field], null>;
};
type WorkspaceOptionalSelectionFields<OptionalFields extends WorkspaceSelectionField> = Partial<
  Pick<WorkspaceSelectionValueFields, OptionalFields>
>;
type WorkspaceForbiddenSelectionFields<AllowedFields extends WorkspaceSelectionField> = {
  [Field in Exclude<WorkspaceSelectionField, AllowedFields>]?: never;
};
type WorkspaceSelectionRefFor<
  Kind extends WorkspaceSelectionKind,
  RequiredFields extends WorkspaceSelectionField,
  AllowedFields extends WorkspaceSelectionField,
> = WorkspaceSelectionRefCommon &
  { kind: Kind } &
  WorkspaceRequiredSelectionFields<RequiredFields> &
  WorkspaceOptionalSelectionFields<Exclude<AllowedFields, RequiredFields>> &
  WorkspaceForbiddenSelectionFields<AllowedFields>;

export type WorkspaceDatasetSampleSelectionRef = WorkspaceSelectionRefFor<
  "DATASET_SAMPLE",
  "datasetId" | "datasetVersion" | "objectId" | "sampleRef",
  "datasetId" | "datasetVersion" | "objectId" | "sampleRef" | "artifactId" | "artifactChecksum"
>;

export type WorkspaceMaterialObjectSelectionRef = WorkspaceSelectionRefFor<
  "MATERIAL_OBJECT",
  "datasetId" | "datasetVersion" | "objectId",
  "datasetId" | "datasetVersion" | "objectId" | "sampleRef" | "artifactId" | "artifactChecksum"
>;

export type WorkspaceStructureSelectionRef = WorkspaceSelectionRefFor<
  "STRUCTURE",
  "datasetId" | "datasetVersion" | "objectId" | "structureId",
  "datasetId" | "datasetVersion" | "objectId" | "structureId" | "artifactId" | "artifactChecksum"
>;

export type WorkspacePeriodicSiteSelectionRef = WorkspaceSelectionRefFor<
  "PERIODIC_SITE",
  "datasetId" | "datasetVersion" | "objectId" | "structureId" | "siteId",
  | "datasetId" | "datasetVersion" | "objectId" | "structureId" | "siteId"
  | "artifactId" | "artifactChecksum"
>;

type WorkspaceN2CommonFields =
  | "datasetId" | "datasetVersion" | "jobId" | "objectId" | "structureId" | "siteId"
  | "artifactId" | "artifactChecksum" | "sourceArtifactId" | "sourceArtifactChecksum";

export type WorkspaceLocalEnvironmentSelectionRef = WorkspaceSelectionRefFor<
  "LOCAL_ENVIRONMENT",
  WorkspaceN2CommonFields | "environmentId",
  WorkspaceN2CommonFields | "environmentId" | "geometryReferenceId"
>;

export type WorkspaceCoordinationPolyhedronSelectionRef = WorkspaceSelectionRefFor<
  "COORDINATION_POLYHEDRON",
  WorkspaceN2CommonFields | "environmentId" | "polyhedronId",
  WorkspaceN2CommonFields | "environmentId" | "polyhedronId" | "geometryReferenceId"
>;

export type WorkspacePolyhedronVertexSelectionRef = WorkspaceSelectionRefFor<
  "POLYHEDRON_VERTEX",
  WorkspaceN2CommonFields | "polyhedronId" | "vertexId",
  WorkspaceN2CommonFields | "polyhedronId" | "vertexId"
>;

export type WorkspacePolyhedronFaceSelectionRef = WorkspaceSelectionRefFor<
  "POLYHEDRON_FACE",
  WorkspaceN2CommonFields | "polyhedronId" | "faceId",
  WorkspaceN2CommonFields | "polyhedronId" | "faceId"
>;

export type WorkspaceTrajectoryAtomSelectionRef = WorkspaceSelectionRefFor<
  "TRAJECTORY_ATOM",
  "datasetId" | "datasetVersion" | "trajectoryId" | "atomId",
  "datasetId" | "datasetVersion" | "trajectoryId" | "atomId" | "artifactId" | "artifactChecksum"
>;

export type WorkspaceTrajectoryFrameSelectionRef = WorkspaceSelectionRefFor<
  "TRAJECTORY_FRAME",
  "datasetId" | "datasetVersion" | "trajectoryId" | "frameId",
  "datasetId" | "datasetVersion" | "trajectoryId" | "frameId" | "artifactId" | "artifactChecksum"
>;

export type WorkspacePhononQPointSelectionRef = WorkspaceSelectionRefFor<
  "PHONON_Q_POINT",
  "datasetId" | "datasetVersion" | "phononArtifactId" | "artifactChecksum" | "qPointId",
  | "datasetId" | "datasetVersion" | "phononArtifactId" | "artifactChecksum" | "qPointId"
  | "branchId"
>;

export type WorkspacePhononBranchSelectionRef = WorkspaceSelectionRefFor<
  "PHONON_BRANCH",
  "datasetId" | "datasetVersion" | "phononArtifactId" | "artifactChecksum" | "branchId",
  | "datasetId" | "datasetVersion" | "phononArtifactId" | "artifactChecksum" | "branchId"
  | "qPointId"
>;

export type WorkspaceReciprocalPointSelectionRef = WorkspaceSelectionRefFor<
  "RECIPROCAL_POINT",
  "datasetId" | "datasetVersion" | "reciprocalArtifactId" | "artifactChecksum" | "reciprocalPointId",
  | "datasetId" | "datasetVersion" | "reciprocalArtifactId" | "artifactChecksum"
  | "reciprocalPointId" | "segmentId"
>;

export type WorkspaceVolumetricFieldSelectionRef = WorkspaceSelectionRefFor<
  "VOLUMETRIC_FIELD",
  "datasetId" | "datasetVersion" | "fieldId" | "artifactId" | "artifactChecksum",
  "datasetId" | "datasetVersion" | "fieldId" | "artifactId" | "artifactChecksum" | "regionId"
>;

export type WorkspaceArtifactSelectionRef = WorkspaceSelectionRefFor<
  "ARTIFACT",
  "jobId" | "artifactId" | "artifactChecksum" | "artifactContract" | "artifactVersion",
  "jobId" | "artifactId" | "artifactChecksum" | "artifactContract" | "artifactVersion" | "toolCallId"
>;

export type WorkspaceEvidenceItemSelectionRef = WorkspaceSelectionRefFor<
  "EVIDENCE_ITEM",
  | "jobId" | "bundleId" | "bundleHash" | "evidenceItemId"
  | "sourceArtifactId" | "sourceArtifactChecksum" | "fieldLocator",
  | "jobId" | "bundleId" | "bundleHash" | "evidenceItemId"
  | "sourceArtifactId" | "sourceArtifactChecksum" | "fieldLocator" | "claimId"
>;

export type WorkspaceClaimSelectionRef = WorkspaceSelectionRefFor<
  "CLAIM",
  "jobId" | "interpretationId" | "interpretationHash" | "claimId",
  "jobId" | "interpretationId" | "interpretationHash" | "claimId" | "evidenceItemId"
>;

export type WorkspaceSelectionRef =
  | WorkspaceDatasetSampleSelectionRef
  | WorkspaceMaterialObjectSelectionRef
  | WorkspaceStructureSelectionRef
  | WorkspacePeriodicSiteSelectionRef
  | WorkspaceLocalEnvironmentSelectionRef
  | WorkspaceCoordinationPolyhedronSelectionRef
  | WorkspacePolyhedronVertexSelectionRef
  | WorkspacePolyhedronFaceSelectionRef
  | WorkspaceTrajectoryAtomSelectionRef
  | WorkspaceTrajectoryFrameSelectionRef
  | WorkspacePhononQPointSelectionRef
  | WorkspacePhononBranchSelectionRef
  | WorkspaceReciprocalPointSelectionRef
  | WorkspaceVolumetricFieldSelectionRef
  | WorkspaceArtifactSelectionRef
  | WorkspaceEvidenceItemSelectionRef
  | WorkspaceClaimSelectionRef;

export type WorkspaceSelectionContext = {
  schemaVersion: "1.0";
  sourceScopeHash: string;
  primary?: WorkspaceSelectionRef | null;
  secondary: WorkspaceSelectionRef[];
  propagation: "EXACT_COMPATIBLE_ONLY";
  compatibility: "EXACT" | "NOT_APPLICABLE" | "STALE" | "UNSUPPORTED";
  cleared: boolean;
};

export type WorkspaceLayoutState = {
  schemaVersion: "1.0";
  activePanelId?: string | null;
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
  selection?: WorkspaceSelectionContext | null;
  semanticHash: string;
  createdBy: string;
  createdAt: string;
};

export type ScientificWorkspace = {
  schemaVersion: "1.0";
  workspaceId: string;
  projectId: string;
  sourceJobId: string;
  sourceReferenceHash: string;
  datasetId?: string | null;
  datasetVersion?: string | null;
  profileId?: string | null;
  profileSemanticHash?: string | null;
  intentId?: string | null;
  intentSemanticHash?: string | null;
  planId?: string | null;
  planHash?: string | null;
  planSchemaVersion?: "0.1" | "0.2" | null;
  title: string;
  activePanelId?: string | null;
  pinnedSelection?: WorkspaceSelectionContext | null;
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
