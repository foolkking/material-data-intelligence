import { reciprocalFractionalToCartesian, validatePhononBandReference } from "../../lib/phononContract";
import { mapBrillouinZoneArtifacts } from "../brillouin-zone/brillouinZoneMapper";
import type { BZPoint, BZSegment, BZVector3 } from "../brillouin-zone/brillouinZoneTypes";
import { BAND_BZ_LINK_SCHEMA_VERSION, type BandBZBranch, type BandBZLinkBundle, type BandBZLinkModel, type BandBZLinkResult, type BandBZPointOccurrence, type BandBZSampleMapping, type BandBZSegmentMapping } from "./bandBZLinkTypes";

export const BAND_BZ_LINK_CAPS = Object.freeze({ samples: 4096, segments: 256, branches: 256, numericValues: 262_144, mappings: 8192 });
const TOLERANCE = 1e-7;

type JsonRecord = Record<string, unknown>;

export function buildBandBZLinkModel(bundle: BandBZLinkBundle): BandBZLinkResult {
  const started = now();
  const errors = new Set<string>();
  const warnings = new Set<string>(["BAND_PATH_PROVIDER_UNDECLARED_EXACT_GEOMETRY_EQUIVALENCE", "BAND_TIME_REVERSAL_UNDECLARED"]);
  const bandValidation = validatePhononBandReference(bundle.band);
  if (!bandValidation.valid) bandValidation.errors.forEach((code) => errors.add(`BAND_BZ_${code}`));
  const bzResult = mapBrillouinZoneArtifacts(bundle.bz);
  if (!bzResult.ok) bzResult.errors.forEach((code) => errors.add(code));
  if (!record(bundle.band) || !bzResult.ok) return failed(errors, warnings);
  if (!sha(bundle.bandHash)) errors.add("BAND_BZ_BAND_HASH_INVALID");
  const band = bundle.band;
  const reciprocal = record(bundle.bz.reciprocal) ? bundle.bz.reciprocal : null;
  const binding = reciprocal && record(reciprocal.real_lattice_binding) ? reciprocal.real_lattice_binding : null;
  if (!binding) errors.add("BAND_BZ_RECIPROCAL_BINDING_INVALID");
  if (band.structure_identity !== bzResult.scene.structureIdentity || band.structure_identity !== binding?.source_structure_sha256) errors.add("BAND_BZ_STRUCTURE_MISMATCH");
  if (band.reciprocal_convention !== "physics_2pi" || bzResult.scene.convention !== "physics_2pi") errors.add("BAND_BZ_CONVENTION_MISMATCH");
  if (band.qpoint_coordinate_system !== "reciprocal_fractional") errors.add("BAND_BZ_COORDINATE_SYSTEM_MISMATCH");
  if (band.path_distance_unit !== "radian_per_angstrom" || bzResult.scene.units !== "angstrom^-1") errors.add("BAND_BZ_UNIT_MISMATCH");
  const bandLattice = matrix(band.real_space_lattice_angstrom);
  const primitiveLattice = matrix(binding?.primitive_real_lattice);
  if (!bandLattice || !primitiveLattice || matrixResidual(bandLattice, primitiveLattice) > TOLERANCE) errors.add("BAND_BZ_PRIMITIVE_LATTICE_MISMATCH");
  const primitiveHash = typeof binding?.primitive_lattice_sha256 === "string" ? binding.primitive_lattice_sha256 : "";
  if (!sha(primitiveHash)) errors.add("BAND_BZ_PRIMITIVE_HASH_INVALID");
  const qpoints = records(band.qpoints);
  const bandSegments = records(band.segments);
  const branchRecords = records(band.branches);
  if (qpoints.length > BAND_BZ_LINK_CAPS.samples || bandSegments.length > BAND_BZ_LINK_CAPS.segments || branchRecords.length > BAND_BZ_LINK_CAPS.branches || qpoints.length * branchRecords.length > BAND_BZ_LINK_CAPS.numericValues) errors.add("BAND_BZ_LINK_RESOURCE_LIMIT");
  const variant = bzResult.scene.variants.find((item) => item.selected);
  if (!variant) errors.add("BAND_BZ_PATH_VARIANT_MISSING");
  const bzSegments = variant ? variant.segmentIds.map((id) => bzResult.scene.segments.find((item) => item.id === id)).filter((item): item is BZSegment => Boolean(item)) : [];
  if (bandSegments.length !== bzSegments.length) errors.add("BAND_BZ_PATH_SEGMENT_COUNT_MISMATCH");
  if (errors.size) return failed(errors, warnings);

  const mappingStarted = now();
  const segmentMappings: BandBZSegmentMapping[] = [];
  const sampleMappings: BandBZSampleMapping[] = [];
  const pointOccurrences: BandBZPointOccurrence[] = [];
  const pointById = new Map(bzResult.scene.points.map((point) => [point.id, point]));
  for (let index = 0; index < bandSegments.length; index += 1) {
    const mapped = mapSegment(index, bandSegments[index], bzSegments[index], qpoints, pointById, bandLattice!);
    if (!mapped.ok) { errors.add(mapped.code); continue; }
    segmentMappings.push(mapped.segment);
    pointOccurrences.push(...mapped.occurrences);
    sampleMappings.push(...mapped.samples);
  }
  if (sampleMappings.length !== qpoints.length || sampleMappings.length > BAND_BZ_LINK_CAPS.mappings) errors.add("BAND_BZ_SAMPLE_MAPPING_INCOMPLETE");
  const branches: BandBZBranch[] = branchRecords.flatMap((item, index) => {
    const values = numbers(item.frequencies);
    if (item.branch_index !== index || values.length !== qpoints.length) { errors.add("BAND_BZ_BRANCH_IDENTITY_INVALID"); return []; }
    return [Object.freeze({ branchIndex: index, frequencies: Object.freeze(values) })];
  });
  if (errors.size) return failed(errors, warnings);
  const model: BandBZLinkModel = Object.freeze({
    schemaVersion: BAND_BZ_LINK_SCHEMA_VERSION,
    status: "compatible",
    bandArtifactHash: bundle.bandHash,
    structureIdentity: String(band.structure_identity),
    reciprocalHash: bzResult.scene.reciprocalHash,
    bzArtifactHash: bzResult.scene.zoneHash,
    kpathArtifactHash: bzResult.scene.kpathHash!,
    primitiveLatticeHash: primitiveHash,
    convention: "physics_2pi",
    units: "radian_per_angstrom",
    provider: Object.freeze({ name: bzResult.scene.provider.name, version: bzResult.scene.provider.version, pathConvention: bzResult.scene.provider.pathConvention, equivalence: "exact_ordered_geometry" }),
    timeReversal: Object.freeze({ bz: bzResult.scene.provider.timeReversal, band: "undeclared" }),
    pathVariantId: variant!.id,
    reciprocalMatrix: bzResult.scene.reciprocalMatrix,
    pointOccurrences: Object.freeze(pointOccurrences),
    segments: Object.freeze(segmentMappings),
    samples: Object.freeze(sampleMappings),
    branches: Object.freeze(branches),
    frequencyZeroTolerance: Number(band.frequency_zero_tolerance),
    warnings: Object.freeze([...warnings].sort()),
    metrics: Object.freeze({ compatibilityMs: elapsed(started), mappingMs: elapsed(mappingStarted), pointMappings: pointOccurrences.length, segmentMappings: segmentMappings.length, sampleMappings: sampleMappings.length, numericValues: qpoints.length * branches.length }),
  });
  return Object.freeze({ ok: true, model });
}

