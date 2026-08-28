import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ScientificReportRoute } from "./ScientificReportRoute";
import { buildScientificReportMarkdown, type ScientificReportView } from "../lib/scientific-report-api";

const mocks = vi.hoisted(() => ({ getScientificReport: vi.fn() }));

vi.mock("../lib/scientific-report-api", async () => {
  const actual = await vi.importActual<typeof import("../lib/scientific-report-api")>("../lib/scientific-report-api");
  return { ...actual, getScientificReport: mocks.getScientificReport };
});
vi.mock("./ProductShell", () => ({ ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>, RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</> }));
vi.mock("./ResearchPages", () => ({ ReportReaderPage: () => <div>Legacy report</div> }));

const report: ScientificReportView = {
  report_id: "agent2_report_1",
  snapshot_id: "snapshot_1",
  project_id: "project_1",
  research_turn_id: "turn_1",
  scientific_result_snapshot_id: "result_1",
  scientific_interpretation_id: "interpretation_1",
  title: "LiFePO4 RDF 第一配位峰分析",
  relevance_at_generation: "CURRENT",
  current_effective_relevance: "CURRENT",
  grounding_status: "VALID",
  scientific_context: "LiFePO4 的 RDF 第一峰在哪里？",
  finding_count: 1,
  figure_count: 1,
  source_fingerprint: "a".repeat(64),
  created_at: "2026-08-24T12:00:00Z",
  viewer_sources: [{ source_ref: "source_1", object_id: "object_1", version_id: "version_1", object_type: "structure.crystal", display_name: "LiFePO4 结构", is_current_version: true }],
  report: {
    contract_version: "1.0",
    title: "LiFePO4 RDF 第一配位峰分析",
    research_question: "LiFePO4 的 RDF 第一峰在哪里？",
    summary: "RDF 第一峰位于 2.84 Å。",
    main_findings: [{ statement: "RDF 第一峰位于 2.84 Å。", finding_refs: ["finding.rdf"], fact_refs: ["rdf.peak"], evidence_refs: ["evidence.rdf"] }],
    primary_figures: [{ figure_ref: "figure.rdf", caption: "LiFePO4 径向分布函数", fact_refs: ["rdf.peak"], evidence_refs: ["evidence.rdf"] }],
    supporting_results: [],
    method_summary: "根据晶体结构计算径向分布函数。",
    limitations: [{ statement: "结果受有限截断范围约束。", source_refs: ["limitation.rdf"] }],
    data_sources: ["source_1"],
    evidence_refs: ["evidence.rdf"],
    reproducibility_summary: "报告绑定 exact source version。",
    omitted_supporting_items: [],
  },
};

describe("ScientificReportRoute", () => {
  beforeEach(() => mocks.getScientificReport.mockReset());

  it("renders meaning and limitations before technical provenance", async () => {
    mocks.getScientificReport.mockResolvedValue(report);
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByRole("heading", { name: report.title })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "主要发现" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "数据与方法" })).toBeInTheDocument();
    expect(screen.getAllByText("LiFePO4 结构").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/version version_1/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole("heading", { name: "限制与适用范围" })).toBeInTheDocument();
    expect(screen.getByText("结果受有限截断范围约束。")).toBeInTheDocument();
    expect(screen.getByText("复现信息")).toBeInTheDocument();
    expect(screen.queryByText(/job_|toolcall_|artifact_private/i)).toBeNull();
  });

  it("shows an explicit historical-version notice for stale reports", async () => {
    mocks.getScientificReport.mockResolvedValue({ ...report, current_effective_relevance: "STALE" });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByText("历史版本")).toBeInTheDocument();
    expect(screen.getByText(/历史数据版本/)).toBeInTheDocument();
  });

  it("does not repeat equivalent limitations from result and interpretation", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      report: { ...report.report!, limitations: [report.report!.limitations[0], { ...report.report!.limitations[0], source_refs: [] }] },
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findAllByText("结果受有限截断范围约束。")).toHaveLength(1);
  });

  it("builds a bounded Markdown export with exact report and source provenance", () => {
    const markdown = buildScientificReportMarkdown(report);
    expect(markdown).toContain(`# ${report.report!.title}`);
    expect(markdown).toContain(`ScientificResultSnapshot: ${report.scientific_result_snapshot_id}`);
    expect(markdown).toContain("LiFePO4 结构");
    expect(markdown).toContain("Evidence refs: evidence.rdf");
    expect(markdown).not.toMatch(/password|api[_ -]?key|redis:\/\/|minio/i);
  });
});
