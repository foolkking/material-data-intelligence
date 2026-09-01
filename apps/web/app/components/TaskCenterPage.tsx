"use client";

import { ProductLink as Link } from "./ProductNavigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { cancelAgent2Execution } from "../lib/agent2-execution-api";
import type { ProjectSummary } from "../lib/planner-api";
import { buildResearchHref } from "../lib/research-navigation";
import {
  getProductTaskFeed,
  invalidateProductTaskFeed,
  type ProductTaskRow,
} from "../lib/task-center-data";
import { ProductShell, RequireProductAuth } from "./ProductShell";
import { ProductModal } from "./ObjectManagement";

type TaskRow = ProductTaskRow;
const statusLabel: Record<string, string> = {
  created: "已创建", queued: "排队中", running: "运行中", cancel_requested: "正在取消",
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
function taskIsLive(task: Pick<TaskRow, "jobStatus" | "workspaceProjectionStatus">) {
  const status = String(task.jobStatus || "").toLowerCase();
  return ["created", "queued", "running", "cancel_requested"].includes(status)
    && task.workspaceProjectionStatus !== "LEGACY_READ_ONLY";
}
const projectionLabel = (task: TaskRow) => {
  if (task.researchTurnId) return "可恢复研究会话";
  if (task.workspaceProjectionStatus === "LEGACY_READ_ONLY") return "历史运行 · 仅查看";
  return task.workspaceProjectionStatus;
};
const taskDisplayTitle = (task: TaskRow) => {
  if (task.researchTurnId) return "可恢复研究";
  if (task.workspaceId) return "工作台研究";
  if (task.workspaceProjectionStatus === "LEGACY_READ_ONLY") return "历史研究";
  return "研究任务";
};
const taskHref = (task: TaskRow) => buildResearchHref(task);
const retryHref = (task: TaskRow) => !task.researchTurnId
  ? null
  : buildResearchHref(task);

export function TaskCenterPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [tasks, setTasks] = useState<TaskRow[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [reloadKey, setReloadKey] = useState(0);
  const [cancelingJobId, setCancelingJobId] = useState<string | null>(null);
  const [cancelError, setCancelError] = useState<string | null>(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);
  const [unavailableProjectCount, setUnavailableProjectCount] = useState(0);
  const [taskFilter, setTaskFilter] = useState<"all" | "active" | "attention" | "completed">("all");
  const hasLoadedRef = useRef(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState(false);
  const [cancelConfirmTask, setCancelConfirmTask] = useState<TaskRow | null>(null);
  const [feedTruncated, setFeedTruncated] = useState(false);
  useEffect(() => {
    let active = true;
    if (hasLoadedRef.current) setIsRefreshing(true);
    else setState("loading");
    void getProductTaskFeed({ forceRefresh: reloadKey > 0 })
      .then((feed) => {
        if (!active) return;
        hasLoadedRef.current = true;
        setRefreshError(false);
        setProjects(feed.projects);
        setUnavailableProjectCount(feed.unavailableProjectCount);
        setFeedTruncated(Boolean(feed.truncated));
        if (
          feed.projects.length &&
          feed.unavailableProjectCount === feed.projects.length
        ) {
          setState("error");
          return;
        }
        setTasks(feed.rows);
        setLastUpdatedAt(feed.loadedAt);
        setState("ready");
        setIsRefreshing(false);
      })
      .catch(() => {
        if (!active) return;
        setIsRefreshing(false);
        if (!hasLoadedRef.current) setState("error");
        else setRefreshError(true);
      });
    return () => { active = false; };
  }, [reloadKey]);
  useEffect(() => {
    const refresh = () => setReloadKey((value) => value + 1);
    const onVisibility = () => { if (document.visibilityState === "visible") refresh(); };
    const onOnline = () => refresh();
    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("online", onOnline);
    const timer = window.setInterval(refresh, 30_000);
    return () => {
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("online", onOnline);
      window.clearInterval(timer);
    };
  }, []);
  const activeTasks = useMemo(() => tasks.filter(taskIsLive), [tasks]);
  const completedTasks = useMemo(() => tasks.filter((task) => !activeTasks.includes(task)), [activeTasks, tasks]);
  const attentionTasks = useMemo(() => completedTasks.filter((task) => ["failed", "partial_success", "cancelled", "canceled"].includes(String(task.jobStatus || "").toLowerCase())), [completedTasks]);
  const filteredTasks = useMemo(() => {
    if (taskFilter === "active") return activeTasks;
    if (taskFilter === "attention") return attentionTasks;
    if (taskFilter === "completed") return completedTasks;
    return tasks;
  }, [activeTasks, attentionTasks, completedTasks, taskFilter, tasks]);
  async function cancelTask(task: TaskRow) {
    if (!task.researchTurnId) return;
    setCancelConfirmTask(null);
    setCancelingJobId(task.jobId);
    setCancelError(null);
    try {
      await cancelAgent2Execution(task.researchTurnId);
      invalidateProductTaskFeed();
      setReloadKey((value) => value + 1);
    } catch (error) {
      setCancelError(error instanceof Error ? error.message : "停止请求未能提交");
    } finally {
      setCancelingJobId(null);
    }
  }
  const visibleTasks = filteredTasks.slice(0, 30);
  const hasMoreTasks = feedTruncated || filteredTasks.length > visibleTasks.length;
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
      <p><strong>{taskDisplayTitle(cancelConfirmTask)}</strong> · {cancelConfirmTask.projectName}</p>
      <p>停止后可从任务中心打开这条记录，查看已完成的 Artifact，并根据实际状态继续、重试或重新研究。</p>
    </ProductModal> : null}
    <header className="product-page-heading"><div><p className="product-kicker">后台任务</p><h1>任务中心</h1><p>跨项目查看研究执行状态。任务状态来自持久化运行记录，离开页面后仍可从这里继续查看。</p>{lastUpdatedAt ? <small className="task-center-sync-status" role="status">{isRefreshing ? "正在同步最新状态…" : "最近同步 " + new Date(lastUpdatedAt).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</small> : null}</div><button type="button" className="product-secondary-action" onClick={() => setReloadKey((value) => value + 1)} disabled={state === "loading" || isRefreshing}>{state === "loading" ? "正在加载…" : isRefreshing ? "正在同步…" : "重新加载"}</button></header>
    {state === "loading" ? <div className="product-loading" role="status">正在加载后台任务…</div> : null}
    {state === "error" ? <div className="product-state" role="alert"><h2>任务暂时无法读取</h2><p>已有研究不会丢失，请检查服务连接后重新打开任务中心。</p></div> : null}
    {refreshError ? <p className="product-form-error" role="status">同步失败，当前显示上次结果；请稍后重新加载。</p> : null}
    {cancelError ? <p className="product-form-error" role="alert">{cancelError}</p> : null}
    {state === "ready" && unavailableProjectCount ? <div className="product-state task-center-partial-state" role="alert"><strong>{unavailableProjectCount} 个项目暂未同步</strong><p>已加载的任务仍可正常打开；使用“重新加载”补取其余项目，不会重启科学计算。</p></div> : null}
    {state === "ready" ? <><section className="task-center-summary" aria-label="任务概览"><div><strong>{activeTasks.length}</strong><span>进行中</span></div><div><strong>{attentionTasks.length}</strong><span>需要关注</span></div><div><strong>{projects.length}</strong><span>授权项目</span></div></section><div className="task-center-filters" role="tablist" aria-label="任务筛选"><button type="button" role="tab" aria-selected={taskFilter === "all"} className={taskFilter === "all" ? "active" : ""} onClick={() => setTaskFilter("all")}>全部 <span>{tasks.length}</span></button><button type="button" role="tab" aria-selected={taskFilter === "active"} className={taskFilter === "active" ? "active" : ""} onClick={() => setTaskFilter("active")}>进行中 <span>{activeTasks.length}</span></button><button type="button" role="tab" aria-selected={taskFilter === "attention"} className={taskFilter === "attention" ? "active" : ""} onClick={() => setTaskFilter("attention")}>需要关注 <span>{attentionTasks.length}</span></button><button type="button" role="tab" aria-selected={taskFilter === "completed"} className={taskFilter === "completed" ? "active" : ""} onClick={() => setTaskFilter("completed")}>已结束 <span>{completedTasks.length}</span></button></div>{hasMoreTasks ? <p className="task-center-bounded-notice" role="status">当前筛选显示最近 30 项；更早任务仍保留在项目历史中。</p> : null}<TaskGroup title={taskFilter === "all" ? "全部任务" : taskFilter === "active" ? "进行中的研究" : taskFilter === "attention" ? "需要关注" : "最近完成与失败"} tasks={visibleTasks} empty={taskFilter === "active" ? "当前没有排队或运行中的研究。" : taskFilter === "attention" ? "当前没有需要关注的研究。" : "还没有可展示的历史任务。"} cancelingJobId={cancelingJobId} onCancel={(task) => setCancelConfirmTask(task)} /></> : null}
  </section></ProductShell></RequireProductAuth>;
}

function TaskGroup({ title, tasks, empty, cancelingJobId, onCancel }: { title: string; tasks: TaskRow[]; empty: string; cancelingJobId?: string | null; onCancel?: (task: TaskRow) => void }) {
    return <section className="task-center-section" aria-labelledby={`task-group-${title}`}><div className="product-section-heading"><h2 id={`task-group-${title}`}>{title}</h2><span>{tasks.length} 项</span></div>{tasks.length ? <div className="task-center-list">{tasks.map((task) => { const status = String(task.jobStatus || "").toLowerCase(); const retry = retryHref(task); const stale = taskIsStale(task); const canCancel = taskIsLive(task) && Boolean(task.researchTurnId); return <article className="task-center-row" key={`${task.projectId}:${task.jobId}`}><div className="task-center-row-main"><p className="product-kicker">{task.projectName}</p><h3 className="task-row-heading"><span className={`task-status-badge task-status-${statusTone[status] || "pending"}`}>{taskLabel(task.jobStatus)}</span><span className="task-display-title">{taskDisplayTitle(task)}</span></h3><p>{task.artifactCount} 个 Artifact · {task.interpretationCount} 个解释 · {projectionLabel(task)}</p>{stale ? <small className="task-stale-notice" role="status">超过 15 分钟没有状态更新；打开任务可查看最新持久化状态。</small> : null}<details className="task-technical-identity"><summary>技术身份</summary><code>{task.jobId}</code></details></div><div className="product-row-actions task-center-row-actions" aria-label={`${taskLabel(task.jobStatus)}操作`}><Link className="product-primary-action" href={taskHref(task)}>打开</Link>{retry && ["failed", "cancelled", "canceled"].includes(status) ? <Link className="product-secondary-action" href={retry}>打开并重试</Link> : null}{onCancel && canCancel ? <button type="button" className="product-secondary-action" onClick={() => onCancel(task)} disabled={cancelingJobId === task.jobId || status === "cancel_requested"}>{cancelingJobId === task.jobId ? "正在停止…" : status === "cancel_requested" ? "正在取消" : "停止研究"}</button> : null}</div></article>; })}</div> : <div className="product-state task-center-empty"><p>{empty}</p></div>}</section>;
}
