"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";

export type ObjectAction = Readonly<{
  label: string;
  href?: string;
  onSelect?: () => void;
  destructive?: boolean;
  disabled?: boolean;
}>;

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
  onSelectedChange?: (selected: boolean) => void;
}>) {
  const [open, setOpen] = useState(false);
  const [placement, setPlacement] = useState<"above" | "below">("below");
  const rowRef = useRef<HTMLDivElement | null>(null);
  const triggerRef = useRef<HTMLButtonElement | null>(null);
  const menuRef = useRef<HTMLDivElement | null>(null);

  const close = (restoreFocus = false) => {
    setOpen(false);
    if (restoreFocus) window.requestAnimationFrame(() => triggerRef.current?.focus());
  };
  const show = () => {
    if (selectionMode) return;
    const row = rowRef.current?.getBoundingClientRect();
    setPlacement(row && window.innerHeight - row.bottom < 280 && row.top > 280 ? "above" : "below");
    setOpen(true);
  };

  useEffect(() => {
    if (!open) return;
    const first = menuRef.current?.querySelector<HTMLElement>("[role='menuitem']:not([aria-disabled='true'])");
    first?.focus();
    const onPointerDown = (event: PointerEvent) => {
      if (!rowRef.current?.contains(event.target as Node)) close(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        close(true);
        return;
      }
      if (event.key === "Tab") {
        close(false);
        return;
      }
      const items = Array.from(menuRef.current?.querySelectorAll<HTMLElement>("[role='menuitem']:not([aria-disabled='true'])") || []);
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
      <input type="checkbox" checked={selected} disabled={!selectable} onChange={(event) => onSelectedChange?.(event.target.checked)} />
      <span className="sr-only">{selectable ? `选择 ${title}` : `${title} 为只读项目`}</span>
    </label> : null}
    <Link className="managed-object-link" href={href} tabIndex={selectionMode ? -1 : 0} aria-disabled={selectionMode || undefined} onClick={(event) => { if (selectionMode) event.preventDefault(); }}>
      <span><strong>{title}</strong><small>{description}</small></span>
      {trailing ? <span className="managed-object-trailing">{trailing}</span> : null}
    </Link>
    {!selectionMode ? <button ref={triggerRef} type="button" className="object-menu-trigger" aria-label={`管理 ${title}`} aria-haspopup="menu" aria-expanded={open} title="更多操作" onClick={() => setOpen((value) => !value)}>⋯</button> : null}
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
  onCloseRef.current = onClose;
  useEffect(() => {
    openerRef.current = returnFocus || (document.activeElement instanceof HTMLElement ? document.activeElement : null);
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
      window.requestAnimationFrame(() => opener?.focus());
    };
  }, [returnFocus]);
  return <div className="product-modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <div ref={dialogRef} className="product-task-dialog" role="dialog" aria-modal="true" aria-labelledby="product-task-dialog-title" aria-describedby={description ? "product-task-dialog-description" : undefined}>
      <header><div><p className="product-kicker">{eyebrow}</p><h2 id="product-task-dialog-title">{title}</h2>{description ? <p id="product-task-dialog-description">{description}</p> : null}</div><button type="button" className="product-icon-action" aria-label="关闭" onClick={onClose}>×</button></header>
      <div className="product-task-dialog-body">{children}</div>
      <footer>{footer}</footer>
    </div>
  </div>;
}
