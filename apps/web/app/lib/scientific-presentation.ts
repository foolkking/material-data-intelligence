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
  versionNo?: number | null;
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

export type PersistedScientificFinding = {
  finding_id: string;
  statement: string;
  importance: "HIGH" | "MEDIUM" | "LOW";
  confidence: "HIGH" | "MEDIUM" | "LIMITED";
  fact_refs: string[];
  evidence_refs: string[];
  result_item_refs: string[];
};

export type PersistedScientificInterpretation = {
  contract_version: "1.0";
  title: string;
  answer_lead: string;
  primary_findings: PersistedScientificFinding[];
  supporting_findings: PersistedScientificFinding[];
  limitations: string[];
  primary_result_refs: string[];
  supporting_result_refs: string[];
  follow_up_suggestions: string[];
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
  exactSourceRefs: Array<{ objectId: string; versionId: string; versionNo?: number | null; objectType?: string; displayName?: string }>;
  historicalNotice?: string;
};

export type PresentationInput = {
  interpretation?: GroundedScientificInterpretation | null;
  /**
   * The current Agent2 interpreter persists this bounded scientific
   * communication contract. It is distinct from the legacy planner
   * GroundedScientificInterpretation contract and must not be cast into it.
   */
  persistedInterpretation?: PersistedScientificInterpretation | null;
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
  sourceObjectRefs?: Array<{ objectId: string; versionId: string; versionNo?: number | null; objectType?: string; displayName?: string }>;
  artifactSourceRefs?: Record<string, Array<{ objectId: string; versionId: string; versionNo?: number | null; objectType?: string; displayName?: string }>>;
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
  return source ? { objectId: source.objectId, versionId: source.versionId, versionNo: source.versionNo } : {};
}

function evidenceSource(item: ScientificEvidenceItem, resultId: string | null | undefined, interpretationId: string | null | undefined, sourceObjectRefs: PresentationInput["sourceObjectRefs"]): PresentationSource {
  return { ...exactSource(sourceObjectRefs), resultId, interpretationId, evidenceId: item.evidenceItemId, artifactId: item.sourceArtifactId, toolCallId: item.sourceToolId };
}

function displayFactValue(value: unknown): string | null {
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
  return null;
}

const NUMERIC_PRESENTATION_VALUE = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/iu;

/**
 * Keep the persisted value untouched in the presentation contract while
 * providing a bounded, readable scientific display value. The exact source
 * value remains available to the renderer and evidence inspector.
 */
export function formatPresentationMetricValue(value: string): string {
  const normalized = value.trim();
  if (!NUMERIC_PRESENTATION_VALUE.test(normalized)) return value;
  const numeric = Number(normalized);
  if (!Number.isFinite(numeric)) return value;
  if (Object.is(numeric, -0) || numeric === 0) return "0";
  const magnitude = Math.abs(numeric);
  if (magnitude >= 1_000_000 || magnitude < 0.0001) {
    return numeric.toExponential(4).replace(/\.?0+e/iu, "e");
  }
  return numeric.toLocaleString("zh-CN", {
    maximumSignificantDigits: 7,
    useGrouping: magnitude >= 10_000,
  });
}

/**
 * Format numeric tokens in a persisted scientific narrative for display only.
 * The persisted message/result remains untouched; authoritative exact values
 * continue to be available from the Result and evidence inspector.
 */
export function formatScientificNarrativeNumbers(text: string): string {
  return text.replace(
    /(^|[^A-Za-z0-9_-])([-+]?(?:\d+\.\d+|\d+e[-+]?\d+|\d+\.\d+e[-+]?\d+))(?=$|[^A-Za-z0-9_-])/giu,
    (_match, prefix: string, token: string) => `${prefix}${formatPresentationMetricValue(token)}`,
  );
}

function persistedFindingConfidence(
  confidence: PersistedScientificFinding["confidence"],
): Extract<ScientificPresentationBlock, { type: "finding" }>["confidence"] {
  if (confidence === "HIGH") return "DIRECT";
  if (confidence === "MEDIUM") return "QUALIFIED";
  return "LIMITED";
}

