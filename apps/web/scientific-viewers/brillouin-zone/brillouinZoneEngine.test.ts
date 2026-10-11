import { afterEach, describe, expect, it, vi } from "vitest";
import * as THREE from "three";

import manifest from "../../../../tests/fixtures/brillouin_zone_v1/simple_cubic/manifest.json";
import reciprocal from "../../../../tests/fixtures/brillouin_zone_v1/simple_cubic/reciprocal_lattice.json";
import zone from "../../../../tests/fixtures/brillouin_zone_v1/simple_cubic/brillouin_zone.json";
import kpath from "../../../../tests/fixtures/brillouin_zone_v1/simple_cubic/kpath.json";
import { createBrillouinZoneEngine } from "./brillouinZoneEngine";
import { mapBrillouinZoneArtifacts } from "./brillouinZoneMapper";

const capture = vi.hoisted(() => ({ camera: null as unknown, resize: () => {}, pngCamera: null as unknown, failPng: false, pauseEncoding: false, encode: null as BlobCallback | null, labels: [] as Array<{id:string;text:string;x:number;y:number}>, palette: {} as Record<string, number>, pngPalette: {} as Record<string, number> }));
vi.mock("./brillouinZoneExport", async importOriginal => {
  const real = await importOriginal<typeof import("./brillouinZoneExport")>();
  return { ...real, composeBrillouinZoneImage: (_source: HTMLCanvasElement, request: {width:number;height:number;pixelRatio:number}, labels: typeof capture.labels) => {
    capture.pngCamera = (capture.camera as THREE.Camera).clone();
    capture.pngPalette = {...capture.palette};
    capture.labels = labels;
    const canvas = document.createElement("canvas");
    canvas.width = request.width * request.pixelRatio; canvas.height = request.height * request.pixelRatio;
    canvas.toBlob = callback => {
      if (capture.pauseEncoding) capture.encode = callback;
      else callback(capture.failPng ? null : new Blob(["image"], {type:"image/png"}));
    };
    return canvas;
  } };
});
vi.mock("three", async importOriginal => {
  const real = await importOriginal<typeof import("three")>();
  return { ...real, WebGLRenderer: class {
    domElement = document.createElement("canvas");
    capabilities = { isWebGL2: true };
    info = { render: { calls: 1 }, memory: { geometries: 9, textures: 0 } };
    size = new real.Vector2();
    ratio = 1;
    color = new real.Color();
    alpha = 1;
    constructor() {
      this.domElement.toBlob = callback => {
        capture.pngCamera = (capture.camera as THREE.Camera).clone();
        callback(capture.failPng ? null : new Blob(["image"], { type: "image/png" }));
      };
    }
    setSize(w: number, h: number) { this.size.set(w, h); }
    getSize(out: THREE.Vector2) { return out.copy(this.size); }
    setPixelRatio(value: number) { this.ratio = value; }
    getPixelRatio() { return this.ratio; }
    setClearColor(value: THREE.ColorRepresentation, alpha: number) { this.color.set(value); this.alpha = alpha; }
    getClearColor(out: THREE.Color) { return out.copy(this.color); }
    getClearAlpha() { return this.alpha; }
    render(scene: THREE.Scene, camera: THREE.Camera) {
      capture.camera = camera;
      const palette: Record<string, number> = {};
      scene.traverse(item => { const material = (item as THREE.Mesh).material as THREE.MeshBasicMaterial; if (material?.color) palette[item.name] = material.color.getHex(); });
      capture.palette = palette;
    }
    forceContextLoss() {}
    dispose() {}
  } };
});

afterEach(() => { vi.unstubAllGlobals(); capture.failPng = false; capture.pauseEncoding = false; capture.encode = null; document.body.replaceChildren(); });

async function setup() {
  vi.stubGlobal("ResizeObserver", class { constructor(callback: () => void) { capture.resize = callback; } observe() {} disconnect() {} });
  const mapped = mapBrillouinZoneArtifacts({ manifest, reciprocal, zone, kpath });
  if (!mapped.ok) throw new Error("Invalid fixture");
  const container = document.createElement("div");
  const size = { width: 240, height: 400 };
  Object.defineProperties(container, { clientWidth: { get: () => size.width }, clientHeight: { get: () => size.height } });
  document.body.append(container);
  const engine = await createBrillouinZoneEngine({ container, scene: mapped.scene, projection: "perspective", opacity: 0.28, variantId: mapped.scene.selectedVariantId, artifactBytes: 100, mappingMs: 0, visibility: { faces: true, edges: true, vertices: true, axes: true, points: true, labels: true, path: true }, onSelection: vi.fn(), onContextLost: vi.fn(), onViewChange: vi.fn() });
  return { engine, size, scene: mapped.scene };
}

