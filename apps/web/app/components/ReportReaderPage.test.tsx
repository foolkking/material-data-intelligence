import React from "react";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getProjectHistory: vi.fn(), getPlannerJobArtifacts: vi.fn(), getPlannerJobInterpretations: vi.fn(),
  getPlannerJob: vi.fn(), getPlannerInterpretationEvidence: vi.fn(), archiveProjectRun: vi.fn(),
  listReportCompositions: vi.fn(), getReportComposition: vi.fn(),
}));
vi.mock("../lib/planner-api", async () => ({ ...await vi.importActual<typeof import("../lib/planner-api")>("../lib/planner-api"), ...mocks }));
vi.mock("../../shared/layout/ProductShell", () => ({ ProductShell: ({children}: {children: React.ReactNode}) => <>{children}</>, RequireProductAuth: ({children}: {children: React.ReactNode}) => <>{children}</> }));
vi.mock("../../scientific-viewers/LazyScientificViewers", () => ({ LazyScientificResultViewer: ({selected}: {selected: {id: string}}) => <div>已保存结果 {selected.id}</div> }));
vi.mock("../lib/report-composition-api", () => ({ listReportCompositions: mocks.listReportCompositions, getReportComposition: mocks.getReportComposition }));
import { ReportReaderPage } from "../../features/reports/ReportPages";

const history = { project: { projectId: "project-1", name: "项目一", role: "owner" }, datasets: [], analyses: [{ jobId: "job-1", userQuestion: "比较回归误差", artifactCount: 1, stepCount: 1 }] };
beforeEach(() => {
  vi.resetAllMocks();
  mocks.getProjectHistory.mockResolvedValue(history);
  mocks.getPlannerJobArtifacts.mockResolvedValue([{ id: "metrics-1", type: "metrics_json", name: "metrics.json" }]);
  mocks.getPlannerJobInterpretations.mockResolvedValue({interpretations: []});
  mocks.getPlannerJob.mockResolvedValue({ analysisPlan: { goal: "比较回归误差", steps: [] } });
  mocks.listReportCompositions.mockResolvedValue({items: []});
});

it("retains previously read output when every endpoint fails on retry", async () => {
  mocks.getPlannerJobInterpretations.mockRejectedValueOnce(new Error("offline"));
  render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
  expect(await screen.findByText("已保存结果 metrics-1")).toBeInTheDocument();
  for (const method of [mocks.getProjectHistory, mocks.getPlannerJobArtifacts, mocks.getPlannerJobInterpretations, mocks.getPlannerJob]) method.mockRejectedValueOnce(new Error("offline"));
  await userEvent.click(await screen.findByRole("button", {name: "重新加载报告内容"}));
  expect(await screen.findByText(/未能读取：.*科学结果列表/u)).toBeInTheDocument();
  expect(screen.getByText("已保存结果 metrics-1")).toBeInTheDocument();
  expect(screen.getByRole("heading", {name: "比较回归误差"})).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", {name: "重新加载报告内容"}));
  await waitFor(() => expect(screen.queryByRole("button", {name: "重新加载报告内容"})).not.toBeInTheDocument());
  expect(screen.getByText("已保存结果 metrics-1")).toBeInTheDocument();
});

it("names supplementary results individually and keeps an opened result through read recovery", async () => {
  mocks.getPlannerJobArtifacts.mockResolvedValue([
    { id: "main-plot", type: "plotly_json", name: "scatter.json" },
    { id: "metrics-1", type: "metrics_json", name: "metrics.json" },
    { id: "data-1", type: "table_json", name: "误差明细.json" },
  ]);
  mocks.getPlannerJobInterpretations.mockRejectedValueOnce(new Error("offline"));
  render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
  expect(await screen.findByText("已保存结果 main-plot")).toBeVisible();
  expect(screen.getByText("已保存结果 metrics-1")).not.toBeVisible();
  expect(screen.getByText("已保存结果 data-1")).not.toBeVisible();
  await userEvent.click(screen.getByText("计算指标", { selector: "summary" }));
  expect(screen.getByText("已保存结果 metrics-1")).toBeVisible();
  expect(screen.getByText("已保存结果 data-1")).not.toBeVisible();
  mocks.getPlannerJobArtifacts.mockRejectedValueOnce(new Error("offline"));
  await userEvent.click(screen.getByRole("button", { name: "重新加载报告内容" }));
  await screen.findByText(/未能读取：.*科学结果列表/u);
  expect(screen.getByText("已保存结果 metrics-1")).toBeVisible();
  await userEvent.click(screen.getByRole("button", { name: "重新加载报告内容" }));
  await waitFor(() => expect(screen.queryByRole("button", { name: "重新加载报告内容" })).not.toBeInTheDocument());
  expect(screen.getByText("已保存结果 metrics-1")).toBeVisible();
});

