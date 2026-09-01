"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { createContext, type ReactNode, useCallback, useContext, useEffect, useRef, useState } from "react";
import {
  createSavedProductSearch,
  deleteSavedProductSearch,
  executeSavedProductSearch,
  getAuthUser,
  listSavedProductSearches,
  listResearchSessions,
  logout,
  type AuthUser,
  type SavedProductSearch,
  updateSavedProductSearch,
} from "../lib/product-api";
import {
  getProjectHistory,
  searchProduct,
  type ProductSearchItem,
} from "../lib/planner-api";
import { getProductTaskFeed } from "../lib/task-center-data";
import { ModelSettingsDialog } from "./ModelSettingsPage";
import { ProductLink as Link, useProductNavigation, useProductRouter } from "./ProductNavigation";

const ProductShellFrameContext = createContext(false);
const ProductAuthFrameContext = createContext(false);

export function ProductShell({ children, projectId }: { children: ReactNode; projectId?: string }) {
  const framed = useContext(ProductShellFrameContext);
  if (framed) return <>{children}</>;
  return <ProductShellFrame projectId={projectId}>{children}</ProductShellFrame>;
}

function ProductShellFrame({ children, projectId }: { children: ReactNode; projectId?: string }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useProductRouter();
  const navigation = useProductNavigation();
  const hasSharedNavigation = navigation !== null;
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checking, setChecking] = useState(true);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchKind, setSearchKind] = useState<ProductSearchItem["kind"] | "">("");
  const [searchStatus, setSearchStatus] = useState<"active" | "archived" | "trashed" | "all">("all");
  const [searchProject, setSearchProject] = useState("");
  const [searchItems, setSearchItems] = useState<ProductSearchItem[]>([]);
  const [searchCount, setSearchCount] = useState(0);
  const [searchTruncated, setSearchTruncated] = useState(false);
  const [searchState, setSearchState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [savedSearches, setSavedSearches] = useState<SavedProductSearch[]>([]);
  const [savedSearchState, setSavedSearchState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [selectedSavedSearchId, setSelectedSavedSearchId] = useState("");
  const [savedSearchEditing, setSavedSearchEditing] = useState(false);
  const [savedSearchName, setSavedSearchName] = useState("");
  const [savedSearchMutation, setSavedSearchMutation] = useState(false);
  const [savedSearchError, setSavedSearchError] = useState("");
  const [modelSettingsOpen, setModelSettingsOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const [online, setOnline] = useState(true);
  const [projectName, setProjectName] = useState("");
  const searchTriggerRef = useRef<HTMLButtonElement | null>(null);
  const searchInputRef = useRef<HTMLInputElement | null>(null);
  const searchDialogRef = useRef<HTMLElement | null>(null);
  const searchRequestSeqRef = useRef(0);
  const skipNextFilterSearchRef = useRef(false);
  const researchSessionsPrefetchRef = useRef(new Set<string>());
  const taskFeedPrefetchRef = useRef(false);
  const routePrefetchAtRef = useRef(new Map<string, number>());
  const projectHistoryWarmRef = useRef(new Map<
    string,
    { at: number; promise: ReturnType<typeof getProjectHistory> }
  >());
  const currentProjectIdRef = useRef<string | undefined>(projectId);
  const accountRef = useRef<HTMLDivElement | null>(null);
  const accountTriggerRef = useRef<HTMLButtonElement | null>(null);
  const accountMenuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let active = true;
    void getAuthUser().then((next) => { if (active) setUser(next); }).catch(() => undefined).finally(() => { if (active) setChecking(false); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    const sync = () => setOnline(window.navigator.onLine !== false);
    const onOnline = () => setOnline(true);
    const onOffline = () => setOnline(false);
    sync();
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
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
  }, []);

  useEffect(() => {
    const onShortcut = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        if (searchOpen) searchInputRef.current?.focus();
        else openSearch();
      }
    };
    window.addEventListener("keydown", onShortcut);
    return () => window.removeEventListener("keydown", onShortcut);
  }, [searchOpen]);

  async function handleLogout() {
    setAccountOpen(false);
    await logout().catch(() => undefined);
    setUser(null);
    router.push("/");
  }

  function closeSearch() {
    setSearchOpen(false);
    setSearchQuery("");
    setSearchKind("");
    setSearchStatus("all");
    setSearchProject("");
    setSearchItems([]);
    setSearchCount(0);
    setSearchTruncated(false);
    setSearchState("idle");
    setSelectedSavedSearchId("");
    setSavedSearchEditing(false);
    setSavedSearchName("");
    setSavedSearchError("");
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
      const nodes = [...searchDialogRef.current.querySelectorAll<HTMLElement>("button, a, input, select, [tabindex]:not([tabindex='-1'])")]
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
    if (!searchOpen || !user) return;
    let active = true;
    setSavedSearchState("loading");
    setSavedSearchError("");
    void listSavedProductSearches()
      .then((items) => {
        if (!active) return;
        setSavedSearches(items);
        setSavedSearchState("ready");
        setSelectedSavedSearchId((current) =>
          items.some((item) => item.id === current) ? current : "",
        );
      })
      .catch(() => {
        if (!active) return;
        setSavedSearchState("error");
        setSavedSearchError("已保存检索暂时无法读取。");
      });
    return () => {
      active = false;
    };
  }, [searchOpen, user]);

  useEffect(() => {
    if (!searchOpen) {
      searchRequestSeqRef.current += 1;
      return;
    }
    if (skipNextFilterSearchRef.current) {
      skipNextFilterSearchRef.current = false;
      return;
    }
    const requestSeq = ++searchRequestSeqRef.current;
    const timer = window.setTimeout(() => {
      setSearchState("loading");
      const options = {
        ...(searchProject ? { projectId: searchProject } : {}),
        ...(searchKind ? { kind: searchKind } : {}),
        ...(searchStatus !== "all" ? { status: searchStatus } : {}),
      };
      const request = Object.keys(options).length ? searchProduct(searchQuery, options) : searchProduct(searchQuery);
      void request.then((result) => {
        if (requestSeq !== searchRequestSeqRef.current) return;
        setSearchItems(result.items);
        setSearchCount(result.count);
        setSearchTruncated(Boolean(result.truncated));
        setSearchState("ready");
      }).catch(() => {
        if (requestSeq === searchRequestSeqRef.current) setSearchState("error");
      });
    }, searchQuery.trim() ? 180 : 0);
    return () => {
      window.clearTimeout(timer);
      if (requestSeq === searchRequestSeqRef.current) searchRequestSeqRef.current += 1;
    };
  }, [searchKind, searchOpen, searchProject, searchQuery, searchStatus]);

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

  const warmProjectHistory = useCallback((targetProjectId: string) => {
    const now = Date.now();
    const cached = projectHistoryWarmRef.current.get(targetProjectId);
    if (cached && now - cached.at < 1_500) return cached.promise;
    const promise = getProjectHistory(targetProjectId).catch((error) => {
      projectHistoryWarmRef.current.delete(targetProjectId);
      throw error;
    });
    projectHistoryWarmRef.current.set(targetProjectId, { at: now, promise });
    return promise;
  }, []);

  useEffect(() => {
    if (currentProjectIdRef.current !== projectId) {
      currentProjectIdRef.current = projectId;
      setProjectName("");
    }
    if (!projectId) {
      if (hasSharedNavigation) return;
      const timeout = window.setTimeout(() => {
        router.prefetch("/projects");
        router.prefetch("/tasks");
        router.prefetch("/notifications");
        router.prefetch("/trash");
      }, 240);
      return () => window.clearTimeout(timeout);
    }
    let active = true;
    const timeout = window.setTimeout(() => {
      // RootLayout supplies ProductNavigationProvider in production. Its
      // ProductLink owns route prefetch, so do not issue a second eager RSC
      // campaign from the shell. The fallback keeps isolated/legacy mounts
      // functional without duplicating requests in the real product.
      if (!hasSharedNavigation) {
        const projectRoot = `/projects/${projectId}`;
        [
          projectRoot,
          `${projectRoot}/data`,
          `${projectRoot}/research`,
          `${projectRoot}/reports`,
          "/tasks",
          "/notifications",
        ].forEach((href) => router.prefetch(href));
      }
      void warmProjectHistory(projectId)
        .then((history) => {
          if (active) setProjectName(history.project.name);
        })
        .catch(() => undefined);
      // Research is a primary project surface. Warm its bounded session
      // inventory alongside the history ledger so a normal Data → Research
      // transition does not wait for a second round trip after the route has
      // already committed. The API helper owns a short TTL and invalidates on
      // session mutations, so this does not pin stale lifecycle state.
      if (!researchSessionsPrefetchRef.current.has(projectId)) {
        researchSessionsPrefetchRef.current.add(projectId);
        void listResearchSessions(projectId).catch(() => {
          researchSessionsPrefetchRef.current.delete(projectId);
        });
      }
    }, 240);
    return () => {
      active = false;
      window.clearTimeout(timeout);
    };
  }, [hasSharedNavigation, projectId, router, warmProjectHistory]);

  const matchingItems = searchItems;
  async function applySavedSearch(savedSearchId: string) {
    setSelectedSavedSearchId(savedSearchId);
    const savedSearch = savedSearches.find((item) => item.id === savedSearchId);
    if (!savedSearch) return;
    skipNextFilterSearchRef.current = true;
    setSearchQuery(savedSearch.query);
    setSearchKind(savedSearch.type || "");
    setSearchProject(savedSearch.project || "");
    setSearchStatus(savedSearch.status || "all");
    setSavedSearchEditing(false);
    setSavedSearchError("");
    setSearchState("loading");
    const requestSeq = ++searchRequestSeqRef.current;
    try {
      const result = await executeSavedProductSearch(savedSearchId);
      if (requestSeq !== searchRequestSeqRef.current) return;
      setSearchItems(result.items);
      setSearchCount(result.count);
      setSearchTruncated(Boolean(result.truncated));
      setSearchState("ready");
    } catch (reason) {
      if (requestSeq !== searchRequestSeqRef.current) return;
      setSearchState("error");
      setSavedSearchError(
        reason instanceof Error ? reason.message : "执行已保存检索失败。",
      );
    }
    window.requestAnimationFrame(() => searchInputRef.current?.focus());
  }

  async function saveCurrentSearch() {
    const name = savedSearchName.trim();
    if (!name) {
      setSavedSearchError("请输入检索名称。");
      return;
    }
    setSavedSearchMutation(true);
    setSavedSearchError("");
    try {
      const saved = await createSavedProductSearch({
        name,
        query: searchQuery,
        ...(searchKind ? { type: searchKind } : {}),
        ...(searchProject ? { project: searchProject } : {}),
        status: searchStatus,
      });
      setSavedSearches((items) => [
        saved,
        ...items.filter((item) => item.id !== saved.id),
      ]);
      setSelectedSavedSearchId(saved.id);
      setSavedSearchEditing(false);
      setSavedSearchName("");
    } catch (reason) {
      setSavedSearchError(
        reason instanceof Error ? reason.message : "保存检索失败。",
      );
    } finally {
      setSavedSearchMutation(false);
    }
  }

  async function removeSelectedSavedSearch() {
    if (!selectedSavedSearchId) return;
    const selected = savedSearches.find(
      (item) => item.id === selectedSavedSearchId,
    );
    if (
      typeof window !== "undefined" &&
      !window.confirm(`删除已保存检索“${selected?.name || "未命名检索"}”？`)
    )
      return;
    setSavedSearchMutation(true);
    setSavedSearchError("");
    try {
      await deleteSavedProductSearch(selectedSavedSearchId);
      setSavedSearches((items) =>
        items.filter((item) => item.id !== selectedSavedSearchId),
      );
      setSelectedSavedSearchId("");
    } catch (reason) {
      setSavedSearchError(
        reason instanceof Error ? reason.message : "删除检索失败。",
      );
    } finally {
      setSavedSearchMutation(false);
    }
  }

  async function updateSelectedSavedSearch() {
    if (!selectedSavedSearchId) return;
    setSavedSearchMutation(true);
    setSavedSearchError("");
    try {
      const updated = await updateSavedProductSearch(selectedSavedSearchId, {
        query: searchQuery,
        type: searchKind || null,
        project: searchProject || null,
        status: searchStatus,
      });
      setSavedSearches((items) =>
        items.map((item) => (item.id === updated.id ? updated : item)),
      );
    } catch (reason) {
      setSavedSearchError(
        reason instanceof Error ? reason.message : "更新检索失败。",
      );
    } finally {
      setSavedSearchMutation(false);
    }
  }

  const kindLabels: Record<ProductSearchItem["kind"], string> = {
    project: "项目",
    dataset: "数据集",
    scientific_object: "科学对象",
    research: "研究会话",
    report: "科学报告",
    result: "科学结果",
  };
  const searchStatusLabel = (status?: string | null) =>
    ({
      active: "当前",
      current: "当前",
      archived: "已归档",
      trashed: "回收站",
      stale: "历史来源",
      source_missing: "来源不可用",
      invalidated: "已失效",
    })[String(status || "active").toLowerCase()] || "当前";

  const isProject = Boolean(projectId);
  const pendingProjectPath =
    navigation?.intent?.targetKey.split("?", 1)[0] || "";
  const projectNavClass = (href: string, active: boolean) =>
    [
      active ? "active" : "",
      pendingProjectPath === href ? "pending" : "",
    ]
      .filter(Boolean)
      .join(" ");
  const prefetchRoute = (href: string, surface: "overview" | "data" | "research" | "reports") => {
    const now = Date.now();
    const lastPrefetchAt = routePrefetchAtRef.current.get(href) || 0;
    if (now - lastPrefetchAt < 1_500) return;
    routePrefetchAtRef.current.set(href, now);
    // ProductLink already delegates route prefetch to the shared navigation
    // provider. Only isolated shell mounts need this compatibility fallback.
    if (!hasSharedNavigation) router.prefetch?.(href);
    if (!projectId || surface === "reports") return;
    // Pointer enter and keyboard focus commonly fire for the same intent.
    // Coalesce that burst while the API cache continues to own freshness.
    void warmProjectHistory(projectId).catch(() => undefined);
    if (surface === "research") {
      if (!researchSessionsPrefetchRef.current.has(projectId)) {
        researchSessionsPrefetchRef.current.add(projectId);
        void listResearchSessions(projectId).catch(() => {
          researchSessionsPrefetchRef.current.delete(projectId);
        });
      }
    }
  };
  const prefetchTaskSurface = (href: "/tasks" | "/notifications") => {
    if (!hasSharedNavigation) router.prefetch?.(href);
    if (taskFeedPrefetchRef.current) return;
    taskFeedPrefetchRef.current = true;
    void getProductTaskFeed().catch(() => {
      taskFeedPrefetchRef.current = false;
    });
  };
  return (
    <ProductShellFrameContext.Provider value>
    <div className="product-shell">
      <header className="product-global-bar">
        <Link href="/" className="product-brand" aria-label="Material Data Intelligence 首页">
          <span className="product-brand-mark" aria-hidden="true">M</span>
          <span>材料智能平台</span>
        </Link>
        <div className="product-context" title={projectName || undefined}>
          {isProject
            ? <span>{projectName ? `项目 · ${projectName}` : "项目研究"}</span>
            : <span>材料数据与科学分析</span>}
        </div>
        <div className="product-global-actions">
          <Link className="product-secondary-action product-task-link" href="/tasks" onMouseEnter={() => prefetchTaskSurface("/tasks")} onFocus={() => prefetchTaskSurface("/tasks")}>任务</Link>
          <Link className="product-secondary-action product-task-link" href="/notifications" onMouseEnter={() => prefetchTaskSurface("/notifications")} onFocus={() => prefetchTaskSurface("/notifications")}>通知</Link>
          <button ref={searchTriggerRef} type="button" className="product-icon-action" aria-label="搜索科学工作" onClick={openSearch}>⌕</button>
          {checking ? <span className="product-user-skeleton" aria-label="正在读取账户" /> : user ? (
            <div ref={accountRef} className="product-account">
              <button ref={accountTriggerRef} type="button" className="product-account-trigger" aria-haspopup="menu" aria-controls={accountOpen ? "product-account-menu" : undefined} aria-expanded={accountOpen} onClick={() => setAccountOpen((value) => !value)}>
                <span className="product-avatar" aria-hidden="true">{(user.displayName || user.email || "研").slice(0, 1)}</span>
                <span className="product-user-name">{user.displayName}</span>
                <span className="product-account-chevron" aria-hidden="true">⌄</span>
                <span className="sr-only">{accountOpen ? "关闭账户菜单" : "打开账户菜单"}</span>
              </button>
              {accountOpen ? <div ref={accountMenuRef} id="product-account-menu" className="product-account-menu" role="menu" aria-label="账户菜单">
                <div className="product-account-identity"><strong>{user.displayName}</strong><span>{user.email}</span></div>
                <Link role="menuitem" href="/trash" onClick={() => closeAccount(false)}>回收站</Link>
                <button type="button" role="menuitem" onClick={openModelSettings}>模型设置</button>
                <button type="button" role="menuitem" onClick={() => void handleLogout()}>退出登录</button>
              </div> : null}
            </div>
          ) : <Link href="/?login=1" className="product-login-link">登录</Link>}
        </div>
      </header>
      {isProject && <nav
        className="product-project-nav"
        aria-label={`${projectName || "当前项目"}导航`}
        aria-busy={Boolean(pendingProjectPath)}
        data-navigation-pending={pendingProjectPath || undefined}
      >
        <Link className={projectNavClass(`/projects/${projectId}`, Boolean(pathname?.endsWith(`/projects/${projectId}`)))} aria-current={pathname?.endsWith(`/projects/${projectId}`) ? "page" : undefined} href={`/projects/${projectId}`} prefetch onMouseEnter={() => prefetchRoute(`/projects/${projectId}`, "overview")} onFocus={() => prefetchRoute(`/projects/${projectId}`, "overview")}>概览</Link>
        <Link className={projectNavClass(`/projects/${projectId}/data`, Boolean(pathname?.includes("/data")))} aria-current={pathname?.includes("/data") ? "page" : undefined} href={`/projects/${projectId}/data`} prefetch onMouseEnter={() => prefetchRoute(`/projects/${projectId}/data`, "data")} onFocus={() => prefetchRoute(`/projects/${projectId}/data`, "data")}>数据</Link>
        <Link className={projectNavClass(`/projects/${projectId}/research`, Boolean(pathname?.includes("/research")))} aria-current={pathname?.includes("/research") ? "page" : undefined} href={`/projects/${projectId}/research`} prefetch onMouseEnter={() => prefetchRoute(`/projects/${projectId}/research`, "research")} onFocus={() => prefetchRoute(`/projects/${projectId}/research`, "research")}>研究</Link>
        <Link className={projectNavClass(`/projects/${projectId}/reports`, Boolean(pathname?.includes("/reports")))} aria-current={pathname?.includes("/reports") ? "page" : undefined} href={`/projects/${projectId}/reports`} prefetch onMouseEnter={() => prefetchRoute(`/projects/${projectId}/reports`, "reports")} onFocus={() => prefetchRoute(`/projects/${projectId}/reports`, "reports")}>报告</Link>
      </nav>}
      {!online ? <div className="product-connectivity-banner" role="status" aria-live="polite"><strong>连接已中断</strong><span>服务器上的研究可能仍在继续；恢复网络后可从任务中心重新同步。</span></div> : null}
      {searchOpen && <div className="product-search-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) closeSearch(); }}>
        <section ref={searchDialogRef} className="product-search-dialog" role="dialog" aria-modal="true" aria-labelledby="product-search-title">
          <header><div><p className="product-kicker">全局搜索</p><h2 id="product-search-title">查找科学工作</h2></div><button type="button" className="product-icon-action" aria-label="关闭搜索" onClick={closeSearch}>×</button></header>
          <div className="product-search-input-label"><label htmlFor="product-project-search">项目、数据、研究或报告</label><kbd>Ctrl/⌘ K</kbd></div>
          <div className="product-search-input-wrap">
            <input ref={searchInputRef} id="product-project-search" aria-label="搜索项目、数据、研究或报告" value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="例如：硅、band_gap、研究报告" aria-describedby="product-search-help" />
            {searchQuery ? <button type="button" className="product-search-clear" aria-label="清除搜索" onClick={() => { setSearchQuery(""); searchInputRef.current?.focus(); }}>×</button> : null}
          </div>
          <p id="product-search-help" className="product-form-hint product-search-help">搜索已授权的项目、数据、研究、结果与报告。</p>
          <div className="product-search-filters" role="group" aria-label="搜索筛选">
            <label htmlFor="product-search-kind">类型</label>
            <select id="product-search-kind" value={searchKind} onChange={(event) => setSearchKind(event.target.value as ProductSearchItem["kind"] | "")}>
              <option value="">全部类型</option>
              <option value="project">项目</option>
              <option value="dataset">数据集</option>
              <option value="scientific_object">科学对象</option>
              <option value="research">研究会话</option>
              <option value="report">科学报告</option>
              <option value="result">科学结果</option>
            </select>
            <label htmlFor="product-search-status">状态</label>
            <select id="product-search-status" value={searchStatus} onChange={(event) => setSearchStatus(event.target.value as "active" | "archived" | "trashed" | "all")}>
              <option value="all">全部状态</option>
              <option value="active">当前</option>
              <option value="archived">已归档</option>
              <option value="trashed">回收站</option>
            </select>
            {projectId ? (
              <>
                <label htmlFor="product-search-project">范围</label>
                <select
                  id="product-search-project"
                  value={searchProject}
                  onChange={(event) => setSearchProject(event.target.value)}
                >
                  <option value="">所有可访问项目</option>
                  <option value={projectId}>当前项目</option>
                </select>
              </>
            ) : null}
          </div>
          <div className="product-search-saved" aria-label="已保存检索">
            <label htmlFor="product-saved-search">已保存</label>
            <select
              id="product-saved-search"
              value={selectedSavedSearchId}
              disabled={savedSearchState === "loading" || savedSearchMutation}
              onChange={(event) => void applySavedSearch(event.target.value)}
            >
              <option value="">
                {savedSearchState === "loading"
                  ? "正在读取…"
                  : savedSearches.length
                    ? "选择检索"
                    : "暂无已保存检索"}
              </option>
              {savedSearches.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
            <button
              type="button"
              className="product-secondary-action"
              disabled={savedSearchMutation}
              onClick={() => {
                setSavedSearchEditing(true);
                setSavedSearchError("");
                setSavedSearchName(
                  searchQuery.trim() || "当前科学工作检索",
                );
              }}
            >
              保存当前检索
            </button>
            {selectedSavedSearchId ? (
              <>
                <button
                  type="button"
                  className="product-secondary-action"
                  disabled={savedSearchMutation}
                  onClick={() => void updateSelectedSavedSearch()}
                >
                  更新
                </button>
                <button
                  type="button"
                  className="product-search-saved-delete"
                  disabled={savedSearchMutation}
                  onClick={() => void removeSelectedSavedSearch()}
                >
                  删除
                </button>
              </>
            ) : null}
          </div>
          {savedSearchEditing ? (
            <form
              className="product-search-save-form"
              onSubmit={(event) => {
                event.preventDefault();
                void saveCurrentSearch();
              }}
            >
              <label htmlFor="product-saved-search-name">检索名称</label>
              <input
                id="product-saved-search-name"
                value={savedSearchName}
                maxLength={80}
                autoComplete="off"
                onChange={(event) => setSavedSearchName(event.target.value)}
              />
              <button
                type="submit"
                className="product-primary-action"
                disabled={savedSearchMutation}
              >
                保存
              </button>
              <button
                type="button"
                className="product-secondary-action"
                disabled={savedSearchMutation}
                onClick={() => {
                  setSavedSearchEditing(false);
                  setSavedSearchError("");
                }}
              >
                取消
              </button>
            </form>
          ) : null}
          {savedSearchError ? (
            <p className="product-form-error product-search-saved-error" role="alert">
              {savedSearchError}
            </p>
          ) : null}
          <div className="product-search-results" aria-live="polite">
            {searchState === "loading" ? <p className="product-form-hint" role="status">正在搜索…</p> : searchState === "error" ? <p className="product-form-error" role="alert">搜索暂时无法读取，请稍后重试。</p> : matchingItems.length ? <>
              <p className="product-search-count" role="status" aria-label={`${searchTruncated ? "至少 " : ""}找到 ${searchCount} 项，显示前 ${matchingItems.length} 项`}>{searchTruncated ? "至少 " : ""}找到 {searchCount} 项，显示前 {matchingItems.length} 项</p>
              {matchingItems.map((item) => <div className="product-search-result" key={`${item.kind}-${item.id}`}><div><strong>{item.title}</strong><span><em className={`product-search-status status-${String(item.status || "active").toLowerCase()}`}>{searchStatusLabel(item.status)}</em>{kindLabels[item.kind]}{item.subtitle && item.subtitle !== kindLabels[item.kind] ? ` · ${item.subtitle}` : ""}</span></div><div className="product-row-actions"><Link className="product-primary-action" href={item.href} onClick={closeSearch}>打开</Link>{item.kind === "project" ? <><Link className="product-secondary-action" href={`/projects/${item.projectId}/data`} onClick={closeSearch}>查看数据</Link><Link className="product-secondary-action" href={`/projects/${item.projectId}/research`} onClick={closeSearch}>进入研究</Link></> : null}</div></div>)}
            </> : <p className="product-form-hint">没有匹配的科学工作。</p>}
          </div>
          <footer><Link className="product-primary-action" href="/projects" onClick={closeSearch}>查看全部项目</Link><button type="button" className="product-secondary-action" onClick={closeSearch}>关闭</button></footer>
        </section>
      </div>}
      <ModelSettingsDialog open={modelSettingsOpen} onClose={closeModelSettings} />
      <main
        className={`product-main ${navigation?.isPending || navigation?.intent ? "is-navigating" : ""}`}
        aria-busy={navigation?.isPending || navigation?.intent ? "true" : undefined}
      >
        {children}
      </main>
    </div>
    </ProductShellFrameContext.Provider>
  );
}

export function RequireProductAuth({ children }: { children: ReactNode }) {
  const framed = useContext(ProductAuthFrameContext);
  if (framed) return <>{children}</>;
  return <ProductAuthFrame>{children}</ProductAuthFrame>;
}

function ProductAuthFrame({ children }: { children: ReactNode }) {
  const router = useProductRouter();
  const [state, setState] = useState<"checking" | "ready" | "unauthenticated">("checking");
  useEffect(() => {
    let active = true;
    void getAuthUser().then(() => { if (active) setState("ready"); }).catch(() => { if (active) { setState("unauthenticated"); const returnTo = `${window.location.pathname}${window.location.search}`; router.replace(`/?login=1&returnTo=${encodeURIComponent(returnTo)}`); } });
    return () => { active = false; };
  }, [router]);
  if (state === "checking") return <div className="product-loading" role="status" aria-live="polite">正在恢复登录状态…</div>;
  if (state === "unauthenticated") return null;
  return <ProductAuthFrameContext.Provider value>{children}</ProductAuthFrameContext.Provider>;
}
