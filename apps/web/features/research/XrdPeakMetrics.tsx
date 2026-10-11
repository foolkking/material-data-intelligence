import React from "react";
import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import { formatPresentationMetricValue, type ScientificPresentationBlock } from "../../app/lib/scientific-presentation";

type Metric = Extract<ScientificPresentationBlock, { type: "metric" }>;
type PeakRow = { id: string; angle: Metric; intensity: Metric; spacing: Metric; structure?: Metric; hkls: string[] };

/** Group only exact subject/artifact matches; incomplete or conflicting facts remain ordinary metrics. */
export function groupXrdPeakMetrics(metrics: Metric[], facts: readonly Agent2ScientificFact[]) {
  const byId = new Map<string, Agent2ScientificFact>();
  const duplicateIds = new Set<string>();
  for (const fact of facts) {
    if (byId.has(fact.fact_id)) duplicateIds.add(fact.fact_id);
    byId.set(fact.fact_id, fact);
  }
  const groups = new Map<string, Array<{ metric: Metric; fact: Agent2ScientificFact }>>();
  for (const metric of metrics) {
    const factId = metric.source.factId || "";
    const fact = byId.get(factId);
    if (!fact || duplicateIds.has(factId) || !fact.subject_ref || !fact.source.artifact_id
      || metric.source.artifactId !== fact.source.artifact_id || metric.value !== String(fact.value)
      || (metric.source.toolCallId || null) !== (fact.source.tool_call_id || null)
      || (metric.unit || null) !== (fact.unit || null)
      || (fact.source.scientific_object_ref && (metric.source.objectId !== fact.source.scientific_object_ref.object_id || metric.source.versionId !== fact.source.scientific_object_ref.version_id))
      || !/^xrd\.peak\.(two_theta|intensity|d_spacing|structure|hkl_\d+\.component_\d+)$/u.test(fact.predicate)) continue;
    const key = JSON.stringify([metric.source.resultId, fact.source.artifact_id, fact.subject_ref, metric.source.objectId, metric.source.versionId]);
    groups.set(key, [...(groups.get(key) || []), { metric, fact }]);
  }
  const rows: PeakRow[] = [];
  const consumed = new Set<string>();
  for (const [id, items] of groups) {
    if (new Set(items.map(item => item.fact.predicate)).size !== items.length) continue;
    const pick = (predicate: string) => items.find(item => item.fact.predicate === predicate)?.metric;
    const angle = pick("xrd.peak.two_theta"), intensity = pick("xrd.peak.intensity"), spacing = pick("xrd.peak.d_spacing");
    if (!angle || !intensity || !spacing || angle.unit !== "degree" || spacing.unit !== "angstrom" || intensity.unit
      || [angle, intensity, spacing].some(item => {
        const value = byId.get(item.source.factId || "")?.value;
        return typeof value !== "number" || !Number.isFinite(value);
      })) continue;
    const families = new Map<number, Map<number, string>>();
    let invalid = false;
    for (const item of items) {
      const match = item.fact.predicate.match(/^xrd\.peak\.hkl_(\d+)\.component_(\d+)$/u);
      if (!match) continue;
      const family = Number(match[1]), component = Number(match[2]);
      if (!Number.isSafeInteger(item.fact.value) || component > 3 || family > 3 || item.metric.unit) { invalid = true; break; }
      const values = families.get(family) || new Map<number, string>();
      values.set(component, item.metric.value);
      families.set(family, values);
    }
    const hkls: string[] = [];
    for (const [, values] of [...families].sort(([a], [b]) => a - b)) {
      if (![3, 4].includes(values.size) || Array.from({ length: values.size }, (_, i) => i).some(i => !values.has(i))) { invalid = true; break; }
      hkls.push(`(${Array.from({ length: values.size }, (_, i) => values.get(i)).join(", ")})`);
    }
    if (invalid) continue;
    rows.push({ id, angle, intensity, spacing, structure: pick("xrd.peak.structure"), hkls });
    items.forEach(item => consumed.add(item.metric.id));
  }
  return { rows, remaining: metrics.filter(metric => !consumed.has(metric.id)) };
}

export function XrdPeakMetrics({ rows }: { rows: PeakRow[] }) {
  if (!rows.length) return null;
  return <section className="scientific-presentation-section">
    <h4>主要衍射峰</h4>
    <div className="scientific-xrd-peak-table" role="region" aria-label="主要衍射峰数据，可横向滚动" tabIndex={0}>
      <table><caption className="sr-only">已保存的主要衍射峰，按相同峰标识对应各项数值</caption>
        <thead><tr><th scope="col">2θ (°)</th><th scope="col">相对强度</th><th scope="col">晶面间距 (Å)</th><th scope="col">晶面指数</th><th scope="col">来源结构</th></tr></thead>
        <tbody>{rows.map(row => <tr key={row.id}>
          {[row.angle, row.intensity, row.spacing].map(metric => <td key={metric.id}><span title={`精确值：${metric.value}`} data-exact-value={metric.value}>{formatPresentationMetricValue(metric.value)}</span><span className="sr-only">精确值 {metric.value}</span></td>)}
          <td>{row.hkls.length ? row.hkls.map((hkl, index) => <span className="scientific-xrd-hkl" key={index}>{hkl}</span>) : "未提供"}</td>
          <td>{row.structure?.value || "未提供"}</td>
        </tr>)}</tbody>
      </table>
    </div>
  </section>;
}
