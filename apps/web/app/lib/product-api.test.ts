import { afterEach, describe, expect, it, vi } from "vitest";

import {
  invalidateResearchSessionList,
  listNotificationReadStates,
  listResearchSessions,
  getResearchSession,
  createResearchSession,
  executeSavedProductSearch,
  login,
  safeApiDetail,
  updateResearchSession,
  updateSavedProductSearch,
  updateNotificationReadState,
  getAuthUser,
  listAuthSessions,
  updateAuthProfile,
  createPlatformInvitation,
  updatePlatformAdminUser,
  updatePlatformAdminProjectMember,
  removePlatformAdminProjectMember,
} from "./product-api";

afterEach(() => {
  invalidateResearchSessionList();
  vi.unstubAllGlobals();
  vi.useRealTimers();
  sessionStorage.clear();
});

it.each(["transport", "body"])("bounds session creation %s and reuses its request on manual retry", async stage => {
  vi.useFakeTimers();
  const stalled = new Promise<never>(() => {});
  const fetchMock = vi.fn().mockImplementationOnce(() => stage === "transport" ? stalled : Promise.resolve({ ok: true, status: 200, json: () => stalled }))
    .mockImplementation(async (_url, init) => {
      const body = JSON.parse(init.body);
      return new Response(JSON.stringify({ id: "session", title: body.title, project_id: "project", status: "active", creationKey: body.creationKey }));
    });
  vi.stubGlobal("fetch", fetchMock);
  const first = createResearchSession("project", "Question", "dataset");
  const failure = expect(first).rejects.toThrow("输入已保留");
  await vi.advanceTimersByTimeAsync(10_000);
  await failure;
  expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(true);
  const recovered = await createResearchSession("project", "Question", "dataset");
  expect(fetchMock.mock.calls[0][1].body).toBe(fetchMock.mock.calls[1][1].body);
  expect(recovered.id).toBe("session");
  await createResearchSession("project", "Question", "dataset");
  expect(JSON.parse(fetchMock.mock.calls[2][1].body).creationKey).not.toBe(recovered.creationKey);
});

describe("product API errors", () => {
  it("turns transport failures into an actionable service message", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    await expect(login("researcher@example.invalid", "not-a-real-secret"))
      .rejects.toThrow("服务暂时不可用，请检查连接后重试。");
  });

  it("does not expose a raw 500 status when the proxy returns no JSON detail", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("Bad gateway", {
      status: 500,
      headers: { "Content-Type": "text/plain" },
    })));

    await expect(login("researcher@example.invalid", "not-a-real-secret"))
      .rejects.toThrow("服务暂时不可用，请稍后重试。");
  });

  it("does not expose server details from a 500 response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({
      detail: "Connection refused at 127.0.0.1:8000",
    }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })));

    await expect(login("researcher@example.invalid", "not-a-real-secret"))
      .rejects.toThrow("服务暂时不可用，请稍后重试。");
  });

  it("preserves a safe server detail for a user-correctable client error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "邮箱或密码错误。" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    })));

    await expect(login("researcher@example.invalid", "not-a-real-secret"))
      .rejects.toThrow("邮箱或密码错误。");
  });

  it("projects structured validation details without rendering object coercion", () => {
    expect(safeApiDetail([
      { type: "missing", loc: ["body", "datasetId"], msg: "Field required" },
    ])).toBe("Field required");
    expect(safeApiDetail({ reason: "请选择一个明确的数据范围。" }))
      .toBe("请选择一个明确的数据范围。");
    expect(safeApiDetail([{ loc: ["body"] }]))
      .toBe("请求输入不完整，请检查后重试。");
  });
});

it("passes abort signals to each bounded administrative write", async () => {
  const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response("{}", { status: 200, headers: { "Content-Type": "application/json" } })));
  vi.stubGlobal("fetch", fetchMock);
  const signal = new AbortController().signal;
  await createPlatformInvitation("invited@example.invalid", "受邀者", 7, { signal });
  await updatePlatformAdminUser("user/2", { isActive: false }, { signal });
  await updatePlatformAdminProjectMember("project/1", "user/2", "viewer", { signal });
  await removePlatformAdminProjectMember("project/1", "user/2", { signal });
  for (const [index, path, method] of [[0, "/api/api/admin/invitations", "POST"], [1, "/api/api/admin/users/user%2F2", "PATCH"], [2, "/api/api/admin/projects/project%2F1/members/user%2F2", "PUT"], [3, "/api/api/admin/projects/project%2F1/members/user%2F2", "DELETE"]] as const) {
    expect(fetchMock.mock.calls[index]).toEqual([path, expect.objectContaining({ method, signal })]);
  }
});

