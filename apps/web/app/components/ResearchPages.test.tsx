import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

import {
  Agent2ReadError,
  type Agent2ResearchTurnResult,
  type Agent2ContextManifest,
  type Agent2TurnDetail,
} from "../lib/agent2-research-api";
import type { InterpretationEvidenceResponse, ProjectHistory } from "../lib/planner-api";
import {
  CONTEXT_MANIFEST_RENDER_WINDOW,
  contextManifestRenderItems,
  evidenceProvenanceSummary,
} from "./ResearchPages";

const mocks = vi.hoisted(() => ({
  routerPush: vi.fn(),
  createResearchMessage: vi.fn(),
  createResearchAssistantProjection: vi.fn(),
  createResearchSession: vi.fn(),
  getDataset: vi.fn(),
  getDatasetProfile: vi.fn(),
  getDatasetSourceResources: vi.fn(),
  admitDatasetResource: vi.fn(),
  promoteDatasetTable: vi.fn(),
  getProjectHistory: vi.fn(),
  getResearchSession: vi.fn(),
  listResearchSessions: vi.fn(),
  bulkUpdateResearchSessions: vi.fn(),
  updateResearchSession: vi.fn(),
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
  unpinAgent2Object: vi.fn(),
  unpinAgent2Result: vi.fn(),
  getAgent2ExecutionProgress: vi.fn(),
  cancelAgent2Execution: vi.fn(),
  getAgent2ContextManifest: vi.fn(),
  listAgent2ResearchTurns: vi.fn(),
  dispatchAgent2ResearchTurn: vi.fn(),
  createAgent2ResearchTurn: vi.fn(),
  getAgent2ResearchTurn: vi.fn(),
  getAgent2ResearchTurnResult: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mocks.routerPush,
    replace: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

vi.mock("../lib/product-api", () => ({
  createResearchMessage: mocks.createResearchMessage,
  createResearchAssistantProjection: mocks.createResearchAssistantProjection,
  createResearchSession: mocks.createResearchSession,
  getDataset: mocks.getDataset,
  getDatasetProfile: mocks.getDatasetProfile,
  getResearchSession: mocks.getResearchSession,
  listResearchSessions: mocks.listResearchSessions,
  bulkUpdateResearchSessions: mocks.bulkUpdateResearchSessions,
  updateResearchSession: mocks.updateResearchSession,
  resolveResearchScope: mocks.resolveResearchScope,
}));

vi.mock("../lib/planner-api", () => ({
  createPlannerJob: mocks.createPlannerJob,
  createPlannerJobInterpretation: mocks.createPlannerJobInterpretation,
  getDataset: mocks.getDataset,
  getDatasetProfile: mocks.getDatasetProfile,
  getDatasetSourceResources: mocks.getDatasetSourceResources,
  admitDatasetResource: mocks.admitDatasetResource,
  promoteDatasetTable: mocks.promoteDatasetTable,
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
  unpinAgent2Object: mocks.unpinAgent2Object,
  unpinAgent2Result: mocks.unpinAgent2Result,
}));
vi.mock("../lib/agent2-execution-api", () => ({
  getAgent2ExecutionProgress: mocks.getAgent2ExecutionProgress,
  cancelAgent2Execution: mocks.cancelAgent2Execution,
}));
vi.mock("../lib/agent2-research-api", () => ({
  Agent2ReadError: class Agent2ReadError extends Error {
    readonly status: number;

    constructor(status: number) {
      super(`科学呈现暂时无法读取 (${status})`);
      this.name = "Agent2ReadError";
      this.status = status;
    }
  },
  getAgent2ContextManifest: mocks.getAgent2ContextManifest,
  listAgent2ResearchTurns: mocks.listAgent2ResearchTurns,
  dispatchAgent2ResearchTurn: mocks.dispatchAgent2ResearchTurn,
  createAgent2ResearchTurn: mocks.createAgent2ResearchTurn,
  getAgent2ResearchTurn: mocks.getAgent2ResearchTurn,
  getAgent2ResearchTurnResult: mocks.getAgent2ResearchTurnResult,
}));

vi.mock("../../shared/layout/ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => (
    <>{children}</>
  ),
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => (
    <>{children}</>
  ),
}));

vi.mock("../../scientific-viewers/ScientificViewerAdapter", () => ({
  ScientificResultViewer: () => <div data-testid="scientific-result-viewer" />,
}));
vi.mock("../../features/research/Agent2ScientificPresentation", () => ({
  Agent2ScientificPresentation: ({ turnId }: { turnId: string }) => (
    <section aria-label="权威 ResearchTurn 科学呈现">Turn {turnId}</section>
  ),
}));

import {
  agent2ContextManifestForTurn,
  agent2ContinueInput,
  agent2ProgressHasFreshSessionMessages,
  agent2ProgressForTurn,
  agent2ProgressNeedsRefresh,
  agent2RetryInput,
  contextOperationSequenceLabel,
  contextManifestVisibleItems,
  dedupeResearchTimelineMessages,
  displayResearchMessage,
  editBranchSubmissionAllowed,
  groundedEvidenceNarrative,
  mergeArtifacts,
  mergeJobEvents,
  ResearchPage,
  researchBranchChoices,
  researchBranchDescriptor,
  researchBranchNavigation,
  researchMessageVisibleInTimeline,
  researchMessageWindow,
  researchStateForAgent2Progress,
  researchStarterPrompts,
  researchTechnicalSummary,
  retryLineageForTurn,
  requestWasAborted,
  resolveAgent2TurnForRecovery,
  runProcessStepState,
  shouldSuppressAgent2DispatchError,
  userFacingPlanStep,
} from "./ResearchPages";

it("recognizes only typed abort failures as canceled requests", () => {
  const abort = new Error("aborted");
  abort.name = "AbortError";
  expect(requestWasAborted(abort)).toBe(true);
  expect(requestWasAborted(new Error("network failed"))).toBe(false);
  expect(requestWasAborted("AbortError")).toBe(false);
});

it("allows Edit-last-message submission only after the authoritative Turn is ready", () => {
  const turn = {
    turn_id: "turn-edit",
    research_session_id: "session-1",
    project_id: "project-1",
    sequence_no: 1,
    parent_turn_id: null,
    status: "COMPLETED",
    user_message: { id: "message-1", role: "user", content: "原问题" },
    context: null,
    created_at: "2026-09-05T00:00:00Z",
  } satisfies Agent2TurnDetail;

  expect(editBranchSubmissionAllowed(undefined, "idle", null)).toBe(true);
  expect(editBranchSubmissionAllowed("turn-edit", "loading", null)).toBe(false);
  expect(editBranchSubmissionAllowed("turn-edit", "error", null)).toBe(false);
  expect(editBranchSubmissionAllowed("turn-edit", "ready", null)).toBe(false);
  expect(editBranchSubmissionAllowed("turn-edit", "ready", turn)).toBe(true);
});

it("keeps context disclosures bounded by default but lets researchers inspect every included item", () => {
  const manifest = {
    context_manifest_id: "manifest",
    operation: "PLANNER",
    project_id: "project",
    research_session_id: "session",
    research_turn_id: "turn",
    policy_version: "2.0",
    included_items: Array.from({ length: 9 }, (_, index) => ({
      item_id: `item-${index}`,
      kind: "SCIENTIFIC_RESULT",
      authority_class: "SCIENTIFIC_RESULT",
      server_side_source_identity: `result-${index}`,
      provider_opaque_ref: `result_${index}`,
      exact_object_id: null,
      exact_object_version_id: null,
      result_ref: `result-${index}`,
      inclusion_reason: "explicit referenced prior Result",
      selection_mode: "EXPLICIT",
      authorization_checked: true,
      content_fingerprint: "a".repeat(64),
      estimated_tokens: 5,
      was_compacted: false,
      was_truncated: false,
      superseded_state: "CURRENT",
    })),
    excluded_items: [],
    estimated_input_tokens: 45,
    input_budget: 10000,
    reserved_output_tokens: 1000,
    repair_margin: 100,
    compaction_state: "NONE",
    truncation_state: "NONE",
    context_fingerprint: "b".repeat(64),
    created_at: "2026-09-04T00:00:00Z",
  } as Agent2ContextManifest;

  expect(contextManifestVisibleItems(manifest, false)).toHaveLength(8);
  expect(contextManifestVisibleItems(manifest, true)).toHaveLength(9);
  expect(contextManifestVisibleItems(null, true)).toEqual([]);
});

it("keeps huge context disclosures bounded while preserving ordered provenance", () => {
  const item = (index: number) => ({
    item_id: `item-${index}`,
    kind: "SCIENTIFIC_RESULT" as const,
    authority_class: "SCIENTIFIC_RESULT" as const,
    server_side_source_identity: `result-${index}`,
    provider_opaque_ref: `opaque-${index}`,
    result_ref: `result-${index}`,
    inclusion_reason: "explicit referenced prior Result",
    selection_mode: "EXPLICIT" as const,
    authorization_checked: true,
    content_fingerprint: "a".repeat(64),
    estimated_tokens: 5,
    was_compacted: false,
    was_truncated: false,
    superseded_state: "CURRENT" as const,
  });
  const manifest = {
    included_items: Array.from({ length: 10_000 }, (_, index) => item(index)),
  } as Agent2ContextManifest;

  expect(contextManifestRenderItems(manifest, false)).toHaveLength(8);
  const expanded = contextManifestRenderItems(manifest, true);
  expect(expanded).toHaveLength(CONTEXT_MANIFEST_RENDER_WINDOW);
  expect(expanded[0].server_side_source_identity).toBe("result-0");
  expect(expanded.at(-1)?.server_side_source_identity).toBe("result-31");
});

it("collapses adjacent duplicate persisted messages without hiding deliberate repeats", () => {
  const base = (id: string, role: "user" | "assistant", content: string) => ({
    id,
    session_id: "session-1",
    role,
    content,
    created_at: "2026-08-31T00:00:00Z",
  });
  const deduped = dedupeResearchTimelineMessages([
    base("u-1", "user", "同一个问题"),
    base("u-2", "user", "同一个问题"),
    base("a-1", "assistant", "回答"),
    base("u-3", "user", "同一个问题"),
    base("u-4", "user", "同一个问题"),
  ]);
  expect(deduped.map((item) => item.id)).toEqual(["u-1", "a-1", "u-3"]);
});

it("disambiguates repeated operation context manifests without hiding retries", () => {
  const records = [
    { operation: "ORCHESTRATOR", manifest: { context_manifest_id: "ctx-1" } },
    { operation: "REPORT", manifest: { context_manifest_id: "ctx-2" } },
    { operation: "REPORT", manifest: { context_manifest_id: "ctx-3" } },
  ] as Parameters<typeof contextOperationSequenceLabel>[0];

  expect(contextOperationSequenceLabel(records, 0)).toBe("理解问题");
  expect(contextOperationSequenceLabel(records, 1)).toBe("整理报告 · 1/2");
  expect(contextOperationSequenceLabel(records, 2)).toBe("整理报告 · 2/2");
});

it("continues polling from the first durable Turn states through interpretation", () => {
  expect(agent2ProgressNeedsRefresh("RECEIVED")).toBe(true);
  expect(agent2ProgressNeedsRefresh("RESOLVING_CONTEXT")).toBe(true);
  expect(agent2ProgressNeedsRefresh("PLAN_READY")).toBe(true);
  expect(agent2ProgressNeedsRefresh("INTERPRETING")).toBe(true);
  expect(agent2ProgressNeedsRefresh("COMPLETED")).toBe(false);
  expect(agent2ProgressNeedsRefresh("CANCELED")).toBe(false);
});

it("maps durable Agent2 progress back into a usable composer state", () => {
  expect(researchStateForAgent2Progress("PLANNING")).toBe("planning");
  expect(researchStateForAgent2Progress("INTERPRETING")).toBe("running");
  expect(researchStateForAgent2Progress("COMPLETED")).toBe("complete");
  expect(researchStateForAgent2Progress("PARTIAL")).toBe("partial");
  expect(researchStateForAgent2Progress("PLAN_REJECTED")).toBe("failed");
  expect(researchStateForAgent2Progress("CANCELED")).toBe("idle");
  expect(researchStateForAgent2Progress("ANSWERED")).toBe("idle");
  expect(researchStateForAgent2Progress("UNKNOWN")).toBeNull();
});

