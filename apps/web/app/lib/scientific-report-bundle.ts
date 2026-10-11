import { createHash } from "node:crypto";
import { zip } from "fflate/node";
import { buildScientificReportMarkdown, buildScientificReportReproducibilityManifest, dedupeReportSentences, humanizeScientificMethodSummary, type ScientificReportView } from "./scientific-report-api";
import { scientificNarrativeText } from "./scientific-narrative-text";
import { reportFindingPresentation } from "./scientific-report-findings";
import { readReportTablePreview, renderReportTableHtml, type ReportTableExport } from "./scientific-report-table-export";
import { reportLimitationPresentation } from "./scientific-limitation-text";
import { escapeReportHtml as html, renderScientificReportFigure } from "./scientific-report-figure";
import { renderReportVolume } from "./scientific-report-volume";
import { boundReportBasis, renderReportBasisHtml, renderReportInputsHtml } from "./scientific-report-basis";
import { readPlatformReferences, referenceSourcesHtml } from "./platform-reference";

const MAX_FILES = 32;
const MAX_BYTES = 32 * 1024 * 1024;
const MAX_FILE_BYTES = 8 * 1024 * 1024;
export class ReportBundleLimitError extends Error {}
type FileEntry = { path: string; sha256: string; bytes: number; artifact_id?: string; job_id?: string; derived_from?: string; point_count?: number };
type FigureEntry = { figureRef: string; caption: string; images: string[]; embeddedImages: string[]; mediumImages: string[]; compactImages: string[]; originals: string[]; fullWidthImages?: string[]; dataFiles?: string[]; note?: string };

