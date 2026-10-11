"use client";

import type { Artifact } from "../../app/lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext, WorkspaceSelectionKind } from "../../app/lib/workspace-api";
import { artifactChecksum, artifactIdentity } from "../../shared/workspace/workspace-renderer-registry";
import { formatPresentationMetricValue } from "../../app/lib/scientific-presentation";
import { presentationLimitationText } from "../../app/lib/scientific-limitation-text";
import { TrajectoryCurve } from "./TrajectoryCurve";
import styles from "./TrajectoryAnalytics.module.css";

type Payload = Record<string, unknown> & { artifactType: "trajectory.rdf" | "trajectory.msd" | "trajectory.diffusion"; schema_version: string; trajectory: Record<string, unknown>; warnings: string[]; limitations: string[] };

export function TrajectoryAnalyticsPanel({ artifacts, selected, workspace, onSelection }: Readonly<{ artifacts: Artifact[]; selected: Artifact; workspace: ScientificWorkspace; onSelection?: (selection: WorkspaceSelectionContext) => void }>) {
  const payload = parse(selected);
  if (!payload) return <section className="workspace-generic-renderer" role="alert"><h5>轨迹分析结果不可用</h5><p>结果契约无法验证，系统不会尝试在浏览器中重新计算。</p></section>;
  const select: Select | null = onSelection && workspace.datasetId && workspace.datasetVersion && workspace.datasetVersion !== "current"
    ? (kind, id, parentId) => emit(workspace, selected, payload, kind, id, parentId, onSelection) : null;
  return <section className={`workspace-generic-renderer ${styles.panel}`} aria-label="轨迹分析" data-testid="trajectory-analytics-panel">
    <header><h5>{title(payload.artifactType)}</h5></header>
    {payload.artifactType === "trajectory.rdf" ? <Rdf payload={payload} select={select} /> : payload.artifactType === "trajectory.msd" ? <Msd payload={payload} select={select} /> : <Diffusion payload={payload} artifacts={artifacts} select={select} />}
    <details className={styles.details}><summary>来源与限制</summary>
    <dl><dt>轨迹校验值</dt><dd><code>{String(payload.trajectory.trajectoryHash ?? "不可用")}</code></dd><dt>结果契约</dt><dd>{payload.schema_version}</dd></dl>
    {payload.warnings.length > 0 && <p role="status">{payload.warnings.map(diffusionStatus).join("；")}</p>}
    <ul>{payload.limitations.map((item) => <li key={item}>{displayLimitation(item)}</li>)}</ul>
    </details>
  </section>;
}

function Rdf({ payload, select }: { payload: Payload; select: Select | null }) {
  const x = numbers(payload.binCentersAngstrom), y = numbers(payload.gR), pair = record(payload.speciesPair), ids = strings(payload.binIds), pairId = String(pair?.pairId ?? "");
  return <><div className={styles.summary}><p>{String(pair?.speciesA)}–{String(pair?.speciesB)} · {x.length} 个采样点</p>{select && <button type="button" className="product-secondary-action" onClick={() => select?.("TRAJECTORY_RDF_PAIR", pairId)}>选择元素对</button>}</div>
    <TrajectoryCurve x={x} series={[{ label: `${String(pair?.speciesA)}–${String(pair?.speciesB)}`, values: y }]} xLabel="距离 r（Å）" yLabel="g(r)" label="径向分布函数曲线" />
    <details className={styles.details}><summary>数值数据 · {x.length} 行</summary><div className={styles.tableScroll} tabIndex={0} role="region" aria-label="径向分布函数数值表"><table><caption>径向分布函数数值表</caption><thead><tr>{select && <th scope="col">选择</th>}<th scope="col">r (Å)</th><th scope="col">g(r)</th></tr></thead><tbody>{x.map((value, index) => <tr key={ids[index]}>{select && <td>{select && <button type="button" className="table-row-select" aria-label={`选择距离 ${value} Å`} onClick={() => select?.("TRAJECTORY_RDF_BIN", ids[index], pairId)}>选择</button>}</td>}<td>{displayNumber(value)}</td><td>{displayNumber(y[index])}</td></tr>)}</tbody></table></div></details></>;
}

