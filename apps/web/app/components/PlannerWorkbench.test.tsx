import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import adapterGeneratedViewerScene from "../../../../docs/phase10f/evidence/phase10f12_viewer_scene_minimal_adapter/generated_viewer_scene.json";
import adapterGeneratedViewerSceneManifest from "../../../../docs/phase10f/evidence/phase10f12_viewer_scene_minimal_adapter/generated_viewer_scene_manifest.json";
import liveAdapterPayload from "../../../../docs/phase10f/evidence/phase10f13_viewer_scene_live_adapter_browser/live_payload.json";
import bzReciprocal from "../../../../docs/phase10i/evidence/phase10i1_brillouin_zone_adapter/artifacts/simple_cubic/reciprocal_lattice.json";
import bzZone from "../../../../docs/phase10i/evidence/phase10i1_brillouin_zone_adapter/artifacts/simple_cubic/brillouin_zone.json";
import bzKpath from "../../../../docs/phase10i/evidence/phase10i1_brillouin_zone_adapter/artifacts/simple_cubic/kpath.json";
import bzManifest from "../../../../docs/phase10i/evidence/phase10i1_brillouin_zone_adapter/artifacts/simple_cubic/brillouin_zone_manifest.json";
import { PlannerWorkbench, VolumetricMetadataPreviewPanel } from "./PlannerWorkbench";
import { isTerminalPlannerJobStatus } from "../lib/planner-api";
import { periodicBoundaryScene } from "./viewer-scene/viewerScenePeriodicBondTestFixture";

type CapturedLiveArtifact = { name?: string; content?: Record<string, unknown> };

const liveWarningArtifacts = (liveAdapterPayload as { cases: { warning_caps: { api: { artifacts: CapturedLiveArtifact[] } } } }).cases.warning_caps.api.artifacts;
const liveAdapterWarningViewerScene = capturedLiveArtifactContent("viewer_scene.json");
const liveAdapterWarningViewerSceneManifest = capturedLiveArtifactContent("viewer_scene_manifest.json");

function capturedLiveArtifactContent(name: string): Record<string, unknown> {
  const artifact = liveWarningArtifacts.find((item) => item.name === name);
  if (!artifact?.content) throw new Error(`Missing captured live adapter artifact: ${name}`);
  return artifact.content;
}

const plan = {
  schemaVersion: "0.1",
  goal: "compute metrics",
  datasetId: "dataset_demo",
  profileId: "profile_demo",
  toolRegistryVersion: "0.1.0",
  steps: [
    {
      stepId: "llm_step_1",
      toolId: "ml.basic_metrics",
      purpose: "Compute basic metrics",
      reason: "Use y_true and y_pred.",
      inputRefs: [{ refType: "normalized_object", ref: "ml_table", objectType: "DataFrame" }],
      params: { targetColumn: "y_true", predictionColumn: "y_pred" },
      output: { artifactTypes: ["metrics_json"] }
    }
  ],
  expectedArtifacts: [{ name: "metrics.json", type: "metrics_json", fromStepId: "llm_step_1" }]
};

const demoProfile = {
  profileId: "profile_demo",
  datasetId: "dataset_demo",
  datasetType: "ml",
  version: "0.1",
  createdAt: "2026-07-04T00:00:00Z",
  tableSummary: {
    nRows: 5,
    nColumns: 3,
    columns: [
      { name: "formula", dtype: "string", inferredRole: "formula" },
      { name: "y_true", dtype: "number", inferredRole: "target" },
      { name: "y_pred", dtype: "number", inferredRole: "prediction" }
    ]
  },
  structureSummary: { nStructures: 0, elements: [], formulaStats: { total: 5, uniqueCount: 5 } },
  profileContractVersion: "2.0" as const,
  semanticColumns: [
    { column: "formula", roles: [{ role: "material_formula", authority: "canonical_name" }] },
    { column: "y_true", roles: [{ role: "regression_target", authority: "canonical_name" }] },
    { column: "y_pred", roles: [{ role: "regression_prediction", authority: "canonical_name" }] }
  ],
  analysisReadiness: [
    { capability: "regression_evaluation", dataStatus: "READY" as const, platformStatus: "NOT_IMPLEMENTED" as const },
    { capability: "uncertainty_evaluation", dataStatus: "READY" as const, platformStatus: "NOT_IMPLEMENTED" as const },
    { capability: "classification_evaluation", dataStatus: "MISSING_REQUIRED_DATA" as const, platformStatus: "NOT_IMPLEMENTED" as const, reasons: ["MISSING:classification_target"] }
  ],
  profileCoverage: { policy: "complete" as const, rowsInspected: 5, totalRows: 5, columnsInspected: 3, totalColumns: 3 },
  qualityIssues: [{ code: "FORMULA_VALUES_PARTIALLY_INVALID" }]
};

const createdJob = {
  ok: true,
  job_id: "job_1",
  plan_id: "plan_1",
  plan_hash: "hash_1",
  validation_errors: [],
  plan,
  plan_source: "llm",
  planner_provider: "mock",
  enqueued: true,
  executed: false
};

const dependencyBindings = [
  {
    bindingId: "binding_band_combined",
    producerStepId: "step_band",
    producerOutputPort: "canonical-band",
    consumerStepId: "step_combined",
    consumerInputPort: "band",
    artifactKind: "phonon_band_json",
    artifactContractVersion: "phase10h.phonon_band.v1",
    mediaType: "application/json",
    cardinality: "EXACTLY_ONE" as const
  }
];

const dependencyPlan = {
  ...plan,
  schemaVersion: "0.2",
  graphHash: "f".repeat(64),
  steps: [
    { ...plan.steps[0], stepId: "step_combined", toolId: "phonon.band_dos", inputRefs: [], output: { artifactTypes: ["phonon_band_dos_json"] } },
    { ...plan.steps[0], stepId: "step_band", toolId: "phonon.band", inputRefs: [{ refType: "normalized_object", ref: "band_source", objectType: "PhononBand" }], output: { artifactTypes: ["phonon_band_json"] } }
  ],
  dependencyBindings
};

const dependencyAudit = {
  jobId: "job_1",
  planId: "plan_1",
  planHash: "hash_1",
  planSchemaVersion: "0.2",
  graphHash: dependencyPlan.graphHash,
  dependencyBindings,
  plannedBindingRecords: [],
  topologicalOrder: ["step_band", "step_combined"],
  bindingResolutions: [{ bindingId: dependencyBindings[0].bindingId, validationOutcome: "FAILED_PRODUCER" }],
  execution: {
    executionId: "execution_partial",
    executionHash: "a".repeat(64),
    outcome: "PARTIAL_RESULTS",
    graphHash: dependencyPlan.graphHash,
    topologicalOrder: ["step_band", "step_combined"],
    steps: [
      { stepId: "step_band", toolId: "phonon.band", state: "FAILED", artifactIds: [], blockedByStepIds: [], errorCode: "ADAPTER_EXECUTION_FAILED", errorMessage: "Fixture failure" },
      { stepId: "step_combined", toolId: "phonon.band_dos", state: "BLOCKED_DEPENDENCY", artifactIds: [], blockedByStepIds: ["step_band"] }
    ],
    bindings: [{ bindingId: dependencyBindings[0].bindingId, state: "FAILED_PRODUCER", errorCode: "FAILED_PRODUCER" }],
    succeededCount: 1,
    failedCount: 1,
    blockedCount: 1,
    notStartedCount: 0,
    partialArtifactIds: ["artifact_independent"]
  },
  artifactLineage: [{
    lineageId: "lineage_independent",
    artifactId: "artifact_independent",
    artifactKind: "table_json",
    producerStepId: "step_independent",
    producerToolId: "composition.summary",
    outputPort: "result-table_json",
    upstreamArtifactIds: [],
    bindingIds: [],
    contentHash: "b".repeat(64)
  }]
};

const baseIntent = {
  schemaVersion: "1.0" as const,
  intentId: "intent_ready",
  intentHash: "a".repeat(64),
  datasetId: "dataset_demo",
  profileId: "profile_demo",
  rawGoal: "Analyze this dataset.",
  normalizedGoal: "Analyze this dataset.",
  language: "en" as const,
  dataScope: {
    datasetId: "dataset_demo",
    datasetVersion: "2",
    profileId: "profile_demo",
    profileContractVersion: "2.0",
    profileSemanticHash: "b".repeat(64),
    resourceRefs: [{ objectId: "table_1", objectType: "DataFrame", objectHash: "c".repeat(64), kind: "dataframe", origin: "PROFILE_EXACT" }],
    modelIds: [],
    groupIds: []
  },
  scientificIntents: ["dataset_overview"],
  targetSemantics: [],
  desiredOutputs: ["summary", "plot"],
  requiredCapabilityNeeds: ["tabular_data"],
  optionalCapabilityNeeds: [],
  ambiguities: [],
  missingFacts: [],
  unsupportedReasons: [],
  outcome: "READY" as const,
  clarification: { round: 0, maxRounds: 1 as const, maxQuestionsPerRound: 3 as const, questions: [] },
  provenance: { provider: "deterministic_mock", model: "bounded-rules-v1", promptVersion: "phase10l1.intent.v1", parentIntentId: null },
  warnings: []
};

const clarificationIntent = {
  ...baseIntent,
  intentId: "intent_needs_clarification",
  outcome: "NEEDS_CLARIFICATION" as const,
  ambiguities: [{ code: "TARGET_SEMANTICS_AMBIGUOUS", field: "targetSemantics", message: "Multiple targets are available.", blocking: true }],
  clarification: {
    round: 0,
    maxRounds: 1 as const,
    maxQuestionsPerRound: 3 as const,
    questions: [{
      questionId: "select_model_target",
      code: "SELECT_TARGET",
      prompt: "Which model target should be evaluated?",
      type: "SELECT_ONE" as const,
      options: [
        { value: "target_a", label: "Formation energy", semanticId: "target_a" },
        { value: "target_b", label: "Band gap", semanticId: "target_b" }
      ],
      required: true,
      bindsTo: "targetSemantics"
    }]
  }
};

const unsupportedIntent = {
  ...baseIntent,
  intentId: "intent_unsupported",
  scientificIntents: [],
  outcome: "UNSUPPORTED" as const,
  unsupportedReasons: [{ code: "INTENT_FUTURE_FERMI_SURFACE", message: "Fermi Surface is Future Scope.", boundary: "FUTURE_SCOPE" }]
};

