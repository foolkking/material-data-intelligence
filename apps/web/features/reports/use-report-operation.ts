"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { readReportContent } from "./report-read";

/** A timed-out write is unconfirmed; reread saved reports before permitting another write. */
export function useReportOperation() {
  const owner = useRef<AbortController | null>(null);
  const needsRead = useRef(false);
  const [pending, setPending] = useState(false);
  const [uncertain, setUncertain] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => () => { owner.current?.abort(); owner.current = null; }, []);

  const isPending = useCallback(() => Boolean(owner.current), []);
  const reconciled = useCallback(() => {
    if (!needsRead.current) return;
    needsRead.current = false;
    setUncertain(false);
    setError(null);
    setNotice("已重新读取报告，请先确认列表中的结果。");
  }, []);

  async function run<T>(
    label: string,
    perform: (signal: AbortSignal) => Promise<T>,
    accept: (result: T) => void,
  ) {
    if (owner.current || needsRead.current) return;
    const controller = new AbortController();
    owner.current = controller;
    setPending(true);
    setError(null);
    setNotice(null);
    try {
      // The bounded request also covers response bodies; accept validates exact returned identities.
      const result = await readReportContent(perform, controller.signal);
      if (owner.current !== controller || controller.signal.aborted) return;
      accept(result);
      setNotice(`${label}完成。`);
    } catch (reason) {
      if (owner.current !== controller || controller.signal.aborted) return;
      const status = (reason as { status?: number } | null)?.status;
      const rejected = status !== undefined && [400, 401, 403, 404, 409, 422].includes(status);
      needsRead.current = !rejected;
      setUncertain(!rejected);
      setError(rejected
        ? `${label}未完成，请检查权限或内容后重试。`
        : `尚未确认${label}的结果。请重新读取报告，确认是否已生效。`);
    } finally {
      if (owner.current === controller) {
        owner.current = null;
        setPending(false);
      }
    }
  }

  return { run, pending, uncertain, error, notice, reconciled, isPending, locked: () => Boolean(owner.current || needsRead.current) };
}
