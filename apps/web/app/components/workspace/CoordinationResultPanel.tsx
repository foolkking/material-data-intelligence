"use client";

import { useMemo, useState } from "react";

import type { Artifact } from "../../lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext } from "../../lib/workspace-api";
import { coordinationSiteSelection } from "./workspace-selection-runtime";

type Neighbor = Readonly<{
  neighborIdentity: string;
  neighborSiteId: string;
  neighborSiteIndex: number;
  periodicImage: readonly [number, number, number];
  distance: number;
  distanceUnit: "angstrom";
  weight: number;
}>;

type SiteResult = Readonly<{
  siteId: string;
  siteIndex: number;
  structureHash: string;
  species: string;
  coordinationSemantics: string;
  coordinationValue: number;
  neighborCount: number;
  neighbors: readonly Neighbor[];
}>;

type CoordinationPayload = Readonly<{
  schema_version: "phase10n1.crystalnn_coordination.v1" | "phase10n1.voronoinn_coordination.v1";
  artifactType: "structure.coordination_crystalnn" | "structure.coordination_voronoinn";
  algorithm: Readonly<{ algorithmId: string; algorithmVersion: string }>;
  library: Readonly<{ name: "pymatgen"; version: string; license: "MIT" }>;
  resolvedParameters: Readonly<Record<string, unknown>>;
  parameterHash: string;
  scope: Readonly<{ sourceResourceId: string; sourceResourceHash: string }>;
  coverage: Readonly<{ status: string; totalSites: number; successfulSites: number; unsupportedSites: number; failedSites: number; ratio: number }>;
  siteResults: readonly SiteResult[];
  warnings: readonly string[];
}>;

type LoadedCoordination = Readonly<{ artifact: Artifact; payload: CoordinationPayload }>;

