"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { validatePhononDosReference } from "../../lib/phononContract";
import type { Artifact } from "../../lib/planner-api";

type JsonRecord = Record<string, unknown>;
type PlotlyApi = {
  newPlot: (target: HTMLElement, data: unknown[], layout: JsonRecord, config: JsonRecord) => Promise<unknown>;
  purge: (target: HTMLElement) => void;
  register?: (modules: unknown[]) => void;
  Plots?: { resize: (target: HTMLElement) => void };
};
export type PlotlyLoader = () => Promise<PlotlyApi>;

const MAX_PREVIEW_VALUES = 100_000;
const MAX_TABLE_ROWS = 300;

export function PhononDosPreviewPanel({ artifacts, plotlyLoader = loadPlotly }: { artifacts: Artifact[]; plotlyLoader?: PlotlyLoader }) {
  const dosArtifact = artifacts.find((artifact) => artifact.type === "phonon_dos_json" || artifact.name === "phonon_dos.json");
  const summaryArtifact = artifacts.find((artifact) => artifact.name === "phonon_dos_summary.json");
  const manifestArtifact = artifacts.find((artifact) => artifact.type === "phonon_manifest_json" || artifact.name === "phonon_manifest.json");
  const [tab, setTab] = useState<"plot" | "table" | "json">("plot");
  const [projectionIndex, setProjectionIndex] = useState<number | null>(null);
  if (!dosArtifact) return null;
  const payload = artifactPayload(dosArtifact);
  const validation = validatePhononDosReference(payload);
  if (!validation.valid || !record(payload)) return <PhononDosFallback payload={payload} errors={validation.errors} />;
  const dos = payload;
  const summary = artifactPayload(summaryArtifact);
  const manifest = artifactPayload(manifestArtifact);
  const projections = records(dos.projected_dos);
  return (
    <section className="panel phonon-dos-preview" data-testid="phonon-dos-preview" aria-label="Phonon density of states preview">
      <header className="phonon-dos-heading">
        <div><h2>Phonon Density of States</h2><p>Validated static DOS artifact</p></div>
        <span data-testid="phonon-dos-schema">{String(dos.schema_version)}</span>
      </header>
      <PhononDosSummary dos={dos} summary={summary} />
      {validation.warnings.length ? <div className="warning" data-testid="phonon-dos-warnings" role="status"><strong>DOS validation warning</strong><ul>{validation.warnings.map((warning) => <li key={warning}><code>{warning}</code></li>)}</ul></div> : null}
      <p className="notice" data-testid="phonon-dos-scope">The canonical curve is normalized to total modes. Frequencies below 0 THz are preserved as imaginary-mode contributions. No smoothing, phonon calculation, bands, combined view, eigenvectors, or animation are included.</p>
      {projections.length ? <label className="phonon-dos-projection-control">Projected series
        <select data-testid="phonon-dos-projection-selector" value={projectionIndex ?? ""} onChange={(event) => setProjectionIndex(event.target.value === "" ? null : Number(event.target.value))}>
          <option value="">Total DOS only</option>
          {projections.map((projection, index) => <option key={projectionKey(projection, index)} value={index}>{projectionLabel(projection)}</option>)}
        </select>
      </label> : null}
      <div className="viewer-preview-tabs" role="tablist" aria-label="Phonon DOS preview modes">
        {(["plot", "table", "json"] as const).map((value) => <button key={value} type="button" role="tab" aria-selected={tab === value} className={tab === value ? "active" : "secondary"} onClick={() => setTab(value)}>{value === "plot" ? "DOS plot" : value === "table" ? "DOS table" : "Canonical JSON"}</button>)}
      </div>
      <div role="tabpanel" className="phonon-dos-tab-panel">
        {tab === "plot" ? <PhononDosPlot dos={dos} projectionIndex={projectionIndex} plotlyLoader={plotlyLoader} /> : null}
        {tab === "table" ? <PhononDosTable dos={dos} projectionIndex={projectionIndex} /> : null}
        {tab === "json" ? <div className="phonon-dos-json-grid"><JsonDetails title="phonon_dos.json" payload={dos} /><JsonDetails title="phonon_dos_summary.json" payload={summary} /><JsonDetails title="phonon_manifest.json" payload={manifest} /></div> : null}
      </div>
    </section>
  );
}