/** Read only the report's bound artifacts; verify each payload before an archive can be returned. */
export async function buildScientificReportBundle(
  view: ScientificReportView,
  fetchArtifact: (jobId: string, artifactId: string) => Promise<Response>,
  signal: AbortSignal,
): Promise<Uint8Array> {
  const files: Record<string, Uint8Array> = {};
  const entries: FileEntry[] = [];
  const stored = new Map<string, { path: string; data: Uint8Array; contentType: string }>();
  let bytes = 0;
  const add = (path: string, data: Uint8Array, source: Partial<FileEntry> = {}) => {
    bytes += data.byteLength;
    if (bytes > MAX_BYTES) throw new ReportBundleLimitError();
    files[path] = data;
    entries.push({ path, sha256: createHash("sha256").update(data).digest("hex"), bytes: data.byteLength, ...source });
  };
  const save = async (jobId: string | null | undefined, artifactId: string, namedPath?: string) => {
    if (!jobId || !artifactId) throw new Error("Missing bound artifact identity");
    const key = JSON.stringify([jobId, artifactId]);
    const known = stored.get(key);
    if (known) return known;
    if (stored.size >= MAX_FILES) throw new ReportBundleLimitError();
    signal.throwIfAborted();
    const response = await fetchArtifact(jobId, artifactId);
    if (!response.ok || !response.body) throw new Error("Artifact unavailable");
    const declared = Number(response.headers.get("x-content-length-validated"));
    const checksum = response.headers.get("x-content-sha256") || "";
    if (!Number.isSafeInteger(declared) || declared <= 0 || !/^[a-f0-9]{64}$/u.test(checksum)) throw new Error("Unverified artifact");
    if (declared > MAX_FILE_BYTES || bytes + declared > MAX_BYTES) { await response.body.cancel(); throw new ReportBundleLimitError(); }
    const reader = response.body.getReader();
    const chunks: Uint8Array[] = [];
    let received = 0;
    try {
      for (;;) {
        signal.throwIfAborted();
        const chunk = await reader.read();
        if (chunk.done) break;
        received += chunk.value.byteLength;
        if (received > declared) throw new Error("Artifact byte mismatch");
        chunks.push(chunk.value);
      }
    } finally { await reader.cancel(); reader.releaseLock(); }
    const data = new Uint8Array(received);
    let offset = 0;
    for (const chunk of chunks) { data.set(chunk, offset); offset += chunk.byteLength; }
    if (received !== declared || createHash("sha256").update(data).digest("hex") !== checksum) throw new Error("Artifact checksum mismatch");
    const contentType = (response.headers.get("content-type") || "").split(";")[0];
    const extension = contentType === "application/json" ? "json" : contentType === "text/markdown" ? "md" : "bin";
    const path = namedPath || `artifacts/artifact-${String(stored.size + 1).padStart(3, "0")}.${extension}`;
    if (files[path]) throw new Error("Conflicting archive path");
    const item = { path, data, contentType };
    stored.set(key, item);
    add(path, data, { artifact_id: artifactId, job_id: jobId });
    return item;
  };
  const figures: FigureEntry[] = [];
  for (const [index, figure] of (view.report?.primary_figures || []).entries()) {
    const sources = (view.figure_sources || []).filter(item => item.figure_ref === figure.figure_ref);
    if (sources.length !== 1) throw new Error("Figure source is not uniquely bound");
    const source = sources[0];
    if (!source?.artifact_ids.length) throw new Error("Missing figure artifact");
    const item: FigureEntry = { figureRef: figure.figure_ref, caption: figure.caption, images: [], embeddedImages: [], mediumImages: [], compactImages: [], originals: [] };
    if (source.renderer === "volumetric") {
      const descriptors = source.artifacts || [];
      if (source.artifact_ids.length !== 1 || !descriptors.some(a => a.id === source.artifact_ids[0] && a.type === "volumetric_dataset_json")
        || descriptors.some(a => a.jobId !== source.job_id || !/^[A-Za-z0-9][A-Za-z0-9_.-]{0,159}$/u.test(a.name))) throw new Error("Invalid volume binding");
      for (const artifact of descriptors) {
        const saved = await save(artifact.jobId, artifact.id, `artifacts/volume-${index + 1}/${artifact.name}`);
        if (saved.data.byteLength !== artifact.sizeBytes || createHash("sha256").update(saved.data).digest("hex") !== artifact.sha256) throw new Error("Volume descriptor mismatch");
        item.originals.push(saved.path);
      }
      const rendered = await renderReportVolume(descriptors, async artifact => (await save(artifact.jobId, artifact.id)).data, signal);
      item.dataFiles = [];
      for (const [part, plane] of rendered.views.entries()) {
        const path = `figures/figure-${index + 1}-${part + 1}.svg`, compactPath = `figures/figure-${index + 1}-${part + 1}-small.svg`;
        const origin = await save(source.job_id, source.artifact_ids[0]);
        add(path, new TextEncoder().encode(plane.svg), { derived_from: origin.path, point_count: plane.sampleCount });
        add(compactPath, new TextEncoder().encode(plane.compactSvg), { derived_from: origin.path, point_count: plane.sampleCount });
        const dataPath = `figures/figure-${index + 1}-${part + 1}.json`;
        add(dataPath, new TextEncoder().encode(plane.data), { derived_from: origin.path, point_count: plane.sampleCount });
        item.dataFiles.push(dataPath);
        item.images.push(path); item.embeddedImages.push(path); item.mediumImages.push(path); item.compactImages.push(compactPath);
      }
      item.note = "图像取自各晶格轴中部的精确网格平面；对应数值保存在同名 JSON 中。等值面和交互式切片可在平台查看。";
      if (rendered.unsupportedFields.length) item.note += `以下字段暂不支持静态切片，原始载荷已附：${rendered.unsupportedFields.join("、")}。`;
      figures.push(item);
      continue;
    }
    for (const [part, id] of source.artifact_ids.entries()) {
      const artifact = await save(source.job_id, id);
      item.originals.push(artifact.path);
      const payload = artifact.contentType === "application/json" ? JSON.parse(new TextDecoder().decode(artifact.data)) : null;
      const rendered = renderScientificReportFigure(payload, scientificNarrativeText(figure.caption));
      if (rendered) {
        const path = `figures/figure-${index + 1}-${part + 1}.svg`;
        add(path, new TextEncoder().encode(rendered.svg), { derived_from: artifact.path, point_count: rendered.pointCount });
        item.images.push(path);
        if (rendered.fit === "width") (item.fullWidthImages ??= []).push(path);
        const embedded = renderScientificReportFigure(payload, scientificNarrativeText(figure.caption), { compact: true })!;
        const embeddedPath = `figures/figure-${index + 1}-${part + 1}-inline.svg`;
        add(embeddedPath, new TextEncoder().encode(embedded.svg), { derived_from: artifact.path, point_count: embedded.pointCount });
        item.embeddedImages.push(embeddedPath);
        const medium = renderScientificReportFigure(payload, scientificNarrativeText(figure.caption), { width: 640, compact: true }) || embedded;
        const mediumPath = `figures/figure-${index + 1}-${part + 1}-medium.svg`;
        add(mediumPath, new TextEncoder().encode(medium.svg), { derived_from: artifact.path, point_count: medium.pointCount });
        item.mediumImages.push(mediumPath);
        const compact = renderScientificReportFigure(payload, scientificNarrativeText(figure.caption), { width: 360, compact: true }) || embedded;
        const compactPath = `figures/figure-${index + 1}-${part + 1}-small.svg`;
        add(compactPath, new TextEncoder().encode(compact.svg), { derived_from: artifact.path, point_count: compact.pointCount });
        item.compactImages.push(compactPath);
      } else {
        item.note = "此图的类型或布局暂不支持静态图片导出；已附完整原始数据，可在平台查看。";
      }
    }
    figures.push(item);
  }
  // Include companion figure files even if an older report did not list them as primary figures.
  for (const figure of view.figure_sources || []) for (const id of figure.artifact_ids) await save(figure.job_id, id);
  const tables: ReportTableExport[] = [];
  for (const table of view.table_sources || []) for (const id of table.artifact_ids) {
    const saved = await save(table.job_id, id);
    if (tables.some(item => item.jobId === table.job_id && item.artifactId === id)) continue;
    let payload: unknown = null;
    if (saved.contentType === "application/json") {
      try { payload = JSON.parse(new TextDecoder().decode(saved.data)); } catch { /* The original remains available. */ }
    }
    tables.push({ jobId: table.job_id!, artifactId: id, preview: readReportTablePreview(payload) });
  }
  for (const file of view.file_sources || []) await save(file.job_id, file.artifact_id);
  const basis = boundReportBasis(view);
  for (const item of [...(basis?.facts || []), ...(basis?.evidence || [])]) {
    if (item.job_id && item.artifact_id) await save(item.job_id, item.artifact_id);
  }
  const encoder = new TextEncoder();
  const artifacts = entries.filter(entry => entry.artifact_id && entry.job_id).map(entry => ({ jobId: entry.job_id!, artifactId: entry.artifact_id!, path: entry.path }));
  add("report.md", encoder.encode(buildScientificReportMarkdown(view, { figures, artifacts, tables })));
  add("reproducibility.json", encoder.encode(buildScientificReportReproducibilityManifest(view)));
  if (basis) add("scientific-basis.json", encoder.encode(JSON.stringify(basis, null, 2) + "\n"));
  add("report.html", encoder.encode(bundleHtml(view, figures, entries, tables)));
  add("bundle-manifest.json", encoder.encode(JSON.stringify({
    schema_version: "mdi.report-bundle/1.0", report_id: view.report_id, snapshot_id: view.snapshot_id,
    rendering: "saved-scientific-svg/1.17", figures, files: [...entries],
  }, null, 2) + "\n"));
  signal.throwIfAborted();
  // fflate's Node worker compression is asynchronous and cancellable; no files or jobs are persisted.
  return new Promise((resolve, reject) => {
    const cancel = () => { terminate(); reject(signal.reason); };
    const terminate = zip(files, { level: 6 }, (error, data) => {
      signal.removeEventListener("abort", cancel);
      if (error) reject(error); else if (signal.aborted) reject(signal.reason); else resolve(data);
    });
    signal.addEventListener("abort", cancel, { once: true });
    if (signal.aborted) cancel();
  });
}

