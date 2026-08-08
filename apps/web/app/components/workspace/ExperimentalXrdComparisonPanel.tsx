"use client";

import { useMemo, useState } from "react";

import type { Artifact } from "../../lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext, WorkspaceSelectionKind } from "../../lib/workspace-api";
import { artifactChecksum, artifactIdentity } from "./workspace-renderer-registry";

type Peak = Readonly<{ peakId: string; twoTheta: number; normalizedIntensity?: number; relativeIntensity?: number; hkls?: readonly unknown[] }>;
type Match = Readonly<{ matchId: string; experimentalPeakId: string; theoreticalPeakId: string; experimentalTwoTheta: number; theoreticalTwoTheta: number; signedDeltaTwoTheta: number; absoluteDeltaTwoTheta: number; theoreticalHkls: readonly unknown[] }>;
type Payload = Readonly<{
  schema_version: "phase10n3.experimental_xrd_comparison.v1";
  artifactType: "structure.experimental_xrd_comparison";
  tool: Readonly<{ toolId: string; toolVersion: string; adapterVersion: string }>;
  experimentalResource: Readonly<{ resourceId: string; resourceHash: string; pointCount: number; wavelength: number; wavelengthUnit: string }>;
  theoreticalArtifact: Readonly<{ artifactId: string; artifactChecksum: string; toolId: string; structureIdentities: readonly string[]; wavelength: number; wavelengthUnit: string }>;
  experimentalSeries: Readonly<{ twoTheta: readonly number[]; normalizedIntensity: readonly number[] }>;
  experimentalPeaks: readonly Peak[];
  theoreticalPeaks: readonly Peak[];
  matches: readonly Match[];
  unmatchedExperimentalPeaks: readonly Peak[];
  unmatchedTheoreticalPeaks: readonly Peak[];
  residualSummary: Readonly<Record<string, number | string | null>>;
  coverage: Readonly<Record<string, number>>;
  matcher: Readonly<{ algorithmId: string; parameters: Readonly<{ matching_tolerance_deg: number }>; parameterHash: string }>;
  peakDetector: Readonly<{ algorithmId: string; libraryVersion: string; parameterHash: string; independentOfTheoreticalMatching: true }>;
  parameterHash: string;
  warnings: readonly string[];
  limitations: readonly string[];
}>;

