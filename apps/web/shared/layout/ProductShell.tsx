"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { createContext, type ReactNode, useCallback, useContext, useEffect, useRef, useState } from "react";
import {
  createSavedProductSearch,
  deleteSavedProductSearch,
  executeSavedProductSearch,
  getAuthUser,
  invalidateProductAuth,
  listSavedProductSearches,
  listResearchSessions,
  logout,
  type AuthUser,
  type SavedProductSearch,
  updateSavedProductSearch,
} from "../../app/lib/product-api";
import {
  getProjectHistory,
  searchProduct,
  type ProductSearchItem,
} from "../../app/lib/planner-api";
import {
  publishSavedSearchesChanged,
  subscribeSavedSearchesChanged,
} from "../../app/lib/saved-search-sync";
import { getProductTaskFeed } from "../../app/lib/task-center-data";
import { ModelSettingsDialog } from "../../features/account/ModelSettingsPage";
import { scientistProjectLabel } from "../product-labels";
import { ProductLink as Link, useProductNavigation, useProductRouter } from "./ProductNavigation";
import { replaceProductQuery } from "./product-query-history";
import { boundedSearchRequest, validateSearchResponse } from "./search-request";

const ProductShellFrameContext = createContext(false);
const ProductAuthFrameContext = createContext(false);

type RoutePrefetcher = { prefetch: (href: string) => void };

export function currentProductReturnTo(target: Location = window.location): string {
  return `${target.pathname}${target.search}${target.hash}`;
}

export function sessionExpiredLoginHref(returnTo: string): string {
  return `/?login=1&reason=session-expired&returnTo=${encodeURIComponent(returnTo)}`;
}

