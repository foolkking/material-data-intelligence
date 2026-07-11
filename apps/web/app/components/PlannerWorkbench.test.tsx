import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import adapterGeneratedViewerScene from "../../../../docs/phase10f/evidence/phase10f12_viewer_scene_minimal_adapter/generated_viewer_scene.json";
import adapterGeneratedViewerSceneManifest from "../../../../docs/phase10f/evidence/phase10f12_viewer_scene_minimal_adapter/generated_viewer_scene_manifest.json";
import liveAdapterPayload from "../../../../docs/phase10f/evidence/phase10f13_viewer_scene_live_adapter_browser/live_payload.json";
import { PlannerWorkbench } from "./PlannerWorkbench";

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
  structureSummary: { nStructures: 0, elements: [], formulaStats: { total: 5, uniqueCount: 5 } }
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

beforeEach(() => {
  eventSources = [];
  savedSecrets = [];
  activeArtifacts = artifacts;
  activeResult = result;
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
  });

  it("opens model dialog from the top bar, saves a secret without browser storage leakage, and tests the provider", async () => {
    const user = userEvent.setup();
    const apiKey = "sk-ui-secret-value";
    render(<PlannerWorkbench />);

    await user.click(contextButton(1));
    const modelDialog = screen.getByRole("dialog");
    expect(modelDialog).not.toBeNull();
    await user.selectOptions(modelDialog.querySelectorAll("select")[0], "openai_compatible");
    await user.clear(screen.getByLabelText("API Key"));
    await user.type(screen.getByLabelText("API Key"), apiKey);
    await user.click(within(modelDialog).getAllByRole("button")[1]);

    await waitFor(() => expect((screen.getByLabelText("API Key") as HTMLInputElement).value).toBe(""));
    expect(document.body.textContent).not.toContain(apiKey);
    expect(JSON.stringify(window.localStorage)).not.toContain(apiKey);
    expect(JSON.stringify(window.sessionStorage)).not.toContain(apiKey);
    expect(await screen.findByText(/Demo LLM Key/)).not.toBeNull();
    expect((await screen.findAllByText("Live LLM / deepseek-chat")).length).toBeGreaterThan(0);

    await user.click(within(modelDialog).getAllByRole("button")[3]);
    expect(await screen.findByText("Provider connection succeeded and returned a valid AnalysisPlan.")).not.toBeNull();
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
    expect(within(results).getByText("phase10d1.viewer_scene.v1")).not.toBeNull();

    expect(within(results).getByTestId("viewer-manifest-preview")).not.toBeNull();
    expect(within(results).getByText("Export package manifest")).not.toBeNull();
    expect(within(results).getByText("Renderer status")).not.toBeNull();
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
    expect(screen.queryByText("structure.viewer_3d")).toBeNull();
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
      llmProvider: { status: "ok", provider: "mock", model: "mock" }
    });
  }
  if (url.endsWith("/planner/providers")) {
    return jsonResponse({
      providers: [
        { id: "mock", label: "Mock Planner", provider: "mock", requiresSecret: false },
        { id: "deepseek", label: "DeepSeek", provider: "openai_compatible", baseUrl: "https://api.deepseek.com/v1", defaultModel: "deepseek-chat", requiresSecret: true }
      ]
    });
  }
  if (url.endsWith("/planner/providers/status")) {
    return jsonResponse({ ok: true, provider: "mock", model: "mock", status: "ready", message: "Mock Planner is active." });
  }
  if (method === "POST" && url.endsWith("/planner/providers/resolve")) {
    const body = JSON.parse(String(init?.body || "{}"));
    expect(JSON.stringify(body)).not.toContain("sk-ui-secret-value");
    if (body.provider === "openai_compatible" && body.secretId) {
      return jsonResponse({
        ok: true,
        provider: "openai_compatible",
        model: body.model || "deepseek-chat",
        status: "ready",
        willUseLiveProvider: true,
        secretConfigured: true,
        source: "secret",
        message: "Current planner job configuration will use an OpenAI-compatible LLM.",
        redacted: true
      });
    }
    if (body.provider === "openai_compatible") {
      return jsonResponse({
        ok: false,
        provider: "openai_compatible",
        model: body.model || "deepseek-chat",
        status: "not_configured",
        willUseLiveProvider: false,
        secretConfigured: false,
        source: "missing_secret",
        message: "Current planner job configuration needs a saved API key before it can use a live LLM.",
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
    expect(JSON.stringify(body)).not.toContain("sk-ui-secret-value");
    return jsonResponse({ ok: true, provider: body.provider, model: body.model || "mock", latencyMs: 9, validated: true, message: "Provider connection succeeded and returned a valid AnalysisPlan.", redacted: true });
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
    expect(JSON.stringify(body)).not.toContain("sk-ui-secret-value");
    return jsonResponse(createdJob);
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
