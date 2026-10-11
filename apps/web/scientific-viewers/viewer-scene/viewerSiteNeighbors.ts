import type { PeriodicSiteRef, RenderBond } from "./viewerSceneRendererTypes";

/** Translate saved endpoints to the selected image; never infer new bonds. */
export function savedSiteNeighbors(bonds: readonly RenderBond[], selected: PeriodicSiteRef) {
  return bonds.flatMap((bond) => {
    const incident = [
      { source: bond.fromRef, target: bond.toRef },
      { source: bond.toRef, target: bond.fromRef },
    ].filter(({ source }) => source.siteIndex === selected.siteIndex);
    return incident.map(({ source, target }) => ({
      bond,
      target: {
        siteIndex: target.siteIndex,
        imageOffset: [
          target.imageOffset[0] + selected.imageOffset[0] - source.imageOffset[0],
          target.imageOffset[1] + selected.imageOffset[1] - source.imageOffset[1],
          target.imageOffset[2] + selected.imageOffset[2] - source.imageOffset[2],
        ] as const,
      },
    }));
  }).sort((a, b) => a.target.siteIndex - b.target.siteIndex
    || a.target.imageOffset[0] - b.target.imageOffset[0]
    || a.target.imageOffset[1] - b.target.imageOffset[1]
    || a.target.imageOffset[2] - b.target.imageOffset[2]);
}

export function samePeriodicSite(a: PeriodicSiteRef, b: PeriodicSiteRef) {
  return a.siteIndex === b.siteIndex && a.imageOffset.every((value, axis) => value === b.imageOffset[axis]);
}
