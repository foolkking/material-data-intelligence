import { mapViewerSceneForRenderer } from "../../scientific-viewers/viewer-scene/viewerSceneRendererMapper";
import { latticeEdges } from "../../scientific-viewers/viewer-scene/viewerSceneLatticeGeometry";
import { periodicSiteKey } from "../../scientific-viewers/viewer-scene/viewerScenePeriodicGeometry";
import type { RenderAtom, RenderVector3 } from "../../scientific-viewers/viewer-scene/viewerSceneRendererTypes";
import { wrapReportSvgText, reportSvgTextWidth } from "./scientific-report-svg-text";

const xml = (v: string) => v.replace(/[&<>"']/gu, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);
const dot = (a: RenderVector3, b: RenderVector3) => a.reduce((sum, value, i) => sum + value * b[i], 0);
const unit = (v: RenderVector3): RenderVector3 => { const length = Math.hypot(...v); return [v[0] / length, v[1] / length, v[2] / length]; };
const cross = (a: RenderVector3, b: RenderVector3): RenderVector3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const obliqueToward = unit([1, 0.6, 1.8]), obliqueRight = unit(cross([0, 1, 0], obliqueToward));
// Use compact display balls to expose recorded connections; positions and
// relative source radii stay unchanged. This is not a physical radius model.
const DISPLAY_RADIUS_SCALE = 0.45;
type View = { name: string; id: string; right: RenderVector3; up: RenderVector3; toward: RenderVector3 };
const VIEWS: View[] = [
  { name: "空间视图", id: "oblique", right: obliqueRight, up: cross(obliqueToward, obliqueRight), toward: obliqueToward },
  { name: "XY 投影", id: "xy", right: [1, 0, 0], up: [0, 1, 0], toward: [0, 0, 1] },
  { name: "XZ 投影", id: "xz", right: [1, 0, 0], up: [0, 0, 1], toward: [0, -1, 0] },
  { name: "YZ 投影", id: "yz", right: [0, 1, 0], up: [0, 0, 1], toward: [1, 0, 0] },
];

/** Inert orthographic projections of validated, saved structure geometry.
 * Periodic images come only from recorded bond endpoints; no neighbors are inferred. */
export function renderReportStructure(payload: unknown, title: string, options?: { width?: number; compact?: boolean }) {
  const mapped = mapViewerSceneForRenderer(payload);
  if (!mapped.ok) return null;
  const raw = payload as { scene: { sites: Array<{ occupancy?: unknown }>; bonds?: unknown[] }; validation?: { truncated?: boolean }; warnings?: unknown[] };
  const scene = mapped.scene;
  if (scene.bonds.length !== (raw.scene.bonds?.length ?? 0)
    || scene.bonds.some(bond => !Number.isFinite(bond.distanceAngstrom) || bond.distanceAngstrom < 0
      || Math.abs(Math.hypot(...bond.end.map((v, i) => v - bond.start[i])) - bond.distanceAngstrom) > 1e-5)
    || scene.atoms.some(atom => atom.siteIndex < 0 || !Number.isSafeInteger(atom.siteIndex) || atom.species.length > 64)
    || raw.scene.sites.some(site => site.occupancy !== undefined && (typeof site.occupancy !== "number" || !Number.isFinite(site.occupancy) || site.occupancy < 0 || site.occupancy > 1))) return null;
  const atoms = new Map(scene.atoms.map(atom => [periodicSiteKey(atom.ref), atom]));
  const bySite = new Map(scene.atoms.map(atom => [atom.siteIndex, atom]));
  for (const bond of scene.bonds) {
    for (const [ref, position] of [[bond.fromRef, bond.start], [bond.toRef, bond.end]] as const) {
      const key = periodicSiteKey(ref);
      if (!atoms.has(key)) {
        const original = bySite.get(ref.siteIndex)!;
        atoms.set(key, { ...original, id: `site-${key}`, ref, position });
      }
    }
  }
  if (atoms.size > 2048) return null;
  const allAtoms = [...atoms.values()], edges = latticeEdges(scene.lattice.matrix);
  const isImage = (atom: RenderAtom) => atom.ref.imageOffset.some(value => value !== 0);
  const width = typeof options?.width === "number" && Number.isFinite(options.width) ? Math.max(360, Math.min(1200, options.width)) : 920;
  const columns = width < 600 ? 1 : 2, gap = 24, panel = (width - 40 - gap * (columns - 1)) / columns;
  const font = width < 600 ? 14 : 15;
  const headings = options?.compact ? [] : wrapReportSvgText(title, width - 40, 22);
  const top = 20 + headings.length * 30;
  const projected = VIEWS.map(view => {
    const points = allAtoms.map(atom => ({ atom, x: dot(atom.position, view.right), y: dot(atom.position, view.up), z: dot(atom.position, view.toward) }));
    const ends = edges.flatMap(edge => edge.map(point => [dot(point, view.right), dot(point, view.up)]));
    const minX = Math.min(...points.map(p => p.x - p.atom.radius * DISPLAY_RADIUS_SCALE), ...ends.map(p => p[0]));
    const maxX = Math.max(...points.map(p => p.x + p.atom.radius * DISPLAY_RADIUS_SCALE), ...ends.map(p => p[0]));
    const minY = Math.min(...points.map(p => p.y - p.atom.radius * DISPLAY_RADIUS_SCALE), ...ends.map(p => p[1]));
    const maxY = Math.max(...points.map(p => p.y + p.atom.radius * DISPLAY_RADIUS_SCALE), ...ends.map(p => p[1]));
    return { view, points, minX, maxX, minY, maxY };
  });
  const span = Math.max(...projected.flatMap(p => [p.maxX - p.minX, p.maxY - p.minY]));
  const scale = (panel - 48) / span;
  if (!Number.isFinite(scale) || scale <= 0 || projected.some(p => ![p.minX, p.maxX, p.minY, p.maxY, ...p.points.flatMap(v => [v.x, v.y, v.z])].every(Number.isFinite))) return null;
  const content: string[] = [];
  for (const [index, p] of projected.entries()) {
    const left = 20 + (index % columns) * (panel + gap), y = top + Math.floor(index / columns) * (panel + 38);
    const centerX = p.minX + (p.maxX - p.minX) / 2, centerY = p.minY + (p.maxY - p.minY) / 2;
    const project = (point: RenderVector3) => [left + panel / 2 + (dot(point, p.view.right) - centerX) * scale,
      y + 28 + panel / 2 - (dot(point, p.view.up) - centerY) * scale];
    const line = (from: RenderVector3, to: RenderVector3) => {
      const a = project(from), b = project(to);
      return `x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}"`;
    };
    content.push(`<g data-structure-view="${p.view.id}" data-scale="${scale}"><text x="${left}" y="${y + 16}" font-size="${font + 1}" font-weight="600">${p.view.name}</text>`);
    for (const [edge, [a, b]] of edges.entries()) content.push(`<line data-cell-edge="${edge}" data-start="${a}" data-end="${b}" ${line(a, b)} stroke="#71817a" stroke-width="1"/>`);
    for (const bond of scene.bonds) content.push(`<line data-bond="${xml(bond.id)}" data-from="${periodicSiteKey(bond.fromRef)}" data-to="${periodicSiteKey(bond.toRef)}" data-start="${bond.start}" data-end="${bond.end}" data-distance="${bond.distanceAngstrom}" data-source="${bond.source}" data-authoritative="${bond.authoritative}" ${line(bond.start, bond.end)} stroke="#5b6762" stroke-width="1.5"${bond.authoritative ? "" : ' stroke-dasharray="4 3"'}><title>${xml(`${bond.id} · 保存距离 ${bond.distanceAngstrom} Å`)}</title></line>`);
    for (const { atom } of [...p.points].sort((a, b) => a.z - b.z || a.atom.siteIndex - b.atom.siteIndex)) {
      const point = project(atom.position), image = isImage(atom);
      const position = `cx="${point[0]}" cy="${point[1]}" r="${atom.radius * DISPLAY_RADIUS_SCALE * scale}"`;
      // Hollow images must not erase a real site at the same projected point.
      if (image) content.push(`<circle ${position} fill="none" stroke="#44534c" stroke-width="3" stroke-dasharray="3 2"/>`);
      content.push(`<circle data-site="${periodicSiteKey(atom.ref)}" data-image="${image}" data-xyz="${atom.position}" data-occupancy="${atom.occupancy}" data-source-radius="${atom.radius}" ${position} fill="${image ? "none" : atom.color}" stroke="${image ? atom.color : "#263b33"}" stroke-width="${image ? 1.5 : 0.7}"${image ? ' stroke-dasharray="3 2"' : ""}><title>${xml(`${atom.label} · 位点 ${atom.siteIndex}${image ? ` · 周期偏移 [${atom.ref.imageOffset}]` : ""} · 笛卡尔坐标 [${atom.position}] Å · 占位率 ${atom.occupancy}`)}</title></circle>`);
    }
    content.push("</g>");
  }
  let cursor = top + Math.ceil(VIEWS.length / columns) * (panel + 38) + 10;
  const notes: string[] = [`晶胞保存 ${scene.atoms.length} 个位点 · ${scene.bonds.length} 条连线`];
  if (scene.connectivity?.method === "ideal_first_shell") notes.push("理想晶格模型；不代表样品实测或结构弛豫结果。");
  const species = [...new Set(scene.atoms.map(atom => atom.species))];
  let legendX = 20;
  for (const name of species) {
    const group = scene.atoms.filter(atom => atom.species === name), label = `${name} · ${group.length} 位点`;
    const labelWidth = reportSvgTextWidth(label, font) + 38;
    if (legendX > 20 && legendX + labelWidth > width - 20) { cursor += 26; legendX = 20; }
    const lines = wrapReportSvgText(label, width - legendX - 40, font);
    content.push(`<g data-species="${xml(name)}"><circle cx="${legendX + 6}" cy="${cursor - 5}" r="5" fill="${group[0].color}" stroke="#263b33" stroke-width="0.7"/><text font-size="${font}">${lines.map((text, i) => `<tspan x="${legendX + 20}" y="${cursor + i * 22}">${xml(text)}</tspan>`).join("")}</text></g>`);
    if (lines.length > 1) { cursor += (lines.length - 1) * 22; legendX = width; } else legendX += labelWidth;
  }
  cursor += 30;
  notes.push("各视图同比例正交投影；球半径仅用于显示，投影距离不等于三维距离。");
  if (allAtoms.length > scene.atoms.length) notes.push(`空心球表示 ${allAtoms.length - scene.atoms.length} 个周期映像，不计入晶胞位点数。`);
  if (scene.bonds.some(bond => !bond.authoritative)) notes.push("虚线为已保存的候选邻接关系，不代表已确认的化学键。");
  if (scene.bonds.some(bond => bond.authoritative)) notes.push("实线为场景中已保存的显式输入关系。");
  if (scene.contractVersion === "viewer_scene.v1" && scene.bonds.length) notes.push("旧版场景连线仅包含同一晶胞内的已保存关系。");
  const partial = scene.atoms.filter(atom => atom.occupancy !== 1);
  if (partial.length) notes.push(`部分占位：${partial.map(atom => `${atom.species} 位点 ${atom.siteIndex} = ${atom.occupancy}`).join("；")}。`);
  if (raw.validation?.truncated) notes.push("已保存的场景经过截断；完整限制见原始文件。");
  else if (raw.warnings?.length) notes.push("场景原件附有限制说明，详见随附原始文件。");
  for (const note of notes) for (const text of wrapReportSvgText(note, width - 40, font)) {
    content.push(`<text data-structure-note="true" x="20" y="${cursor}" font-size="${font}" fill="#44534c">${xml(text)}</text>`); cursor += 22;
  }
  return { pointCount: scene.atoms.length, fit: "width" as const, axes: [],
    svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${cursor + 14}" role="img" aria-labelledby="title desc"><title id="title">${xml(title)}</title><desc id="desc">保存结构的四个正交投影，保留原始笛卡尔坐标、晶格和连线。周期映像与晶胞位点分开计数。</desc><rect width="${width}" height="${cursor + 14}" fill="#fff"/><g font-family="system-ui,sans-serif" fill="#172b22">${headings.map((text, i) => `<text x="20" y="${28 + i * 30}" font-size="22" font-weight="600">${xml(text)}</text>`).join("")}${content.join("")}</g></svg>` };
}
