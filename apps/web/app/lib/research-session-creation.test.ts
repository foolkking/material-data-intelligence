import { afterEach, expect, it, vi } from "vitest";
import type { ResearchSession } from "./product-api";
import { acknowledgeResearchSessionCreation, recoverResearchSessionCreation } from "./research-session-creation";

afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks(); sessionStorage.clear(); });

const accepted = (key: string) => ({
  id: "created-session", project_id: "project", title: "新对话", status: "active", creationKey: key,
}) as ResearchSession;

it("bounds a stalled request, keeps identity on retry, and ignores late success", async () => {
  vi.useFakeTimers();
  let resolve!: (value: ResearchSession) => void;
  const send = vi.fn((_body, _signal) => new Promise<ResearchSession>(done => { resolve = done; }));
  const first = recoverResearchSessionCreation("project", "Draft", undefined, "timeout", send);
  const rejection = expect(first).rejects.toThrow("输入已保留");
  await vi.advanceTimersByTimeAsync(10_000);
  await rejection;
  expect(send.mock.calls[0][1].aborted).toBe(true);
  const receipt = send.mock.calls[0][0].creationKey;
  resolve(accepted(receipt));
  await Promise.resolve();
  const retry = vi.fn(async body => accepted(body.creationKey));
  await recoverResearchSessionCreation("project", "Edited draft", undefined, "timeout", retry);
  expect(retry.mock.calls[0][0].creationKey).toBe(receipt);
  acknowledgeResearchSessionCreation(receipt);
  await recoverResearchSessionCreation("project", "Edited draft", undefined, "timeout", retry);
  expect(retry.mock.calls[1][0].creationKey).not.toBe(receipt);
});

it("retains an unadopted success across module reload and clears it only on composer receipt", async () => {
  const send = vi.fn(async body => accepted(body.creationKey));
  const first = await recoverResearchSessionCreation("project", "First", "dataset", "reload", send);
  vi.resetModules();
  const restored = await import("./research-session-creation");
  const next = await restored.recoverResearchSessionCreation("project", "Edited", "dataset", "reload", send);
  expect(next.creationKey).toBe(first.creationKey);
  restored.acknowledgeResearchSessionCreation(next.creationKey);
  const fresh = await restored.recoverResearchSessionCreation("project", "Edited", "dataset", "reload", send);
  expect(fresh.creationKey).not.toBe(first.creationKey);
});

it.each([401, 403, 422, 500])("keeps the pending key after HTTP %i", async status => {
  const send = vi.fn().mockRejectedValueOnce({ status }).mockImplementation(async body => accepted(body.creationKey));
  await expect(recoverResearchSessionCreation("project", "Draft", undefined, `status-${status}`, send)).rejects.toMatchObject({ status });
  await recoverResearchSessionCreation("project", "Draft", undefined, `status-${status}`, send);
  expect(send.mock.calls[0][0].creationKey).toBe(send.mock.calls[1][0].creationKey);
});

it.each(["project", "receipt", "missing"])("does not confirm a mismatched %s response", async mismatch => {
  const send = vi.fn(async body => mismatch === "missing" ? {} as ResearchSession : ({ ...accepted(body.creationKey),
    ...(mismatch === "project" ? { projectId: "foreign" } : { creationKey: crypto.randomUUID() }),
  }));
  await expect(recoverResearchSessionCreation("project", "Draft", undefined, mismatch, send)).rejects.toThrow("无法确认");
  send.mockImplementation(async body => accepted(body.creationKey));
  await recoverResearchSessionCreation("project", "Draft", undefined, mismatch, send);
  expect(send.mock.calls[0][0].creationKey).toBe(send.mock.calls[1][0].creationKey);
});

it("keeps different project, dataset and composer scopes separate", async () => {
  const receipts: string[] = [];
  for (const [project, dataset, scope] of [["project", undefined, "first"], ["other", undefined, "first"], ["project", "dataset", "first"], ["project", undefined, "second"]]) {
    await recoverResearchSessionCreation(project!, "Same", dataset, scope!, async body => {
      receipts.push(body.creationKey);
      return { ...accepted(body.creationKey), project_id: project! };
    });
  }
  expect(new Set(receipts).size).toBe(4);
});

it("does not resurrect an old readable key after storage writes fail", async () => {
  const send = vi.fn(async body => accepted(body.creationKey));
  const first = await recoverResearchSessionCreation("project", "Draft", undefined, "storage", send);
  vi.spyOn(Storage.prototype, "removeItem").mockImplementation(() => { throw new Error("Denied"); });
  vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => { throw new Error("Full"); });
  acknowledgeResearchSessionCreation(first.creationKey);
  const next = await recoverResearchSessionCreation("project", "Draft", undefined, "storage", send);
  const retry = await recoverResearchSessionCreation("project", "Draft", undefined, "storage", send);
  expect(next.creationKey).not.toBe(first.creationKey);
  expect(retry.creationKey).toBe(next.creationKey);
});
