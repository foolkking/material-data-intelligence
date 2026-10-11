import { afterEach, describe, expect, it, vi } from "vitest";
import { getUserModels, saveUserModelSelection } from "./user-models-api";

function stalledFetch() {
  const fetcher = vi.fn((_url: string, init: RequestInit) => new Promise<Response>((_resolve, reject) => {
    if (init.signal?.aborted) reject(new DOMException("aborted", "AbortError"));
    else init.signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")), { once: true });
  }));
  vi.stubGlobal("fetch", fetcher);
  return fetcher;
}
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });
describe("account model reads", () => {
  it("bounds configuration reads at 10 seconds", async () => {
    vi.useFakeTimers();
    const fetcher = stalledFetch();
    const failure = expect(getUserModels()).rejects.toThrow("读取模型超时，请重试。");
    await vi.advanceTimersByTimeAsync(10_000);
    await failure;
    expect(fetcher.mock.calls[0][1].signal?.aborted).toBe(true);
  });
  it("propagates caller cancellation to the transport", async () => {
    const fetcher = stalledFetch();
    const controller = new AbortController();
    const failure = expect(getUserModels({ signal: controller.signal })).rejects.toThrow();
    controller.abort();
    await failure;
    expect(fetcher.mock.calls[0][1].signal?.aborted).toBe(true);
  });
  it("preserves the longer deadline and exact identity for saving model choices", async () => {
    vi.useFakeTimers();
    const fetcher = stalledFetch();
    const failure = expect(saveUserModelSelection([{ provider: "personal", model: "deepseek-v4-pro" }], 4)).rejects.toThrow("确认保存状态");
    await vi.advanceTimersByTimeAsync(10_000);
    expect(fetcher.mock.calls[0][1].signal?.aborted).toBe(false);
    expect(JSON.parse(String(fetcher.mock.calls[0][1].body))).toEqual({ selected: [{ provider: "personal", model: "deepseek-v4-pro" }], revision: 4 });
    await vi.advanceTimersByTimeAsync(25_000);
    await failure;
  });
});
