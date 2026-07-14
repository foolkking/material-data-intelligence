"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import {
  type JsonRecord,
  PHONON_BAND_DOS_CAPS,
  validatePhononBandDosBundle,
} from "../../lib/phononBandDosContract";
import type { Artifact } from "../../lib/planner-api";

type PlotlyApi = {
  newPlot: (target: HTMLElement, data: unknown[], layout: JsonRecord, config: JsonRecord) => Promise<unknown>;
  purge: (target: HTMLElement) => void;
  downloadImage?: (target: HTMLElement, options: JsonRecord) => Promise<unknown>;
  register?: (modules: unknown[]) => void;
  Plots?: { resize: (target: HTMLElement) => void };
};
export type CombinedPlotlyLoader = () => Promise<PlotlyApi>;

const MAX_TABLE_ROWS = 200;
const BAND_COLOR = "#315d75";
const DOS_COLOR = "#a43f32";
const PROJECTION_COLORS = ["#6b4fa1", "#2e7d5b", "#b36b1e", "#735c45"];

export function PhononBandDosPreviewPanel({ artifacts, plotlyLoader = loadPlotly }: { artifacts: Artifact[]; plotlyLoader?: CombinedPlotlyLoader }) {
  const combinedArtifact = findArtifact(artifacts, "phonon_band_dos_json", "phonon_band_dos.json");
  const [tab, setTab] = useState<"plot" | "compatibility" | "band" | "dos" | "json">("plot");
  const [projectionId, setProjectionId] = useState("");
  if (!combinedArtifact) return null;
  const bundle = {
    combined: artifactPayload(combinedArtifact),
    summary: artifactPayload(findArtifact(artifacts, "phonon_summary_json", "phonon_band_dos_summary.json")),
    report: artifactPayload(findArtifact(artifacts, "phonon_compatibility_json", "phonon_band_dos_compatibility_report.json")),
    plot: artifactPayload(findArtifact(artifacts, "plotly_json", "phonon_band_dos_plot.json")),
    table: artifactPayload(findArtifact(artifacts, "table_json", "phonon_band_dos_table.json")),
    manifest: artifactPayload(findArtifact(artifacts, "phonon_manifest_json", "phonon_band_dos_manifest.json")),
  };
  const validation = validatePhononBandDosBundle(bundle);
  if (!validation.valid || !Object.values(bundle).every(record)) {
    return <CombinedFallback payload={bundle.combined} errors={validation.errors} />;
  }
  const combined = bundle.combined as JsonRecord;
  const summary = bundle.summary as JsonRecord;
  const report = bundle.report as JsonRecord;
  const plot = bundle.plot as JsonRecord;
  const table = bundle.table as JsonRecord;
  const manifest = bundle.manifest as JsonRecord;
  const projections = records(record(plot.dos_panel) ? plot.dos_panel.projections : null);
  const warnings = Array.isArray(combined.warnings) ? combined.warnings.map(String) : [];
  return (
    <section className="panel phonon-band-dos-preview" data-testid="phonon-band-dos-preview" aria-label="Combined phonon band and density of states preview">
      <header className="phonon-band-dos-heading">
        <div><h2>Phonon Band + DOS</h2><p>Validated static artifacts on one shared frequency axis</p></div>
        <span data-testid="phonon-band-dos-schema">{String(combined.schema_version)}</span>
      </header>
      <CombinedSummary summary={summary} />
      {warnings.length ? <div className="warning" data-testid="phonon-band-dos-warnings" role="status"><strong>Combined compatibility warning</strong><ul>{warnings.map((warning) => <li key={warning}><code>{warning}</code></li>)}</ul></div> : null}
      <p className="notice" data-testid="phonon-band-dos-scope">The band panel uses q-path distance on x; the DOS panel uses density on x; both use the same frequency y-axis in THz. Negative values retain the canonical imaginary-mode encoding. This product does not include eigenvectors, animation, thermal properties, or phonon calculation.</p>
      <div className="phonon-band-dos-toolbar">
        {projections.length ? <label>Projected DOS
          <select data-testid="phonon-band-dos-projection-selector" value={projectionId} onChange={(event) => setProjectionId(event.target.value)}>
            <option value="">Total DOS only</option>
            {projections.map((projection) => <option key={String(projection.projection_id)} value={String(projection.projection_id)}>{projectionLabel(projection)}</option>)}
          </select>
        </label> : <span>Projected DOS unavailable in the bounded display artifact.</span>}
        <button type="button" className="secondary" onClick={() => downloadJson(combined, "phonon-band-dos.json")} data-testid="phonon-band-dos-download-json">Download combined JSON</button>
      </div>
      <div className="viewer-preview-tabs phonon-band-dos-tabs" role="tablist" aria-label="Combined phonon preview modes">
        {([
          ["plot", "Combined plot"], ["compatibility", "Compatibility"], ["band", "Band data"], ["dos", "DOS data"], ["json", "Artifact JSON"],
        ] as const).map(([value, label]) => <button key={value} type="button" role="tab" aria-selected={tab === value} className={tab === value ? "active" : "secondary"} onClick={() => setTab(value)}>{label}</button>)}
      </div>
      <div role="tabpanel" className="phonon-band-dos-tab-panel">
        {tab === "plot" ? <CombinedPlot plot={plot} projectionId={projectionId} plotlyLoader={plotlyLoader} /> : null}
        {tab === "compatibility" ? <CompatibilityPanel report={report} /> : null}
        {tab === "band" ? <BandDataTable plot={plot} /> : null}
        {tab === "dos" ? <DosDataTable plot={plot} projectionId={projectionId} /> : null}
        {tab === "json" ? <div className="phonon-band-dos-json-grid"><JsonDetails title="phonon_band_dos.json" payload={combined} /><JsonDetails title="phonon_band_dos_summary.json" payload={summary} /><JsonDetails title="phonon_band_dos_compatibility_report.json" payload={report} /><JsonDetails title="phonon_band_dos_plot.json" payload={plot} /><JsonDetails title="phonon_band_dos_table.json" payload={table} /><JsonDetails title="phonon_band_dos_manifest.json" payload={manifest} /></div> : null}
      </div>
    </section>
  );
}

