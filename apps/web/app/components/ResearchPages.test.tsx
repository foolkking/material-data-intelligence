import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
afterEach(() => vi.useRealTimers());

import {
  Agent2AdmissionUnconfirmedError,
  Agent2ReadError,
  type Agent2ResearchTurnResult,
  type Agent2ContextManifest,
  type Agent2TurnDetail,
} from "../lib/agent2-research-api";
import type { InterpretationEvidenceResponse, ProjectHistory } from "../lib/planner-api";
import { Agent2ExecutionRequestError } from "../lib/agent2-execution-api";
import { recoverResearchSessionCreation } from "../lib/research-session-creation";
import { encodeWorkspaceSelectionUrl, validateWorkspaceSelectionContext } from "../../shared/workspace/workspace-selection-contract";
import trajectoryFixture from "../../../../tests/fixtures/trajectory_viewer/fixed_lattice_md_12_frames.json";
import {
  researchComposerDraftKey,
  CONTEXT_MANIFEST_RENDER_WINDOW,
  contextManifestRenderItems,
  evidenceProvenanceSummary,
} from "./ResearchPages";

const mocks = vi.hoisted(() => ({
  getScientificViewerProjection: vi.fn(),
  getUserModels: vi.fn(),
  routerPush: vi.fn(),
  createResearchMessage: vi.fn(),
  createResearchAssistantProjection: vi.fn(),
  createResearchSession: vi.fn(),
  getDataset: vi.fn(),
  getDatasetProfile: vi.fn(),
  getDatasetSourceResources: vi.fn(),
  getDatasetResearchSources: vi.fn(),
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
  createAgent2AdmissionKey: vi.fn(() => "m4-01-test-admission-key"),
  getAgent2ResearchTurn: vi.fn(),
  getAgent2ResearchTurnResult: vi.fn(),
  presentationProps: vi.fn(),
}));

vi.mock("../lib/scientific-viewer-api", () => ({getScientificViewerProjection:mocks.getScientificViewerProjection}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mocks.routerPush,
    replace: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

vi.mock("../lib/user-models-api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../lib/user-models-api")>()),
  getUserModels: mocks.getUserModels,
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
  PlannerApiError: class PlannerApiError extends Error {
    readonly status: number;
    readonly details: unknown;

    constructor(message: string, status: number, details: unknown) {
      super(message);
      this.name = "PlannerApiError";
      this.status = status;
      this.details = details;
    }
  },
  createPlannerJob: mocks.createPlannerJob,
  createPlannerJobInterpretation: mocks.createPlannerJobInterpretation,
  getDataset: mocks.getDataset,
  getDatasetProfile: mocks.getDatasetProfile,
  getDatasetSourceResources: mocks.getDatasetSourceResources,
  getDatasetResearchSources: mocks.getDatasetResearchSources,
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

vi.mock("../lib/agent2-memory-api", async (importOriginal) => ({
  ...await importOriginal<typeof import("../lib/agent2-memory-api")>(),
  getAgent2SessionMemory: mocks.getAgent2SessionMemory,
  unpinAgent2Object: mocks.unpinAgent2Object,
  unpinAgent2Result: mocks.unpinAgent2Result,
}));
vi.mock("../lib/agent2-execution-api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../lib/agent2-execution-api")>()),
  getAgent2ExecutionProgress: mocks.getAgent2ExecutionProgress,
  cancelAgent2Execution: mocks.cancelAgent2Execution,
}));
vi.mock("../lib/agent2-research-api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../lib/agent2-research-api")>()),
  getAgent2ContextManifest: mocks.getAgent2ContextManifest,
  listAgent2ResearchTurns: mocks.listAgent2ResearchTurns,
  dispatchAgent2ResearchTurn: mocks.dispatchAgent2ResearchTurn,
  createAgent2ResearchTurn: mocks.createAgent2ResearchTurn,
  createAgent2AdmissionKey: mocks.createAgent2AdmissionKey,
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
  Agent2ScientificPresentation: (props: { turnId: string }) => {
    mocks.presentationProps(props);
    return <section aria-label="权威 ResearchTurn 科学呈现">Turn {props.turnId}</section>;
  },
}));

import {
  agent2ContextManifestForTurn,
  agent2ContinueInput,
  agent2ProgressHasFreshSessionMessages,
  agent2ProgressForTurn,
  agent2ProgressNeedsRefresh,
  agent2RetryInput,
  contextOperationSequenceLabel,
  defaultResearchConversationWidth,
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
  researchWorkbenchContentAvailable,
  researchStateForAgent2Progress,
  researchStarterPrompts,
  researchTechnicalSummary,
  retryLineageForTurn,
  requestWasAborted,
  resolveAgent2TurnForRecovery,
  runProcessStepState,
  scientistDatasetLabel,
  scientistFacingResearchRequestError,
  shouldSuppressAgent2DispatchError,
  userFacingPlanStep,
} from "./ResearchPages";
import { PlannerApiError } from "../lib/planner-api";

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

it("gives the research question more space until scientific workbench content exists", () => {
  expect(defaultResearchConversationWidth(false)).toBe(720);
  expect(defaultResearchConversationWidth(true)).toBe(420);
  expect(defaultResearchConversationWidth(true, 1100)).toBe(440);
  expect(defaultResearchConversationWidth(true, 1700)).toBe(640);
  expect(
    researchWorkbenchContentAvailable({
      job: { ok: true, job_id: "job-only", plan: null },
      artifacts: [],
      interpretation: null,
      evidence: null,
      events: [],
      agent2Progress: null,
    }),
  ).toBe(false);
  expect(researchWorkbenchContentAvailable({
    job: null, artifacts: [], interpretation: null, evidence: null, events: [],
    agent2Progress: { contract_version: "1.0", turn_id: "turn-failed", status: "FAILED", steps: [], warnings: [], incremental_outputs: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, result_projection_pending: false },
  })).toBe(false);
  for (const status of ["ORCHESTRATING", "ANSWERED", "NEEDS_CLARIFICATION", "UNSUPPORTED", "PLANNING", "RUNNING"] as const) {
    expect(researchWorkbenchContentAvailable({
      job: null, artifacts: [], interpretation: null, evidence: null, events: [],
      agent2Progress: { contract_version: "1.0", turn_id: "plain-status", status, steps: [], warnings: [], incremental_outputs: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, result_projection_pending: false },
    })).toBe(false);
  }
  expect(researchWorkbenchContentAvailable({
    job: null, artifacts: [], interpretation: null, evidence: null, events: [],
    agent2Progress: { contract_version: "1.0", turn_id: "saved-result", status: "FAILED", preserved_result_available: true, steps: [], warnings: [], incremental_outputs: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, result_projection_pending: false },
  })).toBe(true);
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

it("deduplicates by durable identity without removing identical retry questions", () => {
  const base = (id: string, role: "user" | "assistant", content: string) => ({
    id,
    session_id: "session-1",
    role,
    content,
    created_at: "2026-08-31T00:00:00Z",
  });
  const deduped = dedupeResearchTimelineMessages([
    base("u-1", "user", "同一个问题"),
    base("u-1", "user", "同一个问题"),
    base("u-2", "user", "同一个问题"),
    base("a-1", "assistant", "回答"),
    base("u-3", "user", "同一个问题"),
    base("u-4", "user", "同一个问题"),
  ]);
  expect(deduped.map((item) => item.id)).toEqual(["u-1", "u-2", "a-1", "u-3", "u-4"]);
  expect(researchMessageWindow(deduped, "u-1").visible.map((item) => item.id)).toEqual(["u-1"]);
  expect(researchMessageWindow(deduped, "u-2").visible.map((item) => item.id)).toEqual(["u-2", "a-1"]);
});

it("keeps asynchronous answers with their owning branch even when completion order differs", () => {
  const messages = [
    { id: "original", role: "user", content: "问题" },
    { id: "retry", role: "user", content: "问题" },
    { id: "late-original-answer", role: "assistant", content: "原分支回答" },
    { id: "retry-answer", role: "assistant", content: "重试回答" },
  ].map((message) => ({ ...message, session_id: "session", created_at: "2026-10-06T00:00:00Z" })) as Parameters<typeof researchMessageWindow>[0];
  expect(researchMessageWindow(messages, "original", false, 10, 0, ["original", "late-original-answer"]).visible.map((item) => item.id)).toEqual(["original", "late-original-answer"]);
  expect(researchMessageWindow(messages, "retry", false, 10, 0, ["retry", "retry-answer"]).visible.map((item) => item.id)).toEqual(["retry", "retry-answer"]);
  expect(researchMessageWindow(messages, "original", false, 10, 0, ["original"]).visible.map((item) => item.id)).toEqual(["original"]);
  expect(researchMessageWindow(messages, "unloaded", false, 10, 0, ["unloaded"]).visible).toEqual([]);
  expect(researchMessageWindow(messages, "retry", true, 10, 0, ["retry", "retry-answer"]).visible).toHaveLength(4);
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

it.each(["DOWNSTREAM_ACKNOWLEDGEMENT", "ASSISTANT_PRE_RUN"])("keeps %s process acknowledgements out of the scientific conversation", (messageKind) => {
  expect(
    researchMessageVisibleInTimeline({
      id: "message-process",
      session_id: "session-1",
      role: "assistant",
      content: "provider candidate that has not been grounded",
      payload: { messageKind },
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
  const chained = [{ ...turns[0], id: "ancestor", turn_id: "ancestor", sequence_no: 0 }, ...turns.map((turn) => turn.id === "root" ? { ...turn, parent_turn_id: "ancestor" } : turn)];
  expect(researchBranchNavigation(chained, "root", "root")).toMatchObject({ rootId: "root", currentIndex: 0, previous: null, next: { id: "branch-a" } });
  expect(researchBranchChoices(chained, "root", "root").map((turn) => turn.id)).toEqual(["root", "branch-a", "branch-b"]);
  expect(researchBranchNavigation(chained, "root", "branch-b")).toMatchObject({ rootId: "ancestor", currentIndex: 1, next: null });
  expect(researchBranchNavigation(chained, "root", "unrelated")).toMatchObject({ rootId: "ancestor" });
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
  mocks.getUserModels.mockResolvedValue({
    label: "我的模型服务", baseUrl: "", protocol: "openai_chat_json", secretConfigured: false,
    catalog: [{ provider: "system:deepseek", model: "deepseek-v4-flash" }],
    selected: [{ provider: "system:deepseek", model: "deepseek-v4-flash" }], revision: 1,
  });
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
  mocks.createResearchMessage.mockReset()
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
  mocks.getAgent2ContextManifest.mockReset().mockResolvedValue(null);
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
  mocks.getAgent2ResearchTurnResult.mockRejectedValue(new Agent2ReadError(404));
});

it.each(["new", "continue", "edit"])("submits exact cross-dataset materials for %s while preserving branch identity", async mode => {
  const refs = ["si", "cu"].map(id => ({ project_id: "project_1", object_id: id, version_id: `exact-${id}`, object_type: "structure.crystal", display_name: `${id}.cif` }));
  const selected = { items: refs.map((ref, i) => ({ ref, datasetId: `dataset-${i}` })), selections: [] };
  const oldRef = { ...refs[0], object_id: "old", version_id: "old-version" };
  mocks.getAgent2ResearchTurn.mockResolvedValue({ turn_id: "original", project_id: "project_1", research_session_id: "session_1", user_message: { content: "旧问题" }, context: { scope: [oldRef], selection: [], scientific_selection: [] } });
  mocks.getAgent2ResearchTurnResult.mockResolvedValue({ research_turn_id: "original", result_id: "old-result", source_object_refs: [oldRef], scientific_selections: [] });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "original", status: "COMPLETED", steps: [], warnings: [], incremental_outputs: [] });
  const turnKey = mode === "new" ? undefined : mode === "edit" ? "edit:original" : "original";
  const draftKey = researchComposerDraftKey("project_1", "session_1", turnKey);
  sessionStorage.setItem(`${draftKey}:materials`, JSON.stringify(selected));
  const continuationKey = `${researchComposerDraftKey("project_1", "session_1", "original")}:materials`;
  if (mode === "edit") sessionStorage.setItem(continuationKey, JSON.stringify({ items: [{ ref: oldRef }], selections: [] }));
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId={mode === "new" ? undefined : "original"} editTurnId={mode === "edit" ? "original" : undefined} />);
  const composer = await screen.findByLabelText(mode === "edit" ? "编辑问题" : "研究问题");
  fireEvent.change(composer, { target: { value: "分别分析 Si 和 Cu 的 RDF" } });
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalled());
  const input = mocks.createAgent2ResearchTurn.mock.calls[0][2];
  expect(input.ui_context).toMatchObject({ active_object_refs: refs, explicit_object_refs: refs, scientific_selections: [], explicit_result_ids: [] });
  expect(input.reply_to_turn_id).toBe(mode === "new" ? undefined : "original");
  expect(mocks.getDatasetSourceResources).not.toHaveBeenCalled(); expect(mocks.resolveResearchScope).not.toHaveBeenCalled();
  await waitFor(() => expect(sessionStorage.getItem(`${draftKey}:materials`)).toBeNull());
  expect(sessionStorage.getItem(draftKey)).toBeNull();
  if (mode === "edit") expect(JSON.parse(sessionStorage.getItem(continuationKey)!)).toEqual({ items: [{ ref: oldRef }], selections: [] });
});

it.each(["ANSWERED", "NEEDS_CLARIFICATION", "UNSUPPORTED", "PLAN_REJECTED"])("continues a %s Turn with its exact material when the API has no scientific result", async status => {
  const ref = { project_id: "project_1", object_id: "si", version_id: "exact-si", object_type: "structure.crystal", display_name: "Si.cif" };
  mocks.getAgent2ResearchTurn.mockResolvedValue({ turn_id: "original", project_id: "project_1", research_session_id: "session_1", status,
    user_message: { content: "原问题" }, context: { scope: [ref], selection: [ref], scientific_selection: [] } });
  mocks.getAgent2ResearchTurnResult.mockRejectedValue(new Agent2ReadError(409, "SCIENTIFIC_RESULT_NOT_READY"));
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "original", status, steps: [], warnings: [], incremental_outputs: [] });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="original" />);
  const composer = await screen.findByLabelText("研究问题");
  fireEvent.change(composer, { target: { value: "请说明可以执行哪些计算" } });
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledOnce());
  expect(mocks.createAgent2ResearchTurn.mock.calls[0][2]).toMatchObject({
    message: "请说明可以执行哪些计算", reply_to_turn_id: "original",
    ui_context: { active_object_refs: [ref], explicit_object_refs: [ref], explicit_result_ids: [] },
  });
  expect(mocks.routerPush).toHaveBeenCalledWith("/projects/project_1/research/session_1?turn=turn-new");
  expect(mocks.resolveResearchScope).not.toHaveBeenCalled();
});

it.each([
  ["FAILED", "continue"], ["CANCELED", "continue"], ["FAILED", "edit"], ["CANCELED", "edit"],
])("recovers a %s Turn with no scientific result for %s using its original sources", async (status, mode) => {
  const refs = ["si", "cu"].map(id => ({ project_id: "project_1", object_id: id, version_id: `exact-${id}`, object_type: "structure.crystal", display_name: `${id}.cif` }));
  mocks.getAgent2ResearchTurn.mockResolvedValue({ turn_id: "original", project_id: "project_1", research_session_id: "session_1", status,
    user_message: { content: "分别分析 Si 和 Cu" }, context: { scope: refs, selection: refs, scientific_selection: [] } });
  mocks.getAgent2ResearchTurnResult.mockRejectedValue(new Agent2ReadError(404));
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "original", status, steps: [], warnings: [], incremental_outputs: [] });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="original" editTurnId={mode === "edit" ? "original" : undefined} />);
  const composer = await screen.findByLabelText(mode === "edit" ? "编辑问题" : "研究问题");
  if (mode === "edit") await waitFor(() => expect(composer).toHaveValue("分别分析 Si 和 Cu"));
  fireEvent.change(composer, { target: { value: "说明这两个材料可用的计算" } });
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledOnce());
  expect(mocks.createAgent2ResearchTurn.mock.calls[0][2]).toMatchObject({
    message: "说明这两个材料可用的计算", reply_to_turn_id: "original",
    ui_context: { active_object_refs: refs, explicit_object_refs: refs, explicit_result_ids: [] },
  });
  expect(mocks.resolveResearchScope).not.toHaveBeenCalled();
  expect(mocks.getDatasetSourceResources).not.toHaveBeenCalled();
});

it("keeps exact material selection and question after rejected admission", async () => {
  const key = researchComposerDraftKey("project_1", "session_1", undefined);
  const value = { items: [{ datasetId: "d", ref: { project_id: "project_1", object_id: "si", version_id: "exact", object_type: "structure.crystal", display_name: "Si.cif" } }], selections: [] };
  sessionStorage.setItem(`${key}:materials`, JSON.stringify(value));
  mocks.createAgent2ResearchTurn.mockRejectedValue(new Error("temporarily unavailable"));
  render(<ResearchPage projectId="project_1" sessionId="session_1" />);
  const composer = await screen.findByLabelText("研究问题");
  fireEvent.change(composer, { target: { value: "分析 Si" } });
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  expect(composer).toHaveValue("分析 Si");
  expect(JSON.parse(sessionStorage.getItem(`${key}:materials`)!)).toEqual(value);
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
    await screen.findByRole("button", { name: "重新运行分析" }),
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
  expect(mocks.getAgent2ResearchTurn).toHaveBeenCalledWith("turn-failed", { signal: expect.any(AbortSignal) });
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
  expect(lineage).toHaveTextContent("本次为重新分析");
  expect(lineage).not.toHaveTextContent("ResearchTurn");
  expect(lineage).not.toHaveTextContent("lineage");
  expect(
    within(lineage).getByRole("link", { name: "查看原分析" }),
  ).toHaveAttribute(
    "href",
    "/projects/project_1/research/session_1?turn=turn-failed",
  );
  expect(within(lineage).getByText("turn-retry")).toBeInTheDocument();
  expect(within(lineage).getByText("turn-failed")).toBeInTheDocument();
});

it.each(["COMPLETED", "ANSWERED"] as const)("restores the latest owned %s Turn beside a session landing conversation without moving its draft", async status => {
  mocks.listResearchSessions.mockResolvedValue([{ id: "session_1", project_id: "project_1", title: "已保存研究", status: "active" }]);
  mocks.listAgent2ResearchTurns.mockResolvedValue([1, 3, 2].map(sequence => ({
    turn_id: `saved-${sequence}`, research_session_id: "session_1", project_id: "project_1", sequence_no: sequence, status,
    user_message: { id: `message-${sequence}`, role: "user", content: `问题 ${sequence}` }, created_at: "2026-10-08T00:00:00Z",
  })));
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "saved-3", status, completed_step_count: 0, total_step_count: 0,
    steps: [], incremental_outputs: [], warnings: [] });
  const key = researchComposerDraftKey("project_1", "session_1", undefined);
  sessionStorage.setItem(key!, "保留未发送的问题");
  render(<ResearchPage projectId="project_1" />);
  const results = await screen.findByRole("tabpanel", { name: "结果" });
  expect(await within(results).findByRole("link", { name: "打开这次研究" })).toHaveAttribute("href", "/projects/project_1/research/session_1?turn=saved-3");
  if (status === "COMPLETED") {
    expect(await within(results).findByRole("region", { name: "权威 ResearchTurn 科学呈现" })).toHaveTextContent("saved-3");
    expect(mocks.presentationProps).toHaveBeenLastCalledWith(expect.objectContaining({ turnId: "saved-3", canModify: false }));
  } else expect(await within(results).findByRole("heading", { name: "本次没有新的科学结果" })).toBeInTheDocument();
  expect(screen.getByRole("region", { name: "项目研究工作台" })).toHaveAttribute("data-workbench-open", String(status === "COMPLETED"));
  expect(within(results).queryByRole("heading", { name: "可用数据" })).not.toBeInTheDocument();
  expect(screen.getByLabelText("研究问题")).toHaveValue("保留未发送的问题");
  expect(sessionStorage.getItem(key!)).toBe("保留未发送的问题");
  expect(mocks.routerPush).not.toHaveBeenCalled();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.dispatchAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.getAgent2ExecutionProgress.mock.calls.every(([id]) => id === "saved-3")).toBe(true);
});

it("uses one authoritative completed ResearchTurn presentation without rendering the legacy workbench result twice", async () => {
  const messages = [
    { id: "question", role: "user" as const, content: "生成一条函数曲线。" },
    { id: "ack", role: "assistant" as const, content: "将生成函数曲线。", payload: { messageKind: "ASSISTANT_PRE_RUN", turnId: "turn-complete" } },
    { id: "answer", role: "assistant" as const, content: "已生成曲线，含 41 个采样点。", payload: { messageKind: "ASSISTANT_FINAL", source: "agent2_scientific_interpreter", responseFormat: "markdown", turnId: "turn-complete" } },
  ].map(message => ({ ...message, session_id: "session_1", created_at: "2026-10-10T00:00:00Z" }));
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session_1", project_id: "project_1", title: "研究会话", status: "active" },
  ]);
  mocks.getResearchSession.mockResolvedValue({
    id: "session_1",
    project_id: "project_1",
    title: "研究会话",
    status: "active",
    messages,
  });
  mocks.listAgent2ResearchTurns.mockResolvedValue([{
    turn_id: "turn-complete", research_session_id: "session_1", project_id: "project_1", sequence_no: 1,
    status: "COMPLETED", user_message: messages[0], message_ids: messages.map(message => message.id), created_at: "2026-10-10T00:00:00Z",
  }]);
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
  const conversation = screen.getByRole("log", { name: "研究对话" });
  expect(await within(conversation).findByText("已生成曲线，含 41 个采样点。")).toBeVisible();
  expect(within(conversation).queryByText("将生成函数曲线。")).not.toBeInTheDocument();
  expect(within(conversation).getAllByRole("article", { name: "研究助手消息" })).toHaveLength(1);
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

it.each([
  [401, "登录状态已过期，请重新登录后读取研究进度。"],
  [403, "当前账号无权读取这项研究，请确认项目访问权限。"],
  [404, "找不到这项研究记录，请从研究列表确认记录是否仍可访问。"],
  [410, "这项研究记录已不可用，请从研究列表查看其他记录。"],
] as const)("explains HTTP %s progress unavailability and rereads without resubmitting", async (status, message) => {
  mocks.getAgent2ExecutionProgress.mockRejectedValueOnce(new Agent2ExecutionRequestError("sensitive upstream detail", status))
    .mockResolvedValue({ contract_version: "1.0", turn_id: "turn-access", status: "RUNNING", steps: [], active_step_ids: [], completed_step_count: 0,
      total_step_count: 1, incremental_outputs: [], warnings: [], result_projection_pending: false });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-access" />);
  expect(await screen.findByText(message)).toBeVisible();
  const notice = screen.getByRole("status", { name: "研究进度提示" });
  expect(notice.parentElement).toBe(screen.getByRole("region", { name: "项目研究工作台" }));
  expect(notice.closest('[role="tabpanel"]')).toBeNull();
  expect(screen.queryByText(/sensitive upstream detail|研究执行失败/)).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "重新读取进度" }));
  await waitFor(() => expect(screen.queryByText(message)).not.toBeInTheDocument());
  expect(mocks.getAgent2ExecutionProgress).toHaveBeenCalledTimes(2);
  expect(mocks.getAgent2ExecutionProgress.mock.calls.every(([id]) => id === "turn-access")).toBe(true);
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it.each(["ANSWERED", "NEEDS_CLARIFICATION", "UNSUPPORTED", "PLAN_REJECTED", "RESULT_PENDING", "RUNNING", "QUEUED", "PLANNING"])("keeps the %s Turn result surface separate from the project catalogue", async (status) => {
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-results", status, steps: [], active_step_ids: [], completed_step_count: 0,
    total_step_count: 1, incremental_outputs: [], warnings: [], result_projection_pending: status === "RESULT_PENDING" });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-results" />);
  await screen.findByRole("region", { name: "分析进度" });
  const results = screen.getByRole("tabpanel", { name: "结果" });
  expect(within(results).queryByRole("heading", { name: "可用数据" })).not.toBeInTheDocument();
  expect(within(results).queryByText("已选择的数据", { exact: false })).not.toBeInTheDocument();
  expect(within(results).getByRole("button", { name: "查看研究时间线" })).toBeInTheDocument();
});

it.each(["available", "unavailable"])("keeps unread Turn results unconfirmed with project history %s", async history => {
  let reject!: (reason: unknown) => void;
  mocks.getAgent2ExecutionProgress.mockImplementationOnce(() => new Promise((_, fail) => { reject = fail; }));
  if (history === "unavailable") mocks.getProjectHistory.mockRejectedValue(new Error("history unavailable"));
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-results" />);
  const results = await screen.findByRole("tabpanel", { name: "结果" });
  expect(await within(results).findByRole("heading", { name: "正在读取本次结果状态…" })).toBeInTheDocument();
  await waitFor(() => expect(reject).toBeDefined());
  await act(async () => reject(new Agent2ExecutionRequestError("private server detail", 403)));
  expect(await within(results).findByRole("heading", { name: "结果状态尚未确认" })).toBeInTheDocument();
  expect(results).not.toHaveTextContent(/可用数据|项目数据暂时无法读取|本次没有新的科学结果|private server detail/);
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-results", status: "ANSWERED", steps: [], active_step_ids: [],
    completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], result_projection_pending: false });
  fireEvent.click(screen.getByRole("button", { name: "重新读取进度" }));
  expect(await within(results).findByRole("heading", { name: "本次没有新的科学结果" })).toBeInTheDocument();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it.each(["RUNNING", "RESULT_PENDING"])("opens committed %s output only for the selected Turn", async status => {
  const output = { output_key: "rdf", step_id: "step-rdf", artifact_id: "rdf-1", display_label: "Si 径向分布函数原始数据",
    preview_available: false, available_at: "2026-10-07", content_url: "/api/planner/jobs/job-1/artifacts/rdf-1/content" };
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-results", status, steps: [], active_step_ids: [],
    completed_step_count: 1, total_step_count: 2, incremental_outputs: [output,
      { ...output, output_key: "foreign", display_label: "外部文件", content_url: "https://untrusted.invalid/file" },
      { ...output, output_key: "missing", display_label: "缺少文件地址", content_url: undefined }], warnings: [], result_projection_pending: status === "RESULT_PENDING" });
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-results" />);
  const results = await screen.findByRole("tabpanel", { name: "结果" });
  const link = await within(results).findByRole("link", { name: output.display_label });
  expect(link).toHaveAttribute("href", output.content_url);
  expect(link).toHaveAttribute("target", "_blank");
  expect(link).toHaveAttribute("rel", "noopener noreferrer");
  expect(results).not.toHaveTextContent(/外部文件|缺少文件地址|可用数据/);
  mocks.getAgent2ExecutionProgress.mockImplementation(() => new Promise(() => undefined));
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-other" />);
  expect(within(results).queryByRole("link", { name: output.display_label })).not.toBeInTheDocument();
  expect(within(results).getByRole("heading", { name: "正在读取本次结果状态…" })).toBeInTheDocument();
});

it.each([false, true])("opens the Turn timeline without stealing a later focus: %s", async movesFocus => {
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-results", status: "ANSWERED", steps: [], active_step_ids: [],
    completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], result_projection_pending: false });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-results" />);
  await screen.findByRole("region", { name: "分析进度" });
  fireEvent.click(screen.getByRole("tab", { name: "工作台" }));
  const callbacks: FrameRequestCallback[] = [];
  const frame = vi.spyOn(window, "requestAnimationFrame").mockImplementation(callback => { callbacks.push(callback); return callbacks.length; });
  try {
    const open = screen.getByRole("button", { name: "查看研究时间线" });
    open.focus(); fireEvent.click(open);
    const input = screen.getByLabelText("研究问题");
    if (movesFocus) input.focus();
    act(() => callbacks.forEach(callback => callback(0)));
    expect(screen.getByRole("tab", { name: "对话" })).toHaveAttribute("aria-selected", "true");
    if (movesFocus) expect(input).toHaveFocus();
    else expect(screen.getByRole("region", { name: "分析进度" })).toHaveFocus();
  } finally { frame.mockRestore(); }
});

