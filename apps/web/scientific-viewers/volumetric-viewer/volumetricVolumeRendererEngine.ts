import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

import { cloneScientificExportCamera, copyScientificCameraView, createAtomSphereGeometry, fitScientificCamera, resizeScientificCamera, trackInitialCameraFit } from "../viewer-scene/scientificCamera";
import { captureScientificCanvas, createScientificPngExporter } from "../viewer-scene/scientificPngExport";
import { displayedOverlayBonds, volumetricRenderBounds } from "./volumetricRenderGeometry";
import { captureOrbitControlsDisposer } from "../viewer-scene/orbitControlsLifecycle";
import { domainBasis } from "./volumetricSliceModel";
import { affineVolumeClipPlane, inspectVolumeGpuCapabilities } from "./volumetricVolumeModel";
import { validateVolumeShaderProgram, VOLUME_FRAGMENT_SHADER, VOLUME_SHADER_VERSION, VOLUME_VERTEX_SHADER } from "./volumetricVolumeShader";
import type {
  ValidatedVolumetricGrid,
  VolumeGpuCapabilities,
  VolumeQuality,
  VolumeTransferFunction,
  VolumetricStructureOverlay,
  VolumetricVolumeRendererEngine,
  VolumetricVolumeRendererSnapshot,
} from "./volumetricViewerTypes";
import { VOLUMETRIC_BROWSER_CAPS, VolumetricViewerError } from "./volumetricViewerTypes";

