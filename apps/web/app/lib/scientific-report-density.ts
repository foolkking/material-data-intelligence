import { densityPointColor, readSavedDensityPlot } from "../../scientific-viewers/workspace/saved-density-plot";
import { wrapReportSvgText as wrap } from "./scientific-report-svg-text";
import { isSavedScatter, readSavedScatter } from "../../scientific-viewers/workspace/saved-scatter";

const xml = (value: string) => value.replace(/[&<>"']/gu, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);
const dashes: Record<string, string> = { dash: "6 4", dot: "2 3", dashdot: "6 3 2 3", solid: "" };
const dash = (value: string) => dashes[value];

/** An inert presentation of saved point colors, line endpoints and annotations. */
export function renderReportDensity(payload: unknown, title: string, options?: { width?: number; compact?: boolean }) {
  const scatter = isSavedScatter(payload) ? readSavedScatter(payload) : null;
  if (isSavedScatter(payload) && !scatter) return null;
  const plot = readSavedDensityPlot(payload);
  if (!plot) return null;
  const width = Math.max(360, Math.min(1200, options?.width || 920));
  const compact = options?.compact ?? false;
  const short = (v: number) => {
    const rounded = Number(v.toPrecision(5)), magnitude = Math.abs(rounded);
    return magnitude >= 1e6 || (magnitude > 0 && magnitude < 1e-4) ? rounded.toExponential() : rounded.toString();
  };
  const domain = (values: number[], range?: [number, number]): [number, number] => {
    if (range) return range;
    const min = Math.min(...values), max = Math.max(...values);
    const padding = Math.max(1, Math.abs(min) * 0.05);
    if (min === max) return [min - padding, max + padding];
    const pointPadding = plot.solidColor || scatter ? (max - min) * 0.05 : 0;
    return [min - pointPadding, max + pointPadding];
  };
  const [x0, x1] = domain([...plot.x, ...plot.lines.flatMap(line => [line.x0, line.x1])], plot.xRange);
  const [y0, y1] = domain([...plot.y, ...plot.lines.flatMap(line => [line.y0, line.y1])], plot.yRange);
  if (![x1 - x0, y1 - y0].every(v => Number.isFinite(v) && v !== 0)) return null;
  const ticks = (a: number, b: number, n: number) => Array.from({ length: n }, (_, i) => a + (b - a) * i / (n - 1));
  const yticks = ticks(y0, y1, 5), left = Math.max(86, ...yticks.map(v => short(v).length * 10 + 42)), right = width - 24;
  if (right - left < 120) return null;
  // A distinct saved plot title can name the fitted model or subset; keep it
  // even when the enclosing report already supplies a broader figure caption.
  const titleLines = compact && (!plot.title || plot.title === title) ? [] : wrap(plot.title || title, width - left - 24, 24);
  const top = titleLines.length ? 44 + titleLines.length * 32 : 24, bottom = top + 300, plotWidth = right - left;
  const x = (v: number) => left + (v - x0) / (x1 - x0) * plotWidth;
  const y = (v: number) => bottom - (v - y0) / (y1 - y0) * 300;
  const xTicks = ticks(x0, x1, width < 600 ? 3 : 6).map(v => `<text x="${x(v)}" y="${bottom + 28}" text-anchor="${x(v) === right ? "end" : "middle"}">${xml(short(v))}</text>`).join("");
  const yTicks = yticks.map(v => `<line x1="${left}" x2="${right}" y1="${y(v)}" y2="${y(v)}" stroke="#e7ece9"/><text x="${left - 12}" y="${y(v) + 5}" text-anchor="end">${xml(short(v))}</text>`).join("");
  const lineSvg = (below: boolean) => plot.lines.map((line, i) => line.below !== below ? "" : `<line data-saved-line="${i}" data-x0="${line.x0}" data-x1="${line.x1}" data-y0="${line.y0}" data-y1="${line.y1}" x1="${x(line.x0)}" x2="${x(line.x1)}" y1="${y(line.y0)}" y2="${y(line.y1)}" stroke="${line.color}" stroke-width="${line.width}"${dash(line.dash) ? ` stroke-dasharray="${dash(line.dash)}"` : ""}><title>${xml(`已保存参考线 ${i + 1}：(${line.x0}, ${line.y0}) — (${line.x1}, ${line.y1})`)}</title></line>`).join("");
  // Keep source keys and exact color values; compact only the display markup.
  const pointMarkup = plot.x.map((vx, i) => scatter
    ? `<circle data-source-row="${scatter.traces[0].rows[i][0]}" data-density="${plot.density[i]}" cx="${Number(x(vx).toFixed(3))}" cy="${Number(y(plot.y[i]).toFixed(3))}" r="${plot.markerSize / 2}" fill="${densityPointColor(plot, plot.density[i])}"/>`
    : `<circle data-point="${i}"${plot.solidColor ? "" : ` data-density="${plot.density[i]}"`} cx="${x(vx)}" cy="${y(plot.y[i])}" r="${plot.markerSize / 2}" fill="${plot.solidColor || densityPointColor(plot, plot.density[i])}" opacity="${plot.opacity}"><title>${xml(`${plot.xLabel}: ${vx}; ${plot.yLabel}: ${plot.y[i]}${plot.solidColor ? "" : `; ${plot.densityLabel}: ${plot.density[i]}`}`)}</title></circle>`).join("");
  const points = scatter ? `<g fill-opacity="${plot.opacity}">${pointMarkup}</g>` : pointMarkup;
  const colorTop = bottom + (plot.solidColor ? 20 : 116), notes = [...plot.annotations, ...(scatter?.notes ?? [])].flatMap(note => wrap(note, width - 48));
  const height = colorTop + 76 + notes.length * 24 + (compact ? 0 : 32);
  const gradient = plot.colors.map(([value, color]) => `<stop offset="${value}" stop-color="${color}"/>`).join("");
  const constant = plot.colorRange[0] === plot.colorRange[1];
  const colorBar = plot.solidColor ? "" : `<text x="${left}" y="${colorTop - 12}">${xml(plot.densityLabel)}</text><rect data-colorbar="true" x="${left}" y="${colorTop}" width="${plotWidth}" height="12" fill="${constant ? densityPointColor(plot, plot.colorRange[0]) : "url(#density-scale)"}"/><text x="${left}" y="${colorTop + 36}">${xml(short(plot.colorRange[0]))}</text>${constant ? "" : `<text x="${right}" y="${colorTop + 36}" text-anchor="end">${xml(short(plot.colorRange[1]))}</text>`}`;
  return {
    pointCount: plot.x.length,
    axes: [{ label: plot.xLabel, range: plot.xRange?.join(" 至 ") ?? null, ticks: null }, { label: plot.yLabel, range: plot.yRange?.join(" 至 ") ?? null, ticks: null }],
    svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="title desc"><title id="title">${xml(title)}</title><desc id="desc">完整 ${plot.x.length} 个已保存数据点${plot.solidColor ? "" : scatter ? "及已保存的颜色数值" : "及密度颜色"}，${plot.lines.length} 条已保存参考线；未重新拟合或计算密度。</desc><rect width="${width}" height="${height}" fill="#ffffff"/><defs><clipPath id="density-plot"><rect x="${left}" y="${top}" width="${plotWidth}" height="300"/></clipPath><linearGradient id="density-scale">${gradient}</linearGradient></defs><g font-family="system-ui,sans-serif" font-size="16" fill="#17211e">${titleLines.map((line, i) => `<text data-plot-title="true" x="${left}" y="${36 + i * 32}" font-size="24" font-weight="600">${xml(line)}</text>`).join("")}${yTicks}${xTicks}<path d="M${left} ${top}V${bottom}H${right}" stroke="#44514b" fill="none"/><g clip-path="url(#density-plot)">${lineSvg(true)}${points}${lineSvg(false)}</g><text x="${(left + right) / 2}" y="${bottom + 66}" text-anchor="middle">${xml(plot.xLabel)}</text><text x="20" y="${top + 150}" transform="rotate(-90 20 ${top + 150})" text-anchor="middle">${xml(plot.yLabel)}</text>${colorBar}${notes.map((note, i) => `<text data-annotation="${i}" x="24" y="${colorTop + 76 + i * 24}">${xml(note)}</text>`).join("")}${compact ? "" : `<text x="24" y="${height - 12}" font-size="14">完整显示 ${plot.x.length} 个数据点 · 原始数据随报告提供</text>`}</g></svg>`,
  };
}
