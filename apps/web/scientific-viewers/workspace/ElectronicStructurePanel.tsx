"use client";

import { useMemo, useState } from "react";
import type { Artifact } from "../../app/lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext, WorkspaceSelectionKind } from "../../app/lib/workspace-api";
import { artifactChecksum, artifactIdentity } from "../../shared/workspace/workspace-renderer-registry";
import { ElectronicPlot } from "./ElectronicPlot";
import { ELECTRONIC_POINT_LIMIT, electronicNumber, electronicPlotData, electronicSpinLabel, type ElectronicPlotData } from "./electronic-plot";

type Payload = Record<string, unknown> & { artifactType: "electronic.band_structure" | "electronic.dos"; schemaVersion: string; sourceResource: Record<string, unknown>; warnings: string[]; limitations: string[] };
const MAX_TABLE_ROWS = 500;

export function ElectronicStructurePanel({ artifacts, selected, workspace, onSelection }: Readonly<{ artifacts: Artifact[]; selected: Artifact; workspace: ScientificWorkspace; onSelection: (selection: WorkspaceSelectionContext) => void }>) {
  const current = parse(selected);
  if (!current) return <section className="workspace-generic-renderer" role="alert"><h5>电子结构数据暂时无法显示</h5><p>数据格式或数值未通过检查，请查看来源文件。</p><details><summary>技术详情</summary><code>N5_ELECTRONIC_CONTRACT_INVALID</code></details></section>;
  const parsed = artifacts.map((artifact) => ({ artifact, payload: parse(artifact) })).filter((item): item is { artifact: Artifact; payload: Payload } => item.payload !== null);
  const band = (current.artifactType === "electronic.band_structure" ? { artifact: selected, payload: current } : parsed.find(item => item.payload.artifactType === "electronic.band_structure")) ?? null;
  const dos = (current.artifactType === "electronic.dos" ? { artifact: selected, payload: current } : parsed.find(item => item.payload.artifactType === "electronic.dos")) ?? null;
  const compatible = band && dos ? compatibility(band.payload, dos.payload) : null;
  const sources = (current.artifactType === "electronic.dos" ? [dos, band] : [band, dos]).filter((item): item is { artifact: Artifact; payload: Payload } => item !== null);
  return <section className="workspace-generic-renderer electronic-structure-panel" aria-label="电子结构" data-testid="electronic-structure-panel">
    {compatible === false ? <p className="electronic-data-note" role="status">这两份数据的来源或能量参考不同，曲线分别显示，请勿直接合并比较。</p> : null}
    {sources.map(({ artifact, payload }) => payload.artifactType === "electronic.band_structure" ? <BandView key={`${artifactIdentity(artifact)}:${artifactChecksum(artifact)}`} artifact={artifact} payload={payload} workspace={workspace} onSelection={onSelection} /> : <DosView key={`${artifactIdentity(artifact)}:${artifactChecksum(artifact)}`} artifact={artifact} payload={payload} workspace={workspace} onSelection={onSelection} />)}
    {sources.some(item => item.payload.warnings.length) ? <p className="electronic-data-note" role="status">源数据附带提示，详见“数据与来源”。</p> : null}
    <details className="electronic-source-details"><summary>数据与来源</summary>
      {compatible !== null ? <p data-testid="electronic-combined-status">{compatible ? "数据源、能量参考、费米能级和自旋语义完全兼容。" : "DO_NOT_COMBINE：电子结构来源语义不兼容。"}</p> : null}
      {sources.map(({ artifact, payload }) => <section key={artifactIdentity(artifact)}><h6>{payload.artifactType === "electronic.band_structure" ? "能带来源" : "态密度来源"}</h6>
        <dl><div><dt>工具</dt><dd>{String(record(payload.tool)?.toolId ?? "未提供")}@{String(record(payload.tool)?.toolVersion ?? "未提供")}</dd></div><div><dt>资源</dt><dd><code>{String(payload.sourceResource.resourceHash ?? "未提供")}</code></dd></div><div><dt>计算标识</dt><dd>{String(payload.sourceResource.calculationIdentity ?? "未提供")}</dd></div><div><dt>能量参考</dt><dd>{String(record(payload.energy)?.reference ?? "未提供")}</dd></div><div><dt>契约</dt><dd>{payload.schemaVersion}</dd></div></dl>
        {payload.warnings.length ? <p>数据提示：{payload.warnings.join(" · ")}</p> : null}<ul>{payload.limitations.map(item => <li key={item}>{item}</li>)}</ul>
      </section>)}
    </details>
  </section>;
}