it("shows transport interruption without marking durable work failed, then reconciles the same Turn", async () => {
  mocks.getAgent2ExecutionProgress
    .mockRejectedValueOnce(new TypeError("Failed to fetch"))
    .mockResolvedValue({
      contract_version: "1.0",
      turn_id: "turn-restart",
      status: "COMPLETED",
      response_kind: "SCIENTIFIC_EXECUTION",
      completed_step_count: 1,
      total_step_count: 1,
      active_step_ids: [],
      steps: [],
      incremental_outputs: [],
      warnings: [],
      execution_outcome: "SUCCESS",
      result_projection_pending: false,
    });

  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-restart"
    />,
  );

  expect(
    await screen.findByText(/研究进度暂时无法读取，请重试/),
  ).toBeInTheDocument();
  expect(screen.queryByText("研究执行失败")).not.toBeInTheDocument();
  window.dispatchEvent(new Event("online"));
  await waitFor(() => {
    expect(mocks.getAgent2ExecutionProgress).toHaveBeenCalledTimes(2);
  });
  await waitFor(() => {
    expect(
      screen.queryByText(/研究进度暂时无法读取，请重试/),
    ).not.toBeInTheDocument();
  });
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.getAgent2ExecutionProgress.mock.calls[1][0]).toBe(
    "turn-restart",
  );
});

it("presents used context as researcher-facing provenance with technical identity behind disclosure", async () => {
  mocks.listResearchSessions.mockResolvedValue([
    { id: "session_1", project_id: "project_1", title: "研究会话", status: "active" },
  ]);
  mocks.getAgent2ContextManifest.mockResolvedValue({
    turn_id: "turn-complete",
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
          context_role: "SUBJECT",
          support_eligible: false,
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
          context_role: "EVIDENCE",
          support_eligible: true,
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
  const contextDetails = disclosure.closest("details");
  expect(contextDetails).not.toHaveAttribute("open");
  const user = userEvent.setup();
  await user.click(screen.getByRole("button", { name: "本次上下文" }));
  await waitFor(() => expect(contextDetails).toHaveAttribute("open"));
  await waitFor(() => expect(disclosure.closest("summary")).toHaveFocus());
  const panel = screen.getByRole("tabpanel", { name: "上下文" });
  expect(panel).toContainElement(contextDetails);
  expect(within(panel).getByRole("link", { name: "打开数据" })).toHaveAttribute("href", "/projects/project_1/data?object=object-1&version=version-1");
  expect(within(panel).getByRole("combobox", { name: "调用阶段" })).toBeInTheDocument();
  expect(within(panel).queryByText("当前科学范围")).not.toBeInTheDocument();
  expect(within(panel).queryByText("不作为独立科学依据")).not.toBeInTheDocument();
  const technical = within(panel).getByText("技术详情").closest("details");
  expect(technical).not.toHaveAttribute("open");
  expect(technical).toHaveTextContent("version-1");
  expect(technical).toHaveTextContent("result-extra-9");
  const contextTrigger = screen.getByRole("button", { name: "本次上下文" });
  await waitFor(() => expect(contextTrigger).toHaveAttribute("aria-expanded", "true"));
  await userEvent.setup().click(contextTrigger);
  expect(contextDetails).not.toHaveAttribute("open");
  expect(contextTrigger).toHaveAttribute("aria-expanded", "false");
  await userEvent.setup().click(contextTrigger);
  await waitFor(() => expect(disclosure.closest("summary")).toHaveFocus());
  await userEvent.setup().keyboard("{Escape}");
  expect(contextDetails).not.toHaveAttribute("open");
  await waitFor(() => expect(contextTrigger).toHaveFocus());
});

it("opens the exact referenced result in the workbench without submitting another analysis", async () => {
  mocks.getAgent2ContextManifest.mockResolvedValue({
    turn_id: "turn-context-result", manifest: {
      context_manifest_id: "manifest-result", operation: "ORCHESTRATOR", project_id: "project_1",
      research_session_id: "session_1", research_turn_id: "turn-context-result", excluded_items: [],
      included_items: [{ item_id: "result_1", kind: "SCIENTIFIC_RESULT", authorization_checked: true,
        provider_opaque_ref: "result_1", result_ref: "snapshot-rdf", server_side_source_identity: "snapshot-rdf" }],
      serialized_input: { research_context: { results: [{ ref_key: "result_1", title: "Si RDF" }] } },
    }, result_sources: [{ result_snapshot_id: "snapshot-rdf", project_id: "project_1", research_session_id: "source-session", research_turn_id: "source-turn" }],
  });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-context-result", status: "ANSWERED",
    steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [] });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-context-result" />);
  await screen.findByText("本次研究使用的上下文");
  fireEvent.click(screen.getByRole("button", { name: "本次上下文" }));
  const link = await screen.findByRole("link", { name: "打开结果：Si RDF" });
  expect(link).toHaveAttribute("href", "/projects/project_1/research/source-session?turn=source-turn");
  const preventNativeNavigation = (event: Event) => event.preventDefault();
  document.addEventListener("click", preventNativeNavigation);
  try {
    fireEvent.click(link, { ctrlKey: true });
    expect(screen.getByRole("tab", { name: "上下文" })).toHaveAttribute("aria-selected", "true");
    fireEvent.click(link);
  } finally { document.removeEventListener("click", preventNativeNavigation); }
  expect(screen.getByRole("tab", { name: "结果" })).toHaveAttribute("aria-selected", "true");
  expect(screen.getByRole("tab", { name: "工作台" })).toHaveAttribute("aria-selected", "true");
  expect(screen.getByRole("tab", { name: "结果" })).toHaveFocus();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.dispatchAgent2ResearchTurn).not.toHaveBeenCalled();
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
  mocks.getAgent2ContextManifest.mockRejectedValue(new Error("temporarily unavailable"));
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
  await user.click(screen.getByRole("button", { name: "本次上下文" }));
  const readsBeforeRetry = mocks.getAgent2ContextManifest.mock.calls.length;
  mocks.getAgent2ContextManifest.mockResolvedValue({ turn_id: "turn-context-retry", manifest });
  await user.click(screen.getByRole("button", { name: "重新读取上下文" }));
  expect(
    await screen.findByText("本次研究使用的上下文"),
  ).toBeInTheDocument();
  expect(mocks.getAgent2ContextManifest).toHaveBeenCalledTimes(readsBeforeRetry + 1);
  await waitFor(() => expect(screen.getByText("本次研究使用的上下文").closest("summary")).toHaveFocus());
  expect(screen.getByText("这条记录没有保存可展示的输入内容。")).toBeInTheDocument();
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

  fireEvent.click(await screen.findByRole("button", { name: "取消当前分析" }));

  expect(
    await screen.findByText("分析在取消请求生效前已进入终态；现有科学结果未被覆盖。"),
  ).toBeInTheDocument();
  expect(screen.getByText("科学解释已准备")).toBeInTheDocument();
  expect(screen.queryByText("取消请求未能提交 (409)")).toBeNull();
});

it.each(["RUNNING", "INTERPRETING"])("turns the primary composer action into Stop while %s is active", async (status) => {
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
    status,
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
    name: "从输入区取消当前分析",
  });
  expect(screen.queryByRole("button", { name: "发送" })).toBeNull();
  fireEvent.click(primaryStop);

  await waitFor(() =>
    expect(mocks.cancelAgent2Execution).toHaveBeenCalledWith(
      "turn-primary-stop",
      { signal: expect.any(AbortSignal) },
    ),
  );
  expect(
    await screen.findByText("当前分析已取消。已经提交的有效输出仍会保留；继续当前研究不会自动重算。"),
  ).toBeInTheDocument();
});

it.each(["RUNNING", "INTERPRETING"])("keeps both %s Stop controls unconfirmed until a successful reread", async (status) => {
  const running = {
    contract_version: "1.0", turn_id: "turn-stop-unconfirmed", status,
    steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 1,
    incremental_outputs: [], warnings: [], result_projection_pending: false,
  };
  mocks.getAgent2ExecutionProgress.mockResolvedValueOnce(running).mockRejectedValue(new Error("offline"));
  mocks.cancelAgent2Execution.mockRejectedValue(new Error("unconfirmed"));
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-stop-unconfirmed" />);
  fireEvent.click(await screen.findByRole("button", { name: "取消当前分析" }));
  expect(await screen.findByRole("button", { name: "等待取消确认" })).toBeDisabled();
  expect(screen.getByRole("button", { name: "从输入区取消当前分析" })).toBeDisabled();
  expect(screen.queryByRole("button", { name: "正在提交取消…" })).toBeNull();
  expect(screen.getAllByText(/取消结果尚未确认/)).toHaveLength(1);
  mocks.getAgent2ExecutionProgress.mockResolvedValue(running);
  fireEvent.click(screen.getByRole("button", { name: "重新读取进度" }));
  expect(await screen.findByRole("button", { name: "取消当前分析" })).toBeEnabled();
  expect(mocks.cancelAgent2Execution).toHaveBeenCalledTimes(1);
});

it("does not apply an old Stop response after the selected Turn changes", async () => {
  const running = (turn_id: string) => ({
    contract_version: "1.0", turn_id, status: "RUNNING", steps: [], active_step_ids: [],
    completed_step_count: 0, total_step_count: 1, incremental_outputs: [], warnings: [], result_projection_pending: false,
  });
  mocks.getAgent2ExecutionProgress.mockImplementation(async (id) => running(id));
  let finish!: (value: unknown) => void;
  mocks.cancelAgent2Execution.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-stop-old" />);
  fireEvent.click(await screen.findByRole("button", { name: "取消当前分析" }));
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-stop-new" />);
  await screen.findByRole("button", { name: "取消当前分析" });
  await act(async () => { finish({ turn_id: "turn-stop-old", status: "CANCELED" }); });
  expect(screen.getByText("正在执行分析")).toBeInTheDocument();
  expect(screen.queryByText("分析已取消", { exact: true })).toBeNull();
  expect(mocks.cancelAgent2Execution.mock.calls[0][1].signal.aborted).toBe(true);
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

  fireEvent.click(await screen.findByRole("button", { name: "取消当前分析" }));
  expect(
    await screen.findByText("取消请求已记录，正在等待运行中的科学步骤安全结束。"),
  ).toBeInTheDocument();
  expect(
    await screen.findByText("当前分析已取消。已经提交的有效输出仍会保留；继续当前研究不会自动重算。", {}, { timeout: 3000 }),
  ).toBeInTheDocument();
  expect(screen.queryByText("取消请求已记录，正在等待运行中的科学步骤安全结束。")).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "继续当前研究" }));
  await waitFor(() => {
    expect(screen.getByLabelText("研究问题")).toHaveFocus();
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
  fireEvent.change(screen.getByLabelText("研究问题"), {
    target: { value: "计算这个精确结构版本的 RDF" },
  });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() =>
    expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
      "project_1",
      "session_1",
      {
        admission_key: "m4-01-test-admission-key",
        autonomy_mode: "STANDARD",
        message: "计算这个精确结构版本的 RDF",
        reply_to_turn_id: "turn-queued",
        model_selection: { provider: "system:deepseek", model: "deepseek-v4-flash", thinking_mode: "standard" },
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
  expect(mocks.routerPush).toHaveBeenCalledWith("/projects/project_1/research/session_1?turn=turn-new");
  expect(mocks.resolveResearchScope).not.toHaveBeenCalled();
});

it.each([true, false])("preserves exact branch context for follow-up, explicit Continue=%s", async (explicitContinue) => {
  const selectedRef = { object_id: "11111111-1111-4111-8111-111111111111", version_id: "22222222-2222-4222-8222-222222222222", project_id: "project_1", object_type: "structure.crystal" };
  const selectedSite = { contract_version: "1.0", object_ref: selectedRef, viewer_id: "scientific.structure-3d", selection_type: "PERIODIC_SITE", semantic_locator: { site_index: 0, species: "Li" }, display_label: "Li · 位点 0", evidence_locator: { site_index: 0 } };
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
      scope: [selectedRef],
      selection: [selectedRef],
      scientific_selection: [selectedSite],
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

  const continueAction = await screen.findByRole("button", { name: "继续当前研究" });
  if (explicitContinue) fireEvent.click(continueAction);
  fireEvent.change(screen.getByLabelText("研究问题"), {
    target: { value: "基于现有结果说明局限性" },
  });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));

  await waitFor(() =>
    expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
      "project_1",
      "session_1",
      expect.objectContaining({
        reply_to_turn_id: "turn-reusable",
        ui_context: expect.objectContaining({
          explicit_result_ids: ["result-snapshot-exact"],
          scientific_selections: [selectedSite],
        }),
      }),
    ),
  );
  expect(mocks.routerPush).toHaveBeenCalledWith("/projects/project_1/research/session_1?turn=turn-new");
  expect(screen.queryByText(/result-snapshot-exact/)).toBeNull();
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

  fireEvent.click(await screen.findByRole("button", { name: "继续当前研究" }));
  fireEvent.change(screen.getByLabelText("研究问题"), {
    target: { value: "继续完成尚未执行的分析" },
  });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));

  expect(
    await screen.findByText("原研究的问题或来源暂时无法确认。草稿已保留，请重新读取后再提交。"),
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
  const first = render(
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
  const input = await screen.findByLabelText("研究问题");
  fireEvent.change(input, { target: { value: "分析这个精确结构版本" } });
  const form = screen.getByRole("button", { name: "发送" }).closest("form");
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
  expect(input).toHaveValue("");
  expect(window.sessionStorage.getItem(
    "mdi:research-draft:project_1:session_1:turn-single-flight",
  )).toBeNull();

  first.unmount();
  render(
    <ResearchPage
      projectId="project_1"
      sessionId="session_1"
      agent2TurnId="turn-single-flight"
    />,
  );
  expect(await screen.findByLabelText("研究问题")).toHaveValue("");
});

it.each(["available", "blocked"])(
  "preserves a new composer draft when an earlier admission completes with %s session storage",
  async (storage) => {
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
    mocks.createAgent2ResearchTurn.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolveTurn = resolve;
        }),
    );

    const first = render(
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

    const composer = await screen.findByLabelText("研究问题");
    const storageSpies = storage === "blocked"
      ? (["getItem", "setItem", "removeItem"] as const).map((method) =>
        vi.spyOn(Storage.prototype, method).mockImplementation(() => {
          throw new DOMException("Storage is unavailable", "SecurityError");
        }),
      )
      : [];
    try {
      fireEvent.change(composer, { target: { value: "第一条分析" } });
      fireEvent.click(screen.getByRole("button", { name: "发送" }));
      await waitFor(() =>
        expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledTimes(1),
      );

      fireEvent.change(composer, { target: { value: "下一条草稿" } });
      await act(async () => resolveTurn({ turn_id: "turn-first" }));

      await waitFor(() =>
        expect(mocks.routerPush).toHaveBeenCalledWith(
          "/projects/project_1/research/session_1?turn=turn-first",
        ),
      );
      expect(composer).toHaveValue("下一条草稿");
      expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
        "project_1",
        "session_1",
        expect.objectContaining({ message: "第一条分析" }),
      );
      if (storage === "available") {
        expect(window.sessionStorage.getItem(
          "mdi:research-draft:project_1:session_1:turn-first",
        )).toBe("下一条草稿");
      }

      const admittedTurn = {
        turn_id: "turn-first",
        research_session_id: "session_1",
        project_id: "project_1",
        sequence_no: 1,
        parent_turn_id: null,
        status: "RECEIVED",
        user_message: { id: "message-first", role: "user", content: "第一条分析" },
        context: null,
        created_at: "2026-09-29T00:00:00Z",
      };
      mocks.listAgent2ResearchTurns.mockResolvedValue([admittedTurn]);
      mocks.getAgent2ResearchTurn.mockResolvedValue(admittedTurn);
      const admittedPage = (
        <ResearchPage
          projectId="project_1"
          sessionId="session_1"
          agent2TurnId="turn-first"
        />
      );
      if (storage === "available") {
        first.unmount();
        render(admittedPage);
      } else {
        first.rerender(admittedPage);
      }
      expect(await screen.findByLabelText("研究问题")).toHaveValue("下一条草稿");
      expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledTimes(1);
    } finally {
      storageSpies.forEach((spy) => spy.mockRestore());
    }
  },
);

