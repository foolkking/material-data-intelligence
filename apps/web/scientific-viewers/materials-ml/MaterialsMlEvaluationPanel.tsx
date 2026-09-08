"use client";

import { useMemo, useState, type ReactNode } from "react";

import type { Artifact } from "../../app/lib/planner-api";
import {
  artifactPayload,
  canonicalSampleKey,
  inspectMaterialIntelligenceArtifacts,
  type JsonRecord,
  type MaterialIntelligenceProductId,
} from "../material-intelligence/materialIntelligenceIntegration";

type ProductKind = "regression" | "uncertainty" | "classification";

const PRODUCTS: readonly { id: MaterialIntelligenceProductId; name: string; schema: string; kind: ProductKind; label: string; code: string }[] = [
  { id: "regression", name: "materials_ml_regression.json", schema: "phase10k3.materials_ml_regression.v1", kind: "regression", label: "回归评估", code: "Regression" },
  { id: "uncertainty", name: "materials_ml_uncertainty.json", schema: "phase10k3.materials_ml_uncertainty.v1", kind: "uncertainty", label: "不确定性评估", code: "Uncertainty" },
  { id: "classification", name: "materials_ml_classification.json", schema: "phase10k3.materials_ml_classification.v1", kind: "classification", label: "分类评估", code: "Classification" },
];

const CAPS = { evaluations: 32, points: 10_000, rows: 200, groups: 256, histogramBins: 100, classes: 64, curvePoints: 5_000 };

export function MaterialsMlEvaluationPanel({ artifacts }: { artifacts: Artifact[] }) {
  const integration = useMemo(() => inspectMaterialIntelligenceArtifacts(artifacts, (id, payload) => {
    const product = PRODUCTS.find((item) => item.id === id);
    if (!product) return null;
    const result = validateMaterialsMlPayload(payload, product);
    return result.ok ? null : result.reason;
  }), [artifacts]);
  const available = useMemo(
    () => PRODUCTS.flatMap((product) => {
      const assessment = integration.products.find((item) => item.id === product.id);
      const artifact = assessment?.artifact;
      if (!artifact) return [];
      const payload = artifactPayload(artifact);
      const local = validateMaterialsMlPayload(payload, product);
      const validation = assessment?.state === "PRODUCED"
        ? local
        : { ok: false as const, reason: assessment?.reason || (local.ok ? "MATERIALS_ML_INTEGRATION_INVALID" : local.reason) };
      return [{ product, artifact, payload, validation, state: assessment?.state || "REJECTED" }];
    }),
    [artifacts, integration],
  );
  const [selectedName, setSelectedName] = useState("");
  const active = available.find((item) => item.product.name === selectedName)
    || available.find((item) => item.validation.ok)
    || available[0];
  const validation = active?.validation || null;
  const [selectedTask, setSelectedTask] = useState("");

  if (!active) return null;
  if (!validation?.ok) {
    return <section className="panel materials-ml" data-testid="materials-ml-invalid" role="status" aria-label="Materials ML validation status">
      <header className="panel-heading"><div><span>Profile 2.0 产品</span><h2>材料模型评估暂时不可用</h2></div><span className="badge">未通过校验</span></header>
      {available.length > 1 ? <div className="materials-ml-selectors"><label>产品<select value={active.product.name} onChange={(event) => { setSelectedName(event.target.value); setSelectedTask(""); }}>{available.map((item) => <option key={item.product.name} value={item.product.name}>{item.product.label}（{item.state}）</option>)}</select></label></div> : null}
      <p>结果在产品渲染前未通过校验；结构化数据仍可查看。</p>
      <code>{validation?.reason || "MATERIALS_ML_ARTIFACT_INVALID"}</code>
      <details><summary>结构化数据</summary><pre>{JSON.stringify(active.payload, null, 2)}</pre></details>
    </section>;
  }

  const payload = validation.payload;
  const evaluations = records(payload.evaluations);
  const evaluation = evaluations.find((item) => text(item.taskId) === selectedTask) || evaluations[0];
  const dataset = record(payload.dataset);
    return <section className="panel materials-ml" data-testid="materials-ml-evaluation" aria-label="材料模型评估">
    <header className="panel-heading">
      <div><span>确定性材料模型诊断</span><h2>材料属性模型评估</h2></div>
      <span className="badge" title={active.product.code} data-semantic-code={active.product.code}>{active.product.label}</span>
    </header>
    <dl className="mini-grid materials-ml-identity">
      <Field label="数据集" value={text(dataset.datasetId)} />
      <Field label="数据画像" value={text(dataset.profileId)} />
      <Field label="语义契约" value={text(dataset.profileContractVersion)} />
      <Field label="残差定义" value={active.product.kind === "regression" ? text(payload.residualConvention) : "不适用"} />
    </dl>
    <div className="materials-ml-selectors">
      {available.length > 1 ? <label>产品<select value={active.product.name} onChange={(event) => { setSelectedName(event.target.value); setSelectedTask(""); }}>{available.map((item) => <option key={item.product.name} value={item.product.name}>{item.product.label}（{item.state}）</option>)}</select></label> : null}
      {evaluations.length > 1 ? <label>任务 / 模型<select value={text(evaluation?.taskId)} onChange={(event) => setSelectedTask(event.target.value)}>{evaluations.map((item) => <option key={text(item.taskId)} value={text(item.taskId)}>{text(item.taskId)}</option>)}</select></label> : null}
    </div>
    {!evaluation ? <p className="empty-state">暂无可用的有界评估结果。</p> : null}
    {evaluation && active.product.kind === "regression" ? <RegressionView evaluation={evaluation} comparisons={records(payload.modelComparisons)} /> : null}
    {evaluation && active.product.kind === "uncertainty" ? <UncertaintyView evaluation={evaluation} /> : null}
    {evaluation && active.product.kind === "classification" ? <ClassificationView evaluation={evaluation} /> : null}
    <p className="dataset-method-note">性能诊断仅描述所提供的结果数据集，不代表材料有效性、因果模型质量或科学真值。</p>
  </section>;
}

