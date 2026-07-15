import { triangulateFace, BZ_TRIANGLE_CAP } from "./brillouinZoneTriangulation";
import type { BZEdge, BZFace, BZPathVariant, BZPoint, BZScene, BZSegment, BZVector3, BZVertex } from "./brillouinZoneTypes";

export const BZ_RENDERER_CAPS = Object.freeze({
  vertices: 256,
  edges: 512,
  faces: 256,
  triangles: BZ_TRIANGLE_CAP,
  points: 128,
  variants: 8,
  segments: 256,
  labels: 128,
  visibleLabels: 64,
  artifactBytes: 24_000_000,
});

export type BZArtifactBundle = Readonly<{ reciprocal: unknown; zone: unknown; kpath?: unknown; manifest: unknown }>;
export type BZMappingResult = Readonly<
  | { ok: true; scene: BZScene; artifactBytes: number; mappingMs: number; warnings: readonly string[] }
  | { ok: false; code: string; errors: readonly string[]; warnings: readonly string[] }
>;

const HASH = /^[0-9a-f]{64}$/;
const ID = /^[A-Za-z0-9_.:-]{1,128}$/;
const FORBIDDEN_KEYS = new Set(["__proto__", "prototype", "constructor", "script", "shader", "glsl", "texture", "module", "worker", "iframe", "callback", "eval", "function", "html", "css", "onload"]);
const FORBIDDEN_TEXT = ["javascript:", "<script", "<iframe", "http://", "https://", "file://", "data:text/html", "eval(", "new function"];

