import { describe, expect, it } from "vitest";
import { readPeriodicElementValues, readSavedPeriodicTable } from "./saved-periodic-table";
import { sanitizePlotSpec } from "./WorkspaceGenericPlot";
import { plotTablePreview } from "./workspace-plot-table";
import { savedPeriodicTableFixture as fixture } from "./saved-periodic-table.fixture";

describe("saved periodic element heatmap", () => {
  it.each([false, true])("retains element identity, saved color values and raw counts (log=%s)", log => {
    const input = fixture(log), before = JSON.stringify(input);
    const plot = readSavedPeriodicTable(input);
    expect(plot?.pointCount).toBe(4);
    expect(plot?.layout.annotations).toHaveLength(5);
    expect(plot?.layout.annotations).toContainEqual(expect.objectContaining({ text: "Fe", x: 7, y: 6 }));
    expect(plot?.data[2]).toMatchObject({ zmin: log ? 0 : 1, zmax: log ? Math.log10(12) : 12, text: expect.any(Array) });
    expect(plot?.layout.annotations).toContainEqual(expect.objectContaining({ text: log ? "出现次数（对数色阶）" : "出现次数", xref: "paper" }));
    if (log) expect(plot?.data[2].colorbar).toMatchObject({ tickvals: [0, Math.log10(2), 1], ticktext: ["1", "2", "10"] });
    expect(plotTablePreview(input, 1000)).toMatchObject({ totalRows: 4, rows: [
      { element: "Cu", value: 1 }, { element: "Fe", value: 12 }, { element: "O", value: 12 }, { element: "Si", value: 3 },
    ], columnLabels: { element: "元素", value: "出现次数" } });
    expect(JSON.stringify(input)).toBe(before);
    expect(sanitizePlotSpec(input, 4)).toMatchObject({ ok: true, pointCount: 4, totalPointCount: 4 });
    expect(sanitizePlotSpec(input, 3)).toMatchObject({ ok: false });
  });

  it.each([
    (p: any) => { p.elementValues.Fe = 99; },
    (p: any) => { p.elementValues.Zn = 4; },
    (p: any) => { p.plotlyFigure.data[2].z[6][7] = 99; },
    (p: any) => { p.plotlyFigure.data[0].z[0][0] = 1; },
    (p: any) => { p.plotlyFigure.data[0].z[6][7] = 3; },
    (p: any) => { p.plotlyFigure.data[2].colorscale = [[0, "url(https://bad.invalid)"], [1, "red"]]; },
    (p: any) => { p.plotlyFigure.layout.annotations[0].x = 100; },
    (p: any) => { p.plotlyFigure.layout.annotations[0].xref = "paper"; },
    (p: any) => { p.plotlyFigure.layout.annotations[0].text = "Fe"; },
    (p: any) => { p.plotlyFigure.layout.annotations[0].showarrow = true; },
    (p: any) => { p.plotlyFigure.layout.annotations.pop(); },
    (p: any) => { p.plotlyFigure.data[2].z.pop(); },
    (p: any) => { p.plotlyFigure.data[2].transpose = true; },
    (p: any) => { p.plotlyFigure.data[2].coloraxis = "coloraxis"; },
    (p: any) => { p.plotlyFigure.data[2].x0 = 1; },
    (p: any) => { p.plotlyFigure.data[2].zsmooth = "best"; },
    (p: any) => { p.plotlyFigure.layout.xaxis = { type: "log" }; },
    (p: any) => { delete p.plotlyFigure.data[2].colorscale; },
    (p: any) => { p.plotlyFigure.data[2].colorbar = { tickvals: [0, 1], ticktext: ["1"] }; },
    (p: any) => { p.plotlyFigure.data[2].colorbar = { tickvals: [0, 1], ticktext: ["1", "100"] }; },
    (p: any) => { p.plotlyFigure.data[2].colorbar = { tickvals: [null], ticktext: ["1"] }; },
    (p: any) => { p.elementValues.Cu = Infinity; },
    (p: any) => { p.elementValues.Cu = -1; },
    (p: any) => { p.log = "true"; },
  ])("rejects inconsistent or unsupported saved content", corrupt => {
    const p = fixture(true); corrupt(p);
    expect(readSavedPeriodicTable(p)).toBeNull();
    expect(sanitizePlotSpec(p, 1000)).toMatchObject({ ok: false });
  });

  it("keeps real zeros distinct from absent values and labels the recorded counting method", () => {
    const p = fixture(true); p.elementValues.Cu = 0; p.plotlyFigure.data[2].z[6][10] = null;
    expect(readSavedPeriodicTable(p)).not.toBeNull();
    expect(plotTablePreview(p, 1)).toMatchObject({ totalRows: 4, rows: [{ element: "Cu", value: 0 }] });
    p.countMode = "fractional";
    expect(readPeriodicElementValues(p)?.label).toBe("累计原子分数");
    p.countMode = "unsupported";
    expect(readPeriodicElementValues(p)).toBeNull();
  });

  it("keeps all-zero raw values available without presenting an empty logarithmic heatmap", () => {
    const p = fixture(true);
    p.elementValues = { Cu: 0, Fe: 0, O: 0, Si: 0 };
    p.plotlyFigure.data[2].z = Array.from({ length: 10 }, () => Array(18).fill(null));
    expect(readSavedPeriodicTable(p)).toBeNull();
    expect(plotTablePreview(p, 118)).toMatchObject({ totalRows: 4, rows: [
      { element: "Cu", value: 0 }, { element: "Fe", value: 0 }, { element: "O", value: 0 }, { element: "Si", value: 0 },
    ] });
  });
});
