export const PHONON_BAND_DOS_SCHEMA_VERSION = "phase10h.phonon_band_dos.v1";
export const PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION = "phase10h.phonon_band_dos_summary.v1";
export const PHONON_BAND_DOS_COMPATIBILITY_SCHEMA_VERSION = "phase10h.phonon_band_dos_compatibility_report.v1";
export const PHONON_BAND_DOS_PLOT_SCHEMA_VERSION = "phase10h.phonon_band_dos_plot.v1";
export const PHONON_BAND_DOS_TABLE_SCHEMA_VERSION = "phase10h.phonon_band_dos_table.v1";
export const PHONON_BAND_DOS_MANIFEST_SCHEMA_VERSION = "phase10h.phonon_band_dos_manifest.v1";

export const PHONON_BAND_DOS_CAPS = Object.freeze({
  maxVisibleProjections: 4,
  maxPlotValues: 1_000_000,
  maxPlotTraces: 4_096,
  maxTableRows: 500,
  maxWarnings: 32,
});

export const PHONON_BAND_DOS_CHECK_ORDER = Object.freeze([
  "input_artifacts", "band_schema", "dos_schema", "artifact_hashes", "structure_identity", "atom_count",
  "species_ordering", "cell_lineage", "source_lineage", "force_constants", "frequency_unit",
  "imaginary_encoding", "zero_tolerance", "nac", "dos_normalization", "projection_identity",
  "display_caps", "frequency_domain", "display_options",
]);

export type CombinedContractResult = Readonly<{valid: boolean; errors: readonly string[]}>;
export type CombinedBundle = Readonly<{
  combined: JsonRecord;
  summary: JsonRecord;
  report: JsonRecord;
  plot: JsonRecord;
  table: JsonRecord;
  manifest: JsonRecord;
}>;
export type JsonRecord = Record<string, unknown>;

const securityFields = new Set(["contains_javascript", "contains_html", "external_urls_allowed", "executable_content_allowed", "external_assets"]);
const publicRefFields = new Set(["artifact_id", "schema_version", "media_type", "size_bytes", "sha256"]);
const warningCodes = new Set([
  "PHONON_BAND_DOS_ASR_METADATA_PARTIAL",
  "PHONON_BAND_DOS_FREQUENCY_RANGE_DIFFERENCE",
  "PHONON_BAND_DOS_LINEAGE_INCOMPLETE",
  "PHONON_BAND_DOS_PLOT_DEGRADED",
]);
const resultCodes = new Set([
  "PHONON_BAND_DOS_INPUT_SCHEMA_INVALID", "PHONON_BAND_DOS_STRUCTURE_MISMATCH",
  "PHONON_BAND_DOS_ATOM_COUNT_MISMATCH", "PHONON_BAND_DOS_ATOM_ORDER_MISMATCH",
  "PHONON_BAND_DOS_CELL_LINEAGE_MISMATCH", "PHONON_BAND_DOS_SOURCE_LINEAGE_MISMATCH",
  "PHONON_BAND_DOS_FORCE_CONSTANTS_MISMATCH", "PHONON_BAND_DOS_FREQUENCY_UNIT_INCOMPATIBLE",
  "PHONON_BAND_DOS_UNIT_CONVERSION_APPLIED", "PHONON_BAND_DOS_IMAGINARY_ENCODING_MISMATCH",
  "PHONON_BAND_DOS_ZERO_TOLERANCE_MISMATCH", "PHONON_BAND_DOS_NAC_MISMATCH",
  "PHONON_BAND_DOS_NAC_DIRECTION_MISMATCH", "PHONON_BAND_DOS_NORMALIZATION_INVALID",
]);
const forbiddenKeys = new Set([
  "callback", "callbacks", "code", "eval", "function", "html", "iframe", "module", "script", "shader",
  "src", "texture", "url", "urls", "__proto__", "constructor", "prototype",
]);
const forbiddenMarkers = ["http://", "https://", "javascript:", "<script", "<iframe", "eval(", "new function", "file://", "data:text/html"];

