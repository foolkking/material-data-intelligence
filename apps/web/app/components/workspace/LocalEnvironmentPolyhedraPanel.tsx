"use client";

import { useMemo, useState } from "react";

import type { Artifact } from "../../lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext } from "../../lib/workspace-api";
import { coordinationSiteSelection, localEnvironmentSelection } from "./workspace-selection-runtime";

type Point = Readonly<{ vertexIdentity: string; neighborIdentity: string; neighborSiteId: string; periodicImage: readonly [number, number, number]; relativeCartesian: readonly [number, number, number]; distance: number; distanceUnit: "angstrom" }>;
type Face = Readonly<{ faceIdentity: string; vertexIdentities: readonly string[] }>;
type N2SelectionKind = "LOCAL_ENVIRONMENT" | "COORDINATION_POLYHEDRON" | "POLYHEDRON_VERTEX" | "POLYHEDRON_FACE";
type SiteResult = Readonly<{
  environmentIdentity: string;
  polyhedronIdentity: string;
  siteId: string;
  siteIndex: number;
  structureHash: string;
  classification: Readonly<{ status: string; referenceGeometryId: string | null; referenceGeometryVersion: string | null; geometryDistanceRms: number | null; geometryScore: number | null; alternatives: readonly unknown[] }>;
  sourceCoordinationValue: number;
  sourceCoordinationSemantics: string;
  neighborRelationIdentities: readonly string[];
  polyhedron: Readonly<{ status: string; vertices: readonly Point[]; faces: readonly Face[]; unavailableReason: string | null }>;
  distortionMetrics: Readonly<Record<string, unknown>>;
  warnings: readonly string[];
}>;
type Payload = Readonly<{
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
  siteResults: readonly SiteResult[];
  warnings: readonly string[];
}>;

