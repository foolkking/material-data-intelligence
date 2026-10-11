import { afterEach, expect, it, vi } from "vitest";

import {
  deleteEmptyProject,
  getProjectHistory,
  invalidateProjectHistory,
  invalidateProductDirectories,
  listProjects,
  searchProduct,
  updateDataset,
  updateProject,
  createProject,
  getProjectExportManifest,
  uploadDatasetFiles,
} from "./planner-api";

afterEach(() => {
  invalidateProjectHistory();
  invalidateProductDirectories();
  vi.unstubAllGlobals();
});

it("forwards cancellation to project updates and provenance exports", async () => {
  const fetchMock = vi.fn().mockImplementation(async () => new Response(JSON.stringify({ id: "p", projectId: "p", name: "Materials" }), { status: 200 }));
  vi.stubGlobal("fetch", fetchMock);
  const signal = new AbortController().signal;
  await updateProject("p", { name: "Materials" }, signal);
  await getProjectExportManifest("p", signal);
  expect(fetchMock.mock.calls.every((call) => call[1].signal === signal)).toBe(true);
  expect(fetchMock.mock.calls[0][1].body).toBe(JSON.stringify({ name: "Materials" }));
});

it("forwards cancellation to project creation without adding unsupported admission fields", async () => {
  const fetchMock = vi.fn().mockImplementation(async () => new Response(JSON.stringify({ id: "p", projectId: "p", name: "Materials" }), { status: 200 }));
  vi.stubGlobal("fetch", fetchMock);
  const signal = new AbortController().signal;
  await createProject("Materials", signal);
  expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/projects"), expect.objectContaining({ method: "POST", signal, body: JSON.stringify({ name: "Materials" }) }));
});

it("keeps owned project directory reads separate from the shell cache", async () => {
  const fetchMock = vi.fn().mockImplementation(async () => new Response(JSON.stringify([{ id: "p", name: "Materials" }]), { status: 200 }));
  vi.stubGlobal("fetch", fetchMock);
  const cached = await listProjects();
  const controller = new AbortController();
  await listProjects({ signal: controller.signal });
  controller.abort();
  expect(await listProjects()).toBe(cached);
  expect(fetchMock).toHaveBeenCalledTimes(2);
  expect(fetchMock).toHaveBeenLastCalledWith(expect.stringContaining("/projects"), expect.objectContaining({ signal: controller.signal, cache: "no-store" }));
});

it("keeps owned cancellable history reads separate from the shared warm cache", async () => {
  const fetchMock = vi.fn().mockImplementation(async () => new Response(JSON.stringify({ project: { projectId: "project-owned" }, datasets: [], analyses: [] }), { status: 200 }));
  vi.stubGlobal("fetch", fetchMock);
  const cached = await getProjectHistory("project-owned");
  const controller = new AbortController();
  await getProjectHistory("project-owned", { signal: controller.signal });
  controller.abort();
  expect(await getProjectHistory("project-owned")).toBe(cached);
  expect(fetchMock).toHaveBeenCalledTimes(2);
  expect(fetchMock).toHaveBeenLastCalledWith(expect.stringContaining("/projects/project-owned/history"), expect.objectContaining({ signal: controller.signal, cache: "no-store" }));
});

it("serializes bounded global-search scope and date filters", async () => {
  const fetchMock = vi.fn(async (_input: string | URL | Request) => new Response(JSON.stringify({
    query: "silicon",
    count: 0,
    items: [],
    truncated: false,
    nextCursor: null,
  }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  }));
  vi.stubGlobal("fetch", fetchMock);

  await searchProduct(" silicon ", {
    projectId: "project-1",
    kind: "result",
    status: "archived",
    dateFrom: "2026-08-01",
    dateTo: "2026-08-31",
    limit: 25,
    cursor: "cursor-1",
  });

  const requestUrl = new URL(
    String(fetchMock.mock.calls[0]?.[0]),
    "http://localhost",
  );
  expect(requestUrl.pathname).toBe("/api/search");
  expect(Object.fromEntries(requestUrl.searchParams)).toEqual({
    q: "silicon",
    project_id: "project-1",
    kind: "result",
    status: "archived",
    limit: "25",
    cursor: "cursor-1",
    date_from: "2026-08-01",
    date_to: "2026-08-31",
  });
});

