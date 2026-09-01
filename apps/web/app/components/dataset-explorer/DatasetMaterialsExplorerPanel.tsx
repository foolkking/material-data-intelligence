"use client";

import { useMemo, useState } from "react";

import type { Artifact } from "../../lib/planner-api";
import { CompositionSpaceExplorerBody, validateCompositionSpacePayload } from "../composition-space/CompositionSpaceExplorerPanel";
import {
  artifactPayload,
  canonicalSampleKey,
  inspectMaterialIntelligenceArtifacts,
  type JsonRecord,
} from "../material-intelligence/materialIntelligenceIntegration";

type ExplorerTab = "overview" | "composition" | "composition_space" | "structures" | "properties" | "model" | "quality" | "comparison" | "samples";

const TABS: readonly { id: ExplorerTab; label: string }[] = [
  { id: "overview", label: "概览" },
  { id: "composition", label: "组成" },
  { id: "structures", label: "结构" },
  { id: "properties", label: "性质" },
  { id: "model", label: "模型评估" },
  { id: "quality", label: "数据质量" },
  { id: "comparison", label: "比较" },
  { id: "samples", label: "样本" },
];

const MAX_ROWS = 200;
const MAX_ELEMENTS = 256;
const MAX_PROPERTIES = 64;
const MAX_STRUCTURES = 256;
const MAX_COLUMNS = 512;
const MAX_WARNINGS = 128;
const MAX_HISTOGRAM_BINS = 100;

export type DatasetExplorerSampleSelection = Readonly<{ objectId: string; sampleRef: string; sampleKey: string }>;

