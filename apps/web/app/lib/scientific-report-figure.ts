import { normalizedPlotFigure } from "../../scientific-viewers/workspace/workspace-plot-contract";
import { readPlotCoordinates, readPlotNumericVector } from "../../scientific-viewers/workspace/workspace-plot-data";
import { isSavedDensityPlot } from "../../scientific-viewers/workspace/saved-density-plot";
import { renderReportDensity } from "./scientific-report-density";
import { isSavedPeriodicTable } from "../../scientific-viewers/workspace/saved-periodic-table";
import { renderReportPeriodicTable } from "./scientific-report-periodic-table";
import { renderReportHeatmap } from "./scientific-report-heatmap";
import { reportSvgTextWidth, wrapReportSvgText } from "./scientific-report-svg-text";
import { histogramNotes, isSavedHistogram, readSavedHistogram } from "../../scientific-viewers/workspace/saved-histogram";
import { isSavedScatter, readSavedScatter } from "../../scientific-viewers/workspace/saved-scatter";
import { isSavedElementHistogram } from "../../scientific-viewers/workspace/saved-element-histogram";
import { isSavedFormulaComposition } from "../../scientific-viewers/workspace/saved-formula-composition";
import { renderReportElements } from "./scientific-report-elements";
import { renderReportHierarchy } from "./scientific-report-hierarchy";
import { renderReportStructure } from "./scientific-report-structure";
import { isSavedLocalEnvironment } from "../../scientific-viewers/workspace/saved-local-environment";
import { renderReportLocalEnvironment } from "./scientific-report-local-environment";
import { layoutReportXTicks, readReportAxisTicks, reportAxisTickNotes } from "./scientific-report-axis";

