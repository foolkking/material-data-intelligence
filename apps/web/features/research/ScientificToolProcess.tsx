"use client";

import { useEffect, useState } from "react";
import { getPlannerJobToolCalls, type Artifact, type ToolCall } from "../../app/lib/planner-api";
import type { Agent2ProgressView } from "../../app/lib/agent2-execution-api";
import { readSessionRequest } from "./session-management";
import { ArtifactOpenLink } from "../../shared/ui/ArtifactOpenLink";
import { ProductLink } from "../../shared/layout/ProductNavigation";
import type { Agent2ScientificObjectRef } from "../../app/lib/agent2-research-api";
import { projectScienceNames } from "../../app/lib/project-science-labels";

const statusLabels: Record<string, string> = { SUCCEEDED: "已完成", SUCCESS: "已完成", COMPLETED: "已完成", FAILED: "失败", RUNNING: "执行中", PENDING: "等待执行", QUEUED: "等待执行", SKIPPED: "已跳过", CANCELED: "已取消", CANCELLED: "已取消" };
const outputLabels: Record<string, string> = { "trajectory.json": "原子轨迹数据", "trajectory_summary.json": "轨迹摘要", "trajectory_parse_report.json": "解析检查", "trajectory_manifest.json": "轨迹文件清单" };
const usableSummary = (value?: string) => value && !["No params", "Not available yet", "N/A"].includes(value.trim());

/** Only persisted tool records are shown; no model reasoning or inferred steps. */
export function ScientificToolProcess({ turnId, artifacts, toolCallIds, progress, sources = [], projectId }: { turnId: string; artifacts: readonly Artifact[]; toolCallIds?: readonly string[]; progress?: Agent2ProgressView | null; sources?: readonly Agent2ScientificObjectRef[]; projectId?: string }) {
  const jobs = Array.from(new Set(artifacts.map((item) => item.jobId).filter((id): id is string => Boolean(id))));
  return <div className="scientific-tool-process">
    {sources.length && projectId ? <div><strong>本次分析来源</strong><ul>{sources.map((source) => <li key={`${source.object_id}:${source.version_id}`}><ProductLink href={`/projects/${encodeURIComponent(projectId)}/data?object=${encodeURIComponent(source.object_id)}&version=${encodeURIComponent(source.version_id)}`}>{source.display_name || "查看输入数据"}</ProductLink></li>)}</ul></div> : null}
    {jobs.length ? jobs.map((jobId) => <JobTools key={`${turnId}:${jobId}`} jobId={jobId} artifacts={artifacts.filter((item) => item.jobId === jobId)} toolCallIds={toolCallIds} progress={progress} />) : <p>此结果没有可读取的工具执行记录。来源信息仍可在下方查看。</p>}
  </div>;
}

function JobTools({ jobId, artifacts, toolCallIds, progress }: { jobId: string; artifacts: readonly Artifact[]; toolCallIds?: readonly string[]; progress?: Agent2ProgressView | null }) {
  const [calls, setCalls] = useState<ToolCall[] | null>(null);
  const [error, setError] = useState(false);
  const [pending, setPending] = useState(true);
  const [attempt, setAttempt] = useState(0);
  const allowedIds = new Set(toolCallIds ?? artifacts.flatMap((item) => item.toolCallId ? [item.toolCallId] : []));
  const resultCalls = calls?.filter((call) => typeof call.id === "string" && allowedIds.has(call.id));
  useEffect(() => {
    const controller = new AbortController();
    setPending(true); setError(false);
    void readSessionRequest((signal) => getPlannerJobToolCalls(jobId, { signal }), controller.signal).then((next) => {
      if (!Array.isArray(next) || next.some((call) => !call.id || !call.toolId || call.jobId !== jobId)) throw new Error("Tool execution identity mismatch");
      if (!controller.signal.aborted) setCalls(next);
    }).catch(() => { if (!controller.signal.aborted) setError(true); })
      .finally(() => { if (!controller.signal.aborted) setPending(false); });
    return () => controller.abort();
  }, [jobId, attempt]);
  return <>
    {pending && !calls ? <p role="status">正在读取工具调用…</p> : null}
    {error ? <div role="status"><p>工具调用记录暂时无法读取，分析结果仍可查看。</p><button type="button" className="product-secondary-action" disabled={pending} onClick={() => setAttempt((value) => value + 1)}>重新读取工具调用</button></div> : null}
    {resultCalls?.length === 0 ? <p>没有保存的工具调用记录。</p> : null}
    <ol>{resultCalls?.map((call) => {
      const step = progress?.steps.find((item) => item.step_id === call.stepId);
      const outputs = artifacts.filter((item) => item.toolCallId === call.id);
      return <li key={call.id}>
        <header><strong>{projectScienceNames[call.toolId || ""] || step?.display_name || call.toolId}</strong><span>{statusLabels[(call.status || "").toUpperCase()] || "状态未知"}</span></header>
        {usableSummary(call.inputSummary) ? <p><b>输入</b> {call.inputSummary}</p> : null}
        {usableSummary(call.outputSummary) ? <p><b>输出</b> {call.outputSummary}</p> : null}
        {outputs.length ? <><p>已保存 {outputs.length} 个输出文件</p><ul aria-label="工具输出">{outputs.map((artifact) => <li key={artifact.artifactId || artifact.id}><ArtifactOpenLink href={`/api/planner/jobs/${encodeURIComponent(jobId)}/artifacts/${encodeURIComponent(artifact.artifactId || artifact.id || "")}/content`}>{outputLabels[artifact.name || ""] || artifact.name || artifact.type || "查看输出文件"}</ArtifactOpenLink></li>)}</ul></> : <p>此调用没有已保存的输出文件。</p>}
        <details><summary>调用标识</summary><dl><dt>工具</dt><dd>{call.toolId}</dd><dt>步骤</dt><dd>{call.stepId || "未提供"}</dd><dt>调用</dt><dd>{call.id}</dd><dt>任务</dt><dd>{jobId}</dd></dl></details>
      </li>;
    })}</ol>
  </>;
}
