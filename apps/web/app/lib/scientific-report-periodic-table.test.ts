import { describe, expect, it } from "vitest";
import { savedPeriodicTableFixture as fixture } from "../../scientific-viewers/workspace/saved-periodic-table.fixture";
import { renderScientificReportFigure } from "./scientific-report-figure";

const svg = (payload: unknown, width = 920, compact = false, title = "材料元素统计") => {
  const result = renderScientificReportFigure(payload, title, { width, compact });
  expect(result).not.toBeNull();
  return new DOMParser().parseFromString(result!.svg, "image/svg+xml");
};
const cell = (doc: Document, x: number, y: number) => doc.querySelector(`rect[data-layer="2"][data-x="${x}"][data-y="${y}"]`)!;

describe("periodic-table report images", () => {
  it.each([false, true])("retains exact elements, saved coordinates, colors and original counts (log=%s)", log => {
    const payload = fixture(log), original = JSON.stringify(payload), doc = svg(payload);
    expect(renderScientificReportFigure(payload, "test")?.pointCount).toBe(4);
    expect([...doc.querySelectorAll("[data-element]")].map(el => [el.getAttribute("data-element"), el.getAttribute("data-value")]))
      .toEqual([["Fe", "12"], ["Cu", "1"], ["Si", "3"], ["O", "12"]]);
    expect(cell(doc, 10, 6).getAttribute("fill")).toBe("rgba(68,1,84,1)");
    expect(cell(doc, 7, 6).getAttribute("fill")).toBe("rgba(253,231,37,1)");
    expect(cell(doc, 15, 8).getAttribute("fill")).toBe(cell(doc, 7, 6).getAttribute("fill"));
    expect(Number(cell(doc, 7, 6).getAttribute("y"))).toBeGreaterThan(Number(cell(doc, 15, 8).getAttribute("y")));
    expect(doc.querySelector('[data-element="Fe"] title')?.textContent).toBe("Fe · 出现次数：12");
    expect(doc.querySelector("[data-colorbar]")?.getAttribute("data-min")).toBe(log ? "0" : "1");
    expect(doc.querySelector("[data-colorbar]")?.getAttribute("data-max")).toBe(String(log ? Math.log10(12) : 12));
    if (log) expect([...doc.querySelectorAll("[data-color-tick]")].map(el => el.textContent)).toEqual(["1", "2", "10"]);
    expect(JSON.stringify(payload)).toBe(original);
  });

  it.each([360, 640, 920])("keeps compact and standalone titles distinct at width %s", width => {
    const title = "已保存材料元素的统计与精确版本".repeat(5);
    const compact = svg(fixture(), width, true, title), full = svg(fixture(), width, false, title);
    expect(compact.querySelector("[data-plot-title]")).toBeNull();
    expect([...full.querySelectorAll("[data-plot-title]")].map(el => el.textContent).join("")).toBe(title);
    expect(compact.documentElement.getAttribute("viewBox")).toContain(`0 0 ${width} `);
    expect(full.querySelector("parsererror")).toBeNull();
  });

  it("uses explicit color bounds and retains reversal, step colors and transparency", () => {
    const p = fixture(), main = p.plotlyFigure.data[2];
    main.zmin = 0; main.zmax = 20; main.colorscale = [[0, "#000000"], [1, "#ffffff"]];
    expect(cell(svg(p), 7, 6).getAttribute("fill")).toBe("rgba(153,153,153,1)");
    Object.assign(main, { reversescale: true });
    expect(cell(svg(p), 7, 6).getAttribute("fill")).toBe("rgba(102,102,102,1)");
    Object.assign(main, { reversescale: false, colorscale: [[0,"rgba(0,0,0,0)"],[0.5,"rgba(0,0,0,0)"],[0.5,"#ffffff"],[1,"#ffffff"]] });
    expect(cell(svg(p), 10, 6).getAttribute("fill")).toBe("rgba(0,0,0,0)");
    expect(cell(svg(p), 7, 6).getAttribute("fill")).toBe("rgba(255,255,255,1)");
  });

  it("matches automatic midpoint and constant-value color ranges", () => {
    const p = fixture(), main = p.plotlyFigure.data[2];
    main.colorscale = [[0,"#000"],[1,"#fff"]]; main.zauto = true;
    Object.assign(main, { zmid: 0 });
    expect(cell(svg(p), 7, 6).getAttribute("fill")).toBe("rgba(255,255,255,1)");
    expect(svg(p).querySelector('[data-colorbar]')?.getAttribute('data-min')).toBe('-12');
    Object.assign(main, { zmid: undefined });
    for (const key of Object.keys(p.elementValues) as Array<keyof typeof p.elementValues>) p.elementValues[key] = 1;
    main.z = main.z.map(row => row.map(v => v === null ? null : 1));
    expect(cell(svg(p), 7, 6).getAttribute("fill")).toBe("rgba(128,128,128,1)");
  });

  it("preserves missing elements and zero counts without coloring a log zero", () => {
    const p = fixture(true);
    p.elementValues.Cu = 0; p.plotlyFigure.data[2].z[6][10] = null;
    p.plotlyFigure.layout.annotations[144].text = "H";
    const doc = svg(p);
    expect(doc.querySelector('[data-element="Cu"]')?.getAttribute('data-value')).toBe('0');
    expect(doc.querySelector('[data-element="H"]')?.hasAttribute('data-value')).toBe(false);
    expect(doc.querySelector('rect[data-layer="2"][data-x="10"][data-y="6"]')).toBeNull();
  });

  it("escapes titles and retains exact fractional values", () => {
    const p = fixture();
    p.countMode = "fractional"; p.elementValues.Cu = 1.123456789012345; p.plotlyFigure.data[2].z[6][10] = p.elementValues.Cu;
    const doc = svg(p, 360, false, '<script>alert("x")</script> & values');
    expect(doc.querySelector('script')).toBeNull();
    expect(doc.querySelector('[data-element="Cu"] title')?.textContent).toContain('累计原子分数：1.123456789012345');
  });

  it("declines contradictory or unresolved scales instead of inventing an image", () => {
    const p = fixture(true); p.elementValues.Fe = 100;
    expect(renderScientificReportFigure(p, "invalid")).toBeNull();
    const unresolved = fixture(); Object.assign(unresolved.plotlyFigure.data[2], {colorscale:"Viridis"});
    expect(renderScientificReportFigure(unresolved, "unresolved")).toBeNull();
  });
});
