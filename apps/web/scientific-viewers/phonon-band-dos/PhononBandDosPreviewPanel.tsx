"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { loadPhononPlotly as loadPlotly, usePhononPlot, type PhononPlotlyLoader as CombinedPlotlyLoader } from "../phonon-shared/use-phonon-plot";
export type { PhononPlotlyLoader as CombinedPlotlyLoader } from "../phonon-shared/use-phonon-plot";

import {
  type JsonRecord,
  PHONON_BAND_DOS_CAPS,
  validatePhononBandDosBundle,
} from "../../app/lib/phononBandDosContract";
import type { Artifact } from "../../app/lib/planner-api";

const MAX_TABLE_ROWS = 200;
const BAND_COLOR = "#315d75";
const DOS_COLOR = "#a43f32";
const PROJECTION_COLOR = "#315d75";

export function PhononBandDosPreviewPanel({ artifacts, plotlyLoader = loadPlotly }: { artifacts: Artifact[]; plotlyLoader?: CombinedPlotlyLoader }) {
  const combinedArtifact = findArtifact(artifacts, "phonon_band_dos_json", "phase10h.phonon_band_dos.v1");
  const [projectionId, setProjectionId] = useState("");
  const [jsonExportFailed, setJsonExportFailed] = useState(false);
  const bundle = useMemo(() => ({
    combined: artifactPayload(combinedArtifact),
    summary: artifactPayload(findArtifact(artifacts, "phonon_summary_json", "phase10h.phonon_band_dos_summary.v1")),
    report: artifactPayload(findArtifact(artifacts, "phonon_compatibility_json", "phase10h.phonon_band_dos_compatibility_report.v1")),
    plot: artifactPayload(findArtifact(artifacts, "plotly_json", "phase10h.phonon_band_dos_plot.v1")),
    table: artifactPayload(findArtifact(artifacts, "table_json", "phase10h.phonon_band_dos_table.v1")),
    manifest: artifactPayload(findArtifact(artifacts, "phonon_manifest_json", "phase10h.phonon_band_dos_manifest.v1")),
  }), [artifacts, combinedArtifact]);
  if (!combinedArtifact) return null;
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
    <section className="phonon-band-dos-preview phonon-result phonon-combined-result" data-testid="phonon-band-dos-preview" aria-label="声子色散与态密度组合预览">
      <header className="phonon-band-dos-heading">
        <h2>声子能带与态密度</h2><p>{String(summary.branch_count)} 条分支 · {String(summary.qpoint_count)} 个 q 点 · {String(summary.dos_grid_point_count)} 个频率点</p>
      </header>
      {warnings.length ? <p className="phonon-reading-note" data-testid="phonon-band-dos-warnings" role="status">{[...new Set(warnings.map(phononWarningLabel))].join(" ")}</p> : null}
      <CombinedPlot plot={plot} projectionId={projectionId} projections={projections} onProjectionChange={setProjectionId} plotlyLoader={plotlyLoader} />
      <details className="phonon-details"><summary>能带数值</summary><BandDataTable plot={plot} /></details>
      <details className="phonon-details"><summary>态密度数值</summary><DosDataTable plot={plot} projectionId={projectionId} /></details>
      <details className="phonon-details"><summary>一致性检查</summary><CompatibilityPanel report={report} /></details>
      <details className="phonon-details"><summary>数据与来源</summary>
        <CombinedSummary summary={summary} />
        <p className="phonon-reading-note" data-testid="phonon-band-dos-scope">曲线保留源数据的分支顺序、路径断点和负频率；这里未执行新的声子计算。</p>
        <p data-testid="phonon-band-dos-schema">数据格式：{String(combined.schema_version)}</p>
        {warnings.length ? <p><span>数据提示：</span><code>{warnings.join(" · ")}</code></p> : null}
        <button type="button" className="product-secondary-action" onClick={() => { setJsonExportFailed(false); try { downloadJson(combined, "phonon-band-dos.json"); } catch { setJsonExportFailed(true); } }} data-testid="phonon-band-dos-download-json">下载组合数据</button>
        {jsonExportFailed ? <p role="alert">数据下载未完成，请重试。</p> : null}
        <div className="phonon-band-dos-json-grid"><JsonDetails title="phonon_band_dos.json" payload={combined} /><JsonDetails title="phonon_band_dos_summary.json" payload={summary} /><JsonDetails title="phonon_band_dos_compatibility_report.json" payload={report} /><JsonDetails title="phonon_band_dos_plot.json" payload={plot} /><JsonDetails title="phonon_band_dos_table.json" payload={table} /><JsonDetails title="phonon_band_dos_manifest.json" payload={manifest} /></div>
      </details>
    </section>
  );
}

