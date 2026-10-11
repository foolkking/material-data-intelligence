"use client";

import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import dynamic from "next/dynamic";
import React, { useEffect, useState } from "react";
import {
  compareScientificReportRevisions,
  dedupeReportSentences,
  getScientificReport,
  humanizeScientificMethodSummary,
  listScientificReportRevisions,
  type ScientificReportRevisionComparison,
  type ScientificReportRevisionList,
  type ScientificReportView,
} from "../../app/lib/scientific-report-api";
import { formatScientificNarrativeNumbers, presentationScientificText } from "../../app/lib/scientific-presentation";
import { reportLimitationPresentation } from "../../app/lib/scientific-limitation-text";
import { ProductShell, RequireProductAuth } from "../../shared/layout/ProductShell";
import { useProductRouter } from "../../shared/layout/ProductNavigation";
import { ArtifactOpenLink } from "../../shared/ui/ArtifactOpenLink";
import { ArtifactDownloadLink } from "../../shared/ui/ArtifactDownloadLink";
import { ScientificReportArtifactPreview } from "./ScientificReportArtifactPreview";
import { ScientificReportBasis } from "./ScientificReportBasis";
import { boundReportBasis, reportParameterInputs } from "../../app/lib/scientific-report-basis";
import { readPlatformReferences } from "../../app/lib/platform-reference";
import { PlatformReferenceSources } from "../../shared/ui/PlatformReferenceSources";
import { ProjectInputDetails } from "../../shared/ui/ProjectInputDetails";
import { inputOriginNames, projectScienceNames } from "../../app/lib/project-science-labels";
import { readReportContent } from "./report-read";
import { scientificReportDownloadHref } from "../../app/lib/scientific-report-download";
import { reportFindingPresentation } from "../../app/lib/scientific-report-findings";
import styles from "./ReportDocument.module.css";

const LegacyReportReaderPage = dynamic(
  () => import("./ReportPages").then((module) => module.ReportReaderPage),
  {
    loading: () => (
      <section className="scientific-report-shell" aria-label="历史报告加载状态">
        <div className="product-loading" role="status" aria-live="polite">
          正在打开历史报告…
        </div>
      </section>
    ),
  },
);

function scrollToReportChapter(target: string) {
  const chapter = document.getElementById(target);
  if (!chapter) return;
  chapter.scrollIntoView({
    behavior: window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
    block: "start",
  });
  chapter.tabIndex = -1;
  chapter.focus({ preventScroll: true });
  window.history.replaceState(window.history.state, "", `#${target}`);
}

const relevanceCopy = {
  CURRENT: null,
  STALE: "这是基于历史数据版本生成的报告。当前项目中已有更新的数据版本。",
  SOURCE_MISSING: "该报告保留历史科学记录，但对应的原始数据版本当前不可访问。",
  INVALIDATED: "该报告仅作为历史记录，不应视为当前有效科学证据。",
} as const;

const lifecycleCopy = {
  ARCHIVED: {
    label: "已归档报告",
    body: "此报告已从当前工作列表归档，但其科学结果、证据与精确源版本保持可读。",
  },
  TRASHED: {
    label: "回收站报告",
    body: "此报告位于回收站；受保护的科学结果、证据与精确源版本未被删除。",
  },
} as const;

const sourceLifecycleCopy = {
  ARCHIVED: "来源对象已归档",
  TRASHED: "来源对象位于回收站",
  INVALIDATED: "来源对象已失效",
} as const;

/**
 * Historical run links use the persisted Job identity rather than a
 * ScientificReport id.  They are handled by the read-only compatibility
 * reader and should not first probe the modern report endpoint: that probe
 * can only produce a predictable 404 and console noise for a valid legacy
 * route.
 */
function isLegacyRunReference(value: string) {
  return /^(?:job|run)_[a-z0-9_-]+$/iu.test(value);
}

function sourceLifecycleLabel(status: string | undefined) {
  return sourceLifecycleCopy[status as keyof typeof sourceLifecycleCopy] || null;
}

