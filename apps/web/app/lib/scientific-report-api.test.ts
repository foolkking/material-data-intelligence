import { afterEach, expect, it, vi } from "vitest";
import { createScientificReportRevision, getScientificReportDependencyImpact, updateScientificReportLifecycle, updateScientificReportOrganization } from "./scientific-report-api";

afterEach(() => vi.unstubAllGlobals());

it.each([
  ["lifecycle", (signal: AbortSignal) => updateScientificReportLifecycle("report-1", "ARCHIVED", signal), "PATCH", { lifecycle: "ARCHIVED" }],
  ["organization", (signal: AbortSignal) => updateScientificReportOrganization("report-1", { title: "材料报告" }, signal), "PATCH", { title: "材料报告" }],
  ["revisions", (signal: AbortSignal) => createScientificReportRevision("report-1", { title: "新修订" }, signal), "POST", { reason: "USER_REVISION", title: "新修订" }],
  ["dependency-impact", (signal: AbortSignal) => getScientificReportDependencyImpact("report-1", signal), undefined, undefined],
] as const)("passes cancellation through the report %s request without changing its payload", async (path, run, method, body) => {
  const fetchMock = vi.fn().mockResolvedValue(new Response("{}"));
  vi.stubGlobal("fetch", fetchMock);
  const controller = new AbortController();
  await run(controller.signal);
  expect(fetchMock.mock.calls[0][0]).toContain(`/scientific-reports/report-1/${path}`);
  expect(fetchMock.mock.calls[0][1]).toMatchObject({ signal: controller.signal, credentials: "include" });
  expect(fetchMock.mock.calls[0][1].method).toBe(method);
  expect(fetchMock.mock.calls[0][1].body).toBe(body ? JSON.stringify(body) : undefined);
});
