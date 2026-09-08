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
} from "../../lib/product-api";
import {
  getProjectHistory,
  searchProduct,
  type ProductSearchItem,
} from "../../lib/planner-api";
import {
  publishSavedSearchesChanged,
  subscribeSavedSearchesChanged,
} from "../../lib/saved-search-sync";
import { getProductTaskFeed } from "../../lib/task-center-data";
import { ModelSettingsDialog } from "../../components/ModelSettingsPage";
import { ProductLink as Link, useProductNavigation, useProductRouter } from "./ProductNavigation";

const ProductShellFrameContext = createContext(false);
const ProductAuthFrameContext = createContext(false);

type RoutePrefetcher = { prefetch: (href: string) => void };

export function currentProductReturnTo(target: Location = window.location): string {
  return `${target.pathname}${target.search}${target.hash}`;
}

export function sessionExpiredLoginHref(returnTo: string): string {
  return `/?login=1&reason=session-expired&returnTo=${encodeURIComponent(returnTo)}`;
}

/**
 * Keep speculative route work out of the critical navigation path.  A single
 * idle callback is allowed to enqueue one route; the next route waits for a
 * later idle slot.  The returned disposer cancels both browser idle callbacks
 * and the timer fallback used by test/older browser runtimes.
 */
export function scheduleBoundedRoutePrefetch(
  router: RoutePrefetcher,
  hrefs: string[],
  target: Window = window,
): () => void {
  let cancelled = false;
  let index = 0;
  let timerId: number | null = null;
  let idleId: number | null = null;
  const idleWindow = target as Window & {
    requestIdleCallback?: (callback: () => void, options?: { timeout: number }) => number;
    cancelIdleCallback?: (id: number) => void;
  };
  const schedule = () => {
    if (cancelled || index >= hrefs.length) return;
    const run = () => {
      timerId = null;
      idleId = null;
      if (cancelled || index >= hrefs.length) return;
      router.prefetch(hrefs[index]);
      index += 1;
      schedule();
    };
    if (idleWindow.requestIdleCallback) {
      idleId = idleWindow.requestIdleCallback(run, { timeout: 1000 });
    } else {
      timerId = target.setTimeout(run, 50);
    }
  };
  schedule();
  return () => {
    cancelled = true;
    if (timerId !== null) target.clearTimeout(timerId);
    if (idleId !== null) idleWindow.cancelIdleCallback?.(idleId);
  };
}

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
  const [searchDateFrom, setSearchDateFrom] = useState("");
  const [searchDateTo, setSearchDateTo] = useState("");
  const [searchItems, setSearchItems] = useState<ProductSearchItem[]>([]);
  const [searchCount, setSearchCount] = useState(0);
  const [searchTruncated, setSearchTruncated] = useState(false);
  const [searchNextCursor, setSearchNextCursor] = useState<string | null>(null);
  const [searchLoadingMore, setSearchLoadingMore] = useState(false);
  const [searchLoadMoreError, setSearchLoadMoreError] = useState(false);
  const [searchState, setSearchState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [searchRetryToken, setSearchRetryToken] = useState(0);
  const [savedSearches, setSavedSearches] = useState<SavedProductSearch[]>([]);
  const [savedSearchState, setSavedSearchState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [savedSearchRetryToken, setSavedSearchRetryToken] = useState(0);
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
  const searchAbortControllerRef = useRef<AbortController | null>(null);
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
      router.replace(sessionExpiredLoginHref(currentProductReturnTo()));
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
    searchAbortControllerRef.current?.abort();
    searchAbortControllerRef.current = null;
    setSearchOpen(false);
    setSearchQuery("");
    setSearchKind("");
    setSearchStatus("all");
    setSearchProject("");
    setSearchDateFrom("");
    setSearchDateTo("");
    setSearchItems([]);
    setSearchCount(0);
    setSearchTruncated(false);
    setSearchNextCursor(null);
    setSearchLoadingMore(false);
    setSearchLoadMoreError(false);
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
    setSearchState("idle");
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
  }, [savedSearchRetryToken, searchOpen, user]);

  useEffect(() => {
    if (!user) return;
    return subscribeSavedSearchesChanged(() => {
      if (searchOpen) setSavedSearchRetryToken((current) => current + 1);
    });
  }, [searchOpen, user]);

  useEffect(() => {
    if (!searchOpen) {
      searchRequestSeqRef.current += 1;
      searchAbortControllerRef.current?.abort();
      searchAbortControllerRef.current = null;
      return;
    }
    if (skipNextFilterSearchRef.current) {
      skipNextFilterSearchRef.current = false;
      return;
    }
    const hasCriteria = Boolean(
      searchQuery.trim() ||
      searchKind ||
      searchProject ||
      searchDateFrom ||
      searchDateTo ||
      searchStatus !== "all",
    );
    if (!hasCriteria) {
      searchRequestSeqRef.current += 1;
      searchAbortControllerRef.current?.abort();
      searchAbortControllerRef.current = null;
      setSearchItems([]);
      setSearchCount(0);
      setSearchTruncated(false);
      setSearchNextCursor(null);
      setSearchLoadingMore(false);
      setSearchLoadMoreError(false);
      setSearchState("idle");
      return;
    }
    const requestSeq = ++searchRequestSeqRef.current;
    let controller: AbortController | null = null;
    const timer = window.setTimeout(() => {
      searchAbortControllerRef.current?.abort();
      controller = new AbortController();
      searchAbortControllerRef.current = controller;
      setSearchState("loading");
      const options = {
        ...(searchProject ? { projectId: searchProject } : {}),
        ...(searchKind ? { kind: searchKind } : {}),
        ...(searchStatus !== "all" ? { status: searchStatus } : {}),
        ...(searchDateFrom ? { dateFrom: searchDateFrom } : {}),
        ...(searchDateTo ? { dateTo: searchDateTo } : {}),
        signal: controller.signal,
      };
      const request = searchProduct(searchQuery, options);
      void request.then((result) => {
        if (requestSeq !== searchRequestSeqRef.current) return;
        setSearchItems(result.items);
        setSearchCount(result.count);
        setSearchTruncated(Boolean(result.truncated));
        setSearchNextCursor(result.nextCursor || null);
        setSearchLoadMoreError(false);
        setSearchState("ready");
      }).catch((error) => {
        if (controller?.signal.aborted || (error instanceof DOMException && error.name === "AbortError")) return;
        if (requestSeq === searchRequestSeqRef.current) setSearchState("error");
      }).finally(() => {
        if (searchAbortControllerRef.current === controller) {
          searchAbortControllerRef.current = null;
        }
      });
    }, searchQuery.trim() ? 180 : 0);
    return () => {
      window.clearTimeout(timer);
      controller?.abort();
      if (searchAbortControllerRef.current === controller) {
        searchAbortControllerRef.current = null;
      }
      if (requestSeq === searchRequestSeqRef.current) searchRequestSeqRef.current += 1;
    };
  }, [searchDateFrom, searchDateTo, searchKind, searchOpen, searchProject, searchQuery, searchRetryToken, searchStatus]);

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
      let disposePrefetch: () => void = () => undefined;
      const timeout = window.setTimeout(() => {
        disposePrefetch = scheduleBoundedRoutePrefetch(router, ["/projects", "/tasks", "/notifications", "/trash"]);
      }, 240);
      return () => {
        window.clearTimeout(timeout);
        disposePrefetch();
      };
    }
    let active = true;
    let disposePrefetch: () => void = () => undefined;
    const timeout = window.setTimeout(() => {
      // RootLayout supplies ProductNavigationProvider in production. Its
      // ProductLink owns route prefetch, so do not issue a second eager RSC
      // campaign from the shell. The fallback keeps isolated/legacy mounts
      // functional without duplicating requests in the real product.
      if (!hasSharedNavigation) {
        const projectRoot = `/projects/${projectId}`;
        disposePrefetch = scheduleBoundedRoutePrefetch(router, [
          projectRoot,
          `${projectRoot}/data`,
          `${projectRoot}/research`,
          `${projectRoot}/reports`,
          "/tasks",
          "/notifications",
        ]);
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
      disposePrefetch();
    };
  }, [hasSharedNavigation, projectId, router, warmProjectHistory]);

  const matchingItems = searchItems;
  const searchOptions = {
    ...(searchProject ? { projectId: searchProject } : {}),
    ...(searchKind ? { kind: searchKind } : {}),
    ...(searchStatus !== "all" ? { status: searchStatus } : {}),
    ...(searchDateFrom ? { dateFrom: searchDateFrom } : {}),
    ...(searchDateTo ? { dateTo: searchDateTo } : {}),
  };
  const hasSearchCriteria = Boolean(
    searchQuery.trim() ||
    searchKind ||
    searchProject ||
    searchDateFrom ||
    searchDateTo ||
    searchStatus !== "all",
  );
  async function applySavedSearch(savedSearchId: string) {
    setSelectedSavedSearchId(savedSearchId);
    const savedSearch = savedSearches.find((item) => item.id === savedSearchId);
    if (!savedSearch) return;
    skipNextFilterSearchRef.current = true;
    setSearchQuery(savedSearch.query);
    setSearchKind(savedSearch.type || "");
    setSearchProject(savedSearch.project || "");
    setSearchStatus(savedSearch.status || "all");
    setSearchDateFrom("");
    setSearchDateTo("");
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
      setSearchNextCursor(result.nextCursor || null);
      setSearchLoadMoreError(false);
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

  async function loadMoreSearchResults() {
    if (!searchNextCursor || searchLoadingMore) return;
    const requestSeq = searchRequestSeqRef.current;
    setSearchLoadingMore(true);
    setSearchLoadMoreError(false);
    try {
      const result = await searchProduct(searchQuery, {
        ...searchOptions,
        cursor: searchNextCursor,
      });
      if (requestSeq !== searchRequestSeqRef.current) return;
      setSearchItems((current) => {
        const seen = new Set(
          current.map((item) => `${item.kind}:${item.projectId}:${item.id}`),
        );
        return [
          ...current,
          ...result.items.filter((item) => {
            const identity = `${item.kind}:${item.projectId}:${item.id}`;
            if (seen.has(identity)) return false;
            seen.add(identity);
            return true;
          }),
        ];
      });
      setSearchCount((current) => Math.max(current, result.count));
      setSearchTruncated(Boolean(result.truncated));
      setSearchNextCursor(result.nextCursor || null);
    } catch {
      if (requestSeq === searchRequestSeqRef.current) setSearchLoadMoreError(true);
    } finally {
      if (requestSeq === searchRequestSeqRef.current) setSearchLoadingMore(false);
    }
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
      publishSavedSearchesChanged({ notifyCurrentDocument: false });
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
      publishSavedSearchesChanged({ notifyCurrentDocument: false });
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
      publishSavedSearchesChanged({ notifyCurrentDocument: false });
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
        <Link href="/console" className="product-brand" aria-label="材料智能平台控制台">
          <span className="product-brand-mark" aria-hidden="true">M</span>
          <span>材料智能平台</span>
        </Link>
        <div className="product-context" title={projectName || undefined}>
          {isProject
            ? <span>{projectName ? `项目 · ${projectName}` : "项目研究"}</span>
            : <span>材料数据与科学分析</span>}
        </div>
        <div className="product-global-actions">
          <Link className="product-secondary-action product-console-link" href="/console">控制台</Link>
          <Link className="product-secondary-action product-task-link" href="/tasks" onMouseEnter={() => prefetchTaskSurface("/tasks")} onFocus={() => prefetchTaskSurface("/tasks")}>任务</Link>
          <Link className="product-secondary-action product-task-link" href="/notifications" onMouseEnter={() => prefetchTaskSurface("/notifications")} onFocus={() => prefetchTaskSurface("/notifications")}>通知</Link>
          <Link className="product-secondary-action product-task-link product-trash-link" href="/trash" title="回收站">回收站</Link>
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
                <Link role="menuitem" href="/account" onClick={() => closeAccount(false)}>账户中心</Link>
                <Link role="menuitem" href="/trash" onClick={() => closeAccount(false)}>回收站</Link>
                {user.platformRole === "PLATFORM_ADMIN" ? <Link role="menuitem" href="/admin" onClick={() => closeAccount(false)}>平台管理</Link> : null}
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
        <Link
          className="product-project-mobile-identity"
          href={`/projects/${projectId}`}
          title={projectName || "当前项目"}
        >
          <span aria-hidden="true">项目</span>
          <strong>{projectName || "当前项目"}</strong>
        </Link>
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
          <p id="product-search-help" className="product-form-hint product-search-help">搜索已授权的项目、数据、研究、科学结果与结果中的已验证发现，以及报告。</p>
          <div className="product-search-filters" role="group" aria-label="搜索筛选">
            <label htmlFor="product-search-kind">类型</label>
            <select id="product-search-kind" value={searchKind} onChange={(event) => setSearchKind(event.target.value as ProductSearchItem["kind"] | "")}>
              <option value="">全部类型</option>
              <option value="project">项目</option>
              <option value="dataset">数据集</option>
              <option value="scientific_object">科学对象</option>
              <option value="research">研究会话</option>
              <option value="report">科学报告</option>
              <option value="result">科学结果 / 发现</option>
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
            <label htmlFor="product-search-date-from">起始日期</label>
            <input
              id="product-search-date-from"
              type="date"
              value={searchDateFrom}
              max={searchDateTo || undefined}
              onChange={(event) => setSearchDateFrom(event.target.value)}
            />
            <label htmlFor="product-search-date-to">结束日期</label>
            <input
              id="product-search-date-to"
              type="date"
              value={searchDateTo}
              min={searchDateFrom || undefined}
              onChange={(event) => setSearchDateTo(event.target.value)}
            />
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
                  : savedSearchState === "error"
                    ? "读取失败"
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
              disabled={savedSearchMutation || !hasSearchCriteria}
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
            <div className="product-search-recovery product-search-saved-error">
              <p className="product-form-error" role="alert">{savedSearchError}</p>
              {savedSearchState === "error" ? (
                <button
                  type="button"
                  className="product-secondary-action"
                  onClick={() => setSavedSearchRetryToken((current) => current + 1)}
                >
                  重试读取已保存检索
                </button>
              ) : null}
            </div>
          ) : null}
          <div className="product-search-results" aria-live="polite">
            {searchState === "idle" ? <p className="product-form-hint">输入关键词，或选择项目、类型与状态后开始搜索。不会在空白条件下加载全部历史记录。</p> : searchState === "loading" ? <p className="product-form-hint" role="status">正在搜索…</p> : searchState === "error" ? <div className="product-search-recovery"><p className="product-form-error" role="alert">搜索暂时无法读取，当前条件已保留。</p><button type="button" className="product-secondary-action" onClick={() => setSearchRetryToken((current) => current + 1)}>重试搜索</button></div> : matchingItems.length ? <>
              <p className="product-search-count" role="status" aria-label={`${searchTruncated ? "至少 " : ""}找到 ${searchCount} 项，显示前 ${matchingItems.length} 项`}>{searchTruncated ? "至少 " : ""}找到 {searchCount} 项，显示前 {matchingItems.length} 项</p>
              {matchingItems.map((item) => <div className="product-search-result" key={`${item.kind}-${item.id}`}><div><strong>{item.title}</strong><span><em className={`product-search-status status-${String(item.status || "active").toLowerCase()}`}>{searchStatusLabel(item.status)}</em>{kindLabels[item.kind]}{item.subtitle && item.subtitle !== kindLabels[item.kind] ? ` · ${item.subtitle}` : ""}</span></div><div className="product-row-actions"><Link className="product-primary-action" href={item.href} onClick={closeSearch}>打开</Link>{item.kind === "project" ? <><Link className="product-secondary-action" href={`/projects/${item.projectId}/data`} onClick={closeSearch}>查看数据</Link><Link className="product-secondary-action" href={`/projects/${item.projectId}/research`} onClick={closeSearch}>进入研究</Link></> : null}</div></div>)}
              {searchNextCursor ? (
                <>
                  {searchLoadMoreError ? (
                    <p className="product-form-error" role="alert">更多结果暂时无法读取，已加载内容仍可使用。</p>
                  ) : null}
                  <button
                    type="button"
                    className="product-secondary-action product-search-load-more"
                    disabled={searchLoadingMore}
                    onClick={() => void loadMoreSearchResults()}
                  >
                    {searchLoadingMore ? "正在加载…" : searchLoadMoreError ? "重试加载更多" : "加载更多"}
                  </button>
                </>
              ) : searchTruncated ? (
                <p className="product-form-hint">已达到当前有界检索范围，可缩小筛选条件继续查找。</p>
              ) : null}
            </> : <p className="product-form-hint">没有匹配的科学工作。</p>}
          </div>
          <footer><Link className="product-primary-action" href="/projects" onClick={closeSearch}>查看全部项目</Link><button type="button" className="product-secondary-action" onClick={closeSearch}>关闭</button></footer>
        </section>
      </div>}
      <ModelSettingsDialog
        open={modelSettingsOpen}
        onClose={closeModelSettings}
        canManage={user?.platformRole === "PLATFORM_ADMIN"}
      />
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
    void getAuthUser().then(() => { if (active) setState("ready"); }).catch(() => { if (active) { setState("unauthenticated"); const returnTo = currentProductReturnTo(); router.replace(`/?login=1&returnTo=${encodeURIComponent(returnTo)}`); } });
    return () => { active = false; };
  }, [router]);
  if (state === "checking") return <div className="product-loading" role="status" aria-live="polite">正在恢复登录状态…</div>;
  if (state === "unauthenticated") return null;
  return <ProductAuthFrameContext.Provider value>{children}</ProductAuthFrameContext.Provider>;
}
