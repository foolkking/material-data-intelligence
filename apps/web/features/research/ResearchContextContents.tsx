"use client";

import { useId, useState } from "react";
import Link from "next/link";
import type { Agent2ContextManifest, Agent2ContextManifestItem, Agent2ContextManifestRecord, Agent2ContextResultSource, Agent2ScientificObjectRef } from "../../app/lib/agent2-research-api";
import styles from "./ResearchContextContents.module.css";
import { presentationMetricTitle, presentationMetricUnit } from "../../app/lib/scientific-presentation";
import { readPlatformReferences } from "../../app/lib/platform-reference";
import { PlatformReferenceSources } from "../../shared/ui/PlatformReferenceSources";
import { ProjectInputDetails, projectInputOrigin, projectParameterInputs } from "../../shared/ui/ProjectInputDetails";
import { projectScienceNames } from "../../app/lib/project-science-labels";

type RecordValue = Record<string, unknown>;
const record = (value: unknown): RecordValue => value && typeof value === "object" && !Array.isArray(value) ? value as RecordValue : {};
const list = (value: unknown): RecordValue[] => Array.isArray(value) ? value.map(record) : [];
const text = (value: unknown): string => typeof value === "string" ? value.trim() : "";
const strings = (value: unknown): string[] => Array.isArray(value) ? value.map(text).filter(Boolean) : [];
const unique = (values: string[]) => [...new Set(values.filter(Boolean))];
const cleanSummary = (value: unknown) => text(value).replace(/\s*\[source=[^\]\s;]+; freshness=[A-Z_]+\]\s*$/u, "");
const stageNames: Record<string, string> = { ORCHESTRATOR: "理解问题", PLANNER: "规划分析", INTERPRETER: "解释结果", REPORT: "撰写报告", DATA: "读取数据" };
const actionNames: Record<string, string> = { ANSWER: "回答问题", CLARIFY: "确认需求", ANALYZE: "运行分析", CONTINUE_ANALYSIS: "继续分析", INTERPRET_RESULT: "解释结果", QUERY_DATA: "查询数据", MANAGE_DATA: "管理数据", OPEN_OBJECT: "打开数据", CREATE_REPORT: "生成报告", UPDATE_REPORT: "更新报告", EXPORT: "导出" };
const resultNames: Record<string, string> = {
  ...projectScienceNames,
  "diffraction.xrd.theoretical": "理论 XRD", "diffraction.xrd.comparison": "实验与理论 XRD 对比",
  "structure.summary": "晶体结构摘要", "structure.viewer_3d": "三维晶体结构", "structure.rdf": "径向分布函数（RDF）",
  "trajectory.viewer_3d": "原子轨迹", "trajectory.rdf": "轨迹径向分布函数（RDF）", "trajectory.msd": "均方位移（MSD）", "trajectory.diffusion": "扩散系数",
  "electronic.band": "电子能带", "electronic.dos": "电子态密度", "phonon.band": "声子色散", "phonon.dos": "声子态密度", "volumetric.data": "体数据场",
};
const valueText = (value: unknown): string => value === undefined || value === null ? "" : typeof value === "string" ? value : JSON.stringify(value);
const contentText = (value: unknown): string => typeof value === "string" ? value : text(record(value).statement) || text(record(value).message) || text(record(value).description);
const contentList = (value: unknown): string[] => Array.isArray(value) ? value.map(contentText).filter(Boolean) : [];
function resultTitle(value: RecordValue, kind: "result" | "figure" | "table") {
  const type = text(value[`${kind}_type`]);
  return text(value.title) || (type ? `${resultNames[type] || type} ${kind === "figure" ? "图谱" : kind === "table" ? "数据表" : "结果"}` : "");
}
const capabilityNames: Record<string, string> = {
  ...projectScienceNames,
  "reference.periodic_table": "元素周期表", "reference.compare_elements": "元素参考性质比较",
  "diffraction.theoretical_xrd": "理论 XRD 图谱", "diffraction.generate_theoretical_pattern": "理论 XRD 图谱", "diffraction.experimental_theoretical_comparison": "实验与理论 XRD 对比", "diffraction.compare_experimental_theoretical": "实验与理论 XRD 对比",
  "structure.inspect": "晶体结构摘要", "structure.inspect_view": "三维晶体结构", "structure.viewer_scene": "三维晶体结构", "structure.compute_rdf": "结构径向分布函数", "structure.inspect_brillouin_zone": "布里渊区与高对称路径",
  "structure.inspect_coordination": "配位环境分析", "structure.coordination_analysis": "配位环境分析", "structure.inspect_coordination_hist": "配位数分布", "structure.inspect_coordination_crystalnn": "CrystalNN 配位环境", "structure.inspect_coordination_voronoi": "Voronoi 配位环境",
  "trajectory.inspect_view": "原子轨迹展示", "trajectory.viewer_scene": "原子轨迹展示", "trajectory.compute_msd": "均方位移（MSD）", "trajectory.compute_rdf": "轨迹径向分布函数", "trajectory.estimate_diffusion": "扩散系数估计",
  "electronic.inspect_band": "电子能带", "electronic.inspect_dos": "电子态密度", "phonon.inspect_band": "声子色散", "phonon.inspect_dos": "声子态密度", "phonon.compose_band_dos": "声子色散与态密度", "phonon.animate_mode": "声子振动模式",
  "volumetric.inspect": "体数据场", "volumetric.data": "体数据场", "data.analyze_composition": "元素组成与化学体系", "data.composition_analysis": "元素组成与化学体系", "data.analyze_table": "数值属性、分布与相关性", "data.table_analysis": "数值属性、分布与相关性", "data.explore_composition_space": "材料组成空间", "data.composition_space": "材料组成空间", "data.explore_materials": "材料数据概览", "data.materials_explorer": "材料数据概览",
  "ml.evaluate_regression": "回归结果评估", "ml.evaluate_classification": "分类结果评估", "ml.evaluate_uncertainty": "预测不确定性评估",
};
const selectionNames: Record<string, string> = { site_index: "位点", species: "元素", frame_index: "帧", atom_index: "原子", band_id: "能带", kpoint_id: "k 点", spin_channel: "自旋", energy: "能量", sample_ref: "样本", mode_index: "模式", qpoint_index: "q 点", frequency: "频率", channel_index: "通道" };

