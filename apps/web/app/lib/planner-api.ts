export type PlannerJobRequest = {
  userPrompt: string;
  projectId: string;
  datasetId: string;
  profileId?: string;
  enqueue: boolean;
  provider?: string;
  baseUrl?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
  timeoutSeconds?: number;
  thinkingMode?: "quick" | "standard" | "deep";
  intentSchemaVersion?: "1.0";
  intentId?: string;
  selectedResourceIds?: string[];
  selectedTargetIds?: string[];
  researchSessionId?: string;
};

export const SUPPORTED_DATA_PROFILE_CONTRACT_VERSIONS = ["2.0", "2.1", "2.2", "2.3", "2.4"] as const;
export type SupportedDataProfileContractVersion = (typeof SUPPORTED_DATA_PROFILE_CONTRACT_VERSIONS)[number];

export function isSupportedDataProfileContractVersion(value: unknown): value is SupportedDataProfileContractVersion {
  return typeof value === "string" && (SUPPORTED_DATA_PROFILE_CONTRACT_VERSIONS as readonly string[]).includes(value);
}

export function isTerminalPlannerJobStatus(status: string): boolean {
  return ["completed", "failed", "partial_success"].includes(status);
}

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
    resourceRefs: Array<{ objectId: string; objectType: string; objectHash: string; kind: string; origin: string; versionId?: string; displayName?: string }>;
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
  provenance: { provider: "deterministic_mock" | "openai_compatible" | "deepseek"; model: string; promptVersion: string; createdAt: string; parentIntentId?: string | null; answerBindings: Array<{ questionId: string; selectedValues: string[] }> };
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
  graphHash?: string;
  dependencyBindings?: DependencyBinding[];
};

export type DependencyBinding = {
  bindingId: string;
  producerStepId: string;
  producerOutputPort: string;
  consumerStepId: string;
  consumerInputPort: string;
  artifactKind: string;
  artifactContractVersion: string;
  mediaType: string;
  cardinality: "EXACTLY_ONE";
};

export type DependencyStepExecution = {
  stepId: string;
  toolId: string;
  state: "PENDING" | "READY" | "RUNNING" | "SUCCEEDED" | "FAILED" | "BLOCKED_DEPENDENCY" | "NOT_STARTED";
  toolCallId?: string | null;
  artifactIds: string[];
  blockedByStepIds: string[];
  errorCode?: string | null;
  errorMessage?: string | null;
};

export type DependencyExecutionRecord = {
  executionId: string;
  executionHash: string;
  outcome: "ALL_SUCCEEDED" | "PARTIAL_RESULTS" | "ALL_FAILED" | "VALIDATION_ABORTED";
  graphHash: string;
  topologicalOrder: string[];
  steps: DependencyStepExecution[];
  bindings: Array<{ bindingId: string; state: string; artifactId?: string | null; errorCode?: string | null }>;
  succeededCount: number;
  failedCount: number;
  blockedCount: number;
  notStartedCount: number;
  partialArtifactIds: string[];
};

export type ArtifactLineage = {
  lineageId: string;
  artifactId: string;
  artifactKind: string;
  producerStepId: string;
  producerToolId: string;
  outputPort: string;
  upstreamArtifactIds: string[];
  bindingIds: string[];
  contentHash: string;
};

export type DependencyAudit = {
  jobId?: string;
  planId?: string | null;
  planHash?: string | null;
  planSchemaVersion?: string | null;
  graphHash?: string | null;
  dependencyBindings: DependencyBinding[];
  plannedBindingRecords: Array<Record<string, unknown>>;
  topologicalOrder: string[];
  execution?: DependencyExecutionRecord | null;
  bindingResolutions: Array<Record<string, unknown>>;
  artifactLineage: ArtifactLineage[];
};

export type CapabilityPlanningOutcome =
  | "PLAN_READY"
  | "NEEDS_CLARIFICATION"
  | "UNSUPPORTED"
  | "CAPABILITY_MISMATCH"
  | "VALIDATION_FAILED";

