import React from "react";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  searchProduct: vi.fn(),
  updateProject: vi.fn(),
  bulkProjectAction: vi.fn(),
  updateDataset: vi.fn(),
  bulkDatasetAction: vi.fn(),
  deleteEmptyProject: vi.fn(),
  deleteEmptyDataset: vi.fn(),
  getProjectDependencyImpact: vi.fn(),
  getDatasetDependencyImpact: vi.fn(),
  updateResearchSession: vi.fn(),
  bulkUpdateResearchSessions: vi.fn(),
  updateScientificReportLifecycle: vi.fn(),
  bulkUpdateScientificReportLifecycle: vi.fn(),
  updateScientificObject: vi.fn(),
  bulkUpdateScientificObjects: vi.fn(),
}));

vi.mock("../lib/planner-api", () => ({
  searchProduct: mocks.searchProduct,
  updateProject: mocks.updateProject,
  bulkProjectAction: mocks.bulkProjectAction,
  updateDataset: mocks.updateDataset,
  bulkDatasetAction: mocks.bulkDatasetAction,
  deleteEmptyProject: mocks.deleteEmptyProject,
  deleteEmptyDataset: mocks.deleteEmptyDataset,
  getProjectDependencyImpact: mocks.getProjectDependencyImpact,
  getDatasetDependencyImpact: mocks.getDatasetDependencyImpact,
}));
vi.mock("../lib/product-api", () => ({
  updateResearchSession: mocks.updateResearchSession,
  bulkUpdateResearchSessions: mocks.bulkUpdateResearchSessions,
}));
vi.mock("../lib/scientific-report-api", () => ({
  updateScientificReportLifecycle: mocks.updateScientificReportLifecycle,
  bulkUpdateScientificReportLifecycle: mocks.bulkUpdateScientificReportLifecycle,
}));
vi.mock("../lib/scientific-viewer-api", () => ({
  updateScientificObject: mocks.updateScientificObject,
  bulkUpdateScientificObjects: mocks.bulkUpdateScientificObjects,
}));
vi.mock("./ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));
vi.mock("./ProductNavigation", () => ({
  ProductLink: ({ children, href, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) => <a href={href} {...props}>{children}</a>,
}));

import { TrashCenterPage } from "./TrashCenterPage";

const trashedItems = [
  {
    kind: "research",
    id: "research-1",
    projectId: "project-1",
    title: "被移除的研究",
    subtitle: "研究会话",
    href: "/projects/project-1/research/research-1",
    status: "trashed",
    updatedAt: "2026-08-31T08:00:00Z",
  },
  {
    kind: "project",
    id: "project-empty",
    projectId: "project-empty",
    title: "空白验收项目",
    subtitle: "项目",
    href: "/projects/project-empty",
    status: "trashed",
    updatedAt: "2026-08-31T09:00:00Z",
  },
] as const;

beforeEach(() => {
  vi.clearAllMocks();
  mocks.searchProduct.mockResolvedValue({
    query: "",
    count: trashedItems.length,
    items: trashedItems,
  });
  mocks.updateResearchSession.mockResolvedValue({
    id: "research-1",
    project_id: "project-1",
    title: "被移除的研究",
    status: "ACTIVE",
  });
  mocks.bulkProjectAction.mockImplementation(async (ids: string[]) => ({
    action: "restore",
    projectIds: ids,
    count: ids.length,
  }));
  mocks.bulkDatasetAction.mockImplementation(async (ids: string[]) => ({
    action: "restore",
    datasetIds: ids,
    count: ids.length,
  }));
  mocks.bulkUpdateResearchSessions.mockImplementation(
    async (_projectId: string, ids: string[]) => ({
      action: "RESTORE",
      sessionIds: ids,
      count: ids.length,
    }),
  );
  mocks.bulkUpdateScientificReportLifecycle.mockImplementation(
    async (_projectId: string, ids: string[]) => ({
      lifecycle: "ACTIVE",
      reportIds: ids,
      items: [],
      count: ids.length,
    }),
  );
  mocks.bulkUpdateScientificObjects.mockImplementation(
    async (_projectId: string, ids: string[]) => ({
      project_id: "project-1",
      lifecycle: "ACTIVE",
      items: [],
      count: ids.length,
    }),
  );
  mocks.getProjectDependencyImpact.mockResolvedValue({
    entity: "project",
    entityId: "project-empty",
    displayName: "空白验收项目",
    canDelete: true,
    dependencyCount: 0,
    dependencies: [],
    retentionPolicy: {
      schemaVersion: "phase14r-retention/1.0",
      automaticPurge: "DISABLED",
      referencedProvenance: "PROTECTED_INDEFINITELY",
      unreferencedTrash: "MANUAL_OWNER_PURGE",
      manualPurge: "SERVER_ZERO_DEPENDENCY_ONLY",
      manualPurgeRequiresZeroDependencies: true,
    },
    impact: {
      removedFromActiveDiscovery: true,
      historicalProvenanceProtected: false,
      historicalResearchRemainsAccessible: false,
    },
  });
  mocks.deleteEmptyProject.mockResolvedValue({ projectId: "project-empty", deleted: true });
});

it("loads the unified recoverable trash and restores a research session", async () => {
  const user = userEvent.setup();
  render(<TrashCenterPage />);

  expect(await screen.findByRole("heading", { name: "回收站" })).toBeInTheDocument();
  expect(mocks.searchProduct).toHaveBeenCalledWith("", { status: "trashed", limit: 100 });
  expect(screen.getByText("被移除的研究")).toBeInTheDocument();
  expect(screen.getByText("空白验收项目")).toBeInTheDocument();

  const row = screen.getByText("被移除的研究").closest("article");
  await user.click(row!.querySelector<HTMLButtonElement>("button")!);

  await waitFor(() => expect(mocks.updateResearchSession).toHaveBeenCalledWith("research-1", { lifecycle: "ACTIVE" }));
  expect(screen.queryByText("被移除的研究")).not.toBeInTheDocument();
  expect(screen.getByRole("status")).toHaveTextContent("已恢复");
});

it("restores a mixed selection through authorized atomic service batches", async () => {
  const user = userEvent.setup();
  mocks.searchProduct.mockResolvedValueOnce({
    query: "",
    count: 5,
    items: [
      trashedItems[1],
      {
        kind: "dataset",
        id: "dataset-1",
        projectId: "project-1",
        title: "数据集",
        subtitle: "材料表",
        href: "/projects/project-1/data?dataset=dataset-1",
        status: "trashed",
      },
      {
        kind: "scientific_object",
        id: "object-1",
        projectId: "project-1",
        title: "结构",
        subtitle: "科学对象",
        href: "/projects/project-1/data?object=object-1",
        status: "trashed",
      },
      trashedItems[0],
      {
        kind: "report",
        id: "report-1",
        projectId: "project-1",
        title: "科学报告",
        subtitle: "报告",
        href: "/projects/project-1/reports/report-1",
        status: "trashed",
      },
    ],
  });
  render(<TrashCenterPage />);

  await screen.findByText("空白验收项目");
  await user.click(screen.getByRole("button", { name: "选择当前筛选" }));
  await user.click(screen.getByRole("button", { name: "恢复所选（5）" }));

  await waitFor(() =>
    expect(mocks.bulkProjectAction).toHaveBeenCalledWith(
      ["project-empty"],
      "restore",
    ),
  );
  expect(mocks.bulkDatasetAction).toHaveBeenCalledWith(
    ["dataset-1"],
    "restore",
  );
  expect(mocks.bulkUpdateScientificObjects).toHaveBeenCalledWith(
    "project-1",
    ["object-1"],
    "ACTIVE",
  );
  expect(mocks.bulkUpdateResearchSessions).toHaveBeenCalledWith(
    "project-1",
    ["research-1"],
    "RESTORE",
  );
  expect(mocks.bulkUpdateScientificReportLifecycle).toHaveBeenCalledWith(
    "project-1",
    ["report-1"],
    "ACTIVE",
  );
  expect(await screen.findByText("已恢复 5 项；科学历史与精确来源未发生变化。")).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "当前筛选下没有内容" })).toBeInTheDocument();
});