function mapSegment(index: number, raw: JsonRecord, bz: BZSegment, qpoints: JsonRecord[], points: Map<string, BZPoint>, lattice: number[][]): { ok: true; segment: BandBZSegmentMapping; occurrences: BandBZPointOccurrence[]; samples: BandBZSampleMapping[] } | { ok: false; code: string } {
  if (raw.segment_index !== index || !Number.isSafeInteger(raw.start_qpoint_index) || !Number.isSafeInteger(raw.end_qpoint_index)) return { ok: false, code: "BAND_BZ_SEGMENT_IDENTITY_INVALID" };
  const startIndex = Number(raw.start_qpoint_index), endIndex = Number(raw.end_qpoint_index);
  if (startIndex < 0 || endIndex < startIndex || endIndex >= qpoints.length) return { ok: false, code: "BAND_BZ_SEGMENT_RANGE_INVALID" };
  const startPoint = points.get(bz.startPointId), endPoint = points.get(bz.endPointId);
  const startFractional = vector(qpoints[startIndex]?.coordinates), endFractional = vector(qpoints[endIndex]?.coordinates);
  if (!startPoint || !endPoint || !startFractional || !endFractional) return { ok: false, code: "BAND_BZ_ENDPOINT_INVALID" };
  const forward = Math.max(distance(startFractional, startPoint.fractional), distance(endFractional, endPoint.fractional));
  const reverse = Math.max(distance(startFractional, endPoint.fractional), distance(endFractional, startPoint.fractional));
  const direction = forward <= TOLERANCE ? "forward" : reverse <= TOLERANCE ? "reverse" : null;
  if (!direction) return { ok: false, code: "BAND_BZ_PATH_MISMATCH" };
  const expectedBreak = index > 0 && bz.discontinuityBefore;
  if (Boolean(raw.discontinuous_from_previous) !== expectedBreak) return { ok: false, code: "BAND_BZ_DISCONTINUITY_MISMATCH" };
  const geometricStart = direction === "forward" ? startPoint : endPoint;
  const geometricEnd = direction === "forward" ? endPoint : startPoint;
  const startCartesian = reciprocalFractionalToCartesian(geometricStart.fractional, lattice) as BZVector3;
  const endCartesian = reciprocalFractionalToCartesian(geometricEnd.fractional, lattice) as BZVector3;
  const axis = subtract(endCartesian, startCartesian);
  const denominator = dot(axis, axis);
  if (denominator <= 1e-20) return { ok: false, code: "BAND_BZ_SEGMENT_DEGENERATE" };
  const samples: BandBZSampleMapping[] = [];
  const occurrences: BandBZPointOccurrence[] = [];
  for (let qpointIndex = startIndex; qpointIndex <= endIndex; qpointIndex += 1) {
    const fractional = vector(qpoints[qpointIndex]?.coordinates);
    if (!fractional || qpoints[qpointIndex]?.segment_index !== index || !finite(qpoints[qpointIndex]?.distance)) return { ok: false, code: "BAND_BZ_SAMPLE_INVALID" };
    const cartesian = reciprocalFractionalToCartesian(fractional, lattice) as BZVector3;
    const rawT = dot(subtract(cartesian, startCartesian), axis) / denominator;
    const t = Math.max(0, Math.min(1, rawT));
    const residual = distance(cartesian, add(startCartesian, scale(axis, t)));
    if (rawT < -TOLERANCE || rawT > 1 + TOLERANCE || residual > TOLERANCE) return { ok: false, code: "BAND_BZ_SAMPLE_OFF_SEGMENT" };
    const endpoint = qpointIndex === startIndex ? "start" : qpointIndex === endIndex ? "end" : null;
    const occurrenceId = endpoint ? `occ-${index}-${endpoint}-${qpointIndex}` : null;
    if (endpoint) occurrences.push(Object.freeze({ id: occurrenceId!, qpointIndex, segmentIndex: index, endpoint, bzPointId: endpoint === "start" ? geometricStart.id : geometricEnd.id, fractional, cartesian, residual }));
    samples.push(Object.freeze({ qpointIndex, segmentIndex: index, bzSegmentId: bz.id, t, fractional, cartesian, pathDistance: Number(qpoints[qpointIndex].distance), residual, pointOccurrenceId: occurrenceId }));
  }
  return { ok: true, segment: Object.freeze({ bandSegmentIndex: index, bzSegmentId: bz.id, variantId: bz.variantId, direction, distanceStart: Number(qpoints[startIndex].distance), distanceEnd: Number(qpoints[endIndex].distance), discontinuityBefore: expectedBreak, startPointId: geometricStart.id, endPointId: geometricEnd.id, residual: Math.min(forward, reverse) }), occurrences, samples };
}