function RegressionView({ evaluation, comparisons }: { evaluation: JsonRecord; comparisons: JsonRecord[] }) {
  const metrics = record(evaluation.metrics);
  const coverage = record(evaluation.coverage);
  const points = records(evaluation.parityPoints);
  const chemistry = record(evaluation.chemistryConditioned);
  const histogram = record(evaluation.residualHistogram);
  const counts = numberList(histogram.counts);
  const highError = records(evaluation.highErrorSamples);
  return <div className="materials-ml-view" data-testid="materials-ml-regression">
      <MetricGrid items={[
      ["MAE", format(metrics.mae)], ["RMSE", format(metrics.rmse)], ["R²", metrics.r2 === null ? "未定义" : format(metrics.r2)],
      ["平均误差", format(metrics.meanSignedError)], ["已评估", `${integer(coverage.evaluatedSamples)} / ${integer(coverage.totalSamples)}`], ["单位", text(evaluation.unit) || "未提供"],
    ]} />
    <div className="materials-ml-charts">
      <ChartFrame title="预测值与真实值" note="横轴为真实值，纵轴为预测值；虚线表示 y=x。"><ScatterChart points={points} x="target" y="prediction" reference /></ChartFrame>
      <ChartFrame title="残差与目标属性" note="残差 = 预测值 − 真实值；点来自同一组有界样本。"><ScatterChart points={points} x="target" y="residual" /></ChartFrame>
      <ChartFrame title="残差分布" note="残差 = 预测值 − 真实值。"><Histogram counts={counts} /></ChartFrame>
    </div>
    <h3>预测误差最大的样本</h3>
    <DataTable columns={["样本键", "样本", "化学式", "化学体系", "真实值", "预测值", "残差", "绝对误差", "不确定性"]} rows={highError.map((row) => [canonicalSampleKey(row), text(row.sampleRef), text(row.formula), text(row.chemicalSystem), format(row.target), format(row.prediction), format(row.residual), format(row.absoluteError), format(row.uncertainty)])} rowKeys={highError.map(canonicalSampleKey)} empty="暂无对齐的高误差样本。" testId="materials-ml-high-error-table" />
    <div className="materials-ml-columns">
      <section><h3>按元素统计误差</h3><p className="dataset-method-note">元素分组可以重叠，同一材料可能出现在多行。</p><GroupTable rows={records(chemistry.byElement)} /></section>
      <section><h3>按化学体系统计误差</h3><p className="dataset-method-note">样本数较少的分组仍保留，并明确显示样本数。</p><GroupTable rows={records(chemistry.byChemicalSystem)} /></section>
    </div>
    {comparisons.length ? <><h3>模型比较</h3><DataTable columns={["目标属性", "共同样本", "策略", "模型"]} rows={comparisons.map((item) => [text(item.targetColumn), integer(item.commonSampleCount), text(item.policy), records(item.models).map((model) => text(model.seriesId)).join(", ")])} empty="暂无多模型比较结果。" testId="materials-ml-model-comparison" /></> : null}
    <Warnings values={textList(evaluation.warnings)} />
  </div>;
}

