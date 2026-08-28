import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

import type { InterpretationEvidenceResponse, ProjectHistory } from "../lib/planner-api";

const mocks = vi.hoisted(() => ({
  createResearchMessage: vi.fn(),
  createResearchAssistantProjection: vi.fn(),
  createResearchSession: vi.fn(),
  getProjectHistory: vi.fn(),
  getResearchSession: vi.fn(),
  listResearchSessions: vi.fn(),
  resolveResearchScope: vi.fn(),
  createPlannerJob: vi.fn(),
  createPlannerJobInterpretation: vi.fn(),
  getPlannerJob: vi.fn(),
  getPlannerJobArtifacts: vi.fn(),
  getPlannerJobEvents: vi.fn(),
  getPlannerJobInterpretations: vi.fn(),
  getPlannerInterpretationEvidence: vi.fn(),
  getPlannerProviderStatus: vi.fn(),
  listPlannerProviders: vi.fn(),
  getAgent2SessionMemory: vi.fn(),
}));

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }) }));

vi.mock("../lib/product-api", () => ({
  createResearchMessage: mocks.createResearchMessage,
  createResearchAssistantProjection: mocks.createResearchAssistantProjection,
  createResearchSession: mocks.createResearchSession,
  getResearchSession: mocks.getResearchSession,
  listResearchSessions: mocks.listResearchSessions,
  resolveResearchScope: mocks.resolveResearchScope,
}));

vi.mock("../lib/planner-api", () => ({
  createPlannerJob: mocks.createPlannerJob,
  createPlannerJobInterpretation: mocks.createPlannerJobInterpretation,
  getProjectHistory: mocks.getProjectHistory,
  getPlannerJob: mocks.getPlannerJob,
  getPlannerJobArtifacts: mocks.getPlannerJobArtifacts,
  getPlannerJobEvents: mocks.getPlannerJobEvents,
  getPlannerJobInterpretations: mocks.getPlannerJobInterpretations,
  getPlannerInterpretationEvidence: mocks.getPlannerInterpretationEvidence,
  getPlannerProviderStatus: mocks.getPlannerProviderStatus,
  listPlannerProviders: mocks.listPlannerProviders,
}));

vi.mock("../lib/agent2-memory-api", () => ({
  getAgent2SessionMemory: mocks.getAgent2SessionMemory,
}));

vi.mock("./ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => (
    <>{children}</>
  ),
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => (
    <>{children}</>
  ),
}));

vi.mock("./ScientificViewerAdapter", () => ({
  ScientificResultViewer: () => <div data-testid="scientific-result-viewer" />,
}));

import {
  displayResearchMessage,
  groundedEvidenceNarrative,
  mergeArtifacts,
  mergeJobEvents,
  ResearchPage,
  researchStarterPrompts,
  researchTechnicalSummary,
  runProcessStepState,
  userFacingPlanStep,
} from "./ResearchPages";

function starterHistory(profiles: Array<ProjectHistory["datasets"][number]["profile"]>): ProjectHistory {
  return {
    schemaVersion: "ProjectHistoryView/1.0",
    project: { id: "project_1", name: "研究项目", role: "owner" },
    summary: { datasetCount: profiles.length, analysisCount: 0, completedAnalysisCount: 0, artifactCount: 0, workspaceCount: 0, reportCount: 0 },
    datasets: profiles.map((profile, index) => ({
      datasetId: `dataset_${index + 1}`,
      name: `dataset-${index + 1}`,
      status: "profile_ready",
      analysisCount: 0,
      process: [],
      resultSummary: { artifactCount: 0, workspaceCount: 0, interpretationCount: 0, reportCount: 0, recipeCount: 0, artifactTypes: [] },
      import: { fileCount: 1, files: [], resources: [], parseOutcome: "succeeded" },
      profile,
    })),
    analyses: [],
    activity: [],
  };
}

it("derives at most three starter questions from normalized project capabilities", () => {
  const prompts = researchStarterPrompts(starterHistory([{
    datasetType: "Materials_Tabular_Dataset",
    readyCapabilities: ["STRUCTURE.EXPERIMENTAL_XRD_COMPARISON", "trajectory_visualization", "phonon_visualization", "volumetric_visualization"],
    semanticRoles: { formation_energy: 4, band_gap: 4 },
  }]));

  expect(prompts).toEqual([
    { id: "experimental-xrd", question: "比较实验与理论 XRD" },
    { id: "trajectory", question: "查看 AIMD 轨迹并概览结构演化" },
    { id: "phonon", question: "查看声子能带与态密度" },
  ]);
});

it("only offers the formation-energy relation when both exact semantics exist", () => {
  const history = (semanticRoles: Record<string, number>) => starterHistory([{ semanticRoles }]);

  expect(researchStarterPrompts(history({ formation_energy: 2, band_gap: 2 }))).toContainEqual({
    id: "formation-energy-band-gap",
    question: "比较 formation energy 与 band gap 的关系",
  });
  expect(researchStarterPrompts(history({ formation_energy: 2 }))).toEqual([
    { id: "project-overview", question: "概览当前项目数据与可用分析" },
  ]);
  expect(researchStarterPrompts(history({ formation_energy_prediction: 2, band_gap_prediction: 2 }))).toEqual([
    { id: "project-overview", question: "概览当前项目数据与可用分析" },
  ]);
});