export function mapBrillouinZoneArtifacts(bundle: BZArtifactBundle): BZMappingResult {
  const started = now();
  const errors = new Set<string>();
  const warnings = new Set<string>();
  const reciprocal = record(bundle.reciprocal);
  const zone = record(bundle.zone);
  const kpath = bundle.kpath === undefined || bundle.kpath === null ? null : record(bundle.kpath);
  const manifest = record(bundle.manifest);
  const artifactBytes = byteLength(bundle);
  if (!reciprocal || !zone || !manifest) return failure("BZ_ARTIFACT_BUNDLE_INVALID", ["BZ_ARTIFACT_BUNDLE_INVALID"]);
  if (artifactBytes > BZ_RENDERER_CAPS.artifactBytes) errors.add("BZ_RENDERER_ARTIFACT_CAP_EXCEEDED");
  scanInert(bundle, errors);
  validateSecurity(reciprocal.security, errors);
  validateSecurity(zone.security, errors);
  if (kpath) validateSecurity(kpath.security, errors);
  validateSecurity(manifest.security, errors);
  if (reciprocal.schema_version !== "phase10i.reciprocal_lattice.v1") errors.add("BZ_RECIPROCAL_SCHEMA_UNSUPPORTED");
  if (zone.schema_version !== "phase10i.brillouin_zone.v1") errors.add("BZ_GEOMETRY_SCHEMA_UNSUPPORTED");
  if (kpath && kpath.schema_version !== "phase10i.kpath.v1") errors.add("BZ_KPATH_SCHEMA_UNSUPPORTED");
  if (manifest.schema_version !== "phase10i.brillouin_zone_manifest.v1") errors.add("BZ_MANIFEST_SCHEMA_UNSUPPORTED");
  for (const item of [reciprocal, manifest]) if (item.convention !== "physics_2pi" || item.units !== "angstrom^-1") errors.add("BZ_RECIPROCAL_CONVENTION_INVALID");
  const reciprocalHash = hash(reciprocal.content_hash);
  const zoneHash = hash(zone.content_hash);
  const kpathHash = kpath ? hash(kpath.content_hash) : null;
  if (!reciprocalHash || !zoneHash || (kpath && !kpathHash) || !hash(manifest.content_hash)) errors.add("BZ_CONTENT_HASH_INVALID");
  const manifestArtifacts = array(manifest.artifacts).map(record).filter(Boolean) as Record<string, unknown>[];
  const manifestHashes = new Map(manifestArtifacts.map((item) => [String(item.name), item.sha256]));
  if (manifestHashes.get("reciprocal_lattice.json") !== reciprocalHash || manifestHashes.get("brillouin_zone.json") !== zoneHash || (kpath && manifestHashes.get("kpath.json") !== kpathHash)) errors.add("BZ_MANIFEST_HASH_MISMATCH");
  const binding = record(reciprocal.real_lattice_binding);
  const zoneBinding = record(zone.reciprocal_lattice_binding);
  const kpathBinding = kpath ? record(kpath.reciprocal_lattice_binding) : null;
  const structureIdentity = hash(manifest.structure_identity);
  const primitiveHash = hash(binding?.primitive_lattice_sha256);
  if (!structureIdentity || binding?.source_structure_sha256 !== structureIdentity || zoneBinding?.source_structure_sha256 !== structureIdentity || (kpathBinding && kpathBinding.source_structure_sha256 !== structureIdentity)) errors.add("BZ_STRUCTURE_BINDING_MISMATCH");
  if (!primitiveHash || zoneBinding?.primitive_lattice_sha256 !== primitiveHash || (kpathBinding && kpathBinding.primitive_lattice_sha256 !== primitiveHash)) errors.add("BZ_PRIMITIVE_BINDING_MISMATCH");
  if (zoneBinding?.reciprocal_lattice_sha256 !== reciprocalHash || (kpathBinding && kpathBinding.reciprocal_lattice_sha256 !== reciprocalHash)) errors.add("BZ_RECIPROCAL_BINDING_MISMATCH");
  const reciprocalMatrix = matrix(reciprocal.matrix, errors, "BZ_RECIPROCAL_MATRIX_INVALID");
  const vertices = mapVertices(zone.vertices, errors);
  const vertexById = new Map(vertices.map((vertex) => [vertex.id, vertex]));
  const edges = mapEdges(zone.edges, vertexById, errors);
  const edgeById = new Map(edges.map((edge) => [edge.id, edge]));
  const faces = mapFaces(zone.faces, vertices, vertexById, edgeById, errors);
  const triangleCount = faces.reduce((sum, face) => sum + face.triangleVertexIndices.length / 3, 0);
  if (vertices.length > BZ_RENDERER_CAPS.vertices || edges.length > BZ_RENDERER_CAPS.edges || faces.length > BZ_RENDERER_CAPS.faces || triangleCount > BZ_RENDERER_CAPS.triangles) errors.add("BZ_RENDERER_GEOMETRY_CAP_EXCEEDED");
  const path = kpath ? mapPath(kpath, errors) : emptyPath();
  if (path.points.length > BZ_RENDERER_CAPS.points || path.segments.length > BZ_RENDERER_CAPS.segments || path.variants.length > BZ_RENDERER_CAPS.variants) errors.add("BZ_RENDERER_PATH_CAP_EXCEEDED");
  if (!kpath) warnings.add("BZ_KPATH_UNAVAILABLE");
  for (const value of [...array(zone.warnings), ...(kpath ? array(kpath.warnings) : [])]) if (safeText(value, 128)) warnings.add(value);
  const topology = record(zone.topology);
  if (topology?.vertex_count !== vertices.length || topology?.edge_count !== edges.length || topology?.face_count !== faces.length) errors.add("BZ_TOPOLOGY_COUNT_MISMATCH");
  const volume = positive(zone.volume, errors, "BZ_VOLUME_INVALID");
  const surfaceArea = positive(zone.surface_area, errors, "BZ_SURFACE_AREA_INVALID");
  const packageId = safeId(manifest.package_id, errors, "BZ_PACKAGE_ID_INVALID");
  const provider = record(kpath?.provider ?? reciprocal.provider);
  if (errors.size || !reciprocalMatrix || !structureIdentity || !reciprocalHash || !zoneHash || !packageId) return failure(errors.has("BZ_RENDERER_GEOMETRY_CAP_EXCEEDED") || errors.has("BZ_RENDERER_PATH_CAP_EXCEEDED") || errors.has("BZ_RENDERER_ARTIFACT_CAP_EXCEEDED") ? "BZ_RENDERER_RESOURCE_LIMIT" : "BZ_RENDERER_VALIDATION_FAILED", [...errors], [...warnings]);
  const visualScale = visualScaleFor(vertices, path.points, reciprocalMatrix);
  const scene: BZScene = Object.freeze({
    structureIdentity,
    packageId,
    reciprocalHash,
    zoneHash,
    kpathHash,
    convention: "physics_2pi",
    units: "angstrom^-1",
    reciprocalMatrix,
    visualScale,
    vertices: Object.freeze(vertices),
    edges: Object.freeze(edges),
    faces: Object.freeze(faces),
    points: Object.freeze(path.points),
    segments: Object.freeze(path.segments),
    variants: Object.freeze(path.variants),
    selectedVariantId: path.selectedVariantId,
    discontinuityIds: Object.freeze(path.discontinuityIds),
    volume,
    surfaceArea,
    provider: Object.freeze({ name: safeText(provider?.name, 64) ? provider.name : "unknown", version: safeText(provider?.version, 64) ? provider.version : "unknown", pathConvention: safeText(kpath?.path_convention, 64) ? kpath.path_convention : "unavailable", timeReversal: kpath?.time_reversal_used === true }),
    warnings: Object.freeze([...warnings].sort()),
  });
  return Object.freeze({ ok: true, scene, artifactBytes, mappingMs: elapsed(started), warnings: scene.warnings });
}

