import React from "react";
import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

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

it("distinguishes an unavailable report authority from an empty list and retries in place", async () => {
  mocks.listScientificReports.mockRejectedValueOnce(new Error("unavailable"));
  render(<ScientificReportsIndexPage projectId="project-1" />);
  expect(await screen.findByRole("alert")).toHaveTextContent("研究报告暂时无法读取");
  expect(screen.queryByText("当前筛选下没有报告")).not.toBeInTheDocument();
  expect(screen.queryByText("还没有报告")).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "重新加载报告" }));
  expect(await screen.findByText("还没有报告")).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  expect(mocks.getProjectHistory).toHaveBeenCalledTimes(1);
  expect(mocks.getProjectHistory).toHaveBeenLastCalledWith("project-1", { forceRefresh: true, signal: expect.any(AbortSignal) });
  expect(screen.getByRole("link", { name: "前往研究" })).toHaveAttribute("href", "/projects/project-1/research");
});

it("labels unavailable legacy history even when verified reports loaded", async () => {
  mocks.getProjectHistory.mockRejectedValueOnce(new Error("unavailable"));
  render(<ScientificReportsIndexPage projectId="project-1" />);
  expect(await screen.findByRole("alert")).toHaveTextContent("分析记录暂时无法读取");
  expect(screen.getByText(/分析记录数量待确认/u)).toBeInTheDocument();
});

it("offers retry when neither report authority can be read", async () => {
  mocks.getProjectHistory.mockRejectedValueOnce(new Error("unavailable"));
  mocks.listScientificReports.mockRejectedValueOnce(new Error("unavailable"));
  render(<ScientificReportsIndexPage projectId="project-1" />);
  expect(await screen.findAllByRole("alert")).toHaveLength(2);
  await userEvent.click(screen.getByRole("button", { name: "重新加载分析记录" }));
  await userEvent.click(screen.getByRole("button", { name: "重新加载报告" }));
  expect(await screen.findByText("还没有报告")).toBeInTheDocument();
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

  expect(screen.getByRole("heading", { name: "报告", level: 1 })).toBeInTheDocument();
  expect(await screen.findByRole("heading", { name: "分析记录" })).toBeInTheDocument();
  expect(screen.queryByText("已验证结果")).not.toBeInTheDocument();
  expect(screen.queryByText("兼容历史运行")).not.toBeInTheDocument();
  expect(screen.getAllByRole("link", { name: /静态结构径向分布函数.*查看结果 →/ }).find(
    (link) => link.getAttribute("href")?.endsWith("job-legacy"),
  )).toHaveAttribute("href", "/projects/project-1/reports/job-legacy");
});