export function LocalEnvironmentPolyhedraPanel({ artifacts, selected, workspace, onSelection }: Readonly<{
  artifacts: readonly Artifact[];
  selected: Artifact;
  workspace: ScientificWorkspace;
  onSelection: (selection: WorkspaceSelectionContext) => void;
}>) {
  const loaded = useMemo(() => artifacts.map(parsePayload).filter((item): item is { artifact: Artifact; payload: Payload } => item !== null), [artifacts]);
  const selectedLoaded = parsePayload(selected);
  const active = selectedLoaded ?? loaded[0] ?? null;
  const [activeSiteId, setActiveSiteId] = useState<string | null>(null);
  if (!active) return <section className="workspace-generic-renderer" role="alert"><h5>Local environment Artifact unavailable</h5><p>N2_LOCAL_ENVIRONMENT_CONTRACT_INVALID</p></section>;
  const site = active.payload.siteResults.find((item) => item.siteId === activeSiteId) ?? active.payload.siteResults[0] ?? null;
  const comparison = loaded.filter((item) => item.payload.scope.sourceResourceHash === active.payload.scope.sourceResourceHash);
  return <section className="workspace-generic-renderer local-environment-result" aria-label="Geometry-derived local environment" data-testid="local-environment-polyhedra-panel">
    <header><div><h5>Geometry-derived local environment</h5><strong>{active.payload.sourceCoordination.algorithmId}</strong></div><span className="status-chip">{active.payload.coverage.status}</span></header>
    <dl className="workspace-artifact-metadata">
      <dt>Source coordination</dt><dd>{active.payload.sourceCoordination.toolId} / {active.payload.sourceCoordination.artifactId}</dd>
      <dt>N2 Tool</dt><dd>{active.payload.tool.toolId}@{active.payload.tool.toolVersion}</dd>
      <dt>Reference catalog</dt><dd>{active.payload.referenceCatalog.catalogId}@{active.payload.referenceCatalog.catalogVersion}</dd>
      <dt>Coverage</dt><dd>{active.payload.coverage.evaluatedSites}/{active.payload.coverage.requestedSites} sites ({formatRatio(active.payload.coverage.ratio)})</dd>
      <dt>Classification</dt><dd>{active.payload.algorithm.classification}</dd>
      <dt>Parameter hash</dt><dd><code>{active.payload.parameterHash}</code></dd>
    </dl>
    {active.payload.warnings.length ? <ul className="workspace-artifact-warning">{active.payload.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul> : null}
    {comparison.length > 1 ? <section><h6>Source algorithm comparison</h6><p>Results remain independent persisted Artifacts; no consensus classification is generated.</p><div className="workspace-table-scroll"><table><thead><tr><th scope="col">Source</th><th scope="col">Artifact</th><th scope="col">Evaluated</th><th scope="col">Classified</th></tr></thead><tbody>{comparison.map((item) => <tr key={item.payload.sourceCoordination.artifactId}><th scope="row">{item.payload.sourceCoordination.algorithmId}</th><td>{item.payload.sourceCoordination.artifactId}</td><td>{item.payload.coverage.evaluatedSites}</td><td>{item.payload.coverage.classifiedSites}</td></tr>)}</tbody></table></div></section> : null}
    <section><h6>Environment results</h6><div className="workspace-table-scroll"><table><thead><tr><th scope="col">Site</th><th scope="col">Status</th><th scope="col">Reference</th><th scope="col">Score</th><th scope="col">Faces</th></tr></thead><tbody>{active.payload.siteResults.slice(0, 250).map((item) => <tr key={item.siteId} className={item.siteId === site?.siteId ? "active" : undefined}><td><button type="button" className="coordination-site-button" aria-pressed={item.siteId === site?.siteId} onClick={() => { setActiveSiteId(item.siteId); onSelection(coordinationSiteSelection(workspace, active.artifact, { sourceResourceId: active.payload.scope.sourceResourceId, structureHash: item.structureHash, siteId: item.siteId })); }}>{item.siteIndex}</button></td><td>{item.classification.status}</td><td>{item.classification.referenceGeometryId ?? "unclassified"}</td><td>{displayNumber(item.classification.geometryScore)}</td><td>{item.polyhedron.faces.length} / {item.polyhedron.status}</td></tr>)}</tbody></table></div></section>
    {site ? <EnvironmentInspector site={site} source={active.payload.sourceCoordination} onExactSelection={(kind, exactId) => onSelection(localEnvironmentSelection(workspace, active.artifact, {
      kind,
      sourceResourceId: active.payload.scope.sourceResourceId,
      structureHash: site.structureHash,
      siteId: site.siteId,
      sourceArtifactId: active.payload.sourceCoordination.artifactId,
      sourceArtifactChecksum: active.payload.sourceCoordination.artifactChecksum,
      environmentId: kind === "LOCAL_ENVIRONMENT" || kind === "COORDINATION_POLYHEDRON" ? site.environmentIdentity : undefined,
      polyhedronId: kind !== "LOCAL_ENVIRONMENT" ? site.polyhedronIdentity : undefined,
      vertexId: kind === "POLYHEDRON_VERTEX" ? exactId : undefined,
      faceId: kind === "POLYHEDRON_FACE" ? exactId : undefined,
      geometryReferenceId: kind === "LOCAL_ENVIRONMENT" || kind === "COORDINATION_POLYHEDRON" ? site.classification.referenceGeometryId : undefined,
    }))} /> : null}
    <details><summary>Resolved parameters and provenance</summary><pre>{JSON.stringify({ parameters: active.payload.resolvedParameters, algorithm: active.payload.algorithm, sourceCoordination: active.payload.sourceCoordination }, null, 2)}</pre></details>
    <p className="workspace-artifact-warning">Geometry-derived and source-algorithm-dependent; not definitive bonding chemistry, oxidation state, or structural stability.</p>
  </section>;
}

function EnvironmentInspector({ site, source, onExactSelection }: Readonly<{ site: SiteResult; source: Payload["sourceCoordination"]; onExactSelection: (kind: N2SelectionKind, exactId?: string) => void }>) {
  return <section aria-label="Selected local environment Inspector"><h6>Site {site.siteIndex} Inspector</h6><p><strong>{site.siteId}</strong> | {site.classification.status} | source {source.algorithmId}</p><div className="workspace-row-actions"><button type="button" onClick={() => onExactSelection("LOCAL_ENVIRONMENT")}>Select environment</button><button type="button" onClick={() => onExactSelection("COORDINATION_POLYHEDRON")}>Select polyhedron</button></div><PolyhedronOverlay vertices={site.polyhedron.vertices} faces={site.polyhedron.faces} faceStatus={site.polyhedron.status} /><div className="workspace-table-scroll"><table><thead><tr><th scope="col">Metric</th><th scope="col">Value</th></tr></thead><tbody>{Object.entries(site.distortionMetrics).map(([key, value]) => <tr key={key}><th scope="row">{key}</th><td>{displayNumber(value)}</td></tr>)}<tr><th scope="row">Source coordination value</th><td>{displayNumber(site.sourceCoordinationValue)}</td></tr><tr><th scope="row">Source coordination semantics</th><td>{site.sourceCoordinationSemantics}</td></tr><tr><th scope="row">Geometry score</th><td>{displayNumber(site.classification.geometryScore)}</td></tr><tr><th scope="row">Geometry distance RMS</th><td>{displayNumber(site.classification.geometryDistanceRms)}</td></tr></tbody></table></div><h6>Exact vertices</h6><div className="workspace-table-scroll"><table><thead><tr><th scope="col">Vertex identity</th><th scope="col">Neighbor</th><th scope="col">Periodic image</th><th scope="col">Relative Cartesian (A)</th></tr></thead><tbody>{site.polyhedron.vertices.map((vertex, index) => <tr key={vertex.vertexIdentity}><td><button type="button" onClick={() => onExactSelection("POLYHEDRON_VERTEX", vertex.vertexIdentity)}>Select vertex {index + 1}</button><br /><code>{vertex.vertexIdentity}</code></td><td><code>{vertex.neighborIdentity}</code></td><td>[{vertex.periodicImage.join(", ")}]</td><td>[{vertex.relativeCartesian.map((value) => displayNumber(value)).join(", ")}]</td></tr>)}</tbody></table></div><h6>Exact faces</h6><div className="workspace-table-scroll"><table><thead><tr><th scope="col">Face</th><th scope="col">Persisted vertex identities</th></tr></thead><tbody>{site.polyhedron.faces.map((face, index) => <tr key={face.faceIdentity}><td><button type="button" onClick={() => onExactSelection("POLYHEDRON_FACE", face.faceIdentity)}>Select face {index + 1}</button><br /><code>{face.faceIdentity}</code></td><td>{face.vertexIdentities.map((identity) => <code key={identity}>{identity}<br /></code>)}</td></tr>)}</tbody></table></div><p>Face status: {site.polyhedron.status}{site.polyhedron.unavailableReason ? ` (${site.polyhedron.unavailableReason})` : ""}. Faces are rendered only from the persisted backend Artifact.</p></section>;
}

function PolyhedronOverlay({ vertices, faces, faceStatus }: Readonly<{ vertices: readonly Point[]; faces: readonly Face[]; faceStatus: string }>) {
  if (vertices.length === 0) return <p role="status">No persisted polyhedron vertices are available. {faceStatus}</p>;
  const xs = vertices.map((vertex) => vertex.relativeCartesian[0]);
  const ys = vertices.map((vertex) => vertex.relativeCartesian[1]);
  const xMin = Math.min(...xs), xSpan = Math.max(...xs) - xMin || 1;
  const yMin = Math.min(...ys), ySpan = Math.max(...ys) - yMin || 1;
  const points = vertices.map((vertex, index) => ({ ...vertex, x: 24 + (vertex.relativeCartesian[0] - xMin) / xSpan * 152, y: 24 + (vertex.relativeCartesian[1] - yMin) / ySpan * 92, index }));
  const byId = new Map(points.map((point) => [point.vertexIdentity, point]));
  return <figure aria-label="Persisted coordination polyhedron overlay"><svg viewBox="0 0 200 140" role="img" aria-label={`Persisted polyhedron with ${vertices.length} vertices and ${faces.length} faces`}><g stroke="currentColor" strokeOpacity="0.6" fill="none">{faces.map((face) => <polygon key={face.faceIdentity} points={face.vertexIdentities.map((id) => byId.get(id)).filter(Boolean).map((point) => `${point!.x},${point!.y}`).join(" ")} />)}</g>{points.map((point) => <circle key={point.vertexIdentity} cx={point.x} cy={point.y} r="4" fill="currentColor"><title>{point.neighborIdentity}</title></circle>)}</svg><figcaption>Persisted backend geometry; visual projection only. {faceStatus}.</figcaption></figure>;
}

function parsePayload(artifact: Artifact): { artifact: Artifact; payload: Payload } | null {
  const value = asRecord(artifact.content ?? artifact.payload);
  if (!value || value.schema_version !== "phase10n2.local_environment_polyhedra.v1" || value.artifactType !== "structure.local_environment_polyhedra") return null;
  if (!isPayload(value)) return null;
  return { artifact, payload: value as unknown as Payload };
}

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
  if (!(polyhedron.faces as unknown[]).every((face) => isFace(face, vertexIds))) return false;
  return Object.entries(metrics).every(([key, item]) => boundedString(key, 128) && (item === null || typeof item === "string" ? optionalBoundedString(item, 64) : typeof item === "number" && Number.isFinite(item))) && Array.isArray(site.warnings) && site.warnings.length <= 64 && site.warnings.every((item) => optionalBoundedString(item, 512));
}

function isVertex(value: unknown): boolean {
  const vertex = asRecord(value);
  return Boolean(vertex && boundedString(vertex.vertexIdentity, 1024) && boundedString(vertex.neighborIdentity, 1024) && boundedString(vertex.neighborSiteId, 256) && integerTriplet(vertex.periodicImage) && finiteVector3(vertex.relativeCartesian) && finiteNumber(vertex.distance, 0, Number.MAX_VALUE) && vertex.distanceUnit === "angstrom");
}

function isFace(value: unknown, vertexIds: ReadonlySet<string>): boolean {
  const face = asRecord(value);
  return Boolean(face && boundedString(face.faceIdentity, 3072) && Array.isArray(face.vertexIdentities) && face.vertexIdentities.length === 3 && face.vertexIdentities.every((item) => boundedString(item, 1024) && vertexIds.has(item)));
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
function displayNumber(value: unknown) { return typeof value === "number" && Number.isFinite(value) ? value.toPrecision(7).replace(/\.?0+$/, "") : "unavailable"; }
function formatRatio(value: number) { return `${(value * 100).toFixed(1)}%`; }
