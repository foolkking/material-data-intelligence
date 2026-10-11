import { presentationMetricTitle, presentationMetricUnit } from "./scientific-presentation";
import { tableFactLabels } from "./scientific-table-labels";
import { readPlatformReferences, type PlatformReference } from "./platform-reference";
import type { ScientificReportBasisFact, ScientificReportBasisLocation, ScientificReportBasisSource, ScientificReportView } from "./scientific-report-api";
import { inputOriginNames, projectScienceNames } from "./project-science-labels";
import { projectParameterInputs, projectParameterRows, type ProjectParameterRow } from "./project-input";

export type ReportBasisReferences = { fact_refs?: string[]; evidence_refs?: string[]; finding_refs?: string[] };
export type ReportBasisFact = ScientificReportBasisFact & { title: string; value: string; sources: ScientificReportBasisSource[]; referenceSources: PlatformReference[] };
export type ReportBasisFile = ScientificReportBasisLocation & { title: string };

function uniqueById<T>(items: T[], id: (item: T) => string): Map<string, T> {
  const counts = new Map<string, number>();
  items.forEach(item => counts.set(id(item), (counts.get(id(item)) || 0) + 1));
  return new Map(items.filter(item => counts.get(id(item)) === 1).map(item => [id(item), item]));
}

export function boundReportBasis(view: ScientificReportView) {
  const basis = view.scientific_basis;
  return basis && basis.project_id === view.project_id && basis.result_snapshot_id === view.scientific_result_snapshot_id ? basis : null;
}

export function reportParameterInputs(view: ScientificReportView) {
  const basis = boundReportBasis(view);
  const inputs = projectParameterInputs({ execution_scope: "PROJECT", input_origin: basis?.input_origin, parameter_inputs: basis?.parameter_inputs });
  const locations = [...(basis?.facts || []), ...(basis?.evidence || [])];
  return inputs.filter(input => locations.some(location => location.source_refs.length === 0
    && location.job_id && location.artifact_id && location.tool_call_id === input.tool_call_id
    && location.tool_id === input.tool_id && location.input_origin === input.input_origin && location.input_hash === input.content_hash));
}

function exactSources(view: ScientificReportView, location: ScientificReportBasisLocation): ScientificReportBasisSource[] {
  const refs = location.source_refs;
  if (!Array.isArray(refs) || refs.some(ref => !ref.object_id || !ref.version_id || !ref.object_type)) return [];
  const unique = uniqueById(refs, ref => JSON.stringify([ref.object_id, ref.version_id]));
  if (unique.size !== refs.length) return [];
  if (refs.some(ref => {
    const matches = (view.viewer_sources || []).filter(source => source.object_id === ref.object_id && source.version_id === ref.version_id);
    return matches.length > 1 || (matches.length === 1 && matches[0].object_type !== ref.object_type);
  })) return [];
  return refs.map(ref => {
    const current = (view.viewer_sources || []).filter(source => source.object_id === ref.object_id && source.version_id === ref.version_id);
    // A saved label survives a removed source. Current metadata must belong
    // to this exact version and type; a name or array position is insufficient.
    return { ...ref, display_name: ref.display_name || (current.length === 1 && current[0].object_type === ref.object_type ? current[0].display_name : null) };
  });
}

export function reportBasisSourceLabel(source: ScientificReportBasisSource): string {
  return source.display_name?.trim() || "来源数据";
}

export function reportBasisSourceDisplayLabel(source: ScientificReportBasisSource, sources: ScientificReportBasisSource[]): string {
  const label = reportBasisSourceLabel(source);
  const sameName = sources.filter(candidate => reportBasisSourceLabel(candidate) === label);
  if (sameName.length < 2) return label;
  const versionsUnique = new Set(sameName.map(candidate => candidate.version_id)).size === sameName.length;
  const identity = (item: ScientificReportBasisSource) => versionsUnique ? item.version_id : `${item.object_id}/${item.version_id}`;
  const value = identity(source);
  let length = Math.min(8, value.length);
  while (length < value.length && sameName.some(candidate => identity(candidate) !== value && identity(candidate).slice(0, length) === value.slice(0, length))) length += 1;
  return `${label} · ${value.slice(0, length)}`;
}

function fileTitle(view: ScientificReportView, item: ScientificReportBasisLocation): string {
  const figures = (view.figure_sources || []).filter(source => source.job_id === item.job_id && source.artifact_ids.includes(item.artifact_id || ""));
  if (figures.length === 1) {
    const matches = view.report?.primary_figures.filter(figure => figure.figure_ref === figures[0].figure_ref) || [];
    if (matches.length === 1) return `图表 · ${matches[0].caption}`;
  }
  const tables = (view.table_sources || []).filter(source => source.job_id === item.job_id && source.artifact_ids.includes(item.artifact_id || ""));
  if (tables.length === 1 && tables[0].title) return `数据表 · ${tables[0].title}`;
  return item.artifact_name || (item.tool_id ? `工具调用 · ${item.tool_id}` : "来源文件");
}

