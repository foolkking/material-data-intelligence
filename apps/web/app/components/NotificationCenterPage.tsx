"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { listProjects, type ProjectSummary } from "../lib/planner-api";
import { listWorkspaceAnalysisJobs, type WorkspaceAnalysisJobSummary } from "../lib/workspace-api";
import { ProductShell, RequireProductAuth } from "./ProductShell";

type NotificationRow = WorkspaceAnalysisJobSummary & { projectName: string };

const statusLabel: Record<string, string> = {
  completed: "研究完成",
  partial_success: "研究部分完成",
  failed: "研究失败",
  cancelled: "研究已取消",
  canceled: "研究已取消",
};

const notificationHref = (item: NotificationRow) => item.workspaceId
  ? `/workspaces/${encodeURIComponent(item.workspaceId)}`
  : `/projects/${encodeURIComponent(item.projectId)}/research?run=${encodeURIComponent(item.jobId)}`;
const notificationRetryHref = (item: NotificationRow) => item.workspaceId || !item.researchTurnId
  ? null
  : `/projects/${encodeURIComponent(item.projectId)}/research?run=${encodeURIComponent(item.jobId)}&turn=${encodeURIComponent(item.researchTurnId)}`;

function notificationLabel(status: string | null) {
  return statusLabel[String(status || "").toLowerCase()] || "研究状态更新";
}

export function NotificationCenterPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [items, setItems] = useState<NotificationRow[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [reloadKey, setReloadKey] = useState(0);
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
      setItems(rows.filter((item) => Object.prototype.hasOwnProperty.call(statusLabel, String(item.jobStatus || "").toLowerCase())));
      setLastUpdatedAt(new Date().toISOString());
      setState("ready");
    }).catch(() => { if (active) setState("error"); });
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

  const unreadLikeCount = useMemo(
    () => items.filter((item) => ["failed", "partial_success", "cancelled", "canceled"].includes(String(item.jobStatus || "").toLowerCase())).length,
    [items],
  );

  return <RequireProductAuth><ProductShell><main className="document-page task-center-page notification-center-page">
    <header className="product-page-heading"><div><p className="product-kicker">通知</p><h1>通知中心</h1><p>通知来自已持久化的研究运行状态。打开后可回到对应研究，不会重新执行科学分析。</p>{lastUpdatedAt ? <small className="task-center-sync-status" role="status">最近同步 {new Date(lastUpdatedAt).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</small> : null}</div><button type="button" className="product-secondary-action" onClick={() => setReloadKey((value) => value + 1)} disabled={state === "loading"}>{state === "loading" ? "正在加载…" : "重新加载"}</button></header>
    {state === "loading" ? <div className="product-loading" role="status">正在读取通知…</div> : null}
    {state === "error" ? <div className="product-state" role="alert"><h2>通知暂时无法读取</h2><p>已有研究不会丢失，请检查服务连接后重新加载。</p></div> : null}
    {state === "ready" ? <>
      <section className="task-center-summary" aria-label="通知概览"><div><strong>{items.length}</strong><span>最近更新</span></div><div><strong>{unreadLikeCount}</strong><span>需要关注</span></div><div><strong>{projects.length}</strong><span>授权项目</span></div></section>
      <section className="task-center-section" aria-labelledby="notification-list-title"><div className="product-section-heading"><h2 id="notification-list-title">最近通知</h2><span>{items.length} 项</span></div>{items.length ? <div className="task-center-list">{items.slice(0, 30).map((item) => { const retry = notificationRetryHref(item); const status = String(item.jobStatus || "").toLowerCase(); return <article className="task-center-row" key={`${item.projectId}:${item.jobId}`}><div><p className="product-kicker">{item.projectName}</p><h3>{notificationLabel(item.jobStatus)}</h3><p>{item.artifactCount} 个 Artifact · {item.interpretationCount} 个解释 · {item.workspaceProjectionStatus}</p></div><div className="product-row-actions"><Link className="product-secondary-action" href={notificationHref(item)}>打开研究</Link>{retry && ["failed", "cancelled", "canceled"].includes(status) ? <Link className="product-secondary-action" href={retry}>打开并重试</Link> : null}</div></article>; })}</div> : <div className="product-state task-center-empty"><p>暂无新的研究通知。</p></div>}</section>
    </> : null}
  </main></ProductShell></RequireProductAuth>;
}
