import { describe, expect, it, vi } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import type { WorkspacePanel } from "../../lib/workspace-api";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";
import { validateWorkspaceSelectionContext } from "./workspace-selection-contract";
import { artifactSelectionFromPanel, claimSelection, coordinationSiteSelection, datasetSampleSelection, evidenceItemSelection, resolvePanelSelection, WorkspaceSelectionStore } from "./workspace-selection-runtime";

const HASH = "a".repeat(64);

describe("Phase 10M-3 exact selection runtime", () => {
  it("delivers only to declared compatible panels and suppresses semantic replay", () => {
    const snapshot = workspaceSnapshotFixture();
    const source = declared(snapshot.panels[1], [], ["DATASET_SAMPLE"]);
    const compatible = declared(snapshot.panels[0], ["DATASET_SAMPLE"], []);
    const unrelated = declared(snapshot.panels[3], ["CLAIM"], []);
    const store = new WorkspaceSelectionStore(snapshot.workspace);
    const sourceReceive = vi.fn(), compatibleReceive = vi.fn(), unrelatedReceive = vi.fn();
    store.subscribe(source, sourceReceive);
    store.subscribe(compatible, compatibleReceive);
    store.subscribe(unrelated, unrelatedReceive);
    const value = datasetSelection();
    store.set(value, source.panelId);
    store.set(value, source.panelId);
    expect(sourceReceive).toHaveBeenLastCalledWith(expect.objectContaining({ compatibility: "NOT_APPLICABLE", transaction: 1 }));
    expect(compatibleReceive).toHaveBeenLastCalledWith(expect.objectContaining({ compatibility: "EXACT", context: value, transaction: 1, originPanelId: source.panelId }));
    expect(unrelatedReceive).toHaveBeenLastCalledWith(expect.objectContaining({ compatibility: "NOT_APPLICABLE", context: null }));
    expect(sourceReceive).toHaveBeenCalledTimes(2);
    expect(compatibleReceive).toHaveBeenCalledTimes(2);
  });

  it("returns typed stale and unsupported outcomes without a substitute", () => {
    const snapshot = workspaceSnapshotFixture();
    const panel = declared(snapshot.panels[2], ["DATASET_SAMPLE"], []);
    expect(resolvePanelSelection({ ...panel, state: "STALE" }, datasetSelection(), snapshot.workspace)).toMatchObject({ compatibility: "STALE", context: null });
    expect(resolvePanelSelection({ ...panel, state: "CONTRACT_UNSUPPORTED" }, datasetSelection(), snapshot.workspace)).toMatchObject({ compatibility: "UNSUPPORTED", context: null });
    expect(resolvePanelSelection(declared(panel, ["CLAIM"], []), datasetSelection(), snapshot.workspace)).toMatchObject({ compatibility: "NOT_APPLICABLE", context: null });
  });

  it("rejects foreign workspace, project, job, dataset, and stale version authority", () => {
    const snapshot = workspaceSnapshotFixture();
    const value = datasetSelection();
    const staleScope = validateWorkspaceSelectionContext({ ...value, sourceScopeHash: "b".repeat(64), primary: { ...value.primary!, sourceScopeHash: "b".repeat(64) } });
    expect(() => new WorkspaceSelectionStore(snapshot.workspace, staleScope)).toThrowError(/STALE_SOURCE_SCOPE/u);
    expect(() => new WorkspaceSelectionStore(snapshot.workspace, mutate(value, { projectId: "project_foreign" }))).toThrowError(/FOREIGN_PROJECT/u);
    expect(() => new WorkspaceSelectionStore(snapshot.workspace, mutate(value, { datasetId: "dataset_foreign" }))).toThrowError(/FOREIGN_DATASET/u);
    expect(() => new WorkspaceSelectionStore(snapshot.workspace, mutate(value, { datasetVersion: "v2" }))).toThrowError(/STALE_DATASET_VERSION/u);
  });

  it("creates whole-artifact selections only from exact declared source records", () => {
    const snapshot = workspaceSnapshotFixture();
    const result = snapshot.panels.find((panel) => panel.panelKind === "SCIENTIFIC_RESULT")!;
    const selection = artifactSelectionFromPanel(result, snapshot.workspace);
    expect(selection).toMatchObject({ primary: { kind: "ARTIFACT", artifactId: "artifact_demo", artifactChecksum: HASH, artifactContract: "platform.dataset.summary" } });
    expect(resolvePanelSelection(result, selection, snapshot.workspace)).toMatchObject({ compatibility: "EXACT" });
    const injected = validateWorkspaceSelectionContext({ ...selection!, primary: { ...selection!.primary!, artifactId: "artifact_foreign" } });
    expect(resolvePanelSelection(result, injected, snapshot.workspace)).toMatchObject({ compatibility: "NOT_APPLICABLE", context: null });
    expect(artifactSelectionFromPanel({ ...result, emittedSelectionKinds: [] }, snapshot.workspace)).toBeNull();
  });

  it("emits exact Dataset sample identities through the declared Result panel", () => {
    const snapshot = workspaceSnapshotFixture();
    const result = snapshot.panels.find((panel) => panel.panelKind === "SCIENTIFIC_RESULT")!;
    const selection = datasetSampleSelection(snapshot.workspace, {
      objectId: "object_1",
      sampleRef: "sample_1",
      sampleKey: "object_1:sample_1",
    });
    expect(result.emittedSelectionKinds).toContain("DATASET_SAMPLE");
    expect(resolvePanelSelection(result, selection, snapshot.workspace)).toMatchObject({ compatibility: "EXACT", context: selection });
    expect(() => datasetSampleSelection(snapshot.workspace, {
      objectId: "object_1",
      sampleRef: "sample_1",
      sampleKey: "display-row-0",
    })).toThrowError("SELECTION_SAMPLE_IDENTITY_INVALID");
    expect(() => new WorkspaceSelectionStore(snapshot.workspace, mutate(selection, { datasetVersion: "v2" }))).toThrowError("SELECTION_STALE_DATASET_VERSION");
  });

  it("binds a coordination site to exact structure and Artifact identities", () => {
    const snapshot = workspaceSnapshotFixture();
    const artifact: Artifact = { id: "artifact_coord", artifactId: "artifact_coord", jobId: snapshot.workspace.sourceJobId, type: "table_json", version: "1", name: "coordination.json", sizeBytes: 10, sha256: HASH, metadata: { projectId: snapshot.workspace.projectId } };
    const selection = coordinationSiteSelection(snapshot.workspace, artifact, { sourceResourceId: "resource_1", structureHash: HASH, siteId: `site:${HASH}:0` });
    expect(selection).toMatchObject({ primary: { kind: "PERIODIC_SITE", objectId: "resource_1", structureId: HASH, siteId: `site:${HASH}:0`, artifactId: "artifact_coord", artifactChecksum: HASH } });
    expect(() => coordinationSiteSelection(snapshot.workspace, artifact, { sourceResourceId: "", structureHash: HASH, siteId: `site:${HASH}:0` })).toThrowError("SELECTION_COORDINATION_IDENTITY_INVALID");
  });

  it("constructs exact grounded evidence and claim identities without display-label authority", () => {
    const snapshot = workspaceSnapshotFixture();
    const interpretation = {
      schemaVersion: "1.0" as const, interpretationId: "interpretation_demo", interpretationHash: HASH,
      sourceBundleId: "bundle_demo", sourceBundleHash: HASH, sourceJobId: "job_demo", sourcePlanId: "plan_demo", sourcePlanHash: HASH,
      mode: "DETERMINISTIC" as const, provider: "deterministic", providerVersion: "1.0", globalWarnings: [], globalLimitations: [], recommendations: [],
      completeness: "COMPLETE" as const, partialResultState: false, repairCount: 0 as const, validationOutcome: "VALID", executionRecordId: "execution_demo",
      claims: [{ schemaVersion: "1.0" as const, claimId: "claim_demo", claimType: "OBSERVATION" as const, subjectEvidenceIds: ["evidence_demo"], supportingEvidenceIds: ["evidence_demo"], limitingEvidenceIds: [], contradictingEvidenceIds: [], semanticPredicate: "HAS_VALUE", qualifiers: [], renderedText: "Exact value reported.", scope: "artifact", confidenceClass: "DIRECT" as const, groundingStatus: "GROUNDED" as const, displayOrder: 0 }],
    };
    const evidence = { interpretationId: "interpretation_demo", bundleId: "bundle_demo", bundleHash: HASH, sourceArtifactIds: ["artifact_demo"], bundleWarnings: [], bundleLimitations: [], evidenceItems: [{ schemaVersion: "1.0" as const, evidenceItemId: "evidence_demo", semanticRole: "metric.value", evidenceKind: "SCALAR" as const, subjectId: "artifact_demo", displayValue: "2", unit: null, sourceArtifactId: "artifact_demo", sourceArtifactChecksum: HASH, artifactContract: "platform.dataset.summary", artifactContractVersion: "1.0", sourceToolId: "tool.demo", sourceToolVersion: "1.0", fieldLocator: { fieldId: "metrics.value" }, warnings: [], limitations: [] }] };
    const evidenceSelection = evidenceItemSelection(snapshot.workspace, interpretation, evidence, evidence.evidenceItems[0]);
    const selectedClaim = claimSelection(snapshot.workspace, interpretation, interpretation.claims[0]);
    expect(evidenceSelection.primary).toMatchObject({ kind: "EVIDENCE_ITEM", evidenceItemId: "evidence_demo", sourceArtifactId: "artifact_demo", fieldLocator: "metrics.value" });
    expect(selectedClaim.primary).toMatchObject({ kind: "CLAIM", interpretationId: "interpretation_demo", claimId: "claim_demo" });
    expect(resolvePanelSelection(snapshot.panels.find((panel) => panel.panelKind === "EVIDENCE")!, evidenceSelection, snapshot.workspace)).toMatchObject({ compatibility: "EXACT" });
    expect(() => evidenceItemSelection(snapshot.workspace, interpretation, { ...evidence, sourceArtifactIds: [] }, evidence.evidenceItems[0])).toThrowError("SELECTION_EVIDENCE_SCOPE_MISMATCH");
  });

  it("bounds 32 subscribers, rapid changes, replay suppression, and cleanup", () => {
    const snapshot = workspaceSnapshotFixture();
    const store = new WorkspaceSelectionStore(snapshot.workspace);
    const receivers = Array.from({ length: 32 }, () => vi.fn());
    const unsubscribers = receivers.map((receive, index) => store.subscribe(
      declared({ ...snapshot.panels[0], panelId: `panel_subscriber_${index}` }, ["DATASET_SAMPLE"], []),
      receive,
    ));
    expect(() => store.subscribe(
      declared({ ...snapshot.panels[0], panelId: "panel_subscriber_33" }, ["DATASET_SAMPLE"], []),
      vi.fn(),
    )).toThrowError("SELECTION_SUBSCRIBER_CAP_EXCEEDED");

    for (let index = 0; index < 100; index += 1) {
      store.set(mutate(datasetSelection(), { objectId: `object_${index}`, sampleRef: `sample_${index}` }), "panel_source");
    }
    store.set(mutate(datasetSelection(), { objectId: "object_99", sampleRef: "sample_99" }), "panel_source");
    expect(receivers.every((receive) => receive.mock.calls.length === 101)).toBe(true);

    unsubscribers.forEach((unsubscribe) => unsubscribe());
    store.clear("panel_source");
    expect(receivers.every((receive) => receive.mock.calls.length === 101)).toBe(true);
  });
});

function datasetSelection() {
  return validateWorkspaceSelectionContext({
    schemaVersion: "1.0", sourceScopeHash: HASH,
    primary: {
      selectionSchemaVersion: "1.0", kind: "DATASET_SAMPLE", sourceScopeHash: HASH,
      projectId: "project_demo", datasetId: "dataset_demo", datasetVersion: "v1",
      objectId: "object_1", sampleRef: "sample_1",
    },
    secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false,
  });
}

function declared(panel: WorkspacePanel, acceptedSelectionKinds: WorkspacePanel["acceptedSelectionKinds"], emittedSelectionKinds: WorkspacePanel["emittedSelectionKinds"]): WorkspacePanel {
  return { ...panel, acceptedSelectionKinds, emittedSelectionKinds };
}

function mutate(value: ReturnType<typeof datasetSelection>, changes: Record<string, string>) {
  return validateWorkspaceSelectionContext({ ...value, primary: { ...value.primary!, ...changes } });
}