function PhononDosPlot({ dos, projectionIndex, plotlyLoader }: { dos: JsonRecord; projectionIndex: number | null; plotlyLoader: PlotlyLoader }) {
  const hostRef = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<"loading" | "rendered" | "refused" | "error">("loading");
  const [message, setMessage] = useState("Loading local Plotly renderer.");
  const mapped = useMemo(() => mapPhononDosPlot(dos, projectionIndex), [dos, projectionIndex]);
  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    if (!mapped.ok) { setState("refused"); setMessage(mapped.message); return; }
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
      setMessage(`Rendered ${mapped.pointCount} DOS grid points and ${mapped.traceCount} visible series.`);
    }).catch(() => {
      if (active) { setState("error"); setMessage("PHONON_DOS_PLOT_LOAD_FAILED: canonical JSON and table remain available."); }
    });
    const resize = () => plotly?.Plots?.resize(host);
    window.addEventListener("resize", resize);
    return () => { active = false; window.removeEventListener("resize", resize); if (plotly) plotly.purge(host); };
  }, [mapped, plotlyLoader]);
  return <div className="phonon-dos-plot-wrap">
    <div ref={hostRef} className="phonon-dos-plot" data-testid="phonon-dos-plot" aria-label="Phonon density of states by frequency" />
    {state !== "rendered" ? <div className="phonon-dos-plot-fallback" data-testid="phonon-dos-plot-fallback"><strong>{state === "refused" ? "Plot budget exceeded" : state === "error" ? "Plot unavailable" : "Loading plot"}</strong><p>{message}</p></div> : null}
    <p className="sr-only" aria-live="polite" data-testid="phonon-dos-live-status">{message}</p>
    <pre hidden data-testid="phonon-dos-plot-metrics">{JSON.stringify({ state, pointCount: mapped.ok ? mapped.pointCount : 0, traceCount: mapped.ok ? mapped.traceCount : 0, numericValues: mapped.ok ? mapped.numericValues : 0, negativePreserved: true, externalRequests: 0 })}</pre>
  </div>;
}

function PhononDosSummary({ dos, summary }: { dos: JsonRecord; summary: JsonRecord | null }) {
  const frequencies = numbers(dos.frequencies);
  const integration = record(dos.integration) ? dos.integration : {};
  const broadening = record(dos.broadening) ? dos.broadening : {};
  const projections = records(dos.projected_dos);
  const items: Array<[string, unknown]> = [
    ["Atoms", dos.atom_count], ["Grid points", frequencies.length], ["Frequency range", frequencies.length ? `${format(frequencies[0])} to ${format(frequencies.at(-1) ?? 0)} THz` : "-"],
    ["Normalization", dos.normalization], ["Integral / expected", `${format(Number(integration.observed_integral))} / ${String(integration.expected_mode_count)}`],
    ["Imaginary-region weight", summary ? format(Number(summary.imaginary_region_integral)) : "available in DOS summary"],
    ["Projected series", projections.length], ["Projection completeness", summary?.projection_completeness ?? inferredCompleteness(projections)],
    ["Broadening", broadening.method === "none" ? "none applied" : `${String(broadening.method)} metadata only`],
  ];
  return <dl className="phonon-dos-summary" data-testid="phonon-dos-summary">{items.map(([label, value]) => <div key={String(label)}><dt>{label}</dt><dd>{String(value)}</dd></div>)}</dl>;
}

function PhononDosTable({ dos, projectionIndex }: { dos: JsonRecord; projectionIndex: number | null }) {
  const frequencies = numbers(dos.frequencies);
  const total = numbers(dos.total_dos);
  const projections = records(dos.projected_dos);
  const selected = projectionIndex === null ? null : projections[projectionIndex];
  const projected = selected ? numbers(selected.values) : [];
  const tolerance = Number(dos.frequency_zero_tolerance);
  const rows = frequencies.slice(0, MAX_TABLE_ROWS).map((frequency, index) => ({
    index, frequency, total: total[index], projected: selected ? projected[index] : null,
    classification: frequency < -tolerance ? "imaginary" : Math.abs(frequency) <= tolerance ? "near zero" : "real",
  }));
  return <div className="phonon-dos-table-wrap"><p>{rows.length < frequencies.length ? `Showing first ${rows.length} of ${frequencies.length} grid points. Canonical JSON is complete.` : `${frequencies.length} grid points.`}</p><table data-testid="phonon-dos-table"><caption>Phonon density of states samples</caption><thead><tr><th>Grid</th><th>Frequency (THz)</th><th>Total DOS (modes/THz)</th>{selected ? <th>{projectionLabel(selected)}</th> : null}<th>Classification</th></tr></thead><tbody>{rows.map((row) => <tr key={row.index}><td>{row.index}</td><td>{format(row.frequency)}</td><td>{format(row.total)}</td>{selected ? <td>{format(row.projected ?? 0)}</td> : null}<td>{row.classification}</td></tr>)}</tbody></table></div>;
}

