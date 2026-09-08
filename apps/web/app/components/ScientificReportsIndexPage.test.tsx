import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  bulkUpdateScientificReportLifecycle: vi.fn(),
  createScientificReportRevision: vi.fn(),
  getProjectHistory: vi.fn(),
  getScientificReportDependencyImpact: vi.fn(),
  listScientificReports: vi.fn(),
  updateScientificReportLifecycle: vi.fn(),
  updateScientificReportOrganization: vi.fn(),
}));

vi.mock("next/link", () => ({
  default: ({ children, href, prefetch: _prefetch, ...props }: { children: React.ReactNode; href: string; prefetch?: boolean | null }) => <a href={href} {...props}>{children}</a>,
}));
vi.mock("../lib/planner-api", () => ({ getProjectHistory: mocks.getProjectHistory }));
vi.mock("../lib/scientific-report-api", () => ({
  bulkUpdateScientificReportLifecycle: mocks.bulkUpdateScientificReportLifecycle,
  createScientificReportRevision: mocks.createScientificReportRevision,
  getScientificReportDependencyImpact: mocks.getScientificReportDependencyImpact,
  listScientificReports: mocks.listScientificReports,
  updateScientificReportLifecycle: mocks.updateScientificReportLifecycle,
  updateScientificReportOrganization: mocks.updateScientificReportOrganization,
}));
vi.mock("../../shared/layout/ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

import { ScientificReportsIndexPage } from "./ScientificReportsIndexPage";

async function openReportMenu(title: string) {
  const user = userEvent.setup();
  await user.click(await screen.findByRole("button", { name: `管理 ${title}` }));
  return user;
}

beforeEach(() => {
  vi.clearAllMocks();
  mocks.getScientificReportDependencyImpact.mockResolvedValue({
    entity: "scientific_report",
    entityId: "report-1",
    displayName: "结构分析报告",
    lifecycleStatus: "ACTIVE",
    dependencyCount: 3,
    dependencies: [
      {
        kind: "RESEARCH_TURN",
        id: "turn-1",
        label: "研究回合",
        href: "/projects/project-1/research/session-1?turn=turn-1",
      },
      {
        kind: "SCIENTIFIC_RESULT",
        id: "result-1",
        label: "ScientificResult",
        href: "/projects/project-1/research/session-1?turn=turn-1",
      },
      {
        kind: "SCIENTIFIC_OBJECT_VERSION",
        id: "version-1",
        label: "来源版本 · 结构",
        href: "/projects/project-1/data?object=object-1&version=version-1",
      },
    ],
    canDelete: false,
    impact: {
      removedFromActiveDiscovery: true,
      historicalProvenanceProtected: true,
      historicalResearchRemainsAccessible: true,
      scientificSnapshotMutated: false,
    },
  });
  mocks.listScientificReports.mockResolvedValue({ items: [] });
  mocks.bulkUpdateScientificReportLifecycle.mockResolvedValue({
    lifecycle: "ARCHIVED",
    reportIds: [],
    count: 0,
    items: [],
  });
  mocks.getProjectHistory.mockResolvedValue({ project: { projectId: "project-1", name: "研究项目" }, datasets: [], analyses: [] });
});

it("labels modern and legacy history bindings without changing report routes", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { projectId: "project-1", name: "研究项目" },
    datasets: [],
    analyses: [
      {
        jobId: "job-modern",
        status: "completed",
        userQuestion: "现代研究",
        toolIds: ["structure.rdf"],
        artifactTypes: [],
        stepCount: 1,
        artifactCount: 1,
        reportCount: 1,
        researchContextKind: "RESEARCH_TURN",
      },
      {
        jobId: "job-legacy",
        status: "completed",
        userQuestion: "兼容运行",
        toolIds: ["structure.rdf"],
        artifactTypes: [],
        stepCount: 1,
        artifactCount: 1,
        reportCount: 1,
        researchContextKind: "LEGACY_SESSION_RUN",
      },
    ],
  });

  render(<ScientificReportsIndexPage projectId="project-1" />);

  expect(screen.getByText("项目报告")).toBeInTheDocument();
  expect(await screen.findByText("已验证结果")).toBeInTheDocument();
  expect(await screen.findByText("可恢复研究会话")).toBeInTheDocument();
  expect(screen.getByText("历史运行")).toBeInTheDocument();
  expect(screen.getByText("兼容历史运行")).toBeInTheDocument();
  expect(screen.getAllByRole("link", { name: /静态结构径向分布函数.*阅读旧版/ }).find(
    (link) => link.getAttribute("href")?.endsWith("job-legacy"),
  )).toHaveAttribute("href", "/projects/project-1/reports/job-legacy");
});

