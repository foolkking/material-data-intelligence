import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

import { ProjectHome } from "./ProjectHome";
import {
  invalidateProductDirectories,
  invalidateProjectHistory,
} from "../lib/planner-api";

const history = {
  schemaVersion: "ProjectHistoryView/1.0",
  project: { id: "project_1", projectId: "project_1", name: "Apatite screening" },
  summary: {
    datasetCount: 1,
    analysisCount: 1,
    completedAnalysisCount: 1,
    artifactCount: 2,
    workspaceCount: 1,
    reportCount: 1,
    lastActivityAt: "2026-08-17T03:03:00Z",
  },
  datasets: [{
    datasetId: "dataset_1",
    name: "materials.csv",
    status: "ready",
    analysisCount: 1,
    lastAnalysisStatus: "succeeded",
    import: { fileCount: 1, files: [], resources: [], parseOutcome: "succeeded" },
    profile: { profileId: "profile_1", rowCount: 25, columnCount: 3, readyCapabilities: ["TABULAR_DATA"] },
  }],
  analyses: [{
    jobId: "job_1",
    datasetId: "dataset_1",
    status: "succeeded",
    userQuestion: "Show the distribution of band gap.",
    toolIds: ["viz.histogram"],
    stepCount: 1,
    artifactCount: 2,
    artifactTypes: ["plot.histogram"],
    interpretationCount: 1,
    reportCount: 1,
    recipeCount: 1,
    workspaceId: "workspace_1",
    workspaceTitle: "Band-gap distribution",
  }],
  activity: [{
    activityId: "analysis:job_1",
    kind: "analysis",
    title: "Show the distribution of band gap.",
    detail: "1 tool, 2 artifacts.",
    status: "succeeded",
    occurredAt: "2026-08-17T03:03:00Z",
    jobId: "job_1",
    workspaceId: "workspace_1",
    href: "/workspaces/workspace_1",
  }],
};

beforeEach(() => {
  invalidateProjectHistory();
  invalidateProductDirectories();
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/projects")) {
      return new Response(JSON.stringify([{ id: "project_1", projectId: "project_1", name: "Apatite screening" }]), { status: 200 });
    }
    if (url.includes("/projects/project_1/history")) {
      return new Response(JSON.stringify(history), { status: 200 });
    }
    return new Response("Not found", { status: 404 });
  }));
});

afterEach(() => {
  invalidateProjectHistory();
  invalidateProductDirectories();
  vi.unstubAllGlobals();
});

it("shows durable datasets and resumes their dedicated workbench", async () => {
  render(<ProjectHome />);

  expect(await screen.findByRole("heading", { name: "项目与数据" })).toBeInTheDocument();
  expect(await screen.findByText("Apatite screening")).toBeInTheDocument();

  const datasetLink = await screen.findByRole("link", { name: /materials\.csv/ });
  expect(datasetLink).toHaveAttribute("href", "/projects/project_1/data?dataset=dataset_1");
  expect(datasetLink).toHaveTextContent("25 行");
  expect(screen.getByRole("link", { name: "导入数据并分析" })).toHaveAttribute(
    "href",
    "/projects/project_1/datasets/new",
  );
  expect(screen.getByRole("link", { name: "导入新数据" })).toHaveAttribute(
    "href",
    "/projects/project_1/datasets/new",
  );

  const workspaceLink = screen.getAllByRole("link", { name: /Show the distribution of band gap/ })[0];
  expect(workspaceLink).toHaveAttribute("href", "/workspaces/workspace_1");
});

it("uses the persisted ResearchTurn status and exact route when a job is stale or failed", async () => {
  const failedHistory = {
    ...history,
    analyses: [{
      ...history.analyses[0],
      status: "running",
      workspaceId: null,
      researchSessionId: "session_exact",
      researchTurnId: "turn_exact",
      researchTurnStatus: "FAILED",
    }],
  };
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/projects")) {
      return new Response(JSON.stringify([{ id: "project_1", projectId: "project_1", name: "Apatite screening" }]), { status: 200 });
    }
    if (url.includes("/projects/project_1/history")) {
      return new Response(JSON.stringify(failedHistory), { status: 200 });
    }
    return new Response("Not found", { status: 404 });
  }));

  render(<ProjectHome />);

  const rows = await screen.findAllByRole("link", { name: /Show the distribution of band gap/ });
  const row = rows.find((item) => item.classList.contains("analysis-history-row"));
  expect(row).toBeDefined();
  expect(row).toHaveAttribute(
    "href",
    "/projects/project_1/research/session_exact?turn=turn_exact",
  );
  expect(row).toHaveTextContent("失败");
  expect(row).not.toHaveTextContent("运行中");
});

