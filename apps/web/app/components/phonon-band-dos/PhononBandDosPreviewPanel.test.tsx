import "@testing-library/jest-dom/vitest";

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";

import { mapPhononBandDosPlot, PhononBandDosPreviewPanel } from "./PhononBandDosPreviewPanel";

const root = resolve(__dirname, "../../../../..");
const evidence = resolve(root, "tests/fixtures/phonon_band_dos");
const json = (name: string) => JSON.parse(readFileSync(resolve(evidence, name), "utf8"));
const payloads = {
  combined: json("phonon_band_dos.json"), summary: json("phonon_band_dos_summary.json"),
  report: json("phonon_band_dos_compatibility_report.json"), plot: json("phonon_band_dos_plot.json"),
  table: json("phonon_band_dos_table.json"), manifest: json("phonon_band_dos_manifest.json"),
};

function artifacts(combined: unknown = payloads.combined) {
  return [
    {id: "combined", type: "phonon_band_dos_json", name: "phonon_band_dos.json", content: combined},
    {id: "summary", type: "phonon_summary_json", name: "phonon_band_dos_summary.json", content: payloads.summary},
    {id: "report", type: "phonon_compatibility_json", name: "phonon_band_dos_compatibility_report.json", content: payloads.report},
    {id: "plot", type: "plotly_json", name: "phonon_band_dos_plot.json", content: payloads.plot},
    {id: "table", type: "table_json", name: "phonon_band_dos_table.json", content: payloads.table},
    {id: "manifest", type: "phonon_manifest_json", name: "phonon_band_dos_manifest.json", content: payloads.manifest},
  ];
}

afterEach(() => vi.restoreAllMocks());

