"use client";

import { useEffect, useMemo, useReducer, useRef, useState } from "react";

import type { Artifact } from "../../lib/planner-api";
import { BrillouinZoneSurface } from "../brillouin-zone/BrillouinZoneSurface";
import type { BZRendererEngineFactory, BZSelection } from "../brillouin-zone/brillouinZoneTypes";
import { phononAnimationHandoff } from "../phonon-band/PhononBandPreviewPanel";
import { buildBandBZLinkModel } from "./bandBZLinkModel";
import { effectiveReciprocalSelection, EMPTY_RECIPROCAL_SELECTION, reciprocalSelectionReducer } from "./bandBZLinkState";
import type { BandBZLinkModel, ReciprocalSelection } from "./bandBZLinkTypes";

type JsonRecord = Record<string, unknown>;
type MobileTab = "band" | "bz" | "inspector";

export function BandBZLinkedView({ artifacts, capabilityOverride, engineFactory }: { artifacts: readonly Artifact[]; capabilityOverride?: boolean; engineFactory?: BZRendererEngineFactory }) {
  const bandArtifact = find(artifacts, "phonon_band_json", "phonon_band.json");
  const reciprocalArtifact = find(artifacts, "reciprocal_lattice_json", "reciprocal_lattice.json");
  const zoneArtifact = find(artifacts, "brillouin_zone_json", "brillouin_zone.json");
  const kpathArtifact = find(artifacts, "kpath_json", "kpath.json");
  const manifestArtifact = find(artifacts, "brillouin_zone_manifest_json", "brillouin_zone_manifest.json");
  const animationArtifact = find(artifacts, "phonon_animation_json", "phonon_animation.json");
  const bundle = useMemo(() => bandArtifact && reciprocalArtifact && zoneArtifact && kpathArtifact && manifestArtifact ? {
    band: payload(bandArtifact),
    bandHash: bandArtifact.sha256 ?? bandArtifact.contentHash ?? "",
    bz: { reciprocal: payload(reciprocalArtifact), zone: payload(zoneArtifact), kpath: payload(kpathArtifact), manifest: payload(manifestArtifact) },
    animation: payload(animationArtifact),
  } : null, [bandArtifact, reciprocalArtifact, zoneArtifact, kpathArtifact, manifestArtifact, animationArtifact]);
  const result = useMemo(() => bundle ? buildBandBZLinkModel(bundle) : null, [bundle]);
  const [selectionState, dispatch] = useReducer(reciprocalSelectionReducer, EMPTY_RECIPROCAL_SELECTION);
  const [branchIndex, setBranchIndex] = useState(0);
  const [mobileTab, setMobileTab] = useState<MobileTab>("band");
  const [mobile, setMobile] = useState(false);
  const transaction = useRef(0);
  useEffect(() => { dispatch({ type: "artifacts_changed" }); setBranchIndex(0); }, [bundle]);
  useEffect(() => { if (typeof window === "undefined" || !window.matchMedia) return; const query=window.matchMedia("(max-width: 760px)");const update=()=>setMobile(query.matches);update();query.addEventListener?.("change",update);return()=>query.removeEventListener?.("change",update); }, []);
  if (!bandArtifact || !reciprocalArtifact || !zoneArtifact || !manifestArtifact) return null;
  if (!bundle || !result) return <LinkedFallback errors={["BAND_BZ_REQUIRED_ARTIFACT_MISSING"]} warnings={[]} />;
  if (!result.ok) return <LinkedFallback errors={result.errors} warnings={result.warnings} />;
  const model = result.model;
  const effective = effectiveReciprocalSelection(selectionState);
  const nextTransaction = () => ++transaction.current;
  const sampleSelection = (qpointIndex: number, sourcePanel: ReciprocalSelection["sourcePanel"], pinned: boolean): ReciprocalSelection => {
    const sample = model.samples[qpointIndex];
    const frequency = model.branches[branchIndex]?.frequencies[qpointIndex];
    const handoff = animationArtifact ? phononAnimationHandoff(payload(bandArtifact) as JsonRecord, bandArtifact, payload(animationArtifact) as JsonRecord) : { ok: false as const, code: "PHONON_ANIMATION_EIGENVECTOR_UNAVAILABLE" };
    const modeId = handoff.ok && handoff.qpointIndex === qpointIndex && handoff.branchIndex === branchIndex ? handoff.modeId : undefined;
    return Object.freeze({ sourcePanel, kind: modeId ? "phonon_mode" : "sampled_reciprocal_point", transactionId: nextTransaction(), pinned, bandArtifactHash: model.bandArtifactHash, bzArtifactHash: model.bzArtifactHash, pathVariantId: model.pathVariantId, bzSegmentId: sample.bzSegmentId, pointOccurrenceId: sample.pointOccurrenceId ?? undefined, qpointIndex, branchIndex, modeId, frequency, t: sample.t, reciprocalFractional: sample.fractional, reciprocalCartesian: sample.cartesian, pathDistance: sample.pathDistance, residual: sample.residual });
  };
  const selectSample = (qpointIndex: number, pinned: boolean, sourcePanel: ReciprocalSelection["sourcePanel"] = "band") => dispatch({ type: pinned ? "pin" : "hover", selection: sampleSelection(qpointIndex, sourcePanel, pinned) });
  const selectFromBZ = (selection: BZSelection | null) => {
    if (!selection) { dispatch({ type: "clear" }); return; }
    if (selection.kind === "point") {
      const occurrence = model.pointOccurrences.find((item) => item.bzPointId === selection.id);
      if (!occurrence) return;
      dispatch({ type: "pin", selection: Object.freeze({ sourcePanel: "bz", kind: "high_symmetry_point", transactionId: nextTransaction(), pinned: true, bandArtifactHash: model.bandArtifactHash, bzArtifactHash: model.bzArtifactHash, pathVariantId: model.pathVariantId, bzPointId: selection.id, pointOccurrenceId: occurrence.id, qpointIndex: occurrence.qpointIndex, reciprocalFractional: occurrence.fractional, reciprocalCartesian: occurrence.cartesian, pathDistance: model.samples[occurrence.qpointIndex].pathDistance, residual: occurrence.residual }) });
      return;
    }
    if (selection.kind === "segment") {
      const segment = model.segments.find((item) => item.bzSegmentId === selection.id);
      if (!segment) return;
      dispatch({ type: "pin", selection: Object.freeze({ sourcePanel: "bz", kind: "path_segment", transactionId: nextTransaction(), pinned: true, bandArtifactHash: model.bandArtifactHash, bzArtifactHash: model.bzArtifactHash, pathVariantId: model.pathVariantId, bzSegmentId: selection.id, discontinuity: segment.discontinuityBefore }) });
    }
  };
  const bzSelection = toBZSelection(effective);
  const animation = animationArtifact ? phononAnimationHandoff(payload(bandArtifact) as JsonRecord, bandArtifact, payload(animationArtifact) as JsonRecord) : { ok: false as const, code: "PHONON_ANIMATION_EIGENVECTOR_UNAVAILABLE" };
  const handoffAvailable = Boolean(effective?.modeId && animation.ok && effective.modeId === animation.modeId);
  return <section className="band-bz-linked-view" data-testid="band-bz-linked-view" aria-label="Linked phonon band and Brillouin zone view" tabIndex={0} onKeyDown={(event) => { if (event.key === "Escape") dispatch({ type: "clear" }); }}>
    <header className="band-bz-compatibility" data-testid="band-bz-compatibility-header"><div><h2>Linked Phonon Band and Brillouin Zone</h2><p>Exact ordered reciprocal-path geometry; display labels are never scientific keys.</p></div><strong data-testid="band-bz-compatibility-status">{model.status}</strong><dl><div><dt>structure</dt><dd>{short(model.structureIdentity)}</dd></div><div><dt>primitive lattice</dt><dd>{short(model.primitiveLatticeHash)}</dd></div><div><dt>convention</dt><dd>{model.convention}</dd></div><div><dt>provider</dt><dd>{model.provider.name} {model.provider.version}</dd></div><div><dt>variant</dt><dd>{model.pathVariantId}</dd></div><div><dt>time reversal</dt><dd>BZ {String(model.timeReversal.bz)} / band undeclared</dd></div></dl></header>
    <div className="band-bz-mobile-tabs" role="tablist" aria-label="Linked view panels">{(["band","bz","inspector"] as const).map((tab) => <button key={tab} role="tab" type="button" aria-selected={mobileTab === tab} className={mobileTab === tab ? "active" : "secondary"} onClick={() => setMobileTab(tab)}>{tab === "bz" ? "3D BZ" : tab}</button>)}</div>
    <div className="band-bz-grid">
      <div className={`band-bz-panel band-bz-band ${mobileTab !== "band" ? "mobile-hidden" : ""}`}><LinkedBandChart model={model} branchIndex={branchIndex} selection={effective} onBranch={setBranchIndex} onHover={(index) => selectSample(index, false)} onLeave={(id) => dispatch({ type: "leave", transactionId: id })} onPin={(index, source) => selectSample(index, true, source)} /></div>
      <div className={`band-bz-panel band-bz-bz ${mobileTab !== "bz" ? "mobile-hidden" : ""}`}>{!mobile||mobileTab==="bz"?<BrillouinZoneSurface bundle={bundle.bz} capabilityOverride={capabilityOverride} engineFactory={engineFactory} externalSelection={bzSelection} onSelection={selectFromBZ} />:<p role="status">3D BZ paused while another mobile linked-view tab is active.</p>}</div>
    </div>
    <div className={`band-bz-shared-inspector ${mobileTab !== "inspector" ? "mobile-hidden" : ""}`} data-testid="band-bz-shared-inspector"><h3>Shared reciprocal selection</h3>{effective ? <SelectionDetails selection={effective} /> : <p>No reciprocal selection. Hover is transient; click or keyboard activation pins a selection.</p>}<div className="band-bz-inspector-actions"><button type="button" onClick={() => dispatch({ type: "clear" })}>Clear selection</button><button type="button" disabled={!handoffAvailable} onClick={() => document.querySelector('[data-testid="phonon-animation-preview-panel"]')?.scrollIntoView({ behavior: "smooth", block: "start" })}>Open phonon animation</button><span data-testid="band-bz-animation-status">{handoffAvailable ? "Exact canonical mode handoff available" : animation.ok ? "Select the exact bound q-point and branch" : animation.code}</span></div></div>
    <ul className="warning-list">{model.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>
    <output className="sr-only" aria-live="polite" data-testid="band-bz-live-status">{effective ? `Selected ${effective.kind}, q-point ${effective.qpointIndex ?? "not applicable"}, branch ${effective.branchIndex ?? "not selected"}.` : "Linked reciprocal view ready."}</output>
    <pre hidden data-testid="band-bz-link-metrics">{JSON.stringify({ ...model.metrics, revision: selectionState.revision, canvasExpected: mobileTab === "bz" || typeof window === "undefined" ? 1 : 0, externalRequests: 0 })}</pre>
  </section>;
}

function LinkedBandChart({ model, branchIndex, selection, onBranch, onHover, onLeave, onPin }: { model: BandBZLinkModel; branchIndex: number; selection: ReciprocalSelection | null; onBranch: (value: number) => void; onHover: (index: number) => void; onLeave: (transactionId: number) => void; onPin: (index: number, source: ReciprocalSelection["sourcePanel"]) => void }) {
  const width = 720, height = 360, margin = 44;
  const minX = Math.min(...model.samples.map((item) => item.pathDistance)), maxX = Math.max(...model.samples.map((item) => item.pathDistance));
  const frequencies = model.branches.flatMap((item) => [...item.frequencies]);
  const minY = Math.min(...frequencies), maxY = Math.max(...frequencies);
  const x = (value: number) => margin + (value - minX) / Math.max(maxX - minX, 1e-12) * (width - margin * 2);
  const y = (value: number) => height - margin - (value - minY) / Math.max(maxY - minY, 1e-12) * (height - margin * 2);
  const traceBudget = model.branches.length * model.segments.length <= 4096 ? model.branches : [model.branches[branchIndex]];
  return <section aria-label="Linked phonon band chart"><div className="band-bz-panel-heading"><h3>Phonon band</h3><label>Branch <select data-testid="band-bz-branch" value={branchIndex} onChange={(event) => onBranch(Number(event.target.value))}>{model.branches.map((branch) => <option key={branch.branchIndex} value={branch.branchIndex}>{branch.branchIndex}</option>)}</select></label></div>
    <svg className="band-bz-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Phonon frequencies along the linked reciprocal path" data-testid="band-bz-chart">
      <line x1={margin} y1={height-margin} x2={width-margin} y2={height-margin} /><line x1={margin} y1={margin} x2={margin} y2={height-margin} />
      {traceBudget.flatMap((branch) => model.segments.map((segment) => { const samples = model.samples.filter((item) => item.segmentIndex === segment.bandSegmentIndex); const points = samples.map((sample) => `${x(sample.pathDistance)},${y(branch.frequencies[sample.qpointIndex])}`).join(" "); return <polyline key={`${branch.branchIndex}:${segment.bandSegmentIndex}`} points={points} className={branch.branchIndex === branchIndex ? "selected-branch" : "band-branch"} />; }))}
      {model.samples.map((sample) => { const selected = selection?.qpointIndex === sample.qpointIndex && selection.branchIndex === branchIndex; return <circle key={sample.qpointIndex} cx={x(sample.pathDistance)} cy={y(model.branches[branchIndex].frequencies[sample.qpointIndex])} r={selected ? 6 : 3} className={selected ? "selected-sample" : "band-sample"} tabIndex={0} data-qpoint-index={sample.qpointIndex} onMouseEnter={() => onHover(sample.qpointIndex)} onMouseLeave={() => { if (selection && !selection.pinned) onLeave(selection.transactionId); }} onClick={() => onPin(sample.qpointIndex, "band")} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); onPin(sample.qpointIndex, "band"); } }} />; })}
    </svg>
    <div className="compact-table-wrap"><table className="compact-table" data-testid="band-bz-sample-table"><caption>Linked samples for selected branch {branchIndex}</caption><thead><tr><th>q index</th><th>segment</th><th>t</th><th>frequency THz</th><th>coordinates</th><th>select</th></tr></thead><tbody>{model.samples.slice(0,128).map((sample) => <tr key={sample.qpointIndex}><td>{sample.qpointIndex}</td><td>{sample.segmentIndex}</td><td>{sample.t.toFixed(6)}</td><td>{model.branches[branchIndex].frequencies[sample.qpointIndex].toFixed(6)}</td><td>[{sample.fractional.map(format).join(", ")}]</td><td><button type="button" onClick={() => onPin(sample.qpointIndex, "table")}>Select</button></td></tr>)}</tbody></table></div>
  </section>;
}

