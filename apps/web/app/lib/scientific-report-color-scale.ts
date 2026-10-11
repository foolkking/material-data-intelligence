import { densityColor } from "../../scientific-viewers/workspace/saved-density-plot";
import { readPlotColorScale } from "../../scientific-viewers/workspace/workspace-plot-layout";

type Row = Record<string, unknown>;
type Color = [number, number, number, number];
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);

function color(value: unknown): Color | null {
  const hex = densityColor(value === "green" ? "#008000" : value === "yellow" ? "#ffff00" : value);
  if (hex) return [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16)).concat(1) as Color;
  const match = typeof value === "string" && /^rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(0(?:\.\d+)?|1(?:\.0+)?)\s*\)$/u.exec(value);
  return match && match.slice(1, 4).every(v => Number(v) <= 255) ? match.slice(1).map(Number) as Color : null;
}

/** Scientific labels must remain readable over the actual saved color scale. */
export function readablePlotLabelColor(background: string): string {
  const rgba = color(background);
  if (!rgba) return "#17211e";
  const luminance = (channels: number[]) => channels.map(v => {
    const value = v / 255;
    return value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4;
  }).reduce((sum, value, index) => sum + value * [.2126, .7152, .0722][index], 0);
  const backdrop = luminance(rgba.slice(0, 3).map(v => v * rgba[3] + 255 * (1 - rgba[3])));
  const ink = luminance([23, 33, 30]);
  const darkContrast = (Math.max(backdrop, ink) + .05) / (Math.min(backdrop, ink) + .05);
  const lightContrast = 1.05 / (backdrop + .05);
  return darkContrast >= 4.5 && darkContrast >= lightContrast ? "#17211e" : lightContrast >= 4.5 ? "#ffffff" : "#000000";
}

/** Match the saved Plotly color mapping, including clipped, reversed and
 * constant ranges. This projects saved values; it does not count compositions. */
export function savedReportColorScale(source: Row) {
  const validated = readPlotColorScale(source);
  if (!validated || source.autocolorscale === true) return null;
  const trace: Row = { ...validated, z: source.z };
  if (!Array.isArray(trace.colorscale) || !Array.isArray(trace.z)) return null;
  if (trace.zauto === false && (!finite(trace.zmin) || !finite(trace.zmax))) return null;
  const stops: Array<{ at: number; color: Color }> = [];
  for (const stop of trace.colorscale) {
    const rgba = Array.isArray(stop) ? color(stop[1]) : null;
    if (!rgba) return null;
    stops.push({ at: stop[0], color: rgba });
  }
  if (trace.reversescale === true) stops.reverse().forEach(stop => { stop.at = 1 - stop.at; });
  const values = trace.z.flat().filter(finite);
  if (!values.length) return null;
  const auto = trace.zauto === undefined ? !(finite(trace.zmin) && finite(trace.zmax)) : trace.zauto;
  let min = !auto && finite(trace.zmin) ? trace.zmin : Math.min(...values);
  let max = !auto && finite(trace.zmax) ? trace.zmax : Math.max(...values);
  if (auto && finite(trace.zmid)) {
    const half = Math.max(max - trace.zmid, trace.zmid - min);
    min = trace.zmid - half; max = trace.zmid + half;
  }
  if (min === max) { min -= 0.5; max += 0.5; }
  if (!finite(max - min) || max <= min) return null;
  const css = (rgba: Color) => `rgba(${rgba.slice(0, 3).map(Math.round).join(",")},${rgba[3]})`;
  const fill = (value: number) => {
    const t = Math.max(0, Math.min(1, (value - min) / (max - min)));
    const upper = stops.findIndex(stop => stop.at > t);
    if (upper < 0) return css(stops[stops.length - 1].color);
    if (upper === 0) return css(stops[0].color);
    const a = stops[upper - 1], b = stops[upper], amount = (t - a.at) / (b.at - a.at);
    return css(a.color.map((v, i) => v * (1 - amount) + b.color[i] * amount) as Color);
  };
  return { min, max, fill, gradient: stops.map(stop => `<stop offset="${stop.at}" stop-color="${css(stop.color)}"/>`).join("") };
}
