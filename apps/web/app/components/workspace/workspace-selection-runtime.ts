import type {
  ScientificWorkspace,
  WorkspacePanel,
  WorkspaceSelectionContext,
  WorkspaceSelectionKind,
} from "../../lib/workspace-api";
import type {
  Artifact,
  GroundedScientificInterpretation,
  InterpretationEvidenceResponse,
  ScientificClaim,
  ScientificEvidenceItem,
} from "../../lib/planner-api";
import { artifactChecksum, artifactIdentity, artifactVersion } from "./workspace-renderer-registry";
import {
  clearedWorkspaceSelection,
  selectionsEqual,
  validateWorkspaceSelectionContext,
} from "./workspace-selection-contract";

export type WorkspaceSelectionCompatibilityCode =
  | "EXACT"
  | "NOT_APPLICABLE"
  | "STALE"
  | "UNSUPPORTED";

export type WorkspaceSelectionDelivery = Readonly<{
  panelId: string;
  originPanelId: string | null;
  context: WorkspaceSelectionContext | null;
  compatibility: WorkspaceSelectionCompatibilityCode;
  reason: string;
  transaction: number;
}>;

type Subscriber = Readonly<{
  panel: WorkspacePanel;
  receive: (delivery: WorkspaceSelectionDelivery) => void;
}>;

export class WorkspaceSelectionStore {
  readonly workspaceId: string;
  private context: WorkspaceSelectionContext | null;
  private originPanelId: string | null = null;
  private transaction = 0;
  private subscribers = new Map<string, Subscriber>();

  constructor(private readonly workspace: ScientificWorkspace, initial: WorkspaceSelectionContext | null = null) {
    this.workspaceId = workspace.workspaceId;
    this.context = initial ? this.validateScope(initial) : null;
  }

  current(): WorkspaceSelectionContext | null { return this.context; }

  subscribe(panel: WorkspacePanel, receive: Subscriber["receive"]): () => void {
    if (panel.workspaceId !== this.workspaceId) throw new Error("SELECTION_SUBSCRIBER_WORKSPACE_MISMATCH");
    if (this.subscribers.size >= 32 && !this.subscribers.has(panel.panelId)) throw new Error("SELECTION_SUBSCRIBER_CAP_EXCEEDED");
    this.subscribers.set(panel.panelId, { panel, receive });
    receive(resolvePanelSelection(panel, this.context, this.workspace, this.transaction, this.originPanelId));
    return () => { this.subscribers.delete(panel.panelId); };
  }

  set(next: WorkspaceSelectionContext, originPanelId: string | null = null): WorkspaceSelectionContext {
    const validated = this.validateScope(next);
    if (selectionsEqual(this.context, validated)) return validated;
    this.context = validated;
    this.originPanelId = originPanelId;
    this.transaction += 1;
    for (const subscriber of this.subscribers.values()) {
      subscriber.receive(resolvePanelSelection(subscriber.panel, validated, this.workspace, this.transaction, originPanelId));
    }
    return validated;
  }

  clear(originPanelId: string | null = null): WorkspaceSelectionContext {
    return this.set(clearedWorkspaceSelection(this.workspace.sourceReferenceHash), originPanelId);
  }

  private validateScope(value: WorkspaceSelectionContext): WorkspaceSelectionContext {
    const context = validateWorkspaceSelectionContext(value);
    if (context.sourceScopeHash !== this.workspace.sourceReferenceHash) throw new Error("SELECTION_STALE_SOURCE_SCOPE");
    const refs = context.primary ? [context.primary, ...context.secondary] : [];
    if (refs.some((ref) => ref.projectId !== this.workspace.projectId)) throw new Error("SELECTION_FOREIGN_PROJECT");
    if (refs.some((ref) => ref.jobId !== null && ref.jobId !== this.workspace.sourceJobId)) throw new Error("SELECTION_FOREIGN_JOB");
    if (refs.some((ref) => ref.datasetId !== null && ref.datasetId !== this.workspace.datasetId)) throw new Error("SELECTION_FOREIGN_DATASET");
    if (refs.some((ref) => ref.datasetVersion !== null && ref.datasetVersion !== this.workspace.datasetVersion)) throw new Error("SELECTION_STALE_DATASET_VERSION");
    return context;
  }
}

