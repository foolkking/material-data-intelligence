import { act, renderHook } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { useSessionOperation, validateResearchSession, validateSessionDirectory } from "./session-management";
afterEach(() => vi.useRealTimers());

it("guards duplicate saves and requires reconciliation after a timeout", async () => {
  vi.useFakeTimers();
  const { result } = renderHook(() => useSessionOperation("project_1"));
  const perform = vi.fn(() => new Promise<never>(() => {}));
  const accept = vi.fn();
  act(() => { void result.current.run("保存", perform, accept); void result.current.run("保存", perform, accept); });
  expect(perform).toHaveBeenCalledTimes(1);
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(result.current.pending).toBe(false);
  expect(result.current.uncertain).toBe(true);
  await act(async () => { await result.current.run("保存", perform, accept); });
  expect(perform).toHaveBeenCalledTimes(1);
  act(() => result.current.reconciled());
  await act(async () => { await result.current.run("保存", async () => "saved", accept); });
  expect(accept).toHaveBeenCalledWith("saved");
});

it("ignores a late saved result after dismissing a dialog or changing project", async () => {
  let finish!: (value: string) => void;
  const accept = vi.fn();
  const { result, rerender } = renderHook(({ project }) => useSessionOperation(project), { initialProps: { project: "one" } });
  act(() => { void result.current.run("重命名", () => new Promise(resolve => { finish = resolve; }), accept); });
  act(() => result.current.dismiss());
  await act(async () => finish("obsolete"));
  expect(accept).not.toHaveBeenCalled();
  expect(result.current.uncertain).toBe(true);
  rerender({ project: "two" });
  expect(result.current.uncertain).toBe(false);
  act(() => { void result.current.run("重命名", () => new Promise(resolve => { finish = resolve; }), accept); });
  rerender({ project: "three" });
  await act(async () => finish("different-project"));
  expect(accept).not.toHaveBeenCalled();
});

it("rejects ambiguous project identities and repeated directory records", () => {
  const item = { id: "a", project_id: "one", title: "研究", status: "active", created_at: "", updated_at: "" };
  expect(() => validateResearchSession({ ...item, projectId: "two" }, "one", "a")).toThrow();
  expect(() => validateResearchSession(item, "one", "b")).toThrow();
  expect(() => validateSessionDirectory([item, item], "one")).toThrow();
  expect(validateSessionDirectory([item], "one")).toEqual([item]);
});