const capabilityResolution = {
  schemaVersion: "1.0",
  resolutionId: "resolution_demo",
  resolutionHash: "d".repeat(64),
  intentId: baseIntent.intentId,
  intentHash: baseIntent.intentHash,
  profileId: baseIntent.profileId,
  profileContractVersion: "2.0",
  profileSemanticHash: baseIntent.dataScope.profileSemanticHash,
  datasetId: baseIntent.datasetId,
  datasetVersion: baseIntent.dataScope.datasetVersion,
  registrySnapshotId: "registry_demo",
  registrySnapshotHash: "e".repeat(64),
  resourceIdentities: baseIntent.dataScope.resourceRefs,
  evaluatedCandidates: [
    { toolId: "dataset.materials_explorer", toolName: "Dataset Materials Explorer", toolVersion: "0.1.0", eligible: true, reasons: [] },
    { toolId: "ml.basic_metrics", toolName: "Basic Metrics", toolVersion: "0.1.0", eligible: false, reasons: [{ code: "SCIENTIFIC_INTENT_UNSUPPORTED", field: "scientificIntents", message: "Intent is not supported.", toolId: "ml.basic_metrics", repairable: false }] }
  ],
  eligibleToolIds: ["dataset.materials_explorer"],
  rejectedToolIds: ["ml.basic_metrics"],
  diagnostics: [],
  warnings: [],
  provenance: { resolver: "deterministic_eligibility_resolver", resolverVersion: "1.0" }
};

const capabilityDecision = {
  schemaVersion: "1.0",
  decisionId: "decision_demo",
  decisionHash: "f".repeat(64),
  intentId: baseIntent.intentId,
  intentHash: baseIntent.intentHash,
  profileId: baseIntent.profileId,
  profileSemanticHash: baseIntent.dataScope.profileSemanticHash,
  registrySnapshotId: capabilityResolution.registrySnapshotId,
  registrySnapshotHash: capabilityResolution.registrySnapshotHash,
  resolutionId: capabilityResolution.resolutionId,
  resolutionHash: capabilityResolution.resolutionHash,
  outcome: "PLAN_READY",
  selections: [{
    toolId: "dataset.materials_explorer",
    toolName: "Dataset Materials Explorer",
    toolVersion: "0.1.0",
    coveredScientificIntents: ["dataset_overview"],
    coveredCapabilityNeeds: ["tabular_data"],
    coveredDesiredOutputs: ["summary"],
    inputResourceIds: ["table_1"],
    targetSemanticIds: [],
    boundParameters: [{ parameter: "tableObjectId", value: "table_1", valueId: "resource:table_1", source: "RESOURCE_ID", sourceIdentity: "table_1" }],
    artifactTypes: ["table_json", "summary_md"],
    rankFacts: [1, 1, 1]
  }],
  unfulfilledDesiredOutputs: ["plot"],
  diagnostics: [],
  warnings: [{ code: "DESIRED_OUTPUT_UNFULFILLED", field: "desiredOutputs", message: "Plot is unavailable.", repairable: false }],
  provenance: { provider: "deterministic_mock", providerContractVersion: "1.0", model: "capability-ranker-v1", repairCount: 0, repairDiagnostics: [] }
};

const jobDetail = {
  jobId: "job_1",
  projectId: "project_local",
  datasetId: "dataset_demo",
  status: "completed",
  planId: "plan_1",
  planHash: "hash_1",
  planSource: "llm",
  analysisPlan: plan,
  validationStatus: "validated",
  toolCallCount: 1,
  artifactCount: 3,
  eventCount: 8,
  provenance: {
    planId: "plan_1",
    planHash: "hash_1",
    loadedFrom: "persisted_analysis_plan",
    binding: "jobs.plan_id -> analysis_plans.id",
    toolPath: "Tool Registry + Adapter",
    fallbackUsed: false
  }
};

const events = [
  { id: "evt_1", jobId: "job_1", seq: 1, eventType: "plan.generated", status: "success", message: "Generated plan.", payload: {}, createdAt: "2026-07-04T00:00:00Z" },
  { id: "evt_2", jobId: "job_1", seq: 2, eventType: "plan.persisted", status: "success", message: "Persisted plan.", payload: { planId: "plan_1", planHash: "hash_1" }, createdAt: "2026-07-04T00:00:01Z" },
  { id: "evt_3", jobId: "job_1", seq: 3, eventType: "job.queued", status: "success", message: "Job queued.", payload: {}, createdAt: "2026-07-04T00:00:01Z" },
  { id: "evt_4", jobId: "job_1", seq: 4, eventType: "plan.loaded", status: "success", message: "Loaded persisted AnalysisPlan.", payload: { planId: "plan_1", planHash: "hash_1" }, createdAt: "2026-07-04T00:00:02Z" },
  { id: "evt_5", jobId: "job_1", seq: 5, eventType: "data.loaded", status: "success", message: "Loaded dataset objects.", payload: {}, createdAt: "2026-07-04T00:00:02Z" },
  { id: "evt_6", jobId: "job_1", seq: 6, eventType: "tool.started", status: "running", message: "Tool started.", payload: {}, createdAt: "2026-07-04T00:00:02Z" },
  { id: "evt_7", jobId: "job_1", seq: 7, eventType: "tool.completed", status: "success", message: "Tool completed.", payload: {}, createdAt: "2026-07-04T00:00:03Z" },
  { id: "evt_8", jobId: "job_1", seq: 8, eventType: "job.completed", status: "success", message: "Job completed.", payload: {}, createdAt: "2026-07-04T00:00:04Z" }
];

const toolCalls = [
  {
    id: "call_1",
    jobId: "job_1",
    stepId: "llm_step_1",
    toolId: "ml.basic_metrics",
    status: "completed",
    planId: "plan_1",
    planHash: "hash_1",
    inputSummary: "Params: predictionColumn, targetColumn",
    outputSummary: "1 artifact(s)"
  }
];

const viewerSceneContent = {
  schema_version: "phase10d1.viewer_scene.v1",
  tool_id: "structure.viewer_scene_metadata",
  scene_type: "structure_viewer_scene",
  structure: {
    formula: "Si",
    site_count: 2,
    species: ["Si"],
    lattice: {
      a: 4,
      b: 4,
      c: 4,
      alpha: 90,
      beta: 90,
      gamma: 90,
      volume: 64,
      units: "angstrom",
      matrix: [
        [4, 0, 0],
        [0, 4, 0],
        [0, 0, 4]
      ]
    },
    atoms: [
      { index: 0, element: "Si", frac_coords: [0, 0, 0], cart_coords: [0, 0, 0] },
      { index: 1, element: "Si", frac_coords: [0.25, 0.25, 0.25], cart_coords: [1, 1, 1] }
    ],
    bonds: [{ from: 0, to: 1, distance: 1.732, policy: "covalent_radius_sum_with_tolerance" }],
    limits: { max_sites: 500, max_bonds: 2000, truncated: false },
    warnings: []
  },
  display: { representation: "ball_and_stick", show_unit_cell: true },
  camera: { projection: "perspective", zoom: 1 },
  limits: { max_sites: 500, max_bonds: 2000, truncated: false },
  security: { contains_javascript: false, external_urls_allowed: false, artifact_supplied_js_allowed: false },
  warnings: []
};

const viewerManifestContent = {
  schema_version: "phase10d1.viewer_assets_manifest.v1",
  package_type: "structure_viewer_static_export",
  tool_id: "structure.viewer_export_package",
  entry_artifact: "viewer_scene.json",
  artifacts: [
    { path: "viewer_scene.json", kind: "scene", media_type: "application/json", required: true },
    { path: "summary.md", kind: "summary", media_type: "text/markdown", required: true },
    { path: "recipe.json", kind: "recipe", media_type: "application/json", required: true }
  ],
  renderer: { included: false, renderer_type: "none", future_renderer_contract: "viewer_scene.json" },
  security: { contains_javascript: false, external_urls_allowed: false, artifact_supplied_js_allowed: false },
  limits: { max_sites: 500, max_bonds: 2000, truncated: false },
  warnings: ["VIEWER_RENDERER_NOT_INCLUDED"]
};

const viewerSceneV1MinimalContent = {
  kind: "viewer_scene",
  version: "viewer_scene.v1",
  schema_version: "phase10f8.viewer_scene.v1",
  source: { fixture_source: "valid_minimal_crystal.viewer_scene.v1.json" },
  metadata: { title: "Minimal Si viewer scene fixture", formula: "Si", site_count: 1, species: ["Si"] },
  scene: {
    coordinate_basis: "cartesian_angstrom",
    sites: [{ index: 0, element: "Si", label: "Si1", xyz: [0, 0, 0], frac: [0, 0, 0], occupancy: 1, style: { radius: 1.1, color: "#808080" } }],
    lattice: {
      pbc: [true, true, true],
      vectors: [
        [5.43, 0, 0],
        [0, 5.43, 0],
        [0, 0, 5.43]
      ],
      parameters: { a: 5.43, b: 5.43, c: 5.43, alpha: 90, beta: 90, gamma: 90 }
    },
    bonds: [],
    cell_expansion: [1, 1, 1],
    style: { representation: "ball_and_stick", background: "transparent" }
  },
  validation: { status: "passed", finite_numbers: true, caps_enforced: true, external_resources_detected: false, scriptable_fields_detected: false, truncated: false },
  caps: { max_sites: 256, max_bonds: 2048, max_species: 32, max_cell_expansion: [1, 1, 1], max_scene_json_bytes: 1000000 },
  warnings: [],
  provenance: { phase: "10F-9", fixture: true, provenance_label: "internal_regression", official_pass_claim: false },
  security: { contains_javascript: false, external_urls: [], external_urls_allowed: false, artifact_supplied_js_allowed: false, renderer_required: false, remote_assets_allowed: false, html_allowed: false }
};

const viewerSceneV1MultiSpeciesContent = {
  ...viewerSceneV1MinimalContent,
  source: { fixture_source: "valid_multi_species_crystal.viewer_scene.v1.json" },
  metadata: { title: "NaCl viewer scene fixture", formula: "NaCl", site_count: 2, species: ["Cl", "Na"] },
  scene: {
    ...viewerSceneV1MinimalContent.scene,
    sites: [
      { index: 0, element: "Na", label: "Na1", xyz: [0, 0, 0], frac: [0, 0, 0], occupancy: 1, style: { radius: 1.02, color: "#ab5cf2" } },
      { index: 1, element: "Cl", label: "Cl1", xyz: [2.82, 2.82, 2.82], frac: [0.5, 0.5, 0.5], occupancy: 1, style: { radius: 1.81, color: "#1ff01f" } }
    ]
  }
};

const viewerSceneV1OptionalBondsContent = {
  ...viewerSceneV1MultiSpeciesContent,
  source: { fixture_source: "valid_optional_bonds.viewer_scene.v1.json" },
  scene: {
    ...viewerSceneV1MultiSpeciesContent.scene,
    bonds: [{ from: 0, to: 1, distance_angstrom: 2.82, policy: "fixture_declared_optional_bond" }]
  }
};

