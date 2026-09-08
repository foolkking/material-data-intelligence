import { fireEvent, render, screen, waitFor } from "@testing-library/react";
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
    const disclosure = screen.getByText("查看科学依据");
    expect(disclosure).toBeInTheDocument();
    fireEvent.click(disclosure);
    const evidence = disclosure.closest("details");
    expect(evidence).not.toBeNull();
    expect(evidence).toHaveTextContent("result_1");
    expect(evidence).toHaveTextContent("rdf.peak");
    expect(evidence).toHaveTextContent("evidence.rdf");
    expect(evidence).toHaveTextContent("version_1");
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
    expect(screen.getByRole("link", { name: "打开权威数据表" })).toHaveAttribute(
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
        ],
      },
    });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    expect(await screen.findByText("扩散系数仅在明确选择的拟合时间窗内估算，不代表无条件的长时间体相扩散系数。")).toBeInTheDocument();
    expect(screen.getByText("MSD 使用笛卡尔 x/y/z 轴，不会自动解释为晶体学 a/b/c 方向扩散。")).toBeInTheDocument();
    expect(screen.getByText("本次结果未应用质心漂移校正。")).toBeInTheDocument();
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
    expect(screen.getAllByText(/版本 version_1 · 当前版本 · 来源对象已归档/).length).toBeGreaterThanOrEqual(1);
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
    expect(await screen.findByRole("link", { name: "打开权威 Artifact" })).toHaveAttribute(
      "href",
      "/api/planner/jobs/job.rdf/artifacts/artifact.rdf/content",
    );
    expect(screen.getByRole("link", { name: "下载权威 Artifact" })).toHaveAttribute(
      "download",
      "figure.rdf.figure.json",
    );
  });

  it("creates a real attached Markdown download anchor without changing report state", async () => {
    mocks.getScientificReport.mockResolvedValue(report);
    const createObjectURL = vi.fn(() => "blob:report");
    const revokeObjectURL = vi.fn();
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectURL });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revokeObjectURL });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    await screen.findByRole("heading", { name: report.title });
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    fireEvent.click(screen.getByRole("button", { name: "导出 Markdown" }));
    expect(createObjectURL).toHaveBeenCalledOnce();
    expect(click).toHaveBeenCalledOnce();
    expect(screen.getByRole("status", { name: "报告导出状态" })).toHaveTextContent("Markdown 已准备下载");
    await waitFor(() => expect(revokeObjectURL).toHaveBeenCalledWith("blob:report"));
    click.mockRestore();
  });

  it("offers a bounded reproducibility manifest download without changing report state", async () => {
    mocks.getScientificReport.mockResolvedValue(report);
    const createObjectURL = vi.fn(() => "blob:manifest");
    const revokeObjectURL = vi.fn();
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectURL });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revokeObjectURL });
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    await screen.findByRole("heading", { name: report.title });
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    fireEvent.click(screen.getByRole("button", { name: "导出复现清单" }));
    expect(createObjectURL).toHaveBeenCalledOnce();
    expect(click).toHaveBeenCalledOnce();
    expect(screen.getByRole("status", { name: "报告导出状态" })).toHaveTextContent("复现清单已准备下载");
    await waitFor(() => expect(revokeObjectURL).toHaveBeenCalledWith("blob:manifest"));
    click.mockRestore();
  });

  it("fails closed with an accessible status when browser download support is unavailable", async () => {
    const originalCreateObjectURL = URL.createObjectURL;
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: undefined });
    mocks.getScientificReport.mockResolvedValue(report);
    render(<ScientificReportRoute projectId="project_1" reportId="agent2_report_1" />);
    await screen.findByRole("heading", { name: report.title });
    fireEvent.click(screen.getByRole("button", { name: "导出 Markdown" }));
    expect(screen.getByRole("status", { name: "报告导出状态" })).toHaveTextContent("导出失败，请稍后重试");
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: originalCreateObjectURL });
  });
});