export function resolvePanelSelection(
  panel: WorkspacePanel,
  context: WorkspaceSelectionContext | null,
  workspace: ScientificWorkspace,
  transaction = 0,
  originPanelId: string | null = null,
): WorkspaceSelectionDelivery {
  if (!context || context.cleared || !context.primary) return delivery(panel, null, "NOT_APPLICABLE", "No active canonical selection.", transaction, originPanelId);
  if (context.sourceScopeHash !== workspace.sourceReferenceHash || context.primary.projectId !== workspace.projectId) {
    return delivery(panel, null, "STALE", "Selection source scope does not match this Workspace.", transaction, originPanelId);
  }
  if (["STALE", "SOURCE_DELETED"].includes(panel.state)) return delivery(panel, null, "STALE", "Panel source is stale or deleted.", transaction, originPanelId);
  if (["CONTRACT_UNSUPPORTED", "PROFILE_AUTHORITY_UNAVAILABLE"].includes(panel.state)) return delivery(panel, null, "UNSUPPORTED", "Panel source contract cannot accept canonical selection.", transaction, originPanelId);
  if (!panel.acceptedSelectionKinds.includes(context.primary.kind)) return delivery(panel, null, "NOT_APPLICABLE", `Panel does not declare ${context.primary.kind}.`, transaction, originPanelId);
  if (!panelSourceCompatible(panel, context, workspace)) return delivery(panel, null, "NOT_APPLICABLE", "Selection identity does not match this panel's exact source references.", transaction, originPanelId);
  return delivery(panel, { ...context, compatibility: "EXACT" }, "EXACT", "Exact kind and source scope match.", transaction, originPanelId);
}

export function panelCanEmit(panel: WorkspacePanel, kind: WorkspaceSelectionKind): boolean {
  return panel.emittedSelectionKinds.includes(kind) && !["CONTRACT_UNSUPPORTED", "SOURCE_DELETED", "STALE"].includes(panel.state);
}

export function artifactSelectionFromPanel(
  panel: WorkspacePanel,
  workspace: ScientificWorkspace,
): WorkspaceSelectionContext | null {
  if (!panelCanEmit(panel, "ARTIFACT")) return null;
  const sources = panel.sourceRefs.filter((source) => source.kind === "ARTIFACT");
  if (sources.length !== 1) return null;
  const source = sources[0];
  if (!source.sourceHash || !source.contract || !source.contractVersion || source.projectId !== workspace.projectId || source.jobId !== workspace.sourceJobId) return null;
  return validateWorkspaceSelectionContext({
    schemaVersion: "1.0",
    sourceScopeHash: workspace.sourceReferenceHash,
    primary: {
      selectionSchemaVersion: "1.0",
      kind: "ARTIFACT",
      sourceScopeHash: workspace.sourceReferenceHash,
      projectId: workspace.projectId,
      jobId: workspace.sourceJobId,
      artifactId: source.sourceId,
      artifactChecksum: source.sourceHash,
      artifactContract: source.contract,
      artifactVersion: source.contractVersion,
      toolCallId: source.toolCallId,
    },
    secondary: [],
    propagation: "EXACT_COMPATIBLE_ONLY",
    compatibility: "EXACT",
    cleared: false,
  });
}

export function artifactSelectionFromArtifact(
  artifact: Artifact,
  workspace: ScientificWorkspace,
): WorkspaceSelectionContext | null {
  const artifactId = artifactIdentity(artifact);
  const checksum = artifactChecksum(artifact);
  if (!artifactId || !checksum || !artifact.type || artifact.jobId !== workspace.sourceJobId) return null;
  const projectId = typeof artifact.metadata?.projectId === "string" ? artifact.metadata.projectId : workspace.projectId;
  if (projectId !== workspace.projectId) return null;
  return validateWorkspaceSelectionContext({
    schemaVersion: "1.0",
    sourceScopeHash: workspace.sourceReferenceHash,
    primary: {
      selectionSchemaVersion: "1.0",
      kind: "ARTIFACT",
      sourceScopeHash: workspace.sourceReferenceHash,
      projectId: workspace.projectId,
      jobId: workspace.sourceJobId,
      artifactId,
      artifactChecksum: checksum,
      artifactContract: artifact.type,
      artifactVersion: artifactVersion(artifact),
      toolCallId: artifact.toolCallId ?? null,
    },
    secondary: [],
    propagation: "EXACT_COMPATIBLE_ONLY",
    compatibility: "EXACT",
    cleared: false,
  });
}

export function datasetSampleSelection(
  workspace: ScientificWorkspace,
  identity: Readonly<{ objectId: string; sampleRef: string; sampleKey: string }>,
): WorkspaceSelectionContext {
  if (!identity.objectId || !identity.sampleRef || identity.sampleKey !== `${identity.objectId}:${identity.sampleRef}`) throw new Error("SELECTION_SAMPLE_IDENTITY_INVALID");
  if (!workspace.datasetId || !workspace.datasetVersion) throw new Error("SELECTION_DATASET_SCOPE_UNAVAILABLE");
  return validateWorkspaceSelectionContext({
    schemaVersion: "1.0",
    sourceScopeHash: workspace.sourceReferenceHash,
    primary: {
      selectionSchemaVersion: "1.0",
      kind: "DATASET_SAMPLE",
      sourceScopeHash: workspace.sourceReferenceHash,
      projectId: workspace.projectId,
      datasetId: workspace.datasetId,
      datasetVersion: workspace.datasetVersion,
      objectId: identity.objectId,
      sampleRef: identity.sampleRef,
    },
    secondary: [],
    propagation: "EXACT_COMPATIBLE_ONLY",
    compatibility: "EXACT",
    cleared: false,
  });
}

