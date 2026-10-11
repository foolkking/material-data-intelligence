export type SavedEnvironmentVertex = Readonly<{ vertexIdentity: string; neighborIdentity: string; neighborSiteId: string; periodicImage: readonly [number, number, number]; relativeCartesian: readonly [number, number, number]; distance: number; distanceUnit: "angstrom" }>;
export type SavedEnvironmentFace = Readonly<{ faceIdentity: string; vertexIdentities: readonly string[] }>;
export type SavedEnvironmentSite = Readonly<{
  environmentIdentity: string;
  polyhedronIdentity: string;
  siteId: string;
  siteIndex: number;
  structureHash: string;
  classification: Readonly<{ status: string; referenceGeometryId: string | null; referenceGeometryVersion: string | null; geometryDistanceRms: number | null; geometryScore: number | null; alternatives: readonly unknown[] }>;
  sourceCoordinationValue: number;
  sourceCoordinationSemantics: string;
  neighborRelationIdentities: readonly string[];
  polyhedron: Readonly<{ status: string; vertices: readonly SavedEnvironmentVertex[]; faces: readonly SavedEnvironmentFace[]; unavailableReason: string | null }>;
  distortionMetrics: Readonly<Record<string, unknown>>;
  warnings: readonly string[];
}>;
export type SavedLocalEnvironment = Readonly<{
  schema_version: "phase10n2.local_environment_polyhedra.v1";
  artifactType: "structure.local_environment_polyhedra";
  tool: Readonly<{ toolId: "structure.local_environment_polyhedra"; toolVersion: "0.1.0"; adapterVersion: "0.1.0" }>;
  algorithm: Readonly<{ classification: string; faceConstruction: string }>;
  referenceCatalog: Readonly<{ catalogId: string; catalogVersion: string; geometryIds: readonly string[] }>;
  resolvedParameters: Readonly<Record<string, unknown>>;
  parameterHash: string;
  scope: Readonly<{ sourceResourceId: string; sourceResourceHash: string; structureHash: string }>;
  sourceCoordination: Readonly<{ artifactId: string; artifactChecksum: string; toolId: string; toolVersion: string; algorithmId: string; algorithmVersion: string; contractVersion: string; parameterHash: string }>;
  coverage: Readonly<{ status: string; requestedSites: number; evaluatedSites: number; unavailableSites: number; classifiedSites: number; ambiguousSites: number; unclassifiedSites: number; ratio: number }>;
  siteResults: readonly SavedEnvironmentSite[];
  warnings: readonly string[];
}>;


/** Detect the saved contract before choosing a viewer; invalid geometry never falls through to a generic plot. */
export function isSavedLocalEnvironment(value: unknown): boolean {
  const record = asRecord(value);
  return record?.schema_version === "phase10n2.local_environment_polyhedra.v1" || record?.artifactType === "structure.local_environment_polyhedra";
}

/** Validate only saved geometry and provenance. This reader never recomputes neighbors or faces. */
export function readSavedLocalEnvironment(value: unknown): SavedLocalEnvironment | null {
  const record = asRecord(value);
  return record?.schema_version === "phase10n2.local_environment_polyhedra.v1"
    && record.artifactType === "structure.local_environment_polyhedra" && isPayload(record)
    ? record as unknown as SavedLocalEnvironment : null;
}

export function algorithmLabel(value: string) { return value === "pymatgen.crystalnn" ? "CrystalNN" : value === "pymatgen.voronoinn" ? "VoronoiNN" : value; }
export function classificationLabel(value: string) { return ({ CLASSIFIED: "已分类", AMBIGUOUS: "分类不唯一", UNCLASSIFIED: "未归类", UNSUPPORTED: "无适用参考" } as Record<string, string>)[value] ?? value; }
export function geometryLabel(value: string | null) { return value ? ({ linear: "直线型", trigonal_planar: "平面三角形", tetrahedral: "四面体", square_planar: "平面正方形", trigonal_bipyramidal: "三角双锥", square_pyramidal: "四方锥", octahedral: "八面体", pentagonal_bipyramidal: "五角双锥", cubic: "立方体" } as Record<string, string>)[value] ?? value : "—"; }
export function faceReason(value: string | null) {
  return ({ POLYHEDRON_FACES_DISABLED: "本次分析未启用表面生成。", INSUFFICIENT_POLYHEDRON_VERTICES: "近邻少于 4 个，未生成封闭多面体。", COPLANAR_POLYHEDRON: "近邻共面，未生成三维封闭多面体。", DEGENERATE_POLYHEDRON: "近邻几何退化，无法构建多面体表面。", POLYHEDRON_FACE_CONSTRUCTION_FAILED: "多面体表面构建未成功，保留已有近邻顶点。" } as Record<string, string>)[value ?? ""] ?? "本次结果没有可用的多面体表面，保留已有近邻顶点。";
}
export function metricLabel(value: string) { return ({ radialDistanceMean: "平均近邻距离", radialDistanceSpread: "近邻距离标准差", bondLengthDistortionIndex: "径向畸变指数", angularRmsDeviation: "角度均方根偏差", geometryDistanceRms: "几何距离 RMS", geometryScore: "几何匹配分数", polyhedronVolume: "多面体体积", polyhedronSurfaceArea: "多面体表面积" } as Record<string, string>)[value] ?? value; }
export function metricUnit(value: string) { return ({ radialDistanceMean: " Å", radialDistanceSpread: " Å", angularRmsDeviation: "°", polyhedronVolume: " Å³", polyhedronSurfaceArea: " Å²" } as Record<string, string>)[value] ?? ""; }

