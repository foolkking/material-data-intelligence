"use client";

import { ProductLink as Link } from "./ProductNavigation";
import { useEffect, useMemo, useState } from "react";

import { getCachedProjectHistory, getProjectHistory, listProjects, type ProjectHistory, type ProjectSummary } from "../lib/planner-api";

type LoadState = "loading" | "ready" | "error";

export function ProjectHome() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [history, setHistory] = useState<ProjectHistory | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [error, setError] = useState("");
  const [retrySequence, setRetrySequence] = useState(0);
  const [datasetLimit, setDatasetLimit] = useState(8);
  const [analysisLimit, setAnalysisLimit] = useState(8);
  const [activityLimit, setActivityLimit] = useState(8);
  const [historyLoadingMore, setHistoryLoadingMore] = useState<"datasets" | "analyses" | "activity" | null>(null);

  useEffect(() => {
    let active = true;
    void listProjects()
      .then((nextProjects) => {
        if (!active) return;
        setProjects(nextProjects);
        setSelectedProjectId(nextProjects[0]?.projectId || nextProjects[0]?.id || "");
      })
      .catch((reason) => {
        if (!active) return;
        setError(reason instanceof Error ? reason.message : "项目列表加载失败");
        setLoadState("error");
      });
    return () => {
      active = false;
    };
  }, [retrySequence]);

  useEffect(() => {
    if (!selectedProjectId) {
      if (projects.length === 0 && loadState === "loading") setLoadState("ready");
      return;
    }
    let active = true;
    setError("");
    const cached = getCachedProjectHistory(selectedProjectId);
    if (cached?.pagination) {
      setHistory(cached);
      setLoadState("ready");
      return () => {
        active = false;
      };
    }
    setLoadState("loading");
    // History reads already use the shared bounded directory cache. Mutating
    // operations invalidate that cache explicitly, so forcing a refresh on
    // every project selection only adds a full-latency round trip when users
    // navigate back to the project home.
    void getProjectHistory(selectedProjectId, { limit: 8 })
      .then((nextHistory) => {
        if (!active) return;
        setHistory(nextHistory);
        setLoadState("ready");
      })
      .catch((reason) => {
        if (!active) return;
        setError(reason instanceof Error ? reason.message : "项目历史加载失败");
        setLoadState("error");
      });
    return () => {
      active = false;
    };
  }, [projects.length, retrySequence, selectedProjectId]);

  const projectId = selectedProjectId || history?.project.projectId || history?.project.id || "";
  const uploadHref = projectId
    ? `/projects/${encodeURIComponent(projectId)}/datasets/new`
    : "/analysis";
  const summary = history?.summary;
  const datasets = useMemo(() => history?.datasets || [], [history]);
  const analyses = useMemo(() => history?.analyses || [], [history]);
  const visibleDatasets = datasets.slice(0, datasetLimit);
  const visibleAnalyses = analyses.slice(0, analysisLimit);
  const visibleActivity = (history?.activity || []).slice(0, activityLimit);
  const loadMoreHistory = async (section: "datasets" | "analyses" | "activity") => {
    if (!history || historyLoadingMore) return;
    const cursor = history.pagination?.[section].nextCursor;
    if (!cursor) return;
    setHistoryLoadingMore(section);
    try {
      const next = await getProjectHistory(projectId, {
        limit: 100,
        datasetsCursor: section === "datasets" ? cursor : undefined,
        analysesCursor: section === "analyses" ? cursor : undefined,
        activityCursor: section === "activity" ? cursor : undefined,
      });
      setHistory((current) => current ? {
        ...current,
        datasets: section === "datasets" ? [...current.datasets, ...next.datasets] : current.datasets,
        analyses: section === "analyses" ? [...current.analyses, ...next.analyses] : current.analyses,
        activity: section === "activity" ? [...current.activity, ...next.activity] : current.activity,
        pagination: next.pagination,
      } : current);
      if (section === "datasets") setDatasetLimit((value) => value + next.datasets.length);
      if (section === "analyses") setAnalysisLimit((value) => value + next.analyses.length);
      if (section === "activity") setActivityLimit((value) => value + next.activity.length);
    } finally {
      setHistoryLoadingMore(null);
    }
  };

  return (
    <main className="project-home" data-testid="project-home">
      <header className="project-home-header">
        <div>
          <p className="eyebrow">Material Data Intelligence</p>
          <h1>项目与数据</h1>
          <p className="project-home-lede">材料项目、数据与分析记录</p>
        </div>
        <div className="project-home-actions">
          <Link className="primary-action" href={uploadHref}>导入数据并分析</Link>
        </div>
      </header>

      <section className="project-selector-band" aria-label="项目选择">
        <div>
          <span className="section-kicker">当前项目</span>
          <strong>{history?.project.name || projects.find((item) => (item.projectId || item.id) === projectId)?.name || "选择一个项目"}</strong>
        </div>
        {projects.length > 1 ? (
          <label className="project-selector">
            <span className="sr-only">选择项目</span>
            <select value={projectId} onChange={(event) => setSelectedProjectId(event.target.value)}>
              {projects.map((project) => {
                const id = project.projectId || project.id;
                return <option key={id} value={id}>{project.name}</option>;
              })}
            </select>
          </label>
        ) : null}
      </section>

      {loadState === "loading" ? <section className="project-state" role="status">正在读取项目历史...</section> : null}
      {loadState === "error" ? (
        <section className="project-state project-state-error" role="alert">
          <strong>项目历史暂时不可用</strong>
          <span>{error}</span>
          <div className="project-state-actions">
            <button className="secondary-action" type="button" onClick={() => setRetrySequence((value) => value + 1)}>重新加载</button>
            <Link className="secondary-action" href={uploadHref}>进入分析工作台</Link>
          </div>
        </section>
      ) : null}
      {loadState === "ready" && !history && projects.length === 0 ? (
        <section className="project-state">
          <strong>还没有项目数据</strong>
          <span>先导入一个数据集，系统会在这里保留导入、分析和结果记录。</span>
          <Link className="primary-action" href={uploadHref}>开始导入</Link>
        </section>
      ) : null}

      {history ? (
        <>
          <section className="project-metrics" aria-label="项目概览">
            <Metric value={summary?.datasetCount || 0} label="数据集" />
            <Metric value={summary?.analysisCount || 0} label="分析运行" />
            <Metric value={summary?.completedAnalysisCount || 0} label="已完成" />
            <Metric value={summary?.artifactCount || 0} label="结果" />
            <Metric value={summary?.reportCount || 0} label="报告" />
          </section>

          <section className="project-band" aria-labelledby="datasets-heading">
              <div className="band-heading">
                <div><p className="section-kicker">数据记录</p><h2 id="datasets-heading">数据集</h2></div>
                <Link className="text-action" href={uploadHref}>导入新数据</Link>
            </div>
            {datasets.length === 0 ? <p className="empty-inline">当前项目还没有数据集。</p> : (
              <div className="dataset-history-list">
                {visibleDatasets.map((dataset) => (
                  <Link
                    className="dataset-history-row"
                    href={`/projects/${projectId}/data?dataset=${encodeURIComponent(dataset.datasetId)}`}
                    key={dataset.datasetId}
                  >
                    <span className="dataset-history-main">
                      <strong>{dataset.name}</strong>
                      <span>{dataset.import.fileCount} 个源文件 · {dataset.import.parseOutcome === "succeeded" ? "解析完成" : dataset.import.parseOutcome} · {dataset.resultSummary?.artifactCount || 0} 个结果</span>
                    </span>
                    <span className="dataset-history-meta">
                      <StatusText value={dataset.status} />
                      <span>{dataset.profile ? "Profile " + (dataset.profile.rowCount ?? 0) + " 行" : "Profile 待生成"}</span>
                      <span className="row-chevron" aria-hidden="true">→</span>
                    </span>
                  </Link>
                ))}
              </div>
            )}
            {history?.pagination?.datasets.nextCursor ? <button className="project-history-load-more" type="button" onClick={() => void loadMoreHistory("datasets")} disabled={historyLoadingMore === "datasets"}>继续加载数据集</button> : visibleDatasets.length < datasets.length ? <button className="project-history-load-more" type="button" onClick={() => setDatasetLimit((value) => value + 8)}>显示更多数据集（还剩 {datasets.length - visibleDatasets.length} 个）</button> : null}
          </section>

          <div className="project-lower-grid">
            <section className="project-band" aria-labelledby="analysis-history-heading">
              <div className="band-heading">
                <div><p className="section-kicker">分析记录</p><h2 id="analysis-history-heading">分析历史</h2></div>
                <span className="band-count">{analyses.length}</span>
              </div>
              {analyses.length === 0 ? <p className="empty-inline">暂无分析记录。</p> : (
                <div className="analysis-history-list">
                  {visibleAnalyses.map((analysis) => (
                    <Link className="analysis-history-row" href={analysisHref(projectId, analysis)} key={analysis.jobId}>
                      <span>
                        <strong>{analysis.userQuestion || "未命名分析"}</strong>
                        <span>{analysis.artifactCount} 个结果 · {analysis.reportCount} 份报告</span>
                      </span>
                      <StatusText value={effectiveAnalysisStatus(analysis)} />
                    </Link>
                  ))}
                </div>
              )}
              {history?.pagination?.analyses.nextCursor ? <button className="project-history-load-more" type="button" onClick={() => void loadMoreHistory("analyses")} disabled={historyLoadingMore === "analyses"}>继续加载分析</button> : visibleAnalyses.length < analyses.length ? <button className="project-history-load-more" type="button" onClick={() => setAnalysisLimit((value) => value + 8)}>显示更多分析（还剩 {analyses.length - visibleAnalyses.length} 项）</button> : null}
            </section>

            <section className="project-band" aria-labelledby="activity-heading">
              <div className="band-heading"><div><p className="section-kicker">活动记录</p><h2 id="activity-heading">最近活动</h2></div></div>
              {history.activity.length === 0 ? <p className="empty-inline">暂无活动记录。</p> : (
                <div className="activity-list">
                  {visibleActivity.map((item) => (
                    <Link className="activity-row" href={item.href} key={item.activityId}>
                      <span className="activity-marker" aria-hidden="true" />
                      <span><strong>{item.title}</strong><span>{item.detail}</span></span>
                      <time dateTime={item.occurredAt || undefined}>{formatTime(item.occurredAt)}</time>
                    </Link>
                  ))}
                </div>
              )}
              {history?.pagination?.activity.nextCursor ? <button className="project-history-load-more" type="button" onClick={() => void loadMoreHistory("activity")} disabled={historyLoadingMore === "activity"}>继续加载活动</button> : visibleActivity.length < history.activity.length ? <button className="project-history-load-more" type="button" onClick={() => setActivityLimit((value) => value + 8)}>显示更多活动（还剩 {history.activity.length - visibleActivity.length} 项）</button> : null}
            </section>
          </div>
        </>
      ) : null}
    </main>
  );
}

