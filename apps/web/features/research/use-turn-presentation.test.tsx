import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { useTurnPresentation } from "./use-turn-presentation";

const api = vi.hoisted(() => ({ result: vi.fn(), interpretation: vi.fn() }));
vi.mock("../../app/lib/agent2-research-api", () => ({ getAgent2ResearchTurnResult: api.result, getAgent2ResearchTurnInterpretation: api.interpretation }));
const result = (turn = "turn-a") => ({ result_id: `result-${turn}`, research_turn_id: turn, source_object_refs: [], facts: [], artifacts: [] });
const interpretation = (turn = "turn-a") => ({ interpretation_id: `interpretation-${turn}`, research_turn_id: turn, status: "VALID", message: "已保存的解读" });
const deferred = <T,>() => { let resolve!: (value: T) => void; const promise = new Promise<T>((yes) => { resolve = yes; }); return { promise, resolve }; };
beforeEach(() => { vi.resetAllMocks(); api.result.mockResolvedValue(result()); api.interpretation.mockResolvedValue(interpretation()); });
afterEach(() => vi.useRealTimers());

it("keeps the original result owner when reading an authorized reinterpretation view", async () => {
  const reused = { ...result(), result_id: "original-result", result_snapshot_id: "original-snapshot", source_research_turn_id: "original-turn" };
  api.result.mockResolvedValue(reused);
  api.interpretation.mockRejectedValue(Object.assign(new Error("not ready"), { code: "SCIENTIFIC_RESULT_NOT_READY" }));
  const hook = renderHook(() => useTurnPresentation("project-a", "turn-a"));
  await waitFor(() => expect(hook.result.current.result.value).toEqual(reused));
  await waitFor(() => expect(hook.result.current.interpretation.notReady).toBe(true));
  expect(hook.result.current.result.failed).toBe(false);
  expect(hook.result.current.result.value?.research_turn_id).toBe("turn-a");
  expect(hook.result.current.result.value?.source_research_turn_id).toBe("original-turn");
});

it("distinguishes an absent interpretation from a failed read and recovers on reread", async () => {
  api.interpretation.mockRejectedValueOnce(Object.assign(new Error("not ready"),{code:"SCIENTIFIC_RESULT_NOT_READY"}));
  const hook=renderHook(()=>useTurnPresentation("project-a","turn-a"));
  await waitFor(()=>expect(hook.result.current.interpretation.notReady).toBe(true));
  expect(hook.result.current.result.value).toEqual(result());
  act(()=>hook.result.current.interpretation.retry());
  await waitFor(()=>expect(hook.result.current.interpretation.value).toEqual(interpretation()));
  expect(hook.result.current.interpretation.notReady).toBeFalsy();
});

it("waits for interpretation completion while retaining the already visible result", async () => {
  const hook = renderHook(({ ready }) => useTurnPresentation("project-a", "turn-a", ready), { initialProps: { ready: false } });
  await waitFor(() => expect(hook.result.current.result.value).toEqual(result()));
  const saved = hook.result.current.result.value;
  expect(api.interpretation).not.toHaveBeenCalled();
  expect(hook.result.current.interpretation.failed).toBe(false);
  hook.rerender({ ready: true });
  await waitFor(() => expect(hook.result.current.interpretation.value).toEqual(interpretation()));
  expect(hook.result.current.result.value).toBe(saved);
  expect(api.result).toHaveBeenCalledTimes(1);
  expect(api.interpretation).toHaveBeenCalledTimes(1);
});

it("reads result and interpretation independently and retries only the failed sibling", async () => {
  api.interpretation.mockRejectedValueOnce(new Error("offline"));
  const hook = renderHook(() => useTurnPresentation("project-a", "turn-a"));
  await waitFor(() => expect(hook.result.current.interpretation.failed).toBe(true));
  const saved = hook.result.current.result.value;
  expect(saved).toEqual(result());
  act(() => hook.result.current.interpretation.retry());
  await waitFor(() => expect(hook.result.current.interpretation.value).toEqual(interpretation()));
  expect(hook.result.current.result.value).toBe(saved);
  expect(api.result).toHaveBeenCalledTimes(1);
});
it("retains a saved interpretation when only result reading needs recovery", async () => {
  api.result.mockRejectedValueOnce(new Error("offline"));
  const hook = renderHook(() => useTurnPresentation("project-a", "turn-a"));
  await waitFor(() => expect(hook.result.current.result.failed).toBe(true));
  expect(hook.result.current.interpretation.value).toEqual(interpretation());
  act(() => hook.result.current.result.retry());
  await waitFor(() => expect(hook.result.current.result.value).toEqual(result()));
  expect(api.interpretation).toHaveBeenCalledTimes(1);
});
it("bounds a stalled read, retries once and ignores the old successful response", async () => {
  vi.useFakeTimers(); const old = deferred<ReturnType<typeof result>>();
  api.result.mockReturnValueOnce(old.promise);
  const hook = renderHook(() => useTurnPresentation("project-a", "turn-a"));
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(hook.result.current.result.failed).toBe(true);
  expect(api.result.mock.calls[0][1].signal.aborted).toBe(true);
  await act(async () => { hook.result.current.result.retry(); hook.result.current.result.retry(); });
  expect(api.result).toHaveBeenCalledTimes(2);
  const saved = hook.result.current.result.value;
  await act(async () => old.resolve({ ...result(), result_id: "old-late" }));
  expect(hook.result.current.result.value).toBe(saved);
});
it("retains usable content and its identity when a reread fails", async () => {
  const hook = renderHook(() => useTurnPresentation("project-a", "turn-a"));
  await waitFor(() => expect(hook.result.current.result.value).toEqual(result()));
  const saved = hook.result.current.result.value;
  api.result.mockRejectedValueOnce(new Error("offline"));
  act(() => hook.result.current.result.retry());
  await waitFor(() => expect(hook.result.current.result.failed).toBe(true));
  expect(hook.result.current.result.value).toBe(saved);
});
it("hides old content immediately on scope changes and rejects late responses", async () => {
  const old = deferred<ReturnType<typeof interpretation>>();
  api.interpretation.mockReturnValueOnce(old.promise);
  const hook = renderHook(({ turn }) => useTurnPresentation("project-a", turn), { initialProps: { turn: "turn-a" } });
  await waitFor(() => expect(hook.result.current.result.value).toEqual(result()));
  api.result.mockResolvedValue(result("turn-b")); api.interpretation.mockResolvedValue(interpretation("turn-b"));
  hook.rerender({ turn: "turn-b" });
  expect(hook.result.current.result.value).toBeNull();
  await waitFor(() => expect(hook.result.current.result.value).toEqual(result("turn-b")));
  await act(async () => old.resolve(interpretation()));
  expect(hook.result.current.interpretation.value).toEqual(interpretation("turn-b"));
});
it.each(["turn", "project"])("rejects a mismatched %s identity", async (identity) => {
  api.result.mockResolvedValue(identity === "turn" ? result("foreign") : { ...result(), source_object_refs: [{ project_id: "foreign" }] });
  api.interpretation.mockResolvedValue(interpretation("foreign"));
  const hook = renderHook(() => useTurnPresentation("project-a", "turn-a"));
  await waitFor(() => expect(hook.result.current.result.failed).toBe(true));
  expect(hook.result.current.result.value).toBeNull();
  expect(hook.result.current.interpretation.value).toBeNull();
  expect(hook.result.current.interpretation.failed).toBe(true);
});