function CombinedPlot({ plot, projectionId, plotlyLoader }: { plot: JsonRecord; projectionId: string; plotlyLoader: CombinedPlotlyLoader }) {
  const hostRef = useRef<HTMLDivElement>(null);
  const plotlyRef = useRef<PlotlyApi | null>(null);
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState<"loading" | "rendered" | "refused" | "error">("loading");
  const [message, setMessage] = useState("Loading local Plotly renderer.");
  const mapped = useMemo(() => mapPhononBandDosPlot(plot, projectionId), [plot, projectionId]);
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
      plotlyRef.current = api;
      await api.newPlot(host, mapped.data, mapped.layout, {responsive: true, displaylogo: false, scrollZoom: false});
      if (!active) { api.purge(host); return; }
      setState("rendered");
      setMessage(`Rendered ${mapped.bandTraceCount} band traces and ${mapped.dosTraceCount} DOS series on one shared frequency axis.`);
    }).catch(() => {
      if (active) { setState("error"); setMessage("PHONON_BAND_DOS_PLOT_LOAD_FAILED: compatibility, data, and JSON tabs remain available."); }
    });
    const resize = () => plotly?.Plots?.resize(host);
    window.addEventListener("resize", resize);
    return () => { active = false; window.removeEventListener("resize", resize); if (plotly) plotly.purge(host); if (plotlyRef.current === plotly) plotlyRef.current = null; };
  }, [mapped, plotlyLoader, retry]);
  const downloadPng = () => {
    const host = hostRef.current;
    if (host && plotlyRef.current?.downloadImage) void plotlyRef.current.downloadImage(host, {format: "png", filename: "phonon-band-dos", width: 1600, height: 1000, scale: 1});
  };
  return <div className="phonon-band-dos-plot-wrap">
    <div className="phonon-band-dos-plot-actions"><button type="button" className="secondary" disabled={state !== "rendered" || !plotlyRef.current?.downloadImage} onClick={downloadPng} data-testid="phonon-band-dos-download-png">Download PNG</button></div>
    <div ref={hostRef} className="phonon-band-dos-plot" data-testid="phonon-band-dos-plot" aria-label="Combined phonon band and density of states with shared frequency axis" />
    {state !== "rendered" ? <div className="phonon-band-dos-plot-fallback" data-testid="phonon-band-dos-plot-fallback" role="status"><strong>{state === "refused" ? "Plot budget exceeded" : state === "error" ? "Plot unavailable" : "Loading plot"}</strong><p>{message}</p>{state === "error" ? <button type="button" onClick={() => setRetry((value) => value + 1)}>Retry plot</button> : null}</div> : null}
    <p className="sr-only" aria-live="polite" data-testid="phonon-band-dos-live-status">{message}</p>
    <pre hidden data-testid="phonon-band-dos-plot-metrics">{JSON.stringify({state, sharedFrequencyAxis: mapped.ok, bandTraceCount: mapped.ok ? mapped.bandTraceCount : 0, dosTraceCount: mapped.ok ? mapped.dosTraceCount : 0, numericValues: mapped.ok ? mapped.numericValues : 0, projectionId: projectionId || null, externalRequests: 0})}</pre>
  </div>;
}

