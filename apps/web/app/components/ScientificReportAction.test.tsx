import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ScientificReportAction } from "./ScientificReportAction";

const mocks = vi.hoisted(() => ({
  getScientificReportStatusForTurn: vi.fn(),
  requestScientificReport: vi.fn(),
}));

vi.mock("../lib/scientific-report-api", () => mocks);

describe("ScientificReportAction", () => {
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

  it("requests composition while preserving the zero-recomputation message", async () => {
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
    fireEvent.click(await screen.findByRole("button", { name: "生成报告" }));
    await waitFor(() => expect(mocks.requestScientificReport).toHaveBeenCalledWith("turn_1"));
    expect(screen.getByText("正在整理分析报告")).toBeInTheDocument();
    expect(screen.getByText(/不会重新计算/)).toBeInTheDocument();
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
});
