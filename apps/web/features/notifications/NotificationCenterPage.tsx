"use client";

import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { buildResearchHref } from "../../app/lib/research-navigation";
import { taskRecordTitle, taskResultSummary } from "../../app/lib/task-display";
import { productTaskSearchText, sortProductTaskRows, type ProductTaskSortOrder, type ProductTaskRow } from "../../app/lib/task-center-data";
import { refreshSharedProductTaskFeed, useProductTaskFeed } from "../../app/lib/use-product-task-feed";
import { ProductShell, RequireProductAuth } from "../../shared/layout/ProductShell";
import { scientistProjectLabel } from "../../shared/product-labels";
import { useNotificationReadState } from "./use-notification-read-state";

const statusLabels: Record<string, string> = {
  completed: "研究完成", succeeded: "研究完成", partial_success: "研究部分完成",
  failed: "研究失败", cancelled: "研究已取消", canceled: "研究已取消",
};
const statusTones: Record<string, string> = {
  completed: "success", succeeded: "success", partial_success: "warning",
  failed: "danger", cancelled: "muted", canceled: "muted",
};
const normalizedStatus = (item: ProductTaskRow) => String(item.jobStatus || "").trim().toLowerCase();
const itemKey = (item: ProductTaskRow) => `${item.projectId}:${item.jobId}`;
type NotificationFilter = "all" | "unread" | "attention" | "completed" | "cancelled";