const viewerSceneV1WarningCapsContent = {
  ...viewerSceneV1OptionalBondsContent,
  source: { fixture_source: "valid_warning_caps.viewer_scene.v1.json" },
  validation: { status: "passed_with_warnings", finite_numbers: true, caps_enforced: true, external_resources_detected: false, scriptable_fields_detected: false, truncated: false },
  caps: { max_sites: 2, max_bonds: 1, max_species: 2, max_cell_expansion: [1, 1, 1], max_scene_json_bytes: 1000000 },
  warnings: [{ code: "VIEWER_SCENE_CAP_NEAR_LIMIT", message: "Fixture intentionally reaches declared caps without exceeding them." }]
};

const viewerSceneV1InvalidNanContent = {
  ...viewerSceneV1MinimalContent,
  source: { fixture_source: "invalid_nan_coordinate.viewer_scene.v1.json" },
  validation: { status: "expected_failure", errors: ["VIEWER_SCENE_NON_FINITE_COORDINATE"], finite_numbers: false, caps_enforced: true, external_resources_detected: false, scriptable_fields_detected: false, truncated: false },
  scene: { ...viewerSceneV1MinimalContent.scene, sites: [{ index: 0, element: "Si", label: "Si1", xyz: ["NaN", 0, 0], frac: [0, 0, 0] }] }
};

const viewerSceneV1InvalidExternalContent = {
  ...viewerSceneV1MinimalContent,
  source: { fixture_source: "invalid_external_resource_reference.viewer_scene.v1.json" },
  validation: { status: "expected_failure", errors: ["VIEWER_SCENE_EXTERNAL_RESOURCE_REFERENCE"], finite_numbers: true, caps_enforced: true, external_resources_detected: true, scriptable_fields_detected: false, truncated: false },
  invalid_external_resource_reference: "EXTERNAL_RESOURCE_PLACEHOLDER_REJECTED_BY_CONTRACT"
};

const viewerSceneV1InvalidExecutableContent = {
  ...viewerSceneV1MinimalContent,
  source: { fixture_source: "invalid_executable_field.viewer_scene.v1.json" },
  validation: { status: "expected_failure", errors: ["VIEWER_SCENE_EXECUTABLE_FIELD"], finite_numbers: true, caps_enforced: true, external_resources_detected: false, scriptable_fields_detected: true, truncated: false },
  invalid_executable_field: "EXECUTABLE_FIELD_PLACEHOLDER_REJECTED_BY_CONTRACT"
};

const viewerSceneV1InvalidSchemaContent = {
  ...viewerSceneV1MinimalContent,
  source: { fixture_source: "invalid_schema_version.viewer_scene.v1.json" },
  schema_version: "unsupported.viewer_scene.v9",
  validation: { status: "expected_failure", errors: ["VIEWER_SCENE_UNSUPPORTED_SCHEMA_VERSION"], finite_numbers: true, caps_enforced: true, external_resources_detected: false, scriptable_fields_detected: false, truncated: false }
};

function viewerSceneV1Manifest(fixtureSource: string, validationState: string, expectedErrors: string[] = [], expectedWarnings: string[] = []) {
  return {
    schema_version: "phase10f9.viewer_scene_manifest.v1",
    artifact_id: fixtureSource.replace(".viewer_scene.v1.json", ""),
    artifact_kind: "viewer_scene",
    artifact_version: "viewer_scene.v1",
    fixture_source: fixtureSource,
    expected_validation_state: validationState,
    expected_errors: expectedErrors,
    expected_warnings: expectedWarnings,
    expected_caps: { max_sites: 256, max_bonds: 2048, max_species: 32, max_cell_expansion: [1, 1, 1], max_scene_json_bytes: 1000000 },
    preview_mode: "json_only",
    renderer_required: false,
    executable_assets: "none",
    external_resources: "none"
  };
}

const artifacts = [
  {
    artifactId: "artifact_metrics",
    id: "artifact_metrics",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "metrics_json",
    name: "metrics.json",
    storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/metrics.json",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1"
  },
  {
    artifactId: "artifact_recipe",
    id: "artifact_recipe",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "recipe_json",
    name: "recipe.json",
    storageKey: "projects/project_local/jobs/job_1/recipe.json",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1",
    content: {
      schema_version: "phase10d1.recipe.v1",
      tool_id: "structure.viewer_scene_metadata",
      deterministic: true,
      steps: ["parse_structure", "write_viewer_scene_json"]
    }
  },
  {
    artifactId: "artifact_report",
    id: "artifact_report",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "report_md",
    name: "report.md",
    storageKey: "projects/project_local/jobs/job_1/report.md",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1"
  },
  {
    artifactId: "artifact_scatter_json",
    id: "artifact_scatter_json",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "plotly_json",
    name: "scatter.json",
    storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/scatter.json",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1"
  },
  {
    artifactId: "artifact_scatter_html",
    id: "artifact_scatter_html",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "plotly_html",
    name: "scatter.html",
    storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/scatter.html",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1"
  },
  {
    artifactId: "artifact_histogram_json",
    id: "artifact_histogram_json",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "plotly_json",
    name: "histogram.json",
    storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/histogram.json",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1"
  },
  {
    artifactId: "artifact_correlation_matrix",
    id: "artifact_correlation_matrix",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "table_json",
    name: "correlation_matrix.json",
    storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/correlation_matrix.json",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1"
  },
  {
    artifactId: "artifact_distribution_summary",
    id: "artifact_distribution_summary",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "table_json",
    name: "distribution_summary.json",
    storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/distribution_summary.json",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1"
  },
  {
    artifactId: "artifact_summary",
    id: "artifact_summary",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "summary_md",
    name: "summary.md",
    storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/summary.md",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1",
    content: "Structure Viewer Scene Metadata\n\nNo WebGL renderer included.\nNo artifact JavaScript.\nNo external URLs."
  },
  {
    artifactId: "artifact_viewer_scene",
    id: "artifact_viewer_scene",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "structure_json",
    name: "viewer_scene.json",
    storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/viewer_scene.json",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1",
    content: viewerSceneContent
  },
  {
    artifactId: "artifact_viewer_manifest",
    id: "artifact_viewer_manifest",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "table_json",
    name: "viewer_assets_manifest.json",
    storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/viewer_assets_manifest.json",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1",
    content: viewerManifestContent
  }
];

const result = {
  jobId: "job_1",
  status: "completed",
  planId: "plan_1",
  planHash: "hash_1",
  summary: "Job completed with 1 ToolCall(s) and 11 Artifact(s).",
  toolCallCount: 1,
  artifactCount: 11,
  artifacts
};

let fetchMock: ReturnType<typeof vi.fn>;
let eventSources: MockEventSource[];
let savedSecrets: Array<Record<string, unknown>>;
let activeArtifacts: unknown[];
let activeResult: Record<string, unknown>;
let interpretationCreated: boolean;
let activeInterpretation: Record<string, unknown> | null;
let activeInterpretationRuns: Array<Record<string, unknown>>;
let lastInterpretationRequest: Record<string, unknown> | null;

const interpretationEvidenceId = "evidence_" + "e".repeat(64);
const interpretationFixture = {
  schemaVersion: "1.0",
  interpretationId: "interpretation_" + "i".repeat(64),
  interpretationHash: "a".repeat(64),
  sourceBundleId: "evidence_bundle_" + "b".repeat(64),
  sourceBundleHash: "b".repeat(64),
  sourceJobId: "job_1",
  sourcePlanId: "plan_1",
  sourcePlanHash: "hash_1",
  sourceGraphHash: null,
  mode: "DETERMINISTIC",
  provider: "deterministic",
  providerVersion: "1.0",
  claims: [{
    schemaVersion: "1.0",
    claimId: "claim_" + "c".repeat(64),
    claimType: "OBSERVATION",
    subjectEvidenceIds: [interpretationEvidenceId],
    supportingEvidenceIds: [interpretationEvidenceId],
    limitingEvidenceIds: [],
    contradictingEvidenceIds: [],
    semanticPredicate: "HAS_VALUE",
    qualifiers: [],
    renderedText: "formation_energy reported value: 0.12.",
    scope: "formation_energy",
    confidenceClass: "DIRECT",
    groundingStatus: "GROUNDED",
    displayOrder: 0,
  }],
  globalWarnings: ["Source warning retained."],
  globalLimitations: ["Interpretation is limited to computed metrics."],
  recommendations: [{
    recommendationId: "recommendation_1",
    reasonEvidenceIds: [interpretationEvidenceId],
    suggestedGoalCategory: "sample_inspection",
    expectedMissingEvidence: ["sample-level errors"],
    limitation: "Requires a separate reviewed analysis request.",
    executionAuthorized: false,
    planCreated: false,
    jobCreated: false,
  }],
  completeness: "COMPLETE",
  partialResultState: false,
  repairCount: 0,
  validationOutcome: "VALID",
  executionRecordId: "interpretation_execution_" + "x".repeat(64),
};

const interpretationExecutionFixture = {
  schemaVersion: "1.0",
  executionRecordId: interpretationFixture.executionRecordId,
  executionRecordHash: "f".repeat(64),
  sourceJobId: "job_1",
  sourcePlanId: "plan_1",
  sourcePlanHash: "hash_1",
  sourceGraphHash: null,
  sourceBundleId: interpretationFixture.sourceBundleId,
  sourceBundleHash: interpretationFixture.sourceBundleHash,
  mode: "DETERMINISTIC",
  provider: "deterministic",
  providerVersion: "phase10l4.deterministic.v1",
  providerModel: null,
  repairCount: 0,
  outcome: "INTERPRETATION_READY",
  diagnostics: [],
  evidenceItemCount: 1,
  claimCount: 1,
};

const interpretationEvidenceFixture = {
  interpretationId: interpretationFixture.interpretationId,
  bundleId: interpretationFixture.sourceBundleId,
  bundleHash: interpretationFixture.sourceBundleHash,
  evidenceItems: [{
    schemaVersion: "1.0",
    evidenceItemId: interpretationEvidenceId,
    semanticRole: "ml.rmse",
    evidenceKind: "SCALAR",
    subjectId: "formation_energy",
    displayValue: "0.12",
    unit: null,
    sourceArtifactId: "artifact_metrics",
    sourceArtifactChecksum: "d".repeat(64),
    artifactContract: "platform.ml.basic_metrics",
    artifactContractVersion: "1.0",
    sourceToolId: "ml.basic_metrics",
    sourceToolVersion: "0.1.0",
    fieldLocator: { fieldId: "metrics.rmse", semanticKey: "ml.rmse", entityId: "formation_energy" },
    warnings: [],
    limitations: [],
  }],
  sourceArtifactIds: ["artifact_metrics"],
  bundleWarnings: ["Source warning retained."],
  bundleLimitations: ["Interpretation is limited to computed metrics."],
};

