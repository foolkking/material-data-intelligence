"use client";

import { useEffect, useId, useLayoutEffect, useRef, useState, type PointerEvent } from "react";
import { createPortal } from "react-dom";

/** A clipped name keeps its full accessible text; the popup is only a visual aid. */
export function useClampedTitle(title: string, enabled: boolean) {
  const titleRef = useRef<HTMLElement | null>(null);
  const popupRef = useRef<HTMLDivElement | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const focused = useRef(false);
  const [anchor, setAnchor] = useState<DOMRect | null>(null);
  const [top, setTop] = useState(0);
  const id = useId();
  const clearTimer = () => { if (timer.current !== null) clearTimeout(timer.current); timer.current = null; };
  const close = () => { clearTimer(); setAnchor(null); };
  const show = () => {
    clearTimer();
    const element = titleRef.current;
    if (!enabled || !element || (element.scrollHeight <= element.clientHeight + 1 && element.scrollWidth <= element.clientWidth + 1)) return;
    const rect = element.getBoundingClientRect();
    setTop(rect.bottom + 8);
    setAnchor(rect);
  };
  const leave = () => {
    clearTimer();
    if (!focused.current) timer.current = setTimeout(close, 150);
  };
  useEffect(() => { close(); return clearTimer; }, [title, enabled]);
  useEffect(() => {
    if (!anchor) return;
    const keydown = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      event.preventDefault();
      event.stopPropagation();
      close();
    };
    const scroll = (event: Event) => { if (!(event.target instanceof Node) || !popupRef.current?.contains(event.target)) close(); };
    const pointerdown = (event: Event) => { if (!popupRef.current?.contains(event.target as Node)) close(); };
    // Dismiss this popup before the containing panel receives Escape.
    document.addEventListener("keydown", keydown, true);
    document.addEventListener("pointerdown", pointerdown);
    window.addEventListener("resize", close);
    window.addEventListener("scroll", scroll, true);
    return () => {
      document.removeEventListener("keydown", keydown, true);
      document.removeEventListener("pointerdown", pointerdown);
      window.removeEventListener("resize", close);
      window.removeEventListener("scroll", scroll, true);
    };
  }, [anchor]);
  useLayoutEffect(() => {
    if (!anchor || !popupRef.current) return;
    const height = popupRef.current.getBoundingClientRect().height;
    setTop(Math.max(16, Math.min(window.innerHeight - height - 16, anchor.bottom + height + 24 <= window.innerHeight ? anchor.bottom + 8 : anchor.top - height - 8)));
  }, [anchor, title]);

  return {
    titleRef,
    events: {
      onPointerEnter: (event: PointerEvent<HTMLElement>) => {
        if (!enabled || event.pointerType === "touch") return;
        clearTimer();
        timer.current = setTimeout(show, 250);
      },
      onPointerLeave: leave,
      onFocus: () => { focused.current = true; show(); },
      onBlur: () => { focused.current = false; close(); },
      "aria-describedby": anchor ? id : undefined,
    },
    tooltip: anchor ? createPortal(<div
      ref={popupRef}
      id={id}
      role="tooltip"
      className="managed-name-tooltip"
      style={{ left: Math.max(16, Math.min(anchor.left, window.innerWidth - Math.min(360, window.innerWidth - 32) - 16)), top }}
      onPointerEnter={clearTimer}
      onPointerLeave={leave}
      onPointerDown={(event) => event.stopPropagation()}
    >{title}</div>, document.body) : null,
  };
}
