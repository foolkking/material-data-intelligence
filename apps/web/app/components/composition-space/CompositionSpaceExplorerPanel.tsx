"use client";

import { useMemo, useState } from "react";

import type { Artifact } from "../../lib/planner-api";

type JsonRecord = Record<string, unknown>;
type ValidationResult = { ok: true; payload: JsonRecord } | { ok: false; reason: string };

const SCHEMA_VERSION = "phase10k4.composition_space.v1";
const MAX_POINTS = 20_000;
const MAX_DISPLAY_POINTS = 10_000;
const MAX_TABLE_ROWS = 200;
const MAX_ELEMENTS = 118;
const MAX_CLUSTERS = 12;
const MAX_COLOR_OPTIONS = 64;
const MAX_WARNINGS = 128;
const MAX_VALUE_FIELDS = 128;
const CATEGORICAL_COLORS = ["#16738b", "#b5472d", "#41764b", "#9b6b18", "#5d6194", "#8a4f68", "#347c78", "#71562e"] as const;
const COLOR_SOURCES = new Set([
  "composition_space",
  "composition_semantics",
  "explicit_comparison_binding",
  "material_data_profile_2_material_property",
  "phase10k3_sample_bound_artifact",
]);

export function CompositionSpaceExplorerPanel({ artifacts }: { artifacts: Artifact[] }) {
  const artifact = artifacts.find((item) => item.name === "composition_space.json");
  if (!artifact) return null;
  return (
    <section className="panel composition-space" data-testid="composition-space-explorer" aria-label="Composition Space Explorer">
      <CompositionSpaceContent artifact={artifact} standalone />
    </section>
  );
}

export function CompositionSpaceExplorerBody({ artifacts }: { artifacts: Artifact[] }) {
  const artifact = artifacts.find((item) => item.name === "composition_space.json");
  if (!artifact) return <p className="empty-state">No Composition Space artifact is available.</p>;
  return <CompositionSpaceContent artifact={artifact} standalone={false} />;
}

