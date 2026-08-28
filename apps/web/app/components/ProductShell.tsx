"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { type ReactNode, useEffect, useRef, useState } from "react";
import { getAuthUser, logout, type AuthUser } from "../lib/product-api";
import { searchProduct, type ProductSearchItem } from "../lib/planner-api";
import { ModelSettingsDialog } from "./ModelSettingsPage";

export function ProductShell({ children, projectId }: { children: ReactNode; projectId?: string }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checking, setChecking] = useState(true);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchItems, setSearchItems] = useState<ProductSearchItem[]>([]);
  const [searchState, setSearchState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [modelSettingsOpen, setModelSettingsOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const searchTriggerRef = useRef<HTMLButtonElement | null>(null);
  const searchInputRef = useRef<HTMLInputElement | null>(null);
  const searchDialogRef = useRef<HTMLElement | null>(null);
  const accountRef = useRef<HTMLDivElement | null>(null);
  const accountTriggerRef = useRef<HTMLButtonElement | null>(null);
  const accountMenuRef = useRef<HTMLDivElement | null>(null);

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
    setAccountOpen(false);
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
    setAccountOpen(false);
    setSearchOpen(true);
    setSearchState("loading");
  }

  function closeAccount(restoreFocus = false) {
    setAccountOpen(false);
    if (restoreFocus) window.requestAnimationFrame(() => accountTriggerRef.current?.focus());
  }

  function openModelSettings() {
    setSearchOpen(false);
    setAccountOpen(false);
    setModelSettingsOpen(true);
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

  useEffect(() => {
    if (!searchOpen) return;
    const timer = window.setTimeout(() => {
      setSearchState("loading");
      void searchProduct(searchQuery).then((result) => {
        setSearchItems(result.items);
        setSearchState("ready");
      }).catch(() => setSearchState("error"));
    }, searchQuery.trim() ? 180 : 0);
    return () => window.clearTimeout(timer);
  }, [searchOpen, searchQuery]);

  useEffect(() => {
    if (!accountOpen) return;
    accountMenuRef.current?.querySelector<HTMLElement>("[role='menuitem']")?.focus();
    const onPointerDown = (event: PointerEvent) => {
      if (!accountRef.current?.contains(event.target as Node)) closeAccount(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        closeAccount(true);
        return;
      }
      if (event.key === "Tab") {
        closeAccount(false);
        return;
      }
      const items = Array.from(accountMenuRef.current?.querySelectorAll<HTMLElement>("[role='menuitem']") || []);
      if (!items.length || !["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const current = Math.max(0, items.indexOf(document.activeElement as HTMLElement));
      const next = event.key === "Home" ? 0 : event.key === "End" ? items.length - 1 : event.key === "ArrowDown" ? (current + 1) % items.length : (current - 1 + items.length) % items.length;
      items[next]?.focus();
    };
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [accountOpen]);

  useEffect(() => {
    setSearchOpen(false);
    setAccountOpen(false);
  }, [pathname]);

  const matchingItems = searchItems;
  const kindLabels: Record<ProductSearchItem["kind"], string> = {
    project: "项目",
    dataset: "数据集",
    scientific_object: "科学对象",
    research: "研究会话",
    report: "科学报告",
    result: "ScientificResult",
  };

  const isProject = Boolean(projectId);
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
          <Link className="product-secondary-action product-task-link" href="/tasks">任务</Link>
          <button ref={searchTriggerRef} type="button" className="product-icon-action" aria-label="搜索项目" onClick={openSearch}>⌕</button>
          {checking ? <span className="product-user-skeleton" aria-label="正在读取账户" /> : user ? (
            <div ref={accountRef} className="product-account">
              <button ref={accountTriggerRef} type="button" className="product-account-trigger" aria-haspopup="menu" aria-controls="product-account-menu" aria-expanded={accountOpen} onClick={() => setAccountOpen((value) => !value)}>
                <span className="product-avatar" aria-hidden="true">{(user.displayName || user.email || "研").slice(0, 1)}</span>
                <span className="product-user-name">{user.displayName}</span>
                <span className="product-account-chevron" aria-hidden="true">⌄</span>
                <span className="sr-only">{accountOpen ? "关闭账户菜单" : "打开账户菜单"}</span>
              </button>
              {accountOpen ? <div ref={accountMenuRef} id="product-account-menu" className="product-account-menu" role="menu" aria-label="账户菜单">
                <div className="product-account-identity"><strong>{user.displayName}</strong><span>{user.email}</span></div>
                <button type="button" role="menuitem" onClick={openModelSettings}>模型设置</button>
                <button type="button" role="menuitem" onClick={() => void handleLogout()}>退出登录</button>
              </div> : null}
            </div>
          ) : <Link href="/?login=1" className="product-login-link">登录</Link>}
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
          <header><div><p className="product-kicker">全局搜索</p><h2 id="product-search-title">查找科学工作</h2></div><button type="button" className="product-icon-action" aria-label="关闭搜索" onClick={closeSearch}>×</button></header>
          <label htmlFor="product-project-search">项目、数据、研究或报告</label>
          <input ref={searchInputRef} id="product-project-search" value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="例如：硅、band_gap、研究报告" />
          <div className="product-search-results" aria-live="polite">
            {searchState === "loading" ? <p className="product-form-hint" role="status">正在搜索…</p> : searchState === "error" ? <p className="product-form-error" role="alert">搜索暂时无法读取，请稍后重试。</p> : matchingItems.length ? matchingItems.map((item) => <div className="product-search-result" key={`${item.kind}-${item.id}`}><div><strong>{item.title}</strong><span>{kindLabels[item.kind]} · {item.subtitle}</span></div><div className="product-row-actions"><Link className="product-secondary-action" href={item.href} onClick={closeSearch}>打开</Link>{item.kind === "project" ? <><Link className="product-secondary-action" href={`/projects/${item.projectId}/data`} onClick={closeSearch}>数据</Link><Link className="product-secondary-action" href={`/projects/${item.projectId}/research`} onClick={closeSearch}>研究</Link></> : null}</div></div>) : <p className="product-form-hint">没有匹配的科学工作。</p>}
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