it("summarizes structured result metadata without loading payloads", () => {
  const summary = researchTechnicalSummary(
    { ok: true, job_id: "job_1", plan_id: "plan_1" },
    [
      { artifactId: "plot_1", type: "plotly_json", name: "rdf_plot.json", contentType: "application/json" },
      { artifactId: "table_1", type: "table_csv", name: "rdf.csv", contentType: "text/csv" },
      { artifactId: "recipe_1", type: "recipe_json", name: "recipe.json" },
    ],
  );

  expect(summary).toMatchObject({
    runId: "job_1",
    planId: "plan_1",
    outputCount: 2,
    structuredOutputCount: 2,
    structuredOutputLabel: "rdf_plot.json、recipe.json",
  });
  expect(researchTechnicalSummary(null, [])).toMatchObject({
    runId: null,
    planId: null,
    outputCount: 0,
    structuredOutputCount: 0,
    structuredOutputLabel: "暂无 JSON 输出",
  });
});

beforeEach(() => {
  vi.clearAllMocks();
  mocks.listResearchSessions.mockResolvedValue([]);
  mocks.getAgent2SessionMemory.mockResolvedValue({
    session_id: "session_1", project_id: "project_1", pinned_object_refs: [],
    pinned_result_refs: [], session_constraints: [], active_research_goal: null, version: 1,
  });
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{ datasetId: "dataset_a" }, { datasetId: "dataset_b" }],
    analyses: [],
  });
  mocks.createResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "研究会话",
    status: "active",
    messages: [],
  });
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "研究会话",
    status: "active",
    messages: [],
  });
  mocks.createResearchMessage
    .mockResolvedValueOnce({
      id: "message_question",
      session_id: "session_1",
      role: "user",
      content: "比较两个数据集",
      created_at: "2026-08-18T00:00:00Z",
    })
    .mockResolvedValueOnce({
      id: "message_selection",
      session_id: "session_1",
      role: "user",
      content: "已选择数据集：materials-b",
      created_at: "2026-08-18T00:00:01Z",
    });
  mocks.createResearchAssistantProjection.mockImplementation(
    async (sessionId: string, projection: { phase: string }) => ({
      id: `assistant_${projection.phase}`,
      session_id: sessionId,
      role: "assistant",
      content: projection.phase,
      created_at: "2026-08-18T00:00:02Z",
    }),
  );
  mocks.resolveResearchScope.mockResolvedValue({
    status: "NEEDS_CLARIFICATION",
    reason: "这个问题可以使用多个数据集。",
    candidates: [
      {
        dataset_id: "dataset_a",
        profile_id: "profile_a",
        name: "materials-a",
        semantics: ["formation_energy"],
      },
      {
        dataset_id: "dataset_b",
        profile_id: "profile_b",
        name: "materials-b",
        semantics: ["band_gap"],
      },
    ],
  });
  mocks.createPlannerJob.mockResolvedValue({
    ok: true,
    job_id: "job_1",
    plan_hash: "a".repeat(64),
    plan: { goal: "比较两个数据集", datasetId: "dataset_b", steps: [] },
  });
  mocks.getPlannerJob.mockResolvedValue({
    status: "completed",
    analysisPlan: { goal: "比较两个数据集", datasetId: "dataset_b", steps: [] },
    planHash: "a".repeat(64),
  });
  mocks.getPlannerJobEvents.mockResolvedValue([]);
  mocks.getPlannerJobArtifacts.mockResolvedValue([]);
  mocks.getPlannerJobInterpretations.mockResolvedValue({ interpretations: [] });
  mocks.getPlannerInterpretationEvidence.mockResolvedValue({
    evidenceItems: [],
  });
  mocks.getPlannerProviderStatus.mockResolvedValue({
    ok: true,
    provider: "deepseek",
    model: "deepseek-v4-flash",
    status: "ready",
  });
  mocks.listPlannerProviders.mockResolvedValue({
    providers: [
      {
        provider: "deepseek",
        label: "DeepSeek",
        defaultModel: "deepseek-v4-flash",
        allowedModels: ["deepseek-v4-flash"],
        secretConfigured: true,
        execution: "live",
      },
    ],
  });
  mocks.createPlannerJobInterpretation.mockResolvedValue({ ok: true });
});

it("puts a capability-aware starter question in the composer without submitting", async () => {
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" />);

  expect(await screen.findByRole("region", { name: "从 2 个项目数据集开始" })).toBeInTheDocument();
  const suggestion = screen.getByRole("button", { name: /概览当前项目数据与可用分析/ });
  await user.click(suggestion);
  const composer = screen.getByLabelText("询问此项目中的数据");
  expect(composer).toHaveValue("概览当前项目数据与可用分析");
  await waitFor(() => expect(composer).toHaveFocus());
  expect(mocks.createResearchSession).not.toHaveBeenCalled();
  expect(mocks.createResearchMessage).not.toHaveBeenCalled();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  expect(screen.queryByText("可以尝试")).not.toBeInTheDocument();
});

it("replaces a doomed empty-project composer with the permitted upload action", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "空项目", role: "owner" },
    datasets: [],
    analyses: [],
  });
  render(<ResearchPage projectId="project_1" />);

  expect(await screen.findByRole("heading", { name: "先为项目添加数据" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "上传数据" })).toHaveAttribute("href", "/projects/project_1/datasets/new");
  expect(screen.queryByLabelText("询问此项目中的数据")).not.toBeInTheDocument();
});

it("keeps the no-data starter read-only for a viewer", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "共享空项目", role: "viewer" },
    datasets: [],
    analyses: [],
  });
  render(<ResearchPage projectId="project_1" />);

  expect(await screen.findByRole("heading", { name: "这个项目还没有可研究的数据" })).toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "上传数据" })).not.toBeInTheDocument();
  expect(screen.queryByLabelText("询问此项目中的数据")).not.toBeInTheDocument();
});

