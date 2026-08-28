import type { Artifact, GroundedScientificInterpretation, ScientificEvidenceItem } from "./planner-api";
import type { ScientificReportView } from "./scientific-report-api";
import { projectScientificArtifacts } from "./scientific-result-projection";

export type PresentationSource = {
  resultId?: string | null;
  interpretationId?: string | null;
  factId?: string | null;
  evidenceId?: string | null;
  artifactId?: string | null;
  jobId?: string | null;
  toolCallId?: string | null;
  objectId?: string | null;
  versionId?: string | null;
};

export type AuthoritativePresentationFact = {
  factId: string;
  predicate: string;
  subjectRef: string;
  value: unknown;
  unit?: string | null;
  source?: {
    artifactId?: string | null;
    toolCallId?: string | null;
    scientificObjectRef?: { objectId: string; versionId: string } | null;
  };
};

export type ScientificPresentationBlock =
  | { id: string; type: "narrative"; title?: string; text: string; source: PresentationSource }
  | { id: string; type: "finding"; title: string; text: string; confidence: "DIRECT" | "QUALIFIED" | "LIMITED"; source: PresentationSource; evidenceIds: string[] }
  | { id: string; type: "metric"; title: string; value: string; unit?: string | null; source: PresentationSource }
  | { id: string; type: "table" | "figure"; title: string; artifactId: string; source: PresentationSource }
  | { id: string; type: "viewer_reference"; title: string; label: string; source: PresentationSource }
  | { id: string; type: "evidence_reference"; title: string; label: string; source: PresentationSource }
  | { id: string; type: "limitation" | "warning"; text: string; source: PresentationSource };

export type ScientificPresentation = {
  schemaVersion: "1.0";
  blocks: ScientificPresentationBlock[];
  exactSourceRefs: Array<{ objectId: string; versionId: string; objectType?: string; displayName?: string }>;
  historicalNotice?: string;
};

export type PresentationInput = {
  interpretation?: GroundedScientificInterpretation | null;
  /**
   * The persisted interpretation envelope owns this identity. Keep it
   * separate from the nested grounded payload because the latter is
   * intentionally scientific content only.
   */
  interpretationId?: string | null;
  evidence?: ScientificEvidenceItem[];
  artifacts?: Artifact[];
  facts?: AuthoritativePresentationFact[];
  validatedNarrative?: string | null;
  resultId?: string | null;
  sourceObjectRefs?: Array<{ objectId: string; versionId: string; objectType?: string; displayName?: string }>;
  scientificSelections?: Array<{
    selectionType: string;
    semanticLocator: Record<string, string | number | boolean>;
  }>;
  relevance?: "CURRENT" | "STALE" | "SOURCE_MISSING" | "INVALIDATED";
};

function stableId(prefix: string, value: string, index = 0): string {
  const normalized = value.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 72);
  return `${prefix}-${normalized || index}`;
}

function artifactId(artifact: Artifact): string {
  return artifact.artifactId || artifact.id || "";
}

function exactSource(sourceObjectRefs: PresentationInput["sourceObjectRefs"]): PresentationSource {
  const source = sourceObjectRefs?.[0];
  return source ? { objectId: source.objectId, versionId: source.versionId } : {};
}

function evidenceSource(item: ScientificEvidenceItem, resultId: string | null | undefined, interpretationId: string | null | undefined, sourceObjectRefs: PresentationInput["sourceObjectRefs"]): PresentationSource {
  return { ...exactSource(sourceObjectRefs), resultId, interpretationId, evidenceId: item.evidenceItemId, artifactId: item.sourceArtifactId, toolCallId: item.sourceToolId };
}

function displayFactValue(value: unknown): string | null {
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
  return null;
}

function selectedDatasetSampleRefs(selections: PresentationInput["scientificSelections"]): string[] {
  const refs = selections
    ?.filter((selection) => selection.selectionType === "DATASET_SAMPLE")
    .flatMap((selection) => {
      const locator = selection.semanticLocator || {};
      return [locator.sample_ref, locator.sample_id]
        .filter((value): value is string => typeof value === "string" && value.trim().length > 0);
    }) || [];
  return [...new Set(refs)];
}

function selectedFactsFirst(facts: AuthoritativePresentationFact[], selections: PresentationInput["scientificSelections"]): AuthoritativePresentationFact[] {
  const sampleRefs = selectedDatasetSampleRefs(selections);
  if (sampleRefs.length === 0) return facts;
  const matchesSelectedSample = (fact: AuthoritativePresentationFact) =>
    sampleRefs.some((sampleRef) => fact.subjectRef === sampleRef || fact.subjectRef.endsWith(`:${sampleRef}`));
  return [...facts.filter(matchesSelectedSample), ...facts.filter((fact) => !matchesSelectedSample(fact))];
}

