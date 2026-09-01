import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  searchProduct: vi.fn(),
  updateProject: vi.fn(),
  updateDataset: vi.fn(),
  deleteEmptyProject: vi.fn(),
  deleteEmptyDataset: vi.fn(),
  getProjectDependencyImpact: vi.fn(),
  getDatasetDependencyImpact: vi.fn(),
  updateResearchSession: vi.fn(),
  updateScientificReportLifecycle: vi.fn(),
  updateScientificObject: vi.fn(),
}));

vi.mock("../lib/planner-api", () => ({
  searchProduct: mocks.searchProduct,
  updateProject: mocks.updateProject,
  updateDataset: mocks.updateDataset,
  deleteEmptyProject: mocks.deleteEmptyProject,
  deleteEmptyDataset: mocks.deleteEmptyDataset,
  getProjectDependencyImpact: mocks.getProjectDependencyImpact,
  getDatasetDependencyImpact: mocks.getDatasetDependencyImpact,
}));
vi.mock("../lib/product-api", () => ({
  updateResearchSession: mocks.updateResearchSession,
}));
vi.mock("../lib/scientific-report-api", () => ({
  updateScientificReportLifecycle: mocks.updateScientificReportLifecycle,
}));
vi.mock("../lib/scientific-viewer-api", () => ({
  updateScientificObject: mocks.updateScientificObject,
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
  mocks.getProjectDependencyImpact.mockResolvedValue({
    entity: "project",
    entityId: "project-empty",
    displayName: "空白验收项目",
    canDelete: true,
    dependencyCount: 0,
    dependencies: [],
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

it("requires server approval and exact-name confirmation before permanent deletion", async () => {
  const user = userEvent.setup();
  render(<TrashCenterPage />);
  const projectTitle = await screen.findByText("空白验收项目");
  const row = projectTitle.closest("article")!;

  await user.click(screen.getByRole("button", { name: "永久删除…", hidden: false }));
  expect(await screen.findByRole("dialog", { name: "永久删除空项目？" })).toBeInTheDocument();
  expect(mocks.getProjectDependencyImpact).toHaveBeenCalledWith("project-empty");
  const confirm = screen.getByRole("button", { name: "确认永久删除" });
  expect(confirm).toBeDisabled();

  await user.type(screen.getByRole("textbox"), "空白验收项目");
  expect(confirm).toBeEnabled();
  await user.click(confirm);

  await waitFor(() => expect(mocks.deleteEmptyProject).toHaveBeenCalledWith("project-empty"));
  expect(row).not.toBeInTheDocument();
});

it("does not offer destructive deletion when scientific dependencies protect the item", async () => {
  const user = userEvent.setup();
  mocks.getProjectDependencyImpact.mockResolvedValueOnce({
    entity: "project",
    entityId: "project-empty",
    displayName: "空白验收项目",
    canDelete: false,
    dependencyCount: 2,
    dependencies: [{ kind: "scientific_result", label: "科学结果", count: 2 }],
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
  expect(screen.queryByRole("button", { name: "确认永久删除" })).not.toBeInTheDocument();
  expect(mocks.deleteEmptyProject).not.toHaveBeenCalled();
});
