export const PHONON_MODE_REF_SCHEMA_VERSION = "phase10h.phonon_mode_ref.v1";
export const PHONON_EIGENVECTOR_SCHEMA_VERSION = "phase10h.phonon_eigenvector.v1";
export const PHONON_EIGENVECTOR_SET_SCHEMA_VERSION = "phase10h.phonon_eigenvector_set.v1";
export const PHONON_EIGENVECTOR_SUMMARY_SCHEMA_VERSION = "phase10h.phonon_eigenvector_summary.v1";
export const PHONON_EIGENVECTOR_MANIFEST_SCHEMA_VERSION = "phase10h.phonon_eigenvector_manifest.v1";

export const PHONON_EIGENVECTOR_CAPS = Object.freeze({maxAtoms: 512, maxModes: 4096, maxWarnings: 32});

export type PhononEigenvectorValidation = Readonly<{valid: boolean; errors: readonly string[]; atomCount: number; modeCount: number}>;
type RecordValue = Record<string, unknown>;

const modeFields = new Set(["schema_version", "mode_id", "band_artifact", "structure_identity", "phonon_calculation_identity", "qpoint_index", "qpoint_coordinates", "qpoint_coordinate_system", "reciprocal_convention", "segment_index", "branch_index", "source_branch_identity", "frequency", "frequency_unit", "frequency_tolerance", "nac_direction", "degeneracy"]);
const eigenvectorFields = new Set(["schema_version", "mode", "structure_identity", "atom_count", "species", "atom_ordering", "coordinate_basis", "vector_unit", "atomic_masses", "stored_vector_representation", "normalization", "eigenvectors", "phase_convention", "provenance", "warnings", "security"]);
const securityFields = new Set(["contains_javascript", "contains_html", "external_urls_allowed", "executable_content_allowed", "external_assets"]);
const forbiddenKeys = new Set(["callback", "callbacks", "code", "eval", "function", "html", "iframe", "module", "script", "shader", "src", "texture", "url", "urls", "__proto__", "constructor", "prototype"]);
const forbiddenMarkers = ["http://", "https://", "javascript:", "<script", "<iframe", "eval(", "new function", "file://", "data:text/html"];

function record(value: unknown): value is RecordValue { return typeof value === "object" && value !== null && !Array.isArray(value); }
function finite(value: unknown): value is number { return typeof value === "number" && Number.isFinite(value) && Math.abs(value) <= 1e12; }
function integer(value: unknown): value is number { return typeof value === "number" && Number.isSafeInteger(value); }
function triplet(value: unknown): value is number[] { return Array.isArray(value) && value.length === 3 && value.every(finite); }
function hash(value: unknown): value is string { return typeof value === "string" && /^[0-9a-f]{64}$/.test(value); }
function exact(value: RecordValue, fields: Set<string>): boolean { const keys = Object.keys(value); return keys.length === fields.size && keys.every((key) => fields.has(key)); }
function validSecurity(value: unknown): boolean { return record(value) && exact(value, securityFields) && value.contains_javascript === false && value.contains_html === false && value.external_urls_allowed === false && value.executable_content_allowed === false && Array.isArray(value.external_assets) && value.external_assets.length === 0; }