function BandView({ artifact, payload, workspace, onSelection }: PanelItemProps) {
  const gap = record(payload.gap), kpoints = records(payload.kpoints), states = records(payload.states);
  const plot = useMemo(() => electronicPlotData(payload, "band"), [payload]);
  const pagination = useTablePage(states.length);
  const visibleStates = states.slice(pagination.start, pagination.end);
  const points = new Map(kpoints.map(point => [point.kpointId, point]));
  const gapValue = gap?.valueEv;
  const hasGap = typeof gapValue === "number" && Number.isFinite(gapValue);
  return <section className="electronic-result-section" aria-label="电子能带结构" data-testid="electronic-band-view">
    <header className="electronic-section-heading"><h6>电子能带</h6><span>{plot.totalSeries} 条能带 · {kpoints.length} 个 k 点</span></header>
    <div className="electronic-gap-summary">{hasGap ? <><span>采样带隙</span><strong>{electronicNumber(gapValue)} eV</strong><span>{gap?.directness === "DIRECT" ? "直接带隙" : gap?.directness === "INDIRECT" ? "间接带隙" : "类型未确定"}</span><button type="button" className="product-secondary-action" onClick={() => emit(workspace, artifact, payload, "ELECTRONIC_BAND_GAP", {}, onSelection)}>选择带隙</button></> : <span>源数据未提供带隙结果。</span>}</div>
    {plot.curves.length ? <ElectronicPlot data={plot} kind="band" /> : <p role="status">当前能带结果没有可绘制的有限数值或完整坐标；原始数值仍可查看。</p>}
    <PlotNotice plot={plot} kind="band" />
    <details className="electronic-numeric-details"><summary>能带数值 · {states.length.toLocaleString("zh-CN")} 条</summary>
      <TablePager label="能带" {...pagination} />
      <div className="workspace-table-scroll" role="region" aria-label="能带数值表，可横向滚动" tabIndex={0}><table><caption>能带状态数值表</caption><thead><tr><th scope="col">选择</th><th scope="col">自旋</th><th scope="col">能带</th><th scope="col">k 点</th><th scope="col">坐标</th><th scope="col">能量（eV）</th></tr></thead><tbody>{visibleStates.map(state => { const point = points.get(state.kpointId); return <tr key={String(state.stateId)}><td><button type="button" className="product-secondary-action" onClick={() => emit(workspace, artifact, payload, "ELECTRONIC_BAND_STATE", { spinChannelId: state.spinChannel, bandId: state.bandId, kpointId: state.kpointId, bandStateId: state.stateId }, onSelection)}>选择</button></td><td>{electronicSpinLabel(String(state.spinChannel))}</td><td>{String(state.bandId)}</td><td>{String(point?.label || state.kpointId)}</td><td>{Array.isArray(point?.fractionalCoordinates) ? point.fractionalCoordinates.join(", ") : "—"}</td><td>{String(state.energyEv)}</td></tr>; })}</tbody></table></div>
    </details>
  </section>;
}