export function validatePhononBandDosBundle(value: { [K in keyof CombinedBundle]?: unknown }): CombinedContractResult {
  const errors = new Set<string>();
  validateCombined(value.combined, errors);
  validateSummary(value.summary, errors);
  validateReport(value.report, errors);
  validatePlot(value.plot, errors);
  validateTable(value.table, errors);
  validateManifest(value.manifest, errors);
  if ([value.combined, value.report, value.plot, value.manifest].every(record)) {
    const combined = value.combined as JsonRecord;
    const report = value.report as JsonRecord;
    const plot = value.plot as JsonRecord;
    const manifest = value.manifest as JsonRecord;
    const combinedBand = record(combined.band) ? combined.band : {};
    const combinedDos = record(combined.dos) ? combined.dos : {};
    const reportBand = record(report.band_artifact) ? report.band_artifact : {};
    const reportDos = record(report.dos_artifact) ? report.dos_artifact : {};
    const refs = record(plot.source_refs) ? plot.source_refs : {};
    const plotBand = record(refs.band) ? refs.band : {};
    const plotDos = record(refs.dos) ? refs.dos : {};
    const sources = record(manifest.source_artifacts) ? manifest.source_artifacts : {};
    if (!sameRef(combinedBand, reportBand) || !sameRef(combinedBand, plotBand) || !sameRef(combinedBand, record(sources.band) ? sources.band : {})) errors.add("PHONON_BAND_DOS_SOURCE_REFERENCE_MISMATCH");
    if (!sameRef(combinedDos, reportDos) || !sameRef(combinedDos, plotDos) || !sameRef(combinedDos, record(sources.dos) ? sources.dos : {})) errors.add("PHONON_BAND_DOS_SOURCE_REFERENCE_MISMATCH");
    const compatibility = record(combined.compatibility) ? combined.compatibility : {};
    const artifacts = records(manifest.artifacts);
    const reportEntry = artifacts.find((item) => item.name === "phonon_band_dos_compatibility_report.json");
    if (!reportEntry || compatibility.report_sha256 !== reportEntry.sha256 || compatibility.status !== report.status || compatibility.status !== manifest.compatibility_status) errors.add("PHONON_BAND_DOS_COMPATIBILITY_REPORT_INVALID");
  }
  return Object.freeze({valid: errors.size === 0, errors: Object.freeze([...errors].sort())});
}