it("does not show first-use guidance inside an existing conversation", async () => {
  mocks.listResearchSessions.mockResolvedValue([{ id: "session_1", project_id: "project_1", title: "既有研究", status: "active" }]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "既有研究",
    status: "active",
    messages: [{ id: "message_1", session_id: "session_1", role: "user", content: "查看结构", created_at: "2026-08-22T00:00:00Z" }],
  });
  render(<ResearchPage projectId="project_1" sessionId="session_1" />);

  expect(await screen.findByRole("article", { name: "你的消息" })).toHaveTextContent("查看结构");
  expect(screen.queryByText("研究起点")).not.toBeInTheDocument();
});

it("shows bounded session constraints without exposing internal ids", async () => {
  mocks.listResearchSessions.mockResolvedValue([{ id: "session_1", project_id: "project_1", title: "连续研究", status: "active" }]);
  mocks.getAgent2SessionMemory.mockResolvedValue({
    session_id: "session_1", project_id: "project_1", pinned_object_refs: [{ object_type: "structure.crystal", display_name: "LiFePO4" }],
    pinned_result_refs: ["internal-result-id"],
    session_constraints: [{ id: "constraint-id", statement: "后续 RDF cutoff 固定为 8 Å", structured_constraint: { value: 8 } }],
    active_research_goal: "比较 LiFePO4 的局域结构", version: 2,
  });
  render(<ResearchPage projectId="project_1" sessionId="session_1" />);

  const context = await screen.findByRole("region", { name: "当前研究会话上下文" });
  expect(context).toHaveTextContent("后续 RDF cutoff 固定为 8 Å");
  expect(context).toHaveTextContent("固定结果 1");
  expect(context).not.toHaveTextContent("internal-result-id");
  expect(context).not.toHaveTextContent("constraint-id");
});

it("persists the selected dataset in the same research session before creating a scoped job", async () => {
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" />);

  const composer = await screen.findByLabelText("询问此项目中的数据");
  await user.type(composer, "比较两个数据集");
  await user.click(screen.getByRole("button", { name: "开始分析" }));

  expect(
    await screen.findByRole("heading", {
      name: "本次分析可以使用多个数据集。",
    }),
  ).toBeInTheDocument();
  await user.click(screen.getByLabelText(/materials-b/));
  await user.click(screen.getByRole("button", { name: "确认数据范围" }));

  await waitFor(() =>
    expect(mocks.createPlannerJob).toHaveBeenCalledWith(
      expect.objectContaining({
        projectId: "project_1",
        datasetId: "dataset_b",
        profileId: "profile_b",
        enqueue: true,
      }),
    ),
  );
  expect(mocks.createResearchMessage).toHaveBeenNthCalledWith(
    2,
    "session_1",
    "使用 materials-b 继续分析。",
    "dataset_b",
  );
  expect(mocks.createPlannerJob).toHaveBeenCalledWith(
    expect.objectContaining({ researchSessionId: "session_1" }),
  );
  expect(mocks.createPlannerJob.mock.calls[0][0]).not.toHaveProperty(
    "datasetIds",
  );
  const preRunCall = mocks.createResearchAssistantProjection.mock.calls.find(
    ([, projection]) => projection.phase === "pre_run",
  );
  expect(preRunCall?.[0]).toBe("session_1");
  expect(preRunCall?.[1]).toMatchObject({
    phase: "pre_run",
    datasetId: "dataset_b",
    runId: "job_1",
  });
  expect(preRunCall?.[1]).not.toHaveProperty("steps");
  expect(screen.getByRole("tab", { name: "工作台" })).toHaveAttribute("aria-selected", "true");
});

it("adjusts the conversation splitter with keyboard arrows", async () => {
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" />);

  const splitter = await screen.findByRole("separator", {
    name: "调整研究对话宽度",
  });
  expect(splitter).toHaveAttribute("aria-valuenow", "420");
  splitter.focus();
  await user.keyboard("{ArrowRight}");
  expect(splitter).toHaveAttribute("aria-valuenow", "436");
  await user.keyboard("{ArrowLeft}");
  expect(splitter).toHaveAttribute("aria-valuenow", "420");
  await user.keyboard("{End}");
  expect(splitter).toHaveAttribute("aria-valuenow", "640");
  await user.keyboard("{Home}");
  expect(splitter).toHaveAttribute("aria-valuenow", "320");
});

it("adjusts the conversation splitter with a pointer drag", async () => {
  render(<ResearchPage projectId="project_1" />);

  const workbench = await screen.findByRole("region", {
    name: "项目研究工作台",
  });
  const splitter = screen.getByRole("separator", { name: "调整研究对话宽度" });
  vi.spyOn(workbench, "getBoundingClientRect").mockReturnValue({
    left: 0,
    width: 1200,
  } as DOMRect);
  Object.defineProperties(splitter, {
    setPointerCapture: { value: vi.fn() },
    hasPointerCapture: { value: vi.fn(() => true) },
    releasePointerCapture: { value: vi.fn() },
  });

  fireEvent(
    splitter,
    new MouseEvent("pointerdown", { bubbles: true, clientX: 480 }),
  );
  fireEvent(
    splitter,
    new MouseEvent("pointermove", { bubbles: true, clientX: 560 }),
  );
  fireEvent(
    splitter,
    new MouseEvent("pointerup", { bubbles: true, clientX: 560 }),
  );

  expect(splitter).toHaveAttribute("aria-valuenow", "560");
});

it("keeps a viewer project readable without a research composer", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "共享研究项目", role: "viewer" },
    datasets: [{ datasetId: "dataset_a" }],
    analyses: [],
  });
  render(<ResearchPage projectId="project_1" />);
  expect(await screen.findByText("此项目为只读")).toBeInTheDocument();
  expect(screen.queryByLabelText("询问此项目中的数据")).not.toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: "开始分析" }),
  ).not.toBeInTheDocument();
});

