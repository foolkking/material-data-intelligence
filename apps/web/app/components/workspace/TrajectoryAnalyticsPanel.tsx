"use client";

import type { Artifact } from "../../lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext, WorkspaceSelectionKind } from "../../lib/workspace-api";
import { artifactChecksum, artifactIdentity } from "./workspace-renderer-registry";
import { formatPresentationMetricValue } from "../../lib/scientific-presentation";

type Payload = Record<string, unknown> & { artifactType: "trajectory.rdf" | "trajectory.msd" | "trajectory.diffusion"; schema_version: string; trajectory: Record<string, unknown>; warnings: string[]; limitations: string[] };

export function TrajectoryAnalyticsPanel({ selected, workspace, onSelection }: Readonly<{ artifacts: Artifact[]; selected: Artifact; workspace: ScientificWorkspace; onSelection: (selection: WorkspaceSelectionContext) => void }>) {
  const payload = parse(selected);
  if (!payload) return <section className="workspace-generic-renderer" role="alert"><h5>轨迹分析结果不可用</h5><p>结果契约无法验证，系统不会尝试在浏览器中重新计算。</p></section>;
  return <section className="workspace-generic-renderer trajectory-analytics-panel" aria-label="轨迹分析" data-testid="trajectory-analytics-panel">
    <header><h5>{title(payload.artifactType)}</h5><p>读取已持久化的科学结果；浏览器只负责展示，不会重新计算。</p></header>
    {payload.artifactType === "trajectory.rdf" ? <Rdf payload={payload} select={(kind, id, parentId) => emit(workspace, selected, payload, kind, id, parentId, onSelection)} /> : payload.artifactType === "trajectory.msd" ? <Msd payload={payload} select={(kind, id, parentId) => emit(workspace, selected, payload, kind, id, parentId, onSelection)} /> : <Diffusion payload={payload} select={(kind, id, parentId) => emit(workspace, selected, payload, kind, id, parentId, onSelection)} />}
    <h6>来源与限制</h6>
    <dl><dt>轨迹校验值</dt><dd><code>{String(payload.trajectory.trajectoryHash ?? "不可用")}</code></dd><dt>结果契约</dt><dd>{payload.schema_version}</dd></dl>
    {payload.warnings.length > 0 && <p role="status">警告：{payload.warnings.join("；")}</p>}
    <ul>{payload.limitations.map((item) => <li key={item}>{displayLimitation(item)}</li>)}</ul>
  </section>;
}

function Rdf({ payload, select }: { payload: Payload; select: Select }) {
  const x = numbers(payload.binCentersAngstrom), y = numbers(payload.gR), pair = record(payload.speciesPair), window = record(payload.window), ids = strings(payload.binIds), pairId = String(pair?.pairId ?? "");
  return <><p className="trajectory-selection-summary"><strong>元素对：</strong> {String(pair?.speciesA)}–{String(pair?.speciesB)}；分析窗口：{String(window?.mode)}。 <button type="button" className="product-secondary-action" onClick={() => select("TRAJECTORY_RDF_PAIR", pairId)}>选择元素对</button></p><div className="workspace-table-scroll"><table><caption>径向分布函数数值表</caption><thead><tr><th scope="col">选择</th><th scope="col">r (Å)</th><th scope="col">g(r)</th></tr></thead><tbody>{x.map((value, index) => <tr key={ids[index] ?? `${value}:${index}`}><td><button type="button" className="table-row-select" onClick={() => select("TRAJECTORY_RDF_BIN", ids[index], pairId)}>选择</button></td><td>{displayNumber(value)}</td><td>{displayNumber(y[index])}</td></tr>)}</tbody></table></div></>;
}

