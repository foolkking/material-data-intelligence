"use client";

import { ProductLink as Link, useProductRouter } from "../../shared/layout/ProductNavigation";
import React, {
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
  resolveResearchScope,
  updateResearchSession,
  type ResearchMessage,
  type ResearchSession,
  type ResearchSessionBulkAction,
  type ScopeResolution,
} from "../../app/lib/product-api";
import { ProductShell, RequireProductAuth } from "../../shared/layout/ProductShell";
import { scientistProjectLabel } from "../../shared/product-labels";
import { ManagedObjectRow, ProductModal } from "../../shared/ui/ObjectManagement";
import { LazyScientificResultViewer } from "../../scientific-viewers/LazyScientificViewers";
import {
  projectScientificArtifacts,
  scientificResultTitle,
  type ProjectedScientificArtifact,
} from "../../app/lib/scientific-result-projection";
import { formatScientificNarrativeNumbers } from "../../app/lib/scientific-presentation";
import { Agent2ScientificPresentation } from "./Agent2ScientificPresentation";
import {
  getReportComposition,
  listReportCompositions,
  type ReportEditorialProjection,
} from "../../app/lib/report-composition-api";
import { researchRunTitle } from "../../app/lib/research-display";
import {
  cancelAgent2Execution,
  getAgent2ExecutionProgress,
  type Agent2ProgressView,
} from "../../app/lib/agent2-execution-api";
import { ResearchExecutionActivity } from "./ResearchExecutionActivity";
import { LiteratureEvidencePanel } from "./LiteratureEvidencePanel";
import {
  getAgent2SessionMemory,
  unpinAgent2Object,
  unpinAgent2Result,
  type Agent2SessionMemory,
} from "../../app/lib/agent2-memory-api";
import { ScientificReportAction } from "../reports/ScientificReportAction";
import {
  Agent2ReadError,
  createAgent2ResearchTurn,
  dispatchAgent2ResearchTurn,
  getAgent2ContextManifest,
  getAgent2ResearchTurn,
  getAgent2ResearchTurnResult,
  listAgent2ResearchTurns,
  type Agent2ScientificObjectRef,
  type Agent2ScientificSelection,
  type Agent2ContextManifest,
  type Agent2ContextManifestItem,
  type Agent2ContextManifestRecord,
  type Agent2ResearchTurnResult,
  type Agent2TurnDetail,
  type Agent2TurnResponse,
} from "../../app/lib/agent2-research-api";
import { decodeWorkspaceSelectionUrl } from "../../shared/workspace/workspace-selection-contract";
import {
  apiSemanticLocator,
  scientificSelectionFromWorkspace,
  selectionToResearchObjectRef,
} from "../../scientific-viewers/scientific-viewer/scientificSelection";
import { resolveScientificViewer } from "../../scientific-viewers/scientific-viewer/scientificViewerRegistry";
import { RESEARCH_CANCELLING_POLL_INTERVAL_MS } from "../../app/lib/research-status";
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
): string | null {
  if (!sessionId || !turnId) return null;
  return [
    "mdi",
    "research-draft",
    encodeURIComponent(projectId),
    encodeURIComponent(sessionId),
    encodeURIComponent(turnId),
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
export function researchBranchChoices(
  turns: Agent2TurnResponse[],
  currentTurnId?: string,
): Agent2TurnResponse[] {
  if (!currentTurnId) return [];
  const current = turns.find(
    (turn) => turn.id === currentTurnId || turn.turn_id === currentTurnId,
  );
  if (!current) return [];
  const rootId = current.parent_turn_id || current.turn_id;
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
): {
  choices: Agent2TurnResponse[];
  current: Agent2TurnResponse;
  currentIndex: number;
  previous: Agent2TurnResponse | null;
  next: Agent2TurnResponse | null;
} | null {
  const choices = researchBranchChoices(turns, currentTurnId);
  if (!choices.length || !currentTurnId) return null;
  const currentIndex = choices.findIndex(
    (turn) => (turn.id || turn.turn_id) === currentTurnId,
  );
  if (currentIndex < 0) return null;
  return {
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

export const CONTEXT_MANIFEST_RENDER_WINDOW = 32;

export function defaultResearchConversationWidth(
  hasScientificWorkbenchContent: boolean,
): number {
  return hasScientificWorkbenchContent ? 420 : 720;
}

export function researchWorkbenchContentAvailable(input: {
  job: PlannerJobCreateResult | null;
  artifacts: readonly Artifact[];
  interpretation: GroundedScientificInterpretation | null;
  evidence: InterpretationEvidenceResponse | null;
  events: readonly JobEvent[];
  agent2Progress: Agent2ProgressView | null;
}): boolean {
  // Route identity is not scientific content. A run/turn can exist before any
  // result, evidence or truthful progress is available, so keep the question
  // readable until the workbench has something useful to inspect.
  return Boolean(
    input.artifacts.length ||
      input.interpretation ||
      input.evidence?.evidenceItems?.length ||
      input.events.length ||
      input.job?.plan ||
      (input.agent2Progress &&
        !["RECEIVED", "QUEUED"].includes(
          String(input.agent2Progress.status || "").toUpperCase(),
        )),
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
      explicit_finding_refs: [],
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
  return message.payload?.messageKind !== "DOWNSTREAM_ACKNOWLEDGEMENT";
}

/**
 * Some historical session projections contain repeated copies of the same
 * message (for example, one row from the legacy projection and one from the
 * Agent2 projection). Keep the first durable identity and collapse only
 * adjacent, byte-for-byte duplicate role/content entries. Distinct repeated
 * questions separated by an assistant response remain visible.
 */
export function dedupeResearchTimelineMessages(
  messages: ResearchMessage[],
): ResearchMessage[] {
  const result: ResearchMessage[] = [];
  for (const message of messages) {
    const previous = result[result.length - 1];
    if (
      previous &&
      previous.role === message.role &&
      previous.content.trim() === message.content.trim()
    ) {
      continue;
    }
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
  if (["failed", "error", "cancelled", "canceled"].includes(normalized))
    return "failed";
  if (["queued", "created", "planning", "pending"].includes(normalized))
    return "planning";
  if (["running", "active", "started"].includes(normalized)) return "running";
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
): string {
  const query = new URLSearchParams({ new: "1" });
  if (datasetId) query.set("dataset", datasetId);
  if (sampleRef) query.set("sample", sampleRef);
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

async function resolveExplicitDatasetScope(
  projectId: string,
  datasetId: string,
): Promise<ScopeResolution> {
  const [dataset, profile, resources] = await Promise.all([
    getDataset(datasetId),
    getDatasetProfile(datasetId),
    getDatasetSourceResources(datasetId),
  ]);
  const table = resources.find((item) => item.objectType === "DataFrame");
  const supportedScientificResources = resources.filter((item) =>
    [
      "Structure",
      "Trajectory",
      "ElectronicBand",
      "ElectronicDos",
      "PhononBand",
      "PhononDos",
    ].includes(item.objectType),
  );
  const selectedResource =
    table || (supportedScientificResources.length === 1
      ? supportedScientificResources[0]
      : undefined);
  if (!selectedResource) {
    // Preserve the bounded legacy planner path when no exact normalized
    // scientific resource exists, or when a Dataset contains multiple
    // candidates and the user has not selected one. Never choose silently.
    return {
      status: "READY",
      dataset_id: dataset.datasetId || dataset.id || datasetId,
      profile_id: profile.profileId || profile.id,
      dataset_name: dataset.name,
    };
  }
  const promoted = table
    ? await promoteDatasetTable(projectId, datasetId, selectedResource.objectId)
    : await admitDatasetResource(
        projectId,
        datasetId,
        selectedResource.objectId,
        dataset.name,
      );
  const objectId = String(promoted.object?.id || "");
  const versionId = String(
    promoted.version?.id || promoted.object?.current_version_id || "",
  );
  if (!objectId || !versionId) throw new Error("数据科学对象版本暂时无法解析");
  return {
    status: "READY",
    dataset_id: dataset.datasetId || dataset.id || datasetId,
    profile_id: profile.profileId || profile.id,
    dataset_name: dataset.name,
    dataset_resource_id: selectedResource.objectId,
    scientific_object_ref: {
      object_id: objectId,
      version_id: versionId,
      project_id: projectId,
      object_type:
        promoted.object?.object_type ||
        (table ? "materials.table" : selectedResource.objectType),
      display_name:
        promoted.object?.display_name || dataset.name || "Scientific data",
    },
  };
}

function datasetResearchRefs(
  scope: ScopeResolution,
  sampleRef?: string,
): {
  objectRef: Agent2ScientificObjectRef;
  selections: Agent2ScientificSelection[];
} | null {
  const source = scope.scientific_object_ref;
  if (!source) return null;
  const objectRef: Agent2ScientificObjectRef = source;
  if (!sampleRef?.trim()) return { objectRef, selections: [] };
  const locator = { sample_ref: sampleRef.trim() };
  return {
    objectRef,
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
  sessionId,
  runId,
  agent2TurnId,
  editTurnId,
  retryOfTurnId,
  retryRequested = false,
  fresh = false,
  resultContextId,
  contextCandidateFromSearch = false,
  viewerContext,
}: {
  projectId: string;
  datasetId?: string;
  sampleRef?: string;
  sessionId?: string;
  runId?: string;
  agent2TurnId?: string;
  editTurnId?: string;
  retryOfTurnId?: string;
  retryRequested?: boolean;
  fresh?: boolean;
  resultContextId?: string;
  contextCandidateFromSearch?: boolean;
  viewerContext?: ViewerResearchContext;
}) {
  const router = useProductRouter();
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
  const [researchPerformanceSample, setResearchPerformanceSample] =
    useState<ResearchPerformanceSample | null>(null);
  const [agent2ContextManifest, setAgent2ContextManifest] =
    useState<Agent2ContextManifest | null>(null);
  const [agent2ContextManifests, setAgent2ContextManifests] = useState<
    Agent2ContextManifestRecord[]
  >([]);
  const [agent2ContextManifestLoadState, setAgent2ContextManifestLoadState] =
    useState<"idle" | "loading" | "ready" | "error">("idle");
  const [agent2ContextManifestReloadKey, setAgent2ContextManifestReloadKey] =
    useState(0);
  const [showFullContextManifest, setShowFullContextManifest] = useState(false);
  const [contextManifestWindowStart, setContextManifestWindowStart] = useState(0);
  const [agent2CancelPending, setAgent2CancelPending] = useState(false);
  const [agent2CancelNotice, setAgent2CancelNotice] = useState("");
  const [agent2ContinuationNotice, setAgent2ContinuationNotice] = useState("");
  const [agent2RetryPending, setAgent2RetryPending] = useState(false);
  const [continueTurnId, setContinueTurnId] = useState<string | null>(null);
  const [showFullConversation, setShowFullConversation] = useState(false);
  const [conversationWindowStart, setConversationWindowStart] = useState(0);
  const [editingResult, setEditingResult] =
    useState<Agent2ResearchTurnResult | null>(null);
  const [editingTurn, setEditingTurn] = useState<Agent2TurnDetail | null>(null);
  const [editingLoadState, setEditingLoadState] = useState<
    "idle" | "loading" | "ready" | "error"
  >("idle");
  const agent2DispatchRef = useRef<string | null>(null);
  const submitInFlightRef = useRef(false);
  const autoRetryTurnRef = useRef<string | null>(null);
  const continuationNoticeTurnRef = useRef<string | null>(null);
  const [sessionMemory, setSessionMemory] =
    useState<Agent2SessionMemory | null>(null);
  const [sessionMemoryMutation, setSessionMemoryMutation] = useState(false);
  const [sessionMemoryError, setSessionMemoryError] = useState("");
  const [agent2Turns, setAgent2Turns] = useState<Agent2TurnResponse[]>([]);
  const [conversationWidth, setConversationWidth] = useState(() =>
    defaultResearchConversationWidth(Boolean(runId || agent2TurnId)),
  );
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
  const [mobilePanel, setMobilePanel] = useState<"timeline" | "workbench">(
    runId || agent2TurnId ? "workbench" : "timeline",
  );
  const [pageLoadState, setPageLoadState] = useState<
    "loading" | "ready" | "error"
  >("loading");
  const [runResolutionState, setRunResolutionState] = useState<
    "idle" | "loading" | "settled"
  >(runId && !agent2TurnId ? "loading" : runId ? "settled" : "idle");
  const [pageLoadError, setPageLoadError] = useState("");
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
  const [thinkingMode, setThinkingMode] = useState<
    "quick" | "standard" | "deep"
  >("standard");
  const questionInputRef = useRef<HTMLTextAreaElement | null>(null);
  const restoredDraftRef = useRef<{
    key: string;
    skipPersistence: boolean;
  } | null>(null);
  const workbenchRef = useRef<HTMLElement | null>(null);
  const conversationWidthCustomizedRef = useRef(false);
  const sessionHistoryTriggerRef = useRef<HTMLButtonElement | null>(null);
  const sessionHistoryRef = useRef<HTMLDivElement | null>(null);
  const sessionHistorySearchRef = useRef<HTMLInputElement | null>(null);
  const mobileTimelineTabRef = useRef<HTMLButtonElement | null>(null);
  const mobileWorkbenchTabRef = useRef<HTMLButtonElement | null>(null);
  const conversationHistoryRef = useRef<HTMLDivElement | null>(null);
  const contextManifestRef = useRef<HTMLDetailsElement | null>(null);
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
    if (!viewerContext.selectionToken) return { sourceRef, selection: null };
    try {
      const workspace = decodeWorkspaceSelectionUrl(
        viewerContext.selectionToken,
      );
      const descriptor = resolveScientificViewer({
        objectType: viewerContext.objectType,
      });
      return {
        sourceRef,
        selection: scientificSelectionFromWorkspace(
          workspace,
          sourceRef,
          descriptor.viewerId,
        ),
      };
    } catch {
      return { sourceRef, selection: null };
    }
  }, [projectId, viewerContext]);
  const activeSearchResultContextId =
    contextCandidateFromSearch && searchContextCandidateActive
      ? resultContextId
      : undefined;
  const activeViewerContext =
    exactViewerContext &&
    (!contextCandidateFromSearch || searchContextCandidateActive)
      ? exactViewerContext
      : null;
  const hasExplicitScientificHandoff = Boolean(
    datasetId || activeViewerContext || activeSearchResultContextId,
  );
  const startFreshResearchHref = freshResearchHref(
    projectId,
    datasetId,
    sampleRef,
    viewerContext,
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
    if (continuationNoticeTurnRef.current === agent2TurnId) {
      continuationNoticeTurnRef.current = null;
    } else {
      setAgent2ContinuationNotice("");
    }
    if (!agent2TurnId) {
      setAgent2Progress(null);
      setAgent2CancelNotice("");
      return;
    }
    setAgent2CancelNotice("");
    agent2DispatchRef.current = null;
    let active = true;
    let inFlight = false;
    let timer: number | undefined;
    const refresh = () => {
      if (!active || inFlight) return;
      inFlight = true;
      void getAgent2ExecutionProgress(agent2TurnId, {
        signal: controller.signal,
      })
        .then((next) => {
          if (!active) return;
          setAgent2Progress(next);
          setAgent2CancelNotice((current) => {
            if (!current) return current;
            if (next.status === "CANCELED") {
              return "";
            }
            if (["COMPLETED", "PARTIAL", "FAILED"].includes(next.status)) {
              return "分析在取消请求生效前已进入终态；现有科学结果未被覆盖。";
            }
            return current;
          });
          // QUERY_DATA is a terminal, non-scientific handoff. Clear any
          // optimistic local planning state immediately so a completed
          // read-only query cannot continue to render as a failed analysis.
          if (next.status === "ANSWERED") {
            setState("idle");
            setError("");
          }
          if (
            next.status === "PLAN_READY" &&
            agent2DispatchRef.current !== agent2TurnId
          ) {
            agent2DispatchRef.current = agent2TurnId;
            void dispatchAgent2ResearchTurn(agent2TurnId).catch(async (reason) => {
              if (!active) return;
              // Stop may win the narrow PLAN_READY → dispatch race. The
              // dispatch request can then correctly return a conflict because
              // the durable Turn is already CANCELED. Reconcile durable state
              // before surfacing an execution error so a successful stop is
              // never presented as a failed research run.
              try {
                const latest = await getAgent2ExecutionProgress(agent2TurnId, {
                  signal: controller.signal,
                });
                if (!active) return;
                setAgent2Progress(latest);
                if (shouldSuppressAgent2DispatchError(latest.status)) {
                  setError("");
                  return;
                }
              } catch {
                // Preserve the original dispatch error when durable state is
                // temporarily unavailable.
              }
              setError(
                reason instanceof Error ? reason.message : "研究执行失败",
              );
            });
          }
          if (agent2ProgressNeedsRefresh(next.status))
            timer = window.setTimeout(refresh, RESEARCH_CANCELLING_POLL_INTERVAL_MS);
        })
        .catch((reason) => {
          if (active && !requestWasAborted(reason)) setAgent2Progress(null);
        })
        .finally(() => {
          inFlight = false;
        });
    };
    const controller = new AbortController();
    refresh();
    const onOnline = () => refresh();
    window.addEventListener("online", onOnline);
    return () => {
      active = false;
      controller.abort();
      window.removeEventListener("online", onOnline);
      if (timer) clearTimeout(timer);
    };
  }, [agent2TurnId]);

  useEffect(() => {
    if (
      !session?.id ||
      !agent2TurnId ||
      !agent2ProgressHasFreshSessionMessages(agent2Progress?.status || "")
    )
      return;
    let active = true;
    void getResearchSession(session.id)
      .then((full) => {
        if (active) setSession(full);
      })
      .catch(() => {
        // Durable Turn progress remains authoritative. Normal reconnect and
        // reload paths can retrieve the persisted message after a transient
        // conversation refresh failure.
      });
    return () => {
      active = false;
    };
  }, [agent2Progress?.status, agent2TurnId, session?.id]);

  useEffect(() => {
    if (!agent2TurnId) {
      setAgent2ContextManifest(null);
      setAgent2ContextManifests([]);
      setAgent2ContextManifestLoadState("idle");
      setShowFullContextManifest(false);
      setContextManifestWindowStart(0);
      return;
    }
    setShowFullContextManifest(false);
    setContextManifestWindowStart(0);
    setAgent2ContextManifestLoadState("loading");
    let active = true;
    void getAgent2ContextManifest(agent2TurnId)
      .then((detail) => {
        if (active) {
          if (!detail?.manifest) throw new Error("CONTEXT_MANIFEST_UNAVAILABLE");
          setAgent2ContextManifest(detail.manifest);
          setAgent2ContextManifests(
            detail.manifests?.length
              ? detail.manifests
              : [{ operation: detail.manifest.operation, manifest: detail.manifest }],
          );
          setAgent2ContextManifestLoadState("ready");
        }
      })
      .catch(() => {
        if (active) {
          setAgent2ContextManifest(null);
          setAgent2ContextManifests([]);
          setAgent2ContextManifestLoadState("error");
        }
      });
    return () => {
      active = false;
    };
  }, [
    agent2ContextManifestReloadKey,
    agent2Progress?.status,
    agent2TurnId,
  ]);

  useEffect(() => {
    if (!session?.id) {
      setSessionMemory(null);
      return;
    }
    let active = true;
    void getAgent2SessionMemory(projectId, session.id)
      .then((memory) => {
        if (active) setSessionMemory(memory);
      })
      .catch(() => {
        if (active) setSessionMemory(null);
      });
    return () => {
      active = false;
    };
  }, [projectId, session?.id]);

  async function removePinnedResult(resultId: string) {
    if (!session?.id || sessionMemoryMutation) return;
    setSessionMemoryMutation(true);
    setSessionMemoryError("");
    try {
      setSessionMemory(
        await unpinAgent2Result(projectId, session.id, resultId),
      );
    } catch (reason) {
      setSessionMemoryError(
        reason instanceof Error ? reason.message : "固定结果移除失败",
      );
    } finally {
      setSessionMemoryMutation(false);
    }
  }

  async function removePinnedObject(
    objectRef: Agent2SessionMemory["pinned_object_refs"][number],
  ) {
    if (
      !session?.id ||
      sessionMemoryMutation ||
      !objectRef.object_id ||
      !objectRef.version_id ||
      !objectRef.project_id ||
      !objectRef.object_type
    )
      return;
    setSessionMemoryMutation(true);
    setSessionMemoryError("");
    try {
      setSessionMemory(
        await unpinAgent2Object(projectId, session.id, {
          object_id: objectRef.object_id,
          version_id: objectRef.version_id,
          project_id: objectRef.project_id,
          object_type: objectRef.object_type,
          display_name: objectRef.display_name,
        }),
      );
    } catch (reason) {
      setSessionMemoryError(
        reason instanceof Error ? reason.message : "固定来源移除失败",
      );
    } finally {
      setSessionMemoryMutation(false);
    }
  }

  useEffect(() => {
    if (!session?.id || !agent2TurnId) {
      setAgent2Turns([]);
      return;
    }
    let active = true;
    void listAgent2ResearchTurns(projectId, session.id)
      .then((items) => {
        if (!active) return;
        setAgent2Turns(items);
        const recoveredTurn = resolveAgent2TurnForRecovery(
          items,
          projectId,
          session.id,
          agent2TurnId,
        );
        if (!recoveredTurn) return;
        setSession((current) => {
          if (!current || current.id !== session.id) return current;
          const currentMessages = current.messages || [];
          if (
            currentMessages.some(
              (message) => message.id === recoveredTurn.user_message.id,
            )
          ) {
            return current;
          }
          return {
            ...current,
            messages: [
              ...currentMessages,
              {
                id: recoveredTurn.user_message.id,
                session_id: session.id,
                role: "user",
                content: recoveredTurn.user_message.content,
                created_at: recoveredTurn.created_at,
              },
            ],
          };
        });
      })
      .catch(() => {
        if (active) setAgent2Turns([]);
      });
    return () => {
      active = false;
    };
  }, [projectId, session?.id, agent2TurnId]);

  useEffect(() => {
    if (!editTurnId) {
      setEditingResult(null);
      setEditingTurn(null);
      setEditingLoadState("idle");
      return;
    }
    let active = true;
    setEditingTurn(null);
    setEditingResult(null);
    setQuestion("");
    setEditingLoadState("loading");
    void Promise.allSettled([
      getAgent2ResearchTurn(editTurnId),
      getAgent2ResearchTurnResult(editTurnId),
    ])
      .then(([turnResult, scientificResult]) => {
        if (!active) return;
        if (turnResult.status !== "fulfilled") {
          setEditingTurn(null);
          setEditingResult(null);
          setEditingLoadState("error");
          setError("原研究问题暂时无法读取，历史结果仍保持不变。");
          return;
        }
        setEditingTurn(turnResult.value);
        setQuestion(turnResult.value.user_message.content);
        setEditingResult(
          scientificResult.status === "fulfilled"
            ? scientificResult.value
            : null,
        );
        setEditingLoadState("ready");
      })
      .catch(() => {
        if (!active) return;
        setEditingTurn(null);
        setEditingResult(null);
        setEditingLoadState("error");
        setError("原研究问题暂时无法读取，历史结果仍保持不变。");
      });
    return () => {
      active = false;
    };
  }, [editTurnId]);

  async function cancelAgent2Turn() {
    if (!agent2TurnId || agent2CancelPending) return;
    setAgent2CancelPending(true);
    setAgent2CancelNotice("");
    setError("");
    try {
      const result = await cancelAgent2Execution(agent2TurnId);
      setAgent2Progress((current) =>
        current ? { ...current, status: result.status } : current,
      );
      setAgent2CancelNotice(
        result.status === "CANCELED"
          ? ""
          : "取消请求已记录，正在等待运行中的科学步骤安全结束。",
      );
    } catch (reason) {
      // A fast scientific execution may finish between the last progress poll
      // and the user's Stop click. Re-read durable state before presenting a
      // false cancellation failure. Scientific completion wins this race and
      // must remain explicit rather than being overwritten as CANCELED.
      try {
        const latest = await getAgent2ExecutionProgress(agent2TurnId);
        setAgent2Progress(latest);
        if (["COMPLETED", "PARTIAL", "FAILED", "CANCELED"].includes(latest.status)) {
          setAgent2CancelNotice(
            latest.status === "CANCELED"
              ? ""
              : "分析在取消请求生效前已进入终态；现有科学结果未被覆盖。",
          );
          return;
        }
      } catch {
        // Preserve the original cancellation failure when durable state is
        // temporarily unavailable.
      }
      setError(reason instanceof Error ? reason.message : "取消请求未能提交");
    } finally {
      setAgent2CancelPending(false);
    }
  }

  async function retryAgent2Turn() {
    if (!agent2TurnId || !session || agent2RetryPending) return;
    setAgent2RetryPending(true);
    setError("");
    try {
      const exactTurn = await getAgent2ResearchTurn(agent2TurnId);
      const next = await createAgent2ResearchTurn(
        projectId,
        session.id,
        agent2RetryInput(exactTurn),
      );
      router.push(
        `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(next.turn_id)}&retryOf=${encodeURIComponent(exactTurn.turn_id)}`,
      );
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "重试请求未能提交");
    } finally {
      setAgent2RetryPending(false);
    }
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
    );
  }

  function continueAgent2Research() {
    if (!agent2TurnId) return;
    // Continue is a composer action. Keep the control reachable on mobile
    // even when the user invoked it from the Workbench presentation tab.
    setMobilePanel("timeline");
    setContinueTurnId(agent2TurnId);
    setAgent2CancelNotice(
      "继续研究会保留当前会话与已授权的精确上下文；只有提交新问题后才会开始新的处理。",
    );
    requestAnimationFrame(() => {
      questionInputRef.current?.focus();
      questionInputRef.current?.scrollIntoView?.({ block: "nearest" });
    });
  }

  function clampConversationWidth(value: number): number {
    if (!Number.isFinite(value)) return conversationWidth;
    const workbenchWidth =
      workbenchRef.current?.getBoundingClientRect().width || 1280;
    const maximum = Math.min(760, Math.max(320, workbenchWidth - 480));
    return Math.round(Math.min(maximum, Math.max(320, value)));
  }

  useEffect(() => {
    let active = true;
    setSession(null);
    setScope(null);
    setJob(null);
    setEvents([]);
    setArtifacts([]);
    setInterpretation(null);
    setEvidence(null);
    setError("");
    setState("idle");
    postRunMessageRef.current = null;
    failedRunMessageRef.current = null;
    // An edit route is a conversation action even when it retains the
    // completed Turn in the query string. Keep the mobile view on the
    // composer rather than defaulting back to the scientific workbench.
    setMobilePanel(
      editTurnId
        ? "timeline"
        : runId || agent2TurnId
          ? "workbench"
          : "timeline",
    );
    setPageLoadState("loading");
    setPageLoadError("");
    setRunResolutionState(
      runId && !agent2TurnId ? "loading" : runId ? "settled" : "idle",
    );
    void Promise.all([
      listResearchSessions(projectId),
      getProjectHistory(projectId),
    ])
      .then(([items, nextHistory]) => {
        if (!active) return;
        setSessions(items);
        setHistory(nextHistory);
        setPageLoadState("ready");
        const runSession = runId
          ? items.find((item) => researchSessionReferencesRun(item, runId))
          : undefined;
        // An explicit session id is an authoritative navigation target. When a
        // historical run is not yet normalized onto that session, retain the
        // requested session rather than turning a valid route into a missing
        // conversation error. A run-only route still requires an explicit
        // persisted run binding and must not fall back to an unrelated session.
        const selected = runId
          ? runSession ||
            (sessionId
              ? items.find((item) => item.id === sessionId)
              : undefined)
          : sessionId
            ? items.find((item) => item.id === sessionId)
            : fresh || hasExplicitScientificHandoff
              ? undefined
              : items.find(
                  (item) =>
                    !["archived", "trashed"].includes(
                      String(item.status || "active").toLowerCase(),
                    ),
                );
        if (selected) {
          setSessionLoadState("loading");
          setSessionLoadError("");
          void getResearchSession(selected.id)
            .then((full) => {
              if (!active) return;
              setSession(full);
              setSessionLoadState("ready");
            })
            .catch((reason) => {
              if (!active) return;
              setSession(null);
              setSessionLoadState("error");
              setSessionLoadError(
                reason instanceof Error
                  ? reason.message
                  : "研究会话暂时无法读取",
              );
            });
        } else {
          setSessionLoadState(sessionId ? "error" : "ready");
          setSessionLoadError(sessionId ? "研究会话不存在或已不可访问。" : "");
        }
        if (datasetId && !runId && !sessionId) {
          void resolveExplicitDatasetScope(projectId, datasetId)
            .then((selectedScope) => {
              if (active) setScope(selectedScope);
            })
            .catch((reason) => {
              if (!active) return;
              setScope(null);
              setPageLoadError(
                reason instanceof Error
                  ? reason.message
                  : "所选数据暂时无法读取。",
              );
            });
        }
        if (runId && !agent2TurnId) {
          const historicalRun = nextHistory.analyses.find(
            (item) => item.jobId === runId,
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
            setJob({ ok: true, job_id: runId, plan: null });
            setState(researchRunState(historicalRun.status));
            void Promise.allSettled([
              getPlannerJob(runId),
              getPlannerJobEvents(runId),
              getPlannerJobArtifacts(runId),
              getPlannerJobInterpretations(runId),
            ]).then(
              ([
                detailResult,
                eventResult,
                artifactResult,
                interpretationResult,
              ]) => {
                if (!active) return;
                if (detailResult.status === "fulfilled") {
                  const detail = detailResult.value;
                  setJob((current) =>
                    current
                      ? {
                          ...current,
                          plan: detail.analysisPlan || current.plan,
                          plan_id: detail.planId || current.plan_id,
                          plan_hash: detail.planHash || current.plan_hash,
                        }
                      : current,
                  );
                }
                if (eventResult.status === "fulfilled")
                  setEvents(mergeJobEvents([], eventResult.value));
                if (artifactResult.status === "fulfilled")
                  setArtifacts(mergeArtifacts([], artifactResult.value));
                const historyInterpretations =
                  interpretationResult.status === "fulfilled"
                    ? interpretationResult.value
                    : null;
                const existingInterpretation =
                  historyInterpretations?.interpretations?.at(-1) || null;
                setInterpretation(existingInterpretation);
                setInterpretationStatus(
                  existingInterpretation
                    ? existingInterpretation.completeness === "COMPLETE"
                      ? "ready"
                      : "limited"
                    : "idle",
                );
                if (existingInterpretation)
                  void getPlannerInterpretationEvidence(
                    existingInterpretation.interpretationId,
                  )
                    .then(setEvidence)
                    .catch(() => setEvidence(null));
                const owner = runSession || selected;
                if (
                  existingInterpretation &&
                  owner &&
                  !researchSessionReferencesRun(owner, runId, "post_run")
                ) {
                  void createResearchAssistantProjection(owner.id, {
                    phase: "post_run",
                    datasetId: historicalRun.datasetId,
                    runId,
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
                  !existingInterpretation &&
                  owner &&
                  (historicalState === "complete" ||
                    historicalState === "partial") &&
                  planHash
                ) {
                  setInterpretationStatus("loading");
                  void createScientificInterpretation(runId, planHash)
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
                      if (recovered) {
                        void getPlannerInterpretationEvidence(
                          recovered.interpretationId,
                        )
                          .then((value) => {
                            if (active) setEvidence(value);
                          })
                          .catch(() => undefined);
                        void createResearchAssistantProjection(owner.id, {
                          phase: "post_run",
                          datasetId: historicalRun.datasetId,
                          runId,
                        })
                          .then((message) => {
                            if (active) appendSessionMessage(message);
                          })
                          .catch(() => undefined);
                      }
                    })
                    .catch(() => {
                      if (active) setInterpretationStatus("error");
                    });
                }
                if (
                  historicalState === "failed" &&
                  owner &&
                  !researchSessionReferencesRun(owner, runId, "failed")
                ) {
                  void createResearchAssistantProjection(owner.id, {
                    phase: "failed",
                    datasetId: historicalRun.datasetId,
                    runId,
                    failureCode: "JOB_FAILED",
                  })
                    .then((message) => {
                      if (active) appendSessionMessage(message);
                    })
                    .catch(() => undefined);
                }
                const failures = [
                  detailResult,
                  eventResult,
                  artifactResult,
                  interpretationResult,
                ].filter((item) => item.status === "rejected").length;
                if (failures === 4)
                  setError("历史分析结果暂时无法读取，请稍后重试。");
                else if (failures > 0)
                  setError("部分运行记录暂时无法读取；已保留当前可用结果。");
                setRunResolutionState("settled");
              },
            );
          } else {
            setRunResolutionState("settled");
          }
        }
      })
      .catch((reason) => {
        if (!active) return;
        setPageLoadError(
          reason instanceof Error ? reason.message : "研究内容加载失败",
        );
        setPageLoadState("error");
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
      window.removeEventListener("online", refreshPersistedState);
      document.removeEventListener("visibilitychange", refreshOnVisible);
    };
  }, [
    agent2TurnId,
    datasetId,
    editTurnId,
    fresh,
    hasExplicitScientificHandoff,
    projectId,
    reloadKey,
    runId,
    sessionId,
  ]);

  useEffect(() => {
    if (!sessionHistoryOpen) return;
    sessionHistorySearchRef.current?.focus();
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
  }, [sessionHistoryOpen]);

  function closeSessionHistory(restoreFocus = true) {
    setSessionHistoryOpen(false);
    setSessionHistoryQuery("");
    setSessionSelectionMode(false);
    setSelectedSessionIds([]);
    if (restoreFocus) sessionHistoryTriggerRef.current?.focus();
  }

  useEffect(() => {
    let active = true;
    setProviderLoadState("loading");
    void Promise.all([getPlannerProviderStatus(), listPlannerProviders()])
      .then(([nextStatus, nextProviders]) => {
        if (!active) return;
        setProviderStatus(nextStatus);
        const available = nextProviders.providers.filter(
          (item) =>
            !item.developerOnly &&
            (item.secretConfigured || item.execution === "live"),
        );
        setProviderOptions(available);
        const first =
          available.find((item) => item.provider === nextStatus.provider) ||
          available[0];
        setSelectedProvider(first?.provider || "");
        setSelectedModel(
          nextStatus.model || first?.defaultModel || first?.models?.[0] || "",
        );
        setProviderLoadState("ready");
      })
      .catch(() => {
        if (!active) return;
        setProviderStatus(null);
        setProviderOptions([]);
        setProviderLoadState("error");
      });
    return () => {
      active = false;
    };
  }, [providerReloadKey]);

  const selectedProviderOption = providerOptions.find(
    (item) => item.provider === selectedProvider,
  );
  const selectedModels = selectedProviderOption?.models?.length
    ? selectedProviderOption.models
    : selectedProviderOption?.allowedModels ||
      providerStatus?.allowedModels ||
      [];
  const branchChoices = useMemo(
    () => researchBranchChoices(agent2Turns, agent2TurnId),
    [agent2TurnId, agent2Turns],
  );
  const branchNavigation = useMemo(
    () => researchBranchNavigation(agent2Turns, agent2TurnId),
    [agent2TurnId, agent2Turns],
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
        (turn) => (turn.id || turn.turn_id) === agent2TurnId,
      ) || null,
    [agent2TurnId, agent2Turns],
  );
  const selectedTurnMessageId = selectedAgent2Turn?.user_message.id || null;
  const retryLineage = useMemo(
    () => retryLineageForTurn(agent2Turns, agent2TurnId, retryOfTurnId),
    [agent2TurnId, agent2Turns, retryOfTurnId],
  );
  const activeAgent2Progress = agent2ProgressForTurn(
    agent2Progress,
    agent2TurnId,
  );
  const activeAgent2ContextManifest = agent2ContextManifestForTurn(
    agent2ContextManifest,
    agent2TurnId,
  );
  const visibleContextManifestItems = contextManifestRenderItems(
    activeAgent2ContextManifest,
    showFullContextManifest,
    contextManifestWindowStart,
  );
  const composerDraftKey = useMemo(
    () =>
      researchComposerDraftKey(
        projectId,
        session?.id || sessionId,
        agent2TurnId,
      ),
    [agent2TurnId, projectId, session?.id, sessionId],
  );

  useEffect(() => {
    if (!composerDraftKey || typeof window === "undefined") return;
    let savedDraft = "";
    try {
      savedDraft = window.sessionStorage.getItem(composerDraftKey) || "";
    } catch {
      // A blocked browser storage policy must not block Research itself.
    }
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
    try {
      if (question) {
        window.sessionStorage.setItem(composerDraftKey, question);
      } else {
        window.sessionStorage.removeItem(composerDraftKey);
      }
    } catch {
      // Keep the in-memory draft usable when browser storage is unavailable.
    }
  }, [composerDraftKey, question]);

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
    setMobilePanel("timeline");
    window.requestAnimationFrame(() => {
      const disclosure = contextManifestRef.current;
      if (!disclosure) return;
      disclosure.open = true;
      disclosure.scrollIntoView?.({
        block: "nearest",
        behavior: window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
          ? "auto"
          : "smooth",
      });
      disclosure.querySelector<HTMLElement>("summary")?.focus();
    });
  }

  useEffect(() => {
    if (!selectedTurnMessageId) return;
    const frame = window.requestAnimationFrame(() => {
      const container = conversationHistoryRef.current;
      const message = container?.querySelector<HTMLElement>(
        `[data-message-id="${CSS.escape(selectedTurnMessageId)}"]`,
      );
      if (!container || !message || typeof container.scrollTo !== "function")
        return;
      const containerRect = container.getBoundingClientRect();
      const messageRect = message.getBoundingClientRect();
      const top =
        container.scrollTop +
        messageRect.top -
        containerRect.top -
        Math.max(16, (container.clientHeight - messageRect.height) / 2);
      container.scrollTo({ top: Math.max(0, top), behavior: "auto" });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [selectedTurnMessageId]);

  const hasAuthoritativeTurnPresentation =
    Boolean(agent2TurnId) &&
    Boolean(
      activeAgent2Progress &&
        ["COMPLETED", "PARTIAL"].includes(activeAgent2Progress.status),
    );

  useEffect(() => {
    // A failed/canceled run is actionable from the conversation surface:
    // retry, continue and edit controls live beside the persisted timeline.
    // When a history link opens with `run=`, the initial mobile selection is
    // the workbench; move to the timeline once durable progress confirms the
    // terminal failure so recovery actions are immediately visible.
    if (
      runId &&
      activeAgent2Progress &&
      ["FAILED", "CANCELED"].includes(activeAgent2Progress.status)
    ) {
      setMobilePanel("timeline");
    }
  }, [activeAgent2Progress, runId]);

  async function ensureSession() {
    if (session) return session;
    const created = await createResearchSession(
      projectId,
      question.slice(0, 48) || "新研究",
      datasetId,
    );
    setSession(created);
    setSessions((items) => [created, ...items]);
    return created;
  }

  async function submitQuestion() {
    if (!editBranchSubmissionAllowed(editTurnId, editingLoadState, editingTurn)) {
      setError(
        "原研究问题暂时无法读取，无法安全创建编辑分支。请返回原研究后重试。",
      );
      return;
    }
    if (!question.trim()) return;
    if (submitInFlightRef.current) return;
    submitInFlightRef.current = true;
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
  try {
      activeSession = await ensureSession();
      // A persisted session carries the authoritative Dataset scope for
      // follow-up questions. Keep explicit route handoffs first, then use the
      // session binding before asking the broad project scope resolver.
      const activeDatasetId =
        datasetId || activeSession.datasetId || activeSession.dataset_id || undefined;
      if (editTurnId && editingTurn) {
        const resultRefs = editingResult?.source_object_refs || [];
        const scopeRefs = editingTurn.context?.scope || [];
        const selectionRefs = editingTurn.context?.selection || scopeRefs;
        const refs = resultRefs.length ? resultRefs : scopeRefs;
        const scientificSelections =
          editingResult?.scientific_selections ||
          editingTurn.context?.scientific_selection ||
          [];
        const created = await createAgent2ResearchTurn(
          projectId,
          activeSession.id,
          {
            message: question.trim(),
            reply_to_turn_id: editTurnId,
            autonomy_mode: autonomyMode,
            ui_context: {
              active_object_refs: refs,
              selection_refs: resultRefs.length ? refs : selectionRefs,
              scientific_selections: scientificSelections,
              explicit_object_refs: refs,
              explicit_result_ids: [],
              explicit_finding_refs: [],
            },
          },
        );
        bindResearchPerformanceTurn(performanceAttemptId, created.turn_id);
        router.push(
          `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(activeSession.id)}?turn=${encodeURIComponent(created.turn_id)}`,
        );
        return;
      }
      if (continueTurnId) {
        const exactTurn = await getAgent2ResearchTurn(continueTurnId);
        // A canceled/failed Turn may legitimately have no readable Result.
        // In that case Continue remains a new bounded request. When a
        // persisted snapshot is available, carry its snapshot identity
        // explicitly because child-turn context intentionally excludes
        // implicit historical Result candidates.
        let reusableResult: Agent2ResearchTurnResult | null = null;
        try {
          reusableResult = await getAgent2ResearchTurnResult(continueTurnId);
        } catch (reason) {
          if (!(reason instanceof Agent2ReadError) || reason.status !== 404) {
            throw reason;
          }
        }
        const reusableResultId =
          reusableResult?.result_snapshot_id || reusableResult?.result_id;
        const created = await createAgent2ResearchTurn(
          projectId,
          activeSession.id,
          {
            ...agent2ContinueInput(exactTurn, question, reusableResultId),
            autonomy_mode: autonomyMode,
          },
        );
        bindResearchPerformanceTurn(performanceAttemptId, created.turn_id);
        continuationNoticeTurnRef.current = created.turn_id;
        setAgent2ContinuationNotice(
          reusableResultId
            ? `已将精确结果 ${reusableResultId} 作为复用候选；只有问题超出其证据范围时才会规划新分析。`
            : "原研究没有可复用的科学结果；本次继续将创建新的科学执行，历史 ResearchTurn 保持不变。",
        );
        setContinueTurnId(null);
        setQuestion("");
        setState("planning");
        setMobilePanel("workbench");
        router.push(
          `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(activeSession.id)}?turn=${encodeURIComponent(created.turn_id)}`,
        );
        return;
      }
      if (activeSearchResultContextId) {
        const created = await createAgent2ResearchTurn(
          projectId,
          activeSession.id,
          {
            message: question.trim(),
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
        bindResearchPerformanceTurn(performanceAttemptId, created.turn_id);
        setSearchContextCandidateActive(false);
        setQuestion("");
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
        const scientificSelections = activeViewerContext.selection
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
        const created = await createAgent2ResearchTurn(
          projectId,
          activeSession.id,
          {
            message: question.trim(),
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
        bindResearchPerformanceTurn(performanceAttemptId, created.turn_id);
        if (contextCandidateFromSearch) setSearchContextCandidateActive(false);
        setQuestion("");
        setState("planning");
        setMobilePanel("workbench");
        router.push(
          `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(activeSession.id)}?turn=${encodeURIComponent(created.turn_id)}`,
        );
        return;
      }
      const nextScope = activeDatasetId
        ? await resolveExplicitDatasetScope(projectId, activeDatasetId)
        : await resolveResearchScope(projectId, question.trim());
      setScope(nextScope);
      const activeSessionId = activeSession.id;
      const persistLegacyUserMessage = async () => {
        const savedMessage = await createResearchMessage(
          activeSessionId,
          question.trim(),
          activeDatasetId,
        );
        setSession((current) =>
          current
            ? {
                ...current,
                messages: [...(current.messages || []), savedMessage],
              }
            : current,
        );
      };
      if (nextScope.status === "UNSUPPORTED") {
        await persistLegacyUserMessage();
        const reply = await createResearchAssistantProjection(
          activeSession.id,
          { phase: "unsupported", datasetName: nextScope.dataset_name },
        );
        appendSessionMessage(reply);
        setState("unsupported");
        return;
      }
      if (nextScope.status === "NEEDS_CLARIFICATION") {
        await persistLegacyUserMessage();
        const reply = await createResearchAssistantProjection(
          activeSession.id,
          {
            phase: "clarification",
            candidates: nextScope.candidates?.map((item) => item.name) || [],
          },
        );
        appendSessionMessage(reply);
        setState("clarification");
        return;
      }
      if (!nextScope.dataset_id) throw new Error("没有找到可用于分析的数据");
      const resolvedDatasetId = nextScope.dataset_id;
      const explicitDataset = datasetResearchRefs(
        nextScope,
        sampleRef ||
          question.match(/\bmat-[A-Za-z0-9][A-Za-z0-9_.-]*\b/i)?.[0],
      );
      if (explicitDataset) {
        const created = await createAgent2ResearchTurn(
          projectId,
          activeSession.id,
          {
            message: question.trim(),
            autonomy_mode: autonomyMode,
            ui_context: {
              active_object_refs: [explicitDataset.objectRef],
              selection_refs: explicitDataset.selections.length
                ? [explicitDataset.objectRef]
                : [],
              scientific_selections: explicitDataset.selections,
              explicit_object_refs: [explicitDataset.objectRef],
              explicit_result_ids: [],
              explicit_finding_refs: [],
            },
          },
        );
        bindResearchPerformanceTurn(performanceAttemptId, created.turn_id);
        setQuestion("");
        setState("planning");
        setMobilePanel("workbench");
        router.push(
          `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(activeSession.id)}?turn=${encodeURIComponent(created.turn_id)}`,
        );
        return;
      }
      await persistLegacyUserMessage();
      const nextJob = await createPlannerJob({
        userPrompt: question.trim(),
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
      setJob(nextJob);
      if (!nextJob.ok || !nextJob.job_id) {
        setState(
          nextJob.capability_outcome === "NEEDS_CLARIFICATION"
            ? "capability-clarification"
            : "failed",
        );
        setError(plannerFailureMessage(nextJob));
        const failure = await createResearchAssistantProjection(
          activeSession.id,
          {
            phase: "failed",
            datasetName: nextScope.dataset_name,
            datasetId: nextScope.dataset_id,
            failureCode: plannerFailureCode(nextJob),
          },
        );
        appendSessionMessage(failure);
        return;
      }
      const preRun = await createResearchAssistantProjection(activeSession.id, {
        phase: "pre_run",
        datasetName: nextScope.dataset_name,
        datasetId: resolvedDatasetId,
        runId: nextJob.job_id,
        question: question.trim(),
        provider: selectedProvider || undefined,
        model: selectedModel || undefined,
        thinkingMode,
        useProvider: true,
      });
      appendSessionMessage(preRun);
      setState("running");
      persistRunLink(nextJob.job_id);
      setQuestion("");
      setMobilePanel("workbench");
    } catch (reason) {
      setState("failed");
      setError(scientistFacingResearchRequestError(reason));
      if (activeSession && !(reason instanceof Agent2ReadError)) {
        void createResearchAssistantProjection(activeSession.id, {
          phase: "failed",
          failureCode: "RESEARCH_SERVICE_UNAVAILABLE",
        })
          .then(appendSessionMessage)
          .catch(() => undefined);
      }
    } finally {
      submitInFlightRef.current = false;
    }
  }

  async function confirmScope(datasetId: string) {
    if (!question.trim() || !scope || !datasetId) return;
    setEvents([]);
    setArtifacts([]);
    setInterpretation(null);
    setEvidence(null);
    setInterpretationStatus("idle");
    setError("");
    setState("planning");
    try {
      const candidate = scope.candidates?.find(
        (item) => item.dataset_id === datasetId,
      );
      const activeSession = await ensureSession();
      const savedSelection = await createResearchMessage(
        activeSession.id,
        `使用 ${candidate?.name || "所选数据"} 继续分析。`,
        datasetId,
      );
      setSession((current) =>
        current
          ? {
              ...current,
              datasetId,
              dataset_id: datasetId,
              messages: [...(current.messages || []), savedSelection],
            }
          : current,
      );
      const resolvedDataset = await resolveExplicitDatasetScope(projectId, datasetId);
      setScope(resolvedDataset);
      const explicitDataset = datasetResearchRefs(
        resolvedDataset,
        sampleRef ||
          question.match(/\bmat-[A-Za-z0-9][A-Za-z0-9_.-]*\b/i)?.[0],
      );
      if (explicitDataset) {
        const created = await createAgent2ResearchTurn(
          projectId,
          activeSession.id,
          {
            message: question.trim(),
            autonomy_mode: autonomyMode,
            ui_context: {
              active_object_refs: [explicitDataset.objectRef],
              selection_refs: explicitDataset.selections.length
                ? [explicitDataset.objectRef]
                : [],
              scientific_selections: explicitDataset.selections,
              explicit_object_refs: [explicitDataset.objectRef],
              explicit_result_ids: [],
              explicit_finding_refs: [],
            },
          },
        );
        setQuestion("");
        setState("planning");
        setMobilePanel("workbench");
        router.push(
          `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(activeSession.id)}?turn=${encodeURIComponent(created.turn_id)}`,
        );
        return;
      }
      const nextJob = await createPlannerJob({
        userPrompt: question.trim(),
        projectId,
        datasetId,
        profileId: candidate?.profile_id,
        enqueue: true,
        provider: selectedProvider || undefined,
        model: selectedModel || undefined,
        thinkingMode,
        intentSchemaVersion: "1.0",
        researchSessionId: activeSession.id,
      });
      setJob(nextJob);
      if (!nextJob.ok || !nextJob.job_id) {
        setState(
          nextJob.capability_outcome === "NEEDS_CLARIFICATION"
            ? "capability-clarification"
            : "failed",
        );
        setError(plannerFailureMessage(nextJob));
        const failure = await createResearchAssistantProjection(
          activeSession.id,
          {
            phase: "failed",
            datasetName: candidate?.name,
            datasetId,
            failureCode: plannerFailureCode(nextJob),
          },
        );
        appendSessionMessage(failure);
        return;
      }
      const preRun = await createResearchAssistantProjection(activeSession.id, {
        phase: "pre_run",
        datasetName: candidate?.name,
        datasetId,
        runId: nextJob.job_id,
        question: question.trim(),
        provider: selectedProvider || undefined,
        model: selectedModel || undefined,
        thinkingMode,
        useProvider: true,
      });
      appendSessionMessage(preRun);
      setState("running");
      persistRunLink(nextJob.job_id);
      setQuestion("");
      setMobilePanel("workbench");
    } catch (reason) {
      setState("failed");
      setError(scientistFacingResearchRequestError(reason));
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

  async function changeSessionLifecycle(
    item: ResearchSession,
    next: "ACTIVE" | "ARCHIVED" | "TRASHED",
  ) {
    const label =
      next === "TRASHED"
        ? "移入回收站"
        : next === "ARCHIVED"
          ? "归档"
          : "恢复研究记录";
    if (
      typeof window !== "undefined" &&
      next !== "ACTIVE" &&
      !window.confirm(`${label}“${item.title}”？历史研究结果与精确来源仍会保留。`)
    )
      return;
    sessionLifecycleFocusRef.current =
      document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;
    setSessionLifecycleBusy(item.id);
    setSessionLifecycleNotice("");
    try {
      const updated = await updateResearchSession(item.id, { lifecycle: next });
      setSessions((items) =>
        items.map((candidate) =>
          candidate.id === updated.id ? updated : candidate,
        ),
      );
      if (session?.id === updated.id) setSession(updated);
      setSessionLifecycleNotice(
        `“${item.title}”已${next === "TRASHED" ? "移入回收站" : next === "ARCHIVED" ? "归档" : "恢复"}。`,
      );
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "研究记录状态更新失败",
      );
    } finally {
      setSessionLifecycleBusy(null);
      const origin = sessionLifecycleFocusRef.current;
      window.requestAnimationFrame(() => {
        if (origin?.isConnected) {
          origin.focus();
          return;
        }
        sessionHistoryFilterRefs.current.get(sessionHistoryStatus)?.focus();
      });
    }
  }

  async function toggleSessionPinned(item: ResearchSession) {
    setSessionLifecycleBusy(item.id);
    try {
      const updated = await updateResearchSession(item.id, {
        pinned: !item.pinned,
      });
      setSessions((items) =>
        items
          .map((candidate) =>
            candidate.id === updated.id ? updated : candidate,
          )
          .sort(
            (left, right) =>
              Number(Boolean(right.pinned)) - Number(Boolean(left.pinned)),
          ),
      );
      if (session?.id === updated.id) setSession(updated);
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "研究记录固定状态更新失败",
      );
    } finally {
      setSessionLifecycleBusy(null);
    }
  }

  async function applySessionBulkAction(action: ResearchSessionBulkAction) {
    if (!selectedSessionIds.length) return;
    const actionLabel =
      action === "ARCHIVE"
        ? "归档"
        : action === "TRASH"
          ? "移入回收站"
          : action === "RESTORE"
            ? "恢复"
            : action === "PIN"
              ? "固定"
              : "取消固定";
    if (
      typeof window !== "undefined" &&
      ["ARCHIVE", "TRASH"].includes(action) &&
      !window.confirm(
        `${actionLabel}所选 ${selectedSessionIds.length} 项研究记录？该操作会原子执行，历史结果与精确来源仍会保留。`,
      )
    )
      return;
    setSessionBulkBusy(true);
    try {
      await bulkUpdateResearchSessions(projectId, selectedSessionIds, action);
      const refreshed = await listResearchSessions(projectId);
      setSessions(refreshed);
      if (session) {
        const refreshedCurrent = refreshed.find(
          (candidate) => candidate.id === session.id,
        );
        if (refreshedCurrent) setSession(refreshedCurrent);
      }
      setSelectedSessionIds([]);
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "研究记录批量更新失败",
      );
    } finally {
      setSessionBulkBusy(false);
    }
  }

  function openSessionRename(item: ResearchSession) {
    setSessionRenameTarget(item);
    setSessionRenameValue(item.title);
  }

  async function renameSession() {
    if (!sessionRenameTarget || !sessionRenameValue.trim()) return;
    setSessionLifecycleBusy(sessionRenameTarget.id);
    try {
      const updated = await updateResearchSession(sessionRenameTarget.id, {
        title: sessionRenameValue.trim(),
      });
      setSessions((items) =>
        items.map((candidate) =>
          candidate.id === updated.id ? updated : candidate,
        ),
      );
      if (session?.id === updated.id) setSession(updated);
      setSessionRenameTarget(null);
      setSessionRenameValue("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "研究记录改名失败");
    } finally {
      setSessionLifecycleBusy(null);
    }
  }

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

  useEffect(() => {
    const jobId = job?.job_id;
    // An explicit ResearchTurn is the execution-state authority. Project
    // history may retain its related Job id for provenance/navigation, but
    // the legacy poller must not run alongside the Turn progress projection.
    if (agent2TurnId || !jobId || state !== "running") return;
    let active = true;
    let inFlight = false;
    let lastSeq = 0;
    let timer: number | undefined;
    const controller = new AbortController();
    const poll = async () => {
      if (!active || inFlight) return;
      inFlight = true;
      try {
        const [detail, nextEvents, nextArtifacts] = await Promise.all([
          getPlannerJob(jobId, { signal: controller.signal }),
          getPlannerJobEvents(jobId, lastSeq, { signal: controller.signal }),
          getPlannerJobArtifacts(jobId, { signal: controller.signal }),
        ]);
        if (!active) return;
        if (nextEvents.length) {
          lastSeq = Math.max(
            lastSeq,
            ...nextEvents.map((item) => item.seq || 0),
          );
          setEvents((items) => mergeJobEvents(items, nextEvents));
        }
        setArtifacts((items) => mergeArtifacts(items, nextArtifacts));
        const status = String(detail.status || "").toLowerCase();
        if (["completed", "partial_success", "failed"].includes(status)) {
          setState(
            status === "completed"
              ? "complete"
              : status === "partial_success"
                ? "partial"
                : "failed",
          );
          if (
            status === "failed" &&
            session?.id &&
            failedRunMessageRef.current !== jobId
          ) {
            failedRunMessageRef.current = jobId;
            void createResearchAssistantProjection(session.id, {
              phase: "failed",
              datasetName: scope?.dataset_name,
              datasetId: scope?.dataset_id,
              runId: jobId,
              failureCode: "JOB_FAILED",
            })
              .then(appendSessionMessage)
              .catch(() => {
                failedRunMessageRef.current = null;
              });
          }
          if (
            (status === "completed" || status === "partial_success") &&
            job.plan_hash
          ) {
            setInterpretationStatus("loading");
            void createScientificInterpretation(jobId, job.plan_hash)
              .then((result) => {
                if (!active) return;
                const nextInterpretation = result.interpretation || null;
                setInterpretation(nextInterpretation);
                if (nextInterpretation)
                  void getPlannerInterpretationEvidence(
                    nextInterpretation.interpretationId,
                  )
                    .then((nextEvidence) => {
                      if (active) setEvidence(nextEvidence);
                    })
                    .catch(() => {
                      if (active) setEvidence(null);
                    });
                setInterpretationStatus(
                  nextInterpretation
                    ? nextInterpretation.completeness === "COMPLETE"
                      ? "ready"
                      : "limited"
                    : "error",
                );
                if (session?.id && postRunMessageRef.current !== jobId) {
                  postRunMessageRef.current = jobId;
                  void createResearchAssistantProjection(session.id, {
                    phase: "post_run",
                    datasetName: scope?.dataset_name,
                    datasetId: scope?.dataset_id,
                    runId: jobId,
                  })
                    .then(appendSessionMessage)
                    .catch(() => {
                      postRunMessageRef.current = null;
                    });
                }
              })
              .catch(() => {
                if (active) setInterpretationStatus("error");
              });
          }
          return;
        }
        timer = window.setTimeout(poll, 1400);
      } catch (reason) {
        if (active && !requestWasAborted(reason)) {
          setError(
            reason instanceof Error ? reason.message : "无法更新分析进度",
          );
          timer = window.setTimeout(poll, 2500);
        }
      } finally {
        inFlight = false;
      }
    };
    void poll();
    return () => {
      active = false;
      controller.abort();
      if (timer) clearTimeout(timer);
    };
  }, [agent2TurnId, job, scope?.dataset_id, scope?.dataset_name, session?.id, state]);

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
      ),
    [messages, selectedTurnMessageId, showFullConversation, conversationWindowStart],
  );
  const hiddenConversationCount =
    conversationWindow.hiddenBefore + conversationWindow.hiddenAfter;

  useEffect(() => {
    setShowFullConversation(false);
    setConversationWindowStart(0);
  }, [session?.id, agent2TurnId]);
  const historicalRuns = (history?.analyses || []).filter(
    (item) => item.jobId !== job?.job_id,
  );
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
    !session || selectedSessionLifecycle === "active";
  useEffect(() => {
    if (
      !retryRequested ||
      !agent2TurnId ||
      !session?.id ||
      !selectedSessionIsWritable ||
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
    session?.id,
  ]);
  const starterPrompts = researchStarterPrompts(history);
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
    agent2Progress,
  });
  const researchLayoutMode = hasScientificWorkbenchContent
    ? "scientific-workbench"
    : "asking";
  useEffect(() => {
    if (conversationWidthCustomizedRef.current) return;
    const target = defaultResearchConversationWidth(
      hasScientificWorkbenchContent,
    );
    const workbenchWidth =
      workbenchRef.current?.getBoundingClientRect().width || 1280;
    const maximum = Math.min(760, Math.max(320, workbenchWidth - 480));
    setConversationWidth(Math.round(Math.min(maximum, Math.max(320, target))));
  }, [hasScientificWorkbenchContent]);
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
              <p>项目数据和研究记录没有丢失。请检查服务连接后重试。</p>
              <button
                type="button"
                className="product-primary-action"
                onClick={() => setReloadKey((value) => value + 1)}
              >
                重新加载
              </button>
              {pageLoadError ? (
                <details>
                  <summary>技术详情</summary>
                  <p>{pageLoadError}</p>
                </details>
              ) : null}
            </div>
          </section>
        </ProductShell>
      </RequireProductAuth>
    );
  return (
    <RequireProductAuth>
      <ProductShell projectId={projectId}>
        <a className="skip-link" href="#research-primary-content">
          跳到研究工作台
        </a>
        <section
          ref={workbenchRef}
          id="research-primary-content"
          tabIndex={-1}
          className="research-workbench"
          data-layout-mode={researchLayoutMode}
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
              onClick={() => setMobilePanel("workbench")}
            >
              工作台
            </button>
          </nav>
          <aside
            id="research-timeline-panel"
            role="tabpanel"
            aria-labelledby="research-timeline-tab"
            className={`conversation-pane ${mobilePanel === "timeline" ? "mobile-panel-active" : "mobile-panel-inactive"}`}
          >
            <header>
              <div className="research-timeline-heading">
                <p className="product-kicker">
                  {history?.project.name
                    ? `${scientistProjectLabel(history.project.name, projectId)} · 研究时间线`
                    : "项目研究 · 研究时间线"}
                </p>
                <h1>研究时间线</h1>
                {session?.title ? (
                  <strong className="research-timeline-session-title">
                    {session.title}
                  </strong>
                ) : null}
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
                {activeAgent2ContextManifest ? (
                  <button
                    type="button"
                    className="product-secondary-action"
                    aria-controls="research-context-manifest"
                    onClick={revealActiveContextManifest}
                  >
                    本次上下文
                  </button>
                ) : null}
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
                      disabled={sessionLifecycleBusy === session.id}
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
                          disabled={!filteredSessions.length || sessionBulkBusy}
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
                            disabled={sessionBulkBusy}
                            onClick={() => void applySessionBulkAction("PIN")}
                          >
                            列表置顶
                          </button>
                          <button
                            type="button"
                            disabled={sessionBulkBusy}
                            onClick={() => void applySessionBulkAction("UNPIN")}
                          >
                            取消列表置顶
                          </button>
                          {sessionHistoryStatus === "current" ? (
                            <button
                              type="button"
                              disabled={sessionBulkBusy}
                              onClick={() =>
                                void applySessionBulkAction("ARCHIVE")
                              }
                            >
                              归档所选
                            </button>
                          ) : (
                            <button
                              type="button"
                              disabled={sessionBulkBusy}
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
                              disabled={sessionBulkBusy}
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
                          description={`${item.pinned ? "列表置顶 · " : ""}${researchSessionStatusLabel(item.status)}`}
                          trailing={item.pinned ? "列表置顶" : undefined}
                          actions={canResearch ? [
                            {
                              label: item.pinned ? "取消列表置顶" : "列表置顶",
                              disabled: sessionLifecycleBusy === item.id,
                              onSelect: () => void toggleSessionPinned(item),
                            },
                            {
                              label: "重命名",
                              disabled: sessionLifecycleBusy === item.id,
                              onSelect: () => openSessionRename(item),
                            },
                            ...(status === "trashed"
                              ? [
                                  {
                                    label: "恢复研究记录",
                                    disabled: sessionLifecycleBusy === item.id,
                                    onSelect: () =>
                                      void changeSessionLifecycle(item, "ACTIVE"),
                                  },
                                ]
                              : status === "archived"
                                ? [
                                    {
                                      label: "恢复到当前研究",
                                      disabled: sessionLifecycleBusy === item.id,
                                      onSelect: () =>
                                        void changeSessionLifecycle(item, "ACTIVE"),
                                    },
                                    {
                                      label: "移入回收站",
                                      destructive: true,
                                      disabled: sessionLifecycleBusy === item.id,
                                      onSelect: () =>
                                        void changeSessionLifecycle(item, "TRASHED"),
                                    },
                                  ]
                                : [
                                    {
                                      label: "归档",
                                      disabled: sessionLifecycleBusy === item.id,
                                      onSelect: () =>
                                        void changeSessionLifecycle(item, "ARCHIVED"),
                                    },
                                    {
                                      label: "移入回收站",
                                      destructive: true,
                                      disabled: sessionLifecycleBusy === item.id,
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
            {branchChoices.length > 1 &&
            branchNavigation &&
            session?.id ? (
              <nav
                className="research-branch-switcher conversation-branch-switcher"
                aria-label="研究分支"
              >
                <span className="research-branch-switcher-label">研究分支</span>
                {branchNavigation.previous ? (
                  <Link
                    className="research-branch-step"
                    aria-label={`上一个研究分支：${researchBranchDescriptor(agent2Turns, branchNavigation.previous).title}`}
                    href={`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(branchNavigation.previous.id || branchNavigation.previous.turn_id)}`}
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
                <div className="research-branch-current">
                  <div>
                    <strong>
                      {branchNavigation.currentIndex + 1} /{" "}
                      {branchNavigation.choices.length}
                    </strong>
                    <span title={currentBranchDescriptor?.title}>
                      {currentBranchDescriptor?.title}
                    </span>
                  </div>
                  <small className="research-branch-source">
                    {currentBranchDescriptor?.sourceTitle
                      ? `源自“${currentBranchDescriptor.sourceTitle}”`
                      : currentBranchDescriptor?.sourceTurnId
                        ? "来源问题未在当前分支列表中"
                        : "原始研究问题"}
                  </small>
                </div>
                {branchNavigation.next ? (
                  <Link
                    className="research-branch-step"
                    aria-label={`下一个研究分支：${researchBranchDescriptor(agent2Turns, branchNavigation.next).title}`}
                    href={`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(branchNavigation.next.id || branchNavigation.next.turn_id)}`}
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
                <details className="research-branch-list">
                  <summary>查看全部 {branchDescriptors.length} 个分支</summary>
                  <ol>
                    {branchDescriptors.map((descriptor, index) => (
                      <li key={descriptor.turnId}>
                        <Link
                          href={`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(descriptor.turnId)}`}
                          aria-current={
                            descriptor.turnId === currentBranchDescriptor?.turnId
                              ? "page"
                              : undefined
                          }
                        >
                          <strong>
                            {index + 1}. {descriptor.title}
                          </strong>
                          <span>
                            {descriptor.sourceTitle
                              ? `源自“${descriptor.sourceTitle}”`
                              : descriptor.sourceTurnId
                                ? "来源问题未在当前列表中"
                                : "原始研究问题"}
                          </span>
                          <small>
                            ResearchTurn <code>{descriptor.turnId}</code>
                            {" · "}
                            消息修订 <code>{descriptor.messageRevisionId}</code>
                          </small>
                        </Link>
                      </li>
                    ))}
                  </ol>
                </details>
              </nav>
            ) : null}
            {sessionRenameTarget ? (
              <ProductModal
                eyebrow="研究记录"
                title="重命名研究"
                description="名称用于组织和检索，不会修改历史问题、ResearchTurn、科学结果或来源版本。"
                onClose={() => setSessionRenameTarget(null)}
                footer={
                  <>
                    <button
                      type="button"
                      className="product-secondary-action"
                      onClick={() => setSessionRenameTarget(null)}
                    >
                      取消
                    </button>
                    <button
                      type="button"
                      className="product-primary-action"
                      disabled={
                        !sessionRenameValue.trim() ||
                        sessionLifecycleBusy === sessionRenameTarget.id
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
                <label className="product-field">
                  <span>研究名称</span>
                  <input
                    value={sessionRenameValue}
                    maxLength={200}
                    onChange={(event) => setSessionRenameValue(event.target.value)}
                  />
                </label>
              </ProductModal>
            ) : null}
            <div className="conversation-history" ref={conversationHistoryRef}>
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
                        item.object_type ? (
                          <button
                            type="button"
                            className="research-memory-chip-remove"
                            aria-label={`从本会话上下文移除对象 ${item.display_name || `#${index + 1}`}`}
                            onClick={() => void removePinnedObject(item)}
                            disabled={sessionMemoryMutation}
                          >
                            ×
                          </button>
                        ) : null}
                      </span>
                    ))}
                    {sessionMemory.pinned_result_refs.map((resultId, index) => (
                      <span className="research-memory-chip" key={`result-${resultId}`}>
                        <span>上下文结果 {index + 1}</span>
                        <button
                          type="button"
                          className="research-memory-chip-remove"
                          aria-label={`从本会话上下文移除结果 ${index + 1}`}
                          onClick={() => void removePinnedResult(resultId)}
                          disabled={sessionMemoryMutation}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </section>
              ) : null}
              {sessionMemoryError ? (
                <p className="product-form-error research-memory-error" role="alert">
                  {sessionMemoryError}
                </p>
              ) : null}
              {agent2TurnId &&
              agent2ContextManifestLoadState === "error" &&
              !activeAgent2ContextManifest ? (
                <div className="research-memory-error" role="status">
                  <strong>本次研究的上下文清单暂时无法读取</strong>
                  <p>
                    研究结果和精确来源不会因此改变；重新读取只会检查已保存的上下文记录。
                  </p>
                  <button
                    type="button"
                    className="product-link-button"
                    onClick={() =>
                      setAgent2ContextManifestReloadKey((current) => current + 1)
                    }
                  >
                    重新读取上下文
                  </button>
                </div>
              ) : null}
              {activeAgent2ContextManifest ? (
                <details
                  ref={contextManifestRef}
                  id="research-context-manifest"
                  className="research-memory-strip research-context-manifest"
                  aria-label="本次研究使用的上下文"
                >
                  <summary>
                    <span>本次研究使用的上下文</span>
                    <small>
                      用于{contextOperationLabel(activeAgent2ContextManifest.operation)}
                      · {activeAgent2ContextManifest.included_items.length} 项
                    </small>
                  </summary>
                  <div className="research-context-manifest-summary">
                    <span>精确来源与版本已保留</span>
                    <span>
                      {activeAgent2ContextManifest.input_state === "ACTUAL"
                        ? "这是调用时实际使用的上下文"
                        : "这是发送前的上下文预览"}
                    </span>
                    <span data-state={activeAgent2ContextManifest.compaction_state}>
                      {activeAgent2ContextManifest.compaction_state === "COMPACTED"
                        ? "较早对话已压缩"
                        : "无需压缩"}
                    </span>
                    <span data-state={activeAgent2ContextManifest.truncation_state}>
                      {activeAgent2ContextManifest.truncation_state === "TRUNCATED"
                        ? "部分非关键上下文未纳入"
                        : "关键上下文完整"}
                    </span>
                  </div>
                  {agent2ContextManifests.length > 1 ? (
                    <div className="research-context-manifest-operations" role="group" aria-label="已记录的操作上下文">
                      {agent2ContextManifests.map((entry, index) => (
                        <span key={`${entry.operation}-${entry.manifest.context_manifest_id}`}>
                          {contextOperationSequenceLabel(
                            agent2ContextManifests,
                            index,
                          )}
                        </span>
                      ))}
                    </div>
                  ) : null}
                  {activeAgent2ContextManifest.included_items.length > 8 ? (
                    <button
                      type="button"
                      className="product-link-button research-context-manifest-toggle"
                      aria-controls="research-context-manifest-items"
                      aria-expanded={showFullContextManifest}
                      onClick={() => {
                        setShowFullContextManifest((current) => {
                          setContextManifestWindowStart(0);
                          return !current;
                        });
                      }}
                    >
                      {showFullContextManifest
                        ? "收起上下文列表"
                        : `查看全部上下文（${activeAgent2ContextManifest.included_items.length} 项）`}
                    </button>
                  ) : null}
                  <ul id="research-context-manifest-items">
                    {visibleContextManifestItems.map((item) => (
                        <li key={item.item_id}>
                          <strong>{contextKindLabel(item.kind)}</strong>
                          <div>
                            <span>
                              {contextInclusionReasonLabel(
                                item.inclusion_reason,
                              )}
                            </span>
                            <small>
                              {contextSelectionLabel(item.selection_mode)} ·{" "}
                              {contextRoleLabel(item.context_role)} ·{" "}
                              {contextItemSupportEligible(item)
                                ? "可支持科学主张"
                                : "不作为独立科学依据"}{" "}
                              · {contextAuthorityLabel(item.authority_class)} ·{" "}
                              {contextFreshnessLabel(item.freshness)}
                            </small>
                          </div>
                          {item.exact_object_version_id ? (
                            <details className="research-context-source">
                              <summary>来源版本已锁定</summary>
                              <code>{item.exact_object_version_id}</code>
                            </details>
                          ) : item.result_ref ? (
                            <details className="research-context-source">
                              <summary>结果身份已锁定</summary>
                              <code>{item.result_ref}</code>
                            </details>
                          ) : null}
                          {item.was_compacted || item.was_truncated ? (
                            <small className="research-context-transform">
                              {item.was_compacted ? "对话内容已安全压缩" : ""}
                              {item.was_compacted && item.was_truncated ? " · " : ""}
                              {item.was_truncated ? "非关键内容已裁剪" : ""}
                            </small>
                          ) : null}
                        </li>
                    ))}
                  </ul>
                  {showFullContextManifest ? (
                    <div className="research-context-manifest-window-controls">
                      {contextManifestWindowStart > 0 ? (
                        <button
                          type="button"
                          className="product-link-button research-context-manifest-toggle"
                          aria-controls="research-context-manifest-items"
                          onClick={() =>
                            setContextManifestWindowStart((current) =>
                              Math.max(0, current - CONTEXT_MANIFEST_RENDER_WINDOW),
                            )
                          }
                        >
                          查看上一组上下文
                        </button>
                      ) : null}
                      {contextManifestWindowStart + CONTEXT_MANIFEST_RENDER_WINDOW <
                      activeAgent2ContextManifest.included_items.length ? (
                        <button
                          type="button"
                          className="product-link-button research-context-manifest-toggle"
                          aria-controls="research-context-manifest-items"
                          onClick={() =>
                            setContextManifestWindowStart((current) =>
                              Math.min(
                                current + CONTEXT_MANIFEST_RENDER_WINDOW,
                                Math.max(
                                  0,
                                  activeAgent2ContextManifest.included_items.length -
                                    CONTEXT_MANIFEST_RENDER_WINDOW,
                                ),
                              ),
                            )
                          }
                        >
                          继续显示上下文（已显示 {contextManifestWindowStart + 1}–
                          {Math.min(
                            contextManifestWindowStart + CONTEXT_MANIFEST_RENDER_WINDOW,
                            activeAgent2ContextManifest.included_items.length,
                          )} / {activeAgent2ContextManifest.included_items.length}）
                        </button>
                      ) : null}
                    </div>
                  ) : null}
                  {activeAgent2ContextManifest.excluded_items.length ? (
                    <p className="research-context-manifest-excluded">
                      为保持本次研究聚焦，有 {activeAgent2ContextManifest.excluded_items.length}{" "}
                      项较低优先级内容未纳入；精确科学来源、版本、约束和量化事实不会被静默替换。
                    </p>
                  ) : null}
                  <details
                    className="research-context-technical"
                    aria-label="上下文审计详情"
                  >
                    <summary>审计详情</summary>
                    <dl>
                      <div>
                        <dt>上下文清单</dt>
                        <dd><code>{activeAgent2ContextManifest.context_manifest_id}</code></dd>
                      </div>
                      <div>
                        <dt>策略版本</dt>
                        <dd>{activeAgent2ContextManifest.policy_version}</dd>
                      </div>
                      {activeAgent2ContextManifest.invocation_role ? (
                        <div>
                          <dt>模型职责</dt>
                          <dd>{contextOperationLabel(activeAgent2ContextManifest.operation)}</dd>
                        </div>
                      ) : null}
                      {activeAgent2ContextManifest.prompt_template_version ? (
                        <div>
                          <dt>提示模板版本</dt>
                          <dd>{activeAgent2ContextManifest.prompt_template_version}</dd>
                        </div>
                      ) : null}
                      {activeAgent2ContextManifest.serialized_input_version ? (
                        <div>
                          <dt>输入表示版本</dt>
                          <dd>{activeAgent2ContextManifest.serialized_input_version}</dd>
                        </div>
                      ) : null}
                      <div>
                        <dt>输入预算</dt>
                        <dd>{activeAgent2ContextManifest.input_budget} tokens</dd>
                      </div>
                      <div>
                        <dt>实际估算</dt>
                        <dd>{activeAgent2ContextManifest.estimated_input_tokens} tokens</dd>
                      </div>
                      <div>
                        <dt>上下文指纹</dt>
                        <dd><code>{activeAgent2ContextManifest.context_fingerprint}</code></dd>
                      </div>
                    </dl>
                    {activeAgent2ContextManifest.excluded_items.length ? (
                      <ul className="research-context-manifest-exclusion-list">
                        {(activeAgent2ContextManifest.excluded_item_details || []).map((item) => (
                          <li key={`${item.item_id}-${item.reason}`}>
                            <strong>{item.item_id}</strong>：{item.detail}
                          </li>
                        ))}
                      </ul>
                    ) : null}
                    {activeAgent2ContextManifest.serialized_input ? (
                      <details className="research-context-serialized-input">
                        <summary>模型实际收到的有界表示</summary>
                        <pre>
                          {JSON.stringify(activeAgent2ContextManifest.serialized_input, null, 2)}
                        </pre>
                      </details>
                    ) : null}
                  </details>
                </details>
              ) : null}
              {showResearchStarter && history ? (
                <ResearchStarter
                  projectId={projectId}
                  datasetCount={history.datasets.length}
                  canResearch={canResearch}
                  projectStatus={projectLifecycle}
                  prompts={starterPrompts}
                  onTryQuestion={trySuggestedQuestion}
                />
              ) : null}
              {sessionLoadState === "loading" ? (
                <p className="conversation-load-state" role="status">
                  正在恢复研究对话…
                </p>
              ) : null}
              {sessionLoadState === "error" ? (
                <div className="conversation-load-state error" role="alert">
                  <strong>研究对话暂时无法读取</strong>
                  <p>已有分析结果没有丢失，请重新加载对话</p>
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
                      <p>{displayResearchMessage(message)}</p>
                    </article>
                  );
                })}
                {activeAgent2Progress ? (
                  <ResearchExecutionActivity
                    progress={activeAgent2Progress}
                    onCancel={() => void cancelAgent2Turn()}
                    cancelPending={agent2CancelPending}
                    onRetry={
                      selectedSessionIsWritable
                        ? () => void retryAgent2Turn()
                        : undefined
                    }
                    onContinue={
                      selectedSessionIsWritable
                        ? continueAgent2Research
                        : undefined
                    }
                    retryPending={agent2RetryPending}
                    onEdit={
                      selectedSessionIsWritable
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
                    <strong>已创建新的 ResearchTurn</strong>
                    <span>
                      这是一次新的执行 lineage；原未完成运行及其失败证据仍被保留，不会被覆盖。
                    </span>
                    <Link
                      className="product-link-button"
                      href={`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(retryLineage.source.turn_id)}`}
                    >
                      查看保留的原运行
                    </Link>
                    <details>
                      <summary>研究身份</summary>
                      <span>
                        新 ResearchTurn <code>{retryLineage.current.turn_id}</code>
                      </span>
                      <span>
                        来源 ResearchTurn <code>{retryLineage.source.turn_id}</code>
                      </span>
                    </details>
                  </section>
                ) : null}
                {agent2CancelNotice ? (
                  <p
                    className="research-cancel-notice"
                    role="status"
                    aria-live="polite"
                  >
                    {agent2CancelNotice}
                  </p>
                ) : null}
                {agent2ContinuationNotice ? (
                  <p
                    className="research-cancel-notice"
                    role="status"
                    aria-live="polite"
                  >
                    {agent2ContinuationNotice}
                  </p>
                ) : null}
                {error && activeAgent2Progress ? (
                  <p className="product-form-error" role="alert">
                    {error}
                  </p>
                ) : null}
                {agent2TurnId &&
                activeAgent2Progress &&
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
              {historicalRuns.length ? (
                <section className="timeline-past-runs" aria-label="历史研究">
                  {historicalRuns.slice(0, 6).map((run) => {
                    const status = effectiveResearchRunStatus(run);
                    return (
                      <Link
                        key={run.jobId}
                        href={researchRunHref(
                          projectId,
                          run.jobId,
                          sessions,
                          run.researchSessionId,
                          run.researchTurnId,
                        )}
                        className="timeline-past-run"
                      >
                        <span>
                          {run.archived
                            ? "已归档"
                            : status === "completed"
                              ? "✓ 分析完成"
                              : status === "partial"
                                ? "部分完成"
                                : status === "failed"
                                  ? "分析失败"
                                  : status === "canceled"
                                    ? "已取消"
                                    : "查看运行"}
                        </span>
                        <strong>{researchRunTitle(run)}</strong>
                        <small>
                          {run.stepCount} 个步骤 ·{" "}
                          {status === "failed" || status === "canceled"
                            ? "查看过程"
                            : "查看结果"}
                        </small>
                      </Link>
                    );
                  })}
                </section>
              ) : null}
            </div>
            {history &&
            canResearch &&
            sessionLoadState !== "error" &&
            selectedSessionIsWritable &&
            history.datasets.length ? (
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
                    className="research-edit-notice"
                    role={editingLoadState === "error" ? "alert" : "status"}
                  >
                    <strong>正在编辑上一条问题</strong>
                    <span>
                      {editingLoadState === "loading"
                        ? "正在读取原问题…"
                        : editingLoadState === "error"
                          ? "原问题暂时无法读取；为避免丢失历史上下文，编辑与提交已停用。"
                          : "提交后会创建新的研究分支，历史结果不会被修改。"}
                    </span>
                  </div>
                ) : null}
                <label htmlFor="research-question">
                  {editTurnId ? "编辑问题" : "询问此项目中的数据"}
                </label>
                {contextCandidateFromSearch && searchContextCandidateActive ? (
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
                          : `${activeViewerContext?.sourceRef.displayName || "检索中选择的科学数据"}，提交问题后才会进入实际 Context Used。`}
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
                <textarea
                  ref={questionInputRef}
                  id="research-question"
                  aria-label={editTurnId ? "编辑问题" : "询问此项目中的数据"}
                  aria-describedby={
                    [
                      editTurnId ? "research-edit-status" : null,
                      ["planning", "running"].includes(state) && agent2TurnId
                        ? "research-running-draft-status"
                        : null,
                    ]
                      .filter(Boolean)
                      .join(" ") || undefined
                  }
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="描述要比较、检查或解释的材料科学问题"
                  rows={3}
                  disabled={Boolean(editTurnId) && editingLoadState !== "ready"}
                />
                {["planning", "running"].includes(state) && agent2TurnId ? (
                  <p
                    id="research-running-draft-status"
                    className="research-composer-draft-status"
                  >
                    可以先起草下一条问题。草稿仅保存在当前浏览器标签页，刷新后可恢复；
                    不会修改或重新提交正在运行的研究。
                  </p>
                ) : null}
                <div className="research-composer-footer">
                  <label className="research-autonomy-control">
                    <input
                      type="checkbox"
                      checked={autonomyMode === "BOUNDED_AUTONOMOUS"}
                      onChange={(event) =>
                        setAutonomyMode(
                          event.target.checked
                            ? "BOUNDED_AUTONOMOUS"
                            : "STANDARD",
                        )
                      }
                      disabled={state === "planning" || state === "running"}
                    />
                    <span>有界多步研究</span>
                  </label>
                  <details className="research-model-menu">
                    <summary>
                      {providerLoadState === "loading"
                        ? "正在读取模型"
                        : selectedModel ||
                          selectedProviderOption?.label ||
                          "模型"}{" "}
                      ·{" "}
                      {thinkingMode === "deep"
                        ? "深入"
                        : thinkingMode === "quick"
                          ? "快速"
                          : "标准"}
                    </summary>
                    <div className="research-model-controls">
                      <label>
                        模型
                        <select
                          aria-label="本次分析模型"
                          value={selectedModel}
                          onChange={(event) =>
                            setSelectedModel(event.target.value)
                          }
                          disabled={!selectedModels.length}
                        >
                          {selectedModels.length ? (
                            selectedModels.map((item) => (
                              <option key={item} value={item}>
                                {item}
                              </option>
                            ))
                          ) : (
                            <option value="">由 Provider 决定</option>
                          )}
                        </select>
                      </label>
                      <label>
                        思考深度
                        <select
                          aria-label="思考深度"
                          value={thinkingMode}
                          onChange={(event) =>
                            setThinkingMode(
                              event.target.value as
                                | "quick"
                                | "standard"
                                | "deep",
                            )
                          }
                        >
                          <option value="quick">快速</option>
                          <option value="standard">标准</option>
                          <option value="deep">深入</option>
                        </select>
                      </label>
                    </div>
                  </details>
                  {["planning", "running"].includes(state) && agent2TurnId ? (
                    <button
                      type="button"
                      className="product-danger-action research-composer-stop"
                      aria-label="从输入区取消当前分析"
                      onClick={() => void cancelAgent2Turn()}
                      disabled={agent2CancelPending}
                    >
                      {agent2CancelPending ? "正在取消…" : "取消当前分析"}
                    </button>
                  ) : (
                    <button
                      type="submit"
                      className="product-primary-action"
                      disabled={
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
                          : "开始分析"}
                    </button>
                  )}
                </div>
                {autonomyMode === "BOUNDED_AUTONOMOUS" ? (
                  <p className="research-autonomy-preview" role="note">
                    Agent 可在固定边界内追加有科学依据的分析；问题得到回答、证据不足或达到研究上限时会停止。你仍可随时取消当前分析。
                  </p>
                ) : null}
                {providerLoadState === "error" ? (
                  <div className="research-provider-notice" role="alert">
                    <span>
                      模型状态暂时无法读取；提交时会由服务端再次验证。
                    </span>
                    <button
                      type="button"
                      className="product-link-button"
                      onClick={() => setProviderReloadKey((value) => value + 1)}
                    >
                      重试
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
                正在确认项目权限…
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
            aria-valuemax={760}
            aria-valuenow={conversationWidth}
            aria-valuetext={`${conversationWidth} 像素对话宽度`}
            onPointerDown={(event) => {
              conversationWidthCustomizedRef.current = true;
              event.currentTarget.setPointerCapture(event.pointerId);
              setConversationWidth(
                clampConversationWidth(
                  event.clientX -
                    (workbenchRef.current?.getBoundingClientRect().left || 0),
                ),
              );
            }}
            onPointerMove={(event) => {
              if (event.currentTarget.hasPointerCapture(event.pointerId))
                setConversationWidth(
                  clampConversationWidth(
                    event.clientX -
                      (workbenchRef.current?.getBoundingClientRect().left || 0),
                  ),
                );
            }}
            onPointerUp={(event) => {
              if (event.currentTarget.hasPointerCapture(event.pointerId))
                event.currentTarget.releasePointerCapture(event.pointerId);
            }}
            onKeyDown={(event) => {
              if (event.key === "ArrowLeft") {
                event.preventDefault();
                conversationWidthCustomizedRef.current = true;
                setConversationWidth((value) =>
                  clampConversationWidth(value - 16),
                );
              }
              if (event.key === "ArrowRight") {
                event.preventDefault();
                conversationWidthCustomizedRef.current = true;
                setConversationWidth((value) =>
                  clampConversationWidth(value + 16),
                );
              }
              if (event.key === "Home") {
                event.preventDefault();
                conversationWidthCustomizedRef.current = true;
                setConversationWidth(clampConversationWidth(320));
              }
              if (event.key === "End") {
                event.preventDefault();
                conversationWidthCustomizedRef.current = true;
                setConversationWidth(clampConversationWidth(760));
              }
            }}
          />
          <section
            id="research-workbench-panel"
            role="tabpanel"
            aria-labelledby="research-workbench-tab"
            className={`research-workbench-pane ${mobilePanel === "workbench" ? "mobile-panel-active" : "mobile-panel-inactive"}`}
          >
            {hasAuthoritativeTurnPresentation ? (
              <>
                <Agent2ScientificPresentation
                  turnId={agent2TurnId as string}
                  projectId={projectId}
                  sessionId={session?.id}
                  sessionMemory={sessionMemory}
                  onSessionMemoryChange={setSessionMemory}
                />
                <LiteratureEvidencePanel
                  projectId={projectId}
                  turnId={agent2TurnId as string}
                />
              </>
            ) : null}
            {!hasAuthoritativeTurnPresentation ? (
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
                history={history}
                onConfirmScope={confirmScope}
                onTryQuestion={trySuggestedQuestion}
              />
            ) : null}
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

async function createScientificInterpretation(jobId: string, planHash: string) {
  try {
    const strict = await createPlannerJobInterpretation(jobId, planHash, {
      mode: "STRICT_PROVIDER",
      idempotencyKey: `research-scientific-interpretation:${jobId}`,
    });
    if (strict.interpretation) return strict;
  } catch {
    // A grounded deterministic interpretation keeps verified results readable
    // when the configured provider is temporarily unavailable.
  }
  return createPlannerJobInterpretation(jobId, planHash, {
    mode: "DETERMINISTIC",
    idempotencyKey: `research-deterministic-interpretation:${jobId}`,
  });
}

function ResearchStarter({
  projectId,
  datasetCount,
  canResearch,
  projectStatus,
  prompts,
  onTryQuestion,
}: {
  projectId: string;
  datasetCount: number;
  canResearch: boolean;
  projectStatus: string;
  prompts: ResearchStarterPrompt[];
  onTryQuestion: (question: string) => void;
}) {
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
      <h2 id="research-starter-title">从 {datasetCount} 个项目数据集开始</h2>
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
  history,
  onConfirmScope,
  onTryQuestion,
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
  history: ProjectHistory | null;
  onConfirmScope: (datasetId: string) => Promise<void>;
  onTryQuestion: (question: string) => void;
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
  if (state === "clarification")
    return <ClarificationState scope={scope} onConfirm={onConfirmScope} />;
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
        <p className="product-kicker">当前研究上下文</p>
        <h2>项目数据与最近研究</h2>
        <p>这里保留可用于分析的数据范围，以及已经完成的研究结果。</p>
        <section className="research-idle-section">
          <header>
            <strong>项目数据</strong>
            <span>{history?.datasets.length || 0} 个数据集</span>
          </header>
          {history?.datasets.slice(0, 4).map((dataset) => (
            <Link
              key={dataset.datasetId}
              href={`/projects/${projectId}/data?dataset=${dataset.datasetId}`}
              className="research-context-row"
            >
              <strong>{dataset.name}</strong>
              <span>
                {dataset.profile?.rowCount ??
                  dataset.profile?.objectCount ??
                  "—"}{" "}
                个记录 ·{" "}
                {researchDatasetTypeLabel(dataset.profile?.datasetType)}
              </span>
            </Link>
          ))}
          {!history?.datasets.length && (
            <p className="research-context-empty">
              上传数据后，可在这里查看当前研究范围。
            </p>
          )}
        </section>
        <section className="research-idle-section">
          <header>
            <strong>最近研究</strong>
            <Link href={`/projects/${projectId}/reports`}>查看报告</Link>
          </header>
          {history?.analyses.slice(0, 3).map((run) => (
            <Link
              key={run.jobId}
              href={researchRunHref(
                projectId,
                run.jobId,
                [],
                run.researchSessionId,
                run.researchTurnId,
              )}
              className="research-context-row"
            >
              <strong>{researchRunTitle(run)}</strong>
              <span>
                {researchSessionStatusLabel(effectiveResearchRunStatus(run))}
              </span>
            </Link>
          ))}
          {!history?.analyses.length && (
            <p className="research-context-empty">
              完成第一次研究后，结果会保留在这里。
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
      <section className="live-results">
        <div className="result-heading">
          <h3>{state === "running" ? "本次分析" : "主要结果"}</h3>
          <span>
            {resultArtifacts.length
              ? `${resultArtifacts.length} 个科学输出`
              : scope?.dataset_name || ""}
          </span>
        </div>
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
            正在读取已持久化科学结果…
          </div>
        ) : (
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
          <details className="report-supporting-results">
            <summary>支持性结果 · {supportingArtifacts.length} 项</summary>
            <div className="report-artifact-list">
              {supportingArtifacts.map((artifact) => (
                <ResearchArtifactFigure
                  key={artifact.artifactId || artifact.id}
                  artifact={artifact}
                  highlighted={
                    artifactReference(artifact) === highlightedArtifactId
                  }
                  projectId={projectId}
                  datasetId={datasetId}
                  jobId={jobId}
                  artifacts={artifacts}
                      />
                    ))}
                  </div>
          </details>
        ) : null}
        {(state === "complete" || state === "partial") && (
          <section className="finding-block">
            <h3>主要发现</h3>
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
                本次分析已生成可复核的图表与数据表；当前解释没有足够的用户级科学结论。
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
                    ? "科学结论暂时无法读取；结果仍可查看。"
                    : "解释仅适用于本次分析所使用的数据与证据。")}
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
  highlighted = false,
  projectId,
  datasetId,
  jobId,
  artifacts,
}: {
  artifact: ProjectedScientificArtifact;
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
      <header className="artifact-result-heading">
        <span>
          {artifact.resultRole === "PRIMARY_FIGURE"
            ? "权威图表"
            : artifact.resultRole === "PRIMARY_TABLE"
              ? "权威数据表"
              : artifactLabel(artifact.type)}
        </span>
        <strong>{artifact.resultTitle}</strong>
      </header>
      {jobId ? (
        <LazyScientificResultViewer
          projectId={projectId}
          datasetId={datasetId}
          jobId={jobId}
          selected={artifact}
          artifacts={artifacts}
        />
      ) : null}
      <p>
        {artifact.resultRole === "PRIMARY_FIGURE" ||
        artifact.resultRole === "PRIMARY_TABLE"
          ? "图表与单位来自本次分析的已验证结果。"
          : "支持性科学输出，供结果复核使用。"}
      </p>
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
              : state === "partial"
                ? "部分完成 · 查看过程"
                : state === "planning"
                  ? "正在准备分析方案"
                  : "分析中 · 查看过程"}
      </summary>
      <div className="timeline-process-body" role="status">
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
                    : stepState === "active"
                      ? "●"
                      : "○"}
                </span>
                <div>
                  <strong>{projection.purpose}</strong>
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
): "complete" | "active" | "pending" {
  if (state === "complete") return "complete";
  if (stepId && completedSteps.has(stepId)) return "complete";
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
  return "研究请求暂时无法完成。没有创建新的分析运行；已完成的科学结果仍然保留。";
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
  let text = message.content;
  if (message.payload?.messageKind === "ASSISTANT_FINAL") {
    const scientificBody = text
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
        finding: `在 ${fitWindow} 内，限定扩散系数为 ${displayEvidenceValue(diffusionEstimate)}${diagnostics.length ? `（${diagnostics.join("，")}）` : ""}；轨迹末端 ${displayEvidenceValue(value("trajectory.msd.last_lag"))} 的总 MSD 为 ${displayEvidenceValue(value("trajectory.msd.last_total"))}${rdfClause}。`,
        limitation:
          "该扩散系数只对用户显式选择的拟合窗口、当前轨迹与采样条件有效，不是无条件的长时间体扩散系数。",
      };
    }
    return {
      finding: `在 ${displayEvidenceValue(value("trajectory.msd.last_lag"))} 的末端时滞处，总 MSD 为 ${displayEvidenceValue(value("trajectory.msd.last_total"))}${rdfClause}。`,
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

function ClarificationState({
  scope,
  onConfirm,
}: {
  scope: ScopeResolution | null;
  onConfirm: (datasetId: string) => Promise<void>;
}) {
  const candidates = scope?.candidates || [];
  const [selected, setSelected] = useState(candidates[0]?.dataset_id || "");
  return (
    <div className="research-state">
      <p className="product-kicker">需要确认</p>
      <h2>本次分析可以使用多个数据集。</h2>
      <p>{scope?.reason || "请选择本次主要分析数据。"}</p>
      {candidates.length ? (
        <fieldset>
          <legend>选择本次主要分析数据</legend>
          {candidates.map((candidate) => (
            <label key={candidate.dataset_id}>
              <input
                type="radio"
                name="scope-dataset"
                value={candidate.dataset_id}
                checked={selected === candidate.dataset_id}
                onChange={() => setSelected(candidate.dataset_id)}
              />
              {candidate.name} · {candidate.semantics.join("、")}
            </label>
          ))}
        </fieldset>
      ) : null}
      <p className="product-form-hint">
        确认后会在当前研究会话中继续，不会创建跨数据集的单个运行。
      </p>
      <button
        className="product-primary-action"
        disabled={!selected}
        onClick={() => void onConfirm(selected)}
      >
        确认数据范围
      </button>
    </div>
  );
}

export { artifactLabel, displayEvidenceValue, evidenceLabel, formatPercent, researchRunHref, researchSessionReferencesRun, userFacingClaims, userFacingLimitations };
