import { afterEach, describe, expect, it, vi } from "vitest";

import {
  invalidateResearchSessionList,
  listNotificationReadStates,
  listResearchSessions,
  executeSavedProductSearch,
  login,
  safeApiDetail,
  updateResearchSession,
  updateSavedProductSearch,
  updateNotificationReadState,
} from "./product-api";

afterEach(() => {
  invalidateResearchSessionList();
  vi.unstubAllGlobals();
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

    await listNotificationReadStates();
    await updateNotificationReadState("project_1", "job_1", true);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "/api/api/notifications/read-state",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/api/notifications/project_1/job_1/read-state",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ read: true }),
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
