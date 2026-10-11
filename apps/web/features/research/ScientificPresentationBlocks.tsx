"use client";

import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import React, { useId, useMemo, useRef, useState } from "react";
import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import type { ScientificPresentation, ScientificPresentationBlock } from "../../app/lib/scientific-presentation";
import { formatPresentationMetricValue, isSafePresentationBlock, presentationLimitationText, presentationMetricUnit } from "../../app/lib/scientific-presentation";
import { scientificNarrativeText } from "../../app/lib/scientific-narrative-text";
import { getPlannerInterpretationEvidence, type Artifact, type InterpretationEvidenceResponse } from "../../app/lib/planner-api";
import { LazyScientificResultViewer } from "../../scientific-viewers/LazyScientificViewers";
import { ArtifactOpenLink } from "../../shared/ui/ArtifactOpenLink";
import { ArtifactDownloadLink } from "../../shared/ui/ArtifactDownloadLink";
import { groupXrdPeakMetrics, XrdPeakMetrics } from "./XrdPeakMetrics";
import { groupTableAnalysisMetrics } from "./table-analysis-metrics";
import { TableAnalysisMetrics } from "./TableAnalysisMetrics";
import { groupVolumetricMetrics, VolumetricMetrics } from "./VolumetricMetrics";
import { groupReferenceMetrics, ReferenceMetrics } from "./ReferenceMetrics";
import { ResearchResultVisuals } from "./ResearchResultVisuals";
import { ProjectInputDetails, projectInputOrigin } from "../../shared/ui/ProjectInputDetails";
import type { ResearchVisualTarget } from "./result-navigation";
import resultStyles from "./ResearchResultPresentation.module.css";

