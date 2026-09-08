"use client";

import { useEffect, useState } from "react";
import { activateAuthAccount } from "../../app/lib/product-api";
import { ProductLink as Link } from "../../shared/layout/ProductNavigation";

export function AccountActivationPage() {
  const [token, setToken] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [complete, setComplete] = useState(false);

  useEffect(() => {
    setToken(new URLSearchParams(window.location.search).get("token") || "");
  }, []);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (password !== confirmation) {
      setError("两次输入的密码不一致。");
      return;
    }
    if (password.length < 12) {
      setError("密码至少需要 12 个字符。");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await activateAuthAccount(token.trim(), password, displayName);
      setComplete(true);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "激活失败，请联系平台管理员重新发起邀请。");
    } finally {
      setBusy(false);
    }
  }

  return <main className="document-page account-activation-page">
    <header className="product-page-heading"><div><p className="product-kicker">账户激活</p><h1>{complete ? "账户已激活" : "完成研究者账户设置"}</h1><p>{complete ? "你的账户已经可以登录，科学项目与历史 provenance 将按授权继续保留。" : "使用平台管理员提供的一次性激活凭证设置登录密码。"}</p></div></header>
    {complete ? <section className="product-state"><h2>欢迎加入材料智能平台</h2><p>激活凭证已消费，不能再次使用。</p><Link className="product-primary-action" href="/projects">进入我的项目</Link></section> : <form className="account-form account-activation-form" onSubmit={submit}>
      <label>激活凭证<input value={token} onChange={(event) => setToken(event.target.value)} autoComplete="off" required /></label>
      <label>显示名称（可选）<input value={displayName} onChange={(event) => setDisplayName(event.target.value)} autoComplete="name" maxLength={160} /></label>
      <label>设置密码<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="new-password" minLength={12} required /></label>
      <label>确认密码<input type="password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} autoComplete="new-password" minLength={12} required /></label>
      {error ? <p className="product-form-error" role="alert">{error}</p> : null}
      <div className="account-form-actions"><button className="product-primary-action" type="submit" disabled={busy || !token.trim()}>{busy ? "正在激活…" : "激活账户"}</button><Link className="product-secondary-action" href="/">返回登录</Link></div>
    </form>}
  </main>;
}
