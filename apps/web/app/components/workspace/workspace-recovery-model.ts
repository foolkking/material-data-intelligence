import type {
  ScientificWorkspace,
  WorkspacePatchRequest,
  WorkspaceSnapshot,
  WorkspaceStatus,
} from "../../lib/workspace-api";

export type WorkspaceDurableDraft = Readonly<{
  title: string;
  activePanelId: string | null;
}>;

const NONTERMINAL_STATUSES: ReadonlySet<WorkspaceStatus> = new Set([
  "INITIALIZING",
  "RUNNING",
]);

export function durableDraftFromWorkspace(workspace: ScientificWorkspace): WorkspaceDurableDraft {
  return Object.freeze({
    title: workspace.title,
    activePanelId: workspace.activePanelId,
  });
}

export function workspaceDraftIsDirty(
  draft: WorkspaceDurableDraft,
  base: WorkspaceDurableDraft,
): boolean {
  return draft.title !== base.title || draft.activePanelId !== base.activePanelId;
}

export function workspacePatchForDraft(
  draft: WorkspaceDurableDraft,
  base: WorkspaceDurableDraft,
): WorkspacePatchRequest | null {
  const patch: WorkspacePatchRequest = {};
  if (draft.title !== base.title) patch.title = draft.title;
  if (draft.activePanelId !== base.activePanelId) patch.activePanelId = draft.activePanelId;
  return Object.keys(patch).length ? patch : null;
}

export function workspaceNeedsObservation(snapshot: WorkspaceSnapshot): boolean {
  const jobStatus = snapshot.sourceSummary.jobStatus?.toLowerCase();
  return NONTERMINAL_STATUSES.has(snapshot.workspace.projectedStatus)
    || jobStatus === "created"
    || jobStatus === "queued"
    || jobStatus === "running";
}