it.each(["accepted", "rejected"])("ignores a late ordinary admission after leaving its branch: %s", async outcome => {
  let settle!: () => void;
  mocks.createAgent2ResearchTurn.mockImplementationOnce(() => new Promise((resolve, reject) => {
    settle = () => outcome === "accepted" ? resolve({ turn_id: "late-turn" }) : reject(new Error("old request failed"));
  }));
  const viewerContext = { objectId: "object-exact", versionId: "version-exact", objectType: "structure.crystal" };
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" viewerContext={viewerContext} />);
  const input = await screen.findByLabelText("研究问题");
  fireEvent.change(input, { target: { value: "旧分支问题" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledOnce());

  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-other" viewerContext={viewerContext} />);
  fireEvent.change(input, { target: { value: "新分支草稿" } });
  mocks.routerPush.mockClear();
  await act(async () => settle());
  expect(mocks.routerPush).not.toHaveBeenCalled();
  expect(input).toHaveValue("新分支草稿");
  expect(screen.queryByText(/研究请求暂时无法完成/)).not.toBeInTheDocument();
  expect(sessionStorage.getItem(researchComposerDraftKey("project_1", "session_1", "late-turn")!)).toBeNull();
  expect(screen.getByRole("button", { name: "发送" })).toBeEnabled();
});

it("retains the draft and original creation request after reopening beside another session", async () => {
  const receipts: string[] = [];
  const send = vi.fn(async (body: { creationKey: string }) => {
    receipts.push(body.creationKey);
    if (receipts.length === 1) throw new Error("Connection lost after commit");
    return { id: "recovered-session", project_id: "project_1", title: "原对话", status: "active", creationKey: body.creationKey } as never;
  });
  const create = (project: string, title: string, dataset: string | undefined, scope: string) =>
    recoverResearchSessionCreation(project, title, dataset, scope, send);
  mocks.createResearchSession.mockImplementationOnce(create).mockImplementationOnce(create);
  const view = render(<ResearchPage projectId="project_1" />);
  const input = await screen.findByLabelText("研究问题");
  fireEvent.change(input, { target: { value: "首次发送的研究问题" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await screen.findByText(/暂时无法确认新对话是否已创建/);
  expect(input).toHaveValue("首次发送的研究问题");
  expect(screen.getByRole("button", { name: "发送" })).toBeEnabled();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  view.unmount();
  mocks.listResearchSessions.mockResolvedValue([{ id: "unrelated-session", project_id: "project_1", title: "另一个窗口的对话", status: "active" }]);
  render(<ResearchPage projectId="project_1" />);
  const restored = await screen.findByLabelText("研究问题");
  await waitFor(() => expect(restored).toHaveValue("首次发送的研究问题"));
  expect(mocks.getResearchSession).not.toHaveBeenCalledWith("unrelated-session", expect.anything());
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(receipts).toHaveLength(2));
  expect(receipts[0]).toBe(receipts[1]);
});

it.each(["archived", "trashed"])("does not submit into a recovered %s session", async status => {
  mocks.createResearchSession.mockResolvedValueOnce({ id: "original-session", project_id: "project_1", title: "原对话", status });
  render(<ResearchPage projectId="project_1" viewerContext={{ objectId: "object-exact", versionId: "version-exact", objectType: "structure.crystal" }} />);
  const input = await screen.findByLabelText("研究问题");
  fireEvent.change(input, { target: { value: "保留这个问题" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await screen.findByText(/原对话已归档或在回收站/);
  expect(input).toHaveValue("保留这个问题");
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
});

it("does not attach a late newly-created session to another conversation", async () => {
  let resolve!: (value: unknown) => void;
  mocks.createResearchSession.mockImplementationOnce(() => new Promise(done => { resolve = done; }));
  const viewerContext = { objectId: "object-exact", versionId: "version-exact", objectType: "structure.crystal" };
  const view = render(<ResearchPage projectId="project_1" viewerContext={viewerContext} />);
  const input = await screen.findByLabelText("研究问题");
  fireEvent.change(input, { target: { value: "等待创建会话的问题" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createResearchSession).toHaveBeenCalledOnce());
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" viewerContext={viewerContext} />);
  await waitFor(() => expect(mocks.getResearchSession).toHaveBeenCalledWith("session_1", expect.any(AbortSignal)));
  fireEvent.change(await screen.findByLabelText("研究问题"), { target: { value: "已有会话的新草稿" } });
  await act(async () => resolve({ id: "late-session", project_id: "project_1", title: "迟到会话", status: "active", messages: [] }));
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.routerPush).not.toHaveBeenCalled();
  expect(screen.getByLabelText("研究问题")).toHaveValue("已有会话的新草稿");
  expect(sessionStorage.getItem(researchComposerDraftKey("project_1", "late-session", undefined)!)).toBeNull();
});

it("lets the new branch submit without an old response releasing its lock", async () => {
  const completions: ((value: unknown) => void)[] = [];
  mocks.createAgent2ResearchTurn.mockImplementation(() => new Promise(resolve => completions.push(resolve)));
  const viewerContext = { objectId: "object-exact", versionId: "version-exact", objectType: "structure.crystal" };
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" viewerContext={viewerContext} />);
  const input = await screen.findByLabelText("研究问题");
  fireEvent.change(input, { target: { value: "旧问题" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(completions).toHaveLength(1));
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-other" viewerContext={viewerContext} />);
  fireEvent.change(input, { target: { value: "新问题" } });
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(completions).toHaveLength(2));
  await act(async () => completions[0]({ turn_id: "late-turn" }));
  fireEvent.submit(input.closest("form")!);
  expect(completions).toHaveLength(2);
  expect(mocks.routerPush).not.toHaveBeenCalled();
  expect(screen.getByRole("button", { name: "正在准备…" })).toBeDisabled();
  await act(async () => completions[1]({ turn_id: "new-turn" }));
  expect(mocks.routerPush).toHaveBeenCalledOnce();
  expect(mocks.routerPush).toHaveBeenCalledWith("/projects/project_1/research/session_1?turn=new-turn");
  expect(input).toHaveValue("");
});

it.each(["ready", "rejected"])("does not submit a late source resolution on a different branch: %s", async outcome => {
  const source = legacyResearchSource();
  let settle!: () => void;
  mocks.getDatasetSourceResources.mockImplementationOnce(() => new Promise((resolve, reject) => {
    settle = () => outcome === "ready" ? resolve([]) : reject(new Error("source unavailable"));
  }));
  const view = render(<ResearchPage projectId="project_1" {...source} />);
  const input = await screen.findByLabelText("研究问题");
  fireEvent.change(input, { target: { value: "原问题" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.getDatasetSourceResources).toHaveBeenCalledOnce());
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-other" />);
  fireEvent.change(input, { target: { value: "新分支草稿" } });
  await act(async () => settle());
  expect(mocks.createResearchMessage).not.toHaveBeenCalled();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(input).toHaveValue("新分支草稿");
  expect(screen.queryByText(/研究请求暂时无法完成/)).not.toBeInTheDocument();
});

it.each(["route", "session"] as const)("keeps a late %s legacy admission in its original session", async entry => {
  let resolveJob!: (value: unknown) => void;
  mocks.createPlannerJob.mockImplementationOnce(() => new Promise(resolve => { resolveJob = resolve; }));
  const source = legacyResearchSource(entry);
  const view = render(<ResearchPage projectId="project_1" {...source} />);
  const input = await screen.findByLabelText("研究问题");
  fireEvent.change(input, { target: { value: "比较材料" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createPlannerJob).toHaveBeenCalledOnce());
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-other" />);
  const otherInput = await screen.findByLabelText("研究问题");
  fireEvent.change(otherInput, { target: { value: "新分支草稿" } });
  await act(async () => resolveJob({ ok: true, job_id: "late-job" }));
  expect(mocks.createResearchAssistantProjection).toHaveBeenCalledWith("session_1", expect.objectContaining({ phase: "pre_run", runId: "late-job" }));
  expect(window.location.search).not.toContain("late-job");
  expect(mocks.getPlannerJob).not.toHaveBeenCalledWith("late-job", expect.anything());
  expect(screen.queryByText("pre_run")).not.toBeInTheDocument();
  expect(otherInput).toHaveValue("新分支草稿");
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  view.rerender(<ResearchPage projectId="project_1" {...source} />);
  expect(await screen.findByLabelText("研究问题")).toHaveValue("");
});

it.each([
  ["unchanged", "available"], ["new draft", "available"],
  ["unchanged", "blocked"], ["new draft", "blocked"],
  ["unchanged", "read only"], ["new draft", "read only"],
])("restores only unsent text after returning to a background-admitted branch: %s, storage %s", async (edit, storage) => {
  let resolve!: (value: unknown) => void;
  mocks.createAgent2ResearchTurn.mockImplementationOnce(() => new Promise(done => { resolve = done; }));
  const viewerContext = { objectId: "object-exact", versionId: "version-exact", objectType: "structure.crystal" };
  const origin = <ResearchPage projectId="project_1" sessionId="session_1" viewerContext={viewerContext} />;
  const view = render(origin);
  const input = await screen.findByLabelText("研究问题");
  fireEvent.change(input, { target: { value: "已发送的原问题" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledOnce());
  const blockedMethods: ("getItem" | "setItem" | "removeItem")[] = storage === "blocked" ? ["getItem", "setItem", "removeItem"] : storage === "read only" ? ["setItem", "removeItem"] : [];
  const spies = blockedMethods.map(method => vi.spyOn(Storage.prototype, method).mockImplementation(() => { throw new DOMException("Storage unavailable", "SecurityError"); }));
  try {
    if (edit === "new draft") fireEvent.change(input, { target: { value: "原分支的下一条草稿" } });
    view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-other" viewerContext={viewerContext} />);
    fireEvent.change(input, { target: { value: "其他分支草稿" } });
    await act(async () => resolve({ turn_id: "background-turn" }));
    expect(input).toHaveValue("其他分支草稿");
    expect(mocks.routerPush).not.toHaveBeenCalled();
    view.rerender(origin);
    expect(await screen.findByLabelText("研究问题")).toHaveValue(edit === "new draft" ? "原分支的下一条草稿" : "");
    expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledOnce();
  } finally { spies.forEach(spy => spy.mockRestore()); }
});

it.each(["original", "different source", "new draft"])("reconciles a confirmed draft after remounting the %s composer", async target => {
  let resolve!: (value: unknown) => void;
  mocks.createAgent2ResearchTurn.mockImplementationOnce(() => new Promise(done => { resolve = done; }));
  const viewerContext = { objectId: "object-exact", versionId: "version-exact", objectType: "structure.crystal" };
  const first = render(<ResearchPage projectId="project_1" sessionId="session_1" viewerContext={viewerContext} />);
  fireEvent.change(await screen.findByLabelText("研究问题"), { target: { value: "已提交的问题" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledOnce());
  first.unmount();
  render(<ResearchPage projectId="project_1" sessionId="session_1" viewerContext={target === "different source" ? { ...viewerContext, objectId: "new-source" } : viewerContext} />);
  const input = await screen.findByLabelText("研究问题");
  expect(input).toHaveValue("已提交的问题");
  if (target === "new draft") fireEvent.change(input, { target: { value: "后来输入的草稿" } });
  await act(async () => resolve({ turn_id: "late-turn" }));
  expect(input).toHaveValue(target === "original" ? "" : target === "different source" ? "已提交的问题" : "后来输入的草稿");
  expect(sessionStorage.getItem(researchComposerDraftKey("project_1", "session_1", undefined))).toBe(target === "original" ? null : target === "different source" ? "已提交的问题" : "后来输入的草稿");
  expect(mocks.routerPush).not.toHaveBeenCalled();
});

it("suppresses stale dispatch errors only after a durable terminal outcome", () => {
  expect(shouldSuppressAgent2DispatchError("CANCELED")).toBe(true);
  expect(shouldSuppressAgent2DispatchError("COMPLETED")).toBe(true);
  expect(shouldSuppressAgent2DispatchError("PARTIAL")).toBe(true);
  expect(shouldSuppressAgent2DispatchError("FAILED")).toBe(true);
  expect(shouldSuppressAgent2DispatchError("PLAN_READY")).toBe(false);
  expect(shouldSuppressAgent2DispatchError("RUNNING")).toBe(false);
});

it("offers a source-free question without selecting project data or submitting", async () => {
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" />);

  expect(await screen.findByRole("region", { name: "想研究什么？" })).toBeInTheDocument();
  const suggestion = screen.getByRole("button", { name: "解释元素周期表的排列规律" });
  await user.click(suggestion);
  const composer = screen.getByLabelText("研究问题");
  expect(composer).toHaveValue("解释元素周期表的排列规律");
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
  const composer = await screen.findByLabelText("研究问题");
  expect(composer).toBeEnabled();
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

it("keeps the composer available in an empty writable project", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "空项目", role: "owner", status: "active" },
    datasets: [],
    analyses: [],
  });
  render(<ResearchPage projectId="project_1" />);

  expect(await screen.findByRole("heading", { name: "想研究什么？" })).toBeInTheDocument();
  expect(screen.getByLabelText("研究问题")).toBeEnabled();
  expect(screen.queryByText("先从项目数据开始")).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "发送" })).toBeDisabled();
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
    "原研究暂未读全。可以继续编辑草稿，重新读取后再提交。",
  );
  expect(blockedMessage.closest("[role='alert']")).toBeInTheDocument();
  const editor = screen.getByLabelText("编辑问题");
  expect(editor).toBeEnabled();
  expect(editor).toHaveAttribute("aria-describedby", "research-edit-status");
  const submit = screen.getByRole("button", { name: "发送" });
  expect(submit).toBeDisabled();

  fireEvent.change(editor, { target: { value: "不安全的替代问题" } });
  fireEvent.submit(editor.closest("form")!);

  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.createResearchMessage).not.toHaveBeenCalled();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
});

it("focuses the recovered edit composer once after opening a branch", async () => {
  let resolveTurn!: (value: unknown) => void;
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-edit", status: "FAILED", steps: [], warnings: [], incremental_outputs: [] });
  mocks.getAgent2ResearchTurn.mockImplementationOnce(() => new Promise(resolve => { resolveTurn = resolve; }));
  const user = userEvent.setup();
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-edit" />);
  await user.click(await screen.findByRole("button", { name: "修改问题并创建分支" }));
  expect(mocks.routerPush).toHaveBeenCalledWith("/projects/project_1/research/session_1?turn=turn-edit&edit=turn-edit", { scroll: false });
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-edit" editTurnId="turn-edit" />);
  const editor = await screen.findByLabelText("编辑问题");
  expect(editor).not.toHaveFocus();
  await act(async () => resolveTurn({ turn_id: "turn-edit", project_id: "project_1", research_session_id: "session_1", user_message: { content: "恢复的原问题" }, context: null }));
  await waitFor(() => expect(editor).toHaveFocus());
  expect(editor).toHaveValue("恢复的原问题");
  expect(screen.getByRole("tab", { name: "对话" })).toHaveAttribute("aria-selected", "true");
  const settings = screen.getByRole("button", { name: "研究设置" });
  settings.focus();
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-edit" editTurnId="turn-edit" />);
  expect(settings).toHaveFocus();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it.each(["initial", "retry"])("keeps focus in model settings when %s edit source loading finishes", async mode => {
  let resolveResult!: (value: unknown) => void;
  mocks.getAgent2ResearchTurn.mockResolvedValue({ turn_id: "turn-edit", project_id: "project_1", research_session_id: "session_1", user_message: { content: "原问题" }, context: null });
  if (mode === "retry") mocks.getAgent2ResearchTurnResult.mockRejectedValueOnce(new Agent2ReadError(503));
  mocks.getAgent2ResearchTurnResult.mockImplementationOnce(() => new Promise(resolve => { resolveResult = resolve; }));
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" sessionId="session_1" editTurnId="turn-edit" />);
  const editor = await screen.findByLabelText("编辑问题");
  if (mode === "retry") await user.click(await screen.findByRole("button", { name: "重新读取原研究" }));
  await user.click(screen.getByRole("button", { name: "研究设置" }));
  const model = screen.getByRole("combobox", { name: "本次分析模型" });
  model.focus();
  await act(async () => resolveResult({ research_turn_id: "turn-edit", result_id: "result-edit", source_object_refs: [], scientific_selections: [] }));
  await act(async () => { await new Promise(requestAnimationFrame); });
  expect(model).toHaveFocus();
  expect(editor).toHaveValue("原问题");
  expect(within(editor.closest("form")!).getByRole("button", { name: "发送", hidden: true })).toBeEnabled();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it("keeps the user's text selection when the original edit question arrives", async () => {
  let resolveTurn!: (value: unknown) => void;
  mocks.getAgent2ResearchTurn.mockImplementationOnce(() => new Promise(resolve => { resolveTurn = resolve; }));
  render(<ResearchPage projectId="project_1" sessionId="session_1" editTurnId="turn-edit" />);
  const editor = await screen.findByLabelText<HTMLTextAreaElement>("编辑问题");
  editor.focus();
  fireEvent.change(editor, { target: { value: "保留我选中的草稿文字" } });
  editor.setSelectionRange(2, 6);
  await act(async () => resolveTurn({ turn_id: "turn-edit", project_id: "project_1", research_session_id: "session_1", user_message: { content: "迟到的原问题" }, context: null }));
  await act(async () => { await new Promise(requestAnimationFrame); });
  expect(editor).toHaveFocus();
  expect(editor).toHaveValue("保留我选中的草稿文字");
  expect([editor.selectionStart, editor.selectionEnd]).toEqual([2, 6]);
});

it("discards scheduled edit focus after leaving that branch", async () => {
  const frames: FrameRequestCallback[] = [];
  const raf = vi.spyOn(window, "requestAnimationFrame").mockImplementation(callback => { frames.push(callback); return frames.length; });
  const cancel = vi.spyOn(window, "cancelAnimationFrame").mockImplementation(() => {});
  mocks.getAgent2ResearchTurn.mockResolvedValue({ turn_id: "turn-edit", project_id: "project_1", research_session_id: "session_1", user_message: { content: "原问题" }, context: null });
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" editTurnId="turn-edit" />);
  try {
    await screen.findByDisplayValue("原问题");
    await waitFor(() => expect(frames.length).toBeGreaterThan(0));
    const previousFrames = frames.splice(0);
    view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" />);
    await screen.findByLabelText("研究问题");
    const settings = screen.getByRole("button", { name: "研究设置" });
    settings.focus();
    act(() => previousFrames.forEach(callback => callback(0)));
    expect(settings).toHaveFocus();
  } finally { view.unmount(); raf.mockRestore(); cancel.mockRestore(); }
});

it.each(["navigation", "another control"])("does not move delayed Continue focus after %s", async action => {
  mocks.getAgent2ExecutionProgress.mockImplementation(async (turn_id: string) => ({ turn_id, status: "FAILED", steps: [], warnings: [], incremental_outputs: [] }));
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="old" />);
  const continueButton = await screen.findByRole("button", { name: "继续当前研究" });
  const frames: FrameRequestCallback[] = [];
  const raf = vi.spyOn(window, "requestAnimationFrame").mockImplementation(callback => { frames.push(callback); return frames.length; });
  try {
    continueButton.focus();
    fireEvent.click(continueButton);
    const previousFrames = frames.splice(0);
    if (action === "navigation") view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="new" />);
    const settings = screen.getByRole("button", { name: "研究设置" });
    settings.focus();
    act(() => previousFrames.forEach(callback => callback(0)));
    expect(settings).toHaveFocus();
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  } finally { view.unmount(); raf.mockRestore(); }
});

it("retains edit drafts, retries only missing source reads and submits the exact recovered context", async () => {
  const source = { project_id: "project_1", object_id: "source", version_id: "source-version", object_type: "structure.crystal" };
  mocks.getAgent2ResearchTurn.mockResolvedValue({ turn_id: "turn-edit", project_id: "project_1", research_session_id: "session_1", user_message: { content: "原问题" }, context: { scope: [source], selection: [], scientific_selection: [] } });
  mocks.getAgent2ResearchTurnResult.mockRejectedValueOnce(new Agent2ReadError(503))
    .mockResolvedValue({ research_turn_id: "turn-edit", result_id: "r", source_object_refs: [source], scientific_selections: [] });
  window.sessionStorage.setItem(researchComposerDraftKey("project_1", "session_1", "edit:turn-edit"), "已有编辑草稿");
  window.sessionStorage.setItem(researchComposerDraftKey("project_1", "session_1", "turn-edit"), "未发送的后续问题");
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-edit" editTurnId="turn-edit" />);
  const editor = await screen.findByLabelText("编辑问题");
  await waitFor(() => expect(editor).toHaveValue("已有编辑草稿"));
  expect(editor).toBeEnabled(); expect(screen.getByRole("button", { name: "发送" })).toBeDisabled();
  fireEvent.change(editor, { target: { value: "修改后的问题" } });
  await userEvent.setup().click(await screen.findByRole("button", { name: "重新读取原研究" }));
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  expect(editor).toHaveValue("修改后的问题"); await waitFor(() => expect(editor).toHaveFocus());
  expect(mocks.getAgent2ResearchTurn).toHaveBeenCalledOnce(); expect(mocks.getAgent2ResearchTurnResult).toHaveBeenCalledTimes(2);
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({
    message: "修改后的问题", reply_to_turn_id: "turn-edit", ui_context: expect.objectContaining({ explicit_object_refs: [source], explicit_result_ids: [] }),
  })));
  expect(window.sessionStorage.getItem(researchComposerDraftKey("project_1", "session_1", "turn-edit"))).toBe("未发送的后续问题");
});

it("does not overwrite a draft typed or deliberately cleared while the original question loads", async () => {
  let resolve!: (value: unknown) => void;
  mocks.getAgent2ResearchTurn.mockImplementationOnce(() => new Promise((done) => { resolve = done; }));
  render(<ResearchPage projectId="project_1" sessionId="session_1" editTurnId="turn-edit" />);
  const editor = await screen.findByLabelText("编辑问题");
  expect(editor).toBeEnabled();
  fireEvent.change(editor, { target: { value: "临时草稿" } }); fireEvent.change(editor, { target: { value: "" } });
  await act(async () => resolve({ turn_id: "turn-edit", project_id: "project_1", research_session_id: "session_1", user_message: { content: "迟到的原问题" }, context: null }));
  expect(editor).toHaveValue(""); expect(screen.getByRole("button", { name: "发送" })).toBeDisabled();
});

it("bounds Retry source loading without submitting a duplicate or a legacy error message", async () => {
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-retry", status: "FAILED", steps: [], warnings: [], incremental_outputs: [] });
  mocks.getAgent2ResearchTurn.mockImplementationOnce(() => new Promise(() => {}));
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-retry" />);
  const retry = await screen.findByRole("button", { name: "重新运行分析" });
  const composer = screen.getByLabelText("研究问题"); fireEvent.change(composer, { target: { value: "保留的后续问题" } });
  vi.useFakeTimers();
  fireEvent.click(retry); fireEvent.click(retry);
  await act(async () => { await vi.advanceTimersByTimeAsync(10_001); });
  expect(retry).toBeEnabled(); expect(composer).toHaveValue("保留的后续问题");
  expect(screen.getByText("原研究的问题或来源暂时无法确认。草稿已保留，请重新读取后再提交。")).toBeInTheDocument();
  expect(mocks.getAgent2ResearchTurn).toHaveBeenCalledOnce(); expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled(); expect(mocks.createResearchAssistantProjection).not.toHaveBeenCalled();
});

it("does not admit or navigate a retry after the user switches to another Turn", async () => {
  mocks.getAgent2ExecutionProgress.mockImplementation(async (turn_id: string) => ({ turn_id, status: "FAILED", steps: [], warnings: [], incremental_outputs: [] }));
  let resolve!: (value: unknown) => void;
  mocks.getAgent2ResearchTurn.mockImplementationOnce(() => new Promise((done) => { resolve = done; }));
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="old" />);
  fireEvent.click(await screen.findByRole("button", { name: "重新运行分析" }));
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="new" />);
  await act(async () => resolve({ turn_id: "old", project_id: "project_1", research_session_id: "session_1", user_message: { content: "旧问题" }, context: null }));
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled(); expect(mocks.routerPush).not.toHaveBeenCalled();
});

it("waits for the restored model before honoring an explicit automatic retry", async () => {
  let resolveModels!: (value: unknown) => void;
  mocks.getUserModels.mockImplementationOnce(() => new Promise((resolve) => { resolveModels = resolve; }));
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-failed", status: "FAILED", steps: [], warnings: [], incremental_outputs: [] });
  mocks.getAgent2ResearchTurn.mockResolvedValue({ turn_id: "turn-failed", project_id: "project_1", research_session_id: "session_1", user_message: { content: "原问题" }, context: null });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-failed" retryRequested />);
  await screen.findByRole("button", { name: "重新运行分析" });
  expect(mocks.getAgent2ResearchTurn).not.toHaveBeenCalled(); expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  await act(async () => resolveModels({ selected: [{ provider: "personal", model: "deepseek-v4-pro" }], label: "我的模型" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({ model_selection: { provider: "personal", model: "deepseek-v4-pro", thinking_mode: "standard" } })));
  expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledOnce();
});

it.each(["FAILED", "CANCELED"])("opens a direct %s Turn on its recovery conversation without forcing later tab choices", async (status) => {
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-failed", status, steps: [], warnings: [], incremental_outputs: [] });
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-failed" />);
  await screen.findByRole("button", { name: "重新运行分析" });
  expect(screen.getByRole("tab", { name: "对话" })).toHaveAttribute("aria-selected", "true");
  fireEvent.click(screen.getByRole("tab", { name: "工作台" }));
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-failed" />);
  expect(screen.getByRole("tab", { name: "工作台" })).toHaveAttribute("aria-selected", "true");
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
  expect(screen.queryByLabelText("研究问题")).not.toBeInTheDocument();
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
  expect(screen.queryByLabelText("研究问题")).not.toBeInTheDocument();
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
    session_id: "session_1", project_id: "project_1", pinned_object_refs: [{ project_id: "project_1", object_id: "object-1", version_id: "version-1", object_type: "structure.crystal", display_name: "LiFePO4" }],
    pinned_result_refs: ["internal-result-id"],
    session_constraints: [{ id: "constraint-id", statement: "后续 RDF cutoff 固定为 8 Å", structured_constraint: { value: 8 } }],
    active_research_goal: "比较 LiFePO4 的局域结构", version: 2,
  });
  render(<ResearchPage projectId="project_1" sessionId="session_1" />);

  await userEvent.setup().click(await screen.findByRole("button", { name: "本次上下文" }));
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

  await userEvent.setup().click(await screen.findByRole("button", { name: "本次上下文" }));
  const context = await screen.findByRole("region", { name: "当前研究会话上下文" });
  const remove = await within(context).findByRole("button", { name: "从本会话上下文移除结果 1" });
  await user.click(remove);
  await waitFor(() =>
    expect(mocks.unpinAgent2Result).toHaveBeenCalledWith(
      "project_1",
      "session_1",
      "internal-result-id",
      { signal: expect.any(AbortSignal) },
    ),
  );
  expect(context).not.toHaveTextContent("internal-result-id");
});

function legacyResearchSource(entry: "route" | "session" = "session", datasetId = "dataset_b", name = "materials-b") {
  const profileId = datasetId.replace(/^dataset_/, "profile_");
  const session = { id: "session_1", project_id: "project_1", title: "研究会话", status: "active", datasetId, dataset_id: datasetId, messages: [] };
  mocks.getResearchSession.mockResolvedValue(session);
  mocks.createResearchSession.mockResolvedValue(session);
  mocks.getDataset.mockResolvedValue({ id: datasetId, datasetId, name, profileId });
  mocks.getDatasetProfile.mockResolvedValue({ id: profileId, profileId, datasetId });
  mocks.getDatasetSourceResources.mockResolvedValue([]);
  return entry === "route" ? { datasetId } : { sessionId: session.id };
}

it.each([
  ["new", false], ["existing", false], ["new", true], ["existing", true],
])("admits an unscoped question from a %s conversation (empty project: %s)", async (entry, empty) => {
  if (empty) mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "空项目", role: "owner", status: "active" }, datasets: [], analyses: [],
  });
  render(<ResearchPage projectId="project_1" sessionId={entry === "existing" ? "session_1" : undefined} />);
  const composer = await screen.findByLabelText("研究问题");
  fireEvent.change(composer, { target: { value: "  请用 Markdown 介绍 RDF 是什么。  " } });
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledTimes(1));
  expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({
    message: "请用 Markdown 介绍 RDF 是什么。", admission_key: expect.any(String),
    model_selection: { provider: "system:deepseek", model: "deepseek-v4-flash", thinking_mode: "standard" },
    ui_context: { active_object_refs: [], selection_refs: [], explicit_object_refs: [], scientific_selections: [], explicit_result_ids: [], explicit_finding_refs: [] },
  }));
  await waitFor(() => expect(mocks.routerPush).toHaveBeenCalledWith("/projects/project_1/research/session_1?turn=turn-new"));
  expect(composer).toHaveValue("");
  expect(mocks.resolveResearchScope).not.toHaveBeenCalled();
  expect(mocks.getDatasetSourceResources).not.toHaveBeenCalled();
  expect(mocks.createResearchMessage).not.toHaveBeenCalled();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
});

it("keeps an unscoped question and model available after unconfirmed admission, then retries in the same session", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "空项目", role: "owner", status: "active" }, datasets: [], analyses: [],
  });
  mocks.createAgent2ResearchTurn.mockRejectedValueOnce(new Agent2AdmissionUnconfirmedError(503));
  render(<ResearchPage projectId="project_1" />);
  const composer = await screen.findByLabelText("研究问题");
  fireEvent.change(composer, { target: { value: "什么是 RDF？" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  expect(await screen.findByText(/无法确认本次提交状态/)).toBeVisible();
  expect(composer).toHaveValue("什么是 RDF？");
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.routerPush).toHaveBeenCalledWith("/projects/project_1/research/session_1?turn=turn-new"));
  expect(mocks.createResearchSession).toHaveBeenCalledTimes(1);
  expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledTimes(2);
  expect(mocks.createAgent2ResearchTurn.mock.calls.every(([, session, input]) => session === "session_1" && input.message === "什么是 RDF？" && input.model_selection.model === "deepseek-v4-flash")).toBe(true);
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  expect(mocks.createResearchMessage).not.toHaveBeenCalled();
  expect(composer).toHaveValue("");
});

it("retains a newer unscoped draft while the admitted question moves to its exact Turn", async () => {
  let admit!: (value: { turn_id: string }) => void;
  mocks.createAgent2ResearchTurn.mockReturnValueOnce(new Promise(resolve => { admit = resolve; }));
  render(<ResearchPage projectId="project_1" sessionId="session_1" />);
  const composer = await screen.findByLabelText("研究问题");
  fireEvent.change(composer, { target: { value: "什么是 RDF？" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledTimes(1));
  fireEvent.change(composer, { target: { value: "它与配位数有什么联系？" } });
  await act(async () => admit({ turn_id: "plain-question" }));
  expect(mocks.routerPush).toHaveBeenCalledWith("/projects/project_1/research/session_1?turn=plain-question");
  expect(composer).toHaveValue("它与配位数有什么联系？");
  expect(sessionStorage.getItem(researchComposerDraftKey("project_1", "session_1", "plain-question"))).toBe("它与配位数有什么联系？");
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
});

it.each(["route", "session"] as const)(
  "preserves a new composer draft when an earlier %s legacy Job admission completes",
  async (entry) => {
    const user = userEvent.setup();
    const submittedDraft = "  比较两个数据集  ";
    const nextDraft = "下一条草稿：分析带隙分布";
    let resolveJob!: (value: { ok: boolean; job_id: string }) => void;
    mocks.createPlannerJob.mockImplementationOnce(
      () => new Promise((resolve) => { resolveJob = resolve; }),
    );
    const source = legacyResearchSource(entry);
    render(<ResearchPage projectId="project_1" {...source} />);

    const composer = await screen.findByLabelText("研究问题");
    await user.type(composer, submittedDraft);
    await user.click(screen.getByRole("button", { name: "发送" }));
    await waitFor(() => expect(mocks.createPlannerJob).toHaveBeenCalledTimes(1));
    expect(composer).toHaveValue(submittedDraft);
    expect(mocks.getPlannerJob).not.toHaveBeenCalled();

    await user.clear(composer);
    await user.type(composer, nextDraft);
    expect(composer).toHaveValue(nextDraft);
    await act(async () => resolveJob({ ok: true, job_id: "job_1" }));

    expect(await screen.findByRole("link", { name: "打开分析报告" })).toHaveAttribute(
      "href", "/projects/project_1/reports/job_1",
    );
    expect(composer).toHaveValue(nextDraft);
    expect(mocks.createPlannerJob).toHaveBeenCalledTimes(1);
    expect(mocks.createPlannerJob).toHaveBeenCalledWith(
      expect.objectContaining({
        userPrompt: submittedDraft.trim(),
        projectId: "project_1",
        datasetId: "dataset_b",
        researchSessionId: "session_1",
      }),
    );
    expect(mocks.createResearchAssistantProjection).toHaveBeenCalledWith(
      "session_1",
      expect.objectContaining({
        phase: "pre_run",
        question: submittedDraft.trim(),
        runId: "job_1",
      }),
    );
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  },
);

it.each([
  ["route", "rejected"],
  ["route", "pending"],
  ["session", "rejected"],
  ["session", "pending"],
] as const)("tracks an admitted %s job when its introduction is %s", async (entry, outcome) => {
  const user = userEvent.setup();
  const source = legacyResearchSource(entry);
  const originalProjection = mocks.createResearchAssistantProjection.getMockImplementation()!;
  let rejectIntroduction: (reason: Error) => void = () => undefined;
  mocks.createResearchAssistantProjection.mockImplementation((sessionId, projection) => {
    if (projection.phase !== "pre_run") return originalProjection(sessionId, projection);
    if (outcome === "rejected") return Promise.reject(new Error("provider unavailable"));
    return new Promise((_, reject) => { rejectIntroduction = reject; });
  });
  render(<ResearchPage projectId="project_1" {...source} />);

  await user.type(await screen.findByLabelText("研究问题"), "比较两个数据集");
  await user.click(screen.getByRole("button", { name: "发送" }));

  await waitFor(() => expect(mocks.getPlannerJob).toHaveBeenCalledWith(
    "job_1", expect.objectContaining({ signal: expect.any(AbortSignal) }),
  ));
  expect(await screen.findByRole("link", { name: "打开分析报告" })).toHaveAttribute(
    "href", "/projects/project_1/reports/job_1",
  );
  expect(new URL(window.location.href).searchParams.get("run")).toBe("job_1");

  if (outcome === "pending") {
    // A late narrative failure must not roll a completed Job back to failed.
    await act(async () => rejectIntroduction(new Error("provider timed out")));
  }
  expect(screen.getByRole("link", { name: "打开分析报告" })).toBeInTheDocument();
  expect(mocks.createPlannerJob).toHaveBeenCalledTimes(1);
  expect(mocks.createResearchAssistantProjection).not.toHaveBeenCalledWith(
    expect.anything(), expect.objectContaining({ phase: "failed" }),
  );
  expect(screen.queryByText(/研究请求暂时无法完成/)).not.toBeInTheDocument();
  expect(screen.getByLabelText("研究问题")).toHaveValue("");
});

it("releases submission after Job completion even while its introduction is pending", async () => {
  const user = userEvent.setup();
  const source = legacyResearchSource("session", "dataset_b", "materials-b");
  const originalProjection = mocks.createResearchAssistantProjection.getMockImplementation()!;
  mocks.createResearchAssistantProjection.mockImplementation((sessionId, projection) =>
    projection.phase === "pre_run"
      ? new Promise(() => undefined)
      : originalProjection(sessionId, projection),
  );
  render(<ResearchPage projectId="project_1" {...source} />);
  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "分析带隙分布");
  await user.click(screen.getByRole("button", { name: "发送" }));
  await screen.findByRole("link", { name: "打开分析报告" });

  await user.type(composer, "再比较形成能");
  await user.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createPlannerJob).toHaveBeenCalledTimes(2));
  expect(mocks.createPlannerJob.mock.calls.map(([input]) => input.userPrompt)).toEqual([
    "分析带隙分布", "再比较形成能",
  ]);
});

it("preserves actionable clarification when its narrative cannot be saved", async () => {
  const user = userEvent.setup();
  const source = legacyResearchSource("session", "dataset_b", "materials-b");
  mocks.createPlannerJob.mockResolvedValue({
    ok: false,
    error_code: "COORDINATION_ALGORITHM_CLARIFICATION_REQUIRED",
    capability_outcome: "NEEDS_CLARIFICATION",
  });
  mocks.createResearchAssistantProjection.mockRejectedValue(new Error("write unavailable"));
  render(<ResearchPage projectId="project_1" {...source} />);
  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "分析局部环境");
  await user.click(screen.getByRole("button", { name: "发送" }));

  expect(await screen.findByRole("heading", {
    name: "局部环境分析需要选择配位算法。",
  })).toBeInTheDocument();
  expect(composer).toHaveValue("分析局部环境");
  expect(mocks.getPlannerJob).not.toHaveBeenCalled();
  expect(mocks.createResearchAssistantProjection).toHaveBeenCalledTimes(1);
  expect(screen.queryByText(/研究请求暂时无法完成/)).not.toBeInTheDocument();
});

