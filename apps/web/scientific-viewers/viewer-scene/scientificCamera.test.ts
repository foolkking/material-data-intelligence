import { describe, expect, it, vi } from "vitest";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

import { cloneScientificExportCamera, copyScientificCameraView, fitScientificCamera, resizeScientificCamera, trackInitialCameraFit } from "./scientificCamera";

describe("scientific camera framing", () => {
  it("preserves the full original viewport and leaves both camera types unchanged during export", () => {
    for (const source of [new THREE.PerspectiveCamera(42),new THREE.OrthographicCamera()]) {
      fitScientificCamera(source,new THREE.Sphere(new THREE.Vector3(1,2,3),4),3,new THREE.Vector3(1,1,1));
      source.zoom=1.4;source.updateProjectionMatrix();source.updateMatrixWorld();
      const original=source.toJSON();
      const copy=cloneScientificExportCamera(source,3,4/3);
      expect(source.toJSON()).toEqual(original);
      expect(copy.position.toArray()).toEqual(source.position.toArray());
      expect(copy.quaternion.toArray()).toEqual(source.quaternion.toArray());
      for(const x of [-1,1])for(const y of [-1,1]){
        const corner=new THREE.Vector3(x,y,0).unproject(source).project(copy);
        expect(Math.abs(corner.x)).toBeLessThanOrEqual(1+1e-10);
        expect(Math.abs(corner.y)).toBeLessThanOrEqual(1+1e-10);
      }
    }
  });
  it.each([0.18, 0.55, 1, 1.6, 3])("fits the entire object at aspect %s in both projections", aspect => {
    const sphere = new THREE.Sphere(new THREE.Vector3(8, -5, 12), 7);
    for (const camera of [new THREE.PerspectiveCamera(42), new THREE.OrthographicCamera()]) {
      camera.up.set(0, 0, 1);
      fitScientificCamera(camera, sphere, aspect, new THREE.Vector3(1.15, 0.9, 0.78));
      camera.updateMatrixWorld();
      for (let latitude = 0; latitude <= 20; latitude++) for (let longitude = 0; longitude < 40; longitude++) {
        const point = new THREE.Vector3().setFromSphericalCoords(sphere.radius, latitude * Math.PI / 20, longitude * Math.PI / 20).add(sphere.center).project(camera);
        expect(Math.abs(point.x)).toBeLessThan(1);
        expect(Math.abs(point.y)).toBeLessThan(1);
        expect(Math.abs(point.z)).toBeLessThan(1);
      }
    }
  });

  it("retains manual pose and zoom on resize, then fits the current aspect on explicit reset", () => {
    const camera = new THREE.OrthographicCamera();
    const sphere = new THREE.Sphere(new THREE.Vector3(1, 2, 3), 4);
    fitScientificCamera(camera, sphere, 1, new THREE.Vector3(1, 1, 1));
    camera.position.set(12, 13, 14);
    camera.zoom = 2.5;
    camera.lookAt(new THREE.Vector3(-1, 2, 0));
    const quaternion = camera.quaternion.clone();
    resizeScientificCamera(camera, 0.4);
    expect(camera.position.toArray()).toEqual([12, 13, 14]);
    expect(camera.quaternion.equals(quaternion)).toBe(true);
    expect(camera.zoom).toBe(2.5);
    fitScientificCamera(camera, sphere, 0.4, new THREE.Vector3(1, 1, 1));
    expect(camera.zoom).toBe(1);
    expect(camera.right).toBeGreaterThan(sphere.radius);
  });

  it("preserves the target-plane scale and up direction through projection changes after resize", () => {
    const source = new THREE.PerspectiveCamera(42);
    const sphere = new THREE.Sphere(new THREE.Vector3(1, 2, 3), 4);
    source.up.set(0, 0, 1);
    fitScientificCamera(source, sphere, 0.5, new THREE.Vector3(1, 2, 3));
    source.zoom = 2;
    source.updateProjectionMatrix();
    const orthographic = new THREE.OrthographicCamera();
    copyScientificCameraView(source, orthographic, sphere.center, 0.5);
    const restored = new THREE.PerspectiveCamera(42);
    copyScientificCameraView(orthographic, restored, sphere.center, 0.5);
    const point = sphere.center.clone().add(new THREE.Vector3(1, 0, 0).applyQuaternion(source.quaternion));
    const projections = [source, orthographic, restored].map(camera => { camera.updateMatrixWorld(); return point.clone().project(camera); });
    expect(projections[1].x).toBeCloseTo(projections[0].x);
    expect(projections[2].x).toBeCloseTo(projections[0].x);
    expect(orthographic.up.toArray()).toEqual([0, 0, 1]);
    expect(restored.aspect).toBe(0.5);
  });

  it("fits late initial layout but stops automatic fitting after user interaction", () => {
    const controls = new OrbitControls(new THREE.PerspectiveCamera(), document.createElement("canvas"));
    const fit = vi.fn();
    const initial = trackInitialCameraFit(controls, fit);
    initial.resize();
    controls.dispatchEvent({ type: "start" });
    initial.resize();
    initial.resize();
    expect(fit).toHaveBeenCalledTimes(1);
    initial.dispose();
    controls.dispose();
  });
});
