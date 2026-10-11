import { readPlotNumericVector } from "./workspace-plot-data";

type RecordValue = Record<string, unknown>;
const record = (v: unknown): RecordValue => v && typeof v === "object" && !Array.isArray(v) ? v as RecordValue : {};
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const count = (v: unknown): v is number => Number.isSafeInteger(v) && Number(v) >= 0;
const label = (v: unknown): v is string => typeof v === "string" && !!v.trim() && v.length <= 1024;
const scalar = (v: unknown) => v === null || typeof v === "string" || typeof v === "boolean" || finite(v);

export function isSavedScatter(v: unknown) { return String(record(v).schemaVersion).startsWith("mdi.table-scatter/"); }

/** Validate saved paired values and source-row identities, without recomputing a scientific sample. */
export function readSavedScatter(value: unknown) {
  const root = record(value), figure = record(root.figure), layout = record(figure.layout);
  if (root.schemaVersion !== "mdi.table-scatter/1.0" || root.chartType !== "scatter" || !label(root.xColumn) || !label(root.yColumn)
    || !["none", "numeric", "categorical"].includes(String(root.colorMode))
    || (root.colorMode === "none" ? root.colorColumn !== null : !label(root.colorColumn))
    || ![root.inputCount, root.validPointCount, root.pointCount, root.excludedCount, root.excludedCoordinateCount, root.excludedColorCount, root.omittedPointCount, root.traces].every(count)
    || Number(root.pointCount) < 1 || Number(root.pointCount) > 50_000
    || Number(root.validPointCount) !== Number(root.pointCount) + Number(root.omittedPointCount)
    || Number(root.inputCount) !== Number(root.validPointCount) + Number(root.excludedCount)
    || Number(root.excludedCount) !== Number(root.excludedCoordinateCount) + Number(root.excludedColorCount)
    || root.colorMode !== "numeric" && root.excludedColorCount !== 0
    || root.sampling !== (root.omittedPointCount ? "source-order-even-with-extrema-and-groups" : "none")
    || !Array.isArray(root.hoverColumns) || root.hoverColumns.length > 8 || !root.hoverColumns.every(label) || new Set(root.hoverColumns).size !== root.hoverColumns.length
    || !Array.isArray(root.groups) || !root.groups.length || root.groups.length > 64 || root.groups.length !== root.traces
    || root.colorMode !== "categorical" && root.groups.length !== 1
    || !Array.isArray(figure.data) || figure.data.length !== root.groups.length) return null;
  const xRange = readPlotNumericVector(root.xRange), yRange = readPlotNumericVector(root.yRange);
  if (!xRange || !yRange || [xRange, yRange].some(range => range.length !== 2 || range[0] > range[1] || !finite(range[1] - range[0]))) return null;
  if (["shapes", "annotations", "grid"].some(key => layout[key] !== undefined)) return null;
  for (const key of ["xaxis", "yaxis"]) if (record(layout[key]).type !== "linear") return null;
  const rows = new Set<number>(), names = new Set<string>();
  const groups: Array<{ label: string; pointCount: number; validPointCount: number }> = [];
  const traces: Array<{ x: number[]; y: number[]; color: number[] | null; rows: unknown[][]; label: string }> = [];
  let points = 0, valid = 0, xmin = Infinity, xmax = -Infinity, ymin = Infinity, ymax = -Infinity;
  for (let index = 0; index < root.groups.length; index++) {
    const group = record(root.groups[index]), trace = record(figure.data[index]), marker = record(trace.marker);
    const x = readPlotNumericVector(trace.x), y = readPlotNumericVector(trace.y), custom = trace.customdata;
    if (!label(group.label) || names.has(group.label) || !count(group.pointCount) || group.pointCount < 1
      || !count(group.validPointCount) || group.validPointCount < group.pointCount || trace.name !== group.label
      || !["scatter", "scattergl"].includes(String(trace.type)) || trace.mode !== "markers"
      || !x || !y || x.length !== group.pointCount || y.length !== x.length || !Array.isArray(custom) || custom.length !== x.length
      || ["transforms", "error_x", "error_y", "fill", "stackgroup", "xaxis", "yaxis"].some(key => trace[key] !== undefined)
      || trace.visible !== undefined && trace.visible !== true) return null;
    const color = root.colorMode === "numeric" ? readPlotNumericVector(marker.color) : null;
    if (root.colorMode === "numeric" ? !color || color.length !== x.length || marker.coloraxis !== "coloraxis" : marker.coloraxis !== undefined || Array.isArray(marker.color)) return null;
    for (let point = 0; point < x.length; point++) {
      const row = custom[point];
      if (!Array.isArray(row) || row.length !== root.hoverColumns.length + 1 || !row.every(scalar)
        || !count(row[0]) || row[0] < 1 || row[0] > Number(root.inputCount) || rows.has(row[0])) return null;
      rows.add(row[0]);
      xmin = Math.min(xmin, x[point]); xmax = Math.max(xmax, x[point]);
      ymin = Math.min(ymin, y[point]); ymax = Math.max(ymax, y[point]);
    }
    names.add(group.label); points += group.pointCount; valid += group.validPointCount;
    groups.push({ label: group.label, pointCount: group.pointCount, validPointCount: group.validPointCount });
    traces.push({ x, y, color, rows: custom as unknown[][], label: group.label });
  }
  if (points !== root.pointCount || valid !== root.validPointCount || xRange[0] !== xmin || xRange[1] !== xmax || yRange[0] !== ymin || yRange[1] !== ymax) return null;
  const notes: string[] = [];
  if (root.excludedCoordinateCount) notes.push(`已排除 ${root.excludedCoordinateCount} 行横轴或纵轴缺失、非数值或非有限值。`);
  if (root.excludedColorCount) notes.push(`另排除 ${root.excludedColorCount} 行连续颜色缺失或非有限值。`);
  if (root.omittedPointCount) notes.push(`已绘制 ${points} / ${valid} 个有效点；按来源行均匀采样并保留极值和每个分组，原始数据未改动。`);
  const escape = (v: string) => v.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const hovertemplate = `${escape(root.xColumn)}：%{x}<br>${escape(root.yColumn)}：%{y}<br>来源行：%{customdata[0]}`
    + root.hoverColumns.map((column, index) => `<br>${escape(column)}：%{customdata[${index + 1}]}`).join("")
    + (root.colorMode === "numeric" ? `<br>${escape(String(root.colorColumn))}：%{marker.color}` : "") + "<extra>%{fullData.name}</extra>";
  return { traces, groups, notes, hovertemplate, hoverColumns: root.hoverColumns as string[],
    colorMode: root.colorMode as "none" | "numeric" | "categorical", colorColumn: root.colorColumn as string | null,
    xColumn: root.xColumn, yColumn: root.yColumn, pointCount: points };
}
