import type {
  ValidatedVolumetricBundle,
  ValidatedVolumetricField,
  VolumetricFieldCompatibility,
} from "./volumetricViewerTypes";

export const ELF_ORBITAL_PRODUCT_CAPS = Object.freeze({
  maximumElfFields: 8,
  maximumOrbitalFields: 8,
  maximumFieldSelectorOptions: 8,
  maximumActivePayloads: 1,
  maximumCachedPayloads: 2,
  maximumCachedMeshes: 4,
  maximumIdentityEntries: 16,
  maximumIdentityTextBytes: 2048,
  maximumLabelLength: 96,
  maximumManifestBytes: 16_384,
} as const);

export type ElfOrbitalProductKind = "elf" | "orbital_density" | "unavailable";
export type ProductRangeStatus = "VALID_RANGE" | "NUMERIC_TOLERANCE_WARNING" | "SOURCE_RANGE_ANOMALY" | "INVALID_NON_FINITE";
export type OrbitalIdentityCompleteness = "FULL" | "PARTIAL" | "UNAVAILABLE";

export type ElfOrbitalRangeValidation = Readonly<{
  status: ProductRangeStatus;
  dtype: "float32" | "float64";
  tolerance: number;
  tolerancePolicy: "ELF_ORBITAL_DTYPE_SCALE_TOLERANCE_V1";
  minimum: number;
  maximum: number;
  belowZeroCount: number;
  aboveOneCount: number;
  negativeCount: number;
  maximumLowerViolation: number;
  maximumUpperViolation: number;
  calculationMs: number;
  fieldContentHash: string;
}>;

export type ElfOrbitalSourceIdentity = Readonly<{
  completeness: OrbitalIdentityCompleteness;
  displayName: string;
  sourceFormat: string;
  sourceSha256: string;
  sourceFieldId: string;
  sourceFieldHash: string;
  parser: string;
  parserVersion: string;
  orbitalId: null;
  bandIndex: null;
  kPointIndex: null;
  spinChannel: string | null;
  occupancy: null;
  energy: null;
  selection: null;
  authority: "canonical_source_metadata";
}>;

export type ElfOrbitalPreset = Readonly<{
  id: string;
  label: string;
  exactIsovalue: number;
  unit: string;
  fieldContentHash: string;
  version: "ELF_ORBITAL_PRESETS_V1";
  interpretation: "display_contour_only";
}>;

export type ElfOrbitalProduct = Readonly<{
  schemaVersion: "phase10j5.elf_orbital_product.v1";
  kind: ElfOrbitalProductKind;
  status: "ready" | "scientific_anomaly" | "unavailable";
  title: string;
  compatibility: Readonly<{ compatible: boolean; reasons: readonly string[] }>;
  datasetId: string;
  datasetContentHash: string;
  manifestContentHash: string;
  sourceFieldId: string | null;
  sourceFieldHash: string | null;
  quantity: string | null;
  unit: string | null;
  normalizationSemantics: string | null;
  integralSemantics: string | null;
  integral: number | null;
  integralUnit: string | null;
  integralInterpretation: string;
  identity: ElfOrbitalSourceIdentity | null;
  rangeValidation: ElfOrbitalRangeValidation | null;
  presets: readonly ElfOrbitalPreset[];
  warnings: readonly string[];
  scientificLimitations: readonly string[];
  security: Readonly<{
    sourceImmutable: true;
    artifactCode: false;
    externalResources: false;
    arbitraryNormalization: false;
    filenameAuthority: false;
  }>;
}>;

const LIMITATIONS = Object.freeze([
  "Isosurfaces show spatial sets at exact source values; they are not ELF basin or chemical-bond classifications.",
  "No orbital reconstruction, HOMO/LUMO inference, orbital-character assignment, occupancy inference, or complex phase is performed.",
  "No enclosed-surface electron count or probability is computed.",
] as const);

export function detectElfOrbitalProduct(bundle: ValidatedVolumetricBundle, sourceFieldId?: string): Readonly<{
  kind: ElfOrbitalProductKind;
  field: VolumetricFieldCompatibility | null;
  compatibleFields: readonly VolumetricFieldCompatibility[];
  reasons: readonly string[];
}> {
  const scopedFields = sourceFieldId
    ? bundle.fields.filter((item) => item.field.fieldId === sourceFieldId)
    : bundle.fields;
  const elf = scopedFields.filter((item) => item.field.quantity === "electron_localization_function");
  const orbital = scopedFields.filter((item) => item.field.quantity === "orbital_density");
  const candidates = elf.length ? elf : orbital;
  const kind: ElfOrbitalProductKind = elf.length ? "elf" : orbital.length ? "orbital_density" : "unavailable";
  const cap = kind === "elf" ? ELF_ORBITAL_PRODUCT_CAPS.maximumElfFields : ELF_ORBITAL_PRODUCT_CAPS.maximumOrbitalFields;
  const reasons: string[] = [];
  if (!candidates.length) reasons.push("ELF_ORBITAL_PRODUCT_QUANTITY_UNAVAILABLE");
  if (candidates.length > cap) reasons.push("ELF_ORBITAL_PRODUCT_FIELD_CAP_EXCEEDED");
  for (const item of candidates) {
    if (!item.supported || item.field.valueKind !== "real" || item.field.fieldRank !== "scalar" || item.field.storedComponentCount !== 1) reasons.push("ELF_ORBITAL_PRODUCT_REAL_SCALAR_REQUIRED");
    if (kind === "elf" && item.field.unit !== "dimensionless") reasons.push("ELF_PRODUCT_UNIT_INVALID");
    if (kind === "orbital_density" && !["electron/angstrom^3", "angstrom^-3"].includes(item.field.unit)) reasons.push("ORBITAL_DENSITY_UNIT_INVALID");
  }
  const uniqueReasons = Object.freeze([...new Set(reasons)].sort());
  return Object.freeze({
    kind,
    field: uniqueReasons.length ? null : candidates[0] ?? null,
    compatibleFields: Object.freeze(uniqueReasons.length ? [] : [...candidates]),
    reasons: uniqueReasons,
  });
}

