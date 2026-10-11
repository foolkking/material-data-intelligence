import { afterEach, expect, it, vi } from "vitest";
import { bulkProjectAction, bulkDatasetAction, deleteEmptyProject, deleteEmptyDataset } from "./planner-api";
import { bulkUpdateResearchSessions } from "./product-api";
import { bulkUpdateScientificObjects } from "./scientific-viewer-api";
import { bulkUpdateScientificReportLifecycle } from "./scientific-report-api";

afterEach(() => vi.unstubAllGlobals());

it.each([
  ["project", (signal: AbortSignal) => bulkProjectAction(["p"], "restore", signal), "/projects/bulk", "POST", { projectIds: ["p"], action: "restore" }],
  ["dataset", (signal: AbortSignal) => bulkDatasetAction(["d"], "restore", signal), "/datasets/bulk", "POST", { datasetIds: ["d"], action: "restore" }],
  ["research", (signal: AbortSignal) => bulkUpdateResearchSessions("p", ["r"], "RESTORE", signal), "/projects/p/research-sessions/bulk", "POST", { sessionIds: ["r"], action: "RESTORE" }],
  ["object", (signal: AbortSignal) => bulkUpdateScientificObjects("p", ["o"], "ACTIVE", signal), "/api/projects/p/scientific-objects/bulk", "POST", { object_ids: ["o"], lifecycle: "ACTIVE" }],
  ["report", (signal: AbortSignal) => bulkUpdateScientificReportLifecycle("p", ["r"], "ACTIVE", signal), "/api/projects/p/scientific-reports/bulk", "POST", { reportIds: ["r"], lifecycle: "ACTIVE" }],
  ["delete project", (signal: AbortSignal) => deleteEmptyProject("p", signal), "/projects/p", "DELETE", undefined],
  ["delete dataset", (signal: AbortSignal) => deleteEmptyDataset("d", signal), "/datasets/d", "DELETE", undefined],
] as const)("passes the owned abort signal through %s without changing its request", async (_name, run, path, method, body) => {
  const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ project_id: "p" }), { status: 200 }));
  vi.stubGlobal("fetch", fetchMock);
  const controller = new AbortController();
  await run(controller.signal);
  expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining(path), expect.objectContaining({ signal: controller.signal, method, credentials: "include" }));
  expect(fetchMock.mock.calls[0][1].body).toBe(body ? JSON.stringify(body) : undefined);
});