function selectionText(value: RecordValue) {
  if (text(value.display_label)) return text(value.display_label);
  const locator = record(value.semantic_locator);
  return Object.entries(selectionNames).flatMap(([key, label]) => {
    const item = locator[key];
    return typeof item === "string" || typeof item === "number" ? [`${label} ${item}`] : [];
  }).join(" · ");
}

function exactResultReference(items: Agent2ContextManifestItem[]): string | undefined {
  if (!items.length || items.some(item => item.authorization_checked !== true ||
      !item.result_ref || item.server_side_source_identity !== item.result_ref)) return undefined;
  const references = unique(items.map(item => item.result_ref || ""));
  return references.length === 1 ? references[0] : undefined;
}

type ContextResult = { title: string; question: string; resultRef?: string; resultItemId?: string; resultType?: string; sourceLabels?: string[] };

function sameNameSources(source: Agent2ScientificObjectRef, peers: Agent2ScientificObjectRef[]) {
  return peers.filter(peer => text(peer.display_name) === text(source.display_name) && (peer.object_id !== source.object_id || peer.version_id !== source.version_id));
}

function sourceVersionLabel(source: Agent2ScientificObjectRef, peers: Agent2ScientificObjectRef[]) {
  const others = sameNameSources(source, peers);
  const length = [8, 12, 36].find(size => others.every(peer => peer.version_id.slice(0, size) !== source.version_id.slice(0, size))) || 36;
  return `版本 ${source.version_id.slice(0, length)}${others.some(peer => peer.version_id === source.version_id) ? ` · ${source.object_id}` : ""}`;
}

function sourceName(source: Agent2ScientificObjectRef, peers: Agent2ScientificObjectRef[]) {
  const title = text(source.display_name) || "未记录数据名称";
  return sameNameSources(source, peers).length ? `${title} · ${sourceVersionLabel(source, peers)}` : title;
}

function exactItemSources(item: { scientific_object_refs: Agent2ScientificObjectRef[] }, projectId: string) {
  const sources = new Map<string, Agent2ScientificObjectRef>();
  for (const source of item.scientific_object_refs) {
    if (source.project_id !== projectId || !source.object_id || !source.version_id) return [];
    const key = `${source.object_id}:${source.version_id}`;
    const previous = sources.get(key);
    if (previous && (text(previous.display_name) !== text(source.display_name) || previous.object_type !== source.object_type)) return [];
    sources.set(key, source);
  }
  return [...sources.values()];
}

