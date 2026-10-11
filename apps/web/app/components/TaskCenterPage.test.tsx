import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const mocks = vi.hoisted(() => ({
  getProductTaskFeed: vi.fn(),
  getProductTaskFeedPage: vi.fn(),
  invalidateProductTaskFeed: vi.fn(),
  cancelAgent2Execution: vi.fn(),
}));

vi.mock("../lib/task-center-data", async (importOriginal) => ({
  ...await importOriginal<typeof import("../lib/task-center-data")>(),
  getProductTaskFeed: mocks.getProductTaskFeed,
  getProductTaskFeedPage: mocks.getProductTaskFeedPage,
  invalidateProductTaskFeed: mocks.invalidateProductTaskFeed,
}));
vi.mock("../lib/agent2-execution-api", () => ({ cancelAgent2Execution: mocks.cancelAgent2Execution }));
vi.mock("../../shared/layout/ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

import { TaskCenterPage } from "./TaskCenterPage";
import { NotificationCenterPage } from "./NotificationCenterPage";
import type { ProductTaskFeed, ProductTaskRow } from "../lib/task-center-data";

function sampleTask(overrides: Partial<ProductTaskRow> = {}): ProductTaskRow {
  return {
    jobId: "job-current", projectId: "project-a", projectName: "材料研究",
    datasetId: "dataset-source", researchTurnId: "turn-current", researchQuestion: "比较材料结构",
    jobStatus: "completed", workspaceProjectionStatus: "COMPLETE", analysisPlanSchemaVersion: "0.2",
    dependencyOutcome: "ALL_SUCCEEDED", artifactCount: 1, interpretationCount: 0,
    workspaceId: null, workspaceExists: false,
    createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(), ...overrides,
  };
}
function sampleFeed(rows = [sampleTask()], nextCursor: string | null = null): ProductTaskFeed {
  return { rows, nextCursor, projectCount: 1, unavailableProjectCount: 0, truncated: Boolean(nextCursor), loadedAt: new Date().toISOString() };
}

describe("TaskCenterPage", () => {
  beforeEach(() => {
    mocks.getProductTaskFeed.mockReset();
    mocks.getProductTaskFeedPage.mockReset();
    mocks.invalidateProductTaskFeed.mockReset();
    mocks.cancelAgent2Execution.mockReset();
  });

  it("opens an analysis in the persisted conversation and Turn", async () => {
    mocks.getProductTaskFeed.mockResolvedValue(sampleFeed([sampleTask({ researchSessionId: "session-owned" })]));
    render(<TaskCenterPage />);
    expect(await screen.findByRole("link", { name: "查看结果" })).toHaveAttribute(
      "href", "/projects/project-a/research/session-owned?turn=turn-current",
    );
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
    expect(screen.getAllByText(/的研究$/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/更新于/).length).toBeGreaterThan(0);
    expect(screen.getAllByText("需要关注").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/超过 15 分钟没有更新/)).toHaveLength(2);
    expect(screen.getByText("已取消")).toBeInTheDocument();
    expect(screen.getAllByText("任务详情")).toHaveLength(5);
    expect(screen.getByText("历史研究记录")).toBeInTheDocument();
    expect(screen.queryByRole("region", { name: "任务概览" })).not.toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /进行中/ })).toHaveTextContent("2");
    expect(screen.getAllByRole("link", { name: "检查进度" }).map((link) => link.getAttribute("href"))).toContain("/projects/project-a/research?run=job-running&turn=turn-running");
    expect(screen.getByRole("link", { name: "查看结果" })).toHaveAttribute("href", "/projects/project-b/research?run=job-complete&turn=turn-complete");
    expect(screen.getAllByRole("link", { name: "查看详情" }).map((link) => link.getAttribute("href"))).toContain("/projects/project-b/research?run=job-failed&turn=turn-failed");
    expect(screen.getAllByRole("link", { name: "调整后重试" }).map((link) => link.getAttribute("href"))).toEqual(expect.arrayContaining([
      "/projects/project-b/research?run=job-failed&turn=turn-failed&retry=1",
      "/projects/project-b/research?run=job-canceled&turn=turn-canceled&retry=1",
    ]));
    expect(screen.getAllByRole("link", { name: /^查看/ }).every((link) => !link.getAttribute("href")?.includes("retry=1"))).toBe(true);
    expect(screen.getAllByRole("link", { name: "调整后重试" }).every((link) => link.getAttribute("title") === "准备新的研究，原记录和结果会保留")).toBe(true);
    expect(screen.getAllByRole("button", { name: "停止研究" })).toHaveLength(1);
    expect(screen.getByRole("tab", { name: /全部/ })).toHaveAttribute("aria-selected", "true");
    mocks.cancelAgent2Execution.mockResolvedValue({ turn_id: "turn-running", status: "CANCELING" });
    fireEvent.click(screen.getAllByRole("button", { name: "停止研究" })[0]);
    expect(await screen.findByRole("dialog", { name: "停止这项研究？" })).toBeInTheDocument();
    expect(screen.getByText(/停止后将保留已完成的结果/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "确认停止" }));
    await waitFor(() => expect(mocks.cancelAgent2Execution).toHaveBeenCalledWith("turn-running"));
    await waitFor(() => expect(mocks.getProductTaskFeed).toHaveBeenCalledTimes(2));
    const cancelNotice = await screen.findByText("停止请求已记录；任务中心会继续同步这项研究的最终状态。");
    expect(cancelNotice).toHaveAttribute("role", "status");
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
    await screen.findByText(/的研究$/);
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
        "超过 15 分钟没有更新，请打开研究检查进度。",
      ),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "检查进度" })).toHaveAttribute(
      "href",
      "/projects/project-a/research?run=job-stale-running&turn=turn-stale-running",
    );
    expect(screen.queryByRole("link", { name: "调整后重试" })).toBeNull();
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
    expect(screen.getByRole("link", { name: "查看结果" })).toHaveAttribute(
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
    expect(screen.getAllByText("正在取消研究")).toHaveLength(2);
    const stop = screen.getByRole("button", {
      name: "正在取消研究",
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
    expect(await screen.findByText(/的研究$/)).toBeInTheDocument();
    window.dispatchEvent(new Event("online"));
    expect(await screen.findByText("正在同步最新状态…")).toBeInTheDocument();
    expect(screen.queryByText("正在加载后台任务…")).toBeNull();
    expect(screen.getByText(/的研究$/)).toBeInTheDocument();
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
    expect(await screen.findByText(/的研究$/)).toBeInTheDocument();
    window.dispatchEvent(new Event("online"));
    expect(await screen.findByText(/同步失败，当前显示上次结果/)).toBeInTheDocument();
    expect(screen.getByText(/的研究$/)).toBeInTheDocument();
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
    expect(await screen.findByText("当前显示 30 项，已加载 31 项。可继续显示其余已加载任务。")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "查看结果" })).toHaveLength(30);
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
    expect(screen.getByRole("link", { name: "查看详情" })).toHaveAttribute(
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
      screen.getAllByRole("link", { name: "查看结果" }).some(
        (link) =>
          link.getAttribute("href") ===
          "/projects/project-a/research?run=job-older&turn=turn-older",
      ),
    ).toBe(true);
    expect(mocks.getProductTaskFeedPage).toHaveBeenCalledWith({
      cursor: "cursor-older",
      signal: expect.any(AbortSignal),
    });
  });

  it("searches displayed Chinese states and preserves the selected filter when clearing an empty search", async () => {
    mocks.getProductTaskFeed.mockResolvedValue(sampleFeed([
      sampleTask(), sampleTask({ jobId: "job-failed", researchQuestion: "检查结构失败原因", jobStatus: "failed" }),
    ]));
    render(<TaskCenterPage />);
    const user = userEvent.setup();
    await screen.findByText("比较材料结构");
    const search = screen.getByRole("searchbox", { name: "查找任务" });
    await user.type(search, "失败");
    expect(screen.getByText("检查结构失败原因")).toBeInTheDocument();
    expect(screen.queryByText("比较材料结构")).toBeNull();
    await user.click(screen.getByRole("tab", { name: "需要关注 1" }));
    await user.clear(search);
    await user.type(search, "不存在的研究");
    await user.click(screen.getByRole("button", { name: "清除搜索" }));
    expect(search).toHaveFocus();
    expect(search).toHaveValue("");
    expect(screen.getByRole("tab", { name: "需要关注 1" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByText("检查结构失败原因")).toBeInTheDocument();
    expect(screen.queryByText("比较材料结构")).toBeNull();
    await user.type(search, "job-failed");
    expect(screen.getByText("检查结构失败原因")).toBeInTheDocument();
  });

  it("searches every joint-analysis source and opens each exact dataset from task details", async () => {
    const sourceDatasets = ["Si", "Cu", "NaCl"].map((name) => ({ datasetId: `dataset-${name}`, name: `${name} 晶体` }));
    mocks.getProductTaskFeed.mockResolvedValue(sampleFeed([
      sampleTask({ jobId: "joint", researchQuestion: "比较三种材料", sourceDatasets }),
      sampleTask({ jobId: "other", researchQuestion: "另一项研究" }),
    ]));
    render(<TaskCenterPage />);
    await screen.findByText("比较三种材料");
    const user = userEvent.setup();
    const search = screen.getByRole("searchbox", { name: "查找任务" });
    for (const source of sourceDatasets) {
      await user.clear(search);
      await user.type(search, source.name);
      expect(screen.getByText("比较三种材料")).toBeInTheDocument();
      expect(screen.queryByText("另一项研究")).not.toBeInTheDocument();
    }
    await user.click(screen.getByText("任务详情"));
    for (const source of sourceDatasets) {
      expect(screen.getByRole("link", { name: source.name })).toHaveAttribute("href", `/projects/project-a/data?dataset=${source.datasetId}`);
    }
    expect(screen.queryByRole("link", { name: "查看源数据" })).not.toBeInTheDocument();
  });

  it("keeps an explicit empty source inventory from exposing the routing dataset as provenance", async () => {
    mocks.getProductTaskFeed.mockResolvedValue(sampleFeed([sampleTask({ sourceDatasets: [] })]));
    render(<TaskCenterPage />);
    await userEvent.click(await screen.findByText("任务详情"));
    expect(screen.getByText("来源待核实")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "查看源数据" })).not.toBeInTheDocument();
  });

  it("keeps queued, stopping and legacy active states out of ended tasks and supports keyboard tab navigation", async () => {
    const statuses = ["created", "queued", "running", "canceling", "cancel_requested", "completed", "unknown"];
    mocks.getProductTaskFeed.mockResolvedValue(sampleFeed(statuses.map((status) => sampleTask({
      jobId: `job-${status}`, researchQuestion: `研究 ${status}`, jobStatus: status,
      ...(status === "created" ? { researchTurnId: null, workspaceProjectionStatus: "LEGACY_READ_ONLY" } : {}),
    }))));
    render(<TaskCenterPage />);
    const user = userEvent.setup();
    const all = await screen.findByRole("tab", { name: "全部 7" });
    all.focus();
    await user.keyboard("{ArrowRight}");
    const active = screen.getByRole("tab", { name: "进行中 5" });
    expect(active).toHaveFocus();
    expect(active).toHaveAttribute("tabindex", "0");
    expect(all).toHaveAttribute("tabindex", "-1");
    expect(screen.getByRole("tabpanel", { name: "进行中 5" }).querySelectorAll("article")).toHaveLength(5);
    expect(screen.getAllByRole("button", { name: "停止研究" })).toHaveLength(2);
    await user.keyboard("{End}");
    expect(screen.getByRole("tab", { name: "已结束 1" })).toHaveFocus();
    const ended = screen.getByRole("tabpanel", { name: "已结束 1" });
    expect(within(ended).getByText("研究 completed")).toBeInTheDocument();
    expect(ended.querySelectorAll("article")).toHaveLength(1);
    await user.keyboard("{Home}{ArrowLeft}");
    expect(screen.getByRole("tab", { name: "已结束 1" })).toHaveFocus();
    fireEvent.click(screen.getByText("任务详情"));
    expect(screen.getByRole("link", { name: "查看源数据" })).toHaveAttribute("href", "/projects/project-a/data?dataset=dataset-source");
  });

  it("preserves the list on older-page timeout, retries the same cursor and ignores its late result", async () => {
    mocks.getProductTaskFeed.mockResolvedValue(sampleFeed([sampleTask()], "older-cursor"));
    let resolveOld!: (feed: ProductTaskFeed) => void;
    mocks.getProductTaskFeedPage.mockImplementationOnce(() => new Promise((resolve) => { resolveOld = resolve; }))
      .mockResolvedValueOnce(sampleFeed([sampleTask({ jobId: "older", researchQuestion: "较早的研究" })]));
    render(<TaskCenterPage />);
    await screen.findByRole("button", { name: "读取更早任务" });
    vi.useFakeTimers();
    try {
      fireEvent.click(screen.getByRole("button", { name: "读取更早任务" }));
      const signal = mocks.getProductTaskFeedPage.mock.calls[0][0].signal;
      await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
      expect(signal.aborted).toBe(true);
      expect(screen.getByText(/更早任务读取超时/)).toBeInTheDocument();
      expect(screen.getByText("比较材料结构")).toBeInTheDocument();
      await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重试读取更早任务" })); });
      expect(screen.getByText("较早的研究")).toBeInTheDocument();
      await act(async () => { resolveOld(sampleFeed([sampleTask({ jobId: "obsolete", researchQuestion: "迟到的旧结果" })])); });
      expect(screen.queryByText("迟到的旧结果")).toBeNull();
      expect(mocks.getProductTaskFeedPage.mock.calls.map(([options]) => options.cursor)).toEqual(["older-cursor", "older-cursor"]);
    } finally { vi.useRealTimers(); }
  });

  it("aborts older-page reads on feed replacement so obsolete pages cannot enter the refreshed list", async () => {
    mocks.getProductTaskFeed.mockResolvedValueOnce(sampleFeed([sampleTask()], "older-cursor"))
      .mockResolvedValue(sampleFeed([sampleTask({ researchQuestion: "已刷新的研究" })], "new-cursor"));
    let resolveOld!: (feed: ProductTaskFeed) => void;
    mocks.getProductTaskFeedPage.mockImplementation(() => new Promise((resolve) => { resolveOld = resolve; }));
    render(<TaskCenterPage />);
    const user = userEvent.setup();
    await user.click(await screen.findByRole("button", { name: "读取更早任务" }));
    const signal = mocks.getProductTaskFeedPage.mock.calls[0][0].signal;
    await user.click(screen.getByRole("button", { name: "重新加载" }));
    await screen.findByText("已刷新的研究");
    expect(signal.aborted).toBe(true);
    await act(async () => { resolveOld(sampleFeed([sampleTask({ jobId: "obsolete", researchQuestion: "过期研究" })])); });
    expect(screen.queryByText("过期研究")).toBeNull();
    await user.click(screen.getByRole("button", { name: "读取更早任务" }));
    expect(mocks.getProductTaskFeedPage).toHaveBeenLastCalledWith({ cursor: "new-cursor", signal: expect.any(AbortSignal) });
  });
});
