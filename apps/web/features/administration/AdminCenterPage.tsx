"use client";

import { useEffect, useRef, useState } from "react";
import {
  getAuthUser,
  createPlatformInvitation,
  getPlatformAdminOverview,
  listPlatformAdminAudit,
  listPlatformAdminProjectMembers,
  listPlatformAdminProjects,
  listPlatformAdminUsers,
  removePlatformAdminProjectMember,
  updatePlatformAdminProjectMember,
  updatePlatformAdminUser,
  type AuthUser,
  type PlatformAdminAuditItem,
  type PlatformAdminOverview,
  type PlatformAdminProject,
  type PlatformAdminProjectMember,
  type PlatformAdminUser,
} from "../../app/lib/product-api";
import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { ProductModal } from "../../shared/ui/ObjectManagement";
import { useAdminReads, useAdminWrites } from "./use-admin-reads";

type FilterStatus = "ALL" | "ACTIVE" | "INACTIVE";
type FilterRole = "ALL" | "USER" | "PLATFORM_ADMIN";
type DirectoryState = "loading" | "ready" | "error";
const adminTabs = [
  { key: "users", label: "账户" },
  { key: "projects", label: "项目成员" },
  { key: "operations", label: "运行状态" },
  { key: "audit", label: "变更记录" },
] as const;
type AdminTab = typeof adminTabs[number]["key"];
type PendingUserAction = {
  user: PlatformAdminUser;
  changes: { platformRole?: "USER" | "PLATFORM_ADMIN"; isActive?: boolean };
  title: string;
  consequence: string;
  confirmLabel: string;
};
type PendingMemberAction = {
  member: PlatformAdminProjectMember;
  kind: "role" | "remove";
  role?: PlatformAdminProjectMember["role"];
};

const dateLabel = (value: string) => {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "时间未知"
    : new Intl.DateTimeFormat("zh-CN", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }).format(date);
};

const actionLabel: Record<string, string> = {
  "platform.user.updated": "更新平台账户",
  "account.profile.updated": "更新个人资料",
  "account.session.revoked": "撤销登录会话",
  "account.sessions.revoked_others": "撤销其他会话",
  "account.password.changed": "修改账户密码",
  "account.deactivated": "停用账户",
  "platform.project.member.updated": "修改项目成员角色",
  "platform.project.member.removed": "移除项目成员",
  "platform.account.invited": "邀请研究者",
};

const operationsAlertLabel: Record<string, string> = {
  OPS_QUEUE_DEPTH_EXCEEDED: "等待处理的任务过多",
  OPS_STALE_JOBS: "有任务长时间未推进",
  OPS_WORKER_COUNT_BELOW_MINIMUM: "可用执行进程不足",
  OPS_WORKER_HEALTH_DEGRADED: "执行进程状态异常",
};

const numericMetric = (value: unknown) => {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 ? value : null;
};