function failed(errors: Set<string>, warnings: Set<string>): BandBZLinkResult { return Object.freeze({ ok: false, errors: Object.freeze([...errors].sort()), warnings: Object.freeze([...warnings].sort()) }); }
function record(value: unknown): value is JsonRecord { return typeof value === "object" && value !== null && !Array.isArray(value); }
function records(value: unknown): JsonRecord[] { return Array.isArray(value) ? value.filter(record) : []; }
function numbers(value: unknown): number[] { return Array.isArray(value) ? value.filter(finite) : []; }
function finite(value: unknown): value is number { return typeof value === "number" && Number.isFinite(value); }
function sha(value: unknown): value is string { return typeof value === "string" && /^[0-9a-f]{64}$/.test(value); }
function vector(value: unknown): BZVector3 | null { return Array.isArray(value) && value.length === 3 && value.every(finite) ? Object.freeze([value[0], value[1], value[2]]) : null; }
function matrix(value: unknown): number[][] | null { return Array.isArray(value) && value.length === 3 && value.every((row) => Array.isArray(row) && row.length === 3 && row.every(finite)) ? value as number[][] : null; }
function matrixResidual(left: number[][], right: number[][]): number { return Math.max(...left.flatMap((row, i) => row.map((value, j) => Math.abs(value - right[i][j])))); }
function subtract(a: BZVector3, b: BZVector3): BZVector3 { return [a[0]-b[0],a[1]-b[1],a[2]-b[2]]; }
function add(a: BZVector3, b: BZVector3): BZVector3 { return [a[0]+b[0],a[1]+b[1],a[2]+b[2]]; }
function scale(a: BZVector3, value: number): BZVector3 { return [a[0]*value,a[1]*value,a[2]*value]; }
function dot(a: BZVector3, b: BZVector3): number { return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]; }
function distance(a: BZVector3, b: BZVector3): number { return Math.hypot(a[0]-b[0],a[1]-b[1],a[2]-b[2]); }
function now(): number { return typeof performance === "undefined" ? Date.now() : performance.now(); }
function elapsed(started: number): number { return Math.max(0, now() - started); }
