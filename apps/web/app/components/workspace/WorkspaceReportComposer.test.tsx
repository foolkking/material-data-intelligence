import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  downloadReportComposition,
  finalizeReportComposition,
  getReportComposition,
  getReportCompositionRecipe,
  getReportCompositionSources,
  listReportCompositions,
  previewReportComposition,
  type RecipeReplayManifest,
  type ReportCompositionSnapshot,
  type ReportSourceReference,
} from "../../lib/report-composition-api";
import { WorkspaceReportComposer } from "./WorkspaceReportComposer";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";

vi.mock("../../lib/report-composition-api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../lib/report-composition-api")>();
  return {
    ...actual,
    downloadReportComposition: vi.fn(),
    finalizeReportComposition: vi.fn(),
    getReportComposition: vi.fn(),
    getReportCompositionRecipe: vi.fn(),
    getReportCompositionSources: vi.fn(),
    listReportCompositions: vi.fn(),
    previewReportComposition: vi.fn(),
  };
});

const sourcesMock = vi.mocked(getReportCompositionSources);
const previewMock = vi.mocked(previewReportComposition);
const finalizeMock = vi.mocked(finalizeReportComposition);
const historyMock = vi.mocked(listReportCompositions);
const reportMock = vi.mocked(getReportComposition);
const recipeMock = vi.mocked(getReportCompositionRecipe);
const downloadMock = vi.mocked(downloadReportComposition);
const HASH = "a".repeat(64);

beforeEach(() => {
  vi.clearAllMocks();
  sourcesMock.mockResolvedValue({
    schemaVersion: "1.0", workspaceId: "workspace_demo", workspaceRevision: 1,
    workspaceProjectionHash: HASH, sources: [figureSource(), metadataSource(), unsupportedSource()],
    mandatoryDisclosures: [disclosure()], sourceCount: 3, mandatoryDisclosureCount: 1,
    artifactContractInventoryCount: 42, metadataOnly: true, heavyArtifactPayloadRequests: 0, webglContexts: 0,
  });
  historyMock.mockResolvedValue({ workspaceId: "workspace_demo", items: [], count: 0, immutableHistory: true });
  previewMock.mockResolvedValue({ report: reportFixture(true), recipe: recipeFixture(true), sourceCount: 3, mandatoryDisclosureCount: 1, predictedOutcome: "REPORT_READY_WITH_LIMITS", persisted: false, noExecution: { planCreated: false, jobCreated: false, toolCallCreated: false, queueMessageCreated: false } });
  finalizeMock.mockResolvedValue({ reportId: "report_saved", reportHash: HASH, recipeId: "recipe_saved", recipeHash: HASH, compositionHash: HASH, workspaceId: "workspace_demo", workspaceRevision: 1, outcome: "REPORT_READY_WITH_LIMITS", idempotentReplay: false, immutable: true, noExecution: { planCreated: false, jobCreated: false, toolCallCreated: false, queueMessageCreated: false } });
  reportMock.mockResolvedValue({ legacyReadOnly: false, report: reportFixture(false), recipeId: "recipe_saved" });
  recipeMock.mockResolvedValue({ legacyReadOnly: false, recipe: recipeFixture(false) });
  downloadMock.mockResolvedValue({ blob: new Blob(["report"]), filename: "scientific-report-report_saved.json", exportHash: HASH });
  vi.stubGlobal("URL", { ...URL, createObjectURL: vi.fn(() => "blob:report"), revokeObjectURL: vi.fn() });
  HTMLAnchorElement.prototype.click = vi.fn();
});

