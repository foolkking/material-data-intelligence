"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { cancelAgent2Execution } from "../lib/agent2-execution-api";
import { listProjects, type ProjectSummary } from "../lib/planner-api";
import { listWorkspaceAnalysisJobs, type WorkspaceAnalysisJobSummary } from "../lib/workspace-api";
import { ProductShell, RequireProductAuth } from "./ProductShell";

type TaskRow = WorkspaceAnalysisJobSummary & { projectName: string };
const statusLabel: Record<string, string> = {
  created: "已创建", queued: "排队中", running: "运行中", cancel_requested: "正在取消",
  cancelled: "已取消", completed: "已完成", partial_success: "部分完成", failed: "失败",
};
const taskLabel = (status: string | null) => statusLabel[String(status || "").toLowerCase()] || "处理中";
const taskHref = (task: TaskRow) => task.workspaceId
  ? `/workspaces/${encodeURIComponent(task.workspaceId)}`
  : `/projects/${encodeURIComponent(task.projectId)}/research?run=${encodeURIComponent(task.jobId)}`;

export function TaskCenterPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [tasks, setTasks] = useState<TaskRow[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [reloadKey, setReloadKey] = useState(0);
  const [cancelingJobId, setCancelingJobId] = useState<string | null>(null);
  const [cancelError, setCancelError] = useState<string | null>(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    void listProjects().then(async (projectRows) => {
      if (!active) return;
      setProjects(projectRows);
      const results = await Promise.allSettled(projectRows.map(async (project) => {
        const projectId = project.projectId || project.id;
        const result = await listWorkspaceAnalysisJobs(projectId, { limit: 50 });
        return (result.data?.items || []).map((task) => ({ ...task, projectName: project.name }));
      }));
      if (!active) return;
      const rows = results.flatMap((result) => result.status === "fulfilled" ? result.value : []);
      rows.sort((left, right) => String(right.updatedAt || right.createdAt || "").localeCompare(String(left.updatedAt || left.createdAt || "")));
      setTasks(rows);
      setLastUpdatedAt(new Date().toISOString());
      setState("ready");
    }).catch(() => { if (active) setState("error"); });
    return () => { active = false; };
  }, [reloadKey]);
  useEffect(() => {
    const refresh = () => setReloadKey((value) => value + 1);
    const onVisibility = () => { if (document.visibilityState === "visible") refresh(); };
    document.addEventListener("visibilitychange", onVisibility);
    const timer = window.setInterval(refresh, 30_000);
    return () => { document.removeEventListener("visibilitychange", onVisibility); window.clearInterval(timer); };
  }, []);
  const activeTasks = useMemo(() => tasks.filter((task) => ["created", "queued", "running", "cancel_requested"].includes(String(task.jobStatus || "").toLowerCase())), [tasks]);
  const completedTasks = useMemo(() => tasks.filter((task) => !activeTasks.includes(task)), [activeTasks, tasks]);
  const attentionTasks = useMemo(() => completedTasks.filter((task) => ["failed", "partial_success", "cancelled", "canceled"].includes(String(task.jobStatus || "").toLowerCase())), [completedTasks]);
  async function cancelTask(task: TaskRow) {
    if (!task.researchTurnId) return;
    setCancelingJobId(task.jobId);
    setCancelError(null);
    try {
      await cancelAgent2Execution(task.researchTurnId);
      setReloadKey((value) => value + 1);
    } catch (error) {
      setCancelError(error instanceof Error ? error.message : "停止请求未能提交");
    } finally {
      setCancelingJobId(null);
    }
  }
  return <RequireProductAuth><ProductShell><main className="document-page task-center-page">
    <header className="product-page-heading"><div><p className="product-kicker">后台任务</p><h1>任务中心</h1><p>跨项目查看研究执行状态。任务状态来自持久化运行记录，离开页面后仍可从这里继续查看。</p>{lastUpdatedAt ? <small className="task-center-sync-status" role="status">最近同步 {new Date(lastUpdatedAt).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</small> : null}</div><button type="button" className="product-secondary-action" onClick={() => setReloadKey((value) => value + 1)} disabled={state === "loading"}>{state === "loading" ? "正在加载…" : "重新加载"}</button></header>
    {state === "loading" ? <div className="product-loading" role="status">正在加载后台任务…</div> : null}
    {state === "error" ? <div className="product-state" role="alert"><h2>任务暂时无法读取</h2><p>已有研究不会丢失，请检查服务连接后重新打开任务中心。</p></div> : null}
    {cancelError ? <p className="product-form-error" role="alert">{cancelError}</p> : null}
    {state === "ready" ? <><section className="task-center-summary" aria-label="任务概览"><div><strong>{activeTasks.length}</strong><span>进行中</span></div><div><strong>{completedTasks.length}</strong><span>已结束</span></div><div><strong>{projects.length}</strong><span>授权项目</span></div></section><TaskGroup title="进行中的研究" tasks={activeTasks} empty="当前没有排队或运行中的研究。" cancelingJobId={cancelingJobId} onCancel={cancelTask} />{attentionTasks.length ? <TaskGroup title="需要关注" tasks={attentionTasks.slice(0, 20)} empty="" /> : null}<TaskGroup title="最近完成与失败" tasks={completedTasks.slice(0, 20)} empty="还没有可展示的历史任务。" /></> : null}
  </main></ProductShell></RequireProductAuth>;
}

function TaskGroup({ title, tasks, empty, cancelingJobId, onCancel }: { title: string; tasks: TaskRow[]; empty: string; cancelingJobId?: string | null; onCancel?: (task: TaskRow) => void }) {
  return <section className="task-center-section" aria-labelledby={`task-group-${title}`}><div className="product-section-heading"><h2 id={`task-group-${title}`}>{title}</h2><span>{tasks.length} 项</span></div>{tasks.length ? <div className="task-center-list">{tasks.map((task) => <article className="task-center-row" key={`${task.projectId}:${task.jobId}`}><div><p className="product-kicker">{task.projectName}</p><h3>{taskLabel(task.jobStatus)} · {task.jobId}</h3><p>{task.artifactCount} 个 Artifact · {task.interpretationCount} 个解释 · {task.workspaceProjectionStatus}</p></div><div className="product-row-actions"><Link className="product-secondary-action" href={taskHref(task)}>打开</Link>{onCancel && task.researchTurnId ? <button type="button" className="product-secondary-action" onClick={() => onCancel(task)} disabled={cancelingJobId === task.jobId || String(task.jobStatus || "").toLowerCase() === "cancel_requested"}>{cancelingJobId === task.jobId ? "正在停止…" : String(task.jobStatus || "").toLowerCase() === "cancel_requested" ? "正在取消" : "停止研究"}</button> : null}</div></article>)}</div> : <div className="product-state task-center-empty"><p>{empty}</p></div>}</section>;
}
