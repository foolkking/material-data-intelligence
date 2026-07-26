import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

import { domainBasis } from "./volumetricSliceModel";
import { sliceRgba } from "./volumetricSliceDisplay";
import type { ValidatedVolumetricGrid, VolumeTransferFunction, VolumeVector3, VolumetricSlice, VolumetricStructureOverlay } from "./volumetricViewerTypes";

export type VolumetricSliceRendererEngine = Readonly<{
  resetCamera: () => void;
  setStructureVisible: (visible: boolean) => void;
  setCellVisible: (visible: boolean) => void;
  render: () => void;
  exportPng: () => Promise<Blob>;
  dispose: () => void;
}>;

export async function createVolumetricSliceRendererEngine(args: Readonly<{
  container: HTMLDivElement;
  grid: ValidatedVolumetricGrid;
  slice: VolumetricSlice;
  transferFunction: VolumeTransferFunction;
  overlay: VolumetricStructureOverlay | null;
  onProbe: (uv: readonly [number, number]) => void;
  onContextLost: () => void;
}>): Promise<VolumetricSliceRendererEngine> {
  const { container, slice } = args;
  container.querySelectorAll("canvas").forEach((canvas) => canvas.remove());
  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, preserveDrawingBuffer: true });
  renderer.setClearColor(0xf7f9fb, 1);
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  const width = Math.max(320, container.clientWidth || 720); const height = Math.max(320, Math.min(620, container.clientHeight || 500)); renderer.setSize(width, height, false);
  renderer.domElement.dataset.testid = "volumetric-slice-3d-canvas"; renderer.domElement.setAttribute("aria-label", "Three-dimensional canonical lattice slice plane"); renderer.domElement.setAttribute("role", "img"); container.appendChild(renderer.domElement);
  const scene = new THREE.Scene(); const camera = new THREE.PerspectiveCamera(42, width / height, 0.01, 10000); const controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping = false;
  const resources: Array<{ dispose: () => void }> = [];
  const rgba = sliceRgba(slice, args.transferFunction); const texture = new THREE.DataTexture(rgba, slice.outputShape[1], slice.outputShape[0], THREE.RGBAFormat, THREE.UnsignedByteType); texture.needsUpdate = true; texture.magFilter = THREE.LinearFilter; texture.minFilter = THREE.LinearFilter; texture.flipY = true; resources.push(texture);
  const { origin, basisU, basisV } = slice.plane; const corners: VolumeVector3[] = [origin, add(origin, basisU), add(add(origin, basisU), basisV), add(origin, basisV)];
  const geometry = new THREE.BufferGeometry(); geometry.setAttribute("position", new THREE.Float32BufferAttribute(corners.flatMap((point) => [...point]), 3)); geometry.setAttribute("uv", new THREE.Float32BufferAttribute([0,0,1,0,1,1,0,1],2)); geometry.setIndex([0,1,2,0,2,3]); resources.push(geometry);
  const material = new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide, transparent: false }); resources.push(material); const plane = new THREE.Mesh(geometry, material); plane.name = "canonical-lattice-slice"; scene.add(plane);
  const structureGroup = new THREE.Group(); scene.add(structureGroup); addOverlay(structureGroup, args.overlay, resources);
  const cell = addCell(structureGroup, args.grid, resources);
  const markerGeometry = new THREE.SphereGeometry(Math.max(0.04, Math.min(length(slice.plane.basisU), length(slice.plane.basisV)) * 0.018), 16, 10);
  const markerMaterial = new THREE.MeshBasicMaterial({ color: 0xffd447, depthTest: false });
  const marker = new THREE.Mesh(markerGeometry, markerMaterial); marker.visible = false; marker.renderOrder = 5; scene.add(marker); resources.push(markerGeometry, markerMaterial);
  const points = [...corners, ...(args.overlay?.atoms.map((atom) => atom.position) ?? [])].map((point) => new THREE.Vector3(...point)); const sphere = new THREE.Box3().setFromPoints(points).getBoundingSphere(new THREE.Sphere()); const radius = Math.max(sphere.radius, 1); const initial = sphere.center.clone().add(new THREE.Vector3(radius * 1.7, radius * 1.45, radius * 1.4)); camera.position.copy(initial); camera.near = Math.max(radius / 100, .01); camera.far = Math.max(radius * 40, 20); controls.target.copy(sphere.center); controls.update();
  scene.add(new THREE.AmbientLight(0xffffff, 1.4)); const light = new THREE.DirectionalLight(0xffffff, 1.8); light.position.copy(initial); scene.add(light);
  let disposed = false; let contextLost = false;
  const render = () => { if (!disposed && !contextLost && document.visibilityState !== "hidden") renderer.render(scene, camera); };
  controls.addEventListener("change", render);
  const pick = (event: PointerEvent) => { const bounds = renderer.domElement.getBoundingClientRect(); if (!bounds.width || !bounds.height) return; const pointer = new THREE.Vector2(((event.clientX - bounds.left) / bounds.width) * 2 - 1, -((event.clientY - bounds.top) / bounds.height) * 2 + 1); const ray = new THREE.Raycaster(); ray.setFromCamera(pointer, camera); const hit = ray.intersectObject(plane, false)[0]; if (hit?.uv) { marker.position.copy(hit.point); marker.visible = true; args.onProbe(Object.freeze([hit.uv.x, hit.uv.y])); render(); } };
  renderer.domElement.addEventListener("pointerup", pick); const onLost = (event: Event) => { event.preventDefault(); contextLost = true; args.onContextLost(); }; renderer.domElement.addEventListener("webglcontextlost", onLost, false);
  const resize = () => { if (disposed) return; const nextWidth = Math.max(320, container.clientWidth || width), nextHeight = Math.max(320, Math.min(620, container.clientHeight || height)); camera.aspect = nextWidth / nextHeight; camera.updateProjectionMatrix(); renderer.setSize(nextWidth, nextHeight, false); render(); }; const observer = typeof ResizeObserver === "function" ? new ResizeObserver(resize) : null; observer?.observe(container); window.addEventListener("resize", resize); render();
  return Object.freeze({
    resetCamera: () => { camera.position.copy(initial); controls.target.copy(sphere.center); controls.update(); render(); },
    setStructureVisible: (visible) => { structureGroup.visible = visible; render(); },
    setCellVisible: (visible) => { cell.visible = visible; render(); },
    render,
    exportPng: () => new Promise<Blob>((resolve, reject) => { render(); renderer.domElement.toBlob((blob) => blob ? resolve(blob) : reject(new Error("blob")), "image/png"); }),
    dispose: () => { if (disposed) return; disposed = true; observer?.disconnect(); window.removeEventListener("resize", resize); renderer.domElement.removeEventListener("pointerup", pick); renderer.domElement.removeEventListener("webglcontextlost", onLost); controls.removeEventListener("change", render); controls.dispose(); resources.forEach((resource) => resource.dispose()); renderer.dispose(); renderer.domElement.remove(); },
  });
}