it("keeps unauthorized batch items selected and reports an explicit partial failure", async () => {
  const user = userEvent.setup();
  mocks.bulkProjectAction.mockRejectedValueOnce(new Error("forbidden"));
  render(<TrashCenterPage />);

  await screen.findByText("空白验收项目");
  await user.click(screen.getByRole("button", { name: "选择当前筛选" }));
  await user.click(screen.getByRole("button", { name: "恢复所选（2）" }));

  expect(
    await screen.findByText(
      "已恢复 1 项；1 项未恢复（项目）。失败项仍保留在回收站并保持选中，请检查权限或服务后重试。",
    ),
  ).toBeInTheDocument();
  expect(screen.queryByText("被移除的研究")).not.toBeInTheDocument();
  expect(screen.getByText("空白验收项目")).toBeInTheDocument();
  expect(screen.getByRole("checkbox", { name: "选择恢复项目“空白验收项目”" })).toBeChecked();
  expect(screen.getByRole("button", { name: "恢复所选（1）" })).toBeEnabled();
});

it("requires server approval and stable identity confirmation before permanent deletion", async () => {
  const user = userEvent.setup();
  render(<TrashCenterPage />);
  const projectTitle = await screen.findByText("空白验收项目");
  const row = projectTitle.closest("article")!;

  await user.click(screen.getByRole("button", { name: "永久删除…", hidden: false }));
  expect(await screen.findByRole("dialog", { name: "永久删除空项目？" })).toBeInTheDocument();
  expect(screen.getByText(/自动清理已禁用/)).toBeInTheDocument();
  expect(mocks.getProjectDependencyImpact).toHaveBeenCalledWith("project-empty");
  const confirm = screen.getByRole("button", { name: "确认永久删除" });
  expect(confirm).toBeDisabled();

  expect(screen.getByText("标题可能重复；类型与 ID 用于确认当前选中的确切实体。")).toBeInTheDocument();
  await user.type(screen.getByRole("textbox"), "project:project-empty");
  expect(confirm).toBeEnabled();
  await user.click(confirm);

  await waitFor(() => expect(mocks.deleteEmptyProject).toHaveBeenCalledWith("project-empty"));
  expect(row).not.toBeInTheDocument();
});