export function AdminCenterPage() {
  const [activeTab, setActiveTab] = useState<AdminTab>("users");
  const [inviteOpen, setInviteOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [overview, setOverview] = useState<PlatformAdminOverview | null>(null);
  const [overviewState, setOverviewState] = useState<DirectoryState>("loading");
  const [auditState, setAuditState] = useState<DirectoryState>("loading");
  const overviewRequest = useRef(0);
  const auditRequest = useRef(0);
  const read = useAdminReads();
  const { run: write, cancel: cancelWrite } = useAdminWrites();
  const changeBusy = useRef(false);
  const invitationBusy = useRef(false);
  const invitationGeneration = useRef(0);
  const [users, setUsers] = useState<PlatformAdminUser[]>([]);
  const [audit, setAudit] = useState<PlatformAdminAuditItem[]>([]);
  const [projects, setProjects] = useState<PlatformAdminProject[]>([]);
  const [projectQuery, setProjectQuery] = useState("");
  const [selectedProject, setSelectedProject] = useState<PlatformAdminProject | null>(null);
  const [members, setMembers] = useState<PlatformAdminProjectMember[]>([]);
  const [membersState, setMembersState] = useState<DirectoryState>("ready");
  const [membersError, setMembersError] = useState("");
  const memberRequest = useRef(0);
  const [usersState, setUsersState] = useState<DirectoryState>("loading");
  const usersRequestGeneration = useRef(0);
  const [usersError, setUsersError] = useState("");
  const [usersRequest, setUsersRequest] = useState({ query: "", status: "ALL" as FilterStatus, role: "ALL" as FilterRole, append: false });
  const [projectsState, setProjectsState] = useState<DirectoryState>("loading");
  const projectsRequestGeneration = useRef(0);
  const [projectsError, setProjectsError] = useState("");
  const [projectsRequest, setProjectsRequest] = useState({ query: "", append: false });
  const [total, setTotal] = useState(0);
  const [projectTotal, setProjectTotal] = useState(0);
  const [userHasMore, setUserHasMore] = useState(false);
  const [projectHasMore, setProjectHasMore] = useState(false);
  const [state, setState] = useState<"loading" | "ready" | "forbidden" | "error">("loading");
  const [loadRetryToken, setLoadRetryToken] = useState(0);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<FilterStatus>("ALL");
  const [role, setRole] = useState<FilterRole>("ALL");
  const [busyUserId, setBusyUserId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState("");
  const feedbackRef = useRef<HTMLParagraphElement>(null);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteDisplayName, setInviteDisplayName] = useState("");
  const [inviteBusy, setInviteBusy] = useState(false);
  const [inviteResult, setInviteResult] = useState<{ email: string; expiresAt: string; activationToken: string } | null>(null);
  const [inviteCopied, setInviteCopied] = useState(false);
  const [inviteFeedback, setInviteFeedback] = useState("");
  const [pendingUserAction, setPendingUserAction] = useState<PendingUserAction | null>(null);
  const [pendingMemberAction, setPendingMemberAction] = useState<PendingMemberAction | null>(null);
  const modalOpen = inviteOpen || Boolean(pendingUserAction || pendingMemberAction);
  useEffect(() => {
    if (busyUserId) feedbackRef.current?.focus();
  }, [busyUserId]);
  useEffect(() => {
    if (!modalOpen) return;
    const bodyOverflow = document.body.style.overflow;
    const rootOverflow = document.documentElement.style.overflow;
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = bodyOverflow;
      document.documentElement.style.overflow = rootOverflow;
    };
  }, [modalOpen]);

  async function loadOverview() {
    const requestId = ++overviewRequest.current;
    setOverviewState("loading");
    try {
      const result = await read("overview", (signal) => getPlatformAdminOverview({ signal }));
      if (requestId !== overviewRequest.current) return;
      setOverview(result);
      setOverviewState("ready");
    } catch {
      if (requestId === overviewRequest.current) setOverviewState("error");
    }
  }

  async function loadAudit() {
    const requestId = ++auditRequest.current;
    setAuditState("loading");
    try {
      const result = await read("audit", (signal) => listPlatformAdminAudit(30, { signal }));
      if (requestId !== auditRequest.current) return;
      setAudit(result.items);
      setAuditState("ready");
    } catch {
      if (requestId === auditRequest.current) setAuditState("error");
    }
  }

  async function loadUsers(
    nextQuery = query,
    nextStatus = status,
    nextRole = role,
    append = false,
  ) {
    const requestId = ++usersRequestGeneration.current;
    setUsersState("loading");
    setUsersError("");
    setUsersRequest({ query: nextQuery, status: nextStatus, role: nextRole, append });
    try {
      const offset = append ? users.length : 0;
      const result = await read("users", (signal) => listPlatformAdminUsers({
        signal,
        query: nextQuery,
        status: nextStatus,
        role: nextRole,
        limit: 50,
        ...(offset ? { offset } : {}),
      }));
      if (requestId !== usersRequestGeneration.current) return;
      setUsers((items) => append ? [...items, ...result.items] : result.items);
      setTotal(result.total);
      setUserHasMore(offset + result.items.length < result.total);
      setUsersState("ready");
    } catch (reason) {
      if (requestId !== usersRequestGeneration.current) return;
      setUsersError(reason instanceof Error ? reason.message : "请稍后重试。");
      setUsersState("error");
    }
  }

  useEffect(() => {
    let active = true;
    setState("loading");
    void read("auth", (signal) => getAuthUser({ signal }))
      .then((user) => {
        if (!active) return;
        setCurrentUser(user);
        if (user.platformRole !== "PLATFORM_ADMIN") {
          setState("forbidden");
          return;
        }
        setState("ready");
        void loadOverview();
        void loadUsers("", "ALL", "ALL");
        void loadAudit();
        void loadProjects("");
      })
      .catch(() => {
        if (active) setState("error");
      });
    return () => {
      active = false;
      memberRequest.current += 1;
      overviewRequest.current += 1;
      auditRequest.current += 1;
      usersRequestGeneration.current += 1;
      projectsRequestGeneration.current += 1;
    };
  }, [loadRetryToken, read]);

  async function updateUser(
    user: PlatformAdminUser,
    changes: { platformRole?: "USER" | "PLATFORM_ADMIN"; isActive?: boolean },
  ) {
    if (changeBusy.current) return;
    changeBusy.current = true;
    setBusyUserId(user.id);
    setFeedback(`正在更新 ${user.displayName} 的账户…`);
    try {
      const updated = await write("user", (signal) => updatePlatformAdminUser(user.id, changes, { signal }), "等待更新超时，结果尚未确认。请重新加载账户后核对。");
      if (updated.id !== user.id) throw new Error("返回的账户与目标不一致，请重新加载账户后核对。");
      setUsers((items) => items.map((item) => item.id === updated.id ? updated : item));
      setFeedback(`已更新 ${updated.displayName} 的平台账户。`);
      void loadOverview();
      void loadAudit();
    } catch (reason) {
      setFeedback(reason instanceof Error ? reason.message : "账户更新失败。");
      usersRequestGeneration.current += 1;
      setUsersState("error");
      setUsersError("更新结果尚未确认，请重新加载账户后核对。");
    } finally {
      changeBusy.current = false;
      setBusyUserId(null);
    }
  }

  async function createInvitation(event: React.FormEvent) {
    event.preventDefault();
    if (invitationBusy.current || !inviteEmail.trim() || !inviteDisplayName.trim()) return;
    invitationBusy.current = true;
    const generation = ++invitationGeneration.current;
    setInviteBusy(true);
    setInviteResult(null);
    setInviteFeedback("");
    try {
      const result = await write("invitation", (signal) => createPlatformInvitation(inviteEmail.trim(), inviteDisplayName.trim(), 7, { signal }), "创建邀请超时，尚未取得凭证。重新创建会使此前未使用的凭证失效。");
      if (generation !== invitationGeneration.current) return;
      if (result.email.toLowerCase() !== inviteEmail.trim().toLowerCase() || !result.activationToken?.trim() || Number.isNaN(new Date(result.expiresAt).getTime())) throw new Error("邀请结果不完整，请核对受邀账户后再试。");
      setInviteResult(result);
      setInviteCopied(false);
      setInviteEmail("");
      setInviteDisplayName("");
      setInviteFeedback("邀请已创建。关闭后无法再次查看此凭证。");
    } catch (reason) {
      if (generation !== invitationGeneration.current) return;
      setInviteFeedback(reason instanceof Error ? reason.message : "创建邀请失败。");
    } finally {
      if (generation === invitationGeneration.current) {
        invitationBusy.current = false;
        setInviteBusy(false);
      }
    }
  }

  async function loadProjects(nextQuery = projectQuery, append = false) {
    const requestId = ++projectsRequestGeneration.current;
    setProjectsState("loading");
    setProjectsError("");
    setProjectsRequest({ query: nextQuery, append });
    try {
      const offset = append ? projects.length : 0;
      const result = await read("projects", (signal) => listPlatformAdminProjects({ query: nextQuery, limit: 50, ...(offset ? { offset } : {}), signal }));
      if (requestId !== projectsRequestGeneration.current) return;
      setProjects((items) => append ? [...items, ...result.items] : result.items);
      setProjectTotal(result.total);
      setProjectHasMore(offset + result.items.length < result.total);
      setProjectsState("ready");
      setSelectedProject((current) => current && (
        result.items.some((item) => item.id === current.id) ||
        (append && projects.some((item) => item.id === current.id))
      )
        ? result.items.find((item) => item.id === current.id) || current
        : null);
    } catch (reason) {
      if (requestId !== projectsRequestGeneration.current) return;
      setProjectsError(reason instanceof Error ? reason.message : "请稍后重试。");
      setProjectsState("error");
    }
  }

  async function openMembers(project: PlatformAdminProject) {
    if (changeBusy.current && selectedProject?.id === project.id) return;
    const requestId = ++memberRequest.current;
    setSelectedProject(project);
    setPendingMemberAction(null);
    if (selectedProject?.id !== project.id) setMembers([]);
    setMembersState("loading");
    setMembersError("");
    try {
      const result = await read("members", (signal) => listPlatformAdminProjectMembers(project.id, { signal }));
      if (requestId !== memberRequest.current) return;
      if (result.project.id !== project.id) throw new Error("成员记录与当前项目不一致，请重新读取。");
      setMembers(result.items);
      setMembersState("ready");
    } catch (reason) {
      if (requestId !== memberRequest.current) return;
      setMembersError(reason instanceof Error ? reason.message : "请稍后重试。");
      setMembersState("error");
    }
  }

  async function updateMember(member: PlatformAdminProjectMember, role: PlatformAdminProjectMember["role"]) {
    if (!selectedProject || member.role === role || changeBusy.current) return;
    changeBusy.current = true;
    const requestId = memberRequest.current;
    setBusyUserId(`${selectedProject.id}:${member.userId}`);
    setFeedback(`正在更新 ${member.displayName} 的项目角色…`);
    try {
      const result = await write("member", (signal) => updatePlatformAdminProjectMember(selectedProject.id, member.userId, role, { signal }), "等待更新超时，结果尚未确认。请重新加载成员后核对。");
      if (result.projectId !== selectedProject.id || result.userId !== member.userId || result.role !== role) throw new Error("返回的成员与目标不一致，请重新加载成员后核对。");
      setFeedback(`已更新 ${member.displayName} 在 ${selectedProject.name} 中的角色。`);
      void loadAudit();
      if (requestId !== memberRequest.current) return;
      setMembers((items) => items.map((item) => item.userId === member.userId ? { ...item, role } : item));
    } catch (reason) {
      setFeedback(reason instanceof Error ? `${selectedProject.name}：${reason.message}` : "项目成员角色更新失败。");
      if (requestId !== memberRequest.current) return;
      setMembersState("error");
      setMembersError("角色更新结果尚未确认，请重新加载成员后核对。");
    } finally {
      changeBusy.current = false;
      setBusyUserId(null);
    }
  }

  async function removeMember(member: PlatformAdminProjectMember) {
    if (!selectedProject || member.role === "owner" || changeBusy.current) return;
    changeBusy.current = true;
    const requestId = memberRequest.current;
    setBusyUserId(`${selectedProject.id}:${member.userId}`);
    setFeedback(`正在移除 ${member.displayName} 的项目访问权限…`);
    try {
      const result = await write("member", (signal) => removePlatformAdminProjectMember(selectedProject.id, member.userId, { signal }), "等待移除超时，结果尚未确认。请重新加载成员后核对。");
      if (result.projectId !== selectedProject.id || result.userId !== member.userId || result.removed !== true) throw new Error("移除结果尚未确认，请重新加载成员后核对。");
      setProjects((items) => items.map((item) => item.id === selectedProject.id ? { ...item, memberCount: Math.max(0, item.memberCount - 1) } : item));
      setFeedback(`已移除 ${member.displayName} 对 ${selectedProject.name} 的访问权限。`);
      void loadAudit();
      if (requestId !== memberRequest.current) return;
      setMembers((items) => items.filter((item) => item.userId !== member.userId));
    } catch (reason) {
      setFeedback(reason instanceof Error ? `${selectedProject.name}：${reason.message}` : "移除项目成员失败。");
      if (requestId !== memberRequest.current) return;
      setMembersState("error");
      setMembersError("移除结果尚未确认，请重新加载成员后核对。");
    } finally {
      changeBusy.current = false;
      setBusyUserId(null);
    }
  }

  function requestUserAction(
    user: PlatformAdminUser,
    changes: PendingUserAction["changes"],
    title: string,
    consequence: string,
    confirmLabel: string,
  ) {
    setPendingUserAction({ user, changes, title, consequence, confirmLabel });
  }

  async function confirmUserAction() {
    if (!pendingUserAction) return;
    const action = pendingUserAction;
    setPendingUserAction(null);
    await updateUser(action.user, action.changes);
  }

  function requestMemberRoleChange(member: PlatformAdminProjectMember, nextRole: PlatformAdminProjectMember["role"]) {
    if (!selectedProject || member.role === nextRole) return;
    setPendingMemberAction({ member, kind: "role", role: nextRole });
  }

  function requestMemberRemoval(member: PlatformAdminProjectMember) {
    if (!selectedProject || member.role === "owner") return;
    setPendingMemberAction({ member, kind: "remove" });
  }

  async function confirmMemberAction() {
    if (!pendingMemberAction) return;
    const action = pendingMemberAction;
    setPendingMemberAction(null);
    if (action.kind === "role" && action.role) {
      await updateMember(action.member, action.role);
    } else {
      await removeMember(action.member);
    }
  }

  async function copyInvitationToken() {
    if (!inviteResult) return;
    const generation = invitationGeneration.current;
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(inviteResult.activationToken);
      if (generation !== invitationGeneration.current) return;
      setInviteCopied(true);
      setInviteFeedback("凭证已复制，请仅向受邀者提供。");
    } catch {
      if (generation !== invitationGeneration.current) return;
      setInviteCopied(false);
      setInviteFeedback("浏览器未允许复制，请手动复制页面中的一次性凭证。");
    }
  }

  function closeInvitation() {
    invitationGeneration.current += 1;
    cancelWrite("invitation");
    if (invitationBusy.current) setInviteFeedback("已停止等待，邀请是否创建尚未确认。重新创建会使此前未使用的凭证失效。");
    else setInviteFeedback("");
    invitationBusy.current = false;
    setInviteBusy(false);
    setInviteOpen(false);
    setInviteResult(null);
    setInviteCopied(false);
  }

  if (state === "loading") return <section className="document-page admin-center-page"><div className="product-loading" role="status">正在验证平台管理权限…</div></section>;
  if (state === "forbidden") return <section className="document-page admin-center-page"><div className="product-state" role="alert"><h1>无平台管理权限</h1><p>平台用户可以管理自己的账户与项目，但不能读取全局用户或运行状态。</p><div className="product-row-actions admin-forbidden-actions"><Link className="product-primary-action" href="/console">返回控制台</Link><Link className="product-secondary-action" href="/account">账户中心</Link></div></div></section>;
  if (state === "error" || !currentUser) return <section className="document-page admin-center-page"><div className="product-state" role="alert"><h1>管理权限暂时无法确认</h1><p>请重新读取账户信息后继续。</p><div className="product-row-actions"><button className="product-primary-action" type="button" onClick={() => setLoadRetryToken((value) => value + 1)}>重新读取</button><Link className="product-secondary-action" href="/account">返回账户中心</Link></div></div></section>;

  const operationStatus = String(overview?.operations.status || "unknown").toLowerCase();
  const operationsAlerts = overview?.operations.alerts || [];
  const databaseOperations = overview?.operations.database || {};
  const queueOperations = overview?.operations.queues || {};
  const workerHealth = (
    typeof queueOperations.workerHealth === "object" &&
    queueOperations.workerHealth !== null
      ? queueOperations.workerHealth
      : {}
  ) as Record<string, unknown>;
  const completeOperations = [queueOperations.totalQueued, queueOperations.workerCount, workerHealth.healthyCount, databaseOperations.staleJobs].every((value) => numericMetric(value) !== null) && Array.isArray(overview?.operations.alerts);
  const healthy = overviewState === "ready" && completeOperations && !operationsAlerts.length && ["ok", "healthy"].includes(operationStatus);
  const healthLabel = overviewState !== "ready" || !completeOperations ? "状态待确认" : healthy ? "服务正常" : "需要检查";
  return <section className="document-page admin-center-page">
    <header className="product-page-heading admin-center-heading"><div><h1>管理中心</h1><p>管理账户、项目权限与平台运行。</p></div></header>
    <div className="admin-summary">
      <p><span className={`admin-health-marker status-${healthy ? "healthy" : healthLabel === "状态待确认" ? "unknown" : "attention"}`}>{healthLabel}</span>{numericMetric(overview?.counts.users) !== null ? <span>{overview?.counts.users} 个账户</span> : null}{numericMetric(overview?.counts.projects) !== null ? <span>{overview?.counts.projects} 个项目</span> : null}</p>
      <button className="product-secondary-action" type="button" disabled={overviewState === "loading"} onClick={() => void loadOverview()}>{overviewState === "error" ? "重新读取概览" : "刷新概览"}</button>
    </div>
    {overviewState === "loading" ? <p className="admin-read-feedback" role="status">正在读取平台概览…</p> : overviewState === "error" ? <p className="admin-read-feedback" role="alert">平台概览暂时无法读取。{overview ? "保留上次记录，当前状态尚未确认。" : "账户和项目目录仍可使用。"}</p> : null}
    <div className="task-center-filters admin-tabs" role="tablist" aria-label="管理内容">{adminTabs.map((tab, index) => <button key={tab.key} id={`admin-tab-${tab.key}`} role="tab" type="button" aria-selected={activeTab === tab.key} aria-controls={`admin-panel-${tab.key}`} tabIndex={activeTab === tab.key ? 0 : -1} onClick={() => setActiveTab(tab.key)} onKeyDown={(event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === "Home" ? 0 : event.key === "End" ? adminTabs.length - 1 : (index + (event.key === "ArrowRight" ? 1 : -1) + adminTabs.length) % adminTabs.length;
      setActiveTab(adminTabs[next].key);
      document.getElementById(`admin-tab-${adminTabs[next].key}`)?.focus();
    }}>{tab.label}</button>)}</div>
    {feedback ? <p ref={feedbackRef} tabIndex={-1} className="admin-feedback" role="status">{feedback}</p> : null}
    <div id="admin-panel-users" role="tabpanel" aria-labelledby="admin-tab-users" tabIndex={0} hidden={activeTab !== "users"}>
