export type ViewerSelectionMode = "inspect" | "distance" | "angle" | "dihedral";

export type ViewerSelectionState = {
  readonly mode: ViewerSelectionMode;
  readonly selectedSiteIndices: readonly number[];
  readonly activeSiteIndex: number | null;
};

const MODE_LIMITS: Readonly<Record<ViewerSelectionMode, number>> = Object.freeze({
  inspect: 1,
  distance: 2,
  angle: 3,
  dihedral: 4,
});

export function initialViewerSelection(mode: ViewerSelectionMode = "inspect"): ViewerSelectionState {
  return Object.freeze({ mode, selectedSiteIndices: Object.freeze([]), activeSiteIndex: null });
}

export function selectViewerSite(state: ViewerSelectionState, siteIndex: number | null): ViewerSelectionState {
  if (siteIndex === null) return initialViewerSelection(state.mode);
  if (!Number.isInteger(siteIndex) || siteIndex < 0) return state;
  const existing = state.selectedSiteIndices.indexOf(siteIndex);
  const withoutExisting = existing >= 0 ? state.selectedSiteIndices.filter((value) => value !== siteIndex) : state.selectedSiteIndices;
  const next = existing >= 0
    ? withoutExisting
    : [...withoutExisting, siteIndex].slice(-MODE_LIMITS[state.mode]);
  return Object.freeze({ mode: state.mode, selectedSiteIndices: Object.freeze(next), activeSiteIndex: next.at(-1) ?? null });
}

export function changeViewerSelectionMode(_state: ViewerSelectionState, mode: ViewerSelectionMode): ViewerSelectionState {
  return initialViewerSelection(mode);
}

export function selectionLimit(mode: ViewerSelectionMode) {
  return MODE_LIMITS[mode];
}