it("moves an active report to the recycle bin and restores it", async () => {
  mocks.listScientificReports.mockResolvedValue({
    items: [{
      report_id: "report-1",
      snapshot_id: "snapshot-1",
      project_id: "project-1",
      research_turn_id: "turn-1",
      scientific_result_snapshot_id: "result-1",
      scientific_interpretation_id: "interpretation-1",
      title: "结构分析报告",
      relevance_at_generation: "CURRENT",
      current_effective_relevance: "CURRENT",
      grounding_status: "VALID",
      lifecycle_status: "ACTIVE",
      scientific_context: "CrystalNN",
      finding_count: 1,
      figure_count: 0,
      source_fingerprint: "fingerprint",
      created_at: "2026-08-29T00:00:00Z",
    }],
  });
  mocks.updateScientificReportLifecycle
    .mockResolvedValueOnce({
      report_id: "report-1",
      snapshot_id: "snapshot-1",
      project_id: "project-1",
      research_turn_id: "turn-1",
      scientific_result_snapshot_id: "result-1",
      scientific_interpretation_id: "interpretation-1",
      title: "结构分析报告",
      relevance_at_generation: "CURRENT",
      current_effective_relevance: "CURRENT",
      grounding_status: "VALID",
      lifecycle_status: "TRASHED",
      scientific_context: "CrystalNN",
      finding_count: 1,
      figure_count: 0,
      source_fingerprint: "fingerprint",
      created_at: "2026-08-29T00:00:00Z",
    })
    .mockResolvedValueOnce({
      report_id: "report-1",
      snapshot_id: "snapshot-1",
      project_id: "project-1",
      research_turn_id: "turn-1",
      scientific_result_snapshot_id: "result-1",
      scientific_interpretation_id: "interpretation-1",
      title: "结构分析报告",
      relevance_at_generation: "CURRENT",
      current_effective_relevance: "CURRENT",
      grounding_status: "VALID",
      lifecycle_status: "ACTIVE",
      scientific_context: "CrystalNN",
      finding_count: 1,
      figure_count: 0,
      source_fingerprint: "fingerprint",
      created_at: "2026-08-29T00:00:00Z",
  });
  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = await openReportMenu("结构分析报告");
  await user.click(screen.getByRole("menuitem", { name: "移入回收站" }));
  expect(await screen.findByRole("dialog", { name: "移入回收站前确认" })).toHaveTextContent("ScientificResult");
  expect(screen.getByRole("link", { name: "研究回合" })).toHaveAttribute(
    "href",
    "/projects/project-1/research/session-1?turn=turn-1",
  );
  expect(screen.getByRole("link", { name: "来源版本 · 结构" })).toHaveAttribute(
    "href",
    "/projects/project-1/data?object=object-1&version=version-1",
  );
  await user.click(screen.getByRole("button", { name: "确认移入回收站" }));
  expect(mocks.updateScientificReportLifecycle).toHaveBeenCalledWith("report-1", "TRASHED");

  await user.click(screen.getByRole("button", { name: "回收站" }));
  await openReportMenu("结构分析报告");
  await user.click(screen.getByRole("menuitem", { name: "恢复报告" }));
  expect(mocks.updateScientificReportLifecycle).toHaveBeenLastCalledWith("report-1", "ACTIVE");
});

it("exposes archive as a distinct recoverable report lifecycle", async () => {
  mocks.listScientificReports.mockResolvedValue({
    items: [{
      report_id: "report-archive",
      snapshot_id: "snapshot-archive",
      project_id: "project-1",
      research_turn_id: "turn-archive",
      scientific_result_snapshot_id: "result-archive",
      scientific_interpretation_id: "interpretation-archive",
      title: "可归档报告",
      relevance_at_generation: "CURRENT",
      current_effective_relevance: "CURRENT",
      grounding_status: "VALID",
      lifecycle_status: "ACTIVE",
      scientific_context: "Structure",
      finding_count: 1,
      figure_count: 0,
      source_fingerprint: "archive-fingerprint",
      created_at: "2026-08-29T00:00:00Z",
    }],
  });
  mocks.updateScientificReportLifecycle.mockResolvedValue({
    report_id: "report-archive",
    snapshot_id: "snapshot-archive",
    project_id: "project-1",
    research_turn_id: "turn-archive",
    scientific_result_snapshot_id: "result-archive",
    scientific_interpretation_id: "interpretation-archive",
    title: "可归档报告",
    relevance_at_generation: "CURRENT",
    current_effective_relevance: "CURRENT",
    grounding_status: "VALID",
    lifecycle_status: "ARCHIVED",
    scientific_context: "Structure",
    finding_count: 1,
    figure_count: 0,
    source_fingerprint: "archive-fingerprint",
    created_at: "2026-08-29T00:00:00Z",
  });

  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = await openReportMenu("可归档报告");
  await user.click(screen.getByRole("menuitem", { name: "归档" }));
  expect(mocks.updateScientificReportLifecycle).toHaveBeenCalledWith(
    "report-archive",
    "ARCHIVED",
  );
});