export function DatasetMaterialsExplorerPanel({ artifacts, externalSampleKey, onSampleSelection }: { artifacts: Artifact[]; externalSampleKey?: string | null; onSampleSelection?: (selection: DatasetExplorerSampleSelection) => void }) {
  const integration = useMemo(() => inspectMaterialIntelligenceArtifacts(artifacts, (id, candidate) => {
    if (id === "dataset_explorer") {
      const result = validateDatasetExplorerPayload(candidate);
      return result.ok ? null : result.reason;
    }
    if (id === "composition_space") {
      const result = validateCompositionSpacePayload(candidate);
      return result.ok ? null : result.reason;
    }
    return null;
  }), [artifacts]);
  const artifact = integration.products.find((item) => item.id === "dataset_explorer")?.artifact;
  const payload = useMemo(() => artifactPayload(artifact), [artifact]);
  const validation = useMemo(() => validateDatasetExplorerPayload(payload), [payload]);
  const [tab, setTab] = useState<ExplorerTab>("overview");
  const [selectedProperty, setSelectedProperty] = useState("");
  const [selectedSample, setSelectedSample] = useState("");
  const tabs = integration.hasCompatibleEmbeddedCompositionSpace
    ? [...TABS.slice(0, 2), { id: "composition_space" as const, label: "组成空间" }, ...TABS.slice(2)]
    : TABS;

  if (!artifact) return null;
  if (!validation.ok) {
    return (
      <section className="panel dataset-explorer" data-testid="dataset-materials-explorer-invalid" role="status" aria-label="材料数据视图校验状态">
        <header className="panel-heading"><div><span>材料数据</span><h2>当前结果无法使用专业视图显示</h2></div><span className="badge">不可用</span></header>
        <p>结果未通过当前视图的结构校验；原始结构化内容仍可在技术详情中复核。</p>
        <details><summary>技术详情</summary><code>{validation.reason}</code><pre>{JSON.stringify(payload, null, 2)}</pre></details>
      </section>
    );
  }

  const explorer = validation.payload;
  const dataset = record(explorer.dataset);
  const overview = record(explorer.overview);
  const composition = record(explorer.composition);
  const structures = record(explorer.structures);
  const properties = records(record(explorer.properties).properties);
  const quality = record(explorer.quality);
  const comparison = record(explorer.comparison);
  const samples = records(explorer.sampleIndex).slice(0, MAX_ROWS);
  const activeProperty = properties.find((item) => text(item.column) === selectedProperty) || properties[0];
  const activeSample = samples.find((item) => canonicalSampleKey(item) === (externalSampleKey ?? selectedSample));

  return (
    <section className="panel dataset-explorer" data-testid="dataset-materials-explorer" aria-label="材料数据浏览器">
      <header className="panel-heading">
        <div><span>材料数据</span><h2>材料数据浏览器</h2></div>
        <span className="badge">{datasetTypeLabel(text(dataset.datasetType))}</span>
      </header>
      <details className="dataset-explorer-technical"><summary>技术详情</summary><dl className="mini-grid dataset-explorer-identity">
        <Field label="数据集标识" value={text(dataset.datasetId)} testId="dataset-explorer-dataset-id" />
        <Field label="语义档案标识" value={text(dataset.profileId)} />
        <Field label="语义合同" value={text(dataset.profileContractVersion)} />
        <Field label="语义校验摘要" value={compactHash(text(dataset.semanticHash))} />
      </dl></details>
      <div className="dataset-explorer-tabs" role="tablist" aria-label="材料数据视图">
        {tabs.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={tab === item.id}
            aria-controls={`dataset-explorer-${item.id}`}
            className={tab === item.id ? "active" : ""}
            onClick={() => setTab(item.id)}
          >{item.label}</button>
        ))}
      </div>
      <div id={`dataset-explorer-${tab}`} role="tabpanel" tabIndex={0} className="dataset-explorer-view">
        {tab === "overview" ? <OverviewView overview={overview} warnings={textList(explorer.warnings)} /> : null}
        {tab === "composition" ? <CompositionView composition={composition} /> : null}
        {tab === "composition_space" ? <CompositionSpaceExplorerBody artifacts={artifacts} /> : null}
        {tab === "structures" ? <StructuresView structures={structures} /> : null}
        {tab === "properties" ? (
          <PropertiesView properties={properties} active={activeProperty} onSelect={setSelectedProperty} />
        ) : null}
        {tab === "model" ? <ModelEvaluationView overview={overview} products={integration.products} /> : null}
        {tab === "quality" ? <QualityView quality={quality} /> : null}
        {tab === "comparison" ? <ComparisonView comparison={comparison} /> : null}
        {tab === "samples" ? (
          <SamplesView samples={samples} active={activeSample} onSelect={(key) => {
            setSelectedSample(key);
            const sample = samples.find((item) => canonicalSampleKey(item) === key);
            if (sample && validSampleIdentity(sample)) onSampleSelection?.({ objectId: text(sample.objectId), sampleRef: text(sample.sampleRef), sampleKey: key });
          }} />
        ) : null}
      </div>
    </section>
  );
}

function OverviewView({ overview, warnings }: { overview: JsonRecord; warnings: string[] }) {
  return <div data-testid="dataset-explorer-overview">
    <dl className="dataset-stat-grid">
      <Metric label="样本" value={numberText(overview.sampleCount)} />
      <Metric label="数据表" value={numberText(overview.tableCount)} />
      <Metric label="结构" value={numberText(overview.structureCount)} />
      <Metric label="性质" value={numberText(overview.propertyCount)} />
    </dl>
    <div className="dataset-explorer-columns">
      <ListSection title="可用分析" values={textList(overview.availableAnalyses).map(capabilityLabel)} empty="当前没有已声明的可执行分析。" />
      <ListSection title="当前不可用" values={textList(overview.unavailableAnalyses).map(capabilityLabel)} empty="没有不可用的分析。" />
    </div>
    <ListSection title="数据提示" values={warnings.map(warningLabel)} empty="没有需要提示的数据问题。" />
  </div>;
}

