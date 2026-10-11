import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { Agent2ExecutionRequestError, type Agent2ProgressView } from "../../app/lib/agent2-execution-api";
import { ResearchSessionResult } from "./ResearchSessionResult";

const api = vi.hoisted(() => ({ read: vi.fn(), dispatch: vi.fn(), cancel: vi.fn() }));
vi.mock("../../app/lib/agent2-execution-api", async original => ({
  ...await original<typeof import("../../app/lib/agent2-execution-api")>(), getAgent2ExecutionProgress: api.read, cancelAgent2Execution: api.cancel,
}));
vi.mock("../../app/lib/agent2-research-api", () => ({ dispatchAgent2ResearchTurn: api.dispatch }));
vi.mock("../../shared/layout/ProductNavigation", () => ({ ProductLink: ({ scroll: _scroll, ...props }: any) => <a {...props} /> }));
vi.mock("./Agent2ScientificPresentation", () => ({ Agent2ScientificPresentation: ({ turnId, canModify }: any) =>
  <section aria-label="科学结果">{turnId}{canModify ? "可修改" : "只读"}</section> }));
const progress = (status: Agent2ProgressView["status"], turn_id = "exact") => ({
  turn_id, status, steps: [], incremental_outputs: [], warnings: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0,
});
beforeEach(() => { vi.useFakeTimers(); vi.resetAllMocks(); });
afterEach(() => { vi.useRealTimers(); });
const flush = () => act(async () => { await vi.advanceTimersByTimeAsync(0); });

it("recovers denied reads without a false empty result and refreshes messages once at terminal state", async () => {
  api.read.mockRejectedValueOnce(new Agent2ExecutionRequestError("private detail", 403)).mockResolvedValue(progress("RUNNING"));
  const onTerminal = vi.fn();
  const view = render(<ResearchSessionResult projectId="project" sessionId="session" turnId="exact" onTerminal={onTerminal} />);
  await flush();
  expect(screen.getByRole("heading", { name: "结果状态尚未确认" })).toBeInTheDocument();
  expect(screen.queryByText(/private detail|本次没有新的科学结果/)).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "重新读取进度" })); await flush();
  expect(screen.getByRole("heading", { name: "等待科学结果" })).toBeInTheDocument();
  api.read.mockResolvedValue(progress("COMPLETED"));
  await act(async () => { await vi.advanceTimersByTimeAsync(1800); });
  expect(screen.getByRole("region", { name: "科学结果" })).toHaveTextContent("exact只读");
  expect(onTerminal).toHaveBeenCalledTimes(1);
  window.dispatchEvent(new Event("online")); await flush();
  expect(onTerminal).toHaveBeenCalledTimes(1);
  expect(api.dispatch).not.toHaveBeenCalled(); expect(api.cancel).not.toHaveBeenCalled();
  view.unmount();
});

it("keeps saved results visible during a later read failure and removes them on a Turn switch", async () => {
  api.read.mockResolvedValue(progress("COMPLETED"));
  const onTerminal = vi.fn();
  const view = render(<ResearchSessionResult projectId="project" sessionId="session" turnId="exact" onTerminal={onTerminal} />);
  await flush();
  expect(onTerminal).not.toHaveBeenCalled();
  api.read.mockRejectedValueOnce(new Error("network unavailable"));
  window.dispatchEvent(new Event("online")); await flush();
  expect(screen.getByRole("region", { name: "科学结果" })).toHaveTextContent("exact只读");
  expect(screen.getByText("研究进度暂时无法读取，已打开的结果仍然保留。")).toBeInTheDocument();
  api.read.mockReturnValue(new Promise(() => {}));
  view.rerender(<ResearchSessionResult projectId="project" sessionId="session" turnId="other" onTerminal={onTerminal} />);
  expect(screen.queryByRole("region", { name: "科学结果" })).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: "打开这次研究" })).toHaveAttribute("href", "/projects/project/research/session?turn=other");
  view.unmount();
});
