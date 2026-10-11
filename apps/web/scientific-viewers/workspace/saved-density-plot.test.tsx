import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { densityPointColor, readSavedDensityPlot, savedNumericVector } from "./saved-density-plot";
import { sanitizePlotSpec, WorkspaceGenericPlot } from "./WorkspaceGenericPlot";
import { renderScientificReportFigure } from "../../app/lib/scientific-report-figure";

function fixture(): any {
  return {
    data: [{ type: "scattergl", mode: "markers", x: [1, 2, 3], y: [1.1, 1.9, 3.2], xaxis: "x", yaxis: "y",
      marker: { color: [0, 0.5, 1], coloraxis: "coloraxis", symbol: "circle" } }],
    layout: {
      title: { text: "Prediction Density Scatter" },
      xaxis: { title: { text: "y_true" }, domain: [0, 1], anchor: "y" },
      yaxis: { title: { text: "y_pred" }, domain: [0, 1], anchor: "x" },
      coloraxis: { colorscale: [[0, "#000000"], [1, "#ffffff"]], colorbar: { title: { text: "Point<br>Density" } } },
      shapes: [
        { type: "line", x0: 1, x1: 3, y0: 1, y1: 3, xref: "x", yref: "y", line: { color: "gray", dash: "dash", width: 1 }, layer: "below" },
        { type: "line", x0: 1, x1: 3, y0: 1.08, y1: 3.21, xref: "x", yref: "y", line: { color: "navy", dash: "dash", width: 2 } },
      ],
      annotations: [
        { text: "LS fit: y = 1.065x + 0.015", x: 0.98, y: 0.02, xref: "paper", yref: "paper", showarrow: false },
        { text: "MAE = 0.1333<br>R<sup>2</sup> = 0.97<br>", x: 0.02, y: 0.98, xref: "paper", yref: "paper", showarrow: false },
      ],
    },
  };
}

const encoded = (values: number[]) => ({ dtype: "f8", bdata: btoa(String.fromCharCode(...new Uint8Array(new Float64Array(values).buffer))) });

