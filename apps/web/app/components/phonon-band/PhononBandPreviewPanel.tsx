"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { validatePhononBandReference } from "../../lib/phononContract";
import type { Artifact } from "../../lib/planner-api";

type JsonRecord = Record<string, unknown>;
type PlotlyApi = {
  newPlot: (target: HTMLElement, data: unknown[], layout: JsonRecord, config: JsonRecord) => Promise<unknown>;
  purge: (target: HTMLElement) => void;
  register?: (modules: unknown[]) => void;
  Plots?: { resize: (target: HTMLElement) => void };
};
type PlotlyLoader = () => Promise<PlotlyApi>;

const MAX_PREVIEW_VALUES = 500_000;
const MAX_PREVIEW_TRACES = 4_096;
const MAX_TABLE_ROWS = 200;

export function PhononBandPreviewPanel({ artifacts, plotlyLoader = loadPlotly }: { artifacts: Artifact[]; plotlyLoader?: PlotlyLoader }) {
  const bandArtifact = artifacts.find((artifact) => artifact.type === "phonon_band_json" || artifact.name === "phonon_band.json");
  const summaryArtifact = artifacts.find((artifact) => artifact.type === "phonon_summary_json" || artifact.name === "phonon_summary.json");
  const manifestArtifact = artifacts.find((artifact) => artifact.type === "phonon_manifest_json" || artifact.name === "phonon_manifest.json");
  const animationArtifact = artifacts.find((artifact) => artifact.type === "phonon_animation_json" || artifact.name === "phonon_animation.json");
  const [tab, setTab] = useState<"plot" | "table" | "json">("plot");
  if (!bandArtifact) return null;
  const payload = artifactPayload(bandArtifact);
  const validation = validatePhononBandReference(payload);
  if (!validation.valid || !record(payload)) {
    return <PhononBandFallback payload={payload} errors={validation.errors} />;
  }
  const band = payload;
  const summary = artifactPayload(summaryArtifact);
  const manifest = artifactPayload(manifestArtifact);
  const handoff = phononAnimationHandoff(band, bandArtifact, artifactPayload(animationArtifact));
  return (
    <section className="panel phonon-band-preview" data-testid="phonon-band-preview" aria-label="Phonon band preview">
      <header className="phonon-band-heading">
        <div><h2>Phonon Bands</h2><p>Validated static band artifact</p></div>
        <span data-testid="phonon-band-schema">{String(band.schema_version)}</span>
      </header>
      <PhononBandSummary band={band} summary={summary} />
      <div className="phonon-band-handoff" data-testid="phonon-band-animation-handoff"><span>{handoff.ok?`Mode q${handoff.qpointIndex} / branch ${handoff.branchIndex} is bound by canonical mode ID.`:handoff.code}</span><button type="button" disabled={!handoff.ok} onClick={()=>document.querySelector('[data-testid="phonon-animation-preview-panel"]')?.scrollIntoView({behavior:"smooth",block:"start"})}>Open mode animation</button></div>
      <p className="notice" data-testid="phonon-band-scope">Source branch order is preserved. Negative plotted values represent imaginary phonon modes under the contract&apos;s negative-real encoding. DOS, eigenvectors, animation, and phonon calculation are not included.</p>
      <div className="viewer-preview-tabs" role="tablist" aria-label="Phonon band preview modes">
        {(["plot", "table", "json"] as const).map((value) => <button key={value} type="button" role="tab" aria-selected={tab === value} className={tab === value ? "active" : "secondary"} onClick={() => setTab(value)}>{value === "plot" ? "Band plot" : value === "table" ? "Band table" : "Canonical JSON"}</button>)}
      </div>
      <div role="tabpanel" className="phonon-band-tab-panel">
        {tab === "plot" ? <PhononBandPlot band={band} plotlyLoader={plotlyLoader} /> : null}
        {tab === "table" ? <PhononBandTable band={band} /> : null}
        {tab === "json" ? <div className="phonon-band-json-grid"><JsonDetails title="phonon_band.json" payload={band} /><JsonDetails title="phonon_summary.json" payload={summary} /><JsonDetails title="phonon_manifest.json" payload={manifest} /></div> : null}
      </div>
    </section>
  );
}

