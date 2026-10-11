"use client";

import { useSyncExternalStore } from "react";

import {
  getProductTaskFeed,
  type ProductTaskFeed,
} from "./task-center-data";

export type ProductTaskFeedSnapshot = Readonly<{
  state: "idle" | "loading" | "ready" | "error";
  feed: ProductTaskFeed | null;
  isRefreshing: boolean;
  refreshError: boolean;
}>;

const EMPTY_SNAPSHOT: ProductTaskFeedSnapshot = {
  state: "idle",
  feed: null,
  isRefreshing: false,
  refreshError: false,
};
const POLL_INTERVAL_MS = 30_000;
const INITIAL_REQUEST_TIMEOUT_MS = 10_000;

let snapshot = EMPTY_SNAPSHOT;
let request: Promise<void> | null = null;
let requestController: AbortController | null = null;
let pollTimer: number | null = null;
const listeners = new Set<() => void>();

function publish(next: ProductTaskFeedSnapshot) {
  if (Object.is(snapshot, next)) return;
  snapshot = next;
  listeners.forEach((listener) => listener());
}

function pollingAllowed() {
  return document.visibilityState === "visible" && navigator.onLine;
}

function pauseSharedProductTaskFeed() {
  requestController?.abort();
  requestController = null;
  if (snapshot.isRefreshing) {
    publish({ ...snapshot, isRefreshing: false });
  }
}

export function refreshSharedProductTaskFeed(
  options: Readonly<{ forceRefresh?: boolean }> = {},
): Promise<void> {
  if (!pollingAllowed()) {
    // A visible offline page must settle to a typed failure instead of
    // leaving the notification surface in an indefinite loading state.
    if (document.visibilityState === "visible" && !snapshot.feed) {
      publish({
        state: "error",
        feed: null,
        isRefreshing: false,
        refreshError: false,
      });
    }
    return Promise.resolve();
  }
  if (request && requestController && !requestController.signal.aborted) {
    return request;
  }

  const controller = new AbortController();
  requestController = controller;
  let timedOut = false;
  const timeout = window.setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, INITIAL_REQUEST_TIMEOUT_MS);
  publish(
    snapshot.feed
      ? { ...snapshot, isRefreshing: true, refreshError: false }
      : { ...snapshot, state: "loading", refreshError: false },
  );
  const current = getProductTaskFeed({
    forceRefresh: options.forceRefresh ?? false,
    signal: controller.signal,
  })
    .then((feed) => {
      if (controller.signal.aborted) return;
      publish({
        state: "ready",
        feed,
        isRefreshing: false,
        refreshError: false,
      });
    })
    .catch((error) => {
      if (
        (controller.signal.aborted && !timedOut) ||
        (!timedOut &&
          error instanceof DOMException &&
          error.name === "AbortError")
      )
        return;
      publish(
        snapshot.feed
          ? { ...snapshot, isRefreshing: false, refreshError: true }
          : {
              state: "error",
              feed: null,
              isRefreshing: false,
              refreshError: false,
            },
        );
    })
    .finally(() => {
      window.clearTimeout(timeout);
      if (request === current) request = null;
      if (requestController === controller) requestController = null;
    });
  request = current;
  return current;
}

function startSharedProductTaskFeed() {
  const refresh = () => {
    if (pollingAllowed()) void refreshSharedProductTaskFeed();
  };
  const onVisibility = () => {
    if (pollingAllowed()) refresh();
    else pauseSharedProductTaskFeed();
  };
  const onOnline = () => refresh();
  const onOffline = () => {
    pauseSharedProductTaskFeed();
    if (document.visibilityState === "visible") {
      publish(snapshot.feed
        ? { ...snapshot, isRefreshing: false, refreshError: true }
        : { state: "error", feed: null, isRefreshing: false, refreshError: false });
    }
  };

  document.addEventListener("visibilitychange", onVisibility);
  window.addEventListener("online", onOnline);
  window.addEventListener("offline", onOffline);
  pollTimer = window.setInterval(refresh, POLL_INTERVAL_MS);
  void refreshSharedProductTaskFeed();

  return () => {
    document.removeEventListener("visibilitychange", onVisibility);
    window.removeEventListener("online", onOnline);
    window.removeEventListener("offline", onOffline);
    if (pollTimer !== null) window.clearInterval(pollTimer);
    pollTimer = null;
    pauseSharedProductTaskFeed();
    request = null;
    snapshot = EMPTY_SNAPSHOT;
  };
}

let stopSharedProductTaskFeed: (() => void) | null = null;

function subscribe(listener: () => void) {
  listeners.add(listener);
  if (listeners.size === 1) {
    stopSharedProductTaskFeed = startSharedProductTaskFeed();
  }
  return () => {
    listeners.delete(listener);
    if (listeners.size === 0) {
      stopSharedProductTaskFeed?.();
      stopSharedProductTaskFeed = null;
    }
  };
}

function getSnapshot() {
  return snapshot;
}

export function useProductTaskFeed(): ProductTaskFeedSnapshot {
  return useSyncExternalStore(subscribe, getSnapshot, () => EMPTY_SNAPSHOT);
}
