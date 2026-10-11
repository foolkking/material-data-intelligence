"use client";

import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import type { ScientificPresentationBlock } from "../../app/lib/scientific-presentation";
import { presentationMetricUnit } from "../../app/lib/scientific-presentation";

type Metric = Extract<ScientificPresentationBlock, { type: "metric" }>;
type Entry = { metric: Metric; fact: Agent2ScientificFact };
type Group = { id: string; rows: { symbol: Metric; value: Metric }[]; summary: Metric[]; property: string };
const properties: Record<string, string> = {
  "reference.element.atomic_number": "原子序数",
  "reference.element.covalent_radius": "参考共价半径",
};
const summaryFields = new Set(["reference.element_count", "reference.value_count", "reference.version", "reference.property_definition"]);

/** Pair saved symbol/value facts within one result and producer only. */
export function groupReferenceMetrics(metrics: Metric[], facts: readonly Agent2ScientificFact[]) {
  const byId = new Map<string, Agent2ScientificFact>(), duplicateIds = new Set<string>();
  for (const fact of facts) { if (byId.has(fact.fact_id)) duplicateIds.add(fact.fact_id); byId.set(fact.fact_id, fact); }
  const candidates = new Map<string, Entry[]>();
  for (const metric of metrics) {
    const fact = byId.get(metric.source.factId || "");
    if (!fact || duplicateIds.has(fact.fact_id) || !metric.source.resultId || !fact.source.artifact_id
      || fact.source.artifact_id !== metric.source.artifactId || metric.value !== String(fact.value)
      || (metric.unit || null) !== (fact.unit || null)
      || (metric.source.toolCallId || null) !== (fact.source.tool_call_id || null)
      || metric.source.objectId || metric.source.versionId || fact.source.scientific_object_ref
      || !(summaryFields.has(fact.predicate) || properties[fact.predicate] || fact.predicate === "reference.element.symbol")) continue;
    const id = JSON.stringify([metric.source.resultId, metric.source.artifactId, metric.source.toolCallId]);
    candidates.set(id, [...(candidates.get(id) || []), { metric, fact }]);
  }
  const groups: Group[] = [], consumed = new Set<Metric>();
  for (const [id, entries] of candidates) {
    const kinds = [...new Set(entries.filter(entry => properties[entry.fact.predicate]).map(entry => entry.fact.predicate))];
    if (kinds.length !== 1) continue;
    const property = kinds[0], rows: Group["rows"] = [], subjects = new Map<string, Entry[]>();
    for (const entry of entries.filter(entry => !summaryFields.has(entry.fact.predicate))) {
      if (!entry.fact.subject_ref) continue;
      subjects.set(entry.fact.subject_ref, [...(subjects.get(entry.fact.subject_ref) || []), entry]);
    }
    for (const values of subjects.values()) {
      const symbol = values.find(entry => entry.fact.predicate === "reference.element.symbol");
      const value = values.find(entry => entry.fact.predicate === property);
      if (values.length !== 2 || !symbol || !value || !/^[A-Z][a-z]?$/.test(symbol.metric.value)
        || symbol.fact.unit || typeof value.fact.value !== "number" || !Number.isFinite(value.fact.value) || value.fact.value <= 0
        || (property.endsWith("atomic_number") ? value.fact.unit || !Number.isInteger(value.fact.value) || value.fact.value > 118 : value.fact.unit !== "angstrom")) continue;
      rows.push({symbol: symbol.metric, value: value.metric});
    }
    if (!rows.length || new Set(rows.map(row => row.symbol.value)).size !== rows.length) continue;
    const summary = entries.filter(entry => summaryFields.has(entry.fact.predicate)
      && entries.filter(other => other.fact.predicate === entry.fact.predicate).length === 1).map(entry => entry.metric);
    groups.push({id, rows, summary, property});
    rows.forEach(row => { consumed.add(row.symbol); consumed.add(row.value); });
    summary.forEach(metric => consumed.add(metric));
  }
  return {groups, remaining: metrics.filter(metric => !consumed.has(metric))};
}

export function ReferenceMetrics({ groups }: { groups: Group[] }) {
  return <>{groups.map(group => <details key={group.id} className="scientific-presentation-section">
    <summary>参考数值 · {group.rows.length} 种元素</summary>
    {group.summary.length ? <dl>{group.summary.map(metric => <div key={metric.id}>
      <dt>{metric.title}</dt><dd data-exact-value={metric.value}>{metric.value}</dd>
    </div>)}</dl> : null}
    <div className="workspace-table-scroll" role="region" aria-label="元素参考数值，可横向滚动" tabIndex={0}>
      <table><caption className="sr-only">元素参考数值</caption>
        <thead><tr><th scope="col">元素</th><th scope="col">{properties[group.property]}{group.rows[0].value.unit ? `（${presentationMetricUnit(group.rows[0].value.unit)}）` : ""}</th></tr></thead>
        <tbody>{group.rows.map(row => <tr key={row.symbol.id}>
          <th scope="row" data-fact-id={row.symbol.source.factId}>{row.symbol.value}</th>
          <td data-fact-id={row.value.source.factId} data-exact-value={row.value.value}>{row.value.value}</td>
        </tr>)}</tbody>
      </table>
    </div>
  </details>)}</>;
}
