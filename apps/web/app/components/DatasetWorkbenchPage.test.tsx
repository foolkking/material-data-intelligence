import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

import { DatasetWorkbenchPage } from "./DatasetWorkbenchPage";

vi.mock("./PlannerWorkbench", () => ({
  PlannerWorkbench: (props: { initialProjectId?: string; initialDatasetId?: string; showGlobalContextBar?: boolean }) => (
    <div
      data-testid="embedded-planner"
      data-project-id={props.initialProjectId}
      data-dataset-id={props.initialDatasetId}
      data-global-bar={String(props.showGlobalContextBar)}
    />
  ),
}));

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({
    schemaVersion: "ProjectHistoryView/1.0",
    project: { id: "project_1", projectId: "project_1", name: "Apatite screening" },
    summary: {
      datasetCount: 1,
      analysisCount: 2,
      completedAnalysisCount: 1,
      artifactCount: 3,
      workspaceCount: 1,
      reportCount: 1,
    },
    datasets: [{
      datasetId: "dataset_1",
      name: "materials.csv",
      status: "ready",
      analysisCount: 2,
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
    activity: [],
  }), { status: 200 })));
});

afterEach(() => {
  vi.unstubAllGlobals();
});

it("uses a distinct dataset frame and embeds the planner for the selected dataset", async () => {
  render(<DatasetWorkbenchPage projectId="project_1" datasetId="dataset_1" />);

  expect(await screen.findByRole("heading", { name: "materials.csv" })).toBeInTheDocument();
  expect(screen.getByText("解析状态")).toBeInTheDocument();
  expect(screen.getAllByText("已完成")).toHaveLength(2);
  expect(screen.getByRole("heading", { name: "来源文件与科学资源" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "基于此数据集的分析" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "从来源到结果：每一层负责什么" })).toBeInTheDocument();
  expect(screen.getByText("科学身份与状态")).toBeInTheDocument();
  expect(screen.getByText("语义档案（Profile）")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "项目" })).toHaveAttribute("href", "/projects/project_1");
  expect(screen.getByRole("link", { name: "返回项目" })).toHaveAttribute("href", "/projects/project_1");
  expect(screen.getByRole("link", { name: "导入其他数据" })).toHaveAttribute("href", "/projects/project_1/datasets/new");
  expect(screen.getByRole("link", { name: /Show the distribution of band gap/ })).toHaveAttribute("href", "/projects/project_1/research?run=job_1");

  const planner = screen.getByTestId("embedded-planner");
  expect(planner).toHaveAttribute("data-project-id", "project_1");
  expect(planner).toHaveAttribute("data-dataset-id", "dataset_1");
  expect(planner).toHaveAttribute("data-global-bar", "false");
});