it("exposes the conversation as a labelled log with message roles", async () => {
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "形成能与带隙关系",
    status: "active",
    messages: [
      {
        id: "message_1",
        session_id: "session_1",
        role: "assistant",
        content: "我会先检查当前数据。",
        created_at: "2026-08-18T00:00:00Z",
      },
    ],
  });
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_1",
      project_id: "project_1",
      title: "形成能与带隙关系",
      status: "active",
    },
  ]);
  render(<ResearchPage projectId="project_1" sessionId="session_1" />);

  expect(
    await screen.findByRole("log", { name: "研究对话" }),
  ).toBeInTheDocument();
  expect(
    await screen.findByRole("article", { name: "研究助手消息" }),
  ).toHaveTextContent("我会先检查当前数据。");
  expect(
    screen.getByRole("separator", { name: "调整研究对话宽度" }),
  ).toHaveAttribute("tabindex", "0");
});

it("shows an honest retry state when the initial research context cannot load", async () => {
  const user = userEvent.setup();
  mocks.getProjectHistory.mockRejectedValueOnce(
    new Error("network unavailable"),
  );
  render(<ResearchPage projectId="project_1" />);

  expect(
    await screen.findByRole("heading", { name: "研究内容暂时无法加载" }),
  ).toBeInTheDocument();
  expect(screen.queryByText("正在确认项目权限…")).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重新加载" }));
  expect(
    await screen.findByLabelText("询问此项目中的数据"),
  ).toBeInTheDocument();
  expect(mocks.getProjectHistory).toHaveBeenCalledTimes(2);
});

it("keeps the selected session explicit when its detail request fails and retries it", async () => {
  const user = userEvent.setup();
  const summary = {
    id: "session_1",
    project_id: "project_1",
    title: "形成能研究",
    status: "active",
    messages: [],
  };
  mocks.listResearchSessions.mockResolvedValue([summary]);
  mocks.getResearchSession
    .mockRejectedValueOnce(new Error("session unavailable"))
    .mockResolvedValueOnce(summary);
  render(<ResearchPage projectId="project_1" sessionId="session_1" />);

  expect(await screen.findByText("研究对话暂时无法读取")).toBeInTheDocument();
  expect(screen.queryByLabelText("询问此项目中的数据")).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重新加载对话" }));
  expect(
    await screen.findByLabelText("询问此项目中的数据"),
  ).toBeInTheDocument();
  expect(mocks.getResearchSession).toHaveBeenCalledTimes(2);
});

it("focuses and closes the research history popover with localized status", async () => {
  const user = userEvent.setup();
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_done",
      project_id: "project_1",
      title: "声子色散分析",
      status: "completed",
    },
    {
      id: "session_running",
      project_id: "project_1",
      title: "结构局部环境",
      status: "active",
    },
  ]);
  render(<ResearchPage projectId="project_1" />);

  const trigger = await screen.findByRole("button", { name: "研究记录" });
  await user.click(trigger);
  const dialog = await screen.findByRole("dialog", { name: "研究记录" });
  const search = screen.getByRole("searchbox", { name: "搜索研究记录" });
  await waitFor(() => expect(document.activeElement).toBe(search));
  expect(dialog).toHaveTextContent("2 项");
  expect(dialog).toHaveTextContent("已完成");
  expect(dialog).toHaveTextContent("可继续");
  expect(dialog).not.toHaveTextContent("进行中");
  expect(dialog).not.toHaveTextContent("completed");
  await user.type(search, "局部");
  expect(dialog).toHaveTextContent("结构局部环境");
  expect(dialog).not.toHaveTextContent("声子色散分析");
  await user.clear(search);
  await user.type(search, "不存在的标题");
  expect(dialog).toHaveTextContent("没有匹配“不存在的标题”的研究记录。");
  await user.keyboard("{Escape}");
  await waitFor(() =>
    expect(
      screen.queryByRole("dialog", { name: "研究记录" }),
    ).not.toBeInTheDocument(),
  );
  expect(document.activeElement).toBe(trigger);

  await user.click(trigger);
  expect(await screen.findByRole("searchbox", { name: "搜索研究记录" })).toHaveValue("");
  await user.click(screen.getByRole("heading", { name: "研究时间线" }));
  expect(screen.queryByRole("dialog", { name: "研究记录" })).not.toBeInTheDocument();
});

it("links a research-history session to the newest persisted run and Turn", async () => {
  const user = userEvent.setup();
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_history",
      project_id: "project_1",
      title: "结构研究",
      status: "completed",
      messages: [],
    },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_history",
    project_id: "project_1",
    title: "结构研究",
    status: "completed",
    messages: [],
  });
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [],
    analyses: [{
      jobId: "job_history",
      researchSessionId: "session_history",
      researchTurnId: "turn_history",
      status: "completed",
      userQuestion: "分析结构",
      toolIds: [],
      stepCount: 2,
      artifactCount: 1,
      artifactTypes: ["table_json"],
      interpretationCount: 1,
      reportCount: 0,
      recipeCount: 0,
    }],
  });

  render(<ResearchPage projectId="project_1" />);
  await user.click(await screen.findByRole("button", { name: "研究记录" }));
  const link = await screen.findByRole("link", { name: /结构研究/ });
  expect(link).toHaveAttribute(
    "href",
    "/projects/project_1/research/session_history?run=job_history&turn=turn_history",
  );
});