export async function createVolumetricVolumeRendererEngine(args: Readonly<{
  container: HTMLDivElement;
  grid: ValidatedVolumetricGrid;
  values: Float32Array;
  transferFunction: VolumeTransferFunction;
  quality: VolumeQuality;
  overlay: VolumetricStructureOverlay | null;
  capabilityOverride?: "supported" | "unsupported";
  onContextLost: () => void;
}>): Promise<Readonly<{ engine: VolumetricVolumeRendererEngine; capabilities: VolumeGpuCapabilities; shaderVersion: typeof VOLUME_SHADER_VERSION }>> {
  const { container, grid } = args;
  if (args.capabilityOverride === "unsupported" || typeof document === "undefined") throw new VolumetricViewerError("VOLUME_VIEWER_WEBGL_UNSUPPORTED", "WebGL2 direct volume rendering is unavailable.");
  container.querySelectorAll("canvas").forEach((canvas) => canvas.remove());
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("webgl2", { alpha: true, antialias: true, depth: true, powerPreference: "high-performance" });
  const mobile = typeof matchMedia === "function" && matchMedia("(max-width: 700px)").matches;
  const capabilities = inspectVolumeGpuCapabilities({ context, shape: grid.shape, mobile });
  if (!capabilities.supported || !context) {
    context?.getExtension("WEBGL_lose_context")?.loseContext();
    throw new VolumetricViewerError("VOLUME_VIEWER_WEBGL_UNSUPPORTED", `Direct volume rendering unavailable: ${capabilities.reason ?? "unknown capability"}.`);
  }
  try {
    validateVolumeShaderProgram(context);
  } catch {
    context.getExtension("WEBGL_lose_context")?.loseContext();
    throw new VolumetricViewerError("VOLUME_VIEWER_RENDERER_FAILED", "The application-owned volume shader failed compile/link validation.");
  }
  const renderer = new THREE.WebGLRenderer({ canvas, context, alpha: true, antialias: true, preserveDrawingBuffer: true });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setClearColor(0xf7f9fb, 1);
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, args.quality.pixelRatioCap, VOLUMETRIC_BROWSER_CAPS.maximumVolumePixelRatio));
  let width = Math.max(1, container.clientWidth || 760);
  let height = Math.max(1, container.clientHeight || 520);
  if (width * height * renderer.getPixelRatio() ** 2 > VOLUMETRIC_BROWSER_CAPS.maximumVolumeRenderPixels) renderer.setPixelRatio(1);
  renderer.setSize(width, height, false);
  renderer.autoClear = false;
  renderer.localClippingEnabled = true;
  renderer.domElement.dataset.testid = "volumetric-volume-canvas";
  renderer.domElement.setAttribute("aria-label", "WebGL2 直接体渲染");
  renderer.domElement.setAttribute("role", "img");
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const basis = domainBasis(grid);
  const transform = affineTransform(grid.origin, basis);
  const inverseTransform = transform.clone().invert();
  const sphere = volumetricRenderBounds(grid, args.overlay);
  const direction = new THREE.Vector3(1.8, 1.55, 1.4);
  const perspectiveCamera = new THREE.PerspectiveCamera(42);
  const orthographicCamera = new THREE.OrthographicCamera();
  let camera: THREE.PerspectiveCamera | THREE.OrthographicCamera = perspectiveCamera;
  let projection: "perspective" | "orthographic" = "perspective";
  fitScientificCamera(camera, sphere, width / height, direction);
  const controls = new OrbitControls<THREE.Camera>(camera, renderer.domElement);
  const disposeControls = captureOrbitControlsDisposer(controls);
  controls.enableDamping = false;
  controls.screenSpacePanning = true;
  controls.target.copy(sphere.center);
  const fit = () => {
    fitScientificCamera(camera, sphere, width / height, direction);
    controls.target.copy(sphere.center);
    controls.update();
  };
  const initialFit = trackInitialCameraFit(controls, fit);

  const texture = new THREE.Data3DTexture(args.values, grid.shape[2], grid.shape[1], grid.shape[0]);
  texture.format = THREE.RedFormat;
  texture.type = THREE.FloatType;
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.wrapS = grid.boundaryConditions[2] === "periodic" ? THREE.RepeatWrapping : THREE.ClampToEdgeWrapping;
  texture.wrapT = grid.boundaryConditions[1] === "periodic" ? THREE.RepeatWrapping : THREE.ClampToEdgeWrapping;
  texture.wrapR = grid.boundaryConditions[0] === "periodic" ? THREE.RepeatWrapping : THREE.ClampToEdgeWrapping;
  texture.unpackAlignment = 1;
  texture.needsUpdate = true;
  const depthTexture = new THREE.DepthTexture(1, 1, THREE.UnsignedIntType);
  depthTexture.minFilter = THREE.NearestFilter;
  depthTexture.magFilter = THREE.NearestFilter;
  const structureDepthTarget = new THREE.WebGLRenderTarget(1, 1, {
    minFilter: THREE.NearestFilter,
    magFilter: THREE.NearestFilter,
    format: THREE.RGBAFormat,
    type: THREE.UnsignedByteType,
    depthBuffer: true,
    stencilBuffer: false,
  });
  structureDepthTarget.depthTexture = depthTexture;

  const uniforms = {
    uVolume: { value: texture },
    uStructureDepth: { value: depthTexture },
    uCameraUnit: { value: new THREE.Vector3() },
    uInverseProjectionView: { value: new THREE.Matrix4() },
    uWorldToVolume: { value: inverseTransform.clone() },
    uDepthViewport: { value: new THREE.Vector2(1, 1) },
    uHasStructureDepth: { value: true },
    uGridShape: { value: new THREE.Vector3(...grid.shape) },
    uWindow: { value: new THREE.Vector2(args.transferFunction.windowLow, args.transferFunction.windowHigh) },
    uOpacityScale: { value: args.transferFunction.opacityScale },
    uSamplesPerVoxel: { value: args.quality.samplesPerVoxel },
    uMaximumSteps: { value: args.quality.maximumRaySteps },
    uPalette: { value: paletteIndex(args.transferFunction.paletteId) },
    uTransparentZero: { value: args.transferFunction.zeroPolicy === "transparent_zero" },
    uClipEnabled: { value: false },
    uClipAxis: { value: 2 },
    uClipOffset: { value: 1 },
  };
  const volumeMaterial = new THREE.RawShaderMaterial({
    glslVersion: THREE.GLSL3,
    vertexShader: VOLUME_VERTEX_SHADER,
    fragmentShader: VOLUME_FRAGMENT_SHADER,
    uniforms,
    side: THREE.FrontSide,
    transparent: true,
    depthTest: true,
    depthWrite: false,
  });
  const volumeGeometry = new THREE.BoxGeometry(1, 1, 1);
  const volumeMesh = new THREE.Mesh(volumeGeometry, volumeMaterial);
  volumeMesh.matrixAutoUpdate = false;
  volumeMesh.matrix.copy(transform);
  volumeMesh.renderOrder = 0;
  scene.add(volumeMesh);

  const structureGroup = new THREE.Group();
  structureGroup.renderOrder = 2;
  scene.add(structureGroup);
  const resources: Array<{ dispose: () => void }> = [];
  const clippableMaterials: Array<THREE.Material & { clippingPlanes: THREE.Plane[] | null }> = [];
  addStructureOverlay(structureGroup, args.overlay, resources, clippableMaterials);
  const cellGroup = new THREE.Group();
  cellGroup.renderOrder = 2;
  scene.add(cellGroup);
  addCell(cellGroup, grid, resources, clippableMaterials);
  const ambient = new THREE.AmbientLight(0xffffff, 1.4);
  const key = new THREE.DirectionalLight(0xffffff, 2.1);
  key.position.copy(camera.position);
  scene.add(ambient, key);

  let disposed = false;
  let contextLost = false;
  let structureVisible = true;
  let cellVisible = true;
  let clippingEnabled = false;
  const sharedClipPlane = new THREE.Plane();
  let quality = args.quality;
  const initialDepthRatio = renderer.getPixelRatio();
  const initialDepthWidth = Math.max(1, Math.floor(width * initialDepthRatio));
  const initialDepthHeight = Math.max(1, Math.floor(height * initialDepthRatio));
  structureDepthTarget.setSize(initialDepthWidth, initialDepthHeight);
  uniforms.uDepthViewport.value.set(initialDepthWidth, initialDepthHeight);
  const snapshot = (): VolumetricVolumeRendererSnapshot => Object.freeze({
    state: contextLost ? "context_lost" : disposed ? "disposed" : "rendered",
    canvasCount: container.querySelectorAll("canvas").length,
    contextCount: disposed ? 0 : 1,
    textureShape: capabilities.textureShape,
    textureBytes: capabilities.textureBytes,
    drawCalls: renderer.info.render.calls,
    rayStepCap: quality.maximumRaySteps,
    structureVisible,
    cellVisible,
    clippingEnabled,
    projection,
    depthPolicy: "structure_depth_prepass",
    depthTargetCount: disposed ? 0 : 1,
    clippingPolicy: "shared_affine_plane",
  });
  const publish = () => { (window as unknown as { __mdiVolumetricVolumeEvidence?: unknown }).__mdiVolumetricVolumeEvidence = { ...snapshot(), shaderVersion: VOLUME_SHADER_VERSION, shaderLinked: true, maximum3dTextureSize: capabilities.maximum3dTextureSize, maximumTextureImageUnits: capabilities.maximumTextureImageUnits, estimatedGpuBytes: capabilities.estimatedGpuBytes }; };
  const render = () => {
    if (disposed || contextLost || document.visibilityState === "hidden") return;
    const cameraUnit = camera.position.clone().applyMatrix4(inverseTransform).addScalar(0.5);
    uniforms.uCameraUnit.value.copy(cameraUnit);
    camera.updateMatrixWorld();
    uniforms.uInverseProjectionView.value.multiplyMatrices(camera.matrixWorld, camera.projectionMatrixInverse);
    const overlayVisible = structureVisible || cellVisible;
    uniforms.uHasStructureDepth.value = overlayVisible;

    volumeMesh.visible = false;
    structureGroup.visible = structureVisible;
    cellGroup.visible = cellVisible;
    renderer.setRenderTarget(structureDepthTarget);
    renderer.clear(true, true, false);
    if (overlayVisible) renderer.render(scene, camera);

    renderer.setRenderTarget(null);
    renderer.clear(true, true, false);
    if (overlayVisible) renderer.render(scene, camera);
    structureGroup.visible = false;
    cellGroup.visible = false;
    volumeMesh.visible = true;
    renderer.render(scene, camera);
    structureGroup.visible = structureVisible;
    cellGroup.visible = cellVisible;
    publish();
  };
  const bindControls = () => controls.addEventListener("change", render);
  bindControls();
  const onLost = (event: Event) => { event.preventDefault(); contextLost = true; args.onContextLost(); publish(); };
  renderer.domElement.addEventListener("webglcontextlost", onLost, false);
  const onVisibility = () => { if (document.visibilityState === "visible") render(); };
  document.addEventListener("visibilitychange", onVisibility);
  const resize = () => {
    if (disposed || !container.clientWidth || !container.clientHeight) return;
    width = container.clientWidth;
    height = container.clientHeight;
    resizeScientificCamera(camera, width / height);
    renderer.setSize(width, height, false);
    initialFit.resize();
    const ratio = renderer.getPixelRatio();
    const depthWidth = Math.max(1, Math.floor(width * ratio));
    const depthHeight = Math.max(1, Math.floor(height * ratio));
    structureDepthTarget.setSize(depthWidth, depthHeight);
    uniforms.uDepthViewport.value.set(depthWidth, depthHeight);
    render();
  };
  const observer = typeof ResizeObserver === "function" ? new ResizeObserver(resize) : null;
  observer?.observe(container);
  window.addEventListener("resize", resize);
  controls.update();
  render();

  const exportImage = createScientificPngExporter(([exportWidth, exportHeight, pixelRatio]: readonly [number, number, number]) => {
    if (!Number.isSafeInteger(exportWidth) || !Number.isSafeInteger(exportHeight) || exportWidth < 256 || exportHeight < 256 || exportWidth > 4096 || exportHeight > 4096 || ![1,2].includes(pixelRatio) || exportWidth * exportHeight * pixelRatio * pixelRatio > VOLUMETRIC_BROWSER_CAPS.maximumExportPixels) throw new VolumetricViewerError("VOLUME_VIEWER_MESH_CAP_EXCEEDED", "PNG export exceeds the bounded pixel budget.");
    if (disposed || contextLost) throw new Error("VIEWER_EXPORT_CONTEXT_UNAVAILABLE");
    const oldSize = renderer.getSize(new THREE.Vector2()), oldRatio = renderer.getPixelRatio(), oldCamera = camera;
    try {
      camera = cloneScientificExportCamera(oldCamera, oldSize.x / oldSize.y, exportWidth / exportHeight);
      renderer.setPixelRatio(pixelRatio); renderer.setSize(exportWidth, exportHeight, false);
      structureDepthTarget.setSize(exportWidth * pixelRatio, exportHeight * pixelRatio);
      uniforms.uDepthViewport.value.set(exportWidth * pixelRatio, exportHeight * pixelRatio);
      render();
      return captureScientificCanvas(renderer.domElement);
    } finally {
      camera = oldCamera;
      renderer.setPixelRatio(oldRatio); renderer.setSize(oldSize.x, oldSize.y, false);
      structureDepthTarget.setSize(Math.floor(oldSize.x * oldRatio), Math.floor(oldSize.y * oldRatio));
      uniforms.uDepthViewport.value.set(Math.floor(oldSize.x * oldRatio), Math.floor(oldSize.y * oldRatio));
      render();
    }
  });
  const engine: VolumetricVolumeRendererEngine = Object.freeze({
    setTransferFunction: (value) => { uniforms.uWindow.value.set(value.windowLow, value.windowHigh); uniforms.uOpacityScale.value = value.opacityScale; uniforms.uPalette.value = paletteIndex(value.paletteId); uniforms.uTransparentZero.value = value.zeroPolicy === "transparent_zero"; render(); },
    setQuality: (value) => { quality = value; uniforms.uSamplesPerVoxel.value = value.samplesPerVoxel; uniforms.uMaximumSteps.value = Math.min(768, value.maximumRaySteps); renderer.setPixelRatio(Math.min(devicePixelRatio || 1, value.pixelRatioCap, VOLUMETRIC_BROWSER_CAPS.maximumVolumePixelRatio)); resize(); },
    setStructureVisible: (visible) => { structureVisible = visible; render(); },
    setCellVisible: (visible) => { cellVisible = visible; render(); },
    setClipping: (enabled, axis, offset) => {
      clippingEnabled = enabled;
      const boundedOffset = Math.min(1, Math.max(0, Number.isFinite(offset) ? offset : 1));
      uniforms.uClipEnabled.value = enabled; uniforms.uClipAxis.value = axis; uniforms.uClipOffset.value = boundedOffset;
      if (enabled) { const plane = affineVolumeClipPlane(grid.origin, basis, axis, boundedOffset); sharedClipPlane.set(new THREE.Vector3(...plane.normal), plane.constant); }
      clippableMaterials.forEach((material) => { material.clippingPlanes = enabled ? [sharedClipPlane] : []; material.needsUpdate = true; });
      render();
    },
    setProjection: (value) => {
      if (value === projection) return;
      const next = value === "orthographic" ? orthographicCamera : perspectiveCamera;
      copyScientificCameraView(camera, next, controls.target, width / height);
      camera = next;
      projection = value;
      controls.object = camera;
      controls.update();
      render();
    },
    resetCamera: () => { fit(); render(); },
    render,
    snapshot,
    exportPng: (width, height, ratio) => exportImage([width,height,ratio]),
    dispose: () => {
      if (disposed) return;
      disposed = true;
      observer?.disconnect(); window.removeEventListener("resize", resize); document.removeEventListener("visibilitychange", onVisibility); renderer.domElement.removeEventListener("webglcontextlost", onLost); controls.removeEventListener("change", render); initialFit.dispose(); disposeControls();
      texture.dispose(); structureDepthTarget.dispose(); volumeGeometry.dispose(); volumeMaterial.dispose(); resources.forEach((resource) => resource.dispose()); renderer.forceContextLoss(); renderer.dispose(); renderer.domElement.remove(); publish();
    },
  });
  return Object.freeze({ engine, capabilities, shaderVersion: VOLUME_SHADER_VERSION });
}

