import { describe, expect, it } from "vitest";
import { renderScientificReportFigure } from "./scientific-report-figure";

const symbols = "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn".split(" ");
function fixture(counts = [1, 0.5, 0.5], log = false) {
  const total = counts.reduce((sum, count) => sum + count, 0), elements = counts.map((_, i) => symbols[i]);
  return { schemaVersion: "mdi.element-histogram/1.0", artifactType: "composition.elements_hist", chartType: "bar",
    countMode: "fractional", elementCount: counts.length, omittedElementCount: 0, retainedElementValue: total, totalElementValue: total,
    fractionScope: "displayed_elements", showValues: "count",
    bars: counts.map((count, i) => ({ element: elements[i], count, fraction: count / total })),
    plotlyFigure: { data: [{ type: "bar", x: elements, y: counts, text: counts.map(String), width: 0.7 }],
      layout: { xaxis: { type: "category", categoryorder: "array", categoryarray: elements }, yaxis: { type: log ? "log" : "linear" } } } };
}
function image(payload: unknown, width = 920, title = "元素分布") {
  const result = renderScientificReportFigure(payload, title, { width });
  expect(result).not.toBeNull();
  const svg = new DOMParser().parseFromString(result!.svg, "image/svg+xml");
  expect(svg.querySelector("parsererror")).toBeNull();
  expect(result!.svg).not.toMatch(/NaN|Infinity/);
  return { result: result!, svg };
}
const number = (node: Element, key: string) => Number(node.getAttribute(key));

function formulaFixture() {
  return { schemaVersion: "mdi.project.parameter-figure/1.0", artifactType: "composition.from_formula",
    inputHash: "a".repeat(64), inputOrigin: "USER_PARAMETERS", sampleAnalysis: false,
    plotlyFigure: { data: [{ type: "bar", x: ["Ca", "O", "H"], y: [20, 40, 40] }],
      layout: { title: "Ca(OH)2 · 原子组成", xaxis: { title: "元素", type: "category" }, yaxis: { title: "原子百分比（%）", range: [0, 100] } } },
  };
}

describe("saved formula composition report images", () => {
  it.each([360, 640, 920])("retains exact element percentages and the saved 0–100 scale at %s pixels", width => {
    const payload = formulaFixture(), before = JSON.stringify(payload), { result, svg } = image(payload, width, "化学式组成");
    expect(result.pointCount).toBe(3);
    expect(result.axes[0].ticks).toBe("Ca · O · H");
    expect(result.axes[1].range).toBe("0 → 100");
    expect(result.axes[1].label).toBe("原子百分比（%）");
    const bars = [...svg.querySelectorAll("rect[data-element]")];
    expect(bars.map(node => node.getAttribute("data-element"))).toEqual(["Ca", "O", "H"]);
    expect(bars.map(node => number(node, "data-value"))).toEqual([20, 40, 40]);
    expect(number(bars[0], "height") / number(bars[1], "height")).toBeCloseTo(0.5);
    expect([...svg.querySelectorAll("text[data-value-label]")].map(node => node.textContent)).toEqual(["20%", "40%", "40%"]);
    expect(JSON.stringify(payload)).toBe(before);
  });

  it.each(["sample", "origin", "hash", "duplicate", "length", "total", "nonfinite", "unsafe_label", "extra_trace", "secondary_axis"])("declines inconsistent or unsupported formula plots: %s", fault => {
    const payload = formulaFixture(), trace = payload.plotlyFigure.data[0];
    if (fault === "sample") payload.sampleAnalysis = true;
    if (fault === "origin") payload.inputOrigin = "PLATFORM_REFERENCE";
    if (fault === "hash") payload.inputHash = "invalid";
    if (fault === "duplicate") trace.x[1] = "Ca";
    if (fault === "length") trace.y.pop();
    if (fault === "total") trace.y[0] = 25;
    if (fault === "nonfinite") trace.y[0] = NaN;
    if (fault === "unsafe_label") trace.x[0] = '<script>Ca</script>';
    if (fault === "extra_trace") payload.plotlyFigure.data.push({ ...trace });
    if (fault === "secondary_axis") Object.assign(trace, { yaxis: "y2" });
    expect(renderScientificReportFigure(payload, "化学式组成")).toBeNull();
  });
});

