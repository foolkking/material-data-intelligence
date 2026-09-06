"use client";

const SAVED_SEARCH_SYNC_KEY = "mdi:saved-searches:changed";
const SAVED_SEARCH_EVENT = "mdi:saved-searches-changed";

type SavedSearchChange = Readonly<{
  revision: string;
}>;

let channel: BroadcastChannel | null = null;

function readRevision(value: unknown): string | undefined {
  if (!value || typeof value !== "object") return undefined;
  const revision = (value as { revision?: unknown }).revision;
  return typeof revision === "string" && revision.length > 0 ? revision : undefined;
}

function createRevision() {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function getChannel() {
  if (channel || typeof window === "undefined" || !("BroadcastChannel" in window))
    return channel;
  channel = new BroadcastChannel(SAVED_SEARCH_SYNC_KEY);
  return channel;
}

export function publishSavedSearchesChanged(options?: {
  notifyCurrentDocument?: boolean;
}) {
  if (typeof window === "undefined") return;
  const message: SavedSearchChange = { revision: createRevision() };
  getChannel()?.postMessage(message);
  try {
    window.localStorage.setItem(SAVED_SEARCH_SYNC_KEY, JSON.stringify(message));
    window.localStorage.removeItem(SAVED_SEARCH_SYNC_KEY);
  } catch {
    // Storage may be disabled; the in-document event still synchronizes open shells.
  }
  if (options?.notifyCurrentDocument !== false) {
    window.dispatchEvent(
      new CustomEvent<SavedSearchChange>(SAVED_SEARCH_EVENT, {
        detail: message,
      }),
    );
  }
}

export function subscribeSavedSearchesChanged(
  listener: () => void,
): () => void {
  if (typeof window === "undefined") return () => undefined;
  let lastRevision: string | null = null;
  const notify = (revision?: string) => {
    if (!revision) return;
    if (revision && revision === lastRevision) return;
    lastRevision = revision;
    listener();
  };
  const onMessage = (event: MessageEvent<SavedSearchChange>) => {
    notify(readRevision(event.data));
  };
  const onDocumentEvent = (event: Event) => {
    notify(readRevision((event as CustomEvent<SavedSearchChange>).detail));
  };
  const onStorage = (event: StorageEvent) => {
    if (event.key !== SAVED_SEARCH_SYNC_KEY || !event.newValue) return;
    try {
      notify(readRevision(JSON.parse(event.newValue)));
    } catch {
      // Ignore malformed cross-tab markers; saved-search payloads never cross the boundary.
    }
  };
  window.addEventListener(SAVED_SEARCH_EVENT, onDocumentEvent);
  window.addEventListener("storage", onStorage);
  getChannel()?.addEventListener("message", onMessage);
  return () => {
    window.removeEventListener(SAVED_SEARCH_EVENT, onDocumentEvent);
    window.removeEventListener("storage", onStorage);
    getChannel()?.removeEventListener("message", onMessage);
  };
}

export function closeSavedSearchSyncForTests() {
  channel?.close();
  channel = null;
}
