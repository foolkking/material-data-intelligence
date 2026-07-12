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
  const identity = `${String(payload.version)}|${String(payload.schema_version)}`;
  if (!new Set(["viewer_scene.v1|phase10f8.viewer_scene.v1", "viewer_scene.v2|phase10f18.viewer_scene.v2"]).has(identity)) {
    errors.push("VIEWER_SCENE_SCHEMA_VERSION_INVALID");
  }

  scanValue(payload, errors, 0, new Set<object>());
  validateSecurity(payload.security, errors);
  validateCaps(payload.caps, errors);
  validateScene(payload.scene, errors, payload.version);

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

function validateScene(value: unknown, errors: string[], version: unknown) {
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
    if (version === "viewer_scene.v2") validatePeriodicBonds(bonds, sites, indices, lattice?.vectors, errors);
    else for (const bond of bonds) {
      if (!isRecord(bond) || !indices.has(Number(bond.from)) || !indices.has(Number(bond.to))) errors.push("VIEWER_SCENE_BOND_ENDPOINT_INVALID");
      if (isRecord(bond) && "distance" in bond && !finiteNumber(bond.distance)) errors.push("VIEWER_SCENE_BOND_DISTANCE_INVALID");
    }
  }
  if (!Array.isArray(value.cell_expansion) || value.cell_expansion.length !== 3 || value.cell_expansion.some((item) => item !== 1)) {
    errors.push("VIEWER_SCENE_CELL_EXPANSION_LIMIT_EXCEEDED");
  }
}

function validatePeriodicBonds(bonds: unknown[], sites: unknown[], indices: Set<number>, latticeValue: unknown, errors: string[]) {
  const lattice = finiteMatrix(latticeValue) ? latticeValue : null;
  const positions = new Map<number, [number,number,number]>(sites.flatMap((site) => isRecord(site) && typeof site.index === "number" && finiteTriplet(site.xyz) ? [[site.index, site.xyz]] : []));
  const seen = new Set<string>();
  for (const bond of bonds) {
    if (!isRecord(bond) || !validEndpoint(bond.from, indices) || !validEndpoint(bond.to, indices)) { errors.push("VIEWER_SCENE_BOND_ENDPOINT_INVALID"); continue; }
    const from = bond.from; const to = bond.to;
    const topologyKey = canonicalBondKey(from.site_index, to.site_index, to.image_offset);
    const expectedId = `bond:${topologyKey}`;
    if (from.image_offset.join() !== "0,0,0") errors.push("VIEWER_SCENE_PERIODIC_BOND_SOURCE_IMAGE_INVALID");
    if (from.site_index === to.site_index && to.image_offset.join() === "0,0,0") errors.push("VIEWER_SCENE_PERIODIC_BOND_ZERO_SELF_INVALID");
    if (bond.id !== expectedId) errors.push("VIEWER_SCENE_PERIODIC_BOND_ID_INVALID");
    if (seen.has(topologyKey)) errors.push("VIEWER_SCENE_PERIODIC_BOND_DUPLICATE"); else seen.add(topologyKey);
    if (!new Set(["distance_cutoff","explicit_input"]).has(String(bond.source))) errors.push("VIEWER_SCENE_PERIODIC_BOND_SOURCE_INVALID");
    if (typeof bond.authoritative !== "boolean" || (bond.source === "distance_cutoff" && bond.authoritative !== false)) errors.push("VIEWER_SCENE_PERIODIC_BOND_AUTHORITATIVE_INVALID");
    const displacement = bond.displacement_cartesian;
    if (!finiteTriplet(displacement)) errors.push("VIEWER_SCENE_PERIODIC_BOND_DISPLACEMENT_INVALID");
    if (!finiteNumber(bond.distance_angstrom) || bond.distance_angstrom < 0) errors.push("VIEWER_SCENE_BOND_DISTANCE_INVALID");
    const start=positions.get(from.site_index); const target=positions.get(to.site_index);
    if (!lattice || !start || !target) continue;
    const expected = [0,1,2].map((axis)=>target[axis]-start[axis]+to.image_offset.reduce((sum:number,item:number,row:number)=>sum+item*lattice[row][axis],0)) as [number,number,number];
    if (finiteTriplet(displacement) && expected.some((item,index)=>Math.abs(item-displacement[index])>1e-5)) errors.push("VIEWER_SCENE_PERIODIC_BOND_DISPLACEMENT_MISMATCH");
    if (finiteNumber(bond.distance_angstrom) && Math.abs(Math.hypot(...expected)-bond.distance_angstrom)>1e-5) errors.push("VIEWER_SCENE_PERIODIC_BOND_DISTANCE_MISMATCH");
  }
}

function validEndpoint(value: unknown, indices: Set<number>): value is {site_index:number;image_offset:[number,number,number]} {
  return isRecord(value) && Object.keys(value).sort().join() === "image_offset,site_index" && typeof value.site_index === "number" && indices.has(value.site_index) && Array.isArray(value.image_offset) && value.image_offset.length===3 && value.image_offset.every((item)=>Number.isSafeInteger(item)&&Math.abs(item)<=3);
}

function canonicalBondKey(from:number,to:number,offset:[number,number,number]) {
  const forward=[from,to,...offset]; const reverse=[to,from,...offset.map((item)=>-item)];
  const selected=compareNumbers(forward,reverse)<=0?forward:reverse;
  return `${selected[0]}:0,0,0->${selected[1]}:${selected.slice(2).join(",")}`;
}
function compareNumbers(left:number[],right:number[]){for(let index=0;index<left.length;index+=1){if(left[index]!==right[index])return left[index]-right[index];}return 0;}

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