const PRESENTATION_LIMITATION_TRANSLATIONS: Readonly<Record<string, string>> = {
  "The result projector does not infer peaks or coordination shells from the RDF curve.": "结果投影不会从 RDF 曲线中推断峰位或配位壳层。",
  "MSD series values remain referenced structured data and are not expanded into scalar facts.": "MSD 序列保留为可追溯的结构化数据，不会被展开或改写为额外标量事实。",
  "The current band Artifact does not provide eigenvectors or animation authority.": "当前声子能带 Artifact 不包含特征向量，因此不提供模式动画依据。",
  "The current DOS Artifact does not provide eigenvectors or animation authority.": "当前声子态密度 Artifact 不包含特征向量，因此不提供模式动画依据。",
  "The combined Artifact is a static band/DOS result and does not provide eigenvectors or animation authority.": "当前组合 Artifact 是静态声子能带/DOS 结果，不包含特征向量或动画依据。",
  "The result references the validated coordination Artifact and does not recompute neighbors.": "该结果引用已验证的配位 Artifact；呈现时不会重新计算近邻。",
  "RDF series remain bounded structured evidence; the projector does not detect peaks.": "RDF 序列保留为有界结构化证据；结果投影不会自行识别峰位。",
  "Band values are supplied electronic data; no DFT/GW calculation or interpolation is executed.": "能带数值来自已提供的权威电子结构数据；本次呈现不会执行 DFT/GW 计算或插值。",
  "Band energies and gap facts are derived only from the supplied sampled electronic data; the platform performs no DFT, GW correction, interpolation or projected-band analysis.": "能带能量与带隙事实仅来自已提供的采样电子数据；平台未执行 DFT、GW 修正、插值或投影能带分析。",
  "DOS values are supplied electronic data; no new electronic calculation is executed.": "DOS 数值来自已提供的权威电子结构数据；本次呈现不会执行新的电子结构计算。",
  "DOS values are supplied data. Partial or unknown projection coverage describes only provided channels; no total, electron count, bonding, magnetism or band character is inferred.": "DOS 数值来自已提供的数据。PARTIAL 或未知投影覆盖仅描述现有通道；不会据此推断总态密度、电子数、成键、磁性或能带性质。",
  "Composition-space projection is descriptive and does not establish material identity or causality.": "组成空间投影仅用于描述数据分布，不据此确立材料身份或因果关系。",
  "Only the bounded, profile-authorized dataset projection is included.": "当前结果仅包含通过语义 Profile 授权的有界 Dataset 投影。",
  "Diffusion is estimated only over the explicitly selected fit window and is not an unconditional long-time bulk diffusion coefficient.": "扩散系数仅在明确选择的拟合时间窗内估算，不代表无条件的长时间体相扩散系数。",
  "MSD uses Cartesian x/y/z axes and is not automatically crystallographic a/b/c diffusion.": "MSD 使用笛卡尔 x/y/z 轴，不会自动解释为晶体学 a/b/c 方向扩散。",
  "No center-of-mass drift correction is applied.": "本次结果未应用质心漂移校正。",
};

export function presentationLimitationText(text: string): string {
  return PRESENTATION_LIMITATION_TRANSLATIONS[text] || text;
}

const PRESENTATION_METRIC_LABELS: Readonly<Record<string, string>> = {
  "electronic.band_gap": "电子带隙（供应数据）",
  "electronic.kpoint_count": "k 点数",
  "electronic.energy_point_count": "DOS 能量点数",
  "ml.sample_count": "评估样本数",
  "ml.mae": "平均绝对误差（MAE）",
  "ml.rmse": "均方根误差（RMSE）",
  "ml.r2": "决定系数（R²）",
  "ml.mean_signed_error": "平均符号误差",
  "ml.median_absolute_error": "中位绝对误差",
  "ml.high_error_sample_id": "最大误差样本",
  "ml.high_error_formula": "最大误差样本化学式",
  "ml.high_error_target": "最大误差样本真实值",
  "ml.high_error_prediction": "最大误差样本预测值",
  "ml.high_error_residual": "最大误差样本残差",
  "ml.high_error_absolute_error": "最大绝对误差",
};

export function presentationMetricTitle(predicate: string): string {
  return PRESENTATION_METRIC_LABELS[predicate] || predicate.replaceAll("_", " ");
}

