"use client";

import { useEffect, useMemo, useState } from "react";
import { loadPhononPlotly as loadPlotly, usePhononPlot, type PhononPlotlyLoader as PlotlyLoader } from "../phonon-shared/use-phonon-plot";
export type { PhononPlotlyLoader as PlotlyLoader } from "../phonon-shared/use-phonon-plot";

import { validatePhononDosReference } from "../../app/lib/phononContract";
import type { Artifact } from "../../app/lib/planner-api";
import { phononDosPoint, type PhononDosPoint } from "../phonon-shared/phonon-selection";
import { artifactIdentity, artifactChecksum } from "../../shared/workspace/workspace-renderer-registry";

type JsonRecord = Record<string, unknown>;
const MAX_PREVIEW_VALUES = 100_000;
const MAX_TABLE_ROWS = 300;

export function PhononDosPreviewPanel({ artifacts, selected, selectedPoint = null, onPointSelection, plotlyLoader = loadPlotly }: { artifacts: Artifact[]; selected?: Artifact; selectedPoint?: PhononDosPoint | null; onPointSelection?: (point: PhononDosPoint | null) => void; plotlyLoader?: PlotlyLoader }) {
  const dosArtifact = selected?.type === "phonon_dos_json" ? selected : artifacts.find((artifact) => artifact.type === "phonon_dos_json");
  const summaryArtifact = artifacts.find((artifact) => artifact.type === "phonon_summary_json");
  const manifestArtifact = artifacts.find((artifact) => artifact.type === "phonon_manifest_json");
  const payload = useMemo(() => artifactPayload(dosArtifact), [dosArtifact]);
  const sourceKey = dosArtifact ? `${artifactIdentity(dosArtifact)}:${artifactChecksum(dosArtifact)}` : "";
  const [projectionChoice, setProjectionChoice] = useState<{ sourceKey: string; index: number | null }>({sourceKey, index: selectedPoint?.projectionIndex ?? null});
  const projectionIndex = projectionChoice.sourceKey === sourceKey ? projectionChoice.index : selectedPoint?.projectionIndex ?? null;
  const restoredProjection = selectedPoint?.projectionIndex;
  const restoredFrequency = selectedPoint?.frequencyIndex;
  useEffect(() => {
    if (restoredProjection !== undefined && restoredProjection !== null) setProjectionChoice({sourceKey, index: restoredProjection});
  }, [sourceKey, restoredProjection, restoredFrequency]);
  if (!dosArtifact) return null;
  const validation = validatePhononDosReference(payload);
  if (!validation.valid || !record(payload)) return <PhononDosFallback payload={payload} errors={validation.errors} />;
  const dos = payload;
  const summary = artifactPayload(summaryArtifact);
  const manifest = artifactPayload(manifestArtifact);
  const projections = records(dos.projected_dos);
  const point = selectedPoint ? phononDosPoint(dos, `frequency:${selectedPoint.frequencyIndex}`, selectedPoint.projectionIndex === null ? "total" : `projection:${selectedPoint.projectionIndex}`) : null;
  return (
    <section className="phonon-dos-preview phonon-result" data-testid="phonon-dos-preview" aria-label="声子态密度">
      <header className="phonon-dos-heading"><h2>声子态密度</h2><p>{numbers(dos.frequencies).length.toLocaleString("zh-CN")} 个频率点</p></header>
      {validation.warnings.length ? <div className="phonon-reading-note" data-testid="phonon-dos-warnings" role="status"><p>{validation.warnings.some(warning => warning.includes("PHONON_PROJECTED_DOS_SUM_MISMATCH")) ? "投影数据的合计与总态密度存在差异，请结合来源说明解读。" : "源数据包含需要留意的提示，请结合来源说明解读。"}</p><details><summary>查看数据提示</summary><code>{validation.warnings.join(" · ")}</code></details></div> : null}
      {numbers(dos.frequencies).some(value => value < -Number(dos.frequency_zero_tolerance)) ? <p className="phonon-reading-note">负频率区域表示虚频模式的贡献。</p> : null}
      {projections.length ? <label className="phonon-dos-projection-control">投影通道
        <select data-testid="phonon-dos-projection-selector" value={projectionIndex ?? ""} onChange={(event) => setProjectionChoice({sourceKey, index: event.target.value === "" ? null : Number(event.target.value)})}>
          <option value="">仅总态密度</option>
          {projections.map((projection, index) => <option key={projectionKey(projection, index)} value={index}>{projectionLabel(projection)}</option>)}
        </select>
      </label> : null}
      <PhononDosPlot dos={dos} projectionIndex={projectionIndex} plotlyLoader={plotlyLoader} />
      {point && onPointSelection ? <div className="phonon-point-selection" role="status"><span>已选 {point.projection ? projectionLabel(point.projection) : "总态密度"} · {format(point.frequency)} THz · {format(point.density)} modes/THz</span><button type="button" className="product-secondary-action" onClick={() => onPointSelection(null)}>清除选择</button></div> : null}
      <details className="phonon-details"><summary>态密度数值</summary><PhononDosTable dos={dos} projectionIndex={projectionIndex} selectedPoint={point} onPointSelection={onPointSelection} /></details>
      <details className="phonon-details"><summary>数据与来源</summary>
        <PhononDosSummary dos={dos} summary={summary} />
        <p className="phonon-reading-note" data-testid="phonon-dos-scope">曲线沿用源文件的总模式数归一化；未在浏览器中平滑曲线或执行声子计算。</p>
        <p data-testid="phonon-dos-schema">数据格式：{String(dos.schema_version)}</p>
        <div className="phonon-dos-json-grid"><JsonDetails title="phonon_dos.json" payload={dos} />{summary ? <JsonDetails title="phonon_dos_summary.json" payload={summary} /> : null}{manifest ? <JsonDetails title="phonon_manifest.json" payload={manifest} /> : null}</div>
      </details>
    </section>
  );
}