<section className="admin-section" aria-labelledby="admin-users-title">
      <header><div><h2 id="admin-users-title">平台账户</h2></div><span>{usersState === "ready" ? `${total} 个账户` : "账户数量待确认"}</span><button className="product-primary-action" type="button" onClick={() => setInviteOpen(true)}>邀请研究者</button></header>
      <form className="admin-filter-bar" onSubmit={(event) => { event.preventDefault(); if (!changeBusy.current) void loadUsers(); }}>
        <label>搜索<input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="姓名、邮箱或账户标识" /></label>
        <label>状态<select value={status} onChange={(event) => setStatus(event.target.value as FilterStatus)}><option value="ALL">全部</option><option value="ACTIVE">有效</option><option value="INACTIVE">已停用</option></select></label>
        <label>平台角色<select value={role} onChange={(event) => setRole(event.target.value as FilterRole)}><option value="ALL">全部</option><option value="USER">平台用户</option><option value="PLATFORM_ADMIN">平台管理员</option></select></label>
        <button className="product-secondary-action" type="submit" disabled={usersState === "loading" || busyUserId !== null}>{usersState === "loading" ? "正在筛选…" : "应用筛选"}</button>
      </form>
      {usersState === "loading" ? <p role="status">正在读取账户…</p> : null}
      {usersState === "error" ? <div className="product-state" role="alert"><strong>账户目录暂时无法读取</strong><p>{usersError}</p>{users.length ? <p>以下保留上次读取的账户，重新加载后可继续操作。</p> : null}<button className="product-secondary-action" type="button" onClick={() => void loadUsers(usersRequest.query, usersRequest.status, usersRequest.role, usersRequest.append)}>重新加载账户</button></div> : null}
      {users.length ? <div className="admin-user-table-scroll"><table className="admin-user-table"><thead><tr><th scope="col">账户</th><th scope="col">角色</th><th scope="col">项目</th><th scope="col">状态</th><th scope="col">操作</th></tr></thead><tbody>{users.map((user) => {
        const isSelf = user.id === currentUser.id;
        const busy = busyUserId !== null || usersState !== "ready";
        return <tr key={user.id}><th scope="row"><strong>{user.displayName}</strong><span>{user.email}</span></th><td data-label="角色">{user.platformRole === "PLATFORM_ADMIN" ? "平台管理员" : "平台用户"}</td><td data-label="项目">{user.projectCount}</td><td data-label="状态"><span className={user.isActive ? "admin-account-status active" : "admin-account-status inactive"}>{user.isActive ? "有效" : "已停用"}</span></td><td className="admin-actions-cell"><div className="admin-user-actions"><button className="product-link-button" type="button" disabled={busy || isSelf} onClick={() => requestUserAction(user, { platformRole: user.platformRole === "PLATFORM_ADMIN" ? "USER" : "PLATFORM_ADMIN" }, user.platformRole === "PLATFORM_ADMIN" ? "确认降为平台用户？" : "确认授予平台管理员？", "管理员可以管理平台所有账户、项目成员和运行状态。请确认该用户需要这些权限。", user.platformRole === "PLATFORM_ADMIN" ? "确认降权" : "确认授予管理员权限")}>{user.platformRole === "PLATFORM_ADMIN" ? "设为普通用户" : "设为管理员"}</button><button className="product-link-button" type="button" disabled={busy || isSelf} onClick={() => requestUserAction(user, { isActive: !user.isActive }, user.isActive ? "确认停用账户？" : "确认启用账户？", user.isActive ? "停用后，该用户会退出所有登录，无法再次登录。已有研究数据和来源记录仍会保留。" : "启用后该账户可以重新登录；项目成员关系与历史科学数据保持不变。", user.isActive ? "确认停用" : "确认启用")}>{user.isActive ? "停用" : "启用"}</button>{isSelf ? <small>当前账户</small> : null}</div></td></tr>;
      })}</tbody></table></div> : usersState === "ready" ? <div className="admin-empty"><strong>没有匹配账户</strong><p>调整搜索词或筛选条件后重试。</p></div> : null}
      {userHasMore ? <div className="admin-list-more"><span>已显示 {users.length} / {total} 个账户</span><button className="product-secondary-action" type="button" disabled={usersState !== "ready" || busyUserId !== null} onClick={() => void loadUsers(usersRequest.query, usersRequest.status, usersRequest.role, true)}>{usersState === "loading" ? "正在读取…" : "显示更多账户"}</button></div> : null}
    </section>
    </div>
    <div id="admin-panel-projects" role="tabpanel" aria-labelledby="admin-tab-projects" tabIndex={0} hidden={activeTab !== "projects"}>
