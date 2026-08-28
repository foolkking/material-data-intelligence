import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getAuthUser: vi.fn(),
  searchProduct: vi.fn(),
  logout: vi.fn(),
  push: vi.fn(),
  replace: vi.fn(),
  searchParams: { get: vi.fn(() => null) },
}));

vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: { children: React.ReactNode; href: string }) => <a href={href} {...props}>{children}</a>,
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/projects/project_1/research",
  useRouter: () => ({ push: mocks.push, replace: mocks.replace }),
  useSearchParams: () => mocks.searchParams,
}));
vi.mock("../lib/product-api", () => ({
  getAuthUser: mocks.getAuthUser,
  logout: mocks.logout,
}));
vi.mock("../lib/planner-api", () => ({
  searchProduct: mocks.searchProduct,
}));
vi.mock("./ModelSettingsPage", () => ({
  ModelSettingsDialog: ({ open }: { open: boolean }) => open ? <div role="dialog" aria-label="模型服务测试替身" /> : null,
}));

import { ProductShell } from "./ProductShell";

beforeEach(() => {
  vi.clearAllMocks();
  mocks.getAuthUser.mockResolvedValue({ id: "user_1", displayName: "验收研究员", email: "acceptance.researcher@local.invalid" });
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
});

it("keeps global search and the account menu available on project routes", async () => {
  const user = userEvent.setup();
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  expect(await screen.findByRole("button", { name: "搜索项目" })).toBeInTheDocument();
  const accountTrigger = await screen.findByRole("button", { name: /打开账户菜单/ });
  expect(screen.queryByRole("link", { name: "返回主页" })).not.toBeInTheDocument();

  await user.click(accountTrigger);
  expect(screen.getByRole("menu", { name: "账户菜单" })).toBeInTheDocument();
  expect(screen.getByText("acceptance.researcher@local.invalid")).toBeInTheDocument();
  expect(screen.getByRole("menuitem", { name: "模型设置" })).toHaveFocus();

  await user.keyboard("{ArrowDown}");
  expect(screen.getByRole("menuitem", { name: "退出登录" })).toHaveFocus();
  await user.keyboard("{Escape}");
  expect(screen.queryByRole("menu", { name: "账户菜单" })).not.toBeInTheDocument();
  await waitFor(() => expect(accountTrigger).toHaveFocus());
});

it("opens project search from an internal route and restores focus after outside close", async () => {
  const user = userEvent.setup();
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  const searchTrigger = await screen.findByRole("button", { name: "搜索项目" });
  await user.click(searchTrigger);
  const searchInput = await screen.findByLabelText("项目、数据、研究或报告");
  await waitFor(() => expect(searchInput).toHaveFocus());
  const dialog = screen.getByRole("dialog", { name: "查找科学工作" });
  expect(await within(dialog).findByRole("link", { name: "打开" })).toHaveAttribute("href", "/projects/project_1");
  fireEvent.mouseDown(dialog.parentElement!);
  expect(screen.queryByRole("dialog", { name: "查找项目" })).not.toBeInTheDocument();
  await waitFor(() => expect(searchTrigger).toHaveFocus());
});

it("opens model settings from the compact account menu", async () => {
  const user = userEvent.setup();
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);

  await user.click(await screen.findByRole("button", { name: /打开账户菜单/ }));
  await user.click(screen.getByRole("menuitem", { name: "模型设置" }));
  expect(screen.queryByRole("menu", { name: "账户菜单" })).not.toBeInTheDocument();
  expect(screen.getByRole("dialog", { name: "模型服务测试替身" })).toBeInTheDocument();
});

it("searches across authorized scientific work after the query changes", async () => {
  const user = userEvent.setup();
  mocks.searchProduct
    .mockResolvedValueOnce({ query: "", count: 1, items: [{
      kind: "project", id: "project_1", projectId: "project_1", title: "结构研究",
      subtitle: "RDF 与局部环境", href: "/projects/project_1", status: "active",
    }] })
    .mockResolvedValueOnce({ query: "band", count: 1, items: [{
      kind: "result", id: "result_1", projectId: "project_1", title: "ScientificResult result_1",
      subtitle: "1.0", href: "/projects/project_1/research?result=result_1", status: "CURRENT",
    }] });
  render(<ProductShell projectId="project_1"><div>研究内容</div></ProductShell>);
  await user.click(await screen.findByRole("button", { name: "搜索项目" }));
  const input = await screen.findByLabelText("项目、数据、研究或报告");
  await user.clear(input);
  await user.type(input, "band");
  await waitFor(() => expect(mocks.searchProduct).toHaveBeenLastCalledWith("band"));
  expect(await screen.findByText("ScientificResult result_1")).toBeInTheDocument();
  expect(screen.getByText("ScientificResult · 1.0")).toBeInTheDocument();
});
