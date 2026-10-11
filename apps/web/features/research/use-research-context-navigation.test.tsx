import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { useResearchContextNavigation, validateContextManifest, validateTurnDirectory } from "./use-research-context-navigation";
import type { Agent2ContextManifestResponse, Agent2TurnResponse } from "../../app/lib/agent2-research-api";

const api = vi.hoisted(() => ({ getAgent2ContextManifest: vi.fn(), listAgent2ResearchTurns: vi.fn() }));
vi.mock("../../app/lib/agent2-research-api", async (original) => ({ ...await original<typeof import("../../app/lib/agent2-research-api")>(), ...api }));
const manifest = { turn_id: "t", manifest: { context_manifest_id: "m", project_id: "p", research_session_id: "s", research_turn_id: "t", operation: "PLANNER", included_items: [], excluded_items: [] } } as unknown as Agent2ContextManifestResponse;
const turns = [{ turn_id: "t", project_id: "p", research_session_id: "s", sequence_no: 1, user_message: { id: "message", content: "比较结构" } }] as Agent2TurnResponse[];
const flush = () => act(async () => {});
beforeEach(() => { vi.useFakeTimers(); vi.resetAllMocks(); api.getAgent2ContextManifest.mockResolvedValue(manifest); api.listAgent2ResearchTurns.mockResolvedValue(turns); });
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

it("retains both successful reads during a failed refresh and retries each independently", async () => {
  const view = renderHook(({ status }) => useResearchContextNavigation("p", "s", "t", status), { initialProps: { status: "RUNNING" } });
  await flush();
  api.getAgent2ContextManifest.mockRejectedValue(new Error("offline")); api.listAgent2ResearchTurns.mockRejectedValue(new Error("offline"));
  view.rerender({ status: "FAILED" }); await flush();
  expect(view.result.current.context).toMatchObject({ data: manifest, pending: false, failed: true });
  expect(view.result.current.directory).toMatchObject({ data: turns, pending: false, failed: true });
  api.getAgent2ContextManifest.mockResolvedValue(manifest);
  await act(async () => view.result.current.context.retry());
  expect(view.result.current.context.failed).toBe(false);
  expect(view.result.current.directory.failed).toBe(true);
  expect(api.listAgent2ResearchTurns).toHaveBeenCalledTimes(2);
  api.listAgent2ResearchTurns.mockResolvedValue(turns);
  await act(async () => view.result.current.directory.retry());
  expect(view.result.current.directory.failed).toBe(false);
  expect(api.getAgent2ContextManifest).toHaveBeenCalledTimes(3);
});

it.each(["context", "directory"] as const)("bounds a stalled %s read and rejects its late response after retry", async (part) => {
  const request = part === "context" ? api.getAgent2ContextManifest : api.listAgent2ResearchTurns;
  let finish!: (value: unknown) => void;
  request.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
  const view = renderHook(() => useResearchContextNavigation("p", "s", "t", "RUNNING"));
  await act(async () => { await vi.advanceTimersByTimeAsync(10_001); });
  expect(view.result.current[part]).toMatchObject({ pending: false, failed: true, data: null });
  expect(request.mock.calls[0].at(-1).signal.aborted).toBe(true);
  await act(async () => view.result.current[part].retry());
  expect(view.result.current[part].failed).toBe(false);
  await act(async () => finish(part === "context" ? { ...manifest, manifest: { ...manifest.manifest, context_manifest_id: "late" } } : []));
  expect(view.result.current[part].data).toEqual(part === "context" ? manifest : turns);
});