<section className="admin-section" aria-labelledby="admin-projects-title">
      <header><div><h2 id="admin-projects-title">项目与成员</h2><p>选择项目，查看成员并调整访问权限。</p></div><span>{projectsState === "ready" ? `${projects.length} / ${projectTotal} 个项目` : "项目数量待确认"}</span></header>
      <form className="admin-filter-bar" onSubmit={(event) => { event.preventDefault(); void loadProjects(); }}>
        <label>搜索项目<input value={projectQuery} onChange={(event) => setProjectQuery(event.target.value)} placeholder="项目名称、所有者或项目标识" /></label>
        <button className="product-secondary-action" type="submit" disabled={projectsState === "loading" || busyUserId !== null}>{projectsState === "loading" ? "正在筛选…" : "应用筛选"}</button>
      </form>
      {projectsState === "loading" ? <p role="status">正在读取项目…</p> : null}
      {projectsState === "error" ? <div className="product-state" role="alert"><strong>项目目录暂时无法读取</strong><p>{projectsError}</p>{projects.length ? <p>以下保留上次读取的项目，请重新加载以确认筛选结果。</p> : null}<button className="product-secondary-action" type="button" onClick={() => void loadProjects(projectsRequest.query, projectsRequest.append)}>重新加载项目</button></div> : null}
      <div className="admin-project-layout">
        <div className="admin-project-list" role="list" aria-label="项目目录">
          {projects.length ? projects.map((project) => <button key={project.id} type="button" aria-pressed={selectedProject?.id === project.id} className={`admin-project-row${selectedProject?.id === project.id ? " selected" : ""}`} onClick={() => void openMembers(project)}>
            <strong>{project.name}</strong><span>{project.owner.displayName} · {project.memberCount} 位成员</span><small>{project.description || "暂无项目说明"}</small>
          </button>) : projectsState === "ready" ? <div className="admin-empty"><strong>没有匹配项目</strong><p>调整搜索词后重试。</p></div> : null}
        </div>
        <div className="admin-project-members" aria-live="polite">
          {selectedProject ? <><div className="admin-project-members-heading"><div><h3>{selectedProject.name}</h3></div><span>{membersState === "ready" ? `${members.length} 位成员` : "成员数量待确认"}</span><button className="product-secondary-action" type="button" disabled={membersState === "loading" || busyUserId !== null} onClick={() => void openMembers(selectedProject)}>刷新成员</button></div>
            {membersState === "loading" ? <div className="product-loading" role="status">正在读取成员…</div> : null}
            {membersState === "error" ? <div className="product-state" role="alert"><strong>项目成员暂时无法读取</strong><p>{membersError}</p>{members.length ? <p>保留上次读取的成员，重新加载后可继续操作。</p> : null}<button className="product-secondary-action" type="button" onClick={() => void openMembers(selectedProject)}>重新加载成员</button></div> : null}
            {members.length ? <ul>{members.map((member) => {
              const busy = busyUserId !== null || membersState !== "ready";
              return <li key={member.userId}><div><strong>{member.displayName}</strong><span>{member.email}</span></div><div className="admin-member-actions"><select aria-label={`${member.displayName} 的项目角色`} value={member.role} disabled={busy || member.role === "owner"} onChange={(event) => requestMemberRoleChange(member, event.target.value as PlatformAdminProjectMember["role"])}>{member.role === "owner" ? <option value="owner">所有者</option> : null}<option value="admin">管理员</option><option value="researcher">研究者</option><option value="viewer">查看者</option></select>{member.role !== "owner" ? <button className="product-link-button danger" type="button" disabled={busy} onClick={() => requestMemberRemoval(member)}>移除</button> : <small>受保护所有者</small>}</div></li>;
            })}</ul> : membersState === "ready" ? <div className="admin-empty"><strong>暂无成员关系</strong><p>项目所有者仍由项目本身保留。</p></div> : null}
          </> : <div className="admin-empty"><strong>选择一个项目</strong><p>查看成员关系、角色与访问状态。</p></div>}
        </div>
      </div>
      {projectHasMore ? <div className="admin-list-more"><span>已显示 {projects.length} / {projectTotal} 个项目</span><button className="product-secondary-action" type="button" disabled={projectsState !== "ready" || busyUserId !== null} onClick={() => void loadProjects(projectsRequest.query, true)}>{projectsState === "loading" ? "正在读取…" : "显示更多项目"}</button></div> : null}
    </section>
    </div>
    <div id="admin-panel-operations" role="tabpanel" aria-labelledby="admin-tab-operations" tabIndex={0} hidden={activeTab !== "operations"}>
