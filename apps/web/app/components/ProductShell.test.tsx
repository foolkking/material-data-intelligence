import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getAuthUser: vi.fn(),
  listSavedProductSearches: vi.fn(),
  createSavedProductSearch: vi.fn(),
  updateSavedProductSearch: vi.fn(),
  deleteSavedProductSearch: vi.fn(),
  executeSavedProductSearch: vi.fn(),
  searchProduct: vi.fn(),
  logout: vi.fn(),
  push: vi.fn(),
  replace: vi.fn(),
  prefetch: vi.fn(),
  getProjectHistory: vi.fn(),
  listResearchSessions: vi.fn(),
  searchParams: { get: vi.fn(() => null) },
}));

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    onClick,
    prefetch: _prefetch,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
    onClick?: React.MouseEventHandler<HTMLAnchorElement>;
    prefetch?: boolean;
  }) => (
    <a
      href={href}
      {...props}
      onClick={(event) => {
        onClick?.(event);
        event.preventDefault();
      }}
    >
      {children}
    </a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/projects/project_1/research",
  useRouter: () => ({ push: mocks.push, replace: mocks.replace, prefetch: mocks.prefetch }),
  useSearchParams: () => mocks.searchParams,
}));
vi.mock("../lib/product-api", () => ({
  getAuthUser: mocks.getAuthUser,
  listSavedProductSearches: mocks.listSavedProductSearches,
  createSavedProductSearch: mocks.createSavedProductSearch,
  updateSavedProductSearch: mocks.updateSavedProductSearch,
  deleteSavedProductSearch: mocks.deleteSavedProductSearch,
  executeSavedProductSearch: mocks.executeSavedProductSearch,
  listResearchSessions: mocks.listResearchSessions,
  logout: mocks.logout,
}));
vi.mock("../lib/planner-api", () => ({
  getProjectHistory: mocks.getProjectHistory,
  searchProduct: mocks.searchProduct,
}));
vi.mock("../lib/task-center-data", () => ({
  getProductTaskFeed: vi.fn().mockResolvedValue({
    projects: [],
    rows: [],
    unavailableProjectCount: 0,
    loadedAt: "2026-08-30T00:00:00Z",
  }),
}));
vi.mock("./ModelSettingsPage", () => ({
  ModelSettingsDialog: ({ open, canManage }: { open: boolean; canManage?: boolean }) => open ? <div role="dialog" aria-label="模型服务测试替身" data-can-manage={String(Boolean(canManage))} /> : null,
}));

import {
  currentProductReturnTo,
  ProductShell,
  scheduleBoundedRoutePrefetch,
  sessionExpiredLoginHref,
} from "./ProductShell";
import { ProductNavigationProvider } from "./ProductNavigation";

beforeEach(() => {
  vi.clearAllMocks();
  mocks.getAuthUser.mockResolvedValue({ id: "user_1", displayName: "验收研究员", email: "acceptance.researcher@local.invalid", roles: ["owner"], platformRole: "USER" });
  mocks.listSavedProductSearches.mockResolvedValue([]);
  mocks.createSavedProductSearch.mockResolvedValue({
    id: "saved_new",
    name: "硅历史",
    query: "silicon",
    type: "scientific_object",
    project: "project_1",
    status: "archived",
  });
  mocks.deleteSavedProductSearch.mockResolvedValue({
    id: "saved_new",
    deleted: true,
  });
  mocks.updateSavedProductSearch.mockResolvedValue({
    id: "saved_existing",
    name: "项目内归档结构",
    query: "silicon",
    type: "scientific_object",
    project: "project_1",
    status: "archived",
  });
  mocks.executeSavedProductSearch.mockResolvedValue({
    savedSearch: {
      id: "saved_existing",
      name: "项目内归档结构",
      query: "silicon",
      type: "scientific_object",
      project: "project_1",
      status: "archived",
    },
    query: "silicon",
    count: 0,
    items: [],
  });
  mocks.searchProduct.mockResolvedValue({
    query: "",
    count: 1,
    items: [{
      kind: "project",
      id: "project_1",
      projectId: "project_1",
      title: "结构研究",
      subtitle: "RDF 与局部环境",
      href: "/projects/project_1",
      status: "active",
    }],
  });
  mocks.logout.mockResolvedValue(undefined);
  mocks.getProjectHistory.mockResolvedValue({ project: {}, datasets: [], analyses: [] });
  mocks.listResearchSessions.mockResolvedValue([]);
});