function validateCombined(value: unknown, errors: Set<string>): void {
  const fields = new Set(["schema_version", "tool_id", "structure_identity", "band", "dos", "compatibility", "frequency_axis", "display", "provenance", "warnings", "security"]);
  if (!record(value)) { errors.add("PHONON_BAND_DOS_SCHEMA_INVALID"); return; }
  scanInert(value, errors);
  if (!exact(value, fields) || value.schema_version !== PHONON_BAND_DOS_SCHEMA_VERSION) errors.add("PHONON_BAND_DOS_SCHEMA_INVALID");
  if (value.tool_id !== "phonon.band_dos" || !hash(value.structure_identity) || !publicRef(value.band, "phase10h.phonon_band.v1") || !publicRef(value.dos, "phase10h.phonon_dos.v1")) errors.add("PHONON_BAND_DOS_SCHEMA_INVALID");
  const compatibility = record(value.compatibility) ? value.compatibility : {};
  if (!exact(compatibility, new Set(["status", "report_name", "report_sha256", "frequency_conversion_applied", "density_jacobian_applied", "warnings"])) || !new Set(["compatible", "convertible"]).has(String(compatibility.status)) || compatibility.report_name !== "phonon_band_dos_compatibility_report.json" || !hash(compatibility.report_sha256) || typeof compatibility.frequency_conversion_applied !== "boolean" || typeof compatibility.density_jacobian_applied !== "boolean" || !warnings(compatibility.warnings)) errors.add("PHONON_BAND_DOS_SCHEMA_INVALID");
  const axis = record(value.frequency_axis) ? value.frequency_axis : {};
  if (!exact(axis, new Set(["unit", "minimum", "maximum", "domain_policy", "zero_tolerance"])) || axis.unit !== "terahertz" || !range(axis.minimum, axis.maximum) || !new Set(["union", "manual_view"]).has(String(axis.domain_policy)) || !finite(axis.zero_tolerance) || axis.zero_tolerance < 0) errors.add("PHONON_BAND_DOS_DOMAIN_INVALID");
  const display = record(value.display) ? value.display : {};
  if (!exact(display, new Set(["layout", "shared_frequency_axis", "dos_orientation", "performance_mode", "default_projection_mode", "selected_projection_ids"])) || display.layout !== "band_left_dos_right" || display.shared_frequency_axis !== true || display.dos_orientation !== "density_x_frequency_y" || !new Set(["interactive", "degraded", "refused"]).has(String(display.performance_mode)) || display.default_projection_mode !== "total_only" || !projectionIds(display.selected_projection_ids)) errors.add("PHONON_BAND_DOS_DISPLAY_OPTIONS_INVALID");
  const provenance = record(value.provenance) ? value.provenance : {};
  if (!exact(provenance, new Set(["deterministic", "source_hashes", "derived_for_display"])) || provenance.deterministic !== true || provenance.derived_for_display !== true || !Array.isArray(provenance.source_hashes) || provenance.source_hashes.length !== 2 || !provenance.source_hashes.every(hash)) errors.add("PHONON_BAND_DOS_SCHEMA_INVALID");
  if (!warnings(value.warnings) || !security(value.security)) errors.add("PHONON_BAND_DOS_EXTERNAL_REFERENCE_FORBIDDEN");
}

function validateSummary(value: unknown, errors: Set<string>): void {
  const fields = new Set([
    "schema_version", "structure_identity", "atom_count", "species", "branch_count", "qpoint_count", "segment_count",
    "dos_grid_point_count", "projection_count", "frequency_unit", "frequency_min", "frequency_max", "band_frequency_min",
    "band_frequency_max", "dos_frequency_min", "dos_frequency_max", "imaginary_band_mode_count", "imaginary_dos_integral",
    "dos_density_unit", "dos_normalization", "dos_integral", "expected_modes", "compatibility_status", "nac_enabled",
    "band_asr_applied", "broadening", "warnings", "security",
  ]);
  if (!record(value) || !exact(value, fields) || value.schema_version !== PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION) { errors.add("PHONON_BAND_DOS_SUMMARY_INVALID"); return; }
  scanInert(value, errors);
  const atomCount = positiveInteger(value.atom_count) ? value.atom_count : 0;
  const counts = [value.branch_count, value.qpoint_count, value.segment_count, value.dos_grid_point_count, value.projection_count, value.imaginary_band_mode_count, value.expected_modes];
  if (!hash(value.structure_identity) || atomCount < 1 || !counts.every(nonnegativeInteger) || value.branch_count !== 3 * atomCount || value.expected_modes !== 3 * atomCount || !species(value.species, atomCount)) errors.add("PHONON_BAND_DOS_SUMMARY_INVALID");
  if (![range(value.frequency_min, value.frequency_max), range(value.band_frequency_min, value.band_frequency_max), range(value.dos_frequency_min, value.dos_frequency_max)].every(Boolean) || value.frequency_unit !== "terahertz" || value.dos_density_unit !== "modes_per_terahertz" || value.dos_normalization !== "total_modes" || !new Set(["compatible", "convertible"]).has(String(value.compatibility_status)) || !finite(value.imaginary_dos_integral) || !finite(value.dos_integral) || typeof value.nac_enabled !== "boolean" || typeof value.band_asr_applied !== "boolean" || !broadening(value.broadening) || !warnings(value.warnings) || !security(value.security)) errors.add("PHONON_BAND_DOS_SUMMARY_INVALID");
}