describe("Phase 10M-5 WorkspaceReportComposer", () => {
  it("loads metadata-only inventory and keeps mandatory disclosures immutable", async () => {
    render(<WorkspaceReportComposer workspace={workspaceSnapshotFixture().workspace} />);
    expect(await screen.findByText("3 exact sources; 1 mandatory disclosures")).not.toBeNull();
    expect(sourcesMock).toHaveBeenCalledWith("workspace_demo", expect.any(AbortSignal));
    expect(screen.getByText("Required partial execution disclosure.")).not.toBeNull();
    expect(screen.queryByRole("button", { name: /Remove disclosure/u })).toBeNull();
    expect(screen.getByRole("button", { name: "Add artifact_unsupported to report" })).toBeDisabled();
    expect(screen.getByText("Metadata only")).not.toBeNull();
  });

  it("selects exact eligible and metadata fallback sources, orders them, and previews without writes", async () => {
    const user = userEvent.setup();
    render(<WorkspaceReportComposer workspace={workspaceSnapshotFixture().workspace} />);
    await screen.findByText("3 exact sources; 1 mandatory disclosures");
    await user.click(screen.getByRole("button", { name: "Add artifact_plot to report" }));
    await user.click(screen.getByRole("button", { name: "Add artifact_structure to report" }));
    await user.click(screen.getByRole("button", { name: "Move artifact_structure up" }));
    await user.type(screen.getAllByLabelText("Caption", { selector: "input" })[0], "Exact backend figure");
    await user.click(screen.getByRole("button", { name: "Preview report" }));
    expect(await screen.findByRole("heading", { name: "Deterministic preview" })).not.toBeNull();
    expect(screen.getByText("REPORT_READY_WITH_LIMITS; preview writes: 0")).toHaveAttribute("role", "status");
    expect(screen.getByText(/Report writes 0; Recipe writes 0; Job creation 0/u)).not.toBeNull();
    expect(previewMock).toHaveBeenCalledWith("workspace_demo", expect.objectContaining({
      expectedWorkspaceRevision: 1,
      selectedArtifactIds: ["artifact_structure", "artifact_plot"],
      itemOrder: ["artifact_structure", "artifact_plot"],
    }), expect.any(AbortSignal));
    expect(finalizeMock).not.toHaveBeenCalled();
  });

  it("finalizes only after explicit action and opens immutable Report/Recipe history", async () => {
    const user = userEvent.setup();
    historyMock.mockResolvedValueOnce({ workspaceId: "workspace_demo", items: [], count: 0, immutableHistory: true }).mockResolvedValueOnce({ workspaceId: "workspace_demo", items: [historyItem()], count: 1, immutableHistory: true });
    render(<WorkspaceReportComposer workspace={workspaceSnapshotFixture().workspace} />);
    await screen.findByText("3 exact sources; 1 mandatory disclosures");
    await user.click(screen.getByRole("button", { name: "Add artifact_plot to report" }));
    await user.click(screen.getByRole("button", { name: "Preview report" }));
    await user.click(await screen.findByRole("button", { name: "Finalize report" }));
    await waitFor(() => expect(finalizeMock).toHaveBeenCalledTimes(1));
    expect(finalizeMock.mock.calls[0][2]).toMatch(/^m5-workspace_demo-1-\d+$/u);
    expect(await screen.findByRole("heading", { name: "Report detail" })).not.toBeNull();
    expect(screen.getByText("Exact non-executable Recipe")).not.toBeNull();
    expect(screen.getAllByText("No", { selector: "dd" })).toHaveLength(2);
    expect(reportMock).toHaveBeenCalledWith("workspace_demo", "report_saved", expect.any(AbortSignal));
    expect(recipeMock).toHaveBeenCalledWith("workspace_demo", "report_saved", expect.any(AbortSignal));
  });

  it("renders malicious persisted strings as inert text", async () => {
    const malicious = "<script>window.__m5Injected=true</script><iframe src='https://example.invalid'>";
    const report = reportFixture(false);
    report.title = malicious;
    historyMock.mockResolvedValue({ workspaceId: "workspace_demo", items: [{ ...historyItem(), title: malicious }], count: 1, immutableHistory: true });
    reportMock.mockResolvedValue({ legacyReadOnly: false, report, recipeId: "recipe_saved" });
    const user = userEvent.setup();
    const { container } = render(<WorkspaceReportComposer workspace={workspaceSnapshotFixture().workspace} />);
    await screen.findByText("3 exact sources; 1 mandatory disclosures");
    await user.click(screen.getByRole("tab", { name: "History" }));
    await user.click(screen.getByRole("button", { name: "Open" }));
    expect(await screen.findAllByText(malicious)).not.toHaveLength(0);
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
  });

  it("downloads only the server-authorized immutable export", async () => {
    const user = userEvent.setup();
    historyMock.mockResolvedValue({ workspaceId: "workspace_demo", items: [historyItem()], count: 1, immutableHistory: true });
    render(<WorkspaceReportComposer workspace={workspaceSnapshotFixture().workspace} />);
    await screen.findByText("3 exact sources; 1 mandatory disclosures");
    await user.click(screen.getByRole("tab", { name: "History" }));
    await user.click(screen.getByRole("button", { name: "Open" }));
    await user.click(await screen.findByRole("button", { name: "Download canonical JSON" }));
    expect(downloadMock).toHaveBeenCalledWith("workspace_demo", "report_saved", "json", expect.any(AbortSignal));
    expect(URL.createObjectURL).toHaveBeenCalledTimes(1);
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:report");
  });

  it("uses a focus-contained mobile source sheet and restores focus on Escape", async () => {
    const user = userEvent.setup();
    render(<WorkspaceReportComposer workspace={workspaceSnapshotFixture().workspace} />);
    await screen.findByText("3 exact sources; 1 mandatory disclosures");
    const trigger = screen.getByRole("button", { name: "Choose sources" });
    await user.click(trigger);
    const dialog = screen.getByRole("dialog", { name: "Source inventory" });
    expect(within(dialog).getByRole("button", { name: "Close source picker" })).toHaveFocus();
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog", { name: "Source inventory" })).toBeNull();
    expect(trigger).toHaveFocus();
  });

  it("labels the draft as session-only and protects dirty drafts from refresh", async () => {
    const onDirty = vi.fn();
    const user = userEvent.setup();
    render(<WorkspaceReportComposer workspace={workspaceSnapshotFixture().workspace} onDraftDirtyChange={onDirty} />);
    await screen.findByText("3 exact sources; 1 mandatory disclosures");
    expect(screen.getByText(/Draft is not saved until Finalize/u)).not.toBeNull();
    await user.click(screen.getByRole("button", { name: "Add artifact_plot to report" }));
    await waitFor(() => expect(onDirty).toHaveBeenLastCalledWith(true));
    const event = new Event("beforeunload", { cancelable: true });
    window.dispatchEvent(event);
    expect(event.defaultPrevented).toBe(true);
    expect(screen.getByText(/Unsaved report draft/u)).not.toBeNull();
  });
});