it("spaces speculative route prefetches and cancels the remaining queue", () => {
  vi.useFakeTimers();
  const target = window as Window;
  const dispose = scheduleBoundedRoutePrefetch(mocks, ["/one", "/two", "/three"], target);

  expect(mocks.prefetch).not.toHaveBeenCalled();
  vi.advanceTimersByTime(49);
  expect(mocks.prefetch).not.toHaveBeenCalled();
  vi.advanceTimersByTime(1);
  expect(mocks.prefetch).toHaveBeenCalledTimes(1);
  expect(mocks.prefetch).toHaveBeenLastCalledWith("/one");

  dispose();
  vi.advanceTimersByTime(200);
  expect(mocks.prefetch).toHaveBeenCalledTimes(1);
  vi.useRealTimers();
});

it("preserves the exact return URL and browser draft when the session expires", async () => {
  window.history.replaceState(
    {},
    "",
    "/projects/project_1/research?session=session_1&turn=turn_1#evidence-result_1",
  );
  window.sessionStorage.setItem(
    "mdi:research-composer-draft:project_1:session_1:turn_1",
    "尚未提交的晶体配位问题",
  );
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);
  await screen.findByText("研究内容");

  window.dispatchEvent(new CustomEvent("mdi:session-expired"));

  expect(mocks.replace).toHaveBeenCalledWith(
    "/?login=1&reason=session-expired&returnTo=%2Fprojects%2Fproject_1%2Fresearch%3Fsession%3Dsession_1%26turn%3Dturn_1%23evidence-result_1",
  );
  expect(
    window.sessionStorage.getItem(
      "mdi:research-composer-draft:project_1:session_1:turn_1",
    ),
  ).toBe("尚未提交的晶体配位问题");
});

it("builds browser-friendly reauthentication URLs without dropping fragments", () => {
  window.history.replaceState(
    {},
    "",
    "/projects/project_1/reports/report_1?revision=2#provenance",
  );

  expect(currentProductReturnTo()).toBe(
    "/projects/project_1/reports/report_1?revision=2#provenance",
  );
  expect(sessionExpiredLoginHref(currentProductReturnTo())).toBe(
    "/?login=1&reason=session-expired&returnTo=%2Fprojects%2Fproject_1%2Freports%2Freport_1%3Frevision%3D2%23provenance",
  );
});

it("prewarms authoritative project data without leaving the App Router shell", async () => {
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);
  const research = await screen.findByRole("link", { name: "研究" });
  fireEvent.mouseEnter(research);
  await waitFor(() => {
    expect(mocks.prefetch).toHaveBeenCalledWith("/projects/project_1/research");
    expect(mocks.getProjectHistory).toHaveBeenCalledWith("project_1");
    expect(mocks.listResearchSessions).toHaveBeenCalledWith("project_1");
  });

  fireEvent.mouseEnter(screen.getByRole("link", { name: "报告" }));
  expect(mocks.prefetch).toHaveBeenCalledWith("/projects/project_1/reports");
});

it("coalesces repeated hover and focus prefetches into one authoritative read", async () => {
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);
  const research = await screen.findByRole("link", { name: "研究" });

  fireEvent.mouseEnter(research);
  fireEvent.focus(research);
  fireEvent.mouseEnter(research);
  fireEvent.focus(research);

  await waitFor(() => expect(mocks.getProjectHistory).toHaveBeenCalledTimes(1));
  expect(mocks.listResearchSessions).toHaveBeenCalledTimes(1);

  const tasks = screen.getByRole("link", { name: "任务" });
  fireEvent.mouseEnter(tasks);
  fireEvent.focus(tasks);
  fireEvent.mouseEnter(tasks);
  await waitFor(() => expect(screen.getByRole("link", { name: "任务" })).toBeInTheDocument());
  expect(mocks.prefetch).toHaveBeenCalledWith("/tasks");
});

it("uses one shared App Router prefetch while warming domain data once", async () => {
  render(
    <ProductNavigationProvider>
      <ProductShell projectId="project_1"><div>研究内容</div></ProductShell>
    </ProductNavigationProvider>,
  );
  const research = await screen.findByRole("link", { name: "研究" });

  fireEvent.mouseEnter(research);
  fireEvent.focus(research);

  await waitFor(() => {
    expect(mocks.prefetch).toHaveBeenCalledTimes(1);
    expect(mocks.prefetch).toHaveBeenCalledWith("/projects/project_1/research");
    expect(mocks.getProjectHistory).toHaveBeenCalledTimes(1);
    expect(mocks.listResearchSessions).toHaveBeenCalledTimes(1);
  });
});

