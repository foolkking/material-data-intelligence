"use client";

import React, { useEffect, useRef, useState } from "react";
import type { Agent2ResearchTurnResult } from "../../app/lib/agent2-research-api";
import type { ResultResearchAction } from "./result-follow-up";
import { compileScientificPresentation } from "../../app/lib/scientific-presentation";
import { ScientificPresentationBlocks } from "./ScientificPresentationBlocks";
import type { ScientificEvidenceItem } from "../../app/lib/planner-api";
import { hasPinnedObject, type SessionMemoryController } from "./use-session-memory";
import { SessionMemoryNotice } from "./SessionMemoryNotice";
import { useTurnPresentation } from "./use-turn-presentation";
import type { Agent2ProgressView } from "../../app/lib/agent2-execution-api";
import { ScientificToolProcess } from "./ScientificToolProcess";
import { SavedResearchOutputs } from "./ResearchTurnResultState";
import { resolveResultVisualTarget, type ResearchResultTarget } from "./result-navigation";

type Agent2ScientificPresentationProps = {
  turnId: string;
  projectId: string;
  sessionId?: string;
  context?: SessionMemoryController;
  onContinue?: () => void;
  onEdit?: () => void;
  onRun?: (action: ResultResearchAction, result: Agent2ResearchTurnResult) => Promise<void>;
  canModify?: boolean;
  progress?: Agent2ProgressView | null;
  resultTarget?: ResearchResultTarget;
};