it("propagates cancellation to obsolete global-search requests", async () => {
  const controller = new AbortController();
  const fetchMock = vi.fn(
    async (_input: string | URL | Request, init?: RequestInit) => {
      expect(init?.signal).toBe(controller.signal);
      return new Response(
        JSON.stringify({ query: "silicon", count: 0, items: [] }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      );
    },
  );
  vi.stubGlobal("fetch", fetchMock);

  await searchProduct("silicon", { signal: controller.signal });

  expect(fetchMock).toHaveBeenCalledTimes(1);
});

it("keeps the authenticated browser session on upload-session file PUT requests", async () => {
  let declarationId = "";
  const fetchMock = vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.includes("/upload-sessions") && init?.method === "POST" && !url.includes("/complete")) {
      const body = JSON.parse(String(init.body)) as { files: Array<{ clientFileId: string }> };
      declarationId = body.files[0].clientFileId;
      return new Response(JSON.stringify({ uploadSessionId: "session-1", files: [{ clientFileId: declarationId, fileId: "file-1" }] }), { status: 200 });
    }
    if (url.includes("/files/file-1") && init?.method === "PUT") {
      const bytes = await (init.body as File).arrayBuffer();
      const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)), (item) => item.toString(16).padStart(2, "0")).join("");
      return new Response(JSON.stringify({ byteSize: bytes.byteLength, sha256: hash }), { status: 200 });
    }
    if (url.includes("/complete") && init?.method === "POST") {
      return new Response(JSON.stringify({ id: "dataset-1", datasetId: "dataset-1", projectId: "project-1", name: "test", status: "profile_ready" }), { status: 200 });
    }
    throw new Error(`Unexpected fetch: ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);

  const payload = new TextEncoder().encode("formula,band_gap\nBaTiO3,2.1");
  const file = {
    name: "materials.csv",
    size: payload.byteLength,
    type: "text/csv",
    arrayBuffer: async () => payload.buffer,
    slice: (start: number, end?: number) => new Blob([payload.slice(start, end)]),
  } as File;
  await uploadDatasetFiles("project-1", "test", [{ file }]);

  const putCall = fetchMock.mock.calls.find((call) => String(call[0]).includes("/files/file-1"));
  expect(putCall?.[1]).toEqual(expect.objectContaining({ method: "PUT", credentials: "include" }));
});

it("surfaces the server's safe object-lifecycle explanation", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({
    detail: {
      message: "项目包含数据或研究记录，不能物理删除。请改为归档。",
      blockers: { datasets: 1 },
    },
  }), { status: 409 })));

  await expect(deleteEmptyProject("project-1")).rejects.toThrow("项目包含数据或研究记录，不能物理删除。请改为归档。");
});

it("deduplicates a warm project history request and invalidates it after data mutation", async () => {
  let historyRequestCount = 0;
  const fetchMock = vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/projects/project-1/history")) {
      historyRequestCount += 1;
      return new Response(JSON.stringify({
        project: { id: "project-1", name: `Project ${historyRequestCount}` },
        datasets: [],
        analyses: [],
      }), { status: 200 });
    }
    if (url.endsWith("/datasets/dataset-1") && init?.method === "PATCH") {
      return new Response(JSON.stringify({
        id: "dataset-1",
        datasetId: "dataset-1",
        projectId: "project-1",
        name: "Updated dataset",
        status: "profile_ready",
      }), { status: 200 });
    }
    throw new Error(`Unexpected fetch: ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);

  await Promise.all([
    getProjectHistory("project-1"),
    getProjectHistory("project-1"),
  ]);
  expect(historyRequestCount).toBe(1);

  await updateDataset("dataset-1", { name: "Updated dataset" });
  await getProjectHistory("project-1");

  expect(historyRequestCount).toBe(2);
});