it("keeps the project frame visible and marks the requested surface while App Router navigation is pending", async () => {
  render(
    <ProductNavigationProvider>
      <ProductShell projectId="project_1"><div>研究内容</div></ProductShell>
    </ProductNavigationProvider>,
  );

  const navigation = await screen.findByRole("navigation", {
    name: "当前项目导航",
  });
  const research = screen.getByRole("link", { name: "研究" });
  const reports = screen.getByRole("link", { name: "报告" });

  expect(research).toHaveClass("active");
  fireEvent.click(reports);

  expect(navigation).toHaveAttribute("aria-busy", "true");
  expect(reports).toHaveClass("pending");
  expect(research).toHaveClass("active");
});

it("keeps global search and the account menu available on project routes", async () => {
  const user = userEvent.setup();
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  expect(await screen.findByRole("button", { name: "搜索科学工作" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "控制台" })).toHaveAttribute("href", "/console");
  const accountTrigger = await screen.findByRole("button", { name: /打开账户菜单/ });
  expect(accountTrigger).not.toHaveAttribute("aria-controls");
  expect(screen.queryByRole("link", { name: "返回主页" })).not.toBeInTheDocument();

  await user.click(accountTrigger);
  expect(accountTrigger).toHaveAttribute("aria-controls", "product-account-menu");
  expect(screen.getByRole("menu", { name: "账户菜单" })).toBeInTheDocument();
  expect(screen.getByText("acceptance.researcher@local.invalid")).toBeInTheDocument();
  expect(screen.getByRole("menuitem", { name: "账户中心" })).toHaveFocus();
  expect(screen.getByRole("menuitem", { name: "账户中心" })).toHaveAttribute("href", "/account");
  expect(screen.getByRole("menuitem", { name: "回收站" })).toHaveAttribute("href", "/trash");

  await user.keyboard("{ArrowDown}");
  expect(screen.getByRole("menuitem", { name: "回收站" })).toHaveFocus();
  await user.keyboard("{ArrowDown}");
  expect(screen.getByRole("menuitem", { name: "模型设置" })).toHaveFocus();
  await user.keyboard("{Escape}");
  expect(screen.queryByRole("menu", { name: "账户菜单" })).not.toBeInTheDocument();
  expect(accountTrigger).not.toHaveAttribute("aria-controls");
  await waitFor(() => expect(accountTrigger).toHaveFocus());
});

it("keeps the product brand as a stable Console exit from deep product routes", async () => {
  render(<ProductShell><div>任务内容</div></ProductShell>);

  const brand = await screen.findByRole("link", { name: "材料智能平台控制台" });
  expect(brand).toHaveAttribute("href", "/console");
});

it("opens project search from an internal route and restores focus after outside close", async () => {
  const user = userEvent.setup();
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  const searchTrigger = await screen.findByRole("button", { name: "搜索科学工作" });
  await user.click(searchTrigger);
  const searchInput = await screen.findByLabelText("项目、数据、研究或报告");
  await waitFor(() => expect(searchInput).toHaveFocus());
  const dialog = screen.getByRole("dialog", { name: "查找科学工作" });
  expect(within(dialog).getByText(/不会在空白条件下加载全部历史记录/)).toBeInTheDocument();
  expect(within(dialog).queryByRole("link", { name: "打开" })).not.toBeInTheDocument();
  expect(mocks.searchProduct).not.toHaveBeenCalled();
  fireEvent.mouseDown(dialog.parentElement!);
  expect(screen.queryByRole("dialog", { name: "查找项目" })).not.toBeInTheDocument();
  await waitFor(() => expect(searchTrigger).toHaveFocus());
});

it("supports the keyboard search shortcut and clears a query without losing focus", async () => {
  const user = userEvent.setup();
  mocks.searchProduct.mockResolvedValue({
    query: "band", count: 3, items: [{
      kind: "result", id: "result_1", projectId: "project_1", title: "Band Result",
      subtitle: "2.1", href: "/projects/project_1/research?result=result_1", status: "CURRENT",
    }],
  });
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);
  await screen.findByRole("button", { name: "搜索科学工作" });
  await user.keyboard("{Control>}k{/Control}");
  const input = await screen.findByLabelText("项目、数据、研究或报告");
  await user.type(input, "band");
  expect(await screen.findByRole("status", { name: "找到 3 项，显示前 1 项" })).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "清除搜索" }));
  expect(input).toHaveValue("");
  expect(input).toHaveFocus();
});

