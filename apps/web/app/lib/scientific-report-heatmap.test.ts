import { describe, expect, it } from "vitest";
import { renderScientificReportFigure } from "./scientific-report-figure";
import { plotTablePreview } from "../../scientific-viewers/workspace/workspace-plot-table";

const fixture = (): any => ({ data: [{ type: "heatmap", x: ["A", "B"], y: ["A", "B"],
  z: [[1, 0.9733285267845752], [0.9733285267845752, 1]], zmin: -1, zmax: 1,
  colorscale: [[0, "rgb(103,0,31)"], [0.5, "rgb(247,247,247)"], [1, "rgb(5,48,97)"]], colorbar: { title: { text: "pearson" } } }], layout: {} });
const render = (payload: unknown, width = 920, title = "相关性矩阵") => {
  const result = renderScientificReportFigure(payload, title, { width, compact: true });
  expect(result).not.toBeNull();
  const doc = new DOMParser().parseFromString(result!.svg, "image/svg+xml");
  expect(doc.querySelector("parsererror")).toBeNull();
  return { ...result!, doc };
};
const cell = (doc: Document, row: number, column: number) => doc.querySelector(`[data-cell="${row}:${column}"]`)!;
const number = (el: Element, attribute: string) => Number(el.getAttribute(attribute));