export function mapPhononBandDosPlot(plot: JsonRecord, projectionId = ""): {ok: true; data: unknown[]; layout: JsonRecord; bandTraceCount: number; dosTraceCount: number; numericValues: number} | {ok: false; message: string} {
  const display = record(plot.display) ? plot.display : {};
  if (display.mode === "refused") return {ok: false, message: `PHONON_BAND_DOS_PLOT_BUDGET_EXCEEDED: ${String(display.reason || "display artifact refused")}.`};
  const axis = record(plot.shared_frequency_axis) ? plot.shared_frequency_axis : {};
  const bandPanel = record(plot.band_panel) ? plot.band_panel : {};
  const dosPanel = record(plot.dos_panel) ? plot.dos_panel : {};
  const series = records(bandPanel.series);
  const ticks = records(bandPanel.ticks);
  const frequencies = numbers(dosPanel.frequencies);
  const total = numbers(dosPanel.total_dos);
  const projections = records(dosPanel.projections);
  const selected = projectionId ? projections.find((item) => item.projection_id === projectionId) : null;
  if (projectionId && !selected) return {ok: false, message: "PHONON_BAND_DOS_PROJECTION_INVALID: select an available projected DOS identity."};
  if (frequencies.length < 2 || frequencies.length !== total.length || !finite(axis.minimum) || !finite(axis.maximum)) return {ok: false, message: "PHONON_BAND_DOS_PLOT_INVALID: inert JSON remains available."};
  const data: unknown[] = series.map((item) => ({
    type: "scatter", mode: "lines", xaxis: "x", yaxis: "y", name: `Branch ${Number(item.branch_index) + 1}`,
    legendgroup: "bands", showlegend: false, x: numbers(item.path_distance), y: numbers(item.frequencies),
    line: {color: BAND_COLOR, width: 1.45}, hovertemplate: "Path %{x:.5f}<br>Frequency %{y:.5f} THz<extra></extra>",
  }));
  data.push({type: "scatter", mode: "lines", xaxis: "x2", yaxis: "y", name: "Total DOS", x: total, y: frequencies, line: {color: DOS_COLOR, width: 2.5}, fill: "tozerox", fillcolor: "rgba(164,63,50,0.10)", hovertemplate: "DOS %{x:.5f} modes/THz<br>Frequency %{y:.5f} THz<extra></extra>"});
  if (selected) data.push({type: "scatter", mode: "lines", xaxis: "x2", yaxis: "y", name: projectionLabel(selected), x: numbers(selected.values), y: frequencies, line: {color: PROJECTION_COLORS[0], width: 1.8, dash: "dash"}, hovertemplate: `${projectionLabel(selected)}<br>DOS %{{x:.5f}} modes/THz<br>Frequency %{{y:.5f}} THz<extra></extra>`});
  const verticalShapes = ticks.map((tick) => ({type: "line", xref: "x", yref: "paper", x0: tick.distance, x1: tick.distance, y0: 0, y1: 1, line: {color: "#d7dce1", width: 1}}));
  const shapes: unknown[] = [
    {type: "rect", xref: "paper", yref: "y", x0: 0, x1: 1, y0: axis.minimum, y1: Math.min(-Number(axis.zero_tolerance), Number(axis.maximum)), fillcolor: "rgba(183,72,60,0.07)", line: {width: 0}, layer: "below"},
    {type: "line", xref: "paper", yref: "y", x0: 0, x1: 1, y0: 0, y1: 0, line: {color: "#30363d", width: 1.4}},
    ...verticalShapes,
  ];
  const layout: JsonRecord = {
    autosize: true, margin: {l: 78, r: 30, t: 42, b: 70}, paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff",
    xaxis: {domain: [0, 0.72], title: {text: "Wave vector path"}, tickmode: "array", tickvals: ticks.map((tick) => tick.distance), ticktext: ticks.map((tick) => String(tick.label)), zeroline: false},
    xaxis2: {domain: [0.78, 1], title: {text: "DOS (modes/THz)"}, anchor: "y", rangemode: "tozero", zeroline: true},
    yaxis: {title: {text: "Frequency (THz)"}, range: [axis.minimum, axis.maximum], fixedrange: false},
    showlegend: true, legend: {orientation: "h", x: 0.78, y: 1.08, xanchor: "left"}, hovermode: "closest", shapes,
    annotations: [{xref: "paper", yref: "paper", x: 0.36, y: 1.08, text: "Phonon bands", showarrow: false}, {xref: "paper", yref: "paper", x: 0.89, y: 1.08, text: "Density of states", showarrow: false}],
  };
  const numericValues = Number(display.numeric_values);
  if (!Number.isSafeInteger(numericValues) || numericValues > PHONON_BAND_DOS_CAPS.maxPlotValues || data.length > PHONON_BAND_DOS_CAPS.maxPlotTraces) return {ok: false, message: "PHONON_BAND_DOS_PLOT_BUDGET_EXCEEDED: canonical JSON remains available."};
  return {ok: true, data, layout, bandTraceCount: series.length, dosTraceCount: selected ? 2 : 1, numericValues};
}

