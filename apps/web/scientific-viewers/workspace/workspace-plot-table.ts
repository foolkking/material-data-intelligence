import { normalizedPlotFigure } from "./workspace-plot-contract";
import { readPlotCoordinates, readPlotNumericMatrix } from "./workspace-plot-data";
import { isSavedPeriodicTable, readPeriodicElementValues } from "./saved-periodic-table";
import { histogramNotes, isSavedHistogram, readSavedHistogram } from "./saved-histogram";
import { isSavedScatter, readSavedScatter } from "./saved-scatter";
import { isSavedElementHistogram, readSavedElementHistogram } from "./saved-element-histogram";
import { isSavedElementReference, readSavedElementReference } from "./saved-element-reference";

type Row = Record<string, unknown>;
type Field = { key: string; values: unknown[] };

/** Read saved coordinates, not decimated drawing data. Only allocate the rows
 * that can be displayed; a large figure must not create millions of row objects. */
export function plotTablePreview(content: unknown, maximumRows: number) {
  if (isSavedElementReference(content)) {
    const reference = readSavedElementReference(content);
    const columnLabels: Record<string, string> = { atomicNumber: "原子序数", element: "元素", value: reference?.label ?? "数值" };
    if (!reference) return { rows: [], columnLabels, totalRows: 0, omittedTraces: 0, notes: ["元素参考数据无法核对。"] };
    const cap = Number.isSafeInteger(maximumRows) ? Math.max(0, Math.min(maximumRows, 118)) : 0;
    const rows: Row[] = reference.selected.slice(0, cap).map(element => ({ atomicNumber: reference.identities.get(element)!.atomicNumber,
      element, ...(reference.property === "atomic_number" ? {} : { value: reference.values[element] ?? "参考值缺失" }) }));
    return { rows, columnLabels, totalRows: reference.selected.length, omittedTraces: 0, notes: reference.notes };
  }
  if (isSavedElementHistogram(content)) {
    const histogram = readSavedElementHistogram(content);
    const columnLabels: Record<string, string> = { element: "元素", count: histogram?.label ?? "数值", fraction: "占显示元素的比例" };
    if (!histogram) return { rows: [], columnLabels, totalRows: 0, omittedTraces: 0, notes: ["元素图表与保存的计数不一致；原始文件仍可查看。"] };
    const cap = Number.isSafeInteger(maximumRows) ? Math.max(0, Math.min(maximumRows, 118)) : 0;
    const rows: Row[] = histogram.elements.slice(0, cap);
    return { rows, columnLabels, totalRows: histogram.elements.length, omittedTraces: 0, notes: histogram.notes };
  }
  if (isSavedScatter(content)) {
    const scatter = readSavedScatter(content);
    const columnLabels: Record<string, string> = { sourceRow: "来源行", series: "分组" };
    if (!scatter) return { rows: [], columnLabels, totalRows: 0, omittedTraces: 0, notes: ["散点坐标与保存的统计不一致；原始文件仍可查看。"] };
    columnLabels.x = `${scatter.xColumn} (X)`; columnLabels.y = `${scatter.yColumn} (Y)`;
    if (scatter.colorMode === "numeric") columnLabels.color = `${scatter.colorColumn} (颜色)`;
    scatter.hoverColumns.forEach((label, index) => { columnLabels[`hover${index}`] = label; });
    const rows: Row[] = [], cap = Number.isSafeInteger(maximumRows) ? Math.max(0, Math.min(maximumRows, 10_000)) : 0;
    for (const trace of scatter.traces) for (let index = 0; index < trace.x.length && rows.length < cap; index++) {
      const row: Row = { ...(scatter.colorMode === "categorical" ? { series: trace.label } : {}), sourceRow: trace.rows[index][0], x: trace.x[index], y: trace.y[index] };
      if (trace.color) row.color = trace.color[index];
      scatter.hoverColumns.forEach((_, i) => { row[`hover${i}`] = trace.rows[index][i + 1]; });
      rows.push(row);
    }
    return { rows, columnLabels, totalRows: scatter.pointCount, omittedTraces: 0, notes: scatter.notes };
  }
  if (isSavedHistogram(content)) {
    const histogram = readSavedHistogram(content);
    const columnLabels: Record<string, string> = { series: "分组", point: "序号", start: "左边界", end: "右边界", closed: "包含右端点", count: "样本数" };
    if (!histogram) return { rows: [], columnLabels, totalRows: 0, omittedTraces: 0, notes: ["直方图计数与图形不一致，原始文件保留在“数据与来源”中。"] };
    const cap = Number.isSafeInteger(maximumRows) ? Math.max(0, Math.min(maximumRows, 10_000)) : 0;
    const rows: Row[] = [];
    for (const group of histogram.groups) for (let bin = 0; bin < group.counts.length && rows.length < cap; bin++) {
      rows.push({ ...(histogram.groupBy !== null ? { series: group.label } : {}), point: bin + 1,
        start: histogram.edges[bin], end: histogram.edges[bin + 1], closed: bin === group.counts.length - 1 ? "是" : "否", count: group.counts[bin] });
    }
    return { rows, columnLabels, totalRows: histogram.counts.length * histogram.groups.length, omittedTraces: 0, notes: histogramNotes(histogram) };
  }
  if (isSavedPeriodicTable(content)) {
    const periodic = readPeriodicElementValues(content);
    const values = Object.entries(periodic?.values ?? {});
    const cap = Number.isSafeInteger(maximumRows) ? Math.max(0, Math.min(maximumRows, 118)) : 0;
    return { rows: values.slice(0, cap).map(([element, value], index): Row => ({ point: index + 1, element, value })),
      columnLabels: { point: "序号", element: "元素", value: periodic?.label ?? "数值" }, totalRows: values.length, omittedTraces: 0,
      notes: periodic ? [] : ["元素数值无法读取；原始内容保留在“数据与来源”中。"] };
  }
  const figure = normalizedPlotFigure(content);
  const allTraces = array(figure?.data);
  const traces = allTraces.slice(0, 128);
  const layout = record(figure?.layout);
  const cap = Number.isSafeInteger(maximumRows) ? Math.max(0, Math.min(maximumRows, 10_000)) : 0;
  const rows: Row[] = [];
  const columnLabels: Record<string, string> = { series: "数据系列", point: "序号", row: "网格行", column: "网格列", label: "标签", parent: "父节点", nodeId: "节点标识", value: "数值", intensity: "强度" };
  const notes = new Set<string>();
  let totalRows = 0;
  const axis = (trace: Row, coordinate: "x" | "y" | "z", scene: boolean) => {
    const sceneId = typeof trace.scene === "string" && /^scene\d*$/.test(trace.scene) ? trace.scene : "scene";
    const ref = typeof trace[`${coordinate}axis`] === "string" && new RegExp(`^${coordinate}\\d*$`).test(String(trace[`${coordinate}axis`]))
      ? String(trace[`${coordinate}axis`]) : coordinate;
    const key = scene ? `${sceneId}.${coordinate}` : ref;
    const axisRecord = scene ? record(record(layout?.[sceneId])?.[`${coordinate}axis`]) : record(layout?.[`${coordinate}axis${ref.slice(1)}`]);
    const title = text(record(axisRecord?.title)?.text ?? axisRecord?.title);
    columnLabels[key] = title || (scene && sceneId !== "scene" ? `${sceneId} · ${coordinate.toUpperCase()}` : ref.toUpperCase());
    return key;
  };
  for (const [traceIndex, value] of traces.entries()) {
    const trace = record(value);
    if (!trace) continue;
    const name = text(trace.name);
    const base: Row = allTraces.length > 1 ? { series: name ? `${traceIndex + 1} · ${name}` : `系列 ${traceIndex + 1}` } : {};
    const type = String(trace.type || "scatter");
    if (type === "heatmap") {
      const z = readPlotNumericMatrix(trace.z) ?? [];
      const sourceX = readPlotCoordinates(trace.x), sourceY = readPlotCoordinates(trace.y);
      if (trace.x !== undefined && !sourceX || trace.y !== undefined && !sourceY) notes.add("部分坐标无法读取；原始内容保留在“数据与来源”中。");
      const x = sourceX ?? [], y = sourceY ?? [];
      const width = z.reduce<number>((count, row) => Math.max(count, array(row).length), 0);
      const xKey = axis(trace, "x", false), yKey = axis(trace, "y", false);
      const transposed = trace.transpose === true;
      const xEdges = x.length === (transposed ? z.length : width) + 1;
      const yEdges = y.length === (transposed ? width : z.length) + 1;
      const coordinate = (row: Row, key: string, values: unknown[], index: number, edges: boolean) => {
        if (!values.length) return;
        if (edges) {
          columnLabels[`${key}Start`] = `${columnLabels[key]} · 起边界`;
          columnLabels[`${key}End`] = `${columnLabels[key]} · 止边界`;
          row[`${key}Start`] = values[index] ?? null;
          row[`${key}End`] = values[index + 1] ?? null;
        } else row[key] = values[index] ?? null;
      };
      for (const [rowIndex, values] of z.entries()) {
        const cells = array(values);
        totalRows += cells.length;
        for (let columnIndex = 0; columnIndex < cells.length && rows.length < cap; columnIndex += 1) {
          const row: Row = { ...base, row: rowIndex + 1, column: columnIndex + 1 };
          coordinate(row, xKey, x, transposed ? rowIndex : columnIndex, xEdges);
          coordinate(row, yKey, y, transposed ? columnIndex : rowIndex, yEdges);
          row.value = cells[columnIndex] ?? null;
          rows.push(row);
        }
      }
      continue;
    }
    const fields: Field[] = [];
    const add = (key: string, value: unknown) => {
      const values = readPlotCoordinates(value);
      if (values?.length) fields.push({ key, values });
      else if (record(value)?.bdata !== undefined) notes.add("部分编码数组无法读取；原始内容保留在“数据与来源”中。");
    };
    if (["treemap", "sunburst", "pie"].includes(type)) {
      add("nodeId", trace.ids); add("label", trace.labels); add("parent", trace.parents); add("value", trace.values);
    } else {
      const scene = type === "scatter3d" || type === "mesh3d";
      for (const coordinate of ["x", "y", "z"] as const) {
        if (trace[coordinate] !== undefined) add(axis(trace, coordinate, scene), trace[coordinate]);
      }
      add("value", trace.values);
      if (type === "mesh3d") {
        const vertexCount = fields.find(field => field.key.endsWith(".x"))?.values.length;
        const intensity = readPlotCoordinates(trace.intensity);
        if (trace.intensitymode !== "cell" && intensity?.length && intensity.length === vertexCount) fields.push({ key: "intensity", values: intensity });
        notes.add("网格数值表列出顶点数据；三角面索引和面属性保留在源文件中。");
      }
    }
    const count = fields.reduce((size, field) => Math.max(size, field.values.length), 0);
    totalRows += count;
    const available = Math.min(count, cap - rows.length);
    for (let index = 0; index < available; index += 1) {
      const row: Row = { ...base, point: index + 1 };
      for (const field of fields) row[field.key] = field.values[index] ?? null;
      rows.push(row);
    }
  }
  // Equal axis titles must not make two independent coordinates indistinguishable.
  const visibleKeys = [...new Set(rows.flatMap(row => Object.keys(row)))];
  const labels = visibleKeys.map(key => columnLabels[key] || key);
  for (const key of visibleKeys) {
    const label = columnLabels[key] || key;
    if (labels.filter(value => value === label).length > 1) columnLabels[key] = `${label} (${key.toUpperCase()})`;
  }
  return { rows, columnLabels, totalRows, omittedTraces: allTraces.length - traces.length, notes: [...notes] };
}

function record(value: unknown): Row | null { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Row : null; }
function array(value: unknown): unknown[] { return Array.isArray(value) ? value : []; }
function text(value: unknown): string { return typeof value === "string" ? value.replace(/<[^>]*>/g, "").trim() : ""; }