function UncertaintyView({ evaluation }: { evaluation: JsonRecord }) {
  const coverage = record(evaluation.coverage);
  const association = record(evaluation.association);
  const reliability = record(evaluation.reliability);
  const errorDecay = record(evaluation.errorDecay);
  const points = records(evaluation.uncertaintyErrorPoints);
  return <div className="materials-ml-view" data-testid="materials-ml-uncertainty">
    <MetricGrid items={[["Pearson", format(association.pearson)], ["Spearman", format(association.spearman)], ["Evaluated", `${integer(coverage.evaluatedSamples)} / ${integer(coverage.totalSamples)}`], ["Uncertainty kind", text(evaluation.uncertaintyKind)]]} />
    <div className="materials-ml-charts">
      <ChartFrame title="不确定性与绝对误差" note="每个点保留稳定的材料样本引用。"><ScatterChart points={points} x="uncertainty" y="absoluteError" /></ChartFrame>
      <ChartFrame title="误差衰减" note="优先保留不确定性最低的样本。"><LineChart points={records(errorDecay.points)} x="retainedFraction" y="mae" /></ChartFrame>
    </div>
    <h3>等样本数可靠性分箱</h3>
    <DataTable columns={["分箱", "样本数", "平均不确定性", "平均绝对误差"]} rows={records(reliability.bins).map((row) => [integer(row.bin), integer(row.sampleCount), format(row.meanUncertainty), format(row.meanAbsoluteError)])} empty="暂无可靠性分箱。" testId="materials-ml-reliability-table" />
    <h3>不确定性最高的样本</h3>
    <DataTable columns={["样本键", "样本", "化学式", "不确定性", "绝对误差"]} rows={records(evaluation.highUncertaintySamples).map((row) => [canonicalSampleKey(row), text(row.sampleRef), text(row.formula), format(row.uncertainty), format(row.absoluteError)])} rowKeys={records(evaluation.highUncertaintySamples).map(canonicalSampleKey)} empty="暂无匹配的不确定性样本。" testId="materials-ml-high-uncertainty-table" />
    <Warnings values={textList(evaluation.warnings)} />
  </div>;
}

