"use client";

import { useMemo, useState, type ReactNode } from "react";

import type { Artifact } from "../../lib/planner-api";
import {
  artifactPayload,
  canonicalSampleKey,
  inspectMaterialIntelligenceArtifacts,
  type JsonRecord,
  type MaterialIntelligenceProductId,
} from "../material-intelligence/materialIntelligenceIntegration";

type ProductKind = "regression" | "uncertainty" | "classification";

const PRODUCTS: readonly { id: MaterialIntelligenceProductId; name: string; schema: string; kind: ProductKind; label: string }[] = [
  { id: "regression", name: "materials_ml_regression.json", schema: "phase10k3.materials_ml_regression.v1", kind: "regression", label: "Regression" },
  { id: "uncertainty", name: "materials_ml_uncertainty.json", schema: "phase10k3.materials_ml_uncertainty.v1", kind: "uncertainty", label: "Uncertainty" },
  { id: "classification", name: "materials_ml_classification.json", schema: "phase10k3.materials_ml_classification.v1", kind: "classification", label: "Classification" },
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
      const artifact = artifacts.find((item) => item.name === product.name);
      if (!artifact) return [];
      const assessment = integration.products.find((item) => item.id === product.id);
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
      <header className="panel-heading"><div><span>Profile 2.0 product</span><h2>Materials ML Evaluation unavailable</h2></div><span className="badge">Rejected</span></header>
      {available.length > 1 ? <div className="materials-ml-selectors"><label>Product<select value={active.product.name} onChange={(event) => { setSelectedName(event.target.value); setSelectedTask(""); }}>{available.map((item) => <option key={item.product.name} value={item.product.name}>{item.product.label} ({item.state})</option>)}</select></label></div> : null}
      <p>The artifact was rejected before product rendering. Inert JSON remains available.</p>
      <code>{validation?.reason || "MATERIALS_ML_ARTIFACT_INVALID"}</code>
      <details><summary>Artifact JSON</summary><pre>{JSON.stringify(active.payload, null, 2)}</pre></details>
    </section>;
  }

  const payload = validation.payload;
  const evaluations = records(payload.evaluations);
  const evaluation = evaluations.find((item) => text(item.taskId) === selectedTask) || evaluations[0];
  const dataset = record(payload.dataset);
  return <section className="panel materials-ml" data-testid="materials-ml-evaluation" aria-label="Materials ML Evaluation">
    <header className="panel-heading">
      <div><span>Deterministic materials model diagnostics</span><h2>Materials ML Evaluation</h2></div>
      <span className="badge">{active.product.label}</span>
    </header>
    <dl className="mini-grid materials-ml-identity">
      <Field label="Dataset" value={text(dataset.datasetId)} />
      <Field label="Profile" value={text(dataset.profileId)} />
      <Field label="Semantic contract" value={text(dataset.profileContractVersion)} />
      <Field label="Residual" value={active.product.kind === "regression" ? text(payload.residualConvention) : "not applicable"} />
    </dl>
    <div className="materials-ml-selectors">
      {available.length > 1 ? <label>Product<select value={active.product.name} onChange={(event) => { setSelectedName(event.target.value); setSelectedTask(""); }}>{available.map((item) => <option key={item.product.name} value={item.product.name}>{item.product.label} ({item.state})</option>)}</select></label> : null}
      {evaluations.length > 1 ? <label>Task / model<select value={text(evaluation?.taskId)} onChange={(event) => setSelectedTask(event.target.value)}>{evaluations.map((item) => <option key={text(item.taskId)} value={text(item.taskId)}>{text(item.taskId)}</option>)}</select></label> : null}
    </div>
    {!evaluation ? <p className="empty-state">No bounded evaluation result.</p> : null}
    {evaluation && active.product.kind === "regression" ? <RegressionView evaluation={evaluation} comparisons={records(payload.modelComparisons)} /> : null}
    {evaluation && active.product.kind === "uncertainty" ? <UncertaintyView evaluation={evaluation} /> : null}
    {evaluation && active.product.kind === "classification" ? <ClassificationView evaluation={evaluation} /> : null}
    <p className="dataset-method-note">Performance diagnostics describe the supplied result dataset. They do not establish material validity, causal model quality, or scientific truth.</p>
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
      ["MAE", format(metrics.mae)], ["RMSE", format(metrics.rmse)], ["R2", metrics.r2 === null ? "undefined" : format(metrics.r2)],
      ["Mean error", format(metrics.meanSignedError)], ["Evaluated", `${integer(coverage.evaluatedSamples)} / ${integer(coverage.totalSamples)}`], ["Unit", text(evaluation.unit) || "unavailable"],
    ]} />
    <div className="materials-ml-charts">
      <ChartFrame title="Parity" note="Target x; prediction y; dashed line is y=x."><ScatterChart points={points} x="target" y="prediction" reference /></ChartFrame>
      <ChartFrame title="Residual vs target" note="Residual = prediction - target; points use the same bounded evaluated-sample set."><ScatterChart points={points} x="target" y="residual" /></ChartFrame>
      <ChartFrame title="Residual distribution" note="Residual = prediction - target."><Histogram counts={counts} /></ChartFrame>
    </div>
    <h3>Largest prediction errors</h3>
    <DataTable columns={["Sample key", "Sample", "Formula", "System", "Target", "Prediction", "Residual", "Absolute error", "Uncertainty"]} rows={highError.map((row) => [canonicalSampleKey(row), text(row.sampleRef), text(row.formula), text(row.chemicalSystem), format(row.target), format(row.prediction), format(row.residual), format(row.absoluteError), format(row.uncertainty)])} rowKeys={highError.map(canonicalSampleKey)} empty="No aligned high-error samples." testId="materials-ml-high-error-table" />
    <div className="materials-ml-columns">
      <section><h3>Error by element</h3><p className="dataset-method-note">Element groups overlap; a material can appear in multiple rows.</p><GroupTable rows={records(chemistry.byElement)} /></section>
      <section><h3>Error by chemical system</h3><p className="dataset-method-note">Small groups remain visible and are marked by sample count.</p><GroupTable rows={records(chemistry.byChemicalSystem)} /></section>
    </div>
    {comparisons.length ? <><h3>Model comparison</h3><DataTable columns={["Target", "Common samples", "Policy", "Models"]} rows={comparisons.map((item) => [text(item.targetColumn), integer(item.commonSampleCount), text(item.policy), records(item.models).map((model) => text(model.seriesId)).join(", ")])} empty="No multiple-model comparison." testId="materials-ml-model-comparison" /></> : null}
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
      <ChartFrame title="Uncertainty vs absolute error" note="Each point retains its stable material sample reference."><ScatterChart points={points} x="uncertainty" y="absoluteError" /></ChartFrame>
      <ChartFrame title="Error decay" note="Retain the lowest-uncertainty samples first."><LineChart points={records(errorDecay.points)} x="retainedFraction" y="mae" /></ChartFrame>
    </div>
    <h3>Equal-count reliability bins</h3>
    <DataTable columns={["Bin", "Samples", "Mean uncertainty", "Mean absolute error"]} rows={records(reliability.bins).map((row) => [integer(row.bin), integer(row.sampleCount), format(row.meanUncertainty), format(row.meanAbsoluteError)])} empty="No reliability bins." testId="materials-ml-reliability-table" />
    <h3>Highest uncertainty samples</h3>
    <DataTable columns={["Sample key", "Sample", "Formula", "Uncertainty", "Absolute error"]} rows={records(evaluation.highUncertaintySamples).map((row) => [canonicalSampleKey(row), text(row.sampleRef), text(row.formula), format(row.uncertainty), format(row.absoluteError)])} rowKeys={records(evaluation.highUncertaintySamples).map(canonicalSampleKey)} empty="No aligned uncertainty samples." testId="materials-ml-high-uncertainty-table" />
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
      <section><h3>Confusion matrix (raw counts)</h3><DataTable columns={["Actual / predicted", ...labels]} rows={labels.map((label, index) => [label, ...numberList(matrix[index]).map(String)])} empty="No confusion matrix." testId="materials-ml-confusion-matrix" /></section>
      <section><h3>Per-class metrics</h3><DataTable columns={["Class", "Support", "Precision", "Recall", "F1"]} rows={records(metrics.perClass).map((row) => [text(row.class), integer(row.support), format(row.precision), format(row.recall), format(row.f1)])} empty="No per-class metrics." testId="materials-ml-class-metrics" /></section>
    </div>
    {text(curves.status) === "READY" ? <div className="materials-ml-charts">
      <ChartFrame title={`ROC - positive class ${text(curves.positiveClass)}`} note={`AUC ${format(record(curves.roc).auc)}`}><LineChart points={records(record(curves.roc).points)} x="fpr" y="tpr" /></ChartFrame>
      <ChartFrame title="Precision-recall" note={`Average precision ${format(record(curves.precisionRecall).averagePrecision)}`}><LineChart points={records(record(curves.precisionRecall).points)} x="recall" y="precision" /></ChartFrame>
    </div> : <p className="empty-state" data-testid="materials-ml-curves-unavailable">ROC/PR unavailable: {text(curves.status)}.</p>}
    <h3>Misclassified samples</h3>
    <DataTable columns={["Sample key", "Sample", "Formula", "Actual", "Predicted"]} rows={records(evaluation.misclassifiedSamples).map((row) => [canonicalSampleKey(row), text(row.sampleRef), text(row.formula), text(row.actualClass), text(row.predictedClass)])} rowKeys={records(evaluation.misclassifiedSamples).map(canonicalSampleKey)} empty="No bounded misclassified samples." testId="materials-ml-misclassified-table" />
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
function GroupTable({ rows }: { rows: JsonRecord[] }) { return <DataTable columns={["Group", "Samples", "MAE", "RMSE"]} rows={rows.map((row) => [text(row.group), integer(row.sampleCount), format(row.mae), format(row.rmse)])} empty="No chemistry grouping." />; }
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
  if (dataset.profileContractVersion !== "2.0" || !text(dataset.semanticHash)) return { ok: false, reason: "MATERIALS_ML_PROFILE_BINDING_INVALID" };
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
