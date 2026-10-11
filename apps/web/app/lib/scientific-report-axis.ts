import { reportSvgTextWidth, wrapReportSvgText } from "./scientific-report-svg-text";

export type ReportAxisTick = { value: number; label: string };
const finite = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value);
const short = (value: number) => Number(value.toPrecision(5)).toString();

export function reportAxisTickNotes(ticks: ReportAxisTick[], width: number): string[] {
  if (!ticks.length) return [];
  const lines = wrapReportSvgText("纵轴其余刻度（标签 = 原始数值）：", width, 14);
  let row = "";
  for (const tick of ticks) {
    const pair = `${tick.label} = ${tick.value}`;
    if (row && reportSvgTextWidth(`${row}；${pair}`, 14) > width) { lines.push(row); row = ""; }
    if (reportSvgTextWidth(pair, 14) > width) {
      lines.push(...wrapReportSvgText(tick.label, width, 14), `= ${tick.value}`);
    } else row = row ? `${row}；${pair}` : pair;
  }
  if (row) lines.push(row);
  return lines;
}

/** Keep labels paired with their saved coordinate before range clipping. */
export function readReportAxisTicks(axis: Record<string, unknown>, min: number, max: number, count = 6): ReportAxisTick[] | null {
  const custom = axis.tickmode !== "auto" && axis.tickmode !== "linear" && axis.tickvals !== undefined;
  if (axis.tickmode === "array" && !custom) return null;
  if (axis.tickmode === "linear") return null;
  if (!custom) return Array.from({ length: count }, (_, i) => {
    let value = min + (max - min) * i / (count - 1);
    // Cancellation while interpolating across zero can leave a few ULPs of
    // residue. Only normalize generated interior ticks at that roundoff scale;
    // small scientific ranges, endpoints and all saved ticks stay exact.
    const crossesZero = (min < 0 && max > 0) || (min > 0 && max < 0);
    const roundoff = Math.max(Math.abs(min), Math.abs(max)) * Number.EPSILON * 4;
    if (i > 0 && i < count - 1 && crossesZero && Math.abs(value) <= roundoff) value = 0;
    return { value, label: short(value) };
  });
  if (!Array.isArray(axis.tickvals) || axis.tickvals.length > 2048 || !axis.tickvals.every(finite)
    || (axis.ticktext !== undefined && (!Array.isArray(axis.ticktext)
      || axis.ticktext.some(value => value != null && typeof value !== "string" && !finite(value))))) return null;
  const text = Array.isArray(axis.ticktext) ? axis.ticktext : [];
  return axis.tickvals.map((value, i) => ({ value, label: text[i] == null ? short(value) : String(text[i]) }))
    .filter(tick => tick.value >= Math.min(min, max) && tick.value <= Math.max(min, max));
}

/** Greedy rows preserve exact tick positions without overlapping label boxes. */
export function layoutReportXTicks(ticks: ReportAxisTick[], project: (value: number) => number, left: number, right: number) {
  const rowEnds: number[] = [], rowHeights: number[] = [];
  const items = ticks.map(tick => {
    const lines = wrapReportSvgText(tick.label, right - left, 16);
    const width = Math.max(0, ...lines.map(line => reportSvgTextWidth(line, 16)));
    const position = project(tick.value), x = Math.max(left, Math.min(right - width, position - width / 2));
    return { ...tick, lines, width, position, x, row: 0 };
  }).sort((a, b) => a.x - b.x || a.position - b.position);
  for (const item of items) {
    let row = rowEnds.findIndex(end => end + 8 <= item.x);
    if (row < 0) row = rowEnds.length;
    item.row = row;
    rowEnds[row] = item.x + item.width;
    rowHeights[row] = Math.max(rowHeights[row] || 0, Math.max(1, item.lines.length) * 22);
  }
  const offsets: number[] = [];
  let height = 0;
  for (const rowHeight of rowHeights) { offsets.push(height); height += rowHeight; }
  return { items: items.map(item => ({ ...item, offset: offsets[item.row] })), extraHeight: Math.max(0, height - 22), rows: rowEnds.length };
}
