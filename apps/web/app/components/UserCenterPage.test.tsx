import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getAuthUser: vi.fn(),
  listAuthSessions: vi.fn(),
  updateAuthProfile: vi.fn(),
  revokeAuthSession: vi.fn(),
  revokeOtherAuthSessions: vi.fn(),
  changeAuthPassword: vi.fn(),
  deactivateAuthAccount: vi.fn(),
}));
vi.mock("../lib/product-api", () => mocks);
vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: { children: React.ReactNode; href: string }) => <a href={href} {...props}>{children}</a>,
}));

import { UserCenterPage } from "./UserCenterPage";

afterEach(() => { vi.useRealTimers(); });
beforeEach(() => {
  vi.clearAllMocks();
  mocks.getAuthUser.mockResolvedValue({
    id: "user_1",
    displayName: "验收研究员",
    email: "acceptance.researcher@local.invalid",
    roles: ["owner", "researcher"],
    platformRole: "PLATFORM_ADMIN",
  });
  mocks.listAuthSessions.mockResolvedValue({
    count: 2,
    items: [
      { id: "session_current", isCurrent: true, createdAt: "2026-09-01T01:00:00Z", lastSeenAt: "2026-09-01T02:00:00Z", expiresAt: "2026-09-02T02:00:00Z" },
      { id: "session_other", isCurrent: false, createdAt: "2026-08-31T01:00:00Z", lastSeenAt: "2026-08-31T02:00:00Z", expiresAt: "2026-09-02T02:00:00Z" },
    ],
  });
  mocks.updateAuthProfile.mockResolvedValue({
    id: "user_1",
    displayName: "材料研究员",
    email: "acceptance.researcher@local.invalid",
    roles: ["owner", "researcher"],
    platformRole: "PLATFORM_ADMIN",
  });
  mocks.revokeAuthSession.mockResolvedValue({ ok: true });
  mocks.revokeOtherAuthSessions.mockResolvedValue({ ok: true, revokedCount: 1 });
  mocks.changeAuthPassword.mockResolvedValue({ ok: true, otherSessionsRevoked: 1 });
});

it("renders personal identity and sessions without platform role clutter", async () => {
  render(<UserCenterPage />);
  expect(screen.getByRole("status")).toHaveTextContent("正在读取账户");
  expect(await screen.findByRole("heading", { name: "账户设置" })).toBeInTheDocument();
  expect(screen.queryByText("项目所有者、研究成员")).not.toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "平台管理" })).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: "模型设置" })).toHaveAttribute("href", "/account?settings=models");
  expect(screen.getByText("当前浏览器与其他 1 处登录")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "退出此登录" })).not.toBeInTheDocument();
  expect(screen.queryByLabelText("当前密码")).not.toBeInTheDocument();
  expect(screen.queryByText(/provenance|认证令牌|账户生命周期/)).not.toBeInTheDocument();
});

it("updates the display name through the authoritative profile endpoint", async () => {
  const user = userEvent.setup();
  render(<UserCenterPage />);
  const input = await screen.findByLabelText("显示名称");
  await user.clear(input);
  await user.type(input, "材料研究员");
  await user.click(screen.getByRole("button", { name: "保存名称" }));
  await waitFor(() => expect(mocks.updateAuthProfile).toHaveBeenCalledWith("材料研究员", { signal: expect.any(AbortSignal) }));
  expect(await screen.findByText("显示名称已更新。")).toBeInTheDocument();
});

it("revokes a non-current session without ending the current session", async () => {
  const user = userEvent.setup();
  render(<UserCenterPage />);
  await user.click(await screen.findByRole("button", { name: "查看记录" }));
  await user.click(screen.getByRole("button", { name: "退出此登录" }));
  await waitFor(() => expect(mocks.revokeAuthSession).toHaveBeenCalledWith("session_other", { signal: expect.any(AbortSignal) }));
  expect(screen.queryByRole("button", { name: "退出此登录" })).not.toBeInTheDocument();
  expect(screen.getByText("当前浏览器", { exact: true })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "收起记录" })).toHaveFocus();
});

it("validates and changes the password without rerouting scientific work", async () => {
  const user = userEvent.setup();
  render(<UserCenterPage />);
  await screen.findByRole("heading", { name: "账户设置" });
  await user.click(screen.getByRole("button", { name: "修改密码" }));
  await user.type(screen.getByLabelText("当前密码"), "OldPassword-2026!");
  await user.type(screen.getByLabelText("新密码"), "NewPassword-2026!");
  await user.type(screen.getByLabelText("确认新密码"), "NewPassword-2026!");
  await user.click(screen.getByRole("button", { name: "更新密码" }));
  await waitFor(() => expect(mocks.changeAuthPassword).toHaveBeenCalledWith("OldPassword-2026!", "NewPassword-2026!", { signal: expect.any(AbortSignal) }));
  expect(await screen.findByText(/密码已更新/)).toBeInTheDocument();
});

