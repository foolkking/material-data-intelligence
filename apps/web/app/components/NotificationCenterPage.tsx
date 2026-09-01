"use client";

import { ProductLink as Link } from "./ProductNavigation";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ProjectSummary } from "../lib/planner-api";
import { buildResearchHref } from "../lib/research-navigation";
import {
  getProductTaskFeed,
  type ProductTaskRow,
} from "../lib/task-center-data";
import { ProductShell, RequireProductAuth } from "./ProductShell";

type NotificationRow = ProductTaskRow;

const statusLabel: Record<string, string> = {
  completed: "研究完成",
  partial_success: "研究部分完成",
  failed: "研究失败",
  cancelled: "研究已取消",
  canceled: "研究已取消",
};
const statusTone: Record<string, string> = {
  completed: "success",
  partial_success: "warning",
  failed: "danger",
  cancelled: "muted",
  canceled: "muted",
};

const notificationHref = (item: NotificationRow) => buildResearchHref(item);
const notificationRetryHref = (item: NotificationRow) => !item.researchTurnId
  ? null
  : buildResearchHref(item);
const projectionLabel = (item: NotificationRow) => {
  if (item.researchTurnId) return "可恢复研究会话";
  if (item.workspaceProjectionStatus === "LEGACY_READ_ONLY") return "历史运行 · 仅查看";
  return item.workspaceProjectionStatus;
};
const notificationTitle = (item: NotificationRow) => {
  if (item.researchTurnId) return "研究会话更新";
  if (item.workspaceId) return "工作台研究更新";
  if (item.workspaceProjectionStatus === "LEGACY_READ_ONLY") return "历史研究更新";
  return "研究状态更新";
};

function notificationLabel(status: string | null) {
  return statusLabel[String(status || "").toLowerCase()] || "研究状态更新";
}

