"use client";

import { useEffect, useRef, useState } from "react";

type Target = Readonly<{ id: string; label: string }>;
type Entry<T> = Target & { value?: T; pending: boolean; error?: string };
export type DependencyPreviewState<T> = Readonly<{
  items: T[];
  entries: Entry<T>[];
  complete: boolean;
  pendingCount: number;
  retry: () => void;
}>;

/** Read each target independently; retry missing previews without losing known dependencies. */
export function useDependencyPreview<T>(
  targets: readonly Target[],
  read: (id: string, signal?: AbortSignal) => Promise<T>,
): DependencyPreviewState<T> {
  const key = JSON.stringify(targets);
  const [attempt, setAttempt] = useState(0);
  const [snapshot, setSnapshot] = useState<{ key: string; entries: Entry<T>[] }>({ key: "", entries: [] });
  const snapshotRef = useRef(snapshot);

  useEffect(() => {
    let active = true;
    const currentTargets: Target[] = JSON.parse(key);
    const previous = snapshotRef.current.key === key ? snapshotRef.current.entries : [];
    const entries = currentTargets.map((target): Entry<T> => {
      const loaded = previous.find((entry) => entry.id === target.id && entry.value !== undefined);
      return loaded || { ...target, pending: true };
    });
    const publish = (next: Entry<T>[]) => {
      snapshotRef.current = { key, entries: next };
      setSnapshot(snapshotRef.current);
    };
    publish(entries);
    const cleanup: Array<() => void> = [];
    for (const entry of entries.filter((item) => item.pending)) {
      const controller = new AbortController();
      const settle = (result: Partial<Entry<T>>) => {
        if (!active) return;
        publish(snapshotRef.current.entries.map((item) => item.id === entry.id ? { ...item, ...result, pending: false } : item));
      };
      const timer = setTimeout(() => {
        controller.abort();
        settle({ error: "检查超时" });
      }, 10_000);
      void read(entry.id, controller.signal)
        .then((value) => { if (!controller.signal.aborted) settle({ value, error: undefined }); })
        .catch(() => { if (!controller.signal.aborted) settle({ error: "暂时无法读取" }); })
        .finally(() => clearTimeout(timer));
      cleanup.push(() => { clearTimeout(timer); controller.abort(); });
    }
    return () => {
      active = false;
      cleanup.forEach((cancel) => cancel());
    };
  }, [key, attempt, read]);

  const entries: Entry<T>[] = snapshot.key === key ? snapshot.entries : targets.map((target) => ({ ...target, pending: true }));
  const items = entries.flatMap((entry) => entry.value === undefined ? [] : [entry.value]);
  return {
    entries,
    items,
    complete: entries.length > 0 && items.length === entries.length,
    pendingCount: entries.filter((entry) => entry.pending).length,
    retry: () => setAttempt((value) => value + 1),
  };
}

export function DependencyPreviewFeedback<T>({ preview }: { preview: DependencyPreviewState<T> }) {
  const errors = preview.entries.filter((entry) => entry.error);
  return <>
    {preview.pendingCount > 0 ? <p role="status">正在检查依赖影响… 已读取 {preview.items.length} / {preview.entries.length} 项。</p> : null}
    {errors.length > 0 ? <div className="product-form-error" role="alert">
      <p>部分依赖信息尚未读取，请重试后再确认。已读取的依赖仍然保留。</p>
      <ul>{errors.map((entry) => <li key={entry.id}>{entry.label}：{entry.error}</li>)}</ul>
      <button type="button" className="product-secondary-action" disabled={preview.pendingCount > 0} onClick={preview.retry}>重新检查依赖</button>
    </div> : null}
  </>;
}
