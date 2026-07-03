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
      inputRefs: [{ refType: "normalized_object", ref: "ml_table", objectType: "DataFrame" }],
      params: { targetColumn: "y_true", predictionColumn: "y_pred" },
      output: { artifactTypes: ["metrics_json"] }
    }
  ],
  expectedArtifacts: [{ name: "metrics.json", type: "metrics_json", fromStepId: "llm_step_1" }]
};

const createdJob = {
  ok: true,
  job_id: "job_1",
  plan_id: "plan_1",
  plan_hash: "hash_1",
  validation_errors: [],
  plan,
  plan_source: "llm",
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
  artifactCount: 1,
  eventCount: 4,
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
  { id: "evt_1", jobId: "job_1", seq: 1, eventType: "job.created", status: "info", message: "Created.", payload: {}, createdAt: "2026-07-03T00:00:00Z" },
  {
    id: "evt_2",
    jobId: "job_1",
    seq: 2,
    eventType: "plan.loaded",
    status: "success",
    message: "Loaded persisted AnalysisPlan.",
    payload: { planId: "plan_1", planHash: "hash_1", planSource: "llm" },
    createdAt: "2026-07-03T00:00:01Z"
  },
  { id: "evt_3", jobId: "job_1", seq: 3, eventType: "tool.completed", status: "success", message: "Completed ml.basic_metrics.", payload: {}, createdAt: "2026-07-03T00:00:02Z" },
  { id: "evt_4", jobId: "job_1", seq: 4, eventType: "job.completed", status: "success", message: "Job completed.", payload: {}, createdAt: "2026-07-03T00:00:03Z" }
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
  summary: "Job completed with 1 ToolCall(s) and 1 Artifact(s).",
  toolCallCount: 1,
  artifactCount: 1,
  artifacts
};

let fetchMock: ReturnType<typeof vi.fn>;
let eventSources: MockEventSource[];

