"use client";

import { ProductLink as Link } from "./ProductNavigation";
import { useEffect, useState } from "react";

import { getProjectHistory, type ProjectHistory } from "../lib/planner-api";
import { buildResearchHref } from "../lib/research-navigation";
import { PlannerWorkbench } from "../../features/research/planning/PlannerWorkbench";

export function DatasetWorkbenchPage({ projectId, datasetId }: { projectId: string; datasetId: string }) {
  const [history, setHistory] = useState<ProjectHistory | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    void getProjectHistory(projectId)
      .then((value) => {
        if (active) setHistory(value);
      })
      .catch((reason) => {
        if (active) setError(reason instanceof Error ? reason.message : "数据记录加载失败");
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  const dataset = history?.datasets.find((item) => item.datasetId === datasetId);
  const profile = dataset?.profile;
  const analysisCount = dataset?.analysisCount || 0;
  const resultSummary = dataset?.resultSummary;
  const datasetAnalyses = (history?.analyses || []).filter((item) => item.datasetId === datasetId);
  const projectHref = `/projects/${encodeURIComponent(projectId)}`;
  const datasetUploadHref = `${projectHref}/datasets/new`;

  return (
    <div className="dataset-workbench-page" data-testid="dataset-workbench-page">
      <header className="dataset-workbench-header">
        <div className="dataset-breadcrumb">
          <Link href={projectHref}>项目</Link>
          <span aria-hidden="true">/</span>
          <span>{history?.project.name || projectId}</span>
          <span aria-hidden="true">/</span>
          <strong>{dataset?.name || datasetId}</strong>
        </div>
        <div className="dataset-workbench-title-row">
          <div>
            <p className="eyebrow">数据工作台</p>
            <h1>{dataset?.name || datasetId}</h1>
            <p>{dataset ? dataset.import.fileCount + " 个源文件 · " + (profile ? "语义档案已就绪" : "语义档案待生成") + " · " + analysisCount + " 次科学分析" : "正在读取数据集记录..."}</p>
          </div>
          <div className="dataset-workbench-actions">
            <Link className="secondary-action" href={projectHref}>返回项目</Link>
            <Link className="primary-action" href={datasetUploadHref}>导入其他数据</Link>
          </div>
        </div>
        <div className="dataset-progress" aria-label="数据工作流">
          <ProgressStep label="导入" state={dataset ? "done" : "active"} />
          <ProgressStep label="语义档案" state={profile ? "done" : dataset ? "active" : "pending"} />
          <ProgressStep label="科学分析" state={analysisCount ? "done" : profile ? "active" : "pending"} />
          <ProgressStep label="分析结果" state={resultSummary?.artifactCount ? "done" : analysisCount ? "active" : "pending"} />
        </div>
        <aside className="dataset-context-note" role="note">
          <strong>这是数据集详情页</strong>
          <p>数据集负责保存导入范围；科学对象与不可变版本由数据平台维护。语义档案只描述可用字段和能力，分析结果不会改写源文件。</p>
          <details>
            <summary>术语说明</summary>
            <ul>
              <li><strong>语义档案（Profile）</strong>：从源数据生成的可审计结构、字段和语义摘要。</li>
              <li><strong>科学资源</strong>：供查看器、表格和分析读取的持久化资源；它不改变源文件。</li>
              <li><strong>分析结果（ScientificResult）</strong>：已完成分析产生的权威科学事实，以及它引用的 Artifact 和报告。</li>
            </ul>
          </details>
        </aside>
        <section className="dataset-layer-guide" aria-labelledby="dataset-layer-guide-title">
          <div className="dataset-layer-guide-heading">
            <p className="section-kicker">边界说明</p>
            <h2 id="dataset-layer-guide-title">从来源到结果：每一层负责什么</h2>
            <p>这些层级相互关联，但职责不同；打开查看器或分析结果时，页面会保留对应的精确来源。</p>
          </div>
          <ol>
            <li>
              <span>01 · Dataset</span>
              <strong>来源范围</strong>
              <small>记录导入文件、数据集范围和处理状态。</small>
            </li>
            <li>
              <span>02 · Profile</span>
              <strong>语义档案</strong>
              <small>描述字段、样本和可用能力，不是新的科学结果。</small>
            </li>
            <li>
              <span>03 · ScientificObject / Version</span>
              <strong>科学身份与状态</strong>
              <small>对象代表科学身份；版本保存不可变的精确状态。</small>
            </li>
            <li>
              <span>04 · ScientificResult</span>
              <strong>分析事实</strong>
              <small>保存已完成分析的权威事实，并回链到对象版本和证据。</small>
            </li>
          </ol>
        </section>
        {error ? <p className="dataset-inline-error" role="alert">{error}</p> : null}
      </header>

      <section className="dataset-record-strip" aria-label="当前数据记录摘要">
        <div><span>解析状态</span><strong>{friendlyProcessStatus(dataset?.import.parseOutcome || "unknown")}</strong></div>
        <div><span>记录数</span><strong>{profile?.rowCount ?? profile?.objectCount ?? "—"}</strong></div>
        <div><span>列数</span><strong>{profile?.columnCount ?? "—"}</strong></div>
        <div><span>可用分析</span><strong>{profile?.readyCapabilities?.length ?? 0}</strong></div>
        <div><span>最近分析</span><strong>{friendlyProcessStatus(dataset?.lastAnalysisStatus || "not_started")}</strong></div>
        <div><span>分析结果 / 报告</span><strong>{resultSummary ? resultSummary.artifactCount + " / " + resultSummary.reportCount : "—"}</strong></div>
      </section>

      <section className="dataset-process-strip" aria-label="数据处理过程">
        {(dataset?.process || []).map((item) => (
          <div className={"dataset-process-step process-" + item.status} key={item.key}>
            <span>{item.label}</span>
            <strong>{friendlyProcessStatus(item.status)}</strong>
            <small>{item.detail}</small>
          </div>
        ))}
      </section>

      <section className="dataset-source-band" aria-labelledby="dataset-source-heading">
        <div className="band-heading">
          <div><p className="section-kicker">来源与推导</p><h2 id="dataset-source-heading">来源文件与科学资源</h2></div>
          <span className="band-count">{dataset?.import.fileCount || 0}</span>
        </div>
        <div className="dataset-source-grid">
          <div>
            <span className="source-label">源文件</span>
            {(dataset?.import.files || []).length ? (
              <ul className="dataset-source-list">
                {dataset?.import.files.map((file, index) => (
                  <li key={String(file.fileId || file.name || index)}>
                    <strong>{String(file.name || "未命名文件")}</strong>
                    <span>{String(file.format || "未知格式")} · {friendlyProcessStatus(String(file.status || "unknown"))}</span>
                  </li>
                ))}
              </ul>
            ) : <p className="empty-inline">暂无源文件明细。</p>}
          </div>
          <div>
            <span className="source-label">可查看的科学资源</span>
            <p className="source-value">{dataset?.import.resources.length || 0} 个资源已关联到当前数据集</p>
            <p className="source-value">{profile ? "语义档案 " + (profile.version || "") + " · " + (profile.columnCount || 0) + " 列" : "语义档案尚未生成"}</p>
          </div>
        </div>
      </section>

      <section className="dataset-analysis-band" aria-labelledby="dataset-analysis-heading">
        <div className="band-heading">
          <div><p className="section-kicker">结果记录</p><h2 id="dataset-analysis-heading">基于此数据集的分析</h2></div>
          <span className="band-count">{datasetAnalyses.length}</span>
        </div>
        {datasetAnalyses.length ? (
          <div className="dataset-analysis-list">
            {datasetAnalyses.map((analysis) => (
              <Link className="dataset-analysis-row" key={analysis.jobId} href={buildResearchHref({
                projectId,
                jobId: analysis.jobId,
                researchSessionId: analysis.researchSessionId,
                researchTurnId: analysis.researchTurnId,
                workspaceId: analysis.workspaceId,
              })}>
                <span>
                  <strong>{analysis.userQuestion || "未命名分析"}</strong>
                  <span>{analysis.artifactCount} 个分析结果 · {analysis.reportCount} 份报告 · {friendlyProcessStatus(analysis.status)}</span>
                </span>
                <span className="row-chevron" aria-hidden="true">→</span>
              </Link>
            ))}
          </div>
        ) : <p className="empty-inline">当前数据集还没有分析结果。</p>}
      </section>

      <PlannerWorkbench initialProjectId={projectId} initialDatasetId={datasetId} showGlobalContextBar={false} />
    </div>
  );
}

function friendlyProcessStatus(value: string) {
  const labels: Record<string, string> = {
    succeeded: "已完成",
    success: "已完成",
    completed: "已完成",
    ready: "已就绪",
    pending: "待处理",
    not_started: "未开始",
    processing: "处理中",
    partial: "部分完成",
    failed: "失败",
    unknown: "未知",
  };
  return labels[value] || value;
}

function ProgressStep({ label, state }: { label: string; state: "done" | "active" | "pending" }) {
  return (
    <div className={"dataset-progress-step progress-" + state}>
      <span className="progress-dot" aria-hidden="true">{state === "done" ? "✓" : ""}</span>
      <span>{label}</span>
    </div>
  );
}
