"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  createAgent2ResearchTurn,
  getAgent2ResearchTurnInterpretation,
  getAgent2ResearchTurnResult,
  type Agent2ResearchTurnInterpretation,
  type Agent2ResearchTurnResult,
} from "../lib/agent2-research-api";
import { compileScientificPresentation } from "../lib/scientific-presentation";
import { ScientificPresentationBlocks } from "./ScientificPresentationBlocks";
import type { ScientificEvidenceItem } from "../lib/planner-api";

export function Agent2ScientificPresentation({ turnId, projectId, sessionId }: { turnId: string; projectId: string; sessionId?: string }) {
  const router = useRouter();
  const [result, setResult] = useState<Agent2ResearchTurnResult | null>(null);
  const [interpretation, setInterpretation] = useState<Agent2ResearchTurnInterpretation | null>(null);
  const [failed, setFailed] = useState(false);
  const [reinterpretPending, setReinterpretPending] = useState(false);
  const [reinterpretError, setReinterpretError] = useState("");

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

  const presentation = compileScientificPresentation({
    resultId: result.result_id,
    interpretationId: interpretation?.interpretation_id,
    relevance: result.relevance_status,
    interpretation: interpretation?.status === "VALID" ? interpretation.interpretation : undefined,
    evidence,
    artifacts: result.artifacts || [],
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
      const next = await createAgent2ResearchTurn(projectId, sessionId, {
        message: "请重新解释这份科学结果，突出关键发现、证据与限制；不要重新计算科学结果。",
        ui_context: {
          active_object_refs: refs,
          selection_refs: refs,
          scientific_selections: result.scientific_selections || [],
          explicit_object_refs: refs,
          explicit_result_ids: [result.result_id],
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
  return <section className="agent2-scientific-presentation">
    <ScientificPresentationBlocks presentation={presentation} projectId={projectId} instanceId={turnId} />
    {sessionId && result ? <div className="scientific-presentation-actions">
      <button type="button" className="product-secondary-action" onClick={() => void reinterpret()} disabled={reinterpretPending}>
        {reinterpretPending ? "正在创建解释分支…" : "重新解释（不重算科学结果）"}
      </button>
      {reinterpretError ? <p className="product-form-error" role="alert">{reinterpretError}</p> : null}
    </div> : null}
  </section>;
}