function CombinedSummary({ summary }: { summary: JsonRecord }) {
  const items: Array<[string, unknown]> = [
    ["Atoms", summary.atom_count], ["Branches", summary.branch_count], ["Q-points", summary.qpoint_count],
    ["DOS grid", summary.dos_grid_point_count], ["Projected series", summary.projection_count],
    ["Shared frequency range", `${format(Number(summary.frequency_min))} to ${format(Number(summary.frequency_max))} THz`],
    ["Compatibility", summary.compatibility_status], ["DOS integral / expected", `${format(Number(summary.dos_integral))} / ${String(summary.expected_modes)}`],
    ["Imaginary modes / DOS weight", `${String(summary.imaginary_band_mode_count)} / ${format(Number(summary.imaginary_dos_integral))}`],
  ];
  return <dl className="phonon-band-dos-summary" data-testid="phonon-band-dos-summary">{items.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{String(value)}</dd></div>)}</dl>;
}

function CompatibilityPanel({ report }: { report: JsonRecord }) {
  const rows = records(report.checks);
  return <div className="phonon-band-dos-table-wrap"><p data-testid="phonon-band-dos-compatibility-status">Compatibility status: <strong>{String(report.status)}</strong>. Checks are evaluated in deterministic order.</p><table data-testid="phonon-band-dos-compatibility-table"><caption>Band and DOS compatibility checks</caption><thead><tr><th>Check</th><th>Status</th><th>Band</th><th>DOS</th><th>Result</th></tr></thead><tbody>{rows.map((row) => <tr key={String(row.name)}><td>{String(row.name)}</td><td>{String(row.status)}</td><td><code>{compact(row.band_value)}</code></td><td><code>{compact(row.dos_value)}</code></td><td>{row.result_code ? <code>{String(row.result_code)}</code> : "-"}</td></tr>)}</tbody></table></div>;
}

function BandDataTable({ plot }: { plot: JsonRecord }) {
  const panel = record(plot.band_panel) ? plot.band_panel : {};
  const rows: Array<{branch: number; segment: number; path: number; frequency: number}> = [];
  for (const series of records(panel.series)) {
    const path = numbers(series.path_distance);
    const frequencies = numbers(series.frequencies);
    for (let index = 0; index < Math.min(path.length, frequencies.length) && rows.length < MAX_TABLE_ROWS; index += 1) rows.push({branch: Number(series.branch_index), segment: Number(series.segment_index), path: path[index], frequency: frequencies[index]});
    if (rows.length >= MAX_TABLE_ROWS) break;
  }
  return <div className="phonon-band-dos-table-wrap"><p>Showing {rows.length} bounded display rows.</p><table data-testid="phonon-band-dos-band-table"><caption>Combined display band samples</caption><thead><tr><th>Branch</th><th>Segment</th><th>Path distance</th><th>Frequency (THz)</th></tr></thead><tbody>{rows.map((row, index) => <tr key={`${row.branch}:${row.segment}:${index}`}><td>{row.branch}</td><td>{row.segment}</td><td>{format(row.path)}</td><td>{format(row.frequency)}</td></tr>)}</tbody></table></div>;
}