export type CapabilityDiagnostic = {
  code: string;
  field: string;
  message: string;
  toolId?: string | null;
  repairable: boolean;
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
  resourceIdentities: Array<{ objectId: string; objectType: string; objectHash: string; kind: string }>;
  evaluatedCandidates: Array<{
    toolId: string;
    toolName: string;
    toolVersion: string;
    eligible: boolean;
    reasons: CapabilityDiagnostic[];
  }>;
  eligibleToolIds: string[];
  rejectedToolIds: string[];
  diagnostics: CapabilityDiagnostic[];
  warnings: CapabilityDiagnostic[];
  provenance: { resolver: string; resolverVersion: string };
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
  selections: Array<{
    toolId: string;
    toolName: string;
    toolVersion: string;
    coveredScientificIntents: AnalysisIntentScientificIntent[];
    coveredCapabilityNeeds: AnalysisIntentCapabilityNeed[];
    coveredDesiredOutputs: AnalysisIntentDesiredOutput[];
    inputResourceIds: string[];
    targetSemanticIds: string[];
    boundParameters: Array<{
      parameter: string;
      value: string | number | boolean | string[];
      valueId: string;
      source: string;
      sourceIdentity: string;
    }>;
    artifactTypes: string[];
    rankFacts: Array<number | string>;
  }>;
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
  capability_outcome?: CapabilityPlanningOutcome | null;
  eligibility_resolution?: EligibilityResolution | null;
  capability_decision?: CapabilityPlanningDecision | null;
  provider_visible_tool_ids?: string[];
  plan_schema_version?: string | null;
  graph_hash?: string | null;
  dependency_bindings?: DependencyBinding[];
  topological_order?: string[];
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
  capabilityPlanningOutcome?: CapabilityPlanningOutcome | null;
  eligibilityResolution?: EligibilityResolution | null;
  capabilityDecision?: CapabilityPlanningDecision | null;
  dependencyExecutionSummary?: { executionId?: string; outcome?: string; graphHash?: string; succeededCount?: number; failedCount?: number; blockedCount?: number; notStartedCount?: number } | null;
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
  version?: string;
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

export type ScientificEvidenceItem = {
  schemaVersion: "1.0";
  evidenceItemId: string;
  semanticRole: string;
  evidenceKind: "SCALAR" | "RANGE" | "CATEGORY" | "COUNT" | "BOOLEAN" | "ORDERED_SERIES_SUMMARY" | "TABLE_ROW" | "WARNING" | "LIMITATION" | "EXECUTION_STATE" | "PROVENANCE";
  subjectId: string;
  displayValue: string;
  unit?: string | null;
  sourceArtifactId: string;
  sourceArtifactChecksum: string;
  artifactContract: string;
  artifactContractVersion: string;
  sourceToolId: string;
  sourceToolVersion: string;
  fieldLocator: { fieldId: string; semanticKey?: string | null; entityId?: string | null };
  warnings: string[];
  limitations: string[];
};

export type ScientificClaim = {
  schemaVersion: "1.0";
  claimId: string;
  claimType: "OBSERVATION" | "COMPARISON" | "ANOMALY" | "WARNING" | "LIMITATION" | "RECOMMENDATION" | "NO_SUPPORTED_CONCLUSION";
  subjectEvidenceIds: string[];
  supportingEvidenceIds: string[];
  limitingEvidenceIds: string[];
  contradictingEvidenceIds: string[];
  semanticPredicate: string;
  qualifiers: string[];
  renderedText: string;
  scope: string;
  confidenceClass: "DIRECT" | "QUALIFIED" | "LIMITED";
  groundingStatus: "GROUNDED" | "REJECTED";
  displayOrder: number;
};

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
  recommendations: Array<{
    recommendationId: string;
    reasonEvidenceIds: string[];
    suggestedGoalCategory: string;
    expectedMissingEvidence: string[];
    limitation: string;
    executionAuthorized: false;
    planCreated: false;
    jobCreated: false;
  }>;
  completeness: "COMPLETE" | "PARTIAL" | "NONE";
  partialResultState: boolean;
  repairCount: 0 | 1;
  validationOutcome: string;
  executionRecordId: string;
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
  repairCount: 0 | 1;
  outcome: InterpretationResponse["outcome"];
  diagnostics: string[];
  evidenceItemCount: number;
  claimCount: number;
};

export type InterpretationResponse = {
  outcome: "INTERPRETATION_READY" | "INTERPRETATION_READY_WITH_LIMITS" | "NO_SUPPORTED_EVIDENCE" | "SOURCE_NOT_TERMINAL" | "SOURCE_INTEGRITY_FAILED" | "EVIDENCE_CAP_EXCEEDED" | "PROVIDER_FAILED" | "VALIDATION_FAILED";
  interpretationId?: string | null;
  bundleId?: string | null;
  bundleHash?: string | null;
  sourceJobId?: string | null;
  sourcePlanId?: string | null;
  sourcePlanHash?: string | null;
  sourceGraphHash?: string | null;
  mode?: "DETERMINISTIC" | "STRICT_PROVIDER" | null;
  claims: ScientificClaim[];
  warnings: string[];
  limitations: string[];
  recommendations: GroundedScientificInterpretation["recommendations"];
  partialResultState: boolean;
  repairCount: number;
  diagnostics: string[];
  evidenceItemCount: number;
  noExecution: {
    toolCallCreated: false;
    planCreated: false;
    jobCreated: false;
    enqueued: false;
    recommendationExecutionAuthorized: false;
  };
  execution?: InterpretationExecutionRecord | null;
  interpretation?: GroundedScientificInterpretation | null;
};