export function evidenceItemSelection(
  workspace: ScientificWorkspace,
  interpretation: GroundedScientificInterpretation,
  evidence: InterpretationEvidenceResponse,
  item: ScientificEvidenceItem,
): WorkspaceSelectionContext {
  if (
    interpretation.sourceJobId !== workspace.sourceJobId
    || interpretation.sourceBundleId !== evidence.bundleId
    || interpretation.sourceBundleHash !== evidence.bundleHash
    || evidence.interpretationId !== interpretation.interpretationId
    || !evidence.sourceArtifactIds.includes(item.sourceArtifactId)
  ) throw new Error("SELECTION_EVIDENCE_SCOPE_MISMATCH");
  return validateWorkspaceSelectionContext({
    schemaVersion: "1.0",
    sourceScopeHash: workspace.sourceReferenceHash,
    primary: {
      selectionSchemaVersion: "1.0",
      kind: "EVIDENCE_ITEM",
      sourceScopeHash: workspace.sourceReferenceHash,
      projectId: workspace.projectId,
      jobId: workspace.sourceJobId,
      bundleId: evidence.bundleId,
      bundleHash: evidence.bundleHash,
      evidenceItemId: item.evidenceItemId,
      sourceArtifactId: item.sourceArtifactId,
      sourceArtifactChecksum: item.sourceArtifactChecksum,
      fieldLocator: item.fieldLocator.fieldId,
    },
    secondary: [],
    propagation: "EXACT_COMPATIBLE_ONLY",
    compatibility: "EXACT",
    cleared: false,
  });
}

export function claimSelection(
  workspace: ScientificWorkspace,
  interpretation: GroundedScientificInterpretation,
  claim: ScientificClaim,
): WorkspaceSelectionContext {
  if (interpretation.sourceJobId !== workspace.sourceJobId || !interpretation.claims.some((item) => item.claimId === claim.claimId)) {
    throw new Error("SELECTION_CLAIM_SCOPE_MISMATCH");
  }
  return validateWorkspaceSelectionContext({
    schemaVersion: "1.0",
    sourceScopeHash: workspace.sourceReferenceHash,
    primary: {
      selectionSchemaVersion: "1.0",
      kind: "CLAIM",
      sourceScopeHash: workspace.sourceReferenceHash,
      projectId: workspace.projectId,
      jobId: workspace.sourceJobId,
      interpretationId: interpretation.interpretationId,
      interpretationHash: interpretation.interpretationHash,
      claimId: claim.claimId,
    },
    secondary: [],
    propagation: "EXACT_COMPATIBLE_ONLY",
    compatibility: "EXACT",
    cleared: false,
  });
}

function panelSourceCompatible(panel: WorkspacePanel, context: WorkspaceSelectionContext, workspace: ScientificWorkspace): boolean {
  const selected = context.primary;
  if (!selected) return false;
  if (["OVERVIEW", "DATA", "PLAN", "EXECUTION", "PROVENANCE", "REPORT"].includes(panel.panelKind)) return true;
  if (selected.kind === "CLAIM") {
    return panel.sourceRefs.some((source) => source.kind === "INTERPRETATION" && source.sourceId === selected.interpretationId && source.sourceHash === selected.interpretationHash);
  }
  if (selected.kind === "EVIDENCE_ITEM") {
    return panel.sourceRefs.some((source) =>
      (source.kind === "EVIDENCE_BUNDLE" && source.sourceId === selected.bundleId && source.sourceHash === selected.bundleHash)
      || (source.kind === "ARTIFACT" && source.sourceId === selected.sourceArtifactId && source.sourceHash === selected.sourceArtifactChecksum),
    );
  }
  const artifactId = selected.kind === "ARTIFACT" ? selected.artifactId
    : selected.kind === "PHONON_Q_POINT" || selected.kind === "PHONON_BRANCH" ? selected.phononArtifactId
      : selected.kind === "RECIPROCAL_POINT" ? selected.reciprocalArtifactId
        : selected.kind === "VOLUMETRIC_FIELD" ? selected.artifactId : null;
  const checksum = "artifactChecksum" in selected ? selected.artifactChecksum : null;
  if (artifactId) return panel.sourceRefs.some((source) => source.kind === "ARTIFACT" && source.sourceId === artifactId && source.sourceHash === checksum && source.jobId === workspace.sourceJobId);
  if (selected.kind === "DATASET_SAMPLE" || selected.kind === "MATERIAL_OBJECT") {
    return ["DATA", "SCIENTIFIC_RESULT"].includes(panel.panelKind)
      && selected.datasetId === workspace.datasetId
      && selected.datasetVersion === workspace.datasetVersion;
  }
  return panel.panelKind === "DATA";
}

function delivery(panel: WorkspacePanel, context: WorkspaceSelectionContext | null, compatibility: WorkspaceSelectionCompatibilityCode, reason: string, transaction: number, originPanelId: string | null): WorkspaceSelectionDelivery {
  return Object.freeze({ panelId: panel.panelId, originPanelId, context, compatibility, reason, transaction });
}
