export const PHONON_BAND_SCHEMA_VERSION = "phase10h.phonon_band.v1";
export const PHONON_DOS_SCHEMA_VERSION = "phase10h.phonon_dos.v1";
export const PHONON_SUMMARY_SCHEMA_VERSION = "phase10h.phonon_summary.v1";
export const PHONON_MANIFEST_SCHEMA_VERSION = "phase10h.phonon_manifest.v1";

export const PHONON_CAPS = Object.freeze({
  maxAtoms: 512,
  maxBranches: 1536,
  maxQpoints: 4096,
  maxSegments: 256,
  maxDosPoints: 100_000,
  maxProjectedSeries: 512,
  maxNumericValues: 4_000_000,
  maxDegeneracyGroups: 4096,
});

export type PhononReferenceResult = Readonly<{
  valid: boolean;
  errors: readonly string[];
  atomCount: number;
  qpointCount: number;
  branchCount: number;
  dosPointCount: number;
  projectedSeriesCount: number;
}>;

const bandFields = new Set([
  "schema_version", "structure_identity", "atom_count", "species", "atom_ordering",
  "real_space_lattice_angstrom", "reciprocal_convention", "qpoint_coordinate_system",
  "path_distance_unit", "frequency_unit", "imaginary_frequency_encoding",
  "frequency_zero_tolerance", "branch_scope", "qpoints", "segments", "branches",
  "degeneracy_groups", "acoustic_sum_rule", "source", "warnings", "security",
]);
const dosFields = new Set([
  "schema_version", "structure_identity", "atom_count", "species", "atom_ordering",
  "frequency_unit", "imaginary_frequency_encoding", "frequency_zero_tolerance",
  "density_unit", "normalization", "frequency_grid_semantics", "frequencies", "total_dos",
  "projected_dos", "broadening", "integration", "source", "warnings", "security",
]);
const forbiddenKeys = new Set([
  "callback", "callbacks", "code", "eval", "formula", "function", "html", "iframe",
  "module", "script", "shader", "src", "texture", "url", "urls", "__proto__",
  "constructor", "prototype",
]);
const forbiddenMarkers = ["http://", "https://", "javascript:", "<script", "<iframe", "eval(", "new function", "file://", "data:text/html"];

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function finite(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value) && Math.abs(value) <= 1e12;
}

function integer(value: unknown): value is number {
  return typeof value === "number" && Number.isSafeInteger(value);
}

function triplet(value: unknown): value is [number, number, number] {
  return Array.isArray(value) && value.length === 3 && value.every(finite);
}

function exactFields(value: Record<string, unknown>, expected: Set<string>): boolean {
  const keys = Object.keys(value);
  return keys.length === expected.size && keys.every((key) => expected.has(key));
}

function validHash(value: unknown): boolean {
  return typeof value === "string" && /^[0-9a-f]{64}$/.test(value);
}

function scanInert(root: unknown, errors: Set<string>): void {
  const queue: Array<{value: unknown; key: string; depth: number}> = [{value: root, key: "", depth: 0}];
  let visited = 0;
  while (queue.length > 0) {
    const current = queue.pop()!;
    visited += 1;
    if (visited > 5_000_000 || current.depth > 10) { errors.add("PHONON_CAP_EXCEEDED"); return; }
    if (forbiddenKeys.has(current.key.toLowerCase())) errors.add("PHONON_EXTERNAL_REFERENCE_FORBIDDEN");
    if (typeof current.value === "string") {
      const lowered = current.value.toLowerCase();
      if (forbiddenMarkers.some((marker) => lowered.includes(marker)) || /^[a-z]:[\\/]/i.test(current.value) || /^\/(home|users|root|etc)\//i.test(current.value)) {
        errors.add("PHONON_EXTERNAL_REFERENCE_FORBIDDEN");
      }
    } else if (Array.isArray(current.value)) {
      current.value.forEach((value) => queue.push({value, key: current.key, depth: current.depth + 1}));
    } else if (record(current.value)) {
      Object.entries(current.value).forEach(([key, value]) => queue.push({value, key, depth: current.depth + 1}));
    }
  }
}

function validateShared(payload: Record<string, unknown>, errors: Set<string>): number {
  if (!validHash(payload.structure_identity)) errors.add("PHONON_STRUCTURE_IDENTITY_REQUIRED");
  const atomCount = integer(payload.atom_count) ? payload.atom_count : 0;
  const species = Array.isArray(payload.species) ? payload.species : [];
  if (atomCount < 1 || atomCount > PHONON_CAPS.maxAtoms) errors.add("PHONON_ATOM_COUNT_INVALID");
  if (payload.atom_ordering !== "canonical_structure_order" || species.length !== atomCount || species.some((item) => typeof item !== "string" || !/^[A-Z][a-z]?$/.test(item))) {
    errors.add("PHONON_SPECIES_ORDER_INVALID");
  }
  if (payload.frequency_unit !== "terahertz") errors.add("PHONON_FREQUENCY_UNIT_UNSUPPORTED");
  if (payload.imaginary_frequency_encoding !== "negative_real") errors.add("PHONON_IMAGINARY_ENCODING_UNSUPPORTED");
  if (!finite(payload.frequency_zero_tolerance) || payload.frequency_zero_tolerance < 0 || payload.frequency_zero_tolerance > 1) errors.add("PHONON_ZERO_TOLERANCE_INVALID");
  const security = record(payload.security) ? payload.security : {};
  const securityFields = new Set(["contains_javascript", "contains_html", "external_urls_allowed", "executable_content_allowed", "external_assets"]);
  if (
    !exactFields(security, securityFields)
    || security.contains_javascript !== false
    || security.contains_html !== false
    || security.external_urls_allowed !== false
    || security.executable_content_allowed !== false
    || !Array.isArray(security.external_assets)
    || security.external_assets.length !== 0
  ) errors.add("PHONON_EXTERNAL_REFERENCE_FORBIDDEN");
  scanInert(payload, errors);
  return atomCount;
}

