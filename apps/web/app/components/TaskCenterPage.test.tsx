import React from "react";
import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";

const mocks = vi.hoisted(() => ({
  getProductTaskFeed: vi.fn(),
  invalidateProductTaskFeed: vi.fn(),
  cancelAgent2Execution: vi.fn(),
}));

vi.mock("../lib/task-center-data", () => ({
  getProductTaskFeed: mocks.getProductTaskFeed,
  invalidateProductTaskFeed: mocks.invalidateProductTaskFeed,
}));
vi.mock("../lib/agent2-execution-api", () => ({ cancelAgent2Execution: mocks.cancelAgent2Execution }));
vi.mock("./ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

import { TaskCenterPage } from "./TaskCenterPage";

describe("TaskCenterPage", () => {
  it("aggregates authorized project jobs and preserves exact workspace navigation", async () => {
    mocks.getProductTaskFeed.mockResolvedValue({
      projects: [
        { id: "project-a", projectId: "project-a", name: "Project A" },
        { id: "project-b", projectId: "project-b", name: "Project B" },
      ],
      rows: [
        ...[{ jobId: "job-running", projectId: "project-a", datasetId: null, researchTurnId: "turn-running", jobStatus: "running", workspaceProjectionStatus: "RUNNING", analysisPlanSchemaVersion: "0.2", dependencyOutcome: null, artifactCount: 1, interpretationCount: 0, workspaceId: "workspace-1", workspaceExists: true, createdAt: "2026-08-28T00:00:00Z", updatedAt: "2026-08-28T01:00:00Z", projectName: "Project A" }],
        ...[
          { jobId: "job-complete", projectId: "project-b", datasetId: null, researchTurnId: "turn-complete", jobStatus: "completed", workspaceProjectionStatus: "COMPLETE", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 2, interpretationCount: 1, workspaceId: null, workspaceExists: false, createdAt: "2026-08-27T00:00:00Z", updatedAt: "2026-08-27T01:00:00Z", projectName: "Project B" },
          { jobId: "job-failed", projectId: "project-b", datasetId: null, researchTurnId: "turn-failed", jobStatus: "failed", workspaceProjectionStatus: "FAILED", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "FAILED", artifactCount: 0, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-08-27T00:00:00Z", updatedAt: "2026-08-27T02:00:00Z", projectName: "Project B" },
          { jobId: "job-canceled", projectId: "project-b", datasetId: null, researchTurnId: "turn-canceled", jobStatus: "canceled", workspaceProjectionStatus: "CANCELED", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "CANCELED", artifactCount: 0, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-08-27T00:00:00Z", updatedAt: "2026-08-27T03:00:00Z", projectName: "Project B" },
          { jobId: "job-legacy", projectId: "project-b", datasetId: null, jobStatus: "created", workspaceProjectionStatus: "LEGACY_READ_ONLY", analysisPlanSchemaVersion: "0.1", dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 1, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-08-26T00:00:00Z", updatedAt: "2026-08-26T01:00:00Z", projectName: "Project B" },
        ],
      ],
      unavailableProjectCount: 0,
      loadedAt: "2026-08-30T01:00:00Z",
    });

    render(<TaskCenterPage />);
    await waitFor(() => expect(screen.getByText("任务中心")).toBeInTheDocument());
    expect(screen.getAllByText("可恢复研究").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/超过 15 分钟没有状态更新/).length).toBeGreaterThan(0);
    expect(screen.getByText("历史研究")).toBeInTheDocument();
    expect(screen.getByText("已取消")).toBeInTheDocument();
    expect(screen.getAllByText("技术身份").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/可恢复研究会话/).length).toBeGreaterThan(0);
    expect(screen.getByText(/历史运行 · 仅查看/)).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "任务概览" })).toHaveTextContent("1");
    expect(screen.getAllByRole("link", { name: "打开" })[0]).toHaveAttribute("href", "/projects/project-a/research?run=job-running&turn=turn-running");
    expect(screen.getAllByRole("link", { name: "打开" }).map((link) => link.getAttribute("href"))).toContain("/projects/project-b/research?run=job-complete&turn=turn-complete");
    expect(screen.getAllByRole("link", { name: "打开" }).map((link) => link.getAttribute("href"))).toContain("/projects/project-b/research?run=job-failed&turn=turn-failed");
    expect(screen.getAllByRole("link", { name: "打开并重试" }).map((link) => link.getAttribute("href"))).toEqual([
      "/projects/project-b/research?run=job-failed&turn=turn-failed",
      "/projects/project-b/research?run=job-canceled&turn=turn-canceled",
    ]);
    expect(screen.getAllByRole("button", { name: "停止研究" })).toHaveLength(1);
    expect(screen.getByRole("tab", { name: /全部/ })).toHaveAttribute("aria-selected", "true");
    mocks.cancelAgent2Execution.mockResolvedValue({ turn_id: "turn-running", status: "CANCELING" });
    fireEvent.click(screen.getAllByRole("button", { name: "停止研究" })[0]);
    expect(await screen.findByRole("dialog", { name: "停止这项研究？" })).toBeInTheDocument();
    expect(screen.getByText(/尚未完成的分支不会被伪装成成功/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "确认停止" }));
    await waitFor(() => expect(mocks.cancelAgent2Execution).toHaveBeenCalledWith("turn-running"));
    await waitFor(() => expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(2));
    mocks.getProductTaskFeed.mockClear();
    fireEvent.click(screen.getByRole("button", { name: "重新加载" }));
    await waitFor(() => expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(1));
    mocks.getProductTaskFeed.mockClear();
    fireEvent(window, new Event("online"));
    await waitFor(() => expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(1));
  });

  it("keeps available tasks usable while disclosing a partial project sync", async () => {
    mocks.getProductTaskFeed.mockResolvedValue({
      projects: [
        { id: "project-a", projectId: "project-a", name: "Project A" },
        { id: "project-b", projectId: "project-b", name: "Project B" },
      ],
      rows: [
        { jobId: "job-a", projectId: "project-a", datasetId: null, researchTurnId: "turn-a", jobStatus: "completed", workspaceProjectionStatus: "COMPLETE", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 1, interpretationCount: 1, workspaceId: null, workspaceExists: false, createdAt: "2026-08-30T00:00:00Z", updatedAt: "2026-08-30T01:00:00Z", projectName: "Project A" },
      ],
      unavailableProjectCount: 1,
      loadedAt: "2026-08-30T01:00:00Z",
    });

    render(<TaskCenterPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("1 个项目暂未同步");
    expect(screen.getByRole("link", { name: "打开" })).toHaveAttribute(
      "href",
      "/projects/project-a/research?run=job-a&turn=turn-a",
    );
    expect(screen.queryByRole("button", { name: "停止研究" })).toBeNull();
  });

  it("keeps the current task list visible while a background refresh is in flight", async () => {
    mocks.getProductTaskFeed.mockReset();
    const feed = {
      projects: [{ id: "project-a", projectId: "project-a", name: "Project A" }],
      rows: [
        { jobId: "job-complete", projectId: "project-a", datasetId: null, researchTurnId: "turn-complete", jobStatus: "completed", workspaceProjectionStatus: "COMPLETE", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 1, interpretationCount: 1, workspaceId: null, workspaceExists: false, createdAt: "2026-08-30T00:00:00Z", updatedAt: "2026-08-30T01:00:00Z", projectName: "Project A" },
      ],
      unavailableProjectCount: 0,
      loadedAt: "2026-08-30T01:00:00Z",
    };
    let resolveRefresh: ((value: typeof feed) => void) | undefined;
    mocks.getProductTaskFeed
      .mockResolvedValueOnce(feed)
      .mockImplementationOnce(() => new Promise((resolve) => { resolveRefresh = resolve; }));

    render(<TaskCenterPage />);
    expect(await screen.findByText("可恢复研究")).toBeInTheDocument();
    window.dispatchEvent(new Event("online"));
    expect(await screen.findByText("正在同步最新状态…")).toBeInTheDocument();
    expect(screen.queryByText("正在加载后台任务…")).toBeNull();
    expect(screen.getByText("可恢复研究")).toBeInTheDocument();
    resolveRefresh?.(feed);
    await waitFor(() => expect(screen.getByText(/最近同步/)).toBeInTheDocument());
  });

  it("keeps stale task data visible and discloses a refresh failure", async () => {
    mocks.getProductTaskFeed.mockReset();
    const feed = {
      projects: [{ id: "project-a", projectId: "project-a", name: "Project A" }],
      rows: [
        { jobId: "job-complete", projectId: "project-a", datasetId: null, researchTurnId: "turn-complete", jobStatus: "completed", workspaceProjectionStatus: "COMPLETE", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 1, interpretationCount: 1, workspaceId: null, workspaceExists: false, createdAt: "2026-08-30T00:00:00Z", updatedAt: "2026-08-30T01:00:00Z", projectName: "Project A" },
      ],
      unavailableProjectCount: 0,
      loadedAt: "2026-08-30T01:00:00Z",
    };
    mocks.getProductTaskFeed.mockResolvedValueOnce(feed).mockRejectedValueOnce(new Error("offline"));
    render(<TaskCenterPage />);
    expect(await screen.findByText("可恢复研究")).toBeInTheDocument();
    window.dispatchEvent(new Event("online"));
    expect(await screen.findByText(/同步失败，当前显示上次结果/)).toBeInTheDocument();
    expect(screen.getByText("可恢复研究")).toBeInTheDocument();
  });

  it("discloses the bounded recent-task window instead of implying the feed is complete", async () => {
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
    render(<TaskCenterPage />);
    expect(await screen.findByText("当前筛选显示最近 30 项；更早任务仍保留在项目历史中。")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "打开" })).toHaveLength(30);
  });
});
