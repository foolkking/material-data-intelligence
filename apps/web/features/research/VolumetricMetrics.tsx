import React from "react";
import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import type { Artifact } from "../../app/lib/planner-api";
import { formatPresentationMetricValue, type ScientificPresentationBlock } from "../../app/lib/scientific-presentation";
import { densityFieldName, densityIntegralMeaning, densityUnit } from "../../scientific-viewers/volumetric-viewer/density-display";
import { ArtifactOpenLink } from "../../shared/ui/ArtifactOpenLink";
import styles from "./ResearchResultPresentation.module.css";

type Metric = Extract<ScientificPresentationBlock, { type: "metric" }>;
type Entry = { metric: Metric; fact: Agent2ScientificFact };
type FieldStatistics = { id: string; artifactId: string; name: string; values: Array<{ label: string; metric: Metric }>; reference?: Metric; shift?: Metric };
function statisticUnit(unit: string): string {
  const units: Record<string, string> = {"electronvolt*angstrom^3": "eV·Å³", "hartree*angstrom^3": "Ha·Å³", "volt*angstrom^3": "V·Å³"};
  return units[unit] || densityUnit(unit);
}
const statisticLabels: Record<string, string> = {
  "volumetric.minimum": "最小值", "volumetric.maximum": "最大值", "volumetric.mean": "均值",
  "volumetric.integral": "整胞积分", "volumetric.volume_integral": "整胞体积分",
};
const detailPredicates = new Set([
  "length_unit", "coordinate_space", "sample_location", "endpoint_policy",
  "grid_size_a", "grid_size_b", "grid_size_c", "boundary_a", "boundary_b", "boundary_c",
  "selected_field_name", "selected_component", "selected_quantity", "selected_canonical_unit", "selected_minimum", "selected_maximum",
  "field_name", "quantity", "value_kind", "canonical_unit", "integral_semantics", "normalization_semantics",
  "source_unit", "unit_conversion_applied", "unit_conversion_factor", "statistics_authority",
].map(name => `volumetric.${name}`));

/** Only group values whose exact fact, subject and artifact identities agree. */
export function groupVolumetricMetrics(metrics: Metric[], facts: readonly Agent2ScientificFact[]) {
  const byId = new Map<string, Agent2ScientificFact>();
  const duplicates = new Set<string>();
  for (const fact of facts) {
    if (byId.has(fact.fact_id)) duplicates.add(fact.fact_id);
    byId.set(fact.fact_id, fact);
  }
  const verified: Entry[] = [];
  const candidates = new Map<string, Entry[]>();
  for (const metric of metrics) {
    const fact = byId.get(metric.source.factId || "");
    if (!fact || duplicates.has(fact.fact_id) || !metric.source.resultId || !fact.subject_ref || !fact.source.artifact_id
      || metric.source.artifactId !== fact.source.artifact_id || metric.value !== String(fact.value)
      || (metric.unit || null) !== (fact.unit || null)
      || (metric.source.toolCallId || null) !== (fact.source.tool_call_id || null)
      || (fact.source.scientific_object_ref && (metric.source.objectId !== fact.source.scientific_object_ref.object_id || metric.source.versionId !== fact.source.scientific_object_ref.version_id))
      || !fact.predicate.startsWith("volumetric.")) continue;
    const entry = { metric, fact };
    verified.push(entry);
    const key = JSON.stringify([metric.source.resultId, fact.source.artifact_id, fact.subject_ref, metric.source.objectId, metric.source.versionId]);
    candidates.set(key, [...(candidates.get(key) || []), entry]);
  }
  const groups: FieldStatistics[] = [];
  const consumed = new Set<Metric>();
  for (const [id, entries] of candidates) {
    if (new Set(entries.map(entry => entry.fact.predicate)).size !== entries.length) continue;
    const pick = (predicate: string) => entries.find(entry => entry.fact.predicate === `volumetric.${predicate}`);
    const fieldName = pick("field_name"), quantity = pick("quantity"), unit = pick("canonical_unit");
    const minimum = pick("minimum"), maximum = pick("maximum");
    if (!fieldName || !quantity || !unit || !minimum || !maximum
      || [fieldName, quantity, unit].some(entry => typeof entry.fact.value !== "string" || !entry.metric.value.trim() || entry.metric.unit)) continue;
    const stats = Object.keys(statisticLabels).flatMap(predicate => entries.filter(entry => entry.fact.predicate === predicate));
    if (stats.some(entry => typeof entry.fact.value !== "number" || !Number.isFinite(entry.fact.value)
      || !entry.metric.unit || (["volumetric.minimum", "volumetric.maximum", "volumetric.mean"].includes(entry.fact.predicate) && entry.metric.unit !== unit.metric.value))) continue;
    if (Number(minimum.fact.value) > Number(maximum.fact.value)) continue;
    const reference = pick("potential_reference"), shift = pick("potential_shift");
    const validReference = reference && typeof reference.fact.value === "string" && !reference.metric.unit ? reference.metric : undefined;
    const validShift = shift && typeof shift.fact.value === "number" && Number.isFinite(shift.fact.value) && shift.metric.unit === unit.metric.value ? shift.metric : undefined;
    const name = densityFieldName({fieldName: fieldName.metric.value, quantity: quantity.metric.value, spin: null});
    groups.push({ id, artifactId: fieldName.fact.source.artifact_id!, name,
      values: stats.map(entry => ({label: statisticLabels[entry.fact.predicate], metric: entry.metric})),
      reference: validReference, shift: validShift,
    });
    stats.forEach(entry => consumed.add(entry.metric));
    if (validReference) consumed.add(validReference);
    if (validShift) consumed.add(validShift);
  }
  // Technical definitions remain available; failed/ambiguous statistics remain
  // ordinary visible metrics rather than being silently joined or discarded.
  const details = groups.length ? verified.filter(entry => detailPredicates.has(entry.fact.predicate)) : [];
  details.forEach(entry => consumed.add(entry.metric));
  return { groups, details, remaining: metrics.filter(metric => !consumed.has(metric)) };
}