function analysisHref(
  projectId: string,
  analysis: {
    jobId: string;
    workspaceId?: string | null;
    researchSessionId?: string;
    researchTurnId?: string | null;
  },
) {
  if (analysis.researchSessionId && analysis.researchTurnId) {
    return `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(analysis.researchSessionId)}?turn=${encodeURIComponent(analysis.researchTurnId)}`;
  }
  if (analysis.workspaceId) return "/workspaces/" + encodeURIComponent(analysis.workspaceId);
  return "/analysis?jobId=" + encodeURIComponent(analysis.jobId);
}

function effectiveAnalysisStatus(analysis: {
  status?: string | null;
  researchTurnStatus?: string | null;
}) {
  return analysis.researchTurnStatus || analysis.status;
}

function Metric({ value, label }: { value: number; label: string }) {
  return <div className="project-metric"><strong>{value}</strong><span>{label}</span></div>;
}

function StatusText({ value }: { value?: string | null }) {
  const labels: Record<string, string> = {
    profile_ready: "Profile 已就绪",
    ready: "已就绪",
    succeeded: "已完成",
    success: "已完成",
    completed: "已完成",
    queued: "排队中",
    running: "运行中",
    processing: "处理中",
    failed: "失败",
    error: "错误",
    partial: "部分完成",
    not_started: "未开始",
    pending: "待处理",
  };
  const normalized = String(value || "").trim().toLowerCase();
  const label = labels[normalized] || value || "未开始";
  return <span className={"status-text status-" + label.toLowerCase().replaceAll("_", "-")}>{label}</span>;
}

function formatTime(value?: string | null) {
  if (!value) return "时间未知";
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) return value;
  return new Intl.DateTimeFormat("zh-CN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(date);
}
