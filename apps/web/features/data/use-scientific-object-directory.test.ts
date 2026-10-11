import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { listScientificObjects, type ScientificObjectSummary } from "../../app/lib/scientific-viewer-api";
import { useScientificObjectDirectory } from "./use-scientific-object-directory";

vi.mock("../../app/lib/scientific-viewer-api", () => ({ listScientificObjects: vi.fn() }));
const list = vi.mocked(listScientificObjects);
const item = (id: string): ScientificObjectSummary => ({ id, project_id: "p1", kind: "scientific_object", object_type: "materials.dataset", display_name: id, current_version_id: "v1", lifecycle_status: "ACTIVE" });
beforeEach(() => list.mockReset());
afterEach(() => vi.useRealTimers());

it("retains loaded pages on failure and retries only the failed cursor without duplicates", async () => {
  list.mockResolvedValueOnce({ items: [item("a")], next_cursor: "a" })
    .mockRejectedValueOnce(new Error("private detail"))
    .mockResolvedValueOnce({ items: [item("a"), item("b")], next_cursor: null });
  const { result } = renderHook(() => useScientificObjectDirectory("p1", "ACTIVE"));
  await waitFor(() => expect(result.current.state).toBe("ready"));
  act(() => { result.current.loadMore(); result.current.loadMore(); });
  await waitFor(() => expect(result.current.state).toBe("error"));
  expect(result.current.items.map(({ id }) => id)).toEqual(["a"]);
  expect(result.current.error).not.toContain("private detail");
  act(() => result.current.retry());
  await waitFor(() => expect(result.current.state).toBe("ready"));
  expect(result.current.items.map(({ id }) => id)).toEqual(["a", "b"]);
  expect(list.mock.calls.map((args) => args[3])).toEqual([undefined, "a", "a"]);
});

it("starts at the first page on lifecycle changes and revisits", async () => {
  list.mockImplementation(async (_projectId, _signal, lifecycle) => ({ items: [{ ...item("a"), lifecycle_status: lifecycle || "ACTIVE" }], next_cursor: "a" }));
  const { result, rerender } = renderHook(({ lifecycle }: { lifecycle: "ACTIVE" | "ARCHIVED" }) => useScientificObjectDirectory("p1", lifecycle), { initialProps: { lifecycle: "ACTIVE" } });
  await waitFor(() => expect(result.current.state).toBe("ready"));
  act(() => result.current.loadMore());
  await waitFor(() => expect(result.current.state).toBe("ready"));
  rerender({ lifecycle: "ARCHIVED" });
  await waitFor(() => expect(result.current.state).toBe("ready"));
  rerender({ lifecycle: "ACTIVE" });
  await waitFor(() => expect(result.current.state).toBe("ready"));
  expect(list.mock.calls.map((args) => [args[2], args[3]])).toEqual([["ACTIVE", undefined], ["ACTIVE", "a"], ["ARCHIVED", undefined], ["ACTIVE", undefined]]);
});

it("bounds stalls and ignores late pages after project changes or retry", async () => {
  vi.useFakeTimers();
  let finish!: (value: { items: ScientificObjectSummary[]; next_cursor: null }) => void;
  list.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
  const { result, rerender } = renderHook(({ projectId }) => useScientificObjectDirectory(projectId, "ACTIVE"), { initialProps: { projectId: "p1" } });
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(result.current.error).toContain("读取超时");
  expect(list.mock.calls[0][1]?.aborted).toBe(true);
  list.mockResolvedValueOnce({ items: [item("recovered")], next_cursor: null });
  await act(async () => result.current.retry());
  await act(async () => finish({ items: [item("obsolete")], next_cursor: null }));
  expect(result.current.items[0].id).toBe("recovered");
  list.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
  rerender({ projectId: "p2" });
  expect(result.current.items).toEqual([]);
  list.mockResolvedValueOnce({ items: [{ ...item("new-project"), project_id: "p3" }], next_cursor: null });
  rerender({ projectId: "p3" });
  await act(async () => {});
  await act(async () => finish({ items: [item("old-project")], next_cursor: null }));
  expect(result.current.items[0].id).toBe("new-project");
});

it.each(["project", "lifecycle", "duplicates"])("rejects a mismatched %s directory without removing a previously read page", async (kind) => {
  list.mockResolvedValueOnce({ items: [item("a")], next_cursor: "next" });
  const view = renderHook(() => useScientificObjectDirectory("p1", "ACTIVE"));
  await waitFor(() => expect(view.result.current.state).toBe("ready"));
  const bad = kind === "project" ? { ...item("b"), project_id: "other" } : kind === "lifecycle" ? { ...item("b"), lifecycle_status: "TRASHED" } : item("b");
  list.mockResolvedValueOnce({ items: kind === "duplicates" ? [bad, bad] : [bad], next_cursor: null });
  act(() => view.result.current.loadMore());
  await waitFor(() => expect(view.result.current.state).toBe("error"));
  expect(view.result.current.items).toEqual([item("a")]);
});
