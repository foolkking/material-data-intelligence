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
  const combinedArtifact = findArtifact(artifacts, "phonon_band_dos_json", "phase10h.phonon_band_dos.v1");
  const [tab, setTab] = useState<"plot" | "compatibility" | "band" | "dos" | "json">("plot");
  const [projectionId, setProjectionId] = useState("");
  if (!combinedArtifact) return null;
  const bundle = {
    combined: artifactPayload(combinedArtifact),
    summary: artifactPayload(findArtifact(artifacts, "phonon_summary_json", "phase10h.phonon_band_dos_summary.v1")),
    report: artifactPayload(findArtifact(artifacts, "phonon_compatibility_json", "phase10h.phonon_band_dos_compatibility_report.v1")),
    plot: artifactPayload(findArtifact(artifacts, "plotly_json", "phase10h.phonon_band_dos_plot.v1")),
    table: artifactPayload(findArtifact(artifacts, "table_json", "phase10h.phonon_band_dos_table.v1")),
    manifest: artifactPayload(findArtifact(artifacts, "phonon_manifest_json", "phase10h.phonon_band_dos_manifest.v1")),
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
    <section className="panel phonon-band-dos-preview" data-testid="phonon-band-dos-preview" aria-label="声子色散与态密度组合预览">
      <header className="phonon-band-dos-heading">
        <div><h2>声子色散与态密度</h2><p>已验证的静态结果，共享频率轴</p></div>
      </header>
      <CombinedSummary summary={summary} />
      {warnings.length ? <div className="warning" data-testid="phonon-band-dos-warnings" role="status"><strong>组合数据一致性提示</strong><ul>{warnings.map((warning) => <li key={warning}>{phononWarningLabel(warning)}</li>)}</ul><details><summary>技术详情</summary><code>{warnings.join(" · ")}</code></details></div> : null}
      <p className="notice" data-testid="phonon-band-dos-scope">左侧使用 q 路径距离，右侧使用态密度；两者共享 THz 频率轴。负频率保留为虚频模式。本结果不包含振型、动画、热力学属性或新的声子计算。</p>
      <div className="phonon-band-dos-toolbar">
        {projections.length ? <label>投影态密度
          <select data-testid="phonon-band-dos-projection-selector" value={projectionId} onChange={(event) => setProjectionId(event.target.value)}>
            <option value="">仅总态密度</option>
            {projections.map((projection) => <option key={String(projection.projection_id)} value={String(projection.projection_id)}>{projectionLabel(projection)}</option>)}
          </select>
        </label> : <span>当前显示结果未提供投影态密度。</span>}
        <button type="button" className="secondary" onClick={() => downloadJson(combined, "phonon-band-dos.json")} data-testid="phonon-band-dos-download-json">下载组合数据</button>
      </div>
      <div className="viewer-preview-tabs phonon-band-dos-tabs" role="tablist" aria-label="声子组合查看模式">
        {([
          ["plot", "组合图"], ["compatibility", "一致性检查"], ["band", "色散数据"], ["dos", "态密度数据"], ["json", "结构化数据"],
        ] as const).map(([value, label]) => <button key={value} type="button" role="tab" aria-selected={tab === value} className={tab === value ? "active" : "secondary"} onClick={() => setTab(value)}>{label}</button>)}
      </div>
      <div role="tabpanel" className="phonon-band-dos-tab-panel">
        {tab === "plot" ? <CombinedPlot plot={plot} projectionId={projectionId} plotlyLoader={plotlyLoader} /> : null}
        {tab === "compatibility" ? <CompatibilityPanel report={report} /> : null}
        {tab === "band" ? <BandDataTable plot={plot} /> : null}
        {tab === "dos" ? <DosDataTable plot={plot} projectionId={projectionId} /> : null}
        {tab === "json" ? <div className="phonon-band-dos-json-grid"><JsonDetails title="phonon_band_dos.json" payload={combined} /><JsonDetails title="phonon_band_dos_summary.json" payload={summary} /><JsonDetails title="phonon_band_dos_compatibility_report.json" payload={report} /><JsonDetails title="phonon_band_dos_plot.json" payload={plot} /><JsonDetails title="phonon_band_dos_table.json" payload={table} /><JsonDetails title="phonon_band_dos_manifest.json" payload={manifest} /></div> : null}
      </div>
      <details><summary>技术详情</summary><p data-testid="phonon-band-dos-schema">数据合同：{String(combined.schema_version)}</p></details>
    </section>
  );
}

