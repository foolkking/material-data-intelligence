import { expect, it } from "vitest";
import { plotTablePreview } from "./workspace-plot-table";

it("refuses contradictory composition counts instead of selecting one as authoritative", () => {
  const result = plotTablePreview({ artifactType: "composition.elements_hist", bars: [{ element: "wrong", count: 999 }], plotlyFigure: { data: [{ type: "bar", x: ["Fe", "Si"], y: [12, 3] }], layout: { yaxis: { type: "log", title: "Element Count" } } } }, 10);
  expect(result.rows).toEqual([]);
  expect(result.notes).toContain("元素图表与保存的计数不一致；原始文件仍可查看。");
});

it("reads exact coordinates emitted by the backend Plotly exporter, including encoded gaps", () => {
  const result = plotTablePreview({ data: [{ type: "scatter", x: { dtype: "f8", bdata: "AAAAAAAAAAAAAAAAAADwPwAAAAAAAABAAAAAAAAACEAAAAAAAAAQQA==" }, y: { dtype: "f8", bdata: "AAAAAAAAAEAAAAAAAAAIQAAAAAAAAPh/AAAAAAAAFEAAAAAAAAAYQA==" } }] }, 10);
  expect(result.rows.map(({ x, y }) => [x, y])).toEqual([[0, 2], [1, 3], [2, null], [3, 5], [4, 6]]);
});

it("preserves the backend's row-major shape when expanding encoded heatmap cells", () => {
  const result = plotTablePreview({ data: [{ type: "heatmap", x: { dtype: "i1", bdata: "ChQe" }, y: { dtype: "i1", bdata: "AQI=" }, z: { dtype: "f8", bdata: "AAAAAAAAJkAAAAAAAAAoQAAAAAAAACpAAAAAAAAANUAAAAAAAAD4fwAAAAAAADdA", shape: "2, 3" } }] }, 10);
  expect(result.rows.map(({ x, y, value }) => [x, y, value])).toEqual([[10, 1, 11], [20, 1, 12], [30, 1, 13], [10, 2, 21], [20, 2, null], [30, 2, 23]]);
  expect(result.totalRows).toBe(6);
});

it("keeps saved XY coordinates, explicit gaps and source axis units without placeholder fields", () => {
  const content = { figure: { data: [{ name: "RDF", x: [0, 1, 2], y: [0, null, 1.23456789] }], layout: { xaxis: { title: { text: "<i>r</i> (Å)" } }, yaxis: { title: "g(r)" } } } };
  const before = JSON.stringify(content);
  const result = plotTablePreview(content, 10);
  expect(result.rows).toEqual([{ point: 1, x: 0, y: 0 }, { point: 2, x: 1, y: null }, { point: 3, x: 2, y: 1.23456789 }]);
  expect(result.columnLabels).toMatchObject({ x: "r (Å)", y: "g(r)" });
  expect(JSON.stringify(content)).toBe(before);
});

it("retains Z coordinates and scene units in three-dimensional data", () => {
  const result = plotTablePreview({ data: [{ type: "scatter3d", x: [1, 2], y: [3, 4], z: [0, 7] }], layout: { scene: { zaxis: { title: { text: "z (Å)" } } } } }, 10);
  expect(result.rows).toEqual([{ point: 1, "scene.x": 1, "scene.y": 3, "scene.z": 0 }, { point: 2, "scene.x": 2, "scene.y": 4, "scene.z": 7 }]);
  expect(result.columnLabels["scene.z"]).toBe("z (Å)");
});

it("flattens heatmap cells by row and column without dropping zeros or missing samples", () => {
  const result = plotTablePreview({ data: [{ type: "heatmap", x: [10, 20], y: [30, 40], z: [[0, 2], [3, null]] }] }, 10);
  expect(result.rows).toEqual([
    { row: 1, column: 1, x: 10, y: 30, value: 0 }, { row: 1, column: 2, x: 20, y: 30, value: 2 },
    { row: 2, column: 1, x: 10, y: 40, value: 3 }, { row: 2, column: 2, x: 20, y: 40, value: null },
  ]);
  expect(result.totalRows).toBe(4);
});

it("retains heatmap cell edges instead of inventing centers, and leaves absent physical coordinates absent", () => {
  const result = plotTablePreview({ data: [{ type: "heatmap", x: [0, 2, 5], z: [[1, 2]] }] }, 10);
  expect(result.rows).toEqual([{ row: 1, column: 1, xStart: 0, xEnd: 2, value: 1 }, { row: 1, column: 2, xStart: 2, xEnd: 5, value: 2 }]);
});

it("honors the saved transpose flag when associating matrix cells with physical coordinates", () => {
  const result = plotTablePreview({ data: [{ type: "heatmap", transpose: true, x: [10, 20], y: [1, 2, 3], z: [[11, 12, 13], [21, 22, 23]] }] }, 10);
  expect(result.rows.map(({ x, y, value }) => [x, y, value])).toEqual([
    [10, 1, 11], [10, 2, 12], [10, 3, 13], [20, 1, 21], [20, 2, 22], [20, 3, 23],
  ]);
});

it.each(["treemap", "sunburst"])("keeps %s node labels, parents and IDs without making dataset sample identities", (type) => {
  const result = plotTablePreview({ data: [{ type, ids: ["root", "child"], labels: ["合金", "Fe"], parents: ["", "root"], values: [10, 4] }] }, 10);
  expect(result.rows).toEqual([{ point: 1, nodeId: "root", label: "合金", parent: "", value: 10 }, { point: 2, nodeId: "child", label: "Fe", parent: "root", value: 4 }]);
  expect(result.rows.every(row => !("id" in row) && !("sampleRef" in row))).toBe(true);
});

it("caps all series together while retaining exact total rows and source series order", () => {
  const result = plotTablePreview({ data: [{ name: "same", x: [1, 2, 3], y: [4, 5, 6] }, { name: "same", x: [7, 8, 9], y: [10, 11, 12] }] }, 4);
  expect(result.rows).toHaveLength(4);
  expect(result.totalRows).toBe(6);
  expect(result.rows[3]).toEqual({ series: "2 · same", point: 1, x: 7, y: 10 });
  expect(result.rows[0].series).toBe("1 · same");
});

it("discloses series beyond the bounded inventory", () => {
  const result = plotTablePreview({ data: Array.from({ length: 130 }, () => ({ x: [1], y: [2] })) }, 1000);
  expect(result.rows).toHaveLength(128);
  expect(result.totalRows).toBe(128);
  expect(result.omittedTraces).toBe(2);
});

it("does not attach face-indexed mesh values to unrelated vertices", () => {
  const result = plotTablePreview({ data: [{ type: "mesh3d", x: [0, 1, 0], y: [0, 0, 1], z: [0, 0, 0], i: [0], j: [1], k: [2], intensitymode: "cell", intensity: [99] }] }, 10);
  expect(result.rows).toHaveLength(3);
  expect(result.rows[0]).toEqual({ point: 1, "scene.x": 0, "scene.y": 0, "scene.z": 0 });
  expect(result.notes[0]).toContain("三角面索引");
});

it("distinguishes identically titled axes without overwriting either coordinate", () => {
  const result = plotTablePreview({ data: [{ x: [1], y: [2] }], layout: { xaxis: { title: "Energy (eV)" }, yaxis: { title: "Energy (eV)" } } }, 10);
  expect(result.rows[0]).toEqual({ point: 1, x: 1, y: 2 });
  expect(result.columnLabels).toMatchObject({ x: "Energy (eV) (X)", y: "Energy (eV) (Y)" });
});