export type PlannerJobInterpretationsResponse = {
  jobId: string;
  interpretations: GroundedScientificInterpretation[];
  runs: InterpretationExecutionRecord[];
  count: number;
  runCount: number;
};

export type InterpretationEvidenceResponse = {
  interpretationId: string;
  bundleId: string;
  bundleHash: string;
  jobId?: string;
  planId?: string;
  evidenceItems: ScientificEvidenceItem[];
  sourceArtifactIds: string[];
  sourceObjectRefs?: Array<{
    objectId: string;
    versionId: string;
    objectType?: string;
    displayName?: string;
  }>;
  artifacts?: Artifact[];
  toolCalls?: Array<{
    id?: string;
    toolCallId?: string;
    toolId?: string;
    status?: string;
  }>;
  bundleWarnings: string[];
  bundleLimitations: string[];
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
  createdAt?: string;
  updatedAt?: string;
};

export type DatasetDetail = DatasetOption & {
  demo?: boolean;
  files?: Array<Record<string, unknown>>;
};

export type DatasetSourceResource = {
  objectId: string;
  objectType: string;
  objectHash?: string;
  datasetId: string;
  versionId?: string;
  displayName?: string;
  payload: unknown;
};

export type PromotedDatasetTable = {
  object: {
    id: string;
    project_id?: string;
    object_type?: string;
    display_name?: string;
    current_version_id?: string | null;
  };
  version: {
    id: string;
    scientific_object_id?: string;
    object_type?: string;
    source_resource_refs_json?: unknown;
    content_hash?: string;
    semantic_hash?: string;
  };
};

export type ProjectSummary = {
  id: string;
  projectId?: string;
  name: string;
  role?: string;
  description?: string | null;
  status?: string | null;
  pinned?: boolean;
  tags?: string[];
  createdAt?: string | null;
  updatedAt?: string | null;
};

export type ProductSearchItem = {
  kind: "project" | "dataset" | "scientific_object" | "research" | "report" | "result";
  id: string;
  projectId: string;
  title: string;
  subtitle: string;
  href: string;
  researchTurnId?: string | null;
  status?: string | null;
  updatedAt?: string | null;
};

export type ProductSearchResponse = {
  query: string;
  items: ProductSearchItem[];
  count: number;
  truncated?: boolean;
  nextCursor?: string | null;
};

export type ProjectHistory = {
  schemaVersion: string;
  project: ProjectSummary;
  summary: {
    datasetCount: number;
    analysisCount: number;
    completedAnalysisCount: number;
    artifactCount: number;
    workspaceCount: number;
    reportCount: number;
    lastActivityAt?: string | null;
  };
  datasets: Array<{
    datasetId: string;
    name: string;
    status: string;
    createdAt?: string | null;
    updatedAt?: string | null;
    analysisCount: number;
    lastAnalysisStatus?: string | null;
    process: Array<{
      key: string;
      label: string;
      status: string;
      detail: string;
    }>;
    resultSummary: {
      artifactCount: number;
      workspaceCount: number;
      interpretationCount: number;
      reportCount: number;
      recipeCount: number;
      artifactTypes: string[];
      latestReportStatus?: string | null;
    };
    import: {
      fileCount: number;
      files: Array<Record<string, unknown>>;
      resources: Array<Record<string, unknown>>;
      parseOutcome: string;
    };
    profile?: {
      profileId?: string;
      version?: string;
      profileContractVersion?: string;
      datasetType?: string;
      rowCount?: number;
      columnCount?: number;
      objectCount?: number;
      semanticRoles?: Record<string, number>;
      readyCapabilities?: string[];
      blockedCapabilities?: string[];
      warnings?: string[];
    } | null;
  }>;
  analyses: Array<{
    jobId: string;
    datasetId?: string;
    status: string;
    createdAt?: string | null;
    updatedAt?: string | null;
    userQuestion?: string | null;
    toolIds: string[];
    stepCount: number;
    artifactCount: number;
    artifactTypes: string[];
    interpretationCount: number;
    reportCount: number;
    recipeCount: number;
    workspaceId?: string | null;
    workspaceTitle?: string | null;
    archived?: boolean;
    visibleInReports?: boolean;
    researchSessionId?: string;
    researchTurnId?: string | null;
    researchTurnStatus?: string | null;
    researchContextKind?: "RESEARCH_TURN" | "LEGACY_SESSION_RUN" | null;
  }>;
  activity: Array<{
    activityId: string;
    kind: string;
    title: string;
    detail: string;
    status?: string | null;
    occurredAt?: string | null;
    datasetId?: string;
    jobId?: string;
    workspaceId?: string | null;
    href: string;
  }>;
  pagination?: {
    datasets: { nextCursor: string | null };
    analyses: { nextCursor: string | null };
    activity: { nextCursor: string | null };
  };
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
  profileContractVersion?: SupportedDataProfileContractVersion;
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
  kind?: string;
  baseUrl?: string;
  defaultModel?: string;
  allowedModels?: string[];
  requiresSecret?: boolean;
  secretSource?: string;
  execution?: "live" | "offline" | "unavailable" | string;
  description?: string;
  configurationSource?: string;
  developerOnly?: boolean;
  models?: string[];
  secretConfigured?: boolean;
  thinkingModes?: Array<{ id: string; label: string; description?: string }>;
};