export function ScientificPresentationBlocks({
  presentation,
  mode = "full",
  projectId,
  instanceId,
  artifactCatalog = [],
  executionProcess,
  resultFacts = [],
  layout = "document",
  visualTarget,
  inputProvenance,
}: {
  presentation: ScientificPresentation;
  mode?: "full" | "report_supplement";
  projectId?: string;
  instanceId?: string;
  artifactCatalog?: readonly Artifact[];
  executionProcess?: React.ReactNode;
  resultFacts?: readonly Agent2ScientificFact[];
  layout?: "document" | "research";
  visualTarget?: ResearchVisualTarget;
  inputProvenance?: unknown;
}) {
  const generatedInstanceId = useId().replace(/:/gu, "");
  const [activeVisualId, setActiveVisualId] = useState<string | null>(null);
  const [activeEvidenceId, setActiveEvidenceId] = useState<string | null>(null);
  const [evidenceSectionOpen, setEvidenceSectionOpen] = useState(false);
  const blockedBlockCount = (presentation.blocks as unknown[]).filter((block) => !isSafePresentationBlock(block)).length;
  const blocks = presentation.blocks.filter(isSafePresentationBlock);
  const narrative = blocks.find((block): block is Extract<ScientificPresentationBlock, { type: "narrative" }> => block.type === "narrative");
  const allFindings = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "finding" }> => block.type === "finding");
  const metricBlocks = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "metric" }> => block.type === "metric");
  const xrdMetrics = groupXrdPeakMetrics(metricBlocks, resultFacts);
  const volumeMetrics = groupVolumetricMetrics(xrdMetrics.remaining, resultFacts);
  const tableMetrics = groupTableAnalysisMetrics(volumeMetrics.remaining, resultFacts);
  const referenceMetrics = groupReferenceMetrics(tableMetrics.remaining, resultFacts);
  const coordinationFactIds = new Set(resultFacts.filter(fact => /^structure\.(?:coordination[._]|local_environment\.)/u.test(fact.predicate)).map(fact => fact.fact_id));
  const coordinationMetrics = referenceMetrics.remaining.filter(metric => coordinationFactIds.has(metric.source.factId || ""));
  const metrics = referenceMetrics.remaining.filter(metric => !coordinationFactIds.has(metric.source.factId || ""));
  const visual = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "figure" | "table" | "viewer_reference" }> => block.type === "figure" || block.type === "table" || block.type === "viewer_reference");
  const evidence = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "evidence_reference" }> => block.type === "evidence_reference");
  const limitationBlocks = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "limitation" | "warning" }> => block.type === "limitation" || block.type === "warning");
  const limitations = [...new Set(limitationBlocks
    .map(block => presentationLimitationText(block.text).trim()).filter(Boolean))];
  const limitationFindings = new Map<string, typeof allFindings>();
  const findings = allFindings.filter((finding) => {
    if (layout !== "research" || !finding.source.resultId) return true;
    const matching = limitationBlocks.find((block) =>
      block.source.resultId === finding.source.resultId
      && block.source.interpretationId === finding.source.interpretationId
      && block.source.objectId === finding.source.objectId
      && block.source.versionId === finding.source.versionId
      && presentationLimitationText(block.text).trim() === finding.text.trim());
    if (!matching) return true;
    // Show an exact repeated qualification once, with its original citations.
    // Similar statements and qualifications from other sources stay separate.
    const text = presentationLimitationText(matching.text).trim();
    limitationFindings.set(text, [...(limitationFindings.get(text) || []), finding]);
    return false;
  });
  const instanceScope = safeDomIdPart(instanceId || generatedInstanceId || presentation.exactSourceRefs[0]?.versionId || "current");
  const headingId = `scientific-presentation-title-${instanceScope}`;
  const artifactHref = (block: Extract<ScientificPresentationBlock, { type: "figure" | "table" }>) =>
    block.source.jobId && block.source.artifactId
      ? `/api/planner/jobs/${encodeURIComponent(block.source.jobId)}/artifacts/${encodeURIComponent(block.source.artifactId)}/content`
      : null;
  const viewerHref = (source: ScientificPresentationBlock["source"]) =>
    projectId && source.objectId && source.versionId
      ? `/projects/${projectId}/data?object=${encodeURIComponent(source.objectId)}&version=${encodeURIComponent(source.versionId)}`
      : null;
  const activeVisual = visual.find(
    (block): block is Extract<ScientificPresentationBlock, { type: "figure" | "table" }> =>
      block.id === activeVisualId && (block.type === "figure" || block.type === "table"),
  );
  const activeArtifact = useMemo(
    () => activeVisual?.source.artifactId
      ? artifactCatalog.find((artifact) =>
        (artifact.artifactId || artifact.id) === activeVisual.source.artifactId)
      : undefined,
    [activeVisual, artifactCatalog],
  );
  const renderFindingReferences = (block: (typeof allFindings)[number]) => {
    const linkedEvidence = evidence.find((candidate) =>
      block.evidenceIds.includes(candidate.id)
      || (candidate.source.evidenceId ? block.evidenceIds.includes(candidate.source.evidenceId) : false),
    );
    const evidenceTargetId = linkedEvidence
      ? `scientific-evidence-${instanceScope}-${safeDomIdPart(linkedEvidence.id)}`
      : null;
    return <>
      {block.factIds !== undefined ? <FindingFacts key={`${block.source.resultId}:${block.id}:${block.factIds.join("|")}`} finding={block} metrics={metricBlocks} /> : block.evidenceIds.length ? <small>{block.evidenceIds.length} 项证据</small> : null}
      {block.factIds === undefined && linkedEvidence && evidenceTargetId ? <a
        className="product-link-button scientific-presentation-finding-evidence-link"
        href={`#${evidenceTargetId}`}
        aria-controls={evidenceTargetId}
        onClick={() => {
          setActiveEvidenceId(linkedEvidence.id);
          setEvidenceSectionOpen(true);
        }}
      >
        查看证据链
      </a> : null}
    </>;
  };
  // Only suppress a verbatim summary already present in this result's findings.
  // Whitespace normalization does not merge or reinterpret scientific statements.
  const compactText = (text: string) => text.replace(/\s+/gu, "");
  const redundantNarrative = layout === "research" && narrative && Boolean(compactText(narrative.text))
    && compactText(allFindings.filter((block) => block.source.resultId === narrative.source.resultId).map((block) => block.text).join(""))
      .includes(compactText(narrative.text));
  return <section className={`scientific-presentation ${layout === "research" ? resultStyles.research : ""}`} aria-labelledby={headingId}>
    <header className="scientific-presentation-header">
      <h3 id={headingId}>分析结果</h3>
      {projectInputOrigin(inputProvenance) ? <span>{projectInputOrigin(inputProvenance)}</span> : null}
      {presentation.exactSourceRefs.length ? <span>{presentation.exactSourceRefs.length} 个来源版本</span> : null}
    </header>
    {presentation.historicalNotice ? <aside className="scientific-presentation-notice" role="note">{presentation.historicalNotice}</aside> : null}
    {blockedBlockCount ? <aside className="scientific-presentation-notice" role="status">
      {blockedBlockCount} 个呈现块未通过安全校验，已保持隐藏；未执行任何未知组件或脚本。
    </aside> : null}
    {mode === "full" && narrative && !redundantNarrative ? <div className="scientific-presentation-narrative"><p>{narrative.text}</p></div> : null}
    {layout === "research" ? <ResearchResultVisuals blocks={visual} artifacts={artifactCatalog} projectId={projectId} instanceId={instanceScope} facts={resultFacts} target={visualTarget} /> : null}
    {mode === "full" && findings.length ? <section className="scientific-presentation-section"><h4>关键发现</h4><div className="scientific-presentation-findings">{findings.map((block) => (
      <article key={block.id}>
        {layout !== "research" || block.confidence !== "DIRECT" ? <span>{block.confidence === "DIRECT" ? "直接证据" : block.confidence === "QUALIFIED" ? "限定结论" : "有限结论"}</span> : null}
        <p>{block.text}</p>
        {renderFindingReferences(block)}
      </article>
    ))}</div></section> : null}
    {mode === "full" ? <VolumetricMetrics {...volumeMetrics} artifacts={artifactCatalog} /> : null}
    {mode === "full" ? <TableAnalysisMetrics groups={tableMetrics.groups} artifacts={artifactCatalog} sources={presentation.exactSourceRefs} /> : null}
    {mode === "full" ? <ReferenceMetrics groups={referenceMetrics.groups} /> : null}
    {mode === "full" ? <ProjectInputDetails provenance={inputProvenance} /> : null}
    {mode === "full" && coordinationMetrics.length ? <details className="scientific-presentation-section">
      <summary>配位数值 · {coordinationMetrics.length} 项</summary><MetricValues metrics={coordinationMetrics} />
    </details> : null}
    {mode === "full" && metrics.length && projectInputOrigin(inputProvenance) ? <details className="scientific-presentation-section">
      <summary>计算数值 · {metrics.length} 项</summary><MetricValues metrics={metrics} />
    </details> : mode === "full" && metrics.length ? <section className="scientific-presentation-section"><h4>指标</h4>
      <MetricValues metrics={metrics.slice(0, 12)} />
      {metrics.length > 12 ? <details key={metrics.map(block => `${block.source.resultId || ""}:${block.id}`).join("|")}>
        <summary>更多指标 · {metrics.length - 12} 项</summary>
        <MetricValues metrics={metrics.slice(12)} />
      </details> : null}
    </section> : null}
    {mode === "full" ? <XrdPeakMetrics rows={xrdMetrics.rows} /> : null}
    {layout !== "research" && visual.length ? <section className="scientific-presentation-section"><h4>图表与数据</h4><div className="scientific-presentation-links">{visual.map((block) => {
      const rawLabel = block.type === "viewer_reference" ? block.label : block.title;
      const label = rawLabel === "trajectory" ? "原子轨迹" : rawLabel;
      const href = block.type === "viewer_reference" ? viewerHref(block.source) : artifactHref(block);
      const canPreview = block.type !== "viewer_reference"
        && Boolean(block.source.jobId && block.source.artifactId)
        && artifactCatalog.some((artifact) => (artifact.artifactId || artifact.id) === block.source.artifactId);
      return <div key={block.id}>
        <div className="scientific-presentation-visual-heading"><span>{block.type === "figure" ? "图形" : block.type === "table" ? "表格" : "查看器"}</span><strong>{label}</strong></div>
        <div className="scientific-presentation-link-actions">
          {canPreview ? <button
            type="button"
            className="product-link-button"
            aria-pressed={activeVisualId === block.id}
            onClick={() => setActiveVisualId((current) => current === block.id ? null : block.id)}
          >
            {activeVisualId === block.id ? "收起科学视图" : "在页内查看"}
          </button> : null}
          {block.type === "viewer_reference" && href ? <Link href={href}>打开查看器</Link> : null}
          {block.type !== "viewer_reference" && href ? <>
            <ArtifactOpenLink href={href}>查看源文件</ArtifactOpenLink>
            <ArtifactDownloadLink href={href} downloadName={`${block.id}.${block.type === "figure" ? "figure" : "table"}.json`}>下载</ArtifactDownloadLink>
          </> : null}
        </div>
      </div>;
    })}</div>
    {activeVisual && activeArtifact && projectId && activeVisual.source.jobId ? <section
      className="scientific-presentation-inline-viewer"
      aria-label={`${activeVisual.type === "figure" ? "图形" : "表格"}：${activeVisual.title}`}
    >
      <header>
        <div>
          <h5>{activeVisual.title === "trajectory" ? "原子轨迹" : activeVisual.title}</h5>
        </div>
        <button type="button" className="product-secondary-action" onClick={() => setActiveVisualId(null)}>关闭预览</button>
      </header>
      <LazyScientificResultViewer
        projectId={projectId}
        jobId={activeVisual.source.jobId}
        selected={activeArtifact}
        artifacts={artifactCatalog}
        resultFacts={resultFacts}
      />
    </section> : null}
    </section> : null}
    {evidence.length || executionProcess ? <details
      className="scientific-presentation-evidence"
      open={evidenceSectionOpen}
      onToggle={(event) => setEvidenceSectionOpen(event.currentTarget.open)}
    >
      <summary>{executionProcess ? "工具调用过程" : `证据路径 · ${evidence.length} 项`}</summary>
      {executionProcess && evidenceSectionOpen ? executionProcess : null}
      {executionProcess ? <details open={Boolean(activeEvidenceId)}><summary>来源与证据 · {evidence.length} 项</summary><ul>{evidence.map((block) => {
        const artifact = artifactCatalog.find((item) => (item.artifactId || item.id) === block.source.artifactId);
        const href = artifact?.jobId && block.source.artifactId ? `/api/planner/jobs/${encodeURIComponent(artifact.jobId)}/artifacts/${encodeURIComponent(block.source.artifactId)}/content` : null;
        const sourceHref = viewerHref(block.source);
        return <li key={block.id} id={`scientific-evidence-${instanceScope}-${safeDomIdPart(block.id)}`} className="scientific-presentation-evidence-item"><strong>{artifact?.name || artifact?.type || "结果来源"}</strong>
          {href ? <ArtifactOpenLink href={href}>查看源文件</ArtifactOpenLink> : null}
          {sourceHref ? <Link href={sourceHref}>查看精确来源版本</Link> : null}
          <small>{block.source.evidenceId}</small>
        </li>;
      })}</ul></details> : <ul>{evidence.map((block) => <EvidenceReference
        key={block.id}
        block={block}
        viewerHref={viewerHref(block.source)}
        autoOpenToken={activeEvidenceId === block.id ? activeEvidenceId : null}
        instanceScope={instanceScope}
      />)}</ul>}
    </details> : null}
    {mode === "full" && limitations.length ? <section className="scientific-presentation-section scientific-presentation-limitations"><h4>限制与警告</h4><ul>{limitations.map(text => <li key={text}>
      {text}
      {limitationFindings.get(text)?.map(block => <div key={`${block.source.resultId}:${block.id}`} className={resultStyles.limitationSupport}>
        {block.confidence !== "DIRECT" ? <span>{block.confidence === "QUALIFIED" ? "限定结论" : "有限结论"}</span> : null}
        {renderFindingReferences(block)}
      </div>)}
    </li>)}</ul></section> : null}
  </section>;
}

