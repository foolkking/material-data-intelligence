import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

import { cameraFrame, latticeEdges } from "./viewerSceneRendererGeometry";
import { ViewerRendererError } from "./viewerSceneRendererErrors";
import type { RenderVector3, ViewerRendererEngine, ViewerRendererSnapshot, ValidatedRenderScene } from "./viewerSceneRendererTypes";

export async function createThreeViewerEngine(args: {
  readonly container: HTMLElement;
  readonly scene: ValidatedRenderScene;
  readonly onContextLost: () => void;
  readonly pixelRatioCap: number;
}): Promise<ViewerRendererEngine> {
  const { container, scene, onContextLost, pixelRatioCap } = args;
  const width = Math.max(320, container.clientWidth || 720);
  const height = Math.max(320, container.clientHeight || 480);
  let renderer: THREE.WebGLRenderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: "high-performance" });
  } catch {
    throw new ViewerRendererError("VIEWER_RENDERER_INITIALIZATION_FAILED", "The browser could not initialize the graphics renderer.");
  }
  renderer.domElement.setAttribute("data-testid", "viewer-scene-renderer-canvas");
  renderer.domElement.setAttribute("aria-label", "Interactive three-dimensional crystal structure renderer");
  renderer.domElement.setAttribute("role", "img");
  renderer.setPixelRatio(Math.min(Math.max(window.devicePixelRatio || 1, 1), pixelRatioCap));
  renderer.setSize(width, height, false);
  renderer.setClearColor(0xf3f6f7, 1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.append(renderer.domElement);

  const threeScene = new THREE.Scene();
  const frame = cameraFrame(scene);
  const camera = new THREE.PerspectiveCamera(42, width / height, frame.near, frame.far);
  const initialPosition = new THREE.Vector3(...frame.position);
  const initialTarget = new THREE.Vector3(...frame.target);
  camera.position.copy(initialPosition);
  camera.up.set(0, 0, 1);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = false;
  controls.enablePan = true;
  controls.minDistance = Math.max(0.2, frame.near * 4);
  controls.maxDistance = frame.far * 0.45;
  controls.target.copy(initialTarget);

  const root = new THREE.Group();
  root.name = "validated-viewer-scene";
  threeScene.add(root);

  const sphereGeometry = new THREE.SphereGeometry(1, 20, 14);
  const materials = new Map<string, THREE.MeshStandardMaterial>();
  for (const atom of scene.atoms) {
    let material = materials.get(atom.color);
    if (!material) {
      material = new THREE.MeshStandardMaterial({ color: atom.color, roughness: 0.38, metalness: 0.04 });
      materials.set(atom.color, material);
    }
    const mesh = new THREE.Mesh(sphereGeometry, material);
    mesh.name = atom.id;
    mesh.position.set(...atom.position);
    mesh.scale.setScalar(atom.radius);
    mesh.userData = { siteIndex: atom.siteIndex, species: atom.species };
    root.add(mesh);
  }

  const bondGeometry = lineGeometry(scene.bonds.flatMap((bond) => [bond.start, bond.end]));
  const bondMaterial = new THREE.LineBasicMaterial({ color: 0x62707c, transparent: true, opacity: 0.74 });
  const bondLines = new THREE.LineSegments(bondGeometry, bondMaterial);
  bondLines.name = "bounded-non-authoritative-bonds";
  root.add(bondLines);

  const cellGeometry = lineGeometry(latticeEdges(scene.lattice.matrix).flatMap((edge) => [edge[0], edge[1]]));
  const cellMaterial = new THREE.LineBasicMaterial({ color: 0x1f6f8b, transparent: true, opacity: 0.9 });
  const cellLines = new THREE.LineSegments(cellGeometry, cellMaterial);
  cellLines.name = "unit-cell";
  root.add(cellLines);

  const ambient = new THREE.AmbientLight(0xffffff, 1.35);
  const key = new THREE.DirectionalLight(0xffffff, 2.25);
  key.position.set(frame.position[0], frame.position[1] - 6, frame.position[2] + 4);
  threeScene.add(ambient, key);

  let disposed = false;
  let contextLost = false;
  let publishEvidence = () => {};
  const render = () => {
    if (disposed || contextLost) return;
    renderer.render(threeScene, camera);
    publishEvidence();
  };
  const resetCamera = () => {
    camera.position.copy(initialPosition);
    controls.target.copy(initialTarget);
    camera.near = frame.near;
    camera.far = frame.far;
    camera.updateProjectionMatrix();
    controls.update();
    render();
  };
  const onControlsChange = () => render();
  controls.addEventListener("change", onControlsChange);
  controls.update();

  const onLost = (event: Event) => {
    event.preventDefault();
    contextLost = true;
    onContextLost();
  };
  renderer.domElement.addEventListener("webglcontextlost", onLost, false);

  const resize = () => {
    if (disposed) return;
    const nextWidth = Math.max(320, container.clientWidth || width);
    const nextHeight = Math.max(320, container.clientHeight || height);
    camera.aspect = nextWidth / nextHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(nextWidth, nextHeight, false);
    render();
  };
  const resizeObserver = typeof ResizeObserver === "function" ? new ResizeObserver(resize) : null;
  resizeObserver?.observe(container);
  window.addEventListener("resize", resize);

  const graphicsContext = renderer.capabilities.isWebGL2 ? "webgl2" : "webgl";
  const snapshot = (): ViewerRendererSnapshot => Object.freeze({
    state: contextLost ? "context_lost" : disposed ? "disposed" : "rendered",
    canvasCount: container.querySelectorAll("canvas").length,
    atomCount: scene.atoms.length,
    bondCount: bondLines.visible ? scene.bonds.length : 0,
    latticeEdgeCount: cellLines.visible ? 12 : 0,
    triangleCount: renderer.info.render.triangles,
    lineCount: renderer.info.render.lines,
    cameraPosition: vector(camera.position),
    cameraTarget: vector(controls.target),
    drawingBuffer: Object.freeze([renderer.domElement.width, renderer.domElement.height] as const),
    graphicsContext,
    rendererVersion: THREE.REVISION,
  });
  publishEvidence = () => {
    (window as unknown as { __mdiViewerSceneRendererEvidence?: ViewerRendererSnapshot }).__mdiViewerSceneRendererEvidence = snapshot();
  };
  render();

  return {
    resetCamera,
    setCellVisible(visible) { cellLines.visible = visible; render(); },
    setBondsVisible(visible) { bondLines.visible = visible; render(); },
    render,
    snapshot,
    dispose() {
      if (disposed) return;
      disposed = true;
      resizeObserver?.disconnect();
      window.removeEventListener("resize", resize);
      controls.removeEventListener("change", onControlsChange);
      controls.dispose();
      renderer.domElement.removeEventListener("webglcontextlost", onLost);
      sphereGeometry.dispose();
      bondGeometry.dispose();
      cellGeometry.dispose();
      bondMaterial.dispose();
      cellMaterial.dispose();
      for (const material of materials.values()) material.dispose();
      renderer.dispose();
      renderer.forceContextLoss();
      if (renderer.domElement.parentElement === container) renderer.domElement.remove();
      root.clear();
      threeScene.clear();
      delete (window as unknown as { __mdiViewerSceneRendererEvidence?: ViewerRendererSnapshot }).__mdiViewerSceneRendererEvidence;
    },
  };
}

function lineGeometry(points: readonly RenderVector3[]) {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(points.flatMap((point) => [...point]), 3));
  return geometry;
}

function vector(value: THREE.Vector3): RenderVector3 {
  return Object.freeze([round(value.x), round(value.y), round(value.z)]);
}

function round(value: number) {
  return Math.round(value * 1_000_000) / 1_000_000;
}