function source(overrides: Partial<ReportSourceReference>): ReportSourceReference {
  return {
    sourceKind: "ARTIFACT", sourceId: "artifact_plot", sourceHash: HASH,
    contract: "plotly_json", contractVersion: "1.0", projectId: "project_demo",
    datasetId: "dataset_demo", datasetVersion: "v1", jobId: "job_demo",
    toolCallId: "tool_call_demo", stepId: "step_demo", panelId: "panel_results",
    artifactId: "artifact_plot", artifactChecksum: HASH, interpretationId: null,
    claimId: null, evidenceItemId: null, role: "REPORT_FIGURE_SOURCE", state: "ELIGIBLE",
    representation: "STATIC_FIGURE", fallback: "Backend-produced plot.", reason: null,
    ...overrides,
  };
}

function figureSource() { return source({}); }
function metadataSource() { return source({ sourceId: "artifact_structure", artifactId: "artifact_structure", contract: "structure_json", role: "REPORT_METADATA_ONLY", state: "METADATA_ONLY", representation: "METADATA", fallback: "Structure identity and approved text fallback." }); }
function unsupportedSource() { return source({ sourceId: "artifact_unsupported", artifactId: "artifact_unsupported", contract: "unknown_contract", role: "REPORT_UNSUPPORTED", state: "UNSUPPORTED", representation: "NONE", fallback: null, reason: "Unknown Artifact contract." }); }
function disclosure() { return source({ sourceKind: "DISCLOSURE", sourceId: "disclosure_partial", artifactId: null, artifactChecksum: null, contract: "report.disclosure", role: "REPORT_DISCLOSURE_ONLY", state: "MANDATORY", representation: "DISCLOSURE", fallback: "Required partial execution disclosure." }); }

