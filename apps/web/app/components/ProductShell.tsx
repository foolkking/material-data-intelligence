"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { type ReactNode, useEffect, useRef, useState } from "react";
import { getAuthUser, logout, type AuthUser } from "../lib/product-api";
import { listProjects, type ProjectSummary } from "../lib/planner-api";
import { ModelSettingsDialog } from "./ModelSettingsPage";

export function ProductShell({ children, projectId }: { children: ReactNode; projectId?: string }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checking, setChecking] = useState(true);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchProjects, setSearchProjects] = useState<ProjectSummary[]>([]);
  const [searchState, setSearchState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [modelSettingsOpen, setModelSettingsOpen] = useState(false);
  const searchTriggerRef = useRef<HTMLButtonElement | null>(null);
  const searchInputRef = useRef<HTMLInputElement | null>(null);
  const searchDialogRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    let active = true;
    void getAuthUser().then((next) => { if (active) setUser(next); }).catch(() => undefined).finally(() => { if (active) setChecking(false); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    setModelSettingsOpen(searchParams.get("settings") === "models");
  }, [searchParams]);

  useEffect(() => {
    const onExpired = () => {
      if (pathname === "/") return;
      const returnTo = `${window.location.pathname}${window.location.search}`;
      router.replace(`/?login=1&returnTo=${encodeURIComponent(returnTo)}`);
    };
    window.addEventListener("mdi:session-expired", onExpired);
    return () => window.removeEventListener("mdi:session-expired", onExpired);
  }, [pathname, router]);

  useEffect(() => {
    const onOpenSearch = () => openSearch();
    window.addEventListener("mdi:open-project-search", onOpenSearch);
    return () => window.removeEventListener("mdi:open-project-search", onOpenSearch);
  });

  async function handleLogout() {
    await logout().catch(() => undefined);
    setUser(null);
    router.push("/");
  }

  function closeSearch() {
    setSearchOpen(false);
    setSearchQuery("");
    window.setTimeout(() => searchTriggerRef.current?.focus(), 0);
  }

  function openSearch() {
    setModelSettingsOpen(false);
    setSearchOpen(true);
    if (searchState === "idle") {
      setSearchState("loading");
      void listProjects().then((items) => { setSearchProjects(items); setSearchState("ready"); }).catch(() => setSearchState("error"));
    }
  }

  function closeModelSettings() {
    setModelSettingsOpen(false);
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      if (url.searchParams.get("settings") === "models") {
        url.searchParams.delete("settings");
        window.history.replaceState(window.history.state, "", url.toString());
      }
    }
  }

  useEffect(() => {
    if (!searchOpen) return;
    const focus = window.requestAnimationFrame(() => searchInputRef.current?.focus());
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); closeSearch(); return; }
      if (event.key !== "Tab" || !searchDialogRef.current) return;
      const nodes = [...searchDialogRef.current.querySelectorAll<HTMLElement>("button, a, input, [tabindex]:not([tabindex='-1'])")]
        .filter((node) => !node.hasAttribute("disabled") && node.getAttribute("aria-hidden") !== "true");
      const first = nodes[0];
      const last = nodes[nodes.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => { window.cancelAnimationFrame(focus); document.removeEventListener("keydown", onKeyDown); };
  }, [searchOpen]);

  const normalizedQuery = searchQuery.trim().toLocaleLowerCase();
  const matchingProjects = searchProjects.filter((item) => !normalizedQuery || [item.name, item.description || ""].join(" ").toLocaleLowerCase().includes(normalizedQuery));

  const isProject = Boolean(projectId);
  const internalPage = pathname !== "/";
  return (
    <div className="product-shell">
      <header className="product-global-bar">
        <Link href="/" className="product-brand" aria-label="Material Data Intelligence 首页">
          <span className="product-brand-mark" aria-hidden="true">M</span>
          <span>材料智能平台</span>
        </Link>
        <div className="product-context">
          {isProject ? <span>项目研究</span> : <span>材料数据与科学分析</span>}
        </div>
        <div className="product-global-actions">
          {internalPage ? <Link href="/" className="product-secondary-action">返回主页</Link> : <>
            <button ref={searchTriggerRef} type="button" className="product-icon-action" aria-label="搜索项目" onClick={openSearch}>⌕</button>
            {checking ? <span className="product-user-skeleton" /> : user ? (
              <div className="product-user-menu"><span className="product-avatar" aria-hidden="true">{(user.displayName || user.email || "研").slice(0, 1)}</span><span className="product-user-name">{user.displayName}</span><button type="button" className="product-link-button" onClick={() => { setSearchOpen(false); setModelSettingsOpen(true); }}>模型设置</button><button type="button" className="product-link-button" onClick={() => void handleLogout()}>退出</button></div>
            ) : <Link href="/?login=1" className="product-login-link">登录</Link>}
          </>}
        </div>
      </header>
      {isProject && <nav className="product-project-nav" aria-label="项目导航">
        <Link className={pathname?.endsWith(`/projects/${projectId}`) ? "active" : ""} href={`/projects/${projectId}`}>概览</Link>
        <Link className={pathname?.includes("/data") ? "active" : ""} href={`/projects/${projectId}/data`}>数据</Link>
        <Link className={pathname?.includes("/research") ? "active" : ""} href={`/projects/${projectId}/research`}>研究</Link>
        <Link className={pathname?.includes("/reports") ? "active" : ""} href={`/projects/${projectId}/reports`}>报告</Link>
      </nav>}
      {searchOpen && <div className="product-search-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) closeSearch(); }}>
        <section ref={searchDialogRef} className="product-search-dialog" role="dialog" aria-modal="true" aria-labelledby="product-search-title">
          <header><div><p className="product-kicker">全局搜索</p><h2 id="product-search-title">查找项目</h2></div><button type="button" className="product-icon-action" aria-label="关闭搜索" onClick={closeSearch}>×</button></header>
          <label htmlFor="product-project-search">项目名称或描述</label>
          <input ref={searchInputRef} id="product-project-search" value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="例如：钙钛矿稳定性" />
          <div className="product-search-results" aria-live="polite">
            {searchState === "loading" ? <p className="product-form-hint" role="status">正在加载项目…</p> : searchState === "error" ? <p className="product-form-error" role="alert">项目暂时无法读取，请稍后重试。</p> : matchingProjects.length ? matchingProjects.map((project) => { const id = project.projectId || project.id; return <div className="product-search-result" key={id}><div><strong>{project.name}</strong><span>{project.description || "材料研究项目"}</span></div><div className="product-row-actions"><Link className="product-secondary-action" href={`/projects/${id}`} onClick={closeSearch}>概览</Link><Link className="product-secondary-action" href={`/projects/${id}/data`} onClick={closeSearch}>数据</Link><Link className="product-secondary-action" href={`/projects/${id}/research`} onClick={closeSearch}>研究</Link></div></div>; }) : <p className="product-form-hint">没有匹配的项目。可以先查看全部项目。</p>}
          </div>
          <footer><Link className="product-primary-action" href="/projects" onClick={closeSearch}>查看全部项目</Link><button type="button" className="product-secondary-action" onClick={closeSearch}>关闭</button></footer>
        </section>
      </div>}
      <ModelSettingsDialog open={modelSettingsOpen} onClose={closeModelSettings} />
      <main className="product-main">{children}</main>
    </div>
  );
}

export function RequireProductAuth({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<"checking" | "ready" | "unauthenticated">("checking");
  useEffect(() => {
    let active = true;
    void getAuthUser().then(() => { if (active) setState("ready"); }).catch(() => { if (active) { setState("unauthenticated"); const returnTo = `${window.location.pathname}${window.location.search}`; router.replace(`/?login=1&returnTo=${encodeURIComponent(returnTo)}`); } });
    return () => { active = false; };
  }, [router]);
  if (state === "checking") return <div className="product-loading" role="status" aria-live="polite">正在恢复登录状态…</div>;
  if (state === "unauthenticated") return null;
  return <>{children}</>;
}