it("starts a fresh scoped research session from an explicit dataset handoff", async () => {
  const user = userEvent.setup();
  mocks.listResearchSessions.mockResolvedValue([
    { id: "old_session", project_id: "project_1", title: "旧研究", status: "active" },
  ]);
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" />);
  expect(await screen.findByRole("note", { name: "本次研究的数据范围" })).toHaveTextContent("已指定数据集");
  expect(screen.getByRole("link", { name: "查看来源数据" })).toHaveAttribute("href", "/projects/project_1/data?dataset=dataset_selected");

  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "请比较该 XRD 数据中的峰位与强度并给出来源");
  await user.click(screen.getByRole("button", { name: "发送" }));

  await waitFor(() =>
    expect(mocks.createResearchSession).toHaveBeenCalledWith(
      "project_1",
      expect.stringContaining("请比较该 XRD 数据"),
      "dataset_selected",
      expect.stringContaining("mdi:research-pending-session:"),
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
  expect(mocks.getResearchSession).not.toHaveBeenCalledWith("old_session", expect.any(AbortSignal));
  expect(mocks.createResearchMessage).toHaveBeenCalledWith(
    "session_1",
    "请比较该 XRD 数据中的峰位与强度并给出来源",
    "dataset_selected",
  );
});

it.each(["ml-8", "dataset@version:sample-8"])("retains the selected sample %s when returning to its dataset", async (sampleRef) => {
  const token = viewerSampleToken({ datasetId: "dataset_selected", sampleRef });
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" sampleRef={sampleRef} sourceSelectionToken={token} />);
  const scope = await screen.findByRole("note", { name: "本次研究的数据范围" });
  expect(scope).toHaveTextContent("已指定 1 个样本");
  expect(scope).toHaveTextContent(sampleRef);
  const href = within(scope).getByRole("link", { name: "查看来源数据" }).getAttribute("href")!;
  const source = new URL(href, "https://mdi.example");
  expect(source.pathname).toBe("/projects/project_1/data");
  expect(source.searchParams.get("dataset")).toBe("dataset_selected");
  expect(source.searchParams.get("sample")).toBe(sampleRef);
  expect(source.searchParams.get("selection")).toBe(token);
  expect(screen.queryByText(/链接中的选择无法绑定/)).not.toBeInTheDocument();
  expect(mocks.createResearchSession).not.toHaveBeenCalled();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it.each(["projectId", "datasetId", "sampleRef", "malformed"])("drops a mismatched %s return selection without changing the research scope", async (field) => {
  const token = field === "malformed" ? "invalid-token" : viewerSampleToken({ datasetId: "dataset_selected", sampleRef: "ml-8", [field]: "foreign" });
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" sampleRef="ml-8" sourceSelectionToken={token} />);
  const scope = await screen.findByRole("note", { name: "本次研究的数据范围" });
  expect(scope).toHaveTextContent("ml-8");
  const source = new URL(within(scope).getByRole("link", { name: "查看来源数据" }).getAttribute("href")!, "https://mdi.example");
  expect(source.searchParams.get("selection")).toBeNull();
  expect(source.searchParams.get("dataset")).toBe("dataset_selected");
  expect(mocks.createResearchSession).not.toHaveBeenCalled();
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

  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "评估预测值相对真实值的回归误差");
  await user.click(screen.getByRole("button", { name: "发送" }));

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

it("retains the submitted model when dataset admission opens the canonical session route", async () => {
  const user = userEvent.setup();
  mocks.getUserModels.mockResolvedValue({ selected: [{ provider: "personal", model: "deepseek-v4-flash" }, { provider: "personal", model: "deepseek-v4-pro" }], label: "我的模型" });
  mocks.getDatasetSourceResources.mockResolvedValue([{ objectId: "resource_table", objectType: "DataFrame", datasetId: "dataset_selected", payload: [] }]);
  mocks.promoteDatasetTable.mockResolvedValue({ object: { id: "object_table", object_type: "materials.table", current_version_id: "version_table", display_name: "材料回归表" }, version: { id: "version_table" } });
  mocks.createAgent2ResearchTurn.mockResolvedValue({ turn_id: "turn_dataset_table" });
  const view = render(<ResearchPage projectId="project_1" datasetId="dataset_selected" />);
  await user.click(await screen.findByRole("button", { name: "研究设置" }));
  await user.selectOptions(screen.getByRole("combobox", { name: "本次分析模型" }), JSON.stringify(["personal", "deepseek-v4-pro"]));
  await user.selectOptions(screen.getByRole("combobox", { name: "思考深度" }), "deep");
  await user.click(screen.getByRole("checkbox", { name: "允许继续探索" }));
  await user.keyboard("{Escape}");
  await waitFor(() => expect(screen.getByRole("button", { name: "研究设置" })).toHaveFocus());
  await user.type(screen.getByLabelText("研究问题"), "评估当前表格的回归误差");
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  await user.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({ model_selection: { provider: "personal", model: "deepseek-v4-pro", thinking_mode: "deep" } })));
  view.unmount();
  mocks.getResearchSession.mockResolvedValue({ id: "session_1", project_id: "project_1", title: "回归误差", status: "active", runIds: [], messages: [] });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn_dataset_table" />);
  const trigger = await screen.findByRole("button", { name: "研究设置" });
  await waitFor(() => expect(trigger).toHaveTextContent("deepseek-v4-pro"));
  await user.click(trigger);
  expect(screen.getByRole("combobox", { name: "思考深度" })).toHaveValue("deep");
  expect(screen.getByRole("checkbox", { name: "允许继续探索" })).toBeChecked();
});

it.each([false, true])("restores unsubmitted model settings on reload (existing session: %s)", async (existingSession) => {
  const user = userEvent.setup();
  mocks.getUserModels.mockResolvedValue({ selected: [{ provider: "personal", model: "deepseek-v4-flash" }, { provider: "personal", model: "deepseek-v4-pro" }], label: "我的模型" });
  const props = existingSession ? { sessionId: "session_1" } : { datasetId: "dataset_selected" };
  const view = render(<ResearchPage projectId="project_1" {...props} />);
  await user.click(await screen.findByRole("button", { name: "研究设置" }));
  await user.selectOptions(screen.getByRole("combobox", { name: "本次分析模型" }), JSON.stringify(["personal", "deepseek-v4-pro"]));
  await user.selectOptions(screen.getByRole("combobox", { name: "思考深度" }), "deep");
  await user.click(screen.getByRole("checkbox", { name: "允许继续探索" }));
  await user.keyboard("{Escape}");
  view.unmount();

  const restored = render(<ResearchPage projectId="project_1" {...props} />);
  const trigger = await screen.findByRole("button", { name: "研究设置" });
  await waitFor(() => expect(trigger).toHaveTextContent("deepseek-v4-pro"));
  await user.click(trigger);
  expect(screen.getByRole("combobox", { name: "思考深度" })).toHaveValue("deep");
  expect(screen.getByRole("checkbox", { name: "允许继续探索" })).toBeChecked();
  await user.keyboard("{Escape}");
  restored.rerender(<ResearchPage projectId="project_1" datasetId="different_dataset" />);
  await waitFor(() => expect(screen.getByRole("button", { name: "研究设置" })).toHaveTextContent("deepseek-v4-flash"));
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it.each([
  ["ORCHESTRATOR_PROVIDER_UNAVAILABLE", "模型连接暂时不可用，请检查模型设置。"],
  ["RESEARCH_STAGE_TIMEOUT", "研究准备长时间未完成，本次请求已停止，尚未开始科学计算。原问题已保留，可以重试。"],
  ["EXECUTION_WORKER_LOST", "科学计算意外中断，本次研究未能完成。原问题和已生成的文件已保留，可以重试。"],
])("explains failed pre-execution %s and returns focus to recovery controls", async (code, message) => {
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-1", status: "FAILED", steps: [], incremental_outputs: [], warnings: [{ code, message }] });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-1" />);
  expect(await screen.findByRole("heading", { name: "尚无科学结果" })).toBeInTheDocument();
  const timeline = screen.getByRole("region", { name: "分析进度" });
  expect(timeline).toHaveTextContent(message);
  await userEvent.setup().click(screen.getByRole("button", { name: "查看研究时间线" }));
  await waitFor(() => expect(timeline).toHaveFocus());
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it.each(["INTERPRETATION_GROUNDING_FAILED", "INTERPRETATION_STAGE_TIMEOUT"])("reads the preserved result after %s with no new scientific outputs", async (code) => {
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    turn_id: "turn-1", status: "FAILED", steps: [], incremental_outputs: [],
    warnings: [{ code, message: "已有结果仍可查看。" }],
  });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-1" />);
  expect(await screen.findByRole("region", { name: "权威 ResearchTurn 科学呈现" })).toHaveTextContent("turn-1");
  expect(screen.queryByRole("heading", { name: "尚无科学结果" })).not.toBeInTheDocument();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it("recovers interpretation from the exact saved result without recomputing or consuming the draft", async () => {
  const user = userEvent.setup();
  mocks.getUserModels.mockResolvedValue({ selected: [{ provider: "personal", model: "deepseek-v4-pro" }], label: "我的模型" });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-1", status: "FAILED", steps: [], incremental_outputs: [], warnings: [{ code: "INTERPRETATION_PROVIDER_TIMEOUT", message: "解读超时，科学结果已保留。" }] });
  mocks.getAgent2ResearchTurnResult.mockResolvedValue({ research_turn_id: "turn-1", result_id: "result-1", result_snapshot_id: "snapshot-exact", source_object_refs: [], scientific_selections: [] });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-1" />);
  const retry = await screen.findByRole("button", { name: "重新解读" });
  expect(screen.queryByRole("button", { name: "重新运行分析" })).toBeNull();
  const editor = screen.getByLabelText("研究问题");
  fireEvent.change(editor, { target: { value: "保留我的后续问题" } });
  await user.click(screen.getByRole("button", { name: "研究设置" }));
  await user.click(screen.getByRole("checkbox", { name: "允许继续探索" }));
  await user.keyboard("{Escape}");
  await user.click(retry);
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledOnce());
  expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({
    requested_action: "INTERPRET_RESULT", autonomy_mode: "STANDARD", reply_to_turn_id: "turn-1",
    ui_context: expect.objectContaining({ explicit_result_ids: ["snapshot-exact"] }),
    model_selection: { provider: "personal", model: "deepseek-v4-pro", thinking_mode: "standard" },
  }));
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  expect(editor).toHaveValue("保留我的后续问题");
  expect(window.sessionStorage.getItem(researchComposerDraftKey("project_1", "session_1", "turn-new"))).toBe("保留我的后续问题");
});

it.each(["missing", "wrong-turn", "stalled"])("does not fall back to recomputation when reinterpretation source is %s", async (kind) => {
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-1", status: "FAILED", steps: [], incremental_outputs: [], warnings: [{ code: "INTERPRETATION_GROUNDING_FAILED", message: "解读未完成。" }] });
  if (kind === "wrong-turn") mocks.getAgent2ResearchTurnResult.mockResolvedValue({ research_turn_id: "wrong-turn", result_id: "wrong-result", source_object_refs: [], scientific_selections: [] });
  if (kind === "stalled") mocks.getAgent2ResearchTurnResult.mockImplementation(() => new Promise(() => {}));
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-1" />);
  const retry = await screen.findByRole("button", { name: "重新解读" });
  if (kind === "stalled") vi.useFakeTimers();
  fireEvent.click(retry); fireEvent.click(retry);
  if (kind === "stalled") {
    await act(async () => { await Promise.resolve(); });
    await act(async () => { await vi.advanceTimersByTimeAsync(10_001); });
    vi.useRealTimers();
  }
  await waitFor(() => expect(retry).toBeEnabled());
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  expect(mocks.getAgent2ResearchTurnResult).toHaveBeenCalledTimes(1);
  expect(screen.getByRole("region", { name: "分析进度" })).toHaveTextContent("解读未能完成");
});

it("ignores a late reinterpretation source after the user changes branches", async () => {
  mocks.getAgent2ExecutionProgress.mockImplementation(async (turn_id) => ({ turn_id, status: "FAILED", steps: [], incremental_outputs: [], warnings: [{ code: "INTERPRETATION_PROVIDER_TIMEOUT", message: "解读未完成。" }] }));
  let resolve!: (value: unknown) => void;
  mocks.getAgent2ResearchTurnResult.mockImplementation(() => new Promise((done) => { resolve = done; }));
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-1" />);
  fireEvent.click(await screen.findByRole("button", { name: "重新解读" }));
  await waitFor(() => expect(mocks.getAgent2ResearchTurnResult).toHaveBeenCalledOnce());
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-other" />);
  await act(async () => resolve({ research_turn_id: "turn-1", result_id: "result-1", source_object_refs: [], scientific_selections: [] }));
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.routerPush).not.toHaveBeenCalled();
});

it.each([
  ["FAILED", true], ["FAILED", false], ["CANCELED", true], ["CANCELED", false],
] as const)("uses verified saved-result availability after %s: %s", async (status, available) => {
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    turn_id: "turn-1", status, steps: [], incremental_outputs: [],
    preserved_result_available: available,
    warnings: status === "FAILED" ? [{ code: "ORCHESTRATOR_TIMEOUT", message: "模型响应超时。" }] : [],
  });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-1" />);
  if (available) {
    expect(await screen.findByRole("region", { name: "权威 ResearchTurn 科学呈现" })).toHaveTextContent("turn-1");
    expect(screen.queryByRole("heading", { name: "尚无科学结果" })).not.toBeInTheDocument();
  } else {
    expect(await screen.findByRole("heading", { name: "尚无科学结果" })).toBeInTheDocument();
  }
  expect(screen.getByRole("region", { name: "分析进度" })).toHaveTextContent(status === "FAILED" ? "模型响应超时。" : "分析已取消");
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it.each(["FAILED", "CANCELED", "RESULT_READY", "INTERPRETING"])("keeps committed scientific output readable when the Turn is %s", async (status) => {
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    turn_id: "turn-1", status, steps: [],
    incremental_outputs: [{ artifact_id: "trajectory-output", step_id: "step_1", title: "轨迹查看器" }],
    warnings: [{ code: "INTERPRETATION_GROUNDING_FAILED", message: "科学结果已生成，自动解读未完成。" }],
  });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-1" />);
  expect(await screen.findByRole("region", { name: "权威 ResearchTurn 科学呈现" })).toHaveTextContent("turn-1");
  expect(screen.queryByRole("heading", { name: "尚无科学结果" })).not.toBeInTheDocument();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  if (status === "RESULT_READY") {
    expect(screen.queryByRole("button", { name: /取消当前分析/ })).toBeNull();
  }
});

it("does not offer cancellation while scientific results are being committed", async () => {
  mocks.getAgent2ExecutionProgress.mockResolvedValue({
    contract_version: "1.0", turn_id: "turn-1", status: "RESULT_PENDING", steps: [],
    active_step_ids: [], completed_step_count: 1, total_step_count: 1,
    incremental_outputs: [], warnings: [], execution_outcome: "SUCCESS", result_projection_pending: true,
  });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-1" />);
  expect(await screen.findByText("执行已完成，正在整理科学结果")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /取消当前分析/ })).toBeNull();
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
  const composer = await screen.findByLabelText("研究问题");
  await user.type(
    composer,
    "在 1 ps 到 6 ps 的拟合窗口内计算 MSD 并评估扩散性质",
  );
  await user.click(screen.getByRole("button", { name: "研究设置" }));
  await user.click(screen.getByLabelText("允许继续探索"));
  expect(screen.getByText(/根据已有结果补充分析/u)).toHaveTextContent(
    "问题得到回答、证据不足或达到本次研究上限时停止",
  );
  await user.click(screen.getByRole("button", { name: "完成" }));
  await user.click(screen.getByRole("button", { name: "发送" }));

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
      autonomy_mode: "BOUNDED_AUTONOMOUS",
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

function viewerSampleToken(overrides: Record<string, string> = {}) {
  return encodeWorkspaceSelectionUrl(validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: "a".repeat(64), primary: { selectionSchemaVersion: "1.0", kind: "DATASET_SAMPLE", sourceScopeHash: "a".repeat(64), projectId: "project_1", datasetId: "dataset_1", datasetVersion: "version_table", objectId: "child_sample_object", sampleRef: "sample_Fe", ...overrides }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false }));
}

it.each(["projectId", "datasetVersion", "malformed"])("blocks an invalid %s handoff without creating a session or losing the draft", async (field) => {
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" viewerContext={{ objectId: "object_table", versionId: "version_table", objectType: "materials.table", displayName: "精确材料表", selectionToken: field === "malformed" ? "invalid-token" : viewerSampleToken({ [field]: "foreign" }) }} />);
  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "分析选择的样本");
  expect(screen.getByRole("alert")).toHaveTextContent("链接中的选择无法绑定");
  expect(screen.getByRole("button", { name: "发送" })).toBeDisabled();
  fireEvent.submit(composer.closest("form")!);
  expect(mocks.createResearchSession).not.toHaveBeenCalled();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(composer).toHaveValue("分析选择的样本");
  expect(screen.getByRole("link", { name: "返回数据重新选择" })).toHaveAttribute("href", "/projects/project_1/data?object=object_table&version=version_table");
  await user.click(screen.getByRole("button", { name: "使用此完整版本" }));
  expect(composer).toHaveValue("分析选择的样本");
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({ ui_context: expect.objectContaining({ scientific_selections: [], selection_refs: [], explicit_object_refs: [expect.objectContaining({ object_id: "object_table", version_id: "version_table" })] }) })));
});

it("shows and submits a validated sample with its exact parent scientific version", async () => {
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" viewerContext={{ objectId: "object_table", versionId: "version_table", objectType: "materials.table", displayName: "精确材料表", selectionToken: viewerSampleToken() }} />);
  const composer = await screen.findByLabelText("研究问题");
  expect(within(screen.getByRole("tabpanel", { name: "对话" })).getByText("数据样本 · sample_Fe")).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "研究所选数据" })).toBeInTheDocument();
  expect(screen.getByRole("tab", { name: "上下文" })).toHaveAttribute("aria-selected", "true");
  expect(screen.queryByRole("heading", { name: "调用记录" })).not.toBeInTheDocument();
  expect(screen.queryByText(/在下方描述要检查/)).not.toBeInTheDocument();
  const sourceLink = screen.getByRole("link", { name: "打开来源数据" });
  expect(sourceLink).toHaveAttribute("href", expect.stringContaining("object=object_table&version=version_table&selection="));
  await user.click(screen.getByRole("tab", { name: "结果" }));
  expect(screen.getByRole("heading", { name: "尚无分析结果" })).toBeVisible();
  expect(screen.queryByRole("heading", { name: "可用数据" })).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "查看本次数据上下文" }));
  expect(sourceLink).toBeVisible();
  await user.keyboard("{Escape}");
  await waitFor(() => expect(screen.getByRole("button", { name: "查看本次数据上下文" })).toHaveFocus());
  await user.click(screen.getByRole("button", { name: "查看本次数据上下文" }));
  expect(screen.queryByRole("region", { name: "历史研究" })).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /概览当前项目数据/ })).not.toBeInTheDocument();
  await user.type(composer, "分析这个样本");
  await user.click(screen.getByRole("button", { name: "发送" }));
  expect(screen.getByRole("tab", { name: "结果" })).toHaveAttribute("aria-selected", "true");
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({ ui_context: expect.objectContaining({ scientific_selections: [expect.objectContaining({ object_ref: expect.objectContaining({ object_id: "object_table", version_id: "version_table" }), semantic_locator: { sample_ref: "sample_Fe" } })] }) })));
});

it.each(["objectId", "versionId", "objectType"])("fails closed when an explicit source link omits %s", async (field) => {
  render(<ResearchPage projectId="project_1" viewerContext={{ objectId: "object_table", versionId: "version_table", objectType: "materials.table", [field]: undefined }} />);
  const composer = await screen.findByLabelText("研究问题");
  await userEvent.type(composer, "保留这个问题");
  expect(screen.getByRole("alert")).toHaveTextContent("此来源链接缺少");
  expect(screen.getByRole("button", { name: "发送" })).toBeDisabled();
  fireEvent.submit(composer.closest("form")!);
  expect(mocks.createResearchSession).not.toHaveBeenCalled();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(composer).toHaveValue("保留这个问题");
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

  const composer = await screen.findByLabelText("研究问题");
  expect(mocks.getResearchSession).not.toHaveBeenCalledWith("archived_session", expect.any(AbortSignal));
  expect(mocks.getResearchSession).not.toHaveBeenCalledWith("active_session", expect.any(AbortSignal));

  await user.type(composer, "比较 CrystalNN 与 VoronoiNN 的局域配位结果");
  await user.click(screen.getByRole("button", { name: "发送" }));

  await waitFor(() =>
    expect(mocks.createResearchSession).toHaveBeenCalledWith(
      "project_1",
      expect.stringContaining("比较 CrystalNN"),
      undefined,
      expect.stringContaining("mdi:research-pending-session:"),
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

it("keeps an unconfirmed admission visible without recording a false terminal failure", async () => {
  const user = userEvent.setup();
  mocks.createAgent2ResearchTurn.mockRejectedValueOnce(new Agent2AdmissionUnconfirmedError());
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

  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "分析当前结构的配位环境");
  await user.click(screen.getByRole("button", { name: "发送" }));

  expect(await screen.findByText(/无法确认本次提交状态/)).toBeInTheDocument();
  expect(composer).toHaveValue("分析当前结构的配位环境");
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledTimes(1);
  expect(mocks.createResearchAssistantProjection).not.toHaveBeenCalled();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
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

  expect(await screen.findByLabelText("研究问题")).toBeInTheDocument();
  expect(mocks.getResearchSession).not.toHaveBeenCalledWith("active_session", expect.any(AbortSignal));
});

it("keeps project history out of a new conversation while retaining data entry points", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: Array.from({ length: 5 }, (_, index) => ({
      datasetId: `dataset_${index}`, name: `材料数据 ${index}`,
      profile: { rowCount: index + 1, datasetType: "Materials_Tabular_Dataset" },
    })),
    analyses: [{
      jobId: "job-history", status: "completed", userQuestion: "已有材料分析",
      toolIds: [], stepCount: 1, artifactCount: 1, artifactTypes: [],
    }],
  });
  render(<ResearchPage projectId="project_1" />);

  expect(await screen.findByRole("heading", { name: "可用数据" })).toBeInTheDocument();
  expect(screen.queryByRole("link", { name: /已有材料分析/ })).not.toBeInTheDocument();
  expect(screen.queryByRole("region", { name: "历史研究" })).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: "查看全部数据" })).toHaveAttribute("href", "/projects/project_1/data");
  expect(screen.getByRole("link", { name: /材料数据 0/ })).toHaveAttribute("href", "/projects/project_1/data?dataset=dataset_0");
  expect(screen.getAllByRole("link", { name: /材料数据 \d/ })).toHaveLength(4);
  expect(screen.queryByText("最近研究")).not.toBeInTheDocument();
  expect(screen.getAllByRole("textbox", { name: "研究问题" })).toHaveLength(1);
});

it.each([false, true])("restores a failed pre-Turn draft and its session after reload with fresh=%s", async (fresh) => {
  const savedSession = { id: "session_1", project_id: "project_1", title: "研究会话", status: "active", messages: [] };
  mocks.listResearchSessions.mockReset().mockResolvedValue(fresh ? [] : [savedSession]);
  mocks.getResearchSession.mockReset().mockResolvedValue(savedSession);
  mocks.createAgent2ResearchTurn.mockRejectedValue(new Agent2AdmissionUnconfirmedError());
  const props = {
    projectId: "project_1", sessionId: fresh ? undefined : "session_1", fresh,
    viewerContext: { objectId: "object-exact", versionId: "version-exact", objectType: "structure.crystal" },
  };
  const first = render(<ResearchPage {...props} />);
  const composer = await screen.findByLabelText("研究问题");
  fireEvent.change(composer, { target: { value: "不要丢失尚未确认的问题" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  expect(await screen.findByText(/无法确认本次提交状态/)).toBeInTheDocument();
  first.unmount();

  mocks.listResearchSessions.mockResolvedValue([savedSession]);
  render(<ResearchPage {...props} />);
  await waitFor(() => expect(screen.getByLabelText("研究问题")).toHaveValue("不要丢失尚未确认的问题"));
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledTimes(2));
  expect(mocks.createResearchSession).toHaveBeenCalledTimes(fresh ? 1 : 0);
  expect(mocks.createAgent2ResearchTurn.mock.calls.map(([project, session]) => [project, session])).toEqual([
    ["project_1", "session_1"], ["project_1", "session_1"],
  ]);
  expect(mocks.createResearchAssistantProjection).not.toHaveBeenCalled();
});

it("restores an unsent draft before a session or Turn exists", async () => {
  const first = render(<ResearchPage projectId="project_1" fresh />);
  fireEvent.change(await screen.findByLabelText("研究问题"), { target: { value: "尚未发送的问题" } });
  first.unmount();
  render(<ResearchPage projectId="project_1" fresh />);
  await waitFor(() => expect(screen.getByLabelText("研究问题")).toHaveValue("尚未发送的问题"));
  expect(mocks.createResearchSession).not.toHaveBeenCalled();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it("adjusts the conversation splitter with keyboard arrows", async () => {
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" />);

  const splitter = await screen.findByRole("separator", {
    name: "调整研究对话宽度",
  });
  expect(splitter).toHaveAttribute("aria-valuenow", "720");
  splitter.focus();
  await user.keyboard("{ArrowRight}");
  expect(splitter).toHaveAttribute("aria-valuenow", "736");
  await user.keyboard("{ArrowLeft}");
  expect(splitter).toHaveAttribute("aria-valuenow", "720");
  await user.keyboard("{End}");
  expect(splitter).toHaveAttribute("aria-valuenow", "760");
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

it("fits the conversation to the mounted canvas and keeps keyboard bounds in sync on resize", async () => {
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" />);
  const workbench = await screen.findByRole("region", { name: "项目研究工作台" });
  const splitter = screen.getByRole("separator", { name: "调整研究对话宽度" });
  const bounds = vi.spyOn(workbench, "getBoundingClientRect");
  bounds.mockReturnValue({ left: 0, width: 1000 } as DOMRect);

  fireEvent(window, new Event("resize"));

  expect(splitter).toHaveAttribute("aria-valuenow", "513");
  expect(splitter).toHaveAttribute("aria-valuemax", "513");
  expect(workbench.style.getPropertyValue("--research-conversation-width")).toBe("513px");
  splitter.focus();
  await user.keyboard("{ArrowRight}");
  expect(splitter).toHaveAttribute("aria-valuenow", "513");

  bounds.mockReturnValue({ left: 0, width: 900 } as DOMRect);
  fireEvent(window, new Event("resize"));
  expect(splitter).toHaveAttribute("aria-valuenow", "413");
  expect(splitter).toHaveAttribute("aria-valuemax", "413");
  bounds.mockReturnValue({ left: 0, width: 1700 } as DOMRect);
  fireEvent(window, new Event("resize"));
  expect(splitter).toHaveAttribute("aria-valuenow", "513");
  bounds.mockRestore();
});

it("keeps a viewer project readable without a research composer", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "共享研究项目", role: "viewer" },
    datasets: [{ datasetId: "dataset_a" }],
    analyses: [],
  });
  render(<ResearchPage projectId="project_1" />);
  expect(await screen.findByText("此项目为只读")).toBeInTheDocument();
  expect(screen.queryByLabelText("研究问题")).not.toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: "发送" }),
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

it("shows a local retry when project data cannot load without claiming the workspace is empty", async () => {
  const user = userEvent.setup();
  mocks.getProjectHistory.mockRejectedValueOnce(
    new Error("network unavailable"),
  );
  render(<ResearchPage projectId="project_1" />);

  expect(
    await screen.findByRole("heading", { name: "项目数据暂时无法读取" }),
  ).toBeInTheDocument();
  expect(screen.queryByText("正在确认项目权限…")).not.toBeInTheDocument();
  expect(screen.queryByText("0 个数据集")).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重新读取项目数据" }));
  expect(
    await screen.findByLabelText("研究问题"),
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
  expect(screen.queryByLabelText("研究问题")).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重新加载对话" }));
  expect(
    await screen.findByLabelText("研究问题"),
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
  await user.click(screen.getByRole("heading", { name: "对话" }));
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
  render(<ResearchPage projectId="project_1" fresh />);
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
  }, expect.any(AbortSignal));
  expect(await screen.findByText("列表置顶 · 可继续")).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "管理 可管理研究" }));
  await user.click(screen.getByRole("menuitem", { name: "重命名" }));
  const rename = screen.getByRole("textbox", { name: "研究名称" });
  await user.clear(rename);
  await user.type(rename, "硅结构复核");
  await user.click(screen.getByRole("button", { name: "保存名称" }));
  expect(mocks.updateResearchSession).toHaveBeenCalledWith("session_active", {
    title: "硅结构复核",
  }, expect.any(AbortSignal));

  await user.click(screen.getByRole("button", { name: "管理 硅结构复核" }));
  await user.click(screen.getByRole("menuitem", { name: "归档" }));
  await user.click(screen.getByRole("button", { name: "确认归档" }));
  expect(mocks.updateResearchSession).toHaveBeenCalledWith("session_active", {
    lifecycle: "ARCHIVED",
  }, expect.any(AbortSignal));
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
  }, expect.any(AbortSignal));
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

  render(<ResearchPage projectId="project_1" fresh />);
  await user.click(await screen.findByRole("button", { name: "研究记录" }));
  await user.click(screen.getByRole("button", { name: "批量管理" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 批量研究一" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 批量研究二" }));
  expect(screen.getByText("2 项已选")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "归档所选" }));
  await user.click(screen.getByRole("button", { name: "确认归档" }));

  await waitFor(() =>
    expect(mocks.bulkUpdateResearchSessions).toHaveBeenCalledWith(
      "project_1",
      ["session_bulk_one", "session_bulk_two"],
      "ARCHIVE",
      expect.any(AbortSignal),
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

  expect(await screen.findByRole("heading", { name: "对话" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "对话" })).toHaveAttribute("title", "历史结构研究");
  expect(screen.getByText("已归档")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "开始新的研究" })).toHaveAttribute(
    "href",
    "/projects/project_1/research?new=1",
  );
  expect(screen.getByRole("button", { name: "恢复原会话" })).toBeInTheDocument();
  expect(screen.queryByLabelText("研究问题")).not.toBeInTheDocument();
  expect(
    screen.getByText("历史对话、科学结果和精确来源仍可查看。可以开始新的研究，或恢复原会话后继续。"),
  ).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "恢复原会话" }));
  expect(mocks.updateResearchSession).toHaveBeenCalledWith("session_archived", {
    lifecycle: "ACTIVE",
  }, expect.any(AbortSignal));
  expect(await screen.findByLabelText("研究问题")).toBeInTheDocument();
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

