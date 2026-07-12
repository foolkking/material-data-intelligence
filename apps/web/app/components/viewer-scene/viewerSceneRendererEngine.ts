import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

import { cameraFrame, latticeEdges } from "./viewerSceneRendererGeometry";
import { assertViewerExportDimensions } from "./viewerSceneExport";
import { ViewerRendererError } from "./viewerSceneRendererErrors";
import { periodicSiteKey } from "./viewerScenePeriodicGeometry";
import type { PeriodicSiteRef, RenderVector3, ViewerRendererEngine, ViewerRendererSnapshot, ValidatedRenderScene } from "./viewerSceneRendererTypes";

export async function createThreeViewerEngine(args: {
  readonly container: HTMLElement;
  readonly scene: ValidatedRenderScene;
  readonly onContextLost: () => void;
  readonly onSitePick?: (site: PeriodicSiteRef | null) => void;
  readonly pixelRatioCap: number;
  readonly antialias: boolean;
  readonly performanceTier: "interactive" | "degraded";
}): Promise<ViewerRendererEngine> {
  const startedAt = performance.now();
  const { container, scene, onContextLost, onSitePick, pixelRatioCap, antialias, performanceTier } = args;
  const width = Math.max(320, container.clientWidth || 720);
  const height = Math.max(320, container.clientHeight || 480);
  let renderer: THREE.WebGLRenderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias, alpha: false, powerPreference: performanceTier === "degraded" ? "low-power" : "high-performance" });
  } catch {
    throw new ViewerRendererError("VIEWER_RENDERER_INITIALIZATION_FAILED", "The browser could not initialize the graphics renderer.");
  }
  renderer.domElement.setAttribute("data-testid", "viewer-scene-renderer-canvas");
  renderer.domElement.setAttribute("aria-label", "Interactive three-dimensional crystal structure renderer");
  renderer.domElement.setAttribute("role", "img");
  renderer.domElement.tabIndex = -1;
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
  renderer.domElement.style.touchAction = "pan-y";
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
  const atomGroups = new Map<string, typeof scene.atoms>();
  for (const atom of scene.atoms) {
    const key = `${atom.species}|${atom.color}`;
    atomGroups.set(key, Object.freeze([...(atomGroups.get(key) ?? []), atom]));
  }
  const atomMeshes: THREE.InstancedMesh[] = [];
  const atomsByKey = new Map(scene.atoms.map((atom) => [periodicSiteKey(atom.ref), atom] as const));
  const transform = new THREE.Matrix4();
  for (const [groupKey, atoms] of [...atomGroups.entries()].sort(([left], [right]) => left.localeCompare(right))) {
    const color = atoms[0].color;
    let material = materials.get(color);
    if (!material) {
      material = new THREE.MeshStandardMaterial({ color, roughness: 0.38, metalness: 0.04 });
      materials.set(color, material);
    }
    const mesh = new THREE.InstancedMesh(sphereGeometry, material, atoms.length);
    mesh.name = `atoms-${groupKey}`;
    atoms.forEach((atom, index) => {
      transform.compose(
        new THREE.Vector3(...atom.position),
        new THREE.Quaternion(),
        new THREE.Vector3(atom.radius, atom.radius, atom.radius),
      );
      mesh.setMatrixAt(index, transform);
    });
    mesh.instanceMatrix.needsUpdate = true;
    mesh.computeBoundingBox();
    mesh.computeBoundingSphere();
    mesh.userData = { periodicRefs: atoms.map((atom) => atom.ref), species: atoms[0].species };
    atomMeshes.push(mesh);
    root.add(mesh);
  }

  const bondGeometry = lineGeometry(scene.bonds.flatMap((bond) => [bond.start, bond.end]));
  const bondMaterial = new THREE.LineBasicMaterial({ color: 0x62707c, transparent: true, opacity: 0.74 });
  const bondLines = new THREE.LineSegments(bondGeometry, bondMaterial);
  bondLines.name = "bounded-non-authoritative-bonds";
  root.add(bondLines);

  const cellGeometry = lineGeometry(latticeEdges(scene.displayLattice.matrix).flatMap((edge) => [edge[0], edge[1]]));
  const cellMaterial = new THREE.LineBasicMaterial({ color: 0x1f6f8b, transparent: true, opacity: 0.9 });
  const cellLines = new THREE.LineSegments(cellGeometry, cellMaterial);
  cellLines.name = "unit-cell";
  root.add(cellLines);

  const highlightColors = [0xf5c542, 0x2ca6a4, 0xe85d75, 0x7b61ff] as const;
  const highlightMaterials = highlightColors.map((color) => new THREE.MeshBasicMaterial({ color, wireframe: true, depthTest: false }));
  const highlightMeshes = highlightMaterials.map((material, index) => {
    const mesh = new THREE.Mesh(sphereGeometry, material);
    mesh.name = `selection-${String.fromCharCode(65 + index)}`;
    mesh.renderOrder = 20;
    mesh.visible = false;
    root.add(mesh);
    return mesh;
  });
  const measurementGeometry = new THREE.BufferGeometry();
  const measurementMaterial = new THREE.LineBasicMaterial({ color: 0x0b7285, depthTest: false });
  const measurementLines = new THREE.Line(measurementGeometry, measurementMaterial);
  measurementLines.name = "measurement-chain";
  measurementLines.renderOrder = 19;
  measurementLines.visible = false;
  root.add(measurementLines);
  let selectedSites: readonly PeriodicSiteRef[] = Object.freeze([]);

  const ambient = new THREE.AmbientLight(0xffffff, 1.35);
  const key = new THREE.DirectionalLight(0xffffff, 2.25);
  key.position.set(frame.position[0], frame.position[1] - 6, frame.position[2] + 4);
  threeScene.add(ambient, key);

  let disposed = false;
  let contextLost = false;
  const initializationMs = performance.now() - startedAt;
  let firstFrameMs = 0;
  let publishEvidence = () => {};
  const render = () => {
    if (disposed || contextLost) return;
    camera.updateMatrixWorld();
    renderer.render(threeScene, camera);
    if (!firstFrameMs) firstFrameMs = performance.now() - startedAt;
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
  const keyboardCamera: ViewerRendererEngine["keyboardCamera"] = (action) => {
    const offset = camera.position.clone().sub(controls.target);
    if (action.startsWith("rotate_")) {
      const spherical = new THREE.Spherical().setFromVector3(offset);
      if (action === "rotate_left") spherical.theta -= Math.PI / 18;
      if (action === "rotate_right") spherical.theta += Math.PI / 18;
      if (action === "rotate_up") spherical.phi = Math.max(0.08, spherical.phi - Math.PI / 18);
      if (action === "rotate_down") spherical.phi = Math.min(Math.PI - 0.08, spherical.phi + Math.PI / 18);
      camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical));
    } else if (action.startsWith("pan_")) {
      const distance = Math.max(offset.length() * 0.04, 0.05);
      const right = new THREE.Vector3().crossVectors(camera.getWorldDirection(new THREE.Vector3()), camera.up).normalize();
      const up = camera.up.clone().normalize();
      const delta = action === "pan_left" ? right.multiplyScalar(-distance) : action === "pan_right" ? right.multiplyScalar(distance) : action === "pan_up" ? up.multiplyScalar(distance) : up.multiplyScalar(-distance);
      camera.position.add(delta); controls.target.add(delta);
    } else {
      const scale = action === "zoom_in" ? 0.88 : 1.12;
      const next = offset.multiplyScalar(scale);
      const boundedLength = THREE.MathUtils.clamp(next.length(), controls.minDistance, controls.maxDistance);
      camera.position.copy(controls.target).add(next.setLength(boundedLength));
    }
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

  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let pointerStart: { readonly id: number; readonly x: number; readonly y: number } | null = null;
  const pickAt = (clientX: number, clientY: number) => {
    if (contextLost || disposed) return;
    const bounds = renderer.domElement.getBoundingClientRect();
    if (bounds.width <= 0 || bounds.height <= 0) return;
    pointer.set(((clientX - bounds.left) / bounds.width) * 2 - 1, -((clientY - bounds.top) / bounds.height) * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(atomMeshes, false).find((intersection) => intersection.instanceId !== undefined && intersection.object.visible);
    if (!hit || hit.instanceId === undefined) {
      onSitePick?.(null);
      return;
    }
    const periodicRefs = (hit.object as THREE.InstancedMesh).userData.periodicRefs;
    const ref = Array.isArray(periodicRefs) ? periodicRefs[hit.instanceId] as PeriodicSiteRef | undefined : undefined;
    onSitePick?.(ref && atomsByKey.has(periodicSiteKey(ref)) ? ref : null);
  };
  const onPointerDown = (event: PointerEvent) => {
    if (event.button !== 0 || contextLost || disposed) return;
    pointerStart = { id: event.pointerId, x: event.clientX, y: event.clientY };
  };
  const onPointerUp = (event: PointerEvent) => {
    const start = pointerStart;
    pointerStart = null;
    if (!start || start.id !== event.pointerId || Math.hypot(event.clientX - start.x, event.clientY - start.y) > 5 || contextLost || disposed) return;
    pickAt(event.clientX, event.clientY);
  };
  const onPointerCancel = () => { pointerStart = null; };
  renderer.domElement.addEventListener("pointerdown", onPointerDown);
  renderer.domElement.addEventListener("pointerup", onPointerUp);
  renderer.domElement.addEventListener("pointercancel", onPointerCancel);

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
    selectedSites: Object.freeze([...selectedSites]),
    selectedSiteIndices: Object.freeze(selectedSites.map((site) => site.siteIndex)),
    siteScreenPositions: Object.freeze(scene.atoms.map((atom) => {
      const projected = new THREE.Vector3(...atom.position).project(camera);
      return Object.freeze({
        ref: atom.ref,
        siteIndex: atom.siteIndex,
        x: round((projected.x + 1) * 0.5 * renderer.domElement.clientWidth),
        y: round((1 - projected.y) * 0.5 * renderer.domElement.clientHeight),
      });
    })),
    metrics: Object.freeze({
      performanceTier,
      atomCount: scene.atoms.length,
      bondCount: scene.bonds.length,
      speciesCount: atomGroups.size,
      instancedMeshCount: atomMeshes.length,
      latticeEdgeCount: 12,
      drawCalls: renderer.info.render.calls,
      geometries: renderer.info.memory.geometries,
      materials: materials.size + 2,
      triangles: renderer.info.render.triangles,
      lines: renderer.info.render.lines,
      textures: renderer.info.memory.textures,
      bufferAttributes: 3,
      sceneObjects: root.children.length + 3,
      initializationMs: round(initializationMs),
      firstFrameMs: round(firstFrameMs),
    }),
  });
  publishEvidence = () => {
    (window as unknown as { __mdiViewerSceneRendererEvidence?: ViewerRendererSnapshot }).__mdiViewerSceneRendererEvidence = snapshot();
  };
  render();

  const setSelection = (sites: readonly PeriodicSiteRef[]) => {
    selectedSites = Object.freeze(sites.filter((site, index) => index < 4 && atomsByKey.has(periodicSiteKey(site))));
    highlightMeshes.forEach((mesh, index) => {
      const selected = selectedSites[index];
      const atom = selected ? atomsByKey.get(periodicSiteKey(selected)) : undefined;
      mesh.visible = Boolean(atom);
      if (atom) {
        mesh.position.set(...atom.position);
        const scale = atom.radius * 1.22;
        mesh.scale.set(scale, scale, scale);
      }
    });
    const points = selectedSites.flatMap((site) => {
      const atom = atomsByKey.get(periodicSiteKey(site));
      return atom ? [...atom.position] : [];
    });
    measurementGeometry.setAttribute("position", new THREE.Float32BufferAttribute(points, 3));
    measurementGeometry.computeBoundingSphere();
    measurementLines.visible = selectedSites.length >= 2;
    render();
  };

  const exportPng = async () => {
    assertViewerExportDimensions(renderer.domElement.width, renderer.domElement.height);
    render();
    return new Promise<Blob>((resolve, reject) => {
      renderer.domElement.toBlob(
        (blob) => blob ? resolve(blob) : reject(new ViewerRendererError("VIEWER_RENDERER_INITIALIZATION_FAILED", "The current view could not be exported.")),
        "image/png",
      );
    });
  };

  return {
    resetCamera,
    setCellVisible(visible) { cellLines.visible = visible; render(); },
    setBondsVisible(visible) { bondLines.visible = visible; render(); },
    setSelection,
    keyboardCamera,
    exportPng,
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
      renderer.domElement.removeEventListener("pointerdown", onPointerDown);
      renderer.domElement.removeEventListener("pointerup", onPointerUp);
      renderer.domElement.removeEventListener("pointercancel", onPointerCancel);
      sphereGeometry.dispose();
      bondGeometry.dispose();
      cellGeometry.dispose();
      measurementGeometry.dispose();
      bondMaterial.dispose();
      cellMaterial.dispose();
      measurementMaterial.dispose();
      for (const material of highlightMaterials) material.dispose();
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
