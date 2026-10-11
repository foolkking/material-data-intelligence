import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const user = { id: "user-current", displayName: "当前研究员", email: "research@example.invalid", roles: [] };
beforeEach(() => vi.resetModules());
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

describe("authentication read recovery", () => {
  it("retains confirmed 401 without waiting for an error body", async () => {
    const json = vi.fn(() => new Promise(() => {}));
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 401, json }));
    const api = await import("./product-api");
    await expect(api.getAuthUser()).rejects.toMatchObject({ status: 401 });
    expect(json).not.toHaveBeenCalled();
  });

  it.each(["transport", "body"])("bounds stalled %s and lets the next read recover", async phase => {
    vi.useFakeTimers();
    const stalled = new Promise(() => {});
    const fetchMock = vi.fn().mockReturnValueOnce(phase === "transport" ? stalled : Promise.resolve({ ok: true, status: 200, json: () => stalled }))
      .mockResolvedValueOnce(Response.json(user));
    vi.stubGlobal("fetch", fetchMock);
    const api = await import("./product-api");
    const first = api.getAuthUser();
    expect(api.getAuthUser()).toBe(first);
    const failure = expect(first).rejects.toMatchObject({ message: "登录状态读取超时，请重新连接。", status: undefined });
    await vi.advanceTimersByTimeAsync(10_000);
    await failure;
    expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(true);
    expect(await api.getAuthUser()).toEqual(user);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("does not let a late expired response clear a newer login", async () => {
    vi.useFakeTimers();
    let deliver!: (value: Response) => void;
    const fetchMock = vi.fn().mockReturnValueOnce(new Promise<Response>(resolve => { deliver = resolve; }))
      .mockResolvedValueOnce(Response.json(user));
    vi.stubGlobal("fetch", fetchMock);
    const api = await import("./product-api");
    const failure = expect(api.getAuthUser()).rejects.toThrow("读取超时");
    await vi.advanceTimersByTimeAsync(10_000);
    await failure;
    await api.login("research@example.invalid", "test-only");
    deliver(new Response(null, { status: 401 }));
    await vi.advanceTimersByTimeAsync(0);
    expect(await api.getAuthUser()).toEqual(user);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("does not publish an old profile after the account has changed", async () => {
    let deliver!: (value: unknown) => void;
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce({ ok: true, status: 200, json: () => new Promise(resolve => { deliver = resolve; }) })
      .mockResolvedValueOnce(Response.json(user)));
    const api = await import("./product-api");
    const pending = api.getAuthUser();
    const failure = expect(pending).rejects.toThrow("登录状态已变化");
    await vi.waitFor(() => expect(deliver).toBeTypeOf("function"));
    await api.login("research@example.invalid", "test-only");
    deliver({ ...user, id: "former-user" });
    await failure;
    expect(await api.getAuthUser()).toEqual(user);
  });

  it("does not revive a signed-out account from an earlier read", async () => {
    let deliver!: (value: unknown) => void;
    const fetchMock = vi.fn().mockResolvedValueOnce({ ok: true, status: 200, json: () => new Promise(resolve => { deliver = resolve; }) })
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(new Response(null, { status: 401 }));
    vi.stubGlobal("fetch", fetchMock);
    const api = await import("./product-api");
    const failure = expect(api.getAuthUser()).rejects.toThrow("登录状态已变化");
    await vi.waitFor(() => expect(deliver).toBeTypeOf("function"));
    await api.logout();
    deliver(user);
    await failure;
    await expect(api.getAuthUser()).rejects.toMatchObject({ status: 401 });
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("keeps cancellation local to an owned authentication read", async () => {
    vi.stubGlobal("fetch", vi.fn().mockReturnValueOnce(new Promise(() => {})).mockResolvedValueOnce(Response.json(user)));
    const api = await import("./product-api");
    const controller = new AbortController();
    const pending = api.getAuthUser({ signal: controller.signal });
    const failure = expect(pending).rejects.toMatchObject({ name: "AbortError" });
    controller.abort();
    await failure;
    expect(await api.getAuthUser()).toEqual(user);
  });

  it("requires a fresh authentication read after another API reports expiry", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(Response.json(user))
      .mockResolvedValueOnce(new Response(null, { status: 401 }));
    vi.stubGlobal("fetch", fetchMock);
    const api = await import("./product-api");
    await api.login("research@example.invalid", "test-only");
    expect(await api.getAuthUser()).toEqual(user);
    api.invalidateProductAuth();
    await expect(api.getAuthUser()).rejects.toMatchObject({ status: 401 });
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it.each([null, {}, { id: "", displayName: "missing" }])("rejects an invalid successful auth response %j", async value => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(Response.json(value)).mockResolvedValueOnce(Response.json(user)));
    const api = await import("./product-api");
    await expect(api.getAuthUser()).rejects.toThrow("登录状态暂时无法读取");
    expect(await api.getAuthUser()).toEqual(user);
  });
});
