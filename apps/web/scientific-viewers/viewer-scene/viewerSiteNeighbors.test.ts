import { describe, expect, it } from "vitest";
import { savedSiteNeighbors } from "./viewerSiteNeighbors";
import type { RenderBond } from "./viewerSceneRendererTypes";

const edge: RenderBond = {
  id: "saved-Li-O", fromSiteIndex: 0, toSiteIndex: 2,
  fromRef: { siteIndex: 0, imageOffset: [0, 0, 0] },
  toRef: { siteIndex: 2, imageOffset: [-1, 0, 0] },
  start: [0.796346, 0.910108, 1.524296], end: [-1.115347, 1.706452, 2.486005],
  displacementCartesian: [-1.911693, 0.796344, 0.961709], distanceAngstrom: 2.283335,
  source: "distance_cutoff", authoritative: false,
};

describe("saved periodic neighbors", () => {
  it("retains an out-of-cell endpoint and the saved distance without a rendered copy", () => {
    expect(savedSiteNeighbors([edge], { siteIndex: 0, imageOffset: [0, 0, 0] })).toEqual([
      { bond: edge, target: { siteIndex: 2, imageOffset: [-1, 0, 0] } },
    ]);
  });

  it("translates both forward and reverse incidence to the selected periodic image", () => {
    expect(savedSiteNeighbors([edge], { siteIndex: 0, imageOffset: [2, -1, 1] })[0].target)
      .toEqual({ siteIndex: 2, imageOffset: [1, -1, 1] });
    expect(savedSiteNeighbors([edge], { siteIndex: 2, imageOffset: [0, 0, 0] })[0].target)
      .toEqual({ siteIndex: 0, imageOffset: [1, 0, 0] });
    expect(edge.toRef.imageOffset).toEqual([-1, 0, 0]);
  });

  it("accounts for a saved nonzero source offset", () => {
    const shifted = { ...edge, fromRef: { siteIndex: 0, imageOffset: [2, 1, -1] as const }, toRef: { siteIndex: 2, imageOffset: [1, 1, -1] as const } };
    expect(savedSiteNeighbors([shifted], { siteIndex: 0, imageOffset: [0, 0, 0] })[0].target)
      .toEqual({ siteIndex: 2, imageOffset: [-1, 0, 0] });
  });

  it("keeps both neighbors of a recorded self-periodic edge", () => {
    const self = { ...edge, toSiteIndex: 0, toRef: { siteIndex: 0, imageOffset: [-1, 0, 0] as const } };
    expect(savedSiteNeighbors([self], { siteIndex: 0, imageOffset: [0, 0, 0] }).map(item => item.target.imageOffset))
      .toEqual([[-1, 0, 0], [1, 0, 0]]);
  });

  it("does not invent neighbors for unconnected sites", () => {
    expect(savedSiteNeighbors([edge], { siteIndex: 1, imageOffset: [0, 0, 0] })).toEqual([]);
  });
});
