"use client";

import React, { useState } from "react";
import Link from "next/link";
import type { ScientificPresentation, ScientificPresentationBlock } from "../lib/scientific-presentation";
import { isSafePresentationBlock } from "../lib/scientific-presentation";
import { getPlannerInterpretationEvidence, type InterpretationEvidenceResponse } from "../lib/planner-api";

export function ScientificPresentationBlocks({ presentation, mode = "full", projectId, instanceId }: { presentation: ScientificPresentation; mode?: "full" | "report_supplement"; projectId?: string; instanceId?: string }) {
  const blocks = presentation.blocks.filter(isSafePresentationBlock);
  const narrative = blocks.find((block): block is Extract<ScientificPresentationBlock, { type: "narrative" }> => block.type === "narrative");
  const findings = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "finding" }> => block.type === "finding");
  const metrics = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "metric" }> => block.type === "metric");
  const visual = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "figure" | "table" | "viewer_reference" }> => block.type === "figure" || block.type === "table" || block.type === "viewer_reference");
  const evidence = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "evidence_reference" }> => block.type === "evidence_reference");
  const limitations = blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "limitation" | "warning" }> => block.type === "limitation" || block.type === "warning");
  const headingId = `scientific-presentation-title-${(instanceId || presentation.exactSourceRefs[0]?.versionId || "current").replace(/[^a-zA-Z0-9_-]/g, "-")}`;
  const artifactHref = (block: Extract<ScientificPresentationBlock, { type: "figure" | "table" }>) =>
    block.source.jobId && block.source.artifactId
      ? `/api/planner/jobs/${encodeURIComponent(block.source.jobId)}/artifacts/${encodeURIComponent(block.source.artifactId)}/content`
      : null;
  const viewerHref = (source: ScientificPresentationBlock["source"]) =>
    projectId && source.objectId && source.versionId
      ? `/projects/${projectId}/data?object=${encodeURIComponent(source.objectId)}&version=${encodeURIComponent(source.versionId)}`
      : null;
  return <section className="scientific-presentation" aria-labelledby={headingId}>
    <header className="scientific-presentation-header">
      <div><p className="product-kicker">Presentation projection · 1.0</p><h3 id={headingId}>科学呈现</h3></div>
      {presentation.exactSourceRefs.length ? <span>绑定 {presentation.exactSourceRefs.length} 个 exact source version</span> : null}
    </header>
    {presentation.historicalNotice ? <aside className="scientific-presentation-notice" role="note">{presentation.historicalNotice}</aside> : null}
    {mode === "full" && narrative ? <div className="scientific-presentation-narrative"><p>{narrative.text}</p></div> : null}
    {mode === "full" && findings.length ? <section className="scientific-presentation-section"><h4>关键发现</h4><div className="scientific-presentation-findings">{findings.map((block) => <article key={block.id}><span>{block.confidence === "DIRECT" ? "直接证据" : block.confidence === "QUALIFIED" ? "限定结论" : "有限结论"}</span><p>{block.text}</p><small>{block.evidenceIds.length ? `${block.evidenceIds.length} 项证据绑定` : "已绑定 Result"}</small></article>)}</div></section> : null}
    {mode === "full" && metrics.length ? <section className="scientific-presentation-section"><h4>权威指标</h4><div className="scientific-presentation-metrics">{metrics.map((block) => <div key={block.id}><span>{block.title}</span><strong>{block.value}</strong>{block.unit ? <small>{block.unit}</small> : null}</div>)}</div></section> : null}
    {visual.length ? <section className="scientific-presentation-section"><h4>结果入口</h4><div className="scientific-presentation-links">{visual.map((block) => {
      const label = block.type === "viewer_reference" ? block.label : block.title;
      const href = block.type === "viewer_reference" ? viewerHref(block.source) : artifactHref(block);
      return <div key={block.id}><span>{block.type === "figure" ? "图形" : block.type === "table" ? "表格" : "Viewer"}</span>{href ? <Link href={href}><strong>{label}</strong></Link> : <strong>{label}</strong>}<small>{block.source.versionId ? `exact version ${block.source.versionId}` : "来自 ScientificResult"}</small></div>;
    })}</div></section> : null}
    {evidence.length ? <details className="scientific-presentation-evidence"><summary>证据路径 · {evidence.length} 项</summary><ul>{evidence.map((block) => <EvidenceReference key={block.id} block={block} viewerHref={viewerHref(block.source)} />)}</ul></details> : null}
    {mode === "full" && limitations.length ? <section className="scientific-presentation-section scientific-presentation-limitations"><h4>限制与警告</h4><ul>{limitations.map((block) => <li key={block.id}>{block.text}</li>)}</ul></section> : null}
  </section>;
}