it("opens model settings from the compact account menu", async () => {
  const user = userEvent.setup();
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  await user.click(await screen.findByRole("button", { name: /打开账户菜单/ }));
  await user.click(screen.getByRole("menuitem", { name: "模型设置" }));
  expect(screen.queryByRole("menu", { name: "账户菜单" })).not.toBeInTheDocument();
  expect(screen.getByRole("dialog", { name: "模型服务测试替身" })).toHaveAttribute("data-can-manage", "false");
});

it("passes platform administration authority to model settings", async () => {
  const user = userEvent.setup();
  mocks.getAuthUser.mockResolvedValue({
    id: "admin_1",
    displayName: "平台管理员",
    email: "admin@local.invalid",
    roles: [],
    platformRole: "PLATFORM_ADMIN",
  });
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  await user.click(await screen.findByRole("button", { name: /打开账户菜单/ }));
  expect(screen.getByRole("menuitem", { name: "平台管理" })).toHaveAttribute("href", "/admin");
  await user.click(screen.getByRole("menuitem", { name: "模型设置" }));
  expect(screen.getByRole("dialog", { name: "模型服务测试替身" })).toHaveAttribute("data-can-manage", "true");
});

it("keeps platform management hidden from ordinary users", async () => {
  const user = userEvent.setup();
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  await user.click(await screen.findByRole("button", { name: /打开账户菜单/ }));
  expect(screen.queryByRole("menuitem", { name: "平台管理" })).not.toBeInTheDocument();
});

it("keeps the current project identity visible in the mobile navigation contract", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "高温扩散研究", role: "owner" },
    datasets: [],
    analyses: [],
  });
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  const projectIdentity = await screen.findByRole("link", { name: "高温扩散研究" });
  expect(projectIdentity).toHaveAttribute("href", "/projects/project_1");
  expect(projectIdentity).toHaveAttribute("title", "高温扩散研究");
});

it("does not allow saving an unbounded blank search", async () => {
  const user = userEvent.setup();
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  await user.click(await screen.findByRole("button", { name: "搜索科学工作" }));
  expect(screen.getByRole("button", { name: "保存当前检索" })).toBeDisabled();
  expect(mocks.searchProduct).not.toHaveBeenCalled();
});

it("searches across authorized scientific work after the query changes", async () => {
  const user = userEvent.setup();
  mocks.searchProduct.mockResolvedValue({ query: "band", count: 1, items: [{
      kind: "result", id: "result_1", projectId: "project_1", title: "分析所选结构的带隙与来源",
      subtitle: "结果 result_1 · 1.0", href: "/projects/project_1/research?result=result_1", status: "CURRENT",
    }] });
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);
  await user.click(await screen.findByRole("button", { name: "搜索科学工作" }));
  const input = await screen.findByLabelText("项目、数据、研究或报告");
  await user.clear(input);
  await user.type(input, "band");
  await waitFor(() =>
    expect(mocks.searchProduct).toHaveBeenLastCalledWith(
      "band",
      expect.objectContaining({ signal: expect.any(AbortSignal) }),
    ),
  );
  expect(await screen.findByText("分析所选结构的带隙与来源")).toBeInTheDocument();
  expect(screen.getByText("科学结果 · 结果 result_1 · 1.0")).toBeInTheDocument();
  expect(screen.getByText(/科学结果与结果中的已验证发现/)).toBeInTheDocument();
  expect(document.querySelector(".product-search-status")).toHaveTextContent("当前");
  expect(screen.getByRole("link", { name: "打开" })).toHaveClass("product-primary-action");
});

