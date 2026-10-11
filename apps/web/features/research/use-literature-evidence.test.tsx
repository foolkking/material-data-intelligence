import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { type LiteratureCandidate } from "../../app/lib/scientific-knowledge-api";
import { useLiteratureEvidence } from "./use-literature-evidence";

const api = vi.hoisted(() => ({ list: vi.fn(), search: vi.fn(), select: vi.fn() }));
vi.mock("../../app/lib/scientific-knowledge-api", async (original) => ({
  ...await original<typeof import("../../app/lib/scientific-knowledge-api")>(),
  listTurnLiteratureEvidence: api.list, searchScientificLiterature: api.search, selectLiteratureEvidence: api.select,
}));
const candidate: LiteratureCandidate = { candidate_id: "candidate-1", work: { work_id: "work-1", canonical_key: "doi:example" }, possible_duplicate_of: [], snapshots: [{ snapshot_id: "snapshot-1", provider: "CROSSREF", title: "Read recovery fixture", authors: [], publication_status: "PEER_REVIEWED_ARTICLE", access_status: "METADATA_ONLY", retrieved_at: "2026-10-01T00:00:00Z" }] };
const evidence = { id: "evidence-1", work_id: "work-1", snapshot_id: "snapshot-1", title: "Saved citation", research_turn_id: "turn-1", project_id: "project-1" };
const deferred = <T,>() => { let resolve!: (value: T) => void; const promise = new Promise<T>((yes) => { resolve = yes; }); return { promise, resolve }; };
beforeEach(() => {
  vi.resetAllMocks();
  api.list.mockResolvedValue({ turnId: "turn-1", literatureEvidence: [] });
  api.search.mockResolvedValue({ candidates: [candidate] });
  api.select.mockResolvedValue({ evidence_id: "evidence-1", project_id: "project-1", research_turn_id: "turn-1", work_id: "work-1", snapshot_id: "snapshot-1" });
});
afterEach(() => vi.useRealTimers());