function CombinedPlot({ plot, projectionId, projections, onProjectionChange, plotlyLoader }: { plot: JsonRecord; projectionId: string; projections: JsonRecord[]; onProjectionChange: (id: string) => void; plotlyLoader: CombinedPlotlyLoader }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [stacked, setStacked] = useState(false);
  useEffect(() => {
    const element = containerRef.current;
    if (!element) return;
    const measure = () => { const width = element.getBoundingClientRect().width; if (width > 0) setStacked(width < 560); };
    measure();
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(measure);
    observer?.observe(element); window.addEventListener("resize", measure);
    return () => { observer?.disconnect(); window.removeEventListener("resize", measure); };
  }, []);
  const mapped = useMemo(() => mapPhononBandDosPlot(plot, projectionId, stacked), [plot, projectionId, stacked]);
  const { hostRef, phase: state, retry, downloadPng, canExport, exportState } = usePhononPlot(mapped, plotlyLoader);
  const message = state === "rendered" && mapped.ok ? `已渲染 ${mapped.bandTraceCount} 条色散曲线和 ${mapped.dosTraceCount} 条态密度曲线，共享频率轴。`
    : state === "timeout" ? "绘图已等待超过 10 秒，数据表和来源仍可查看。" : state === "error" ? "组合图暂时无法渲染；数据表和来源仍可查看。"
    : state === "refused" ? "数据量超出组合图的显示限制，仍可查看一致性检查与来源信息。" : "正在绘制组合图…";
  return <div ref={containerRef} className="phonon-combined-figure" data-layout={stacked ? "stacked" : "side-by-side"}>
    <div className="phonon-band-dos-toolbar">
      {projections.length ? <label>投影通道<select data-testid="phonon-band-dos-projection-selector" value={projectionId} onChange={event => onProjectionChange(event.target.value)}><option value="">仅总态密度</option>{projections.map(projection => <option key={String(projection.projection_id)} value={String(projection.projection_id)}>{projectionLabel(projection)}</option>)}</select></label> : null}
      <button type="button" className="product-secondary-action" disabled={!canExport || exportState === "pending"} onClick={() => downloadPng("phonon-band-dos", stacked ? {width: 500, height: 900} : undefined)} data-testid="phonon-band-dos-download-png">{exportState === "pending" ? "正在导出…" : "下载图片"}</button>
    </div>
    {exportState === "failed" ? <p role="alert">图片导出未完成，请重试。</p> : null}
    <p className="phonon-reading-note">{stacked ? "上下两图采用相同频率刻度。" : "左右两图共享频率轴。"}{record(plot.shared_frequency_axis) && Number(plot.shared_frequency_axis.minimum) < -Number(plot.shared_frequency_axis.zero_tolerance) ? "浅色区域表示虚频范围。" : ""}</p>
    <div className="phonon-band-dos-plot-wrap">
    <div ref={hostRef} className="phonon-band-dos-plot" data-testid="phonon-band-dos-plot" aria-label="共享频率轴的声子色散与态密度" />
    {state !== "rendered" ? <div className="phonon-band-dos-plot-fallback" data-testid="phonon-band-dos-plot-fallback" role="status"><strong>{state === "refused" ? "图表数据量超出显示范围" : state === "timeout" ? "图表绘制超时" : state === "error" ? "图表暂时无法显示" : "正在加载图表"}</strong><p>{message}</p>{state === "error" || state === "timeout" ? <button type="button" onClick={retry}>重试图表</button> : null}</div> : null}
    <p className="sr-only" aria-live="polite" data-testid="phonon-band-dos-live-status">{message}</p>
    <pre hidden data-testid="phonon-band-dos-plot-metrics">{JSON.stringify({state, stacked, sharedFrequencyAxis: mapped.ok, bandTraceCount: mapped.ok ? mapped.bandTraceCount : 0, dosTraceCount: mapped.ok ? mapped.dosTraceCount : 0, numericValues: mapped.ok ? mapped.numericValues : 0, projectionId: projectionId || null, externalRequests: 0})}</pre>
    </div>
  </div>;
}