it("renames and pins reports as organization metadata without replacing their route", async () => {
  const report = {
    report_id: "report-organized",
    snapshot_id: "snapshot-organized",
    project_id: "project-1",
    research_turn_id: "turn-organized",
    scientific_result_snapshot_id: "result-organized",
    scientific_interpretation_id: "interpretation-organized",
    title: "原始报告标题",
    source_title: "原始报告标题",
    pinned: false,
    relevance_at_generation: "CURRENT" as const,
    current_effective_relevance: "CURRENT" as const,
    grounding_status: "VALID" as const,
    lifecycle_status: "ACTIVE" as const,
    scientific_context: "CrystalNN",
    finding_count: 1,
    figure_count: 0,
    source_fingerprint: "organization-fingerprint",
    created_at: "2026-09-01T00:00:00Z",
  };
  mocks.listScientificReports.mockResolvedValue({ items: [report] });
  mocks.updateScientificReportOrganization
    .mockResolvedValueOnce({ ...report, pinned: true })
    .mockResolvedValueOnce({ ...report, pinned: true, title: "面向论文的结构报告" });

  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = await openReportMenu("原始报告标题");
  await user.click(screen.getByRole("menuitem", { name: "列表置顶" }));

  expect(mocks.updateScientificReportOrganization).toHaveBeenCalledWith(
    "report-organized",
    { pinned: true },
  );
  expect(await screen.findByText("列表置顶 · 第 1 版 · 当前结果")).toBeInTheDocument();

  await openReportMenu("原始报告标题");
  await user.click(screen.getByRole("menuitem", { name: "重命名" }));
  const input = await screen.findByRole("textbox", { name: "报告显示名称" });
  await user.clear(input);
  await user.type(input, "面向论文的结构报告");
  await user.click(screen.getByRole("button", { name: "保存名称" }));

  expect(mocks.updateScientificReportOrganization).toHaveBeenLastCalledWith(
    "report-organized",
    { title: "面向论文的结构报告" },
  );
  expect(await screen.findByRole("link", { name: /面向论文的结构报告/ })).toHaveAttribute(
    "href",
    "/projects/project-1/reports/report-organized",
  );
});

it("creates a new immutable report revision without replacing the source route", async () => {
  const report = {
    report_id: "report-revision-1",
    snapshot_id: "snapshot-revision-1",
    project_id: "project-1",
    research_turn_id: "turn-revision",
    scientific_result_snapshot_id: "result-revision",
    scientific_interpretation_id: "interpretation-revision",
    title: "结构研究报告",
    revision_number: 1,
    relevance_at_generation: "CURRENT" as const,
    current_effective_relevance: "CURRENT" as const,
    grounding_status: "VALID" as const,
    lifecycle_status: "ACTIVE" as const,
    scientific_context: "CrystalNN + VoronoiNN",
    finding_count: 2,
    figure_count: 1,
    source_fingerprint: "revision-1-fingerprint",
    created_at: "2026-09-01T00:00:00Z",
  };
  mocks.listScientificReports.mockResolvedValue({ items: [report] });
  mocks.createScientificReportRevision.mockResolvedValue({
    ...report,
    report_id: "report-revision-2",
    snapshot_id: "snapshot-revision-2",
    parent_report_id: report.report_id,
    parent_snapshot_id: report.snapshot_id,
    revision_group_id: report.report_id,
    revision_number: 2,
    title: "结构研究报告（论文修订）",
    source_fingerprint: "revision-2-fingerprint",
  });
  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = await openReportMenu("结构研究报告");
  await user.click(screen.getByRole("menuitem", { name: "创建修订" }));
  const input = await screen.findByRole("textbox", { name: "新修订名称" });
  await user.clear(input);
  await user.type(input, "结构研究报告（论文修订）");
  await user.click(screen.getByRole("button", { name: "创建修订" }));

  expect(mocks.createScientificReportRevision).toHaveBeenCalledWith(
    "report-revision-1",
    {
      reason: "USER_REVISION",
      title: "结构研究报告（论文修订）",
    },
  );
  expect(
    await screen.findByRole("link", { name: /结构研究报告（论文修订）/ }),
  ).toHaveAttribute(
    "href",
    "/projects/project-1/reports/report-revision-2",
  );
  expect(screen.getByText("第 2 版 · 当前结果")).toBeInTheDocument();
  expect(
    screen.getByRole("link", { name: /结构研究报告.*第 1 版/ }),
  ).toHaveAttribute(
    "href",
    "/projects/project-1/reports/report-revision-1",
  );
});

