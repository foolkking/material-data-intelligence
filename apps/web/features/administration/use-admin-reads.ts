"use client";

import { useCallback, useEffect, useRef } from "react";

type ReadKey = "auth" | "overview" | "audit" | "users" | "projects" | "members";

function useAdminRequests<Key extends string>() {
  const pending = useRef(new Map<Key, AbortController>());
  useEffect(() => () => {
    for (const controller of pending.current.values()) controller.abort();
    pending.current.clear();
  }, []);
  const cancel = useCallback((key: Key) => pending.current.get(key)?.abort(), []);
  const run = useCallback(async <T,>(key: Key, perform: (signal: AbortSignal) => Promise<T>, timeoutMessage = "读取超时，请重试。"): Promise<T> => {
    pending.current.get(key)?.abort();
    const controller = new AbortController();
    pending.current.set(key, controller);
    let rejectInterrupted: (reason: unknown) => void = () => {};
    const interrupted = new Promise<never>((_, reject) => { rejectInterrupted = reject; });
    const abort = () => rejectInterrupted(controller.signal.reason);
    controller.signal.addEventListener("abort", abort, { once: true });
    const timer = window.setTimeout(() => controller.abort(new Error(timeoutMessage)), 10_000);
    try {
      return await Promise.race([interrupted, Promise.resolve().then(() => {
        controller.signal.throwIfAborted();
        return perform(controller.signal);
      })]);
    } finally {
      window.clearTimeout(timer);
      controller.signal.removeEventListener("abort", abort);
      if (pending.current.get(key) === controller) pending.current.delete(key);
    }
  }, []);
  return { run, cancel };
}

export function useAdminReads() {
  return useAdminRequests<ReadKey>().run;
}

export function useAdminWrites() {
  return useAdminRequests<"user" | "member" | "invitation">();
}
