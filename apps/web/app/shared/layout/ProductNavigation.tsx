"use client";

import NextLink from "next/link";
import { useRouter } from "next/navigation";
import {
  createContext,
  type ComponentProps,
  type FocusEvent,
  type MouseEvent,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  useTransition,
} from "react";

type NavigationIntent = {
  sourceKey: string;
  targetKey: string;
};

type ProductNavigationContextValue = {
  intent: NavigationIntent | null;
  isPending: boolean;
  beginNavigation: (href: string) => boolean;
  completeNavigation: () => void;
  prefetch: (href: string) => void;
  navigate: (
    href: string,
    options?: Readonly<{ replace?: boolean; scroll?: boolean }>,
  ) => void;
};

const ProductNavigationContext =
  createContext<ProductNavigationContextValue | null>(null);

function currentRouteKey(): string {
  if (typeof window === "undefined") return "";
  return `${window.location.pathname}${window.location.search}`;
}

export function resolveClientNavigationTarget(
  href: string,
  currentHref: string,
): string | null {
  let target: URL;
  let current: URL;
  try {
    target = new URL(href, currentHref);
    current = new URL(currentHref);
  } catch {
    return null;
  }
  if (target.origin !== current.origin) return null;
  if (target.pathname.startsWith("/api/")) return null;
  if (
    target.pathname === current.pathname &&
    target.search === current.search &&
    target.hash
  ) {
    return null;
  }
  const targetKey = `${target.pathname}${target.search}`;
  const currentKey = `${current.pathname}${current.search}`;
  if (targetKey === currentKey && target.hash === current.hash) return null;
  return `${target.pathname}${target.search}${target.hash}`;
}

export function ProductNavigationProvider({
  children,
}: Readonly<{ children: ReactNode }>) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [intent, setIntent] = useState<NavigationIntent | null>(null);
  const prefetchAtRef = useRef(new Map<string, number>());

  const completeNavigation = useCallback(() => setIntent(null), []);
  const prefetch = useCallback(
    (href: string) => {
      const resolved = resolveClientNavigationTarget(
        href,
        typeof window === "undefined"
          ? "http://localhost/"
          : window.location.href,
      );
      if (!resolved) return;
      const now = Date.now();
      const lastPrefetchAt = prefetchAtRef.current.get(resolved) || 0;
      if (now - lastPrefetchAt < 1_500) return;
      prefetchAtRef.current.set(resolved, now);
      router.prefetch(resolved);
    },
    [router],
  );
  const beginNavigation = useCallback((href: string) => {
    const sourceKey = currentRouteKey();
    const resolved = resolveClientNavigationTarget(
      href,
      typeof window === "undefined"
        ? "http://localhost/"
        : window.location.href,
    );
    if (!resolved) return false;
    const targetUrl = new URL(
      resolved,
      typeof window === "undefined"
        ? "http://localhost/"
        : window.location.origin,
    );
    setIntent({
      sourceKey,
      targetKey: `${targetUrl.pathname}${targetUrl.search}`,
    });
    return true;
  }, []);
  const navigate = useCallback(
    (
      href: string,
      options: Readonly<{ replace?: boolean; scroll?: boolean }> = {},
    ) => {
      const resolved = resolveClientNavigationTarget(
        href,
        typeof window === "undefined"
          ? "http://localhost/"
          : window.location.href,
      );
      if (!resolved) return;
      beginNavigation(resolved);
      startTransition(() => {
        if (options.replace) {
          router.replace(resolved, { scroll: options.scroll });
        } else {
          router.push(resolved, { scroll: options.scroll });
        }
      });
    },
    [beginNavigation, router],
  );

  useEffect(() => {
    if (!intent) return;
    const timeout = window.setTimeout(completeNavigation, 15_000);
    return () => window.clearTimeout(timeout);
  }, [completeNavigation, intent]);

  const value = useMemo<ProductNavigationContextValue>(
    () => ({
      beginNavigation,
      completeNavigation,
      intent,
      isPending,
      navigate,
      prefetch,
    }),
    [beginNavigation, completeNavigation, intent, isPending, navigate, prefetch],
  );
  return (
    <ProductNavigationContext.Provider value={value}>
      {children}
    </ProductNavigationContext.Provider>
  );
}

export function useProductNavigation() {
  return useContext(ProductNavigationContext);
}

export function useProductRouter() {
  const router = useRouter();
  const navigation = useProductNavigation();
  const prefetch = useCallback(
    (href: string) => {
      if (navigation) navigation.prefetch(href);
      else router.prefetch(href);
    },
    [navigation, router],
  );
  const push = useCallback(
    (
      href: string,
      options?: Readonly<{ scroll?: boolean }>,
    ) => {
      if (navigation) {
        navigation.navigate(href, options);
        return;
      }
      if (options) router.push(href, options);
      else router.push(href);
    },
    [navigation, router],
  );
  const replace = useCallback(
    (
      href: string,
      options?: Readonly<{ scroll?: boolean }>,
    ) => {
      if (navigation) {
        navigation.navigate(href, { ...options, replace: true });
        return;
      }
      if (options) router.replace(href, options);
      else router.replace(href);
    },
    [navigation, router],
  );
  return useMemo(
    () => ({
      back: router.back,
      forward: router.forward,
      prefetch,
      push,
      refresh: router.refresh,
      replace,
    }),
    [prefetch, push, replace, router],
  );
}

type ProductLinkProps = ComponentProps<typeof NextLink>;

export function ProductLink({
  href,
  onClick,
  onFocus,
  onMouseEnter,
  replace,
  scroll,
  prefetch,
  ...props
}: ProductLinkProps) {
  const navigation = useProductNavigation();
  const handleClick = (event: MouseEvent<HTMLAnchorElement>) => {
    onClick?.(event);
    if (!navigation || event.defaultPrevented || event.button !== 0) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (props.target && props.target !== "_self") return;
    if (props.download || props["aria-disabled"] === true) return;
    if (typeof href !== "string") return;
    const target = resolveClientNavigationTarget(href, window.location.href);
    if (!target) return;
    navigation.beginNavigation(target);
  };
  const warmInternalRoute = () => {
    if (!navigation || typeof href !== "string") return;
    navigation.prefetch(href);
  };
  const handleFocus = (event: FocusEvent<HTMLAnchorElement>) => {
    onFocus?.(event);
    if (!event.defaultPrevented) warmInternalRoute();
  };
  const handleMouseEnter = (event: MouseEvent<HTMLAnchorElement>) => {
    onMouseEnter?.(event);
    if (!event.defaultPrevented) warmInternalRoute();
  };
  return (
    <NextLink
      {...props}
      href={href}
      onClick={handleClick}
      onFocus={handleFocus}
      onMouseEnter={handleMouseEnter}
      replace={replace}
      scroll={scroll}
      // Dense result/history lists warm routes on pointer or keyboard intent.
      // Primary navigation opts into eager prefetch explicitly.
      prefetch={prefetch}
    />
  );
}