it("finds a joint analysis by any saved source name without inventing missing provenance", async () => {
  const sources = [{ datasetId: "si", name: "Si 晶体" }, { datasetId: "cu", name: "Cu 晶体" }, { datasetId: "nacl", name: "NaCl 晶体" }];
  const run = { datasetId: "si", status: "completed", artifactCount: 12, reportCount: 0, toolIds: ["structure.rdf"] };
  mocks.getProjectHistory.mockResolvedValue({
    project: { projectId: "project-1" }, datasets: sources,
    analyses: [
      { ...run, jobId: "joint", sourceDatasetIds: sources.map((source) => source.datasetId) },
      { ...run, jobId: "unverified", sourceDatasetIds: [] },
    ],
  });
  render(<ScientificReportsIndexPage projectId="project-1" />);
  const list = (await screen.findByRole("heading", { name: "分析记录" })).closest("section")!;
  const joint = within(list).getByRole("link", { name: /Si 晶体.*Cu 晶体.*NaCl 晶体/ });
  expect(joint).toHaveAttribute("href", "/projects/project-1/reports/joint");
  expect(within(list).getByRole("link", { name: /来源待核实/ })).not.toHaveTextContent("Si 晶体");
  const user = userEvent.setup();
  const search = screen.getByRole("searchbox", { name: "搜索报告" });
  for (const source of sources) {
    await user.clear(search);
    await user.type(search, source.name);
    expect(within(list).getAllByRole("link")).toHaveLength(1);
    expect(within(list).getByRole("link")).toHaveAttribute("href", "/projects/project-1/reports/joint");
  }
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
  await screen.findByRole("button", { name: "确认移入回收站" });
  await user.click(await screen.findByText("查看 3 项关联内容"));
  expect(screen.getByRole("dialog", { name: "移入回收站前确认" })).toHaveTextContent("分析结果");
  expect(screen.getByRole("link", { name: "研究回合" })).toHaveAttribute(
    "href",
    "/projects/project-1/research/session-1?turn=turn-1",
  );
  expect(screen.getByRole("link", { name: "来源版本 · 结构" })).toHaveAttribute(
    "href",
    "/projects/project-1/data?object=object-1&version=version-1",
  );
  await user.click(screen.getByRole("button", { name: "确认移入回收站" }));
  expect(mocks.updateScientificReportLifecycle).toHaveBeenCalledWith("report-1", "TRASHED", expect.any(AbortSignal));

  await user.click(screen.getByRole("button", { name: "回收站" }));
  await openReportMenu("结构分析报告");
  await user.click(screen.getByRole("menuitem", { name: "恢复报告" }));
  expect(mocks.updateScientificReportLifecycle).toHaveBeenLastCalledWith("report-1", "ACTIVE", expect.any(AbortSignal));
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
    expect.any(AbortSignal),
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
    expect.any(AbortSignal),
  );
  expect(await screen.findByText("列表置顶 · 第 1 版 · 当前结果")).toBeInTheDocument();

  await openReportMenu("原始报告标题");
  await user.click(screen.getByRole("menuitem", { name: "重命名" }));
  await user.keyboard("{Escape}");
  await waitFor(() => expect(screen.getByRole("button", { name: "管理 原始报告标题" })).toHaveFocus());
  await openReportMenu("原始报告标题");
  await user.click(screen.getByRole("menuitem", { name: "重命名" }));
  const input = await screen.findByRole("textbox", { name: "报告显示名称" });
  await user.clear(input);
  await user.type(input, "面向论文的结构报告");
  await user.click(screen.getByRole("button", { name: "保存名称" }));

  expect(mocks.updateScientificReportOrganization).toHaveBeenLastCalledWith(
    "report-organized",
    { title: "面向论文的结构报告" },
    expect.any(AbortSignal),
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
    expect.any(AbortSignal),
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
    expect.any(AbortSignal),
  );
  expect(screen.queryByRole("button", { name: /批量回收站/ })).toBeNull();
});

it("uses one select-all control to select and clear visible reports", async () => {
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
  await user.click(screen.getByRole("checkbox", { name: "全选可批量操作报告" }));
  expect(screen.getByText("2 份已选择")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "全选报告" })).not.toBeInTheDocument();
  await user.click(screen.getByRole("checkbox", { name: "全选可批量操作报告" }));
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
    "尚未确认批量归档的结果",
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
  ).toHaveTextContent("暂时无法检查关联内容");
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
  expect(screen.getByRole("button", { name: /加载更多研究报告/ })).toHaveTextContent("还剩 3 份");
  expect(screen.getByRole("button", { name: /加载更多分析记录/ })).toHaveTextContent("还剩 3 份");

  await user.click(screen.getByRole("button", { name: /加载更多研究报告/ }));
  expect(screen.getByRole("link", { name: /目标结构报告/ })).toBeInTheDocument();

  const search = screen.getByRole("searchbox", { name: "搜索报告" });
  await user.type(search, "目标");
  expect(screen.getByRole("link", { name: /目标结构报告/ })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /查看结果 →/ })).toHaveAttribute(
    "href",
    "/projects/project-1/reports/job-15",
  );
  expect(screen.getByText("1 份研究报告 · 1 条分析记录")).toBeInTheDocument();
  expect(screen.queryByRole("link", { name: /已验证报告 1/ })).toBeNull();
});

afterEach(() => { vi.useRealTimers(); });

