"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  bulkDatasetAction,
  bulkProjectAction,
  deleteEmptyDataset,
  deleteEmptyProject,
  getDatasetDependencyImpact,
  getProjectDependencyImpact,
  searchProduct,
  updateDataset,
  updateProject,
  type DependencyImpact,
  type ProductSearchItem,
} from "../../app/lib/planner-api";
import {
  bulkUpdateResearchSessions,
  updateResearchSession,
} from "../../app/lib/product-api";
import {
  bulkUpdateScientificReportLifecycle,
  updateScientificReportLifecycle,
} from "../../app/lib/scientific-report-api";
import {
  bulkUpdateScientificObjects,
  updateScientificObject,
} from "../../app/lib/scientific-viewer-api";
import { ProductModal } from "../../shared/ui/ObjectManagement";
import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { ProductShell, RequireProductAuth } from "../../shared/layout/ProductShell";

type TrashKind = Exclude<ProductSearchItem["kind"], "result">;
type PurgeTarget = {
  item: ProductSearchItem;
  impact: DependencyImpact;
};
type RestoreBatch = {
  label: string;
  items: ProductSearchItem[];
  run: () => Promise<{ count: number }>;
};

const KIND_LABELS: Record<TrashKind, string> = {
  project: "项目",
  dataset: "数据集",
  scientific_object: "科学对象",
  research: "研究会话",
  report: "科学报告",
};

const RESTORABLE_KINDS = new Set<ProductSearchItem["kind"]>([
  "project",
  "dataset",
  "scientific_object",
  "research",
  "report",
]);

function itemIdentity(item: ProductSearchItem) {
  return `${item.kind}:${item.id}`;
}

function purgeConfirmationToken(item: ProductSearchItem) {
  // Titles are user-editable and can collide. Require the stable server
  // identity instead so a destructive confirmation cannot be ambiguous.
  return itemIdentity(item);
}

function groupByProject(items: ProductSearchItem[]) {
  const groups = new Map<string, ProductSearchItem[]>();
  for (const item of items) {
    const projectItems = groups.get(item.projectId) || [];
    projectItems.push(item);
    groups.set(item.projectId, projectItems);
  }
  return groups;
}

function formatUpdatedAt(value?: string | null) {
  if (!value) return "更新时间未知";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "更新时间未知";
  return `更新于 ${parsed.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  })}`;
}