function PhononDosPlot({ dos, projectionIndex, plotlyLoader }: { dos: JsonRecord; projectionIndex: number | null; plotlyLoader: PlotlyLoader }) {
  const mapped = useMemo(() => mapPhononDosPlot(dos, projectionIndex), [dos, projectionIndex]);
  const { hostRef, phase: state, retry } = usePhononPlot(mapped, plotlyLoader);
  const message = state === "rendered" && mapped.ok ? `已显示 ${mapped.pointCount} 个频率点、${mapped.traceCount} 条曲线。`
    : state === "timeout" ? "绘图已等待超过 10 秒，数值与来源仍可查看。" : state === "error" ? "图表未能完成绘制，数值与来源仍可查看。"
    : state === "refused" ? "数据超出交互绘图范围，请查看数值与来源。" : "正在绘制态密度…";
  return <div className="phonon-dos-plot-wrap">
    <div ref={hostRef} className="phonon-dos-plot" data-testid="phonon-dos-plot" aria-label="声子态密度与频率" />
    {state !== "rendered" ? <div className="phonon-dos-plot-fallback" data-testid="phonon-dos-plot-fallback" role={state === "loading" ? "status" : "alert"}><strong>{state === "timeout" ? "图表绘制超时" : state === "refused" ? "图表超出显示范围" : state === "error" ? "图表暂时无法显示" : "正在绘制图表"}</strong><p>{message}</p>{state === "error" || state === "timeout" ? <button type="button" className="product-secondary-action" onClick={retry}>重新绘制图表</button> : null}</div> : null}
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
    ["原子数", dos.atom_count], ["频率点数", frequencies.length], ["频率范围", frequencies.length ? `${format(frequencies[0])} 至 ${format(frequencies.at(-1) ?? 0)} THz` : "-"],
    ["归一化", dos.normalization === "total_modes" ? "总模式数" : dos.normalization], ["积分 / 预期模式数", `${format(Number(integration.observed_integral))} / ${String(integration.expected_mode_count)}`],
    ["虚频区域权重", finite(summary?.imaginary_region_integral) ? format(summary.imaginary_region_integral) : "未提供"],
    ["投影通道数", projections.length], ["投影完整性", ({ complete: "完整", partial: "部分", unknown: "未确定" } as Record<string, string>)[String(summary?.projection_completeness ?? inferredCompleteness(projections))] || "未确定"],
    ["展宽方式", broadening.method === "none" ? "未展宽" : `${String(broadening.method)}（源文件记录）`],
  ];
  return <dl className="phonon-dos-summary" data-testid="phonon-dos-summary">{items.map(([label, value]) => <div key={String(label)}><dt>{label}</dt><dd>{String(value)}</dd></div>)}</dl>;
}

