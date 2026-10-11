import { hierarchyRecord, readReportHierarchy, type HierarchyNode } from "./scientific-report-hierarchy-model";
import { reportSvgTextWidth, wrapReportSvgText } from "./scientific-report-svg-text";

type Box = { x: number; y: number; w: number; h: number };
type Weighted = { index: number; weight: number };
const xml = (v: string) => v.replace(/[&<>"']/gu, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);
const COLORS = ["#b4dcd2", "#c6d5ed", "#edccbb", "#d9cce9", "#d9deb0", "#bedbdc", "#edcfdb", "#ded5c5"];

/** Allocate rectangles by aggregate weight, including unassigned parent area. */
function tile(items: Weighted[], total: number, box: Box, packing: string, depth: number) {
  const sum = items.reduce((acc, item) => acc + item.weight, 0), denominator = Math.max(total, sum);
  if (denominator <= 0 || box.w <= 0 || box.h <= 0) return [];
  const weights = [...items, ...(total > sum ? [{ index: -1, weight: total - sum }] : [])]
    .filter(item => item.weight > 0).map(item => ({ ...item, area: item.weight / denominator * box.w * box.h }));
  const result: Array<{ index: number; box: Box }> = [];
  let x = box.x, y = box.y, w = box.w, h = box.h;
  const row = (entries: typeof weights, vertical: boolean) => {
    const area = entries.reduce((acc, item) => acc + item.area, 0), size = vertical ? h : w;
    if (size <= 0 || area <= 0) return;
    const thickness = Math.min(vertical ? w : h, area / size);
    let position = vertical ? y : x;
    for (const item of entries) {
      const length = item.area / area * size;
      result.push({ index: item.index, box: vertical ? { x, y: position, w: thickness, h: length } : { x: position, y, w: length, h: thickness } });
      position += length;
    }
    if (vertical) { x += thickness; w = Math.max(0, w - thickness); } else { y += thickness; h = Math.max(0, h - thickness); }
  };
  if (packing !== "squarify") { row(weights, packing === "slice" || packing === "slice-dice" && depth % 2 === 0); return result; }
  const worst = (entries: typeof weights, side: number) => {
    const areas = entries.map(item => item.area), sum = areas.reduce((a, b) => a + b, 0);
    return Math.max(side * side * Math.max(...areas) / (sum * sum), sum * sum / (side * side * Math.min(...areas)));
  };
  let batch: typeof weights = [];
  for (const item of weights) {
    if (batch.length && worst([...batch, item], Math.min(w, h)) > worst(batch, Math.min(w, h))) { row(batch, w >= h); batch = []; }
    batch.push(item);
  }
  if (batch.length) row(batch, w >= h);
  return result;
}

function sector(cx: number, cy: number, r0: number, r1: number, start: number, end: number) {
  const point = (r: number, angle: number) => `${cx + r * Math.cos(angle)},${cy - r * Math.sin(angle)}`;
  const span = end - start;
  if (span >= Math.PI * 2 - 1e-10) {
    const outer = `M${point(r1, start)}A${r1},${r1} 0 1 0 ${point(r1, start + Math.PI)}A${r1},${r1} 0 1 0 ${point(r1, end)}`;
    return r0 === 0 ? `${outer}Z` : `${outer}L${point(r0, end)}A${r0},${r0} 0 1 1 ${point(r0, start + Math.PI)}A${r0},${r0} 0 1 1 ${point(r0, start)}Z`;
  }
  const outer = `M${point(r1, start)}A${r1},${r1} 0 ${span > Math.PI ? 1 : 0} 0 ${point(r1, end)}`;
  return r0 === 0 ? `${outer}L${cx},${cy}Z` : `${outer}L${point(r0, end)}A${r0},${r0} 0 ${span > Math.PI ? 1 : 0} 1 ${point(r0, start)}Z`;
}

/** Saved hierarchy geometry plus a complete identity/count index for small cells. */
export function renderReportHierarchy(payload: unknown, title: string, options?: { width?: number; compact?: boolean }) {
  const graph = readReportHierarchy(payload);
  if (!graph) return null;
  const width = typeof options?.width === "number" && Number.isFinite(options.width) ? Math.max(360, Math.min(1200, options.width)) : 920;
  const font = width < 600 ? 14 : 15;
  const distinct = graph.title && ![title, "Chemical System Treemap", "Chemical System Sunburst"].includes(graph.title) ? graph.title : "";
  const headings = wrapReportSvgText([options?.compact ? "" : title, distinct].filter(Boolean).join("\n"), width - 40, 22);
  const top = 20 + headings.length * 30, chartHeight = graph.type === "sunburst" ? Math.min(width - 40, 540) : width < 600 ? 340 : 420;
  const box = { x: 20 + graph.domain.x[0] * (width - 40), y: top + (1 - graph.domain.y[1]) * chartHeight,
    w: (graph.domain.x[1] - graph.domain.x[0]) * (width - 40), h: (graph.domain.y[1] - graph.domain.y[0]) * chartHeight };
  const visible = new Set(graph.visible), keys = new Map(graph.visible.map((index, i) => [index, i + 1]));
  const composition = ["composition.chem_sys_treemap", "composition.chem_sys_sunburst"].includes(String(hierarchyRecord(payload).artifactType));
  const arities: Record<string, string> = { unary: "一元体系", binary: "二元体系", ternary: "三元体系", quaternary: "四元体系", quinary: "五元体系", senary: "六元体系" };
  const displayLabel = (text: string) => {
    const match = composition ? /^(unary|binary|ternary|quaternary|quinary|senary)(?: \(N=\d+, [\d.]+%\))?$/u.exec(text) : null;
    return match ? arities[match[1]] : text;
  };
  const colors = new Map<number, string>();
  for (const [rootIndex, root] of graph.roots.entries()) {
    const queue = [root];
    for (let i = 0; i < queue.length; i++) { colors.set(queue[i], COLORS[rootIndex % COLORS.length]); queue.push(...graph.nodes[queue[i]].children); }
  }
  const attributes = (node: HierarchyNode) => `data-node="${xml(node.id)}" data-parent="${xml(node.parent < 0 ? "" : graph.nodes[node.parent].id)}" data-value="${node.value}" data-total="${node.total}"`;
  const description = (node: HierarchyNode) => `<title>${xml(`${node.path} · 保存值：${node.value}${graph.branchvalues === "remainder" ? ` · 含子分组合计：${node.total}` : ""}`)}</title>`;
  const shownLabel = (node: HierarchyNode) => {
    if (graph.textinfo === "none") return "";
    const parts = [String(keys.get(node.index))];
    if (graph.textinfo.includes("current path")) parts.push(node.path.split(" / ").map(displayLabel).join(" / "));
    else if (graph.textinfo.includes("label")) parts.push(displayLabel(node.label));
    if (graph.textinfo.includes("value")) parts.push(String(node.value));
    if (graph.textinfo.includes("percent root")) parts.push(`${Number((node.total / graph.fullTotal * 100).toFixed(1))}%`);
    if (graph.textinfo.includes("percent entry")) parts.push(`${Number((node.total / graph.total * 100).toFixed(1))}%`);
    if (graph.textinfo.includes("percent parent") && node.parent >= 0) {
      const parent = graph.nodes[node.parent].total;
      parts.push(`${Number((parent ? node.total / parent * 100 : 0).toFixed(1))}%`);
    }
    return parts.join(" · ");
  };
  const shapes: string[] = [];
  if (graph.type === "treemap") {
    const pending = tile(graph.roots.map(index => ({ index, weight: graph.nodes[index].total })), graph.total, box, graph.packing, 0).reverse();
    while (pending.length) {
      const entry = pending.pop()!;
      if (entry.index < 0 || !visible.has(entry.index)) continue;
      const node = graph.nodes[entry.index], r = entry.box, children = node.children.filter(index => visible.has(index));
      const inset = Math.min(2, r.w / 20, r.h / 20), header = children.length ? Math.min(25, r.h * 0.18) : 0;
      shapes.push(`<rect ${attributes(node)} x="${r.x}" y="${r.y}" width="${r.w}" height="${r.h}" fill="${colors.get(node.index)}" stroke="#fff" stroke-width="1">${description(node)}</rect>`);
      const text = shownLabel(node), pieces = text.split(" · ");
      const lines = reportSvgTextWidth(text, font) <= r.w - 12 ? [text] : pieces;
      const availableHeight = children.length ? header : r.h;
      if (text && r.w > 30 && availableHeight >= font + 8) {
        const fits = lines.every(line => reportSvgTextWidth(line, font) <= r.w - 12) && lines.length * (font + 3) <= availableHeight - 6;
        const compact = `${keys.get(node.index)} ${displayLabel(node.label)}`;
        const chosen = fits ? lines : [graph.textinfo.includes("label") && reportSvgTextWidth(compact, font) <= r.w - 12 ? compact : String(keys.get(node.index))];
        shapes.push(`<text data-node-label="${xml(node.id)}" font-size="${font}">${chosen.map((line, i) => `<tspan x="${r.x + 6}" y="${r.y + font + 4 + i * (font + 3)}">${xml(line)}</tspan>`).join("")}</text>`);
      }
      if (children.length) pending.push(...tile(children.map(index => ({ index, weight: graph.nodes[index].total })), node.total,
        { x: r.x + inset, y: r.y + header, w: Math.max(0, r.w - inset * 2), h: Math.max(0, r.h - header - inset) }, graph.packing, node.depth + 1).reverse());
    }
  } else {
    const depth = Math.max(...graph.visible.map(index => graph.nodes[index].depth - graph.baseDepth)) + 1;
    const radius = Math.min(box.w, box.h) / 2, ring = radius / depth, cx = box.x + box.w / 2, cy = box.y + box.h / 2;
    const pending = [{ children: graph.roots, start: graph.rotation * Math.PI / 180, span: Math.PI * 2, total: graph.total }];
    while (pending.length) {
      const group = pending.pop()!; let angle = group.start;
      const sum = group.children.reduce((acc, index) => acc + graph.nodes[index].total, 0), denominator = Math.max(group.total, sum);
      for (const index of group.children) {
        const node = graph.nodes[index], span = denominator ? group.span * node.total / denominator : 0;
        if (visible.has(index) && span > 0) {
          const level = node.depth - graph.baseDepth, r0 = ring * level, r1 = ring * (level + 1);
          shapes.push(`<path ${attributes(node)} data-start="${angle}" data-span="${span}" data-inner-radius="${r0}" data-outer-radius="${r1}" d="${sector(cx, cy, r0, r1, angle, angle + span)}" fill="${colors.get(index)}" stroke="#fff" stroke-width="1">${description(node)}</path>`);
          const mid = angle + span / 2, rm = (r0 + r1) / 2, text = shownLabel(node);
          const tx = cx + rm * Math.cos(mid), ty = cy - rm * Math.sin(mid);
          const fits = (value: string) => {
            const half = reportSvgTextWidth(value, font) / 2, hh = font * 0.65, dx = tx - cx, dy = ty - cy;
            const minimum = Math.hypot(Math.max(0, Math.abs(dx) - half), Math.max(0, Math.abs(dy) - hh));
            if (minimum < r0 + 2) return false;
            return [-half, half].every(x => [-hh, hh].every(y => {
              const distance = Math.hypot(dx + x, dy + y), relative = ((Math.atan2(-dy - y, dx + x) - angle) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2);
              return distance < r1 - 2 && (span >= Math.PI * 2 - 1e-10 || relative > 0 && relative < span);
            }));
          };
          const compactLabel = graph.textinfo.includes("label") ? `${keys.get(index)} ${displayLabel(node.label)}` : String(keys.get(index));
          const label = [text, compactLabel, String(keys.get(index))].find(value => value && fits(value)) ?? "";
          if (text && label) shapes.push(`<text data-node-label="${xml(node.id)}" x="${tx}" y="${ty + font / 3}" text-anchor="middle" font-size="${font}">${xml(label)}</text>`);
          const children = node.children.filter(child => visible.has(child));
          if (children.length) pending.push({ children, start: angle, span, total: node.total });
        }
        angle += span;
      }
    }
  }
  let cursor = top + chartHeight + 32;
  const notes = graph.notes.flatMap(note => wrapReportSvgText(note.trim(), width - 40, font));
  const footer: string[] = [];
  for (const note of notes) { footer.push(`<text data-hierarchy-note="true" x="20" y="${cursor}" font-size="${font}">${xml(note)}</text>`); cursor += 22; }
  footer.push(`<text x="20" y="${cursor + 8}" font-size="${font + 1}" font-weight="600">分组与计数</text>`); cursor += 36;
  const labelLeft = Math.max(66, 54 + reportSvgTextWidth(String(graph.visible.length), font));
  for (const index of graph.visible) {
    const node = graph.nodes[index], key = keys.get(index)!;
    const percentages: string[] = [];
    if (graph.textinfo.includes("percent root")) percentages.push(`${Number((node.total / graph.fullTotal * 100).toFixed(1))}%（全图）`);
    if (graph.textinfo.includes("percent entry")) percentages.push(`${Number((node.total / graph.total * 100).toFixed(1))}%（当前范围）`);
    if (graph.textinfo.includes("percent parent") && node.parent >= 0) {
      const parent = graph.nodes[node.parent].total;
      percentages.push(`${Number((parent ? node.total / parent * 100 : 0).toFixed(1))}%（父分组）`);
    }
    const text = [`${node.path.split(" / ").map(displayLabel).join(" / ")} · ${graph.branchvalues === "remainder" ? `本组 ${node.value}；含子分组合计 ${node.total}` : node.value}`, ...percentages].join(" · ");
    const lines = wrapReportSvgText(text, width - labelLeft - 20, font);
    footer.push(`<g data-node-index="${xml(node.id)}" data-parent="${xml(node.parent < 0 ? "" : graph.nodes[node.parent].id)}" data-value="${node.value}" data-total="${node.total}">${description(node)}<rect x="20" y="${cursor - font + 2}" width="10" height="10" fill="${colors.get(index)}"/><text x="36" y="${cursor}" font-size="${font}" fill="#44514b">${key}</text><text font-size="${font}">${lines.map((line, i) => `<tspan x="${labelLeft}" y="${cursor + i * 22}">${xml(line)}</tspan>`).join("")}</text></g>`);
    cursor += lines.length * 22 + 10;
  }
  return { pointCount: graph.visible.length, fit: "width" as const, axes: [],
    svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${cursor + 12}" role="img" aria-labelledby="title desc"><title id="title">${xml(title)}</title><desc id="desc">${xml(`${graph.type === "treemap" ? "矩形树图" : "旭日图"}；${graph.visible.length} 个保存节点。分组按保存的 ID 关联；完整名称和计数见图下索引。`)}</desc><rect width="${width}" height="${cursor + 12}" fill="#fff"/><g font-family="system-ui,sans-serif" fill="#17211e">${headings.map((text, i) => `<text data-plot-title="true" x="20" y="${28 + i * 30}" font-size="22" font-weight="600">${xml(text)}</text>`).join("")}${shapes.join("")}${footer.join("")}</g></svg>` };
}