export function validateElfOrbitalValues(
  values: ArrayLike<number>,
  dtype: "float32" | "float64",
  kind: Exclude<ElfOrbitalProductKind, "unavailable">,
  fieldContentHash: string,
): ElfOrbitalRangeValidation {
  const started = performance.now();
  let minimum = Number.POSITIVE_INFINITY;
  let maximum = Number.NEGATIVE_INFINITY;
  let belowZeroCount = 0;
  let aboveOneCount = 0;
  let negativeCount = 0;
  let finite = true;
  for (let index = 0; index < values.length; index += 1) {
    const value = Number(values[index]);
    if (!Number.isFinite(value)) { finite = false; continue; }
    minimum = Math.min(minimum, value);
    maximum = Math.max(maximum, value);
    if (value < 0) { belowZeroCount += 1; negativeCount += 1; }
    if (value > 1) aboveOneCount += 1;
  }
  const scale = Math.max(1, Math.abs(minimum), Math.abs(maximum));
  const tolerance = (dtype === "float32" ? 64 * 2 ** -23 : 256 * Number.EPSILON) * scale;
  const lower = Math.max(0, -minimum);
  const upper = kind === "elf" ? Math.max(0, maximum - 1) : 0;
  let status: ProductRangeStatus;
  if (!finite || !Number.isFinite(minimum) || !Number.isFinite(maximum)) status = "INVALID_NON_FINITE";
  else if (kind === "elf" && (lower > tolerance || upper > tolerance) || kind === "orbital_density" && lower > tolerance) status = "SOURCE_RANGE_ANOMALY";
  else if (lower > 0 || upper > 0) status = "NUMERIC_TOLERANCE_WARNING";
  else status = "VALID_RANGE";
  return Object.freeze({
    status, dtype, tolerance, tolerancePolicy: "ELF_ORBITAL_DTYPE_SCALE_TOLERANCE_V1",
    minimum, maximum, belowZeroCount, aboveOneCount, negativeCount,
    maximumLowerViolation: lower, maximumUpperViolation: upper,
    calculationMs: performance.now() - started, fieldContentHash,
  });
}

export function buildElfOrbitalProduct(
  bundle: ValidatedVolumetricBundle,
  rangeValidation: ElfOrbitalRangeValidation | null = null,
  sourceFieldId?: string,
): ElfOrbitalProduct {
  const detection = detectElfOrbitalProduct(bundle, sourceFieldId);
  const selected = sourceFieldId
    ? detection.compatibleFields.find((item) => item.field.fieldId === sourceFieldId) ?? null
    : detection.field;
  if (!selected) return freezeProduct({
    kind: "unavailable", status: "unavailable", title: "ELF / Orbital volumetric product unavailable",
    compatibility: { compatible: false, reasons: detection.reasons }, datasetId: bundle.datasetId,
    datasetContentHash: bundle.datasetContentHash, manifestContentHash: bundle.manifestContentHash,
    sourceFieldId: null, sourceFieldHash: null, quantity: null, unit: null,
    normalizationSemantics: null, integralSemantics: null, integral: null, integralUnit: null,
    integralInterpretation: "No compatible source field is available.", identity: null, rangeValidation: null,
    presets: [], warnings: detection.reasons, scientificLimitations: LIMITATIONS,
  });
  const field = selected.field;
  const kind = detection.kind as Exclude<ElfOrbitalProductKind, "unavailable">;
  const identity = kind === "orbital_density" ? sourceIdentity(bundle, field) : null;
  const warnings = [...bundle.warnings, ...field.warnings];
  if (rangeValidation?.status === "NUMERIC_TOLERANCE_WARNING") warnings.push(kind === "elf" ? "ELF_NUMERIC_RANGE_TOLERANCE_WARNING" : "ORBITAL_DENSITY_NUMERIC_NEGATIVE_WARNING");
  if (rangeValidation?.status === "SOURCE_RANGE_ANOMALY") warnings.push(kind === "elf" ? "ELF_SOURCE_RANGE_ANOMALY" : "ORBITAL_DENSITY_SOURCE_RANGE_ANOMALY");
  if (kind === "orbital_density" && identity?.completeness === "UNAVAILABLE") warnings.push("ORBITAL_SOURCE_IDENTITY_UNAVAILABLE");
  const presets = kind === "elf" ? [0.5, 0.7, 0.8, 0.9].map((value) => preset(`elf-${value.toFixed(2)}`, `ELF ${value.toFixed(2)}`, value, field)) : orbitalPresets(field);
  return freezeProduct({
    kind,
    status: rangeValidation?.status === "SOURCE_RANGE_ANOMALY" || rangeValidation?.status === "INVALID_NON_FINITE" ? "scientific_anomaly" : "ready",
    title: kind === "elf" ? "Electron Localization Function" : "Source-defined partial density",
    compatibility: { compatible: true, reasons: [] }, datasetId: bundle.datasetId,
    datasetContentHash: bundle.datasetContentHash, manifestContentHash: bundle.manifestContentHash,
    sourceFieldId: field.fieldId, sourceFieldHash: field.contentHash, quantity: field.quantity, unit: field.unit,
    normalizationSemantics: field.normalizationSemantics, integralSemantics: field.integralSemantics,
    integral: field.integral, integralUnit: integralUnit(field), integralInterpretation: integralInterpretation(field, kind),
    identity, rangeValidation, presets, warnings: [...new Set(warnings)].sort(), scientificLimitations: LIMITATIONS,
  });
}

