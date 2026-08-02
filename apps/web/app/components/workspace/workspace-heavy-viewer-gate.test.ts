import { describe, expect, it } from "vitest";

import { MAX_ACTIVE_HEAVY_VIEWERS, workspaceHeavyViewerLeases } from "./workspace-heavy-viewer-gate";

describe("Phase 10M-4 heavy viewer gate", () => {
  it("keeps one active owner across 50 mount/unmount cycles", () => {
    expect(MAX_ACTIVE_HEAVY_VIEWERS).toBe(1);
    for (let index = 0; index < 50; index += 1) {
      const owner = `workspace_demo:artifact_${index}`;
      const release = workspaceHeavyViewerLeases.acquire(owner);
      expect(release).not.toBeNull();
      expect(workspaceHeavyViewerLeases.snapshot()).toMatchObject({ activeOwner: owner, activeCount: 1, cap: 1 });
      expect(workspaceHeavyViewerLeases.acquire(`workspace_demo:parallel_${index}`)).toBeNull();
      release?.();
      expect(workspaceHeavyViewerLeases.snapshot()).toMatchObject({ activeOwner: null, activeCount: 0, cap: 1 });
    }
  });
});