function Msd({ payload, select }: { payload: Payload; select: Select | null }) {
  const x = numbers(payload.lagTimesPs), total = numbers(payload.totalMsdAngstrom2), directional = record(payload.directionalMsdAngstrom2), origins = numbers(payload.originCounts), ids = strings(payload.lagIds), seriesId = String(payload.seriesId ?? "");
  const xs = numbers(directional?.x), ys = numbers(directional?.y), zs = numbers(directional?.z);
  return <><div className={styles.summary}><p>{String(payload.species)} · {displayNumber(x[0])}–{displayNumber(x.at(-1))} ps · {x.length} 个滞后时间点</p>{select && <button type="button" className="product-secondary-action" onClick={() => select?.("TRAJECTORY_MSD_SPECIES", seriesId)}>选择 {String(payload.species)} 的 MSD 序列</button>}</div>
    <TrajectoryCurve x={x} series={[{ label: "总 MSD", values: total }, { label: "x 方向", values: xs }, { label: "y 方向", values: ys }, { label: "z 方向", values: zs }]} xLabel="滞后时间（ps）" yLabel="MSD（Å²）" label="均方位移曲线：总 MSD 与 x、y、z 方向" />
    <p className="trajectory-selection-summary">时间原点数：首个滞后点 {origins[0]}，末个滞后点 {origins.at(-1)}</p>
    <details className={styles.details}><summary>数值数据 · {x.length} 行</summary><div className={styles.tableScroll} tabIndex={0} role="region" aria-label="均方位移数值表"><table><caption>均方位移数值表</caption><thead><tr>{select && <th scope="col">选择</th>}<th scope="col">滞后时间 (ps)</th><th scope="col">总 MSD (Å²)</th><th scope="col">x (Å²)</th><th scope="col">y (Å²)</th><th scope="col">z (Å²)</th><th scope="col">时间原点数</th></tr></thead><tbody>{x.map((value, index) => <tr key={ids[index]}>{select && <td>{select && <button type="button" className="table-row-select" aria-label={`选择滞后时间 ${value} ps`} onClick={() => select?.("TRAJECTORY_MSD_LAG", ids[index], seriesId)}>选择</button>}</td>}<td title={String(value)}>{displayNumber(value)}</td>{[total, xs, ys, zs].map((values, axis) => <td key={axis} title={String(values[index])}>{displayNumber(values[index])}</td>)}<td>{displayNumber(origins[index])}</td></tr>)}</tbody></table></div></details></>;
}

function Diffusion({ payload, artifacts, select }: { payload: Payload; artifacts: Artifact[]; select: Select | null }) {
  const fit = record(payload.fit), diagnostic = record(payload.regimeDiagnostic), estimate = record(payload.diffusionEstimate), window = record(payload.fitWindow);
  const windowId = String(window?.windowId ?? ""), diagnosticId = String(diagnostic?.diagnosticId ?? "");
  const parameters = record(payload.resolvedParameters);
  const plot = diffusionPlot(payload, artifacts);
  const accepted = diagnostic?.status === "DIFFUSIVE_WINDOW_ACCEPTED" && estimate?.available === true && finite(estimate.value);
  const metrics = [["拟合时长（ps）", window?.durationPs], ["最短要求（ps）", parameters?.minimum_fit_duration_ps], ["拟合点数", window?.pointCount], ["时间原点覆盖率", diagnostic?.originCoverage], ["斜率（Å²/ps）", fit?.slopeAngstrom2PerPs], ["决定系数 R²", fit?.rSquared], ["拟合误差（Å²）", fit?.rmseAngstrom2], ["扩散指数 α", diagnostic?.alpha]];
  return <><div className={styles.diagnostic} role="status"><div><strong>{diffusionStatus(String(diagnostic?.status ?? ""))}</strong><p>{accepted ? `扩散系数 D：${displayNumber(estimate.value)} Å²/ps（仅限所选窗口）` : "未给出扩散系数；拟合统计不代表通过扩散判据。"}</p></div>{select && <button type="button" className="product-secondary-action" onClick={() => select?.("TRAJECTORY_DIFFUSION_DIAGNOSTIC", diagnosticId, windowId)}>选择诊断</button>}</div>
    <div className={styles.summary}><p>拟合区间：{displayNumber(window?.startPs)}–{displayNumber(window?.endPs)} ps</p>{select && <button type="button" className="product-secondary-action" onClick={() => select?.("TRAJECTORY_DIFFUSION_WINDOW", windowId)}>选择区间</button>}</div>
    {plot ? <TrajectoryCurve x={plot.x} series={plot.series} xLabel="滞后时间（ps）" yLabel="MSD（Å²）" label="所选窗口的 MSD 与已保存拟合线" /> : null}
    <dl className={styles.metrics} aria-label="扩散拟合诊断">{metrics.filter(([, value]) => finite(value)).map(([label, value]) => <div key={String(label)}><dt>{String(label)}</dt><dd title={String(value)}>{displayNumber(value)}</dd></div>)}</dl></>;
}

