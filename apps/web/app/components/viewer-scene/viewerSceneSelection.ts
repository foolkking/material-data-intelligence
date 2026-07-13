import { periodicSiteKey } from "./viewerScenePeriodicGeometry";
import type { PeriodicSiteRef } from "./viewerSceneRendererTypes";

export type ViewerSelectionMode = "inspect" | "distance" | "angle" | "dihedral";

export type ViewerSelectionState = {
  readonly mode: ViewerSelectionMode;
  readonly selectedSites: readonly PeriodicSiteRef[];
  readonly activeSite: PeriodicSiteRef | null;
};

const MODE_LIMITS: Readonly<Record<ViewerSelectionMode, number>> = Object.freeze({
  inspect: 1,
  distance: 2,
  angle: 3,
  dihedral: 4,
});

export function initialViewerSelection(mode: ViewerSelectionMode = "inspect"): ViewerSelectionState {
  return Object.freeze({ mode, selectedSites: Object.freeze([]), activeSite: null });
}

export function selectViewerSite(state: ViewerSelectionState, site: PeriodicSiteRef | null): ViewerSelectionState {
  if (site === null) return initialViewerSelection(state.mode);
  let key: string;
  try { key = periodicSiteKey(site); } catch { return state; }
  const existing = state.selectedSites.findIndex((value) => periodicSiteKey(value) === key);
  const withoutExisting = existing >= 0 ? state.selectedSites.filter((value) => periodicSiteKey(value) !== key) : state.selectedSites;
  const next = existing >= 0
    ? withoutExisting
    : [...withoutExisting, Object.freeze({ siteIndex: site.siteIndex, imageOffset: Object.freeze([...site.imageOffset]) as PeriodicSiteRef["imageOffset"] })].slice(-MODE_LIMITS[state.mode]);
  return Object.freeze({ mode: state.mode, selectedSites: Object.freeze(next), activeSite: next.at(-1) ?? null });
}

export function changeViewerSelectionMode(_state: ViewerSelectionState, mode: ViewerSelectionMode): ViewerSelectionState {
  return initialViewerSelection(mode);
}

export function undoViewerSelection(state: ViewerSelectionState): ViewerSelectionState {
  const next = state.selectedSites.slice(0, -1);
  return Object.freeze({ mode: state.mode, selectedSites: Object.freeze(next), activeSite: next.at(-1) ?? null });
}

export function selectViewerBondEndpoints(state: ViewerSelectionState, from: PeriodicSiteRef, to: PeriodicSiteRef): ViewerSelectionState {
  if (state.mode === "inspect") return selectViewerSite(state, from);
  let next = state;
  for (const ref of [from, to]) {
    if (next.selectedSites.length >= MODE_LIMITS[state.mode]) break;
    if (!next.selectedSites.some((selected) => periodicSiteKey(selected) === periodicSiteKey(ref))) next = selectViewerSite(next, ref);
  }
  return next;
}

export function selectionLimit(mode: ViewerSelectionMode) {
  return MODE_LIMITS[mode];
}