export function NotificationCenterPage() {
  const [filter, setFilter] = useState<NotificationFilter>("all");
  const [displayLimit, setDisplayLimit] = useState(30);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortOrder, setSortOrder] = useState<ProductTaskSortOrder>("recent");
  const filterButtons = useRef<Array<HTMLButtonElement | null>>([]);
  const sharedFeed = useProductTaskFeed();
  const feed = sharedFeed.feed;
  const reading = useNotificationReadState();
  const refreshReading = reading.refresh;
  useEffect(() => { void refreshReading(); }, [feed, refreshReading]);

  const items = useMemo(() => (feed?.rows ?? []).filter((item) => Object.hasOwn(statusLabels, normalizedStatus(item))), [feed?.rows]);
  const unreadItems = items.filter((item) => !reading.readKeys.has(itemKey(item)));
  const attentionItems = items.filter((item) => ["failed", "partial_success"].includes(normalizedStatus(item)));
  const completedItems = items.filter((item) => ["completed", "succeeded"].includes(normalizedStatus(item)));
  const cancelledItems = items.filter((item) => ["cancelled", "canceled"].includes(normalizedStatus(item)));
  const filteredItems = filter === "unread" ? (reading.loaded ? unreadItems : []) : filter === "attention" ? attentionItems : filter === "completed" ? completedItems : filter === "cancelled" ? cancelledItems : items;
  const query = searchQuery.trim().toLocaleLowerCase("zh-CN");
  const searchedItems = sortProductTaskRows(filteredItems.filter((item) => !query || productTaskSearchText(item).includes(query)), sortOrder);
  const visibleItems = searchedItems.slice(0, displayLimit);
  const hasMoreLoaded = visibleItems.length < searchedItems.length;
  const state = feed && feed.projectCount > 0 && feed.unavailableProjectCount === feed.projectCount ? "error" : sharedFeed.state === "idle" ? "loading" : sharedFeed.state;
  useEffect(() => { setDisplayLimit(30); }, [filter, searchQuery, sortOrder]);
  const filters: Array<{ key: NotificationFilter; label: string; count: number | string; disabled?: boolean }> = [
    { key: "all", label: "全部", count: items.length },
    { key: "unread", label: "未读", count: reading.loaded ? unreadItems.length : "—", disabled: !reading.loaded },
    { key: "attention", label: "需要关注", count: attentionItems.length },
    { key: "completed", label: "已完成", count: completedItems.length },
    { key: "cancelled", label: "已取消", count: cancelledItems.length },
  ];

  return <RequireProductAuth><ProductShell><section className="document-page task-center-page notification-center-page">
    <header className="product-page-heading">
      <div><h1>通知中心</h1><p>查看研究完成、失败和取消的最新消息。</p>{feed?.loadedAt ? <small className="task-center-sync-status" role="status">{sharedFeed.isRefreshing ? "正在同步最新状态…" : "最近同步 " + new Date(feed.loadedAt).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</small> : null}</div>
      <button type="button" className="product-secondary-action" disabled={state === "loading" || sharedFeed.isRefreshing} onClick={() => { void refreshSharedProductTaskFeed({ forceRefresh: true }); void refreshReading(); }}>{state === "loading" ? "正在加载…" : sharedFeed.isRefreshing ? "正在同步…" : "重新加载"}</button>
    </header>
    {state === "loading" ? <div className="product-loading" role="status">正在读取通知…</div> : null}
    {state === "error" ? <div className="product-state" role="alert"><h2>通知暂时无法读取</h2><p>已有研究不会丢失，请检查服务连接后重新加载。</p></div> : null}
    {sharedFeed.refreshError ? <p className="product-form-error" role="status">同步失败，当前显示上次结果；请稍后重新加载。</p> : null}
    {reading.readError ? <div className="product-search-recovery" role="status"><p className="product-form-error">{reading.loaded ? "阅读状态未能更新，暂用上次结果。" : "阅读状态暂时无法读取，通知仍可打开。"}</p><button type="button" className="product-secondary-action" disabled={reading.loading} onClick={() => void refreshReading()}>重试阅读状态</button></div> : null}
    {state === "ready" && feed?.unavailableProjectCount ? <div className="product-state task-center-partial-state" role="alert"><strong>{feed.unavailableProjectCount} 个项目暂未同步</strong><p>已加载的通知仍可打开，请重新加载以更新其余项目。</p></div> : null}
    {state === "ready" ? <>
      <div className="task-center-filters" role="tablist" aria-label="通知筛选">{filters.map((entry, index) => <button
        key={entry.key} ref={(element) => { filterButtons.current[index] = element; }} id={`notification-filter-${entry.key}`}
        type="button" role="tab" aria-controls="notification-results" aria-selected={filter === entry.key} tabIndex={filter === entry.key ? 0 : -1}
        disabled={entry.disabled} className={filter === entry.key ? "active" : ""} onClick={() => setFilter(entry.key)}
        onKeyDown={(event) => {
          let next = event.key === "Home" ? 0 : event.key === "End" ? filters.length - 1 : event.key === "ArrowRight" ? (index + 1) % filters.length : event.key === "ArrowLeft" ? (index + filters.length - 1) % filters.length : null;
          if (next === null) return;
          event.preventDefault();
          while (filters[next].disabled) next = (next + (event.key === "ArrowLeft" ? filters.length - 1 : 1)) % filters.length;
          setFilter(filters[next].key); filterButtons.current[next]?.focus();
        }}
      >{entry.label} <span>{entry.count}</span></button>)}</div>
      <div className="task-center-list-tools">
        <label htmlFor="notification-center-search">查找通知<input id="notification-center-search" type="search" value={searchQuery} placeholder="搜索项目、研究问题或状态" onChange={(event) => setSearchQuery(event.target.value)} /></label>
        <label htmlFor="notification-center-sort">排序<select id="notification-center-sort" value={sortOrder} onChange={(event) => setSortOrder(event.target.value as ProductTaskSortOrder)}><option value="recent">最近更新</option><option value="oldest">最早更新</option></select></label>
      </div>
      <section id="notification-results" role="tabpanel" className="task-center-section notification-center-section" aria-labelledby={`notification-filter-${filter}`}>
        <h2 className="sr-only">{filter === "all" ? "最近通知" : filter === "unread" ? "未读通知" : filter === "attention" ? "需要关注" : filter === "completed" ? "已完成研究" : "已取消研究"}</h2>
        {hasMoreLoaded ? <p className="task-center-bounded-notice" role="status">当前显示 {visibleItems.length} 条，还有 {searchedItems.length - visibleItems.length} 条匹配通知可查看。</p> : null}
        {visibleItems.length ? <div className="task-center-list">{visibleItems.map((item) => {
          const key = itemKey(item), status = normalizedStatus(item), isRead = reading.readKeys.has(key), saving = reading.savingKeys.has(key);
          const timestamp = item.updatedAt || item.createdAt;
          const date = timestamp ? new Date(timestamp) : null;
          return <article className={`task-center-row${reading.loaded ? isRead ? " notification-read" : " notification-unread" : ""}`} key={key} aria-busy={saving}>
            <div className="task-center-row-main">
              <h3 className="task-row-heading"><span className="task-display-title">{taskRecordTitle(item)}</span><span className={`task-status-badge task-status-${statusTones[status]}`}>{statusLabels[status]}</span></h3>
              <div className="task-record-meta"><Link href={`/projects/${encodeURIComponent(item.projectId)}`}>{scientistProjectLabel(item.projectName, item.projectId)}</Link>{date && !Number.isNaN(date.getTime()) ? <time dateTime={timestamp!}>更新于 {date.toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" })}</time> : null}</div>
              <p>{taskResultSummary(item)} <span className="notification-read-state">· {reading.loaded ? isRead ? "已读" : "未读" : reading.readError ? "阅读状态待确认" : "正在读取阅读状态…"}</span></p>
              {reading.saveErrors.has(key) ? <p className="notification-save-error" role="alert">未能确认阅读状态，请重试。研究仍可查看。</p> : null}
            </div>
            <details className="task-technical-identity"><summary>通知详情</summary><dl><dt>任务编号</dt><dd><code>{item.jobId}</code></dd>{item.researchTurnId ? <><dt>研究编号</dt><dd><code>{item.researchTurnId}</code></dd></> : null}{item.datasetId ? <><dt>来源数据</dt><dd><Link href={`/projects/${encodeURIComponent(item.projectId)}/data?dataset=${encodeURIComponent(item.datasetId)}`}>查看源数据</Link></dd></> : null}</dl></details>
            <div className="product-row-actions task-center-row-actions">
              <button type="button" className="product-secondary-action" disabled={!reading.loaded || saving} onClick={async () => {
                const saved = await reading.setRead(item.projectId, item.jobId, !isRead);
                if (saved && filter === "unread" && !isRead) filterButtons.current[1]?.focus();
              }}>{saving ? "正在保存…" : isRead ? "标为未读" : "标为已读"}</button>
              <Link className="product-secondary-action" href={buildResearchHref(item)} onClick={() => { if (reading.loaded && !isRead) void reading.setRead(item.projectId, item.jobId, true); }}>查看研究</Link>
            </div>
          </article>;
        })}</div> : <div className="product-state task-center-empty"><p>{query ? "没有匹配的通知。试试其他关键词，或清除搜索。" : filter === "unread" ? reading.loaded ? "没有未读通知。" : "阅读状态尚未确认，请重试读取。" : filter === "all" ? "暂无研究通知，研究结束后会在这里显示。" : "当前筛选下没有通知。"}</p>{query ? <button type="button" className="product-secondary-action" onClick={() => { setSearchQuery(""); document.getElementById("notification-center-search")?.focus(); }}>清除搜索</button> : <Link className="product-secondary-action" href="/tasks">查看任务</Link>}</div>}
        {hasMoreLoaded ? <button type="button" className="task-center-load-more" onClick={() => setDisplayLimit((limit) => limit + 30)}>显示更多通知</button> : null}
        {feed?.truncated ? <p className="notification-history-link">这里显示近期通知。<Link href="/tasks">到任务中心查找更早记录</Link></p> : null}
      </section>
    </> : null}
  </section></ProductShell></RequireProductAuth>;
}
