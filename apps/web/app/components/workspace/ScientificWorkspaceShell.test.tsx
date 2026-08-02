import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createHash } from "node:crypto";

import { getWorkspace, patchWorkspace } from "../../lib/workspace-api";
import { getPlannerArtifactContent, getPlannerInterpretationEvidence, getPlannerJobArtifacts, getPlannerJobInterpretations } from "../../lib/planner-api";
import { ScientificWorkspaceShell } from "./ScientificWorkspaceShell";
import { validateAndOrderArtifactMetadata } from "./WorkspaceArtifactGallery";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";
import { encodeWorkspaceSelectionUrl, validateWorkspaceSelectionContext } from "./workspace-selection-contract";

vi.mock("../../lib/workspace-api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../lib/workspace-api")>();
  return { ...actual, getWorkspace: vi.fn(), patchWorkspace: vi.fn() };
});
vi.mock("../../lib/planner-api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../lib/planner-api")>();
  return { ...actual, getPlannerJobArtifacts: vi.fn(), getPlannerArtifactContent: vi.fn(), getPlannerJobInterpretations: vi.fn(), getPlannerInterpretationEvidence: vi.fn() };
});

const getWorkspaceMock = vi.mocked(getWorkspace);
const patchWorkspaceMock = vi.mocked(patchWorkspace);
const getArtifactsMock = vi.mocked(getPlannerJobArtifacts);
const getContentMock = vi.mocked(getPlannerArtifactContent);
const getInterpretationsMock = vi.mocked(getPlannerJobInterpretations);
const getEvidenceMock = vi.mocked(getPlannerInterpretationEvidence);
const HASH = "a".repeat(64);

beforeEach(() => {
  window.history.replaceState({}, "", "/workspaces/workspace_demo");
  getWorkspaceMock.mockReset();
  patchWorkspaceMock.mockReset();
  getArtifactsMock.mockReset();
  getContentMock.mockReset();
  getInterpretationsMock.mockReset();
  getEvidenceMock.mockReset();
  const bytes = new TextEncoder().encode(JSON.stringify({ rows: [{ objectId: "object_1", value: 2 }] })).buffer;
  const artifactHash = createHash("sha256").update(new Uint8Array(bytes)).digest("hex");
  getArtifactsMock.mockResolvedValue([{ id: "artifact_demo", artifactId: "artifact_demo", jobId: "job_demo", toolCallId: "tool_call_demo", type: "metrics_json", version: "1", name: "Demo metrics", sizeBytes: bytes.byteLength, contentType: "application/json", sha256: artifactHash, metadata: { projectId: "project_demo", stepId: "step_demo" } }]);
  getContentMock.mockResolvedValue(bytes);
  const claim = { schemaVersion: "1.0" as const, claimId: "claim_demo", claimType: "OBSERVATION" as const, subjectEvidenceIds: ["evidence_demo"], supportingEvidenceIds: ["evidence_demo"], limitingEvidenceIds: [], contradictingEvidenceIds: [], semanticPredicate: "HAS_VALUE", qualifiers: [], renderedText: "Exact value reported.", scope: "artifact", confidenceClass: "DIRECT" as const, groundingStatus: "GROUNDED" as const, displayOrder: 0 };
  const interpretation = { schemaVersion: "1.0" as const, interpretationId: "interpretation_demo", interpretationHash: HASH, sourceBundleId: "bundle_demo", sourceBundleHash: HASH, sourceJobId: "job_demo", sourcePlanId: "plan_demo", sourcePlanHash: HASH, mode: "DETERMINISTIC" as const, provider: "deterministic", providerVersion: "1.0", claims: [claim], globalWarnings: [], globalLimitations: [], recommendations: [], completeness: "COMPLETE" as const, partialResultState: false, repairCount: 0 as const, validationOutcome: "VALID", executionRecordId: "execution_demo" };
  getInterpretationsMock.mockResolvedValue({ jobId: "job_demo", interpretations: [interpretation], runs: [], count: 1, runCount: 0 });
  getEvidenceMock.mockResolvedValue({ interpretationId: "interpretation_demo", bundleId: "bundle_demo", bundleHash: HASH, sourceArtifactIds: ["artifact_demo"], bundleWarnings: [], bundleLimitations: [], evidenceItems: [{ schemaVersion: "1.0", evidenceItemId: "evidence_demo", semanticRole: "metric.value", evidenceKind: "SCALAR", subjectId: "artifact_demo", displayValue: "2", unit: null, sourceArtifactId: "artifact_demo", sourceArtifactChecksum: artifactHash, artifactContract: "platform.dataset.summary", artifactContractVersion: "1.0", sourceToolId: "tool.demo", sourceToolVersion: "1.0", fieldLocator: { fieldId: "metrics.value" }, warnings: [], limitations: [] }] });
  vi.stubGlobal("crypto", { subtle: { digest: async (_algorithm: string, value: BufferSource) => { const input = ArrayBuffer.isView(value) ? new Uint8Array(value.buffer, value.byteOffset, value.byteLength) : new Uint8Array(value as ArrayBuffer); const digest = createHash("sha256").update(input).digest(); return digest.buffer.slice(digest.byteOffset, digest.byteOffset + digest.byteLength); } } });
  const snapshot = workspaceSnapshotFixture();
  for (const panel of snapshot.panels.filter((item) => item.panelKind === "FINDINGS" || item.panelKind === "EVIDENCE")) {
    const source = panel.sourceRefs.find((item) => item.kind === "ARTIFACT");
    if (source) source.sourceHash = artifactHash;
  }
  getWorkspaceMock.mockResolvedValue({ data: snapshot, status: 200, etag: "etag", idempotentReplay: null });
});

