import { describe, expect, it } from "vitest";

import { changeViewerSelectionMode, initialViewerSelection, selectViewerSite } from "./viewerSceneSelection";

const primary = (siteIndex: number) => ({ siteIndex, imageOffset: [0,0,0] as const });

describe("viewer selection state", () => {
  it("toggles inspect selection and clears on empty pick", () => {
    const selected = selectViewerSite(initialViewerSelection(), primary(7));
    expect(selected.activeSite).toEqual(primary(7));
    expect(selectViewerSite(selected, primary(7)).selectedSites).toEqual([]);
    expect(selectViewerSite(selected, null).selectedSites).toEqual([]);
  });

  it("enforces measurement limits and resets on mode switch", () => {
    let state = changeViewerSelectionMode(initialViewerSelection(), "distance");
    state = selectViewerSite(state, primary(1));
    state = selectViewerSite(state, primary(2));
    state = selectViewerSite(state, primary(3));
    expect(state.selectedSites).toEqual([primary(2), primary(3)]);
    expect(changeViewerSelectionMode(state, "dihedral").selectedSites).toEqual([]);
  });

  it("distinguishes replicas and ignores invalid refs", () => {
    const primarySelected = selectViewerSite(initialViewerSelection("distance"), primary(1));
    expect(selectViewerSite(primarySelected, {siteIndex:1,imageOffset:[1,0,0]}).selectedSites).toHaveLength(2);
    expect(selectViewerSite(initialViewerSelection(), {siteIndex:-1,imageOffset:[0,0,0]})).toEqual(initialViewerSelection());
  });
});
