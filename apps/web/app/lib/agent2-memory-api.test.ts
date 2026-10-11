import { afterEach, describe, expect, it, vi } from "vitest";
import { getAgent2SessionMemory, pinAgent2Object, pinAgent2Result } from "./agent2-memory-api";

const memory = { project_id: "p", session_id: "s", version: 1, pinned_result_refs: [], pinned_object_refs: [], session_constraints: [] };
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });
describe("session memory transport", () => {
  it.each(["headers", "body"])("bounds stalled %s and aborts the transport", async (part) => {
    vi.useFakeTimers();
    const fetchMock = vi.fn().mockImplementation(() => part === "headers" ? new Promise(() => {}) : Promise.resolve({ ok: true, status: 200, json: () => new Promise(() => {}) }));
    vi.stubGlobal("fetch", fetchMock);
    const request = expect(getAgent2SessionMemory("p", "s")).rejects.toThrow("超时");
    await vi.advanceTimersByTimeAsync(10_001); await request;
    expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(true);
  });
  it("honors cancellation even if a response ignores abort", async () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise(() => {})));
    const controller = new AbortController(); const request = expect(pinAgent2Result("p", "s", "r", { signal: controller.signal })).rejects.toMatchObject({ name: "AbortError" });
    controller.abort(); await request;
  });
  it.each([{ project_id: "wrong" }, { session_id: "wrong" }, { version: "1" }, { pinned_object_refs: [{ object_id: "o" }] }, { session_constraints: null }])("rejects invalid saved context %j", async (patch) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...memory, ...patch }))));
    await expect(getAgent2SessionMemory("p", "s")).rejects.toThrow("不匹配");
  });
  it("reports expired authentication without reading an unbounded error body", async () => {
    const expired = vi.fn(); window.addEventListener("mdi:session-expired", expired);
    try {
      vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 401, json: () => new Promise(() => {}) }));
      await expect(pinAgent2Result("p", "s", "r")).rejects.toMatchObject({ status: 401 }); expect(expired).toHaveBeenCalledOnce();
    } finally { window.removeEventListener("mdi:session-expired", expired); }
  });
  it("sends the exact source version and rejects foreign scope before transmission", async () => {
    const source = { project_id: "p", object_id: "o", version_id: "v", object_type: "structure.crystal" };
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...memory, version: 2, pinned_object_refs: [source] })));
    vi.stubGlobal("fetch", fetchMock);
    await pinAgent2Object("p", "s", source);
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({ object_ref: source });
    await expect(pinAgent2Object("p", "s", { ...source, project_id: "foreign" })).rejects.toThrow("不匹配"); expect(fetchMock).toHaveBeenCalledOnce();
  });
});