function addOverlay(group: THREE.Group, overlay: VolumetricStructureOverlay | null, resources: Array<{ dispose: () => void }>) { if (!overlay?.atoms.length) return; const geometry = new THREE.SphereGeometry(1, 10, 7); resources.push(geometry); const bySpecies = new Map<string, typeof overlay.atoms>(); for (const atom of overlay.atoms) bySpecies.set(atom.species, [...(bySpecies.get(atom.species) ?? []), atom]); for (const atoms of bySpecies.values()) { const material = new THREE.MeshStandardMaterial({ color: atoms[0].color, roughness: .55 }); resources.push(material); const mesh = new THREE.InstancedMesh(geometry, material, atoms.length); const matrix = new THREE.Matrix4(); atoms.forEach((atom, index) => { matrix.makeScale(atom.radius, atom.radius, atom.radius); matrix.setPosition(...atom.position); mesh.setMatrixAt(index, matrix); }); group.add(mesh); } }
function addCell(group: THREE.Group, grid: ValidatedVolumetricGrid, resources: Array<{ dispose: () => void }>): THREE.LineSegments { const basis = domainBasis(grid), origin = grid.origin; const corners = [origin, add(origin, basis[0]), add(add(origin, basis[0]), basis[1]), add(origin, basis[1]), add(origin, basis[2]), add(add(origin, basis[0]), basis[2]), add(add(add(origin, basis[0]), basis[1]), basis[2]), add(add(origin, basis[1]), basis[2])]; const edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]; const geometry = new THREE.BufferGeometry(); geometry.setAttribute("position", new THREE.Float32BufferAttribute(edges.flatMap(([a,b]) => [...corners[a], ...corners[b]]), 3)); const material = new THREE.LineBasicMaterial({ color: 0x176b82, transparent: true, opacity: 0.9 }); resources.push(geometry, material); const cell = new THREE.LineSegments(geometry, material); group.add(cell); return cell; }
function length(value: VolumeVector3): number { return Math.hypot(value[0], value[1], value[2]); }
function add(a: VolumeVector3, b: VolumeVector3): VolumeVector3 { return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]; }
