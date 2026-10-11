import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ScientificReportRoute } from "./ScientificReportRoute";
import { buildScientificReportMarkdown, buildScientificReportReproducibilityManifest, humanizeScientificMethodSummary, type ScientificReportView } from "../lib/scientific-report-api";

const mocks = vi.hoisted(() => ({
  compareScientificReportRevisions: vi.fn(),
  getScientificReport: vi.fn(),
  listScientificReportRevisions: vi.fn(),
  replace: vi.fn(),
}));

vi.mock("../lib/scientific-report-api", async () => {
  const actual = await vi.importActual<typeof import("../lib/scientific-report-api")>("../lib/scientific-report-api");
  return {
    ...actual,
    compareScientificReportRevisions:
      mocks.compareScientificReportRevisions,
    getScientificReport: mocks.getScientificReport,
    listScientificReportRevisions: mocks.listScientificReportRevisions,
  };
});
vi.mock("../../shared/layout/ProductShell", () => ({ ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>, RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</> }));
vi.mock("../../shared/layout/ProductNavigation", async () => {
  const actual = await vi.importActual<typeof import("./ProductNavigation")>("./ProductNavigation");
  return {
    ...actual,
    useProductRouter: () => ({ replace: mocks.replace }),
  };
});
vi.mock("../../features/reports/ReportPages", () => ({ ReportReaderPage: () => <div>Legacy report</div> }));

