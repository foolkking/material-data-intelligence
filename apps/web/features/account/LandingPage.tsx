"use client";

import { ProductLink as Link, useProductRouter } from "../../app/components/ProductNavigation";
import { FormEvent, useEffect, useRef, useState } from "react";
import { getAuthUser, login, logout, type AuthUser } from "../../app/lib/product-api";

export function LandingPage() {
  const router = useProductRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [open, setOpen] = useState(false);
  const [sessionExpired, setSessionExpired] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setOpen(params.get("login") === "1");
    setSessionExpired(params.get("reason") === "session-expired");
    void getAuthUser().then(setUser).catch(() => undefined);
  }, []);
  return <main className="landing-page">
    <header className="landing-bar">
      <span className="product-brand"><span className="product-brand-mark">M</span>材料智能平台</span>
      {user ? <div className="landing-account-actions"><span className="landing-account-state">{user.displayName} · 当前账户</span><Link href="/console" className="product-secondary-action">进入控制台</Link><button className="product-link-button" disabled={loggingOut} onClick={() => { setLoggingOut(true); void logout().finally(() => { setUser(null); setLoggingOut(false); }); }}>{loggingOut ? "正在退出…" : "退出登录"}</button></div> : <button className="product-link-button" onClick={() => setOpen(true)}>登录</button>}
    </header>
    <section className="landing-hero">
      <div className="landing-copy">
        <p className="product-kicker">面向材料科研的科学研究工作台</p>
        <h1>材料智能平台</h1>
        <p>将真实材料数据、经过验证的科学工具和可追溯结果放进一个持续的研究项目。查看数据，提出问题，获得有依据的图表、发现与限制。</p>
        {user ? <Link className="product-primary-action" href="/console">进入控制台</Link> : <button className="product-primary-action" onClick={() => setOpen(true)}>开始使用</button>}
      </div>
      <div className="landing-product-view" aria-label="材料科学工作台示意">
        <div className="landing-view-head"><span>Perovskite stability study</span><span>项目研究</span></div>
        <div className="landing-view-body">
          <div className="landing-data-list"><strong>项目数据</strong><span className="selected">materials.csv</span><span>BaTiO3.cif</span><span>AIMD trajectory</span></div>
          <div className="landing-figure"><p>形成能与带隙</p><div className="scatter-demo">{[18,32,47,59,73,86].map((left, index) => <i key={left} style={{left: `${left}%`, bottom: `${18 + index * 10}%`}} />)}</div><strong>主要发现</strong><p>形成能降低时，样本的带隙整体呈上升趋势。</p></div>
        </div>
      </div>
    </section>
    <section className="landing-next" aria-label="工作方式">
      <div><strong>查看数据</strong><p>在项目中浏览表格、结构、轨迹与科学属性。</p></div>
      <div><strong>提出问题</strong><p>用自然语言描述想要验证的材料科学关系。</p></div>
      <div><strong>获得有依据的结果</strong><p>图表、发现、限制与来源过程一起保留。</p></div>
    </section>
    <section className="landing-context-band" aria-labelledby="landing-context-title">
      <div className="landing-section-inner">
        <header className="landing-section-lead">
          <p className="product-kicker">以项目为研究边界</p>
          <h2 id="landing-context-title">数据、分析与结果始终处于同一研究脉络</h2>
          <p>不是把材料数据塞进通用聊天窗口，而是让每一次提问都建立在明确的数据范围和科学语义之上。</p>
        </header>
        <div className="landing-capability-lines">
          <article><strong>专业数据查看</strong><p>直接检查表格属性、晶体结构和模拟轨迹，让数据本身成为页面主角。</p><span>materials.csv · BaTiO3.cif · AIMD trajectory</span></article>
          <article><strong>受约束的科学分析</strong><p>研究问题先转化为可验证的分析方案，再由已注册工具执行，不把任意代码交给模型运行。</p><span>形成能（formation energy）· 带隙（band gap）· 密度</span></article>
          <article><strong>可追溯的研究结果</strong><p>图、表、主要发现与限制一起保存，并可继续查看数据来源和分析过程。</p><span>Figure · Finding · Limitation · Evidence</span></article>
        </div>
      </div>
    </section>
    <section className="landing-result-band" aria-labelledby="landing-result-title">
      <div className="landing-section-inner landing-result-inner">
        <div className="landing-result-copy">
          <p className="product-kicker">科学结果，而不是答案卡片</p>
          <h2 id="landing-result-title">从主要图表开始阅读，也能一路追溯到来源</h2>
          <p>结果按科研阅读顺序组织：图与单位、主要发现、限制、支持输出、方法与依据。技术细节保持可达，但不会抢占研究工作流。</p>
          <dl>
            <div><dt>主结果</dt><dd>清晰呈现变量、单位与样本范围</dd></div>
            <div><dt>科学解释</dt><dd>区分观察、推断与当前限制</dd></div>
            <div><dt>来源与过程</dt><dd>需要时查看数据、工具与输出关系</dd></div>
          </dl>
        </div>
        <figure className="landing-publication-view">
          <figcaption><span>主要结果</span><strong>形成能与带隙的关系</strong><small>64 个钙钛矿样本 · formation_energy (eV/atom) · band_gap (eV)</small></figcaption>
          <div className="landing-publication-plot" aria-label="形成能与带隙散点图示意">
            {[12,24,37,49,63,77,88].map((left, index) => <i key={left} style={{left: `${left}%`, bottom: `${18 + index * 8}%`}} />)}
          </div>
          <div className="landing-publication-finding"><strong>主要发现</strong><p>在当前样本范围内，形成能降低与带隙增大呈中等相关；这一关系不代表因果。</p></div>
        </figure>
      </div>
    </section>
    <section className="landing-final-action" aria-labelledby="landing-final-title">
      <div><p className="product-kicker">开始一个真实研究项目</p><h2 id="landing-final-title">让下一次材料分析从数据事实开始</h2></div>
      {user ? <Link className="product-primary-action" href="/console">进入控制台</Link> : <button className="product-primary-action" onClick={() => setOpen(true)}>登录并开始</button>}
    </section>
    {open && <LoginModal sessionExpired={sessionExpired} onClose={() => setOpen(false)} onLogin={(next) => {
      setUser(next);
      setOpen(false);
      const returnTo = safeProductReturnTo(new URLSearchParams(window.location.search).get("returnTo"));
      if (returnTo) router.replace(returnTo);
    }} />}
  </main>;
}

