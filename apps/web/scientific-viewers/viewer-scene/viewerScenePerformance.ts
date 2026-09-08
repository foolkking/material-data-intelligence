import type { ValidatedRenderScene } from "./viewerSceneRendererTypes";

export const VIEWER_PERFORMANCE_BUDGETS = Object.freeze({
  interactiveAtoms: 1_000,
  interactiveBonds: 4_096,
  maxDisplayedAtoms: 2_048,
  maxDisplayedBonds: 8_192,
  maxStyleGroups: 32,
  maxAtomDrawCalls: 32,
  maxTotalDrawCalls: 40,
  maxGeometries: 5,
  maxMaterials: 39,
});

export type ViewerPerformanceTier = "interactive" | "degraded" | "refused";

export type ViewerPerformanceDecision = Readonly<{
  tier: ViewerPerformanceTier;
  atomCount: number;
  bondCount: number;
  styleGroupCount: number;
  pixelRatioCap: 1 | 2;
  antialias: boolean;
  warning: string | null;
  reason: string | null;
}>;

export function classifyViewerPerformance(scene: ValidatedRenderScene): ViewerPerformanceDecision {
  const styleGroupCount = new Set(scene.atoms.map((atom) => `${atom.species}|${atom.color}`)).size;
  const atomCount = scene.atoms.length;
  const bondCount = scene.bonds.length;
  if (atomCount > VIEWER_PERFORMANCE_BUDGETS.maxDisplayedAtoms || bondCount > VIEWER_PERFORMANCE_BUDGETS.maxDisplayedBonds || styleGroupCount > VIEWER_PERFORMANCE_BUDGETS.maxStyleGroups) {
    return Object.freeze({ tier: "refused", atomCount, bondCount, styleGroupCount, pixelRatioCap: 1, antialias: false, warning: null, reason: "VIEWER_RENDERER_PERFORMANCE_BUDGET_EXCEEDED" });
  }
  if (atomCount > VIEWER_PERFORMANCE_BUDGETS.interactiveAtoms || bondCount > VIEWER_PERFORMANCE_BUDGETS.interactiveBonds) {
    return Object.freeze({ tier: "degraded", atomCount, bondCount, styleGroupCount, pixelRatioCap: 1, antialias: false, warning: "VIEWER_RENDERER_DEGRADED_RESOURCE_MODE", reason: null });
  }
  return Object.freeze({ tier: "interactive", atomCount, bondCount, styleGroupCount, pixelRatioCap: 2, antialias: true, warning: null, reason: null });
}

export function assertViewerResourceMetrics(metrics: { drawCalls: number; geometries: number; materials: number }) {
  return metrics.drawCalls <= VIEWER_PERFORMANCE_BUDGETS.maxTotalDrawCalls
    && metrics.geometries <= VIEWER_PERFORMANCE_BUDGETS.maxGeometries
    && metrics.materials <= VIEWER_PERFORMANCE_BUDGETS.maxMaterials;
}
