import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { PlannerWorkbench } from "./PlannerWorkbench";

const plan = {
  schemaVersion: "0.1",
  goal: "compute metrics",
  datasetId: "dataset_demo",
  profileId: "profile_demo",
  toolRegistryVersion: "0.1.0",
  steps: [
    {
      stepId: "llm_step_1",
      toolId: "ml.basic_metrics",
      purpose: "Compute basic metrics",
      reason: "Use y_true and y_pred.",
      inputRefs: [{ refType: "normalized_object", ref: "ml_table", objectType: "DataFrame" }],
      params: { targetColumn: "y_true", predictionColumn: "y_pred" },
      output: { artifactTypes: ["metrics_json"] }
    }
  ],
  expectedArtifacts: [{ name: "metrics.json", type: "metrics_json", fromStepId: "llm_step_1" }]
};

const demoProfile = {
  profileId: "profile_demo",
  datasetId: "dataset_demo",
  datasetType: "ml",
  version: "0.1",
  createdAt: "2026-07-04T00:00:00Z",
  tableSummary: {
    nRows: 5,
    nColumns: 3,
    columns: [
      { name: "formula", dtype: "string", inferredRole: "formula" },
      { name: "y_true", dtype: "number", inferredRole: "target" },
      { name: "y_pred", dtype: "number", inferredRole: "prediction" }
    ]
  },
  structureSummary: { nStructures: 0, elements: [], formulaStats: { total: 5, uniqueCount: 5 } }
};

const createdJob = {
  ok: true,
  job_id: "job_1",
  plan_id: "plan_1",
  plan_hash: "hash_1",
  validation_errors: [],
  plan,
  plan_source: "llm",
  planner_provider: "mock",
  enqueued: true,
  executed: false
};

const jobDetail = {
  jobId: "job_1",
  projectId: "project_local",
  datasetId: "dataset_demo",
  status: "completed",
  planId: "plan_1",
  planHash: "hash_1",
  planSource: "llm",
  analysisPlan: plan,
  validationStatus: "validated",
  toolCallCount: 1,
  artifactCount: 3,
  eventCount: 8,
  provenance: {
    planId: "plan_1",
    planHash: "hash_1",
    loadedFrom: "persisted_analysis_plan",
    binding: "jobs.plan_id -> analysis_plans.id",
    toolPath: "Tool Registry + Adapter",
    fallbackUsed: false
  }
};

const events = [
  { id: "evt_1", jobId: "job_1", seq: 1, eventType: "plan.generated", status: "success", message: "Generated plan.", payload: {}, createdAt: "2026-07-04T00:00:00Z" },
  { id: "evt_2", jobId: "job_1", seq: 2, eventType: "plan.persisted", status: "success", message: "Persisted plan.", payload: { planId: "plan_1", planHash: "hash_1" }, createdAt: "2026-07-04T00:00:01Z" },
  { id: "evt_3", jobId: "job_1", seq: 3, eventType: "job.queued", status: "success", message: "Job queued.", payload: {}, createdAt: "2026-07-04T00:00:01Z" },
  { id: "evt_4", jobId: "job_1", seq: 4, eventType: "plan.loaded", status: "success", message: "Loaded persisted AnalysisPlan.", payload: { planId: "plan_1", planHash: "hash_1" }, createdAt: "2026-07-04T00:00:02Z" },
  { id: "evt_5", jobId: "job_1", seq: 5, eventType: "data.loaded", status: "success", message: "Loaded dataset objects.", payload: {}, createdAt: "2026-07-04T00:00:02Z" },
  { id: "evt_6", jobId: "job_1", seq: 6, eventType: "tool.started", status: "running", message: "Tool started.", payload: {}, createdAt: "2026-07-04T00:00:02Z" },
  { id: "evt_7", jobId: "job_1", seq: 7, eventType: "tool.completed", status: "success", message: "Tool completed.", payload: {}, createdAt: "2026-07-04T00:00:03Z" },
  { id: "evt_8", jobId: "job_1", seq: 8, eventType: "job.completed", status: "success", message: "Job completed.", payload: {}, createdAt: "2026-07-04T00:00:04Z" }
];

const toolCalls = [
  {
    id: "call_1",
    jobId: "job_1",
    stepId: "llm_step_1",
    toolId: "ml.basic_metrics",
    status: "completed",
    planId: "plan_1",
    planHash: "hash_1",
    inputSummary: "Params: predictionColumn, targetColumn",
    outputSummary: "1 artifact(s)"
  }
];

