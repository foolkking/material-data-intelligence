import * as THREE from "three";

import type { BZScene } from "./brillouinZoneTypes";

export function brillouinZoneBounds(scene: BZScene): THREE.Sphere {
  const box = new THREE.Box3().expandByPoint(new THREE.Vector3());
  const point = new THREE.Vector3();
  // Axes and saved paths can extend beyond the zone itself.
  for (const value of [
    ...scene.vertices.map(vertex => vertex.cartesian),
    ...scene.points.map(item => item.cartesian),
    ...scene.reciprocalMatrix,
    ...scene.segments.flatMap(segment => [segment.start, segment.end]),
  ]) box.expandByPoint(point.set(...value).multiplyScalar(scene.visualScale));
  return box.expandByScalar(0.11).getBoundingSphere(new THREE.Sphere());
}