export function ScientificReportRoute({ projectId, reportId }: { projectId: string; reportId: string }) {
  return <ScientificReportLoader key={`${projectId}:${reportId}`} projectId={projectId} reportId={reportId} />;
}

function ScientificReportLoader({ projectId, reportId }: { projectId: string; reportId: string }) {
  const router = useProductRouter();
  const [report, setReport] = useState<ScientificReportView | null>(null);
  const legacy = isLegacyRunReference(reportId);
  const [error, setError] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  useEffect(() => {
    if (legacy) return;
    const controller = new AbortController();
    setError(false);
    void readReportContent((signal) => getScientificReport(reportId, signal), controller.signal)
      .then((value) => {
        if (!value.report) throw new Error("Report body unavailable");
        if (!controller.signal.aborted) setReport(value);
      })
      .catch(() => {
        if (!controller.signal.aborted) setError(true);
      });
    return () => controller.abort();
  }, [reportId, legacy, reloadKey]);
  useEffect(() => {
    if (!report?.project_id || report.project_id === projectId) return;
    router.replace(
      `/projects/${encodeURIComponent(report.project_id)}/reports/${encodeURIComponent(report.report_id)}`,
    );
  }, [projectId, report, router]);
  if (legacy) return <LegacyReportReaderPage projectId={projectId} reportId={reportId} />;
  const authoritativeProjectId = report?.project_id || projectId;
  const isCorrectingProjectRoute = Boolean(
    report?.project_id && report.project_id !== projectId,
  );
  return <RequireProductAuth><ProductShell projectId={authoritativeProjectId}>
    {!report && !error ? <section className="scientific-report-shell" aria-label="科学报告加载状态"><div className="product-loading" role="status" aria-live="polite">正在打开科学报告…</div></section> : null}
    {error ? <section className="scientific-report-shell" aria-label="科学报告错误状态"><div className="product-state" role="alert"><h1>报告暂时无法打开</h1><p>未能读取报告正文。请重试，或返回报告列表确认访问权限与报告状态。</p><div className="product-row-actions"><button type="button" className="product-secondary-action" onClick={() => setReloadKey((key) => key + 1)}>重新加载报告</button><Link className="product-secondary-action" href={`/projects/${projectId}/reports`}>返回报告列表</Link></div></div></section> : null}
    {isCorrectingProjectRoute ? <section className="scientific-report-shell" aria-label="报告项目校正状态"><div className="product-loading" role="status" aria-live="polite">正在返回报告所属项目…</div></section> : null}
    {report?.report && !isCorrectingProjectRoute ? <ScientificReportDocument projectId={authoritativeProjectId} view={report} /> : null}
  </ProductShell></RequireProductAuth>;
}