it("keeps other sessions and sibling branch results out of the selected conversation", async () => {
  mocks.getAgent2ExecutionProgress.mockResolvedValue({turn_id:"turn_selected",status:"COMPLETED",completed_step_count:1,total_step_count:1,steps:[],incremental_outputs:[],warnings:[]});
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
      {jobId:"job_sibling",researchSessionId:"session_1",researchTurnId:"turn_sibling",researchTurnStatus:"COMPLETED",status:"completed",userQuestion:"同一对话的其他分支",toolIds:[],stepCount:1,artifactCount:1,artifactTypes:[]},
    ],
  });

  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn_selected" />);

  expect(
    await screen.findByRole("heading", { name: "对话" }),
  ).toBeInTheDocument();
  expect(screen.queryByText("声子验证项目 · 研究时间线")).not.toBeInTheDocument();
  expect(screen.queryByText("比较声子带与态密度")).not.toBeInTheDocument();
  expect(screen.queryByText("同一对话的其他分支")).not.toBeInTheDocument();
  expect(screen.queryByText("2 个步骤 · 查看过程")).not.toBeInTheDocument();
  expect(screen.queryByText("✓ 分析完成")).not.toBeInTheDocument();
  expect(
    screen.queryByRole("region", { name: "历史研究" }),
  ).not.toBeInTheDocument();
  expect(await screen.findByRole("region", {name: "权威 ResearchTurn 科学呈现"})).toHaveTextContent("turn_selected");
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
    "/projects/project_1/research/session_branch?turn=turn_root&branchRoot=turn_root",
  );
  await user.click(
    within(branchNavigation).getByLabelText("查看全部 2 个分支"),
  );
  expect(
    within(branchNavigation).getByRole("link", { name: /1\. 计算 MSD/ }),
  ).toHaveAttribute(
    "href",
    "/projects/project_1/research/session_branch?turn=turn_root&branchRoot=turn_root",
  );
  const currentBranch = within(branchNavigation).getByRole("link", {
    name: /2\. 限定 1–6 ps 重新评估扩散/,
  });
  expect(currentBranch).toHaveAttribute("aria-current", "page");
  const branchDetails = within(branchNavigation).getByLabelText("分支 2 详情").closest("details");
  expect(branchDetails).not.toHaveAttribute("open");
  await user.click(within(branchNavigation).getByLabelText("分支 2 详情"));
  // user-event 14 omits native summary elements from its focusable selector.
  // Mirror the click focus verified in the real browser before keyboard input.
  within(branchNavigation).getByLabelText("分支 2 详情").focus();
  expect(branchDetails).toHaveTextContent("ResearchTurn turn_branch");
  expect(branchDetails).toHaveTextContent("消息修订 message_branch");
  await user.keyboard("{Escape}");
  expect(within(branchNavigation).getByLabelText("查看全部 2 个分支").closest("details")).not.toHaveAttribute("open");
  expect(within(branchNavigation).getByLabelText("查看全部 2 个分支")).toHaveFocus();
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

it.each(["", "尚未发送的新草稿"])("restores a failed run question while preserving draft %s and its data scope", async (draft) => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{ datasetId: "original-dataset", name: "原数据" }],
    analyses: [{ jobId: "job_failed", datasetId: "original-dataset", status: "failed", userQuestion: "分析原始目标列", stepCount: 1, artifactCount: 0 }],
  });
  mocks.getPlannerJob.mockResolvedValue({ status: "failed", analysisPlan: { goal: "分析原始目标列", datasetId: "original-dataset", steps: [{ stepId: "metrics", toolId: "ml.basic_metrics" }] } });
  mocks.getPlannerJobEvents.mockResolvedValue([{ eventType: "tool.failed", message: "TOOL_INPUT_INVALID: Requested target column does not exist.", payload: { stepId: "metrics" } }]);
  mocks.getPlannerJobArtifacts.mockResolvedValue([]);
  render(<ResearchPage projectId="project_1" runId="job_failed" />);
  const feedback = await screen.findByRole("status", { name: "分析失败与恢复" });
  await waitFor(() => expect(feedback).toHaveTextContent("目标列不存在"));
  expect(screen.getByText("此步骤执行失败")).toBeInTheDocument();
  const composer = screen.getByLabelText("研究问题");
  if (draft) fireEvent.change(composer, { target: { value: draft } });
  fireEvent.click(within(feedback).getByRole("button", { name: "修改问题后重试" }));
  await waitFor(() => expect(composer).toHaveFocus());
  expect(composer).toHaveValue(draft || "分析原始目标列");
  expect(screen.getByText("分析未完成 · 查看过程")).toBeInTheDocument();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createResearchSession).toHaveBeenCalledWith("project_1", expect.any(String), "original-dataset", expect.stringContaining("mdi:research-pending-session:")));
});

it.each(["cancelled", "canceled"])("shows a live %s Job as terminal and keeps the composer usable", async (status) => {
  const user = userEvent.setup();
  const source = legacyResearchSource("session", "dataset_b", "materials-b");
  mocks.getPlannerJob.mockResolvedValue({ status });
  render(<ResearchPage projectId="project_1" {...source} />);
  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "分析当前数据");
  await user.click(screen.getByRole("button", { name: "发送" }));

  expect(await screen.findByText("分析已取消 · 查看过程")).toBeInTheDocument();
  expect(screen.getByText("本次分析已取消，取消前已保存的输出仍可查看。")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "正在分析…" })).not.toBeInTheDocument();
  expect(mocks.createPlannerJobInterpretation).not.toHaveBeenCalled();
  expect(mocks.createResearchAssistantProjection).not.toHaveBeenCalledWith(
    expect.anything(), expect.objectContaining({ phase: "failed" }),
  );
  await user.type(composer, "下一条问题");
  expect(screen.getByRole("button", { name: "发送" })).toBeEnabled();
});

it("reopens a canceled Job without turning it into a failure or starting interpretation", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{ datasetId: "dataset_a" }],
    analyses: [{
      jobId: "job_canceled", status: "cancelled", userQuestion: "已取消的分析",
      stepCount: 1, artifactCount: 0,
    }],
  });
  mocks.getPlannerJob.mockResolvedValue({ status: "cancelled" });
  render(<ResearchPage projectId="project_1" runId="job_canceled" />);

  expect(await screen.findByText("分析已取消 · 查看过程")).toBeInTheDocument();
  expect(screen.queryByText("分析未完成 · 查看过程")).not.toBeInTheDocument();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  expect(mocks.createPlannerJobInterpretation).not.toHaveBeenCalled();
});

it.each(["queued", "cancel_requested"])("reconciles a reopened %s Job to its durable terminal state", async (status) => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{ datasetId: "dataset_a" }],
    analyses: [{
      jobId: "job_reopened", status, userQuestion: "已接收的分析", stepCount: 1, artifactCount: 0,
    }],
  });
  mocks.getPlannerJob.mockResolvedValue({
    status: "completed", analysisPlan: { goal: "已接收的分析", steps: [] },
  });
  render(<ResearchPage projectId="project_1" runId="job_reopened" />);

  expect(await screen.findByRole("link", { name: "打开分析报告" })).toHaveAttribute(
    "href", "/projects/project_1/reports/job_reopened",
  );
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  expect(mocks.getPlannerJob).toHaveBeenCalledWith(
    "job_reopened", expect.objectContaining({ signal: expect.any(AbortSignal) }),
  );
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

it("shows a terminal job before stalled logs settle and keeps late final artifacts", async () => {
  let deliverArtifacts!: (value: unknown[]) => void;
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" }, datasets: [],
    analyses: [{ jobId: "job_terminal", status: "running", userQuestion: "核对最终结果" }],
  });
  mocks.getPlannerJobEvents.mockImplementation(() => new Promise(() => {}));
  const finalArtifacts = new Promise<unknown[]>((resolve) => { deliverArtifacts = resolve; });
  mocks.getPlannerJobArtifacts.mockReturnValue(finalArtifacts);
  mocks.getPlannerJob.mockResolvedValue({ jobId: "job_terminal", status: "completed", planHash: "a".repeat(64) });
  render(<ResearchPage projectId="project_1" runId="job_terminal" />);
  expect(await screen.findByRole("link", { name: "打开分析报告" })).toBeInTheDocument();
  expect(screen.queryByText("正在分析", { exact: true })).not.toBeInTheDocument();
  await act(async () => { deliverArtifacts([{ artifactId: "final_result", jobId: "job_terminal", type: "table_json", name: "最后保存的结果" }]); });
  expect(await screen.findByTestId("scientific-result-viewer")).toBeInTheDocument();
  expect(mocks.createPlannerJobInterpretation).not.toHaveBeenCalled();
});

it("keeps a completed job's interpretation alive after the running-state transition", async () => {
  let deliverInterpretation!: (value: unknown) => void;
  const source = legacyResearchSource("session", "dataset_b", "materials-b");
  mocks.createPlannerJobInterpretation.mockImplementationOnce(() => new Promise((resolve) => { deliverInterpretation = resolve; }));
  mocks.getPlannerJobArtifacts.mockResolvedValue([{ artifactId: "final_result", jobId: "job_1", type: "table_json", name: "已保存的结果" }]);
  render(<ResearchPage projectId="project_1" {...source} />);
  fireEvent.change(await screen.findByLabelText("研究问题"), { target: { value: "分析当前数据" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createPlannerJobInterpretation).toHaveBeenCalledTimes(1));
  expect(screen.getByRole("link", { name: "打开分析报告" })).toBeInTheDocument();
  expect(screen.getByText("正在整理科学结论…")).toBeInTheDocument();
  await act(async () => { deliverInterpretation({ outcome: "INTERPRETATION_READY", interpretation: { interpretationId: "fresh_conclusion", sourceJobId: "job_1", completeness: "COMPLETE", claims: [{ claimId: "finding", renderedText: "最终计算结论仍可呈现" }], globalLimitations: [] } }); });
  expect(await screen.findByText("最终计算结论仍可呈现")).toBeInTheDocument();
  expect(screen.queryByText("正在整理科学结论…")).not.toBeInTheDocument();
  expect(mocks.createPlannerJobInterpretation).toHaveBeenCalledTimes(1);
});

it("bounds an uncertain interpretation write without starting fallback and recovers by rereading its saved result", async () => {
  const source = legacyResearchSource("session", "dataset_b", "materials-b");
  mocks.createPlannerJobInterpretation.mockImplementation(() => new Promise(() => {}));
  mocks.getPlannerJobArtifacts.mockResolvedValue([{ artifactId: "final_result", jobId: "job_1", type: "table_json", name: "已保存的结果" }]);
  render(<ResearchPage projectId="project_1" {...source} />);
  fireEvent.change(await screen.findByLabelText("研究问题"), { target: { value: "分析当前数据" } });
  vi.useFakeTimers();
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  expect(mocks.createPlannerJobInterpretation).toHaveBeenCalledTimes(1);
  await act(async () => { await vi.advanceTimersByTimeAsync(10000); });
  expect(screen.getByText("暂时无法读取：结果解读。")).toBeInTheDocument();
  expect(screen.queryByText("正在整理科学结论…")).not.toBeInTheDocument();
  expect(mocks.createPlannerJobInterpretation).toHaveBeenCalledTimes(1);
  expect(mocks.createPlannerJobInterpretation.mock.calls[0][2].signal.aborted).toBe(true);
  mocks.getPlannerJobInterpretations.mockResolvedValue({ jobId: "job_1", interpretations: [{ interpretationId: "saved_after_timeout", sourceJobId: "job_1", completeness: "COMPLETE", claims: [{ claimId: "result", renderedText: "超时后读回已保存结论" }], globalLimitations: [] }] });
  mocks.getPlannerInterpretationEvidence.mockResolvedValue({ interpretationId: "saved_after_timeout", evidenceItems: [] });
  fireEvent.click(screen.getByRole("button", { name: "重新读取分析结果" }));
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  expect(screen.getByText("超时后读回已保存结论")).toBeInTheDocument();
  expect(mocks.createPlannerJobInterpretation).toHaveBeenCalledTimes(1);
  expect(screen.queryByText("正在读取…")).not.toBeInTheDocument();
});

it("rejects an interpretation for another job instead of showing its claims or generating a fallback", async () => {
  const source = legacyResearchSource("session", "dataset_b", "materials-b");
  mocks.createPlannerJobInterpretation.mockResolvedValue({ outcome: "INTERPRETATION_READY", interpretation: { interpretationId: "foreign", sourceJobId: "different_job", completeness: "COMPLETE", claims: [{ renderedText: "不属于本次分析的结论" }] } });
  render(<ResearchPage projectId="project_1" {...source} />);
  fireEvent.change(await screen.findByLabelText("研究问题"), { target: { value: "分析当前数据" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  expect(await screen.findByText("暂时无法读取：结果解读。")).toBeInTheDocument();
  expect(screen.queryByText("不属于本次分析的结论")).not.toBeInTheDocument();
  expect(mocks.createPlannerJobInterpretation).toHaveBeenCalledTimes(1);
});

it("uses deterministic interpretation only after a definitive provider failure", async () => {
  const source = legacyResearchSource("session", "dataset_b", "materials-b");
  mocks.createPlannerJobInterpretation.mockResolvedValueOnce({ outcome: "PROVIDER_FAILED" }).mockResolvedValueOnce({ outcome: "INTERPRETATION_READY", interpretation: { interpretationId: "deterministic", sourceJobId: "job_1", completeness: "COMPLETE", claims: [{ claimId: "bounded", renderedText: "由已有证据得到的确定性解读" }], globalLimitations: [] } });
  render(<ResearchPage projectId="project_1" {...source} />);
  fireEvent.change(await screen.findByLabelText("研究问题"), { target: { value: "分析当前数据" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  expect(await screen.findByText("由已有证据得到的确定性解读")).toBeInTheDocument();
  expect(mocks.createPlannerJobInterpretation.mock.calls.map((call) => call[2].mode)).toEqual(["STRICT_PROVIDER", "DETERMINISTIC"]);
});

it("reopens a historical run from research records in its persisted session", async () => {
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
        researchSessionId: "session_owner",
        status: "completed",
        userQuestion: "分析扩散行为",
        stepCount: 2,
        artifactCount: 1,
      },
    ],
  });
  render(<ResearchPage projectId="project_1" />);

  await userEvent.setup().click(await screen.findByRole("button", {name: "研究记录"}));
  const runLink = await screen.findByRole("link", {name: /扩散研究/});
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
    expect(mocks.getResearchSession).toHaveBeenCalledWith("session_bound", expect.any(AbortSignal)),
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
    expect(mocks.getResearchSession).toHaveBeenCalledWith("session_explicit", expect.any(AbortSignal)),
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

it.each([false, true])("does not claim scientific output exists when a completed run has none (interpretation unavailable: %s)", async (unavailable) => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [],
    analyses: [{ jobId: "job_no_output", status: "completed", userQuestion: "核对历史计算", stepCount: 1, artifactCount: 0 }],
  });
  if (unavailable) mocks.getPlannerJobInterpretations.mockRejectedValueOnce(new Error("unavailable"));
  render(<ResearchPage projectId="project_1" runId="job_no_output" />);

  expect(await screen.findByRole("heading", { name: "状态说明" })).toBeInTheDocument();
  expect(screen.getByText("当前未读取到可展示的科学输出；请打开分析报告查看执行状态与依据。")).toBeInTheDocument();
  expect(screen.queryByText(/本次分析已生成可复核的图表与数据表/)).not.toBeInTheDocument();
  expect(screen.queryByText("科学结论暂时无法读取；结果仍可查看。")).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: "打开分析报告" })).toHaveAttribute("href", "/projects/project_1/reports/job_no_output");
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
    await screen.findByText(/暂时无法读取：.*运行记录/u),
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
  const source = legacyResearchSource("session", "dataset_a", "材料表");
  mocks.getPlannerJob.mockResolvedValue({
    status: "failed",
    analysisPlan: { goal: "分析失败", datasetId: "dataset_a", steps: [] },
    planHash: "a".repeat(64),
  });
  render(<ResearchPage projectId="project_1" {...source} />);

  await user.type(
    await screen.findByLabelText("研究问题"),
    "分析失败",
  );
  await user.click(screen.getByRole("button", { name: "发送" }));
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

it("keeps research settings bounded to a dialog and preserves a choice across model refreshes", async () => {
  const selected = [{ provider: "personal", model: "deepseek-v4-pro" }, { provider: "personal", model: "deepseek-v4-flash" }];
  mocks.getUserModels.mockResolvedValue({ selected, label: "我的模型" });
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" />);
  const trigger = await screen.findByRole("button", { name: "研究设置" });
  await user.click(trigger);
  const dialog = screen.getByRole("dialog", { name: "研究设置" });
  await user.selectOptions(within(dialog).getByRole("combobox", { name: "本次分析模型" }), JSON.stringify(["personal", "deepseek-v4-flash"]));
  await user.selectOptions(within(dialog).getByRole("combobox", { name: "思考深度" }), "deep");
  await user.click(within(dialog).getByRole("checkbox", { name: "允许继续探索" }));
  await user.keyboard("{Escape}");
  await waitFor(() => expect(trigger).toHaveFocus());
  expect(screen.queryByRole("dialog")).toBeNull();
  expect(trigger).toHaveTextContent("deepseek-v4-flash");
  fireEvent(window, new Event("mdi:models-changed"));
  await waitFor(() => expect(mocks.getUserModels).toHaveBeenCalledTimes(2));
  await user.click(trigger);
  expect(screen.getByRole("combobox", { name: "本次分析模型" })).toHaveValue(JSON.stringify(["personal", "deepseek-v4-flash"]));
  expect(screen.getByRole("combobox", { name: "思考深度" })).toHaveValue("deep");
  expect(screen.getByRole("checkbox", { name: "允许继续探索" })).toBeChecked();
  mocks.getUserModels.mockRejectedValueOnce(new Error("unavailable"));
  fireEvent(window, new Event("mdi:models-changed"));
  expect(await screen.findByText("模型列表暂未更新，当前选择仍保留。")).toBeInTheDocument();
  expect(screen.getByRole("combobox", { name: "本次分析模型" })).toHaveValue(JSON.stringify(["personal", "deepseek-v4-flash"]));
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it("routes result actions through the selected model and carries an unsent draft into the new Turn", async () => {
  mocks.getUserModels.mockResolvedValue({ selected: [{ provider: "personal", model: "deepseek-v4-pro" }], label: "我的模型" });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-1", status: "COMPLETED", steps: [], warnings: [], incremental_outputs: [] });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-1" />);
  const input = await screen.findByLabelText("研究问题");
  fireEvent.change(input, { target: { value: "保留未发送的草稿" } });
  await waitFor(() => expect(mocks.presentationProps.mock.lastCall?.[0].onRun).toBeTypeOf("function"));
  const props = mocks.presentationProps.mock.lastCall![0];
  act(() => props.onContinue());
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  await waitFor(() => expect(input).toHaveFocus());
  await act(async () => { await props.onRun("reinterpret", { research_turn_id: "turn-1", result_id: "result-1", result_snapshot_id: "snapshot-1", research_question: "科学问题", source_object_refs: [], scientific_selections: [] }); });
  expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({
    model_selection: { provider: "personal", model: "deepseek-v4-pro", thinking_mode: "standard" },
     requested_action: "INTERPRET_RESULT", reply_to_turn_id: "turn-1", ui_context: expect.objectContaining({ explicit_result_ids: ["snapshot-1"] }),
  }));
  expect(input).toHaveValue("保留未发送的草稿");
  expect(window.sessionStorage.getItem(researchComposerDraftKey("project_1", "session_1", "turn-new")!)).toBe("保留未发送的草稿");
});

it("does not navigate when a result action completes after switching Turns", async () => {
  mocks.listAgent2ResearchTurns.mockResolvedValue([{
    turn_id: "turn-1", research_session_id: "session_1", project_id: "project_1",
    sequence_no: 1, parent_turn_id: null, status: "COMPLETED",
    user_message: { id: "message-1", role: "user", content: "原始中文研究问题" },
    created_at: "2026-08-30T00:00:00Z",
  }]);
  mocks.getAgent2ExecutionProgress.mockImplementation(async (id: string) => ({ turn_id: id, status: "COMPLETED", steps: [], warnings: [], incremental_outputs: [] }));
  let resolve!: (value: unknown) => void;
  mocks.createAgent2ResearchTurn.mockImplementationOnce(() => new Promise((done) => { resolve = done; }));
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-1" />);
  await waitFor(() => expect(mocks.presentationProps.mock.lastCall?.[0].onRun).toBeTypeOf("function"));
  const result = { research_turn_id: "turn-1", result_id: "result-1", research_question: "科学问题", source_object_refs: [], scientific_selections: [] };
  let pending!: Promise<void>;
  act(() => { pending = mocks.presentationProps.mock.lastCall![0].onRun("rerun", result); });
  expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledOnce();
  expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({ message: "原始中文研究问题" }));
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-2" />);
  mocks.routerPush.mockClear();
  await act(async () => { resolve({ turn_id: "late-turn" }); await pending; });
  expect(mocks.routerPush).not.toHaveBeenCalled();
});

it.each([false, true])("keeps the split stable while the next branch is unread, customized=%s", async (customized) => {
  let resolveNext!: (value: unknown) => void;
  mocks.getAgent2ExecutionProgress.mockImplementation((id: string) => id === "turn-b"
    ? new Promise((resolve) => { resolveNext = resolve; })
    : Promise.resolve({ turn_id: id, status: "COMPLETED", steps: [], warnings: [], incremental_outputs: [] }));
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-a" />);
  const splitter = await screen.findByRole("separator", { name: "调整研究对话宽度" });
  await waitFor(() => expect(mocks.presentationProps.mock.lastCall?.[0].turnId).toBe("turn-a"));
  expect(splitter).toHaveAttribute("aria-valuenow", "512");
  if (customized) fireEvent.keyDown(splitter, { key: "ArrowRight" });
  const expectedWidth = customized ? "528" : "512";
  const workbench = screen.getByRole("region", { name: "项目研究工作台" });

  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-b" />);
  await waitFor(() => expect(resolveNext).toBeTypeOf("function"));
  expect(splitter).toHaveAttribute("aria-valuenow", expectedWidth);
  expect(workbench.style.getPropertyValue("--research-conversation-width")).toBe(`${expectedWidth}px`);
  // A resize notification during the read must not reapply the empty-workspace default.
  fireEvent(window, new Event("resize"));
  expect(splitter).toHaveAttribute("aria-valuenow", expectedWidth);
  await act(async () => { resolveNext({ turn_id: "turn-b", status: "COMPLETED", steps: [], warnings: [], incremental_outputs: [] }); });
  expect(splitter).toHaveAttribute("aria-valuenow", expectedWidth);

  const bounds = vi.spyOn(workbench, "getBoundingClientRect").mockReturnValue({ width: 880 } as DOMRect);
  fireEvent(window, new Event("resize"));
  expect(splitter).toHaveAttribute("aria-valuenow", "393");
  expect(splitter).toHaveAttribute("aria-valuemax", "393");
  bounds.mockReturnValue({ width: 1700 } as DOMRect);
  fireEvent(window, new Event("resize"));
  expect(splitter).toHaveAttribute("aria-valuenow", customized ? "528" : "640");
  bounds.mockRestore();
});

it("keeps the mounted conversation and shared reads while switching or editing Turns", async () => {
  mocks.getAgent2ContextManifest.mockImplementation(async (id: string) => ({ turn_id: id, manifest: {
    context_manifest_id: `context-${id}`, operation: "ORCHESTRATOR", project_id: "project_1", research_session_id: "session_1", research_turn_id: id,
    included_items: [], excluded_items: [], serialized_input: { user_message: `问题 ${id}` },
  } }));
  mocks.getAgent2ExecutionProgress.mockImplementation(async (id: string) => ({ turn_id: id, status: "COMPLETED", steps: [], warnings: [], incremental_outputs: [] }));
  const view = render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-a" />);
  const input = await screen.findByLabelText("研究问题");
  const timeline = screen.getByRole("tabpanel", { name: "对话" });
  const workbench = screen.getByRole("tabpanel", { name: "工作台" });
  await waitFor(() => expect(mocks.getProjectHistory).toHaveBeenCalled());
  fireEvent.change(input, { target: { value: "分支 A 的未发送草稿" } });
  const projectReads = mocks.getProjectHistory.mock.calls.length;
  const directoryReads = mocks.listResearchSessions.mock.calls.length;
  fireEvent.click(screen.getByRole("button", { name: "本次上下文" }));
  await waitFor(() => expect(screen.getByLabelText("本次研究使用的上下文")).toHaveAttribute("open"));
  mocks.getProjectHistory.mockRejectedValue(new Error("must not refetch on branch changes"));
  mocks.listResearchSessions.mockRejectedValue(new Error("must not refetch on branch changes"));

  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-b" />);
  expect(screen.getByLabelText("研究问题")).toBe(input);
  expect(screen.getByRole("tabpanel", { name: "对话" })).toBe(timeline);
  expect(screen.getByRole("tabpanel", { name: "工作台" })).toBe(workbench);
  expect(screen.queryByLabelText("研究页面加载状态")).not.toBeInTheDocument();
  expect(mocks.getProjectHistory).toHaveBeenCalledTimes(projectReads);
  expect(mocks.listResearchSessions).toHaveBeenCalledTimes(directoryReads);
  await waitFor(() => expect(screen.getByLabelText("本次研究使用的上下文")).toHaveAttribute("open"));
  fireEvent.click(within(screen.getByRole("tabpanel", { name: "上下文" })).getByText("本次问题"));
  expect(screen.getByText("问题 turn-b")).toBeVisible();
  expect(screen.queryByText("问题 turn-a")).not.toBeInTheDocument();
  fireEvent.change(input, { target: { value: "分支 B 的未发送草稿" } });

  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-a" />);
  expect(input).toHaveValue("分支 A 的未发送草稿");
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-b" />);
  expect(input).toHaveValue("分支 B 的未发送草稿");
  view.rerender(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-b" editTurnId="turn-b" />);
  expect(screen.getByLabelText("编辑问题")).toBe(input);
  expect(screen.getByRole("tabpanel", { name: "工作台" })).toBe(workbench);
  expect(mocks.getProjectHistory).toHaveBeenCalledTimes(projectReads);
  expect(mocks.listResearchSessions).toHaveBeenCalledTimes(directoryReads);
});

it("rejects result follow-ups with no available model or a different Turn", async () => {
  mocks.getUserModels.mockResolvedValue({ selected: [], label: "我的模型" });
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "turn-1", status: "COMPLETED", steps: [], warnings: [], incremental_outputs: [] });
  render(<ResearchPage projectId="project_1" sessionId="session_1" agent2TurnId="turn-1" />);
  await waitFor(() => expect(mocks.presentationProps.mock.lastCall?.[0].onRun).toBeTypeOf("function"));
  const run = mocks.presentationProps.mock.lastCall![0].onRun;
  const result = { research_turn_id: "turn-1", result_id: "result-1", source_object_refs: [] };
  await expect(run("rerun", result)).rejects.toThrow("选择可用模型");
  await expect(run("rerun", { ...result, research_turn_id: "foreign" })).rejects.toThrow("不匹配");
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it("requires an explicit new model choice when the selected model is no longer available", async () => {
  mocks.getUserModels.mockResolvedValueOnce({ selected: [{ provider: "personal", model: "deepseek-v4-pro" }], label: "我的模型" })
    .mockResolvedValue({ selected: [{ provider: "personal", model: "another-model" }], label: "我的模型" });
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" />);
  await user.type(await screen.findByLabelText("研究问题"), "比较材料");
  expect(screen.getByRole("button", { name: "发送" })).toBeEnabled();
  fireEvent(window, new Event("mdi:models-changed"));
  await user.click(screen.getByRole("button", { name: "研究设置" }));
  expect(await screen.findByText("之前的模型已不可用，请重新选择。")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "发送" })).toBeDisabled();
  fireEvent(window, new Event("mdi:models-changed"));
  await waitFor(() => expect(mocks.getUserModels).toHaveBeenCalledTimes(3));
  expect(screen.getByRole("combobox", { name: "本次分析模型" })).toHaveValue("");
  await user.selectOptions(screen.getByRole("combobox", { name: "本次分析模型" }), JSON.stringify(["personal", "another-model"]));
  await user.click(screen.getByRole("button", { name: "完成" }));
  expect(screen.getByRole("button", { name: "发送" })).toBeEnabled();
});

