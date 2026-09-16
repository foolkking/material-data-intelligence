"use client";

import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { useEffect, useMemo, useState } from "react";
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
import {
  RESEARCH_CANCELLING_LABEL,
  RESEARCH_CANCELLING_POLL_INTERVAL_MS,
  isResearchCancellationPending,
  researchCancellationContract,
} from "../../app/lib/research-status";

type TaskRow = ProductTaskRow;
const statusLabel: Record<string, string> = {
  created: "已创建", queued: "排队中", running: "运行中", cancel_requested: RESEARCH_CANCELLING_LABEL,
  cancelled: "已取消", canceled: "已取消", completed: "已完成", partial_success: "部分完成", failed: "失败",
};
const statusTone: Record<string, string> = {
  created: "pending",
  queued: "pending",
  running: "active",
  cancel_requested: "warning",
  cancelled: "muted",
  canceled: "muted",
  completed: "success",
  partial_success: "warning",
  failed: "danger",
};
const STALE_TASK_AGE_MS = 15 * 60 * 1000;
const taskLabel = (status: string | null) => statusLabel[String(status || "").toLowerCase()] || "处理中";
function taskIsStale(task: Pick<TaskRow, "jobStatus" | "updatedAt" | "createdAt">, now = Date.now()) {
  const status = String(task.jobStatus || "").toLowerCase();
  if (!["created", "queued", "running", "cancel_requested"].includes(status)) return false;
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
    (status === "running" && taskIsStale(task, now))
  );
}
function taskIsLive(task: Pick<TaskRow, "jobStatus" | "workspaceProjectionStatus" | "researchTurnId">) {
  const status = String(task.jobStatus || "").toLowerCase();
  return ["created", "queued", "running", "cancel_requested"].includes(status)
    && researchCancellationContract(task) === "MODERN_TURN";
}
const projectionLabel = (task: TaskRow) => {
  if (task.researchTurnId) return "可恢复研究会话";
  if (task.workspaceProjectionStatus === "LEGACY_READ_ONLY") return "历史运行 · 仅查看";
  return task.workspaceProjectionStatus;
};
const taskDisplayTitle = (task: TaskRow) => {
  if (task.researchQuestion) return task.researchQuestion;
  if (task.researchTurnId) return "可恢复研究";
  if (task.workspaceId) return "工作台研究";
  if (task.workspaceProjectionStatus === "LEGACY_READ_ONLY") return "历史研究";
  return "研究任务";
};
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
  const [taskFilter, setTaskFilter] = useState<"all" | "active" | "attention" | "completed">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortOrder, setSortOrder] = useState<ProductTaskSortOrder>("recent");
  const [cancelConfirmTask, setCancelConfirmTask] = useState<TaskRow | null>(null);
  const [displayLimit, setDisplayLimit] = useState(30);
  const [olderTasks, setOlderTasks] = useState<TaskRow[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [loadMoreError, setLoadMoreError] = useState<string | null>(null);
  const sharedFeed = useProductTaskFeed();
  const feed = sharedFeed.feed;
  const tasks = useMemo(() => {
    const merged = new Map<string, TaskRow>();
    for (const task of [...(feed?.rows ?? []), ...olderTasks]) {
      merged.set(`${task.projectId}:${task.jobId}`, task);
    }
    return [...merged.values()];
  }, [feed?.rows, olderTasks]);
  const projectCount = feed?.projectCount ?? 0;
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
  const activeTasks = useMemo(() => tasks.filter(taskIsLive), [tasks]);
  const completedTasks = useMemo(() => tasks.filter((task) => !activeTasks.includes(task)), [activeTasks, tasks]);
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
    setOlderTasks([]);
    setNextCursor(feed?.nextCursor ?? null);
    setLoadMoreError(null);
    setIsLoadingMore(false);
  }, [feed?.loadedAt, feed?.nextCursor]);
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
    try {
      await cancelAgent2Execution(task.researchTurnId);
      invalidateProductTaskFeed();
      await refreshSharedProductTaskFeed({ forceRefresh: true });
    } catch (error) {
      setCancelError(error instanceof Error ? error.message : "停止请求未能提交");
    } finally {
      setCancelingJobId(null);
    }
  }
  async function loadMoreTasks() {
    if (!nextCursor || isLoadingMore) return;
    setIsLoadingMore(true);
    setLoadMoreError(null);
    try {
      const page = await getProductTaskFeedPage({ cursor: nextCursor });
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
    } catch (error) {
      setLoadMoreError(error instanceof Error ? error.message : "更早任务暂时无法读取。");
    } finally {
      setIsLoadingMore(false);
    }
  }
  const visibleTasks = searchedTasks.slice(0, displayLimit);
  const hasMoreTasks = Boolean(nextCursor) || searchedTasks.length > visibleTasks.length;
  return <RequireProductAuth><ProductShell><section className="document-page task-center-page">
    {cancelConfirmTask ? <ProductModal
      eyebrow="研究控制"
      title="停止这项研究？"
      description="停止请求会写入当前 ResearchTurn，并保留已经提交的有效结果；尚未完成的分支不会被伪装成成功。"
      onClose={() => setCancelConfirmTask(null)}
      footer={<>
        <button type="button" className="product-secondary-action" onClick={() => setCancelConfirmTask(null)}>继续运行</button>
        <button type="button" className="product-primary-action" onClick={() => void cancelTask(cancelConfirmTask)}>确认停止</button>
      </>}
    >
      <p><strong>{taskDisplayTitle(cancelConfirmTask)}</strong> · {scientistProjectLabel(cancelConfirmTask.projectName, cancelConfirmTask.projectId)}</p>
      <p>停止后可从任务中心打开这条记录，查看已完成的 Artifact，并根据实际状态继续、重试或重新研究。</p>
    </ProductModal> : null}
    <header className="product-page-heading"><div><p className="product-kicker">后台任务</p><h1>任务中心</h1><p>跨项目查看研究执行状态。任务状态来自持久化运行记录，离开页面后仍可从这里继续查看。</p>{lastUpdatedAt ? <small className="task-center-sync-status" role="status">{isRefreshing ? "正在同步最新状态…" : "最近同步 " + new Date(lastUpdatedAt).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</small> : null}</div><button type="button" className="product-secondary-action" onClick={() => void refreshSharedProductTaskFeed({ forceRefresh: true })} disabled={state === "loading" || isRefreshing}>{state === "loading" ? "正在加载…" : isRefreshing ? "正在同步…" : "重新加载"}</button></header>
    {state === "loading" ? <div className="product-loading" role="status">正在加载后台任务…</div> : null}
    {state === "error" ? <div className="product-state" role="alert"><h2>任务暂时无法读取</h2><p>已有研究不会丢失，请检查服务连接后重新打开任务中心。</p></div> : null}
    {refreshError ? <p className="product-form-error" role="status">同步失败，当前显示上次结果；请稍后重新加载。</p> : null}
    {loadMoreError ? <div className="product-search-recovery" role="alert"><p className="product-form-error">{loadMoreError}</p><button type="button" className="product-secondary-action" onClick={() => void loadMoreTasks()} disabled={isLoadingMore}>{isLoadingMore ? "正在读取…" : "重试读取更早任务"}</button></div> : null}
    {cancelError ? <p className="product-form-error" role="alert">{cancelError}</p> : null}
    {state === "ready" && unavailableProjectCount ? <div className="product-state task-center-partial-state" role="alert"><strong>{unavailableProjectCount} 个项目暂未同步</strong><p>已加载的任务仍可正常打开；使用“重新加载”补取其余项目，不会重启科学计算。</p></div> : null}
    {state === "ready" ? <><section className="task-center-summary" aria-label="任务概览"><div><strong>{activeTasks.length}</strong><span>进行中</span></div><div><strong>{attentionTasks.length}</strong><span>需要关注</span></div><div><strong>{projectCount}</strong><span>授权项目</span></div></section><div className="task-center-filters" role="tablist" aria-label="任务筛选"><button type="button" role="tab" aria-selected={taskFilter === "all"} className={taskFilter === "all" ? "active" : ""} onClick={() => setTaskFilter("all")}>全部 <span>{tasks.length}</span></button><button type="button" role="tab" aria-selected={taskFilter === "active"} className={taskFilter === "active" ? "active" : ""} onClick={() => setTaskFilter("active")}>进行中 <span>{activeTasks.length}</span></button><button type="button" role="tab" aria-selected={taskFilter === "attention"} className={taskFilter === "attention" ? "active" : ""} onClick={() => setTaskFilter("attention")}>需要关注 <span>{attentionTasks.length}</span></button><button type="button" role="tab" aria-selected={taskFilter === "completed"} className={taskFilter === "completed" ? "active" : ""} onClick={() => setTaskFilter("completed")}>已结束 <span>{completedTasks.length}</span></button></div><div className="task-center-list-tools"><label htmlFor="task-center-search">查找任务<input id="task-center-search" type="search" value={searchQuery} placeholder="按项目、研究问题、状态或任务 ID 搜索" onChange={(event) => setSearchQuery(event.target.value)} /></label><label htmlFor="task-center-sort">排序<select id="task-center-sort" value={sortOrder} onChange={(event) => setSortOrder(event.target.value as ProductTaskSortOrder)}><option value="recent">最近更新</option><option value="oldest">最早更新</option></select></label></div>{hasMoreTasks ? <p className="task-center-bounded-notice" role="status">{nextCursor ? `当前筛选显示最近 ${displayLimit} 项；已加载 ${tasks.length} 项；更早任务仍可继续读取。` : `当前筛选显示最近 ${displayLimit} 项；更早任务仍保留在项目历史中。`}</p> : null}<TaskGroup title={taskFilter === "all" ? "全部任务" : taskFilter === "active" ? "进行中的研究" : taskFilter === "attention" ? "需要关注" : "最近完成与失败"} tasks={visibleTasks} empty={normalizedSearchQuery ? "没有匹配的任务，请尝试项目名、研究问题、状态或任务 ID。" : taskFilter === "active" ? "当前没有排队或运行中的研究。" : taskFilter === "attention" ? "当前没有需要关注的研究。" : "还没有可展示的历史任务。"} cancelingJobId={cancelingJobId} onCancel={(task) => setCancelConfirmTask(task)} />{hasMoreTasks ? <button type="button" className="task-center-load-more" onClick={() => displayLimit < searchedTasks.length ? setDisplayLimit((limit) => limit + 30) : void loadMoreTasks()} disabled={isLoadingMore}>{isLoadingMore ? "正在读取更早任务…" : displayLimit < searchedTasks.length ? "显示更多已加载任务" : "读取更早任务"}</button> : null}</> : null}
  </section></ProductShell></RequireProductAuth>;
}