function CompositionSpaceContent({ artifact, standalone }: { artifact: Artifact; standalone: boolean }) {
  const payload = useMemo(() => artifactPayload(artifact), [artifact]);
  const validation = useMemo(() => validatePayload(payload), [payload]);
  const [requestedColor, setRequestedColor] = useState("");
  const [selectedKey, setSelectedKey] = useState("");

  if (!validation.ok) {
    return <div className="composition-space-invalid" data-testid="composition-space-invalid" role="status" aria-label="Composition Space validation status">
      {standalone ? <header className="panel-heading"><div><span>Profile 2.0 product</span><h2>Composition Space Explorer unavailable</h2></div><span className="badge">Rejected</span></header> : <h3>Composition Space unavailable</h3>}
      <p>The artifact was rejected before product rendering. Inert JSON remains available.</p>
      <code>{validation.reason}</code>
      <details><summary>Artifact JSON</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details>
    </div>;
  }

  const data = validation.payload;
  const dataset = record(data.dataset);
  const coverage = record(data.coverage);
  const feature = record(data.featureRepresentation);
  const projection = record(data.projection);
  const clustering = record(data.clustering);
  const comparison = record(data.comparison);
  const coloring = record(data.coloring);
  const points = records(data.points);
  const displayed = displayPoints(points, textList(data.displayPointKeys));
  const colorOptions = records(coloring.available);
  const defaultColor = colorOptions.some((option) => text(option.id) === text(coloring.default)) ? text(coloring.default) : text(colorOptions[0]?.id);
  const colorId = colorOptions.some((option) => text(option.id) === requestedColor) ? requestedColor : defaultColor;
  const selected = points.find((point) => pointKey(point) === selectedKey);
  const warnings = collectWarnings(data, coverage);

  return <div className="composition-space-content">
    {standalone ? <header className="panel-heading">
      <div><span>Deterministic composition informatics</span><h2>Composition Space Explorer</h2></div>
      <span className="badge">PCA 2D</span>
    </header> : <div className="composition-space-subheading"><div><h3>Composition Space</h3><p>Backend-computed atomic-fraction PCA with stable sample linkage.</p></div><span className="badge">PCA 2D</span></div>}

    <dl className="mini-grid composition-space-identity">
      <Field label="Dataset" value={text(dataset.datasetId)} />
      <Field label="Profile" value={text(dataset.profileId)} />
      <Field label="Valid samples" value={integer(coverage.validCompositionSamples)} />
      <Field label="Invalid samples" value={integer(coverage.invalidCompositionSamples)} />
      <Field label="Element dimensions" value={integer(feature.featureDimensions)} />
      <Field label="Explained variance" value={percentage(projection.cumulativeExplainedVarianceRatio)} />
    </dl>

    <div className="composition-space-toolbar">
      <label htmlFor={`composition-space-color-${standalone ? "panel" : "tab"}`}>Color by
        <select
          id={`composition-space-color-${standalone ? "panel" : "tab"}`}
          value={colorId}
          onChange={(event) => setRequestedColor(event.target.value)}
          data-testid="composition-space-color-mode"
        >
          {colorOptions.map((option) => <option key={text(option.id)} value={text(option.id)}>{text(option.label)}{text(option.unit) ? ` (${text(option.unit)})` : ""}</option>)}
        </select>
      </label>
      <dl className="composition-space-method">
        <Field label="Features" value="Normalized atomic fractions" />
        <Field label="Projection" value={`${text(projection.method)} / ${text(projection.solver)}`} />
        <Field label="Clustering" value={text(clustering.status) === "READY" ? `${text(clustering.method)} on feature space` : text(clustering.status)} />
      </dl>
    </div>

    <div className="composition-space-main">
      <figure className="composition-space-figure">
        <figcaption>
          <strong>Composition projection</strong>
          <span>{colorDescription(colorId, colorOptions, displayed)}</span>
        </figcaption>
        <CompositionScatter points={displayed} colorId={colorId} selectedKey={selectedKey} onSelect={setSelectedKey} />
      </figure>
      <SampleInspector sample={selected} />
    </div>

    <p className="dataset-method-note">PCA proximity and composition clusters are descriptive views of normalized composition only. They do not establish structural similarity, material families, validity, or chemical truth.</p>

    {text(comparison.status) === "READY" ? <section className="composition-space-comparison" data-testid="composition-space-comparison">
      <h3>Dataset comparison</h3>
      <dl className="mini-grid">
        <Field label="Mode" value={text(comparison.mode)} />
        <Field label="Policy" value={text(comparison.projectionPolicy)} />
        <Field label="Shared basis" value={booleanText(comparison.sharedElementBasis)} />
        <Field label="Shared PCA fit" value={booleanText(comparison.sharedPcaFit)} />
      </dl>
      <DataTable columns={["Dataset / group", "Samples"]} rows={records(comparison.groups).map((item) => [text(item.group), integer(item.sampleCount)])} empty="No comparison groups." />
      <p className="dataset-method-note">The combined projection is exploratory and is not evidence that a split is safe for model training.</p>
    </section> : null}

    <div className="composition-space-detail-grid">
      <section data-testid="composition-space-clusters">
        <h3>Composition clusters</h3>
        {text(clustering.status) !== "READY" ? <p className="empty-state">Clustering was not requested.</p> : <DataTable
          columns={["Cluster", "Samples", "Dominant elements", "Top chemical systems"]}
          rows={records(clustering.clusters).map((cluster) => [
            integer(cluster.cluster),
            integer(cluster.sampleCount),
            records(cluster.dominantElements).map((item) => `${text(item.element)} ${percentage(item.meanFraction)}`).join(", "),
            records(cluster.topChemicalSystems).map((item) => `${text(item.chemicalSystem)} (${integer(item.count)})`).join(", "),
          ])}
          empty="No bounded cluster summaries."
        />}
      </section>
      <section data-testid="composition-space-outliers">
        <h3>Composition-space candidates</h3>
        <DataTable
          columns={["Rank", "Sample", "Object", "Row", "Feature-centroid distance"]}
          rows={records(data.outlierCandidates).map((item) => [integer(item.rank), text(item.sampleRef), text(item.objectId), integer(item.rowIndex), format(item.distance)])}
          empty="No bounded distance candidates."
        />
        <p className="dataset-method-note">Distance ranking identifies composition-space candidates only; it does not label a material invalid or anomalous.</p>
      </section>
    </div>

    <details className="composition-space-table-fallback">
      <summary>Accessible sample table ({Math.min(displayed.length, MAX_TABLE_ROWS)} of {displayed.length})</summary>
      <DataTable
        columns={["Sample", "Object", "Row", "Formula", "System", "PC1", "PC2", "Cluster"]}
        rows={displayed.slice(0, MAX_TABLE_ROWS).map((point) => [text(point.sampleRef), text(point.objectId), integer(point.rowIndex), text(point.formula), text(point.chemicalSystem), format(numberList(point.coordinates)[0]), format(numberList(point.coordinates)[1]), nullableInteger(point.cluster)])}
        empty="No display samples."
      />
    </details>

    <Warnings values={warnings} />
  </div>;
}