beforeEach(() => {
  eventSources = [];
  savedSecrets = [];
  activeArtifacts = artifacts;
  activeResult = result;
  interpretationCreated = false;
  activeInterpretation = null;
  activeInterpretationRuns = [];
  lastInterpretationRequest = null;
  window.localStorage.clear();
  window.sessionStorage.clear();
  fetchMock = vi.fn(mockPlannerFetch);
  vi.stubGlobal("fetch", fetchMock);
  vi.stubGlobal("EventSource", MockEventSource);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("Phase 9C PlannerWorkbench", () => {
  it("treats Phase 10L-3 partial execution as terminal for interpretation", () => {
    expect(isTerminalPlannerJobStatus("partial_success")).toBe(true);
    expect(isTerminalPlannerJobStatus("running")).toBe(false);
    expect(isTerminalPlannerJobStatus("cancelled")).toBe(false);
  });

  it("renders bounded volumetric metadata without binary values or executable content", () => {
    const dataset = {
      schema_version: "phase10j.volumetric_dataset.v1",
      grid: { shape: [2, 3, 4], sample_location: "node", endpoint_policy: "excluded", boundary_conditions: ["periodic", "periodic", "periodic"] },
      fields: [{ field_name: "total", quantity: "electron_density", stored_component_count: 1, unit: { canonical_unit: "electron/angstrom^3" } }],
      security: { renderer_included: false, external_urls_allowed: false, contains_executable: false }
    };
    const manifest = { capabilities: { metadata_preview: true, renderer_included: false }, security: dataset.security };
    const artifacts = [
      { id: "dataset", artifactId: "dataset", type: "volumetric_dataset_json", name: "volumetric_dataset.json", content: dataset },
      { id: "manifest", artifactId: "manifest", type: "volumetric_manifest_json", name: "volumetric_manifest.json", content: manifest }
    ];
    const { container } = render(<VolumetricMetadataPreviewPanel artifacts={artifacts as never} />);
    expect(screen.getByTestId("volumetric-grid-shape").textContent).toContain("2 x 3 x 4");
    expect(screen.getByText("electron_density")).not.toBeNull();
    expect(screen.getByTestId("volumetric-renderer-included").textContent).toContain("false");
    expect(container.querySelector("canvas")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
  });
  it("renders the strict top/left/main-tab layout in Chinese by default", async () => {
    render(<PlannerWorkbench />);

    expect(await screen.findByTestId("global-context-bar")).not.toBeNull();
    expect(screen.getByTestId("data-context-viewer")).not.toBeNull();
    expect(screen.getByTestId("main-workspace")).not.toBeNull();
    expect(contextButton(0)).not.toBeNull();
    expect(contextButton(1)).not.toBeNull();
    expect(document.querySelectorAll(".main-tab-list button").length).toBe(3);
    expect(screen.queryByText("Not available yet")).toBeNull();
    expect(screen.queryByTestId("agent-process-tab")).toBeNull();
    expect(screen.queryByTestId("results-export-tab")).toBeNull();
    expect(screen.getByTestId("conversation-plan-tab")).not.toBeNull();
  });

  it("opens dataset dialog from the top bar, loads demo data, and updates the left data viewer", async () => {
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await user.click(contextButton(0));
    const datasetDialog = screen.getByRole("dialog");
    expect(datasetDialog).not.toBeNull();
    await user.click(within(datasetDialog).getAllByRole("button")[1]);

    await waitFor(() => {
      expect(screen.queryByRole("dialog")).toBeNull();
      expect(within(screen.getByTestId("data-context-viewer")).getByText("dataset_demo")).not.toBeNull();
      expect(within(screen.getByTestId("data-context-viewer")).getByText("profile_demo")).not.toBeNull();
    });
    expect(within(screen.getByTestId("data-context-viewer")).getByText("y_true")).not.toBeNull();
    const profileIntelligence = within(screen.getByTestId("data-context-viewer")).getByTestId("material-profile-intelligence");
    expect(profileIntelligence.textContent).toContain("regression_target");
    expect(profileIntelligence.textContent).toContain("regression_evaluation");
    expect(profileIntelligence.textContent).toContain("uncertainty_evaluation");
    expect(profileIntelligence.textContent).toContain("MISSING_REQUIRED_DATA");
    expect(profileIntelligence.textContent).toContain("MISSING:classification_target");
    expect(profileIntelligence.textContent).toContain("FORMULA_VALUES_PARTIALLY_INVALID");
  });

  it("shows only server-owned DeepSeek configuration with no browser key or custom endpoint input", async () => {
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await user.click(contextButton(1));
    const modelDialog = screen.getByRole("dialog");
    expect(modelDialog).not.toBeNull();
    expect(within(modelDialog).getByText("https://api.deepseek.com")).not.toBeNull();
    expect(within(modelDialog).getByText("Configuration source: server environment")).not.toBeNull();
    expect(within(modelDialog).queryByLabelText("API Key")).toBeNull();
    expect(within(modelDialog).queryByDisplayValue("https://api.deepseek.com")).toBeNull();
    expect(within(modelDialog).queryByText("OpenAI")).toBeNull();
    expect(within(modelDialog).queryByText("Custom OpenAI-compatible")).toBeNull();
    await user.click(within(modelDialog).getAllByRole("button")[1]);

    expect(await screen.findByText("DeepSeek connection succeeded with a strict JSON response.")).not.toBeNull();
    expect(JSON.stringify(window.localStorage)).not.toContain("DEEPSEEK_KEY");
    expect(JSON.stringify(window.sessionStorage)).not.toContain("DEEPSEEK_KEY");
  });

  it("keeps main tabs mutually exclusive and routes job evidence into Agent process and Results/export", async () => {
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());

    await waitForViewerArtifacts();
    expect(screen.getByText("plan_1")).not.toBeNull();
    expect(screen.getByText("hash_1")).not.toBeNull();
    await waitFor(() => expect(eventSources[0]?.url).toBe("http://localhost:8000/planner/jobs/job_1/events/stream?after_seq=8"));

    await openAgentTab(user);
    expect(screen.getByTestId("agent-process-tab")).not.toBeNull();
    expect(screen.queryByTestId("conversation-plan-tab")).toBeNull();
    expect(screen.queryByTestId("results-export-tab")).toBeNull();
    expect(screen.getByText("Loaded from persisted AnalysisPlan")).not.toBeNull();
    expect(screen.getByText("Executed through Tool Registry + Adapter")).not.toBeNull();
    expect(screen.getByText("No deterministic fallback used")).not.toBeNull();

    await openResultsTab(user);
    expect(screen.getByTestId("results-export-tab")).not.toBeNull();
    expect(screen.queryByTestId("agent-process-tab")).toBeNull();
    expect(screen.queryByTestId("conversation-plan-tab")).toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).getByText("Report / Recipe Summary")).not.toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).getByText("Structure artifact preview")).not.toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).getByText("Metrics")).not.toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).getByText("Table / Numeric Summary")).not.toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).getByText("Artifact Gallery")).not.toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).getAllByText("metrics.json").length).toBeGreaterThan(0);
    expect(within(screen.getByTestId("results-export-tab")).getAllByText("recipe.json").length).toBeGreaterThan(0);
    expect(within(screen.getByTestId("results-export-tab")).getAllByText("scatter.json").length).toBeGreaterThan(0);
    expect(within(screen.getByTestId("results-export-tab")).getAllByText("histogram.json").length).toBeGreaterThan(0);
    expect(within(screen.getByTestId("results-export-tab")).getAllByText("correlation_matrix.json").length).toBeGreaterThan(0);
    expect(within(screen.getByTestId("results-export-tab")).getAllByText("distribution_summary.json").length).toBeGreaterThan(0);
    expect(within(screen.getByTestId("results-export-tab")).getAllByText("viewer_scene.json").length).toBeGreaterThan(0);
    expect(within(screen.getByTestId("results-export-tab")).getAllByText("viewer_assets_manifest.json").length).toBeGreaterThan(0);
    expect(within(screen.getByTestId("results-export-tab")).getAllByText("summary.md").length).toBeGreaterThan(0);
    expect(within(screen.getByTestId("results-export-tab")).getByText("ml.basic_metrics")).not.toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).queryByText("storage URI")).toBeNull();
  });

  it("renders Phase 10D-3 viewer scene and manifest static previews without a 3D renderer", async () => {
    const user = userEvent.setup();
    const { container } = render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const results = screen.getByTestId("results-export-tab");
    expect(within(results).getByTestId("viewer-static-preview-panel")).not.toBeNull();
    expect(within(results).getByTestId("viewer-scene-preview")).not.toBeNull();
    expect(within(results).getByText("Scene overview")).not.toBeNull();
    expect(within(results).getByText("Lattice")).not.toBeNull();
    expect(within(results).getByText("Atoms preview (2)")).not.toBeNull();
    expect(within(results).getByText("Bonds preview (1)")).not.toBeNull();
    expect(within(results).getByText("Display / camera")).not.toBeNull();
    expect(within(results).getAllByText("Si").length).toBeGreaterThan(0);
    expect(within(results).getByText("ball_and_stick")).not.toBeNull();
    expect(within(results).getAllByText("phase10d1.viewer_scene.v1").length).toBeGreaterThan(0);
    expect(within(results).getByTestId("viewer-scene-legacy-notice").textContent).toContain("deprecated");
    expect(within(results).getByTestId("viewer-scene-legacy-notice").textContent).toContain("structure.viewer_3d");
    expect(within(results).getByTestId("viewer-scene-compatibility-status").textContent).toContain("deprecated_read_only");
    expect(within(results).getByTestId("viewer-scene-compatibility-renderer").textContent).toContain("false");
    expect(within(results).getByTestId("viewer-scene-compatibility-periodic").textContent).toContain("false");

    expect(within(results).getByTestId("viewer-manifest-preview")).not.toBeNull();
    expect(within(results).getByText("Export package manifest")).not.toBeNull();
    expect(within(results).getByText("Renderer status")).not.toBeNull();
    expect(within(results).getByTestId("viewer-manifest-compatibility-status").textContent).toContain("deprecated_read_only");
    expect(within(results).getAllByText("none").length).toBeGreaterThan(0);
    expect(within(results).getAllByText(/Renderer included: false/).length).toBeGreaterThan(0);
    expect(within(results).getAllByText(/Artifact JS: false/).length).toBeGreaterThan(0);
    expect(within(results).getAllByText(/External URLs: false/).length).toBeGreaterThan(0);
    expect(within(results).getAllByText("Raw JSON fallback").length).toBeGreaterThan(0);

    expect(within(results).getByTestId("summary-static-preview")).not.toBeNull();
    expect(within(results).getByText(/No WebGL renderer included/)).not.toBeNull();
    expect(within(results).getByTestId("recipe-static-preview")).not.toBeNull();
    expect(within(results).getAllByText("true").length).toBeGreaterThan(0);

    expect(container.querySelector("canvas")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(screen.queryByText(/Three\.js/i)).toBeNull();
    expect(screen.queryByText("structure.viewer_3d")).not.toBeNull();
  });

  it("renders Phase 10F-10 viewer_scene.v1 JSON-only preview and manifest metadata without a renderer", async () => {
    useViewerSceneV1Artifacts(
      viewerSceneV1MinimalContent,
      viewerSceneV1Manifest("valid_minimal_crystal.viewer_scene.v1.json", "valid")
    );
    const user = userEvent.setup();
    const { container } = render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const results = screen.getByTestId("results-export-tab");
    expect(within(results).getByTestId("viewer-scene-v1-preview")).not.toBeNull();
    expect(within(results).getByTestId("viewer-scene-kind").textContent).toContain("viewer_scene");
    expect(within(results).getByTestId("viewer-scene-version").textContent).toContain("viewer_scene.v1");
    expect(within(results).getByTestId("viewer-scene-schema-version").textContent).toContain("phase10f8.viewer_scene.v1");
    expect(within(results).getByTestId("viewer-scene-validation-state").textContent).toContain("passed");
    expect(within(results).getByTestId("viewer-scene-summary").textContent).toContain("cartesian_angstrom");
    expect(within(results).getByTestId("viewer-scene-summary").textContent).toContain("lattice present");
    expect(within(results).getByTestId("viewer-manifest-json-only-preview")).not.toBeNull();
    expect(within(results).getByTestId("viewer-manifest-preview-mode").textContent).toContain("json_only");
    expect(within(results).getByTestId("viewer-manifest-renderer-required").textContent).toContain("false");
    expect(within(results).getByTestId("viewer-manifest-executable-assets").textContent).toContain("none");
    expect(within(results).getByTestId("viewer-manifest-external-resources").textContent).toContain("none");
    expect(within(results).getAllByText(/Renderer included: false/).length).toBeGreaterThan(0);
    expect(within(results).getAllByText(/Artifact JS: false/).length).toBeGreaterThan(0);
    expect(within(results).getAllByText(/External URLs: false/).length).toBeGreaterThan(0);
    expect(container.querySelector("canvas")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
    expect(screen.queryByText(/Three\.js/i)).toBeNull();
    expect(screen.queryByText("structure.viewer_3d")).toBeNull();
  });

  it("renders grounded findings with evidence and keeps recommendations non-executable", async () => {
    const user = userEvent.setup();
    const { container } = render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const panel = screen.getByTestId("grounded-interpretation-panel");
    const createButton = within(panel).getByRole("button", { name: "Generate grounded interpretation" });
    expect(createButton).not.toBeDisabled();
    await user.click(createButton);

    expect(await within(panel).findByText("INTERPRETATION_READY")).not.toBeNull();
    expect(within(panel).getByTestId("interpretation-limitations").textContent).toContain("computed metrics");
    expect(within(panel).getByText("formation_energy reported value: 0.12.")).not.toBeNull();
    await user.click(within(panel).getByText("Show evidence (1)"));
    expect(within(panel).getByText("platform.ml.basic_metrics @ 1.0")).not.toBeNull();
    expect(within(panel).getByText("ml.basic_metrics @ 0.1.0")).not.toBeNull();
    expect(within(panel).getByTestId("interpretation-recommendations").textContent).toContain("execution authorized: no");
    expect(within(panel).queryByRole("button", { name: /sample_inspection/i })).toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
    expect(container.innerHTML).not.toContain("dangerouslySetInnerHTML");
  });

  it("submits strict-provider interpretation mode through the bounded existing transport", async () => {
    const user = userEvent.setup();
    render(<PlannerWorkbench />);
    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const panel = screen.getByTestId("grounded-interpretation-panel");
    await user.click(within(panel).getByRole("button", { name: "Strict provider" }));
    await user.click(within(panel).getByRole("button", { name: "Generate grounded interpretation" }));

    expect(await within(panel).findByText("INTERPRETATION_READY")).not.toBeNull();
    expect(lastInterpretationRequest?.mode).toBe("STRICT_PROVIDER");
    expect(lastInterpretationRequest?.provider).toBe("deepseek");
    expect(within(panel).getByTestId("interpretation-provenance").textContent).toContain("STRICT_PROVIDER");
    expect(within(panel).getByTestId("interpretation-provenance").textContent).toContain("deepseek");
  });

  it("restores a persisted non-ready interpretation run for audit", async () => {
    activeInterpretationRuns = [{
      ...interpretationExecutionFixture,
      executionRecordId: "interpretation_execution_" + "v".repeat(64),
      executionRecordHash: "9".repeat(64),
      mode: "STRICT_PROVIDER",
      provider: "openai_compatible",
      repairCount: 1,
      outcome: "VALIDATION_FAILED",
      diagnostics: ["UNGROUNDED_NUMERIC_CLAIM"],
      claimCount: 0,
    }];
    const user = userEvent.setup();
    render(<PlannerWorkbench />);
    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const panel = screen.getByTestId("grounded-interpretation-panel");
    expect(await within(panel).findByText("VALIDATION_FAILED")).not.toBeNull();
    expect(within(panel).getByTestId("interpretation-provenance").textContent).toContain("openai_compatible");
    expect(within(panel).getByText("UNGROUNDED_NUMERIC_CLAIM")).not.toBeNull();
    await user.click(screen.getByRole("checkbox", { name: "用户模式" }));
    expect(within(panel).getByTestId("interpretation-audit-json")).not.toBeNull();
  });

  it("does not pair an older ready interpretation with a newer failed run", async () => {
    interpretationCreated = true;
    activeInterpretation = interpretationFixture;
    activeInterpretationRuns = [{
      ...interpretationExecutionFixture,
      executionRecordId: "interpretation_execution_" + "w".repeat(64),
      executionRecordHash: "8".repeat(64),
      mode: "STRICT_PROVIDER",
      provider: "openai_compatible",
      outcome: "VALIDATION_FAILED",
      diagnostics: ["PROVIDER_RESULT_NOT_GROUNDED"],
      claimCount: 0,
    }];
    const user = userEvent.setup();
    render(<PlannerWorkbench />);
    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const panel = screen.getByTestId("grounded-interpretation-panel");
    expect(await within(panel).findByText("VALIDATION_FAILED")).not.toBeNull();
    expect(within(panel).queryByText("formation_energy reported value: 0.12.")).toBeNull();
    expect(within(panel).getByText("PROVIDER_RESULT_NOT_GROUNDED")).not.toBeNull();
  });

  it("offers the validated Brillouin-zone renderer product with JSON and manifest fallbacks", async () => {
    useBrillouinZoneArtifacts();
    const user = userEvent.setup();
    const { container } = render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const panel = screen.getByTestId("brillouin-zone-preview-panel");
    expect(within(panel).getByText("Standalone reciprocal-space product")).not.toBeNull();
    expect(within(panel).getByTestId("brillouin-zone-renderer-state")).toHaveTextContent("unsupported");
    expect(within(panel).getByTestId("brillouin-zone-renderer-fallback")).toHaveTextContent("BZ_RENDERER_UNSUPPORTED");
    expect(within(panel).getByTestId("brillouin-zone-summary").textContent).toContain("8");
    expect(within(panel).getByTestId("brillouin-zone-summary").textContent).toContain("6");
    await user.click(within(panel).getByRole("tab", { name: "Scientific data" }));
    expect(within(panel).getByText("K-path").parentElement?.textContent).toContain("phase10i.kpath.v1");
    await user.click(within(panel).getByRole("tab", { name: "Manifest" }));
    expect(within(panel).getByTestId("brillouin-zone-manifest-json").textContent).toContain("phase10i.brillouin_zone_manifest.v1");
    expect(container.querySelector("canvas")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
  });

  it("renders Phase 10F-12 adapter-generated viewer_scene.v1 artifacts in the JSON-only preview", async () => {
    useViewerSceneV1Artifacts(
      adapterGeneratedViewerScene as Record<string, unknown>,
      adapterGeneratedViewerSceneManifest as Record<string, unknown>
    );
    const user = userEvent.setup();
    const { container } = render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const results = screen.getByTestId("results-export-tab");
    expect(within(results).getByTestId("viewer-scene-v1-preview")).not.toBeNull();
    expect(within(results).getByTestId("viewer-scene-kind").textContent).toContain("viewer_scene");
    expect(within(results).getByTestId("viewer-scene-version").textContent).toContain("viewer_scene.v1");
    expect(within(results).getByTestId("viewer-scene-schema-version").textContent).toContain("phase10f8.viewer_scene.v1");
    expect(within(results).getByTestId("viewer-scene-validation-state").textContent).toContain("passed");
    expect(within(results).getByTestId("viewer-scene-summary").textContent).toContain("cartesian_angstrom");
    expect(within(results).getByTestId("viewer-scene-summary").textContent).toContain("lattice present");
    expect(within(results).getByTestId("viewer-manifest-preview-mode").textContent).toContain("json_only");
    expect(within(results).getByTestId("viewer-manifest-renderer-required").textContent).toContain("false");
    expect(within(results).getByTestId("viewer-manifest-executable-assets").textContent).toContain("none");
    expect(within(results).getByTestId("viewer-manifest-external-resources").textContent).toContain("none");
    expect(container.querySelector("canvas")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
    expect(document.body.innerHTML).not.toMatch(/<canvas|<iframe|dangerouslySetInnerHTML/i);
  });

  it("renders Phase 10F-13 live adapter-generated warning/caps artifacts in the JSON-only preview", async () => {
    useViewerSceneV1Artifacts(
      liveAdapterWarningViewerScene as Record<string, unknown>,
      liveAdapterWarningViewerSceneManifest as Record<string, unknown>
    );
    const user = userEvent.setup();
    const { container } = render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const results = screen.getByTestId("results-export-tab");
    expect(within(results).getByTestId("viewer-scene-v1-preview")).not.toBeNull();
    expect(within(results).getByTestId("viewer-scene-validation-state").textContent).toContain("passed_with_warnings");
    expect(within(results).getByTestId("viewer-scene-warning-codes").textContent).toContain("VIEWER_SCENE_CAP_NEAR_LIMIT");
    expect(within(results).getByTestId("viewer-scene-warning-codes").textContent).toContain("VIEWER_SCENE_BONDS_TRUNCATED");
    expect(within(results).getByTestId("viewer-manifest-preview-mode").textContent).toContain("json_only");
    expect(within(results).getByTestId("viewer-manifest-renderer-required").textContent).toContain("false");
    expect(container.querySelector("canvas")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
  });

  it("renders viewer_scene.v1 warning and cap fixture state in the JSON-only preview", async () => {
    useViewerSceneV1Artifacts(
      viewerSceneV1WarningCapsContent,
      viewerSceneV1Manifest("valid_warning_caps.viewer_scene.v1.json", "valid_with_warnings", [], ["VIEWER_SCENE_CAP_NEAR_LIMIT"])
    );
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const results = screen.getByTestId("results-export-tab");
    expect(within(results).getByTestId("viewer-scene-validation-state").textContent).toContain("passed_with_warnings");
    expect(within(results).getByTestId("viewer-scene-warning-codes").textContent).toContain("VIEWER_SCENE_CAP_NEAR_LIMIT");
    expect(within(results).getAllByText("2").length).toBeGreaterThan(0);
    expect(within(results).getAllByText("1").length).toBeGreaterThan(0);
    expect(within(results).getByTestId("viewer-manifest-preview-mode").textContent).toContain("json_only");
  });

  it("renders viewer_scene.v1 invalid fixture validation errors without executing payload content", async () => {
    useViewerSceneV1Artifacts(
      viewerSceneV1InvalidExternalContent,
      viewerSceneV1Manifest("invalid_external_resource_reference.viewer_scene.v1.json", "invalid", ["VIEWER_SCENE_EXTERNAL_RESOURCE_REFERENCE"])
    );
    const user = userEvent.setup();
    const { container } = render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const results = screen.getByTestId("results-export-tab");
    expect(within(results).getByTestId("viewer-scene-validation-state").textContent).toContain("expected_failure");
    expect(within(results).getByTestId("viewer-scene-error-codes").textContent).toContain("VIEWER_SCENE_EXTERNAL_RESOURCE_REFERENCE");
    expect(within(results).getByTestId("viewer-scene-preview").textContent).toContain("EXTERNAL_RESOURCE_PLACEHOLDER_REJECTED_BY_CONTRACT");
    expect(container.querySelector("canvas")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
    expect(document.body.innerHTML).not.toMatch(/<canvas|<script|<iframe/i);
  });

  it("renders invalid viewer_scene schema as inert JSON-only preview without a renderer", async () => {
    useViewerSceneV1Artifacts(
      viewerSceneV1InvalidSchemaContent,
      viewerSceneV1Manifest("invalid_schema_version.viewer_scene.v1.json", "invalid", ["VIEWER_SCENE_UNSUPPORTED_SCHEMA_VERSION"])
    );
    const user = userEvent.setup();
    const { container } = render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const results = screen.getByTestId("results-export-tab");
    expect(within(results).getByTestId("viewer-scene-json-preview")).not.toBeNull();
    expect(within(results).queryByTestId("viewer-scene-v1-preview")).toBeNull();
    expect(within(results).getByTestId("viewer-scene-kind").textContent).toContain("viewer_scene");
    expect(within(results).getByTestId("viewer-scene-version").textContent).toContain("viewer_scene.v1");
    expect(within(results).getByTestId("viewer-scene-schema-version").textContent).toContain("unsupported.viewer_scene.v9");
    expect(within(results).getByTestId("viewer-scene-validation-state").textContent).toContain("expected_failure");
    expect(within(results).getByTestId("viewer-scene-error-codes").textContent).toContain("VIEWER_SCENE_UNSUPPORTED_SCHEMA_VERSION");
    expect(within(results).getByTestId("viewer-manifest-preview-mode").textContent).toContain("json_only");
    expect(within(results).getByTestId("viewer-manifest-renderer-required").textContent).toContain("false");
    expect(container.querySelector("canvas")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
  });

  it("offers the canonical renderer tab and keeps JSON available when WebGL is unsupported", async () => {
    useViewerSceneV1Artifacts(viewerSceneV1MinimalContent, viewerSceneV1Manifest("valid_minimal_crystal.viewer_scene.v1.json", "valid", [], []));
    const user = userEvent.setup();
    const { container } = render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const results = screen.getByTestId("results-export-tab");
    expect(within(results).getByRole("tab", { name: "Scene JSON" }).getAttribute("aria-selected")).toBe("true");
    await user.click(within(results).getByRole("tab", { name: "3D Renderer" }));
    expect((await within(results).findByTestId("viewer-scene-renderer-unavailable")).textContent).toContain("Scene JSON and Manifest views remain available");
    expect(container.querySelector("canvas")).toBeNull();
    await user.click(within(results).getByRole("tab", { name: "Scene JSON" }));
    expect(within(results).getByTestId("viewer-scene-json-preview")).not.toBeNull();
  });

  it("offers the canonical renderer for viewer_scene.v2 periodic topology artifacts", async () => {
    const manifest: any = viewerSceneV1Manifest("periodic_boundary.viewer_scene.v2.json", "valid_with_warnings", [], ["VIEWER_SCENE_BONDS_NON_AUTHORITATIVE"]);
    manifest.schema_version = "phase10f19.viewer_assets_manifest.v2";
    manifest.artifact_version = "viewer_scene.v2";
    manifest.capabilities = {scene_contract:"phase10f18.viewer_scene.v2",periodic_topology:true,renderer_included:false,webgl_included:false};
    manifest.webgl_included = false;
    useViewerSceneV1Artifacts(periodicBoundaryScene(), manifest);
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);

    const results = screen.getByTestId("results-export-tab");
    expect(within(results).getByTestId("viewer-scene-version").textContent).toContain("viewer_scene.v2");
    expect(within(results).getByTestId("viewer-scene-cross-boundary-bond-count").textContent).toContain("1");
    expect(within(results).getByTestId("viewer-scene-self-periodic-bond-count").textContent).toContain("0");
    expect(within(results).getByTestId("viewer-scene-neighbor-count").textContent).toContain("1");
    expect(within(results).getByTestId("viewer-scene-artifact-renderer-status").textContent).toContain("not included");
    expect(within(results).getByTestId("viewer-scene-future-renderer-contract").textContent).toContain("consumer of viewer_scene.v2");
    expect(within(results).getByTestId("viewer-manifest-scene-contract").textContent).toContain("phase10f18.viewer_scene.v2");
    expect(within(results).getByTestId("viewer-manifest-periodic-topology").textContent).toContain("true");
    await user.click(within(results).getByRole("tab", { name: "3D Renderer" }));
    expect(await within(results).findByTestId("viewer-scene-renderer-unavailable")).not.toBeNull();
  });

  it("blocks canonical invalid payloads before renderer initialization", async () => {
    useViewerSceneV1Artifacts(
      viewerSceneV1InvalidExternalContent,
      viewerSceneV1Manifest("invalid_external_resource_reference.viewer_scene.v1.json", "invalid", ["VIEWER_SCENE_EXTERNAL_RESOURCE_REFERENCE"])
    );
    const user = userEvent.setup();
    const { container } = render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await waitForViewerArtifacts();
    await openResultsTab(user);
    const results = screen.getByTestId("results-export-tab");
    await user.click(within(results).getByRole("tab", { name: "3D Renderer" }));
    expect(within(results).getByTestId("viewer-scene-renderer-invalid").textContent).toContain("VIEWER_SCENE_EXTERNAL_RESOURCE_REFERENCE");
    expect(container.querySelector("canvas")).toBeNull();
  });

  it("keeps Phase 10F-9 viewer_scene.v1 fixture coverage renderer-free in frontend samples", () => {
    const fixtureSamples = [
      viewerSceneV1MinimalContent,
      viewerSceneV1MultiSpeciesContent,
      viewerSceneV1OptionalBondsContent,
      viewerSceneV1WarningCapsContent,
      viewerSceneV1InvalidNanContent,
      viewerSceneV1InvalidExternalContent,
      viewerSceneV1InvalidExecutableContent,
      viewerSceneV1InvalidSchemaContent
    ];
    for (const sample of fixtureSamples) {
      const serialized = JSON.stringify(sample);
      expect(serialized).not.toMatch(/https?:\/\//i);
      expect(serialized).not.toMatch(/<script|<\/script|javascript:|onload=|onerror=|eval\(/i);
      expect(serialized).not.toMatch(/three\.js/i);
      expect(serialized).not.toMatch(/webgl/i);
      expect(sample.security.renderer_required).toBe(false);
      expect(sample.security.external_urls_allowed).toBe(false);
      expect(sample.security.artifact_supplied_js_allowed).toBe(false);
    }
  });

  it("shows the required result empty state when no chunk is selected", async () => {
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await openResultsTab(user);
    expect(screen.getByTestId("results-export-tab")).not.toBeNull();
    expect(screen.getByTestId("results-export-tab").querySelector(".empty-state")).not.toBeNull();
  });

  it("keeps successful job slices visible when artifact refresh fails", async () => {
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      if (String(input).endsWith("/planner/jobs/job_1/artifacts")) {
        return jsonResponse({ detail: "artifact storage temporarily unavailable" }, 503);
      }
      return mockPlannerFetch(input, init);
    });
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());
    await openResultsTab(user);

    expect(await screen.findByTestId("workspace-partial-failure")).not.toBeNull();
    expect(screen.getByText("MATERIAL_INTELLIGENCE_PARTIAL_RESULT_LOAD")).not.toBeNull();
    expect(screen.getByText("artifacts")).not.toBeNull();
    expect(screen.getAllByText("job_1").length).toBeGreaterThan(0);
  });

  it("explains validation failure without creating job, plan, enqueue, polling, or SSE", async () => {
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === "POST" && url.endsWith("/planner/jobs")) {
        return jsonResponse({
          ok: false,
          job_id: null,
          plan_id: null,
          plan_hash: null,
          validation_errors: [{ code: "UNKNOWN_TOOL", message: "Unknown tool", detail: { toolId: "bad.tool" } }],
          enqueued: false,
          executed: false
        });
      }
      return mockPlannerFetch(input, init);
    });
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());

    expect((await screen.findAllByText("Plan validation failed")).length).toBeGreaterThan(0);
    expect(screen.getByText("No AnalysisPlan was saved")).not.toBeNull();
    expect(screen.getByText("No Job was created")).not.toBeNull();
    expect(screen.getByText("Nothing was enqueued")).not.toBeNull();
    expect(screen.getAllByText("UNKNOWN_TOOL").length).toBeGreaterThan(0);
    expect(fetchMock).not.toHaveBeenCalledWith(expect.stringContaining("/planner/jobs/job_1"), expect.anything());
    expect(eventSources).toHaveLength(0);
  });

  it("uses the v1 intent gate and completes one bounded clarification before planning", async () => {
    const jobBodies: Array<Record<string, unknown>> = [];
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === "POST" && url.endsWith("/planner/jobs")) {
        const body = JSON.parse(String(init.body || "{}")) as Record<string, unknown>;
        jobBodies.push(body);
        if (!body.intentId) {
          return jsonResponse({
            ok: false,
            job_id: null,
            plan_id: null,
            plan_hash: null,
            validation_errors: [],
            intent_id: clarificationIntent.intentId,
            intent_outcome: clarificationIntent.outcome,
            intent: clarificationIntent,
            error_code: "INTENT_CLARIFICATION_REQUIRED",
            enqueued: false,
            executed: false
          });
        }
        return jsonResponse({ ...createdJob, intent_id: baseIntent.intentId, intent_outcome: "READY", intent: baseIntent });
      }
      if (init?.method === "POST" && url.endsWith(`/planner/intents/${clarificationIntent.intentId}/clarification`)) {
        const body = JSON.parse(String(init.body || "{}"));
        expect(body.answers).toEqual([{ questionId: "select_model_target", selectedValues: ["target_b"] }]);
        return jsonResponse({ ok: true, intent_id: baseIntent.intentId, outcome: "READY", intent: { ...baseIntent, provenance: { ...baseIntent.provenance, parentIntentId: clarificationIntent.intentId } } });
      }
      return mockPlannerFetch(input, init);
    });
    const user = userEvent.setup();
    render(<PlannerWorkbench />);
    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());

    const panel = await screen.findByTestId("analysis-intent-panel");
    expect(within(panel).getByText("NEEDS_CLARIFICATION")).not.toBeNull();
    expect(jobBodies[0]?.intentSchemaVersion).toBe("1.0");
    const runControlButton = within(screen.getByTestId("run-controls")).getByRole("button");
    expect(runControlButton).toBeDisabled();

    await user.selectOptions(within(panel).getByLabelText("Which model target should be evaluated?"), "target_b");
    await user.click(within(panel).getByRole("button", { name: "Confirm intent" }));
    await waitFor(() => expect(jobBodies).toHaveLength(2));
    expect(jobBodies[1]?.intentId).toBe(baseIntent.intentId);
    expect(await screen.findByTestId("plan-preview-panel")).not.toBeNull();
  });

  it("shows unsupported boundary, disables Run, and renders audit JSON as inert text", async () => {
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === "POST" && url.endsWith("/planner/jobs")) {
        return jsonResponse({
          ok: false,
          job_id: null,
          plan_id: null,
          plan_hash: null,
          validation_errors: [],
          intent_id: unsupportedIntent.intentId,
          intent_outcome: unsupportedIntent.outcome,
          intent: unsupportedIntent,
          error_code: "INTENT_UNSUPPORTED",
          enqueued: false,
          executed: false
        });
      }
      return mockPlannerFetch(input, init);
    });
    const user = userEvent.setup();
    render(<PlannerWorkbench />);
    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());

    const panel = await screen.findByTestId("analysis-intent-panel");
    expect(within(panel).getByTestId("analysis-intent-unsupported").textContent).toContain("FUTURE_SCOPE");
    expect(within(screen.getByTestId("run-controls")).getByRole("button")).toBeDisabled();

    await user.click(screen.getByRole("checkbox"));
    const audit = await screen.findByTestId("analysis-intent-audit-json");
    expect(audit.querySelector("pre")?.textContent).toContain("INTENT_FUTURE_FERMI_SURFACE");
    expect(audit.querySelector("script")).toBeNull();
    expect(document.querySelector("iframe")).toBeNull();
  });

  it("shows the capability-aware selection, exact bindings, and inert audit record", async () => {
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === "POST" && url.endsWith("/planner/jobs")) {
        return jsonResponse({
          ...createdJob,
          plan_source: "capability_planner",
          intent_id: baseIntent.intentId,
          intent_outcome: "READY",
          intent: baseIntent,
          capability_outcome: "PLAN_READY",
          eligibility_resolution: capabilityResolution,
          capability_decision: capabilityDecision,
          provider_visible_tool_ids: capabilityResolution.eligibleToolIds
        });
      }
      return mockPlannerFetch(input, init);
    });
    const user = userEvent.setup();
    render(<PlannerWorkbench />);
    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());

    const panel = await screen.findByTestId("capability-planning-panel");
    expect(within(panel).getByText("PLAN_READY")).not.toBeNull();
    expect(within(panel).getByRole("heading", { name: "Dataset Materials Explorer" })).not.toBeNull();
    expect(within(panel).getByText("dataset.materials_explorer@0.1.0")).not.toBeNull();
    expect(within(panel).getByText("RESOURCE_ID / table_1")).not.toBeNull();
    expect(within(screen.getByTestId("run-controls")).getByRole("button")).toBeEnabled();

    await user.click(screen.getByRole("checkbox"));
    const audit = await screen.findByTestId("capability-planning-audit-json");
    expect(audit.querySelector("pre")?.textContent).toContain("resolution_demo");
    expect(audit.querySelector("script")).toBeNull();
  });

  it("shows typed capability mismatch and keeps Run disabled", async () => {
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === "POST" && url.endsWith("/planner/jobs")) {
        return jsonResponse({
          ok: false,
          job_id: null,
          plan_id: null,
          plan_hash: null,
          plan: null,
          validation_errors: [{ code: "CAPABILITY_COVERAGE_INCOMPLETE", message: "No current capability covers the request." }],
          intent_id: baseIntent.intentId,
          intent_outcome: "READY",
          intent: baseIntent,
          capability_outcome: "CAPABILITY_MISMATCH",
          eligibility_resolution: { ...capabilityResolution, eligibleToolIds: [], rejectedToolIds: ["dataset.materials_explorer", "ml.basic_metrics"], diagnostics: [{ code: "CAPABILITY_COVERAGE_INCOMPLETE", field: "scientificIntents", message: "No current capability covers the request.", repairable: false }] },
          capability_decision: { ...capabilityDecision, outcome: "CAPABILITY_MISMATCH", selections: [], diagnostics: [{ code: "CAPABILITY_COVERAGE_INCOMPLETE", field: "scientificIntents", message: "No current capability covers the request.", repairable: false }] },
          provider_visible_tool_ids: [],
          enqueued: false,
          executed: false
        });
      }
      return mockPlannerFetch(input, init);
    });
    const user = userEvent.setup();
    render(<PlannerWorkbench />);
    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());

    const panel = await screen.findByTestId("capability-planning-panel");
    expect(within(panel).getByText("CAPABILITY_MISMATCH")).not.toBeNull();
    expect(within(panel).getByTestId("capability-planning-diagnostics")).toHaveTextContent("CAPABILITY_COVERAGE_INCOMPLETE");
    expect(within(screen.getByTestId("run-controls")).getByRole("button")).toBeDisabled();
  });

  it("shows the typed dependency graph, partial execution, blocked step, and inert lineage audit", async () => {
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === "POST" && url.endsWith("/planner/jobs")) {
        return jsonResponse({
          ...createdJob,
          plan: dependencyPlan,
          plan_schema_version: "0.2",
          graph_hash: dependencyPlan.graphHash,
          dependency_bindings: dependencyBindings,
          topological_order: dependencyAudit.topologicalOrder
        });
      }
      if (url.endsWith("/planner/jobs/job_1/dependencies")) return jsonResponse(dependencyAudit);
      return mockPlannerFetch(input, init);
    });
    const user = userEvent.setup();
    render(<PlannerWorkbench />);
    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());

    const panel = await screen.findByTestId("dependency-execution-panel");
    expect(within(panel).getByText("PARTIAL_RESULTS")).not.toBeNull();
    expect(within(panel).getByText("step_band:canonical-band -> step_combined:band")).not.toBeNull();
    expect(within(panel).getByText("BLOCKED_DEPENDENCY")).not.toBeNull();
    expect(within(panel).getByText("Blocked by step_band")).not.toBeNull();
    expect(within(panel).getByTestId("artifact-lineage-list")).toHaveTextContent("composition.summary");
    expect(document.body.scrollWidth).toBeLessThanOrEqual(document.documentElement.clientWidth || document.body.scrollWidth);

    await user.click(screen.getByRole("checkbox"));
    const audit = await screen.findByTestId("dependency-audit-json");
    expect(audit.querySelector("pre")?.textContent).toContain("binding_band_combined");
    expect(audit.querySelector("script")).toBeNull();
    expect(document.querySelector("iframe")).toBeNull();
  });
});