function ContextResultRow({ title, href, sources, sourcePeers, projectId, question, onOpenResult }: {
  title: string; href?: string; sources: Agent2ScientificObjectRef[]; sourcePeers: Agent2ScientificObjectRef[]; projectId: string; question: string; onOpenResult?: () => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const sourceId = useId();
  return <li>
    <div className={styles.resultHeader}>
      {href ? <Link className={styles.resultLink} href={href} aria-label={`打开结果：${title}`} prefetch={false} scroll={false}
        onClick={event => { if (!event.defaultPrevented && event.button === 0 && !event.metaKey && !event.ctrlKey && !event.altKey && !event.shiftKey) onOpenResult?.(); }}
      >{title}</Link> : <strong>{title}</strong>}
      {sources.length ? <button type="button" className="product-link-button" aria-expanded={expanded} aria-controls={sourceId}
        aria-label={`查看${title}的来源版本`} onClick={() => setExpanded(value => !value)}>来源</button> : null}
    </div>
    {expanded ? <ul id={sourceId} className={styles.resultSources}>{sources.map(source => <li key={`${source.object_id}:${source.version_id}`}>
      <Link href={`/projects/${encodeURIComponent(projectId)}/data?object=${encodeURIComponent(source.object_id)}&version=${encodeURIComponent(source.version_id)}`}
        title={`版本 ${source.version_id}`}>{source.display_name || "查看来源数据"} · {sourceVersionLabel(source, sourcePeers)}</Link>
    </li>)}</ul> : null}
    {question ? <TextDisclosure title="对应问题">{question}</TextDisclosure> : null}
  </li>;
}

export function contextContentView(manifest: Agent2ContextManifest) {
  const input = record(manifest.serialized_input);
  const context = record(input.research_context);
  const result = record(input.result);
  const objects = new Map<string, { title: string; objectId?: string; versionId?: string; selections: string[]; items: Agent2ContextManifestItem[] }>();
  for (const item of manifest.included_items) {
    if (!["SCIENTIFIC_OBJECT", "SCIENTIFIC_SELECTION"].includes(item.kind)) continue;
    const content = record(item.serialized_representation);
    const ref = Object.keys(record(content.object_ref)).length ? record(content.object_ref) : content;
    const key = item.exact_object_id && item.exact_object_version_id ? `${item.exact_object_id}:${item.exact_object_version_id}` : item.item_id;
    const existing = objects.get(key);
    const title = text(ref.display_name) || text(content.display_name);
    const selection = selectionText(content);
    if (existing) {
      if (title) existing.title = title;
      existing.selections = unique([...existing.selections, selection]);
      existing.items.push(item);
    } else objects.set(key, { title: title || "未记录数据名称", objectId: item.exact_object_id || undefined, versionId: item.exact_object_version_id || undefined, selections: selection ? [selection] : [], items: [item] });
  }
  // Match only explicit provider references; never infer source identity by type or position.
  for (const source of [...list(context.objects), ...list(input.source_bindings)]) {
    const matches = [...objects.values()].filter((entry) => entry.items.some((item) => item.provider_opaque_ref === source.ref_key));
    const match = matches.length === 1 ? matches[0] : undefined;
    if (match && match.title === "未记录数据名称" && text(source.display_name)) match.title = text(source.display_name);
  }
  const resultItems = manifest.included_items.filter(item => item.kind === "SCIENTIFIC_RESULT");
  const namedResult = (value: RecordValue, resultRef?: string, resultItemId?: string): ContextResult => ({
    title: text(value.title) || cleanSummary(value.summary) || resultTitle(value, "result") || text(value.research_question) || "未记录结果名称",
    question: text(value.research_question), ...(resultRef ? { resultRef } : {}),
    ...(resultItemId ? { resultItemId, resultType: text(value.result_type), sourceLabels: strings(value.source_labels) } : {}),
  });
  const results = [
    ...list(context.results).map(value => namedResult(value, exactResultReference(resultItems.filter(item =>
      Boolean(text(value.ref_key)) && item.provider_opaque_ref === text(value.ref_key))))),
    ...list(result.result_items).map(value => {
      const matches = resultItems.filter(item => Boolean(text(value.id)) &&
        strings(record(item.serialized_representation).result_item_ids).includes(text(value.id)));
      return namedResult(value, exactResultReference(matches), text(value.id));
    }),
  ];
  if (!results.length) for (const item of manifest.included_items.filter((item) => item.kind === "SCIENTIFIC_RESULT")) {
    const value = record(item.serialized_representation);
    results.push(namedResult({ ...value, title: text(value.title) || cleanSummary(value.summary) || strings(value.output_object_types).join("、") || "已引用的科学结果" }, exactResultReference([item])));
  }
  const facts = [context.relevant_findings, input.facts, result.facts].flatMap((values, scope) => list(values).map((fact, index) => ({
    label: presentationMetricTitle(text(fact.display_label) || text(fact.predicate) || text(fact.label) || text(fact.name) || text(fact.fact_key) || "已记录数值"),
    value: text(fact.summary) || valueText(fact.value),
    unit: presentationMetricUnit(text(fact.unit)),
    predicate: text(fact.predicate),
    group: `${scope}:${text(fact.subject_ref) || `unbound-${index}`}`,
  }))).filter((fact) => fact.value);
  // Subject references are scoped to one saved input array. Missing references never merge.
  const factGroups = [...new Set(facts.map((fact) => fact.group))].map((group) => {
    const members = facts.filter((fact) => fact.group === group);
    const angles = members.filter((fact) => fact.predicate === "xrd.peak.two_theta");
    const elements = members.filter(fact => fact.predicate === "reference.element.symbol");
    return { key: group, title: angles.length === 1 ? `衍射峰 · 2θ ${angles[0].value}${angles[0].unit ? ` ${angles[0].unit}` : ""}` : elements.length === 1 ? elements[0].value : "", facts: members };
  });
  const constraints = unique([
    ...strings(context.explicit_constraints),
    ...strings(context.unresolved_questions),
    ...manifest.included_items.filter((item) => ["USER_CONSTRAINT", "RESEARCH_GOAL"].includes(item.kind)).map((item) => text(item.serialized_representation)),
  ]);
  return {
    input, objects: [...objects.values()], results, facts, factGroups, constraints,
    question: text(input.user_message) || text(input.research_objective) || text(input.research_question) || text(input.question) || text(context.current_user_message),
    messages: list(context.recent_conversation).filter((message) => text(message.content)),
    candidates: list(input.candidates), requirements: list(input.available_requirement_ids),
    actions: strings(input.allowed_actions).map((action) => actionNames[action] || action),
    methods: list(result.methods),
    inputProvenance: record(result.provenance),
    visuals: [...list(result.figures).map((item) => resultTitle(item, "figure")), ...list(result.tables).map((item) => resultTitle(item, "table"))].filter(Boolean),
    findings: unique([...contentList(record(input.interpretation).findings), ...contentList(record(input.interpretation).primary_findings), ...contentList(record(input.interpretation).supporting_findings)]),
    narrative: ["answer_lead", "discussion", "conclusion"].map((key) => contentText(record(input.interpretation)[key])).filter(Boolean),
    limitations: unique([...contentList(result.limitations), ...contentList(record(input.interpretation).limitations)]),
    warnings: contentList(result.warnings),
    structuredConstraints: Array.isArray(input.explicit_constraints) ? input.explicit_constraints : [],
    literature: [...list(context.literature_evidence), ...list(input.literature_sources), ...list(input.literature_evidence)],
    referenceSources: [...new Map([record(result.provenance).reference_sources, ...list(input.candidates).map(candidate => candidate.reference_sources)]
      .flatMap(readPlatformReferences).map(source => [`${source.referenceId}:${source.version}:${source.contentHash}`, source])).values()],
  };
}

function TextDisclosure({ title, children }: { title: string; children: string }) {
  return <details className={styles.textDisclosure}><summary>{title}</summary><p>{children}</p></details>;
}

export function ResearchContextContents({ manifest, manifests, projectId, toolLabel, resultSources = [], onOpenResult }: {
  manifest: Agent2ContextManifest; manifests: Agent2ContextManifestRecord[]; projectId: string; toolLabel: (id: string, fallback: string) => string;
  resultSources?: Agent2ContextResultSource[]; onOpenResult?: () => void;
}) {
  const [selected, setSelected] = useState(manifest.context_manifest_id);
  const records = [...new Map([...manifests.map((entry) => entry.manifest), manifest].map((entry) => [entry.context_manifest_id, entry])).values()];
  const active = records.find((entry) => entry.context_manifest_id === selected) || manifest;
  const view = contextContentView(active);
  const parameterInputs = projectParameterInputs(view.inputProvenance);
  const inputTools = new Set(parameterInputs.map(item => item.tool_id));
  const resultMethods = view.methods.filter(method => !parameterInputs.some(input => {
    const parameters = Object.entries(record(method.parameters));
    const resolved = record(input.resolved_parameters);
    return input.tool_id === (text(method.tool_id) || text(method.capability_id)) && parameters.length > 0
      && parameters.every(([key, value]) => Object.hasOwn(resolved, key) && JSON.stringify(resolved[key]) === JSON.stringify(value));
  }));
  const resultRows = view.results.map(result => {
    const locations = resultSources.filter(source => source.result_snapshot_id === result.resultRef && source.project_id === projectId);
    const location = locations.length === 1 ? locations[0] : undefined;
    const items = location?.result_items?.filter(item => item.id === result.resultItemId) || [];
    const sources = items.length === 1 && (!result.resultType || items[0].result_type === result.resultType)
      ? exactItemSources(items[0], projectId) : [];
    const query = location ? new URLSearchParams({turn:location.research_turn_id}) : undefined;
    if (query && result.resultRef && result.resultItemId) { query.set("resultSnapshot", result.resultRef); query.set("resultItem", result.resultItemId); }
    return {result, sources, href:location ? `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(location.research_session_id)}?${query}` : undefined};
  });
  const resultSourcePeers = resultRows.flatMap(row => row.sources);
  const hasContent = Boolean(view.question) || inputTools.size > 0 || [view.objects, view.results, view.facts, view.messages, view.constraints, view.structuredConstraints, view.actions, view.requirements, view.candidates, view.methods, view.visuals, view.findings, view.narrative, view.limitations, view.warnings, view.literature, view.referenceSources].some((items) => items.length > 0);
  const namedTool = (id: string, fallback: string) => capabilityNames[id] || toolLabel(id, fallback);
  const [showAllData, setShowAllData] = useState(false);
  return <div className={styles.root}>
    {records.length > 1 ? <label className={styles.stage}><span>调用阶段</span><select aria-label="调用阶段" value={active.context_manifest_id} onChange={(event) => { setSelected(event.target.value); setShowAllData(false); }}>
      {records.map((entry, index) => <option key={entry.context_manifest_id} value={entry.context_manifest_id}>{index + 1}. {stageNames[entry.operation] || entry.operation}</option>)}
    </select></label> : null}
    {active.input_state === "PROSPECTIVE" ? <p className={styles.state}>调用前预览</p> : null}
    {view.question ? <TextDisclosure title="本次问题">{view.question}</TextDisclosure> : null}
    {projectInputOrigin(view.inputProvenance) ? <ProjectInputDetails provenance={view.inputProvenance} /> : <PlatformReferenceSources sources={view.referenceSources} />}
    {view.objects.length ? <section aria-label="使用的数据"><h3>数据与选择</h3><ul className={styles.sources}>
      {(showAllData ? view.objects : view.objects.slice(0, 8)).map((source, index) => <li key={`${source.objectId}:${source.versionId}:${index}`}>
        <strong>{source.title}</strong>
        {source.selections.map((selection) => <p key={selection}>{selection}</p>)}
        {source.objectId && source.versionId ? <Link href={`/projects/${encodeURIComponent(projectId)}/data?object=${encodeURIComponent(source.objectId)}&version=${encodeURIComponent(source.versionId)}`}>打开数据</Link> : null}
      </li>)}
    </ul>{view.objects.length > 8 ? <button type="button" className="product-link-button" onClick={() => setShowAllData((value) => !value)}>{showAllData ? "收起数据" : `查看全部 ${view.objects.length} 份数据`}</button> : null}</section> : null}
    {view.results.length ? <section><h3>引用结果</h3><ul className={styles.sources}>{resultRows.map(({result, sources, href}, index) => {
      const names = sources.length ? sources.map(source => sourceName(source, resultSourcePeers)) : result.sourceLabels || [];
      const title = names.length ? `${names.join("、")} · ${resultNames[result.resultType || ""] || result.title}` : result.title;
      return <ContextResultRow key={`${active.context_manifest_id}:${result.resultRef}:${result.resultItemId}:${index}`}
        title={title} href={href} sources={sources} sourcePeers={resultSourcePeers} projectId={projectId} question={result.question} onOpenResult={onOpenResult} />;
    })}</ul></section> : null}
    {view.facts.length ? <details><summary>输入数值 · {view.facts.length}</summary>{view.factGroups.map((group) => <div className={styles.factGroup} key={group.key}>{group.title ? <h4>{group.title}</h4> : null}<dl className={styles.facts}>{group.facts.map((fact, index) => <div key={index}><dt>{fact.label}</dt><dd>{fact.value}{fact.unit ? ` ${fact.unit}` : ""}</dd></div>)}</dl></div>)}</details> : null}
    {view.messages.length ? <details><summary>历史消息 · {view.messages.length}</summary><ol className={styles.messages}>{view.messages.map((message, index) => <li key={index}><strong>{text(message.role).toUpperCase() === "USER" ? "你" : "研究助手"}</strong><p>{text(message.content)}</p></li>)}</ol></details> : null}
    {view.constraints.length || view.structuredConstraints.length ? <details><summary>目标与约束</summary>{view.constraints.map((constraint) => <p key={constraint}>{constraint}</p>)}{view.structuredConstraints.length ? <pre>{JSON.stringify(view.structuredConstraints, null, 2)}</pre> : null}</details> : null}
    {view.actions.length ? <details><summary>模型可选操作 · {view.actions.length}</summary><ul>{view.actions.map((action) => <li key={action}>{action}</li>)}</ul></details> : null}
    {view.requirements.length ? <details><summary>可选分析能力 · {view.requirements.length}</summary><ul className={styles.sources}>{view.requirements.map((capability, index) => <li key={index}><strong>{namedTool(text(capability.requirement_id), text(capability.display_name) || text(capability.requirement_id))}</strong><details><summary>参数要求</summary><pre>{JSON.stringify(capability.constraint_schema, null, 2)}</pre></details></li>)}</ul></details> : null}
    {view.candidates.length ? <details><summary>提供给模型的工具选项 · {view.candidates.length}</summary><ul className={styles.sources}>{view.candidates.map((candidate, index) => <li key={index}><strong>{namedTool(text(candidate.capability_id), text(candidate.display_name) || text(candidate.capability_id))}</strong><details><summary>输入与输出</summary><pre>{JSON.stringify({ inputs: candidate.input_slots, outputs: candidate.output_slots, constraints: candidate.known_limitations }, null, 2)}</pre></details></li>)}</ul></details> : null}
    {resultMethods.length ? <details><summary>结果中的工具与参数 · {resultMethods.length}</summary><ul className={styles.sources}>{resultMethods.map((method, index) => <li key={index}><strong>{namedTool(text(method.tool_id) || text(method.capability_id), text(method.tool_id) || text(method.capability_id))}</strong>{Object.keys(record(method.parameters)).length ? <pre>{JSON.stringify(method.parameters, null, 2)}</pre> : null}</li>)}</ul></details> : null}
    {view.visuals.length ? <details><summary>图表 · {view.visuals.length}</summary><ul>{view.visuals.map((title, index) => <li key={index}>{title}</li>)}</ul></details> : null}
    {view.findings.length ? <details><summary>已保存的结论 · {view.findings.length}</summary>{view.findings.map((finding, index) => <p key={index}>{finding}</p>)}</details> : null}
    {view.narrative.length ? <details><summary>已有回答</summary>{view.narrative.map((paragraph, index) => <p key={index}>{paragraph}</p>)}</details> : null}
    {view.limitations.length ? <details><summary>科学限制</summary>{view.limitations.map((limitation, index) => <p key={index}>{limitation}</p>)}</details> : null}
    {view.warnings.length ? <details><summary>数据警告</summary>{view.warnings.map((warning, index) => <p key={index}>{warning}</p>)}</details> : null}
    {view.literature.length ? <details><summary>参考文献 · {view.literature.length}</summary><ul>{view.literature.map((item, index) => <li key={index}>{text(item.title) || text(item.display_label) || "未记录文献标题"}</li>)}</ul></details> : null}
    {!hasContent ? <p>这条记录没有保存可展示的输入内容。</p> : null}
    <details className={styles.technical} aria-label="上下文技术详情"><summary>技术详情</summary>
      <p>这里只展示已保存的输入记录；未保存的系统提示和修复消息不在其中。</p>
      <dl className={styles.facts}><div><dt>提示模板</dt><dd>{active.prompt_template_version || "未记录"}</dd></div><div><dt>输入估算 / 预算</dt><dd>{active.estimated_input_tokens} / {active.input_budget} tokens</dd></div></dl>
      <details><summary>来源与处理记录</summary><pre>{JSON.stringify({ items: active.included_items, excluded: active.excluded_item_details || active.excluded_items, compaction: active.compaction_state, truncation: active.truncation_state }, null, 2)}</pre></details>
      {active.serialized_input ? <details><summary>已保存的模型输入</summary><pre>{JSON.stringify(active.serialized_input, null, 2)}</pre></details> : null}
    </details>
  </div>;
}
