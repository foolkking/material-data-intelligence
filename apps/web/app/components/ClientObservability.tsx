"use client";

import { useEffect, useRef } from "react";
import {
  buildClientExceptionEvent,
  sendClientExceptionEvent,
} from "../lib/client-observability";


export function ClientObservability({
  releaseSha,
}: Readonly<{ releaseSha?: string }>) {
  const previousRef = useRef<{ fingerprint: string; at: number } | null>(null);

  useEffect(() => {
    const capture = (
      source: "window.error" | "unhandledrejection",
      error: unknown,
    ) => {
      const clientEventId =
        globalThis.crypto?.randomUUID?.() ||
        `client-${Date.now().toString(36)}`;
      const event = buildClientExceptionEvent({
        source,
        releaseSha,
        location: window.location,
        error,
        clientEventId,
      });
      const fingerprint = `${event.source}:${event.route}:${event.errorType}`;
      const now = Date.now();
      if (
        previousRef.current?.fingerprint === fingerprint &&
        now - previousRef.current.at < 1_000
      ) {
        return;
      }
      previousRef.current = { fingerprint, at: now };
      void sendClientExceptionEvent(event).catch(() => undefined);
    };
    const onError = (event: ErrorEvent) => {
      capture("window.error", event.error);
    };
    const onUnhandledRejection = (event: PromiseRejectionEvent) => {
      capture("unhandledrejection", event.reason);
    };
    window.addEventListener("error", onError);
    window.addEventListener("unhandledrejection", onUnhandledRejection);
    return () => {
      window.removeEventListener("error", onError);
      window.removeEventListener("unhandledrejection", onUnhandledRejection);
    };
  }, [releaseSha]);

  return null;
}
