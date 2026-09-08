import type { BZVector3 } from "./brillouinZoneTypes";

export const BZ_TRIANGLE_CAP = 512;

export type BZTriangulation = Readonly<{
  indices: readonly number[];
  triangleCount: number;
  area: number;
}>;

export function triangulateFace(vertices: readonly BZVector3[], normal: BZVector3, expectedArea: number, tolerance = 1e-7): BZTriangulation {
  if (vertices.length < 3 || vertices.length > 64 || !finiteVector(normal) || !Number.isFinite(expectedArea) || expectedArea <= 0) throw new Error("BZ_FACE_INVALID");
  const normalLength = length(normal);
  if (normalLength < 1e-12) throw new Error("BZ_FACE_NORMAL_INVALID");
  const n = scale(normal, 1 / normalLength);
  const origin = vertices[0];
  const seed = Math.abs(n[0]) < 0.8 ? ([1, 0, 0] as const) : ([0, 1, 0] as const);
  const u = normalize(cross(seed, n));
  const v = cross(n, u);
  const projected = vertices.map((point) => {
    if (!finiteVector(point) || Math.abs(dot(subtract(point, origin), n)) > tolerance) throw new Error("BZ_FACE_NON_COPLANAR");
    const relative = subtract(point, origin);
    return [dot(relative, u), dot(relative, v)] as const;
  });
  const signedArea = polygonArea(projected);
  if (!Number.isFinite(signedArea) || signedArea <= tolerance) throw new Error(signedArea < 0 ? "BZ_FACE_WINDING_INVALID" : "BZ_FACE_DEGENERATE");
  const indices: number[] = [];
  for (let index = 1; index < vertices.length - 1; index += 1) indices.push(0, index, index + 1);
  if (indices.length / 3 > BZ_TRIANGLE_CAP) throw new Error("BZ_TRIANGLE_CAP_EXCEEDED");
  let triangleArea = 0;
  for (let index = 0; index < indices.length; index += 3) {
    const a = vertices[indices[index]];
    const b = vertices[indices[index + 1]];
    const c = vertices[indices[index + 2]];
    const area = length(cross(subtract(b, a), subtract(c, a))) / 2;
    if (!Number.isFinite(area) || area <= tolerance) throw new Error("BZ_TRIANGLE_DEGENERATE");
    triangleArea += area;
  }
  const allowed = Math.max(tolerance, Math.abs(expectedArea) * 1e-7);
  if (Math.abs(triangleArea - expectedArea) > allowed) throw new Error("BZ_FACE_AREA_MISMATCH");
  return Object.freeze({ indices: Object.freeze(indices), triangleCount: indices.length / 3, area: triangleArea });
}

function polygonArea(points: readonly (readonly [number, number])[]) {
  let sum = 0;
  for (let index = 0; index < points.length; index += 1) {
    const current = points[index];
    const next = points[(index + 1) % points.length];
    sum += current[0] * next[1] - next[0] * current[1];
  }
  return sum / 2;
}

function finiteVector(value: readonly number[]): value is BZVector3 {
  return value.length === 3 && value.every((item) => Number.isFinite(item));
}

function subtract(left: BZVector3, right: BZVector3): BZVector3 { return [left[0] - right[0], left[1] - right[1], left[2] - right[2]]; }
function scale(value: BZVector3, factor: number): BZVector3 { return [value[0] * factor, value[1] * factor, value[2] * factor]; }
function dot(left: BZVector3, right: BZVector3) { return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]; }
function cross(left: BZVector3, right: BZVector3): BZVector3 { return [left[1] * right[2] - left[2] * right[1], left[2] * right[0] - left[0] * right[2], left[0] * right[1] - left[1] * right[0]]; }
function length(value: BZVector3) { return Math.hypot(value[0], value[1], value[2]); }
function normalize(value: BZVector3): BZVector3 { const magnitude = length(value); if (magnitude < 1e-12) throw new Error("BZ_FACE_NORMAL_INVALID"); return scale(value, 1 / magnitude); }
