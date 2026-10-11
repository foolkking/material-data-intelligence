"use client";

import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { taskHasEnded, taskIsInProgress, taskRecordTitle, taskResultSummary, taskStatusLabel } from "../../app/lib/task-display";
import { cancelAgent2Execution } from "../../app/lib/agent2-execution-api";
import { buildResearchHref } from "../../app/lib/research-navigation";
import {
  getProductTaskFeedPage,
  invalidateProductTaskFeed,
  productTaskSearchText,
  sortProductTaskRows,
  type ProductTaskSortOrder,
  type ProductTaskRow,
} from "../../app/lib/task-center-data";
import {
  refreshSharedProductTaskFeed,
  useProductTaskFeed,
} from "../../app/lib/use-product-task-feed";
import { ProductShell, RequireProductAuth } from "../../shared/layout/ProductShell";
import { scientistProjectLabel } from "../../shared/product-labels";
import { ProductModal } from "../../shared/ui/ObjectManagement";
import { SourceDatasetList } from "../../shared/ui/SourceDatasetList";
import {
  RESEARCH_CANCELLING_LABEL,
  RESEARCH_CANCELLING_POLL_INTERVAL_MS,
  isResearchCancellationPending,
  researchCancellationContract,
} from "../../app/lib/research-status";

type TaskRow = ProductTaskRow;
const statusTone: Record<string, string> = {
  created: "pending",
  queued: "pending",
  running: "active",
  cancel_requested: "warning",
  canceling: "warning",
  cancelled: "muted",
  canceled: "muted",
  completed: "success",
  succeeded: "success",
  partial_success: "warning",
  failed: "danger",
};
const STALE_TASK_AGE_MS = 15 * 60 * 1000;
function taskIsStale(task: Pick<TaskRow, "jobStatus" | "updatedAt" | "createdAt">, now = Date.now()) {
  if (!taskIsInProgress(task.jobStatus)) return false;
  const timestamp = Date.parse(String(task.updatedAt || task.createdAt || ""));
  return Number.isFinite(timestamp) && now - timestamp >= STALE_TASK_AGE_MS;
}
function taskNeedsAttention(
  task: Pick<TaskRow, "jobStatus" | "updatedAt" | "createdAt">,
  now = Date.now(),
) {
  const status = String(task.jobStatus || "").toLowerCase();
  return (
    ["failed", "partial_success", "cancelled", "canceled"].includes(status) ||
    taskIsStale(task, now)
  );
}
function taskIsLive(task: Pick<TaskRow, "jobStatus" | "workspaceProjectionStatus" | "researchTurnId">) {
  return taskIsInProgress(task.jobStatus)
    && researchCancellationContract(task) === "MODERN_TURN";
}
const taskTimestamp = (task: TaskRow) => task.updatedAt || task.createdAt;
const taskTimestampLabel = (task: TaskRow) => {
  const value = taskTimestamp(task);
  if (!value) return null;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};
const taskHref = (task: TaskRow) => buildResearchHref(task);
const retryHref = (task: TaskRow) => {
  if (!task.researchTurnId) return null;
  const href = buildResearchHref(task);
  return `${href}${href.includes("?") ? "&" : "?"}retry=1`;
};