function PhononDosTable({ dos, projectionIndex, selectedPoint, onPointSelection }: { dos: JsonRecord; projectionIndex: number | null; selectedPoint: PhononDosPoint | null; onPointSelection?: (point: PhononDosPoint | null) => void }) {
  const [pageChoice, setPageChoice] = useState({ dos, page: Math.floor((selectedPoint?.frequencyIndex ?? 0) / MAX_TABLE_ROWS) });
  const page = pageChoice.dos === dos ? pageChoice.page : 0;
  const selectedIndex = selectedPoint?.frequencyIndex;
  useEffect(() => {
    if (selectedIndex !== undefined) setPageChoice({ dos, page: Math.floor(selectedIndex / MAX_TABLE_ROWS) });
  }, [dos, selectedIndex]);
  const frequencies = numbers(dos.frequencies);
  const total = numbers(dos.total_dos);
  const projections = records(dos.projected_dos);
  const selected = projectionIndex === null ? null : projections[projectionIndex];
  const projected = selected ? numbers(selected.values) : [];
  const tolerance = Number(dos.frequency_zero_tolerance);
  const start = page * MAX_TABLE_ROWS;
  const rows = frequencies.slice(start, start + MAX_TABLE_ROWS).map((frequency, offset) => { const index = start + offset; return ({
    index, frequency, total: total[index], projected: selected ? projected[index] : null,
    classification: frequency < -tolerance ? "虚频" : Math.abs(frequency) <= tolerance ? "近零" : "实频",
  }); });
  const value = (frequencyIndex: number, projectionIndex: number | null, density: number, label: string) => onPointSelection
    ? <button type="button" className="product-secondary-action phonon-dos-value" aria-label={`选择${label}频率点 ${frequencyIndex}`} aria-pressed={selectedPoint?.frequencyIndex === frequencyIndex && selectedPoint.projectionIndex === projectionIndex} onClick={() => onPointSelection({frequencyIndex, projectionIndex})}>{format(density)}</button>
    : format(density);
  return <>
    {frequencies.length > MAX_TABLE_ROWS ? <div className="phonon-point-selection" aria-label="态密度数值分页"><span>第 {start + 1}–{start + rows.length} / {frequencies.length} 个频率点</span><div><button type="button" className="product-secondary-action" disabled={page === 0} onClick={() => setPageChoice({dos, page: page - 1})}>上一页</button><button type="button" className="product-secondary-action" disabled={start + rows.length >= frequencies.length} onClick={() => setPageChoice({dos, page: page + 1})}>下一页</button></div></div> : null}
    <p className="phonon-reading-note">{onPointSelection ? "点击态密度数值，可选中该点用于研究。" : `共 ${frequencies.length} 个频率点。`}</p>
    <div className="phonon-dos-table-wrap" role="region" aria-label="声子态密度数值，可横向滚动" tabIndex={0}><table data-testid="phonon-dos-table"><caption className="sr-only">声子态密度采样数值</caption><thead><tr><th scope="col">采样点</th><th scope="col">频率（THz）</th><th scope="col">总态密度（modes/THz）</th>{selected ? <th scope="col">{projectionLabel(selected)}（modes/THz）</th> : null}<th scope="col">类型</th></tr></thead><tbody>{rows.map((row) => <tr key={row.index}><td>{row.index}</td><td>{format(row.frequency)}</td><td>{value(row.index, null, row.total, "总态密度")}</td>{selected ? <td>{value(row.index, projectionIndex, row.projected!, projectionLabel(selected))}</td> : null}<td>{row.classification}</td></tr>)}</tbody></table></div>
  </>;
}

function PhononDosFallback({ payload, errors }: { payload: unknown; errors: readonly string[] }) {
  return <section className="phonon-result" data-testid="phonon-dos-preview-invalid" role="alert"><h2>声子态密度暂时无法显示</h2><p>数据格式或数值未通过检查，请核对来源文件。</p><details><summary>技术详情与原始数据</summary><code>{errors[0] || "PHONON_SCHEMA_UNSUPPORTED"}</code><pre>{JSON.stringify(payload, null, 2)}</pre></details></section>;
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
  const data: unknown[] = [{ type: "scatter", mode: "lines", name: "总态密度", x: frequencies, y: total, line: { color: "#176b87", width: 2.5 }, hovertemplate: "频率 %{x:.5f} THz<br>总态密度 %{y:.5f} modes/THz<extra></extra>" }];
  if (selected) data.push({ type: "scatter", mode: "lines", name: projectionLabel(selected), x: frequencies, y: projected, line: { color: "#a54336", width: 1.8, dash: "dash" }, hovertemplate: `${projectionLabel(selected)}<br>频率 %{x:.5f} THz<br>态密度 %{y:.5f} modes/THz<extra></extra>` });
  return { ok: true, data, layout: { autosize: true, margin: { l: 76, r: 24, t: 60, b: 64 }, xaxis: { title: { text: "频率（THz）" }, zeroline: true, zerolinewidth: 1.5, zerolinecolor: "#30363d" }, yaxis: { title: { text: "态密度（modes/THz）" }, rangemode: "tozero" }, showlegend: true, legend: { orientation: "h", x: 0, y: 1.06, yanchor: "bottom" }, hovermode: "x unified", paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff" }, pointCount: frequencies.length, traceCount, numericValues };
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
function JsonDetails({ title, payload }: { title: string; payload: unknown }) { return <details><summary>{title}</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details>; }
function projectionLabel(projection: JsonRecord): string { return projection.projection_type === "atom" ? `原子 ${String(projection.atom_index)} (${String(projection.species)})` : `元素 ${String(projection.species)}`; }
function projectionKey(projection: JsonRecord, index: number): string { return `${String(projection.projection_type)}:${String(projection.atom_index)}:${String(projection.species)}:${index}`; }
function inferredCompleteness(projections: JsonRecord[]): string { return !projections.length ? "unknown" : projections.every((item) => item.source_guarantees_sum === true) ? "complete" : "partial"; }
function record(value: unknown): value is JsonRecord { return typeof value === "object" && value !== null && !Array.isArray(value); }
function records(value: unknown): JsonRecord[] { return Array.isArray(value) ? value.filter(record) : []; }
function numbers(value: unknown): number[] { return Array.isArray(value) ? value.filter(finite) : []; }
function finite(value: unknown): value is number { return typeof value === "number" && Number.isFinite(value); }
function format(value: number): string { return Math.abs(value) >= 1000 || (Math.abs(value) < 0.001 && value !== 0) ? value.toExponential(4) : value.toFixed(5); }
