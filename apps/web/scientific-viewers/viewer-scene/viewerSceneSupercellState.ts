import type { ValidatedRenderScene } from "./viewerSceneRendererTypes";
import { estimatePeriodicSupercell, PERIODIC_DERIVED_CAPS, validSupercellRepeat, type SupercellRepeat } from "./viewerSceneSupercell";

export type ViewerSupercellSettings = Readonly<{ expansion: SupercellRepeat; originPolicy: "positive_octant"; showPrimaryCell: boolean; showSupercellBoundary: boolean; showInternalGrid: false }>;

export function buildViewerSupercellState(scene: ValidatedRenderScene, settings: ViewerSupercellSettings) {
  const estimate = estimatePeriodicSupercell(scene, settings.expansion);
  if (estimate.mode === "refused") throw new Error(estimate.error ?? "VIEWER_SUPERCELL_RENDER_BUDGET_EXCEEDED");
  const result = Object.freeze({
    schema_version: "phase10f24.viewer_supercell_state.v1" as const,
    scene: Object.freeze({ schema_version: scene.schemaVersion, resource_id: scene.source.resourceId, formula: scene.formula }),
    expansion: Object.freeze([...settings.expansion]) as SupercellRepeat,
    origin_policy: settings.originPolicy,
    display: Object.freeze({ show_primary_cell: settings.showPrimaryCell, show_supercell_boundary: settings.showSupercellBoundary, show_internal_grid: false as const }),
    counts: Object.freeze({ total_cells: estimate.totalCells, canonical_sites: scene.atoms.length, displayed_atoms: estimate.displayedAtoms, canonical_bonds: scene.bonds.length, displayed_bonds: estimate.displayedBonds }),
    mode: estimate.mode,
    caps: PERIODIC_DERIVED_CAPS,
    warnings: estimate.warnings,
    deterministic: true as const,
    policy: Object.freeze({ renderer_local: true as const, structure_mutated: false as const, canonical_topology_mutated: false as const }),
    security: Object.freeze({ inert_json: true as const, contains_javascript: false as const, external_urls: Object.freeze([]) as readonly string[] }),
  });
  if (JSON.stringify(result).length > PERIODIC_DERIVED_CAPS.maxArtifactBytes) throw new Error("VIEWER_SUPERCELL_STATE_TOO_LARGE");
  return result;
}

export function replayViewerSupercellState(scene: ValidatedRenderScene, value: unknown): ViewerSupercellSettings {
  if (!value || typeof value !== "object") throw new Error("VIEWER_SUPERCELL_STATE_INVALID");
  const input = value as Record<string, unknown>;
  const source = input.scene as Record<string, unknown> | undefined;
  const display = input.display as Record<string, unknown> | undefined;
  if (input.schema_version !== "phase10f24.viewer_supercell_state.v1" || source?.schema_version !== scene.schemaVersion || source.resource_id !== scene.source.resourceId || !validSupercellRepeat(input.expansion) || input.origin_policy !== "positive_octant" || typeof display?.show_primary_cell !== "boolean" || typeof display.show_supercell_boundary !== "boolean" || display.show_internal_grid !== false) throw new Error("VIEWER_SUPERCELL_STATE_INVALID");
  const estimate = estimatePeriodicSupercell(scene, input.expansion);
  if (estimate.mode === "refused") throw new Error(estimate.error ?? "VIEWER_SUPERCELL_RENDER_BUDGET_EXCEEDED");
  return Object.freeze({ expansion: Object.freeze([...input.expansion]) as SupercellRepeat, originPolicy: "positive_octant", showPrimaryCell: display.show_primary_cell, showSupercellBoundary: display.show_supercell_boundary, showInternalGrid: false });
}
