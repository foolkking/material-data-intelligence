"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  deleteEmptyDataset, deleteEmptyProject, getDatasetDependencyImpact,
  getProjectDependencyImpact, searchProduct, type DependencyImpact, type ProductSearchItem,
} from "../../app/lib/planner-api";
import { ProductModal } from "../../shared/ui/ObjectManagement";
import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { ProductShell, RequireProductAuth } from "../../shared/layout/ProductShell";
import { TRASH_KIND_LABELS as LABELS, trashIdentity, trashRequest, trashRestoreBatches, type TrashKind } from "./trash-operations";

type Directory = {
  scope: string; items: ProductSearchItem[]; loading: boolean; error: boolean;
  cursor?: string | null; truncated?: boolean; append: boolean; changed?: boolean;
};
type Detail = {
  item: ProductSearchItem; state: "idle" | "loading" | "ready" | "error";
  impact?: DependencyImpact; error?: string; opener: HTMLElement | null;
};
const scopeKey = (query: string, filter: string) => JSON.stringify([query.trim(), filter]);

function updatedAt(value?: string | null) {
  if (!value || Number.isNaN(new Date(value).getTime())) return null;
  return new Date(value).toLocaleString("zh-CN", { year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}

export function TrashCenterPage() {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<TrashKind | "all">("all");
  const scope = scopeKey(query, filter);
  const currentScope = useRef(scope);
  currentScope.current = scope;
  const [directory, setDirectory] = useState<Directory>({ scope, items: [], loading: true, error: false, append: false });
  const [selecting, setSelecting] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [uncertain, setUncertain] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<{ error: boolean; text: string } | null>(null);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [confirmText, setConfirmText] = useState("");
  const readOwner = useRef<AbortController | null>(null);
  const detailOwner = useRef<AbortController | null>(null);
  const writeOwner = useRef<AbortController | null>(null);
  const alive = useRef(true);
  const feedbackRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const confirmationRef = useRef<HTMLInputElement>(null);
  const items = directory.scope === scope ? directory.items : [];
  const reading = directory.scope !== scope || directory.loading;
  const selectedItems = items.filter((item) => selected.includes(trashIdentity(item)) && !uncertain.includes(trashIdentity(item)));
  const selectableItems = items.filter((item) => !uncertain.includes(trashIdentity(item)));
  const allSelected = selectableItems.length > 0 && selectableItems.every((item) => selected.includes(trashIdentity(item)));

  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
      readOwner.current?.abort(); detailOwner.current?.abort(); writeOwner.current?.abort();
    };
  }, []);

  const load = useCallback(async (readQuery: string, readFilter: TrashKind | "all", cursor?: string) => {
    const requestScope = scopeKey(readQuery, readFilter);
    readOwner.current?.abort();
    const owner = new AbortController();
    readOwner.current = owner;
    setDirectory((old) => ({ ...(old.scope === requestScope ? old : { scope: requestScope, items: [] }), loading: true, error: false, append: Boolean(cursor) }));
    try {
      const response = await trashRequest((signal) => searchProduct(readQuery, {
        status: "trashed", limit: 100, ...(readFilter !== "all" ? { kind: readFilter } : {}), ...(cursor ? { cursor } : {}), signal,
      }), owner.signal);
      if (owner.signal.aborted || currentScope.current !== requestScope) return;
      if (response.query.trim() !== readQuery.trim() || (cursor && response.nextCursor === cursor)) throw new Error("Search response mismatch");
      const nextItems = response.items.filter((item) => item.kind in LABELS && item.id && item.projectId
        && item.status?.toLowerCase() === "trashed" && (readFilter === "all" || item.kind === readFilter));
      setDirectory((old) => ({ scope: requestScope, items: [...new Map([...(cursor ? old.items : []), ...nextItems].map((item) => [trashIdentity(item), item])).values()], loading: false, error: false, append: false, cursor: response.nextCursor, truncated: response.truncated }));
      // A fresh read of this exact record is required before retrying an uncertain write.
      setUncertain((old) => old.filter((key) => !nextItems.some((item) => trashIdentity(item) === key)));
      if (!cursor) setSelected((old) => old.filter((key) => nextItems.some((item) => trashIdentity(item) === key)));
    } catch {
      if (!owner.signal.aborted && currentScope.current === requestScope) setDirectory((old) => ({ ...old, loading: false, error: true }));
    }
  }, []);

  useEffect(() => {
    setSelected([]);
    const timer = window.setTimeout(() => void load(query.trim(), filter), query.trim() ? 250 : 0);
    return () => { window.clearTimeout(timer); readOwner.current?.abort(); };
  }, [query, filter, load]);

  useEffect(() => {
    if (detail?.state === "ready" && detail.impact?.canDelete) confirmationRef.current?.focus();
  }, [detail?.state, detail?.impact]);

  function announce(error: boolean, text: string) {
    setFeedback({ error, text });
    window.requestAnimationFrame(() => feedbackRef.current?.focus());
  }
  function remove(targets: ProductSearchItem[]) {
    const keys = new Set(targets.map(trashIdentity));
    setDirectory((old) => ({ ...old, items: old.items.filter((item) => !keys.has(trashIdentity(item))), changed: old.changed || Boolean(old.cursor) }));
    setSelected((old) => old.filter((key) => !keys.has(key)));
  }
  function closeDetail() {
    detailOwner.current?.abort();
    setDetail(null); setConfirmText("");
  }

  async function restore(targets: ProductSearchItem[]) {
    if (!targets.length || writeOwner.current || reading || targets.some((item) => uncertain.includes(trashIdentity(item)))) return;
    const owner = new AbortController(); writeOwner.current = owner;
    setBusy(true); announce(false, `正在恢复 ${targets.length} 项…`);
    let restored = 0;
    const failed: ProductSearchItem[] = [];
    await Promise.all(trashRestoreBatches(targets).map(async (batch) => {
      try {
        await trashRequest(batch.run, owner.signal);
        if (!alive.current || owner.signal.aborted) return;
        restored += batch.items.length;
        remove(batch.items);
        setFeedback({ error: false, text: `已恢复 ${restored} 项，正在处理其余内容…` });
      } catch {
        if (!alive.current || owner.signal.aborted) return;
        failed.push(...batch.items);
        setUncertain((old) => [...new Set([...old, ...batch.items.map(trashIdentity)])]);
      }
    }));
    if (!alive.current || owner.signal.aborted) return;
    writeOwner.current = null; setBusy(false);
    announce(failed.length > 0, failed.length
      ? `${restored ? `已恢复 ${restored} 项；` : ""}${failed.length} 项的恢复结果尚未确认。请刷新列表后查看，再决定是否重试。`
      : targets.length === 1 ? `已恢复“${targets[0].title}”。` : `已恢复 ${restored} 项。`);
  }

  async function inspectPurge() {
    if (!detail || writeOwner.current || detailOwner.current && detail.state === "loading") return;
    const { item } = detail;
    if (item.kind !== "project" && item.kind !== "dataset") return;
    detailOwner.current?.abort();
    const owner = new AbortController(); detailOwner.current = owner;
    setDetail({ ...detail, state: "loading", error: undefined }); setConfirmText("");
    try {
      const impact = await trashRequest((signal) => item.kind === "project" ? getProjectDependencyImpact(item.id, signal) : getDatasetDependencyImpact(item.id, signal), owner.signal);
      if (owner.signal.aborted || !alive.current) return;
      if (impact.entity !== item.kind || impact.entityId !== item.id || typeof impact.canDelete !== "boolean" || !Array.isArray(impact.dependencies)) throw new Error("Dependency response mismatch");
      setDetail((old) => old && ({ ...old, state: "ready", impact }));
    } catch {
      if (!owner.signal.aborted && alive.current) setDetail((old) => old && ({ ...old, state: "error", error: "暂时无法确认能否删除，请重试。内容尚未删除。" }));
    }
  }

  async function purge() {
    if (!detail?.impact?.canDelete || confirmText !== trashIdentity(detail.item) || writeOwner.current || uncertain.includes(trashIdentity(detail.item))) return;
    const { item } = detail;
    const owner = new AbortController(); writeOwner.current = owner;
    setBusy(true); setDetail({ ...detail, error: undefined });
    setFeedback({ error: false, text: `正在删除“${item.title}”…` });
    try {
      await trashRequest(async (signal) => {
        if (item.kind === "project") {
          const r = await deleteEmptyProject(item.id, signal);
          if (!r.deleted || r.projectId !== item.id) throw new Error("Delete response mismatch");
        } else if (item.kind === "dataset") {
          const r = await deleteEmptyDataset(item.id, signal);
          if (!r.deleted || r.datasetId !== item.id) throw new Error("Delete response mismatch");
        } else throw new Error("Unsupported purge target");
      }, owner.signal);
      if (!alive.current || owner.signal.aborted) return;
      remove([item]); closeDetail();
      announce(false, `已永久删除“${item.title}”。`);
    } catch {
      if (!alive.current || owner.signal.aborted) return;
      const text = "删除结果尚未确认。请关闭此窗口并刷新列表，确认内容状态后再操作。";
      setUncertain((old) => [...new Set([...old, trashIdentity(item)])]);
      setDetail((old) => old && ({ ...old, error: text }));
      setFeedback({ error: true, text });
    } finally {
      if (alive.current) { writeOwner.current = null; setBusy(false); }
    }
  }

  const canPurge = detail && ["project", "dataset"].includes(detail.item.kind);
  return <RequireProductAuth><ProductShell>
    <main className="document-page trash-center-page" aria-labelledby="trash-center-title">
      <header className="product-page-heading trash-center-heading">
        <div><h1 id="trash-center-title">回收站</h1><p>找回移除的内容，恢复后可在原来的位置继续使用。</p></div>
        <button className="product-secondary-action" type="button" disabled={reading || busy} onClick={() => void load(query.trim(), filter)}>{reading ? "正在读取…" : "刷新列表"}</button>
      </header>
      <div className="trash-toolbar">
        <label className="trash-search"><span className="sr-only">搜索回收站</span><input ref={searchRef} type="search" value={query} placeholder="搜索名称或关键词" disabled={busy} onChange={(event) => setQuery(event.target.value)} /></label>
        <div className="product-filter-row trash-center-filters" role="group" aria-label="回收站类型筛选" onKeyDown={(event) => {
          if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
          const buttons = [...event.currentTarget.querySelectorAll<HTMLButtonElement>("button:not(:disabled)")];
          const index = buttons.indexOf(document.activeElement as HTMLButtonElement);
          if (index < 0 || !buttons.length) return;
          event.preventDefault();
          const next = event.key === "Home" ? 0 : event.key === "End" ? buttons.length - 1 : (index + (event.key === "ArrowRight" ? 1 : -1) + buttons.length) % buttons.length;
          buttons[next].focus(); buttons[next].click();
        }}>
          {(["all", ...Object.keys(LABELS)] as Array<TrashKind | "all">).map((kind) => <button key={kind} type="button" className="product-filter-button" aria-pressed={filter === kind} disabled={busy} onClick={() => setFilter(kind)}>{kind === "all" ? "全部" : LABELS[kind]}</button>)}
        </div>
      </div>
      {feedback ? <div ref={feedbackRef} tabIndex={-1} className={feedback.error ? "product-form-error trash-feedback" : "product-form-success trash-feedback"} role={feedback.error ? "alert" : "status"}>{feedback.text}</div> : null}
      {directory.error && directory.scope === scope ? <div className="trash-read-state" role="alert">
        <strong>{items.length ? "列表暂时无法更新" : "回收站暂时无法读取"}</strong>
        <p>{items.length ? "已显示的内容仍在这里，请重试。" : "请检查连接后重试。"}</p>
        <button type="button" className="product-secondary-action" disabled={busy} onClick={() => void load(query.trim(), filter, directory.append ? directory.cursor || undefined : undefined)}>重新加载回收站</button>
      </div> : null}
      {reading ? <p role="status" className="trash-read-state">{items.length ? "正在更新列表…" : "正在读取回收站…"}</p> : null}
      {items.length ? <>
        <div className="trash-list-toolbar">
          <span>{directory.cursor || directory.truncated ? "已显示 " : ""}{items.length} 项</span>
          {selecting ? <div className="trash-bulk-actions">
            <label className="trash-select-all"><input type="checkbox" aria-label="选择当前显示的内容" checked={allSelected} disabled={busy || reading || !selectableItems.length} onChange={() => setSelected(allSelected ? [] : selectableItems.map(trashIdentity))} />全选</label>
            <button type="button" className="product-primary-action" disabled={busy || reading || !selectedItems.length} onClick={() => void restore(selectedItems)}>{busy ? "正在恢复…" : `恢复所选（${selectedItems.length}）`}</button>
            <button type="button" className="product-secondary-action" disabled={busy} onClick={() => { setSelecting(false); setSelected([]); }}>完成选择</button>
          </div> : <button type="button" className="product-secondary-action" disabled={busy || reading} onClick={() => setSelecting(true)}>批量选择</button>}
        </div>
        <section className="trash-center-list" aria-label="回收站内容">
          {items.map((item) => {
            const key = trashIdentity(item), waiting = uncertain.includes(key), date = updatedAt(item.updatedAt);
            return <article className="trash-center-row" key={key} data-selected={selected.includes(key)}>
              {selecting ? <label className="trash-row-selection"><input type="checkbox" aria-label={`选择 ${item.title}`} checked={selected.includes(key)} disabled={busy || reading || waiting} onChange={() => setSelected((old) => old.includes(key) ? old.filter((id) => id !== key) : [...old, key])} /></label> : null}
              <div className="trash-center-row-main"><h2>{item.title}</h2><div className="trash-center-row-meta"><span>{LABELS[item.kind as TrashKind]}</span>{date ? <span>更新于 {date}</span> : null}</div>{waiting ? <p className="trash-unconfirmed">操作结果待确认，请刷新列表。</p> : null}</div>
              {!selecting ? <div className="trash-center-row-actions"><button type="button" className="product-secondary-action" disabled={busy || reading || waiting} onClick={() => void restore([item])}>恢复</button><button type="button" className="product-link-button" disabled={busy} aria-label={`查看 ${item.title} 的详情`} onClick={(event) => { setDetail({ item, state: "idle", opener: event.currentTarget }); setConfirmText(""); }}>详情</button></div> : null}
            </article>;
          })}
        </section>
      </> : !reading && !directory.error ? <section className="trash-center-empty">
        <h2>{query.trim() || filter !== "all" ? "没有找到匹配的内容" : "回收站是空的"}</h2>
        <p>{query.trim() || filter !== "all" ? "试试其他关键词，或查看全部类型。" : "移除的内容会暂存在这里，需要时可以恢复。"}</p>
        {query.trim() || filter !== "all" ? <button className="product-secondary-action" type="button" onClick={() => { setQuery(""); setFilter("all"); searchRef.current?.focus(); }}>清除筛选</button> : <Link className="product-secondary-action" href="/projects">查看项目</Link>}
      </section> : null}
      {!reading && !directory.error && (directory.cursor || directory.truncated) ? <div className="trash-list-more"><p>{directory.changed ? "列表已变更，请刷新后继续查看。" : directory.cursor ? "还有内容未显示。" : "还有内容未显示，请缩小搜索范围。"}</p>{directory.cursor ? <button type="button" className="product-secondary-action" disabled={busy} onClick={() => void load(query.trim(), filter, directory.changed ? undefined : directory.cursor || undefined)}>{directory.changed ? "刷新后查看更多" : "显示更多"}</button> : null}</div> : null}
      <p className="trash-retention-note">这里的内容不会自动清空。</p>
      {detail ? <ProductModal eyebrow={LABELS[detail.item.kind as TrashKind]} title={detail.state === "ready" ? detail.impact?.canDelete ? "永久删除这项内容？" : "这项内容暂不能永久删除" : "内容详情"} description={detail.item.title} returnFocus={items.some((item) => trashIdentity(item) === trashIdentity(detail.item)) ? detail.opener : feedbackRef.current} onClose={closeDetail} footer={<>
        <button className="product-secondary-action" type="button" onClick={closeDetail}>关闭</button>
        {canPurge && detail.state !== "ready" ? <button className="product-link-button danger" type="button" disabled={busy || detail.state === "loading" || uncertain.includes(trashIdentity(detail.item))} onClick={() => void inspectPurge()}>{detail.state === "loading" ? "正在检查…" : detail.state === "error" ? "重新检查" : "永久删除…"}</button> : null}
        {detail.state === "ready" && detail.impact?.canDelete ? <button type="button" className="product-primary-action trash-delete-action" disabled={busy || uncertain.includes(trashIdentity(detail.item)) || confirmText !== trashIdentity(detail.item)} onClick={() => void purge()}>{busy ? "正在删除…" : "确认永久删除"}</button> : null}
      </>}>
        {detail.state !== "ready" ? <div className="trash-detail-content"><dl><dt>类型</dt><dd>{LABELS[detail.item.kind as TrashKind]}</dd>{updatedAt(detail.item.updatedAt) ? <><dt>更新时间</dt><dd>{updatedAt(detail.item.updatedAt)}</dd></> : null}<dt>内容编号</dt><dd><code>{detail.item.id}</code></dd></dl><Link className="product-secondary-action" href={detail.item.href}>查看原内容</Link></div> : <>
          <p>{detail.impact?.canDelete ? "这项内容没有关联记录，删除后无法恢复。" : "它仍有关联内容。你可以恢复它，或继续保留在回收站。"}</p>
          {detail.impact?.dependencies.length ? <ul className="trash-dependency-list">{detail.impact.dependencies.map((dependency) => <li key={dependency.kind}>{dependency.href ? <Link href={dependency.href}>{dependency.label}</Link> : <span>{dependency.label}</span>}<strong>{dependency.count}</strong></li>)}</ul> : null}
          {detail.impact?.canDelete ? <label className="trash-confirm-field">输入下面的内容编号以确认<strong>{trashIdentity(detail.item)}</strong><input ref={confirmationRef} value={confirmText} disabled={busy} onChange={(event) => setConfirmText(event.target.value)} autoComplete="off" aria-label="输入内容编号以确认永久删除" aria-describedby="trash-confirm-help" /><span id="trash-confirm-help">名称可能重复，内容编号可以避免删错。</span></label> : null}
        </>}
        {detail.state === "loading" ? <p role="status">正在检查关联内容…</p> : null}
        {detail.error ? <p className="product-form-error" role="alert">{detail.error}</p> : null}
      </ProductModal> : null}
    </main>
  </ProductShell></RequireProductAuth>;
}