function affineTransform(origin: readonly number[], basis: readonly (readonly number[])[]): THREE.Matrix4 {
  const center = new THREE.Vector3(origin[0], origin[1], origin[2]).add(new THREE.Vector3(...basis[0]).add(new THREE.Vector3(...basis[1])).add(new THREE.Vector3(...basis[2])).multiplyScalar(0.5));
  return new THREE.Matrix4().set(basis[0][0], basis[1][0], basis[2][0], center.x, basis[0][1], basis[1][1], basis[2][1], center.y, basis[0][2], basis[1][2], basis[2][2], center.z, 0, 0, 0, 1);
}
function paletteIndex(value: VolumeTransferFunction["paletteId"]): number { return value === "diverging_blue_red" ? 1 : value === "magma" ? 2 : value === "elf_teal_yellow" ? 3 : 0; }
function addStructureOverlay(group: THREE.Group, overlay: VolumetricStructureOverlay | null, resources: Array<{ dispose: () => void }>, clippableMaterials: Array<THREE.Material & { clippingPlanes: THREE.Plane[] | null }>) {
  if (!overlay?.atoms.length) return;
  const geometry = createAtomSphereGeometry(overlay.atoms.length); resources.push(geometry);
  const bySpecies = new Map<string, typeof overlay.atoms>();
  for (const atom of overlay.atoms) bySpecies.set(atom.species, [...(bySpecies.get(atom.species) ?? []), atom]);
  for (const atoms of bySpecies.values()) {
    const material = new THREE.MeshStandardMaterial({ color: atoms[0].color, roughness: 0.55, metalness: 0.05 }); resources.push(material); clippableMaterials.push(material);
    const mesh = new THREE.InstancedMesh(geometry, material, atoms.length); const matrix = new THREE.Matrix4();
    atoms.forEach((atom, index) => { matrix.makeScale(atom.radius, atom.radius, atom.radius); matrix.setPosition(...atom.position); mesh.setMatrixAt(index, matrix); });
    mesh.renderOrder = 2; group.add(mesh);
  }
  const displayedBonds = displayedOverlayBonds(overlay);
  if (displayedBonds.length) {
    const bondGeometry = new THREE.BufferGeometry(); bondGeometry.setAttribute("position", new THREE.Float32BufferAttribute(displayedBonds.flatMap((bond) => [...bond.start, ...bond.end]), 3)); resources.push(bondGeometry);
    const material = new THREE.LineBasicMaterial({ color: 0x526879, transparent: true, opacity: 0.72 }); resources.push(material); clippableMaterials.push(material); group.add(new THREE.LineSegments(bondGeometry, material));
  }
}
function addCell(group: THREE.Group, grid: ValidatedVolumetricGrid, resources: Array<{ dispose: () => void }>, clippableMaterials: Array<THREE.Material & { clippingPlanes: THREE.Plane[] | null }>): THREE.LineSegments {
  const basis = domainBasis(grid); const origin = grid.origin;
  const corners = [origin, add(origin, basis[0]), add(add(origin, basis[0]), basis[1]), add(origin, basis[1]), add(origin, basis[2]), add(add(origin, basis[0]), basis[2]), add(add(add(origin, basis[0]), basis[1]), basis[2]), add(add(origin, basis[1]), basis[2])];
  const edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];
  const geometry = new THREE.BufferGeometry(); geometry.setAttribute("position", new THREE.Float32BufferAttribute(edges.flatMap(([a,b]) => [...corners[a], ...corners[b]]), 3)); resources.push(geometry);
  const material = new THREE.LineBasicMaterial({ color: 0x176b82, transparent: true, opacity: 0.9 }); resources.push(material); clippableMaterials.push(material); const lines = new THREE.LineSegments(geometry, material); lines.renderOrder = 2; group.add(lines); return lines;
}
function add(a: readonly number[], b: readonly number[]): [number, number, number] { return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]; }