export function mapPhononBandDosPlot(plot: JsonRecord, projectionId = "", stacked = false): {ok: true; data: unknown[]; layout: JsonRecord; bandTraceCount: number; dosTraceCount: number; numericValues: number} | {ok: false; message: string} {
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
  const dosAxis = stacked ? "y2" : "y";
  data.push({type: "scatter", mode: "lines", xaxis: "x2", yaxis: dosAxis, name: "总态密度", x: total, y: frequencies, line: {color: DOS_COLOR, width: 2.2}, hovertemplate: "态密度 %{x:.5f} modes/THz<br>频率 %{y:.5f} THz<extra></extra>"});
  if (selected) data.push({type: "scatter", mode: "lines", xaxis: "x2", yaxis: dosAxis, name: projectionLabel(selected), x: numbers(selected.values), y: frequencies, line: {color: PROJECTION_COLOR, width: 1.8, dash: "dash"}, hovertemplate: `${projectionLabel(selected)}<br>态密度 %{x:.5f} modes/THz<br>频率 %{y:.5f} THz<extra></extra>`});
  const labels = new Map<number, string[]>();
  for (const tick of ticks) { const distance = Number(tick.distance), names = labels.get(distance) ?? []; if (!names.includes(String(tick.label))) names.push(String(tick.label)); labels.set(distance, names); }
  const shapes: unknown[] = [];
  if (Number(axis.minimum) < -Number(axis.zero_tolerance)) {
    for (const [yref, x0, x1] of stacked ? [["y", 0, 1], ["y2", 0, 1]] : [["y", 0, 0.72], ["y", 0.78, 1]]) {
      shapes.push({type: "rect", xref: "paper", yref, x0, x1, y0: axis.minimum, y1: Math.min(-Number(axis.zero_tolerance), Number(axis.maximum)), fillcolor: "rgba(183,72,60,0.07)", line: {width: 0}, layer: "below"});
    }
  }
  const frequencyAxis = {title: {text: "频率（THz）", standoff: 8, font: {size: 13}}, range: [axis.minimum, axis.maximum], zeroline: true, zerolinecolor: "#59655f", zerolinewidth: 1.2, gridcolor: "#e7ece9", fixedrange: false};
  const layout: JsonRecord = {
    autosize: true, margin: {l: 64, r: 24, t: 36, b: 100}, paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff",
    xaxis: {domain: [0, stacked ? 1 : 0.72], anchor: "y", title: {text: "波矢路径", standoff: 8}, tickmode: "array", tickvals: [...labels.keys()], ticktext: [...labels.values()].map(names => names.join("｜")), zeroline: false, gridcolor: "#e7ece9"},
    xaxis2: {domain: [stacked ? 0 : 0.78, 1], title: {text: "态密度（modes/THz）", standoff: 8, font: {size: 13}}, anchor: dosAxis, rangemode: "tozero", zeroline: true, nticks: 4, gridcolor: "#e7ece9"},
    yaxis: {...frequencyAxis, domain: stacked ? [0.60, 1] : [0, 1]},
    ...(stacked ? {yaxis2: {...frequencyAxis, domain: [0, 0.40], anchor: "x2", matches: "y"}} : {}),
    showlegend: true, legend: {orientation: "h", x: 0, y: stacked ? -0.10 : -0.20, xanchor: "left", yanchor: "top"}, hovermode: "closest", shapes,
    annotations: [{xref: "paper", yref: "paper", x: stacked ? 0.5 : 0.36, y: 1.02, yanchor: "bottom", text: "声子能带", showarrow: false}, {xref: "paper", yref: "paper", x: stacked ? 0.5 : 0.89, y: stacked ? 0.43 : 1.02, yanchor: "bottom", text: "态密度", showarrow: false}],
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
  return <div className="phonon-band-dos-table-wrap" role="region" aria-label="一致性检查，可横向滚动" tabIndex={0}><p data-testid="phonon-band-dos-compatibility-status">一致性：<strong>{compatibilityLabel(String(report.status))}</strong></p><table data-testid="phonon-band-dos-compatibility-table"><caption>色散与态密度一致性检查</caption><thead><tr><th scope="col">检查项</th><th scope="col">结果</th><th scope="col">对照数据</th></tr></thead><tbody>{rows.map(row => <tr key={String(row.name)}><td>{checkLabel(String(row.name))}</td><td>{checkStatusLabel(String(row.status))}</td><td><details><summary>查看对照值</summary><dl><dt>能带</dt><dd><pre>{JSON.stringify(row.band_value, null, 2)}</pre></dd><dt>态密度</dt><dd><pre>{JSON.stringify(row.dos_value, null, 2)}</pre></dd><dt>检查标识</dt><dd><code>{String(row.name)}</code></dd>{row.result_code ? <><dt>技术代码</dt><dd><code>{String(row.result_code)}</code></dd></> : null}</dl></details></td></tr>)}</tbody></table></div>;
}

function BandDataTable({ plot }: { plot: JsonRecord }) {
  if (record(plot.display) && plot.display.mode === "refused") return <p>此组合结果未包含能带逐点数值。请在数据与来源中查找原始能带文件标识。</p>;
  const panel = record(plot.band_panel) ? plot.band_panel : {};
  const rows: Array<{branch: number; segment: number; path: number; frequency: number}> = [];
  for (const series of records(panel.series)) {
    const path = numbers(series.path_distance);
    const frequencies = numbers(series.frequencies);
    for (let index = 0; index < Math.min(path.length, frequencies.length) && rows.length < MAX_TABLE_ROWS; index += 1) rows.push({branch: Number(series.branch_index), segment: Number(series.segment_index), path: path[index], frequency: frequencies[index]});
    if (rows.length >= MAX_TABLE_ROWS) break;
  }
  const total = records(panel.series).reduce((count, series) => count + numbers(series.path_distance).length, 0);
  return <div className="phonon-band-dos-table-wrap" role="region" aria-label="组合能带数值，可横向滚动" tabIndex={0}><p>{rows.length < total ? `显示前 ${rows.length} / ${total} 行，完整数据可在来源中查看。` : `共 ${total} 行。`}</p><table data-testid="phonon-band-dos-band-table"><caption>组合色散采样</caption><thead><tr><th scope="col">分支</th><th scope="col">路径段</th><th scope="col">路径距离（rad/Å）</th><th scope="col">频率（THz）</th></tr></thead><tbody>{rows.map((row, index) => <tr key={`${row.branch}:${row.segment}:${index}`}><td>{row.branch}</td><td>{row.segment}</td><td>{format(row.path)}</td><td>{format(row.frequency)}</td></tr>)}</tbody></table></div>;
}

function DosDataTable({ plot, projectionId }: { plot: JsonRecord; projectionId: string }) {
  if (record(plot.display) && plot.display.mode === "refused") return <p>此组合结果未包含态密度逐点数值。请在数据与来源中查找原始态密度文件标识。</p>;
  const panel = record(plot.dos_panel) ? plot.dos_panel : {};
  const frequencies = numbers(panel.frequencies);
  const total = numbers(panel.total_dos);
  const selected = records(panel.projections).find((item) => item.projection_id === projectionId);
  const projected = selected ? numbers(selected.values) : [];
  return <div className="phonon-band-dos-table-wrap" role="region" aria-label="组合态密度数值，可横向滚动" tabIndex={0}><p>{frequencies.length > MAX_TABLE_ROWS ? `显示前 ${MAX_TABLE_ROWS} / ${frequencies.length} 个频率点，完整数据可在来源中查看。` : `共 ${frequencies.length} 个频率点。`}</p><table data-testid="phonon-band-dos-dos-table"><caption>组合态密度采样</caption><thead><tr><th scope="col">采样点</th><th scope="col">频率（THz）</th><th scope="col">总态密度（modes/THz）</th>{selected ? <th scope="col">{projectionLabel(selected)}</th> : null}</tr></thead><tbody>{frequencies.slice(0, MAX_TABLE_ROWS).map((frequency, index) => <tr key={index}><td>{index}</td><td>{format(frequency)}</td><td>{format(total[index])}</td>{selected ? <td>{format(projected[index])}</td> : null}</tr>)}</tbody></table></div>;
}

function CombinedFallback({ payload, errors }: { payload: unknown; errors: readonly string[] }) {
  return <section className="phonon-result phonon-combined-result" data-testid="phonon-band-dos-preview-invalid" role="alert"><h2>声子组合图暂时无法显示</h2><p>数据格式或来源关联未通过检查，请核对原始文件。</p><details><summary>技术详情与原始数据</summary><code>{errors[0] || "PHONON_BAND_DOS_SCHEMA_INVALID"}</code><pre>{JSON.stringify(payload, null, 2)}</pre></details></section>;
}

function findArtifact(artifacts: Artifact[], type: string, schemaVersion: string): Artifact | undefined { return artifacts.find((artifact) => artifact.type === type && artifactPayload(artifact)?.schema_version === schemaVersion); }
function artifactPayload(artifact?: Artifact): JsonRecord | null { if (!artifact) return null; const metadata = record(artifact.metadata) ? artifact.metadata : null; for (const candidate of [artifact.content, artifact.payload, metadata?.content, metadata?.payload, metadata?.preview]) { if (record(candidate)) return candidate; if (typeof candidate === "string") { try { const parsed = JSON.parse(candidate); if (record(parsed)) return parsed; } catch { /* inert fallback */ } } } return null; }
function JsonDetails({ title, payload }: { title: string; payload: unknown }) { return <details><summary>{title}</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details>; }
function projectionLabel(projection: JsonRecord): string { return projection.projection_type === "atom" ? `原子 ${String(projection.atom_index)}（${String(projection.species)}）` : `元素 ${String(projection.species)}`; }
function downloadJson(payload: JsonRecord, filename: string): void { const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], {type: "application/json"})); const anchor = document.createElement("a"); try { anchor.href = url; anchor.download = filename; document.body.appendChild(anchor); anchor.click(); } finally { anchor.remove(); URL.revokeObjectURL(url); } }
function record(value: unknown): value is JsonRecord { return typeof value === "object" && value !== null && !Array.isArray(value); }
function records(value: unknown): JsonRecord[] { return Array.isArray(value) ? value.filter(record) : []; }
function numbers(value: unknown): number[] { return Array.isArray(value) && value.every(finite) ? value : []; }
function finite(value: unknown): value is number { return typeof value === "number" && Number.isFinite(value); }
function format(value: number): string { return Math.abs(value) >= 1000 || (Math.abs(value) < 0.001 && value !== 0) ? value.toExponential(4) : value.toFixed(5); }
function compatibilityLabel(value: string): string { return ({ compatible: "一致", convertible: "经单位换算后一致", within_tolerance: "在容差内", incompatible: "不一致" } as Record<string, string>)[value] || value; }
function phononWarningLabel(value: string): string { return ({
  PHONON_BAND_DOS_ASR_METADATA_PARTIAL: "声学和规则信息不完整；稳定性判断需结合来源复核。",
  PHONON_BAND_DOS_FREQUENCY_RANGE_DIFFERENCE: "能带与态密度覆盖的频率范围不同，请留意两图的覆盖范围。",
  PHONON_BAND_DOS_LINEAGE_INCOMPLETE: "部分计算来源信息不完整，详情见数据与来源。",
  PHONON_BAND_DOS_PLOT_DEGRADED: "数据量较大，组合图仅显示总态密度；投影数值请查阅原始态密度文件。",
} as Record<string, string>)[value] || "组合数据有需要留意的提示，详情见数据与来源。"; }
function checkStatusLabel(value: string): string { return ({ pass: "通过", fail: "未通过", warning: "需留意", converted: "已换算", skipped: "未检查" } as Record<string, string>)[value] || value; }
function checkLabel(value: string): string { return ({ input_artifacts: "输入文件", band_schema: "能带数据格式", dos_schema: "态密度数据格式", artifact_hashes: "文件校验值", structure_identity: "结构来源", atom_count: "原子数", species_ordering: "元素顺序", cell_lineage: "晶胞设置", source_lineage: "计算来源", force_constants: "力常数来源", frequency_unit: "频率单位", imaginary_encoding: "虚频表示", zero_tolerance: "零频容差", nac: "非解析修正", dos_normalization: "态密度归一化", projection_identity: "投影来源", display_caps: "绘图数据量", frequency_domain: "频率范围", display_options: "绘图设置" } as Record<string, string>)[value] || value; }