function PhononDosFallback({ payload, errors }: { payload: unknown; errors: readonly string[] }) {
  return <section className="panel phonon-dos-preview" data-testid="phonon-dos-preview-invalid" role="status"><h2>Phonon DOS preview unavailable</h2><code>{errors[0] || "PHONON_SCHEMA_UNSUPPORTED"}</code><p>The artifact was rejected before Plotly initialization. Inert JSON remains available for inspection.</p><details><summary>Artifact JSON</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details></section>;
}

export function mapPhononDosPlot(dos: JsonRecord, projectionIndex: number | null): { ok: true; data: unknown[]; layout: JsonRecord; pointCount: number; traceCount: number; numericValues: number } | { ok: false; message: string } {
  const frequencies = numbers(dos.frequencies);
  const total = numbers(dos.total_dos);
  const projections = records(dos.projected_dos);
  const selected = projectionIndex === null ? null : projections[projectionIndex];
  const projected = selected ? numbers(selected.values) : [];
  const traceCount = selected ? 2 : 1;
  const numericValues = frequencies.length * traceCount;
  if (frequencies.length !== total.length || (selected && projected.length !== frequencies.length)) return { ok: false, message: "PHONON_DOS_SHAPE_INVALID: canonical JSON remains available." };
  if (numericValues > MAX_PREVIEW_VALUES) return { ok: false, message: `PHONON_DOS_PREVIEW_LIMIT_EXCEEDED: ${numericValues} values exceed the static preview budget. Canonical JSON remains available.` };
  const data: unknown[] = [{ type: "scatter", mode: "lines", name: "Total DOS", x: frequencies, y: total, line: { color: "#176b87", width: 2.5 }, hovertemplate: "Frequency %{x:.5f} THz<br>Total DOS %{y:.5f} modes/THz<extra></extra>" }];
  if (selected) data.push({ type: "scatter", mode: "lines", name: projectionLabel(selected), x: frequencies, y: projected, line: { color: "#a54336", width: 1.8, dash: "dash" }, hovertemplate: `${projectionLabel(selected)}<br>Frequency %{x:.5f} THz<br>DOS %{y:.5f} modes/THz<extra></extra>` });
  return { ok: true, data, layout: { autosize: true, margin: { l: 76, r: 24, t: 24, b: 64 }, xaxis: { title: { text: "Frequency (THz)" }, zeroline: true, zerolinewidth: 1.5, zerolinecolor: "#30363d" }, yaxis: { title: { text: "DOS (modes/THz)" }, rangemode: "tozero" }, showlegend: true, hovermode: "x unified", paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff" }, pointCount: frequencies.length, traceCount, numericValues };
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
function JsonDetails({ title, payload }: { title: string; payload: unknown }) { return <details open><summary>{title}</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details>; }
function projectionLabel(projection: JsonRecord): string { return projection.projection_type === "atom" ? `Atom ${String(projection.atom_index)} (${String(projection.species)})` : `Species ${String(projection.species)}`; }
function projectionKey(projection: JsonRecord, index: number): string { return `${String(projection.projection_type)}:${String(projection.atom_index)}:${String(projection.species)}:${index}`; }
function inferredCompleteness(projections: JsonRecord[]): string { return !projections.length ? "unknown" : projections.every((item) => item.source_guarantees_sum === true) ? "complete" : "partial"; }
function record(value: unknown): value is JsonRecord { return typeof value === "object" && value !== null && !Array.isArray(value); }
function records(value: unknown): JsonRecord[] { return Array.isArray(value) ? value.filter(record) : []; }
function numbers(value: unknown): number[] { return Array.isArray(value) ? value.filter(finite) : []; }
function finite(value: unknown): value is number { return typeof value === "number" && Number.isFinite(value); }
function format(value: number): string { return Math.abs(value) >= 1000 || (Math.abs(value) < 0.001 && value !== 0) ? value.toExponential(4) : value.toFixed(5); }