it("retains saved citations when a reread fails and rejects another Turn's directory", async () => {
  api.list.mockResolvedValueOnce({ turnId: "turn-1", literatureEvidence: [evidence] }).mockResolvedValueOnce({ turnId: "foreign", literatureEvidence: [] });
  const hook = renderHook(() => useLiteratureEvidence("project-1", "turn-1"));
  await waitFor(() => expect(hook.result.current.used).toHaveLength(1));
  await act(async () => { await hook.result.current.refreshUsed(); });
  expect(hook.result.current.readState).toBe("error");
  expect(hook.result.current.used).toEqual([evidence]);
});
it("bounds both stalled reads and search without losing the draft or prior candidates", async () => {
  vi.useFakeTimers(); api.list.mockReturnValueOnce(new Promise(() => {}));
  const hook = renderHook(() => useLiteratureEvidence("project-1", "turn-1"));
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(hook.result.current.readState).toBe("error");
  act(() => hook.result.current.setQuestion("diffusion"));
  await act(async () => { await hook.result.current.runSearch(); });
  expect(hook.result.current.candidates).toEqual([candidate]);
  api.search.mockReturnValueOnce(new Promise(() => {}));
  await act(async () => { void hook.result.current.runSearch(); void hook.result.current.runSearch(); await vi.advanceTimersByTimeAsync(10_000); });
  expect(api.search).toHaveBeenCalledTimes(2);
  expect(hook.result.current.operation).toBeNull();
  expect(hook.result.current.question).toBe("diffusion");
  expect(hook.result.current.candidates).toEqual([candidate]);
});
it("recovers an uncertain selection through a read without submitting it twice", async () => {
  const hook = renderHook(() => useLiteratureEvidence("project-1", "turn-1"));
  await waitFor(() => expect(hook.result.current.readState).toBe("ready"));
  api.select.mockRejectedValueOnce(new Error("lost")); api.list.mockRejectedValue(new Error("offline"));
  await act(async () => { await hook.result.current.useCandidate(candidate); });
  await waitFor(() => expect(hook.result.current.readState).toBe("error"));
  expect(hook.result.current.unconfirmed).toBe(true); expect(hook.result.current.operation).toBeNull();
  await act(async () => { await hook.result.current.useCandidate(candidate); });
  expect(api.select).toHaveBeenCalledTimes(1);
  api.list.mockResolvedValue({ turnId: "turn-1", literatureEvidence: [evidence] });
  await act(async () => { await hook.result.current.refreshUsed(); });
  expect(hook.result.current.unconfirmed).toBe(false); expect(hook.result.current.alreadyUsed(candidate)).toBe(true);
  await act(async () => { await hook.result.current.useCandidate(candidate); });
  expect(api.select).toHaveBeenCalledTimes(1);
});
it("times out selection and ignores a late acknowledgement after reread recovery", async () => {
  vi.useFakeTimers(); const old = deferred<unknown>(); api.select.mockReturnValueOnce(old.promise);
  const hook = renderHook(() => useLiteratureEvidence("project-1", "turn-1"));
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  api.list.mockResolvedValue({ turnId: "turn-1", literatureEvidence: [evidence] });
  await act(async () => { void hook.result.current.useCandidate(candidate); await vi.advanceTimersByTimeAsync(10_000); });
  expect(hook.result.current.used).toEqual([evidence]);
  await act(async () => old.resolve({ evidence_id: "foreign" }));
  expect(hook.result.current.error).toBe(""); expect(hook.result.current.used).toEqual([evidence]);
});
it("permits public metadata cache reuse within this project but rejects foreign search content", async () => {
  const hook = renderHook(() => useLiteratureEvidence("project-1", "turn-1"));
  act(() => hook.result.current.setQuestion("diffusion"));
  api.search.mockResolvedValueOnce({ candidates: [candidate], cacheStatus: "REUSED_FRESH_PUBLIC_METADATA", search: { project_id: "project-1", research_turn_id: "previous-turn" } });
  await act(async () => { await hook.result.current.runSearch(); });
  expect(hook.result.current.candidates).toEqual([candidate]);
  api.search.mockResolvedValueOnce({ candidates: [], search: { project_id: "foreign" } });
  await act(async () => { await hook.result.current.runSearch(); });
  expect(hook.result.current.candidates).toEqual([candidate]); expect(hook.result.current.error).toContain("暂未完成");
});
it("rejects invalid candidate snapshots before rendering or selecting them", async () => {
  const hook = renderHook(() => useLiteratureEvidence("project-1", "turn-1"));
  act(() => hook.result.current.setQuestion("diffusion"));
  api.search.mockResolvedValue({ candidates: [{ ...candidate, snapshots: [] }] });
  await act(async () => { await hook.result.current.runSearch(); });
  expect(hook.result.current.candidates).toEqual([]); expect(hook.result.current.error).toContain("暂未完成");
});
it("does not select before reading current usage or select withdrawn sources", async () => {
  api.list.mockRejectedValue(new Error("offline"));
  const hook = renderHook(() => useLiteratureEvidence("project-1", "turn-1"));
  await waitFor(() => expect(hook.result.current.readState).toBe("error"));
  await act(async () => { await hook.result.current.useCandidate(candidate); }); expect(api.select).not.toHaveBeenCalled();
  api.list.mockResolvedValue({ turnId: "turn-1", literatureEvidence: [] });
  await act(async () => { await hook.result.current.refreshUsed(); });
  await act(async () => { await hook.result.current.useCandidate({ ...candidate, snapshots: [{ ...candidate.snapshots[0], publication_status: "WITHDRAWN" }] }); });
  expect(api.select).not.toHaveBeenCalled();
});
it("aborts late search work when its keyed panel unmounts", async () => {
  const old = deferred<unknown>(); api.search.mockReturnValueOnce(old.promise);
  const hook = renderHook(() => useLiteratureEvidence("project-1", "turn-1"));
  act(() => hook.result.current.setQuestion("diffusion"));
  let pending!: Promise<void>; act(() => { pending = hook.result.current.runSearch(); });
  hook.unmount(); await pending; old.resolve({ candidates: [candidate] });
  expect(api.search.mock.calls[0][3].signal.aborted).toBe(true);
});