it("refreshes persisted conversation messages when a Turn reaches a terminal state", () => {
  expect(agent2ProgressHasFreshSessionMessages("RECEIVED")).toBe(false);
  expect(agent2ProgressHasFreshSessionMessages("INTERPRETING")).toBe(false);
  expect(agent2ProgressHasFreshSessionMessages("ANSWERED")).toBe(true);
  expect(agent2ProgressHasFreshSessionMessages("COMPLETED")).toBe(true);
  expect(agent2ProgressHasFreshSessionMessages("PARTIAL")).toBe(true);
  expect(agent2ProgressHasFreshSessionMessages("FAILED")).toBe(true);
  expect(agent2ProgressHasFreshSessionMessages("CANCELED")).toBe(true);
});

it("resolves recovery state only for the exact authorized Project/Session/Turn scope", () => {
  const turn = {
    turn_id: "turn-exact",
    research_session_id: "session-exact",
    project_id: "project-exact",
    sequence_no: 1,
    parent_turn_id: null,
    status: "COMPLETED",
    user_message: { id: "message-exact", role: "user", content: "原问题" },
    created_at: "2026-09-05T00:00:00Z",
  };
  expect(
    resolveAgent2TurnForRecovery(
      [turn],
      "project-exact",
      "session-exact",
      "turn-exact",
    ),
  ).toEqual(turn);
  expect(
    resolveAgent2TurnForRecovery(
      [turn],
      "project-other",
      "session-exact",
      "turn-exact",
    ),
  ).toBeNull();
  expect(
    resolveAgent2TurnForRecovery(
      [turn],
      "project-exact",
      "session-other",
      "turn-exact",
    ),
  ).toBeNull();
  expect(
    resolveAgent2TurnForRecovery(
      [turn],
      "project-exact",
      "session-exact",
      "turn-missing",
    ),
  ).toBeNull();
});

it("reconstructs the exact persisted Turn message after remount and reconnect", async () => {
  const session = {
    id: "session-recover",
    project_id: "project_1",
    title: "可恢复研究",
    status: "active",
    messages: [],
  };
  const turn = {
    turn_id: "turn-recover",
    research_session_id: "session-recover",
    project_id: "project_1",
    sequence_no: 2,
    parent_turn_id: null,
    status: "RUNNING",
    user_message: {
      id: "message-recover",
      role: "user",
      content: "关闭页面后仍应恢复这条研究",
    },
    created_at: "2026-09-05T00:00:00Z",
  };
  mocks.listResearchSessions.mockResolvedValue([session]);
  mocks.getResearchSession.mockResolvedValue(session);
  mocks.listAgent2ResearchTurns.mockResolvedValue([turn]);

  const first = render(
    <ResearchPage
      projectId="project_1"
      sessionId="session-recover"
      agent2TurnId="turn-recover"
    />,
  );
  expect(await screen.findByText("关闭页面后仍应恢复这条研究")).toBeInTheDocument();
  first.unmount();

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session-recover"
      agent2TurnId="turn-recover"
    />,
  );
  expect(await screen.findByText("关闭页面后仍应恢复这条研究")).toBeInTheDocument();

  mocks.listResearchSessions.mockClear();
  mocks.getProjectHistory.mockClear();
  window.dispatchEvent(new Event("online"));
  await waitFor(() => {
    expect(mocks.listResearchSessions).toHaveBeenCalled();
    expect(mocks.getProjectHistory).toHaveBeenCalled();
  });
});

it("builds retry input from the exact failed Turn rather than the session tail", () => {
  expect(
    agent2RetryInput({
      turn_id: "turn-failed",
      id: "turn-failed",
      research_session_id: "session-1",
      project_id: "project-1",
      sequence_no: 3,
      parent_turn_id: "turn-parent",
      status: "FAILED",
      user_message: {
        id: "message-failed",
        role: "user",
        content: "  分析精确结构版本  ",
      },
      context: {
        scope: [
          {
            object_id: "object-1",
            version_id: "version-1",
            project_id: "project-1",
            object_type: "structure.crystal",
          },
        ],
        selection: [],
        scientific_selection: [],
      },
      created_at: "2026-08-30T00:00:00Z",
    }),
  ).toEqual({
    message: "分析精确结构版本",
    reply_to_turn_id: "turn-failed",
    ui_context: {
      active_object_refs: [
        {
          object_id: "object-1",
          version_id: "version-1",
          project_id: "project-1",
          object_type: "structure.crystal",
        },
      ],
      selection_refs: [],
      scientific_selections: [],
      explicit_object_refs: [
        {
          object_id: "object-1",
          version_id: "version-1",
          project_id: "project-1",
          object_type: "structure.crystal",
        },
      ],
      explicit_result_ids: [],
      explicit_finding_refs: [],
    },
  });
});

it("accepts a retry lineage only when the persisted parent is the preserved failed Turn", () => {
  const turns = [
    {
      turn_id: "turn-failed",
      research_session_id: "session-1",
      project_id: "project-1",
      sequence_no: 1,
      parent_turn_id: null,
      status: "FAILED",
      user_message: { id: "message-failed", role: "user", content: "分析结构" },
      created_at: "2026-09-05T00:00:00Z",
    },
    {
      turn_id: "turn-retry",
      research_session_id: "session-1",
      project_id: "project-1",
      sequence_no: 2,
      parent_turn_id: "turn-failed",
      status: "ORCHESTRATING",
      user_message: { id: "message-retry", role: "user", content: "分析结构" },
      created_at: "2026-09-05T00:01:00Z",
    },
  ];

  expect(
    retryLineageForTurn(turns, "turn-retry", "turn-failed"),
  ).toMatchObject({
    current: { turn_id: "turn-retry" },
    source: { turn_id: "turn-failed", status: "FAILED" },
  });
  expect(
    retryLineageForTurn(turns, "turn-retry", "turn-other"),
  ).toBeNull();
  expect(
    retryLineageForTurn(
      [{ ...turns[0], status: "COMPLETED" }, turns[1]],
      "turn-retry",
      "turn-failed",
    ),
  ).toBeNull();
});

it("builds Continue input from the exact selected Turn with a new question", () => {
  const turn = {
    turn_id: "turn-canceled",
    id: "turn-canceled",
    research_session_id: "session-1",
    project_id: "project-1",
    sequence_no: 4,
    parent_turn_id: "turn-parent",
    status: "CANCELED",
    user_message: {
      id: "message-canceled",
      role: "user",
      content: "旧问题",
    },
    context: {
      scope: [
        {
          object_id: "object-exact",
          version_id: "version-exact",
          project_id: "project-1",
          object_type: "structure.crystal",
        },
      ],
      selection: [],
      scientific_selection: [],
    },
    created_at: "2026-08-30T00:00:00Z",
  } satisfies Agent2TurnDetail;

  expect(agent2ContinueInput(turn, "  计算这个精确版本的 RDF  ")).toEqual({
    message: "计算这个精确版本的 RDF",
    reply_to_turn_id: "turn-canceled",
    ui_context: {
      active_object_refs: turn.context.scope,
      selection_refs: [],
      scientific_selections: [],
      explicit_object_refs: turn.context.scope,
      explicit_result_ids: [],
      explicit_finding_refs: [],
    },
  });
});

it("binds Continue to an exact reusable Result snapshot when one is available", () => {
  const turn = {
    turn_id: "turn-canceled",
    id: "turn-canceled",
    research_session_id: "session-1",
    project_id: "project-1",
    sequence_no: 4,
    parent_turn_id: "turn-parent",
    status: "CANCELED",
    user_message: {
      id: "message-canceled",
      role: "user",
      content: "旧问题",
    },
    context: {
      scope: [],
      selection: [],
      scientific_selection: [],
    },
    created_at: "2026-08-30T00:00:00Z",
  } satisfies Agent2TurnDetail;

  expect(agent2ContinueInput(turn, "换一个角度解释", "snapshot-exact")).toEqual({
    message: "换一个角度解释",
    reply_to_turn_id: "turn-canceled",
    ui_context: {
      active_object_refs: [],
      selection_refs: [],
      scientific_selections: [],
      explicit_object_refs: [],
      explicit_result_ids: ["snapshot-exact"],
      explicit_finding_refs: [],
    },
  });
});

it("focuses a long conversation on the exact selected research branch", () => {
  const messages = Array.from({ length: 24 }, (_, index) => ({
    id: `message-${index + 1}`,
    session_id: "session-1",
    role: index % 2 === 0 ? "user" as const : "assistant" as const,
    content: `message ${index + 1}`,
    created_at: "2026-08-30T00:00:00Z",
  }));

  const bounded = researchMessageWindow(messages, "message-9");
  expect(bounded.visible.map((message) => message.id)).toEqual([
    "message-9",
    "message-10",
  ]);
  expect(bounded.hiddenBefore).toBe(8);
  expect(bounded.hiddenAfter).toBe(14);
  expect(researchMessageWindow(messages, "message-9", true).visible).toHaveLength(24);
});

it("bounds the expanded conversation DOM window for 1000+ messages", () => {
  const messages = Array.from({ length: 1001 }, (_, index) => ({
    id: `message-${index + 1}`,
    session_id: "session-long",
    role: index % 2 === 0 ? "user" as const : "assistant" as const,
    content: `message ${index + 1}`,
    created_at: `2026-09-05T00:${String(index).padStart(4, "0")}Z`,
  }));
  const window = researchMessageWindow(messages, null, true);
  expect(window.visible).toHaveLength(100);
  expect(window.hiddenBefore).toBe(0);
  expect(window.visible[0].id).toBe("message-1");
  expect(window.visible.at(-1)?.id).toBe("message-100");
  expect(window.visible.every((message) =>
    messages.some((candidate) => candidate.id === message.id),
  )).toBe(true);
});

it("keeps the real conversation DOM bounded and navigable across message windows", async () => {
  const messages = Array.from({ length: 1001 }, (_, index) => ({
    id: `message-${index + 1}`,
    session_id: "session-windowed",
    role: index % 2 === 0 ? "user" as const : "assistant" as const,
    content: `window message ${index + 1}`,
    created_at: `2026-09-05T00:${String(index).padStart(4, "0")}Z`,
  }));
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session-windowed", project_id: "project_1", title: "长研究", status: "active" },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session-windowed",
    project_id: "project_1",
    title: "长研究",
    status: "active",
    messages,
  });

  const started = performance.now();
  for (let index = 0; index < 20; index += 1) researchMessageWindow(messages, null, true);
  const elapsed = performance.now() - started;
  expect(elapsed).toBeLessThan(100);

  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" sessionId="session-windowed" />);
  expect(await screen.findByText("window message 1001")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "查看会话窗口" }));
  const stream = screen.getByRole("log", { name: "研究对话" });
  expect(stream.querySelectorAll("[data-message-id]")).toHaveLength(100);
  expect(within(stream).getByText("window message 1")).toBeInTheDocument();
  expect(within(stream).queryByText("window message 101")).toBeNull();

  const next = screen.getByRole("button", { name: "查看更新消息" });
  await user.click(next);
  expect(next).toHaveFocus();
  expect(within(stream).getByText("window message 101")).toBeInTheDocument();
  expect(within(stream).queryByText("window message 1")).toBeNull();
  expect(stream.querySelectorAll("[data-message-id]")).toHaveLength(100);
});

