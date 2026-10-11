import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({ getAuthUser: vi.fn(), replace: vi.fn() }));
vi.mock("../../app/lib/product-api", () => ({ getAuthUser: mocks.getAuthUser }));
vi.mock("./ProductNavigation", () => ({
  useProductRouter: () => ({ replace: mocks.replace }),
  ProductLink: ({ href, children }: { href: string; children: React.ReactNode }) => <a href={href}>{children}</a>,
}));
import { RequireProductAuth } from "./ProductShell";

beforeEach(() => {
  vi.resetAllMocks();
  window.history.replaceState({}, "", "/projects/project-a/research/session-a?turn=turn-a&branchRoot=root-a#result");
  window.sessionStorage.setItem("mdi:research-composer-draft:project-a:session-a:turn-a", "尚未发送的材料分析问题");
});

it.each([new TypeError("Failed to fetch"), Object.assign(new Error("Unavailable"), { status: 503 }), new Error("登录状态读取超时")])("keeps the exact route and draft while retrying %s", async error => {
  mocks.getAuthUser.mockRejectedValueOnce(error).mockResolvedValueOnce({ id: "user-a" });
  render(<RequireProductAuth><p>当前研究内容</p></RequireProductAuth>);
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法确认登录状态");
  await waitFor(() => expect(screen.getByRole("button", { name: "重新连接" })).toHaveFocus());
  expect(mocks.replace).not.toHaveBeenCalled();
  expect(screen.queryByText("当前研究内容")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "重新连接" }));
  expect(await screen.findByText("当前研究内容")).toBeInTheDocument();
  expect(window.location.search).toBe("?turn=turn-a&branchRoot=root-a");
  expect(window.location.hash).toBe("#result");
  expect(window.sessionStorage.getItem("mdi:research-composer-draft:project-a:session-a:turn-a")).toBe("尚未发送的材料分析问题");
  expect(mocks.getAuthUser).toHaveBeenCalledTimes(2);
});

it("redirects only confirmed 401 and leaves a usable login link during navigation", async () => {
  mocks.getAuthUser.mockRejectedValueOnce(Object.assign(new Error("Expired"), { status: 401 }));
  render(<RequireProductAuth><p>受保护内容</p></RequireProductAuth>);
  const link = await screen.findByRole("link", { name: "前往登录" });
  const expected = "/?login=1&reason=session-expired&returnTo=" + encodeURIComponent("/projects/project-a/research/session-a?turn=turn-a&branchRoot=root-a#result");
  expect(link).toHaveAttribute("href", expected);
  expect(mocks.replace).toHaveBeenCalledTimes(1);
  expect(mocks.replace).toHaveBeenCalledWith(expected);
  expect(screen.queryByText("受保护内容")).not.toBeInTheDocument();
});

it("ignores a late auth failure after leaving the protected page", async () => {
  let reject!: (reason: unknown) => void;
  mocks.getAuthUser.mockReturnValueOnce(new Promise((_, fail) => { reject = fail; }));
  const mounted = render(<RequireProductAuth><p>受保护内容</p></RequireProductAuth>);
  mounted.unmount();
  await act(async () => { reject(Object.assign(new Error("Expired"), { status: 401 })); });
  expect(mocks.replace).not.toHaveBeenCalled();
});

it("checks once for nested auth gates despite router object changes", async () => {
  mocks.getAuthUser.mockResolvedValue({ id: "user-a" });
  render(<RequireProductAuth><RequireProductAuth><p>受保护内容</p></RequireProductAuth></RequireProductAuth>);
  expect(await screen.findByText("受保护内容")).toBeInTheDocument();
  expect(mocks.getAuthUser).toHaveBeenCalledTimes(1);
});