function isPayload(value: Record<string, unknown>): boolean {
  const tool = asRecord(value.tool), scope = asRecord(value.scope), source = asRecord(value.sourceCoordination), coverage = asRecord(value.coverage), algorithm = asRecord(value.algorithm), catalog = asRecord(value.referenceCatalog);
  return Boolean(
    !hasUnsafeValue(value)
    && tool && scope && source && coverage && algorithm && catalog
    && tool.toolId === "structure.local_environment_polyhedra" && tool.toolVersion === "0.1.0" && tool.adapterVersion === "0.1.0"
    && algorithm.classification === "mdi.angular_spectrum_reference_match@1.0.0" && algorithm.faceConstruction === "scipy.spatial.ConvexHull@1.17.1"
    && catalog.catalogId === "mdi.local_geometry_reference_catalog" && catalog.catalogVersion === "1.0.0"
    && Array.isArray(catalog.geometryIds) && catalog.geometryIds.length <= 9 && catalog.geometryIds.every((item) => GEOMETRY_IDS.has(item as string))
    && boundedString(scope.sourceResourceId, 512) && hashString(scope.sourceResourceHash) && hashString(scope.structureHash)
    && boundedString(source.artifactId, 256) && hashString(source.artifactChecksum) && N1_TOOL_IDS.has(source.toolId as string)
    && source.toolVersion === "0.1.0" && N1_ALGORITHM_IDS.has(source.algorithmId as string) && boundedString(source.algorithmVersion, 64)
    && N1_CONTRACTS.has(source.contractVersion as string) && hashString(source.parameterHash)
    && hashString(value.parameterHash) && isSafeRecord(value.resolvedParameters)
    && Array.isArray(value.warnings) && value.warnings.length <= 1000 && value.warnings.every((item) => optionalBoundedString(item, 512))
    && finiteInteger(coverage.requestedSites, 0, 5000) && finiteInteger(coverage.evaluatedSites, 0, 5000) && finiteInteger(coverage.unavailableSites, 0, 5000)
    && finiteInteger(coverage.classifiedSites, 0, 5000) && finiteInteger(coverage.ambiguousSites, 0, 5000) && finiteInteger(coverage.unclassifiedSites, 0, 5000) && finiteNumber(coverage.ratio, 0, 1)
    && Array.isArray(value.siteResults) && value.siteResults.length <= 5000 && value.siteResults.every((item) => isSiteResult(item, scope.structureHash as string))
  );
}

const GEOMETRY_IDS = new Set(["linear", "trigonal_planar", "tetrahedral", "square_planar", "trigonal_bipyramidal", "square_pyramidal", "octahedral", "pentagonal_bipyramidal", "cubic"]);
const N1_TOOL_IDS = new Set(["structure.coordination_crystalnn", "structure.coordination_voronoinn"]);
const N1_ALGORITHM_IDS = new Set(["pymatgen.crystalnn", "pymatgen.voronoinn"]);
const N1_CONTRACTS = new Set(["phase10n1.crystalnn_coordination.v1", "phase10n1.voronoinn_coordination.v1"]);

