import { ProductLink } from "../../shared/layout/ProductNavigation";
import { ArtifactOpenLink } from "../../shared/ui/ArtifactOpenLink";
import { reportBasisGroupLabel, reportBasisMissingText, reportBasisSourceLabel, reportBasisSourceDisplayLabel, resolveReportBasis, type ReportBasisReferences } from "../../app/lib/scientific-report-basis";
import type { ScientificReportView } from "../../app/lib/scientific-report-api";
import styles from "./ReportDocument.module.css";

export function ScientificReportBasis({ view, references, originalStatement, label = "查看科学依据" }: {
  view: ScientificReportView;
  references: ReportBasisReferences;
  originalStatement?: string;
  label?: string;
}) {
  const basis = resolveReportBasis(view, references);
  const missing = reportBasisMissingText(basis);
  const hasRefs = references.fact_refs?.length || references.evidence_refs?.length || references.finding_refs?.length;
  if (!hasRefs && !originalStatement) return null;
  const identities = [["事实引用", references.fact_refs], ["证据引用", references.evidence_refs], ["发现引用", references.finding_refs]] as const;
  const sourceLink = (source: typeof basis.sources[number]) => {
    return <ProductLink key={`${source.object_id}:${source.version_id}`} title={`精确版本 ${source.version_id}`}
      href={`/projects/${encodeURIComponent(view.project_id)}/data?object=${encodeURIComponent(source.object_id)}&version=${encodeURIComponent(source.version_id)}`}>
      {reportBasisSourceDisplayLabel(source, basis.sources)}
    </ProductLink>;
  };
  return <details className={`scientific-report-finding-evidence ${styles.basis}`}>
    <summary>{label}</summary>
    {basis.comparisonTitle ? <table className={styles.basisComparison}>
      <caption className="sr-only">引用事实对比</caption>
      <thead><tr><th scope="col">材料</th><th scope="col">{basis.comparisonTitle}</th></tr></thead>
      <tbody>{basis.groups.map(group => <tr key={group.key}><th scope="row">{sourceLink(group.sources[0])}</th><td data-exact-value={group.facts[0].value_text}>{group.facts[0].value}</td></tr>)}</tbody>
    </table> : basis.groups.map(group => <div className={styles.basisGroup} key={group.key}>
      <div className={styles.basisSources}>{group.sources.length ? group.sources.map(sourceLink) : <span>{reportBasisGroupLabel(group, basis.sources)}</span>}</div>
      <dl className={styles.basisValues}>{group.facts.map(fact => <div key={fact.fact_id}>
        <dt>{fact.title}</dt>
        <dd data-exact-value={fact.value_text}>{fact.value.length > 240 ? <details><summary>查看数值</summary><pre tabIndex={0} aria-label={fact.title}>{fact.value}</pre></details> : fact.value}</dd>
      </div>)}</dl>
    </div>)}
    {basis.files.length ? <div className={styles.basisFiles} aria-label="依据文件">{basis.files.map(file =>
      <ArtifactOpenLink key={`${file.job_id}:${file.artifact_id}`} href={`/api/planner/jobs/${encodeURIComponent(file.job_id!)}/artifacts/${encodeURIComponent(file.artifact_id!)}/content`}>{file.title}</ArtifactOpenLink>,
    )}</div> : null}
    {missing ? <p role="status">{missing}</p> : null}
    <details className={styles.basisRecords}>
      <summary>引用与版本</summary>
      <dl>
        {originalStatement ? <div><dt>原始表述（保留数值精度）</dt><dd>{originalStatement}</dd></div> : null}
        {basis.sources.map(source => <div key={`${source.object_id}:${source.version_id}`}><dt>{reportBasisSourceLabel(source)}</dt><dd>对象：<code>{source.object_id}</code><br />版本：<code>{source.version_id}</code></dd></div>)}
        <div><dt>科学结果快照</dt><dd><code>{view.scientific_result_snapshot_id}</code></dd></div>
        {identities.filter(([, refs]) => refs?.length).map(([title, refs]) => <div key={title}><dt>{title}</dt><dd>{[...new Set(refs)].map(ref => <code key={ref}>{ref}</code>)}</dd></div>)}
        {basis.facts.map(fact => <div key={`locator:${fact.fact_id}`}><dt>{fact.title}</dt><dd>
          <code>{fact.fact_id}</code><code>{fact.subject_ref}</code>
          {fact.artifact_locator ? <code>{fact.artifact_locator}</code> : null}
          {fact.uncertainty_text ? <span>不确定度：{fact.uncertainty_text}</span> : null}
        </dd></div>)}
        {basis.evidence.map(item => <div key={item.evidence_id}><dt>{item.tool_id || "来源记录"}</dt><dd>
          <code>{item.evidence_id}</code>{item.artifact_id ? <code>{item.artifact_id}</code> : null}
          {item.tool_call_id ? <code>{item.tool_call_id}</code> : null}
          {item.artifact_locator ? <code>{item.artifact_locator}</code> : null}
        </dd></div>)}
      </dl>
    </details>
  </details>;
}
