"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useEffect, useMemo, useRef, useState, type CSSProperties, type KeyboardEvent as ReactKeyboardEvent } from "react";
import { archiveProjectRun, createPlannerJob, createPlannerJobInterpretation, getPlannerInterpretationEvidence, getPlannerJob, getPlannerJobArtifacts, getPlannerJobEvents, getPlannerJobInterpretations, getPlannerProviderStatus, listPlannerProviders, getProjectHistory, restoreProjectRun, type Artifact, type GroundedScientificInterpretation, type InterpretationEvidenceResponse, type JobEvent, type PlannerJobCreateResult, type PlannerJobDetail, type ProjectHistory, type ProviderOption, type ProviderStatus } from "../lib/planner-api";
import { createResearchAssistantProjection, createResearchMessage, createResearchSession, getResearchSession, listResearchSessions, resolveResearchScope, type ResearchMessage, type ResearchSession, type ScopeResolution } from "../lib/product-api";
import { ProductShell, RequireProductAuth } from "./ProductShell";
import { ScientificResultViewer } from "./ScientificViewerAdapter";
import { projectScientificArtifacts, scientificResultTitle, type ProjectedScientificArtifact } from "../lib/scientific-result-projection";
import { compileScientificPresentation } from "../lib/scientific-presentation";
import { ScientificPresentationBlocks } from "./ScientificPresentationBlocks";
import { Agent2ScientificPresentation } from "./Agent2ScientificPresentation";
import { getReportComposition, listReportCompositions, type ReportEditorialProjection } from "../lib/report-composition-api";
import { researchRunTitle } from "../lib/research-display";
import { cancelAgent2Execution, getAgent2ExecutionProgress, type Agent2ProgressView } from "../lib/agent2-execution-api";
import { ResearchExecutionActivity } from "./ResearchExecutionActivity";
import { getAgent2SessionMemory, type Agent2SessionMemory } from "../lib/agent2-memory-api";
import { ScientificReportAction } from "./ScientificReportAction";
import { createAgent2ResearchTurn, dispatchAgent2ResearchTurn, getAgent2ContextManifest, getAgent2ResearchTurnResult, listAgent2ResearchTurns, type Agent2ContextManifest, type Agent2ResearchTurnResult, type Agent2TurnResponse } from "../lib/agent2-research-api";
import { decodeWorkspaceSelectionUrl } from "./workspace/workspace-selection-contract";
import { apiSemanticLocator, scientificSelectionFromWorkspace, selectionToResearchObjectRef } from "./scientific-viewer/scientificSelection";
import { resolveScientificViewer } from "./scientific-viewer/scientificViewerRegistry";

type ResearchState = "idle" | "planning" | "running" | "complete" | "partial" | "failed" | "unsupported" | "clarification" | "capability-clarification";

export type ResearchTechnicalSummary = {
  runId: string | null;
  planId: string | null;
  outputCount: number;
  structuredOutputCount: number;
  structuredOutputLabel: string;
};

type ResearchStarterPrompt = {
  id: string;
  question: string;
};

const RESEARCH_STARTER_CATALOG: Array<ResearchStarterPrompt & { signals: string[] }> = [
  { id: "experimental-xrd", question: "比较实验与理论 XRD", signals: ["structure_experimental_xrd_comparison", "experimental_xrd_comparison"] },
  { id: "trajectory", question: "查看 AIMD 轨迹并概览结构演化", signals: ["trajectory_visualization", "trajectory_rdf", "trajectory"] },
  { id: "phonon", question: "查看声子能带与态密度", signals: ["phonon_visualization", "phonon"] },
  { id: "electronic", question: "查看电子能带与态密度", signals: ["electronic_band_structure", "electronic_dos", "electronicband", "electronicdos", "electronic"] },
  { id: "volumetric", question: "查看体数据的等值面与切片", signals: ["volumetric_visualization", "structure_volumetric_data", "volumetric", "charge_density", "elf"] },
  { id: "local-environment", question: "分析局部配位环境", signals: ["structure_local_environment_polyhedra", "local_environment_polyhedra"] },
  { id: "structure", question: "概览结构组成与晶格", signals: ["structure_summary", "dataset_structure_statistics", "crystal_structure"] },
  { id: "regression", question: "评估材料属性回归结果", signals: ["regression_evaluation", "regression_target", "regression_prediction"] },
  { id: "uncertainty", question: "评估预测不确定性", signals: ["uncertainty_evaluation", "regression_uncertainty"] },
  { id: "classification", question: "评估材料分类结果", signals: ["classification_evaluation", "classification_target", "classification_prediction"] },
  { id: "composition", question: "查看材料组成分布", signals: ["composition_space", "composition_summary", "material_formula"] },
];

function normalizeResearchSignal(value: string): string {
  return value.trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}

/** Resolve sibling research branches from the persisted Turn relation. */
export function researchBranchChoices(turns: Agent2TurnResponse[], currentTurnId?: string): Agent2TurnResponse[] {
  if (!currentTurnId) return [];
  const current = turns.find((turn) => turn.id === currentTurnId || turn.turn_id === currentTurnId);
  if (!current) return [];
  const rootId = current.parent_turn_id || current.turn_id;
  const root = turns.find((turn) => turn.id === rootId || turn.turn_id === rootId);
  const choices = turns.filter((turn) => (turn.parent_turn_id || turn.turn_id) === rootId);
  if (root && !choices.some((turn) => (turn.id || turn.turn_id) === (root.id || root.turn_id))) choices.unshift(root);
  if (choices.length <= 1) return [];
  return [...choices].sort((left, right) => left.sequence_no - right.sequence_no);
}

/** Build inert starter questions only from the already-authorized Project History projection. */
export function researchStarterPrompts(history: ProjectHistory | null): ResearchStarterPrompt[] {
  if (!history?.datasets.length) return [];
  const signals = new Set<string>();
  const semanticRoles = new Set<string>();
  for (const dataset of history.datasets) {
    const profile = dataset.profile;
    for (const value of Object.keys(profile?.semanticRoles || {})) {
      const normalized = normalizeResearchSignal(value);
      if (normalized) semanticRoles.add(normalized);
    }
    for (const value of [profile?.datasetType, ...(profile?.readyCapabilities || []), ...semanticRoles]) {
      if (value) signals.add(normalizeResearchSignal(String(value)));
    }
  }
  const hasSignal = (candidate: string) => signals.has(candidate);
  const prompts: ResearchStarterPrompt[] = [];
  for (const candidate of RESEARCH_STARTER_CATALOG) {
    if (candidate.signals.some(hasSignal) && !prompts.some((prompt) => prompt.question === candidate.question)) {
      prompts.push({ id: candidate.id, question: candidate.question });
    }
    if (prompts.length === 3) break;
  }
  if (prompts.length < 3 && semanticRoles.has("formation_energy") && semanticRoles.has("band_gap")) {
    prompts.push({ id: "formation-energy-band-gap", question: "比较 formation energy 与 band gap 的关系" });
  }
  return prompts.length ? prompts.slice(0, 3) : [{ id: "project-overview", question: "概览当前项目数据与可用分析" }];
}

