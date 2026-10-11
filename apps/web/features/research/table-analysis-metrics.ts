import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import type { ScientificPresentationBlock } from "../../app/lib/scientific-presentation";

export type TableMetric = Extract<ScientificPresentationBlock, { type: "metric" }>;
type Entry = { metric: TableMetric; fact: Agent2ScientificFact };
export type TableMetricKind = "correlation" | "numeric" | "categorical" | "category" | "histogram" | "scatter";
export type TableMetricRow = { id: string; values: Record<string, TableMetric> };
export type TableMetricGroup = { id: string; kind: TableMetricKind; artifactId: string; source: TableMetric["source"]; rows: TableMetricRow[]; summary: TableMetric[] };
const fields: Record<TableMetricKind, string[]> = {
  correlation: ["left_column", "right_column", "coefficient"],
  numeric: ["column", "count", "missing", "missing_rate", "mean", "std", "min", "p25", "median", "p75", "max", "unique_count"],
  categorical: ["column", "count", "missing", "missing_rate", "unique_count"],
  category: ["column", "value", "count"],
  histogram: ["column", "count", "input_count", "excluded_count", "bins", "min", "max", "mean", "median"],
  scatter: ["x_column", "y_column", "point_count", "valid_point_count", "input_count", "excluded_count", "omitted_point_count", "x_min", "x_max", "y_min", "y_max"],
};
const summaryPredicates = new Set(["table.row_count", "table.column_count", "correlation.method", "correlation.pair_count",
  "correlation.valid_pair_count", "correlation.missing_pair_count", "correlation.minimum_sample_count"]);

function field(predicate: string): { kind: TableMetricKind; key: string } | null {
  const match = predicate.match(/^(?:table\.(numeric|categorical|category)|(correlation|histogram|scatter))\.(.+)$/u);
  if (!match) return null;
  const kind = (match[1] || match[2]) as TableMetricKind;
  return fields[kind].includes(match[3]) ? { kind, key: match[3] } : null;
}

/** Presentation grouping never joins different results, artifacts or source versions. */
export function groupTableAnalysisMetrics(metrics: TableMetric[], facts: readonly Agent2ScientificFact[]) {
  const factsById = new Map<string, Agent2ScientificFact>(), duplicates = new Set<string>();
  for (const fact of facts) { if (factsById.has(fact.fact_id)) duplicates.add(fact.fact_id); factsById.set(fact.fact_id, fact); }
  const candidates = new Map<string, Entry[]>(), verified: Entry[] = [];
  for (const metric of metrics) {
    const fact = factsById.get(metric.source.factId || "");
    if (!fact || duplicates.has(fact.fact_id) || !metric.source.resultId || !fact.subject_ref || !fact.source.artifact_id
      || fact.source.artifact_id !== metric.source.artifactId || metric.value !== String(fact.value)
      || (metric.unit || null) !== (fact.unit || null)
      || (metric.source.toolCallId || null) !== (fact.source.tool_call_id || null)
      || (fact.source.scientific_object_ref && (metric.source.objectId !== fact.source.scientific_object_ref.object_id
        || metric.source.versionId !== fact.source.scientific_object_ref.version_id))
      || (!field(fact.predicate) && !summaryPredicates.has(fact.predicate))) continue;
    const entry = { metric, fact }; verified.push(entry);
    const key = JSON.stringify([metric.source.resultId, fact.source.artifact_id, fact.subject_ref,
      metric.source.objectId, metric.source.versionId]);
    candidates.set(key, [...(candidates.get(key) || []), entry]);
  }
  const grouped = new Map<string, TableMetricGroup>(), consumed = new Set<TableMetric>();
  for (const [rowId, entries] of candidates) {
    if (new Set(entries.map(e => e.fact.predicate)).size !== entries.length) continue;
    const shape = entries.map(e => field(e.fact.predicate)).find(Boolean);
    if (!shape) continue;
    const { kind } = shape;
    const items = entries.filter(e => field(e.fact.predicate)?.kind === kind);
    const values = Object.fromEntries(items.map(e => [field(e.fact.predicate)!.key, e.metric]));
    const textKeys = kind === "correlation" ? ["left_column", "right_column"] : kind === "scatter" ? ["x_column", "y_column"] : kind === "category" ? ["column", "value"] : ["column"];
    if (textKeys.some(key => !values[key] || values[key].unit || typeof factsById.get(values[key].source.factId!)?.value !== "string" || !values[key].value.trim())) continue;
    const numbers = items.filter(e => !textKeys.includes(field(e.fact.predicate)!.key));
    if (!numbers.length || numbers.some(e => typeof e.fact.value !== "number" || !Number.isFinite(e.fact.value))) continue;
    if (kind === "correlation" && (!values.coefficient || values.coefficient.unit || Math.abs(Number(values.coefficient.value)) > 1)) continue;
    if (numbers.some(e => /\.(?:count|input_count|excluded_count|missing|unique_count|point_count|valid_point_count|omitted_point_count|bins)$/u.test(e.fact.predicate)
      && (e.fact.unit !== "count" || !Number.isSafeInteger(e.fact.value) || Number(e.fact.value) < 0))) continue;
    if (values.missing_rate && (values.missing_rate.unit || Number(values.missing_rate.value) < 0 || Number(values.missing_rate.value) > 1)) continue;
    const source = items[0].metric.source;
    const id = JSON.stringify([source.resultId, source.artifactId, source.objectId, source.versionId, kind]);
    const group = grouped.get(id) || { id, kind, artifactId: source.artifactId!, source, rows: [], summary: [] };
    group.rows.push({ id: rowId, values }); grouped.set(id, group);
    items.forEach(e => consumed.add(e.metric));
  }
  // Global counts appear once for the exact artifact, never once per column.
  for (const group of grouped.values()) {
    const source = group.rows[0].values[Object.keys(group.rows[0].values)[0]].source;
    for (const entry of verified) {
      if (consumed.has(entry.metric) || !summaryPredicates.has(entry.fact.predicate)
        || entry.metric.source.resultId !== source.resultId || entry.metric.source.artifactId !== source.artifactId
        || entry.metric.source.objectId !== source.objectId || entry.metric.source.versionId !== source.versionId) continue;
      if (verified.filter(e => e.fact.predicate === entry.fact.predicate && e.metric.source.artifactId === source.artifactId
        && e.metric.source.resultId === source.resultId).length !== 1) continue;
      if (entry.fact.predicate === "correlation.method" ?
        (entry.fact.unit || !["pearson", "spearman", "kendall"].includes(String(entry.fact.value))) :
        (entry.fact.unit !== "count" || !Number.isSafeInteger(entry.fact.value) || Number(entry.fact.value) < 0)) continue;
      group.summary.push(entry.metric); consumed.add(entry.metric);
    }
  }
  return { groups: [...grouped.values()], remaining: metrics.filter(metric => !consumed.has(metric)) };
}