describe("saved heatmap report export", () => {
  it.each([360, 640, 920])("keeps positive correlations on their absolute -1 to 1 scale at %s", width => {
    const payload = fixture(), original = JSON.stringify(payload), { doc, pointCount } = render(payload, width);
    expect(pointCount).toBe(4);
    expect(doc.querySelectorAll("[data-cell]")).toHaveLength(4);
    expect(cell(doc, 0, 0).getAttribute("fill")).toBe("rgba(5,48,97,1)");
    expect(cell(doc, 0, 1).getAttribute("data-value")).toBe("0.9733285267845752");
    expect(cell(doc, 0, 1).textContent).toContain("B · A：0.9733285267845752");
    expect(number(cell(doc, 0, 0), "y")).toBeGreaterThan(number(cell(doc, 1, 0), "y"));
    expect(doc.querySelector("[data-colorbar]")?.getAttribute("data-min")).toBe("-1");
    expect([...doc.querySelectorAll("[data-color-tick]")].map(el => el.textContent)).toEqual(["-1", "0", "1"]);
    expect(doc.querySelector("[data-plot-title]")).toBeNull();
    expect(JSON.stringify(payload)).toBe(original);
  });

  it("retains missing cells separately from zero without recomputing coefficients", () => {
    const p = fixture(); p.data[0].z = [[1, null], [0, -1]];
    const { doc, pointCount } = render(p);
    expect(pointCount).toBe(3);
    expect(cell(doc, 0, 1).getAttribute("fill")).toBe("url(#missing-cell)");
    expect(cell(doc, 1, 0).getAttribute("fill")).toBe("rgba(247,247,247,1)");
    expect(doc.documentElement.textContent).toContain("斜线格：缺失值（1）");
  });

  it("matches transposed encoded arrays and the original numeric inspector", () => {
    const p = fixture(); Object.assign(p.data[0], { x: [10, 20], y: [1, 2, 3], transpose: true,
      z: { dtype: "f8", bdata: "AAAAAAAAJkAAAAAAAAAoQAAAAAAAACpAAAAAAAAANUAAAAAAAAD4fwAAAAAAADdA", shape: "2, 3" } });
    const original = JSON.stringify(p), { doc, pointCount } = render(p);
    expect(pointCount).toBe(5);
    expect(cell(doc, 2, 1).textContent).toContain("20 · 3：23");
    expect(cell(doc, 1, 1).textContent).toContain("20 · 2：缺失");
    expect(plotTablePreview(p, 10).rows.at(-1)).toMatchObject({ x: 20, y: 3, value: 23 });
    expect(JSON.stringify(p)).toBe(original);
  });

  it("preserves nonuniform edges, descending coordinates and reversed axes", () => {
    const p = fixture(); Object.assign(p.data[0], { x: [0, 2, 5], y: [40, 30], z: [[1, 2], [3, 4]] });
    p.layout.yaxis = { autorange: "reversed" };
    const { doc } = render(p);
    expect(number(cell(doc, 0, 0), "width") / number(cell(doc, 0, 1), "width")).toBeCloseTo(2 / 3);
    expect(number(cell(doc, 0, 0), "y")).toBeGreaterThan(number(cell(doc, 1, 0), "y"));
    expect(cell(doc, 0, 0).textContent).toContain("[0, 2] · 40：1");
  });

  it("preserves explicit categorical ordering and source cell identities", () => {
    const p = fixture(); p.layout.xaxis = { categoryorder: "array", categoryarray: ["B", "A"] };
    const { doc } = render(p);
    expect(number(cell(doc, 0, 0), "x")).toBeGreaterThan(number(cell(doc, 0, 1), "x"));
    expect(cell(doc, 0, 0).textContent).toContain("A · A：1");
    expect([...doc.querySelectorAll('[data-axis="x"]')].map(el => el.textContent)).toEqual(["B", "A"]);
  });

  it("honors explicit axis ranges through clipping", () => {
    const p = fixture(); p.layout.xaxis = { range: [0, 1] };
    const { doc } = render(p);
    const clip = doc.querySelector("clipPath rect")!;
    expect(number(cell(doc, 0, 0), "x")).toBeLessThan(number(clip, "x"));
    expect(doc.querySelector('[clip-path="url(#heatmap-clip)"] [data-cell]')).not.toBeNull();
  });

  it("shares reversed, transparent and stepped color mappings with saved exports", () => {
    const p = fixture(); Object.assign(p.data[0], { reversescale: true, z: [[-1, 0], [0.1, 1]],
      colorscale: [[0, "rgba(0,0,0,0)"], [0.5, "rgba(0,0,0,0)"], [0.5, "#ffffff"], [1, "#ffffff"]] });
    const { doc } = render(p);
    expect(cell(doc, 0, 0).getAttribute("fill")).toBe("rgba(255,255,255,1)");
    expect(cell(doc, 1, 1).getAttribute("fill")).toBe("rgba(0,0,0,0)");
  });

  it("resolves a saved shared coloraxis and retains explicit colorbar labels", () => {
    const p = fixture(); p.data[0].coloraxis = "coloraxis";
    p.layout.coloraxis = { cmin: -2, cmax: 2, colorscale: [[0, "#000"], [1, "#fff"]],
      colorbar: { tickvals: [-2, 0, 2], ticktext: ["low", "middle", "high"] } };
    const { doc } = render(p);
    expect(cell(doc, 0, 0).getAttribute("fill")).toBe("rgba(191,191,191,1)");
    expect([...doc.querySelectorAll("[data-color-tick]")].map(el => el.textContent)).toEqual(["low", "middle", "high"]);
  });

  it.each([360, 640, 920])("retains all 30 long variable names using compact keys at %s", width => {
    const p = fixture(), names = Array.from({ length: 30 }, (_, i) => `材料属性_${i + 1}_对应精确来源与单位`);
    Object.assign(p.data[0], { x: names, y: names, z: names.map((_, i) => names.map((_, j) => i === j ? 1 : 0)) });
    const { doc, pointCount } = render(p, width);
    expect(pointCount).toBe(900);
    const keys = [...doc.querySelectorAll("[data-axis-key]")];
    expect(keys).toHaveLength(30);
    expect(keys.map(el => el.textContent)).toEqual(names.map((name, i) => `${i + 1} · ${name}`));
    expect([...doc.querySelectorAll('[data-axis="x"]')].every(el => /^\d+$/.test(el.textContent!))).toBe(true);
  });

  it("escapes labels and titles as inert XML", () => {
    const p = fixture(); p.data[0].x[0] = '<script>alert("bad")</script>';
    const { doc } = render(p, 360, '<img src="bad"/> & matrix');
    expect(doc.querySelector("script,img,image,foreignObject")).toBeNull();
    expect(doc.querySelector("title")?.textContent).toContain('<img src="bad"/>');
    expect(cell(doc, 0, 0).textContent).toContain('<script>alert("bad")</script>');
  });

  it("wraps long scientific axis titles without losing units", () => {
    const p = fixture(), title = "材料属性与对应的精确来源和单位（电子伏特）".repeat(4);
    p.layout = { xaxis: { title }, yaxis: { title } };
    const { doc } = render(p, 360);
    for (const axis of ["x", "y"]) {
      const lines = [...doc.querySelectorAll(`[data-axis-title="${axis}"]`)];
      expect(lines.length).toBeGreaterThan(1);
      expect(lines.map(el => el.textContent).join("")).toBe(title);
    }
  });

  it("honors coordinate and color defaults saved in the figure template", () => {
    const p = fixture(); p.layout.template = { layout: { yaxis: { autorange: "reversed" } }, data: { heatmap: [{ reversescale: true }] } };
    const { doc } = render(p);
    expect(number(cell(doc, 0, 0), "y")).toBeLessThan(number(cell(doc, 1, 0), "y"));
    expect(cell(doc, 0, 0).getAttribute("fill")).toBe("rgba(103,0,31,1)");
    p.layout.template.layout.yaxis.type = "log";
    expect(renderScientificReportFigure(p, "template log")).toBeNull();
  });

  it("keeps explicit numeric-looking category names equally spaced", () => {
    const p = fixture(); p.data[0].x = ["1", "100"];
    expect(renderScientificReportFigure(p, "ambiguous auto type")).toBeNull();
    p.layout.xaxis = { type: "category" };
    const { doc } = render(p);
    expect(number(cell(doc, 0, 0), "width")).toBe(number(cell(doc, 0, 1), "width"));
    expect(cell(doc, 0, 1).textContent).toContain("100 · A");
  });

  it.each([
    (p: any) => { p.data[0].z = [[null, null], [null, null]]; },
    (p: any) => { p.data[0].z[1] = [1]; },
    (p: any) => { p.data[0].z[0][0] = Infinity; },
    (p: any) => { p.data[0].x = [1, 1]; },
    (p: any) => { p.data[0].x = ["A", "A"]; },
    (p: any) => { p.data[0].colorscale = [[0, "url(https://bad.invalid)"], [1, "red"]]; },
    (p: any) => { p.data[0].colorscale = [[0.5, "red"], [1, "blue"]]; },
    (p: any) => { p.data[0].zauto = false; delete p.data[0].zmin; },
    (p: any) => { p.data[0].zsmooth = "best"; },
    (p: any) => { p.data[0].connectgaps = true; },
    (p: any) => { p.data[0].coloraxis = "unresolved"; },
    (p: any) => { p.data[0].xgap = 1000; },
    (p: any) => { p.layout.yaxis = { type: "log" }; },
    (p: any) => { p.layout.xaxis = { range: [1, 1] }; },
    (p: any) => { p.layout.annotations = [{ text: "saved annotation" }]; },
    (p: any) => { p.data.push({ ...p.data[0] }); },
  ])("declines invalid data or unsupported semantics instead of inventing a successful figure", change => {
    const p = fixture(); change(p);
    expect(renderScientificReportFigure(p, "invalid")).toBeNull();
  });
});
