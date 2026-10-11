import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { savedPeriodicTableFixture } from "../../scientific-viewers/workspace/saved-periodic-table.fixture";
import { localEnvironmentArtifactFixture } from "../../scientific-viewers/workspace/saved-local-environment.fixture";
import {
  ScientificReportArtifactPreview,
  scientificReportTableRowKeys,
} from "./ScientificReportArtifactPreview";

const getPlannerArtifactContent = vi.hoisted(() => vi.fn());

vi.mock("../lib/planner-api", () => ({ getPlannerArtifactContent }));
vi.mock("../../scientific-viewers/workspace/WorkspaceGenericPlot", () => ({ WorkspaceGenericPlot: ({ content }: { content: unknown }) => <div data-testid="controlled-plot">{JSON.stringify(content)}</div> }));
vi.mock("../../scientific-viewers/LazyScientificViewers", () => ({ LazyScientificResultViewer: (props: unknown) => <div data-testid="bound-volume-viewer">{JSON.stringify(props)}</div> }));

function savedSvg(image: HTMLElement) {
  const src = image.getAttribute("src")!;
  return new DOMParser().parseFromString(decodeURIComponent(src.slice(src.indexOf(",") + 1)), "image/svg+xml");
}

describe("ScientificReportArtifactPreview", () => {
  it("opens the exact saved polyhedron with rotation and vertex data in a report", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify(localEnvironmentArtifactFixture().content)).buffer);
    render(<ScientificReportArtifactPreview jobId="poly-job" artifactId="poly" kind="figure" title="配位多面体" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("heading", { name: "位点 0 · 四面体" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /4 个近邻顶点，4 个已保存三角面/u })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "XZ" }));
    expect(screen.getByRole("button", { name: "XZ" })).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(screen.getByText("顶点与周期近邻（4）"));
    expect(screen.getByRole("region", { name: "多面体顶点数据" })).toBeVisible();
    expect(screen.queryByRole("button", { name: "选中配位环境" })).toBeNull();
    expect(screen.queryByTestId("controlled-plot")).toBeNull();
  });
  it("uses the same scientific unit symbols in saved conversion report tables", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      schemaVersion: "mdi.project.parameter-table/1.0", artifactType: "reference.convert_units", sampleAnalysis: false,
      rows: [{ "原数值": 0.5, "原单位": "nm", "换算结果": 5, "目标单位": "angstrom" }],
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="conversion-job" artifactId="conversion" kind="table" title="单位换算" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    const table = await screen.findByRole("table");
    expect(within(table).getByRole("cell", { name: "Å" })).toBeInTheDocument();
    expect(within(table).getByRole("cell", { name: "5" })).toBeInTheDocument();
  });

  it("searches all directed RDF pairs and reaches their final saved bin", async () => {
    const r = Array.from({ length: 25 }, (_, i) => i + 0.5);
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      artifactType: "structure.rdf", schema_version: "phase10e7.rdf.v1",
      rdf: { r_angstrom: r, g_r: r.map(() => 0), counts: r.map(() => 0) },
      partial_rdf: [{ center_element: "Na", neighbor_element: "Cl", r_angstrom: r,
        g_r: r.map((_, i) => i === 24 ? 12.123456789012345 : 0), counts: r.map((_, i) => i === 24 ? 126 : 0) }],
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="rdf-job" artifactId="rdf" kind="table" title="RDF" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByText("显示 1–24 / 50 行")).toBeInTheDocument();
    fireEvent.change(screen.getByRole("searchbox", { name: "搜索表格内容" }), { target: { value: "Na → Cl" } });
    expect(screen.getByText("匹配 25 / 50 行，当前 1–24")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "下一页" }));
    const table = screen.getByRole("table");
    expect(within(table).getAllByRole("row")).toHaveLength(2);
    expect(within(table).getByRole("cell", { name: "24.5" })).toBeInTheDocument();
    expect(within(table).getByRole("cell", { name: "12.123456789012344" })).toBeInTheDocument();
    expect(within(table).getByRole("cell", { name: "126" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "下一页" })).toBeDisabled();
  });

  it.each(["sunburst", "treemap"])("previews saved %s identities as an inert report image", async type => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      data: [{ type, ids: ["root", "root/Cu"], labels: ["Cu", "Cu"], parents: ["", "root"], values: [2, 2], branchvalues: "total" }],
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="hierarchy-job" artifactId={type} kind="figure" title="化学体系" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    const image = await screen.findByRole("img", { name: "化学体系持久化数据预览" });
    expect(savedSvg(image).querySelector('[data-node="root/Cu"]')?.getAttribute("data-parent")).toBe("root");
    expect(savedSvg(image).querySelectorAll("[data-node-index]")).toHaveLength(2);
    expect(screen.queryByTestId("controlled-plot")).not.toBeInTheDocument();
    expect(screen.queryByText("坐标轴来源")).not.toBeInTheDocument();
  });

  it("previews saved fractional element counts as a report image with the correct scale", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      artifactType: "composition.elements_hist", chartType: "bar", countMode: "fractional", elementCount: 2,
      bars: [{ element: "Fe", count: 0.5, fraction: 0.5 }, { element: "O", count: 0.5, fraction: 0.5 }],
      plotlyFigure: { data: [{ type: "bar", x: ["Fe", "O"], y: [0.5, 0.5] }], layout: { yaxis: { type: "log" } } },
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="elements-job" artifactId="elements" kind="figure" title="元素计数" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    const image = await screen.findByRole("img", { name: "元素计数持久化数据预览" });
    expect(savedSvg(image).querySelector('[data-element="Fe"]')?.getAttribute("data-value")).toBe("0.5");
    expect(screen.queryByTestId("controlled-plot")).not.toBeInTheDocument();
    expect(screen.getByText("Y 轴 · 分数贡献总和（对数刻度）")).toBeInTheDocument();
  });

  it("previews saved correlation pairs including zero and missing coefficients", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      chartType:"correlation_heatmap", columns:["A","B","constant"],
      matrix:[[1,0,null],[0,1,null],[null,null,null]],
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="correlation-job" artifactId="matrix" kind="table" title="相关系数" />);
    fireEvent.click(screen.getByRole("button", {name:"在报告内查看"}));
    const table=await screen.findByRole("table");
    expect(within(table).getAllByRole("row")).toHaveLength(10);
    const rows=within(table).getAllByRole("row").map(row=>row.textContent);
    expect(rows).toContain("AB0"); expect(rows).toContain("Aconstant—");
    expect(screen.queryByText(/暂无可预览/)).not.toBeInTheDocument();
  });

  it("previews saved numeric summaries at original precision", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      rowCount:4,numericColumns:{energy:{count:4,mean:0.12345678901234568,min:0,max:0.4}},categoricalColumns:{},
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="summary-job" artifactId="summary" kind="table" title="数值统计" />);
    fireEvent.click(screen.getByRole("button", {name:"在报告内查看"}));
    expect(await screen.findByRole("cell",{name:"0.12345678901234568"})).toBeInTheDocument();
    expect(screen.getByRole("columnheader",{name:"平均值"})).toBeInTheDocument();
  });

  it("previews saved periodic values without showing empty Cartesian-axis details", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify(savedPeriodicTableFixture(true))).buffer);
    render(<ScientificReportArtifactPreview jobId="periodic-job" artifactId="periodic" kind="figure" title="元素分布" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    const image = await screen.findByRole("img", { name: "元素分布持久化数据预览" });
    expect(savedSvg(image).querySelector('[data-element="Fe"]')?.getAttribute('data-value')).toBe('12');
    expect(screen.queryByText('坐标轴来源')).not.toBeInTheDocument();
    expect(screen.getByText('完整显示 4 个数据点')).toBeInTheDocument();
  });

  it("shows saved regression metrics and source columns at their original precision", async () => {
    const metrics = { n: 4096, mae: 0.06367252119238281, rmse: 0.07072364590422509,
      r2: 0.9977103333264732, meanError: 9.097270800781292e-5, maxAbsError: 0.10000000000000009 };
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      metrics, targetColumn: "y_true", predictionColumn: "y_pred",
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="metrics-job" artifactId="metrics" kind="table" title="回归评估指标" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    const table = await screen.findByRole("table");
    expect(within(table).getAllByRole("row").slice(1).map(row => Array.from(row.querySelectorAll("th, td"), cell => cell.textContent)))
      .toEqual([
        ["样本数", "4096"], ["MAE", String(metrics.mae)], ["RMSE", String(metrics.rmse)],
        ["R²", String(metrics.r2)], ["平均误差", String(metrics.meanError)], ["最大绝对误差", String(metrics.maxAbsError)],
        ["目标值列", "y_true"], ["预测值列", "y_pred"],
      ]);
    expect(screen.queryByRole("searchbox")).not.toBeInTheDocument();
    expect(screen.queryByText(/暂无可预览/)).not.toBeInTheDocument();
  });

  it("distinguishes saved undefined R² from a missing metric", async () => {
    const metrics = { n: 3, mae: 0, rmse: 0, r2: null, r2Status: "undefined_constant_target", meanError: 0, maxAbsError: 0 };
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({ metrics, targetColumn: "y_true", predictionColumn: "y_pred" })).buffer);
    render(<ScientificReportArtifactPreview jobId="constant-job" artifactId="metrics" kind="table" title="回归评估指标" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("cell", { name: "未定义（目标值为常量）" })).toBeInTheDocument();
    expect(screen.queryByText("r2Status")).not.toBeInTheDocument();
  });

  it.each([
    { metrics: { n: 4, mae: 0.1, rmse: 0.2, r2: null, r2Status: "defined", meanError: 0, maxAbsError: 0.3 }, targetColumn: "a", predictionColumn: "b" },
    { metrics: { n: 4, mae: 0.1, rmse: 0.2, r2: 1, r2Status: "undefined_constant_target", meanError: 0, maxAbsError: 0.3 }, targetColumn: "a", predictionColumn: "b" },
    { metrics: { n: 4, mae: 0.1 } },
    { metrics: { n: 4, mae: 0.1, rmse: 0.2, r2: 0.8, meanError: null, maxAbsError: 0.3 }, targetColumn: "a", predictionColumn: "b" },
    { metrics: { n: 4, mae: 0.1, rmse: 0.2, r2: 0.8, meanError: 0, maxAbsError: 0.3, otherMetric: 99 }, targetColumn: "a", predictionColumn: "b" },
  ])("does not guess regression semantics from incomplete or unsupported metrics", async payload => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify(payload)).buffer);
    render(<ScientificReportArtifactPreview jobId="unknown-job" artifactId="unknown-metrics" kind="table" title="未知指标" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByText(/暂无可预览的表格行/)).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("opens the exact volumetric producer bundle on demand and preserves it while collapsed", () => {
    const dataset = { id:"dataset",jobId:"job",toolCallId:"call",type:"volumetric_dataset_json",name:"dataset.json",sha256:"a".repeat(64),sizeBytes:64,contentType:"application/json" };
    const binary = {...dataset,id:"payload",name:"field.f64",type:"volumetric_binary"};
    const viewer = {projectId:"project",artifacts:[dataset,binary]};
    const {rerender} = render(<ScientificReportArtifactPreview jobId="job" artifactId="dataset" kind="figure" title="体数据场" viewer={viewer} />);
    expect(screen.queryByTestId("bound-volume-viewer")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button",{name:"在报告内查看"}));
    const content = screen.getByTestId("bound-volume-viewer");
    expect(content).toHaveTextContent('"toolCallId":"call"');
    expect(content).toHaveTextContent('"id":"payload"');
    fireEvent.click(screen.getByRole("button",{name:"收起页内预览"}));
    expect(content).not.toBeVisible();
    fireEvent.click(screen.getByRole("button",{name:"在报告内查看"}));
    expect(content).toBeVisible();
    rerender(<ScientificReportArtifactPreview jobId="job" artifactId="dataset" kind="figure" title="体数据场"
      viewer={{...viewer,artifacts:[dataset,{...binary,sha256:"b".repeat(64)}]}} />);
    expect(screen.queryByTestId("bound-volume-viewer")).not.toBeInTheDocument();
    rerender(<ScientificReportArtifactPreview jobId="job" artifactId="dataset" kind="figure" title="体数据场"
      viewer={{...viewer,artifacts:[dataset,{...binary,toolCallId:"foreign"}]}} />);
    expect(screen.getByRole("alert")).toHaveTextContent("来源无法准确对应");
  });

  it("puts exact phonon q-point, branch and frequency before secondary coordinates and preserves all rows", async () => {
    const user = userEvent.setup();
    const rows = Array.from({ length: 306 }, (_, i) => ({ classification: "real", q_x: i / 306, q_y: 0, q_z: 0,
      path_distance: i / 306, label: "Γ", branch_index: i % 6, qpoint_index: Math.floor(i / 6), segment_index: 0,
      frequency_terahertz: i === 5 ? 47.60626794807822 : i }));
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      schema_version: "phase10h1.phonon_band_table.v1", rows,
      units: { frequency: "terahertz", path_distance: "radian_per_angstrom", qpoint_coordinates: "reciprocal_fractional" },
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="phonon" artifactId="table" kind="table" title="声子能带" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    const table = await screen.findByRole("table");
    expect(within(table).getAllByRole("columnheader").map(cell => cell.textContent)).toEqual([
      "q 点索引", "分支索引", "频率 (THz)", "路径标签", "频率分类", "路径距离 (rad/Å)", "路径段索引",
    ]);
    expect(within(table).getAllByRole("row")[6]).toHaveTextContent("47.60626794807822");
    const page = screen.getByRole("spinbutton", { name: "表格页码" });
    await user.clear(page);
    expect(page).toHaveValue(null);
    await user.type(page, "13");
    expect(page).toHaveValue(13);
    await user.keyboard("{Enter}");
    expect(page).toHaveValue(13);
    expect(screen.getByRole("status")).toHaveTextContent("289–306 / 306 行");
    expect(table).toHaveTextContent("305");
    fireEvent.click(screen.getByRole("button", { name: "列显示" }));
    fireEvent.click(screen.getByRole("checkbox", { name: "qₓ" }));
    expect(within(table).getByRole("columnheader", { name: "qₓ" })).toBeVisible();
    fireEvent.change(screen.getByRole("searchbox"), { target: { value: "47.60626794807822" } });
    expect(screen.getByRole("status")).toHaveTextContent("匹配 1 / 306 行");
  });

  it("does not substitute a generic plot for phonon data with ambiguous branch labels", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      schema_version: "phase10h1.phonon_band_plot.v1", data: [{ x: [0], y: [47.6], name: "Branch 6" }],
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="phonon-invalid" artifactId="plot" kind="figure" title="声子能带" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("无法生成可信预览");
    expect(screen.queryByTestId("controlled-plot")).not.toBeInTheDocument();
  });

  it("uses the saved electronic band renderer with disconnected paths instead of a generic continuous plot", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      schemaVersion: "phase10n5.electronic_band_plot.v1",
      data: [{ type: "scatter", mode: "lines", name: "down:band-3", x: [0, 0.5, 0.5, 1.4], y: [-1, -2, 1, 3.365951568], customdata: ["g", "x", "l", "g2"] }],
      pathSegments: [{ segmentId: "gx", startKpointId: "g", endKpointId: "x", breakAfter: true }, { segmentId: "lg", startKpointId: "l", endKpointId: "g2", breakAfter: false }],
      layout: { shapes: [{ type: "line", x0: 0, x1: 1.4, y0: 0, y1: 0, line: { dash: "dash" } }] },
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="band" artifactId="plot" kind="figure" title="电子能带" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    const image = await screen.findByRole("img", { name: "电子能带持久化数据预览" });
    const svg = savedSvg(image);
    expect(svg.querySelector('path[data-series="down:band-3"]')?.getAttribute("d")?.match(/M/g)).toHaveLength(2);
    expect(svg.querySelector('[data-reference="fermi"]')).not.toBeNull();
    expect(screen.getByRole("status")).toHaveTextContent("完整显示 4 个数据点");
    expect(screen.queryByTestId("controlled-plot")).not.toBeInTheDocument();
    fireEvent.error(image);
    expect(screen.getByRole("alert")).toHaveTextContent("能带图片暂时无法显示");
    expect(screen.queryByTestId("controlled-plot")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "重新绘制能带图" }));
    expect(screen.getByRole("img", { name: "电子能带持久化数据预览" })).toBeVisible();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("keeps malformed band paths visible as unavailable instead of showing a misleading generic plot", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      schemaVersion: "phase10n5.electronic_band_plot.v1",
      data: [{ type: "scatter", mode: "lines", name: "up:b", x: [0, 1], y: [1, 2] }],
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="invalid-band" artifactId="plot" kind="figure" title="电子能带" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("能带路径或参考线信息不完整");
    expect(screen.queryByTestId("controlled-plot")).not.toBeInTheDocument();
  });

  it("keeps long cell values available through disclosure and searches their full content", async () => {
    const text = `saved-source:${"x".repeat(80)}:exact-middle:${"y".repeat(80)}`;
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({rows: [{description: text}, {description: "other"}]})).buffer);
    render(<ScientificReportArtifactPreview jobId="long-value" artifactId="long-value" kind="table" title="长值" />);
    fireEvent.click(screen.getByRole("button", {name: "在报告内查看"}));
    await screen.findByRole("table");
    const details = screen.getByText(/，查看完整值/).closest("details")!;
    expect(details).not.toHaveAttribute("open");
    fireEvent.click(details.querySelector("summary")!);
    expect(details).toHaveAttribute("open");
    expect(within(details).getByText(text)).toBeVisible();
    fireEvent.change(screen.getByRole("searchbox", {name: "搜索表格内容"}), {target: {value: "exact-middle"}});
    expect(screen.getByRole("status")).toHaveTextContent("匹配 1 / 2 行");
  });

  it("reads saved electronic states with exact energies and only unambiguous k-point coordinates", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      artifactType: "electronic.band_structure", schemaVersion: "phase10n5.electronic_band_structure.v1",
      kpoints: [{ kpointId: "k-90", label: "X", fractionalCoordinates: [0.5, 0, 0] },
        { kpointId: "duplicate", fractionalCoordinates: [1, 0, 0] }, { kpointId: "duplicate", fractionalCoordinates: [2, 0, 0] }],
      states: [{ stateId: "state-exact", bandId: "band-3", spinChannel: "down", kpointId: "k-90", energyEv: 3.365951568 },
        { stateId: "state-ambiguous", bandId: "band-1", spinChannel: "up", kpointId: "duplicate", energyEv: 0 }],
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="band" artifactId="states" kind="table" title="能带" />);
    fireEvent.click(screen.getByRole("button", {name: "在报告内查看"}));
    const table = await screen.findByRole("table");
    expect(table).toHaveTextContent("3.365951568");
    expect(table).toHaveTextContent("[0.5, 0, 0]");
    expect(table).toHaveTextContent("下自旋");
    expect(within(table).getAllByRole("row")[2]).not.toHaveTextContent("[1, 0, 0]");
    expect(within(table).getAllByRole("row")[2]).toHaveTextContent("—");
  });

  it("preserves DOS spin, projection identity, units and missing samples without summing or aligning", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      artifactType: "electronic.dos", schemaVersion: "phase10n5.electronic_dos.v1", energiesEv: [-1.25, 0, 1.75],
      energyPointIds: ["e-0", "e-1", "e-2"], dosUnitSemantic: "states_per_ev_cell",
      totalDos: [{ channelId: "up-total", channelIdentity: "total-id", spinChannel: "up", values: [0.125, 2, 4.25] }],
      projections: [{ channelId: "down-p", channelIdentity: "projection-id", label: "Fe p", spinChannel: "down", projectionKind: "orbital", values: [0.0625] }],
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="dos" artifactId="points" kind="table" title="态密度" />);
    fireEvent.click(screen.getByRole("button", {name: "在报告内查看"}));
    const table = await screen.findByRole("table");
    expect(table).toHaveTextContent("态密度 (states/eV/cell)");
    expect(table).toHaveTextContent("-1.25");
    expect(table).toHaveTextContent("4.25");
    expect(table).toHaveTextContent("Fe p");
    expect(table).toHaveTextContent("下自旋");
    expect(within(table).getAllByRole("row")).toHaveLength(7);
    expect(within(table).getAllByRole("row").at(-1)).toHaveTextContent("—");
    fireEvent.click(screen.getByRole("button", {name: "列显示"}));
    fireEvent.click(screen.getByRole("checkbox", {name: "通道标识"}));
    expect(table).toHaveTextContent("projection-id");
  });

  it("searches all saved columns, jumps directly to distant pages and retains the table view after collapse", async () => {
    const rows = Array.from({length: 8194}, (_, index) => ({energy: index, a: 1, b: 2, c: 3, d: 4, e: 5, f: 6, g: 7, detail: `point-${index}`}));
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({rows})).buffer);
    const {rerender} = render(<ScientificReportArtifactPreview jobId="large" artifactId="rows" kind="table" title="长表" />);
    fireEvent.click(screen.getByRole("button", {name: "在报告内查看"}));
    const table = await screen.findByRole("table");
    const page = screen.getByRole("spinbutton", {name: "表格页码"});
    fireEvent.change(page, {target: {value: "342"}});
    fireEvent.keyDown(page, {key: "Enter"});
    expect(screen.getByRole("status")).toHaveTextContent("8185–8194 / 8194 行");
    expect(table).toHaveTextContent("8193");
    fireEvent.click(screen.getByRole("button", {name: "列显示"}));
    fireEvent.click(screen.getByRole("checkbox", {name: "detail"}));
    expect(table).toHaveTextContent("point-8193");
    fireEvent.click(screen.getByRole("button", {name: "收起页内预览"}));
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", {name: "在报告内查看"}));
    expect(screen.getByRole("status")).toHaveTextContent("8185–8194 / 8194 行");
    expect(screen.getByRole("table")).toHaveTextContent("point-8193");
    const search = screen.getByRole("searchbox", {name: "搜索表格内容"});
    fireEvent.change(search, {target: {value: "point-8100"}});
    expect(screen.getByRole("status")).toHaveTextContent("1 / 8194 行");
    expect(within(screen.getByRole("table")).getAllByRole("row")).toHaveLength(2);
    fireEvent.change(search, {target: {value: "absent"}});
    expect(screen.getByText("没有匹配的数据。")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", {name: "清除搜索"}));
    expect(screen.getByRole("status")).toHaveTextContent("1–24 / 8194 行");
    const restoredPage = screen.getByRole("spinbutton", {name: "表格页码"});
    fireEvent.change(restoredPage, {target: {value: "9999"}});
    fireEvent.blur(restoredPage);
    expect(restoredPage).toHaveValue(342);
    fireEvent.change(restoredPage, {target: {value: ""}});
    fireEvent.keyDown(restoredPage, {key: "Enter"});
    expect(restoredPage).toHaveValue(342);
    fireEvent.change(restoredPage, {target: {value: "2"}});
    fireEvent.keyDown(restoredPage, {key: "Escape"});
    expect(restoredPage).toHaveValue(342);
    fireEvent.keyDown(screen.getByRole("group", {name: "显示列"}), {key: "Escape"});
    expect(screen.getByRole("button", {name: "列显示"})).toHaveFocus();
    expect(screen.queryByRole("checkbox")).not.toBeInTheDocument();
    rerender(<ScientificReportArtifactPreview jobId="other" artifactId="rows" kind="table" title="另一份表" />);
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("reads every saved XRD peak through bounded table pages with exact values", async () => {
    const peaks = Array.from({ length: 26 }, (_, index) => ({ two_theta_deg: 20.498535 + index,
      intensity: index, d_spacing_angstrom: 4.332692, hkls: [{ hkl: [0, 1, -1] }] }));
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      schema_version: "phase10e4.xrd_pattern.v1", pattern: { peaks },
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="xrd-job" artifactId="xrd-table" kind="table" title="峰位表" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    const table = await screen.findByRole("table");
    expect(table).toHaveTextContent("20.498535");
    expect(table).toHaveTextContent("4.332692");
    expect(table).toHaveTextContent("(0 1 -1)");
    expect(within(table).getAllByRole("row")).toHaveLength(25);
    expect(screen.getByRole("status")).toHaveTextContent("1–24 / 26 行");
    fireEvent.click(screen.getByRole("button", { name: "下一页" }));
    expect(screen.getByRole("status")).toHaveTextContent("25–26 / 26 行");
    expect(within(table).getAllByRole("row")).toHaveLength(3);
    expect(table).toHaveTextContent(String(peaks[25].two_theta_deg));
    expect(table).not.toHaveTextContent("20.498535");
    expect(screen.getByRole("button", { name: "下一页" })).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: "上一页" }));
    expect(table).toHaveTextContent("20.498535");
  });
  it("renders all XRD stems with saved axis names and range", async () => {
    const values = Array.from({ length: 290 }, (_, i) => i * 0.3);
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      chart_type: "stem", x_axis: { label: "2theta (degrees)" }, y_axis: { label: "Relative Intensity" },
      metadata: { two_theta_min: 0, two_theta_max: 90 }, series: [{ name: "XRD", x: values, y: values.map(() => 1) }],
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="xrd-job" artifactId="xrd-plot" kind="figure" title="理论 XRD" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    const svg = savedSvg(await screen.findByRole("img"));
    expect(svg.querySelectorAll('g[clip-path] line')).toHaveLength(290);
    expect(svg.querySelectorAll('g[clip-path] path')).toHaveLength(0);
    expect(svg.documentElement.textContent).toContain("2theta (degrees)");
    expect(svg.documentElement.textContent).toContain("Relative Intensity");
    expect(screen.getByRole("status")).toHaveTextContent("完整显示 290 个数据点");
    fireEvent.click(screen.getByText("坐标轴来源"));
    expect(screen.getByText("范围：0 至 90")).toBeInTheDocument();
  });

  it("hands unsupported plot semantics to the controlled viewer without substituting a line", async () => {
    const payload = { data: [{ type: "heatmap", z: [[1, 2], [3, 4]] }] };
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify(payload)).buffer);
    render(<ScientificReportArtifactPreview jobId="heatmap-job" artifactId="heatmap" kind="figure" title="热图" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByTestId("controlled-plot")).toHaveTextContent(JSON.stringify(payload));
    expect(screen.queryByRole("img")).toBeNull();
  });

  it("recovers an image render failure through the controlled viewer without fetching again", async () => {
    const payload = { data: [{ x: [0, 1], y: [2, 3] }] };
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify(payload)).buffer);
    render(<ScientificReportArtifactPreview jobId="image-job" artifactId="image" kind="figure" title="图表" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    fireEvent.error(await screen.findByRole("img"));
    expect(await screen.findByTestId("controlled-plot")).toHaveTextContent(JSON.stringify(payload));
    expect(screen.queryByRole("img")).toBeNull();
  });
  it("routes structure figures through scene validation instead of a numeric plot", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({ kind: "viewer_scene", scene: {} })).buffer);
    render(<ScientificReportArtifactPreview jobId="structure-job" artifactId="scene" kind="figure" title="晶体结构" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByTestId("viewer-scene-renderer-invalid")).toBeInTheDocument();
    expect(screen.queryByText(/没有可绘制的有限序列/)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "收起页内预览" }));
    expect(screen.queryByTestId("viewer-scene-renderer-invalid")).not.toBeInTheDocument();
  });

  it("reads structure summary properties without inventing missing values", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      schemaVersion: "phase10c1.structure_summary.v2", artifactType: "structure.summary",
      structures: [{ structureId: "structure-1", reducedFormula: "LiPO2", numSites: 4,
        isPeriodic: false, lattice: { a: 5, volume: 176.7 }, symmetry: { spacegroupSymbol: "P1" } }],
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="job-1" artifactId="summary-1" kind="table" title="结构摘要" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("table")).toHaveTextContent("晶胞体积 (Å³)");
    expect(screen.getByRole("table")).toHaveTextContent("176.7");
    expect(screen.getByRole("table")).toHaveTextContent("周期结构否");
    expect(screen.queryByText("晶格 b (Å)")).not.toBeInTheDocument();
    expect(screen.queryByText("结构标识")).not.toBeInTheDocument();
  });

  it("renders a bounded persisted figure preview without recomputation", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      artifactType: "structure.coordination_hist_plot",
      series: [{ name: "All sites", x: [6], y: [1] }],
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="job-1" artifactId="artifact-1" kind="figure" title="配位数分布" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("img", { name: "配位数分布持久化数据预览" })).toBeInTheDocument();
    expect(screen.getByText(/完整显示 1 个数据点/)).toBeInTheDocument();
    expect(getPlannerArtifactContent).toHaveBeenCalledWith("job-1", "artifact-1", { maximumBytes: 8 * 1024 * 1024, signal: expect.any(AbortSignal) });
  });

  it("maps authorization and missing-artifact failures to stable safe states", async () => {
    getPlannerArtifactContent.mockRejectedValueOnce({ status: 403, message: "forbidden" });
    const { rerender } = render(<ScientificReportArtifactPreview jobId="job-denied" artifactId="artifact-denied" kind="figure" title="受限图形" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("当前账号无权查看此科学结果");

    getPlannerArtifactContent.mockRejectedValueOnce({ status: 404, message: "missing" });
    rerender(<ScientificReportArtifactPreview jobId="job-missing" artifactId="artifact-missing" kind="table" title="缺失表格" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("找不到这项科学结果");
  });

  it("renders Plotly-compatible persisted data traces", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      artifactType: "trajectory_msd_plot",
      data: [{ type: "scatter", name: "total", x: [0.5, 1], y: [0.2, 0.8] }],
      layout: { xaxis: { title: "lag time / ps" }, yaxis: { title: "MSD / angstrom^2" } },
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="job-plotly" artifactId="artifact-plotly" kind="figure" title="轨迹均方位移" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("img", { name: "轨迹均方位移持久化数据预览" })).toBeInTheDocument();
    expect(screen.getByText(/完整显示 2 个数据点/)).toBeInTheDocument();
  });

  it("preserves every bounded point including narrow extrema instead of sampling the report", async () => {
    const x = Array.from({ length: 120 }, (_, index) => index);
    const y = x.map((index) => index);
    y[110] = 1000;
    y[115] = -1000;
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      artifactType: "trajectory_msd_plot",
      data: [{ type: "scatter", name: "total", x, y }],
    })).buffer);
    const { container } = render(<ScientificReportArtifactPreview jobId="job-sampled" artifactId="artifact-sampled" kind="figure" title="采样图" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("img", { name: "采样图持久化数据预览" })).toBeInTheDocument();
    expect(screen.getByText(/完整显示 120 个数据点/)).toBeInTheDocument();
    const plot = savedSvg(screen.getByRole("img"));
    const points = [...plot.querySelectorAll("[clip-path] circle")];
    expect(points).toHaveLength(120);
    const heights = points.map(point => Number(point.getAttribute("cy")));
    expect(heights[110]).toBe(Math.min(...heights));
    expect(heights[115]).toBe(Math.max(...heights));
  });

  it("surfaces authoritative axis ranges, ticks, and units without inferring them", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      artifactType: "electronic.band",
      data: [{ type: "scatter", name: "Γ–X", x: [0, 1], y: [-2, 3] }],
      layout: {
        xaxis: { title: { text: "k-path (Å⁻¹)" }, range: [0, 1], tickvals: [0, 0.5, 1], ticktext: ["Γ", "M", "X"] },
        yaxis: { title: { text: "Energy (eV)" }, range: [-2, 3], tickvals: [-2, 0, 3] },
      },
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="job-band" artifactId="artifact-band" kind="figure" title="能带结构" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));

    await screen.findByRole("img");
    fireEvent.click(screen.getByText("坐标轴来源"));
    expect(screen.getByRole("group", { name: "权威坐标轴信息" })).toBeInTheDocument();
    expect(screen.getByText("X 轴 · k-path (Å⁻¹)")).toBeInTheDocument();
    expect(screen.getByText("范围：0 至 1")).toBeInTheDocument();
    expect(screen.getByText("刻度：Γ · M · X")).toBeInTheDocument();
    expect(screen.getByText("Y 轴 · Energy (eV)")).toBeInTheDocument();
    expect(screen.getByText("范围：-2 至 3")).toBeInTheDocument();
    expect(screen.getByText("刻度：-2 · 0 · 3")).toBeInTheDocument();
    const svg = savedSvg(screen.getByRole("img", { name: "能带结构持久化数据预览" }));
    expect(svg.documentElement.textContent).toContain("k-path (Å⁻¹)");
    expect(svg.documentElement.textContent).toContain("Energy (eV)");
  });

  it("preserves authoritative non-uniform x spacing in the report preview", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      artifactType: "xrd.pattern",
      data: [{ type: "scatter", name: "XRD", x: [0, 0.1, 10], y: [0.2, 0.4, 0.8] }],
    })).buffer);
    const { container } = render(
      <ScientificReportArtifactPreview jobId="job-xrd" artifactId="artifact-xrd" kind="figure" title="非均匀 XRD" />,
    );
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("img", { name: "非均匀 XRD持久化数据预览" })).toBeInTheDocument();
    const xCoordinates = Array.from(savedSvg(screen.getByRole("img")).querySelectorAll("[clip-path] circle")).map((point) => Number(point.getAttribute("cx")));
    expect(xCoordinates).toHaveLength(3);
    expect(xCoordinates[1] - xCoordinates[0]).toBeCloseTo((xCoordinates[2] - xCoordinates[0]) * 0.01, 4);
  });

  it("renders the repository Plotly payload when data is nested under figure", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      schema_version: "phase10e4.static_chart.v1",
      figure: {
        data: [{ type: "scattergl", name: "实验 XRD", x: [20, 30], y: [0, 1] }],
        layout: {
          xaxis: { title: { text: "2θ (°)" } },
          yaxis: { title: { text: "归一化强度" } },
        },
      },
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="job-nested" artifactId="artifact-nested" kind="figure" title="实验 XRD" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("img", { name: "实验 XRD持久化数据预览" })).toBeInTheDocument();
    expect(screen.getByText(/完整显示 2 个数据点/)).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "图形预览：实验 XRD" })).toBeInTheDocument();
    expect(savedSvg(screen.getByRole("img")).documentElement.textContent).toContain("实验 XRD");
  });

  it("renders bounded table rows and preserves a truthful fallback", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      histogram: { bins: [{ coordination_number: 6, count: 1 }] },
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="job-2" artifactId="artifact-2" kind="table" title="配位数表" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    await waitFor(() => expect(screen.getByRole("region", { name: "持久化数据表预览" })).toBeInTheDocument());
    expect(screen.getByText("配位数")).toBeInTheDocument();
    expect(screen.getByText("6")).toBeInTheDocument();
  });

  it("projects persisted MSD arrays into a bounded typed table", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      artifactType: "trajectory.msd",
      lagTimesPs: [0.5, 1],
      totalMsdAngstrom2: [0.2, 0.8],
      directionalMsdAngstrom2: { x: [0.1, 0.4], y: [0.08, 0.3], z: [0.02, 0.1] },
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="job-msd" artifactId="artifact-msd" kind="table" title="轨迹均方位移" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    await waitFor(() => expect(screen.getByRole("region", { name: "持久化数据表预览" })).toBeInTheDocument());
    expect(screen.getByText("总 MSD (Å²)")).toBeInTheDocument();
    expect(screen.getByText("0.8")).toBeInTheDocument();
  });

  it("keeps saved MSD rows beyond the old 96-row cutoff reachable without padding missing values", async () => {
    const times = Array.from({ length: 101 }, (_, index) => index * 0.25);
    const total = times.map((_, index) => index * 0.00314159);
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      artifactType: "trajectory.msd", lagTimesPs: times, totalMsdAngstrom2: total,
      directionalMsdAngstrom2: { x: [0], y: [0], z: [0] },
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="long-msd" artifactId="long-msd-table" kind="table" title="完整轨迹" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    const table = await screen.findByRole("table");
    expect(screen.getByRole("status")).toHaveTextContent("1–24 / 101 行");
    for (let page = 0; page < 4; page += 1) fireEvent.click(screen.getByRole("button", { name: "下一页" }));
    expect(screen.getByRole("status")).toHaveTextContent("97–101 / 101 行");
    const lastRow = within(table).getAllByRole("row").at(-1)!;
    expect(within(lastRow).getAllByRole("cell").map(cell => cell.textContent))
      .toEqual([String(times[100]), String(total[100]), "—", "—", "—"]);
    expect(screen.getByRole("button", { name: "下一页" })).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: "上一页" }));
    expect(screen.getByRole("status")).toHaveTextContent("73–96 / 101 行");
  });

  it("allows every saved column to be displayed instead of only naming hidden columns", async () => {
    const rows = Array.from({ length: 26 }, (_, index) => ({
      sample_id: `mat-${index + 1}`,
      band_gap: index / 10,
      formula: "Si",
      formation_energy: -1,
      quality: "verified",
      source: "dataset",
      phase: "cubic",
      temperature: 300,
      pressure: 1,
      notes: "bounded",
    }));
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({ rows })).buffer);
    render(<ScientificReportArtifactPreview jobId="job-table" artifactId="artifact-table" kind="table" title="数据表" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));

    expect(await screen.findByRole("region", { name: "持久化数据表预览" })).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("显示 1–24 / 26 行 · 8 / 10 列");
    fireEvent.click(screen.getByRole("button", {name: "列显示"}));
    expect(screen.getByRole("checkbox", {name: "temperature"})).toBeChecked();
    fireEvent.click(screen.getByRole("checkbox", {name: "pressure"}));
    expect(screen.getByRole("columnheader", {name: "pressure"})).toBeInTheDocument();
  });

  it("keeps report table row identity stable when rows are reordered", () => {
    const silicon = { formula: "Si", band_gap: 1.1 };
    const oxide = { band_gap: 2.2, formula: "Fe2O3" };
    const original = scientificReportTableRowKeys([silicon, oxide]);
    const reordered = scientificReportTableRowKeys([oxide, silicon]);
    expect(original[0]).toBe(reordered[1]);
    expect(original[1]).toBe(reordered[0]);
    expect(original[0]).not.toBe(original[1]);
  });

  it("uses unique semantic row identities and safely disambiguates duplicate rows", () => {
    const semantic = scientificReportTableRowKeys([
      { sample_id: "mat-2", band_gap: 2.1 },
      { sample_id: "mat-3", band_gap: 2.1 },
    ]);
    expect(semantic).toEqual(["semantic:sample_id:mat-2", "semantic:sample_id:mat-3"]);
    const duplicates = scientificReportTableRowKeys([{ value: 1 }, { value: 1 }]);
    expect(new Set(duplicates).size).toBe(2);
  });

  it("does not turn failed payload reads into a false success", async () => {
    getPlannerArtifactContent.mockRejectedValueOnce(new Error("SOURCE_MISSING"));
    render(<ScientificReportArtifactPreview jobId="job-3" artifactId="artifact-3" kind="figure" title="缺失图表" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("科学结果暂时无法读取");
    expect(screen.queryByText(/SOURCE_MISSING/u)).not.toBeInTheDocument();
    expect(screen.queryByRole("img")).toBeNull();
  });

  it.each([
    [401, "登录状态已过期"],
    [403, "当前账号无权查看此科学结果"],
    [404, "找不到这项科学结果"],
    [410, "这项科学结果已过期"],
    [413, "内容超出页内预览范围"],
  ])("maps HTTP %s to a typed Artifact preview state", async (status, code) => {
    getPlannerArtifactContent.mockRejectedValueOnce(Object.assign(new Error(code), {
      status,
      details: { detail: { code } },
    }));
    render(<ScientificReportArtifactPreview jobId="job-status" artifactId="artifact-status" kind="figure" title="状态图表" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(code);
    expect(screen.queryByRole("img")).toBeNull();
  });

  it("retries an unavailable preview and retains it across collapse and reopen", async () => {
    getPlannerArtifactContent.mockRejectedValueOnce(new Error("private transport error"))
      .mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({series: [{x: [1, 2], y: [3, 4]}]})).buffer);
    render(<ScientificReportArtifactPreview jobId="retry-job" artifactId="retry-artifact" kind="figure" title="可恢复图形" />);
    fireEvent.click(screen.getByRole("button", {name: "在报告内查看"}));
    fireEvent.click(await screen.findByRole("button", {name: "重新加载预览"}));
    expect(await screen.findByRole("img", {name: "可恢复图形持久化数据预览"})).toBeInTheDocument();
    const requestCount = getPlannerArtifactContent.mock.calls.length;
    fireEvent.click(screen.getByRole("button", {name: "收起页内预览"}));
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", {name: "在报告内查看"}));
    expect(screen.getByRole("img", {name: "可恢复图形持久化数据预览"})).toBeInTheDocument();
    expect(getPlannerArtifactContent.mock.calls.length).toBe(requestCount);
  });

  it("ignores a late preview after its source identity changes", async () => {
    let finish!: (value: ArrayBuffer) => void;
    getPlannerArtifactContent.mockReturnValueOnce(new Promise(resolve => {finish = resolve;}));
    const {rerender} = render(<ScientificReportArtifactPreview jobId="old-job" artifactId="old-artifact" kind="figure" title="旧图形" />);
    fireEvent.click(screen.getByRole("button", {name: "在报告内查看"}));
    const oldSignal = getPlannerArtifactContent.mock.calls.at(-1)![2].signal;
    rerender(<ScientificReportArtifactPreview jobId="new-job" artifactId="new-artifact" kind="figure" title="新图形" />);
    expect(oldSignal.aborted).toBe(true);
    await act(async () => finish(new TextEncoder().encode(JSON.stringify({series: [{x: [1], y: [2]}]})).buffer));
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(screen.getByRole("button", {name: "在报告内查看"})).toBeEnabled();
  });

  it("ends stalled previews with a retry action and ignores responses after timeout", async () => {
    vi.useFakeTimers();
    try {
      let finish!: (value: ArrayBuffer) => void;
      getPlannerArtifactContent.mockReturnValueOnce(new Promise(resolve => {finish = resolve;}));
      render(<ScientificReportArtifactPreview jobId="slow-job" artifactId="slow-artifact" kind="figure" title="慢速图形" />);
      fireEvent.click(screen.getByRole("button", {name: "在报告内查看"}));
      expect(screen.getByRole("button", {name: "正在读取…"})).toBeDisabled();
      await act(async () => {await vi.advanceTimersByTimeAsync(10_000);});
      expect(screen.getByRole("alert")).toHaveTextContent("预览读取超时，请重试");
      expect(screen.getByRole("button", {name: "重新加载预览"})).toBeEnabled();
      await act(async () => finish(new TextEncoder().encode('{}').buffer));
      expect(screen.queryByRole("img")).not.toBeInTheDocument();
    } finally { vi.useRealTimers(); }
  });
});