it("hides old scope synchronously and cancels reads when switching project or session", async () => {
  const renders: Array<ReturnType<typeof useResearchContextNavigation>> = [];
  const view = renderHook(({ project, session }) => { const value = useResearchContextNavigation(project, session, "t", "RUNNING"); renders.push(value); return value; }, { initialProps: { project: "p", session: "s" } });
  await flush();
  api.getAgent2ContextManifest.mockReturnValue(new Promise(() => {})); api.listAgent2ResearchTurns.mockReturnValue(new Promise(() => {}));
  const firstNew = renders.length;
  view.rerender({ project: "new", session: "other" });
  expect(renders.slice(firstNew).every((value) => !value.context.data && !value.directory.data)).toBe(true);
  view.unmount();
  expect(api.getAgent2ContextManifest.mock.calls.at(-1)?.at(-1).signal.aborted).toBe(true);
  expect(api.listAgent2ResearchTurns.mock.calls.at(-1)?.at(-1).signal.aborted).toBe(true);
});

it("keeps the directory when moving between turns but never reuses another turn's context", async () => {
  const view = renderHook(({ turn }) => useResearchContextNavigation("p", "s", turn, "FAILED"), { initialProps: { turn: "t" } });
  await flush();
  api.getAgent2ContextManifest.mockRejectedValue(new Error("offline")); api.listAgent2ResearchTurns.mockRejectedValue(new Error("offline"));
  view.rerender({ turn: "next" }); await flush();
  expect(view.result.current.context).toMatchObject({ data: null, failed: true });
  expect(view.result.current.directory).toMatchObject({ data: turns, failed: true });
});

it("immediately hides the directory when leaving the turn route", async () => {
  const renders: Array<ReturnType<typeof useResearchContextNavigation>> = [];
  const view = renderHook(({ turn }: { turn?: string }) => { const value = useResearchContextNavigation("p", "s", turn, "FAILED"); renders.push(value); return value; }, { initialProps: { turn: "t" } as { turn?: string } });
  await flush();
  const firstNew = renders.length;
  view.rerender({ turn: undefined });
  expect(renders.slice(firstNew).every((value) => !value.context.data && !value.directory.data)).toBe(true);
});

it("opens the latest owned context from a session without a Turn URL", async () => {
  const newest = { ...turns[0], turn_id: "latest", sequence_no: 3 };
  api.listAgent2ResearchTurns.mockResolvedValue([newest, turns[0]]);
  api.getAgent2ContextManifest.mockResolvedValue({ ...manifest, turn_id: "latest", manifest: { ...manifest.manifest, research_turn_id: "latest" } });
  const view = renderHook(() => useResearchContextNavigation("p", "s", undefined, undefined, true));
  await flush();
  expect(view.result.current.selectedTurnId).toBe("latest");
  expect(view.result.current.context.failed).toBe(false);
  expect(api.getAgent2ContextManifest).toHaveBeenCalledWith("latest", { signal: expect.any(AbortSignal) });
});

it("waits for every directory page before selecting the latest session context", async () => {
  const original = await vi.importActual<typeof import("../../app/lib/agent2-research-api")>("../../app/lib/agent2-research-api");
  api.listAgent2ResearchTurns.mockImplementation(original.listAgent2ResearchTurns);
  const item = (sequence: number) => ({
    id: `t${sequence}`, project_id: "p", research_session_id: "s", sequence_no: sequence,
    parent_turn_id: sequence > 1 ? `t${sequence - 1}` : null, status: "COMPLETED", created_at: "2026-10-08T00:00:00Z",
    messages: [{ id: `m${sequence}`, role: "USER", content: `问题 ${sequence}`, created_at: "2026-10-08T00:00:00Z" }],
  });
  let finish!: (response: Response) => void;
  vi.stubGlobal("fetch", vi.fn()
    .mockResolvedValueOnce(Response.json({ items: Array.from({ length: 50 }, (_, index) => item(index + 1)), next_cursor: 50 }))
    .mockImplementationOnce(() => new Promise(resolve => { finish = resolve; })));
  api.getAgent2ContextManifest.mockResolvedValue({ ...manifest, turn_id: "t51", manifest: { ...manifest.manifest, research_turn_id: "t51" } });
  const view = renderHook(() => useResearchContextNavigation("p", "s", undefined, undefined, true));
  await flush();
  expect(view.result.current.directory).toMatchObject({ data: null, pending: true });
  expect(view.result.current.selectedTurnId).toBeUndefined();
  expect(api.getAgent2ContextManifest).not.toHaveBeenCalled();
  await act(async () => finish(Response.json({ items: [item(51)], next_cursor: null })));
  expect(view.result.current.directory.data).toHaveLength(51);
  expect(view.result.current.selectedTurnId).toBe("t51");
  expect(view.result.current.directory.data?.at(-1)?.parent_turn_id).toBe("t50");
  expect(api.getAgent2ContextManifest).toHaveBeenCalledWith("t51", { signal: expect.any(AbortSignal) });
});

