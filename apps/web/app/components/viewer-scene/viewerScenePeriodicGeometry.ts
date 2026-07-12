import { measureAngle, measureDihedral } from "./viewerSceneMeasurements";
import type { ImageOffset, PeriodicSiteRef, RenderLattice, RenderVector3 } from "./viewerSceneRendererTypes";

export const PERIODIC_SEARCH_LIMITS = Object.freeze({ maxRadius: 4, maxCandidates: 729, maxCondition: 1e8, determinantRelativeEpsilon: 1e-12 });

export type PeriodicErrorCode = "PERIODIC_LATTICE_SINGULAR" | "PERIODIC_LATTICE_ILL_CONDITIONED" | "PERIODIC_SEARCH_LIMIT_EXCEEDED" | "PERIODIC_COORDINATE_INVALID" | "PERIODIC_MEASUREMENT_DEGENERATE";

export type MinimumImageResult = {
  readonly displacementCartesian: RenderVector3;
  readonly displacementFractional: RenderVector3;
  readonly imageOffset: ImageOffset;
  readonly distance: number;
  readonly searchRadius: number;
  readonly candidateCount: number;
  readonly status: "exact_bounded";
};

export type MinimumImageEvaluation = { readonly ok: true; readonly result: MinimumImageResult } | { readonly ok: false; readonly error: PeriodicErrorCode };

export function periodicSiteKey(ref: PeriodicSiteRef) {
  validatePeriodicRef(ref);
  return `${ref.siteIndex}:${ref.imageOffset[0]}:${ref.imageOffset[1]}:${ref.imageOffset[2]}`;
}

export function fractionalToCartesian(frac: RenderVector3, lattice: RenderLattice["matrix"]): RenderVector3 {
  assertFiniteVector(frac);
  assertFiniteMatrix(lattice);
  return freezeVector([
    frac[0] * lattice[0][0] + frac[1] * lattice[1][0] + frac[2] * lattice[2][0],
    frac[0] * lattice[0][1] + frac[1] * lattice[1][1] + frac[2] * lattice[2][1],
    frac[0] * lattice[0][2] + frac[1] * lattice[1][2] + frac[2] * lattice[2][2],
  ]);
}

export function cartesianToFractional(cart: RenderVector3, lattice: RenderLattice["matrix"]): RenderVector3 {
  return fractionalToCartesian(cart, inverseLattice(lattice));
}

export function translateCartesian(cart: RenderVector3, offset: ImageOffset, lattice: RenderLattice["matrix"]): RenderVector3 {
  validateImageOffset(offset);
  const translation = fractionalToCartesian(offset, lattice);
  return freezeVector([cart[0] + translation[0], cart[1] + translation[1], cart[2] + translation[2]]);
}

export function determinant(lattice: RenderLattice["matrix"]) {
  const [a, b, c] = lattice;
  return a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0]);
}

export function inverseLattice(lattice: RenderLattice["matrix"]): RenderLattice["matrix"] {
  assertFiniteMatrix(lattice);
  const det = determinant(lattice);
  const scale = Math.max(...lattice.flat().map(Math.abs), 1);
  if (Math.abs(det) <= scale ** 3 * PERIODIC_SEARCH_LIMITS.determinantRelativeEpsilon) throw periodicError("PERIODIC_LATTICE_SINGULAR");
  const [[a,b,c],[d,e,f],[g,h,i]] = lattice;
  const inverse = freezeMatrix([
    [(e*i-f*h)/det, (c*h-b*i)/det, (b*f-c*e)/det],
    [(f*g-d*i)/det, (a*i-c*g)/det, (c*d-a*f)/det],
    [(d*h-e*g)/det, (b*g-a*h)/det, (a*e-b*d)/det],
  ]);
  const conditionBound = frobenius(lattice) * frobenius(inverse);
  if (!Number.isFinite(conditionBound) || conditionBound > PERIODIC_SEARCH_LIMITS.maxCondition) throw periodicError("PERIODIC_LATTICE_ILL_CONDITIONED");
  return inverse;
}