const managedReport = {
  report_id: "report-1", snapshot_id: "snapshot-1", project_id: "project-1", title: "结构分析报告",
  research_turn_id: "turn-1", scientific_result_snapshot_id: "result-1", scientific_interpretation_id: "interpretation-1",
  lifecycle_status: "ACTIVE", relevance_at_generation: "CURRENT", current_effective_relevance: "CURRENT", grounding_status: "VALID",
  scientific_context: "材料结构", finding_count: 2, figure_count: 1, source_fingerprint: "source-1", created_at: "2026-09-01T00:00:00Z",
};

it("bounds an unconfirmed rename, keeps the draft and requires rereading before another write", async () => {
  mocks.listScientificReports.mockResolvedValue({ items: [managedReport] });
  let finish!: (value: unknown) => void;
  mocks.updateScientificReportOrganization.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = await openReportMenu(managedReport.title);
  await user.click(screen.getByRole("menuitem", { name: "重命名" }));
  const input = screen.getByRole("textbox", { name: "报告显示名称" });
  await user.clear(input); await user.type(input, "论文用报告");
  vi.useFakeTimers();
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "保存名称" }));
    fireEvent.click(screen.getByRole("button", { name: "保存名称" }));
  });
  expect(mocks.updateScientificReportOrganization).toHaveBeenCalledTimes(1);
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("dialog")).toHaveTextContent("尚未确认保存名称的结果");
  expect(input).toHaveValue("论文用报告");
  expect(input).toBeEnabled();
  expect(screen.getByRole("button", { name: "保存名称" })).toBeDisabled();
  expect(mocks.updateScientificReportOrganization.mock.calls[0][2].aborted).toBe(true);
  mocks.listScientificReports.mockRejectedValueOnce(new Error("offline"));
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新读取报告" })); });
  expect(screen.getByRole("button", { name: "保存名称" })).toBeDisabled();
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新读取报告" })); });
  expect(screen.getByRole("button", { name: "保存名称" })).toBeEnabled();
  await act(async () => { finish({ ...managedReport, title: "迟到的名称" }); });
  expect(screen.queryByText("迟到的名称")).not.toBeInTheDocument();
  expect(input).toHaveValue("论文用报告");
});

it.each(["report_id", "project_id", "snapshot_id"])("does not accept a report lifecycle write with a mismatched %s", async (field) => {
  mocks.listScientificReports.mockResolvedValue({ items: [managedReport] });
  mocks.updateScientificReportLifecycle.mockResolvedValue({ ...managedReport, lifecycle_status: "ARCHIVED", [field]: "wrong" });
  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = await openReportMenu(managedReport.title);
  await user.click(screen.getByRole("menuitem", { name: "归档" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("尚未确认归档报告的结果");
  expect(screen.getByRole("link", { name: /结构分析报告/ })).toBeInTheDocument();
});

it("rejects a dependency preview for another report and allows a local retry", async () => {
  mocks.listScientificReports.mockResolvedValue({ items: [managedReport] });
  const impactValue = await mocks.getScientificReportDependencyImpact();
  mocks.getScientificReportDependencyImpact.mockResolvedValueOnce({ ...impactValue, entityId: "foreign" });
  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = await openReportMenu(managedReport.title);
  await user.click(screen.getByRole("menuitem", { name: "移入回收站" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法检查关联内容");
  expect(screen.getByRole("button", { name: "确认移入回收站" })).toBeDisabled();
  expect(mocks.updateScientificReportLifecycle).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "重新检查" }));
  await waitFor(() => expect(screen.getByRole("button", { name: "确认移入回收站" })).toBeEnabled());
});

it("times out a dependency check and prevents it reopening a closed dialog", async () => {
  mocks.listScientificReports.mockResolvedValue({ items: [managedReport] });
  let finish!: (value: unknown) => void;
  mocks.getScientificReportDependencyImpact.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = await openReportMenu(managedReport.title);
  vi.useFakeTimers();
  await act(async () => { fireEvent.click(screen.getByRole("menuitem", { name: "移入回收站" })); });
  expect(screen.getByRole("dialog")).toHaveTextContent("正在检查关联内容");
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("button", { name: "确认移入回收站" })).toBeDisabled();
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "取消" })); });
  await act(async () => { finish({ entity: "scientific_report", entityId: "report-1", dependencies: [], dependencyCount: 0 }); });
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  expect(mocks.updateScientificReportLifecycle).not.toHaveBeenCalled();
});