function CompositionScatter({ points, colorId, selectedKey, onSelect }: { points: JsonRecord[]; colorId: string; selectedKey: string; onSelect: (key: string) => void }) {
  const mapped = points.map((point) => {
    const coordinates = numberList(point.coordinates);
    return { point, x: coordinates[0], y: coordinates[1], color: colorValue(point, colorId) };
  });
  const xs = mapped.map((item) => item.x);
  const ys = mapped.map((item) => item.y);
  const xBounds = paddedBounds(xs);
  const yBounds = paddedBounds(ys);
  const continuous = mapped.map((item) => typeof item.color === "number" ? item.color : null).filter((value): value is number => value !== null);
  const colorBounds = simpleBounds(continuous);
  return <svg className="composition-space-chart" viewBox="0 0 720 400" role="img" aria-label={`PCA composition scatter colored by ${colorId}`}>
    <line x1="58" y1="350" x2="694" y2="350" className="composition-space-axis" />
    <line x1="58" y1="24" x2="58" y2="350" className="composition-space-axis" />
    {mapped.map(({ point, x, y, color }) => {
      const key = pointKey(point);
      const selected = key === selectedKey;
      const label = `${text(point.sampleRef)}, ${text(point.formula) || "formula unavailable"}, PC1 ${format(x)}, PC2 ${format(y)}`;
      return <circle
        key={key}
        cx={scale(x, xBounds[0], xBounds[1], 58, 694)}
        cy={scale(y, yBounds[0], yBounds[1], 350, 24)}
        r={selected ? 8 : 5}
        fill={pointColor(color, colorBounds)}
        className={selected ? "selected" : ""}
        role="button"
        tabIndex={0}
        aria-label={label}
        aria-pressed={selected}
        onClick={() => onSelect(key)}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            onSelect(key);
          }
        }}
      ><title>{label}; {colorId}={String(color ?? "unavailable")}</title></circle>;
    })}
    <text x="376" y="388">PC1</text>
    <text x="18" y="190" transform="rotate(-90 18 190)">PC2</text>
  </svg>;
}

