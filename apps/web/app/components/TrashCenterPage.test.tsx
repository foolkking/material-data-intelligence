import React from "react";
import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

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
vi.mock("../../shared/layout/ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));
vi.mock("../../shared/layout/ProductNavigation", () => ({
  ProductLink: ({ children, href, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) => <a href={href} {...props}>{children}</a>,
}));

import { TrashCenterPage } from "./TrashCenterPage";
import { trashRestoreBatches } from "../../features/projects/trash-operations";

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
  vi.resetAllMocks();
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
      items: ids.map((id) => ({ id, project_id: "project-1", lifecycle_status: "ACTIVE" })),
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

afterEach(() => vi.useRealTimers());
it("keeps multi-page recovery within each service's 100-item limit", async () => {
  const items = Array.from({ length: 205 }, (_, i) => ({ ...trashedItems[1], id: `p-${i}`, projectId: `p-${i}` }));
  const batches = trashRestoreBatches(items);
  expect(batches.map((batch) => batch.items.length)).toEqual([100, 100, 5]);
  await Promise.all(batches.map((batch) => batch.run(new AbortController().signal)));
  expect(mocks.bulkProjectAction.mock.calls.flatMap((call) => call[0])).toEqual(items.map((item) => item.id));
});
const signal = expect.any(AbortSignal);
async function showProjectDetail(user: ReturnType<typeof userEvent.setup>, index = 0) {
  await user.click((await screen.findAllByRole("button", { name: "查看 空白验收项目 的详情" }))[index]);
  await user.click(screen.getByRole("button", { name: "永久删除…" }));
}
async function selectAll(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole("button", { name: "批量选择" }));
  await user.click(screen.getByRole("checkbox", { name: "选择当前显示的内容" }));
}
function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => { resolve = done; });
  return { promise, resolve };
}

it("restores one exact record and keeps implementation detail out of the list", async () => {
  const user = userEvent.setup(); render(<TrashCenterPage />);
  const title = await screen.findByText("被移除的研究");
  expect(mocks.searchProduct).toHaveBeenCalledWith("", { status: "trashed", limit: 100, signal });
  expect(screen.queryByText("技术身份")).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "永久删除…" })).not.toBeInTheDocument();
  await user.click(within(title.closest("article")!).getByRole("button", { name: "恢复" }));
  await waitFor(() => expect(mocks.bulkUpdateResearchSessions).toHaveBeenCalledWith("project-1", ["research-1"], "RESTORE", signal));
  expect(screen.queryByText("被移除的研究")).not.toBeInTheDocument();
  expect(screen.getByRole("status")).toHaveTextContent("已恢复“被移除的研究”。");
});

it("restores a mixed selection with exact atomic service batches", async () => {
  const user = userEvent.setup();
  mocks.searchProduct.mockResolvedValueOnce({ query: "", count: 5, items: [
    ...trashedItems,
    ...(["dataset", "scientific_object", "report"] as const).map((kind) => ({ kind, id: `${kind}-1`, projectId: "project-1", title: kind, subtitle: "", status: "trashed", href: "/source" })),
  ] });
  render(<TrashCenterPage />); await screen.findByText("空白验收项目"); await selectAll(user);
  await user.click(screen.getByRole("button", { name: "恢复所选（5）" }));
  expect(await screen.findByText("已恢复 5 项。")).toBeInTheDocument();
  expect(mocks.bulkProjectAction).toHaveBeenCalledWith(["project-empty"], "restore", signal);
  expect(mocks.bulkDatasetAction).toHaveBeenCalledWith(["dataset-1"], "restore", signal);
  expect(mocks.bulkUpdateScientificObjects).toHaveBeenCalledWith("project-1", ["scientific_object-1"], "ACTIVE", signal);
  expect(mocks.bulkUpdateResearchSessions).toHaveBeenCalledWith("project-1", ["research-1"], "RESTORE", signal);
  expect(mocks.bulkUpdateScientificReportLifecycle).toHaveBeenCalledWith("project-1", ["report-1"], "ACTIVE", signal);
  expect(screen.getByRole("heading", { name: "回收站是空的" })).toBeInTheDocument();
});