function PhononBandPlot({ band, plotlyLoader }: { band: JsonRecord; plotlyLoader: PlotlyLoader }) {
  const hostRef = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<"loading" | "rendered" | "refused" | "error">("loading");
  const [message, setMessage] = useState("Loading local Plotly renderer.");
  const mapped = useMemo(() => mapPhononBandPlot(band), [band]);
  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    if (!mapped.ok) {
      setState("refused");
      setMessage(mapped.message);
      return;
    }
    let active = true;
    let plotly: PlotlyApi | null = null;
    setState("loading");
    setMessage("Loading local Plotly renderer.");
    plotlyLoader().then(async (api) => {
      if (!active) return;
      plotly = api;
      await api.newPlot(host, mapped.data, mapped.layout, { responsive: true, displaylogo: false, scrollZoom: false });
      if (!active) { api.purge(host); return; }
      setState("rendered");
      setMessage(`Rendered ${mapped.branchCount} branches across ${mapped.segmentCount} path segments.`);
    }).catch(() => {
      if (active) { setState("error"); setMessage("PHONON_BAND_PLOT_LOAD_FAILED: canonical JSON and table remain available."); }
    });
    const resize = () => plotly?.Plots?.resize(host);
    window.addEventListener("resize", resize);
    return () => { active = false; window.removeEventListener("resize", resize); if (plotly) plotly.purge(host); };
  }, [mapped, plotlyLoader]);
  return <div className="phonon-band-plot-wrap">
    <div ref={hostRef} className="phonon-band-plot" data-testid="phonon-band-plot" aria-label="Phonon frequency by wave vector path" />
    {state !== "rendered" ? <div className="phonon-band-plot-fallback" data-testid="phonon-band-plot-fallback"><strong>{state === "refused" ? "Plot budget exceeded" : state === "error" ? "Plot unavailable" : "Loading plot"}</strong><p>{message}</p></div> : null}
    <p className="sr-only" aria-live="polite" data-testid="phonon-band-live-status">{message}</p>
    <pre hidden data-testid="phonon-band-plot-metrics">{JSON.stringify({ state, branchCount: mapped.ok ? mapped.branchCount : 0, segmentCount: mapped.ok ? mapped.segmentCount : 0, traceCount: mapped.ok ? mapped.data.length : 0, numericValues: mapped.ok ? mapped.numericValues : 0, negativePreserved: true, externalRequests: 0 })}</pre>
  </div>;
}

function PhononBandSummary({ band, summary }: { band: JsonRecord; summary: JsonRecord | null }) {
  const branches = records(band.branches);
  const qpoints = records(band.qpoints);
  const segments = records(band.segments);
  const frequencies = branches.flatMap((branch) => numbers(branch.frequencies));
  const species = Array.isArray(band.species) ? band.species.map(String) : [];
  return <dl className="phonon-band-summary" data-testid="phonon-band-summary">
    <div><dt>Atoms</dt><dd>{String(band.atom_count)}</dd></div>
    <div><dt>Species order</dt><dd>{species.join(", ")}</dd></div>
    <div><dt>Branches</dt><dd>{branches.length}</dd></div>
    <div><dt>Q-points</dt><dd>{qpoints.length}</dd></div>
    <div><dt>Segments</dt><dd>{segments.length}</dd></div>
    <div><dt>Frequency range</dt><dd>{finite(summary?.frequency_min) ? summary?.frequency_min : Math.min(...frequencies)} to {finite(summary?.frequency_max) ? summary?.frequency_max : Math.max(...frequencies)} THz</dd></div>
  </dl>;
}