function ScientificReportDocument({ projectId, view }: { projectId: string; view: ScientificReportView }) {
  const report = view.report!;
  const findingPresentation = reportFindingPresentation(report.main_findings);
  const [revisions, setRevisions] =
    useState<ScientificReportRevisionList | null>(null);
  const [comparison, setComparison] =
    useState<ScientificReportRevisionComparison | null>(null);
  const [revisionErrors, setRevisionErrors] = useState<string[]>([]);
  const [revisionBusy, setRevisionBusy] = useState(false);
  const [revisionReloadKey, setRevisionReloadKey] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setRevisionBusy(true);
    async function readRevisionPart<T>(label: string, request: (signal: AbortSignal) => Promise<T>, accept: (value: T) => void) {
      try {
        const value = await readReportContent(request, controller.signal);
        if (controller.signal.aborted) return;
        accept(value);
        setRevisionErrors((current) => current.filter((item) => item !== label));
      } catch {
        if (!controller.signal.aborted) setRevisionErrors((current) => current.includes(label) ? current : [...current, label]);
      }
    }
    void Promise.all([
      readRevisionPart("版本记录", (signal) => listScientificReportRevisions(view.report_id, signal), setRevisions),
      ...(view.revision_number && view.revision_number > 1
        ? [readRevisionPart("版本比较", (signal) => compareScientificReportRevisions(view.report_id, undefined, signal), setComparison)]
        : []),
    ]).then(() => {
      if (!controller.signal.aborted) setRevisionBusy(false);
    });
    return () => controller.abort();
  }, [view.report_id, view.revision_number, revisionReloadKey]);
  const warning = relevanceCopy[view.current_effective_relevance];
  const lifecycle = lifecycleCopy[
    String(view.lifecycle_status || "ACTIVE").toUpperCase() as keyof typeof lifecycleCopy
  ];
  const limitations = reportLimitationPresentation(report.limitations);
  const methodSummary = dedupeReportSentences(
    humanizeScientificMethodSummary(presentationScientificText(report.method_summary)),
  );
  const readableReportText = (value: string) =>
    normalizeReportNarrative(presentationScientificText(value));
  const readableReproducibilitySummary = readableReportText(report.reproducibility_summary);
  const referenceSources = readPlatformReferences(boundReportBasis(view)?.reference_sources);
  const parameterInputs = reportParameterInputs(view);
  const sourceCount = (view.viewer_sources?.length || report.data_sources.length) + referenceSources.length + parameterInputs.length;
  const sourceResearchHref = view.research_session_id
    ? `/projects/${projectId}/research/${encodeURIComponent(view.research_session_id)}?turn=${encodeURIComponent(view.research_turn_id)}`
    : `/projects/${projectId}/research?turn=${encodeURIComponent(view.research_turn_id)}`;
  const anchor = (section: string) => `report-${view.report_id}-${section}`;
  const reportSections = [
    { id: anchor("question"), label: "摘要" },
    { id: anchor("methods"), label: "数据与方法" },
    ...(report.main_findings.length ? [{ id: anchor("findings"), label: "主要发现" }] : []),
    ...(report.primary_figures.length ? [{ id: anchor("figures"), label: "图表" }] : []),
    ...(view.table_sources?.length ? [{ id: anchor("tables"), label: "数据表" }] : []),
    ...(report.discussion?.text ? [{ id: anchor("discussion"), label: "科学讨论" }] : []),
    { id: anchor("limitations"), label: "限制" },
    ...(report.conclusion?.text ? [{ id: anchor("conclusion"), label: "结论" }] : []),
    ...(report.next_steps?.text ? [{ id: anchor("next-steps"), label: "后续工作建议" }] : []),
  ];
  return <section className="scientific-report-shell" aria-label="科学报告阅读器">
    <article className={`scientific-report-document ${styles.document}`}>
      <nav className="scientific-report-back" aria-label="报告导航"><div className="scientific-report-back-primary"><Link href={`/projects/${projectId}/reports`}>返回报告</Link><Link className="product-primary-action" href={sourceResearchHref}>打开来源研究</Link></div><div className="scientific-report-back-secondary"><a className="product-secondary-action" data-testid="scientific-report-export-zip" href={scientificReportDownloadHref(view.report_id, "zip")} target="_blank" rel="noopener" title="打包正文、图表与原始数据；解压后打开 report.html 阅读">导出 ZIP（含图表）</a><a className="product-secondary-action" data-testid="scientific-report-export-markdown" href={scientificReportDownloadHref(view.report_id, "markdown")} target="_blank" rel="noopener" title="下载在新窗口处理，原报告保持打开">导出 Markdown</a><a className="product-secondary-action" data-testid="scientific-report-export-manifest" href={scientificReportDownloadHref(view.report_id, "manifest")} target="_blank" rel="noopener" title="下载在新窗口处理，原报告保持打开">导出复现清单</a></div></nav>
      <header className="scientific-report-masthead">
        <p className="product-kicker">经验证科学报告</p>
        <h1>{report.title}</h1>
        <p className="scientific-report-context">{new Date(view.created_at).toLocaleString("zh-CN")} · 第 {view.revision_number || 1} 版 · {report.main_findings.length} 项主要发现</p>
      </header>
      {(revisions && revisions.count > 1) || comparison || revisionErrors.length ? (
        <section
          className="scientific-report-revision-bar"
          aria-labelledby={anchor("revisions-heading")}
        >
          <div>
            <p className="product-kicker">不可变修订历史</p>
            <h2 id={anchor("revisions-heading")}>
              {revisions ? `${revisions.count} 个报告版本` : "报告版本"}
            </h2>
            <p>
              每个版本都保留同一精确 ScientificResult 与来源；打开或比较不会重新运行科学计算。
            </p>
          </div>
          {revisionErrors.length ? <div role="alert" className="scientific-report-revision-error">
            <p>未能读取：{revisionErrors.join("、")}。报告正文与已读取的版本信息仍可查看。</p>
            <button type="button" className="product-secondary-action" disabled={revisionBusy} onClick={() => setRevisionReloadKey((key) => key + 1)}>{revisionBusy ? "正在重新加载…" : "重新加载版本信息"}</button>
          </div> : null}
          {revisions ? <nav aria-label="报告修订版本">
            {revisions.items.map((item) => (
              <Link
                key={item.report_id}
                href={`/projects/${projectId}/reports/${item.report_id}`}
                aria-current={
                  item.report_id === view.report_id ? "page" : undefined
                }
              >
                第 {item.revision_number || 1} 版
              </Link>
            ))}
          </nav> : null}
          {comparison ? (
            <details className="scientific-report-revision-comparison">
              <summary>
                与第 {comparison.base_revision_number} 版比较
              </summary>
              <p>
                科学权威
                {comparison.scientific_authority_unchanged
                  ? "未改变"
                  : "发生变化"}
                ；精确源版本
                {comparison.source_versions_unchanged
                  ? "未改变"
                  : "发生变化"}。
              </p>
              <p>
                {comparison.changed_sections.length
                  ? `沟通层变化：${comparison.changed_sections.join("、")}`
                  : "报告科学内容一致；本修订用于独立命名、组织或后续沟通。"}
              </p>
              {comparison.added_findings.length ||
              comparison.removed_findings.length ? (
                <ul>
                  {comparison.added_findings.map((finding) => (
                    <li key={`added:${finding}`}>新增发现：{finding}</li>
                  ))}
                  {comparison.removed_findings.map((finding) => (
                    <li key={`removed:${finding}`}>移除发现：{finding}</li>
                  ))}
                </ul>
              ) : null}
            </details>
          ) : null}
        </section>
      ) : null}
      <nav className="scientific-report-contents" aria-label="报告章节">
        <span>章节</span>
        {reportSections.map((section) => (
          <a key={section.id} href={`#${section.id}`} onClick={(event) => {
            if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
            event.preventDefault();
            scrollToReportChapter(section.id);
          }}>{section.label}</a>
        ))}
        <label className="scientific-report-contents-select">
          <span>跳转章节</span>
          <select
            aria-label="跳转报告章节"
            defaultValue=""
            onChange={(event) => {
              const target = event.target.value;
              if (!target) return;
              scrollToReportChapter(target);
              event.target.value = "";
            }}
          >
            <option value="" disabled>选择章节</option>
            {reportSections.map((section) => (
              <option key={section.id} value={section.id}>{section.label}</option>
            ))}
          </select>
        </label>
        <small className="scientific-report-contents-hint" role="note">
          移动端可左右滑动或选择章节
        </small>
      </nav>
      {lifecycle ? <aside className={`scientific-report-status is-${String(view.lifecycle_status).toLowerCase()}`} role="note"><strong>{lifecycle.label}</strong><p>{lifecycle.body}</p></aside> : null}
      {warning ? <aside className={`scientific-report-status is-${view.current_effective_relevance.toLowerCase()}`} role="note"><strong>{view.current_effective_relevance === "STALE" ? "历史版本" : "来源状态提示"}</strong><p>{warning}</p></aside> : null}
      <section id={anchor("question")} className="scientific-report-lead" aria-labelledby={`${anchor("question")}-heading`}>
        <h2 id={`${anchor("question")}-heading`}>摘要</h2>
        <p>{readableReportText(report.summary)}</p>
        <details className={styles.question}><summary>研究问题</summary><p>{report.research_question}</p></details>
      </section>
      <section id={anchor("methods")} className="scientific-report-methods" aria-labelledby={`${anchor("methods")}-heading`}>
        <h2 id={`${anchor("methods")}-heading`}>数据与方法</h2><p>{methodSummary}</p>
        {view.viewer_sources?.length ? <ul className="scientific-report-sources">{view.viewer_sources.map((source) => { const sourceLifecycle = sourceLifecycleLabel(source.lifecycle_status); return <li key={`${source.object_id}:${source.version_id}`}><Link href={`/projects/${encodeURIComponent(projectId)}/data?object=${encodeURIComponent(source.object_id)}&version=${encodeURIComponent(source.version_id)}`}>{source.display_name}</Link><span>{humanizeSourceType(source.object_type)}{source.is_current_version ? " · 当前版本" : " · 历史版本"}{sourceLifecycle ? ` · ${sourceLifecycle}` : ""}</span></li>; })}</ul>
          : referenceSources.length || parameterInputs.length ? null : <p className="scientific-report-source-fallback">{report.data_sources.length ? "报告保留了来源引用；当前页面未返回可展示的对象版本摘要。" : "输入来源暂不可读取。"}</p>}
        <ProjectInputDetails provenance={{ execution_scope: "PROJECT", input_origin: boundReportBasis(view)?.input_origin, parameter_inputs: parameterInputs }} />
        <PlatformReferenceSources sources={referenceSources} />
      </section>
      <section id={anchor("findings")} className="scientific-report-findings" aria-labelledby={`${anchor("findings")}-heading`}><h2 id={`${anchor("findings")}-heading`}>主要发现</h2>
        {findingPresentation.sharedLimitations.length ? <p className={styles.sharedLimitation} role="note" aria-label="共同限制">共同限制：{readableReportText(findingPresentation.sharedLimitations.join(""))}</p> : null}
        <ol>{report.main_findings.map((finding, index) => {
        return <li key={`${finding.statement}-${index}`}><div className="scientific-report-finding-body"><p>{readableReportText(findingPresentation.statements[index])}</p>
          <ScientificReportBasis view={view} references={finding} originalStatement={findingPresentation.statements[index] !== finding.statement || formatScientificNarrativeNumbers(finding.statement) !== finding.statement ? finding.statement : undefined} />
        </div></li>;
      })}</ol></section>
      {report.primary_figures.length ? <section id={anchor("figures")} className="scientific-report-figures" aria-labelledby={`${anchor("figures")}-heading`}><h2 id={`${anchor("figures")}-heading`}>主要图表</h2>{report.primary_figures.map((figure, index) => {
        const matchingSources = (view.figure_sources || []).filter((candidate) => candidate.figure_ref === figure.figure_ref);
        const figureSource = matchingSources.length === 1 ? matchingSources[0] : null;
        const artifactId = figureSource?.artifact_ids?.[0];
        const artifactHref = artifactId && figureSource?.job_id
          ? `/api/planner/jobs/${encodeURIComponent(figureSource.job_id)}/artifacts/${encodeURIComponent(artifactId)}/content`
          : null;
        return <figure key={figure.figure_ref} className="scientific-report-figure-plate" data-figure-ref={figure.figure_ref}>
          <figcaption><span>图表 {index + 1}</span><strong>{readableReportText(figure.caption)}</strong></figcaption>
          {!artifactHref ? <p>此图表暂未提供可预览的文件，可返回来源研究查看。</p> : null}
          {artifactHref ? <ScientificReportArtifactPreview jobId={figureSource!.job_id!} artifactId={artifactId!} kind="figure" title={readableReportText(figure.caption)}
            viewer={figureSource?.renderer === "volumetric" ? { projectId, artifacts: figureSource.artifacts || [] } : undefined} /> : null}
          <div className="scientific-report-artifact-actions">
            {artifactHref ? <>
              <ArtifactOpenLink href={artifactHref}>查看源文件</ArtifactOpenLink>
              <ArtifactDownloadLink href={artifactHref} downloadName={`${figure.figure_ref}.figure.json`}>下载</ArtifactDownloadLink>
            </> : figureSource?.object_id && figureSource.version_id ? <Link href={`/projects/${encodeURIComponent(projectId)}/data?object=${encodeURIComponent(figureSource.object_id)}&version=${encodeURIComponent(figureSource.version_id)}`}>在科学视图中查看</Link> : <Link href={sourceResearchHref}>打开来源研究</Link>}
          </div>
        </figure>;
      })}</section> : null}
      {view.table_sources?.length ? <section id={anchor("tables")} className="scientific-report-tables" aria-labelledby={`${anchor("tables")}-heading`}><h2 id={`${anchor("tables")}-heading`}>主要数据表</h2><div className="scientific-report-table-list">{view.table_sources.map((table, index) => {
        const artifactId = table.artifact_ids[0];
        const artifactHref = artifactId && table.job_id
          ? `/api/planner/jobs/${encodeURIComponent(table.job_id)}/artifacts/${encodeURIComponent(artifactId)}/content`
          : null;
        const tableTitle = table.title || `数据表 ${index + 1}`;
        return <article key={table.table_ref} className="scientific-report-table-card">
          <header><span>表格 {index + 1}</span><h3>{tableTitle}</h3></header>
          {artifactHref ? <ScientificReportArtifactPreview jobId={table.job_id!} artifactId={artifactId!} kind="table" title={tableTitle} /> : <p>此数据表暂未提供可预览的文件。</p>}
          <div className="scientific-report-artifact-actions">
            {artifactHref ? <>
              <ArtifactOpenLink href={artifactHref}>查看源文件</ArtifactOpenLink>
              <ArtifactDownloadLink href={artifactHref} downloadName={`${table.table_ref}.table.json`}>下载</ArtifactDownloadLink>
            </> : <Link href={sourceResearchHref}>打开来源研究</Link>}
          </div>
          <details className={styles.sourceDetails}><summary>来源详情</summary><dl>
            <div><dt>数据表标识</dt><dd>{table.table_ref}</dd></div>
            {table.source_refs?.map(source => <div key={`${source.object_id}:${source.version_id}`}><dt>精确版本</dt><dd><Link href={`/projects/${encodeURIComponent(projectId)}/data?object=${encodeURIComponent(source.object_id)}&version=${encodeURIComponent(source.version_id)}`}>{source.version_id}</Link></dd></div>)}
          </dl></details>
        </article>;
      })}</div></section> : null}
      {view.file_sources?.length ? <details className="scientific-report-tables"><summary>结果文件 · {view.file_sources.length} 项</summary><ul>{view.file_sources.map((file) => {
        const href = file.job_id ? `/api/planner/jobs/${encodeURIComponent(file.job_id)}/artifacts/${encodeURIComponent(file.artifact_id)}/content` : null;
        return <li key={file.artifact_id}><span>{file.title}</span><div className="scientific-report-artifact-actions">{href ? <><ArtifactOpenLink href={href}>查看源文件</ArtifactOpenLink><ArtifactDownloadLink href={href} downloadName={`${file.artifact_id}.json`}>下载</ArtifactDownloadLink></> : <Link href={sourceResearchHref}>打开来源研究</Link>}</div></li>;
      })}</ul></details> : null}
      {report.discussion?.text ? <section id={anchor("discussion")} className="scientific-report-discussion" aria-labelledby={`${anchor("discussion")}-heading`}><h2 id={`${anchor("discussion")}-heading`}>科学讨论</h2><p>{readableReportText(report.discussion.text)}</p><ScientificReportBasis view={view} references={report.discussion} /></section> : null}
      <section id={anchor("limitations")} className="scientific-report-limitations" aria-labelledby={`${anchor("limitations")}-heading`}><h2 id={`${anchor("limitations")}-heading`}>限制与适用范围</h2>{limitations.length ? <ul>{limitations.map((item) => <li key={item.statement}>{item.statement}</li>)}</ul> : <p>未记录额外限制；结论仍只适用于本报告绑定的精确源版本。</p>}</section>
      {report.conclusion?.text ? <section id={anchor("conclusion")} className="scientific-report-conclusion" aria-labelledby={`${anchor("conclusion")}-heading`}><h2 id={`${anchor("conclusion")}-heading`}>结论</h2><p>{readableReportText(report.conclusion.text)}</p><ScientificReportBasis view={view} references={report.conclusion} /></section> : null}
      {report.next_steps?.text ? <section id={anchor("next-steps")} className="scientific-report-next-steps" aria-labelledby={`${anchor("next-steps")}-heading`}><h2 id={`${anchor("next-steps")}-heading`}>后续工作建议</h2><p>{readableReportText(report.next_steps.text)}</p><ScientificReportBasis view={view} references={report.next_steps} /></section> : null}
      {report.supporting_results.length ? <section className="scientific-report-supporting" aria-labelledby="report-supporting"><h2 id="report-supporting">支持结果</h2><div>{report.supporting_results.map((item) => <article key={item.result_item_ref}><strong>{item.description}</strong><span>已验证 supporting result</span></article>)}</div></section> : null}
      <section className="scientific-report-disclosures" aria-label="报告依据与复现信息">
        <ScientificReportBasis view={view} references={{ evidence_refs: report.evidence_refs }} label={`科学依据 · ${report.evidence_refs.length}`} />
        <details><summary>来源数据 · {sourceCount}</summary><ul>{view.viewer_sources?.length ? view.viewer_sources.map((source) => { const sourceLifecycle = sourceLifecycleLabel(source.lifecycle_status); return <li key={source.source_ref}><strong>{source.display_name}</strong> · 精确版本 {source.version_id}{sourceLifecycle ? ` · ${sourceLifecycle}` : ""}</li>; }) : report.data_sources.map((source) => <li key={source}>已授权精确源版本</li>)}{referenceSources.map(source => <li key={source.referenceId}>{source.name} · {source.version}</li>)}{parameterInputs.map(input => <li key={input.tool_call_id}>{projectScienceNames[input.tool_id]} · {inputOriginNames[input.input_origin]}</li>)}</ul></details>
        <details><summary>复现信息</summary><p>{readableReproducibilitySummary}</p><p className="scientific-report-technical">报告契约 {report.contract_version} · 系统校验已通过</p></details>
        <details className="scientific-report-technical-details">
          <summary>技术详情（用于复现与排查）</summary>
          <p>这些标识用于定位已保存的科学记录，不会改变报告内容，也不会在打开报告时重新执行分析。</p>
          <dl>
            <div><dt>报告</dt><dd><code>{view.report_id}</code></dd></div>
            <div><dt>报告快照</dt><dd><code>{view.snapshot_id}</code></dd></div>
            <div><dt>研究回合</dt><dd><code>{view.research_turn_id}</code></dd></div>
            <div><dt>ScientificResult</dt><dd><code>{view.scientific_result_snapshot_id}</code></dd></div>
            <div><dt>精确来源</dt><dd>{[
              ...(view.viewer_sources || []).map(source => `${source.object_id} / ${source.version_id}`),
              ...referenceSources.map(source => `${source.name} / ${source.version} / SHA256 ${source.contentHash}`),
              ...parameterInputs.map(input => `${projectScienceNames[input.tool_id]} / SHA256 ${input.content_hash}`),
            ].join("；") || "报告中未返回来源摘要"}</dd></div>
          </dl>
        </details>
      </section>
    </article>
  </section>;
}

function normalizeReportNarrative(value: string): string {
  return value
    .replaceAll("。；", "；")
    .replaceAll("；。", "。")
    .replaceAll("。。", "。")
    .trim();
}

function humanizeSourceType(value: string): string {
  const labels: Record<string, string> = {
    "materials.table": "材料数据表",
    "structure.crystal": "晶体结构",
    "electronic.band": "电子能带",
    "electronic.dos": "电子态密度",
    "trajectory.extxyz": "原子轨迹",
  };
  return labels[value] || value;
}
