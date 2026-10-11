import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const currentUser = { id: "current-user", displayName: "当前研究员", email: "current@example.invalid", roles: [] };
beforeEach(() => vi.resetModules());
afterEach(() => vi.unstubAllGlobals());

describe("login response ownership", () => {
  it("does not transmit a login that has already been canceled", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const api = await import("./product-api");
    const controller = new AbortController();
    controller.abort();
    await expect(api.login("test@example.invalid", "test-only", { signal: controller.signal })).rejects.toMatchObject({ name: "AbortError" });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it.each(["transport", "body", "failure"])("does not replace or invalidate a newer account when canceled %s settles late", async phase => {
    let deliver!: (value: unknown) => void;
    const delayed = new Promise(resolve => { deliver = resolve; });
    const fetchMock = vi.fn().mockReturnValueOnce(phase === "body"
      ? Promise.resolve({ ok: true, status: 200, json: () => delayed }) : delayed)
      .mockResolvedValueOnce(Response.json(currentUser));
    vi.stubGlobal("fetch", fetchMock);
    const api = await import("./product-api");
    const controller = new AbortController();
    const pending = api.login("old@example.invalid", "test-only", { signal: controller.signal });
    const rejection = expect(pending).rejects.toMatchObject({ name: "AbortError" });
    await Promise.resolve();
    controller.abort();
    await api.login("current@example.invalid", "test-only");
    const old = { ...currentUser, id: "old-user" };
    deliver(phase === "failure" ? new Response(null, { status: 401 }) : phase === "body" ? old : Response.json(old));
    await rejection;
    expect(await api.getAuthUser()).toEqual(currentUser);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock.mock.calls[0][1].signal).toBe(controller.signal);
  });

  it.each([null, {}, { id: "", displayName: "empty" }, { id: "missing-name" }])("does not publish an invalid successful login %j", async value => {
    const fetchMock = vi.fn().mockResolvedValueOnce(Response.json(value)).mockResolvedValueOnce(Response.json(currentUser));
    vi.stubGlobal("fetch", fetchMock);
    const api = await import("./product-api");
    await expect(api.login("test@example.invalid", "test-only")).rejects.toThrow("登录结果暂时无法确认，请重试。");
    expect(await api.getAuthUser()).toEqual(currentUser);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("replaces a malformed response parser message with a safe recovery message", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("private-upstream-response", { status: 200 })));
    const api = await import("./product-api");
    await expect(api.login("test@example.invalid", "test-only")).rejects.toThrow("登录结果暂时无法确认，请重试。");
  });
});
