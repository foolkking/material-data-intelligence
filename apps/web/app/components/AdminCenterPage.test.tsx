import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getAuthUser: vi.fn(),
  getPlatformAdminOverview: vi.fn(),
  listPlatformAdminUsers: vi.fn(),
  updatePlatformAdminUser: vi.fn(),
  listPlatformAdminAudit: vi.fn(),
  listPlatformAdminProjects: vi.fn(),
  listPlatformAdminProjectMembers: vi.fn(),
  updatePlatformAdminProjectMember: vi.fn(),
  removePlatformAdminProjectMember: vi.fn(),
}));
vi.mock("../lib/product-api", () => mocks);
vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: { children: React.ReactNode; href: string }) => <a href={href} {...props}>{children}</a>,
}));

import { AdminCenterPage } from "./AdminCenterPage";

const overview = {
  schemaVersion: "platform-admin-overview/1.0",
  counts: { users: 12, activeUsers: 10, platformAdmins: 2, projects: 7, activeSessions: 3 },
  operations: {
    status: "ok",
    capturedAt: "2026-09-01T08:00:00Z",
    alertSummary: { total: 0 },
    alerts: [],
    database: { staleJobs: 0 },
    queues: {
      totalQueued: 0,
      workerCount: 6,
      workerHealth: { healthyCount: 6 },
    },
  },
};
const users = {
  count: 2,
  total: 2,
  limit: 50,
  offset: 0,
  items: [
    { id: "admin_1", email: "admin@local.invalid", displayName: "平台管理员", platformRole: "PLATFORM_ADMIN", isActive: true, projectCount: 2, activeSessionCount: 1, createdAt: "2026-08-01T00:00:00Z", updatedAt: "2026-09-01T00:00:00Z" },
    { id: "user_2", email: "researcher@local.invalid", displayName: "研究成员", platformRole: "USER", isActive: true, projectCount: 1, activeSessionCount: 1, createdAt: "2026-08-01T00:00:00Z", updatedAt: "2026-09-01T00:00:00Z" },
  ],
};
const projects = {
  count: 1,
  total: 1,
  limit: 50,
  offset: 0,
  items: [{
    id: "project_1",
    name: "硅结构项目",
    description: "结构与电子分析",
    owner: { id: "admin_1", email: "admin@local.invalid", displayName: "平台管理员" },
    memberCount: 2,
    createdAt: "2026-08-01T00:00:00Z",
    updatedAt: "2026-09-01T00:00:00Z",
  }],
};

beforeEach(() => {
  vi.clearAllMocks();
  mocks.getAuthUser.mockResolvedValue({ id: "admin_1", displayName: "平台管理员", email: "admin@local.invalid", roles: [], platformRole: "PLATFORM_ADMIN" });
  mocks.getPlatformAdminOverview.mockResolvedValue(overview);
  mocks.listPlatformAdminUsers.mockResolvedValue(users);
  mocks.listPlatformAdminAudit.mockResolvedValue({ count: 1, items: [{ id: "audit_1", actor: { id: "admin_1", email: "admin@local.invalid" }, action: "platform.user.updated", targetType: "user", targetId: "user_2", metadata: {}, createdAt: "2026-09-01T08:00:00Z" }] });
  mocks.listPlatformAdminProjects.mockResolvedValue(projects);
  mocks.listPlatformAdminProjectMembers.mockResolvedValue({
    project: { id: "project_1", name: "硅结构项目", ownerId: "admin_1" },
    count: 2,
    items: [
      { userId: "admin_1", email: "admin@local.invalid", displayName: "平台管理员", role: "owner", isActive: true, createdAt: "2026-08-01T00:00:00Z" },
      { userId: "user_2", email: "researcher@local.invalid", displayName: "研究成员", role: "viewer", isActive: true, createdAt: "2026-08-01T00:00:00Z" },
    ],
  });
  mocks.updatePlatformAdminUser.mockResolvedValue({ ...users.items[1], platformRole: "PLATFORM_ADMIN" });
});

it("loads the bounded overview, user directory and audit trail for an administrator", async () => {
  render(<AdminCenterPage />);
  expect(await screen.findByRole("heading", { name: "管理中心" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "返回控制台" })).toHaveAttribute("href", "/console");
  expect(screen.getByText("12")).toBeInTheDocument();
  expect(screen.getByRole("table")).toHaveTextContent("researcher@local.invalid");
  expect(screen.getByText("更新平台账户")).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "队列、Job 与 worker" })).toBeInTheDocument();
  expect(screen.getByText("队列运行正常")).toBeInTheDocument();
});

