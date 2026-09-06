import { afterEach, describe, expect, it, vi } from "vitest";

import {
  closeSavedSearchSyncForTests,
  publishSavedSearchesChanged,
  subscribeSavedSearchesChanged,
} from "./saved-search-sync";

describe("saved search synchronization", () => {
  afterEach(() => {
    closeSavedSearchSyncForTests();
    vi.restoreAllMocks();
    window.localStorage.clear();
  });

  it("notifies open same-document shells and writes a cross-tab invalidation marker", () => {
    const listener = vi.fn();
    const unsubscribe = subscribeSavedSearchesChanged(listener);

    publishSavedSearchesChanged();

    expect(listener).toHaveBeenCalledOnce();
    expect(window.localStorage.getItem("mdi:saved-searches:changed")).toBeNull();
    unsubscribe();
  });

  it("accepts a storage event from another tab without exposing payload data", () => {
    const listener = vi.fn();
    const unsubscribe = subscribeSavedSearchesChanged(listener);
    const event = new StorageEvent("storage", {
      key: "mdi:saved-searches:changed",
      newValue: JSON.stringify({ revision: "remote-revision" }),
    });

    window.dispatchEvent(event);

    expect(listener).toHaveBeenCalledOnce();
    unsubscribe();
  });

  it("deduplicates the same revision delivered by multiple browser channels", () => {
    const listener = vi.fn();
    const unsubscribe = subscribeSavedSearchesChanged(listener);
    const event = new StorageEvent("storage", {
      key: "mdi:saved-searches:changed",
      newValue: JSON.stringify({ revision: "remote-revision" }),
    });

    window.dispatchEvent(event);
    window.dispatchEvent(new StorageEvent("storage", {
      key: "mdi:saved-searches:changed",
      newValue: JSON.stringify({ revision: "remote-revision" }),
    }));

    expect(listener).toHaveBeenCalledOnce();
    unsubscribe();
  });

  it("ignores malformed invalidation markers", () => {
    const listener = vi.fn();
    const unsubscribe = subscribeSavedSearchesChanged(listener);

    window.dispatchEvent(new StorageEvent("storage", {
      key: "mdi:saved-searches:changed",
      newValue: JSON.stringify({ revision: 42 }),
    }));
    window.dispatchEvent(new CustomEvent("mdi:saved-searches-changed", {
      detail: { revision: "" },
    }));

    expect(listener).not.toHaveBeenCalled();
    unsubscribe();
  });

  it("removes listeners without receiving later invalidations", () => {
    const listener = vi.fn();
    const unsubscribe = subscribeSavedSearchesChanged(listener);
    unsubscribe();

    publishSavedSearchesChanged();

    expect(listener).not.toHaveBeenCalled();
  });
});