it("times out model loading without losing the question and ignores late model lists after retry", async () => {
  let resolveOld!: (value: unknown) => void;
  mocks.getUserModels.mockImplementationOnce(() => new Promise((resolve) => { resolveOld = resolve; }));
  vi.useFakeTimers();
  const view = render(<ResearchPage projectId="project_1" />);
  try {
    await act(async () => {});
    fireEvent.change(screen.getByLabelText("研究问题"), { target: { value: "保留这个问题" } });
    expect(screen.getByRole("button", { name: "发送" })).toBeDisabled();
    await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
    expect(screen.getByText("模型暂时无法读取，请重试后发送。")).toBeInTheDocument();
    expect(mocks.getUserModels.mock.calls[0][0].signal.aborted).toBe(true);
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新读取模型" })); });
    expect(screen.getByRole("button", { name: "发送" })).toBeEnabled();
    await act(async () => { resolveOld({ selected: [{ provider: "personal", model: "late-model" }], label: "迟到" }); });
    expect(screen.getByRole("button", { name: "研究设置" })).not.toHaveTextContent("late-model");
    expect(screen.getByLabelText("研究问题")).toHaveValue("保留这个问题");
  } finally { view.unmount(); vi.useRealTimers(); }
});

it("waits for the target session before exposing a composer that could overwrite a new question", async () => {
  let resolveSession!: (value: unknown) => void;
  mocks.listResearchSessions.mockResolvedValue([{ id: "session-delayed", project_id: "project_1", title: "恢复中的研究", status: "active" }]);
  mocks.getResearchSession.mockImplementationOnce(() => new Promise((resolve) => { resolveSession = resolve; }));
  render(<ResearchPage projectId="project_1" />);
  await waitFor(() => expect(mocks.getResearchSession).toHaveBeenCalledWith("session-delayed", expect.any(AbortSignal)));
  expect(screen.queryByLabelText("研究问题")).toBeNull();
  await act(async () => { resolveSession({ id: "session-delayed", project_id: "project_1", title: "恢复中的研究", status: "active", messages: [] }); });
  expect(await screen.findByLabelText("研究问题")).toBeEnabled();
});

it("shows provider status failure and offers a recoverable retry", async () => {
  const user = userEvent.setup();
  mocks.getUserModels.mockRejectedValueOnce(
    new Error("provider unavailable"),
  );
  render(<ResearchPage projectId="project_1" />);

  expect(
    await screen.findByText("模型暂时无法读取，请重试后发送。"),
  ).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重新读取模型" }));
  await waitFor(() =>
    expect(mocks.getUserModels).toHaveBeenCalledTimes(2),
  );
  await waitFor(() =>
    expect(
      screen.queryByText("模型暂时无法读取，请重试后发送。"),
    ).not.toBeInTheDocument(),
  );
});

function setupHistoricalReadRecovery() {
  const owner = {
    id: "session_read", project_id: "project_1", title: "样品对照研究", status: "active", runIds: ["job_read"],
    messages: [{ id: "post", session_id: "session_read", role: "assistant", content: "已保存结果", created_at: "2026-08-20T00:00:00Z", payload: { runId: "job_read", phase: "post_run" } }],
  };
  mocks.listResearchSessions.mockResolvedValue([owner]);
  mocks.getResearchSession.mockResolvedValue(owner);
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{ datasetId: "dataset_a", name: "样品数据" }],
    analyses: [{ jobId: "job_read", status: "completed", datasetId: "dataset_a", userQuestion: "对照样品性能", stepCount: 1, artifactCount: 1 }],
  });
  mocks.getPlannerJobArtifacts.mockResolvedValue([{ artifactId: "saved_table", jobId: "job_read", type: "table_json", name: "保存的对照表" }]);
  mocks.getPlannerJobInterpretations.mockResolvedValue({ interpretations: [{ interpretationId: "saved_interpretation", completeness: "COMPLETE", claims: [{ claimId: "saved", renderedText: "保存的样品对照结论" }], globalLimitations: [] }] });
  mocks.getPlannerInterpretationEvidence.mockResolvedValue({ interpretationId: "saved_interpretation", evidenceItems: [] });
}

it("shows saved results before optional run records settle and bounds the stalled read", async () => {
  vi.useFakeTimers();
  setupHistoricalReadRecovery();
  let finish!: (value: unknown[]) => void;
  mocks.getPlannerJobEvents.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
  await act(async () => { render(<ResearchPage projectId="project_1" runId="job_read" />); });
  expect(screen.getByText("1 个科学输出")).toBeInTheDocument();
  expect(screen.getByText("保存的样品对照结论")).toBeInTheDocument();
  expect(screen.queryByText("正在读取分析结果…")).not.toBeInTheDocument();
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("alert")).toHaveTextContent("暂时无法读取：运行记录。");
  const signal = mocks.getPlannerJobEvents.mock.calls[0][2].signal as AbortSignal;
  expect(signal.aborted).toBe(true);
  expect(screen.getByRole("button", { name: "重新读取分析结果" })).toBeEnabled();
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新读取分析结果" })); });
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  await act(async () => { finish([{ seq: 1, eventType: "tool.started", payload: { stepId: "late" } }]); });
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  expect(screen.getByText("保存的样品对照结论")).toBeInTheDocument();
  expect(mocks.createPlannerJobInterpretation).not.toHaveBeenCalled();
});

it("retains scientific content and the unsent question when a later result reread fails", async () => {
  setupHistoricalReadRecovery();
  mocks.getPlannerJobEvents.mockRejectedValueOnce(new Error("record unavailable"));
  render(<ResearchPage projectId="project_1" sessionId="session_read" runId="job_read" />);
  await screen.findByText("保存的样品对照结论");
  const result = await screen.findByTestId("scientific-result-viewer");
  const question = await screen.findByRole("textbox", { name: "研究问题" });
  fireEvent.change(question, { target: { value: "保留后续问题" } });
  mocks.getPlannerJobArtifacts.mockRejectedValueOnce(new Error("result unavailable"));
  mocks.getPlannerJobInterpretations.mockRejectedValueOnce(new Error("interpretation unavailable"));
  fireEvent.click(screen.getByRole("button", { name: "重新读取分析结果" }));
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("结果解读"));
  expect(screen.getByTestId("scientific-result-viewer")).toBe(result);
  expect(screen.getByText("保存的样品对照结论")).toBeInTheDocument();
  expect(question).toHaveValue("保留后续问题");
  expect(mocks.createPlannerJobInterpretation).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "重新读取分析结果" }));
  await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
  expect(screen.getByTestId("scientific-result-viewer")).toBe(result);
});

it("does not generate a replacement interpretation when the saved interpretation could not be read", async () => {
  setupHistoricalReadRecovery();
  mocks.getPlannerJobInterpretations.mockRejectedValueOnce(new Error("read failed"));
  render(<ResearchPage projectId="project_1" runId="job_read" />);
  await screen.findByText("暂时无法读取：结果解读。");
  expect(screen.getByText("1 个科学输出")).toBeInTheDocument();
  expect(mocks.createPlannerJobInterpretation).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "重新读取分析结果" }));
  expect(await screen.findByText("保存的样品对照结论")).toBeInTheDocument();
  expect(mocks.createPlannerJobInterpretation).not.toHaveBeenCalled();
});

it("keeps recovered interpretation evidence when a timed-out previous read finishes late", async () => {
  vi.useFakeTimers();
  setupHistoricalReadRecovery();
  let finish!: (value: unknown) => void;
  mocks.getPlannerInterpretationEvidence.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
  await act(async () => { render(<ResearchPage projectId="project_1" runId="job_read" />); });
  expect(screen.getByText("保存的样品对照结论")).toBeInTheDocument();
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("alert")).toHaveTextContent("解读依据");
  const evidence = { evidenceItemId: "fresh", semanticRole: "sample_count", displayValue: "新读取的样品依据", sourceArtifactId: "saved_table", sourceToolId: "metrics", fieldLocator: "samples" };
  mocks.getPlannerJobInterpretations.mockResolvedValue({ interpretations: [{ interpretationId: "fresh_interpretation", completeness: "COMPLETE", claims: [], globalLimitations: [] }] });
  mocks.getPlannerInterpretationEvidence.mockResolvedValue({ interpretationId: "fresh_interpretation", evidenceItems: [evidence] });
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新读取分析结果" })); });
  expect(screen.getByText("新读取的样品依据")).toBeInTheDocument();
  await act(async () => { finish({ interpretationId: "saved_interpretation", evidenceItems: [{ ...evidence, displayValue: "迟到的旧依据" }] }); });
  expect(screen.getByText("新读取的样品依据")).toBeInTheDocument();
  expect(screen.queryByText("迟到的旧依据")).not.toBeInTheDocument();
});

it("rejects evidence that belongs to a different interpretation", async () => {
  setupHistoricalReadRecovery();
  mocks.getPlannerInterpretationEvidence.mockResolvedValue({ interpretationId: "foreign_interpretation", evidenceItems: [{ evidenceItemId: "foreign", semanticRole: "sample_count", displayValue: "其他分析的依据" }] });
  render(<ResearchPage projectId="project_1" runId="job_read" />);
  await screen.findByText("暂时无法读取：解读依据。");
  expect(screen.getByText("保存的样品对照结论")).toBeInTheDocument();
  expect(screen.queryByText("其他分析的依据")).not.toBeInTheDocument();
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
      { signal: expect.any(AbortSignal) },
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
  const source = legacyResearchSource("session", "dataset_a", "实验 XRD");
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

  render(<ResearchPage projectId="project_1" {...source} />);
  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "比较实验与理论 XRD");
  await user.click(screen.getByRole("button", { name: "发送" }));

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
  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "计算 MSD");
  await user.click(screen.getByRole("button", { name: "发送" }));

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
  const source = legacyResearchSource("session", "dataset_a", "晶体结构");
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

  render(<ResearchPage projectId="project_1" {...source} />);
  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "查看当前结构的径向分布与局部环境。");
  await user.click(screen.getByRole("button", { name: "发送" }));

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
  const source = legacyResearchSource("session", "dataset_trajectory", "未包裹轨迹");
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

  render(<ResearchPage projectId="project_1" {...source} />);
  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "计算当前轨迹的 MSD 与扩散系数。");
  await user.click(screen.getByRole("button", { name: "发送" }));

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

it("keeps a global-search object as a removable candidate until turn submission", async () => {
  const user = userEvent.setup();
  render(
    <ResearchPage
      projectId="project_1"
      contextCandidateFromSearch
      viewerContext={{
        objectId: "object_search",
        versionId: "version_search_v2",
        objectType: "structure.crystal",
        displayName: "检索到的 Si 结构",
      }}
    />,
  );

  expect(
    await screen.findByRole("status", { name: "待加入本次研究的检索上下文" }),
  ).toHaveTextContent("检索到的 Si 结构");
  await user.click(screen.getByRole("button", { name: "移除" }));
  expect(
    screen.queryByRole("status", { name: "待加入本次研究的检索上下文" }),
  ).not.toBeInTheDocument();

  await user.type(
    screen.getByLabelText("研究问题"),
    "仅使用当前项目中的可用数据",
  );
  await user.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledTimes(1));
  expect(mocks.createAgent2ResearchTurn.mock.calls[0][2].ui_context).toEqual({
    active_object_refs: [], selection_refs: [], explicit_object_refs: [], scientific_selections: [], explicit_result_ids: [], explicit_finding_refs: [],
  });
  expect(mocks.resolveResearchScope).not.toHaveBeenCalled();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
});

it("submits a global-search object candidate only through explicit Context refs", async () => {
  const user = userEvent.setup();
  mocks.createAgent2ResearchTurn.mockResolvedValue({ turn_id: "turn-search" });
  render(
    <ResearchPage
      projectId="project_1"
      contextCandidateFromSearch
      viewerContext={{
        objectId: "object_search",
        versionId: "version_search_v2",
        objectType: "structure.crystal",
        displayName: "检索到的 Si 结构",
      }}
    />,
  );
  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "解释这个精确结构");
  await user.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() =>
    expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
      "project_1",
      "session_1",
      expect.objectContaining({
        ui_context: expect.objectContaining({
          explicit_object_refs: [
            expect.objectContaining({
              object_id: "object_search",
              version_id: "version_search_v2",
            }),
          ],
        }),
      }),
    ),
  );
});

it("normalizes a historical unsupported projection without duplicating the source prefix", () => {
  expect(
    displayResearchMessage({
      id: "unsupported",
      session_id: "session",
      role: "assistant",
      created_at: "2026-09-10T00:00:00Z",
      content:
        "当前 当前项目材料数据 缺少完成这项分析所需的科学属性，因此没有创建分析运行。",
    }),
  ).toBe(
    "当前项目材料数据 缺少完成这项分析所需的科学属性，因此没有创建分析运行。",
  );
});

it.each(["agent2_research_orchestration", undefined])("preserves a direct final answer from %s without inventing scientific results", source => {
  const content = "当前受控工具不支持 DFT 自洽计算。\n未执行 GW 计算。请提供已计算的电子结构数据。\n- 不以 RDF 替代。\n- 不生成带隙数值。";
  expect(displayResearchMessage({ id: "direct", session_id: "session", role: "assistant", created_at: "2026-10-08T00:00:00Z",
    payload: { messageKind: "ASSISTANT_FINAL", source }, content })).toBe(content);
});

it("keeps a persisted scientific final readable without rendering the raw machine contract", () => {
  const rendered = displayResearchMessage({
    id: "agent2-final",
    session_id: "session",
    role: "assistant",
    created_at: "2026-08-31T00:00:00Z",
    payload: { messageKind: "ASSISTANT_FINAL", source: "agent2_scientific_interpreter" },
    content: "联合分析电子能带与态密度来源\nBand 结果提供了带隙事实 fact.band，值为 0.6 eV，单位 eV。该事实来自证据 evidence.band。Band 结果提供了 k 点计数事实 fact.k，值为 3（单位 count）。\n- Band 结果提供了带隙事实 fact.band，值为 0.6 eV，单位 eV。该事实来自证据 evidence.band。\n- Band 结果提供了 k 点计数事实 fact.k，值为 3（单位 count）。\n限制：\n- Band values are supplied electronic data.",
  });
  expect(rendered).toBe(
    "Band 结果提供了带隙事实，值为 0.6 eV，单位 eV。Band 结果提供了 k 点计数事实，值为 3（单位 count）。\n\n完整结构化结果已在右侧工作台提供。",
  );
  expect(rendered).not.toContain("Band values are supplied electronic data");
  expect(rendered).not.toContain("限制：");
});

it.each(["agent2_scientific_interpreter", "agent2_research_orchestrator"])("preserves exact final Markdown from %s after streaming", source => {
  const content = "## 分析结果\n\n数密度：0.0499677265116949 Å⁻³。\n\n```json\n{\"schema\": \"1.0\", \"job_id\": \"example\"}\n```\n\n### 限制\n\n- 仅对应当前来源。";
  expect(displayResearchMessage({ id: "markdown-final", session_id: "session", role: "assistant", created_at: "2026-10-09T00:00:00Z",
    payload: { messageKind: "ASSISTANT_FINAL", source, responseFormat: "markdown" }, content })).toBe(content);
});

it("shares scientific terminology with the result panel while preserving user-authored text", () => {
  const message = {
    id: "volume-final", session_id: "session", role: "assistant" as const,
    created_at: "2026-10-06T00:00:00Z", payload: { messageKind: "ASSISTANT_FINAL", source: "agent2_scientific_interpreter" },
    content: "体数据解读\n轨道密度（orbital_density），积分语义为 electron_count。\n- 轨道密度（orbital_density），积分语义为 electron_count。\n- 端点策略为 excluded，不能推断单轨道占据数。",
  };
  expect(displayResearchMessage(message)).toBe("轨道密度，积分表示电子数。网格不包含终点，不能推断单轨道占据数。\n\n完整结构化结果已在右侧工作台提供。");
  expect(displayResearchMessage({ ...message, role: "user" })).toBe(message.content);
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
    reason: "已根据当前研究问题、数据范围和可用科学方法确定这一步。",
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
    reason: "用于比较实验与理论衍射证据，同时保留峰匹配和物相判断的限制。",
  });
  expect(userFacingPlanStep("", "", 0, "phonon.band_dos")).toEqual({
    purpose: "组合声子色散与态密度",
  });
  expect(userFacingPlanStep("", "", 0, "future.scientific_tool")).toEqual({
    purpose: "科学分析步骤 1",
  });
  expect(
    userFacingPlanStep(
      "Build deterministic Profile-bound PCA composition space.",
      "The request explicitly asks for composition-space exploration on a Profile 2.0 formula-bearing table.",
      0,
      "dataset.composition_space",
    ),
  ).toEqual({
    purpose: "分析材料组成空间",
    reason: "用于观察材料组成分布，并判断是否存在值得继续研究的材料分组。",
  });
});

it("keeps identity-shaped dataset names and validation internals out of scientist copy", () => {
  expect(
    scientistDatasetLabel({
      status: "READY",
      dataset_id: "dataset_phase10k4_fixture",
      dataset_name: "dataset_phase10k4_fixture",
    }),
  ).toBe("当前项目材料数据");
  expect(
    scientistDatasetLabel({
      status: "READY",
      dataset_id: "dataset-1",
      dataset_name: "锂扩散轨迹",
    }),
  ).toBe("锂扩散轨迹");

  const validation = new PlannerApiError(
    "Input should be a valid string",
    422,
    { detail: [{ msg: "Input should be a valid string" }] },
  );
  expect(scientistFacingResearchRequestError(validation)).toContain(
    "缺少可验证的科学数据描述或参数",
  );
  expect(scientistFacingResearchRequestError(validation)).not.toContain(
    "Input should",
  );
});

it("does not infer that no work was admitted from a transport error", () => {
  const feedback = scientistFacingResearchRequestError(new TypeError("Failed to fetch"));
  expect(feedback).toContain("检查最新进度");
  expect(feedback).not.toContain("没有创建");
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

it("bounds stalled research-page reads and ignores their late response after retry", async () => {
  let finish!: (value: unknown) => void;
  mocks.listResearchSessions.mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
  vi.useFakeTimers();
  render(<ResearchPage projectId="project_1" />);
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByText("研究记录列表暂时无法读取，请重试后继续。")).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "可用数据" })).toBeInTheDocument();
  expect(mocks.listResearchSessions.mock.calls[0][1].aborted).toBe(true);
  await act(async () => fireEvent.click(screen.getByRole("button", { name: "重新读取研究内容" })));
  expect(screen.getByRole("textbox", { name: "研究问题" })).toBeInTheDocument();
  await act(async () => finish([{ id: "late", project_id: "project_1", title: "迟到的旧记录", status: "active" }]));
  fireEvent.click(screen.getByRole("button", { name: "研究记录" }));
  expect(screen.queryByText("迟到的旧记录")).toBeNull();
});

function independentConversation(id = "session_exact", project = "project_1") {
  return { id, project_id: project, title: "独立恢复的研究", status: "active", messages: [{ id: `${id}_answer`, session_id: id, role: "assistant", content: "这是已保存的研究答复", created_at: "2026-08-20T00:00:00Z" }] };
}

it("opens an exact conversation even when both surrounding directories fail", async () => {
  mocks.listResearchSessions.mockRejectedValueOnce(new Error("directory offline"));
  mocks.getProjectHistory.mockRejectedValueOnce(new Error("history offline"));
  mocks.getResearchSession.mockResolvedValue(independentConversation());
  render(<ResearchPage projectId="project_1" sessionId="session_exact" />);
  expect(await screen.findByRole("article", { name: "研究助手消息" })).toHaveTextContent("这是已保存的研究答复");
  expect(screen.queryByRole("heading", { name: "研究内容暂时无法加载" })).not.toBeInTheDocument();
  expect(screen.getByText("项目权限暂时无法确认。请重新读取研究内容后再发送。")).toBeInTheDocument();
  expect(screen.queryByRole("textbox", { name: "研究问题" })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "重新读取项目数据" }));
  expect(await screen.findByRole("textbox", { name: "研究问题" })).toBeInTheDocument();
  expect(mocks.createResearchSession).not.toHaveBeenCalled();
});

it("reads the selected conversation before a stalled project-history request settles", async () => {
  vi.useFakeTimers();
  let finish!: (value: unknown) => void;
  mocks.listResearchSessions.mockResolvedValue([independentConversation()]);
  mocks.getResearchSession.mockResolvedValue(independentConversation());
  mocks.getProjectHistory.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
  await act(async () => { render(<ResearchPage projectId="project_1" />); });
  expect(screen.getByRole("article", { name: "研究助手消息" })).toHaveTextContent("这是已保存的研究答复");
  expect(screen.queryByRole("textbox", { name: "研究问题" })).not.toBeInTheDocument();
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("heading", { name: "项目数据暂时无法读取" })).toBeInTheDocument();
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新读取项目数据" })); });
  expect(screen.getByRole("textbox", { name: "研究问题" })).toBeInTheDocument();
  await act(async () => { finish({ project: { id: "foreign", name: "迟到的项目" }, datasets: [], analyses: [] }); });
  expect(screen.queryByText("迟到的项目")).not.toBeInTheDocument();
  expect(screen.queryByRole("heading", { name: "项目数据暂时无法读取" })).not.toBeInTheDocument();
});

it("shows a full retry only when none of the initial reads succeeds", async () => {
  mocks.listResearchSessions.mockRejectedValueOnce(new Error("directory offline"));
  mocks.getProjectHistory.mockRejectedValueOnce(new Error("history offline"));
  mocks.getResearchSession.mockRejectedValueOnce(new Error("session offline"));
  render(<ResearchPage projectId="project_1" sessionId="session_exact" />);
  expect(await screen.findByRole("heading", { name: "研究内容暂时无法加载" })).toBeInTheDocument();
  mocks.getResearchSession.mockResolvedValue(independentConversation());
  fireEvent.click(screen.getByRole("button", { name: "重新加载" }));
  expect(await screen.findByRole("article", { name: "研究助手消息" })).toHaveTextContent("这是已保存的研究答复");
});

it("never transfers another session's run into an explicit conversation link", async () => {
  const exact = independentConversation();
  mocks.getResearchSession.mockResolvedValue(exact);
  mocks.listResearchSessions.mockResolvedValue([exact, { ...independentConversation("other"), runIds: ["job_other"] }]);
  mocks.getProjectHistory.mockResolvedValue({ project: { id: "project_1", name: "研究项目", role: "owner" }, datasets: [], analyses: [{ jobId: "job_other", status: "completed", researchSessionId: "other", userQuestion: "另一段研究", stepCount: 1, artifactCount: 0 }] });
  render(<ResearchPage projectId="project_1" sessionId="session_exact" runId="job_other" />);
  await screen.findByRole("article", { name: "研究助手消息" });
  expect(mocks.getResearchSession).toHaveBeenCalledWith("session_exact", expect.any(AbortSignal));
  expect(mocks.getResearchSession).not.toHaveBeenCalledWith("other", expect.anything());
  expect(mocks.createResearchAssistantProjection).not.toHaveBeenCalled();
  expect(mocks.createPlannerJobInterpretation).not.toHaveBeenCalled();
});

it("retains the current composer and data when refreshing research records fails", async () => {
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" fresh />);
  const composer = await screen.findByRole("textbox", { name: "研究问题" });
  await user.type(composer, "还没发送的问题");
  mocks.listResearchSessions.mockRejectedValueOnce(new Error("private transport failure"));
  fireEvent(window, new Event("online"));
  await screen.findByText("暂时无法读取：研究记录列表。已打开的内容和输入仍然保留。");
  expect(screen.getByRole("textbox", { name: "研究问题" })).toBe(composer);
  expect(composer).toHaveValue("还没发送的问题");
  expect(screen.queryByText("private transport failure")).toBeNull();
  await user.click(screen.getByRole("button", { name: "重新读取研究内容" }));
  await waitFor(() => expect(screen.queryByText("暂时无法读取：研究记录列表。已打开的内容和输入仍然保留。")).toBeNull());
  expect(composer).toHaveValue("还没发送的问题");
});

it("keeps a failed rename draft inside its dialog and requires a successful reread after timeout", async () => {
  const user = userEvent.setup();
  const record = { id: "editable", project_id: "project_1", title: "可重命名的研究", status: "active" };
  mocks.listResearchSessions.mockResolvedValue([record]);
  let finish!: (value: unknown) => void;
  mocks.updateResearchSession.mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
  render(<ResearchPage projectId="project_1" fresh />);
  await user.click(await screen.findByRole("button", { name: "研究记录" }));
  await user.click(screen.getByRole("button", { name: "管理 可重命名的研究" }));
  await user.click(screen.getByRole("menuitem", { name: "重命名" }));
  const modal = screen.getByRole("dialog", { name: "重命名研究" });
  await user.clear(within(modal).getByLabelText("研究名称"));
  await user.type(within(modal).getByLabelText("研究名称"), "新的材料研究名称");
  vi.useFakeTimers();
  fireEvent.click(within(modal).getByRole("button", { name: "保存名称" }));
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(within(modal).getByRole("alert")).toHaveTextContent("尚未确认重命名的结果");
  expect(within(modal).getByLabelText("研究名称")).toHaveValue("新的材料研究名称");
  expect(within(modal).getByRole("button", { name: "保存名称" })).toBeDisabled();
  mocks.listResearchSessions.mockRejectedValueOnce(new Error("refresh failed"));
  await act(async () => fireEvent.click(within(modal).getByRole("button", { name: "重新读取研究记录" })));
  expect(within(modal).getByRole("button", { name: "保存名称" })).toBeDisabled();
  await act(async () => fireEvent.click(within(modal).getByRole("button", { name: "重新读取研究记录" })));
  expect(within(modal).getByRole("button", { name: "保存名称" })).toBeEnabled();
  await act(async () => finish({ ...record, title: "迟到的修改" }));
  expect(screen.queryByText("迟到的修改")).toBeNull();
  mocks.updateResearchSession.mockResolvedValueOnce({ ...record, title: "新的材料研究名称" });
  await act(async () => fireEvent.click(within(modal).getByRole("button", { name: "保存名称" })));
  expect(screen.queryByRole("dialog", { name: "重命名研究" })).toBeNull();
  expect(screen.getByRole("button", { name: "管理 新的材料研究名称" })).toBeInTheDocument();
});

it("removes hidden research selections and confirms exactly the visible batch", async () => {
  const user = userEvent.setup();
  const records = [{ id: "a", project_id: "project_1", title: "氧化物样本", status: "active" }, { id: "b", project_id: "project_1", title: "金属样本", status: "active" }];
  mocks.listResearchSessions.mockResolvedValue(records);
  mocks.bulkUpdateResearchSessions.mockResolvedValue({ action: "ARCHIVE", sessionIds: ["a"], count: 1 });
  render(<ResearchPage projectId="project_1" fresh />);
  await user.click(await screen.findByRole("button", { name: "研究记录" }));
  await user.click(screen.getByRole("button", { name: "批量管理" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 氧化物样本" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 金属样本" }));
  await user.type(screen.getByRole("searchbox", { name: "搜索研究记录" }), "氧化物");
  expect(screen.getByText("1 项已选")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "归档所选" }));
  const modal = screen.getByRole("dialog", { name: "归档研究记录" });
  expect(modal).toHaveTextContent("氧化物样本");
  expect(modal).not.toHaveTextContent("金属样本");
  await user.click(within(modal).getByRole("button", { name: "确认归档" }));
  expect(mocks.bulkUpdateResearchSessions).toHaveBeenCalledWith("project_1", ["a"], "ARCHIVE", expect.any(AbortSignal));
});