it("supports bounded bulk archive and restore without exposing bulk trash", async () => {
  const report = {
    report_id: "report-bulk",
    snapshot_id: "snapshot-bulk",
    project_id: "project-1",
    research_turn_id: "turn-bulk",
    scientific_result_snapshot_id: "result-bulk",
    scientific_interpretation_id: "interpretation-bulk",
    title: "批量生命周期报告",
    relevance_at_generation: "CURRENT" as const,
    current_effective_relevance: "CURRENT" as const,
    grounding_status: "VALID" as const,
    lifecycle_status: "ACTIVE" as const,
    scientific_context: "Structure",
    finding_count: 1,
    figure_count: 0,
    source_fingerprint: "bulk-fingerprint",
    created_at: "2026-08-29T00:00:00Z",
  };
  mocks.listScientificReports.mockResolvedValue({ items: [report] });
  mocks.bulkUpdateScientificReportLifecycle.mockResolvedValue({
    lifecycle: "ARCHIVED",
    reportIds: ["report-bulk"],
    count: 1,
    items: [{ ...report, lifecycle_status: "ARCHIVED" }],
  });
  render(<ScientificReportsIndexPage projectId="project-1" />);

  const user = userEvent.setup();
  await screen.findByRole("link", { name: /批量生命周期报告/ });
  await user.click(screen.getByRole("button", { name: "批量管理" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 批量生命周期报告" }));
  await user.click(screen.getByRole("button", { name: "归档 1 份" }));
  expect(mocks.bulkUpdateScientificReportLifecycle).toHaveBeenCalledWith(
    "project-1",
    ["report-bulk"],
    "ARCHIVED",
  );
  expect(screen.queryByRole("button", { name: /批量回收站/ })).toBeNull();
});

it("offers explicit current-filter select-all and clear controls", async () => {
  const reports = ["report-a", "report-b"].map((reportId) => ({
    report_id: reportId,
    snapshot_id: `snapshot-${reportId}`,
    project_id: "project-1",
    research_turn_id: `turn-${reportId}`,
    scientific_result_snapshot_id: `result-${reportId}`,
    scientific_interpretation_id: `interpretation-${reportId}`,
    title: reportId === "report-a" ? "当前报告 A" : "当前报告 B",
    relevance_at_generation: "CURRENT" as const,
    current_effective_relevance: "CURRENT" as const,
    grounding_status: "VALID" as const,
    lifecycle_status: "ACTIVE" as const,
    scientific_context: "Structure",
    finding_count: 1,
    figure_count: 0,
    source_fingerprint: `${reportId}-fingerprint`,
    created_at: "2026-08-29T00:00:00Z",
  }));
  mocks.listScientificReports.mockResolvedValue({ items: reports });
  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = userEvent.setup();
  await screen.findByRole("link", { name: /当前报告 A/ });
  await user.click(screen.getByRole("button", { name: "批量管理" }));
  expect(screen.getByText("当前筛选")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "全选报告" }));
  expect(screen.getByText("2 份已选择")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "清空报告" })).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "清除选择" }));
  expect(screen.getByText("0 份已选择")).toBeInTheDocument();
});