function EvidenceReference({ block, viewerHref }: { block: Extract<ScientificPresentationBlock, { type: "evidence_reference" }>; viewerHref: string | null }) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [detail, setDetail] = useState<InterpretationEvidenceResponse | null>(null);
  const evidenceId = block.source.evidenceId || "";
  const interpretationId = block.source.interpretationId || "";
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
  const item = detail?.evidenceItems.find((candidate) => candidate.evidenceItemId === evidenceId);
  const artifact = detail?.artifacts?.find((candidate) => (candidate.artifactId || candidate.id) === (item?.sourceArtifactId || block.source.artifactId));
  const tool = detail?.toolCalls?.find((candidate) =>
    candidate.toolId === item?.sourceToolId
    || (candidate.id || candidate.toolCallId) === (item?.sourceToolId || block.source.toolCallId),
  );
  return <li className="scientific-presentation-evidence-item">
    <strong>{block.label}</strong>
    <small>Result {block.source.resultId || "—"} · Evidence {evidenceId || "—"}</small>
    <div className="scientific-presentation-evidence-actions">
      <button type="button" className="product-link-button" onClick={() => void inspect()} disabled={loading} aria-expanded={open}>
        {loading ? "正在读取证据…" : open ? "收起证据链" : "检查证据链"}
      </button>
      {!detail && block.source.artifactId && block.source.jobId ? <Link href={`/api/planner/jobs/${encodeURIComponent(block.source.jobId)}/artifacts/${encodeURIComponent(block.source.artifactId)}/content`}>打开 Artifact</Link> : null}
      {!detail && !block.source.artifactId && viewerHref ? <Link href={viewerHref}>查看精确来源</Link> : null}
    </div>
    {open ? <div className="scientific-presentation-evidence-inspector" role="region" aria-label={`证据链 ${evidenceId || block.label}`}>
      {error ? <p role="alert">{error}</p> : detail ? <>
        <dl>
          <div><dt>来源对象</dt><dd>{detail.sourceObjectRefs?.length ? detail.sourceObjectRefs.map((source) => `${source.displayName || source.objectType || "ScientificObject"} · ${source.versionId}`).join("；") : "未返回 exact source"}</dd></div>
          <div><dt>Artifact</dt><dd>{artifact ? `${artifact.artifactId || artifact.id || "—"}${artifact.contentHash || artifact.sha256 ? ` · ${artifact.contentHash || artifact.sha256}` : ""}` : "未返回 Artifact"}</dd></div>
          <div><dt>ToolCall</dt><dd>{tool ? `${tool.toolId || tool.id || tool.toolCallId || "—"} · ${tool.status || "unknown"}` : "未返回 ToolCall"}</dd></div>
          <div><dt>字段</dt><dd>{item?.fieldLocator?.fieldId || "—"} · {item?.displayValue || block.label}{item?.unit ? ` ${item.unit}` : ""}</dd></div>
        </dl>
        {artifact && (artifact.artifactId || artifact.id) && (artifact.jobId || detail.jobId) ? <Link href={`/api/planner/jobs/${encodeURIComponent(artifact.jobId || detail.jobId || "")}/artifacts/${encodeURIComponent(artifact.artifactId || artifact.id || "")}/content`}>打开权威 Artifact</Link> : null}
      </> : <p>此呈现块没有可用的 interpretation evidence identity。</p>}
    </div> : null}
    {block.source.versionId ? <small>exact version {block.source.versionId}</small> : null}
  </li>;
}
