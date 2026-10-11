// @vitest-environment node
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { GET } from "./route";
import { createHash } from "node:crypto";
import { unzipSync, strFromU8 } from "fflate/node";
import { buildScientificReportMarkdown, buildScientificReportReproducibilityManifest, type ScientificReportView } from "../../../../lib/scientific-report-api";
import { savedPeriodicTableFixture } from "../../../../../scientific-viewers/workspace/saved-periodic-table.fixture";
import savedStructure from "../../../../../../../tests/fixtures/viewer_scene_v1/valid_optional_bonds.viewer_scene.v1.json";

const report: ScientificReportView = {
  report_id: "agent2_report_exact", snapshot_id: "saved_snapshot", project_id: "owned_project",
  research_turn_id: "saved_turn", scientific_result_snapshot_id: "saved_result",
  scientific_interpretation_id: "saved_interpretation", source_fingerprint: "saved_hash",
  grounding_status: "VALID", created_at: "2026-10-03T00:00:00Z",
  title: "XRD 合成晶体", relevance_at_generation: "CURRENT", current_effective_relevance: "CURRENT",
  scientific_context: "波长？", finding_count: 1, figure_count: 0,
  viewer_sources: [{ source_ref: "source", object_id: "object", version_id: "exact_version", object_type: "structure.crystal", display_name: "原始晶体", is_current_version: false }],
  report: {
    contract_version: "2.0", title: 'XRD 合成晶体 "test"\r\nunsafe/header', research_question: "波长？", summary: "1.54184 Å",
    main_findings: [{ statement: "峰位 20.498535°", finding_refs: [], fact_refs: ["peak"], evidence_refs: ["evidence"] }],
    primary_figures: [], supporting_results: [], method_summary: "已保存计算", limitations: [],
    data_sources: ["source"], evidence_refs: ["evidence"], reproducibility_summary: "精确版本", omitted_supporting_items: [],
  },
};
const fetchMock = vi.fn<typeof fetch>();
const request = (signal?: AbortSignal) => new Request("http://localhost:3023/downloads/scientific-reports/agent2_report_exact/markdown", {
  headers: { cookie: "session=private-test-session", "x-ignore": "untrusted" }, signal,
});
const params = (format = "markdown", reportId = report.report_id) => ({ params: Promise.resolve({ reportId, format }) });

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
  vi.stubEnv("MDI_API_PROXY_TARGET", "http://127.0.0.1:8005/");
});
afterEach(() => { vi.unstubAllGlobals(); vi.unstubAllEnvs(); vi.useRealTimers(); });

