import { normalizedPlotFigure } from "./workspace-plot-contract";

type RecordValue = Record<string, unknown>;
const record = (v: unknown): RecordValue => v && typeof v === "object" && !Array.isArray(v) ? v as RecordValue : {};
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const only = (v: RecordValue, keys: string[]) => Object.keys(v).every(key => keys.includes(key));

// The saved producer uses Plotly's stock presentation template. Template
// defaults that add scientific content must not be discarded on this path.
function presentationTemplate(value: unknown, traceType: string): boolean {
  if (value === undefined) return true;
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const template = record(value), layout = record(template.layout);
  if (!only(template, ["layout", "data"]) || !only(layout, ["autotypenumbers", "colorway", "font", "hovermode", "hoverlabel",
    "paper_bgcolor", "plot_bgcolor", "polar", "ternary", "coloraxis", "colorscale", "xaxis", "yaxis", "scene",
    "shapedefaults", "annotationdefaults", "geo", "title", "mapbox"])) return false;
  for (const axis of [record(layout.xaxis), record(layout.yaxis)]) {
    if (!only(axis, ["gridcolor", "linecolor", "ticks", "title", "zerolinecolor", "automargin", "zerolinewidth"])
      || !only(record(axis.title), ["standoff", "font"])) return false;
  }
  if (!only(record(layout.title), ["x", "y", "xanchor", "yanchor", "font"])) return false;
  const colorbarStyle = (bar: unknown) => only(record(bar), ["outlinewidth", "ticks"]);
  if (!only(record(layout.coloraxis), ["colorbar"]) || !colorbarStyle(record(layout.coloraxis).colorbar)) return false;
  const defaults = record(template.data)[traceType];
  return defaults === undefined || (Array.isArray(defaults) && defaults.length === 1 && defaults.every(value => {
    const trace = record(value);
    return only(trace, ["type", "marker"]) && only(record(trace.marker), ["colorbar"]) && colorbarStyle(record(trace.marker).colorbar);
  }));
}

export type SavedDensityPlot = {
  x: number[]; y: number[]; density: number[];
  solidColor?: string;
  xLabel: string; yLabel: string; title: string; densityLabel: string;
  xRange?: [number, number]; yRange?: [number, number];
  colors: Array<[number, string]>; colorRange: [number, number];
  markerSize: number; opacity: number;
  lines: Array<{ x0: number; x1: number; y0: number; y1: number; color: string; width: number; dash: string; below: boolean }>;
  annotations: string[];
};

/** Decode saved values only. Shape/size guards prevent a matrix being treated as a vector. */
export function savedNumericVector(value: unknown, maximum = 50_000): number[] | null {
  if (Array.isArray(value)) return value.length > 0 && value.length <= maximum && value.every(finite) ? [...value] : null;
  const encoded = record(value), match = /^([<>=|]?)([fiu])([1248])$/u.exec(String(encoded.dtype || ""));
  if (!match || !only(encoded, ["dtype", "bdata", "shape"]) || typeof encoded.bdata !== "string"
    || encoded.bdata.length > Math.ceil(maximum * Number(match[3]) / 3) * 4
    || !/^[A-Za-z0-9+/]*={0,2}$/u.test(encoded.bdata)) return null;
  const kind = match[2], size = Number(match[3]);
  if (kind === "f" ? ![4, 8].includes(size) : ![1, 2, 4].includes(size)) return null;
  try {
    const raw = atob(encoded.bdata), count = raw.length / size;
    if (!Number.isInteger(count) || count < 1 || count > maximum
      || (encoded.shape !== undefined && String(encoded.shape).trim() !== String(count))) return null;
    const bytes = Uint8Array.from(raw, char => char.charCodeAt(0)), view = new DataView(bytes.buffer), little = match[1] !== ">";
    const result: number[] = [];
    for (let i = 0; i < raw.length; i += size) {
      const v = kind === "f" ? size === 4 ? view.getFloat32(i, little) : view.getFloat64(i, little)
        : kind === "i" ? size === 1 ? view.getInt8(i) : size === 2 ? view.getInt16(i, little) : view.getInt32(i, little)
          : size === 1 ? view.getUint8(i) : size === 2 ? view.getUint16(i, little) : view.getUint32(i, little);
      if (!finite(v)) return null;
      result.push(v);
    }
    return result;
  } catch { return null; }
}

export function plotText(value: unknown): string | null {
  const text = typeof value === "string" ? value : record(value).text;
  if (text === undefined) return "";
  if (typeof text !== "string" || text.length > 500) return null;
  const plain = text.replace(/<br\s*\/?\s*>/giu, "\n").replace(/<sup>2<\/sup>/gu, "²")
    .replace(/<sup>([\w+−-]+)<\/sup>/giu, "^($1)").replace(/<sub>([\w+−-]+)<\/sub>/giu, "_($1)");
  if (/[<>]/u.test(plain)) return null;
  return plain.trim().replace(/^LS fit:/u, "最小二乘拟合：");
}