function DosView({ artifact, payload, workspace, onSelection }: PanelItemProps) {
  const energies = Array.isArray(payload.energiesEv) ? payload.energiesEv : [], points = Array.isArray(payload.energyPointIds) ? payload.energyPointIds : [], channels = [...records(payload.totalDos), ...records(payload.projections)];
  const plot = useMemo(() => electronicPlotData(payload, "dos"), [payload]);
  const totalRows = channels.length * energies.length;
  const pagination = useTablePage(totalRows);
  const visibleRows = Array.from({ length: pagination.end - pagination.start }, (_, offset) => {
    const ordinal = pagination.start + offset;
    const channel = channels[Math.floor(ordinal / energies.length)];
    const index = ordinal % energies.length;
    const values = Array.isArray(channel.values) ? channel.values : [];
    return { channel, energy: energies[index], value: values[index], index };
  });
  const unit = ({ states_per_ev: "态密度（states/eV）", states_per_ev_cell: "态密度（states/eV/cell）", states_per_ev_formula_unit: "态密度（states/eV/f.u.）", source_relative: "态密度（相对单位）" } as Record<string, string>)[String(payload.dosUnitSemantic)] || "态密度（单位未提供）";
  return <section className="electronic-result-section" aria-label="电子态密度" data-testid="electronic-dos-view">
    <header className="electronic-section-heading"><h6>电子态密度</h6><span>{energies.length.toLocaleString("zh-CN")} 个能量点</span></header>
    {records(payload.projections).length ? <p className="electronic-data-note">{payload.projectionCompleteness === "COMPLETE" ? "包含完整投影通道。" : "仅展示已提供的投影通道，不代表全部贡献。"}</p> : null}
    {plot.curves.length ? <ElectronicPlot data={plot} kind="dos" dosUnit={unit} /> : <p role="status">当前态密度结果没有可绘制的有限数值或完整坐标；原始数值仍可查看。</p>}
    <PlotNotice plot={plot} kind="dos" />
    <details className="electronic-numeric-details"><summary>态密度数值 · {totalRows.toLocaleString("zh-CN")} 条</summary>
      <TablePager label="态密度" {...pagination} />
      <div className="workspace-table-scroll" role="region" aria-label="态密度数值表，可横向滚动" tabIndex={0}><table><caption>态密度数值表</caption><thead><tr><th scope="col">选择</th><th scope="col">通道</th><th scope="col">自旋</th><th scope="col">能量（eV）</th><th scope="col">DOS</th></tr></thead><tbody>{visibleRows.map(({ channel, energy, value, index }) => <tr key={String(channel.channelIdentity) + ":" + index}><td><button type="button" className="product-secondary-action" disabled={typeof points[index] !== "string" || typeof value !== "number"} onClick={() => emit(workspace, artifact, payload, "ELECTRONIC_DOS_POINT", { spinChannelId: channel.spinChannel, dosChannelId: channel.channelId, projectionId: channel.projectionKind ? channel.channelIdentity : undefined, energyPointId: points[index] }, onSelection)}>选择</button></td><td>{String(channel.label ?? channel.channelId)}</td><td>{electronicSpinLabel(String(channel.spinChannel))}</td><td>{String(energy)}</td><td>{value === undefined ? "—" : String(value)}</td></tr>)}</tbody></table></div>
    </details>
  </section>;
}

function useTablePage(total: number) {
  const [requestedPage, setPage] = useState(1);
  const pages = Math.max(1, Math.ceil(total / MAX_TABLE_ROWS));
  const page = Math.min(requestedPage, pages);
  const start = (page - 1) * MAX_TABLE_ROWS;
  return { total, page, pages, start, end: Math.min(start + MAX_TABLE_ROWS, total), setPage };
}

function TablePager({ label, total, page, pages, start, end, setPage }: ReturnType<typeof useTablePage> & { label: string }) {
  return <div className="electronic-table-pagination" aria-label={`${label}表格分页`}>
    <span role="status">{total ? `${start + 1}–${end} / ${total} 行` : "暂无数值"}</span>
    {pages > 1 ? <div>
      <button type="button" className="product-secondary-action" disabled={page === 1} onClick={() => setPage(page - 1)}>上一页</button>
      <label>第 <input aria-label={`${label}页码`} type="number" min={1} max={pages} value={page} onChange={event => {
        const value = event.currentTarget.valueAsNumber;
        if (Number.isFinite(value)) setPage(Math.max(1, Math.min(pages, Math.trunc(value))));
      }} /> / {pages} 页</label>
      <button type="button" className="product-secondary-action" disabled={page === pages} onClick={() => setPage(page + 1)}>下一页</button>
    </div> : null}
  </div>;
}

function PlotNotice({ plot, kind }: { plot: ElectronicPlotData; kind: "band" | "dos" }) {
  const count = plot.curves.length;
  return <>{plot.invalidSeries ? <p className="electronic-data-note" role="status">{plot.invalidSeries} 条曲线的数值与坐标不匹配，未绘制；请在数值表中检查来源。</p> : null}
    {plot.totalSeries > count || plot.curves.some(curve => curve.sampled) ? <details className="electronic-preview-details"><summary>{plot.totalSeries > count ? "图中仅显示部分曲线" : "密集曲线已抽样显示"}，原始数据未修改</summary><p className="electronic-data-note">{kind === "band" ? "能带图" : "态密度图"}为有界预览：显示 {count} / {plot.totalSeries} {kind === "band" ? "条能带" : "个通道"}，每条最多 {ELECTRONIC_POINT_LIMIT.toLocaleString("zh-CN")} 个原始采样点，保留端点与区间极值。完整数值未修改。</p></details> : null}</>;
}