const artifacts = [
  {
    artifactId: "artifact_metrics",
    id: "artifact_metrics",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "metrics_json",
    name: "metrics.json",
    storageKey: "projects/project_local/jobs/job_1/tool_calls/call_1/metrics.json",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1"
  },
  {
    artifactId: "artifact_recipe",
    id: "artifact_recipe",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "recipe_json",
    name: "recipe.json",
    storageKey: "projects/project_local/jobs/job_1/recipe.json",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1"
  },
  {
    artifactId: "artifact_report",
    id: "artifact_report",
    jobId: "job_1",
    toolCallId: "call_1",
    type: "report_md",
    name: "report.md",
    storageKey: "projects/project_local/jobs/job_1/report.md",
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_1"
  }
];

const result = {
  jobId: "job_1",
  status: "completed",
  planId: "plan_1",
  planHash: "hash_1",
  summary: "Job completed with 1 ToolCall(s) and 3 Artifact(s).",
  toolCallCount: 1,
  artifactCount: 3,
  artifacts
};

let fetchMock: ReturnType<typeof vi.fn>;
let eventSources: MockEventSource[];
let savedSecrets: Array<Record<string, unknown>>;

beforeEach(() => {
  eventSources = [];
  savedSecrets = [];
  window.localStorage.clear();
  window.sessionStorage.clear();
  fetchMock = vi.fn(mockPlannerFetch);
  vi.stubGlobal("fetch", fetchMock);
  vi.stubGlobal("EventSource", MockEventSource);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("Phase 9C PlannerWorkbench", () => {
  it("renders the strict top/left/main-tab layout in Chinese by default", async () => {
    render(<PlannerWorkbench />);

    expect(await screen.findByTestId("global-context-bar")).not.toBeNull();
    expect(screen.getByTestId("data-context-viewer")).not.toBeNull();
    expect(screen.getByTestId("main-workspace")).not.toBeNull();
    expect(screen.getByRole("button", { name: /当前数据集/ })).not.toBeNull();
    expect(screen.getByRole("button", { name: /模型状态/ })).not.toBeNull();
    expect(screen.getByRole("button", { name: "Agent 过程" })).not.toBeNull();
    expect(screen.getByRole("button", { name: "对话与 Plan" })).not.toBeNull();
    expect(screen.getByRole("button", { name: "结果与导出" })).not.toBeNull();
    expect(screen.queryByText("Not available yet")).toBeNull();
    expect(screen.queryByTestId("agent-process-tab")).toBeNull();
    expect(screen.queryByTestId("results-export-tab")).toBeNull();
    expect(screen.getByTestId("conversation-plan-tab")).not.toBeNull();
  });

  it("opens dataset dialog from the top bar, loads demo data, and updates the left data viewer", async () => {
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await user.click(screen.getByRole("button", { name: /当前数据集/ }));
    expect(screen.getByRole("dialog", { name: "数据集与 Profile" })).not.toBeNull();
    await user.click(screen.getByRole("button", { name: "加载演示数据" }));

    await waitFor(() => {
      expect(screen.queryByRole("dialog", { name: "数据集与 Profile" })).toBeNull();
      expect(within(screen.getByTestId("data-context-viewer")).getByText("dataset_demo")).not.toBeNull();
      expect(within(screen.getByTestId("data-context-viewer")).getByText("profile_demo")).not.toBeNull();
    });
    expect(within(screen.getByTestId("data-context-viewer")).getAllByText("表格数据").length).toBeGreaterThan(0);
    expect(within(screen.getByTestId("data-context-viewer")).getByText("y_true")).not.toBeNull();
  });

  it("opens model dialog from the top bar, saves a secret without browser storage leakage, and tests the provider", async () => {
    const user = userEvent.setup();
    const apiKey = "sk-ui-secret-value";
    render(<PlannerWorkbench />);

    await user.click(screen.getByRole("button", { name: /模型状态/ }));
    expect(screen.getByRole("dialog", { name: "模型与 API 配置" })).not.toBeNull();
    await user.selectOptions(screen.getByLabelText("规划器模式"), "openai_compatible");
    await user.clear(screen.getByLabelText("API Key"));
    await user.type(screen.getByLabelText("API Key"), apiKey);
    await user.click(screen.getByRole("button", { name: "保存密钥" }));

    await waitFor(() => expect((screen.getByLabelText("API Key") as HTMLInputElement).value).toBe(""));
    expect(document.body.textContent).not.toContain(apiKey);
    expect(JSON.stringify(window.localStorage)).not.toContain(apiKey);
    expect(JSON.stringify(window.sessionStorage)).not.toContain(apiKey);
    expect(await screen.findByText(/Demo LLM Key/)).not.toBeNull();

    await user.click(screen.getByRole("button", { name: "测试模型连接" }));
    expect(await screen.findByText("模型连接成功，并成功返回可解析的 AnalysisPlan。")).not.toBeNull();
  });

  it("keeps main tabs mutually exclusive and routes job evidence into Agent process and Results/export", async () => {
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());

    expect(await screen.findByText("基础指标计算")).not.toBeNull();
    expect(screen.getByText("plan_1")).not.toBeNull();
    expect(screen.getByText("hash_1")).not.toBeNull();
    await waitFor(() => expect(eventSources[0]?.url).toBe("http://localhost:8000/planner/jobs/job_1/events/stream?after_seq=8"));

    await user.click(screen.getByRole("button", { name: "Agent 过程" }));
    expect(screen.getByTestId("agent-process-tab")).not.toBeNull();
    expect(screen.queryByTestId("conversation-plan-tab")).toBeNull();
    expect(screen.queryByTestId("results-export-tab")).toBeNull();
    expect(within(screen.getByTestId("agent-process-tab")).getByText("Worker 已加载分析计划")).not.toBeNull();
    expect(within(screen.getByTestId("agent-process-tab")).getByText("数据对象已加载")).not.toBeNull();
    expect(within(screen.getByTestId("agent-process-tab")).getByText("工具执行完成")).not.toBeNull();
    expect(within(screen.getByTestId("agent-process-tab")).getByText("任务完成")).not.toBeNull();
    expect(screen.getByText("Loaded from persisted AnalysisPlan")).not.toBeNull();
    expect(screen.getByText("Executed through Tool Registry + Adapter")).not.toBeNull();
    expect(screen.getByText("No deterministic fallback used")).not.toBeNull();

    await user.click(screen.getByRole("button", { name: "结果与导出" }));
    expect(screen.getByTestId("results-export-tab")).not.toBeNull();
    expect(screen.queryByTestId("agent-process-tab")).toBeNull();
    expect(screen.queryByTestId("conversation-plan-tab")).toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).getByText("Report / Recipe Summary")).not.toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).getByText("3D 材料图")).not.toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).getByText("Metrics")).not.toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).getByText("Table / Numeric Summary")).not.toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).getByText("Artifact Gallery")).not.toBeNull();
    expect(within(screen.getByTestId("results-export-tab")).getAllByText("metrics.json").length).toBeGreaterThan(0);
    expect(within(screen.getByTestId("results-export-tab")).getAllByText("recipe.json").length).toBeGreaterThan(0);
    expect(within(screen.getByTestId("results-export-tab")).getByText("ml.basic_metrics")).not.toBeNull();
  });

  it("shows the required result empty state when no chunk is selected", async () => {
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await user.click(screen.getByRole("button", { name: "结果与导出" }));
    expect(screen.getByTestId("results-export-tab")).not.toBeNull();
    expect(screen.getAllByText("请选择一个分析步骤或结果 chunk").length).toBeGreaterThan(0);
  });

  it("explains validation failure without creating job, plan, enqueue, polling, or SSE", async () => {
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === "POST" && url.endsWith("/planner/jobs")) {
        return jsonResponse({
          ok: false,
          job_id: null,
          plan_id: null,
          plan_hash: null,
          validation_errors: [{ code: "UNKNOWN_TOOL", message: "Unknown tool", detail: { toolId: "bad.tool" } }],
          enqueued: false,
          executed: false
        });
      }
      return mockPlannerFetch(input, init);
    });
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await loadDemoFromTopBar(user);
    await user.click(primaryRunButton());

    expect((await screen.findAllByText("Plan validation failed")).length).toBeGreaterThan(0);
    expect(screen.getByText("No AnalysisPlan was saved")).not.toBeNull();
    expect(screen.getByText("No Job was created")).not.toBeNull();
    expect(screen.getByText("Nothing was enqueued")).not.toBeNull();
    expect(screen.getAllByText("UNKNOWN_TOOL").length).toBeGreaterThan(0);
    expect(fetchMock).not.toHaveBeenCalledWith(expect.stringContaining("/planner/jobs/job_1"), expect.anything());
    expect(eventSources).toHaveLength(0);
  });
});

