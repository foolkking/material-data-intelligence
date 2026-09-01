"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { useProductNavigation } from "./ProductNavigation";

export function RouteTransitionProgress() {
  return (
    <Suspense fallback={null}>
      <RouteTransitionProgressInner />
    </Suspense>
  );
}

function RouteTransitionProgressInner() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const routeKey = `${pathname}?${searchParams.toString()}`;
  const navigation = useProductNavigation();
  const pending = Boolean(navigation?.intent || navigation?.isPending);
  const [visible, setVisible] = useState(false);
  const pendingTimer = useRef<number | null>(null);

  useEffect(() => {
    if (
      navigation?.intent &&
      routeKey.replace(/\?$/u, "") === navigation.intent.targetKey &&
      !navigation.isPending
    ) {
      navigation.completeNavigation();
    }
  }, [navigation, routeKey]);

  useEffect(() => {
    if (pending) {
      if (pendingTimer.current !== null) {
        window.clearTimeout(pendingTimer.current);
      }
      pendingTimer.current = window.setTimeout(() => {
        pendingTimer.current = null;
        setVisible(true);
      }, 120);
    } else {
      if (pendingTimer.current !== null) {
        window.clearTimeout(pendingTimer.current);
        pendingTimer.current = null;
      }
      setVisible(false);
    }
    return () => {
      if (pendingTimer.current !== null) window.clearTimeout(pendingTimer.current);
    };
  }, [pending]);

  if (!visible) return null;
  return (
    <div className="route-transition-progress" role="status" aria-live="polite">
      <span className="route-transition-progress-bar" aria-hidden="true" />
      <span className="sr-only">正在切换工作区…</span>
    </div>
  );
}