async function loadDemoFromTopBar(user: ReturnType<typeof userEvent.setup>) {
  await user.click(contextButton(0));
  const datasetDialog = screen.getByRole("dialog");
  await user.click(within(datasetDialog).getAllByRole("button")[1]);
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
}

function contextButton(index: number) {
  const buttons = document.querySelectorAll<HTMLButtonElement>(".global-context-bar .context-button");
  expect(buttons.length).toBeGreaterThan(index);
  return buttons[index];
}

function primaryRunButton() {
  const buttons = screen.getByTestId("planner-form").querySelectorAll<HTMLButtonElement>("button");
  expect(buttons.length).toBeGreaterThan(0);
  return buttons[buttons.length - 1];
}

async function waitForViewerArtifacts() {
  await waitFor(() => {
    expect(fetchMock.mock.calls.some(([input]) => String(input).endsWith("/planner/jobs/job_1/artifacts"))).toBe(true);
  });
}

async function openResultsTab(user: ReturnType<typeof userEvent.setup>) {
  const tabButtons = document.querySelectorAll<HTMLButtonElement>(".main-tab-list button");
  expect(tabButtons.length).toBeGreaterThanOrEqual(3);
  await user.click(tabButtons[2]);
}

async function openAgentTab(user: ReturnType<typeof userEvent.setup>) {
  const tabButtons = document.querySelectorAll<HTMLButtonElement>(".main-tab-list button");
  expect(tabButtons.length).toBeGreaterThanOrEqual(1);
  await user.click(tabButtons[0]);
}