it("provides a single-view mobile switch between conversation and workbench", async () => {
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" />);

  const timeline = await screen.findByRole("tab", { name: "对话" });
  const workbench = screen.getByRole("tab", { name: "工作台" });
  expect(timeline).toHaveAttribute("aria-selected", "true");
  expect(timeline).toHaveAttribute("aria-controls", "research-timeline-panel");
  expect(timeline).toHaveAttribute("tabindex", "0");
  expect(workbench).toHaveAttribute("tabindex", "-1");
  timeline.focus();
  await user.keyboard("{ArrowRight}");
  expect(workbench).toHaveAttribute("aria-selected", "true");
  expect(timeline).toHaveAttribute("aria-selected", "false");
  expect(workbench).toHaveFocus();
  expect(workbench).toHaveAttribute("tabindex", "0");
  expect(screen.getByRole("tabpanel", { name: "工作台" })).toHaveAttribute("id", "research-workbench-panel");
  await user.keyboard("{Home}");
  expect(timeline).toHaveFocus();
  expect(timeline).toHaveAttribute("aria-selected", "true");
});

it("does not present a historical failed run as still running", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{ datasetId: "dataset_a" }],
    analyses: [
      {
        jobId: "job_failed",
        status: "failed",
        userQuestion: "比较失败样本",
        stepCount: 1,
        artifactCount: 0,
      },
    ],
  });
  mocks.getPlannerJob.mockResolvedValue({
    status: "failed",
    analysisPlan: { goal: "比较失败样本", steps: [] },
    planHash: "a".repeat(64),
  });
  mocks.getPlannerJobEvents.mockResolvedValue([]);
  mocks.getPlannerJobArtifacts.mockResolvedValue([]);
  render(<ResearchPage projectId="project_1" runId="job_failed" />);

  expect(await screen.findByText("分析未完成 · 查看过程")).toBeInTheDocument();
  expect(screen.queryByText("研究起点")).not.toBeInTheDocument();
  expect(screen.queryByText("分析中 · 查看过程")).not.toBeInTheDocument();
  expect(
    screen.queryByText("结果生成后会在这里显示。"),
  ).not.toBeInTheDocument();
});

it("renders a persisted artifact while the job is still running", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_running",
      project_id: "project_1",
      title: "RDF 分析",
      status: "active",
      runIds: ["job_running"],
      messages: [],
    },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_running",
    project_id: "project_1",
    title: "RDF 分析",
    status: "active",
    runIds: ["job_running"],
    messages: [],
  });
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{ datasetId: "dataset_a", name: "晶体结构" }],
    analyses: [
      {
        jobId: "job_running",
        researchSessionId: "session_running",
        datasetId: "dataset_a",
        status: "running",
        userQuestion: "查看径向分布",
        stepCount: 2,
        artifactCount: 1,
      },
    ],
  });
  mocks.getPlannerJob.mockResolvedValue({
    status: "running",
    analysisPlan: {
      goal: "查看径向分布",
      datasetId: "dataset_a",
      steps: [
        {
          stepId: "rdf",
          toolId: "structure.rdf",
          inputRefs: [],
          params: {},
          expectedArtifacts: ["plotly_json"],
          dependsOn: [],
        },
      ],
    },
    planHash: "a".repeat(64),
  });
  mocks.getPlannerJobEvents.mockResolvedValue([
    {
      id: "event_ready",
      seq: 4,
      eventType: "artifact.ready",
      status: "success",
      payload: { artifactId: "artifact_rdf" },
    },
    {
      id: "event_second",
      seq: 5,
      eventType: "tool.started",
      status: "running",
      payload: { stepId: "second" },
    },
  ]);
  mocks.getPlannerJobArtifacts.mockResolvedValue([
    {
      artifactId: "artifact_rdf",
      jobId: "job_running",
      type: "plotly_json",
      name: "rdf_plot.json",
      metadata: {
        resultRole: "PRIMARY_FIGURE",
        resultTitle: "径向分布函数（RDF）",
      },
    },
  ]);

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_running"
      runId="job_running"
    />,
  );

  expect(await screen.findByText("1 个科学输出")).toBeInTheDocument();
  expect(screen.getByText("正在分析")).toBeInTheDocument();
  expect(screen.getByTestId("scientific-result-viewer")).toBeInTheDocument();
  expect(
    screen.queryByText("结果生成后会在这里显示。"),
  ).not.toBeInTheDocument();
});

it("reopens a historical run in its persisted research session", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_other",
      project_id: "project_1",
      title: "其他研究",
      status: "active",
      messages: [],
    },
    {
      id: "session_owner",
      project_id: "project_1",
      title: "扩散研究",
      status: "completed",
      messages: [
        {
          id: "pre",
          session_id: "session_owner",
          role: "assistant",
          content: "准备分析",
          created_at: "2026-08-20T00:00:00Z",
          payload: { runId: "job_owned", phase: "pre_run" },
        },
      ],
    },
  ]);
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [],
    analyses: [
      {
        jobId: "job_owned",
        status: "completed",
        userQuestion: "分析扩散行为",
        stepCount: 2,
        artifactCount: 1,
      },
    ],
  });
  render(<ResearchPage projectId="project_1" />);

  const runLink = (
    await screen.findAllByRole("link", { name: /分析扩散行为/ })
  ).find((item) => item.classList.contains("timeline-past-run"));
  expect(runLink).toHaveAttribute(
    "href",
    "/projects/project_1/research/session_owner?run=job_owned",
  );
});