async function loadDemoFromTopBar(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole("button", { name: /当前数据集/ }));
  await user.click(screen.getByRole("button", { name: "加载演示数据" }));
  await waitFor(() => expect(screen.queryByRole("dialog", { name: "数据集与 Profile" })).toBeNull());
}

function primaryRunButton() {
  return within(screen.getByTestId("planner-form")).getByRole("button", { name: "创建并运行" });
}

function mockPlannerFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const url = String(input);
  const method = init?.method || "GET";
  if (url.endsWith("/health/runtime")) {
    return jsonResponse({
      api: { status: "ok" },
      database: { status: "ok", backend: "sqlite" },
      redis: { status: "unknown", reason: "not configured" },
      artifactStorage: { status: "ok", backend: "local" },
      worker: { status: "ok", backend: "local" },
      llmProvider: { status: "ok", provider: "mock", model: "mock" }
    });
  }
  if (url.endsWith("/planner/providers")) {
    return jsonResponse({
      providers: [
        { id: "mock", label: "Mock Planner", provider: "mock", requiresSecret: false },
        { id: "deepseek", label: "DeepSeek", provider: "openai_compatible", baseUrl: "https://api.deepseek.com/v1", defaultModel: "deepseek-chat", requiresSecret: true }
      ]
    });
  }
  if (url.endsWith("/planner/providers/status")) {
    return jsonResponse({ ok: true, provider: "mock", model: "mock", status: "ready", message: "Mock Planner is active." });
  }
  if (method === "POST" && url.endsWith("/planner/providers/test")) {
    const body = JSON.parse(String(init?.body || "{}"));
    expect(JSON.stringify(body)).not.toContain("sk-ui-secret-value");
    return jsonResponse({ ok: true, provider: body.provider, model: body.model || "mock", latencyMs: 9, validated: true, message: "模型连接成功，并成功返回可解析的 AnalysisPlan。", redacted: true });
  }
  if (url.endsWith("/me/secrets") && method === "GET") {
    return jsonResponse(savedSecrets);
  }
  if (url.endsWith("/me/secrets") && method === "POST") {
    const body = JSON.parse(String(init?.body || "{}"));
    const secret = {
      id: "secret_1",
      secret_id: "secret_1",
      alias: body.alias,
      provider: body.provider,
      createdAt: "2026-07-04T00:00:00Z",
      status: "active",
      maskedPreview: "••••••••"
    };
    savedSecrets = [secret];
    return jsonResponse(secret);
  }
  if (url.includes("/me/secrets/") && method === "DELETE") {
    savedSecrets = [];
    return jsonResponse(true);
  }
  if (url.endsWith("/datasets")) {
    return jsonResponse([{ id: "dataset_api", datasetId: "dataset_api", projectId: "project_local", name: "Demo metrics dataset", status: "profile_ready", profileId: "profile_api" }]);
  }
  if (method === "POST" && url.endsWith("/datasets/demo")) {
    return jsonResponse({ id: "dataset_demo", datasetId: "dataset_demo", projectId: "project_local", name: "Demo metrics dataset", status: "profile_ready", demo: true, profileId: "profile_demo", profile: demoProfile });
  }
  if (url.endsWith("/datasets/dataset_demo/profile") || url.endsWith("/datasets/dataset_api/profile")) {
    return jsonResponse(url.includes("dataset_api") ? { ...demoProfile, datasetId: "dataset_api", profileId: "profile_api" } : demoProfile);
  }
  if (method === "POST" && url.endsWith("/planner/jobs")) {
    const body = JSON.parse(String(init?.body || "{}"));
    expect(JSON.stringify(body)).not.toContain("sk-ui-secret-value");
    return jsonResponse(createdJob);
  }
  if (url.endsWith("/planner/jobs/job_1")) {
    return jsonResponse(jobDetail);
  }
  if (url.endsWith("/planner/jobs/job_1/events")) {
    return jsonResponse(events);
  }
  if (url.endsWith("/planner/jobs/job_1/tool-calls")) {
    return jsonResponse(toolCalls);
  }
  if (url.endsWith("/planner/jobs/job_1/artifacts")) {
    return jsonResponse(artifacts);
  }
  if (url.endsWith("/planner/jobs/job_1/result")) {
    return jsonResponse(result);
  }
  return jsonResponse({ detail: "not found" }, 404);
}

function jsonResponse(body: unknown, status = 200): Promise<Response> {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" }
    })
  );
}

class MockEventSource {
  url: string;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: (() => void) | null = null;
  listeners = new Map<string, Array<(event: MessageEvent) => void>>();

  constructor(url: string) {
    this.url = url;
    eventSources.push(this);
  }

  addEventListener(type: string, listener: EventListener) {
    const current = this.listeners.get(type) || [];
    current.push(listener as (event: MessageEvent) => void);
    this.listeners.set(type, current);
  }

  close() {
    // no-op for tests
  }

  emit(type: string, payload: unknown) {
    const message = new MessageEvent(type, { data: JSON.stringify(payload) });
    this.onmessage?.(message);
    (this.listeners.get(type) || []).forEach((listener) => listener(message));
  }
}
