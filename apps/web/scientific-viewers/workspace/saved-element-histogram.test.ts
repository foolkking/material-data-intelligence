import { describe, expect, it } from "vitest";
import { readSavedElementHistogram } from "./saved-element-histogram";
import { sanitizePlotSpec } from "./WorkspaceGenericPlot";
import { plotTablePreview } from "./workspace-plot-table";

function fixture() {
  return { schemaVersion: "mdi.element-histogram/1.0", artifactType: "composition.elements_hist", chartType: "bar",
    countMode: "fractional", elementCount: 3, omittedElementCount: 0, retainedElementValue: 2, totalElementValue: 2,
    fractionScope: "displayed_elements", showValues: "count",
    bars: [{ element: "Si", count: 1, fraction: 0.5 }, { element: "Fe", count: 0.5, fraction: 0.25 }, { element: "O", count: 0.5, fraction: 0.25 }],
    plotlyFigure: { data: [{ type: "bar", x: ["Si", "Fe", "O"], y: [1, 0.5, 0.5], text: ["1", "0.5", "0.5"], width: 0.7 }],
      layout: { xaxis: { type: "category", categoryorder: "array", categoryarray: ["Si", "Fe", "O"] }, yaxis: { type: "log" } } } };
}

describe("saved element histogram", () => {
  it("keeps fractional values, exact elements and the saved log axis through viewer and numeric inspection", () => {
    const source = fixture();
    expect(readSavedElementHistogram(source)?.elements).toEqual(source.bars);
    const table = plotTablePreview(source, 2);
    expect(table.rows).toEqual(source.bars.slice(0, 2));
    expect(table.totalRows).toBe(3);
    expect(table.columnLabels.count).toBe("分数贡献总和");
    const spec = sanitizePlotSpec(source, 100);
    expect(spec.ok).toBe(true);
    if (spec.ok) {
      expect(spec.data[0]).toMatchObject({ x: ["Si", "Fe", "O"], y: [1, 0.5, 0.5], text: ["1", "0.5", "0.5"] });
      expect(spec.layout.yaxis).toMatchObject({ type: "log" });
    }
  });

  it("reads consistent historical order without rewriting its snapshot", () => {
    const { schemaVersion: _, ...source } = fixture();
    source.bars.reverse();
    const before = JSON.stringify(source);
    expect(readSavedElementHistogram(source)?.elements.map(bar => bar.element)).toEqual(["Si", "Fe", "O"]);
    expect(JSON.stringify(source)).toBe(before);
  });

  it("rejects the historical top-one Fe/O identity mismatch in both scientific views", () => {
    const source = { artifactType: "composition.elements_hist", chartType: "bar", countMode: "occurrence", elementCount: 4,
      bars: [{ element: "Fe", count: 12, fraction: 1 }], plotlyFigure: { data: [{ type: "bar", x: ["O"], y: [12] }] } };
    expect(readSavedElementHistogram(source)).toBeNull();
    expect(sanitizePlotSpec(source, 100)).toEqual({ ok: false, code: "ELEMENT_HISTOGRAM_INCONSISTENT" });
    expect(plotTablePreview(source, 100)).toMatchObject({ rows: [], totalRows: 0 });
  });

  it("discloses the retained subset without changing the saved proportions", () => {
    const source = { ...fixture(), elementCount: 5, omittedElementCount: 2, totalElementValue: 4 };
    const table = plotTablePreview(source, 100);
    expect(table.rows).toEqual(source.bars);
    expect(table.notes).toEqual(["仅显示前 3 个元素，省略 2 个元素；百分比以显示元素的合计值为分母。"]);
    const spec = sanitizePlotSpec(source, 100);
    if (!spec.ok) throw new Error("expected a consistent saved figure");
    expect(spec.notes).toEqual(table.notes);
  });

  it.each([
    (p: ReturnType<typeof fixture>) => { p.plotlyFigure.data[0].y[1] = 0.6; },
    (p: ReturnType<typeof fixture>) => { p.bars[1].fraction = 0.5; },
    (p: ReturnType<typeof fixture>) => { p.bars[1].element = "Si"; },
    (p: ReturnType<typeof fixture>) => { p.plotlyFigure.data[0].x[1] = "Si"; },
    (p: ReturnType<typeof fixture>) => { p.bars[1].count = NaN; },
    (p: ReturnType<typeof fixture>) => { p.fractionScope = "all_elements"; },
    (p: ReturnType<typeof fixture>) => { p.totalElementValue = 1; },
    (p: ReturnType<typeof fixture>) => { p.omittedElementCount = 1; },
    (p: ReturnType<typeof fixture>) => { p.schemaVersion = "mdi.element-histogram/9.0"; },
    (p: ReturnType<typeof fixture>) => { p.plotlyFigure.data[0].text[1] = "0"; },
  ])("rejects inconsistent saved data", change => {
    const source = fixture(); change(source);
    expect(readSavedElementHistogram(source)).toBeNull();
  });
});
