import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { ScientificToolProcess } from "./ScientificToolProcess";

const api = vi.hoisted(() => vi.fn());
vi.mock("../../app/lib/planner-api", () => ({ getPlannerJobToolCalls: api }));
vi.mock("../../shared/ui/ArtifactOpenLink", () => ({ ArtifactOpenLink: ({ href, children }: { href: string; children: React.ReactNode }) => <a href={href}>{children}</a> }));
const artifacts = [{ id: "output-a", jobId: "job-a", toolCallId: "call-a", name: "轨迹数据" }, { id: "output-b", jobId: "job-a", toolCallId: "call-b", name: "轨迹摘要" }];
beforeEach(() => api.mockReset());
afterEach(() => vi.useRealTimers());

it("shows persisted calls and associates each output only with its exact call", async () => {
  api.mockResolvedValue([{ id: "call-a", jobId: "job-a", stepId: "step-a", toolId: "trajectory.inspect_view", status: "SUCCEEDED", inputSummary: "读取精确轨迹版本" }]);
  render(<ScientificToolProcess turnId="turn-a" artifacts={artifacts} />);
  expect(await screen.findByText("trajectory.inspect_view", { selector: "strong" })).toBeInTheDocument();
  expect(screen.getByText("已完成")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "轨迹数据" })).toHaveAttribute("href", "/api/planner/jobs/job-a/artifacts/output-a/content");
  expect(screen.queryByRole("link", { name: "轨迹摘要" })).not.toBeInTheDocument();
});

it("rejects foreign job records and recovers with a local retry", async () => {
  api.mockResolvedValueOnce([{ id: "call-a", jobId: "foreign", toolId: "foreign-tool" }]).mockResolvedValue([]);
  render(<ScientificToolProcess turnId="turn-a" artifacts={artifacts} />);
  fireEvent.click(await screen.findByRole("button", { name: "重新读取工具调用" }));
  expect(await screen.findByText("没有保存的工具调用记录。")).toBeInTheDocument();
  expect(screen.queryByText("foreign-tool")).not.toBeInTheDocument();
});

it("does not show calls from another attempt of the same job", async () => {
  api.mockResolvedValue([
    { id: "old-call", jobId: "job-a", toolId: "old-retry-tool", status: "FAILED" },
    { id: "call-a", jobId: "job-a", toolId: "saved-result-tool", status: "SUCCEEDED" },
  ]);
  render(<ScientificToolProcess turnId="turn-a" artifacts={artifacts} toolCallIds={["call-a"]} />);
  expect(await screen.findByText("saved-result-tool", { selector: "strong" })).toBeInTheDocument();
  expect(screen.queryByText("old-retry-tool")).not.toBeInTheDocument();
});

it("uses exact output producers for older responses without a call inventory", async () => {
  api.mockResolvedValue([
    { id: "unrelated", jobId: "job-a", toolId: "unrelated-tool" },
    { id: "call-a", jobId: "job-a", toolId: "source-tool" },
  ]);
  render(<ScientificToolProcess turnId="turn-a" artifacts={artifacts} />);
  expect(await screen.findByText("source-tool", { selector: "strong" })).toBeInTheDocument();
  expect(screen.queryByText("unrelated-tool")).not.toBeInTheDocument();
});

it("honors an explicit empty call inventory", async () => {
  api.mockResolvedValue([{ id: "call-a", jobId: "job-a", toolId: "unrecorded-tool" }]);
  render(<ScientificToolProcess turnId="turn-a" artifacts={artifacts} toolCallIds={[]} />);
  expect(await screen.findByText("没有保存的工具调用记录。")).toBeInTheDocument();
  expect(screen.queryByText("unrecorded-tool")).not.toBeInTheDocument();
});

it("updates the visible scope without borrowing cached calls from another result", async () => {
  api.mockResolvedValue([
    { id: "call-a", jobId: "job-a", toolId: "first-result-tool" },
    { id: "call-b", jobId: "job-a", toolId: "second-result-tool" },
  ]);
  const view = render(<ScientificToolProcess turnId="turn-a" artifacts={artifacts} toolCallIds={["call-a"]} />);
  expect(await screen.findByText("first-result-tool", { selector: "strong" })).toBeInTheDocument();
  view.rerender(<ScientificToolProcess turnId="turn-a" artifacts={artifacts} toolCallIds={["call-b"]} />);
  expect(screen.getByText("second-result-tool", { selector: "strong" })).toBeInTheDocument();
  expect(screen.queryByText("first-result-tool")).not.toBeInTheDocument();
  expect(api).toHaveBeenCalledTimes(1);
});

it("times out a stalled read and ignores its late result after recovery", async () => {
  vi.useFakeTimers();
  let finish!: (value: unknown) => void;
  api.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; })).mockResolvedValue([]);
  render(<ScientificToolProcess turnId="turn-a" artifacts={artifacts} />);
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(api.mock.calls[0][1].signal.aborted).toBe(true);
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新读取工具调用" })); });
  await act(async () => finish([{ id: "late", jobId: "job-a", toolId: "late-tool" }]));
  expect(screen.getByText("没有保存的工具调用记录。")).toBeInTheDocument();
  expect(screen.queryByText("late-tool")).not.toBeInTheDocument();
});
