import { describe, expect, it } from "vitest";

import legacyV1 from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_optional_bonds.viewer_scene.v1.json";
import { buildViewerExportMarkdown, buildViewerExportState, DEFAULT_VIEWER_EXPORT_REQUEST } from "./viewerSceneExport";
import { measureDistance } from "./viewerSceneMeasurements";
import { classifyViewerPerformance } from "./viewerScenePerformance";
import { periodicBoundaryScene } from "./viewerScenePeriodicBondTestFixture";
import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import type { ValidatedRenderScene, ViewerRendererSnapshot } from "./viewerSceneRendererTypes";
import { validateViewerSceneForRenderer } from "./viewerSceneRendererValidation";
import { changeViewerSelectionMode, initialViewerSelection, selectViewerSite } from "./viewerSceneSelection";
import { derivePeriodicSupercell } from "./viewerSceneSupercell";
import { initialViewerClipState } from "./viewerSceneViewState";
import { viewerSceneCompatibility } from "./viewerSceneCompatibility";

describe("Phase 10 product closure", () => {
  it("composes validated periodic viewing, measurement, supercell, clipping, and export without scientific mutation", () => {
    const mapped = mapViewerSceneForRenderer(periodicBoundaryScene());
    expect(mapped.ok).toBe(true);
    if (!mapped.ok) return;
    const canonical = mapped.scene;
    expect(canonical.schemaVersion).toBe("phase10f18.viewer_scene.v2");
    expect(canonical.bonds).toHaveLength(1);
    expect(canonical.bonds[0].id).toBe("bond:0:0,0,0->1:1,0,0");

    const derived = derivePeriodicSupercell(canonical, [2, 2, 2]);
    expect(derived.ok).toBe(true);
    if (!derived.ok) return;
    expect(derived.scene.atoms).toHaveLength(canonical.atoms.length * 8);
    expect(derived.scene.source.resourceId).toBe(canonical.source.resourceId);
    expect(classifyViewerPerformance(derived.scene).tier).toBe("interactive");

    let selection = changeViewerSelectionMode(initialViewerSelection(), "distance");
    selection = selectViewerSite(selection, { siteIndex: 0, imageOffset: [0, 0, 0] });
    selection = selectViewerSite(selection, { siteIndex: 1, imageOffset: [1, 0, 0] });
    expect(selection.selectedSites).toEqual([
      { siteIndex: 0, imageOffset: [0, 0, 0] },
      { siteIndex: 1, imageOffset: [1, 0, 0] },
    ]);
    const measured = measureDistance([0, 1], [canonical.bonds[0].start, canonical.bonds[0].end]);
    expect(measured.ok).toBe(true);
    if (!measured.ok) return;
    expect(measured.result.value).toBeCloseTo(canonical.bonds[0].distanceAngstrom, 8);

    const state = buildViewerExportState({
      scene: derived.scene,
      snapshot: snapshot(derived.scene),
      request: DEFAULT_VIEWER_EXPORT_REQUEST,
      clip: initialViewerClipState(derived.scene),
      cameraPreset: "isometric",
      showCell: true,
      showSupercellBoundary: true,
      showAxes: true,
      showBonds: true,
      measurements: [{ result: measured.result, refs: selection.selectedSites }],
    });
    const markdown = buildViewerExportMarkdown(derived.scene, state);
    expect(state.policy).toMatchObject({ structure_mutated: false, topology_mutated: false });
    expect(state.security).toEqual({ contains_javascript: false, contains_html: false, external_urls: [] });
    expect(state.viewer_state.supercell_expansion).toEqual([2, 2, 2]);
    expect(markdown).toContain("No structure or topology mutation occurred");
    expect(markdown).not.toMatch(/<script|javascript:|https?:\/\//i);
    expect(canonical.supercellRepeat).toEqual([1, 1, 1]);
    expect(canonical.atoms).toHaveLength(2);
  });

  it("keeps legacy/current capability truth and stops invalid or over-budget data before rendering", () => {
    expect(viewerSceneCompatibility("phase10d1.viewer_scene.v1")).toMatchObject({ status: "deprecated_read_only", rendererSupported: false });
    expect(viewerSceneCompatibility("phase10f8.viewer_scene.v1")).toMatchObject({ status: "supported_legacy_same_cell", periodicTopologySupported: false });
    expect(viewerSceneCompatibility("phase10f18.viewer_scene.v2")).toMatchObject({ status: "current", rendererSupported: true, periodicTopologySupported: true });
    expect(mapViewerSceneForRenderer(legacyV1).ok).toBe(true);

    const malformed = periodicBoundaryScene();
    malformed.scene.sites[0].xyz = [Number.NaN, 0, 0];
    expect(validateViewerSceneForRenderer(malformed)).toMatchObject({ valid: false });
    expect(mapViewerSceneForRenderer(malformed).ok).toBe(false);

    const mapped = mapViewerSceneForRenderer(periodicBoundaryScene());
    expect(mapped.ok).toBe(true);
    if (!mapped.ok) return;
    const refused = Object.freeze({
      ...mapped.scene,
      atoms: Object.freeze(Array.from({ length: 2_049 }, () => mapped.scene.atoms[0])),
    }) as ValidatedRenderScene;
    expect(classifyViewerPerformance(refused)).toMatchObject({ tier: "refused", reason: "VIEWER_RENDERER_PERFORMANCE_BUDGET_EXCEEDED" });
  });
});

function snapshot(scene: ValidatedRenderScene): ViewerRendererSnapshot {
  return {
    state: "rendered", canvasCount: 1, atomCount: scene.atoms.length, bondCount: scene.bonds.length,
    latticeEdgeCount: 12, triangleCount: scene.atoms.length * 560, lineCount: scene.bonds.length + 12,
    cameraPosition: [12, 12, 12], cameraTarget: [5, 5, 5], cameraUp: [0, 0, 1], cameraZoom: 1,
    cameraPreset: "isometric", activeClipPlanes: 0, latticeAxesVisible: true, drawingBuffer: [1200, 900],
    graphicsContext: "webgl2", rendererVersion: "185", selectedSites: [], selectedSiteIndices: [], selectedBondId: null,
    siteScreenPositions: [], bondScreenPositions: [],
    metrics: {
      performanceTier: "interactive", atomCount: scene.atoms.length, bondCount: scene.bonds.length,
      speciesCount: new Set(scene.atoms.map((atom) => atom.species)).size, instancedMeshCount: 2,
      latticeEdgeCount: 12, drawCalls: 5, geometries: 5, materials: 6, triangles: scene.atoms.length * 560,
      lines: scene.bonds.length + 12, textures: 0, bufferAttributes: 3, sceneObjects: 10,
      initializationMs: 1, firstFrameMs: 2,
    },
  };
}