it("renders a recovery state when authentication is unavailable", async () => {
  mocks.getAuthUser.mockRejectedValue(new Error("offline"));
  render(<UserCenterPage />);
  expect(await screen.findByRole("alert")).toHaveTextContent("账户信息暂时无法读取");
  expect(screen.getByRole("button", { name: "重新读取" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "返回控制台" })).toHaveAttribute("href", "/console");
});

it("offers an in-place retry when sessions are temporarily unavailable", async () => {
  const user = userEvent.setup();
  mocks.listAuthSessions.mockRejectedValueOnce(new Error("offline"));
  render(<UserCenterPage />);
  await screen.findByRole("heading", { name: "账户设置" });
  expect(await screen.findByRole("alert")).toHaveTextContent("登录记录暂时无法读取");
  const input = screen.getByLabelText("显示名称");
  await user.clear(input);
  await user.type(input, "未保存的新名称");
  mocks.listAuthSessions.mockResolvedValueOnce({
    count: 1,
    items: [{ id: "session_current", isCurrent: true, createdAt: "2026-09-01T01:00:00Z", lastSeenAt: "2026-09-01T02:00:00Z", expiresAt: "2026-09-02T02:00:00Z" }],
  });
  await user.click(screen.getByRole("button", { name: "重新读取记录" }));
  expect(await screen.findByText("仅当前浏览器已登录")).toBeInTheDocument();
  expect(input).toHaveValue("未保存的新名称");
  expect(mocks.getAuthUser).toHaveBeenCalledTimes(1);
});

it("bounds a large session list until the user explicitly expands it", async () => {
  mocks.listAuthSessions.mockResolvedValue({
    count: 11,
    items: [
      { id: "session_current", isCurrent: true, createdAt: "2026-09-01T01:00:00Z", lastSeenAt: "2026-09-01T02:00:00Z", expiresAt: "2026-09-02T02:00:00Z" },
      ...Array.from({ length: 10 }, (_, index) => ({
        id: `session_${index}`,
        isCurrent: false,
        createdAt: "2026-08-31T01:00:00Z",
        lastSeenAt: "2026-08-31T02:00:00Z",
        expiresAt: "2026-09-02T02:00:00Z",
      })),
    ],
  });
  const user = userEvent.setup();
  render(<UserCenterPage />);
  await user.click(await screen.findByRole("button", { name: "查看记录" }));
  expect(screen.getByRole("button", { name: "查看全部（11）" })).toBeInTheDocument();
  expect(screen.getAllByRole("button", { name: "退出此登录" })).toHaveLength(3);
  await user.click(screen.getByRole("button", { name: "查看全部（11）" }));
  expect(screen.getAllByRole("button", { name: "退出此登录" })).toHaveLength(10);
});

it("shows editable profile while sessions stall, and ignores a late session read after retry", async () => {
  vi.useFakeTimers();
  let resolveLate!: (value: unknown) => void;
  mocks.listAuthSessions.mockReturnValueOnce(new Promise((resolve) => { resolveLate = resolve; }));
  render(<UserCenterPage />);
  await act(async () => { await Promise.resolve(); });
  fireEvent.change(screen.getByLabelText("显示名称"), { target: { value: "仍在编辑的名称" } });
  expect(screen.getByText("正在读取登录记录…")).toBeInTheDocument();
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("alert")).toHaveTextContent("登录记录暂时无法读取");
  expect(mocks.listAuthSessions.mock.calls[0][0].signal.aborted).toBe(true);
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新读取记录" })); });
  expect(screen.getByText("当前浏览器与其他 1 处登录")).toBeInTheDocument();
  await act(async () => { resolveLate({ items: [], count: 0 }); });
  expect(screen.getByText("当前浏览器与其他 1 处登录")).toBeInTheDocument();
  expect(screen.getByLabelText("显示名称")).toHaveValue("仍在编辑的名称");
});