it("shows completed output while a separate report request is still pending", async () => {
  let finish!: (value: unknown) => void;
  mocks.getPlannerJobInterpretations.mockReturnValueOnce(new Promise(resolve => {finish = resolve;}));
  render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
  expect(await screen.findByText("已保存结果 metrics-1")).toBeInTheDocument();
  expect(screen.queryByText("尚无已保存的结果解读，可先复核上方科学输出与来源。")).not.toBeInTheDocument();
  await act(async () => finish({interpretations: []}));
});

it("times out a stalled read, preserves output, ignores its late response, and allows retry", async () => {
  vi.useFakeTimers();
  try {
    let finish!: (value: unknown) => void;
    mocks.getPlannerJobInterpretations.mockReturnValueOnce(new Promise(resolve => {finish = resolve;}));
    render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
    await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
    expect(screen.getByText("已保存结果 metrics-1")).toBeInTheDocument();
    expect(screen.getByText(/未能读取：结果解读/u)).toBeInTheDocument();
    expect(mocks.getPlannerJobInterpretations.mock.calls[0][1].signal.aborted).toBe(true);
    expect(screen.getByRole("button", {name: "重新加载报告内容"})).toBeEnabled();
    await act(async () => finish({interpretations: []}));
    expect(screen.getByText(/未能读取：结果解读/u)).toBeInTheDocument();
    await act(async () => fireEvent.click(screen.getByRole("button", {name: "重新加载报告内容"})));
    expect(screen.queryByText(/未能读取：结果解读/u)).not.toBeInTheDocument();
    expect(screen.getByText("已保存结果 metrics-1")).toBeInTheDocument();
  } finally {
    vi.useRealTimers();
  }
});

it("retains evidence for the same interpretation after a failed retry", async () => {
  mocks.getProjectHistory.mockRejectedValueOnce(new Error("offline"));
  mocks.getPlannerJobInterpretations.mockResolvedValue({interpretations: [{interpretationId: "interpretation-1", claims: [], globalLimitations: []}]});
  mocks.getPlannerInterpretationEvidence.mockResolvedValueOnce({interpretationId: "interpretation-1", evidenceItems: [{evidenceItemId: "evidence-1", semanticRole: "sample_count", displayValue: "4"}]});
  render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
  expect(await screen.findByText("依据 · 1 项")).toBeInTheDocument();
  mocks.getPlannerInterpretationEvidence.mockRejectedValueOnce(new Error("offline"));
  await userEvent.click(screen.getByRole("button", {name: "重新加载报告内容"}));
  expect(await screen.findByText(/未能读取：解读依据/u)).toBeInTheDocument();
  expect(screen.getByText("依据 · 1 项")).toBeInTheDocument();
});

it("never attaches evidence from a previous interpretation to a newly read interpretation", async () => {
  mocks.getProjectHistory.mockRejectedValueOnce(new Error("offline"));
  mocks.getPlannerJobInterpretations.mockResolvedValueOnce({interpretations: [{interpretationId: "interpretation-1", claims: [], globalLimitations: []}]});
  mocks.getPlannerInterpretationEvidence.mockResolvedValueOnce({interpretationId: "interpretation-1", evidenceItems: [{evidenceItemId: "evidence-1", semanticRole: "sample_count", displayValue: "4"}]});
  render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
  expect(await screen.findByText("依据 · 1 项")).toBeInTheDocument();
  mocks.getPlannerJobInterpretations.mockResolvedValueOnce({interpretations: [{interpretationId: "interpretation-2", claims: [], globalLimitations: []}]});
  mocks.getPlannerInterpretationEvidence.mockRejectedValueOnce(new Error("offline"));
  await userEvent.click(screen.getByRole("button", {name: "重新加载报告内容"}));
  expect(await screen.findByText(/未能读取：解读依据/u)).toBeInTheDocument();
  expect(screen.queryByText("依据 · 1 项")).not.toBeInTheDocument();
});

it("reports missing editorial content, retries it, and retains it across another failure", async () => {
  mocks.getProjectHistory.mockResolvedValue({...history, analyses: [{...history.analyses[0], workspaceId: "workspace-1"}]});
  mocks.listReportCompositions.mockRejectedValueOnce(new Error("offline"));
  render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
  expect(await screen.findByText(/未能读取：报告正文/u)).toBeInTheDocument();
  expect(screen.getByText("已保存结果 metrics-1")).toBeInTheDocument();
  mocks.listReportCompositions.mockResolvedValue({items: [{sourceJobId: "job-1", reportId: "composition-1"}]});
  mocks.getReportComposition.mockResolvedValue({editorialProjection: {reportTitle: "保存的报告正文", summary: "已保存的总结"}});
  mocks.getPlannerJobInterpretations.mockRejectedValueOnce(new Error("offline"));
  await userEvent.click(screen.getByRole("button", {name: "重新加载报告内容"}));
  expect(await screen.findByRole("heading", {name: "保存的报告正文"})).toBeInTheDocument();
  await waitFor(() => expect(screen.getByRole("button", {name: "重新加载报告内容"})).toBeEnabled());
  mocks.getReportComposition.mockRejectedValueOnce(new Error("offline"));
  await userEvent.click(screen.getByRole("button", {name: "重新加载报告内容"}));
  expect(await screen.findByText(/未能读取：报告正文/u)).toBeInTheDocument();
  expect(screen.getByText("已保存的总结")).toBeInTheDocument();
});

