import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ResearchExecutionActivity } from "./ResearchExecutionActivity";

describe("ResearchExecutionActivity", () => {
  it("renders capability-level progress without runtime implementation identifiers", () => {
    render(<ResearchExecutionActivity progress={{
      contract_version: "1.0", turn_id: "turn-1", status: "RUNNING", plan_title: "XRD",
      steps: [
        { step_id: "step_1", display_name: "生成理论 XRD 图谱", status: "SUCCEEDED", output_available: true, completed_label: "理论 XRD 图谱已生成" },
        { step_id: "step_2", display_name: "比较实验峰与理论峰", status: "RUNNING", output_available: false, running_label: "正在比较实验峰与理论峰" },
      ],
      active_step_ids: ["step_2"], completed_step_count: 1, total_step_count: 2,
      incremental_outputs: [{ output_key: "step_1.output_1", step_id: "step_1", display_label: "理论 XRD 图谱已生成", artifact_id: "artifact-secret", preview_available: true, available_at: "2026-08-23T00:00:00Z" }],
      warnings: [], execution_outcome: null, result_projection_pending: false,
    }} />);
    expect(screen.getByText("正在执行分析")).toBeInTheDocument();
    expect(screen.getByText("理论 XRD 图谱已生成")).toBeInTheDocument();
    expect(screen.getByText("正在比较实验峰与理论峰")).toBeInTheDocument();
    expect(screen.queryByText(/artifact-secret|tool_call|job_/i)).toBeNull();
  });

  it("does not describe RESULT_PENDING as fully completed research", () => {
    render(<ResearchExecutionActivity progress={{ contract_version: "1.0", turn_id: "turn-2", status: "RESULT_PENDING", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: "SUCCESS", result_projection_pending: true }} />);
    expect(screen.getByText("执行已完成，正在整理科学结果")).toBeInTheDocument();
    expect(screen.queryByText("研究完成")).toBeNull();
  });

  it("shows RESULT_READY as a result-ready state", () => {
    render(<ResearchExecutionActivity progress={{ contract_version: "1.0", turn_id: "turn-3", status: "RESULT_READY", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: "SUCCESS", result_projection_pending: false }} />);
    expect(screen.getByText("科学结果已准备")).toBeInTheDocument();
  });

  it("uses the shared cancellation language and removes conflicting stop controls while CANCELING", () => {
    render(
      <ResearchExecutionActivity
        onCancel={() => undefined}
        progress={{
          contract_version: "1.0",
          turn_id: "turn-canceling",
          status: "CANCELING",
          steps: [],
          active_step_ids: [],
          completed_step_count: 1,
          total_step_count: 2,
          incremental_outputs: [],
          warnings: [],
          execution_outcome: null,
          result_projection_pending: false,
        }}
      />,
    );

    expect(screen.getByText("正在取消研究")).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("等待服务端确认");
    expect(screen.queryByRole("button", { name: "取消当前分析" })).toBeNull();
  });

  it("distinguishes interpretation progress and partial final interpretation", () => {
    const base = { contract_version: "1.0" as const, turn_id: "turn-4", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: "PARTIAL" as const, result_projection_pending: false };
    const { rerender } = render(<ResearchExecutionActivity progress={{ ...base, status: "INTERPRETING" }} />);
    expect(screen.getByText("正在生成科学解释")).toBeInTheDocument();
    rerender(<ResearchExecutionActivity progress={{ ...base, status: "PARTIAL" }} />);
    expect(screen.getByText("部分科学解释已准备")).toBeInTheDocument();
  });

  it("shows bounded provider retry while keeping completed science preserved", () => {
    render(<ResearchExecutionActivity progress={{
      contract_version: "1.0",
      turn_id: "turn-retrying",
      status: "INTERPRETING",
      steps: [],
      active_step_ids: [],
      completed_step_count: 0,
      total_step_count: 0,
      incremental_outputs: [],
      warnings: [{
        code: "INTERPRETATION_RETRYING",
        message: "解释服务暂时繁忙，正在按有界策略重试；已完成的科学结果仍然保留。",
      }],
      execution_outcome: "SUCCESS",
      result_projection_pending: false,
    }} />);

    expect(screen.getByText("正在生成科学解释")).toBeInTheDocument();
    expect(screen.getByText(/正在按有界策略重试/)).toBeInTheDocument();
    expect(screen.getByText(/已完成的科学结果仍然保留/)).toBeInTheDocument();
  });

  it("offers one keyboard-accessible cancel command only while execution is active", () => {
    const onCancel = vi.fn();
    render(<ResearchExecutionActivity onCancel={onCancel} progress={{ contract_version: "1.0", turn_id: "turn-3", status: "RUNNING", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: null, result_projection_pending: false }} />);
    const button = screen.getByRole("button", { name: "取消当前分析" });
    fireEvent.click(button);
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("offers cancellation during orchestration and planning before a Job exists", () => {
    const onCancel = vi.fn();
    render(<ResearchExecutionActivity onCancel={onCancel} progress={{ contract_version: "1.0", turn_id: "turn-plan", status: "PLANNING", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: null, result_projection_pending: false }} />);
    expect(screen.getByText("正在准备分析方案")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "取消当前分析" }));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("distinguishes continue, edit, and explicit new-run recovery for terminal failed work", () => {
    const onContinue = vi.fn();
    const onEdit = vi.fn();
    const onRetry = vi.fn();
    render(<ResearchExecutionActivity onContinue={onContinue} onEdit={onEdit} onRetry={onRetry} progress={{ contract_version: "1.0", turn_id: "turn-5", status: "FAILED", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: "FAILED", result_projection_pending: false }} />);
    fireEvent.click(screen.getByRole("button", { name: "继续当前研究" }));
    fireEvent.click(screen.getByRole("button", { name: "修改问题并创建分支" }));
    fireEvent.click(screen.getByRole("button", { name: "重新运行分析" }));
    expect(onContinue).toHaveBeenCalledTimes(1);
    expect(onEdit).toHaveBeenCalledTimes(1);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("explains that committed outputs survive cancellation", () => {
    render(<ResearchExecutionActivity onContinue={() => undefined} onEdit={() => undefined} progress={{ contract_version: "1.0", turn_id: "turn-canceled", status: "CANCELED", steps: [], active_step_ids: [], completed_step_count: 1, total_step_count: 2, incremental_outputs: [{ output_key: "output-1", step_id: "step-1", display_label: "结构输出", artifact_id: "artifact-1", preview_available: true, available_at: "2026-08-30T00:00:00Z" }], warnings: [], execution_outcome: "CANCELED", result_projection_pending: false }} />);
    expect(screen.getByText(/已经提交的有效输出仍会保留/)).toBeInTheDocument();
    expect(screen.getByText("继续当前研究不会自动重算。", { exact: false })).toBeInTheDocument();
    expect(screen.getByText("已有 1 项真实执行输出可查看。")).toBeInTheDocument();
  });

  it("renders query-only turns as completed without exposing scientific controls", () => {
    const onCancel = vi.fn();
    render(<ResearchExecutionActivity onCancel={onCancel} progress={{ contract_version: "1.0", turn_id: "turn-query", status: "ANSWERED", response_kind: "DATA_QUERY", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: null, result_projection_pending: false }} />);
    expect(screen.getByText("数据查询已完成")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "取消当前分析" })).toBeNull();
  });

  it("labels a zero-recompute continuation as Result reuse rather than a data query", () => {
    render(<ResearchExecutionActivity progress={{ contract_version: "1.0", turn_id: "turn-reuse", status: "ANSWERED", response_kind: "RESULT_REUSE", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: null, result_projection_pending: false }} />);
    expect(screen.getByText("已基于现有科学结果继续回答")).toBeInTheDocument();
    expect(screen.queryByText("数据查询已完成")).toBeNull();
  });

  it("shows bounded scientific strategy without exposing hidden reasoning or runtime ids", () => {
    render(<ResearchExecutionActivity progress={{
      contract_version: "1.0",
      turn_id: "turn-strategy",
      status: "RESULT_READY",
      steps: [],
      active_step_ids: [],
      completed_step_count: 1,
      total_step_count: 1,
      incremental_outputs: [],
      warnings: [],
      execution_outcome: "SUCCESS",
      result_projection_pending: false,
      autonomy: {
        enabled: true,
        mode: "BOUNDED_AUTONOMOUS",
        cycle_index: 2,
        decision: {
          outcome: "CONTINUE_WITH_ANALYSIS",
          limitations: ["该关系目前仍是方法依赖的解释。"],
          qualification_level: "DOMAIN_VALIDATED",
          strategy: {
            action: "TEST_HYPOTHESIS",
            current_question: { question_id: "q-structure", statement: "局部结构是否能解释输运异常？", status: "OPEN" },
            questions: [
              { question_id: "q-transport", statement: "扩散是否升高？", status: "RESOLVED", evidence_result_ids: ["result-1"] },
              { question_id: "q-structure", statement: "局部结构是否能解释输运异常？", status: "OPEN", evidence_result_ids: [] },
            ],
            active_evidence_gap: { statement: "缺少局部结构证据。" },
            active_hypothesis: {
              statement: "较弱的局部约束可能与较高扩散相关。",
              status: "PROPOSED",
              supporting_result_ids: [],
              known_assumptions: ["当前结构与轨迹代表相同材料状态。"],
            },
            comparison_status: "CONDITIONALLY_COMPATIBLE",
            contradictions: [{
              contradiction_id: "contradiction-1",
              predicate: "transport.regime",
              unresolved: true,
              resolution: "两项结果使用了不同的拟合区间，当前不能静默合并。",
            }],
          },
        },
        stop: { stopped: false, reason: null },
      },
    }} />);

    expect(screen.getByRole("complementary", { name: "研究策略" })).toHaveTextContent("第 2 轮");
    expect(screen.getByRole("heading", { name: "研究地图" })).toBeInTheDocument();
    expect(screen.getByText("扩散是否升高？")).toBeInTheDocument();
    expect(screen.getByText(/已由证据回答 · 1 项科学结果/)).toBeInTheDocument();
    expect(screen.getByText("尚未解决")).toBeInTheDocument();
    expect(screen.getByText("局部结构是否能解释输运异常？")).toBeInTheDocument();
    expect(screen.getByText("较弱的局部约束可能与较高扩散相关。")).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "科学假设" })).toHaveTextContent("尚未检验");
    expect(screen.getByRole("region", { name: "科学假设" })).toHaveTextContent("不是已计算的科学事实");
    expect(screen.getByText("当前结果只能在所列方法或条件限制下比较。")).toBeInTheDocument();
    expect(screen.getByRole("note", { name: "证据冲突" })).toHaveTextContent("不同的拟合区间");
    expect(screen.getByText("将用下一项分析检验当前假设")).toBeInTheDocument();
    expect(screen.getByText("已在声明适用范围内验证")).toBeInTheDocument();
    expect(screen.queryByText(/hidden_reasoning|tool\\.|adapter\\.|job_/i)).toBeNull();
  });

  it("deduplicates repeated execution warnings without duplicate React keys", () => {
    render(<ResearchExecutionActivity progress={{
      contract_version: "1.0",
      turn_id: "turn-warning",
      status: "FAILED",
      steps: [],
      active_step_ids: [],
      completed_step_count: 0,
      total_step_count: 0,
      incremental_outputs: [],
      warnings: [
        { code: "EXECUTION_STEP_FAILED", message: "该步骤未能完成，已保留已生成的输出。" },
        { code: "EXECUTION_STEP_FAILED", message: "该步骤未能完成，已保留已生成的输出。" },
      ],
      execution_outcome: "FAILED",
      result_projection_pending: false,
    }} />);

    expect(screen.getAllByText("该步骤未能完成，已保留已生成的输出。")).toHaveLength(1);
  });
});