it("settles successful siblings immediately and requires rereading uncertain writes", async () => {
  const user = userEvent.setup(), pending = deferred<unknown>();
  mocks.bulkProjectAction.mockReturnValueOnce(pending.promise);
  render(<TrashCenterPage />); await screen.findByText("空白验收项目"); await selectAll(user);
  vi.useFakeTimers();
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "恢复所选（2）" })); });
  expect(screen.queryByText("被移除的研究")).not.toBeInTheDocument();
  expect(screen.getByText("空白验收项目")).toBeInTheDocument();
  await act(async () => { vi.advanceTimersByTime(10_000); });
  expect(screen.getByRole("alert")).toHaveTextContent("已恢复 1 项；1 项的恢复结果尚未确认");
  expect(screen.getByRole("checkbox", { name: "选择 空白验收项目" })).toBeDisabled();
  expect(mocks.bulkProjectAction.mock.calls[0][2].aborted).toBe(true);
  await act(async () => { pending.resolve({ action: "restore", projectIds: ["project-empty"], count: 1 }); });
  expect(screen.getByText("空白验收项目")).toBeInTheDocument();
  vi.useRealTimers();
  mocks.searchProduct.mockResolvedValueOnce({ query: "", count: 1, items: [trashedItems[1]] });
  await user.click(screen.getByRole("button", { name: "刷新列表" }));
  await waitFor(() => expect(screen.getByRole("checkbox", { name: "选择 空白验收项目" })).toBeEnabled());
});

it("rejects a same-count response with different restored identities", async () => {
  const user = userEvent.setup();
  mocks.bulkProjectAction.mockResolvedValueOnce({ action: "restore", count: 1, projectIds: ["foreign"] });
  render(<TrashCenterPage />); const title = await screen.findByText("空白验收项目");
  await user.click(within(title.closest("article")!).getByRole("button", { name: "恢复" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("恢复结果尚未确认");
  expect(screen.getByText("空白验收项目")).toBeInTheDocument();
});

it("clears hidden selection when the type or search changes", async () => {
  const user = userEvent.setup();
  mocks.searchProduct.mockImplementation(async (query: string, options: { kind?: string }) => ({ query, count: 2, items: trashedItems.filter((item) => (!options.kind || item.kind === options.kind) && item.title.includes(query)) }));
  render(<TrashCenterPage />); await screen.findByText("空白验收项目"); await selectAll(user);
  await user.click(screen.getByRole("button", { name: "项目" }));
  await waitFor(() => expect(screen.getByRole("checkbox", { name: "选择 空白验收项目" })).toBeEnabled());
  expect(screen.getByRole("button", { name: "恢复所选（0）" })).toBeDisabled();
  expect(screen.queryByText("被移除的研究")).not.toBeInTheDocument();
  await user.click(screen.getByRole("checkbox", { name: "选择当前显示的内容" }));
  await user.type(screen.getByRole("searchbox"), "空白");
  await waitFor(() => expect(mocks.searchProduct).toHaveBeenLastCalledWith("空白", expect.objectContaining({ kind: "project", signal })));
  expect(screen.getByRole("button", { name: "恢复所选（0）" })).toBeDisabled();
  await user.click(screen.getByRole("checkbox", { name: "选择当前显示的内容" }));
  await user.click(screen.getByRole("button", { name: "恢复所选（1）" }));
  await waitFor(() => expect(mocks.bulkProjectAction).toHaveBeenCalledWith(["project-empty"], "restore", signal));
  expect(mocks.bulkUpdateResearchSessions).not.toHaveBeenCalled();
});

it("retains loaded rows on failed refresh and retries the same page cursor", async () => {
  const user = userEvent.setup();
  mocks.searchProduct.mockResolvedValueOnce({ query: "", count: 1, items: [trashedItems[0]], nextCursor: "page-2", truncated: true });
  render(<TrashCenterPage />); await screen.findByText("被移除的研究");
  mocks.searchProduct.mockRejectedValueOnce(new Error("offline"));
  await user.click(screen.getByRole("button", { name: "显示更多" }));
  expect(await screen.findByText("列表暂时无法更新")).toBeInTheDocument();
  expect(screen.getByText("被移除的研究")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重新加载回收站" }));
  await screen.findByText("空白验收项目");
  expect(mocks.searchProduct).toHaveBeenLastCalledWith("", expect.objectContaining({ cursor: "page-2" }));
  expect(screen.getAllByRole("heading", { name: "被移除的研究" })).toHaveLength(1);
  mocks.searchProduct.mockRejectedValueOnce(new Error("offline"));
  await user.click(screen.getByRole("button", { name: "刷新列表" }));
  await screen.findByText("列表暂时无法更新");
  expect(screen.getByText("空白验收项目")).toBeInTheDocument();
});

it("bounds a stalled refresh and ignores its late response after recovery", async () => {
  const user = userEvent.setup(), pending = deferred<unknown>();
  render(<TrashCenterPage />); await screen.findByText("空白验收项目");
  mocks.searchProduct.mockReturnValueOnce(pending.promise);
  vi.useFakeTimers();
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "刷新列表" })); });
  await act(async () => { vi.advanceTimersByTime(10_000); });
  expect(screen.getByText("列表暂时无法更新")).toBeInTheDocument();
  expect(screen.getByText("空白验收项目")).toBeInTheDocument();
  vi.useRealTimers(); await user.click(screen.getByRole("button", { name: "重新加载回收站" }));
  await waitFor(() => expect(screen.queryByText("列表暂时无法更新")).not.toBeInTheDocument());
  await act(async () => { pending.resolve({ query: "", items: [], count: 0 }); });
  expect(screen.getByText("空白验收项目")).toBeInTheDocument();
});