export function presentationScientificText(text: string): string {
  const normalized = text
    .replace(
      /该事实来自证据\s*(?:\b(?:fact|evidence|limitation|figure)\.[a-z0-9.]+\b)(?:\s*（step_[^)]+）)?/giu,
      "该数值已绑定本次分析证据",
    )
    .replace(
      /(?:来自|来源于)\s*(?:证据\s*)?(?:\b(?:fact|evidence|limitation|figure)\.[a-z0-9.]+\b)(?:\s*（step_[^)]+）)?/giu,
      "已绑定本次分析证据",
    )
    .replace(/\b(?:fact|evidence|limitation|figure)\.[a-z0-9.]+/giu, "")
    .replace(/（step_[^)]+）/giu, "")
    .replace(/（\s*）/gu, "")
    .replace(/该事实来自证据\s*(?:（[^）]*）)?。/gu, "该数值已绑定本次分析证据。")
    .replace(/由证据\s*支持/gu, "由已提交证据支持")
    .replace(/但\s*明确说明：/gu, "同时，权威限制说明：")
    .replace(/[ \t]{2,}/gu, " ")
    .replace(/\s+([，。；：！？])/gu, "$1")
    .trim();
  const sentences = normalized.match(/[^。！？!?]*[。！？!?]|[^。！？!?]+$/gu);
  if (!sentences) return normalized;
  return formatScientificNarrativeNumbers(sentences
    .map((sentence) => sentence.trim())
    .filter((sentence, index, items) => index === 0 || sentence !== items[index - 1])
    .join("")
    .trim());
}