it("rejects a bulk response with the correct count but different report identities", async () => {
  mocks.listScientificReports.mockResolvedValue({ items: [managedReport] });
  mocks.bulkUpdateScientificReportLifecycle.mockResolvedValue({ lifecycle: "ARCHIVED", reportIds: ["foreign"], count: 1, items: [{ ...managedReport, lifecycle_status: "ARCHIVED" }] });
  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = userEvent.setup(); await screen.findByRole("link", { name: /结构分析报告/ });
  await user.click(screen.getByRole("button", { name: "批量管理" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 结构分析报告" }));
  await user.click(screen.getByRole("button", { name: "归档 1 份" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("尚未确认批量归档的结果");
  expect(screen.getByRole("checkbox", { name: "选择 结构分析报告" })).toBeChecked();
});

it("cancels the old operation when navigating to another project", async () => {
  mocks.listScientificReports.mockResolvedValue({ items: [managedReport] });
  let finish!: (value: unknown) => void;
  mocks.updateScientificReportLifecycle.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
  const view = render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = await openReportMenu(managedReport.title); await user.click(screen.getByRole("menuitem", { name: "归档" }));
  mocks.listScientificReports.mockResolvedValue({ items: [] });
  mocks.getProjectHistory.mockResolvedValue({ project: { projectId: "project-2" }, datasets: [], analyses: [] });
  view.rerender(<ScientificReportsIndexPage projectId="project-2" />);
  await screen.findByText("还没有报告");
  expect(mocks.updateScientificReportLifecycle.mock.calls[0][2].aborted).toBe(true);
  await act(async () => { finish({ ...managedReport, lifecycle_status: "ARCHIVED" }); });
  expect(screen.queryByText("归档报告完成。")).not.toBeInTheDocument();
});

it("retains completed bulk batches when a later batch stalls and stays within the 100-report limit", async () => {
  const reports = Array.from({ length: 102 }, (_, index) => ({ ...managedReport, report_id: `report-${index}`, snapshot_id: `snapshot-${index}`, title: `报告 ${index}` }));
  mocks.listScientificReports.mockResolvedValue({ items: reports });
  mocks.bulkUpdateScientificReportLifecycle.mockImplementationOnce(async (_project: string, ids: string[]) => ({
    lifecycle: "ARCHIVED", reportIds: ids, count: ids.length, items: reports.filter((report) => ids.includes(report.report_id)).map((report) => ({ ...report, lifecycle_status: "ARCHIVED" })),
  })).mockImplementationOnce(() => new Promise(() => {}));
  render(<ScientificReportsIndexPage projectId="project-1" />);
  await screen.findByRole("link", { name: /报告 0/ });
  while (screen.queryByRole("button", { name: /加载更多研究报告/ })) fireEvent.click(screen.getByRole("button", { name: /加载更多研究报告/ }));
  fireEvent.click(screen.getByRole("button", { name: "批量管理" }));
  fireEvent.click(screen.getByRole("checkbox", { name: "全选可批量操作报告" }));
  vi.useFakeTimers();
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "归档 102 份" })); });
  expect(mocks.bulkUpdateScientificReportLifecycle.mock.calls.map((call) => call[1].length)).toEqual([100, 2]);
  expect(screen.getByText("2 份已选择")).toBeInTheDocument();
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("alert")).toHaveTextContent("尚未确认批量归档的结果");
  expect(screen.getByRole("link", { name: /报告 100/ })).toBeInTheDocument();
  expect(screen.queryByRole("link", { name: /报告 0 / })).not.toBeInTheDocument();
});

