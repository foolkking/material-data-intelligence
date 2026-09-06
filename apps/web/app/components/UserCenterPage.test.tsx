import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

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

it("renders identity, sessions and administrator navigation", async () => {
  render(<UserCenterPage />);
  expect(screen.getByRole("status")).toHaveTextContent("正在读取账户与会话");
  expect(await screen.findByRole("heading", { name: "账户中心" })).toBeInTheDocument();
  expect(screen.getByText("项目所有者、研究成员")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "平台管理" })).toHaveAttribute("href", "/admin");
  expect(screen.getByRole("link", { name: "返回控制台" })).toHaveAttribute("href", "/console");
  expect(screen.getByText("当前会话")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "撤销会话" })).toBeInTheDocument();
});

it("updates the display name through the authoritative profile endpoint", async () => {
  const user = userEvent.setup();
  render(<UserCenterPage />);
  const input = await screen.findByLabelText("显示名称");
  await user.clear(input);
  await user.type(input, "材料研究员");
  await user.click(screen.getByRole("button", { name: "保存资料" }));
  await waitFor(() => expect(mocks.updateAuthProfile).toHaveBeenCalledWith("材料研究员"));
  expect(await screen.findByText("显示名称已更新。")).toBeInTheDocument();
});

it("revokes a non-current session without ending the current session", async () => {
  const user = userEvent.setup();
  render(<UserCenterPage />);
  await user.click(await screen.findByRole("button", { name: "撤销会话" }));
  await waitFor(() => expect(mocks.revokeAuthSession).toHaveBeenCalledWith("session_other"));
  expect(screen.queryByRole("button", { name: "撤销会话" })).not.toBeInTheDocument();
  expect(screen.getByText("当前会话")).toBeInTheDocument();
});

it("validates and changes the password without rerouting scientific work", async () => {
  const user = userEvent.setup();
  render(<UserCenterPage />);
  await screen.findByRole("heading", { name: "账户中心" });
  await user.type(screen.getByLabelText("当前密码", { selector: "#password input" }), "OldPassword-2026!");
  await user.type(screen.getByLabelText("新密码"), "NewPassword-2026!");
  await user.type(screen.getByLabelText("确认新密码"), "NewPassword-2026!");
  await user.click(screen.getByRole("button", { name: "更新密码" }));
  await waitFor(() => expect(mocks.changeAuthPassword).toHaveBeenCalledWith("OldPassword-2026!", "NewPassword-2026!"));
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
  await screen.findByRole("heading", { name: "账户中心" });
  expect(await screen.findByRole("alert")).toHaveTextContent("登录会话暂时无法读取");
  mocks.listAuthSessions.mockResolvedValueOnce({
    count: 1,
    items: [{ id: "session_current", isCurrent: true, createdAt: "2026-09-01T01:00:00Z", lastSeenAt: "2026-09-01T02:00:00Z", expiresAt: "2026-09-02T02:00:00Z" }],
  });
  await user.click(screen.getByRole("button", { name: "重新读取会话" }));
  expect(await screen.findByText("当前会话")).toBeInTheDocument();
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
  expect(await screen.findByRole("button", { name: "显示全部会话（11）" })).toBeInTheDocument();
  expect(screen.getAllByRole("button", { name: "撤销会话" })).toHaveLength(7);
  await user.click(screen.getByRole("button", { name: "显示全部会话（11）" }));
  expect(screen.getAllByRole("button", { name: "撤销会话" })).toHaveLength(10);
});
