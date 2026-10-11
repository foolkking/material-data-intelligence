"use client";

import { useState } from "react";
import type { ProjectHistory } from "../../app/lib/planner-api";
import { buildResearchHref } from "../../app/lib/research-navigation";
import { researchRunStatusLabel, researchRunTitle } from "../../app/lib/research-display";
import { ProductLink } from "../../shared/layout/ProductNavigation";
import styles from "./DatasetSourceDetails.module.css";

type Dataset = ProjectHistory["datasets"][number];
type Analysis = ProjectHistory["analyses"][number];

function ResearchEntry({ projectId, run }: { projectId: string; run: Analysis }) {
  const title = researchRunTitle(run);
  const date = new Date(run.createdAt || run.updatedAt || "");
  const sourceCount = new Set(run.sourceDatasetIds || (run.datasetId ? [run.datasetId] : [])).size;
  return <li>
    <ProductLink className={styles.researchLink} href={buildResearchHref({ ...run, projectId })} prefetch={false} title={run.userQuestion?.trim() || undefined}>
      <strong className={styles.question}>{title}</strong>
      <span className={styles.meta}>
        <span>{researchRunStatusLabel(run)}</span>
        {sourceCount > 1 ? <span>{sourceCount} 份数据</span> : null}
        {run.archived ? <span>已归档</span> : null}
        {Number.isFinite(date.getTime()) ? <time dateTime={date.toISOString()}>{date.toLocaleString("zh-CN", {
          year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false,
        })}</time> : null}
      </span>
    </ProductLink>
  </li>;
}

export function DatasetSourceDetails({ projectId, dataset, analyses }: {
  projectId: string;
  dataset: Dataset;
  analyses: Analysis[];
}) {
  const [expanded, setExpanded] = useState(false);
  const files = (dataset.import.files || []).flatMap(file =>
    typeof file.name === "string" && file.name.trim() ? [file.name.trim()] : []);
  const runs = analyses.filter(run => run.sourceDatasetIds === undefined
    ? run.datasetId === dataset.datasetId
    : Array.isArray(run.sourceDatasetIds) && run.sourceDatasetIds.includes(dataset.datasetId))
    .sort((a, b) => (Date.parse(b.createdAt || b.updatedAt || "") || 0) - (Date.parse(a.createdAt || a.updatedAt || "") || 0));
  const outputCount = dataset.resultSummary?.artifactCount;
  return <div className={styles.details}>
    <section aria-label="源文件">
      <h3>源文件</h3>
      {files.length ? <ul className={styles.files}>{files.map((file, index) => <li key={`${index}:${file}`}>{file}</li>)}</ul>
        : <p>{dataset.import.fileCount ? "源文件名称未记录" : "暂无源文件"}</p>}
    </section>
    <section aria-label="相关研究">
      <h3>相关研究</h3>
      {runs.length ? <>
        <p className={styles.meta}>
          <span>{runs.length} 次分析</span>
          {typeof outputCount === "number" && Number.isInteger(outputCount) && outputCount >= 0 ? <span>{outputCount} 个输出文件</span> : null}
        </p>
        <ul className={styles.researchList}>{(expanded ? runs : runs.slice(0, 5)).map(run => <ResearchEntry key={run.jobId} projectId={projectId} run={run} />)}</ul>
        {runs.length > 5 ? <button type="button" className={styles.more} aria-expanded={expanded} onClick={() => setExpanded(value => !value)}>
          {expanded ? "收起研究记录" : `显示全部 ${runs.length} 次分析`}
        </button> : null}
      </> : <p>暂无相关研究</p>}
    </section>
  </div>;
}
