import * as THREE from "three";

import { latticeCorners } from "../viewer-scene/viewerSceneRendererGeometry";
import { domainBasis } from "./volumetricSliceModel";
import type { IsosurfaceMesh, ValidatedVolumetricGrid, VolumeVector3, VolumetricStructureOverlay } from "./volumetricViewerTypes";

export function volumetricRenderBounds(grid: ValidatedVolumetricGrid, overlay: VolumetricStructureOverlay | null, meshes: readonly IsosurfaceMesh[] = [], points: readonly VolumeVector3[] = []): THREE.Sphere {
  const box = new THREE.Box3();
  const point = new THREE.Vector3();
  // Include all affine-domain corners: two opposite corners are insufficient for skew cells.
  for (const corner of latticeCorners(domainBasis(grid))) box.expandByPoint(point.set(...corner).add(new THREE.Vector3(...grid.origin)));
  if (overlay?.lattice) for (const corner of latticeCorners(overlay.lattice)) box.expandByPoint(point.set(...corner).add(new THREE.Vector3(...grid.origin)));
  for (const atom of overlay?.atoms ?? []) {
    box.expandByPoint(point.set(...atom.position).addScalar(atom.radius));
    box.expandByPoint(point.set(...atom.position).addScalar(-atom.radius));
  }
  for (const mesh of meshes) for (let index = 0; index < mesh.positions.length; index += 3) box.expandByPoint(point.fromArray(mesh.positions, index));
  for (const value of points) box.expandByPoint(point.set(...value));
  return box.getBoundingSphere(new THREE.Sphere());
}

// Periodic neighbor bonds may end outside the displayed replicas. Draw only
// saved segments whose two endpoints have rendered atoms; never invent bonds.
export function displayedOverlayBonds(overlay: VolumetricStructureOverlay): VolumetricStructureOverlay["bonds"] {
  const tolerance = 1e-6;
  const buckets = new Map<string, VolumeVector3[]>();
  const cell = (point: VolumeVector3) => point.map(value => Math.floor(value / tolerance));
  for (const atom of overlay.atoms) {
    const key = cell(atom.position).join(":");
    const bucket = buckets.get(key) ?? [];
    bucket.push(atom.position);
    buckets.set(key, bucket);
  }
  const hasAtom = (point: VolumeVector3) => {
    const [x, y, z] = cell(point);
    for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) for (let k = -1; k <= 1; k++) {
      if (buckets.get(`${x + i}:${y + j}:${z + k}`)?.some(atom => Math.hypot(atom[0] - point[0], atom[1] - point[1], atom[2] - point[2]) <= tolerance)) return true;
    }
    return false;
  };
  return overlay.bonds.filter(bond => hasAtom(bond.start) && hasAtom(bond.end));
}
