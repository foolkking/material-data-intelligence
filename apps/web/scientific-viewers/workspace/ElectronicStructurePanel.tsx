"use client";

import type { Artifact } from "../../app/lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext, WorkspaceSelectionKind } from "../../app/lib/workspace-api";
import { artifactChecksum, artifactIdentity } from "../../shared/workspace/workspace-renderer-registry";

type Payload = Record<string, unknown> & { artifactType: "electronic.band_structure" | "electronic.dos"; schemaVersion: string; sourceResource: Record<string, unknown>; warnings: string[]; limitations: string[] };
const MAX_PLOT_POINTS = 2_400;
const MAX_BAND_PLOT_SERIES = 48;
const MAX_DOS_PLOT_CHANNELS = 24;
const MAX_TABLE_ROWS = 500;

export function ElectronicStructurePanel({ artifacts, selected, workspace, onSelection }: Readonly<{ artifacts: Artifact[]; selected: Artifact; workspace: ScientificWorkspace; onSelection: (selection: WorkspaceSelectionContext) => void }>) {
  const current = parse(selected);
  if (!current) return <section className="workspace-generic-renderer" role="alert"><h5>电子结构结果不可用</h5><p>N5_ELECTRONIC_CONTRACT_INVALID</p></section>;
  const parsed = artifacts.map((artifact) => ({ artifact, payload: parse(artifact) })).filter((item): item is { artifact: Artifact; payload: Payload } => item.payload !== null);
  const band = parsed.find((item) => item.payload.artifactType === "electronic.band_structure") ?? (current.artifactType === "electronic.band_structure" ? { artifact: selected, payload: current } : null);
  const dos = parsed.find((item) => item.payload.artifactType === "electronic.dos") ?? (current.artifactType === "electronic.dos" ? { artifact: selected, payload: current } : null);
  const compatible = band && dos ? compatibility(band.payload, dos.payload) : null;
  return <section className="workspace-generic-renderer" aria-label="电子结构" data-testid="electronic-structure-panel">
    <header><h5>电子结构</h5><p>基于已保存供应方输出的分析结果。平台不会执行 DFT 或 GW 计算。</p></header>
    {band ? <BandView artifact={band.artifact} payload={band.payload} workspace={workspace} onSelection={onSelection} /> : <p role="status">能带结构结果不可用。</p>}
    {dos ? <DosView artifact={dos.artifact} payload={dos.payload} workspace={workspace} onSelection={onSelection} /> : <p role="status">态密度结果不可用。</p>}
    <section aria-label="能带与态密度组合一致性" data-testid="electronic-combined-status">
      <h6>能带 + 态密度</h6>
      <p role="status">{compatible === null ? "组合视图需要同时存在已保存的能带和态密度结果。" : compatible ? "数据源、能量参考、费米能级和自旋语义完全兼容。" : "DO_NOT_COMBINE：电子结构来源语义不兼容。"}</p>
    </section>
    <h6>检查器来源</h6>
    <dl><dt>工具</dt><dd>{String(record(current.tool)?.toolId)}@{String(record(current.tool)?.toolVersion)}</dd><dt>资源</dt><dd><code>{String(current.sourceResource.resourceHash)}</code></dd><dt>计算</dt><dd>{String(current.sourceResource.calculationIdentity)}</dd><dt>契约</dt><dd>{current.schemaVersion}</dd></dl>
    {current.warnings.length > 0 && <p role="status">警告：{current.warnings.join(", ")}</p>}
    <ul>{current.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
  </section>;
}

function BandView({ artifact, payload, workspace, onSelection }: PanelItemProps) {
  const gap = record(payload.gap), bands = records(payload.bands), kpoints = records(payload.kpoints), states = records(payload.states);
  const plotBands = bands.slice(0, MAX_BAND_PLOT_SERIES).map((band) => boundedNumbers(band.energiesEv));
  const plotDomain = numericDomain(plotBands);
  const hasPlotData = plotBands.some((values) => values.length > 0);
  const visibleStates = states.slice(0, MAX_TABLE_ROWS);
  return <section aria-label="电子能带结构" data-testid="electronic-band-view"><h6>电子能带</h6>
    <p><strong>采样带隙：</strong> {gap?.valueEv === null || gap?.valueEv === undefined ? "不可用" : `${String(gap.valueEv)} eV`} · {String(gap?.directness)} · {String(gap?.classification)} <button type="button" onClick={() => emit(workspace, artifact, payload, "ELECTRONIC_BAND_GAP", {}, onSelection)}>选择带隙</button></p>
    {hasPlotData ? <svg viewBox="0 0 640 220" role="img" aria-label="供应方能带曲线；数值可在表格中查看" data-testid="electronic-band-plot"><title>供应方能带曲线（有界显示）</title>{plotBands.map((values, index) => <polyline key={String(bands[index].bandIdentity)} fill="none" stroke={String(bands[index].spinChannel) === "down" ? "#b42318" : "#176b87"} strokeDasharray={String(bands[index].spinChannel) === "down" ? "6 4" : undefined} strokeWidth="2" points={polyline(values, plotDomain)} />)}</svg> : <p role="status">当前能带结果没有可绘制的有限数值；完整原始表仍可供检查。</p>}
    {bands.length > plotBands.length || plotBands.some((values, index) => numbers(bands[index].energiesEv).length > values.length) ? <p className="notice" role="status">能带图为有界预览：显示 {plotBands.length} / {bands.length} 条能带，每条最多 {MAX_PLOT_POINTS.toLocaleString("zh-CN")} 个显示采样点；完整供应方结果未被修改。</p> : null}
    <p className="notice" role="status">能带状态表显示 {visibleStates.length} / {states.length} 行；完整状态仍保留在权威结果中。</p>
    <div className="workspace-table-scroll"><table><caption>能带状态数值表</caption><thead><tr><th scope="col">选择</th><th scope="col">自旋</th><th scope="col">能带</th><th scope="col">k 点</th><th scope="col">坐标</th><th scope="col">能量（eV）</th></tr></thead><tbody>{visibleStates.map((state) => { const point = kpoints.find((item) => item.kpointId === state.kpointId); return <tr key={String(state.stateId)}><td><button type="button" onClick={() => emit(workspace, artifact, payload, "ELECTRONIC_BAND_STATE", { spinChannelId: state.spinChannel, bandId: state.bandId, kpointId: state.kpointId, bandStateId: state.stateId }, onSelection)}>选择</button></td><td>{String(state.spinChannel)}</td><td>{String(state.bandId)}</td><td>{String(state.kpointId)}</td><td>{Array.isArray(point?.fractionalCoordinates) ? point.fractionalCoordinates.join(", ") : ""}</td><td>{String(state.energyEv)}</td></tr>; })}</tbody></table></div>
  </section>;
}

function DosView({ artifact, payload, workspace, onSelection }: PanelItemProps) {
  const energies = numbers(payload.energiesEv), points = strings(payload.energyPointIds), total = records(payload.totalDos), projections = records(payload.projections), channels = [...total, ...projections];
  const plotChannels = channels.slice(0, MAX_DOS_PLOT_CHANNELS).map((channel) => boundedNumbers(channel.values));
  const plotDomain = numericDomain(plotChannels);
  const hasPlotData = plotChannels.some((values) => values.length > 0);
  const allRows = channels.flatMap((channel) => energies.map((energy, index) => ({ channel, energy, index })));
  const visibleRows = allRows.slice(0, MAX_TABLE_ROWS);
  return <section aria-label="电子态密度" data-testid="electronic-dos-view"><h6>电子态密度（DOS）</h6><p><strong>投影覆盖：</strong> {String(payload.projectionCompleteness)} · <strong>单位：</strong> {String(payload.dosUnitSemantic)}</p>
    {hasPlotData ? <svg viewBox="0 0 640 220" role="img" aria-label="供应方态密度通道；数值可在表格中查看" data-testid="electronic-dos-plot"><title>供应方电子态密度（有界显示）</title>{plotChannels.map((values, index) => <polyline key={String(channels[index].channelIdentity)} fill="none" stroke={String(channels[index].spinChannel) === "down" ? "#b42318" : index === 0 ? "#176b87" : "#627d32"} strokeDasharray={String(channels[index].spinChannel) === "down" ? "6 4" : undefined} strokeWidth="2" points={polyline(values, plotDomain)} />)}</svg> : <p role="status">当前 DOS 结果没有可绘制的有限数值；完整原始表仍可供检查。</p>}
    {channels.length > plotChannels.length || plotChannels.some((values, index) => numbers(channels[index].values).length > values.length) ? <p className="notice" role="status">DOS 图为有界预览：显示 {plotChannels.length} / {channels.length} 个通道，每个通道最多 {MAX_PLOT_POINTS.toLocaleString("zh-CN")} 个显示采样点；完整供应方结果未被修改。</p> : null}
    <p className="notice" role="status">态密度表显示 {visibleRows.length} / {allRows.length} 个通道-能量数值；完整数值仍保留在权威结果中。</p>
    <div className="workspace-table-scroll"><table><caption>态密度数值表</caption><thead><tr><th scope="col">选择</th><th scope="col">通道</th><th scope="col">自旋</th><th scope="col">能量（eV）</th><th scope="col">DOS</th></tr></thead><tbody>{visibleRows.map(({ channel, energy, index }) => <tr key={`${String(channel.channelIdentity)}:${points[index]}`}><td><button type="button" onClick={() => emit(workspace, artifact, payload, "ELECTRONIC_DOS_POINT", { spinChannelId: channel.spinChannel, dosChannelId: channel.channelId, projectionId: channel.projectionKind ? channel.channelIdentity : undefined, energyPointId: points[index] }, onSelection)}>选择</button></td><td>{String(channel.label ?? channel.channelId)}</td><td>{String(channel.spinChannel)}</td><td>{energy}</td><td>{numbers(channel.values)[index]}</td></tr>)}</tbody></table></div>
  </section>;
}

type PanelItemProps = Readonly<{ artifact: Artifact; payload: Payload; workspace: ScientificWorkspace; onSelection: (selection: WorkspaceSelectionContext) => void }>;
function emit(workspace: ScientificWorkspace, artifact: Artifact, payload: Payload, kind: WorkspaceSelectionKind, identity: Record<string, unknown>, onSelection: (selection: WorkspaceSelectionContext) => void) {
  const artifactId = artifactIdentity(artifact), checksum = artifactChecksum(artifact), electronicResourceId = String(payload.sourceResource.resourceId ?? "");
  if (!artifactId || !checksum || !workspace.datasetId || !workspace.datasetVersion || !electronicResourceId) return;
  const primary = { selectionSchemaVersion: "1.0", kind, sourceScopeHash: workspace.sourceReferenceHash, projectId: workspace.projectId, datasetId: workspace.datasetId, datasetVersion: workspace.datasetVersion, jobId: workspace.sourceJobId, artifactId, artifactChecksum: checksum, electronicResourceId, ...identity } as never;
  onSelection({ schemaVersion: "1.0", sourceScopeHash: workspace.sourceReferenceHash, primary, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
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
function polyline(values: number[], domain: readonly [number, number]): string { const [min, max] = domain, range = max - min || 1; return values.map((value, index) => `${20 + index * (600 / Math.max(1, values.length - 1))},${200 - ((value - min) / range) * 180}`).join(" "); }
function record(value: unknown): Record<string, unknown> | null { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function records(value: unknown): Array<Record<string, unknown>> { return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => record(item) !== null) : []; }
function numbers(value: unknown): number[] { return Array.isArray(value) ? value.filter((item): item is number => typeof item === "number" && Number.isFinite(item)) : []; }
function boundedNumbers(value: unknown): number[] {
  const values = numbers(value);
  if (values.length <= MAX_PLOT_POINTS) return values;
  return Array.from({ length: MAX_PLOT_POINTS }, (_, index) => values[Math.round(index * (values.length - 1) / (MAX_PLOT_POINTS - 1))]);
}
function numericDomain(series: readonly number[][]): [number, number] {
  let min = 0, max = 1;
  for (const values of series) for (const value of values) {
    if (value < min) min = value;
    if (value > max) max = value;
  }
  return [min, max];
}
function strings(value: unknown): string[] { return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : []; }
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