it("keeps the full selection unchanged when atomic bulk lifecycle fails", async () => {
  const reports = ["report-ok", "report-failed"].map((reportId) => ({
    report_id: reportId,
    snapshot_id: `snapshot-${reportId}`,
    project_id: "project-1",
    research_turn_id: `turn-${reportId}`,
    scientific_result_snapshot_id: `result-${reportId}`,
    scientific_interpretation_id: `interpretation-${reportId}`,
    title: reportId === "report-ok" ? "成功报告" : "失败报告",
    relevance_at_generation: "CURRENT" as const,
    current_effective_relevance: "CURRENT" as const,
    grounding_status: "VALID" as const,
    lifecycle_status: "ACTIVE" as const,
    scientific_context: "Structure",
    finding_count: 1,
    figure_count: 0,
    source_fingerprint: `${reportId}-fingerprint`,
    created_at: "2026-08-29T00:00:00Z",
  }));
  mocks.listScientificReports.mockResolvedValue({ items: reports });
  mocks.bulkUpdateScientificReportLifecycle.mockRejectedValueOnce(
    new Error("service unavailable"),
  );

  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = userEvent.setup();
  await screen.findByRole("link", { name: /成功报告/ });
  await user.click(screen.getByRole("button", { name: "批量管理" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 成功报告" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 失败报告" }));
  await user.click(screen.getByRole("button", { name: "归档 2 份" }));

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "批量报告状态未更新；所选报告保持原状态，可检查权限或服务后重试。",
  );
  expect(screen.getByRole("link", { name: /成功报告/ })).toBeInTheDocument();
  expect(screen.getByRole("checkbox", { name: "选择 成功报告" })).toBeChecked();
  expect(screen.getByRole("checkbox", { name: "选择 失败报告" })).toBeChecked();
  expect(mocks.bulkUpdateScientificReportLifecycle).toHaveBeenCalledTimes(1);
});

it("clears report selection when changing lifecycle filters", async () => {
  mocks.listScientificReports.mockResolvedValue({
    items: [{
      report_id: "report-filter",
      snapshot_id: "snapshot-filter",
      project_id: "project-1",
      research_turn_id: "turn-filter",
      scientific_result_snapshot_id: "result-filter",
      scientific_interpretation_id: "interpretation-filter",
      title: "筛选报告",
      relevance_at_generation: "CURRENT",
      current_effective_relevance: "CURRENT",
      grounding_status: "VALID",
      lifecycle_status: "ACTIVE",
      scientific_context: "Dataset",
      finding_count: 1,
      figure_count: 0,
      source_fingerprint: "filter-fingerprint",
      created_at: "2026-08-29T00:00:00Z",
    }],
  });

  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = userEvent.setup();
  await screen.findByRole("link", { name: /筛选报告/ });
  await user.click(screen.getByRole("button", { name: "批量管理" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 筛选报告" }));
  expect(screen.getByText("1 份已选择")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "已归档" }));
  await user.click(screen.getByRole("button", { name: "当前" }));
  expect(screen.queryByRole("checkbox", { name: "选择 筛选报告" })).toBeNull();
  expect(screen.queryByText("1 份已选择")).toBeNull();
  await user.click(screen.getByRole("button", { name: "批量管理" }));
  expect(screen.getByRole("checkbox", { name: "选择 筛选报告" })).not.toBeChecked();
});

it("keeps bulk actions available when the all-reports filter mixes lifecycle states", async () => {
  const base = {
    snapshot_id: "snapshot-all",
    project_id: "project-1",
    research_turn_id: "turn-all",
    scientific_result_snapshot_id: "result-all",
    scientific_interpretation_id: "interpretation-all",
    relevance_at_generation: "CURRENT" as const,
    current_effective_relevance: "CURRENT" as const,
    grounding_status: "VALID" as const,
    scientific_context: "Dataset",
    finding_count: 1,
    figure_count: 0,
    source_fingerprint: "all-fingerprint",
    created_at: "2026-08-29T00:00:00Z",
  };
  mocks.listScientificReports.mockResolvedValue({
    items: [
      { ...base, report_id: "active-all", title: "全部中的活动报告", lifecycle_status: "ACTIVE" as const },
      { ...base, report_id: "archived-all", title: "全部中的归档报告", lifecycle_status: "ARCHIVED" as const },
    ],
  });
  mocks.updateScientificReportLifecycle.mockImplementation(async (reportId: string, status: string) => ({
    ...base,
    report_id: reportId,
    title: reportId === "active-all" ? "全部中的活动报告" : "全部中的归档报告",
    lifecycle_status: status,
  }));

  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = userEvent.setup();
  await screen.findByRole("link", { name: /全部中的活动报告/ });
  await user.click(screen.getByRole("button", { name: "全部" }));
  await user.click(screen.getByRole("button", { name: "批量管理" }));
  await user.click(screen.getByRole("checkbox", { name: "全选可批量操作报告" }));
  expect(screen.getByRole("button", { name: "归档 1 份" })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "恢复 1 份" })).toBeInTheDocument();
});

