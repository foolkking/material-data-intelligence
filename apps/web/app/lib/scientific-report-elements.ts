import { readSavedElementHistogram } from "../../scientific-viewers/workspace/saved-element-histogram";
import { isSavedElementComparison, readSavedElementComparison } from "../../scientific-viewers/workspace/saved-element-reference";
import { isSavedFormulaComposition, readSavedFormulaComposition } from "../../scientific-viewers/workspace/saved-formula-composition";
import { readPlotNumericVector } from "../../scientific-viewers/workspace/workspace-plot-data";
import { reportSvgTextWidth, wrapReportSvgText } from "./scientific-report-svg-text";

type Row = Record<string, unknown>;
const record = (v: unknown): Row => v && typeof v === "object" && !Array.isArray(v) ? v as Row : {};
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const has = (row: Row, keys: string[]) => keys.some(key => row[key] !== undefined);
const xml = (v: string) => v.replace(/[&<>"']/gu, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);
const short = (v: number) => Number(v.toPrecision(5)).toString();
const label = (v: unknown) => typeof v === "string" ? v : typeof record(v).text === "string" ? String(record(v).text) : "";

/** Project validated saved element values; no formula parsing or scientific recounting. */
export function renderReportElements(payload: unknown, title: string, options?: { width?: number; compact?: boolean }) {
  const saved = isSavedFormulaComposition(payload) ? readSavedFormulaComposition(payload)
    : isSavedElementComparison(payload) ? readSavedElementComparison(payload) : readSavedElementHistogram(payload);
  if (!saved) return null;
  const figure = record(record(payload).plotlyFigure), rawLayout = record(figure.layout), template = record(rawLayout.template);
  if (typeof rawLayout.template === "string") return null;
  const defaults = record(template.layout), barDefaults = record(template.data).bar;
  const trace: Row = { ...(Array.isArray(barDefaults) ? record(barDefaults[0]) : {}), ...record((figure.data as unknown[])[0]) };
  const layout = { ...defaults, ...rawLayout }, xaxis = { ...record(defaults.xaxis), ...record(rawLayout.xaxis) }, yaxis = { ...record(defaults.yaxis), ...record(rawLayout.yaxis) };
  if (trace.orientation !== undefined && trace.orientation !== "v" || trace.visible !== undefined && trace.visible !== true
    || trace.xaxis !== undefined && trace.xaxis !== "x" || trace.yaxis !== undefined && trace.yaxis !== "y"
    || has(trace, ["transforms", "offset", "texttemplate", "xperiod", "yperiod"])
    || [trace.error_x, trace.error_y].some(error => error !== undefined && (!error || typeof error !== "object" || Array.isArray(error) || record(error).visible === true
      || Object.keys(record(error)).some(key => !["color", "thickness", "width", "visible"].includes(key))))
    || trace.base !== undefined && trace.base !== 0 || Array.isArray(record(trace.marker).color) || finite(record(trace.marker).color)
    || has(record(trace.marker), ["colorscale", "coloraxis"])
    || has(layout, ["barnorm", "grid", "annotations", "shapes", "images"])
    || Object.keys(layout).some(key => /^[xy]axis\d/u.test(key))
    || xaxis.type !== undefined && !["category", "-"].includes(String(xaxis.type))
    || yaxis.type !== undefined && !["linear", "log", "-"].includes(String(yaxis.type))
    || has(xaxis, ["range", "tickvals", "ticktext"])
    || [xaxis, yaxis].some(axis => has(axis, ["overlaying", "matches", "scaleanchor", "rangebreaks", "tickprefix", "ticksuffix", "labelalias", "tickformat", "dtick", "tick0"])
      || axis.domain !== undefined && JSON.stringify(axis.domain) !== "[0,1]"
      || axis.autorange !== undefined && ![true, false, "reversed"].includes(axis.autorange as boolean)
      || axis.visible === false || axis.showticklabels === false)) return null;
  const widths = finite(trace.width) ? saved.elements.map(() => Number(trace.width))
    : trace.width === undefined ? saved.elements.map(() => 0.7) : readPlotNumericVector(trace.width);
  if (!widths || widths.length !== saved.elements.length || !widths.every(v => v > 0 && v <= 1)) return null;
  let entries = saved.elements.map((element, index) => ({ ...element, text: saved.textLabels?.[index], width: widths[index] }));
  const order = xaxis.categoryorder ?? "trace";
  if (order === "array") {
    if (!Array.isArray(xaxis.categoryarray) || xaxis.categoryarray.length > 118 || new Set(xaxis.categoryarray).size !== xaxis.categoryarray.length
      || xaxis.categoryarray.some(name => !entries.some(entry => entry.element === name))) return null;
    const names = [...xaxis.categoryarray, ...entries.map(entry => entry.element).filter(name => !(xaxis.categoryarray as unknown[]).includes(name))];
    entries.sort((a, b) => names.indexOf(a.element) - names.indexOf(b.element));
  } else if (order === "category ascending" || order === "category descending") {
    entries.sort((a, b) => a.element < b.element ? -1 : a.element > b.element ? 1 : 0);
    if (order === "category descending") entries.reverse();
  } else if (order === "total ascending" || order === "total descending") {
    entries.sort((a, b) => order === "total ascending" ? a.count - b.count : b.count - a.count);
  } else if (order !== "trace") return null;
  if (xaxis.autorange === "reversed") entries.reverse();
  const log = yaxis.type === "log", transform = (v: number) => log ? Math.log10(v) : v;
  const min = Math.min(...entries.map(e => transform(e.count))), max = Math.max(...entries.map(e => transform(e.count)));
  const span = max - min || 1;
  let range = log ? [min - span * 0.1, max + span * 0.15] : [0, max * 1.15];
  if (yaxis.range !== undefined && (yaxis.autorange === undefined || yaxis.autorange === false)) {
    if (!Array.isArray(yaxis.range) || yaxis.range.length !== 2 || !yaxis.range.every(finite)) return null;
    range = [...yaxis.range];
  } else if (yaxis.autorange === "reversed") range.reverse();
  const [y0, y1] = range, lo = Math.min(y0, y1), hi = Math.max(y0, y1);
  if (![y0, y1, y1 - y0].every(finite) || y0 === y1 || log && (![10 ** y0, 10 ** y1].every(finite) || 10 ** lo <= 0)) return null;
  let ticks: Array<{ value: number; text: string }>;
  if (yaxis.tickmode === "array" || yaxis.tickvals !== undefined) {
    const values = readPlotNumericVector(yaxis.tickvals);
    if (!values?.length || values.length > 32 || log && values.some(value => value <= 0)
      || yaxis.ticktext !== undefined && (!Array.isArray(yaxis.ticktext) || yaxis.ticktext.length !== values.length || yaxis.ticktext.some(v => typeof v !== "string" || v.length > 128))) return null;
    ticks = values.map((value, i) => ({ value, text: Array.isArray(yaxis.ticktext) ? String(yaxis.ticktext[i]) : short(value) }));
  } else {
    if (yaxis.ticktext !== undefined || yaxis.tickmode !== undefined && yaxis.tickmode !== "auto") return null;
    if (log) {
      const first = Math.ceil(lo), last = Math.floor(hi), step = Math.max(1, Math.ceil((last - first) / 4));
      const powers = Array.from({ length: Math.max(0, Math.floor((last - first) / step) + 1) }, (_, i) => first + i * step);
      const candidates = Array.from({ length: Math.ceil(hi) - Math.floor(lo) + 1 }, (_, i) => i + Math.floor(lo))
        .flatMap(power => [1, 2, 5].map(factor => factor * 10 ** power)).filter(value => finite(value) && value > 0 && transform(value) >= lo && transform(value) <= hi);
      const values = candidates.length > 8 ? powers.map(power => 10 ** power) : candidates.length ? candidates : [10 ** lo, 10 ** hi];
      ticks = values.map(value => ({ value, text: short(value) }));
    } else {
      const rough = (hi - lo) / 5, power = 10 ** Math.floor(Math.log10(rough));
      const step = [1, 2, 2.5, 5, 10].find(factor => factor * power >= rough)! * power;
      if (!finite(step) || step <= 0) return null;
      const first = Math.ceil(lo / step) * step;
      ticks = Array.from({ length: 7 }, (_, i) => first + i * step).filter(value => value <= hi).map(value => ({ value, text: short(value) }));
    }
  }
  ticks = ticks.filter(tick => transform(tick.value) >= lo && transform(tick.value) <= hi);
  const width = finite(options?.width) ? Math.max(360, Math.min(1200, options.width)) : 920;
  const font = width < 600 ? 14 : 15;
  const left = Math.max(56, ...ticks.map(tick => reportSvgTextWidth(tick.text, font) + 24)), right = width - 20, plotWidth = right - left;
  if (plotWidth < 120) return null;
  const needed = Math.max(44, ...entries.map(entry => Math.min(150, reportSvgTextWidth(entry.text ?? "", font) + 16)));
  const perPanel = Math.max(1, Math.floor(plotWidth / needed)), panelCount = Math.ceil(entries.length / perPanel);
  const savedTitle = label(layout.title);
  const distinctTitle = savedTitle && savedTitle !== "Element Histogram" && savedTitle !== title ? savedTitle : "";
  const heading = [options?.compact ? "" : title, distinctTitle].filter(Boolean).join("\n");
  const titleLines = wrapReportSvgText(heading, width - 40, 22);
  const yLabel = label(yaxis.title) || saved.label;
  const scaleLabel = log && !yLabel.includes("对数刻度") ? `${yLabel}（对数刻度）` : yLabel;
  const intro = wrapReportSvgText(scaleLabel, width - 40, font);
  if (panelCount > 1) intro.push(...wrapReportSvgText(`${entries.length} 个元素 · 分段显示，纵轴刻度一致`, width - 40, font));
  let cursor = 20 + titleLines.length * 30 + intro.length * 22;
  const panels: string[] = [], plotHeight = width < 600 ? 190 : 240;
  const baseline = log ? lo : 0;
  for (let panel = 0; panel < panelCount; panel++) {
    const subset = entries.slice(panel * perPanel, (panel + 1) * perPanel), step = plotWidth / Math.min(perPanel, entries.length);
    const labelLines = subset.map(entry => entry.text ? wrapReportSvgText(entry.text, step - 8, font) : []);
    const extraLabelHeight = Math.max(1, ...labelLines.map(lines => lines.length)) * (font + 3);
    const reversed = y1 < y0, belowLabels = reversed ? extraLabelHeight + 8 : 0;
    const top = cursor + extraLabelHeight + (panelCount > 1 ? 22 : 8), bottom = top + plotHeight;
    const y = (value: number) => bottom - (value - y0) / (y1 - y0) * plotHeight;
    const bounded = (v: number) => Math.max(top, Math.min(bottom, v));
    const bars = subset.map((entry, index) => {
      const center = left + (index + 0.5) * step, end = y(transform(entry.count)), base = y(baseline);
      const bar = `<rect data-element="${entry.element}" data-value="${entry.count}"${entry.fraction === null ? "" : ` data-fraction="${entry.fraction}"`} x="${center - step * entry.width / 2}" y="${Math.min(bounded(base), bounded(end))}" width="${step * entry.width}" height="${Math.abs(bounded(end) - bounded(base))}" fill="#08756c"><title>${xml(`${entry.element} · ${saved.label}：${entry.count}${entry.fraction === null ? "" : ` · 占显示元素比例：${entry.fraction}`}`)}</title></rect>`;
      const withinRange = transform(entry.count) >= lo && transform(entry.count) <= hi;
      const values = withinRange && labelLines[index].length ? `<text data-value-label="${entry.element}" text-anchor="middle">${labelLines[index].map((text, line) => `<tspan x="${center}" y="${reversed ? end + 8 + font + line * (font + 3) : end - 8 - (labelLines[index].length - 1 - line) * (font + 3)}">${xml(text)}</tspan>`).join("")}</text>` : "";
      return `${bar}${values}<text data-element-label="${entry.element}" x="${center}" y="${bottom + 24 + belowLabels}" text-anchor="middle" font-family="ui-monospace,Consolas,monospace">${entry.element}</text>`;
    }).join("");
    const grid = ticks.map(tick => `<line x1="${left}" x2="${right}" y1="${y(transform(tick.value))}" y2="${y(transform(tick.value))}" stroke="#e7ece9"/><text data-tick-value="${tick.value}" x="${left - 10}" y="${y(transform(tick.value)) + 4}" text-anchor="end">${xml(tick.text)}</text>`).join("");
    panels.push(`<g data-element-panel="${panel}" data-y-range="${y0},${y1}" font-size="${font}">${panelCount > 1 ? `<text x="${left}" y="${cursor + 18}">${panel * perPanel + 1}–${Math.min(entries.length, (panel + 1) * perPanel)} / ${entries.length}</text>` : ""}${grid}${bars}</g>`);
    cursor = bottom + 42 + belowLabels;
  }
  const xTitle = wrapReportSvgText(label(xaxis.title) || "元素", width - 40, font);
  const notes = saved.notes.flatMap(note => wrapReportSvgText(note, width - 40, font));
  const height = cursor + (xTitle.length + notes.length) * 22 + 16;
  return { pointCount: entries.length, fit: "width" as const,
    axes: [{ label: label(xaxis.title) || "元素", range: null, ticks: entries.map(entry => entry.element).join(" · ") },
      { label: scaleLabel, range: (log ? range.map(v => 10 ** v) : range).join(" → "), ticks: ticks.map(tick => tick.text).join(" · ") }],
    svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="title desc"><title id="title">${xml(title)}</title><desc id="desc">${xml(`${scaleLabel}；${entries.length} 个已保存元素。${saved.notes.join(" ")}`)}</desc><rect width="${width}" height="${height}" fill="#fff"/><g font-family="system-ui,sans-serif" fill="#17211e">${titleLines.map((line, i) => `<text data-plot-title="true" x="20" y="${28 + i * 30}" font-size="22" font-weight="600">${xml(line)}</text>`).join("")}${intro.map((line, i) => `<text x="20" y="${20 + titleLines.length * 30 + (i + 1) * 22}" font-size="${font}">${xml(line)}</text>`).join("")}${panels.join("")}${xTitle.map((line, i) => `<text x="${width / 2}" y="${cursor + i * 22}" text-anchor="middle" font-size="${font}">${xml(line)}</text>`).join("")}${notes.map((line, i) => `<text data-plot-note="true" x="20" y="${cursor + (xTitle.length + i + 1) * 22}" font-size="${font}">${xml(line)}</text>`).join("")}</g></svg>`,
  };
}