function TaskGroup({ title, tasks, empty, cancelingJobId, onCancel }: { title: string; tasks: TaskRow[]; empty: string; cancelingJobId?: string | null; onCancel?: (task: TaskRow) => void }) {
    return <section className="task-center-section" aria-labelledby={`task-group-${title}`}><div className="product-section-heading"><h2 id={`task-group-${title}`}>{title}</h2><span>{tasks.length} 项</span></div>{tasks.length ? <div className="task-center-list">{tasks.map((task) => { const status = String(task.jobStatus || "").toLowerCase(); const retry = retryHref(task); const stale = taskIsStale(task); const staleRunning = status === "running" && stale; const cancelPending = isResearchCancellationPending(task.jobStatus); const canCancel = taskIsLive(task) && Boolean(task.researchTurnId); const timestamp = taskTimestamp(task); const timestampLabel = taskTimestampLabel(task); return <article className="task-center-row" key={`${task.projectId}:${task.jobId}`}><div className="task-center-row-main"><p className="product-kicker">{scientistProjectLabel(task.projectName, task.projectId)}</p><h3 className="task-row-heading"><span className={`task-status-badge task-status-${staleRunning ? "warning" : statusTone[status] || "pending"}`}>{staleRunning ? "需要关注" : taskLabel(task.jobStatus)}</span><span className="task-display-title">{taskDisplayTitle(task)}</span></h3><p>{task.artifactCount} 个 Artifact · {task.interpretationCount} 个解释 · {projectionLabel(task)}</p>{timestamp && timestampLabel ? <time className="task-row-timestamp" dateTime={timestamp}>{cancelPending ? `${RESEARCH_CANCELLING_LABEL} · ${timestampLabel}` : `更新于 ${timestampLabel}`}</time> : null}{stale ? <small className="task-stale-notice" role="status">{staleRunning ? "持久化状态仍为运行中，但已超过 15 分钟没有更新；打开研究核对最新状态。" : "超过 15 分钟没有状态更新；打开任务可查看最新持久化状态。"}</small> : null}<details className="task-technical-identity"><summary>技术身份</summary><code>{task.jobId}</code></details></div><div className="product-row-actions task-center-row-actions" aria-label={`${staleRunning ? "需要关注" : taskLabel(task.jobStatus)}操作`}><Link className="product-primary-action" href={taskHref(task)} title="恢复这条现有 ResearchTurn，不创建新运行">{staleRunning ? "打开并检查" : "打开"}</Link>{retry && ["failed", "cancelled", "canceled"].includes(status) ? <Link className="product-secondary-action" href={retry} title="创建新的 ResearchTurn；原失败运行及其证据保留">打开并重试（新运行）</Link> : null}{onCancel && canCancel ? <button type="button" className="product-secondary-action" onClick={() => onCancel(task)} disabled={cancelingJobId === task.jobId || cancelPending}>{cancelingJobId === task.jobId ? "正在提交停止…" : cancelPending ? `${RESEARCH_CANCELLING_LABEL}，等待服务端确认` : "停止研究"}</button> : null}</div></article>; })}</div> : <div className="product-state task-center-empty"><p>{empty}</p></div>}</section>;
}
