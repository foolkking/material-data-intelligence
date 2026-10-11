import { describe, expect, it } from "vitest";
import * as THREE from "three";

import manifest from "../../../../tests/fixtures/brillouin_zone_v1/simple_cubic/manifest.json";
import reciprocal from "../../../../tests/fixtures/brillouin_zone_v1/simple_cubic/reciprocal_lattice.json";
import zone from "../../../../tests/fixtures/brillouin_zone_v1/simple_cubic/brillouin_zone.json";
import kpath from "../../../../tests/fixtures/brillouin_zone_v1/simple_cubic/kpath.json";
import { fitScientificCamera } from "../viewer-scene/scientificCamera";
import { brillouinZoneBounds } from "./brillouinZoneBounds";
import { mapBrillouinZoneArtifacts } from "./brillouinZoneMapper";

const mapped = mapBrillouinZoneArtifacts({ manifest, reciprocal, zone, kpath });
if (!mapped.ok) throw new Error("Invalid canonical test fixture");
const scene = mapped.scene;

describe("Brillouin zone framing", () => {
  it.each([0.3, 0.75, 1, 2])("fits saved geometry, path points and full reciprocal axes at aspect %s", aspect => {
    const bounds = brillouinZoneBounds(scene);
    const positions = [...scene.vertices.map(item => item.cartesian), ...scene.points.map(item => item.cartesian), ...scene.reciprocalMatrix];
    for (const camera of [new THREE.PerspectiveCamera(42), new THREE.OrthographicCamera()]) {
      camera.up.set(0, 0, 1);
      fitScientificCamera(camera, bounds, aspect, new THREE.Vector3(1, 1, 1));
      camera.updateMatrixWorld();
      for (const position of positions) {
        const projected = new THREE.Vector3(...position).multiplyScalar(scene.visualScale).project(camera);
        expect(Math.abs(projected.x)).toBeLessThan(1);
        expect(Math.abs(projected.y)).toBeLessThan(1);
        expect(Math.abs(projected.z)).toBeLessThan(1);
      }
    }
  });

  it("includes saved path endpoints outside the zone without changing scientific coordinates", () => {
    const changed = { ...scene, segments: [{ ...scene.segments[0], end: [10, -5, 2] as const }] };
    const original = JSON.stringify(changed);
    const bounds = brillouinZoneBounds(changed);
    expect(bounds.containsPoint(new THREE.Vector3(10, -5, 2).multiplyScalar(scene.visualScale))).toBe(true);
    expect(JSON.stringify(changed)).toBe(original);
  });
});
