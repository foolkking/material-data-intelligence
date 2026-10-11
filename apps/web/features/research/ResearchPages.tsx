"use client";

import { getUserModels, type UserModel } from "../../app/lib/user-models-api";
import { ResearchSettings } from "./ResearchSettings";
import { acknowledgeResearchSessionCreation, hasPendingResearchSessionCreation } from "../../app/lib/research-session-creation";
import { ResearchMaterialPicker } from "./ResearchMaterialPicker";
import { useResearchMaterials } from "./use-research-materials";
import { admitResearchMaterial, materialKey, materialTypes, materialsContext, type ResearchMaterials } from "./research-materials";
import materialStyles from "./ResearchMaterials.module.css";
import conversationStyles from "./ResearchConversation.module.css";
import { ResearchContextContents } from "./ResearchContextContents";
import { ResearchReplyContent } from "./ResearchReplyContent";
import { useResearchAnswerStream } from "./use-research-answer-stream";
import { useConversationScroll } from "./use-conversation-scroll";

import { ProductLink as Link, useProductRouter } from "../../shared/layout/ProductNavigation";
import React, {
  useLayoutEffect,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type KeyboardEvent as ReactKeyboardEvent,
} from "react";
import {
  admitDatasetResource,
  archiveProjectRun,
  createPlannerJob,
  createPlannerJobInterpretation,
  getPlannerInterpretationEvidence,
  getPlannerJob,
  getPlannerJobArtifacts,
  getPlannerJobEvents,
  getPlannerJobInterpretations,
  getPlannerProviderStatus,
  listPlannerProviders,
  getDataset,
  getDatasetProfile,
  getDatasetSourceResources,
  getDatasetResearchSources,
  promoteDatasetTable,
  getProjectHistory,
  restoreProjectRun,
  type Artifact,
  type GroundedScientificInterpretation,
  type ScientificEvidenceItem,
  type InterpretationEvidenceResponse,
  type JobEvent,
  PlannerApiError,
  type PlannerJobCreateResult,
  type PlannerJobDetail,
  type ProjectHistory,
  type ProviderOption,
  type ProviderStatus,
} from "../../app/lib/planner-api";
import {
  bulkUpdateResearchSessions,
  createResearchAssistantProjection,
  createResearchMessage,
  createResearchSession,
  getResearchSession,
  listResearchSessions,
  updateResearchSession,
  type ResearchAssistantProjection,
  type ResearchMessage,
  type ResearchSession,
  type ResearchSessionBulkAction,
  type ScopeResolution,
} from "../../app/lib/product-api";
import { ProductShell, RequireProductAuth } from "../../shared/layout/ProductShell";
import { scientistProjectLabel } from "../../shared/product-labels";
import { ManagedObjectRow, ProductModal } from "../../shared/ui/ObjectManagement";
import { readSessionRequest, useSessionOperation, validateResearchSession, validateSessionDirectory } from "./session-management";
import { legacyJobIsTerminal, validateLegacyJob, watchLegacyJob } from "./legacy-job-polling";
import { LazyScientificResultViewer } from "../../scientific-viewers/LazyScientificViewers";
import {
  projectScientificArtifacts,
  scientificResultTitle,
  type ProjectedScientificArtifact,
} from "../../app/lib/scientific-result-projection";
import { formatScientificNarrativeNumbers } from "../../app/lib/scientific-presentation";
import { scientificNarrativeText } from "../../app/lib/scientific-narrative-text";
import { Agent2ScientificPresentation } from "./Agent2ScientificPresentation";
import {
  getReportComposition,
  listReportCompositions,
  type ReportEditorialProjection,
} from "../../app/lib/report-composition-api";
import { researchRunFailureMessage } from "../../app/lib/research-display";
import {
  type Agent2ProgressView,
} from "../../app/lib/agent2-execution-api";
import { ResearchExecutionActivity } from "./ResearchExecutionActivity";
import { ResearchTurnResultState } from "./ResearchTurnResultState";
import { ResearchSessionResult } from "./ResearchSessionResult";
import { LiteratureEvidencePanel } from "./LiteratureEvidencePanel";
import { readBranchResult, readBranchTurn, validateBranchTurn } from "./branch-source";
import { useEditResearchSource } from "./use-edit-research-source";
import { useResearchContextNavigation } from "./use-research-context-navigation";
import { useSessionMemory } from "./use-session-memory";
import { SessionMemoryNotice } from "./SessionMemoryNotice";
import { ScientificReportAction } from "../reports/ScientificReportAction";
import {
  Agent2AdmissionUnconfirmedError,
  Agent2ReadError,
  createAgent2AdmissionKey,
  getAgent2ResearchTurn,
  createAgent2ResearchTurn as admitResearchTurn,
  type Agent2ScientificObjectRef,
  type Agent2ScientificSelection,
  type Agent2ContextManifest,
  type Agent2ContextManifestItem,
  type Agent2ContextManifestRecord,
  type Agent2ResearchTurnResult,
  type Agent2TurnDetail,
  type Agent2TurnResponse,
} from "../../app/lib/agent2-research-api";
import { bindDatasetSourceSelection, datasetSourceSelection, selectedDatasetSourceResource, DatasetSourceSelectionError, type DatasetSourceSelection } from "./dataset-source-selection";
import { decodeWorkspaceSelectionUrl } from "../../shared/workspace/workspace-selection-contract";
import {
  apiSemanticLocator,
  scientificSelectionFromWorkspace,
  selectionToResearchObjectRef,
} from "../../scientific-viewers/scientific-viewer/scientificSelection";
import { resolveScientificViewer } from "../../scientific-viewers/scientific-viewer/scientificViewerRegistry";
import { getScientificViewerProjection } from "../../app/lib/scientific-viewer-api";
import { volumetricVersionLocator } from "../../scientific-viewers/volumetric-viewer/volumetric-selection";
import { trajectoryVersionLocator } from "../../scientific-viewers/trajectory-viewer/trajectory-selection";
import { watchAgent2Execution, type ExecutionCancelState, type ExecutionReadState } from "./execution-recovery";
import { canCancelResearchTurn, canReadSavedAgent2Result, hasAgent2ResultPresentation, isResearchCancellationPending } from "../../app/lib/research-status";
import { resultFollowUpInput, type ResultResearchAction } from "./result-follow-up";
import {
  beginResearchPerformanceAttempt,
  bindResearchPerformanceTurn,
  recordResearchFirstTruthfulProgress,
  scheduleResearchSubmitAcknowledgement,
  type ResearchPerformanceSample,
} from "../../app/lib/research-performance";
import { projectRoleAllows } from "../../app/lib/project-permissions";

type ResearchState =
  | "idle"
  | "planning"
  | "running"
  | "complete"
  | "partial"
  | "failed"
  | "canceled"
  | "unsupported"
  | "clarification"
  | "capability-clarification";

export type ResearchTechnicalSummary = {
  runId: string | null;
  planId: string | null;
  outputCount: number;
  structuredOutputCount: number;
  structuredOutputLabel: string;
};

export function researchComposerDraftKey(
  projectId: string,
  sessionId: string | undefined,
  turnId: string | undefined,
): string {
  return [
    "mdi",
    "research-draft",
    encodeURIComponent(projectId),
    encodeURIComponent(sessionId || "new"),
    encodeURIComponent(turnId || "composer"),
  ].join(":");
}

type ResearchStarterPrompt = {
  id: string;
  question: string;
};

const contextOperationLabel = (operation: string) =>
  ({
    ORCHESTRATOR: "理解问题",
    PLANNER: "规划分析",
    INTERPRETER: "解释结果",
    DATA: "查询数据",
    REPORT: "整理报告",
  })[operation] || "研究";

export function contextOperationSequenceLabel(
  records: Agent2ContextManifestRecord[],
  index: number,
): string {
  const current = records[index];
  if (!current) return "研究";
  const label = contextOperationLabel(current.operation);
  const matching = records.filter(
    (entry) => entry.operation === current.operation,
  );
  if (matching.length <= 1) return label;
  const occurrence = records
    .slice(0, index + 1)
    .filter((entry) => entry.operation === current.operation).length;
  return `${label} · ${occurrence}/${matching.length}`;
}

const contextKindLabel = (kind: string) =>
  ({
    SCIENTIFIC_OBJECT: "科学数据",
    SCIENTIFIC_SELECTION: "当前选择",
    SCIENTIFIC_RESULT: "既有结果",
    USER_CONSTRAINT: "用户约束",
    RESEARCH_GOAL: "研究目标",
    CAPABILITY_CANDIDATE: "分析能力",
    SCIENTIFIC_EVIDENCE: "科学证据",
    LITERATURE_EVIDENCE: "文献证据",
  })[kind] || "上下文";

const contextSelectionLabel = (selectionMode: string) =>
  ({
    EXPLICIT: "明确指定",
    UI_SELECTION: "从界面选择",
    CURRENT: "当前来源",
    PINNED: "已固定",
    RECENT: "近期相关",
    CONTINUATION: "延续研究",
    RETRIEVED: "检索纳入",
  })[selectionMode] || "系统选择";

const contextAuthorityLabel = (authorityClass: string) =>
  ({
    SCIENTIFIC_DATA: "科学数据权威",
    SCIENTIFIC_RESULT: "科学结果权威",
    USER_CONSTRAINT: "用户约束",
    CONVERSATIONAL_NARRATIVE: "对话背景",
    SCIENTIFIC_EVIDENCE: "证据权威",
    SYSTEM_RUNTIME_STATE: "系统运行状态",
    DERIVED_SUMMARY: "派生摘要",
  })[authorityClass] || "上下文信息";

const contextRoleLabel = (role?: string) =>
  ({
    EVIDENCE: "科学依据",
    CONTINUITY: "研究连续性",
    SUBJECT: "研究对象",
    CONSTRAINT: "科学约束",
    PREFERENCE: "呈现偏好",
  })[role || ""] || "研究上下文";

function contextItemSupportEligible(item: Agent2ContextManifestItem): boolean {
  if (item.support_eligible === true) return true;
  if (item.support_eligible === false) return false;
  return (
    (item.kind === "SCIENTIFIC_RESULT" &&
      item.authority_class === "SCIENTIFIC_RESULT") ||
    (["SCIENTIFIC_EVIDENCE", "LITERATURE_EVIDENCE"].includes(item.kind) &&
      item.authority_class === "SCIENTIFIC_EVIDENCE")
  );
}

const contextFreshnessLabel = (freshness?: string) =>
  ({
    CURRENT: "当前",
    HISTORICAL_VALID: "历史有效",
    STALE: "已过期",
    INVALIDATED: "已失效",
    SOURCE_MISSING: "来源不可用",
    UNKNOWN: "状态未知",
  })[freshness || "UNKNOWN"] || freshness || "状态未知";

const contextInclusionReasonLabel = (reason: string) =>
  ({
    "active scientific scope": "当前科学范围",
    "persisted active scientific scope": "已保存的当前科学范围",
    "explicit UI selection": "界面明确选择",
    "explicit UI scientific selection": "界面明确选择的科学数据",
    "persisted UI scientific selection": "已保存的界面科学选择",
    "semantic UI selection": "界面语义选择",
    "persisted semantic UI selection": "已保存的界面语义选择",
    "explicit referenced prior Result": "明确引用的既有科学结果",
    "persisted referenced Result": "已保存的引用科学结果",
    "session/user constraint": "会话或用户约束",
    "persisted user constraint": "已保存的用户约束",
    "active research goal": "当前研究目标",
    "persisted research goal": "已保存的研究目标",
    "exact source binding for capability planning": "用于能力规划的精确来源",
    "eligible registered capability candidate": "符合条件的已注册分析能力",
    "authorized exact-result reuse candidate": "已授权的精确结果复用候选",
    "explicit scientific constraint": "明确的科学约束",
    "exact source bound to ScientificResult": "科学结果绑定的精确来源",
    "authoritative result facts for grounded interpretation":
      "用于有据解释的权威结果事实",
    "bounded evidence references supporting Result facts":
      "支持结果事实的有界证据",
    "current interpretation question": "当前解释问题",
    "exact source bound to Report result": "报告结果绑定的精确来源",
    "authoritative Result projection for report composition":
      "用于报告编排的权威结果投影",
    "validated grounded interpretation used for communication":
      "用于科学沟通的已验证解释",
    "bounded evidence references for report provenance":
      "用于报告溯源的有界证据",
    "operation input": "本次操作输入",
  })[reason] || reason;

const RESEARCH_STARTER_CATALOG: Array<
  ResearchStarterPrompt & { signals: string[] }
> = [
  {
    id: "experimental-xrd",
    question: "比较实验与理论 XRD",
    signals: [
      "structure_experimental_xrd_comparison",
      "experimental_xrd_comparison",
    ],
  },
  {
    id: "trajectory",
    question: "查看 AIMD 轨迹并概览结构演化",
    signals: ["trajectory_visualization", "trajectory_rdf", "trajectory"],
  },
  {
    id: "phonon",
    question: "查看声子能带与态密度",
    signals: ["phonon_visualization", "phonon"],
  },
  {
    id: "electronic",
    question: "查看电子能带与态密度",
    signals: [
      "electronic_band_structure",
      "electronic_dos",
      "electronicband",
      "electronicdos",
      "electronic",
    ],
  },
  {
    id: "volumetric",
    question: "查看体数据的等值面与切片",
    signals: [
      "volumetric_visualization",
      "structure_volumetric_data",
      "volumetric",
      "charge_density",
      "elf",
    ],
  },
  {
    id: "local-environment",
    question: "分析局部配位环境",
    signals: [
      "structure_local_environment_polyhedra",
      "local_environment_polyhedra",
    ],
  },
  {
    id: "structure",
    question: "概览结构组成与晶格",
    signals: [
      "structure_summary",
      "dataset_structure_statistics",
      "crystal_structure",
    ],
  },
  {
    id: "regression",
    question: "评估材料属性回归结果",
    signals: [
      "regression_evaluation",
      "regression_target",
      "regression_prediction",
    ],
  },
  {
    id: "uncertainty",
    question: "评估预测不确定性",
    signals: ["uncertainty_evaluation", "regression_uncertainty"],
  },
  {
    id: "classification",
    question: "评估材料分类结果",
    signals: [
      "classification_evaluation",
      "classification_target",
      "classification_prediction",
    ],
  },
  {
    id: "composition",
    question: "查看材料组成分布",
    signals: ["composition_space", "composition_summary", "material_formula"],
  },
];

