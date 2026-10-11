import { describe, expect, it } from "vitest";
import { readSavedScatter } from "./saved-scatter";
import { sanitizePlotSpec } from "./WorkspaceGenericPlot";
import { plotTablePreview } from "./workspace-plot-table";
import { renderScientificReportFigure } from "../../app/lib/scientific-report-figure";

function scatter(mode: "none" | "numeric" | "categorical" = "none") {
  const groups = mode === "categorical" ? [{ label: "Si", pointCount: 1, validPointCount: 1 }, { label: "（缺失）", pointCount: 1, validPointCount: 1 }]
    : [{ label: "x · y", pointCount: 2, validPointCount: 2 }];
  const data = mode === "categorical" ? groups.map((group, index) => ({ type: "scatter", mode: "markers", name: group.label,
    x: [index ? 10 : 2], y: [index ? 4 : 1], customdata: [[index ? 3 : 1, index ? "last" : "first"]], marker: { size: 6, opacity: .85 } }))
    : [{ type: "scatter", mode: "markers", name: groups[0].label, x: [2, 10], y: [1, 4], customdata: [[1, "first"], [3, "last"]],
      marker: { size: 6, opacity: .85, ...(mode === "numeric" ? { color: [10, 30], coloraxis: "coloraxis" } : {}) } }];
  return {
    schemaVersion: "mdi.table-scatter/1.0", chartType: "scatter", xColumn: "x", yColumn: "y", colorColumn: mode === "none" ? null : "color", colorMode: mode,
    hoverColumns: ["label"], inputCount: mode === "numeric" ? 4 : 3, pointCount: 2, validPointCount: 2, excludedCount: mode === "numeric" ? 2 : 1,
    excludedCoordinateCount: 1, excludedColorCount: mode === "numeric" ? 1 : 0, omittedPointCount: 0, sampling: "none", traces: groups.length,
    groups, xRange: [2, 10], yRange: [1, 4], figure: { data, layout: { title: { text: "散点图" },
      xaxis: { title: { text: "x" }, type: "linear" }, yaxis: { title: { text: "y" }, type: "linear" },
      ...(mode === "numeric" ? { coloraxis: { colorscale: [[0, "#440154"], [1, "#fde725"]], colorbar: { title: { text: "color" } } } } : {}) } },
  };
}

