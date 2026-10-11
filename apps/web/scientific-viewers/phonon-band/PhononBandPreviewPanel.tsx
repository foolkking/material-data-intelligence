"use client";

import { useMemo } from "react";
import { loadPhononPlotly as loadPlotly, usePhononPlot, type PhononPlotlyLoader as PlotlyLoader } from "../phonon-shared/use-phonon-plot";

import { validatePhononBandReference } from "../../app/lib/phononContract";
import type { Artifact } from "../../app/lib/planner-api";
import type { PhononBandPoint } from "../phonon-shared/phonon-selection";

type JsonRecord = Record<string, unknown>;

const MAX_PREVIEW_VALUES = 500_000;
const MAX_PREVIEW_TRACES = 4_096;
const MAX_TABLE_ROWS = 200;

export function PhononBandPreviewPanel({ artifacts, selected, selectedPoint = null, onPointSelection, plotlyLoader = loadPlotly }: { artifacts: Artifact[]; selected?: Artifact; selectedPoint?: PhononBandPoint | null; onPointSelection?: (point: PhononBandPoint | null) => void; plotlyLoader?: PlotlyLoader }) {
  const bandArtifact = selected?.type === "phonon_band_json" ? selected : artifacts.find((artifact) => artifact.type === "phonon_band_json");
  const summaryArtifact = artifacts.find((artifact) => artifact.type === "phonon_summary_json");
  const manifestArtifact = artifacts.find((artifact) => artifact.type === "phonon_manifest_json");
  const animationArtifact = artifacts.find((artifact) => artifact.type === "phonon_animation_json");
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
    <section className="phonon-band-preview phonon-result" data-testid="phonon-band-preview" aria-label="声子能带">
      <header className="phonon-band-heading">
        <h2>声子能带</h2><p>{records(band.branches).length} 条分支 · {records(band.qpoints).length} 个 q 点</p>
      </header>
      {records(band.branches).some(branch => numbers(branch.frequencies).some(value => value < -Number(band.frequency_zero_tolerance))) ? <p className="phonon-reading-note">负频率表示虚频模式，已按源数据保留。</p> : null}
      <PhononBandPlot band={band} plotlyLoader={plotlyLoader} />
      {selectedPoint && onPointSelection ? <div className="phonon-point-selection" role="status"><span>已选 q 点 {selectedPoint.qpointIndex} · 分支 {selectedPoint.branchIndex}</span><button type="button" className="product-secondary-action" onClick={() => onPointSelection(null)}>清除选择</button></div> : null}
      <details className="phonon-details"><summary>能带数值</summary><PhononBandTable band={band} selectedPoint={selectedPoint} onPointSelection={onPointSelection} /></details>
      {animationArtifact ? <div className="phonon-band-handoff" data-testid="phonon-band-animation-handoff"><span>{handoff.ok ? `已关联 q 点 ${handoff.qpointIndex}、分支 ${handoff.branchIndex} 的振动模式。` : "振动模式与当前能带无法对应。"}</span>{handoff.ok ? <button type="button" className="product-secondary-action" onClick={()=>document.querySelector('[data-testid="phonon-animation-preview-panel"]')?.scrollIntoView({behavior:"auto",block:"start"})}>查看振动动画</button> : <details><summary>技术详情</summary><code>{handoff.code}</code></details>}</div> : null}
      <details className="phonon-details"><summary>数据与来源</summary>
        <PhononBandSummary band={band} summary={summary} />
        <p className="phonon-reading-note" data-testid="phonon-band-scope">保留源文件的分支顺序与负频率；这里未执行插值或新的声子计算。</p>
        <p data-testid="phonon-band-schema">数据格式：{String(band.schema_version)}</p>
        <div className="phonon-band-json-grid"><JsonDetails title="phonon_band.json" payload={band} />{summary ? <JsonDetails title="phonon_summary.json" payload={summary} /> : null}{manifest ? <JsonDetails title="phonon_manifest.json" payload={manifest} /> : null}</div>
      </details>
    </section>
  );
}

