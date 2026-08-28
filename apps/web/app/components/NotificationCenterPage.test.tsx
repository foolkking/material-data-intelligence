import React from "react";
import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

const mocks = vi.hoisted(() => ({
  listProjects: vi.fn(),
  listWorkspaceAnalysisJobs: vi.fn(),
}));

vi.mock("../lib/planner-api", () => ({ listProjects: mocks.listProjects }));
vi.mock("../lib/workspace-api", () => ({ listWorkspaceAnalysisJobs: mocks.listWorkspaceAnalysisJobs }));
vi.mock("./ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

import { NotificationCenterPage } from "./NotificationCenterPage";

describe("NotificationCenterPage", () => {
  it("projects persisted terminal task states without creating new work", async () => {
    mocks.listProjects.mockResolvedValue([{ id: "project-a", projectId: "project-a", name: "Project A" }]);
    mocks.listWorkspaceAnalysisJobs.mockResolvedValue({
      data: {
        items: [
          { jobId: "job-failed", projectId: "project-a", datasetId: null, researchTurnId: "turn-failed", jobStatus: "failed", workspaceProjectionStatus: "FAILED", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "FAILED", artifactCount: 1, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-08-28T00:00:00Z", updatedAt: "2026-08-28T01:00:00Z" },
          { jobId: "job-running", projectId: "project-a", datasetId: null, researchTurnId: "turn-running", jobStatus: "running", workspaceProjectionStatus: "RUNNING", analysisPlanSchemaVersion: "0.2", dependencyOutcome: null, artifactCount: 0, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-08-28T00:00:00Z", updatedAt: "2026-08-28T00:00:00Z" },
        ],
      },
      status: 200,
      etag: null,
      idempotentReplay: null,
    });

    render(<NotificationCenterPage />);
    await waitFor(() => expect(screen.getByText("通知中心")).toBeInTheDocument());
    expect(screen.getByText("研究失败")).toBeInTheDocument();
    expect(screen.queryByText("研究状态更新")).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "打开研究" })).toHaveAttribute("href", "/projects/project-a/research?run=job-failed");
    expect(screen.getByText("1 个", { exact: false })).toBeInTheDocument();
  });
});
