import { normalizedPlotFigure } from "../../scientific-viewers/workspace/workspace-plot-contract";
import { readPlotHierarchy } from "../../scientific-viewers/workspace/workspace-plot-hierarchy";

export type HierarchyNode = { index: number; id: string; label: string; value: number; total: number; parent: number; children: number[]; depth: number; path: string };
type Row = Record<string, unknown>;
export const hierarchyRecord = (v: unknown): Row => v && typeof v === "object" && !Array.isArray(v) ? v as Row : {};
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const has = (row: Row, keys: string[]) => keys.some(key => row[key] !== undefined);
const label = (v: unknown) => typeof v === "string" ? v : typeof hierarchyRecord(v).text === "string" ? String(hierarchyRecord(v).text) : "";

/** The report and interactive plot share graph validation. Raw IDs and full
 * labels remain in the report index; renderer-local IDs are never provenance. */
export function readReportHierarchy(payload: unknown) {
  const figure = normalizedPlotFigure(payload);
  if (!figure || !Array.isArray(figure.data) || figure.data.length !== 1) return null;
  const rawLayout = hierarchyRecord(figure.layout), template = hierarchyRecord(rawLayout.template);
  if (typeof rawLayout.template === "string") return null;
  const raw = hierarchyRecord(figure.data[0]), type = raw.type;
  if (type !== "treemap" && type !== "sunburst") return null;
  const templates = hierarchyRecord(template.data)[type];
  const trace = { ...(Array.isArray(templates) ? hierarchyRecord(templates[0]) : {}), ...raw };
  const layout = { ...hierarchyRecord(template.layout), ...rawLayout }, marker = hierarchyRecord(trace.marker);
  if (has(trace, ["transforms", "customdata", "meta", "count", "leaf", "root", "insidetextorientation"])
    || trace.visible !== undefined && trace.visible !== true || trace.opacity !== undefined && trace.opacity !== 1
    || has(layout, ["grid", "annotations", "shapes", "images"])
    || has(marker, ["colors", "colorscale", "coloraxis", "cmin", "cmax"])
    || has(hierarchyRecord(trace.tiling), ["squarifyratio", "flip", "pad"])) return null;
  const packing = hierarchyRecord(trace.tiling).packing ?? "squarify";
  if (!["squarify", "slice", "dice", "slice-dice"].includes(String(packing))) return null;
  if (trace.rotation !== undefined && !finite(trace.rotation)) return null;
  // Permit the adapter's label/value formatting; arbitrary template fields
  // would add scientific content that this renderer cannot represent.
  if (trace.texttemplate !== undefined && trace.texttemplate !== "" && (typeof trace.texttemplate !== "string"
    || !/^(?:%\{(?:label|value|percentRoot|percentParent|percentEntry)(?::(?:\.\d{1,2}[f%]|,\.\d{1,2}%))?\}|<br>|N=|Count: |\s)+$/u.test(trace.texttemplate))) return null;
  const graph = readPlotHierarchy(trace);
  if (!graph || (graph.values as number[]).length > 5000) return null;
  const values = graph.values as number[], labels = trace.labels as string[], ids = (trace.ids ?? labels) as string[];
  const nodes: HierarchyNode[] = values.map((value, index) => ({ index, id: ids[index], label: labels[index], value, total: value,
    parent: (graph.parents as string[])[index] === "" ? -1 : Number((graph.parents as string[])[index].slice(5)), children: [], depth: 0, path: "" }));
  const roots: number[] = [];
  for (const node of nodes) { if (node.parent < 0) roots.push(node.index); else nodes[node.parent].children.push(node.index); }
  const traversal: number[] = [], queue = [...roots];
  for (let i = 0; i < queue.length; i++) {
    const node = nodes[queue[i]]; traversal.push(node.index);
    for (const child of node.children) { nodes[child].depth = node.depth + 1; queue.push(child); }
  }
  for (const index of [...traversal].reverse()) {
    const node = nodes[index], children = node.children.reduce((sum, child) => sum + nodes[child].total, 0);
    if (graph.branchvalues === "remainder") node.total += children;
    else if (children > 0 && node.total === 0) return null;
    if (!finite(node.total)) return null;
  }
  const level = typeof graph.level === "string" && graph.level ? Number(graph.level.slice(5)) : null;
  const selectedRoots = level === null ? roots : [level];
  const baseDepth = level === null ? 0 : nodes[level].depth;
  const maxdepth = graph.maxdepth === undefined || graph.maxdepth === -1 ? Infinity : Number(graph.maxdepth);
  const ordered = (children: number[]) => graph.sort === false ? [...children] : [...children].sort((a, b) => nodes[b].total - nodes[a].total || a - b);
  const rootOrder = ordered(selectedRoots), visible: number[] = [], pending = [...rootOrder].reverse();
  let hidden = 0, pathBudget = 0;
  while (pending.length) {
    const node = nodes[pending.pop()!], depth = node.depth - baseDepth;
    if (depth >= maxdepth) { hidden++; pending.push(...node.children); continue; }
    // Deep arbitrary graphs are valid data, but not a readable bounded image.
    if (depth > 32) return null;
    node.path = node.parent < 0 || node.index === level ? node.label : `${nodes[node.parent].path} / ${node.label}`;
    if ((pathBudget += node.path.length) > 1_000_000) return null;
    node.children = ordered(node.children);
    visible.push(node.index); pending.push(...[...node.children].reverse());
  }
  const total = rootOrder.reduce((sum, index) => sum + nodes[index].total, 0);
  const fullTotal = roots.reduce((sum, index) => sum + nodes[index].total, 0);
  if (!finite(total) || total <= 0 || !finite(fullTotal)) return null;
  const domain = hierarchyRecord(graph.domain);
  const dx = (domain.x ?? [0, 1]) as number[], dy = (domain.y ?? [0, 1]) as number[];
  const notes: string[] = [];
  const warnings = hierarchyRecord(payload).warnings;
  if (Array.isArray(warnings) && warnings.some(w => ["too_many_groups_warning", "too_many_leaf_nodes_warning"].includes(String(w)))) notes.push("分析结果已省略部分分组；图中仅展示已保存的分组与计数。");
  if (hidden) notes.push(`按保存的显示深度隐藏 ${hidden} 个节点；完整层级见原始文件。`);
  if (level !== null) notes.push(`显示分组：${nodes[level].label}；其他分支见原始文件。`);
  if (graph.branchvalues === "remainder") notes.push("面积按本组值与子分组合计分配；索引保留本组保存值。 ");
  const templateFlags: Record<string, string> = { label: "label", value: "value", percentRoot: "percent root", percentParent: "percent parent", percentEntry: "percent entry" };
  const textinfo = trace.texttemplate ? [...new Set([...String(trace.texttemplate).matchAll(/%\{(label|value|percentRoot|percentParent|percentEntry)(?=[:}])/gu)].map(match => templateFlags[match[1]]))].join("+") : String(graph.textinfo);
  return { type, nodes, roots: rootOrder, visible, total, fullTotal, baseDepth, branchvalues: graph.branchvalues as "total" | "remainder",
    textinfo, packing: String(packing), rotation: Number(trace.rotation ?? 0) % 360, domain: { x: dx, y: dy },
    title: label(layout.title), notes };
}