function diffusionPlot(payload: Payload, artifacts: Artifact[]) {
  const scope = record(payload.scope);
  if (!scope?.toolCallId || !scope.jobId) return null;
  const matches = artifacts.filter(artifact => artifact.type === "plotly_json"
    && artifact.jobId === scope.jobId && artifact.toolCallId === scope.toolCallId);
  if (matches.length !== 1) return null;
  const plot = record(matches[0].content ?? matches[0].payload);
  if (plot?.schema_version !== "phase10n4.trajectory_plot.v1" || plot.artifactType !== "diffusion_fit_plot"
    || !Array.isArray(plot.data) || plot.data.length !== 2) return null;
  const raw = plot.data.map(record), x = raw[0]?.x;
  if (!Array.isArray(x) || !x.length || x.length > 8192 || !x.every(finite)
    || raw[0]?.name !== "MSD" || raw[1]?.name !== "persisted fit"
    || raw.some(trace => !trace || !Array.isArray(trace.x) || trace.x.length !== x.length || trace.x.some((value, i) => value !== x[i])
      || !Array.isArray(trace.y) || trace.y.length !== x.length || !trace.y.every(finite))) return null;
  return { x: x as number[], series: raw.map((trace, i) => ({ label: i === 0 ? "MSD" : "窗口拟合线", values: trace!.y as number[] })) };
}

