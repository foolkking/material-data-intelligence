"use client";

import { useMemo, useState } from "react";

import type { Artifact } from "../../lib/planner-api";

type JsonRecord = Record<string, unknown>;
type ExplorerTab = "overview" | "composition" | "structures" | "properties" | "model" | "quality" | "comparison" | "samples";

const TABS: readonly { id: ExplorerTab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "composition", label: "Composition" },
  { id: "structures", label: "Structures" },
  { id: "properties", label: "Properties" },
  { id: "model", label: "Model evaluation" },
  { id: "quality", label: "Data quality" },
  { id: "comparison", label: "Comparison" },
  { id: "samples", label: "Samples" },
];

const MAX_ROWS = 200;
const MAX_ELEMENTS = 256;
const MAX_PROPERTIES = 64;
const MAX_STRUCTURES = 256;
const MAX_COLUMNS = 512;
const MAX_WARNINGS = 128;
const MAX_HISTOGRAM_BINS = 100;

export function DatasetMaterialsExplorerPanel({ artifacts }: { artifacts: Artifact[] }) {
  const artifact = artifacts.find((item) => item.name === "dataset_materials_explorer.json");
  const payload = useMemo(() => artifactPayload(artifact), [artifact]);
  const validation = useMemo(() => validateExplorer(payload), [payload]);
  const [tab, setTab] = useState<ExplorerTab>("overview");
  const [selectedProperty, setSelectedProperty] = useState("");
  const [selectedSample, setSelectedSample] = useState("");

  if (!artifact) return null;
  if (!validation.ok) {
    return (
      <section className="panel dataset-explorer" data-testid="dataset-materials-explorer-invalid" role="status" aria-label="Dataset Materials Explorer validation status">
        <header className="panel-heading"><div><span>Dataset product</span><h2>Dataset Materials Explorer unavailable</h2></div><span className="badge">Rejected</span></header>
        <p>The artifact was rejected before product rendering. Inert JSON remains available.</p>
        <code>{validation.reason}</code>
        <details><summary>Artifact JSON</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details>
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
  const activeSample = samples.find((item) => text(item.sampleRef) === selectedSample);

  return (
    <section className="panel dataset-explorer" data-testid="dataset-materials-explorer" aria-label="Dataset Materials Explorer">
      <header className="panel-heading">
        <div><span>Profile 2.0 product</span><h2>Dataset Materials Explorer</h2></div>
        <span className="badge">{text(dataset.datasetType) || "materials dataset"}</span>
      </header>
      <dl className="mini-grid dataset-explorer-identity">
        <Field label="Dataset" value={text(dataset.datasetId)} testId="dataset-explorer-dataset-id" />
        <Field label="Profile" value={text(dataset.profileId)} />
        <Field label="Semantic contract" value={text(dataset.profileContractVersion)} />
        <Field label="Semantic hash" value={compactHash(text(dataset.semanticHash))} />
      </dl>
      <div className="dataset-explorer-tabs" role="tablist" aria-label="Dataset explorer views">
        {TABS.map((item) => (
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
        {tab === "structures" ? <StructuresView structures={structures} /> : null}
        {tab === "properties" ? (
          <PropertiesView properties={properties} active={activeProperty} onSelect={setSelectedProperty} />
        ) : null}
        {tab === "model" ? <ModelEvaluationView overview={overview} /> : null}
        {tab === "quality" ? <QualityView quality={quality} /> : null}
        {tab === "comparison" ? <ComparisonView comparison={comparison} /> : null}
        {tab === "samples" ? (
          <SamplesView samples={samples} active={activeSample} onSelect={setSelectedSample} />
        ) : null}
      </div>
    </section>
  );
}

function OverviewView({ overview, warnings }: { overview: JsonRecord; warnings: string[] }) {
  return <div data-testid="dataset-explorer-overview">
    <dl className="dataset-stat-grid">
      <Metric label="Samples" value={numberText(overview.sampleCount)} />
      <Metric label="Tables" value={numberText(overview.tableCount)} />
      <Metric label="Structures" value={numberText(overview.structureCount)} />
      <Metric label="Properties" value={numberText(overview.propertyCount)} />
    </dl>
    <div className="dataset-explorer-columns">
      <ListSection title="Available analyses" values={textList(overview.availableAnalyses)} empty="No executable analyses declared." />
      <ListSection title="Unavailable analyses" values={textList(overview.unavailableAnalyses)} empty="No unavailable analyses declared." />
    </div>
    <ListSection title="Warnings" values={warnings} empty="No bounded product warnings." />
  </div>;
}

function CompositionView({ composition }: { composition: JsonRecord }) {
  const elements = records(composition.elements).slice(0, MAX_ELEMENTS);
  const systems = records(composition.chemicalSystems).slice(0, MAX_ROWS);
  const maxCount = Math.max(1, ...elements.map((item) => number(item.materialsContainingElement)));
  return <div data-testid="dataset-explorer-composition">
    <dl className="mini-grid">
      <Field label="Status" value={text(composition.status)} />
      <Field label="Formula column" value={text(composition.formulaColumn)} />
      <Field label="Unique formulas" value={numberText(composition.uniqueFormulaCount)} />
      <Field label="Unique reduced formulas" value={numberText(composition.uniqueReducedFormulaCount)} />
    </dl>
    <h3>Element coverage</h3>
    {!elements.length ? <p className="empty-state">Formula semantics are unavailable.</p> : (
      <div className="dataset-bar-list" data-testid="dataset-element-bars">
        {elements.map((item) => <BarRow key={text(item.element)} label={text(item.element)} value={number(item.materialsContainingElement)} max={maxCount} />)}
      </div>
    )}
    <h3>Chemical systems</h3>
    <DataTable columns={["Chemical system", "Count"]} rows={systems.map((item) => [text(item.chemicalSystem), numberText(item.count)])} empty="No chemical systems." />
  </div>;
}

function StructuresView({ structures }: { structures: JsonRecord }) {
  const rows = records(structures.records).slice(0, MAX_ROWS);
  return <div data-testid="dataset-explorer-structures">
    <dl className="mini-grid"><Field label="Status" value={text(structures.status)} /><Field label="Structures" value={numberText(structures.structureCount)} /></dl>
    <DataTable
      columns={["Resource", "Formula", "Sites", "Volume (A^3)", "Density (g/cm^3)", "Space group", "Crystal system"]}
      rows={rows.map((item) => [text(item.objectId), text(item.formula), numberText(item.siteCount), format(item.volumeAngstrom3), format(item.densityGramCm3), text(item.spacegroup), text(item.crystalSystem)])}
      empty="No canonical structures were bound."
    />
    <p className="dataset-method-note">Symmetry uses the fixed adapter policy. Exact structure duplicates require equal canonical normalized object hashes.</p>
  </div>;
}

function PropertiesView({ properties, active, onSelect }: { properties: JsonRecord[]; active?: JsonRecord; onSelect: (value: string) => void }) {
  const histogram = record(active?.histogram);
  const counts = numberList(histogram.counts);
  const maxCount = Math.max(1, ...counts);
  return <div data-testid="dataset-explorer-properties">
    {!properties.length ? <p className="empty-state">No Profile 2.0 material-property roles are available.</p> : <>
      <label className="dataset-property-select">Property
        <select value={text(active?.column)} onChange={(event) => onSelect(event.target.value)}>
          {properties.map((item) => <option key={text(item.column)} value={text(item.column)}>{text(item.column)}{text(item.unit) ? ` (${text(item.unit)})` : ""}</option>)}
        </select>
      </label>
      <dl className="mini-grid">
        <Field label="Count" value={numberText(active?.count)} />
        <Field label="Missing" value={numberText(active?.missingCount)} />
        <Field label="Non-finite" value={numberText(active?.nonFiniteCount)} />
        <Field label="Unit" value={text(active?.unit) || "not declared"} />
      </dl>
      <Statistics statistics={record(active?.statistics)} />
      <div className="dataset-histogram" data-testid="dataset-property-histogram" aria-label={`${text(active?.column)} histogram`}>
        {counts.map((value, index) => <span key={index} style={{ height: `${Math.max(3, value / maxCount * 100)}%` }} title={`${value}`} />)}
      </div>
      <p className="dataset-method-note">Outliers use the 1.5 IQR rule and are statistical candidates only.</p>
    </>}
  </div>;
}

function ModelEvaluationView({ overview }: { overview: JsonRecord }) {
  const capabilities = ["regression_evaluation", "uncertainty_evaluation", "classification_evaluation"];
  const available = textList(overview.availableAnalyses).filter((item) => capabilities.includes(item));
  const unavailable = textList(overview.unavailableAnalyses).filter((item) => capabilities.includes(item));
  return <div data-testid="dataset-explorer-model-evaluation">
    {!available.length ? <p className="empty-state">No model-result semantics detected.</p> : <>
      <h3>Profile-ready model evaluations</h3>
      <ul>{available.map((item) => <li key={item}>{item}</li>)}</ul>
      <p className="dataset-method-note">Run the matching Materials ML Evaluation tool to create deterministic diagnostics linked to stable material samples.</p>
    </>}
    {unavailable.length ? <><h3>Unavailable for this dataset</h3><ul>{unavailable.map((item) => <li key={item}>{item}</li>)}</ul></> : null}
  </div>;
}

function QualityView({ quality }: { quality: JsonRecord }) {
  const columnIssues = records(quality.columnIssues).slice(0, MAX_ROWS);
  const duplicates = records(quality.duplicateSampleIdentityValues).slice(0, MAX_ROWS);
  return <div data-testid="dataset-explorer-quality">
    <dl className="mini-grid">
      <Field label="Invalid formulas" value={numberText(quality.invalidFormulaCount)} />
      <Field label="Sample links" value={numberText(quality.sampleLinksMaterialized)} />
      <Field label="Near duplicates" value={text(quality.nearDuplicateAnalysis)} />
    </dl>
    <h3>Column issues</h3>
    <DataTable columns={["Column", "Missing", "Non-finite", "Ambiguities"]} rows={columnIssues.map((item) => [text(item.column), numberText(item.missingCount), numberText(item.nonFiniteCount), textList(item.ambiguities).join(", ") || "none"])} empty="No column issues." />
    <h3>Duplicate identity values</h3>
    <DataTable columns={["Column", "Value", "Count"]} rows={duplicates.map((item) => [text(item.column), text(item.value), numberText(item.count)])} empty="No duplicate explicit IDs." />
  </div>;
}

function ComparisonView({ comparison }: { comparison: JsonRecord }) {
  if (text(comparison.status) !== "READY") return <div data-testid="dataset-explorer-comparison"><p className="empty-state">No explicit dataset comparison was requested.</p></div>;
  const overlap = record(comparison.elementOverlap);
  const rows = records(comparison.propertyComparison).slice(0, MAX_PROPERTIES);
  return <div data-testid="dataset-explorer-comparison">
    <dl className="mini-grid"><Field label="Mode" value={text(comparison.mode)} /><Field label="Binding" value={JSON.stringify(comparison.binding || {})} /></dl>
    <div className="dataset-explorer-columns">
      <ListSection title="Shared elements" values={textList(overlap.shared)} empty="None" />
      <ListSection title="Left only" values={textList(overlap.leftOnly)} empty="None" />
      <ListSection title="Right only" values={textList(overlap.rightOnly)} empty="None" />
    </div>
    <DataTable columns={["Property", "Unit", "Comparable", "Left median", "Right median"]} rows={rows.map((item) => [text(item.column), text(item.unit) || "-", String(Boolean(item.comparable)), format(record(item.left).median), format(record(item.right).median)])} empty="No comparable material properties." />
    <p className="dataset-method-note">{text(comparison.semantics)}</p>
  </div>;
}

function SamplesView({ samples, active, onSelect }: { samples: JsonRecord[]; active?: JsonRecord; onSelect: (value: string) => void }) {
  return <div data-testid="dataset-explorer-samples">
    {active ? <dl className="mini-grid dataset-sample-inspector" aria-live="polite" data-testid="dataset-sample-inspector"><Field label="Sample" value={text(active.sampleRef)} /><Field label="Formula" value={text(active.formula)} /><Field label="Reduced formula" value={text(active.reducedFormula)} /><Field label="Source" value={`${text(active.objectId)} row ${numberText(active.rowIndex)}`} /></dl> : <p className="empty-state">Select a stable sample reference to inspect its source row.</p>}
    <div className="compact-table-wrap"><table className="compact-table"><caption>Bounded stable sample index</caption><thead><tr><th>Sample reference</th><th>Formula</th><th>Reduced formula</th><th>Object</th><th>Row</th></tr></thead><tbody>
      {samples.map((item) => <tr key={`${text(item.sampleRef)}:${numberText(item.rowIndex)}`}><td><button type="button" className="link-button" onClick={() => onSelect(text(item.sampleRef))}>{text(item.sampleRef)}</button></td><td>{text(item.formula) || "-"}</td><td>{text(item.reducedFormula) || "-"}</td><td>{text(item.objectId)}</td><td>{numberText(item.rowIndex)}</td></tr>)}
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
  return <div className="compact-table-wrap"><table className="compact-table"><thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={index}>{row.map((value, column) => <td key={column}>{value || "-"}</td>)}</tr>)}</tbody></table></div>;
}

function validateExplorer(payload: JsonRecord | null): { ok: true; payload: JsonRecord } | { ok: false; reason: string } {
  if (!payload || payload.schemaVersion !== "phase10k2.dataset_materials_explorer.v1") return { ok: false, reason: "DATASET_EXPLORER_SCHEMA_UNSUPPORTED" };
  if (!record(payload.dataset).profileId || record(payload.dataset).profileContractVersion !== "2.0") return { ok: false, reason: "DATASET_EXPLORER_PROFILE_BINDING_INVALID" };
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
  return { ok: true, payload };
}

function artifactPayload(artifact?: Artifact): JsonRecord | null {
  if (!artifact) return null;
  const metadata = record(artifact.metadata);
  for (const candidate of [artifact.content, artifact.payload, metadata.content, metadata.payload, metadata.preview]) {
    if (isRecord(candidate)) return candidate;
    if (typeof candidate === "string") { try { const parsed = JSON.parse(candidate); if (isRecord(parsed)) return parsed; } catch { /* inert fallback */ } }
  }
  return null;
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