function SelectionDetails({ selection }: { selection: ReciprocalSelection }) { return <dl className="mini-grid"><div><dt>source</dt><dd>{selection.sourcePanel}</dd></div><div><dt>kind</dt><dd>{selection.kind}</dd></div><div><dt>q-point</dt><dd>{selection.qpointIndex ?? "not selected"}</dd></div><div><dt>branch</dt><dd>{selection.branchIndex ?? "not inferred"}</dd></div><div><dt>mode ID</dt><dd>{selection.modeId ?? "unavailable"}</dd></div><div><dt>frequency</dt><dd>{selection.frequency === undefined ? "not selected" : `${selection.frequency.toFixed(6)} THz`}</dd></div><div><dt>BZ point</dt><dd>{selection.bzPointId ?? "interior/segment"}</dd></div><div><dt>BZ segment</dt><dd>{selection.bzSegmentId ?? "not applicable"}</dd></div><div><dt>t</dt><dd>{selection.t === undefined ? "not applicable" : selection.t.toFixed(8)}</dd></div><div><dt>fractional q</dt><dd>{selection.reciprocalFractional ? `[${selection.reciprocalFractional.map(format).join(", ")}]` : "not applicable"}</dd></div><div><dt>Cartesian q</dt><dd>{selection.reciprocalCartesian ? `[${selection.reciprocalCartesian.map(format).join(", ")}] angstrom^-1` : "not applicable"}</dd></div><div><dt>mapping residual</dt><dd>{selection.residual?.toExponential(3) ?? "not applicable"}</dd></div></dl>; }
function LinkedFallback({ errors, warnings }: { errors: readonly string[]; warnings: readonly string[] }) { return <section className="panel band-bz-linked-fallback" data-testid="band-bz-linked-fallback" role="status"><h2>Band-BZ linked view unavailable</h2><p>Artifacts remain independently available, but no linked interaction or WebGL marker was initialized.</p><ul>{errors.map((error) => <li key={error}><code>{error}</code></li>)}</ul>{warnings.length ? <ul className="warning-list">{warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul> : null}</section>; }
function toBZSelection(selection: ReciprocalSelection | null): BZSelection | null { if (!selection) return null; if (selection.kind === "high_symmetry_point" && selection.bzPointId) return { kind: "point", id: selection.bzPointId }; if (selection.kind === "path_segment" && selection.bzSegmentId) return { kind: "segment", id: selection.bzSegmentId, variantId: selection.pathVariantId }; if ((selection.kind === "sampled_reciprocal_point" || selection.kind === "phonon_mode") && selection.reciprocalCartesian && selection.bzSegmentId) return { kind: "reciprocal_sample", id: `q-${selection.qpointIndex}`, cartesian: selection.reciprocalCartesian, segmentId: selection.bzSegmentId }; return null; }
function find(artifacts: readonly Artifact[], type: string, name: string): Artifact | undefined { return artifacts.find((item) => item.type === type || item.name === name); }
function payload(artifact?: Artifact): unknown { if (!artifact) return null; const value = artifact.content ?? artifact.payload ?? artifact.metadata; if (typeof value === "string") { try { return JSON.parse(value); } catch { return value; } } return value ?? artifact; }
function short(value: string): string { return `${value.slice(0,8)}...${value.slice(-8)}`; }
function format(value: number): string { return Math.abs(value) < 1e-4 && value !== 0 ? value.toExponential(3) : value.toFixed(5); }
