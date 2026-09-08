import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const mocks = vi.hoisted(() => ({
  getProductTaskFeed: vi.fn(),
  getProductTaskFeedPage: vi.fn(),
  invalidateProductTaskFeed: vi.fn(),
  cancelAgent2Execution: vi.fn(),
}));

vi.mock("../lib/task-center-data", () => ({
  getProductTaskFeed: mocks.getProductTaskFeed,
  getProductTaskFeedPage: mocks.getProductTaskFeedPage,
  invalidateProductTaskFeed: mocks.invalidateProductTaskFeed,
  productTaskSearchText: (task: { projectName?: string; researchQuestion?: string | null; jobId?: string; jobStatus?: string | null; workspaceProjectionStatus?: string }) =>
    [task.projectName, task.researchQuestion, task.jobId, task.jobStatus, task.workspaceProjectionStatus].filter(Boolean).join(" ").toLocaleLowerCase("zh-CN"),
  sortProductTaskRows: (rows: Array<{ updatedAt?: string; createdAt?: string }>, order = "recent") =>
    [...rows].sort((left, right) => {
      const leftTime = Date.parse(String(left.updatedAt || left.createdAt || "")) || 0;
      const rightTime = Date.parse(String(right.updatedAt || right.createdAt || "")) || 0;
      return order === "oldest" ? leftTime - rightTime : rightTime - leftTime;
    }),
}));
vi.mock("../lib/agent2-execution-api", () => ({ cancelAgent2Execution: mocks.cancelAgent2Execution }));
vi.mock("../../shared/layout/ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

import { TaskCenterPage } from "./TaskCenterPage";
import { NotificationCenterPage } from "./NotificationCenterPage";

describe("TaskCenterPage", () => {
  beforeEach(() => {
    mocks.getProductTaskFeed.mockReset();
    mocks.invalidateProductTaskFeed.mockReset();
    mocks.cancelAgent2Execution.mockReset();
  });

  it("shares one feed request and refresh transition with the notification surface", async () => {
    let resolveInitial:
      | ((value: {
          projectCount: number;
          rows: Array<{
            jobId: string;
            projectId: string;
            datasetId: null;
            researchTurnId: string;
            jobStatus: string;
            workspaceProjectionStatus: string;
            analysisPlanSchemaVersion: string;
            dependencyOutcome: string;
            artifactCount: number;
            interpretationCount: number;
            workspaceId: null;
            workspaceExists: boolean;
            createdAt: string;
            updatedAt: string;
            projectName: string;
          }>;
          unavailableProjectCount: number;
          loadedAt: string;
          truncated: boolean;
        }) => void)
      | undefined;
    const feed = {
      projectCount: 1,
      rows: [
        {
          jobId: "job-shared",
          projectId: "project-a",
          datasetId: null,
          researchTurnId: "turn-shared",
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
          projectName: "Shared Project",
        },
      ],
      unavailableProjectCount: 0,
      loadedAt: "2026-09-05T01:01:00Z",
      truncated: false,
    };
    mocks.getProductTaskFeed
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            resolveInitial = resolve;
          }),
      )
      .mockResolvedValue(feed);

    render(
      <>
        <TaskCenterPage />
        <NotificationCenterPage />
      </>,
    );
    await waitFor(() =>
      expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(1),
    );
    resolveInitial?.(feed);
    expect(await screen.findByRole("heading", { name: "全部任务" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "最近通知" })).toBeInTheDocument();
    expect(screen.getAllByText("Shared Project").length).toBeGreaterThanOrEqual(1);

    mocks.getProductTaskFeed.mockClear();
    window.dispatchEvent(new Event("online"));
    await waitFor(() =>
      expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(1),
    );
    expect(screen.getAllByText(/最近同步/)).toHaveLength(2);
  });

  it("aggregates authorized project jobs and preserves exact workspace navigation", async () => {
    mocks.getProductTaskFeed.mockResolvedValue({
      projectCount: 2,
      rows: [
        ...[{ jobId: "job-running", projectId: "project-a", datasetId: null, researchTurnId: "turn-running", researchQuestion: "比较 CrystalNN 与 VoronoiNN", jobStatus: "running", workspaceProjectionStatus: "RUNNING", analysisPlanSchemaVersion: "0.2", dependencyOutcome: null, artifactCount: 1, interpretationCount: 0, workspaceId: "workspace-1", workspaceExists: true, createdAt: "2026-08-28T00:00:00Z", updatedAt: "2026-08-28T01:00:00Z", projectName: "Project A" }],
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
    expect(screen.getByText("比较 CrystalNN 与 VoronoiNN")).toBeInTheDocument();
    expect(screen.getAllByText("可恢复研究").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/更新于/).length).toBeGreaterThan(0);
    expect(screen.getAllByText("需要关注").length).toBeGreaterThan(0);
    expect(screen.getByText(/持久化状态仍为运行中，但已超过 15 分钟没有更新/)).toBeInTheDocument();
    expect(screen.getByText("历史研究")).toBeInTheDocument();
    expect(screen.getByText("已取消")).toBeInTheDocument();
    expect(screen.getAllByText("技术身份").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/可恢复研究会话/).length).toBeGreaterThan(0);
    expect(screen.getByText(/历史运行 · 仅查看/)).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "任务概览" })).toHaveTextContent("1");
    expect(screen.getByRole("link", { name: "打开并检查" })).toHaveAttribute("href", "/projects/project-a/research?run=job-running&turn=turn-running");
    expect(screen.getAllByRole("link", { name: "打开" }).map((link) => link.getAttribute("href"))).toContain("/projects/project-b/research?run=job-complete&turn=turn-complete");
    expect(screen.getAllByRole("link", { name: "打开" }).map((link) => link.getAttribute("href"))).toContain("/projects/project-b/research?run=job-failed&turn=turn-failed");
    expect(screen.getAllByRole("link", { name: "打开并重试（新运行）" }).map((link) => link.getAttribute("href"))).toEqual(expect.arrayContaining([
      "/projects/project-b/research?run=job-failed&turn=turn-failed&retry=1",
      "/projects/project-b/research?run=job-canceled&turn=turn-canceled&retry=1",
    ]));
    expect(screen.getAllByRole("link", { name: "打开" }).every((link) => !link.getAttribute("href")?.includes("retry=1"))).toBe(true);
    expect(screen.getAllByRole("link", { name: "打开并重试（新运行）" }).every((link) => link.getAttribute("title") === "创建新的 ResearchTurn；原失败运行及其证据保留")).toBe(true);
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
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "重新加载" })).toBeEnabled(),
    );
    fireEvent.click(screen.getByRole("button", { name: "重新加载" }));
    await waitFor(() => expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(1));
    expect(mocks.getProductTaskFeed).toHaveBeenLastCalledWith(
      expect.objectContaining({
        forceRefresh: true,
        signal: expect.any(AbortSignal),
      }),
    );
    mocks.getProductTaskFeed.mockClear();
    fireEvent(window, new Event("online"));
    await waitFor(() => expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(1));
    expect(mocks.getProductTaskFeed).toHaveBeenLastCalledWith(
      expect.objectContaining({
        forceRefresh: false,
        signal: expect.any(AbortSignal),
      }),
    );
  });

  it("pauses hidden-tab polling, aborts the obsolete request and refreshes on return", async () => {
    const visibility = vi
      .spyOn(document, "visibilityState", "get")
      .mockReturnValue("visible");
    const feed = {
      projectCount: 1,
      rows: [
        {
          jobId: "job-complete",
          projectId: "project-a",
          datasetId: null,
          researchTurnId: "turn-complete",
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

    render(<TaskCenterPage />);
    await screen.findByText("可恢复研究");
    mocks.getProductTaskFeed.mockClear();
    window.dispatchEvent(new Event("online"));
    await waitFor(() => expect(refreshSignal).toBeDefined());
    expect(refreshSignal?.aborted).toBe(false);

    visibility.mockReturnValue("hidden");
    document.dispatchEvent(new Event("visibilitychange"));
    expect(refreshSignal?.aborted).toBe(true);
    window.dispatchEvent(new Event("online"));
    expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(1);

    visibility.mockReturnValue("visible");
    document.dispatchEvent(new Event("visibilitychange"));
    await waitFor(() =>
      expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(2),
    );
    visibility.mockRestore();
  });

  it("surfaces an unchanged running task in attention without claiming a retry", async () => {
    const staleUpdatedAt = new Date(Date.now() - 16 * 60 * 1000).toISOString();
    const freshUpdatedAt = new Date(Date.now() - 2 * 60 * 1000).toISOString();
    mocks.getProductTaskFeed.mockResolvedValue({
      projectCount: 1,
      rows: [
        {
          jobId: "job-stale-running",
          projectId: "project-a",
          datasetId: null,
          researchTurnId: "turn-stale-running",
          researchQuestion: "检查停滞的结构研究",
          jobStatus: "running",
          workspaceProjectionStatus: "RUNNING",
          analysisPlanSchemaVersion: "0.2",
          dependencyOutcome: null,
          artifactCount: 1,
          interpretationCount: 0,
          workspaceId: null,
          workspaceExists: false,
          createdAt: staleUpdatedAt,
          updatedAt: staleUpdatedAt,
          projectName: "Project A",
        },
        {
          jobId: "job-fresh-running",
          projectId: "project-a",
          datasetId: null,
          researchTurnId: "turn-fresh-running",
          researchQuestion: "正常运行的结构研究",
          jobStatus: "running",
          workspaceProjectionStatus: "RUNNING",
          analysisPlanSchemaVersion: "0.2",
          dependencyOutcome: null,
          artifactCount: 0,
          interpretationCount: 0,
          workspaceId: null,
          workspaceExists: false,
          createdAt: freshUpdatedAt,
          updatedAt: freshUpdatedAt,
          projectName: "Project A",
        },
      ],
      unavailableProjectCount: 0,
      loadedAt: new Date().toISOString(),
    });

    render(<TaskCenterPage />);
    const user = userEvent.setup();
    await screen.findByText("检查停滞的结构研究");
    await user.click(screen.getByRole("tab", { name: "需要关注 1" }));

    expect(screen.getByText("检查停滞的结构研究")).toBeInTheDocument();
    expect(screen.queryByText("正常运行的结构研究")).toBeNull();
    expect(screen.getAllByText("需要关注").length).toBeGreaterThan(0);
    expect(
      screen.getByText(
        "持久化状态仍为运行中，但已超过 15 分钟没有更新；打开研究核对最新状态。",
      ),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "打开并检查" })).toHaveAttribute(
      "href",
      "/projects/project-a/research?run=job-stale-running&turn=turn-stale-running",
    );
    expect(screen.queryByRole("link", { name: "打开并重试" })).toBeNull();
    expect(screen.getByRole("button", { name: "停止研究" })).toBeInTheDocument();
  });

  it("keeps available tasks usable while disclosing a partial project sync", async () => {
    mocks.getProductTaskFeed.mockResolvedValue({
      projectCount: 2,
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

  it("uses the Research cancellation language and disables conflicting Task Center controls", async () => {
    const feed = {
      projectCount: 1,
      rows: [
        {
          jobId: "job-canceling",
          projectId: "project-a",
          datasetId: null,
          researchTurnId: "turn-canceling",
          researchQuestion: "正在停止的结构研究",
          jobStatus: "cancel_requested",
          workspaceProjectionStatus: "CANCELING",
          analysisPlanSchemaVersion: "0.2",
          dependencyOutcome: null,
          artifactCount: 0,
          interpretationCount: 0,
          workspaceId: null,
          workspaceExists: false,
          createdAt: "2026-09-05T01:00:00Z",
          updatedAt: "2026-09-05T01:01:00Z",
          projectName: "Project A",
        },
      ],
      unavailableProjectCount: 0,
      loadedAt: "2026-09-05T01:01:00Z",
      truncated: false,
    };
    mocks.getProductTaskFeed.mockResolvedValue(feed);

    render(<TaskCenterPage />);

    expect(await screen.findByText("正在停止的结构研究")).toBeInTheDocument();
    expect(screen.getByText("正在取消研究")).toBeInTheDocument();
    const stop = screen.getByRole("button", {
      name: "正在取消研究，等待服务端确认",
    });
    expect(stop).toBeDisabled();
    expect(screen.queryByRole("button", { name: "停止研究" })).toBeNull();
  });

  it("uses the fast cancellation refresh cadence while a task is canceling", async () => {
    const interval = vi.spyOn(window, "setInterval");
    mocks.getProductTaskFeed.mockResolvedValue({
      projectCount: 1,
      rows: [
        {
          jobId: "job-canceling-cadence",
          projectId: "project-a",
          datasetId: null,
          researchTurnId: "turn-canceling-cadence",
          researchQuestion: "检查取消节奏",
          jobStatus: "cancel_requested",
          workspaceProjectionStatus: "CANCELING",
          analysisPlanSchemaVersion: "0.2",
          dependencyOutcome: null,
          artifactCount: 0,
          interpretationCount: 0,
          workspaceId: null,
          workspaceExists: false,
          createdAt: "2026-09-05T01:00:00Z",
          updatedAt: "2026-09-05T01:01:00Z",
          projectName: "Project A",
        },
      ],
      unavailableProjectCount: 0,
      loadedAt: "2026-09-05T01:01:00Z",
      truncated: false,
    });

    render(<TaskCenterPage />);
    await screen.findByText("检查取消节奏");

    expect(
      interval.mock.calls.map(([, delay]) => delay),
    ).toContain(1800);
    interval.mockRestore();
  });

  it("keeps the current task list visible while a background refresh is in flight", async () => {
    mocks.getProductTaskFeed.mockReset();
    const feed = {
      projectCount: 1,
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
      projectCount: 1,
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
    render(<TaskCenterPage />);
    expect(await screen.findByText("当前筛选显示最近 30 项；更早任务仍保留在项目历史中。")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "打开" })).toHaveLength(30);
  });

  it("filters long task feeds by project or status without changing exact navigation", async () => {
    mocks.getProductTaskFeed.mockReset();
    mocks.getProductTaskFeed.mockResolvedValue({
      projectCount: 2,
      rows: [
        { jobId: "job-silicon", projectId: "project-a", datasetId: null, researchTurnId: "turn-silicon", researchQuestion: "比较 CrystalNN 和 VoronoiNN 配位", jobStatus: "completed", workspaceProjectionStatus: "COMPLETE", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 1, interpretationCount: 1, workspaceId: null, workspaceExists: false, createdAt: "2026-08-30T00:00:00Z", updatedAt: "2026-08-30T01:00:00Z", projectName: "Silicon study" },
        { jobId: "job-failed", projectId: "project-b", datasetId: null, researchTurnId: "turn-failed", jobStatus: "failed", workspaceProjectionStatus: "FAILED", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "FAILED", artifactCount: 0, interpretationCount: 0, workspaceId: null, workspaceExists: false, createdAt: "2026-08-30T02:00:00Z", updatedAt: "2026-08-30T03:00:00Z", projectName: "Polymer study" },
      ],
      unavailableProjectCount: 0,
      loadedAt: "2026-08-30T03:00:00Z",
    });

    render(<TaskCenterPage />);
    const user = userEvent.setup();
    await screen.findByText("Silicon study");
    const search = screen.getByRole("searchbox", { name: "查找任务" });
    await user.type(search, "VoronoiNN");
    expect(screen.getByText("比较 CrystalNN 和 VoronoiNN 配位")).toBeInTheDocument();
    expect(screen.queryByText("Polymer study")).toBeNull();
    await user.clear(search);
    await user.type(search, "failed");
    expect(screen.queryByText("Silicon study")).toBeNull();
    expect(screen.getByText("Polymer study")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "打开" })).toHaveAttribute(
      "href",
      "/projects/project-b/research?run=job-failed&turn=turn-failed",
    );
    await user.selectOptions(screen.getByRole("combobox", { name: "排序" }), "oldest");
    expect(screen.getByRole("combobox", { name: "排序" })).toHaveValue("oldest");
  });

  it("loads an older cursor page and preserves its exact ResearchTurn link", async () => {
    const firstTask = {
      jobId: "job-first",
      projectId: "project-a",
      datasetId: null,
      researchTurnId: "turn-first",
      jobStatus: "completed",
      workspaceProjectionStatus: "COMPLETE",
      analysisPlanSchemaVersion: "0.2",
      dependencyOutcome: "ALL_SUCCEEDED",
      artifactCount: 1,
      interpretationCount: 1,
      workspaceId: null,
      workspaceExists: false,
      createdAt: "2026-09-05T00:00:00Z",
      updatedAt: "2026-09-05T00:01:00Z",
      projectName: "Project A",
    };
    const olderTask = {
      ...firstTask,
      jobId: "job-older",
      researchTurnId: "turn-older",
      researchQuestion: "旧页面的结构研究",
      updatedAt: "2026-09-04T00:01:00Z",
    };
    mocks.getProductTaskFeed.mockResolvedValue({
      projectCount: 1,
      rows: [firstTask],
      unavailableProjectCount: 0,
      loadedAt: "2026-09-05T00:01:00Z",
      truncated: true,
      nextCursor: "cursor-older",
    });
    mocks.getProductTaskFeedPage.mockResolvedValue({
      projectCount: 1,
      rows: [olderTask],
      unavailableProjectCount: 0,
      loadedAt: "2026-09-05T00:02:00Z",
      truncated: false,
      nextCursor: null,
    });

    render(<TaskCenterPage />);
    const user = userEvent.setup();
    const loadMore = await screen.findByRole("button", { name: "读取更早任务" });
    await user.click(loadMore);

    expect(await screen.findByText("旧页面的结构研究")).toBeInTheDocument();
    expect(
      screen.getAllByRole("link", { name: "打开" }).some(
        (link) =>
          link.getAttribute("href") ===
          "/projects/project-a/research?run=job-older&turn=turn-older",
      ),
    ).toBe(true);
    expect(mocks.getProductTaskFeedPage).toHaveBeenCalledWith({
      cursor: "cursor-older",
    });
  });
});