it("never lets an old search response replace the current search", async () => {
  const user = userEvent.setup(), pending = deferred<unknown>();
  render(<TrashCenterPage />); await screen.findByText("空白验收项目");
  mocks.searchProduct.mockReturnValueOnce(pending.promise);
  await user.type(screen.getByRole("searchbox"), "旧");
  await waitFor(() => expect(mocks.searchProduct).toHaveBeenCalledWith("旧", expect.anything()));
  mocks.searchProduct.mockImplementation(async (query: string) => ({ query, items: query === "新" ? [{ ...trashedItems[0], title: "新的研究" }] : [], count: 1 }));
  await user.clear(screen.getByRole("searchbox")); await user.type(screen.getByRole("searchbox"), "新");
  await screen.findByText("新的研究");
  await act(async () => pending.resolve({ query: "旧", items: trashedItems, count: 2 }));
  expect(screen.queryByText("空白验收项目")).not.toBeInTheDocument();
});

it("keeps exact identity confirmation for duplicate names", async () => {
  const user = userEvent.setup();
  mocks.searchProduct.mockResolvedValueOnce({ query: "", count: 3, items: [...trashedItems, { ...trashedItems[1], id: "project-empty-2", projectId: "project-empty-2" }] });
  mocks.getProjectDependencyImpact.mockImplementation(async (id: string) => ({ entity: "project", entityId: id, canDelete: true, dependencies: [] }));
  mocks.deleteEmptyProject.mockResolvedValueOnce({ projectId: "project-empty-2", deleted: true });
  render(<TrashCenterPage />); await showProjectDetail(user, 1);
  await screen.findByRole("dialog", { name: "永久删除这项内容？" });
  expect(mocks.getProjectDependencyImpact).toHaveBeenCalledWith("project-empty-2", signal);
  const input = screen.getByRole("textbox"), confirm = screen.getByRole("button", { name: "确认永久删除" });
  await user.type(input, "project:project-empty"); expect(confirm).toBeDisabled();
  await user.type(input, "-2"); expect(confirm).toBeEnabled();
  await user.dblClick(confirm);
  await waitFor(() => expect(mocks.deleteEmptyProject).toHaveBeenCalledWith("project-empty-2", signal));
  expect(mocks.deleteEmptyProject).toHaveBeenCalledTimes(1);
  expect(screen.getAllByRole("heading", { name: "空白验收项目" })).toHaveLength(1);
});