it("describes a research branch from persisted message revision and parent Turn identities", () => {
  const root = {
    turn_id: "turn-root",
    research_session_id: "session-1",
    project_id: "project-1",
    sequence_no: 1,
    parent_turn_id: null,
    status: "COMPLETED",
    user_message: {
      id: "message-revision-root",
      role: "user",
      content: "计算 MSD",
    },
    created_at: "2026-09-05T00:00:00Z",
  };
  const branch = {
    ...root,
    turn_id: "turn-branch",
    sequence_no: 2,
    parent_turn_id: "turn-root",
    user_message: {
      id: "message-revision-branch",
      role: "user",
      content: "限定 1–6 ps 重新评估扩散",
    },
  };

  expect(researchBranchDescriptor([root, branch], branch)).toEqual({
    turnId: "turn-branch",
    messageRevisionId: "message-revision-branch",
    title: "限定 1–6 ps 重新评估扩散",
    sourceTurnId: "turn-root",
    sourceTitle: "计算 MSD",
  });
});

it("does not render sibling or duplicated user projections beside the selected branch", () => {
  const messages = [
    { id: "old-question", session_id: "session-1", role: "user" as const, content: "同一个问题", created_at: "2026-08-30T00:00:00Z" },
    { id: "old-answer", session_id: "session-1", role: "assistant" as const, content: "旧结果", created_at: "2026-08-30T00:01:00Z" },
    { id: "sibling-question", session_id: "session-1", role: "user" as const, content: "同一个问题", created_at: "2026-08-30T00:02:00Z" },
    { id: "current-question", session_id: "session-1", role: "user" as const, content: "同一个问题", created_at: "2026-08-30T00:03:00Z" },
    { id: "current-answer", session_id: "session-1", role: "assistant" as const, content: "当前结果", created_at: "2026-08-30T00:04:00Z" },
  ];

  const focused = researchMessageWindow(messages, "current-question");

  expect(focused.visible.map((message) => message.id)).toEqual([
    "current-question",
    "current-answer",
  ]);
  expect(focused.hiddenBefore).toBe(3);
  expect(focused.hiddenAfter).toBe(0);
});

it("keeps downstream process acknowledgements out of the scientific conversation", () => {
  expect(
    researchMessageVisibleInTimeline({
      id: "message-process",
      session_id: "session-1",
      role: "assistant",
      content: "provider candidate that has not been grounded",
      payload: { messageKind: "DOWNSTREAM_ACKNOWLEDGEMENT" },
      created_at: "2026-08-30T00:00:00Z",
    }),
  ).toBe(false);
  expect(
    researchMessageVisibleInTimeline({
      id: "message-final",
      session_id: "session-1",
      role: "assistant",
      content: "grounded final",
      payload: { messageKind: "ASSISTANT_FINAL" },
      created_at: "2026-08-30T00:00:00Z",
    }),
  ).toBe(true);
});

it("resolves branch choices from explicit persisted turn relations", () => {
  const turns = [
    { id: "root", turn_id: "root", research_session_id: "session", project_id: "project", sequence_no: 1, parent_turn_id: null, status: "COMPLETED", user_message: { id: "m1", role: "user", content: "原问题" }, created_at: "2026-08-28T00:00:00Z" },
    { id: "branch-a", turn_id: "branch-a", research_session_id: "session", project_id: "project", sequence_no: 2, parent_turn_id: "root", status: "COMPLETED", user_message: { id: "m2", role: "user", content: "分支 A" }, created_at: "2026-08-28T00:01:00Z" },
    { id: "branch-b", turn_id: "branch-b", research_session_id: "session", project_id: "project", sequence_no: 3, parent_turn_id: "root", status: "PLANNING", user_message: { id: "m3", role: "user", content: "分支 B" }, created_at: "2026-08-28T00:02:00Z" },
  ];

  expect(researchBranchChoices(turns, "branch-b").map((turn) => turn.id)).toEqual(["root", "branch-a", "branch-b"]);
  expect(researchBranchNavigation(turns, "branch-a")).toMatchObject({
    currentIndex: 1,
    current: { id: "branch-a" },
    previous: { id: "root" },
    next: { id: "branch-b" },
  });
});

it("never projects a previous Turn's progress or context into a newly selected Turn", () => {
  const progress = {
    contract_version: "1.0" as const,
    turn_id: "turn-parent",
    status: "COMPLETED" as const,
    steps: [],
    active_step_ids: [],
    completed_step_count: 0,
    total_step_count: 0,
    incremental_outputs: [],
    warnings: [],
    result_projection_pending: false,
  };
  const manifest = {
    context_manifest_id: "manifest-parent",
    operation: "ORCHESTRATE",
    project_id: "project",
    research_session_id: "session",
    research_turn_id: "turn-parent",
    policy_version: "2.0",
    included_items: [],
    excluded_items: [],
    estimated_input_tokens: 10,
    input_budget: 100,
    reserved_output_tokens: 20,
    repair_margin: 5,
    compaction_state: "NONE",
    truncation_state: "NONE",
    context_fingerprint: "fingerprint",
    created_at: "2026-08-30T00:00:00Z",
  };

  expect(agent2ProgressForTurn(progress, "turn-child")).toBeNull();
  expect(agent2ContextManifestForTurn(manifest, "turn-child")).toBeNull();
  expect(agent2ProgressForTurn(progress, "turn-parent")).toBe(progress);
  expect(agent2ContextManifestForTurn(manifest, "turn-parent")).toBe(manifest);
});

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
  window.sessionStorage.clear();
  mocks.listResearchSessions.mockResolvedValue([]);
  mocks.bulkUpdateResearchSessions.mockResolvedValue({
    action: "ARCHIVE",
    sessionIds: [],
    count: 0,
  });
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
  mocks.getDataset.mockResolvedValue({
    id: "dataset_selected",
    datasetId: "dataset_selected",
    name: "选中的 XRD 数据",
    profileId: "profile_selected",
  });
  mocks.getDatasetProfile.mockResolvedValue({
    id: "profile_selected",
    profileId: "profile_selected",
    datasetId: "dataset_selected",
  });
  mocks.getDatasetSourceResources.mockResolvedValue([]);
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
  mocks.getAgent2ExecutionProgress.mockResolvedValue(null);
  mocks.cancelAgent2Execution.mockResolvedValue({ turn_id: "turn-1", status: "CANCELED" });
  mocks.getAgent2ContextManifest.mockResolvedValue(null);
  mocks.listAgent2ResearchTurns.mockResolvedValue([]);
  mocks.dispatchAgent2ResearchTurn.mockResolvedValue({ turn_id: "turn-1" });
  mocks.createAgent2ResearchTurn.mockResolvedValue({ turn_id: "turn-new" });
  mocks.getAgent2ResearchTurn.mockResolvedValue({
    turn_id: "turn-1",
    research_session_id: "session_1",
    project_id: "project_1",
    sequence_no: 1,
    parent_turn_id: null,
    status: "FAILED",
    user_message: { id: "message-1", role: "user", content: "分析精确版本" },
    context: null,
    created_at: "2026-08-30T00:00:00Z",
  });
  mocks.getAgent2ResearchTurnResult.mockResolvedValue(null);
});

it("creates Retry as a new ResearchTurn lineage and carries the preserved failed Turn into navigation", async () => {
  const user = userEvent.setup();
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_1",
      project_id: "project_1",
      title: "失败研究",
      status: "active",
    },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "失败研究",
    status: "active",
    messages: [],
  });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    turn_id: "turn-failed",
    status: "FAILED",
    completed_step_count: 0,
    total_step_count: 1,
    steps: [],
    incremental_outputs: [],
    warnings: [],
  });
  mocks.getAgent2ResearchTurn.mockResolvedValue({
    turn_id: "turn-failed",
    research_session_id: "session_1",
    project_id: "project_1",
    sequence_no: 1,
    parent_turn_id: null,
    status: "FAILED",
    user_message: {
      id: "message-failed",
      role: "user",
      content: "分析这个结构的局部环境",
    },
    context: {
      scope: [],
      selection: [],
      scientific_selection: [],
    },
    created_at: "2026-09-05T00:00:00Z",
  });
  mocks.createAgent2ResearchTurn.mockResolvedValue({
    turn_id: "turn-retry",
    research_session_id: "session_1",
    project_id: "project_1",
    sequence_no: 2,
    parent_turn_id: "turn-failed",
    status: "ORCHESTRATING",
    user_message: {
      id: "message-retry",
      role: "user",
      content: "分析这个结构的局部环境",
    },
    created_at: "2026-09-05T00:01:00Z",
  });

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-failed"
    />,
  );

  await user.click(
    await screen.findByRole("button", { name: "重新研究（新运行）" }),
  );

  await waitFor(() =>
    expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
      "project_1",
      "session_1",
      expect.objectContaining({
        message: "分析这个结构的局部环境",
        reply_to_turn_id: "turn-failed",
      }),
    ),
  );
  expect(mocks.routerPush).toHaveBeenCalledWith(
    "/projects/project_1/research/session_1?turn=turn-retry&retryOf=turn-failed",
  );
});

it("opens a failed Turn with retry intent by creating one new lineage and preserving the original", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_1",
      project_id: "project_1",
      title: "失败研究",
      status: "active",
    },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "失败研究",
    status: "active",
    messages: [],
  });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    turn_id: "turn-failed",
    status: "FAILED",
    completed_step_count: 0,
    total_step_count: 1,
    steps: [],
    incremental_outputs: [],
    warnings: [],
  });
  mocks.getAgent2ResearchTurn.mockResolvedValue({
    turn_id: "turn-failed",
    research_session_id: "session_1",
    project_id: "project_1",
    sequence_no: 4,
    parent_turn_id: null,
    status: "FAILED",
    user_message: {
      id: "message-failed",
      role: "user",
      content: "解释这个结构的局部环境",
    },
    context: {
      scope: [],
      selection: [],
      scientific_selection: [],
    },
    created_at: "2026-09-05T00:00:00Z",
  });
  mocks.createAgent2ResearchTurn.mockResolvedValue({
    turn_id: "turn-retry",
    research_session_id: "session_1",
    project_id: "project_1",
    sequence_no: 5,
    parent_turn_id: "turn-failed",
    status: "ORCHESTRATING",
    user_message: {
      id: "message-retry",
      role: "user",
      content: "解释这个结构的局部环境",
    },
    created_at: "2026-09-05T00:01:00Z",
  });

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-failed"
      retryRequested
    />,
  );

  await waitFor(() =>
    expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
      "project_1",
      "session_1",
      expect.objectContaining({
        message: "解释这个结构的局部环境",
        reply_to_turn_id: "turn-failed",
      }),
    ),
  );
  expect(mocks.getAgent2ResearchTurn).toHaveBeenCalledWith("turn-failed");
  expect(mocks.routerPush).toHaveBeenCalledWith(
    "/projects/project_1/research/session_1?turn=turn-retry&retryOf=turn-failed",
  );
  expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledTimes(1);
});

it("shows a validated Retry identity and a navigation link to the preserved failed Turn", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_1",
      project_id: "project_1",
      title: "重试研究",
      status: "active",
    },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "重试研究",
    status: "active",
    messages: [],
  });
  mocks.listAgent2ResearchTurns.mockResolvedValue([
    {
      id: "turn-failed",
      turn_id: "turn-failed",
      research_session_id: "session_1",
      project_id: "project_1",
      sequence_no: 1,
      parent_turn_id: null,
      status: "FAILED",
      user_message: {
        id: "message-failed",
        role: "user",
        content: "分析这个结构的局部环境",
      },
      created_at: "2026-09-05T00:00:00Z",
    },
    {
      id: "turn-retry",
      turn_id: "turn-retry",
      research_session_id: "session_1",
      project_id: "project_1",
      sequence_no: 2,
      parent_turn_id: "turn-failed",
      status: "COMPLETED",
      user_message: {
        id: "message-retry",
        role: "user",
        content: "分析这个结构的局部环境",
      },
      created_at: "2026-09-05T00:01:00Z",
    },
  ]);
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    turn_id: "turn-retry",
    status: "COMPLETED",
    completed_step_count: 1,
    total_step_count: 1,
    steps: [],
    incremental_outputs: [],
    warnings: [],
  });

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-retry"
      retryOfTurnId="turn-failed"
    />,
  );

  const lineage = await screen.findByRole("status", {
    name: "研究重试关系",
  });
  expect(lineage).toHaveTextContent("已创建新的 ResearchTurn");
  expect(lineage).toHaveTextContent("原未完成运行及其失败证据仍被保留");
  expect(
    within(lineage).getByRole("link", { name: "查看保留的原运行" }),
  ).toHaveAttribute(
    "href",
    "/projects/project_1/research/session_1?turn=turn-failed",
  );
  expect(within(lineage).getByText("turn-retry")).toBeInTheDocument();
  expect(within(lineage).getByText("turn-failed")).toBeInTheDocument();
});