const report: ScientificReportView = {
  report_id: "agent2_report_1",
  snapshot_id: "snapshot_1",
  project_id: "project_1",
  research_session_id: "session_1",
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
  viewer_sources: [{ source_ref: "source_1", object_id: "object_1", version_id: "version_1", object_type: "structure.crystal", display_name: "LiFePO4 结构", is_current_version: true, lifecycle_status: "ACTIVE" }],
  figure_sources: [{
    figure_ref: "figure.rdf",
    artifact_ids: ["artifact.rdf"],
    job_id: "job.rdf",
    object_id: "object-1",
    version_id: "version-1",
    object_type: "structure.crystal",
  }],
  report: {
    contract_version: "1.0",
    title: "LiFePO4 RDF 第一配位峰分析",
    research_question: "LiFePO4 的 RDF 第一峰在哪里？",
    summary: "RDF 第一峰位于 2.84 Å。",
    discussion: { text: "该峰由已提交的 RDF 曲线支持。", fact_refs: ["rdf.peak"], evidence_refs: ["evidence.rdf"] },
    conclusion: { text: "在本次来源版本与截断范围内，第一峰位于 2.84 Å。", fact_refs: ["rdf.peak"], evidence_refs: ["evidence.rdf"] },
    next_steps: { text: "可在相同来源版本上比较不同截断范围。", fact_refs: [], evidence_refs: [] },
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
  it("shows the report's bound parameters and verbatim table without a missing-material notice", async () => {
    const input = { tool_call_id: "csv-call", tool_id: "viz.inline_xy", input_origin: "USER_TEXT_DATA",
      content_hash: "a".repeat(64), resolved_parameters: { data_text: "x,signal\n0,0\n1,2\n2,1\n3,4" } };
    const view: ScientificReportView = { ...report, viewer_sources: [], figure_sources: [],
      report: { ...report.report!, primary_figures: [], data_sources: [] },
      scientific_basis: { project_id: report.project_id, result_snapshot_id: report.scientific_result_snapshot_id,
        input_origin: "USER_TEXT_DATA", parameter_inputs: [input], evidence: [], facts: [{
          fact_id: "rows", predicate: "inline.row_count", subject_ref: "input", value_text: "4", source_refs: [],
          artifact_id: "csv-table", job_id: "job", tool_id: input.tool_id, tool_call_id: input.tool_call_id,
          input_origin: "USER_TEXT_DATA", input_hash: input.content_hash,
        }],
      },
    };
    mocks.getScientificReport.mockResolvedValue(view);
    render(<ScientificReportRoute projectId={view.project_id} reportId={view.report_id} />);
    const methods = within(await screen.findByRole("region", { name: "数据与方法" }));
    expect(methods.queryByText(/未返回可展示的对象版本/)).not.toBeInTheDocument();
    expect(methods.getByText("输入参数与原始数据").closest("details")).not.toHaveAttribute("open");
    fireEvent.click(methods.getByText("输入参数与原始数据"));
    expect(methods.getByLabelText("原始输入表格").textContent).toBe(input.resolved_parameters.data_text);
    expect(methods.getByLabelText("原始输入表格")).toBeVisible();
    expect(methods.getByLabelText("原始输入表格")).toHaveAttribute("tabindex", "0");
    expect(screen.getByText("来源数据 · 1").closest("details")).toHaveTextContent("输入数据绘图 · 输入表格");
  });

  it("shows saved fact values and exact material links before technical identifiers", async () => {
    const source = { object_id: "cu-object", version_id: "cu-version", object_type: "structure.crystal", display_name: "Cu.cif" };
    const view: ScientificReportView = { ...report,
      scientific_basis: { project_id: report.project_id, result_snapshot_id: report.scientific_result_snapshot_id,
        facts: [{ fact_id: "density-cu", predicate: "rdf.number_density", subject_ref: "cu-result", value_text: "0.085023", unit: "angstrom^-3", source_refs: [source],
          artifact_id: "cu-artifact", job_id: "cu-job", artifact_name: "Cu-rdf.json" }], evidence: [] },
      report: { ...report.report!, main_findings: [{ statement: "Cu 的数密度来自已保存的 RDF 结果。", fact_refs: ["density-cu"], evidence_refs: [], finding_refs: ["finding-cu"] }] },
    };
    const before = JSON.stringify(view);
    mocks.getScientificReport.mockResolvedValue(view);
    render(<ScientificReportRoute projectId="project_1" reportId={view.report_id} />);
    const section = within(await screen.findByRole("region", { name: "主要发现" }));
    expect(section.getByText("0.085023 Å⁻³")).not.toBeVisible();
    fireEvent.click(section.getByText("查看科学依据"));
    expect(section.getByText("0.085023 Å⁻³").previousElementSibling).toHaveTextContent("数密度");
    expect(section.getByText("0.085023 Å⁻³")).toHaveAttribute("data-exact-value", "0.085023");
    expect(section.getByRole("link", { name: "Cu.cif" })).toHaveAttribute("href", "/projects/project_1/data?object=cu-object&version=cu-version");
    expect(section.getByRole("link", { name: "Cu-rdf.json" })).toHaveAttribute("href", "/api/planner/jobs/cu-job/artifacts/cu-artifact/content");
    expect(section.getByText("cu-version")).not.toBeVisible();
    fireEvent.click(section.getByText("引用与版本"));
    expect(section.getByText("cu-version")).toBeVisible();
    expect(JSON.stringify(view)).toBe(before);
  });

  it("shows a common limitation once above scoped findings while retaining their complete source statements", async () => {
    const limit = "数据为合成测试样本，不能据此断言真实材料预测能力或泛化性能。";
    const statements = ["MAE 为 0.06367252119238281。", "RMSE 为 0.07072364590422509。"];
    const findings = statements.map((statement, index) => ({ statement: statement + limit,
      finding_refs: [`finding.${index}`], fact_refs: [`fact.${index}`], evidence_refs: [`evidence.${index}`],
      reasoning_assessment: { accepted: true, scope: "当前合成回归数据", limitations: [limit] },
    }));
    const view = { ...report, report: { ...report.report!, main_findings: findings, discussion: null } };
    mocks.getScientificReport.mockResolvedValue(view);
    render(<ScientificReportRoute projectId="project_1" reportId={view.report_id} />);
    const note = await screen.findByRole("note", { name: "共同限制" });
    expect(note).toHaveTextContent(limit);
    const section = screen.getByRole("region", { name: "主要发现" });
    const items = within(section).getAllByRole("listitem");
    expect(note.compareDocumentPosition(items[0]) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    items.forEach((item, index) => {
      expect(item.querySelector("p")!.textContent).not.toContain(limit);
      fireEvent.click(within(item).getByText("查看科学依据"));
      fireEvent.click(within(item).getByText("引用与版本"));
      expect(within(item).getByText(findings[index].statement)).toBeVisible();
      expect(within(item).getByText(`fact.${index}`)).toBeVisible();
    });
    expect(screen.queryByRole("link", { name: "科学讨论" })).not.toBeInTheDocument();
    const markdown = buildScientificReportMarkdown(view).split("## 主要发现")[1].split("## 主要图表")[0];
    expect(markdown.split(limit)).toHaveLength(2);
    statements.forEach(statement => expect(markdown).toContain(statement));
    expect(view.report.main_findings).toEqual(findings);
  });

  it("uses readable narrative in the page and export while leaving the research question intact", async () => {
    const question = "electron_count 是什么？3.1000000000000005 electron 与 source_native/field.json 的关系？";
    const view: ScientificReportView = { ...report, report: { ...report.report!,
      research_question: question,
      summary: "积分语义为 electron_count，归一化语义为 source_native；不能推断成键。",
      reproducibility_summary: "本报告绑定 immutable ScientificResultSnapshot、validated Interpretation 与其 exact source versions。",
    } };
    mocks.getScientificReport.mockResolvedValue(view);
    render(<ScientificReportRoute projectId="project_1" reportId={view.report_id} />);
    await screen.findByText("积分表示电子数，归一化沿用源数据；不能推断成键。");
    expect(screen.getByText(question)).toBeInTheDocument();
    expect(screen.getByText("本报告绑定 不可变的科学结果快照、已验证的解读 与其 精确来源版本。")).toBeInTheDocument();
    const markdown = buildScientificReportMarkdown(view);
    expect(markdown).toContain(question);
    expect(markdown).toContain("积分表示电子数，归一化沿用源数据；不能推断成键。");
  });

  it("keeps chapter order aligned with the document and presents each figure once", async () => {
    mocks.getScientificReport.mockResolvedValue(report);
    render(<ScientificReportRoute projectId="project_1" reportId={report.report_id} />);
    await screen.findByRole("heading", { name: report.title });
    const chapters = within(screen.getByRole("navigation", { name: "报告章节" })).getAllByRole("link");
    const targets = chapters.map(link => document.getElementById(link.getAttribute("href")!.slice(1))!);
    expect(targets.every(Boolean)).toBe(true);
    targets.slice(1).forEach((target, index) => expect(targets[index].compareDocumentPosition(target) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy());
    expect(screen.getAllByText("LiFePO4 径向分布函数")).toHaveLength(1);
  });

  it("does not assign the first report input to a finding or a figure with no exact source", async () => {
    mocks.getScientificReport.mockResolvedValue({ ...report, figure_sources: [], viewer_sources: [
      ...report.viewer_sources!, { ...report.viewer_sources![0], source_ref: "source_2", object_id: "object_2", version_id: "version_2", display_name: "另一份同源数据" },
    ] });
    render(<ScientificReportRoute projectId="project_1" reportId={report.report_id} />);
    const evidence = within(await screen.findByRole("region", { name: "主要发现" })).getByText("查看科学依据").closest("details")!;
    expect(evidence).not.toHaveTextContent("version_1");
    expect(evidence).not.toHaveTextContent("version_2");
    expect(evidence).toHaveTextContent("rdf.peak");
    const figures = screen.getByRole("region", { name: "主要图表" });
    expect(figures.querySelector('a[href*="object="]')).toBeNull();
    expect(within(figures).getByRole("link")).toHaveAttribute("href", "/projects/project_1/research/session_1?turn=turn_1");
  });

  it("keeps every unavailable report reference and opens only an unambiguous figure source", async () => {
    const figureSource = { ...report.figure_sources![0], artifact_ids: [] };
    mocks.getScientificReport.mockResolvedValue({ ...report, figure_sources: [figureSource], report: {
      ...report.report!, evidence_refs: Array.from({ length: 15 }, (_, index) => `evidence-${index}`),
    } });
    const view = render(<ScientificReportRoute projectId="project_1" reportId={report.report_id} />);
    const evidence = await screen.findByText("科学依据 · 15");
    fireEvent.click(evidence);
    const records = within(evidence.closest("details")!);
    expect(records.getByRole("status")).toHaveTextContent("15 项来源记录暂不可读取。");
    fireEvent.click(records.getByText("引用与版本"));
    for (let index = 0; index < 15; index += 1) expect(records.getByText(`evidence-${index}`)).toBeVisible();
    expect(within(screen.getByRole("region", { name: "主要图表" })).getByRole("link")).toHaveAttribute("href", "/projects/project_1/data?object=object-1&version=version-1");
    mocks.getScientificReport.mockResolvedValue({ ...report, report_id: "ambiguous", figure_sources: [figureSource, figureSource] });
    view.rerender(<ScientificReportRoute projectId="project_1" reportId="ambiguous" />);
    await screen.findByRole("heading", { name: report.title });
    expect(within(screen.getByRole("region", { name: "主要图表" })).getByRole("link")).toHaveAttribute("href", "/projects/project_1/research/session_1?turn=turn_1");
  });

  it("uses human scientific method names instead of internal capability IDs", () => {
    expect(
      humanizeScientificMethodSummary(
        "使用材料数据集探索工具（capability: data.materials_explorer, version 1.0）获取属性。",
      ),
    ).toBe("使用材料数据集探索（版本 1.0）获取属性。");
    expect(
      humanizeScientificMethodSummary(
        "使用 data.materials_explorer 工具（版本 1.0）获取属性。",
      ),
    ).toBe("使用材料数据集探索（版本 1.0）获取属性。");
  });
  beforeEach(() => {
    mocks.getScientificReport.mockReset();
    mocks.compareScientificReportRevisions.mockReset();
    mocks.listScientificReportRevisions.mockReset();
    mocks.replace.mockReset();
    mocks.listScientificReportRevisions.mockResolvedValue({
      revision_group_id: report.report_id,
      current_report_id: report.report_id,
      items: [report],
      count: 1,
    });
  });

  it("redirects a report opened under the wrong project to its authoritative project route", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      project_id: "project_authoritative",
    });
    render(
      <ScientificReportRoute
        projectId="project_route_guess"
        reportId={report.report_id}
      />,
    );

    expect(
      await screen.findByText("正在返回报告所属项目…"),
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(mocks.replace).toHaveBeenCalledWith(
        "/projects/project_authoritative/reports/agent2_report_1",
      );
    });
    expect(
      screen.queryByRole("heading", { name: report.title }),
    ).toBeNull();
  });

  it("opens legacy Job report links without probing the modern report endpoint", async () => {
    render(
      <ScientificReportRoute
        projectId="project_1"
        reportId="job_dc63f3f5d57742009c6be09e"
      />,
    );

    expect(await screen.findByText("Legacy report")).toBeInTheDocument();
    expect(mocks.getScientificReport).not.toHaveBeenCalled();
  });

  it("retries an unavailable modern report in place without falling back to unrelated legacy content", async () => {
    mocks.getScientificReport.mockRejectedValueOnce(Object.assign(new Error("private upstream error"), {status: 404})).mockResolvedValueOnce(report);
    render(<ScientificReportRoute projectId="project_1" reportId={report.report_id} />);
    expect(await screen.findByRole("heading", {name: "报告暂时无法打开"})).toBeInTheDocument();
    expect(screen.queryByText("Legacy report")).not.toBeInTheDocument();
    expect(screen.queryByText(/private upstream/u)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", {name: "重新加载报告"}));
    expect(await screen.findByRole("heading", {name: report.title})).toBeInTheDocument();
    expect(screen.queryByRole("button", {name: "重新加载报告"})).not.toBeInTheDocument();
  });

  it("provides recovery instead of a blank page when the response has no report body", async () => {
    mocks.getScientificReport.mockResolvedValue({...report, report: undefined});
    render(<ScientificReportRoute projectId="project_1" reportId={report.report_id} />);
    expect(await screen.findByRole("button", {name: "重新加载报告"})).toBeInTheDocument();
  });

  it("times out a stalled report request and ignores its late response", async () => {
    vi.useFakeTimers();
    try {
      let finish!: (value: ScientificReportView) => void;
      mocks.getScientificReport.mockReturnValueOnce(new Promise(resolve => {finish = resolve;}));
      render(<ScientificReportRoute projectId="project_1" reportId={report.report_id} />);
      await act(async () => {await vi.advanceTimersByTimeAsync(10_000);});
      expect(screen.getByRole("button", {name: "重新加载报告"})).toBeInTheDocument();
      expect(mocks.getScientificReport.mock.calls[0][1].aborted).toBe(true);
      await act(async () => finish(report));
      expect(screen.queryByRole("heading", {name: report.title})).not.toBeInTheDocument();
    } finally { vi.useRealTimers(); }
  });

  it("resets report identity when navigating from legacy to modern and between modern reports", async () => {
    const {rerender} = render(<ScientificReportRoute projectId="project_1" reportId="job_old" />);
    expect(await screen.findByText("Legacy report")).toBeInTheDocument();
    mocks.getScientificReport.mockResolvedValueOnce(report);
    rerender(<ScientificReportRoute projectId="project_1" reportId={report.report_id} />);
    expect(await screen.findByRole("heading", {name: report.title})).toBeInTheDocument();
    let finish!: (value: ScientificReportView) => void;
    mocks.getScientificReport.mockReturnValueOnce(new Promise(resolve => {finish = resolve;}));
    rerender(<ScientificReportRoute projectId="project_1" reportId="agent2_report_next" />);
    expect(screen.queryByRole("heading", {name: report.title})).not.toBeInTheDocument();
    expect(screen.getByText("正在打开科学报告…")).toBeInTheDocument();
    await act(async () => finish({...report, report_id: "agent2_report_next", report: {...report.report!, title: "新的报告"}}));
    expect(screen.getByRole("heading", {name: "新的报告"})).toBeInTheDocument();
  });

  it("keeps body and revision links readable through comparison failure and failed retries", async () => {
    mocks.getScientificReport.mockResolvedValue({...report, revision_number: 2});
    mocks.listScientificReportRevisions.mockResolvedValue({items: [{...report, revision_number: 2}, {...report, report_id: "agent2_report_old", revision_number: 1}], count: 2});
    mocks.compareScientificReportRevisions.mockRejectedValueOnce(new Error("offline"));
    render(<ScientificReportRoute projectId="project_1" reportId={report.report_id} />);
    expect(await screen.findByText(/未能读取：版本比较/u)).toBeInTheDocument();
    expect(screen.getByRole("heading", {name: report.title})).toBeInTheDocument();
    expect(screen.getByRole("link", {name: "第 1 版"})).toBeInTheDocument();
    mocks.listScientificReportRevisions.mockRejectedValueOnce(new Error("offline"));
    mocks.compareScientificReportRevisions.mockResolvedValue({base_revision_number: 1, scientific_authority_unchanged: true, source_versions_unchanged: true, changed_sections: [], added_findings: [], removed_findings: []});
    fireEvent.click(screen.getByRole("button", {name: "重新加载版本信息"}));
    expect(await screen.findByText(/未能读取：版本记录/u)).toBeInTheDocument();
    expect(screen.getByRole("link", {name: "第 1 版"})).toBeInTheDocument();
    expect(screen.getByText("与第 1 版比较")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("button", {name: "重新加载版本信息"})).toBeEnabled());
    fireEvent.click(screen.getByRole("button", {name: "重新加载版本信息"}));
    await waitFor(() => expect(screen.queryByRole("button", {name: "重新加载版本信息"})).not.toBeInTheDocument());
    expect(mocks.getScientificReport).toHaveBeenCalledTimes(1);
  });

  it("renders meaning and limitations before technical provenance", async () => {
    mocks.getScientificReport.mockResolvedValue(report);
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByRole("heading", { name: report.title })).toBeInTheDocument();
    expect(document.querySelectorAll("main")).toHaveLength(0);
    expect(screen.getByRole("region", { name: "科学报告阅读器" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "主要发现" })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "报告章节" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "主要发现" })).toHaveAttribute("href", "#report-agent2_report_1-findings");
    expect(screen.getByRole("heading", { name: "数据与方法" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "科学讨论" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "结论" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "后续工作建议" })).toBeInTheDocument();
    expect(screen.getAllByText("LiFePO4 结构").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/版本 version_1/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole("heading", { name: "限制与适用范围" })).toBeInTheDocument();
    expect(screen.getByText("结果受有限截断范围约束。")).toBeInTheDocument();
    expect(screen.getByText("复现信息")).toBeInTheDocument();
    expect(screen.getByText("技术详情（用于复现与排查）")).toBeInTheDocument();
    const technicalDetails = screen.getByText("技术详情（用于复现与排查）").closest("details");
    expect(technicalDetails).not.toBeNull();
    expect(technicalDetails).toHaveTextContent("result_1");
    expect(technicalDetails).toHaveTextContent("version_1");
    expect(screen.queryByText(/job_|toolcall_|artifact_private/i)).toBeNull();
  });

  it("keeps each finding traceable to its exact Result and evidence refs", async () => {
    mocks.getScientificReport.mockResolvedValue(report);
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);

    expect(await screen.findByRole("heading", { name: "主要发现" })).toBeInTheDocument();
    const disclosure = within(screen.getByRole("region", { name: "主要发现" })).getByText("查看科学依据");
    expect(disclosure).toBeInTheDocument();
    fireEvent.click(disclosure);
    const evidence = disclosure.closest("details");
    expect(evidence).not.toBeNull();
    expect(evidence).toHaveTextContent("result_1");
    expect(evidence).toHaveTextContent("rdf.peak");
    expect(evidence).toHaveTextContent("evidence.rdf");
    expect(evidence).toHaveTextContent("1 项引用事实、1 项来源记录暂不可读取。");
    expect(evidence).not.toHaveTextContent("version_1");
  });

  it("keeps unrounded finding values available inside the evidence disclosure", async () => {
    const statement = "原始坐标为 (9.308486082, 3.968153027, 14.972857668) Å。";
    mocks.getScientificReport.mockResolvedValue({ ...report, report: { ...report.report,
      main_findings: [{ ...report.report!.main_findings[0], statement }],
    } });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    const disclosure = within(await screen.findByRole("region", { name: "主要发现" })).getByText("查看科学依据");
    expect(disclosure.closest("details")).not.toHaveAttribute("open");
    fireEvent.click(disclosure);
    expect(disclosure.closest("details")).toHaveTextContent("原始表述（保留数值精度）");
    expect(disclosure.closest("details")).toHaveTextContent(statement);
    expect(screen.getByText("原始坐标为 (9.308486, 3.968153, 14.97286) Å。")).toBeInTheDocument();
  });

  it("offers an accessible chapter jump control for narrow report layouts", async () => {
    mocks.getScientificReport.mockResolvedValue(report);
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);

    const chapterSelect = await screen.findByRole("combobox", {
      name: "跳转报告章节",
    });
    const target = document.getElementById("report-agent2_report_1-findings");
    expect(chapterSelect).toBeInTheDocument();
    expect(chapterSelect).toHaveDisplayValue("选择章节");
    expect(target).not.toBeNull();
    target!.scrollIntoView = vi.fn();

    fireEvent.change(chapterSelect, {
      target: { value: "report-agent2_report_1-findings" },
    });

    expect(target!.scrollIntoView).toHaveBeenCalledWith({
      behavior: "smooth",
      block: "start",
    });
    expect(chapterSelect).toHaveDisplayValue("选择章节");
    expect(target).toHaveFocus();
    fireEvent.change(chapterSelect, { target: { value: "report-agent2_report_1-findings" } });
    const link = screen.getByRole("link", { name: "主要发现" });
    fireEvent.click(link);
    fireEvent.click(link);
    expect(target!.scrollIntoView).toHaveBeenCalledTimes(4);
    fireEvent.click(link, { ctrlKey: true });
    expect(target!.scrollIntoView).toHaveBeenCalledTimes(4);
  });

  it("switches immutable revisions and compares only the communication layer", async () => {
    const revision = {
      ...report,
      report_id: "agent2_report_2",
      snapshot_id: "snapshot_2",
      revision_group_id: report.report_id,
      parent_report_id: report.report_id,
      parent_snapshot_id: report.snapshot_id,
      revision_number: 2,
      revision_reason: "USER_REVISION" as const,
      title: "LiFePO4 RDF 第一配位峰分析（修订 2）",
      report: {
        ...report.report!,
        title: "LiFePO4 RDF 第一配位峰分析（修订 2）",
      },
    };
    mocks.getScientificReport.mockResolvedValue(revision);
    mocks.listScientificReportRevisions.mockResolvedValue({
      revision_group_id: report.report_id,
      current_report_id: revision.report_id,
      items: [
        { ...report, revision_number: 1 },
        revision,
      ],
      count: 2,
    });
    mocks.compareScientificReportRevisions.mockResolvedValue({
      revision_group_id: report.report_id,
      base_report_id: report.report_id,
      report_id: revision.report_id,
      base_revision_number: 1,
      revision_number: 2,
      scientific_authority_unchanged: true,
      source_versions_unchanged: true,
      changed_sections: ["title"],
      added_findings: [],
      removed_findings: [],
    });
    render(
      <ScientificReportRoute
        projectId="project_1"
        reportId={revision.report_id}
      />,
    );

    expect(
      await screen.findByRole("heading", { name: "2 个报告版本" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "第 1 版" })).toHaveAttribute(
      "href",
      "/projects/project_1/reports/agent2_report_1",
    );
    expect(screen.getByRole("link", { name: "第 2 版" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    fireEvent.click(screen.getByText("与第 1 版比较"));
    expect(await screen.findByText(/科学权威未改变/)).toBeInTheDocument();
    expect(screen.getByText(/沟通层变化：title/)).toBeInTheDocument();
  });

  it("normalizes legacy narrative punctuation without changing report facts", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      report: { ...report.report!, discussion: { ...report.report!.discussion!, text: "第一项已验证。；第二项已验证。。" } },
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByText("第一项已验证；第二项已验证。")).toBeInTheDocument();
    expect(screen.queryByText(/。；|。。/)).toBeNull();
  });

  it("uses exact viewer provenance for the source disclosure count and labels", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      report: { ...report.report!, data_sources: [] },
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByText("来源数据 · 1")).toBeInTheDocument();
    expect(screen.getAllByText(/LiFePO4 结构/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/精确版本 version_1/).length).toBeGreaterThanOrEqual(1);
  });

  it("renders persisted ScientificResult tables as bounded report entry points", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      table_sources: [{
        table_ref: "diffusion.diagnostic",
        title: "扩散拟合诊断",
        artifact_ids: ["artifact.diffusion.table"],
        job_id: "job.diffusion",
        source_refs: [{ object_id: "object_1", version_id: "version_1", object_type: "trajectory.extxyz" }],
      }],
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByRole("heading", { name: "主要数据表" })).toBeInTheDocument();
    expect(screen.getByText("扩散拟合诊断")).toBeInTheDocument();
    expect(screen.getByText("diffusion.diagnostic")).toBeInTheDocument();
    expect(within(screen.getByRole("region", { name: "主要数据表" })).getByRole("link", { name: "查看源文件" })).toHaveAttribute(
      "href",
      "/api/planner/jobs/job.diffusion/artifacts/artifact.diffusion.table/content",
    );
    expect(screen.getAllByText(/精确版本 version_1/).length).toBeGreaterThan(0);
  });

  it("keeps trajectory limitations in the same user-facing scientific language", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      report: {
        ...report.report!,
        limitations: [
          { statement: "Diffusion is estimated only over the explicitly selected fit window and is not an unconditional long-time bulk diffusion coefficient.", source_refs: [] },
          { statement: "MSD uses Cartesian x/y/z axes and is not automatically crystallographic a/b/c diffusion.", source_refs: [] },
          { statement: "No center-of-mass drift correction is applied.", source_refs: [] },
          { statement: "未应用质心漂移校正。", source_refs: [] },
          { statement: "MSD使用笛卡尔x/y/z轴，非自动晶格a/b/c扩散。", source_refs: [] },
          { statement: "拟合窗口时长0.08 ps，不能成立扩散系数。", source_refs: [] },
        ],
      },
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByText("扩散系数仅在明确选择的拟合时间窗内估算，不代表无条件的长时间体相扩散系数。")).toBeInTheDocument();
    expect(screen.getByText("MSD 使用笛卡尔 x/y/z 轴，不会自动解释为晶体学 a/b/c 方向扩散。")).toBeInTheDocument();
    expect(screen.getByText("本次结果未应用质心漂移校正。")).toBeInTheDocument();
    const limitations = within(screen.getByRole("region", { name: "限制与适用范围" }));
    expect(limitations.getAllByRole("listitem")).toHaveLength(4);
    expect(limitations.getByText("拟合窗口时长0.08 ps，不能成立扩散系数。")).toBeInTheDocument();
  });

  it("shows an explicit historical-version notice for stale reports", async () => {
    mocks.getScientificReport.mockResolvedValue({ ...report, current_effective_relevance: "STALE" });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByText("历史版本")).toBeInTheDocument();
    expect(screen.getByText(/历史数据版本/)).toBeInTheDocument();
  });

  it("discloses archived lifecycle state while keeping an exact ResearchTurn route", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      lifecycle_status: "ARCHIVED",
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByText("已归档报告")).toBeInTheDocument();
    expect(screen.getByText(/科学结果、证据与精确源版本保持可读/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "打开来源研究" })).toHaveAttribute(
      "href",
      "/projects/project_1/research/session_1?turn=turn_1",
    );
  });

  it("discloses an archived scientific source independently from report lifecycle", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      lifecycle_status: "ACTIVE",
      viewer_sources: report.viewer_sources?.map((source) => ({
        ...source,
        lifecycle_status: "ARCHIVED" as const,
      })),
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect((await screen.findAllByText(/来源对象已归档/)).length).toBeGreaterThan(0);
    expect(screen.queryByText("已归档报告")).toBeNull();
    expect(within(screen.getByRole("region", { name: "数据与方法" })).getByText(/当前版本 · 来源对象已归档/)).toBeVisible();
    expect(screen.getByText("来源数据 · 1").closest("details")).toHaveTextContent("精确版本 version_1");
  });

  it("keeps a bounded turn-only fallback for historical reports without a session identity", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      research_session_id: null,
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByRole("link", { name: "打开来源研究" })).toHaveAttribute(
      "href",
      "/projects/project_1/research?turn=turn_1",
    );
  });

  it("discloses recycle-bin state without implying scientific deletion", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      lifecycle_status: "TRASHED",
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByText("回收站报告")).toBeInTheDocument();
    expect(screen.getByText(/受保护的科学结果、证据与精确源版本未被删除/)).toBeInTheDocument();
  });

  it("does not repeat equivalent limitations from result and interpretation", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      report: { ...report.report!, limitations: [report.report!.limitations[0], { ...report.report!.limitations[0], source_refs: [] }] },
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findAllByText("结果受有限截断范围约束。")).toHaveLength(1);
  });

  it("renders persisted canonical limitations in the same product language as Research presentation", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      report: {
        ...report.report!,
        limitations: [{ statement: "The current band Artifact does not provide eigenvectors or animation authority.", source_refs: ["limitation.band"] }],
      },
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByText("当前声子能带 Artifact 不包含特征向量，因此不提供模式动画依据。")).toBeInTheDocument();
    expect(screen.queryByText("The current band Artifact does not provide eigenvectors or animation authority.")).toBeNull();
  });

  it("keeps internal fact and evidence identifiers out of the readable report body", async () => {
    mocks.getScientificReport.mockResolvedValue({
      ...report,
      report: {
        ...report.report!,
        summary: "结果事实 fact.abc123 的值为 0.6 eV，来自 evidence.xyz。",
        discussion: {
          text: "结果事实 fact.abc123 的值为 0.6 eV，来自 evidence.xyz（step_1-table_json）。",
          fact_refs: ["rdf.peak"],
          evidence_refs: ["evidence.rdf"],
        },
        conclusion: {
          text: "结果事实 fact.abc123 的值为 0.6 eV，来自 evidence.xyz。",
          fact_refs: ["rdf.peak"],
          evidence_refs: ["evidence.rdf"],
        },
        main_findings: [{
          statement: "结果事实 fact.abc123 的值为 0.6 eV，来自 evidence.xyz。",
          finding_refs: ["finding.rdf"],
          fact_refs: ["rdf.peak"],
          evidence_refs: ["evidence.rdf"],
        }],
      },
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect((await screen.findAllByText("结果事实 的值为 0.6 eV，已绑定本次分析证据。")).length).toBeGreaterThan(0);
    expect(screen.queryByText(/fact\.abc123|evidence\.xyz|step_1-table_json/)).toBeNull();
  });

  it("builds a bounded Markdown export with exact report and source provenance", () => {
    const archivedSourceReport = {
      ...report,
      viewer_sources: report.viewer_sources?.map((source) => ({
        ...source,
        lifecycle_status: "ARCHIVED" as const,
      })),
    };
    const markdown = buildScientificReportMarkdown(archivedSourceReport);
    expect(markdown).toContain(`# ${report.report!.title}`);
    expect(markdown).toContain(`ScientificResultSnapshot: ${report.scientific_result_snapshot_id}`);
    expect(markdown).toContain("LiFePO4 结构");
    expect(markdown).toContain("来源对象已归档");
    expect(markdown).toContain("## 科学讨论");
    expect(markdown).toContain("## 结论");
    expect(markdown).toContain("## 后续工作建议");
    expect(markdown).toContain("Artifacts: artifact.rdf");
    expect(markdown).toContain("exact source object-1 / version version-1");
    expect(markdown).toContain("Evidence refs: evidence.rdf");
    expect(markdown).not.toMatch(/password|api[_ -]?key|redis:\/\/|minio/i);
  });

  it("builds a non-executable reproducibility manifest with exact identities", () => {
    const manifest = JSON.parse(buildScientificReportReproducibilityManifest(report)) as Record<string, any>;
    expect(manifest.schema_version).toBe("mdi.reproducibility-manifest/1.0");
    expect(manifest.report.scientific_result_snapshot_id).toBe(report.scientific_result_snapshot_id);
    expect(manifest.scientific_sources[0]).toMatchObject({
      object_id: "object_1",
      version_id: "version_1",
      lifecycle_status: "ACTIVE",
    });
    expect(manifest.figures[0].artifact_ids).toEqual(["artifact.rdf"]);
    expect(JSON.stringify(manifest)).not.toMatch(/password|api[_ -]?key|redis:\/\/|minio|javascript:/i);
  });

  it("opens a persisted Figure Artifact through the secured content route", async () => {
    mocks.getScientificReport.mockResolvedValue(report);
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByRole("link", { name: "查看源文件" })).toHaveAttribute(
      "href",
      "/api/planner/jobs/job.rdf/artifacts/artifact.rdf/content",
    );
    expect(screen.getByRole("link", { name: "下载" })).toHaveAttribute(
      "download",
      "figure.rdf.figure.json",
    );
  });

  it.each([["导出 Markdown", "markdown"], ["导出复现清单", "manifest"], ["导出 ZIP（含图表）", "zip"]])("offers %s through an authorized HTTP download while preserving the report", async (label, format) => {
    mocks.getScientificReport.mockResolvedValue(report);
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    await screen.findByRole("heading", { name: report.title });
    const link = screen.getByRole("link", { name: label });
    expect(link).toHaveAttribute("href", `/downloads/scientific-reports/agent2_report_1/${format}`);
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener");
    expect(link).not.toHaveAttribute("download");
    expect(screen.queryByRole("status", { name: "报告导出状态" })).toBeNull();
  });
});


