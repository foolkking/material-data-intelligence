"use client";

import type { Artifact } from "../../lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext, WorkspaceSelectionKind } from "../../lib/workspace-api";
import { artifactChecksum, artifactIdentity } from "./workspace-renderer-registry";

type Payload = Record<string, unknown> & { artifactType: "trajectory.rdf" | "trajectory.msd" | "trajectory.diffusion"; schema_version: string; trajectory: Record<string, unknown>; warnings: string[]; limitations: string[] };

export function TrajectoryAnalyticsPanel({ selected, workspace, onSelection }: Readonly<{ artifacts: Artifact[]; selected: Artifact; workspace: ScientificWorkspace; onSelection: (selection: WorkspaceSelectionContext) => void }>) {
  const payload = parse(selected);
  if (!payload) return <section className="workspace-generic-renderer" role="alert"><h5>Trajectory analytics Artifact unavailable</h5><p>N4_TRAJECTORY_ANALYTICS_CONTRACT_INVALID</p></section>;
  return <section className="workspace-generic-renderer" aria-label="Trajectory Analytics" data-testid="trajectory-analytics-panel">
    <header><h5>{title(payload.artifactType)}</h5><p>Persisted backend scientific result. Frontend recomputation is disabled.</p></header>
    {payload.artifactType === "trajectory.rdf" ? <Rdf payload={payload} select={(kind, id, parentId) => emit(workspace, selected, payload, kind, id, parentId, onSelection)} /> : payload.artifactType === "trajectory.msd" ? <Msd payload={payload} select={(kind, id, parentId) => emit(workspace, selected, payload, kind, id, parentId, onSelection)} /> : <Diffusion payload={payload} select={(kind, id, parentId) => emit(workspace, selected, payload, kind, id, parentId, onSelection)} />}
    <h6>Provenance and limits</h6>
    <dl><dt>Trajectory</dt><dd><code>{String(payload.trajectory.trajectoryHash ?? "unavailable")}</code></dd><dt>Contract</dt><dd>{payload.schema_version}</dd></dl>
    {payload.warnings.length > 0 && <p role="status">Warnings: {payload.warnings.join(", ")}</p>}
    <ul>{payload.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
  </section>;
}

function Rdf({ payload, select }: { payload: Payload; select: Select }) {
  const x = numbers(payload.binCentersAngstrom), y = numbers(payload.gR), pair = record(payload.speciesPair), window = record(payload.window), ids = strings(payload.binIds), pairId = String(pair?.pairId ?? "");
  return <><p><strong>Species pair:</strong> {String(pair?.speciesA)}-{String(pair?.speciesB)}; window {String(window?.mode)}. <button type="button" onClick={() => select("TRAJECTORY_RDF_PAIR", pairId)}>Select pair</button></p><div className="workspace-table-scroll"><table><caption>RDF numeric alternative</caption><thead><tr><th scope="col">Selection</th><th scope="col">r (angstrom)</th><th scope="col">g(r)</th></tr></thead><tbody>{x.map((value, index) => <tr key={ids[index] ?? `${value}:${index}`}><td><button type="button" onClick={() => select("TRAJECTORY_RDF_BIN", ids[index], pairId)}>Select</button></td><td>{value}</td><td>{y[index]}</td></tr>)}</tbody></table></div></>;
}

function Msd({ payload, select }: { payload: Payload; select: Select }) {
  const x = numbers(payload.lagTimesPs), total = numbers(payload.totalMsdAngstrom2), directional = record(payload.directionalMsdAngstrom2), origins = numbers(payload.originCounts), ids = strings(payload.lagIds), seriesId = String(payload.seriesId ?? "");
  const xs = numbers(directional?.x), ys = numbers(directional?.y), zs = numbers(directional?.z);
  return <><button type="button" onClick={() => select("TRAJECTORY_MSD_SPECIES", seriesId)}>Select {String(payload.species)} MSD series</button><div className="workspace-table-scroll"><table><caption>MSD numeric alternative</caption><thead><tr><th scope="col">Selection</th><th scope="col">Lag (ps)</th><th scope="col">Total (A^2)</th><th scope="col">x</th><th scope="col">y</th><th scope="col">z</th><th scope="col">Origins</th></tr></thead><tbody>{x.map((value, index) => <tr key={ids[index] ?? `${value}:${index}`}><td><button type="button" onClick={() => select("TRAJECTORY_MSD_LAG", ids[index], seriesId)}>Select</button></td><td>{value}</td><td>{total[index]}</td><td>{xs[index]}</td><td>{ys[index]}</td><td>{zs[index]}</td><td>{origins[index]}</td></tr>)}</tbody></table></div></>;
}

function Diffusion({ payload, select }: { payload: Payload; select: Select }) {
  const fit = record(payload.fit), diagnostic = record(payload.regimeDiagnostic), estimate = record(payload.diffusionEstimate), window = record(payload.fitWindow);
  const windowId = String(window?.windowId ?? ""), diagnosticId = String(diagnostic?.diagnosticId ?? "");
  return <><p role="status"><strong>{String(diagnostic?.status)}</strong> <button type="button" onClick={() => select("TRAJECTORY_DIFFUSION_DIAGNOSTIC", diagnosticId, windowId)}>Select diagnostic</button></p><div className="workspace-table-scroll"><table><caption>Diffusion fit diagnostics</caption><tbody><tr><th scope="row">Fit window (ps)</th><td>{String(window?.startPs)} to {String(window?.endPs)} <button type="button" onClick={() => select("TRAJECTORY_DIFFUSION_WINDOW", windowId)}>Select</button></td></tr><tr><th scope="row">Slope (A^2/ps)</th><td>{String(fit?.slopeAngstrom2PerPs)}</td></tr><tr><th scope="row">R squared</th><td>{String(fit?.rSquared)}</td></tr><tr><th scope="row">Alpha</th><td>{String(diagnostic?.alpha)}</td></tr><tr><th scope="row">Qualified D (A^2/ps)</th><td>{estimate?.available ? String(estimate.value) : "Unavailable"}</td></tr></tbody></table></div></>;
}

type Select = (kind: WorkspaceSelectionKind, id: string, parentId?: string) => void;
function emit(workspace: ScientificWorkspace, artifact: Artifact, payload: Payload, kind: WorkspaceSelectionKind, id: string, parentId: string | undefined, onSelection: (selection: WorkspaceSelectionContext) => void) {
  const artifactId = artifactIdentity(artifact), checksum = artifactChecksum(artifact), trajectoryId = String(payload.trajectory.trajectoryHash ?? "");
  if (!artifactId || !checksum || !workspace.datasetId || !workspace.datasetVersion || !trajectoryId || !id) return;
  const base = { selectionSchemaVersion: "1.0" as const, kind, sourceScopeHash: workspace.sourceReferenceHash, projectId: workspace.projectId, datasetId: workspace.datasetId, datasetVersion: workspace.datasetVersion, jobId: workspace.sourceJobId, trajectoryId, artifactId, artifactChecksum: checksum };
  const identity = kind === "TRAJECTORY_RDF_PAIR" ? { speciesPairId: id } : kind === "TRAJECTORY_RDF_BIN" ? { speciesPairId: parentId, rdfBinId: id } : kind === "TRAJECTORY_MSD_SPECIES" ? { msdSeriesId: id } : kind === "TRAJECTORY_MSD_LAG" ? { msdSeriesId: parentId, msdLagId: id } : kind === "TRAJECTORY_DIFFUSION_WINDOW" ? { diffusionWindowId: id } : { diffusionWindowId: parentId, diffusionDiagnosticId: id };
  onSelection({ schemaVersion: "1.0", sourceScopeHash: workspace.sourceReferenceHash, primary: { ...base, ...identity } as never, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
}

function parse(artifact: Artifact): Payload | null {
  const payload = record(artifact.content ?? artifact.payload);
  const expected: Record<string, string> = { "trajectory.rdf": "phase10n4.trajectory_rdf.v1", "trajectory.msd": "phase10n4.trajectory_msd.v1", "trajectory.diffusion": "phase10n4.trajectory_diffusion.v1" };
  const type = typeof payload?.artifactType === "string" ? payload.artifactType : "";
  if (!payload || expected[type] !== payload.schema_version || !record(payload.trajectory) || !Array.isArray(payload.warnings) || !Array.isArray(payload.limitations)) return null;
  return payload as Payload;
}
function record(value: unknown): Record<string, unknown> | null { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function numbers(value: unknown): number[] { return Array.isArray(value) ? value.filter((item): item is number => typeof item === "number" && Number.isFinite(item)) : []; }
function strings(value: unknown): string[] { return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : []; }
function title(type: Payload["artifactType"]): string { return type === "trajectory.rdf" ? "Trajectory RDF" : type === "trajectory.msd" ? "Trajectory MSD" : "Trajectory Diffusion"; }

export default TrajectoryAnalyticsPanel;
