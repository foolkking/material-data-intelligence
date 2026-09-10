"use client";

import type { Agent2ProgressView } from "../../app/lib/agent2-execution-api";
import {
  RESEARCH_CANCELLING_LABEL,
  isResearchCancellationPending,
} from "../../app/lib/research-status";

const statusLabel: Record<Agent2ProgressView["status"], string> = {
  ORCHESTRATING: "正在组织研究",
  READY_TO_PLAN: "等待生成分析方案",
  PLANNING: "正在准备分析方案",
  PLAN_READY: "分析方案已准备",
  QUEUED: "等待执行资源",
  RUNNING: "正在执行分析",
   CANCELING: RESEARCH_CANCELLING_LABEL,
  RESULT_PENDING: "执行已完成，正在整理科学结果",
  RESULT_READY: "科学结果已准备",
  INTERPRETING: "正在生成科学解释",
  COMPLETED: "科学解释已准备",
  PARTIAL: "部分科学解释已准备",
  FAILED: "分析未能完成",
  CANCELED: "分析已取消",
  ANSWERED: "回答已完成",
};

const strategyActionLabel: Record<string, string> = {
  SYNTHESIZE: "现有证据已足够，正在形成结论",
  CONTINUE_ANALYSIS: "仍有关键证据缺口，需要继续分析",
  REUSE_RESULT: "已有科学结果可以直接复用",
  TEST_HYPOTHESIS: "将用下一项分析检验当前假设",
  COMPARE: "需要可比证据完成科学比较",
  NEEDS_CLARIFICATION: "继续研究前需要补充明确条件",
  CONFLICTING_EVIDENCE: "现有证据存在尚未解决的冲突",
  STOP_WITH_LIMITATIONS: "当前证据不足以支持进一步结论",
};

const stopReasonLabel: Record<string, string> = {
  GOAL_SATISFIED: "研究问题已由现有证据充分回答",
  NO_QUALIFIED_CAPABILITY: "当前没有适用且满足质量要求的进一步分析",
  NEEDS_CLARIFICATION: "继续研究需要用户明确关键条件",
  BUDGET_EXHAUSTED: "本次自主研究已达到执行边界",
  NON_PROGRESS: "继续执行只会重复已有分析",
  CONFLICTING_EVIDENCE: "证据冲突尚不能可靠消解",
  STOP_WITH_LIMITATIONS: "现有数据或方法不足以支持更强结论",
};

export function ResearchExecutionActivity({ progress, onCancel, cancelPending = false, onContinue, onRetry, retryPending = false, onEdit }: { progress: Agent2ProgressView; onCancel?: () => void; cancelPending?: boolean; onContinue?: () => void; onRetry?: () => void; retryPending?: boolean; onEdit?: () => void }) {
  const importantStatus = progress.status === "FAILED" || progress.status === "CANCELED" || progress.status === "RESULT_PENDING" || progress.status === "RESULT_READY" || progress.status === "INTERPRETING" || progress.status === "COMPLETED" || progress.status === "PARTIAL";
  const cancelable = progress.status === "ORCHESTRATING" || progress.status === "READY_TO_PLAN" || progress.status === "PLANNING" || progress.status === "PLAN_READY" || progress.status === "QUEUED" || progress.status === "RUNNING";
  const cancellationPending = isResearchCancellationPending(progress.status);
  const retryable = progress.status === "FAILED" || progress.status === "CANCELED";
  const warnings = Array.from(
    new Map(
      progress.warnings.map((warning) => [
        `${warning.code}\u0000${warning.message}`,
        warning,
      ]),
    ).values(),
  );
  const autonomy = progress.autonomy?.enabled ? progress.autonomy : null;
  const strategy = autonomy?.decision?.strategy;
  const strategySummary = autonomy?.stop?.stopped
    ? stopReasonLabel[autonomy.stop.reason || ""] || "自主研究已在当前科学边界停止"
    : strategyActionLabel[strategy?.action || ""] || null;
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
        <div>{progress.total_step_count > 0 ? <span>{progress.completed_step_count}/{progress.total_step_count}</span> : null}{cancelable && onCancel ? <button type="button" className="product-link-button research-execution-cancel" onClick={onCancel} disabled={cancelPending}>{cancelPending ? "正在提交停止…" : "停止研究"}</button> : cancellationPending ? <span className="research-execution-cancel-state" role="status">{RESEARCH_CANCELLING_LABEL}，等待服务端确认</span> : null}</div>
      </div>
      {autonomy ? (
        <aside className="research-strategy-progress" aria-label="研究策略">
          <div>
            <strong>研究策略</strong>
            <span>第 {autonomy.cycle_index} 轮</span>
          </div>
          {strategy?.current_question?.statement ? <p><b>当前问题</b>{strategy.current_question.statement}</p> : null}
          {strategy?.active_evidence_gap?.statement ? <p><b>待补证据</b>{strategy.active_evidence_gap.statement}</p> : null}
          {strategy?.active_hypothesis?.statement ? <p><b>待检验假设</b>{strategy.active_hypothesis.statement}</p> : null}
          {strategySummary ? <p><b>{autonomy.stop?.stopped ? "停止原因" : "下一步依据"}</b>{strategySummary}</p> : null}
          {autonomy.decision?.limitations?.length ? <p><b>科学限制</b>{autonomy.decision.limitations[0]}</p> : null}
        </aside>
      ) : null}
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