it("uses the normalized run binding even when legacy assistant payloads are absent", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_other",
      project_id: "project_1",
      title: "其他研究",
      status: "active",
      messages: [],
    },
    {
      id: "session_bound",
      project_id: "project_1",
      title: "扩散研究",
      status: "completed",
      runIds: ["job_bound"],
      messages: [],
    },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_bound",
    project_id: "project_1",
    title: "扩散研究",
    status: "completed",
    runIds: ["job_bound"],
    messages: [],
  });
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [],
    analyses: [
      {
        jobId: "job_bound",
        researchSessionId: "session_bound",
        status: "completed",
        userQuestion: "分析扩散行为",
        stepCount: 2,
        artifactCount: 1,
      },
    ],
  });
  render(<ResearchPage projectId="project_1" runId="job_bound" />);

  await waitFor(() =>
    expect(mocks.getResearchSession).toHaveBeenCalledWith("session_bound"),
  );
  expect(
    screen.queryByText("这次历史分析没有关联到可恢复的研究对话"),
  ).not.toBeInTheDocument();
});

it("does not silently attach an orphaned historical run to the first session", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_first",
      project_id: "project_1",
      title: "无关研究",
      status: "active",
      messages: [],
    },
  ]);
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [],
    analyses: [
      {
        jobId: "job_orphan",
        status: "failed",
        userQuestion: "孤立运行",
        stepCount: 1,
        artifactCount: 0,
      },
    ],
  });
  render(<ResearchPage projectId="project_1" runId="job_orphan" />);

  expect(
    await screen.findByText("这次历史分析没有关联到可恢复的研究对话"),
  ).toBeInTheDocument();
  expect(mocks.getResearchSession).not.toHaveBeenCalled();
});

it("retains available historical results when an optional run record fails to load", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_bound",
      project_id: "project_1",
      title: "历史研究",
      status: "completed",
      runIds: ["job_partial_load"],
      messages: [],
    },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_bound",
    project_id: "project_1",
    title: "历史研究",
    status: "completed",
    runIds: ["job_partial_load"],
    messages: [],
  });
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{ datasetId: "dataset_a", name: "材料表" }],
    analyses: [
      {
        jobId: "job_partial_load",
        researchSessionId: "session_bound",
        datasetId: "dataset_a",
        status: "completed",
        userQuestion: "历史结果",
        stepCount: 1,
        artifactCount: 1,
      },
    ],
  });
  mocks.getPlannerJobEvents.mockRejectedValueOnce(
    new Error("events unavailable"),
  );
  mocks.getPlannerJobArtifacts.mockResolvedValue([
    { artifactId: "artifact_1", type: "table_json", name: "结果表" },
  ]);
  render(<ResearchPage projectId="project_1" runId="job_partial_load" />);

  expect(
    await screen.findByText("部分运行记录暂时无法读取；已保留当前可用结果。"),
  ).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "查看数据" })).toHaveAttribute(
    "href",
    "/projects/project_1/data?dataset=dataset_a",
  );
  expect(screen.getByRole("link", { name: "打开分析报告" })).toHaveAttribute(
    "href",
    "/projects/project_1/reports/job_partial_load",
  );
});

it("persists a bounded assistant failure when a real run reaches failed", async () => {
  const user = userEvent.setup();
  mocks.resolveResearchScope.mockResolvedValue({
    status: "READY",
    dataset_id: "dataset_a",
    profile_id: "profile_a",
    dataset_name: "材料表",
  });
  mocks.getPlannerJob.mockResolvedValue({
    status: "failed",
    analysisPlan: { goal: "分析失败", datasetId: "dataset_a", steps: [] },
    planHash: "a".repeat(64),
  });
  render(<ResearchPage projectId="project_1" />);

  await user.type(
    await screen.findByLabelText("询问此项目中的数据"),
    "分析失败",
  );
  await user.click(screen.getByRole("button", { name: "开始分析" }));
  await waitFor(() =>
    expect(mocks.createResearchAssistantProjection).toHaveBeenCalledWith(
      "session_1",
      expect.objectContaining({
        phase: "failed",
        runId: "job_1",
        failureCode: "JOB_FAILED",
      }),
    ),
  );
});

it("shows provider status failure and offers a recoverable retry", async () => {
  const user = userEvent.setup();
  mocks.getPlannerProviderStatus.mockRejectedValueOnce(
    new Error("provider unavailable"),
  );
  render(<ResearchPage projectId="project_1" />);

  expect(
    await screen.findByText("模型状态暂时无法读取；提交时会由服务端再次验证。"),
  ).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重试" }));
  await waitFor(() =>
    expect(mocks.getPlannerProviderStatus).toHaveBeenCalledTimes(2),
  );
  await waitFor(() =>
    expect(
      screen.queryByText("模型状态暂时无法读取；提交时会由服务端再次验证。"),
    ).not.toBeInTheDocument(),
  );
});

it("idempotently reconciles a missing post-run message when reopening a completed run", async () => {
  const owner = {
    id: "session_owner",
    project_id: "project_1",
    title: "扩散研究",
    status: "completed",
    messages: [
      {
        id: "pre",
        session_id: "session_owner",
        role: "assistant",
        content: "准备分析",
        created_at: "2026-08-20T00:00:00Z",
        payload: { runId: "job_owned", phase: "pre_run" },
      },
    ],
  };
  mocks.listResearchSessions.mockResolvedValue([owner]);
  mocks.getResearchSession.mockResolvedValue(owner);
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [],
    analyses: [
      {
        jobId: "job_owned",
        status: "completed",
        datasetId: "dataset_a",
        userQuestion: "分析扩散行为",
        stepCount: 2,
        artifactCount: 1,
      },
    ],
  });
  mocks.getPlannerJobInterpretations.mockResolvedValue({
    interpretations: [
      {
        interpretationId: "interpretation_1",
        completeness: "COMPLETE",
        claims: [],
        globalLimitations: [],
      },
    ],
  });
  render(<ResearchPage projectId="project_1" runId="job_owned" />);

  await waitFor(() =>
    expect(mocks.createResearchAssistantProjection).toHaveBeenCalledWith(
      "session_owner",
      expect.objectContaining({ phase: "post_run", runId: "job_owned" }),
    ),
  );
});

