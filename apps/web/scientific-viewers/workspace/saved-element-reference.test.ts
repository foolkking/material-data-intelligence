import { describe, expect, it } from "vitest";
import periodic from "./element-reference-periodic.fixture.json";
import comparison from "./element-reference-comparison.fixture.json";
import filtered from "./element-reference-filtered.fixture.json";
import { readSavedElementReference, readSavedElementComparison } from "./saved-element-reference";
import { periodicLayoutForWidth, readSavedPeriodicTable } from "./saved-periodic-table";
import { sanitizePlotSpec } from "./WorkspaceGenericPlot";
import { plotTablePreview } from "./workspace-plot-table";
import { renderScientificReportFigure } from "../../app/lib/scientific-report-figure";
import { savedReportColorScale } from "../../app/lib/scientific-report-color-scale";

describe("versioned platform element figures", () => {
  it.each([periodic, comparison, filtered])("reads the real adapter output with matching scientific values", payload => {
    const before = JSON.stringify(payload), reference = readSavedElementReference(payload);
    expect(reference).not.toBeNull();
    expect(reference!.references[0].sources[0].license).toBe("LGPL-2.1-or-later");
    expect(sanitizePlotSpec(payload, 1000)).toMatchObject({ ok: true, pointCount: payload.valueCount });
    expect(JSON.stringify(payload)).toBe(before);
  });

  it("retains all 118 identities and explicit highlights in a complete table", () => {
    const plot = readSavedPeriodicTable(periodic)!;
    expect(plot).not.toBeNull();
    expect(plot.cells).toHaveLength(118);
    expect(plot.pointCount).toBe(118);
    expect(plot.cells.filter(cell => cell.highlighted).map(cell => cell.symbol).sort()).toEqual(["Cu", "Si"]);
    expect(plot.cells.find(cell => cell.symbol === "Og")?.atomicNumber).toBe(118);
    expect(plot.layout.shapes).toHaveLength(4);
    const compact = periodicLayoutForWidth(plot.layout, 375).annotations as Array<{ name?: string; text: string }>;
    const wide = periodicLayoutForWidth(plot.layout, 920).annotations as Array<{ name?: string; text: string }>;
    expect(compact.filter(a => a.name?.startsWith("atomic-number:"))).toHaveLength(0);
    expect(wide.filter(a => a.name?.startsWith("atomic-number:"))).toHaveLength(118);
    expect(compact.filter(a => a.name?.startsWith("element:"))).toHaveLength(118);
  });

  it.each([periodic, filtered])("keeps symbol contrast readable over saved reference colors", payload => {
    const plot = readSavedPeriodicTable(payload)!;
    const scales = plot.data.map(savedReportColorScale);
    const luminance = (channels: number[]) => channels.map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
      .reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
    for (const cell of plot.cells) {
      const layer = [2, 1, 0].find(index => (plot.data[index].z as Array<Array<number | null>>)[cell.y][cell.x] !== null)!;
      const value = (plot.data[layer].z as number[][])[cell.y][cell.x];
      const rgb = scales[layer]!.fill(value).match(/\d+/gu)!.slice(0, 3).map(Number);
      const bg = luminance(rgb), fg = luminance([1, 3, 5].map(index => parseInt(cell.color.slice(index, index + 2), 16)));
      expect((Math.max(bg, fg) + .05) / (Math.min(bg, fg) + .05), cell.symbol).toBeGreaterThanOrEqual(4.5);
    }
  });

  it("keeps filtered and unavailable elements separate from zero and from the atomic number", () => {
    const plot = readSavedPeriodicTable(filtered)!;
    expect(plot).not.toBeNull();
    expect(plot.cells.filter(cell => cell.selected)).toHaveLength(3);
    expect(plotTablePreview(filtered, 10)).toMatchObject({ totalRows: 3, rows: [
      { element: "C", atomicNumber: 6, value: .76 }, { element: "Si", atomicNumber: 14, value: 1.11 },
      { element: "Og", atomicNumber: 118, value: "参考值缺失" },
    ], columnLabels: { atomicNumber: "原子序数", value: "参考共价半径（Å）" } });
    expect(readSavedElementComparison(comparison)!.elements.map(e => e.count)).toEqual([.76, 1.11, 1.32]);
    expect(plotTablePreview(comparison, 10).rows.at(-1)).toMatchObject({ element: "Og", value: "参考值缺失" });
  });

  it.each([375, 770, 1280])("exports the same table and comparison at width %i", width => {
    const table = renderScientificReportFigure(periodic, "元素周期表", { width, compact: true })!;
    expect(table).not.toBeNull();
    expect(table.pointCount).toBe(118);
    expect(table.svg.match(/data-element="/gu)).toHaveLength(118);
    expect(table.svg.match(/data-highlight="/gu)).toHaveLength(4);
    expect(table.svg).toContain('data-value="118"');
    expect(table.svg).not.toMatch(/(?:NaN|Infinity|<script)/u);
    const compare = renderScientificReportFigure(comparison, "元素参考性质比较", { width, compact: true })!;
    expect(compare).not.toBeNull();
    expect(compare.pointCount).toBe(3);
    expect(compare.svg).toContain('data-element="Si" data-value="1.11"');
    expect(compare.svg).toContain("参考值缺失：Og");
    expect(compare.svg).not.toContain("data-fraction");
    expect(compare.svg).not.toContain("占显示元素比例");
  });

  it.each([
    (p: any) => { p.elementValues.Si = 999; },
    (p: any) => { p.selectedElements.push("Xx"); },
    (p: any) => { p.elementIdentities[13].atomicNumber = 15; },
    (p: any) => { p.elementIdentities[13].symbol = "C"; },
    (p: any) => { p.referenceSource.contentHash = "unverified"; },
    (p: any) => { p.referenceSource.sources[0].url = "javascript:alert(1)"; },
    (p: any) => { p.missingElements = ["Si"]; },
    (p: any) => { p.plotlyFigure.layout.shapes.pop(); },
    (p: any) => { p.plotlyFigure.layout.shapes[0].x0 = 999; },
    (p: any) => { p.unit = "nanometer"; },
    (p: any) => { p.sampleAnalysis = true; },
  ])("rejects inconsistent identity, graphics or provenance", corrupt => {
    const input = structuredClone(periodic); corrupt(input);
    expect(sanitizePlotSpec(input, 1000)).toMatchObject({ ok: false });
    expect(renderScientificReportFigure(input, "不一致的参考图")).toBeNull();
  });

  it("does not render changed comparison bars as valid references", () => {
    const input = structuredClone(comparison);
    input.plotlyFigure.data[0].y[0] = 999;
    expect(readSavedElementComparison(input)).toBeNull();
    expect(sanitizePlotSpec(input, 1000)).toMatchObject({ ok: false });
    expect(renderScientificReportFigure(input, "不一致的比较图")).toBeNull();
  });
});
