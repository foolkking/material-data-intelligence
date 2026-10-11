"use client";

import React, { useId, useState } from "react";
import type { Artifact } from "../../app/lib/planner-api";
import { formatPresentationMetricValue, presentationMetricUnit, type ScientificPresentation } from "../../app/lib/scientific-presentation";
import { tableMetricTitle, TABLE_STAT_LABELS } from "../../app/lib/scientific-table-labels";
import { ArtifactOpenLink } from "../../shared/ui/ArtifactOpenLink";
import type { TableMetric, TableMetricGroup } from "./table-analysis-metrics";
import styles from "./TableAnalysisMetrics.module.css";

const names = { correlation: "变量相关性", numeric: "数值统计", categorical: "类别统计", category: "类别计数", histogram: "直方图统计", scatter: "散点图统计" };
const order = ["column", "left_column", "right_column", "x_column", "y_column", "value", "coefficient", "count", "point_count", "missing", "missing_rate",
  "excluded_count", "input_count", "valid_point_count", "omitted_point_count", "mean", "std", "min", "p25", "median", "p75", "max", "unique_count", "bins", "x_min", "x_max", "y_min", "y_max"];
const primary = new Set(["column", "left_column", "right_column", "x_column", "y_column", "value", "coefficient", "count", "point_count", "missing", "mean", "std", "median", "unique_count"]);
const textFields = new Set(["column", "left_column", "right_column", "x_column", "y_column", "value"]);
const pageSize = 10;

function SavedValue({ metric, coefficient = false }: { metric?: TableMetric; coefficient?: boolean }) {
  if (!metric) return <span aria-label="未提供">—</span>;
  const unit = presentationMetricUnit(metric.unit || "");
  const display = coefficient ? String(Number(Number(metric.value).toPrecision(5))) : ({ pearson: "Pearson", spearman: "Spearman", kendall: "Kendall" } as Record<string, string>)[metric.value]
    || formatPresentationMetricValue(metric.value);
  return <span title={`精确值：${metric.value}${unit ? ` ${unit}` : ""}`} data-exact-value={metric.value} data-fact-id={metric.source.factId}>
    {display}{unit ? ` ${unit}` : ""}{display !== metric.value ? <span className="sr-only">精确值 {metric.value}</span> : null}
  </span>;
}