/** Reuse the exact evidence inspector without duplicating report figures or source lists. */
export function ScientificEvidenceReferences({ references, instanceId }: {
  references: readonly Extract<ScientificPresentationBlock, { type: "evidence_reference" }>[];
  instanceId: string;
}) {
  return <ul>{references.map((block) => <EvidenceReference
    key={block.id} block={block} viewerHref={null} instanceScope={safeDomIdPart(instanceId)}
  />)}</ul>;
}

function EvidenceReference({
  block,
  viewerHref,
  autoOpenToken = null,
  instanceScope,
}: {
  block: Extract<ScientificPresentationBlock, { type: "evidence_reference" }>;
  viewerHref: string | null;
  autoOpenToken?: string | null;
  instanceScope: string;
}) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [detail, setDetail] = useState<InterpretationEvidenceResponse | null>(null);
  const triggerRef = useRef<HTMLButtonElement | null>(null);
  const inspectorRef = useRef<HTMLDivElement | null>(null);
  const hasInteracted = useRef(false);
  const evidenceId = block.source.evidenceId || "";
  const interpretationId = block.source.interpretationId || "";
  const evidenceItemId = `scientific-evidence-${instanceScope}-${safeDomIdPart(block.id)}`;
  const evidenceInspectorId = `scientific-evidence-inspector-${instanceScope}-${safeDomIdPart(block.id)}`;
  async function inspect() {
    if (!interpretationId || !evidenceId || loading) {
      setOpen((value) => !value);
      return;
    }
    if (detail) {
      setOpen((value) => !value);
      return;
    }
    setLoading(true);
    setError("");
    try {
      const next = await getPlannerInterpretationEvidence(interpretationId);
      setDetail(next);
      setOpen(true);
    } catch {
      setError("证据链暂时无法读取；科学结果仍保持只读。");
      setOpen(true);
    } finally {
      setLoading(false);
    }
  }
  React.useEffect(() => {
    if (autoOpenToken) void inspect();
  }, [autoOpenToken]);
  React.useEffect(() => {
    if (!hasInteracted.current) return;
    if (open) {
      inspectorRef.current?.focus();
    } else {
      triggerRef.current?.focus();
    }
  }, [open]);
  const item = detail?.evidenceItems.find((candidate) => candidate.evidenceItemId === evidenceId);
  const artifact = detail?.artifacts?.find((candidate) => (candidate.artifactId || candidate.id) === (item?.sourceArtifactId || block.source.artifactId));
  const tool = detail?.toolCalls?.find((candidate) =>
    candidate.toolId === item?.sourceToolId
    || (candidate.id || candidate.toolCallId) === (item?.sourceToolId || block.source.toolCallId),
  );
  return <li id={evidenceItemId} className="scientific-presentation-evidence-item">
    <strong>{block.label}</strong>
    <small>已绑定科学结果与证据</small>
    <div className="scientific-presentation-evidence-actions">
      <button
        ref={triggerRef}
        type="button"
        className="product-link-button"
        onClick={() => {
          hasInteracted.current = true;
          void inspect();
        }}
        disabled={loading}
        aria-expanded={open}
        aria-controls={evidenceInspectorId}
      >
        {loading ? "正在读取证据…" : open ? "收起证据链" : "检查证据链"}
      </button>
      {!detail && block.source.artifactId && block.source.jobId ? <ArtifactOpenLink href={`/api/planner/jobs/${encodeURIComponent(block.source.jobId)}/artifacts/${encodeURIComponent(block.source.artifactId)}/content`}>打开 Artifact</ArtifactOpenLink> : null}
      {!detail && block.source.artifactId && block.source.jobId ? <ArtifactDownloadLink href={`/api/planner/jobs/${encodeURIComponent(block.source.jobId)}/artifacts/${encodeURIComponent(block.source.artifactId)}/content`} downloadName={`${block.id}.artifact`}>下载 Artifact</ArtifactDownloadLink> : null}
      {!detail && !block.source.artifactId && viewerHref ? <Link href={viewerHref}>查看精确来源</Link> : null}
    </div>
    {open ? <div
      ref={inspectorRef}
      id={evidenceInspectorId}
      className="scientific-presentation-evidence-inspector"
      role="region"
      tabIndex={-1}
      aria-label={`证据链 ${evidenceId || block.label}`}
    >
      {error ? <p role="alert">{error}</p> : detail ? <>
        <dl>
          <div><dt>来源对象</dt><dd>{detail.sourceObjectRefs?.length ? detail.sourceObjectRefs.map((source) => `${source.displayName || source.objectType || "ScientificObject"} · ${source.versionId}`).join("；") : "未返回 exact source"}</dd></div>
          <div><dt>Artifact</dt><dd>{artifact ? `${artifact.artifactId || artifact.id || "—"}${artifact.contentHash || artifact.sha256 ? ` · ${artifact.contentHash || artifact.sha256}` : ""}` : "未返回 Artifact"}</dd></div>
          <div><dt>ToolCall</dt><dd>{tool ? `${tool.toolId || tool.id || tool.toolCallId || "—"} · ${tool.status || "unknown"}` : "未返回 ToolCall"}</dd></div>
          <div><dt>字段</dt><dd>{item?.fieldLocator?.fieldId || "—"} · {item?.displayValue || block.label}{item?.unit ? ` ${item.unit}` : ""}</dd></div>
        </dl>
        {artifact && (artifact.artifactId || artifact.id) && (artifact.jobId || detail.jobId) ? <>
          <ArtifactOpenLink href={`/api/planner/jobs/${encodeURIComponent(artifact.jobId || detail.jobId || "")}/artifacts/${encodeURIComponent(artifact.artifactId || artifact.id || "")}/content`}>打开权威 Artifact</ArtifactOpenLink>
          <ArtifactDownloadLink href={`/api/planner/jobs/${encodeURIComponent(artifact.jobId || detail.jobId || "")}/artifacts/${encodeURIComponent(artifact.artifactId || artifact.id || "")}/content`} downloadName={`${artifact.artifactId || artifact.id}.artifact`}>下载权威 Artifact</ArtifactDownloadLink>
        </> : null}
      </> : <p>此呈现块没有可用的 interpretation evidence identity。</p>}
    </div> : null}
    {block.source.versionId ? <small>{block.source.versionNo ? `来源版本 ${block.source.versionNo}` : "已锁定精确来源版本"}</small> : null}
  </li>;
}