function CompositionView({ composition }: { composition: JsonRecord }) {
  const elements = records(composition.elements).slice(0, MAX_ELEMENTS);
  const systems = records(composition.chemicalSystems).slice(0, MAX_ROWS);
  const maxCount = Math.max(1, ...elements.map((item) => number(item.materialsContainingElement)));
  return <div data-testid="dataset-explorer-composition">
    <dl className="mini-grid">
      <Field label="状态" value={statusLabel(text(composition.status))} />
      <Field label="化学式字段" value={text(composition.formulaColumn)} />
      <Field label="唯一化学式" value={numberText(composition.uniqueFormulaCount)} />
      <Field label="唯一最简式" value={numberText(composition.uniqueReducedFormulaCount)} />
    </dl>
    <h3>元素覆盖</h3>
    {!elements.length ? <p className="empty-state">当前数据没有可用的化学式语义。</p> : (
      <div className="dataset-bar-list" data-testid="dataset-element-bars">
        {elements.map((item) => <BarRow key={text(item.element)} label={text(item.element)} value={number(item.materialsContainingElement)} max={maxCount} />)}
      </div>
    )}
    <h3>化学体系</h3>
    <DataTable columns={["化学体系", "数量"]} rows={systems.map((item) => [text(item.chemicalSystem), numberText(item.count)])} empty="没有可展示的化学体系。" />
  </div>;
}

function StructuresView({ structures }: { structures: JsonRecord }) {
  const rows = records(structures.records).slice(0, MAX_ROWS);
  return <div data-testid="dataset-explorer-structures">
    <dl className="mini-grid"><Field label="状态" value={statusLabel(text(structures.status))} /><Field label="结构" value={numberText(structures.structureCount)} /></dl>
    <DataTable
      columns={["来源对象", "化学式", "位点", "体积 (Å³)", "密度 (g/cm³)", "空间群", "晶系"]}
      rows={rows.map((item) => [text(item.objectId), text(item.formula), numberText(item.siteCount), format(item.volumeAngstrom3), format(item.densityGramCm3), text(item.spacegroup), text(item.crystalSystem)])}
      empty="当前数据没有绑定可展示的标准结构。"
    />
    <p className="dataset-method-note">对称性来自固定的结构适配策略；结构重复判断基于标准化对象的一致性。</p>
  </div>;
}

function PropertiesView({ properties, active, onSelect }: { properties: JsonRecord[]; active?: JsonRecord; onSelect: (value: string) => void }) {
  const histogram = record(active?.histogram);
  const counts = numberList(histogram.counts);
  const maxCount = Math.max(1, ...counts);
  return <div data-testid="dataset-explorer-properties">
    {!properties.length ? <p className="empty-state">当前数据没有可展示的材料性质字段。</p> : <>
      <label className="dataset-property-select">性质
        <select value={text(active?.column)} onChange={(event) => onSelect(event.target.value)}>
          {properties.map((item) => <option key={text(item.column)} value={text(item.column)}>{text(item.column)}{text(item.unit) ? ` (${text(item.unit)})` : ""}</option>)}
        </select>
      </label>
      <dl className="mini-grid">
        <Field label="数量" value={numberText(active?.count)} />
        <Field label="缺失" value={numberText(active?.missingCount)} />
        <Field label="非有限值" value={numberText(active?.nonFiniteCount)} />
        <Field label="单位" value={text(active?.unit) || "未声明"} />
      </dl>
      <Statistics statistics={record(active?.statistics)} />
      <div className="dataset-histogram" data-testid="dataset-property-histogram" aria-label={`${text(active?.column)} histogram`}>
        {counts.map((value, index) => <span key={index} style={{ height: `${Math.max(3, value / maxCount * 100)}%` }} title={`${value}`} />)}
      </div>
      <p className="dataset-method-note">异常候选使用 1.5 IQR 规则，仅表示统计候选，不等同于科学异常结论。</p>
    </>}
  </div>;
}

