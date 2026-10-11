"use client";

import { useEffect, useRef, useState, type CSSProperties, type KeyboardEvent, type PointerEvent } from "react";

const DEFAULT_WIDTH = 264;
const MIN_WIDTH = 220;
const MAX_WIDTH = 480;
const STORAGE_KEY = "mdi:data-directory-width";
const clamp = (width: number, max = MAX_WIDTH) => Math.round(Math.max(MIN_WIDTH, Math.min(max, width)));

export function useDataNavigator() {
  const [workbench, workbenchRef] = useState<HTMLElement | null>(null);
  const [preferredWidth, setPreferredWidth] = useState(DEFAULT_WIDTH);
  const [maxWidth, setMaxWidth] = useState(MAX_WIDTH);
  const [collapsed, setCollapsed] = useState(false);
  const [dragging, setDragging] = useState(false);
  const drag = useRef<{ pointerId: number; startX: number; startWidth: number; preferred: number; target: HTMLElement } | null>(null);
  const currentWidth = useRef(preferredWidth);
  const width = clamp(preferredWidth, maxWidth);
  currentWidth.current = preferredWidth;

  useEffect(() => {
    try {
      const saved = Number(window.localStorage.getItem(STORAGE_KEY));
      if (Number.isFinite(saved) && saved >= MIN_WIDTH && saved <= MAX_WIDTH) setPreferredWidth(saved);
    } catch { /* Browser storage is optional. */ }
  }, []);

  useEffect(() => {
    if (!workbench) return;
    const measure = () => {
      const available = workbench.clientWidth;
      if (available > 0) setMaxWidth(clamp(available - 428));
    };
    measure();
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(measure);
    observer?.observe(workbench);
    window.addEventListener("resize", measure);
    return () => { observer?.disconnect(); window.removeEventListener("resize", measure); };
  }, [workbench]);

  const persist = (next: number) => {
    try { window.localStorage.setItem(STORAGE_KEY, String(next)); } catch { /* Keep resizing usable without storage. */ }
  };
  const finishDrag = (cancel = false) => {
    const active = drag.current;
    if (!active) return;
    drag.current = null;
    if (cancel) setPreferredWidth(active.preferred);
    else persist(clamp(currentWidth.current, maxWidth));
    setDragging(false);
    if (active.target.hasPointerCapture?.(active.pointerId)) active.target.releasePointerCapture(active.pointerId);
  };

  useEffect(() => {
    if (!dragging) return;
    const cancel = () => finishDrag(true);
    const keydown = (event: globalThis.KeyboardEvent) => {
      if (event.key !== "Escape") return;
      event.preventDefault();
      cancel();
    };
    window.addEventListener("keydown", keydown);
    window.addEventListener("blur", cancel);
    // A viewport change can replace the desktop divider with the mobile header.
    window.addEventListener("resize", cancel);
    return () => {
      window.removeEventListener("keydown", keydown);
      window.removeEventListener("blur", cancel);
      window.removeEventListener("resize", cancel);
    };
  }, [dragging]);

  const reset = () => { setPreferredWidth(DEFAULT_WIDTH); persist(DEFAULT_WIDTH); };
  return {
    workbenchRef,
    collapsed,
    setCollapsed,
    dragging,
    style: { "--data-directory-width": `${width}px` } as CSSProperties,
    separatorProps: {
      role: "separator" as const,
      tabIndex: 0,
      "aria-label": "调整数据目录宽度",
      "aria-orientation": "vertical" as const,
      "aria-controls": "data-navigator-content",
      "aria-valuemin": MIN_WIDTH,
      "aria-valuemax": maxWidth,
      "aria-valuenow": width,
      "aria-valuetext": `${width} 像素`,
      title: "拖动调整目录宽度，双击恢复；也可用左右方向键调整",
      onDoubleClick: reset,
      onKeyDown: (event: KeyboardEvent<HTMLElement>) => {
        if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        const next = event.key === "Home" ? MIN_WIDTH : event.key === "End" ? maxWidth : clamp(width + (event.key === "ArrowRight" ? 16 : -16), maxWidth);
        setPreferredWidth(next);
        persist(next);
      },
      onPointerDown: (event: PointerEvent<HTMLElement>) => {
        if (event.button !== 0 || drag.current) return;
        event.preventDefault();
        event.currentTarget.focus();
        event.currentTarget.setPointerCapture(event.pointerId);
        drag.current = { pointerId: event.pointerId, startX: event.clientX, startWidth: width, preferred: preferredWidth, target: event.currentTarget };
        setDragging(true);
      },
      onPointerMove: (event: PointerEvent<HTMLElement>) => {
        const active = drag.current;
        if (!active || active.pointerId !== event.pointerId) return;
        const next = clamp(active.startWidth + event.clientX - active.startX, maxWidth);
        currentWidth.current = next;
        setPreferredWidth(next);
      },
      onPointerUp: (event: PointerEvent<HTMLElement>) => { if (drag.current?.pointerId === event.pointerId) finishDrag(); },
      onPointerCancel: () => finishDrag(true),
      onLostPointerCapture: () => finishDrag(true),
    },
  };
}
