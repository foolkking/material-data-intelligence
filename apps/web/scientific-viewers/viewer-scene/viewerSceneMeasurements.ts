import type { RenderVector3 } from "./viewerSceneRendererTypes";

export type ViewerMeasurementResult =
  | { readonly kind: "distance"; readonly siteIndices: readonly [number, number]; readonly value: number; readonly unit: "angstrom" }
  | { readonly kind: "angle"; readonly siteIndices: readonly [number, number, number]; readonly value: number; readonly unit: "degree" }
  | { readonly kind: "dihedral"; readonly siteIndices: readonly [number, number, number, number]; readonly value: number; readonly unit: "degree" };

export type ViewerMeasurementEvaluation =
  | { readonly ok: true; readonly result: ViewerMeasurementResult }
  | { readonly ok: false; readonly error: "INVALID_COORDINATE" | "DEGENERATE_MEASUREMENT" };

const EPSILON = 1e-12;

export function measureDistance(indices: readonly [number, number], points: readonly [RenderVector3, RenderVector3]): ViewerMeasurementEvaluation {
  if (!points.every(finitePoint)) return invalid("INVALID_COORDINATE");
  return valid({ kind: "distance", siteIndices: indices, value: length(subtract(points[1], points[0])), unit: "angstrom" });
}

export function measureAngle(indices: readonly [number, number, number], points: readonly [RenderVector3, RenderVector3, RenderVector3]): ViewerMeasurementEvaluation {
  if (!points.every(finitePoint)) return invalid("INVALID_COORDINATE");
  const left = subtract(points[0], points[1]);
  const right = subtract(points[2], points[1]);
  const denominator = length(left) * length(right);
  if (denominator <= EPSILON) return invalid("DEGENERATE_MEASUREMENT");
  const cosine = clamp(dot(left, right) / denominator, -1, 1);
  return valid({ kind: "angle", siteIndices: indices, value: radiansToDegrees(Math.acos(cosine)), unit: "degree" });
}

export function measureDihedral(indices: readonly [number, number, number, number], points: readonly [RenderVector3, RenderVector3, RenderVector3, RenderVector3]): ViewerMeasurementEvaluation {
  if (!points.every(finitePoint)) return invalid("INVALID_COORDINATE");
  const b0 = subtract(points[0], points[1]);
  const b1 = subtract(points[2], points[1]);
  const b2 = subtract(points[3], points[2]);
  const b1Length = length(b1);
  if (b1Length <= EPSILON) return invalid("DEGENERATE_MEASUREMENT");
  const axis = scale(b1, 1 / b1Length);
  const v = subtract(b0, scale(axis, dot(b0, axis)));
  const w = subtract(b2, scale(axis, dot(b2, axis)));
  if (length(v) <= EPSILON || length(w) <= EPSILON) return invalid("DEGENERATE_MEASUREMENT");
  const value = radiansToDegrees(Math.atan2(dot(cross(axis, v), w), dot(v, w)));
  return valid({ kind: "dihedral", siteIndices: indices, value, unit: "degree" });
}

export function formatMeasurement(value: number, precision = 3) {
  if (!Number.isFinite(value)) return "invalid";
  return value.toFixed(Math.min(Math.max(precision, 0), 6));
}

function valid(result: ViewerMeasurementResult): ViewerMeasurementEvaluation { return Object.freeze({ ok: true, result: Object.freeze(result) }); }
function invalid(error: "INVALID_COORDINATE" | "DEGENERATE_MEASUREMENT"): ViewerMeasurementEvaluation { return Object.freeze({ ok: false, error }); }
function finitePoint(point: RenderVector3) { return point.length === 3 && point.every(Number.isFinite); }
function subtract(a: RenderVector3, b: RenderVector3): RenderVector3 { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
function scale(a: RenderVector3, value: number): RenderVector3 { return [a[0] * value, a[1] * value, a[2] * value]; }
function dot(a: RenderVector3, b: RenderVector3) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
function cross(a: RenderVector3, b: RenderVector3): RenderVector3 { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
function length(value: RenderVector3) { return Math.hypot(...value); }
function clamp(value: number, min: number, max: number) { return Math.min(Math.max(value, min), max); }
function radiansToDegrees(value: number) { return value * 180 / Math.PI; }