it("keeps protected records and links to their actual dependencies", async () => {
  const user = userEvent.setup();
  mocks.getProjectDependencyImpact.mockResolvedValueOnce({ entity: "project", entityId: "project-empty", canDelete: false, dependencies: [{ kind: "result", label: "分析结果", count: 2, href: "/projects/project-empty/research" }] });
  render(<TrashCenterPage />); await showProjectDetail(user);
  await screen.findByRole("dialog", { name: "这项内容暂不能永久删除" });
  expect(screen.getByRole("link", { name: "分析结果" })).toHaveAttribute("href", "/projects/project-empty/research");
  expect(screen.queryByRole("button", { name: "确认永久删除" })).not.toBeInTheDocument();
  expect(mocks.deleteEmptyProject).not.toHaveBeenCalled();
});

it("rejects a dependency preview for another entity", async () => {
  const user = userEvent.setup();
  mocks.getProjectDependencyImpact.mockResolvedValueOnce({ entity: "project", entityId: "foreign", canDelete: true, dependencies: [] });
  render(<TrashCenterPage />); await showProjectDetail(user);
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法确认能否删除");
  expect(screen.queryByRole("button", { name: "确认永久删除" })).not.toBeInTheDocument();
});

it("contains delete failures in the open dialog and blocks an immediate repeat", async () => {
  const user = userEvent.setup(); mocks.deleteEmptyProject.mockRejectedValueOnce(new Error("socket closed"));
  render(<TrashCenterPage />); await showProjectDetail(user); await screen.findByRole("textbox");
  await user.type(screen.getByRole("textbox"), "project:project-empty");
  await user.click(screen.getByRole("button", { name: "确认永久删除" }));
  expect(await within(screen.getByRole("dialog")).findByRole("alert")).toHaveTextContent("删除结果尚未确认");
  expect(screen.getByRole("button", { name: "确认永久删除" })).toBeDisabled();
  expect(mocks.deleteEmptyProject).toHaveBeenCalledTimes(1);
  await user.keyboard("{Escape}");
  expect(screen.getByRole("heading", { name: "空白验收项目" })).toBeInTheDocument();
});

it("cancels closed dependency reads so they cannot reopen the dialog", async () => {
  const user = userEvent.setup(), pending = deferred<unknown>(); mocks.getProjectDependencyImpact.mockReturnValueOnce(pending.promise);
  render(<TrashCenterPage />); await showProjectDetail(user);
  await user.keyboard("{Escape}");
  expect(mocks.getProjectDependencyImpact.mock.calls[0][1].aborted).toBe(true);
  await act(async () => { pending.resolve({ entity: "project", entityId: "project-empty", canDelete: true, dependencies: [] }); });
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
});

it("distinguishes empty trash, missing search results and failed reads", async () => {
  const user = userEvent.setup();
  mocks.searchProduct.mockRejectedValueOnce(new Error("offline"));
  render(<TrashCenterPage />); await screen.findByText("回收站暂时无法读取");
  expect(screen.queryByText("回收站是空的")).not.toBeInTheDocument();
  mocks.searchProduct.mockImplementation(async (query: string) => ({ query, items: [], count: 0 }));
  await user.click(screen.getByRole("button", { name: "重新加载回收站" }));
  await screen.findByRole("heading", { name: "回收站是空的" });
  expect(screen.getByRole("link", { name: "查看项目" })).toHaveAttribute("href", "/projects");
  await user.type(screen.getByRole("searchbox"), "不存在");
  await screen.findByRole("heading", { name: "没有找到匹配的内容" });
  await user.click(screen.getByRole("button", { name: "清除筛选" }));
  await screen.findByRole("heading", { name: "回收站是空的" });
  expect(screen.getByRole("searchbox")).toHaveFocus();
});