function ModelEvaluationView({ overview, products }: { overview: JsonRecord; products: readonly { id: string; label: string; state: string; reason: string }[] }) {
  const capabilities = ["regression_evaluation", "uncertainty_evaluation", "classification_evaluation"];
  const available = textList(overview.availableAnalyses).filter((item) => capabilities.includes(item));
  const unavailable = textList(overview.unavailableAnalyses).filter((item) => capabilities.includes(item));
  const actual = products.filter((item) => ["regression", "uncertainty", "classification"].includes(item.id));
  return <div data-testid="dataset-explorer-model-evaluation">
    {!available.length ? <p className="empty-state">当前数据没有检测到模型结果语义。</p> : <>
      <h3>可用的模型评估</h3>
      <ul>{available.map((item) => <li key={item}>{capabilityLabel(item)}</li>)}</ul>
      <p className="dataset-method-note">只有通过数据与语义档案绑定校验的稳定材料样本才会展示模型诊断。</p>
    </>}
    {unavailable.length ? <><h3>当前数据不可用</h3><ul>{unavailable.map((item) => <li key={item}>{capabilityLabel(item)}</li>)}</ul></> : null}
    <h3>结果生成状态</h3>
    <ul className="material-product-state-list">{actual.map((item) => <li key={item.id}><strong>{item.label}</strong><span className="badge">{statusLabel(item.state)}</span>{item.state !== "PRODUCED" ? <details><summary>技术详情</summary><code>{item.reason}</code></details> : null}</li>)}</ul>
  </div>;
}

function QualityView({ quality }: { quality: JsonRecord }) {
  const columnIssues = records(quality.columnIssues).slice(0, MAX_ROWS);
  const duplicates = records(quality.duplicateSampleIdentityValues).slice(0, MAX_ROWS);
  return <div data-testid="dataset-explorer-quality">
    <dl className="mini-grid">
      <Field label="无效化学式" value={numberText(quality.invalidFormulaCount)} />
      <Field label="可追溯样本" value={numberText(quality.sampleLinksMaterialized)} />
      <Field label="近重复分析" value={statusLabel(text(quality.nearDuplicateAnalysis))} />
    </dl>
    <h3>字段问题</h3>
    <DataTable columns={["字段", "缺失", "非有限值", "歧义"]} rows={columnIssues.map((item) => [text(item.column), numberText(item.missingCount), numberText(item.nonFiniteCount), textList(item.ambiguities).join(", ") || "无"])} empty="没有字段问题。" />
    <h3>重复标识值</h3>
    <DataTable columns={["字段", "值", "数量"]} rows={duplicates.map((item) => [text(item.column), text(item.value), numberText(item.count)])} empty="没有重复的显式标识值。" />
  </div>;
}

function ComparisonView({ comparison }: { comparison: JsonRecord }) {
  if (text(comparison.status) !== "READY") return <div data-testid="dataset-explorer-comparison"><p className="empty-state">当前没有请求数据集比较。</p></div>;
  const overlap = record(comparison.elementOverlap);
  const rows = records(comparison.propertyComparison).slice(0, MAX_PROPERTIES);
  return <div data-testid="dataset-explorer-comparison">
    <dl className="mini-grid"><Field label="比较方式" value={text(comparison.mode)} /><details><summary>技术详情</summary><Field label="数据绑定" value={JSON.stringify(comparison.binding || {})} /></details></dl>
    <div className="dataset-explorer-columns">
      <ListSection title="共有元素" values={textList(overlap.shared)} empty="无" />
      <ListSection title="仅左侧" values={textList(overlap.leftOnly)} empty="无" />
      <ListSection title="仅右侧" values={textList(overlap.rightOnly)} empty="无" />
    </div>
    <DataTable columns={["性质", "单位", "可比较", "左侧中位数", "右侧中位数"]} rows={rows.map((item) => [text(item.column), text(item.unit) || "-", Boolean(item.comparable) ? "是" : "否", format(record(item.left).median), format(record(item.right).median)])} empty="没有可比较的材料性质。" />
    <p className="dataset-method-note">{text(comparison.semantics)}</p>
  </div>;
}