function CombinedPlot({ plot, projectionId, plotlyLoader }: { plot: JsonRecord; projectionId: string; plotlyLoader: CombinedPlotlyLoader }) {
  const hostRef = useRef<HTMLDivElement>(null);
  const plotlyRef = useRef<PlotlyApi | null>(null);
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState<"loading" | "rendered" | "refused" | "error">("loading");
  const [message, setMessage] = useState("正在加载本地图表渲染器。");
  const mapped = useMemo(() => mapPhononBandDosPlot(plot, projectionId), [plot, projectionId]);
  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    if (!mapped.ok) { setState("refused"); setMessage(mapped.message); return; }
    let active = true;
    let plotly: PlotlyApi | null = null;
    setState("loading");
    setMessage("正在加载本地图表渲染器。");
    plotlyLoader().then(async (api) => {
      if (!active) return;
      plotly = api;
      plotlyRef.current = api;
      await api.newPlot(host, mapped.data, mapped.layout, {responsive: true, displaylogo: false, displayModeBar: false, scrollZoom: false});
      if (!active) { api.purge(host); return; }
      setState("rendered");
      setMessage(`已渲染 ${mapped.bandTraceCount} 条色散曲线和 ${mapped.dosTraceCount} 条态密度系列，共享频率轴。`);
    }).catch(() => {
      if (active) { setState("error"); setMessage("组合图暂时无法渲染；一致性检查、数据表和结构化数据仍可查看。"); }
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
    <div className="phonon-band-dos-plot-actions"><button type="button" className="secondary" disabled={state !== "rendered" || !plotlyRef.current?.downloadImage} onClick={downloadPng} data-testid="phonon-band-dos-download-png">下载图片</button></div>
    <div ref={hostRef} className="phonon-band-dos-plot" data-testid="phonon-band-dos-plot" aria-label="共享频率轴的声子色散与态密度" />
    {state !== "rendered" ? <div className="phonon-band-dos-plot-fallback" data-testid="phonon-band-dos-plot-fallback" role="status"><strong>{state === "refused" ? "图表数据量超出显示范围" : state === "error" ? "图表暂时无法显示" : "正在加载图表"}</strong><p>{message}</p>{state === "error" ? <button type="button" onClick={() => setRetry((value) => value + 1)}>重试图表</button> : null}</div> : null}
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
    type: "scatter", mode: "lines", xaxis: "x", yaxis: "y", name: `分支 ${Number(item.branch_index) + 1}`,
    legendgroup: "bands", showlegend: false, x: numbers(item.path_distance), y: numbers(item.frequencies),
    line: {color: BAND_COLOR, width: 1.45}, hovertemplate: "路径 %{x:.5f}<br>频率 %{y:.5f} THz<extra></extra>",
  }));
  data.push({type: "scatter", mode: "lines", xaxis: "x2", yaxis: "y", name: "总态密度", x: total, y: frequencies, line: {color: DOS_COLOR, width: 2.5}, fill: "tozerox", fillcolor: "rgba(164,63,50,0.10)", hovertemplate: "态密度 %{x:.5f} modes/THz<br>频率 %{y:.5f} THz<extra></extra>"});
  if (selected) data.push({type: "scatter", mode: "lines", xaxis: "x2", yaxis: "y", name: projectionLabel(selected), x: numbers(selected.values), y: frequencies, line: {color: PROJECTION_COLORS[0], width: 1.8, dash: "dash"}, hovertemplate: `${projectionLabel(selected)}<br>态密度 %{{x:.5f}} modes/THz<br>频率 %{{y:.5f}} THz<extra></extra>`});
  const verticalShapes = ticks.map((tick) => ({type: "line", xref: "x", yref: "paper", x0: tick.distance, x1: tick.distance, y0: 0, y1: 1, line: {color: "#d7dce1", width: 1}}));
  const shapes: unknown[] = [
    {type: "rect", xref: "paper", yref: "y", x0: 0, x1: 1, y0: axis.minimum, y1: Math.min(-Number(axis.zero_tolerance), Number(axis.maximum)), fillcolor: "rgba(183,72,60,0.07)", line: {width: 0}, layer: "below"},
    {type: "line", xref: "paper", yref: "y", x0: 0, x1: 1, y0: 0, y1: 0, line: {color: "#30363d", width: 1.4}},
    ...verticalShapes,
  ];
  const layout: JsonRecord = {
    autosize: true, margin: {l: 78, r: 30, t: 42, b: 70}, paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff",
    xaxis: {domain: [0, 0.72], title: {text: "q 路径"}, tickmode: "array", tickvals: ticks.map((tick) => tick.distance), ticktext: ticks.map((tick) => String(tick.label)), zeroline: false},
    xaxis2: {domain: [0.78, 1], title: {text: "态密度（modes/THz）"}, anchor: "y", rangemode: "tozero", zeroline: true},
    yaxis: {title: {text: "频率（THz）"}, range: [axis.minimum, axis.maximum], fixedrange: false},
    showlegend: true, legend: {orientation: "h", x: 0.78, y: 1.08, xanchor: "left"}, hovermode: "closest", shapes,
    annotations: [{xref: "paper", yref: "paper", x: 0.36, y: 1.08, text: "声子色散", showarrow: false}, {xref: "paper", yref: "paper", x: 0.89, y: 1.08, text: "态密度", showarrow: false}],
  };
  const numericValues = Number(display.numeric_values);
  if (!Number.isSafeInteger(numericValues) || numericValues > PHONON_BAND_DOS_CAPS.maxPlotValues || data.length > PHONON_BAND_DOS_CAPS.maxPlotTraces) return {ok: false, message: "PHONON_BAND_DOS_PLOT_BUDGET_EXCEEDED: canonical JSON remains available."};
  return {ok: true, data, layout, bandTraceCount: series.length, dosTraceCount: selected ? 2 : 1, numericValues};
}