function safeDomIdPart(value: string): string {
  return value.replace(/[^a-zA-Z0-9_-]/gu, "-") || "instance";
}

/** Fact references and shared tool/artifact provenance are different kinds of support. */
function FindingFacts({ finding, metrics }: {
  finding: Extract<ScientificPresentationBlock, { type: "finding" }>;
  metrics: Extract<ScientificPresentationBlock, { type: "metric" }>[];
}) {
  const references = [...new Set(finding.factIds || [])];
  if (!references.length) return null;
  const cited = references.flatMap((factId) => {
    const matches = metrics.filter(metric => finding.source.resultId
      && metric.source.resultId === finding.source.resultId && metric.source.factId === factId);
    return matches.length === 1 ? matches : [];
  });
  return <details className="scientific-finding-facts">
    <summary>查看引用事实 · {references.length} 项</summary>
    <dl>{cited.map(metric => <div key={metric.id}>
      <dt>{metric.title}</dt>
      <dd data-exact-value={metric.value}>{metric.value}{metric.unit ? ` ${metric.unit}` : ""}</dd>
    </div>)}</dl>
    {cited.length !== references.length ? <p role="status">{references.length - cited.length} 项引用事实暂未提供可展示的数值，可通过来源文件核对。</p> : null}
  </details>;
}

function MetricValues({ metrics }: { metrics: Extract<ScientificPresentationBlock, { type: "metric" }>[] }) {
  return <div className="scientific-presentation-metrics">{metrics.map((block) => {
      const displayValue = scientificNarrativeText(formatPresentationMetricValue(block.value));
      const unit = block.unit ? presentationMetricUnit(block.unit) : "";
      const formatted = displayValue !== block.value;
      return <div key={block.id}>
        <span>{block.title}</span>
        <strong
          title={formatted ? `精确值：${block.value}` : undefined}
          data-exact-value={block.value}
        >
          {displayValue}
        </strong>
        {unit ? <small>{unit}</small> : null}
        {formatted ? <span className="sr-only">精确值 {block.value}</span> : null}
      </div>;
  })}</div>;
}