it("uses one authoritative completed ResearchTurn presentation without rendering the legacy workbench result twice", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session_1", project_id: "project_1", title: "研究会话", status: "active" },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "研究会话",
    status: "active",
    messages: [],
  });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    turn_id: "turn-complete",
    status: "COMPLETED",
    completed_step_count: 1,
    total_step_count: 1,
    steps: [],
    incremental_outputs: [],
    warnings: [],
  });

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      runId="job_agent2_turn-complete"
      agent2TurnId="turn-complete"
    />,
  );

  expect(
    await screen.findByRole("region", { name: "权威 ResearchTurn 科学呈现" }),
  ).toHaveTextContent("turn-complete");
  expect(screen.queryByText("当前没有可展示的结果。")).not.toBeInTheDocument();
  expect(screen.queryByRole("heading", { name: "主要结果" })).not.toBeInTheDocument();
  expect(screen.getAllByRole("region", { name: "分析进度" })).toHaveLength(1);
  expect(screen.queryByText("✓ 分析完成 · 0 个步骤")).not.toBeInTheDocument();
});

it("does not hydrate or poll legacy Job execution state when an explicit ResearchTurn is present", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session_1", project_id: "project_1", title: "研究会话", status: "active" },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "研究会话",
    status: "active",
    messages: [],
  });
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [],
    analyses: [{
      jobId: "job-related",
      researchSessionId: "session_1",
      researchTurnId: "turn-related",
      status: "running",
      userQuestion: "分析精确结构",
      toolIds: [],
      stepCount: 1,
      artifactCount: 0,
      artifactTypes: [],
      interpretationCount: 0,
      reportCount: 0,
      recipeCount: 0,
    }],
  });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    contract_version: "1.0",
    turn_id: "turn-related",
    status: "RUNNING",
    response_kind: "SCIENTIFIC_EXECUTION",
    completed_step_count: 0,
    total_step_count: 1,
    active_step_ids: ["step-1"],
    steps: [],
    incremental_outputs: [],
    warnings: [],
    execution_outcome: null,
    result_projection_pending: false,
  });

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      runId="job-related"
      agent2TurnId="turn-related"
    />,
  );

  expect(await screen.findByRole("region", { name: "分析进度" })).toBeInTheDocument();
  expect(mocks.getPlannerJob).not.toHaveBeenCalled();
  expect(mocks.getPlannerJobEvents).not.toHaveBeenCalled();
  expect(mocks.getPlannerJobArtifacts).not.toHaveBeenCalled();
});

it("aborts an in-flight ResearchTurn poll and prevents duplicate online polling after navigation", async () => {
  let progressSignal: AbortSignal | undefined;
  mocks.getAgent2ExecutionProgress.mockImplementationOnce(
    (_turnId: string, options?: { signal?: AbortSignal }) => {
      progressSignal = options?.signal;
      return new Promise(() => undefined);
    },
  );

  const { unmount } = render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-in-flight"
    />,
  );

  await waitFor(() => expect(progressSignal).toBeDefined());
  window.dispatchEvent(new Event("online"));
  expect(mocks.getAgent2ExecutionProgress).toHaveBeenCalledTimes(1);
  unmount();
  expect(progressSignal?.aborted).toBe(true);
  window.dispatchEvent(new Event("online"));
  expect(mocks.getAgent2ExecutionProgress).toHaveBeenCalledTimes(1);
});

it("presents used context as researcher-facing provenance with technical identity behind disclosure", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session_1", project_id: "project_1", title: "研究会话", status: "active" },
  ]);
  mocks.getAgent2ContextManifest.mockResolvedValue({
    manifest: {
      context_manifest_id: "2be3bfa5-4951-468a-a47f-3bccd4e10f6d",
      operation: "PLANNER",
      project_id: "project_1",
      research_session_id: "session_1",
      research_turn_id: "turn-complete",
      policy_version: "2.0",
      included_items: [
        {
          item_id: "selection-1",
          kind: "SCIENTIFIC_SELECTION",
          authority_class: "SCIENTIFIC_DATA",
          freshness: "CURRENT",
          server_side_source_identity: "object-1:version-1",
          provider_opaque_ref: "source-1",
          exact_object_id: "object-1",
          exact_object_version_id: "version-1",
          result_ref: null,
          inclusion_reason: "active scientific scope",
          selection_mode: "UI_SELECTION",
          authorization_checked: true,
          content_fingerprint: "a".repeat(64),
          estimated_tokens: 24,
          was_compacted: false,
          was_truncated: false,
          superseded_state: "CURRENT",
        },
        ...Array.from({ length: 8 }, (_, index) => ({
          item_id: `result-${index + 2}`,
          kind: "SCIENTIFIC_RESULT",
          authority_class: "SCIENTIFIC_RESULT",
          freshness: "HISTORICAL_VALID",
          server_side_source_identity: `result-extra-${index + 2}`,
          provider_opaque_ref: `result_${index + 2}`,
          exact_object_id: null,
          exact_object_version_id: null,
          result_ref: `result-extra-${index + 2}`,
          inclusion_reason: "explicit referenced prior Result",
          selection_mode: "EXPLICIT",
          authorization_checked: true,
          content_fingerprint: "f".repeat(64),
          estimated_tokens: 8,
          was_compacted: false,
          was_truncated: false,
          superseded_state: "CURRENT",
        })),
      ],
      excluded_items: ["old-conversation-4"],
      estimated_input_tokens: 24,
      input_budget: 12000,
      reserved_output_tokens: 2000,
      repair_margin: 512,
      compaction_state: "NONE",
      truncation_state: "NONE",
      context_fingerprint: "b".repeat(64),
      created_at: "2026-08-30T00:00:00Z",
    },
    manifests: [
      {
        operation: "ORCHESTRATOR",
        manifest: {
          context_manifest_id: "1be3bfa5-4951-468a-a47f-3bccd4e10f6d",
          operation: "ORCHESTRATOR",
          project_id: "project_1",
          research_session_id: "session_1",
          research_turn_id: "turn-complete",
          policy_version: "2.0",
          included_items: [],
          excluded_items: [],
          estimated_input_tokens: 0,
          input_budget: 12000,
          reserved_output_tokens: 2000,
          repair_margin: 512,
          compaction_state: "NONE",
          truncation_state: "NONE",
          context_fingerprint: "c".repeat(64),
          created_at: "2026-08-30T00:00:00Z",
        },
      },
      {
        operation: "PLANNER",
        manifest: {
          context_manifest_id: "2be3bfa5-4951-468a-a47f-3bccd4e10f6d",
          operation: "PLANNER",
          project_id: "project_1",
          research_session_id: "session_1",
          research_turn_id: "turn-complete",
          policy_version: "2.0",
          included_items: [],
          excluded_items: [],
          estimated_input_tokens: 0,
          input_budget: 10000,
          reserved_output_tokens: 2000,
          repair_margin: 512,
          compaction_state: "NONE",
          truncation_state: "NONE",
          context_fingerprint: "d".repeat(64),
          created_at: "2026-08-30T00:00:00Z",
        },
      },
      {
        operation: "INTERPRETER",
        manifest: {
          context_manifest_id: "3be3bfa5-4951-468a-a47f-3bccd4e10f6d",
          operation: "INTERPRETER",
          project_id: "project_1",
          research_session_id: "session_1",
          research_turn_id: "turn-complete",
          policy_version: "2.0",
          included_items: [],
          excluded_items: [],
          estimated_input_tokens: 0,
          input_budget: 12000,
          reserved_output_tokens: 2000,
          repair_margin: 512,
          compaction_state: "NONE",
          truncation_state: "NONE",
          context_fingerprint: "e".repeat(64),
          created_at: "2026-08-30T00:00:00Z",
        },
      },
    ],
  });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    turn_id: "turn-complete",
    status: "COMPLETED",
    completed_step_count: 1,
    total_step_count: 1,
    steps: [],
    incremental_outputs: [],
    warnings: [],
  });

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-complete"
    />,
  );

  const disclosure = await screen.findByText("本次研究使用的上下文");
  expect(disclosure.closest("summary")).toHaveTextContent(/用于规划分析\s*·\s*9 项/);
  const contextDetails = disclosure.closest("details");
  expect(contextDetails).not.toHaveAttribute("open");
  expect(contextDetails).toHaveAttribute("aria-label", "本次研究使用的上下文");
  await userEvent.setup().click(
    screen.getByRole("button", { name: "本次上下文" }),
  );
  await waitFor(() => expect(contextDetails).toHaveAttribute("open"));
  await waitFor(() =>
    expect(document.activeElement).toBe(disclosure.closest("summary")),
  );
  expect(screen.getByText("精确来源与版本已保留")).toBeInTheDocument();
  expect(screen.getByText("当前选择")).toBeInTheDocument();
  expect(screen.getByText("当前科学范围")).toBeInTheDocument();
  expect(screen.queryByText("active scientific scope")).not.toBeInTheDocument();
  expect(
    screen.getByText("从界面选择 · 科学数据权威 · 当前"),
  ).toBeInTheDocument();
  expect(screen.getByText("精确版本")).toHaveTextContent("version-1");
  expect(screen.queryByText("result-extra-9")).not.toBeInTheDocument();
  const expandContext = screen.getByRole("button", {
    name: "查看全部上下文（9 项）",
  });
  expect(expandContext).toHaveAttribute("aria-expanded", "false");
  await userEvent.setup().click(expandContext);
  expect(
    screen.getByRole("button", { name: "收起上下文列表" }),
  ).toHaveAttribute("aria-expanded", "true");
  expect(screen.getByText("result-extra-9")).toBeInTheDocument();
  expect(screen.getAllByText(/科学结果权威 · 历史有效/).length).toBeGreaterThan(0);
  expect(screen.getByText(/有 1 项较低优先级内容未纳入/)).toBeInTheDocument();
  const operations = screen.getByRole("group", { name: "已记录的操作上下文" });
  expect(operations).toHaveTextContent("理解问题");
  expect(operations).toHaveTextContent("规划分析");
  expect(operations).toHaveTextContent("解释结果");
  expect(screen.getByText("审计详情").closest("details"))
    .toHaveAttribute("aria-label", "上下文审计详情");
  expect(screen.getByText("审计详情").closest("details")).not.toHaveAttribute("open");
});

it("offers an in-place retry when the persisted context manifest is temporarily unavailable", async () => {
  const user = userEvent.setup();
  const manifest = {
    context_manifest_id: "manifest-retry",
    operation: "PLANNER",
    project_id: "project_1",
    research_session_id: "session_1",
    research_turn_id: "turn-context-retry",
    policy_version: "2.0",
    included_items: [],
    excluded_items: [],
    estimated_input_tokens: 0,
    input_budget: 10000,
    reserved_output_tokens: 1000,
    repair_margin: 100,
    compaction_state: "NONE",
    truncation_state: "NONE",
    context_fingerprint: "a".repeat(64),
    created_at: "2026-09-04T00:00:00Z",
  } as Agent2ContextManifest;
  mocks.getAgent2ContextManifest
    .mockRejectedValueOnce(new Error("temporarily unavailable"))
    .mockResolvedValueOnce({ manifest });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    turn_id: "turn-context-retry",
    status: "COMPLETED",
    completed_step_count: 1,
    total_step_count: 1,
    steps: [],
    incremental_outputs: [],
    warnings: [],
  });

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-context-retry"
    />,
  );

  expect(
    await screen.findByText("本次研究的上下文清单暂时无法读取"),
  ).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重新读取上下文" }));
  expect(
    await screen.findByText("本次研究使用的上下文"),
  ).toBeInTheDocument();
  expect(mocks.getAgent2ContextManifest).toHaveBeenCalledTimes(2);
});

