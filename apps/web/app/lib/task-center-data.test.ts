import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  listProjects: vi.fn(),
  listWorkspaceAnalysisJobs: vi.fn(),
}));

vi.mock("./planner-api", () => ({ listProjects: mocks.listProjects }));
vi.mock("./workspace-api", () => ({
  listWorkspaceAnalysisJobs: mocks.listWorkspaceAnalysisJobs,
}));

import {
  getProductTaskFeed,
  invalidateProductTaskFeed,
} from "./task-center-data";

beforeEach(() => {
  invalidateProductTaskFeed();
  mocks.listProjects.mockReset();
  mocks.listWorkspaceAnalysisJobs.mockReset();
});

describe("product task feed", () => {
  it("shares one authorized cross-project request between task surfaces", async () => {
    mocks.listProjects.mockResolvedValue([
      { id: "project-a", projectId: "project-a", name: "Project A" },
    ]);
    mocks.listWorkspaceAnalysisJobs.mockResolvedValue({
      data: {
        items: [
          {
            jobId: "job-1",
            projectId: "project-a",
            jobStatus: "completed",
            createdAt: "2026-08-30T00:00:00Z",
            updatedAt: "2026-08-30T01:00:00Z",
          },
        ],
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
    expect(mocks.listProjects).toHaveBeenCalledTimes(1);
    expect(mocks.listWorkspaceAnalysisJobs).toHaveBeenCalledTimes(1);
  });

  it("retains authorized rows when one project is temporarily unavailable", async () => {
    mocks.listProjects.mockResolvedValue([
      { id: "project-a", projectId: "project-a", name: "Project A" },
      { id: "project-b", projectId: "project-b", name: "Project B" },
    ]);
    mocks.listWorkspaceAnalysisJobs.mockImplementation(
      async (projectId: string) => {
        if (projectId === "project-b") throw new Error("unavailable");
        return {
          data: {
            items: [
              {
                jobId: "job-a",
                projectId,
                jobStatus: "completed",
                createdAt: "2026-08-30T00:00:00Z",
                updatedAt: "2026-08-30T01:00:00Z",
              },
            ],
          },
        };
      },
    );

    const feed = await getProductTaskFeed({ forceRefresh: true });

    expect(feed.rows).toHaveLength(1);
    expect(feed.unavailableProjectCount).toBe(1);
    expect(feed.truncated).toBe(false);
  });

  it("propagates an authoritative next cursor as a bounded-feed signal", async () => {
    mocks.listProjects.mockResolvedValue([
      { id: "project-a", projectId: "project-a", name: "Project A" },
    ]);
    mocks.listWorkspaceAnalysisJobs.mockResolvedValue({
      data: {
        items: [],
        nextCursor: "cursor-next",
      },
    });

    const feed = await getProductTaskFeed({ forceRefresh: true });

    expect(feed.rows).toHaveLength(0);
    expect(feed.truncated).toBe(true);
  });
});