it("does not mislabel a failed artifact read as no results and retries the exact report", async () => {
  mocks.getPlannerJobArtifacts.mockRejectedValueOnce(new Error("offline"));
  render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
  expect(await screen.findByText(/未能读取：科学结果列表/u)).toBeInTheDocument();
  expect(screen.queryByText("本次运行没有可展示的结果")).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", {name: "重新加载报告内容"}));
  expect(await screen.findByText("已保存结果 metrics-1")).toBeInTheDocument();
  expect(screen.queryByRole("button", {name: "重新加载报告内容"})).not.toBeInTheDocument();
  expect(mocks.getPlannerJobArtifacts).toHaveBeenLastCalledWith("job-1", {signal: expect.any(AbortSignal)});
});

it("keeps scientific output readable when interpretation and project history are unavailable", async () => {
  mocks.getPlannerJobInterpretations.mockRejectedValueOnce(new Error("offline"));
  mocks.getProjectHistory.mockRejectedValueOnce(new Error("offline"));
  render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
  expect(await screen.findByText("已保存结果 metrics-1")).toBeInTheDocument();
  expect(screen.getByText(/未能读取：项目历史、结果解读/u)).toBeInTheDocument();
  expect(screen.getByText("结果解读暂时无法读取，请重新加载报告内容。")).toBeInTheDocument();
});

it("shows archive failure without changing the report or exposing upstream errors", async () => {
  mocks.archiveProjectRun.mockRejectedValueOnce(new Error("private upstream text"));
  render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
  await userEvent.click(await screen.findByRole("button", {name: "归档此报告"}));
  expect(await screen.findByText("报告状态未能更新，请重试。已有报告内容未被更改。")).toBeInTheDocument();
  expect(screen.getByRole("button", {name: "归档此报告"})).toBeEnabled();
  expect(screen.queryByText(/private upstream text/u)).not.toBeInTheDocument();
});

it("can recover when all report reads fail", async () => {
  for (const method of [mocks.getProjectHistory, mocks.getPlannerJobArtifacts, mocks.getPlannerJobInterpretations, mocks.getPlannerJob]) method.mockRejectedValueOnce(new Error("offline"));
  render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
  expect(await screen.findByRole("heading", {name: "报告内容暂时无法读取"})).toBeInTheDocument();
  expect(screen.queryByText("本次运行没有可展示的结果")).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", {name: "重新加载报告内容"}));
  expect(await screen.findByText("已保存结果 metrics-1")).toBeInTheDocument();
});

it("distinguishes unavailable evidence from an interpretation without evidence", async () => {
  mocks.getPlannerJobInterpretations.mockResolvedValue({interpretations: [{interpretationId: "interpretation-1", claims: [], globalLimitations: []}]});
  mocks.getPlannerInterpretationEvidence.mockRejectedValueOnce(new Error("offline"));
  render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
  expect(await screen.findByText(/未能读取：解读依据/u)).toBeInTheDocument();
  expect(screen.getByText("已保存结果 metrics-1")).toBeInTheDocument();
});

it("ignores late report evidence after navigating to another report", async () => {
  let finish!: (value: unknown) => void;
  mocks.getPlannerJobInterpretations.mockResolvedValueOnce({interpretations: [{interpretationId: "interpretation-old", claims: [], globalLimitations: []}]});
  mocks.getPlannerInterpretationEvidence.mockReturnValueOnce(new Promise(resolve => {finish = resolve;}));
  const {rerender} = render(<ReportReaderPage projectId="project-1" reportId="job-1" />);
  await waitFor(() => expect(mocks.getPlannerInterpretationEvidence).toHaveBeenCalledWith("interpretation-old", {signal: expect.any(AbortSignal)}));
  mocks.getPlannerJobArtifacts.mockResolvedValue([{id: "metrics-new", type: "metrics_json", name: "metrics.json"}]);
  rerender(<ReportReaderPage projectId="project-1" reportId="job-2" />);
  expect(await screen.findByText("已保存结果 metrics-new")).toBeInTheDocument();
  await act(async () => finish({items: []}));
  expect(screen.getByText("已保存结果 metrics-new")).toBeInTheDocument();
  expect(screen.queryByText("已保存结果 metrics-1")).not.toBeInTheDocument();
});
