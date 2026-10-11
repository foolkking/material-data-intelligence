import { describe, expect, it } from "vitest";
import * as THREE from "three";

import { createBondSticks, updateBondSticks } from "./viewerSceneBonds";
import type { RenderAtom, RenderBond, RenderVector3 } from "./viewerSceneRendererTypes";

function connection(end: RenderVector3) {
  const atoms: RenderAtom[] = ["O", "H"].map((element, index) => ({
    id: `atom-${index}`, siteIndex: index, ref: { siteIndex: index, imageOffset: [0, 0, 0] },
    species: element, element, label: `${element}${index + 1}`, occupancy: 1,
    position: index ? end : [0, 0, 0], canonicalPosition: index ? end : [0, 0, 0],
    fractionalPosition: null, radius: index ? 0.14 : 0.30, color: index ? "#ffffff" : "#ff0d0d",
  }));
  const bond: RenderBond = {
    id: "candidate", fromSiteIndex: 0, toSiteIndex: 1, fromRef: atoms[0].ref, toRef: atoms[1].ref,
    start: [0, 0, 0], end, displacementCartesian: end, distanceAngstrom: Math.hypot(...end),
    source: "distance_cutoff", authoritative: false,
  };
  return { atoms, bonds: [bond] };
}

describe("solid structure connections", () => {
  it.each<RenderVector3>([[2, 0, 0], [0, -2, 0], [-1, 2, 3]])("keeps exact endpoints and element colors for %j", (...coordinates) => {
    const scene = connection(coordinates as unknown as RenderVector3);
    const before = JSON.stringify(scene);
    const material = new THREE.MeshStandardMaterial();
    const mesh = createBondSticks(scene, material);
    expect(mesh.count).toBe(2);
    const matrix = new THREE.Matrix4();
    for (const half of [0, 1]) {
      mesh.getMatrixAt(half, matrix);
      for (const [axisPosition, fraction] of [[-0.5, half / 2], [0.5, (half + 1) / 2]]) {
        const actual = new THREE.Vector3(0, axisPosition, 0).applyMatrix4(matrix);
        actual.toArray().forEach((value, axis) => expect(value).toBeCloseTo(coordinates[axis] * fraction, 6));
      }
      const color = new THREE.Color();
      mesh.getColorAt(half, color);
      expect(color.getHexString()).toBe(half ? "ffffff" : "ff0d0d");
    }
    expect(JSON.stringify(scene)).toBe(before);
    mesh.geometry.dispose(); mesh.dispose(); material.dispose();
  });

  it("picks both colored halves as the same connection and follows frame updates", () => {
    const material = new THREE.MeshStandardMaterial();
    const mesh = createBondSticks(connection([2, 0, 0]), material);
    mesh.updateMatrixWorld();
    for (const x of [0.5, 1.5]) {
      const hit = new THREE.Raycaster(new THREE.Vector3(x, 0, 5), new THREE.Vector3(0, 0, -1)).intersectObject(mesh)[0];
      expect(hit?.instanceId).toBeDefined();
      expect(mesh.userData.bondIds[Math.floor(hit.instanceId! / 2)]).toBe("candidate");
    }
    updateBondSticks(mesh, connection([0, 2, 0]));
    const oldHit = new THREE.Raycaster(new THREE.Vector3(1.5, 0, 5), new THREE.Vector3(0, 0, -1)).intersectObject(mesh);
    const newHit = new THREE.Raycaster(new THREE.Vector3(0, 1.5, 5), new THREE.Vector3(0, 0, -1)).intersectObject(mesh);
    expect(oldHit).toHaveLength(0);
    expect(newHit[0]?.instanceId).toBe(1);
    expect(() => updateBondSticks(mesh, { atoms: [], bonds: [] })).toThrow("topology changed");
    mesh.geometry.dispose(); mesh.dispose(); material.dispose();
  });

  it("does not invent geometry for atom-only scenes", () => {
    const material = new THREE.MeshStandardMaterial();
    const mesh = createBondSticks({ atoms: [], bonds: [] }, material);
    expect(mesh.count).toBe(0);
    expect(mesh.userData.bondIds).toEqual([]);
    mesh.geometry.dispose(); mesh.dispose(); material.dispose();
  });
});