function sourceIdentity(bundle: ValidatedVolumetricBundle, field: ValidatedVolumetricField): ElfOrbitalSourceIdentity {
  return Object.freeze({
    completeness: field.spin?.channel ? "PARTIAL" : "UNAVAILABLE",
    displayName: "Source-defined partial density", sourceFormat: bundle.sourceFormat,
    sourceSha256: bundle.sourceSha256, sourceFieldId: field.fieldId, sourceFieldHash: field.contentHash,
    parser: field.provenance.producer, parserVersion: field.provenance.producerVersion,
    orbitalId: null, bandIndex: null, kPointIndex: null, spinChannel: field.spin?.channel ?? null,
    occupancy: null, energy: null, selection: null, authority: "canonical_source_metadata",
  });
}

function orbitalPresets(field: ValidatedVolumetricField): readonly ElfOrbitalPreset[] {
  const maximum = Math.max(0, field.maximum);
  return [0.1, 0.25, 0.5].map((fraction, index) => preset(`orbital-${index + 1}`, ["Low contour", "Medium contour", "High contour"][index], maximum * fraction, field));
}

function preset(id: string, label: string, value: number, field: ValidatedVolumetricField): ElfOrbitalPreset {
  return Object.freeze({ id, label, exactIsovalue: value, unit: field.unit, fieldContentHash: field.contentHash, version: "ELF_ORBITAL_PRESETS_V1", interpretation: "display_contour_only" });
}

function integralUnit(field: ValidatedVolumetricField): string {
  if (field.unit === "dimensionless") return "angstrom^3";
  if (field.unit === "electron/angstrom^3") return "electron";
  if (field.unit === "angstrom^-3") return "dimensionless";
  return `${field.unit}*angstrom^3`;
}

function integralInterpretation(field: ValidatedVolumetricField, kind: Exclude<ElfOrbitalProductKind, "unavailable">): string {
  if (kind === "elf") return "Full-cell volume integral of source ELF samples; not an electron count or basin population.";
  if (field.integralSemantics === "electron_count") return "Source-declared full-cell electron-count integral; not automatically an occupancy or single-orbital probability.";
  if (field.normalizationSemantics === "normalized_to_unit_integral") return "Source-declared unit-integral field; no occupancy inference is made.";
  return "Full-cell source-grid integral with no occupancy or probability interpretation.";
}

function freezeProduct(value: Omit<ElfOrbitalProduct, "schemaVersion" | "security">): ElfOrbitalProduct {
  const result = {
    schemaVersion: "phase10j5.elf_orbital_product.v1" as const,
    ...value,
    compatibility: Object.freeze({ ...value.compatibility, reasons: Object.freeze([...value.compatibility.reasons]) }),
    presets: Object.freeze([...value.presets]), warnings: Object.freeze([...value.warnings]),
    scientificLimitations: Object.freeze([...value.scientificLimitations]),
    security: Object.freeze({ sourceImmutable: true as const, artifactCode: false as const, externalResources: false as const, arbitraryNormalization: false as const, filenameAuthority: false as const }),
  };
  const bytes = new TextEncoder().encode(JSON.stringify(result)).byteLength;
  if (bytes > ELF_ORBITAL_PRODUCT_CAPS.maximumManifestBytes) throw new Error("ELF_ORBITAL_PRODUCT_MANIFEST_CAP_EXCEEDED");
  return Object.freeze(result);
}