it("keeps result files distinct from scientific tables in reading and exports", async () => {
  const view: ScientificReportView = { ...report, table_sources: [], file_sources: [
    { artifact_id: "trajectory_payload", job_id: "job_exact", title: "轨迹结果文件" },
    { artifact_id: "trajectory_manifest", job_id: "job_exact", title: "轨迹结果文件" },
  ] };
  mocks.getScientificReport.mockResolvedValue(view);
  mocks.listScientificReportRevisions.mockResolvedValue({ items: [], count: 0 });
  render(<ScientificReportRoute projectId="project_1" reportId={report.report_id} />);
  expect(await screen.findByText("结果文件 · 2 项")).toBeInTheDocument();
  expect(screen.queryByRole("heading", { name: "主要数据表" })).not.toBeInTheDocument();
  fireEvent.click(screen.getByText("结果文件 · 2 项"));
  expect(within(screen.getByText("结果文件 · 2 项").closest("details")!).getAllByRole("link", { name: "查看源文件" }).map((link) => link.getAttribute("href"))).toEqual([
    "/api/planner/jobs/job_exact/artifacts/trajectory_payload/content",
    "/api/planner/jobs/job_exact/artifacts/trajectory_manifest/content",
  ]);
  expect(buildScientificReportMarkdown(view)).toContain("## 结果文件");
  expect(JSON.parse(buildScientificReportReproducibilityManifest(view)).result_files).toEqual([
    { artifact_id: "trajectory_payload", job_id: "job_exact" },
    { artifact_id: "trajectory_manifest", job_id: "job_exact" },
  ]);
});


