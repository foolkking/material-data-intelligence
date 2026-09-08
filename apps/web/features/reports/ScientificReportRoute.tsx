"use client";

import { ProductLink as Link } from "../../app/components/ProductNavigation";
import dynamic from "next/dynamic";
import React, { useEffect, useState } from "react";
import {
  buildScientificReportMarkdown,
  buildScientificReportReproducibilityManifest,
  compareScientificReportRevisions,
  getScientificReport,
  humanizeScientificMethodSummary,
  listScientificReportRevisions,
  type ScientificReportRevisionComparison,
  type ScientificReportRevisionList,
  type ScientificReportView,
} from "../../app/lib/scientific-report-api";
import { compileReportPresentation, presentationLimitationText, presentationScientificText } from "../../app/lib/scientific-presentation";
import { ProductShell, RequireProductAuth } from "../../app/components/ProductShell";
import { useProductRouter } from "../../app/components/ProductNavigation";
import { ScientificPresentationBlocks } from "../../app/components/ScientificPresentationBlocks";
import { ArtifactOpenLink } from "../../app/components/ArtifactOpenLink";
import { ArtifactDownloadLink } from "../../app/components/ArtifactDownloadLink";
import { ScientificReportArtifactPreview } from "../../app/components/ScientificReportArtifactPreview";

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
  const router = useProductRouter();
  const [report, setReport] = useState<ScientificReportView | null>(null);
  const [legacy, setLegacy] = useState(false);
  const [error, setError] = useState(false);
  useEffect(() => {
    let active = true;
    if (isLegacyRunReference(reportId)) {
      setLegacy(true);
      return () => { active = false; };
    }
    void getScientificReport(reportId)
      .then((value) => { if (active) setReport(value); })
      .catch((reason: Error & { status?: number }) => {
        if (!active) return;
        if (reason.status === 404) setLegacy(true);
        else setError(true);
    });
    return () => { active = false; };
  }, [reportId]);
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
    {error ? <section className="scientific-report-shell" aria-label="科学报告错误状态"><div className="product-state" role="alert"><h1>报告暂时无法打开</h1><p>已生成的报告仍保存在项目中，请稍后重试。</p><Link className="product-secondary-action" href={`/projects/${projectId}/reports`}>返回报告列表</Link></div></section> : null}
    {isCorrectingProjectRoute ? <section className="scientific-report-shell" aria-label="报告项目校正状态"><div className="product-loading" role="status" aria-live="polite">正在返回报告所属项目…</div></section> : null}
    {report?.report && !isCorrectingProjectRoute ? <ScientificReportDocument projectId={authoritativeProjectId} view={report} /> : null}
  </ProductShell></RequireProductAuth>;
}