function reportFixture(preview: boolean): ReportCompositionSnapshot {
  const ids = ["TITLE", "ANALYSIS_GOAL", "DATASET_RESOURCE_SCOPE", "METHODS_PLAN", "EXECUTION_STATUS", "SELECTED_RESULTS", "GROUNDED_FINDINGS", "WARNINGS_LIMITATIONS", "FAILED_BLOCKED_MISSING", "EVIDENCE_PROVENANCE", "ENVIRONMENT_REFERENCES", "EXACT_RERUN_RECIPE"];
  return { schemaVersion: "1.0", reportId: preview ? "report_preview" : "report_saved", reportHash: HASH, compositionHash: HASH, recipeId: preview ? "recipe_preview" : "recipe_saved", workspaceId: "workspace_demo", workspaceRevision: 1, projectId: "project_demo", datasetId: "dataset_demo", datasetVersion: "v1", sourceJobId: "job_demo", sourcePlanId: "plan_demo", sourcePlanHash: HASH, sourcePlanSchemaVersion: "0.2", title: "Scientific report", analysisGoal: "Evaluate exact persisted results", outcome: "REPORT_READY_WITH_LIMITS", selectedSources: [figureSource()], mandatoryDisclosures: [disclosure()], sections: ids.map((sectionId) => ({ sectionId, title: sectionId.replaceAll("_", " "), status: "READY", items: [`${sectionId} exact content`] })), warnings: ["Required warning"], limitations: [], executionAuthorized: false, scientificAuthority: false, createdAt: "2026-08-01T00:00:00Z" };
}

function recipeFixture(preview: boolean): RecipeReplayManifest {
  return { schemaVersion: "1.0", recipeId: preview ? "recipe_preview" : "recipe_saved", recipeHash: HASH, compositionHash: HASH, sourceReportId: preview ? "report_preview" : "report_saved", sourceReportHash: HASH, workspaceId: "workspace_demo", workspaceRevision: 1, projectId: "project_demo", datasetId: "dataset_demo", datasetVersion: "v1", datasetHash: HASH, profileId: "profile_demo", profileVersion: "2.0", profileHash: HASH, intentId: "intent_demo", intentHash: HASH, eligibilityResolutionId: "eligibility_demo", eligibilityResolutionHash: HASH, plannerDecisionId: "decision_demo", plannerDecisionHash: HASH, analysisPlanId: "plan_demo", analysisPlanHash: HASH, planSchemaVersion: "0.2", dependencyModel: "TYPED_ARTIFACT_BINDINGS", graphHash: HASH, steps: [{ stepId: "step_demo", toolId: "tool.demo", toolVersion: "1.0", adapterVersion: "1.0", params: {}, inputRefs: [], expectedOutputContracts: ["plotly_json"] }], dependencyBindings: [], sourceResourceBindings: [], originalArtifacts: [figureSource()], executionOutcome: "PARTIAL_RESULTS", providerProvenance: null, environmentProvenance: {}, warnings: ["Required warning"], limitations: [], outcome: "RECIPE_READY_WITH_LIMITS", executionAuthorized: false, planCreated: false, jobCreated: false, queueMessageCreated: false, automaticReplay: false, createdAt: "2026-08-01T00:00:00Z" };
}

function historyItem() {
  return { reportId: "report_saved", recipeId: "recipe_saved", version: "m5.report_recipe.v1", title: "Scientific report", reportHash: HASH, recipeHash: HASH, compositionHash: HASH, workspaceId: "workspace_demo", workspaceRevision: 1, sourceJobId: "job_demo", outcome: "REPORT_READY_WITH_LIMITS", createdAt: "2026-08-01T00:00:00Z", legacyReadOnly: false, exportFormats: ["json", "markdown"] as Array<"json" | "markdown"> };
}