type Select = (kind: WorkspaceSelectionKind, id: string, parentId?: string) => void;
function emit(workspace: ScientificWorkspace, artifact: Artifact, payload: Payload, kind: WorkspaceSelectionKind, id: string, parentId: string | undefined, onSelection: (selection: WorkspaceSelectionContext) => void) {
  const artifactId = artifactIdentity(artifact), checksum = artifactChecksum(artifact), trajectoryId = String(payload.trajectory.trajectoryHash ?? "");
  if (!artifactId || !checksum || !workspace.datasetId || !workspace.datasetVersion || !trajectoryId || !id) return;
  const base = { selectionSchemaVersion: "1.0" as const, kind, sourceScopeHash: workspace.sourceReferenceHash, projectId: workspace.projectId, datasetId: workspace.datasetId, datasetVersion: workspace.datasetVersion, jobId: workspace.sourceJobId, trajectoryId, artifactId, artifactChecksum: checksum };
  const identity = kind === "TRAJECTORY_RDF_PAIR" ? { speciesPairId: id } : kind === "TRAJECTORY_RDF_BIN" ? { speciesPairId: parentId, rdfBinId: id } : kind === "TRAJECTORY_MSD_SPECIES" ? { msdSeriesId: id } : kind === "TRAJECTORY_MSD_LAG" ? { msdSeriesId: parentId, msdLagId: id } : kind === "TRAJECTORY_DIFFUSION_WINDOW" ? { diffusionWindowId: id } : { diffusionWindowId: parentId, diffusionDiagnosticId: id };
  onSelection({ schemaVersion: "1.0", sourceScopeHash: workspace.sourceReferenceHash, primary: { ...base, ...identity } as never, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
}

function parse(artifact: Artifact): Payload | null {
  const payload = record(artifact.content ?? artifact.payload);
  const expected: Record<string, string> = { "trajectory.rdf": "phase10n4.trajectory_rdf.v1", "trajectory.msd": "phase10n4.trajectory_msd.v1", "trajectory.diffusion": "phase10n4.trajectory_diffusion.v1" };
  const type = typeof payload?.artifactType === "string" ? payload.artifactType : "";
  if (!payload || expected[type] !== payload.schema_version || !record(payload.trajectory) || !stringArray(payload.warnings) || !stringArray(payload.limitations)) return null;
  if (type === "trajectory.msd") {
    const direction = record(payload.directionalMsdAngstrom2), times = payload.lagTimesPs;
    if (!validSeries(times, [payload.totalMsdAngstrom2, direction?.x, direction?.y, direction?.z, payload.originCounts], payload.lagIds)
      || typeof payload.seriesId !== "string" || !payload.seriesId || typeof payload.species !== "string"
      || !(payload.originCounts as number[]).every(value => Number.isInteger(value) && value >= 1)) return null;
  } else if (type === "trajectory.rdf" && (!validSeries(payload.binCentersAngstrom, [payload.gR], payload.binIds) || !record(payload.speciesPair)?.pairId)) return null;
  else if (type === "trajectory.diffusion" && (!record(payload.fitWindow)?.windowId || !record(payload.regimeDiagnostic)?.diagnosticId || !record(payload.diffusionEstimate))) return null;
  return payload as Payload;
}
function record(value: unknown): Record<string, unknown> | null { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function finite(value: unknown): value is number { return typeof value === "number" && Number.isFinite(value); }
function stringArray(value: unknown): value is string[] { return Array.isArray(value) && value.every(item => typeof item === "string"); }
function validSeries(x: unknown, series: unknown[], ids: unknown): boolean {
  return Array.isArray(x) && x.length > 0 && x.length <= 8192 && x.every(finite) && x.every((v, i) => i === 0 || v > x[i - 1])
    && series.every(values => Array.isArray(values) && values.length === x.length && values.every(finite))
    && stringArray(ids) && ids.length === x.length && ids.every(Boolean) && new Set(ids).size === ids.length;
}
function numbers(value: unknown): number[] { return value as number[]; }
function strings(value: unknown): string[] { return value as string[]; }
function displayNumber(value: unknown): string {
  return typeof value === "number" && Number.isFinite(value)
    ? formatPresentationMetricValue(String(value))
    : String(value ?? "不可用");
}
function title(type: Payload["artifactType"]): string { return type === "trajectory.rdf" ? "径向分布函数（RDF）" : type === "trajectory.msd" ? "均方位移（MSD）" : "轨迹扩散分析"; }
function diffusionStatus(status: string): string {
  return {
    DIFFUSIVE_WINDOW_ACCEPTED: "拟合区间满足扩散判据",
    INSUFFICIENT_DURATION: "拟合窗口时长不足",
    INSUFFICIENT_POINTS: "拟合点数量不足",
    INSUFFICIENT_ORIGIN_COVERAGE: "时间原点覆盖不足",
    NON_POSITIVE_SLOPE: "拟合斜率非正",
    POOR_LINEAR_FIT: "线性拟合质量不足",
    INSUFFICIENT_MSD_SIGNAL: "均方位移信号不足",
    BALLISTIC_LIKE_WINDOW: "所选窗口呈类弹道行为",
    NON_DIFFUSIVE_WINDOW: "所选窗口未满足扩散判据",
    INSUFFICIENT_FIT_POINTS: "拟合点数量不足",
    LOW_ORIGIN_COVERAGE: "时间原点覆盖不足",
    LOW_R_SQUARED: "线性拟合质量不足",
    NON_DIFFUSIVE_ALPHA: "扩散指数不满足判据",
  }[status] ?? (status || "诊断状态不可用");
}
function displayLimitation(value: string): string {
  if (value === "Diffusion is estimated only over the explicitly selected fit window and is not an unconditional long-time bulk diffusion coefficient.") {
    return "扩散系数仅针对明确选择的拟合区间，不代表无条件的长时间体扩散系数。";
  }
  if (value === "Bounded persisted result.") return "该结果来自有界、已持久化的科学输出。";
  return presentationLimitationText(value);
}

export default TrajectoryAnalyticsPanel;