describe("PhononBandDosPreviewPanel", () => {
  it("renders one shared-axis figure, selects projected DOS, exports PNG, and purges", async () => {
    const newPlot = vi.fn().mockResolvedValue(undefined);
    const purge = vi.fn();
    const downloadImage = vi.fn().mockResolvedValue(undefined);
    const view = render(<PhononBandDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({newPlot, purge, downloadImage})} />);
    expect(screen.getByTestId("phonon-band-dos-schema")).toHaveTextContent("phase10h.phonon_band_dos.v1");
    expect(screen.getByTestId("phonon-band-dos-summary")).toHaveTextContent("一致");
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    const firstLayout = newPlot.mock.calls[0][2];
    expect(firstLayout.xaxis.domain).toEqual([0, 0.72]);
    expect(firstLayout.xaxis2.domain).toEqual([0.78, 1]);
    expect(firstLayout.yaxis.title.text).toBe("频率（THz）");
    expect(newPlot.mock.calls[0][1]).toHaveLength(7);
    fireEvent.change(screen.getByTestId("phonon-band-dos-projection-selector"), {target: {value: "atom:0"}});
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(2));
    expect(newPlot.mock.calls[1][1]).toHaveLength(8);
    expect(screen.getByTestId("phonon-band-dos-live-status")).toHaveTextContent("共享频率轴");
    fireEvent.click(screen.getByTestId("phonon-band-dos-download-png"));
    await waitFor(() => expect(downloadImage).toHaveBeenCalledWith(expect.any(HTMLElement), expect.objectContaining({format: "png", width: 800, height: 500, scale: 2})));
    view.unmount();
    expect(purge).toHaveBeenCalled();
  });

  it("opens compatibility, bounded data and source details without remounting the plot", async () => {
    const newPlot = vi.fn().mockResolvedValue(undefined);
    render(<PhononBandDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({newPlot, purge: vi.fn()})} />);
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    const target = newPlot.mock.calls[0][0];
    expect(screen.queryByRole("tablist")).not.toBeInTheDocument();
    expect(screen.getByTestId("phonon-band-dos-summary")).not.toBeVisible();
    fireEvent.click(screen.getByText("一致性检查", {selector: "summary"}));
    expect(screen.getByRole("table", {name: "色散与态密度一致性检查"})).toBeInTheDocument();
    expect(screen.getByTestId("phonon-band-dos-compatibility-status")).toHaveTextContent("一致");
    expect(screen.getByRole("cell", {name: "文件校验值"})).toBeVisible();
    fireEvent.click(screen.getByText("能带数值", {selector: "summary"}));
    expect(screen.getByRole("table", {name: "组合色散采样"})).toBeInTheDocument();
    fireEvent.click(screen.getByText("态密度数值", {selector: "summary"}));
    expect(screen.getByRole("table", {name: "组合态密度采样"})).toBeInTheDocument();
    fireEvent.click(screen.getByText("数据与来源", {selector: "summary"}));
    expect(screen.getByText("phonon_band_dos.json")).toBeInTheDocument();
    expect(screen.getByText("phonon_band_dos_manifest.json")).toBeInTheDocument();
    expect(newPlot).toHaveBeenCalledTimes(1);
    expect(target.isConnected).toBe(true);
  });

  it("rejects an invalid combined bundle before Plotly initialization", () => {
    const loader = vi.fn();
    const invalid = structuredClone(payloads.combined);
    invalid.tool_id = "phonon.eigenvector";
    render(<PhononBandDosPreviewPanel artifacts={artifacts(invalid)} plotlyLoader={loader} />);
    expect(screen.getByTestId("phonon-band-dos-preview-invalid")).toHaveTextContent("PHONON_BAND_DOS_SCHEMA_INVALID");
    expect(loader).not.toHaveBeenCalled();
  });

  it("reports lazy chunk failure, retries, and retains non-plot tabs", async () => {
    const newPlot = vi.fn().mockResolvedValue(undefined);
    const loader = vi.fn().mockRejectedValueOnce(new Error("chunk missing")).mockResolvedValue({newPlot, purge: vi.fn()});
    render(<PhononBandDosPreviewPanel artifacts={artifacts()} plotlyLoader={loader} />);
    await waitFor(() => expect(screen.getByTestId("phonon-band-dos-plot-fallback")).toHaveTextContent("组合图暂时无法渲染"));
    fireEvent.click(screen.getByRole("button", {name: "重试图表"}));
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    fireEvent.click(screen.getByText("一致性检查", {selector: "summary"}));
    expect(screen.getByRole("table", {name: "色散与态密度一致性检查"})).toBeVisible();
  });

  it("downloads combined JSON locally without a network request", () => {
    const createObjectURL = vi.fn().mockReturnValue("blob:combined");
    const revokeObjectURL = vi.fn();
    Object.defineProperty(URL, "createObjectURL", {value: createObjectURL, configurable: true});
    Object.defineProperty(URL, "revokeObjectURL", {value: revokeObjectURL, configurable: true});
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    render(<PhononBandDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({newPlot: vi.fn().mockResolvedValue(undefined), purge: vi.fn()})} />);
    fireEvent.click(screen.getByText("数据与来源", {selector: "summary"}));
    fireEvent.click(screen.getByTestId("phonon-band-dos-download-json"));
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    expect(click).toHaveBeenCalledTimes(1);
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:combined");
  });

  it("refuses application-owned plot budget and unknown projection identities", () => {
    const refused = structuredClone(payloads.plot);
    refused.display.mode = "refused";
    refused.display.reason = "PHONON_BAND_DOS_PLOT_BUDGET_EXCEEDED";
    expect(mapPhononBandDosPlot(refused).ok).toBe(false);
    const unknown = mapPhononBandDosPlot(payloads.plot, "species:Na");
    expect(unknown.ok).toBe(false);
  });

  it("uses matched frequency axes in a narrow container and preserves source pairs when resizing", async () => {
    let width = 375;
    vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockImplementation(() => new DOMRect(0, 0, width, 680));
    const newPlot = vi.fn().mockResolvedValue(undefined);
    const downloadImage = vi.fn().mockResolvedValue(undefined);
    const loader = async () => ({newPlot, purge: vi.fn(), downloadImage});
    render(<PhononBandDosPreviewPanel artifacts={artifacts()} plotlyLoader={loader} />);
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    const [target, stackedData, stackedLayout] = newPlot.mock.calls[0];
    expect(stackedLayout.yaxis2).toMatchObject({matches: "y", range: stackedLayout.yaxis.range, domain: [0, 0.4]});
    expect(stackedLayout.xaxis2.anchor).toBe("y2");
    expect(stackedData.at(-1)).toMatchObject({x: payloads.plot.dos_panel.total_dos, y: payloads.plot.dos_panel.frequencies, yaxis: "y2"});
    fireEvent.click(screen.getByTestId("phonon-band-dos-download-png"));
    await waitFor(() => expect(downloadImage).toHaveBeenCalledWith(target, expect.objectContaining({width: 500, height: 900, scale: 2})));
    fireEvent.click(screen.getByText("能带数值", {selector: "summary"}));
    width = 900; fireEvent(window, new Event("resize"));
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(2));
    expect(target.isConnected).toBe(false);
    const [, wideData, wideLayout] = newPlot.mock.calls[1];
    expect(wideLayout.yaxis2).toBeUndefined();
    expect(wideLayout.yaxis.range).toEqual(stackedLayout.yaxis.range);
    expect(wideData.map((trace: {x: unknown; y: unknown}) => [trace.x, trace.y])).toEqual(stackedData.map((trace: {x: unknown; y: unknown}) => [trace.x, trace.y]));
    expect(screen.getByRole("table", {name: "组合色散采样"})).toBeVisible();
  });

  it("retains disconnected segment labels and shades only actual negative frequency ranges", () => {
    const discontinuous = structuredClone(payloads.plot);
    discontinuous.band_panel.ticks.push({...discontinuous.band_panel.ticks.at(-1), label: "Γ"});
    const mapped = mapPhononBandDosPlot(discontinuous, "atom:0", true);
    expect(mapped.ok).toBe(true);
    if (!mapped.ok) return;
    expect(mapped.layout.xaxis).toMatchObject({ticktext: ["Γ", "X", "L｜Γ"]});
    expect(mapped.data.at(-1)).toMatchObject({x: payloads.plot.dos_panel.projections[0].values, y: payloads.plot.dos_panel.frequencies, hovertemplate: expect.stringContaining("%{x:.5f}")});
    expect(mapped.layout.shapes).toHaveLength(2);
    const nonnegative = structuredClone(payloads.plot); nonnegative.shared_frequency_axis.minimum = 0;
    const positive = mapPhononBandDosPlot(nonnegative);
    if (!positive.ok) throw new Error("Expected valid mapping");
    expect(positive.layout.shapes).toEqual([]);
  });

  it("reports local JSON download failure and releases the generated URL", () => {
    Object.defineProperty(URL, "createObjectURL", {value: vi.fn().mockReturnValue("blob:combined"), configurable: true});
    const revoke = vi.fn(); Object.defineProperty(URL, "revokeObjectURL", {value: revoke, configurable: true});
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {throw new Error("download unavailable");});
    render(<PhononBandDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({newPlot: vi.fn().mockResolvedValue(undefined), purge: vi.fn()})} />);
    fireEvent.click(screen.getByText("数据与来源", {selector: "summary"}));
    fireEvent.click(screen.getByTestId("phonon-band-dos-download-json"));
    expect(screen.getByRole("alert")).toHaveTextContent("数据下载未完成");
    expect(revoke).toHaveBeenCalledWith("blob:combined");
    expect(document.querySelector('a[download="phonon-band-dos.json"]')).toBeNull();
  });

  it("distinguishes withheld plot values from empty scientific data", () => {
    const items = structuredClone(artifacts());
    const combined = items[0].content as typeof payloads.combined;
    const plot = items[3].content as typeof payloads.plot;
    combined.display.performance_mode = "refused";
    plot.display = {...plot.display, mode: "refused", reason: "PHONON_BAND_DOS_PLOT_BUDGET_EXCEEDED", numeric_values: 0, trace_count: 0, selected_projection_ids: []};
    plot.band_panel.series = []; plot.band_panel.ticks = [];
    plot.dos_panel.frequencies = []; plot.dos_panel.total_dos = []; plot.dos_panel.projections = [];
    const loader = vi.fn();
    render(<PhononBandDosPreviewPanel artifacts={items} plotlyLoader={loader} />);
    expect(screen.getByTestId("phonon-band-dos-plot-fallback")).toHaveTextContent("仍可查看一致性检查与来源信息");
    fireEvent.click(screen.getByText("能带数值", {selector: "summary"}));
    fireEvent.click(screen.getByText("态密度数值", {selector: "summary"}));
    expect(screen.getByText(/此组合结果未包含能带逐点数值/)).toBeVisible();
    expect(screen.getByText(/此组合结果未包含态密度逐点数值/)).toBeVisible();
    expect(screen.queryByText("共 0 行。")).not.toBeInTheDocument();
    expect(loader).not.toHaveBeenCalled();
    expect(screen.getByTestId("phonon-band-dos-download-png")).toBeDisabled();
  });
});
