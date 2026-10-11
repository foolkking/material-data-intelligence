import { normalizedPlotFigure } from "../../scientific-viewers/workspace/workspace-plot-contract";
import { readPlotCoordinates, readPlotNumericMatrix } from "../../scientific-viewers/workspace/workspace-plot-data";
import { savedReportColorScale } from "./scientific-report-color-scale";
import { reportSvgTextWidth, wrapReportSvgText } from "./scientific-report-svg-text";

type Row = Record<string, unknown>;
const record = (v: unknown): Row => v && typeof v === "object" && !Array.isArray(v) ? v as Row : {};
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const xml = (v: string) => v.replace(/[&<>"']/gu, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);
const label = (v: unknown) => typeof v === "string" ? v : typeof record(v).text === "string" ? String(record(v).text) : "";
const short = (v: number) => Number(v.toPrecision(5)).toString();
const has = (row: Row, keys: string[]) => keys.some(key => row[key] !== undefined);

/** Cell boundaries follow Plotly's centers/edges convention. Categories keep
 * their saved order; numeric positions are never replaced by equal-width bins. */
function readAxis(raw: unknown, count: number, axis: Row, start: unknown, step: unknown) {
  if (axis.type !== undefined && !["-", "linear", "category"].includes(String(axis.type))
    || has(axis, ["overlaying", "matches", "scaleanchor", "rangebreaks", "tickvals", "ticktext", "tickformat", "tickprefix", "ticksuffix"])
    || axis.domain !== undefined && JSON.stringify(axis.domain) !== "[0,1]"
    || axis.autorange !== undefined && ![true, false, "reversed"].includes(axis.autorange as boolean)
    || start !== undefined && !finite(start) || step !== undefined && (!finite(step) || step === 0)) return null;
  const values = raw === undefined
    ? Array.from({ length: count }, (_, i) => Number(start ?? 0) + i * Number(step ?? 1))
    : readPlotCoordinates(raw);
  if (!values?.length || values.some(v => v === null) || ![count, count + 1].includes(values.length)) return null;
  // Numeric-looking strings have Plotly autotype rules; do not assume their
  // scientific coordinates are equally spaced categories without a saved type.
  if ((axis.type === undefined || axis.type === "-") && values.some(v => typeof v === "string" && v.trim() !== "" && Number.isFinite(Number(v)))) return null;
  const categorical = axis.type === "category" || values.every(v => typeof v === "string");
  if (categorical && axis.type === "linear") return null;
  let edges: number[], positions: number[], labels: string[], names: string[] | null = null;
  if (categorical) {
    if (values.length !== count || new Set(values.map(String)).size !== count) return null;
    names = values.map(String);
    if (names.some(name => !name || name.length > 512)) return null;
    const order = axis.categoryorder ?? "trace";
    if (!["trace", "array", "category ascending", "category descending"].includes(String(order))) return null;
    if (order === "array") {
      if (!Array.isArray(axis.categoryarray) || axis.categoryarray.some(v => typeof v !== "string")
        || new Set(axis.categoryarray).size !== axis.categoryarray.length) return null;
      const orderNames = axis.categoryarray as string[];
      names = [...orderNames, ...names.filter(name => !orderNames.includes(name))];
    } else if (order !== "trace") {
      names = [...names].sort();
      if (order === "category descending") names.reverse();
    }
    if (names.length > 512 || names.some(name => !name || name.length > 512)) return null;
    positions = values.map(v => names!.indexOf(String(v)));
    edges = Array.from({ length: names.length + 1 }, (_, i) => i - 0.5);
    labels = values.map(String);
  } else {
    if (!values.every(finite) || axis.type === "category" || has(axis, ["categoryorder", "categoryarray"])) return null;
    const numbers = values as number[];
    if (numbers.length > 1) {
      const direction = Math.sign(numbers[1] - numbers[0]);
      if (!direction || numbers.some((v, i) => i > 0 && Math.sign(v - numbers[i - 1]) !== direction)) return null;
    }
    if (numbers.length === count + 1) {
      edges = numbers;
      positions = numbers.slice(0, -1).map((v, i) => v / 2 + numbers[i + 1] / 2);
      labels = numbers.slice(0, -1).map((v, i) => `[${v}, ${numbers[i + 1]}]`);
    } else {
      positions = numbers; labels = numbers.map(String);
      edges = count === 1 ? [numbers[0] - 0.5, numbers[0] + 0.5]
        : [numbers[0] - (numbers[1] - numbers[0]) / 2,
          ...numbers.slice(1).map((v, i) => v / 2 + numbers[i] / 2),
          numbers[count - 1] + (numbers[count - 1] - numbers[count - 2]) / 2];
    }
  }
  if (edges.some(v => !finite(v))) return null;
  let range = [Math.min(...edges), Math.max(...edges)];
  if (axis.range !== undefined && (axis.autorange === false || axis.autorange === undefined)) {
    if (!Array.isArray(axis.range) || axis.range.length !== 2 || !axis.range.every(finite)) return null;
    range = [...axis.range];
  } else if (axis.autorange === "reversed") range.reverse();
  if (!finite(range[1] - range[0]) || range[0] === range[1]) return null;
  const bounds = positions.map((p, i) => names ? [p - 0.5, p + 0.5] : [edges[i], edges[i + 1]]);
  return { range, bounds, positions, labels, names, title: label(axis.title), visible: axis.visible !== false };
}

/** One saved Cartesian heatmap, rendered without running plotting scripts. */
export function renderReportHeatmap(payload: unknown, title: string, options?: { width?: number; compact?: boolean }) {
  const figure = normalizedPlotFigure(payload), data = figure?.data;
  if (!Array.isArray(data) || data.length !== 1) return null;
  const rawTrace = record(data[0]), rawLayout = record(figure?.layout), template = record(rawLayout.template);
  if (rawTrace.type !== "heatmap") return null;
  if (typeof rawLayout.template === "string") return null;
  const templateLayout = record(template.layout), templates = record(template.data).heatmap;
  const traceDefaults = Array.isArray(templates) ? record(templates[0]) : {};
  const trace: Row = { ...traceDefaults, ...rawTrace, colorbar: { ...record(traceDefaults.colorbar), ...record(rawTrace.colorbar) } };
  const layout: Row = { ...templateLayout, ...rawLayout };
  for (const key of ["xaxis", "yaxis", ...(typeof trace.coloraxis === "string" ? [trace.coloraxis] : [])]) {
    layout[key] = { ...record(templateLayout[key]), ...record(rawLayout[key]) };
  }
  if (trace.type !== "heatmap" || has(layout, ["annotations", "shapes", "images", "grid"])
    || trace.xaxis !== undefined && trace.xaxis !== "x" || trace.yaxis !== undefined && trace.yaxis !== "y"
    || trace.visible !== undefined && trace.visible !== true || trace.opacity !== undefined && trace.opacity !== 1
    || trace.zsmooth !== undefined && trace.zsmooth !== false || trace.connectgaps === true
    || has(trace, ["transforms", "texttemplate", "xperiod", "yperiod"])
    || trace.transpose !== undefined && typeof trace.transpose !== "boolean") return null;
  const matrix = readPlotNumericMatrix(trace.z);
  if (!matrix?.length || !matrix[0]?.length || matrix.some(row => row.length !== matrix[0].length)
    || matrix.length * matrix[0].length > 50_000 || Math.max(matrix.length, matrix[0].length) > 512) return null;
  const rows = trace.transpose ? matrix[0].length : matrix.length, columns = trace.transpose ? matrix.length : matrix[0].length;
  const x = readAxis(trace.x, columns, record(layout.xaxis), trace.x0, trace.dx);
  const y = readAxis(trace.y, rows, record(layout.yaxis), trace.y0, trace.dy);
  if (!x || !y) return null;
  const linked = typeof trace.coloraxis === "string" ? record(layout[trace.coloraxis]) : null;
  if (trace.coloraxis !== undefined && (!linked || !/^coloraxis\d*$/u.test(String(trace.coloraxis)))) return null;
  const scaleSource: Row = linked ? { ...linked, zmin: linked.cmin, zmax: linked.cmax, zmid: linked.cmid, zauto: linked.cauto, z: matrix } : { ...trace, z: matrix };
  const scale = savedReportColorScale(scaleSource);
  if (!scale) return null;
  const bar = record(scaleSource.colorbar);
  if (has(bar, ["tickformat", "tickprefix", "ticksuffix", "labelalias"])) return null;
  const gapX = trace.xgap ?? 0, gapY = trace.ygap ?? 0;
  if (!finite(gapX) || !finite(gapY) || gapX < 0 || gapY < 0) return null;
  const width = finite(options?.width) ? Math.max(360, Math.min(1200, options.width)) : 920;
  const compact = options?.compact ?? false, font = width < 600 ? 14 : 16;
  const titleLines = wrapReportSvgText(compact ? "" : title, width - 48, 24);
  const headingBottom = titleLines.length ? 28 + titleLines.length * 32 : 16;
  let indexX = !!x.names && (x.names.length > 12 || x.names.some(name => reportSvgTextWidth(name, font) > (width - 120) / x.names!.length - 8));
  let indexY = !!y.names && y.names.some(name => reportSvgTextWidth(name, font) > width * 0.24);
  const sameNames = x.names && y.names && JSON.stringify(x.names) === JSON.stringify(y.names);
  if (sameNames && (indexX || indexY)) indexX = indexY = true;
  const maxY = y.names ? indexY ? 28 : Math.max(...y.names.map(name => reportSvgTextWidth(name, font)))
    : Math.max(...Array.from({ length: 5 }, (_, i) => reportSvgTextWidth(short(y.range[0] + (y.range[1] - y.range[0]) * i / 4), font)));
  const left = Math.max(48, maxY + 16), plotWidth = width - left - 24;
  if (plotWidth < 120) return null;
  const yTitleLines = wrapReportSvgText(y.title, plotWidth, font);
  const top = headingBottom + (yTitleLines.length ? yTitleLines.length * (font + 6) + 8 : 0);
  const plotHeight = Math.max(200, Math.min(560, plotWidth * rows / columns)), bottom = top + plotHeight;
  const sx = (v: number) => left + (v - x.range[0]) / (x.range[1] - x.range[0]) * plotWidth;
  const sy = (v: number) => bottom - (v - y.range[0]) / (y.range[1] - y.range[0]) * plotHeight;
  const cells: string[] = [];
  let pointCount = 0;
  for (let row = 0; row < rows; row++) for (let column = 0; column < columns; column++) {
    const value = trace.transpose ? matrix[column][row] : matrix[row][column];
    const [x0, x1] = x.bounds[column].map(sx), [y0, y1] = y.bounds[row].map(sy);
    const w = Math.abs(x1 - x0) - gapX, h = Math.abs(y1 - y0) - gapY;
    if (w <= 0 || h <= 0) return null;
    if (value !== null) pointCount++;
    cells.push(`<rect data-cell="${row}:${column}" data-value="${value ?? ""}" x="${Math.min(x0, x1) + gapX / 2}" y="${Math.min(y0, y1) + gapY / 2}" width="${w}" height="${h}" fill="${value === null ? "url(#missing-cell)" : scale.fill(value)}"><title>${xml(`${x.labels[column]} · ${y.labels[row]}：${value ?? "缺失"}`)}</title></rect>`);
  }
  const axisTicks = (axis: typeof x, isX: boolean, indexed: boolean) => {
    const extent = isX ? plotWidth : plotHeight;
    const ticks = axis.names ? axis.names.map((name, i) => ({ at: i, text: indexed ? String(i + 1) : name }))
      : Array.from({ length: 5 }, (_, i) => { const at = axis.range[0] + (axis.range[1] - axis.range[0]) * i / 4; return { at, text: short(at) }; });
    let edge = -Infinity;
    return ticks.map(tick => ({ ...tick, pixel: isX ? sx(tick.at) : sy(tick.at) }))
      .filter(tick => tick.pixel >= (isX ? left : top) && tick.pixel <= (isX ? left + plotWidth : bottom))
      .sort((a, b) => a.pixel - b.pixel).flatMap(tick => {
        const size = isX ? reportSvgTextWidth(tick.text, font) : font;
        if (tick.pixel - size / 2 < edge || size > extent) return [];
        edge = tick.pixel + size / 2 + 8;
        const textX = isX ? Math.max(12 + size / 2, Math.min(width - 12 - size / 2, tick.pixel)) : left - 10;
        return [`<text data-axis="${isX ? "x" : "y"}" data-coordinate="${tick.at}" x="${textX}" y="${isX ? bottom + 24 : tick.pixel + font * 0.35}" text-anchor="${isX ? "middle" : "end"}" font-size="${font}">${xml(tick.text)}</text>`];
      }).join("");
  };
  const headings: string[] = [];
  const xTitleLines = wrapReportSvgText(x.title, plotWidth, font);
  xTitleLines.forEach((line, i) => headings.push(`<text data-axis-title="x" x="${left + plotWidth / 2}" y="${bottom + 50 + i * (font + 6)}" text-anchor="middle" font-size="${font}">${xml(line)}</text>`));
  yTitleLines.forEach((line, i) => headings.push(`<text data-axis-title="y" x="${left}" y="${headingBottom + font + i * (font + 6)}" font-size="${font}">${xml(line)}</text>`));
  let cursor = bottom + 58 + xTitleLines.length * (font + 6);
  const extra: string[] = [];
  if (scaleSource.showscale !== false) {
    const barTitle = label(bar.title), barX = left, barWidth = plotWidth;
    const caption = wrapReportSvgText(barTitle, barWidth, font);
    for (const line of caption) { extra.push(`<text x="${barX + barWidth / 2}" y="${cursor}" text-anchor="middle" font-size="${font}">${xml(line)}</text>`); cursor += font + 6; }
    let ticks = [scale.min, (scale.min + scale.max) / 2, scale.max].map(value => ({ value, text: short(value) }));
    if (bar.tickvals !== undefined || bar.ticktext !== undefined) {
      if (!Array.isArray(bar.tickvals) || !bar.tickvals.every(finite) || bar.ticktext !== undefined && (!Array.isArray(bar.ticktext) || bar.ticktext.length !== bar.tickvals.length)) return null;
      ticks = bar.tickvals.map((value, i) => ({ value, text: Array.isArray(bar.ticktext) ? String(bar.ticktext[i]) : short(value) }));
    }
    extra.push(`<rect data-colorbar="true" data-min="${scale.min}" data-max="${scale.max}" x="${barX}" y="${cursor}" width="${barWidth}" height="12" fill="url(#heatmap-scale)"/>`);
    let edge = -Infinity;
    for (const tick of ticks.filter(t => t.value >= scale.min && t.value <= scale.max).sort((a, b) => a.value - b.value)) {
      const pixel = barX + (tick.value - scale.min) / (scale.max - scale.min) * barWidth, half = reportSvgTextWidth(tick.text, font) / 2;
      if (pixel - half < edge) continue;
      const textX = Math.max(12 + half, Math.min(width - 12 - half, pixel));
      extra.push(`<text data-color-tick="${tick.value}" x="${textX}" y="${cursor + 30}" text-anchor="middle" font-size="${font}">${xml(tick.text)}</text>`); edge = textX + half + 8;
    }
    cursor += 56;
  }
  const keys = (names: string[], prefix: string) => {
    for (let i = 0; i < names.length; i += 2) {
      const keyWidth = (width - 64) / 2;
      const lines = names.slice(i, i + 2).map((name, part) => wrapReportSvgText(`${prefix}${i + part + 1} · ${name}`, keyWidth, font));
      lines.forEach((lines, part) => extra.push(`<text data-axis-key="${xml(prefix + (i + part + 1))}" x="${24 + part * (keyWidth + 16)}" y="${cursor}" font-size="${font}">${lines.map((line, j) => `<tspan x="${24 + part * (keyWidth + 16)}" dy="${j ? font + 6 : 0}">${xml(line)}</tspan>`).join("")}</text>`));
      cursor += Math.max(...lines.map(lines => lines.length)) * (font + 6) + 8;
    }
  };
  if (sameNames && indexX && indexY) keys(x.names!, "");
  else { if (indexX) keys(x.names!, "X "); if (indexY) keys(y.names!, "Y "); }
  const missing = rows * columns - pointCount;
  if (missing) { extra.push(`<text x="24" y="${cursor}" font-size="${font}">斜线格：缺失值（${missing}）</text>`); cursor += font + 16; }
  const height = cursor + 16;
  return {
    pointCount, fit: "width" as const, axes: [x, y].map((axis, i) => ({ label: axis.title || (i ? "Y" : "X"), range: axis.names ? null : axis.range.join(" → "), ticks: axis.names?.join(" · ") ?? null })),
    svg: `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" style="display:block;width:100%;height:auto" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="title desc"><title id="title">${xml(title)}</title><desc id="desc">${rows} 行 × ${columns} 列；${pointCount} 个保存数值，${missing} 个缺失值。每个单元格保留原始坐标和值。</desc><rect width="${width}" height="${height}" fill="#ffffff"/><defs><linearGradient id="heatmap-scale">${scale.gradient}</linearGradient><pattern id="missing-cell" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#f3f5f4"/><path d="M-2 2L2-2M0 8L8 0M6 10L10 6" stroke="#899790"/></pattern><clipPath id="heatmap-clip"><rect x="${left}" y="${top}" width="${plotWidth}" height="${plotHeight}"/></clipPath></defs><g font-family="system-ui,sans-serif" fill="#17211e">${titleLines.map((line, i) => `<text data-plot-title="true" x="24" y="${32 + i * 32}" font-size="24" font-weight="600">${xml(line)}</text>`).join("")}<g clip-path="url(#heatmap-clip)">${cells.join("")}</g>${x.visible ? axisTicks(x, true, indexX) : ""}${y.visible ? axisTicks(y, false, indexY) : ""}${headings.join("")}${extra.join("")}</g></svg>`,
  };
}
