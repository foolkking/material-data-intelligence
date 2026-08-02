import type {
  ScientificWorkspace,
  WorkspacePanel,
  WorkspacePanelKind,
  WorkspacePanelState,
  WorkspaceSnapshot,
  WorkspaceStatus,
} from "../../lib/workspace-api";

export type WorkspaceNavigationGroup = {
  id: string;
  label: string;
  panelKind: WorkspacePanelKind;
};

export const WORKSPACE_NAVIGATION_GROUPS: readonly WorkspaceNavigationGroup[] = Object.freeze([
  { id: "overview", label: "Overview", panelKind: "OVERVIEW" },
  { id: "data", label: "Data", panelKind: "DATA" },
  { id: "plan", label: "Plan", panelKind: "PLAN" },
  { id: "execution", label: "Execution", panelKind: "EXECUTION" },
  { id: "results", label: "Results", panelKind: "SCIENTIFIC_RESULT" },
  { id: "findings", label: "Findings", panelKind: "FINDINGS" },
  { id: "evidence", label: "Evidence", panelKind: "EVIDENCE" },
  { id: "provenance", label: "Provenance", panelKind: "PROVENANCE" },
  { id: "report", label: "Report", panelKind: "REPORT" },
]);

const PANEL_STATE_COPY: Record<WorkspacePanelState, string> = {
  NOT_APPLICABLE: "Not applicable to this source",
  READY_NOT_RUN: "Available when the source operation completes",
  LOADING: "Source work is still running",
  PRODUCED: "Source metadata is available",
  PARTIAL: "Partial source results are available",
  UNAVAILABLE: "Source metadata is unavailable",
  FAILED: "The source operation failed",
  BLOCKED_BY_DEPENDENCY: "Blocked by a failed dependency",
  STALE: "Bound to an exact historical source version",
  CAP_EXCEEDED: "Source metadata exceeds the bounded contract",
  CONTRACT_UNSUPPORTED: "The source contract is not supported",
  SOURCE_DELETED: "The exact source is no longer available",
  PROFILE_AUTHORITY_UNAVAILABLE: "Profile authority is unavailable",
};

const WORKSPACE_STATUS_COPY: Record<WorkspaceStatus, string> = {
  SOURCE_MISSING: "One or more exact sources are missing",
  UNSUPPORTED: "This historical source is read-only and unsupported",
  LEGACY_READ_ONLY: "Historical source opened in read-only mode",
  STALE: "Workspace remains bound to its exact historical source",
  RUNNING: "Analysis is still running",
  PARTIAL_RESULTS: "Some branches completed and some did not",
  COMPLETE: "Analysis completed",
  FAILED: "Analysis did not complete",
  READY: "Workspace is ready",
  INITIALIZING: "Workspace is initializing",
};

export function orderedVisiblePanels(snapshot: WorkspaceSnapshot): WorkspacePanel[] {
  const visible = snapshot.panels.filter((panel) => panel.visible);
  return [...visible].sort((left, right) => left.ordinal - right.ordinal || left.panelId.localeCompare(right.panelId));
}

export function panelForRequestedId(snapshot: WorkspaceSnapshot, requestedPanelId: string | null): WorkspacePanel | null {
  const visible = orderedVisiblePanels(snapshot);
  if (requestedPanelId) {
    return visible.find((panel) => panel.panelId === requestedPanelId) || null;
  }
  const persisted = snapshot.currentLayoutRevision?.layout.activePanelId || snapshot.workspace.activePanelId;
  return visible.find((panel) => panel.panelId === persisted) || visible[0] || null;
}

export function firstPanelForKind(snapshot: WorkspaceSnapshot, kind: WorkspacePanelKind): WorkspacePanel | null {
  return orderedVisiblePanels(snapshot).find((panel) => panel.panelKind === kind) || null;
}

export function panelStateCopy(state: WorkspacePanelState): string {
  return PANEL_STATE_COPY[state];
}

export function workspaceStatusCopy(status: WorkspaceStatus): string {
  return WORKSPACE_STATUS_COPY[status];
}

export function workspaceGoalSummary(workspace: ScientificWorkspace): string {
  if (workspace.intentId) return `Intent ${compactIdentity(workspace.intentId)}`;
  if (workspace.planId) return `Plan ${compactIdentity(workspace.planId)}`;
  return "Historical analysis source";
}

export function compactIdentity(value: string | null, max = 24): string {
  if (!value) return "Not available";
  if (value.length <= max) return value;
  const side = Math.max(4, Math.floor((max - 3) / 2));
  return `${value.slice(0, side)}...${value.slice(-side)}`;
}

export function panelStateTone(state: WorkspacePanelState): "success" | "warning" | "danger" | "neutral" {
  if (state === "PRODUCED") return "success";
  if (["PARTIAL", "STALE", "READY_NOT_RUN", "PROFILE_AUTHORITY_UNAVAILABLE"].includes(state)) return "warning";
  if (["FAILED", "BLOCKED_BY_DEPENDENCY", "SOURCE_DELETED", "CAP_EXCEEDED"].includes(state)) return "danger";
  return "neutral";
}

export function workspaceStatusTone(status: WorkspaceStatus): "success" | "warning" | "danger" | "neutral" {
  if (["COMPLETE", "READY"].includes(status)) return "success";
  if (["PARTIAL_RESULTS", "STALE", "LEGACY_READ_ONLY", "RUNNING", "INITIALIZING"].includes(status)) return "warning";
  if (["FAILED", "SOURCE_MISSING"].includes(status)) return "danger";
  return "neutral";
}