type RecordValue = Record<string, unknown>;
const record = (value: unknown): RecordValue => value && typeof value === "object" && !Array.isArray(value) ? value as RecordValue : {};
const finite = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value);
export const escapeReportHtml = (value: string) => value.replace(/[&<>"']/gu, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]!);
const axisTitle = (value: unknown) => typeof value === "string" ? value : typeof record(value).text === "string" ? String(record(value).text) : "";
const SERIES_COLORS = ["#08756c", "#b34c39", "#355b99", "#755398", "#8a6510"];

/** The adapter emits a separate trace for each saved branch segment. Keep that identity. */
function savedPhononStyles(root: RecordValue) {
  const metadata = record(root.metadata);
  if (root.artifact_type !== "phonon.band_plot" || !Array.isArray(root.data) || !root.data.length || root.data.length > 64
    || metadata.discontinuities_split !== true || !Number.isInteger(metadata.branch_count) || !Number.isInteger(metadata.segment_count)
    || Number(metadata.branch_count) < 1 || Number(metadata.segment_count) < 1 || metadata.trace_count !== root.data.length) return null;
  const groups = new Map<string, number>();
  const styles = [];
  for (const value of root.data) {
    const trace = record(value), match = /^branch-(0|[1-9]\d*)$/u.exec(String(trace.legendgroup));
    if (!match || !Number.isSafeInteger(Number(match[1])) || trace.name !== `Branch ${Number(match[1]) + 1}`
      || trace.mode !== "lines" || trace.line !== undefined || trace.connectgaps === true) return null;
    const id = String(trace.legendgroup);
    if (!groups.has(id)) groups.set(id, 0);
    groups.set(id, groups.get(id)! + 1);
    const index = [...groups.keys()].indexOf(id);
    styles.push({ color: SERIES_COLORS[index % SERIES_COLORS.length], dash: index >= SERIES_COLORS.length ? "6 4" : "", label: `分支 ${match[1]}`, identity: id });
  }
  if (groups.size !== metadata.branch_count || [...groups.values()].some(count => count !== metadata.segment_count)) return null;
  return styles;
}

/** Interpret only the saved electronic contract; do not infer breaks from distances or energies. */
function savedBandProjection(root: RecordValue): {
  data: RecordValue[];
  styles: Array<{ color: string; dash: string; label: string }>;
  breaks: number[];
  fermi: { x0: number; x1: number; energy: number } | null;
} | null {
  if (!Array.isArray(root.data) || !root.data.length || root.data.length > 64
    || !Array.isArray(root.pathSegments) || !root.pathSegments.length || root.pathSegments.length > 1024) return null;
  const first = record(root.data[0]), ids = first.customdata, distances = first.x;
  if (!Array.isArray(ids) || !ids.length || ids.length * root.data.length > 50_000
    || !ids.every(id => typeof id === "string" && id.length > 0) || new Set(ids).size !== ids.length
    || !Array.isArray(distances) || distances.length !== ids.length || !distances.every(finite)) return null;
  const indices = new Map(ids.map((id, index) => [id, index]));
  const cuts = new Set<number>(), segmentIds = new Set<string>();
  for (const value of root.pathSegments) {
    const segment = record(value), start = indices.get(segment.startKpointId), end = indices.get(segment.endKpointId);
    if (typeof segment.segmentId !== "string" || !segment.segmentId || segmentIds.has(segment.segmentId)
      || start === undefined || end === undefined || start > end || typeof segment.breakAfter !== "boolean") return null;
    segmentIds.add(segment.segmentId);
    if (segment.breakAfter && end + 1 < ids.length) cuts.add(end + 1);
  }
  const shapes = record(root.layout).shapes;
  if (!Array.isArray(shapes) || shapes.length > 1) return null;
  let fermi: { x0: number; x1: number; energy: number } | null = null;
  if (shapes.length) {
    const shape = record(shapes[0]), line = record(shape.line);
    if (Object.keys(shape).some(key => !["type", "x0", "x1", "y0", "y1", "line"].includes(key))
      || Object.keys(line).some(key => key !== "dash") || line.dash !== "dash"
      || shape.type !== "line" || !finite(shape.x0) || !finite(shape.x1) || !finite(shape.y0) || shape.y0 !== shape.y1) return null;
    fermi = { x0: shape.x0, x1: shape.x1, energy: shape.y0 };
  }
  const bandColors = new Map<string, string>(), names = new Set<string>();
  const styles: Array<{ color: string; dash: string; label: string }> = [], data: RecordValue[] = [];
  for (const value of root.data) {
    const trace = record(value), name = typeof trace.name === "string" ? trace.name : "";
    const identity = /^(none|up|down):(.+)$/u.exec(name);
    if (!identity || names.has(name) || trace.line !== undefined || trace.connectgaps === true
      || !Array.isArray(trace.customdata) || trace.customdata.length !== ids.length || trace.customdata.some((id, i) => id !== ids[i])
      || !Array.isArray(trace.x) || trace.x.length !== ids.length || trace.x.some((x, i) => x !== distances[i])
      || !Array.isArray(trace.y) || trace.y.length !== ids.length || !trace.y.every(finite)) return null;
    names.add(name);
    const [, spin, band] = identity;
    if (!bandColors.has(band)) bandColors.set(band, SERIES_COLORS[bandColors.size % SERIES_COLORS.length]);
    styles.push({ color: bandColors.get(band)!, dash: spin === "down" ? "6 4" : "", label: `${band}${spin === "none" ? "" : spin === "up" ? " · ↑" : " · ↓"}` });
    const x: Array<number | null> = [], y: Array<number | null> = [];
    for (let i = 0; i < ids.length; i++) {
      if (cuts.has(i)) { x.push(null); y.push(null); }
      x.push(distances[i]); y.push(trace.y[i]);
    }
    data.push({ ...trace, x, y });
  }
  return { data, styles, fermi, breaks: [...new Set([...cuts].flatMap(cut => [distances[cut - 1], distances[cut]]))] };
}

/** Bounded, inert SVGs of saved scientific data. Unsupported semantics remain raw files. */
export function renderScientificReportFigure(payload: unknown, title: string, options?: { width?: number; compact?: boolean }): {
  svg: string; pointCount: number; fit?: "width"; axes: Array<{ label: string; range: string | null; ticks: string | null }>;
} | null {
  if (record(payload).kind === "viewer_scene") return renderReportStructure(payload, title, options);
  if (isSavedLocalEnvironment(payload)) return renderReportLocalEnvironment(payload, title, options);
  if (isSavedElementHistogram(payload) || isSavedElementComparison(payload) || isSavedFormulaComposition(payload)) return renderReportElements(payload, title, options);
  const hierarchy = renderReportHierarchy(payload, title, options);
  if (hierarchy) return hierarchy;
  const scatter = isSavedScatter(payload) ? readSavedScatter(payload) : null;
  if (isSavedScatter(payload) && !scatter) return null;
  if (isSavedPeriodicTable(payload)) return renderReportPeriodicTable(payload, title, options);
  if (isSavedDensityPlot(payload)) return renderReportDensity(payload, title, options);
  const heatmap = renderReportHeatmap(payload, title, options);
  if (heatmap) return heatmap;
  const root = record(payload);
  const histogram = isSavedHistogram(payload) ? readSavedHistogram(payload) : null;
  if (isSavedHistogram(payload) && !histogram) return null;
  const stem = root.chart_type === "stem";
  const isBand = root.schemaVersion === "phase10n5.electronic_band_plot.v1";
  const band = isBand ? savedBandProjection(root) : null;
  const isPhonon = root.schema_version === "phase10h1.phonon_band_plot.v1";
  const phonon = isPhonon ? savedPhononStyles(root) : null;
  if (isPhonon && !phonon) return null;
  if ((isBand && !band) || (!isBand && root.pathSegments !== undefined)) return null;
  const source = band ? { data: band.data, layout: root.layout } : stem ? {
    data: root.series,
    layout: {
      xaxis: { title: record(root.x_axis).label, range: [record(root.metadata).two_theta_min, record(root.metadata).two_theta_max] },
      yaxis: { title: record(root.y_axis).label },
    },
  } : normalizedPlotFigure(payload) || (Array.isArray(root.series) && !root.chart_type ? {
    data: root.series, layout: root.layout,
  } : null);
  if (!source || !Array.isArray(source.data) || !source.data.length || source.data.length > 64) return null;
  if (Array.isArray(root.series) && source.data.length !== root.series.length) return null;
  const layout = record(source.layout), xaxis = record(layout.xaxis), yaxis = record(layout.yaxis);
  if ([xaxis, yaxis].some(axis => axis.type && axis.type !== "linear" && axis.type !== "-")) return null;
  if (layout.barmode && layout.barmode !== "overlay" && !(histogram && layout.barmode === "stack")) return null;
  if (layout.annotations || (!band && layout.shapes)) return null;
  let pointCount = 0;
  const traces: Array<{ name: string; type: string; mode: string; points: Array<[number, number] | null>; widths?: number[]; color: string; dash: string; label: string }> = [];
  for (const [index, value] of source.data.entries()) {
    const trace = record(value), type = stem ? "stem" : String(trace.type || "scatter");
    if (!["stem", "scatter", "scattergl", "bar"].includes(type) || trace.orientation === "h" || trace.xaxis || trace.yaxis
      || trace.error_x || trace.error_y || trace.fill || trace.transforms || trace.stackgroup || (trace.visible !== undefined && trace.visible !== true)
      || (record(trace.line).shape && record(trace.line).shape !== "linear")) return null;
    const x = readPlotCoordinates(trace.x), y = readPlotCoordinates(trace.y);
    if (!Array.isArray(x) || !Array.isArray(y) || x.length !== y.length) return null;
    if ((pointCount += x.length) > 50_000) return null;
    const points: Array<[number, number] | null> = [];
    for (let i = 0; i < x.length; i++) {
      const xValue = x[i], yValue = y[i];
      if (xValue === null || yValue === null) { points.push(null); continue; }
      if (!finite(xValue) || !finite(yValue)) return null;
      points.push([xValue, yValue]);
    }
    const mode = String(trace.mode || (type === "scatter" || type === "scattergl" ? "lines+markers" : ""));
    if (type !== "stem" && type !== "bar" && !["lines", "markers", "lines+markers"].includes(mode)) return null;
    const widths = type === "bar" && trace.width !== undefined ? readPlotNumericVector(trace.width) : undefined;
    if (widths !== undefined && (!Array.isArray(widths) || widths.length !== x.length || !widths.every(value => finite(value) && value > 0))) return null;
    if (type === "bar" && (trace.offset !== undefined || trace.base !== undefined)) return null;
    const name = typeof trace.name === "string" ? trace.name : `序列 ${index + 1}`;
    traces.push({ name, type, mode, points, widths: widths as number[] | undefined, ...(band?.styles[index] || phonon?.[index] || { color: SERIES_COLORS[index % SERIES_COLORS.length], dash: "", label: name }) });
  }
  const points = traces.flatMap(trace => trace.points.filter((point): point is [number, number] => point !== null));
  if (!points.length) return null;
  pointCount = points.length;
  const histogramBases = histogram?.groups.map((_, index) => histogram.counts.map((__, bin) =>
    histogram.groups.slice(0, index).reduce((sum, group) => sum + group.counts[bin], 0)));
  let xmin = Infinity, xmax = -Infinity, ymin = Infinity, ymax = -Infinity;
  for (const [x, y] of points) { xmin = Math.min(xmin, x); xmax = Math.max(xmax, x); ymin = Math.min(ymin, y); ymax = Math.max(ymax, y); }
  if (histogram) ymax = Math.max(ymax, ...histogram.counts);
  for (const trace of traces) if (trace.widths) trace.points.forEach((point, index) => {
    if (point) { xmin = Math.min(xmin, point[0] - trace.widths![index] / 2); xmax = Math.max(xmax, point[0] + trace.widths![index] / 2); }
  });
  if (traces.some(trace => trace.type === "bar" || trace.type === "stem")) { ymin = Math.min(0, ymin); ymax = Math.max(0, ymax); }
  if (band?.fermi) { ymin = Math.min(ymin, band.fermi.energy); ymax = Math.max(ymax, band.fermi.energy); }
  const domain = (axis: RecordValue, min: number, max: number): [number, number] => {
    if (Array.isArray(axis.range) && axis.range.length === 2 && axis.range.every(finite) && axis.range[0] !== axis.range[1]) return [axis.range[0], axis.range[1]];
    if (axis.autorange === "reversed") return max === min ? [max + 1, min - 1] : [max, min];
    const padding = Math.max(1, Math.abs(min) * 0.05);
    const pointPadding = scatter ? (max - min) * 0.05 : 0;
    return min === max ? [min - padding, max + padding] : [min - pointPadding, max + pointPadding];
  };
  const [x0, x1] = domain(xaxis, xmin, xmax), [y0, y1] = domain(yaxis, ymin, ymax);
  if (![x0, x1, y0, y1, x1 - x0, y1 - y0].every(finite) || x0 === x1 || y0 === y1) return null;
  const width = finite(options?.width) ? Math.max(360, Math.min(1200, options.width)) : 920;
  const yTicks = readReportAxisTicks(yaxis, y0, y1);
  if (!yTicks) return null;
  const yTickLabels = yTicks.map(tick => tick.label);
  // Reserve space for long decimals and signed exponents before positioning
  // the plot. A fixed gutter let tick labels collide with the vertical title.
  const tickWidth = Math.max(0, ...yTickLabels.map(label => reportSvgTextWidth(label)));
  const left = Math.max(width < 640 ? 96 : 100, tickWidth + 50), right = width - 24;
  if (right - left < 120) return null;
  const titleLines = options?.compact ? [] : wrapReportSvgText(title, right - left, 24);
  const top = titleLines.length ? 58 + titleLines.length * 32 : 24;
  const plotHeight = 300, bottom = top + plotHeight;
  const x = (value: number) => left + (value - x0) / (x1 - x0) * (right - left);
  const y = (value: number) => bottom - (value - y0) / (y1 - y0) * plotHeight;
  const xml = escapeReportHtml;
  const xTicks = readReportAxisTicks(xaxis, x0, x1, Math.min(6, Math.max(3, Math.floor((right - left) / 120) + 1)));
  if (!xTicks) return null;
  const xTickLayout = layoutReportXTicks(xTicks, x, left, right);
  const tickLeaders = xTickLayout.items.map(tick => `<path d="M${tick.position} ${bottom + 6}L${tick.x + tick.width / 2} ${bottom + 12 + tick.offset}" stroke="#71817a" fill="none"/>`).join("");
  const xticks = tickLeaders + xTickLayout.items.map(tick => `<g data-axis-tick="x" data-value="${tick.value}"><line x1="${tick.position}" y1="${bottom}" x2="${tick.position}" y2="${bottom + 6}" stroke="#44514b"/><rect x="${tick.x - 2}" y="${bottom + 12 + tick.offset}" width="${tick.width + 4}" height="${Math.max(1, tick.lines.length) * 22}" fill="#fff"/><text x="${tick.x}" y="${bottom + 28 + tick.offset}">${tick.lines.map((line, i) => `<tspan x="${tick.x}" dy="${i ? 22 : 0}">${xml(line)}</tspan>`).join("")}</text></g>`).join("");
  const placedYTicks = yTicks.map(tick => ({ ...tick, position: y(tick.value) })).sort((a, b) => a.position - b.position);
  const visibleYTicks: typeof placedYTicks = [];
  for (const tick of placedYTicks) if (!visibleYTicks.length || tick.position - visibleYTicks.at(-1)!.position >= 22) visibleYTicks.push(tick);
  const lastYTick = placedYTicks.at(-1);
  if (lastYTick && visibleYTicks.at(-1) !== lastYTick) {
    while (visibleYTicks.length && lastYTick.position - visibleYTicks.at(-1)!.position < 22) visibleYTicks.pop();
    visibleYTicks.push(lastYTick);
  }
  const hiddenYTicks = placedYTicks.filter(tick => !visibleYTicks.includes(tick));
  const yticks = placedYTicks.map(tick => `<g data-axis-tick="y" data-value="${tick.value}"><title>${xml(`${tick.label} = ${tick.value}`)}</title><line x1="${left}" y1="${tick.position}" x2="${right}" y2="${tick.position}" stroke="#e7ece9"/>${visibleYTicks.includes(tick) ? `<text x="${left - 14}" y="${tick.position + 5}" text-anchor="end">${xml(tick.label)}</text>` : ""}</g>`).join("");
  const xTitle = phonon && axisTitle(xaxis.title) === "Wave vector path" ? "波矢路径" : axisTitle(xaxis.title) || "X（原始坐标）";
  const xTitleLines = wrapReportSvgText(xTitle, right - left);
  const xTitleY = bottom + 65 + xTickLayout.extraHeight;
  const xAxisExtra = xTickLayout.extraHeight + Math.max(0, xTitleLines.length - 1) * 22;
  const geometry = traces.map((trace, index) => {
    const color = trace.color;
    if (histogram && histogramBases) return trace.points.map((point, bin) => {
      if (!point) return "";
      const base = histogramBases[index][bin], end = base + point[1];
      const lo = histogram.edges[bin], hi = histogram.edges[bin + 1];
      return `<rect data-series="${xml(trace.name)}" data-bin="${bin}" data-count="${point[1]}" data-base="${base}" x="${Math.min(x(lo), x(hi))}" y="${Math.min(y(base), y(end))}" width="${Math.abs(x(hi) - x(lo))}" height="${Math.abs(y(base) - y(end))}" fill="${color}"><title>${xml(`${trace.name}: [${lo}, ${hi}${bin === histogram.counts.length - 1 ? "]" : ")"}, ${point[1]}`)}</title></rect>`;
    }).join("");
    if (trace.type === "bar" && trace.widths) return trace.points.map((point, i) => point ? `<rect data-bin="${i}" x="${Math.min(x(point[0] - trace.widths![i] / 2), x(point[0] + trace.widths![i] / 2))}" y="${Math.min(y(0), y(point[1]))}" width="${Math.abs(x(point[0] + trace.widths![i] / 2) - x(point[0] - trace.widths![i] / 2))}" height="${Math.abs(y(0) - y(point[1]))}" fill="${color}"><title>${xml(`${trace.name}: [${point[0] - trace.widths![i] / 2}, ${point[0] + trace.widths![i] / 2}], ${point[1]}`)}</title></rect>` : "").join("");
    if (trace.type === "stem" || trace.type === "bar") return trace.points.map(point => point ? `<line x1="${x(point[0])}" y1="${y(0)}" x2="${x(point[0])}" y2="${y(point[1])}" stroke="${color}" stroke-width="${trace.type === "stem" ? 1.4 : Math.max(1, Math.min(16, 592 / trace.points.length))}"><title>${xml(`${trace.name}: ${point[0]}, ${point[1]}`)}</title></line>` : "").join("");
    // Static scatter exports retain every saved point and its source-row key.
    // Round only SVG pixel positions, not scientific values in the original.
    // Repeating full tooltips in four responsive images can exceed the ZIP cap.
    if (scatter) return `<g data-series="${xml(trace.name)}" fill="${color}" fill-opacity="0.85">${trace.points.map((point, i) => point ? `<circle data-source-row="${scatter.traces[index].rows[i][0]}" cx="${Number(x(point[0]).toFixed(3))}" cy="${Number(y(point[1]).toFixed(3))}" r="3"/>` : "").join("")}</g>`;
    let path = "", open = false;
    for (const point of trace.points) {
      if (!point) { open = false; continue; }
      path += `${open ? "L" : "M"}${x(point[0])},${y(point[1])} `;
      open = true;
    }
    const lines = trace.mode.includes("lines") ? `<path data-series="${xml(trace.name)}" d="${path}" fill="none" stroke="${color}" stroke-width="1.5"${trace.dash ? ` stroke-dasharray="${trace.dash}"` : ""}><title>${xml(trace.name)}</title></path>` : "";
    const dots = trace.mode.includes("markers") ? trace.points.map(point => point ? `<circle cx="${x(point[0])}" cy="${y(point[1])}" r="2.5" fill="${color}"><title>${xml(`${trace.name}: ${point[0]}, ${point[1]}`)}</title></circle>` : "").join("") : "";
    return lines + dots;
  }).join("");
  const legendTraces = phonon ? traces.filter((_, index) => phonon.findIndex(style => style.identity === phonon[index].identity) === index) : traces;
  let legendX = left, legendY = bottom + 100 + xAxisExtra, rowHeight = 0;
  const legend = legendTraces.map(trace => {
    const lines = wrapReportSvgText(trace.label, right - left - 32);
    const itemWidth = 32 + Math.max(0, ...lines.map(line => reportSvgTextWidth(line)));
    if (legendX > left && legendX + itemWidth > right) {
      legendX = left; legendY += rowHeight; rowHeight = 0;
    }
    const sample = trace.type === "bar"
      ? `<rect x="${legendX}" y="${legendY - 12}" width="18" height="10" fill="${trace.color}"/>`
      : `<line x1="${legendX}" x2="${legendX + 18}" y1="${legendY - 5}" y2="${legendY - 5}" stroke="${trace.color}" stroke-width="2"${trace.dash ? ` stroke-dasharray="${trace.dash}"` : ""}/>`;
    const marker = trace.mode.includes("markers") ? `<circle cx="${legendX + 9}" cy="${legendY - 5}" r="3" fill="${trace.color}"/>` : "";
    const item = `<g data-legend="${xml(trace.label)}"><title>${xml(trace.name)}</title>${trace.mode === "markers" ? "" : sample}${marker}<text>${lines.map((line, i) => `<tspan x="${legendX + 24}" y="${legendY + i * 24}">${xml(line)}</tspan>`).join("")}</text></g>`;
    legendX += itemWidth + 24;
    rowHeight = Math.max(rowHeight, Math.max(1, lines.length) * 24);
    return item;
  }).join("");
  const legendEnd = legendY + rowHeight;
  const zeroLine = phonon && yaxis.zeroline === true && Math.min(y0, y1) <= 0 && Math.max(y0, y1) >= 0
    ? `<line data-reference="zero-frequency" x1="${left}" x2="${right}" y1="${y(0)}" y2="${y(0)}" stroke="#44514b" stroke-dasharray="6 4"><title>零频率</title></line>` : "";
  const fermi = band?.fermi;
  const reference = fermi ? `<line data-reference="fermi" x1="${x(fermi.x0)}" x2="${x(fermi.x1)}" y1="${y(fermi.energy)}" y2="${y(fermi.energy)}" stroke="#44514b" stroke-dasharray="6 4"><title>${xml(`费米能级：${fermi.energy} eV`)}</title></line>` : "";
  const referenceLegend = fermi ? `<text x="${left}" y="${legendEnd}" font-size="14" fill="#44514b">${xml(`费米能级：${fermi.energy} eV（虚线）`)}</text>` : "";
  const pathBreaks = (band?.breaks || []).map(value => `<line data-path-break="${value}" x1="${x(value)}" x2="${x(value)}" y1="${top}" y2="${bottom}" stroke="#44514b" stroke-dasharray="2 4"><title>路径断点</title></line>`).join("");
  const breakLegend = pathBreaks ? `<text x="${left}" y="${legendEnd + (fermi ? 24 : 0)}" font-size="14" fill="#44514b">路径断点（竖点线）</text>` : "";
  const footerLeft = hiddenYTicks.length ? 20 : left, footerWidth = right - footerLeft;
  const footerLines = [
    ...reportAxisTickNotes(hiddenYTicks, footerWidth),
    ...(options?.compact ? [] : wrapReportSvgText(`完整显示 ${pointCount} 个数据点 · 原始数据随报告提供`, footerWidth, 14)),
    ...(histogram ? histogramNotes(histogram).flatMap(note => wrapReportSvgText(note, footerWidth, 14)) : []),
    ...(scatter ? scatter.notes.flatMap(note => wrapReportSvgText(note, footerWidth, 14)) : []),
  ];
  const height = legendEnd + (fermi ? 24 : 0) + (pathBreaks ? 24 : 0) + (footerLines.length ? 22 + footerLines.length * 20 : 8);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="title desc">
<title id="title">${xml(title)}</title><desc id="desc">已保存的二维图表，完整 ${pointCount} 个有限数据点。未重新计算科学结果。</desc>
<rect width="${width}" height="${height}" fill="#ffffff"/><defs><clipPath id="plot"><rect x="${left}" y="${top}" width="${right - left}" height="${plotHeight}"/></clipPath></defs>
<g font-family="system-ui,sans-serif" font-size="16" fill="#17211e">${titleLines.map((line, i) => `<text data-plot-title="true" x="${left}" y="${40 + i * 32}" font-size="24" font-weight="600">${xml(line)}</text>`).join("")}${yticks}${xticks}
<path d="M${left} ${top}V${bottom}H${right}" fill="none" stroke="#44514b"/><g clip-path="url(#plot)">${reference}${zeroLine}${pathBreaks}${geometry}</g>
<text data-axis-title="x" x="${(left + right) / 2}" y="${xTitleY}" text-anchor="middle">${xTitleLines.map((line, i) => `<tspan x="${(left + right) / 2}" dy="${i ? 22 : 0}">${xml(line)}</tspan>`).join("")}</text><text x="20" y="${top + plotHeight / 2}" text-anchor="middle" transform="rotate(-90 20 ${top + plotHeight / 2})">${xml(phonon && axisTitle(yaxis.title) === "Frequency (THz)" ? "频率 (THz)" : axisTitle(yaxis.title) || "Y（原始数值）")}</text>
${legend}${referenceLegend}${breakLegend}${footerLines.map((line, index) => `<text data-plot-footer="true" x="${footerLeft}" y="${height - 16 - (footerLines.length - index - 1) * 20}" font-size="14" fill="#44514b">${xml(line)}</text>`).join("")}</g></svg>`;
  const axes = [xaxis, yaxis].map((axis, index) => ({
    label: axisTitle(axis.title) || (index === 0 ? "X（原始坐标）" : "Y（原始数值）"),
    range: Array.isArray(axis.range) && axis.range.length === 2 && axis.range.every(finite) ? axis.range.join(" 至 ") : null,
    ticks: Array.isArray(axis.tickvals) ? axis.tickvals.map((v, i) => Array.isArray(axis.ticktext) ? String(axis.ticktext[i] ?? v) : String(v)).join(" · ") : null,
  }));
  return { svg, pointCount, axes, ...(xTickLayout.rows > 1 || hiddenYTicks.length || (histogram?.groups.length ?? scatter?.groups.length ?? 0) > 4 ? { fit: "width" as const } : {}) };
}
import { isSavedElementComparison } from "../../scientific-viewers/workspace/saved-element-reference";
