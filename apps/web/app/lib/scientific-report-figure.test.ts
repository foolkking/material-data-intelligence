import { describe, expect, it } from "vitest";
import { renderScientificReportFigure } from "./scientific-report-figure";

describe("saved figure SVG export", () => {
  it.each([360, 920])("keeps more than sixteen saved tick labels at their exact nonuniform coordinates at width %s", width => {
    const values = Array.from({ length: 21 }, (_, i) => i * i / 10);
    const labels = values.map((_, i) => `K${i}`);
    const payload = { data: [{ x: [0, 40], y: [0, 1], mode: "lines" }],
      layout: { xaxis: { tickvals: values, ticktext: labels } } };
    const original = JSON.stringify(payload);
    const rendered = renderScientificReportFigure(payload, "非均匀路径", { width })!;
    const svg = new DOMParser().parseFromString(rendered.svg, "image/svg+xml");
    for (const label of labels) expect([...svg.querySelectorAll("text")].some(text => text.textContent === label)).toBe(true);
    const frame = svg.querySelector("clipPath rect")!;
    const x = Number(frame.getAttribute("x")), span = Number(frame.getAttribute("width"));
    for (const [i, value] of values.entries()) {
      const tick = svg.querySelector(`[data-axis-tick="x"][data-value="${value}"]`)!;
      expect(tick).not.toBeNull();
      expect(tick.querySelector("text")?.textContent).toBe(labels[i]);
      expect(Number(tick.querySelector("line")?.getAttribute("x1"))).toBeCloseTo(x + value / 40 * span);
    }
    expect(JSON.stringify(payload)).toBe(original);
  });
  it("keeps reversed and clipped axis labels bound before clipping, including coincident ticks", () => {
    const result = renderScientificReportFigure({ data: [{ x: [0, 10], y: [0, 1] }],
      layout: { xaxis: { range: [10, 1], tickvals: [0, 1, 1, 10], ticktext: ["outside", "X", "L", "Γ"] } } }, "反向路径", { width: 360 })!;
    const svg = new DOMParser().parseFromString(result.svg, "image/svg+xml");
    const ticks = [...svg.querySelectorAll('[data-axis-tick="x"]')];
    expect(ticks).toHaveLength(3);
    expect(ticks.map(tick => tick.querySelector("text")!.textContent).sort()).toEqual(["L", "X", "Γ"].sort());
    const pair = ticks.filter(tick => tick.getAttribute("data-value") === "1");
    expect(pair[0].querySelector("line")!.getAttribute("x1")).toBe(pair[1].querySelector("line")!.getAttribute("x1"));
    expect(pair[0].querySelector("text")!.getAttribute("y")).not.toBe(pair[1].querySelector("text")!.getAttribute("y"));
    expect(result.fit).toBe("width");
  });

  it("keeps dense Y labels at exact ticks and exposes the remaining label/value pairs", () => {
    const values = Array.from({ length: 21 }, (_, i) => i * i / 10);
    const result = renderScientificReportFigure({ data: [{ x: [0, 1], y: [0, 40] }],
      layout: { yaxis: { tickvals: values, ticktext: values.map((_, i) => `Y${i}`) } } }, "纵轴", { width: 360 })!;
    const svg = new DOMParser().parseFromString(result.svg, "image/svg+xml");
    const frame = svg.querySelector("clipPath rect")!, top = Number(frame.getAttribute("y")), height = Number(frame.getAttribute("height"));
    const ticks = [...svg.querySelectorAll('[data-axis-tick="y"]')];
    expect(ticks).toHaveLength(21);
    for (const [i, value] of values.entries()) {
      const tick = ticks.find(tick => Number(tick.getAttribute("data-value")) === value)!;
      expect(tick.querySelector("title")!.textContent).toBe(`Y${i} = ${value}`);
      expect(Number(tick.querySelector("line")!.getAttribute("y1"))).toBeCloseTo(top + height * (1 - value / 40));
      const label = tick.querySelector("text");
      if (label) expect(Number(label.getAttribute("y"))).toBeCloseTo(top + height * (1 - value / 40) + 5);
      else expect([...svg.querySelectorAll('[data-plot-footer]')].some(e => e.textContent!.includes(`Y${i} = ${value}`))).toBe(true);
    }
    const labels = ticks.filter(tick => tick.querySelector("text")).map(tick => Number(tick.querySelector("text")!.getAttribute("y"))).sort((a, b) => a - b);
    for (let i = 1; i < labels.length; i++) expect(labels[i] - labels[i - 1]).toBeGreaterThanOrEqual(21.99);
  });

  it.each([
    { tickvals: [0, NaN], ticktext: ["A", "B"] },
    { tickvals: "0,1", ticktext: ["A", "B"] },
    { tickmode: "array", ticktext: ["A", "B"] },
    { tickvals: [0, 1], ticktext: [{ label: "A" }, "B"] },
  ])("declines malformed explicit ticks instead of relabeling generated coordinates", xaxis => {
    expect(renderScientificReportFigure({ data: [{ x: [0, 1], y: [0, 1] }], layout: { xaxis } }, "invalid")).toBeNull();
  });

  it("never attaches stale custom text to automatic ticks", () => {
    const result = renderScientificReportFigure({ data: [{ x: [0, 1], y: [0, 1] }],
      layout: { xaxis: { tickmode: "auto", tickvals: [0, 1], ticktext: ["OLD_A", "OLD_B"] } } }, "auto")!;
    expect(result.svg).not.toMatch(/OLD_A|OLD_B/);
  });

  it.each([360, 920])("uses zero for interpolation residue on automatic axes at width %s without changing saved points", width => {
    const payload = { data: [{ x: [-0.05, 0, 0.04999999999999999], y: [-0.06, 0, 0.04], mode: "markers" }],
      layout: { xaxis: { range: width === 360 ? [-0.05, 0.04999999999999999] : [-0.06, 0.04] } } };
    const before = JSON.stringify(payload);
    const result = renderScientificReportFigure(payload, "残差", { width, compact: true })!;
    const svg = new DOMParser().parseFromString(result.svg, "image/svg+xml");
    for (const axis of ["x", "y"]) {
      const zero = svg.querySelector(`[data-axis-tick="${axis}"][data-value="0"]`);
      expect(zero?.querySelector("text")?.textContent).toBe("0");
    }
    expect(result.pointCount).toBe(3);
    expect(JSON.stringify(payload)).toBe(before);
  });

  it.each([[1e-18, 5e-18], [1e-18, 0.1]])("preserves genuinely small automatic values and endpoints for range %j", (min, max) => {
    const result = renderScientificReportFigure({ data: [{ x: [min, max], y: [1, 2] }] }, "微小数值", { width: 360 })!;
    const svg = new DOMParser().parseFromString(result.svg, "image/svg+xml");
    const ticks = [...svg.querySelectorAll('[data-axis-tick="x"]')];
    expect(ticks.every(tick => Number(tick.getAttribute("data-value")) > 0)).toBe(true);
    expect(ticks.find(tick => Number(tick.getAttribute("data-value")) === min)?.querySelector("text")?.textContent).toBe("1e-18");
  });

  it("preserves explicit near-zero coordinates and labels on both axes", () => {
    const axis = { range: [-0.05, 0.05], tickvals: [-1e-18, 1e-18] };
    const result = renderScientificReportFigure({ data: [{ x: [-0.05, 0.05], y: [-0.05, 0.05] }],
      layout: { xaxis: axis, yaxis: { ...axis, ticktext: ["负侧", "正侧"] } } }, "精确刻度")!;
    const svg = new DOMParser().parseFromString(result.svg, "image/svg+xml");
    for (const name of ["x", "y"]) expect([...svg.querySelectorAll(`[data-axis-tick="${name}"]`)].map(tick => Number(tick.getAttribute("data-value"))).sort()).toEqual([-1e-18, 1e-18]);
    expect([...svg.querySelectorAll('[data-axis-tick="x"] text')].map(tick => tick.textContent)).toEqual(["-1e-18", "1e-18"]);
    expect(result.svg).toContain("负侧"); expect(result.svg).toContain("正侧");
  });

  it.each([360, 920])("retains distinct tiny ticks across zero at width %s", width => {
    const result = renderScientificReportFigure({ data: [{ x: [-2e-18, 3e-18], y: [1, 2] }] }, "微小范围", { width })!;
    const svg = new DOMParser().parseFromString(result.svg, "image/svg+xml");
    const values = [...svg.querySelectorAll('[data-axis-tick="x"]')].map(tick => Number(tick.getAttribute("data-value")));
    expect(new Set(values).size).toBe(width === 360 ? 3 : 6);
    expect(values.filter(value => value !== 0)).toHaveLength(width === 360 ? 3 : 5);
    expect(values.filter(value => value !== 0).every(value => Math.abs(value) < 4e-18)).toBe(true);
  });

  it("does not export logarithmic or secondary-axis figures as misleading linear SVGs", () => {
    expect(renderScientificReportFigure({ plotlyFigure: { data: [{ x: [1, 2], y: [10, 100] }], layout: { yaxis: { type: "log" } } } }, "log plot")).toBeNull();
    expect(renderScientificReportFigure({ data: [{ x: [1, 2], y: [10, 100], yaxis: "y2" }] }, "secondary axis")).toBeNull();
  });
  it("exports backend encoded XY arrays with the same exact gaps as the interactive plot", () => {
    const result = renderScientificReportFigure({ data: [{ mode: "lines+markers", x: { dtype: "f8", bdata: "AAAAAAAAAAAAAAAAAADwPwAAAAAAAABAAAAAAAAACEAAAAAAAAAQQA==" }, y: { dtype: "f8", bdata: "AAAAAAAAAEAAAAAAAAAIQAAAAAAAAPh/AAAAAAAAFEAAAAAAAAAYQA==" } }] }, "编码数组");
    expect(result?.pointCount).toBe(4);
    const svg = new DOMParser().parseFromString(result!.svg, "image/svg+xml");
    expect(svg.querySelector("path[data-series]")!.getAttribute("d")!.match(/[ML]/g)).toEqual(["M", "L", "M", "L"]);
  });
  it("keeps static-chart gaps as separate path segments in report exports", () => {
    const payload = { chart_type: "line", series: [{ name: "含缺失区间", x: [0, 1, 2, 3, 4], y: [2, 3, null, 5, 6] }] };
    const original = JSON.stringify(payload);
    const result = renderScientificReportFigure(payload, "断点曲线");
    expect(result?.pointCount).toBe(4);
    const svg = new DOMParser().parseFromString(result!.svg, "image/svg+xml");
    expect(svg.querySelector("path[data-series]")!.getAttribute("d")!.match(/[ML]/g)).toEqual(["M", "L", "M", "L"]);
    expect(JSON.stringify(payload)).toBe(original);
  });

  it.each([920, 360])("preserves full material titles and series names while wrapping at width %s", width => {
    const title = "三个不同温度下的合成晶体径向分布函数与对应结构文件版本".repeat(3);
    const names = ["All pairs", "Cl->Cl", "Cl->Na", "Na->Cl", "Na->Na", "长材料名称与精确版本_".repeat(8)];
    const payload = { data: names.map(name => ({ name, x: [0, 1], y: [2, 3], mode: "lines" })) };
    const original = JSON.stringify(payload);
    const result = renderScientificReportFigure(payload, title, { width })!;
    const svg = new DOMParser().parseFromString(result.svg, "image/svg+xml");
    expect([...svg.querySelectorAll('[data-plot-title]')].map(text => text.textContent).join("")).toBe(title);
    const legends = [...svg.querySelectorAll('[data-legend]')];
    expect(legends.map(item => item.querySelector('text')!.textContent)).toEqual(names);
    expect(legends.at(-1)!.querySelectorAll('tspan').length).toBeGreaterThan(1);
    expect(svg.querySelectorAll('[clip-path] path[data-series]')).toHaveLength(names.length);
    legends.forEach((item, i) => {
      const curve = svg.querySelectorAll('path[data-series]')[i];
      expect(item.querySelector('line')?.getAttribute('stroke')).toBe(curve.getAttribute('stroke'));
    });
    expect(result.pointCount).toBe(12);
    const footerLines = [...svg.querySelectorAll('[data-plot-footer]')];
    expect(footerLines.map(line => line.textContent).join("").replace(/\s/g, "")).toBe("完整显示12个数据点·原始数据随报告提供");
    if (width === 360) expect(footerLines.length).toBeGreaterThan(1);
    expect(JSON.stringify(payload)).toBe(original);
  });

  it.each([920, 360])("exports backend histogram bins at their saved widths without clipping at %s", width => {
    const payload = { data: [{ type: "bar", name: "残差分布", x: [-1, 1], y: [2, 3], width: [2, 2] }],
      layout: { barmode: "overlay", xaxis: { title: "残差" }, yaxis: { title: "样本数" } } };
    const original = JSON.stringify(payload);
    const result = renderScientificReportFigure(payload, "残差分布", { width, compact: true });
    expect(result?.pointCount).toBe(2);
    const svg = new DOMParser().parseFromString(result!.svg, "image/svg+xml");
    const bars = [...svg.querySelectorAll("rect[data-bin]")];
    expect(bars).toHaveLength(2);
    expect(bars[0].textContent).toContain("[-2, 0], 2");
    expect(bars[1].textContent).toContain("[0, 2], 3");
    expect(Number(bars[0].getAttribute("x")) + Number(bars[0].getAttribute("width"))).toBeCloseTo(Number(bars[1].getAttribute("x")));
    expect(Number(bars[0].getAttribute("height")) / Number(bars[1].getAttribute("height"))).toBeCloseTo(2 / 3);
    const clip = svg.querySelector("clipPath rect")!;
    expect(Number(bars[0].getAttribute("x"))).toBeCloseTo(Number(clip.getAttribute("x")));
    expect(Number(bars[1].getAttribute("x")) + Number(bars[1].getAttribute("width"))).toBeCloseTo(Number(clip.getAttribute("x")) + Number(clip.getAttribute("width")));
    expect(JSON.stringify(payload)).toBe(original);
  });

  it.each([[2], [0, 2], [NaN, 2], [-1, 2]].map(width => ({ width })))("declines invalid saved bar widths $width", ({ width }) => {
    expect(renderScientificReportFigure({ data: [{ type: "bar", x: [1, 2], y: [2, 3], width }] }, "残差")).toBeNull();
  });

  it.each([920, 360])("leaves room between long decimal ticks and the vertical title at width %s", width => {
    const result = renderScientificReportFigure({
      data: [{ x: [0.02, 0.1], y: [0.0058796, 0.030799], mode: "lines", name: "MSD" }],
      layout: { yaxis: { title: "MSD / angstrom^2" } },
    }, "扩散拟合", { width, compact: width === 360 });
    expect(result?.pointCount).toBe(2);
    const svg = new DOMParser().parseFromString(result!.svg, "image/svg+xml");
    const tick = [...svg.querySelectorAll("text")].find(item => item.textContent === "0.0058796")!;
    // Eight glyphs at the export's 16px type size must clear the title at x=20.
    expect(Number(tick.getAttribute("x")) - 8 * 10).toBeGreaterThan(28);
    expect(Number(svg.querySelector("clipPath rect")!.getAttribute("width"))).toBeGreaterThanOrEqual(120);
    expect(svg.querySelector("path[data-series]")!.getAttribute("d")!.match(/[ML]/g)).toHaveLength(2);
  });

  const phononPlot = () => ({
    schema_version: "phase10h1.phonon_band_plot.v1", artifact_type: "phonon.band_plot",
    metadata: { discontinuities_split: true, branch_count: 6, segment_count: 2, trace_count: 12 },
    data: Array.from({ length: 6 }, (_, index) => [
      { type: "scatter", mode: "lines", legendgroup: `branch-${index}`, name: `Branch ${index + 1}`, x: [0, 0.5], y: [index - 1, index] },
      { type: "scatter", mode: "lines", legendgroup: `branch-${index}`, name: `Branch ${index + 1}`, x: [0.5, 2], y: [index + 1, index + 2] },
    ]).flat(),
    layout: { xaxis: { title: { text: "Wave vector path" }, tickvals: [0, 0.5, 2], ticktext: ["Γ", "X|L", "Γ"] },
      yaxis: { title: { text: "Frequency (THz)" }, zeroline: true } },
  });

  it.each([920, 360])("keeps phonon branch identities and separate saved segments at width %s", width => {
    const payload = phononPlot(), original = JSON.stringify(payload);
    const result = renderScientificReportFigure(payload, "声子能带", { width, compact: true });
    expect(result?.pointCount).toBe(24);
    const svg = new DOMParser().parseFromString(result!.svg, "image/svg+xml");
    expect(svg.querySelector("parsererror")).toBeNull();
    expect(svg.querySelectorAll("[data-legend]")).toHaveLength(6);
    expect(svg.querySelector('[data-legend="分支 5"]')?.textContent).toContain("Branch 6");
    for (let i = 1; i <= 6; i++) {
      const paths = [...svg.querySelectorAll(`path[data-series="Branch ${i}"]`)];
      expect(paths).toHaveLength(2);
      expect(paths[0].getAttribute("stroke")).toBe(paths[1].getAttribute("stroke"));
      expect(paths[0].getAttribute("stroke-dasharray")).toBe(paths[1].getAttribute("stroke-dasharray"));
      paths.forEach(path => expect(path.getAttribute("d")?.match(/M/g)).toHaveLength(1));
    }
    expect(svg.querySelector('path[data-series="Branch 1"]')?.getAttribute("stroke-dasharray"))
      .not.toBe(svg.querySelector('path[data-series="Branch 6"]')?.getAttribute("stroke-dasharray"));
    expect(svg.querySelector('[data-reference="zero-frequency"]')).not.toBeNull();
    expect(svg.documentElement.textContent).toContain("X|L");
    expect(svg.documentElement.textContent).toContain("频率 (THz)");
    expect(result?.axes[1].label).toBe("Frequency (THz)");
    expect(JSON.stringify(payload)).toBe(original);
  });

  it.each([
    (p: any) => { p.data[0].legendgroup = "branch-5"; },
    (p: any) => { p.data[0].name = "Branch 0"; },
    (p: any) => { p.metadata.branch_count = 5; },
    (p: any) => { p.metadata.segment_count = 3; },
    (p: any) => { p.metadata.discontinuities_split = false; },
    (p: any) => { p.data[1].line = { shape: "spline" }; },
  ])("declines inconsistent phonon branch identity or segment metadata", change => {
    const payload = phononPlot(); change(payload);
    expect(renderScientificReportFigure(payload, "声子能带")).toBeNull();
  });

  const bandPlot = () => ({
    schemaVersion: "phase10n5.electronic_band_plot.v1", frontendScientificComputation: false,
    data: [
      { type: "scatter", mode: "lines", name: "up:band-3", x: [0, 0.5, 0.5, 1.4], y: [-1, -2, 1, 2], customdata: ["g", "x", "l", "g2"] },
      { type: "scatter", mode: "lines", name: "down:band-3", x: [0, 0.5, 0.5, 1.4], y: [-1.1, -2.1, 1.1, 3.365951568], customdata: ["g", "x", "l", "g2"] },
    ],
    pathSegments: [
      { segmentId: "one", startKpointId: "g", endKpointId: "x", breakAfter: true },
      { segmentId: "two", startKpointId: "l", endKpointId: "g2", breakAfter: false },
    ],
    layout: { xaxis: { title: { text: "Reciprocal path" } }, yaxis: { title: { text: "Energy / eV" } },
      shapes: [{ type: "line", x0: 0, x1: 1.4, y0: 0, y1: 0, line: { dash: "dash" } }],
    },
  });

  it.each([920, 360])("exports saved band paths, spin styles and the Fermi reference at width %s", (width) => {
    const payload = bandPlot(), original = JSON.stringify(payload);
    const result = renderScientificReportFigure(payload, "电子能带", { width, compact: true });
    expect(result?.pointCount).toBe(8);
    const svg = new DOMParser().parseFromString(result!.svg, "image/svg+xml");
    expect(svg.querySelector("parsererror")).toBeNull();
    const paths = [...svg.querySelectorAll('path[data-series]')];
    expect(paths).toHaveLength(2);
    paths.forEach(path => {
      expect(path.getAttribute("d")?.match(/M/g)).toHaveLength(2);
      expect(path.getAttribute("d")?.match(/L/g)).toHaveLength(2);
    });
    expect(paths[0].getAttribute("stroke")).toBe(paths[1].getAttribute("stroke"));
    expect(paths[0].getAttribute("stroke-dasharray")).toBeNull();
    expect(paths[1].getAttribute("stroke-dasharray")).toBe("6 4");
    expect(svg.querySelectorAll('[data-path-break="0.5"]')).toHaveLength(1);
    const reference = svg.querySelector('[data-reference="fermi"]')!;
    expect(reference.getAttribute("y1")).toBe(reference.getAttribute("y2"));
    expect(Number(reference.getAttribute("y1"))).toBeCloseTo(24 + 3.365951568 / (3.365951568 + 2.1) * 300);
    expect(reference.getAttribute("stroke-dasharray")).toBe("6 4");
    expect(svg.documentElement.textContent).toContain("费米能级：0 eV");
    expect(result?.axes.map(axis => axis.label)).toEqual(["Reciprocal path", "Energy / eV"]);
    expect(JSON.stringify(payload)).toBe(original);
  });

  it("exports bands without inventing a missing Fermi reference", () => {
    const payload = bandPlot(); payload.layout.shapes = [];
    const result = renderScientificReportFigure(payload, "电子能带");
    expect(result?.pointCount).toBe(8);
    expect(result?.svg).not.toContain('data-reference="fermi"');
    expect(result?.svg).not.toContain("费米能级");
  });

  it("does not split a connected path solely because successive points share a distance", () => {
    const payload = bandPlot(); payload.pathSegments[0].breakAfter = false;
    const result = renderScientificReportFigure(payload, "电子能带");
    const svg = new DOMParser().parseFromString(result!.svg, "image/svg+xml");
    expect(svg.querySelector("path[data-series]")?.getAttribute("d")?.match(/M/g)).toHaveLength(1);
    expect(svg.querySelector("[data-path-break]")).toBeNull();
  });

  it.each([
    (p: any) => { p.pathSegments[0].endKpointId = "missing"; },
    (p: any) => { p.pathSegments[0].startKpointId = "missing"; },
    (p: any) => { p.pathSegments[0].breakAfter = "true"; },
    (p: any) => { p.pathSegments = undefined; },
    (p: any) => { p.data[1].customdata[1] = "g"; },
    (p: any) => { p.data[1].customdata = ["g", "l", "x", "g2"]; },
    (p: any) => { p.data[1].x[1] = 0.6; },
    (p: any) => { p.data[1].name = "unknown-spin:band-3"; },
    (p: any) => { p.layout.shapes[0].yref = "paper"; },
    (p: any) => { p.layout.shapes[0].type = "rect"; },
    (p: any) => { p.layout.shapes[0].y1 = 1; },
    (p: any) => { p.layout.shapes[0].y0 = Infinity; },
    (p: any) => { p.layout.annotations = [{ text: "not rendered" }]; },
    (p: any) => { p.schemaVersion = "unknown-band-version"; },
  ])("declines incomplete or ambiguous band semantics", (change) => {
    const payload = bandPlot(); change(payload);
    expect(renderScientificReportFigure(payload, "电子能带")).toBeNull();
  });

  it("preserves every XRD stem and source axes without joining or sampling peaks", () => {
    const x = Array.from({ length: 290 }, (_, i) => i * 0.3);
    const result = renderScientificReportFigure({ chart_type: "stem", x_axis: { label: "2theta (degrees)" }, y_axis: { label: "Relative Intensity" }, series: [{ name: "XRD peaks", x, y: x.map((_, i) => i === 27 ? 100 : 2) }], metadata: { two_theta_min: 0, two_theta_max: 90 } }, "理论 XRD");
    expect(result?.pointCount).toBe(290);
    expect(result?.svg.match(/<title>XRD peaks:/g)).toHaveLength(290);
    expect(result?.svg).toContain("2theta (degrees)");
    expect(result?.svg).toContain("Relative Intensity");
    expect(result?.svg).toContain("8.1, 100");
    expect(result?.svg).not.toContain("<polyline");
  });

  it("preserves gaps in line traces and escapes all source text", () => {
    const result = renderScientificReportFigure({ data: [{ x: [0, 1, null, 3, 4], y: [1, 2, null, 4, 5], mode: "lines", name: '<script>alert(1)</script>' }] }, '<img src="https://example.test">');
    expect(result?.pointCount).toBe(4);
    const svg = new DOMParser().parseFromString(result!.svg, "image/svg+xml");
    expect(svg.querySelector("path[data-series]")?.getAttribute("d")).toMatch(/^M[^L]+L[^M]+M[^L]+L/);
    expect(result?.svg).not.toMatch(/<script>|<img/);
    expect(result?.svg).toContain("&lt;script&gt;");
  });

  it.each([
    { data: [{ type: "scatter3d", x: [1], y: [2], z: [3] }] },
    { data: [{ x: [1], y: [2] }], layout: { xaxis: { type: "log" } } },
    { data: [{ x: [1], y: [2], yaxis: "y2" }] },
    { data: [{ x: [1], y: [Infinity] }] },
    { data: [{ x: ["a"], y: [2] }] },
    { data: [{ x: [1], y: [2], error_y: { array: [0.1] } }] },
    { chart_type: "line", series: [{ x: [0], y: [1] }, { x: [1], y: [] }] },
  ])("declines unsupported or incomplete scientific semantics without inventing a substitute", (payload) => {
    expect(renderScientificReportFigure(payload, "test")).toBeNull();
  });
});