function ClassificationView({ evaluation }: { evaluation: JsonRecord }) {
  const metrics = record(evaluation.metrics);
  const confusion = record(metrics.confusionMatrix);
  const labels = textList(confusion.labels);
  const matrix = Array.isArray(confusion.values) ? confusion.values : [];
  const curves = record(evaluation.curves);
  return <div className="materials-ml-view" data-testid="materials-ml-classification">
    <MetricGrid items={[["Accuracy", format(metrics.accuracy)], ["Macro precision", format(metrics.macroPrecision)], ["Macro recall", format(metrics.macroRecall)], ["Macro F1", format(metrics.macroF1)], ["Evaluated", integer(record(evaluation.coverage).evaluatedSamples)], ["Curve status", text(curves.status)]]} />
    <div className="materials-ml-columns">
      <section><h3>混淆矩阵（原始计数）</h3><DataTable columns={["真实 / 预测 · Actual / predicted", ...labels]} rows={labels.map((label, index) => [label, ...numberList(matrix[index]).map(String)])} empty="暂无混淆矩阵。" testId="materials-ml-confusion-matrix" /></section>
      <section><h3>Per-class metrics</h3><DataTable columns={["Class", "Support", "Precision", "Recall", "F1"]} rows={records(metrics.perClass).map((row) => [text(row.class), integer(row.support), format(row.precision), format(row.recall), format(row.f1)])} empty="No per-class metrics." testId="materials-ml-class-metrics" /></section>
    </div>
    {text(curves.status) === "READY" ? <div className="materials-ml-charts">
      <ChartFrame title={`ROC - positive class ${text(curves.positiveClass)}`} note={`AUC ${format(record(curves.roc).auc)}`}><LineChart points={records(record(curves.roc).points)} x="fpr" y="tpr" /></ChartFrame>
      <ChartFrame title="Precision-recall" note={`Average precision ${format(record(curves.precisionRecall).averagePrecision)}`}><LineChart points={records(record(curves.precisionRecall).points)} x="recall" y="precision" /></ChartFrame>
    </div> : <p className="empty-state" data-testid="materials-ml-curves-unavailable">ROC/PR unavailable: {text(curves.status)}.</p>}
    <h3>Misclassified samples</h3>
    <DataTable columns={["样本键", "样本", "化学式", "真实类别", "预测类别"]} rows={records(evaluation.misclassifiedSamples).map((row) => [canonicalSampleKey(row), text(row.sampleRef), text(row.formula), text(row.actualClass), text(row.predictedClass)])} rowKeys={records(evaluation.misclassifiedSamples).map(canonicalSampleKey)} empty="暂无有界的错误分类样本。" testId="materials-ml-misclassified-table" />
    <Warnings values={textList(evaluation.warnings)} />
  </div>;
}

function ScatterChart({ points, x, y, reference = false }: { points: JsonRecord[]; x: string; y: string; reference?: boolean }) {
  const mapped = points.map((point) => ({ x: finite(point[x]), y: finite(point[y]), source: point })).filter((point): point is { x: number; y: number; source: JsonRecord } => point.x !== null && point.y !== null);
  const rawBounds = chartBounds(mapped);
  const sharedMinimum = Math.min(rawBounds.minX, rawBounds.minY);
  const sharedMaximum = Math.max(rawBounds.maxX, rawBounds.maxY);
  const bounds = reference
    ? { minX: sharedMinimum, maxX: sharedMaximum, minY: sharedMinimum, maxY: sharedMaximum }
    : rawBounds;
  return <svg className="materials-ml-chart" viewBox="0 0 560 260" role="img" aria-label={`${x} versus ${y}`}>
    <ChartAxes />
    {reference ? <line x1="42" y1="226" x2="536" y2="18" className="chart-reference" /> : null}
    {mapped.map((point) => <circle key={canonicalSampleKey(point.source)} cx={scale(point.x, bounds.minX, bounds.maxX, 42, 536)} cy={scale(point.y, bounds.minY, bounds.maxY, 226, 18)} r="3.5"><title>{[canonicalSampleKey(point.source), text(point.source.formula), `${x}=${format(point.x)}`, `${y}=${format(point.y)}`, point.source.absoluteError !== undefined ? `absolute error=${format(point.source.absoluteError)}` : ""].filter(Boolean).join("; ")}</title></circle>)}
    <text x="280" y="255">{x}</text><text x="12" y="130" transform="rotate(-90 12 130)">{y}</text>
  </svg>;
}