beforeEach(() => {
  eventSources = [];
  fetchMock = vi.fn(mockPlannerFetch);
  vi.stubGlobal("fetch", fetchMock);
  vi.stubGlobal("EventSource", MockEventSource);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("PlannerWorkbench", () => {
  it("renders the planner job form and empty planner state", () => {
    render(<PlannerWorkbench />);

    expect(screen.getByTestId("planner-form")).not.toBeNull();
    expect(screen.getByLabelText("Project ID")).not.toBeNull();
    expect(screen.getByTestId("data-context-selector")).not.toBeNull();
    expect(screen.getByLabelText("Dataset selector")).not.toBeNull();
    expect(screen.getByLabelText("Profile selector")).not.toBeNull();
    expect(screen.getByLabelText("Dataset ID")).not.toBeNull();
    expect(screen.getByLabelText("Analysis intent")).not.toBeNull();
    expect(screen.getByText("Validated Plan Preview")).not.toBeNull();
    expect(screen.getByText("Report / Recipe Summary")).not.toBeNull();
    expect(screen.getAllByText("Not available yet").length).toBeGreaterThan(0);
  });

  it("submits a valid request and displays persisted plan provenance", async () => {
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await user.click(screen.getByRole("button", { name: "Create and enqueue" }));

    expect((await screen.findAllByText("job_1")).length).toBeGreaterThan(0);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/planner/jobs",
      expect.objectContaining({
        method: "POST",
        body: expect.stringContaining("\"datasetId\":\"dataset_demo\"")
      })
    );
    expect(screen.getAllByText("plan_1").length).toBeGreaterThan(0);
    expect(screen.getAllByText("hash_1").length).toBeGreaterThan(0);
    expect(screen.getAllByText("llm_step_1").length).toBeGreaterThan(0);
    expect(screen.getAllByText("ml.basic_metrics").length).toBeGreaterThan(0);
    await waitFor(() => expect(eventSources[0]?.url).toBe("http://localhost:8000/planner/jobs/job_1/events/stream?after_seq=4"));
    expect(screen.getByText("SSE/EventSource")).not.toBeNull();
    eventSources[0].emit("artifact.ready", {
      id: "evt_5",
      jobId: "job_1",
      seq: 5,
      eventType: "artifact.ready",
      status: "success",
      message: "Artifact ready from SSE.",
      payload: { planId: "plan_1", planHash: "hash_1" },
      createdAt: "2026-07-03T00:00:04Z"
    });
    await screen.findByText("artifact.ready");
    expect(screen.getByText("Loaded from persisted AnalysisPlan")).not.toBeNull();
    expect(screen.getByText("Executed through Tool Registry + Adapter")).not.toBeNull();
    expect(screen.getByText("No deterministic fallback used")).not.toBeNull();
    expect(within(screen.getByTestId("job-timeline")).getByText("plan.loaded")).not.toBeNull();
    expect(within(screen.getByTestId("toolcalls-panel")).getByText("llm_step_1")).not.toBeNull();
    expect(within(screen.getByTestId("toolcalls-panel")).getByText("plan_1")).not.toBeNull();
    expect(within(screen.getByTestId("artifacts-panel")).getByText("metrics.json")).not.toBeNull();
    expect(within(screen.getByTestId("report-recipe-panel")).getByText("Report summary")).not.toBeNull();
    expect(within(screen.getByTestId("report-recipe-panel")).getByText("recipe.json")).not.toBeNull();
    expect(within(screen.getByTestId("report-recipe-panel")).getByText("report.md")).not.toBeNull();
    expect(within(screen.getByTestId("report-recipe-panel")).getByText("Job completed with 1 ToolCall(s) and 1 Artifact(s).")).not.toBeNull();
    expect(within(screen.getByTestId("report-recipe-panel")).getByText(/persisted AnalysisPlan/)).not.toBeNull();
  });

  it("uses API-backed dataset/profile selectors while preserving manual ID fallback", async () => {
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await screen.findByText("Demo metrics dataset (profile_ready)");
    await user.selectOptions(screen.getByLabelText("Dataset selector"), "dataset_api");

    await waitFor(() => {
      expect((screen.getByLabelText("Dataset ID") as HTMLInputElement).value).toBe("dataset_api");
      expect((screen.getByLabelText("Profile ID") as HTMLInputElement).value).toBe("profile_api");
    });
    expect(screen.getByText("Dataset/profile loaded from API")).not.toBeNull();

    await user.selectOptions(screen.getByLabelText("Dataset selector"), "__manual");
    expect(screen.getByText("Manual dataset/profile ID fallback is active")).not.toBeNull();
  });

  it("shows validation failure semantics and does not poll job state", async () => {
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === "POST" && url.endsWith("/planner/jobs")) {
        return jsonResponse({
          ok: false,
          job_id: null,
          plan_id: null,
          plan_hash: null,
          validation_errors: [{ code: "UNKNOWN_TOOL", message: "Unknown tool", detail: { toolId: "bad.tool" } }],
          plan: { steps: [] },
          enqueued: false,
          executed: false
        });
      }
      return mockPlannerFetch(input, init);
    });
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await user.click(screen.getByRole("button", { name: "Create and enqueue" }));

    await screen.findByText("Plan validation failed");
    expect(screen.getByText("No AnalysisPlan was saved")).not.toBeNull();
    expect(screen.getByText("No Job was created")).not.toBeNull();
    expect(screen.getByText("Nothing was enqueued")).not.toBeNull();
    expect(screen.getByText("Please fix the request and try again")).not.toBeNull();
    expect(screen.getByText("UNKNOWN_TOOL")).not.toBeNull();
    expect(fetchMock).not.toHaveBeenCalledWith(expect.stringContaining("/planner/jobs/job_1"), expect.anything());
    expect(eventSources).toHaveLength(0);
  });

  it("shows loading and API error states", async () => {
    let resolvePost: (value: Response) => void = () => {};
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === "POST" && url.endsWith("/planner/jobs")) {
        return (
        new Promise<Response>((resolve) => {
          resolvePost = resolve;
        })
        );
      }
      return mockPlannerFetch(input, init);
    });
    const user = userEvent.setup();
    render(<PlannerWorkbench />);

    await user.click(screen.getByRole("button", { name: "Create and enqueue" }));
    expect(screen.getByRole("button", { name: "Submitting" })).not.toBeNull();

    resolvePost(new Response(JSON.stringify({ detail: "Planner unavailable" }), { status: 503 }));
    await screen.findByText("Planner unavailable");
  });
});

function mockPlannerFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const url = String(input);
  if (url.endsWith("/datasets")) {
    return jsonResponse([{ id: "dataset_api", projectId: "project_local", name: "Demo metrics dataset", status: "profile_ready" }]);
  }
  if (url.endsWith("/datasets/dataset_api/profile")) {
    return jsonResponse({ profileId: "profile_api", datasetId: "dataset_api", datasetType: "ml", version: "0.1", createdAt: "2026-07-03T00:00:00Z" });
  }
  if (init?.method === "POST" && url.endsWith("/planner/jobs")) {
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
  if (url.endsWith("/planner/analysis-plans/plan_1")) {
    return jsonResponse({ planId: "plan_1", planHash: "hash_1", validationStatus: "validated", analysisPlan: plan });
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
