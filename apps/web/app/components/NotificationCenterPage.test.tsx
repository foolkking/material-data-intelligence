import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const mocks = vi.hoisted(() => ({
  getProductTaskFeed: vi.fn(),
  listNotificationReadStates: vi.fn(),
  updateNotificationReadState: vi.fn(),
}));

vi.mock("../lib/task-center-data", () => ({
  getProductTaskFeed: mocks.getProductTaskFeed,
  productTaskSearchText: (task: { projectName?: string; researchQuestion?: string | null; jobId?: string; jobStatus?: string | null; workspaceProjectionStatus?: string }) =>
    [task.projectName, task.researchQuestion, task.jobId, task.jobStatus, task.workspaceProjectionStatus].filter(Boolean).join(" ").toLocaleLowerCase("zh-CN"),
  sortProductTaskRows: (rows: Array<{ updatedAt?: string; createdAt?: string }>, order = "recent") =>
    [...rows].sort((left, right) => {
      const leftTime = Date.parse(String(left.updatedAt || left.createdAt || "")) || 0;
      const rightTime = Date.parse(String(right.updatedAt || right.createdAt || "")) || 0;
      return order === "oldest" ? leftTime - rightTime : rightTime - leftTime;
    }),
}));
vi.mock("../../shared/layout/ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));
vi.mock("../lib/product-api", () => ({
  listNotificationReadStates: mocks.listNotificationReadStates,
  updateNotificationReadState: mocks.updateNotificationReadState,
}));

import { NotificationCenterPage } from "./NotificationCenterPage";

describe("NotificationCenterPage", () => {
  beforeEach(() => {
    mocks.getProductTaskFeed.mockReset();
    mocks.listNotificationReadStates.mockReset();
    mocks.listNotificationReadStates.mockResolvedValue({
      schemaVersion: "NotificationReadState/1.0",
      items: [],
      count: 0,
    });
    mocks.updateNotificationReadState.mockReset();
    mocks.updateNotificationReadState.mockImplementation(
      async (projectId: string, jobId: string, read: boolean) => ({
        projectId,
        jobId,
        read,
        readAt: read ? "2026-09-05T08:00:00Z" : null,
        notificationUpdatedAt: "2026-09-05T07:00:00Z",
      }),
    );
  });

  it("restores server-owned read state and persists read/unread transitions", async () => {
    mocks.getProductTaskFeed.mockResolvedValue({
      projectCount: 1,
      rows: [
        { jobId: "job-read", projectId: "project-a", datasetId: null, researchTurnId: "turn-read", jobStatus: "completed", workspaceProjectionStatus: "COMPLETE", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 1, interpretationCount: 1, workspaceId: null, workspaceExists: false, createdAt: "2026-09-05T06:00:00Z", updatedAt: "2026-09-05T07:00:00Z", projectName: "Project A" },
        { jobId: "job-unread", projectId: "project-a", datasetId: null, researchTurnId: "turn-unread", jobStatus: "failed", workspaceProjectionStatus: "FAILED", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "FAILED", artifactCount: 0, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-09-05T06:00:00Z", updatedAt: "2026-09-05T07:30:00Z", projectName: "Project A" },
      ],
      unavailableProjectCount: 0,
      truncated: false,
      nextCursor: null,
      loadedAt: "2026-09-05T07:31:00Z",
    });
    mocks.listNotificationReadStates.mockResolvedValue({
      schemaVersion: "NotificationReadState/1.0",
      items: [{
        projectId: "project-a",
        jobId: "job-read",
        read: true,
        readAt: "2026-09-05T07:10:00Z",
        notificationUpdatedAt: "2026-09-05T07:00:00Z",
      }],
      count: 1,
    });

    const user = userEvent.setup();
    render(<NotificationCenterPage />);

    await screen.findByText("研究失败");
    expect(await screen.findByRole("tab", { name: /未读 1/ })).toBeInTheDocument();
    const originallyReadRow = screen.getByText("Project A · 已读").closest("article");
    expect(originallyReadRow).not.toBeNull();
    expect(screen.getByText("Project A · 未读")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "标为已读" }));
    await waitFor(() =>
      expect(mocks.updateNotificationReadState).toHaveBeenCalledWith(
        "project-a",
        "job-unread",
        true,
      ),
    );
    expect(screen.getByRole("tab", { name: /未读 0/ })).toBeInTheDocument();

    await user.click(within(originallyReadRow as HTMLElement).getByRole("button", { name: "标为未读" }));
    await waitFor(() =>
      expect(mocks.updateNotificationReadState).toHaveBeenCalledWith(
        "project-a",
        "job-read",
        false,
      ),
    );
    expect(screen.getByRole("tab", { name: /未读 1/ })).toBeInTheDocument();
  });

  it("projects persisted terminal task states without creating new work", async () => {
    mocks.getProductTaskFeed.mockResolvedValue({
      projectCount: 1,
      rows: [
        { jobId: "job-failed", projectId: "project-a", datasetId: null, researchTurnId: "turn-failed", researchQuestion: "分析 XRD 峰位偏差", jobStatus: "failed", workspaceProjectionStatus: "FAILED", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "FAILED", artifactCount: 1, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-08-28T00:00:00Z", updatedAt: "2026-08-28T01:00:00Z", projectName: "Project A" },
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
    expect(screen.getByText("分析 XRD 峰位偏差")).toBeInTheDocument();
    expect(screen.getAllByText("研究会话更新")).toHaveLength(2);
    expect(screen.getAllByText(/更新于/).length).toBeGreaterThan(0);
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
    expect(mocks.getProductTaskFeed).toHaveBeenLastCalledWith(
      expect.objectContaining({
        forceRefresh: false,
        signal: expect.any(AbortSignal),
      }),
    );
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "重新加载" })).toBeEnabled(),
    );
    mocks.getProductTaskFeed.mockClear();
    fireEvent.click(screen.getByRole("button", { name: "重新加载" }));
    await waitFor(() => expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(1));
    expect(mocks.getProductTaskFeed).toHaveBeenLastCalledWith(
      expect.objectContaining({
        forceRefresh: true,
        signal: expect.any(AbortSignal),
      }),
    );
  });

  it("pauses offline polling, aborts the obsolete request and refreshes after reconnect", async () => {
    const online = vi
      .spyOn(navigator, "onLine", "get")
      .mockReturnValue(true);
    const feed = {
      projectCount: 1,
      rows: [
        {
          jobId: "job-completed",
          projectId: "project-a",
          datasetId: null,
          researchTurnId: "turn-completed",
          jobStatus: "completed",
          workspaceProjectionStatus: "COMPLETE",
          analysisPlanSchemaVersion: "0.2",
          dependencyOutcome: "ALL_SUCCEEDED",
          artifactCount: 1,
          interpretationCount: 1,
          workspaceId: null,
          workspaceExists: false,
          createdAt: "2026-09-05T01:00:00Z",
          updatedAt: "2026-09-05T01:01:00Z",
          projectName: "Project A",
        },
      ],
      unavailableProjectCount: 0,
      loadedAt: "2026-09-05T01:01:00Z",
    };
    let refreshSignal: AbortSignal | undefined;
    mocks.getProductTaskFeed
      .mockResolvedValueOnce(feed)
      .mockImplementationOnce(
        (options: { signal?: AbortSignal }) => {
          refreshSignal = options.signal;
          return new Promise(() => undefined);
        },
      )
      .mockResolvedValue(feed);

    render(<NotificationCenterPage />);
    await screen.findByText("研究完成");
    mocks.getProductTaskFeed.mockClear();
    window.dispatchEvent(new Event("online"));
    await waitFor(() => expect(refreshSignal).toBeDefined());
    expect(refreshSignal?.aborted).toBe(false);

    online.mockReturnValue(false);
    window.dispatchEvent(new Event("offline"));
    expect(refreshSignal?.aborted).toBe(true);
    window.dispatchEvent(new Event("online"));
    expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(1);

    online.mockReturnValue(true);
    window.dispatchEvent(new Event("online"));
    await waitFor(() =>
      expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(2),
    );
    online.mockRestore();
  });

  it("discloses partial project loading without hiding authorized notifications", async () => {
    mocks.getProductTaskFeed.mockResolvedValue({
      projectCount: 2,
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

  it("settles to an actionable error when the visible browser is offline", async () => {
    const online = vi.spyOn(navigator, "onLine", "get").mockReturnValue(false);

    render(<NotificationCenterPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "通知暂时无法读取",
    );
    expect(mocks.getProductTaskFeed).not.toHaveBeenCalled();
    online.mockRestore();
  });

  it("discloses the bounded recent-notification window", async () => {
    mocks.getProductTaskFeed.mockReset();
    mocks.getProductTaskFeed.mockResolvedValue({
      projectCount: 1,
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

  it("filters notifications in place while retaining the persisted research route", async () => {
    mocks.getProductTaskFeed.mockReset();
    mocks.getProductTaskFeed.mockResolvedValue({
      projectCount: 2,
      rows: [
        { jobId: "job-dataset", projectId: "project-a", datasetId: null, researchTurnId: "turn-dataset", jobStatus: "completed", workspaceProjectionStatus: "COMPLETE", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 1, interpretationCount: 1, workspaceId: null, workspaceExists: false, createdAt: "2026-08-30T00:00:00Z", updatedAt: "2026-08-30T01:00:00Z", projectName: "Dataset study" },
        { jobId: "job-xrd", projectId: "project-b", datasetId: null, researchTurnId: "turn-xrd", researchQuestion: "比较实验 XRD 和理论 XRD", jobStatus: "failed", workspaceProjectionStatus: "FAILED", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "FAILED", artifactCount: 0, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-08-30T02:00:00Z", updatedAt: "2026-08-30T03:00:00Z", projectName: "XRD study" },
      ],
      unavailableProjectCount: 0,
      loadedAt: "2026-08-30T03:00:00Z",
    });

    render(<NotificationCenterPage />);
    const user = userEvent.setup();
    await screen.findByText(/Dataset study/);
    const search = screen.getByRole("searchbox", { name: "查找通知" });
    await user.type(search, "理论 XRD");
    expect(screen.queryByText(/Dataset study/)).toBeNull();
    expect(screen.getByText(/XRD study/)).toBeInTheDocument();
    expect(screen.getByText("比较实验 XRD 和理论 XRD")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "打开研究" })).toHaveAttribute(
      "href",
      "/projects/project-b/research?run=job-xrd&turn=turn-xrd",
    );
  });
});