function factSource(fact: AuthoritativePresentationFact, resultId: string | null | undefined, sourceObjectRefs: PresentationInput["sourceObjectRefs"]): PresentationSource {
  const exact = fact.source?.scientificObjectRef;
  return {
    ...(exact ? { objectId: exact.objectId, versionId: exact.versionId } : exactSource(sourceObjectRefs)),
    resultId,
    factId: fact.factId,
    artifactId: fact.source?.artifactId,
    toolCallId: fact.source?.toolCallId,
  };
}

function projectedArtifactBlocks(artifacts: Artifact[], resultId: string | null | undefined, sourceObjectRefs: PresentationInput["sourceObjectRefs"]): ScientificPresentationBlock[] {
  return projectScientificArtifacts(artifacts).slice(0, 12).map((artifact, index) => {
    const id = artifactId(artifact);
    const title = artifact.resultTitle;
    const source = { ...exactSource(sourceObjectRefs), resultId, artifactId: id, jobId: artifact.jobId };
    const isTable = artifact.resultRole.endsWith("TABLE");
    const block: ScientificPresentationBlock = { id: stableId(isTable ? "table" : "figure", title, index), type: isTable ? "table" : "figure", title, artifactId: id, source };
    return block;
  });
}

/**
 * Compile only bounded, persisted scientific semantics. This function has no
 * execution hooks, HTML fields, component names, or latest-version lookup.
 */
export function compileScientificPresentation(input: PresentationInput): ScientificPresentation {
  const interpretation = input.interpretation;
  const interpretationId = input.interpretationId || interpretation?.interpretationId;
  const evidence = input.evidence || [];
  const artifacts = input.artifacts || [];
  const blocks: ScientificPresentationBlock[] = [];
  const source = exactSource(input.sourceObjectRefs);

  const groundedClaims = (interpretation?.claims || []).filter((claim) => claim.groundingStatus === "GROUNDED" && claim.renderedText.trim());
  groundedClaims.slice(0, 8).forEach((claim, index) => {
    blocks.push({
      id: stableId("finding", claim.claimId || claim.renderedText, index),
      type: "finding",
      title: claim.claimType === "LIMITATION" ? "限制" : claim.claimType === "COMPARISON" ? "比较发现" : "科学发现",
      text: claim.renderedText,
      confidence: claim.confidenceClass,
      source: { ...source, resultId: input.resultId, interpretationId, evidenceId: claim.supportingEvidenceIds[0] || claim.subjectEvidenceIds[0] || null },
      evidenceIds: [...new Set([...claim.subjectEvidenceIds, ...claim.supportingEvidenceIds])].slice(0, 12),
    });
  });

  const narrative = groundedClaims[0]?.renderedText || input.validatedNarrative?.trim();
  if (narrative) blocks.unshift({ id: "narrative-grounded-summary", type: "narrative", title: "科学摘要", text: narrative, source: { ...source, resultId: input.resultId, interpretationId } });

  evidence.filter((item) => ["SCALAR", "COUNT", "RANGE", "CATEGORY", "BOOLEAN"].includes(item.evidenceKind)).slice(0, 12).forEach((item, index) => {
    blocks.push({
      id: stableId("metric", item.semanticRole || item.evidenceItemId, index),
      type: "metric",
      title: item.semanticRole.replaceAll("_", " "),
      value: item.displayValue,
      unit: item.unit,
      source: evidenceSource(item, input.resultId, interpretationId, input.sourceObjectRefs),
    });
  });

  selectedFactsFirst(input.facts || [], input.scientificSelections).slice(0, 12).forEach((fact, index) => {
    const value = displayFactValue(fact.value);
    if (value === null) return;
    blocks.push({
      id: stableId("fact-metric", fact.factId || fact.predicate, index),
      type: "metric",
      title: fact.predicate.replaceAll("_", " "),
      value,
      unit: fact.unit,
      source: factSource(fact, input.resultId, input.sourceObjectRefs),
    });
  });

  blocks.push(...projectedArtifactBlocks(artifacts, input.resultId, input.sourceObjectRefs));

  evidence.slice(0, 8).forEach((item, index) => {
    blocks.push({
      id: stableId("evidence", item.evidenceItemId, index),
      type: "evidence_reference",
      title: "证据",
      label: item.displayValue,
      source: evidenceSource(item, input.resultId, interpretationId, input.sourceObjectRefs),
    });
  });

  (interpretation?.globalLimitations || []).filter(Boolean).slice(0, 6).forEach((text, index) => {
    blocks.push({ id: stableId("limitation", text, index), type: "limitation", text, source: { ...source, resultId: input.resultId, interpretationId } });
  });
  (interpretation?.globalWarnings || []).filter(Boolean).slice(0, 6).forEach((text, index) => {
    blocks.push({ id: stableId("warning", text, index), type: "warning", text, source: { ...source, resultId: input.resultId, interpretationId } });
  });

  const viewerSource = input.sourceObjectRefs?.[0];
  if (viewerSource) {
    blocks.push({
      id: "viewer-exact-source",
      type: "viewer_reference",
      title: "精确科学视图",
      label: viewerSource.displayName || `${viewerSource.objectType || "ScientificObject"} · ${viewerSource.versionId}`,
      source: { ...source, resultId: input.resultId },
    });
  }

  return {
    schemaVersion: "1.0",
    blocks,
    exactSourceRefs: input.sourceObjectRefs || [],
    historicalNotice: input.relevance && input.relevance !== "CURRENT"
      ? input.relevance === "STALE"
        ? "本次呈现基于历史 source version；新版本存在时不会替换本记录。"
        : "本次呈现保留历史来源，但当前来源状态需要进一步检查。"
      : undefined,
  };
}