function useViewerSceneV1Artifacts(sceneContent: Record<string, unknown>, manifestContent: Record<string, unknown>) {
  const viewerArtifacts = [
    {
      artifactId: "artifact_viewer_scene_v1",
      id: "artifact_viewer_scene_v1",
      jobId: "job_1",
      toolCallId: "call_1",
      type: "viewer_scene_json",
      name: String(sceneContent.source && typeof sceneContent.source === "object" && "fixture_source" in sceneContent.source ? (sceneContent.source as { fixture_source?: string }).fixture_source : "viewer_scene.v1.json"),
      storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/viewer_scene.v1.json",
      storageProvider: "local",
      planId: "plan_1",
      planHash: "hash_1",
      content: sceneContent
    },
    {
      artifactId: "artifact_viewer_manifest_v1",
      id: "artifact_viewer_manifest_v1",
      jobId: "job_1",
      toolCallId: "call_1",
      type: "viewer_scene_manifest_json",
      name: String(manifestContent.fixture_source ? `manifest_${manifestContent.fixture_source}` : "manifest_valid_minimal_crystal.viewer_scene.v1.json"),
      storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/viewer_scene_manifest.v1.json",
      storageProvider: "local",
      planId: "plan_1",
      planHash: "hash_1",
      content: manifestContent
    },
    {
      artifactId: "artifact_summary_v1",
      id: "artifact_summary_v1",
      jobId: "job_1",
      toolCallId: "call_1",
      type: "summary_md",
      name: "summary.md",
      storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/summary.md",
      storageProvider: "local",
      planId: "plan_1",
      planHash: "hash_1",
      content: "Viewer Scene JSON-only Preview\n\nNo renderer bundle.\nNo artifact JavaScript.\nNo external resources."
    },
    {
      artifactId: "artifact_recipe_v1",
      id: "artifact_recipe_v1",
      jobId: "job_1",
      toolCallId: "call_1",
      type: "recipe_json",
      name: "recipe.json",
      storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/recipe.json",
      storageProvider: "local",
      planId: "plan_1",
      planHash: "hash_1",
      content: {
        schema_version: "phase10f10.viewer_scene_json_preview.recipe.v1",
        deterministic: true,
        renderer_required: false,
        steps: ["load_fixture", "validate_contract", "render_json_only_preview"]
      }
    }
  ];
  activeArtifacts = viewerArtifacts;
  activeResult = { ...result, artifactCount: viewerArtifacts.length, artifacts: viewerArtifacts };
}

