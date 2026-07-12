import { describe, expect, it } from "vitest";

import { changeViewerSelectionMode, initialViewerSelection, selectViewerSite } from "./viewerSceneSelection";

describe("viewer selection state", () => {
  it("toggles inspect selection and clears on empty pick", () => {
    const selected = selectViewerSite(initialViewerSelection(), 7);
    expect(selected.activeSiteIndex).toBe(7);
    expect(selectViewerSite(selected, 7).selectedSiteIndices).toEqual([]);
    expect(selectViewerSite(selected, null).selectedSiteIndices).toEqual([]);
  });

  it("enforces measurement limits and resets on mode switch", () => {
    let state = changeViewerSelectionMode(initialViewerSelection(), "distance");
    state = selectViewerSite(state, 1);
    state = selectViewerSite(state, 2);
    state = selectViewerSite(state, 3);
    expect(state.selectedSiteIndices).toEqual([2, 3]);
    expect(changeViewerSelectionMode(state, "dihedral").selectedSiteIndices).toEqual([]);
  });

  it("ignores invalid site indices", () => expect(selectViewerSite(initialViewerSelection(), -1)).toEqual(initialViewerSelection()));
});
