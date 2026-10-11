import { readSavedLocalEnvironment, algorithmLabel, classificationLabel, geometryLabel, faceReason } from "../../scientific-viewers/workspace/saved-local-environment";
import { POLYHEDRON_VIEWS, projectSavedPolyhedron } from "../../scientific-viewers/workspace/localEnvironmentProjection";
import { wrapReportSvgText } from "./scientific-report-svg-text";

const xml = (value: string) => value.replace(/[&<>"']/gu, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]!);
const VIEWS = [["spatial", "空间视图"], ["xy", "XY 投影"], ["xz", "XZ 投影"], ["yz", "YZ 投影"]] as const;

/** Render the exact saved vertices and faces. Never search for neighbors or infer a missing surface. */
export function renderReportLocalEnvironment(payload: unknown, title: string, options?: { width?: number; compact?: boolean }) {
  const saved = readSavedLocalEnvironment(payload);
  // A single export stays bounded. Larger results retain their complete original
  // file and interactive site list; no partial sheet is labelled as complete.
  if (!saved || !saved.siteResults.length || saved.siteResults.length > 16) return null;
  const width = typeof options?.width === "number" && Number.isFinite(options.width) ? Math.max(360, Math.min(1200, options.width)) : 920;
  const columns = width < 600 ? 1 : 2, margin = 20, gap = 24;
  const panel = (width - margin * 2 - gap * (columns - 1)) / columns;
  const font = width < 600 ? 14 : 15;
  const content: string[] = [];
  let cursor = 24;
  const text = (value: string, size = font, bold = false) => {
    for (const line of wrapReportSvgText(value, width - margin * 2, size)) {
      content.push(`<text x="${margin}" y="${cursor}" font-size="${size}"${bold ? ' font-weight="600"' : ""}>${xml(line)}</text>`);
      cursor += size + 8;
    }
  };
  if (!options?.compact) { text(title, 22, true); cursor += 8; }
  for (const site of saved.siteResults) {
    const { vertices, faces } = site.polyhedron;
    const classified = site.classification.status === "CLASSIFIED";
    const classification = classified ? geometryLabel(site.classification.referenceGeometryId) : classificationLabel(site.classification.status);
    content.push(`<g data-environment="${xml(site.environmentIdentity)}" data-site="${site.siteIndex}" data-classification-status="${site.classification.status}">`);
    text(`位点 ${site.siteIndex} · ${classification}`, 18, true);
    if (!classified && site.classification.referenceGeometryId) text(`最近参考：${geometryLabel(site.classification.referenceGeometryId)}`);
    const top = cursor;
    if (vertices.length) {
      for (const [index, [key, name]] of VIEWS.entries()) {
        const left = margin + (index % columns) * (panel + gap);
        const y = top + Math.floor(index / columns) * (panel + 36);
        const projection = projectSavedPolyhedron(vertices, faces, panel, panel, POLYHEDRON_VIEWS[key]);
        content.push(`<g data-polyhedron-view="${key}" transform="translate(${left} ${y})"><text x="0" y="16" font-size="${font}" font-weight="600">${name}</text><g transform="translate(0 26)">`);
        for (const face of projection.polygons) content.push(`<polygon data-face="${xml(face.faceIdentity)}" data-vertices="${xml(faces.find(item => item.faceIdentity === face.faceIdentity)!.vertexIdentities.join(" "))}" points="${face.points.map(point => `${point.x},${point.y}`).join(" ")}" fill="#08756c" fill-opacity="0.12" stroke="#3d7166" stroke-width="1.2"/>`);
        for (const point of projection.points) {
          const vertex = vertices[point.index];
          content.push(`<line data-neighbor="${xml(vertex.neighborIdentity)}" data-distance="${vertex.distance}" x1="${projection.center.x}" y1="${projection.center.y}" x2="${point.x}" y2="${point.y}" stroke="#52645c" stroke-width="1.2" stroke-dasharray="4 4"/>`);
        }
        for (const point of [...projection.points].sort((a, b) => a.depth - b.depth)) {
          const vertex = vertices[point.index];
          content.push(`<circle data-vertex="${xml(vertex.vertexIdentity)}" data-xyz="${vertex.relativeCartesian}" data-image="${vertex.periodicImage}" data-neighbor-site="${xml(vertex.neighborSiteId)}" cx="${point.x}" cy="${point.y}" r="6" fill="#dcebe5" stroke="#3d7166" stroke-width="1.5"><title>${xml(`顶点 ${point.index + 1} · 相对坐标 [${vertex.relativeCartesian}] Å · 周期偏移 [${vertex.periodicImage}] · 距离 ${vertex.distance} Å`)}</title></circle>`);
          if (vertices.length <= 12) content.push(`<text x="${point.x + 10}" y="${point.y - 9}" font-size="${font}">${point.index + 1}</text>`);
        }
        content.push(`<circle data-center="true" cx="${projection.center.x}" cy="${projection.center.y}" r="8" fill="#172b22"/><text x="${projection.center.x + 12}" y="${projection.center.y + 20}" font-size="${font}">中心</text>`);
        content.push(`<g transform="translate(44 ${panel - 44})">`);
        for (const axis of projection.axes) content.push(`<line x1="0" y1="0" x2="${axis.x}" y2="${axis.y}" stroke="#52645c"/><text x="${axis.x * 1.35}" y="${axis.y * 1.35 + 4}" font-size="12" text-anchor="middle">${axis.label}</text>`);
        content.push("</g></g></g>");
      }
      cursor = top + Math.ceil(VIEWS.length / columns) * (panel + 36) + 12;
    } else text("该位点没有已保存的近邻顶点。");
    text(`${vertices.length} 个近邻 · ${faces.length} 个已保存三角面`);
    if (site.polyhedron.status === "UNAVAILABLE") text(faceReason(site.polyhedron.unavailableReason));
    if (site.warnings.length) text("该位点附有限制说明，详见随附原始结果。");
    content.push("</g>");
    cursor += 20;
  }
  text(`${algorithmLabel(saved.sourceCoordination.algorithmId)} ${saved.sourceCoordination.algorithmVersion} · 几何近邻不代表确定的化学键。`);
  text("每个位点的四幅视图采用相同尺度的正交投影；不同位点独立适配。投影距离不等于三维距离。");
  if (saved.coverage.status !== "COMPLETE") text(`覆盖状态：${saved.coverage.evaluatedSites}/${saved.coverage.requestedSites} 个位点已评估，${saved.coverage.unavailableSites} 个不可用。`);
  if (saved.warnings.length) text("本次结果附有限制说明，详见随附原始结果。");
  return { pointCount: saved.siteResults.reduce((count, site) => count + site.polyhedron.vertices.length, 0), fit: "width" as const, axes: [],
    svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${cursor + 8}" role="img" aria-labelledby="title desc" data-source-coordination="${xml(saved.sourceCoordination.artifactId)}" data-source-checksum="${saved.sourceCoordination.artifactChecksum}" data-parameter-hash="${saved.parameterHash}"><title id="title">${xml(title)}</title><desc id="desc">保存近邻几何的空间、XY、XZ 和 YZ 正交投影。保留每个顶点的三维坐标、周期偏移与已保存的三角面。</desc><rect width="${width}" height="${cursor + 8}" fill="#fff"/><g font-family="system-ui,sans-serif" fill="#172b22">${content.join("")}</g></svg>` };
}