function SamplesView({ samples, active, onSelect }: { samples: JsonRecord[]; active?: JsonRecord; onSelect: (value: string) => void }) {
  return <div data-testid="dataset-explorer-samples">
    {active ? <dl className="mini-grid dataset-sample-inspector" aria-live="polite" data-testid="dataset-sample-inspector"><Field label="样本键" value={canonicalSampleKey(active)} /><Field label="样本" value={text(active.sampleRef)} /><Field label="化学式" value={text(active.formula)} /><Field label="最简式" value={text(active.reducedFormula)} /><Field label="来源" value={`${text(active.objectId)} · 第 ${numberText(active.rowIndex)} 行`} /></dl> : <p className="empty-state">选择一个稳定样本以查看其来源行。</p>}
    <div className="compact-table-wrap" role="region" aria-label="稳定样本索引，可横向滚动查看完整列" tabIndex={0}><table className="compact-table"><caption>稳定样本索引</caption><thead><tr><th>样本引用</th><th>化学式</th><th>最简式</th><th>来源对象</th><th>行</th></tr></thead><tbody>
      {samples.map((item) => <tr key={canonicalSampleKey(item)}><td><button type="button" className="link-button" aria-label={`${text(item.sampleRef)} from ${text(item.objectId) || "legacy source"}`} onClick={() => onSelect(canonicalSampleKey(item))}>{text(item.sampleRef)}</button></td><td>{text(item.formula) || "-"}</td><td>{text(item.reducedFormula) || "-"}</td><td>{text(item.objectId)}</td><td>{numberText(item.rowIndex)}</td></tr>)}
    </tbody></table></div>
  </div>;
}

function Statistics({ statistics }: { statistics: JsonRecord }) {
  return <dl className="dataset-stat-grid">
    {(["min", "q1", "median", "q3", "max", "mean", "std"] as const).map((key) => <Metric key={key} label={key.toUpperCase()} value={format(statistics[key])} />)}
  </dl>;
}

function Metric({ label, value }: { label: string; value: string }) { return <div><dt>{label}</dt><dd>{value}</dd></div>; }
function Field({ label, value, testId }: { label: string; value: string; testId?: string }) { return <div data-testid={testId}><dt>{label}</dt><dd>{value || "-"}</dd></div>; }
function ListSection({ title, values, empty }: { title: string; values: string[]; empty: string }) { return <section><h3>{title}</h3>{values.length ? <ul>{values.map((value) => <li key={value}>{value}</li>)}</ul> : <p className="empty-state">{empty}</p>}</section>; }
function BarRow({ label, value, max }: { label: string; value: number; max: number }) { return <div><strong>{label}</strong><span><i style={{ width: `${value / max * 100}%` }} /></span><small>{value}</small></div>; }

function DataTable({ columns, rows, empty }: { columns: string[]; rows: string[][]; empty: string }) {
  if (!rows.length) return <p className="empty-state">{empty}</p>;
  return <div className="compact-table-wrap" role="region" aria-label="科学数据表，可横向滚动查看完整列" tabIndex={0}><table className="compact-table"><thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={index}>{row.map((value, column) => <td key={column}>{value || "-"}</td>)}</tr>)}</tbody></table></div>;
}

export function validateDatasetExplorerPayload(payload: JsonRecord | null): { ok: true; payload: JsonRecord } | { ok: false; reason: string } {
  if (!payload || payload.schemaVersion !== "phase10k2.dataset_materials_explorer.v1") return { ok: false, reason: "DATASET_EXPLORER_SCHEMA_UNSUPPORTED" };
  if (!record(payload.dataset).profileId || !["2.0", "2.1"].includes(String(record(payload.dataset).profileContractVersion))) return { ok: false, reason: "DATASET_EXPLORER_PROFILE_BINDING_INVALID" };
  const composition = record(payload.composition);
  const structures = record(payload.structures);
  const properties = records(record(payload.properties).properties);
  const quality = record(payload.quality);
  const comparison = record(payload.comparison);
  const overCap = records(composition.elements).length > MAX_ELEMENTS
    || records(composition.chemicalSystems).length > MAX_ROWS
    || records(composition.duplicateReducedFormulaGroups).length > MAX_ROWS
    || records(structures.records).length > MAX_STRUCTURES
    || properties.length > MAX_PROPERTIES
    || properties.some((item) => numberList(record(item.histogram).counts).length > MAX_HISTOGRAM_BINS)
    || records(quality.columnIssues).length > MAX_COLUMNS
    || records(quality.duplicateSampleIdentityValues).length > MAX_ROWS
    || records(comparison.propertyComparison).length > MAX_PROPERTIES
    || records(payload.sampleIndex).length > MAX_ROWS
    || textList(payload.warnings).length > MAX_WARNINGS;
  if (overCap) return { ok: false, reason: "DATASET_EXPLORER_PREVIEW_CAP_EXCEEDED" };
  const samples = records(payload.sampleIndex);
  const sampleKeys = samples.map((item) => text(item.sampleKey));
  if (samples.some((item) => !validSampleIdentity(item)) || new Set(sampleKeys).size !== sampleKeys.length) {
    return { ok: false, reason: "DATASET_EXPLORER_SAMPLE_IDENTITY_INVALID" };
  }
  return { ok: true, payload };
}