it("continues an authorized search without duplicates or a hard refresh", async () => {
  const user = userEvent.setup();
  mocks.searchProduct
    .mockResolvedValueOnce({
      query: "band",
      count: 3,
      truncated: true,
      nextCursor: "cursor-page-2",
      items: [
        {
          kind: "result",
          id: "result_1",
          projectId: "project_1",
          title: "带隙结果一",
          subtitle: "结果 result_1",
          href: "/projects/project_1/research?result=result_1",
          status: "CURRENT",
        },
        {
          kind: "result",
          id: "result_2",
          projectId: "project_1",
          title: "带隙结果二",
          subtitle: "结果 result_2",
          href: "/projects/project_1/research?result=result_2",
          status: "CURRENT",
        },
      ],
    })
    .mockResolvedValueOnce({
      query: "band",
      count: 3,
      truncated: false,
      nextCursor: null,
      items: [
        {
          kind: "result",
          id: "result_2",
          projectId: "project_1",
          title: "带隙结果二",
          subtitle: "结果 result_2",
          href: "/projects/project_1/research?result=result_2",
          status: "CURRENT",
        },
        {
          kind: "result",
          id: "result_3",
          projectId: "project_1",
          title: "带隙结果三",
          subtitle: "结果 result_3",
          href: "/projects/project_1/research?result=result_3",
          status: "CURRENT",
        },
      ],
    });
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  await user.click(await screen.findByRole("button", { name: "搜索科学工作" }));
  await user.type(screen.getByLabelText("项目、数据、研究或报告"), "band");
  await user.click(await screen.findByRole("button", { name: "加载更多" }));

  await waitFor(() =>
    expect(mocks.searchProduct).toHaveBeenLastCalledWith("band", {
      cursor: "cursor-page-2",
    }),
  );
  expect(screen.getAllByText("带隙结果二")).toHaveLength(1);
  expect(screen.getByText("带隙结果三")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "加载更多" })).not.toBeInTheDocument();
});

it("surfaces a recoverable offline state without changing scientific work", async () => {
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);
  await screen.findByRole("button", { name: "搜索科学工作" });
  fireEvent(window, new Event("offline"));
  expect(screen.getByRole("status")).toHaveTextContent("连接已中断");
  fireEvent(window, new Event("online"));
  await waitFor(() => expect(screen.queryByText("连接已中断")).not.toBeInTheDocument());
});

it("supports bounded type, lifecycle and date filters for global search", async () => {
  const user = userEvent.setup();
  mocks.searchProduct.mockResolvedValue({ query: "silicon", count: 0, items: [] });
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);
  await user.click(await screen.findByRole("button", { name: "搜索科学工作" }));
  const input = await screen.findByLabelText("项目、数据、研究或报告");
  await user.clear(input);
  await user.type(input, "silicon");
  fireEvent.change(screen.getByLabelText("类型"), { target: { value: "scientific_object" } });
  fireEvent.change(screen.getByLabelText("状态"), { target: { value: "archived" } });
  fireEvent.change(screen.getByLabelText("起始日期"), { target: { value: "2026-08-01" } });
  fireEvent.change(screen.getByLabelText("结束日期"), { target: { value: "2026-08-31" } });
  await waitFor(() =>
    expect(mocks.searchProduct).toHaveBeenLastCalledWith(
      "silicon",
      expect.objectContaining({
        kind: "scientific_object",
        status: "archived",
        dateFrom: "2026-08-01",
        dateTo: "2026-08-31",
        signal: expect.any(AbortSignal),
      }),
    ),
  );
});

it("applies, saves and deletes user-owned searches without persisting results", async () => {
  const user = userEvent.setup();
  mocks.listSavedProductSearches.mockResolvedValue([
    {
      id: "saved_existing",
      name: "项目内归档结构",
      query: "silicon",
      type: "scientific_object",
      project: "project_1",
      status: "archived",
    },
  ]);
  mocks.searchProduct.mockResolvedValue({
    query: "silicon",
    count: 0,
    items: [],
  });
  vi.spyOn(window, "confirm").mockReturnValue(true);
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  await user.click(await screen.findByRole("button", { name: "搜索科学工作" }));
  const savedSelect = await screen.findByLabelText("已保存");
  await user.selectOptions(savedSelect, "saved_existing");
  await waitFor(() =>
    expect(mocks.executeSavedProductSearch).toHaveBeenCalledWith(
      "saved_existing",
    ),
  );
  expect(screen.getByLabelText("范围")).toHaveValue("project_1");

  await user.click(screen.getByRole("button", { name: "更新" }));
  await waitFor(() =>
    expect(mocks.updateSavedProductSearch).toHaveBeenCalledWith(
      "saved_existing",
      {
        query: "silicon",
        type: "scientific_object",
        project: "project_1",
        status: "archived",
      },
    ),
  );

  await user.click(screen.getByRole("button", { name: "保存当前检索" }));
  const nameInput = screen.getByLabelText("检索名称");
  await user.clear(nameInput);
  await user.type(nameInput, "硅历史");
  await user.click(screen.getByRole("button", { name: "保存" }));
  await waitFor(() =>
    expect(mocks.createSavedProductSearch).toHaveBeenCalledWith({
      name: "硅历史",
      query: "silicon",
      type: "scientific_object",
      project: "project_1",
      status: "archived",
    }),
  );
  expect(mocks.createSavedProductSearch.mock.calls[0]?.[0]).not.toHaveProperty(
    "items",
  );

  await user.click(screen.getByRole("button", { name: "删除" }));
  await waitFor(() =>
    expect(mocks.deleteSavedProductSearch).toHaveBeenCalledWith("saved_new"),
  );
});

