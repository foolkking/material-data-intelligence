import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getAuthUser: vi.fn(),
  createPlatformInvitation: vi.fn(),
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
  mocks.updatePlatformAdminProjectMember.mockResolvedValue({ projectId: "project_1", userId: "user_2", role: "admin" });
  mocks.removePlatformAdminProjectMember.mockResolvedValue({ projectId: "project_1", userId: "user_2", removed: true });
  mocks.createPlatformInvitation.mockResolvedValue({ email: "invited@example.invalid", expiresAt: "2026-10-07T08:00:00Z", activationToken: "test-only-invitation" });
});
afterEach(() => { vi.useRealTimers(); });

function selectTab(name: string) { fireEvent.click(screen.getByRole("tab", { name })); }
async function openTab(name: string) { await screen.findByRole("tab", { name }); selectTab(name); }


it("loads the bounded overview, user directory and audit trail for an administrator", async () => {
  render(<AdminCenterPage />);
  expect(await screen.findByRole("heading", { name: "管理中心" })).toBeInTheDocument();
  expect(screen.getAllByRole("tabpanel")).toHaveLength(1);
  expect(screen.getByText("12 个账户")).toBeInTheDocument();
  expect(screen.getByRole("table")).toHaveTextContent("researcher@local.invalid");
  expect(screen.getByText("更新平台账户")).toBeInTheDocument();
  selectTab("运行状态");
  expect(screen.getByRole("heading", { name: "任务运行状态" })).toBeInTheDocument();
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

  await openTab("运行状态");
  expect(await screen.findByText("3 个告警")).toBeInTheDocument();
  const alerts = screen.getByRole("list", { name: "运行告警与处置建议" });
  expect(alerts).toHaveTextContent("等待处理的任务过多");
  expect(alerts).toHaveTextContent("有任务长时间未推进");
  expect(alerts).toHaveTextContent("执行进程状态异常");
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
  await waitFor(() => expect(mocks.listPlatformAdminUsers).toHaveBeenLastCalledWith(expect.objectContaining({ query: "researcher", status: "ACTIVE", role: "ALL", limit: 50 })));
  await user.click(screen.getByRole("button", { name: "设为管理员" }));
  expect(screen.getByRole("dialog")).toHaveTextContent("确认授予平台管理员");
  expect(screen.getByRole("button", { name: "关闭" })).toHaveFocus();
  await user.click(screen.getByRole("button", { name: "确认授予管理员权限" }));
  await waitFor(() => expect(mocks.updatePlatformAdminUser).toHaveBeenCalledWith("user_2", { platformRole: "PLATFORM_ADMIN" }, { signal: expect.any(AbortSignal) }));
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
  expect(screen.getByRole("dialog")).toHaveTextContent("确认停用账户");
  expect(mocks.updatePlatformAdminUser).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "取消" }));
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
});

it("recovers a failed overview without hiding working directories or reloading them", async () => {
  const user = userEvent.setup();
  mocks.getPlatformAdminOverview.mockRejectedValueOnce(new Error("offline"));
  render(<AdminCenterPage />);
  expect(await screen.findByRole("alert")).toHaveTextContent("平台概览暂时无法读取");
  expect(screen.getByRole("table")).toHaveTextContent("研究成员");
  selectTab("项目成员");
  expect(screen.getByRole("button", { name: /硅结构项目/ })).toBeInTheDocument();
  mocks.getPlatformAdminOverview.mockResolvedValueOnce(overview);
  await user.click(screen.getByRole("button", { name: "重新读取概览" }));
  expect(await screen.findByText("队列运行正常")).toBeInTheDocument();
  expect(mocks.listPlatformAdminUsers).toHaveBeenCalledTimes(1);
  expect(mocks.listPlatformAdminProjects).toHaveBeenCalledTimes(1);
});

it("keeps project ownership immutable while allowing bounded collaborator roles", async () => {
  const user = userEvent.setup();
  render(<AdminCenterPage />);
  await screen.findByRole("heading", { name: "管理中心" });
  await openTab("项目成员");
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
  expect(screen.getByRole("dialog")).toHaveTextContent("确认更新项目角色");
  expect(screen.getByRole("dialog")).toHaveTextContent("研究者");
});