it("maps queue, stale Job and worker alerts to the bounded runbook surface", async () => {
  mocks.getPlatformAdminOverview.mockResolvedValueOnce({
    ...overview,
    operations: {
      status: "attention",
      capturedAt: "2026-09-05T08:00:00Z",
      alertSummary: { total: 3, critical: 2, warning: 1 },
      database: { staleJobs: 2 },
      queues: {
        totalQueued: 101,
        workerCount: 4,
        workerHealth: { healthyCount: 3 },
      },
      alerts: [
        {
          code: "OPS_QUEUE_DEPTH_EXCEEDED",
          severity: "WARNING",
          component: "queues",
          observed: 101,
          threshold: 100,
          message: "Canonical queue depth exceeded the attention threshold.",
          runbook: {
            id: "OPS-RUNBOOK-QUEUE-BACKLOG",
            operatorAction: "先检查各队列积压与 worker 消费状态，再决定扩容或重试。",
          },
        },
        {
          code: "OPS_STALE_JOBS",
          severity: "CRITICAL",
          component: "database",
          observed: 2,
          threshold: 0,
          message: "Jobs exceeded the age threshold.",
          runbook: {
            id: "OPS-RUNBOOK-STALE-JOBS",
            operatorAction: "先核对 Job 年龄及其 ResearchTurn。",
          },
        },
        {
          code: "OPS_WORKER_HEALTH_DEGRADED",
          severity: "CRITICAL",
          component: "queues",
          observed: { staleHeartbeatCount: 1 },
          threshold: { staleHeartbeatCount: 0 },
          message: "Canonical workers reported a stale heartbeat.",
          runbook: {
            id: "OPS-RUNBOOK-WORKER-HEALTH",
            operatorAction: "替换进程前先检查过期心跳。",
          },
        },
      ],
    },
  });

  render(<AdminCenterPage />);

  expect(await screen.findByText("3 个告警")).toBeInTheDocument();
  const alerts = screen.getByRole("list", { name: "运行告警与处置建议" });
  expect(alerts).toHaveTextContent("队列积压超过阈值");
  expect(alerts).toHaveTextContent("发现超时未推进的 Job");
  expect(alerts).toHaveTextContent("worker 心跳或状态异常");
  expect(alerts).toHaveTextContent("OPS-RUNBOOK-QUEUE-BACKLOG");
  expect(alerts).toHaveTextContent("OPS-RUNBOOK-STALE-JOBS");
  expect(alerts).toHaveTextContent("OPS-RUNBOOK-WORKER-HEALTH");
});

it("fails closed before requesting platform data for a non-admin user", async () => {
  mocks.getAuthUser.mockResolvedValue({ id: "user_1", displayName: "研究员", email: "user@local.invalid", roles: [], platformRole: "USER" });
  render(<AdminCenterPage />);
  expect(await screen.findByRole("alert")).toHaveTextContent("无平台管理权限");
  expect(mocks.getPlatformAdminOverview).not.toHaveBeenCalled();
  expect(mocks.listPlatformAdminUsers).not.toHaveBeenCalled();
});

it("applies bounded user filters and updates another user's role", async () => {
  const user = userEvent.setup();
  render(<AdminCenterPage />);
  await screen.findByRole("heading", { name: "管理中心" });
  await user.type(screen.getByLabelText("搜索"), "researcher");
  await user.selectOptions(screen.getByLabelText("状态"), "ACTIVE");
  await user.click(screen.getAllByRole("button", { name: "应用筛选" })[0]);
  await waitFor(() => expect(mocks.listPlatformAdminUsers).toHaveBeenLastCalledWith({ query: "researcher", status: "ACTIVE", role: "ALL", limit: 50 }));
  await user.click(screen.getByRole("button", { name: "设为管理员" }));
  expect(screen.getByRole("alertdialog")).toHaveTextContent("确认授予平台管理员");
  await user.click(screen.getByRole("button", { name: "确认授予管理员权限" }));
  await waitFor(() => expect(mocks.updatePlatformAdminUser).toHaveBeenCalledWith("user_2", { platformRole: "PLATFORM_ADMIN" }));
});

it("keeps self-demotion and self-deactivation unavailable in the product UI", async () => {
  render(<AdminCenterPage />);
  await screen.findByRole("heading", { name: "管理中心" });
  const selfRow = screen.getByText("admin@local.invalid").closest("tr");
  expect(selfRow).not.toBeNull();
  expect(selfRow?.querySelectorAll("button:disabled")).toHaveLength(2);
  expect(selfRow).toHaveTextContent("当前账户");
});

it("requires an explicit confirmation before changing another account", async () => {
  const user = userEvent.setup();
  render(<AdminCenterPage />);
  await screen.findByRole("heading", { name: "管理中心" });
  await user.click(screen.getAllByRole("button", { name: "停用" })[1]);
  expect(screen.getByRole("alertdialog")).toHaveTextContent("确认停用账户");
  expect(mocks.updatePlatformAdminUser).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "取消" }));
  expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument();
});

it("renders a recovery action when the initial admin read fails", async () => {
  const user = userEvent.setup();
  mocks.getPlatformAdminOverview.mockRejectedValueOnce(new Error("offline"));
  render(<AdminCenterPage />);
  expect(await screen.findByRole("alert")).toHaveTextContent("管理中心暂时无法读取");
  mocks.getPlatformAdminOverview.mockResolvedValueOnce(overview);
  await user.click(screen.getByRole("button", { name: "重新读取" }));
  expect(await screen.findByRole("heading", { name: "管理中心" })).toBeInTheDocument();
});

it("keeps project ownership immutable while allowing bounded collaborator roles", async () => {
  const user = userEvent.setup();
  render(<AdminCenterPage />);
  await screen.findByRole("heading", { name: "管理中心" });
  await user.click(screen.getByRole("button", { name: /硅结构项目/ }));

  const ownerRole = await screen.findByRole("combobox", {
    name: "平台管理员 的项目角色",
  });
  const collaboratorRole = screen.getByRole("combobox", {
    name: "研究成员 的项目角色",
  });

  expect(ownerRole).toBeDisabled();
  expect(ownerRole).toHaveValue("owner");
  expect(Array.from(ownerRole.querySelectorAll("option")).map((item) => item.value)).toEqual([
    "owner",
    "admin",
    "researcher",
    "viewer",
  ]);
  expect(Array.from(collaboratorRole.querySelectorAll("option")).map((item) => item.value)).toEqual([
    "admin",
    "researcher",
    "viewer",
  ]);

  await user.selectOptions(collaboratorRole, "researcher");
  expect(screen.getByRole("alertdialog")).toHaveTextContent("确认更新项目角色");
  expect(screen.getByRole("alertdialog")).toHaveTextContent("研究者");
});
