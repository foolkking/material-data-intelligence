"use client";

import type { Agent2ProgressView } from "../lib/agent2-execution-api";

const statusLabel: Record<Agent2ProgressView["status"], string> = {
  ORCHESTRATING: "正在组织研究",
  READY_TO_PLAN: "等待生成分析方案",
  PLANNING: "正在准备分析方案",
  PLAN_READY: "分析方案已准备",
  QUEUED: "等待执行资源",
  RUNNING: "正在执行分析",
  CANCELING: "正在取消分析",
  RESULT_PENDING: "执行已完成，正在整理科学结果",
  RESULT_READY: "科学结果已准备",
  INTERPRETING: "正在生成科学解释",
  COMPLETED: "科学解释已准备",
  PARTIAL: "部分科学解释已准备",
  FAILED: "分析未能完成",
  CANCELED: "分析已取消",
  ANSWERED: "回答已完成",
};

export function ResearchExecutionActivity({ progress, onCancel, cancelPending = false, onContinue, onRetry, retryPending = false, onEdit }: { progress: Agent2ProgressView; onCancel?: () => void; cancelPending?: boolean; onContinue?: () => void; onRetry?: () => void; retryPending?: boolean; onEdit?: () => void }) {
  const importantStatus = progress.status === "FAILED" || progress.status === "CANCELED" || progress.status === "RESULT_PENDING" || progress.status === "RESULT_READY" || progress.status === "INTERPRETING" || progress.status === "COMPLETED" || progress.status === "PARTIAL";
  const cancelable = progress.status === "ORCHESTRATING" || progress.status === "READY_TO_PLAN" || progress.status === "PLANNING" || progress.status === "PLAN_READY" || progress.status === "QUEUED" || progress.status === "RUNNING";
  const retryable = progress.status === "FAILED" || progress.status === "CANCELED";
  const warnings = Array.from(
    new Map(
      progress.warnings.map((warning) => [
        `${warning.code}\u0000${warning.message}`,
        warning,
      ]),
    ).values(),
  );
  return (
    <section className="research-execution-activity" aria-label="分析进度">
      <div className="research-execution-heading">
        <strong>{progress.status === "ANSWERED"
          ? progress.response_kind === "DATA_QUERY"
            ? "数据查询已完成"
            : progress.response_kind === "RESULT_REUSE"
              ? "已基于现有科学结果继续回答"
              : "回答已完成"
          : statusLabel[progress.status]}</strong>
        <div>{progress.total_step_count > 0 ? <span>{progress.completed_step_count}/{progress.total_step_count}</span> : null}{cancelable && onCancel ? <button type="button" className="product-link-button research-execution-cancel" onClick={onCancel} disabled={cancelPending}>{cancelPending ? "正在停止…" : "停止研究"}</button> : null}</div>
      </div>
      <ol className="research-execution-steps">
        {progress.steps.map((step) => (
          <li key={step.step_id} className={`research-execution-step status-${step.status.toLowerCase()}`}>
            <span className="research-execution-marker" aria-hidden="true">{step.status === "SUCCEEDED" ? "✓" : step.status === "RUNNING" ? "●" : step.status === "FAILED" ? "!" : "○"}</span>
            <span>{step.status === "RUNNING" ? step.running_label || `正在${step.display_name}` : step.status === "SUCCEEDED" ? step.completed_label || `${step.display_name}已完成` : step.warning || step.display_name}</span>
            {step.output_available ? <small>已有输出</small> : null}
          </li>
        ))}
      </ol>
      {progress.incremental_outputs.length > 0 ? <p className="research-execution-output-note" role="status">已有 {progress.incremental_outputs.length} 项真实执行输出可查看。</p> : null}
      {importantStatus && warnings.length > 0 ? <ul className="research-execution-warnings" role="status">{warnings.map((warning) => <li key={`${warning.code}-${warning.message}`}>{warning.message}</li>)}</ul> : null}
      {retryable && (onContinue || onEdit || onRetry) ? (
        <div className="research-execution-recovery" role="group" aria-label="研究恢复操作">
          <p>{progress.status === "CANCELED" ? "研究已停止。已经提交的有效输出仍会保留；继续研究不会自动重算。" : "本次研究未完成，历史失败记录会保留。"}</p>
          <div>
            {onContinue ? <button type="button" className="product-primary-action" onClick={onContinue}>继续研究</button> : null}
            {onEdit ? <button type="button" className="product-secondary-action" onClick={onEdit}>修改问题</button> : null}
            {onRetry ? <button type="button" className="product-secondary-action" onClick={onRetry} disabled={retryPending}>{retryPending ? "正在创建新运行…" : "重新研究（新运行）"}</button> : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}
