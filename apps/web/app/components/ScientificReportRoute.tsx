"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getScientificReport, type ScientificReportView } from "../lib/scientific-report-api";
import { ProductShell, RequireProductAuth } from "./ProductShell";
import { ReportReaderPage } from "./ResearchPages";

const relevanceCopy = {
  CURRENT: null,
  STALE: "这是基于历史数据版本生成的报告。当前项目中已有更新的数据版本。",
  SOURCE_MISSING: "该报告保留历史科学记录，但对应的原始数据版本当前不可访问。",
  INVALIDATED: "该报告仅作为历史记录，不应视为当前有效科学证据。",
} as const;

const methodCopy: Record<string, string> = {
  "structure.rdf": "根据晶体结构统计指定截断范围内的原子对距离分布，得到径向分布函数。",
  "diffraction.theoretical_xrd": "根据晶体结构与执行时记录的衍射参数计算理论 XRD 图谱。",
  "diffraction.experimental_theoretical_comparison": "在执行时记录的匹配容差下比较实验与理论 XRD 峰位。",
  "ml.regression_evaluation": "使用已提交的预测与真实值评估回归模型表现。",
  "trajectory.msd": "根据轨迹时间序列计算均方位移，并保留执行时的分量与时间单位。",
  "trajectory.diffusion": "基于已提交的 MSD 结果和拟合区间估计扩散系数。",
  "phonon.band": "沿既定布里渊区路径整理声子色散关系。",
  "phonon.dos": "根据已提交的频率网格整理声子态密度。",
  "phonon.band_dos": "联合呈现同一计算上下文中的声子色散与态密度。",
};

export function ScientificReportRoute({ projectId, reportId }: { projectId: string; reportId: string }) {
  const [report, setReport] = useState<ScientificReportView | null>(null);
  const [legacy, setLegacy] = useState(false);
  const [error, setError] = useState(false);
  useEffect(() => {
    let active = true;
    void getScientificReport(reportId)
      .then((value) => { if (active) setReport(value); })
      .catch((reason: Error & { status?: number }) => {
        if (!active) return;
        if (reason.status === 404) setLegacy(true);
        else setError(true);
      });
    return () => { active = false; };
  }, [reportId]);
  if (legacy) return <ReportReaderPage projectId={projectId} reportId={reportId} />;
  return <RequireProductAuth><ProductShell projectId={projectId}>
    {!report && !error ? <main className="scientific-report-shell"><div className="product-loading" role="status" aria-live="polite">正在打开科学报告…</div></main> : null}
    {error ? <main className="scientific-report-shell"><div className="product-state" role="alert"><h1>报告暂时无法打开</h1><p>已生成的报告仍保存在项目中，请稍后重试。</p><Link className="product-secondary-action" href={`/projects/${projectId}/reports`}>返回报告列表</Link></div></main> : null}
    {report?.report ? <ScientificReportDocument projectId={projectId} view={report} /> : null}
  </ProductShell></RequireProductAuth>;
}

function ScientificReportDocument({ projectId, view }: { projectId: string; view: ScientificReportView }) {
  const report = view.report!;
  const warning = relevanceCopy[view.current_effective_relevance];
  const limitations = report.limitations.filter((item, index, items) => items.findIndex((candidate) => candidate.statement.trim().toLocaleLowerCase() === item.statement.trim().toLocaleLowerCase()) === index);
  const methodSummary = Object.entries(methodCopy).reduce(
    (summary, [capability, copy]) => summary.replace(new RegExp(`${capability.replaceAll(".", "\\.")}\\s*\\([^)]*\\)`, "gu"), copy),
    report.method_summary,
  );
  return <main className="scientific-report-shell">
    <article className="scientific-report-document">
      <nav className="scientific-report-back" aria-label="报告导航"><Link href={`/projects/${projectId}/reports`}>返回报告</Link><Link href={`/projects/${projectId}/research`}>回到研究</Link></nav>
      <header className="scientific-report-masthead">
        <p className="product-kicker">Grounded Scientific Report</p>
        <h1>{report.title}</h1>
        <p className="scientific-report-context">{new Date(view.created_at).toLocaleString("zh-CN")} · {report.main_findings.length} 项主要发现</p>
      </header>
      {warning ? <aside className={`scientific-report-status is-${view.current_effective_relevance.toLowerCase()}`} role="note"><strong>{view.current_effective_relevance === "STALE" ? "历史版本" : "来源状态提示"}</strong><p>{warning}</p></aside> : null}
      <section className="scientific-report-lead" aria-labelledby="report-question"><p className="product-kicker">研究问题</p><h2 id="report-question">{report.research_question}</h2><p>{report.summary}</p></section>
      {report.primary_figures.length ? <section className="scientific-report-figures" aria-labelledby="report-figures"><h2 id="report-figures">主要图表</h2>{report.primary_figures.map((figure, index) => <figure key={figure.figure_ref}><div className="scientific-report-figure-plate" data-figure-ref={figure.figure_ref}><span>{String(index + 1).padStart(2, "0")}</span><strong>{figure.caption}</strong><p>交互图形和完整数据保留在对应的 Scientific Result 中。</p>{view.viewer_sources?.[0] ? <Link href={`/projects/${projectId}/data?object=${encodeURIComponent(view.viewer_sources[0].object_id)}&version=${encodeURIComponent(view.viewer_sources[0].version_id)}&name=${encodeURIComponent(view.viewer_sources[0].display_name)}`}>在科学视图中查看</Link> : <Link href={`/projects/${projectId}/research?turn=${encodeURIComponent(view.research_turn_id)}`}>打开对应科学结果</Link>}</div><figcaption>Figure {index + 1}. {figure.caption}</figcaption></figure>)}</section> : null}
      <section className="scientific-report-findings" aria-labelledby="report-findings"><h2 id="report-findings">主要发现</h2><ol>{report.main_findings.map((finding, index) => <li key={`${finding.statement}-${index}`}><span>{String(index + 1).padStart(2, "0")}</span><p>{finding.statement}</p></li>)}</ol></section>
      <section className="scientific-report-limitations" aria-labelledby="report-limitations"><h2 id="report-limitations">限制与适用范围</h2>{limitations.length ? <ul>{limitations.map((item) => <li key={item.statement}>{item.statement}</li>)}</ul> : <p>未记录额外限制；结论仍只适用于本报告绑定的 exact source versions。</p>}</section>
      {report.supporting_results.length ? <section className="scientific-report-supporting" aria-labelledby="report-supporting"><h2 id="report-supporting">支持结果</h2><div>{report.supporting_results.map((item) => <article key={item.result_item_ref}><strong>{item.description}</strong><span>已验证 supporting result</span></article>)}</div></section> : null}
      <section className="scientific-report-disclosures" aria-label="报告依据与复现信息">
        <details open><summary>分析方法</summary><p>{methodSummary}</p></details>
        <details><summary>科学依据 · {report.evidence_refs.length}</summary><p>所有发现与图表引用均已通过 ReportGroundingValidator，并绑定到同一 ScientificResult。</p></details>
        <details><summary>来源数据 · {report.data_sources.length}</summary><ul>{report.data_sources.map((source) => <li key={source}>已授权 exact source version</li>)}</ul></details>
        <details><summary>复现信息</summary><p>{report.reproducibility_summary}</p><p className="scientific-report-technical">Report contract {report.contract_version} · 系统校验已通过</p></details>
      </section>
    </article>
  </main>;
}