function LineChart({ points, x, y }: { points: JsonRecord[]; x: string; y: string }) {
  const mapped = points.map((point) => ({ x: finite(point[x]), y: finite(point[y]) })).filter((point): point is { x: number; y: number } => point.x !== null && point.y !== null);
  const bounds = chartBounds(mapped);
  const path = mapped.map((point, index) => `${index ? "L" : "M"}${scale(point.x, bounds.minX, bounds.maxX, 42, 536)},${scale(point.y, bounds.minY, bounds.maxY, 226, 18)}`).join(" ");
  return <svg className="materials-ml-chart" viewBox="0 0 560 260" role="img" aria-label={`${y} by ${x}`}><ChartAxes /><path d={path} className="chart-line" />{mapped.map((point, index) => <circle key={index} cx={scale(point.x, bounds.minX, bounds.maxX, 42, 536)} cy={scale(point.y, bounds.minY, bounds.maxY, 226, 18)} r="3" />)}<text x="280" y="255">{x}</text><text x="12" y="130" transform="rotate(-90 12 130)">{y}</text></svg>;
}

function Histogram({ counts }: { counts: number[] }) {
  const maximum = Math.max(1, ...counts);
  return <div className="materials-ml-histogram" role="img" aria-label="Residual histogram">{counts.map((count, index) => <span key={index} style={{ height: `${Math.max(2, count / maximum * 100)}%` }} title={`${count}`} />)}</div>;
}

function ChartAxes() { return <><line x1="42" y1="226" x2="536" y2="226" className="chart-axis" /><line x1="42" y1="18" x2="42" y2="226" className="chart-axis" /></>; }
function ChartFrame({ title, note, children }: { title: string; note: string; children: ReactNode }) { return <figure><figcaption><strong>{title}</strong><span>{note}</span></figcaption>{children}</figure>; }
function MetricGrid({ items }: { items: [string, string][] }) { return <dl className="dataset-stat-grid">{items.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>; }
function Field({ label, value }: { label: string; value: string }) { return <div><dt>{label}</dt><dd>{value || "-"}</dd></div>; }
function GroupTable({ rows }: { rows: JsonRecord[] }) { return <DataTable columns={["分组", "样本数", "MAE", "RMSE"]} rows={rows.map((row) => [text(row.group), integer(row.sampleCount), format(row.mae), format(row.rmse)])} empty="暂无化学分组统计。" />; }
function Warnings({ values }: { values: string[] }) { return values.length ? <div className="warning-list" role="status">{values.map((value) => <span className="badge" key={value}>{value}</span>)}</div> : null; }

function DataTable({ columns, rows, rowKeys, empty, testId }: { columns: string[]; rows: string[][]; rowKeys?: string[]; empty: string; testId?: string }) {
  if (!rows.length) return <p className="empty-state">{empty}</p>;
  return <div className="compact-table-wrap" data-testid={testId}><table className="compact-table"><thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={rowKeys?.[index] || index}>{row.map((value, column) => <td key={column}>{value || "-"}</td>)}</tr>)}</tbody></table></div>;
}

