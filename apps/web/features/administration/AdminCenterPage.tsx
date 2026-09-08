"use client";

import { useEffect, useState } from "react";
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

type FilterStatus = "ALL" | "ACTIVE" | "INACTIVE";
type FilterRole = "ALL" | "USER" | "PLATFORM_ADMIN";
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
};

const operationsAlertLabel: Record<string, string> = {
  OPS_QUEUE_DEPTH_EXCEEDED: "队列积压超过阈值",
  OPS_STALE_JOBS: "发现超时未推进的 Job",
  OPS_WORKER_COUNT_BELOW_MINIMUM: "可用 worker 数量不足",
  OPS_WORKER_HEALTH_DEGRADED: "worker 心跳或状态异常",
};

const numericMetric = (value: unknown) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : 0;
};

export function AdminCenterPage() {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [overview, setOverview] = useState<PlatformAdminOverview | null>(null);
  const [users, setUsers] = useState<PlatformAdminUser[]>([]);
  const [audit, setAudit] = useState<PlatformAdminAuditItem[]>([]);
  const [projects, setProjects] = useState<PlatformAdminProject[]>([]);
  const [projectQuery, setProjectQuery] = useState("");
  const [selectedProject, setSelectedProject] = useState<PlatformAdminProject | null>(null);
  const [members, setMembers] = useState<PlatformAdminProjectMember[]>([]);
  const [membersLoading, setMembersLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [projectTotal, setProjectTotal] = useState(0);
  const [userHasMore, setUserHasMore] = useState(false);
  const [projectHasMore, setProjectHasMore] = useState(false);
  const [state, setState] = useState<"loading" | "ready" | "forbidden" | "error">("loading");
  const [loadRetryToken, setLoadRetryToken] = useState(0);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<FilterStatus>("ALL");
  const [role, setRole] = useState<FilterRole>("ALL");
  const [searching, setSearching] = useState(false);
  const [busyUserId, setBusyUserId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteDisplayName, setInviteDisplayName] = useState("");
  const [inviteBusy, setInviteBusy] = useState(false);
  const [inviteResult, setInviteResult] = useState<{ email: string; expiresAt: string; activationToken: string } | null>(null);
  const [inviteCopied, setInviteCopied] = useState(false);
  const [pendingUserAction, setPendingUserAction] = useState<PendingUserAction | null>(null);
  const [pendingMemberAction, setPendingMemberAction] = useState<PendingMemberAction | null>(null);

  async function loadUsers(
    nextQuery = query,
    nextStatus = status,
    nextRole = role,
    append = false,
  ) {
    setSearching(true);
    setFeedback("");
    try {
      const offset = append ? users.length : 0;
      const result = await listPlatformAdminUsers({
        query: nextQuery,
        status: nextStatus,
        role: nextRole,
        limit: 50,
        ...(offset ? { offset } : {}),
      });
      setUsers((items) => append ? [...items, ...result.items] : result.items);
      setTotal(result.total);
      setUserHasMore(offset + result.items.length < result.total);
    } catch (reason) {
      setFeedback(reason instanceof Error ? reason.message : "账户目录暂时无法读取。");
    } finally {
      setSearching(false);
    }
  }

  useEffect(() => {
    let active = true;
    void getAuthUser()
      .then(async (user) => {
        if (!active) return;
        setCurrentUser(user);
        if (user.platformRole !== "PLATFORM_ADMIN") {
          setState("forbidden");
          return;
        }
        const [overviewResult, usersResult, auditResult, projectsResult] = await Promise.all([
          getPlatformAdminOverview(),
          listPlatformAdminUsers({ limit: 50 }),
          listPlatformAdminAudit(30),
          listPlatformAdminProjects({ limit: 50 }),
        ]);
        if (!active) return;
        setOverview(overviewResult);
        setUsers(usersResult.items);
        setTotal(usersResult.total);
        setUserHasMore(usersResult.items.length < usersResult.total);
        setAudit(auditResult.items);
        setProjects(projectsResult.items);
        setProjectTotal(projectsResult.total);
        setProjectHasMore(projectsResult.items.length < projectsResult.total);
        setState("ready");
      })
      .catch(() => {
        if (active) setState("error");
      });
    return () => {
      active = false;
    };
  }, [loadRetryToken]);

  async function updateUser(
    user: PlatformAdminUser,
    changes: { platformRole?: "USER" | "PLATFORM_ADMIN"; isActive?: boolean },
  ) {
    setBusyUserId(user.id);
    setFeedback("");
    try {
      const updated = await updatePlatformAdminUser(user.id, changes);
      setUsers((items) => items.map((item) => item.id === updated.id ? updated : item));
      const nextOverview = await getPlatformAdminOverview();
      setOverview(nextOverview);
      setFeedback(`已更新 ${updated.displayName} 的平台账户。`);
    } catch (reason) {
      setFeedback(reason instanceof Error ? reason.message : "账户更新失败。");
    } finally {
      setBusyUserId(null);
    }
  }

  async function createInvitation(event: React.FormEvent) {
    event.preventDefault();
    setInviteBusy(true);
    setInviteResult(null);
    setFeedback("");
    try {
      const result = await createPlatformInvitation(inviteEmail.trim(), inviteDisplayName.trim());
      setInviteResult(result);
      setInviteCopied(false);
      setInviteEmail("");
      setInviteDisplayName("");
      setFeedback("邀请已创建；激活凭证只在此处显示一次，请通过受控渠道交付。");
    } catch (reason) {
      setFeedback(reason instanceof Error ? reason.message : "创建邀请失败。");
    } finally {
      setInviteBusy(false);
    }
  }

  async function loadProjects(nextQuery = projectQuery, append = false) {
    setSearching(true);
    setFeedback("");
    try {
      const offset = append ? projects.length : 0;
      const result = await listPlatformAdminProjects({ query: nextQuery, limit: 50, ...(offset ? { offset } : {}) });
      setProjects((items) => append ? [...items, ...result.items] : result.items);
      setProjectTotal(result.total);
      setProjectHasMore(offset + result.items.length < result.total);
      setSelectedProject((current) => current && (
        result.items.some((item) => item.id === current.id) ||
        (append && projects.some((item) => item.id === current.id))
      )
        ? result.items.find((item) => item.id === current.id) || current
        : null);
    } catch (reason) {
      setFeedback(reason instanceof Error ? reason.message : "项目目录暂时无法读取。");
    } finally {
      setSearching(false);
    }
  }

  async function openMembers(project: PlatformAdminProject) {
    setSelectedProject(project);
    setMembersLoading(true);
    setFeedback("");
    try {
      const result = await listPlatformAdminProjectMembers(project.id);
      setMembers(result.items);
    } catch (reason) {
      setMembers([]);
      setFeedback(reason instanceof Error ? reason.message : "项目成员暂时无法读取。");
    } finally {
      setMembersLoading(false);
    }
  }

  async function updateMember(member: PlatformAdminProjectMember, role: PlatformAdminProjectMember["role"]) {
    if (!selectedProject || member.role === role) return;
    setBusyUserId(`${selectedProject.id}:${member.userId}`);
    setFeedback("");
    try {
      await updatePlatformAdminProjectMember(selectedProject.id, member.userId, role);
      setMembers((items) => items.map((item) => item.userId === member.userId ? { ...item, role } : item));
      setFeedback(`已更新 ${member.displayName} 在项目中的角色。`);
    } catch (reason) {
      setFeedback(reason instanceof Error ? reason.message : "项目成员角色更新失败。");
    } finally {
      setBusyUserId(null);
    }
  }

  async function removeMember(member: PlatformAdminProjectMember) {
    if (!selectedProject || member.role === "owner") return;
    setBusyUserId(`${selectedProject.id}:${member.userId}`);
    setFeedback("");
    try {
      await removePlatformAdminProjectMember(selectedProject.id, member.userId);
      setMembers((items) => items.filter((item) => item.userId !== member.userId));
      setProjects((items) => items.map((item) => item.id === selectedProject.id ? { ...item, memberCount: Math.max(0, item.memberCount - 1) } : item));
      setFeedback(`已移除 ${member.displayName} 的项目访问权限。`);
    } catch (reason) {
      setFeedback(reason instanceof Error ? reason.message : "移除项目成员失败。");
    } finally {
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
    try {
      await navigator.clipboard?.writeText(inviteResult.activationToken);
      setInviteCopied(true);
      setFeedback("一次性激活凭证已复制；请通过受控渠道交付。");
    } catch {
      setInviteCopied(false);
      setFeedback("浏览器未允许复制，请手动复制页面中的一次性凭证。");
    }
  }

  if (state === "loading") return <section className="document-page admin-center-page"><div className="product-loading" role="status">正在验证平台管理权限…</div></section>;
  if (state === "forbidden") return <section className="document-page admin-center-page"><div className="product-state" role="alert"><h1>无平台管理权限</h1><p>平台用户可以管理自己的账户与项目，但不能读取全局用户或运行状态。</p><div className="product-row-actions admin-forbidden-actions"><Link className="product-primary-action" href="/console">返回控制台</Link><Link className="product-secondary-action" href="/account">账户中心</Link></div></div></section>;
  if (state === "error" || !currentUser || !overview) return <section className="document-page admin-center-page"><div className="product-state" role="alert"><h1>管理中心暂时无法读取</h1><p>权限状态或服务连接发生变化；没有执行任何账户变更。</p><div className="product-row-actions"><button className="product-primary-action" type="button" onClick={() => setLoadRetryToken((value) => value + 1)}>重新读取</button><Link className="product-secondary-action" href="/account">返回账户中心</Link></div></div></section>;

  const operationStatus = String(overview.operations.status || "unknown").toLowerCase();
  const operationsAlerts = overview.operations.alerts || [];
  const databaseOperations = overview.operations.database || {};
  const queueOperations = overview.operations.queues || {};
  const workerHealth = (
    typeof queueOperations.workerHealth === "object" &&
    queueOperations.workerHealth !== null
      ? queueOperations.workerHealth
      : {}
  ) as Record<string, unknown>;
  return <section className="document-page admin-center-page">
    <header className="product-page-heading admin-center-heading"><div><p className="product-kicker">平台治理</p><h1>管理中心</h1><p>管理平台账户、访问状态与审计记录。项目科学权限仍由各项目成员关系独立控制。</p></div><div className="product-row-actions"><Link className="product-secondary-action" href="/console">返回控制台</Link><Link className="product-secondary-action" href="/account">账户中心</Link></div></header>

    <section className="admin-overview" aria-labelledby="admin-overview-title">
      <div className="admin-overview-lead"><p className="product-kicker">当前运行</p><h2 id="admin-overview-title">平台概览</h2><p><span className={`admin-health-marker status-${operationStatus}`}>{operationStatus === "ok" || operationStatus === "healthy" ? "服务正常" : "需要检查"}</span>{overview.operations.capturedAt ? ` · 更新于 ${dateLabel(String(overview.operations.capturedAt))}` : ""}</p></div>
      <dl>{[["用户", overview.counts.users], ["有效用户", overview.counts.activeUsers], ["平台管理员", overview.counts.platformAdmins], ["项目", overview.counts.projects], ["有效会话", overview.counts.activeSessions]].map(([label, value]) => <div key={String(label)}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
    </section>

    <section className="admin-section admin-operations-section" aria-labelledby="admin-operations-title">
      <header><div><p className="product-kicker">运行与恢复</p><h2 id="admin-operations-title">队列、Job 与 worker</h2><p>指标来自只读 operations snapshot；处置建议引用仓库内的受控 runbook，不会从此页面直接修改队列或科学记录。</p></div><span>{operationsAlerts.length ? `${operationsAlerts.length} 个告警` : "无告警"}</span></header>
      <dl className="admin-operations-metrics">
        <div><dt>排队任务</dt><dd>{numericMetric(queueOperations.totalQueued)}</dd></div>
        <div><dt>注册 worker</dt><dd>{numericMetric(queueOperations.workerCount)}</dd></div>
        <div><dt>健康 worker</dt><dd>{numericMetric(workerHealth.healthyCount)}</dd></div>
        <div><dt>过期 Job</dt><dd>{numericMetric(databaseOperations.staleJobs)}</dd></div>
      </dl>
      {operationsAlerts.length ? <ul className="admin-operations-alerts" aria-label="运行告警与处置建议">{operationsAlerts.map((alert) => <li key={alert.code} className={`severity-${alert.severity.toLowerCase()}`}><div><strong>{operationsAlertLabel[alert.code] || alert.code}</strong><span>{alert.message}</span></div><div><code>{alert.runbook?.id || alert.code}</code>{alert.runbook?.operatorAction ? <p>{alert.runbook.operatorAction}</p> : null}</div></li>)}</ul> : <div className="admin-operations-healthy" role="status"><strong>队列运行正常</strong><p>当前没有 queue depth、stale Job 或 worker health 告警。</p></div>}
    </section>

    <section className="admin-section" aria-labelledby="admin-users-title">
      <header><div><p className="product-kicker">身份与访问</p><h2 id="admin-users-title">平台账户</h2><p>显示前 50 项授权账户。停用账户会由服务端撤销其全部有效会话。</p></div><span>{total} 个账户</span></header>
      <form className="admin-filter-bar" onSubmit={(event) => { event.preventDefault(); void loadUsers(); }}>
        <label>搜索<input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="姓名、邮箱或账户标识" /></label>
        <label>状态<select value={status} onChange={(event) => setStatus(event.target.value as FilterStatus)}><option value="ALL">全部</option><option value="ACTIVE">有效</option><option value="INACTIVE">已停用</option></select></label>
        <label>平台角色<select value={role} onChange={(event) => setRole(event.target.value as FilterRole)}><option value="ALL">全部</option><option value="USER">平台用户</option><option value="PLATFORM_ADMIN">平台管理员</option></select></label>
        <button className="product-secondary-action" type="submit" disabled={searching}>{searching ? "正在筛选…" : "应用筛选"}</button>
      </form>
      {feedback ? <p className="admin-feedback" role="status">{feedback}</p> : null}
      {pendingUserAction ? <div className="admin-confirmation" role="alertdialog" aria-labelledby="admin-user-confirm-title" aria-describedby="admin-user-confirm-description"><div><strong id="admin-user-confirm-title">{pendingUserAction.title}</strong><p id="admin-user-confirm-description">{pendingUserAction.consequence}</p><span>目标账户：{pendingUserAction.user.displayName} · {pendingUserAction.user.email}</span></div><div className="admin-confirmation-actions"><button className="product-primary-action" type="button" onClick={() => void confirmUserAction()}>{pendingUserAction.confirmLabel}</button><button className="product-secondary-action" type="button" onClick={() => setPendingUserAction(null)}>取消</button></div></div> : null}
      {users.length ? <div className="admin-user-table-scroll"><table className="admin-user-table"><thead><tr><th scope="col">账户</th><th scope="col">角色</th><th scope="col">项目</th><th scope="col">会话</th><th scope="col">状态</th><th scope="col">操作</th></tr></thead><tbody>{users.map((user) => {
        const isSelf = user.id === currentUser.id;
        const busy = busyUserId === user.id;
        return <tr key={user.id}><th scope="row"><strong>{user.displayName}</strong><span>{user.email}</span></th><td>{user.platformRole === "PLATFORM_ADMIN" ? "平台管理员" : "平台用户"}</td><td>{user.projectCount}</td><td>{user.activeSessionCount}</td><td><span className={user.isActive ? "admin-account-status active" : "admin-account-status inactive"}>{user.isActive ? "有效" : "已停用"}</span></td><td><div className="admin-user-actions"><button className="product-link-button" type="button" disabled={busy || isSelf} onClick={() => requestUserAction(user, { platformRole: user.platformRole === "PLATFORM_ADMIN" ? "USER" : "PLATFORM_ADMIN" }, user.platformRole === "PLATFORM_ADMIN" ? "确认降为平台用户？" : "确认授予平台管理员？", "这会改变该账户访问平台级用户、项目和运行状态管理功能的权限。", user.platformRole === "PLATFORM_ADMIN" ? "确认降权" : "确认授予管理员权限")}>{user.platformRole === "PLATFORM_ADMIN" ? "设为普通用户" : "设为管理员"}</button><button className="product-link-button" type="button" disabled={busy || isSelf} onClick={() => requestUserAction(user, { isActive: !user.isActive }, user.isActive ? "确认停用账户？" : "确认启用账户？", user.isActive ? "停用后服务端会撤销该账户全部有效会话，历史科学 provenance 不会删除。" : "启用后该账户可以重新登录；项目成员关系与历史科学数据保持不变。", user.isActive ? "确认停用" : "确认启用")}>{user.isActive ? "停用" : "启用"}</button>{isSelf ? <small>当前账户</small> : null}</div></td></tr>;
      })}</tbody></table></div> : <div className="admin-empty"><strong>没有匹配账户</strong><p>调整搜索词或筛选条件后重试。</p></div>}
      {userHasMore ? <div className="admin-list-more"><span>已显示 {users.length} / {total} 个账户</span><button className="product-secondary-action" type="button" disabled={searching} onClick={() => void loadUsers(query, status, role, true)}>{searching ? "正在读取…" : "显示更多账户"}</button></div> : null}
    </section>

    <section className="admin-section" aria-labelledby="admin-audit-title">
      <header><div><p className="product-kicker">审计</p><h2 id="admin-audit-title">近期平台变更</h2><p>这里只展示经过清理的平台级账户事件，不包含凭据、令牌或内部连接信息。</p></div><span>最近 {audit.length} 项</span></header>
      {audit.length ? <ol className="admin-audit-list">{audit.map((item) => <li key={item.id}><div><strong>{actionLabel[item.action] || item.action}</strong><span>{item.actor.email || item.actor.id || "系统"} · {item.targetId}</span></div><time dateTime={item.createdAt}>{dateLabel(item.createdAt)}</time></li>)}</ol> : <div className="admin-empty"><strong>暂无平台变更</strong><p>管理员操作发生后会在此形成可审计记录。</p></div>}
    </section>
    <section className="admin-section" aria-labelledby="admin-invitations-title">
      <header><div><p className="product-kicker">账户入口</p><h2 id="admin-invitations-title">邀请研究者</h2><p>凭证由服务端一次性消费并设置密码；平台不记录明文凭证，也不自动发送邮件。</p></div></header>
      <form className="admin-filter-bar" onSubmit={createInvitation}>
        <label>邮箱<input type="email" value={inviteEmail} onChange={(event) => setInviteEmail(event.target.value)} autoComplete="off" required /></label>
        <label>显示名称<input value={inviteDisplayName} onChange={(event) => setInviteDisplayName(event.target.value)} maxLength={160} required /></label>
        <button className="product-primary-action" type="submit" disabled={inviteBusy}>{inviteBusy ? "正在创建…" : "创建邀请"}</button>
      </form>
      {inviteResult ? <div className="admin-invitation-result" role="status"><strong>请安全交付以下一次性凭证</strong><code>{inviteResult.activationToken}</code><span>有效期至 {dateLabel(inviteResult.expiresAt)} · 激活页：/activate?token=…</span><button className="product-secondary-action" type="button" onClick={() => void copyInvitationToken()}>{inviteCopied ? "已复制凭证" : "复制凭证"}</button></div> : null}
    </section>
    <section className="admin-section" aria-labelledby="admin-projects-title">
      <header><div><p className="product-kicker">项目权限</p><h2 id="admin-projects-title">项目与成员</h2><p>平台管理员可查看项目成员关系并调整协作者角色；科学对象、版本与结果仍由项目权限边界保护。</p></div><span>{projects.length} / {projectTotal} 个项目</span></header>
      <form className="admin-filter-bar" onSubmit={(event) => { event.preventDefault(); void loadProjects(); }}>
        <label>搜索项目<input value={projectQuery} onChange={(event) => setProjectQuery(event.target.value)} placeholder="项目名称、所有者或项目标识" /></label>
        <button className="product-secondary-action" type="submit" disabled={searching}>{searching ? "正在筛选…" : "应用筛选"}</button>
      </form>
      <div className="admin-project-layout">
        <div className="admin-project-list" role="list" aria-label="项目目录">
          {projects.length ? projects.map((project) => <button key={project.id} type="button" className={`admin-project-row${selectedProject?.id === project.id ? " selected" : ""}`} onClick={() => void openMembers(project)}>
            <strong>{project.name}</strong><span>{project.owner.displayName} · {project.memberCount} 位成员</span><small>{project.description || "暂无项目说明"}</small>
          </button>) : <div className="admin-empty"><strong>没有匹配项目</strong><p>调整搜索词后重试。</p></div>}
        </div>
        <div className="admin-project-members" aria-live="polite">
          {selectedProject ? <><div className="admin-project-members-heading"><div><p className="product-kicker">成员关系</p><h3>{selectedProject.name}</h3></div><span>{members.length} 位成员</span></div>
            {pendingMemberAction ? <div className="admin-confirmation admin-confirmation-member" role="alertdialog" aria-labelledby="admin-member-confirm-title" aria-describedby="admin-member-confirm-description"><div><strong id="admin-member-confirm-title">{pendingMemberAction.kind === "remove" ? "确认移除项目访问权限？" : "确认更新项目角色？"}</strong><p id="admin-member-confirm-description">{pendingMemberAction.kind === "remove" ? "移除后该成员将无法继续访问此项目，但不会删除其账户或历史科学结果。" : `角色将变更为${pendingMemberAction.role === "admin" ? "项目管理员" : pendingMemberAction.role === "researcher" ? "研究者" : "查看者"}；项目科学数据和历史 provenance 不会被修改。`}</p><span>目标成员：{pendingMemberAction.member.displayName} · {pendingMemberAction.member.email}</span></div><div className="admin-confirmation-actions"><button className={pendingMemberAction.kind === "remove" ? "product-danger-action" : "product-primary-action"} type="button" onClick={() => void confirmMemberAction()}>{pendingMemberAction.kind === "remove" ? "确认移除" : "确认更新"}</button><button className="product-secondary-action" type="button" onClick={() => setPendingMemberAction(null)}>取消</button></div></div> : null}
            {membersLoading ? <div className="product-loading" role="status">正在读取成员…</div> : members.length ? <ul>{members.map((member) => {
              const key = `${selectedProject.id}:${member.userId}`;
              const busy = busyUserId === key;
              return <li key={member.userId}><div><strong>{member.displayName}</strong><span>{member.email}</span></div><div className="admin-member-actions"><select aria-label={`${member.displayName} 的项目角色`} value={member.role} disabled={busy || member.role === "owner"} onChange={(event) => requestMemberRoleChange(member, event.target.value as PlatformAdminProjectMember["role"])}>{member.role === "owner" ? <option value="owner">所有者</option> : null}<option value="admin">管理员</option><option value="researcher">研究者</option><option value="viewer">查看者</option></select>{member.role !== "owner" ? <button className="product-link-button danger" type="button" disabled={busy} onClick={() => requestMemberRemoval(member)}>移除</button> : <small>受保护所有者</small>}</div></li>;
            })}</ul> : <div className="admin-empty"><strong>暂无成员关系</strong><p>项目所有者仍由项目本身保留。</p></div>}
          </> : <div className="admin-empty"><strong>选择一个项目</strong><p>查看成员关系、角色与访问状态。</p></div>}
        </div>
      </div>
      {projectHasMore ? <div className="admin-list-more"><span>已显示 {projects.length} / {projectTotal} 个项目</span><button className="product-secondary-action" type="button" disabled={searching} onClick={() => void loadProjects(projectQuery, true)}>{searching ? "正在读取…" : "显示更多项目"}</button></div> : null}
    </section>
  </section>;
}
