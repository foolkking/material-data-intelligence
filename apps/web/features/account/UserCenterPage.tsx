"use client";

import { useEffect, useState } from "react";
import {
  changeAuthPassword,
  deactivateAuthAccount,
  getAuthUser,
  listAuthSessions,
  revokeAuthSession,
  revokeOtherAuthSessions,
  updateAuthProfile,
  type AuthSession,
  type AuthUser,
} from "../../app/lib/product-api";
import { ProductLink as Link } from "../../shared/layout/ProductNavigation";

const roleLabel: Record<string, string> = {
  owner: "项目所有者",
  admin: "项目管理员",
  researcher: "研究成员",
  viewer: "只读成员",
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
type Feedback = { tone: "success" | "error"; message: string } | null;
const VISIBLE_SESSION_LIMIT = 8;

export function UserCenterPage() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [sessions, setSessions] = useState<AuthSession[]>([]);
  const [showAllSessions, setShowAllSessions] = useState(false);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [sessionsState, setSessionsState] = useState<"loading" | "ready" | "error">("loading");
  const [accountRetryToken, setAccountRetryToken] = useState(0);
  const [sessionRetryToken, setSessionRetryToken] = useState(0);
  const [displayName, setDisplayName] = useState("");
  const [profileBusy, setProfileBusy] = useState(false);
  const [profileFeedback, setProfileFeedback] = useState<Feedback>(null);
  const [sessionBusy, setSessionBusy] = useState<string | null>(null);
  const [sessionFeedback, setSessionFeedback] = useState<Feedback>(null);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordBusy, setPasswordBusy] = useState(false);
  const [passwordFeedback, setPasswordFeedback] = useState<Feedback>(null);
  const [deactivatePassword, setDeactivatePassword] = useState("");
  const [deactivateEmail, setDeactivateEmail] = useState("");
  const [deactivateAcknowledged, setDeactivateAcknowledged] = useState(false);
  const [deactivateFeedback, setDeactivateFeedback] = useState<Feedback>(null);

  useEffect(() => {
    let active = true;
    setState("loading");
    setSessionsState("loading");
    void Promise.allSettled([getAuthUser(), listAuthSessions()]).then(([auth, sessionResult]) => {
      if (!active) return;
      if (auth.status === "rejected") {
        setState("error");
        return;
      }
      setUser(auth.value);
      setDisplayName(auth.value.displayName);
      setState("ready");
      if (sessionResult.status === "fulfilled") {
        setSessions(sessionResult.value.items);
        setSessionsState("ready");
      } else setSessionsState("error");
    });
    return () => {
      active = false;
    };
  }, [accountRetryToken, sessionRetryToken]);

  async function saveProfile(event: React.FormEvent) {
    event.preventDefault();
    setProfileBusy(true);
    setProfileFeedback(null);
    try {
      const next = await updateAuthProfile(displayName.trim());
      setUser(next);
      setDisplayName(next.displayName);
      setProfileFeedback({ tone: "success", message: "显示名称已更新。" });
    } catch (reason) {
      setProfileFeedback({ tone: "error", message: reason instanceof Error ? reason.message : "资料更新失败。" });
    } finally {
      setProfileBusy(false);
    }
  }

  async function revokeSession(sessionId: string) {
    setSessionBusy(sessionId);
    setSessionFeedback(null);
    try {
      await revokeAuthSession(sessionId);
      setSessions((items) => items.filter((item) => item.id !== sessionId));
      setSessionFeedback({ tone: "success", message: "该登录会话已撤销。" });
    } catch (reason) {
      setSessionFeedback({ tone: "error", message: reason instanceof Error ? reason.message : "会话撤销失败。" });
    } finally {
      setSessionBusy(null);
    }
  }

  async function revokeOthers() {
    setSessionBusy("others");
    setSessionFeedback(null);
    try {
      const result = await revokeOtherAuthSessions();
      setSessions((items) => items.filter((item) => item.isCurrent));
      setSessionFeedback({ tone: "success", message: `已撤销 ${result.revokedCount} 个其他登录会话。` });
    } catch (reason) {
      setSessionFeedback({ tone: "error", message: reason instanceof Error ? reason.message : "其他会话撤销失败。" });
    } finally {
      setSessionBusy(null);
    }
  }

  async function changePassword(event: React.FormEvent) {
    event.preventDefault();
    if (newPassword !== confirmPassword) {
      setPasswordFeedback({ tone: "error", message: "两次输入的新密码不一致。" });
      return;
    }
    if (newPassword.length < 12) {
      setPasswordFeedback({ tone: "error", message: "新密码至少需要 12 个字符。" });
      return;
    }
    setPasswordBusy(true);
    setPasswordFeedback(null);
    try {
      const result = await changeAuthPassword(currentPassword, newPassword);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setSessions((items) => items.filter((item) => item.isCurrent));
      setPasswordFeedback({ tone: "success", message: `密码已更新，并撤销 ${result.otherSessionsRevoked} 个其他会话。` });
    } catch (reason) {
      setPasswordFeedback({ tone: "error", message: reason instanceof Error ? reason.message : "密码更新失败。" });
    } finally {
      setPasswordBusy(false);
    }
  }

  async function deactivate(event: React.FormEvent) {
    event.preventDefault();
    if (!user || !window.confirm("停用会立即退出并撤销全部会话；历史科学结果仍会保留。确定继续？")) return;
    setDeactivateFeedback(null);
    try {
      await deactivateAuthAccount(deactivatePassword, deactivateEmail);
      window.location.assign("/");
    } catch (reason) {
      setDeactivateFeedback({ tone: "error", message: reason instanceof Error ? reason.message : "账户停用失败。" });
    }
  }

  if (state === "loading") return <section className="document-page user-center-page"><div className="product-loading" role="status">正在读取账户与会话…</div></section>;
  if (state === "error" || !user) return <section className="document-page user-center-page"><div className="product-state" role="alert"><h1>账户信息暂时无法读取</h1><p>登录状态或服务连接发生变化；账户数据没有被修改。</p><div className="product-row-actions"><button className="product-primary-action" type="button" onClick={() => setAccountRetryToken((value) => value + 1)}>重新读取</button><Link className="product-secondary-action" href="/console">返回控制台</Link></div></div></section>;

  const otherSessions = sessions.filter((session) => !session.isCurrent);
  const visibleSessions = showAllSessions
    ? sessions
    : [
        ...sessions.filter((session) => session.isCurrent),
        ...sessions.filter((session) => !session.isCurrent),
      ].slice(0, VISIBLE_SESSION_LIMIT);
  const roles = user.roles.length ? user.roles.map((role) => roleLabel[role.toLowerCase()] || role).join("、") : "尚未分配项目角色";
  const feedback = (value: Feedback) => value ? <p className={value.tone === "success" ? "product-form-success" : "product-form-error"} role={value.tone === "error" ? "alert" : "status"}>{value.message}</p> : null;

  return <section className="document-page user-center-page">
    <header className="product-page-heading user-center-heading">
      <div><p className="product-kicker">账户与安全</p><h1>账户中心</h1><p>管理公开身份、登录会话与密码。科学结果和精确来源版本不会因账户设置变更而被改写。</p></div>
      <div className="product-row-actions"><Link className="product-secondary-action" href="/console">返回控制台</Link>{user.platformRole === "PLATFORM_ADMIN" ? <Link className="product-secondary-action" href="/admin">平台管理</Link> : null}<Link className="product-secondary-action" href="/projects">我的项目</Link></div>
    </header>

    <div className="user-center-identity">
      <div className="user-center-avatar" aria-hidden="true">{(user.displayName || user.email || "研").slice(0, 1)}</div>
      <div><strong>{user.displayName}</strong><span>{user.email}</span></div>
      <dl><div><dt>平台角色</dt><dd>{user.platformRole === "PLATFORM_ADMIN" ? "平台管理员" : "平台用户"}</dd></div><div><dt>项目角色</dt><dd>{roles}</dd></div></dl>
    </div>

    <div className="user-center-layout">
      <nav className="user-center-index" aria-label="账户设置目录"><a href="#profile">个人资料</a><a href="#sessions">登录会话</a><a href="#password">密码</a><a href="#deactivate">停用账户</a></nav>
      <div className="user-center-sections">
        <section id="profile" className="user-center-section" aria-labelledby="profile-title">
          <header><div><p className="product-kicker">公开身份</p><h2 id="profile-title">个人资料</h2></div><p>显示名称会出现在项目成员和审计记录中；登录邮箱不可在此修改。</p></header>
          <form className="account-form" onSubmit={saveProfile}><label>显示名称<input value={displayName} onChange={(event) => setDisplayName(event.target.value)} autoComplete="name" maxLength={160} required /></label><label>登录邮箱<input value={user.email} readOnly aria-readonly="true" /></label>{feedback(profileFeedback)}<div className="account-form-actions"><button className="product-primary-action" disabled={profileBusy || !displayName.trim() || displayName.trim() === user.displayName} type="submit">{profileBusy ? "正在保存…" : "保存资料"}</button></div></form>
        </section>

        <section id="sessions" className="user-center-section" aria-labelledby="sessions-title">
          <header><div><p className="product-kicker">访问安全</p><h2 id="sessions-title">登录会话</h2></div><p>只显示仍有效的会话；认证令牌不会出现在页面中。</p></header>
          {sessionsState === "loading" ? <p className="product-form-hint" role="status">正在读取登录会话…</p> : sessionsState === "error" ? <div className="account-recovery-state" role="alert"><p className="product-form-error">登录会话暂时无法读取；账户资料仍可安全使用。</p><button className="product-secondary-action" type="button" onClick={() => setSessionRetryToken((value) => value + 1)}>重新读取会话</button></div> : sessions.length ? <><div className="account-session-list">{visibleSessions.map((session) => <article key={session.id}><div><strong>{session.isCurrent ? "当前会话" : "已登录会话"}</strong><span>最近活动 {dateLabel(session.lastSeenAt)} · 到期 {dateLabel(session.expiresAt)}</span></div>{session.isCurrent ? <span className="account-current-marker">正在使用</span> : <button className="product-secondary-action" disabled={sessionBusy !== null} type="button" onClick={() => void revokeSession(session.id)}>{sessionBusy === session.id ? "正在撤销…" : "撤销会话"}</button>}</article>)}</div>{sessions.length > VISIBLE_SESSION_LIMIT ? <div className="account-session-toggle"><span>默认仅显示最近 {VISIBLE_SESSION_LIMIT} 个会话，避免账户页过度延伸。</span><button className="product-secondary-action" type="button" aria-expanded={showAllSessions} onClick={() => setShowAllSessions((value) => !value)}>{showAllSessions ? "收起会话" : `显示全部会话（${sessions.length}）`}</button></div> : null}</> : <p className="product-form-hint">当前没有有效登录会话。</p>}
          {feedback(sessionFeedback)}
          {otherSessions.length ? <div className="account-form-actions"><button className="product-secondary-action" disabled={sessionBusy !== null} type="button" onClick={() => void revokeOthers()}>{sessionBusy === "others" ? "正在撤销…" : "撤销所有其他会话"}</button></div> : null}
        </section>

        <section id="password" className="user-center-section" aria-labelledby="password-title">
          <header><div><p className="product-kicker">凭据</p><h2 id="password-title">修改密码</h2></div><p>新密码至少 12 个字符；保存后会保留当前会话并撤销其他会话。</p></header>
          <form className="account-form" onSubmit={changePassword}><label>当前密码<input type="password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} autoComplete="current-password" required /></label><div className="account-form-split"><label>新密码<input type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} autoComplete="new-password" minLength={12} required /></label><label>确认新密码<input type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} autoComplete="new-password" minLength={12} required /></label></div>{feedback(passwordFeedback)}<div className="account-form-actions"><button className="product-primary-action" disabled={passwordBusy || !currentPassword || !newPassword || !confirmPassword} type="submit">{passwordBusy ? "正在更新…" : "更新密码"}</button></div></form>
        </section>

        <section id="deactivate" className="user-center-section account-danger-section" aria-labelledby="deactivate-title">
          <header><div><p className="product-kicker">账户生命周期</p><h2 id="deactivate-title">停用账户</h2></div><p>停用会立即撤销全部会话。历史科学结果与来源版本仍按授权和审计要求保留。</p></header>
          <form className="account-form" onSubmit={deactivate}><label>输入完整邮箱确认<input type="email" value={deactivateEmail} onChange={(event) => setDeactivateEmail(event.target.value)} placeholder={user.email} autoComplete="off" required /></label><label>当前密码<input type="password" value={deactivatePassword} onChange={(event) => setDeactivatePassword(event.target.value)} autoComplete="current-password" required /></label><label className="account-confirmation"><input type="checkbox" checked={deactivateAcknowledged} onChange={(event) => setDeactivateAcknowledged(event.target.checked)} /><span>我理解停用后将立即退出，且历史科学 provenance 不会被删除。</span></label>{feedback(deactivateFeedback)}<div className="account-form-actions"><button className="product-danger-action" disabled={!deactivateAcknowledged || !deactivatePassword || deactivateEmail.trim().toLowerCase() !== user.email.toLowerCase()} type="submit">停用我的账户</button></div></form>
        </section>
      </div>
    </div>
  </section>;
}
