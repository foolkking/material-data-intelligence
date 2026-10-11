import { act, render, renderHook, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import { DependencyPreviewFeedback, useDependencyPreview } from "../../shared/ui/DependencyPreview";

const targets = [{ id: "a", label: "Alpha" }, { id: "b", label: "Beta" }];

it("retains successful dependency previews and retries only failed targets", async () => {
  const read = vi.fn().mockImplementation(async (id: string) => {
    if (id === "b") throw new Error("private storage exception");
    return { count: 7 };
  });
  function Preview() {
    const preview = useDependencyPreview<{ count: number }>(targets, read);
    return <><output>{preview.items.reduce((sum, item) => sum + item.count, 0)}</output><DependencyPreviewFeedback preview={preview} /><button disabled={!preview.complete}>确认</button></>;
  }
  render(<Preview />);
  const failure = await screen.findByRole("alert");
  expect(failure).toHaveTextContent("Beta：暂时无法读取");
  expect(failure).not.toHaveTextContent("private storage exception");
  expect(screen.getByRole("status")).toHaveTextContent("7");
  expect(screen.getByRole("button", { name: "确认" })).toBeDisabled();
  read.mockResolvedValue({ count: 3 });
  await userEvent.setup().click(screen.getByRole("button", { name: "重新检查依赖" }));
  await waitFor(() => expect(screen.getByRole("button", { name: "确认" })).toBeEnabled());
  expect(screen.getByRole("status")).toHaveTextContent("10");
  expect(read.mock.calls.map(([id]) => id)).toEqual(["a", "b", "b"]);
});

it("ends a stalled preview after ten seconds while retaining completed siblings", async () => {
  let late!: (value: number) => void;
  let stalledSignal!: AbortSignal;
  const read = vi.fn((id: string, signal?: AbortSignal) => id === "a" ? Promise.resolve(7) : new Promise<number>((resolve) => { late = resolve; stalledSignal = signal!; }));
  vi.useFakeTimers();
  try {
    const { result, unmount } = renderHook(() => useDependencyPreview(targets, read));
    await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
    expect(result.current.items).toEqual([7]);
    expect(result.current.pendingCount).toBe(0);
    expect(result.current.complete).toBe(false);
    expect(result.current.entries[1].error).toBe("检查超时");
    expect(stalledSignal.aborted).toBe(true);
    await act(async () => { late(99); });
    expect(result.current.items).toEqual([7]);
    unmount();
  } finally { vi.useRealTimers(); }
});

it("cancels abandoned previews and rejects late responses across target changes", async () => {
  let late!: (value: number) => void;
  let oldSignal!: AbortSignal;
  const read = vi.fn((id: string, signal?: AbortSignal) => id === "a" ? new Promise<number>((resolve) => { late = resolve; oldSignal = signal!; }) : Promise.resolve(3));
  const { result, rerender, unmount } = renderHook(({ selected }) => useDependencyPreview(selected, read), { initialProps: { selected: [targets[0]] } });
  rerender({ selected: [targets[1]] });
  await waitFor(() => expect(result.current.items).toEqual([3]));
  expect(oldSignal.aborted).toBe(true);
  await act(async () => { late(99); });
  expect(result.current.items).toEqual([3]);
  rerender({ selected: [] });
  expect(result.current.items).toEqual([]);
  expect(result.current.complete).toBe(false);
  unmount();
});