<section className="admin-overview" aria-labelledby="admin-overview-title">
      <div className="admin-overview-lead"><h2 id="admin-overview-title">平台概览</h2><p>{overview?.operations.capturedAt ? `记录时间 ${dateLabel(String(overview.operations.capturedAt))}` : "记录时间未知"}</p></div>
      <dl>{[["用户", overview?.counts.users], ["有效用户", overview?.counts.activeUsers], ["平台管理员", overview?.counts.platformAdmins], ["项目", overview?.counts.projects], ["有效登录", overview?.counts.activeSessions]].map(([label, value]) => <div key={String(label)}><dt>{label}</dt><dd>{numericMetric(value) ?? "—"}</dd></div>)}</dl>
    </section>
<section className="admin-section admin-operations-section" aria-labelledby="admin-operations-title">
      <header><div><h2 id="admin-operations-title">任务运行状态</h2><p>查看等待处理的任务、执行进程和需要处理的告警。</p></div><span>{overviewState !== "ready" || !completeOperations ? "待确认" : operationsAlerts.length ? `${operationsAlerts.length} 个告警` : "无告警"}</span></header>
      <dl className="admin-operations-metrics">
        <div><dt>排队任务</dt><dd>{numericMetric(queueOperations.totalQueued) ?? "—"}</dd></div>
        <div><dt>执行进程</dt><dd>{numericMetric(queueOperations.workerCount) ?? "—"}</dd></div>
        <div><dt>正常进程</dt><dd>{numericMetric(workerHealth.healthyCount) ?? "—"}</dd></div>
        <div><dt>长时间未更新的任务</dt><dd>{numericMetric(databaseOperations.staleJobs) ?? "—"}</dd></div>
      </dl>
      {operationsAlerts.length ? <ul className="admin-operations-alerts" aria-label="运行告警与处置建议">{operationsAlerts.map((alert) => <li key={alert.code} className={`severity-${alert.severity.toLowerCase()}`}><div><strong>{operationsAlertLabel[alert.code] || "运行异常"}</strong>{alert.runbook?.operatorAction ? <p>{alert.runbook.operatorAction}</p> : null}<details><summary>技术详情</summary><p>{alert.message}</p><code>{alert.runbook?.id || alert.code}</code></details></div></li>)}</ul> : healthy ? <div className="admin-operations-healthy" role="status"><strong>队列运行正常</strong><p>没有发现积压、任务超时或执行进程异常。</p></div> : <div className="admin-operations-unknown" role="status"><strong>运行状态尚未确认</strong><p>缺失的指标以“—”显示。请刷新平台概览后核对。</p></div>}
    </section>
    </div>
    <div id="admin-panel-audit" role="tabpanel" aria-labelledby="admin-tab-audit" tabIndex={0} hidden={activeTab !== "audit"}>
