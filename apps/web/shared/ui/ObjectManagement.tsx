"use client";

import { ProductLink as Link } from "../layout/ProductNavigation";
import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { useClampedTitle } from "./use-clamped-title";

export type ObjectAction = Readonly<{
  label: string;
  href?: string;
  onSelect?: () => void;
  destructive?: boolean;
  disabled?: boolean;
}>;

function restoreUnclaimedFocus(target: HTMLElement | null) {
  const active = document.activeElement;
  // Closing removes the focused overlay control. Restore its trigger only
  // while focus is still unclaimed; a later click, typing or dialog owns it.
  if (!target?.isConnected || (active?.isConnected && active !== document.body && active !== document.documentElement)) return;
  target.focus();
}

const availableMenuItems = "[role='menuitem']:not(:disabled):not([aria-disabled='true'])";

export function ManagedObjectRow({
  href,
  title,
  description,
  trailing,
  actions,
  selectionMode = false,
  selectable = true,
  selected = false,
  active = false,
  truncateTitle = false,
  onOpen,
  onSelectedChange,
}: Readonly<{
  href: string;
  title: string;
  description: string;
  trailing?: ReactNode;
  actions: ObjectAction[];
  selectionMode?: boolean;
  selectable?: boolean;
  selected?: boolean;
  active?: boolean;
  truncateTitle?: boolean;
  onOpen?: () => void;
  onSelectedChange?: (selected: boolean) => void;
}>) {
  const [open, setOpen] = useState(false);
  const [placement, setPlacement] = useState<"above" | "below">("below");
  const rowRef = useRef<HTMLDivElement | null>(null);
  const triggerRef = useRef<HTMLButtonElement | null>(null);
  const menuRef = useRef<HTMLDivElement | null>(null);
  const name = useClampedTitle(title, truncateTitle && !open);

  const close = (restoreFocus = false) => {
    setOpen(false);
    if (restoreFocus) window.requestAnimationFrame(() => restoreUnclaimedFocus(triggerRef.current));
  };
  const show = () => {
    if (selectionMode) return;
    const row = rowRef.current?.getBoundingClientRect();
    setPlacement(row && window.innerHeight - row.bottom < 280 && row.top > 280 ? "above" : "below");
    setOpen(true);
  };

  useEffect(() => {
    if (!open) return;
    const first = menuRef.current?.querySelector<HTMLElement>(availableMenuItems);
    first?.focus();
    const onPointerDown = (event: PointerEvent) => {
      if (!rowRef.current?.contains(event.target as Node)) close(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        event.stopPropagation();
        close(true);
        return;
      }
      if (event.key === "Tab") {
        close(false);
        return;
      }
      const items = Array.from(menuRef.current?.querySelectorAll<HTMLElement>(availableMenuItems) || []);
      if (!items.length || !["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const current = Math.max(0, items.indexOf(document.activeElement as HTMLElement));
      const next = event.key === "Home" ? 0 : event.key === "End" ? items.length - 1 : event.key === "ArrowDown" ? (current + 1) % items.length : (current - 1 + items.length) % items.length;
      items[next]?.focus();
    };
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown, true);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown, true);
    };
  }, [open]);

  return <div
    ref={rowRef}
    className={`managed-object-row ${selectionMode ? "selecting" : ""} ${selected ? "selected" : ""} ${active ? "current" : ""}`}
    onContextMenu={(event) => {
      if (selectionMode) return;
      event.preventDefault();
      show();
    }}
    onKeyDown={(event) => {
      if ((event.shiftKey && event.key === "F10") || event.key === "ContextMenu") {
        event.preventDefault();
        show();
      }
    }}
  >
    {selectionMode ? <label className="object-selection-control">
      <input aria-label={selectable ? `选择 ${title}` : `${title} 当前不可批量操作`} type="checkbox" checked={selected} disabled={!selectable} onChange={(event) => onSelectedChange?.(event.target.checked)} />
      <span className="sr-only">{selectable ? `选择 ${title}` : `${title} 当前不可批量操作`}</span>
    </label> : null}
    <Link className="managed-object-link" href={href} tabIndex={selectionMode ? -1 : 0} aria-current={active ? "page" : undefined} aria-disabled={selectionMode || undefined} onClick={(event) => { if (selectionMode) event.preventDefault(); else if (!event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey && event.button === 0) onOpen?.(); }} {...name.events}>
      <span><strong ref={name.titleRef} className={truncateTitle ? "managed-object-name-clamped" : undefined}>{title}</strong>{description ? <small>{description}</small> : null}</span>
      {trailing ? <span className="managed-object-trailing">{trailing}</span> : null}
    </Link>
    {name.tooltip}
    {!selectionMode && actions.length ? <button ref={triggerRef} type="button" className="object-menu-trigger" aria-label={`管理 ${title}`} aria-haspopup="menu" aria-expanded={open} title="更多操作" onClick={() => setOpen((value) => !value)}>⋯</button> : null}
    {open ? <div ref={menuRef} className={`object-action-menu ${placement}`} role="menu" aria-label={`${title} 操作`}>
      {actions.map((action) => action.href
        ? <Link key={`${action.label}-${action.href}`} role="menuitem" href={action.href} aria-disabled={action.disabled || undefined} tabIndex={action.disabled ? -1 : 0} className={action.destructive ? "danger" : undefined} onClick={(event) => { if (action.disabled) event.preventDefault(); else close(false); }}>{action.label}</Link>
        : <button key={action.label} type="button" role="menuitem" disabled={action.disabled} className={action.destructive ? "danger" : undefined} onClick={() => { close(false); triggerRef.current?.focus(); action.onSelect?.(); }}>{action.label}</button>
      )}
    </div> : null}
  </div>;
}