it("keeps a late search response from replacing the newer query", async () => {
  const user = userEvent.setup();
  type SearchResponse = {
    query: string;
    count: number;
    items: Array<{
      kind: "result";
      id: string;
      projectId: string;
      title: string;
      subtitle: string;
      href: string;
      status: string;
    }>;
  };
  const pending = new Map<string, (value: SearchResponse) => void>();
  const searchSignals = new Map<string, AbortSignal>();
  mocks.searchProduct.mockImplementation(
    (query: string, options?: { signal?: AbortSignal }) =>
      new Promise<SearchResponse>((resolve) => {
        if (options?.signal) searchSignals.set(query, options.signal);
        pending.set(query, resolve);
      }),
  );
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);
  await user.click(await screen.findByRole("button", { name: "搜索科学工作" }));
  const input = await screen.findByLabelText("项目、数据、研究或报告");
  await user.clear(input);
  await user.type(input, "old");
  await new Promise((resolve) => window.setTimeout(resolve, 220));
  await user.clear(input);
  await user.type(input, "new");
  await new Promise((resolve) => window.setTimeout(resolve, 220));
  expect(searchSignals.get("old")?.aborted).toBe(true);
  expect(searchSignals.get("new")?.aborted).toBe(false);
  pending.get("new")?.({
    query: "new",
    count: 1,
    items: [{ kind: "result", id: "new-result", projectId: "project_1", title: "新结果", subtitle: "1.0", href: "/projects/project_1/research?result=new-result", status: "CURRENT" }],
  });
  await waitFor(() => expect(screen.getByText("新结果")).toBeInTheDocument());
  pending.get("old")?.({
    query: "old",
    count: 1,
    items: [{ kind: "result", id: "old-result", projectId: "project_1", title: "旧结果", subtitle: "1.0", href: "/projects/project_1/research?result=old-result", status: "CURRENT" }],
  });
  await new Promise((resolve) => window.setTimeout(resolve, 30));
  expect(screen.queryByText("旧结果")).not.toBeInTheDocument();
});

it("retries a failed search in place without clearing the current criteria", async () => {
  const user = userEvent.setup();
  mocks.searchProduct
    .mockRejectedValueOnce(new Error("temporary search failure"))
    .mockResolvedValueOnce({
      query: "silicon",
      count: 1,
      items: [{
        kind: "scientific_object",
        id: "object_1",
        projectId: "project_1",
        title: "Silicon structure",
        subtitle: "structure.crystal",
        href: "/projects/project_1/data?object=object_1",
        status: "active",
      }],
    });
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  await user.click(await screen.findByRole("button", { name: "搜索科学工作" }));
  const input = screen.getByLabelText("项目、数据、研究或报告");
  await user.type(input, "silicon");
  expect(await screen.findByRole("alert")).toHaveTextContent("当前条件已保留");
  expect(input).toHaveValue("silicon");

  await user.click(screen.getByRole("button", { name: "重试搜索" }));
  expect(await screen.findByText("Silicon structure")).toBeInTheDocument();
  expect(input).toHaveValue("silicon");
  expect(mocks.searchProduct).toHaveBeenCalledTimes(2);
});

it("retries loading saved searches without closing the global search", async () => {
  const user = userEvent.setup();
  mocks.listSavedProductSearches
    .mockRejectedValueOnce(new Error("temporary saved-search failure"))
    .mockResolvedValueOnce([{
      id: "saved_retry",
      name: "恢复后的检索",
      query: "silicon",
      type: "scientific_object",
      project: "project_1",
      status: "active",
    }]);
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  await user.click(await screen.findByRole("button", { name: "搜索科学工作" }));
  expect(await screen.findByText("已保存检索暂时无法读取。")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重试读取已保存检索" }));

  expect(await screen.findByRole("option", { name: "恢复后的检索" })).toBeInTheDocument();
  expect(screen.getByRole("dialog", { name: "查找科学工作" })).toBeInTheDocument();
  expect(mocks.listSavedProductSearches).toHaveBeenCalledTimes(2);
});
