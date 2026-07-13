import { describe, expect, it } from "vitest";

import minimalScene from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_minimal_crystal.viewer_scene.v1.json";
import {
  assertViewerExportDimensions,
  buildViewerExportManifest,
  buildViewerExportMarkdown,
  buildViewerExportState,
  DEFAULT_VIEWER_EXPORT_REQUEST,
  jsonBlob,
  sanitizeViewerFilename,
  validateViewerExportRequest,
} from "./viewerSceneExport";
import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import type { ViewerRendererSnapshot } from "./viewerSceneRendererTypes";
import { initialViewerClipState } from "./viewerSceneViewState";

describe("viewer export security", () => {
  it("sanitizes filenames without retaining paths or markup", () => {
    expect(sanitizeViewerFilename("../../<script> Na Cl")).toBe("script-Na-Cl-structure-viewer.png");
  });

  it("enforces the effective pixel cap", () => {
    expect(() => assertViewerExportDimensions(4096, 4096)).not.toThrow();
    expect(() => assertViewerExportDimensions(4097, 256)).toThrow("VIEWER_EXPORT_INVALID_SIZE");
    expect(() => assertViewerExportDimensions(4096, 4096, 2)).toThrow("VIEWER_EXPORT_INVALID_SIZE");
    expect(() => assertViewerExportDimensions(2400, 1800, 1)).not.toThrow();
  });

  it("strictly validates formats, backgrounds, dimensions, and unknown fields", () => {
    expect(validateViewerExportRequest(DEFAULT_VIEWER_EXPORT_REQUEST)).toEqual(DEFAULT_VIEWER_EXPORT_REQUEST);
    expect(() => validateViewerExportRequest({...DEFAULT_VIEWER_EXPORT_REQUEST, format:"pdf"})).toThrow("VIEWER_EXPORT_REQUEST_INVALID");
    expect(() => validateViewerExportRequest({...DEFAULT_VIEWER_EXPORT_REQUEST, background:"url(x)"})).toThrow("VIEWER_EXPORT_REQUEST_INVALID");
    expect(() => validateViewerExportRequest({...DEFAULT_VIEWER_EXPORT_REQUEST, shader:"main"})).toThrow("VIEWER_EXPORT_REQUEST_INVALID");
    expect(() => validateViewerExportRequest({...DEFAULT_VIEWER_EXPORT_REQUEST, width:Number.NaN})).toThrow("VIEWER_EXPORT_INVALID_SIZE");
  });

  it("builds inert deterministic state and Markdown from the validated scene", () => {
    const mapped = mapViewerSceneForRenderer(minimalScene);
    expect(mapped.ok).toBe(true);
    if (!mapped.ok) return;
    const state = buildViewerExportState({
      scene:mapped.scene,
      snapshot:snapshot(),
      request:DEFAULT_VIEWER_EXPORT_REQUEST,
      clip:initialViewerClipState(mapped.scene),
      cameraPreset:"default",
      showCell:true,
      showSupercellBoundary:true,
      showAxes:false,
      showBonds:true,
      measurements:[],
      inspectorSummary:{siteIndex:0,imageOffset:[0,0,0],species:"Si<script>",displayedCartesian:[0,0,0]},
    });
    const markdown = buildViewerExportMarkdown(mapped.scene, state);
    expect(state.schema_version).toBe("phase10f26.viewer_export_state.v1");
    expect(state.policy.structure_mutated).toBe(false);
    expect(state.security.external_urls).toEqual([]);
    expect(state.inspector_summary).toBeNull();
    expect(markdown).toContain("# Scientific Structure Viewer Export");
    expect(markdown).toContain("No structure or topology mutation occurred");
    expect(markdown).not.toMatch(/<script|javascript:|https?:\/\//i);
  });

  it("emits a stable manifest with real SHA-256 hashes", async () => {
    const artifacts = [
      {name:"viewer.png", mediaType:"image/png" as const, blob:new Blob(["png"])},
      {name:"viewer_export_state.json", mediaType:"application/json" as const, blob:new Blob(["json"])},
      {name:"viewer_export_summary.md", mediaType:"text/markdown" as const, blob:new Blob(["markdown"])},
    ];
    const manifest = await buildViewerExportManifest(artifacts);
    expect(manifest.artifacts.map((item) => item.name)).toEqual(artifacts.map((item) => item.name));
    expect(manifest.artifacts.every((item) => /^[0-9a-f]{64}$/.test(item.sha256))).toBe(true);
    expect(manifest.renderer_included).toBe(false);
    expect(manifest.external_assets).toEqual([]);
  });

  it("creates inert JSON blobs", () => {
    const blob = jsonBlob({ label: "<script>" });
    expect(blob.type).toBe("application/json");
    expect(blob.size).toBeGreaterThan(0);
  });
});

function snapshot(): ViewerRendererSnapshot {
  return {
    state:"rendered", canvasCount:1, atomCount:1, bondCount:0, latticeEdgeCount:12,
    triangleCount:560, lineCount:12, cameraPosition:[8,8,8], cameraTarget:[0,0,0],
    cameraUp:[0,0,1], cameraZoom:1, cameraPreset:"default", activeClipPlanes:0,
    latticeAxesVisible:false, drawingBuffer:[720,480], graphicsContext:"webgl2",
    rendererVersion:"185", selectedSites:[], selectedSiteIndices:[], selectedBondId:null,
    siteScreenPositions:[], bondScreenPositions:[],
    metrics:{performanceTier:"interactive", atomCount:1, bondCount:0, speciesCount:1,
      instancedMeshCount:1, latticeEdgeCount:12, drawCalls:3, geometries:3, materials:3,
      triangles:560, lines:12, textures:0, bufferAttributes:3, sceneObjects:8,
      initializationMs:1, firstFrameMs:2},
  };
}