it("reconciles a Stop race when the scientific run finishes before cancellation", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session_1", project_id: "project_1", title: "研究会话", status: "active" },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "研究会话",
    status: "active",
    messages: [],
  });
  const running = {
    contract_version: "1.0",
    turn_id: "turn-race",
    status: "RUNNING",
    response_kind: "SCIENTIFIC_EXECUTION",
    plan_title: "局部配位环境分析",
    completed_step_count: 0,
    total_step_count: 2,
    active_step_ids: ["step-1"],
    steps: [],
    incremental_outputs: [],
    warnings: [],
    execution_outcome: null,
    result_projection_pending: false,
  } as const;
  const completed = {
    ...running,
    status: "COMPLETED",
    completed_step_count: 2,
    active_step_ids: [],
    execution_outcome: "SUCCESS",
  } as const;
  mocks.getAgent2ExecutionProgress
    .mockResolvedValueOnce(running)
    .mockResolvedValueOnce(completed);
  mocks.cancelAgent2Execution.mockRejectedValueOnce(
    new Error("取消请求未能提交 (409)"),
  );

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-race"
    />,
  );

  fireEvent.click(await screen.findByRole("button", { name: "停止研究" }));

  expect(
    await screen.findByText("研究在停止请求生效前已进入终态；现有科学结果未被覆盖。"),
  ).toBeInTheDocument();
  expect(screen.getByText("科学解释已准备")).toBeInTheDocument();
  expect(screen.queryByText("取消请求未能提交 (409)")).toBeNull();
});

it("turns the primary composer action into Stop while scientific work is active", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session_1", project_id: "project_1", title: "研究会话", status: "active" },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "研究会话",
    status: "active",
    messages: [],
  });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    contract_version: "1.0",
    turn_id: "turn-primary-stop",
    status: "RUNNING",
    response_kind: "SCIENTIFIC_EXECUTION",
    completed_step_count: 0,
    total_step_count: 1,
    active_step_ids: ["step-1"],
    steps: [],
    incremental_outputs: [],
    warnings: [],
    execution_outcome: null,
    result_projection_pending: false,
  });
  mocks.cancelAgent2Execution.mockResolvedValue({
    turn_id: "turn-primary-stop",
    status: "CANCELED",
  });

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-primary-stop"
    />,
  );

  const primaryStop = await screen.findByRole("button", {
    name: "从输入区停止研究",
  });
  expect(screen.queryByRole("button", { name: "开始分析" })).toBeNull();
  fireEvent.click(primaryStop);

  await waitFor(() =>
    expect(mocks.cancelAgent2Execution).toHaveBeenCalledWith(
      "turn-primary-stop",
    ),
  );
  expect(
    await screen.findByText("研究已停止。已经提交的有效输出仍会保留；继续研究不会自动重算。"),
  ).toBeInTheDocument();
});

it("reconciles a queued Stop notice when durable progress reaches CANCELED", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session_1", project_id: "project_1", title: "研究会话", status: "active" },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "研究会话",
    status: "active",
    messages: [],
  });
  const queued = {
    turn_id: "turn-queued",
    status: "QUEUED",
    action: "ANALYZE",
    plan_id: "plan-1",
    job_id: "job-1",
    total_step_count: 2,
    completed_step_count: 0,
    failed_step_count: 0,
    active_step_ids: [],
    execution_outcome: null,
    interpretation_status: null,
    interpretation_id: null,
    steps: [],
    incremental_outputs: [],
    warnings: [],
    result_projection_pending: false,
  } as const;
  const canceled = {
    ...queued,
    status: "CANCELED",
    execution_outcome: "CANCELED",
  } as const;
  mocks.getAgent2ExecutionProgress
    .mockResolvedValueOnce(queued)
    .mockResolvedValueOnce(canceled);
  mocks.cancelAgent2Execution.mockResolvedValueOnce({
    turn_id: "turn-queued",
    status: "CANCELING",
  });

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-queued"
    />,
  );

  fireEvent.click(await screen.findByRole("button", { name: "停止研究" }));
  expect(
    await screen.findByText("停止请求已记录，正在等待运行中的科学步骤安全结束。"),
  ).toBeInTheDocument();
  expect(
    await screen.findByText("研究已停止。已经提交的有效输出仍会保留；继续研究不会自动重算。", {}, { timeout: 3000 }),
  ).toBeInTheDocument();
  expect(screen.queryByText("停止请求已记录，正在等待运行中的科学步骤安全结束。")).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "继续研究" }));
  await waitFor(() => {
    expect(screen.getByLabelText("询问此项目中的数据")).toHaveFocus();
  });
  expect(
    screen.getByText(
      "继续研究会保留当前会话与已授权的精确上下文；只有提交新问题后才会开始新的处理。",
    ),
  ).toBeInTheDocument();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();

  mocks.getAgent2ResearchTurn.mockResolvedValueOnce({
    turn_id: "turn-queued",
    research_session_id: "session_1",
    project_id: "project_1",
    sequence_no: 2,
    parent_turn_id: null,
    status: "CANCELED",
    user_message: {
      id: "message-queued",
      role: "user",
      content: "原始配位问题",
    },
    context: {
      scope: [
        {
          object_id: "object-exact",
          version_id: "version-exact",
          project_id: "project_1",
          object_type: "structure.crystal",
        },
      ],
      selection: [],
      scientific_selection: [],
    },
    created_at: "2026-08-30T00:00:00Z",
  });
  fireEvent.change(screen.getByLabelText("询问此项目中的数据"), {
    target: { value: "计算这个精确结构版本的 RDF" },
  });
  fireEvent.click(screen.getByRole("button", { name: "开始分析" }));
  await waitFor(() =>
    expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
      "project_1",
      "session_1",
      {
        message: "计算这个精确结构版本的 RDF",
        reply_to_turn_id: "turn-queued",
        ui_context: {
          active_object_refs: [
            {
              object_id: "object-exact",
              version_id: "version-exact",
              project_id: "project_1",
              object_type: "structure.crystal",
            },
          ],
          selection_refs: [],
          scientific_selections: [],
          explicit_object_refs: [
            {
              object_id: "object-exact",
              version_id: "version-exact",
              project_id: "project_1",
              object_type: "structure.crystal",
            },
          ],
          explicit_result_ids: [],
          explicit_finding_refs: [],
        },
      },
    ),
  );
  expect(
    screen.getByText(
      "原研究没有可复用的科学结果；本次继续将创建新的科学执行，历史 ResearchTurn 保持不变。",
    ),
  ).toBeInTheDocument();
  expect(mocks.resolveResearchScope).not.toHaveBeenCalled();
});

it("carries an exact persisted Result as an explicit Continue reuse candidate", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session_1", project_id: "project_1", title: "研究会话", status: "active" },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "研究会话",
    status: "active",
    messages: [],
  });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    turn_id: "turn-reusable",
    status: "CANCELED",
    action: "ANALYZE",
    plan_id: "plan-reusable",
    job_id: "job-reusable",
    total_step_count: 1,
    completed_step_count: 1,
    failed_step_count: 0,
    active_step_ids: [],
    execution_outcome: "CANCELED",
    interpretation_status: null,
    interpretation_id: null,
    steps: [],
    incremental_outputs: [],
    warnings: [],
    result_projection_pending: false,
  });
  mocks.getAgent2ResearchTurn.mockResolvedValue({
    turn_id: "turn-reusable",
    research_session_id: "session_1",
    project_id: "project_1",
    sequence_no: 2,
    parent_turn_id: null,
    status: "CANCELED",
    user_message: {
      id: "message-reusable",
      role: "user",
      content: "分析精确结构版本",
    },
    context: {
      scope: [],
      selection: [],
      scientific_selection: [],
    },
    created_at: "2026-08-30T00:00:00Z",
  });
  mocks.getAgent2ResearchTurnResult.mockResolvedValue({
    result_id: "result-readable",
    result_snapshot_id: "result-snapshot-exact",
    research_turn_id: "turn-reusable",
    research_question: "分析精确结构版本",
    execution_status: "PARTIAL",
    relevance_status: "CURRENT",
    source_object_refs: [],
    result_items: [],
    facts: [],
    figures: [],
    tables: [],
    evidence: [],
    artifacts: [],
    scientific_selections: [],
  } satisfies Agent2ResearchTurnResult);

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-reusable"
    />,
  );

  fireEvent.click(await screen.findByRole("button", { name: "继续研究" }));
  fireEvent.change(screen.getByLabelText("询问此项目中的数据"), {
    target: { value: "基于现有结果说明局限性" },
  });
  fireEvent.click(screen.getByRole("button", { name: "开始分析" }));

  await waitFor(() =>
    expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
      "project_1",
      "session_1",
      expect.objectContaining({
        reply_to_turn_id: "turn-reusable",
        ui_context: expect.objectContaining({
          explicit_result_ids: ["result-snapshot-exact"],
        }),
      }),
    ),
  );
  expect(
    screen.getByText(
      "已将精确结果 result-snapshot-exact 作为复用候选；只有问题超出其证据范围时才会规划新分析。",
    ),
  ).toBeInTheDocument();
});

it("fails closed when Continue cannot determine whether an exact Result exists", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session_1", project_id: "project_1", title: "研究会话", status: "active" },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "研究会话",
    status: "active",
    messages: [],
  });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    turn_id: "turn-result-unavailable",
    status: "FAILED",
    action: "ANALYZE",
    plan_id: "plan-unavailable",
    job_id: "job-unavailable",
    total_step_count: 1,
    completed_step_count: 0,
    failed_step_count: 1,
    active_step_ids: [],
    execution_outcome: "FAILED",
    interpretation_status: null,
    interpretation_id: null,
    steps: [],
    incremental_outputs: [],
    warnings: [],
    result_projection_pending: false,
  });
  mocks.getAgent2ResearchTurnResult.mockRejectedValue(
    new Agent2ReadError(503),
  );

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-result-unavailable"
    />,
  );

  fireEvent.click(await screen.findByRole("button", { name: "继续研究" }));
  fireEvent.change(screen.getByLabelText("询问此项目中的数据"), {
    target: { value: "继续完成尚未执行的分析" },
  });
  fireEvent.click(screen.getByRole("button", { name: "开始分析" }));

  expect(
    await screen.findByText("科学呈现暂时无法读取 (503)"),
  ).toBeInTheDocument();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.createResearchAssistantProjection).not.toHaveBeenCalled();
});

it("coalesces same-tick Research submissions before durable admission returns", async () => {
  let resolveTurn!: (value: { turn_id: string }) => void;
  const session = {
    id: "session_1",
    project_id: "project_1",
    title: "研究会话",
    status: "active",
    messages: [],
  };
  mocks.listResearchSessions.mockReset().mockResolvedValue([session]);
  mocks.getResearchSession.mockReset().mockResolvedValue(session);
  mocks.getProjectHistory.mockReset().mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{ datasetId: "dataset_a" }, { datasetId: "dataset_b" }],
    analyses: [],
  });
  mocks.createAgent2ResearchTurn.mockImplementation(
    () =>
      new Promise((resolve) => {
        resolveTurn = resolve;
      }),
  );
  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      viewerContext={{
        objectId: "object-exact",
        versionId: "version-exact",
        objectType: "structure.crystal",
      }}
    />,
  );
  const input = await screen.findByLabelText("询问此项目中的数据");
  fireEvent.change(input, { target: { value: "分析这个精确结构版本" } });
  const form = screen.getByRole("button", { name: "开始分析" }).closest("form");
  expect(form).not.toBeNull();

  fireEvent.submit(form!);
  fireEvent.submit(form!);

  await waitFor(() =>
    expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledTimes(1),
  );
  resolveTurn({ turn_id: "turn-single-flight" });
  await waitFor(() =>
    expect(mocks.routerPush).toHaveBeenCalledWith(
      "/projects/project_1/research/session_1?turn=turn-single-flight",
    ),
  );
});