/** Join citations within this report's saved snapshot; never choose a first match. */
export function resolveReportBasis(view: ScientificReportView, references: ReportBasisReferences) {
  const basis = boundReportBasis(view);
  const referenceSources = readPlatformReferences(basis?.reference_sources);
  const exactReferences = (location: ScientificReportBasisLocation) => {
    const ids = location.reference_source_ids;
    if (!ids?.length || location.source_refs.length || !location.job_id || !location.artifact_id || !location.tool_call_id
      || ids.some(id => !referenceSources.some(source => source.referenceId === id))) return [];
    return referenceSources.filter(source => ids.includes(source.referenceId));
  };
  const factsById = uniqueById(basis?.facts || [], fact => fact.fact_id);
  const evidenceById = uniqueById(basis?.evidence || [], evidence => evidence.evidence_id);
  const labels = tableFactLabels([...factsById.values()].map(fact => ({
    factId: fact.fact_id, predicate: fact.predicate, subjectRef: fact.subject_ref, value: fact.value_text,
    source: { artifactId: fact.artifact_id, scientificObjectRef: fact.source_refs.length === 1
      ? { objectId: fact.source_refs[0].object_id, versionId: fact.source_refs[0].version_id } : undefined },
  })));
  const missingFacts: string[] = [], missingEvidence: string[] = [];
  const facts = [...new Set(references.fact_refs || [])].flatMap(id => {
    const fact = factsById.get(id);
    if (!fact || typeof fact.value_text !== "string") { missingFacts.push(id); return []; }
    const unit = fact.unit ? presentationMetricUnit(fact.unit) : "";
    return [{ ...fact, title: labels.get(id) || presentationMetricTitle(fact.predicate),
      value: `${fact.value_text}${unit ? ` ${unit}` : ""}`, sources: exactSources(view, fact), referenceSources: exactReferences(fact) }];
  });
  const evidence = [...new Set(references.evidence_refs || [])].flatMap(id => {
    const item = evidenceById.get(id);
    if (!item) { missingEvidence.push(id); return []; }
    return [{ ...item, source_refs: exactSources(view, item) }];
  });
  const groups = new Map<string, { key: string; sources: ScientificReportBasisSource[]; referenceSources: PlatformReference[]; inputTitle?: string; facts: ReportBasisFact[] }>();
  for (const fact of facts) {
    const inputName = !fact.source_refs.length && fact.job_id && fact.artifact_id && fact.tool_call_id
      && projectScienceNames[fact.tool_id || ""] && ["USER_PARAMETERS", "USER_TEXT_DATA", "IDEAL_MODEL"].includes(fact.input_origin || "")
      && /^[a-f0-9]{64}$/.test(fact.input_hash || "")
      ? inputOriginNames[fact.input_origin || ""] : undefined;
    const inputTitle = inputName ? [projectScienceNames[fact.tool_id || ""], inputName].filter(Boolean).join(" · ") : undefined;
    const key = JSON.stringify([fact.sources.map(source => [source.object_id, source.version_id]).sort(), fact.referenceSources.map(source => source.referenceId), inputTitle ? [fact.tool_call_id, fact.input_hash] : null]);
    const group = groups.get(key) || { key, sources: fact.sources, referenceSources: fact.referenceSources, inputTitle, facts: [] };
    group.facts.push(fact); groups.set(key, group);
  }
  const files = new Map<string, ReportBasisFile>();
  for (const location of [...facts, ...evidence]) {
    if (!location.artifact_id || !location.job_id) continue;
    const key = JSON.stringify([location.job_id, location.artifact_id]);
    files.set(key, { ...location, title: fileTitle(view, location) });
  }
  const sources = new Map<string, ScientificReportBasisSource>();
  for (const source of [...facts.flatMap(fact => fact.sources), ...evidence.flatMap(item => item.source_refs)]) {
    sources.set(JSON.stringify([source.object_id, source.version_id]), source);
  }
  const grouped = [...groups.values()];
  const comparisonTitle = grouped.length > 1 && grouped.every(group => group.sources.length === 1 && group.facts.length === 1
    && group.facts[0].predicate === grouped[0].facts[0].predicate && group.facts[0].title === grouped[0].facts[0].title
    && group.facts[0].unit === grouped[0].facts[0].unit && group.facts[0].value.length <= 240) ? grouped[0].facts[0].title : null;
  return { facts, evidence, groups: grouped, files: [...files.values()], sources: [...sources.values()], referenceSources, missingFacts, missingEvidence, comparisonTitle };
}