function SampleInspector({ sample }: { sample?: JsonRecord }) {
  if (!sample) return <aside className="composition-space-inspector" data-testid="composition-space-sample-inspector" aria-live="polite"><h3>Sample inspector</h3><p className="empty-state">Select a point with mouse, touch, Enter, or Space.</p></aside>;
  return <aside className="composition-space-inspector" data-testid="composition-space-sample-inspector" aria-live="polite">
    <div className="composition-space-inspector-heading"><h3>Sample inspector</h3><span className="badge">{nullableInteger(sample.cluster) === "-" ? "unclustered" : `cluster ${nullableInteger(sample.cluster)}`}</span></div>
    <dl className="mini-grid">
      <Field label="Sample reference" value={text(sample.sampleRef)} />
      <Field label="Identity source" value={text(sample.identitySource)} />
      <Field label="Object" value={text(sample.objectId)} />
      <Field label="Row" value={integer(sample.rowIndex)} />
      <Field label="Formula" value={text(sample.formula)} />
      <Field label="Reduced formula" value={text(sample.reducedFormula)} />
      <Field label="Chemical system" value={text(sample.chemicalSystem)} />
      <Field label="Dataset / group" value={text(sample.group)} />
    </dl>
    <ValueTable title="Atomic fractions" values={record(sample.elementFractions)} />
    <ValueTable title="Profile properties" values={record(sample.propertyValues)} />
    <ValueTable title="Linked ML values" values={record(sample.mlValues)} />
  </aside>;
}

function ValueTable({ title, values }: { title: string; values: JsonRecord }) {
  const entries = Object.entries(values).sort(([left], [right]) => left.localeCompare(right));
  return <section className="composition-space-values"><h4>{title}</h4>{entries.length ? <dl>{entries.map(([key, value]) => <div key={key}><dt>{key}</dt><dd>{format(value)}</dd></div>)}</dl> : <p className="empty-state">None supplied.</p>}</section>;
}

function Warnings({ values }: { values: string[] }) {
  return <section className="composition-space-warnings" aria-label="Composition Space warnings"><h3>Warnings</h3>{values.length ? <ul>{values.map((value, index) => <li key={`${value}:${index}`}>{value}</li>)}</ul> : <p className="empty-state">No bounded product warnings.</p>}</section>;
}

function DataTable({ columns, rows, empty }: { columns: string[]; rows: string[][]; empty: string }) {
  if (!rows.length) return <p className="empty-state">{empty}</p>;
  return <div className="compact-table-wrap"><table className="compact-table"><thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{rows.map((row, rowIndex) => <tr key={rowIndex}>{row.map((value, columnIndex) => <td key={columnIndex}>{value || "-"}</td>)}</tr>)}</tbody></table></div>;
}

function Field({ label, value }: { label: string; value: string }) {
  return <div><dt>{label}</dt><dd>{value || "-"}</dd></div>;
}