it("suppresses stale dispatch errors only after a durable terminal outcome", () => {
  expect(shouldSuppressAgent2DispatchError("CANCELED")).toBe(true);
  expect(shouldSuppressAgent2DispatchError("COMPLETED")).toBe(true);
  expect(shouldSuppressAgent2DispatchError("PARTIAL")).toBe(true);
  expect(shouldSuppressAgent2DispatchError("FAILED")).toBe(true);
  expect(shouldSuppressAgent2DispatchError("PLAN_READY")).toBe(false);
  expect(shouldSuppressAgent2DispatchError("RUNNING")).toBe(false);
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

it("persists a running-turn draft in the current browser tab and restores it after reload", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session_1", project_id: "project_1", title: "研究会话", status: "active" },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "研究会话",
    status: "active",
    messages: [],
  });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    turn_id: "turn-running-draft",
    status: "RUNNING",
    action: "ANALYZE",
    plan_id: "plan-running",
    job_id: "job-running",
    total_step_count: 2,
    completed_step_count: 1,
    failed_step_count: 0,
    active_step_ids: ["step-2"],
    execution_outcome: null,
    interpretation_status: null,
    interpretation_id: null,
    steps: [],
    incremental_outputs: [],
    warnings: [],
    result_projection_pending: false,
  });

  const first = render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-running-draft"
    />,
  );
  const composer = await screen.findByLabelText("询问此项目中的数据");
  expect(
    await screen.findByText(
      /草稿仅保存在当前浏览器标签页，刷新后可恢复/,
    ),
  ).toBeInTheDocument();
  fireEvent.change(composer, {
    target: { value: "下一步比较第二个配位模型" },
  });
  await waitFor(() =>
    expect(
      window.sessionStorage.getItem(
        "mdi:research-draft:project_1:session_1:turn-running-draft",
      ),
    ).toBe("下一步比较第二个配位模型"),
  );

  first.unmount();
  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-running-draft"
    />,
  );

  expect(
    await screen.findByDisplayValue("下一步比较第二个配位模型"),
  ).toBeInTheDocument();
});

it("replaces a doomed empty-project composer with the Data import and selection entry", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "空项目", role: "owner", status: "active" },
    datasets: [],
    analyses: [],
  });
  render(<ResearchPage projectId="project_1" />);

  expect(await screen.findByRole("heading", { name: "先从项目数据开始" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "打开数据平台" })).toHaveAttribute("href", "/projects/project_1/data");
  expect(screen.queryByLabelText("询问此项目中的数据")).not.toBeInTheDocument();
});

it("fails closed when Edit-last-message cannot load the authoritative original question", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_1",
      project_id: "project_1",
      title: "研究会话",
      status: "active",
    },
  ]);
  mocks.getAgent2ResearchTurn.mockRejectedValueOnce(
    new Error("turn unavailable"),
  );
  mocks.getAgent2ResearchTurnResult.mockRejectedValueOnce(
    new Error("result unavailable"),
  );

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      editTurnId="turn-missing"
    />,
  );

  const blockedMessage = await screen.findByText(
    "原问题暂时无法读取；为避免丢失历史上下文，编辑与提交已停用。",
  );
  expect(blockedMessage.closest("[role='alert']")).toBeInTheDocument();
  const editor = screen.getByLabelText("编辑问题");
  expect(editor).toBeDisabled();
  expect(editor).toHaveAttribute("aria-describedby", "research-edit-status");
  const submit = screen.getByRole("button", { name: "开始分析" });
  expect(submit).toBeDisabled();

  fireEvent.change(editor, { target: { value: "不安全的替代问题" } });
  fireEvent.submit(editor.closest("form")!);

  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.createResearchMessage).not.toHaveBeenCalled();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
});

it("keeps the no-data starter read-only while preserving a Data navigation path for a viewer", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "共享空项目", role: "viewer", status: "active" },
    datasets: [],
    analyses: [],
  });
  render(<ResearchPage projectId="project_1" />);

  expect(await screen.findByRole("heading", { name: "这个项目还没有可研究的数据" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "查看数据平台" })).toHaveAttribute("href", "/projects/project_1/data");
  expect(screen.getByRole("note")).toHaveTextContent("此项目为只读");
  expect(screen.queryByRole("link", { name: "打开数据平台" })).not.toBeInTheDocument();
  expect(screen.queryByLabelText("询问此项目中的数据")).not.toBeInTheDocument();
});

it("prevents archived projects from importing or researching while keeping preserved Data reachable", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "已归档项目", role: "owner", status: "archived" },
    datasets: [],
    analyses: [],
  });
  render(<ResearchPage projectId="project_1" />);

  expect(await screen.findByRole("heading", { name: "这个项目已归档" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "查看保留的数据" })).toHaveAttribute("href", "/projects/project_1/data");
  expect(screen.getByRole("note")).toHaveTextContent("恢复为活跃状态后才能继续导入与研究");
  expect(screen.queryByRole("link", { name: "打开数据平台" })).not.toBeInTheDocument();
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
  expect(context).toHaveTextContent("上下文结果 1");
  expect(context).not.toHaveTextContent("internal-result-id");
  expect(context).not.toHaveTextContent("constraint-id");
});

it("lets users remove a pinned result without exposing its internal identity", async () => {
  const user = userEvent.setup();
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session_1", project_id: "project_1", title: "连续研究", status: "active" },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "连续研究",
    status: "active",
    messages: [],
  });
  mocks.getAgent2SessionMemory.mockResolvedValue({
    session_id: "session_1",
    project_id: "project_1",
    pinned_object_refs: [],
    pinned_result_refs: ["internal-result-id"],
    session_constraints: [],
    active_research_goal: null,
    version: 1,
  });
  mocks.unpinAgent2Result.mockResolvedValue({
    session_id: "session_1",
    project_id: "project_1",
    pinned_object_refs: [],
    pinned_result_refs: [],
    session_constraints: [],
    active_research_goal: null,
    version: 2,
  });
  render(<ResearchPage projectId="project_1" sessionId="session_1" />);

  const context = await screen.findByRole("region", { name: "当前研究会话上下文" });
  const remove = await within(context).findByRole("button", { name: "从本会话上下文移除结果 1" });
  await user.click(remove);
  await waitFor(() =>
    expect(mocks.unpinAgent2Result).toHaveBeenCalledWith(
      "project_1",
      "session_1",
      "internal-result-id",
    ),
  );
  expect(context).not.toHaveTextContent("internal-result-id");
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

it("starts a fresh scoped research session from an explicit dataset handoff", async () => {
  const user = userEvent.setup();
  mocks.listResearchSessions.mockResolvedValue([
    { id: "old_session", project_id: "project_1", title: "旧研究", status: "active" },
  ]);
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" />);

  const composer = await screen.findByLabelText("询问此项目中的数据");
  await user.type(composer, "请比较该 XRD 数据中的峰位与强度并给出来源");
  await user.click(screen.getByRole("button", { name: "开始分析" }));

  await waitFor(() =>
    expect(mocks.createResearchSession).toHaveBeenCalledWith(
      "project_1",
      expect.stringContaining("请比较该 XRD 数据"),
      "dataset_selected",
    ),
  );
  await waitFor(() =>
    expect(mocks.createPlannerJob).toHaveBeenCalledWith(
      expect.objectContaining({
        projectId: "project_1",
        datasetId: "dataset_selected",
        profileId: "profile_selected",
        researchSessionId: "session_1",
        enqueue: true,
      }),
    ),
  );
  expect(mocks.resolveResearchScope).not.toHaveBeenCalled();
  expect(mocks.getResearchSession).not.toHaveBeenCalledWith("old_session");
  expect(mocks.createResearchMessage).toHaveBeenCalledWith(
    "session_1",
    "请比较该 XRD 数据中的峰位与强度并给出来源",
    "dataset_selected",
  );
});

it("uses one authoritative Agent2 message for a promoted Dataset table handoff", async () => {
  const user = userEvent.setup();
  mocks.getDatasetSourceResources.mockResolvedValue([
    {
      objectId: "resource_table",
      objectType: "DataFrame",
      datasetId: "dataset_selected",
      payload: [],
    },
  ]);
  mocks.promoteDatasetTable.mockResolvedValue({
    object: {
      id: "object_table",
      object_type: "materials.table",
      current_version_id: "version_table",
      display_name: "材料回归表",
    },
    version: { id: "version_table" },
  });
  mocks.createAgent2ResearchTurn.mockResolvedValue({
    turn_id: "turn_dataset_table",
  });

  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" />);

  const composer = await screen.findByLabelText("询问此项目中的数据");
  await user.type(composer, "评估预测值相对真实值的回归误差");
  await user.click(screen.getByRole("button", { name: "开始分析" }));

  await waitFor(() =>
    expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
      "project_1",
      "session_1",
      expect.objectContaining({
        message: "评估预测值相对真实值的回归误差",
        ui_context: expect.objectContaining({
          active_object_refs: [
            expect.objectContaining({
              object_id: "object_table",
              version_id: "version_table",
              object_type: "materials.table",
            }),
          ],
          explicit_object_refs: [
            expect.objectContaining({
              object_id: "object_table",
              version_id: "version_table",
            }),
          ],
        }),
      }),
    ),
  );
  expect(mocks.createResearchMessage).not.toHaveBeenCalled();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
});

it("admits one exact trajectory resource and uses the modern ResearchTurn path", async () => {
  const user = userEvent.setup();
  mocks.getDataset.mockResolvedValue({
    id: "dataset_trajectory",
    datasetId: "dataset_trajectory",
    name: "未包裹锂离子轨迹",
    profileId: "profile_trajectory",
  });
  mocks.getDatasetProfile.mockResolvedValue({
    id: "profile_trajectory",
    profileId: "profile_trajectory",
    datasetId: "dataset_trajectory",
  });
  mocks.getDatasetSourceResources.mockResolvedValue([
    {
      objectId: "resource_trajectory",
      objectType: "Trajectory",
      datasetId: "dataset_trajectory",
      payload: {},
    },
  ]);
  mocks.admitDatasetResource.mockResolvedValue({
    object: {
      id: "object_trajectory",
      object_type: "trajectory.atomic",
      current_version_id: "version_trajectory",
      display_name: "未包裹锂离子轨迹",
    },
    version: { id: "version_trajectory" },
  });
  mocks.createAgent2ResearchTurn.mockResolvedValue({
    turn_id: "turn_trajectory",
  });

  render(
    <ResearchPage
      projectId="project_1"
      datasetId="dataset_trajectory"
    />,
  );
  const composer = await screen.findByLabelText("询问此项目中的数据");
  await user.type(
    composer,
    "在 1 ps 到 6 ps 的拟合窗口内计算 MSD 并评估扩散性质",
  );
  await user.click(screen.getByRole("button", { name: "开始分析" }));

  await waitFor(() =>
    expect(mocks.admitDatasetResource).toHaveBeenCalledWith(
      "project_1",
      "dataset_trajectory",
      "resource_trajectory",
      "未包裹锂离子轨迹",
    ),
  );
  expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
    "project_1",
    "session_1",
    expect.objectContaining({
      ui_context: expect.objectContaining({
        active_object_refs: [
          expect.objectContaining({
            object_id: "object_trajectory",
            version_id: "version_trajectory",
            object_type: "trajectory.atomic",
          }),
        ],
        explicit_object_refs: [
          expect.objectContaining({
            object_id: "object_trajectory",
            version_id: "version_trajectory",
          }),
        ],
      }),
    }),
  );
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  expect(mocks.createResearchMessage).not.toHaveBeenCalled();
});