it("does not let duplicate titles make the destructive confirmation ambiguous", async () => {
  const user = userEvent.setup();
  mocks.searchProduct.mockResolvedValueOnce({
    query: "",
    count: 3,
    items: [
      ...trashedItems,
      {
        kind: "project",
        id: "project-empty-2",
        projectId: "project-empty-2",
        title: "空白验收项目",
        subtitle: "同名项目",
        href: "/projects/project-empty-2",
        status: "trashed",
        updatedAt: "2026-08-31T10:00:00Z",
      },
    ],
  });
  render(<TrashCenterPage />);

  const rows = await screen.findAllByRole("heading", { name: "空白验收项目" });
  expect(rows).toHaveLength(2);
  const targetRow = rows[1].closest("article")!;
  await user.click(
    within(targetRow).getByRole("button", { name: "永久删除…" }),
  );
  expect(
    await screen.findByText("project:project-empty-2"),
  ).toBeInTheDocument();
  const confirm = screen.getByRole("button", { name: "确认永久删除" });
  await user.type(screen.getByRole("textbox"), "project:project-empty");
  expect(confirm).toBeDisabled();
  expect(mocks.deleteEmptyProject).not.toHaveBeenCalled();
  await user.clear(screen.getByRole("textbox"));
  await user.type(screen.getByRole("textbox"), "project:project-empty-2");
  expect(confirm).toBeEnabled();
  await user.click(confirm);

  await waitFor(() =>
    expect(mocks.deleteEmptyProject).toHaveBeenCalledWith("project-empty-2"),
  );
});

it("does not offer destructive deletion when scientific dependencies protect the item", async () => {
  const user = userEvent.setup();
  mocks.getProjectDependencyImpact.mockResolvedValueOnce({
    entity: "project",
    entityId: "project-empty",
    displayName: "空白验收项目",
    canDelete: false,
    dependencyCount: 2,
    dependencies: [{
      kind: "scientific_result",
      label: "科学结果",
      count: 2,
      href: "/projects/project-empty/research",
    }],
    impact: {
      removedFromActiveDiscovery: true,
      historicalProvenanceProtected: true,
      historicalResearchRemainsAccessible: true,
    },
  });
  render(<TrashCenterPage />);

  await screen.findByText("空白验收项目");
  await user.click(screen.getByRole("button", { name: "永久删除…" }));
  expect(await screen.findByRole("dialog", { name: "该内容受科学依赖保护" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "科学结果" })).toHaveAttribute(
    "href",
    "/projects/project-empty/research",
  );
  expect(screen.queryByRole("button", { name: "确认永久删除" })).not.toBeInTheDocument();
  expect(mocks.deleteEmptyProject).not.toHaveBeenCalled();
});

it("keeps an empty trash view from becoming a navigation dead end", async () => {
  mocks.searchProduct.mockResolvedValueOnce({
    query: "",
    count: 0,
    items: [],
  });
  render(<TrashCenterPage />);

  expect(await screen.findByRole("heading", { name: "当前筛选下没有内容" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "查看项目" })).toHaveAttribute("href", "/projects");
  expect(screen.getByRole("link", { name: "返回控制台" })).toHaveAttribute("href", "/console");
});

it("offers an in-place retry when the trash inventory cannot be read", async () => {
  const user = userEvent.setup();
  mocks.searchProduct
    .mockRejectedValueOnce(new Error("service unavailable"))
    .mockResolvedValueOnce({ query: "", count: 0, items: [] });
  render(<TrashCenterPage />);

  expect(await screen.findByRole("heading", { name: "回收站暂时无法读取" })).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重新加载回收站" }));
  expect(await screen.findByRole("heading", { name: "当前筛选下没有内容" })).toBeInTheDocument();
  expect(mocks.searchProduct).toHaveBeenCalledTimes(2);
});