export function TrashCenterPage() {
  const [items, setItems] = useState<ProductSearchItem[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [filter, setFilter] = useState<TrashKind | "all">("all");
  const [busyId, setBusyId] = useState<string | null>(null);
  const [bulkBusy, setBulkBusy] = useState(false);
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);
  const [feedback, setFeedback] = useState<{ tone: "success" | "error"; text: string } | null>(null);
  const [purgeTarget, setPurgeTarget] = useState<PurgeTarget | null>(null);
  const [confirmText, setConfirmText] = useState("");

  const load = useCallback(async () => {
    setState("loading");
    setFeedback(null);
    try {
      const response = await searchProduct("", { status: "trashed", limit: 100 });
      setItems(
        response.items.filter(
          (item) =>
            RESTORABLE_KINDS.has(item.kind) &&
            String(item.status || "").toLowerCase() === "trashed",
        ),
      );
      setSelectedKeys([]);
      setState("ready");
    } catch {
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const counts = useMemo(() => {
    const next = new Map<TrashKind, number>();
    for (const item of items) {
      if (item.kind === "result") continue;
      next.set(item.kind, (next.get(item.kind) || 0) + 1);
    }
    return next;
  }, [items]);
  const visibleItems = filter === "all" ? items : items.filter((item) => item.kind === filter);
  const selectedItems = items.filter((item) =>
    selectedKeys.includes(itemIdentity(item)),
  );
  const allVisibleSelected =
    visibleItems.length > 0 &&
    visibleItems.every((item) => selectedKeys.includes(itemIdentity(item)));

  function toggleSelection(item: ProductSearchItem) {
    const key = itemIdentity(item);
    setSelectedKeys((current) =>
      current.includes(key)
        ? current.filter((candidate) => candidate !== key)
        : [...current, key],
    );
  }

  function toggleVisibleSelection() {
    const visibleKeys = visibleItems.map(itemIdentity);
    setSelectedKeys((current) =>
      allVisibleSelected
        ? current.filter((key) => !visibleKeys.includes(key))
        : [...new Set([...current, ...visibleKeys])],
    );
  }

  function restoreBatches(targets: ProductSearchItem[]): RestoreBatch[] {
    const batches: RestoreBatch[] = [];
    const projects = targets.filter((item) => item.kind === "project");
    const datasets = targets.filter((item) => item.kind === "dataset");
    if (projects.length) {
      batches.push({
        label: "项目",
        items: projects,
        run: () => bulkProjectAction(projects.map((item) => item.id), "restore"),
      });
    }
    if (datasets.length) {
      batches.push({
        label: "数据集",
        items: datasets,
        run: () => bulkDatasetAction(datasets.map((item) => item.id), "restore"),
      });
    }
    for (const [projectId, projectItems] of groupByProject(
      targets.filter((item) => item.kind === "scientific_object"),
    )) {
      batches.push({
        label: "科学对象",
        items: projectItems,
        run: () =>
          bulkUpdateScientificObjects(
            projectId,
            projectItems.map((item) => item.id),
            "ACTIVE",
          ),
      });
    }
    for (const [projectId, projectItems] of groupByProject(
      targets.filter((item) => item.kind === "research"),
    )) {
      batches.push({
        label: "研究会话",
        items: projectItems,
        run: () =>
          bulkUpdateResearchSessions(
            projectId,
            projectItems.map((item) => item.id),
            "RESTORE",
          ),
      });
    }
    for (const [projectId, projectItems] of groupByProject(
      targets.filter((item) => item.kind === "report"),
    )) {
      batches.push({
        label: "科学报告",
        items: projectItems,
        run: () =>
          bulkUpdateScientificReportLifecycle(
            projectId,
            projectItems.map((item) => item.id),
            "ACTIVE",
          ),
      });
    }
    return batches;
  }

  async function restoreSelected() {
    if (!selectedItems.length || bulkBusy) return;
    setBulkBusy(true);
    setFeedback(null);
    const batches = restoreBatches(selectedItems);
    const outcomes = await Promise.allSettled(
      batches.map(async (batch) => {
        const result = await batch.run();
        if (result.count !== batch.items.length) {
          throw new Error(`${batch.label}批次返回数量不完整`);
        }
        return batch;
      }),
    );
    const restoredKeys = new Set(
      outcomes.flatMap((outcome) =>
        outcome.status === "fulfilled"
          ? outcome.value.items.map(itemIdentity)
          : [],
      ),
    );
    const failedBatches = outcomes.flatMap((outcome, index) =>
      outcome.status === "rejected" ? [batches[index]] : [],
    );
    setItems((current) =>
      current.filter((item) => !restoredKeys.has(itemIdentity(item))),
    );
    setSelectedKeys((current) =>
      current.filter((key) => !restoredKeys.has(key)),
    );
    if (failedBatches.length) {
      const failedCount = failedBatches.reduce(
        (total, batch) => total + batch.items.length,
        0,
      );
      setFeedback({
        tone: "error",
        text: `已恢复 ${restoredKeys.size} 项；${failedCount} 项未恢复（${failedBatches.map((batch) => batch.label).join("、")}）。失败项仍保留在回收站并保持选中，请检查权限或服务后重试。`,
      });
    } else {
      setFeedback({
        tone: "success",
        text: `已恢复 ${restoredKeys.size} 项；科学历史与精确来源未发生变化。`,
      });
    }
    setBulkBusy(false);
  }

  async function restore(item: ProductSearchItem) {
    const key = itemIdentity(item);
    setBusyId(key);
    setFeedback(null);
    try {
      if (item.kind === "project") await updateProject(item.id, { lifecycle: "ACTIVE" });
      else if (item.kind === "dataset") await updateDataset(item.id, { lifecycle: "ACTIVE" });
      else if (item.kind === "scientific_object") await updateScientificObject(item.id, { lifecycle: "ACTIVE" });
      else if (item.kind === "research") await updateResearchSession(item.id, { lifecycle: "ACTIVE" });
      else if (item.kind === "report") await updateScientificReportLifecycle(item.id, "ACTIVE");
      else return;
      setItems((current) => current.filter((candidate) => itemIdentity(candidate) !== key));
      setSelectedKeys((current) => current.filter((candidate) => candidate !== key));
      setFeedback({ tone: "success", text: `“${item.title}”已恢复；科学历史与精确来源未发生变化。` });
    } catch (error) {
      setFeedback({
        tone: "error",
        text: error instanceof Error ? error.message : "恢复失败，请稍后重试。",
      });
    } finally {
      setBusyId(null);
    }
  }

  async function inspectPurge(item: ProductSearchItem) {
    if (item.kind !== "project" && item.kind !== "dataset") return;
    const key = itemIdentity(item);
    setBusyId(key);
    setFeedback(null);
    try {
      const impact =
        item.kind === "project"
          ? await getProjectDependencyImpact(item.id)
          : await getDatasetDependencyImpact(item.id);
      setConfirmText("");
      setPurgeTarget({ item, impact });
    } catch {
      setFeedback({ tone: "error", text: "依赖影响暂时无法读取，未执行永久删除。" });
    } finally {
      setBusyId(null);
    }
  }

  async function purge() {
    if (
      !purgeTarget ||
      !purgeTarget.impact.canDelete ||
      confirmText !== purgeConfirmationToken(purgeTarget.item)
    )
      return;
    const { item } = purgeTarget;
    const key = itemIdentity(item);
    setBusyId(key);
    try {
      if (item.kind === "project") await deleteEmptyProject(item.id);
      else if (item.kind === "dataset") await deleteEmptyDataset(item.id);
      else return;
      setItems((current) => current.filter((candidate) => itemIdentity(candidate) !== key));
      setPurgeTarget(null);
      setConfirmText("");
      setFeedback({ tone: "success", text: `空${KIND_LABELS[item.kind]}“${item.title}”已永久删除。` });
    } catch (error) {
      setFeedback({
        tone: "error",
        text: error instanceof Error ? error.message : "永久删除失败，记录保持在回收站中。",
      });
    } finally {
      setBusyId(null);
    }
  }

  return (
    <RequireProductAuth>
      <ProductShell>
        <main className="document-page trash-center-page" aria-labelledby="trash-center-title">
          <header className="product-page-heading trash-center-heading">
            <div>
              <p className="product-kicker">内容管理</p>
              <h1 id="trash-center-title">回收站</h1>
              <p>集中恢复已移除的项目、数据、科学对象、研究会话与报告。科学来源和历史证据受保护，不会因界面隐藏而删除。</p>
            </div>
            <button type="button" className="product-secondary-action" onClick={() => void load()} disabled={state === "loading"}>
              {state === "loading" ? "正在同步…" : "重新加载"}
            </button>
          </header>

          <aside className="trash-retention-note" aria-label="保留策略">
            <strong>可恢复保留</strong>
            <p>当前不自动清空回收站。只有无依赖的空项目或空数据集可由服务器确认后永久删除；受引用的科学版本、结果与报告继续保留以保证可复现性。</p>
          </aside>

          {feedback ? <p className={feedback.tone === "success" ? "product-form-success" : "product-form-error"} role={feedback.tone === "error" ? "alert" : "status"}>{feedback.text}</p> : null}
          {state === "loading" ? <div className="product-loading" role="status">正在读取回收站…</div> : null}
          {state === "error" ? (
            <div className="product-state" role="alert">
              <h2>回收站暂时无法读取</h2>
              <p>内容仍保留在服务器中，请检查连接后重新加载。</p>
              <button
                type="button"
                className="product-primary-action"
                onClick={() => void load()}
              >
                重新加载回收站
              </button>
            </div>
          ) : null}

          {state === "ready" ? (
            <>
              <div className="product-filter-row trash-center-filters" role="group" aria-label="回收站类型筛选">
                <button type="button" className="product-filter-button" aria-pressed={filter === "all"} onClick={() => setFilter("all")}>全部 <span>{items.length}</span></button>
                {(Object.keys(KIND_LABELS) as TrashKind[]).map((kind) => (
                  <button key={kind} type="button" className="product-filter-button" aria-pressed={filter === kind} onClick={() => setFilter(kind)}>
                    {KIND_LABELS[kind]} <span>{counts.get(kind) || 0}</span>
                  </button>
                ))}
              </div>
              {visibleItems.length ? (
                <div
                  className="product-filter-row"
                  role="group"
                  aria-label="批量恢复"
                >
                  <button
                    type="button"
                    className="product-secondary-action"
                    onClick={toggleVisibleSelection}
                    disabled={bulkBusy}
                  >
                    {allVisibleSelected ? "取消选择当前筛选" : "选择当前筛选"}
                  </button>
                  <span aria-live="polite">已选 {selectedItems.length} 项</span>
                  <button
                    type="button"
                    className="product-primary-action"
                    onClick={() => void restoreSelected()}
                    disabled={!selectedItems.length || bulkBusy}
                  >
                    {bulkBusy
                      ? "正在恢复所选内容…"
                      : `恢复所选（${selectedItems.length}）`}
                  </button>
                </div>
              ) : null}
              <section className="trash-center-list" aria-label="回收站内容" aria-live="polite">
                {visibleItems.length ? visibleItems.map((item) => {
                  const key = itemIdentity(item);
                  const canInspectPurge = item.kind === "project" || item.kind === "dataset";
                  return <article className="trash-center-row" key={key}>
                    <div className="trash-center-row-main">
                      <div className="trash-center-row-meta">
                        <span>{KIND_LABELS[item.kind as TrashKind]}</span>
                        <span>{formatUpdatedAt(item.updatedAt)}</span>
                      </div>
                      <h2>{item.title}</h2>
                      <p>{item.subtitle || "已移入回收站"}</p>
                      <details>
                        <summary>技术身份</summary>
                        <code>{item.id}</code>
                      </details>
                    </div>
                    <div className="product-row-actions trash-center-row-actions">
                      <label>
                        <input
                          type="checkbox"
                          checked={selectedKeys.includes(key)}
                          onChange={() => toggleSelection(item)}
                          disabled={bulkBusy || busyId === key}
                          aria-label={`选择恢复${KIND_LABELS[item.kind as TrashKind]}“${item.title}”`}
                        />
                        选择
                      </label>
                      <button type="button" className="product-primary-action" onClick={() => void restore(item)} disabled={bulkBusy || busyId === key}>
                        {busyId === key ? "处理中…" : "恢复"}
                      </button>
                      <Link className="product-secondary-action" href={item.href}>查看历史</Link>
                      {canInspectPurge ? <button type="button" className="product-link-button danger" onClick={() => void inspectPurge(item)} disabled={busyId === key}>永久删除…</button> : null}
                    </div>
                  </article>;
                }) : (
                  <div className="product-state trash-center-empty">
                    <h2>当前筛选下没有内容</h2>
                    <p>从项目、数据、研究或报告页面移入回收站的内容会显示在这里。</p>
                    <div className="trash-center-empty-actions">
                      <Link className="product-primary-action" href="/projects">查看项目</Link>
                      <Link className="product-secondary-action" href="/console">返回控制台</Link>
                    </div>
                  </div>
                )}
              </section>
            </>
          ) : null}

          {purgeTarget ? <ProductModal
            eyebrow="永久删除"
            title={purgeTarget.impact.canDelete ? `永久删除空${KIND_LABELS[purgeTarget.item.kind as TrashKind]}？` : "该内容受科学依赖保护"}
            description={purgeTarget.impact.canDelete ? "此操作不可撤销，且仅适用于服务器确认无任何依赖的空内容。" : "服务器检测到历史或科学依赖，因此不会提供永久删除操作。"}
            onClose={() => { setPurgeTarget(null); setConfirmText(""); }}
            footer={<>
              <button type="button" className="product-secondary-action" onClick={() => { setPurgeTarget(null); setConfirmText(""); }}>关闭</button>
              {purgeTarget.impact.canDelete ? <button type="button" className="product-primary-action" disabled={confirmText !== purgeConfirmationToken(purgeTarget.item) || busyId === itemIdentity(purgeTarget.item)} onClick={() => void purge()}>确认永久删除</button> : null}
            </>}
          >
            {purgeTarget.impact.dependencies.length ? <ul className="trash-dependency-list">{purgeTarget.impact.dependencies.map((dependency) => <li key={dependency.kind}><span>{dependency.href ? <Link href={dependency.href}>{dependency.label}</Link> : dependency.label}</span><strong>{dependency.count}</strong></li>)}</ul> : <p>服务器未发现研究、结果、Artifact、报告或科学版本依赖。</p>}
            {purgeTarget.impact.retentionPolicy ? (
              <p className="product-form-hint">
                留存策略：自动清理已禁用；受引用科学 provenance 永久保护；永久删除仅允许服务器确认零依赖的内容。
              </p>
            ) : null}
            <p className="product-form-hint">✓ 回收站恢复不受影响 · ✓ 历史 provenance 不会被级联破坏</p>
            {purgeTarget.impact.canDelete ? (
              <label className="trash-confirm-field">
                输入稳定身份 <strong>{purgeConfirmationToken(purgeTarget.item)}</strong> 以确认
                <input
                  value={confirmText}
                  onChange={(event) => setConfirmText(event.target.value)}
                  autoComplete="off"
                  aria-label={`输入 ${purgeConfirmationToken(purgeTarget.item)} 以确认永久删除`}
                  aria-describedby="trash-purge-confirmation-help"
                />
                <span id="trash-purge-confirmation-help">
                  标题可能重复；类型与 ID 用于确认当前选中的确切实体。
                </span>
              </label>
            ) : <p className="product-form-error" role="status">请使用“恢复”，或保留该记录以维护科学历史。</p>}
          </ProductModal> : null}
        </main>
      </ProductShell>
    </RequireProductAuth>
  );
}