function CombinedSummary({ summary }: { summary: JsonRecord }) {
  const items: Array<[string, unknown]> = [
    ["原子数", summary.atom_count], ["分支数", summary.branch_count], ["q 点数", summary.qpoint_count],
    ["态密度网格", summary.dos_grid_point_count], ["投影系列", summary.projection_count],
    ["共享频率范围", `${format(Number(summary.frequency_min))} 至 ${format(Number(summary.frequency_max))} THz`],
    ["一致性", compatibilityLabel(String(summary.compatibility_status))], ["态密度积分 / 预期", `${format(Number(summary.dos_integral))} / ${String(summary.expected_modes)}`],
    ["虚频模式 / 态密度权重", `${String(summary.imaginary_band_mode_count)} / ${format(Number(summary.imaginary_dos_integral))}`],
  ];
  return <dl className="phonon-band-dos-summary" data-testid="phonon-band-dos-summary">{items.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{String(value)}</dd></div>)}</dl>;
}

function CompatibilityPanel({ report }: { report: JsonRecord }) {
  const rows = records(report.checks);
  return <div className="phonon-band-dos-table-wrap"><p data-testid="phonon-band-dos-compatibility-status">一致性状态：<strong>{String(report.status)}</strong>。检查按确定性顺序执行。</p><table data-testid="phonon-band-dos-compatibility-table"><caption>色散与态密度一致性检查</caption><thead><tr><th>检查项</th><th>状态</th><th>色散</th><th>态密度</th><th>结果</th></tr></thead><tbody>{rows.map((row) => <tr key={String(row.name)}><td>{String(row.name)}</td><td>{String(row.status)}</td><td><code>{compact(row.band_value)}</code></td><td><code>{compact(row.dos_value)}</code></td><td>{row.result_code ? <code>{String(row.result_code)}</code> : "-"}</td></tr>)}</tbody></table></div>;
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
  return <div className="phonon-band-dos-table-wrap"><p>显示 {rows.length} 行有界数据。</p><table data-testid="phonon-band-dos-band-table"><caption>组合色散采样</caption><thead><tr><th>分支</th><th>分段</th><th>路径距离</th><th>频率（THz）</th></tr></thead><tbody>{rows.map((row, index) => <tr key={`${row.branch}:${row.segment}:${index}`}><td>{row.branch}</td><td>{row.segment}</td><td>{format(row.path)}</td><td>{format(row.frequency)}</td></tr>)}</tbody></table></div>;
}