<section className="admin-section" aria-labelledby="admin-audit-title">
      <header><div><h2 id="admin-audit-title">近期平台变更</h2><p>查看账户和权限的近期修改记录。</p></div><button className="product-secondary-action" type="button" disabled={auditState === "loading"} onClick={() => void loadAudit()}>{auditState === "error" ? "重新读取变更" : "刷新变更"}</button></header>
      {auditState === "loading" ? <p role="status">正在读取平台变更…</p> : auditState === "error" ? <p className="product-form-error" role="alert">平台变更暂时无法读取。{audit.length ? "以下保留上次记录。" : ""}</p> : null}
      {audit.length ? <ol className="admin-audit-list">{audit.map((item) => <li key={item.id}><div><strong>{actionLabel[item.action] || item.action}</strong><span>{item.actor.email || item.actor.id || "系统"} · {item.targetId}</span></div><time dateTime={item.createdAt}>{dateLabel(item.createdAt)}</time></li>)}</ol> : auditState === "ready" ? <div className="admin-empty"><strong>暂无平台变更</strong><p>账户或权限变更后，可在此查看记录。</p></div> : null}
    </section>
    </div>
    {pendingUserAction ? <ProductModal title={pendingUserAction.title} eyebrow="账户权限" description={pendingUserAction.consequence} onClose={() => setPendingUserAction(null)} footer={<><button className="product-secondary-action" type="button" onClick={() => setPendingUserAction(null)}>取消</button><button className={pendingUserAction.changes.isActive === false ? "product-danger-action" : "product-primary-action"} type="button" onClick={() => void confirmUserAction()}>{pendingUserAction.confirmLabel}</button></>}><div className="admin-action-target"><strong>{pendingUserAction.user.displayName}</strong><span>{pendingUserAction.user.email}</span></div></ProductModal> : null}
    {pendingMemberAction ? <ProductModal title={pendingMemberAction.kind === "remove" ? "确认移除项目访问权限？" : "确认更新项目角色？"} eyebrow={selectedProject?.name || "项目成员"} description={pendingMemberAction.kind === "remove" ? "移除后，该成员无法继续访问此项目。账户和已有研究结果仍会保留。" : `角色将变更为${pendingMemberAction.role === "admin" ? "项目管理员" : pendingMemberAction.role === "researcher" ? "研究者" : "查看者"}。`} onClose={() => setPendingMemberAction(null)} footer={<><button className="product-secondary-action" type="button" onClick={() => setPendingMemberAction(null)}>取消</button><button className={pendingMemberAction.kind === "remove" ? "product-danger-action" : "product-primary-action"} type="button" onClick={() => void confirmMemberAction()}>{pendingMemberAction.kind === "remove" ? "确认移除" : "确认更新"}</button></>}><div className="admin-action-target"><strong>{pendingMemberAction.member.displayName}</strong><span>{pendingMemberAction.member.email}</span></div></ProductModal> : null}
    {inviteOpen ? <ProductModal title="邀请研究者" eyebrow="添加账户" description="创建后，将激活凭证交给受邀者。系统不会自动发送邮件。" onClose={closeInvitation} footer={<><button className="product-secondary-action" type="button" onClick={closeInvitation}>{inviteResult ? "完成" : "取消"}</button>{!inviteResult ? <button className="product-primary-action" type="submit" form="admin-invitation-form" disabled={inviteBusy || !inviteEmail.trim() || !inviteDisplayName.trim()}>{inviteBusy ? "正在创建…" : "创建邀请"}</button> : null}</>}>
      {!inviteResult ? (
<form id="admin-invitation-form" className="admin-invitation-form" onSubmit={createInvitation}>
        <label>邮箱<input type="email" disabled={inviteBusy} value={inviteEmail} onChange={(event) => setInviteEmail(event.target.value)} autoComplete="off" required /></label>
        <label>姓名<input disabled={inviteBusy} value={inviteDisplayName} onChange={(event) => setInviteDisplayName(event.target.value)} maxLength={160} required /></label>
      </form>
      ) : <div className="admin-invitation-result"><strong>{inviteResult.email}</strong><p>请将凭证与<Link href="/activate">激活页面</Link>地址交给受邀者，由其设置登录密码。</p><code>{inviteResult.activationToken}</code><span>有效期至 {dateLabel(inviteResult.expiresAt)}</span><button className="product-secondary-action" type="button" onClick={() => void copyInvitationToken()}>{inviteCopied ? "已复制凭证" : "复制凭证"}</button></div>}
      {inviteFeedback ? <p role="status">{inviteFeedback}</p> : null}
    </ProductModal> : null}
  </section>;
}