it("keeps an exact object handoff out of archived or existing sessions", async () => {
  const user = userEvent.setup();
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "archived_session",
      project_id: "project_1",
      title: "已归档历史研究",
      status: "archived",
    },
    {
      id: "active_session",
      project_id: "project_1",
      title: "其他当前研究",
      status: "active",
    },
  ]);
  mocks.createAgent2ResearchTurn.mockResolvedValue({
    turn_id: "turn_exact_structure",
  });

  render(
    <ResearchPage
      projectId="project_1"
      viewerContext={{
        objectId: "object_structure",
        versionId: "version_structure_v2",
        objectType: "structure.crystal",
        displayName: "Si 精确结构",
      }}
    />,
  );

  const composer = await screen.findByLabelText("询问此项目中的数据");
  expect(mocks.getResearchSession).not.toHaveBeenCalledWith("archived_session");
  expect(mocks.getResearchSession).not.toHaveBeenCalledWith("active_session");

  await user.type(composer, "比较 CrystalNN 与 VoronoiNN 的局域配位结果");
  await user.click(screen.getByRole("button", { name: "开始分析" }));

  await waitFor(() =>
    expect(mocks.createResearchSession).toHaveBeenCalledWith(
      "project_1",
      expect.stringContaining("比较 CrystalNN"),
      undefined,
    ),
  );
  expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
    "project_1",
    "session_1",
    expect.objectContaining({
      ui_context: expect.objectContaining({
        active_object_refs: [
          expect.objectContaining({
            object_id: "object_structure",
            version_id: "version_structure_v2",
          }),
        ],
        explicit_object_refs: [
          expect.objectContaining({
            object_id: "object_structure",
            version_id: "version_structure_v2",
          }),
        ],
      }),
    }),
  );
});

it("treats new=1 as a clean research route instead of reopening recent work", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "active_session",
      project_id: "project_1",
      title: "最近研究",
      status: "active",
    },
  ]);

  render(<ResearchPage projectId="project_1" fresh />);

  expect(await screen.findByLabelText("询问此项目中的数据")).toBeInTheDocument();
  expect(mocks.getResearchSession).not.toHaveBeenCalledWith("active_session");
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
  expect(trigger).not.toHaveAttribute("aria-controls");
  await user.click(trigger);
  expect(trigger).toHaveAttribute("aria-controls", "research-session-history");
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
  expect(trigger).not.toHaveAttribute("aria-controls");

  await user.click(trigger);
  expect(await screen.findByRole("searchbox", { name: "搜索研究记录" })).toHaveValue("");
  await user.click(screen.getByRole("heading", { name: "研究时间线" }));
  expect(screen.queryByRole("dialog", { name: "研究记录" })).not.toBeInTheDocument();
});

it("organizes research records with current, archived and trash views", async () => {
  const user = userEvent.setup();
  let records = {
    session_active: {
      id: "session_active",
      project_id: "project_1",
      title: "可管理研究",
      status: "active",
      pinned: false,
    },
    session_archived: {
      id: "session_archived",
      project_id: "project_1",
      title: "已归档研究",
      status: "archived",
      pinned: false,
    },
    session_trashed: {
      id: "session_trashed",
      project_id: "project_1",
      title: "已回收研究",
      status: "trashed",
      pinned: false,
    },
  };
  mocks.listResearchSessions.mockResolvedValue([
    records.session_active,
    records.session_archived,
    records.session_trashed,
  ]);
  mocks.updateResearchSession.mockImplementation(
    async (
      id: keyof typeof records,
      changes: { lifecycle?: string; pinned?: boolean; title?: string },
    ) => {
      const current = records[id];
      const updated = {
        ...current,
        ...(changes.title ? { title: changes.title } : {}),
        ...(changes.pinned !== undefined ? { pinned: changes.pinned } : {}),
        ...(changes.lifecycle
          ? { status: changes.lifecycle.toLowerCase() }
          : {}),
      };
      records = { ...records, [id]: updated };
      return updated;
    },
  );
  vi.spyOn(window, "confirm").mockReturnValue(true);
  render(<ResearchPage projectId="project_1" />);
  await user.click(await screen.findByRole("button", { name: "研究记录" }));

  expect(screen.getByRole("button", { name: "当前 1" })).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  expect(screen.getByText("可管理研究")).toBeInTheDocument();
  expect(screen.queryByText("已归档研究")).not.toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "管理 可管理研究" }));
  await user.click(screen.getByRole("menuitem", { name: "列表置顶" }));
  expect(mocks.updateResearchSession).toHaveBeenCalledWith("session_active", {
    pinned: true,
  });
  expect(await screen.findByText("列表置顶 · 可继续")).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "管理 可管理研究" }));
  await user.click(screen.getByRole("menuitem", { name: "重命名" }));
  const rename = screen.getByRole("textbox", { name: "研究名称" });
  await user.clear(rename);
  await user.type(rename, "硅结构复核");
  await user.click(screen.getByRole("button", { name: "保存名称" }));
  expect(mocks.updateResearchSession).toHaveBeenCalledWith("session_active", {
    title: "硅结构复核",
  });

  await user.click(screen.getByRole("button", { name: "研究记录" }));
  await user.click(screen.getByRole("button", { name: "管理 硅结构复核" }));
  await user.click(screen.getByRole("menuitem", { name: "归档" }));
  expect(mocks.updateResearchSession).toHaveBeenCalledWith("session_active", {
    lifecycle: "ARCHIVED",
  });
  expect(screen.queryByText("硅结构复核")).not.toBeInTheDocument();
  await waitFor(() =>
    expect(document.activeElement).toBe(
      screen.getByRole("button", { name: "当前 0" }),
    ),
  );
  expect(screen.getByText("“硅结构复核”已归档。")).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "已归档 2" }));
  expect(await screen.findByText("硅结构复核")).toBeInTheDocument();
  expect(screen.getByText("已归档研究")).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "回收站 1" }));
  expect(await screen.findByText("已回收研究")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "管理 已回收研究" }));
  await user.click(screen.getByRole("menuitem", { name: "恢复研究记录" }));
  expect(mocks.updateResearchSession).toHaveBeenCalledWith("session_trashed", {
    lifecycle: "ACTIVE",
  });
  await waitFor(() =>
    expect(document.activeElement).toBe(
      screen.getByRole("button", { name: "回收站 0" }),
    ),
  );
  expect(screen.getByText("“已回收研究”已恢复。")).toBeInTheDocument();
});

it("names the research status filters and supports directional keyboard selection", async () => {
  const user = userEvent.setup();
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_active",
      project_id: "project_1",
      title: "当前研究",
      status: "active",
    },
    {
      id: "session_archived",
      project_id: "project_1",
      title: "归档研究",
      status: "archived",
    },
    {
      id: "session_trashed",
      project_id: "project_1",
      title: "回收研究",
      status: "trashed",
    },
  ]);
  render(<ResearchPage projectId="project_1" />);
  await user.click(await screen.findByRole("button", { name: "研究记录" }));

  const filters = screen.getByRole("group", { name: "研究记录状态" });
  const current = within(filters).getByRole("button", { name: "当前 1" });
  const archived = within(filters).getByRole("button", { name: "已归档 1" });
  const trashed = within(filters).getByRole("button", { name: "回收站 1" });
  current.focus();

  await user.keyboard("{ArrowRight}");
  expect(archived).toHaveFocus();
  expect(archived).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByText("归档研究")).toBeInTheDocument();

  await user.keyboard("{End}");
  expect(trashed).toHaveFocus();
  expect(trashed).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByText("回收研究")).toBeInTheDocument();

  await user.keyboard("{ArrowRight}");
  expect(current).toHaveFocus();
  expect(current).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByText("当前研究")).toBeInTheDocument();
});

it("applies research record bulk actions through one atomic project request", async () => {
  const user = userEvent.setup();
  let records = [
    {
      id: "session_bulk_one",
      project_id: "project_1",
      title: "批量研究一",
      status: "active",
      pinned: false,
    },
    {
      id: "session_bulk_two",
      project_id: "project_1",
      title: "批量研究二",
      status: "active",
      pinned: false,
    },
  ];
  mocks.listResearchSessions.mockImplementation(async () => records);
  mocks.bulkUpdateResearchSessions.mockImplementation(
    async (
      _projectId: string,
      sessionIds: string[],
      action: "ARCHIVE" | "RESTORE" | "TRASH" | "PIN" | "UNPIN",
    ) => {
      records = records.map((record) =>
        sessionIds.includes(record.id)
          ? {
              ...record,
              status:
                action === "ARCHIVE"
                  ? "archived"
                  : action === "TRASH"
                    ? "trashed"
                    : action === "RESTORE"
                      ? "active"
                      : record.status,
              pinned:
                action === "PIN"
                  ? true
                  : action === "UNPIN"
                    ? false
                    : record.pinned,
            }
          : record,
      );
      return { action, sessionIds, count: sessionIds.length };
    },
  );
  vi.spyOn(window, "confirm").mockReturnValue(true);

  render(<ResearchPage projectId="project_1" />);
  await user.click(await screen.findByRole("button", { name: "研究记录" }));
  await user.click(screen.getByRole("button", { name: "批量管理" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 批量研究一" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 批量研究二" }));
  expect(screen.getByText("2 项已选")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "归档所选" }));

  await waitFor(() =>
    expect(mocks.bulkUpdateResearchSessions).toHaveBeenCalledWith(
      "project_1",
      ["session_bulk_one", "session_bulk_two"],
      "ARCHIVE",
    ),
  );
  expect(mocks.bulkUpdateResearchSessions).toHaveBeenCalledTimes(1);
  expect(mocks.updateResearchSession).not.toHaveBeenCalled();
  expect(screen.getByText("当前没有可继续的研究记录。")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "已归档 2" }));
  expect(await screen.findByText("批量研究一")).toBeInTheDocument();
  expect(screen.getByText("批量研究二")).toBeInTheDocument();
});

it("keeps an archived session readable with separate new and restore actions", async () => {
  const user = userEvent.setup();
  const archived = {
    id: "session_archived",
    project_id: "project_1",
    title: "历史结构研究",
    status: "archived",
    pinned: false,
    messages: [
      {
        id: "message_historical",
        session_id: "session_archived",
        role: "user",
        content: "查看历史结构结果",
        created_at: "2026-08-20T00:00:00Z",
      },
    ],
  };
  mocks.listResearchSessions.mockResolvedValue([archived]);
  mocks.getResearchSession.mockResolvedValue(archived);
  mocks.updateResearchSession.mockImplementation(
    async (_id: string, changes: { lifecycle?: string }) => ({
      ...archived,
      status: changes.lifecycle?.toLowerCase() || archived.status,
    }),
  );

  render(<ResearchPage projectId="project_1" sessionId="session_archived" />);

  expect(await screen.findByRole("heading", { name: "研究时间线" })).toBeInTheDocument();
  expect(screen.getByText("历史结构研究")).toBeInTheDocument();
  expect(screen.getByText("已归档")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "开始新的研究" })).toHaveAttribute(
    "href",
    "/projects/project_1/research?new=1",
  );
  expect(screen.getByRole("button", { name: "恢复原会话" })).toBeInTheDocument();
  expect(screen.queryByLabelText("询问此项目中的数据")).not.toBeInTheDocument();
  expect(
    screen.getByText("历史对话、科学结果和精确来源仍可查看。可以开始新的研究，或恢复原会话后继续。"),
  ).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "恢复原会话" }));
  expect(mocks.updateResearchSession).toHaveBeenCalledWith("session_archived", {
    lifecycle: "ACTIVE",
  });
  expect(await screen.findByLabelText("询问此项目中的数据")).toBeInTheDocument();
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

it("uses authoritative Turn status for history and keeps project identity visible", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "声子验证项目", role: "owner" },
    datasets: [],
    analyses: [
      {
        jobId: "job_completed_but_turn_failed",
        researchSessionId: "session_history",
        researchTurnId: "turn_failed",
        researchTurnStatus: "FAILED",
        status: "completed",
        userQuestion: "比较声子带与态密度",
        toolIds: ["phonon.band", "phonon.dos"],
        stepCount: 2,
        artifactCount: 14,
        artifactTypes: ["plotly_json", "table_json"],
        interpretationCount: 0,
        reportCount: 0,
        recipeCount: 0,
      },
    ],
  });

  render(<ResearchPage projectId="project_1" />);

  expect(
    await screen.findByText("声子验证项目 · 研究时间线"),
  ).toBeInTheDocument();
  expect(screen.getByText("分析失败")).toBeInTheDocument();
  expect(screen.getByText("2 个步骤 · 查看过程")).toBeInTheDocument();
  expect(screen.queryByText("✓ 分析完成")).not.toBeInTheDocument();
  expect(
    screen.getByRole("region", { name: "历史研究" }),
  ).toBeInTheDocument();
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