export function isGlobalProductRouteActive(
  pathname: string | null,
  href: "/console" | "/projects" | "/tasks" | "/notifications" | "/trash",
): boolean {
  return Boolean(pathname && (pathname === href || pathname.startsWith(`${href}/`)));
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

function NavigationIcon({ kind }: { kind: "console" | "projects" | "tasks" | "notifications" | "trash" }) {
  const paths = {
    console: "M3 10 12 3l9 7M5 9v12h5v-7h4v7h5V9",
    projects: "M3 7V4h6l2 3h10v13H3V7Z",
    tasks: "m3 6 1 1 2-2M9 6h12M3 12h3m3 0h12M3 18h3m3 0h12",
    notifications: "M6 9a6 6 0 0 1 12 0v6l2 3H4l2-3V9Zm4 12h4",
    trash: "M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7m4-7v7",
  };
  return <svg className="product-navigation-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d={paths[kind]} /></svg>;
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
  const [savedSearchUncertain, setSavedSearchUncertain] = useState(false);
  const [savedSearchNotice, setSavedSearchNotice] = useState("");
  const [savedSearchDeleteConfirm, setSavedSearchDeleteConfirm] = useState(false);
  const [appliedSearchToken, setAppliedSearchToken] = useState(0);
  const [modelSettingsOpen, setModelSettingsOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const [online, setOnline] = useState(true);
  const [projectName, setProjectName] = useState("");
  const searchTriggerRef = useRef<HTMLButtonElement | null>(null);
  const searchInputRef = useRef<HTMLInputElement | null>(null);
  const searchDialogRef = useRef<HTMLElement | null>(null);
  const searchRequestSeqRef = useRef(0);
  const searchAbortControllerRef = useRef<AbortController | null>(null);
  const searchMoreControllerRef = useRef<AbortController | null>(null);
  const savedReadControllerRef = useRef<AbortController | null>(null);
  const savedWriteControllerRef = useRef<AbortController | null>(null);
  const savedNeedsReadRef = useRef(false);
  const lastSearchKeyRef = useRef("");
  const searchOpenerRef = useRef<HTMLElement | null>(null);
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
      invalidateProductAuth();
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
    skipNextFilterSearchRef.current = false;
    lastSearchKeyRef.current = "";
    searchRequestSeqRef.current += 1;
    searchAbortControllerRef.current?.abort();
    searchAbortControllerRef.current = null;
    searchMoreControllerRef.current?.abort();
    searchMoreControllerRef.current = null;
    savedReadControllerRef.current?.abort();
    if (savedWriteControllerRef.current) savedNeedsReadRef.current = true;
    savedWriteControllerRef.current?.abort();
    savedWriteControllerRef.current = null;
    setSavedSearchMutation(false);
    setSavedSearchDeleteConfirm(false);
    setSavedSearchNotice("");
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
    window.requestAnimationFrame(() => (searchOpenerRef.current?.isConnected ? searchOpenerRef.current : searchTriggerRef.current)?.focus());
  }

  function openSearch() {
    searchOpenerRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    setSavedSearchMutation(false);
    setSavedSearchUncertain(savedNeedsReadRef.current);
    setSavedSearchDeleteConfirm(false);
    setSavedSearchNotice("");
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
        replaceProductQuery(url.toString());
      }
    }
  }

  useEffect(() => {
    if (!searchOpen) return;
    const bodyOverflow = document.body.style.overflow;
    const rootOverflow = document.documentElement.style.overflow;
    document.body.style.overflow = document.documentElement.style.overflow = "hidden";
    const focus = window.requestAnimationFrame(() => searchInputRef.current?.focus());
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); closeSearch(); return; }
      if (event.key !== "Tab" || !searchDialogRef.current) return;
      const nodes = [...searchDialogRef.current.querySelectorAll<HTMLElement>("button, a, input, select, summary, [tabindex]:not([tabindex='-1'])")]
        .filter((node) => !node.hasAttribute("disabled") && node.getAttribute("aria-hidden") !== "true" && (!node.closest("details:not([open])") || node.tagName === "SUMMARY"));
      const first = nodes[0];
      const last = nodes[nodes.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      window.cancelAnimationFrame(focus); document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = bodyOverflow;
      document.documentElement.style.overflow = rootOverflow;
      searchMoreControllerRef.current?.abort(); searchMoreControllerRef.current = null;
      savedReadControllerRef.current?.abort();
      if (savedWriteControllerRef.current) savedNeedsReadRef.current = true;
      savedWriteControllerRef.current?.abort(); savedWriteControllerRef.current = null;
    };
  }, [searchOpen]);

  useEffect(() => {
    if (!searchOpen || !user) return;
    const controller = new AbortController();
    savedReadControllerRef.current?.abort();
    savedReadControllerRef.current = controller;
    setSavedSearchState("loading");
    setSavedSearchError("");
    void boundedSearchRequest((signal) => listSavedProductSearches(signal), controller.signal)
      .then((items) => {
        if (controller.signal.aborted) return;
        if (!Array.isArray(items) || items.some((item) => !item.id || typeof item.name !== "string" || typeof item.query !== "string") || new Set(items.map((item) => item.id)).size !== items.length) throw new Error("Saved search identity mismatch");
        setSavedSearches(items);
        setSavedSearchState("ready");
        savedNeedsReadRef.current = false;
        setSavedSearchUncertain(false);
        setSelectedSavedSearchId((current) =>
          items.some((item) => item.id === current) ? current : "",
        );
      })
      .catch(() => {
        if (controller.signal.aborted) return;
        setSavedSearchState("error");
        setSavedSearchError("常用搜索暂时无法读取，请重试。");
      });
    return () => { controller.abort(); };
  }, [savedSearchRetryToken, searchOpen, user]);

  useEffect(() => {
    if (!user) return;
    return subscribeSavedSearchesChanged(() => {
      if (searchOpen) setSavedSearchRetryToken((current) => current + 1);
    });
  }, [searchOpen, user]);

  useEffect(() => {
    searchMoreControllerRef.current?.abort();
    searchMoreControllerRef.current = null;
    setSearchLoadingMore(false);
    setSearchLoadMoreError(false);
    if (!searchOpen) {
      searchRequestSeqRef.current += 1;
      searchAbortControllerRef.current?.abort();
      searchAbortControllerRef.current = null;
      return;
    }
    if (skipNextFilterSearchRef.current) { skipNextFilterSearchRef.current = false; return; }
    const key = JSON.stringify([searchQuery.trim(), searchKind, searchStatus, searchProject, searchDateFrom, searchDateTo]);
    const hasCriteria = Boolean(searchQuery.trim() || searchKind || searchProject || searchDateFrom || searchDateTo || searchStatus !== "all");
    const requestSeq = ++searchRequestSeqRef.current;
    searchAbortControllerRef.current?.abort();
    searchAbortControllerRef.current = null;
    if (lastSearchKeyRef.current !== key || !hasCriteria) {
      setSearchItems([]); setSearchCount(0); setSearchTruncated(false); setSearchNextCursor(null);
      lastSearchKeyRef.current = key;
    }
    if (!hasCriteria) { setSearchState("idle"); return; }
    if (searchDateFrom && searchDateTo && searchDateFrom > searchDateTo) { setSearchState("error"); return; }
    const controller = new AbortController();
    searchAbortControllerRef.current = controller;
    setSearchState("loading");
    const timer = window.setTimeout(() => {
      void boundedSearchRequest((signal) => searchProduct(searchQuery, {
        ...(searchProject ? { projectId: searchProject } : {}),
        ...(searchKind ? { kind: searchKind } : {}),
        ...(searchStatus !== "all" ? { status: searchStatus } : {}),
        ...(searchDateFrom ? { dateFrom: searchDateFrom } : {}),
        ...(searchDateTo ? { dateTo: searchDateTo } : {}), signal,
      }), controller.signal).then((value) => {
        if (controller.signal.aborted || requestSeq !== searchRequestSeqRef.current) return;
        const result = validateSearchResponse(value);
        setSearchItems(result.items); setSearchCount(result.count);
        setSearchTruncated(Boolean(result.truncated)); setSearchNextCursor(result.nextCursor || null);
        setSearchState("ready");
      }).catch(() => {
        if (!controller.signal.aborted && requestSeq === searchRequestSeqRef.current) setSearchState("error");
      });
    }, searchQuery.trim() ? 180 : 0);
    return () => {
      window.clearTimeout(timer); controller.abort();
      if (searchAbortControllerRef.current === controller) searchAbortControllerRef.current = null;
      if (requestSeq === searchRequestSeqRef.current) searchRequestSeqRef.current += 1;
    };
  }, [searchDateFrom, searchDateTo, searchKind, searchOpen, searchProject, searchQuery, searchRetryToken, searchStatus, appliedSearchToken]);
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
  function retrySearch() {
    if (!hasSearchCriteria && selectedSavedSearchId) void applySavedSearch(selectedSavedSearchId);
    else setSearchRetryToken((current) => current + 1);
  }
  async function applySavedSearch(savedSearchId: string) {
    if (savedWriteControllerRef.current) return;
    setSelectedSavedSearchId(savedSearchId);
    setSavedSearchDeleteConfirm(false);
    const savedSearch = savedSearches.find((item) => item.id === savedSearchId);
    if (!savedSearch) return;
    skipNextFilterSearchRef.current = true;
    setAppliedSearchToken((value) => value + 1);
    setSearchQuery(savedSearch.query); setSearchKind(savedSearch.type || "");
    setSearchProject(savedSearch.project || ""); setSearchStatus(savedSearch.status || "all");
    setSearchDateFrom(""); setSearchDateTo("");
    setSavedSearchEditing(false); setSavedSearchError("");
    setSearchItems([]); setSearchCount(0); setSearchNextCursor(null); setSearchTruncated(false);
    setSearchState("loading");
    lastSearchKeyRef.current = JSON.stringify([savedSearch.query.trim(), savedSearch.type || "", savedSearch.status || "all", savedSearch.project || "", "", ""]);
    const requestSeq = ++searchRequestSeqRef.current;
    searchAbortControllerRef.current?.abort();
    const controller = new AbortController(); searchAbortControllerRef.current = controller;
    try {
      const result = await boundedSearchRequest((signal) => executeSavedProductSearch(savedSearchId, 40, signal), controller.signal);
      if (controller.signal.aborted || requestSeq !== searchRequestSeqRef.current) return;
      if (result.savedSearch.id !== savedSearchId || !sameSavedCriteria(result.savedSearch, savedSearch)) throw new Error("Saved search identity mismatch");
      validateSearchResponse(result);
      setSearchItems(result.items); setSearchCount(result.count); setSearchTruncated(Boolean(result.truncated));
      setSearchNextCursor(result.nextCursor || null); setSearchLoadMoreError(false); setSearchState("ready");
    } catch {
      if (!controller.signal.aborted && requestSeq === searchRequestSeqRef.current) setSearchState("error");
    }
    if (!controller.signal.aborted && requestSeq === searchRequestSeqRef.current) window.requestAnimationFrame(() => searchInputRef.current?.focus());
  }

  async function loadMoreSearchResults() {
    if (!searchNextCursor || searchMoreControllerRef.current || searchState !== "ready") return;
    const requestSeq = searchRequestSeqRef.current, cursor = searchNextCursor;
    const controller = new AbortController(); searchMoreControllerRef.current = controller;
    setSearchLoadingMore(true); setSearchLoadMoreError(false);
    try {
      const value = await boundedSearchRequest((signal) => searchProduct(searchQuery, { ...searchOptions, cursor, signal }), controller.signal);
      if (controller.signal.aborted || requestSeq !== searchRequestSeqRef.current) return;
      const result = validateSearchResponse(value);
      if (result.nextCursor === cursor) throw new Error("Search cursor did not advance");
      setSearchItems((current) => {
        const seen = new Set(current.map((item) => `${item.kind}:${item.projectId}:${item.id}`));
        return [...current, ...result.items.filter((item) => {
          const identity = `${item.kind}:${item.projectId}:${item.id}`;
          if (seen.has(identity)) return false;
          seen.add(identity); return true;
        })];
      });
      setSearchCount((current) => Math.max(current, result.count));
      setSearchTruncated(Boolean(result.truncated)); setSearchNextCursor(result.nextCursor || null);
    } catch {
      if (!controller.signal.aborted && requestSeq === searchRequestSeqRef.current) setSearchLoadMoreError(true);
    } finally {
      if (searchMoreControllerRef.current === controller) {
        searchMoreControllerRef.current = null;
        if (requestSeq === searchRequestSeqRef.current) setSearchLoadingMore(false);
      }
    }
  }

  function sameSavedCriteria(left: Partial<SavedProductSearch>, right: Partial<SavedProductSearch>) {
    return (left.query || "").trim() === (right.query || "").trim() &&
      (left.type || "") === (right.type || "") && (left.project || "") === (right.project || "") &&
      (left.status || "all") === (right.status || "all");
  }
  async function writeSavedSearch<T>(label: string, perform: (signal: AbortSignal) => Promise<T>, accept: (result: T) => void) {
    if (savedWriteControllerRef.current || savedNeedsReadRef.current || savedSearchState !== "ready") return;
    const controller = new AbortController(); savedWriteControllerRef.current = controller;
    savedReadControllerRef.current?.abort();
    setSavedSearchMutation(true); setSavedSearchError(""); setSavedSearchNotice("");
    try {
      const result = await boundedSearchRequest(perform, controller.signal);
      if (controller.signal.aborted || savedWriteControllerRef.current !== controller) return;
      accept(result);
      setSavedSearchNotice(`${label}完成。`);
      publishSavedSearchesChanged({ notifyCurrentDocument: false });
    } catch (reason) {
      if (controller.signal.aborted || savedWriteControllerRef.current !== controller) return;
      const status = (reason as { status?: number } | null)?.status;
      const uncertain = status === undefined || ![400, 401, 403, 404, 409, 422].includes(status);
      savedNeedsReadRef.current = uncertain; setSavedSearchUncertain(uncertain);
      setSavedSearchError(uncertain ? `尚未确认${label}的结果，请重新读取常用搜索后再操作。` : `${label}未完成，请检查名称或权限后重试。`);
    } finally {
      if (savedWriteControllerRef.current === controller) { savedWriteControllerRef.current = null; setSavedSearchMutation(false); }
    }
  }
  async function saveCurrentSearch() {
    const name = savedSearchName.trim();
    if (!name) { setSavedSearchError("请输入搜索名称。"); return; }
    if (!hasSearchCriteria || searchDateFrom || searchDateTo) return;
    const requested = { name, query: searchQuery, ...(searchKind ? { type: searchKind } : {}), ...(searchProject ? { project: searchProject } : {}), status: searchStatus };
    await writeSavedSearch("保存搜索", (signal) => createSavedProductSearch(requested, signal), (saved) => {
      if (!saved.id || saved.name !== name || !sameSavedCriteria(saved, requested)) throw new Error("Saved search mismatch");
      setSavedSearches((items) => [saved, ...items.filter((item) => item.id !== saved.id)]);
      setSelectedSavedSearchId(saved.id); setSavedSearchEditing(false); setSavedSearchName("");
    });
  }
  async function removeSelectedSavedSearch() {
    const id = selectedSavedSearchId;
    if (!id || !savedSearchDeleteConfirm) return;
    await writeSavedSearch("删除常用搜索", (signal) => deleteSavedProductSearch(id, signal), (result) => {
      if (result.id !== id || result.deleted !== true) throw new Error("Saved search deletion mismatch");
      setSavedSearches((items) => items.filter((item) => item.id !== id));
      setSelectedSavedSearchId(""); setSavedSearchDeleteConfirm(false);
    });
  }
  async function updateSelectedSavedSearch() {
    const id = selectedSavedSearchId;
    if (!id || !hasSearchCriteria || searchDateFrom || searchDateTo) return;
    const changes = { query: searchQuery, type: searchKind || null, project: searchProject || null, status: searchStatus };
    await writeSavedSearch("更新常用搜索", (signal) => updateSavedProductSearch(id, changes, signal), (updated) => {
      if (updated.id !== id || !sameSavedCriteria(updated, changes)) throw new Error("Saved search update mismatch");
      setSavedSearches((items) => items.map((item) => item.id === updated.id ? updated : item));
    });
  }
  const kindLabels: Record<ProductSearchItem["kind"], string> = {
    project: "项目",
    dataset: "上传数据",
    scientific_object: "数据视图",
    research: "研究",
    report: "报告",
    result: "分析结果",
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
  const askWithHref = (item: ProductSearchItem): string | null => {
    if (item.kind === "scientific_object" && item.objectVersionId && item.objectType) {
      const query = new URLSearchParams({
        object: item.id,
        version: item.objectVersionId,
        type: item.objectType,
        name: item.title,
        fromSearch: "1",
      });
      return `/projects/${encodeURIComponent(item.projectId)}/research?${query.toString()}`;
    }
    if (item.kind === "result" && item.researchSessionId) {
      const query = new URLSearchParams({
        resultContext: item.id,
        fromSearch: "1",
      });
      return `/projects/${encodeURIComponent(item.projectId)}/research/${encodeURIComponent(item.researchSessionId)}?${query.toString()}`;
    }
    return null;
  };

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
  const displayedProjectName = scientistProjectLabel(projectName, projectId);
  return (
    <ProductShellFrameContext.Provider value>
    <div className="product-shell">
      <aside className="product-navigation-rail" aria-label="材料智能平台工作区">
        <div className="product-navigation-rail-brand">
          <Link href="/console" className="product-rail-brand" aria-label="材料智能平台控制台">
            <span className="product-brand-mark" aria-hidden="true">M</span>
            <span>材料智能平台</span>
          </Link>
          <span className="product-rail-caption">科学工作区</span>
        </div>
        <nav className="product-navigation-rail-nav" aria-label="全局导航">
          <span className="product-navigation-section-label">工作区</span>
          <Link className="product-navigation-link" href="/console" aria-current={isGlobalProductRouteActive(pathname, "/console") ? "page" : undefined}>
            <NavigationIcon kind="console" /><span>控制台</span>
          </Link>
          <Link className="product-navigation-link" href="/projects" aria-current={isGlobalProductRouteActive(pathname, "/projects") ? "page" : undefined}>
            <NavigationIcon kind="projects" /><span>项目</span>
          </Link>
          <Link className="product-navigation-link" href="/tasks" aria-current={isGlobalProductRouteActive(pathname, "/tasks") ? "page" : undefined} onMouseEnter={() => prefetchTaskSurface("/tasks")} onFocus={() => prefetchTaskSurface("/tasks")}>
            <NavigationIcon kind="tasks" /><span>任务</span>
          </Link>
          <Link className="product-navigation-link" href="/notifications" aria-current={isGlobalProductRouteActive(pathname, "/notifications") ? "page" : undefined} onMouseEnter={() => prefetchTaskSurface("/notifications")} onFocus={() => prefetchTaskSurface("/notifications")}>
            <NavigationIcon kind="notifications" /><span>通知</span>
          </Link>
          <Link className="product-navigation-link" href="/trash" aria-current={isGlobalProductRouteActive(pathname, "/trash") ? "page" : undefined} title="回收站">
            <NavigationIcon kind="trash" /><span>回收站</span>
          </Link>
        </nav>
      </aside>
      <div className="product-shell-body">
        <header className="product-global-bar">
          <div className="product-context" title={displayedProjectName || undefined}>
            {isProject ? <Link className="product-context-project" href={`/projects/${projectId}`} title={displayedProjectName}><strong>{displayedProjectName}</strong></Link> : <span className="product-context-eyebrow">材料数据与科学分析</span>}
          </div>
          <div className="product-global-actions">
            <button ref={searchTriggerRef} type="button" className="product-icon-action" aria-label="搜索科学工作" onClick={openSearch}>⌕</button>
            {checking ? <span className="product-user-skeleton" aria-label="正在读取账户" /> : user ? (
              <div ref={accountRef} className="product-account">
                <button ref={accountTriggerRef} type="button" className="product-account-trigger" title="我的账户" aria-haspopup="menu" aria-controls={accountOpen ? "product-account-menu" : undefined} aria-expanded={accountOpen} onClick={() => setAccountOpen((value) => !value)}>
                  <span className="product-avatar" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6"><circle cx="12" cy="8" r="3.5" /><path d="M5 21v-2a7 7 0 0 1 14 0v2" /></svg></span>
                  <span className="product-account-chevron" aria-hidden="true">⌄</span>
                  <span className="sr-only">{accountOpen ? "关闭账户菜单" : "打开账户菜单"}</span>
                </button>
                {accountOpen ? <div ref={accountMenuRef} id="product-account-menu" className="product-account-menu" role="menu" aria-label="账户菜单">
                  <div className="product-account-identity"><strong>{user.displayName}</strong><span>{user.email}</span></div>
                  <Link role="menuitem" href="/account" onClick={() => closeAccount(false)}>账户中心</Link>
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
          aria-label={`${displayedProjectName}导航`}
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
          <header><h2 id="product-search-title">搜索</h2><button type="button" className="product-icon-action" aria-label="关闭搜索" onClick={closeSearch}>×</button></header>
          <div className="product-search-input-label"><label htmlFor="product-project-search">项目、数据、研究或报告</label><kbd>Ctrl/⌘ K</kbd></div>
          <div className="product-search-input-wrap">
            <input ref={searchInputRef} id="product-project-search" aria-label="搜索项目、数据、研究或报告" value={searchQuery} disabled={savedSearchMutation} maxLength={160} onChange={(event) => setSearchQuery(event.target.value)} placeholder="输入名称或关键词" />
            {searchQuery ? <button type="button" className="product-search-clear" disabled={savedSearchMutation} aria-label="清除搜索" onClick={() => { setSearchQuery(""); searchInputRef.current?.focus(); }}>×</button> : null}
          </div>
          <div className="product-search-main-filters" role="group" aria-label="搜索筛选">
            <label htmlFor="product-search-kind">类型<select id="product-search-kind" value={searchKind} disabled={savedSearchMutation} onChange={(event) => setSearchKind(event.target.value as ProductSearchItem["kind"] | "")}>
              <option value="">全部类型</option>{Object.entries(kindLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select></label>
            <label htmlFor="product-search-status">状态<select id="product-search-status" value={searchStatus} disabled={savedSearchMutation} onChange={(event) => setSearchStatus(event.target.value as typeof searchStatus)}>
              <option value="all">全部状态</option><option value="active">当前</option><option value="archived">已归档</option><option value="trashed">回收站</option>
            </select></label>
          </div>
          <details className="product-search-options">
            <summary>更多筛选{searchProject || searchDateFrom || searchDateTo ? "（已启用）" : ""}</summary>
            <div className="product-search-filters">
              {projectId || searchProject ? <><label htmlFor="product-search-project">范围</label><select id="product-search-project" value={searchProject} disabled={savedSearchMutation} onChange={(event) => setSearchProject(event.target.value)}>
                <option value="">所有项目</option>{projectId ? <option value={projectId}>当前项目</option> : null}{searchProject && searchProject !== projectId ? <option value={searchProject}>已保存搜索中的项目</option> : null}
              </select></> : null}
              <label htmlFor="product-search-date-from">起始日期</label><input id="product-search-date-from" type="date" value={searchDateFrom} disabled={savedSearchMutation} max={searchDateTo || undefined} onChange={(event) => setSearchDateFrom(event.target.value)} />
              <label htmlFor="product-search-date-to">结束日期</label><input id="product-search-date-to" type="date" value={searchDateTo} disabled={savedSearchMutation} min={searchDateFrom || undefined} onChange={(event) => setSearchDateTo(event.target.value)} />
            </div>
            {searchProject || searchDateFrom || searchDateTo ? <button type="button" className="product-link-button" disabled={savedSearchMutation} onClick={() => { setSearchProject(""); setSearchDateFrom(""); setSearchDateTo(""); }}>清除范围与日期</button> : null}
          </details>
          <details className="product-search-options product-search-saved-options">
            <summary>常用搜索{selectedSavedSearchId ? ` · ${savedSearches.find((item) => item.id === selectedSavedSearchId)?.name || "已选择"}` : ""}</summary>
            <div className="product-search-saved" aria-label="常用搜索">
              <label htmlFor="product-saved-search">已保存</label>
              <select id="product-saved-search" value={selectedSavedSearchId} disabled={(savedSearchState === "loading" && !savedSearches.length) || savedSearchMutation} onChange={(event) => void applySavedSearch(event.target.value)}>
                <option value="">{savedSearchState === "loading" ? "正在读取…" : savedSearches.length ? "选择常用搜索" : "暂无常用搜索"}</option>
                {savedSearches.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
              </select>
              <button type="button" className="product-secondary-action" disabled={savedSearchMutation || savedSearchUncertain || savedSearchState !== "ready" || !hasSearchCriteria || Boolean(searchDateFrom || searchDateTo)} onClick={() => {
                setSavedSearchEditing(true); setSavedSearchError(""); setSavedSearchDeleteConfirm(false); setSavedSearchName(searchQuery.trim().slice(0, 80) || "常用搜索");
                window.requestAnimationFrame(() => document.getElementById("product-saved-search-name")?.focus());
              }}>保存当前搜索</button>
              {selectedSavedSearchId ? <>
                <button type="button" className="product-secondary-action" disabled={savedSearchMutation || savedSearchUncertain || savedSearchState !== "ready" || !hasSearchCriteria || Boolean(searchDateFrom || searchDateTo)} onClick={() => void updateSelectedSavedSearch()}>更新</button>
                <button type="button" className="product-search-saved-delete" disabled={savedSearchMutation || savedSearchUncertain || savedSearchState !== "ready"} onClick={() => { setSavedSearchDeleteConfirm(true); setSavedSearchEditing(false); }}>删除</button>
              </> : null}
            </div>
            {searchDateFrom || searchDateTo ? <p className="product-form-hint">常用搜索暂不支持保存日期范围，请先清除日期筛选。</p> : null}
            {savedSearchEditing ? <form className="product-search-save-form" onSubmit={(event) => { event.preventDefault(); void saveCurrentSearch(); }}>
              <label htmlFor="product-saved-search-name">搜索名称</label><input id="product-saved-search-name" value={savedSearchName} maxLength={80} autoComplete="off" disabled={savedSearchMutation} onChange={(event) => setSavedSearchName(event.target.value)} />
              <button type="submit" className="product-primary-action" disabled={savedSearchMutation || savedSearchUncertain || savedSearchState !== "ready" || Boolean(searchDateFrom || searchDateTo)}>保存</button>
              <button type="button" className="product-secondary-action" disabled={savedSearchMutation} onClick={() => { setSavedSearchEditing(false); setSavedSearchError(""); }}>取消</button>
            </form> : null}
            {savedSearchDeleteConfirm ? <div className="product-search-delete-confirm"><p>删除“{savedSearches.find((item) => item.id === selectedSavedSearchId)?.name}”这个常用搜索？</p><div className="product-row-actions">
              <button type="button" className="product-danger-action" disabled={savedSearchMutation || savedSearchUncertain || savedSearchState !== "ready"} onClick={() => void removeSelectedSavedSearch()}>确认删除</button>
              <button type="button" className="product-secondary-action" disabled={savedSearchMutation} onClick={() => setSavedSearchDeleteConfirm(false)}>取消</button>
            </div></div> : null}
            {savedSearchMutation ? <p role="status">正在保存更改…</p> : null}
            {savedSearchNotice ? <p role="status">{savedSearchNotice}</p> : null}
            {savedSearchError ? <div className="product-search-recovery product-search-saved-error"><p className="product-form-error" role="alert">{savedSearchError}</p>
              {savedSearchState === "error" || savedSearchUncertain ? <button type="button" className="product-secondary-action" disabled={savedSearchState === "loading"} onClick={() => setSavedSearchRetryToken((current) => current + 1)}>重新读取常用搜索</button> : null}
            </div> : null}
          </details>
          <div className="product-search-results" aria-live="polite">
            {searchState === "idle" ? <p className="product-form-hint">输入关键词，或选择类型开始查找。</p> : null}
            {searchState === "loading" ? <p className="product-form-hint" role="status">正在搜索…</p> : null}
            {searchState === "error" ? <div className="product-search-recovery"><p className="product-form-error" role="alert">{searchDateFrom && searchDateTo && searchDateFrom > searchDateTo ? "结束日期需要晚于或等于起始日期。" : "搜索暂时无法读取，当前条件和已读取的结果已保留。"}</p><button type="button" className="product-secondary-action" onClick={retrySearch}>重试搜索</button></div> : null}
            {matchingItems.length ? <>
              <p className="product-search-count" role="status" aria-label={`${searchTruncated ? "至少 " : ""}找到 ${searchCount} 项，显示前 ${matchingItems.length} 项`}>{searchNextCursor || searchTruncated ? `已显示 ${matchingItems.length} 项` : `${matchingItems.length} 项结果`}</p>
              {matchingItems.map((item) => {
                const contextHref = askWithHref(item);
                const subtitle = (item.kind === "scientific_object" && /^[a-z_]+\.[a-z_.]+$/u.test(item.subtitle)) || ["数据集", "研究会话"].includes(item.subtitle) ? "" : item.subtitle;
                return <div className="product-search-result" key={`${item.kind}-${item.projectId}-${item.id}`}><div><strong>{item.title}</strong><span>{kindLabels[item.kind]}{item.status ? <em className={`product-search-status status-${String(item.status).toLowerCase()}`}>{searchStatusLabel(item.status)}</em> : null}{subtitle && subtitle !== kindLabels[item.kind] ? ` · ${subtitle}` : ""}</span></div><div className="product-row-actions"><Link className="product-secondary-action" href={item.href} onClick={closeSearch}>打开</Link>{contextHref ? <Link className="product-link-button" href={contextHref} onClick={closeSearch}>带入研究</Link> : null}</div></div>;
              })}
              {searchNextCursor ? <>
                {searchLoadMoreError ? <p className="product-form-error" role="alert">更多结果暂时无法读取，已加载内容仍可使用。</p> : null}
                <button type="button" className="product-secondary-action product-search-load-more" disabled={searchLoadingMore || searchState !== "ready"} onClick={() => void loadMoreSearchResults()}>{searchLoadingMore ? "正在加载…" : searchLoadMoreError ? "重试加载更多" : "加载更多"}</button>
              </> : searchTruncated ? <p className="product-form-hint">还有其他结果，请缩小筛选范围继续查找。</p> : null}
            </> : searchState === "ready" ? <p className="product-form-hint">没有匹配内容，试试其他关键词或清除筛选。</p> : null}
          </div>
          <footer><Link className="product-link-button" href="/projects" onClick={closeSearch}>查看全部项目</Link></footer>
        </section>
      </div>}
        <ModelSettingsDialog
          open={modelSettingsOpen}
          onClose={closeModelSettings}
          fallbackFocus={accountTriggerRef.current}
        />
        <main
          className={`product-main ${navigation?.isPending || navigation?.intent ? "is-navigating" : ""}`}
          aria-busy={navigation?.isPending || navigation?.intent ? "true" : undefined}
        >
          {children}
        </main>
      </div>
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
  const routerRef = useRef(router);
  routerRef.current = router;
  const [state, setState] = useState<"checking" | "ready" | "unauthenticated" | "error">("checking");
  const [retry, setRetry] = useState(0);
  const [loginHref, setLoginHref] = useState("/?login=1");
  const retryRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    let active = true;
    setState("checking");
    void getAuthUser().then(() => { if (active) setState("ready"); }).catch((reason: unknown) => {
      if (!active) return;
      if (reason instanceof Error && "status" in reason && reason.status === 401) {
        const href = sessionExpiredLoginHref(currentProductReturnTo());
        setLoginHref(href);
        setState("unauthenticated");
        routerRef.current.replace(href);
      } else {
        setState("error");
      }
    });
    return () => { active = false; };
  }, [retry]);
  useEffect(() => { if (state === "error") retryRef.current?.focus(); }, [state]);
  if (state === "checking") return <div className="product-loading" role="status" aria-live="polite">正在恢复登录状态…</div>;
  if (state === "unauthenticated") return <section className="document-page product-state" role="status"><p>需要重新登录，正在打开登录页…</p><Link href={loginHref}>前往登录</Link></section>;
  if (state === "error") return <section className="document-page product-state" role="alert"><h1>暂时无法确认登录状态</h1><p>请检查网络连接后重试。</p><button ref={retryRef} className="product-primary-action" onClick={() => setRetry(value => value + 1)}>重新连接</button></section>;
  return <ProductAuthFrameContext.Provider value>{children}</ProductAuthFrameContext.Provider>;
}
