import type { WorkspacePanel, WorkspacePanelKind, WorkspaceSnapshot } from "../../lib/workspace-api";

const HASH = "a".repeat(64);

export function workspaceSnapshotFixture(status: WorkspaceSnapshot["workspace"]["projectedStatus"] = "COMPLETE"): WorkspaceSnapshot {
  const workspaceId = "workspace_demo";
  const panels = [
    panel(workspaceId, "panel_overview", "OVERVIEW", "Analysis overview", 0),
    panel(workspaceId, "panel_data", "DATA", "Dataset context", 1),
    panel(workspaceId, "panel_results", "SCIENTIFIC_RESULT", "Scientific results", 2),
    panel(workspaceId, "panel_findings", "FINDINGS", "Grounded findings", 3),
    panel(workspaceId, "panel_evidence", "EVIDENCE", "Evidence", 4),
    panel(workspaceId, "panel_provenance", "PROVENANCE", "Provenance", 5),
    panel(workspaceId, "panel_report", "REPORT", "Report", 6),
  ];
  return {
    workspace: {
      schemaVersion: "1.0",
      workspaceId,
      projectId: "project_demo",
      sourceJobId: "job_demo",
      sourceReferenceHash: HASH,
      datasetId: "dataset_demo",
      datasetVersion: "v1",
      profileId: "profile_demo",
      profileSemanticHash: HASH,
      intentId: "intent_demo",
      intentSemanticHash: HASH,
      planId: "plan_demo",
      planHash: HASH,
      planSchemaVersion: "0.2",
      title: "Formation energy analysis",
      activePanelId: "panel_overview",
      pinnedSelection: null,
      durableMetadata: { tags: [], note: null },
      panelIds: panels.map((item) => item.panelId),
      currentLayoutRevision: 1,
      revision: 1,
      projectedStatus: status,
      historicalProjection: status === "LEGACY_READ_ONLY",
      readOnly: status === "LEGACY_READ_ONLY" || status === "STALE",
      warnings: [],
      diagnostics: [],
      artifactCount: 2,
      toolCallCount: 2,
      interpretationCount: 1,
      reportCount: 0,
      recipeCount: 0,
      createdByKind: "USER",
      createdBy: "fixture",
      createdAt: "2026-08-01T00:00:00Z",
      updatedAt: "2026-08-01T00:00:00Z",
      executionAuthorized: false,
      scientificAuthority: false,
    },
    panels,
    currentLayoutRevision: {
      schemaVersion: "1.0",
      workspaceId,
      revision: 1,
      layout: {
        schemaVersion: "1.0",
        activePanelId: "panel_overview",
        panelOrder: panels.map((item) => item.panelId),
        visiblePanelIds: panels.map((item) => item.panelId),
        panelLayouts: panels.map((item) => ({ panelId: item.panelId, ...item.layout })),
        durableMetadata: { tags: [], note: null },
      },
      selection: null,
      semanticHash: HASH,
      createdBy: "fixture",
      createdAt: "2026-08-01T00:00:00Z",
    },
    sourceSummary: {
      jobStatus: status === "RUNNING" ? "running" : status === "FAILED" ? "failed" : "completed",
      analysisPlanSchemaVersion: "0.2",
      dependencyOutcome: status === "PARTIAL_RESULTS" ? "PARTIAL_RESULTS" : "ALL_SUCCEEDED",
      artifactCount: 2,
      toolCallCount: 2,
      interpretationCount: 1,
      reportCount: 0,
      recipeCount: 0,
      metadataOnly: true,
    },
    projectionHash: HASH,
  };
}

function panel(workspaceId: string, panelId: string, panelKind: WorkspacePanelKind, title: string, ordinal: number): WorkspacePanel {
  const declarations: Record<WorkspacePanelKind, [WorkspacePanel["acceptedSelectionKinds"], WorkspacePanel["emittedSelectionKinds"]]> = {
    OVERVIEW: [["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME", "PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []],
    DATA: [["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME"], []],
    PLAN: [[], []],
    EXECUTION: [["ARTIFACT"], []],
    SCIENTIFIC_RESULT: [["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME", "PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT"], ["DATASET_SAMPLE", "MATERIAL_OBJECT", "ARTIFACT"]],
    FINDINGS: [["PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []],
    EVIDENCE: [["PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []],
    PROVENANCE: [["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME", "PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []],
    REPORT: [["ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []],
  };
  const renderer: Record<WorkspacePanelKind, string> = {
    OVERVIEW: "workspace.overview/1.0", DATA: "workspace.data/1.0", PLAN: "workspace.plan/1.0",
    EXECUTION: "workspace.execution/1.0", SCIENTIFIC_RESULT: "workspace.artifact-metadata/1.0",
    FINDINGS: "workspace.findings/1.0", EVIDENCE: "workspace.evidence/1.0",
    PROVENANCE: "workspace.provenance/1.0", REPORT: "workspace.report/1.0",
  };
  const source = panelKind === "SCIENTIFIC_RESULT" ? {
    kind: "ARTIFACT" as const, sourceId: "artifact_demo", sourceHash: HASH,
    contract: "platform.dataset.summary", contractVersion: "1.0", mediaType: "application/json",
    projectId: "project_demo", jobId: "job_demo", toolCallId: "tool_call_demo", stepId: "step_demo",
  } : panelKind === "FINDINGS" ? {
    kind: "INTERPRETATION" as const, sourceId: "interpretation_demo", sourceHash: HASH,
    contract: "grounded_interpretation", contractVersion: "1.0", mediaType: null,
    projectId: "project_demo", jobId: "job_demo", toolCallId: null, stepId: null,
  } : panelKind === "EVIDENCE" ? {
    kind: "EVIDENCE_BUNDLE" as const, sourceId: "bundle_demo", sourceHash: HASH,
    contract: "scientific_evidence_bundle", contractVersion: "1.0", mediaType: null,
    projectId: "project_demo", jobId: "job_demo", toolCallId: null, stepId: null,
  } : {
    kind: "JOB" as const, sourceId: "job_demo", sourceHash: HASH, contract: null,
    contractVersion: null, mediaType: null, projectId: "project_demo", jobId: "job_demo",
    toolCallId: null, stepId: null,
  };
  const artifactSource = {
    kind: "ARTIFACT" as const, sourceId: "artifact_demo", sourceHash: HASH,
    contract: "platform.dataset.summary", contractVersion: "1.0", mediaType: "application/json",
    projectId: "project_demo", jobId: "job_demo", toolCallId: "tool_call_demo", stepId: "step_demo",
  };
  const sourceRefs = panelKind === "EVIDENCE" || panelKind === "FINDINGS"
    ? [source, artifactSource]
    : [source];
  return {
    schemaVersion: "1.0",
    panelId,
    workspaceId,
    panelKind,
    title,
    ordinal,
    visible: true,
    sourceRefs,
    sourceReferenceHash: HASH,
    rendererContract: renderer[panelKind],
    state: "PRODUCED",
    acceptedSelectionKinds: declarations[panelKind][0],
    emittedSelectionKinds: declarations[panelKind][1],
    evidenceRefs: panelKind === "EVIDENCE" ? ["evidence_demo"] : [],
    provenanceRefs: ["job_demo"],
    capabilityRequirement: null,
    layout: { region: "PRIMARY", order: ordinal, width: 1, height: 1, collapsed: false },
    mobilePresentationMode: "FULL_WIDTH",
    accessibleName: title,
    unsupportedReason: null,
    panelStateHash: HASH,
    contractProvenance: "phase10m1.workspace_projection.v1",
  };
}
