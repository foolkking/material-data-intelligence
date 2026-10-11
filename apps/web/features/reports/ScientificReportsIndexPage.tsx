"use client";

import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { getProjectHistory, type ProjectHistory } from "../../app/lib/planner-api";
import { researchRunSourceDatasets, researchRunTitle } from "../../app/lib/research-display";
import { SourceDatasetList } from "../../shared/ui/SourceDatasetList";
import {
  bulkUpdateScientificReportLifecycle,
  createScientificReportRevision,
  getScientificReportDependencyImpact,
  listScientificReports,

  type ScientificReportView,
  updateScientificReportLifecycle,
  updateScientificReportOrganization,
} from "../../app/lib/scientific-report-api";
import { ManagedObjectRow, ProductModal } from "../../shared/ui/ObjectManagement";
import { ProductShell, RequireProductAuth } from "../../shared/layout/ProductShell";
import { readReportContent } from "./report-read";
import { useReportOperation } from "./use-report-operation";
import { useDependencyPreview } from "../../shared/ui/DependencyPreview";

const REPORT_PAGE_SIZE = 12;

function assertSameReport(original: ScientificReportView, updated: ScientificReportView) {
  if (updated.report_id !== original.report_id || updated.project_id !== original.project_id || updated.snapshot_id !== original.snapshot_id) {
    throw new Error("Report identity mismatch");
  }
}

async function readReportImpact(reportId: string, signal?: AbortSignal) {
  const result = await getScientificReportDependencyImpact(reportId, signal);
  if (result.entity !== "scientific_report" || result.entityId !== reportId) throw new Error("Report dependency identity mismatch");
  return result;
}

export function ScientificReportsIndexPage({
  projectId,
}: {
  projectId: string;
}) {
  return <ScientificReportsIndexContent key={projectId} projectId={projectId} />;
}