function MetricTable({ group, artifact, sourceLabel }: { group: TableMetricGroup; artifact?: Artifact; sourceLabel?: string }) {
  const id = useId(), [query, setQuery] = useState(""), [page, setPage] = useState(0), [expanded, setExpanded] = useState(false);
  const available = order.filter(key => group.rows.some(row => row.values[key]));
  const distribution = group.kind === "numeric" && available.includes("p25");
  const initial = distribution ? new Set(["column", "count", "missing", "p25", "median", "p75"]) : primary;
  const columns = available.filter(key => expanded || initial.has(key));
  const extended = available.some(key => !initial.has(key));
  const title = distribution ? "分布统计" : names[group.kind];
  const filtered = group.rows.filter(row => [...textFields].some(key => row.values[key]?.value.toLocaleLowerCase().includes(query.trim().toLocaleLowerCase())));
  const lastPage = Math.max(0, Math.ceil(filtered.length / pageSize) - 1), current = Math.min(page, lastPage);
  const rows = filtered.slice(current * pageSize, (current + 1) * pageSize);
  const prefix = ["numeric", "categorical", "category"].includes(group.kind) ? `table.${group.kind}` : group.kind;
  const label = (key: string) => tableMetricTitle(`${prefix}.${key}`) || TABLE_STAT_LABELS[key] || key;
  return <section className={styles.group} aria-labelledby={`${id}-title`}>
    <header className={styles.heading}><h4 id={`${id}-title`}>{title}</h4>
      {sourceLabel ? <span className={styles.source} title={`精确版本：${group.source.versionId}`}>{sourceLabel}</span> : null}
      {artifact?.jobId ? <ArtifactOpenLink href={`/api/planner/jobs/${encodeURIComponent(artifact.jobId)}/artifacts/${encodeURIComponent(group.artifactId)}/content`}>
        来源数据
      </ArtifactOpenLink> : null}
    </header>
    {group.summary.length ? <dl className={styles.summary}>{group.summary.map(metric => <div key={metric.id}>
      <dt>{metric.title}</dt><dd><SavedValue metric={metric} /></dd>
    </div>)}</dl> : null}
    {group.rows.length > pageSize || extended ? <div className={styles.toolbar}>
      {group.rows.length > pageSize ? <input aria-label={`搜索${title}的变量`} placeholder="搜索变量" type="search" value={query}
        onChange={event => { setQuery(event.target.value); setPage(0); }} /> : null}
      {extended ? <button type="button" aria-expanded={expanded} aria-controls={`${id}-table`} onClick={() => setExpanded(value => !value)}>
        {expanded ? "常用统计" : "全部统计"}
      </button> : null}
    </div> : null}
    <div className={`${styles.scroll} ${group.kind === "correlation" ? styles.pairs : ""}`} role="region" tabIndex={0} aria-label={`${title}，可横向滚动`}>
      <table id={`${id}-table`}>
        <caption className="sr-only">{title}，按已保存的变量身份对应数值</caption>
        <thead><tr>{columns.map(key => <th key={key} scope="col" className={textFields.has(key) ? styles.name : styles.number}>{label(key)}</th>)}</tr></thead>
        <tbody>{rows.map(row => <tr key={row.id}>{columns.map((key, index) => {
          const Cell = index === 0 ? "th" : "td";
          return <Cell key={key} scope={index === 0 ? "row" : undefined} className={textFields.has(key) ? styles.name : styles.number}>
            <SavedValue metric={row.values[key]} coefficient={key === "coefficient"} />
          </Cell>;
        })}</tr>)}</tbody>
      </table>
    </div>
    {!rows.length ? <p role="status" className={styles.empty}>没有匹配的变量</p> : null}
    {group.rows.length > pageSize ? <nav className={styles.pagination} aria-label={`${title}分页`}>
      <span role="status">{filtered.length ? current * pageSize + 1 : 0}–{Math.min((current + 1) * pageSize, filtered.length)} / {filtered.length}</span>
      <button type="button" aria-label={`${title}上一页`} disabled={current === 0} onClick={() => setPage(current - 1)}>上一页</button>
      <button type="button" aria-label={`${title}下一页`} disabled={current === lastPage} onClick={() => setPage(current + 1)}>下一页</button>
    </nav> : null}
  </section>;
}

export function TableAnalysisMetrics({ groups, artifacts, sources = [] }: { groups: TableMetricGroup[]; artifacts: readonly Artifact[]; sources?: ScientificPresentation["exactSourceRefs"] }) {
  if (!groups.length) return null;
  const preferred = groups.filter(group => group.kind === "correlation" || (group.kind === "numeric" && !group.rows.some(row => row.values.p25)));
  const main = groups.length <= 2 ? groups : (preferred.length ? preferred : groups).slice(0, 2);
  const more = groups.filter(group => !main.includes(group));
  const render = (group: TableMetricGroup) => {
    const source = sources.find(item => item.objectId === group.source.objectId && item.versionId === group.source.versionId);
    const sourceLabel = sources.length > 1 && source ? source.displayName || `来源版本 ${source.versionId.slice(0, 8)}` : undefined;
    return <MetricTable key={group.id} group={group} sourceLabel={sourceLabel}
      artifact={artifacts.find(item => (item.artifactId || item.id) === group.artifactId)} />;
  };
  return <div className={styles.tables}>{main.map(render)}
    {more.length ? <details className={styles.more} key={more.map(group => group.id).join("|")}>
      <summary>更多统计 · {more.length} 组</summary><div className={styles.tables}>{more.map(render)}</div>
    </details> : null}
  </div>;
}