function validateReport(value: unknown, errors: Set<string>): void {
  const fields = new Set(["schema_version", "status", "band_artifact", "dos_artifact", "checks", "conversion", "frequency_domain", "warnings", "deterministic", "security"]);
  if (!record(value) || !exact(value, fields) || value.schema_version !== PHONON_BAND_DOS_COMPATIBILITY_SCHEMA_VERSION) { errors.add("PHONON_BAND_DOS_COMPATIBILITY_REPORT_INVALID"); return; }
  scanInert(value, errors);
  const checks = records(value.checks);
  if (!new Set(["compatible", "convertible", "incompatible"]).has(String(value.status)) || value.deterministic !== true || checks.length !== PHONON_BAND_DOS_CHECK_ORDER.length || checks.some((item, index) => item.name !== PHONON_BAND_DOS_CHECK_ORDER[index] || !exact(item, new Set(["name", "status", "result_code", "band_value", "dos_value"])) || !new Set(["pass", "convertible", "warning", "fail"]).has(String(item.status)) || item.result_code !== null && !resultCodes.has(String(item.result_code)))) errors.add("PHONON_BAND_DOS_COMPATIBILITY_REPORT_INVALID");
  if (!publicRef(value.band_artifact, "phase10h.phonon_band.v1") || !publicRef(value.dos_artifact, "phase10h.phonon_dos.v1") || !conversion(value.conversion) || !frequencyDomain(value.frequency_domain) || !warnings(value.warnings) || !security(value.security)) errors.add("PHONON_BAND_DOS_COMPATIBILITY_REPORT_INVALID");
}