it("exports every table artifact and exact version without inventing missing sources", () => {
  const view: ScientificReportView = { ...report, table_sources: [
    { table_ref: "table.samples", title: "样本结果", artifact_ids: ["artifact.one", "artifact.two"], job_id: "job.tables", source_refs: [
      { object_id: "object.one", version_id: "version.old", object_type: "data.table" },
      { object_id: "object.two", version_id: "version.other", object_type: "data.table" },
    ] },
    { table_ref: "table.unavailable", artifact_ids: [] },
  ] };
  const original = JSON.stringify(view);
  const markdown = buildScientificReportMarkdown(view);
  expect(markdown).toContain("## 主要数据表");
  expect(markdown).toContain("样本结果 (table.samples)");
  expect(markdown).toContain("Artifacts: artifact.one, artifact.two");
  expect(markdown).toContain("Job: job.tables");
  expect(markdown).toContain("exact source object.one / version version.old (data.table)");
  expect(markdown).toContain("exact source object.two / version version.other (data.table)");
  expect(markdown).toContain("table.unavailable (table.unavailable)");
  const manifest = JSON.parse(buildScientificReportReproducibilityManifest(view));
  expect(manifest.tables).toEqual([
    { table_ref: "table.samples", artifact_ids: ["artifact.one", "artifact.two"], job_id: "job.tables", source_refs: view.table_sources![0].source_refs },
    { table_ref: "table.unavailable", artifact_ids: [], job_id: null, source_refs: [] },
  ]);
  expect(JSON.stringify(view)).toBe(original);
  expect(JSON.parse(buildScientificReportReproducibilityManifest({ ...view, table_sources: undefined })).tables).toEqual([]);
});