function detailValue(entry: Entry): string {
  const { fact, metric } = entry;
  const name = fact.predicate.replace(/^volumetric\./u, "");
  if (typeof fact.value === "boolean") return fact.value ? "是" : "否";
  if (["canonical_unit", "selected_canonical_unit", "source_unit", "length_unit"].includes(name)) return densityUnit(metric.value === "angstrom" ? "Å" : metric.value);
  if (["integral_semantics", "normalization_semantics"].includes(name)) return metric.value === "cell_average" ? "源数据声明胞平均" : densityIntegralMeaning(metric.value);
  if (["quantity", "selected_quantity"].includes(name)) {
    return ({orbital_density: "部分电荷密度", electron_density: "电子密度", magnetization_density: "磁化密度"} as Record<string, string>)[metric.value]
      || densityFieldName({ fieldName: metric.value, quantity: metric.value, spin: null });
  }
  const values: Record<string, Record<string, string>> = {
    coordinate_space: { real_cartesian: "笛卡尔坐标" }, sample_location: { node: "网格节点", cell_center: "网格中心" },
    endpoint_policy: { excluded: "不包含终点", included: "包含终点" },
    boundary_a: { periodic: "周期边界", open: "开放边界" }, boundary_b: { periodic: "周期边界", open: "开放边界" }, boundary_c: { periodic: "周期边界", open: "开放边界" },
    value_kind: { real: "实数", complex: "复数" }, statistics_authority: { computed_from_payload: "由保存的场数据计算", source_declared: "源数据声明" },
  };
  return values[name]?.[metric.value] || formatPresentationMetricValue(metric.value);
}

export function VolumetricMetrics({ groups, details, artifacts }: ReturnType<typeof groupVolumetricMetrics> & { artifacts: readonly Artifact[] }) {
  if (!groups.length) return null;
  return <section className={`scientific-presentation-section ${styles.fieldStatistics}`} aria-label="场数据统计">
    {groups.map(group => {
      const artifact = artifacts.find(item => (item.artifactId || item.id) === group.artifactId);
      return <section key={group.id} aria-label={`${group.name}统计`}>
        <div className={styles.statisticHeading}><h4>{group.name}</h4>
          {artifact?.jobId ? <ArtifactOpenLink href={`/api/planner/jobs/${encodeURIComponent(artifact.jobId)}/artifacts/${encodeURIComponent(group.artifactId)}/content`}>来源数据</ArtifactOpenLink> : null}
        </div>
        <dl className={styles.statisticValues}>{group.values.map(({label, metric}) => <div key={metric.id}>
          <dt>{label}</dt><dd title={`精确值：${metric.value} ${metric.unit || ""}`} data-exact-value={metric.value} data-unit={metric.unit}>
            {formatPresentationMetricValue(metric.value)} <span>{statisticUnit(metric.unit || "")}</span>
          </dd>
        </div>)}</dl>
        {group.reference || group.shift ? <div className={styles.statisticReference}>
          {group.reference ? <span title={`源值：${group.reference.value}`} data-exact-value={group.reference.value}>参考零点：{group.reference.value === "source_defined" ? "源数据定义" : group.reference.value}</span> : null}
          {group.shift ? <span title={`精确值：${group.shift.value} ${group.shift.unit || ""}`} data-exact-value={group.shift.value}>已保存平移：{formatPresentationMetricValue(group.shift.value)} {statisticUnit(group.shift.unit || "")}</span> : null}
        </div> : null}
      </section>;
    })}
    {details.length ? <details key={details.map(entry => entry.metric.id).join("|")}>
      <summary>数据定义与网格 · {details.length} 项</summary>
      <dl className={styles.fieldDefinitions}>{details.map(entry => <div key={entry.metric.id}>
        <dt>{entry.metric.title}</dt><dd title={`源值：${entry.metric.value}`} data-exact-value={entry.metric.value}>
          {detailValue(entry)}{entry.metric.unit ? ` ${densityUnit(entry.metric.unit)}` : ""}
        </dd>
      </div>)}</dl>
    </details> : null}
  </section>;
}
