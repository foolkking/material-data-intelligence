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
  SEARCH_LITERATURE: "当前证据缺口需要受限的外部科学文献",
};

const stopReasonLabel: Record<string, string> = {
  GOAL_SATISFIED: "研究问题已由现有证据充分回答",
  NO_QUALIFIED_CAPABILITY: "当前没有适用且满足质量要求的进一步分析",
  NEEDS_CLARIFICATION: "继续研究需要用户明确关键条件",
  BUDGET_EXHAUSTED: "本次自主研究已达到执行边界",
  NON_PROGRESS: "继续执行只会重复已有分析",
  CONFLICTING_EVIDENCE: "证据冲突尚不能可靠消解",
  STOP_WITH_LIMITATIONS: "现有数据或方法不足以支持更强结论",
  CANCELLED: "用户已取消当前分析，已完成的科学结果仍然保留",
};

const questionStatus = {
  RESOLVED: { icon: "✓", label: "已由证据回答", className: "resolved" },
  LIMITED: { icon: "◐", label: "部分回答，证据有限", className: "limited" },
  CONFLICTING: { icon: "!", label: "证据存在冲突", className: "conflicting" },
  OPEN: { icon: "○", label: "尚未解决", className: "open" },
} as const;

const hypothesisStatusLabel: Record<string, string> = {
  PROPOSED: "尚未检验",
  PARTIALLY_SUPPORTED: "部分证据支持",
  SUPPORTED_WITHIN_SCOPE: "在当前证据范围内获得支持",
  CONTRADICTED: "当前证据不支持",
  UNRESOLVED: "尚未解决",
  NOT_TESTABLE_WITH_AVAILABLE_CAPABILITIES: "现有能力无法检验",
};

const qualificationLabel: Record<string, string> = {
  DOMAIN_VALIDATED: "已在声明适用范围内验证",
  REFERENCE_VALIDATED: "已通过科学参考案例验证",
  EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED: "平台集成与结果语义已验证",
  STRUCTURAL_ONLY: "仅完成结构集成验证",
};

const comparisonStatusLabel: Record<string, string> = {
  COMPATIBLE: "当前结果在数量语义、单位与分析条件上可直接比较。",
  CONDITIONALLY_COMPATIBLE: "当前结果只能在所列方法或条件限制下比较。",
  NOT_COMPATIBLE: "当前结果不能直接比较；系统不会生成误导性的比较结论。",
  INSUFFICIENT_METADATA: "现有元数据不足以确认这些结果是否可比较。",
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
  const researchQuestions = strategy?.questions?.length
    ? strategy.questions
    : strategy?.current_question?.statement
      ? [strategy.current_question]
      : [];
  const activeHypothesis = strategy?.active_hypothesis
    || strategy?.hypotheses?.find((item) => item.status !== "CONTRADICTED")
    || strategy?.hypotheses?.[0];
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
        <div>{progress.total_step_count > 0 ? <span>{progress.completed_step_count}/{progress.total_step_count}</span> : null}{cancelable && onCancel ? <button type="button" className="product-link-button research-execution-cancel" onClick={onCancel} disabled={cancelPending}>{cancelPending ? "正在提交取消…" : "取消当前分析"}</button> : cancellationPending ? <span className="research-execution-cancel-state" role="status">{RESEARCH_CANCELLING_LABEL}，等待服务端确认</span> : null}</div>
      </div>
      {autonomy ? (
        <aside className="research-strategy-progress" aria-label="研究策略">
          <div>
            <strong>研究进展</strong>
            <span>有界研究 · 第 {autonomy.cycle_index} 轮</span>
          </div>
          {autonomy.objective ? <p className="research-strategy-objective"><b>主要问题</b>{autonomy.objective}</p> : null}
          {strategy?.current_question?.statement && !strategy.questions?.length && strategy.current_question.statement !== autonomy.objective ? <p><b>当前问题</b>{strategy.current_question.statement}</p> : null}
          {researchQuestions.length ? (
            <section className="research-map" aria-labelledby={`research-map-${progress.turn_id}`}>
              <h4 id={`research-map-${progress.turn_id}`}>研究地图</h4>
              <ul>
                {researchQuestions.map((question, index) => {
                  const status = questionStatus[(question.status || "OPEN") as keyof typeof questionStatus] || questionStatus.OPEN;
                  const evidenceCount = question.evidence_result_ids?.length || 0;
                  return (
                    <li key={question.question_id || `${question.statement}-${index}`} className={`research-map-${status.className}`}>
                      <span aria-hidden="true">{status.icon}</span>
                      <div>
                        <strong>{question.statement || "未命名科学问题"}</strong>
                        <small>{status.label}{evidenceCount ? ` · ${evidenceCount} 项科学结果` : ""}</small>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </section>
          ) : null}
          {strategy?.active_evidence_gap?.statement ? <p className="research-evidence-gap"><b>仍缺少</b>{strategy.active_evidence_gap.statement}</p> : null}
          {strategy?.comparison_status ? <p className={`research-comparison-status status-${strategy.comparison_status.toLowerCase()}`}><b>比较条件</b>{comparisonStatusLabel[strategy.comparison_status] || strategy.comparison_status}</p> : null}
          {strategy?.contradictions?.some((item) => item.unresolved) ? (
            <section className="research-contradiction" role="note" aria-label="证据冲突">
              <strong>证据冲突尚未解决</strong>
              {strategy.contradictions.filter((item) => item.unresolved).slice(0, 2).map((item) => (
                <p key={item.contradiction_id || item.predicate}>{item.resolution || "现有证据不能可靠确定同一结论。"}</p>
              ))}
            </section>
          ) : null}
          {activeHypothesis?.statement ? (
            <section className="research-hypothesis" aria-label="科学假设">
              <div>
                <strong>科学假设</strong>
                <span>{hypothesisStatusLabel[activeHypothesis.status || ""] || "状态待确认"}</span>
              </div>
              <p>{activeHypothesis.statement}</p>
              {activeHypothesis.supporting_result_ids?.length ? <small>已有 {activeHypothesis.supporting_result_ids.length} 项结果提供支持，但假设仍不等同于计算事实。</small> : <small>这是待检验的研究假设，不是已计算的科学事实。</small>}
              {activeHypothesis.known_assumptions?.[0] ? <small>前提：{activeHypothesis.known_assumptions[0]}</small> : null}
            </section>
          ) : null}
          {strategySummary ? <p><b>{autonomy.stop?.stopped ? "停止原因" : "下一步依据"}</b>{strategySummary}</p> : null}
          {autonomy.decision?.qualification_level ? <p><b>方法验证</b>{qualificationLabel[autonomy.decision.qualification_level] || autonomy.decision.qualification_level}</p> : null}
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
          <p>{progress.status === "CANCELED" ? "当前分析已取消。已经提交的有效输出仍会保留；继续当前研究不会自动重算。" : "本次研究未完成。已完成的科学结果会保留；重新运行会创建一次新的执行。"}</p>
          <div>
            {onContinue ? <button type="button" className="product-primary-action" onClick={onContinue}>继续当前研究</button> : null}
            {onEdit ? <button type="button" className="product-secondary-action" onClick={onEdit}>修改问题并创建分支</button> : null}
            {onRetry ? <button type="button" className="product-secondary-action" onClick={onRetry} disabled={retryPending}>{retryPending ? "正在创建新运行…" : "重新运行分析"}</button> : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}
