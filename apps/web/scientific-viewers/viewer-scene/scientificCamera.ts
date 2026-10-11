import * as THREE from "three";
import type { OrbitControls } from "three/addons/controls/OrbitControls.js";

// Leave a small margin around the full scientific object, including atom radii.
const FIT_MARGIN = 1.12;

export function perspectiveFitDistance(radius: number, aspect: number, fov = 42): number {
  const vertical = THREE.MathUtils.degToRad(fov) / 2;
  const horizontal = Math.atan(Math.tan(vertical) * Math.max(aspect, 1e-6));
  return Math.max(radius, 0.01) * FIT_MARGIN / Math.sin(Math.min(vertical, horizontal));
}

export function fitScientificCamera(
  camera: THREE.PerspectiveCamera | THREE.OrthographicCamera,
  sphere: THREE.Sphere,
  aspect: number,
  direction: THREE.Vector3,
): void {
  const radius = Math.max(sphere.radius, 0.01);
  const distance = perspectiveFitDistance(radius, aspect, camera instanceof THREE.PerspectiveCamera ? camera.fov : 42);
  camera.position.copy(sphere.center).addScaledVector(direction.clone().normalize(), distance);
  camera.zoom = 1;
  camera.near = Math.max(radius / 1000, 0.0001);
  camera.far = Math.max(distance + radius * 20, 100);
  if (camera instanceof THREE.OrthographicCamera) {
    const halfHeight = radius * FIT_MARGIN / Math.min(aspect, 1);
    camera.top = halfHeight;
    camera.bottom = -halfHeight;
  }
  resizeScientificCamera(camera, aspect);
  camera.lookAt(sphere.center);
}

// Resizing preserves the chosen position, target and zoom after user input.
export function resizeScientificCamera(camera: THREE.PerspectiveCamera | THREE.OrthographicCamera, aspect: number): void {
  if (camera instanceof THREE.PerspectiveCamera) camera.aspect = aspect;
  else {
    const halfHeight = (camera.top - camera.bottom) / 2;
    camera.left = -halfHeight * aspect;
    camera.right = halfHeight * aspect;
  }
  camera.updateProjectionMatrix();
}

export function cloneScientificExportCamera(camera: THREE.PerspectiveCamera | THREE.OrthographicCamera, sourceAspect: number, outputAspect: number): THREE.PerspectiveCamera | THREE.OrthographicCamera {
  const copy = camera.clone();
  copy.zoom /= Math.max(1, sourceAspect / outputAspect);
  resizeScientificCamera(copy, outputAspect);
  copy.updateMatrixWorld();
  return copy;
}

export function copyScientificCameraView(previous: THREE.PerspectiveCamera | THREE.OrthographicCamera, next: THREE.PerspectiveCamera | THREE.OrthographicCamera, target: THREE.Vector3, aspect: number): void {
  next.position.copy(previous.position);
  next.up.copy(previous.up);
  next.near = previous.near;
  next.far = previous.far;
  next.zoom = 1;
  const distance = previous.position.distanceTo(target);
  const halfHeight = previous instanceof THREE.PerspectiveCamera
    ? distance * Math.tan(THREE.MathUtils.degToRad(previous.fov) / 2) / previous.zoom
    : (previous.top - previous.bottom) / 2 / previous.zoom;
  if (next instanceof THREE.OrthographicCamera) {
    next.top = halfHeight;
    next.bottom = -halfHeight;
  } else {
    next.position.sub(target).setLength(halfHeight / Math.tan(THREE.MathUtils.degToRad(next.fov) / 2)).add(target);
  }
  resizeScientificCamera(next, aspect);
  next.lookAt(target);
}

export function trackInitialCameraFit(controls: OrbitControls, fit: () => void) {
  let pristine = true;
  const markInteracted = () => { pristine = false; };
  controls.addEventListener("start", markInteracted);
  return {
    markInteracted,
    resize: () => { if (pristine) fit(); },
    dispose: () => controls.removeEventListener("start", markInteracted),
  };
}

export function createAtomSphereGeometry(atomCount: number): THREE.SphereGeometry {
  return atomCount <= 256 ? new THREE.SphereGeometry(1, 48, 32) : new THREE.SphereGeometry(1, 20, 14);
}