export function validateMaterialsMlPayload(payload: JsonRecord | null, product: typeof PRODUCTS[number]): { ok: true; payload: JsonRecord } | { ok: false; reason: string } {
  if (!payload || payload.schemaVersion !== product.schema || payload.artifactType !== `ml.${product.kind}_evaluation`) return { ok: false, reason: "MATERIALS_ML_SCHEMA_UNSUPPORTED" };
  const dataset = record(payload.dataset);
  const security = record(payload.security);
  const evaluations = records(payload.evaluations);
  if (typeof dataset.profileContractVersion !== "string" || !["2.0", "2.1"].includes(dataset.profileContractVersion) || !text(dataset.semanticHash)) return { ok: false, reason: "MATERIALS_ML_PROFILE_BINDING_INVALID" };
  if (security.artifactJavaScript !== false || security.externalUrls !== false || security.externalAssets !== false || security.executableContent !== false) return { ok: false, reason: "MATERIALS_ML_SECURITY_DECLARATION_INVALID" };
  if (!evaluations.length || evaluations.length > CAPS.evaluations) return { ok: false, reason: "MATERIALS_ML_PREVIEW_CAP_EXCEEDED" };
  const overCap = evaluations.some((item) => records(item.parityPoints).length > CAPS.points
    || records(item.uncertaintyErrorPoints).length > CAPS.points
    || records(item.highErrorSamples).length > CAPS.rows
    || records(item.highUncertaintySamples).length > CAPS.rows
    || records(item.misclassifiedSamples).length > CAPS.rows
    || records(item.sampleRows).length > CAPS.rows
    || records(record(item.chemistryConditioned).byElement).length > CAPS.groups
    || records(record(item.chemistryConditioned).byChemicalSystem).length > CAPS.groups
    || numberList(record(item.residualHistogram).counts).length > CAPS.histogramBins
    || textList(record(record(item.metrics).confusionMatrix).labels).length > CAPS.classes
    || records(record(record(item.curves).roc).points).length > CAPS.curvePoints
    || records(record(record(item.curves).precisionRecall).points).length > CAPS.curvePoints);
  if (overCap) return { ok: false, reason: "MATERIALS_ML_PREVIEW_CAP_EXCEEDED" };
  const sampleRows = evaluations.flatMap((item) => [
    ...records(item.parityPoints),
    ...records(item.uncertaintyErrorPoints),
    ...records(item.highErrorSamples),
    ...records(item.highUncertaintySamples),
    ...records(item.misclassifiedSamples),
    ...records(item.sampleRows),
  ]);
  if (sampleRows.some((item) => !validSampleIdentity(item))) return { ok: false, reason: "MATERIALS_ML_SAMPLE_IDENTITY_INVALID" };
  return { ok: true, payload };
}

function validSampleIdentity(value: JsonRecord): boolean {
  const objectId = text(value.objectId);
  const sampleRef = text(value.sampleRef);
  return Boolean(objectId && sampleRef && value.sampleKey === `${objectId}:${sampleRef}` && Number.isSafeInteger(value.rowIndex) && Number(value.rowIndex) >= 0);
}

export function validateMaterialsMlProductPayload(id: MaterialIntelligenceProductId, payload: JsonRecord | null): { ok: true; payload: JsonRecord } | { ok: false; reason: string } {
  const product = PRODUCTS.find((item) => item.id === id);
  return product ? validateMaterialsMlPayload(payload, product) : { ok: false, reason: "MATERIALS_ML_PRODUCT_UNKNOWN" };
}

function chartBounds(points: { x: number; y: number }[]) { const xs = points.map((item) => item.x); const ys = points.map((item) => item.y); return { minX: Math.min(...xs, 0), maxX: Math.max(...xs, 1), minY: Math.min(...ys, 0), maxY: Math.max(...ys, 1) }; }
function scale(value: number, min: number, max: number, low: number, high: number) { return max === min ? (low + high) / 2 : low + (value - min) / (max - min) * (high - low); }
function isRecord(value: unknown): value is JsonRecord { return Boolean(value && typeof value === "object" && !Array.isArray(value)); }
function record(value: unknown): JsonRecord { return isRecord(value) ? value : {}; }
function records(value: unknown): JsonRecord[] { return Array.isArray(value) ? value.filter(isRecord) : []; }
function text(value: unknown): string { return typeof value === "string" || typeof value === "number" ? String(value) : ""; }
function textList(value: unknown): string[] { return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : []; }
function numberList(value: unknown): number[] { return Array.isArray(value) ? value.map((item) => Number(item)).filter(Number.isFinite) : []; }
function finite(value: unknown): number | null { const parsed = Number(value); return Number.isFinite(parsed) ? parsed : null; }
function integer(value: unknown): string { const parsed = Number(value); return Number.isFinite(parsed) ? String(Math.trunc(parsed)) : "0"; }
function format(value: unknown): string { const parsed = Number(value); return Number.isFinite(parsed) ? parsed.toLocaleString(undefined, { maximumFractionDigits: 5 }) : "-"; }