it("keeps branch navigation with the conversation timeline instead of scientific results", async () => {
  const user = userEvent.setup();
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_branch",
      project_id: "project_1",
      title: "扩散研究分支",
      status: "active",
      messages: [],
    },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_branch",
    project_id: "project_1",
    title: "扩散研究分支",
    status: "active",
    messages: [],
  });
  mocks.listAgent2ResearchTurns.mockResolvedValue([
    {
      id: "turn_root",
      turn_id: "turn_root",
      research_session_id: "session_branch",
      project_id: "project_1",
      sequence_no: 1,
      parent_turn_id: null,
      status: "COMPLETED",
      user_message: {
        id: "message_root",
        role: "user",
        content: "计算 MSD",
      },
      created_at: "2026-08-31T00:00:00Z",
    },
    {
      id: "turn_branch",
      turn_id: "turn_branch",
      research_session_id: "session_branch",
      project_id: "project_1",
      sequence_no: 2,
      parent_turn_id: "turn_root",
      status: "COMPLETED",
      user_message: {
        id: "message_branch",
        role: "user",
        content: "限定 1–6 ps 重新评估扩散",
      },
      created_at: "2026-08-31T00:01:00Z",
    },
  ]);

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_branch"
      agent2TurnId="turn_branch"
    />,
  );

  const timeline = await screen.findByRole("tabpanel", { name: "对话" });
  const workbench = screen.getByRole("tabpanel", { name: "工作台" });
  const branchNavigation = await within(timeline).findByRole("navigation", {
    name: "研究分支",
  });
  expect(branchNavigation).toHaveTextContent("2 / 2");
  expect(branchNavigation).toHaveTextContent("限定 1–6 ps 重新评估扩散");
  expect(branchNavigation).toHaveTextContent("源自“计算 MSD”");
  expect(
    within(branchNavigation).getByRole("link", {
      name: "上一个研究分支：计算 MSD",
    }),
  ).toHaveAttribute(
    "href",
    "/projects/project_1/research/session_branch?turn=turn_root",
  );
  await user.click(
    within(branchNavigation).getByText("查看全部 2 个分支"),
  );
  expect(
    within(branchNavigation).getByRole("link", { name: /1\. 计算 MSD/ }),
  ).toHaveAttribute(
    "href",
    "/projects/project_1/research/session_branch?turn=turn_root",
  );
  const currentBranch = within(branchNavigation).getByRole("link", {
    name: /2\. 限定 1–6 ps 重新评估扩散/,
  });
  expect(currentBranch).toHaveAttribute("aria-current", "page");
  expect(currentBranch).toHaveTextContent("ResearchTurn turn_branch");
  expect(currentBranch).toHaveTextContent("消息修订 message_branch");
  expect(
    within(workbench).queryByRole("navigation", { name: "研究分支" }),
  ).not.toBeInTheDocument();
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
  // Scientific viewers are intentionally lazy-loaded so the research shell
  // and persisted result metadata remain interactive while the heavy renderer
  // is fetched. Await the deferred renderer instead of coupling this test to
  // a synchronous dynamic-import timing.
  expect(await screen.findByTestId("scientific-result-viewer")).toBeInTheDocument();
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

it("honors an explicit session id when a historical run is not yet bound to it", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    {
      id: "session_explicit",
      project_id: "project_1",
      title: "当前研究",
      status: "completed",
      messages: [],
    },
    {
      id: "session_other",
      project_id: "project_1",
      title: "其他研究",
      status: "active",
      messages: [],
    },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_explicit",
    project_id: "project_1",
    title: "当前研究",
    status: "completed",
    messages: [],
  });
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [],
    analyses: [
      {
        jobId: "job_unbound",
        status: "completed",
        userQuestion: "新完成的研究",
        stepCount: 2,
        artifactCount: 1,
      },
    ],
  });
  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_explicit"
      runId="job_unbound"
    />,
  );

  await waitFor(() =>
    expect(mocks.getResearchSession).toHaveBeenCalledWith("session_explicit"),
  );
  expect(
    screen.queryByText("研究会话不存在或已不可访问。"),
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

it("reopens the latest immutable interpretation instead of the oldest snapshot", async () => {
  const owner = {
    id: "session_owner",
    project_id: "project_1",
    title: "扩散研究",
    status: "completed",
    messages: [],
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
        interpretationId: "interpretation_old",
        completeness: "PARTIAL",
        claims: [],
        globalLimitations: ["旧解释缺少拟合窗依据。"],
      },
      {
        interpretationId: "interpretation_latest",
        completeness: "COMPLETE",
        claims: [],
        globalLimitations: [],
      },
    ],
  });

  render(<ResearchPage projectId="project_1" runId="job_owned" />);

  await waitFor(() =>
    expect(mocks.getPlannerInterpretationEvidence).toHaveBeenCalledWith(
      "interpretation_latest",
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

it("uses the persisted session Dataset for follow-up research instead of reopening project-wide ambiguity", async () => {
  const user = userEvent.setup();
  const trajectorySession = {
    id: "session_trajectory",
    project_id: "project_1",
    dataset_id: "dataset_trajectory",
    datasetId: "dataset_trajectory",
    title: "轨迹研究",
    status: "active",
    messages: [],
  };
  mocks.listResearchSessions.mockResolvedValue([trajectorySession]);
  mocks.getResearchSession.mockResolvedValue(trajectorySession);
  mocks.getDataset.mockResolvedValue({
    id: "dataset_trajectory",
    datasetId: "dataset_trajectory",
    name: "轨迹数据",
    profileId: "profile_trajectory",
  });
  mocks.getDatasetProfile.mockResolvedValue({
    id: "profile_trajectory",
    profileId: "profile_trajectory",
    datasetId: "dataset_trajectory",
  });
  mocks.getDatasetSourceResources.mockResolvedValue([]);
  mocks.createResearchMessage.mockResolvedValue({
    id: "message_follow_up",
    session_id: "session_trajectory",
    role: "user",
    content: "计算 MSD",
    created_at: "2026-08-31T00:00:00Z",
  });
  mocks.createPlannerJob.mockResolvedValue({
    ok: true,
    job_id: "job_msd",
    plan_hash: "b".repeat(64),
    plan: {
      goal: "计算 MSD",
      datasetId: "dataset_trajectory",
      steps: [],
    },
  });

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_trajectory"
    />,
  );
  const composer = await screen.findByLabelText("询问此项目中的数据");
  await user.type(composer, "计算 MSD");
  await user.click(screen.getByRole("button", { name: "开始分析" }));

  await waitFor(() =>
    expect(mocks.createPlannerJob).toHaveBeenCalledWith(
      expect.objectContaining({ datasetId: "dataset_trajectory" }),
    ),
  );
  expect(mocks.resolveResearchScope).not.toHaveBeenCalled();
  expect(mocks.createResearchMessage).toHaveBeenCalledWith(
    "session_trajectory",
    "计算 MSD",
    "dataset_trajectory",
  );
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

it("renders a diffusion-window clarification without coordination controls", async () => {
  const user = userEvent.setup();
  mocks.resolveResearchScope.mockResolvedValue({
    status: "READY",
    dataset_id: "dataset_trajectory",
    profile_id: "profile_trajectory",
    dataset_name: "未包裹轨迹",
  });
  mocks.createPlannerJob.mockResolvedValue({
    ok: false,
    error_code: "VALIDATION_FAILED",
    capability_outcome: "NEEDS_CLARIFICATION",
    validation_errors: [
      {
        code: "DIFFUSION_FIT_WINDOW_REQUIRED",
        message: "Diffusion planning requires an explicit fit window.",
      },
    ],
  });

  render(<ResearchPage projectId="project_1" />);
  const composer = await screen.findByLabelText("询问此项目中的数据");
  await user.type(composer, "计算当前轨迹的 MSD 与扩散系数。");
  await user.click(screen.getByRole("button", { name: "开始分析" }));

  expect(
    await screen.findByRole("heading", {
      name: "扩散估计需要明确拟合时间窗。",
    }),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("button", { name: "使用完整时间范围" }),
  ).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "仅计算 MSD" })).toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: "使用 CrystalNN" }),
  ).not.toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: "使用 VoronoiNN" }),
  ).not.toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "使用完整时间范围" }));
  expect((composer as HTMLTextAreaElement).value).toContain(
    "完整提供的时间范围",
  );
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

it("keeps a persisted scientific final readable without rendering the raw machine contract", () => {
  const rendered = displayResearchMessage({
    id: "agent2-final",
    session_id: "session",
    role: "assistant",
    created_at: "2026-08-31T00:00:00Z",
    payload: { messageKind: "ASSISTANT_FINAL" },
    content: "联合分析电子能带与态密度来源\nBand 结果提供了带隙事实 fact.band，值为 0.6 eV，单位 eV。该事实来自证据 evidence.band。Band 结果提供了 k 点计数事实 fact.k，值为 3（单位 count）。\n- Band 结果提供了带隙事实 fact.band，值为 0.6 eV，单位 eV。该事实来自证据 evidence.band。\n- Band 结果提供了 k 点计数事实 fact.k，值为 3（单位 count）。\n限制：\n- Band values are supplied electronic data.",
  });
  expect(rendered).toBe(
    "Band 结果提供了带隙事实，值为 0.6 eV，单位 eV。Band 结果提供了 k 点计数事实，值为 3（单位 count）。\n\n完整结构化结果已在右侧工作台提供。",
  );
  expect(rendered).not.toContain("Band values are supplied electronic data");
  expect(rendered).not.toContain("限制：");
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
  expect(
    groundedEvidenceNarrative(
      evidence([
        ["trajectory.msd.last_lag", "11.5 picosecond"],
        ["trajectory.msd.last_total", "0.641793 angstrom^2"],
        ["trajectory.diffusion.fit_start", "1 picosecond"],
        ["trajectory.diffusion.fit_end", "6 picosecond"],
        ["trajectory.diffusion.fit_points", "11"],
        ["trajectory.diffusion.estimate", "0.0386181 angstrom^2/picosecond"],
        ["trajectory.diffusion.r_squared", "0.970302"],
        ["trajectory.diffusion.alpha", "0.924032"],
        ["trajectory.diffusion.status", "DIFFUSIVE_WINDOW_ACCEPTED"],
      ]),
    ),
  ).toEqual({
    finding:
      "在 1 ps 到 6 ps 内，限定扩散系数为 0.0386181 Å^2/ps（11 个拟合点，R² = 0.970302，α = 0.924032）；轨迹末端 11.5 ps 的总 MSD 为 0.641793 Å^2。",
    limitation:
      "该扩散系数只对用户显式选择的拟合窗口、当前轨迹与采样条件有效，不是无条件的长时间体扩散系数。",
  });
  expect(
    groundedEvidenceNarrative(
      evidence([
        ["trajectory.msd.last_lag", "0.003 picosecond"],
        ["trajectory.msd.last_total", "0.0009 angstrom^2"],
      ]),
    ),
  ).toEqual({
    finding: "在 0.003 ps 的末端时滞处，总 MSD 为 0.0009 Å^2。",
    limitation:
      "当前结果仅报告 MSD，未执行扩散系数估算；MSD 解释仅适用于当前轨迹、时间窗和采样条件。",
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

it("exposes a bounded, navigable provenance summary for evidence rows", () => {
  expect(
    evidenceProvenanceSummary({
      sourceArtifactId: "artifact-rdf-1",
      sourceArtifactChecksum: "a".repeat(64),
      sourceToolId: "tool-rdf",
      fieldLocator: { fieldId: "trajectory.rdf.included_frames" },
    }),
  ).toBe(
    `字段 trajectory.rdf.included_frames · Artifact artifact-rdf-1 · ToolCall tool-rdf · SHA-256 ${"a".repeat(64)}`,
  );
});