describe("saved density scatter semantics", () => {
  function rawFixture(): any {
    const p = fixture();
    p.data[0].x = [0.1, 0.1, 0.1]; p.data[0].y = [0.1, 0.1, 0.1];
    p.data[0].marker = { color: "#287d74", size: 6 };
    delete p.layout.coloraxis;
    p.layout.meta = { schemaVersion: "mdi.raw-parity-scatter/1.0" };
    p.layout.shapes = p.layout.shapes.slice(0, 1);
    p.layout.annotations = [{ text: "R² 未定义（目标值为常量）<br>核密度未估计，显示原始散点。", x: 0, y: 1, xref: "paper", yref: "paper", showarrow: false }];
    return p;
  }

  it.each([360, 920])("preserves explicitly saved raw scatter at width %s without density or fit invention", width => {
    const p = rawFixture(), before = JSON.stringify(p);
    const output = renderScientificReportFigure(p, "常量目标", { width, compact: true })!;
    expect(output.pointCount).toBe(3);
    const doc = new DOMParser().parseFromString(output.svg, "image/svg+xml");
    expect(doc.querySelectorAll("circle")).toHaveLength(3);
    expect([...doc.querySelectorAll("circle")].map(c => c.getAttribute("fill"))).toEqual(Array(3).fill("#287d74"));
    expect(doc.querySelectorAll("[data-colorbar], [data-density]")).toHaveLength(0);
    expect(doc.querySelectorAll("[data-saved-line]")).toHaveLength(1);
    expect(output.svg).toContain("R² 未定义");
    expect(output.svg).not.toMatch(/NaN|Infinity|及密度颜色/u);
    const spec = sanitizePlotSpec(p, 3);
    expect(spec).toMatchObject({ ok: true, data: [{ x: [0.1, 0.1, 0.1], marker: { color: "#287d74" } }] });
    if (spec.ok) { expect(spec.layout).not.toHaveProperty("coloraxis"); expect(spec.data[0].marker).not.toHaveProperty("coloraxis"); }
    expect(JSON.stringify(p)).toBe(before);
  });

  it.each([
    (p: any) => { p.layout.meta.schemaVersion = "mdi.raw-parity-scatter/2.0"; },
    (p: any) => { p.layout.meta.extra = "unrecognized"; },
    (p: any) => { p.data[0].marker.color = [1, 2, 3]; },
    (p: any) => { p.layout.coloraxis = { showscale: false }; },
    (p: any) => { p.layout.annotations[0].text = '<img src="https://bad.invalid">'; },
  ])("rejects raw-scatter schema mismatches and unsupported semantics", change => {
    const p = rawFixture(); change(p);
    expect(readSavedDensityPlot(p)).toBeNull();
    expect(renderScientificReportFigure(p, "预测")).toBeNull();
    expect(sanitizePlotSpec(p, 3)).toMatchObject({ ok: false });
  });

  it("keeps sparse raw points wholly inside automatic plot bounds and honors explicit saved ranges", () => {
    const p = rawFixture(); p.data[0].y = [1, 2, 3]; delete p.layout.shapes;
    const doc = new DOMParser().parseFromString(renderScientificReportFigure(p, "常量目标", { width: 360 })!.svg, "image/svg+xml");
    const bounds = doc.querySelector("clipPath rect")!;
    const top = Number(bounds.getAttribute("y")), bottom = top + Number(bounds.getAttribute("height"));
    for (const point of doc.querySelectorAll("circle")) {
      const y = Number(point.getAttribute("cy")), radius = Number(point.getAttribute("r"));
      expect(y - radius).toBeGreaterThan(top); expect(y + radius).toBeLessThan(bottom);
    }
    p.layout.yaxis.range = [1, 3];
    expect(renderScientificReportFigure(p, "常量目标")!.axes[1].range).toBe("1 至 3");
  });

  it("keeps typed point coordinates, density values, lines and annotations without refitting", () => {
    const payload = fixture();
    for (const key of ["x", "y"]) payload.data[0][key] = encoded(payload.data[0][key]);
    payload.data[0].marker.color = encoded([0, 0.5, 1]);
    const original = JSON.stringify(payload), plot = readSavedDensityPlot(payload)!;
    expect(plot.x).toEqual([1, 2, 3]); expect(plot.y).toEqual([1.1, 1.9, 3.2]); expect(plot.density).toEqual([0, 0.5, 1]);
    expect(plot.lines[1]).toMatchObject({ x0: 1, x1: 3, y0: 1.08, y1: 3.21, color: "#000080", width: 2 });
    expect(plot.annotations).toEqual(["最小二乘拟合： y = 1.065x + 0.015", "MAE = 0.1333\nR² = 0.97"]);
    expect([0, 0.5, 1].map(v => densityPointColor(plot, v))).toEqual(["#000000", "#808080", "#ffffff"]);
    expect(JSON.stringify(payload)).toBe(original);
  });

  it.each([360, 920])("exports every point/color and exact saved line endpoint at width %s", width => {
    const output = renderScientificReportFigure(fixture(), "回归评估", { width, compact: true })!;
    expect(output.pointCount).toBe(3);
    const doc = new DOMParser().parseFromString(output.svg, "image/svg+xml");
    expect(doc.querySelector("parsererror")).toBeNull();
    expect([...doc.querySelectorAll("circle")].map(c => c.getAttribute("fill"))).toEqual(["#000000", "#808080", "#ffffff"]);
    expect([...doc.querySelectorAll("circle")].map(c => c.getAttribute("data-density"))).toEqual(["0", "0.5", "1"]);
    const line = doc.querySelector('[data-saved-line="1"]')!;
    expect(line.getAttribute("data-y0")).toBe("1.08"); expect(line.getAttribute("data-y1")).toBe("3.21");
    expect(doc.querySelectorAll("[data-saved-line]")).toHaveLength(2);
    expect(doc.querySelectorAll("linearGradient stop")).toHaveLength(2);
    expect(doc.documentElement.textContent).toContain("MAE = 0.1333");
    expect(doc.documentElement.textContent).toContain("R² = 0.97");
    expect(output.axes.map(a => a.label)).toEqual(["真实值", "预测值"]);
  });

  it("uses saved color bounds and reversal without changing density values", () => {
    const p = fixture(); p.layout.coloraxis.cmin = 0; p.layout.coloraxis.cmax = 2; p.layout.coloraxis.reversescale = true;
    const plot = readSavedDensityPlot(p)!;
    expect(plot.density).toEqual([0, 0.5, 1]);
    expect([0, 1, 2].map(v => densityPointColor(plot, v))).toEqual(["#ffffff", "#808080", "#000000"]);
  });

  it("retains a constant density without inventing variation or invalid coordinates", () => {
    const p = fixture(); p.data[0].marker.color = [3, 3, 3];
    p.data[0].x = [1e20, 1e20, 1e20]; p.data[0].y = [1e20, 1e20, 1e20]; delete p.layout.shapes;
    const output = renderScientificReportFigure(p, "恒定值", { width: 360 })!;
    const doc = new DOMParser().parseFromString(output.svg, "image/svg+xml");
    expect([...doc.querySelectorAll("circle")].map(c => c.getAttribute("fill"))).toEqual(["#808080", "#808080", "#808080"]);
    expect(output.svg).not.toMatch(/NaN|Infinity/u);
    expect(doc.querySelector('[data-colorbar]')?.getAttribute("fill")).toBe("#808080");
  });

  it.each([false, true])("wraps distinct saved titles without losing text in compact=%s", compact => {
    const p = fixture(); p.layout.title.text = "已保存的回归模型预测结果与真实观测值对比".repeat(3);
    const doc = new DOMParser().parseFromString(renderScientificReportFigure(p, "预测", { width: 360, compact })!.svg, "image/svg+xml");
    const titles = [...doc.querySelectorAll('[data-plot-title]')];
    expect(titles.length).toBeGreaterThan(1);
    expect(titles.map(t => t.textContent).join("")).toBe(p.layout.title.text);
    expect(Number(doc.querySelector('clipPath rect')?.getAttribute("y"))).toBeGreaterThan(Number(titles.at(-1)?.getAttribute("y")) + 24);
  });

  it("omits only an identical caption from embedded density plots", () => {
    const p = fixture();
    const output = renderScientificReportFigure(p, readSavedDensityPlot(p)!.title, { compact: true })!;
    expect(output.svg).not.toContain('data-plot-title');
    expect(output.pointCount).toBe(3);
    expect(output.svg).toContain('data-annotation');
  });

  it("does not invent missing references or annotations", () => {
    const p = fixture(); delete p.layout.shapes; delete p.layout.annotations;
    const output = renderScientificReportFigure(p, "预测")!;
    expect(output.svg).not.toContain("data-saved-line="); expect(output.svg).not.toContain("data-annotation=");
    expect(output.svg).not.toContain("MAE"); expect(output.svg).not.toContain("最小二乘拟合");
  });

  it.each([
    (p: any) => { p.data[0].marker.color = [1, 2]; },
    (p: any) => { p.data[0].marker.color = [0, Infinity, 1]; },
    (p: any) => { p.data[0].marker.color = [-1e308, 0, 1e308]; },
    (p: any) => { p.data[0].x = { ...encoded([1, 2, 3]), shape: "1,3" }; },
    (p: any) => { p.data[0].marker.coloraxis = "coloraxis2"; },
    (p: any) => { p.data[0].marker.symbol = "square"; },
    (p: any) => { p.data[0].error_y = { array: [1, 2, 3] }; },
    (p: any) => { p.layout.shapes[1].type = "path"; },
    (p: any) => { p.layout.shapes[1].xref = "paper"; },
    (p: any) => { p.layout.shapes[1].y0 = NaN; },
    (p: any) => { p.layout.annotations[0].text = '<img src="https://bad.invalid">'; },
    (p: any) => { p.layout.annotations[0].showarrow = true; },
    (p: any) => { p.layout.coloraxis.colorscale = [[0, "red"], [0, "blue"]]; },
    (p: any) => { p.layout.coloraxis.colorscale[1][1] = "url(https://bad.invalid)"; },
    (p: any) => { p.layout.coloraxis.cmin = 0; },
    (p: any) => { p.layout.xaxis.type = "log"; },
    (p: any) => { p.layout.xaxis.range = [0, 5]; p.layout.xaxis.autorange = true; },
    (p: any) => { p.layout.template = { layout: { xaxis: { type: "log" } } }; },
    (p: any) => { p.layout.template = { layout: { shapes: p.layout.shapes } }; },
    (p: any) => { p.layout.template = { data: { scattergl: [{ marker: { opacity: 0 } }] } }; },
    (p: any) => { p.layout.images = [{ source: "https://bad.invalid" }]; },
  ])("rejects unsupported semantics instead of silently losing them", change => {
    const p = fixture(); change(p);
    expect(readSavedDensityPlot(p)).toBeNull();
    expect(renderScientificReportFigure(p, "预测")).toBeNull();
    expect(sanitizePlotSpec(p, 100)).toMatchObject({ ok: false });
  });

  it("keeps numerical color alignment and all reference shapes in the interactive renderer", () => {
    const p = fixture(), before = JSON.stringify(p), spec = sanitizePlotSpec(p, 3);
    expect(spec).toMatchObject({ ok: true, decimated: false, pointCount: 3, data: [{ x: p.data[0].x, y: p.data[0].y, marker: { color: p.data[0].marker.color } }],
      layout: { shapes: [{ x0: 1, y0: 1, x1: 3, y1: 3 }, { x0: 1, x1: 3, y0: 1.08, y1: 3.21 }] } });
    expect(sanitizePlotSpec(p, 2)).toMatchObject({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
    expect(JSON.stringify(p)).toBe(before);
  });

  it("shows exact saved annotations as inert text outside the interactive data area", async () => {
    render(<WorkspaceGenericPlot content={fixture()} maximumPoints={10} plotlyLoader={async () => ({ newPlot: async () => undefined, purge: () => undefined })} />);
    await waitFor(() => expect(screen.getByLabelText("已保存的图表注释")).toHaveTextContent("1.065x + 0.015"));
    expect(screen.getByLabelText("已保存的图表注释")).toHaveTextContent("R² = 0.97");
  });

  it("bounds typed arrays before decoding and preserves declared byte order", () => {
    expect(savedNumericVector(encoded([1, 2, 3]), 2)).toBeNull();
    expect(savedNumericVector({ dtype: "f8", bdata: "garbage!" })).toBeNull();
    const bytes = new Uint8Array(16), view = new DataView(bytes.buffer);
    view.setFloat64(0, 1.25, false); view.setFloat64(8, -3.5, false);
    expect(savedNumericVector({ dtype: ">f8", shape: "2", bdata: btoa(String.fromCharCode(...bytes)) })).toEqual([1.25, -3.5]);
  });
});