it("does not guess a context when a session directory is empty or unreadable", async () => {
  api.listAgent2ResearchTurns.mockResolvedValue([]);
  const view = renderHook(() => useResearchContextNavigation("p", "s", undefined, undefined, true));
  await flush();
  expect(view.result.current.selectedTurnId).toBeUndefined();
  expect(api.getAgent2ContextManifest).not.toHaveBeenCalled();
  api.listAgent2ResearchTurns.mockRejectedValue(new Error("offline"));
  await act(async () => view.result.current.directory.retry());
  expect(view.result.current.directory.failed).toBe(true);
  expect(api.getAgent2ContextManifest).not.toHaveBeenCalled();
});

it.each(["project_id", "research_session_id", "research_turn_id"] as const)("rejects a manifest with mismatched %s, including historical operations", (field) => {
  const foreign = { ...manifest.manifest, [field]: "wrong" };
  expect(() => validateContextManifest({ ...manifest, manifest: foreign }, "p", "s", "t")).toThrow();
  expect(() => validateContextManifest({ ...manifest, manifests: [{ operation: "PLANNER", manifest: foreign }] }, "p", "s", "t")).toThrow();
});

it("rejects missing or mismatched response identity and malformed collections", () => {
  for (const value of [null, { ...manifest, turn_id: "other" }, { ...manifest, manifest: null }, { ...manifest, manifests: {} }, { ...manifest, manifest: { ...manifest.manifest, included_items: null } }]) {
    expect(() => validateContextManifest(value as Agent2ContextManifestResponse, "p", "s", "t")).toThrow();
  }
});

it("accepts only source locations for result identities recorded in this response", () => {
  const response = { ...manifest, manifest: { ...manifest.manifest, included_items: [{
    item_id: "result_1", kind: "SCIENTIFIC_RESULT", authorization_checked: true,
    result_ref: "snapshot", server_side_source_identity: "snapshot",
  }] }, result_sources: [{ result_snapshot_id: "snapshot", project_id: "p", research_session_id: "original-session", research_turn_id: "original-turn" }] } as Agent2ContextManifestResponse;
  expect(validateContextManifest(response, "p", "s", "t")).toBe(response);
  for (const result_sources of [null, {}, [null],
    [{ ...response.result_sources![0], project_id: "wrong" }],
    [{ ...response.result_sources![0], result_snapshot_id: "unreferenced" }],
    [{ ...response.result_sources![0], research_session_id: "" }],
    [{ ...response.result_sources![0], research_turn_id: "" }],
    [...response.result_sources!, ...response.result_sources!],
  ]) expect(() => validateContextManifest({ ...response, result_sources } as Agent2ContextManifestResponse, "p", "s", "t")).toThrow();
});

it.each([{ project_id: "wrong" }, { research_session_id: "wrong" }, { id: "wrong" }, { user_message: null }, { sequence_no: undefined }])("rejects a directory containing foreign or malformed entries %j", (patch) => {
  expect(() => validateTurnDirectory([{ ...turns[0], ...patch }] as Agent2TurnResponse[], "p", "s")).toThrow();
});

it("distinguishes a confirmed empty directory from missing and duplicate records", () => {
  expect(validateTurnDirectory([], "p", "s")).toEqual([]);
  expect(() => validateTurnDirectory(null as unknown as Agent2TurnResponse[], "p", "s")).toThrow();
  expect(() => validateTurnDirectory([...turns, ...turns], "p", "s")).toThrow();
});