describe("account-owned requests", () => {
  it("bypasses shared authentication cache for independently cancellable account reads", async () => {
    const cached = { id: "account_1", displayName: "旧名称" };
    const latest = { id: "account_1", displayName: "当前名称" };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(cached)))
      .mockResolvedValueOnce(new Response(JSON.stringify(latest)))
      .mockResolvedValueOnce(new Response(JSON.stringify({ items: [], count: 0 })));
    vi.stubGlobal("fetch", fetchMock);
    await login("account@example.invalid", "example-password");
    const controller = new AbortController();
    expect(await getAuthUser({ signal: controller.signal })).toEqual(latest);
    await listAuthSessions({ signal: controller.signal });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "/api/auth/me", expect.objectContaining({ signal: expect.any(AbortSignal), cache: "no-store" }));
    expect(fetchMock).toHaveBeenNthCalledWith(3, "/api/auth/sessions", expect.objectContaining({ signal: controller.signal, cache: "no-store" }));
  });

  it("does not replace the shared profile cache with an aborted late save", async () => {
    const cached = { id: "account_1", displayName: "当前名称" };
    let resolveBody!: (value: unknown) => void;
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(cached)))
      .mockResolvedValueOnce({ ok: true, status: 200, json: () => new Promise((resolve) => { resolveBody = resolve; }) }));
    await login("account@example.invalid", "example-password");
    const controller = new AbortController();
    const save = updateAuthProfile("迟到的名称", { signal: controller.signal });
    const rejection = expect(save).rejects.toBeDefined();
    await vi.waitFor(() => expect(resolveBody).toBeTypeOf("function"));
    controller.abort();
    resolveBody({ id: "account_1", displayName: "迟到的名称" });
    await rejection;
    expect(await getAuthUser()).toEqual(cached);
  });
});

describe("saved search API", () => {
  it("updates filters and executes them through the bounded server route", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({
        id: "saved_1",
        name: "结构历史",
        query: "silicon",
        type: "scientific_object",
        project: "project_1",
        status: "archived",
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        savedSearch: {
          id: "saved_1",
          name: "结构历史",
          query: "silicon",
          type: "scientific_object",
          project: "project_1",
          status: "archived",
        },
        query: "silicon",
        count: 0,
        items: [],
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }));
    vi.stubGlobal("fetch", fetchMock);

    await updateSavedProductSearch("saved_1", {
      query: "silicon",
      type: "scientific_object",
      project: "project_1",
      status: "archived",
    });
    await executeSavedProductSearch("saved_1", 25);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "/api/saved-searches/saved_1",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({
          query: "silicon",
          type: "scientific_object",
          project: "project_1",
          status: "archived",
        }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/saved-searches/saved_1/execute",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ limit: 25 }),
      }),
    );
  });
});

describe("notification read state API", () => {
  it("loads and persists user-owned read markers through the authorized routes", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({
        schemaVersion: "NotificationReadState/1.0",
        items: [],
        count: 0,
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        projectId: "project_1",
        jobId: "job_1",
        read: true,
        readAt: "2026-09-05T08:00:00Z",
        notificationUpdatedAt: "2026-09-05T07:00:00Z",
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }));
    vi.stubGlobal("fetch", fetchMock);

    const controller = new AbortController();
    await listNotificationReadStates({ signal: controller.signal });
    await updateNotificationReadState("project_1", "job_1", true, { signal: controller.signal });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "/api/api/notifications/read-state",
      expect.objectContaining({ credentials: "include", signal: controller.signal }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/api/notifications/project_1/job_1/read-state",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ read: true }),
        signal: controller.signal,
      }),
    );
  });
});

describe("research session list cache", () => {
  it("invalidates prewarmed lifecycle state after a session mutation", async () => {
    const active = {
      id: "session_1",
      project_id: "project_1",
      title: "结构研究",
      status: "active",
      lifecycle: "ACTIVE",
    };
    const archived = { ...active, lifecycle: "ARCHIVED" };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([active]), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }))
      .mockResolvedValueOnce(new Response(JSON.stringify(archived), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }))
      .mockResolvedValueOnce(new Response(JSON.stringify([archived]), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }));
    vi.stubGlobal("fetch", fetchMock);

    const first = await listResearchSessions("project_1");
    const prewarmed = await listResearchSessions("project_1");
    expect(first).toEqual([active]);
    expect(prewarmed).toBe(first);
    expect(fetchMock).toHaveBeenCalledTimes(1);

    await updateResearchSession("session_1", { lifecycle: "ARCHIVED" });
    const refreshed = await listResearchSessions("project_1");

    expect(refreshed).toEqual([archived]);
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "/api/projects/project_1/research-sessions",
      expect.objectContaining({ credentials: "include" }),
    );
  });
});

it("keeps owned session reads outside the shared warm cache and carries their cancellation", async () => {
  const shared = [{ id: "one", project_id: "project", title: "shared", status: "active" }];
  const owned = [{ ...shared[0], title: "fresh" }];
  const fetchMock = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify(shared))).mockResolvedValueOnce(new Response(JSON.stringify(owned))).mockResolvedValueOnce(new Response(JSON.stringify(owned[0])));
  vi.stubGlobal("fetch", fetchMock);
  expect(await listResearchSessions("project")).toEqual(shared);
  const controller = new AbortController();
  expect(await listResearchSessions("project", controller.signal)).toEqual(owned);
  expect(await listResearchSessions("project")).toEqual(shared);
  expect(await getResearchSession("one", controller.signal)).toEqual(owned[0]);
  expect(fetchMock).toHaveBeenNthCalledWith(2, "/api/projects/project/research-sessions", expect.objectContaining({ signal: controller.signal, cache: "no-store" }));
  expect(fetchMock).toHaveBeenNthCalledWith(3, "/api/research-sessions/one", expect.objectContaining({ signal: controller.signal }));
});