describe("Phase 10M-2 ScientificWorkspaceShell", () => {
  it("loads metadata-first and renders the sealed shell with one active panel", async () => {
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    expect(screen.getByRole("heading", { name: "Loading Workspace" })).not.toBeNull();
    expect(await screen.findByTestId("scientific-workspace-shell")).not.toBeNull();
    expect(screen.getByRole("navigation", { name: "Workspace sections" })).not.toBeNull();
    expect(screen.getByRole("heading", { name: "Analysis overview" })).not.toBeNull();
    expect(screen.getAllByRole("button").filter((button) => button.getAttribute("aria-current") === "page")).toHaveLength(1);
    expect(getWorkspaceMock).toHaveBeenCalledWith("workspace_demo", expect.objectContaining({ signal: expect.any(AbortSignal) }));
  });

  it("uses exact panel deep links and restores browser history", async () => {
    window.history.replaceState({}, "", "/workspaces/workspace_demo?panel=panel_data");
    const user = userEvent.setup();
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    expect(await screen.findByRole("heading", { name: "Dataset context" })).not.toBeNull();
    await user.click(screen.getByRole("button", { name: /Results/ }));
    expect(screen.getByRole("heading", { name: "Scientific results" })).not.toBeNull();
    expect(window.location.search).toBe("?panel=panel_results");
    window.history.back();
    window.dispatchEvent(new PopStateEvent("popstate"));
    await waitFor(() => expect(screen.getByRole("heading", { name: "Dataset context" })).not.toBeNull());
  });

  it("reports an unknown panel without choosing a substitute", async () => {
    window.history.replaceState({}, "", "/workspaces/workspace_demo?panel=panel_invented");
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    const alert = await screen.findByTestId("workspace-invalid-panel");
    expect(alert.textContent).toContain("panel_invented");
    expect(screen.getByRole("heading", { name: "No active panel" })).not.toBeNull();
  });

  it.each(["RUNNING", "PARTIAL_RESULTS", "FAILED", "STALE", "LEGACY_READ_ONLY"] as const)("projects %s as a typed Workspace state", async (status) => {
    getWorkspaceMock.mockResolvedValue({ data: workspaceSnapshotFixture(status), status: 200, etag: "etag", idempotentReplay: null });
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    expect((await screen.findAllByText(status)).length).toBeGreaterThan(0);
    expect(screen.getByRole("status", { name: "Workspace source state" }).textContent).toContain("Exact historical bindings are preserved");
  });

  it("renders unsupported content as inert text", async () => {
    const snapshot = workspaceSnapshotFixture();
    snapshot.panels[0].state = "CONTRACT_UNSUPPORTED";
    snapshot.panels[0].unsupportedReason = '<script>window.__workspaceInjected=true</script><iframe src="https://example.invalid">';
    getWorkspaceMock.mockResolvedValue({ data: snapshot, status: 200, etag: "etag", idempotentReplay: null });
    const { container } = render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    expect(await screen.findByText(snapshot.panels[0].unsupportedReason)).not.toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
  });

  it("opens the inspector, moves focus, and closes with Escape", async () => {
    const user = userEvent.setup();
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    await screen.findByTestId("scientific-workspace-shell");
    await user.click(screen.getByRole("button", { name: "Inspector" }));
    const dialog = screen.getByRole("dialog", { name: "Context inspector" });
    const close = within(dialog).getByRole("button", { name: "Close inspector" });
    expect(close).toHaveFocus();
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog", { name: "Context inspector" })).toBeNull();
    expect(screen.getByRole("button", { name: "Inspector" })).toHaveFocus();
  });

  it("opens the bounded mobile context drawer and switches one active panel", async () => {
    const user = userEvent.setup();
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    await screen.findByTestId("scientific-workspace-shell");
    await user.click(screen.getByRole("button", { name: "Open data context" }));
    const drawer = screen.getByRole("dialog", { name: "Data context drawer" });
    await user.click(within(drawer).getByRole("button", { name: "Scientific results" }));
    expect(screen.queryByRole("dialog", { name: "Data context drawer" })).toBeNull();
    expect(screen.getByRole("heading", { name: "Scientific results" })).not.toBeNull();
  });

  it("restores, clears, and exposes canonical URL selection without a substitute", async () => {
    const token = encodeWorkspaceSelectionUrl(datasetSelection());
    window.history.replaceState({}, "", `/workspaces/workspace_demo?panel=panel_data&selection=${token}`);
    const user = userEvent.setup();
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    expect(await screen.findByTestId("workspace-selection-status")).toHaveTextContent("Restored canonical selection");
    expect(screen.getByTestId("workspace-selection-status")).toHaveTextContent("DATASET_SAMPLE");
    await user.click(screen.getByRole("button", { name: "Inspector" }));
    expect(screen.getByRole("heading", { name: "Canonical selection" })).not.toBeNull();
    expect(screen.getAllByText("Exact kind and source scope match.").length).toBeGreaterThan(1);
    await user.click(screen.getByRole("button", { name: "Clear selection" }));
    expect(screen.getByTestId("workspace-selection-status")).toHaveTextContent("Canonical selection cleared");
    expect(window.location.search).toBe("?panel=panel_data");
  });

  it("selects an exact Artifact and pins only through the existing ETag patch", async () => {
    const snapshot = workspaceSnapshotFixture();
    patchWorkspaceMock.mockResolvedValue({ data: snapshot, status: 200, etag: "etag_next", idempotentReplay: false });
    const user = userEvent.setup();
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    await screen.findByTestId("scientific-workspace-shell");
    await user.click(screen.getByRole("button", { name: /Results/ }));
    await user.click(screen.getByTestId("workspace-select-artifact-panel_results"));
    expect(screen.getByTestId("workspace-selection-status")).toHaveTextContent("Selected exact ARTIFACT");
    expect(window.location.search).toContain("selection=");
    await user.click(screen.getByRole("button", { name: "Inspector" }));
    await user.click(screen.getByRole("button", { name: "Pin selection" }));
    await waitFor(() => expect(patchWorkspaceMock).toHaveBeenCalledWith("workspace_demo", "etag", expect.objectContaining({ pinnedSelection: expect.objectContaining({ primary: expect.objectContaining({ artifactId: "artifact_demo" }) }) })));
    expect(screen.getByText(/Pin state: SAVED/u)).not.toBeNull();
    expect(screen.getByRole("status", { name: "Panel selection compatibility" })).toHaveTextContent("EXACT");
  });

  it("loads Artifact metadata first and requests the exact payload only after Open", async () => {
    const user = userEvent.setup();
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    await screen.findByTestId("scientific-workspace-shell");
    await user.click(screen.getByRole("button", { name: /Results/ }));
    expect(await screen.findByTestId("workspace-artifact-gallery")).toHaveTextContent("payload requests remain zero");
    expect(getContentMock).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Open Demo metrics" }));
    expect(await screen.findByText(/bounded payload record/u)).not.toBeNull();
    expect(getContentMock).toHaveBeenCalledTimes(1);
    expect(screen.getByRole("table")).toHaveTextContent("object_1");
  });

  it("accepts the exact 256-record metadata cap and rejects record 257 without truncation", async () => {
    const artifact = (await getArtifactsMock("job_demo"))[0];
    const bounded = Array.from({ length: 256 }, (_, index) => ({
      ...artifact,
      id: `artifact_${index.toString().padStart(3, "0")}`,
      artifactId: `artifact_${index.toString().padStart(3, "0")}`,
      name: `Bounded Artifact ${index.toString().padStart(3, "0")}`,
    }));
    const sourceScope = { workspaceId: "workspace_demo", workspaceRevision: 1, projectId: "project_demo", sourceJobId: "job_demo" };
    expect(validateAndOrderArtifactMetadata(bounded, sourceScope)).toHaveLength(256);
    expect(() => validateAndOrderArtifactMetadata([...bounded, { ...bounded[0], id: "artifact_256", artifactId: "artifact_256", name: "Rejected Artifact 256" }], sourceScope)).toThrow("ARTIFACT_METADATA_CAP_EXCEEDED: 257 exceeds 256.");
  });

  it("navigates exact Artifact lineage and grounded evidence through the M3 selection runtime", async () => {
    const user = userEvent.setup();
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    await screen.findByTestId("scientific-workspace-shell");
    await user.click(screen.getByRole("button", { name: /Results/ }));
    await screen.findByTestId("workspace-artifact-gallery");
    await user.click(screen.getByRole("button", { name: "Evidence" }));
    expect(await screen.findByRole("heading", { name: "Scientific evidence" })).not.toBeNull();
    expect(await screen.findByTestId("workspace-grounded-evidence")).toHaveTextContent("metrics.value");
    await user.click(screen.getByRole("button", { name: "Select exact evidence" }));
    expect(screen.getByTestId("workspace-selection-status")).toHaveTextContent("EVIDENCE_ITEM");
    await user.click(screen.getByRole("button", { name: /Results/ }));
    await user.click(screen.getByRole("button", { name: "Lineage" }));
    expect(await screen.findByRole("heading", { name: "Provenance" })).not.toBeNull();
    expect(screen.getByTestId("workspace-artifact-lineage")).toHaveTextContent("artifact_demo");
    expect(window.location.search).toContain("panel=panel_provenance");
  });

  it("does not request a stale panel payload and keeps the safe download action", async () => {
    const snapshot = workspaceSnapshotFixture();
    snapshot.panels.find((panel) => panel.panelKind === "SCIENTIFIC_RESULT")!.state = "STALE";
    getWorkspaceMock.mockResolvedValue({ data: snapshot, status: 200, etag: "etag", idempotentReplay: null });
    const user = userEvent.setup();
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    await user.click(await screen.findByRole("button", { name: /Results/ }));
    const open = await screen.findByRole("button", { name: /Open Demo metrics/ });
    expect(open).toBeDisabled();
    expect(screen.getByRole("button", { name: /Download Demo metrics/ })).not.toBeDisabled();
    expect(getContentMock).not.toHaveBeenCalled();
  });

  it("aborts stale metadata requests when the route identity changes", async () => {
    let firstSignal: AbortSignal | undefined;
    getWorkspaceMock
      .mockImplementationOnce((_workspaceId, options) => {
        firstSignal = options?.signal;
        return new Promise(() => undefined);
      })
      .mockResolvedValueOnce({ data: workspaceSnapshotFixture(), status: 200, etag: "etag", idempotentReplay: null });
    const { rerender } = render(<ScientificWorkspaceShell workspaceId="workspace_old" />);
    await waitFor(() => expect(firstSignal).toBeDefined());
    rerender(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    await screen.findByTestId("scientific-workspace-shell");
    expect(firstSignal?.aborted).toBe(true);
  });

  it("renders typed not-found and bounded error states", async () => {
    getWorkspaceMock.mockRejectedValueOnce(Object.assign(new Error("missing"), { status: 404 }));
    const { rerender } = render(<ScientificWorkspaceShell workspaceId="missing" />);
    expect(await screen.findByRole("heading", { name: "Workspace not found" })).not.toBeNull();
    getWorkspaceMock.mockRejectedValueOnce(new Error("private\nstack\tmessage"));
    rerender(<ScientificWorkspaceShell workspaceId="error" />);
    expect(await screen.findByRole("heading", { name: "Workspace unavailable" })).not.toBeNull();
    expect(screen.getByText("private stack message")).not.toBeNull();
  });
});

function datasetSelection() {
  return validateWorkspaceSelectionContext({
    schemaVersion: "1.0", sourceScopeHash: "a".repeat(64),
    primary: { selectionSchemaVersion: "1.0", kind: "DATASET_SAMPLE", sourceScopeHash: "a".repeat(64), projectId: "project_demo", datasetId: "dataset_demo", datasetVersion: "v1", objectId: "object_1", sampleRef: "sample_1" },
    secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false,
  });
}