describe("Brillouin zone camera lifecycle", () => {
  it("uses the actual narrow canvas and preserves a manual pose through resize and projection changes", async () => {
    const { engine, size } = await setup();
    expect((capture.camera as THREE.PerspectiveCamera).aspect).toBe(0.6);
    engine.keyboardCamera("rotate_left");
    const before = engine.snapshot();
    size.width = 720;
    capture.resize();
    expect(engine.snapshot().cameraPosition).toEqual(before.cameraPosition);
    expect(engine.snapshot().cameraTarget).toEqual(before.cameraTarget);
    engine.setProjection("orthographic");
    expect(engine.snapshot().cameraPosition).toEqual(before.cameraPosition);
    const camera = capture.camera as THREE.OrthographicCamera;
    const zoom = camera.zoom;
    engine.keyboardCamera("zoom_in");
    expect(camera.zoom).toBeGreaterThan(zoom);
    const manualZoom = camera.zoom;
    size.width = 320;
    capture.resize();
    expect(camera.zoom).toBe(manualZoom);
    engine.dispose();
  });

  it.each([false, true])("preserves orthographic image proportions and restores the canvas after PNG success/failure (%s)", async fail => {
    const { engine } = await setup();
    engine.setProjection("orthographic");
    const camera = capture.camera as THREE.OrthographicCamera;
    const original = [camera.left, camera.right, camera.top, camera.bottom];
    capture.failPng = fail;
    const exporting = engine.exportPng({ width: 1600, height: 1200, pixelRatio: 1, background: "light" });
    if (fail) await expect(exporting).rejects.toThrow("BZ_EXPORT_FAILED");
    else await expect(exporting).resolves.toBeInstanceOf(Blob);
    const imageCamera = capture.pngCamera as THREE.OrthographicCamera;
    expect((imageCamera.right - imageCamera.left) / (imageCamera.top - imageCamera.bottom)).toBeCloseTo(4 / 3);
    expect([camera.left, camera.right, camera.top, camera.bottom]).toEqual(original);
    engine.dispose();
  });

  it("keeps pose, selection and zoom while encoding, and rejects duplicate exports", async () => {
    const { engine, size } = await setup();
    size.width = 1200; size.height = 400; capture.resize();
    engine.setProjection("orthographic");
    engine.keyboardCamera("rotate_right"); engine.keyboardCamera("zoom_in");
    engine.setSelection({kind:"point",id:kpath.points[0].point_id});
    const before = engine.snapshot();
    const camera = capture.camera as THREE.OrthographicCamera;
    const zoom = camera.zoom;
    const palette = {...capture.palette};
    capture.pauseEncoding = true;
    const request = {width:1600,height:1200,pixelRatio:2,background:"dark"} as const;
    const exporting = engine.exportPng(request);
    expect(engine.snapshot()).toMatchObject({cameraPosition:before.cameraPosition,cameraTarget:before.cameraTarget,selection:before.selection});
    expect(camera.zoom).toBe(zoom);
    expect(capture.palette).toEqual(palette);
    expect(capture.pngPalette["canonical-bz-edges"]).toBe(0xa9cbd4);
    expect(capture.labels.map(item => item.text)).toEqual(kpath.points.map(item => item.display_label));
    const imageCamera = capture.pngCamera as THREE.OrthographicCamera;
    expect(imageCamera.zoom).toBeCloseTo(zoom / (3 / (4 / 3)));
    await expect(engine.exportPng(request)).rejects.toThrow("BZ_EXPORT_IN_PROGRESS");
    engine.keyboardCamera("rotate_left");
    const moved = engine.snapshot().cameraPosition;
    capture.encode?.(new Blob(["image"], {type:"image/png"}));
    await exporting;
    expect(engine.snapshot().cameraPosition).toEqual(moved);
    engine.dispose();
  });

  it("projects PNG labels into output coordinates and honors hidden labels", async () => {
    const { engine, scene } = await setup();
    await engine.exportPng({width:1600,height:1200,pixelRatio:1,background:"light"});
    for (const label of capture.labels) {
      const point=scene.points.find(item=>item.id===label.id)!;
      const projected=new THREE.Vector3(...point.cartesian).multiplyScalar(scene.visualScale).project(capture.pngCamera as THREE.Camera);
      expect(label.x).toBeCloseTo((projected.x+1)*800,5);
      expect(label.y).toBeCloseTo((1-projected.y)*600,5);
    }
    const gamma = capture.labels.find(item => item.text === "Γ")!;
    expect(gamma.x).toBeGreaterThan(500); expect(gamma.x).toBeLessThan(1100);
    expect(gamma.y).toBeGreaterThan(300); expect(gamma.y).toBeLessThan(900);
    engine.setVisibility({faces:true,edges:true,vertices:false,axes:true,points:true,labels:false,path:true});
    await engine.exportPng({width:1600,height:1200,pixelRatio:1,background:"transparent"});
    expect(capture.labels).toEqual([]);
    engine.dispose();
  });
});
