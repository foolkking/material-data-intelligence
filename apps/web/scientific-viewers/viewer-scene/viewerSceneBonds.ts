import * as THREE from "three";

import { ViewerRendererError } from "./viewerSceneRendererErrors";
import type { ValidatedRenderScene } from "./viewerSceneRendererTypes";

type BondScene = Pick<ValidatedRenderScene, "atoms" | "bonds">;

/** Solid, element-colored connections; this changes display geometry only. */
export function createBondSticks(scene: BondScene, material: THREE.MeshStandardMaterial) {
  const geometry = new THREE.CylinderGeometry(1, 1, 1, 10, 1);
  const mesh = new THREE.InstancedMesh(geometry, material, Math.max(1, scene.bonds.length * 2));
  mesh.count = scene.bonds.length * 2;
  mesh.name = "bounded-scene-connections";
  updateBondSticks(mesh, scene);
  return mesh;
}

export function updateBondSticks(mesh: THREE.InstancedMesh, scene: BondScene) {
  if (mesh.count !== scene.bonds.length * 2) {
    throw new ViewerRendererError("VIEWER_RENDERER_INVALID_GEOMETRY", "Connection topology changed across frames.");
  }
  // Periodic copies share the canonical element color and display radius.
  const atoms = new Map(scene.atoms.map(atom => [atom.siteIndex, atom] as const));
  const up = new THREE.Vector3(0, 1, 0);
  const start = new THREE.Vector3();
  const end = new THREE.Vector3();
  const direction = new THREE.Vector3();
  const center = new THREE.Vector3();
  const rotation = new THREE.Quaternion();
  const transform = new THREE.Matrix4();
  const scale = new THREE.Vector3();
  const color = new THREE.Color();
  scene.bonds.forEach((bond, index) => {
    start.set(...bond.start);
    end.set(...bond.end);
    direction.subVectors(end, start);
    const length = direction.length();
    if (!Number.isFinite(length) || length <= 0) {
      throw new ViewerRendererError("VIEWER_RENDERER_INVALID_GEOMETRY", "A connection has invalid endpoints.");
    }
    const from = atoms.get(bond.fromSiteIndex);
    const to = atoms.get(bond.toSiteIndex);
    if (!from || !to) {
      throw new ViewerRendererError("VIEWER_RENDERER_INVALID_GEOMETRY", "A connection is missing its source atoms.");
    }
    // Keep sticks legible beside small H atoms and unobtrusive in dense cells.
    const radius = Math.min(0.12, Math.max(0.04, Math.min(from.radius, to.radius) * 0.18));
    rotation.setFromUnitVectors(up, direction.divideScalar(length));
    scale.set(radius, length / 2, radius);
    for (const half of [0, 1]) {
      center.lerpVectors(start, end, half === 0 ? 0.25 : 0.75);
      transform.compose(center, rotation, scale);
      mesh.setMatrixAt(index * 2 + half, transform);
      mesh.setColorAt(index * 2 + half, color.set(half === 0 ? from.color : to.color));
    }
  });
  mesh.instanceMatrix.needsUpdate = true;
  if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  mesh.computeBoundingBox();
  mesh.computeBoundingSphere();
  mesh.userData = { bondIds: scene.bonds.map(bond => bond.id) };
}
