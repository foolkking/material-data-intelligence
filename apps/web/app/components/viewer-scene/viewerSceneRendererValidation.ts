import type { ViewerSceneValidation } from "./viewerSceneRendererTypes";

type JsonRecord = Record<string, unknown>;

export const VIEWER_SCENE_RENDER_LIMITS = Object.freeze({
  maxSites: 256,
  maxBonds: 2048,
  maxSpecies: 32,
  maxJsonBytes: 1_000_000,
  maxDepth: 16,
  maxStringLength: 16_384,
});

const REQUIRED_FIELDS = ["kind", "version", "schema_version", "source", "metadata", "scene", "validation", "caps", "warnings", "provenance", "security"];
const FORBIDDEN_KEYS = /callback|eval|onload|onerror|onclick|shader|module_path|texture_url|external_resource_(reference|url)|html_payload|script_payload|executable|function/i;
const FORBIDDEN_VALUES = /https?:\/\/|javascript:|<\/?script|<\/?iframe|<\/?object|<\/?embed|eval\s*\(|function\s*\(/i;

export function validateViewerSceneForRenderer(payload: unknown): ViewerSceneValidation {
  const errors: string[] = [];
  const warnings: string[] = [];
  if (!isRecord(payload)) return result(["VIEWER_RENDERER_PAYLOAD_REQUIRED"], warnings);

  try {
    if (new TextEncoder().encode(JSON.stringify(payload)).byteLength > VIEWER_SCENE_RENDER_LIMITS.maxJsonBytes) {
      errors.push("VIEWER_SCENE_JSON_SIZE_LIMIT_EXCEEDED");
    }
  } catch {
    errors.push("VIEWER_SCENE_PAYLOAD_SERIALIZATION_FAILED");
  }

  for (const field of REQUIRED_FIELDS) {
    if (!(field in payload)) errors.push("VIEWER_SCENE_REQUIRED_FIELD_MISSING");
  }
  if (payload.kind !== "viewer_scene") errors.push("VIEWER_SCENE_KIND_INVALID");
  if (payload.version !== "viewer_scene.v1") errors.push("VIEWER_SCENE_VERSION_INVALID");
  if (payload.schema_version !== "phase10f8.viewer_scene.v1") errors.push("VIEWER_SCENE_SCHEMA_VERSION_INVALID");

  scanValue(payload, errors, 0, new Set<object>());
  validateSecurity(payload.security, errors);
  validateCaps(payload.caps, errors);
  validateScene(payload.scene, errors);

  if (Array.isArray(payload.warnings)) {
    for (const warning of payload.warnings) {
      const code = typeof warning === "string" ? warning.split(":", 1)[0] : isRecord(warning) && typeof warning.code === "string" ? warning.code : null;
      if (code) warnings.push(code);
    }
  }
  return result(errors, warnings);
}

function validateSecurity(value: unknown, errors: string[]) {
  if (!isRecord(value)) {
    errors.push("VIEWER_SCENE_SECURITY_REQUIRED");
    return;
  }
  for (const key of ["contains_javascript", "external_urls_allowed", "artifact_supplied_js_allowed", "renderer_required", "remote_assets_allowed", "html_allowed"]) {
    if (value[key] !== false) errors.push("VIEWER_SCENE_SECURITY_FLAG_INVALID");
  }
  if (!Array.isArray(value.external_urls) || value.external_urls.length !== 0) errors.push("VIEWER_SCENE_EXTERNAL_URLS_NOT_EMPTY");
}

function validateCaps(value: unknown, errors: string[]) {
  if (!isRecord(value)) {
    errors.push("VIEWER_SCENE_CAPS_REQUIRED");
    return;
  }
  if (!positiveIntegerAtMost(value.max_sites, VIEWER_SCENE_RENDER_LIMITS.maxSites)) errors.push("VIEWER_SCENE_SITE_LIMIT_INVALID");
  if (!nonNegativeIntegerAtMost(value.max_bonds, VIEWER_SCENE_RENDER_LIMITS.maxBonds)) errors.push("VIEWER_SCENE_BOND_LIMIT_INVALID");
  if (!positiveIntegerAtMost(value.max_species, VIEWER_SCENE_RENDER_LIMITS.maxSpecies)) errors.push("VIEWER_SCENE_SPECIES_LIMIT_INVALID");
  if (!positiveIntegerAtMost(value.max_scene_json_bytes, VIEWER_SCENE_RENDER_LIMITS.maxJsonBytes)) errors.push("VIEWER_SCENE_JSON_SIZE_LIMIT_INVALID");
  if (!Array.isArray(value.max_cell_expansion) || value.max_cell_expansion.length !== 3 || value.max_cell_expansion.some((item) => item !== 1)) {
    errors.push("VIEWER_SCENE_CELL_EXPANSION_LIMIT_EXCEEDED");
  }
}

function validateScene(value: unknown, errors: string[]) {
  if (!isRecord(value)) {
    errors.push("VIEWER_SCENE_SCENE_REQUIRED");
    return;
  }
  if (value.coordinate_basis !== "cartesian_angstrom") errors.push("VIEWER_SCENE_COORDINATE_BASIS_INVALID");
  const sites = Array.isArray(value.sites) ? value.sites : [];
  if (!sites.length) errors.push("VIEWER_SCENE_SITES_REQUIRED");
  if (sites.length > VIEWER_SCENE_RENDER_LIMITS.maxSites) errors.push("VIEWER_SCENE_SITE_LIMIT_EXCEEDED");
  const indices = new Set<number>();
  const species = new Set<string>();
  for (const site of sites) {
    if (!isRecord(site)) {
      errors.push("VIEWER_SCENE_SITE_SHAPE_INVALID");
      continue;
    }
    if (!Number.isInteger(site.index) || typeof site.index !== "number") errors.push("VIEWER_SCENE_SITE_INDEX_INVALID");
    else if (indices.has(site.index)) errors.push("VIEWER_SCENE_SITE_INDEX_DUPLICATE");
    else indices.add(site.index);
    if (typeof site.element !== "string" || !site.element.trim()) errors.push("VIEWER_SCENE_SITE_ELEMENT_INVALID");
    else species.add(site.element);
    if (typeof site.label !== "string" || !site.label.trim()) errors.push("VIEWER_SCENE_SITE_LABEL_INVALID");
    if (!finiteTriplet(site.xyz)) errors.push("VIEWER_SCENE_COORDINATE_NON_FINITE");
    if ("frac" in site && !finiteTriplet(site.frac)) errors.push("VIEWER_SCENE_FRACTIONAL_COORDINATE_NON_FINITE");
  }
  if (species.size > VIEWER_SCENE_RENDER_LIMITS.maxSpecies) errors.push("VIEWER_SCENE_SPECIES_LIMIT_EXCEEDED");

  const lattice = isRecord(value.lattice) ? value.lattice : null;
  if (!lattice || !finiteMatrix(lattice.vectors)) errors.push("VIEWER_SCENE_LATTICE_VECTOR_INVALID");

  const bonds = value.bonds === undefined ? [] : value.bonds;
  if (!Array.isArray(bonds)) errors.push("VIEWER_SCENE_BONDS_SHAPE_INVALID");
  else {
    if (bonds.length > VIEWER_SCENE_RENDER_LIMITS.maxBonds) errors.push("VIEWER_SCENE_BOND_LIMIT_EXCEEDED");
    for (const bond of bonds) {
      if (!isRecord(bond) || !indices.has(Number(bond.from)) || !indices.has(Number(bond.to))) errors.push("VIEWER_SCENE_BOND_ENDPOINT_INVALID");
      if (isRecord(bond) && "distance" in bond && !finiteNumber(bond.distance)) errors.push("VIEWER_SCENE_BOND_DISTANCE_INVALID");
    }
  }
  if (!Array.isArray(value.cell_expansion) || value.cell_expansion.length !== 3 || value.cell_expansion.some((item) => item !== 1)) {
    errors.push("VIEWER_SCENE_CELL_EXPANSION_LIMIT_EXCEEDED");
  }
}

function scanValue(value: unknown, errors: string[], depth: number, seen: Set<object>) {
  if (depth > VIEWER_SCENE_RENDER_LIMITS.maxDepth) {
    errors.push("VIEWER_SCENE_NESTING_LIMIT_EXCEEDED");
    return;
  }
  if (typeof value === "string") {
    if (value.length > VIEWER_SCENE_RENDER_LIMITS.maxStringLength) errors.push("VIEWER_SCENE_STRING_LIMIT_EXCEEDED");
    if (FORBIDDEN_VALUES.test(value)) errors.push("VIEWER_SCENE_FORBIDDEN_STRING_CONTENT");
    return;
  }
  if (typeof value === "number" && !Number.isFinite(value)) errors.push("VIEWER_SCENE_COORDINATE_NON_FINITE");
  if (!value || typeof value !== "object") return;
  if (seen.has(value)) {
    errors.push("VIEWER_SCENE_CYCLIC_VALUE_REJECTED");
    return;
  }
  seen.add(value);
  if (Array.isArray(value)) {
    for (const child of value) scanValue(child, errors, depth + 1, seen);
  } else {
    for (const [key, child] of Object.entries(value)) {
      if (key === "invalid_external_resource_reference") errors.push("VIEWER_SCENE_EXTERNAL_RESOURCE_REFERENCE");
      if (key === "invalid_executable_field") errors.push("VIEWER_SCENE_EXECUTABLE_FIELD");
      if (FORBIDDEN_KEYS.test(key) || key === "__proto__" || key === "constructor" || key === "prototype") errors.push("VIEWER_SCENE_EXECUTABLE_FIELD");
      scanValue(child, errors, depth + 1, seen);
    }
  }
  seen.delete(value);
}

function result(errors: string[], warnings: string[]): ViewerSceneValidation {
  return Object.freeze({ valid: errors.length === 0, errors: Object.freeze([...new Set(errors)].sort()), warnings: Object.freeze([...new Set(warnings)].sort()) });
}

export function isRecord(value: unknown): value is JsonRecord {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

export function finiteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

export function finiteTriplet(value: unknown): value is [number, number, number] {
  return Array.isArray(value) && value.length === 3 && value.every(finiteNumber);
}

function finiteMatrix(value: unknown): value is [[number, number, number], [number, number, number], [number, number, number]] {
  return Array.isArray(value) && value.length === 3 && value.every(finiteTriplet);
}

function positiveIntegerAtMost(value: unknown, cap: number) {
  return Number.isInteger(value) && typeof value === "number" && value > 0 && value <= cap;
}

function nonNegativeIntegerAtMost(value: unknown, cap: number) {
  return Number.isInteger(value) && typeof value === "number" && value >= 0 && value <= cap;
}