export function minimumImage(sourceFractional: RenderVector3, targetFractional: RenderVector3, lattice: RenderLattice["matrix"]): MinimumImageEvaluation {
  try {
    assertFiniteVector(sourceFractional); assertFiniteVector(targetFractional);
    const inverse = inverseLattice(lattice);
    const delta = subtract(targetFractional, sourceFractional);
    const center: ImageOffset = freezeOffset([-Math.round(delta[0]), -Math.round(delta[1]), -Math.round(delta[2])]);
    const sigmaLowerBound = 1 / frobenius(inverse);
    let bestDistance = Number.POSITIVE_INFINITY;
    let bestOffset: ImageOffset | null = null;
    let bestDisplacementFractional: RenderVector3 | null = null;
    let bestDisplacementCartesian: RenderVector3 | null = null;
    let candidateCount = 0;
    for (let radius = 0; radius <= PERIODIC_SEARCH_LIMITS.maxRadius; radius += 1) {
      for (let x = -radius; x <= radius; x += 1) for (let y = -radius; y <= radius; y += 1) for (let z = -radius; z <= radius; z += 1) {
        if (radius > 0 && Math.max(Math.abs(x), Math.abs(y), Math.abs(z)) !== radius) continue;
        candidateCount += 1;
        if (candidateCount > PERIODIC_SEARCH_LIMITS.maxCandidates) return Object.freeze({ ok: false, error: "PERIODIC_SEARCH_LIMIT_EXCEEDED" });
        const offset = freezeOffset([center[0] + x, center[1] + y, center[2] + z]);
        const displacementFractional = freezeVector([delta[0] + offset[0], delta[1] + offset[1], delta[2] + offset[2]]);
        const displacementCartesian = fractionalToCartesian(displacementFractional, lattice);
        const distance = Math.hypot(...displacementCartesian);
        if (distance < bestDistance - 1e-12 || (Math.abs(distance - bestDistance) <= 1e-12 && (!bestOffset || compareOffset(offset, bestOffset) < 0))) {
          bestDistance = distance;
          bestOffset = offset;
          bestDisplacementFractional = displacementFractional;
          bestDisplacementCartesian = displacementCartesian;
        }
      }
      if (bestOffset && bestDisplacementFractional && bestDisplacementCartesian && bestDistance < sigmaLowerBound * (radius + 0.5) - 1e-12) {
        return Object.freeze({
          ok: true,
          result: Object.freeze({
            displacementCartesian: bestDisplacementCartesian,
            displacementFractional: bestDisplacementFractional,
            imageOffset: bestOffset,
            distance: bestDistance,
            searchRadius: radius,
            candidateCount,
            status: "exact_bounded",
          }),
        });
      }
    }
    return Object.freeze({ ok: false, error: "PERIODIC_SEARCH_LIMIT_EXCEEDED" });
  } catch (error) {
    return Object.freeze({ ok: false, error: isPeriodicError(error) ? error.code : "PERIODIC_COORDINATE_INVALID" });
  }
}

export function periodicAngle(anchor: PeriodicSiteRef, aSiteIndex: number, cSiteIndex: number, fractionalBySite: ReadonlyMap<number, RenderVector3>, lattice: RenderLattice["matrix"]) {
  const b = translatedFractional(fractionalBySite.get(anchor.siteIndex), anchor.imageOffset);
  const a = resolveFromAnchor(b, aSiteIndex, fractionalBySite, lattice);
  const c = resolveFromAnchor(b, cSiteIndex, fractionalBySite, lattice);
  if (!a.ok) return Object.freeze({ ok: false, error: a.error });
  if (!c.ok) return Object.freeze({ ok: false, error: c.error });
  const measured = measureAngle([aSiteIndex, anchor.siteIndex, cSiteIndex], [a.result.displacementCartesian, [0,0,0], c.result.displacementCartesian]);
  if (!measured.ok) return Object.freeze({ ok: false, error: "PERIODIC_MEASUREMENT_DEGENERATE" as const });
  return Object.freeze({ ok: true, value: measured.result.value, refs: Object.freeze([{ siteIndex: aSiteIndex, imageOffset: a.result.imageOffset }, anchor, { siteIndex: cSiteIndex, imageOffset: c.result.imageOffset }]) });
}