it("reuses the bounded history cache when navigating back to a recently opened project", async () => {
  const historyCalls = new Map<string, number>();
  const projects = [
    { id: "project_1", projectId: "project_1", name: "Apatite screening" },
    { id: "project_2", projectId: "project_2", name: "Silicon validation" },
  ];
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/projects")) {
      return new Response(JSON.stringify(projects), { status: 200 });
    }
    const match = url.match(/\/projects\/([^/]+)\/history(?:\?.*)?$/);
    if (match) {
      const projectId = match[1];
      historyCalls.set(projectId, (historyCalls.get(projectId) || 0) + 1);
      return new Response(JSON.stringify({
        ...history,
        project: { ...history.project, projectId, id: projectId, name: projectId },
        pagination: {
          datasets: { nextCursor: null },
          analyses: { nextCursor: null },
          activity: { nextCursor: null },
        },
      }), { status: 200 });
    }
    return new Response("Not found", { status: 404 });
  }));

  render(<ProjectHome />);
  const selector = await screen.findByRole("combobox");
  await screen.findByText("project_1");

  fireEvent.change(selector, { target: { value: "project_2" } });
  await waitFor(() => expect(screen.getByText("project_2")).toBeInTheDocument());
  fireEvent.change(selector, { target: { value: "project_1" } });
  await waitFor(() => expect(screen.getByText("project_1")).toBeInTheDocument());

  expect(historyCalls.get("project_1")).toBe(1);
  expect(historyCalls.get("project_2")).toBe(1);
});

it("reveals bounded project history progressively and keeps the retry action reachable", async () => {
  const longHistory = {
    ...history,
    datasets: Array.from({ length: 10 }, (_, index) => ({
      ...history.datasets[0],
      datasetId: `dataset_${index + 1}`,
      name: `materials-${index + 1}.csv`,
    })),
    analyses: Array.from({ length: 10 }, (_, index) => ({
      ...history.analyses[0],
      jobId: `job_${index + 1}`,
      userQuestion: `分析问题 ${index + 1}`,
    })),
    activity: Array.from({ length: 10 }, (_, index) => ({
      ...history.activity[0],
      activityId: `activity_${index + 1}`,
      title: `活动 ${index + 1}`,
    })),
  };
  let projectRequestCount = 0;
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/projects")) {
      projectRequestCount += 1;
      if (projectRequestCount === 1) {
        return new Response("temporary failure", { status: 503 });
      }
      return new Response(JSON.stringify([{ id: "project_1", projectId: "project_1", name: "Apatite screening" }]), { status: 200 });
    }
    if (url.includes("/projects/project_1/history")) {
      return new Response(JSON.stringify(longHistory), { status: 200 });
    }
    return new Response("Not found", { status: 404 });
  }));

  render(<ProjectHome />);
  expect(await screen.findByRole("alert")).toHaveTextContent("项目历史暂时不可用");
  fireEvent.click(screen.getByRole("button", { name: "重新加载" }));
  expect(await screen.findByText("materials-1.csv")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /显示更多数据集/ })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /显示更多分析/ })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /显示更多活动/ })).toBeInTheDocument();
  expect(screen.queryByText("materials-9.csv")).toBeNull();

  fireEvent.click(screen.getByRole("button", { name: /显示更多数据集/ }));
  expect(screen.getByText("materials-9.csv")).toBeInTheDocument();
});

it("requests bounded history pages and appends a large dataset history deterministically", async () => {
  const allDatasets = Array.from({ length: 1000 }, (_, index) => ({
    ...history.datasets[0],
    datasetId: `dataset_${index + 1}`,
    name: `materials-${index + 1}.csv`,
  }));
  const historyUrls: string[] = [];
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/projects")) {
      return new Response(JSON.stringify([{ id: "project_1", projectId: "project_1", name: "Apatite screening" }]), { status: 200 });
    }
    if (url.includes("/projects/project_1/history")) {
      historyUrls.push(url);
      const query = new URL(url, "http://localhost").searchParams;
      const cursor = Number(query.get("datasets_cursor") || "0");
      const limit = Number(query.get("limit") || "8");
      const page = allDatasets.slice(cursor, cursor + limit);
      return new Response(JSON.stringify({
        ...history,
        datasets: page,
        pagination: {
          datasets: {
            nextCursor: cursor + page.length < allDatasets.length ? String(cursor + page.length) : null,
          },
          analyses: { nextCursor: null },
          activity: { nextCursor: null },
        },
      }), { status: 200 });
    }
    return new Response("Not found", { status: 404 });
  }));

  render(<ProjectHome />);

  expect(await screen.findByText("materials-1.csv")).toBeInTheDocument();
  expect(screen.queryByText("materials-100.csv")).toBeNull();
  const loadMore = screen.getByRole("button", { name: "继续加载数据集" });
  expect(historyUrls[0]).toContain("limit=8");
  fireEvent.click(loadMore);

  await waitFor(() => expect(screen.getByText("materials-100.csv")).toBeInTheDocument());
  expect(historyUrls[1]).toContain("limit=100");
  expect(historyUrls[1]).toContain("datasets_cursor=8");
  expect(screen.queryByText("materials-1000.csv")).toBeNull();
});