function mapVertices(value: unknown, errors: Set<string>): BZVertex[] {
  const values = array(value);
  if (values.length > BZ_RENDERER_CAPS.vertices) errors.add("BZ_RENDERER_GEOMETRY_CAP_EXCEEDED");
  const ids = new Set<string>();
  return values.flatMap((item, index) => {
    const entry = record(item); const id = safeId(entry?.vertex_id, errors, "BZ_VERTEX_INVALID"); const cartesian = vector(entry?.cartesian_coordinates); const fractional = vector(entry?.fractional_coordinates);
    if (!entry || !id || !cartesian || !fractional || entry.order_index !== index || ids.has(id)) { errors.add("BZ_VERTEX_INVALID"); return []; }
    ids.add(id);
    return [Object.freeze({ id, orderIndex: index, cartesian, fractional, incidentFaceIds: Object.freeze(safeIds(entry.incident_face_ids, errors, "BZ_VERTEX_INVALID")) })];
  });
}

function mapEdges(value: unknown, vertices: Map<string, BZVertex>, errors: Set<string>): BZEdge[] {
  const ids = new Set<string>();
  return array(value).flatMap((item, index) => {
    const entry = record(item); const id = safeId(entry?.edge_id, errors, "BZ_EDGE_INVALID"); const endpointIds = safeIds(entry?.vertex_ids, errors, "BZ_EDGE_INVALID");
    if (!entry || !id || endpointIds.length !== 2 || !vertices.has(endpointIds[0]) || !vertices.has(endpointIds[1]) || endpointIds[0] === endpointIds[1] || entry.order_index !== index || ids.has(id)) { errors.add("BZ_EDGE_INVALID"); return []; }
    ids.add(id); const length = positive(entry.length, errors, "BZ_EDGE_INVALID");
    return [Object.freeze({ id, orderIndex: index, vertexIds: Object.freeze([endpointIds[0], endpointIds[1]]) as readonly [string, string], length, incidentFaceIds: Object.freeze(safeIds(entry.incident_face_ids, errors, "BZ_EDGE_INVALID")) })];
  });
}

function mapFaces(value: unknown, vertices: readonly BZVertex[], vertexById: Map<string, BZVertex>, edgeById: Map<string, BZEdge>, errors: Set<string>): BZFace[] {
  const ids = new Set<string>(); const vertexIndex = new Map(vertices.map((vertex, index) => [vertex.id, index]));
  return array(value).flatMap((item, index) => {
    const entry = record(item); const id = safeId(entry?.face_id, errors, "BZ_FACE_INVALID"); const vertexIds = safeIds(entry?.vertex_ids, errors, "BZ_FACE_INVALID"); const edgeIds = safeIds(entry?.edge_ids, errors, "BZ_FACE_INVALID"); const normal = vector(entry?.outward_normal); const centroid = vector(entry?.centroid); const generator = vector(entry?.generator_cartesian); const hkl = integerTriplet(entry?.generator_hkl); const area = positive(entry?.area, errors, "BZ_FACE_INVALID"); const planeOffset = positive(entry?.plane_offset, errors, "BZ_FACE_INVALID");
    if (!entry || !id || ids.has(id) || entry.order_index !== index || entry.winding !== "ccw_from_outside" || vertexIds.length < 3 || vertexIds.length !== new Set(vertexIds).size || edgeIds.length !== vertexIds.length || vertexIds.some((value) => !vertexById.has(value)) || edgeIds.some((value) => !edgeById.has(value)) || !normal || !centroid || !generator || !hkl) { errors.add("BZ_FACE_INVALID"); return []; }
    ids.add(id);
    try {
      const local = triangulateFace(vertexIds.map((value) => vertexById.get(value)!.cartesian), normal, area);
      const globalIndices = local.indices.map((localIndex) => vertexIndex.get(vertexIds[localIndex])!);
      return [Object.freeze({ id, orderIndex: index, vertexIds: Object.freeze(vertexIds), edgeIds: Object.freeze(edgeIds), area, centroid, outwardNormal: normal, generatorHkl: hkl, generatorCartesian: generator, planeOffset, triangleVertexIndices: Object.freeze(globalIndices) })];
    } catch (error) { errors.add(error instanceof Error ? error.message : "BZ_FACE_TRIANGULATION_FAILED"); return []; }
  });
}