function useBrillouinZoneArtifacts() {
  const definitions = [
    ["reciprocal_lattice_json", "reciprocal_lattice.json", bzReciprocal],
    ["brillouin_zone_json", "brillouin_zone.json", bzZone],
    ["kpath_json", "kpath.json", bzKpath],
    ["brillouin_zone_manifest_json", "brillouin_zone_manifest.json", bzManifest]
  ] as const;
  activeArtifacts = definitions.map(([type, name, content], index) => ({
    artifactId: `artifact_bz_${index}`,
    id: `artifact_bz_${index}`,
    jobId: "job_1",
    toolCallId: "call_bz",
    type,
    name,
    storageKey: `projects/project_local/jobs/job_1/tool_calls/call_bz/${name}`,
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1",
    content
  }));
  activeResult = { ...result, artifactCount: activeArtifacts.length, artifacts: activeArtifacts };
}

function mockPlannerFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const url = String(input);
  const method = init?.method || "GET";
  if (url.endsWith("/health/runtime")) {
    return jsonResponse({
      api: { status: "ok" },
      database: { status: "ok", backend: "sqlite" },
      redis: { status: "unknown", reason: "not configured" },
      artifactStorage: { status: "ok", backend: "local" },
      worker: { status: "ok", backend: "local" },
      llmProvider: { status: "ok", provider: "deepseek", model: "deepseek-v4-flash" }
    });
  }
  if (url.endsWith("/planner/providers")) {
    return jsonResponse({
      providers: [
        { id: "deepseek", label: "DeepSeek", provider: "deepseek", baseUrl: "https://api.deepseek.com", defaultModel: "deepseek-v4-flash", allowedModels: ["deepseek-v4-flash", "deepseek-v4-pro"], requiresSecret: false, configurationSource: "server_environment" },
        { id: "mock", label: "Deterministic test provider", provider: "mock", requiresSecret: false, developerOnly: true }
      ]
    });
  }
  if (url.endsWith("/planner/providers/status")) {
    return jsonResponse({ ok: true, provider: "deepseek", model: "deepseek-v4-flash", status: "ready", configured: true, configurationSource: "server_environment", message: "DeepSeek is configured." });
  }
  if (method === "POST" && url.endsWith("/planner/providers/resolve")) {
    const body = JSON.parse(String(init?.body || "{}"));
    expect(body).not.toHaveProperty("baseUrl");
    expect(body).not.toHaveProperty("secretId");
    if (body.provider === "deepseek") {
      return jsonResponse({
        ok: true,
        provider: "deepseek",
        model: body.model || "deepseek-v4-flash",
        status: "ready",
        willUseLiveProvider: true,
        secretConfigured: false,
        source: "server_environment",
        message: "DeepSeek is configured.",
        redacted: true
      });
    }
    return jsonResponse({
      ok: true,
      provider: "mock",
      model: "mock",
      status: "ready",
      willUseLiveProvider: false,
      secretConfigured: false,
      source: "request",
      message: "Current planner job configuration will use Mock Planner.",
      redacted: true
    });
  }
  if (method === "POST" && url.endsWith("/planner/providers/test")) {
    const body = JSON.parse(String(init?.body || "{}"));
    expect(body).not.toHaveProperty("baseUrl");
    expect(body).not.toHaveProperty("secretId");
    return jsonResponse({ ok: true, provider: body.provider, model: body.model || "mock", latencyMs: 9, validated: true, message: "DeepSeek connection succeeded with a strict JSON response.", redacted: true, realLlmCalls: 0 });
  }
  if (url.endsWith("/me/secrets") && method === "GET") {
    return jsonResponse(savedSecrets);
  }
  if (url.endsWith("/me/secrets") && method === "POST") {
    const body = JSON.parse(String(init?.body || "{}"));
    const secret = {
      id: "secret_1",
      secret_id: "secret_1",
      alias: body.alias,
      provider: body.provider,
      createdAt: "2026-07-04T00:00:00Z",
      status: "active",
      maskedPreview: "********"
    };
    savedSecrets = [secret];
    return jsonResponse(secret);
  }
  if (url.includes("/me/secrets/") && method === "DELETE") {
    savedSecrets = [];
    return jsonResponse(true);
  }
  if (url.endsWith("/datasets")) {
    return jsonResponse([{ id: "dataset_api", datasetId: "dataset_api", projectId: "project_local", name: "Demo metrics dataset", status: "profile_ready", profileId: "profile_api" }]);
  }
  if (method === "POST" && url.endsWith("/datasets/demo")) {
    return jsonResponse({ id: "dataset_demo", datasetId: "dataset_demo", projectId: "project_local", name: "Demo metrics dataset", status: "profile_ready", demo: true, profileId: "profile_demo", profile: demoProfile });
  }
  if (url.endsWith("/datasets/dataset_demo/profile") || url.endsWith("/datasets/dataset_api/profile")) {
    return jsonResponse(url.includes("dataset_api") ? { ...demoProfile, datasetId: "dataset_api", profileId: "profile_api" } : demoProfile);
  }
  if (method === "POST" && url.endsWith("/planner/jobs")) {
    const body = JSON.parse(String(init?.body || "{}"));
    expect(body).not.toHaveProperty("baseUrl");
    expect(body).not.toHaveProperty("secretId");
    expect(body.intentSchemaVersion).toBe("1.0");
    return jsonResponse(createdJob);
  }
  if (url.endsWith("/planner/jobs/job_1/interpretations") && method === "POST") {
    const body = JSON.parse(String(init?.body || "{}"));
    expect(["DETERMINISTIC", "STRICT_PROVIDER"]).toContain(body.mode);
    expect(body.expectedPlanHash).toBe("hash_1");
    expect(JSON.stringify(body)).not.toContain("artifact_metrics");
    lastInterpretationRequest = body;
    interpretationCreated = true;
    activeInterpretation = body.mode === "STRICT_PROVIDER"
      ? { ...interpretationFixture, mode: "STRICT_PROVIDER", provider: "deepseek" }
      : interpretationFixture;
    const execution = body.mode === "STRICT_PROVIDER"
      ? { ...interpretationExecutionFixture, mode: "STRICT_PROVIDER", provider: "deepseek" }
      : interpretationExecutionFixture;
    return jsonResponse({
      outcome: "INTERPRETATION_READY",
      interpretationId: interpretationFixture.interpretationId,
      bundleId: interpretationFixture.sourceBundleId,
      bundleHash: interpretationFixture.sourceBundleHash,
      sourceJobId: "job_1",
      sourcePlanId: "plan_1",
      sourcePlanHash: "hash_1",
      sourceGraphHash: null,
      mode: activeInterpretation.mode,
      claims: interpretationFixture.claims,
      warnings: interpretationFixture.globalWarnings,
      limitations: interpretationFixture.globalLimitations,
      recommendations: interpretationFixture.recommendations,
      partialResultState: false,
      repairCount: 0,
      diagnostics: [],
      evidenceItemCount: 1,
      noExecution: { toolCallCreated: false, planCreated: false, jobCreated: false, enqueued: false, recommendationExecutionAuthorized: false },
      execution,
      interpretation: activeInterpretation,
    });
  }
  if (url.endsWith("/planner/jobs/job_1/interpretations") && method === "GET") {
    const runs = activeInterpretationRuns.length
      ? activeInterpretationRuns
      : interpretationCreated ? [interpretationExecutionFixture] : [];
    return jsonResponse({
      jobId: "job_1",
      interpretations: interpretationCreated && activeInterpretation ? [activeInterpretation] : [],
      runs,
      count: interpretationCreated ? 1 : 0,
      runCount: runs.length,
    });
  }
  if (url.endsWith(`/planner/interpretations/${interpretationFixture.interpretationId}/evidence`)) {
    return jsonResponse(interpretationEvidenceFixture);
  }
  if (url.endsWith("/planner/jobs/job_1")) {
    return jsonResponse(jobDetail);
  }
  if (url.endsWith("/planner/jobs/job_1/events")) {
    return jsonResponse(events);
  }
  if (url.endsWith("/planner/jobs/job_1/tool-calls")) {
    return jsonResponse(toolCalls);
  }
  if (url.endsWith("/planner/jobs/job_1/artifacts")) {
    return jsonResponse(activeArtifacts);
  }
  if (url.endsWith("/planner/jobs/job_1/dependencies")) {
    return jsonResponse({
      jobId: "job_1", planId: "plan_1", planHash: "hash_1", planSchemaVersion: "0.1",
      graphHash: null, dependencyBindings: [], plannedBindingRecords: [], topologicalOrder: [],
      execution: null, bindingResolutions: [], artifactLineage: []
    });
  }
  if (url.endsWith("/planner/jobs/job_1/result")) {
    return jsonResponse(activeResult);
  }
  return jsonResponse({ detail: "not found" }, 404);
}

function jsonResponse(body: unknown, status = 200): Promise<Response> {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" }
    })
  );
}

class MockEventSource {
  url: string;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: (() => void) | null = null;
  listeners = new Map<string, Array<(event: MessageEvent) => void>>();

  constructor(url: string) {
    this.url = url;
    eventSources.push(this);
  }

  addEventListener(type: string, listener: EventListener) {
    const current = this.listeners.get(type) || [];
    current.push(listener as (event: MessageEvent) => void);
    this.listeners.set(type, current);
  }

  close() {
    // no-op for tests
  }

  emit(type: string, payload: unknown) {
    const message = new MessageEvent(type, { data: JSON.stringify(payload) });
    this.onmessage?.(message);
    (this.listeners.get(type) || []).forEach((listener) => listener(message));
  }
}