describe("saved scatter views", () => {
  it.each(["none", "numeric", "categorical"] as const)("retains paired coordinates, source rows and hover values for %s colors", mode => {
    const source = scatter(mode), before = JSON.stringify(source);
    const parsed = readSavedScatter(source);
    expect(parsed?.pointCount).toBe(2);
    const plot = sanitizePlotSpec(source, 50000);
    expect(plot.ok).toBe(true);
    if (!plot.ok) throw Error(plot.code);
    expect(plot.data.flatMap((trace: any) => trace.customdata)).toEqual([[1, "first"], [3, "last"]]);
    expect(plot.notes?.join("")).toContain("已排除 1 行横轴或纵轴");
    if (mode === "numeric") {
      expect((plot.data[0] as any).marker.color).toEqual([10, 30]);
      expect((plot.layout.coloraxis as any).cmin).toBe(10);
      expect((plot.layout.coloraxis as any).cmax).toBe(30);
      expect(plot.notes?.join("")).toContain("另排除 1 行连续颜色");
    }
    const table = plotTablePreview(source, 100);
    expect(table.rows.map(row => [row.sourceRow, row.x, row.y, row.hover0])).toEqual([[1, 2, 1, "first"], [3, 10, 4, "last"]]);
    if (mode === "numeric") expect(table.rows.map(row => row.color)).toEqual([10, 30]);
    if (mode === "categorical") expect(table.rows.map(row => row.series)).toEqual(["Si", "（缺失）"]);
    const report = renderScientificReportFigure(source, "报告", { width: 360, compact: true });
    expect(report?.pointCount).toBe(2);
    const doc = new DOMParser().parseFromString(report!.svg, "image/svg+xml");
    expect([...doc.querySelectorAll('circle[data-source-row]')].map(point => point.getAttribute('data-source-row'))).toEqual(["1", "3"]);
    const clip = doc.querySelector('clipPath rect')!;
    for (const point of doc.querySelectorAll('circle[data-source-row]')) {
      const cx = Number(point.getAttribute('cx')), cy = Number(point.getAttribute('cy')), radius = Number(point.getAttribute('r'));
      expect(cx - radius).toBeGreaterThan(Number(clip.getAttribute('x')));
      expect(cx + radius).toBeLessThan(Number(clip.getAttribute('x')) + Number(clip.getAttribute('width')));
      expect(cy - radius).toBeGreaterThan(Number(clip.getAttribute('y')));
      expect(cy + radius).toBeLessThan(Number(clip.getAttribute('y')) + Number(clip.getAttribute('height')));
    }
    expect(doc.documentElement.textContent).toContain("已排除 1 行");
    if (mode === "numeric") {
      expect([...doc.querySelectorAll('circle[data-source-row]')].map(point => point.getAttribute('fill'))).toEqual(["#440154", "#fde725"]);
      expect(doc.documentElement.textContent).not.toContain("及密度颜色");
    }
    expect(JSON.stringify(source)).toBe(before);
  });

  it("keeps source sampling distinct from invalid values and prevents a second lossy sample", () => {
    const source = scatter();
    source.validPointCount = 100; source.inputCount = 101; source.omittedPointCount = 98;
    source.groups[0].validPointCount = 100; source.sampling = "source-order-even-with-extrema-and-groups";
    expect(readSavedScatter(source)?.notes.join("")).toContain("2 / 100");
    expect(sanitizePlotSpec(source, 1)).toEqual({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
    expect(plotTablePreview(source, 1)).toMatchObject({ totalRows: 2, rows: [{ sourceRow: 1 }] });
    const report = renderScientificReportFigure(source, "采样图")!;
    expect(new DOMParser().parseFromString(report.svg, "image/svg+xml").documentElement.textContent).toContain("2 / 100");
  });

  it.each([
    (p: any) => { p.xRange = [2, 99]; },
    (p: any) => { p.figure.data[0].customdata[1][0] = 1; },
    (p: any) => { p.figure.data[0].customdata[0][0] = 0; },
    (p: any) => { p.figure.data[0].x = ["2", "10"]; },
    (p: any) => { p.figure.data[0].y = [1, null]; },
    (p: any) => { p.pointCount = 3; },
    (p: any) => { p.excludedCount = 0; },
    (p: any) => { p.hoverColumns = ["label", "label"]; },
    (p: any) => { p.figure.data[0].customdata[0] = [1]; },
    (p: any) => { p.figure.layout.xaxis.type = "category"; },
    (p: any) => { p.figure.data[0].transforms = []; },
    (p: any) => { p.figure.data[0].marker.color = [1, 2]; },
    (p: any) => { p.schemaVersion = "mdi.table-scatter/2.0"; },
  ])("rejects inconsistent point semantics %s", mutate => {
    const source = scatter(); mutate(source);
    expect(readSavedScatter(source)).toBeNull();
    expect(sanitizePlotSpec(source, 50000)).toEqual({ ok: false, code: "PLOTLY_TRACE_INVALID" });
    expect(plotTablePreview(source, 100).rows).toEqual([]);
    expect(renderScientificReportFigure(source, "invalid")).toBeNull();
  });

  it("does not export invalid coordinate spans or degenerate huge constants as NaN geometry", () => {
    const source = scatter(); source.figure.data[0].x = [1e308, 1e308]; source.xRange = [1e308, 1e308];
    const report = renderScientificReportFigure(source, "constant");
    expect(report).not.toBeNull();
    expect(report!.svg).not.toMatch(/NaN|Infinity/);
    expect(renderScientificReportFigure({ data: [{ x: [-1e308, 1e308], y: [1, 2] }] }, "overflow")).toBeNull();
  });

  it.each(["none", "numeric"] as const)("bounds 50,000-point %s SVG size without discarding source rows", mode => {
    const source = scatter(mode), trace = source.figure.data[0];
    source.inputCount = source.validPointCount = source.pointCount = 50_000;
    source.excludedCount = source.excludedCoordinateCount = source.excludedColorCount = 0;
    source.groups[0].pointCount = source.groups[0].validPointCount = 50_000;
    trace.x = Array.from({ length: 50_000 }, (_, i) => i);
    trace.y = trace.x.map(i => Math.sin(i / 100));
    trace.customdata = trace.x.map(i => [i + 1, `row ${i + 1}`]);
    if (mode === "numeric") (trace.marker as any).color = trace.x;
    source.xRange = [0, 49_999]; source.yRange = [Math.min(...trace.y), Math.max(...trace.y)];
    const report = renderScientificReportFigure(source, "large")!;
    expect(report.pointCount).toBe(50_000);
    expect([...report.svg.matchAll(/data-source-row="(\d+)"/g)].map(match => Number(match[1]))).toEqual(trace.x.map(i => i + 1));
    expect(new TextEncoder().encode(report.svg).length).toBeLessThan(6 * 1024 * 1024);
    if (mode === "numeric") expect([...report.svg.matchAll(/data-density="([^"]+)"/g)].map(match => Number(match[1]))).toEqual(trace.x);
  });
});
