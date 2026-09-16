"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  createAgent2ResearchTurn,
  getAgent2ResearchTurnInterpretation,
  getAgent2ResearchTurnResult,
  type Agent2ResearchTurnInterpretation,
  type Agent2ResearchTurnResult,
} from "../../app/lib/agent2-research-api";
import { compileScientificPresentation } from "../../app/lib/scientific-presentation";
import { ScientificPresentationBlocks } from "./ScientificPresentationBlocks";
import type { ScientificEvidenceItem } from "../../app/lib/planner-api";
import {
  getAgent2SessionMemory,
  pinAgent2Object,
  pinAgent2Result,
  unpinAgent2Object,
  unpinAgent2Result,
  type Agent2SessionMemory,
} from "../../app/lib/agent2-memory-api";
import { useProductRouter } from "../../shared/layout/ProductNavigation";

type Agent2ScientificPresentationProps = {
  turnId: string;
  projectId: string;
  sessionId?: string;
  sessionMemory?: Agent2SessionMemory | null;
  onSessionMemoryChange?: (memory: Agent2SessionMemory) => void;
};

export function Agent2ScientificPresentation({
  turnId,
  projectId,
  sessionId,
  sessionMemory,
  onSessionMemoryChange,
}: Agent2ScientificPresentationProps) {
  const router = useProductRouter();
  const [result, setResult] = useState<Agent2ResearchTurnResult | null>(null);
  const [interpretation, setInterpretation] = useState<Agent2ResearchTurnInterpretation | null>(null);
  const [failed, setFailed] = useState(false);
  const [reinterpretPending, setReinterpretPending] = useState(false);
  const [reinterpretError, setReinterpretError] = useState("");
  const [followUpPending, setFollowUpPending] = useState<"continue" | "rerun" | null>(null);
  const [followUpError, setFollowUpError] = useState("");
  const [resultPinned, setResultPinned] = useState(false);
  const [sourcesPinned, setSourcesPinned] = useState(false);
  const [pinPending, setPinPending] = useState(false);
  const [pinError, setPinError] = useState("");
  const pinMutationSeq = useRef(0);

  useEffect(() => {
    let active = true;
    setFailed(false);
    void getAgent2ResearchTurnResult(turnId)
      .then((next) => { if (active) setResult(next); })
      .catch(() => { if (active) setFailed(true); });
    void getAgent2ResearchTurnInterpretation(turnId)
      .then((next) => { if (active) setInterpretation(next); })
      .catch(() => { if (active) setInterpretation(null); });
    return () => { active = false; };
  }, [turnId]);

  useEffect(() => {
    if (!sessionId || !result?.result_id) {
      setResultPinned(false);
      setSourcesPinned(false);
      return;
    }
    const applyMemory = (memory: Agent2SessionMemory | null) => {
      setResultPinned(
        Boolean(memory) &&
          memory!.pinned_result_refs.includes(
            result.result_snapshot_id || result.result_id,
          ),
      );
      const refs = result.source_object_refs || [];
      setSourcesPinned(
        Boolean(memory) &&
          refs.length > 0 &&
          refs.every((source) =>
            (memory!.pinned_object_refs || []).some(
              (pinned) =>
                pinned.object_id === source.object_id &&
                pinned.version_id === source.version_id,
            ),
          ),
      );
    };
    if (sessionMemory !== undefined) {
      applyMemory(sessionMemory);
      return;
    }
    let active = true;
    const requestSeq = pinMutationSeq.current;
    void getAgent2SessionMemory(projectId, sessionId)
      .then((memory) => {
        if (active && requestSeq === pinMutationSeq.current) {
          applyMemory(memory);
        }
      })
      .catch(() => {
        if (active && requestSeq === pinMutationSeq.current) {
          applyMemory(null);
        }
      });
    return () => { active = false; };
  }, [
    projectId,
    sessionId,
    sessionMemory,
    result?.result_id,
    result?.result_snapshot_id,
    result?.source_object_refs,
  ]);

  if (failed) return <section className="scientific-presentation scientific-presentation-unavailable" role="status"><p>科学结果已保存；呈现投影暂时无法读取。</p></section>;
  if (!result) return <section className="scientific-presentation scientific-presentation-unavailable" role="status"><p>正在读取已验证的科学结果…</p></section>;

  const evidence: ScientificEvidenceItem[] = (result.evidence || []).map((item) => ({
    schemaVersion: "1.0",
    evidenceItemId: item.evidence_id,
    semanticRole: item.evidence_type,
    evidenceKind: "PROVENANCE",
    subjectId: item.supports_result_item_refs?.[0] || item.supports_fact_refs?.[0] || item.evidence_id,
    displayValue: item.evidence_type,
    unit: null,
    sourceArtifactId: item.artifact_id || item.evidence_id,
    sourceArtifactChecksum: "",
    artifactContract: "scientific-result-evidence",
    artifactContractVersion: "1.0",
    sourceToolId: item.tool_call_id || "scientific-result",
    sourceToolVersion: "1.0",
    fieldLocator: { fieldId: item.artifact_locator || item.evidence_id },
    warnings: [],
    limitations: [],
  }));
  const artifactSourceRefs = (result.result_items || []).reduce<
    Record<
      string,
      Array<{
        objectId: string;
        versionId: string;
        objectType?: string;
        displayName?: string;
      }>
    >
  >((mapping, item) => {
    const sources = (item.scientific_object_refs || []).map((source) => ({
      objectId: source.object_id,
      versionId: source.version_id,
      versionNo: source.version_no,
      objectType: source.object_type,
      displayName: source.display_name,
    }));
    for (const artifactId of item.artifact_ids || []) {
      const known = mapping[artifactId] || [];
      mapping[artifactId] = [
        ...new Map(
          [...known, ...sources].map((source) => [
            `${source.objectId}:${source.versionId}`,
            source,
          ]),
        ).values(),
      ];
    }
    return mapping;
  }, {});

  const presentation = compileScientificPresentation({
    resultId: result.result_id,
    interpretationId: interpretation?.interpretation_id,
    relevance: result.relevance_status,
    persistedInterpretation: interpretation?.status === "VALID" ? interpretation.interpretation : undefined,
    evidence,
    artifacts: result.artifacts || [],
    artifactSourceRefs,
    validatedNarrative: interpretation?.status === "VALID" ? interpretation.message : undefined,
    facts: (result.facts || []).map((fact) => ({
      factId: fact.fact_id,
      predicate: fact.predicate,
      subjectRef: fact.subject_ref,
      value: fact.value,
      unit: fact.unit,
      source: {
        artifactId: fact.source.artifact_id,
        toolCallId: fact.source.tool_call_id,
        scientificObjectRef: fact.source.scientific_object_ref
          ? { objectId: fact.source.scientific_object_ref.object_id, versionId: fact.source.scientific_object_ref.version_id }
          : undefined,
      },
    })),
    sourceObjectRefs: (result.source_object_refs || []).map((source) => ({
      objectId: source.object_id,
      versionId: source.version_id,
      objectType: source.object_type,
      displayName: source.display_name,
    })),
    scientificSelections: (result.scientific_selections || []).map((selection) => ({
      selectionType: selection.selection_type,
      semanticLocator: selection.semantic_locator,
    })),
  });
  async function reinterpret() {
    if (!sessionId || !result || reinterpretPending) return;
    setReinterpretPending(true);
    setReinterpretError("");
    try {
      const refs = result.source_object_refs || [];
      const snapshotId = result.result_snapshot_id || result.result_id;
      const next = await createAgent2ResearchTurn(projectId, sessionId, {
        message: "请重新解释这份科学结果，突出关键发现、证据与限制；不要重新计算科学结果。",
        reply_to_turn_id: turnId,
        ui_context: {
          active_object_refs: refs,
          selection_refs: refs,
          scientific_selections: result.scientific_selections || [],
          explicit_object_refs: refs,
          explicit_result_ids: [snapshotId],
          explicit_finding_refs: [],
        },
      });
      router.push(`/projects/${projectId}/research/${encodeURIComponent(sessionId)}?turn=${encodeURIComponent(next.turn_id)}`);
    } catch (reason) {
      setReinterpretError(reason instanceof Error ? reason.message : "重新解释请求未能提交");
    } finally {
      setReinterpretPending(false);
    }
  }
  async function createFollowUp(mode: "continue" | "rerun") {
    if (!sessionId || !result || followUpPending) return;
    setFollowUpPending(mode);
    setFollowUpError("");
    try {
      const refs = result.source_object_refs || [];
      const isContinue = mode === "continue";
      const snapshotId = result.result_snapshot_id || result.result_id;
      const next = await createAgent2ResearchTurn(projectId, sessionId, {
        message: isContinue
          ? "请基于这份已完成的科学结果继续研究，只补充当前证据支持的后续分析；如需新的计算，请明确说明。"
          : `请重新执行同一个科学研究问题：${result.research_question}。这是一次新的研究运行，不要覆盖之前的结果。`,
        reply_to_turn_id: turnId,
        ui_context: {
          active_object_refs: refs,
          selection_refs: refs,
          scientific_selections: result.scientific_selections || [],
          explicit_object_refs: refs,
          explicit_result_ids: isContinue ? [snapshotId] : [],
          explicit_finding_refs: [],
        },
      });
      router.push(`/projects/${projectId}/research/${encodeURIComponent(sessionId)}?turn=${encodeURIComponent(next.turn_id)}`);
    } catch (reason) {
      setFollowUpError(reason instanceof Error ? reason.message : "后续研究请求未能提交");
    } finally {
      setFollowUpPending(null);
    }
  }
  function editQuestion() {
    if (!sessionId || !result) return;
    router.push(`/projects/${projectId}/research/${encodeURIComponent(sessionId)}?turn=${encodeURIComponent(turnId)}&edit=${encodeURIComponent(turnId)}`);
  }
  async function togglePinnedResult() {
    if (!sessionId || !result || pinPending) return;
    pinMutationSeq.current += 1;
    const previousPinned = resultPinned;
    setResultPinned(!previousPinned);
    setPinPending(true);
    setPinError("");
    try {
      const next = resultPinned
        ? await unpinAgent2Result(projectId, sessionId, result.result_snapshot_id || result.result_id)
        : await pinAgent2Result(projectId, sessionId, result.result_snapshot_id || result.result_id);
      // Invalidate any session-memory read that started before this mutation
      // completed. Without this bump, a slower stale read can overwrite the
      // optimistic/server-confirmed pin state and make the control appear to
      // have reverted.
      pinMutationSeq.current += 1;
      setResultPinned(next.pinned_result_refs.includes(result.result_snapshot_id || result.result_id));
      onSessionMemoryChange?.(next);
    } catch (reason) {
      pinMutationSeq.current += 1;
      setResultPinned(previousPinned);
      setPinError(reason instanceof Error ? reason.message : "上下文固定操作未能完成");
    } finally {
      setPinPending(false);
    }
  }
  async function togglePinnedSources() {
    if (!sessionId || !result || pinPending || !result.source_object_refs?.length) return;
    const refs = result.source_object_refs;
    const previousPinned = sourcesPinned;
    setSourcesPinned(!previousPinned);
    setPinPending(true);
    setPinError("");
    try {
      let nextMemory = null;
      for (const source of refs) {
        const objectRef = {
          object_id: source.object_id,
          version_id: source.version_id,
          project_id: source.project_id,
          object_type: source.object_type,
          display_name: source.display_name,
        };
        nextMemory = previousPinned
          ? await unpinAgent2Object(projectId, sessionId, objectRef)
          : await pinAgent2Object(projectId, sessionId, objectRef);
      }
      pinMutationSeq.current += 1;
      setSourcesPinned(
        Boolean(nextMemory) &&
          refs.every((source) =>
            (nextMemory!.pinned_object_refs || []).some(
              (pinned) =>
                pinned.object_id === source.object_id &&
                pinned.version_id === source.version_id,
            ),
          ),
      );
      if (nextMemory) onSessionMemoryChange?.(nextMemory);
    } catch (reason) {
      pinMutationSeq.current += 1;
      setSourcesPinned(previousPinned);
      setPinError(reason instanceof Error ? reason.message : "来源版本固定操作未能完成");
    } finally {
      setPinPending(false);
    }
  }
  return <section className="agent2-scientific-presentation">
    <ScientificPresentationBlocks
      presentation={presentation}
      projectId={projectId}
      instanceId={turnId}
      artifactCatalog={result.artifacts || []}
    />
    {sessionId && result ? <section className="scientific-presentation-actions" aria-labelledby={`scientific-presentation-actions-${turnId}`}>
      <div className="scientific-presentation-actions-heading">
        <h3 id={`scientific-presentation-actions-${turnId}`}>继续这项研究</h3>
        <p>下面的操作会明确区分继续、重新计算与仅重新解释。</p>
      </div>
      <div className="scientific-presentation-action-primary">
        <button type="button" className="product-primary-action" onClick={() => void createFollowUp("continue")} disabled={Boolean(followUpPending) || reinterpretPending}>
          {followUpPending === "continue" ? "正在准备后续研究…" : "继续研究"}
        </button>
        <button type="button" className="product-secondary-action" onClick={editQuestion} disabled={Boolean(followUpPending) || reinterpretPending}>
          编辑问题
        </button>
      </div>
      <div className="scientific-presentation-action-secondary" aria-label="其他研究操作">
        <button type="button" className="product-secondary-action" onClick={() => void reinterpret()} disabled={reinterpretPending}>
          {reinterpretPending ? "正在创建解释分支…" : "重新解释（不重算科学结果）"}
        </button>
        <button type="button" className="product-secondary-action scientific-presentation-rerun" onClick={() => void createFollowUp("rerun")} disabled={Boolean(followUpPending) || reinterpretPending}>
          {followUpPending === "rerun" ? "正在创建新的研究运行…" : "重新研究（新运行）"}
        </button>
        <button type="button" className="product-secondary-action" onClick={() => void togglePinnedResult()} disabled={pinPending}>
          {pinPending ? "正在更新上下文…" : resultPinned ? "从本会话上下文移除结果" : "将结果加入本会话上下文"}
        </button>
        {result.source_object_refs?.length ? (
          <button type="button" className="product-secondary-action" onClick={() => void togglePinnedSources()} disabled={pinPending}>
            {pinPending ? "正在更新来源…" : sourcesPinned ? "从本会话上下文移除来源版本" : "将来源版本加入本会话上下文"}
          </button>
        ) : null}
      </div>
      <p className="scientific-presentation-action-status">
        本会话上下文会影响后续研究；列表置顶只改变排序，不会进入科学上下文。
      </p>
      {followUpError ? <p className="product-form-error" role="alert">{followUpError}</p> : null}
      {reinterpretError ? <p className="product-form-error" role="alert">{reinterpretError}</p> : null}
      {pinError ? <p className="product-form-error" role="alert">{pinError}</p> : null}
      {(followUpPending || reinterpretPending || pinPending) ? <p className="scientific-presentation-action-status" role="status" aria-live="polite">正在提交操作，科学结果本身不会被覆盖。</p> : null}
    </section> : null}
  </section>;
}
