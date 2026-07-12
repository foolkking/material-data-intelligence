import { describe, expect, it } from "vitest";

import minimalScene from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_minimal_crystal.viewer_scene.v1.json";
import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import { classifyViewerPerformance, VIEWER_PERFORMANCE_BUDGETS } from "./viewerScenePerformance";

function sceneWithCounts(atoms: number, bonds: number) {
  const mapped = mapViewerSceneForRenderer(minimalScene);
  if (!mapped.ok) throw new Error("fixture mapping failed");
  const atom = mapped.scene.atoms[0];
  const bond = mapped.scene.bonds[0];
  return Object.freeze({ ...mapped.scene, atoms: Object.freeze(Array.from({ length: atoms }, (_, index) => Object.freeze({ ...atom, id: `a-${index}`, siteIndex: index, ref: Object.freeze({ siteIndex: index, imageOffset: Object.freeze([0,0,0] as const) }) }))), bonds: Object.freeze(bond ? Array.from({ length: bonds }, (_, index) => Object.freeze({ ...bond, id: `b-${index}` })) : []) });
}

describe("viewer performance policy", () => {
  it("keeps small scenes interactive", () => expect(classifyViewerPerformance(sceneWithCounts(64, 0))).toMatchObject({ tier: "interactive", pixelRatioCap: 2, antialias: true }));
  it("degrades near-cap scenes without dropping data", () => expect(classifyViewerPerformance(sceneWithCounts(1_024, 0))).toMatchObject({ tier: "degraded", atomCount: 1_024, pixelRatioCap: 1, antialias: false }));
  it("refuses over-budget scenes before engine creation", () => expect(classifyViewerPerformance(sceneWithCounts(VIEWER_PERFORMANCE_BUDGETS.maxDisplayedAtoms + 1, 0))).toMatchObject({ tier: "refused", reason: "VIEWER_RENDERER_PERFORMANCE_BUDGET_EXCEEDED" }));
});