type PanelItemProps = Readonly<{ artifact: Artifact; payload: Payload; workspace: ScientificWorkspace; onSelection: (selection: WorkspaceSelectionContext) => void }>;
function emit(workspace: ScientificWorkspace, artifact: Artifact, payload: Payload, kind: WorkspaceSelectionKind, identity: Record<string, unknown>, onSelection: (selection: WorkspaceSelectionContext) => void) {
  const artifactId = artifactIdentity(artifact), checksum = artifactChecksum(artifact), electronicResourceId = String(payload.sourceResource.resourceId ?? "");
  if (!artifactId || !checksum || !workspace.datasetId || !workspace.datasetVersion || !electronicResourceId) return;
  let sourceScopeHash = workspace.sourceReferenceHash, datasetVersion = workspace.datasetVersion;
  if (workspace.sourceJobId === "source-view") {
    // A companion source owns its immutable scope, even when another resource
    // is the active tab. Generated results retain their shared Job scope.
    const metadata = artifact.metadata;
    if (artifact.jobId !== "source-view" || !metadata?.sourceObjectId || artifactId !== `source:${metadata.sourceObjectId}` || metadata.sourceDatasetId !== workspace.datasetId) return;
    sourceScopeHash = checksum;
    datasetVersion = typeof metadata.sourceVersionId === "string" && metadata.sourceVersionId ? metadata.sourceVersionId : checksum;
  }
  const primary = { selectionSchemaVersion: "1.0", kind, sourceScopeHash, projectId: workspace.projectId, datasetId: workspace.datasetId, datasetVersion, jobId: workspace.sourceJobId, artifactId, artifactChecksum: checksum, electronicResourceId, ...identity } as never;
  onSelection({ schemaVersion: "1.0", sourceScopeHash, primary, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
}

function compatibility(band: Payload, dos: Payload): boolean {
  const be = record(band.energy), de = record(dos.energy), bs = record(band.spin), ds = record(dos.spin);
  const bf = be?.fermiEnergyEv, df = de?.fermiEnergyEv;
  return band.sourceResource.calculationIdentity === dos.sourceResource.calculationIdentity && JSON.stringify(band.sourceResource.structureIdentity ?? null) === JSON.stringify(dos.sourceResource.structureIdentity ?? null) && be?.unit === de?.unit && be?.reference === de?.reference && bs?.mode === ds?.mode && ((bf == null && df == null) || (typeof bf === "number" && typeof df === "number" && Math.abs(bf - df) <= 1e-8));
}

function parse(artifact: Artifact): Payload | null {
  const payload = record(artifact.content ?? artifact.payload), type = payload?.artifactType;
  const expected: Record<string, string> = { "electronic.band_structure": "phase10n5.electronic_band_structure.v1", "electronic.dos": "phase10n5.electronic_dos.v1" };
  if (!payload || !boundedJson(payload) || typeof type !== "string" || expected[type] !== payload.schemaVersion || !record(payload.sourceResource) || !record(payload.tool) || !record(payload.energy) || !record(payload.spin) || !Array.isArray(payload.warnings) || !Array.isArray(payload.limitations)) return null;
  if (type === "electronic.band_structure" && (!Array.isArray(payload.kpoints) || !Array.isArray(payload.bands) || !Array.isArray(payload.states) || !record(payload.gap))) return null;
  if (type === "electronic.dos" && (!Array.isArray(payload.energiesEv) || !Array.isArray(payload.energyPointIds) || !Array.isArray(payload.totalDos) || !Array.isArray(payload.projections))) return null;
  return payload as Payload;
}
function record(value: unknown): Record<string, unknown> | null { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function records(value: unknown): Array<Record<string, unknown>> { return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => record(item) !== null) : []; }
function boundedJson(value: unknown, depth = 0): boolean {
  if (depth > 12) return false;
  if (value === null || typeof value === "string" || typeof value === "boolean") return true;
  if (typeof value === "number") return Number.isFinite(value);
  if (Array.isArray(value)) return value.length <= 500_000 && value.every((item) => boundedJson(item, depth + 1));
  if (typeof value !== "object" || Object.getPrototypeOf(value) !== Object.prototype) return false;
  const entries = Object.entries(value as Record<string, unknown>);
  return entries.length <= 1_024 && entries.every(([key, item]) => !["__proto__", "constructor", "prototype", "html", "javascript", "iframe", "url"].includes(key.toLowerCase()) && boundedJson(item, depth + 1));
}

export default ElectronicStructurePanel;
