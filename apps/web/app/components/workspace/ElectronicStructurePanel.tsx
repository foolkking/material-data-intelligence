"use client";

import type { Artifact } from "../../lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext, WorkspaceSelectionKind } from "../../lib/workspace-api";
import { artifactChecksum, artifactIdentity } from "./workspace-renderer-registry";

type Payload = Record<string, unknown> & { artifactType: "electronic.band_structure" | "electronic.dos"; schemaVersion: string; sourceResource: Record<string, unknown>; warnings: string[]; limitations: string[] };

export function ElectronicStructurePanel({ artifacts, selected, workspace, onSelection }: Readonly<{ artifacts: Artifact[]; selected: Artifact; workspace: ScientificWorkspace; onSelection: (selection: WorkspaceSelectionContext) => void }>) {
  const current = parse(selected);
  if (!current) return <section className="workspace-generic-renderer" role="alert"><h5>Electronic Structure Artifact unavailable</h5><p>N5_ELECTRONIC_CONTRACT_INVALID</p></section>;
  const parsed = artifacts.map((artifact) => ({ artifact, payload: parse(artifact) })).filter((item): item is { artifact: Artifact; payload: Payload } => item.payload !== null);
  const band = parsed.find((item) => item.payload.artifactType === "electronic.band_structure") ?? (current.artifactType === "electronic.band_structure" ? { artifact: selected, payload: current } : null);
  const dos = parsed.find((item) => item.payload.artifactType === "electronic.dos") ?? (current.artifactType === "electronic.dos" ? { artifact: selected, payload: current } : null);
  const compatible = band && dos ? compatibility(band.payload, dos.payload) : null;
  return <section className="workspace-generic-renderer" aria-label="Electronic Structure" data-testid="electronic-structure-panel">
    <header><h5>Electronic Structure</h5><p>Persisted supplied-output analysis. The platform does not perform DFT or GW calculations.</p></header>
    {band ? <BandView artifact={band.artifact} payload={band.payload} workspace={workspace} onSelection={onSelection} /> : <p role="status">Band Structure Artifact not available.</p>}
    {dos ? <DosView artifact={dos.artifact} payload={dos.payload} workspace={workspace} onSelection={onSelection} /> : <p role="status">DOS Artifact not available.</p>}
    <section aria-label="Band and DOS combined compatibility" data-testid="electronic-combined-status">
      <h6>Band + DOS</h6>
      <p role="status">{compatible === null ? "Combined view requires both persisted Artifacts." : compatible ? "Exact compatible source, energy-reference, Fermi and spin semantics." : "DO_NOT_COMBINE: electronic source semantics are incompatible."}</p>
    </section>
    <h6>Inspector provenance</h6>
    <dl><dt>Tool</dt><dd>{String(record(current.tool)?.toolId)}@{String(record(current.tool)?.toolVersion)}</dd><dt>Resource</dt><dd><code>{String(current.sourceResource.resourceHash)}</code></dd><dt>Calculation</dt><dd>{String(current.sourceResource.calculationIdentity)}</dd><dt>Contract</dt><dd>{current.schemaVersion}</dd></dl>
    {current.warnings.length > 0 && <p role="status">Warnings: {current.warnings.join(", ")}</p>}
    <ul>{current.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
  </section>;
}

function BandView({ artifact, payload, workspace, onSelection }: PanelItemProps) {
  const gap = record(payload.gap), bands = records(payload.bands), kpoints = records(payload.kpoints), states = records(payload.states);
  return <section aria-label="Electronic band structure" data-testid="electronic-band-view"><h6>Band Structure</h6>
    <p><strong>Sampled gap:</strong> {gap?.valueEv === null || gap?.valueEv === undefined ? "Unavailable" : `${String(gap.valueEv)} eV`} · {String(gap?.directness)} · {String(gap?.classification)} <button type="button" onClick={() => emit(workspace, artifact, payload, "ELECTRONIC_BAND_GAP", {}, onSelection)}>Select gap</button></p>
    <svg viewBox="0 0 640 220" role="img" aria-label="Supplied band curves; numeric values are available in the table" data-testid="electronic-band-plot"><title>Supplied electronic band curves</title>{bands.slice(0, 48).map((band, index) => <polyline key={String(band.bandIdentity)} fill="none" stroke={String(band.spinChannel) === "down" ? "#b42318" : "#176b87"} strokeDasharray={String(band.spinChannel) === "down" ? "6 4" : undefined} strokeWidth="2" points={polyline(numbers(band.energiesEv), index, bands)} />)}</svg>
    <div className="workspace-table-scroll"><table><caption>Band state numeric alternative</caption><thead><tr><th>Selection</th><th>Spin</th><th>Band</th><th>k-point</th><th>Coordinate</th><th>Energy (eV)</th></tr></thead><tbody>{states.slice(0, 500).map((state) => { const point = kpoints.find((item) => item.kpointId === state.kpointId); return <tr key={String(state.stateId)}><td><button type="button" onClick={() => emit(workspace, artifact, payload, "ELECTRONIC_BAND_STATE", { spinChannelId: state.spinChannel, bandId: state.bandId, kpointId: state.kpointId, bandStateId: state.stateId }, onSelection)}>Select</button></td><td>{String(state.spinChannel)}</td><td>{String(state.bandId)}</td><td>{String(state.kpointId)}</td><td>{Array.isArray(point?.fractionalCoordinates) ? point.fractionalCoordinates.join(", ") : ""}</td><td>{String(state.energyEv)}</td></tr>; })}</tbody></table></div>
  </section>;
}

function DosView({ artifact, payload, workspace, onSelection }: PanelItemProps) {
  const energies = numbers(payload.energiesEv), points = strings(payload.energyPointIds), total = records(payload.totalDos), projections = records(payload.projections), channels = [...total, ...projections];
  return <section aria-label="Electronic density of states" data-testid="electronic-dos-view"><h6>Density of States</h6><p><strong>Projection coverage:</strong> {String(payload.projectionCompleteness)} · <strong>Unit:</strong> {String(payload.dosUnitSemantic)}</p>
    <svg viewBox="0 0 640 220" role="img" aria-label="Supplied DOS channels; numeric values are available in the table" data-testid="electronic-dos-plot"><title>Supplied electronic DOS</title>{channels.slice(0, 24).map((channel, index) => <polyline key={String(channel.channelIdentity)} fill="none" stroke={String(channel.spinChannel) === "down" ? "#b42318" : index === 0 ? "#176b87" : "#627d32"} strokeDasharray={String(channel.spinChannel) === "down" ? "6 4" : undefined} strokeWidth="2" points={polyline(numbers(channel.values), index, channels)} />)}</svg>
    <div className="workspace-table-scroll"><table><caption>DOS numeric alternative</caption><thead><tr><th>Selection</th><th>Channel</th><th>Spin</th><th>Energy (eV)</th><th>DOS</th></tr></thead><tbody>{channels.flatMap((channel) => energies.slice(0, 500).map((energy, index) => <tr key={`${String(channel.channelIdentity)}:${points[index]}`}><td><button type="button" onClick={() => emit(workspace, artifact, payload, "ELECTRONIC_DOS_POINT", { spinChannelId: channel.spinChannel, dosChannelId: channel.channelId, projectionId: channel.projectionKind ? channel.channelIdentity : undefined, energyPointId: points[index] }, onSelection)}>Select</button></td><td>{String(channel.label ?? channel.channelId)}</td><td>{String(channel.spinChannel)}</td><td>{energy}</td><td>{numbers(channel.values)[index]}</td></tr>))}</tbody></table></div>
  </section>;
}

type PanelItemProps = Readonly<{ artifact: Artifact; payload: Payload; workspace: ScientificWorkspace; onSelection: (selection: WorkspaceSelectionContext) => void }>;
function emit(workspace: ScientificWorkspace, artifact: Artifact, payload: Payload, kind: WorkspaceSelectionKind, identity: Record<string, unknown>, onSelection: (selection: WorkspaceSelectionContext) => void) {
  const artifactId = artifactIdentity(artifact), checksum = artifactChecksum(artifact), electronicResourceId = String(payload.sourceResource.resourceId ?? "");
  if (!artifactId || !checksum || !workspace.datasetId || !workspace.datasetVersion || !electronicResourceId) return;
  const primary = { selectionSchemaVersion: "1.0", kind, sourceScopeHash: workspace.sourceReferenceHash, projectId: workspace.projectId, datasetId: workspace.datasetId, datasetVersion: workspace.datasetVersion, jobId: workspace.sourceJobId, artifactId, artifactChecksum: checksum, electronicResourceId, ...identity } as never;
  onSelection({ schemaVersion: "1.0", sourceScopeHash: workspace.sourceReferenceHash, primary, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
}

function compatibility(band: Payload, dos: Payload): boolean {
  const be = record(band.energy), de = record(dos.energy), bs = record(band.spin), ds = record(dos.spin);
  const bf = be?.fermiEnergyEv, df = de?.fermiEnergyEv;
  return band.sourceResource.calculationIdentity === dos.sourceResource.calculationIdentity && JSON.stringify(band.sourceResource.structureIdentity ?? null) === JSON.stringify(dos.sourceResource.structureIdentity ?? null) && be?.unit === de?.unit && be?.reference === de?.reference && bs?.mode === ds?.mode && ((bf == null && df == null) || (typeof bf === "number" && typeof df === "number" && Math.abs(bf - df) <= 1e-8));
}

function parse(artifact: Artifact): Payload | null {
  const payload = record(artifact.content ?? artifact.payload), type = payload?.artifactType;
  const expected: Record<string, string> = { "electronic.band_structure": "phase10n5.electronic_band_structure.v1", "electronic.dos": "phase10n5.electronic_dos.v1" };
  if (!payload || !boundedJson(payload) || typeof type !== "string" || expected[type] !== payload.schemaVersion || !record(payload.sourceResource) || !record(payload.tool) || !record(payload.energy) || !record(payload.spin) || !Array.isArray(payload.warnings) || !Array.isArray(payload.limitations)) return null;
  if (type === "electronic.band_structure" && (!Array.isArray(payload.kpoints) || !Array.isArray(payload.bands) || !Array.isArray(payload.states) || !record(payload.gap))) return null;
  if (type === "electronic.dos" && (!Array.isArray(payload.energiesEv) || !Array.isArray(payload.energyPointIds) || !Array.isArray(payload.totalDos) || !Array.isArray(payload.projections))) return null;
  return payload as Payload;
}
function polyline(values: number[], offset: number, all: Array<Record<string, unknown>>): string { const flat = all.flatMap((item) => numbers(item.energiesEv ?? item.values)); const min = Math.min(...flat, 0), max = Math.max(...flat, 1), range = max - min || 1; return values.map((value, index) => `${20 + index * (600 / Math.max(1, values.length - 1))},${200 - ((value - min) / range) * 180 + (offset % 2) * 0}`).join(" "); }
function record(value: unknown): Record<string, unknown> | null { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function records(value: unknown): Array<Record<string, unknown>> { return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => record(item) !== null) : []; }
function numbers(value: unknown): number[] { return Array.isArray(value) ? value.filter((item): item is number => typeof item === "number" && Number.isFinite(item)) : []; }
function strings(value: unknown): string[] { return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : []; }
function boundedJson(value: unknown, depth = 0): boolean {
  if (depth > 12) return false;
  if (value === null || typeof value === "string" || typeof value === "boolean") return true;
  if (typeof value === "number") return Number.isFinite(value);
  if (Array.isArray(value)) return value.length <= 500_000 && value.every((item) => boundedJson(item, depth + 1));
  if (typeof value !== "object" || Object.getPrototypeOf(value) !== Object.prototype) return false;
  const entries = Object.entries(value as Record<string, unknown>);
  return entries.length <= 1_024 && entries.every(([key, item]) => !["__proto__", "constructor", "prototype", "html", "javascript", "iframe", "url"].includes(key.toLowerCase()) && boundedJson(item, depth + 1));
}

export default ElectronicStructurePanel;