function mapPath(kpath: Record<string, unknown>, errors: Set<string>) {
  const pointEntries = array(kpath.points).map(record).filter(Boolean) as Record<string, unknown>[];
  const segmentEntries = array(kpath.segments).map(record).filter(Boolean) as Record<string, unknown>[];
  const incident = new Map<string, string[]>();
  for (const entry of segmentEntries) for (const key of [entry.start_point_id, entry.end_point_id]) if (typeof key === "string") incident.set(key, [...(incident.get(key) ?? []), String(entry.segment_id)]);
  const pointIds = new Set<string>();
  const points: BZPoint[] = pointEntries.flatMap((entry) => {
    const id = safeId(entry.point_id, errors, "BZ_POINT_INVALID"); const labelKey = safeLabel(entry.label_key); const displayLabel = safeLabel(entry.display_label); const cartesian = vector(entry.cartesian_coordinates); const fractional = vector(entry.fractional_coordinates);
    if (!id || !labelKey || !displayLabel || !cartesian || !fractional || pointIds.has(id)) { errors.add("BZ_POINT_INVALID"); return []; }
    pointIds.add(id); return [Object.freeze({ id, labelKey, displayLabel, aliases: Object.freeze(array(entry.aliases).filter((value): value is string => Boolean(safeLabel(value))).map(String)), fractional, cartesian, incidentSegmentIds: Object.freeze((incident.get(id) ?? []).sort()) })];
  });
  const pointById = new Map(points.map((point) => [point.id, point])); const segmentIds = new Set<string>();
  const segments: BZSegment[] = segmentEntries.flatMap((entry, index) => {
    const id = safeId(entry.segment_id, errors, "BZ_SEGMENT_INVALID"); const variantId = safeId(entry.variant_id, errors, "BZ_SEGMENT_INVALID"); const startPointId = safeId(entry.start_point_id, errors, "BZ_SEGMENT_INVALID"); const endPointId = safeId(entry.end_point_id, errors, "BZ_SEGMENT_INVALID"); const start = startPointId ? pointById.get(startPointId) : undefined; const end = endPointId ? pointById.get(endPointId) : undefined;
    if (!id || !variantId || !startPointId || !endPointId || !start || !end || segmentIds.has(id) || entry.order_index !== index || typeof entry.discontinuity_before !== "boolean" || typeof entry.discontinuity_after !== "boolean") { errors.add("BZ_SEGMENT_INVALID"); return []; }
    segmentIds.add(id); return [Object.freeze({ id, variantId, orderIndex: index, startPointId, endPointId, startLabelKey: start.labelKey, endLabelKey: end.labelKey, start: start.cartesian, end: end.cartesian, length: positive(entry.length, errors, "BZ_SEGMENT_INVALID"), discontinuityBefore: entry.discontinuity_before, discontinuityAfter: entry.discontinuity_after })];
  });
  const variants: BZPathVariant[] = array(kpath.path_variants).flatMap((item) => { const entry = record(item); const id = safeId(entry?.variant_id, errors, "BZ_VARIANT_INVALID"); const segmentIds = safeIds(entry?.segment_ids, errors, "BZ_VARIANT_INVALID"); if (!id || segmentIds.some((value) => !segments.some((segment) => segment.id === value))) { errors.add("BZ_VARIANT_INVALID"); return []; } return [Object.freeze({ id, description: safeText(entry?.description, 128) ? entry.description : id, selected: entry?.selected === true, segmentIds: Object.freeze(segmentIds) })]; });
  const selectedVariantId = typeof kpath.selected_variant_id === "string" ? kpath.selected_variant_id : null;
  if (selectedVariantId && !variants.some((variant) => variant.id === selectedVariantId)) errors.add("BZ_VARIANT_INVALID");
  const discontinuityIds = array(kpath.discontinuities).flatMap((item) => { const entry = record(item); const id = safeId(entry?.discontinuity_id, errors, "BZ_DISCONTINUITY_INVALID"); if (!id || !segments.some((segment) => segment.id === entry?.after_segment_id) || !segments.some((segment) => segment.id === entry?.before_segment_id)) { errors.add("BZ_DISCONTINUITY_INVALID"); return []; } return [id]; });
  return { points, segments, variants, selectedVariantId, discontinuityIds };
}