function result(errors: Set<string>, atomCount: number, qpointCount = 0, branchCount = 0, dosPointCount = 0, projectedSeriesCount = 0): PhononReferenceResult {
  return Object.freeze({valid: errors.size === 0, errors: Object.freeze([...errors].sort()), atomCount, qpointCount, branchCount, dosPointCount, projectedSeriesCount});
}

export function reciprocalLatticePhysics2Pi(real: readonly (readonly number[])[]): number[][] {
  if (!Array.isArray(real) || real.length !== 3 || !real.every(triplet)) throw new Error("PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED");
  const [[a,b,c],[d,e,f],[g,h,i]] = real;
  const det = a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g);
  const scale = Math.max(...real.map((row) => Math.hypot(...row)));
  if (!(scale > 0) || Math.abs(det) <= 1e-12 * scale ** 3) throw new Error("PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED");
  const inverse = [
    [(e*i-f*h)/det, (c*h-b*i)/det, (b*f-c*e)/det],
    [(f*g-d*i)/det, (a*i-c*g)/det, (c*d-a*f)/det],
    [(d*h-e*g)/det, (b*g-a*h)/det, (a*e-b*d)/det],
  ];
  return [0,1,2].map((row) => [0,1,2].map((column) => 2 * Math.PI * inverse[column][row]));
}

export function reciprocalFractionalToCartesian(coordinates: readonly number[], real: readonly (readonly number[])[]): [number, number, number] {
  if (!triplet(coordinates)) throw new Error("PHONON_QPOINT_SHAPE_INVALID");
  const reciprocal = reciprocalLatticePhysics2Pi(real);
  return [0,1,2].map((axis) => coordinates[0] * reciprocal[0][axis] + coordinates[1] * reciprocal[1][axis] + coordinates[2] * reciprocal[2][axis]) as [number, number, number];
}

export function convertFrequency(value: number, source: string, target: string): number {
  if (!finite(value)) throw new Error("PHONON_FREQUENCY_NONFINITE");
  const approved = new Set(["terahertz", "inverse_centimeter", "millielectronvolt"]);
  if (!approved.has(source) || !approved.has(target)) throw new Error("PHONON_FREQUENCY_UNIT_UNSUPPORTED");
  const h = 6.62607015e-34;
  const c = 299_792_458;
  const electronvolt = 1.602176634e-19;
  const thz = source === "terahertz" ? value : source === "inverse_centimeter" ? value * c * 100 / 1e12 : value * electronvolt / (h * 1e15);
  return target === "terahertz" ? thz : target === "inverse_centimeter" ? thz * 1e12 / (c * 100) : thz * h * 1e15 / electronvolt;
}