function ScientificReportsIndexContent({ projectId }: { projectId: string }) {
  const [grounded, setGrounded] = useState<ScientificReportView[]>([]);
  const [history, setHistory] = useState<ProjectHistory | null>(null);
  const [readStates, setReadStates] = useState<Record<"reports" | "history", "loading" | "ready" | "error">>({ reports: "loading", history: "loading" });
  const requests = useRef(new Map<"reports" | "history", AbortController>());
  const [filter, setFilter] = useState<
    "active" | "archived" | "trashed" | "all"
  >("active");
  const [query, setQuery] = useState("");
  const [groundedLimit, setGroundedLimit] = useState(REPORT_PAGE_SIZE);
  const [legacyLimit, setLegacyLimit] = useState(REPORT_PAGE_SIZE);
  const [selectedReportIds, setSelectedReportIds] = useState<string[]>([]);
  const [selectionMode, setSelectionMode] = useState(false);
  const operation = useReportOperation();
  const { reconciled, isPending } = operation;
  const [impactReport, setImpactReport] = useState<ScientificReportView | null>(null);
  const impact = useDependencyPreview(impactReport ? [{ id: impactReport.report_id, label: impactReport.title }] : [], readReportImpact);
  const impactPreview = impactReport && impact.complete ? { report: impactReport, impact: impact.items[0] } : null;
  const [renameEditor, setRenameEditor] = useState<{
    report: ScientificReportView;
    title: string;
  } | null>(null);
  const [revisionEditor, setRevisionEditor] = useState<{
    report: ScientificReportView;
    title: string;
  } | null>(null);
  const dialogOpen = Boolean(renameEditor || revisionEditor || impactReport);
  useEffect(() => {
    if (!dialogOpen) return;
    const bodyOverflow = document.body.style.overflow;
    const rootOverflow = document.documentElement.style.overflow;
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = bodyOverflow;
      document.documentElement.style.overflow = rootOverflow;
    };
  }, [dialogOpen]);
  const loadDirectory = useCallback(async (key: "reports" | "history") => {
    if (isPending()) return;
    requests.current.get(key)?.abort();
    const controller = new AbortController();
    requests.current.set(key, controller);
    setReadStates((current) => ({ ...current, [key]: "loading" }));
    try {
      if (key === "reports") {
        const result = await readReportContent((signal) => listScientificReports(projectId, signal), controller.signal);
        if (controller.signal.aborted) return;
        if (result.items.some((item) => item.project_id !== projectId || !item.report_id) || new Set(result.items.map((item) => item.report_id)).size !== result.items.length) throw new Error("Report identity mismatch");
        setGrounded(result.items);
        reconciled();
      } else {
        const result = await readReportContent((signal) => getProjectHistory(projectId, { signal, forceRefresh: true }), controller.signal);
        if (controller.signal.aborted) return;
        if (result.project.projectId !== projectId) throw new Error("History project mismatch");
        setHistory(result);
      }
      setReadStates((current) => ({ ...current, [key]: "ready" }));
    } catch {
      if (!controller.signal.aborted) setReadStates((current) => ({ ...current, [key]: "error" }));
    } finally {
      if (requests.current.get(key) === controller) requests.current.delete(key);
    }
  }, [projectId, reconciled, isPending]);
  useEffect(() => {
    void loadDirectory("reports");
    void loadDirectory("history");
    const pending = requests.current;
    return () => {
      for (const controller of pending.values()) controller.abort();
      pending.clear();
    };
  }, [loadDirectory]);
  const normalizedQuery = query.trim().toLocaleLowerCase("zh-CN");
  const legacyReports = useMemo(
    () =>
      (history?.analyses || []).filter((item) => {
        if (
          item.visibleInReports === false ||
          !(
            item.reportCount > 0 ||
            ["completed", "succeeded", "success"].includes(
              item.status.toLowerCase(),
            )
          )
        ) {
          return false;
        }
        if (!normalizedQuery) return true;
        const sources = researchRunSourceDatasets(item, history?.datasets || []);
        return [
          researchRunTitle(item),
          item.userQuestion,
          ...sources.map((source) => source.name),
          ...(item.toolIds || []),
        ]
          .filter(Boolean)
          .join(" ")
          .toLocaleLowerCase("zh-CN")
          .includes(normalizedQuery);
      }),
    [history, normalizedQuery],
  );
  const visibleGrounded = useMemo(
    () =>
      grounded
        .filter((report) => {
          const status = String(
            report.lifecycle_status || "ACTIVE",
          ).toLowerCase();
          if (filter !== "all" && status !== filter) return false;
          if (!normalizedQuery) return true;
          return [
            report.title,
            report.source_title,
            report.scientific_context,
            report.grounding_status,
          ]
            .filter(Boolean)
            .join(" ")
            .toLocaleLowerCase("zh-CN")
            .includes(normalizedQuery);
        })
        .sort(
          (left, right) =>
            Number(Boolean(right.pinned)) -
              Number(Boolean(left.pinned)) ||
            Date.parse(right.created_at) - Date.parse(left.created_at),
        ),
    [filter, grounded, normalizedQuery],
  );
  const displayedGrounded = visibleGrounded.slice(0, groundedLimit);
  const displayedLegacy = legacyReports.slice(0, legacyLimit);
  const selectableReports = displayedGrounded.filter((report) =>
    ["active", "archived"].includes(String(report.lifecycle_status || "ACTIVE").toLowerCase()),
  );
  const selectedReports = selectableReports.filter((report) =>
    selectedReportIds.includes(report.report_id),
  );
  const selectedActiveReports = selectedReports.filter(
    (report) => String(report.lifecycle_status || "ACTIVE").toLowerCase() === "active",
  );
  const selectedArchivedReports = selectedReports.filter(
    (report) => String(report.lifecycle_status || "ACTIVE").toLowerCase() === "archived",
  );
  const allSelected =
    selectableReports.length > 0 &&
    selectableReports.every((report) => selectedReportIds.includes(report.report_id));
  const selectedVisibleCount = selectedReports.length;
  function toggleReportSelection(reportId: string) {
    setSelectedReportIds((current) =>
      current.includes(reportId)
        ? current.filter((id) => id !== reportId)
        : [...current, reportId],
    );
  }
  function toggleAllReports() {
    setSelectedReportIds(allSelected ? [] : selectableReports.map((report) => report.report_id));
  }
  const writesBlocked = operation.pending || operation.uncertain || readStates.reports !== "ready";
  async function bulkLifecycle(next: "ACTIVE" | "ARCHIVED") {
    const targets = next === "ARCHIVED" ? selectedActiveReports : selectedArchivedReports;
    if (!targets.length || writesBlocked || requests.current.has("reports")) return;
    await operation.run(next === "ARCHIVED" ? "批量归档" : "批量恢复", async (signal) => {
      for (let start = 0; start < targets.length; start += 100) {
        signal.throwIfAborted();
        const batch = targets.slice(start, start + 100);
        const ids = batch.map((report) => report.report_id);
        const result = await bulkUpdateScientificReportLifecycle(projectId, ids, next, signal);
        signal.throwIfAborted();
        if (result.lifecycle !== next || result.count !== ids.length || result.reportIds.length !== ids.length ||
          new Set(result.reportIds).size !== ids.length || result.reportIds.some((id) => !ids.includes(id)) ||
          result.items.length !== ids.length || new Set(result.items.map((item) => item.report_id)).size !== ids.length) throw new Error("Report batch mismatch");
        for (const updated of result.items) {
          const original = batch.find((item) => item.report_id === updated.report_id);
          if (!original || updated.lifecycle_status !== next) throw new Error("Report batch mismatch");
          assertSameReport(original, updated);
        }
        setGrounded((items) => items.map((item) => result.items.find((value) => value.report_id === item.report_id) || item));
        setSelectedReportIds((current) => current.filter((id) => !ids.includes(id)));
      }
    }, () => {});
  }
  async function changeLifecycle(report: ScientificReportView, next: "ACTIVE" | "ARCHIVED" | "TRASHED", confirmed = false) {
    if (writesBlocked || requests.current.has("reports") || operation.locked()) return;
    if (next === "TRASHED" && !confirmed) { setImpactReport(report); return; }
    if (next === "TRASHED" && impactPreview?.report.report_id !== report.report_id) return;
    await operation.run(next === "TRASHED" ? "移入回收站" : next === "ARCHIVED" ? "归档报告" : "恢复报告",
      (signal) => updateScientificReportLifecycle(report.report_id, next, signal), (updated) => {
        assertSameReport(report, updated);
        if (updated.lifecycle_status !== next) throw new Error("Report status mismatch");
        setGrounded((items) => items.map((item) => item.report_id === updated.report_id ? updated : item));
        setImpactReport(null);
      });
  }
  async function changeOrganization(report: ScientificReportView, changes: { title?: string | null; pinned?: boolean }) {
    if (writesBlocked || requests.current.has("reports")) return;
    const editor = renameEditor;
    await operation.run(changes.title !== undefined ? "保存名称" : changes.pinned ? "置顶报告" : "取消置顶",
      (signal) => updateScientificReportOrganization(report.report_id, changes, signal), (updated) => {
        assertSameReport(report, updated);
        if ((changes.title !== undefined && updated.title !== changes.title) ||
          (changes.pinned !== undefined && updated.pinned !== changes.pinned)) throw new Error("Report organization mismatch");
        setGrounded((items) => items.map((item) => item.report_id === updated.report_id ? updated : item));
        setRenameEditor((current) => current === editor ? null : current);
      });
  }
  async function createRevision() {
    if (!revisionEditor || !revisionEditor.title.trim() || writesBlocked || requests.current.has("reports")) return;
    const editor = revisionEditor, original = editor.report;
    await operation.run("创建修订", (signal) => createScientificReportRevision(original.report_id, {
      reason: "USER_REVISION", title: editor.title.trim(),
    }, signal), (created) => {
      if (!created.report_id || created.report_id === original.report_id || created.project_id !== projectId ||
        created.parent_report_id !== original.report_id || created.parent_snapshot_id !== original.snapshot_id ||
        created.revision_group_id !== (original.revision_group_id || original.report_id) ||
        created.scientific_result_snapshot_id !== original.scientific_result_snapshot_id ||
        created.research_turn_id !== original.research_turn_id) throw new Error("Report revision mismatch");
      setGrounded((items) => [created, ...items.filter((item) => item.report_id !== created.report_id)]);
      setRevisionEditor((current) => current === editor ? null : current);
    });
  }
  const feedback = <>
    {operation.pending ? <p role="status">正在保存，请稍候…</p> : null}
    {operation.error ? <div className="product-form-error" role="alert"><p>{operation.error}</p>
      {operation.uncertain ? <button type="button" className="product-secondary-action" disabled={readStates.reports === "loading"} onClick={() => void loadDirectory("reports")}>{readStates.reports === "loading" ? "正在重新读取…" : "重新读取报告"}</button> : null}
    </div> : null}
    {operation.notice ? <p role="status">{operation.notice}</p> : null}
  </>;
  return (
    <RequireProductAuth>
      <ProductShell projectId={projectId}>
        <section className="document-page scientific-report-index" aria-labelledby="scientific-reports-page-title">
          <header className="product-page-heading report-directory-header">
            <div><h1 id="scientific-reports-page-title">报告</h1><p>阅读研究结论、图表与分析结果。</p></div>
            <button type="button" className="product-secondary-action" disabled={operation.pending || readStates.reports === "loading" || readStates.history === "loading"} onClick={() => { void loadDirectory("reports"); void loadDirectory("history"); }}>刷新列表</button>
          </header>
          {(["reports", "history"] as const).map((key) => readStates[key] === "loading" ? <p key={key} className="report-directory-read-state" role="status">{key === "reports" ? "正在读取研究报告…" : "正在读取分析记录…"}</p> : readStates[key] === "error" ? <div key={key} className="report-directory-read-state" role="alert"><strong>{key === "reports" ? "研究报告暂时无法读取" : "分析记录暂时无法读取"}</strong><p>保留已读取的内容，请重试以确认完整列表。</p><button type="button" className="product-secondary-action" onClick={() => void loadDirectory(key)}>{key === "reports" ? "重新加载报告" : "重新加载分析记录"}</button></div> : null)}
          {!renameEditor && !revisionEditor && !impactReport ? feedback : null}
          {renameEditor ? (
            <ProductModal
              eyebrow=""
              title="重命名报告"
              description="修改列表中显示的名称，报告正文与来源记录会保留。"
              onClose={() => setRenameEditor(null)}
              footer={
                <>
                  <button
                    type="button"
                    className="product-secondary-action"
                    onClick={() => setRenameEditor(null)}
                  >
                    取消
                  </button>
                  <button
                    type="button"
                    className="product-primary-action"
                    disabled={!renameEditor.title.trim() || writesBlocked}
                    onClick={() => void changeOrganization(renameEditor.report, { title: renameEditor.title.trim() })}
                  >
                    保存名称
                  </button>
                </>
              }
            >
              <label htmlFor="scientific-report-title-override">报告显示名称</label>
              <input
                id="scientific-report-title-override"
                value={renameEditor.title}
                disabled={operation.pending}
                maxLength={256}
                onChange={(event) =>
                  setRenameEditor((current) => current ? { ...current, title: event.target.value } : current)
                }
              />
              {feedback}
            </ProductModal>
          ) : null}
          {revisionEditor ? (
            <ProductModal
              eyebrow=""
              title="创建新修订"
              description="使用已有结果创建一个新版本，旧版仍可阅读。这不会重新执行分析。"
              onClose={() => setRevisionEditor(null)}
              footer={
                <>
                  <button
                    type="button"
                    className="product-secondary-action"
                    onClick={() => setRevisionEditor(null)}
                  >
                    取消
                  </button>
                  <button
                    type="button"
                    className="product-primary-action"
                    disabled={
                      !revisionEditor.title.trim() ||
                      writesBlocked
                    }
                    onClick={() => void createRevision()}
                  >
                    创建修订
                  </button>
                </>
              }
            >
              <label htmlFor="scientific-report-revision-title">
                新修订名称
              </label>
              <input
                id="scientific-report-revision-title"
                value={revisionEditor.title}
                disabled={operation.pending}
                maxLength={256}
                onChange={(event) =>
                  setRevisionEditor((current) =>
                    current
                      ? { ...current, title: event.target.value }
                      : current,
                  )
                }
              />
              {feedback}
            </ProductModal>
          ) : null}
          {impactReport ? (
            <ProductModal
              eyebrow=""
              title="移入回收站前确认"
              description={`“${impactReport.title}”将移入回收站，之后可以恢复。`}
              onClose={() => setImpactReport(null)}
              footer={
                <>
                  <button
                    type="button"
                    className="product-secondary-action"
                    onClick={() => setImpactReport(null)}
                  >
                    取消
                  </button>
                  <button
                    type="button"
                    className="product-primary-action"
                    disabled={!impactPreview || writesBlocked}
                    onClick={() => void changeLifecycle(impactReport, "TRASHED", true)}
                  >
                    确认移入回收站
                  </button>
                </>
              }
            >
              {impact.pendingCount ? <p role="status">正在检查关联内容…</p> : null}
              {impact.entries.some((entry) => entry.error) ? <div role="alert" className="product-form-error"><p>暂时无法检查关联内容，请重试后再确认。</p><button type="button" className="product-secondary-action" onClick={impact.retry}>重新检查</button></div> : null}
              {impactPreview ? <p>已有研究和来源数据会保留。</p> : null}
              {impactPreview?.impact.dependencies.length ? (
                <details><summary>查看 {impactPreview.impact.dependencyCount} 项关联内容</summary><ul>
                  {impactPreview.impact.dependencies.map((item) => (
                    <li key={`${item.kind}:${item.id}`}>
                      <strong>
                        {item.href ? <Link href={item.href}>{item.kind === "SCIENTIFIC_RESULT" ? "分析结果" : item.label}</Link> : item.kind === "SCIENTIFIC_RESULT" ? "分析结果" : item.label}
                      </strong>
                    </li>
                  ))}
                </ul></details>
              ) : null}
              {feedback}
            </ProductModal>
          ) : null}
          {(
            <>
              <div className="scientific-report-discovery">
                <label htmlFor="scientific-report-search">
                  搜索报告
                  <input
                    id="scientific-report-search"
                    type="search"
                    value={query}
                    placeholder="搜索标题、数据或分析方法"
                    onChange={(event) => {
                      setQuery(event.target.value);
                      setGroundedLimit(REPORT_PAGE_SIZE);
                      setLegacyLimit(REPORT_PAGE_SIZE);
                      setSelectedReportIds([]);
                      setSelectionMode(false);
                    }}
                  />
                </label>
                <p aria-live="polite">
                  {readStates.reports !== "ready" ? "报告数量待确认" : `${visibleGrounded.length} 份研究报告`}
                  {readStates.history !== "ready" ? " · 分析记录数量待确认" : ` · ${legacyReports.length} 条分析记录`}
                </p>
              </div>
              {grounded.length > 0 ? <section
                className="scientific-report-index-section"
                aria-labelledby="grounded-reports"
              >
                <div className="scientific-report-index-heading">
                  <div>
                    <h2 id="grounded-reports">研究报告</h2>
                  </div>

                </div>
                <div className="report-directory-tools"><div
                  className="product-filter-row"
                  role="group"
                  aria-label="报告状态筛选"
                >
                  {(["active", "archived", "trashed", "all"] as const).map(
                    (value) => (
                      <button
                        key={value}
                        type="button"
                        className="product-filter-button"
                        aria-pressed={filter === value}
                        onClick={() => {
                          setFilter(value);
                          setGroundedLimit(REPORT_PAGE_SIZE);
                          setSelectedReportIds([]);
                          setSelectionMode(false);

                        }}
                      >
                        {value === "active"
                          ? "当前"
                          : value === "archived"
                            ? "已归档"
                            : value === "trashed"
                              ? "回收站"
                              : "全部"}
                      </button>
                    ),
                  )}
                </div>
                {selectableReports.length ? (
                  <div
                    className="product-row-actions scientific-report-bulk-actions"
                    data-selection-mode={selectionMode}
                  >
                    {!selectionMode ? (
                      <button
                        type="button"
                        className="product-secondary-action"
                        onClick={() => setSelectionMode(true)}
                      >
                        批量管理
                      </button>
                    ) : (
                      <>
                        <div className="scientific-report-bulk-selection">
                          <label className="scientific-report-bulk-checkbox">
                            <input
                              type="checkbox"
                              checked={allSelected}
                              onChange={toggleAllReports}
                              aria-label="全选可批量操作报告"
                            />
                            全选
                          </label>
                          <span>{selectedVisibleCount} 份已选择</span>

                        </div>
                        {selectedActiveReports.length ? (
                          <button
                            type="button"
                            className="product-secondary-action"
                            onClick={() => void bulkLifecycle("ARCHIVED")}
                            disabled={writesBlocked}
                          >
                            {operation.pending ? "批量处理中…" : `归档 ${selectedActiveReports.length} 份`}
                          </button>
                        ) : null}
                        {selectedArchivedReports.length ? (
                          <button
                            type="button"
                            className="product-secondary-action"
                            onClick={() => void bulkLifecycle("ACTIVE")}
                            disabled={writesBlocked}
                          >
                            {operation.pending ? "批量处理中…" : `恢复 ${selectedArchivedReports.length} 份`}
                          </button>
                        ) : null}
                        <button
                          type="button"
                          className="product-link-button"
                          onClick={() => {
                            setSelectionMode(false);
                            setSelectedReportIds([]);
                          }}
                        >
                          退出批量
                        </button>
                      </>
                    )}
                  </div>
                ) : null}
                </div><div className="report-list report-managed-list">
                  {displayedGrounded.map((report) => {
                    const status = String(
                      report.lifecycle_status || "ACTIVE",
                    ).toLowerCase();
                    const statusLabel =
                      status === "active"
                        ? report.current_effective_relevance === "CURRENT"
                          ? "当前结果"
                          : "历史结果"
                        : status === "archived"
                          ? "已归档"
                          : "回收站";
                    const revisionLabel = `第 ${report.revision_number || 1} 版`;
                    const trailing = report.pinned
                      ? `列表置顶 · ${revisionLabel} · ${statusLabel}`
                      : `${revisionLabel} · ${statusLabel}`;
                    const description = [
                      report.scientific_context,
                      new Date(report.created_at).toLocaleString("zh-CN"),
                      `${report.finding_count} 项主要发现`,
                      report.figure_count ? `${report.figure_count} 幅图` : null,
                    ]
                      .filter(Boolean)
                      .join(" · ");
                    return (
                      <ManagedObjectRow
                        key={report.report_id}
                        href={`/projects/${projectId}/reports/${report.report_id}`}
                        title={report.title}
                        description={description}
                        trailing={trailing}
                        selectionMode={selectionMode}
                        selectable={["active", "archived"].includes(status)}
                        selected={selectedReportIds.includes(report.report_id)}
                        onSelectedChange={() =>
                          toggleReportSelection(report.report_id)
                        }
                        actions={
                          writesBlocked
                            ? [
                                {
                                  label: operation.uncertain ? "请先重新读取报告" : operation.pending ? "处理中…" : "正在读取报告…",
                                  disabled: true,
                                },
                              ]
                            : status === "active"
                              ? [
                                  {
                                    label: "重命名",
                                    onSelect: () =>
                                      setRenameEditor({ report, title: report.title }),
                                  },
                                  {
                                    label: report.pinned ? "取消列表置顶" : "列表置顶",
                                    onSelect: () =>
                                      void changeOrganization(report, { pinned: !report.pinned }),
                                  },
                                  {
                                    label: "创建修订",
                                    onSelect: () =>
                                      setRevisionEditor({
                                        report,
                                        title: `${report.title}（修订 ${(report.revision_number || 1) + 1}）`,
                                      }),
                                  },
                                  {
                                    label: "归档",
                                    onSelect: () =>
                                      void changeLifecycle(report, "ARCHIVED"),
                                  },
                                  {
                                    label: "移入回收站",
                                    destructive: true,
                                    onSelect: () =>
                                      void changeLifecycle(report, "TRASHED"),
                                  },
                                ]
                              : status === "archived"
                                ? [
                                    {
                                      label: "重命名",
                                      onSelect: () =>
                                        setRenameEditor({ report, title: report.title }),
                                    },
                                    {
                                      label: report.pinned ? "取消列表置顶" : "列表置顶",
                                      onSelect: () =>
                                        void changeOrganization(report, { pinned: !report.pinned }),
                                    },
                                    {
                                      label: "创建修订",
                                      onSelect: () =>
                                        setRevisionEditor({
                                          report,
                                          title: `${report.title}（修订 ${(report.revision_number || 1) + 1}）`,
                                        }),
                                    },
                                    {
                                      label: "恢复到当前报告",
                                      onSelect: () =>
                                        void changeLifecycle(report, "ACTIVE"),
                                    },
                                    {
                                      label: "移入回收站",
                                      destructive: true,
                                      onSelect: () =>
                                        void changeLifecycle(report, "TRASHED"),
                                    },
                                  ]
                                : [
                                    {
                                      label: "恢复报告",
                                      onSelect: () =>
                                        void changeLifecycle(report, "ACTIVE"),
                                    },
                                  ]
                        }
                      />
                    );
                  })}
                  {visibleGrounded.length === 0 && readStates.reports === "ready" ? (
                    <div className="report-directory-empty">
                      <h3>{normalizedQuery ? "没有匹配的研究报告" : "当前筛选下没有报告"}</h3>
                      <p>
                        {normalizedQuery
                          ? "尝试缩短关键词，或切换报告状态。"
                          : grounded.length ? "切换报告状态查看其他已生成报告。" : "完成研究分析后，可将结果整理为科学报告。"}
                      </p>
                      <button className="product-secondary-action" type="button" onClick={() => { setQuery(""); setFilter("all"); }}>显示全部报告</button>
                    </div>
                  ) : null}
                </div>
                {displayedGrounded.length < visibleGrounded.length ? (
                  <button
                    type="button"
                    className="product-secondary-action scientific-report-load-more"
                    onClick={() =>
                      setGroundedLimit((value) => value + REPORT_PAGE_SIZE)
                    }
                  >
                    加载更多研究报告（还剩{" "}
                    {visibleGrounded.length - displayedGrounded.length} 份）
                  </button>
                ) : null}
              </section> : null}
              {legacyReports.length ? (
                <section
                  className="scientific-report-index-section"
                  aria-labelledby="legacy-reports"
                >
                  <div className="scientific-report-index-heading">
                    <div>
                      <h2 id="legacy-reports">分析记录</h2>
                    </div>
                    <span>查看已完成分析的结果</span>
                  </div>
                  <div className="report-list">
                    {displayedLegacy.map((run) => {
                      const sources = researchRunSourceDatasets(run, history?.datasets || []);
                      return (
                        <Link
                          className="report-list-row"
                          key={run.jobId}
                          href={`/projects/${projectId}/reports/${run.jobId}`}
                        >
                          <div>
                            <h3>{researchRunTitle(run)}</h3>
                            <SourceDatasetList sources={sources} />
                            <p>
                              {!sources.length ? `${run.sourceDatasetIds === undefined ? "项目数据" : "来源待核实"} · ` : null}
                              {run.artifactCount} 项结果
                            </p>
                          </div>
                          <span>查看结果 →</span>
                        </Link>
                      );
                    })}
                  </div>
                  {displayedLegacy.length < legacyReports.length ? (
                    <button
                      type="button"
                      className="product-secondary-action scientific-report-load-more"
                      onClick={() =>
                        setLegacyLimit((value) => value + REPORT_PAGE_SIZE)
                      }
                    >
                      加载更多分析记录（还剩{" "}
                      {legacyReports.length - displayedLegacy.length} 份）
                    </button>
                  ) : null}
                </section>
              ) : null}
              {readStates.reports === "ready" && readStates.history === "ready" && !grounded.length && !legacyReports.length ? <div className="report-directory-empty"><h2>{normalizedQuery ? "没有匹配的报告或分析记录" : "还没有报告"}</h2><p>{normalizedQuery ? "试试其他关键词，或清除搜索查看全部内容。" : "完成一次研究后，可在这里查看分析结果与生成的报告。"}</p>{normalizedQuery ? <button className="product-secondary-action" type="button" onClick={() => setQuery("")}>清除搜索</button> : <Link className="product-secondary-action" href={`/projects/${projectId}/research`}>前往研究</Link>}</div> : null}
            </>
          )}
        </section>
      </ProductShell>
    </RequireProductAuth>
  );
}