function DosDataTable({ plot, projectionId }: { plot: JsonRecord; projectionId: string }) {
  const panel = record(plot.dos_panel) ? plot.dos_panel : {};
  const frequencies = numbers(panel.frequencies);
  const total = numbers(panel.total_dos);
  const selected = records(panel.projections).find((item) => item.projection_id === projectionId);
  const projected = selected ? numbers(selected.values) : [];
  return <div className="phonon-band-dos-table-wrap"><p>显示 {Math.min(frequencies.length, MAX_TABLE_ROWS)} / {frequencies.length} 个态密度网格点。</p><table data-testid="phonon-band-dos-dos-table"><caption>组合态密度采样</caption><thead><tr><th>网格点</th><th>频率（THz）</th><th>总态密度</th>{selected ? <th>{projectionLabel(selected)}</th> : null}</tr></thead><tbody>{frequencies.slice(0, MAX_TABLE_ROWS).map((frequency, index) => <tr key={index}><td>{index}</td><td>{format(frequency)}</td><td>{format(total[index])}</td>{selected ? <td>{format(projected[index])}</td> : null}</tr>)}</tbody></table></div>;
}

function CombinedFallback({ payload, errors }: { payload: unknown; errors: readonly string[] }) {
  return <section className="panel phonon-band-dos-preview" data-testid="phonon-band-dos-preview-invalid" role="status"><h2>声子组合查看器暂时不可用</h2><code>{errors[0] || "PHONON_BAND_DOS_SCHEMA_INVALID"}</code><p>组合数据在图表初始化前未通过校验；结构化数据仍可在结果详情中查看。</p><details><summary>组合数据</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details></section>;
}

async function loadPlotly(): Promise<PlotlyApi> {
  const [coreModule, scatterModule] = await Promise.all([import("plotly.js/lib/core"), import("plotly.js/lib/scatter")]);
  const plotly = ("default" in coreModule ? coreModule.default : coreModule) as unknown as PlotlyApi;
  const scatter = "default" in scatterModule ? scatterModule.default : scatterModule;
  plotly.register?.([scatter]);
  return plotly;
}

function findArtifact(artifacts: Artifact[], type: string, schemaVersion: string): Artifact | undefined { return artifacts.find((artifact) => artifact.type === type && artifactPayload(artifact)?.schema_version === schemaVersion); }
function artifactPayload(artifact?: Artifact): JsonRecord | null { if (!artifact) return null; const metadata = record(artifact.metadata) ? artifact.metadata : null; for (const candidate of [artifact.content, artifact.payload, metadata?.content, metadata?.payload, metadata?.preview]) { if (record(candidate)) return candidate; if (typeof candidate === "string") { try { const parsed = JSON.parse(candidate); if (record(parsed)) return parsed; } catch { /* inert fallback */ } } } return null; }
function JsonDetails({ title, payload }: { title: string; payload: unknown }) { return <details><summary>{title}</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details>; }
function projectionLabel(projection: JsonRecord): string { return projection.projection_type === "atom" ? `原子 ${String(projection.atom_index)}（${String(projection.species)}）` : `元素 ${String(projection.species)}`; }
function downloadJson(payload: JsonRecord, filename: string): void { const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], {type: "application/json"})); const anchor = document.createElement("a"); anchor.href = url; anchor.download = filename; document.body.appendChild(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url); }
function compact(value: unknown): string { const text = typeof value === "string" ? value : JSON.stringify(value); return text.length > 120 ? `${text.slice(0, 117)}...` : text; }
function record(value: unknown): value is JsonRecord { return typeof value === "object" && value !== null && !Array.isArray(value); }
function records(value: unknown): JsonRecord[] { return Array.isArray(value) ? value.filter(record) : []; }
function numbers(value: unknown): number[] { return Array.isArray(value) && value.every(finite) ? value : []; }
function finite(value: unknown): value is number { return typeof value === "number" && Number.isFinite(value); }
function format(value: number): string { return Math.abs(value) >= 1000 || (Math.abs(value) < 0.001 && value !== 0) ? value.toExponential(4) : value.toFixed(5); }
function compatibilityLabel(value: string): string { return ({ compatible: "一致", within_tolerance: "在容差内", incompatible: "不一致" } as Record<string, string>)[value] || value; }
function phononWarningLabel(value: string): string { return ({ PHONON_BAND_DOS_ASR_METADATA_PARTIAL: "声学和规则元数据不完整；当前图表保留原始频率，稳定性判断需结合收敛性复核。" } as Record<string, string>)[value] || "组合结果包含需要在技术详情中复核的限定信息。"; }