function inert(root: unknown, errors: Set<string>): void {
  const queue: Array<{key: string; value: unknown; depth: number}> = [{key: "", value: root, depth: 0}];
  let visited = 0;
  while (queue.length) {
    const current = queue.pop()!; visited += 1;
    if (visited > 5_000_000 || current.depth > 14) { errors.add("PHONON_EIGENVECTOR_CAP_EXCEEDED"); return; }
    if (forbiddenKeys.has(current.key.toLowerCase())) errors.add("PHONON_EIGENVECTOR_EXTERNAL_REFERENCE_FORBIDDEN");
    if (typeof current.value === "string") {
      const lowered = current.value.toLowerCase();
      if (forbiddenMarkers.some((marker) => lowered.includes(marker)) || /^[a-z]:[\\/]/i.test(current.value) || /^\/(home|users|root|etc)\//i.test(current.value)) errors.add("PHONON_EIGENVECTOR_EXTERNAL_REFERENCE_FORBIDDEN");
    } else if (Array.isArray(current.value)) current.value.forEach((value) => queue.push({key: current.key, value, depth: current.depth + 1}));
    else if (record(current.value)) Object.entries(current.value).forEach(([key, value]) => queue.push({key, value, depth: current.depth + 1}));
  }
}

function result(errors: Set<string>, atomCount = 0, modeCount = 0): PhononEigenvectorValidation { return Object.freeze({valid: errors.size === 0, errors: Object.freeze([...errors].sort()), atomCount, modeCount}); }

export function validatePhononModeRef(value: unknown): PhononEigenvectorValidation {
  const errors = new Set<string>();
  if (!record(value) || !exact(value, modeFields) || value.schema_version !== PHONON_MODE_REF_SCHEMA_VERSION) return result(new Set(["PHONON_EIGENVECTOR_SCHEMA_UNSUPPORTED"]));
  const artifact = record(value.band_artifact) ? value.band_artifact : {};
  if (!exact(artifact, new Set(["artifact_id", "schema_version", "sha256"])) || typeof artifact.artifact_id !== "string" || !/^[A-Za-z0-9_.:-]{1,128}$/.test(artifact.artifact_id) || artifact.schema_version !== "phase10h.phonon_band.v1" || !hash(artifact.sha256)) errors.add("PHONON_MODE_ARTIFACT_INVALID");
  if (!hash(value.mode_id) || !hash(value.structure_identity) || !hash(value.phonon_calculation_identity) || !integer(value.qpoint_index) || value.qpoint_index < 0 || !integer(value.branch_index) || value.branch_index < 0) errors.add("PHONON_MODE_REFERENCE_INVALID");
  if (!triplet(value.qpoint_coordinates) || value.qpoint_coordinate_system !== "reciprocal_fractional" || value.reciprocal_convention !== "physics_2pi") errors.add("PHONON_MODE_QPOINT_MISMATCH");
  if (!finite(value.frequency) || value.frequency_unit !== "terahertz" || value.frequency_tolerance !== 1e-8) errors.add("PHONON_MODE_FREQUENCY_MISMATCH");
  if (value.nac_direction !== null && !triplet(value.nac_direction)) errors.add("PHONON_EIGENVECTOR_NAC_DIRECTION_MISMATCH");
  if (value.degeneracy !== null) {
    const degeneracy = record(value.degeneracy) ? value.degeneracy : {};
    const indices = Array.isArray(degeneracy.branch_indices) ? degeneracy.branch_indices : [];
    if (!exact(degeneracy, new Set(["group_id", "branch_indices", "source_declared", "basis_arbitrary_within_subspace"])) || typeof degeneracy.group_id !== "string" || indices.length < 2 || indices.some((item) => !integer(item) || item < 0) || degeneracy.source_declared !== true || degeneracy.basis_arbitrary_within_subspace !== true) errors.add("PHONON_EIGENVECTOR_DEGENERACY_INVALID");
  }
  inert(value, errors); return result(errors);
}

export function validatePhononEigenvector(value: unknown): PhononEigenvectorValidation {
  const errors = new Set<string>();
  if (!record(value) || !exact(value, eigenvectorFields) || value.schema_version !== PHONON_EIGENVECTOR_SCHEMA_VERSION) return result(new Set(["PHONON_EIGENVECTOR_SCHEMA_UNSUPPORTED"]));
  validatePhononModeRef(value.mode).errors.forEach((error) => errors.add(error));
  const mode = record(value.mode) ? value.mode : {};
  const atomCount = integer(value.atom_count) ? value.atom_count : 0;
  const species = Array.isArray(value.species) ? value.species : [];
  if (atomCount < 1 || atomCount > PHONON_EIGENVECTOR_CAPS.maxAtoms) errors.add("PHONON_EIGENVECTOR_CAP_EXCEEDED");
  if (value.structure_identity !== mode.structure_identity || value.atom_ordering !== "canonical_structure_order" || species.length !== atomCount || species.some((item) => typeof item !== "string" || !/^[A-Z][a-z]?$/.test(item))) errors.add("PHONON_EIGENVECTOR_ATOM_ORDER_MISMATCH");
  if (value.coordinate_basis !== "cartesian" || value.vector_unit !== "dimensionless" || value.stored_vector_representation !== "mass_weighted_eigenvector") errors.add("PHONON_EIGENVECTOR_COORDINATE_BASIS_UNSUPPORTED");
  const masses = record(value.atomic_masses) ? value.atomic_masses : {};
  const massValues = Array.isArray(masses.values) ? masses.values : [];
  if (!exact(masses, new Set(["values", "unit", "source", "reference"])) || massValues.length !== atomCount || massValues.some((item) => !finite(item) || item <= 0) || masses.unit !== "unified_atomic_mass_unit") errors.add("PHONON_EIGENVECTOR_MASS_INVALID");
  const normalization = record(value.normalization) ? value.normalization : {};
  if (!exact(normalization, new Set(["type", "tolerance", "unweighting_formula"])) || normalization.type !== "euclidean_unit_norm" || normalization.tolerance !== 1e-9 || normalization.unweighting_formula !== "u_i=e_i/sqrt(m_i)") errors.add("PHONON_EIGENVECTOR_NORMALIZATION_INVALID");
  const vectors = Array.isArray(value.eigenvectors) ? value.eigenvectors : [];
  let norm = 0; let pivotReal: number | null = null; let pivotImag: number | null = null;
  if (vectors.length !== atomCount) errors.add("PHONON_EIGENVECTOR_SHAPE_INVALID");
  vectors.forEach((item, index) => {
    const entry = record(item) ? item : {};
    if (!exact(entry, new Set(["atom_index", "real", "imag"])) || entry.atom_index !== index || !triplet(entry.real) || !triplet(entry.imag)) { errors.add("PHONON_EIGENVECTOR_SHAPE_INVALID"); return; }
    (entry.real as number[]).forEach((real, component) => { const imag = (entry.imag as number[])[component]; norm += real * real + imag * imag; if (pivotReal === null && Math.hypot(real, imag) > 1e-12) { pivotReal = real; pivotImag = imag; } });
  });
  if (Math.abs(norm - 1) > 1e-9) errors.add("PHONON_EIGENVECTOR_NORMALIZATION_INVALID");
  if (pivotReal === null || pivotImag === null) errors.add("PHONON_EIGENVECTOR_ZERO_NORM"); else if (Math.abs(pivotImag) > 1e-12 || pivotReal < 0) errors.add("PHONON_EIGENVECTOR_PHASE_INVALID");
  const phase = record(value.phase_convention) ? value.phase_convention : {};
  if (phase.global_phase_policy !== "first_nonzero_component_real_positive" || phase.component_order !== "atom_major_xyz" || phase.tolerance !== 1e-12 || phase.canonicalized !== true) errors.add("PHONON_EIGENVECTOR_PHASE_INVALID");
  const provenance = record(value.provenance) ? value.provenance : {};
  if (provenance.source_phase_preserved !== false || provenance.canonical_global_phase !== true || provenance.partial_occupancy !== false || provenance.display_amplitude_policy !== "max_atom_displacement" || provenance.display_only !== true || provenance.deterministic !== true) errors.add("PHONON_EIGENVECTOR_PROVENANCE_INVALID");
  const warnings = Array.isArray(value.warnings) ? value.warnings : [];
  if (warnings.length > PHONON_EIGENVECTOR_CAPS.maxWarnings || warnings.some((item) => item !== "PHONON_EIGENVECTOR_IMAGINARY_MODE_STATIC_ONLY")) errors.add("PHONON_EIGENVECTOR_METADATA_INVALID");
  if (!validSecurity(value.security)) errors.add("PHONON_EIGENVECTOR_EXTERNAL_REFERENCE_FORBIDDEN");
  inert(value, errors); return result(errors, atomCount, 1);
}

export function validatePhononEigenvectorBundle(bundle: unknown): PhononEigenvectorValidation {
  const errors = new Set<string>();
  if (!record(bundle)) return result(new Set(["PHONON_EIGENVECTOR_SCHEMA_UNSUPPORTED"]));
  validatePhononModeRef(bundle.mode).errors.forEach((error) => errors.add(error));
  validatePhononEigenvector(bundle.eigenvector).errors.forEach((error) => errors.add(error));
  const set = record(bundle.set) ? bundle.set : {};
  const modes = Array.isArray(set.modes) ? set.modes : [];
  if (set.schema_version !== PHONON_EIGENVECTOR_SET_SCHEMA_VERSION || set.ordering !== "qpoint_then_branch" || !integer(set.mode_count) || set.mode_count !== modes.length || modes.length < 1 || modes.length > PHONON_EIGENVECTOR_CAPS.maxModes || !validSecurity(set.security)) errors.add("PHONON_EIGENVECTOR_SET_INVALID");
  const order: string[] = [];
  modes.forEach((item) => { validatePhononEigenvector(item).errors.forEach((error) => errors.add(error)); const selected = record(item) && record(item.mode) ? item.mode : {}; order.push(`${selected.qpoint_index}:${selected.branch_index}`); });
  if (order.join("|") !== [...order].sort((a, b) => { const [aq, ab] = a.split(":").map(Number); const [bq, bb] = b.split(":").map(Number); return aq - bq || ab - bb; }).join("|") || new Set(order).size !== order.length) errors.add("PHONON_EIGENVECTOR_ORDER_INVALID");
  const summary = record(bundle.summary) ? bundle.summary : {};
  if (summary.schema_version !== PHONON_EIGENVECTOR_SUMMARY_SCHEMA_VERSION || !hash(summary.structure_identity) || !integer(summary.mode_count) || summary.mode_count !== modes.length || summary.normalization !== "mass_weighted_eigenvector/euclidean_unit_norm" || summary.phase_policy !== "first_nonzero_component_real_positive") errors.add("PHONON_EIGENVECTOR_SUMMARY_INVALID");
  const manifest = record(bundle.manifest) ? bundle.manifest : {};
  const artifacts = Array.isArray(manifest.artifacts) ? manifest.artifacts : [];
  if (manifest.schema_version !== PHONON_EIGENVECTOR_MANIFEST_SCHEMA_VERSION || !hash(manifest.structure_identity) || artifacts.length !== 2 || artifacts.some((item) => !record(item) || !hash(item.sha256)) || !validSecurity(manifest.security)) errors.add("PHONON_EIGENVECTOR_MANIFEST_INVALID");
  const topMode = record(bundle.mode) ? bundle.mode : {};
  const eigenvector = record(bundle.eigenvector) ? bundle.eigenvector : {};
  const eigenvectorMode = record(eigenvector.mode) ? eigenvector.mode : {};
  const topArtifact = record(topMode.band_artifact) ? topMode.band_artifact : {};
  const setArtifact = record(set.band_artifact) ? set.band_artifact : {};
  const manifestArtifact = record(manifest.band_artifact) ? manifest.band_artifact : {};
  if (topMode.mode_id !== eigenvectorMode.mode_id || topArtifact.sha256 !== setArtifact.sha256 || topArtifact.sha256 !== manifestArtifact.sha256 || bundle.mode !== eigenvector.mode && JSON.stringify(bundle.mode) !== JSON.stringify(eigenvector.mode)) errors.add("PHONON_MODE_REFERENCE_STALE");
  inert(bundle, errors); return result(errors, record(bundle.eigenvector) && integer(bundle.eigenvector.atom_count) ? bundle.eigenvector.atom_count : 0, modes.length);
}