function presentationSummary(
  persistedInterpretation: PersistedScientificInterpretation | null | undefined,
  fallback: string | null | undefined,
): string {
  const primary = (persistedInterpretation?.primary_findings || [])
    .map((finding) => presentationScientificText(finding.statement))
    .map((statement) => statement.match(/^[^。！？!?]*[。！？!?]/u)?.[0]?.trim() || statement)
    .filter(Boolean)
    .slice(0, 2);
  return primary.length
    ? primary.join("")
    : fallback
      ? presentationScientificText(fallback)
      : "";
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

function projectedArtifactBlocks(
  artifacts: Artifact[],
  resultId: string | null | undefined,
  sourceObjectRefs: PresentationInput["sourceObjectRefs"],
  artifactSourceRefs: PresentationInput["artifactSourceRefs"],
): ScientificPresentationBlock[] {
  return projectScientificArtifacts(artifacts).slice(0, 12).map((artifact, index) => {
    const id = artifactId(artifact);
    const title = artifact.resultTitle;
    const itemSources = artifactSourceRefs?.[id] || [];
    const exactArtifactSource =
      itemSources.length === 1
        ? exactSource(itemSources)
        : sourceObjectRefs?.length === 1
          ? exactSource(sourceObjectRefs)
          : {};
    const source = { ...exactArtifactSource, resultId, artifactId: id, jobId: artifact.jobId };
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
  const persistedInterpretation = input.persistedInterpretation;
  const interpretationId = input.interpretationId || interpretation?.interpretationId;
  const evidence = input.evidence || [];
  const artifacts = input.artifacts || [];
  const blocks: ScientificPresentationBlock[] = [];
  const source = exactSource(input.sourceObjectRefs);

  const persistedFindings = [
    ...(persistedInterpretation?.primary_findings || []).map((finding) => ({ finding, primary: true })),
    ...(persistedInterpretation?.supporting_findings || []).map((finding) => ({ finding, primary: false })),
  ].filter(({ finding }) => finding.statement.trim());
  if (persistedFindings.length) {
    persistedFindings.slice(0, 12).forEach(({ finding, primary }, index) => {
      blocks.push({
        id: stableId("finding", finding.finding_id || finding.statement, index),
        type: "finding",
        title: primary ? "主要发现" : "支持发现",
        text: presentationScientificText(finding.statement),
        confidence: persistedFindingConfidence(finding.confidence),
        source: {
          ...source,
          resultId: input.resultId,
          interpretationId,
          factId: finding.fact_refs[0] || null,
          evidenceId: finding.evidence_refs[0] || null,
        },
        evidenceIds: [...new Set([...finding.fact_refs, ...finding.evidence_refs])].slice(0, 12),
      });
    });
  } else {
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
  }

  const groundedClaims = (interpretation?.claims || []).filter((claim) => claim.groundingStatus === "GROUNDED" && claim.renderedText.trim());
  const narrativeSource = persistedInterpretation?.answer_lead?.trim() || groundedClaims[0]?.renderedText || input.validatedNarrative?.trim();
  const narrative = presentationSummary(persistedInterpretation, narrativeSource);
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
      title: presentationMetricTitle(fact.predicate),
      value,
      unit: fact.unit,
      source: factSource(fact, input.resultId, input.sourceObjectRefs),
    });
  });

  blocks.push(
    ...projectedArtifactBlocks(
      artifacts,
      input.resultId,
      input.sourceObjectRefs,
      input.artifactSourceRefs,
    ),
  );

  evidence.slice(0, 8).forEach((item, index) => {
    blocks.push({
      id: stableId("evidence", item.evidenceItemId, index),
      type: "evidence_reference",
      title: "证据",
      label: item.displayValue,
      source: evidenceSource(item, input.resultId, interpretationId, input.sourceObjectRefs),
    });
  });

  const presentationLimitations = persistedInterpretation?.limitations || interpretation?.globalLimitations || [];
  presentationLimitations.filter(Boolean).slice(0, 8).forEach((text, index) => {
    blocks.push({ id: stableId("limitation", text, index), type: "limitation", text, source: { ...source, resultId: input.resultId, interpretationId } });
  });
  (interpretation?.globalWarnings || []).filter(Boolean).slice(0, 6).forEach((text, index) => {
    blocks.push({ id: stableId("warning", text, index), type: "warning", text, source: { ...source, resultId: input.resultId, interpretationId } });
  });

  const viewerSources = [...new Map(
    (input.sourceObjectRefs || []).map((item) => [
      `${item.objectId}:${item.versionId}`,
      item,
    ]),
  ).values()].slice(0, 8);
  viewerSources.forEach((viewerSource, index) => {
    blocks.push({
      id: stableId(
        "viewer-exact-source",
        `${viewerSource.objectId}-${viewerSource.versionId}`,
        index,
      ),
      type: "viewer_reference",
      title: "精确科学视图",
      label: viewerSource.displayName
        || `${viewerSource.objectType || "ScientificObject"} · ${viewerSource.versionNo ? `版本 ${viewerSource.versionNo}` : "精确版本"}`,
      source: {
        objectId: viewerSource.objectId,
        versionId: viewerSource.versionId,
        versionNo: viewerSource.versionNo,
        resultId: input.resultId,
      },
    });
  });

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
      text: presentationScientificText(report.summary),
      source: { ...source, resultId: view.scientific_result_snapshot_id, interpretationId },
    });
  }
  for (const section of [
    ["科学讨论", report?.discussion],
    ["结论", report?.conclusion],
    ["后续工作建议", report?.next_steps],
  ] as const) {
    const [title, value] = section;
    if (!value?.text) continue;
    blocks.push({
      id: stableId("report-narrative", title, blocks.length),
      type: "narrative",
      title,
      text: presentationScientificText(value.text),
      source: { ...source, resultId: view.scientific_result_snapshot_id, interpretationId, factId: value.fact_refs[0] || null, evidenceId: value.evidence_refs[0] || null },
    });
  }
  (report?.main_findings || []).slice(0, 12).forEach((finding, index) => {
    blocks.push({
      id: stableId("report-finding", finding.statement, index),
      type: "finding",
      title: "报告发现",
      text: presentationScientificText(finding.statement),
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
    const figureExactSource = figureSource?.object_id && figureSource.version_id
      ? {
          objectId: figureSource.object_id,
          versionId: figureSource.version_id,
          objectType: figureSource.object_type || null,
          displayName: sourceRefs.find((candidate) => candidate.objectId === figureSource.object_id)?.displayName || null,
        }
      : source;
    blocks.push({
      id: stableId("report-figure", figure.figure_ref || figure.caption, index),
      type: "figure",
      title: figure.caption || figure.figure_ref,
      artifactId,
      source: {
        ...figureExactSource,
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
      label: sourceRef.displayName || `${sourceRef.objectType || "ScientificObject"} · 精确版本`,
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

const PRESENTATION_BLOCK_TYPES = new Set([
  "narrative",
  "finding",
  "metric",
  "table",
  "figure",
  "viewer_reference",
  "evidence_reference",
  "limitation",
  "warning",
]);

const PRESENTATION_SOURCE_KEYS = new Set([
  "resultId",
  "interpretationId",
  "factId",
  "evidenceId",
  "artifactId",
  "jobId",
  "toolCallId",
  "objectId",
  "versionId",
  "versionNo",
]);

const PRESENTATION_BLOCK_KEYS: Readonly<Record<string, ReadonlySet<string>>> = {
  narrative: new Set(["id", "type", "title", "text", "source"]),
  finding: new Set(["id", "type", "title", "text", "confidence", "source", "evidenceIds"]),
  metric: new Set(["id", "type", "title", "value", "unit", "source"]),
  table: new Set(["id", "type", "title", "artifactId", "source"]),
  figure: new Set(["id", "type", "title", "artifactId", "source"]),
  viewer_reference: new Set(["id", "type", "title", "label", "source"]),
  evidence_reference: new Set(["id", "type", "title", "label", "source"]),
  limitation: new Set(["id", "type", "text", "source"]),
  warning: new Set(["id", "type", "text", "source"]),
};

const EXECUTABLE_PRESENTATION_TEXT = /[<>]|javascript:|vbscript:|data:text\/html/iu;
const REMOTE_OR_EXECUTABLE_REFERENCE = /[<>]|(?:javascript|vbscript|data:text\/html):|https?:\/\/|^\/\//iu;

function isPlainRecord(value: unknown): value is Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function hasOnlyKeys(value: Record<string, unknown>, allowed: ReadonlySet<string>): boolean {
  return Object.keys(value).every((key) => allowed.has(key));
}

function isSafeDisplayText(value: unknown, optional = false): value is string | undefined {
  if (optional && value === undefined) return true;
  return typeof value === "string"
    && value.length <= 16_000
    && !EXECUTABLE_PRESENTATION_TEXT.test(value);
}

function isSafeReference(value: unknown, optional = false): value is string | null | undefined {
  if (optional && (value === undefined || value === null)) return true;
  return typeof value === "string"
    && value.length > 0
    && value.length <= 256
    && !REMOTE_OR_EXECUTABLE_REFERENCE.test(value);
}

function isSafePresentationSource(value: unknown): value is PresentationSource {
  if (!isPlainRecord(value) || !hasOnlyKeys(value, PRESENTATION_SOURCE_KEYS)) return false;
  return Object.entries(value).every(([key, item]) =>
    key === "versionNo"
      ? item === undefined
        || item === null
        || (Number.isSafeInteger(item) && Number(item) > 0)
      : isSafeReference(item, true),
  );
}

export function isSafePresentationBlock(block: unknown): block is ScientificPresentationBlock {
  if (!isPlainRecord(block)) return false;
  const candidate = block as Record<string, unknown>;
  if (typeof candidate.type !== "string" || !PRESENTATION_BLOCK_TYPES.has(candidate.type)) return false;
  const allowedKeys = PRESENTATION_BLOCK_KEYS[candidate.type];
  if (!allowedKeys || !hasOnlyKeys(candidate, allowedKeys)) return false;
  if (!isSafeReference(candidate.id) || !isSafePresentationSource(candidate.source)) return false;

  if (candidate.type === "narrative") {
    return isSafeDisplayText(candidate.title, true) && isSafeDisplayText(candidate.text);
  }
  if (candidate.type === "finding") {
    return isSafeDisplayText(candidate.title)
      && isSafeDisplayText(candidate.text)
      && ["DIRECT", "QUALIFIED", "LIMITED"].includes(String(candidate.confidence))
      && Array.isArray(candidate.evidenceIds)
      && candidate.evidenceIds.length <= 12
      && candidate.evidenceIds.every((item) => isSafeReference(item));
  }
  if (candidate.type === "metric") {
    return isSafeDisplayText(candidate.title)
      && isSafeDisplayText(candidate.value)
      && (candidate.unit === null || isSafeDisplayText(candidate.unit, true));
  }
  if (candidate.type === "table" || candidate.type === "figure") {
    return isSafeDisplayText(candidate.title) && isSafeReference(candidate.artifactId);
  }
  if (candidate.type === "viewer_reference" || candidate.type === "evidence_reference") {
    return isSafeDisplayText(candidate.title) && isSafeDisplayText(candidate.label);
  }
  return isSafeDisplayText(candidate.text);
}