function PhononBandTable({ band }: { band: JsonRecord }) {
  const rows = useMemo(() => {
    const qpoints = records(band.qpoints);
    const branches = records(band.branches);
    const zeroTolerance = Number(band.frequency_zero_tolerance);
    const result: Array<{ qpoint: number; segment: number; coordinates: number[]; label: string; distance: number; branch: number; frequency: number; classification: string }> = [];
    for (const point of qpoints) for (const branch of branches) {
      if (result.length >= MAX_TABLE_ROWS) return result;
      const index = Number(point.index);
      const frequency = numbers(branch.frequencies)[index];
      result.push({
        qpoint: index,
        segment: Number(point.segment_index),
        coordinates: numbers(point.coordinates),
        label: typeof point.label === "string" ? point.label : "",
        distance: Number(point.distance),
        branch: Number(branch.branch_index),
        frequency,
        classification: frequency < -zeroTolerance ? "imaginary" : Math.abs(frequency) <= zeroTolerance ? "near zero" : "real",
      });
    }
    return result;
  }, [band]);
  const total = records(band.qpoints).length * records(band.branches).length;
  return <div className="phonon-band-table-wrap"><p>{rows.length < total ? `Showing first ${rows.length} of ${total} rows. Canonical JSON is complete.` : `${total} rows.`}</p><table data-testid="phonon-band-table"><caption>Phonon band q-point and branch frequencies</caption><thead><tr><th>Q-point</th><th>Segment</th><th>q coordinates</th><th>Label</th><th>Path distance (rad/angstrom)</th><th>Branch</th><th>Frequency (THz)</th><th>Classification</th></tr></thead><tbody>{rows.map((row) => <tr key={`${row.qpoint}:${row.branch}`}><td>{row.qpoint}</td><td>{row.segment}</td><td>[{row.coordinates.map(format).join(", ")}]</td><td>{row.label || "-"}</td><td>{format(row.distance)}</td><td>{row.branch}</td><td>{format(row.frequency)}</td><td>{row.classification}</td></tr>)}</tbody></table></div>;
}

function PhononBandFallback({ payload, errors }: { payload: unknown; errors: readonly string[] }) {
  return <section className="panel phonon-band-preview" data-testid="phonon-band-preview-invalid" role="status"><h2>Phonon band preview unavailable</h2><code>{errors[0] || "PHONON_SCHEMA_UNSUPPORTED"}</code><p>The artifact was rejected before Plotly initialization. Inert JSON remains available for inspection.</p><details><summary>Artifact JSON</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details></section>;
}

function JsonDetails({ title, payload }: { title: string; payload: unknown }) { return <details open><summary>{title}</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details>; }