export function ExperimentalXrdComparisonPanel({ artifacts, selected, workspace, onSelection }: Readonly<{
  artifacts: readonly Artifact[];
  selected: Artifact;
  workspace: ScientificWorkspace;
  onSelection: (selection: WorkspaceSelectionContext) => void;
}>) {
  const parsed = useMemo(() => artifacts.map(parse).filter((item): item is { artifact: Artifact; payload: Payload } => item !== null), [artifacts]);
  const active = parse(selected) ?? parsed[0] ?? null;
  const [selectedIdentity, setSelectedIdentity] = useState<string | null>(null);
  if (!active) return <section className="workspace-generic-renderer" role="alert"><h5>Experimental XRD comparison unavailable</h5><p>N3_XRD_CONTRACT_INVALID</p></section>;
  const payload = active.payload;
  const choose = (kind: WorkspaceSelectionKind, exactId: string) => {
    setSelectedIdentity(exactId);
    const selection = xrdSelection(workspace, active.artifact, payload, kind, exactId);
    if (selection) onSelection(selection);
  };
  return <section className="workspace-generic-renderer experimental-xrd-comparison" aria-label="Experimental XRD peak correspondence" data-testid="experimental-xrd-comparison-panel">
    <header><div><h5>Experimental XRD comparison</h5><p>Peak correspondence under the stated tolerance</p></div><span className="status-chip">{payload.coverage.matchedPairs} matched</span></header>
    <dl className="workspace-artifact-metadata"><dt>Experimental resource</dt><dd>{payload.experimentalResource.resourceId}</dd><dt>Theoretical Artifact</dt><dd>{payload.theoreticalArtifact.artifactId}</dd><dt>Wavelength</dt><dd>{payload.experimentalResource.wavelength} {payload.experimentalResource.wavelengthUnit}</dd><dt>Matching tolerance</dt><dd>+/- {payload.matcher.parameters.matching_tolerance_deg} degree 2theta</dd><dt>Detector</dt><dd>{payload.peakDetector.algorithmId} / SciPy {payload.peakDetector.libraryVersion}</dd><dt>Matcher</dt><dd>{payload.matcher.algorithmId}</dd></dl>
    <XrdOverlay payload={payload} />
    <ResidualTable values={payload.residualSummary} />
    <PeakTable title="Matched peak pairs" empty="No peak pairs met the stated tolerance." rows={payload.matches} identity={(row) => row.matchId} selected={selectedIdentity} onSelect={(row) => choose("XRD_MATCH", row.matchId)} columns={(row) => [row.experimentalTwoTheta, row.theoreticalTwoTheta, row.signedDeltaTwoTheta, row.absoluteDeltaTwoTheta, formatHkls(row.theoreticalHkls)]} headings={["Experimental 2theta", "Theoretical 2theta", "Signed delta", "Absolute delta", "Theoretical hkl metadata"]} />
    <PeakTable title="Unmatched experimental peaks" empty="No unmatched experimental peaks." rows={payload.unmatchedExperimentalPeaks} identity={(row) => row.peakId} selected={selectedIdentity} onSelect={(row) => choose("EXPERIMENTAL_XRD_PEAK", row.peakId)} columns={(row) => [row.twoTheta, row.normalizedIntensity ?? null]} headings={["2theta", "Normalized intensity"]} />
    <PeakTable title="Unmatched theoretical peaks" empty="No unmatched theoretical peaks." rows={payload.unmatchedTheoreticalPeaks} identity={(row) => row.peakId} selected={selectedIdentity} onSelect={(row) => choose("THEORETICAL_XRD_PEAK", row.peakId)} columns={(row) => [row.twoTheta, row.relativeIntensity ?? null, formatHkls(row.hkls ?? [])]} headings={["2theta", "Relative intensity", "hkl metadata"]} />
    {payload.warnings.length ? <ul className="workspace-artifact-warning">{payload.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul> : null}
    <section aria-label="Scientific limitations"><h6>Limitations</h6><ul>{payload.limitations.map((item) => <li key={item}>{item}</li>)}</ul></section>
    <details><summary>Exact provenance</summary><pre>{JSON.stringify({ experimentalResource: payload.experimentalResource, theoreticalArtifact: payload.theoreticalArtifact, detector: payload.peakDetector, matcher: payload.matcher, parameterHash: payload.parameterHash }, null, 2)}</pre></details>
  </section>;
}

function XrdOverlay({ payload }: { payload: Payload }) {
  const x = payload.experimentalSeries.twoTheta;
  const y = payload.experimentalSeries.normalizedIntensity;
  if (!x.length) return <p role="status">No experimental display series is available.</p>;
  let minX = x[0], maxX = x[0], maxY = 0;
  for (let index = 0; index < x.length; index += 1) { minX = Math.min(minX, x[index]); maxX = Math.max(maxX, x[index]); maxY = Math.max(maxY, y[index] ?? 0); }
  const spanX = maxX - minX || 1;
  maxY ||= 1;
  const points = x.map((value, index) => `${20 + (value - minX) / spanX * 560},${170 - y[index] / maxY * 140}`).join(" ");
  return <figure aria-label="Experimental line and theoretical stick XRD comparison"><svg viewBox="0 0 600 190" role="img" aria-label={`${payload.experimentalPeaks.length} detected experimental peaks, ${payload.theoreticalPeaks.length} theoretical peaks, ${payload.matches.length} matches`}><polyline points={points} fill="none" stroke="currentColor" strokeWidth="2" />{payload.theoreticalPeaks.map((peak) => { const px = 20 + (peak.twoTheta - minX) / spanX * 560; return <line key={peak.peakId} x1={px} x2={px} y1="170" y2="120" stroke="var(--color-accent, #b23a48)" strokeWidth="2"><title>Theoretical peak {peak.twoTheta} degree</title></line>; })}{payload.experimentalPeaks.map((peak) => { const px = 20 + (peak.twoTheta - minX) / spanX * 560; return <circle key={peak.peakId} cx={px} cy="24" r="4" fill="currentColor"><title>Detected experimental peak {peak.twoTheta} degree</title></circle>; })}</svg><figcaption>Experimental line, theoretical sticks and detected markers. Tables below contain all scientific numbers and match states.</figcaption></figure>;
}

function ResidualTable({ values }: { values: Payload["residualSummary"] }) { return <section><h6>Position residual summary</h6><div className="workspace-table-scroll"><table><tbody>{Object.entries(values).map(([key, value]) => <tr key={key}><th scope="row">{key}</th><td>{value === null ? "not available" : String(value)}</td></tr>)}</tbody></table></div></section>; }

function PeakTable<T>({ title, empty, rows, identity, selected, onSelect, columns, headings }: Readonly<{ title: string; empty: string; rows: readonly T[]; identity: (row: T) => string; selected: string | null; onSelect: (row: T) => void; columns: (row: T) => readonly unknown[]; headings: readonly string[] }>) {
  return <section><h6>{title}</h6>{rows.length === 0 ? <p role="status">{empty}</p> : <div className="workspace-table-scroll"><table><thead><tr><th scope="col">Selection</th>{headings.map((heading) => <th scope="col" key={heading}>{heading}</th>)}</tr></thead><tbody>{rows.slice(0, 10_000).map((row) => { const id = identity(row); return <tr key={id} className={selected === id ? "active" : undefined}><td><button type="button" aria-pressed={selected === id} onClick={() => onSelect(row)}>Select</button><br /><code>{id}</code></td>{columns(row).map((value, index) => <td key={`${id}:${index}`}>{value === null ? "n/a" : String(value)}</td>)}</tr>; })}</tbody></table></div>}</section>;
}

function xrdSelection(workspace: ScientificWorkspace, artifact: Artifact, payload: Payload, kind: WorkspaceSelectionKind, exactId: string): WorkspaceSelectionContext | null {
  const artifactId = artifactIdentity(artifact), checksum = artifactChecksum(artifact);
  if (!artifactId || !checksum || !workspace.datasetId || !workspace.datasetVersion) return null;
  const base = {
    selectionSchemaVersion: "1.0" as const, kind, sourceScopeHash: workspace.sourceReferenceHash,
    projectId: workspace.projectId, datasetId: workspace.datasetId, datasetVersion: workspace.datasetVersion,
    jobId: workspace.sourceJobId, artifactId, artifactChecksum: checksum,
    experimentalResourceId: payload.experimentalResource.resourceId,
    theoreticalArtifactId: payload.theoreticalArtifact.artifactId,
  };
  const primary = kind === "XRD_MATCH" ? { ...base, matchId: exactId } : { ...base, peakId: exactId };
  return { schemaVersion: "1.0", sourceScopeHash: workspace.sourceReferenceHash, primary: primary as never, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false };
}

function parse(artifact: Artifact): { artifact: Artifact; payload: Payload } | null { const value = record(artifact.content ?? artifact.payload); if (!value || value.schema_version !== "phase10n3.experimental_xrd_comparison.v1" || value.artifactType !== "structure.experimental_xrd_comparison" || hasUnsafe(value)) return null; const resource = record(value.experimentalResource), theory = record(value.theoreticalArtifact); if (!resource || !theory || !Array.isArray(value.experimentalPeaks) || !Array.isArray(value.theoreticalPeaks) || !Array.isArray(value.matches) || !Array.isArray(value.unmatchedExperimentalPeaks) || !Array.isArray(value.unmatchedTheoreticalPeaks)) return null; return { artifact, payload: value as unknown as Payload }; }
function record(value: unknown): Record<string, unknown> | null { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function hasUnsafe(value: unknown, depth = 0): boolean { if (depth > 24) return true; if (typeof value === "string") return /<script|javascript:|https?:\/\//iu.test(value); if (Array.isArray(value)) return value.length > 250_000 || value.some((item) => hasUnsafe(item, depth + 1)); if (record(value)) return Object.entries(record(value)!).some(([key, item]) => ["__proto__", "prototype", "constructor"].includes(key) || hasUnsafe(item, depth + 1)); return typeof value === "number" && !Number.isFinite(value); }
function formatHkls(value: readonly unknown[]): string { return value.length ? JSON.stringify(value).slice(0, 500) : "none"; }

export default ExperimentalXrdComparisonPanel;