export function ProductModal({
  title,
  eyebrow = "项目管理",
  description,
  children,
  footer,
  onClose,
  returnFocus,
}: Readonly<{
  title: string;
  eyebrow?: string;
  description?: string;
  children: ReactNode;
  footer: ReactNode;
  onClose: () => void;
  returnFocus?: HTMLElement | null;
}>) {
  const dialogRef = useRef<HTMLDivElement | null>(null);
  const onCloseRef = useRef(onClose);
  const openerRef = useRef<HTMLElement | null>(null);
  const restoreFrameRef = useRef<number | null>(null);
  const dialogId = useId().replace(/:/gu, "");
  const titleId = `product-task-dialog-title-${dialogId}`;
  const descriptionId = `product-task-dialog-description-${dialogId}`;
  onCloseRef.current = onClose;
  useEffect(() => {
    if (restoreFrameRef.current !== null) window.cancelAnimationFrame(restoreFrameRef.current);
    restoreFrameRef.current = null;
    // Strict Mode replays effects while the dialog is still mounted. Keep the
    // original trigger and cancel a replay's pending restoration before focus
    // enters the dialog again.
    openerRef.current = returnFocus || openerRef.current || (document.activeElement instanceof HTMLElement ? document.activeElement : null);
    const dialog = dialogRef.current;
    const focusables = () => Array.from(dialog?.querySelectorAll<HTMLElement>("button:not(:disabled), input:not(:disabled), textarea:not(:disabled), select:not(:disabled), a[href]") || []);
    const preferred = dialog?.querySelector<HTMLElement>("input:not(:disabled), textarea:not(:disabled), select:not(:disabled)");
    (preferred || focusables()[0])?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onCloseRef.current();
      }
      if (event.key !== "Tab") return;
      const items = focusables();
      if (!items.length) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      const opener = openerRef.current;
      restoreFrameRef.current = window.requestAnimationFrame(() => restoreUnclaimedFocus(opener));
    };
  }, [returnFocus]);
  return <div className="product-modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <div ref={dialogRef} className="product-task-dialog" role="dialog" aria-modal="true" aria-labelledby={titleId} aria-describedby={description ? descriptionId : undefined}>
      <header><div>{eyebrow ? <p className="product-kicker">{eyebrow}</p> : null}<h2 id={titleId}>{title}</h2>{description ? <p id={descriptionId}>{description}</p> : null}</div><button type="button" className="product-icon-action" aria-label="关闭" onClick={onClose}>×</button></header>
      <div className="product-task-dialog-body">{children}</div>
      <footer>{footer}</footer>
    </div>
  </div>;
}