export function CoordinationResultPanel({
  artifacts,
  selected,
  workspace,
  onSelection,
}: Readonly<{
  artifacts: readonly Artifact[];
  selected: Artifact;
  workspace: ScientificWorkspace;
  onSelection: (selection: WorkspaceSelectionContext) => void;
}>) {
  const loaded = useMemo(() => artifacts.map(parseCoordination).filter((item): item is LoadedCoordination => item !== null), [artifacts]);
  const selectedLoaded = parseCoordination(selected);
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(selected.artifactId ?? selected.id ?? null);
  const active = loaded.find((item) => (item.artifact.artifactId ?? item.artifact.id) === activeArtifactId) ?? selectedLoaded ?? loaded[0] ?? null;
  const [activeSiteId, setActiveSiteId] = useState<string | null>(null);
  const activeSite = active?.payload.siteResults.find((site) => site.siteId === activeSiteId) ?? active?.payload.siteResults[0] ?? null;
  if (!active) return <section className="workspace-generic-renderer" role="alert"><h5>Coordination Artifact unavailable</h5><p>COORDINATION_CONTRACT_INVALID</p></section>;

  const comparable = loaded.filter((item) => item.payload.scope.sourceResourceHash === active.payload.scope.sourceResourceHash);
  const siteRows = active.payload.siteResults.slice(0, 250);
  const comparisonRows = comparisonSites(comparable).slice(0, 250);
  return <section className="workspace-generic-renderer coordination-result" aria-label="Algorithm-derived coordination" data-testid="coordination-result-panel">
    <header>
      <div><h5>Algorithm-derived coordination</h5><strong>{active.payload.algorithm.algorithmId}</strong></div>
      <span className="status-chip">{active.payload.coverage.status}</span>
    </header>
    <div className="coordination-algorithm-switch" role="group" aria-label="Coordination algorithm">
      {comparable.map((item) => {
        const id = item.artifact.artifactId ?? item.artifact.id ?? item.payload.algorithm.algorithmId;
        return <button type="button" key={id} className={item === active ? "active" : "secondary"} aria-pressed={item === active} onClick={() => { setActiveArtifactId(id); setActiveSiteId(null); }}>{algorithmLabel(item.payload)}</button>;
      })}
    </div>
    <dl className="workspace-artifact-metadata">
      <dt>Algorithm</dt><dd>{active.payload.algorithm.algorithmId}@{active.payload.algorithm.algorithmVersion}</dd>
      <dt>Library</dt><dd>{active.payload.library.name}@{active.payload.library.version} ({active.payload.library.license})</dd>
      <dt>Coverage</dt><dd>{active.payload.coverage.successfulSites}/{active.payload.coverage.totalSites} sites ({formatRatio(active.payload.coverage.ratio)})</dd>
      <dt>Parameter hash</dt><dd><code>{active.payload.parameterHash}</code></dd>
      <dt>Source hash</dt><dd><code>{active.payload.scope.sourceResourceHash}</code></dd>
    </dl>
    {active.payload.warnings.length ? <ul className="workspace-artifact-warning">{active.payload.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul> : null}
    {comparisonRows.length && comparable.length > 1 ? <section><h6>Algorithm comparison</h6><div className="workspace-table-scroll"><table><thead><tr><th scope="col">Site</th>{comparable.map((item) => <th scope="col" key={item.payload.algorithm.algorithmId}>{algorithmLabel(item.payload)}</th>)}</tr></thead><tbody>{comparisonRows.map((row) => <tr key={row.siteId}><th scope="row">{row.siteId}</th>{comparable.map((item) => <td key={item.payload.algorithm.algorithmId}>{displayNumber(row.values[item.payload.algorithm.algorithmId])}</td>)}</tr>)}</tbody></table></div></section> : null}
    <section><h6>Site results</h6><div className="workspace-table-scroll"><table><thead><tr><th scope="col">Site</th><th scope="col">Species</th><th scope="col">Coordination</th><th scope="col">Semantics</th><th scope="col">Neighbors</th></tr></thead><tbody>{siteRows.map((site) => <tr key={site.siteId} className={site.siteId === activeSite?.siteId ? "active" : undefined}><td><button type="button" className="coordination-site-button" aria-pressed={site.siteId === activeSite?.siteId} onClick={() => { setActiveSiteId(site.siteId); onSelection(coordinationSiteSelection(workspace, active.artifact, { sourceResourceId: active.payload.scope.sourceResourceId, structureHash: site.structureHash, siteId: site.siteId })); }}>{site.siteIndex}</button></td><td>{site.species}</td><td>{displayNumber(site.coordinationValue)}</td><td>{site.coordinationSemantics}</td><td>{site.neighborCount}</td></tr>)}</tbody></table></div>{active.payload.siteResults.length > siteRows.length ? <p role="status">Showing 250 of {active.payload.siteResults.length} persisted site rows.</p> : null}</section>
    {activeSite ? <section aria-label="Selected site coordination Inspector"><h6>Site {activeSite.siteIndex} neighbor relations</h6><p><strong>{activeSite.siteId}</strong> | {activeSite.coordinationSemantics} | {displayNumber(activeSite.coordinationValue)}</p><div className="workspace-table-scroll"><table><thead><tr><th scope="col">Neighbor</th><th scope="col">Periodic image</th><th scope="col">Distance</th><th scope="col">Weight</th><th scope="col">Exact relation</th></tr></thead><tbody>{activeSite.neighbors.slice(0, 1000).map((neighbor) => <tr key={neighbor.neighborIdentity}><td>{neighbor.neighborSiteIndex}</td><td>[{neighbor.periodicImage.join(", ")}]</td><td>{displayNumber(neighbor.distance)} {neighbor.distanceUnit}</td><td>{displayNumber(neighbor.weight)}</td><td><code>{neighbor.neighborIdentity}</code></td></tr>)}</tbody></table></div></section> : null}
    <details><summary>Resolved parameters</summary><pre>{JSON.stringify(active.payload.resolvedParameters, null, 2)}</pre></details>
    <p className="workspace-artifact-warning">Algorithm-derived local coordination under the stated parameters; not definitive chemical bonding.</p>
  </section>;
}

function parseCoordination(artifact: Artifact): LoadedCoordination | null {
  const value = asRecord(artifact.content ?? artifact.payload);
  if (!value) return null;
  const schema = value?.schema_version;
  const type = value?.artifactType;
  if (!((schema === "phase10n1.crystalnn_coordination.v1" && type === "structure.coordination_crystalnn") || (schema === "phase10n1.voronoinn_coordination.v1" && type === "structure.coordination_voronoinn"))) return null;
  if (!isCoordinationPayload(value)) return null;
  return { artifact, payload: value as unknown as CoordinationPayload };
}

function isCoordinationPayload(value: Record<string, unknown>): boolean {
  const algorithm = asRecord(value.algorithm), library = asRecord(value.library), scope = asRecord(value.scope), coverage = asRecord(value.coverage);
  if (!algorithm || !library || !scope || !coverage || !Array.isArray(value.siteResults) || !Array.isArray(value.warnings)) return false;
  if (!boundedString(algorithm.algorithmId, 128) || !boundedString(algorithm.algorithmVersion, 64)) return false;
  if (library.name !== "pymatgen" || !boundedString(library.version, 64) || library.license !== "MIT") return false;
  if (!boundedString(scope.sourceResourceId, 512) || !hashString(scope.sourceResourceHash)) return false;
  if (!hashString(value.parameterHash) || !asRecord(value.resolvedParameters) || value.siteResults.length > 5_000 || value.warnings.length > 1_000) return false;
  if (!boundedString(coverage.status, 64) || !finiteInteger(coverage.totalSites, 0, 5_000) || !finiteInteger(coverage.successfulSites, 0, 5_000) || !finiteInteger(coverage.unsupportedSites, 0, 5_000) || !finiteInteger(coverage.failedSites, 0, 5_000) || !finiteNumber(coverage.ratio, 0, 1)) return false;
  if (!value.warnings.every((item) => boundedString(item, 512))) return false;
  let neighborRows = 0;
  for (const candidate of value.siteResults) {
    const site = asRecord(candidate);
    if (!site || !boundedString(site.siteId, 512) || !finiteInteger(site.siteIndex, 0, 4_999) || !hashString(site.structureHash) || !boundedString(site.species, 128) || !boundedString(site.coordinationSemantics, 128) || !finiteNumber(site.coordinationValue, 0, 100_000) || !finiteInteger(site.neighborCount, 0, 1_000) || !Array.isArray(site.neighbors) || site.neighbors.length !== site.neighborCount) return false;
    neighborRows += site.neighbors.length;
    if (neighborRows > 50_000) return false;
    for (const candidateNeighbor of site.neighbors) {
      const neighbor = asRecord(candidateNeighbor);
      if (!neighbor || !boundedString(neighbor.neighborIdentity, 1_024) || !boundedString(neighbor.neighborSiteId, 512) || !finiteInteger(neighbor.neighborSiteIndex, 0, 4_999) || !Array.isArray(neighbor.periodicImage) || neighbor.periodicImage.length !== 3 || !neighbor.periodicImage.every((item) => finiteInteger(item, -1_000, 1_000)) || !finiteNumber(neighbor.distance, 0, 1_000_000) || neighbor.distanceUnit !== "angstrom" || !finiteNumber(neighbor.weight, 0, 1_000_000)) return false;
    }
  }
  return true;
}

function comparisonSites(items: readonly LoadedCoordination[]): Array<{ siteId: string; values: Record<string, number> }> {
  const rows = new Map<string, Record<string, number>>();
  for (const item of items) for (const site of item.payload.siteResults) {
    const values = rows.get(site.siteId) ?? {};
    values[item.payload.algorithm.algorithmId] = site.coordinationValue;
    rows.set(site.siteId, values);
  }
  return [...rows.entries()].sort(([left], [right]) => left.localeCompare(right)).map(([siteId, values]) => ({ siteId, values }));
}

function asRecord(value: unknown): Record<string, unknown> | null { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function boundedString(value: unknown, maximum: number): value is string { return typeof value === "string" && value.length > 0 && value.length <= maximum; }
function hashString(value: unknown): value is string { return typeof value === "string" && /^[0-9a-f]{64}$/u.test(value); }
function finiteNumber(value: unknown, minimum: number, maximum: number): value is number { return typeof value === "number" && Number.isFinite(value) && value >= minimum && value <= maximum; }
function finiteInteger(value: unknown, minimum: number, maximum: number): value is number { return finiteNumber(value, minimum, maximum) && Number.isInteger(value); }
function algorithmLabel(payload: CoordinationPayload) { return payload.artifactType.endsWith("crystalnn") ? "CrystalNN" : "VoronoiNN"; }
function displayNumber(value: unknown) { return typeof value === "number" && Number.isFinite(value) ? value.toPrecision(7).replace(/\.?0+$/, "") : "unavailable"; }
function formatRatio(value: number) { return `${(value * 100).toFixed(1)}%`; }
