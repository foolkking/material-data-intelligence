import { afterEach, describe, expect, it, vi } from "vitest";

import { login } from "./product-api";

afterEach(() => {
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
});