function emptyPath() { return { points: [] as BZPoint[], segments: [] as BZSegment[], variants: [] as BZPathVariant[], selectedVariantId: null, discontinuityIds: [] as string[] }; }
function visualScaleFor(vertices: readonly BZVertex[], points: readonly BZPoint[], matrixValue: readonly BZVector3[]) { const radius = Math.max(...vertices.map((item) => norm(item.cartesian)), ...points.map((item) => norm(item.cartesian)), ...matrixValue.map(norm), 1e-9); return Math.min(4, Math.max(0.05, 3 / radius)); }
function validateSecurity(value: unknown, errors: Set<string>) { const security = record(value); if (!security || security.contains_javascript !== false || security.contains_html !== false || security.contains_css !== false || security.executable_content_allowed !== false || security.external_urls_allowed !== false || security.renderer_included !== false || array(security.external_urls).length || array(security.executable_assets).length || array(security.remote_assets).length || array(security.shader_sources).length) errors.add("BZ_SECURITY_DECLARATION_INVALID"); }
function scanInert(value: unknown, errors: Set<string>, depth = 0, counter = { value: 0 }) { if (depth > 32 || ++counter.value > 100_000) { errors.add("BZ_ARTIFACT_SCAN_LIMIT_EXCEEDED"); return; } if (typeof value === "string" && FORBIDDEN_TEXT.some((marker) => value.toLowerCase().includes(marker))) errors.add("BZ_ARTIFACT_EXECUTABLE_FIELD"); if (Array.isArray(value)) value.forEach((item) => scanInert(item, errors, depth + 1, counter)); else if (record(value)) for (const [key, item] of Object.entries(value as Record<string, unknown>)) { if (FORBIDDEN_KEYS.has(key.toLowerCase())) errors.add("BZ_ARTIFACT_EXECUTABLE_FIELD"); scanInert(item, errors, depth + 1, counter); } }
function byteLength(bundle: BZArtifactBundle) { try { return new TextEncoder().encode(JSON.stringify(bundle)).byteLength; } catch { return Number.POSITIVE_INFINITY; } }
function record(value: unknown): Record<string, unknown> | null { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function array(value: unknown): unknown[] { return Array.isArray(value) ? value : []; }
function hash(value: unknown): string | null { return typeof value === "string" && HASH.test(value) ? value : null; }
function safeId(value: unknown, errors: Set<string>, code: string): string | null { if (typeof value !== "string" || !ID.test(value)) { errors.add(code); return null; } return value; }
function safeIds(value: unknown, errors: Set<string>, code: string): string[] { const values = array(value); if (values.some((item) => typeof item !== "string" || !ID.test(item))) errors.add(code); return values.filter((item): item is string => typeof item === "string" && ID.test(item)); }
function safeLabel(value: unknown): string | null { return safeText(value, 64) && !/[<>]/.test(value) ? value.normalize("NFC") : null; }
function safeText(value: unknown, max: number): value is string { return typeof value === "string" && value.length > 0 && value.length <= max && !/[\u0000-\u001f\u007f]/.test(value); }
function vector(value: unknown): BZVector3 | null { return Array.isArray(value) && value.length === 3 && value.every((item) => typeof item === "number" && Number.isFinite(item) && Math.abs(item) <= 1e12) ? Object.freeze([value[0], value[1], value[2]]) : null; }
function matrix(value: unknown, errors: Set<string>, code: string): readonly [BZVector3, BZVector3, BZVector3] | null { if (!Array.isArray(value) || value.length !== 3) { errors.add(code); return null; } const rows = value.map(vector); if (rows.some((item) => !item)) { errors.add(code); return null; } return Object.freeze(rows) as readonly [BZVector3, BZVector3, BZVector3]; }
function integerTriplet(value: unknown): readonly [number, number, number] | null { return Array.isArray(value) && value.length === 3 && value.every((item) => Number.isSafeInteger(item) && Math.abs(item) <= 4) ? Object.freeze([value[0], value[1], value[2]]) as readonly [number, number, number] : null; }
function positive(value: unknown, errors: Set<string>, code: string): number { if (typeof value !== "number" || !Number.isFinite(value) || value <= 0) { errors.add(code); return 0; } return value; }
function norm(value: BZVector3) { return Math.hypot(value[0], value[1], value[2]); }
function failure(code: string, errors: readonly string[], warnings: readonly string[] = []): BZMappingResult { return Object.freeze({ ok: false, code, errors: Object.freeze([...new Set(errors)].sort()), warnings: Object.freeze([...new Set(warnings)].sort()) }); }
function now() { return typeof performance === "undefined" ? Date.now() : performance.now(); }
function elapsed(started: number) { return Math.max(0, now() - started); }