function validSampleIdentity(value: JsonRecord): boolean {
  const objectId = text(value.objectId);
  const sampleRef = text(value.sampleRef);
  return Boolean(objectId && sampleRef && value.sampleKey === `${objectId}:${sampleRef}` && Number.isSafeInteger(value.rowIndex) && Number(value.rowIndex) >= 0);
}

function isRecord(value: unknown): value is JsonRecord { return Boolean(value && typeof value === "object" && !Array.isArray(value)); }
function record(value: unknown): JsonRecord { return isRecord(value) ? value : {}; }
function records(value: unknown): JsonRecord[] { return Array.isArray(value) ? value.filter(isRecord) : []; }
function text(value: unknown): string { return typeof value === "string" || typeof value === "number" ? String(value) : ""; }
function textList(value: unknown): string[] { return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : []; }
function number(value: unknown): number { const result = Number(value); return Number.isFinite(result) ? result : 0; }
function numberList(value: unknown): number[] { return Array.isArray(value) ? value.map(number) : []; }
function numberText(value: unknown): string { const result = Number(value); return Number.isFinite(result) ? String(result) : "0"; }
function format(value: unknown): string { const result = Number(value); return Number.isFinite(result) ? result.toLocaleString(undefined, { maximumFractionDigits: 5 }) : "-"; }
function compactHash(value: string): string { return value.length > 20 ? `${value.slice(0, 12)}...${value.slice(-6)}` : value; }
function datasetTypeLabel(value: string): string { return ({ mixed_material_dataset: "混合材料数据", materials_dataset: "材料数据" } as Record<string, string>)[value] || "材料数据"; }
function statusLabel(value: string): string { return ({ READY: "可用", PRODUCED: "已生成", UNAVAILABLE: "不可用", NOT_IMPLEMENTED_BY_DESIGN: "当前未提供", NOT_REQUESTED: "未请求", REJECTED: "已拒绝" } as Record<string, string>)[value] || value; }
function capabilityLabel(value: string): string { return ({ dataset_materials_explorer: "材料数据浏览", table_distribution: "数据分布", scatter: "散点关系", histogram: "直方分布", correlation: "相关分析", composition_summary: "组成概览", formula_statistics: "化学式统计", element_distribution: "元素分布", chemical_system_visualization: "化学体系可视化", composition_space: "组成空间", structure_summary: "结构概览", trajectory_visualization: "轨迹可视化", phonon_visualization: "声子可视化", volumetric_visualization: "体数据可视化", regression_evaluation: "回归评估", uncertainty_evaluation: "不确定性评估", classification_evaluation: "分类评估", dataset_structure_statistics: "数据结构统计" } as Record<string, string>)[value] || value.replaceAll("_", " "); }
function warningLabel(value: string): string { return ({ FORMULA_VALUES_PARTIALLY_INVALID: "部分化学式无法解析，相关统计已限定在可用样本内。" } as Record<string, string>)[value] || "数据包含需要复核的限定信息。"; }
