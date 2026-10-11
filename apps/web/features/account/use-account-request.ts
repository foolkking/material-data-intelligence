"use client";

import { useCallback, useEffect, useRef } from "react";

/** Each account operation owns its deadline; stalled bodies cannot settle later. */
export function useAccountRequest() {
  const controllers = useRef(new Set<AbortController>());
  useEffect(() => () => {
    for (const controller of controllers.current) controller.abort();
    controllers.current.clear();
  }, []);

  return useCallback(async <T,>(perform: (signal: AbortSignal) => Promise<T>, timeoutMessage: string): Promise<T> => {
    const controller = new AbortController();
    controllers.current.add(controller);
    let rejectInterrupted: (reason: unknown) => void = () => {};
    const interrupted = new Promise<never>((_, reject) => { rejectInterrupted = reject; });
    const onAbort = () => rejectInterrupted(controller.signal.reason);
    controller.signal.addEventListener("abort", onAbort, { once: true });
    const timer = window.setTimeout(() => controller.abort(new Error(timeoutMessage)), 10_000);
    try {
      return await Promise.race([Promise.resolve().then(() => {
        controller.signal.throwIfAborted();
        return perform(controller.signal);
      }), interrupted]);
    } finally {
      window.clearTimeout(timer);
      controller.signal.removeEventListener("abort", onAbort);
      controllers.current.delete(controller);
    }
  }, []);
}
