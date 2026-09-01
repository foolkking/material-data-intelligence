import React from "react";
import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";

const mocks = vi.hoisted(() => ({
  getProductTaskFeed: vi.fn(),
}));

vi.mock("../lib/task-center-data", () => ({
  getProductTaskFeed: mocks.getProductTaskFeed,
}));
vi.mock("./ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

import { NotificationCenterPage } from "./NotificationCenterPage";

describe("NotificationCenterPage", () => {
  it("projects persisted terminal task states without creating new work", async () => {
    mocks.getProductTaskFeed.mockResolvedValue({
      projects: [{ id: "project-a", projectId: "project-a", name: "Project A" }],
      rows: [
        { jobId: "job-failed", projectId: "project-a", datasetId: null, researchTurnId: "turn-failed", jobStatus: "failed", workspaceProjectionStatus: "FAILED", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "FAILED", artifactCount: 1, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-08-28T00:00:00Z", updatedAt: "2026-08-28T01:00:00Z", projectName: "Project A" },
        { jobId: "job-completed", projectId: "project-a", datasetId: null, researchTurnId: "turn-completed", jobStatus: "completed", workspaceProjectionStatus: "COMPLETE", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 2, interpretationCount: 1, workspaceId: null, workspaceExists: false, createdAt: "2026-08-28T00:00:00Z", updatedAt: "2026-08-28T02:00:00Z", projectName: "Project A" },
        { jobId: "job-cancelled", projectId: "project-a", datasetId: null, researchTurnId: "turn-cancelled", jobStatus: "cancelled", workspaceProjectionStatus: "CANCELLED", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "CANCELLED", artifactCount: 0, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-08-28T00:00:00Z", updatedAt: "2026-08-28T03:00:00Z", projectName: "Project A" },
        { jobId: "job-running", projectId: "project-a", datasetId: null, researchTurnId: "turn-running", jobStatus: "running", workspaceProjectionStatus: "RUNNING", analysisPlanSchemaVersion: "0.2", dependencyOutcome: null, artifactCount: 0, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-08-28T00:00:00Z", updatedAt: "2026-08-28T00:00:00Z", projectName: "Project A" },
      ],
      unavailableProjectCount: 0,
      loadedAt: "2026-08-30T01:00:00Z",
    });

    render(<NotificationCenterPage />);
    await waitFor(() => expect(screen.getByText("通知中心")).toBeInTheDocument());
    expect(screen.getByText("研究失败")).toBeInTheDocument();
    expect(screen.getAllByText("研究会话更新")).toHaveLength(3);
    expect(screen.getAllByText(/可恢复研究会话/)).toHaveLength(3);
    expect(screen.queryByText("研究状态更新")).not.toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "打开研究" }).map((link) => link.getAttribute("href"))).toContain("/projects/project-a/research?run=job-failed&turn=turn-failed");
    expect(screen.getAllByRole("link", { name: "打开并重试" }).map((link) => link.getAttribute("href"))).toContain("/projects/project-a/research?run=job-failed&turn=turn-failed");
    expect(screen.getByRole("tab", { name: /需要关注/ })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("tab", { name: /已完成/ }));
    expect(screen.getByText("研究完成")).toBeInTheDocument();
    expect(screen.queryByText("研究失败")).toBeNull();
    fireEvent.click(screen.getByRole("tab", { name: /已取消/ }));
    expect(screen.getByText("研究已取消")).toBeInTheDocument();
    expect(screen.queryByText("研究完成")).toBeNull();
    mocks.getProductTaskFeed.mockClear();
    window.dispatchEvent(new Event("online"));
    await waitFor(() => expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(1));
  });

  it("discloses partial project loading without hiding authorized notifications", async () => {
    mocks.getProductTaskFeed.mockResolvedValue({
      projects: [
        { id: "project-a", projectId: "project-a", name: "Project A" },
        { id: "project-b", projectId: "project-b", name: "Project B" },
      ],
      rows: [
        { jobId: "job-completed", projectId: "project-a", datasetId: null, researchTurnId: "turn-completed", jobStatus: "completed", workspaceProjectionStatus: "COMPLETE", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 2, interpretationCount: 1, workspaceId: null, workspaceExists: false, createdAt: "2026-08-30T00:00:00Z", updatedAt: "2026-08-30T01:00:00Z", projectName: "Project A" },
      ],
      unavailableProjectCount: 1,
      loadedAt: "2026-08-30T01:00:00Z",
    });

    render(<NotificationCenterPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("1 个项目暂未同步");
    expect(screen.getByRole("link", { name: "打开研究" })).toHaveAttribute(
      "href",
      "/projects/project-a/research?run=job-completed&turn=turn-completed",
    );
  });

  it("discloses the bounded recent-notification window", async () => {
    mocks.getProductTaskFeed.mockReset();
    mocks.getProductTaskFeed.mockResolvedValue({
      projects: [{ id: "project-a", projectId: "project-a", name: "Project A" }],
      rows: Array.from({ length: 31 }, (_, index) => ({
        jobId: `job-${index}`,
        projectId: "project-a",
        datasetId: null,
        researchTurnId: `turn-${index}`,
        jobStatus: "completed",
        workspaceProjectionStatus: "COMPLETE",
        analysisPlanSchemaVersion: "0.2",
        dependencyOutcome: "ALL_SUCCEEDED",
        artifactCount: 1,
        interpretationCount: 1,
        workspaceId: null,
        workspaceExists: false,
        createdAt: `2026-08-30T00:${String(index).padStart(2, "0")}:00Z`,
        updatedAt: `2026-08-30T01:${String(index).padStart(2, "0")}:00Z`,
        projectName: "Project A",
      })),
      unavailableProjectCount: 0,
      loadedAt: "2026-08-30T01:00:00Z",
    });
    render(<NotificationCenterPage />);
    expect(await screen.findByText("当前筛选显示最近 30 项；更早通知仍可从对应项目历史打开。")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "打开研究" })).toHaveLength(30);
  });
});
