"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getProjectHistory, type ProjectHistory } from "../lib/planner-api";
import { researchRunTitle } from "../lib/research-display";
import { listScientificReports, type ScientificReportView } from "../lib/scientific-report-api";
import { ProductShell, RequireProductAuth } from "./ProductShell";

export function ScientificReportsIndexPage({ projectId }: { projectId: string }) {
  const [grounded, setGrounded] = useState<ScientificReportView[]>([]);
  const [history, setHistory] = useState<ProjectHistory | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  useEffect(() => {
    let active = true;
    void Promise.allSettled([listScientificReports(projectId), getProjectHistory(projectId)]).then(([reports, legacy]) => {
      if (!active) return;
      if (reports.status === "fulfilled") setGrounded(reports.value.items);
      if (legacy.status === "fulfilled") setHistory(legacy.value);
      setState(reports.status === "fulfilled" || legacy.status === "fulfilled" ? "ready" : "error");
    });
    return () => { active = false; };
  }, [projectId]);
  const legacyReports = history?.analyses.filter((item) => item.visibleInReports !== false && (item.reportCount > 0 || ["completed", "succeeded", "success"].includes(item.status.toLowerCase()))) || [];
  return <RequireProductAuth><ProductShell projectId={projectId}><main className="document-page scientific-report-index">
    <header className="product-page-heading"><p className="product-kicker">Project Reports</p><h1>科学报告</h1><p>将已验证的研究结果整理为可阅读、可引用、可复现的持久科学记录。</p></header>
    {state === "loading" ? <div className="product-loading" role="status" aria-live="polite">正在加载项目报告…</div> : null}
    {state === "error" ? <div className="product-state" role="alert"><h2>报告列表暂时无法加载</h2><p>已生成的报告仍保存在项目中，请检查服务连接后重试。</p></div> : null}
    {state === "ready" ? <>
      <section className="scientific-report-index-section" aria-labelledby="grounded-reports"><div className="scientific-report-index-heading"><div><p className="product-kicker">Grounded Reports</p><h2 id="grounded-reports">已验证科学报告</h2></div><span>{grounded.length} 份</span></div>
        <div className="report-list">{grounded.map((report) => <Link className="report-list-row scientific-report-list-row" key={report.report_id} href={`/projects/${projectId}/reports/${report.report_id}`}><div><span className="product-kicker">{report.current_effective_relevance === "CURRENT" ? "当前结果" : "历史结果"}</span><h3>{report.title}</h3><p>{report.scientific_context}</p><p>{new Date(report.created_at).toLocaleString("zh-CN")} · {report.finding_count} 项主要发现{report.figure_count ? ` · ${report.figure_count} 幅图` : ""}</p></div><span>阅读报告</span></Link>)}{grounded.length === 0 ? <div className="product-state"><h3>还没有已验证科学报告</h3><p>在完成科学解释后，可从研究会话按需生成报告。</p></div> : null}</div>
      </section>
      {legacyReports.length ? <section className="scientific-report-index-section" aria-labelledby="legacy-reports"><div className="scientific-report-index-heading"><div><p className="product-kicker">Legacy Reports</p><h2 id="legacy-reports">历史运行报告</h2></div><span>{legacyReports.length} 份</span></div><div className="report-list">{legacyReports.map((run) => { const dataset = history?.datasets.find((item) => item.datasetId === run.datasetId); const contextLabel = run.researchContextKind === "RESEARCH_TURN" ? "可恢复研究会话" : run.researchContextKind === "LEGACY_SESSION_RUN" ? "兼容历史运行" : "历史运行"; return <Link className="report-list-row" key={run.jobId} href={`/projects/${projectId}/reports/${run.jobId}`}><div><span className="product-kicker">{contextLabel}</span><h3>{researchRunTitle(run)}</h3><p>{dataset?.name || "项目数据"} · {run.artifactCount} 个结果 · {run.stepCount} 个步骤</p></div><span>阅读旧版</span></Link>; })}</div></section> : null}
    </> : null}
  </main></ProductShell></RequireProductAuth>;
}
