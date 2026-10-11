import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ScientificReportAction } from "./ScientificReportAction";

const mocks = vi.hoisted(() => ({
  getScientificReportStatusForTurn: vi.fn(),
  requestScientificReport: vi.fn(),
}));

vi.mock("../lib/scientific-report-api", () => mocks);

describe("ScientificReportAction", () => {
  afterEach(() => vi.useRealTimers());
  beforeEach(() => {
    mocks.getScientificReportStatusForTurn.mockReset();
    mocks.requestScientificReport.mockReset();
  });

  it("opens an already persisted report without a new composition request", async () => {
    mocks.getScientificReportStatusForTurn.mockResolvedValue({
      research_turn_id: "turn_1", status: "READY", report_id: "report_1",
      generation_id: null, attempt_count: 0, error_code: null, updated_at: "2026-08-30T00:00:00Z",
    });
    render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate />);
    expect(await screen.findByRole("link", { name: "打开报告" })).toHaveAttribute("href", "/projects/project_1/reports/report_1");
    expect(mocks.requestScientificReport).not.toHaveBeenCalled();
  });

  it.each([
    ["REPORT_PROVIDER_TIMEOUT", "模型服务响应超时"],
    ["REPORT_PROVIDER_RATE_LIMITED", "模型服务请求过于频繁"],
    ["REPORT_PROVIDER_AUTH_FAILED", "模型服务认证失败"],
    ["REPORT_EXTERNAL_UNAVAILABLE", "模型服务暂时不可用"],
    ["REPORT_GROUNDING_FAILED", "报告内容未通过科学依据校验"],
    ["REPORT_SCHEMA_INVALID", "模型返回的报告格式未通过校验"],
    ["private upstream body secret-key", "报告生成失败"],
  ])("explains confirmed failure %s without exposing upstream content", async (code, message) => {
    mocks.getScientificReportStatusForTurn.mockResolvedValue({
      research_turn_id: "turn_1", status: "FAILED", error_code: code,
    });
    render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate />);
    expect(await screen.findByText(new RegExp(message))).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "重试生成" })).toBeEnabled();
    expect(screen.queryByText(/secret-key/)).not.toBeInTheDocument();
    expect(mocks.requestScientificReport).not.toHaveBeenCalled();
  });

  it("offers a compact report action and one composition status", async () => {
    mocks.getScientificReportStatusForTurn
      .mockResolvedValueOnce({
        research_turn_id: "turn_1", status: "NOT_REQUESTED", report_id: null,
        generation_id: null, attempt_count: 0, error_code: null, updated_at: null,
      })
      .mockResolvedValue({
        research_turn_id: "turn_1", status: "COMPOSING", report_id: null,
        generation_id: "generation_1", attempt_count: 1, error_code: null, updated_at: "2026-08-30T00:00:00Z",
      });
    mocks.requestScientificReport.mockResolvedValue({ generation_id: "generation_1", status: "REQUESTED" });
    render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate />);
    const action = await screen.findByRole("button", { name: "生成报告" });
    expect(action).toHaveAttribute("title", "使用已保存的结果生成报告，不会重新计算。");
    expect(screen.queryByText("生成科学报告")).toBeNull();
    fireEvent.click(action);
    await waitFor(() => expect(mocks.requestScientificReport).toHaveBeenCalledWith("turn_1", expect.any(AbortSignal)));
    expect(await screen.findByText("正在整理分析报告")).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("正在整理分析报告");
    expect(screen.queryByText("处理中…")).toBeNull();
  });

  it("treats a missing report as an ordinary idle state without a 404 probe", async () => {
    mocks.getScientificReportStatusForTurn.mockResolvedValue({
      research_turn_id: "turn_1", status: "NOT_REQUESTED", report_id: null,
      generation_id: null, attempt_count: 0, error_code: null, updated_at: null,
    });
    render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate />);
    expect(await screen.findByRole("button", { name: "生成报告" })).toBeEnabled();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(mocks.getScientificReportStatusForTurn).toHaveBeenCalledTimes(1);
  });
  it("omits the empty report controls for a reader without a saved report", async () => {
    mocks.getScientificReportStatusForTurn.mockResolvedValue({ research_turn_id: "turn_1", status: "NOT_REQUESTED" });
    render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate={false} />);
    await waitFor(() => expect(screen.queryByRole("region", { name: "科学报告" })).toBeNull());
    expect(mocks.requestScientificReport).not.toHaveBeenCalled();
  });
  it("rereads after an uncertain write without submitting again", async () => {
    mocks.getScientificReportStatusForTurn.mockResolvedValue({ research_turn_id: "turn_1", status: "NOT_REQUESTED" });
    mocks.requestScientificReport.mockRejectedValue(new Error("lost response"));
    render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate />);
    fireEvent.click(await screen.findByRole("button", { name: "生成报告" }));
    const retry = await screen.findByRole("button", { name: "重新读取报告状态" });
    expect(screen.queryByRole("button", { name: "重试生成" })).not.toBeInTheDocument();
    mocks.getScientificReportStatusForTurn.mockResolvedValue({ research_turn_id: "turn_1", status: "READY", report_id: "saved_report" });
    fireEvent.click(retry);
    expect(await screen.findByRole("link", { name: "打开报告" })).toHaveAttribute("href", "/projects/project_1/reports/saved_report");
    expect(mocks.requestScientificReport).toHaveBeenCalledTimes(1);
  });

  it("rejects foreign report status and preserves read-only recovery", async () => {
    mocks.getScientificReportStatusForTurn.mockResolvedValue({ research_turn_id: "foreign", status: "READY", report_id: "foreign_report" });
    render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate={false} />);
    expect(await screen.findByRole("button", { name: "重新读取报告状态" })).toBeEnabled();
    expect(screen.queryByRole("link", { name: "打开报告" })).not.toBeInTheDocument();
  });

  it("bounds stalled reads and ignores their late results", async () => {
    vi.useFakeTimers();
    let resolve!: (value: unknown) => void;
    mocks.getScientificReportStatusForTurn.mockReturnValue(new Promise((done) => { resolve = done; }));
    render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate />);
    await act(async () => { await vi.advanceTimersByTimeAsync(10_001); });
    expect(screen.getByRole("button", { name: "重新读取报告状态" })).toBeEnabled();
    await act(async () => resolve({ research_turn_id: "turn_1", status: "READY", report_id: "late" }));
    expect(screen.queryByRole("link", { name: "打开报告" })).not.toBeInTheDocument();
  });

  it("discards an unfinished admission after navigating to another Turn", async () => {
    let resolve!: (value: unknown) => void;
    mocks.getScientificReportStatusForTurn.mockImplementation((id) => Promise.resolve({ research_turn_id: id, status: "NOT_REQUESTED" }));
    mocks.requestScientificReport.mockReturnValue(new Promise((done) => { resolve = done; }));
    const view = render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate />);
    fireEvent.click(await screen.findByRole("button", { name: "生成报告" }));
    view.rerender(<ScientificReportAction projectId="project_1" turnId="turn_2" canGenerate />);
    expect(await screen.findByRole("button", { name: "生成报告" })).toBeEnabled();
    const reads = mocks.getScientificReportStatusForTurn.mock.calls.length;
    await act(async () => resolve({ generation_id: "old", status: "REQUESTED" }));
    expect(mocks.getScientificReportStatusForTurn).toHaveBeenCalledTimes(reads);
    expect(screen.getByRole("button", { name: "生成报告" })).toBeEnabled();
  });
  it("bounds a stalled submission and blocks duplicate generation", async () => {
    mocks.getScientificReportStatusForTurn.mockResolvedValue({ research_turn_id: "turn_1", status: "NOT_REQUESTED" });
    mocks.requestScientificReport.mockReturnValue(new Promise(() => {}));
    render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate />);
    const button = await screen.findByRole("button", { name: "生成报告" });
    vi.useFakeTimers();
    fireEvent.click(button); fireEvent.click(button);
    await act(async () => { await vi.advanceTimersByTimeAsync(10_001); });
    expect(screen.getByRole("button", { name: "重新读取报告状态" })).toBeEnabled();
    expect(mocks.requestScientificReport).toHaveBeenCalledTimes(1);
  });

  it.each([
    ["REPORT_QUEUE_TIMEOUT", "报告等待处理超时"],
    ["REPORT_STAGE_TIMEOUT", "报告生成中断或超时"],
  ])("offers explicit retry after durable %s without automatically regenerating", async (code, message) => {
    mocks.getScientificReportStatusForTurn.mockResolvedValue({ research_turn_id: "turn_1", status: "FAILED", error_code: code });
    render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate />);
    const retry = await screen.findByRole("button", { name: "重试生成" });
    expect(screen.getByRole("status")).toHaveTextContent(message);
    expect(screen.getByRole("status")).toHaveTextContent("已保存的科学结果仍可查看");
    expect(mocks.requestScientificReport).not.toHaveBeenCalled();
    mocks.requestScientificReport.mockResolvedValue({ generation_id: "generation_1", status: "REQUESTED" });
    mocks.getScientificReportStatusForTurn.mockResolvedValue({ research_turn_id: "turn_1", status: "READY", report_id: "retried_report" });
    fireEvent.click(retry);
    expect(await screen.findByRole("link", { name: "打开报告" })).toHaveAttribute("href", "/projects/project_1/reports/retried_report");
    expect(mocks.requestScientificReport).toHaveBeenCalledTimes(1);
  });

});