it("rejects a renamed record returned for another project without replacing the current name", async () => {
  const user = userEvent.setup();
  const record = { id: "editable", project_id: "project_1", title: "原研究记录", status: "active" };
  mocks.listResearchSessions.mockResolvedValue([record]);
  mocks.updateResearchSession.mockResolvedValueOnce({ ...record, project_id: "other-project", title: "错误项目记录" });
  render(<ResearchPage projectId="project_1" fresh />);
  await user.click(await screen.findByRole("button", { name: "研究记录" }));
  await user.click(screen.getByRole("button", { name: "管理 原研究记录" }));
  await user.click(screen.getByRole("menuitem", { name: "重命名" }));
  await user.click(screen.getByRole("button", { name: "保存名称" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("尚未确认重命名的结果");
  expect(screen.queryByText("错误项目记录")).toBeNull();
  expect(screen.getByRole("button", { name: "管理 原研究记录" })).toBeInTheDocument();
});

it("retains successful batches and retries only remaining research records after a later batch fails", async () => {
  const user = userEvent.setup();
  let records = Array.from({ length: 105 }, (_, index) => ({ id: `batch-${index}`, project_id: "project_1", title: `研究 ${index}`, status: "active" }));
  mocks.listResearchSessions.mockImplementation(async () => records);
  let failSecond = true;
  mocks.bulkUpdateResearchSessions.mockImplementation(async (_project: string, ids: string[], action: string) => {
    if (ids.length === 5 && failSecond) { failSecond = false; throw new Error("unconfirmed second batch"); }
    records = records.map((item) => ids.includes(item.id) ? { ...item, status: "archived" } : item);
    return { action, sessionIds: ids, count: ids.length };
  });
  render(<ResearchPage projectId="project_1" fresh />);
  await user.click(await screen.findByRole("button", { name: "研究记录" }));
  await user.click(screen.getByRole("button", { name: "批量管理" }));
  await user.click(screen.getByRole("button", { name: "全选当前" }));
  await user.click(screen.getByRole("button", { name: "归档所选" }));
  await user.click(screen.getByRole("button", { name: "确认归档" }));
  const remaining = await screen.findByRole("dialog", { name: "归档 5 项研究记录" });
  expect(within(remaining).getAllByRole("listitem")).toHaveLength(5);
  expect(mocks.bulkUpdateResearchSessions.mock.calls.map((call) => call[1].length)).toEqual([100, 5]);
  await user.click(within(remaining).getByRole("button", { name: "重新读取研究记录" }));
  await waitFor(() => expect(within(remaining).getByRole("button", { name: "确认归档" })).toBeEnabled());
  await user.click(within(remaining).getByRole("button", { name: "确认归档" }));
  expect(mocks.bulkUpdateResearchSessions.mock.calls.map((call) => call[1].length)).toEqual([100, 5, 5]);
  expect(screen.getByRole("button", { name: "当前 0" })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "已归档 105" })).toBeInTheDocument();
});

it("recovers an explicit session independently of an incomplete directory without choosing another record", async () => {
  mocks.listResearchSessions.mockResolvedValue([{ id: "unrelated", project_id: "project_1", title: "别的研究", status: "active" }]);
  mocks.getResearchSession.mockResolvedValue({ id: "exact", project_id: "project_1", title: "精确链接的研究", status: "active", messages: [] });
  render(<ResearchPage projectId="project_1" sessionId="exact" />);
  await screen.findByRole("textbox", { name: "研究问题" });
  expect(mocks.getResearchSession).toHaveBeenCalledWith("exact", expect.any(AbortSignal));
  expect(mocks.getResearchSession.mock.calls.every(([id]) => id === "exact")).toBe(true);
  expect(screen.getByRole("heading", { name: "对话" })).toHaveAttribute("title", "精确链接的研究");
});

function setupTurnOnlyLink() {
  const turn: Agent2TurnDetail = {
    turn_id: "turn-owned", research_session_id: "session-owned", project_id: "project_1",
    sequence_no: 1, status: "ANSWERED", created_at: "2026-10-08T00:00:00Z",
    user_message: { id: "message-owned", role: "user", content: "分别比较 Si、Cu 和 NaCl 的径向分布" },
    context: null,
  };
  const owner = {
    id: turn.research_session_id, project_id: turn.project_id, title: "三个材料的联合研究", status: "active",
    messages: [{ ...turn.user_message, session_id: turn.research_session_id, created_at: turn.created_at }],
  };
  mocks.getAgent2ResearchTurn.mockResolvedValue(turn);
  mocks.getResearchSession.mockResolvedValue(owner);
  mocks.listResearchSessions.mockResolvedValue([{ id: "unrelated", project_id: "project_1", title: "最近的其他研究", status: "active" }]);
  mocks.listAgent2ResearchTurns.mockResolvedValue([turn]);
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: turn.turn_id, status: "ANSWERED", steps: [], warnings: [], incremental_outputs: [] });
  mocks.getAgent2ContextManifest.mockResolvedValue({ turn_id: turn.turn_id, manifest: {
    context_manifest_id: "context-owned", operation: "ORCHESTRATOR", project_id: turn.project_id,
    research_session_id: turn.research_session_id, research_turn_id: turn.turn_id,
    included_items: [], excluded_items: [], serialized_input: { user_message: turn.user_message.content },
  } });
  return { turn, owner };
}

it("gives a plain answer the reading area while keeping context one action away", async () => {
  const { turn, owner } = setupTurnOnlyLink();
  const user = userEvent.setup();
  render(<ResearchPage projectId="project_1" sessionId={owner.id} agent2TurnId={turn.turn_id} />);
  await screen.findByRole("region", { name: "分析进度" });
  const workbench = screen.getByRole("region", { name: "项目研究工作台" });
  expect(workbench).toHaveAttribute("data-workbench-open", "false");
  expect(screen.queryByRole("button", { name: "本次科学结果" })).toBeNull();
  const context = screen.getByRole("button", { name: "本次上下文" });
  await user.click(context);
  expect(workbench).toHaveAttribute("data-workbench-open", "true");
  expect(context).toHaveAttribute("aria-expanded", "true");
  await user.click(screen.getByRole("button", { name: "收起工作台" }));
  expect(workbench).toHaveAttribute("data-workbench-open", "false");
  await waitFor(() => expect(context).toHaveFocus());
  expect(mocks.routerPush).not.toHaveBeenCalled();
});

it("opens scientific results automatically and preserves an explicit collapse until the branch changes", async () => {
  const { turn, owner } = setupTurnOnlyLink();
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: turn.turn_id, status: "COMPLETED", steps: [], warnings: [], incremental_outputs: [] });
  const view = render(<ResearchPage projectId="project_1" sessionId={owner.id} agent2TurnId={turn.turn_id} />);
  const results = await screen.findByRole("button", { name: "本次科学结果" });
  const workbench = screen.getByRole("region", { name: "项目研究工作台" });
  expect(workbench).toHaveAttribute("data-workbench-open", "true");
  fireEvent.click(screen.getByRole("button", { name: "收起工作台" }));
  view.rerender(<ResearchPage projectId="project_1" sessionId={owner.id} agent2TurnId={turn.turn_id} />);
  expect(workbench).toHaveAttribute("data-workbench-open", "false");
  fireEvent.click(results);
  expect(workbench).toHaveAttribute("data-workbench-open", "true");
  expect(results).toHaveAttribute("aria-expanded", "true");
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: "other-answer", status: "ANSWERED", steps: [], warnings: [], incremental_outputs: [] });
  view.rerender(<ResearchPage projectId="project_1" sessionId={owner.id} agent2TurnId="other-answer" />);
  await waitFor(() => expect(mocks.getAgent2ExecutionProgress).toHaveBeenCalledWith("other-answer", expect.anything()));
  expect(workbench).toHaveAttribute("data-workbench-open", "false");
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it.each(["COMPLETED", "FAILED", "CANCELED"])("restores a cited result in the workbench for %s and preserves the page while switching items", async status => {
  const { turn, owner } = setupTurnOnlyLink();
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: turn.turn_id, status, preserved_result_available: true, steps: [], warnings: [], incremental_outputs: [] });
  const props = { projectId: "project_1", sessionId: owner.id, agent2TurnId: turn.turn_id, resultTargetSnapshotId: "snapshot-materials", resultTargetItemId: "Cu" };
  const view = render(<ResearchPage {...props} />);
  await screen.findByRole("region", { name: "权威 ResearchTurn 科学呈现" });
  const workbench = screen.getByRole("region", { name: "项目研究工作台" });
  const composer = screen.getByRole("textbox", { name: "研究问题" });
  fireEvent.change(composer, { target: { value: "保留未发送的问题" } });
  expect(screen.getByRole("tab", { name: "工作台" })).toHaveAttribute("aria-selected", "true");
  expect(mocks.presentationProps).toHaveBeenLastCalledWith(expect.objectContaining({ resultTarget: { snapshotId: "snapshot-materials", itemId: "Cu", requestKey: 0 } }));
  fireEvent.click(screen.getByRole("button", { name: "本次上下文" }));
  view.rerender(<ResearchPage {...props} />);
  expect(screen.getByRole("tab", { name: "上下文" })).toHaveAttribute("aria-selected", "true");
  const readCount = mocks.getAgent2ExecutionProgress.mock.calls.length;
  view.rerender(<ResearchPage {...props} resultTargetItemId="Si" />);
  expect(screen.getByRole("tab", { name: "结果" })).toHaveAttribute("aria-selected", "true");
  expect(screen.getByRole("tab", { name: "工作台" })).toHaveAttribute("aria-selected", "true");
  expect(screen.getByRole("region", { name: "项目研究工作台" })).toBe(workbench);
  expect(screen.getByRole("textbox", { name: "研究问题" })).toBe(composer);
  expect(composer).toHaveValue("保留未发送的问题");
  expect(mocks.presentationProps).toHaveBeenLastCalledWith(expect.objectContaining({ resultTarget: { snapshotId: "snapshot-materials", itemId: "Si", requestKey: 0 } }));
  expect(mocks.getAgent2ExecutionProgress).toHaveBeenCalledTimes(readCount);
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.routerPush).not.toHaveBeenCalled();
});

it("reopens an already selected result citation and keeps navigation parameters out of model context", async () => {
  const { turn, owner } = setupTurnOnlyLink();
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: turn.turn_id, status: "COMPLETED", steps: [], warnings: [], incremental_outputs: [] });
  mocks.getAgent2ContextManifest.mockResolvedValue({ turn_id: turn.turn_id, manifest: {
    context_manifest_id: "context-copper", operation: "INTERPRETER", project_id: turn.project_id,
    research_session_id: owner.id, research_turn_id: turn.turn_id,
    included_items: [{ item_id: "result_1", kind: "SCIENTIFIC_RESULT", authorization_checked: true,
      result_ref: "snapshot-materials", server_side_source_identity: "snapshot-materials", serialized_representation: { result_item_ids: ["Cu"] } }],
    excluded_items: [], serialized_input: { result: { result_items: [{ id: "Cu", result_type: "structure.rdf", source_labels: ["Cu.cif"] }] } },
  }, result_sources: [{ result_snapshot_id: "snapshot-materials", project_id: turn.project_id, research_session_id: owner.id, research_turn_id: turn.turn_id }] });
  render(<ResearchPage projectId="project_1" sessionId={owner.id} agent2TurnId={turn.turn_id} resultTargetSnapshotId="snapshot-materials" resultTargetItemId="Cu" />);
  await screen.findByRole("region", { name: "权威 ResearchTurn 科学呈现" });
  const preventNativeNavigation = (event: Event) => event.preventDefault();
  document.addEventListener("click", preventNativeNavigation);
  try {
    for (const requestKey of [1, 2]) {
      fireEvent.click(screen.getByRole("button", { name: "本次上下文" }));
      fireEvent.click(await screen.findByRole("link", { name: "打开结果：Cu.cif · 径向分布函数（RDF）" }));
      expect(screen.getByRole("tab", { name: "结果" })).toHaveFocus();
      expect(mocks.presentationProps).toHaveBeenLastCalledWith(expect.objectContaining({ resultTarget: { snapshotId: "snapshot-materials", itemId: "Cu", requestKey } }));
    }
  } finally { document.removeEventListener("click", preventNativeNavigation); }
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  const composer = screen.getByRole("textbox", { name: "研究问题" });
  fireEvent.change(composer, { target: { value: "请解释 RDF 的定义" } });
  await waitFor(() => expect(screen.getByRole("button", { name: "发送" })).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledTimes(1));
  expect(mocks.createAgent2ResearchTurn.mock.calls[0][2].ui_context).toEqual({
    active_object_refs: [], selection_refs: [], explicit_object_refs: [], scientific_selections: [], explicit_result_ids: [], explicit_finding_refs: [],
  });
});

it.each(["ANSWERED", "NEEDS_CLARIFICATION", "UNSUPPORTED", "PLAN_REJECTED"])("opens a restored %s response in the conversation and respects later panel choices", async status => {
  const { turn, owner } = setupTurnOnlyLink();
  turn.status = status;
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: turn.turn_id, status, steps: [], warnings: [], incremental_outputs: [] });
  const view = render(<ResearchPage projectId="project_1" sessionId={owner.id} agent2TurnId={turn.turn_id} />);
  await waitFor(() => expect(screen.getByRole("tab", { name: "对话" })).toHaveAttribute("aria-selected", "true"));
  fireEvent.click(screen.getByRole("tab", { name: "工作台" }));
  view.rerender(<ResearchPage projectId="project_1" sessionId={owner.id} agent2TurnId={turn.turn_id} />);
  expect(screen.getByRole("tab", { name: "工作台" })).toHaveAttribute("aria-selected", "true");
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it("renders incoming Markdown, preserves reading position, and keeps the saved answer while the branch directory catches up", async () => {
  class Stream extends EventTarget {
    static current: Stream;
    close = vi.fn();
    constructor() { super(); Stream.current = this; }
    emit(kind: string, payload: Record<string, unknown>) {
      this.dispatchEvent(new MessageEvent(kind, { data: JSON.stringify(payload) }));
    }
  }
  vi.stubGlobal("EventSource", Stream);
  try {
    const { turn, owner } = setupTurnOnlyLink();
    turn.status = "ORCHESTRATING";
    const progress = { turn_id: turn.turn_id, status: "ORCHESTRATING", steps: [], warnings: [], incremental_outputs: [] };
    mocks.getAgent2ExecutionProgress.mockResolvedValue(progress);
    const { container } = render(<ResearchPage projectId="project_1" sessionId={owner.id} agent2TurnId={turn.turn_id} />);
    await screen.findByText("正在组织研究");
    await waitFor(() => expect(Stream.current).toBeDefined());
    const source = Stream.current;
    const frame = { turn_id: turn.turn_id, response_id: "response-live" };
    act(() => source.emit("answer.delta", { ...frame, revision: 1, text: "## 数密度\n\n1. **NaCl" }));
    const draft = await screen.findByRole("article", { name: "正在生成的研究回答" });
    expect(draft).toHaveAttribute("aria-busy", "true");
    expect(within(draft).getByText("NaCl").tagName).toBe("STRONG");
    expect(screen.getByRole("button", { name: "停止生成" })).toBeEnabled();
    expect(screen.queryByRole("region", { name: "分析进度" })).toBeNull();
    expect(screen.queryByRole("button", { name: "从输入区取消当前分析" })).toBeNull();
    expect(screen.getByRole("tab", { name: "对话" })).toHaveAttribute("aria-selected", "true");
    fireEvent.click(screen.getByRole("tab", { name: "工作台" }));
    const scroller = container.querySelector<HTMLElement>(".conversation-history")!;
    Object.defineProperty(scroller, "scrollHeight", { configurable: true, value: 1400 });
    Object.defineProperty(scroller, "clientHeight", { configurable: true, value: 400 });
    scroller.scrollTop = 120;
    fireEvent.scroll(scroller);
    act(() => source.emit("answer.delta", { ...frame, revision: 2, text: "** — 0.043419 Å⁻³" }));
    expect(screen.getByRole("tab", { name: "工作台" })).toHaveAttribute("aria-selected", "true");
    expect(scroller.scrollTop).toBe(120);
    expect(screen.getByRole("button", { name: "回到对话底部" })).toHaveAttribute("aria-controls", scroller.id);
    expect(within(draft).getByRole("listitem")).toHaveTextContent("NaCl — 0.043419 Å⁻³");
    const final = "## 数密度\n\n1. **NaCl** — 0.043419 Å⁻³\n\n来自已保存结果。";
    mocks.getResearchSession.mockResolvedValue({ ...owner, messages: [...owner.messages, {
      id: "saved-live", session_id: owner.id, role: "assistant", content: final, created_at: turn.created_at,
      payload: { messageKind: "ASSISTANT_FINAL", turnId: turn.turn_id },
    }] });
    mocks.getAgent2ExecutionProgress.mockResolvedValue({ ...progress, status: "ANSWERED" });
    act(() => source.emit("answer.completed", { turn_id: turn.turn_id, message_id: "saved-live", text: final, status: "ANSWERED" }));
    const saved = await screen.findByRole("article", { name: "研究助手消息" });
    await waitFor(() => expect(screen.queryByRole("article", { name: "正在生成的研究回答" })).toBeNull());
    expect(within(saved).getByText("来自已保存结果。")).toBeVisible();
    expect(screen.getAllByRole("heading", { name: "数密度" })).toHaveLength(1);
    expect(screen.getByRole("tab", { name: "工作台" })).toHaveAttribute("aria-selected", "true");
    expect(scroller.scrollTop).toBe(120);
    fireEvent.click(screen.getByRole("tab", { name: "对话" }));
    const jump = screen.getByRole("button", { name: "回到对话底部" });
    jump.focus();
    fireEvent.click(jump);
    expect(scroller.scrollTop).toBe(1000);
    expect(scroller).toHaveFocus();
    expect(screen.queryByRole("button", { name: "回到对话底部" })).toBeNull();
    expect(source.close).toHaveBeenCalled();
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  } finally { vi.unstubAllGlobals(); }
});

it("follows a saved answer that arrives before its first streaming delta", async () => {
  class Stream extends EventTarget {
    static current: Stream;
    close = vi.fn();
    constructor() { super(); Stream.current = this; }
  }
  vi.stubGlobal("EventSource", Stream);
  try {
    const { turn, owner } = setupTurnOnlyLink();
    turn.status = "ORCHESTRATING";
    const progress = { turn_id: turn.turn_id, status: "ORCHESTRATING", steps: [], warnings: [], incremental_outputs: [] };
    mocks.getAgent2ExecutionProgress.mockResolvedValue(progress);
    render(<ResearchPage projectId="project_1" sessionId={owner.id} agent2TurnId={turn.turn_id} />);
    await screen.findByText("正在组织研究");
    await waitFor(() => expect(Stream.current).toBeDefined());
    const scroller = screen.getByRole("region", { name: "对话内容" });
    Object.defineProperty(scroller, "scrollHeight", { configurable: true, value: 1400 });
    Object.defineProperty(scroller, "clientHeight", { configurable: true, value: 400 });
    const content = "## 记录核验\n\n完整回答已保存。";
    mocks.getResearchSession.mockResolvedValue({ ...owner, messages: [...owner.messages, {
      id: "saved-fast", session_id: owner.id, role: "assistant", content, created_at: turn.created_at,
      payload: { messageKind: "ASSISTANT_FINAL", turnId: turn.turn_id },
    }] });
    mocks.getAgent2ExecutionProgress.mockResolvedValue({ ...progress, status: "ANSWERED" });
    act(() => Stream.current.dispatchEvent(new MessageEvent("answer.completed", { data: JSON.stringify({
      turn_id: turn.turn_id, message_id: "saved-fast", text: content, status: "ANSWERED",
    }) })));
    expect(await screen.findByRole("heading", { name: "记录核验" })).toBeVisible();
    await waitFor(() => expect(scroller.scrollTop).toBe(1000));
    expect(screen.queryByRole("button", { name: "回到对话底部" })).toBeNull();
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  } finally { vi.unstubAllGlobals(); }
});

it("stops an incoming answer before progress has loaded and ignores the stale initial read", async () => {
  class Stream extends EventTarget {
    static current: Stream;
    close = vi.fn();
    constructor() { super(); Stream.current = this; }
    emit(kind: string, payload: Record<string, unknown>) {
      this.dispatchEvent(new MessageEvent(kind, { data: JSON.stringify(payload) }));
    }
  }
  vi.stubGlobal("EventSource", Stream);
  try {
    const { turn, owner } = setupTurnOnlyLink();
    turn.status = "ORCHESTRATING";
    const progress = { turn_id: turn.turn_id, status: "ORCHESTRATING", steps: [], warnings: [], incremental_outputs: [] };
    let finishInitial!: (value: typeof progress) => void;
    mocks.getAgent2ExecutionProgress.mockReturnValueOnce(new Promise(resolve => { finishInitial = resolve; }))
      .mockResolvedValue({ ...progress, status: "CANCELED" });
    mocks.cancelAgent2Execution.mockResolvedValue({ turn_id: turn.turn_id, status: "CANCELED" });
    render(<ResearchPage projectId="project_1" sessionId={owner.id} agent2TurnId={turn.turn_id} />);
    await screen.findByRole("textbox", { name: "研究问题" });
    await waitFor(() => expect(Stream.current).toBeDefined());
    act(() => Stream.current.emit("answer.delta", { turn_id: turn.turn_id, response_id: "early", revision: 1, text: "## 数密度\n\n正在比较" }));
    const stop = screen.getByRole("button", { name: "停止生成" });
    expect(stop).toBeEnabled();
    fireEvent.click(stop);
    await waitFor(() => expect(mocks.cancelAgent2Execution).toHaveBeenCalledWith(turn.turn_id, { signal: expect.any(AbortSignal) }));
    expect(mocks.cancelAgent2Execution).toHaveBeenCalledTimes(1);
    expect(mocks.getAgent2ExecutionProgress.mock.calls[0][1].signal.aborted).toBe(true);
    await act(async () => { finishInitial(progress); });
    expect(await screen.findByText("分析已取消", { exact: true })).toBeVisible();
    expect(screen.queryByRole("article", { name: "正在生成的研究回答" })).toBeNull();
    expect(screen.queryByRole("button", { name: "停止生成" })).toBeNull();
    expect(screen.queryByText("正在组织研究")).toBeNull();
    expect(Stream.current.close).toHaveBeenCalled();
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  } finally { vi.unstubAllGlobals(); }
});

it("formats a saved assistant ranking while preserving user-authored question markup", async () => {
  const conversation = independentConversation();
  conversation.messages[0].content = "已保存的数密度：\n\n1. **NaCl_derived.cif** — 0.043419 Å⁻³\n2. **Si_diamond_synthetic.cif** — 0.049968 Å⁻³";
  conversation.messages.unshift({ id: "original-question", session_id: conversation.id, role: "user", content: "保留 **原始文本**\nE**2 + v**2", created_at: "2026-08-19T00:00:00Z" });
  const before = JSON.stringify(conversation);
  mocks.getResearchSession.mockResolvedValue(conversation);
  render(<ResearchPage projectId="project_1" sessionId="session_exact" />);
  const reply = await screen.findByRole("article", { name: "研究助手消息" });
  expect(within(reply).getAllByRole("listitem")).toHaveLength(2);
  expect(within(reply).getByText("NaCl_derived.cif").tagName).toBe("STRONG");
  const question = screen.getByRole("article", { name: "你的消息" });
  expect(question.querySelector("p")?.textContent).toBe("保留 **原始文本**\nE**2 + v**2");
  expect(question.querySelector("strong")).toBeNull();
  expect(JSON.stringify(conversation)).toBe(before);
});

it.each([
  { label: "below the composer", summaryTop: 340, listBottom: 540, scrollTop: 180 },
  { label: "taller than the conversation", summaryTop: 340, listBottom: 1190, scrollTop: 280 },
  { label: "already visible", summaryTop: 120, listBottom: 290, scrollTop: 40 },
])("reveals a branch list $label inside the conversation while retaining focus", async ({ summaryTop, listBottom, scrollTop }) => {
  const { turn, owner } = setupTurnOnlyLink();
  const branch = { ...turn, turn_id: "turn-branch", parent_turn_id: turn.turn_id, sequence_no: 2,
    user_message: { id: "message-branch", role: "user", content: "使用一致参数比较三份材料" } };
  mocks.listAgent2ResearchTurns.mockResolvedValue([turn, branch]);
  mocks.getAgent2ExecutionProgress.mockResolvedValue({ turn_id: branch.turn_id, status: "ANSWERED", steps: [], warnings: [], incremental_outputs: [] });
  mocks.getResearchSession.mockResolvedValue({ ...owner, messages: [...owner.messages, { ...branch.user_message, session_id: owner.id, created_at: branch.created_at }] });
  render(<ResearchPage projectId="project_1" sessionId={owner.id} agent2TurnId={branch.turn_id} />);
  const summary = await screen.findByLabelText("查看全部 2 个分支");
  const disclosure = summary.closest("details")!;
  const scroller = disclosure.closest<HTMLElement>(".conversation-history")!;
  const list = disclosure.querySelector("ol")!;
  const rect = (top: number, bottom: number) => ({ top, bottom, height: bottom - top, left: 0, right: 300, width: 300, x: 0, y: top, toJSON: () => ({}) });
  Object.defineProperty(scroller, "clientHeight", { configurable: true, value: 300 });
  vi.spyOn(scroller, "getBoundingClientRect").mockReturnValue(rect(100, 400));
  vi.spyOn(summary, "getBoundingClientRect").mockReturnValue(rect(summaryTop, summaryTop + 44));
  vi.spyOn(list, "getBoundingClientRect").mockReturnValue(rect(summaryTop + 50, listBottom));
  scroller.scrollTop = 40;
  const pageScroll = document.documentElement.scrollTop;
  const user = userEvent.setup();
  await user.click(summary);
  summary.focus(); // Native summary click focus, omitted by user-event 14.
  await waitFor(() => expect(scroller.scrollTop).toBe(scrollTop));
  expect(disclosure).toHaveAttribute("open");
  expect(summary).toHaveFocus();
  expect(document.documentElement.scrollTop).toBe(pageScroll);
  await user.keyboard("{Escape}");
  expect(disclosure).not.toHaveAttribute("open");
  expect(summary).toHaveFocus();
});

it.each([undefined, "job-owned"])("recovers a Turn's owning conversation without a session URL (run=%s)", async (runId) => {
  const { turn } = setupTurnOnlyLink();
  const pendingKey = `mdi:research-pending-session:${JSON.stringify(["project_1", null, null, false, null, null, null, null])}`;
  sessionStorage.setItem(pendingKey, "unrelated");
  render(<ResearchPage projectId="project_1" runId={runId} agent2TurnId={turn.turn_id} />);

  expect(within(await screen.findByRole("article", { name: "当前分支的研究问题" })).getByText(turn.user_message.content)).toBeVisible();
  expect(screen.getByRole("heading", { name: "对话" })).toHaveAttribute("title", "三个材料的联合研究");
  expect(mocks.getResearchSession.mock.calls.every(([id]) => id === turn.research_session_id)).toBe(true);
  expect(sessionStorage.getItem(pendingKey)).toBe("unrelated");
  expect(mocks.getPlannerJob).not.toHaveBeenCalled();
  expect(mocks.createResearchSession).not.toHaveBeenCalled();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "本次上下文" }));
  await waitFor(() => expect(screen.getByLabelText("本次研究使用的上下文")).toHaveAttribute("open"));
  fireEvent.click(within(screen.getByRole("tabpanel", { name: "上下文" })).getByText("本次问题"));
  expect(within(screen.getByRole("tabpanel", { name: "上下文" })).getByText(turn.user_message.content)).toBeVisible();
  expect(mocks.listAgent2ResearchTurns.mock.calls.every(([, session]) => session === turn.research_session_id)).toBe(true);
});