/**
 * Reports are immutable communication snapshots. Compile their bounded,
 * already-authoritative fields into the same presentation contract used by
 * Research so a report cannot silently acquire a second fact authority.
 */
export function compileReportPresentation(view: ScientificReportView): ScientificPresentation {
  const report = view.report;
  const interpretationId = view.scientific_interpretation_id || null;
  const sourceRefs = (view.viewer_sources || []).map((source) => ({
    objectId: source.object_id,
    versionId: source.version_id,
    objectType: source.object_type,
    displayName: source.display_name,
  }));
  const source = exactSource(sourceRefs);
  const blocks: ScientificPresentationBlock[] = [];
  if (report?.summary) {
    blocks.push({
      id: "report-summary",
      type: "narrative",
      title: "报告摘要",
      text: report.summary,
      source: { ...source, resultId: view.scientific_result_snapshot_id, interpretationId },
    });
  }
  (report?.main_findings || []).slice(0, 12).forEach((finding, index) => {
    blocks.push({
      id: stableId("report-finding", finding.statement, index),
      type: "finding",
      title: "报告发现",
      text: finding.statement,
      confidence: "QUALIFIED",
      source: {
        ...source,
        resultId: view.scientific_result_snapshot_id,
        interpretationId,
        factId: finding.fact_refs[0] || null,
      },
      evidenceIds: [...new Set([...finding.finding_refs, ...finding.fact_refs, ...finding.evidence_refs])].slice(0, 12),
    });
  });
  (report?.primary_figures || []).slice(0, 12).forEach((figure, index) => {
    const figureSource = (view.figure_sources || []).find((candidate) => candidate.figure_ref === figure.figure_ref);
    const artifactId = figureSource?.artifact_ids?.[0] || figure.figure_ref;
    blocks.push({
      id: stableId("report-figure", figure.figure_ref || figure.caption, index),
      type: "figure",
      title: figure.caption || figure.figure_ref,
      artifactId,
      source: {
        ...source,
        resultId: view.scientific_result_snapshot_id,
        interpretationId,
        artifactId,
        jobId: figureSource?.job_id || null,
      },
    });
  });
  (report?.evidence_refs || []).slice(0, 12).forEach((evidenceId, index) => {
    blocks.push({
      id: stableId("report-evidence", evidenceId, index),
      type: "evidence_reference",
      title: "报告证据",
      label: evidenceId,
      source: { ...source, resultId: view.scientific_result_snapshot_id, interpretationId, evidenceId },
    });
  });
  (report?.limitations || []).slice(0, 8).forEach((limitation, index) => {
    blocks.push({
      id: stableId("report-limitation", limitation.statement, index),
      type: "limitation",
      text: limitation.statement,
      source: { ...source, resultId: view.scientific_result_snapshot_id, interpretationId },
    });
  });
  sourceRefs.slice(0, 8).forEach((sourceRef, index) => {
    blocks.push({
      id: stableId("report-viewer", sourceRef.versionId, index),
      type: "viewer_reference",
      title: "历史 Viewer",
      label: sourceRef.displayName || `${sourceRef.objectType || "ScientificObject"} · ${sourceRef.versionId}`,
      source: { objectId: sourceRef.objectId, versionId: sourceRef.versionId, resultId: view.scientific_result_snapshot_id, interpretationId },
    });
  });
  return {
    schemaVersion: "1.0",
    blocks,
    exactSourceRefs: sourceRefs,
    historicalNotice: view.current_effective_relevance !== "CURRENT"
      ? "本报告保留生成时的精确来源；新版本不会静默替换历史报告。"
      : undefined,
  };
}

export function presentationBlockLabel(block: ScientificPresentationBlock): string {
  if (block.type === "metric") return `${block.value}${block.unit ? ` ${block.unit}` : ""}`;
  if (block.type === "evidence_reference" || block.type === "viewer_reference") return block.label;
  if (block.type === "figure" || block.type === "table") return block.title;
  if (block.type === "finding" || block.type === "narrative" || block.type === "limitation" || block.type === "warning") return block.text;
  return "";
}

export function isSafePresentationBlock(block: ScientificPresentationBlock): boolean {
  return !/[<>]|javascript:|data:text\/html/i.test(presentationBlockLabel(block));
}
