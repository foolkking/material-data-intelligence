"use client";

import React, { useId, useMemo, useRef, useState } from "react";
import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import type { ScientificPresentation, ScientificPresentationBlock } from "../../app/lib/scientific-presentation";
import { formatPresentationMetricValue, isSafePresentationBlock, presentationLimitationText } from "../../app/lib/scientific-presentation";
import { getPlannerInterpretationEvidence, type Artifact, type InterpretationEvidenceResponse } from "../../app/lib/planner-api";
import { LazyScientificResultViewer } from "../../scientific-viewers/LazyScientificViewers";
import { ArtifactOpenLink } from "../../shared/ui/ArtifactOpenLink";
import { ArtifactDownloadLink } from "../../shared/ui/ArtifactDownloadLink";

export function ScientificPresentationBlocks({
  presentation,
  mode = "full",
  projectId,
  instanceId,
  artifactCatalog = [],
}: {
  presentation: ScientificPresentation;
  mode?: "full" | "report_supplement";
  projectId?: string;
  instanceId?: string;
  artifactCatalog?: readonly Artifact[];
}) {
  const generatedInstanceId = useId().replace(/:/gu, "");
  const [activeVisualId, setActiveVisualId] = useState<string | null>(null);
  const [activeEvidenceId, setActiveEvidenceId] = useState<string | null>(null);
  const [evidenceSectionOpen, setEvidenceSectionOpen] = useState(false);
  const blockedBlockCount = (presentation.blocks as unknown[]).filter((block) => !isSafePresentationBlock(block)).length;
  const blocks = presentation.blocks.filter(isSafePresentationBlock);
  const narrative = blocks.find((block): block is Extract<ScientificPresentationBlock, { type: "narrative" }> => block.type === "narrative");
  const findings = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "finding" }> => block.type === "finding");
  const metrics = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "metric" }> => block.type === "metric");
  const visual = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "figure" | "table" | "viewer_reference" }> => block.type === "figure" || block.type === "table" || block.type === "viewer_reference");
  const evidence = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "evidence_reference" }> => block.type === "evidence_reference");
  const limitations = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "limitation" | "warning" }> => block.type === "limitation" || block.type === "warning");
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
  return <section className="scientific-presentation" aria-labelledby={headingId}>
    <header className="scientific-presentation-header">
      <div><p className="product-kicker">科学呈现 · 1.0</p><h3 id={headingId}>科学呈现</h3></div>
      {presentation.exactSourceRefs.length ? <span>绑定 {presentation.exactSourceRefs.length} 个精确源版本</span> : null}
    </header>
    {presentation.historicalNotice ? <aside className="scientific-presentation-notice" role="note">{presentation.historicalNotice}</aside> : null}
    {blockedBlockCount ? <aside className="scientific-presentation-notice" role="status">
      {blockedBlockCount} 个呈现块未通过安全校验，已保持隐藏；未执行任何未知组件或脚本。
    </aside> : null}
    {mode === "full" && narrative ? <div className="scientific-presentation-narrative"><p>{narrative.text}</p></div> : null}
    {mode === "full" && findings.length ? <section className="scientific-presentation-section"><h4>关键发现</h4><div className="scientific-presentation-findings">{findings.map((block) => {
      const linkedEvidence = evidence.find((candidate) =>
        block.evidenceIds.includes(candidate.id)
        || (candidate.source.evidenceId ? block.evidenceIds.includes(candidate.source.evidenceId) : false),
      );
      const evidenceTargetId = linkedEvidence
        ? `scientific-evidence-${instanceScope}-${safeDomIdPart(linkedEvidence.id)}`
        : null;
      return <article key={block.id}>
        <span>{block.confidence === "DIRECT" ? "直接证据" : block.confidence === "QUALIFIED" ? "限定结论" : "有限结论"}</span>
        <p>{block.text}</p>
        <small>{block.evidenceIds.length ? `${block.evidenceIds.length} 项证据绑定` : "已绑定 Result"}</small>
        {linkedEvidence && evidenceTargetId ? <a
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
      </article>;
    })}</div></section> : null}
    {mode === "full" && metrics.length ? <section className="scientific-presentation-section"><h4>权威指标</h4><div className="scientific-presentation-metrics">{metrics.map((block) => {
      const displayValue = formatPresentationMetricValue(block.value);
      const formatted = displayValue !== block.value;
      return <div key={block.id}>
        <span>{block.title}</span>
        <strong
          title={formatted ? `精确值：${block.value}` : undefined}
          data-exact-value={block.value}
        >
          {displayValue}
        </strong>
        {block.unit ? <small>{block.unit}</small> : null}
        {formatted ? <span className="sr-only">精确值 {block.value}</span> : null}
      </div>;
    })}</div></section> : null}
    {visual.length ? <section className="scientific-presentation-section"><h4>结果入口</h4><div className="scientific-presentation-links">{visual.map((block) => {
      const label = block.type === "viewer_reference" ? block.label : block.title;
      const href = block.type === "viewer_reference" ? viewerHref(block.source) : artifactHref(block);
      const canPreview = block.type !== "viewer_reference"
        && Boolean(block.source.jobId && block.source.artifactId)
        && artifactCatalog.some((artifact) => (artifact.artifactId || artifact.id) === block.source.artifactId);
      return <div key={block.id}>
        <span>{block.type === "figure" ? "图形" : block.type === "table" ? "表格" : "查看器"}</span>
        <strong>{label}</strong>
        <small>{block.source.versionId ? (block.source.versionNo ? `来源版本 ${block.source.versionNo}` : "已锁定精确来源版本") : "来自 ScientificResult"}</small>
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
            <ArtifactOpenLink href={href}>打开原始 Artifact</ArtifactOpenLink>
            <ArtifactDownloadLink href={href} downloadName={`${block.id}.${block.type === "figure" ? "figure" : "table"}.json`}>下载原始 Artifact</ArtifactDownloadLink>
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
          <span className="scientific-surface-kicker">权威结果预览</span>
          <h5>{activeVisual.title}</h5>
          <p>读取已持久化 Artifact；切换和查看不会重新执行科学计算。</p>
        </div>
        <button type="button" className="product-secondary-action" onClick={() => setActiveVisualId(null)}>关闭预览</button>
      </header>
      <LazyScientificResultViewer
        projectId={projectId}
        jobId={activeVisual.source.jobId}
        selected={activeArtifact}
        artifacts={artifactCatalog}
      />
    </section> : null}
    </section> : null}
    {evidence.length ? <details
      className="scientific-presentation-evidence"
      open={evidenceSectionOpen}
      onToggle={(event) => setEvidenceSectionOpen(event.currentTarget.open)}
    >
      <summary>证据路径 · {evidence.length} 项</summary>
      <ul>{evidence.map((block) => <EvidenceReference
        key={block.id}
        block={block}
        viewerHref={viewerHref(block.source)}
        autoOpenToken={activeEvidenceId === block.id ? activeEvidenceId : null}
        instanceScope={instanceScope}
      />)}</ul>
    </details> : null}
    {mode === "full" && limitations.length ? <section className="scientific-presentation-section scientific-presentation-limitations"><h4>限制与警告</h4><ul>{limitations.map((block) => <li key={block.id}>{presentationLimitationText(block.text)}</li>)}</ul></section> : null}
  </section>;
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
