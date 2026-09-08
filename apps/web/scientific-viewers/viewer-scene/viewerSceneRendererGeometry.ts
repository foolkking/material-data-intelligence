import type { RenderBond, RenderVector3, ValidatedRenderScene } from "./viewerSceneRendererTypes";

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

export function latticeCorners(matrix: ValidatedRenderScene["lattice"]["matrix"]): readonly RenderVector3[] {
  const [a, b, c] = matrix;
  return Object.freeze([
    vector(0, 0, 0), a, b, c,
    add(a, b), add(a, c), add(b, c), add(add(a, b), c),
  ]);
}

export function latticeEdges(matrix: ValidatedRenderScene["lattice"]["matrix"]): readonly (readonly [RenderVector3, RenderVector3])[] {
  const corners = latticeCorners(matrix);
  const pairs = [[0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 4], [2, 6], [3, 5], [3, 6], [4, 7], [5, 7], [6, 7]] as const;
  return Object.freeze(pairs.map(([from, to]) => Object.freeze([corners[from], corners[to]] as const)));
}

export function bondMetrics(bond: RenderBond) {
  const delta = subtract(bond.end, bond.start);
  const length = Math.hypot(...delta);
  return Object.freeze({ midpoint: scale(add(bond.start, bond.end), 0.5), direction: length > 0 ? scale(delta, 1 / length) : vector(0, 0, 0), length });
}

export function sceneBounds(scene: ValidatedRenderScene): SceneBounds {
  const points = [...scene.atoms.map((atom) => atom.position), ...latticeCorners(scene.lattice.matrix)];
  const min = vector(Math.min(...points.map((point) => point[0])), Math.min(...points.map((point) => point[1])), Math.min(...points.map((point) => point[2])));
  const max = vector(Math.max(...points.map((point) => point[0])), Math.max(...points.map((point) => point[1])), Math.max(...points.map((point) => point[2])));
  const center = scale(add(min, max), 0.5);
  const radius = Math.max(0.5, ...points.map((point) => Math.hypot(...subtract(point, center))));
  return Object.freeze({ min, max, center, radius });
}

export function cameraFrame(scene: ValidatedRenderScene): CameraFrame {
  const bounds = sceneBounds(scene);
  const distance = Math.max(4, bounds.radius * 3.2);
  const direction = normalize(vector(1.15, 0.9, 0.78));
  return Object.freeze({
    position: add(bounds.center, scale(direction, distance)),
    target: bounds.center,
    near: Math.max(0.01, distance / 100),
    far: Math.max(100, distance + bounds.radius * 12),
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