function isSiteResult(value: unknown, structureHash: string): boolean {
  const site = asRecord(value), classification = asRecord(site?.classification), polyhedron = asRecord(site?.polyhedron), metrics = asRecord(site?.distortionMetrics);
  if (!site || !classification || !polyhedron || !metrics || site.structureHash !== structureHash || !boundedString(site.environmentIdentity, 2048) || !boundedString(site.polyhedronIdentity, 2048) || !boundedString(site.siteId, 256) || !finiteInteger(site.siteIndex, 0, 4999)) return false;
  if (!new Set(["CLASSIFIED", "AMBIGUOUS", "UNCLASSIFIED", "UNSUPPORTED"]).has(classification.status as string) || !nullableGeometryId(classification.referenceGeometryId) || !nullableBoundedString(classification.referenceGeometryVersion, 64) || !nullableFiniteNumber(classification.geometryDistanceRms, 0, 2) || !nullableFiniteNumber(classification.geometryScore, 0, 1) || !Array.isArray(classification.alternatives) || classification.alternatives.length > 7 || !classification.alternatives.every(isClassificationCandidate)) return false;
  if (!new Set(["crystalnn_weight_sum", "voronoinn_solid_angle_weight_sum"]).has(site.sourceCoordinationSemantics as string) || !finiteNumber(site.sourceCoordinationValue, 0, Number.MAX_VALUE) || !Array.isArray(site.neighborRelationIdentities) || site.neighborRelationIdentities.length > 64 || !site.neighborRelationIdentities.every((item) => boundedString(item, 1024))) return false;
  if (!new Set(["AVAILABLE", "UNAVAILABLE"]).has(polyhedron.status as string) || !nullableBoundedString(polyhedron.unavailableReason, 128) || !Array.isArray(polyhedron.vertices) || polyhedron.vertices.length > 64 || !Array.isArray(polyhedron.faces) || polyhedron.faces.length > 128 || !polyhedron.vertices.every(isVertex)) return false;
  const vertexIds = new Set((polyhedron.vertices as Record<string, unknown>[]).map((item) => item.vertexIdentity as string));
  if (vertexIds.size !== polyhedron.vertices.length || (polyhedron.status === "UNAVAILABLE" && polyhedron.faces.length > 0)) return false;
  if (new Set((polyhedron.faces as Record<string, unknown>[]).map((item) => item?.faceIdentity)).size !== polyhedron.faces.length) return false;
  if (!(polyhedron.faces as unknown[]).every((face) => isFace(face, vertexIds))) return false;
  return Object.entries(metrics).every(([key, item]) => boundedString(key, 128) && (item === null || typeof item === "string" ? optionalBoundedString(item, 64) : typeof item === "number" && Number.isFinite(item))) && Array.isArray(site.warnings) && site.warnings.length <= 64 && site.warnings.every((item) => optionalBoundedString(item, 512));
}

function isVertex(value: unknown): boolean {
  const vertex = asRecord(value);
  return Boolean(vertex && boundedString(vertex.vertexIdentity, 1024) && boundedString(vertex.neighborIdentity, 1024) && boundedString(vertex.neighborSiteId, 256) && integerTriplet(vertex.periodicImage) && finiteVector3(vertex.relativeCartesian) && finiteNumber(vertex.distance, 0, Number.MAX_VALUE) && vertex.distanceUnit === "angstrom");
}

function isFace(value: unknown, vertexIds: ReadonlySet<string>): boolean {
  const face = asRecord(value);
  return Boolean(face && boundedString(face.faceIdentity, 3072) && Array.isArray(face.vertexIdentities) && face.vertexIdentities.length === 3 && new Set(face.vertexIdentities).size === 3 && face.vertexIdentities.every((item) => boundedString(item, 1024) && vertexIds.has(item)));
}

function isClassificationCandidate(value: unknown): boolean {
  const candidate = asRecord(value);
  return Boolean(candidate && nullableGeometryId(candidate.referenceGeometryId) && nullableBoundedString(candidate.referenceGeometryVersion, 64) && nullableFiniteNumber(candidate.geometryDistanceRms, 0, 2) && nullableFiniteNumber(candidate.geometryScore, 0, 1));
}

function hasUnsafeValue(value: unknown, depth = 0): boolean {
  if (depth > 12) return true;
  if (typeof value === "number") return !Number.isFinite(value);
  if (value === null || typeof value !== "object") return false;
  if (Array.isArray(value)) return value.some((item) => hasUnsafeValue(item, depth + 1));
  return Object.entries(value as Record<string, unknown>).some(([key, item]) => ["__proto__", "prototype", "constructor"].includes(key) || hasUnsafeValue(item, depth + 1));
}

function asRecord(value: unknown): Record<string, unknown> | null { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function boundedString(value: unknown, maximum: number): value is string { return typeof value === "string" && value.length > 0 && value.length <= maximum && !/[<>]/u.test(value); }
function optionalBoundedString(value: unknown, maximum: number): value is string { return typeof value === "string" && value.length <= maximum && !/[<>]/u.test(value); }
function hashString(value: unknown): value is string { return typeof value === "string" && /^[0-9a-f]{64}$/u.test(value); }
function finiteNumber(value: unknown, minimum: number, maximum: number): value is number { return typeof value === "number" && Number.isFinite(value) && value >= minimum && value <= maximum; }
function finiteInteger(value: unknown, minimum: number, maximum: number): value is number { return finiteNumber(value, minimum, maximum) && Number.isInteger(value); }
function nullableFiniteNumber(value: unknown, minimum: number, maximum: number): boolean { return value === null || finiteNumber(value, minimum, maximum); }
function nullableBoundedString(value: unknown, maximum: number): boolean { return value === null || boundedString(value, maximum); }
function nullableGeometryId(value: unknown): boolean { return value === null || GEOMETRY_IDS.has(value as string); }
function finiteVector3(value: unknown): boolean { return Array.isArray(value) && value.length === 3 && value.every((item) => finiteNumber(item, -Number.MAX_VALUE, Number.MAX_VALUE)); }
function integerTriplet(value: unknown): boolean { return Array.isArray(value) && value.length === 3 && value.every((item) => finiteInteger(item, -2147483648, 2147483647)); }
function isSafeRecord(value: unknown): boolean { return asRecord(value) !== null && !hasUnsafeValue(value); }