function PhononBandPlot({ band, plotlyLoader }: { band: JsonRecord; plotlyLoader: PlotlyLoader }) {
  const mapped = useMemo(() => mapPhononBandPlot(band), [band]);
  const { hostRef, phase: state, retry } = usePhononPlot(mapped, plotlyLoader);
  const message = state === "rendered" && mapped.ok ? `已显示 ${mapped.branchCount} 条分支、${mapped.segmentCount} 段路径。`
    : state === "timeout" ? "绘图已等待超过 10 秒，数值与来源仍可查看。" : state === "error" ? "图表未能完成绘制，数值与来源仍可查看。"
    : state === "refused" ? "数据超过交互绘图上限，请查看数值与来源。" : "正在绘制声子能带…";
  return <div className="phonon-band-plot-wrap">
    <div ref={hostRef} className="phonon-band-plot" data-testid="phonon-band-plot" aria-label="声子频率与波矢路径" />
    {state !== "rendered" ? <div className="phonon-band-plot-fallback" data-testid="phonon-band-plot-fallback" role={state === "loading" ? "status" : "alert"}><strong>{state === "timeout" ? "图表绘制超时" : state === "refused" ? "图表超出显示范围" : state === "error" ? "图表暂时无法显示" : "正在绘制图表"}</strong><p>{message}</p>{state === "error" || state === "timeout" ? <button type="button" className="product-secondary-action" onClick={retry}>重新绘制图表</button> : null}</div> : null}
    <p className="sr-only" aria-live="polite" data-testid="phonon-band-live-status">{message}</p>
    <pre hidden data-testid="phonon-band-plot-metrics">{JSON.stringify({ state, branchCount: mapped.ok ? mapped.branchCount : 0, segmentCount: mapped.ok ? mapped.segmentCount : 0, traceCount: mapped.ok ? mapped.data.length : 0, numericValues: mapped.ok ? mapped.numericValues : 0, negativePreserved: true, externalRequests: 0 })}</pre>
  </div>;
}

function PhononBandSummary({ band, summary }: { band: JsonRecord; summary: JsonRecord | null }) {
  const branches = records(band.branches);
  const qpoints = records(band.qpoints);
  const segments = records(band.segments);
  const frequencies = branches.flatMap((branch) => numbers(branch.frequencies));
  const frequencyRange = numericRange(frequencies);
  const species = Array.isArray(band.species) ? band.species.map(String) : [];
  return <dl className="phonon-band-summary" data-testid="phonon-band-summary">
    <div><dt>原子数</dt><dd>{String(band.atom_count)}</dd></div>
    <div><dt>元素顺序</dt><dd>{species.join(", ")}</dd></div>
    <div><dt>分支数</dt><dd>{branches.length}</dd></div>
    <div><dt>q 点数</dt><dd>{qpoints.length}</dd></div>
    <div><dt>路径段数</dt><dd>{segments.length}</dd></div>
    <div><dt>频率范围</dt><dd>{finite(summary?.frequency_min) ? summary?.frequency_min : frequencyRange?.[0] ?? "未提供"} 至 {finite(summary?.frequency_max) ? summary?.frequency_max : frequencyRange?.[1] ?? "未提供"} THz</dd></div>
  </dl>;
}

function PhononBandTable({ band, selectedPoint, onPointSelection }: { band: JsonRecord; selectedPoint: PhononBandPoint | null; onPointSelection?: (point: PhononBandPoint | null) => void }) {
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
        classification: frequency < -zeroTolerance ? "虚频" : Math.abs(frequency) <= zeroTolerance ? "近零" : "实频",
      });
    }
    return result;
  }, [band]);
  const total = records(band.qpoints).length * records(band.branches).length;
  return <div className="phonon-band-table-wrap" role="region" aria-label="声子能带数值，可横向滚动" tabIndex={0}><p>{rows.length < total ? `显示前 ${rows.length} / ${total} 行，完整数据可在来源中查看。` : `共 ${total} 行。`}</p><table data-testid="phonon-band-table"><caption>声子能带采样数值</caption><thead><tr>{onPointSelection ? <th scope="col">选择</th> : null}<th scope="col">q 点</th><th scope="col">路径段</th><th scope="col">q 坐标</th><th scope="col">标签</th><th scope="col">路径距离（rad/Å）</th><th scope="col">分支</th><th scope="col">频率（THz）</th><th scope="col">类型</th></tr></thead><tbody>{rows.map((row) => <tr key={`${row.qpoint}:${row.branch}`}>
    {onPointSelection ? <td><button type="button" className="product-secondary-action" aria-label={`选择 q 点 ${row.qpoint}、分支 ${row.branch}`} aria-pressed={selectedPoint?.qpointIndex === row.qpoint && selectedPoint.branchIndex === row.branch} onClick={() => onPointSelection({qpointIndex: row.qpoint, branchIndex: row.branch})}>选择</button></td> : null}
    <td>{row.qpoint}</td><td>{row.segment}</td><td>[{row.coordinates.map(format).join(", ")}]</td><td>{row.label || "-"}</td><td>{format(row.distance)}</td><td>{row.branch}</td><td>{format(row.frequency)}</td><td>{row.classification}</td></tr>)}</tbody></table></div>;
}