export function TaskCenterPage() {
  const [cancelingJobId, setCancelingJobId] = useState<string | null>(null);
  const [cancelError, setCancelError] = useState<string | null>(null);
  const [cancelNotice, setCancelNotice] = useState<string | null>(null);
  const [taskFilter, setTaskFilter] = useState<"all" | "active" | "attention" | "completed">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortOrder, setSortOrder] = useState<ProductTaskSortOrder>("recent");
  const [cancelConfirmTask, setCancelConfirmTask] = useState<TaskRow | null>(null);
  const [displayLimit, setDisplayLimit] = useState(30);
  const [olderTasks, setOlderTasks] = useState<TaskRow[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [loadMoreError, setLoadMoreError] = useState<string | null>(null);
  const pageRequestRef = useRef<{ controller: AbortController; timer: number } | null>(null);
  const filterButtonsRef = useRef<Array<HTMLButtonElement | null>>([]);
  const sharedFeed = useProductTaskFeed();
  const feed = sharedFeed.feed;
  const tasks = useMemo(() => {
    const merged = new Map<string, TaskRow>();
    for (const task of [...olderTasks, ...(feed?.rows ?? [])]) {
      merged.set(`${task.projectId}:${task.jobId}`, task);
    }
    return [...merged.values()];
  }, [feed?.rows, olderTasks]);
  const unavailableProjectCount = feed?.unavailableProjectCount ?? 0;
  const lastUpdatedAt = feed?.loadedAt ?? null;
  const isRefreshing = sharedFeed.isRefreshing;
  const refreshError = sharedFeed.refreshError;
  const state =
    feed &&
    feed.projectCount > 0 &&
    feed.unavailableProjectCount === feed.projectCount
      ? "error"
      : sharedFeed.state === "idle"
        ? "loading"
        : sharedFeed.state;
  const activeTasks = useMemo(() => tasks.filter((task) => taskIsInProgress(task.jobStatus)), [tasks]);
  const completedTasks = useMemo(() => tasks.filter((task) => taskHasEnded(task.jobStatus)), [tasks]);
  const attentionTasks = useMemo(
    () => tasks.filter((task) => taskNeedsAttention(task)),
    [tasks],
  );
  const filteredTasks = useMemo(() => {
    if (taskFilter === "active") return activeTasks;
    if (taskFilter === "attention") return attentionTasks;
    if (taskFilter === "completed") return completedTasks;
    return tasks;
  }, [activeTasks, attentionTasks, completedTasks, taskFilter, tasks]);
  const normalizedSearchQuery = searchQuery.trim().toLocaleLowerCase("zh-CN");
  const searchedTasks = useMemo(
    () =>
      sortProductTaskRows(
        filteredTasks.filter(
          (task) =>
            !normalizedSearchQuery ||
            productTaskSearchText(task).includes(normalizedSearchQuery),
        ),
        sortOrder,
      ),
    [filteredTasks, normalizedSearchQuery, sortOrder],
  );
  useEffect(() => {
    setDisplayLimit(30);
  }, [searchQuery, sortOrder, taskFilter]);
  useEffect(() => {
    pageRequestRef.current?.controller.abort();
    if (pageRequestRef.current) window.clearTimeout(pageRequestRef.current.timer);
    pageRequestRef.current = null;
    setOlderTasks([]);
    setNextCursor(feed?.nextCursor ?? null);
    setLoadMoreError(null);
    setIsLoadingMore(false);
  }, [feed]);
  useEffect(() => () => {
    pageRequestRef.current?.controller.abort();
    if (pageRequestRef.current) window.clearTimeout(pageRequestRef.current.timer);
  }, []);
  useEffect(() => {
    if (!tasks.some((task) => isResearchCancellationPending(task.jobStatus))) {
      return;
    }
    const timer = window.setInterval(() => {
      void refreshSharedProductTaskFeed({ forceRefresh: true });
    }, RESEARCH_CANCELLING_POLL_INTERVAL_MS);
    return () => window.clearInterval(timer);
  }, [tasks]);
  async function cancelTask(task: TaskRow) {
    if (!task.researchTurnId) return;
    setCancelConfirmTask(null);
    setCancelingJobId(task.jobId);
    setCancelError(null);
    setCancelNotice(null);
    try {
      await cancelAgent2Execution(task.researchTurnId);
      invalidateProductTaskFeed();
      await refreshSharedProductTaskFeed({ forceRefresh: true });
      setCancelNotice("停止请求已记录；任务中心会继续同步这项研究的最终状态。");
    } catch (error) {
      setCancelError(error instanceof Error ? error.message : "停止请求未能提交");
    } finally {
      setCancelingJobId(null);
    }
  }
  async function loadMoreTasks() {
    if (!nextCursor || pageRequestRef.current) return;
    setIsLoadingMore(true);
    setLoadMoreError(null);
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      controller.abort();
      pageRequestRef.current = null;
      setIsLoadingMore(false);
      setLoadMoreError("更早任务读取超时。已显示的任务仍可查看，请重试。");
    }, 10_000);
    pageRequestRef.current = { controller, timer };
    try {
      const page = await getProductTaskFeedPage({ cursor: nextCursor, signal: controller.signal });
      if (controller.signal.aborted) return;
      setOlderTasks((current) => {
        const merged = new Map(
          current.map((task) => [`${task.projectId}:${task.jobId}`, task] as const),
        );
        for (const task of page.rows) {
          merged.set(`${task.projectId}:${task.jobId}`, task);
        }
        return [...merged.values()];
      });
      setNextCursor(page.nextCursor);
      setDisplayLimit((limit) => Math.max(limit, 30));
    } catch {
      if (!controller.signal.aborted) setLoadMoreError("更早任务暂时无法读取。已显示的任务仍可查看，请重试。");
    } finally {
      window.clearTimeout(timer);
      if (pageRequestRef.current?.controller === controller) {
        pageRequestRef.current = null;
        setIsLoadingMore(false);
      }
    }
  }
  const visibleTasks = searchedTasks.slice(0, displayLimit);
  const hasMoreTasks = Boolean(nextCursor) || searchedTasks.length > visibleTasks.length;
  return <RequireProductAuth><ProductShell><section className="document-page task-center-page">
    {cancelConfirmTask ? <ProductModal
      eyebrow="研究控制"
      title="停止这项研究？"
      description="停止后将保留已完成的结果。正在执行的步骤可能需要一点时间才能停止。"
      onClose={() => setCancelConfirmTask(null)}
      footer={<>
        <button type="button" className="product-secondary-action" onClick={() => setCancelConfirmTask(null)}>继续运行</button>
        <button type="button" className="product-primary-action" onClick={() => void cancelTask(cancelConfirmTask)}>确认停止</button>
      </>}
    >
      <p><strong>{taskRecordTitle(cancelConfirmTask)}</strong> · {scientistProjectLabel(cancelConfirmTask.projectName, cancelConfirmTask.projectId)}</p>
      <p>稍后可从这条记录查看结果，或重新发起研究。</p>
    </ProductModal> : null}
    <header className="product-page-heading"><div><h1>任务中心</h1><p>查看研究进度、结果和需要处理的问题。</p>{lastUpdatedAt ? <small className="task-center-sync-status" role="status">{isRefreshing ? "正在同步最新状态…" : "最近同步 " + new Date(lastUpdatedAt).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</small> : null}</div><button type="button" className="product-secondary-action" onClick={() => void refreshSharedProductTaskFeed({ forceRefresh: true })} disabled={state === "loading" || isRefreshing}>{state === "loading" ? "正在加载…" : isRefreshing ? "正在同步…" : "重新加载"}</button></header>
    {state === "loading" ? <div className="product-loading" role="status">正在加载后台任务…</div> : null}
    {state === "error" ? <div className="product-state" role="alert"><h2>任务暂时无法读取</h2><p>已有研究不会丢失，请检查服务连接后重新打开任务中心。</p></div> : null}
    {refreshError ? <p className="product-form-error" role="status">同步失败，当前显示上次结果；请稍后重新加载。</p> : null}
    {loadMoreError ? <div className="product-search-recovery" role="alert"><p className="product-form-error">{loadMoreError}</p><button type="button" className="product-secondary-action" onClick={() => void loadMoreTasks()} disabled={isLoadingMore}>{isLoadingMore ? "正在读取…" : "重试读取更早任务"}</button></div> : null}
    {cancelError ? <p className="product-form-error" role="alert">{cancelError}</p> : null}
    {cancelNotice ? <p className="product-form-success" role="status" aria-live="polite">{cancelNotice}</p> : null}
    {state === "ready" && unavailableProjectCount ? <div className="product-state task-center-partial-state" role="alert"><strong>{unavailableProjectCount} 个项目暂未同步</strong><p>已加载的任务仍可正常打开；使用“重新加载”补取其余项目，不会重启科学计算。</p></div> : null}
    {state === "ready" ? <>
      <div className="task-center-filters" role="tablist" aria-label="任务筛选">
        {([
          { key: "all", label: "全部", count: tasks.length },
          { key: "active", label: "进行中", count: activeTasks.length },
          { key: "attention", label: "需要关注", count: attentionTasks.length },
          { key: "completed", label: "已结束", count: completedTasks.length },
        ] as const).map((filter, index, filters) => <button
          key={filter.key} ref={(element) => { filterButtonsRef.current[index] = element; }}
          id={`task-filter-${filter.key}`} type="button" role="tab" aria-controls="task-result-list"
          aria-selected={taskFilter === filter.key} tabIndex={taskFilter === filter.key ? 0 : -1}
          className={taskFilter === filter.key ? "active" : ""} onClick={() => setTaskFilter(filter.key)}
          onKeyDown={(event) => {
            const next = event.key === "ArrowRight" ? (index + 1) % filters.length : event.key === "ArrowLeft" ? (index + filters.length - 1) % filters.length : event.key === "Home" ? 0 : event.key === "End" ? filters.length - 1 : null;
            if (next === null) return;
            event.preventDefault(); setTaskFilter(filters[next].key); filterButtonsRef.current[next]?.focus();
          }}
        >{filter.label} <span>{filter.count}</span></button>)}
      </div>
      <div className="task-center-list-tools">
        <label htmlFor="task-center-search">查找任务<input id="task-center-search" type="search" value={searchQuery} placeholder="搜索项目、研究问题或状态" onChange={(event) => setSearchQuery(event.target.value)} /></label>
        <label htmlFor="task-center-sort">排序<select id="task-center-sort" value={sortOrder} onChange={(event) => setSortOrder(event.target.value as ProductTaskSortOrder)}><option value="recent">最近更新</option><option value="oldest">最早更新</option></select></label>
      </div>
      {hasMoreTasks ? <p className="task-center-bounded-notice" role="status">当前显示 {visibleTasks.length} 项，已加载 {tasks.length} 项。{nextCursor ? "还有更早的任务可继续读取。" : "可继续显示其余已加载任务。"}</p> : null}
      <TaskGroup labelledBy={`task-filter-${taskFilter}`} title={taskFilter === "all" ? "全部任务" : taskFilter === "active" ? "进行中的研究" : taskFilter === "attention" ? "需要关注" : "已结束的研究"} tasks={visibleTasks}
        empty={normalizedSearchQuery ? "没有匹配的任务。试试其他关键词，或清除搜索。" : taskFilter === "active" ? "当前没有排队或运行中的研究。" : taskFilter === "attention" ? "当前没有需要关注的研究。" : "还没有可展示的任务。"}
        cancelingJobId={cancelingJobId} onCancel={(task) => setCancelConfirmTask(task)}
        onClearSearch={normalizedSearchQuery ? () => { setSearchQuery(""); document.getElementById("task-center-search")?.focus(); } : undefined}
      />
      {hasMoreTasks ? <button type="button" className="task-center-load-more" onClick={() => displayLimit < searchedTasks.length ? setDisplayLimit((limit) => limit + 30) : void loadMoreTasks()} disabled={isLoadingMore}>{isLoadingMore ? "正在读取更早任务…" : displayLimit < searchedTasks.length ? "显示更多已加载任务" : "读取更早任务"}</button> : null}
    </> : null}
  </section></ProductShell></RequireProductAuth>;
}