it("projects planner capability failures into user-facing scientific language", async () => {
  const user = userEvent.setup();
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{ datasetId: "dataset_a" }],
    analyses: [],
  });
  mocks.resolveResearchScope.mockResolvedValue({
    status: "READY",
    dataset_id: "dataset_a",
    profile_id: "profile_a",
    dataset_name: "实验 XRD",
  });
  mocks.createPlannerJob.mockResolvedValue({
    ok: false,
    error_code: "CAPABILITY_COVERAGE_INCOMPLETE",
    validation_errors: [
      {
        code: "CAPABILITY_COVERAGE_INCOMPLETE",
        message:
          "Eligible capabilities cannot cover the complete structured Intent independently.",
      },
    ],
  });

  render(<ResearchPage projectId="project_1" />);
  const composer = await screen.findByLabelText("询问此项目中的数据");
  await user.type(composer, "比较实验与理论 XRD");
  await user.click(screen.getByRole("button", { name: "开始分析" }));

  expect(
    await screen.findByText(/当前已验证的分析能力无法完整覆盖这个问题/),
  ).toBeInTheDocument();
  expect(
    screen.queryByText(/Eligible capabilities cannot cover/),
  ).not.toBeInTheDocument();
});

it("turns a local-environment algorithm gap into an actionable clarification", async () => {
  const user = userEvent.setup();
  mocks.resolveResearchScope.mockResolvedValue({
    status: "READY",
    dataset_id: "dataset_a",
    profile_id: "profile_a",
    dataset_name: "晶体结构",
  });
  mocks.createPlannerJob.mockResolvedValue({
    ok: false,
    error_code: "COORDINATION_ALGORITHM_CLARIFICATION_REQUIRED",
    capability_outcome: "NEEDS_CLARIFICATION",
    validation_errors: [
      {
        code: "COORDINATION_ALGORITHM_CLARIFICATION_REQUIRED",
        message:
          "Local-environment analysis requires an explicit coordination source.",
      },
    ],
  });

  render(<ResearchPage projectId="project_1" />);
  const composer = await screen.findByLabelText("询问此项目中的数据");
  await user.type(composer, "查看当前结构的径向分布与局部环境。");
  await user.click(screen.getByRole("button", { name: "开始分析" }));

  expect(
    await screen.findByRole("heading", {
      name: "局部环境分析需要选择配位算法。",
    }),
  ).toBeInTheDocument();
  expect(screen.getByText(/径向分布可以直接计算/)).toBeInTheDocument();
  expect(mocks.createResearchAssistantProjection).toHaveBeenCalledWith(
    "session_1",
    expect.objectContaining({
      phase: "failed",
      failureCode: "COORDINATION_ALGORITHM_CLARIFICATION_REQUIRED",
    }),
  );

  await user.click(screen.getByRole("tab", { name: "工作台" }));
  expect(screen.getByRole("tab", { name: "工作台" })).toHaveAttribute("aria-selected", "true");
  await user.click(screen.getByRole("button", { name: "使用 CrystalNN" }));
  expect(composer).toHaveValue(
    "使用 CrystalNN 计算当前结构的径向分布并分析局部环境",
  );
  expect(screen.getByRole("tab", { name: "对话" })).toHaveAttribute("aria-selected", "true");
  await waitFor(() => expect(composer).toHaveFocus());
  expect(
    screen.queryByRole("heading", { name: "局部环境分析需要选择配位算法。" }),
  ).not.toBeInTheDocument();
});

it("hides legacy machine-plan and interpretation leakage from the conversation timeline", () => {
  expect(
    displayResearchMessage({
      id: "legacy",
      session_id: "session",
      role: "assistant",
      created_at: "2026-08-19T00:00:00Z",
      content:
        "我会使用数据完成分析。\n\n分析方案：\n1. Satisfy the validated structured AnalysisIntent with an eligible registered capability.\n\n分析已经完成。 dataset reported count: 1. 2 artifact(s) have no approved structured evidence projector. 可以在右侧查看科学结果、依据与来源。",
    }),
  ).toBe(
    "本次分析将以数据集“数据”为范围。\n\n分析方案：\n1. 执行已验证的科学分析步骤。\n\n分析已经完成。\n\n可以在右侧查看科学结果、依据与来源。",
  );
});

it("projects process state from persisted tool events instead of event counts", () => {
  expect(
    runProcessStepState("step-a", "running", new Set(), new Set(["step-a"])),
  ).toBe("active");
  expect(
    runProcessStepState(
      "step-a",
      "running",
      new Set(["step-a"]),
      new Set(["step-a"]),
    ),
  ).toBe("complete");
  expect(
    runProcessStepState(
      "step-b",
      "running",
      new Set(["step-a"]),
      new Set(["step-a"]),
    ),
  ).toBe("pending");
  expect(
    runProcessStepState("step-b", "partial", new Set(["step-a"]), new Set()),
  ).toBe("pending");
  expect(runProcessStepState("step-b", "complete", new Set(), new Set())).toBe(
    "complete",
  );
});