const namedColors: Record<string, string> = { gray: "#808080", grey: "#808080", navy: "#000080", black: "#000000", red: "#ff0000", blue: "#0000ff", white: "#ffffff" };
export function densityColor(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const color = value.trim().toLowerCase();
  if (namedColors[color]) return namedColors[color];
  if (/^#[0-9a-f]{6}$/u.test(color)) return color;
  if (/^#[0-9a-f]{3}$/u.test(color)) return `#${[...color.slice(1)].map(c => c + c).join("")}`;
  const rgb = /^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$/u.exec(color);
  if (!rgb || rgb.slice(1).some(c => Number(c) > 255)) return null;
  return `#${rgb.slice(1).map(c => Number(c).toString(16).padStart(2, "0")).join("")}`;
}

export function isSavedDensityPlot(payload: unknown): boolean {
  const figure = normalizedPlotFigure(payload);
  return Boolean(figure && (String(record(record(figure.layout).meta).schemaVersion).startsWith("mdi.raw-parity-scatter/")
    || (Array.isArray(figure.data) && figure.data.some(value => record(record(value).marker).coloraxis !== undefined))));
}

/** A deliberately bounded subset of saved Plotly density scatter semantics. */
export function readSavedDensityPlot(payload: unknown): SavedDensityPlot | null {
  const figure = normalizedPlotFigure(payload);
  if (!figure || !Array.isArray(figure.data) || figure.data.length !== 1) return null;
  const trace = record(figure.data[0]), marker = record(trace.marker), layout = record(figure.layout);
  const raw = record(layout.meta).schemaVersion === "mdi.raw-parity-scatter/1.0";
  const solidColor = raw ? densityColor(marker.color) : null;
  if (raw ? !solidColor || !only(record(layout.meta), ["schemaVersion"]) || layout.coloraxis !== undefined || marker.coloraxis !== undefined : layout.meta !== undefined) return null;
  if (!["scatter", "scattergl"].includes(String(trace.type)) || trace.mode !== "markers"
    || !presentationTemplate(layout.template, String(trace.type))
    || (trace.xaxis !== undefined && trace.xaxis !== "x") || (trace.yaxis !== undefined && trace.yaxis !== "y")
    || !only(trace, ["type", "mode", "name", "x", "y", "xaxis", "yaxis", "marker", "customdata", "hovertemplate", "legendgroup", "showlegend"])
    || (!raw && marker.coloraxis !== "coloraxis") || (marker.symbol !== undefined && marker.symbol !== "circle")
    || !only(marker, ["color", "coloraxis", "symbol", "size", "opacity"])
    || !only(layout, ["template", "xaxis", "yaxis", "coloraxis", "legend", "margin", "shapes", "annotations", "title", "width", "height", "showlegend", "meta"])) return null;
  const x = savedNumericVector(trace.x), y = savedNumericVector(trace.y), density = raw ? [] : savedNumericVector(marker.color);
  if (!x || !y || !density || x.length !== y.length || (!raw && x.length !== density.length)) return null;
  const axes = [record(layout.xaxis), record(layout.yaxis)];
  for (const [i, axis] of axes.entries()) {
    if (!only(axis, ["title", "anchor", "domain", "type", "range", "autorange"])
      || (axis.type !== undefined && axis.type !== "linear")
      || (axis.anchor !== undefined && axis.anchor !== (i ? "x" : "y"))
      || (axis.domain !== undefined && JSON.stringify(axis.domain) !== "[0,1]")
      || (axis.autorange !== undefined && ![true, false].includes(axis.autorange as boolean))
      || (axis.range !== undefined && axis.autorange === true)
      || (axis.range !== undefined && (!Array.isArray(axis.range) || axis.range.length !== 2 || !axis.range.every(finite) || axis.range[0] === axis.range[1]))) return null;
  }
  const coloraxis = record(layout.coloraxis), colors: Array<[number, string]> = [];
  let colorRange: [number, number] = [0, 0];
  if (!raw) {
  if (!only(coloraxis, ["colorscale", "colorbar", "autocolorscale", "cmin", "cmax", "cauto", "reversescale", "showscale"])
    || coloraxis.autocolorscale === true || coloraxis.showscale === false
    || !Array.isArray(coloraxis.colorscale) || coloraxis.colorscale.length < 2 || coloraxis.colorscale.length > 32) return null;
  for (const stop of coloraxis.colorscale) {
    if (!Array.isArray(stop) || stop.length !== 2 || !finite(stop[0]) || stop[0] < 0 || stop[0] > 1) return null;
    const color = densityColor(stop[1]);
    if (!color || (colors.length && stop[0] <= colors[colors.length - 1][0])) return null;
    colors.push([stop[0], color]);
  }
  if (colors[0][0] !== 0 || colors[colors.length - 1][0] !== 1) return null;
  if (coloraxis.reversescale === true) colors.reverse().forEach(stop => { stop[0] = 1 - stop[0]; });
  const hasRange = coloraxis.cmin !== undefined || coloraxis.cmax !== undefined;
  if (hasRange && (!finite(coloraxis.cmin) || !finite(coloraxis.cmax) || coloraxis.cmin >= coloraxis.cmax || coloraxis.cauto === true)) return null;
  colorRange = hasRange ? [Number(coloraxis.cmin), Number(coloraxis.cmax)] : [Math.min(...density), Math.max(...density)];
  if (!finite(colorRange[1] - colorRange[0])) return null;
  }
  const markerSize = marker.size ?? 6, opacity = marker.opacity ?? 1;
  if (!finite(markerSize) || markerSize <= 0 || markerSize > 32 || !finite(opacity) || opacity < 0 || opacity > 1) return null;
  const lines: SavedDensityPlot["lines"] = [], annotations: string[] = [];
  if (layout.shapes !== undefined && (!Array.isArray(layout.shapes) || layout.shapes.length > 8)) return null;
  for (const value of (layout.shapes as unknown[] || [])) {
    const shape = record(value), line = record(shape.line), color = densityColor(line.color ?? "gray"), width = line.width ?? 1, dash = line.dash ?? "solid";
    if (!only(shape, ["type", "x0", "x1", "y0", "y1", "xref", "yref", "line", "layer"])
      || !only(line, ["color", "width", "dash"]) || shape.type !== "line"
      || (shape.xref !== undefined && shape.xref !== "x") || (shape.yref !== undefined && shape.yref !== "y")
      || ![shape.x0, shape.x1, shape.y0, shape.y1].every(finite) || !color || !finite(width) || width <= 0 || width > 8
      || !["solid", "dash", "dot", "dashdot"].includes(String(dash))
      || (shape.layer !== undefined && !["above", "below"].includes(String(shape.layer)))) return null;
    lines.push({ x0: Number(shape.x0), x1: Number(shape.x1), y0: Number(shape.y0), y1: Number(shape.y1), color, width, dash: String(dash), below: shape.layer === "below" });
  }
  if (layout.annotations !== undefined && (!Array.isArray(layout.annotations) || layout.annotations.length > 8)) return null;
  for (const value of (layout.annotations as unknown[] || [])) {
    const a = record(value), text = plotText(a.text);
    if (!only(a, ["text", "x", "y", "xref", "yref", "xanchor", "yanchor", "align", "font", "showarrow"])
      || a.showarrow !== false || a.xref !== "paper" || a.yref !== "paper" || !finite(a.x) || !finite(a.y)
      || a.x < 0 || a.x > 1 || a.y < 0 || a.y > 1 || text === null) return null;
    if (text) annotations.push(text);
  }
  const xLabel = plotText(axes[0].title), yLabel = plotText(axes[1].title), title = plotText(layout.title), colorLabel = plotText(record(coloraxis.colorbar).title);
  if ([xLabel, yLabel, title, colorLabel].some(value => value === null)) return null;
  return { x, y, density, colors, colorRange, markerSize, opacity, lines, annotations, ...(solidColor ? { solidColor } : {}),
    xRange: axes[0].range as [number, number] | undefined, yRange: axes[1].range as [number, number] | undefined,
    xLabel: xLabel === "y_true" ? "真实值" : xLabel!, yLabel: yLabel === "y_pred" ? "预测值" : yLabel!,
    title: title === "Prediction Density Scatter" ? "真实值与预测值" : title!, densityLabel: colorLabel?.replace(/\s/gu, "") === "PointDensity" ? "点密度" : colorLabel || "颜色数值" };
}

/** Graphical color interpolation; no density/fit/statistics are recomputed. */
export function densityPointColor(plot: SavedDensityPlot, value: number): string {
  const [min, max] = plot.colorRange, t = max === min ? 0.5 : Math.min(1, Math.max(0, (value - min) / (max - min)));
  const index = Math.max(1, plot.colors.findIndex(stop => stop[0] >= t));
  const [a, b] = [plot.colors[index - 1], plot.colors[index]], amount = (t - a[0]) / (b[0] - a[0]);
  const rgb = [1, 3, 5].map(offset => Math.round(parseInt(a[1].slice(offset, offset + 2), 16) * (1 - amount) + parseInt(b[1].slice(offset, offset + 2), 16) * amount));
  return `#${rgb.map(v => v.toString(16).padStart(2, "0")).join("")}`;
}
