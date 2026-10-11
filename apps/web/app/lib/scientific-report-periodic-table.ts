import { readPeriodicElementValues, readSavedPeriodicTable } from "../../scientific-viewers/workspace/saved-periodic-table";
import { readSavedElementReference } from "../../scientific-viewers/workspace/saved-element-reference";
import { savedReportColorScale } from "./scientific-report-color-scale";
import { reportSvgTextWidth, wrapReportSvgText } from "./scientific-report-svg-text";

type Row = Record<string, unknown>;
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const xml = (v: string) => v.replace(/[&<>"']/gu, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);
const short = (v: number) => Number(v.toPrecision(5)).toString();

/** Inert report image of the same validated periodic table used interactively. */
export function renderReportPeriodicTable(payload: unknown, title: string, options?: { width?: number; compact?: boolean }) {
  const plot = readSavedPeriodicTable(payload), entries = readPeriodicElementValues(payload);
  const reference = readSavedElementReference(payload);
  if (!plot || !entries) return null;
  const scales = plot.data.map(savedReportColorScale);
  if (scales.some(scale => !scale)) return null;
  const width = finite(options?.width) ? Math.max(360, Math.min(1200, options.width)) : 920;
  const compact = options?.compact ?? false, left = 16, cell = (width - left * 2) / 18;
  const savedTitle = plot.layout.title.text;
  const distinctTitle = savedTitle !== "元素周期表" && savedTitle !== title;
  const heading = distinctTitle ? savedTitle : compact ? "" : title;
  const titleLines = wrapReportSvgText(heading, width - 48, 24);
  const top = titleLines.length ? 28 + titleLines.length * 32 : 12;
  const tableBottom = top + cell * 10, barY = tableBottom + 44;
  const barX = width * 0.1, barWidth = width * 0.8;
  const mainScale = scales[2]!, main = plot.data[2];
  const label = String(plot.layout.annotations.find(a => a.xref === "paper")?.text ?? entries.label);
  const log = (payload as Row).log === true;
  const originalBar = main.colorbar as Row;
  const roughStep = (mainScale.max - mainScale.min) / 4, power = 10 ** Math.floor(Math.log10(roughStep));
  const step = [1, 2, 5, 10].find(factor => factor * power >= roughStep)! * power;
  const first = Math.ceil(mainScale.min / step) * step;
  const automaticTicks = [mainScale.min, ...Array.from({ length: 6 }, (_, i) => first + i * step)
    .filter(v => v > mainScale.min && v < mainScale.max), mainScale.max];
  const ticks = Array.isArray(originalBar.tickvals) && Array.isArray(originalBar.ticktext)
    ? originalBar.tickvals.map((v, i) => ({ value: Number(v), label: String((originalBar.ticktext as unknown[])[i]) }))
    : automaticTicks.map(value => ({ value, label: short(log ? 10 ** value : value) }));
  const visibleTicks = ticks.filter(t => t.value >= mainScale.min && t.value <= mainScale.max)
    .sort((a, b) => a.value - b.value).map(t => ({ ...t, x: barX + (t.value - mainScale.min) / (mainScale.max - mainScale.min) * barWidth }));
  const tickSvg: string[] = [];
  let previousRight = -Infinity;
  for (const [i, tick] of visibleTicks.entries()) {
    const half = reportSvgTextWidth(tick.label, 12) / 2, last = visibleTicks.at(-1)!;
    const lastLeft = last.x - reportSvgTextWidth(last.label, 12) / 2;
    if (tick.x - half < previousRight + 8 || i < visibleTicks.length - 1 && tick.x + half + 8 > lastLeft) continue;
    tickSvg.push(`<text data-color-tick="${tick.value}" x="${tick.x}" y="${barY + 32}" text-anchor="middle" font-size="12">${xml(tick.label)}</text>`);
    previousRight = tick.x + half;
  }
  const layers = plot.data.map((trace, index) => (trace.z as Array<Array<number | null>>).map((row, y) => row.map((value, x) => value === null ? "" :
    `<rect data-layer="${index}" data-x="${x}" data-y="${y}" x="${left + x * cell + (index ? 1 : 0.5)}" y="${top + (9 - y) * cell + (index ? 1 : 0.5)}" width="${cell - (index ? 2 : 1)}" height="${cell - (index ? 2 : 1)}" fill="${scales[index]!.fill(value)}"/>`).join("")).join("")).join("");
  const outlines = plot.layout.shapes.map(shape => `<rect data-highlight="${xml(String(shape.name))}" x="${left + (Number(shape.x0) + .5) * cell}" y="${top + (9.5 - Number(shape.y1)) * cell}" width="${(Number(shape.x1) - Number(shape.x0)) * cell}" height="${(Number(shape.y1) - Number(shape.y0)) * cell}" fill="none" stroke="${(shape.line as Row).color}" stroke-width="${(shape.line as Row).width}"/>`).join("");
  const symbols = plot.cells.map(a => {
    const name = a.symbol, value = entries.values[name], description = `${a.atomicNumber ? `${a.atomicNumber} · ` : ""}${name} · ${a.selected ? `${entries.label}：${value ?? "参考值缺失"}` : "未选入本次范围"}`;
    const x = left + (a.x + .5) * cell, y = top + (9 - a.y + .5) * cell;
    const numbered = width >= 650 && a.atomicNumber !== undefined;
    return `<g data-element="${name}"${value === undefined ? "" : ` data-value="${value}"`}><title>${xml(description)}</title>${numbered ? `<text data-atomic-number="${a.atomicNumber}" x="${x}" y="${y - cell * .25}" text-anchor="middle" dominant-baseline="central" font-size="12" fill="${a.color}">${a.atomicNumber}</text>` : ""}<text x="${x}" y="${y + (numbered ? cell * .1 : 0)}" text-anchor="middle" dominant-baseline="central" font-family="ui-monospace,Consolas,monospace" font-size="${width < 600 ? 12 : 16}" fill="${a.color}">${name}</text></g>`;
  }).join("");
  const footer = reference ? reference.notes.flatMap(note => wrapReportSvgText(note, width - 48, 14))
    : compact ? [] : wrapReportSvgText(`完整显示 ${plot.pointCount} 个元素的原始数值 · 原始数据随报告提供`, width - 48, 14);
  const height = barY + 52 + footer.length * 22;
  return {
    pointCount: plot.pointCount, axes: [], fit: "width" as const,
    svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="title desc"><title id="title">${xml(title)}</title><desc id="desc">${xml(label)}；${plot.pointCount} 个元素有保存数值。${reference ? "平台参考资料。" : "元素位置和色阶来自已保存图表；未重新统计材料。"}</desc><rect width="${width}" height="${height}" fill="#ffffff"/><defs><linearGradient id="periodic-scale">${mainScale.gradient}</linearGradient></defs><g font-family="system-ui,sans-serif" fill="#17211e">${titleLines.map((line, i) => `<text data-plot-title="true" x="24" y="${32 + i * 32}" font-size="24" font-weight="600">${xml(line)}</text>`).join("")}${layers}${outlines}${symbols}<text x="${width / 2}" y="${barY - 14}" font-size="14" text-anchor="middle">${xml(label)}</text><rect data-colorbar="true" data-min="${mainScale.min}" data-max="${mainScale.max}" x="${barX}" y="${barY}" width="${barWidth}" height="12" fill="url(#periodic-scale)"/>${tickSvg.join("")}${footer.map((line, i) => `<text data-plot-footer="true" x="24" y="${barY + 60 + i * 22}" font-size="14">${xml(line)}</text>`).join("")}</g></svg>`,
  };
}
