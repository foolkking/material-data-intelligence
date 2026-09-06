import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  listWorkspaceTaskFeed: vi.fn(),
}));

vi.mock("./workspace-api", () => ({
  listWorkspaceTaskFeed: mocks.listWorkspaceTaskFeed,
}));

import {
  getProductTaskFeed,
  getProductTaskFeedPage,
  invalidateProductTaskFeed,
  productTaskSearchText,
  sortProductTaskRows,
} from "./task-center-data";

beforeEach(() => {
  invalidateProductTaskFeed();
  mocks.listWorkspaceTaskFeed.mockReset();
});

describe("product task feed", () => {
  it("supports bounded search text and stable recent/oldest ordering", () => {
    const rows = [
      { projectName: "Project A", researchQuestion: "Compare CrystalNN and VoronoiNN", jobId: "job-old", jobStatus: "completed", workspaceProjectionStatus: "COMPLETE", createdAt: "2026-08-30T00:00:00Z", updatedAt: "2026-08-30T01:00:00Z" },
      { projectName: "Project B", jobId: "job-new", jobStatus: "failed", workspaceProjectionStatus: "FAILED", createdAt: "2026-08-30T02:00:00Z", updatedAt: "2026-08-30T03:00:00Z" },
    ] as const;

    expect(productTaskSearchText(rows[0])).toContain("project a");
    expect(productTaskSearchText(rows[0])).toContain("crystalnn and voronoinn");
    expect(productTaskSearchText(rows[0])).toContain("job-old completed complete");
    expect(sortProductTaskRows(rows, "recent").map((row) => row.jobId)).toEqual(["job-new", "job-old"]);
    expect(sortProductTaskRows(rows, "oldest").map((row) => row.jobId)).toEqual(["job-old", "job-new"]);
  });

  it("shares one authorized global request between task surfaces", async () => {
    mocks.listWorkspaceTaskFeed.mockResolvedValue({
      data: {
        schemaVersion: "ProductTaskFeed/1.0",
        items: [
          {
            jobId: "job-1",
            projectId: "project-a",
            projectName: "Project A",
            jobStatus: "completed",
            createdAt: "2026-08-30T00:00:00Z",
            updatedAt: "2026-08-30T01:00:00Z",
          },
        ],
        nextCursor: null,
        limit: 100,
        projectCount: 1,
        truncated: false,
      },
    });

    const [first, second] = await Promise.all([
      getProductTaskFeed(),
      getProductTaskFeed(),
    ]);

    expect(first).toEqual(second);
    expect(first.rows[0]).toMatchObject({
      jobId: "job-1",
      projectName: "Project A",
    });
    expect(first.truncated).toBe(false);
    expect(mocks.listWorkspaceTaskFeed).toHaveBeenCalledTimes(1);
  });

  it("propagates service failure instead of presenting partial authorization state", async () => {
    mocks.listWorkspaceTaskFeed.mockRejectedValueOnce(new Error("unavailable"));
    await expect(
      getProductTaskFeed({ forceRefresh: true }),
    ).rejects.toThrow("unavailable");
  });

  it("propagates an authoritative next cursor as a bounded-feed signal", async () => {
    mocks.listWorkspaceTaskFeed.mockResolvedValue({
      data: {
        schemaVersion: "ProductTaskFeed/1.0",
        items: [],
        nextCursor: "cursor-next",
        limit: 100,
        projectCount: 1,
        truncated: true,
      },
    });

    const feed = await getProductTaskFeed({ forceRefresh: true });

    expect(feed.rows).toHaveLength(0);
    expect(feed.truncated).toBe(true);
  });

  it("walks a 1000-job feed through authoritative cursors without dropping exact job metadata", async () => {
    const pageSize = 100;
    mocks.listWorkspaceTaskFeed.mockImplementation(
      async (options: { cursor?: string }) => {
        const pageIndex = options.cursor ? Number(options.cursor.replace("page-", "")) : 0;
        const start = pageIndex * pageSize;
        const items = Array.from({ length: pageSize }, (_, offset) => ({
          jobId: `job-${start + offset}`,
          projectId: `project-${(start + offset) % 3}`,
          projectName: `Project ${(start + offset) % 3}`,
          jobStatus: "completed",
          workspaceProjectionStatus: "COMPLETE",
          createdAt: `2026-08-30T00:${String(start + offset).padStart(2, "0")}:00Z`,
          updatedAt: `2026-08-30T00:${String(start + offset).padStart(2, "0")}:00Z`,
        }));
        return {
          data: {
            schemaVersion: "ProductTaskFeed/1.0" as const,
            items,
            nextCursor: pageIndex < 9 ? `page-${pageIndex + 1}` : null,
            limit: pageSize,
            projectCount: 3,
            truncated: pageIndex < 9,
          },
        };
      },
    );

    const collected: string[] = [];
    let cursor: string | undefined;
    do {
      const page = await getProductTaskFeedPage(cursor ? { cursor } : {});
      collected.push(...page.rows.map((row) => row.jobId));
      cursor = page.nextCursor ?? undefined;
    } while (cursor);

    expect(collected).toHaveLength(1000);
    expect(new Set(collected).size).toBe(1000);
    expect(collected[0]).toBe("job-0");
    expect(collected.at(-1)).toBe("job-999");
    expect(mocks.listWorkspaceTaskFeed).toHaveBeenCalledTimes(10);
    expect(mocks.listWorkspaceTaskFeed.mock.calls.map(([options]) => options.cursor)).toEqual([
      undefined,
      "page-1",
      "page-2",
      "page-3",
      "page-4",
      "page-5",
      "page-6",
      "page-7",
      "page-8",
      "page-9",
    ]);
  });

  it("coalesces an explicit refresh with an authorized request already in flight", async () => {
    let resolveFeed:
      | ((value: {
          data: {
            schemaVersion: string;
            items: never[];
            nextCursor: null;
            limit: number;
            projectCount: number;
            truncated: boolean;
          };
        }) => void)
      | undefined;
    mocks.listWorkspaceTaskFeed.mockImplementationOnce(
      () => new Promise((resolve) => { resolveFeed = resolve; }),
    );

    const automatic = getProductTaskFeed();
    const explicit = getProductTaskFeed({ forceRefresh: true });

    expect(explicit).toBe(automatic);
    expect(mocks.listWorkspaceTaskFeed).toHaveBeenCalledTimes(1);
    resolveFeed?.({
      data: {
        schemaVersion: "ProductTaskFeed/1.0",
        items: [],
        nextCursor: null,
        limit: 100,
        projectCount: 0,
        truncated: false,
      },
    });
    await expect(automatic).resolves.toMatchObject({ rows: [] });
  });

  it("aborts the shared transport after its only consumer leaves", async () => {
    let transportSignal: AbortSignal | undefined;
    mocks.listWorkspaceTaskFeed.mockImplementationOnce(
      (options: { signal?: AbortSignal }) =>
        new Promise((_resolve, reject) => {
          transportSignal = options.signal;
          options.signal?.addEventListener(
            "abort",
            () =>
              reject(
                new DOMException("Task feed request was aborted.", "AbortError"),
              ),
            { once: true },
          );
        }),
    );
    const controller = new AbortController();
    const request = getProductTaskFeed({ signal: controller.signal });

    expect(transportSignal?.aborted).toBe(false);
    controller.abort();

    await expect(request).rejects.toMatchObject({ name: "AbortError" });
    expect(transportSignal?.aborted).toBe(true);
  });

  it("does not abort a coalesced transport while another consumer remains", async () => {
    let transportSignal: AbortSignal | undefined;
    let resolveFeed:
      | ((value: {
          data: {
            schemaVersion: string;
            items: never[];
            nextCursor: null;
            limit: number;
            projectCount: number;
            truncated: boolean;
          };
        }) => void)
      | undefined;
    mocks.listWorkspaceTaskFeed.mockImplementationOnce(
      (options: { signal?: AbortSignal }) =>
        new Promise((resolve) => {
          transportSignal = options.signal;
          resolveFeed = resolve;
        }),
    );
    const firstController = new AbortController();
    const secondController = new AbortController();
    const first = getProductTaskFeed({ signal: firstController.signal });
    const second = getProductTaskFeed({ signal: secondController.signal });

    firstController.abort();
    await expect(first).rejects.toMatchObject({ name: "AbortError" });
    expect(transportSignal?.aborted).toBe(false);

    resolveFeed?.({
      data: {
        schemaVersion: "ProductTaskFeed/1.0",
        items: [],
        nextCursor: null,
        limit: 100,
        projectCount: 0,
        truncated: false,
      },
    });
    await expect(second).resolves.toMatchObject({ rows: [] });
  });

  it("uses warm data for automatic refreshes but lets a user refresh bypass it", async () => {
    mocks.listWorkspaceTaskFeed.mockResolvedValue({
      data: {
        schemaVersion: "ProductTaskFeed/1.0",
        items: [],
        nextCursor: null,
        limit: 100,
        projectCount: 0,
        truncated: false,
      },
    });

    await getProductTaskFeed();
    await getProductTaskFeed();
    expect(mocks.listWorkspaceTaskFeed).toHaveBeenCalledTimes(1);

    await getProductTaskFeed({ forceRefresh: true });
    expect(mocks.listWorkspaceTaskFeed).toHaveBeenCalledTimes(2);
  });
});
