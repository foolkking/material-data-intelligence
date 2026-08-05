import { describe, expect, it } from "vitest";

import { workspaceSnapshotFixture } from "./workspace-test-fixture";
import {
  durableDraftFromWorkspace,
  workspaceDraftIsDirty,
  workspaceNeedsObservation,
  workspacePatchForDraft,
} from "./workspace-recovery-model";

describe("Phase 10M-6 Workspace recovery model", () => {
  it("compares only approved durable fields and suppresses no-op saves", () => {
    const base = durableDraftFromWorkspace(workspaceSnapshotFixture().workspace);
    expect(workspaceDraftIsDirty(base, base)).toBe(false);
    expect(workspacePatchForDraft(base, base)).toBeNull();
  });

  it("creates a bounded patch without source or transient state", () => {
    const base = durableDraftFromWorkspace(workspaceSnapshotFixture().workspace);
    const draft = { title: "Updated title", activePanelId: "panel_results" };
    expect(workspaceDraftIsDirty(draft, base)).toBe(true);
    expect(workspacePatchForDraft(draft, base)).toEqual({
      title: "Updated title",
      activePanelId: "panel_results",
    });
  });

  it("observes only nonterminal persisted Job projections", () => {
    expect(workspaceNeedsObservation(workspaceSnapshotFixture("RUNNING"))).toBe(true);
    expect(workspaceNeedsObservation(workspaceSnapshotFixture("INITIALIZING"))).toBe(true);
    expect(workspaceNeedsObservation(workspaceSnapshotFixture("COMPLETE"))).toBe(false);
    expect(workspaceNeedsObservation(workspaceSnapshotFixture("PARTIAL_RESULTS"))).toBe(false);
  });
});