function validatePlot(value: unknown, errors: Set<string>): void {
  const fields = new Set(["schema_version", "layout", "shared_frequency_axis", "band_panel", "dos_panel", "display", "source_refs", "security"]);
  if (!record(value) || !exact(value, fields) || value.schema_version !== PHONON_BAND_DOS_PLOT_SCHEMA_VERSION) { errors.add("PHONON_BAND_DOS_PLOT_INVALID"); return; }
  scanInert(value, errors);
  const axis = record(value.shared_frequency_axis) ? value.shared_frequency_axis : {};
  const band = record(value.band_panel) ? value.band_panel : {};
  const dos = record(value.dos_panel) ? value.dos_panel : {};
  const display = record(value.display) ? value.display : {};
  if (value.layout !== "band_left_dos_right" || !exact(axis, new Set(["unit", "minimum", "maximum", "zero_tolerance", "domain_policy"])) || axis.unit !== "terahertz" || !range(axis.minimum, axis.maximum) || !finite(axis.zero_tolerance) || !new Set(["union", "manual_view"]).has(String(axis.domain_policy))) errors.add("PHONON_BAND_DOS_PLOT_INVALID");
  if (!exact(band, new Set(["x_axis", "series", "ticks", "preserve_segment_breaks"])) || band.x_axis !== "q_path_distance" || band.preserve_segment_breaks !== true || !Array.isArray(band.series) || !Array.isArray(band.ticks)) errors.add("PHONON_BAND_DOS_PLOT_INVALID");
  if (!exact(dos, new Set(["x_axis", "y_axis", "density_unit", "frequencies", "total_dos", "projections"])) || dos.x_axis !== "dos_density" || dos.y_axis !== "shared_frequency" || dos.density_unit !== "modes_per_terahertz" || !Array.isArray(dos.frequencies) || !Array.isArray(dos.total_dos) || !Array.isArray(dos.projections)) errors.add("PHONON_BAND_DOS_PLOT_INVALID");
  if (!exact(display, new Set(["show_imaginary_region", "show_high_symmetry_labels", "mode", "reason", "numeric_values", "trace_count", "selected_projection_ids"])) || typeof display.show_imaginary_region !== "boolean" || typeof display.show_high_symmetry_labels !== "boolean" || !new Set(["interactive", "degraded", "refused"]).has(String(display.mode)) || !nonnegativeInteger(display.numeric_values) || display.numeric_values > PHONON_BAND_DOS_CAPS.maxPlotValues || !nonnegativeInteger(display.trace_count) || display.trace_count > PHONON_BAND_DOS_CAPS.maxPlotTraces || !projectionIds(display.selected_projection_ids)) errors.add("PHONON_BAND_DOS_PLOT_INVALID");
  const series = records(band.series);
  for (const item of series) {
    const path = numbers(item.path_distance);
    const frequencies = numbers(item.frequencies);
    if (!exact(item, new Set(["branch_index", "segment_index", "path_distance", "frequencies"])) || !nonnegativeInteger(item.branch_index) || !nonnegativeInteger(item.segment_index) || path.length < 2 || path.length !== frequencies.length || path.some((point, index) => index > 0 && point < path[index - 1])) errors.add("PHONON_BAND_DOS_PLOT_INVALID");
  }
  const dosFrequencies = numbers(dos.frequencies);
  const total = numbers(dos.total_dos);
  if (dosFrequencies.length !== total.length || dosFrequencies.some((point, index) => index > 0 && point <= dosFrequencies[index - 1]) || total.some((point) => point < 0)) errors.add("PHONON_BAND_DOS_PLOT_INVALID");
  const projectionIdentities = new Set<string>();
  for (const item of records(dos.projections)) {
    const identity = String(item.projection_id || "");
    const values = numbers(item.values);
    if (!exact(item, new Set(["projection_id", "projection_type", "atom_index", "species", "source_guarantees_sum", "values"])) || !/^(atom:[0-9]{1,6}|species:[A-Z][a-z]?)$/.test(identity) || projectionIdentities.has(identity) || values.length !== dosFrequencies.length || values.some((point) => point < 0) || typeof item.source_guarantees_sum !== "boolean") errors.add("PHONON_BAND_DOS_PLOT_INVALID");
    projectionIdentities.add(identity);
  }
  const selected = Array.isArray(display.selected_projection_ids) ? display.selected_projection_ids : [];
  if (selected.some((identity) => !projectionIdentities.has(String(identity)))) errors.add("PHONON_BAND_DOS_PLOT_INVALID");
  const refs = record(value.source_refs) ? value.source_refs : {};
  if (!exact(refs, new Set(["band", "dos"])) || !publicRef(refs.band, "phase10h.phonon_band.v1") || !publicRef(refs.dos, "phase10h.phonon_dos.v1") || !security(value.security)) errors.add("PHONON_BAND_DOS_PLOT_INVALID");
}

function validateTable(value: unknown, errors: Set<string>): void {
  const fields = new Set(["schema_version", "compatibility_columns", "compatibility_rows", "summary_rows", "row_count", "truncated", "security"]);
  if (!record(value) || !exact(value, fields) || value.schema_version !== PHONON_BAND_DOS_TABLE_SCHEMA_VERSION || !Array.isArray(value.compatibility_columns) || value.compatibility_columns.join("|") !== "check|band_value|dos_value|status|result_code" || !Array.isArray(value.compatibility_rows) || !Array.isArray(value.summary_rows) || !nonnegativeInteger(value.row_count) || value.row_count !== value.compatibility_rows.length + value.summary_rows.length || value.row_count > PHONON_BAND_DOS_CAPS.maxTableRows || typeof value.truncated !== "boolean" || !security(value.security)) errors.add("PHONON_BAND_DOS_TABLE_INVALID");
  else scanInert(value, errors);
}