function PhononBandFallback({ payload, errors }: { payload: unknown; errors: readonly string[] }) {
  return <section className="phonon-result" data-testid="phonon-band-preview-invalid" role="alert"><h2>声子能带暂时无法显示</h2><p>数据格式或数值未通过检查，请核对来源文件。</p><details><summary>技术详情与原始数据</summary><code>{errors[0] || "PHONON_SCHEMA_UNSUPPORTED"}</code><pre>{JSON.stringify(payload, null, 2)}</pre></details></section>;
}

function JsonDetails({ title, payload }: { title: string; payload: unknown }) { return <details><summary>{title}</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details>; }

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
    data.push({ type: "scatter", mode: "lines", name: `分支 ${Number(branch.branch_index) + 1}`, legendgroup: `branch-${String(branch.branch_index)}`, showlegend: false, line: { color: "#176b87", width: 1.6 }, x: qpoints.slice(start, end).map((point) => Number(point.distance)), y: numbers(branch.frequencies).slice(start, end), hovertemplate: "路径 %{x:.5f}<br>频率 %{y:.5f} THz<extra></extra>" });
  }
  const labels = new Map<number, string[]>();
  for (const point of qpoints) {
    if (typeof point.label !== "string" || !point.label) continue;
    const distance = Number(point.distance);
    const names = labels.get(distance) ?? [];
    if (!names.includes(point.label)) names.push(point.label);
    labels.set(distance, names);
  }
  return { ok: true, data, layout: { autosize: true, margin: { l: 72, r: 20, t: 24, b: 64 }, xaxis: { title: { text: "波矢路径" }, tickmode: "array", tickvals: [...labels.keys()], ticktext: [...labels.values()].map(names => names.join("｜")) }, yaxis: { title: { text: "频率（THz）" }, zeroline: true }, showlegend: false, hovermode: "x unified", paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff" }, branchCount: branches.length, segmentCount: segments.length, numericValues };
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
function numericRange(values: readonly number[]): [number, number] | null {
  if (!values.length) return null;
  let minimum = values[0], maximum = values[0];
  for (let index = 1; index < values.length; index += 1) {
    const value = values[index];
    if (value < minimum) minimum = value;
    if (value > maximum) maximum = value;
  }
  return [minimum, maximum];
}
function format(value: number): string { return Math.abs(value) >= 1000 || (Math.abs(value) < 0.001 && value !== 0) ? value.toExponential(4) : value.toFixed(5); }

export function phononAnimationHandoff(band:JsonRecord,artifact:Artifact,animation:JsonRecord|null):{ok:true;modeId:string;qpointIndex:number;branchIndex:number}|{ok:false;code:string}{
  if(!animation)return{ok:false,code:"PHONON_ANIMATION_EIGENVECTOR_UNAVAILABLE"};const mode=record(animation.mode)&&record(animation.mode.mode)?animation.mode.mode:null;const source=record(animation.source)?animation.source:null;if(!mode||!source||typeof mode.mode_id!=="string")return{ok:false,code:"PHONON_ANIMATION_HANDOFF_INVALID"};
  const artifactHash=artifact.sha256||artifact.contentHash;const expected=source.band_sha256;const modeArtifact=record(mode.band_artifact)?mode.band_artifact:null;if(typeof artifactHash!=="string"||artifactHash!==expected||modeArtifact?.sha256!==expected)return{ok:false,code:"PHONON_ANIMATION_BAND_HASH_MISMATCH"};
  const qpointIndex=Number(mode.qpoint_index),branchIndex=Number(mode.branch_index);const qpoint=records(band.qpoints).find((item)=>Number(item.index)===qpointIndex);const branch=records(band.branches).find((item)=>Number(item.branch_index)===branchIndex);const frequency=branch?numbers(branch.frequencies)[qpointIndex]:undefined;if(!qpoint||!branch||!finite(frequency)||Math.abs(frequency-Number(mode.frequency))>Number(mode.frequency_tolerance))return{ok:false,code:"PHONON_ANIMATION_MODE_REFERENCE_STALE"};
  return{ok:true,modeId:String(mode.mode_id),qpointIndex,branchIndex};
}