export function periodicDihedral(anchor: PeriodicSiteRef, aSiteIndex: number, cSiteIndex: number, dSiteIndex: number, fractionalBySite: ReadonlyMap<number, RenderVector3>, lattice: RenderLattice["matrix"]) {
  const bFractional = translatedFractional(fractionalBySite.get(anchor.siteIndex), anchor.imageOffset);
  const a = resolveFromAnchor(bFractional, aSiteIndex, fractionalBySite, lattice);
  const c = resolveFromAnchor(bFractional, cSiteIndex, fractionalBySite, lattice);
  if (!a.ok) return Object.freeze({ ok: false, error: a.error });
  if (!c.ok) return Object.freeze({ ok: false, error: c.error });
  const cAbsolute = translatedFractional(fractionalBySite.get(cSiteIndex), c.result.imageOffset);
  const d = resolveFromAnchor(cAbsolute, dSiteIndex, fractionalBySite, lattice);
  if (!d.ok) return Object.freeze({ ok: false, error: d.error });
  const aPoint = a.result.displacementCartesian;
  const bPoint: RenderVector3 = [0,0,0];
  const cPoint = c.result.displacementCartesian;
  const dPoint = freezeVector([cPoint[0] + d.result.displacementCartesian[0], cPoint[1] + d.result.displacementCartesian[1], cPoint[2] + d.result.displacementCartesian[2]]);
  const measured = measureDihedral([aSiteIndex, anchor.siteIndex, cSiteIndex, dSiteIndex], [aPoint, bPoint, cPoint, dPoint]);
  if (!measured.ok) return Object.freeze({ ok: false, error: "PERIODIC_MEASUREMENT_DEGENERATE" as const });
  return Object.freeze({ ok: true, value: measured.result.value, refs: Object.freeze([{ siteIndex: aSiteIndex, imageOffset: a.result.imageOffset }, anchor, { siteIndex: cSiteIndex, imageOffset: c.result.imageOffset }, { siteIndex: dSiteIndex, imageOffset: d.result.imageOffset }]) });
}

function resolveFromAnchor(anchorFractional: RenderVector3, targetSiteIndex: number, fractionalBySite: ReadonlyMap<number, RenderVector3>, lattice: RenderLattice["matrix"]) {
  const target = fractionalBySite.get(targetSiteIndex);
  if (!target) return Object.freeze({ ok: false, error: "PERIODIC_COORDINATE_INVALID" as const });
  return minimumImage(anchorFractional, target, lattice);
}
function translatedFractional(value: RenderVector3 | undefined, offset: ImageOffset): RenderVector3 { if (!value) throw periodicError("PERIODIC_COORDINATE_INVALID"); return freezeVector([value[0]+offset[0],value[1]+offset[1],value[2]+offset[2]]); }
function subtract(a: RenderVector3,b: RenderVector3): RenderVector3 { return freezeVector([a[0]-b[0],a[1]-b[1],a[2]-b[2]]); }
function frobenius(matrix: RenderLattice["matrix"]) { return Math.hypot(...matrix.flat()); }
function compareOffset(a: ImageOffset,b: ImageOffset) { return a[0]-b[0] || a[1]-b[1] || a[2]-b[2]; }
function validatePeriodicRef(ref: PeriodicSiteRef) { if (!Number.isInteger(ref.siteIndex) || ref.siteIndex < 0) throw periodicError("PERIODIC_COORDINATE_INVALID"); validateImageOffset(ref.imageOffset); }
function validateImageOffset(offset: ImageOffset) { if (offset.length !== 3 || offset.some((v) => !Number.isSafeInteger(v) || Math.abs(v)>3)) throw periodicError("PERIODIC_COORDINATE_INVALID"); }
function assertFiniteVector(value: RenderVector3) { if (value.length !== 3 || value.some((v)=>!Number.isFinite(v))) throw periodicError("PERIODIC_COORDINATE_INVALID"); }
function assertFiniteMatrix(value: RenderLattice["matrix"]) { if (value.length!==3 || value.some((row)=>row.length!==3 || row.some((v)=>!Number.isFinite(v)))) throw periodicError("PERIODIC_COORDINATE_INVALID"); }
function normalizeZero(value: number) { return Object.is(value, -0) ? 0 : value; }
function freezeVector(value: number[]): RenderVector3 { return Object.freeze([normalizeZero(value[0]),normalizeZero(value[1]),normalizeZero(value[2])]); }
function freezeOffset(value: number[]): ImageOffset { return Object.freeze([normalizeZero(value[0]),normalizeZero(value[1]),normalizeZero(value[2])]); }
function freezeMatrix(value: number[][]): RenderLattice["matrix"] { return Object.freeze([freezeVector(value[0]),freezeVector(value[1]),freezeVector(value[2])]); }
function periodicError(code: PeriodicErrorCode) { return Object.assign(new Error(code), { code }); }
function isPeriodicError(value: unknown): value is Error & {code: PeriodicErrorCode} { return value instanceof Error && "code" in value; }