describe("report HTTP downloads", () => {
  const plot = JSON.stringify({ chart_type: "stem", x_axis: { label: "2θ (degrees)" }, y_axis: { label: "Relative Intensity" }, series: [{ name: "XRD", x: [20.498535, 21.874628], y: [100, 75.000168] }] });
  const artifactResponse = (content: string, checksum?: string) => new Response(content, { headers: {
    "content-type": "application/json", "x-content-length-validated": String(Buffer.byteLength(content)),
    "x-content-sha256": checksum || createHash("sha256").update(content).digest("hex"),
  } });
  const figureReport: ScientificReportView = { ...report,
    report: { ...report.report!, primary_figures: [{ figure_ref: "figure-xrd", caption: "XRD 图谱", fact_refs: [], evidence_refs: [] }] },
    figure_sources: [{ figure_ref: "figure-xrd", job_id: "job_exact", artifact_ids: ["plot_exact"] }],
    table_sources: [{ table_ref: "table-xrd", job_id: "job_exact", artifact_ids: ["table_exact"] }],
    file_sources: [{ artifact_id: "table_exact", job_id: "job_exact", title: "same table" }],
  };

  it("keeps a shared scientific limitation with all findings in both ZIP documents", async () => {
    const limit = "合成测试样本，不能外推到真实材料。";
    const findings = ["MAE 为 0.123456789012345。", "RMSE 为 0.234567890123456。"].map((text, i) => ({
      statement: text + limit, finding_refs: [`finding.${i}`], fact_refs: [`fact.${i}`], evidence_refs: [`evidence.${i}`],
      reasoning_assessment: { accepted: true, scope: "同一合成数据版本", limitations: [limit] },
    }));
    fetchMock.mockResolvedValueOnce(Response.json({ ...report, report: { ...report.report!, main_findings: findings, discussion: null } }));
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(200);
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    for (const name of ["report.html", "report.md"]) {
      const text = strFromU8(files[name]);
      expect(text.split(limit)).toHaveLength(2);
      expect(text).toContain("共同限制：");
      expect(text).toContain("MAE 为 0.123456789012345。");
      expect(text).toContain("RMSE 为 0.234567890123456。");
      for (const ref of ["finding.0", "fact.0", "evidence.0", "finding.1", "fact.1", "evidence.1"]) expect(text).toContain(ref);
      expect(text).not.toContain("科学讨论");
    }
  });

  it("uses the same conservative limitation list in Markdown and ZIP without rewriting the saved manifest", async () => {
    const limitations = [
      { statement: "No center-of-mass drift correction is applied.", source_refs: ["limit.saved"] },
      { statement: "未应用质心漂移校正。", source_refs: [] },
      { statement: "本次结果未应用质心漂移校正。", source_refs: [] },
      { statement: "MSD uses Cartesian x/y/z axes and is not automatically crystallographic a/b/c diffusion.", source_refs: ["limit.axes"] },
      { statement: "MSD使用笛卡尔x/y/z轴，非自动晶格a/b/c扩散。", source_refs: [] },
      { statement: "拟合窗口时长0.08 ps，小于1.0 ps；不能成立扩散系数。", source_refs: [] },
      { statement: "材料 A 未应用质心漂移校正。", source_refs: [] },
    ];
    const view = { ...report, report: { ...report.report!, limitations } };
    fetchMock.mockResolvedValueOnce(Response.json(view)).mockResolvedValueOnce(Response.json(view));
    const markdown = await (await GET(request(), params("markdown"))).text();
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(200);
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    for (const text of [markdown, strFromU8(files["report.md"]), strFromU8(files["report.html"])]) {
      for (const sentence of [
        "本次结果未应用质心漂移校正。",
        "MSD 使用笛卡尔 x/y/z 轴，不会自动解释为晶体学 a/b/c 方向扩散。",
        "拟合窗口时长0.08 ps，小于1.0 ps；不能成立扩散系数。",
        "材料 A 未应用质心漂移校正。",
      ]) expect(text.split(sentence)).toHaveLength(2);
      expect(text).not.toContain("MSD使用笛卡尔x/y/z轴，非自动晶格a/b/c扩散。");
    }
    expect(JSON.parse(strFromU8(files["reproducibility.json"])).limitations).toEqual(limitations.map(item => item.statement));
    const manifest = JSON.parse(strFromU8(files["bundle-manifest.json"]));
    for (const entry of manifest.files) expect(createHash("sha256").update(files[entry.path]).digest("hex")).toBe(entry.sha256);
  });

  it("downloads a self-contained ZIP with linked figures, exact artifacts and checksums", async () => {
    fetchMock.mockResolvedValueOnce(Response.json(figureReport)).mockResolvedValueOnce(artifactResponse(plot)).mockResolvedValueOnce(artifactResponse('{"peak":20.498535}'));
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toBe("application/zip");
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    expect(Object.keys(files)).toEqual(expect.arrayContaining(["report.html", "report.md", "reproducibility.json", "bundle-manifest.json", "figures/figure-1-1.svg", "artifacts/artifact-001.json", "artifacts/artifact-002.json"]));
    expect(strFromU8(files["report.md"])).toContain("[![科学图表](figures/figure-1-1-inline.svg)](figures/figure-1-1.svg)");
    expect(strFromU8(files["report.html"])).toContain('src="figures/figure-1-1-inline.svg"');
    expect(strFromU8(files["report.html"])).toContain('href="figures/figure-1-1.svg"');
    expect(strFromU8(files["figures/figure-1-1.svg"])).toContain('data-plot-title="true"');
    expect(strFromU8(files["figures/figure-1-1-inline.svg"])).not.toContain('data-plot-title="true"');
    expect(strFromU8(files["figures/figure-1-1-inline.svg"])).toContain('<title id="title">XRD 图谱</title>');
    expect(strFromU8(files["report.html"])).toContain('media="(max-width:600px)" srcset="figures/figure-1-1-small.svg"');
    expect(strFromU8(files["report.html"])).toContain('media="(max-width:960px)" srcset="figures/figure-1-1-medium.svg"');
    expect(strFromU8(files["figures/figure-1-1-medium.svg"])).toContain('viewBox="0 0 640');
    expect(strFromU8(files["figures/figure-1-1-small.svg"])).toContain('viewBox="0 0 360');
    expect(strFromU8(files["report.html"])).not.toContain("<script");
    expect(strFromU8(files["artifacts/artifact-001.json"])).toBe(plot);
    const manifest = JSON.parse(strFromU8(files["bundle-manifest.json"]));
    expect(manifest.snapshot_id).toBe(report.snapshot_id);
    for (const entry of manifest.files) expect(createHash("sha256").update(files[entry.path]).digest("hex")).toBe(entry.sha256);
    expect(manifest.files.find((entry: { point_count?: number }) => entry.point_count)?.point_count).toBe(2);
    expect(manifest.files.find((entry: { path: string }) => entry.path === "figures/figure-1-1-small.svg")).toMatchObject({ derived_from: "artifacts/artifact-001.json", point_count: 2 });
    expect(manifest.files.find((entry: { path: string }) => entry.path === "figures/figure-1-1-inline.svg")).toMatchObject({ derived_from: "artifacts/artifact-001.json", point_count: 2 });
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(fetchMock.mock.calls[1][0]).toBe("http://127.0.0.1:8005/planner/jobs/job_exact/artifacts/plot_exact/content");
  });

  it("exports every saved correlation cell and its original JSON in the report ZIP", async () => {
    const matrix = JSON.stringify({ data: [{ type: "heatmap", x: ["A", "B"], y: ["A", "B"],
      z: [[1, 0.9733285267845752], [0.9733285267845752, 1]], zmin: -1, zmax: 1,
      colorscale: [[0, "#67001f"], [0.5, "#f7f7f7"], [1, "#053061"]], colorbar: { title: "pearson" } }] });
    const view = { ...figureReport, table_sources: [], file_sources: [], report: { ...figureReport.report!, primary_figures: [{ figure_ref: "figure-xrd", caption: "相关性矩阵", fact_refs: [], evidence_refs: [] }] } };
    fetchMock.mockResolvedValueOnce(Response.json(view)).mockResolvedValueOnce(artifactResponse(matrix));
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(200);
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    expect(strFromU8(files["artifacts/artifact-001.json"])).toBe(matrix);
    for (const suffix of ["", "-inline", "-medium", "-small"]) {
      const svg = strFromU8(files[`figures/figure-1-1${suffix}.svg`]);
      expect(svg.match(/data-cell=/g)).toHaveLength(4);
      expect(svg).toContain('data-min="-1" data-max="1"');
      expect(svg).toContain('data-value="0.9733285267845752"');
    }
    expect(strFromU8(files["report.html"])).not.toContain("暂不支持静态图片导出");
    expect(strFromU8(files["report.html"])).toContain('data-figure-fit="width"');
    const manifest = JSON.parse(strFromU8(files["bundle-manifest.json"]));
    for (const entry of manifest.files) expect(createHash("sha256").update(files[entry.path]).digest("hex")).toBe(entry.sha256);
  });

  it("includes periodic-table images and byte-identical raw counts in every ZIP layout", async () => {
    const original = JSON.stringify(savedPeriodicTableFixture(true));
    fetchMock.mockResolvedValueOnce(Response.json(figureReport)).mockResolvedValueOnce(artifactResponse(original)).mockResolvedValueOnce(artifactResponse('{"count":4}'));
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(200);
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    for (const suffix of ["", "-inline", "-medium", "-small"]) {
      const text = strFromU8(files[`figures/figure-1-1${suffix}.svg`]);
      expect(text).toContain('data-element="Fe" data-value="12"');
      expect(text).toContain('出现次数（对数色阶）');
    }
    expect(strFromU8(files["artifacts/artifact-001.json"])).toBe(original);
    expect(strFromU8(files["report.html"])).not.toContain('暂不支持静态图片导出');
    expect(strFromU8(files["report.md"])).toContain('figures/figure-1-1-inline.svg');
    const manifest = JSON.parse(strFromU8(files["bundle-manifest.json"]));
    expect(manifest.rendering).toBe('saved-scientific-svg/1.17');
    for (const entry of manifest.files) expect(createHash('sha256').update(files[entry.path]).digest('hex')).toBe(entry.sha256);
  });

  it.each(["sunburst", "treemap"])("exports %s geometry, identity index and original bytes in all image layouts", async type => {
    const original = JSON.stringify({ data: [{ type, ids: ["root", "root/Cu"], labels: ["Cu", "Cu"], parents: ["", "root"], values: [2, 2], branchvalues: "total" }] });
    fetchMock.mockResolvedValueOnce(Response.json({ ...figureReport, table_sources: [], file_sources: [] })).mockResolvedValueOnce(artifactResponse(original));
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(200);
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    for (const suffix of ["", "-inline", "-medium", "-small"]) {
      const svg = strFromU8(files[`figures/figure-1-1${suffix}.svg`]);
      expect(svg).toContain('data-node="root/Cu" data-parent="root" data-value="2"');
      expect(svg).toContain('data-node-index="root/Cu"');
    }
    expect(strFromU8(files["artifacts/artifact-001.json"])).toBe(original);
    expect(strFromU8(files["report.html"])).toContain('data-figure-fit="width"');
    const manifest = JSON.parse(strFromU8(files["bundle-manifest.json"]));
    for (const entry of manifest.files) expect(createHash("sha256").update(files[entry.path]).digest("hex")).toBe(entry.sha256);
  });

  it("exports saved element counts in every ZIP image size and preserves their source bytes", async () => {
    const original = JSON.stringify({ artifactType: "composition.elements_hist", chartType: "bar", countMode: "fractional", elementCount: 2,
      bars: [{ element: "Fe", count: 0.5, fraction: 0.5 }, { element: "O", count: 0.5, fraction: 0.5 }],
      plotlyFigure: { data: [{ type: "bar", x: ["Fe", "O"], y: [0.5, 0.5] }], layout: { yaxis: { type: "log" } } } });
    fetchMock.mockResolvedValueOnce(Response.json({ ...figureReport, table_sources: [], file_sources: [] })).mockResolvedValueOnce(artifactResponse(original));
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(200);
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    for (const suffix of ["", "-inline", "-medium", "-small"]) {
      const svg = strFromU8(files[`figures/figure-1-1${suffix}.svg`]);
      expect(svg).toContain('data-element="Fe" data-value="0.5"');
      expect(svg).toContain('data-element="O" data-value="0.5"');
      expect(svg).toContain("对数刻度");
    }
    expect(strFromU8(files["artifacts/artifact-001.json"])).toBe(original);
    expect(strFromU8(files["report.html"])).toContain('data-figure-fit="width"');
    expect(strFromU8(files["report.md"])).toContain("figures/figure-1-1-inline.svg");
    const manifest = JSON.parse(strFromU8(files["bundle-manifest.json"]));
    for (const entry of manifest.files) expect(createHash("sha256").update(files[entry.path]).digest("hex")).toBe(entry.sha256);
  });

  it("keeps a valid export when saved tick labels cannot fit the narrow SVG", async () => {
    const payload = JSON.stringify({ data: [{ x: [0, 1], y: [0, 1], mode: "lines" }],
      layout: { yaxis: { tickvals: [0, 1], ticktext: ["0.000000000000000000000", "1.000000000000000000000"] } } });
    fetchMock.mockResolvedValueOnce(Response.json({ ...figureReport, table_sources: [], file_sources: [] }))
      .mockResolvedValueOnce(artifactResponse(payload));
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(200);
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    expect(strFromU8(files["figures/figure-1-1-small.svg"])).toContain("0.000000000000000000000");
    expect(strFromU8(files["artifacts/artifact-001.json"])).toBe(payload);
  });

  it("exports valid structures as linked projection images with byte-identical source data", async () => {
    const payload = JSON.stringify(savedStructure);
    const view = { ...figureReport, table_sources: [], file_sources: [], report: { ...figureReport.report!,
      primary_figures: [{ figure_ref: "figure-xrd", caption: "晶体结构", fact_refs: [], evidence_refs: [] }] } };
    fetchMock.mockResolvedValueOnce(Response.json(view)).mockResolvedValueOnce(artifactResponse(payload));
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(200);
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    const images = Object.keys(files).filter(path => path.endsWith(".svg"));
    expect(images).toHaveLength(4);
    for (const path of images) {
      const svg = strFromU8(files[path]);
      expect(svg.match(/data-structure-view=/g)).toHaveLength(4);
      expect(svg.match(/data-site=/g)).toHaveLength(8);
      expect(svg).not.toMatch(/NaN|Infinity/);
    }
    expect(strFromU8(files["artifacts/artifact-001.json"])).toBe(payload);
    expect(strFromU8(files["report.html"])).toContain("figures/figure-1-1-inline.svg");
    expect(strFromU8(files["report.md"])).toContain("figures/figure-1-1.svg");
    const manifest = JSON.parse(strFromU8(files["bundle-manifest.json"]));
    for (const file of manifest.files) expect(createHash("sha256").update(files[file.path]).digest("hex")).toBe(file.sha256);
  });

  it("retains unsupported figure files with an explicit note instead of a fabricated image", async () => {
    fetchMock.mockResolvedValueOnce(Response.json({ ...figureReport, table_sources: [], file_sources: [] })).mockResolvedValueOnce(artifactResponse('{"kind":"viewer_scene"}'));
    const response = await GET(request(), params("zip"));
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    expect(Object.keys(files).some(path => path.endsWith(".svg"))).toBe(false);
    expect(strFromU8(files["report.html"])).toContain("暂不支持静态图片导出");
    expect(strFromU8(files["report.md"])).toContain("artifacts/artifact-001.json");
  });

  it("translates export prose and image captions without changing source files, manifests or questions", async () => {
    const caption = 'orbital_density <img src=x onerror="alert(1)">';
    const view: ScientificReportView = { ...figureReport, table_sources: [], file_sources: [], report: { ...figureReport.report!,
      research_question: "electron_count 和 source_native 是什么？",
      summary: "积分语义为 electron_count，数值 3.1000000000000005 electron；不能据此判断成键。",
      primary_figures: [{ figure_ref: "figure-xrd", caption, fact_refs: [], evidence_refs: [] }],
    } };
    const manifestBefore = buildScientificReportReproducibilityManifest(view);
    fetchMock.mockResolvedValueOnce(Response.json(view)).mockResolvedValueOnce(artifactResponse(plot));
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(200);
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    for (const file of ["report.html", "report.md"]) {
      const content = strFromU8(files[file]);
      expect(content).toContain("积分表示电子数，数值 3.1000000000000005 electron；不能据此判断成键。");
      expect(content).toContain("electron_count 和 source_native 是什么？");
      expect(content).toContain("轨道密度");
    }
    expect(strFromU8(files["report.html"])).toContain('alt="轨道密度 &lt;img');
    expect(strFromU8(files["report.html"])).not.toContain('<img src=x');
    expect(strFromU8(files["figures/figure-1-1.svg"])).toContain("轨道密度");
    expect(strFromU8(files["artifacts/artifact-001.json"])).toBe(plot);
    expect(strFromU8(files["reproducibility.json"])).toBe(manifestBefore);
    expect(JSON.parse(strFromU8(files["bundle-manifest.json"])).figures[0].caption).toBe(caption);
  });

  it("links named tables and result files to their exact job/artifact pair, including reused artifact IDs", async () => {
    const tableA = '{"value":3.365951568}', tableB = '{"value":5.28253434983e-78}';
    const view: ScientificReportView = { ...report,
      table_sources: [
        { table_ref: "same-ref", title: "能带数据", job_id: "job_a", artifact_ids: ["same_id"], source_refs: [{ object_id: "band", version_id: "band_version", object_type: "electronic.band_structure" }] },
        { table_ref: "same-ref", title: "态密度数据", job_id: "job_b", artifact_ids: ["same_id"] },
        { table_ref: "unbound", title: "未绑定表格", job_id: null, artifact_ids: [] },
      ],
      file_sources: [{ title: "能带原始结果", job_id: "job_a", artifact_id: "same_id" }],
    };
    fetchMock.mockResolvedValueOnce(Response.json(view)).mockResolvedValueOnce(artifactResponse(tableA)).mockResolvedValueOnce(artifactResponse(tableB));
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(200);
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    const html = strFromU8(files["report.html"]), md = strFromU8(files["report.md"]);
    expect(html).toMatch(/能带数据[\s\S]*?href="artifacts\/artifact-001.json"/);
    expect(html).toMatch(/态密度数据[\s\S]*?href="artifacts\/artifact-002.json"/);
    expect(html).toMatch(/能带原始结果[\s\S]*?href="artifacts\/artifact-001.json"/);
    expect(html).toContain("主要数据表</h2>");
    expect(html).toContain("band_version");
    expect(html).toContain("此表未绑定可导出的数据文件");
    expect(md).toMatch(/能带数据[\s\S]*?\[原始数据表\]\(artifacts\/artifact-001.json\)/);
    expect(md).toMatch(/态密度数据[\s\S]*?\[原始数据表\]\(artifacts\/artifact-002.json\)/);
    expect(md).toMatch(/能带原始结果[\s\S]*?\[原始结果文件\]\(artifacts\/artifact-001.json\)/);
    expect(strFromU8(files["artifacts/artifact-001.json"])).toBe(tableA);
    expect(strFromU8(files["artifacts/artifact-002.json"])).toBe(tableB);
    expect(fetchMock).toHaveBeenCalledTimes(3);
    for (const [, path] of html.matchAll(/(?:href|src)="([^"#][^"]*)"/g)) expect(files[path], path).toBeDefined();
    for (const [, anchor] of html.matchAll(/href="#([^"]+)"/g)) expect(html).toContain(`id="${anchor}"`);
  });

  it.each(["missing", "ambiguous"])("does not choose a figure source when the binding is %s", async (binding) => {
    const view = { ...figureReport, figure_sources: binding === "missing" ? [] : [
      figureReport.figure_sources![0], { ...figureReport.figure_sources![0], job_id: "foreign_job", version_id: "foreign_version" },
    ] };
    fetchMock.mockResolvedValueOnce(Response.json(view));
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(303);
    expect(response.headers.get("location")).toContain("reason=unavailable");
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const md = buildScientificReportMarkdown(view);
    expect(md).not.toContain("Artifacts: plot_exact");
    expect(md).not.toContain("foreign_version");
    expect(md).toContain("图表来源未唯一绑定");
  });

  it("keeps document order, supporting text and per-finding evidence in inert HTML and Markdown", async () => {
    const view: ScientificReportView = { ...report, report: { ...report.report!,
      research_question: '<img src=x onerror="alert(1)">',
      method_summary: "波长 1.54184 Å。波长 1.54184 Å。保留精确源版本。",
      discussion: { text: "讨论正文", fact_refs: [], evidence_refs: ["discussion-evidence"] },
      supporting_results: [{ description: "支持结果正文", result_item_ref: "saved-result-item" }],
    }, table_sources: [{ table_ref: "t", title: '<script>alert("title")</script>', artifact_ids: [] }] };
    fetchMock.mockResolvedValueOnce(Response.json(view));
    const response = await GET(request(), params("zip"));
    const files = unzipSync(new Uint8Array(await response.arrayBuffer()));
    const html = strFromU8(files["report.html"]), md = strFromU8(files["report.md"]);
    expect(html).toContain('<nav aria-label="报告章节">');
    expect(html).toContain('<details><summary>研究问题</summary>');
    expect(html.indexOf("摘要</h2>")).toBeLessThan(html.indexOf("研究问题</summary>"));
    expect(html.indexOf("主要数据表</h2>")).toBeLessThan(html.indexOf("科学讨论</h2>"));
    expect(md.indexOf("## 主要数据表")).toBeLessThan(md.indexOf("## 科学讨论"));
    for (const content of [html, md]) {
      expect(content.match(/波长 1.54184 Å。/g)).toHaveLength(1);
      expect(content).toContain("支持结果正文");
      expect(content).toContain("saved-result-item");
      expect(content).toContain("discussion-evidence");
      expect(content).toContain("peak");
    }
    expect(html).toContain("&lt;img");
    expect(html).toContain("&lt;script&gt;");
    expect(html).not.toContain("<script");
    expect(html).not.toContain("<img src=x");
  });

  it.each(["missing", "checksum", "oversize"])("refuses an incomplete ZIP on artifact %s failures", async (failure) => {
    fetchMock.mockResolvedValueOnce(Response.json(figureReport));
    const bad = failure === "missing" ? new Response("gone", { status: 404 }) : artifactResponse(plot, "0".repeat(64));
    if (failure === "oversize") bad.headers.set("x-content-length-validated", String(9 * 1024 * 1024));
    fetchMock.mockResolvedValueOnce(bad);
    const response = await GET(request(), params("zip"));
    expect(response.status).toBe(303);
    expect(response.headers.get("content-disposition")).toBeNull();
    expect(response.headers.get("location")).toContain(failure === "oversize" ? "reason=bundle_limit" : "reason=unavailable");
  });

  it.each(["markdown", "manifest"])("exports the exact authorized %s view without caching or changing precision", async (format) => {
    fetchMock.mockResolvedValue(Response.json(report));
    const response = await GET(request(), params(format));
    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toBe("private, no-store");
    expect(response.headers.get("x-content-type-options")).toBe("nosniff");
    expect(response.headers.get("content-type")).toContain(format === "markdown" ? "text/markdown" : "application/json");
    const disposition = response.headers.get("content-disposition")!;
    expect(disposition).toContain("attachment; filename=\"agent2_report_exact");
    expect(disposition).toContain("filename*=UTF-8''XRD-");
    expect(disposition).not.toMatch(/[\r\n]/);
    const body = await response.text();
    expect(body).toBe(format === "markdown" ? buildScientificReportMarkdown(report) : buildScientificReportReproducibilityManifest(report));
    expect(body).toContain("exact_version");
    expect(body).not.toContain("private-test-session");
    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8005/api/scientific-reports/agent2_report_exact", expect.objectContaining({
      headers: { cookie: "session=private-test-session", accept: "application/json" }, cache: "no-store", redirect: "error",
    }));
  });

  it.each([[401, "auth"], [403, "forbidden"], [404, "missing"], [500, "unavailable"]])("keeps %s failures visible without exporting error bodies", async (status, reason) => {
    fetchMock.mockResolvedValue(new Response("sensitive upstream diagnostics", { status: Number(status) }));
    const response = await GET(request(), params());
    expect(response.status).toBe(303);
    expect(response.headers.get("content-disposition")).toBeNull();
    expect(response.headers.get("location")).toMatch(/^\/downloads\/error\?/);
    const target = new URL(response.headers.get("location")!, "http://127.0.0.1:3023");
    expect(target.origin).toBe("http://127.0.0.1:3023");
    expect(target.pathname).toBe("/downloads/error");
    expect(target.searchParams.get("reason")).toBe(reason);
    expect(target.searchParams.get("reportId")).toBe(report.report_id);
    expect(await response.text()).not.toContain("sensitive");
    expect(response.headers.get("cache-control")).toContain("no-store");
  });

  it.each([["markdown", "../auth"], ["shell", "agent2_report_exact"], ["markdown", "https://external.test"]])("rejects an invalid format or report identity (%s, %s)", async (format, id) => {
    expect((await GET(request(), params(format, id))).status).toBe(303);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it.each([{ ...report, report_id: "another_report" }, { ...report, report: null }, { ...report, grounding_status: "INVALID" }])("rejects missing or mismatched authoritative content", async (view) => {
    fetchMock.mockResolvedValue(Response.json(view));
    const response = await GET(request(), params());
    expect(response.status).toBe(303);
    expect(response.headers.get("location")).toContain("reason=unavailable");
  });

  it("aborts a stalled read and offers retry, then permits a fresh download", async () => {
    vi.useFakeTimers();
    fetchMock.mockImplementationOnce((_url, init) => new Promise((_resolve, reject) => {
      init!.signal!.addEventListener("abort", () => reject(new Error("read aborted")));
    }));
    const pending = GET(request(), params());
    await vi.advanceTimersByTimeAsync(10_000);
    expect((await pending).headers.get("location")).toContain("reason=timeout");
    expect(fetchMock.mock.calls[0][1]?.signal?.aborted).toBe(true);
    fetchMock.mockResolvedValueOnce(Response.json(report));
    expect((await GET(request(), params())).status).toBe(200);
    expect(vi.getTimerCount()).toBe(0);
  });

  it("cancels the upstream read when its download request is abandoned", async () => {
    const cancel = new AbortController();
    fetchMock.mockImplementationOnce((_url, init) => new Promise((_resolve, reject) => {
      init!.signal!.addEventListener("abort", () => reject(new Error("aborted")));
    }));
    const pending = GET(request(cancel.signal), params());
    await Promise.resolve();
    cancel.abort();
    expect((await pending).status).toBe(303);
    expect(fetchMock.mock.calls[0][1]?.signal?.aborted).toBe(true);
  });
});