export function safeProductReturnTo(value: string | null): string | null {
  if (!value || !value.startsWith("/") || value.startsWith("//") || value.includes("\\")) return null;
  try {
    const resolved = new URL(value, window.location.origin);
    return resolved.origin === window.location.origin ? `${resolved.pathname}${resolved.search}${resolved.hash}` : null;
  } catch {
    return null;
  }
}

function LoginModal({ onClose, onLogin, sessionExpired = false }: { onClose: () => void; onLogin: (user: AuthUser) => void; sessionExpired?: boolean }) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLElement | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    triggerRef.current = document.activeElement as HTMLElement;
    const first = dialogRef.current?.querySelector<HTMLInputElement>("input"); first?.focus();
    function keydown(event: KeyboardEvent) {
      if (event.key === "Escape") { onClose(); triggerRef.current?.focus(); }
      if (event.key === "Tab" && dialogRef.current) {
        const nodes = [...dialogRef.current.querySelectorAll<HTMLElement>("button,input,a")].filter((node) => !node.hasAttribute("disabled"));
        const firstNode = nodes[0], lastNode = nodes[nodes.length - 1];
        if (event.shiftKey && document.activeElement === firstNode) { event.preventDefault(); lastNode?.focus(); }
        else if (!event.shiftKey && document.activeElement === lastNode) { event.preventDefault(); firstNode?.focus(); }
      }
    }
    document.addEventListener("keydown", keydown); return () => document.removeEventListener("keydown", keydown);
  }, [onClose]);
  async function submit(event: FormEvent) { event.preventDefault(); setBusy(true); setError(""); try { onLogin(await login(email, password)); } catch (reason) { setError(reason instanceof Error ? reason.message : "登录失败"); } finally { setBusy(false); } }
  return <div className="product-modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.currentTarget === event.target) onClose(); }}>
    <div ref={dialogRef} className="product-modal" role="dialog" aria-modal="true" aria-labelledby="login-title">
      <button className="product-modal-close" onClick={onClose} aria-label="关闭登录窗口">×</button>
      <p className="product-kicker">材料智能平台</p><h2 id="login-title">{sessionExpired ? "登录已过期" : "登录"}</h2><p>{sessionExpired ? "重新登录后将返回刚才的页面；本浏览器中尚未提交的研究草稿会保留。" : "继续你的材料研究项目。"}</p>
      <form onSubmit={(event) => void submit(event)}>
        <label>邮箱<input type="email" autoComplete="username" required value={email} onChange={(event) => setEmail(event.target.value)} /></label>
        <label>密码<input type="password" autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} /></label>
        {error && <p className="product-form-error" role="alert">{error}</p>}
        <button className="product-primary-action" disabled={busy}>{busy ? "正在登录…" : "登录"}</button>
      </form>
    </div>
  </div>;
}
