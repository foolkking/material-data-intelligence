import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { watchLegacyJob } from "./legacy-job-polling";

const api = vi.hoisted(() => ({ getPlannerJob: vi.fn(), getPlannerJobEvents: vi.fn(), getPlannerJobArtifacts: vi.fn() }));
vi.mock("../../app/lib/planner-api", () => api);
beforeEach(() => {
  vi.useFakeTimers();
  vi.resetAllMocks();
  api.getPlannerJob.mockResolvedValue({ jobId: "job", projectId: "project", status: "running" });
  api.getPlannerJobEvents.mockResolvedValue([]);
  api.getPlannerJobArtifacts.mockResolvedValue([]);
});
afterEach(() => vi.useRealTimers());
const listeners = () => ({ detail: vi.fn(), events: vi.fn(), artifacts: vi.fn(), failure: vi.fn() });

it("reaches a durable terminal state while both optional streams are stalled, then ignores their late responses", async () => {
  let resolveEvents!: (value: unknown) => void;
  api.getPlannerJobEvents.mockImplementationOnce(() => new Promise((resolve) => { resolveEvents = resolve; })).mockResolvedValue([{ jobId: "job", seq: 9 }]);
  api.getPlannerJobArtifacts.mockImplementationOnce(() => new Promise(() => {})).mockResolvedValue([{ jobId: "job", artifactId: "final" }]);
  api.getPlannerJob.mockResolvedValueOnce({ jobId: "job", status: "running" }).mockResolvedValue({ jobId: "job", status: "completed" });
  const callbacks = listeners(), stop = watchLegacyJob("job", "project", callbacks);
  await vi.advanceTimersByTimeAsync(1400);
  expect(callbacks.detail).toHaveBeenLastCalledWith(expect.objectContaining({ status: "completed" }));
  expect(callbacks.events).not.toHaveBeenCalled();
  await vi.advanceTimersByTimeAsync(8601);
  expect(callbacks.failure).toHaveBeenCalledWith("运行记录", true);
  expect(callbacks.events).toHaveBeenLastCalledWith([{ jobId: "job", seq: 9 }]);
  expect(callbacks.artifacts).toHaveBeenLastCalledWith([{ jobId: "job", artifactId: "final" }]);
  const count = callbacks.events.mock.calls.length;
  resolveEvents([{ jobId: "job", seq: 1 }]);
  await vi.advanceTimersByTimeAsync(0);
  expect(callbacks.events).toHaveBeenCalledTimes(count);
  stop();
  expect(vi.getTimerCount()).toBe(0);
});

it("retains independent results during a status timeout, retries, and rejects mismatched status identities", async () => {
  api.getPlannerJob.mockImplementationOnce(() => new Promise(() => {}))
    .mockResolvedValueOnce({ jobId: "other-job", status: "completed" })
    .mockResolvedValue({ jobId: "job", status: "cancelled" });
  api.getPlannerJobArtifacts.mockResolvedValue([{ jobId: "job", artifactId: "kept" }]);
  const callbacks = listeners(), stop = watchLegacyJob("job", "project", callbacks);
  await vi.advanceTimersByTimeAsync(10000);
  expect(callbacks.artifacts).toHaveBeenCalledWith([{ jobId: "job", artifactId: "kept" }]);
  expect(callbacks.failure).toHaveBeenCalledWith("运行详情", true);
  await vi.advanceTimersByTimeAsync(2500);
  expect(callbacks.detail).not.toHaveBeenCalled();
  await vi.advanceTimersByTimeAsync(5000);
  expect(callbacks.detail).toHaveBeenCalledWith(expect.objectContaining({ status: "cancelled" }));
  expect(callbacks.failure).toHaveBeenLastCalledWith(expect.any(String), false);
  stop();
});

it("reads events after the last accepted sequence and obtains final artifacts after completion", async () => {
  api.getPlannerJobEvents.mockResolvedValueOnce([{ jobId: "job", seq: 5 }]).mockResolvedValue([{ jobId: "job", seq: 6 }]);
  api.getPlannerJob.mockResolvedValueOnce({ jobId: "job", status: "running" }).mockResolvedValue({ jobId: "job", status: "completed" });
  api.getPlannerJobArtifacts.mockResolvedValueOnce([]).mockResolvedValue([{ jobId: "job", artifactId: "final" }]);
  const callbacks = listeners(), stop = watchLegacyJob("job", "project", callbacks);
  await vi.advanceTimersByTimeAsync(1401);
  expect(api.getPlannerJobEvents).toHaveBeenCalledWith("job", 5, expect.anything());
  expect(callbacks.artifacts).toHaveBeenLastCalledWith([{ jobId: "job", artifactId: "final" }]);
  const calls = api.getPlannerJob.mock.calls.length;
  await vi.advanceTimersByTimeAsync(20000);
  expect(api.getPlannerJob).toHaveBeenCalledTimes(calls);
  stop();
});

it("aborts owned requests and prevents late callbacks and scheduled retries after navigation", async () => {
  let resolveDetail!: (value: unknown) => void;
  api.getPlannerJob.mockImplementationOnce(() => new Promise((resolve) => { resolveDetail = resolve; }));
  const callbacks = listeners(), stop = watchLegacyJob("job", "project", callbacks);
  await vi.advanceTimersByTimeAsync(0);
  const signal = api.getPlannerJob.mock.calls[0][1].signal as AbortSignal;
  stop();
  expect(signal.aborted).toBe(true);
  resolveDetail({ jobId: "job", status: "completed" });
  await vi.advanceTimersByTimeAsync(30000);
  expect(callbacks.detail).not.toHaveBeenCalled();
  expect(api.getPlannerJob).toHaveBeenCalledTimes(1);
  expect(vi.getTimerCount()).toBe(0);
});