function validatePayload(payload: JsonRecord | null): ValidationResult {
  if (!payload || payload.schemaVersion !== SCHEMA_VERSION || payload.artifactType !== "dataset.composition_space") return { ok: false, reason: "COMPOSITION_SPACE_SCHEMA_UNSUPPORTED" };
  const dataset = record(payload.dataset);
  if (!safeText(dataset.datasetId) || !safeText(dataset.profileId) || dataset.profileContractVersion !== "2.0" || !hashText(dataset.semanticHash)) return { ok: false, reason: "COMPOSITION_SPACE_PROFILE_BINDING_INVALID" };
  const security = record(payload.security);
  if (security.artifactJavaScript !== false || security.externalUrls !== false || security.externalAssets !== false || security.executableContent !== false) return { ok: false, reason: "COMPOSITION_SPACE_SECURITY_DECLARATION_INVALID" };

  const feature = record(payload.featureRepresentation);
  const basis = textList(feature.elementBasis);
  if (feature.type !== "normalized_atomic_fraction" || feature.basisOrder !== "atomic_number_ascending" || feature.normalization !== "element_amount_divided_by_total_amount" || basis.length < 2 || basis.length > MAX_ELEMENTS || new Set(basis).size !== basis.length || basis.some((item) => !/^[A-Z][a-z]?$/.test(item))) return { ok: false, reason: "COMPOSITION_SPACE_FEATURE_CONTRACT_INVALID" };

  const projection = record(payload.projection);
  const components = Array.isArray(projection.components) ? projection.components : [];
  if (projection.method !== "PCA"
    || projection.dimensions !== 2
    || projection.centering !== true
    || projection.scaling !== "none"
    || projection.solver !== "sklearn_full_svd"
    || projection.signConvention !== "largest_absolute_loading_is_positive"
    || !finiteVector(projection.explainedVarianceRatio, 2)
    || !finiteRange(projection.cumulativeExplainedVarianceRatio, 0, 1.000001)
    || !finiteVector(projection.mean, basis.length)
    || components.length !== 2
    || components.some((row) => !finiteVector(row, basis.length))) return { ok: false, reason: "COMPOSITION_SPACE_PROJECTION_CONTRACT_INVALID" };

  const clustering = record(payload.clustering);
  if (!new Set(["READY", "DISABLED"]).has(text(clustering.status)) || (text(clustering.status) === "READY" && (clustering.method !== "kmeans_lloyd" || clustering.featureSpace !== "normalized_atomic_fraction" || records(clustering.clusters).length > MAX_CLUSTERS))) return { ok: false, reason: "COMPOSITION_SPACE_CLUSTER_CONTRACT_INVALID" };

  const points = records(payload.points);
  const displayPointKeys = textList(payload.displayPointKeys);
  const outliers = records(payload.outlierCandidates);
  const options = records(record(payload.coloring).available);
  const warningCount = textList(payload.warnings).length + records(record(payload.coverage).invalidExamples).length;
  if (points.length < 3 || points.length > MAX_POINTS || displayPointKeys.length < 1 || displayPointKeys.length > MAX_DISPLAY_POINTS || outliers.length > MAX_TABLE_ROWS || options.length < 1 || options.length > MAX_COLOR_OPTIONS || warningCount > MAX_WARNINGS) return { ok: false, reason: "COMPOSITION_SPACE_PREVIEW_CAP_EXCEEDED" };
  if (!points.every((point) => validPoint(point, basis, records(clustering.clusters).length))) return { ok: false, reason: "COMPOSITION_SPACE_POINT_INVALID" };
  const knownPointKeys = new Set(points.map(pointKey));
  if (new Set(displayPointKeys).size !== displayPointKeys.length || displayPointKeys.some((key) => !knownPointKeys.has(key))) return { ok: false, reason: "COMPOSITION_SPACE_DISPLAY_BINDING_INVALID" };
  if (!options.every(validColorOption)) return { ok: false, reason: "COMPOSITION_SPACE_COLOR_METADATA_INVALID" };
  if (!validSemantics(record(payload.semantics))) return { ok: false, reason: "COMPOSITION_SPACE_SEMANTICS_INVALID" };
  return { ok: true, payload };
}

function validPoint(point: JsonRecord, basis: string[], clusterCount: number): boolean {
  const coordinates = point.coordinates;
  const fractions = record(point.elementFractions);
  const fractionEntries = Object.entries(fractions);
  const cluster = point.cluster;
  const validCluster = cluster === null || (Number.isSafeInteger(cluster) && Number(cluster) >= 0 && Number(cluster) < Math.max(clusterCount, 1));
  const fractionSum = fractionEntries.reduce((sum, [, value]) => sum + Number(value), 0);
  return safeText(point.sampleRef)
    && point.sampleKey === `${text(point.objectId)}:${text(point.sampleRef)}`
    && safeText(point.identitySource)
    && safeText(point.objectId)
    && Number.isSafeInteger(point.rowIndex)
    && Number(point.rowIndex) >= 0
    && finiteVector(coordinates, 2)
    && validCluster
    && fractionEntries.length >= 1
    && fractionEntries.length <= MAX_ELEMENTS
    && fractionEntries.every(([key, value]) => basis.includes(key) && finiteRange(value, 0, 1))
    && Math.abs(fractionSum - 1) <= 1e-6
    && validNumberRecord(record(point.propertyValues), MAX_VALUE_FIELDS)
    && validNumberRecord(record(point.mlValues), MAX_VALUE_FIELDS);
}

