import React from "react";
import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";

const mocks = vi.hoisted(() => ({
  listProjects: vi.fn(),
  listWorkspaceAnalysisJobs: vi.fn(),
  cancelAgent2Execution: vi.fn(),
}));

vi.mock("../lib/planner-api", () => ({ listProjects: mocks.listProjects }));
vi.mock("../lib/workspace-api", () => ({ listWorkspaceAnalysisJobs: mocks.listWorkspaceAnalysisJobs }));
vi.mock("../lib/agent2-execution-api", () => ({ cancelAgent2Execution: mocks.cancelAgent2Execution }));
vi.mock("./ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

import { TaskCenterPage } from "./TaskCenterPage";

describe("TaskCenterPage", () => {
  it("aggregates authorized project jobs and preserves exact workspace navigation", async () => {
    mocks.listProjects.mockResolvedValue([
      { id: "project-a", projectId: "project-a", name: "Project A" },
      { id: "project-b", projectId: "project-b", name: "Project B" },
    ]);
    mocks.listWorkspaceAnalysisJobs.mockImplementation(async (projectId: string) => ({
      data: {
        items: projectId === "project-a"
          ? [{ jobId: "job-running", projectId, datasetId: null, researchTurnId: "turn-running", jobStatus: "running", workspaceProjectionStatus: "RUNNING", analysisPlanSchemaVersion: "0.2", dependencyOutcome: null, artifactCount: 1, interpretationCount: 0, workspaceId: "workspace-1", workspaceExists: true, createdAt: "2026-08-28T00:00:00Z", updatedAt: "2026-08-28T01:00:00Z" }]
          : [{ jobId: "job-complete", projectId, datasetId: null, jobStatus: "completed", workspaceProjectionStatus: "COMPLETE", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 2, interpretationCount: 1, workspaceId: null, workspaceExists: false, createdAt: "2026-08-27T00:00:00Z", updatedAt: "2026-08-27T01:00:00Z" }, { jobId: "job-failed", projectId, datasetId: null, researchTurnId: "turn-failed", jobStatus: "failed", workspaceProjectionStatus: "FAILED", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "FAILED", artifactCount: 0, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-08-27T00:00:00Z", updatedAt: "2026-08-27T02:00:00Z" }],
      },
      status: 200,
      etag: null,
      idempotentReplay: null,
    }));

    render(<TaskCenterPage />);
    await waitFor(() => expect(screen.getByText("任务中心")).toBeInTheDocument());
    expect(screen.getByText("运行中 · job-running")).toBeInTheDocument();
    expect(screen.getByText("已完成 · job-complete")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "打开" })[0]).toHaveAttribute("href", "/workspaces/workspace-1");
    expect(screen.getAllByRole("link", { name: "打开" }).map((link) => link.getAttribute("href"))).toContain("/projects/project-b/research?run=job-complete");
    expect(screen.getAllByRole("link", { name: "打开" }).map((link) => link.getAttribute("href"))).toContain("/projects/project-b/research?run=job-failed");
    expect(screen.getAllByRole("link", { name: "打开并重试" }).map((link) => link.getAttribute("href"))).toEqual([
      "/projects/project-b/research?run=job-failed&turn=turn-failed",
      "/projects/project-b/research?run=job-failed&turn=turn-failed",
    ]);
    mocks.cancelAgent2Execution.mockResolvedValue({ turn_id: "turn-running", status: "CANCELING" });
    fireEvent.click(screen.getByRole("button", { name: "停止研究" }));
    await waitFor(() => expect(mocks.cancelAgent2Execution).toHaveBeenCalledWith("turn-running"));
    await waitFor(() => expect(mocks.listProjects).toHaveBeenCalledTimes(2));
    mocks.listProjects.mockClear();
    fireEvent.click(screen.getByRole("button", { name: "重新加载" }));
    await waitFor(() => expect(mocks.listProjects).toHaveBeenCalledTimes(1));
    mocks.listProjects.mockClear();
    fireEvent(window, new Event("online"));
    await waitFor(() => expect(mocks.listProjects).toHaveBeenCalledTimes(1));
  });
});
