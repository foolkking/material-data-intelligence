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

  it("distinguishes interpretation progress and partial final interpretation", () => {
    const base = { contract_version: "1.0" as const, turn_id: "turn-4", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: "PARTIAL" as const, result_projection_pending: false };
    const { rerender } = render(<ResearchExecutionActivity progress={{ ...base, status: "INTERPRETING" }} />);
    expect(screen.getByText("正在生成科学解释")).toBeInTheDocument();
    rerender(<ResearchExecutionActivity progress={{ ...base, status: "PARTIAL" }} />);
    expect(screen.getByText("部分科学解释已准备")).toBeInTheDocument();
  });

  it("offers one keyboard-accessible cancel command only while execution is active", () => {
    const onCancel = vi.fn();
    render(<ResearchExecutionActivity onCancel={onCancel} progress={{ contract_version: "1.0", turn_id: "turn-3", status: "RUNNING", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: null, result_projection_pending: false }} />);
    const button = screen.getByRole("button", { name: "停止研究" });
    fireEvent.click(button);
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("offers cancellation during orchestration and planning before a Job exists", () => {
    const onCancel = vi.fn();
    render(<ResearchExecutionActivity onCancel={onCancel} progress={{ contract_version: "1.0", turn_id: "turn-plan", status: "PLANNING", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: null, result_projection_pending: false }} />);
    expect(screen.getByText("正在准备分析方案")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "停止研究" }));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("distinguishes continue, edit, and explicit new-run recovery for terminal failed work", () => {
    const onContinue = vi.fn();
    const onEdit = vi.fn();
    const onRetry = vi.fn();
    render(<ResearchExecutionActivity onContinue={onContinue} onEdit={onEdit} onRetry={onRetry} progress={{ contract_version: "1.0", turn_id: "turn-5", status: "FAILED", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: "FAILED", result_projection_pending: false }} />);
    fireEvent.click(screen.getByRole("button", { name: "继续研究" }));
    fireEvent.click(screen.getByRole("button", { name: "修改问题" }));
    fireEvent.click(screen.getByRole("button", { name: "重新研究（新运行）" }));
    expect(onContinue).toHaveBeenCalledTimes(1);
    expect(onEdit).toHaveBeenCalledTimes(1);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("explains that committed outputs survive cancellation", () => {
    render(<ResearchExecutionActivity onContinue={() => undefined} onEdit={() => undefined} progress={{ contract_version: "1.0", turn_id: "turn-canceled", status: "CANCELED", steps: [], active_step_ids: [], completed_step_count: 1, total_step_count: 2, incremental_outputs: [{ output_key: "output-1", step_id: "step-1", display_label: "结构输出", artifact_id: "artifact-1", preview_available: true, available_at: "2026-08-30T00:00:00Z" }], warnings: [], execution_outcome: "CANCELED", result_projection_pending: false }} />);
    expect(screen.getByText(/已经提交的有效输出仍会保留/)).toBeInTheDocument();
    expect(screen.getByText("继续研究不会自动重算。", { exact: false })).toBeInTheDocument();
    expect(screen.getByText("已有 1 项真实执行输出可查看。")).toBeInTheDocument();
  });

  it("renders query-only turns as completed without exposing scientific controls", () => {
    const onCancel = vi.fn();
    render(<ResearchExecutionActivity onCancel={onCancel} progress={{ contract_version: "1.0", turn_id: "turn-query", status: "ANSWERED", response_kind: "DATA_QUERY", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: null, result_projection_pending: false }} />);
    expect(screen.getByText("数据查询已完成")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "停止研究" })).toBeNull();
  });

  it("labels a zero-recompute continuation as Result reuse rather than a data query", () => {
    render(<ResearchExecutionActivity progress={{ contract_version: "1.0", turn_id: "turn-reuse", status: "ANSWERED", response_kind: "RESULT_REUSE", steps: [], active_step_ids: [], completed_step_count: 0, total_step_count: 0, incremental_outputs: [], warnings: [], execution_outcome: null, result_projection_pending: false }} />);
    expect(screen.getByText("已基于现有科学结果继续回答")).toBeInTheDocument();
    expect(screen.queryByText("数据查询已完成")).toBeNull();
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