export function Agent2ScientificPresentation({
  turnId,
  projectId,
  sessionId,
  context,
  onContinue,
  onEdit,
  onRun,
  canModify = true,
  progress,
  resultTarget,
}: Agent2ScientificPresentationProps) {
  const ownedProgress = progress?.turn_id === turnId ? progress : null;
  const interpretationReady = !ownedProgress || !["RESULT_READY", "INTERPRETING", "RESULT_PENDING"].includes(ownedProgress.status);
  const reads = useTurnPresentation(projectId, turnId, interpretationReady);
  const result = reads.result.value;
  const interpretation = reads.interpretation.value;
  const [resultActionPending, setResultActionPending] = useState<ResultResearchAction | null>(null);
  const [resultActionError, setResultActionError] = useState("");
  const resultActionOwner = useRef<symbol | null>(null);
  useEffect(() => {
    setResultActionPending(null); setResultActionError("");
    return () => { resultActionOwner.current = null; };
  }, [projectId, sessionId, turnId]);
  const memory = context?.memory;
  const resultPinned = Boolean(memory && result && memory.pinned_result_refs.includes(result.result_snapshot_id || result.result_id));
  const sourceCount = (result?.source_object_refs || []).filter((ref) => memory && hasPinnedObject(memory, ref)).length;
  const sourcesPinned = Boolean(sourceCount && sourceCount === result?.source_object_refs?.length);
  const pinPending = Boolean(context?.updating);

  const readNotice = (
    <div className="research-result-read-error" role="status">
      {reads.result.failed ? <p>分析结果暂时无法读取，请重试。</p> : null}
      {reads.interpretation.failed && result ? <p>{reads.interpretation.notReady && !interpretation
        ? ownedProgress?.status === "FAILED" || ownedProgress?.status === "CANCELED"
          ? "本次研究未生成可用解读，已完成的科学结果仍可查看。"
          : "结果解读尚未生成，已完成的科学结果仍可查看。"
        : "结果解读暂时无法读取，分析结果仍可查看。"}</p> : null}
      {reads.result.failed ? <button type="button" className="product-secondary-action" disabled={reads.result.pending} onClick={reads.result.retry}>{reads.result.pending ? "正在读取…" : "重新读取分析结果"}</button> : null}
      {reads.interpretation.failed && result ? <button type="button" className="product-secondary-action" disabled={reads.interpretation.pending} onClick={reads.interpretation.retry}>{reads.interpretation.pending ? "正在读取…" : reads.interpretation.notReady && !interpretation ? "检查解读状态" : "重新读取结果解读"}</button> : null}
    </div>
  );
  if (!result) {
    return <div className="agent2-scientific-presentation">
      {reads.result.failed ? readNotice : <section className="scientific-presentation scientific-presentation-unavailable" role="status"><p>正在读取分析结果…</p></section>}
      <SavedResearchOutputs turnId={turnId} progress={ownedProgress} />
    </div>;
  }

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

  // The saved polyhedron result owns its N1 dependency, but only N2 is its
  // visual. Keep the original dependency available in the tool process.
  const polyhedronItems = (result.result_items || []).filter(item => item.result_type === "structure.local_environment.polyhedra");
  const declaredVisualIds = new Set([...(result.figures || []), ...(result.tables || [])].flatMap(item => item.artifact_ids));
  const dependencyIds = new Set(polyhedronItems.flatMap(item => item.artifact_ids).filter(id => !declaredVisualIds.has(id)));
  const presentation = compileScientificPresentation({
    resultId: result.result_id,
    interpretationId: interpretation?.interpretation_id,
    relevance: result.relevance_status,
    persistedInterpretation: interpretation?.status === "VALID" ? interpretation.interpretation : undefined,
    evidence,
    artifacts: (result.artifacts || []).filter(artifact => !dependencyIds.has(artifact.artifactId || artifact.id || "")),
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
  async function runResultAction(action: ResultResearchAction) {
    if (!onRun || !result || resultActionOwner.current) return;
    const owner = Symbol(); resultActionOwner.current = owner;
    setResultActionPending(action); setResultActionError("");
    try { await onRun(action, result); }
    catch (reason) { if (resultActionOwner.current === owner) setResultActionError(reason instanceof Error ? reason.message : "研究请求暂未确认，请重试。"); }
    finally { if (resultActionOwner.current === owner) { resultActionOwner.current = null; setResultActionPending(null); } }
  }
  return <section className="agent2-scientific-presentation">
    {reads.result.failed || reads.interpretation.failed ? readNotice : null}
    {!reads.interpretation.failed && reads.interpretation.pending ? <p className="scientific-presentation-action-status" role="status">正在读取结果解读…</p> : null}
    {!reads.interpretation.failed && interpretation?.status === "PENDING" ? <p className="scientific-presentation-action-status" role="status">结果解读尚未完成。 <button type="button" className="product-link-button" disabled={reads.interpretation.pending} onClick={reads.interpretation.retry}>重新读取结果解读</button></p> : null}
    {!reads.interpretation.failed && interpretation?.status === "REJECTED" ? <p className="scientific-presentation-action-status" role="status">结果解读未通过检查，分析结果仍可查看。</p> : null}
    <ScientificPresentationBlocks
      layout="research"
      presentation={presentation}
      projectId={projectId}
      instanceId={turnId}
      artifactCatalog={result.artifacts || []}
      resultFacts={result.facts || []}
      inputProvenance={result.input_provenance}
      visualTarget={resolveResultVisualTarget(result, resultTarget)}
      executionProcess={<ScientificToolProcess turnId={turnId} projectId={projectId} sources={result.source_object_refs || []} artifacts={result.artifacts || []} toolCallIds={result.tool_call_ids} progress={ownedProgress} />}
    />
    {sessionId && result && canModify ? <section className="scientific-presentation-actions" aria-labelledby={`scientific-presentation-actions-${turnId}`}>
      <div className="scientific-presentation-actions-heading">
        <h3 id={`scientific-presentation-actions-${turnId}`}>下一步</h3>
      </div>
      <div className="scientific-presentation-action-primary">
        <button type="button" className="product-primary-action" onClick={onContinue} disabled={!onContinue || Boolean(resultActionPending)}>
          继续研究
        </button>
        <button type="button" className="product-secondary-action" onClick={onEdit} disabled={!onEdit || Boolean(resultActionPending)}>
          编辑问题
        </button>
      </div>
      <details className="scientific-presentation-more-actions">
      <summary>更多操作</summary>
      <div className="scientific-presentation-action-secondary" aria-label="其他研究操作">
        <button type="button" className="product-secondary-action" onClick={() => void runResultAction("reinterpret")} disabled={!onRun || Boolean(resultActionPending)}>
          {resultActionPending === "reinterpret" ? "正在创建解释分支…" : "重新解释（不重算科学结果）"}
        </button>
        <button type="button" className="product-secondary-action scientific-presentation-rerun" onClick={() => void runResultAction("rerun")} disabled={!onRun || Boolean(resultActionPending)}>
          {resultActionPending === "rerun" ? "正在创建新的研究运行…" : "重新研究（新运行）"}
        </button>
        <button type="button" className="product-secondary-action" onClick={() => void context?.setResultPinned(result.result_snapshot_id || result.result_id, !resultPinned)} disabled={!context?.canUpdate}>
          {pinPending ? "正在更新上下文…" : resultPinned ? "从本会话上下文移除结果" : "将结果加入本会话上下文"}
        </button>
        {result.source_object_refs?.length ? (
          <button type="button" className="product-secondary-action" onClick={() => void context?.setSourcesPinned(result.source_object_refs || [], !sourcesPinned)} disabled={!context?.canUpdate}>
            {pinPending ? "正在更新来源…" : sourcesPinned ? "从本会话上下文移除来源版本" : "将来源版本加入本会话上下文"}
          </button>
        ) : null}
      </div>
      </details>
      {resultActionError ? <p className="product-form-error" role="alert">{resultActionError}</p> : null}
      {context ? <SessionMemoryNotice context={context} /> : null}
      {sourceCount > 0 && !sourcesPinned ? <p className="scientific-presentation-action-status">已加入 {sourceCount} / {result.source_object_refs?.length} 个来源。</p> : null}
      {resultActionPending ? <p className="scientific-presentation-action-status" role="status" aria-live="polite">正在提交操作，科学结果本身不会被覆盖。</p> : null}
    </section> : null}
  </section>;
}
