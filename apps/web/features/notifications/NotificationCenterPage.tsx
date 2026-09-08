"use client";

import { ProductLink as Link } from "../../app/components/ProductNavigation";
import { useEffect, useMemo, useState } from "react";
import { buildResearchHref } from "../../app/lib/research-navigation";
import {
  listNotificationReadStates,
  updateNotificationReadState,
} from "../../app/lib/product-api";
import {
  productTaskSearchText,
  sortProductTaskRows,
  type ProductTaskSortOrder,
  type ProductTaskRow,
} from "../../app/lib/task-center-data";
import {
  refreshSharedProductTaskFeed,
  useProductTaskFeed,
} from "../../app/lib/use-product-task-feed";
import { ProductShell, RequireProductAuth } from "../../app/components/ProductShell";

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
  if (item.researchQuestion) return item.researchQuestion;
  if (item.researchTurnId) return "研究会话更新";
  if (item.workspaceId) return "工作台研究更新";
  if (item.workspaceProjectionStatus === "LEGACY_READ_ONLY") return "历史研究更新";
  return "研究状态更新";
};
const notificationTimestamp = (item: NotificationRow) => item.updatedAt || item.createdAt;
const notificationTimestampLabel = (item: NotificationRow) => {
  const value = notificationTimestamp(item);
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

function notificationLabel(status: string | null) {
  return statusLabel[String(status || "").toLowerCase()] || "研究状态更新";
}

export function NotificationCenterPage() {
  const [notificationFilter, setNotificationFilter] = useState<"all" | "unread" | "attention" | "completed" | "cancelled">("all");
  const [displayLimit, setDisplayLimit] = useState(30);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortOrder, setSortOrder] = useState<ProductTaskSortOrder>("recent");
  const [readKeys, setReadKeys] = useState<Set<string>>(new Set());
  const [readStateError, setReadStateError] = useState(false);
  const [updatingReadKey, setUpdatingReadKey] = useState<string | null>(null);
  const sharedFeed = useProductTaskFeed();
  const feed = sharedFeed.feed;
  const items = useMemo(
    () =>
      (feed?.rows ?? []).filter((item) =>
        Object.prototype.hasOwnProperty.call(
          statusLabel,
          String(item.jobStatus || "").toLowerCase(),
        ),
      ),
    [feed?.rows],
  );
  const projectCount = feed?.projectCount ?? 0;
  const unavailableProjectCount = feed?.unavailableProjectCount ?? 0;
  const feedTruncated = Boolean(feed?.truncated);
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

  useEffect(() => {
    let active = true;
    void listNotificationReadStates()
      .then((result) => {
        if (!active) return;
        setReadKeys(
          new Set(result.items.map((item) => `${item.projectId}:${item.jobId}`)),
        );
        setReadStateError(false);
      })
      .catch(() => {
        if (active) setReadStateError(true);
      });
    return () => {
      active = false;
    };
  }, [feed?.loadedAt]);

  const unreadItems = useMemo(
    () => items.filter((item) => !readKeys.has(`${item.projectId}:${item.jobId}`)),
    [items, readKeys],
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
    if (notificationFilter === "unread") return unreadItems;
    if (notificationFilter === "attention") return attentionItems;
    if (notificationFilter === "completed") return completedItems;
    if (notificationFilter === "cancelled") return cancelledItems;
    return items;
  }, [attentionItems, cancelledItems, completedItems, items, notificationFilter, unreadItems]);
  const normalizedSearchQuery = searchQuery.trim().toLocaleLowerCase("zh-CN");
  const searchedItems = useMemo(
    () =>
      sortProductTaskRows(
        visibleItems.filter(
          (item) =>
            !normalizedSearchQuery ||
            productTaskSearchText(item).includes(normalizedSearchQuery),
        ),
        sortOrder,
      ),
    [normalizedSearchQuery, sortOrder, visibleItems],
  );
  useEffect(() => {
    setDisplayLimit(30);
  }, [notificationFilter, searchQuery, sortOrder]);
  const boundedVisibleItems = searchedItems.slice(0, displayLimit);
  const hasMoreVisibleItems = feedTruncated || searchedItems.length > boundedVisibleItems.length;
  const setNotificationRead = async (item: NotificationRow, read: boolean) => {
    const key = `${item.projectId}:${item.jobId}`;
    setUpdatingReadKey(key);
    try {
      await updateNotificationReadState(item.projectId, item.jobId, read);
      setReadKeys((current) => {
        const next = new Set(current);
        if (read) next.add(key);
        else next.delete(key);
        return next;
      });
      setReadStateError(false);
    } catch {
      setReadStateError(true);
    } finally {
      setUpdatingReadKey(null);
    }
  };

  return <RequireProductAuth><ProductShell><section className="document-page task-center-page notification-center-page">
    <header className="product-page-heading"><div><p className="product-kicker">通知</p><h1>通知中心</h1><p>通知来自已持久化的研究运行状态。打开后可回到对应研究，不会重新执行科学分析。</p>{lastUpdatedAt ? <small className="task-center-sync-status" role="status">{isRefreshing ? "正在同步最新状态…" : "最近同步 " + new Date(lastUpdatedAt).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</small> : null}</div><button type="button" className="product-secondary-action" onClick={() => void refreshSharedProductTaskFeed({ forceRefresh: true })} disabled={state === "loading" || isRefreshing}>{state === "loading" ? "正在加载…" : isRefreshing ? "正在同步…" : "重新加载"}</button></header>
    {state === "loading" ? <div className="product-loading" role="status">正在读取通知…</div> : null}
    {state === "error" ? <div className="product-state" role="alert"><h2>通知暂时无法读取</h2><p>已有研究不会丢失，请检查服务连接后重新加载。</p></div> : null}
    {refreshError ? <p className="product-form-error" role="status">同步失败，当前显示上次结果；请稍后重新加载。</p> : null}
    {readStateError ? <p className="product-form-error" role="status">通知阅读状态暂时无法同步；研究内容仍可正常打开。</p> : null}
    {state === "ready" && unavailableProjectCount ? <div className="product-state task-center-partial-state" role="alert"><strong>{unavailableProjectCount} 个项目暂未同步</strong><p>已加载的通知仍可打开；重新加载会补取其余项目，不会重新执行研究。</p></div> : null}
    {state === "ready" ? <>
      <section className="task-center-summary" aria-label="通知概览"><div><strong>{items.length}</strong><span>最近更新</span></div><div><strong>{unreadItems.length}</strong><span>未读</span></div><div><strong>{projectCount}</strong><span>授权项目</span></div></section>
      <div className="task-center-filters" role="tablist" aria-label="通知筛选"><button type="button" role="tab" aria-selected={notificationFilter === "all"} className={notificationFilter === "all" ? "active" : ""} onClick={() => setNotificationFilter("all")}>全部 <span>{items.length}</span></button><button type="button" role="tab" aria-selected={notificationFilter === "unread"} className={notificationFilter === "unread" ? "active" : ""} onClick={() => setNotificationFilter("unread")}>未读 <span>{unreadItems.length}</span></button><button type="button" role="tab" aria-selected={notificationFilter === "attention"} className={notificationFilter === "attention" ? "active" : ""} onClick={() => setNotificationFilter("attention")}>需要关注 <span>{attentionItems.length}</span></button><button type="button" role="tab" aria-selected={notificationFilter === "completed"} className={notificationFilter === "completed" ? "active" : ""} onClick={() => setNotificationFilter("completed")}>已完成 <span>{completedItems.length}</span></button><button type="button" role="tab" aria-selected={notificationFilter === "cancelled"} className={notificationFilter === "cancelled" ? "active" : ""} onClick={() => setNotificationFilter("cancelled")}>已取消 <span>{cancelledItems.length}</span></button></div>
      <div className="task-center-list-tools"><label htmlFor="notification-center-search">查找通知<input id="notification-center-search" type="search" value={searchQuery} placeholder="按项目、研究问题、状态或任务 ID 搜索" onChange={(event) => setSearchQuery(event.target.value)} /></label><label htmlFor="notification-center-sort">排序<select id="notification-center-sort" value={sortOrder} onChange={(event) => setSortOrder(event.target.value as ProductTaskSortOrder)}><option value="recent">最近更新</option><option value="oldest">最早更新</option></select></label></div>
      <section className="task-center-section notification-center-section" aria-labelledby="notification-list-title"><div className="product-section-heading"><h2 id="notification-list-title">{notificationFilter === "all" ? "最近通知" : notificationFilter === "unread" ? "未读通知" : notificationFilter === "attention" ? "需要关注" : notificationFilter === "completed" ? "已完成研究" : "已取消研究"}</h2><span>{searchedItems.length} 项</span></div>{hasMoreVisibleItems ? <p className="task-center-bounded-notice" role="status">当前筛选显示最近 {displayLimit} 项；更早通知仍可从对应项目历史打开。</p> : null}{searchedItems.length ? <div className="task-center-list">{boundedVisibleItems.map((item) => { const retry = notificationRetryHref(item); const status = String(item.jobStatus || "").toLowerCase(); const timestamp = notificationTimestamp(item); const timestampLabel = notificationTimestampLabel(item); const notificationKey = `${item.projectId}:${item.jobId}`; const isRead = readKeys.has(notificationKey); return <article className={`task-center-row${isRead ? " notification-read" : " notification-unread"}`} key={notificationKey}><div className="task-center-row-main"><p className="product-kicker">{item.projectName} · {isRead ? "已读" : "未读"}</p><h3 className="task-row-heading"><span className={`task-status-badge task-status-${statusTone[status] || "pending"}`}>{notificationLabel(item.jobStatus)}</span><span className="task-display-title">{notificationTitle(item)}</span></h3><p>{item.artifactCount} 个 Artifact · {item.interpretationCount} 个解释 · {projectionLabel(item)}</p>{timestamp && timestampLabel ? <time className="task-row-timestamp" dateTime={timestamp}>更新于 {timestampLabel}</time> : null}<details className="task-technical-identity"><summary>技术身份</summary><code>{item.jobId}</code></details></div><div className="product-row-actions task-center-row-actions" aria-label={`${notificationLabel(item.jobStatus)}操作`}><button type="button" className="product-secondary-action" disabled={updatingReadKey === notificationKey} onClick={() => void setNotificationRead(item, !isRead)}>{updatingReadKey === notificationKey ? "正在同步…" : isRead ? "标为未读" : "标为已读"}</button><Link className="product-primary-action" href={notificationHref(item)} onClick={() => { if (!isRead) void setNotificationRead(item, true); }}>打开研究</Link>{retry && ["failed", "cancelled", "canceled"].includes(status) ? <Link className="product-secondary-action" href={retry}>打开并重试</Link> : null}</div></article>; })}</div> : <div className="product-state task-center-empty"><p>{normalizedSearchQuery ? "没有匹配的通知，请尝试项目名、研究问题、状态或任务 ID。" : notificationFilter === "all" ? "暂无新的研究通知。" : "当前筛选下没有通知。"}</p></div>}{hasMoreVisibleItems ? <button type="button" className="task-center-load-more" onClick={() => setDisplayLimit((limit) => limit + 30)}>显示更早通知</button> : null}</section>
    </> : null}
  </section></ProductShell></RequireProductAuth>;
}
