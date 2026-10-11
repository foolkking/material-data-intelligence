import { describe, expect, it } from "vitest";
import { renderScientificReportFigure } from "./scientific-report-figure";
import { readReportHierarchy } from "./scientific-report-hierarchy-model";

function fixture(type = "sunburst") {
  return { data: [{ type, ids: ["a", "a/Cu", "b", "b/Cu"], labels: ["unary A", "Cu", "unary B", "Cu"],
    parents: ["", "a", "", "b"], values: [8, 8, 2, 2], branchvalues: "total", textinfo: "label+value", sort: false }], layout: {} };
}
function image(payload: unknown, width = 920) {
  const result = renderScientificReportFigure(payload, "保存的化学体系", { width });
  expect(result).not.toBeNull();
  expect(result!.svg).not.toMatch(/NaN|Infinity/);
  const svg = new DOMParser().parseFromString(result!.svg, "image/svg+xml");
  expect(svg.querySelector("parsererror")).toBeNull();
  return { result: result!, svg };
}
const number = (element: Element, name: string) => Number(element.getAttribute(name));
describe("saved hierarchy report export", () => {
  it("translates known composition levels while retaining original labels in source titles", () => {
    const payload = { artifactType: "composition.chem_sys_treemap", ...fixture("treemap") };
    payload.data[0].labels[0] = "binary (N=8, 80.0%)";
    const { svg } = image(payload, 360), row = svg.querySelector('[data-node-index="a"]')!;
    expect(row.querySelector("title")?.textContent).toContain("binary (N=8, 80.0%)");
    expect([...row.querySelectorAll("text")].map(n => n.textContent).join(" ")).toContain("二元体系 · 8");
  });
  it("keeps explicitly requested root and parent proportions inspectable", () => {
    const payload = fixture(); payload.data[0].textinfo = "label+percent root+percent parent";
    const { svg } = image(payload, 360), row = svg.querySelector('[data-node-index="a/Cu"]')!;
    expect(row.textContent).toContain("80%（全图）");
    expect(row.textContent).toContain("100%（父分组）");
  });
  it("distinguishes the full-tree denominator from the selected entry, including templates", () => {
    const payload = fixture();
    Object.assign(payload.data[0], { level: "a", texttemplate: "%{label}<br>%{percentRoot:.1%}<br>%{percentEntry:.1%}" });
    const { svg } = image(payload, 360), row = svg.querySelector('[data-node-index="a/Cu"]')!;
    expect(row.textContent).toContain("80%（全图）");
    expect(row.textContent).toContain("100%（当前范围）");
  });
  it.each(["treemap", "sunburst"])("keeps repeated labels separate by ID in %s geometry and the index", type => {
    const payload = fixture(type), original = JSON.stringify(payload), { svg, result } = image(payload);
    expect(result.pointCount).toBe(4);
    expect(svg.querySelector('[data-node="a/Cu"]')?.getAttribute("data-parent")).toBe("a");
    expect(svg.querySelector('[data-node="b/Cu"]')?.getAttribute("data-parent")).toBe("b");
    expect(svg.querySelector('[data-node-index="a/Cu"]')?.textContent).toContain("unary A / Cu · 8");
    expect(svg.querySelector('[data-node-index="b/Cu"]')?.textContent).toContain("unary B / Cu · 2");
    expect(JSON.stringify(payload)).toBe(original);
  });
  it.each([360, 640, 920])("retains root area ratios in treemaps at %s", width => {
    const { svg } = image(fixture("treemap"), width);
    const a = svg.querySelector('[data-node="a"]')!, b = svg.querySelector('[data-node="b"]')!;
    expect(number(a, "width") * number(a, "height") / (number(b, "width") * number(b, "height"))).toBeCloseTo(4);
    for (const node of svg.querySelectorAll("rect[data-node]")) {
      expect(number(node, "x")).toBeGreaterThanOrEqual(20);
      expect(number(node, "x") + number(node, "width")).toBeLessThanOrEqual(width - 19.999);
    }
  });
  it("retains root angular ratios and nests children in the same angle", () => {
    const { svg } = image(fixture());
    const a = svg.querySelector('[data-node="a"]')!, child = svg.querySelector('[data-node="a/Cu"]')!, b = svg.querySelector('[data-node="b"]')!;
    expect(number(a, "data-span") / number(b, "data-span")).toBeCloseTo(4);
    expect(number(a, "data-start")).toBe(number(child, "data-start"));
    expect(number(a, "data-span")).toBe(number(child, "data-span"));
    expect(number(a, "data-outer-radius")).toBe(number(child, "data-inner-radius"));
  });
  it.each(["treemap", "sunburst"])("keeps unallocated parent total instead of inflating saved children in %s", type => {
    const payload = fixture(type); payload.data[0].values[1] = 4;
    const { svg } = image(payload);
    const parent = svg.querySelector('[data-node="a"]')!, child = svg.querySelector('[data-node="a/Cu"]')!;
    if (type === "sunburst") expect(number(child, "data-span") / number(parent, "data-span")).toBeCloseTo(0.5);
    expect(child.getAttribute("data-value")).toBe("4");
    expect(child.getAttribute("data-total")).toBe("4");
  });
  it("calculates remainder area without replacing the original saved values", () => {
    const payload = fixture(); payload.data[0].branchvalues = "remainder"; payload.data[0].values = [2, 8, 0, 2];
    const { svg } = image(payload);
    const parent = svg.querySelector('[data-node="a"]')!, child = svg.querySelector('[data-node="a/Cu"]')!;
    expect(parent.getAttribute("data-value")).toBe("2"); expect(parent.getAttribute("data-total")).toBe("10");
    expect(number(child, "data-span") / number(parent, "data-span")).toBeCloseTo(0.8);
    expect(svg.querySelector('[data-node-index="a"]')?.textContent).toContain("本组 2；含子分组合计 10");
  });
  it("honors a selected level, depth and domain while disclosing hidden nodes", () => {
    const payload = fixture(); Object.assign(payload.data[0], { level: "a", maxdepth: 1, domain: { x: [0.25, 0.75], y: [0.1, 0.9] } });
    const { result, svg } = image(payload, 360);
    expect(result.pointCount).toBe(1);
    expect(svg.querySelectorAll("[data-node]")).toHaveLength(1);
    expect(svg.documentElement.textContent).toContain("隐藏 1 个节点");
    expect(svg.documentElement.textContent).toContain("显示分组：unary A");
  });
  it("preserves full-circle paths, zero-value index rows and saved sorting", () => {
    const payload = fixture(); payload.data[0].values = [10, 10, 0, 0]; payload.data[0].sort = true;
    const { svg } = image(payload);
    expect(svg.querySelector('[data-node="a"]')?.getAttribute("d")?.match(/A/g)).toHaveLength(2);
    expect(svg.querySelector('[data-node-index="b/Cu"]')?.getAttribute("data-value")).toBe("0");
    expect(svg.querySelectorAll("[data-node-index]")).toHaveLength(4);
  });

  it.each(["treemap", "sunburst"])("does not export impossible tiny parent totals as %s", type => {
    const payload = fixture(type);
    payload.data[0].values = [1e-12, 5e-11, 2e-12, 2e-12];
    payload.data[0].textinfo = "label+percent parent";
    expect(renderScientificReportFigure(payload, "图")).toBeNull();
  });

  it.each([1e308, -1e308])("reduces finite rotations before converting %s degrees to geometry", rotation => {
    const payload = fixture(); Object.assign(payload.data[0], { rotation });
    const before = JSON.stringify(payload), { svg } = image(payload);
    Object.assign(payload.data[0], { rotation: rotation % 360 });
    const expected = image(payload).svg;
    expect([...svg.querySelectorAll("path[data-node]")].map(node => node.getAttribute("d")))
      .toEqual([...expected.querySelectorAll("path[data-node]")].map(node => node.getAttribute("d")));
    Object.assign(payload.data[0], { rotation });
    expect(JSON.stringify(payload)).toBe(before);
  });
  it("keeps complete escaped labels and IDs even when tiny cells cannot fit text", () => {
    const payload = fixture("treemap"); payload.data[0].labels[1] = '<script>Fe2O3 & Cu</script>'.repeat(12);
    payload.data[0].ids[1] = '<node & "a">';
    const { svg } = image(payload, 360);
    expect(svg.querySelector("script, foreignObject")).toBeNull();
    const row = [...svg.querySelectorAll("[data-node-index]")].find(n => n.getAttribute("data-node-index") === payload.data[0].ids[1])!;
    expect(row.textContent).toContain(payload.data[0].labels[1]);
  });
  it.each([
    (p: ReturnType<typeof fixture>) => { p.data[0].parents[0] = "a/Cu"; },
    (p: ReturnType<typeof fixture>) => { p.data[0].values[1] = 20; },
    (p: ReturnType<typeof fixture>) => { p.data[0].values = [0, 0, 0, 0]; },
    (p: ReturnType<typeof fixture>) => { Object.assign(p.data[0], { marker: { colors: [1, 2, 3, 4] } }); },
    (p: ReturnType<typeof fixture>) => { Object.assign(p.data[0], { texttemplate: "%{unvalidatedOtherFact}" }); },
  ])("declines invalid topology or unrepresented scientific encodings", mutate => {
    const payload = fixture(); mutate(payload);
    expect(readReportHierarchy(payload)).toBeNull();
    expect(renderScientificReportFigure(payload, "图")).toBeNull();
  });
});
