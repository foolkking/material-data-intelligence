import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ScientificReportAction } from "./ScientificReportAction";

const mocks = vi.hoisted(() => ({
  getScientificReportForTurn: vi.fn(),
  requestScientificReport: vi.fn(),
}));

vi.mock("../lib/scientific-report-api", () => mocks);

describe("ScientificReportAction", () => {
  beforeEach(() => {
    mocks.getScientificReportForTurn.mockReset();
    mocks.requestScientificReport.mockReset();
  });

  it("opens an already persisted report without a new composition request", async () => {
    mocks.getScientificReportForTurn.mockResolvedValue({ report_id: "report_1" });
    render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate />);
    expect(await screen.findByRole("link", { name: "打开报告" })).toHaveAttribute("href", "/projects/project_1/reports/report_1");
    expect(mocks.requestScientificReport).not.toHaveBeenCalled();
  });

  it("requests composition while preserving the zero-recomputation message", async () => {
    const notReady = Object.assign(new Error("not ready"), { status: 404 });
    mocks.getScientificReportForTurn.mockRejectedValue(notReady);
    mocks.requestScientificReport.mockResolvedValue({ generation_id: "generation_1", status: "REQUESTED" });
    render(<ScientificReportAction projectId="project_1" turnId="turn_1" canGenerate />);
    fireEvent.click(await screen.findByRole("button", { name: "生成报告" }));
    await waitFor(() => expect(mocks.requestScientificReport).toHaveBeenCalledWith("turn_1"));
    expect(screen.getByText("正在整理分析报告")).toBeInTheDocument();
    expect(screen.getByText(/不会重新计算/)).toBeInTheDocument();
  });
});
