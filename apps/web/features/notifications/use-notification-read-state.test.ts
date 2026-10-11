import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({ list: vi.fn(), update: vi.fn() }));
vi.mock("../../app/lib/product-api", () => ({ listNotificationReadStates: mocks.list, updateNotificationReadState: mocks.update }));
import { useNotificationReadState } from "./use-notification-read-state";
const empty = { items: [] };
const read = (jobId = "job-a") => ({ projectId: "project-a", jobId, read: true });
const deferred = <T,>() => { let resolve!: (value: T) => void; const promise = new Promise<T>((res) => { resolve = res; }); return { promise, resolve }; };

beforeEach(() => { mocks.list.mockReset().mockResolvedValue(empty); mocks.update.mockReset().mockImplementation(async (projectId, jobId, read) => ({ projectId, jobId, read })); });

describe("notification reading state", () => {
  it("keeps unknown reading state distinct from unread and recovers after a read deadline", async () => {
    vi.useFakeTimers();
    const first = deferred<typeof empty>();
    mocks.list.mockReturnValueOnce(first.promise).mockResolvedValue({ items: [read()] });
    const { result, unmount } = renderHook(useNotificationReadState);
    try {
      act(() => { void result.current.refresh(); });
      expect(result.current.loaded).toBe(false);
      expect(result.current.loading).toBe(true);
      const signal = mocks.list.mock.calls[0][0].signal;
      await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
      expect(signal.aborted).toBe(true);
      expect(result.current.readError).toBe(true);
      expect(result.current.loaded).toBe(false);
      await act(async () => { await result.current.refresh(); });
      expect(result.current.readKeys.has("project-a:job-a")).toBe(true);
      await act(async () => { first.resolve(empty); });
      expect(result.current.readKeys.has("project-a:job-a")).toBe(true);
    } finally { unmount(); vi.useRealTimers(); }
  });

  it("retains known reading state when refresh fails", async () => {
    mocks.list.mockResolvedValueOnce({ items: [read()] }).mockRejectedValueOnce(new Error("offline"));
    const { result } = renderHook(useNotificationReadState);
    await act(async () => { await result.current.refresh(); });
    await act(async () => { await result.current.refresh(); });
    expect(result.current.loaded).toBe(true);
    expect(result.current.readError).toBe(true);
    expect(result.current.readKeys.has("project-a:job-a")).toBe(true);
  });

  it("rejects a stale read snapshot after a reading change", async () => {
    const stale = deferred<typeof empty>();
    const { result } = renderHook(useNotificationReadState);
    await act(async () => { await result.current.refresh(); });
    mocks.list.mockReturnValueOnce(stale.promise);
    act(() => { void result.current.refresh(); });
    const signal = mocks.list.mock.calls[1][0].signal;
    await act(async () => { await result.current.setRead("project-a", "job-a", true); });
    expect(signal.aborted).toBe(true);
    await act(async () => { stale.resolve(empty); });
    expect(result.current.readKeys.has("project-a:job-a")).toBe(true);
  });

  it("locks each saving notification independently and does not duplicate its request", async () => {
    const first = deferred<ReturnType<typeof read>>(), second = deferred<ReturnType<typeof read>>();
    mocks.update.mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    const { result } = renderHook(useNotificationReadState);
    act(() => {
      void result.current.setRead("project-a", "job-a", true);
      void result.current.setRead("project-a", "job-b", true);
      void result.current.setRead("project-a", "job-a", true);
    });
    expect(mocks.update).toHaveBeenCalledTimes(2);
    expect(result.current.savingKeys.size).toBe(2);
    await act(async () => { first.resolve(read()); });
    expect([...result.current.savingKeys]).toEqual(["project-a:job-b"]);
    await act(async () => { second.resolve(read("job-b")); });
    expect(result.current.savingKeys.size).toBe(0);
    expect(result.current.readKeys.size).toBe(2);
  });

  it("releases a stalled save for retry and ignores its late acknowledgement", async () => {
    vi.useFakeTimers();
    const late = deferred<ReturnType<typeof read>>();
    mocks.update.mockReturnValueOnce(late.promise);
    const { result, unmount } = renderHook(useNotificationReadState);
    try {
      act(() => { void result.current.setRead("project-a", "job-a", true); });
      await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
      expect(result.current.savingKeys.size).toBe(0);
      expect(result.current.saveErrors.has("project-a:job-a")).toBe(true);
      await act(async () => { await result.current.setRead("project-a", "job-a", false); });
      await act(async () => { late.resolve(read()); });
      expect(result.current.readKeys.has("project-a:job-a")).toBe(false);
      expect(result.current.saveErrors.size).toBe(0);
    } finally { unmount(); vi.useRealTimers(); }
  });

  it("rejects a mismatched save response and aborts pending requests on unmount", async () => {
    mocks.update.mockResolvedValueOnce(read("foreign"));
    const { result, unmount } = renderHook(useNotificationReadState);
    await act(async () => { await result.current.setRead("project-a", "job-a", true); });
    expect(result.current.readKeys.size).toBe(0);
    expect(result.current.saveErrors.has("project-a:job-a")).toBe(true);
    mocks.update.mockImplementationOnce(() => new Promise(() => {}));
    act(() => { void result.current.setRead("project-a", "job-a", true); });
    const signal = mocks.update.mock.calls[1][3].signal;
    unmount();
    expect(signal.aborted).toBe(true);
  });
});