function Msd({ payload, select }: { payload: Payload; select: Select }) {
  const x = numbers(payload.lagTimesPs), total = numbers(payload.totalMsdAngstrom2), directional = record(payload.directionalMsdAngstrom2), origins = numbers(payload.originCounts), ids = strings(payload.lagIds), seriesId = String(payload.seriesId ?? "");
  const xs = numbers(directional?.x), ys = numbers(directional?.y), zs = numbers(directional?.z);
  return <><button type="button" className="product-secondary-action trajectory-series-action" onClick={() => select("TRAJECTORY_MSD_SPECIES", seriesId)}>选择 {String(payload.species)} 的 MSD 序列</button><div className="workspace-table-scroll"><table><caption>均方位移数值表</caption><thead><tr><th scope="col">选择</th><th scope="col">滞后时间 (ps)</th><th scope="col">总 MSD (Å²)</th><th scope="col">x</th><th scope="col">y</th><th scope="col">z</th><th scope="col">时间原点数</th></tr></thead><tbody>{x.map((value, index) => <tr key={ids[index] ?? `${value}:${index}`}><td><button type="button" className="table-row-select" onClick={() => select("TRAJECTORY_MSD_LAG", ids[index], seriesId)}>选择</button></td><td>{displayNumber(value)}</td><td>{displayNumber(total[index])}</td><td>{displayNumber(xs[index])}</td><td>{displayNumber(ys[index])}</td><td>{displayNumber(zs[index])}</td><td>{displayNumber(origins[index])}</td></tr>)}</tbody></table></div></>;
}

function Diffusion({ payload, select }: { payload: Payload; select: Select }) {
  const fit = record(payload.fit), diagnostic = record(payload.regimeDiagnostic), estimate = record(payload.diffusionEstimate), window = record(payload.fitWindow);
  const windowId = String(window?.windowId ?? ""), diagnosticId = String(diagnostic?.diagnosticId ?? "");
  return <><div className="trajectory-diagnostic-status" role="status"><strong>{diffusionStatus(String(diagnostic?.status ?? ""))}</strong><button type="button" className="product-secondary-action" onClick={() => select("TRAJECTORY_DIFFUSION_DIAGNOSTIC", diagnosticId, windowId)}>设为当前诊断</button></div><div className="workspace-table-scroll"><table><caption>扩散拟合诊断</caption><tbody><tr><th scope="row">拟合区间 (ps)</th><td><span>{displayNumber(window?.startPs)}–{displayNumber(window?.endPs)}</span><button type="button" className="table-row-select trajectory-inline-action" onClick={() => select("TRAJECTORY_DIFFUSION_WINDOW", windowId)}>选择区间</button></td></tr><tr><th scope="row">斜率 (Å²/ps)</th><td>{displayNumber(fit?.slopeAngstrom2PerPs)}</td></tr><tr><th scope="row">决定系数 R²</th><td>{displayNumber(fit?.rSquared)}</td></tr><tr><th scope="row">扩散指数 α</th><td>{displayNumber(diagnostic?.alpha)}</td></tr><tr><th scope="row">限定扩散系数 D (Å²/ps)</th><td>{estimate?.available ? displayNumber(estimate.value) : "未给出"}</td></tr></tbody></table></div></>;
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
  if (!payload || expected[type] !== payload.schema_version || !record(payload.trajectory) || !Array.isArray(payload.warnings) || !Array.isArray(payload.limitations)) return null;
  return payload as Payload;
}
function record(value: unknown): Record<string, unknown> | null { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function numbers(value: unknown): number[] { return Array.isArray(value) ? value.filter((item): item is number => typeof item === "number" && Number.isFinite(item)) : []; }
function strings(value: unknown): string[] { return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : []; }
function displayNumber(value: unknown): string {
  return typeof value === "number" && Number.isFinite(value)
    ? formatPresentationMetricValue(String(value))
    : String(value ?? "不可用");
}
function title(type: Payload["artifactType"]): string { return type === "trajectory.rdf" ? "径向分布函数（RDF）" : type === "trajectory.msd" ? "均方位移（MSD）" : "轨迹扩散分析"; }
function diffusionStatus(status: string): string {
  return {
    DIFFUSIVE_WINDOW_ACCEPTED: "拟合区间满足扩散判据",
    INSUFFICIENT_DURATION: "轨迹时长不足",
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
  return value;
}

export default TrajectoryAnalyticsPanel;