/** Expose audit metadata without loading or rendering secret-bearing payloads. */
export function researchTechnicalSummary(job: PlannerJobCreateResult | null, artifacts: Artifact[], resultArtifacts: ProjectedScientificArtifact[] = projectScientificArtifacts(artifacts)): ResearchTechnicalSummary {
  const structuredOutputs = artifacts.filter((artifact) => {
    const type = String(artifact.type || "").toLowerCase();
    const contentType = String(artifact.contentType || "").toLowerCase();
    return contentType.includes("json") || type.endsWith("_json") || type === "json";
  });
  const names = structuredOutputs.map((artifact) => String(artifact.name || "").trim()).filter(Boolean).slice(0, 3);
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

function canWriteProject(role?: string | null) {
  return role === "owner" || role === "admin" || role === "researcher";
}

function researchRunState(status: string | null | undefined): ResearchState {
  const normalized = String(status || "").toLowerCase();
  if (["completed", "complete", "ready", "succeeded", "success"].includes(normalized)) return "complete";
  if (["partial_success", "partial", "degraded"].includes(normalized)) return "partial";
  if (["failed", "error", "cancelled", "canceled"].includes(normalized)) return "failed";
  if (["queued", "created", "planning", "pending"].includes(normalized)) return "planning";
  if (["running", "active", "started"].includes(normalized)) return "running";
  return "failed";
}

function researchSessionReferencesRun(session: ResearchSession, runId: string, phase?: string): boolean {
  if (!phase && (session.runIds || []).includes(runId)) return true;
  return (session.messages || []).some((message) => {
    const payload = message.payload || {};
    return payload.runId === runId && (!phase || payload.phase === phase);
  });
}

function researchRunHref(projectId: string, runId: string, sessions: ResearchSession[], researchSessionId?: string, researchTurnId?: string | null): string {
  const owner = researchSessionId
    ? sessions.find((item) => item.id === researchSessionId) || { id: researchSessionId } as ResearchSession
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
function researchSessionHref(projectId: string, sessionId: string, history: ProjectHistory | null): string {
  const related = (history?.analyses || [])
    .filter((run) => run.researchSessionId === sessionId)
    .sort((left, right) =>
      String(right.updatedAt || right.createdAt || "").localeCompare(
        String(left.updatedAt || left.createdAt || ""),
      ),
    )[0];
  return related
    ? researchRunHref(projectId, related.jobId, [], sessionId, related.researchTurnId)
    : `/projects/${projectId}/research/${encodeURIComponent(sessionId)}`;
}

type ViewerResearchContext = { objectId?: string; versionId?: string; objectType?: string; displayName?: string; selectionToken?: string; selectionLabel?: string };

export function ResearchPage({ projectId, sessionId, runId, agent2TurnId, editTurnId, viewerContext }: { projectId: string; sessionId?: string; runId?: string; agent2TurnId?: string; editTurnId?: string; viewerContext?: ViewerResearchContext }) {
  const router = useRouter();
  const [session, setSession] = useState<ResearchSession | null>(null);
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [history, setHistory] = useState<ProjectHistory | null>(null);
  const [question, setQuestion] = useState("");
  const [state, setState] = useState<ResearchState>("idle");
  const [scope, setScope] = useState<ScopeResolution | null>(null);
  const [job, setJob] = useState<PlannerJobCreateResult | null>(null);
  const [events, setEvents] = useState<JobEvent[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [interpretation, setInterpretation] = useState<GroundedScientificInterpretation | null>(null);
  const [evidence, setEvidence] = useState<InterpretationEvidenceResponse | null>(null);
  const [interpretationStatus, setInterpretationStatus] = useState<"idle" | "loading" | "ready" | "limited" | "error">("idle");
  const [error, setError] = useState("");
  const [agent2Progress, setAgent2Progress] = useState<Agent2ProgressView | null>(null);
  const [agent2ContextManifest, setAgent2ContextManifest] = useState<Agent2ContextManifest | null>(null);
  const [agent2CancelPending, setAgent2CancelPending] = useState(false);
  const [agent2RetryPending, setAgent2RetryPending] = useState(false);
  const [editingResult, setEditingResult] = useState<Agent2ResearchTurnResult | null>(null);
  const [editingLoadState, setEditingLoadState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const agent2DispatchRef = useRef<string | null>(null);
  const [sessionMemory, setSessionMemory] = useState<Agent2SessionMemory | null>(null);
  const [agent2Turns, setAgent2Turns] = useState<Agent2TurnResponse[]>([]);
  const [conversationWidth, setConversationWidth] = useState(420);
  const [sessionHistoryOpen, setSessionHistoryOpen] = useState(false);
  const [sessionHistoryQuery, setSessionHistoryQuery] = useState("");
  const [mobilePanel, setMobilePanel] = useState<"timeline" | "workbench">(runId ? "workbench" : "timeline");
  const [pageLoadState, setPageLoadState] = useState<"loading" | "ready" | "error">("loading");
  const [pageLoadError, setPageLoadError] = useState("");
  const [sessionLoadState, setSessionLoadState] = useState<"ready" | "loading" | "error">("ready");
  const [sessionLoadError, setSessionLoadError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const postRunMessageRef = useRef<string | null>(null);
  const failedRunMessageRef = useRef<string | null>(null);
  const [providerStatus, setProviderStatus] = useState<ProviderStatus | null>(null);
  const [providerOptions, setProviderOptions] = useState<ProviderOption[]>([]);
  const [providerLoadState, setProviderLoadState] = useState<"loading" | "ready" | "error">("loading");
  const [providerReloadKey, setProviderReloadKey] = useState(0);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [thinkingMode, setThinkingMode] = useState<"quick" | "standard" | "deep">("standard");
  const questionInputRef = useRef<HTMLTextAreaElement | null>(null);
  const workbenchRef = useRef<HTMLElement | null>(null);
  const sessionHistoryTriggerRef = useRef<HTMLButtonElement | null>(null);
  const sessionHistoryRef = useRef<HTMLDivElement | null>(null);
  const sessionHistorySearchRef = useRef<HTMLInputElement | null>(null);
  const mobileTimelineTabRef = useRef<HTMLButtonElement | null>(null);
  const mobileWorkbenchTabRef = useRef<HTMLButtonElement | null>(null);
  const exactViewerContext = useMemo(() => {
    if (!viewerContext?.objectId || !viewerContext.versionId || !viewerContext.objectType) return null;
    const sourceRef = { projectId, objectId: viewerContext.objectId, versionId: viewerContext.versionId, objectType: viewerContext.objectType, displayName: viewerContext.displayName || "所选科学数据" };
    if (!viewerContext.selectionToken) return { sourceRef, selection: null };
    try {
      const workspace = decodeWorkspaceSelectionUrl(viewerContext.selectionToken);
      const descriptor = resolveScientificViewer({ objectType: viewerContext.objectType });
      return { sourceRef, selection: scientificSelectionFromWorkspace(workspace, sourceRef, descriptor.viewerId) };
    } catch { return { sourceRef, selection: null }; }
  }, [projectId, viewerContext]);

  useEffect(() => {
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
  }, []);

  useEffect(() => {
    if (!agent2TurnId) { setAgent2Progress(null); return; }
    agent2DispatchRef.current = null;
    let active = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const refresh = () => {
      void getAgent2ExecutionProgress(agent2TurnId).then((next) => {
        if (!active) return;
        setAgent2Progress(next);
        if (next.status === "PLAN_READY" && agent2DispatchRef.current !== agent2TurnId) {
          agent2DispatchRef.current = agent2TurnId;
          void dispatchAgent2ResearchTurn(agent2TurnId).catch((reason) => {
            if (active) setError(reason instanceof Error ? reason.message : "研究执行失败");
          });
        }
        if (["ORCHESTRATING", "READY_TO_PLAN", "PLANNING", "PLAN_READY", "QUEUED", "RUNNING", "CANCELING", "RESULT_PENDING", "RESULT_READY", "INTERPRETING"].includes(next.status)) timer = setTimeout(refresh, 1800);
      }).catch(() => { if (active) setAgent2Progress(null); });
    };
    refresh();
    const onOnline = () => refresh();
    window.addEventListener("online", onOnline);
    return () => {
      active = false;
      window.removeEventListener("online", onOnline);
      if (timer) clearTimeout(timer);
    };
  }, [agent2TurnId]);

  useEffect(() => {
    if (!agent2TurnId) { setAgent2ContextManifest(null); return; }
    let active = true;
    void getAgent2ContextManifest(agent2TurnId)
      .then((detail) => { if (active) setAgent2ContextManifest(detail.manifest); })
      .catch(() => { if (active) setAgent2ContextManifest(null); });
    return () => { active = false; };
  }, [agent2TurnId, agent2Progress?.status]);

  useEffect(() => {
    if (!session?.id) { setSessionMemory(null); return; }
    let active = true;
    void getAgent2SessionMemory(projectId, session.id)
      .then((memory) => { if (active) setSessionMemory(memory); })
      .catch(() => { if (active) setSessionMemory(null); });
    return () => { active = false; };
  }, [projectId, session?.id]);

  useEffect(() => {
    if (!session?.id || !agent2TurnId) {
      setAgent2Turns([]);
      return;
    }
    let active = true;
    void listAgent2ResearchTurns(projectId, session.id)
      .then((items) => { if (active) setAgent2Turns(items); })
      .catch(() => { if (active) setAgent2Turns([]); });
    return () => { active = false; };
  }, [projectId, session?.id, agent2TurnId]);

  useEffect(() => {
    if (!editTurnId) {
      setEditingResult(null);
      setEditingLoadState("idle");
      return;
    }
    let active = true;
    setEditingLoadState("loading");
    void getAgent2ResearchTurnResult(editTurnId).then((next) => {
      if (!active) return;
      setEditingResult(next);
      setQuestion(next.research_question);
      setEditingLoadState("ready");
    }).catch(() => {
      if (!active) return;
      setEditingResult(null);
      setEditingLoadState("error");
      setError("原研究问题暂时无法读取，历史结果仍保持不变。");
    });
    return () => { active = false; };
  }, [editTurnId]);

  async function cancelAgent2Turn() {
    if (!agent2TurnId || agent2CancelPending) return;
    setAgent2CancelPending(true);
    try {
      const result = await cancelAgent2Execution(agent2TurnId);
      setAgent2Progress((current) => current ? { ...current, status: result.status } : current);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "取消请求未能提交");
    } finally {
      setAgent2CancelPending(false);
    }
  }

  async function retryAgent2Turn() {
    if (!agent2TurnId || !session || agent2RetryPending) return;
    const previousQuestion = [...(session.messages || [])].reverse().find((message) => message.role === "user")?.content?.trim();
    if (!previousQuestion) {
      setError("原研究问题暂时无法读取，无法安全重试。");
      return;
    }
    setAgent2RetryPending(true);
    setError("");
    try {
      const next = await createAgent2ResearchTurn(projectId, session.id, {
        message: previousQuestion,
        reply_to_turn_id: agent2TurnId,
        ui_context: {
          active_object_refs: [],
          selection_refs: [],
          scientific_selections: [],
          explicit_object_refs: [],
          explicit_result_ids: [],
          explicit_finding_refs: [],
        },
      });
      router.push(`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(next.turn_id)}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "重试请求未能提交");
    } finally {
      setAgent2RetryPending(false);
    }
  }

  function clampConversationWidth(value: number): number {
    if (!Number.isFinite(value)) return conversationWidth;
    const workbenchWidth = workbenchRef.current?.getBoundingClientRect().width || 1280;
    const maximum = Math.min(640, Math.max(320, workbenchWidth - 480));
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
    setMobilePanel(runId ? "workbench" : "timeline");
    setPageLoadState("loading");
    setPageLoadError("");
    void Promise.all([listResearchSessions(projectId), getProjectHistory(projectId)]).then(([items, nextHistory]) => {
      if (!active) return;
      setSessions(items);
      setHistory(nextHistory);
      setPageLoadState("ready");
      const runSession = runId ? items.find((item) => researchSessionReferencesRun(item, runId)) : undefined;
      // An explicit session id is an authoritative navigation target. When a
      // historical run is not yet normalized onto that session, retain the
      // requested session rather than turning a valid route into a missing
      // conversation error. A run-only route still requires an explicit
      // persisted run binding and must not fall back to an unrelated session.
      const selected = runId
        ? runSession || (sessionId ? items.find((item) => item.id === sessionId) : undefined)
        : sessionId
          ? items.find((item) => item.id === sessionId)
          : items[0];
      if (selected) {
        setSessionLoadState("loading");
        setSessionLoadError("");
        void getResearchSession(selected.id).then((full) => {
          if (!active) return;
          setSession(full);
          setSessionLoadState("ready");
        }).catch((reason) => {
          if (!active) return;
          setSession(null);
          setSessionLoadState("error");
          setSessionLoadError(reason instanceof Error ? reason.message : "研究会话暂时无法读取");
        });
      } else {
        setSessionLoadState(sessionId ? "error" : "ready");
        setSessionLoadError(sessionId ? "研究会话不存在或已不可访问。" : "");
      }
      if (runId) {
        const historicalRun = nextHistory.analyses.find((item) => item.jobId === runId);
        if (historicalRun) {
          const historicalDataset = nextHistory.datasets.find((item) => item.datasetId === historicalRun.datasetId);
          setScope(historicalRun.datasetId ? {
            status: "READY",
            dataset_id: historicalRun.datasetId,
            dataset_name: historicalDataset?.name,
          } : null);
          setJob({ ok: true, job_id: runId, plan: null });
          setState(researchRunState(historicalRun.status));
          void Promise.allSettled([getPlannerJob(runId), getPlannerJobEvents(runId), getPlannerJobArtifacts(runId), getPlannerJobInterpretations(runId)]).then(([detailResult, eventResult, artifactResult, interpretationResult]) => {
            if (!active) return;
            if (detailResult.status === "fulfilled") {
              const detail = detailResult.value;
              setJob((current) => current ? { ...current, plan: detail.analysisPlan || current.plan, plan_id: detail.planId || current.plan_id, plan_hash: detail.planHash || current.plan_hash } : current);
            }
            if (eventResult.status === "fulfilled") setEvents(mergeJobEvents([], eventResult.value));
            if (artifactResult.status === "fulfilled") setArtifacts(mergeArtifacts([], artifactResult.value));
            const historyInterpretations = interpretationResult.status === "fulfilled" ? interpretationResult.value : null;
            const existingInterpretation = historyInterpretations?.interpretations?.[0] || null;
            setInterpretation(existingInterpretation);
            setInterpretationStatus(existingInterpretation ? (existingInterpretation.completeness === "COMPLETE" ? "ready" : "limited") : "idle");
            if (existingInterpretation) void getPlannerInterpretationEvidence(existingInterpretation.interpretationId).then(setEvidence).catch(() => setEvidence(null));
            const owner = runSession || selected;
            if (existingInterpretation && owner && !researchSessionReferencesRun(owner, runId, "post_run")) {
              void createResearchAssistantProjection(owner.id, {
                phase: "post_run",
                datasetId: historicalRun.datasetId,
                runId,
              }).then((message) => { if (active) appendSessionMessage(message); }).catch(() => undefined);
            }
            const historicalState = researchRunState(historicalRun.status);
            const planHash = detailResult.status === "fulfilled" ? detailResult.value.planHash : null;
            if (!existingInterpretation && owner && (historicalState === "complete" || historicalState === "partial") && planHash) {
              setInterpretationStatus("loading");
              void createScientificInterpretation(runId, planHash).then((result) => {
                if (!active) return;
                const recovered = result.interpretation || null;
                setInterpretation(recovered);
                setInterpretationStatus(recovered ? (recovered.completeness === "COMPLETE" ? "ready" : "limited") : "error");
                if (recovered) {
                  void getPlannerInterpretationEvidence(recovered.interpretationId).then((value) => { if (active) setEvidence(value); }).catch(() => undefined);
                  void createResearchAssistantProjection(owner.id, {
                    phase: "post_run",
                    datasetId: historicalRun.datasetId,
                    runId,
                  }).then((message) => { if (active) appendSessionMessage(message); }).catch(() => undefined);
                }
              }).catch(() => { if (active) setInterpretationStatus("error"); });
            }
            if (historicalState === "failed" && owner && !researchSessionReferencesRun(owner, runId, "failed")) {
              void createResearchAssistantProjection(owner.id, {
                phase: "failed",
                datasetId: historicalRun.datasetId,
                runId,
                failureCode: "JOB_FAILED",
              }).then((message) => { if (active) appendSessionMessage(message); }).catch(() => undefined);
            }
            const failures = [detailResult, eventResult, artifactResult, interpretationResult].filter((item) => item.status === "rejected").length;
            if (failures === 4) setError("历史分析结果暂时无法读取，请稍后重试。");
            else if (failures > 0) setError("部分运行记录暂时无法读取；已保留当前可用结果。");
          });
        }
      }
    }).catch((reason) => {
      if (!active) return;
      setPageLoadError(reason instanceof Error ? reason.message : "研究内容加载失败");
      setPageLoadState("error");
    });
    return () => { active = false; };
  }, [projectId, sessionId, runId, reloadKey]);

  useEffect(() => {
    if (!sessionHistoryOpen) return;
    sessionHistorySearchRef.current?.focus();
    const closeOnPointerDown = (event: PointerEvent) => {
      const target = event.target as Node | null;
      if (!target || sessionHistoryRef.current?.contains(target) || sessionHistoryTriggerRef.current?.contains(target)) return;
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
    if (restoreFocus) sessionHistoryTriggerRef.current?.focus();
  }

  useEffect(() => {
    let active = true;
    setProviderLoadState("loading");
    void Promise.all([getPlannerProviderStatus(), listPlannerProviders()]).then(([nextStatus, nextProviders]) => {
      if (!active) return;
      setProviderStatus(nextStatus);
      const available = nextProviders.providers.filter((item) => !item.developerOnly && (item.secretConfigured || item.execution === "live"));
      setProviderOptions(available);
      const first = available.find((item) => item.provider === nextStatus.provider) || available[0];
      setSelectedProvider(first?.provider || "");
      setSelectedModel(nextStatus.model || first?.defaultModel || first?.models?.[0] || "");
      setProviderLoadState("ready");
    }).catch(() => {
      if (!active) return;
      setProviderStatus(null);
      setProviderOptions([]);
      setProviderLoadState("error");
    });
    return () => { active = false; };
  }, [providerReloadKey]);

  const selectedProviderOption = providerOptions.find((item) => item.provider === selectedProvider);
  const selectedModels = selectedProviderOption?.models?.length ? selectedProviderOption.models : selectedProviderOption?.allowedModels || providerStatus?.allowedModels || [];
  const branchChoices = useMemo(() => researchBranchChoices(agent2Turns, agent2TurnId), [agent2TurnId, agent2Turns]);

  async function ensureSession() {
    if (session) return session;
    const created = await createResearchSession(projectId, question.slice(0, 48) || "新研究");
    setSession(created);
    setSessions((items) => [created, ...items]);
    return created;
  }

  async function submitQuestion() {
    if (!question.trim()) return;
    setEvents([]);
    setArtifacts([]);
    setInterpretation(null);
    setEvidence(null);
    setInterpretationStatus("idle");
    setError("");
    setState("planning");
    let activeSession: ResearchSession | null = null;
    try {
      activeSession = await ensureSession();
      if (editTurnId && editingResult) {
        const refs = editingResult.source_object_refs || [];
        const created = await createAgent2ResearchTurn(projectId, activeSession.id, {
          message: question.trim(),
          reply_to_turn_id: editTurnId,
          ui_context: {
            active_object_refs: refs,
            selection_refs: refs,
            scientific_selections: editingResult.scientific_selections || [],
            explicit_object_refs: refs,
            explicit_result_ids: [],
            explicit_finding_refs: [],
          },
        });
        router.push(`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(activeSession.id)}?turn=${encodeURIComponent(created.turn_id)}`);
        return;
      }
      if (exactViewerContext) {
        const objectRef = exactViewerContext.selection ? selectionToResearchObjectRef(exactViewerContext.selection) : {
          object_id: exactViewerContext.sourceRef.objectId, version_id: exactViewerContext.sourceRef.versionId,
          project_id: exactViewerContext.sourceRef.projectId, object_type: exactViewerContext.sourceRef.objectType,
          display_name: exactViewerContext.sourceRef.displayName,
        };
        const scientificSelections = exactViewerContext.selection ? [{
          contract_version: "1.0" as const, object_ref: objectRef, viewer_id: exactViewerContext.selection.viewerId,
          selection_type: exactViewerContext.selection.selectionType, semantic_locator: apiSemanticLocator(exactViewerContext.selection),
          display_label: exactViewerContext.selection.displayLabel,
          evidence_locator: exactViewerContext.selection.evidenceLocator ? { field_locator: exactViewerContext.selection.evidenceLocator } : null,
        }] : [];
        const created = await createAgent2ResearchTurn(projectId, activeSession.id, {
          message: question.trim(),
          // A deep-linked Viewer context is already an explicit, exact object/version
          // selection. Preserve it in the resolver's explicit channel as well as the
          // bounded active/selection channels so ambiguous project history cannot
          // downgrade a targeted research request to clarification.
          ui_context: { active_object_refs: [objectRef], selection_refs: exactViewerContext.selection ? [objectRef] : [], scientific_selections: scientificSelections, explicit_object_refs: [objectRef], explicit_result_ids: [], explicit_finding_refs: [] },
        });
        setQuestion(""); setState("planning"); setMobilePanel("workbench");
        router.push(`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(activeSession.id)}?turn=${encodeURIComponent(created.turn_id)}`);
        return;
      }
      const savedMessage = await createResearchMessage(activeSession.id, question.trim());
      setSession((current) => current ? { ...current, messages: [...(current.messages || []), savedMessage] } : current);
      const nextScope = await resolveResearchScope(projectId, question.trim());
      setScope(nextScope);
      if (nextScope.status === "UNSUPPORTED") {
        const reply = await createResearchAssistantProjection(activeSession.id, { phase: "unsupported", datasetName: nextScope.dataset_name });
        appendSessionMessage(reply); setState("unsupported"); return;
      }
      if (nextScope.status === "NEEDS_CLARIFICATION") {
        const reply = await createResearchAssistantProjection(activeSession.id, { phase: "clarification", candidates: nextScope.candidates?.map((item) => item.name) || [] });
        appendSessionMessage(reply); setState("clarification"); return;
      }
      if (!nextScope.dataset_id) throw new Error("没有找到可用于分析的数据");
      const nextJob = await createPlannerJob({ userPrompt: question.trim(), projectId, datasetId: nextScope.dataset_id, profileId: nextScope.profile_id, enqueue: true, provider: selectedProvider || undefined, model: selectedModel || undefined, thinkingMode, intentSchemaVersion: "1.0", researchSessionId: activeSession.id });
      setJob(nextJob);
      if (!nextJob.ok || !nextJob.job_id) {
        setState(nextJob.capability_outcome === "NEEDS_CLARIFICATION" ? "capability-clarification" : "failed");
        setError(plannerFailureMessage(nextJob));
        const failure = await createResearchAssistantProjection(activeSession.id, {
          phase: "failed",
          datasetName: nextScope.dataset_name,
          datasetId: nextScope.dataset_id,
          failureCode: plannerFailureCode(nextJob),
        });
        appendSessionMessage(failure);
        return;
      }
      const preRun = await createResearchAssistantProjection(activeSession.id, {
        phase: "pre_run",
        datasetName: nextScope.dataset_name,
        datasetId: nextScope.dataset_id,
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
      setError(reason instanceof Error ? reason.message : "研究请求失败");
      if (activeSession) {
        void createResearchAssistantProjection(activeSession.id, {
          phase: "failed",
          failureCode: "RESEARCH_SERVICE_UNAVAILABLE",
        }).then(appendSessionMessage).catch(() => undefined);
      }
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
      const candidate = scope.candidates?.find((item) => item.dataset_id === datasetId);
      const activeSession = await ensureSession();
      const savedSelection = await createResearchMessage(
        activeSession.id,
        `使用 ${candidate?.name || "所选数据"} 继续分析。`,
        datasetId,
      );
      setSession((current) => current ? { ...current, datasetId, dataset_id: datasetId, messages: [...(current.messages || []), savedSelection] } : current);
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
        setState(nextJob.capability_outcome === "NEEDS_CLARIFICATION" ? "capability-clarification" : "failed");
        setError(plannerFailureMessage(nextJob));
        const failure = await createResearchAssistantProjection(activeSession.id, {
          phase: "failed",
          datasetName: candidate?.name,
          datasetId,
          failureCode: plannerFailureCode(nextJob),
        });
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
      setError(reason instanceof Error ? reason.message : "研究请求失败");
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

  function handleMobileTabKey(event: ReactKeyboardEvent<HTMLButtonElement>, current: "timeline" | "workbench") {
    let next: "timeline" | "workbench" | null = null;
    if (event.key === "ArrowLeft" || event.key === "ArrowUp" || event.key === "Home") next = "timeline";
    if (event.key === "ArrowRight" || event.key === "ArrowDown" || event.key === "End") next = "workbench";
    if (!next) return;
    event.preventDefault();
    if (next !== current) setMobilePanel(next);
    (next === "timeline" ? mobileTimelineTabRef : mobileWorkbenchTabRef).current?.focus();
  }

  function appendSessionMessage(message: ResearchMessage) {
    setSession((current) => current && current.id === message.session_id && !(current.messages || []).some((item) => item.id === message.id)
      ? { ...current, messages: [...(current.messages || []), message] }
      : current);
  }

  useEffect(() => {
    const jobId = job?.job_id;
    if (!jobId || state !== "running") return;
    let active = true;
    let lastSeq = 0;
    const poll = async () => {
      try {
        const [detail, nextEvents, nextArtifacts] = await Promise.all([getPlannerJob(jobId), getPlannerJobEvents(jobId, lastSeq), getPlannerJobArtifacts(jobId)]);
        if (!active) return;
        if (nextEvents.length) {
          lastSeq = Math.max(lastSeq, ...nextEvents.map((item) => item.seq || 0));
          setEvents((items) => mergeJobEvents(items, nextEvents));
        }
        setArtifacts((items) => mergeArtifacts(items, nextArtifacts));
        const status = String(detail.status || "").toLowerCase();
        if (["completed", "partial_success", "failed"].includes(status)) {
          setState(status === "completed" ? "complete" : status === "partial_success" ? "partial" : "failed");
          if (status === "failed" && session?.id && failedRunMessageRef.current !== jobId) {
            failedRunMessageRef.current = jobId;
            void createResearchAssistantProjection(session.id, {
              phase: "failed",
              datasetName: scope?.dataset_name,
              datasetId: scope?.dataset_id,
              runId: jobId,
              failureCode: "JOB_FAILED",
            }).then(appendSessionMessage).catch(() => { failedRunMessageRef.current = null; });
          }
          if ((status === "completed" || status === "partial_success") && job.plan_hash) {
            setInterpretationStatus("loading");
            void createScientificInterpretation(jobId, job.plan_hash).then((result) => {
              const nextInterpretation = result.interpretation || null;
              setInterpretation(nextInterpretation);
              if (nextInterpretation) void getPlannerInterpretationEvidence(nextInterpretation.interpretationId).then(setEvidence).catch(() => setEvidence(null));
              setInterpretationStatus(nextInterpretation ? (nextInterpretation.completeness === "COMPLETE" ? "ready" : "limited") : "error");
              if (session?.id && postRunMessageRef.current !== jobId) {
                postRunMessageRef.current = jobId;
                void createResearchAssistantProjection(session.id, {
                  phase: "post_run",
                  datasetName: scope?.dataset_name,
                  datasetId: scope?.dataset_id,
                  runId: jobId,
                }).then(appendSessionMessage).catch(() => { postRunMessageRef.current = null; });
              }
            }).catch(() => setInterpretationStatus("error"));
          }
          return;
        }
        window.setTimeout(poll, 1400);
      } catch (reason) {
        if (active) {
          setError(reason instanceof Error ? reason.message : "无法更新分析进度");
          window.setTimeout(poll, 2500);
        }
      }
    };
    void poll();
    return () => { active = false; };
  }, [job, scope?.dataset_id, scope?.dataset_name, session?.id, state]);

  const messages = session?.messages || [];
  const historicalRuns = (history?.analyses || []).filter((item) => item.jobId !== job?.job_id);
  const canResearch = canWriteProject(history?.project?.role);
  const starterPrompts = researchStarterPrompts(history);
  const showResearchStarter = sessionLoadState === "ready" && state === "idle" && !runId && !job && messages.length === 0;
  const normalizedSessionQuery = sessionHistoryQuery.trim().toLocaleLowerCase("zh-CN");
  const filteredSessions = normalizedSessionQuery
    ? sessions.filter((item) => item.title.toLocaleLowerCase("zh-CN").includes(normalizedSessionQuery))
    : sessions;
  if (pageLoadState === "loading") return <RequireProductAuth><ProductShell projectId={projectId}><main className="research-route-state" aria-busy="true"><div className="product-loading" role="status" aria-live="polite">正在加载研究时间线与项目数据…</div></main></ProductShell></RequireProductAuth>;
  if (pageLoadState === "error") return <RequireProductAuth><ProductShell projectId={projectId}><main className="research-route-state"><div className="product-state" role="alert"><h1>研究内容暂时无法加载</h1><p>项目数据和研究记录没有丢失。请检查服务连接后重试。</p><button type="button" className="product-primary-action" onClick={() => setReloadKey((value) => value + 1)}>重新加载</button>{pageLoadError ? <details><summary>技术详情</summary><p>{pageLoadError}</p></details> : null}</div></main></ProductShell></RequireProductAuth>;
  return <RequireProductAuth><ProductShell projectId={projectId}><a className="skip-link" href="#research-primary-content">跳到研究工作台</a><section ref={workbenchRef} id="research-primary-content" tabIndex={-1} className="research-workbench" aria-label="项目研究工作台" style={{ "--research-conversation-width": conversationWidth + "px" } as CSSProperties}>
    <nav className="research-mobile-tabs" role="tablist" aria-label="研究页面视图"><button ref={mobileTimelineTabRef} id="research-timeline-tab" type="button" role="tab" aria-controls="research-timeline-panel" aria-selected={mobilePanel === "timeline"} tabIndex={mobilePanel === "timeline" ? 0 : -1} onKeyDown={(event) => handleMobileTabKey(event, "timeline")} onClick={() => setMobilePanel("timeline")}>对话</button><button ref={mobileWorkbenchTabRef} id="research-workbench-tab" type="button" role="tab" aria-controls="research-workbench-panel" aria-selected={mobilePanel === "workbench"} tabIndex={mobilePanel === "workbench" ? 0 : -1} onKeyDown={(event) => handleMobileTabKey(event, "workbench")} onClick={() => setMobilePanel("workbench")}>工作台</button></nav>
    <aside id="research-timeline-panel" role="tabpanel" aria-labelledby="research-timeline-tab" className={`conversation-pane ${mobilePanel === "timeline" ? "mobile-panel-active" : "mobile-panel-inactive"}`}><header><div><p className="product-kicker">项目研究</p><h1>研究时间线</h1></div><button ref={sessionHistoryTriggerRef} type="button" className="product-secondary-action" aria-expanded={sessionHistoryOpen} aria-controls="research-session-history" onClick={() => { if (sessionHistoryOpen) closeSessionHistory(); else setSessionHistoryOpen(true); }}>研究记录</button>{sessionHistoryOpen && <div ref={sessionHistoryRef} id="research-session-history" className="research-session-history" role="dialog" aria-modal="false" aria-labelledby="research-session-history-title"><div className="research-session-history-heading"><div><h2 id="research-session-history-title">研究记录</h2><span>{sessions.length} 项</span></div>{canResearch ? <Link href={`/projects/${projectId}/research`} onClick={() => closeSessionHistory(false)}>新建研究</Link> : null}</div><label className="research-session-search"><span className="sr-only">搜索研究记录</span><input ref={sessionHistorySearchRef} type="search" value={sessionHistoryQuery} onChange={(event) => setSessionHistoryQuery(event.target.value)} placeholder="搜索研究标题" autoComplete="off" /></label><div className="research-session-list" aria-live="polite">{filteredSessions.map((item) => <Link key={item.id} className={item.id === session?.id ? "active" : ""} aria-current={item.id === session?.id ? "page" : undefined} href={researchSessionHref(projectId, item.id, history)} onClick={() => closeSessionHistory(false)}><strong>{item.title}</strong><span>{researchSessionStatusLabel(item.status)}</span></Link>)}{!sessions.length ? <p className="research-session-empty">还没有研究记录。新建研究后会保存在这里。</p> : !filteredSessions.length ? <p className="research-session-empty">没有匹配“{sessionHistoryQuery.trim()}”的研究记录。</p> : null}</div></div>}</header>
      <div className="conversation-history">{sessionMemory && (sessionMemory.pinned_object_refs.length || sessionMemory.pinned_result_refs.length || sessionMemory.session_constraints.length || sessionMemory.active_research_goal) ? <section className="research-memory-strip" aria-label="当前研究会话上下文"><strong>本会话上下文</strong><div>{sessionMemory.active_research_goal ? <span>目标：{sessionMemory.active_research_goal}</span> : null}{sessionMemory.session_constraints.map((item) => <span key={item.id}>约束：{item.statement}</span>)}{sessionMemory.pinned_object_refs.length ? <span>固定对象 {sessionMemory.pinned_object_refs.length}</span> : null}{sessionMemory.pinned_result_refs.length ? <span>固定结果 {sessionMemory.pinned_result_refs.length}</span> : null}</div></section> : null}{agent2ContextManifest ? <details className="research-memory-strip research-context-manifest" open={false}><summary>本次研究使用的上下文</summary><div className="research-context-manifest-summary"><span>{agent2ContextManifest.included_items.length} 项已纳入</span><span>{agent2ContextManifest.compaction_state === "COMPACTED" ? "已压缩" : "未压缩"}</span><span>预算 {agent2ContextManifest.input_budget} tokens</span></div><ul>{agent2ContextManifest.included_items.slice(0, 8).map((item) => <li key={item.item_id}><strong>{item.kind === "SCIENTIFIC_OBJECT" || item.kind === "SCIENTIFIC_SELECTION" ? "科学数据" : item.kind === "SCIENTIFIC_RESULT" ? "既有结果" : item.kind === "USER_CONSTRAINT" ? "用户约束" : "研究目标"}</strong><span>{item.inclusion_reason}</span>{item.exact_object_version_id ? <code>{item.exact_object_version_id}</code> : item.result_ref ? <code>{item.result_ref}</code> : null}</li>)}</ul></details> : null}{showResearchStarter && history ? <ResearchStarter projectId={projectId} datasetCount={history.datasets.length} canResearch={canResearch} prompts={starterPrompts} onTryQuestion={trySuggestedQuestion} /> : null}{sessionLoadState === "loading" ? <p className="conversation-load-state" role="status">正在恢复研究对话…</p> : null}{sessionLoadState === "error" ? <div className="conversation-load-state error" role="alert"><strong>研究对话暂时无法读取</strong><p>已有分析结果没有丢失，请重新加载对话</p><button type="button" className="product-secondary-action" onClick={() => setReloadKey((value) => value + 1)}>重新加载对话</button></div> : null}{runId && !session && sessionLoadState === "ready" ? <div className="conversation-load-state" role="note"><strong>这次历史分析没有关联到可恢复的研究对话</strong><p>右侧结果仍可查看；系统不会把它归入其他会话。</p></div> : null}<div className="conversation-stream" role="log" aria-label="研究对话" aria-live="polite">{messages.map((message) => <article key={message.id} className={"conversation-message " + message.role} aria-label={message.role === "user" ? "你的消息" : "研究助手消息"}><span>{message.role === "user" ? "你" : "研究助手"}</span><p>{displayResearchMessage(message)}</p></article>)}{agent2Progress ? <ResearchExecutionActivity progress={agent2Progress} onCancel={() => void cancelAgent2Turn()} cancelPending={agent2CancelPending} onRetry={() => void retryAgent2Turn()} retryPending={agent2RetryPending} /> : null}{agent2TurnId && agent2Progress && ["COMPLETED", "PARTIAL"].includes(agent2Progress.status) ? <ScientificReportAction projectId={projectId} turnId={agent2TurnId} canGenerate={canResearch} /> : null}{state !== "idle" && <InlineRunProcess state={state} scope={scope} job={job} events={events} artifacts={artifacts} error={error} />}</div>{historicalRuns.length ? <section className="timeline-past-runs" aria-label="已完成研究">{historicalRuns.slice(0, 6).map((run) => <Link key={run.jobId} href={researchRunHref(projectId, run.jobId, sessions, run.researchSessionId, run.researchTurnId)} className="timeline-past-run"><span>{run.archived ? "已归档" : run.status === "completed" ? "✓ 分析完成" : run.status === "partial_success" ? "部分完成" : "查看运行"}</span><strong>{researchRunTitle(run)}</strong><small>{run.stepCount} 个步骤 · 查看结果</small></Link>)}</section> : null}</div>
      {history && canResearch && sessionLoadState !== "error" && history.datasets.length ? <form className="research-composer" onSubmit={(event) => { event.preventDefault(); void submitQuestion(); }}>{editTurnId ? <div className="research-edit-notice" role="status"><strong>正在编辑上一条问题</strong><span>{editingLoadState === "loading" ? "正在读取原问题…" : editingLoadState === "error" ? "原问题暂时无法读取；你仍可输入新问题。" : "提交后会创建新的研究分支，历史结果不会被修改。"}</span></div> : null}<label htmlFor="research-question">{editTurnId ? "编辑问题" : "询问此项目中的数据"}</label><textarea ref={questionInputRef} id="research-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="描述要比较、检查或解释的材料科学问题" rows={3} /><div className="research-composer-footer"><span>项目数据</span><details className="research-model-menu"><summary>{providerLoadState === "loading" ? "正在读取模型" : selectedModel || selectedProviderOption?.label || "模型"} · {thinkingMode === "deep" ? "深入" : thinkingMode === "quick" ? "快速" : "标准"}</summary><div className="research-model-controls"><label>模型<select aria-label="本次分析模型" value={selectedModel} onChange={(event) => setSelectedModel(event.target.value)} disabled={!selectedModels.length}>{selectedModels.length ? selectedModels.map((item) => <option key={item} value={item}>{item}</option>) : <option value="">由 Provider 决定</option>}</select></label><label>思考深度<select aria-label="思考深度" value={thinkingMode} onChange={(event) => setThinkingMode(event.target.value as "quick" | "standard" | "deep")}><option value="quick">快速</option><option value="standard">标准</option><option value="deep">深入</option></select></label></div></details><button className="product-primary-action" disabled={!question.trim() || state === "planning" || state === "running"}>{state === "planning" ? "正在准备…" : "开始分析"}</button></div>{providerLoadState === "error" ? <div className="research-provider-notice" role="alert"><span>模型状态暂时无法读取；提交时会由服务端再次验证。</span><button type="button" className="product-link-button" onClick={() => setProviderReloadKey((value) => value + 1)}>重试</button></div> : providerStatus && providerStatus.status !== "ready" && !providerOptions.some((item) => item.secretConfigured) ? <Link className="research-provider-notice" href="/console?settings=models">研究助手尚未配置 · 打开模型设置</Link> : null}</form> : history && canResearch && sessionLoadState !== "error" ? null : history && !canResearch && showResearchStarter ? null : history ? <div className="research-composer research-composer-readonly" role="note"><strong>{sessionLoadState === "error" ? "研究对话暂时不可写" : "此项目为只读"}</strong><p>{sessionLoadState === "error" ? "重新加载对话后可继续研究，避免把内容写入错误会话。" : "你可以查看已有对话、分析过程和科学结果，但不能发起新的研究。"}</p></div> : <div className="research-composer research-composer-readonly" role="status">正在确认项目权限…</div>}
    </aside><button type="button" tabIndex={0} className="research-splitter" role="separator" aria-label="调整研究对话宽度" aria-orientation="vertical" aria-valuemin={320} aria-valuemax={640} aria-valuenow={conversationWidth} aria-valuetext={`${conversationWidth} 像素对话宽度`} onPointerDown={(event) => { event.currentTarget.setPointerCapture(event.pointerId); setConversationWidth(clampConversationWidth(event.clientX - (workbenchRef.current?.getBoundingClientRect().left || 0))); }} onPointerMove={(event) => { if (event.currentTarget.hasPointerCapture(event.pointerId)) setConversationWidth(clampConversationWidth(event.clientX - (workbenchRef.current?.getBoundingClientRect().left || 0))); }} onPointerUp={(event) => { if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId); }} onKeyDown={(event) => { if (event.key === "ArrowLeft") { event.preventDefault(); setConversationWidth((value) => clampConversationWidth(value - 16)); } if (event.key === "ArrowRight") { event.preventDefault(); setConversationWidth((value) => clampConversationWidth(value + 16)); } if (event.key === "Home") { event.preventDefault(); setConversationWidth(clampConversationWidth(320)); } if (event.key === "End") { event.preventDefault(); setConversationWidth(clampConversationWidth(640)); } }} />
    <section id="research-workbench-panel" role="tabpanel" aria-labelledby="research-workbench-tab" className={`research-workbench-pane ${mobilePanel === "workbench" ? "mobile-panel-active" : "mobile-panel-inactive"}`}>
      {branchChoices.length > 1 && session?.id ? (
        <nav className="research-branch-switcher" aria-label="研究分支">
          <span>研究分支</span>
          {branchChoices.map((turn, index) => {
            const turnId = turn.id || turn.turn_id;
            const active = turnId === agent2TurnId;
            return (
              <Link
                key={turnId}
                className={active ? "active" : undefined}
                aria-current={active ? "page" : undefined}
                href={`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(session.id)}?turn=${encodeURIComponent(turnId)}`}
              >
                第 {index + 1} 个分支
              </Link>
            );
          })}
        </nav>
      ) : null}
      {agent2TurnId && agent2Progress && ["COMPLETED", "PARTIAL"].includes(agent2Progress.status) ? <Agent2ScientificPresentation turnId={agent2TurnId} projectId={projectId} sessionId={session?.id} /> : null}
      <ResearchWorkbenchContent projectId={projectId} state={state} scope={scope} job={job} events={events} artifacts={artifacts} interpretation={interpretation} interpretationStatus={interpretationStatus} evidence={evidence} error={error} history={history} onConfirmScope={confirmScope} onTryQuestion={trySuggestedQuestion} />
    </section>
  </section></ProductShell></RequireProductAuth>;
}

export function mergeJobEvents(current: JobEvent[], incoming: JobEvent[]): JobEvent[] {
  const byIdentity = new Map<string, JobEvent>();
  for (const event of [...current, ...incoming]) {
    const identity = String(event.id || `${event.seq || 0}:${event.eventType || "event"}`);
    byIdentity.set(identity, event);
  }
  return [...byIdentity.values()].sort((left, right) => (left.seq || 0) - (right.seq || 0));
}

export function mergeArtifacts(current: Artifact[], incoming: Artifact[]): Artifact[] {
  const byIdentity = new Map<string, Artifact>();
  for (const artifact of [...current, ...incoming]) {
    const identity = artifactReference(artifact) || `${artifact.type || "artifact"}:${JSON.stringify(artifact)}`;
    byIdentity.set(identity, artifact);
  }
  return [...byIdentity.values()].sort((left, right) => artifactReference(left).localeCompare(artifactReference(right)));
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

function ResearchStarter({ projectId, datasetCount, canResearch, prompts, onTryQuestion }: { projectId: string; datasetCount: number; canResearch: boolean; prompts: ResearchStarterPrompt[]; onTryQuestion: (question: string) => void }) {
  if (!datasetCount) {
    return <section className="research-starter" aria-labelledby="research-starter-title"><p className="product-kicker">研究起点</p><h2 id="research-starter-title">{canResearch ? "先为项目添加数据" : "这个项目还没有可研究的数据"}</h2><p>{canResearch ? "上传支持的材料数据后，系统会识别可用的科学对象与分析方向。" : "具备编辑权限的成员上传数据后，可在这里继续研究。"}</p>{canResearch ? <Link className="product-primary-action research-starter-upload" href={`/projects/${projectId}/datasets/new`}>上传数据</Link> : <p className="research-starter-readonly" role="note">此项目为只读</p>}</section>;
  }
  return <section className="research-starter" aria-labelledby="research-starter-title"><p className="product-kicker">研究起点</p><h2 id="research-starter-title">从 {datasetCount} 个项目数据集开始</h2><p>{canResearch ? "选择一个与当前数据匹配的方向；问题只会填入下方输入框，由你确认后开始分析。" : "你可以查看项目数据与已有结果，但当前权限不能发起新的研究。"}</p>{canResearch ? <div className="research-starter-directions"><strong>当前可研究方向</strong><div className="research-starter-questions">{prompts.map((prompt) => <button key={prompt.id} type="button" onClick={() => onTryQuestion(prompt.question)}><span>{prompt.question}</span><small>填入问题框</small></button>)}</div></div> : <p className="research-starter-readonly" role="note">此项目为只读</p>}</section>;
}

function ResearchWorkbenchContent({ projectId, state, scope, job, events, artifacts, interpretation, interpretationStatus, evidence, error, history, onConfirmScope, onTryQuestion }: { projectId: string; state: ResearchState; scope: ScopeResolution | null; job: PlannerJobCreateResult | null; events: JobEvent[]; artifacts: Artifact[]; interpretation: GroundedScientificInterpretation | null; interpretationStatus: "idle" | "loading" | "ready" | "limited" | "error"; evidence: InterpretationEvidenceResponse | null; error: string; history: ProjectHistory | null; onConfirmScope: (datasetId: string) => Promise<void>; onTryQuestion: (question: string) => void }) {
  const resultArtifacts = projectScientificArtifacts(artifacts);
  const [highlightedArtifactId, setHighlightedArtifactId] = useState<string | null>(null);
  if (state === "unsupported") return <div className="research-state unsupported"><p className="product-kicker">无法进行此分析</p><h2>当前数据缺少完成这项分析所需的科学属性。</h2><p>当前可用：{scope?.available_semantics?.join("、") || "已识别的材料属性"}</p><div className="product-row-actions"><button type="button" className="product-secondary-action" onClick={() => onTryQuestion("查看 band gap 分布")}>查看带隙分布</button><button type="button" className="product-secondary-action" onClick={() => onTryQuestion("比较 formation energy 与 density 的关系")}>比较形成能与密度</button></div><details><summary>技术详情</summary><p>未创建分析方案或作业。</p></details></div>;
  if (state === "clarification") return <ClarificationState scope={scope} onConfirm={onConfirmScope} />;
  if (state === "capability-clarification") return <div className="research-state"><p className="product-kicker">需要确认</p><h2>局部环境分析需要选择配位算法。</h2><p>径向分布可以直接计算；局部环境与配位多面体会依赖所选邻居算法。请选择本次分析使用的方法。</p><div className="research-suggestion-list"><button type="button" className="product-secondary-action" onClick={() => onTryQuestion("使用 CrystalNN 计算当前结构的径向分布并分析局部环境")}>使用 CrystalNN</button><button type="button" className="product-secondary-action" onClick={() => onTryQuestion("使用 VoronoiNN 计算当前结构的径向分布并分析局部环境")}>使用 VoronoiNN</button></div><p className="product-form-hint">当前尚未创建分析运行；选择后可在左侧检查问题并提交。</p></div>;
  if (state === "idle") return <div className="research-state idle"><p className="product-kicker">当前研究上下文</p><h2>项目数据与最近研究</h2><p>这里保留可用于分析的数据范围，以及已经完成的研究结果。</p><section className="research-idle-section"><header><strong>项目数据</strong><span>{history?.datasets.length || 0} 个数据集</span></header>{history?.datasets.slice(0, 4).map((dataset) => <Link key={dataset.datasetId} href={`/projects/${projectId}/data?dataset=${dataset.datasetId}`} className="research-context-row"><strong>{dataset.name}</strong><span>{dataset.profile?.rowCount ?? dataset.profile?.objectCount ?? "—"} 个记录 · {researchDatasetTypeLabel(dataset.profile?.datasetType)}</span></Link>)}{!history?.datasets.length && <p className="research-context-empty">上传数据后，可在这里查看当前研究范围。</p>}</section><section className="research-idle-section"><header><strong>最近研究</strong><Link href={`/projects/${projectId}/reports`}>查看报告</Link></header>{history?.analyses.slice(0, 3).map((run) => <Link key={run.jobId} href={researchRunHref(projectId, run.jobId, [], run.researchSessionId, run.researchTurnId)} className="research-context-row"><strong>{researchRunTitle(run)}</strong><span>{researchSessionStatusLabel(run.status)}</span></Link>)}{!history?.analyses.length && <p className="research-context-empty">完成第一次研究后，结果会保留在这里。</p>}</section></div>;
  const groundedNarrative = groundedEvidenceNarrative(evidence);
  const primaryArtifact = resultArtifacts.find((artifact) => artifactReference(artifact) === highlightedArtifactId)
    || resultArtifacts.find((artifact) => artifact.resultRole === "PRIMARY_FIGURE" || artifact.resultRole === "PRIMARY_TABLE")
    || resultArtifacts[0];
  const supportingArtifacts = resultArtifacts.filter((artifact) => artifact !== primaryArtifact);
  const datasetId = scope?.dataset_id || job?.plan?.datasetId || undefined;
  const jobId = job?.job_id || undefined;
  const technical = researchTechnicalSummary(job, artifacts, resultArtifacts);
  const presentationSources = (job?.intent?.dataScope.resourceRefs || [])
    .filter((item) => Boolean(item.versionId))
    .map((item) => ({
      objectId: item.objectId,
      versionId: item.versionId as string,
      objectType: item.objectType,
      displayName: item.displayName || scope?.dataset_name,
    }));
  const presentation = compileScientificPresentation({
    interpretation,
    evidence: evidence?.evidenceItems,
    artifacts,
    sourceObjectRefs: presentationSources,
  });
  return <div className={"research-result-state " + state}><header className="workbench-heading"><div><p className="product-kicker">{state === "running" ? "正在分析" : state === "complete" ? "科学结果" : state === "partial" ? "部分结果" : "分析未完成"}</p><h2>{scientificResultTitle(job?.plan?.goal || null, artifacts, interpretation)}</h2></div><div className="workbench-heading-actions">{datasetId ? <Link className="product-secondary-action" href={`/projects/${projectId}/data?dataset=${datasetId}`}>查看数据</Link> : null}{(state === "complete" || state === "partial") && jobId ? <Link className="product-secondary-action" href={`/projects/${projectId}/reports/${jobId}`}>打开分析报告</Link> : null}</div></header>
     <section className="live-results"><div className="result-heading"><h3>{state === "running" ? "本次分析" : "主要结果"}</h3><span>{resultArtifacts.length ? `${resultArtifacts.length} 个科学输出` : scope?.dataset_name || ""}</span></div>{primaryArtifact ? <ResearchArtifactFigure artifact={primaryArtifact} highlighted={artifactReference(primaryArtifact) === highlightedArtifactId} projectId={projectId} datasetId={datasetId} jobId={jobId} artifacts={artifacts} /> : <div className="result-empty">{state === "running" ? <>结果生成后会在这里显示。<br />当前使用：{scope?.dataset_name || "已选择的数据"}</> : "当前没有可展示的结果。"}</div>}{supportingArtifacts.length ? <details className="report-supporting-results"><summary>支持性结果 · {supportingArtifacts.length} 项</summary><div className="report-artifact-list">{supportingArtifacts.map((artifact) => <ResearchArtifactFigure key={artifact.artifactId || artifact.id} artifact={artifact} highlighted={artifactReference(artifact) === highlightedArtifactId} projectId={projectId} datasetId={datasetId} jobId={jobId} artifacts={artifacts} />)}</div></details> : null}{(state === "complete" || state === "partial") && <section className="finding-block"><h3>主要发现</h3>{interpretationStatus === "loading" ? <p role="status">正在整理科学结论…</p> : userFacingClaims(interpretation).length ? <ul className="research-findings">{userFacingClaims(interpretation).slice(0, 8).map((claim) => <li key={claim.claimId}><strong>{claim.claimType === "LIMITATION" ? "限制" : "观察"}</strong><p>{claim.renderedText}</p></li>)}</ul> : groundedNarrative.finding ? <p>{groundedNarrative.finding}</p> : <p>本次分析已生成可复核的图表与数据表；当前解释没有足够的用户级科学结论。</p>}<h3>限制</h3>{userFacingLimitations(interpretation).length ? <ul>{userFacingLimitations(interpretation).map((item) => <li key={item}>{item}</li>)}</ul> : <p>{groundedNarrative.limitation || (interpretationStatus === "error" ? "科学结论暂时无法读取；结果仍可查看。" : "解释仅适用于本次分析所使用的数据与证据。")}</p>}{evidence?.evidenceItems?.length ? <details className="research-evidence"><summary>依据 · {evidence.evidenceItems.length} 项</summary><ul>{evidence.evidenceItems.slice(0, 12).map((item) => { const target = resultArtifacts.find((artifact) => artifactReference(artifact) === item.sourceArtifactId); return <li key={item.evidenceItemId}><strong>{evidenceLabel(item.semanticRole)}</strong><span>{displayEvidenceValue(item.displayValue)}</span><small>已绑定本次分析的来源数据字段</small>{target ? <button type="button" className="product-link-button" onClick={() => { setHighlightedArtifactId(artifactReference(target)); window.requestAnimationFrame(() => document.getElementById(artifactDomId(target))?.scrollIntoView({ block: "center" })); }}>在结果中查看</button> : null}</li>; })}</ul></details> : null}{evidence?.sourceObjectRefs?.length ? <details className="research-evidence"><summary>精确科学来源 · {evidence.sourceObjectRefs.length} 个版本</summary><ul>{evidence.sourceObjectRefs.map((source) => <li key={`${source.objectId}:${source.versionId}`}><strong>{source.displayName || source.objectType || "ScientificObject"}</strong><span>对象 {source.objectId}</span><small>exact version {source.versionId}</small></li>)}</ul></details> : null}<details><summary>来源与过程</summary><p>{interpretation ? "结论来自本次分析的已验证结果与依据。" : "分析方法、来源数据与输出记录可继续查看。"}</p></details><details className="research-technical-details"><summary>技术详情</summary><dl><div><dt>运行 ID</dt><dd><code>{compactTechnicalId(technical.runId)}</code></dd></div><div><dt>方案 ID</dt><dd><code>{compactTechnicalId(technical.planId)}</code></dd></div><div><dt>输出</dt><dd>{technical.outputCount ? `${technical.outputCount} 个可查看结果` : "暂无可查看结果"}</dd></div><div><dt>结构化数据</dt><dd>{technical.structuredOutputCount ? `${technical.structuredOutputCount} 个 JSON Artifact` : "当前运行没有可展示的结构化结果"}</dd></div></dl>{technical.structuredOutputCount ? <p className="research-technical-hint">可打开上方结果的“技术详情”查看有界 JSON；示例：{technical.structuredOutputLabel}。</p> : <p className="research-technical-hint">运行身份与结果状态仍保存在审计记录中；结构化数据会在结果成功加载后显示。</p>}</details></section>}</section>
    {(state === "complete" || state === "partial") && <ScientificPresentationBlocks presentation={presentation} projectId={projectId} instanceId={jobId || "live-result"} />}
  </div>;
}

function ResearchArtifactFigure({ artifact, highlighted = false, projectId, datasetId, jobId, artifacts }: { artifact: ProjectedScientificArtifact; highlighted?: boolean; projectId: string; datasetId?: string; jobId?: string; artifacts: Artifact[] }) {
  return <article id={artifactDomId(artifact)} className={`artifact-result result-role-${artifact.resultRole.toLowerCase()}${highlighted ? " evidence-target" : ""}`}><header className="artifact-result-heading"><span>{artifact.resultRole === "PRIMARY_FIGURE" ? "主要结果" : artifact.resultRole === "PRIMARY_TABLE" ? "主要数据表" : artifactLabel(artifact.type)}</span><strong>{artifact.resultTitle}</strong></header>{jobId ? <ScientificResultViewer projectId={projectId} datasetId={datasetId} jobId={jobId} selected={artifact} artifacts={artifacts} /> : null}<p>{artifact.resultRole === "PRIMARY_FIGURE" || artifact.resultRole === "PRIMARY_TABLE" ? "图表与单位来自本次分析的已验证结果。" : "支持性科学输出，供结果复核使用。"}</p></article>;
}

function artifactReference(artifact: Artifact) { return artifact.artifactId || artifact.id || ""; }
function artifactDomId(artifact: Artifact) { return `research-artifact-${encodeURIComponent(artifactReference(artifact))}`; }

function InlineRunProcess({ state, scope, job, events, artifacts, error }: { state: ResearchState; scope: ScopeResolution | null; job: PlannerJobCreateResult | null; events: JobEvent[]; artifacts: Artifact[]; error: string }) {
  const steps = job?.plan?.steps || [];
  const complete = state === "complete";
  const completedSteps = new Set(events.filter((event) => event.eventType === "tool.completed").map(eventStepId).filter((value): value is string => value !== null));
  const activeSteps = new Set(events.filter((event) => event.eventType === "tool.started").map(eventStepId).filter((value): value is string => value !== null));
  return <details className="timeline-run-process" open={!complete}>
    <summary>{complete ? `✓ 分析完成 · ${steps.length || events.length} 个步骤` : state === "capability-clarification" ? "需要确认分析方法" : state === "failed" ? "分析未完成 · 查看过程" : state === "partial" ? "部分完成 · 查看过程" : state === "planning" ? "正在准备分析方案" : "分析中 · 查看过程"}</summary>
    <div className="timeline-process-body" role="status">
      {scope?.dataset_name && <p>✓ 已确定分析数据<br /><small>{scope.dataset_name}</small></p>}
      {steps.length > 0 && <p>✓ 分析方案已准备</p>}
      <ol>{steps.map((step, index) => { const stepState = runProcessStepState(step.stepId, state, completedSteps, activeSteps); const projection = userFacingPlanStep(step.purpose, step.reason, index, step.toolId); return <li key={step.stepId || index}><span>{stepState === "complete" ? "✓" : stepState === "active" ? "●" : "○"}</span><div><strong>{projection.purpose}</strong>{projection.reason && <small>{projection.reason}</small>}</div></li>; })}</ol>
      {artifacts.length > 0 && <p>✓ 已生成 {artifacts.length} 个结果 <span>右侧可查看</span></p>}
      {error && <p className="product-form-error" role="alert">{error}</p>}
    </div>
  </details>;
}

function eventStepId(event: JobEvent): string | null {
  const value = event.payload?.stepId;
  return typeof value === "string" && value.length > 0 ? value : null;
}

export function runProcessStepState(stepId: string | undefined, state: ResearchState, completedSteps: ReadonlySet<string>, activeSteps: ReadonlySet<string>): "complete" | "active" | "pending" {
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

export function userFacingPlanStep(purpose: string | null | undefined, reason: string | null | undefined, index = 0, toolId?: string | null): { purpose: string; reason?: string } {
  const rawPurpose = String(purpose || "").trim();
  const rawReason = String(reason || "").trim();
  const machinePlan = /validated structured AnalysisIntent|eligible registered capability|exact (?:Intent|DataProfile|Registry)|parameter-binding facts|inputref|registry\s*(?:hash|version)|plan[_\s-]?id|job[_\s-]?id/i;
  const registryPurpose = toolId ? USER_FACING_TOOL_STEPS[toolId] : undefined;
  const projectedPurpose = registryPurpose || (machinePlan.test(rawPurpose) ? "整理当前数据中的科学信息" : rawPurpose || `科学分析步骤 ${index + 1}`);
  const projectedReason = machinePlan.test(rawReason) ? "已根据当前数据和科学能力确定本次步骤。" : rawReason || undefined;
  return { purpose: projectedPurpose, ...(projectedReason ? { reason: projectedReason } : {}) };
}

function plannerFailureMessage(result: PlannerJobCreateResult) {
  const code = plannerFailureCode(result);
  if (code === "COORDINATION_ALGORITHM_CLARIFICATION_REQUIRED") return "局部环境分析需要先选择 CrystalNN 或 VoronoiNN 配位算法；当前没有创建运行。";
  if (code.includes("CAPABILITY") || code.includes("ELIGIB")) return "当前已验证的分析能力无法完整覆盖这个问题。请尝试缩小问题范围，或从右侧项目数据中选择更匹配的数据。";
  if (code.includes("INTENT_UNSUPPORTED")) return "当前数据无法支持这项分析；没有创建分析方案或运行。";
  if (code.includes("INTENT_CLARIFICATION")) return "需要先确认本次分析使用的数据范围。";
  if (code.includes("DURABLE_ROOT_INPUTS")) return "当前数据尚未准备好用于执行分析。请等待导入完成后重试。";
  if (code.includes("PROVIDER")) return "研究助手暂时无法准备分析方案。请检查模型设置后重试。";
  return "分析方案未能通过当前数据和科学能力的验证；没有创建运行。";
}

function plannerFailureCode(result: PlannerJobCreateResult) {
  const errorCode = String(result.error_code || "").toUpperCase();
  const diagnosticCode = String(result.validation_errors?.[0]?.code || "").toUpperCase();
  return ["NEEDS_CLARIFICATION", "CAPABILITY_MISMATCH", "VALIDATION_FAILED"].includes(errorCode) && diagnosticCode
    ? diagnosticCode
    : errorCode || diagnosticCode || "UNKNOWN";
}

function researchSessionStatusLabel(status?: string | null) {
  const normalized = String(status || "").toLowerCase();
  if (normalized === "active") return "可继续";
  if (["queued", "running", "planning"].includes(normalized)) return "进行中";
  if (["completed", "complete", "succeeded", "success"].includes(normalized)) return "已完成";
  if (normalized === "partial_success" || normalized === "partial") return "部分完成";
  if (normalized === "failed") return "未完成";
  if (normalized === "archived") return "已归档";
  return "研究记录";
}

function researchDatasetTypeLabel(datasetType?: string | null) {
  const normalized = String(datasetType || "").toLowerCase();
  if (!normalized) return "科学数据";
  if (normalized.includes("table") || normalized.includes("csv") || normalized.includes("dataframe")) return "材料数据表";
  if (normalized.includes("structure") || normalized.includes("atoms")) return "原子结构";
  if (normalized.includes("trajectory")) return "原子轨迹";
  if (normalized.includes("xrd")) return "XRD 数据";
  if (normalized.includes("electronic") || normalized.includes("band") || normalized.includes("dos")) return "电子结构数据";
  if (normalized.includes("phonon")) return "声子数据";
  if (normalized.includes("volumetric") || normalized.includes("cube")) return "体数据";
  return "科学数据";
}

function isPrimaryScientificArtifact(artifact: Artifact) {
  return !["recipe_json", "summary_md", "table_csv"].includes(String(artifact.type || "").toLowerCase());
}

function userFacingClaims(interpretation: GroundedScientificInterpretation | null) {
  return interpretation?.claims.filter((claim) => !/(?:reported\s+(?:count|category|value|range)|artifact\s*\(s\)|projector|schema|contract|toolcall|inputref|plan[_\s-]?id|job[_\s-]?id|registry\s*(?:hash|version))/i.test(claim.renderedText) && !/(?:^|:)[a-f0-9]{24,}/i.test(claim.renderedText)) || [];
}

export function displayResearchMessage(message: ResearchMessage): string {
  if (message.role !== "assistant") return message.content;
  let text = message.content;
  // Keep legacy persisted projections readable without rewriting historical
  // Messages. Dataset identifiers remain exact, but the surrounding sentence
  // uses the current Chinese research-workbench vocabulary.
  text = text.replace(/^我会使用\s*(.+?)\s*完成(?:本次)?分析。/u, "本次分析将以数据集“$1”为范围。");
  text = text.replace(/Satisfy the validated structured AnalysisIntent with an eligible registered capability\.?/gi, "执行已验证的科学分析步骤。");
  text = text.replace(/分析已经完成。[\s\S]*?可以在右侧查看科学结果、依据与来源。/gi, "分析已经完成。\n\n可以在右侧查看科学结果、依据与来源。");
  text = text.replace(/(?:dataset\s+reported\s+(?:count|category|value)|artifact\s*\(s\)|projector|schema|contract|toolcall|inputref|plan[_\s-]?id|job[_\s-]?id)[^。\n]*[。]?/gi, "");
  return text.replace(/[ \t]{2,}/g, " ").replace(/\n{3,}/g, "\n\n").trim();
}

function userFacingLimitations(interpretation: GroundedScientificInterpretation | null) {
  return interpretation?.globalLimitations.filter((item) => !/(?:reported\s+(?:count|category|value)|artifact\s*\(s\)|projector|schema|contract|toolcall|inputref|plan[_\s-]?id|job[_\s-]?id|registry\s*(?:hash|version))/i.test(item)) || [];
}

export function groundedEvidenceNarrative(evidence: InterpretationEvidenceResponse | null) {
  const values = new Map((evidence?.evidenceItems || []).map((item) => [item.semanticRole, item.displayValue]));
  const value = (role: string) => values.get(role) || "";
  const number = (role: string) => Number.parseFloat(value(role));
  const hasNumbers = (...roles: string[]) => roles.every((role) => Number.isFinite(number(role)));
  const algorithmLabel = (raw: string) => raw.toLowerCase().includes("crystalnn") ? "CrystalNN" : raw.toLowerCase().includes("voronoinn") ? "VoronoiNN" : raw;
  if (value("local_environment.source_algorithm") && hasNumbers("local_environment.evaluated_sites", "local_environment.classified_sites", "local_environment.ambiguous_sites", "local_environment.unclassified_sites", "local_environment.coverage")) {
    const evaluated = number("local_environment.evaluated_sites");
    const classified = number("local_environment.classified_sites");
    const ambiguous = number("local_environment.ambiguous_sites");
    const unclassified = number("local_environment.unclassified_sites");
    return {
      finding: `${algorithmLabel(value("local_environment.source_algorithm"))} 局部环境分析评估了 ${evaluated} 个位点，其中 ${classified} 个完成分类、${ambiguous} 个存在歧义、${unclassified} 个未分类；覆盖率为 ${formatPercent(number("local_environment.coverage"))}。`,
      limitation: "局部环境分类来自所选配位算法与几何参考匹配，不等同于确定的化学键或价态判定。",
    };
  }
  if (value("coordination.algorithm") && hasNumbers("coordination.total_sites", "coordination.successful_sites", "coordination.coverage")) {
    const ranges = [
      value("coordination.value_range") ? `配位值范围为 ${displayEvidenceValue(value("coordination.value_range"))}` : "",
      value("coordination.distance_range") ? `邻居距离范围为 ${displayEvidenceValue(value("coordination.distance_range"))}` : "",
    ].filter(Boolean);
    const warningCodes = new Set((evidence?.evidenceItems || []).flatMap((item) => item.warnings || []));
    const caveats = [
      warningCodes.has("CRYSTALNN_OXIDATION_STATES_NOT_DECLARED") ? "当前输入未声明氧化态" : "",
      warningCodes.has("CRYSTALNN_RADIUS_FALLBACK_USED") ? "部分判断使用了半径回退规则" : "",
    ].filter(Boolean);
    return {
      finding: `${algorithmLabel(value("coordination.algorithm"))} 在 ${number("coordination.successful_sites")}/${number("coordination.total_sites")} 个位点完成配位分析，覆盖率为 ${formatPercent(number("coordination.coverage"))}${ranges.length ? `；${ranges.join("，")}` : ""}。`,
      limitation: `${caveats.length ? `${caveats.join("；")}。` : ""}配位结果依赖所选算法、参数与当前结构，不作为确定化学键结论。`,
    };
  }
  if (hasNumbers("xrd.experimental_detected_peaks", "xrd.theoretical_peaks", "xrd.matched_pairs", "xrd.matching_tolerance", "xrd.residual.mae", "xrd.residual.maximum_residual")) {
    return {
      finding: `在 ${number("xrd.matching_tolerance")}° 的匹配容差内，${number("xrd.experimental_detected_peaks")} 个实验峰中有 ${number("xrd.matched_pairs")} 个与 ${number("xrd.theoretical_peaks")} 个理论峰对应；已匹配峰位的平均绝对偏差为 ${number("xrd.residual.mae")}°，最大偏差为 ${number("xrd.residual.maximum_residual")}°。`,
      limitation: `仍有 ${number("xrd.unmatched_experimental")} 个实验峰和 ${number("xrd.unmatched_theoretical")} 个理论峰未匹配；该对比不能单独作为物相确认或 Rietveld 精修结论。`,
    };
  }
  if (hasNumbers("dataset.sample_count", "composition.valid_count", "composition.unique_formula_count")) {
    return {
      finding: `当前材料数据包含 ${number("dataset.sample_count")} 个样本，其中 ${number("composition.valid_count")} 个样本具有可解析化学式，共覆盖 ${number("composition.unique_formula_count")} 个唯一化学式。`,
      limitation: `材料性质字段数量为 ${number("dataset.property_count")}；数据质量概览不替代针对具体性质或结构的科学分析。`,
    };
  }
  const correlation = [...values.entries()].find(([role]) => role.startsWith("correlation."));
  if (correlation && Number.isFinite(Number.parseFloat(correlation[1]))) {
    const fields = correlation[0].replace("correlation.", "").split(".").map((item) => item.replaceAll("_", " "));
    return {
      finding: `${fields.join(" 与 ")} 的 Pearson 相关系数为 ${Number.parseFloat(correlation[1])}。`,
      limitation: "相关性描述当前样本中的线性关系，不代表因果关系，也不替代异常值、分组效应和数据质量复核。",
    };
  }
  if (value("structure.formula") && hasNumbers("structure.site_count")) {
    const lattice = [value("structure.lattice.a"), value("structure.lattice.b"), value("structure.lattice.c")].filter(Boolean).map(displayEvidenceValue);
    return {
      finding: `${value("structure.formula")} 结构包含 ${number("structure.site_count")} 个位点${lattice.length === 3 ? `，晶格参数 a、b、c 分别为 ${lattice.join("、")}` : ""}。`,
      limitation: "结构摘要仅陈述当前标准化结构中的几何事实；未提供的信息不会由界面推断。",
    };
  }
  if (value("trajectory.msd.last_total") && value("trajectory.msd.last_lag")) {
    const status = value("trajectory.diffusion.status");
    return {
      finding: `在 ${displayEvidenceValue(value("trajectory.msd.last_lag"))} 的末端时滞处，总 MSD 为 ${displayEvidenceValue(value("trajectory.msd.last_total"))}；RDF 统计使用 ${number("trajectory.rdf.included_frames")} 帧。`,
      limitation: status === "INSUFFICIENT_DURATION" ? "当前轨迹时长不足以形成稳健扩散系数结论；应延长采样并检查线性扩散区间。" : "扩散解释仅适用于当前轨迹、时间窗和采样条件。",
    };
  }
  if (value("electronic.band.sampled_gap") && hasNumbers("electronic.band.band_count", "electronic.band.kpoint_count", "electronic.dos.energy_point_count")) {
    return {
      finding: `当前能带包含 ${number("electronic.band.band_count")} 条带和 ${number("electronic.band.kpoint_count")} 个 k 点，采样带隙为 ${displayEvidenceValue(value("electronic.band.sampled_gap"))}；DOS 使用 ${number("electronic.dos.energy_point_count")} 个能量点。`,
      limitation: "采样带隙与金属/半导体分类受 k 路径、费米能级和计算设置约束，不等同于实验带隙。",
    };
  }
  if (value("phonon.frequency_range") && hasNumbers("phonon.branch_count", "phonon.qpoint_count", "phonon.imaginary_mode_count")) {
    return {
      finding: `声子结果包含 ${number("phonon.branch_count")} 条分支和 ${number("phonon.qpoint_count")} 个 q 点，频率范围为 ${displayEvidenceValue(value("phonon.frequency_range"))}，检测到 ${number("phonon.imaginary_mode_count")} 个虚频模式。`,
      limitation: "动力学稳定性判断仅适用于当前结构、力常数、q 路径和数值容差；近零频模式需要结合收敛性复核。",
    };
  }
  return { finding: "", limitation: "" };
}

function evidenceLabel(role: string) {
  return ({ "xrd.matching_tolerance": "匹配容差", "xrd.theoretical_peaks": "理论峰", "xrd.residual.mae": "平均绝对偏差", "xrd.unmatched_theoretical": "未匹配理论峰", "xrd.unmatched_experimental": "未匹配实验峰", "xrd.residual.rmse": "均方根偏差", "xrd.matched_pairs": "匹配峰", "xrd.experimental_detected_peaks": "实验峰", "xrd.wavelength": "辐射波长", "xrd.residual.maximum_residual": "最大偏差", "dataset.sample_count": "样本数", "dataset.property_count": "性质字段数", "composition.valid_count": "有效化学式", "composition.invalid_count": "无效化学式", "composition.unique_formula_count": "唯一化学式", "structure.formula": "化学式", "structure.site_count": "位点数", "coordination.algorithm": "配位算法", "coordination.coverage": "配位覆盖率", "coordination.total_sites": "总位点数", "coordination.successful_sites": "成功分析位点", "coordination.value_range": "配位值范围", "coordination.distance_range": "邻居距离范围", "local_environment.source_algorithm": "局部环境来源算法", "local_environment.coverage": "局部环境覆盖率", "local_environment.evaluated_sites": "已评估位点", "local_environment.classified_sites": "已分类位点", "local_environment.ambiguous_sites": "歧义位点", "local_environment.unclassified_sites": "未分类位点", "trajectory.msd.last_total": "末端总 MSD", "trajectory.msd.last_lag": "末端时滞", "trajectory.rdf.included_frames": "RDF 帧数", "electronic.band.sampled_gap": "采样带隙", "electronic.band.band_count": "能带数", "electronic.band.kpoint_count": "k 点数", "electronic.dos.energy_point_count": "DOS 能量点", "phonon.frequency_range": "频率范围", "phonon.branch_count": "声子分支", "phonon.qpoint_count": "q 点数", "phonon.imaginary_mode_count": "虚频模式" } as Record<string, string>)[role] || role.replaceAll("_", " ");
}

function displayEvidenceValue(value: string) { return value.replace(/\s+to\s+/gi, " 至 ").replace(/\bdegree\b/gi, "°").replace(/\bangstrom\b/gi, "Å").replace(/\bpicosecond\b/gi, "ps").replace(/\bterahertz\b/gi, "THz"); }

function formatPercent(value: number) {
  const percent = value * 100;
  return `${Number.isInteger(percent) ? percent.toFixed(0) : percent.toFixed(1)}%`;
}

function artifactLabel(type: string | undefined) {
  return ({ table_json: "数据表", plotly_json: "科学图表", structure_json: "晶体结构", trajectory_json: "原子轨迹", xrd_json: "XRD 结果", electronic_band_json: "能带结果", electronic_dos_json: "态密度结果", phonon_band_json: "声子能带", phonon_dos_json: "声子态密度", volumetric_payload_json: "体数据" } as Record<string, string>)[String(type || "").toLowerCase()] || "科学结果";
}

function ClarificationState({ scope, onConfirm }: { scope: ScopeResolution | null; onConfirm: (datasetId: string) => Promise<void> }) {
  const candidates = scope?.candidates || [];
  const [selected, setSelected] = useState(candidates[0]?.dataset_id || "");
  return <div className="research-state"><p className="product-kicker">需要确认</p><h2>本次分析可以使用多个数据集。</h2><p>{scope?.reason || "请选择本次主要分析数据。"}</p>{candidates.length ? <fieldset><legend>选择本次主要分析数据</legend>{candidates.map((candidate) => <label key={candidate.dataset_id}><input type="radio" name="scope-dataset" value={candidate.dataset_id} checked={selected === candidate.dataset_id} onChange={() => setSelected(candidate.dataset_id)} />{candidate.name} · {candidate.semantics.join("、")}</label>)}</fieldset> : null}<p className="product-form-hint">确认后会在当前研究会话中继续，不会创建跨数据集的单个运行。</p><button className="product-primary-action" disabled={!selected} onClick={() => void onConfirm(selected)}>确认数据范围</button></div>;
}

export function ReportsPage({ projectId }: { projectId: string }) {
  const [history, setHistory] = useState<ProjectHistory | null>(null);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">("loading");
  const [reloadKey, setReloadKey] = useState(0);
  useEffect(() => {
    let active = true;
    setLoadState("loading");
    void getProjectHistory(projectId)
      .then((value) => { if (active) { setHistory(value); setLoadState("ready"); } })
      .catch(() => { if (active) setLoadState("error"); });
    return () => { active = false; };
  }, [projectId, reloadKey]);
  const reports = history?.analyses.filter((item) => item.visibleInReports !== false && (item.reportCount > 0 || ["completed", "succeeded", "success"].includes(item.status.toLowerCase()))) || [];
  return <RequireProductAuth><ProductShell projectId={projectId}><section className="document-page"><header className="product-page-heading"><p className="product-kicker">报告</p><h1>分析报告</h1><p>这个项目中的分析报告，保留研究目标、方法、结果和依据。</p></header><div className="report-list">{loadState === "loading" ? <div className="product-loading" role="status" aria-live="polite">正在加载项目报告…</div> : loadState === "error" ? <div className="product-state" role="alert"><h2>报告列表暂时无法加载</h2><p>已生成的报告没有丢失，请检查服务连接后重试。</p><button type="button" className="product-primary-action" onClick={() => setReloadKey((value) => value + 1)}>重新加载</button></div> : <>{reports.map((run) => { const dataset = history?.datasets.find((item) => item.datasetId === run.datasetId); return <Link className="report-list-row" key={run.jobId} href={"/projects/" + projectId + "/reports/" + run.jobId}><div><span className="product-kicker">分析报告</span><h2>{researchRunTitle(run)}</h2><p>{dataset?.name || "项目数据"} · {run.artifactCount} 个结果 · {run.stepCount} 个步骤</p></div><span>阅读报告 →</span></Link>; })}{reports.length === 0 && <div className="product-state"><h2>还没有分析报告</h2><p>完成一次研究后，分析报告会出现在这里。</p></div>}</>}</div></section></ProductShell></RequireProductAuth>;
}

export function ReportReaderPage({ projectId, reportId }: { projectId: string; reportId: string }) {
  const [history, setHistory] = useState<ProjectHistory | null>(null);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [interpretation, setInterpretation] = useState<GroundedScientificInterpretation | null>(null);
  const [runDetail, setRunDetail] = useState<PlannerJobDetail | null>(null);
  const [reportEvidence, setReportEvidence] = useState<InterpretationEvidenceResponse | null>(null);
  const [editorial, setEditorial] = useState<ReportEditorialProjection | null>(null);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">("loading");
  useEffect(() => { void getProjectHistory(projectId).then(setHistory); }, [projectId]);
  useEffect(() => {
    const controller = new AbortController();
    setLoadState("loading");
    void Promise.allSettled([getPlannerJobArtifacts(reportId), getPlannerJobInterpretations(reportId), getPlannerJob(reportId)])
      .then(([artifactResult, interpretationResult, detailResult]) => {
        if (controller.signal.aborted) return;
        setArtifacts(artifactResult.status === "fulfilled" ? artifactResult.value : []);
        const nextInterpretation = interpretationResult.status === "fulfilled" ? interpretationResult.value.interpretations?.[0] || null : null;
        setInterpretation(nextInterpretation);
        setRunDetail(detailResult.status === "fulfilled" ? detailResult.value : null);
        if (nextInterpretation) void getPlannerInterpretationEvidence(nextInterpretation.interpretationId).then(setReportEvidence).catch(() => setReportEvidence(null));
        setLoadState(artifactResult.status === "fulfilled" || interpretationResult.status === "fulfilled" || detailResult.status === "fulfilled" ? "ready" : "error");
      })
      .catch(() => { if (!controller.signal.aborted) setLoadState("error"); });
    return () => controller.abort();
  }, [reportId]);
  const report = history?.analyses.find((item) => item.jobId === reportId);
  useEffect(() => {
    if (!report?.workspaceId) { setEditorial(null); return; }
    const controller = new AbortController();
    void listReportCompositions(report.workspaceId, controller.signal)
      .then((value) => value.items.find((item) => item.sourceJobId === reportId))
      .then((item) => item ? getReportComposition(report.workspaceId!, item.reportId, controller.signal) : null)
      .then((detail) => { if (!controller.signal.aborted) setEditorial(detail?.editorialProjection || null); })
      .catch(() => { if (!controller.signal.aborted) setEditorial(null); });
    return () => controller.abort();
  }, [report?.workspaceId, reportId]);
  const reportArtifacts = projectScientificArtifacts(artifacts);
  const researchQuestion = editorial?.researchQuestion || report?.userQuestion || runDetail?.analysisPlan?.goal || "本次研究围绕项目中的材料数据展开。";
  const reportTitle = editorial?.reportTitle || scientificResultTitle(researchQuestion, artifacts, interpretation);
  const claims = userFacingClaims(interpretation);
  const limitations = userFacingLimitations(interpretation);
  const narrative = groundedEvidenceNarrative(reportEvidence);
  const primaryArtifact = reportArtifacts.find((item) => item.resultRole === "PRIMARY_FIGURE")
    || reportArtifacts.find((item) => item.resultRole === "PRIMARY_TABLE")
    || reportArtifacts[0];
  const supportingArtifacts = reportArtifacts.filter((item) => item !== primaryArtifact);
  const reportLimitations = editorial?.limitations?.length ? editorial.limitations : limitations;
  const canManageReport = canWriteProject(history?.project?.role);
  const [archiveBusy, setArchiveBusy] = useState(false);
  const toggleArchive = async () => {
    setArchiveBusy(true);
    try {
      if (report?.archived) await restoreProjectRun(projectId, reportId);
      else await archiveProjectRun(projectId, reportId);
      setHistory((current) => current ? { ...current, analyses: current.analyses.map((item) => item.jobId === reportId ? { ...item, archived: !item.archived, visibleInReports: item.archived } : item) } : current);
    } finally { setArchiveBusy(false); }
  };
  return (
    <RequireProductAuth>
      <ProductShell projectId={projectId}>
        <article className="report-reader">
          <Link href={`/projects/${projectId}/reports`} className="back-link">← 返回报告</Link>
          <div className="report-reader-actions">
            <p className="product-kicker">分析报告 · 单次运行</p>
            <div className="workbench-heading-actions">
              {report?.datasetId ? <Link className="product-secondary-action" href={`/projects/${projectId}/data?dataset=${report.datasetId}`}>查看数据</Link> : null}
              <Link className="product-secondary-action" href={researchRunHref(projectId, reportId, [], report?.researchSessionId, report?.researchTurnId)}>返回研究</Link>
              {canManageReport ? <button type="button" className="product-secondary-action" onClick={() => void toggleArchive()} disabled={archiveBusy || !report}>
              {report?.archived ? "恢复到报告列表" : "归档此报告"}
              </button> : null}
            </div>
          </div>
          <h1>{reportTitle}</h1>
          <p className="report-meta">
            {report?.archived ? "已归档 · " : ""}{history?.datasets.find((item) => item.datasetId === report?.datasetId)?.name || "项目数据"} · {reportArtifacts.length || report?.artifactCount || 0} 个输出 · {report?.stepCount || runDetail?.analysisPlan?.steps?.length || 0} 个步骤
          </p>
          <hr />
          <section className="report-primary-result" aria-labelledby="report-primary-result-title"><h2 id="report-primary-result-title">主要结果</h2>{loadState === "loading" ? <p className="product-loading" role="status">正在加载运行结果…</p> : loadState === "error" ? <p className="product-form-error" role="alert">运行结果暂时无法读取，历史摘要仍然可用。</p> : primaryArtifact ? <ReportArtifactFigure artifact={primaryArtifact} projectId={projectId} datasetId={report?.datasetId} reportId={reportId} artifacts={artifacts} /> : <div className="product-state"><h3>本次运行没有可展示的结果</h3><p>保留运行记录和限制信息。</p></div>}</section>
          <section className="report-conclusion" aria-labelledby="report-conclusion-title"><h2 id="report-conclusion-title">主要结论</h2><p>{editorial?.summary || claims[0]?.renderedText || narrative.finding || "本次报告汇总已验证的科学输出、依据和限制。"}</p>{claims.length ? <ul className="report-findings">{claims.map((claim) => <li key={claim.claimId}><strong>发现</strong><p>{claim.renderedText}</p></li>)}</ul> : null}</section>
          <section className="report-limitations" aria-labelledby="report-limitations-title"><h2 id="report-limitations-title">限制</h2>{reportLimitations.length ? <ul>{reportLimitations.map((item) => <li key={item}>{item}</li>)}</ul> : <p>{narrative.limitation || "报告结论仅适用于本次运行选择的数据和经过验证的工具步骤。"}</p>}</section>
          {supportingArtifacts.length ? <details className="report-supporting-results"><summary>支持性结果 · {supportingArtifacts.length} 项</summary><div className="report-artifact-list">{supportingArtifacts.map((artifact) => <ReportArtifactFigure key={artifact.artifactId || artifact.id} artifact={artifact} projectId={projectId} datasetId={report?.datasetId} reportId={reportId} artifacts={artifacts} />)}</div></details> : null}
          <h2>研究问题</h2>
          <p>{researchQuestion}</p>
          <h2>方法与依据</h2>
          <p>{editorial?.methodSummary?.join("；") || "分析方案、来源数据、输出与可复现信息由运行记录提供。"}</p>
          {reportEvidence?.evidenceItems?.length ? <details><summary>依据 · {reportEvidence.evidenceItems.length} 项</summary><ul>{reportEvidence.evidenceItems.map((item) => <li key={item.evidenceItemId}>{evidenceLabel(item.semanticRole)}：{displayEvidenceValue(item.displayValue)}</li>)}</ul></details> : null}
          {interpretation ? <details><summary>来源与过程</summary><p>结论来自已完成的科学解释，依据已与本次运行绑定。</p></details> : null}
          <details><summary>复现信息</summary><p>此报告对应单次分析运行；复现信息由运行方案和来源资源绑定提供，不自动重新执行。</p></details>
        </article>
      </ProductShell>
    </RequireProductAuth>
  );
}

function ReportArtifactFigure({ artifact, projectId, datasetId, reportId, artifacts }: { artifact: ReturnType<typeof projectScientificArtifacts>[number]; projectId: string; datasetId?: string; reportId: string; artifacts: Artifact[] }) {
  return <section className={`report-figure result-role-${artifact.resultRole.toLowerCase()}`}><span>{artifact.resultRole === "PRIMARY_FIGURE" || artifact.resultRole === "PRIMARY_TABLE" ? "主要结果" : artifactLabel(artifact.type)}</span><strong>{artifact.resultTitle}</strong><ScientificResultViewer projectId={projectId} datasetId={datasetId} jobId={reportId} selected={artifact} artifacts={artifacts} /><p>{artifact.resultRole === "PRIMARY_FIGURE" || artifact.resultRole === "PRIMARY_TABLE" ? "图表、表格和单位来自本次运行的已验证输出。" : "支持性科学输出，供结果复核使用。"}</p></section>;
}