function validColorOption(option: JsonRecord): boolean {
  const id = text(option.id);
  const validId = id === "cluster" || id === "chemical_system" || id === "group" || /^property:[^\s<>]{1,128}$/.test(id) || /^ml:[^<>]{1,256}$/.test(id);
  return validId
    && new Set(["categorical", "continuous"]).has(text(option.kind))
    && safeText(option.label)
    && COLOR_SOURCES.has(text(option.source))
    && (option.unit === undefined || option.unit === null || safeText(option.unit));
}

function validSemantics(semantics: JsonRecord): boolean {
  return semantics.roleInferenceRepeated === false
    && semantics.sampleIdentityPreserved === true
    && semantics.projectionIsNotCanonicalMaterialIdentity === true
    && semantics.clusterMeaning === "composition_cluster_only"
    && semantics.outlierMeaning === "distance_to_feature_centroid_candidate_only"
    && semantics.structuralSimilarityClaimed === false
    && semantics.chemicalFamilyClaimed === false;
}

function displayPoints(points: JsonRecord[], pointKeys: string[]): JsonRecord[] {
  const byKey = new Map(points.map((point) => [pointKey(point), point]));
  return pointKeys.map((key) => byKey.get(key)).filter((point): point is JsonRecord => Boolean(point)).slice(0, MAX_DISPLAY_POINTS);
}

function colorValue(point: JsonRecord, colorId: string): string | number | null {
  if (colorId === "cluster") return point.cluster === null ? null : Number(point.cluster);
  if (colorId === "chemical_system") return text(point.chemicalSystem) || null;
  if (colorId === "group") return text(point.group) || null;
  if (colorId.startsWith("property:")) return finite(record(point.propertyValues)[colorId.slice(9)]);
  if (colorId.startsWith("ml:")) return finite(record(point.mlValues)[colorId.slice(3)]);
  return null;
}

function pointColor(value: string | number | null, continuousBounds: readonly [number, number]): string {
  if (typeof value === "number") {
    const ratio = continuousBounds[1] === continuousBounds[0] ? 0.5 : (value - continuousBounds[0]) / (continuousBounds[1] - continuousBounds[0]);
    const red = Math.round(32 + 158 * Math.max(0, Math.min(1, ratio)));
    const green = Math.round(116 - 45 * Math.max(0, Math.min(1, ratio)));
    const blue = Math.round(132 - 92 * Math.max(0, Math.min(1, ratio)));
    return `rgb(${red}, ${green}, ${blue})`;
  }
  if (typeof value === "string") return CATEGORICAL_COLORS[stableIndex(value, CATEGORICAL_COLORS.length)];
  return "#8b9499";
}

function colorDescription(colorId: string, options: JsonRecord[], points: JsonRecord[]): string {
  const option = options.find((item) => text(item.id) === colorId);
  const values = points.map((point) => colorValue(point, colorId)).filter((value) => value !== null);
  if (option?.kind === "continuous") {
    const bounds = simpleBounds(values.filter((value): value is number => typeof value === "number"));
    return `${text(option.label)}: ${format(bounds[0])} to ${format(bounds[1])}${text(option.unit) ? ` ${text(option.unit)}` : ""}; unavailable values are gray.`;
  }
  return `${text(option?.label) || colorId}; ${new Set(values.map(String)).size} categories; colors are display-only.`;
}

function collectWarnings(payload: JsonRecord, coverage: JsonRecord): string[] {
  const values = [...textList(payload.warnings)];
  const invalidCount = Number(coverage.invalidCompositionSamples);
  if (Number.isFinite(invalidCount) && invalidCount > 0) values.push(`${invalidCount} composition rows were excluded by the backend parser; no silent drops were used.`);
  for (const item of records(coverage.invalidExamples)) values.push(`${text(item.objectId)} row ${integer(item.rowIndex)}: ${text(item.reason)}`);
  return values.slice(0, MAX_WARNINGS);
}