export function mapPhononBandPlot(band: JsonRecord): { ok: true; data: unknown[]; layout: JsonRecord; branchCount: number; segmentCount: number; numericValues: number } | { ok: false; message: string } {
  const qpoints = records(band.qpoints);
  const segments = records(band.segments);
  const branches = records(band.branches);
  const numericValues = qpoints.length * branches.length;
  const traceCount = branches.length * segments.length;
  if (numericValues > MAX_PREVIEW_VALUES || traceCount > MAX_PREVIEW_TRACES) return { ok: false, message: `PHONON_BAND_PREVIEW_LIMIT_EXCEEDED: ${numericValues} values and ${traceCount} traces exceed the static preview budget. Canonical JSON remains available.` };
  const data: unknown[] = [];
  for (const branch of branches) for (const segment of segments) {
    const start = Number(segment.start_qpoint_index);
    const end = Number(segment.end_qpoint_index) + 1;
    data.push({ type: "scatter", mode: "lines", name: `Branch ${Number(branch.branch_index) + 1}`, legendgroup: `branch-${String(branch.branch_index)}`, showlegend: false, x: qpoints.slice(start, end).map((point) => Number(point.distance)), y: numbers(branch.frequencies).slice(start, end), hovertemplate: "Path %{x:.5f}<br>Frequency %{y:.5f} THz<extra></extra>" });
  }
  const labeled = qpoints.filter((point) => typeof point.label === "string");
  return { ok: true, data, layout: { autosize: true, margin: { l: 72, r: 20, t: 24, b: 64 }, xaxis: { title: { text: "Wave vector path" }, tickmode: "array", tickvals: labeled.map((point) => Number(point.distance)), ticktext: labeled.map((point) => String(point.label)) }, yaxis: { title: { text: "Frequency (THz)" }, zeroline: true }, showlegend: false, hovermode: "x unified", paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff" }, branchCount: branches.length, segmentCount: segments.length, numericValues };
}

async function loadPlotly(): Promise<PlotlyApi> {
  const [coreModule, scatterModule] = await Promise.all([import("plotly.js/lib/core"), import("plotly.js/lib/scatter")]);
  const plotly = ("default" in coreModule ? coreModule.default : coreModule) as unknown as PlotlyApi;
  const scatter = "default" in scatterModule ? scatterModule.default : scatterModule;
  plotly.register?.([scatter]);
  return plotly;
}

function artifactPayload(artifact?: Artifact): JsonRecord | null {
  if (!artifact) return null;
  const metadata = record(artifact.metadata) ? artifact.metadata : null;
  for (const candidate of [artifact.content, artifact.payload, metadata?.content, metadata?.payload, metadata?.preview]) {
    if (record(candidate)) return candidate;
    if (typeof candidate === "string") { try { const parsed = JSON.parse(candidate); if (record(parsed)) return parsed; } catch { /* inert fallback */ } }
  }
  return null;
}
function record(value: unknown): value is JsonRecord { return typeof value === "object" && value !== null && !Array.isArray(value); }
function records(value: unknown): JsonRecord[] { return Array.isArray(value) ? value.filter(record) : []; }
function numbers(value: unknown): number[] { return Array.isArray(value) ? value.filter(finite) : []; }
function finite(value: unknown): value is number { return typeof value === "number" && Number.isFinite(value); }
function format(value: number): string { return Math.abs(value) >= 1000 || (Math.abs(value) < 0.001 && value !== 0) ? value.toExponential(4) : value.toFixed(5); }

export function phononAnimationHandoff(band:JsonRecord,artifact:Artifact,animation:JsonRecord|null):{ok:true;modeId:string;qpointIndex:number;branchIndex:number}|{ok:false;code:string}{
  if(!animation)return{ok:false,code:"PHONON_ANIMATION_EIGENVECTOR_UNAVAILABLE"};const mode=record(animation.mode)&&record(animation.mode.mode)?animation.mode.mode:null;const source=record(animation.source)?animation.source:null;if(!mode||!source||typeof mode.mode_id!=="string")return{ok:false,code:"PHONON_ANIMATION_HANDOFF_INVALID"};
  const artifactHash=artifact.sha256||artifact.contentHash;const expected=source.band_sha256;const modeArtifact=record(mode.band_artifact)?mode.band_artifact:null;if(typeof artifactHash!=="string"||artifactHash!==expected||modeArtifact?.sha256!==expected)return{ok:false,code:"PHONON_ANIMATION_BAND_HASH_MISMATCH"};
  const qpointIndex=Number(mode.qpoint_index),branchIndex=Number(mode.branch_index);const qpoint=records(band.qpoints).find((item)=>Number(item.index)===qpointIndex);const branch=records(band.branches).find((item)=>Number(item.branch_index)===branchIndex);const frequency=branch?numbers(branch.frequencies)[qpointIndex]:undefined;if(!qpoint||!branch||!finite(frequency)||Math.abs(frequency-Number(mode.frequency))>Number(mode.frequency_tolerance))return{ok:false,code:"PHONON_ANIMATION_MODE_REFERENCE_STALE"};
  return{ok:true,modeId:String(mode.mode_id),qpointIndex,branchIndex};
}
