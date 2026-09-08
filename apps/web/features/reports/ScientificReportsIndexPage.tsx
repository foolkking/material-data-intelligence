"use client";

import { ProductLink as Link } from "../../app/components/ProductNavigation";
import { useEffect, useMemo, useState } from "react";
import { getProjectHistory, type ProjectHistory } from "../../app/lib/planner-api";
import { researchRunTitle } from "../../app/lib/research-display";
import {
  bulkUpdateScientificReportLifecycle,
  createScientificReportRevision,
  getScientificReportDependencyImpact,
  listScientificReports,
  type ScientificReportDependencyImpact,
  type ScientificReportView,
  updateScientificReportLifecycle,
  updateScientificReportOrganization,
} from "../../app/lib/scientific-report-api";
import { ManagedObjectRow, ProductModal } from "../../app/components/ObjectManagement";
import { ProductShell, RequireProductAuth } from "../../app/components/ProductShell";

const REPORT_PAGE_SIZE = 12;

export function ScientificReportsIndexPage({
  projectId,
}: {
  projectId: string;
}) {
  const [grounded, setGrounded] = useState<ScientificReportView[]>([]);
  const [history, setHistory] = useState<ProjectHistory | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [filter, setFilter] = useState<
    "active" | "archived" | "trashed" | "all"
  >("active");
  const [query, setQuery] = useState("");
  const [groundedLimit, setGroundedLimit] = useState(REPORT_PAGE_SIZE);
  const [legacyLimit, setLegacyLimit] = useState(REPORT_PAGE_SIZE);
  const [busyReportId, setBusyReportId] = useState<string | null>(null);
  const [selectedReportIds, setSelectedReportIds] = useState<string[]>([]);
  const [selectionMode, setSelectionMode] = useState(false);
  const [bulkBusy, setBulkBusy] = useState(false);
  const [lifecycleError, setLifecycleError] = useState<string | null>(null);
  const [impactPreview, setImpactPreview] = useState<{
    report: ScientificReportView;
    impact: ScientificReportDependencyImpact;
  } | null>(null);
  const [renameEditor, setRenameEditor] = useState<{
    report: ScientificReportView;
    title: string;
  } | null>(null);
  const [revisionEditor, setRevisionEditor] = useState<{
    report: ScientificReportView;
    title: string;
  } | null>(null);
  useEffect(() => {
    let active = true;
    void Promise.allSettled([
      listScientificReports(projectId),
      getProjectHistory(projectId),
    ]).then(([reports, legacy]) => {
      if (!active) return;
      if (reports.status === "fulfilled") setGrounded(reports.value.items);
      if (legacy.status === "fulfilled") setHistory(legacy.value);
      setState(
        reports.status === "fulfilled" || legacy.status === "fulfilled"
          ? "ready"
          : "error",
      );
    });
    return () => {
      active = false;
    };
  }, [projectId]);
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
        const dataset = history?.datasets.find(
          (candidate) => candidate.datasetId === item.datasetId,
        );
        return [
          researchRunTitle(item),
          item.userQuestion,
          dataset?.name,
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
  async function bulkLifecycle(next: "ACTIVE" | "ARCHIVED") {
    const targets = next === "ARCHIVED" ? selectedActiveReports : selectedArchivedReports;
    if (!targets.length || bulkBusy) return;
    setBulkBusy(true);
    setLifecycleError(null);
    try {
      const result = await bulkUpdateScientificReportLifecycle(
        projectId,
        targets.map((report) => report.report_id),
        next,
      );
      setGrounded((items) =>
        items.map((item) =>
          result.items.find((value) => value.report_id === item.report_id) || item
        ),
      );
      setSelectedReportIds([]);
    } catch {
      setLifecycleError(
        "批量报告状态未更新；所选报告保持原状态，可检查权限或服务后重试。",
      );
    } finally {
      setBulkBusy(false);
    }
  }
  async function changeLifecycle(
    report: ScientificReportView,
    next: "ACTIVE" | "ARCHIVED" | "TRASHED",
    confirmed = false,
  ) {
    if (next === "TRASHED" && !confirmed) {
      setBusyReportId(report.report_id);
      setLifecycleError(null);
      try {
        const impact = await getScientificReportDependencyImpact(report.report_id);
        setImpactPreview({ report, impact });
      } catch {
        setLifecycleError("报告依赖影响暂时无法读取，未执行回收站操作。");
      } finally {
        setBusyReportId(null);
      }
      return;
    }
    setBusyReportId(report.report_id);
    setLifecycleError(null);
    try {
      const updated = await updateScientificReportLifecycle(
        report.report_id,
        next,
      );
      setGrounded((items) =>
        items.map((item) =>
          item.report_id === updated.report_id ? updated : item,
        ),
      );
    } catch {
      setLifecycleError("报告状态更新失败，请检查服务连接后重试。");
    } finally {
      setBusyReportId(null);
    }
  }
  async function changeOrganization(
    report: ScientificReportView,
    changes: { title?: string | null; pinned?: boolean },
  ) {
    setBusyReportId(report.report_id);
    setLifecycleError(null);
    try {
      const updated = await updateScientificReportOrganization(report.report_id, changes);
      setGrounded((items) =>
        items.map((item) => item.report_id === updated.report_id ? updated : item),
      );
      setRenameEditor(null);
    } catch {
      setLifecycleError("报告组织信息更新失败；科学报告快照未发生变化。");
    } finally {
      setBusyReportId(null);
    }
  }
  async function createRevision() {
    if (!revisionEditor || !revisionEditor.title.trim()) return;
    setBusyReportId(revisionEditor.report.report_id);
    setLifecycleError(null);
    try {
      const created = await createScientificReportRevision(
        revisionEditor.report.report_id,
        {
          reason: "USER_REVISION",
          title: revisionEditor.title.trim(),
        },
      );
      setGrounded((items) => [created, ...items]);
      setRevisionEditor(null);
    } catch {
      setLifecycleError(
        "报告修订创建失败；原报告、ScientificResult 与精确来源均未改变。",
      );
    } finally {
      setBusyReportId(null);
    }
  }
  return (
    <RequireProductAuth>
      <ProductShell projectId={projectId}>
        <section className="document-page scientific-report-index" aria-labelledby="scientific-reports-page-title">
          <header className="product-page-heading">
            <p className="product-kicker">项目报告</p>
            <h1 id="scientific-reports-page-title">科学报告</h1>
            <p>
              将已验证的研究结果整理为可阅读、可引用、可复现的持久科学记录。
            </p>
          </header>
          {state === "loading" ? (
            <div className="product-loading" role="status" aria-live="polite">
              正在加载项目报告…
            </div>
          ) : null}
          {state === "error" ? (
            <div className="product-state" role="alert">
              <h2>报告列表暂时无法加载</h2>
              <p>已生成的报告仍保存在项目中，请检查服务连接后重试。</p>
            </div>
          ) : null}
          {lifecycleError ? (
            <div className="product-state" role="alert">
              {lifecycleError}
            </div>
          ) : null}
          {renameEditor ? (
            <ProductModal
              eyebrow="报告组织"
              title="重命名报告"
              description="仅修改项目中的显示名称；不可变报告快照、ScientificResult、证据与精确来源保持不变。"
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
                    disabled={!renameEditor.title.trim() || busyReportId === renameEditor.report.report_id}
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
                maxLength={256}
                autoFocus
                onChange={(event) =>
                  setRenameEditor((current) => current ? { ...current, title: event.target.value } : current)
                }
              />
              <p className="product-form-hint">
                原始快照标题仍保留在审计和复现数据中。
              </p>
            </ProductModal>
          ) : null}
          {revisionEditor ? (
            <ProductModal
              eyebrow="不可变报告修订"
              title="创建新修订"
              description="新修订沿用同一 ScientificResult、解释与精确源版本；不会重新运行科学计算，也不会修改旧报告。"
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
                      busyReportId === revisionEditor.report.report_id
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
                maxLength={256}
                autoFocus
                onChange={(event) =>
                  setRevisionEditor((current) =>
                    current
                      ? { ...current, title: event.target.value }
                      : current,
                  )
                }
              />
              <p className="product-form-hint">
                旧版保持可读；新修订只改变报告沟通层，不改变科学事实。
              </p>
            </ProductModal>
          ) : null}
          {impactPreview ? (
            <ProductModal
              eyebrow="报告管理"
              title="移入回收站前确认"
              description="报告将离开当前工作列表；受保护的科学记录与精确来源不会被删除。"
              onClose={() => setImpactPreview(null)}
              footer={
                <>
                  <button
                    type="button"
                    className="product-secondary-action"
                    onClick={() => setImpactPreview(null)}
                  >
                    取消
                  </button>
                  <button
                    type="button"
                    className="product-primary-action"
                    onClick={() => {
                      const pending = impactPreview;
                      setImpactPreview(null);
                      void changeLifecycle(pending.report, "TRASHED", true);
                    }}
                  >
                    确认移入回收站
                  </button>
                </>
              }
            >
              <p>
                “{impactPreview.report.title}”仍被 {impactPreview.impact.dependencyCount} 项科学记录引用。
                回收站操作不会删除或改写这些记录。
              </p>
              {impactPreview.impact.dependencies.length ? (
                <ul>
                  {impactPreview.impact.dependencies.slice(0, 8).map((item) => (
                    <li key={`${item.kind}:${item.id}`}>
                      <strong>
                        {item.href ? <Link href={item.href}>{item.label}</Link> : item.label}
                      </strong>{" "}
                      <code>{item.id}</code>
                    </li>
                  ))}
                </ul>
              ) : null}
              <p>
                ✓ 从当前报告发现中移除 · ✓ 保留历史研究与 exact source provenance
              </p>
            </ProductModal>
          ) : null}
          {state === "ready" ? (
            <>
              <div className="scientific-report-discovery">
                <label htmlFor="scientific-report-search">
                  搜索报告
                  <input
                    id="scientific-report-search"
                    type="search"
                    value={query}
                    placeholder="按标题、科学内容、数据或方法搜索"
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
                  找到 {visibleGrounded.length} 份已验证报告
                  {legacyReports.length ? `和 ${legacyReports.length} 份历史运行报告` : ""}
                </p>
              </div>
              <section
                className="scientific-report-index-section"
                aria-labelledby="grounded-reports"
              >
                <div className="scientific-report-index-heading">
                  <div>
                    <p className="product-kicker">已验证结果</p>
                    <h2 id="grounded-reports">已验证科学报告</h2>
                  </div>
                  <span>{visibleGrounded.length} 份</span>
                </div>
                <div
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
                          setLifecycleError(null);
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
                          <span className="scientific-report-bulk-filter">当前筛选</span>
                        </div>
                        <div className="scientific-report-bulk-selection-tools" role="group" aria-label="报告选择">
                          <button
                            type="button"
                            className="product-link-button"
                            onClick={toggleAllReports}
                            aria-pressed={allSelected}
                          >
                            {allSelected ? "清空报告" : "全选报告"}
                          </button>
                          {selectedVisibleCount ? (
                            <button
                              type="button"
                              className="product-link-button"
                              onClick={() => setSelectedReportIds([])}
                            >
                              清除选择
                            </button>
                          ) : null}
                        </div>
                        {selectedActiveReports.length ? (
                          <button
                            type="button"
                            className="product-secondary-action"
                            onClick={() => void bulkLifecycle("ARCHIVED")}
                            disabled={bulkBusy}
                          >
                            {bulkBusy ? "批量处理中…" : `归档 ${selectedActiveReports.length} 份`}
                          </button>
                        ) : null}
                        {selectedArchivedReports.length ? (
                          <button
                            type="button"
                            className="product-secondary-action"
                            onClick={() => void bulkLifecycle("ACTIVE")}
                            disabled={bulkBusy}
                          >
                            {bulkBusy ? "批量处理中…" : `恢复 ${selectedArchivedReports.length} 份`}
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
                <div className="report-list report-managed-list">
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
                          busyReportId === report.report_id
                            ? [
                                {
                                  label: "处理中…",
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
                  {visibleGrounded.length === 0 ? (
                    <div className="product-state">
                      <h3>{normalizedQuery ? "没有匹配的已验证报告" : "当前筛选下没有报告"}</h3>
                      <p>
                        {normalizedQuery
                          ? "尝试缩短关键词，或切换报告状态。"
                          : "已生成的报告仍保留在其他状态筛选中。"}
                      </p>
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
                    加载更多已验证报告（还剩{" "}
                    {visibleGrounded.length - displayedGrounded.length} 份）
                  </button>
                ) : null}
              </section>
              {legacyReports.length ? (
                <section
                  className="scientific-report-index-section"
                  aria-labelledby="legacy-reports"
                >
                  <div className="scientific-report-index-heading">
                    <div>
                      <p className="product-kicker">历史运行</p>
                      <h2 id="legacy-reports">历史运行报告</h2>
                    </div>
                    <span>{legacyReports.length} 份</span>
                  </div>
                  <div className="report-list">
                    {displayedLegacy.map((run) => {
                      const dataset = history?.datasets.find(
                        (item) => item.datasetId === run.datasetId,
                      );
                      const contextLabel =
                        run.researchContextKind === "RESEARCH_TURN"
                          ? "可恢复研究会话"
                          : run.researchContextKind === "LEGACY_SESSION_RUN"
                            ? "兼容历史运行"
                            : "历史运行";
                      return (
                        <Link
                          className="report-list-row"
                          key={run.jobId}
                          href={`/projects/${projectId}/reports/${run.jobId}`}
                        >
                          <div>
                            <span className="product-kicker">
                              {contextLabel}
                            </span>
                            <h3>{researchRunTitle(run)}</h3>
                            <p>
                              {dataset?.name || "项目数据"} ·{" "}
                              {run.artifactCount} 个结果 · {run.stepCount}{" "}
                              个步骤
                            </p>
                          </div>
                          <span>阅读旧版</span>
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
                      加载更多历史运行（还剩{" "}
                      {legacyReports.length - displayedLegacy.length} 份）
                    </button>
                  ) : null}
                </section>
              ) : null}
            </>
          ) : null}
        </section>
      </ProductShell>
    </RequireProductAuth>
  );
}