it("rejects a revision for a different source while keeping its name editable", async () => {
  mocks.listScientificReports.mockResolvedValue({ items: [managedReport] });
  mocks.createScientificReportRevision.mockResolvedValue({ ...managedReport, report_id: "new-report", parent_report_id: "foreign-report" });
  render(<ScientificReportsIndexPage projectId="project-1" />);
  const user = await openReportMenu(managedReport.title);
  await user.click(screen.getByRole("menuitem", { name: "创建修订" }));
  await user.click(screen.getByRole("button", { name: "创建修订" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("尚未确认创建修订的结果");
  expect(screen.getByRole("textbox", { name: "新修订名称" })).toHaveValue("结构分析报告（修订 2）");
  expect(screen.getByRole("button", { name: "创建修订" })).toBeDisabled();
});

const readableHistory = {
  project: { projectId: "project-1", name: "研究项目" }, datasets: [],
  analyses: [{ jobId: "saved-job", status: "completed", title: "已保存的分析", toolIds: [], artifactTypes: [], stepCount: 1, artifactCount: 1, reportCount: 1 }],
};

it("shows a saved analysis while the report catalogue stalls and retries only that catalogue", async () => {
  vi.useFakeTimers();
  let finish!: (value: unknown) => void;
  mocks.listScientificReports.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
  mocks.getProjectHistory.mockResolvedValue(readableHistory);
  render(<ScientificReportsIndexPage projectId="project-1" />);
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  expect(screen.getByRole("link", { name: /查看结果 →/ })).toHaveAttribute("href", "/projects/project-1/reports/saved-job");
  fireEvent.change(screen.getByRole("searchbox", { name: "搜索报告" }), { target: { value: "材料" } });
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("alert")).toHaveTextContent("研究报告暂时无法读取");
  expect(mocks.listScientificReports.mock.calls[0][1].aborted).toBe(true);
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新加载报告" })); });
  await act(async () => { finish({ items: [{ report_id: "late", project_id: "project-1", title: "迟到报告" }] }); });
  expect(screen.queryByText("迟到报告")).not.toBeInTheDocument();
  expect(screen.getByRole("searchbox", { name: "搜索报告" })).toHaveValue("材料");
  expect(mocks.getProjectHistory).toHaveBeenCalledTimes(1);
});

it("retains analysis links and search on failed refresh and restores the failed source locally", async () => {
  const user = userEvent.setup();
  mocks.getProjectHistory.mockResolvedValue(readableHistory);
  render(<ScientificReportsIndexPage projectId="project-1" />);
  await screen.findByRole("link", { name: /查看结果 →/ });
  mocks.getProjectHistory.mockRejectedValueOnce(new Error("offline"));
  await user.click(screen.getByRole("button", { name: "刷新列表" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("分析记录暂时无法读取");
  expect(screen.getByRole("link", { name: /查看结果 →/ })).toHaveAttribute("href", "/projects/project-1/reports/saved-job");
  expect(screen.queryByText("还没有报告")).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重新加载分析记录" }));
  await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
  expect(mocks.listScientificReports).toHaveBeenCalledTimes(2);
});

it("rejects mismatched project identities without offering links to foreign reports", async () => {
  mocks.listScientificReports.mockResolvedValue({ items: [{ report_id: "foreign", title: "其他项目报告", project_id: "project-2" }] });
  mocks.getProjectHistory.mockResolvedValue({ ...readableHistory, project: { projectId: "project-2" } });
  render(<ScientificReportsIndexPage projectId="project-1" />);
  expect(await screen.findAllByRole("alert")).toHaveLength(2);
  expect(screen.queryByRole("link", { name: /其他项目报告|查看结果 →/ })).not.toBeInTheDocument();
});

it("aborts old reads and clears report search when the project changes", async () => {
  vi.useFakeTimers();
  let finish!: (value: unknown) => void;
  mocks.getProjectHistory.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
  const view = render(<ScientificReportsIndexPage projectId="project-1" />);
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  fireEvent.change(screen.getByRole("searchbox", { name: "搜索报告" }), { target: { value: "旧项目搜索" } });
  mocks.getProjectHistory.mockResolvedValueOnce({ project: { projectId: "project-2" }, analyses: [], datasets: [] });
  view.rerender(<ScientificReportsIndexPage projectId="project-2" />);
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  expect(mocks.getProjectHistory.mock.calls[0][1].signal.aborted).toBe(true);
  await act(async () => { finish(readableHistory); });
  expect(screen.getByRole("searchbox", { name: "搜索报告" })).toHaveValue("");
  expect(screen.queryByRole("link", { name: /查看结果 →/ })).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: "前往研究" })).toHaveAttribute("href", "/projects/project-2/research");
});
