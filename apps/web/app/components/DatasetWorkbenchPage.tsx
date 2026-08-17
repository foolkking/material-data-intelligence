"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { getProjectHistory, type ProjectHistory } from "../lib/planner-api";
import { PlannerWorkbench } from "./PlannerWorkbench";

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

  return (
    <div className="dataset-workbench-page" data-testid="dataset-workbench-page">
      <header className="dataset-workbench-header">
        <div className="dataset-breadcrumb">
          <Link href="/">项目</Link>
          <span aria-hidden="true">/</span>
          <span>{history?.project.name || projectId}</span>
          <span aria-hidden="true">/</span>
          <strong>{dataset?.name || datasetId}</strong>
        </div>
        <div className="dataset-workbench-title-row">
          <div>
            <p className="eyebrow">数据工作台</p>
            <h1>{dataset?.name || datasetId}</h1>
            <p>{dataset ? dataset.import.fileCount + " 个源文件 · " + (profile ? "Profile 已就绪" : "Profile 待生成") + " · " + analysisCount + " 次分析" : "正在读取数据集记录..."}</p>
          </div>
          <div className="dataset-workbench-actions">
            <Link className="secondary-action" href="/">返回项目</Link>
            <Link className="primary-action" href="/analysis">导入其他数据</Link>
          </div>
        </div>
        <div className="dataset-progress" aria-label="数据工作流">
          <ProgressStep label="导入" state={dataset ? "done" : "active"} />
          <ProgressStep label="Profile" state={profile ? "done" : dataset ? "active" : "pending"} />
          <ProgressStep label="分析" state={analysisCount ? "done" : profile ? "active" : "pending"} />
          <ProgressStep label="结果" state={resultSummary?.artifactCount ? "done" : analysisCount ? "active" : "pending"} />
        </div>
        {error ? <p className="dataset-inline-error" role="alert">{error}</p> : null}
      </header>

      <section className="dataset-record-strip" aria-label="当前数据记录摘要">
        <div><span>解析状态</span><strong>{friendlyProcessStatus(dataset?.import.parseOutcome || "unknown")}</strong></div>
        <div><span>表格行数</span><strong>{profile?.rowCount ?? "—"}</strong></div>
        <div><span>列数</span><strong>{profile?.columnCount ?? "—"}</strong></div>
        <div><span>可用能力</span><strong>{profile?.readyCapabilities?.length ?? 0}</strong></div>
        <div><span>最近分析</span><strong>{friendlyProcessStatus(dataset?.lastAnalysisStatus || "not_started")}</strong></div>
        <div><span>结果 / 报告</span><strong>{resultSummary ? resultSummary.artifactCount + " / " + resultSummary.reportCount : "—"}</strong></div>
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
          <div><p className="section-kicker">来源与推导</p><h2 id="dataset-source-heading">上传记录</h2></div>
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
            <span className="source-label">规范化资源</span>
            <p className="source-value">{dataset?.import.resources.length || 0} 个资源已关联到当前数据集</p>
            <p className="source-value">{profile ? "Profile " + (profile.version || "") + " · " + (profile.columnCount || 0) + " 列" : "Profile 尚未生成"}</p>
          </div>
        </div>
      </section>

      <section className="dataset-analysis-band" aria-labelledby="dataset-analysis-heading">
        <div className="band-heading">
          <div><p className="section-kicker">结果记录</p><h2 id="dataset-analysis-heading">该数据集的分析</h2></div>
          <span className="band-count">{datasetAnalyses.length}</span>
        </div>
        {datasetAnalyses.length ? (
          <div className="dataset-analysis-list">
            {datasetAnalyses.map((analysis) => (
              <Link className="dataset-analysis-row" key={analysis.jobId} href={analysis.workspaceId ? "/workspaces/" + analysis.workspaceId : "/analysis?jobId=" + analysis.jobId}>
                <span>
                  <strong>{analysis.userQuestion || "未命名分析"}</strong>
                  <span>{analysis.artifactCount} 个结果 · {analysis.reportCount} 份报告 · {friendlyProcessStatus(analysis.status)}</span>
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