it("recovers a Turn's conversation even when its session directory cannot be read", async () => {
  const { turn } = setupTurnOnlyLink();
  mocks.listResearchSessions.mockRejectedValue(new Error("directory unavailable"));
  render(<ResearchPage projectId="project_1" agent2TurnId={turn.turn_id} />);
  expect(within(await screen.findByRole("article", { name: "当前分支的研究问题" })).getByText(turn.user_message.content)).toBeVisible();
  expect(screen.getByRole("textbox", { name: "研究问题" })).toBeEnabled();
  expect(screen.queryByRole("button", { name: "重新加载对话" })).not.toBeInTheDocument();
});

it.each(["turn-id", "turn-project", "missing-owner", "session-id", "session-project"])("rejects mismatched Turn-only navigation (%s) without opening another conversation", async (corruption) => {
  const { turn, owner } = setupTurnOnlyLink();
  if (corruption === "turn-id") mocks.getAgent2ResearchTurn.mockResolvedValue({ ...turn, turn_id: "another-turn" });
  if (corruption === "turn-project") mocks.getAgent2ResearchTurn.mockResolvedValue({ ...turn, project_id: "another-project" });
  if (corruption === "missing-owner") mocks.getAgent2ResearchTurn.mockResolvedValue({ ...turn, research_session_id: "" });
  if (corruption === "session-id") mocks.getResearchSession.mockResolvedValue({ ...owner, id: "another-session" });
  if (corruption === "session-project") mocks.getResearchSession.mockResolvedValue({ ...owner, project_id: "another-project" });
  render(<ResearchPage projectId="project_1" agent2TurnId={turn.turn_id} />);
  expect(await screen.findByRole("button", { name: "重新加载对话" })).toBeEnabled();
  expect(screen.queryByRole("textbox", { name: "研究问题" })).not.toBeInTheDocument();
  expect(screen.queryByText(turn.user_message.content)).not.toBeInTheDocument();
  expect(mocks.getResearchSession.mock.calls.every(([id]) => id === turn.research_session_id)).toBe(true);
  expect(mocks.createResearchSession).not.toHaveBeenCalled();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
});

it("bounds a stalled Turn owner read and restores the preserved draft on retry", async () => {
  const { turn } = setupTurnOnlyLink();
  let ownerSignal: AbortSignal | undefined;
  mocks.getAgent2ResearchTurn.mockImplementationOnce((_id: string, options: { signal: AbortSignal }) => {
    ownerSignal = options.signal;
    return new Promise(() => {});
  });
  sessionStorage.setItem(researchComposerDraftKey("project_1", turn.research_session_id, turn.turn_id), "继续比较这三个材料");
  vi.useFakeTimers();
  const view = render(<ResearchPage projectId="project_1" agent2TurnId={turn.turn_id} />);
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  expect(mocks.getResearchSession).not.toHaveBeenCalled();
  expect(screen.queryByRole("textbox", { name: "研究问题" })).not.toBeInTheDocument();
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(ownerSignal?.aborted).toBe(true);
  fireEvent.click(screen.getByRole("button", { name: "重新加载对话" }));
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  expect(screen.getByRole("textbox", { name: "研究问题" })).toHaveValue("继续比较这三个材料");
  expect(mocks.getResearchSession.mock.calls.every(([id]) => id === turn.research_session_id)).toBe(true);
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  view.unmount();
});

it("ignores a late Turn owner after navigating to a different Turn-only link", async () => {
  const { turn, owner } = setupTurnOnlyLink();
  let finishOld!: (value: Agent2TurnDetail) => void;
  let oldSignal: AbortSignal | undefined;
  mocks.getAgent2ResearchTurn.mockImplementationOnce((_id: string, options: { signal: AbortSignal }) => {
    oldSignal = options.signal;
    return new Promise((resolve) => { finishOld = resolve; });
  });
  const view = render(<ResearchPage projectId="project_1" agent2TurnId={turn.turn_id} />);
  await waitFor(() => expect(oldSignal).toBeDefined());
  const next = { ...turn, turn_id: "turn-next", research_session_id: "session-next" };
  mocks.getAgent2ResearchTurn.mockResolvedValue(next);
  mocks.listAgent2ResearchTurns.mockResolvedValue([next]);
  mocks.getResearchSession.mockResolvedValue({ ...owner, id: "session-next", title: "新打开的研究", messages: [] });
  view.rerender(<ResearchPage projectId="project_1" agent2TurnId={next.turn_id} />);
  await waitFor(() => expect(screen.getByRole("heading", { name: "对话" })).toHaveAttribute("title", "新打开的研究"));
  await act(async () => { finishOld(turn); });
  expect(oldSignal?.aborted).toBe(true);
  expect(mocks.getResearchSession.mock.calls.every(([id]) => id === "session-next")).toBe(true);
  expect(screen.getByRole("heading", { name: "对话" })).toHaveAttribute("title", "新打开的研究");
});

function structureSourceHandoff() {
  const hash = "c".repeat(64);
  const token = encodeWorkspaceSelectionUrl(validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: hash,
    primary: { selectionSchemaVersion: "1.0", kind: "PERIODIC_SITE", sourceScopeHash: hash, projectId: "project_1", datasetId: "dataset_selected", datasetVersion: hash, objectId: "resource_structure", structureId: hash, siteId: "Li-0:1.0.0" },
    secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false }));
  const resource = { objectId: "resource_structure", objectType: "Structure", datasetId: "dataset_selected", objectHash: hash,
    payload: { lattice: { matrix: [[5,0,0],[0,5,0],[0,0,5]] }, sites: [{ species: [{ element: "Li" }], xyz: [0,0,0] }] } };
  const admitted = { object: { id: "object_structure", project_id: "project_1", object_type: "structure.crystal", display_name: "锂结构" },
    version: { id: "version_structure", scientific_object_id: "object_structure", semantic_hash: hash, source_resource_refs_json: [{ project_id: "project_1", dataset_id: "dataset_selected", resource_id: "resource_structure" }] } };
  return { token, resource, admitted };
}

it("carries a periodic atom into the exact admitted structure version and preserves its return link", async () => {
  const { token, resource, admitted } = structureSourceHandoff();
  mocks.getDatasetSourceResources.mockResolvedValue([resource]);
  mocks.admitDatasetResource.mockResolvedValue(admitted);
  mocks.createAgent2ResearchTurn.mockResolvedValue({ turn_id: "turn_structure" });
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" sourceSelectionToken={token} />);
  const link = await screen.findByRole("link", { name: "查看所选原子" });
  expect(new URL(link.getAttribute("href")!, "http://localhost").searchParams.get("selection")).toBe(token);
  expect(within(screen.getByRole("tabpanel", { name: "对话" })).getByText(/Li · 位点 0 · 周期位置/)).toBeInTheDocument();
  expect(mocks.admitDatasetResource).not.toHaveBeenCalled();
  const user = userEvent.setup();
  await user.type(screen.getByLabelText("研究问题"), "解释所选锂原子的局部环境");
  await user.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({ ui_context: expect.objectContaining({
    scientific_selections: [expect.objectContaining({ selection_type: "PERIODIC_SITE", object_ref: expect.objectContaining({ object_id: "object_structure", version_id: "version_structure" }), semantic_locator: { site_id: "Li-0:1.0.0", site_index: 0, species: "Li", image_offset_a: 1, image_offset_b: 0, image_offset_c: 0 } })],
  }) })));
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
});

it("blocks a malformed structure handoff without discarding an editable question", async () => {
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" sourceSelectionToken="invalid-site-token" />);
  expect(await screen.findByText("需要重新选择数据")).toBeInTheDocument();
  const user = userEvent.setup();
  await user.type(screen.getByLabelText("研究问题"), "保留我的问题");
  expect(screen.getByRole("button", { name: "发送" })).toBeDisabled();
  expect(screen.getByRole("link", { name: "返回来源数据重新选择" })).toHaveAttribute("href", "/projects/project_1/data?dataset=dataset_selected");
  expect(mocks.createResearchSession).not.toHaveBeenCalled();
});

it("keeps the selected structure as the visible subject when its dataset also contains a table", async () => {
  const { token, resource, admitted } = structureSourceHandoff();
  mocks.getDatasetSourceResources.mockResolvedValue([
    { objectId: "resource_table", objectType: "DataFrame", datasetId: "dataset_selected", payload: [] },
    resource,
  ]);
  mocks.promoteDatasetTable.mockResolvedValue({ object: { id: "object_table", project_id: "project_1", object_type: "materials.table", display_name: "同批上传的表格" }, version: { id: "version_table" } });
  mocks.admitDatasetResource.mockResolvedValue(admitted);
  mocks.createAgent2ResearchTurn.mockRejectedValue(new Error("研究服务暂时不可用"));
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" sourceSelectionToken={token} />);
  const user = userEvent.setup();
  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "解释这个锂原子的局部环境");
  await user.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({ ui_context: expect.objectContaining({
    active_object_refs: [expect.objectContaining({ object_id: "object_table", version_id: "version_table" }), expect.objectContaining({ object_id: "object_structure", version_id: "version_structure" })],
    selection_refs: [expect.objectContaining({ object_id: "object_structure", version_id: "version_structure" })],
    scientific_selections: [expect.objectContaining({ selection_type: "PERIODIC_SITE", object_ref: expect.objectContaining({ object_id: "object_structure", version_id: "version_structure" }) })],
  }) })));
  expect(await screen.findByText("锂结构", { selector: ".timeline-process-body small" })).toBeInTheDocument();
  expect(composer).toHaveValue("解释这个锂原子的局部环境");
  expect(screen.queryByText("同批上传的表格")).not.toBeInTheDocument();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
});

it.each(["source", "version"])("retains a question when the selected atom's %s cannot be verified", async (which) => {
  const { token, resource, admitted } = structureSourceHandoff();
  mocks.getDatasetSourceResources.mockResolvedValue([{ ...resource, objectHash: which === "source" ? "d".repeat(64) : resource.objectHash }]);
  mocks.admitDatasetResource.mockResolvedValue({ ...admitted, version: { ...admitted.version, semantic_hash: "d".repeat(64) } });
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" sourceSelectionToken={token} />);
  const user = userEvent.setup();
  const composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "分析所选原子");
  await user.click(screen.getByRole("button", { name: "发送" }));
  await screen.findByText(/问题已保留，尚未提交分析/);
  expect(composer).toHaveValue("分析所选原子");
  expect(screen.getByRole("link", { name: "查看所选原子" })).toBeInTheDocument();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  if (which === "source") expect(mocks.admitDatasetResource).not.toHaveBeenCalled();
});

it("does not admit a structure after a source read has timed out", async () => {
  const { token, resource } = structureSourceHandoff();
  let release: ((value: unknown[]) => void) | undefined;
  mocks.getDatasetSourceResources.mockImplementation(() => new Promise(resolve => { release = resolve; }));
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" sourceSelectionToken={token} />);
  const composer = await screen.findByLabelText("研究问题");
  await waitFor(() => expect(screen.getByRole("button", { name: "研究设置" })).toHaveTextContent("deepseek"));
  vi.useFakeTimers();
  fireEvent.change(composer, { target: { value: "检查原子环境" } });
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "发送" })); });
  expect(release).toBeTypeOf("function");
  await act(async () => { await vi.advanceTimersByTimeAsync(10_001); });
  expect(composer).toHaveValue("检查原子环境");
  expect(screen.getByRole("button", { name: "发送" })).not.toBeDisabled();
  await act(async () => { release?.([resource]); });
  expect(mocks.admitDatasetResource).not.toHaveBeenCalled();
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  vi.useRealTimers();
});

it("does not combine a dataset atom with a conflicting exact object route", async () => {
  const { token } = structureSourceHandoff();
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" sourceSelectionToken={token} viewerContext={{ objectId: "other", versionId: "other-version", objectType: "structure.crystal" }} />);
  expect(await screen.findByText("需要重新选择数据")).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("研究问题"), { target: { value: "不要替换原子来源" } });
  expect(screen.getByRole("button", { name: "发送" })).toBeDisabled();
  expect(mocks.createResearchSession).not.toHaveBeenCalled();
});

function electronicSourceHandoff(kind: "band" | "dos") {
  const hash = "c".repeat(64), resourceId = `resource_${kind}`;
  const token = encodeWorkspaceSelectionUrl(validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: hash,
    primary: { selectionSchemaVersion: "1.0", kind: kind === "band" ? "ELECTRONIC_BAND_STATE" : "ELECTRONIC_DOS_POINT", sourceScopeHash: hash, projectId: "project_1", datasetId: "dataset_selected", datasetVersion: hash,
      jobId: "source-view", artifactId: `source:${resourceId}`, artifactChecksum: hash, electronicResourceId: "calculation_resource", spinChannelId: "down",
      ...(kind === "band" ? { bandId: "b1", kpointId: "k1", bandStateId: `source-state:${resourceId}:b1:0` } : { dosChannelId: "total", energyPointId: `source-dos-point:${resourceId}:0` }) },
    secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false }));
  const resource = { objectId: resourceId, objectType: kind === "band" ? "ElectronicBand" : "ElectronicDos", datasetId: "dataset_selected", objectHash: hash,
    payload: { schemaVersion: kind === "band" ? "phase10n5.electronic_band_resource.v1" : "phase10n5.electronic_dos_resource.v1", resourceId: "calculation_resource", energyUnit: "eV", energyReference: "source_absolute",
      kpoints: [{ kpointId: "k1" }], bands: [{ bandId: "b1", spinChannel: "down", energiesEv: [0.25] }], energiesEv: [0.25], totalDos: [{ channelId: "total", spinChannel: "down", values: [1.5] }] } };
  const admitted = { object: { id: "object_electronic", project_id: "project_1", object_type: kind === "band" ? "electronic.band_structure" : "electronic.dos", display_name: "选中的电子数据" },
    version: { id: "version_electronic", scientific_object_id: "object_electronic", semantic_hash: hash, source_resource_refs_json: [{ project_id: "project_1", dataset_id: "dataset_selected", resource_id: resourceId }] } };
  return { token, resource, admitted };
}

it.each(["valid", "changed_source", "wrong_version"])("binds an uploaded volumetric field to its admitted version: %s", async variant => {
  const hash = "b".repeat(64), resourceId = "dataset_selected:volume";
  const token = encodeWorkspaceSelectionUrl(validateWorkspaceSelectionContext({schemaVersion:"1.0",sourceScopeHash:hash,primary:{
    selectionSchemaVersion:"1.0",kind:"VOLUMETRIC_FIELD",sourceScopeHash:hash,projectId:"project_1",datasetId:"dataset_selected",datasetVersion:hash,
    artifactId:`source:${resourceId}:volumetric-dataset`,artifactChecksum:hash,fieldId:"channel:1",
  },secondary:[],compatibility:"EXACT",propagation:"EXACT_COMPATIBLE_ONLY",cleared:false}));
  mocks.getDatasetSourceResources.mockResolvedValue([{objectId:resourceId,datasetId:"dataset_selected",objectType:"VolumetricData",objectHash:variant === "changed_source" ? "c".repeat(64) : hash,
    payload:{channels:[{name:"first",quantity:"generic_scalar",values:[1]},{name:"ELF",quantity:"elf",values:[0.7]}]}}]);
  mocks.admitDatasetResource.mockResolvedValue({object:{id:"volume",project_id:"project_1",object_type:"volumetric.field",display_name:"ELF"},version:{id:"exact-volume-version",scientific_object_id:"volume",semantic_hash:variant === "wrong_version" ? "c".repeat(64) : hash,source_resource_refs_json:[{project_id:"project_1",dataset_id:"dataset_selected",resource_id:resourceId}]}});
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" sourceSelectionToken={token}/>);
  const link = await screen.findByRole("link", {name:"查看所选体数据字段"});
  expect(new URL(link.getAttribute("href")!, "http://localhost").searchParams.get("selection")).toBe(token);
  const composer = screen.getByLabelText("研究问题");
  fireEvent.change(composer,{target:{value:"分析所选 ELF 字段"}});
  fireEvent.submit(composer.closest("form")!);
  if (variant === "valid") {
    await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1","session_1",expect.objectContaining({ui_context:expect.objectContaining({scientific_selections:[expect.objectContaining({
      object_ref:expect.objectContaining({object_id:"volume",version_id:"exact-volume-version"}),selection_type:"VOLUMETRIC_FIELD",semantic_locator:{field_id:"channel:1",source_channel_index:1,field_locator:"/channels/1"},
    })]})})));
  } else {
    await screen.findByText(/问题已保留，尚未提交分析/);
    expect(composer).toHaveValue("分析所选 ELF 字段");
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  }
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
});

it("recovers an interrupted admission after a rejected retry without duplicating the research", async () => {
  const api = await vi.importActual<typeof import("../lib/agent2-research-api")>("../lib/agent2-research-api");
  mocks.createAgent2ResearchTurn.mockImplementation(api.createAgent2ResearchTurn);
  mocks.createAgent2AdmissionKey.mockReturnValueOnce("first-send").mockReturnValue("retry-send");
  const fetchMock = vi.fn().mockRejectedValueOnce(new TypeError("Response lost after commit"))
    .mockResolvedValueOnce(new Response(null, { status: 429 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ turn_id: "original-turn" }), { status: 202 }));
  vi.stubGlobal("fetch", fetchMock);
  const props = { projectId: "project_1", sessionId: "session_1", viewerContext: {
    objectId: "object_structure", versionId: "version_structure_v2", objectType: "structure.crystal", displayName: "Si 精确结构",
  } };
  try {
    const first = render(<ResearchPage {...props} />);
    fireEvent.change(await screen.findByLabelText("研究问题"), { target: { value: "分析当前结构的配位环境" } });
    fireEvent.click(screen.getByRole("button", { name: "发送" }));
    expect(await screen.findByText(/当前请求暂受限制；无法确认本次提交状态/)).toBeInTheDocument();
    expect(screen.getByLabelText("研究问题")).toHaveValue("分析当前结构的配位环境");
    expect(screen.getByRole("button", { name: "发送" })).toBeEnabled();
    first.unmount();
    render(<ResearchPage {...props} />);
    await waitFor(() => expect(screen.getByLabelText("研究问题")).toHaveValue("分析当前结构的配位环境"));
    fireEvent.click(screen.getByRole("button", { name: "发送" }));
    await waitFor(() => expect(mocks.routerPush).toHaveBeenCalledWith("/projects/project_1/research/session_1?turn=original-turn"));
    expect(fetchMock.mock.calls.map(call => JSON.parse(call[1].body).admission_key)).toEqual(Array(3).fill("first-send"));
    expect(screen.getByLabelText("研究问题")).toHaveValue("");
    expect(mocks.createResearchAssistantProjection).not.toHaveBeenCalled();
    expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  } finally { vi.unstubAllGlobals(); }
});

it.each(["valid", "missing", "read_failure"])("rereads a %s volumetric channel before admitting Research", async variant => {
  const token = encodeWorkspaceSelectionUrl(validateWorkspaceSelectionContext({schemaVersion: "1.0", sourceScopeHash: "a".repeat(64), primary: {selectionSchemaVersion: "1.0", kind: "VOLUMETRIC_FIELD", sourceScopeHash: "a".repeat(64), projectId: "project_1", datasetId: "dataset_volume", datasetVersion: "version_volume", artifactId: "source:object_volume:volumetric-dataset", artifactChecksum: "a".repeat(64), fieldId: "channel:1"}, secondary: [], compatibility: "EXACT", propagation: "EXACT_COMPATIBLE_ONLY", cleared: false}));
  if (variant === "read_failure") mocks.getScientificViewerProjection.mockRejectedValue(new Error("offline"));
  else mocks.getScientificViewerProjection.mockResolvedValue({ project_id: "project_1", object_id: "object_volume", version_id: "version_volume", object_type: "volumetric.field", payload_status: "READY", payload: {channels: variant === "missing" ? [] : [{values: [1]}, {values: [2]}]}, content_hash: "a".repeat(64), source_resource_refs: [{dataset_id: "dataset_volume"}] });
  render(<ResearchPage projectId="project_1" viewerContext={{objectId: "object_volume", versionId: "version_volume", objectType: "volumetric.field", displayName: "体数据", selectionToken: token}} />);
  const composer = await screen.findByLabelText("研究问题");
  fireEvent.change(composer, {target: {value: "分析所选体数据字段"}});
  fireEvent.submit(composer.closest("form")!);
  if (variant === "valid") {
    await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({ ui_context: expect.objectContaining({scientific_selections: [expect.objectContaining({ selection_type: "VOLUMETRIC_FIELD", semantic_locator: {field_id: "channel:1", source_channel_index: 1, field_locator: "/channels/1"} })]})})));
  } else {
    await screen.findByText(variant === "missing" ? /所选体数据字段无法在此精确版本中确认/ : /暂时无法读取所选体数据的精确版本/);
    expect(composer).toHaveValue("分析所选体数据字段");
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  }
});

function trajectoryViewerContext() {
  return {objectId:"object_trajectory",versionId:"version_trajectory",objectType:"trajectory.atomic",displayName:"原子轨迹",selectionToken:encodeWorkspaceSelectionUrl(validateWorkspaceSelectionContext({
    schemaVersion:"1.0",sourceScopeHash:"a".repeat(64),primary:{selectionSchemaVersion:"1.0",kind:"TRAJECTORY_ATOM",sourceScopeHash:"a".repeat(64),projectId:"project_1",datasetId:"dataset_trajectory",datasetVersion:"version_trajectory",trajectoryId:trajectoryFixture.trajectory_id,artifactId:"source:object_trajectory",artifactChecksum:"a".repeat(64),frameId:"frame:5",atomId:"atom:1:0.0.0"},secondary:[],propagation:"EXACT_COMPATIBLE_ONLY",compatibility:"EXACT",cleared:false,
  }))};
}

it("binds a trajectory atom to the reread exact frame values before Research admission", async () => {
  mocks.getScientificViewerProjection.mockResolvedValue({project_id:"project_1",object_id:"object_trajectory",version_id:"version_trajectory",object_type:"trajectory.atomic",payload_status:"READY",payload:trajectoryFixture,content_hash:"a".repeat(64),source_resource_refs:[{dataset_id:"dataset_trajectory"}]});
  render(<ResearchPage projectId="project_1" viewerContext={trajectoryViewerContext()}/>);
  const composer=await screen.findByLabelText("研究问题");
  fireEvent.change(composer,{target:{value:"分析第六帧的这个原子"}});
  fireEvent.submit(composer.closest("form")!);
  await waitFor(()=>expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1","session_1",expect.objectContaining({ui_context:expect.objectContaining({scientific_selections:[expect.objectContaining({selection_type:"TRAJECTORY_ATOM",semantic_locator:expect.objectContaining({frame_index:5,atom_index:1,source_x:trajectoryFixture.frames[5].positions[1][0],image_offset_a:0})})]})})));
  expect(mocks.getScientificViewerProjection).toHaveBeenCalledWith("object_trajectory","version_trajectory",expect.any(AbortSignal));
});

it.each(["read_failure","foreign_version"])("retains the trajectory question and rejects admission on %s", async failure => {
  if(failure==="read_failure") mocks.getScientificViewerProjection.mockRejectedValue(new Error("offline"));
  else mocks.getScientificViewerProjection.mockResolvedValue({project_id:"project_1",object_id:"object_trajectory",version_id:"foreign"});
  render(<ResearchPage projectId="project_1" viewerContext={trajectoryViewerContext()}/>);
  const composer=await screen.findByLabelText("研究问题");
  fireEvent.change(composer,{target:{value:"保留轨迹问题"}});
  fireEvent.submit(composer.closest("form")!);
  await screen.findByText(failure==="read_failure"?/暂时无法读取所选轨迹的精确版本/:/所选轨迹位置无法在此精确版本中确认/);
  expect(composer).toHaveValue("保留轨迹问题");
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.createResearchMessage).not.toHaveBeenCalled();
});

it("ignores a late trajectory read after navigating to another selection", async () => {
  let finish!:(value:unknown)=>void;
  mocks.getScientificViewerProjection.mockReturnValue(new Promise(resolve=>{finish=resolve;}));
  const view=render(<ResearchPage projectId="project_1" viewerContext={trajectoryViewerContext()}/>);
  const composer=await screen.findByLabelText("研究问题");
  fireEvent.change(composer,{target:{value:"等待中的轨迹问题"}});
  fireEvent.submit(composer.closest("form")!);
  await waitFor(()=>expect(mocks.getScientificViewerProjection).toHaveBeenCalled());
  view.rerender(<ResearchPage projectId="project_1" viewerContext={{objectId:"other",versionId:"other_version",objectType:"trajectory.atomic"}}/>);
  await act(async()=>{finish({project_id:"project_1",object_id:"object_trajectory",version_id:"version_trajectory",object_type:"trajectory.atomic",payload_status:"READY",payload:trajectoryFixture,content_hash:"a".repeat(64),source_resource_refs:[{dataset_id:"dataset_trajectory"}]});});
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.routerPush).not.toHaveBeenCalled();
});

it.each(["band", "dos"] as const)("sends the selected %s value and retains all companion objects and the return link", async kind => {
  const { token, resource, admitted } = electronicSourceHandoff(kind);
  mocks.getDatasetSourceResources.mockResolvedValue([{ objectId: "table", objectType: "DataFrame", datasetId: "dataset_selected", payload: [] }, resource]);
  mocks.promoteDatasetTable.mockResolvedValue({ object: { id: "table", project_id: "project_1", object_type: "materials.table", display_name: "辅助表" }, version: { id: "table_version" } });
  mocks.admitDatasetResource.mockResolvedValue(admitted);
  mocks.createAgent2ResearchTurn.mockRejectedValue(new Error("研究服务暂时不可用"));
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" sourceSelectionToken={token} />);
  const link = await screen.findByRole("link", { name: "查看所选电子数据" });
  expect(new URL(link.getAttribute("href")!, "http://localhost").searchParams.get("selection")).toBe(token);
  expect(mocks.admitDatasetResource).not.toHaveBeenCalled();
  const user = userEvent.setup(), composer = screen.getByLabelText("研究问题");
  await user.type(composer, "解释选中的电子状态");
  await user.click(screen.getByRole("button", { name: "发送" }));
  await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith("project_1", "session_1", expect.objectContaining({ ui_context: expect.objectContaining({
    active_object_refs: [expect.objectContaining({ object_id: "table" }), expect.objectContaining({ object_id: "object_electronic", version_id: "version_electronic" })],
    selection_refs: [expect.objectContaining({ object_id: "object_electronic" })], scientific_selections: [expect.objectContaining({ selection_type: kind === "band" ? "ELECTRONIC_BAND_STATE" : "ELECTRONIC_DOS_POINT", semantic_locator: expect.objectContaining({ spin_channel_id: "down", energy_ev: 0.25 }) })],
  }) })));
  expect(composer).toHaveValue("解释选中的电子状态");
  expect(await screen.findByText("选中的电子数据", { selector: ".timeline-process-body small" })).toBeInTheDocument();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  expect(mocks.createResearchAssistantProjection).not.toHaveBeenCalled();
});

it.each(["source", "version"])("blocks a changed electronic %s while retaining the question", async which => {
  const { token, resource, admitted } = electronicSourceHandoff("dos");
  mocks.getDatasetSourceResources.mockResolvedValue([{ ...resource, objectHash: which === "source" ? "d".repeat(64) : resource.objectHash }]);
  mocks.admitDatasetResource.mockResolvedValue({ ...admitted, version: { ...admitted.version, semantic_hash: "d".repeat(64) } });
  render(<ResearchPage projectId="project_1" datasetId="dataset_selected" sourceSelectionToken={token} />);
  const user = userEvent.setup(), composer = await screen.findByLabelText("研究问题");
  await user.type(composer, "检查选中的态密度点");
  await user.click(screen.getByRole("button", { name: "发送" }));
  await screen.findByText(/问题已保留，尚未提交分析/);
  expect(composer).toHaveValue("检查选中的态密度点");
  expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  expect(mocks.createPlannerJob).not.toHaveBeenCalled();
  if (which === "source") expect(mocks.admitDatasetResource).not.toHaveBeenCalled();
  expect(mocks.createResearchAssistantProjection).not.toHaveBeenCalled();
});
