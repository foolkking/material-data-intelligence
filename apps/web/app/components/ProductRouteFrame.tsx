"use client";

import { type ReactNode, useEffect, useMemo, useRef } from "react";
import { usePathname } from "next/navigation";
import { ProductShell, RequireProductAuth } from "./ProductShell";

export function isProductRoutePath(pathname: string): boolean {
  return (
    pathname === "/analysis" ||
    pathname === "/console" ||
    pathname === "/notifications" ||
    pathname === "/tasks" ||
    pathname === "/trash" ||
    pathname.startsWith("/projects") ||
    pathname.startsWith("/settings/")
  );
}

export function projectIdFromPath(pathname: string): string | undefined {
  const match = pathname.match(/^\/projects\/([^/]+)/u);
  if (!match?.[1]) return undefined;
  try {
    return decodeURIComponent(match[1]);
  } catch {
    return match[1];
  }
}

export function shouldResetProductDocumentScroll(
  previousPathname: string,
  nextPathname: string,
): boolean {
  return Boolean(previousPathname && nextPathname && previousPathname !== nextPathname);
}

export function ProductRouteFrame({ children }: Readonly<{ children: ReactNode }>) {
  const pathname = usePathname();
  const projectId = useMemo(() => projectIdFromPath(pathname), [pathname]);
  const previousPathnameRef = useRef(pathname);

  useEffect(() => {
    const previousPathname = previousPathnameRef.current;
    previousPathnameRef.current = pathname;
    if (!shouldResetProductDocumentScroll(previousPathname, pathname)) return;
    // Next App Router preserves the shared ProductShell correctly, but a
    // document-scrolling source page can otherwise leave the destination
    // partially offset beneath the global/project context bars. Query-only
    // ResearchTurn navigation intentionally keeps its current scroll owner.
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  }, [pathname]);

  if (!isProductRoutePath(pathname)) return <>{children}</>;

  return (
    <RequireProductAuth>
      <ProductShell projectId={projectId}>{children}</ProductShell>
    </RequireProductAuth>
  );
}