export function validatePhononBandReference(payload: unknown): PhononReferenceResult {
  const errors = new Set<string>();
  if (!record(payload)) return result(new Set(["PHONON_SCHEMA_UNSUPPORTED"]), 0);
  if (!exactFields(payload, bandFields) || payload.schema_version !== PHONON_BAND_SCHEMA_VERSION) errors.add("PHONON_SCHEMA_UNSUPPORTED");
  const atomCount = validateShared(payload, errors);
  if (payload.reciprocal_convention !== "physics_2pi" || payload.path_distance_unit !== "radian_per_angstrom") errors.add("PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED");
  if (payload.qpoint_coordinate_system !== "reciprocal_fractional") errors.add("PHONON_QPOINT_COORDINATE_SYSTEM_UNSUPPORTED");
  try { reciprocalLatticePhysics2Pi(payload.real_space_lattice_angstrom as number[][]); } catch { errors.add("PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED"); }
  const qpoints = Array.isArray(payload.qpoints) ? payload.qpoints : [];
  const segments = Array.isArray(payload.segments) ? payload.segments : [];
  const branches = Array.isArray(payload.branches) ? payload.branches : [];
  const degeneracy = Array.isArray(payload.degeneracy_groups) ? payload.degeneracy_groups : [];
  if (qpoints.length < 1) errors.add("PHONON_QPOINT_SHAPE_INVALID");
  if (segments.length < 1) errors.add("PHONON_PATH_SEGMENT_INVALID");
  if (branches.length !== 3 * atomCount || payload.branch_scope !== "full") errors.add("PHONON_BRANCH_COUNT_MISMATCH");
  if (qpoints.length > PHONON_CAPS.maxQpoints || segments.length > PHONON_CAPS.maxSegments || branches.length > PHONON_CAPS.maxBranches || degeneracy.length > PHONON_CAPS.maxDegeneracyGroups || qpoints.length * branches.length > PHONON_CAPS.maxNumericValues) errors.add("PHONON_CAP_EXCEEDED");
  let priorDistance = -1;
  qpoints.forEach((qpoint, index) => {
    if (!record(qpoint) || qpoint.index !== index || !triplet(qpoint.coordinates)) { errors.add("PHONON_QPOINT_SHAPE_INVALID"); return; }
    if (!finite(qpoint.distance)) errors.add("PHONON_QPOINT_NONFINITE");
    else if (qpoint.distance < priorDistance - 1e-10) errors.add("PHONON_QPOINT_DISTANCE_NONMONOTONIC");
    else priorDistance = qpoint.distance;
    if (!integer(qpoint.segment_index) || qpoint.segment_index < 0) errors.add("PHONON_QPOINT_INDEX_INVALID");
    if (qpoint.label !== null && (typeof qpoint.label !== "string" || qpoint.label.length > 64 || /[<>]/.test(qpoint.label))) errors.add("PHONON_PATH_LABEL_INVALID");
  });
  branches.forEach((branch, index) => {
    if (!record(branch) || branch.branch_index !== index) { errors.add("PHONON_BRANCH_INDEX_INVALID"); return; }
    const frequencies = Array.isArray(branch.frequencies) ? branch.frequencies : [];
    if (frequencies.length !== qpoints.length) errors.add("PHONON_FREQUENCY_SHAPE_INVALID");
    if (frequencies.some((value) => !finite(value))) errors.add("PHONON_FREQUENCY_NONFINITE");
  });
  return result(errors, atomCount, qpoints.length, branches.length);
}

export function validatePhononDosReference(payload: unknown): PhononReferenceResult {
  const errors = new Set<string>();
  if (!record(payload)) return result(new Set(["PHONON_SCHEMA_UNSUPPORTED"]), 0);
  if (!exactFields(payload, dosFields) || payload.schema_version !== PHONON_DOS_SCHEMA_VERSION) errors.add("PHONON_SCHEMA_UNSUPPORTED");
  const atomCount = validateShared(payload, errors);
  if (payload.density_unit !== "modes_per_terahertz" || payload.normalization !== "total_modes") errors.add("PHONON_DOS_NORMALIZATION_UNSUPPORTED");
  if (payload.frequency_grid_semantics !== "sample_grid_points") errors.add("PHONON_DOS_GRID_INVALID");
  const frequencies = Array.isArray(payload.frequencies) ? payload.frequencies : [];
  const total = Array.isArray(payload.total_dos) ? payload.total_dos : [];
  const projected = Array.isArray(payload.projected_dos) ? payload.projected_dos : [];
  if (frequencies.length < 2 || frequencies.some((value) => !finite(value)) || frequencies.some((value, index) => index > 0 && value <= frequencies[index - 1])) errors.add("PHONON_DOS_GRID_INVALID");
  if (total.length !== frequencies.length) errors.add("PHONON_DOS_SHAPE_INVALID");
  if (total.some((value) => !finite(value) || value < 0)) errors.add("PHONON_DOS_NONFINITE");
  if (frequencies.length > PHONON_CAPS.maxDosPoints || projected.length > PHONON_CAPS.maxProjectedSeries || frequencies.length * (projected.length + 2) > PHONON_CAPS.maxNumericValues) errors.add("PHONON_CAP_EXCEEDED");
  const identities = new Set<string>();
  projected.forEach((projection, index) => {
    if (!record(projection) || projection.projection_index !== index) { errors.add("PHONON_PROJECTED_DOS_IDENTITY_INVALID"); return; }
    const identity = projection.projection_type === "atom" ? `atom:${String(projection.atom_index)}` : projection.projection_type === "species" ? `species:${String(projection.species)}` : "invalid";
    if (identity === "invalid") errors.add("PHONON_PROJECTED_DOS_IDENTITY_INVALID");
    if (identities.has(identity)) errors.add("PHONON_PROJECTED_DOS_DUPLICATE");
    identities.add(identity);
    if (!Array.isArray(projection.values) || projection.values.length !== frequencies.length) errors.add("PHONON_DOS_SHAPE_INVALID");
    else if (projection.values.some((value) => !finite(value) || value < 0)) errors.add("PHONON_DOS_NONFINITE");
  });
  const integration = record(payload.integration) ? payload.integration : {};
  if (integration.method !== "trapezoidal" || integration.expected_mode_count !== 3 * atomCount || !finite(integration.observed_integral) || !finite(integration.relative_tolerance)) errors.add("PHONON_DOS_INTEGRAL_MISMATCH");
  return result(errors, atomCount, 0, 0, frequencies.length, projected.length);
}