function ScientificReportDocument({ projectId, view }: { projectId: string; view: ScientificReportView }) {
  const report = view.report!;
  const [exportStatus, setExportStatus] = useState<"idle" | "markdown" | "manifest" | "error">("idle");
  const [revisions, setRevisions] =
    useState<ScientificReportRevisionList | null>(null);
  const [comparison, setComparison] =
    useState<ScientificReportRevisionComparison | null>(null);
  useEffect(() => {
    let active = true;
    void listScientificReportRevisions(view.report_id)
      .then((value) => {
        if (!active) return;
        setRevisions(value);
        if ((view.revision_number || 1) > 1) {
          void compareScientificReportRevisions(view.report_id)
            .then((result) => {
              if (active) setComparison(result);
            })
            .catch(() => {
              if (active) setComparison(null);
            });
        }
      })
      .catch(() => {
        if (active) setRevisions(null);
      });
    return () => {
      active = false;
    };
  }, [view.report_id, view.revision_number]);
  const warning = relevanceCopy[view.current_effective_relevance];
  const lifecycle = lifecycleCopy[
    String(view.lifecycle_status || "ACTIVE").toUpperCase() as keyof typeof lifecycleCopy
  ];
  const limitations = report.limitations
    .map((item) => ({ ...item, statement: presentationLimitationText(item.statement) }))
    .filter((item, index, items) => items.findIndex((candidate) => candidate.statement.trim().toLocaleLowerCase() === item.statement.trim().toLocaleLowerCase()) === index);
  const methodSummary = dedupeReportSentences(
    humanizeScientificMethodSummary(presentationScientificText(report.method_summary)),
  );
  const readableReportText = (value: string) =>
    normalizeReportNarrative(presentationScientificText(value));
  const readableReproducibilitySummary = readableReportText(report.reproducibility_summary)
    .replaceAll("exact source version", "精确源版本")
    .replaceAll("exact source versions", "精确源版本");
  const presentation = compileReportPresentation(view);
  const sourceCount = view.viewer_sources?.length || report.data_sources.length;
  const sourceResearchHref = view.research_session_id
    ? `/projects/${projectId}/research/${encodeURIComponent(view.research_session_id)}?turn=${encodeURIComponent(view.research_turn_id)}`
    : `/projects/${projectId}/research?turn=${encodeURIComponent(view.research_turn_id)}`;
  const exportBlob = (contents: string, mimeType: string, filename: string, status: "markdown" | "manifest") => {
    try {
      const createObjectURL = URL.createObjectURL;
      if (typeof createObjectURL !== "function") throw new Error("下载能力不可用");
      const url = createObjectURL.call(URL, new Blob([contents], { type: mimeType }));
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      anchor.rel = "noopener";
      anchor.style.display = "none";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      setExportStatus(status);
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch {
      setExportStatus("error");
    }
  };
  const downloadMarkdown = () => exportBlob(
    buildScientificReportMarkdown(view),
    "text/markdown;charset=utf-8",
    `${report.title.replace(/[^\w\u4e00-\u9fff.-]+/g, "-").slice(0, 96) || "scientific-report"}.md`,
    "markdown",
  );
  const downloadReproducibilityManifest = () => exportBlob(
    buildScientificReportReproducibilityManifest(view),
    "application/json;charset=utf-8",
    `${report.title.replace(/[^\w\u4e00-\u9fff.-]+/g, "-").slice(0, 96) || "scientific-report"}-reproducibility.json`,
    "manifest",
  );
  const anchor = (section: string) => `report-${view.report_id}-${section}`;
  const reportSections = [
    { id: anchor("question"), label: "研究问题" },
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
    <article className="scientific-report-document">
      <nav className="scientific-report-back" aria-label="报告导航"><div className="scientific-report-back-primary"><Link href={`/projects/${projectId}/reports`}>返回报告</Link><Link className="product-primary-action" href={sourceResearchHref}>打开来源研究</Link></div><div className="scientific-report-back-secondary"><button type="button" className="product-secondary-action" data-testid="scientific-report-export-markdown" onClick={downloadMarkdown}>导出 Markdown</button><button type="button" className="product-secondary-action" data-testid="scientific-report-export-manifest" onClick={downloadReproducibilityManifest}>导出复现清单</button></div>{exportStatus !== "idle" ? <span className="scientific-report-export-status" role="status" aria-label="报告导出状态" aria-live="polite">{exportStatus === "markdown" ? "Markdown 已准备下载" : exportStatus === "manifest" ? "复现清单已准备下载" : "导出失败，请稍后重试"}</span> : null}</nav>
      <header className="scientific-report-masthead">
        <p className="product-kicker">经验证科学报告</p>
        <h1>{report.title}</h1>
        <p className="scientific-report-context">{new Date(view.created_at).toLocaleString("zh-CN")} · 第 {view.revision_number || 1} 版 · {report.main_findings.length} 项主要发现</p>
      </header>
      {revisions && revisions.count > 1 ? (
        <section
          className="scientific-report-revision-bar"
          aria-labelledby={anchor("revisions-heading")}
        >
          <div>
            <p className="product-kicker">不可变修订历史</p>
            <h2 id={anchor("revisions-heading")}>
              {revisions.count} 个报告版本
            </h2>
            <p>
              每个版本都保留同一精确 ScientificResult 与来源；打开或比较不会重新运行科学计算。
            </p>
          </div>
          <nav aria-label="报告修订版本">
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
          </nav>
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
          <a key={section.id} href={`#${section.id}`}>{section.label}</a>
        ))}
        <label className="scientific-report-contents-select">
          <span>跳转章节</span>
          <select
            aria-label="跳转报告章节"
            defaultValue=""
            onChange={(event) => {
              const target = event.target.value;
              if (!target) return;
              document.getElementById(target)?.scrollIntoView({
                behavior: "smooth",
                block: "start",
              });
              window.history.replaceState(null, "", `#${target}`);
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
      <section id={anchor("question")} className="scientific-report-lead" aria-labelledby={`${anchor("question")}-heading`}><p className="product-kicker">研究问题</p><h2 id={`${anchor("question")}-heading`}>{readableReportText(report.research_question)}</h2><p>{readableReportText(report.summary)}</p></section>
      <section id={anchor("methods")} className="scientific-report-methods" aria-labelledby={`${anchor("methods")}-heading`}><h2 id={`${anchor("methods")}-heading`}>数据与方法</h2><p>{methodSummary}</p>{view.viewer_sources?.length ? <ul className="scientific-report-sources">{view.viewer_sources.map((source) => { const sourceLifecycle = sourceLifecycleLabel(source.lifecycle_status); return <li key={`${source.object_id}:${source.version_id}`}><strong>{source.display_name}</strong><span>{humanizeSourceType(source.object_type)} · 版本 {source.version_id}{source.is_current_version ? " · 当前版本" : " · 历史版本"}{sourceLifecycle ? ` · ${sourceLifecycle}` : ""}</span></li>; })}</ul> : <p className="scientific-report-source-fallback">报告保留了来源引用；当前页面未返回可展示的对象版本摘要。</p>}</section>
      <ScientificPresentationBlocks presentation={presentation} mode="report_supplement" projectId={projectId} instanceId={view.report_id} />
      {report.discussion?.text ? <section id={anchor("discussion")} className="scientific-report-discussion" aria-labelledby={`${anchor("discussion")}-heading`}><h2 id={`${anchor("discussion")}-heading`}>科学讨论</h2><p>{readableReportText(report.discussion.text)}</p></section> : null}
      {report.primary_figures.length ? <section id={anchor("figures")} className="scientific-report-figures" aria-labelledby={`${anchor("figures")}-heading`}><h2 id={`${anchor("figures")}-heading`}>主要图表</h2>{report.primary_figures.map((figure, index) => {
        const figureSource = (view.figure_sources || []).find((candidate) => candidate.figure_ref === figure.figure_ref);
        const artifactId = figureSource?.artifact_ids?.[0];
        const artifactHref = artifactId && figureSource?.job_id
          ? `/api/planner/jobs/${encodeURIComponent(figureSource.job_id)}/artifacts/${encodeURIComponent(artifactId)}/content`
          : null;
        return <figure key={figure.figure_ref}><div className="scientific-report-figure-plate" data-figure-ref={figure.figure_ref}><span>{String(index + 1).padStart(2, "0")}</span><strong>{readableReportText(figure.caption)}</strong><p>{artifactHref ? "已绑定持久化 Artifact；打开或下载不会重新执行科学计算。" : "交互图形和完整数据保留在对应的 Scientific Result 中。"}</p>{artifactHref ? <ScientificReportArtifactPreview jobId={figureSource!.job_id!} artifactId={artifactId!} kind="figure" title={readableReportText(figure.caption)} /> : null}{artifactHref ? <><ArtifactOpenLink href={artifactHref}>打开权威 Artifact</ArtifactOpenLink><ArtifactDownloadLink href={artifactHref} downloadName={`${figure.figure_ref}.figure.json`}>下载权威 Artifact</ArtifactDownloadLink></> : view.viewer_sources?.[0] ? <Link href={`/projects/${projectId}/data?object=${encodeURIComponent(view.viewer_sources[0].object_id)}&version=${encodeURIComponent(view.viewer_sources[0].version_id)}&name=${encodeURIComponent(view.viewer_sources[0].display_name)}`}>在科学视图中查看</Link> : <Link href={sourceResearchHref}>打开对应科学结果</Link>}</div><figcaption>图表 {index + 1} · {readableReportText(figure.caption)}</figcaption></figure>;
      })}</section> : null}
      {view.table_sources?.length ? <section id={anchor("tables")} className="scientific-report-tables" aria-labelledby={`${anchor("tables")}-heading`}><h2 id={`${anchor("tables")}-heading`}>主要数据表</h2><div className="scientific-report-table-list">{view.table_sources.map((table, index) => {
        const artifactId = table.artifact_ids[0];
        const artifactHref = artifactId && table.job_id
          ? `/api/planner/jobs/${encodeURIComponent(table.job_id)}/artifacts/${encodeURIComponent(artifactId)}/content`
          : null;
        const sourceLabel = table.source_refs?.length
          ? `精确版本 ${table.source_refs.map((source) => source.version_id).join("、")}`
          : "来自 ScientificResult";
        return <article key={table.table_ref} className="scientific-report-table-card"><div><span>表格 {String(index + 1).padStart(2, "0")}</span><strong>{table.title || table.table_ref}</strong>{table.title && table.title !== table.table_ref ? <small>{table.table_ref}</small> : null}<p>{sourceLabel} · 读取或下载已持久化数据，不会重新执行科学计算。</p>{artifactHref ? <ScientificReportArtifactPreview jobId={table.job_id!} artifactId={artifactId!} kind="table" title={table.title || table.table_ref} /> : null}</div>{artifactHref ? <><ArtifactOpenLink href={artifactHref}>打开权威数据表</ArtifactOpenLink><ArtifactDownloadLink href={artifactHref} downloadName={`${table.table_ref}.table.json`}>下载权威数据表</ArtifactDownloadLink></> : <Link href={sourceResearchHref}>打开来源研究</Link>}</article>;
      })}</div></section> : null}
      <section id={anchor("findings")} className="scientific-report-findings" aria-labelledby={`${anchor("findings")}-heading`}><h2 id={`${anchor("findings")}-heading`}>主要发现</h2><ol>{report.main_findings.map((finding, index) => {
        const exactSource = view.viewer_sources?.[0];
        const factRefs = [...new Set(finding.fact_refs || [])];
        const evidenceRefs = [...new Set(finding.evidence_refs || [])];
        const findingRefs = [...new Set(finding.finding_refs || [])];
        return <li key={`${finding.statement}-${index}`}><span>{String(index + 1).padStart(2, "0")}</span><div className="scientific-report-finding-body"><p>{readableReportText(finding.statement)}</p><details className="scientific-report-finding-evidence"><summary>查看科学依据</summary><dl>
          <div><dt>ScientificResult</dt><dd><code>{view.scientific_result_snapshot_id}</code></dd></div>
          {exactSource ? <div><dt>精确来源</dt><dd>{exactSource.display_name} · {exactSource.version_id}{exactSource.lifecycle_status === "ARCHIVED" ? " · 来源对象已归档" : ""}</dd></div> : null}
          <div><dt>Result 事实</dt><dd>{factRefs.length ? factRefs.map((ref) => <code key={ref}>{ref}</code>) : "该发现未声明独立 fact ref；仍受报告 grounding 校验约束。"}</dd></div>
          <div><dt>证据</dt><dd>{evidenceRefs.length ? evidenceRefs.map((ref) => <code key={ref}>{ref}</code>) : "该发现未声明独立 evidence ref。"}</dd></div>
          {findingRefs.length ? <div><dt>发现引用</dt><dd>{findingRefs.map((ref) => <code key={ref}>{ref}</code>)}</dd></div> : null}
        </dl></details></div></li>;
      })}</ol></section>
      <section id={anchor("limitations")} className="scientific-report-limitations" aria-labelledby={`${anchor("limitations")}-heading`}><h2 id={`${anchor("limitations")}-heading`}>限制与适用范围</h2>{limitations.length ? <ul>{limitations.map((item) => <li key={item.statement}>{item.statement}</li>)}</ul> : <p>未记录额外限制；结论仍只适用于本报告绑定的精确源版本。</p>}</section>
      {report.conclusion?.text ? <section id={anchor("conclusion")} className="scientific-report-conclusion" aria-labelledby={`${anchor("conclusion")}-heading`}><h2 id={`${anchor("conclusion")}-heading`}>结论</h2><p>{readableReportText(report.conclusion.text)}</p></section> : null}
      {report.next_steps?.text ? <section id={anchor("next-steps")} className="scientific-report-next-steps" aria-labelledby={`${anchor("next-steps")}-heading`}><h2 id={`${anchor("next-steps")}-heading`}>后续工作建议</h2><p>{readableReportText(report.next_steps.text)}</p></section> : null}
      {report.supporting_results.length ? <section className="scientific-report-supporting" aria-labelledby="report-supporting"><h2 id="report-supporting">支持结果</h2><div>{report.supporting_results.map((item) => <article key={item.result_item_ref}><strong>{item.description}</strong><span>已验证 supporting result</span></article>)}</div></section> : null}
      <section className="scientific-report-disclosures" aria-label="报告依据与复现信息">
        <details><summary>科学依据 · {report.evidence_refs.length}</summary><p>所有发现与图表引用均已通过 ReportGroundingValidator，并绑定到同一 ScientificResult。</p></details>
        <details><summary>来源数据 · {sourceCount}</summary><ul>{view.viewer_sources?.length ? view.viewer_sources.map((source) => { const sourceLifecycle = sourceLifecycleLabel(source.lifecycle_status); return <li key={source.source_ref}><strong>{source.display_name}</strong> · 精确版本 {source.version_id}{sourceLifecycle ? ` · ${sourceLifecycle}` : ""}</li>; }) : report.data_sources.map((source) => <li key={source}>已授权精确源版本</li>)}</ul></details>
        <details><summary>复现信息</summary><p>{readableReproducibilitySummary}</p><p className="scientific-report-technical">报告契约 {report.contract_version} · 系统校验已通过</p></details>
        <details className="scientific-report-technical-details">
          <summary>技术详情（用于复现与排查）</summary>
          <p>这些标识用于定位已保存的科学记录，不会改变报告内容，也不会在打开报告时重新执行分析。</p>
          <dl>
            <div><dt>报告</dt><dd><code>{view.report_id}</code></dd></div>
            <div><dt>报告快照</dt><dd><code>{view.snapshot_id}</code></dd></div>
            <div><dt>研究回合</dt><dd><code>{view.research_turn_id}</code></dd></div>
            <div><dt>ScientificResult</dt><dd><code>{view.scientific_result_snapshot_id}</code></dd></div>
            <div><dt>精确来源</dt><dd>{view.viewer_sources?.length ? view.viewer_sources.map((source) => `${source.object_id} / ${source.version_id}`).join("；") : "报告中未返回来源摘要"}</dd></div>
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

function dedupeReportSentences(value: string): string {
  const sentences = value.match(/[^。！？!?]*[。！？!?]|[^。！？!?]+$/gu) || [];
  const seen = new Set<string>();
  return sentences
    .map((sentence) => sentence.trim())
    .filter((sentence) => {
      const key = sentence.toLocaleLowerCase();
      if (!sentence || seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .join("")
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