function validateManifest(value: unknown, errors: Set<string>): void {
  const fields = new Set(["schema_version", "tool_id", "structure_identity", "compatibility_status", "frequency_unit", "source_artifacts", "artifact_order", "artifacts", "capabilities", "security"]);
  const order = ["phonon_band_dos.json", "phonon_band_dos_summary.json", "phonon_band_dos_compatibility_report.json", "phonon_band_dos_plot.json", "phonon_band_dos_table.json", "phonon_band_dos_manifest.json"];
  if (!record(value) || !exact(value, fields) || value.schema_version !== PHONON_BAND_DOS_MANIFEST_SCHEMA_VERSION) { errors.add("PHONON_BAND_DOS_MANIFEST_INVALID"); return; }
  scanInert(value, errors);
  const sources = record(value.source_artifacts) ? value.source_artifacts : {};
  const capabilities = record(value.capabilities) ? value.capabilities : {};
  const expectedCapabilities = {band: true, dos: true, combined_view: true, shared_frequency_axis: true, projected_dos: true, eigenvectors: false, animation: false, thermal_properties: false, phonon_calculation: false, external_resources: false};
  const capabilityFields = new Set(Object.keys(expectedCapabilities));
  const capabilitiesMatch = exact(capabilities, capabilityFields) && Object.entries(expectedCapabilities).every(([key, expected]) => capabilities[key] === expected);
  if (value.tool_id !== "phonon.band_dos" || !hash(value.structure_identity) || !new Set(["compatible", "convertible"]).has(String(value.compatibility_status)) || value.frequency_unit !== "terahertz" || !exact(sources, new Set(["band", "dos"])) || !publicRef(sources.band, "phase10h.phonon_band.v1") || !publicRef(sources.dos, "phase10h.phonon_dos.v1") || !Array.isArray(value.artifact_order) || value.artifact_order.join("|") !== order.join("|") || !capabilitiesMatch || !security(value.security)) errors.add("PHONON_BAND_DOS_MANIFEST_INVALID");
  const artifacts = records(value.artifacts);
  if (artifacts.length !== order.length - 1 || artifacts.map((item) => item.name).join("|") !== order.slice(0, -1).join("|") || artifacts.some((item) => !exact(item, new Set(["name", "schema_version", "media_type", "size_bytes", "sha256"])) || item.media_type !== "application/json" || !positiveInteger(item.size_bytes) || !hash(item.sha256))) errors.add("PHONON_BAND_DOS_MANIFEST_INVALID");
}

function conversion(value: unknown): boolean {
  if (!record(value) || !exact(value, new Set(["band_frequency_unit_from", "dos_frequency_unit_from", "frequency_unit_to", "band_frequency_factor", "dos_frequency_factor", "frequency_conversion_applied", "density_jacobian_applied", "broadening_width_converted", "integral_before", "integral_after"]))) return false;
  const units = new Set(["terahertz", "inverse_centimeter", "millielectronvolt"]);
  return units.has(String(value.band_frequency_unit_from)) && units.has(String(value.dos_frequency_unit_from)) && value.frequency_unit_to === "terahertz" && finite(value.band_frequency_factor) && value.band_frequency_factor > 0 && finite(value.dos_frequency_factor) && value.dos_frequency_factor > 0 && typeof value.frequency_conversion_applied === "boolean" && typeof value.density_jacobian_applied === "boolean" && typeof value.broadening_width_converted === "boolean" && finite(value.integral_before) && finite(value.integral_after) && Math.abs(value.integral_before - value.integral_after) <= Math.max(1e-10, Math.abs(value.integral_before) * 1e-10);
}

function frequencyDomain(value: unknown): boolean {
  if (!record(value) || !exact(value, new Set(["band", "dos", "display", "union", "policy"])) || !new Set(["union", "manual_view"]).has(String(value.policy))) return false;
  return [value.band, value.dos, value.display, value.union].every((item) => Array.isArray(item) && item.length === 2 && range(item[0], item[1]));
}

function publicRef(value: unknown, schema: string): boolean {
  return record(value) && exact(value, publicRefFields) && typeof value.artifact_id === "string" && /^[A-Za-z0-9_.:-]{1,128}$/.test(value.artifact_id) && value.schema_version === schema && value.media_type === "application/json" && positiveInteger(value.size_bytes) && hash(value.sha256);
}

function sameRef(left: JsonRecord, right: JsonRecord): boolean {
  return left.artifact_id === right.artifact_id && left.schema_version === right.schema_version && left.sha256 === right.sha256 && left.size_bytes === right.size_bytes;
}