it.each(["账户", "项目"])("recovers an initial %s directory failure without claiming it is empty", async (directory) => {
  const user = userEvent.setup();
  const request = directory === "账户" ? mocks.listPlatformAdminUsers : mocks.listPlatformAdminProjects;
  request.mockRejectedValueOnce(new Error("offline"));
  render(<AdminCenterPage />);

  await screen.findByRole("heading", { name: "管理中心" });
  if (directory === "项目") selectTab("项目成员");
  expect(screen.getByRole("alert")).toHaveTextContent(`${directory}目录暂时无法读取`);
  expect(screen.queryByText(`没有匹配${directory}`)).not.toBeInTheDocument();
  expect(mocks.listPlatformAdminAudit).toHaveBeenCalledTimes(1);
  await user.click(screen.getByRole("button", { name: `重新加载${directory}` }));
  await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
  if (directory === "账户") expect(screen.getByRole("table")).toHaveTextContent("研究成员");
  else expect(screen.getByRole("button", { name: /硅结构项目/ })).toBeInTheDocument();
});

it("retries failed user filters with their original values and keeps prior records labelled stale", async () => {
  const user = userEvent.setup();
  render(<AdminCenterPage />);
  await screen.findByRole("heading", { name: "管理中心" });
  mocks.listPlatformAdminUsers.mockRejectedValueOnce(new Error("网络中断"));
  await user.type(screen.getByLabelText("搜索", { exact: true }), "researcher");
  await user.selectOptions(screen.getByLabelText("状态"), "ACTIVE");
  await user.click(within(screen.getByRole("region", { name: "平台账户" })).getByRole("button", { name: "应用筛选" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("保留上次读取的账户");
  expect(screen.getByRole("table")).toHaveTextContent("研究成员");
  expect(screen.getByRole("button", { name: "设为管理员" })).toBeDisabled();
  await user.type(screen.getByLabelText("搜索", { exact: true }), "-unsent-edit");
  await user.click(screen.getByRole("button", { name: "重新加载账户" }));
  await waitFor(() => expect(mocks.listPlatformAdminUsers).toHaveBeenLastCalledWith(expect.objectContaining({ query: "researcher", status: "ACTIVE", role: "ALL", limit: 50 })));
  expect(screen.getByLabelText("搜索", { exact: true })).toHaveValue("researcher-unsent-edit");
  await waitFor(() => expect(screen.getByRole("button", { name: "设为管理员" })).toBeEnabled());
});

it("retains the current page and retries the failed project page without resetting pagination", async () => {
  const user = userEvent.setup();
  mocks.listPlatformAdminProjects.mockResolvedValueOnce({ ...projects, total: 2 });
  render(<AdminCenterPage />);
  await screen.findByRole("heading", { name: "管理中心" });
  mocks.listPlatformAdminProjects.mockRejectedValueOnce(new Error("网络中断"));
  await openTab("项目成员");
  await user.click(screen.getByRole("button", { name: "显示更多项目" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("保留上次读取的项目");
  selectTab("项目成员");
  expect(screen.getByRole("button", { name: /硅结构项目/ })).toBeInTheDocument();
  mocks.listPlatformAdminProjects.mockResolvedValueOnce({ ...projects, total: 2, items: [{ ...projects.items[0], id: "project_2", name: "锂扩散项目" }] });
  await user.click(screen.getByRole("button", { name: "重新加载项目" }));
  await waitFor(() => expect(mocks.listPlatformAdminProjects).toHaveBeenLastCalledWith(expect.objectContaining({ query: "", limit: 50, offset: 1 })));
  expect(await screen.findByRole("button", { name: /锂扩散项目/ })).toBeInTheDocument();
  selectTab("项目成员");
  expect(screen.getByRole("button", { name: /硅结构项目/ })).toBeInTheDocument();
});

it("distinguishes unavailable membership from an empty project and offers local retry", async () => {
  const user = userEvent.setup();
  mocks.listPlatformAdminProjectMembers.mockRejectedValueOnce(new Error("网络中断"));
  render(<AdminCenterPage />);
  await openTab("项目成员");
  await user.click(await screen.findByRole("button", { name: /硅结构项目/ }));
  expect(await screen.findByRole("alert")).toHaveTextContent("项目成员暂时无法读取");
  expect(screen.queryByText("暂无成员关系")).not.toBeInTheDocument();
  expect(screen.getByText("成员数量待确认")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重新加载成员" }));
  expect(await screen.findByRole("combobox", { name: "研究成员 的项目角色" })).toBeInTheDocument();
  expect(mocks.listPlatformAdminProjectMembers).toHaveBeenLastCalledWith("project_1", { signal: expect.any(AbortSignal) });
});

it("does not replace a newly selected project's members with a late read from another project", async () => {
  const user = userEvent.setup();
  let finishOldRequest!: (value: unknown) => void;
  mocks.listPlatformAdminProjects.mockResolvedValueOnce({ ...projects, items: [...projects.items, { ...projects.items[0], id: "project_2", name: "锂扩散项目" }] });
  mocks.listPlatformAdminProjectMembers.mockImplementationOnce(() => new Promise((resolve) => { finishOldRequest = resolve; }));
  mocks.listPlatformAdminProjectMembers.mockResolvedValueOnce({ project: { id: "project_2" }, items: [{ userId: "user_lithium", displayName: "锂研究者", email: "lithium@local.invalid", role: "researcher" }] });
  render(<AdminCenterPage />);
  await openTab("项目成员");
  await user.click(await screen.findByRole("button", { name: /硅结构项目/ }));
  expect(screen.getByText("正在读取成员…")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: /锂扩散项目/ }));
  expect(await screen.findByRole("combobox", { name: "锂研究者 的项目角色" })).toBeInTheDocument();
  await act(async () => finishOldRequest({ items: [{ userId: "old_user", displayName: "旧项目成员", role: "viewer" }] }));
  expect(screen.queryByText("旧项目成员")).not.toBeInTheDocument();
  expect(screen.getByRole("combobox", { name: "锂研究者 的项目角色" })).toBeInTheDocument();
});

it("does not apply a late role-change response to the same user in another project", async () => {
  const user = userEvent.setup();
  let finishRoleChange!: (value: unknown) => void;
  mocks.listPlatformAdminProjects.mockResolvedValueOnce({ ...projects, items: [...projects.items, { ...projects.items[0], id: "project_2", name: "锂扩散项目" }] });
  mocks.updatePlatformAdminProjectMember.mockImplementationOnce(() => new Promise((resolve) => { finishRoleChange = resolve; }));
  render(<AdminCenterPage />);
  await openTab("项目成员");
  await user.click(await screen.findByRole("button", { name: /硅结构项目/ }));
  await user.selectOptions(await screen.findByRole("combobox", { name: "研究成员 的项目角色" }), "admin");
  await user.click(screen.getByRole("button", { name: "确认更新" }));
  expect(mocks.updatePlatformAdminProjectMember).toHaveBeenCalledWith("project_1", "user_2", "admin", { signal: expect.any(AbortSignal) });
  mocks.listPlatformAdminProjectMembers.mockResolvedValueOnce({ project: { id: "project_2" }, items: [{ userId: "user_2", displayName: "研究成员", email: "researcher@local.invalid", role: "viewer" }] });
  await user.click(screen.getByRole("button", { name: /锂扩散项目/ }));
  expect(await screen.findByRole("combobox", { name: "研究成员 的项目角色" })).toHaveValue("viewer");
  await act(async () => finishRoleChange({ projectId: "project_1", userId: "user_2", role: "admin" }));
  expect(screen.getByRole("combobox", { name: "研究成员 的项目角色" })).toHaveValue("viewer");
  expect(screen.queryByText(/正在更新.*项目角色/)).not.toBeInTheDocument();
});

it("keeps working directories available while overview and audit reads stall, then rejects late responses", async () => {
  vi.useFakeTimers();
  let resolveOverview!: (value: unknown) => void;
  let resolveAudit!: (value: unknown) => void;
  mocks.getPlatformAdminOverview.mockReturnValueOnce(new Promise((resolve) => { resolveOverview = resolve; }));
  mocks.listPlatformAdminAudit.mockReturnValueOnce(new Promise((resolve) => { resolveAudit = resolve; }));
  render(<AdminCenterPage />);
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  expect(screen.getByRole("table")).toHaveTextContent("研究成员");
  selectTab("项目成员");
  expect(screen.getByRole("button", { name: /硅结构项目/ })).toBeInTheDocument();
  expect(screen.queryByText("队列运行正常")).not.toBeInTheDocument();
  expect(screen.queryByText("暂无平台变更")).not.toBeInTheDocument();
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  selectTab("变更记录");
  expect(screen.getAllByRole("alert")).toHaveLength(2);
  expect(mocks.getPlatformAdminOverview.mock.calls[0][0].signal.aborted).toBe(true);
  expect(mocks.listPlatformAdminAudit.mock.calls[0][1].signal.aborted).toBe(true);
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新读取概览" })); fireEvent.click(screen.getByRole("button", { name: "重新读取变更" })); });
  expect(screen.getByText("队列运行正常")).toBeInTheDocument();
  await act(async () => { resolveOverview({ ...overview, counts: { ...overview.counts, users: 999 } }); resolveAudit({ items: [], count: 0 }); });
  expect(screen.queryByText("999")).not.toBeInTheDocument();
  expect(screen.getByText("更新平台账户")).toBeInTheDocument();
  expect(mocks.listPlatformAdminUsers).toHaveBeenCalledTimes(1);
  expect(mocks.listPlatformAdminProjects).toHaveBeenCalledTimes(1);
});

it("preserves audit records on refresh failure without blocking the account directory", async () => {
  const user = userEvent.setup();
  render(<AdminCenterPage />);
  await openTab("变更记录");
  await screen.findByText("更新平台账户");
  mocks.listPlatformAdminAudit.mockRejectedValueOnce(new Error("offline"));
  await user.click(screen.getByRole("button", { name: "刷新变更" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("以下保留上次记录");
  expect(screen.getByText("更新平台账户")).toBeInTheDocument();
  selectTab("账户");
  expect(screen.getByRole("button", { name: "设为管理员" })).toBeEnabled();
  selectTab("变更记录");
  await user.click(screen.getByRole("button", { name: "重新读取变更" }));
  await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
});

it.each([undefined, null, "", "0", false, -1])("does not treat missing or invalid metrics (%s) as zero or healthy", async (metric) => {
  mocks.getPlatformAdminOverview.mockResolvedValue({ ...overview, operations: { ...overview.operations, queues: { ...overview.operations.queues, totalQueued: metric } } });
  render(<AdminCenterPage />);
  await screen.findByRole("table");
  expect(screen.queryByText("队列运行正常")).not.toBeInTheDocument();
  expect(screen.getByText("状态待确认")).toBeInTheDocument();
  expect(screen.getByText("排队任务").nextElementSibling).toHaveTextContent("—");
});

it("keeps a confirmed account update successful when its overview refresh fails", async () => {
  const user = userEvent.setup();
  render(<AdminCenterPage />);
  await screen.findByRole("table");
  mocks.getPlatformAdminOverview.mockRejectedValueOnce(new Error("offline"));
  await user.click(screen.getByRole("button", { name: "设为管理员" }));
  await user.click(screen.getByRole("button", { name: "确认授予管理员权限" }));
  expect(await screen.findByText("已更新 研究成员 的平台账户。")).toBeInTheDocument();
  expect(await screen.findByRole("alert")).toHaveTextContent("保留上次记录");
  expect(screen.getByText("researcher@local.invalid").closest("tr")).toHaveTextContent("平台管理员");
});

it("bounds permission checks and never requests administrative data without confirmation", async () => {
  vi.useFakeTimers();
  mocks.getAuthUser.mockReturnValueOnce(new Promise(() => {}));
  render(<AdminCenterPage />);
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("heading", { name: "管理权限暂时无法确认" })).toBeInTheDocument();
  expect(mocks.getPlatformAdminOverview).not.toHaveBeenCalled();
  expect(mocks.listPlatformAdminUsers).not.toHaveBeenCalled();
});

it("retains users through a timed-out filter and retries the original query", async () => {
  vi.useFakeTimers();
  render(<AdminCenterPage />);
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  mocks.listPlatformAdminUsers.mockReturnValueOnce(new Promise(() => {}));
  fireEvent.change(screen.getByLabelText("搜索", { exact: true }), { target: { value: "researcher" } });
  await act(async () => { fireEvent.submit(screen.getByLabelText("搜索", { exact: true }).closest("form")!); await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("alert")).toHaveTextContent("读取超时");
  expect(screen.getByRole("table")).toHaveTextContent("研究成员");
  expect(screen.getByRole("button", { name: "设为管理员" })).toBeDisabled();
  fireEvent.change(screen.getByLabelText("搜索", { exact: true }), { target: { value: "还未提交的新搜索" } });
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新加载账户" })); });
  expect(mocks.listPlatformAdminUsers).toHaveBeenLastCalledWith(expect.objectContaining({ query: "researcher" }));
  expect(screen.getByLabelText("搜索", { exact: true })).toHaveValue("还未提交的新搜索");
});

it("rejects a member response belonging to another project", async () => {
  const user = userEvent.setup();
  mocks.listPlatformAdminProjectMembers.mockResolvedValueOnce({ project: { id: "foreign_project" }, items: [{ userId: "foreign_user", displayName: "其他项目成员", role: "viewer" }] });
  render(<AdminCenterPage />);
  await openTab("项目成员");
  await user.click(await screen.findByRole("button", { name: /硅结构项目/ }));
  expect(await screen.findByRole("alert")).toHaveTextContent("成员记录与当前项目不一致");
  expect(screen.queryByText("其他项目成员")).not.toBeInTheDocument();
});

it("starts with accounts and keeps filters while navigating tabs by keyboard", async () => {
  const user = userEvent.setup();
  render(<AdminCenterPage />);
  await screen.findByRole("table");
  expect(screen.getByRole("tabpanel")).toHaveAccessibleName("账户");
  expect(screen.queryByRole("heading", { name: "任务运行状态" })).not.toBeInTheDocument();
  await user.type(screen.getByLabelText("搜索", { exact: true }), "保留筛选");
  const tab = screen.getByRole("tab", { name: "账户" });
  tab.focus();
  await user.keyboard("{ArrowRight}");
  expect(screen.getByRole("tab", { name: "项目成员" })).toHaveFocus();
  expect(screen.getByRole("tabpanel")).toHaveAccessibleName("项目成员");
  await user.keyboard("{End}");
  expect(screen.getByRole("tabpanel")).toHaveAccessibleName("变更记录");
  await user.keyboard("{Home}");
  expect(screen.getByLabelText("搜索", { exact: true })).toHaveValue("保留筛选");
  expect(mocks.listPlatformAdminUsers).toHaveBeenCalledTimes(1);
});

it("dismisses account confirmation with Escape and restores focus without a write", async () => {
  const user = userEvent.setup();
  render(<AdminCenterPage />);
  const opener = await screen.findByRole("button", { name: "设为管理员" });
  await user.click(opener);
  expect(document.body.style.overflow).toBe("hidden");
  await user.keyboard("{Escape}");
  await waitFor(() => expect(opener).toHaveFocus());
  expect(document.body.style.overflow).not.toBe("hidden");
  expect(mocks.updatePlatformAdminUser).not.toHaveBeenCalled();
});

it("retains members through refresh failure and re-enables changes after recovery", async () => {
  const user = userEvent.setup();
  render(<AdminCenterPage />);
  await openTab("项目成员");
  await user.click(screen.getByRole("button", { name: /硅结构项目/ }));
  const role = await screen.findByRole("combobox", { name: "研究成员 的项目角色" });
  mocks.listPlatformAdminProjectMembers.mockRejectedValueOnce(new Error("offline"));
  await user.click(screen.getByRole("button", { name: "刷新成员" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("保留上次读取的成员");
  expect(role).toHaveValue("viewer");
  expect(role).toBeDisabled();
  await user.click(screen.getByRole("button", { name: "重新加载成员" }));
  await waitFor(() => expect(role).toBeEnabled());
});

it("bounds account writes, rejects late success, and requires a fresh read before another change", async () => {
  vi.useFakeTimers();
  let finish!: (value: unknown) => void;
  mocks.updatePlatformAdminUser.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
  render(<AdminCenterPage />);
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  fireEvent.click(screen.getByRole("button", { name: "设为管理员" }));
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "确认授予管理员权限" })); });
  expect(screen.getByRole("button", { name: "设为管理员" })).toBeDisabled();
  expect(screen.getByText("正在更新 研究成员 的账户…")).toHaveFocus();
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByText(/等待更新超时/)).toBeInTheDocument();
  expect(mocks.updatePlatformAdminUser.mock.calls[0][2].signal.aborted).toBe(true);
  expect(screen.getByRole("button", { name: "设为管理员" })).toBeDisabled();
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新加载账户" })); });
  await act(async () => { finish({ ...users.items[1], platformRole: "PLATFORM_ADMIN" }); });
  expect(screen.getByRole("button", { name: "设为管理员" })).toBeEnabled();
  expect(screen.getByText("researcher@local.invalid").closest("tr")).toHaveTextContent("平台用户");
  expect(mocks.updatePlatformAdminUser).toHaveBeenCalledTimes(1);
});

it("rejects a role update response for another member and retains the current role", async () => {
  const user = userEvent.setup();
  mocks.updatePlatformAdminProjectMember.mockResolvedValueOnce({ projectId: "project_1", userId: "foreign_user", role: "admin" });
  render(<AdminCenterPage />);
  await openTab("项目成员");
  await user.click(screen.getByRole("button", { name: /硅结构项目/ }));
  const role = await screen.findByRole("combobox", { name: "研究成员 的项目角色" });
  await user.selectOptions(role, "admin");
  await user.click(screen.getByRole("button", { name: "确认更新" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("角色更新结果尚未确认");
  expect(role).toHaveValue("viewer");
  expect(role).toBeDisabled();
});

it("applies a confirmed removal to the exact project's members", async () => {
  const user = userEvent.setup();
  render(<AdminCenterPage />);
  await openTab("项目成员");
  await user.click(screen.getByRole("button", { name: /硅结构项目/ }));
  await user.click(await screen.findByRole("button", { name: "移除" }));
  await user.click(screen.getByRole("button", { name: "确认移除" }));
  await waitFor(() => expect(screen.queryByRole("combobox", { name: "研究成员 的项目角色" })).not.toBeInTheDocument());
  expect(mocks.removePlatformAdminProjectMember).toHaveBeenCalledWith("project_1", "user_2", { signal: expect.any(AbortSignal) });
  expect(screen.getByRole("button", { name: /硅结构项目/ })).toHaveTextContent("1 位成员");
});

it("retains an invitation draft on failure and never claims unavailable clipboard copying succeeded", async () => {
  const user = userEvent.setup();
  mocks.createPlatformInvitation.mockRejectedValueOnce(new Error("创建邀请暂时不可用"));
  render(<AdminCenterPage />);
  await user.click(await screen.findByRole("button", { name: "邀请研究者" }));
  await user.type(screen.getByLabelText("邮箱", { exact: true }), "invited@example.invalid");
  await user.type(screen.getByLabelText("姓名", { exact: true }), "受邀者");
  await user.click(screen.getByRole("button", { name: "创建邀请" }));
  expect(await screen.findByText("创建邀请暂时不可用")).toBeInTheDocument();
  expect(screen.getByLabelText("姓名", { exact: true })).toHaveValue("受邀者");
  await user.click(screen.getByRole("button", { name: "创建邀请" }));
  const clipboard = Object.getOwnPropertyDescriptor(navigator, "clipboard");
  Object.defineProperty(navigator, "clipboard", { configurable: true, value: undefined });
  try {
    await user.click(await screen.findByRole("button", { name: "复制凭证" }));
    expect(await screen.findByText(/浏览器未允许复制/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "已复制凭证" })).not.toBeInTheDocument();
  } finally { if (clipboard) Object.defineProperty(navigator, "clipboard", clipboard); }
  await user.click(screen.getByRole("button", { name: "完成" }));
  expect(screen.queryByText("test-only-invitation")).not.toBeInTheDocument();
});

it("does not deliver late invitation results into a reopened dialog", async () => {
  vi.useFakeTimers();
  let finish!: (value: unknown) => void;
  mocks.createPlatformInvitation.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
  render(<AdminCenterPage />);
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  fireEvent.click(screen.getByRole("button", { name: "邀请研究者" }));
  fireEvent.change(screen.getByLabelText("邮箱", { exact: true }), { target: { value: "invited@example.invalid" } });
  fireEvent.change(screen.getByLabelText("姓名", { exact: true }), { target: { value: "受邀者" } });
  const form = screen.getByLabelText("姓名", { exact: true }).closest("form")!;
  await act(async () => { fireEvent.submit(form); fireEvent.submit(form); });
  expect(mocks.createPlatformInvitation).toHaveBeenCalledTimes(1);
  fireEvent.keyDown(document, { key: "Escape" });
  expect(mocks.createPlatformInvitation.mock.calls[0][3].signal.aborted).toBe(true);
  fireEvent.click(screen.getByRole("button", { name: "邀请研究者" }));
  expect(screen.getByText(/邀请是否创建尚未确认/)).toBeInTheDocument();
  await act(async () => { finish({ activationToken: "late-test-token", email: "invited@example.invalid" }); });
  expect(screen.queryByText("late-test-token")).not.toBeInTheDocument();
  expect(screen.getByLabelText("姓名", { exact: true })).toHaveValue("受邀者");
});
