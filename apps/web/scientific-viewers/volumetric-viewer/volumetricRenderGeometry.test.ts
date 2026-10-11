import { describe, expect, it } from "vitest";
import * as THREE from "three";

import { latticeCorners } from "../viewer-scene/viewerSceneRendererGeometry";
import { displayedOverlayBonds, volumetricRenderBounds } from "./volumetricRenderGeometry";
import { deriveVolumetricOverlaySupercell } from "./volumetricOverlaySupercell";
import { domainBasis } from "./volumetricSliceModel";
import type { ValidatedVolumetricGrid, VolumetricStructureOverlay } from "./volumetricViewerTypes";

const grid: ValidatedVolumetricGrid = {
  schemaVersion: "phase10j.volumetric_grid.v1", gridId: "grid", contentHash: "a".repeat(64), shape: [4, 3, 2], origin: [1, 2, 3],
  stepMatrix: [[1, 0, 0], [-2, 1, 0], [0, 0.2, 1]], sampleLocation: "node", boundaryConditions: ["periodic", "periodic", "periodic"], endpointPolicy: "excluded", periodic: true, structureBinding: null,
};
const overlay: VolumetricStructureOverlay = {
  kind: "periodic_viewer_scene", unavailableReason: null, lattice: [[2, 0, 0], [0, 2, 0], [0, 0, 2]],
  atoms: [{ siteIndex: 0, species: "Si", position: [0, 0, 0], radius: 0.5, color: "#ffffff" }, { siteIndex: 1, species: "Si", position: [1, 0, 0], radius: 0.5, color: "#ffffff" }],
  bonds: [{ id: "inside", start: [0, 0, 0], end: [1, 0, 0] }, { id: "periodic", start: [1, 0, 0], end: [2, 0, 0] }],
};

describe("volumetric display geometry", () => {
  it("includes every skew cell corner even when surface extraction is empty", () => {
    const bounds = volumetricRenderBounds(grid, null);
    for (const corner of latticeCorners(domainBasis(grid))) {
      expect(new THREE.Vector3(...corner).add(new THREE.Vector3(...grid.origin)).distanceTo(bounds.center)).toBeLessThanOrEqual(bounds.radius + 1e-12);
    }
  });
  it("includes atom radii and full overlay supercell corners", () => {
    const repeated = deriveVolumetricOverlaySupercell(overlay, 2).overlay!;
    const bounds = volumetricRenderBounds(grid, repeated);
    for (const atom of repeated.atoms) for (const direction of [-1, 1]) {
      expect(bounds.containsPoint(new THREE.Vector3(...atom.position).addScalar(direction * atom.radius))).toBe(true);
    }
    for (const corner of latticeCorners(repeated.lattice!)) expect(bounds.containsPoint(new THREE.Vector3(...corner).add(new THREE.Vector3(...grid.origin)))).toBe(true);
  });
  it("does not draw dangling periodic bonds or modify the saved topology", () => {
    expect(displayedOverlayBonds(overlay).map(bond => bond.id)).toEqual(["inside"]);
    const repeated = deriveVolumetricOverlaySupercell(overlay, 2).overlay!;
    expect(displayedOverlayBonds(repeated)).toHaveLength(12);
    expect(displayedOverlayBonds(repeated).some(bond => bond.id === "periodic@0:0:0")).toBe(true);
    expect(displayedOverlayBonds(repeated).some(bond => bond.id === "periodic@1:0:0")).toBe(false);
    expect(overlay.bonds).toHaveLength(2);
  });
  it("tolerates arithmetic roundoff across spatial buckets without joining distinct atoms", () => {
    const source = { ...overlay, bonds: [{ id: "roundoff", start: [-1e-10, 0, 0], end: [1 + 1e-10, 0, 0] }, { id: "absent", start: [0, 0, 0], end: [1.001, 0, 0] }] };
    expect(displayedOverlayBonds(source).map(bond => bond.id)).toEqual(["roundoff"]);
  });
});