export function reportBasisGroupLabel(group: { sources: ScientificReportBasisSource[]; referenceSources: PlatformReference[]; inputTitle?: string }, sources: ScientificReportBasisSource[]): string {
  return group.sources.map(source => reportBasisSourceDisplayLabel(source, sources)).join("、")
    || [group.inputTitle, ...group.referenceSources.map(source => `${source.name} · ${source.version}`)].filter(Boolean).join("；") || "来源未能核对";
}

export function reportBasisMissingText(basis: ReturnType<typeof resolveReportBasis>): string | null {
  const parts = [basis.missingFacts.length ? `${basis.missingFacts.length} 项引用事实` : "", basis.missingEvidence.length ? `${basis.missingEvidence.length} 项来源记录` : ""].filter(Boolean);
  return parts.length ? `${parts.join("、")}暂不可读取。` : null;
}

export type ReportBasisArtifact = { jobId: string; artifactId: string; path: string };
const escapeHtml = (value: string) => value.replace(/[&<>"']/gu, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]!);
const markdown = (value: string) => value.replace(/[&<>|\\`*_\[\]]/gu, character => `&#${character.charCodeAt(0)};`).replace(/\r\n?|\n/gu, "<br>");

export function renderReportInputsMarkdown(view: ScientificReportView): string {
  const inputs = reportParameterInputs(view);
  if (!inputs.length) return "";
  const rows = (items: ProjectParameterRow[]): string => items.map(row => {
    if (row.kind === "functions") return row.groups.map((group, index) => `**${markdown(row.label)} ${index + 1}**\n\n${rows(group)}`).join("\n\n");
    if (row.kind === "text") {
      const fence = "`".repeat(Math.max(3, ...[...row.text.matchAll(/`+/gu)].map(match => match[0].length + 1)));
      return `**${markdown(row.label)}**\n\n${fence}text\n${row.text}\n${fence}`;
    }
    return `- ${markdown(row.label)}：${markdown(row.text)}`;
  }).join("\n\n");
  return ["### 输入参数与原始数据", ...inputs.map(input => [
    `#### ${projectScienceNames[input.tool_id]} · ${inputOriginNames[input.input_origin]}`,
    rows(projectParameterRows(input.resolved_parameters)),
    `<details>\n<summary>输入标识</summary>\n\nSHA256: ${input.content_hash}\n\n</details>`,
  ].join("\n\n"))].join("\n\n");
}

export function renderReportInputsHtml(view: ScientificReportView): string {
  const inputs = reportParameterInputs(view);
  if (!inputs.length) return "";
  const rows = (items: ProjectParameterRow[]): string => `<dl class="report-input-parameters">${items.map(row =>
    `<div><dt>${escapeHtml(row.label)}</dt><dd>${row.kind === "functions" ? row.groups.map(rows).join("")
      : row.kind === "text" ? `<pre tabindex="0" aria-label="原始输入表格">${escapeHtml(row.text)}</pre>`
        : escapeHtml(row.text)}</dd></div>`).join("")}</dl>`;
  return `<details class="report-inputs"><summary>输入参数与原始数据</summary>${inputs.map(input =>
    `<div><strong>${escapeHtml(projectScienceNames[input.tool_id])} · ${escapeHtml(inputOriginNames[input.input_origin])}</strong>${rows(projectParameterRows(input.resolved_parameters))}<details><summary>输入标识</summary><code>${input.content_hash}</code></details></div>`).join("")}</details>`;
}
const artifactPath = (files: ReportBasisArtifact[], location: ScientificReportBasisLocation) => {
  const matches = files.filter(file => file.jobId === location.job_id && file.artifactId === location.artifact_id);
  return matches.length === 1 ? matches[0].path : null;
};

export function renderReportBasisMarkdown(view: ScientificReportView, references: ReportBasisReferences, files: ReportBasisArtifact[] = []): string {
  const basis = resolveReportBasis(view, references), lines: string[] = [];
  if (basis.comparisonTitle) {
    lines.push("", `| 材料 | ${markdown(basis.comparisonTitle)} |`, "| --- | --- |",
      ...basis.groups.map(group => `| ${markdown(reportBasisSourceDisplayLabel(group.sources[0], basis.sources))} | ${markdown(group.facts[0].value)} |`));
  }
  for (const group of basis.comparisonTitle ? [] : basis.groups) {
    lines.push("", `**${markdown(reportBasisGroupLabel(group, basis.sources))}**`, "",
      "| 指标 | 保存值 |", "| --- | --- |", ...group.facts.map(fact => `| ${markdown(fact.title)} | ${markdown(fact.value)} |`));
  }
  lines.push("");
  for (const file of basis.files) {
    const path = artifactPath(files, file);
    lines.push(path ? `- [${markdown(file.title)}](${path})` : `- 来源文件：${markdown(file.title)}`);
  }
  const missing = reportBasisMissingText(basis);
  if (missing) lines.push(missing);
  if (!references.fact_refs?.length && !references.evidence_refs?.length && !references.finding_refs?.length) return "";
  lines.push("", "<details>", "<summary>引用与版本</summary>", "");
  basis.sources.forEach(source => lines.push(`- ${markdown(reportBasisSourceLabel(source))} · version ${markdown(source.version_id)} · object ${markdown(source.object_id)}`));
  if (references.finding_refs?.length) lines.push(`Finding refs: ${references.finding_refs.map(markdown).join(", ")}`);
  if (references.fact_refs?.length) lines.push(`Fact refs: ${references.fact_refs.map(markdown).join(", ")}`);
  if (references.evidence_refs?.length) lines.push(`Evidence refs: ${references.evidence_refs.map(markdown).join(", ")}`);
  for (const fact of basis.facts) {
    lines.push(`- ${markdown(fact.fact_id)} · ${markdown(fact.subject_ref)}${fact.artifact_locator ? ` · ${markdown(fact.artifact_locator)}` : ""}${fact.uncertainty_text ? ` · 不确定度 ${markdown(fact.uncertainty_text)}` : ""}`);
  }
  lines.push("", "</details>", "");
  return lines.join("\n");
}

export function renderReportBasisHtml(view: ScientificReportView, references: ReportBasisReferences, files: ReportBasisArtifact[] = []): string {
  if (!references.fact_refs?.length && !references.evidence_refs?.length && !references.finding_refs?.length) return "";
  const basis = resolveReportBasis(view, references);
  const facts = basis.comparisonTitle
    ? `<table class="report-basis-comparison"><thead><tr><th scope="col">材料</th><th scope="col">${escapeHtml(basis.comparisonTitle)}</th></tr></thead><tbody>${basis.groups.map(group => `<tr><th scope="row">${escapeHtml(reportBasisSourceDisplayLabel(group.sources[0], basis.sources))}</th><td>${escapeHtml(group.facts[0].value)}</td></tr>`).join("")}</tbody></table>`
    : basis.groups.map(group => `<div class="report-basis-group"><strong>${escapeHtml(reportBasisGroupLabel(group, basis.sources))}</strong><dl class="report-basis-values">${group.facts.map(fact => `<div><dt>${escapeHtml(fact.title)}</dt><dd>${escapeHtml(fact.value)}</dd></div>`).join("")}</dl></div>`).join("");
  const links = basis.files.map(file => {
    const path = artifactPath(files, file);
    return path ? `<li><a href="${escapeHtml(path)}">${escapeHtml(file.title)}</a></li>` : `<li>${escapeHtml(file.title)}</li>`;
  }).join("");
  const identities = [["发现引用", references.finding_refs], ["事实引用", references.fact_refs], ["证据引用", references.evidence_refs]] as const;
  const sources = basis.sources.map(source => `<div><dt>${escapeHtml(reportBasisSourceLabel(source))}</dt><dd>对象：${escapeHtml(source.object_id)}<br>版本：${escapeHtml(source.version_id)}</dd></div>`).join("");
  const locators = basis.facts.map(fact => `<div><dt>${escapeHtml(fact.title)}</dt><dd>${escapeHtml(fact.fact_id)}<br>${escapeHtml(fact.subject_ref)}${fact.artifact_locator ? `<br>${escapeHtml(fact.artifact_locator)}` : ""}${fact.uncertainty_text ? `<br>不确定度：${escapeHtml(fact.uncertainty_text)}` : ""}</dd></div>`).join("");
  const missing = reportBasisMissingText(basis);
  return `<details class="report-basis"><summary>科学依据</summary>${facts}${links ? `<ul class="file-links">${links}</ul>` : ""}${missing ? `<p>${missing}</p>` : ""}<details><summary>引用与版本</summary><dl>${sources}${identities.filter(([, refs]) => refs?.length).map(([label, refs]) => `<div><dt>${label}</dt><dd>${refs!.map(escapeHtml).join("<br>")}</dd></div>`).join("")}${locators}</dl></details></details>`;
}