it("deduplicates overlapping event pages and artifact refreshes by stable identity", () => {
  expect(
    mergeJobEvents(
      [{ id: "event_2", seq: 2, eventType: "tool.started" }],
      [
        { id: "event_1", seq: 1, eventType: "job.created" },
        { id: "event_2", seq: 2, eventType: "tool.started", status: "success" },
      ],
    ),
  ).toEqual([
    expect.objectContaining({ id: "event_1", seq: 1 }),
    expect.objectContaining({ id: "event_2", seq: 2, status: "success" }),
  ]);
  expect(
    mergeArtifacts(
      [
        { artifactId: "artifact_b", type: "table_json" },
        { artifactId: "artifact_a", type: "plotly_json" },
      ],
      [{ artifactId: "artifact_b", type: "table_json", sizeBytes: 42 }],
    ),
  ).toEqual([
    expect.objectContaining({ artifactId: "artifact_a" }),
    expect.objectContaining({ artifactId: "artifact_b", sizeBytes: 42 }),
  ]);
});

it("does not expose machine plan language in the research timeline", () => {
  expect(
    userFacingPlanStep(
      "Satisfy the validated structured AnalysisIntent with an eligible registered capability.",
      "Selected from exact Intent, DataProfile, Registry, and parameter-binding facts.",
    ),
  ).toEqual({
    purpose: "整理当前数据中的科学信息",
    reason: "已根据当前数据和科学能力确定本次步骤。",
  });
  expect(
    userFacingPlanStep(
      "生成数值相关图",
      "比较当前数据中的 formation_energy 与 band_gap。",
    ),
  ).toEqual({
    purpose: "生成数值相关图",
    reason: "比较当前数据中的 formation_energy 与 band_gap。",
  });
  expect(
    userFacingPlanStep(
      "Satisfy the validated structured AnalysisIntent with an eligible registered capability.",
      "",
      0,
      "structure.experimental_xrd_comparison",
    ),
  ).toEqual({
    purpose: "比较实验峰与理论峰的位置和强度",
  });
  expect(userFacingPlanStep("", "", 0, "phonon.band_dos")).toEqual({
    purpose: "组合声子色散与态密度",
  });
  expect(userFacingPlanStep("", "", 0, "future.scientific_tool")).toEqual({
    purpose: "科学分析步骤 1",
  });
});

it("projects user-facing findings only from persisted scientific evidence", () => {
  const evidence = (items: Array<[string, string]>) =>
    ({
      interpretationId: "interpretation_1",
      bundleId: "bundle_1",
      bundleHash: "a".repeat(64),
      evidenceItems: items.map(([semanticRole, displayValue], index) => ({
        evidenceItemId: `evidence_${index}`,
        semanticRole,
        displayValue,
        sourceArtifactId: "artifact_1",
      })),
      sourceArtifactIds: ["artifact_1"],
      bundleWarnings: [],
      bundleLimitations: [],
    }) as unknown as InterpretationEvidenceResponse;
  const datasetNarrative = groundedEvidenceNarrative(
    evidence([
      ["dataset.sample_count", "576"],
      ["dataset.property_count", "0"],
      ["composition.valid_count", "576"],
      ["composition.unique_formula_count", "576"],
    ]),
  );
  expect(datasetNarrative).toEqual({
    finding:
      "当前材料数据包含 576 个样本，其中 576 个样本具有可解析化学式，共覆盖 576 个唯一化学式。",
    limitation:
      "材料性质字段数量为 0；数据质量概览不替代针对具体性质或结构的科学分析。",
  });
  const trajectoryNarrative = groundedEvidenceNarrative(
    evidence([
      ["trajectory.msd.last_lag", "1.05 picosecond"],
      ["trajectory.msd.last_total", "2.01431 angstrom^2"],
      ["trajectory.rdf.included_frames", "15"],
      ["trajectory.diffusion.status", "INSUFFICIENT_DURATION"],
    ]),
  );
  expect(trajectoryNarrative).toEqual({
    finding:
      "在 1.05 ps 的末端时滞处，总 MSD 为 2.01431 Å^2；RDF 统计使用 15 帧。",
    limitation:
      "当前轨迹时长不足以形成稳健扩散系数结论；应延长采样并检查线性扩散区间。",
  });
  const coordinationEvidence = evidence([
    ["coordination.algorithm", "pymatgen.crystalnn"],
    ["coordination.total_sites", "56"],
    ["coordination.successful_sites", "56"],
    ["coordination.coverage", "1"],
    ["coordination.value_range", "3.78746 to 6"],
    ["coordination.distance_range", "1.88862 to 3.63475 angstrom"],
  ]);
  coordinationEvidence.evidenceItems[0].warnings = [
    "CRYSTALNN_OXIDATION_STATES_NOT_DECLARED",
    "CRYSTALNN_RADIUS_FALLBACK_USED",
  ];
  expect(groundedEvidenceNarrative(coordinationEvidence)).toEqual({
    finding:
      "CrystalNN 在 56/56 个位点完成配位分析，覆盖率为 100%；配位值范围为 3.78746 至 6，邻居距离范围为 1.88862 至 3.63475 Å。",
    limitation:
      "当前输入未声明氧化态；部分判断使用了半径回退规则。配位结果依赖所选算法、参数与当前结构，不作为确定化学键结论。",
  });
  expect(
    groundedEvidenceNarrative(
      evidence([
        ["local_environment.source_algorithm", "pymatgen.voronoinn"],
        ["local_environment.evaluated_sites", "8"],
        ["local_environment.classified_sites", "6"],
        ["local_environment.ambiguous_sites", "1"],
        ["local_environment.unclassified_sites", "1"],
        ["local_environment.coverage", "0.75"],
      ]),
    ),
  ).toEqual({
    finding:
      "VoronoiNN 局部环境分析评估了 8 个位点，其中 6 个完成分类、1 个存在歧义、1 个未分类；覆盖率为 75%。",
    limitation:
      "局部环境分类来自所选配位算法与几何参考匹配，不等同于确定的化学键或价态判定。",
  });
});
