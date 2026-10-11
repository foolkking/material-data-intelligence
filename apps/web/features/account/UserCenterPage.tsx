"use client";

import { useEffect, useRef, useState } from "react";
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
import { ProductModal } from "../../shared/ui/ObjectManagement";
import { useAccountRequest } from "./use-account-request";

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
const VISIBLE_SESSION_LIMIT = 4;

export function UserCenterPage() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [sessions, setSessions] = useState<AuthSession[]>([]);
  const [sessionsOpen, setSessionsOpen] = useState(false);
  const [showAllSessions, setShowAllSessions] = useState(false);
  const [dialog, setDialog] = useState<"password" | "deactivate" | null>(null);
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
  const [deactivateBusy, setDeactivateBusy] = useState(false);
  const busyOperations = useRef(new Set<string>());
  const sessionsGeneration = useRef(0);
  const sessionToggleRef = useRef<HTMLButtonElement>(null);
  const runRequest = useAccountRequest();

  useEffect(() => {
    if (!dialog) return;
    const bodyOverflow = document.body.style.overflow;
    const rootOverflow = document.documentElement.style.overflow;
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = bodyOverflow;
      document.documentElement.style.overflow = rootOverflow;
    };
  }, [dialog]);

  useEffect(() => {
    let active = true;
    setState("loading");
    void runRequest((signal) => getAuthUser({ signal }), "账户信息读取超时，请重新读取。").then((next) => {
      if (!active) return;
      setUser(next);
      setDisplayName(next.displayName);
      setState("ready");
    }).catch(() => { if (active) setState("error"); });
    return () => {
      active = false;
    };
  }, [accountRetryToken, runRequest]);

  useEffect(() => {
    const generation = ++sessionsGeneration.current;
    setSessionsState("loading");
    void runRequest((signal) => listAuthSessions({ signal }), "登录记录读取超时，请重试。").then((result) => {
      if (generation !== sessionsGeneration.current) return;
      setSessions(result.items);
      setSessionsState("ready");
    }).catch(() => { if (generation === sessionsGeneration.current) setSessionsState("error"); });
    return () => { sessionsGeneration.current++; };
  }, [sessionRetryToken, runRequest]);

  function closeDialog() {
    setDialog(null);
    setCurrentPassword(""); setNewPassword(""); setConfirmPassword("");
    setDeactivatePassword(""); setDeactivateEmail(""); setDeactivateAcknowledged(false);
  }

  async function saveProfile(event: React.FormEvent) {
    event.preventDefault();
    if (busyOperations.current.has("profile") || !displayName.trim()) return;
    busyOperations.current.add("profile");
    setProfileBusy(true);
    setProfileFeedback(null);
    try {
      const next = await runRequest((signal) => updateAuthProfile(displayName.trim(), { signal }), "暂未确认名称是否保存。请稍后重新打开账户页核对。");
      setUser(next);
      setDisplayName(next.displayName);
      setProfileFeedback({ tone: "success", message: "显示名称已更新。" });
    } catch (reason) {
      setProfileFeedback({ tone: "error", message: reason instanceof Error ? reason.message : "资料更新失败。" });
    } finally {
      busyOperations.current.delete("profile");
      setProfileBusy(false);
    }
  }

  async function revokeSession(sessionId: string) {
    if (busyOperations.current.has("sessions") || sessionsState !== "ready") return;
    busyOperations.current.add("sessions");
    setSessionBusy(sessionId);
    setSessionFeedback(null);
    try {
      const result = await runRequest((signal) => revokeAuthSession(sessionId, { signal }), "暂未确认是否退出。请刷新登录记录后核对。");
      if (!result.ok) throw new Error("未能退出该处登录，请重试。");
      sessionsGeneration.current++;
      setSessions((items) => items.filter((item) => item.id !== sessionId));
      setSessionFeedback({ tone: "success", message: "已退出该处登录。" });
      sessionToggleRef.current?.focus();
    } catch (reason) {
      setSessionFeedback({ tone: "error", message: reason instanceof Error ? reason.message : "未能退出该处登录，请重试。" });
    } finally {
      busyOperations.current.delete("sessions");
      setSessionBusy(null);
    }
  }

  async function revokeOthers() {
    if (busyOperations.current.has("sessions") || sessionsState !== "ready") return;
    busyOperations.current.add("sessions");
    setSessionBusy("others");
    setSessionFeedback(null);
    try {
      const result = await runRequest((signal) => revokeOtherAuthSessions({ signal }), "暂未确认是否退出。请刷新登录记录后核对。");
      if (!result.ok) throw new Error("未能退出其他登录，请重试。");
      sessionsGeneration.current++;
      setSessions((items) => items.filter((item) => item.isCurrent));
      setSessionFeedback({ tone: "success", message: `已退出其他 ${result.revokedCount} 处登录，当前登录保持不变。` });
      sessionToggleRef.current?.focus();
    } catch (reason) {
      setSessionFeedback({ tone: "error", message: reason instanceof Error ? reason.message : "未能退出其他登录，请重试。" });
    } finally {
      busyOperations.current.delete("sessions");
      setSessionBusy(null);
    }
  }

  async function changePassword(event: React.FormEvent) {
    event.preventDefault();
    if (busyOperations.current.has("password")) return;
    if (newPassword !== confirmPassword) {
      setPasswordFeedback({ tone: "error", message: "两次输入的新密码不一致。" });
      return;
    }
    if (newPassword.length < 12) {
      setPasswordFeedback({ tone: "error", message: "新密码至少需要 12 个字符。" });
      return;
    }
    setPasswordBusy(true);
    busyOperations.current.add("password");
    setPasswordFeedback(null);
    try {
      const result = await runRequest((signal) => changeAuthPassword(currentPassword, newPassword, { signal }), "暂未确认密码是否更新。下次登录时请先尝试新密码。");
      if (!result.ok) throw new Error("密码未能更新，请重试。");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setSessions((items) => items.filter((item) => item.isCurrent));
      sessionsGeneration.current++;
      setSessionRetryToken((value) => value + 1);
      setPasswordFeedback({ tone: "success", message: "密码已更新，其他登录已退出。" });
      closeDialog();
    } catch (reason) {
      setPasswordFeedback({ tone: "error", message: reason instanceof Error ? reason.message : "密码更新失败。" });
    } finally {
      busyOperations.current.delete("password");
      setPasswordBusy(false);
    }
  }

  async function deactivate(event: React.FormEvent) {
    event.preventDefault();
    if (!user || busyOperations.current.has("deactivate") || !deactivateAcknowledged || !deactivatePassword || deactivateEmail.trim().toLowerCase() !== user.email.toLowerCase()) return;
    busyOperations.current.add("deactivate");
    setDeactivateBusy(true);
    setDeactivateFeedback(null);
    try {
      const result = await runRequest((signal) => deactivateAuthAccount(deactivatePassword, deactivateEmail, { signal }), "暂未确认账户是否停用。请稍后重新打开账户页核对。");
      if (!result.ok) throw new Error("账户未能停用，请重试。");
      window.location.assign("/");
    } catch (reason) {
      setDeactivateFeedback({ tone: "error", message: reason instanceof Error ? reason.message : "账户停用失败。" });
    } finally {
      busyOperations.current.delete("deactivate");
      setDeactivateBusy(false);
    }
  }

  if (state === "loading") return <section className="document-page user-center-page"><div className="product-loading" role="status">正在读取账户…</div></section>;
  if (state === "error" || !user) return <section className="document-page user-center-page"><div className="product-state" role="alert"><h1>账户信息暂时无法读取</h1><p>登录状态或服务连接发生变化；账户数据没有被修改。</p><div className="product-row-actions"><button className="product-primary-action" type="button" onClick={() => setAccountRetryToken((value) => value + 1)}>重新读取</button><Link className="product-secondary-action" href="/console">返回控制台</Link></div></div></section>;

  const otherSessions = sessions.filter((session) => !session.isCurrent);
  const orderedSessions = [
        ...sessions.filter((session) => session.isCurrent),
        ...otherSessions.sort((left, right) => (Date.parse(right.lastSeenAt) || 0) - (Date.parse(left.lastSeenAt) || 0)),
      ];
  const visibleSessions = showAllSessions ? orderedSessions : orderedSessions.slice(0, VISIBLE_SESSION_LIMIT);
  const feedback = (value: Feedback) => value ? <p className={value.tone === "success" ? "product-form-success" : "product-form-error"} role={value.tone === "error" ? "alert" : "status"}>{value.message}</p> : null;

  return <section className="document-page user-center-page">
    <header className="product-page-heading user-center-heading">
      <div><h1>账户设置</h1><p>管理个人资料与登录安全。</p></div>
      <Link className="product-secondary-action" href="/account?settings=models">模型设置</Link>
    </header>

    <div className="user-center-sections">
      <section id="profile" className="user-center-section" aria-labelledby="profile-title">
        <header><h2 id="profile-title">个人资料</h2><p>让项目伙伴知道你是谁。</p></header>
        <div className="account-profile-fields">
          <div className="account-email"><span>登录邮箱</span><strong>{user.email}</strong><small>邮箱暂不支持修改</small></div>
          <form className="account-form" onSubmit={saveProfile}>
            <label>显示名称<input value={displayName} disabled={profileBusy} onChange={(event) => setDisplayName(event.target.value)} autoComplete="name" maxLength={160} required /></label>
            {feedback(profileFeedback)}
            <div className="account-form-actions"><button className="product-primary-action" disabled={profileBusy || !displayName.trim() || displayName.trim() === user.displayName} type="submit">{profileBusy ? "正在保存…" : "保存名称"}</button></div>
          </form>
        </div>
      </section>

      <section className="user-center-section" aria-labelledby="security-title">
        <header><h2 id="security-title">登录安全</h2></header>
        <div id="password" className="account-setting-row">
          <div><h3>密码</h3><p>修改后，其他登录会自动退出。</p></div>
          <button className="product-secondary-action" disabled={passwordBusy || sessionBusy !== null} type="button" onClick={() => { setPasswordFeedback(null); setDialog("password"); }}>修改密码</button>
        </div>
        {dialog !== "password" ? feedback(passwordFeedback) : null}
        <div id="sessions" className="account-setting-row">
          <div><h3>登录记录</h3><p>{sessionsState === "ready" ? sessions.some((session) => session.isCurrent) ? otherSessions.length ? `当前浏览器与其他 ${otherSessions.length} 处登录` : "仅当前浏览器已登录" : `${sessions.length} 处有效登录` : "查看并退出不再使用的登录。"}</p></div>
          <button ref={sessionToggleRef} className="product-secondary-action" type="button" aria-expanded={sessionsOpen} aria-controls="account-sessions" onClick={() => setSessionsOpen((value) => !value)}>{sessionsOpen ? "收起记录" : "查看记录"}</button>
        </div>
        {sessionsState === "loading" ? <p className="product-form-hint" role="status">正在读取登录记录…</p> : null}
        {sessionsState === "error" ? <div className="account-recovery-state" role="alert"><p className="product-form-error">登录记录暂时无法读取。{sessions.length ? "下方保留上次记录。" : ""}</p><button className="product-secondary-action" disabled={passwordBusy || sessionBusy !== null} type="button" onClick={() => setSessionRetryToken((value) => value + 1)}>重新读取记录</button></div> : null}
        {feedback(sessionFeedback)}
        <div id="account-sessions" hidden={!sessionsOpen} className="account-sessions-detail">
          <p className="product-form-hint">每条记录代表一次仍有效的登录，同一设备可能有多条记录。</p>
          {sessions.length ? <>
            <div className="account-session-list">{visibleSessions.map((session) => <article key={session.id}>
              <div><strong>{session.isCurrent ? "当前浏览器" : `登录于 ${dateLabel(session.createdAt)}`}</strong><span>最近使用 {dateLabel(session.lastSeenAt)}</span></div>
              {session.isCurrent ? <span className="account-current-marker">正在使用</span> : <button className="product-secondary-action" disabled={sessionBusy !== null || passwordBusy || sessionsState !== "ready"} type="button" onClick={() => void revokeSession(session.id)}>{sessionBusy === session.id ? "正在退出…" : "退出此登录"}</button>}
            </article>)}</div>
            {sessions.length > VISIBLE_SESSION_LIMIT ? <div className="account-session-toggle"><span>已显示 {visibleSessions.length} / {sessions.length} 条</span><button className="product-secondary-action" type="button" aria-expanded={showAllSessions} onClick={() => setShowAllSessions((value) => !value)}>{showAllSessions ? "只看最近记录" : `查看全部（${sessions.length}）`}</button></div> : null}
          </> : sessionsState === "ready" ? <p className="product-form-hint">没有查到有效的登录记录，请刷新后核对。</p> : null}
          <div className="account-form-actions">
            {otherSessions.length ? <button className="product-secondary-action" disabled={sessionBusy !== null || passwordBusy || sessionsState !== "ready"} type="button" onClick={() => void revokeOthers()}>{sessionBusy === "others" ? "正在退出…" : "退出其他所有登录"}</button> : null}
            {sessionsState === "ready" ? <button className="product-secondary-action" disabled={sessionBusy !== null || passwordBusy} type="button" onClick={() => { setSessionFeedback(null); setSessionRetryToken((value) => value + 1); }}>刷新记录</button> : null}
          </div>
        </div>
      </section>

      <section id="deactivate" className="user-center-section" aria-labelledby="deactivate-title">
        <div className="account-setting-row">
          <div><h2 id="deactivate-title">停用账户</h2><p>停用后无法登录，已有研究数据与结果仍会保留。</p></div>
          <button className="product-secondary-action" disabled={deactivateBusy || passwordBusy} type="button" onClick={() => { setDeactivateFeedback(null); setDialog("deactivate"); }}>停用账户</button>
        </div>
        {dialog !== "deactivate" ? feedback(deactivateFeedback) : null}
      </section>
    </div>

    {dialog === "password" ? <ProductModal title="修改密码" eyebrow="账户设置" description="新密码至少 12 个字符。更新后保留当前登录，其他登录会自动退出。" onClose={closeDialog} footer={<>
      <button type="button" className="product-secondary-action" onClick={closeDialog}>取消</button>
      <button form="account-password-form" className="product-primary-action" disabled={passwordBusy || !currentPassword || !newPassword || !confirmPassword} type="submit">{passwordBusy ? "正在更新…" : "更新密码"}</button>
    </>}>
      <form id="account-password-form" className="account-form" onSubmit={changePassword}>
        <label>当前密码<input type="password" value={currentPassword} disabled={passwordBusy} onChange={(event) => setCurrentPassword(event.target.value)} autoComplete="current-password" required /></label>
        <label>新密码<input type="password" value={newPassword} disabled={passwordBusy} onChange={(event) => setNewPassword(event.target.value)} autoComplete="new-password" minLength={12} required /></label>
        <label>确认新密码<input type="password" value={confirmPassword} disabled={passwordBusy} onChange={(event) => setConfirmPassword(event.target.value)} autoComplete="new-password" minLength={12} required /></label>
        {feedback(passwordFeedback)}
      </form>
    </ProductModal> : null}
    {dialog === "deactivate" ? <ProductModal title="停用账户" eyebrow="账户设置" description="你将立即退出，之后无法使用此账户登录。已有研究数据、结果及其来源记录仍会保留。" onClose={closeDialog} footer={<>
      <button className="product-secondary-action" type="button" onClick={closeDialog}>保留账户</button>
      <button form="account-deactivate-form" className="product-danger-action" disabled={deactivateBusy || !deactivateAcknowledged || !deactivatePassword || deactivateEmail.trim().toLowerCase() !== user.email.toLowerCase()} type="submit">{deactivateBusy ? "正在停用…" : "确认停用"}</button>
    </>}>
      <form id="account-deactivate-form" className="account-form" onSubmit={deactivate}>
        <p className="account-deactivate-identity">当前账户：{user.email}</p>
        <label>输入完整邮箱确认<input type="email" value={deactivateEmail} disabled={deactivateBusy} onChange={(event) => setDeactivateEmail(event.target.value)} autoComplete="off" required /></label>
        <label>当前密码<input type="password" value={deactivatePassword} disabled={deactivateBusy} onChange={(event) => setDeactivatePassword(event.target.value)} autoComplete="current-password" required /></label>
        <label className="account-confirmation"><input type="checkbox" checked={deactivateAcknowledged} disabled={deactivateBusy} onChange={(event) => setDeactivateAcknowledged(event.target.checked)} /><span>我了解停用后将无法登录，已有研究数据不会被删除。</span></label>
        {feedback(deactivateFeedback)}
      </form>
    </ProductModal> : null}
  </section>;
}