it("surfaces lifecycle request failures without dropping the report", async () => {
  mocks.listScientificReports.mockResolvedValue({
    items: [{
      report_id: "report-error",
      snapshot_id: "snapshot-error",
      project_id: "project-1",
      research_turn_id: "turn-error",
      scientific_result_snapshot_id: "result-error",
      scientific_interpretation_id: "interpretation-error",
      title: "失败回滚报告",
      relevance_at_generation: "CURRENT",
      current_effective_relevance: "CURRENT",
      grounding_status: "VALID",
      lifecycle_status: "ACTIVE",
      scientific_context: "Dataset",
      finding_count: 1,
      figure_count: 0,
      source_fingerprint: "error-fingerprint",
      created_at: "2026-08-29T00:00:00Z",
    }],
  });
  mocks.updateScientificReportLifecycle.mockRejectedValue(
    new Error("network unavailable"),
  );
  mocks.getScientificReportDependencyImpact.mockRejectedValue(
    new Error("dependency preview unavailable"),
  );

  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = await openReportMenu("失败回滚报告");
  await user.click(screen.getByRole("menuitem", { name: "移入回收站" }));
  expect(
    await screen.findByRole("alert"),
  ).toHaveTextContent("报告依赖影响暂时无法读取");
  expect(screen.getByRole("button", { name: "管理 失败回滚报告" })).toBeEnabled();
});

it("searches both report authorities and progressively reveals long ledgers", async () => {
  const grounded = Array.from({ length: 15 }, (_, index) => ({
    report_id: `report-${index + 1}`,
    snapshot_id: `snapshot-${index + 1}`,
    project_id: "project-1",
    research_turn_id: `turn-${index + 1}`,
    scientific_result_snapshot_id: `result-${index + 1}`,
    scientific_interpretation_id: `interpretation-${index + 1}`,
    title: index === 14 ? "目标结构报告" : `已验证报告 ${index + 1}`,
    relevance_at_generation: "CURRENT" as const,
    current_effective_relevance: "CURRENT" as const,
    grounding_status: "VALID" as const,
    lifecycle_status: "ACTIVE" as const,
    scientific_context: index === 14 ? "CrystalNN target" : "Dataset",
    finding_count: 1,
    figure_count: 0,
    source_fingerprint: `fingerprint-${index + 1}`,
    created_at:
      index === 14
        ? "2026-07-01T00:00:00Z"
        : `2026-08-${String(index + 1).padStart(2, "0")}T00:00:00Z`,
  }));
  mocks.listScientificReports.mockResolvedValue({ items: grounded });
  mocks.getProjectHistory.mockResolvedValue({
    project: { projectId: "project-1", name: "研究项目" },
    datasets: [{ datasetId: "dataset-1", name: "高熵合金数据" }],
    analyses: Array.from({ length: 15 }, (_, index) => ({
      jobId: `job-${index + 1}`,
      datasetId: "dataset-1",
      status: "completed",
      userQuestion: index === 14 ? "目标历史运行" : `历史问题 ${index + 1}`,
      toolIds: [index === 14 ? "structure.target" : "structure.rdf"],
      artifactTypes: [],
      stepCount: 1,
      artifactCount: 1,
      reportCount: 1,
      researchContextKind: "RESEARCH_TURN",
    })),
  });

  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = userEvent.setup();

  expect(await screen.findAllByRole("link", { name: /已验证报告/ })).toHaveLength(12);
  expect(screen.queryByRole("link", { name: /目标结构报告/ })).toBeNull();
  expect(screen.getByRole("button", { name: /加载更多已验证报告/ })).toHaveTextContent("还剩 3 份");
  expect(screen.getByRole("button", { name: /加载更多历史运行/ })).toHaveTextContent("还剩 3 份");

  await user.click(screen.getByRole("button", { name: /加载更多已验证报告/ }));
  expect(screen.getByRole("link", { name: /目标结构报告/ })).toBeInTheDocument();

  const search = screen.getByRole("searchbox", { name: "搜索报告" });
  await user.type(search, "目标");
  expect(screen.getByRole("link", { name: /目标结构报告/ })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /阅读旧版/ })).toHaveAttribute(
    "href",
    "/projects/project-1/reports/job-15",
  );
  expect(screen.getByText("找到 1 份已验证报告和 1 份历史运行报告")).toBeInTheDocument();
  expect(screen.queryByRole("link", { name: /已验证报告 1/ })).toBeNull();
});