function bundleHtml(view: ScientificReportView, figures: FigureEntry[], entries: FileEntry[], tablePreviews: ReportTableExport[]): string {
  const report = view.report!;
  const list = (values: string[]) => `<ul>${values.map(value => `<li>${html(value)}</li>`).join("")}</ul>`;
  const packagedArtifacts = entries.filter(entry => entry.artifact_id && entry.job_id).map(entry => ({ jobId: entry.job_id!, artifactId: entry.artifact_id!, path: entry.path }));
  const references = (item: { fact_refs?: string[]; evidence_refs?: string[]; finding_refs?: string[] }) => renderReportBasisHtml(view, item, packagedArtifacts);
  const exactSources = (sources: NonNullable<ScientificReportView["table_sources"]>[number]["source_refs"]) =>
    (sources || []).map(source => `<li>${html(source.object_type)}<br>对象：<code>${html(source.object_id)}</code><br>版本：<code>${html(source.version_id)}</code></li>`).join("");
  const artifactLinks = (jobId: string | null | undefined, ids: string[], label: string) => `<ul class="file-links">${ids.map((id, index) => {
    const matches = entries.filter(entry => entry.job_id === jobId && entry.artifact_id === id);
    if (matches.length !== 1) throw new Error("Missing exact packaged artifact");
    const path = matches[0].path;
    return `<li><a href="${path}">${label}${ids.length > 1 ? ` ${index + 1}` : ""} · ${path.split(".").pop()!.toUpperCase()}</a></li>`;
  }).join("")}</ul>`;
  const sources = (view.viewer_sources || []).map(source => `<li>${html(source.display_name)} · ${html(source.object_type)}<details><summary>来源版本</summary><p>对象：<code>${html(source.object_id)}</code><br>版本：<code>${html(source.version_id)}</code></p></details></li>`).join("")
    + referenceSourcesHtml(readPlatformReferences(boundReportBasis(view)?.reference_sources));
  const figureHtml = figures.map((figure, index) => `<figure><figcaption>图 ${index + 1} · ${html(scientificNarrativeText(figure.caption))}</figcaption>${figure.images.map((path, part) => `<a class="figure-image"${figure.fullWidthImages?.includes(path) ? ' data-figure-fit="width"' : ""} href="${path}" aria-label="查看图 ${index + 1}-${part + 1} 的原尺寸" title="查看原尺寸图表"><picture><source media="(max-width:600px)" srcset="${figure.compactImages[part]}"><source media="(max-width:960px)" srcset="${figure.mediumImages[part]}"><img src="${figure.embeddedImages[part]}" alt="${html(scientificNarrativeText(figure.caption))}"></picture></a>`).join("")}${figure.note ? `<p>${html(figure.note)}</p>` : ""}<ul class="file-links">${figure.originals.map((path, part) => `<li><a href="${path}">原始图表数据${figure.originals.length > 1 ? ` ${part + 1}` : ""}</a></li>`).join("")}</ul>${figure.dataFiles?.length ? `<ul class="file-links">${figure.dataFiles.map((path, part) => `<li><a href="${path}">切片 ${part + 1} 原始数值</a></li>`).join("")}</ul>` : ""}${references(report.primary_figures[index])}</figure>`).join("");
  const tables = (view.table_sources || []).map((table, index) => `<article><h3>表 ${index + 1} · ${html(table.title || table.table_ref)}</h3>${table.artifact_ids.map((id, part) => renderReportTableHtml(tablePreviews.find(item => item.jobId === table.job_id && item.artifactId === id)?.preview ?? null, `${table.title || table.table_ref}${table.artifact_ids.length > 1 ? ` · ${part + 1}` : ""}`)).join("")}${table.artifact_ids.length ? artifactLinks(table.job_id, table.artifact_ids, "原始数据表") : "<p>此表未绑定可导出的数据文件。</p>"}<details><summary>来源详情</summary><p>表格：<code>${html(table.table_ref)}</code>${table.job_id ? `<br>任务：<code>${html(table.job_id)}</code>` : ""}</p>${list(table.artifact_ids)}<ul>${exactSources(table.source_refs)}</ul></details></article>`).join("");
  const resultFiles = (view.file_sources || []).map(file => `<article><h3>${html(file.title)}</h3>${artifactLinks(file.job_id, [file.artifact_id], "原始结果文件")}<details><summary>来源详情</summary><p>产物：<code>${html(file.artifact_id)}</code><br>任务：<code>${html(file.job_id!)}</code></p></details></article>`).join("");
  const sections: Array<{ id: string; title: string; body: string }> = [];
  const section = (id: string, title: string, body: string) => { if (body) sections.push({ id, title, body }); };
  const narrative = (id: string, title: string, item: typeof report.discussion) => {
    if (item?.text) section(id, title, `<p>${html(scientificNarrativeText(item.text))}</p>${references(item)}`);
  };
  section("summary", "摘要", `<p>${html(scientificNarrativeText(report.summary))}</p><details><summary>研究问题</summary><p>${html(report.research_question)}</p></details>`);
  section("methods", "数据与方法", `<p>${html(dedupeReportSentences(humanizeScientificMethodSummary(report.method_summary)))}</p>${sources ? `<ul>${sources}</ul>` : ""}${renderReportInputsHtml(view)}`);
  if (report.main_findings.length) {
    const presentation = reportFindingPresentation(report.main_findings);
    const shared = presentation.sharedLimitations.length ? `<p role="note" aria-label="共同限制">共同限制：${html(scientificNarrativeText(presentation.sharedLimitations.join("")))}</p>` : "";
    section("findings", "主要发现", `${shared}<ol>${report.main_findings.map((item, index) => `<li><p>${html(scientificNarrativeText(presentation.statements[index]))}</p>${references(item)}</li>`).join("")}</ol>`);
  }
  section("figures", "主要图表", figureHtml);
  section("tables", "主要数据表", tables);
  narrative("discussion", "科学讨论", report.discussion);
  if (report.limitations.length) section("limitations", "限制与适用范围", list(reportLimitationPresentation(report.limitations).map(item => item.statement)));
  narrative("conclusion", "结论", report.conclusion);
  narrative("next-steps", "后续工作建议", report.next_steps);
  if (report.supporting_results.length) section("supporting", "支持结果", `<ul>${report.supporting_results.map(item => `<li>${html(scientificNarrativeText(item.description))}<details><summary>结果引用</summary><p>${html(item.result_item_ref)}</p></details></li>`).join("")}</ul>`);
  section("files", "结果文件", resultFiles);
  section("reproducibility", "复现信息", `<p>${html(scientificNarrativeText(report.reproducibility_summary))}</p>${references({ evidence_refs: report.evidence_refs })}`);
  const attachments = entries.filter(entry => entry.artifact_id).map(entry => `<li><a href="${entry.path}">${entry.path}</a><br><small>${html(entry.artifact_id!)} · ${html(entry.job_id!)}</small></li>`).join("");
  const basisStyle = ".report-basis-group{margin:8px 0 16px}.report-basis-values{font-size:14px}.report-basis-values>div{display:grid;grid-template-columns:minmax(0,1fr) minmax(100px,1fr);gap:16px;padding:8px 0;border-bottom:1px solid #dfe5e1}.report-basis-values dt{font-weight:400}.report-basis-values dd{color:#17211e;text-align:right;font-variant-numeric:tabular-nums;white-space:pre-wrap;overflow-wrap:anywhere}.report-basis details dl>div{margin:12px 0}"
    + ".report-basis-comparison{width:100%;border-collapse:collapse;margin:8px 0 16px;font-size:14px}.report-basis-comparison th,.report-basis-comparison td{padding:12px 0;border-bottom:1px solid #dfe5e1;text-align:left;overflow-wrap:anywhere;font-weight:400}.report-basis-comparison th{padding-right:16px}.report-basis-comparison td,.report-basis-comparison th:last-child{padding-right:0;text-align:right}.report-basis-comparison td{min-width:100px;color:#17211e;font-variant-numeric:tabular-nums}"
    + ".report-basis .file-links{font-size:14px}.report-inputs>div+div{margin-top:24px}.report-input-parameters{font-size:14px;min-width:0}.report-input-parameters>div{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2fr);gap:12px;padding:8px 0;border-bottom:1px solid #dfe5e1}.report-input-parameters dt{font-weight:400}.report-input-parameters dd{min-width:0;color:#17211e;font-variant-numeric:tabular-nums}.report-input-parameters pre{margin:0;max-height:360px;overflow:auto;padding:8px;background:#f4f6f5}.report-input-parameters pre:focus-visible{outline:2px solid #075a53;outline-offset:3px}@media(max-width:600px){#findings>ol{padding-inline-start:24px}}@media(max-width:480px){.report-input-parameters>div{grid-template-columns:minmax(0,1fr);gap:4px}}";
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' file:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'"><title>${html(report.title)}</title><style>${basisStyle}</style>
<style>.report-table-scroll{max-width:100%;overflow-x:auto;margin:16px 0;border:1px solid #cbd4cf}.report-table-scroll:focus-visible{outline:2px solid #075a53;outline-offset:3px}.report-table-scroll table{border-collapse:collapse;min-width:100%;font-size:14px;font-variant-numeric:tabular-nums}.report-table-scroll caption{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}.report-table-scroll th,.report-table-scroll td{padding:10px 12px;border-bottom:1px solid #dfe5e1;text-align:left;vertical-align:top;min-width:60px;max-width:280px;white-space:pre-wrap;overflow-wrap:anywhere}.report-table-scroll thead th{background:#f4f6f5;font-weight:600}.report-table-scroll tbody th{font-weight:500}.report-table-scroll .table-number{text-align:right;white-space:nowrap}.report-table-scroll tbody th,.report-table-scroll thead th:first-child{position:sticky;left:0;background:#fff;z-index:1}.report-table-scroll thead th:first-child{background:#f4f6f5}.report-table-note{color:#44514b;font-size:14px;margin:8px 0}@media print{.report-table-scroll{overflow:visible;border:0}.report-table-scroll table{width:100%;table-layout:fixed;font-size:11px}.report-table-scroll th,.report-table-scroll td{min-width:0;padding:4px;max-width:none}.report-table-scroll thead{display:table-header-group}.report-table-scroll tr{break-inside:avoid}.report-table-scroll tbody th,.report-table-scroll thead th:first-child{position:static}}body{margin:0;background:#f4f6f5;color:#17211e;font:16px/1.65 system-ui,sans-serif}main{box-sizing:border-box;max-width:960px;margin:32px auto;padding:48px;background:#fff;overflow-wrap:anywhere}h1{font-size:30px;line-height:1.3}h2{font-size:21px;margin:32px 0 12px}h3{font-size:17px;margin:0 0 8px}p,li{white-space:pre-line}li{margin:8px 0}a{color:#075a53;text-underline-offset:3px}a:focus-visible,summary:focus-visible{outline:2px solid #075a53;outline-offset:4px}nav,.document-links{display:flex;flex-wrap:wrap;gap:0 20px}nav{border-block:1px solid #cbd4cf;padding:8px 0;margin:24px 0}nav a,.document-links a,.file-links a{display:inline-flex;align-items:center;min-height:44px}section{scroll-margin-top:24px}section:focus{outline:none}.figure-image{display:block;width:100%;max-width:100%;margin:16px auto;cursor:zoom-in}picture{display:block}img{display:block;width:100%;max-width:100%;height:auto;max-height:80vh;max-height:80svh;object-fit:contain}.figure-image[data-figure-fit="width"] img{max-height:none}figure{margin:32px 0}figcaption{font-weight:600}small,code{overflow-wrap:anywhere}.file-links{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:0 20px}.file-links li{margin:0}article{padding:24px 0;border-bottom:1px solid #cbd4cf}article:first-of-type{padding-top:8px}details{margin:8px 0;color:#44514b}summary{cursor:pointer;min-height:44px;align-content:center}details p{margin:8px 0}dt{font-weight:600}dd{margin:0}dd ul{padding-left:24px}footer{margin-top:40px;color:#44514b}@media(max-width:600px){main{margin:0;padding:24px}h1{font-size:24px}nav,.document-links{gap:0 16px}}@media print{body{background:#fff}main{padding:0;margin:0;max-width:none}figure{break-inside:avoid}img{max-height:none}nav,.document-links{display:none}}</style></head><body><main>
<header><h1>${html(report.title)}</h1><p>第 ${view.revision_number || 1} 版 · ${html(view.created_at)}</p><div class="document-links"><a href="report.md">Markdown 正文</a>${boundReportBasis(view) ? '<a href="scientific-basis.json">引用事实</a>' : ""}<a href="reproducibility.json">复现清单</a><a href="bundle-manifest.json">文件校验清单</a></div></header>
<nav aria-label="报告章节">${sections.map(item => `<a href="#${item.id}">${item.title}</a>`).join("")}</nav>
${sections.map(item => `<section id="${item.id}" tabindex="-1" aria-labelledby="${item.id}-heading"><h2 id="${item.id}-heading">${item.title}</h2>${item.body}</section>`).join("\n")}
<details><summary>随附原始结果文件 · ${entries.filter(entry => entry.artifact_id).length}</summary><ul>${attachments}</ul></details>
<footer><details><summary>报告与快照</summary><p>报告：${html(view.report_id)}<br>快照：${html(view.snapshot_id)}</p></details></footer>
</main></body></html>`;
}