function DosDataTable({ plot, projectionId }: { plot: JsonRecord; projectionId: string }) {
  const panel = record(plot.dos_panel) ? plot.dos_panel : {};
  const frequencies = numbers(panel.frequencies);
  const total = numbers(panel.total_dos);
  const selected = records(panel.projections).find((item) => item.projection_id === projectionId);
  const projected = selected ? numbers(selected.values) : [];
  return <div className="phonon-band-dos-table-wrap"><p>Showing {Math.min(frequencies.length, MAX_TABLE_ROWS)} of {frequencies.length} display grid points.</p><table data-testid="phonon-band-dos-dos-table"><caption>Combined display DOS samples</caption><thead><tr><th>Grid</th><th>Frequency (THz)</th><th>Total DOS</th>{selected ? <th>{projectionLabel(selected)}</th> : null}</tr></thead><tbody>{frequencies.slice(0, MAX_TABLE_ROWS).map((frequency, index) => <tr key={index}><td>{index}</td><td>{format(frequency)}</td><td>{format(total[index])}</td>{selected ? <td>{format(projected[index])}</td> : null}</tr>)}</tbody></table></div>;
}

function CombinedFallback({ payload, errors }: { payload: unknown; errors: readonly string[] }) {
  return <section className="panel phonon-band-dos-preview" data-testid="phonon-band-dos-preview-invalid" role="status"><h2>Combined phonon preview unavailable</h2><code>{errors[0] || "PHONON_BAND_DOS_SCHEMA_INVALID"}</code><p>The combined bundle was rejected before Plotly initialization. Inert artifact JSON remains available in the artifact gallery.</p><details><summary>Combined artifact JSON</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details></section>;
}

async function loadPlotly(): Promise<PlotlyApi> {
  const [coreModule, scatterModule] = await Promise.all([import("plotly.js/lib/core"), import("plotly.js/lib/scatter")]);
  const plotly = ("default" in coreModule ? coreModule.default : coreModule) as unknown as PlotlyApi;
  const scatter = "default" in scatterModule ? scatterModule.default : scatterModule;
  plotly.register?.([scatter]);
  return plotly;
}

function findArtifact(artifacts: Artifact[], type: string, name: string): Artifact | undefined { return artifacts.find((artifact) => artifact.name === name || artifact.type === type && artifact.name === name); }
function artifactPayload(artifact?: Artifact): JsonRecord | null { if (!artifact) return null; const metadata = record(artifact.metadata) ? artifact.metadata : null; for (const candidate of [artifact.content, artifact.payload, metadata?.content, metadata?.payload, metadata?.preview]) { if (record(candidate)) return candidate; if (typeof candidate === "string") { try { const parsed = JSON.parse(candidate); if (record(parsed)) return parsed; } catch { /* inert fallback */ } } } return null; }
function JsonDetails({ title, payload }: { title: string; payload: unknown }) { return <details><summary>{title}</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details>; }
function projectionLabel(projection: JsonRecord): string { return projection.projection_type === "atom" ? `Atom ${String(projection.atom_index)} (${String(projection.species)})` : `Species ${String(projection.species)}`; }
function downloadJson(payload: JsonRecord, filename: string): void { const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], {type: "application/json"})); const anchor = document.createElement("a"); anchor.href = url; anchor.download = filename; document.body.appendChild(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url); }
function compact(value: unknown): string { const text = typeof value === "string" ? value : JSON.stringify(value); return text.length > 120 ? `${text.slice(0, 117)}...` : text; }
function record(value: unknown): value is JsonRecord { return typeof value === "object" && value !== null && !Array.isArray(value); }
function records(value: unknown): JsonRecord[] { return Array.isArray(value) ? value.filter(record) : []; }
function numbers(value: unknown): number[] { return Array.isArray(value) && value.every(finite) ? value : []; }
function finite(value: unknown): value is number { return typeof value === "number" && Number.isFinite(value); }
function format(value: number): string { return Math.abs(value) >= 1000 || (Math.abs(value) < 0.001 && value !== 0) ? value.toExponential(4) : value.toFixed(5); }
