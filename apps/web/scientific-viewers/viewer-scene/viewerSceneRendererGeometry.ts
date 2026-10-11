import type { RenderBond, RenderVector3, ValidatedRenderScene } from "./viewerSceneRendererTypes";
import { perspectiveFitDistance } from "./scientificCamera";
import { latticeCorners } from "./viewerSceneLatticeGeometry";
export { latticeCorners, latticeEdges } from "./viewerSceneLatticeGeometry";

export type SceneBounds = {
  readonly min: RenderVector3;
  readonly max: RenderVector3;
  readonly center: RenderVector3;
  readonly radius: number;
};

export type CameraFrame = {
  readonly position: RenderVector3;
  readonly target: RenderVector3;
  readonly near: number;
  readonly far: number;
};

export function bondMetrics(bond: RenderBond) {
  const delta = subtract(bond.end, bond.start);
  const length = Math.hypot(...delta);
  return Object.freeze({ midpoint: scale(add(bond.start, bond.end), 0.5), direction: length > 0 ? scale(delta, 1 / length) : vector(0, 0, 0), length });
}

export function sceneBounds(scene: ValidatedRenderScene): SceneBounds {
  const points = [
    ...scene.atoms.flatMap(atom => [vector(...atom.position.map(value => value - atom.radius) as [number, number, number]), vector(...atom.position.map(value => value + atom.radius) as [number, number, number])]),
    ...latticeCorners(scene.lattice.matrix), ...latticeCorners(scene.displayLattice.matrix),
    ...scene.bonds.flatMap(bond => [bond.start, bond.end]),
  ];
  const min = vector(Math.min(...points.map((point) => point[0])), Math.min(...points.map((point) => point[1])), Math.min(...points.map((point) => point[2])));
  const max = vector(Math.max(...points.map((point) => point[0])), Math.max(...points.map((point) => point[1])), Math.max(...points.map((point) => point[2])));
  const center = scale(add(min, max), 0.5);
  const radius = Math.max(0.01, Math.hypot(...subtract(max, min)) / 2);
  return Object.freeze({ min, max, center, radius });
}

export function cameraFrame(scene: ValidatedRenderScene, aspect = 1): CameraFrame {
  const bounds = sceneBounds(scene);
  const distance = perspectiveFitDistance(bounds.radius, aspect);
  const direction = normalize(vector(1.15, 0.9, 0.78));
  return Object.freeze({
    position: add(bounds.center, scale(direction, distance)),
    target: bounds.center,
    near: Math.max(0.01, distance / 100),
    far: Math.max(100, distance * 3, distance + bounds.radius * 12),
  });
}

function normalize(value: RenderVector3): RenderVector3 {
  const length = Math.hypot(...value);
  return length > 0 ? scale(value, 1 / length) : vector(1, 1, 1);
}

function add(left: RenderVector3, right: RenderVector3): RenderVector3 {
  return vector(left[0] + right[0], left[1] + right[1], left[2] + right[2]);
}

function subtract(left: RenderVector3, right: RenderVector3): RenderVector3 {
  return vector(left[0] - right[0], left[1] - right[1], left[2] - right[2]);
}

function scale(value: RenderVector3, scalar: number): RenderVector3 {
  return vector(value[0] * scalar, value[1] * scalar, value[2] * scalar);
}

function vector(x: number, y: number, z: number): RenderVector3 {
  return Object.freeze([x, y, z]);
}