export function NotificationCenterPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [items, setItems] = useState<NotificationRow[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [reloadKey, setReloadKey] = useState(0);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);
  const [unavailableProjectCount, setUnavailableProjectCount] = useState(0);
  const [notificationFilter, setNotificationFilter] = useState<"all" | "attention" | "completed" | "cancelled">("all");
  const hasLoadedRef = useRef(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState(false);
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
        setItems(
          feed.rows.filter((item) =>
            Object.prototype.hasOwnProperty.call(
              statusLabel,
              String(item.jobStatus || "").toLowerCase(),
            ),
          ),
        );
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

  const unreadLikeCount = useMemo(
    () => items.filter((item) => ["failed", "partial_success", "cancelled", "canceled"].includes(String(item.jobStatus || "").toLowerCase())).length,
    [items],
  );
  const attentionItems = useMemo(
    () => items.filter((item) => ["failed", "partial_success"].includes(String(item.jobStatus || "").toLowerCase())),
    [items],
  );
  const completedItems = useMemo(
    () => items.filter((item) => String(item.jobStatus || "").toLowerCase() === "completed"),
    [items],
  );
  const cancelledItems = useMemo(
    () => items.filter((item) => ["cancelled", "canceled"].includes(String(item.jobStatus || "").toLowerCase())),
    [items],
  );
  const visibleItems = useMemo(() => {
    if (notificationFilter === "attention") return attentionItems;
    if (notificationFilter === "completed") return completedItems;
    if (notificationFilter === "cancelled") return cancelledItems;
    return items;
  }, [attentionItems, cancelledItems, completedItems, items, notificationFilter]);
  const boundedVisibleItems = visibleItems.slice(0, 30);
  const hasMoreVisibleItems = feedTruncated || visibleItems.length > boundedVisibleItems.length;

  return <RequireProductAuth><ProductShell><section className="document-page task-center-page notification-center-page">
    <header className="product-page-heading"><div><p className="product-kicker">通知</p><h1>通知中心</h1><p>通知来自已持久化的研究运行状态。打开后可回到对应研究，不会重新执行科学分析。</p>{lastUpdatedAt ? <small className="task-center-sync-status" role="status">{isRefreshing ? "正在同步最新状态…" : "最近同步 " + new Date(lastUpdatedAt).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</small> : null}</div><button type="button" className="product-secondary-action" onClick={() => setReloadKey((value) => value + 1)} disabled={state === "loading" || isRefreshing}>{state === "loading" ? "正在加载…" : isRefreshing ? "正在同步…" : "重新加载"}</button></header>
    {state === "loading" ? <div className="product-loading" role="status">正在读取通知…</div> : null}
    {state === "error" ? <div className="product-state" role="alert"><h2>通知暂时无法读取</h2><p>已有研究不会丢失，请检查服务连接后重新加载。</p></div> : null}
    {refreshError ? <p className="product-form-error" role="status">同步失败，当前显示上次结果；请稍后重新加载。</p> : null}
    {state === "ready" && unavailableProjectCount ? <div className="product-state task-center-partial-state" role="alert"><strong>{unavailableProjectCount} 个项目暂未同步</strong><p>已加载的通知仍可打开；重新加载会补取其余项目，不会重新执行研究。</p></div> : null}
    {state === "ready" ? <>
      <section className="task-center-summary" aria-label="通知概览"><div><strong>{items.length}</strong><span>最近更新</span></div><div><strong>{unreadLikeCount}</strong><span>需要关注</span></div><div><strong>{projects.length}</strong><span>授权项目</span></div></section>
      <div className="task-center-filters" role="tablist" aria-label="通知筛选"><button type="button" role="tab" aria-selected={notificationFilter === "all"} className={notificationFilter === "all" ? "active" : ""} onClick={() => setNotificationFilter("all")}>全部 <span>{items.length}</span></button><button type="button" role="tab" aria-selected={notificationFilter === "attention"} className={notificationFilter === "attention" ? "active" : ""} onClick={() => setNotificationFilter("attention")}>需要关注 <span>{attentionItems.length}</span></button><button type="button" role="tab" aria-selected={notificationFilter === "completed"} className={notificationFilter === "completed" ? "active" : ""} onClick={() => setNotificationFilter("completed")}>已完成 <span>{completedItems.length}</span></button><button type="button" role="tab" aria-selected={notificationFilter === "cancelled"} className={notificationFilter === "cancelled" ? "active" : ""} onClick={() => setNotificationFilter("cancelled")}>已取消 <span>{cancelledItems.length}</span></button></div>
      <section className="task-center-section notification-center-section" aria-labelledby="notification-list-title"><div className="product-section-heading"><h2 id="notification-list-title">{notificationFilter === "all" ? "最近通知" : notificationFilter === "attention" ? "需要关注" : notificationFilter === "completed" ? "已完成研究" : "已取消研究"}</h2><span>{visibleItems.length} 项</span></div>{hasMoreVisibleItems ? <p className="task-center-bounded-notice" role="status">当前筛选显示最近 30 项；更早通知仍可从对应项目历史打开。</p> : null}{visibleItems.length ? <div className="task-center-list">{boundedVisibleItems.map((item) => { const retry = notificationRetryHref(item); const status = String(item.jobStatus || "").toLowerCase(); return <article className="task-center-row" key={`${item.projectId}:${item.jobId}`}><div className="task-center-row-main"><p className="product-kicker">{item.projectName}</p><h3 className="task-row-heading"><span className={`task-status-badge task-status-${statusTone[status] || "pending"}`}>{notificationLabel(item.jobStatus)}</span><span className="task-display-title">{notificationTitle(item)}</span></h3><p>{item.artifactCount} 个 Artifact · {item.interpretationCount} 个解释 · {projectionLabel(item)}</p><details className="task-technical-identity"><summary>技术身份</summary><code>{item.jobId}</code></details></div><div className="product-row-actions task-center-row-actions" aria-label={`${notificationLabel(item.jobStatus)}操作`}><Link className="product-primary-action" href={notificationHref(item)}>打开研究</Link>{retry && ["failed", "cancelled", "canceled"].includes(status) ? <Link className="product-secondary-action" href={retry}>打开并重试</Link> : null}</div></article>; })}</div> : <div className="product-state task-center-empty"><p>{notificationFilter === "all" ? "暂无新的研究通知。" : "当前筛选下没有通知。"}</p></div>}</section>
    </> : null}
  </section></ProductShell></RequireProductAuth>;
}
