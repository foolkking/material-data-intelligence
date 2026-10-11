"use client";

import { useRef, useState } from "react";
import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import type { Artifact } from "../../app/lib/planner-api";
import type { ScientificPresentationBlock } from "../../app/lib/scientific-presentation";
import { LazyScientificResultViewer } from "../../scientific-viewers/LazyScientificViewers";
import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { ArtifactOpenLink } from "../../shared/ui/ArtifactOpenLink";
import { ArtifactDownloadLink } from "../../shared/ui/ArtifactDownloadLink";
import styles from "./ResearchResultPresentation.module.css";
import type { ResearchVisualTarget } from "./result-navigation";

type VisualBlock = Extract<ScientificPresentationBlock, { type: "figure" | "table" | "viewer_reference" }>;
const visualLabel = (block: VisualBlock) => {
  const label = block.type === "viewer_reference" ? block.label : block.title;
  return label === "trajectory" ? "原子轨迹" : label;
};
const artifactHref = (block: VisualBlock) => block.source.jobId && block.source.artifactId
  ? `/api/planner/jobs/${encodeURIComponent(block.source.jobId)}/artifacts/${encodeURIComponent(block.source.artifactId)}/content`
  : null;

/** One exact saved output is rendered at a time; changing the selection never runs science. */
export function ResearchResultVisuals({ blocks, artifacts, projectId, instanceId, facts, target }: {
  blocks: readonly VisualBlock[];
  artifacts: readonly Artifact[];
  projectId?: string;
  instanceId: string;
  facts: readonly Agent2ScientificFact[];
  target?: ResearchVisualTarget;
}) {
  const scope = JSON.stringify([instanceId, target?.key, blocks.map((block) => [block.id, block.source.resultId, block.source.jobId, block.source.artifactId])]);
  const [selection, setSelection] = useState<{ scope: string; id: string | null } | null>(null);
  const triggers = useRef(new Map<string, HTMLButtonElement>());
  const selectTrigger = useRef<HTMLSelectElement>(null);
  const previews = blocks.flatMap((block) => {
    if (block.type === "viewer_reference" || !projectId || !block.source.jobId || !block.source.artifactId) return [];
    const matches = artifacts.filter((artifact) => (artifact.artifactId || artifact.id) === block.source.artifactId
      && (!artifact.jobId || artifact.jobId === block.source.jobId));
    return matches.length === 1 ? [{ block, artifact: matches[0] }] : [];
  });
  const candidates = target ? previews.filter(({block}) => !target.missing && target.artifactIds.includes(block.source.artifactId || "")) : previews;
  const preferred = candidates.find(({ block }) => block.type === "figure") || candidates[0];
  const selectedId = selection?.scope === scope ? selection.id : preferred?.block.id;
  const active = previews.find(({ block }) => block.id === selectedId);
  const otherOutputs = blocks.filter((block) => !previews.some((preview) => preview.block === block));
  const closePreview = () => {
    setSelection({ scope, id: null });
    if (previews.length > 3) selectTrigger.current?.focus();
    else if (active) triggers.current.get(active.block.id)?.focus();
  };
  if (!blocks.length && !target) return null;
  return <section className={styles.visuals} aria-label="图表与数据">
    {target && !preferred && selection?.scope !== scope ? <p role="status">{target.missing
      ? "这条引用的结果项当前无法定位。可选择本次研究已保存的图表查看。"
      : "这条结果项没有可预览的图表。"}</p> : null}
    {previews.length > 3 ? <select ref={selectTrigger} className={styles.visualSelect}
      aria-label="选择结果视图" aria-controls={`research-result-visual-${instanceId}`}
      value={active?.block.id || ""} onChange={(event) => setSelection({ scope, id: event.target.value })}>
      <option value="" disabled>选择图表或数据</option>
      {previews.map(({ block }) => <option key={block.id} value={block.id}>{visualLabel(block)}</option>)}
    </select> : previews.length ? <div className={styles.choices} role="group" aria-label="选择结果视图">
      {previews.map(({ block }) => <button key={block.id} type="button"
        ref={(node) => { if (node) triggers.current.set(block.id, node); else triggers.current.delete(block.id); }}
        aria-pressed={active?.block.id === block.id}
        aria-controls={`research-result-visual-${instanceId}`}
        onClick={() => setSelection({ scope, id: block.id })}>{visualLabel(block)}</button>)}
    </div> : null}
    <div id={`research-result-visual-${instanceId}`}>
      {active && projectId ? <section aria-label={`${active.block.type === "figure" ? "图形" : "表格"}：${visualLabel(active.block)}`}>
        <div className={styles.previewActions}>
          <ArtifactOpenLink href={artifactHref(active.block)!}>查看源文件</ArtifactOpenLink>
          <ArtifactDownloadLink href={artifactHref(active.block)!} downloadName={`${active.block.id}.${active.block.type}.json`}>下载</ArtifactDownloadLink>
          <button type="button" className="product-link-button" onClick={closePreview}>收起视图</button>
        </div>
        <LazyScientificResultViewer key={`${scope}:${active.block.id}`} projectId={projectId}
          jobId={active.block.source.jobId!} selected={active.artifact} artifacts={artifacts} resultFacts={facts} />
      </section> : null}
    </div>
    {otherOutputs.length ? <div className={styles.otherOutputs}>{otherOutputs.map((block) => {
      const href = block.type === "viewer_reference"
        ? projectId && block.source.objectId && block.source.versionId
          ? `/projects/${encodeURIComponent(projectId)}/data?object=${encodeURIComponent(block.source.objectId)}&version=${encodeURIComponent(block.source.versionId)}` : null
        : artifactHref(block);
      return <div key={block.id}>
        {block.type === "viewer_reference" && href ? <Link href={href}>打开{visualLabel(block)}</Link> : <>
          <span>{visualLabel(block)}</span>
          {href ? <ArtifactOpenLink href={href}>查看源文件</ArtifactOpenLink> : null}
        </>}
      </div>;
    })}</div> : null}
  </section>;
}