export type ProviderStatus = {
  ok?: boolean;
  provider?: string;
  kind?: string;
  baseUrl?: string | null;
  model?: string;
  status?: string;
  message?: string;
  redacted?: boolean;
  configurationSource?: string;
  secretSource?: string | null;
  execution?: "live" | "offline" | "unavailable" | string;
  allowedModels?: string[];
  errorType?: string | null;
  configured?: boolean;
  thinkingModes?: Array<{ id: string; label: string; description?: string }>;
};

export type ProviderResolveRequest = {
  provider: string;
  baseUrl?: string;
  model?: string;
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
  temperature?: number;
  maxTokens?: number;
  timeoutSeconds?: number;
};

export type ProviderTestResult = {
  ok: boolean;
  provider?: string;
  kind?: string;
  baseUrl?: string | null;
  model?: string;
  latencyMs?: number;
  validated?: boolean;
  message?: string;
  errorType?: string;
  safeDetails?: string;
  suggestions?: string[];
  redacted?: boolean;
};

export type ProviderConfigureRequest = {
  provider: string;
  label?: string;
  kind?: "openai_compatible";
  baseUrl: string;
  apiKey?: string;
  defaultModel?: string;
  modelIds?: string[];
};

export type ProviderModelList = {
  ok: boolean;
  provider: string;
  models: string[];
  source?: string;
  message?: string;
};

export type UploadDatasetRequest = {
  projectId: string;
  datasetName: string;
  files: Array<{
    fileName: string;
    content: string;
    importKind?: "phonon_band" | "phonon_dos";
    contractVersion?: string;
  }>;
};

export type UploadDatasetFile = {
  file: File;
  importKind?: "phonon_band" | "phonon_dos";
  contractVersion?: string;
  companionGroupId?: string;
};