describe("saved element histogram report images", () => {
  it("accepts the adapter's Plotly template with inactive error-bar styling and encoded counts", () => {
    const payload = fixture();
    Object.assign(payload.plotlyFigure.layout, { template: { data: { bar: [{ type: "bar", error_x: { color: "#2a3f5f" }, error_y: { color: "#2a3f5f" } }] } } });
    Object.assign(payload.plotlyFigure.data[0], { y: { dtype: "f8", bdata: "AAAAAAAA8D8AAAAAAADgPwAAAAAAAOA/" } });
    const { svg } = image(payload);
    expect([...svg.querySelectorAll("rect[data-element]")].map(n => n.getAttribute("data-value"))).toEqual(["1", "0.5", "0.5"]);
  });
  it.each([360, 640, 920])("keeps fractional counts, labels and linear bar ratios at %s", width => {
    const payload = fixture(), original = JSON.stringify(payload), { result, svg } = image(payload, width);
    const bars = [...svg.querySelectorAll("rect[data-element]")];
    expect(result.pointCount).toBe(3);
    expect(bars.map(n => n.getAttribute("data-element"))).toEqual(["H", "He", "Li"]);
    expect(bars.map(n => n.getAttribute("data-value"))).toEqual(["1", "0.5", "0.5"]);
    expect(number(bars[1], "height") / number(bars[0], "height")).toBeCloseTo(0.5);
    expect([...svg.querySelectorAll("[data-value-label]")].map(n => n.textContent)).toEqual(["1", "0.5", "0.5"]);
    expect(JSON.stringify(payload)).toBe(original);
  });
  it("places equal log ratios at equal distances while retaining untransformed values", () => {
    const { svg, result } = image(fixture([1, 10, 100], true));
    const bars = [...svg.querySelectorAll("rect[data-element]")];
    expect(number(bars[0], "y") - number(bars[1], "y")).toBeCloseTo(number(bars[1], "y") - number(bars[2], "y"));
    expect(bars.map(n => n.getAttribute("data-value"))).toEqual(["1", "10", "100"]);
    expect(result.axes[1].label).toContain("对数刻度");
  });
  it("retains an explicit reversed logarithmic range and matching custom ticks", () => {
    const payload = fixture([1, 10, 100], true);
    Object.assign(payload.plotlyFigure.layout.yaxis, { range: [2.5, -0.5], tickmode: "array", tickvals: [1, 10, 100], ticktext: ["one", "ten", "hundred"] });
    const { svg, result } = image(payload);
    const bars = [...svg.querySelectorAll("rect[data-element]")];
    expect(number(bars[0], "height")).toBeLessThan(number(bars[1], "height"));
    expect(number(bars[1], "height")).toBeLessThan(number(bars[2], "height"));
    expect(result.axes[1].range).toBe(`${10 ** 2.5} → ${10 ** -0.5}`);
    expect(svg.querySelector('[data-tick-value="10"]')?.textContent).toBe("ten");
    const text = svg.querySelector('[data-value-label="Li"] tspan')!;
    expect(number(text, "y")).toBeGreaterThan(number(bars[2], "y") + number(bars[2], "height"));
  });
  it.each([360, 640, 920])("keeps every dense element and a common scale across panels at %s", width => {
    const { svg, result } = image(fixture(Array.from({ length: 30 }, (_, i) => 30 - i)), width);
    const panels = [...svg.querySelectorAll("[data-element-panel]")];
    expect(panels.length).toBeGreaterThan(1);
    expect(result.fit).toBe("width");
    expect([...svg.querySelectorAll("rect[data-element]")].map(n => n.getAttribute("data-element"))).toEqual(symbols);
    expect(new Set(panels.map(n => n.getAttribute("data-y-range"))).size).toBe(1);
    const bars = [...svg.querySelectorAll("rect[data-element]")];
    bars.forEach((bar, index) => expect(number(bar, "height") / (30 - index)).toBeCloseTo(number(bars[0], "height") / 30));
    for (const bar of bars) {
      expect(number(bar, "x")).toBeGreaterThan(0);
      expect(number(bar, "x") + number(bar, "width")).toBeLessThan(width);
    }
  });
  it("retains saved percentage labels and the Top-N denominator", () => {
    const payload = fixture([12]);
    Object.assign(payload, { elementCount: 4, omittedElementCount: 3, totalElementValue: 28, showValues: "percent" });
    payload.plotlyFigure.data[0].text = ["100%"];
    const { svg } = image(payload);
    expect(svg.querySelector("[data-value-label]")?.textContent).toBe("100%");
    expect(svg.documentElement.textContent).toContain("省略 3 个元素");
    expect(svg.documentElement.textContent).toContain("以显示元素的合计值为分母");
  });
  it("keeps labels hidden and preserves saved category ordering", () => {
    const payload = fixture();
    Object.assign(payload, { showValues: null });
    payload.plotlyFigure.layout.xaxis.categoryarray = ["Li", "H", "He"];
    const { svg } = image(payload);
    expect(svg.querySelectorAll("[data-value-label]")).toHaveLength(0);
    expect([...svg.querySelectorAll("rect[data-element]")].map(n => n.getAttribute("data-element"))).toEqual(["Li", "H", "He"]);
  });
  it("wraps and escapes full titles without inserting executable markup", () => {
    const title = '<script>元素与计数</script>'.repeat(10), { svg } = image(fixture(), 360, title);
    expect([...svg.querySelectorAll("[data-plot-title]")].map(n => n.textContent).join("")).toBe(title);
    expect(svg.querySelector("script, foreignObject, image")).toBeNull();
    expect(renderScientificReportFigure(fixture(), title, { compact: true })?.svg).not.toContain('data-plot-title');
  });
  it("keeps a distinct user-saved plot title in compact report previews", () => {
    const payload = fixture(), title = "选定配方的元素计数";
    Object.assign(payload.plotlyFigure.layout, { title: { text: title } });
    const result = renderScientificReportFigure(payload, "图 1", { compact: true });
    expect(result?.svg).toContain(`font-weight="600">${title}</text>`);
    expect(result?.svg).not.toContain('font-weight="600">图 1');
  });
  it.each([
    (p: ReturnType<typeof fixture>) => { p.plotlyFigure.data[0].x[0] = "Fe"; },
    (p: ReturnType<typeof fixture>) => { p.plotlyFigure.data[0].text[1] = "0"; },
    (p: ReturnType<typeof fixture>) => { Object.assign(p.plotlyFigure.data[0], { base: 2 }); },
    (p: ReturnType<typeof fixture>) => { Object.assign(p.plotlyFigure.layout, { barnorm: "percent" }); },
    (p: ReturnType<typeof fixture>) => { Object.assign(p.plotlyFigure.layout.yaxis, { rangebreaks: [] }); },
    (p: ReturnType<typeof fixture>) => { Object.assign(p.plotlyFigure.layout, { template: { layout: { yaxis: { type: "date" } } }, yaxis: {} }); },
  ])("declines contradictions and unrepresented scientific transformations", change => {
    const payload = fixture(); change(payload);
    expect(renderScientificReportFigure(payload, "元素")).toBeNull();
  });
});
