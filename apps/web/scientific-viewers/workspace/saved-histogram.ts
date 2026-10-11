import { readPlotNumericVector } from "./workspace-plot-data";

type RecordValue = Record<string, unknown>;
const record = (value: unknown): RecordValue => value && typeof value === "object" && !Array.isArray(value) ? value as RecordValue : {};
const finite = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value);
const count = (value: unknown): value is number => Number.isSafeInteger(value) && Number(value) >= 0;
const text = (value: unknown): value is string => typeof value === "string" && !!value.trim();
export const HISTOGRAM_INTERVALS = "left-closed-right-open; final bin includes right edge";

export function isSavedHistogram(value: unknown): boolean {
  return String(record(value).schemaVersion).startsWith("mdi.table-histogram/");
}

/** Inspect saved counts and geometry. Never bin raw samples in the browser. */
export function readSavedHistogram(value: unknown) {
  const root = record(value), figure = record(root.figure), layout = record(figure.layout);
  if (root.schemaVersion !== "mdi.table-histogram/1.0" || root.chartType !== "histogram" || !text(root.column)
    || !count(root.bins) || root.bins < 1 || root.bins > 4096 || !count(root.count) || root.count < 1
    || !count(root.inputCount) || !count(root.excludedCount) || root.inputCount !== root.count + root.excludedCount
    || root.intervalConvention !== HISTOGRAM_INTERVALS || (root.groupBy !== null && !text(root.groupBy))) return null;
  const edges = readPlotNumericVector(root.binEdges), counts = readPlotNumericVector(root.binCounts);
  if (!edges || edges.length !== root.bins + 1 || !edges.every(finite) || edges.some((v, i) => i > 0 && v <= edges[i - 1]!)
    || !counts || counts.length !== root.bins || !counts.every(count) || counts.reduce((sum, n) => sum + n, 0) !== root.count) return null;
  if (![root.min, root.max, root.mean, root.median].every(finite) || Number(root.min) > Number(root.max)
    || Number(root.min) < edges[0]! || Number(root.max) > edges.at(-1)!
    || [root.mean, root.median].some(v => Number(v) < Number(root.min) || Number(v) > Number(root.max))) return null;
  if (!Array.isArray(root.groups) || !root.groups.length || root.groups.length > 16 || root.groups.length * root.bins > 50_000
    || root.groupBy === null && root.groups.length !== 1 || !Array.isArray(figure.data) || figure.data.length !== root.groups.length
    || layout.barmode !== (root.groupBy === null ? "overlay" : "stack") || layout.barnorm || layout.grid || layout.shapes || layout.annotations) return null;
  for (const coordinate of ["x", "y"]) {
    const axis = record(layout[`${coordinate}axis`]);
    if (axis.type !== "linear" || ["domain", "matches", "scaleanchor", "overlaying", "anchor"].some(key => axis[key] !== undefined)) return null;
  }
  const names = new Set<string>(), totals = Array<number>(root.bins).fill(0);
  const groups: Array<{ label: string; count: number; counts: number[] }> = [];
  for (let index = 0; index < root.groups.length; index++) {
    const group = record(root.groups[index]), trace = record(figure.data[index]);
    const groupCounts = readPlotNumericVector(group.binCounts), x = readPlotNumericVector(trace.x);
    const y = readPlotNumericVector(trace.y), widths = readPlotNumericVector(trace.width);
    if (!text(group.label) || names.has(group.label) || !count(group.count) || group.count < 1
      || !groupCounts || groupCounts.length !== root.bins || !groupCounts.every(count)
      || groupCounts.reduce((sum, n) => sum + n, 0) !== group.count || trace.type !== "bar" || trace.name !== group.label
      || !x || !y || !widths || [x, y, widths].some(array => array.length !== root.bins)
      || ["offset", "base", "transforms", "xaxis", "yaxis", "orientation", "error_x", "error_y", "offsetgroup", "alignmentgroup"].some(key => trace[key] !== undefined)
      || trace.visible !== undefined && trace.visible !== true) return null;
    for (let bin = 0; bin < root.bins; bin++) {
      const width = edges[bin + 1]! - edges[bin]!;
      if (!Number.isFinite(width) || x[bin] !== edges[bin]! + width / 2 || widths[bin] !== width || y[bin] !== groupCounts[bin]) return null;
      totals[bin] += groupCounts[bin];
    }
    names.add(group.label);
    groups.push({ label: group.label, count: group.count, counts: groupCounts });
  }
  if (totals.some((n, i) => n !== counts[i])) return null;
  return { edges: edges as number[], counts: counts as number[], groups, column: root.column,
    groupBy: root.groupBy as string | null, count: root.count, inputCount: root.inputCount, excludedCount: root.excludedCount };
}

export function histogramNotes(histogram: NonNullable<ReturnType<typeof readSavedHistogram>>): string[] {
  return ["区间左闭右开，最后一个区间包含右端点。",
    ...(histogram.excludedCount ? [`已排除 ${histogram.excludedCount} 行缺失、非数值或非有限值。`] : [])];
}