it("times out an account read and retries independently from sessions", async () => {
  vi.useFakeTimers();
  let resolveLate!: (value: unknown) => void;
  mocks.getAuthUser.mockReturnValueOnce(new Promise((resolve) => { resolveLate = resolve; }));
  render(<UserCenterPage />);
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("alert")).toHaveTextContent("账户信息暂时无法读取");
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新读取" })); });
  expect(screen.getByLabelText("显示名称")).toHaveValue("验收研究员");
  await act(async () => { resolveLate({ displayName: "迟到的名称" }); });
  expect(screen.getByLabelText("显示名称")).toHaveValue("验收研究员");
  expect(mocks.listAuthSessions).toHaveBeenCalledTimes(1);
});

it("keeps known sessions visible on failed refresh and disables changes until rechecked", async () => {
  const user = userEvent.setup();
  render(<UserCenterPage />);
  await user.click(await screen.findByRole("button", { name: "查看记录" }));
  mocks.listAuthSessions.mockRejectedValueOnce(new Error("offline"));
  await user.click(screen.getByRole("button", { name: "刷新记录" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("下方保留上次记录");
  expect(screen.getByRole("button", { name: "退出此登录" })).toBeDisabled();
  expect(screen.getByText("当前浏览器", { exact: true })).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重新读取记录" }));
  await waitFor(() => expect(screen.getByRole("button", { name: "退出此登录" })).toBeEnabled());
});

it("retains password fields after failure and clears them on Escape with focus return", async () => {
  const user = userEvent.setup();
  mocks.changeAuthPassword.mockRejectedValueOnce(new Error("当前密码不正确。"));
  render(<UserCenterPage />);
  const trigger = await screen.findByRole("button", { name: "修改密码" });
  await user.click(trigger);
  expect(document.documentElement.style.overflow).toBe("hidden");
  await user.type(screen.getByLabelText("当前密码"), "WrongPassword-2026!");
  await user.type(screen.getByLabelText("新密码"), "NewPassword-2026!");
  await user.type(screen.getByLabelText("确认新密码"), "NewPassword-2026!");
  await user.click(screen.getByRole("button", { name: "更新密码" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("当前密码不正确");
  expect(screen.getByLabelText("新密码")).toHaveValue("NewPassword-2026!");
  await user.keyboard("{Escape}");
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  expect(document.documentElement.style.overflow).not.toBe("hidden");
  await waitFor(() => expect(trigger).toHaveFocus());
  await user.click(trigger);
  expect(screen.getByLabelText("当前密码")).toHaveValue("");
  expect(screen.getByLabelText("新密码")).toHaveValue("");
});

it("requires complete deactivation confirmation, prevents duplicate writes and retains failed input", async () => {
  const user = userEvent.setup();
  let reject!: (reason: Error) => void;
  mocks.deactivateAuthAccount.mockReturnValueOnce(new Promise((_, fail) => { reject = fail; }));
  render(<UserCenterPage />);
  await user.click(await screen.findByRole("button", { name: "停用账户" }));
  const dialog = screen.getByRole("dialog", { name: "停用账户" });
  expect(within(dialog).getByRole("button", { name: "确认停用" })).toBeDisabled();
  await user.type(screen.getByLabelText("输入完整邮箱确认"), "acceptance.researcher@local.invalid");
  await user.type(screen.getByLabelText("当前密码"), "ExamplePassword-2026!");
  await user.click(screen.getByRole("checkbox"));
  const form = dialog.querySelector("form")!;
  fireEvent.submit(form); fireEvent.submit(form);
  await waitFor(() => expect(mocks.deactivateAuthAccount).toHaveBeenCalledTimes(1));
  expect(screen.getByRole("button", { name: "正在停用…" })).toBeDisabled();
  await act(async () => { reject(new Error("服务暂时不可用，请重试。")); });
  expect(screen.getByLabelText("当前密码")).toHaveValue("ExamplePassword-2026!");
  expect(screen.getByRole("button", { name: "确认停用" })).toBeEnabled();
  await user.click(screen.getByRole("button", { name: "保留账户" }));
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
});

it("reports an unconfirmed session exit on timeout and ignores late acknowledgements", async () => {
  vi.useFakeTimers();
  let resolveLate!: (value: unknown) => void;
  mocks.revokeAuthSession.mockReturnValueOnce(new Promise((resolve) => { resolveLate = resolve; }));
  render(<UserCenterPage />);
  await act(async () => { await Promise.resolve(); });
  fireEvent.click(screen.getByRole("button", { name: "查看记录" }));
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "退出此登录" })); });
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("alert")).toHaveTextContent("暂未确认是否退出");
  await act(async () => { resolveLate({ ok: true }); });
  expect(screen.getByRole("button", { name: "退出此登录" })).toBeEnabled();
  expect(screen.queryByText("已退出该处登录。")).not.toBeInTheDocument();
});
