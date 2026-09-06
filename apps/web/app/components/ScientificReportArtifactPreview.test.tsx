import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import {
  ScientificReportArtifactPreview,
  scientificReportTableRowKeys,
} from "./ScientificReportArtifactPreview";

const getPlannerArtifactContent = vi.hoisted(() => vi.fn());

vi.mock("../lib/planner-api", () => ({ getPlannerArtifactContent }));

describe("ScientificReportArtifactPreview", () => {
  it("renders a bounded persisted figure preview without recomputation", async () => {
    getPlannerArtifactContent.mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({
      artifactType: "structure.coordination_hist_plot",
      series: [{ name: "All sites", x: [6], y: [1] }],
    })).buffer);
    render(<ScientificReportArtifactPreview jobId="job-1" artifactId="artifact-1" kind="figure" title="配位数分布" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("img", { name: "配位数分布持久化数据预览" })).toBeInTheDocument();
    expect(screen.getByText(/共显示 1\/1 个有限数据点；抽样策略：无抽样/)).toBeInTheDocument();
    expect(getPlannerArtifactContent).toHaveBeenCalledWith("job-1", "artifact-1", { maximumBytes: 8 * 1024 * 1024 });
  });

  it("maps authorization and missing-artifact failures to stable safe states", async () => {
    getPlannerArtifactContent.mockRejectedValueOnce({ status: 403, message: "forbidden" });
    const { rerender } = render(<ScientificReportArtifactPreview jobId="job-denied" artifactId="artifact-denied" kind="figure" title="受限图形" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("ARTIFACT_ACCESS_DENIED");

    getPlannerArtifactContent.mockRejectedValueOnce({ status: 404, message: "missing" });
    rerender(<ScientificReportArtifactPreview jobId="job-missing" artifactId="artifact-missing" kind="table" title="缺失表格" />);
    fireEvent.click(screen.getByRole("button", { name: "在报告内查看" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("ARTIFACT_NOT_FOUND");
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
    expect(screen.getByText(/共显示 2\/2 个有限数据点；抽样策略：无抽样/)).toBeInTheDocument();
  });

  it("uses deterministic extrema-preserving sampling and discloses shown/total/strategy", async () => {
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
    expect(screen.getByText(/共显示 96\/120 个有限数据点；抽样策略：固定端点 \+ 全局最小\/最大值 \+ 分桶局部极值/)).toBeInTheDocument();
    expect(container.querySelectorAll("circle")).toHaveLength(96);
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

    expect(await screen.findByRole("group", { name: "权威坐标轴信息" })).toBeInTheDocument();
    expect(screen.getByText("X 轴 · k-path (Å⁻¹)")).toBeInTheDocument();
    expect(screen.getByText("范围：0 至 1")).toBeInTheDocument();
    expect(screen.getByText("刻度：Γ · M · X")).toBeInTheDocument();
    expect(screen.getByText("Y 轴 · Energy (eV)")).toBeInTheDocument();
    expect(screen.getByText("范围：-2 至 3")).toBeInTheDocument();
    expect(screen.getByText("刻度：-2 · 0 · 3")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "能带结构持久化数据预览" }).querySelector("desc")).toHaveTextContent(
      "k-path (Å⁻¹)，范围 0 至 1，刻度 Γ · M · X",
    );
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
    const xCoordinates = Array.from(container.querySelectorAll("circle")).map((point) => Number(point.getAttribute("cx")));
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
    expect(screen.getByText(/共显示 2\/2 个有限数据点；抽样策略：无抽样/)).toBeInTheDocument();
    expect(screen.getAllByText("实验 XRD").length).toBeGreaterThanOrEqual(2);
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

  it("discloses exact omitted row and column counts for bounded table previews", async () => {
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
    expect(screen.getByText(/显示前 24 行；另有 2 行未显示；显示前 8 列，另有 2 列未显示/)).toBeInTheDocument();
    expect(screen.getByText("查看未显示列（2）")).toBeInTheDocument();
    fireEvent.click(screen.getByText("查看未显示列（2）"));
    expect(screen.getByText("temperature")).toBeInTheDocument();
    expect(screen.getByText("pressure")).toBeInTheDocument();
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
    expect(await screen.findByRole("alert")).toHaveTextContent("SOURCE_MISSING");
    expect(screen.queryByRole("img")).toBeNull();
  });

  it.each([
    [401, "ARTIFACT_SESSION_EXPIRED"],
    [403, "ARTIFACT_ACCESS_DENIED"],
    [404, "ARTIFACT_NOT_FOUND"],
    [410, "ARTIFACT_GONE"],
    [413, "ARTIFACT_CONTENT_TOO_LARGE"],
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
});