type UploadSession = {
  uploadSessionId: string;
  files: Array<{
    fileId: string;
    clientFileId: string;
    byteSize: number;
    sha256: string;
  }>;
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

const API_BASE = normalizeBaseUrl(process.env.NEXT_PUBLIC_MDI_API_BASE_URL || (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api"));

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

export async function getPlannerJob(
  jobId: string,
  options: Readonly<{ signal?: AbortSignal }> = {},
): Promise<PlannerJobDetail> {
  return apiFetch<PlannerJobDetail>(
    `/planner/jobs/${encodeURIComponent(jobId)}`,
    { signal: options.signal },
  );
}

export async function getPlannerJobEvents(
  jobId: string,
  afterSeq = 0,
  options: Readonly<{ signal?: AbortSignal }> = {},
): Promise<JobEvent[]> {
  const query = afterSeq > 0 ? `?after_seq=${encodeURIComponent(String(afterSeq))}` : "";
  return apiFetch<JobEvent[]>(
    `/planner/jobs/${encodeURIComponent(jobId)}/events${query}`,
    { signal: options.signal },
  );
}

export function getPlannerJobEventsStreamUrl(jobId: string, afterSeq = 0): string {
  const query = afterSeq > 0 ? `?after_seq=${encodeURIComponent(String(afterSeq))}` : "";
  return `${API_BASE}/planner/jobs/${encodeURIComponent(jobId)}/events/stream${query}`;
}

export async function getPlannerJobToolCalls(jobId: string): Promise<ToolCall[]> {
  return apiFetch<ToolCall[]>(`/planner/jobs/${encodeURIComponent(jobId)}/tool-calls`);
}

export async function getPlannerJobArtifacts(jobId: string, options: Readonly<{ signal?: AbortSignal }> = {}): Promise<Artifact[]> {
  return apiFetch<Artifact[]>(`/planner/jobs/${encodeURIComponent(jobId)}/artifacts`, { signal: options.signal });
}

export async function getPlannerJobDependencies(jobId: string): Promise<DependencyAudit> {
  return apiFetch<DependencyAudit>(`/planner/jobs/${encodeURIComponent(jobId)}/dependencies`);
}

export async function createPlannerJobInterpretation(
  jobId: string,
  expectedPlanHash: string,
  options: Readonly<{
    mode?: "DETERMINISTIC" | "STRICT_PROVIDER";
    provider?: string;
    baseUrl?: string;
    model?: string;
    temperature?: number;
    maxTokens?: number;
    timeoutSeconds?: number;
    idempotencyKey?: string;
  }> = {},
): Promise<InterpretationResponse> {
  return apiFetch<InterpretationResponse>(`/planner/jobs/${encodeURIComponent(jobId)}/interpretations`, {
    method: "POST",
    body: JSON.stringify({ mode: options.mode || "DETERMINISTIC", expectedPlanHash, ...options }),
  });
}

export async function getPlannerJobInterpretations(
  jobId: string,
  options: Readonly<{ signal?: AbortSignal }> = {},
): Promise<PlannerJobInterpretationsResponse> {
  return apiFetch<PlannerJobInterpretationsResponse>(
    `/planner/jobs/${encodeURIComponent(jobId)}/interpretations`,
    { signal: options.signal },
  );
}

export async function getPlannerInterpretationEvidence(
  interpretationId: string,
  options: Readonly<{ signal?: AbortSignal }> = {},
): Promise<InterpretationEvidenceResponse> {
  return apiFetch<InterpretationEvidenceResponse>(
    `/planner/interpretations/${encodeURIComponent(interpretationId)}/evidence`,
    { signal: options.signal },
  );
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
    { method: "GET", signal: options.signal, credentials: "include" },
  );
  if (!response.ok) {
    if (response.status === 401 && typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("mdi:session-expired"));
    }
    const text = await response.text();
    const body = text ? safeParseJson(text) : null;
    throw new PlannerApiError(
      errorMessage(body) || "Artifact content could not be loaded.",
      response.status,
      body,
    );
  }
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

const PRODUCT_DIRECTORY_CACHE_TTL_MS = 20_000;
let datasetsDirectoryCache: { expiresAt: number; promise: Promise<DatasetOption[]> } | null = null;
let projectsDirectoryCache: { expiresAt: number; promise: Promise<ProjectSummary[]> } | null = null;

export function invalidateProductDirectories(): void {
  datasetsDirectoryCache = null;
  projectsDirectoryCache = null;
}

export async function listDatasets(options: Readonly<{ forceRefresh?: boolean }> = {}): Promise<DatasetOption[]> {
  if (!options.forceRefresh && datasetsDirectoryCache && datasetsDirectoryCache.expiresAt > Date.now()) {
    return datasetsDirectoryCache.promise;
  }
  const promise = apiFetch<DatasetOption[] | { value: DatasetOption[] }>("/datasets")
    .then((result) => Array.isArray(result) ? result : result.value)
    .catch((error) => {
      datasetsDirectoryCache = null;
      throw error;
    });
  datasetsDirectoryCache = { expiresAt: Date.now() + PRODUCT_DIRECTORY_CACHE_TTL_MS, promise };
  return promise;
}

export async function listProjects(options: Readonly<{ forceRefresh?: boolean }> = {}): Promise<ProjectSummary[]> {
  if (!options.forceRefresh && projectsDirectoryCache && projectsDirectoryCache.expiresAt > Date.now()) {
    return projectsDirectoryCache.promise;
  }
  const promise = apiFetch<ProjectSummary[] | { value: ProjectSummary[] }>("/projects")
    .then((result) => Array.isArray(result) ? result : result.value)
    .catch((error) => {
      projectsDirectoryCache = null;
      throw error;
    });
  projectsDirectoryCache = { expiresAt: Date.now() + PRODUCT_DIRECTORY_CACHE_TTL_MS, promise };
  return promise;
}

export async function searchProduct(
  query: string,
  options: {
    projectId?: string;
    kind?: ProductSearchItem["kind"];
    status?: "active" | "archived" | "trashed" | "all";
    limit?: number;
    cursor?: string;
    dateFrom?: string;
    dateTo?: string;
    signal?: AbortSignal;
  } = {},
): Promise<ProductSearchResponse> {
  const params = new URLSearchParams();
  if (query.trim()) params.set("q", query.trim());
  if (options.projectId) params.set("project_id", options.projectId);
  if (options.kind) params.set("kind", options.kind);
  if (options.status) params.set("status", options.status);
  if (options.limit) params.set("limit", String(options.limit));
  if (options.cursor) params.set("cursor", options.cursor);
  if (options.dateFrom) params.set("date_from", options.dateFrom);
  if (options.dateTo) params.set("date_to", options.dateTo);
  return apiFetch<ProductSearchResponse>(`/search?${params.toString()}`, {
    signal: options.signal,
  });
}

export async function createProject(name: string): Promise<ProjectSummary> {
  const project = await apiFetch<ProjectSummary>("/projects", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
  invalidateProjectHistory();
  invalidateProductDirectories();
  return project;
}

export async function updateProject(
  projectId: string,
  changes: Readonly<{
    name?: string;
    description?: string;
    archived?: boolean;
    lifecycle?: "ACTIVE" | "ARCHIVED" | "TRASHED";
    pinned?: boolean;
    tags?: string[];
  }>,
): Promise<ProjectSummary> {
  const project = await apiFetch<ProjectSummary>(`/projects/${encodeURIComponent(projectId)}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });
  invalidateProjectHistory(projectId);
  invalidateProductDirectories();
  return project;
}

export async function bulkProjectAction(
  projectIds: string[],
  action: "archive" | "trash" | "restore" | "pin" | "unpin",
): Promise<{ action: "archive" | "trash" | "restore" | "pin" | "unpin"; projectIds: string[]; count: number }> {
  const result = await apiFetch<{ action: "archive" | "trash" | "restore" | "pin" | "unpin"; projectIds: string[]; count: number }>("/projects/bulk", {
    method: "POST",
    body: JSON.stringify({ projectIds, action }),
  });
  projectIds.forEach((projectId) => invalidateProjectHistory(projectId));
  invalidateProductDirectories();
  return result;
}

export async function deleteEmptyProject(projectId: string): Promise<{ projectId: string; deleted: boolean }> {
  const result = await apiFetch<{ projectId: string; deleted: boolean }>(
    `/projects/${encodeURIComponent(projectId)}`,
    { method: "DELETE" },
  );
  invalidateProjectHistory(projectId);
  invalidateProductDirectories();
  return result;
}

export type DependencyImpact = {
  entity: "project" | "dataset";
  entityId: string;
  displayName: string;
  canDelete: boolean;
  dependencyCount: number;
  dependencies: Array<{ kind: string; label: string; count: number; href?: string }>;
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
  };
};

export async function getProjectDependencyImpact(projectId: string): Promise<DependencyImpact> {
  return apiFetch<DependencyImpact>(`/projects/${encodeURIComponent(projectId)}/dependency-impact`);
}

export type ProjectExportManifest = Readonly<{
  schemaVersion: string;
  exportKind: "authorized_project_provenance";
  executable: false;
  generatedAt: string;
  project: Readonly<{
    id: string;
    name: string;
    description: string;
    status: string;
    pinned: boolean;
    tags: string[];
    role: string;
  }>;
  datasets: ReadonlyArray<Record<string, unknown>>;
  scientificObjects: ReadonlyArray<Record<string, unknown>>;
  scientificObjectVersions: ReadonlyArray<Record<string, unknown>>;
  researchSessions: ReadonlyArray<Record<string, unknown>>;
  researchTurns: ReadonlyArray<Record<string, unknown>>;
  scientificResults: ReadonlyArray<Record<string, unknown>>;
  reports: ReadonlyArray<Record<string, unknown>>;
  bounds: Readonly<{ truncated: Readonly<Record<string, boolean>> }>;
  excluded: ReadonlyArray<string>;
}>;

export async function getProjectExportManifest(projectId: string): Promise<ProjectExportManifest> {
  return apiFetch<ProjectExportManifest>(
    `/projects/${encodeURIComponent(projectId)}/export-manifest`,
  );
}

// Project history is explicitly invalidated by every product mutation below.
// Keep read-only route transitions warm long enough for a researcher to inspect
// a Viewer before moving into Research, instead of reloading the same project
// ledger after a few seconds.
const PROJECT_HISTORY_WARM_TTL_MS = 30_000;
const projectHistoryRequests = new Map<
  string,
  { expiresAt: number; promise: Promise<ProjectHistory>; value?: ProjectHistory }
>();

export function invalidateProjectHistory(projectId?: string): void {
  if (projectId) projectHistoryRequests.delete(projectId);
  else projectHistoryRequests.clear();
}

/**
 * Return the last successfully resolved history snapshot without starting a
 * request. Route components use this to paint immediately after navigation
 * when ProductShell has already warmed the same project ledger.
 */
export function getCachedProjectHistory(projectId: string): ProjectHistory | null {
  const cached = projectHistoryRequests.get(projectId);
  if (!cached || cached.expiresAt <= Date.now() || !cached.value) return null;
  return cached.value;
}

export async function getProjectHistory(
  projectId: string,
  options: Readonly<{ forceRefresh?: boolean; limit?: number; datasetsCursor?: string; analysesCursor?: string; activityCursor?: string }> = {},
): Promise<ProjectHistory> {
  const continuation = Boolean(options.datasetsCursor || options.analysesCursor || options.activityCursor);
  const cacheable = !continuation;
  const requestsBoundedPage = options.limit !== undefined;
  const cached = projectHistoryRequests.get(projectId);
  if (
    cacheable
    && !options.forceRefresh
    && cached
    && cached.expiresAt > Date.now()
    && (!requestsBoundedPage || cached.value?.pagination)
  ) {
    return cached.promise;
  }
  const promise = apiFetch<ProjectHistory>(
    "/projects/" + encodeURIComponent(projectId) + "/history" + historyQuery(options),
  ).then((value) => {
    const current = projectHistoryRequests.get(projectId);
    if (cacheable && current?.promise === promise) current.value = value;
    return value;
  }).catch((error) => {
    const current = projectHistoryRequests.get(projectId);
    if (cacheable && current?.promise === promise) projectHistoryRequests.delete(projectId);
    throw error;
  });
  if (cacheable) {
    projectHistoryRequests.set(projectId, {
      expiresAt: Date.now() + PROJECT_HISTORY_WARM_TTL_MS,
      promise,
    });
  }
  return promise;
}

function historyQuery(options: Readonly<{ limit?: number; datasetsCursor?: string; analysesCursor?: string; activityCursor?: string }>): string {
  const params = new URLSearchParams();
  if (options.limit !== undefined) params.set("limit", String(Math.max(1, Math.min(100, Math.floor(options.limit)))));
  if (options.datasetsCursor) params.set("datasets_cursor", options.datasetsCursor);
  if (options.analysesCursor) params.set("analyses_cursor", options.analysesCursor);
  if (options.activityCursor) params.set("activity_cursor", options.activityCursor);
  const query = params.toString();
  return query ? `?${query}` : "";
}

export async function archiveProjectRun(projectId: string, jobId: string): Promise<{ projectId: string; jobId: string; archived: boolean }> {
  const result = await apiFetch<{ projectId: string; jobId: string; archived: boolean }>(
    `/projects/${encodeURIComponent(projectId)}/runs/${encodeURIComponent(jobId)}/archive`,
    { method: "POST" },
  );
  invalidateProjectHistory(projectId);
  return result;
}

export async function restoreProjectRun(projectId: string, jobId: string): Promise<{ projectId: string; jobId: string; archived: boolean }> {
  const result = await apiFetch<{ projectId: string; jobId: string; archived: boolean }>(
    `/projects/${encodeURIComponent(projectId)}/runs/${encodeURIComponent(jobId)}/archive`,
    { method: "DELETE" },
  );
  invalidateProjectHistory(projectId);
  return result;
}

export async function getDataset(datasetId: string): Promise<DatasetDetail> {
  return apiFetch<DatasetDetail>(`/datasets/${encodeURIComponent(datasetId)}`);
}

export async function updateDataset(
  datasetId: string,
  changes: Readonly<{ name?: string; archived?: boolean; lifecycle?: "ACTIVE" | "ARCHIVED" | "TRASHED" }>,
): Promise<DatasetDetail> {
  const dataset = await apiFetch<DatasetDetail>(`/datasets/${encodeURIComponent(datasetId)}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });
  invalidateProjectHistory();
  invalidateProductDirectories();
  return dataset;
}

export async function bulkDatasetAction(
  datasetIds: string[],
  action: "archive" | "trash" | "restore",
): Promise<{ action: "archive" | "trash" | "restore"; datasetIds: string[]; count: number }> {
  const result = await apiFetch<{ action: "archive" | "trash" | "restore"; datasetIds: string[]; count: number }>("/datasets/bulk", {
    method: "POST",
    body: JSON.stringify({ datasetIds, action }),
  });
  invalidateProjectHistory();
  invalidateProductDirectories();
  return result;
}

export async function deleteEmptyDataset(datasetId: string): Promise<{ datasetId: string; deleted: boolean }> {
  const result = await apiFetch<{ datasetId: string; deleted: boolean }>(
    `/datasets/${encodeURIComponent(datasetId)}`,
    { method: "DELETE" },
  );
  invalidateProjectHistory();
  invalidateProductDirectories();
  return result;
}

export async function getDatasetDependencyImpact(datasetId: string): Promise<DependencyImpact> {
  return apiFetch<DependencyImpact>(`/datasets/${encodeURIComponent(datasetId)}/dependency-impact`);
}

export async function getDatasetSourceResources(datasetId: string, signal?: AbortSignal): Promise<DatasetSourceResource[]> {
  const result = await apiFetch<{ datasetId: string; resources: DatasetSourceResource[] }>(
    `/datasets/${encodeURIComponent(datasetId)}/object-store`,
    { signal },
  );
  return result.resources;
}

export async function promoteDatasetTable(
  projectId: string,
  datasetId: string,
  resourceId?: string,
): Promise<PromotedDatasetTable> {
  const result = await apiFetch<PromotedDatasetTable>(
    `/api/projects/${encodeURIComponent(projectId)}/datasets/${encodeURIComponent(datasetId)}/scientific-table`,
    {
      method: "POST",
      body: JSON.stringify(resourceId ? { resource_id: resourceId } : {}),
    },
  );
  invalidateProjectHistory(projectId);
  return result;
}

export async function admitDatasetResource(
  projectId: string,
  datasetId: string,
  resourceId: string,
  displayName?: string,
): Promise<PromotedDatasetTable> {
  const result = await apiFetch<PromotedDatasetTable>(
    `/api/projects/${encodeURIComponent(projectId)}/scientific-objects`,
    {
      method: "POST",
      body: JSON.stringify({
        dataset_id: datasetId,
        resource_id: resourceId,
        ...(displayName?.trim() ? { display_name: displayName.trim() } : {}),
      }),
    },
  );
  invalidateProjectHistory(projectId);
  return result;
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

export async function uploadDatasetFiles(
  projectId: string,
  datasetName: string,
  files: UploadDatasetFile[],
): Promise<DatasetDetail & { profile?: DataProfileSummary }> {
  if (files.length === 0) throw new Error("UPLOAD_FILES_REQUIRED");
  const declared = await Promise.all(files.map(async (item, index) => {
    const bytes = await item.file.arrayBuffer();
    const sha256 = bytesToHex(await crypto.subtle.digest("SHA-256", bytes));
    return {
      item,
      declaration: {
        clientFileId: `client_${index + 1}_${sha256.slice(0, 12)}`,
        fileName: item.file.name,
        byteSize: item.file.size,
        sha256,
        importKind: item.importKind,
        contractVersion: item.contractVersion,
        companionGroupId: item.companionGroupId,
      },
    };
  }));
  const session = await apiFetch<UploadSession>(`/projects/${encodeURIComponent(projectId)}/upload-sessions`, {
    method: "POST",
    body: JSON.stringify({ datasetName, files: declared.map((item) => item.declaration) }),
  });
  const serverFiles = new Map(session.files.map((item) => [item.clientFileId, item]));
  try {
    await Promise.all(declared.map(async ({ item, declaration }) => {
      const serverFile = serverFiles.get(declaration.clientFileId);
      if (!serverFile) throw new Error("UPLOAD_SESSION_FILE_MAPPING_MISSING");
      const response = await fetch(
        `${API_BASE}/upload-sessions/${encodeURIComponent(session.uploadSessionId)}/files/${encodeURIComponent(serverFile.fileId)}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/octet-stream" },
          body: item.file,
          credentials: "include",
        },
      );
      if (!response.ok) {
        const text = await response.text();
        const body = text ? safeParseJson(text) : null;
        throw new PlannerApiError(errorMessage(body) || `Upload failed with status ${response.status}`, response.status, body);
      }
      const receipt = await response.json() as { byteSize?: number; sha256?: string };
      if (receipt.byteSize !== declaration.byteSize || receipt.sha256 !== declaration.sha256) {
        throw new Error("UPLOAD_SERVER_RECEIPT_MISMATCH");
      }
    }));
    const result = await apiFetch<DatasetDetail & { profile?: DataProfileSummary }>(
      `/upload-sessions/${encodeURIComponent(session.uploadSessionId)}/complete`,
      { method: "POST" },
    );
    invalidateProjectHistory(projectId);
    invalidateProductDirectories();
    return result;
  } catch (error) {
    await apiFetch(`/upload-sessions/${encodeURIComponent(session.uploadSessionId)}`, { method: "DELETE" }).catch(() => undefined);
    throw error;
  }
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

export async function configurePlannerProvider(payload: ProviderConfigureRequest): Promise<{ ok: boolean; provider: ProviderOption; message?: string }> {
  return apiFetch<{ ok: boolean; provider: ProviderOption; message?: string }>("/planner/providers/configure", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updatePlannerProviderModels(provider: string, modelIds: string[], defaultModel?: string): Promise<{ ok: boolean; provider: ProviderOption; message?: string }> {
  return apiFetch<{ ok: boolean; provider: ProviderOption; message?: string }>(`/planner/providers/${encodeURIComponent(provider)}/models`, {
    method: "PATCH",
    body: JSON.stringify({ modelIds, defaultModel }),
  });
}

export async function listProviderModels(provider: string): Promise<ProviderModelList> {
  return apiFetch<ProviderModelList>(`/planner/providers/${encodeURIComponent(provider)}/models`);
}

export async function removePlannerProvider(provider: string): Promise<{ ok: boolean; provider: string }> {
  return apiFetch<{ ok: boolean; provider: string }>(`/planner/providers/${encodeURIComponent(provider)}`, { method: "DELETE" });
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {})
    }
  });
  const text = await response.text();
  const body = text ? safeParseJson(text) : null;
  if (!response.ok) {
    if (response.status === 401 && typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("mdi:session-expired"));
    }
    const message = errorMessage(body) || `Request failed with status ${response.status}`;
    throw new PlannerApiError(message, response.status, body);
  }
  return unwrapFastApiListResponse(body) as T;
}

function normalizeBaseUrl(value: string): string {
  return value.endsWith("/") ? value.slice(0, -1) : value;
}

function bytesToHex(value: ArrayBuffer): string {
  return Array.from(new Uint8Array(value), (item) => item.toString(16).padStart(2, "0")).join("");
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
    if (detail && typeof detail === "object" && "message" in detail && typeof detail.message === "string") {
      return detail.message;
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