function TaskGroup({ title, labelledBy, tasks, empty, cancelingJobId, onCancel, onClearSearch }: { title: string; labelledBy: string; tasks: TaskRow[]; empty: string; cancelingJobId?: string | null; onCancel?: (task: TaskRow) => void; onClearSearch?: () => void }) {
  return <section id="task-result-list" role="tabpanel" className="task-center-section" aria-labelledby={labelledBy}>
    <div className="sr-only"><h2>{title}</h2><span>{tasks.length} 项</span></div>
    {tasks.length ? <div className="task-center-list">{tasks.map((task) => {
      const status = String(task.jobStatus || "").trim().toLowerCase();
      const retry = retryHref(task);
      const stale = taskIsStale(task);
      const cancelPending = isResearchCancellationPending(task.jobStatus);
      const canCancel = taskIsLive(task) && Boolean(task.researchTurnId);
      const timestamp = taskTimestamp(task);
      const timestampLabel = taskTimestampLabel(task);
      const openLabel = stale ? "检查进度" : taskIsInProgress(status) ? "查看进度" : taskHasEnded(status) && (task.artifactCount > 0 || task.interpretationCount > 0) ? "查看结果" : "查看详情";
      return <article className="task-center-row" key={`${task.projectId}:${task.jobId}`}>
        <div className="task-center-row-main">
          <h3 className="task-row-heading"><span className="task-display-title">{taskRecordTitle(task)}</span><span className={`task-status-badge task-status-${stale ? "warning" : statusTone[status] || "pending"}`}>{taskStatusLabel(task.jobStatus)}</span></h3>
          <div className="task-record-meta"><Link href={`/projects/${encodeURIComponent(task.projectId)}`}>{scientistProjectLabel(task.projectName, task.projectId)}</Link>{timestamp && timestampLabel ? <time dateTime={timestamp}>更新于 {timestampLabel}</time> : null}</div>
          <p className="task-result-summary">{taskResultSummary(task)}</p>
          {stale ? <small className="task-stale-notice" role="status">超过 15 分钟没有更新，请打开研究检查进度。</small> : null}
        </div>
        <details className="task-technical-identity"><summary>任务详情</summary><dl>
          <dt>任务编号</dt><dd><code>{task.jobId}</code></dd>
          {task.researchTurnId ? <><dt>研究编号</dt><dd><code>{task.researchTurnId}</code></dd></> : null}
          {task.workspaceProjectionStatus === "LEGACY_READ_ONLY" ? <><dt>记录类型</dt><dd>历史研究记录</dd></> : null}
          {task.sourceDatasets !== undefined ? <><dt>来源数据</dt><dd>
            {task.sourceDatasets.length ? <SourceDatasetList sources={task.sourceDatasets} projectId={task.projectId} /> : "来源待核实"}
          </dd></> : task.datasetId ? <><dt>来源数据</dt><dd><Link href={`/projects/${encodeURIComponent(task.projectId)}/data?dataset=${encodeURIComponent(task.datasetId)}`}>查看源数据</Link></dd></> : null}
        </dl></details>
        <div className="product-row-actions task-center-row-actions" aria-label={`${taskStatusLabel(task.jobStatus)}操作`}>
          <Link className="product-secondary-action" href={taskHref(task)}>{openLabel}</Link>
          {retry && ["failed", "cancelled", "canceled"].includes(status) ? <Link className="product-secondary-action" href={retry} title="准备新的研究，原记录和结果会保留">调整后重试</Link> : null}
          {onCancel && canCancel ? <button type="button" className="product-secondary-action" onClick={() => onCancel(task)} disabled={cancelingJobId === task.jobId || cancelPending}>{cancelingJobId === task.jobId ? "正在提交停止…" : cancelPending ? "正在取消研究" : "停止研究"}</button> : null}
        </div>
      </article>;
    })}</div> : <div className="product-state task-center-empty"><p>{empty}</p>{onClearSearch ? <button type="button" className="product-secondary-action" onClick={onClearSearch}>清除搜索</button> : null}</div>}
  </section>;
}
