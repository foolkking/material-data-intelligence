import { describe, expect, it } from "vitest";

import type { WorkspaceSnapshot } from "../../lib/workspace-api";
import { WORKSPACE_NAVIGATION_GROUPS, orderedVisiblePanels, panelForRequestedId } from "./workspace-shell-model";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";

describe("Phase 10M-2 Workspace shell model", () => {
  it("keeps the sealed nine-group information architecture", () => {
    expect(WORKSPACE_NAVIGATION_GROUPS.map((group) => group.label)).toEqual([
      "Overview", "Data", "Plan", "Execution", "Results", "Findings", "Evidence", "Provenance", "Report",
    ]);
  });

  it("orders visible panels by exact ordinal and stable panel identity", () => {
    const snapshot = workspaceSnapshotFixture();
    snapshot.panels = [snapshot.panels[2], snapshot.panels[0], snapshot.panels[1]];
    expect(orderedVisiblePanels(snapshot).map((panel) => panel.panelId)).toEqual(["panel_overview", "panel_data", "panel_results"]);
  });

  it("does not replace an unknown requested panel with a nearby panel", () => {
    const snapshot = workspaceSnapshotFixture();
    expect(panelForRequestedId(snapshot, "panel_invented")).toBeNull();
  });

  it("uses the exact persisted active panel only when no URL panel is requested", () => {
    const snapshot = workspaceSnapshotFixture() as WorkspaceSnapshot;
    snapshot.workspace.activePanelId = "panel_data";
    if (snapshot.currentLayoutRevision) snapshot.currentLayoutRevision.layout.activePanelId = "panel_data";
    expect(panelForRequestedId(snapshot, null)?.panelId).toBe("panel_data");
  });
});