function security(value: unknown): boolean {
  return record(value) && exact(value, securityFields) && value.contains_javascript === false && value.contains_html === false && value.external_urls_allowed === false && value.executable_content_allowed === false && Array.isArray(value.external_assets) && value.external_assets.length === 0;
}

function warnings(value: unknown): boolean {
  return Array.isArray(value) && value.length <= PHONON_BAND_DOS_CAPS.maxWarnings && value.every((item) => typeof item === "string" && warningCodes.has(item)) && value.every((item, index) => index === 0 || String(item) > String(value[index - 1]));
}

function broadening(value: unknown): boolean {
  if (!record(value) || !exact(value, new Set(["method", "width", "unit", "source"])) || !new Set(["none", "gaussian", "source_defined"]).has(String(value.method)) || value.source !== null && (typeof value.source !== "string" || value.source.length > 128)) return false;
  return value.method === "none" ? value.width === null && value.unit === null : finite(value.width) && value.width > 0 && value.unit === "terahertz";
}

function species(value: unknown, count: number): boolean {
  return Array.isArray(value) && value.length === count && value.every((item) => typeof item === "string" && /^[A-Z][a-z]?$/.test(item));
}

function projectionIds(value: unknown): boolean {
  return Array.isArray(value) && value.length <= PHONON_BAND_DOS_CAPS.maxVisibleProjections && new Set(value).size === value.length && value.every((item) => typeof item === "string" && /^(atom:[0-9]{1,6}|species:[A-Z][a-z]?)$/.test(item));
}

function scanInert(root: unknown, errors: Set<string>): void {
  const queue: Array<{value: unknown; key: string; depth: number}> = [{value: root, key: "", depth: 0}];
  let visited = 0;
  while (queue.length) {
    const current = queue.pop()!;
    visited += 1;
    if (visited > 5_000_000 || current.depth > 12) { errors.add("PHONON_BAND_DOS_ARTIFACT_LIMIT_EXCEEDED"); return; }
    if (forbiddenKeys.has(current.key.toLowerCase())) errors.add("PHONON_BAND_DOS_EXTERNAL_REFERENCE_FORBIDDEN");
    if (typeof current.value === "string") {
      const lowered = current.value.toLowerCase();
      if (forbiddenMarkers.some((marker) => lowered.includes(marker)) || /^[a-z]:[\\/]/i.test(current.value) || /^\/(home|users|root|etc)\//i.test(current.value)) errors.add("PHONON_BAND_DOS_EXTERNAL_REFERENCE_FORBIDDEN");
    } else if (Array.isArray(current.value)) current.value.forEach((value) => queue.push({value, key: current.key, depth: current.depth + 1}));
    else if (record(current.value)) Object.entries(current.value).forEach(([key, value]) => queue.push({value, key, depth: current.depth + 1}));
  }
}

function exact(value: JsonRecord, fields: Set<string>): boolean { const keys = Object.keys(value); return keys.length === fields.size && keys.every((key) => fields.has(key)); }
function record(value: unknown): value is JsonRecord { return typeof value === "object" && value !== null && !Array.isArray(value); }
function records(value: unknown): JsonRecord[] { return Array.isArray(value) ? value.filter(record) : []; }
function numbers(value: unknown): number[] { return Array.isArray(value) && value.every(finite) ? value : []; }
function finite(value: unknown): value is number { return typeof value === "number" && Number.isFinite(value) && Math.abs(value) <= 1e12; }
function nonnegativeInteger(value: unknown): value is number { return typeof value === "number" && Number.isSafeInteger(value) && value >= 0; }
function positiveInteger(value: unknown): value is number { return nonnegativeInteger(value) && value > 0; }
function hash(value: unknown): boolean { return typeof value === "string" && /^[0-9a-f]{64}$/.test(value); }
function range(minimum: unknown, maximum: unknown): boolean { return finite(minimum) && finite(maximum) && minimum < maximum; }