function artifactPayload(artifact: Artifact): JsonRecord | null {
  const metadata = record(artifact.metadata);
  for (const candidate of [artifact.content, artifact.payload, metadata.content, metadata.payload, metadata.preview]) {
    if (isRecord(candidate)) return candidate;
    if (typeof candidate === "string") {
      try { const parsed = JSON.parse(candidate); if (isRecord(parsed)) return parsed; } catch { /* inert fallback */ }
    }
  }
  return null;
}

function pointKey(point: JsonRecord): string { return text(point.sampleKey); }
function stableIndex(value: string, size: number): number { let hash = 0; for (let index = 0; index < value.length; index += 1) hash = ((hash * 31) + value.charCodeAt(index)) >>> 0; return hash % size; }
function simpleBounds(values: number[]): readonly [number, number] { return values.length ? [Math.min(...values), Math.max(...values)] : [0, 1]; }
function paddedBounds(values: number[]): readonly [number, number] { const [minimum, maximum] = simpleBounds(values); if (minimum === maximum) return [minimum - 0.5, maximum + 0.5]; const padding = (maximum - minimum) * 0.06; return [minimum - padding, maximum + padding]; }
function scale(value: number, minimum: number, maximum: number, low: number, high: number): number { return maximum === minimum ? (low + high) / 2 : low + ((value - minimum) / (maximum - minimum)) * (high - low); }
function isRecord(value: unknown): value is JsonRecord { return Boolean(value && typeof value === "object" && !Array.isArray(value)); }
function record(value: unknown): JsonRecord { return isRecord(value) ? value : {}; }
function records(value: unknown): JsonRecord[] { return Array.isArray(value) ? value.filter(isRecord) : []; }
function text(value: unknown): string { return typeof value === "string" || typeof value === "number" ? String(value) : ""; }
function textList(value: unknown): string[] { return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : []; }
function numberList(value: unknown): number[] { return Array.isArray(value) ? value.map((item) => Number(item)).filter(Number.isFinite) : []; }
function finite(value: unknown): number | null { const result = Number(value); return Number.isFinite(result) ? result : null; }
function finiteNumber(value: unknown): boolean { return typeof value === "number" && Number.isFinite(value); }
function finiteVector(value: unknown, length: number): boolean { return Array.isArray(value) && value.length === length && value.every(finiteNumber); }
function finiteRange(value: unknown, minimum: number, maximum: number): boolean { return finiteNumber(value) && Number(value) >= minimum && Number(value) <= maximum; }
function safeText(value: unknown): boolean { return typeof value === "string" && value.length > 0 && value.length <= 512; }
function hashText(value: unknown): boolean { return typeof value === "string" && /^[a-f0-9]{64}$/i.test(value); }
function validNumberRecord(value: JsonRecord, limit: number): boolean { const entries = Object.entries(value); return entries.length <= limit && entries.every(([key, item]) => key.length > 0 && key.length <= 256 && finiteNumber(item)); }
function integer(value: unknown): string { const result = Number(value); return Number.isFinite(result) ? String(Math.trunc(result)) : "0"; }
function nullableInteger(value: unknown): string { return value === null || value === undefined ? "-" : integer(value); }
function format(value: unknown): string { const result = Number(value); return Number.isFinite(result) ? result.toLocaleString(undefined, { maximumFractionDigits: 6 }) : "-"; }
function percentage(value: unknown): string { const result = Number(value); return Number.isFinite(result) ? `${(result * 100).toLocaleString(undefined, { maximumFractionDigits: 2 })}%` : "-"; }
function booleanText(value: unknown): string { return value === true ? "yes" : value === false ? "no" : "unknown"; }