function normalizeResearchSignal(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

/** Resolve sibling research branches from the persisted Turn relation. */
function researchBranchRootId(turns: Agent2TurnResponse[], current: Agent2TurnResponse, requestedRootId?: string) {
  // The URL preserves the group being browsed; it cannot invent a relationship.
  return requestedRootId && turns.some((turn) => turn.turn_id === requestedRootId) &&
    (current.turn_id === requestedRootId || current.parent_turn_id === requestedRootId)
    ? requestedRootId : current.parent_turn_id || current.turn_id;
}

export function researchBranchChoices(
  turns: Agent2TurnResponse[],
  currentTurnId?: string,
  requestedRootId?: string,
): Agent2TurnResponse[] {
  if (!currentTurnId) return [];
  const current = turns.find(
    (turn) => turn.id === currentTurnId || turn.turn_id === currentTurnId,
  );
  if (!current) return [];
  const rootId = researchBranchRootId(turns, current, requestedRootId);
  const root = turns.find(
    (turn) => turn.id === rootId || turn.turn_id === rootId,
  );
  const choices = turns.filter(
    (turn) => (turn.parent_turn_id || turn.turn_id) === rootId,
  );
  if (
    root &&
    !choices.some(
      (turn) => (turn.id || turn.turn_id) === (root.id || root.turn_id),
    )
  )
    choices.unshift(root);
  if (choices.length <= 1) return [];
  return [...choices].sort(
    (left, right) => left.sequence_no - right.sequence_no,
  );
}

export function researchBranchNavigation(
  turns: Agent2TurnResponse[],
  currentTurnId?: string,
  requestedRootId?: string,
): {
  rootId: string;
  choices: Agent2TurnResponse[];
  current: Agent2TurnResponse;
  currentIndex: number;
  previous: Agent2TurnResponse | null;
  next: Agent2TurnResponse | null;
} | null {
  const choices = researchBranchChoices(turns, currentTurnId, requestedRootId);
  if (!choices.length || !currentTurnId) return null;
  const currentIndex = choices.findIndex(
    (turn) => (turn.id || turn.turn_id) === currentTurnId,
  );
  if (currentIndex < 0) return null;
  return {
    rootId: researchBranchRootId(turns, choices[currentIndex], requestedRootId),
    choices,
    current: choices[currentIndex],
    currentIndex,
    previous: choices[currentIndex - 1] || null,
    next: choices[currentIndex + 1] || null,
  };
}

export function researchBranchDescriptor(
  turns: Agent2TurnResponse[],
  turn: Agent2TurnResponse,
): {
  turnId: string;
  messageRevisionId: string;
  title: string;
  sourceTurnId: string | null;
  sourceTitle: string | null;
} {
  const turnId = turn.id || turn.turn_id;
  const sourceTurnId = turn.parent_turn_id || null;
  const source = sourceTurnId
    ? turns.find((item) => (item.id || item.turn_id) === sourceTurnId)
    : null;
  return {
    turnId,
    messageRevisionId: turn.user_message.id,
    title: turn.user_message.content.trim() || "未命名研究问题",
    sourceTurnId,
    sourceTitle: source?.user_message.content.trim() || null,
  };
}

/** Resolve a retry notice only from the persisted Turn relationship.
 *
 * The route hint explains why the new branch was opened, but it is not
 * authoritative on its own.  A hand-crafted `retryOf` value must match the
 * current Turn's server-returned parent and that parent must be a preserved
 * failed/canceled Turn in the same session response.
 */
export function retryLineageForTurn(
  turns: Agent2TurnResponse[],
  currentTurnId?: string,
  retryOfTurnId?: string,
): {
  current: Agent2TurnResponse;
  source: Agent2TurnResponse;
} | null {
  if (!currentTurnId || !retryOfTurnId || currentTurnId === retryOfTurnId)
    return null;
  const current = turns.find(
    (turn) => (turn.id || turn.turn_id) === currentTurnId,
  );
  if (!current || current.parent_turn_id !== retryOfTurnId) return null;
  const source = turns.find(
    (turn) => (turn.id || turn.turn_id) === retryOfTurnId,
  );
  if (!source || !["FAILED", "CANCELED"].includes(source.status)) return null;
  return { current, source };
}

export function agent2ProgressForTurn(
  progress: Agent2ProgressView | null,
  turnId?: string,
): Agent2ProgressView | null {
  return progress?.turn_id === turnId ? progress : null;
}

/**
 * Resolve a persisted ResearchTurn only inside the exact project/session
 * scope used by the route. This is the reload/reconnect boundary: the
 * frontend may reconstruct display state from this record, but it must not
 * infer identity from a Job name or from a stale in-memory object.
 */
export function resolveAgent2TurnForRecovery(
  turns: Agent2TurnResponse[],
  projectId: string,
  sessionId: string,
  turnId: string,
): Agent2TurnResponse | null {
  const turn = turns.find(
    (item) => (item.id || item.turn_id) === turnId,
  );
  if (
    !turn ||
    turn.project_id !== projectId ||
    turn.research_session_id !== sessionId
  ) {
    return null;
  }
  return turn;
}

export function agent2ContextManifestForTurn(
  manifest: Agent2ContextManifest | null,
  turnId?: string,
): Agent2ContextManifest | null {
  return manifest?.research_turn_id === turnId ? manifest : null;
}

const EMPTY_RESEARCH_TURNS: Agent2TurnResponse[] = [];
export const CONTEXT_MANIFEST_RENDER_WINDOW = 32;

export function defaultResearchConversationWidth(
  hasScientificWorkbenchContent: boolean,
  workbenchWidth = 0,
): number {
  return hasScientificWorkbenchContent
    ? Math.round(Math.min(640, Math.max(420, workbenchWidth * 0.4)))
    : 720;
}

export function researchWorkbenchContentAvailable(input: {
  job: PlannerJobCreateResult | null;
  artifacts: readonly Artifact[];
  interpretation: GroundedScientificInterpretation | null;
  evidence: InterpretationEvidenceResponse | null;
  events: readonly JobEvent[];
  agent2Progress: Agent2ProgressView | null;
}): boolean {
  // Conversation and planning status already live beside the messages. The
  // second pane opens automatically when there is scientific content to read.
  return Boolean(
    input.artifacts.length ||
      input.interpretation ||
      input.evidence?.evidenceItems?.length ||
      input.events.length ||
      input.job?.plan ||
      hasAgent2ResultPresentation(input.agent2Progress) ||
      (input.agent2Progress && canReadSavedAgent2Result(input.agent2Progress)),
  );
}

/** Keep the disclosure bounded by default while allowing a researcher to inspect
 * every included item when the manifest is larger than the compact preview. */
export function contextManifestVisibleItems(
  manifest: Agent2ContextManifest | null,
  expanded: boolean,
): Agent2ContextManifestItem[] {
  if (!manifest) return [];
  return expanded ? manifest.included_items : manifest.included_items.slice(0, 8);
}

export function contextManifestRenderItems(
  manifest: Agent2ContextManifest | null,
  expanded: boolean,
  windowStart = 0,
): Agent2ContextManifestItem[] {
  const items = contextManifestVisibleItems(manifest, expanded);
  return expanded
    ? items.slice(windowStart, windowStart + CONTEXT_MANIFEST_RENDER_WINDOW)
    : items.slice(0, 8);
}

export function agent2ProgressNeedsRefresh(status: string): boolean {
  return [
    "RECEIVED",
    "RESOLVING_CONTEXT",
    "ORCHESTRATING",
    "READY_TO_PLAN",
    "PLANNING",
    "PLAN_READY",
    "QUEUED",
    "RUNNING",
    "CANCELING",
    "RESULT_PENDING",
    "RESULT_READY",
    "INTERPRETING",
  ].includes(status);
}

export function agent2ProgressHasFreshSessionMessages(status: string): boolean {
  return [
    "ANSWERED",
    "NEEDS_CLARIFICATION",
    "UNSUPPORTED",
    "PLAN_REJECTED",
    "COMPLETED",
    "PARTIAL",
    "FAILED",
    "CANCELED",
  ].includes(status);
}

/** A stale dispatch conflict must not mask a durable terminal outcome. */
export function shouldSuppressAgent2DispatchError(status: string): boolean {
  return ["CANCELED", "COMPLETED", "PARTIAL", "FAILED"].includes(status);
}

export function requestWasAborted(reason: unknown): boolean {
  return reason instanceof Error && reason.name === "AbortError";
}

export function editBranchSubmissionAllowed(
  editTurnId: string | undefined,
  loadState: "idle" | "loading" | "ready" | "error",
  editingTurn: Agent2TurnDetail | null,
): boolean {
  return !editTurnId || (loadState === "ready" && Boolean(editingTurn));
}

export function researchStateForAgent2Progress(
  status: string,
): ResearchState | null {
  if (["RECEIVED", "RESOLVING_CONTEXT", "ORCHESTRATING", "READY_TO_PLAN", "PLANNING", "PLAN_READY"].includes(status)) {
    return "planning";
  }
  if (["QUEUED", "RUNNING", "CANCELING", "RESULT_PENDING", "RESULT_READY", "INTERPRETING"].includes(status)) {
    return "running";
  }
  if (status === "COMPLETED") return "complete";
  if (status === "PARTIAL") return "partial";
  if (["FAILED", "PLAN_REJECTED"].includes(status)) return "failed";
  if (status === "UNSUPPORTED") return "unsupported";
  if (status === "NEEDS_CLARIFICATION") return "clarification";
  // ANSWERED and CANCELED are terminal states with no active scientific
  // execution. The persisted progress panel still communicates their exact
  // outcome while the composer becomes usable again.
  if (["ANSWERED", "CANCELED"].includes(status)) return "idle";
  return null;
}

export function agent2RetryInput(turn: Agent2TurnDetail) {
  const message = turn.user_message.content.trim();
  if (!message) {
    throw new Error("原研究问题暂时无法读取，无法安全重试。");
  }
  const context = turn.context;
  return {
    message,
    reply_to_turn_id: turn.turn_id,
    ui_context: {
      active_object_refs: context?.scope || [],
      selection_refs: context?.selection || [],
      scientific_selections: context?.scientific_selection || [],
      explicit_object_refs: context?.scope || [],
      explicit_result_ids: [],
      explicit_finding_refs: [] as string[],
    },
  };
}

export function agent2ContinueInput(
  turn: Agent2TurnDetail,
  message: string,
  resultSnapshotId?: string | null,
) {
  const normalizedMessage = message.trim();
  if (!normalizedMessage) {
    throw new Error("继续研究的问题不能为空。");
  }
  const exactTurnInput = agent2RetryInput(turn);
  return {
    ...exactTurnInput,
    message: normalizedMessage,
    ui_context: {
      ...exactTurnInput.ui_context,
      // A child Turn suppresses recency-derived Result candidates. Bind an
      // explicitly reusable snapshot when one is available so Continue can
      // remain a zero-recompute follow-up instead of accidentally planning a
      // fresh scientific run.
      explicit_result_ids: resultSnapshotId ? [resultSnapshotId] : [],
    },
  };
}

export function researchMessageWindow(
  messages: ResearchMessage[],
  selectedMessageId?: string | null,
  expanded = false,
  recentLimit = 10,
  expandedWindowStart = 0,
  branchMessageIds?: readonly string[],
) {
  if (expanded) {
    if (messages.length <= 100) {
      return {
        visible: messages,
        hiddenBefore: 0,
        hiddenAfter: 0,
      };
    }
    return {
      visible: messages.slice(expandedWindowStart, expandedWindowStart + 100),
      hiddenBefore: expandedWindowStart,
      hiddenAfter: Math.max(0, messages.length - expandedWindowStart - 100),
    };
  }
  const selectedIndex = selectedMessageId
    ? messages.findIndex((message) => message.id === selectedMessageId)
    : -1;
  if (branchMessageIds) {
    // Completion order is not branch ownership. A late answer may follow a
    // different question; only the Turn's referenced message IDs are authority.
    const owned = new Set(branchMessageIds);
    const visible = messages.filter((message) => owned.has(message.id));
    const hiddenBefore = Math.max(0, selectedIndex);
    return { visible, hiddenBefore, hiddenAfter: Math.max(0, messages.length - hiddenBefore - visible.length) };
  }
  if (selectedIndex >= 0) {
    // A selected ResearchTurn is an exact conversational branch, not merely a
    // scroll anchor inside the whole session transcript. Show its authoritative
    // user message and the following assistant projections up to the next user
    // message. Older/sibling branch questions stay available through branch
    // navigation or the explicit complete-conversation control instead of
    // appearing as duplicate submissions beside the current branch.
    let end = selectedIndex + 1;
    while (end < messages.length && messages[end].role !== "user") end += 1;
    return {
      visible: messages.slice(selectedIndex, end),
      hiddenBefore: selectedIndex,
      hiddenAfter: messages.length - end,
    };
  }
  if (messages.length <= recentLimit) {
    return {
      visible: messages,
      hiddenBefore: 0,
      hiddenAfter: 0,
    };
  }
  const start =
    Math.max(0, messages.length - recentLimit);
  const end = messages.length;
  return {
    visible: messages.slice(start, end),
    hiddenBefore: start,
    hiddenAfter: messages.length - end,
  };
}

export function researchMessageVisibleInTimeline(
  message: ResearchMessage,
): boolean {
  // Execution progress already has a structured, cancellable presentation.
  // A planning acknowledgement is not another answer to the user's question.
  return message.role !== "assistant" || !["ASSISTANT_PRE_RUN", "DOWNSTREAM_ACKNOWLEDGEMENT"]
    .includes(String(message.payload?.messageKind));
}

/**
 * Collapse repeated projections of the same durable message only. Identical
 * text with a different ID can be a retry or a distinct research branch.
 */
export function dedupeResearchTimelineMessages(
  messages: ResearchMessage[],
): ResearchMessage[] {
  const result: ResearchMessage[] = [];
  const seen = new Set<string>();
  for (const message of messages) {
    if (seen.has(message.id)) continue;
    seen.add(message.id);
    result.push(message);
  }
  return result;
}

/** Build inert starter questions only from the already-authorized Project History projection. */
export function researchStarterPrompts(
  history: ProjectHistory | null,
): ResearchStarterPrompt[] {
  if (!history?.datasets.length) return [];
  const signals = new Set<string>();
  const semanticRoles = new Set<string>();
  for (const dataset of history.datasets) {
    const profile = dataset.profile;
    for (const value of Object.keys(profile?.semanticRoles || {})) {
      const normalized = normalizeResearchSignal(value);
      if (normalized) semanticRoles.add(normalized);
    }
    for (const value of [
      profile?.datasetType,
      ...(profile?.readyCapabilities || []),
      ...semanticRoles,
    ]) {
      if (value) signals.add(normalizeResearchSignal(String(value)));
    }
  }
  const hasSignal = (candidate: string) => signals.has(candidate);
  const prompts: ResearchStarterPrompt[] = [];
  for (const candidate of RESEARCH_STARTER_CATALOG) {
    if (
      candidate.signals.some(hasSignal) &&
      !prompts.some((prompt) => prompt.question === candidate.question)
    ) {
      prompts.push({ id: candidate.id, question: candidate.question });
    }
    if (prompts.length === 3) break;
  }
  if (
    prompts.length < 3 &&
    semanticRoles.has("formation_energy") &&
    semanticRoles.has("band_gap")
  ) {
    prompts.push({
      id: "formation-energy-band-gap",
      question: "比较 formation energy 与 band gap 的关系",
    });
  }
  return prompts.length
    ? prompts.slice(0, 3)
    : [{ id: "project-overview", question: "概览当前项目数据与可用分析" }];
}

/** Expose audit metadata without loading or rendering secret-bearing payloads. */
export function researchTechnicalSummary(
  job: PlannerJobCreateResult | null,
  artifacts: Artifact[],
  resultArtifacts: ProjectedScientificArtifact[] = projectScientificArtifacts(
    artifacts,
  ),
): ResearchTechnicalSummary {
  const structuredOutputs = artifacts.filter((artifact) => {
    const type = String(artifact.type || "").toLowerCase();
    const contentType = String(artifact.contentType || "").toLowerCase();
    return (
      contentType.includes("json") || type.endsWith("_json") || type === "json"
    );
  });
  const names = structuredOutputs
    .map((artifact) => String(artifact.name || "").trim())
    .filter(Boolean)
    .slice(0, 3);
  return {
    runId: job?.job_id || null,
    planId: job?.plan_id || null,
    outputCount: resultArtifacts.length,
    structuredOutputCount: structuredOutputs.length,
    structuredOutputLabel: names.length ? names.join("、") : "暂无 JSON 输出",
  };
}

function compactTechnicalId(value: string | null): string {
  if (!value) return "未提供";
  return value.length > 24 ? `${value.slice(0, 12)}…${value.slice(-8)}` : value;
}

function researchRunState(status: string | null | undefined): ResearchState {
  const normalized = String(status || "").toLowerCase();
  if (
    ["completed", "complete", "ready", "succeeded", "success"].includes(
      normalized,
    )
  )
    return "complete";
  if (normalized === "answered") return "idle";
  if (["partial_success", "partial", "degraded"].includes(normalized))
    return "partial";
  if (["cancelled", "canceled"].includes(normalized)) return "canceled";
  if (["failed", "error"].includes(normalized)) return "failed";
  if (["queued", "created", "planning", "pending"].includes(normalized))
    return "planning";
  if (["running", "active", "started", "cancel_requested"].includes(normalized)) return "running";
  return "failed";
}

function researchSessionReferencesRun(
  session: ResearchSession,
  runId: string,
  phase?: string,
): boolean {
  if (!phase && (session.runIds || []).includes(runId)) return true;
  return (session.messages || []).some((message) => {
    const payload = message.payload || {};
    return payload.runId === runId && (!phase || payload.phase === phase);
  });
}

function researchRunHref(
  projectId: string,
  runId: string,
  sessions: ResearchSession[],
  researchSessionId?: string,
  researchTurnId?: string | null,
): string {
  const owner = researchSessionId
    ? sessions.find((item) => item.id === researchSessionId) ||
      ({ id: researchSessionId } as ResearchSession)
    : sessions.find((item) => researchSessionReferencesRun(item, runId));
  const query = new URLSearchParams({ run: runId });
  // A ResearchTurn ID is only accepted from the persisted history relation.
  // Legacy jobs without that relation remain viewable through their run route;
  // the frontend must never infer scientific identity from a Job name.
  if (researchTurnId) query.set("turn", researchTurnId);
  return owner
    ? `/projects/${projectId}/research/${owner.id}?${query.toString()}`
    : `/projects/${projectId}/research?${query.toString()}`;
}

/** Resolve session-history navigation from the persisted run relation. */
function researchSessionHref(
  projectId: string,
  sessionId: string,
  history: ProjectHistory | null,
): string {
  const related = (history?.analyses || [])
    .filter((run) => run.researchSessionId === sessionId)
    .sort((left, right) =>
      String(right.updatedAt || right.createdAt || "").localeCompare(
        String(left.updatedAt || left.createdAt || ""),
      ),
    )[0];
  return related
    ? researchRunHref(
        projectId,
        related.jobId,
        [],
        sessionId,
        related.researchTurnId,
      )
    : `/projects/${projectId}/research/${encodeURIComponent(sessionId)}`;
}

type ViewerResearchContext = {
  objectId?: string;
  versionId?: string;
  objectType?: string;
  displayName?: string;
  selectionToken?: string;
  selectionLabel?: string;
};

function freshResearchHref(
  projectId: string,
  datasetId?: string,
  sampleRef?: string,
  viewerContext?: ViewerResearchContext,
  sourceSelectionToken?: string,
): string {
  const query = new URLSearchParams({ new: "1" });
  if (datasetId) query.set("dataset", datasetId);
  if (sampleRef) query.set("sample", sampleRef);
  if (sourceSelectionToken) query.set("sourceSelection", sourceSelectionToken);
  if (viewerContext?.objectId) query.set("object", viewerContext.objectId);
  if (viewerContext?.versionId) query.set("version", viewerContext.versionId);
  if (viewerContext?.objectType) query.set("type", viewerContext.objectType);
  if (viewerContext?.displayName) query.set("name", viewerContext.displayName);
  if (viewerContext?.selectionToken)
    query.set("selection", viewerContext.selectionToken);
  if (viewerContext?.selectionLabel)
    query.set("selectionLabel", viewerContext.selectionLabel);
  return `/projects/${encodeURIComponent(projectId)}/research?${query.toString()}`;
}

type DatasetResearchScope = ScopeResolution & { scientific_selections?: Agent2ScientificSelection[] };

async function resolveExplicitDatasetScope(
  projectId: string,
  datasetId: string,
  sourceSelection: DatasetSourceSelection | null = null,
): Promise<DatasetResearchScope> {
  return readSessionRequest(async (signal) => {
    const [dataset, profile, resources] = await Promise.all([
      getDataset(datasetId),
      getDatasetProfile(datasetId),
      getDatasetSourceResources(datasetId),
    ]);
    signal.throwIfAborted();
    if (sourceSelection && ((dataset.datasetId || dataset.id) !== datasetId || profile.datasetId !== datasetId)) throw new DatasetSourceSelectionError();
    const selectedSource = sourceSelection ? selectedDatasetSourceResource(sourceSelection, resources) : null;
    const supportedScientificResources = resources.filter((item) =>
      [
        "DataFrame",
        "Structure",
        "Trajectory",
        "ElectronicBand",
        "ElectronicDos",
        "PhononBand",
        "PhononDos",
        "VolumetricData",
      ].includes(item.objectType),
    );
    if (!supportedScientificResources.length) {
      // A dataset without an admitted normalized resource cannot enter the
      // durable Agent2 path. Keep the existing bounded product response rather
      // than inventing a source reference.
      return {
        status: "READY",
        dataset_id: dataset.datasetId || dataset.id || datasetId,
        profile_id: profile.profileId || profile.id,
        dataset_name: dataset.name,
      };
    }
    // Materialize every normalized resource into the existing ScientificObject
    // authority.  The previous single-resource selection silently downgraded
    // multi-resource datasets (XRD, phonon, electronic, multi-tool tables) to
    // the legacy planner.  Agent2 needs the complete exact source set so its
    // capability resolver can bind all required slots without question-string
    // special cases.
    const admitted = await Promise.all(
      supportedScientificResources.map(async (resource) => {
        signal.throwIfAborted();
        const promoted = resource.objectType === "DataFrame"
          ? await promoteDatasetTable(projectId, datasetId, resource.objectId)
          : await admitDatasetResource(
              projectId,
              datasetId,
              resource.objectId,
              dataset.name,
            );
        signal.throwIfAborted();
        const selection = sourceSelection && resource === selectedSource ? bindDatasetSourceSelection(sourceSelection, resource, promoted) : null;
        const objectId = String(promoted.object?.id || "");
        const versionId = String(
          promoted.version?.id || promoted.object?.current_version_id || "",
        );
        if (!objectId || !versionId) {
          throw new Error(`数据科学对象版本暂时无法解析: ${resource.objectType}`);
        }
        return {
          resource,
          selection,
          ref: {
            object_id: objectId,
            version_id: versionId,
            project_id: projectId,
            object_type:
              promoted.object?.object_type || resource.objectType,
            display_name:
              promoted.object?.display_name || dataset.name || "Scientific data",
          },
        };
      }),
    );
    const scientificObjectRefs = admitted.map((item) => item.ref);
    const selectedResource = admitted.find((item) => item.selection) || admitted.find(
      (item) => item.ref.object_type === "materials.table",
    ) || admitted[0];
    return {
      status: "READY",
      dataset_id: dataset.datasetId || dataset.id || datasetId,
      profile_id: profile.profileId || profile.id,
      dataset_name: dataset.name,
      dataset_resource_id: selectedResource.resource.objectId,
      scientific_object_ref: selectedResource.ref,
      scientific_object_refs: scientificObjectRefs,
      scientific_selections: admitted.flatMap(item => item.selection ? [item.selection] : []),
    };
  }, new AbortController().signal);
}

function datasetResearchRefs(
  scope: DatasetResearchScope,
  sampleRef?: string,
): {
  objectRefs: Agent2ScientificObjectRef[];
  selections: Agent2ScientificSelection[];
} | null {
  const objectRefs = (
    scope.scientific_object_refs?.length
      ? scope.scientific_object_refs
      : scope.scientific_object_ref
        ? [scope.scientific_object_ref]
        : []
  ) as Agent2ScientificObjectRef[];
  if (!objectRefs.length) return null;
  if (scope.scientific_selections?.length) return { objectRefs, selections: scope.scientific_selections };
  if (!sampleRef?.trim()) return { objectRefs, selections: [] };
  const locator = { sample_ref: sampleRef.trim() };
  const objectRef = objectRefs.find((item) => item.object_type === "materials.table") || objectRefs[0];
  return {
    objectRefs,
    selections: [
      {
        contract_version: "1.0",
        object_ref: objectRef,
        viewer_id: "scientific.table",
        selection_type: "DATASET_SAMPLE",
        semantic_locator: locator,
        display_label: sampleRef.trim(),
        evidence_locator: locator,
      },
    ],
  };
}

export function ResearchPage({
  projectId,
  datasetId,
  sampleRef,
  sourceSelectionToken,
  sessionId,
  runId,
  agent2TurnId,
  branchRootTurnId,
  editTurnId,
  retryOfTurnId,
  retryRequested = false,
  fresh = false,
  resultContextId,
  resultTargetSnapshotId,
  resultTargetItemId,
  contextCandidateFromSearch = false,
  viewerContext,
}: {
  projectId: string;
  datasetId?: string;
  sampleRef?: string;
  sourceSelectionToken?: string;
  sessionId?: string;
  runId?: string;
  agent2TurnId?: string;
  branchRootTurnId?: string;
  editTurnId?: string;
  retryOfTurnId?: string;
  retryRequested?: boolean;
  fresh?: boolean;
  resultContextId?: string;
  resultTargetSnapshotId?: string;
  resultTargetItemId?: string;
  contextCandidateFromSearch?: boolean;
  viewerContext?: ViewerResearchContext;
}) {
  const router = useProductRouter();
  const [resultOpenRequest, setResultOpenRequest] = useState(0);
  const pendingSessionKey = useMemo(() => `mdi:research-pending-session:${JSON.stringify([
    projectId, datasetId || null, sampleRef || null, fresh, resultContextId || null,
    viewerContext?.objectId || null, viewerContext?.versionId || null,
    viewerContext?.selectionToken || null,
    ...(!sampleRef && sourceSelectionToken ? [sourceSelectionToken] : []),
  ])}`, [projectId, datasetId, sampleRef, sourceSelectionToken, fresh, resultContextId, viewerContext?.objectId, viewerContext?.versionId, viewerContext?.selectionToken]);
  const providerSettingsKey = sessionId
    ? `mdi:research-session-settings:${JSON.stringify([projectId, sessionId])}`
    : `${pendingSessionKey}:settings`;
  const [session, setSession] = useState<ResearchSession | null>(null);
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [history, setHistory] = useState<ProjectHistory | null>(null);
  const [question, setQuestion] = useState("");
  const [searchContextCandidateActive, setSearchContextCandidateActive] =
    useState(contextCandidateFromSearch);
  const [autonomyMode, setAutonomyMode] = useState<
    "STANDARD" | "BOUNDED_AUTONOMOUS"
  >("STANDARD");
  const [state, setState] = useState<ResearchState>("idle");
  const [scope, setScope] = useState<ScopeResolution | null>(null);
  const [job, setJob] = useState<PlannerJobCreateResult | null>(null);
  const [events, setEvents] = useState<JobEvent[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [interpretation, setInterpretation] =
    useState<GroundedScientificInterpretation | null>(null);
  const [evidence, setEvidence] =
    useState<InterpretationEvidenceResponse | null>(null);
  const [interpretationStatus, setInterpretationStatus] = useState<
    "idle" | "loading" | "ready" | "limited" | "error"
  >("idle");
  const [error, setError] = useState("");
  const [agent2Progress, setAgent2Progress] =
    useState<Agent2ProgressView | null>(null);
  const [sessionResultProgress, setSessionResultProgress] = useState<Agent2ProgressView | null>(null);
  const [agent2RecoveryState, setAgent2RecoveryState] = useState<ExecutionReadState & { turnId: string }>({ status: "connected", turnId: "" });
  const [researchPerformanceSample, setResearchPerformanceSample] =
    useState<ResearchPerformanceSample | null>(null);
  const contextNavigation = useResearchContextNavigation(projectId, sessionId || session?.id, agent2TurnId, agent2ProgressForTurn(agent2Progress, agent2TurnId)?.status, true);
  const navigationTurnId = contextNavigation.selectedTurnId;
  const agent2ContextManifest = contextNavigation.context.data?.manifest || null;
  const agent2ContextManifests = contextNavigation.context.data?.manifests || [];
  const agent2Turns = contextNavigation.directory.data || EMPTY_RESEARCH_TURNS;
  const [agent2CancelState, setAgent2CancelState] = useState<ExecutionCancelState>("idle");
  const [agent2DispatchNotice, setAgent2DispatchNotice] = useState("");
  const [agent2DispatchRetryable, setAgent2DispatchRetryable] = useState(false);
  const [agent2CancelNotice, setAgent2CancelNotice] = useState("");
  const [agent2RetryPending, setAgent2RetryPending] = useState(false);
  const [continueTurnId, setContinueTurnId] = useState<string | null>(null);
  const [showFullConversation, setShowFullConversation] = useState(false);
  const [conversationWindowStart, setConversationWindowStart] = useState(0);
  const editSource = useEditResearchSource(projectId, sessionId || session?.id, editTurnId);
  const editingTurn = editSource.turn;
  const editingResult = editSource.result;
  const editingLoadState = editSource.loadState;
  const editedDraftKeyRef = useRef<string | null>(null);
  const seededEditDraftKeyRef = useRef<string | null>(null);
  const editComposerFocusRef = useRef<{
    key: string; origin: Element | null; handled: boolean;
  } | null>(null);
  const agent2ExecutionRef = useRef<ReturnType<typeof watchAgent2Execution> | null>(null);
  const submitInFlightRef = useRef<symbol | null>(null);
  // Route identity excludes the session created by this submission itself.
  // A new route releases its composer while accepted work stays in the original session.
  const submitScope = JSON.stringify([pendingSessionKey, sessionId, agent2TurnId, editTurnId, runId]);
  const submitLifetime = useMemo(() => Symbol(), [submitScope]);
  const currentSubmitScope = useRef<symbol | null>(submitLifetime);
  currentSubmitScope.current = submitLifetime;
  const isCurrentSubmissionScope = () => currentSubmitScope.current === submitLifetime;
  useEffect(() => {
    currentSubmitScope.current = submitLifetime;
    setState(current => current === "planning" ? "idle" : current);
    setError("");
    return () => { submitInFlightRef.current = null; currentSubmitScope.current = null; };
  }, [submitLifetime]);
  const resultActionRef = useRef<symbol | null>(null);
  const [resultActionPending, setResultActionPending] = useState(false);
  const resultActionScope = JSON.stringify([projectId, sessionId || session?.id, agent2TurnId, editTurnId]);
  const branchReadRef = useRef<AbortController | null>(null);
  const currentResultActionScope = useRef(resultActionScope);
  currentResultActionScope.current = resultActionScope;
  useEffect(() => {
    setResultActionPending(false); setAgent2RetryPending(false); setContinueTurnId(null);
    return () => { resultActionRef.current = null; branchReadRef.current?.abort(); branchReadRef.current = null; };
  }, [resultActionScope]);
  const autoRetryTurnRef = useRef<string | null>(null);
  const [conversationWidth, setConversationWidth] = useState(() =>
    defaultResearchConversationWidth(Boolean(runId || agent2TurnId)),
  );
  const [conversationMaxWidth, setConversationMaxWidth] = useState(760);
  const [sessionHistoryOpen, setSessionHistoryOpen] = useState(false);
  const [sessionHistoryQuery, setSessionHistoryQuery] = useState("");
  const [sessionHistoryStatus, setSessionHistoryStatus] = useState<
    "current" | "archived" | "trashed"
  >("current");
  const [sessionSelectionMode, setSessionSelectionMode] = useState(false);
  const [selectedSessionIds, setSelectedSessionIds] = useState<string[]>([]);
  const [sessionBulkBusy, setSessionBulkBusy] = useState(false);
  const [sessionLifecycleBusy, setSessionLifecycleBusy] = useState<
    string | null
  >(null);
  const [sessionRenameTarget, setSessionRenameTarget] =
    useState<ResearchSession | null>(null);
  const [sessionRenameValue, setSessionRenameValue] = useState("");
  const sessionLifecycleFocusRef = useRef<HTMLElement | null>(null);
  const sessionHistoryFilterRefs = useRef(
    new Map<"current" | "archived" | "trashed", HTMLButtonElement>(),
  );
  const [sessionLifecycleNotice, setSessionLifecycleNotice] = useState("");
  const sessionOperation = useSessionOperation(projectId);
  const [sessionActionConfirmation, setSessionActionConfirmation] = useState<{ items: ResearchSession[]; action: ResearchSessionBulkAction; bulk: boolean } | null>(null);
  const [sessionDirectoryReading, setSessionDirectoryReading] = useState(false);
  const [sessionDirectoryError, setSessionDirectoryError] = useState("");
  const sessionDirectoryReadRef = useRef<AbortController | null>(null);
  const pageReadScopeRef = useRef("");
  useEffect(() => {
    setSessionRenameTarget(null); setSessionActionConfirmation(null);
    setSessionLifecycleNotice(""); setSessionDirectoryError(""); setSessionDirectoryReading(false);
    setSelectedSessionIds([]);
    return () => { sessionDirectoryReadRef.current?.abort(); sessionDirectoryReadRef.current = null; };
  }, [projectId]);
  useEffect(() => {
    if (!sessionRenameTarget && !sessionActionConfirmation) return;
    const bodyOverflow = document.body.style.overflow;
    const rootOverflow = document.documentElement.style.overflow;
    document.body.style.overflow = document.documentElement.style.overflow = "hidden";
    return () => { document.body.style.overflow = bodyOverflow; document.documentElement.style.overflow = rootOverflow; };
  }, [Boolean(sessionRenameTarget || sessionActionConfirmation)]);
  const [mobilePanel, setMobilePanel] = useState<"timeline" | "workbench">(
    !editTurnId && (runId || agent2TurnId) ? "workbench" : "timeline",
  );
  useEffect(() => { if (editTurnId) setMobilePanel("timeline"); }, [editTurnId]);
  const [pageLoadState, setPageLoadState] = useState<
    "loading" | "ready" | "error"
  >("loading");
  const [runResolutionState, setRunResolutionState] = useState<
    "idle" | "loading" | "settled"
  >(runId && !agent2TurnId ? "loading" : runId ? "settled" : "idle");
  const [runReadFailures, setRunReadFailures] = useState<string[]>([]);
  const [runReadPending, setRunReadPending] = useState(false);
  const [pageLoadError, setPageLoadError] = useState("");
  const [projectHistoryReadState, setProjectHistoryReadState] = useState<"loading" | "ready" | "error">("loading");
  const [sessionLoadState, setSessionLoadState] = useState<
    "ready" | "loading" | "error"
  >("ready");
  const [sessionLoadError, setSessionLoadError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const postRunMessageRef = useRef<string | null>(null);
  const failedRunMessageRef = useRef<string | null>(null);
  const [providerStatus, setProviderStatus] = useState<ProviderStatus | null>(
    null,
  );
  const [providerOptions, setProviderOptions] = useState<ProviderOption[]>([]);
  const [providerLoadState, setProviderLoadState] = useState<
    "loading" | "ready" | "error"
  >("loading");
  const [providerReloadKey, setProviderReloadKey] = useState(0);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [userModels, setUserModels] = useState<UserModel[]>([]);
  const [researchSettingsOpen, setResearchSettingsOpen] = useState(false);
  const providerChoiceRef = useRef<{ key: string; provider: string; model: string } | null>(null);
  const providerScopeRef = useRef<string | null>(null);
  function createAgent2ResearchTurn(project: string, session: string, input: Parameters<typeof admitResearchTurn>[2]) {
    try {
      const settings = JSON.stringify({
        provider: selectedProvider, model: selectedModel, thinkingMode, autonomyMode,
      });
      window.sessionStorage.setItem(providerSettingsKey, settings);
      // Admission navigates from a dataset/object URL to the canonical session
      // URL. Keep that exact session's choice across the route handoff.
      window.sessionStorage.setItem(`mdi:research-session-settings:${JSON.stringify([project, session])}`, settings);
    } catch {
      // The current submission still carries the exact selected settings.
    }
    return admitResearchTurn(project, session, {
      ...input,
      ...(input.requested_action === "INTERPRET_RESULT" ? { autonomy_mode: "STANDARD" as const } : {}),
      model_selection: { provider: selectedProvider, model: selectedModel, thinking_mode: thinkingMode },
    });
  }
  const [thinkingMode, setThinkingMode] = useState<
    "quick" | "standard" | "deep"
  >("standard");
  const questionInputRef = useRef<HTMLTextAreaElement | null>(null);
  const pendingDraftHandoffRef = useRef<{ key: string; draft: string } | null>(null);
  const composerDraftCache = useRef(new Map<string, string>());
  const composerDraftWriteFailures = useRef(new Set<string>());
  const restoredDraftRef = useRef<{
    key: string;
    skipPersistence: boolean;
  } | null>(null);
  const workbenchRef = useRef<HTMLElement | null>(null);
  const conversationPreferredWidthRef = useRef<number | null>(null);
  const sessionHistoryTriggerRef = useRef<HTMLButtonElement | null>(null);
  const sessionHistoryRef = useRef<HTMLDivElement | null>(null);
  const sessionHistorySearchRef = useRef<HTMLInputElement | null>(null);
  const mobileTimelineTabRef = useRef<HTMLButtonElement | null>(null);
  const mobileWorkbenchTabRef = useRef<HTMLButtonElement | null>(null);
  const conversationHistoryRef = useRef<HTMLDivElement | null>(null);
  const contextManifestRef = useRef<HTMLDetailsElement | null>(null);
  const contextManifestTriggerRef = useRef<HTMLButtonElement | null>(null);
  const contextReturnFocusRef = useRef<HTMLElement | null>(null);
  const workbenchFocusRef = useRef<{
    scope: string;
    target: "context" | "results" | "return";
    from: Element | null;
  } | null>(null);
  const contextPanelRef = useRef<HTMLDivElement | null>(null);
  const branchNavigationRef = useRef<HTMLElement | null>(null);
  const contextRetryFocus = useRef<string | null>(null);
  const directoryRetryFocus = useRef<string | null>(null);
  useEffect(() => () => { contextRetryFocus.current = null; directoryRetryFocus.current = null; }, [projectId, sessionId, agent2TurnId]);
  useEffect(() => {
    if (!contextNavigation.context.pending && !contextNavigation.context.failed && contextNavigation.context.data && contextRetryFocus.current === contextNavigation.context.scope) {
      contextRetryFocus.current = null;
      if (contextManifestRef.current) {
        contextManifestRef.current.open = true;
        contextManifestRef.current.querySelector<HTMLElement>("summary")?.focus();
      }
    }
  }, [contextNavigation.context.pending, contextNavigation.context.failed, contextNavigation.context.data, contextNavigation.context.scope]);
  useEffect(() => {
    if (!contextNavigation.directory.pending && !contextNavigation.directory.failed && contextNavigation.directory.data && directoryRetryFocus.current === contextNavigation.directory.scope) {
      directoryRetryFocus.current = null;
      (branchNavigationRef.current?.querySelector<HTMLElement>("summary") || questionInputRef.current)?.focus();
    }
  }, [contextNavigation.directory.pending, contextNavigation.directory.failed, contextNavigation.directory.data, contextNavigation.directory.scope]);
  const [wholeViewerVersionKey, setWholeViewerVersionKey] = useState("");
  const viewerSelectionKey = JSON.stringify([projectId, viewerContext?.objectId, viewerContext?.versionId, viewerContext?.selectionToken]);
  const currentViewerSelectionKey = useRef(viewerSelectionKey); currentViewerSelectionKey.current = viewerSelectionKey;
  const scientificSelectionRead = useRef<AbortController | null>(null);
  useEffect(() => () => scientificSelectionRead.current?.abort(), [viewerSelectionKey]);
  const exactViewerContext = useMemo(() => {
    if (
      !viewerContext?.objectId ||
      !viewerContext.versionId ||
      !viewerContext.objectType
    )
      return null;
    const sourceRef = {
      projectId,
      objectId: viewerContext.objectId,
      versionId: viewerContext.versionId,
      objectType: viewerContext.objectType,
      displayName: viewerContext.displayName || "所选科学数据",
    };
    if (!viewerContext.selectionToken || wholeViewerVersionKey === viewerSelectionKey) return { sourceRef, selection: null, selectionError: "" };
    try {
      const workspace = decodeWorkspaceSelectionUrl(
        viewerContext.selectionToken,
      );
      const descriptor = resolveScientificViewer({
        objectType: viewerContext.objectType,
      });
      const selection = scientificSelectionFromWorkspace(
          workspace,
          sourceRef,
          descriptor.viewerId,
        );
      if (!selection) throw new Error("VIEWER_SELECTION_SCOPE_INVALID");
      return { sourceRef, selection, selectionError: "" };
    } catch {
      return { sourceRef, selection: null, selectionError: "链接中的选择无法绑定到此项目的精确版本。请返回数据重新选择，或明确改用此完整版本。" };
    }
  }, [projectId, viewerContext, wholeViewerVersionKey, viewerSelectionKey]);
  const activeSearchResultContextId =
    contextCandidateFromSearch && searchContextCandidateActive
      ? resultContextId
      : undefined;
  const activeViewerContext =
    exactViewerContext &&
    (!contextCandidateFromSearch || searchContextCandidateActive)
      ? exactViewerContext
      : null;
  const incompleteViewerContext = Boolean(viewerContext?.objectId || viewerContext?.versionId || viewerContext?.objectType || viewerContext?.selectionToken)
    && (!viewerContext?.objectId || !viewerContext?.versionId || !viewerContext?.objectType);
  const viewerSelectionError = incompleteViewerContext
    ? "此来源链接缺少对象、版本或科学类型，请返回项目数据重新打开。"
    : activeViewerContext?.selectionError || "";
  const hasExplicitScientificHandoff = Boolean(
    datasetId || sourceSelectionToken || activeViewerContext || activeSearchResultContextId || incompleteViewerContext,
  );
  const datasetSelection = useMemo(() => {
    try {
      const selection = datasetSourceSelection(projectId, datasetId, sourceSelectionToken, sampleRef);
      if (selection && (activeViewerContext || incompleteViewerContext || activeSearchResultContextId)) throw new DatasetSourceSelectionError();
      return { selection, error: "" };
    }
    catch { return { selection: null, error: "链接中的数据选择无法用于本次研究。请返回来源数据重新选择；你可以继续编辑问题。" }; }
  }, [projectId, datasetId, sourceSelectionToken, sampleRef, activeViewerContext, incompleteViewerContext, activeSearchResultContextId]);
  const [workbenchView, setWorkbenchView] = useState<"results" | "context">(() =>
    !agent2TurnId && !runId && (activeViewerContext || datasetId) && !viewerSelectionError && !datasetSelection.error
      ? "context" : "results",
  );
  const [workbenchVisibility, setWorkbenchVisibility] = useState<{ scope: string; open: boolean } | null>(null);
  useEffect(() => {
    if (workbenchView === "context" && contextManifestRef.current) contextManifestRef.current.open = true;
  }, [workbenchView, contextNavigation.context.data?.manifest.context_manifest_id]);
  const startFreshResearchHref = freshResearchHref(
    projectId,
    datasetId,
    sampleRef,
    viewerContext,
    sourceSelectionToken,
  );

  useEffect(() => {
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
  }, []);

  useEffect(() => {
    const onResearchPerformance = (event: Event) => {
      const sample = (event as CustomEvent<ResearchPerformanceSample>).detail;
      if (
        sample &&
        typeof sample.attemptId === "string" &&
        typeof sample.turnId === "string" &&
        Number.isFinite(sample.firstTruthfulProgressMs)
      ) {
        setResearchPerformanceSample(sample);
      }
    };
    window.addEventListener(
      "mdi:research-performance",
      onResearchPerformance,
    );
    return () =>
      window.removeEventListener(
        "mdi:research-performance",
        onResearchPerformance,
      );
  }, []);

  useEffect(() => {
    setAgent2Progress(null);
    setAgent2CancelNotice("");
    setAgent2CancelState("idle");
    setAgent2DispatchNotice("");
    setAgent2DispatchRetryable(false);
    setAgent2RecoveryState({ status: "connected", turnId: agent2TurnId || "" });
    if (!agent2TurnId) return;
    const execution = watchAgent2Execution(agent2TurnId, {
      progress: (next) => {
        setAgent2Progress(next);
        if (next.status === "ANSWERED") {
          setState("idle");
          setError("");
        }
      },
      recovery: (value) => setAgent2RecoveryState({ ...value, turnId: agent2TurnId }),
      cancellation: (state, notice) => {
        setAgent2CancelState(state);
        setAgent2CancelNotice(notice);
      },
      dispatch: (notice, retryable) => {
        setAgent2DispatchNotice(notice);
        setAgent2DispatchRetryable(retryable);
      },
    });
    agent2ExecutionRef.current = execution;
    return () => {
      execution.dispose();
      agent2ExecutionRef.current = null;
    };
  }, [agent2TurnId, projectId, sessionId]);

  useEffect(() => {
    if (
      !session?.id ||
      !agent2TurnId ||
      !agent2ProgressHasFreshSessionMessages(agent2Progress?.status || "")
    )
      return;
    let active = true;
    const controller = new AbortController();
    const currentSessionId = session.id;
    void readSessionRequest((signal) => getResearchSession(currentSessionId, signal), controller.signal)
      .then((full) => {
        if (!active) return;
        validateResearchSession(full, projectId, currentSessionId);
        setSession(full);
        setSessionLoadState("ready");
      })
      .catch(() => {
        if (active) {
          setSessionLoadState("error");
          setSessionLoadError("研究对话暂时无法更新，请重新加载对话。");
        }
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [agent2Progress?.status, agent2TurnId, session?.id, projectId]);

  useEffect(() => {
    if (!session?.id || !agent2TurnId) return;
    const recoveredTurn = resolveAgent2TurnForRecovery(agent2Turns, projectId, session.id, agent2TurnId);
    if (!recoveredTurn) return;
    setSession((current) => {
      if (!current || current.id !== recoveredTurn.research_session_id ||
          (current.projectId || current.project_id) !== projectId) return current;
      const messages = current.messages || [];
      if (messages.some((message) => message.id === recoveredTurn.user_message.id)) return current;
      return { ...current, messages: [...messages, {
        id: recoveredTurn.user_message.id, session_id: current.id, role: "user",
        content: recoveredTurn.user_message.content, created_at: recoveredTurn.created_at,
      }] };
    });
  }, [agent2Turns, projectId, session?.id, agent2TurnId]);

  async function cancelAgent2Turn() {
    setError("");
    await agent2ExecutionRef.current?.cancel();
  }

  async function retryAgent2Turn(action: ResultResearchAction = "rerun") {
    if (!agent2TurnId || !session || !canResearch || !selectedSessionIsWritable || submitInFlightRef.current || resultActionRef.current) return;
    if (!userModels.some((item) => item.provider === selectedProvider && item.model === selectedModel)) {
      setError("请先在研究设置中选择可用模型。"); return;
    }
    const owner = Symbol(); resultActionRef.current = owner;
    const actionScope = resultActionScope;
    const controller = new AbortController(); branchReadRef.current = controller;
    const owns = () => resultActionRef.current === owner && currentResultActionScope.current === actionScope;
    setAgent2RetryPending(true); setResultActionPending(true); setError("");
    try {
      const exactTurn = await readBranchTurn(projectId, session.id, agent2TurnId, controller.signal);
      if (!owns()) return;
      let input: Parameters<typeof admitResearchTurn>[2] = agent2RetryInput(exactTurn);
      if (action === "reinterpret") {
        const result = await readBranchResult(projectId, agent2TurnId, controller.signal);
        if (!owns()) return;
        if (!result) throw new Error("科学结果暂时无法读取，请重新读取后再解读。");
        input = resultFollowUpInput("reinterpret", result);
      }
      const next = await createAgent2ResearchTurn(projectId, session.id, {
        ...input, admission_key: createAgent2AdmissionKey(), autonomy_mode: autonomyMode,
      });
      if (!owns()) return;
      carryUnsentDraft(next.turn_id);
      router.push(`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(next.turn_id)}${action === "rerun" ? `&retryOf=${encodeURIComponent(exactTurn.turn_id)}` : ""}`);
    } catch (reason) {
      if (owns()) setError(scientistFacingResearchRequestError(reason));
    } finally {
      controller.abort();
      if (owns()) { resultActionRef.current = null; branchReadRef.current = null; setAgent2RetryPending(false); setResultActionPending(false); }
    }
  }

  function carryUnsentDraft(turnId: string) {
    if (!session) return;
    const draft = questionInputRef.current?.value ?? question;
    const key = researchComposerDraftKey(projectId, session.id, turnId);
    pendingDraftHandoffRef.current = { key, draft };
    storeComposerDraft(key, draft);
  }

  function editAgent2Turn() {
    if (!agent2TurnId || !session) return;
    // On narrow screens the workbench tab can be active while a user starts
    // editing from the scientific presentation. Switch back to the
    // conversation surface immediately so the immutable branch composer is
    // visible instead of leaving the user on the result panel.
    setMobilePanel("timeline");
    router.push(
      `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(agent2TurnId)}&edit=${encodeURIComponent(agent2TurnId)}`,
      { scroll: false },
    );
  }

  function continueAgent2Research() {
    if (!agent2TurnId) return;
    const focusOrigin = document.activeElement;
    // Continue is a composer action. Keep the control reachable on mobile
    // even when the user invoked it from the Workbench presentation tab.
    setMobilePanel("timeline");
    setContinueTurnId(agent2TurnId);
    setAgent2CancelNotice(
      "继续研究会保留当前会话与已授权的精确上下文；只有提交新问题后才会开始新的处理。",
    );
    requestAnimationFrame(() => {
      if (currentSubmitScope.current !== submitLifetime || document.activeElement !== focusOrigin) return;
      const input = questionInputRef.current;
      if (!input || input === focusOrigin) return;
      input.focus({ preventScroll: true });
      input.scrollIntoView?.({ block: "nearest" });
    });
  }

  async function runResultResearch(action: ResultResearchAction, result: Agent2ResearchTurnResult) {
    if (!session?.id || !canResearch || !selectedSessionIsWritable) throw new Error("当前研究不可修改，请检查访问权限。");
    if (result.research_turn_id !== agent2TurnId) throw new Error("分析结果与当前研究不匹配，请重新读取。");
    if (!userModels.some((item) => item.provider === selectedProvider && item.model === selectedModel)) throw new Error("请先在研究设置中选择可用模型。");
    if (submitInFlightRef.current || resultActionRef.current) throw new Error("正在提交研究，请稍候。");
    const owner = Symbol(); resultActionRef.current = owner;
    const scope = resultActionScope;
    setResultActionPending(true);
    try {
      const next = await createAgent2ResearchTurn(projectId, session.id, {
        ...resultFollowUpInput(action, result, selectedAgent2Turn), admission_key: createAgent2AdmissionKey(), autonomy_mode: autonomyMode,
      });
      if (resultActionRef.current !== owner || currentResultActionScope.current !== scope) return;
      carryUnsentDraft(next.turn_id);
      router.push(`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(next.turn_id)}`);
    } finally {
      if (resultActionRef.current === owner) { resultActionRef.current = null; setResultActionPending(false); }
    }
  }

  function clampConversationWidth(value: number): number {
    if (!Number.isFinite(value)) return conversationWidth;
    const workbenchWidth =
      workbenchRef.current?.getBoundingClientRect().width || 1280;
    const maximum = Math.min(760, Math.max(320, workbenchWidth - 487));
    return Math.round(Math.min(maximum, Math.max(320, value)));
  }

  function chooseConversationWidth(value: number) {
    const width = clampConversationWidth(value);
    conversationPreferredWidthRef.current = width;
    setConversationWidth(width);
  }

  // Modern Turn reads have their own scoped subscriptions. Selecting a Turn or
  // editing its question must not invalidate the shared project/session page.
  const pageRunId = agent2TurnId ? undefined : runId;
  const pageTurnId = sessionId ? undefined : agent2TurnId;
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const scopeKey = JSON.stringify([projectId, sessionId, pageRunId, pageTurnId, datasetId, fresh, hasExplicitScientificHandoff]);
    const preservePage = pageReadScopeRef.current === scopeKey && pageLoadState === "ready";
    pageReadScopeRef.current = scopeKey;
    if (!preservePage) {
      setSession(null);
      setHistory(null);
      setSessions([]);
      setScope(null);
      setJob(null);
      setEvents([]);
      setArtifacts([]);
      setInterpretation(null);
      setEvidence(null);
      setRunReadFailures([]);
      setRunReadPending(false);
      setError("");
      setState("idle");
      postRunMessageRef.current = null;
      failedRunMessageRef.current = null;
    }
    if (!preservePage) setPageLoadState("loading");
    if (!preservePage) setSessionLoadState("loading");
    setPageLoadError("");
    setProjectHistoryReadState("loading");
    if (!preservePage) setRunResolutionState(
      pageRunId ? "loading" : "idle",
    );
    let targetSessionId = sessionId;
    if (!targetSessionId && !pageTurnId && !pageRunId) {
      try { targetSessionId = window.sessionStorage.getItem(pendingSessionKey) || undefined; }
      catch { /* An explicit URL still recovers the conversation without storage. */ }
    }
    let pendingReads = 0;
    let hasReadableContent = preservePage;
    const readFailures = new Set<string>();
    const showReadFailures = () => {
      const labels = [...readFailures].filter((label) => label !== "当前对话");
      setPageLoadError(labels.length ? `暂时无法读取：${labels.join("、")}。已打开的内容和输入仍然保留。` : "");
    };
    async function readPagePart<T>(label: string, request: (signal: AbortSignal) => Promise<T>, accept: (value: T) => void, reject: () => void = () => {}): Promise<T | null> {
      pendingReads += 1;
      try {
        const value = await readSessionRequest(request, controller.signal);
        if (!active) return null;
        accept(value);
        hasReadableContent = true;
        setPageLoadState("ready");
        readFailures.delete(label);
        showReadFailures();
        return value;
      } catch {
        if (active) { readFailures.add(label); showReadFailures(); reject(); }
        return null;
      } finally {
        pendingReads -= 1;
        if (active && pendingReads === 0 && !hasReadableContent) setPageLoadState("error");
      }
    }
    let sessionRequest: Promise<ResearchSession | null> | null = null;
    const readSelectedSession = (id?: string) => {
      if (sessionRequest) return sessionRequest;
      if (!preservePage) setSessionLoadState("loading");
      setSessionLoadError("");
      sessionRequest = readPagePart("当前对话", async (signal) => {
        let ownerId = id;
        if (!ownerId && pageTurnId) {
          const turn = await getAgent2ResearchTurn(pageTurnId, { signal });
          ownerId = turn?.research_session_id;
          if (typeof ownerId !== "string" || !ownerId.trim()) throw new Error("Research turn owner missing");
          validateBranchTurn(turn, projectId, ownerId, pageTurnId);
        }
        signal.throwIfAborted();
        if (!ownerId) throw new Error("Research session owner missing");
        return validateResearchSession(await getResearchSession(ownerId, signal), projectId, ownerId);
      }, (full) => {
        targetSessionId = full.id;
        setSession(full);
        setSessions((current) => current.some((item) => item.id === full.id) ? current : [full, ...current]);
        setSessionLoadState("ready");
      }, () => {
        if (!preservePage) setSession(null);
        setSessionLoadState("error");
        setSessionLoadError("这条研究记录暂时无法读取，请重试。");
      });
      return sessionRequest;
    };
    // Resolve old Turn links from their saved owner before opening a conversation.
    // Neither an exact session nor a Turn depends on directory/history reads.
    if (targetSessionId || pageTurnId) void readSelectedSession(targetSessionId);
    const pendingCreation = hasPendingResearchSessionCreation(projectId, datasetId, pendingSessionKey);
    const explicitNewResearch = !targetSessionId && !pageRunId && !pageTurnId && (fresh || hasExplicitScientificHandoff || pendingCreation);
    if (explicitNewResearch) setSessionLoadState("ready");
    const directoryRequest = readPagePart("研究记录列表", (signal) => listResearchSessions(projectId, signal), (items) => {
        validateSessionDirectory(items, projectId);
        setSessions((current) => {
          const exact = current.find((item) => item.id === targetSessionId);
          return exact && !items.some((item) => item.id === exact.id) ? [exact, ...items] : items;
        });
        if (pageTurnId) return;
        const runSession = pageRunId
          ? items.find((item) => researchSessionReferencesRun(item, pageRunId))
          : undefined;
        // An explicit session id is an authoritative navigation target. When a
        // historical run is not yet normalized onto that session, retain the
        // requested session rather than turning a valid route into a missing
        // conversation error. A run-only route still requires an explicit
        // persisted run binding and must not fall back to an unrelated session.
        const selected = targetSessionId
          ? items.find((item) => item.id === targetSessionId)
          : pageRunId
            ? runSession
            : fresh || hasExplicitScientificHandoff || pendingCreation
              ? undefined
              : items.find(
                  (item) =>
                    !["archived", "trashed"].includes(
                      String(item.status || "active").toLowerCase(),
                    ),
                );
        const requestedSessionId = selected?.id || targetSessionId;
        if (requestedSessionId) {
          void readSelectedSession(requestedSessionId);
        } else {
          setSessionLoadState(targetSessionId ? "error" : "ready");
          setSessionLoadError(targetSessionId ? "研究会话不存在或已不可访问。" : "");
        }
    }, () => {
      if (!targetSessionId && !pageTurnId && !explicitNewResearch && !preservePage) {
        setSessionLoadState("error");
        setSessionLoadError("研究记录列表暂时无法读取，请重试后继续。");
      }
    });
    void readPagePart("项目数据", (signal) => getProjectHistory(projectId, { signal }), (nextHistory) => {
        const historyIds = [nextHistory.project.id, nextHistory.project.projectId].filter(Boolean);
        if (!historyIds.length || historyIds.some((id) => id !== projectId)) throw new Error("Project history mismatch");
        setHistory(nextHistory);
        setProjectHistoryReadState("ready");
        if (datasetId && !pageRunId && !sessionId) {
          // Opening Research reads its source; scientific admission belongs to
          // the user's submission, after any exact selection is validated.
          void readSessionRequest(async () => {
            const [dataset, profile] = await Promise.all([getDataset(datasetId), getDatasetProfile(datasetId)]);
            if ((dataset.datasetId || dataset.id) !== datasetId || profile.datasetId !== datasetId) throw new Error("Research source identity mismatch");
            return { status: "READY" as const, dataset_id: datasetId, dataset_name: dataset.name, profile_id: profile.profileId || profile.id };
          }, controller.signal)
            .then((selectedScope) => {
              if (active) setScope(selectedScope);
            })
            .catch(() => {
              if (!active) return;
              setScope(null);
              setPageLoadError("所选数据暂时无法读取，请重新加载后再试。问题仍会保留。");
            });
        }
        if (pageRunId) {
          const historicalRun = nextHistory.analyses.find(
            (item) => item.jobId === pageRunId,
          );
          if (historicalRun) {
            const historicalDataset = nextHistory.datasets.find(
              (item) => item.datasetId === historicalRun.datasetId,
            );
            setScope(
              historicalRun.datasetId
                ? {
                    status: "READY",
                    dataset_id: historicalRun.datasetId,
                    dataset_name: historicalDataset?.name,
                  }
                : null,
            );
            setJob((current) => current?.job_id === pageRunId ? current : { ok: true, job_id: pageRunId, plan: null });
            if (!preservePage) setState(researchRunState(historicalRun.status));
            let pendingReads = 0;
            async function readRunPart<T>(label: string, request: (signal: AbortSignal) => Promise<T>, accept: (value: T) => void): Promise<T> {
              pendingReads += 1;
              setRunReadPending(true);
              try {
                const value = await readSessionRequest(request, controller.signal);
                if (!active) throw new Error("Run read cancelled");
                accept(value);
                setRunReadFailures((current) => current.filter((item) => item !== label));
                return value;
              } catch (reason) {
                if (active) setRunReadFailures((current) => current.includes(label) ? current : [...current, label]);
                throw reason;
              } finally {
                pendingReads -= 1;
                if (active && pendingReads === 0) setRunReadPending(false);
              }
            }
            const readEvidence = (interpretationId: string) => readRunPart("解读依据", (signal) => getPlannerInterpretationEvidence(interpretationId, { signal }), (value) => {
              if (value.interpretationId !== interpretationId) throw new Error("Interpretation evidence mismatch");
              setEvidence(value);
            }).catch(() => undefined);
            // Show successful sections immediately. Optional run records must
            // not hold saved scientific results behind a shared loading state.
            void Promise.allSettled([
              readRunPart("运行详情", (signal) => getPlannerJob(pageRunId, { signal }), (detail) => {
                validateLegacyJob(detail, pageRunId, projectId);
                setJob((current) => current ? {
                  ...current,
                  plan: detail.analysisPlan || current.plan,
                  plan_id: detail.planId || current.plan_id,
                  plan_hash: detail.planHash || current.plan_hash,
                } : current);
              }),
              readRunPart("运行记录", (signal) => getPlannerJobEvents(pageRunId, 0, { signal }), (value) => setEvents((items) => mergeJobEvents(items, value))),
              readRunPart("科学结果", (signal) => getPlannerJobArtifacts(pageRunId, { signal }), (value) => setArtifacts((items) => mergeArtifacts(items, value)))
                .finally(() => { if (active) setRunResolutionState("settled"); }),
              readRunPart("结果解读", (signal) => getPlannerJobInterpretations(pageRunId, { signal }), (value) => {
                const saved = value.interpretations?.at(-1) || null;
                setInterpretation((current) => saved || current);
                setInterpretationStatus((current) => saved ? saved.completeness === "COMPLETE" ? "ready" : "limited" : current);
                setEvidence((current) => !saved || current?.interpretationId === saved.interpretationId ? current : null);
                if (saved) void readEvidence(saved.interpretationId);
                else setRunReadFailures((current) => current.filter((item) => item !== "解读依据"));
              }),
            ]).then(
              async ([
                detailResult,
                ,
                ,
                interpretationResult,
              ]) => {
                if (!active) return;
                const historyInterpretations =
                  interpretationResult.status === "fulfilled"
                    ? interpretationResult.value
                    : null;
                const existingInterpretation =
                  historyInterpretations?.interpretations?.at(-1) || null;
                const directory = await directoryRequest;
                const loadedSession = await sessionRequest;
                const knownOwnerId = directory?.find((item) => researchSessionReferencesRun(item, pageRunId))?.id || historicalRun.researchSessionId;
                const owner = knownOwnerId && loadedSession?.id !== knownOwnerId ? null : loadedSession;
                if (!active) return;
                if (
                  existingInterpretation &&
                  owner &&
                  !researchSessionReferencesRun(owner, pageRunId, "post_run")
                ) {
                  void createResearchAssistantProjection(owner.id, {
                    phase: "post_run",
                    datasetId: historicalRun.datasetId,
                    runId: pageRunId,
                  })
                    .then((message) => {
                      if (active) appendSessionMessage(message);
                    })
                    .catch(() => undefined);
                }
                const historicalState = researchRunState(historicalRun.status);
                const planHash =
                  detailResult.status === "fulfilled"
                    ? detailResult.value.planHash
                    : null;
                if (
                  interpretationResult.status === "fulfilled" &&
                  !existingInterpretation &&
                  owner &&
                  (historicalState === "complete" ||
                    historicalState === "partial") &&
                  planHash
                ) {
                  setInterpretationStatus("loading");
                  void createScientificInterpretation(pageRunId, planHash, controller.signal)
                    .then((result) => {
                      if (!active) return;
                      const recovered = result.interpretation || null;
                      setInterpretation(recovered);
                      setInterpretationStatus(
                        recovered
                          ? recovered.completeness === "COMPLETE"
                            ? "ready"
                            : "limited"
                          : "error",
                      );
                      if (!recovered) setRunReadFailures((items) => items.includes("结果解读") ? items : [...items, "结果解读"]);
                      if (recovered) {
                        setEvidence((current) => current?.interpretationId === recovered.interpretationId ? current : null);
                        void readEvidence(recovered.interpretationId);
                        void createResearchAssistantProjection(owner.id, {
                          phase: "post_run",
                          datasetId: historicalRun.datasetId,
                          runId: pageRunId,
                        })
                          .then((message) => {
                            if (active) appendSessionMessage(message);
                          })
                          .catch(() => undefined);
                      }
                    })
                    .catch(() => {
                      if (active) {
                        setInterpretationStatus("error");
                        setRunReadFailures((items) => items.includes("结果解读") ? items : [...items, "结果解读"]);
                      }
                    });
                }
                if (
                  historicalState === "failed" &&
                  owner &&
                  !researchSessionReferencesRun(owner, pageRunId, "failed")
                ) {
                  void createResearchAssistantProjection(owner.id, {
                    phase: "failed",
                    datasetId: historicalRun.datasetId,
                    runId: pageRunId,
                    failureCode: "JOB_FAILED",
                  })
                    .then((message) => {
                      if (active) appendSessionMessage(message);
                    })
                    .catch(() => undefined);
                }
                setRunResolutionState("settled");
              },
            );
          } else {
            setRunResolutionState("settled");
            setRunReadPending(false);
          }
        }
      }, () => {
        setProjectHistoryReadState("error");
        setRunReadPending(false);
      });
    const refreshPersistedState = () => {
      setReloadKey((current) => current + 1);
    };
    const refreshOnVisible = () => {
      if (document.visibilityState === "visible") refreshPersistedState();
    };
    window.addEventListener("online", refreshPersistedState);
    document.addEventListener("visibilitychange", refreshOnVisible);
    return () => {
      active = false;
      controller.abort();
      window.removeEventListener("online", refreshPersistedState);
      document.removeEventListener("visibilitychange", refreshOnVisible);
    };
  }, [
    pendingSessionKey,
    datasetId,
    fresh,
    hasExplicitScientificHandoff,
    projectId,
    reloadKey,
    pageRunId,
    pageTurnId,
    sessionId,
  ]);

  useEffect(() => {
    if (sessionHistoryOpen) sessionHistorySearchRef.current?.focus();
  }, [sessionHistoryOpen]);

  useEffect(() => {
    if (!sessionHistoryOpen || sessionRenameTarget || sessionActionConfirmation) return;
    const closeOnPointerDown = (event: PointerEvent) => {
      const target = event.target as Node | null;
      if (
        !target ||
        sessionHistoryRef.current?.contains(target) ||
        sessionHistoryTriggerRef.current?.contains(target)
      )
        return;
      closeSessionHistory();
    };
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      event.preventDefault();
      closeSessionHistory();
    };
    document.addEventListener("pointerdown", closeOnPointerDown);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("pointerdown", closeOnPointerDown);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [sessionHistoryOpen, Boolean(sessionRenameTarget || sessionActionConfirmation)]);

  function closeSessionHistory(restoreFocus = true) {
    setSessionHistoryOpen(false);
    setSessionHistoryQuery("");
    setSessionSelectionMode(false);
    setSelectedSessionIds([]);
    if (restoreFocus) sessionHistoryTriggerRef.current?.focus();
  }

  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const newScope = providerChoiceRef.current?.key !== providerSettingsKey;
    if (providerScopeRef.current !== providerSettingsKey) {
      providerScopeRef.current = providerSettingsKey;
      setUserModels([]);
      setSelectedProvider("");
      setSelectedModel("");
      setResearchSettingsOpen(false);
    }
    setProviderLoadState("loading");
    const timer = window.setTimeout(() => {
      controller.abort();
      if (active) setProviderLoadState("error");
    }, 10_000);
    void getUserModels({ signal: controller.signal })
      .then((settings) => {
        if (!active || controller.signal.aborted) return;
        const selected = settings.selected.map((item) => ({ ...item,
          label: settings.connections?.find((connection) => connection.provider === item.provider)?.label || item.label,
        }));
        setUserModels(selected);
        const available: ProviderOption[] = Array.from(new Set(selected.map((item) => item.provider))).map((provider) => ({
          id: provider, provider, label: provider.startsWith("platform:") ? "平台提供" : selected.find((item) => item.provider === provider)?.label || settings.label,
          secretConfigured: true, models: selected.filter((item) => item.provider === provider).map((item) => item.model),
        }));
        setProviderOptions(available);
        setProviderStatus({ ok: selected.length > 0, status: selected.length ? "ready" : "not_configured" });
        let preferred: UserModel | undefined = newScope ? selected[0] : selected.find((item) => item.provider === providerChoiceRef.current?.provider && item.model === providerChoiceRef.current?.model);
        try {
          const saved = JSON.parse(window.sessionStorage.getItem(providerSettingsKey) || "null");
          const choice = newScope ? saved : providerChoiceRef.current;
          if (newScope && choice?.provider && choice?.model) preferred = selected.find((item) => item.provider === choice.provider && item.model === choice.model);
          if (newScope) setThinkingMode(["quick", "standard", "deep"].includes(saved?.thinkingMode) ? saved.thinkingMode : "standard");
          if (newScope) setAutonomyMode(["STANDARD", "BOUNDED_AUTONOMOUS"].includes(saved?.autonomyMode) ? saved.autonomyMode : "STANDARD");
        } catch {
          // Fall back to available account models when local settings cannot be read.
        }
        setSelectedProvider(preferred?.provider || "");
        setSelectedModel(preferred?.model || "");
        providerChoiceRef.current = { key: providerSettingsKey, provider: preferred?.provider || "", model: preferred?.model || "" };
        setProviderLoadState("ready");
      })
      .catch(() => {
        if (!active || controller.signal.aborted) return;
        setProviderLoadState("error");
      }).finally(() => window.clearTimeout(timer));
    return () => {
      active = false;
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [providerReloadKey, providerSettingsKey]);

  useEffect(() => {
    // Persist the draft's choices only after this exact scope has restored its
    // available models. Route changes and failed catalogue reads must not
    // overwrite another scope's saved settings with transient/default state.
    const choice = providerChoiceRef.current;
    if (providerLoadState !== "ready" || choice?.key !== providerSettingsKey
      || !selectedProvider || !selectedModel
      || choice.provider !== selectedProvider || choice.model !== selectedModel) return;
    try {
      window.sessionStorage.setItem(providerSettingsKey, JSON.stringify({
        provider: selectedProvider, model: selectedModel, thinkingMode, autonomyMode,
      }));
    } catch { /* The in-memory choice remains usable when storage is unavailable. */ }
  }, [providerLoadState, providerSettingsKey, selectedProvider, selectedModel, thinkingMode, autonomyMode]);

  useEffect(() => {
    const refresh = () => setProviderReloadKey((value) => value + 1);
    window.addEventListener("mdi:models-changed", refresh);
    return () => window.removeEventListener("mdi:models-changed", refresh);
  }, []);

  const branchChoices = useMemo(
    () => researchBranchChoices(agent2Turns, navigationTurnId, branchRootTurnId),
    [navigationTurnId, agent2Turns, branchRootTurnId],
  );
  const branchNavigation = useMemo(
    () => researchBranchNavigation(agent2Turns, navigationTurnId, branchRootTurnId),
    [navigationTurnId, agent2Turns, branchRootTurnId],
  );
  const branchDescriptors = useMemo(
    () =>
      branchNavigation?.choices.map((turn) =>
        researchBranchDescriptor(agent2Turns, turn),
      ) || [],
    [agent2Turns, branchNavigation],
  );
  const currentBranchDescriptor =
    branchDescriptors[branchNavigation?.currentIndex ?? -1] || null;
  const selectedAgent2Turn = useMemo(
    () =>
      agent2Turns.find(
        (turn) => (turn.id || turn.turn_id) === navigationTurnId,
      ) || null,
    [navigationTurnId, agent2Turns],
  );
  const selectedTurnMessageId = selectedAgent2Turn?.user_message.id || null;
  const sessionResultTurn = !agent2TurnId && !runId && !editTurnId && !fresh && !hasExplicitScientificHandoff
    ? selectedAgent2Turn : null;
  const workbenchScope = JSON.stringify([submitScope, navigationTurnId]);
  useEffect(() => {
    if (!agent2TurnId || editTurnId || !(resultTargetSnapshotId || resultTargetItemId)) return;
    setWorkbenchVisibility({ scope: workbenchScope, open: true });
    setWorkbenchView("results");
    setMobilePanel("workbench");
  }, [agent2TurnId, editTurnId, resultTargetSnapshotId, resultTargetItemId, workbenchScope, resultOpenRequest]);
  const selectedTurnMessageIds = useMemo(
    () => navigationTurnId
      ? selectedAgent2Turn?.message_ids ?? (selectedTurnMessageId ? [selectedTurnMessageId] : [])
      : undefined,
    [navigationTurnId, selectedAgent2Turn?.message_ids, selectedTurnMessageId],
  );
  const retryLineage = useMemo(
    () => retryLineageForTurn(agent2Turns, agent2TurnId, retryOfTurnId),
    [agent2TurnId, agent2Turns, retryOfTurnId],
  );
  const activeAgent2Progress = agent2ProgressForTurn(
    agent2Progress,
    agent2TurnId,
  );
  const answerDraft = useResearchAnswerStream(agent2TurnId ?? null, activeAgent2Progress?.status, () => {
    agent2ExecutionRef.current?.refresh();
  });
  const activeAgent2ContextManifest = agent2ContextManifestForTurn(
    agent2ContextManifest,
    navigationTurnId,
  );
  const composerDraftKey = useMemo(
    () =>
      researchComposerDraftKey(
        projectId,
        sessionId || session?.id,
        editTurnId ? `edit:${editTurnId}` : agent2TurnId,
      ),
    [agent2TurnId, editTurnId, projectId, session?.id, sessionId],
  );
  const currentComposerIdentity = useRef({ key: composerDraftKey, scope: submitScope });
  currentComposerIdentity.current = { key: composerDraftKey, scope: submitScope };
  const materials = useResearchMaterials(projectId, composerDraftKey);
  const [materialPickerKey, setMaterialPickerKey] = useState<string | null>(null);
  const materialPickerTrigger = useRef<HTMLElement | null>(null);
  useEffect(() => setMaterialPickerKey(null), [composerDraftKey]);
  async function loadInitialMaterials(signal: AbortSignal): Promise<ResearchMaterials> {
    if (materials.value) return materials.value;
    if (materials.error) return { items: [], selections: [] };
    const sourceTurnId = editTurnId || continueTurnId || agent2TurnId;
    if (sourceTurnId && session && (editTurnId || continueTurnId || !hasExplicitScientificHandoff)) {
      const [turn, result] = await Promise.all([
        readBranchTurn(projectId, session.id, sourceTurnId, signal),
        readBranchResult(projectId, sourceTurnId, signal),
      ]);
      const refs = result?.source_object_refs.length ? result.source_object_refs : turn.context?.scope || [];
      return { items: refs.map(ref => ({ ref })), selections: result?.scientific_selections || turn.context?.scientific_selection || [] };
    }
    if (activeViewerContext && !viewerSelectionError) {
      const ref = activeViewerContext.selection ? selectionToResearchObjectRef(activeViewerContext.selection) : {
        project_id: projectId, object_id: activeViewerContext.sourceRef.objectId,
        version_id: activeViewerContext.sourceRef.versionId, object_type: activeViewerContext.sourceRef.objectType,
        display_name: activeViewerContext.sourceRef.displayName,
      };
      const selected = activeViewerContext.selection;
      let locator = selected ? apiSemanticLocator(selected) : {};
      if (selected && ["TRAJECTORY_FRAME", "TRAJECTORY_ATOM", "VOLUMETRIC_FIELD"].includes(selected.selectionType)) {
        const projection = await getScientificViewerProjection(ref.object_id, ref.version_id, signal);
        const context = decodeWorkspaceSelectionUrl(viewerContext!.selectionToken!);
        const exact = projection.project_id === projectId && projection.object_id === ref.object_id && projection.version_id === ref.version_id;
        const bound = exact ? (selected.selectionType === "VOLUMETRIC_FIELD" ? volumetricVersionLocator(context, projection) : trajectoryVersionLocator(context, projection)) : null;
        if (!bound) throw new Error("所选科学位置无法绑定到此版本。");
        locator = bound;
      }
      return { items: [{ ref }], selections: selected ? [{ contract_version: "1.0", object_ref: ref,
        viewer_id: selected.viewerId, selection_type: selected.selectionType, display_label: selected.displayLabel,
        semantic_locator: locator,
        evidence_locator: selected.evidenceLocator ? { field_locator: selected.evidenceLocator } : undefined }] : [] };
    }
    const sourceDatasetId = datasetId || session?.datasetId || session?.dataset_id;
    if (sourceDatasetId && !datasetSelection.error && !viewerSelectionError) {
      if (!datasetSelection.selection && !sampleRef) {
        const catalog = await getDatasetResearchSources(sourceDatasetId, signal);
        if (catalog.projectId !== projectId || catalog.datasetId !== sourceDatasetId || catalog.resources.length > 64 ||
            catalog.resources.some(source => source.datasetId !== sourceDatasetId)) throw new Error("材料来源范围无法确认。");
        const items = [];
        for (const source of catalog.resources) items.push(await admitResearchMaterial(projectId, source, signal));
        return { items, selections: [] };
      }
      const resolved = await resolveExplicitDatasetScope(projectId, sourceDatasetId, datasetSelection.selection);
      signal.throwIfAborted();
      const refs = datasetResearchRefs(resolved, sampleRef);
      return { items: (refs?.objectRefs || []).map(ref => ({ ref, datasetId: sourceDatasetId })), selections: refs?.selections || [] };
    }
    return { items: [], selections: [] };
  }

  useEffect(() => {
    if (!composerDraftKey || typeof window === "undefined") return;
    let savedDraft = readComposerDraft(composerDraftKey);
    const handoff = pendingDraftHandoffRef.current;
    if (handoff?.key === composerDraftKey) {
      savedDraft = handoff.draft;
      pendingDraftHandoffRef.current = null;
    }
    composerDraftCache.current.set(composerDraftKey, savedDraft);
    restoredDraftRef.current = {
      key: composerDraftKey,
      skipPersistence: true,
    };
    setQuestion(savedDraft);
  }, [composerDraftKey]);

  useEffect(() => {
    if (!composerDraftKey || typeof window === "undefined") return;
    const restored = restoredDraftRef.current;
    if (restored?.key === composerDraftKey && restored.skipPersistence) {
      restored.skipPersistence = false;
      return;
    }
    storeComposerDraft(composerDraftKey, question);
  }, [composerDraftKey, question]);

  useEffect(() => {
    const accepted = (event: Event) => {
      const detail = (event as CustomEvent<{ key: string; scope: string; draft: string }>).detail;
      if (!detail || typeof detail.key !== "string" || typeof detail.scope !== "string" || typeof detail.draft !== "string") return;
      const current = currentComposerIdentity.current;
      if (current.key === detail.key && current.scope !== detail.scope) {
        event.preventDefault();
        return;
      }
      if (composerDraftCache.current.get(detail.key) === detail.draft) composerDraftCache.current.set(detail.key, "");
      if (current.key === detail.key && current.scope === detail.scope) {
        setQuestion(draft => draft === detail.draft ? "" : draft);
      }
    };
    window.addEventListener("mdi:research-draft-accepted", accepted);
    return () => window.removeEventListener("mdi:research-draft-accepted", accepted);
  }, []);

  useEffect(() => {
    if (!editTurnId) { seededEditDraftKeyRef.current = null; return; }
    if (!editingTurn || seededEditDraftKeyRef.current === composerDraftKey) return;
    seededEditDraftKeyRef.current = composerDraftKey;
    if (editedDraftKeyRef.current !== composerDraftKey) setQuestion((draft) => draft || editingTurn.user_message.content);
  }, [editTurnId, editingTurn, composerDraftKey]);

  useEffect(() => {
    if (!editTurnId) { editComposerFocusRef.current = null; return; }
    editComposerFocusRef.current = { key: composerDraftKey, origin: document.activeElement, handled: false };
    // A slow source read must not pull the user out of a dialog, another
    // panel, or text they have already started editing.
    const keepUserFocus = (event: Event) => {
      const request = editComposerFocusRef.current;
      if (request && event.target !== request.origin) request.handled = true;
    };
    document.addEventListener("focusin", keepUserFocus);
    document.addEventListener("pointerdown", keepUserFocus);
    return () => {
      editComposerFocusRef.current = null;
      document.removeEventListener("focusin", keepUserFocus);
      document.removeEventListener("pointerdown", keepUserFocus);
    };
  }, [composerDraftKey, editTurnId, submitLifetime]);

  useEffect(() => {
    if (!activeAgent2Progress) return;
    recordResearchFirstTruthfulProgress(
      activeAgent2Progress.turn_id,
      activeAgent2Progress.status,
    );
    const nextState = researchStateForAgent2Progress(activeAgent2Progress.status);
    if (!nextState) return;
    setState(nextState);
    if (["COMPLETED", "PARTIAL", "ANSWERED", "CANCELED"].includes(activeAgent2Progress.status)) {
      setError("");
    }
  }, [activeAgent2Progress?.status, agent2TurnId]);

  function revealActiveContextManifest() {
    const opener = document.activeElement;
    contextReturnFocusRef.current = opener instanceof HTMLElement && opener.closest("#research-timeline-panel")
      ? opener : contextManifestTriggerRef.current;
    workbenchFocusRef.current = { scope: workbenchScope, target: "context", from: opener };
    setWorkbenchVisibility({ scope: workbenchScope, open: true });
    setWorkbenchView("context");
    setMobilePanel("workbench");
  }

  function closeContextPanel() {
    if (contextManifestRef.current) contextManifestRef.current.open = false;
    workbenchFocusRef.current = { scope: workbenchScope, target: "return", from: document.activeElement };
    setWorkbenchVisibility({ scope: workbenchScope, open: false });
    setWorkbenchView("results");
    setMobilePanel("timeline");
  }

  function revealScientificWorkbench() {
    const opener = document.activeElement;
    contextReturnFocusRef.current = opener instanceof HTMLElement ? opener : contextManifestTriggerRef.current;
    workbenchFocusRef.current = { scope: workbenchScope, target: "results", from: opener };
    setWorkbenchVisibility({ scope: workbenchScope, open: true });
    setWorkbenchView("results");
    setMobilePanel("workbench");
  }

  const hasAuthoritativeTurnPresentation =
    Boolean(agent2TurnId) && hasAgent2ResultPresentation(activeAgent2Progress);

  useEffect(() => {
    // A failed/canceled run is actionable from the conversation surface:
    // retry, continue and edit controls live beside the persisted timeline.
    // Direct Turn links and returning from Edit need the same recovery surface
    // as a run-history link. React only to route/terminal-state changes so a
    // subsequent manual switch to the workbench remains respected.
    if (
      (runId || agent2TurnId) &&
      activeAgent2Progress &&
      !(hasAuthoritativeTurnPresentation && (resultTargetSnapshotId || resultTargetItemId)) &&
      ["FAILED", "CANCELED"].includes(activeAgent2Progress.status)
    ) {
      setMobilePanel("timeline");
    }
  }, [activeAgent2Progress?.turn_id, activeAgent2Progress?.status, runId, agent2TurnId, editTurnId, hasAuthoritativeTurnPresentation, resultTargetSnapshotId, resultTargetItemId]);

  async function ensureSession(owns: () => boolean) {
    if (session) return session;
    const created = await createResearchSession(
      projectId,
      question.slice(0, 48) || "新研究",
      datasetId || (runId ? scope?.dataset_id : undefined),
      pendingSessionKey,
    );
    if (!owns()) return null;
    const key = researchComposerDraftKey(projectId, created.id, agent2TurnId);
    materials.copyTo(key);
    const draft = questionInputRef.current?.value ?? question;
    pendingDraftHandoffRef.current = { key, draft };
    storeComposerDraft(key, draft);
    storeComposerDraft(composerDraftKey, "");
    try {
      window.sessionStorage.setItem(pendingSessionKey, created.id);
    } catch {
      // The in-memory handoff still retains input during session creation.
    }
    setSession(created);
    setSessions((items) => [created, ...items]);
    acknowledgeResearchSessionCreation(created.creationKey);
    if (["archived", "trashed"].includes(created.status.toLowerCase())) {
      throw new Error("原对话已归档或在回收站，请恢复该对话后再发送。输入已保留。");
    }
    return created;
  }

  async function persistResearchProjection(
    sessionId: string,
    projection: ResearchAssistantProjection,
    owns: () => boolean = () => true,
  ) {
    try {
      const message = await createResearchAssistantProjection(sessionId, projection);
      if (owns()) appendSessionMessage(message);
    } catch {
      // A narrative projection does not own execution state. The inline
      // feedback and durable Job remain authoritative if this write fails.
    }
  }

  function clearQuestionIfUnchanged(
    submittedDraft: string,
    admittedTurn?: { sessionId: string; turnId: string },
  ) {
    try {
      window.sessionStorage.removeItem(pendingSessionKey);
    } catch {
      // A confirmed request still clears its in-memory composer below.
    }
    if (!admittedTurn && pendingDraftHandoffRef.current) {
      const handoff = pendingDraftHandoffRef.current;
      if (handoff.draft === submittedDraft) handoff.draft = "";
      storeComposerDraft(handoff.key, handoff.draft);
    }
    if (admittedTurn) {
      materials.set(null);
      materials.clearKey(researchComposerDraftKey(projectId, admittedTurn.sessionId, editTurnId ? `edit:${editTurnId}` : agent2TurnId));
      // Admission navigates to a new Turn. Carry only the unsent draft, not
      // the submitted message, across that route's storage-key change.
      const currentDraft = questionInputRef.current?.value ?? submittedDraft;
      const draft = currentDraft === submittedDraft ? "" : currentDraft;
      const key = researchComposerDraftKey(
        projectId,
        admittedTurn.sessionId,
        admittedTurn.turnId,
      )!;
      pendingDraftHandoffRef.current = { key, draft };
      storeComposerDraft(key, draft);
    }
    setQuestion((currentDraft) =>
      currentDraft === submittedDraft ? "" : currentDraft,
    );
  }

  function readComposerDraft(key: string) {
    if (!composerDraftWriteFailures.current.has(key)) {
      try { return window.sessionStorage.getItem(key) || ""; } catch { /* Use this page's latest draft. */ }
    }
    return composerDraftCache.current.get(key) || "";
  }

  function storeComposerDraft(key: string, draft: string) {
    composerDraftCache.current.set(key, draft);
    try {
      if (draft) window.sessionStorage.setItem(key, draft);
      else window.sessionStorage.removeItem(key);
      composerDraftWriteFailures.current.delete(key);
    } catch {
      // Readable old storage must not override a newer draft after a failed write.
      composerDraftWriteFailures.current.add(key);
    }
  }

  function acknowledgeComposerDraft(submittedDraft: string, admittedSessionId: string) {
    const key = researchComposerDraftKey(projectId, admittedSessionId, editTurnId ? `edit:${editTurnId}` : agent2TurnId);
    const current = currentComposerIdentity.current;
    // A different source handoff may reuse this route's draft key. Its text is
    // now owned by that source choice even when the words have not changed.
    if (current.key === key && current.scope !== submitScope) return;
    const saved = readComposerDraft(key);
    if (saved !== submittedDraft) return;
    // Reception belongs to the original draft independently of navigation.
    // A remounted original composer also reconciles the confirmed receipt.
    const receipt = new CustomEvent("mdi:research-draft-accepted", {
      cancelable: true, detail: { key, scope: submitScope, draft: submittedDraft },
    });
    if (!window.dispatchEvent(receipt)) return;
    storeComposerDraft(key, "");
  }

  async function submitBranchQuestion(submittedDraft: string, submittedQuestion: string) {
    const selectedMaterials = materials.value;
    const sourceTurnId = editTurnId || continueTurnId || agent2TurnId;
    if (!sourceTurnId || !session || !canResearch || !selectedSessionIsWritable || submitInFlightRef.current || resultActionRef.current) return;
    const owner = Symbol(); resultActionRef.current = owner;
    const actionScope = resultActionScope;
    const controller = new AbortController(); branchReadRef.current = controller;
    const owns = () => resultActionRef.current === owner && currentResultActionScope.current === actionScope;
    const performanceAttemptId = beginResearchPerformanceAttempt(); scheduleResearchSubmitAcknowledgement(performanceAttemptId);
    setResultActionPending(true); setError(""); setState("planning");
    try {
      const [original, result] = editTurnId
        ? [validateBranchTurn(editingTurn!, projectId, session.id, sourceTurnId), editingResult]
        : await Promise.all([readBranchTurn(projectId, session.id, sourceTurnId, controller.signal), readBranchResult(projectId, sourceTurnId, controller.signal)]);
      if (!owns()) return;
      const resultId = result?.result_snapshot_id || result?.result_id;
      const input = agent2ContinueInput(original, submittedQuestion, editTurnId ? undefined : resultId);
      if (editTurnId && result?.source_object_refs.length) {
        input.ui_context = { ...input.ui_context, active_object_refs: result.source_object_refs, selection_refs: result.source_object_refs,
          explicit_object_refs: result.source_object_refs, scientific_selections: result.scientific_selections || original.context?.scientific_selection || [] };
      }
      if (selectedMaterials) input.ui_context = materialsContext(selectedMaterials, projectId);
      const created = await createAgent2ResearchTurn(projectId, session.id, { ...input, autonomy_mode: autonomyMode, admission_key: createAgent2AdmissionKey() });
      acknowledgeComposerDraft(submittedDraft, session.id);
      if (!owns()) return;
      bindResearchPerformanceTurn(performanceAttemptId, created.turn_id);
      clearQuestionIfUnchanged(submittedDraft, { sessionId: session.id, turnId: created.turn_id });
      setContinueTurnId(null); setMobilePanel("workbench");
      router.push(`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(created.turn_id)}`);
    } catch (reason) {
      if (owns()) { setState("failed"); setError(scientistFacingResearchRequestError(reason)); }
    } finally {
      controller.abort();
      if (owns()) { resultActionRef.current = null; branchReadRef.current = null; setResultActionPending(false); }
    }
  }

  async function submitQuestion() {
    if (materials.pending || materials.error || (!materials.value && (viewerSelectionError || datasetSelection.error))) return;
    const selectedMaterials = materials.value;
    if (!userModels.some((item) => item.provider === selectedProvider && item.model === selectedModel)) {
      setError("请先打开模型设置，探测并保存至少一个对话模型。");
      setState("failed");
      return;
    }
    if (!editBranchSubmissionAllowed(editTurnId, editingLoadState, editingTurn)) {
      setError(
        "原研究尚未读全，请重新读取后提交。草稿仍保留。",
      );
      return;
    }
    const submittedDraft = question;
    const submittedQuestion = submittedDraft.trim();
    if (!submittedQuestion) return;
    if (submitInFlightRef.current || resultActionRef.current) return;
    setWorkbenchView("results");
    if (editTurnId || continueTurnId || (agent2TurnId && !hasExplicitScientificHandoff)) {
      await submitBranchQuestion(submittedDraft, submittedQuestion); return;
    }
    const owner = Symbol();
    submitInFlightRef.current = owner;
    const owns = () => submitInFlightRef.current === owner && isCurrentSubmissionScope();
    const admissionKey = createAgent2AdmissionKey();
    const performanceAttemptId = beginResearchPerformanceAttempt();
    scheduleResearchSubmitAcknowledgement(performanceAttemptId);
    setEvents([]);
    setArtifacts([]);
    setInterpretation(null);
    setEvidence(null);
    setInterpretationStatus("idle");
    setJob(null);
    setScope(null);
    setError("");
    setState("planning");
    let activeSession: ResearchSession | null = null;
    let legacyMessageSaved = false;
  try {
      activeSession = await ensureSession(owns);
      if (!activeSession || !owns()) return;
      if (selectedMaterials) {
        const created = await createAgent2ResearchTurn(projectId, activeSession.id, {
          message: submittedQuestion, admission_key: admissionKey, autonomy_mode: autonomyMode,
          ui_context: materialsContext(selectedMaterials, projectId),
        });
        acknowledgeComposerDraft(submittedDraft, activeSession.id);
        if (!owns()) return;
        bindResearchPerformanceTurn(performanceAttemptId, created.turn_id);
        clearQuestionIfUnchanged(submittedDraft, { sessionId: activeSession.id, turnId: created.turn_id });
        setMobilePanel("workbench");
        router.push(`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(activeSession.id)}?turn=${encodeURIComponent(created.turn_id)}`);
        return;
      }
      // Explicit route handoffs and a persisted Dataset binding retain their
      // source. An unscoped question belongs to the conversation itself.
      const activeDatasetId =
        datasetId || activeSession.datasetId || activeSession.dataset_id || undefined;
      if (activeSearchResultContextId) {
        const created = await createAgent2ResearchTurn(
          projectId,
          activeSession.id,
          {
            message: submittedQuestion,
            admission_key: admissionKey,
            autonomy_mode: autonomyMode,
            ui_context: {
              active_object_refs: [],
              selection_refs: [],
              scientific_selections: [],
              explicit_object_refs: [],
              explicit_result_ids: [activeSearchResultContextId],
              explicit_finding_refs: [],
            },
          },
        );
        acknowledgeComposerDraft(submittedDraft, activeSession.id);
        if (!owns()) return;
        bindResearchPerformanceTurn(performanceAttemptId, created.turn_id);
        setSearchContextCandidateActive(false);
        clearQuestionIfUnchanged(submittedDraft, {
          sessionId: activeSession.id,
          turnId: created.turn_id,
        });
        setState("planning");
        setMobilePanel("workbench");
        router.push(
          `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(activeSession.id)}?turn=${encodeURIComponent(created.turn_id)}`,
        );
        return;
      }
      if (activeViewerContext) {
        const objectRef = activeViewerContext.selection
          ? selectionToResearchObjectRef(activeViewerContext.selection)
          : {
              object_id: activeViewerContext.sourceRef.objectId,
              version_id: activeViewerContext.sourceRef.versionId,
              project_id: activeViewerContext.sourceRef.projectId,
              object_type: activeViewerContext.sourceRef.objectType,
              display_name: activeViewerContext.sourceRef.displayName,
            };
        const scientificSelections: Agent2ScientificSelection[] = activeViewerContext.selection
          ? [
              {
                contract_version: "1.0" as const,
                object_ref: objectRef,
                viewer_id: activeViewerContext.selection.viewerId,
                selection_type: activeViewerContext.selection.selectionType,
                semantic_locator: apiSemanticLocator(
                  activeViewerContext.selection,
                ),
                display_label: activeViewerContext.selection.displayLabel,
                evidence_locator: activeViewerContext.selection.evidenceLocator
                  ? {
                      field_locator:
                        activeViewerContext.selection.evidenceLocator,
                    }
                  : null,
              },
            ]
          : [];
        if (["TRAJECTORY_FRAME", "TRAJECTORY_ATOM", "VOLUMETRIC_FIELD"].includes(activeViewerContext.selection?.selectionType || "")) {
          const isVolume = activeViewerContext.selection?.selectionType === "VOLUMETRIC_FIELD";
          const controller = new AbortController(); scientificSelectionRead.current = controller;
          try {
            const projection = await readSessionRequest(signal => getScientificViewerProjection(objectRef.object_id, objectRef.version_id, signal), controller.signal);
            if (!owns() || currentViewerSelectionKey.current !== viewerSelectionKey || controller.signal.aborted) return;
            const context = decodeWorkspaceSelectionUrl(viewerContext!.selectionToken!);
            const locator = projection.object_id === objectRef.object_id && projection.version_id === objectRef.version_id && projection.project_id === projectId ? (isVolume ? volumetricVersionLocator(context, projection) : trajectoryVersionLocator(context, projection)) : null;
            if (!locator) throw new DatasetSourceSelectionError(isVolume ? "所选体数据字段无法在此精确版本中确认。请返回数据重新选择；问题已保留，尚未提交分析。" : "所选轨迹位置无法在此精确版本中确认。请返回数据重新选择；问题已保留，尚未提交分析。");
            scientificSelections[0].semantic_locator = locator; scientificSelections[0].evidence_locator = locator;
          } catch (reason) {
            if (!owns() || controller.signal.aborted || currentViewerSelectionKey.current !== viewerSelectionKey) return;
            if (reason instanceof DatasetSourceSelectionError) throw reason;
            throw new DatasetSourceSelectionError(isVolume ? "暂时无法读取所选体数据的精确版本，请重试。问题已保留，尚未提交分析。" : "暂时无法读取所选轨迹的精确版本，请重试。问题已保留，尚未提交分析。");
          } finally { controller.abort(); if (scientificSelectionRead.current === controller) scientificSelectionRead.current = null; }
        }
        const created = await createAgent2ResearchTurn(
          projectId,
          activeSession.id,
          {
            message: submittedQuestion,
            admission_key: admissionKey,
            autonomy_mode: autonomyMode,
            // A deep-linked Viewer context is already an explicit, exact object/version
            // selection. Preserve it in the resolver's explicit channel as well as the
            // bounded active/selection channels so ambiguous project history cannot
            // downgrade a targeted research request to clarification.
            ui_context: {
              active_object_refs: [objectRef],
              selection_refs: activeViewerContext.selection ? [objectRef] : [],
              scientific_selections: scientificSelections,
              explicit_object_refs: [objectRef],
              explicit_result_ids: [],
              explicit_finding_refs: [],
            },
          },
        );
        acknowledgeComposerDraft(submittedDraft, activeSession.id);
        if (!owns()) return;
        bindResearchPerformanceTurn(performanceAttemptId, created.turn_id);
        if (contextCandidateFromSearch) setSearchContextCandidateActive(false);
        clearQuestionIfUnchanged(submittedDraft, {
          sessionId: activeSession.id,
          turnId: created.turn_id,
        });
        setState("planning");
        setMobilePanel("workbench");
        router.push(
          `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(activeSession.id)}?turn=${encodeURIComponent(created.turn_id)}`,
        );
        return;
      }
      if (!activeDatasetId) {
        const created = await createAgent2ResearchTurn(projectId, activeSession.id, {
          message: submittedQuestion, admission_key: admissionKey, autonomy_mode: autonomyMode,
          ui_context: {
            active_object_refs: [], selection_refs: [], explicit_object_refs: [],
            scientific_selections: [], explicit_result_ids: [], explicit_finding_refs: [],
          },
        });
        acknowledgeComposerDraft(submittedDraft, activeSession.id);
        if (!owns()) return;
        bindResearchPerformanceTurn(performanceAttemptId, created.turn_id);
        clearQuestionIfUnchanged(submittedDraft, { sessionId: activeSession.id, turnId: created.turn_id });
        setMobilePanel("timeline");
        router.push(`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(activeSession.id)}?turn=${encodeURIComponent(created.turn_id)}`);
        return;
      }
      const nextScope = await resolveExplicitDatasetScope(projectId, activeDatasetId, datasetSelection.selection);
      if (!owns()) return;
      setScope(nextScope);
      const activeSessionId = activeSession.id;
      const persistLegacyUserMessage = async () => {
        const savedMessage = await createResearchMessage(
          activeSessionId,
          submittedQuestion,
          activeDatasetId,
        );
        legacyMessageSaved = true;
        if (owns()) setSession((current) =>
          current
            ? {
                ...current,
                messages: [...(current.messages || []), savedMessage],
              }
            : current,
        );
      };
      if (!nextScope.dataset_id) throw new Error("没有找到可用于分析的数据");
      const resolvedDatasetId = nextScope.dataset_id;
      const explicitDataset = datasetResearchRefs(
        nextScope,
        sampleRef ||
          submittedQuestion.match(/\bmat-[A-Za-z0-9][A-Za-z0-9_.-]*\b/i)?.[0],
      );
      if (explicitDataset) {
        const created = await createAgent2ResearchTurn(
          projectId,
          activeSession.id,
          {
            message: submittedQuestion,
            admission_key: admissionKey,
            autonomy_mode: autonomyMode,
            ui_context: {
              active_object_refs: explicitDataset.objectRefs,
              selection_refs: explicitDataset.selections.length
                ? [explicitDataset.selections[0].object_ref]
                : [],
              scientific_selections: explicitDataset.selections,
              explicit_object_refs: explicitDataset.objectRefs,
              explicit_result_ids: [],
              explicit_finding_refs: [],
            },
          },
        );
        acknowledgeComposerDraft(submittedDraft, activeSession.id);
        if (!owns()) return;
        bindResearchPerformanceTurn(performanceAttemptId, created.turn_id);
        clearQuestionIfUnchanged(submittedDraft, {
          sessionId: activeSession.id,
          turnId: created.turn_id,
        });
        setState("planning");
        setMobilePanel("workbench");
        router.push(
          `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(activeSession.id)}?turn=${encodeURIComponent(created.turn_id)}`,
        );
        return;
      }
      await persistLegacyUserMessage();
      const nextJob = await createPlannerJob({
        userPrompt: submittedQuestion,
        projectId,
        datasetId: resolvedDatasetId,
        profileId: nextScope.profile_id,
        enqueue: true,
        provider: selectedProvider || undefined,
        model: selectedModel || undefined,
        thinkingMode,
        intentSchemaVersion: "1.0",
        researchSessionId: activeSession.id,
      });
      if (owns()) setJob(nextJob);
      if (!nextJob.ok || !nextJob.job_id) {
        if (owns()) setState(
          nextJob.capability_outcome === "NEEDS_CLARIFICATION"
            ? "capability-clarification"
            : "failed",
        );
        if (owns()) setError(plannerFailureMessage(nextJob));
        void persistResearchProjection(
          activeSession.id,
          {
            phase: "failed",
            datasetName: nextScope.dataset_name,
            datasetId: nextScope.dataset_id,
            failureCode: plannerFailureCode(nextJob),
          },
          isCurrentSubmissionScope,
        );
        return;
      }
      // Begin tracking the admitted Job before requesting optional narration.
      // A slow provider must not delay recovery links or terminal feedback.
      acknowledgeComposerDraft(submittedDraft, activeSession.id);
      if (owns()) {
        setState("running");
        persistRunLink(nextJob.job_id);
        clearQuestionIfUnchanged(submittedDraft);
        setMobilePanel("workbench");
      }
      void persistResearchProjection(activeSession.id, {
        phase: "pre_run",
        datasetName: nextScope.dataset_name,
        datasetId: resolvedDatasetId,
        runId: nextJob.job_id,
        question: submittedQuestion,
        provider: selectedProvider || undefined,
        model: selectedModel || undefined,
        thinkingMode,
        useProvider: true,
      }, isCurrentSubmissionScope);
    } catch (reason) {
      if (owns()) {
        setState("failed");
        setError(scientistFacingResearchRequestError(reason));
      }
      if (activeSession && legacyMessageSaved && !(reason instanceof Agent2ReadError) && !(reason instanceof Agent2AdmissionUnconfirmedError) && !(reason instanceof DatasetSourceSelectionError)) {
        void persistResearchProjection(activeSession.id, {
          phase: "failed",
          failureCode: "RESEARCH_SERVICE_UNAVAILABLE",
        }, isCurrentSubmissionScope);
      }
    } finally {
      if (owns()) submitInFlightRef.current = null;
    }
  }

  function persistRunLink(jobId: string | undefined) {
    if (!jobId || typeof window === "undefined") return;
    const url = new URL(window.location.href);
    url.searchParams.set("run", jobId);
    window.history.replaceState(window.history.state, "", url.toString());
  }

  function trySuggestedQuestion(nextQuestion: string) {
    setQuestion(nextQuestion);
    setState("idle");
    setError("");
    setJob(null);
    setMobilePanel("timeline");
    window.requestAnimationFrame(() => questionInputRef.current?.focus());
  }

  function restoreRunQuestion() {
    const originalQuestion = history?.analyses.find((item) => item.jobId === job?.job_id)?.userQuestion?.trim() || job?.plan?.goal?.trim();
    setQuestion((draft) => draft.trim() ? draft : originalQuestion || "");
    setMobilePanel("timeline");
    requestAnimationFrame(() => {
      questionInputRef.current?.focus();
      questionInputRef.current?.scrollIntoView?.({ block: "nearest" });
    });
  }

  function rememberSessionActionFocus() {
    sessionLifecycleFocusRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  }
  function restoreSessionActionFocus() {
    const origin = sessionLifecycleFocusRef.current;
    window.requestAnimationFrame(() => {
      if (origin?.isConnected) origin.focus();
      else sessionHistoryFilterRefs.current.get(sessionHistoryStatus)?.focus();
    });
  }
  async function refreshSessionDirectory() {
    if (sessionOperation.pending || sessionDirectoryReadRef.current) return;
    const controller = new AbortController(); sessionDirectoryReadRef.current = controller;
    setSessionDirectoryReading(true); setSessionDirectoryError("");
    try {
      const items = validateSessionDirectory(await readSessionRequest((signal) => listResearchSessions(projectId, signal), controller.signal), projectId);
      if (controller.signal.aborted || sessionDirectoryReadRef.current !== controller) return;
      setSessions(items);
      setSession((current) => {
        const saved = current && items.find((item) => item.id === current.id);
        return current && saved ? { ...current, ...saved } : current;
      });
      sessionOperation.reconciled();
    } catch {
      if (!controller.signal.aborted) setSessionDirectoryError("研究记录暂时无法更新，已读取的记录和输入仍然保留。");
    } finally {
      if (sessionDirectoryReadRef.current === controller) { sessionDirectoryReadRef.current = null; setSessionDirectoryReading(false); }
    }
  }
  function acceptSessionUpdate(updated: ResearchSession) {
    setSessions((items) => items.map((item) => item.id === updated.id ? { ...item, ...updated } : item)
      .sort((left, right) => Number(Boolean(right.pinned)) - Number(Boolean(left.pinned))));
    setSession((current) => current?.id === updated.id ? { ...current, ...updated } : current);
  }
  async function updateSessionRecord(item: ResearchSession, changes: { title?: string; pinned?: boolean; lifecycle?: "ACTIVE" | "ARCHIVED" | "TRASHED" }, label: string) {
    if (!canResearch || sessionOperation.locked() || sessionDirectoryReading) return false;
    setSessionLifecycleBusy(item.id); setSessionLifecycleNotice("");
    const saved = await sessionOperation.run(label, (signal) => updateResearchSession(item.id, changes, signal), (updated) => {
      validateResearchSession(updated, projectId, item.id);
      if ((changes.title !== undefined && updated.title !== changes.title) ||
          (changes.pinned !== undefined && Boolean(updated.pinned) !== changes.pinned) ||
          (changes.lifecycle && updated.status.toUpperCase() !== changes.lifecycle)) throw new Error("Session update mismatch");
      acceptSessionUpdate(updated);
    });
    setSessionLifecycleBusy(null);
    return saved;
  }
  function sessionActionLabel(action: ResearchSessionBulkAction) {
    return ({ ARCHIVE: "归档", TRASH: "移入回收站", RESTORE: "恢复", PIN: "置顶", UNPIN: "取消置顶" })[action];
  }
  async function executeSessionAction(target: { items: ResearchSession[]; action: ResearchSessionBulkAction; bulk: boolean }) {
    if (!canResearch || !target.items.length || sessionOperation.locked() || sessionDirectoryReading) return;
    const label = sessionActionLabel(target.action);
    let saved = false;
    if (!target.bulk) {
      const lifecycle = target.action === "ARCHIVE" ? "ARCHIVED" : target.action === "TRASH" ? "TRASHED" : "ACTIVE";
      saved = await updateSessionRecord(target.items[0], { lifecycle }, `${label}研究记录`);
      if (saved) setSessionLifecycleNotice(`“${target.items[0].title}”已${label}。`);
    } else {
      setSessionBulkBusy(true); setSessionLifecycleNotice("");
      saved = await sessionOperation.run(`${label}研究记录`, async (signal) => {
        for (let offset = 0; offset < target.items.length; offset += 100) {
          signal.throwIfAborted();
          const ids = target.items.slice(offset, offset + 100).map((item) => item.id);
          const result = await bulkUpdateResearchSessions(projectId, ids, target.action, signal);
          signal.throwIfAborted();
          if (result.action !== target.action || result.count !== ids.length || result.sessionIds.length !== ids.length || new Set(result.sessionIds).size !== ids.length || result.sessionIds.some((id) => !ids.includes(id))) throw new Error("Session bulk response mismatch");
          const update = (item: ResearchSession) => !ids.includes(item.id) ? item : {
            ...item,
            ...(["PIN", "UNPIN"].includes(target.action) ? { pinned: target.action === "PIN" } : { status: target.action === "ARCHIVE" ? "archived" : target.action === "TRASH" ? "trashed" : "active" }),
          };
          setSessions((items) => items.map(update).sort((left, right) => Number(Boolean(right.pinned)) - Number(Boolean(left.pinned))));
          setSession((current) => current ? update(current) : current);
          setSelectedSessionIds((current) => current.filter((id) => !ids.includes(id)));
          setSessionActionConfirmation((current) => current ? { ...current, items: current.items.filter((item) => !ids.includes(item.id)) } : current);
        }
      }, () => {});
      setSessionBulkBusy(false);
    }
    if (saved) { setSessionActionConfirmation(null); restoreSessionActionFocus(); }
  }
  async function changeSessionLifecycle(item: ResearchSession, next: "ACTIVE" | "ARCHIVED" | "TRASHED") {
    if (sessionOperation.locked() || sessionDirectoryReading) return;
    rememberSessionActionFocus();
    const target = { items: [item], action: (next === "ACTIVE" ? "RESTORE" : next === "ARCHIVED" ? "ARCHIVE" : "TRASH") as ResearchSessionBulkAction, bulk: false };
    if (next === "ACTIVE") await executeSessionAction(target);
    else setSessionActionConfirmation(target);
  }
  async function toggleSessionPinned(item: ResearchSession) {
    rememberSessionActionFocus();
    await updateSessionRecord(item, { pinned: !item.pinned }, item.pinned ? "取消置顶" : "置顶研究记录");
  }
  async function applySessionBulkAction(action: ResearchSessionBulkAction) {
    if (sessionOperation.locked() || sessionDirectoryReading) return;
    const items = filteredSessions.filter((item) => selectedSessionIds.includes(item.id));
    if (!items.length) return;
    rememberSessionActionFocus();
    const target = { items, action, bulk: true };
    if (["ARCHIVE", "TRASH"].includes(action)) setSessionActionConfirmation(target);
    else await executeSessionAction(target);
  }
  function openSessionRename(item: ResearchSession) {
    if (sessionOperation.locked() || sessionDirectoryReading) return;
    rememberSessionActionFocus();
    setSessionRenameTarget(item); setSessionRenameValue(item.title);
  }
  function closeSessionRename() {
    sessionOperation.dismiss(); setSessionRenameTarget(null);
  }
  async function renameSession() {
    if (!sessionRenameTarget || !sessionRenameValue.trim()) return;
    if (await updateSessionRecord(sessionRenameTarget, { title: sessionRenameValue.trim() }, "重命名")) {
      setSessionRenameTarget(null); setSessionRenameValue("");
    }
  }
  const sessionManagementFeedback = <>
    {sessionOperation.error || sessionDirectoryError ? <div className="research-session-operation-error" role="alert">
      {sessionOperation.error ? <p>{sessionOperation.error}</p> : null}
      {sessionDirectoryError ? <p>{sessionDirectoryError}</p> : null}
      {sessionOperation.uncertain || sessionDirectoryError ? <button type="button" className="product-secondary-action" disabled={sessionDirectoryReading || sessionOperation.pending} onClick={() => void refreshSessionDirectory()}>{sessionDirectoryReading ? "正在读取…" : "重新读取研究记录"}</button> : null}
    </div> : null}
  </>;

  function handleSessionHistoryFilterKey(
    event: ReactKeyboardEvent<HTMLButtonElement>,
    current: "current" | "archived" | "trashed",
  ) {
    const filters = ["current", "archived", "trashed"] as const;
    const currentIndex = filters.indexOf(current);
    let next: (typeof filters)[number] | null = null;
    if (event.key === "Home") next = filters[0];
    else if (event.key === "End") next = filters[filters.length - 1];
    else if (event.key === "ArrowLeft" || event.key === "ArrowUp")
      next = filters[(currentIndex - 1 + filters.length) % filters.length];
    else if (event.key === "ArrowRight" || event.key === "ArrowDown")
      next = filters[(currentIndex + 1) % filters.length];
    if (!next) return;
    event.preventDefault();
    setSessionHistoryStatus(next);
    setSelectedSessionIds([]);
    sessionHistoryFilterRefs.current.get(next)?.focus();
  }

  function handleMobileTabKey(
    event: ReactKeyboardEvent<HTMLButtonElement>,
    current: "timeline" | "workbench",
  ) {
    let next: "timeline" | "workbench" | null = null;
    if (
      event.key === "ArrowLeft" ||
      event.key === "ArrowUp" ||
      event.key === "Home"
    )
      next = "timeline";
    if (
      event.key === "ArrowRight" ||
      event.key === "ArrowDown" ||
      event.key === "End"
    )
      next = "workbench";
    if (!next) return;
    event.preventDefault();
    if (next === "workbench") setWorkbenchVisibility({ scope: workbenchScope, open: true });
    if (next !== current) setMobilePanel(next);
    (next === "timeline"
      ? mobileTimelineTabRef
      : mobileWorkbenchTabRef
    ).current?.focus();
  }

  function appendSessionMessage(message: ResearchMessage) {
    setSession((current) =>
      current &&
      current.id === message.session_id &&
      !(current.messages || []).some((item) => item.id === message.id)
        ? { ...current, messages: [...(current.messages || []), message] }
        : current,
    );
  }

  const [legacyTerminalJob, setLegacyTerminalJob] = useState<{ jobId: string; detail: PlannerJobDetail } | null>(null);
  const legacyJobContext = useRef({ job, scope, session, interpretation, history });
  legacyJobContext.current = { job, scope, session, interpretation, history };
  useEffect(() => {
    const jobId = job?.job_id;
    // A ResearchTurn owns its own progress; only watch an admitted legacy job.
    if (agent2TurnId || !jobId || (!["planning", "running"].includes(state) && legacyTerminalJob?.jobId !== jobId)) return;
    return watchLegacyJob(jobId, projectId, {
      events: (value) => setEvents((items) => mergeJobEvents(items, value)),
      artifacts: (value) => { setArtifacts((items) => mergeArtifacts(items, value)); setRunResolutionState("settled"); },
      failure: (part, failed) => {
        setRunReadFailures((items) => failed ? items.includes(part) ? items : [...items, part] : items.filter((item) => item !== part));
        if (part === "科学结果" && failed) setRunResolutionState("settled");
        if (!runId) setRunReadPending(false);
      },
      detail: (detail) => {
        setState(researchRunState(detail.status));
        if (legacyJobIsTerminal(detail.status)) setLegacyTerminalJob({ jobId, detail });
      },
    });
    // Changing the displayed state or loading a plan must not cancel final reads.
  }, [agent2TurnId, job?.job_id, projectId, runId, sessionId, reloadKey]);

  useEffect(() => {
    const context = legacyJobContext.current;
    const jobId = context.job?.job_id;
    if (agent2TurnId || !jobId || legacyTerminalJob?.jobId !== jobId || sessionLoadState !== "ready") return;
    const owner = context.session;
    const writableOwner = owner && (!sessionId || owner.id === sessionId) &&
      (owner.project_id || owner.projectId) === projectId && projectRoleAllows(context.history?.project.role, "research") &&
      String(context.history?.project.status || "active").toLowerCase() === "active" &&
      String(owner.status || "active").toLowerCase() === "active" &&
      (!runId || researchSessionReferencesRun(owner, jobId) ||
        context.history?.analyses.some((item) => item.jobId === jobId && item.researchSessionId === owner.id));
    if (!writableOwner || !owner) return;
    const status = String(legacyTerminalJob.detail.status).toLowerCase();
    if (["cancelled", "canceled"].includes(status)) return;
    const controller = new AbortController();
    const fail = (part: string) => {
      if (!controller.signal.aborted) setRunReadFailures((items) => items.includes(part) ? items : [...items, part]);
    };
    const projectMessage = async (phase: "post_run" | "failed") => {
      const ref = phase === "failed" ? failedRunMessageRef : postRunMessageRef;
      if (ref.current === jobId || researchSessionReferencesRun(owner, jobId, phase)) return;
      ref.current = jobId;
      try {
        const message = await readSessionRequest(() => createResearchAssistantProjection(owner.id, {
          phase, datasetName: context.scope?.dataset_name, datasetId: context.scope?.dataset_id,
          runId: jobId, ...(phase === "failed" ? { failureCode: "JOB_FAILED" } : {}),
        }), controller.signal);
        if (!controller.signal.aborted) {
          appendSessionMessage(message);
          setRunReadFailures((items) => items.filter((item) => item !== "对话结果"));
        }
      } catch { ref.current = null; fail("对话结果"); }
    };
    if (status === "failed") {
      void projectMessage("failed").finally(() => { if (!controller.signal.aborted) setRunReadPending(false); });
    } else {
      const planHash = legacyTerminalJob.detail.planHash || context.job?.plan_hash;
      if (planHash) {
        setInterpretationStatus("loading");
        void createScientificInterpretation(jobId, planHash, controller.signal).then((result) => {
          if (controller.signal.aborted) return;
          const saved = result.interpretation || null;
          setInterpretation(saved);
          setInterpretationStatus(saved ? saved.completeness === "COMPLETE" ? "ready" : "limited" : "error");
          if (!saved) { fail("结果解读"); return; }
          setRunReadFailures((items) => items.filter((item) => item !== "结果解读"));
          setEvidence((current) => current?.interpretationId === saved.interpretationId ? current : null);
          void readSessionRequest((signal) => getPlannerInterpretationEvidence(saved.interpretationId, { signal }), controller.signal).then((value) => {
            if (controller.signal.aborted) return;
            if (value.interpretationId !== saved.interpretationId) throw new Error("Interpretation evidence mismatch");
            setEvidence(value);
            setRunReadFailures((items) => items.filter((item) => item !== "解读依据"));
          }).catch(() => fail("解读依据"));
          void projectMessage("post_run");
        }).catch(() => {
          if (!controller.signal.aborted) { setInterpretationStatus("error"); fail("结果解读"); }
        }).finally(() => { if (!controller.signal.aborted) setRunReadPending(false); });
      }
    }
    return () => controller.abort();
  }, [legacyTerminalJob, agent2TurnId, job?.job_id, projectId, runId, sessionId, session?.id, session?.status, sessionLoadState, history?.project.role, history?.project.status, reloadKey]);

  const messages = dedupeResearchTimelineMessages(
    (session?.messages || []).filter(researchMessageVisibleInTimeline),
  );
  const conversationWindow = useMemo(
    () =>
      researchMessageWindow(
        messages,
        selectedTurnMessageId,
        showFullConversation,
        10,
        conversationWindowStart,
        selectedTurnMessageIds,
      ),
    [messages, selectedTurnMessageId, selectedTurnMessageIds, showFullConversation, conversationWindowStart],
  );
  // Session messages and the branch directory refresh independently. Retain
  // the saved stream completion until its replacement is actually visible.
  const showAnswerDraft = Boolean(answerDraft?.text) && !conversationWindow.visible.some(message =>
    message.id === answerDraft?.messageId || (message.role === "assistant" &&
      message.payload?.turnId === agent2TurnId && message.payload?.messageKind === "ASSISTANT_FINAL"),
  );
  const answerStreaming = showAnswerDraft && answerDraft?.phase !== "completed";
  const completedAnswerVisible = Boolean(
    (showAnswerDraft && answerDraft?.phase === "completed") ||
    (agent2TurnId && conversationWindow.visible.some(message =>
      message.role === "assistant" && message.content.trim() &&
      message.payload?.turnId === agent2TurnId && message.payload?.messageKind === "ASSISTANT_FINAL")),
  );
  const conversationReady = Boolean(answerDraft?.text) ||
    ["ANSWERED", "NEEDS_CLARIFICATION", "UNSUPPORTED", "PLAN_REJECTED"].includes(activeAgent2Progress?.status || "");
  const revealedConversation = useRef({ turnId: agent2TurnId, revealed: false });
  useEffect(() => {
    if (revealedConversation.current.turnId !== agent2TurnId) {
      revealedConversation.current = { turnId: agent2TurnId, revealed: false };
    }
    // A saved answer or clarification also belongs in the conversation on a
    // narrow screen. Reveal once per Turn; completion and reconnects must not
    // override a later manual visit to the workbench.
    if (agent2TurnId && conversationReady && !(resultTargetSnapshotId || resultTargetItemId) && !revealedConversation.current.revealed) {
      revealedConversation.current.revealed = true;
      setMobilePanel("timeline");
    }
  }, [agent2TurnId, conversationReady, resultTargetSnapshotId, resultTargetItemId]);
  const savedTurnAnswer = agent2TurnId ? conversationWindow.visible.find(message =>
    message.role === "assistant" && message.payload?.turnId === agent2TurnId &&
    message.payload?.messageKind === "ASSISTANT_FINAL") : undefined;
  const conversationScroll = useConversationScroll({
    scope: JSON.stringify([projectId, sessionId, agent2TurnId || runId || navigationTurnId]),
    viewportRef: conversationHistoryRef,
    focusMessageId: selectedTurnMessageId,
    answerId: showAnswerDraft ? answerDraft?.responseId : savedTurnAnswer?.id,
    answerText: showAnswerDraft ? answerDraft?.text : savedTurnAnswer?.content,
    streaming: answerStreaming,
    answerPending: ["RECEIVED", "RESOLVING_CONTEXT", "ORCHESTRATING", "INTERPRETING"].includes(activeAgent2Progress?.status || ""),
    ready: pageLoadState === "ready",
  });
  const hiddenConversationCount =
    conversationWindow.hiddenBefore + conversationWindow.hiddenAfter;

  useEffect(() => {
    setShowFullConversation(false);
    setConversationWindowStart(0);
  }, [session?.id, agent2TurnId]);
  const projectLifecycle = String(
    history?.project?.status || "active",
  ).toLowerCase();
  const canResearch =
    projectRoleAllows(history?.project?.role, "research") &&
    projectLifecycle === "active";
  const selectedSessionLifecycle = String(
    session?.status || "active",
  ).toLowerCase();
  const selectedSessionIsArchived =
    Boolean(session) && selectedSessionLifecycle === "archived";
  const selectedSessionIsTrashed =
    Boolean(session) && selectedSessionLifecycle === "trashed";
  const selectedSessionIsWritable =
    sessionLoadState === "ready" &&
    (!agent2TurnId || Boolean(session)) &&
    (!session || selectedSessionLifecycle === "active");
  useEffect(() => {
    const request = editComposerFocusRef.current;
    if (!editTurnId || !request || request.key !== composerDraftKey || request.handled ||
        editingLoadState !== "ready" || !canResearch || !selectedSessionIsWritable ||
        !history || mobilePanel !== "timeline") return;
    const frame = window.requestAnimationFrame(() => {
      if (editComposerFocusRef.current !== request || request.handled || currentSubmitScope.current !== submitLifetime) return;
      request.handled = true;
      const input = questionInputRef.current;
      const focused = document.activeElement;
      if (!input || focused === input) return;
      // A successful retry removes its button, returning focus to the body.
      if (focused !== request.origin && !(focused === document.body && !request.origin?.isConnected)) return;
      input.focus({ preventScroll: true });
      input.scrollIntoView?.({ block: "nearest" });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [composerDraftKey, editTurnId, editingLoadState, canResearch, selectedSessionIsWritable, history, mobilePanel, submitLifetime]);
  const memorySessionId = session && (session.projectId || session.project_id) === projectId && (!sessionId || session.id === sessionId) ? session.id : undefined;
  const sessionContext = useSessionMemory(projectId, memorySessionId, canResearch && selectedSessionIsWritable);
  const sessionMemory = sessionContext.memory;

  useEffect(() => {
    if (
      !retryRequested ||
      !agent2TurnId ||
      !session?.id ||
      !selectedSessionIsWritable ||
      !canResearch ||
      providerLoadState !== "ready" ||
      !userModels.some((item) => item.provider === selectedProvider && item.model === selectedModel) ||
      !activeAgent2Progress ||
      !["FAILED", "CANCELED"].includes(activeAgent2Progress.status) ||
      autoRetryTurnRef.current === agent2TurnId
    ) {
      return;
    }
    autoRetryTurnRef.current = agent2TurnId;
    void retryAgent2Turn();
  }, [
    activeAgent2Progress?.status,
    agent2TurnId,
    retryRequested,
    selectedSessionIsWritable,
    canResearch, providerLoadState, selectedProvider, selectedModel, userModels,
    session?.id,
  ]);
  const starterDataset = history?.datasets.find((dataset) => dataset.datasetId === datasetId);
  const starterPrompts = researchStarterPrompts(
    history && starterDataset ? { ...history, datasets: [starterDataset] } : history,
  ).map((prompt) => datasetId && prompt.id === "project-overview"
    ? { ...prompt, question: "概览所选数据与可用分析" }
    : prompt);
  const showResearchStarter =
    sessionLoadState === "ready" &&
    selectedSessionIsWritable &&
    state === "idle" &&
    !runId &&
    !job &&
    messages.length === 0;
  const hasScientificWorkbenchContent = researchWorkbenchContentAvailable({
    job,
    artifacts,
    interpretation,
    evidence,
    events,
    agent2Progress: activeAgent2Progress || (sessionResultTurn?.turn_id === sessionResultProgress?.turn_id ? sessionResultProgress : null),
  });
  const workbenchOpen = workbenchVisibility?.scope === workbenchScope
    ? workbenchVisibility.open
    : hasScientificWorkbenchContent || workbenchView === "context";
  useLayoutEffect(() => {
    const request = workbenchFocusRef.current;
    workbenchFocusRef.current = null;
    if (!request || request.scope !== workbenchScope) return;
    // The destination must be visible before focusing it, including on mobile.
    // Finish in this commit so a delayed frame cannot steal a later interaction.
    if (document.activeElement !== request.from && document.activeElement !== document.body) return;
    if (request.target === "return") {
      const opener = contextReturnFocusRef.current;
      (opener?.isConnected ? opener : contextManifestTriggerRef.current)?.focus();
    } else if (request.target === "results") {
      document.getElementById("research-results-panel")?.focus();
    } else {
      const disclosure = contextManifestRef.current;
      if (!disclosure) {
        contextPanelRef.current?.focus();
        return;
      }
      disclosure.open = true;
      disclosure.scrollIntoView?.({ block: "nearest", behavior: "auto" });
      disclosure.querySelector<HTMLElement>("summary")?.focus();
    }
  }, [workbenchScope, workbenchVisibility, workbenchOpen, workbenchView, mobilePanel]);
  const researchLayoutMode = hasScientificWorkbenchContent
    ? "scientific-workbench"
    : "asking";
  const waitingForTurnProgress = Boolean(agent2TurnId && !activeAgent2Progress);
  useLayoutEffect(() => {
    const workbench = workbenchRef.current;
    if (!workbench) return;
    // Measure after loading has mounted the workspace, and whenever the shell
    // changes size. Keep the splitter's value and the rendered columns aligned.
    const fitConversation = () => {
      const width = workbench.getBoundingClientRect().width || 1280;
      const maximum = Math.round(Math.min(760, Math.max(320, width - 487)));
      setConversationMaxWidth(maximum);
      setConversationWidth((previous) => {
        // A branch read temporarily has no progress. Preserve its current split
        // until the selected Turn is known; still clamp it when the canvas shrinks.
        const target = conversationPreferredWidthRef.current ?? (waitingForTurnProgress
          ? previous
          : defaultResearchConversationWidth(hasScientificWorkbenchContent, width));
        return Math.round(Math.min(maximum, Math.max(320, target)));
      });
    };
    fitConversation();
    const observer = typeof ResizeObserver === "undefined"
      ? null
      : new ResizeObserver(fitConversation);
    observer?.observe(workbench);
    window.addEventListener("resize", fitConversation);
    return () => {
      observer?.disconnect();
      window.removeEventListener("resize", fitConversation);
    };
  }, [hasScientificWorkbenchContent, waitingForTurnProgress, pageLoadState]);
  const normalizedSessionQuery = sessionHistoryQuery
    .trim()
    .toLocaleLowerCase("zh-CN");
  const sessionStatusCounts = sessions.reduce(
    (counts, item) => {
      const status = String(item.status || "active").toLowerCase();
      if (status === "trashed") counts.trashed += 1;
      else if (status === "archived") counts.archived += 1;
      else counts.current += 1;
      return counts;
    },
    { current: 0, archived: 0, trashed: 0 },
  );
  const filteredSessions = sessions.filter((item) => {
    const status = String(item.status || "active").toLowerCase();
    const inStatus =
      sessionHistoryStatus === "trashed"
        ? status === "trashed"
        : sessionHistoryStatus === "archived"
          ? status === "archived"
          : !["archived", "trashed"].includes(status);
    return (
      inStatus &&
      (!normalizedSessionQuery ||
        item.title.toLocaleLowerCase("zh-CN").includes(normalizedSessionQuery))
    );
  });
  useEffect(() => {
    const visible = new Set(filteredSessions.map((item) => item.id));
    setSelectedSessionIds((current) => current.some((id) => !visible.has(id)) ? current.filter((id) => visible.has(id)) : current);
  }, [sessions, normalizedSessionQuery, sessionHistoryStatus]);
  const branchVersionNavigation = branchChoices.length > 1 &&
            branchNavigation &&
            session?.id ? (
              <nav
                ref={branchNavigationRef}
                className="research-branch-switcher conversation-branch-switcher"
                aria-label="研究分支"
              >
                {branchNavigation.previous ? (
                  <Link
                    className="research-branch-step"
                    scroll={false}
                    aria-label={`上一个研究分支：${researchBranchDescriptor(agent2Turns, branchNavigation.previous).title}`}
                    href={`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(branchNavigation.previous.id || branchNavigation.previous.turn_id)}&branchRoot=${encodeURIComponent(branchNavigation.rootId)}`}
                  >
                    ‹
                  </Link>
                ) : (
                  <span
                    className="research-branch-step disabled"
                    aria-hidden="true"
                  >
                    ‹
                  </span>
                )}
                <details className="research-branch-list" onToggle={(event) => {
                  const disclosure = event.currentTarget;
                  if (event.target !== disclosure || !disclosure.open) return;
                  const scroller = disclosure.closest<HTMLElement>(".conversation-history");
                  const summary = disclosure.querySelector<HTMLElement>(":scope > summary");
                  const list = disclosure.querySelector<HTMLElement>(":scope > ol");
                  if (!scroller?.clientHeight || !summary || !list) return;
                  const viewportTop = scroller.getBoundingClientRect().top + scroller.clientTop;
                  const summaryTop = summary.getBoundingClientRect().top;
                  // Keep the trigger visible even when a long list exceeds the pane.
                  const listBottom = Math.min(list.getBoundingClientRect().bottom, summaryTop + scroller.clientHeight);
                  const offset = summaryTop < viewportTop
                    ? summaryTop - viewportTop
                    : Math.max(0, listBottom - viewportTop - scroller.clientHeight);
                  scroller.scrollTop += offset;
                }} onKeyDown={(event) => {
                  if (event.key === "Escape") {
                    event.preventDefault(); event.currentTarget.open = false;
                    event.currentTarget.querySelector<HTMLElement>("summary")?.focus();
                  }
                }} onBlur={(event) => {
                  if (event.relatedTarget && !event.currentTarget.contains(event.relatedTarget as Node)) event.currentTarget.open = false;
                }}>
                  <summary aria-label={`查看全部 ${branchDescriptors.length} 个分支`}>{branchNavigation.currentIndex + 1} / {branchNavigation.choices.length} <span aria-hidden="true">⌄</span></summary>
                  <ol>
                    {branchDescriptors.map((descriptor, index) => (
                      <li key={descriptor.turnId}>
                        <Link
                          scroll={false}
                          href={`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(descriptor.turnId)}&branchRoot=${encodeURIComponent(branchNavigation.rootId)}`}
                          aria-current={
                            descriptor.turnId === currentBranchDescriptor?.turnId
                              ? "page"
                              : undefined
                          }
                        >
                          <strong>
                            {index + 1}. {descriptor.title}
                          </strong>
                        </Link>
                        <details className={conversationStyles.branchDetails}>
                          <summary aria-label={`分支 ${index + 1} 详情`}>详情</summary>
                          <p>{descriptor.title}</p>
                          <p>{descriptor.sourceTitle ? `源自“${descriptor.sourceTitle}”` : descriptor.sourceTurnId ? "来源问题未在当前列表中" : "原始研究问题"}</p>
                          <p>ResearchTurn <code>{descriptor.turnId}</code><br />消息修订 <code>{descriptor.messageRevisionId}</code></p>
                        </details>
                      </li>
                    ))}
                  </ol>
                </details>
                {branchNavigation.next ? (
                  <Link
                    className="research-branch-step"
                    scroll={false}
                    aria-label={`下一个研究分支：${researchBranchDescriptor(agent2Turns, branchNavigation.next).title}`}
                    href={`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(branchNavigation.next.id || branchNavigation.next.turn_id)}&branchRoot=${encodeURIComponent(branchNavigation.rootId)}`}
                  >
                    ›
                  </Link>
                ) : (
                  <span
                    className="research-branch-step disabled"
                    aria-hidden="true"
                  >
                    ›
                  </span>
                )}
              </nav>
            ) : null;
  if (pageLoadState === "loading")
    return (
      <RequireProductAuth>
        <ProductShell projectId={projectId}>
          <section
            className="research-route-state"
            aria-busy="true"
            aria-label="研究页面加载状态"
          >
            <div className="product-loading" role="status" aria-live="polite">
              正在加载研究时间线与项目数据…
            </div>
          </section>
        </ProductShell>
      </RequireProductAuth>
    );
  if (pageLoadState === "error")
    return (
      <RequireProductAuth>
        <ProductShell projectId={projectId}>
          <section
            className="research-route-state"
            aria-label="研究页面错误状态"
          >
            <div className="product-state" role="alert">
              <h1>研究内容暂时无法加载</h1>
              <p>暂时无法读取项目数据或研究记录，请重试。</p>
              <button
                type="button"
                className="product-primary-action"
                onClick={() => setReloadKey((value) => value + 1)}
              >
                重新加载
              </button>
            </div>
          </section>
        </ProductShell>
      </RequireProductAuth>
    );
  return (
    <RequireProductAuth>
      <ProductShell projectId={projectId}>
        {materialPickerKey === composerDraftKey && history ? <ResearchMaterialPicker
          key={composerDraftKey} projectId={projectId}
          datasets={history.datasets.filter(item => item.status !== "trashed")}
          loadInitial={loadInitialMaterials} returnFocus={materialPickerTrigger.current}
          onClose={() => { setMobilePanel("timeline"); setMaterialPickerKey(null); }}
          onApply={value => { materials.set(value); setMobilePanel("timeline"); setMaterialPickerKey(null); }}
        /> : null}
        <a className="skip-link" href="#research-primary-content">
          跳到研究工作台
        </a>
        <section
          ref={workbenchRef}
          id="research-primary-content"
          tabIndex={-1}
          className={`research-workbench ${conversationStyles.workbench}`}
          data-layout-mode={researchLayoutMode}
          data-workbench-open={workbenchOpen}
          aria-label="项目研究工作台"
          style={
            {
              "--research-conversation-width": conversationWidth + "px",
            } as CSSProperties
          }
        >
          <output
            hidden
            data-testid="research-performance-diagnostic"
            data-turn-id={researchPerformanceSample?.turnId || ""}
            data-status={researchPerformanceSample?.status || ""}
            data-acknowledgement-ms={
              researchPerformanceSample?.acknowledgementMs ?? ""
            }
            data-first-truthful-progress-ms={
              researchPerformanceSample?.firstTruthfulProgressMs ?? ""
            }
          />
          <nav
            className="research-mobile-tabs"
            role="tablist"
            aria-label="研究页面视图"
          >
            <button
              ref={mobileTimelineTabRef}
              id="research-timeline-tab"
              type="button"
              role="tab"
              aria-controls="research-timeline-panel"
              aria-selected={mobilePanel === "timeline"}
              tabIndex={mobilePanel === "timeline" ? 0 : -1}
              onKeyDown={(event) => handleMobileTabKey(event, "timeline")}
              onClick={() => setMobilePanel("timeline")}
            >
              对话
            </button>
            <button
              ref={mobileWorkbenchTabRef}
              id="research-workbench-tab"
              type="button"
              role="tab"
              aria-controls="research-workbench-panel"
              aria-selected={mobilePanel === "workbench"}
              tabIndex={mobilePanel === "workbench" ? 0 : -1}
              onKeyDown={(event) => handleMobileTabKey(event, "workbench")}
              onClick={() => { setWorkbenchVisibility({ scope: workbenchScope, open: true }); setMobilePanel("workbench"); }}
            >
              工作台
            </button>
          </nav>
                {agent2TurnId && ((agent2RecoveryState.turnId === agent2TurnId && agent2RecoveryState.status !== "connected") || agent2CancelState === "confirming" || agent2DispatchNotice) ? (
                  <p
                    className={conversationStyles.progressNotice + " research-reconnect-notice"}
                    role="status"
                    aria-label="研究进度提示"
                    aria-live="polite"
                  >
                    <span>{agent2RecoveryState.turnId === agent2TurnId && agent2RecoveryState.status === "unavailable"
                      ? <>{agent2RecoveryState.message}{activeAgent2Progress ? " 当前显示上次读取的状态。" : ""}{agent2CancelState === "confirming" ? " 取消结果仍未确认。" : ""}</>
                      : agent2CancelState === "confirming" ? agent2CancelNotice : agent2RecoveryState.turnId === agent2TurnId && agent2RecoveryState.status === "reconnecting" ? (activeAgent2Progress ? "进度暂未确认，当前显示上次读取的状态。" : "研究进度暂时无法读取，请重试。") : agent2DispatchNotice}</span>
                    {" "}<button type="button" className="product-link-button" onClick={() => agent2ExecutionRef.current?.refresh()}>重新读取进度</button>
                    {agent2DispatchRetryable ? <button type="button" className="product-link-button" onClick={() => agent2ExecutionRef.current?.retryDispatch()}>重试开始分析</button> : null}
                  </p>
                ) : null}
          <aside
            id="research-timeline-panel"
            role="tabpanel"
            aria-labelledby="research-timeline-tab"
            className={`conversation-pane ${conversationStyles.pane} ${mobilePanel === "timeline" ? "mobile-panel-active" : "mobile-panel-inactive"}`}
          >
            <header>
              <div className="research-timeline-heading">
                <h1 title={session?.title || undefined}>对话</h1>
                {selectedSessionIsArchived || selectedSessionIsTrashed ? (
                  <span
                    className="research-session-lifecycle-badge"
                    data-status={selectedSessionLifecycle}
                  >
                    {selectedSessionIsTrashed ? "回收站" : "已归档"}
                  </span>
                ) : null}
              </div>
              <div className="research-timeline-actions">
                {canResearch && (session || hasExplicitScientificHandoff) && !selectedSessionIsArchived && !selectedSessionIsTrashed ? <Link
                  className={conversationStyles.newConversation}
                  href={freshResearchHref(projectId)} scroll={false}
                  aria-label="新建对话" title="新建对话"
                ><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg></Link> : null}
                {hasScientificWorkbenchContent ? <button type="button" className="product-secondary-action"
                  aria-label="本次科学结果" aria-controls="research-results-panel"
                  aria-expanded={workbenchOpen && workbenchView === "results"}
                  onClick={workbenchOpen && workbenchView === "results" ? closeContextPanel : revealScientificWorkbench}>
                  结果
                </button> : null}
                <button
                  ref={contextManifestTriggerRef}
                  type="button"
                  className="product-secondary-action"
                  aria-label="本次上下文"
                  aria-expanded={workbenchOpen && workbenchView === "context"}
                  aria-controls="research-context-panel"
                  onClick={workbenchView === "context" && mobilePanel === "workbench" ? closeContextPanel : revealActiveContextManifest}
                >
                  上下文
                </button>
                {session &&
                canResearch &&
                (selectedSessionIsArchived || selectedSessionIsTrashed) ? (
                  <>
                    <Link
                      className="product-primary-action"
                      href={startFreshResearchHref}
                    >
                      开始新的研究
                    </Link>
                    <button
                      type="button"
                      className="product-secondary-action"
                      disabled={sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading}
                      onClick={() =>
                        void changeSessionLifecycle(session, "ACTIVE")
                      }
                    >
                      {sessionLifecycleBusy === session.id
                        ? "正在恢复…"
                        : "恢复原会话"}
                    </button>
                  </>
                ) : null}
                <button
                  ref={sessionHistoryTriggerRef}
                  type="button"
                  className="product-secondary-action"
                  aria-expanded={sessionHistoryOpen}
                  aria-controls={
                    sessionHistoryOpen ? "research-session-history" : undefined
                  }
                  onClick={() => {
                    if (sessionHistoryOpen) closeSessionHistory();
                    else setSessionHistoryOpen(true);
                  }}
                >
                  研究记录
                </button>
              </div>
              {sessionHistoryOpen && (
                <div
                  ref={sessionHistoryRef}
                  id="research-session-history"
                  className="research-session-history"
                  role="dialog"
                  aria-modal="false"
                  aria-labelledby="research-session-history-title"
                >
                  <div className="research-session-history-heading">
                    <div>
                      <h2 id="research-session-history-title">研究记录</h2>
                      <span>{sessions.length} 项</span>
                    </div>
                    {canResearch ? <div className="research-session-history-actions">
                      <button
                        type="button"
                        onClick={() => {
                          setSessionSelectionMode((value) => !value);
                          setSelectedSessionIds([]);
                        }}
                      >
                        {sessionSelectionMode ? "完成" : "批量管理"}
                      </button>
                      {!sessionSelectionMode ? (
                        <Link
                          href={freshResearchHref(projectId)}
                          onClick={() => closeSessionHistory(false)}
                        >
                          新建研究
                        </Link>
                      ) : null}
                    </div> : null}
                  </div>
                  <label className="research-session-search">
                    <span className="sr-only">搜索研究记录</span>
                    <input
                      ref={sessionHistorySearchRef}
                      type="search"
                      value={sessionHistoryQuery}
                      onChange={(event) =>
                        setSessionHistoryQuery(event.target.value)
                      }
                      placeholder="搜索研究标题"
                      autoComplete="off"
                    />
                  </label>
                  <div
                    className="research-session-filters segmented-control"
                    role="group"
                    aria-label="研究记录状态"
                  >
                    {(
                      [
                        ["current", "当前"],
                        ["archived", "已归档"],
                        ["trashed", "回收站"],
                      ] as const
                    ).map(([value, label]) => (
                      <button
                        key={value}
                        ref={(element) => {
                          if (element) sessionHistoryFilterRefs.current.set(value, element);
                          else sessionHistoryFilterRefs.current.delete(value);
                        }}
                        type="button"
                        className={sessionHistoryStatus === value ? "active" : ""}
                        aria-pressed={sessionHistoryStatus === value}
                        onClick={() => {
                          setSessionHistoryStatus(value);
                          setSelectedSessionIds([]);
                        }}
                        onKeyDown={(event) =>
                          handleSessionHistoryFilterKey(event, value)
                        }
                      >
                        {label} {sessionStatusCounts[value]}
                      </button>
                    ))}
                  </div>
                  {!sessionRenameTarget && !sessionActionConfirmation ? sessionManagementFeedback : null}
                  {!sessionLifecycleNotice && sessionOperation.notice ? <p className="research-session-lifecycle-notice" role="status">{sessionOperation.notice}</p> : null}
                  {sessionLifecycleNotice ? (
                    <p className="sr-only" role="status" aria-live="polite">
                      {sessionLifecycleNotice}
                    </p>
                  ) : null}
                  {sessionSelectionMode ? (
                    <div
                      className="research-session-bulk-actions"
                      aria-label="研究记录批量操作"
                    >
                      <div>
                        <button
                          type="button"
                          disabled={!filteredSessions.length || sessionBulkBusy || sessionOperation.pending}
                          onClick={() =>
                            setSelectedSessionIds((current) =>
                              filteredSessions.every((item) =>
                                current.includes(item.id),
                              )
                                ? current.filter(
                                    (id) =>
                                      !filteredSessions.some(
                                        (item) => item.id === id,
                                      ),
                                  )
                                : Array.from(
                                    new Set([
                                      ...current,
                                      ...filteredSessions.map((item) => item.id),
                                    ]),
                                  ),
                            )
                          }
                        >
                          {filteredSessions.length > 0 &&
                          filteredSessions.every((item) =>
                            selectedSessionIds.includes(item.id),
                          )
                            ? "取消全选"
                            : "全选当前"}
                        </button>
                        <span>{selectedSessionIds.length} 项已选</span>
                      </div>
                      {selectedSessionIds.length ? (
                        <div>
                          <button
                            type="button"
                            disabled={sessionBulkBusy || sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading}
                            onClick={() => void applySessionBulkAction("PIN")}
                          >
                            列表置顶
                          </button>
                          <button
                            type="button"
                            disabled={sessionBulkBusy || sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading}
                            onClick={() => void applySessionBulkAction("UNPIN")}
                          >
                            取消列表置顶
                          </button>
                          {sessionHistoryStatus === "current" ? (
                            <button
                              type="button"
                              disabled={sessionBulkBusy || sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading}
                              onClick={() =>
                                void applySessionBulkAction("ARCHIVE")
                              }
                            >
                              归档所选
                            </button>
                          ) : (
                            <button
                              type="button"
                              disabled={sessionBulkBusy || sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading}
                              onClick={() =>
                                void applySessionBulkAction("RESTORE")
                              }
                            >
                              恢复所选
                            </button>
                          )}
                          {sessionHistoryStatus !== "trashed" ? (
                            <button
                              type="button"
                              className="danger"
                              disabled={sessionBulkBusy || sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading}
                              onClick={() =>
                                void applySessionBulkAction("TRASH")
                              }
                            >
                              移入回收站
                            </button>
                          ) : null}
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                  <div className="research-session-list" aria-live="polite">
                    {filteredSessions.map((item) => {
                      const status = String(
                        item.status || "active",
                      ).toLowerCase();
                      return (
                        <ManagedObjectRow
                          key={item.id}
                          active={item.id === session?.id}
                          selectionMode={sessionSelectionMode}
                          selected={selectedSessionIds.includes(item.id)}
                          onSelectedChange={(selected) =>
                            setSelectedSessionIds((current) =>
                              selected
                                ? Array.from(new Set([...current, item.id]))
                                : current.filter((id) => id !== item.id),
                            )
                          }
                          href={researchSessionHref(
                            projectId,
                            item.id,
                            history,
                          )}
                          title={item.title}
                          truncateTitle
                          description={`${item.pinned ? "列表置顶 · " : ""}${researchSessionStatusLabel(item.status)}`}
                          actions={canResearch ? [
                            {
                              label: item.pinned ? "取消列表置顶" : "列表置顶",
                              disabled: sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading,
                              onSelect: () => void toggleSessionPinned(item),
                            },
                            {
                              label: "重命名",
                              disabled: sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading,
                              onSelect: () => openSessionRename(item),
                            },
                            ...(status === "trashed"
                              ? [
                                  {
                                    label: "恢复研究记录",
                                    disabled: sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading,
                                    onSelect: () =>
                                      void changeSessionLifecycle(item, "ACTIVE"),
                                  },
                                ]
                              : status === "archived"
                                ? [
                                    {
                                      label: "恢复到当前研究",
                                      disabled: sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading,
                                      onSelect: () =>
                                        void changeSessionLifecycle(item, "ACTIVE"),
                                    },
                                    {
                                      label: "移入回收站",
                                      destructive: true,
                                      disabled: sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading,
                                      onSelect: () =>
                                        void changeSessionLifecycle(item, "TRASHED"),
                                    },
                                  ]
                                : [
                                    {
                                      label: "归档",
                                      disabled: sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading,
                                      onSelect: () =>
                                        void changeSessionLifecycle(item, "ARCHIVED"),
                                    },
                                    {
                                      label: "移入回收站",
                                      destructive: true,
                                      disabled: sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading,
                                      onSelect: () =>
                                        void changeSessionLifecycle(item, "TRASHED"),
                                    },
                                  ]),
                          ] : []}
                        />
                      );
                    })}
                    {!sessions.length ? (
                      <p className="research-session-empty">
                        还没有研究记录。新建研究后会保存在这里。
                      </p>
                    ) : !filteredSessions.length ? (
                      <p className="research-session-empty">
                        {normalizedSessionQuery
                          ? `没有匹配“${sessionHistoryQuery.trim()}”的研究记录。`
                          : sessionHistoryStatus === "archived"
                            ? "还没有已归档的研究记录。"
                            : sessionHistoryStatus === "trashed"
                              ? "回收站中没有研究记录。"
                              : "当前没有可继续的研究记录。"}
                      </p>
                    ) : null}
                  </div>
                </div>
              )}
            </header>
            <div className="conversation-branch-region">
            {(contextNavigation.directory.pending || contextNavigation.directory.failed) ? (
              <div className="research-navigation-notice" role="status">
                <span>{contextNavigation.directory.pending
                  ? "正在读取分支记录…"
                  : contextNavigation.directory.data ? "分支记录暂未更新，仍显示上次读取的内容。" : "分支记录暂时无法读取。"}</span>
                {contextNavigation.directory.failed ? <button type="button" className="product-link-button" onClick={() => { directoryRetryFocus.current = contextNavigation.directory.scope; contextNavigation.directory.retry(); }}>重新读取分支记录</button> : null}
              </div>
            ) : null}
            {!conversationWindow.visible.some((message) => message.id === selectedTurnMessageId) ? branchVersionNavigation : null}
            </div>
            {researchSettingsOpen ? <ResearchSettings
              models={userModels} provider={selectedProvider} model={selectedModel} thinkingMode={thinkingMode} autonomyMode={autonomyMode}
              busy={state === "planning" || state === "running"} loadState={providerLoadState}
              onModel={(choice) => { providerChoiceRef.current = { key: providerSettingsKey, provider: choice.provider, model: choice.model }; setSelectedProvider(choice.provider); setSelectedModel(choice.model); }}
              onThinking={setThinkingMode} onAutonomy={setAutonomyMode} onRetry={() => setProviderReloadKey((value) => value + 1)} onClose={() => setResearchSettingsOpen(false)}
            /> : null}
            {sessionActionConfirmation ? <ProductModal
              eyebrow=""
              title={`${sessionActionLabel(sessionActionConfirmation.action)}${sessionActionConfirmation.items.length > 1 ? ` ${sessionActionConfirmation.items.length} 项` : ""}研究记录`}
              description={sessionActionConfirmation.action === "TRASH" ? "移入回收站后仍可恢复，历史问题、结果与来源会保留。" : "归档后可以继续查看历史内容，需要继续研究时可恢复。"}
              returnFocus={sessionLifecycleFocusRef.current}
              onClose={() => { sessionOperation.dismiss(); setSessionActionConfirmation(null); }}
              footer={<><button type="button" className="product-secondary-action" onClick={() => { sessionOperation.dismiss(); setSessionActionConfirmation(null); }}>取消</button><button type="button" className={sessionActionConfirmation.action === "TRASH" ? "product-danger-action" : "product-primary-action"} disabled={sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading} onClick={() => void executeSessionAction(sessionActionConfirmation)}>{sessionOperation.pending ? "正在保存…" : `确认${sessionActionLabel(sessionActionConfirmation.action)}`}</button></>}
            >
              <ul className="research-session-confirm-items">{sessionActionConfirmation.items.map((item) => <li key={item.id}>{item.title}</li>)}</ul>
              {sessionManagementFeedback}
            </ProductModal> : null}
            {sessionRenameTarget ? (
              <ProductModal
                eyebrow=""
                title="重命名研究"
                returnFocus={sessionLifecycleFocusRef.current}
                onClose={closeSessionRename}
                footer={
                  <>
                    <button
                      type="button"
                      className="product-secondary-action"
                      onClick={closeSessionRename}
                    >
                      取消
                    </button>
                    <button
                      type="button"
                      className="product-primary-action"
                      disabled={
                        !sessionRenameValue.trim() ||
                        sessionOperation.pending || sessionOperation.uncertain || sessionDirectoryReading
                      }
                      onClick={() => void renameSession()}
                    >
                      {sessionLifecycleBusy === sessionRenameTarget.id
                        ? "正在保存…"
                        : "保存名称"}
                    </button>
                  </>
                }
              >
                <label className="product-field research-session-name-field">
                  <span>研究名称</span>
                  <input
                    value={sessionRenameValue}
                    disabled={sessionOperation.pending}
                    maxLength={200}
                    onChange={(event) => setSessionRenameValue(event.target.value)}
                  />
                </label>
                {sessionManagementFeedback}
              </ProductModal>
            ) : null}
            <div className="conversation-history" id="research-conversation-history" role="region" aria-label="对话内容" tabIndex={0} ref={conversationHistoryRef}>
              {showResearchStarter && history && (activeViewerContext || incompleteViewerContext) ? (
                <section className="research-starter" aria-labelledby="research-starter-title">
                  <h2 id="research-starter-title">{viewerSelectionError ? "先确认本次研究范围" : "研究所选数据"}</h2>
                  {!canResearch ? <p>你可以查看来源与已有结果，当前权限不能发起新研究。</p> : null}
                </section>
              ) : showResearchStarter && history ? (
                <ResearchStarter
                  projectId={projectId}
                  datasetCount={history.datasets.length}
                  selectedDataset={datasetId ? { id: datasetId, name: starterDataset?.name || datasetId, sampleRef, sourceSelectionToken, hasSourceSelection: Boolean(datasetSelection.selection || datasetSelection.error) } : undefined}
                  canResearch={canResearch}
                  projectStatus={projectLifecycle}
                  prompts={starterPrompts}
                  onTryQuestion={trySuggestedQuestion}
                />
              ) : null}
              {pageLoadError ? <div className="conversation-load-state error" role="alert"><p>{pageLoadError}</p><button type="button" className="product-secondary-action" onClick={() => setReloadKey((value) => value + 1)}>重新读取研究内容</button></div> : null}
              {sessionLoadState === "loading" ? (
                <p className="conversation-load-state" role="status">
                  正在恢复研究对话…
                </p>
              ) : null}
              {sessionLoadState === "error" ? (
                <div className="conversation-load-state error" role="alert">
                  <strong>研究对话暂时无法读取</strong>
                  <p>{sessionLoadError || "请重新加载对话，确认这条研究记录的当前状态。"}</p>
                  <button
                    type="button"
                    className="product-secondary-action"
                    onClick={() => setReloadKey((value) => value + 1)}
                  >
                    重新加载对话
                  </button>
                </div>
              ) : null}
              {runId && !session && sessionLoadState === "ready" ? (
                <div className="conversation-load-state" role="note">
                  <strong>这次历史分析没有关联到可恢复的研究对话</strong>
                  <p>右侧结果仍可查看；系统不会把它归入其他会话。</p>
                </div>
              ) : null}
              {messages.length > 10 ? (
                <div className="conversation-window-control" role="status">
                  <span>
                    {showFullConversation
                      ? conversationWindow.hiddenBefore
                        ? `正在显示会话窗口 · ${conversationWindow.hiddenBefore + 1}–${conversationWindow.hiddenBefore + conversationWindow.visible.length} / ${messages.length} 条消息`
                        : `正在显示完整会话 · ${messages.length} 条消息`
                      : selectedTurnMessageId
                        ? `已聚焦当前研究分支 · 隐藏 ${hiddenConversationCount} 条其他历史消息`
                        : `正在显示最近 ${conversationWindow.visible.length} 条消息`}
                  </span>
                  {showFullConversation && conversationWindow.hiddenBefore > 0 ? (
                    <button
                      type="button"
                      className="product-link-button"
                      onClick={() =>
                        setConversationWindowStart((current) =>
                          Math.max(0, current - 100),
                        )
                      }
                    >
                      查看更早消息
                    </button>
                  ) : null}
                  {showFullConversation && conversationWindow.hiddenAfter > 0 ? (
                    <button
                      type="button"
                      className="product-link-button"
                      onClick={() =>
                        setConversationWindowStart((current) =>
                          Math.min(messages.length - 100, current + 100),
                        )
                      }
                    >
                      查看更新消息
                    </button>
                  ) : null}
                  <button
                    type="button"
                    className="product-link-button"
                    onClick={() => {
                      setShowFullConversation((value) => !value);
                      setConversationWindowStart(0);
                    }}
                  >
                    {showFullConversation ? "收起会话窗口" : "查看会话窗口"}
                  </button>
                </div>
              ) : null}
              <div
                className="conversation-stream"
                ref={conversationScroll.contentRef}
                role="log"
                aria-label="研究对话"
                aria-live="off"
              >
                {conversationWindow.visible.map((message) => {
                  const isSelectedTurnMessage =
                    message.id === selectedTurnMessageId;
                  return (
                    <article
                      key={message.id}
                      data-message-id={message.id}
                      className={`conversation-message ${message.role}${isSelectedTurnMessage ? " current-turn-message" : ""}`}
                      aria-current={isSelectedTurnMessage ? "true" : undefined}
                      aria-label={
                        message.role === "user"
                          ? isSelectedTurnMessage
                            ? "当前分支的研究问题"
                            : "你的消息"
                          : "研究助手消息"
                      }
                    >
                      <div className="conversation-message-meta">
                        <span>
                          {message.role === "user" ? "你" : "研究助手"}
                        </span>
                        {isSelectedTurnMessage ? (
                          <strong>当前分支问题</strong>
                        ) : null}
                      </div>
                      {message.role === "assistant" ? (
                        <ResearchReplyContent text={displayResearchMessage(message)} scientific={message.payload?.source === "agent2_scientific_interpreter"} />
                      ) : <p>{displayResearchMessage(message)}</p>}
                      {isSelectedTurnMessage ? branchVersionNavigation : null}
                    </article>
                  );
                })}
                {showAnswerDraft && answerDraft ? <article className="conversation-message assistant" aria-label={answerDraft.phase === "completed" ? "研究助手消息" : "正在生成的研究回答"} aria-busy={answerDraft.phase !== "completed"}>
                  <div className="conversation-message-meta">
                    <span>研究助手</span>
                    {answerDraft.phase === "reconnecting" ? <span role="status">正在重新连接…</span> : null}
                  </div>
                  <ResearchReplyContent text={answerDraft.text} streaming={answerDraft.phase !== "completed"} scientific={answerDraft.scientific} />
                </article> : null}
                {activeAgent2Progress && !answerStreaming ? (
                  <ResearchExecutionActivity
                    progress={activeAgent2Progress}
                    completedAnswerVisible={completedAnswerVisible}
                    onCancel={() => void cancelAgent2Turn()}
                    cancelPending={agent2CancelState === "submitting"}
                    cancelUnconfirmed={agent2CancelState === "confirming"}
                    onRetry={
                      selectedSessionIsWritable && canResearch
                        ? () => void retryAgent2Turn()
                        : undefined
                    }
                    onContinue={
                      selectedSessionIsWritable && canResearch
                        ? continueAgent2Research
                        : undefined
                    }
                    retryPending={agent2RetryPending}
                    onReinterpret={selectedSessionIsWritable && canResearch ? () => void retryAgent2Turn("reinterpret") : undefined}
                    onEdit={
                      selectedSessionIsWritable && canResearch
                        ? editAgent2Turn
                        : undefined
                    }
                  />
                ) : null}
                {retryLineage && session ? (
                  <section
                    className="research-edit-notice"
                    role="status"
                    aria-label="研究重试关系"
                  >
                    <strong>本次为重新分析</strong>
                    <Link
                      className="product-link-button"
                      href={`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(retryLineage.source.turn_id)}`}
                    >
                      查看原分析
                    </Link>
                    <details>
                      <summary>分支标识</summary>
                      <span>
                        当前 <code>{retryLineage.current.turn_id}</code>
                      </span>
                      <span>
                        来源 <code>{retryLineage.source.turn_id}</code>
                      </span>
                    </details>
                  </section>
                ) : null}
                {agent2CancelNotice && agent2CancelState !== "confirming" ? (
                  <p
                    className="research-cancel-notice"
                    role="status"
                    aria-live="polite"
                  >
                    {agent2CancelNotice}
                  </p>
                ) : null}
                {error && activeAgent2Progress ? (
                  <p className="product-form-error" role="alert">
                    {error}
                  </p>
                ) : null}
                {agent2TurnId &&
                activeAgent2Progress &&
                !activeAgent2Progress.warnings.some((warning) => warning.code === "INTERPRETATION_GROUNDING_REJECTED") &&
                ["COMPLETED", "PARTIAL"].includes(activeAgent2Progress.status) ? (
                  <ScientificReportAction
                    projectId={projectId}
                    turnId={agent2TurnId}
                    canGenerate={canResearch}
                  />
                ) : null}
                {state !== "idle" && !activeAgent2Progress && (
                  <InlineRunProcess
                    state={state}
                    scope={scope}
                    job={job}
                    events={events}
                    artifacts={artifacts}
                    error={error}
                  />
                )}
              </div>
            </div>
            {conversationScroll.showJump ? <button
              type="button"
              className={conversationStyles.jumpToLatest}
              ref={conversationScroll.jumpButtonRef}
              aria-label="回到对话底部"
              aria-controls="research-conversation-history"
              title="回到对话底部"
              onClick={conversationScroll.jumpToLatest}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 5v14m-6-6 6 6 6-6" /></svg>
            </button> : null}
            {history &&
            canResearch &&
            sessionLoadState === "ready" &&
            selectedSessionIsWritable ? (
              <form
                className="research-composer"
                onSubmit={(event) => {
                  event.preventDefault();
                  void submitQuestion();
                }}
              >
                {editTurnId ? (
                  <div
                    id="research-edit-status"
                    className="research-edit-notice research-composer-edit-mode"
                    role={editingLoadState === "error" ? "alert" : "status"}
                  >
                    <span>
                      {editingLoadState === "loading"
                        ? "正在读取原问题和来源…"
                        : editingLoadState === "error"
                          ? "原研究暂未读全。可以继续编辑草稿，重新读取后再提交。"
                          : "编辑问题"}
                    </span>
                    <div className="research-edit-actions">
                      {editSource.failed ? <button type="button" className="product-secondary-action" disabled={editSource.pending} onClick={() => {
                        editComposerFocusRef.current = { key: composerDraftKey, origin: document.activeElement, handled: false };
                        editSource.retry();
                      }}>
                        {editSource.pending ? "正在读取原研究…" : "重新读取原研究"}
                      </button> : null}
                      <Link className="product-link-button" scroll={false} href={`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session?.id || sessionId || "")}?turn=${encodeURIComponent(editTurnId)}`}>返回原研究</Link>
                    </div>
                  </div>
                ) : null}
                <label className="sr-only" htmlFor="research-question">
                  {editTurnId ? "编辑问题" : "研究问题"}
                </label>
                {materials.error ? <p role="alert">{materials.error}</p> : null}
                {!materials.value ? <>
                {datasetSelection.selection || datasetSelection.error ? <div className="research-composer-source" role={datasetSelection.error ? "alert" : "status"} id="research-dataset-source">
                  <div><strong>{datasetSelection.error ? "需要重新选择数据" : datasetSelection.selection?.family === "volumetric" ? "已指定 1 个体数据字段" : datasetSelection.selection?.family === "trajectory" ? (datasetSelection.selection.context.primary?.kind === "TRAJECTORY_ATOM" ? "已指定轨迹中的 1 个原子" : "已指定 1 个轨迹帧") : datasetSelection.selection?.family === "structure" ? "已指定 1 个原子" : datasetSelection.selection?.family === "phonon" ? (datasetSelection.selection.context.primary?.kind === "PHONON_DOS_POINT" ? "已指定 1 个声子态密度点" : "已指定 1 个声子模式") : datasetSelection.selection?.context.primary?.kind === "ELECTRONIC_BAND_STATE" ? "已指定 1 个能带状态" : "已指定 1 个态密度点"}</strong><span>{datasetSelection.error || datasetSelection.selection?.label}</span></div>
                  <Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/data?dataset=${encodeURIComponent(datasetId || "")}${datasetSelection.selection && sourceSelectionToken ? `&selection=${encodeURIComponent(sourceSelectionToken)}` : ""}`}>{datasetSelection.error ? "返回来源数据重新选择" : datasetSelection.selection?.family === "volumetric" ? "查看所选体数据字段" : datasetSelection.selection?.family === "trajectory" ? "查看所选轨迹位置" : datasetSelection.selection?.family === "structure" ? "查看所选原子" : datasetSelection.selection?.family === "phonon" ? (datasetSelection.selection.context.primary?.kind === "PHONON_DOS_POINT" ? "查看所选态密度点" : "查看所选声子模式") : "查看所选电子数据"}</Link>
                </div> : null}
                {incompleteViewerContext ? <div className="research-composer-source" role="alert" id="research-viewer-source"><p>{viewerSelectionError}</p><Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/data`}>返回项目数据</Link></div> : activeViewerContext && !contextCandidateFromSearch && !viewerSelectionError ? (
                  <button type="button" id="research-viewer-source" className={conversationStyles.composerSource}
                    aria-label="查看本次数据上下文" aria-controls="research-context-panel" onClick={revealActiveContextManifest}>
                    <span><strong>{activeViewerContext.sourceRef.displayName}</strong><span>{activeViewerContext.selection?.displayLabel || "完整数据版本"}</span></span>
                    <span aria-hidden="true">›</span>
                  </button>
                ) : activeViewerContext && viewerSelectionError ? (
                  <div className="research-composer-source" role={viewerSelectionError ? "alert" : "status"} id="research-viewer-source">
                    <div><strong>{activeViewerContext.sourceRef.displayName}</strong><span>{viewerSelectionError || activeViewerContext.selection?.displayLabel || "使用此完整版本"}</span></div>
                    <div className="product-row-actions">
                      <Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/data?object=${encodeURIComponent(activeViewerContext.sourceRef.objectId)}&version=${encodeURIComponent(activeViewerContext.sourceRef.versionId)}${!viewerSelectionError && activeViewerContext.selection && viewerContext?.selectionToken ? `&selection=${encodeURIComponent(viewerContext.selectionToken)}` : ""}`}>{viewerSelectionError ? "返回数据重新选择" : "查看所选来源"}</Link>
                      {viewerSelectionError ? <button type="button" className="product-secondary-action" onClick={() => setWholeViewerVersionKey(viewerSelectionKey)}>使用此完整版本</button> : null}
                    </div>
                  </div>
                ) : null}
                {contextCandidateFromSearch && searchContextCandidateActive && !viewerSelectionError ? (
                  <div
                    className="research-composer-context-candidate"
                    role="status"
                    aria-label="待加入本次研究的检索上下文"
                  >
                    <span>
                      <strong>待使用来源</strong>
                      <small>
                        {activeSearchResultContextId
                          ? "检索中选择的科学结果，提交问题后才会进入实际 Context Used。"
                          : `${activeViewerContext?.sourceRef.displayName || "检索中选择的科学数据"}${activeViewerContext?.selection ? ` · ${activeViewerContext.selection.displayLabel}` : ""}，提交问题后才会进入实际 Context Used。`}
                      </small>
                    </span>
                    <button
                      type="button"
                      className="product-secondary-action"
                      onClick={() => setSearchContextCandidateActive(false)}
                    >
                      移除
                    </button>
                  </div>
                ) : null}
                </> : null}
                <textarea
                  ref={questionInputRef}
                  id="research-question"
                  aria-label={editTurnId ? "编辑问题" : "研究问题"}
                  aria-describedby={
                    [
                      editTurnId ? "research-edit-status" : null,
                      !materials.value && (datasetSelection.selection || datasetSelection.error) ? "research-dataset-source" : null,
                      !materials.value && (incompleteViewerContext || (activeViewerContext && (!contextCandidateFromSearch || viewerSelectionError))) ? "research-viewer-source" : null,
                    ]
                      .filter(Boolean)
                      .join(" ") || undefined
                  }
                  value={question}
                  onChange={(event) => { editedDraftKeyRef.current = composerDraftKey; setQuestion(event.target.value); }}
                  placeholder="输入研究问题…"
                  rows={3}
                />
                <div className="research-composer-footer">
                  <div className={materialStyles.composerTools}>
                  <button type="button" className={materialStyles.trigger}
                    aria-label={materials.value ? `选择材料，已选 ${materials.value.items.length} 项` : "选择材料"} aria-haspopup="dialog"
                    aria-expanded={materialPickerKey === composerDraftKey}
                    disabled={materials.pending || state === "planning" || state === "running" || resultActionPending}
                    onClick={event => { materialPickerTrigger.current = event.currentTarget; setMaterialPickerKey(composerDraftKey); }}>
                    <span aria-hidden="true">＋</span><span>{materials.value ? `材料 · ${materials.value.items.length}` : "材料"}</span>
                  </button>
                  <button type="button" className="research-settings-trigger" aria-label="研究设置" aria-haspopup="dialog" aria-expanded={researchSettingsOpen} onClick={() => setResearchSettingsOpen(true)}>
                    <span>{selectedModel || (providerLoadState === "loading" ? "正在读取模型…" : "选择模型")}</span><span aria-hidden="true">⌄</span>
                  </button>
                  </div>
                  {agent2TurnId && (answerStreaming || canCancelResearchTurn(activeAgent2Progress?.status) || isResearchCancellationPending(activeAgent2Progress?.status) || agent2CancelState !== "idle") ? (
                    <button
                      type="button"
                      className="product-danger-action research-composer-stop"
                      aria-label={answerStreaming ? "停止生成" : "从输入区取消当前分析"}
                      onClick={() => void cancelAgent2Turn()}
                      disabled={agent2CancelState !== "idle" || isResearchCancellationPending(activeAgent2Progress?.status)}
                    >
                      {agent2CancelState === "submitting" ? "正在提交取消…" : agent2CancelState === "confirming" ? "等待取消确认" : answerStreaming ? "停止生成" : "取消当前分析"}
                    </button>
                  ) : (
                    <button
                      type="submit"
                      className="product-primary-action"
                      disabled={
                        materials.pending || Boolean(materials.error || (!materials.value && (viewerSelectionError || datasetSelection.error))) ||
                        resultActionPending ||
                        !userModels.some((item) => item.provider === selectedProvider && item.model === selectedModel) ||
                        !question.trim() ||
                        state === "planning" ||
                        state === "running" ||
                        !editBranchSubmissionAllowed(
                          editTurnId,
                          editingLoadState,
                          editingTurn,
                        )
                      }
                    >
                      {state === "planning"
                        ? "正在准备…"
                        : state === "running"
                          ? "正在分析…"
                          : "发送"}
                    </button>
                  )}
                </div>
                {providerLoadState === "error" && !researchSettingsOpen ? (
                  <div className="research-provider-notice" role="alert">
                    <span>
                      {userModels.length ? "模型列表暂未更新，当前选择仍保留。" : "模型暂时无法读取，请重试后发送。"}
                    </span>
                    <button
                      type="button"
                      className="product-link-button"
                      onClick={() => setProviderReloadKey((value) => value + 1)}
                    >
                      重新读取模型
                    </button>
                  </div>
                ) : providerStatus &&
                  providerStatus.status !== "ready" &&
                  !providerOptions.some((item) => item.secretConfigured) ? (
                  <Link
                    className="research-provider-notice"
                    href="/console?settings=models"
                  >
                    研究助手尚未配置 · 打开模型设置
                  </Link>
                ) : null}
              </form>
            ) : history &&
              canResearch &&
              sessionLoadState !== "error" &&
              selectedSessionIsWritable ? null : history &&
              !canResearch &&
              showResearchStarter ? null : history ? (
              <div
                className="research-composer research-composer-readonly"
                role="note"
              >
                <strong>
                  {selectedSessionIsTrashed
                    ? "这条研究记录位于回收站"
                    : selectedSessionIsArchived
                      ? "这条研究记录已归档"
                      : sessionLoadState === "error"
                        ? "研究对话暂时不可写"
                        : "此项目为只读"}
                </strong>
                <p>
                  {selectedSessionIsTrashed
                    ? "历史对话、科学结果和精确来源仍可查看。先从回收站恢复，才能继续或重试研究。"
                    : selectedSessionIsArchived
                      ? "历史对话、科学结果和精确来源仍可查看。可以开始新的研究，或恢复原会话后继续。"
                      : sessionLoadState === "error"
                        ? "重新加载对话后可继续研究，避免把内容写入错误会话。"
                        : "你可以查看已有对话、分析过程和科学结果，但不能发起新的研究。"}
                </p>
              </div>
            ) : (
              <div
                className="research-composer research-composer-readonly"
                role="status"
              >
                {projectHistoryReadState === "error" ? "项目权限暂时无法确认。请重新读取研究内容后再发送。" : "正在确认项目权限…"}
              </div>
            )}
          </aside>
          <button
            type="button"
            tabIndex={0}
            className="research-splitter"
            role="separator"
            aria-label="调整研究对话宽度"
            aria-orientation="vertical"
            aria-valuemin={320}
            aria-valuemax={conversationMaxWidth}
            aria-valuenow={conversationWidth}
            aria-valuetext={`${conversationWidth} 像素对话宽度`}
            onPointerDown={(event) => {
              event.currentTarget.setPointerCapture(event.pointerId);
              chooseConversationWidth(
                event.clientX - (workbenchRef.current?.getBoundingClientRect().left || 0),
              );
            }}
            onPointerMove={(event) => {
              if (event.currentTarget.hasPointerCapture(event.pointerId))
                chooseConversationWidth(
                  event.clientX - (workbenchRef.current?.getBoundingClientRect().left || 0),
                );
            }}
            onPointerUp={(event) => {
              if (event.currentTarget.hasPointerCapture(event.pointerId))
                event.currentTarget.releasePointerCapture(event.pointerId);
            }}
            onKeyDown={(event) => {
              const requested = event.key === "ArrowLeft" ? conversationWidth - 16
                : event.key === "ArrowRight" ? conversationWidth + 16
                : event.key === "Home" ? 320
                : event.key === "End" ? 760 : null;
              if (requested === null) return;
              event.preventDefault();
              chooseConversationWidth(requested);
            }}
          />
          <section
            id="research-workbench-panel"
            role="tabpanel"
            aria-labelledby="research-workbench-tab"
            className={`research-workbench-pane ${conversationStyles.detailPane} ${mobilePanel === "workbench" ? "mobile-panel-active" : "mobile-panel-inactive"}`}
          >
            <div className={conversationStyles.workbenchHeader}>
            <div className={conversationStyles.workbenchTabs} role="tablist" aria-label="研究详情">
              {(["results", "context"] as const).map((view) => (
                <button key={view} type="button" role="tab"
                  id={`research-detail-${view}-tab`}
                  aria-controls={`research-${view}-panel`}
                  aria-selected={workbenchView === view}
                  tabIndex={workbenchView === view ? 0 : -1}
                  onClick={() => { if (view === "context") revealActiveContextManifest(); else setWorkbenchView("results"); }}
                  onKeyDown={(event) => {
                    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
                    event.preventDefault();
                    const next = event.key === "Home" ? "results" : event.key === "End" ? "context" : view === "results" ? "context" : "results";
                    setWorkbenchView(next);
                    document.getElementById(`research-detail-${next}-tab`)?.focus();
                  }}
                >{view === "results" ? "结果" : "上下文"}</button>
              ))}
            </div>
            <button type="button" className={conversationStyles.closeWorkbench} aria-label="收起工作台"
              onClick={closeContextPanel}>收起</button>
            </div>
            <div id="research-context-panel" ref={contextPanelRef} className={conversationStyles.contextPanel}
              role="tabpanel" aria-labelledby="research-detail-context-tab" hidden={workbenchView !== "context"} tabIndex={-1}
              onKeyDown={(event) => { if (event.key === "Escape") { event.preventDefault(); closeContextPanel(); } }}>
              {materials.value || materials.error || activeViewerContext || datasetId || !navigationTurnId ? <section className={conversationStyles.contextSelection} aria-label="准备发送的上下文">
                <h2>待使用的数据</h2>
                {materials.value ? <>
                  <ul className={materialStyles.contextList}>{materials.value.items.map(item => <li key={materialKey(item.ref)}>
                    <Link href={`/projects/${encodeURIComponent(projectId)}/data?object=${encodeURIComponent(item.ref.object_id)}&version=${encodeURIComponent(item.ref.version_id)}`}>{item.ref.display_name || materialTypes[item.ref.object_type] || item.ref.object_type}</Link>
                    <span>{materialTypes[item.ref.object_type]} · 版本 {item.ref.version_id.slice(0, 8)}</span>
                    {materials.value!.selections.filter(s => materialKey(s.object_ref) === materialKey(item.ref)).map((s, index) => <span key={index}>{s.display_label}</span>)}
                  </li>)}</ul>
                  <button type="button" className="product-link-button" disabled={state === "planning" || state === "running" || resultActionPending} onClick={() => materials.set(null)}>恢复原来源</button>
                </> : materials.error ? <p role="alert">{materials.error}</p> : activeViewerContext ? <>
                  <p>{activeViewerContext.sourceRef.displayName}</p>
                  <p>{viewerSelectionError || activeViewerContext.selection?.displayLabel || "完整数据版本"}</p>
                  <Link href={`/projects/${encodeURIComponent(projectId)}/data?object=${encodeURIComponent(activeViewerContext.sourceRef.objectId)}&version=${encodeURIComponent(activeViewerContext.sourceRef.versionId)}${!viewerSelectionError && activeViewerContext.selection && viewerContext?.selectionToken ? `&selection=${encodeURIComponent(viewerContext.selectionToken)}` : ""}`}>打开来源数据</Link>
                </> : datasetId ? <>
                  <p>{starterDataset?.name || "所选数据集"}</p>
                  {datasetSelection.selection?.label ? <p>{datasetSelection.selection.label}</p> : null}
                  {datasetSelection.error ? <p role="alert">{datasetSelection.error}</p> : null}
                  <Link href={`/projects/${encodeURIComponent(projectId)}/data?dataset=${encodeURIComponent(datasetId)}${sourceSelectionToken ? `&selection=${encodeURIComponent(sourceSelectionToken)}` : ""}`}>查看所选数据</Link>
                </> : <>
                  <p>{agent2TurnId ? "没有另外指定下一次提问的数据。" : "尚未指定研究数据。"}</p>
                  <Link href={`/projects/${encodeURIComponent(projectId)}/data`}>选择数据</Link>
                </>}
              </section> : null}
              {sessionMemory &&
              (sessionMemory.pinned_object_refs.length ||
                sessionMemory.pinned_result_refs.length ||
                sessionMemory.session_constraints.length ||
                sessionMemory.active_research_goal) ? (
                <section
                  className="research-memory-strip"
                  aria-label="当前研究会话上下文"
                >
                  <strong>本会话上下文</strong>
                  <div>
                    {sessionMemory.active_research_goal ? (
                      <span>目标：{sessionMemory.active_research_goal}</span>
                    ) : null}
                    {sessionMemory.session_constraints.map((item) => (
                      <span key={item.id}>约束：{item.statement}</span>
                    ))}
                    {sessionMemory.pinned_object_refs.map((item, index) => (
                      <span
                        className="research-memory-chip"
                        key={`${item.object_id || "object"}-${item.version_id || index}`}
                      >
                        <span>上下文对象 {item.display_name || `#${index + 1}`}</span>
                        {item.object_id &&
                        item.version_id &&
                        item.project_id &&
                        item.object_type && canResearch && selectedSessionIsWritable ? (
                          <button
                            type="button"
                            className="research-memory-chip-remove"
                            aria-label={`从本会话上下文移除对象 ${item.display_name || `#${index + 1}`}`}
                            onClick={() => void sessionContext.setSourcesPinned([item], false)}
                            disabled={!sessionContext.canUpdate}
                          >
                            ×
                          </button>
                        ) : null}
                      </span>
                    ))}
                    {sessionMemory.pinned_result_refs.map((resultId, index) => (
                      <span className="research-memory-chip" key={`result-${resultId}`}>
                        <span>上下文结果 {index + 1}</span>
                        {canResearch && selectedSessionIsWritable ? <button
                          type="button"
                          className="research-memory-chip-remove"
                          aria-label={`从本会话上下文移除结果 ${index + 1}`}
                          onClick={() => void sessionContext.setResultPinned(resultId, false)}
                          disabled={!sessionContext.canUpdate}
                        >
                          ×
                        </button> : null}
                      </span>
                    ))}
                  </div>
                </section>
              ) : null}
              <SessionMemoryNotice context={sessionContext} />
              {navigationTurnId &&
              (contextNavigation.context.failed || contextNavigation.context.pending) ? (
                <div className="research-memory-error" role="status">
                  <span>{contextNavigation.context.pending ? "正在读取本次上下文…" : activeAgent2ContextManifest
                    ? "上下文暂未更新，仍显示上次读取的内容。"
                    : "本次研究的上下文清单暂时无法读取"}</span>
                  {contextNavigation.context.failed ? <button
                    type="button"
                    className="product-link-button"
                    onClick={() => { contextRetryFocus.current = contextNavigation.context.scope; contextNavigation.context.retry(); }}
                  >
                    重新读取上下文
                  </button> : null}
                </div>
              ) : null}
              {activeAgent2ContextManifest ? (
                <details
                  key={contextNavigation.context.scope}
                  ref={contextManifestRef}
                  id="research-context-manifest"
                  className={conversationStyles.contextManifest}
                  aria-label="本次研究使用的上下文"
                  onKeyDown={(event) => {
                    if (event.key === "Escape") {
                      event.preventDefault();
                      event.stopPropagation();
                      closeContextPanel();
                    }
                  }}
                >
                  <summary>本次研究使用的上下文</summary>
                  {!agent2TurnId && selectedAgent2Turn ? <Link className="product-link-button" href={`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(selectedAgent2Turn.research_session_id)}?turn=${encodeURIComponent(selectedAgent2Turn.turn_id)}`}>打开这次研究</Link> : null}
                  <ResearchContextContents
                    key={activeAgent2ContextManifest.context_manifest_id}
                    manifest={activeAgent2ContextManifest}
                    manifests={agent2ContextManifests}
                    projectId={projectId}
                    resultSources={contextNavigation.context.data?.result_sources}
                    onOpenResult={() => {
                      setResultOpenRequest(value => value + 1);
                      setWorkbenchView("results");
                      setMobilePanel("workbench");
                      document.getElementById("research-detail-results-tab")?.focus();
                    }}
                    toolLabel={(id, fallback) => USER_FACING_TOOL_STEPS[id] || fallback}
                  />
                </details>
              ) : null}
              {!agent2TurnId && contextNavigation.directory.pending ? <p role="status">正在读取研究记录…</p> : null}
              {!agent2TurnId && contextNavigation.directory.failed ? <div role="alert"><p>研究记录暂时无法读取。</p><button type="button" className="product-secondary-action" onClick={contextNavigation.directory.retry}>重新读取研究记录</button></div> : null}
              {(navigationTurnId || Boolean(session?.messages?.length)) && !activeAgent2ContextManifest && !contextNavigation.context.pending && !contextNavigation.context.failed && !contextNavigation.directory.pending && !contextNavigation.directory.failed ? (
                <section className={conversationStyles.contextSelection}>
                  <h2>调用记录</h2>
                  <p>{navigationTurnId || session?.messages?.length ? "这段对话尚无已记录的调用上下文。" : "尚无调用记录。"}</p>
                </section>
              ) : null}
            </div>
            <div id="research-results-panel" className={conversationStyles.resultsPanel} role="tabpanel" aria-labelledby="research-detail-results-tab" hidden={workbenchView !== "results"} tabIndex={-1}>
            {sessionResultTurn ? <ResearchSessionResult key={`${projectId}:${sessionResultTurn.research_session_id}:${sessionResultTurn.turn_id}`}
              projectId={projectId} sessionId={sessionResultTurn.research_session_id} turnId={sessionResultTurn.turn_id}
              onProgress={setSessionResultProgress} onTerminal={() => setReloadKey(value => value + 1)} /> : null}
            {!agent2TurnId && runReadFailures.length > 0 ? (
              <div className="research-result-read-error" role="alert">
                <p>暂时无法读取：{runReadFailures.join("、")}。</p>
                {runReadFailures.includes("运行详情") ? <p>进度暂未确认，当前显示上次读取的状态。</p> : null}
                <p>已打开的内容仍可查看。</p>
                <button type="button" className="product-secondary-action" disabled={runReadPending} onClick={() => { setRunReadPending(true); setReloadKey((value) => value + 1); }}>{runReadPending ? "正在读取…" : "重新读取分析结果"}</button>
              </div>
            ) : null}
            {hasAuthoritativeTurnPresentation ? (
              <>
                <Agent2ScientificPresentation
                  turnId={agent2TurnId as string}
                  resultTarget={resultTargetSnapshotId || resultTargetItemId ? {
                    snapshotId: resultTargetSnapshotId || "", itemId: resultTargetItemId || "", requestKey: resultOpenRequest,
                  } : undefined}
                  progress={activeAgent2Progress}
                  projectId={projectId}
                  sessionId={session?.id}
                  context={sessionContext}
                  onContinue={selectedSessionIsWritable && canResearch ? continueAgent2Research : undefined}
                  onEdit={selectedSessionIsWritable && canResearch ? editAgent2Turn : undefined}
                  onRun={selectedSessionIsWritable && canResearch ? runResultResearch : undefined}
                  canModify={selectedSessionIsWritable && canResearch}
                />
                <LiteratureEvidencePanel
                  projectId={projectId}
                  turnId={agent2TurnId as string}
                />
              </>
            ) : null}
            {agent2TurnId && !hasAuthoritativeTurnPresentation ? <ResearchTurnResultState
              turnId={agent2TurnId} progress={activeAgent2Progress}
              unconfirmed={agent2RecoveryState.turnId === agent2TurnId && agent2RecoveryState.status !== "connected"}
              onOpenTimeline={() => {
                const opener = document.activeElement;
                setMobilePanel("timeline");
                window.requestAnimationFrame(() => {
                  if (document.activeElement !== opener && document.activeElement !== document.body) return;
                  const target = conversationHistoryRef.current?.querySelector<HTMLElement>(".research-execution-activity") || conversationHistoryRef.current;
                  if (target) { target.tabIndex = -1; target.focus(); target.scrollIntoView?.({ block: "nearest" }); }
                });
              }}
            /> : null}
            {!agent2TurnId && !sessionResultTurn && !history ? (
              <div className="research-state idle" role="status">
                <h2>{projectHistoryReadState === "error" ? "项目数据暂时无法读取" : "正在读取项目数据…"}</h2>
                {projectHistoryReadState === "error" ? <button type="button" className="product-secondary-action" onClick={() => setReloadKey((value) => value + 1)}>重新读取项目数据</button> : null}
              </div>
            ) : null}
            {!agent2TurnId && !sessionResultTurn && history && showResearchStarter && hasExplicitScientificHandoff ? (
              <section className="research-state idle"><h2>尚无分析结果</h2></section>
            ) : !agent2TurnId && !sessionResultTurn && history ? (
              <ResearchWorkbenchContent
                projectId={projectId}
                state={state}
                scope={scope}
                job={job}
                events={events}
                artifacts={artifacts}
                interpretation={interpretation}
                interpretationStatus={interpretationStatus}
                evidence={evidence}
                error={error}
                runResolutionState={runResolutionState}
                resultsUnavailable={runReadFailures.includes("科学结果")}
                history={history}
                onTryQuestion={trySuggestedQuestion}
                onRestoreQuestion={canResearch ? restoreRunQuestion : undefined}
              />
            ) : null}
            </div>
          </section>
        </section>
      </ProductShell>
    </RequireProductAuth>
  );
}

export function mergeJobEvents(
  current: JobEvent[],
  incoming: JobEvent[],
): JobEvent[] {
  const byIdentity = new Map<string, JobEvent>();
  for (const event of [...current, ...incoming]) {
    const identity = String(
      event.id || `${event.seq || 0}:${event.eventType || "event"}`,
    );
    byIdentity.set(identity, event);
  }
  return [...byIdentity.values()].sort(
    (left, right) => (left.seq || 0) - (right.seq || 0),
  );
}

export function mergeArtifacts(
  current: Artifact[],
  incoming: Artifact[],
): Artifact[] {
  const byIdentity = new Map<string, Artifact>();
  for (const artifact of [...current, ...incoming]) {
    const identity =
      artifactReference(artifact) ||
      `${artifact.type || "artifact"}:${JSON.stringify(artifact)}`;
    byIdentity.set(identity, artifact);
  }
  return [...byIdentity.values()].sort((left, right) =>
    artifactReference(left).localeCompare(artifactReference(right)),
  );
}

async function createScientificInterpretation(jobId: string, planHash: string, signal: AbortSignal) {
  const validate = (interpretation: GroundedScientificInterpretation) => {
    if (!interpretation.interpretationId || (interpretation.sourceJobId && interpretation.sourceJobId !== jobId) ||
        (interpretation.sourcePlanHash && interpretation.sourcePlanHash !== planHash)) throw new Error("Interpretation source mismatch");
  };
  const saved = await readSessionRequest((requestSignal) => getPlannerJobInterpretations(jobId, { signal: requestSignal }), signal);
  if (saved.jobId && saved.jobId !== jobId) throw new Error("Job interpretations mismatch");
  const existing = saved.interpretations.at(-1);
  if (existing) { validate(existing); return { interpretation: existing }; }
  const create = async (mode: "STRICT_PROVIDER" | "DETERMINISTIC", idempotencyKey: string) => {
    const value = await readSessionRequest((requestSignal) => createPlannerJobInterpretation(jobId, planHash, {
      mode, idempotencyKey, signal: requestSignal,
    }), signal);
    if ((value.sourceJobId && value.sourceJobId !== jobId) ||
        (value.sourcePlanHash && value.sourcePlanHash !== planHash)) throw new Error("Interpretation response mismatch");
    if (value.interpretation) validate(value.interpretation);
    return value;
  };
  const strict = await create("STRICT_PROVIDER", `research-scientific-interpretation:${jobId}`);
  if (strict.interpretation) return strict;
  // A transport timeout does not prove the original write failed. Only a
  // definitive provider/validation outcome permits a different fallback.
  if (!["PROVIDER_FAILED", "VALIDATION_FAILED"].includes(strict.outcome)) return strict;
  return create("DETERMINISTIC", `research-deterministic-interpretation:${jobId}`);
}

function ResearchStarter({
  projectId,
  datasetCount,
  selectedDataset,
  canResearch,
  projectStatus,
  prompts,
  onTryQuestion,
}: {
  projectId: string;
  datasetCount: number;
  selectedDataset?: { id: string; name: string; sampleRef?: string; sourceSelectionToken?: string; hasSourceSelection?: boolean };
  canResearch: boolean;
  projectStatus: string;
  prompts: ResearchStarterPrompt[];
  onTryQuestion: (question: string) => void;
}) {
  // Carry the original dataset version back to Data. Research admission still
  // resolves scientific authority through the existing dataset bridge.
  let returnSelection = "";
  if (selectedDataset?.sourceSelectionToken && selectedDataset.sampleRef) {
    try {
      const selection = decodeWorkspaceSelectionUrl(selectedDataset.sourceSelectionToken);
      const primary = selection.primary;
      if (!selection.cleared && selection.compatibility === "EXACT" && primary?.kind === "DATASET_SAMPLE"
        && primary.projectId === projectId && primary.datasetId === selectedDataset.id
        && primary.sampleRef === selectedDataset.sampleRef) returnSelection = selectedDataset.sourceSelectionToken;
    } catch { /* Invalid navigation context must not select a different source. */ }
  }
  if (canResearch && !selectedDataset) {
    return <section className="research-starter" aria-labelledby="research-starter-title">
      <h2 id="research-starter-title">想研究什么？</h2>
      <div className="research-starter-questions">
        {["解释元素周期表的排列规律", "共价键、离子键和金属键有什么区别？"].map(question =>
          <button key={question} type="button" onClick={() => onTryQuestion(question)}>{question}</button>
        )}
      </div>
    </section>;
  }
  if (!datasetCount) {
    const projectIsArchived = projectStatus === "archived";
    const projectIsTrashed = projectStatus === "trashed";
    const projectIsLifecycleBlocked = projectIsArchived || projectIsTrashed;
    return (
      <section
        className="research-starter"
        aria-labelledby="research-starter-title"
      >
        <p className="product-kicker">研究起点</p>
        <h2 id="research-starter-title">
          {projectIsArchived
            ? "这个项目已归档"
            : projectIsTrashed
              ? "这个项目已移入回收站"
              : canResearch
                ? "先从项目数据开始"
                : "这个项目还没有可研究的数据"}
        </h2>
        <p>
          {projectIsLifecycleBlocked
            ? "当前不能导入数据或发起新研究；已有数据与历史研究仍可继续查看。"
            : canResearch
              ? "前往数据平台导入支持的材料数据，或选择已有数据进入研究。"
              : "你没有此项目的写入权限，但仍可前往数据平台查看现有数据状态。"}
        </p>
        <Link
          className={
            canResearch
              ? "product-primary-action research-starter-upload"
              : "product-secondary-action research-starter-upload"
          }
          href={`/projects/${projectId}/data`}
        >
          {canResearch
            ? "打开数据平台"
            : projectIsLifecycleBlocked
              ? "查看保留的数据"
              : "查看数据平台"}
        </Link>
        {!canResearch ? (
          <p className="research-starter-readonly" role="note">
            {projectIsLifecycleBlocked
              ? "项目当前不可写；恢复为活跃状态后才能继续导入与研究。"
              : "此项目为只读"}
          </p>
        ) : null}
      </section>
    );
  }
  return (
    <section
      className="research-starter"
      aria-labelledby="research-starter-title"
    >
      <p className="product-kicker">研究起点</p>
      <h2 id="research-starter-title">{selectedDataset ? `围绕 ${selectedDataset.name} 开始研究` : `从 ${datasetCount} 个项目数据集开始`}</h2>
      {selectedDataset && !selectedDataset.hasSourceSelection ? <div className="research-starter-scope" role="note" aria-label="本次研究的数据范围">
        <span>{selectedDataset.sampleRef ? "已指定 1 个样本" : "已指定数据集"}</span>
        {selectedDataset.sampleRef ? <code>{selectedDataset.sampleRef}</code> : null}
        <Link href={`/projects/${projectId}/data?dataset=${encodeURIComponent(selectedDataset.id)}${selectedDataset.sampleRef ? `&sample=${encodeURIComponent(selectedDataset.sampleRef)}` : ""}${returnSelection ? `&selection=${encodeURIComponent(returnSelection)}` : ""}`}>查看来源数据</Link>
      </div> : null}
      <p>
        {canResearch
          ? "选择一个与当前数据匹配的方向；问题只会填入下方输入框，由你确认后开始分析。"
          : "你可以查看项目数据与已有结果，但当前权限不能发起新的研究。"}
      </p>
      {canResearch ? (
        <div className="research-starter-directions">
          <strong>当前可研究方向</strong>
          <div className="research-starter-questions">
            {prompts.map((prompt) => (
              <button
                key={prompt.id}
                type="button"
                onClick={() => onTryQuestion(prompt.question)}
              >
                <span>{prompt.question}</span>
                <small>填入问题框</small>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <p className="research-starter-readonly" role="note">
          此项目为只读
        </p>
      )}
    </section>
  );
}

function ResearchWorkbenchContent({
  projectId,
  state,
  scope,
  job,
  events,
  artifacts,
  interpretation,
  interpretationStatus,
  evidence,
  error,
  runResolutionState,
  resultsUnavailable = false,
  history,
  onTryQuestion,
  onRestoreQuestion,
}: {
  projectId: string;
  state: ResearchState;
  scope: ScopeResolution | null;
  job: PlannerJobCreateResult | null;
  events: JobEvent[];
  artifacts: Artifact[];
  interpretation: GroundedScientificInterpretation | null;
  interpretationStatus: "idle" | "loading" | "ready" | "limited" | "error";
  evidence: InterpretationEvidenceResponse | null;
  error: string;
  runResolutionState: "idle" | "loading" | "settled";
  resultsUnavailable?: boolean;
  history: ProjectHistory | null;
  onTryQuestion: (question: string) => void;
  onRestoreQuestion?: () => void;
}) {
  const resultArtifacts = projectScientificArtifacts(artifacts);
  const [highlightedArtifactId, setHighlightedArtifactId] = useState<
    string | null
  >(null);
  if (state === "unsupported")
    return (
      <div className="research-state unsupported">
        <p className="product-kicker">无法进行此分析</p>
        <h2>当前数据缺少完成这项分析所需的科学属性。</h2>
        <p>
          当前可用：
          {scope?.available_semantics?.join("、") || "已识别的材料属性"}
        </p>
        <div className="product-row-actions">
          <button
            type="button"
            className="product-secondary-action"
            onClick={() => onTryQuestion("查看 band gap 分布")}
          >
            查看带隙分布
          </button>
          <button
            type="button"
            className="product-secondary-action"
            onClick={() =>
              onTryQuestion("比较 formation energy 与 density 的关系")
            }
          >
            比较形成能与密度
          </button>
        </div>
        <details>
          <summary>技术详情</summary>
          <p>未创建分析方案或作业。</p>
        </details>
      </div>
    );
  if (state === "capability-clarification")
    return (
      <CapabilityClarificationState
        code={job ? plannerFailureCode(job) : ""}
        onTryQuestion={onTryQuestion}
      />
    );
  if (state === "idle")
    return (
      <div className="research-state idle">
        <h2>可用数据</h2>
        <p>打开数据集查看内容、选择样本，再围绕具体数据继续研究。</p>
        <section className="research-idle-section">
          <header>
            <span>{history?.datasets.length || 0} 个数据集</span>
            <Link href={`/projects/${projectId}/data`}>查看全部数据</Link>
          </header>
          {history?.datasets.slice(0, 4).map((dataset) => (
            <Link
              key={dataset.datasetId}
              href={`/projects/${projectId}/data?dataset=${dataset.datasetId}`}
              className="research-context-row"
            >
              <div>
                <strong>{dataset.name}</strong>
                <span>
                {dataset.profile?.rowCount ??
                  dataset.profile?.objectCount ??
                  "—"}{" "}
                个记录 ·{" "}
                {researchDatasetTypeLabel(dataset.profile?.datasetType)}
                </span>
              </div>
              <span aria-hidden="true">查看 →</span>
            </Link>
          ))}
          {!history?.datasets.length && (
            <p className="research-context-empty">
              上传数据后，可在这里查看当前研究范围。
            </p>
          )}
        </section>
      </div>
    );
  const groundedNarrative = groundedEvidenceNarrative(evidence);
  const primaryArtifact =
    resultArtifacts.find(
      (artifact) => artifactReference(artifact) === highlightedArtifactId,
    ) ||
    resultArtifacts.find(
      (artifact) =>
        artifact.resultRole === "PRIMARY_FIGURE" ||
        artifact.resultRole === "PRIMARY_TABLE",
    ) ||
    resultArtifacts[0];
  const supportingArtifacts = resultArtifacts.filter(
    (artifact) => artifact !== primaryArtifact,
  );
  const datasetId = scope?.dataset_id || job?.plan?.datasetId || undefined;
  const jobId = job?.job_id || undefined;
  const technical = researchTechnicalSummary(job, artifacts, resultArtifacts);
  return (
    <div className={"research-result-state " + state}>
      <header className="workbench-heading">
        <div>
          <p className="product-kicker">
            {state === "running"
              ? "正在分析"
              : state === "complete"
                ? "科学结果"
                : state === "partial"
                  ? "部分结果"
                  : state === "canceled"
                    ? "分析已取消"
                  : "分析未完成"}
          </p>
          <h2>
            {scientificResultTitle(
              job?.plan?.goal || null,
              artifacts,
              interpretation,
            )}
          </h2>
        </div>
        <div className="workbench-heading-actions">
          {datasetId ? (
            <Link
              className="product-secondary-action"
              href={`/projects/${projectId}/data?dataset=${datasetId}`}
            >
              查看数据
            </Link>
          ) : null}
          {(state === "complete" || state === "partial") && jobId ? (
            <Link
              className="product-secondary-action"
              href={`/projects/${projectId}/reports/${jobId}`}
            >
              打开分析报告
            </Link>
          ) : null}
        </div>
      </header>
      {state === "failed" && jobId ? (
        <section className="research-run-recovery" role="status" aria-label="分析失败与恢复">
          <p>{researchRunFailureMessage(events)}</p>
          <p>{resultArtifacts.length ? "已保存的科学输出仍保留在下方，可继续查看。" : "本次运行尚无可展示的科学结果。"}</p>
          {onRestoreQuestion ? <button type="button" className="product-secondary-action" onClick={onRestoreQuestion}>修改问题后重试</button> : null}
        </section>
      ) : null}
      <section className="live-results">
        {state !== "failed" || resultArtifacts.length ? <div className="result-heading">
          <h3>{state === "running" ? "本次分析" : "主要结果"}</h3>
          <span>
            {resultArtifacts.length
              ? `${resultArtifacts.length} 个科学输出`
              : scope?.dataset_name || ""}
          </span>
        </div> : null}
        {primaryArtifact ? (
          <ResearchArtifactFigure
            artifact={primaryArtifact}
            highlighted={
              artifactReference(primaryArtifact) === highlightedArtifactId
            }
            projectId={projectId}
            datasetId={datasetId}
            jobId={jobId}
            artifacts={artifacts}
          />
        ) : runResolutionState === "loading" ? (
          <div className="result-empty product-loading" role="status">
            正在读取分析结果…
          </div>
        ) : resultsUnavailable ? (
          <div className="result-empty">科学结果暂时无法读取，请重试。</div>
        ) : state === "failed" ? null : (
          <div className="result-empty">
            {state === "running" ? (
              <>
                结果生成后会在这里显示。
                <br />
                当前使用：{scope?.dataset_name || "已选择的数据"}
              </>
            ) : (
              "当前没有可展示的结果。"
            )}
          </div>
        )}
        {supportingArtifacts.length ? (
          <section className="report-supporting-results" aria-label="补充结果">
            {supportingArtifacts.map((artifact) => (
              <details key={artifact.artifactId || artifact.id} className="report-supplementary-result">
                <summary>{artifact.resultTitle}</summary>
                <ResearchArtifactFigure
                  showHeading={false}
                  artifact={artifact}
                  highlighted={
                    artifactReference(artifact) === highlightedArtifactId
                  }
                  projectId={projectId}
                  datasetId={datasetId}
                  jobId={jobId}
                  artifacts={artifacts}
                />
              </details>
            ))}
          </section>
        ) : null}
        {(state === "complete" || state === "partial") && (
          <section className="finding-block">
            <h3>
              {resultArtifacts.length ||
              userFacingClaims(interpretation).length ||
              groundedNarrative.finding
                ? "主要发现"
                : "状态说明"}
            </h3>
            {interpretationStatus === "loading" ? (
              <p role="status">正在整理科学结论…</p>
            ) : userFacingClaims(interpretation).length ? (
              <ul className="research-findings">
                {userFacingClaims(interpretation)
                  .slice(0, 8)
                  .map((claim) => (
                    <li key={claim.claimId}>
                      <strong>
                        {claim.claimType === "LIMITATION" ? "限制" : "观察"}
                      </strong>
                      <p>{claim.renderedText}</p>
                    </li>
                  ))}
              </ul>
            ) : groundedNarrative.finding ? (
              <p>{groundedNarrative.finding}</p>
            ) : (
              <p>
                {resultArtifacts.length
                  ? "本次分析已生成可复核的图表与数据表；当前解释没有足够的用户级科学结论。"
                  : "当前未读取到可展示的科学输出；请打开分析报告查看执行状态与依据。"}
              </p>
            )}
            <h3>限制</h3>
            {userFacingLimitations(interpretation).length ? (
              <ul>
                {userFacingLimitations(interpretation).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p>
                {groundedNarrative.limitation ||
                  (interpretationStatus === "error"
                    ? resultArtifacts.length
                      ? "科学结论暂时无法读取；结果仍可查看。"
                      : "科学结论暂时无法读取；请从分析报告核对本次运行。"
                    : resultArtifacts.length
                      ? "解释仅适用于本次分析所使用的数据与证据。"
                      : "当前没有可展示的科学输出；结果解释需要先读取持久化输出。")}
              </p>
            )}
            {evidence?.evidenceItems?.length ? (
              <details className="research-evidence">
                <summary>依据 · {evidence.evidenceItems.length} 项</summary>
                <ul>
                  {evidence.evidenceItems.slice(0, 12).map((item) => {
                    const target = resultArtifacts.find(
                      (artifact) =>
                        artifactReference(artifact) === item.sourceArtifactId,
                    );
                    return (
                      <li key={item.evidenceItemId}>
                        <strong>{evidenceLabel(item.semanticRole)}</strong>
                        <span>{displayEvidenceValue(item.displayValue)}</span>
                        <small>{evidenceProvenanceSummary(item)}</small>
                        {target ? (
                          <button
                            type="button"
                            className="product-link-button"
                            onClick={() => {
                              setHighlightedArtifactId(
                                artifactReference(target),
                              );
                              window.requestAnimationFrame(() =>
                                document
                                  .getElementById(artifactDomId(target))
                                  ?.scrollIntoView({ block: "center" }),
                              );
                            }}
                          >
                            在结果中查看
                          </button>
                        ) : null}
                      </li>
                    );
                  })}
                </ul>
              </details>
            ) : null}
            {evidence?.sourceObjectRefs?.length ? (
              <details className="research-evidence">
                <summary>
                  精确科学来源 · {evidence.sourceObjectRefs.length} 个版本
                </summary>
                <ul>
                  {evidence.sourceObjectRefs.map((source) => (
                    <li key={`${source.objectId}:${source.versionId}`}>
                      <strong>
                        {source.displayName ||
                          source.objectType ||
                          "ScientificObject"}
                      </strong>
                      <span>
                        {source.versionNo
                          ? `版本 ${source.versionNo}`
                          : "已锁定精确版本"}
                        {source.isCurrentVersion === false ? " · 历史版本" : ""}
                      </span>
                      <small>本次结果不会自动切换到更新版本。</small>
                    </li>
                  ))}
                </ul>
              </details>
            ) : null}
            <details>
              <summary>来源与过程</summary>
              <p>
                {interpretation
                  ? "结论来自本次分析的已验证结果与依据。"
                  : "分析方法、来源数据与输出记录可继续查看。"}
              </p>
            </details>
            <details className="research-technical-details">
              <summary>技术详情</summary>
              <dl>
                <div>
                  <dt>运行 ID</dt>
                  <dd>
                    <code>{compactTechnicalId(technical.runId)}</code>
                  </dd>
                </div>
                <div>
                  <dt>方案 ID</dt>
                  <dd>
                    <code>{compactTechnicalId(technical.planId)}</code>
                  </dd>
                </div>
                <div>
                  <dt>输出</dt>
                  <dd>
                    {technical.outputCount
                      ? `${technical.outputCount} 个可查看结果`
                      : "暂无可查看结果"}
                  </dd>
                </div>
                {evidence?.sourceObjectRefs?.length ? (
                  <div>
                    <dt>精确来源版本</dt>
                    <dd>
                      {evidence.sourceObjectRefs.map((source) => (
                        <code key={`${source.objectId}:${source.versionId}`}>
                          {compactTechnicalId(source.objectId)} / {compactTechnicalId(source.versionId)}
                        </code>
                      ))}
                    </dd>
                  </div>
                ) : null}
                <div>
                  <dt>结构化数据</dt>
                  <dd>
                    {technical.structuredOutputCount
                      ? `${technical.structuredOutputCount} 个 JSON Artifact`
                      : "当前运行没有可展示的结构化结果"}
                  </dd>
                </div>
              </dl>
              {technical.structuredOutputCount ? (
                <p className="research-technical-hint">
                  可打开上方结果的“技术详情”查看有界 JSON；示例：
                  {technical.structuredOutputLabel}。
                </p>
              ) : (
                <p className="research-technical-hint">
                  运行身份与结果状态仍保存在审计记录中；结构化数据会在结果成功加载后显示。
                </p>
              )}
            </details>
          </section>
        )}
      </section>
    </div>
  );
}

function ResearchArtifactFigure({
  artifact,
  showHeading = true,
  highlighted = false,
  projectId,
  datasetId,
  jobId,
  artifacts,
}: {
  artifact: ProjectedScientificArtifact;
  showHeading?: boolean;
  highlighted?: boolean;
  projectId: string;
  datasetId?: string;
  jobId?: string;
  artifacts: Artifact[];
}) {
  return (
    <article
      id={artifactDomId(artifact)}
      className={`artifact-result result-role-${artifact.resultRole.toLowerCase()}${highlighted ? " evidence-target" : ""}`}
    >
      {showHeading && artifact.type !== "metrics_json" ? <header className="artifact-result-heading">
        {artifactLabel(artifact.type) !== artifact.resultTitle ? <span>{artifactLabel(artifact.type)}</span> : null}
        <strong>{artifact.resultTitle}</strong>
      </header> : null}
      {jobId ? (
        <LazyScientificResultViewer
          projectId={projectId}
          datasetId={datasetId}
          jobId={jobId}
          selected={artifact}
          artifacts={artifacts}
        />
      ) : null}
    </article>
  );
}

function artifactReference(artifact: Artifact) {
  return artifact.artifactId || artifact.id || "";
}

function artifactDomId(artifact: Artifact) {
  return `research-artifact-${encodeURIComponent(artifactReference(artifact))}`;
}

function InlineRunProcess({
  state,
  scope,
  job,
  events,
  artifacts,
  error,
}: {
  state: ResearchState;
  scope: ScopeResolution | null;
  job: PlannerJobCreateResult | null;
  events: JobEvent[];
  artifacts: Artifact[];
  error: string;
}) {
  const steps = job?.plan?.steps || [];
  const datasetLabel = scientistDatasetLabel(scope);
  const complete = state === "complete";
  const completedSteps = new Set(
    events
      .filter((event) => event.eventType === "tool.completed")
      .map(eventStepId)
      .filter((value): value is string => value !== null),
  );
  const activeSteps = new Set(
    events
      .filter((event) => event.eventType === "tool.started")
      .map(eventStepId)
      .filter((value): value is string => value !== null),
  );
  const failedSteps = new Set(
    events.filter((event) => event.eventType === "tool.failed").map(eventStepId)
      .filter((value): value is string => value !== null),
  );
  return (
    <details className="timeline-run-process" open={!complete}>
      <summary>
        {complete
          ? `✓ 分析完成 · ${steps.length || events.length} 个步骤`
          : state === "unsupported"
            ? "未创建分析运行"
          : state === "capability-clarification"
            ? "需要确认分析方法"
            : state === "failed"
              ? "分析未完成 · 查看过程"
              : state === "canceled"
                ? "分析已取消 · 查看过程"
              : state === "partial"
                ? "部分完成 · 查看过程"
                : state === "planning"
                  ? "正在准备分析方案"
                  : "分析中 · 查看过程"}
      </summary>
      <div className="timeline-process-body" role="status">
        {state === "canceled" ? (
          <p>本次分析已取消，取消前已保存的输出仍可查看。</p>
        ) : null}
        {datasetLabel && (
          <p>
            ✓ 已确定分析数据
            <br />
            <small>{datasetLabel}</small>
          </p>
        )}
        {steps.length > 0 && <p>✓ 分析方案已准备</p>}
        <ol>
          {steps.map((step, index) => {
            const stepState = runProcessStepState(
              step.stepId,
              state,
              completedSteps,
              activeSteps,
              failedSteps,
            );
            const projection = userFacingPlanStep(
              step.purpose,
              step.reason,
              index,
              step.toolId,
            );
            return (
              <li key={step.stepId || index}>
                <span>
                  {stepState === "complete"
                    ? "✓"
                    : stepState === "failed"
                      ? "×"
                    : stepState === "active"
                      ? "●"
                      : "○"}
                </span>
                <div>
                  <strong>{projection.purpose}</strong>
                  {stepState === "failed" ? <small>此步骤执行失败</small> : null}
                  {projection.reason && <small>{projection.reason}</small>}
                </div>
              </li>
            );
          })}
        </ol>
        {artifacts.length > 0 && (
          <p>
            ✓ 已生成 {artifacts.length} 个结果 <span>右侧可查看</span>
          </p>
        )}
        {error && (
          <p className="product-form-error" role="alert">
            {error}
          </p>
        )}
      </div>
    </details>
  );
}

function eventStepId(event: JobEvent): string | null {
  const value = event.payload?.stepId;
  return typeof value === "string" && value.length > 0 ? value : null;
}

export function runProcessStepState(
  stepId: string | undefined,
  state: ResearchState,
  completedSteps: ReadonlySet<string>,
  activeSteps: ReadonlySet<string>,
  failedSteps: ReadonlySet<string> = new Set(),
): "complete" | "active" | "pending" | "failed" {
  if (state === "complete") return "complete";
  if (stepId && completedSteps.has(stepId)) return "complete";
  if (stepId && failedSteps.has(stepId)) return "failed";
  if (state === "running" && stepId && activeSteps.has(stepId)) return "active";
  return "pending";
}

const USER_FACING_TOOL_STEPS: Record<string, string> = {
  "structure.summary": "整理晶体结构与组成信息",
  "structure.lattice_summary": "整理晶格参数",
  "structure.spacegroup_summary": "整理空间群信息",
  "structure.composition_from_structure": "从晶体结构提取组成信息",
  "structure.brillouin_zone": "生成布里渊区与高对称路径",
  "structure.volumetric_data": "整理体数据场",
  "structure.coordination_hist": "统计结构中的配位环境",
  "structure.coordination_crystalnn": "分析 CrystalNN 配位环境",
  "structure.coordination_voronoinn": "分析 VoronoiNN 配位环境",
  "structure.local_environment_polyhedra": "分析局部环境多面体",
  "structure.xrd": "根据晶体结构生成理论 XRD 图谱",
  "structure.experimental_xrd_comparison": "比较实验峰与理论峰的位置和强度",
  "structure.rdf": "计算结构径向分布函数（RDF）",
  "structure.trajectory_viewer": "整理分子动力学轨迹",
  "structure.trajectory_import": "读取分子动力学轨迹",
  "trajectory.viewer": "整理分子动力学轨迹",
  "trajectory.rdf": "计算轨迹径向分布函数（RDF）",
  "trajectory.msd": "计算轨迹均方位移（MSD）",
  "trajectory.diffusion": "根据均方位移估计扩散行为",
  "electronic.band_structure": "整理电子能带与能量参考",
  "electronic.dos": "整理电子态密度与能量分布",
  "phonon.band": "整理声子色散关系",
  "phonon.dos": "整理声子态密度",
  "phonon.band_dos": "组合声子色散与态密度",
  "phonon.animation": "准备声子振动模式",
  "dataset.materials_explorer": "整理材料样本与属性概览",
  "dataset.composition_space": "分析材料组成空间",
  "ml.regression_evaluation": "评估材料属性回归结果",
  "ml.classification_evaluation": "评估材料分类结果",
  "ml.uncertainty_evaluation": "评估预测不确定性",
  "ml.basic_metrics": "汇总预测结果指标",
  "ml.density_scatter": "生成预测值与真实值关系图",
  "ml.error_distribution": "分析预测误差分布",
  "ml.outlier_table": "整理异常样本",
  "table.numeric_summary": "汇总数据中的数值属性",
  "table.distribution_summary": "分析材料属性的分布特征",
  "table.property_distribution": "分析材料属性的分布特征",
  "viz.scatter": "生成材料属性关系图",
  "viz.histogram": "生成材料属性分布图",
  "viz.correlation": "计算材料属性之间的相关关系",
};

const USER_FACING_TOOL_REASONS: Record<string, string> = {
  "dataset.composition_space":
    "用于观察材料组成分布，并判断是否存在值得继续研究的材料分组。",
  "dataset.materials_explorer":
    "用于先建立当前材料数据的有界概览，再判断是否需要更具体的分析。",
  "trajectory.msd":
    "用于量化原子位移随时间的变化，并为后续输运分析提供依据。",
  "trajectory.diffusion":
    "用于在已验证的时间范围内估算扩散行为。",
  "structure.experimental_xrd_comparison":
    "用于比较实验与理论衍射证据，同时保留峰匹配和物相判断的限制。",
};

export function userFacingPlanStep(
  purpose: string | null | undefined,
  reason: string | null | undefined,
  index = 0,
  toolId?: string | null,
): { purpose: string; reason?: string } {
  const rawPurpose = String(purpose || "").trim();
  const rawReason = String(reason || "").trim();
  const machinePlan =
    /validated structured AnalysisIntent|eligible registered capability|exact (?:Intent|DataProfile|Registry)|parameter-binding facts|inputref|registry\s*(?:hash|version)|plan[_\s-]?id|job[_\s-]?id/i;
  const registryPurpose = toolId ? USER_FACING_TOOL_STEPS[toolId] : undefined;
  const projectedPurpose =
    registryPurpose ||
    (machinePlan.test(rawPurpose)
      ? "整理当前数据中的科学信息"
      : rawPurpose || `科学分析步骤 ${index + 1}`);
  const projectedReason =
    (toolId ? USER_FACING_TOOL_REASONS[toolId] : undefined) ||
    (machinePlan.test(rawReason) || /^[A-Z][\s\S]*[.]$/u.test(rawReason)
      ? "已根据当前研究问题、数据范围和可用科学方法确定这一步。"
      : rawReason || undefined);
  return {
    purpose: projectedPurpose,
    ...(projectedReason ? { reason: projectedReason } : {}),
  };
}

export function scientistDatasetLabel(scope: ScopeResolution | null): string {
  if (!scope) return "";
  const name = String(
    scope.scientific_object_ref?.display_name || scope.dataset_name || "",
  ).trim();
  const datasetId = String(scope.dataset_id || "").trim();
  if (!name || (datasetId && name === datasetId)) return "当前项目材料数据";
  return name;
}

export function scientistFacingResearchRequestError(reason: unknown): string {
  if (reason instanceof PlannerApiError) {
    if (reason.status === 422) {
      return "当前分析请求缺少可验证的科学数据描述或参数。请确认所选数据已完成解析，并更具体地说明要分析的问题；没有创建运行。";
    }
    if (reason.status === 409) {
      return "当前研究状态已发生变化。已完成的科学结果仍然保留，请重新打开研究后继续。";
    }
    if (reason.status >= 500) {
      return "研究服务暂时无法完成请求。已完成的科学工作仍然保留，请稍后重试。";
    }
  }
  if (reason instanceof Error) {
    const message = reason.message.trim();
    const exposesImplementation =
      /Input should|Request failed|ValidationError|Pydantic|Traceback|status \d{3}|^[A-Z0-9_]{4,}$/iu;
    if (message && /[\u3400-\u9fff]/u.test(message) && !exposesImplementation.test(message)) {
      return message;
    }
  }
  return "研究请求暂时无法完成。请重新打开当前研究检查最新进度后再重试；已完成的科学结果仍然保留。";
}

function plannerFailureMessage(result: PlannerJobCreateResult) {
  const code = plannerFailureCode(result);
  if (code === "COORDINATION_ALGORITHM_CLARIFICATION_REQUIRED")
    return "局部环境分析需要先选择 CrystalNN 或 VoronoiNN 配位算法；当前没有创建运行。";
  if (code === "DIFFUSION_FIT_WINDOW_REQUIRED")
    return "扩散估计需要明确拟合时间窗，或明确使用当前数据提供的完整时间范围；当前没有创建运行。";
  if (code === "DIFFUSION_FIT_WINDOW_INVALID")
    return "扩散拟合时间窗无效：起始时间必须早于结束时间；当前没有创建运行。";
  if (code === "DIFFUSION_FIT_WINDOW_OUT_OF_RANGE")
    return "扩散拟合时间窗超出当前轨迹的权威时间范围；当前没有创建运行。";
  if (code === "DIFFUSION_TIME_RANGE_UNAVAILABLE")
    return "当前轨迹没有可验证的时间语义，因此不能估计扩散系数；仍可先计算不依赖时间单位的位移信息。";
  if (code.includes("CAPABILITY") || code.includes("ELIGIB"))
    return "当前已验证的分析能力无法完整覆盖这个问题。请尝试缩小问题范围，或从右侧项目数据中选择更匹配的数据。";
  if (code.includes("INTENT_UNSUPPORTED"))
    return "当前数据无法支持这项分析；没有创建分析方案或运行。";
  if (code.includes("INTENT_CLARIFICATION"))
    return "需要先确认本次分析使用的数据范围。";
  if (code.includes("DURABLE_ROOT_INPUTS"))
    return "当前数据尚未准备好用于执行分析。请等待导入完成后重试。";
  if (code.includes("PROVIDER"))
    return "研究助手暂时无法准备分析方案。请检查模型设置后重试。";
  return "分析方案未能通过当前数据和科学能力的验证；没有创建运行。";
}

function CapabilityClarificationState({
  code,
  onTryQuestion,
}: {
  code: string;
  onTryQuestion: (question: string) => void;
}) {
  const normalized = code.toUpperCase();
  if (normalized === "COORDINATION_ALGORITHM_CLARIFICATION_REQUIRED") {
    return (
      <div className="research-state research-clarification-state">
        <p className="product-kicker">需要确认分析方法</p>
        <h2>局部环境分析需要选择配位算法。</h2>
        <p>
          径向分布可以直接计算；局部环境与配位多面体会依赖所选邻居算法。请选择本次分析使用的方法。
        </p>
        <div className="research-suggestion-list" aria-label="配位算法选项">
          <button
            type="button"
            className="product-secondary-action"
            onClick={() =>
              onTryQuestion(
                "使用 CrystalNN 计算当前结构的径向分布并分析局部环境",
              )
            }
          >
            使用 CrystalNN
          </button>
          <button
            type="button"
            className="product-secondary-action"
            onClick={() =>
              onTryQuestion(
                "使用 VoronoiNN 计算当前结构的径向分布并分析局部环境",
              )
            }
          >
            使用 VoronoiNN
          </button>
        </div>
        <p className="product-form-hint">
          当前尚未创建分析运行；选择后可在左侧检查问题并提交。
        </p>
      </div>
    );
  }
  if (
    [
      "DIFFUSION_FIT_WINDOW_REQUIRED",
      "DIFFUSION_FIT_WINDOW_INVALID",
      "DIFFUSION_FIT_WINDOW_OUT_OF_RANGE",
      "DIFFUSION_TIME_RANGE_UNAVAILABLE",
    ].includes(normalized)
  ) {
    const noTimeAxis = normalized === "DIFFUSION_TIME_RANGE_UNAVAILABLE";
    return (
      <div className="research-state research-clarification-state">
        <p className="product-kicker">需要确认时间范围</p>
        <h2>
          {noTimeAxis
            ? "当前轨迹缺少可验证的时间语义。"
            : "扩散估计需要明确拟合时间窗。"}
        </h2>
        <p>
          {noTimeAxis
            ? "没有权威时间轴时，平台不会推断扩散系数或时间单位。你仍可先计算均方位移，并查看数据限制。"
            : normalized === "DIFFUSION_FIT_WINDOW_OUT_OF_RANGE"
              ? "指定时间窗超出当前轨迹范围。请选择数据实际覆盖的区间，或明确使用完整提供范围。"
              : normalized === "DIFFUSION_FIT_WINDOW_INVALID"
                ? "起始时间必须早于结束时间。请在问题中提供一个有效区间，或明确使用完整提供范围。"
                : "为了避免平台替你选择科学结论，请指定拟合起止时间，或明确接受完整提供范围并保留拟合诊断。"}
        </p>
        <div className="research-suggestion-list" aria-label="轨迹分析范围选项">
          {!noTimeAxis ? (
            <button
              type="button"
              className="product-secondary-action"
              onClick={() =>
                onTryQuestion(
                  "使用当前轨迹完整提供的时间范围计算 MSD，并仅在拟合诊断满足条件时估计扩散系数；报告拟合窗口、拟合点数、R²、异常扩散指数和单位。",
                )
              }
            >
              使用完整时间范围
            </button>
          ) : null}
          <button
            type="button"
            className="product-secondary-action"
            onClick={() =>
              onTryQuestion(
                "先计算当前轨迹的均方位移（MSD），报告可用时间范围、末端 MSD、证据和限制，不估计扩散系数。",
              )
            }
          >
            仅计算 MSD
          </button>
        </div>
        <p className="product-form-hint">
          选择只会填入研究问题，不会自动开始计算；请在左侧核对后提交。
        </p>
      </div>
    );
  }
  return (
    <div className="research-state research-clarification-state">
      <p className="product-kicker">需要确认分析范围</p>
      <h2>当前问题还缺少一个会改变科学方法的选择。</h2>
      <p>请在左侧问题中补充方法、范围或数据选择。确认前不会创建分析运行。</p>
    </div>
  );
}

function plannerFailureCode(result: PlannerJobCreateResult) {
  const errorCode = String(result.error_code || "").toUpperCase();
  const diagnosticCode = String(
    result.validation_errors?.[0]?.code || "",
  ).toUpperCase();
  return [
    "NEEDS_CLARIFICATION",
    "CAPABILITY_MISMATCH",
    "VALIDATION_FAILED",
  ].includes(errorCode) && diagnosticCode
    ? diagnosticCode
    : errorCode || diagnosticCode || "UNKNOWN";
}

function researchSessionStatusLabel(status?: string | null) {
  const normalized = String(status || "").toLowerCase();
  if (normalized === "active") return "可继续";
  if (normalized === "trashed") return "在回收站";
  if (["queued", "running", "planning"].includes(normalized)) return "进行中";
  if (["completed", "complete", "succeeded", "success"].includes(normalized))
    return "已完成";
  if (normalized === "partial_success" || normalized === "partial")
    return "部分完成";
  if (normalized === "failed") return "未完成";
  if (normalized === "archived") return "已归档";
  return "研究记录";
}

function effectiveResearchRunStatus(run: {
  status?: string | null;
  researchTurnStatus?: string | null;
}) {
  const normalized = String(
    run.researchTurnStatus || run.status || "",
  ).toLowerCase();
  if (["completed", "complete", "succeeded", "success"].includes(normalized))
    return "completed";
  if (["partial", "partial_success"].includes(normalized)) return "partial";
  if (["failed", "rejected"].includes(normalized)) return "failed";
  if (["canceled", "cancelled"].includes(normalized)) return "canceled";
  return normalized;
}

function researchDatasetTypeLabel(datasetType?: string | null) {
  const normalized = String(datasetType || "").toLowerCase();
  if (!normalized) return "科学数据";
  if (
    normalized.includes("table") ||
    normalized.includes("csv") ||
    normalized.includes("dataframe")
  )
    return "材料数据表";
  if (normalized.includes("structure") || normalized.includes("atoms"))
    return "原子结构";
  if (normalized.includes("trajectory")) return "原子轨迹";
  if (normalized.includes("xrd")) return "XRD 数据";
  if (
    normalized.includes("electronic") ||
    normalized.includes("band") ||
    normalized.includes("dos")
  )
    return "电子结构数据";
  if (normalized.includes("phonon")) return "声子数据";
  if (normalized.includes("volumetric") || normalized.includes("cube"))
    return "体数据";
  return "科学数据";
}

function isPrimaryScientificArtifact(artifact: Artifact) {
  return !["recipe_json", "summary_md", "table_csv"].includes(
    String(artifact.type || "").toLowerCase(),
  );
}

function userFacingClaims(
  interpretation: GroundedScientificInterpretation | null,
) {
  return (
    interpretation?.claims.filter(
      (claim) =>
        !/(?:reported\s+(?:count|category|value|range)|artifact\s*\(s\)|projector|schema|contract|toolcall|inputref|plan[_\s-]?id|job[_\s-]?id|registry\s*(?:hash|version))/i.test(
          claim.renderedText,
        ) && !/(?:^|:)[a-f0-9]{24,}/i.test(claim.renderedText),
    ) || []
  );
}

export function displayResearchMessage(message: ResearchMessage): string {
  if (message.role !== "assistant") return message.content;
  if (message.payload?.messageKind === "ASSISTANT_FINAL" &&
      (message.payload.source !== "agent2_scientific_interpreter" || message.payload.responseFormat === "markdown")) {
    return message.content;
  }
  let text = message.content;
  if (message.payload?.messageKind === "ASSISTANT_FINAL"
      && message.payload.source === "agent2_scientific_interpreter") {
    const scientificBody = scientificNarrativeText(text)
      .replace(/^[^\n]*\n/u, "")
      .split(/\n\s*(?:限制：|可考虑的后续方向：)/u, 1)[0];
    const cleanScientificText = (value: string) => value
      .replace(/\s+(?:fact|evidence|limitation|figure)\.[a-z0-9.]+/giu, "")
      .replace(/（step_[^)]+）/giu, "")
      .trim();
    const boundedFindings = scientificBody
      .split("\n")
      .filter((line) => /^-\s+/u.test(line))
      .map((line) => cleanScientificText(line.replace(/^-\s+/u, "")))
      .map((line) => line.match(/^[^。！？!?]*[。！？!?]/u)?.[0]?.trim() || line)
      .filter(Boolean)
      .slice(0, 2);
    const answer = cleanScientificText(scientificBody.split(/\n\s*-/u, 1)[0]);
    const sentences = answer
      .match(/[^。！？!?]*[。！？!?]/gu)
      ?.map((sentence) => sentence.trim())
      .filter((sentence) => !/^该事实来自证据/u.test(sentence))
      .slice(0, 2)
      .join("")
      .trim() || answer;
    const summary = boundedFindings.length ? boundedFindings.join("") : sentences;
    if (summary) {
      text = `${summary}\n\n完整结构化结果已在右侧工作台提供。`;
    }
  }
  // Keep legacy persisted projections readable without rewriting historical
  // Messages. Dataset identifiers remain exact, but the surrounding sentence
  // uses the current Chinese research-workbench vocabulary.
  text = text.replace(
    /^我会使用\s*(.+?)\s*完成(?:本次)?分析。/u,
    "本次分析将以数据集“$1”为范围。",
  );
  text = text.replace(/^当前\s+当前项目材料数据/u, "当前项目材料数据");
  text = text.replace(
    /Satisfy the validated structured AnalysisIntent with an eligible registered capability\.?/gi,
    "执行已验证的科学分析步骤。",
  );
  text = text.replace(
    /分析已经完成。[\s\S]*?可以在右侧查看科学结果、依据与来源。/gi,
    "分析已经完成。\n\n可以在右侧查看科学结果、依据与来源。",
  );
  text = text.replace(
    /(?:dataset\s+reported\s+(?:count|category|value)|artifact\s*\(s\)|projector|schema|contract|toolcall|inputref|plan[_\s-]?id|job[_\s-]?id)[^。\n]*[。]?/gi,
    "",
  );
  return formatScientificNarrativeNumbers(text
    .replace(/[ \t]{2,}/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim());
}

function userFacingLimitations(
  interpretation: GroundedScientificInterpretation | null,
) {
  return (
    interpretation?.globalLimitations.filter(
      (item) =>
        !/(?:reported\s+(?:count|category|value)|artifact\s*\(s\)|projector|schema|contract|toolcall|inputref|plan[_\s-]?id|job[_\s-]?id|registry\s*(?:hash|version))/i.test(
          item,
        ),
    ) || []
  );
}

export function groundedEvidenceNarrative(
  evidence: InterpretationEvidenceResponse | null,
) {
  const values = new Map(
    (evidence?.evidenceItems || []).map((item) => [
      item.semanticRole,
      item.displayValue,
    ]),
  );
  const value = (role: string) => values.get(role) || "";
  const number = (role: string) => Number.parseFloat(value(role));
  const hasNumbers = (...roles: string[]) =>
    roles.every((role) => Number.isFinite(number(role)));
  const algorithmLabel = (raw: string) =>
    raw.toLowerCase().includes("crystalnn")
      ? "CrystalNN"
      : raw.toLowerCase().includes("voronoinn")
        ? "VoronoiNN"
        : raw;
  if (
    value("local_environment.source_algorithm") &&
    hasNumbers(
      "local_environment.evaluated_sites",
      "local_environment.classified_sites",
      "local_environment.ambiguous_sites",
      "local_environment.unclassified_sites",
      "local_environment.coverage",
    )
  ) {
    const evaluated = number("local_environment.evaluated_sites");
    const classified = number("local_environment.classified_sites");
    const ambiguous = number("local_environment.ambiguous_sites");
    const unclassified = number("local_environment.unclassified_sites");
    return {
      finding: `${algorithmLabel(value("local_environment.source_algorithm"))} 局部环境分析评估了 ${evaluated} 个位点，其中 ${classified} 个完成分类、${ambiguous} 个存在歧义、${unclassified} 个未分类；覆盖率为 ${formatPercent(number("local_environment.coverage"))}。`,
      limitation:
        "局部环境分类来自所选配位算法与几何参考匹配，不等同于确定的化学键或价态判定。",
    };
  }
  if (
    value("coordination.algorithm") &&
    hasNumbers(
      "coordination.total_sites",
      "coordination.successful_sites",
      "coordination.coverage",
    )
  ) {
    const ranges = [
      value("coordination.value_range")
        ? `配位值范围为 ${displayEvidenceValue(value("coordination.value_range"))}`
        : "",
      value("coordination.distance_range")
        ? `邻居距离范围为 ${displayEvidenceValue(value("coordination.distance_range"))}`
        : "",
    ].filter(Boolean);
    const warningCodes = new Set(
      (evidence?.evidenceItems || []).flatMap((item) => item.warnings || []),
    );
    const caveats = [
      warningCodes.has("CRYSTALNN_OXIDATION_STATES_NOT_DECLARED")
        ? "当前输入未声明氧化态"
        : "",
      warningCodes.has("CRYSTALNN_RADIUS_FALLBACK_USED")
        ? "部分判断使用了半径回退规则"
        : "",
    ].filter(Boolean);
    return {
      finding: `${algorithmLabel(value("coordination.algorithm"))} 在 ${number("coordination.successful_sites")}/${number("coordination.total_sites")} 个位点完成配位分析，覆盖率为 ${formatPercent(number("coordination.coverage"))}${ranges.length ? `；${ranges.join("，")}` : ""}。`,
      limitation: `${caveats.length ? `${caveats.join("；")}。` : ""}配位结果依赖所选算法、参数与当前结构，不作为确定化学键结论。`,
    };
  }
  if (
    hasNumbers(
      "xrd.experimental_detected_peaks",
      "xrd.theoretical_peaks",
      "xrd.matched_pairs",
      "xrd.matching_tolerance",
      "xrd.residual.mae",
      "xrd.residual.maximum_residual",
    )
  ) {
    return {
      finding: `在 ${number("xrd.matching_tolerance")}° 的匹配容差内，${number("xrd.experimental_detected_peaks")} 个实验峰中有 ${number("xrd.matched_pairs")} 个与 ${number("xrd.theoretical_peaks")} 个理论峰对应；已匹配峰位的平均绝对偏差为 ${number("xrd.residual.mae")}°，最大偏差为 ${number("xrd.residual.maximum_residual")}°。`,
      limitation: `仍有 ${number("xrd.unmatched_experimental")} 个实验峰和 ${number("xrd.unmatched_theoretical")} 个理论峰未匹配；该对比不能单独作为物相确认或 Rietveld 精修结论。`,
    };
  }
  if (
    hasNumbers(
      "dataset.sample_count",
      "composition.valid_count",
      "composition.unique_formula_count",
    )
  ) {
    return {
      finding: `当前材料数据包含 ${number("dataset.sample_count")} 个样本，其中 ${number("composition.valid_count")} 个样本具有可解析化学式，共覆盖 ${number("composition.unique_formula_count")} 个唯一化学式。`,
      limitation: `材料性质字段数量为 ${number("dataset.property_count")}；数据质量概览不替代针对具体性质或结构的科学分析。`,
    };
  }
  const correlation = [...values.entries()].find(([role]) =>
    role.startsWith("correlation."),
  );
  if (correlation && Number.isFinite(Number.parseFloat(correlation[1]))) {
    const fields = correlation[0]
      .replace("correlation.", "")
      .split(".")
      .map((item) => item.replaceAll("_", " "));
    return {
      finding: `${fields.join(" 与 ")} 的 Pearson 相关系数为 ${Number.parseFloat(correlation[1])}。`,
      limitation:
        "相关性描述当前样本中的线性关系，不代表因果关系，也不替代异常值、分组效应和数据质量复核。",
    };
  }
  if (value("structure.formula") && hasNumbers("structure.site_count")) {
    const lattice = [
      value("structure.lattice.a"),
      value("structure.lattice.b"),
      value("structure.lattice.c"),
    ]
      .filter(Boolean)
      .map(displayEvidenceValue);
    return {
      finding: `${value("structure.formula")} 结构包含 ${number("structure.site_count")} 个位点${lattice.length === 3 ? `，晶格参数 a、b、c 分别为 ${lattice.join("、")}` : ""}。`,
      limitation:
        "结构摘要仅陈述当前标准化结构中的几何事实；未提供的信息不会由界面推断。",
    };
  }
  if (value("trajectory.msd.last_total") && value("trajectory.msd.last_lag")) {
    const status = value("trajectory.diffusion.status");
    const diffusionEstimate = value("trajectory.diffusion.estimate");
    const fitStart = value("trajectory.diffusion.fit_start");
    const fitEnd = value("trajectory.diffusion.fit_end");
    const fitPoints = value("trajectory.diffusion.fit_points");
    const rSquared = value("trajectory.diffusion.r_squared");
    const alpha = value("trajectory.diffusion.alpha");
    const rdfFrames = value("trajectory.rdf.included_frames");
    const sourceFrames =
      value("trajectory.source_frame_count") || value("trajectory.frame_count");
    const analysisFrames = value("trajectory.analysis_frame_count");
    const analysisFirst = value("trajectory.analysis_first_frame");
    const analysisLast = value("trajectory.analysis_last_frame");
    const boundedWindowClause =
      sourceFrames && analysisFrames && analysisFirst && analysisLast
        ? `完整轨迹共 ${displayEvidenceValue(sourceFrames)} 帧；科学分析显式使用第 ${displayEvidenceValue(analysisFirst)}–${displayEvidenceValue(analysisLast)} 帧（${displayEvidenceValue(analysisFrames)} 帧）`
        : "";
    const rdfClause = rdfFrames
      ? `；RDF 统计使用 ${displayEvidenceValue(rdfFrames)} 帧`
      : "";
    if (status === "DIFFUSIVE_WINDOW_ACCEPTED" && diffusionEstimate) {
      const fitWindow =
        fitStart && fitEnd
          ? `${displayEvidenceValue(fitStart)} 到 ${displayEvidenceValue(fitEnd)}`
          : "用户显式选择的时间窗";
      const diagnostics = [
        fitPoints ? `${displayEvidenceValue(fitPoints)} 个拟合点` : "",
        rSquared ? `R² = ${displayEvidenceValue(rSquared)}` : "",
        alpha ? `α = ${displayEvidenceValue(alpha)}` : "",
      ].filter(Boolean);
      return {
        finding: `${boundedWindowClause ? `${boundedWindowClause}。` : ""}在 ${fitWindow} 内，限定扩散系数为 ${displayEvidenceValue(diffusionEstimate)}${diagnostics.length ? `（${diagnostics.join("，")}）` : ""}；轨迹末端 ${displayEvidenceValue(value("trajectory.msd.last_lag"))} 的总 MSD 为 ${displayEvidenceValue(value("trajectory.msd.last_total"))}${rdfClause}。`,
        limitation:
          "该扩散系数只对用户显式选择的拟合窗口、当前轨迹与采样条件有效，不是无条件的长时间体扩散系数。",
      };
    }
    return {
      finding: `${boundedWindowClause ? `${boundedWindowClause}。` : ""}在 ${displayEvidenceValue(value("trajectory.msd.last_lag"))} 的末端时滞处，总 MSD 为 ${displayEvidenceValue(value("trajectory.msd.last_total"))}${rdfClause}。`,
      limitation:
        status === "INSUFFICIENT_DURATION"
          ? "当前轨迹时长不足以形成稳健扩散系数结论；应延长采样并检查线性扩散区间。"
          : status
            ? "扩散解释仅适用于当前轨迹、时间窗和采样条件。"
            : "当前结果仅报告 MSD，未执行扩散系数估算；MSD 解释仅适用于当前轨迹、时间窗和采样条件。",
    };
  }
  if (
    value("electronic.band.sampled_gap") &&
    hasNumbers(
      "electronic.band.band_count",
      "electronic.band.kpoint_count",
      "electronic.dos.energy_point_count",
    )
  ) {
    return {
      finding: `当前能带包含 ${number("electronic.band.band_count")} 条带和 ${number("electronic.band.kpoint_count")} 个 k 点，采样带隙为 ${displayEvidenceValue(value("electronic.band.sampled_gap"))}；DOS 使用 ${number("electronic.dos.energy_point_count")} 个能量点。`,
      limitation:
        "采样带隙与金属/半导体分类受 k 路径、费米能级和计算设置约束，不等同于实验带隙。",
    };
  }
  if (
    value("phonon.frequency_range") &&
    hasNumbers(
      "phonon.branch_count",
      "phonon.qpoint_count",
      "phonon.imaginary_mode_count",
    )
  ) {
    return {
      finding: `声子结果包含 ${number("phonon.branch_count")} 条分支和 ${number("phonon.qpoint_count")} 个 q 点，频率范围为 ${displayEvidenceValue(value("phonon.frequency_range"))}，检测到 ${number("phonon.imaginary_mode_count")} 个虚频模式。`,
      limitation:
        "动力学稳定性判断仅适用于当前结构、力常数、q 路径和数值容差；近零频模式需要结合收敛性复核。",
    };
  }
  return { finding: "", limitation: "" };
}

function evidenceLabel(role: string) {
  return (
    (
      {
        "xrd.matching_tolerance": "匹配容差",
        "xrd.theoretical_peaks": "理论峰",
        "xrd.residual.mae": "平均绝对偏差",
        "xrd.unmatched_theoretical": "未匹配理论峰",
        "xrd.unmatched_experimental": "未匹配实验峰",
        "xrd.residual.rmse": "均方根偏差",
        "xrd.matched_pairs": "匹配峰",
        "xrd.experimental_detected_peaks": "实验峰",
        "xrd.wavelength": "辐射波长",
        "xrd.residual.maximum_residual": "最大偏差",
        "dataset.sample_count": "样本数",
        "dataset.property_count": "性质字段数",
        "composition.valid_count": "有效化学式",
        "composition.invalid_count": "无效化学式",
        "composition.unique_formula_count": "唯一化学式",
        "structure.formula": "化学式",
        "structure.site_count": "位点数",
        "coordination.algorithm": "配位算法",
        "coordination.coverage": "配位覆盖率",
        "coordination.total_sites": "总位点数",
        "coordination.successful_sites": "成功分析位点",
        "coordination.value_range": "配位值范围",
        "coordination.distance_range": "邻居距离范围",
        "local_environment.source_algorithm": "局部环境来源算法",
        "local_environment.coverage": "局部环境覆盖率",
        "local_environment.evaluated_sites": "已评估位点",
        "local_environment.classified_sites": "已分类位点",
        "local_environment.ambiguous_sites": "歧义位点",
        "local_environment.unclassified_sites": "未分类位点",
        "trajectory.msd.last_total": "末端总 MSD",
        "trajectory.msd.last_lag": "末端时滞",
        "trajectory.rdf.included_frames": "RDF 帧数",
        "trajectory.source_frame_count": "完整轨迹帧数",
        "trajectory.analysis_frame_count": "分析窗口帧数",
        "trajectory.analysis_first_frame": "分析起始帧",
        "trajectory.analysis_last_frame": "分析结束帧",
        "trajectory.analysis_start_time": "分析起始时间",
        "trajectory.analysis_end_time": "分析结束时间",
        "electronic.band.sampled_gap": "采样带隙",
        "electronic.band.band_count": "能带数",
        "electronic.band.kpoint_count": "k 点数",
        "electronic.dos.energy_point_count": "DOS 能量点",
        "phonon.frequency_range": "频率范围",
        "phonon.branch_count": "声子分支",
        "phonon.qpoint_count": "q 点数",
        "phonon.imaginary_mode_count": "虚频模式",
      } as Record<string, string>
    )[role] || role.replaceAll("_", " ")
  );
}

function displayEvidenceValue(value: string) {
  return value
    .replace(/\s+to\s+/gi, " 至 ")
    .replace(/\bdegree\b/gi, "°")
    .replace(/\bangstrom\b/gi, "Å")
    .replace(/\bpicosecond\b/gi, "ps")
    .replace(/\bterahertz\b/gi, "THz");
}

export function evidenceProvenanceSummary(item: Pick<ScientificEvidenceItem, "sourceArtifactId" | "sourceArtifactChecksum" | "sourceToolId" | "fieldLocator">): string {
  const parts = [`字段 ${item.fieldLocator.fieldId}`];
  if (item.sourceArtifactId) parts.push(`Artifact ${item.sourceArtifactId}`);
  if (item.sourceToolId) parts.push(`ToolCall ${item.sourceToolId}`);
  if (item.sourceArtifactChecksum) parts.push(`SHA-256 ${item.sourceArtifactChecksum}`);
  return parts.join(" · ");
}

function formatPercent(value: number) {
  const percent = value * 100;
  return `${Number.isInteger(percent) ? percent.toFixed(0) : percent.toFixed(1)}%`;
}

function artifactLabel(type: string | undefined) {
  return (
    (
      {
        table_json: "数据表",
        plotly_json: "科学图表",
        structure_json: "晶体结构",
        trajectory_json: "原子轨迹",
        xrd_json: "XRD 结果",
        electronic_band_json: "能带结果",
        electronic_dos_json: "态密度结果",
        phonon_band_json: "声子能带",
        phonon_dos_json: "声子态密度",
        volumetric_payload_json: "体数据",
      } as Record<string, string>
    )[String(type || "").toLowerCase()] || "科学结果"
  );
}

export { artifactLabel, displayEvidenceValue, evidenceLabel, formatPercent, researchRunHref, researchSessionReferencesRun, userFacingClaims, userFacingLimitations };
