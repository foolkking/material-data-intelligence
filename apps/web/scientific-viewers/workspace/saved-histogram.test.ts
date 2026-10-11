import { createElement } from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HISTOGRAM_INTERVALS, readSavedHistogram } from "./saved-histogram";
import { sanitizePlotSpec, WorkspaceGenericPlot } from "./WorkspaceGenericPlot";
import { plotTablePreview } from "./workspace-plot-table";
import { renderScientificReportFigure } from "../../app/lib/scientific-report-figure";

function histogram(grouped = true) {
  const groups = grouped ? [
    { value: "A", label: "A", count: 3, binCounts: [1, 2] },
    { value: null, label: "（缺失）", count: 1, binCounts: [0, 1] },
  ] : [{ value: null, label: "能量", count: 4, binCounts: [1, 3] }];
  return {
    schemaVersion: "mdi.table-histogram/1.0", chartType: "histogram", column: "能量", groupBy: grouped ? "材料" : null,
    count: 4, inputCount: 6, excludedCount: 2, bins: 2, binEdges: [0, 1, 2], binCounts: [1, 3],
    min: 0, max: 2, mean: 1.25, median: 1.5, intervalConvention: HISTOGRAM_INTERVALS, groups,
    figure: { data: groups.map(group => ({ type: "bar", name: group.label, x: [0.5, 1.5], y: [...group.binCounts], width: [1, 1] })),
      layout: { barmode: grouped ? "stack" : "overlay", xaxis: { title: "能量", type: "linear" }, yaxis: { title: "样本数", type: "linear" } } },
  };
}

describe("saved histogram scientific views", () => {
  it("keeps group controls outside the plot, retains one visible group, and resets on source changes", async () => {
    const source = histogram(), before = JSON.stringify(source);
    const newPlot = vi.fn().mockResolvedValue(undefined), purge = vi.fn();
    const loader = async () => ({ newPlot, purge });
    const view = render(createElement(WorkspaceGenericPlot, { content: source, maximumPoints: 50000, plotlyLoader: loader }));
    await waitFor(() => expect(screen.getByRole("button", { name: "A" })).toBeEnabled());
    expect(newPlot.mock.calls.at(-1)![2].showlegend).toBe(false);
    fireEvent.click(screen.getByRole("button", { name: "A" }));
    await waitFor(() => expect(screen.getByRole("button", { name: "A" })).toBeEnabled());
    expect(screen.getByRole("button", { name: "A" })).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByRole("button", { name: "（缺失）" })).toBeDisabled();
    expect(newPlot.mock.calls.at(-1)![1][0].visible).toBe("legendonly");
    expect(JSON.stringify(source)).toBe(before);
    view.rerender(createElement(WorkspaceGenericPlot, { content: histogram(), maximumPoints: 50000, plotlyLoader: loader }));
    await waitFor(() => expect(screen.getByRole("button", { name: "（缺失）" })).toBeEnabled());
    expect(screen.getByRole("button", { name: "A" })).toHaveAttribute("aria-pressed", "true");
    view.unmount();
  });
  it.each([false, true])("uses exact saved bins in plot, table and SVG (grouped=%s)", grouped => {
    const source = histogram(grouped), before = JSON.stringify(source);
    const plot = sanitizePlotSpec(source, 50_000);
    expect(plot.ok).toBe(true);
    if (!plot.ok) throw Error(plot.code);
    expect(plot.layout.barmode).toBe(grouped ? "stack" : "overlay");
    expect(plot.data.map((trace: any) => trace.y)).toEqual(source.groups.map(group => group.binCounts));
    expect((plot.data[0] as any).customdata).toEqual([[0, 1, ")"], [1, 2, "]"]]);
    expect(plot.notes).toContain("已排除 2 行缺失、非数值或非有限值。");
    const table = plotTablePreview(source, 100);
    expect(table.rows.map(row => row.count)).toEqual(grouped ? [1, 2, 0, 1] : [1, 3]);
    expect(table.rows.map(row => [row.start, row.end, row.closed])).toEqual(grouped
      ? [[0, 1, "否"], [1, 2, "是"], [0, 1, "否"], [1, 2, "是"]] : [[0, 1, "否"], [1, 2, "是"]]);
    const result = renderScientificReportFigure(source, "能量分布")!;
    const doc = new DOMParser().parseFromString(result.svg, "image/svg+xml");
    const bars = [...doc.querySelectorAll("rect[data-bin]")];
    expect(bars.map(bar => Number(bar.getAttribute("data-count")))).toEqual(table.rows.map(row => row.count));
    expect(bars.map(bar => Number(bar.getAttribute("data-base")))).toEqual(grouped ? [0, 0, 1, 2] : [0, 0]);
    expect(bars.map(bar => Number(bar.getAttribute("height")))).toEqual(grouped ? [100, 200, 0, 100] : [100, 300]);
    if (grouped) expect(Number(bars[3].getAttribute("y")) + Number(bars[3].getAttribute("height"))).toBe(Number(bars[1].getAttribute("y")));
    expect(bars[0].textContent).toContain("[0, 1)");
    expect(bars[1].textContent).toContain("[1, 2]");
    expect(doc.documentElement.textContent).toContain("已排除 2 行");
    expect(JSON.stringify(source)).toBe(before);
  });

  it.each([360, 920])("retains exclusion and interval notes in compact report width %s", width => {
    const result = renderScientificReportFigure(histogram(), "直方图", { width, compact: true })!;
    expect(result.svg).toContain("已排除 2 行");
    const doc = new DOMParser().parseFromString(result.svg, "image/svg+xml");
    expect([...doc.querySelectorAll("[data-plot-footer]")].map(item => item.textContent).join("")).toContain("最后一个区间包含右端点");
  });

  it("bounds table rows and refuses to sample histogram counts", () => {
    const source = histogram();
    expect(plotTablePreview(source, 1).rows).toHaveLength(1);
    expect(plotTablePreview(source, 1).totalRows).toBe(4);
    expect(sanitizePlotSpec(source, 3)).toEqual({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
  });

  it.each([
    (p: any) => { p.binCounts = [2, 2]; },
    (p: any) => { p.binEdges = [0, 0, 2]; },
    (p: any) => { p.excludedCount = 0; },
    (p: any) => { p.groups[0].binCounts = [2, 1]; },
    (p: any) => { p.figure.data[0].y = [2, 1]; },
    (p: any) => { p.figure.data[0].x = [0, 2]; },
    (p: any) => { p.figure.data[0].width = [0.8, 0.8]; },
    (p: any) => { p.figure.layout.barmode = "group"; },
    (p: any) => { p.figure.layout.yaxis.type = "log"; },
    (p: any) => { p.figure.data[0].base = 2; },
    (p: any) => { p.figure.data[0].visible = "legendonly"; },
    (p: any) => { p.schemaVersion = "mdi.table-histogram/2.0"; },
  ])("rejects inconsistent or unsupported saved semantics %s", change => {
    const source = histogram(); change(source);
    expect(readSavedHistogram(source)).toBeNull();
    expect(sanitizePlotSpec(source, 50000)).toEqual({ ok: false, code: "PLOTLY_TRACE_INVALID" });
    expect(renderScientificReportFigure(source, "invalid")).toBeNull();
    expect(plotTablePreview(source, 100).rows).toEqual([]);
  });

  it("keeps generic stacked bars unsupported instead of assuming histogram semantics", () => {
    const { figure } = histogram();
    expect(renderScientificReportFigure(figure, "arbitrary stack")).toBeNull();
  });
});
