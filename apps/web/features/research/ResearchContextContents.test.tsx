import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import type { Agent2ContextManifest, Agent2ContextManifestItem, Agent2ContextResultSource, Agent2ScientificObjectRef } from "../../app/lib/agent2-research-api";
import { contextContentView, ResearchContextContents } from "./ResearchContextContents";
import referenceFigure from "../../scientific-viewers/workspace/element-reference-comparison.fixture.json";
import { readSavedElementReference } from "../../scientific-viewers/workspace/saved-element-reference";

function source(id: string, version: string, selection = false): Agent2ContextManifestItem {
  return { item_id: id, kind: selection ? "SCIENTIFIC_SELECTION" : "SCIENTIFIC_OBJECT", exact_object_id: "object-a", exact_object_version_id: version,
    provider_opaque_ref: id, serialized_representation: selection ? { object_ref: { display_name: "合成三斜晶胞" }, display_label: "Li · 位点 0", semantic_locator: { site_index: 0 } } : { display_name: "合成三斜晶胞" },
  } as Agent2ContextManifestItem;
}
function manifest(patch: Partial<Agent2ContextManifest> = {}): Agent2ContextManifest {
  return { context_manifest_id: "m1", project_id: "p", research_session_id: "s", research_turn_id: "t", operation: "ORCHESTRATOR", input_state: "ACTUAL", included_items: [source("object_1", "v1"), source("selection_1", "v1", true)], excluded_items: [],
    serialized_input: { user_message: "计算理论 XRD", research_context: { results: [{ ref_key: "result_1", research_question: "查看上次衍射图", summary: "理论 XRD 图谱 [source=result-original; freshness=CURRENT]" }], recent_conversation: [{ role: "USER", content: "使用原始晶胞" }] } }, ...patch,
  } as Agent2ContextManifest;
}
const toolLabel = (_id: string, fallback: string) => fallback;

it("names parameter result types and scientific units without rewriting recorded inputs", () => {
  const value = manifest({ serialized_input: { result: {
    result_items: [{ id: "units", result_type: "reference.convert_units" }, { id: "curve", result_type: "generation.function_curve" }],
    facts: [{ predicate: "calculation.output_value", value: 5, unit: "angstrom", subject_ref: "units:row:0" }],
  } } });
  const before = JSON.stringify(value), view = contextContentView(value);
  expect(view.results.map(item => item.title)).toEqual(["单位换算 结果", "函数曲线 结果"]);
  expect(view.facts[0]).toMatchObject({ value: "5", unit: "Å" });
  expect(JSON.stringify(value)).toBe(before);
});

it.each(["tool_id", "capability_id"])("shows supplied parameters once while keeping other result methods available (%s)", async methodKey => {
  const value = manifest({ included_items: [], serialized_input: { result: {
    provenance: { execution_scope: "PROJECT", input_origin: "USER_PARAMETERS", parameter_inputs: [{
      tool_call_id: "units", tool_id: "reference.convert_units", input_origin: "USER_PARAMETERS", content_hash: "c".repeat(64),
      resolved_parameters: { values: [25], from_unit: "degC", to_unit: "K" },
    }] },
    methods: [{ [methodKey]: "reference.convert_units", parameters: { values: [25], from_unit: "degC", to_unit: "K" } },
      { tool_id: "reference.compare_elements", parameters: { elements: ["C", "Si"] } }],
  } } });
  render(<ResearchContextContents manifest={value} manifests={[]} projectId="p" toolLabel={toolLabel} />);
  await userEvent.click(screen.getByText("输入参数与原始数据"));
  expect(screen.getByText("单位换算 · 输入参数")).toBeVisible();
  expect(screen.getByText("°C")).toBeVisible();
  await userEvent.click(screen.getByText("结果中的工具与参数 · 1"));
  expect(screen.getByText("元素参考性质比较")).toBeVisible();
  expect(screen.queryByText("单位换算", { exact: true })).not.toBeInTheDocument();
});

it("retains a method with different parameters even when its tool has another disclosed input", () => {
  const value = manifest({ serialized_input: { result: {
    provenance: { execution_scope: "PROJECT", input_origin: "USER_PARAMETERS", parameter_inputs: [{
      tool_call_id: "units", tool_id: "reference.convert_units", input_origin: "USER_PARAMETERS", content_hash: "c".repeat(64),
      resolved_parameters: { values: [25], from_unit: "degC", to_unit: "K" },
    }] },
    methods: [{ capability_id: "reference.convert_units", parameters: { values: [50], from_unit: "degC", to_unit: "K" } }],
  } } });
  render(<ResearchContextContents manifest={value} manifests={[]} projectId="p" toolLabel={toolLabel} />);
  expect(screen.getByText("结果中的工具与参数 · 1")).toBeInTheDocument();
});

it("discloses the reference actually supplied to the planner or interpreter", async () => {
  const sources = readSavedElementReference(referenceFigure)!.references;
  const value = manifest({ included_items: [], serialized_input: { research_question: "比较元素性质",
    candidates: [{ capability_id: "reference.compare_elements", reference_sources: sources }],
    result: { provenance: { input_origin: "PLATFORM_REFERENCE", reference_sources: sources } },
  } });
  expect(contextContentView(value).referenceSources).toHaveLength(1);
  render(<ResearchContextContents manifest={value} manifests={[]} projectId="p" toolLabel={toolLabel} />);
  const summary = screen.getByText("参考资料 · 1");
  expect(summary.closest("details")).not.toHaveAttribute("open");
  await userEvent.click(summary);
  expect(screen.getByRole("link", { name: "ASE element symbols and Cordero covalent radii" })).toHaveAttribute("href", "https://ase-lib.org/ase/data.html");
  expect(screen.queryByRole("link", { name: "打开数据" })).not.toBeInTheDocument();
});
const resultItem = (reference: string, snapshot: string, patch: Partial<Agent2ContextManifestItem> = {}) => ({
  item_id: reference, kind: "SCIENTIFIC_RESULT", provider_opaque_ref: reference,
  result_ref: snapshot, server_side_source_identity: snapshot, authorization_checked: true, ...patch,
}) as Agent2ContextManifestItem;
const resultSource = (snapshot: string, turn = "original-turn", session = "original-session") => ({
  result_snapshot_id: snapshot, project_id: "p", research_session_id: session, research_turn_id: turn,
});

it("groups duplicate source and selection while keeping distinct exact versions separate", () => {
  const value = manifest();
  value.included_items.push(source("object_2", "v2"));
  const before = JSON.stringify(value);
  const view = contextContentView(value);
  expect(view.objects).toHaveLength(2);
  expect(view.objects[0]).toMatchObject({ title: "合成三斜晶胞", versionId: "v1", selections: ["Li · 位点 0"] });
  expect(view.objects[1].versionId).toBe("v2");
  expect(view.results[0]).toEqual({ title: "理论 XRD 图谱", question: "查看上次衍射图" });
  expect(JSON.stringify(value)).toBe(before);
});

it("does not name an unknown source from an unrelated object of the same type", () => {
  const value = manifest({ included_items: [{ ...source("missing", "v1"), serialized_representation: {} }], serialized_input: { research_context: { objects: [{ ref_key: "different", display_name: "其他材料", object_type: "structure.crystal" }] } } });
  expect(contextContentView(value).objects[0].title).toBe("未记录数据名称");
});

it("shows named source, selection and result without permanent provenance descriptions", async () => {
  render(<ResearchContextContents manifest={manifest()} manifests={[]} projectId="p" toolLabel={toolLabel} />);
  expect(screen.getByText("合成三斜晶胞")).toBeVisible();
  expect(screen.getByText("Li · 位点 0")).toBeVisible();
  expect(screen.getByText("理论 XRD 图谱")).toBeVisible();
  expect(screen.getByRole("link", { name: "打开数据" })).toHaveAttribute("href", "/projects/p/data?object=object-a&version=v1");
  expect(screen.queryByText("不作为独立科学依据")).not.toBeInTheDocument();
  expect(screen.getByText("技术详情").closest("details")).not.toHaveAttribute("open");
  const user = userEvent.setup();
  await user.click(screen.getByText("历史消息 · 1"));
  expect(screen.getByText("使用原始晶胞")).toBeVisible();
});

it("opens each referenced result by its exact recorded identity rather than title or list order", () => {
  const value = manifest({ included_items: [resultItem("result_2", "s2"), resultItem("result_1", "s1")],
    serialized_input: { research_context: { results: [{ ref_key: "result_1", title: "Si RDF" }, { ref_key: "result_2", title: "Cu RDF" }] } } });
  const before = JSON.stringify(value);
  const open = vi.fn();
  render(<ResearchContextContents manifest={value} manifests={[]} projectId="p" toolLabel={toolLabel}
    resultSources={[resultSource("s2", "cu-turn", "cu-session"), resultSource("s1", "si-turn", "si-session")]} onOpenResult={open} />);
  const silicon = screen.getByRole("link", { name: "打开结果：Si RDF" });
  expect(silicon).toHaveAttribute("href", "/projects/p/research/si-session?turn=si-turn");
  expect(screen.getByRole("link", { name: "打开结果：Cu RDF" })).toHaveAttribute("href", "/projects/p/research/cu-session?turn=cu-turn");
  const preventNativeNavigation = (event: Event) => event.preventDefault();
  document.addEventListener("click", preventNativeNavigation);
  try {
    fireEvent.click(silicon, { ctrlKey: true });
    expect(open).not.toHaveBeenCalled();
    fireEvent.click(silicon);
    expect(open).toHaveBeenCalledOnce();
  } finally { document.removeEventListener("click", preventNativeNavigation); }
  expect(JSON.stringify(value)).toBe(before);
});

it.each([
  { included_items: [] },
  { included_items: [resultItem("unrelated", "s1")] },
  { included_items: [resultItem("result_1", "s1", { authorization_checked: false })] },
  { included_items: [resultItem("result_1", "s1", { server_side_source_identity: "different" })] },
  { included_items: [resultItem("result_1", "s1"), resultItem("result_1", "s2")] },
])("retains the result title without guessing unverified or conflicting navigation (%j)", ({ included_items }) => {
  render(<ResearchContextContents manifest={manifest({ included_items })} manifests={[]} projectId="p" toolLabel={toolLabel}
    resultSources={[resultSource("s1"), resultSource("s2")]} />);
  expect(screen.getByText("理论 XRD 图谱")).toBeVisible();
  expect(screen.queryByRole("link", { name: /打开结果/ })).not.toBeInTheDocument();
});

it("keeps identical provider aliases isolated when changing recorded stages", async () => {
  const first = manifest({ included_items: [resultItem("result_1", "s1")] });
  const second = manifest({ context_manifest_id: "m2", operation: "INTERPRETER", included_items: [resultItem("result_1", "s2", {
    serialized_representation: { result_item_ids: ["rdf-copper"] },
  })], serialized_input: { result: { result_items: [{ id: "rdf-copper", title: "Cu RDF" }, { id: "unknown", title: "Unbound result" }] } } });
  render(<ResearchContextContents manifest={first} manifests={[{ operation: "INTERPRETER", manifest: second }]} projectId="p" toolLabel={toolLabel}
    resultSources={[resultSource("s1", "first"), resultSource("s2", "second")]} />);
  expect(screen.getByRole("link", { name: "打开结果：理论 XRD 图谱" })).toHaveAttribute("href", "/projects/p/research/original-session?turn=first");
  await userEvent.setup().selectOptions(screen.getByRole("combobox", { name: "调用阶段" }), "m2");
  expect(screen.getByRole("link", { name: "打开结果：Cu RDF" })).toHaveAttribute("href", "/projects/p/research/original-session?turn=second&resultSnapshot=s2&resultItem=rdf-copper");
  expect(screen.queryByRole("link", { name: "打开结果：Unbound result" })).not.toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "打开结果：理论 XRD 图谱" })).not.toBeInTheDocument();
});

it("keeps historical result metadata readable when its source is absent or belongs to another project", () => {
  const value = manifest({ included_items: [resultItem("result_1", "s1")] });
  render(<ResearchContextContents manifest={value} manifests={[]} projectId="p" toolLabel={toolLabel}
    resultSources={[{ ...resultSource("s1"), project_id: "other" }]} />);
  expect(screen.getByText("理论 XRD 图谱")).toBeVisible();
  expect(screen.queryByRole("link", { name: /打开结果/ })).not.toBeInTheDocument();
});

const resultRef = (name: string, version = `${name}-version`): Agent2ScientificObjectRef => ({
  project_id: "p", object_id: `${name}-object`, version_id: version, object_type: "structure.crystal", display_name: name,
});
const sourceItem = (id: string, source: Agent2ScientificObjectRef) => ({
  id, title: "structure.rdf 结果", result_type: "structure.rdf", scientific_object_refs: [source],
});
function interpretationManifest(ids: string[], labels?: string[]) {
  return manifest({ operation: "INTERPRETER", included_items: [resultItem("result_1", "s1", {
    serialized_representation: { result_item_ids: ids },
  })], serialized_input: { result: { result_items: ids.map(id => ({ id, result_type: "structure.rdf", ...(labels ? { source_labels: labels } : {}) })) } } });
}

it("names same-type materials and opens their exact result items independently of metadata order", async () => {
  const value = interpretationManifest(["si", "cu", "nacl"]);
  const location = { ...resultSource("s1"), result_items: [sourceItem("nacl", resultRef("NaCl.cif")), sourceItem("si", resultRef("Si.cif")), sourceItem("cu", resultRef("Cu.cif"))] };
  const before = JSON.stringify({ value, location });
  render(<ResearchContextContents manifest={value} manifests={[]} projectId="p" toolLabel={toolLabel} resultSources={[location]} />);
  for (const [id, name] of [["si", "Si"], ["cu", "Cu"], ["nacl", "NaCl"]]) {
    expect(screen.getByRole("link", { name: `打开结果：${name}.cif · 径向分布函数（RDF）` }))
      .toHaveAttribute("href", `/projects/p/research/original-session?turn=original-turn&resultSnapshot=s1&resultItem=${id}`);
  }
  expect(screen.queryByRole("link", { name: "Cu.cif · 版本 Cu.cif-v" })).not.toBeInTheDocument();
  const button = screen.getByRole("button", { name: "查看Cu.cif · 径向分布函数（RDF）的来源版本" });
  await userEvent.setup().click(button);
  expect(button).toHaveAttribute("aria-expanded", "true");
  expect(screen.getByRole("link", { name: "Cu.cif · 版本 Cu.cif-v" })).toHaveAttribute("href", "/projects/p/data?object=Cu.cif-object&version=Cu.cif-version");
  expect(JSON.stringify({ value, location })).toBe(before);
});

it("keeps same-name versions distinct even when their first eight identity characters match", async () => {
  const versions = ["abcdef01-1234-4567-8901-123456789012", "abcdef01-9876-4567-8901-123456789012"];
  render(<ResearchContextContents manifest={interpretationManifest(["old", "new"])} manifests={[]} projectId="p" toolLabel={toolLabel}
    resultSources={[{ ...resultSource("s1"), result_items: versions.map((version, index) => sourceItem(index ? "new" : "old", resultRef("sample.cif", version))) }]} />);
  const links = screen.getAllByRole("link", { name: /打开结果：sample.cif/ });
  expect(links).toHaveLength(2);
  expect(links[0]).toHaveTextContent("版本 abcdef01-123");
  expect(links[1]).toHaveTextContent("版本 abcdef01-987");
  const user = userEvent.setup();
  for (const button of screen.getAllByRole("button", { name: /的来源版本/ })) await user.click(button);
  for (const version of versions) {
    expect(screen.getByRole("link", { name: `sample.cif · 版本 ${version.slice(0, 12)}` }))
      .toHaveAttribute("href", `/projects/p/data?object=sample.cif-object&version=${version}`);
  }
});

it.each(["missing", "wrong-type", "duplicate-id", "foreign-source", "conflicting-source"])("uses only saved labels when result navigation metadata is %s", issue => {
  const item = sourceItem("cu", resultRef("Unverified.cif"));
  const location: Agent2ContextResultSource = { ...resultSource("s1"), result_items: [item] };
  if (issue === "missing") location.result_items = undefined;
  if (issue === "wrong-type") item.result_type = "electronic.band";
  if (issue === "duplicate-id") location.result_items!.push({ ...item, result_type: "electronic.band" });
  if (issue === "foreign-source") item.scientific_object_refs[0].project_id = "other";
  if (issue === "conflicting-source") item.scientific_object_refs.push({ ...item.scientific_object_refs[0], display_name: "Conflicting.cif" });
  render(<ResearchContextContents manifest={interpretationManifest(["cu"], ["Saved Cu.cif"])} manifests={[]} projectId="p" toolLabel={toolLabel} resultSources={[location]} />);
  expect(screen.getByRole("link", { name: "打开结果：Saved Cu.cif · 径向分布函数（RDF）" }))
    .toHaveAttribute("href", "/projects/p/research/original-session?turn=original-turn&resultSnapshot=s1&resultItem=cu");
  expect(screen.queryByText(/Unverified.cif|Conflicting.cif/)).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /的来源版本/ })).not.toBeInTheDocument();
});

it("does not choose a destination when the same snapshot has conflicting current locations", () => {
  render(<ResearchContextContents manifest={interpretationManifest(["cu"], ["Cu.cif"])} manifests={[]} projectId="p" toolLabel={toolLabel}
    resultSources={[resultSource("s1", "one"), resultSource("s1", "two")]} />);
  expect(screen.getByText("Cu.cif · 径向分布函数（RDF）")).toBeVisible();
  expect(screen.queryByRole("link", { name: /打开结果/ })).not.toBeInTheDocument();
});

it("switches between exact recorded model stages and distinguishes candidates from result methods", async () => {
  const first = manifest();
  const planner = manifest({ context_manifest_id: "m2", operation: "PLANNER", serialized_input: { research_objective: "计算衍射", candidates: [{ capability_id: "diffraction.theoretical_xrd", input_slots: [{ name: "structure" }], output_slots: [{ name: "theoretical_xrd" }] }] } });
  const interpreter = manifest({ context_manifest_id: "m3", operation: "INTERPRETER", serialized_input: { research_question: "解释保存结果", result: { facts: [{ predicate: "xrd.peak_count", value: 290, unit: null }, { predicate: "xrd.scan_min", value: 0, unit: "deg" }], result_items: [{ title: "保存的理论衍射图" }], methods: [{ tool_id: "structure.xrd", parameters: { wavelength: 1.54184 } }] } } });
  render(<ResearchContextContents manifest={first} manifests={[first, planner, interpreter].map((item) => ({ operation: item.operation, manifest: item }))} projectId="p" toolLabel={toolLabel} />);
  const user = userEvent.setup();
  await user.selectOptions(screen.getByRole("combobox", { name: "调用阶段" }), "m2");
  await user.click(screen.getByText("提供给模型的工具选项 · 1"));
  expect(screen.getByText("理论 XRD 图谱")).toBeVisible();
  expect(screen.queryByText(/结果中的工具与参数/)).not.toBeInTheDocument();
  await user.selectOptions(screen.getByRole("combobox", { name: "调用阶段" }), "m3");
  expect(screen.getByText("保存的理论衍射图")).toBeVisible();
  await user.click(screen.getByText("输入数值 · 2"));
  expect(screen.getByText("290")).toBeVisible();
  expect(screen.getByText("0 deg")).toBeVisible();
  expect(screen.getByText("结果中的工具与参数 · 1")).toBeVisible();
  expect(screen.queryByText(/提供给模型的工具选项/)).not.toBeInTheDocument();
});

it("renders compact interpreter types and limits and preserves exact peak subjects", () => {
  const value = manifest({ included_items: [], serialized_input: { result: {
    result_items: [{ result_type: "diffraction.xrd.theoretical" }],
    figures: [{ figure_type: "diffraction.xrd.theoretical" }], tables: [{ table_type: "diffraction.xrd.theoretical" }],
    limitations: [{ code: "XRD_THEORETICAL_ONLY", message: "这是理论衍射数据。" }],
    facts: [
      { predicate: "xrd.peak_count", subject_ref: "global", value: 290 },
      { predicate: "xrd.peak.two_theta", subject_ref: "peak_a", value: 20.498535, unit: "degree" },
      { predicate: "xrd.peak.two_theta", subject_ref: "peak_b", value: 21.874628, unit: "degree" },
      { predicate: "xrd.peak.intensity", subject_ref: "peak_b", value: 75.000168 },
      { predicate: "xrd.peak.intensity", subject_ref: "peak_a", value: 100 },
      { predicate: "xrd.peak.intensity", value: 0 },
      { predicate: "xrd.peak.intensity", value: 10 },
    ],
  } } });
  const view = contextContentView(value);
  expect(view.results[0].title).toBe("理论 XRD 结果");
  expect(view.visuals).toEqual(["理论 XRD 图谱", "理论 XRD 数据表"]);
  expect(view.limitations).toEqual(["这是理论衍射数据。"]);
  expect(view.factGroups).toHaveLength(5);
  expect(view.factGroups[1].facts.map((fact) => fact.value)).toEqual(["20.498535", "100"]);
  expect(view.factGroups[2].facts.map((fact) => fact.value)).toEqual(["21.874628", "75.000168"]);
  expect(view.factGroups[3].facts[0].value).toBe("0");
});

it("exposes report findings, prior answer and supplied actions without inventing missing subjects", () => {
  const value = manifest({ serialized_input: { allowed_actions: ["ANSWER", "ANALYZE"],
    result: { facts: [{ predicate: "xrd.peak.intensity", value: 100 }, { predicate: "xrd.peak.intensity", value: 75 }] },
    interpretation: { findings: [{ statement: "第一条结论" }], supporting_findings: [{ statement: "补充结论" }], answer_lead: "已有回答正文", limitations: ["原始限制"] },
    literature_evidence: [{ title: "衍射方法文献" }],
  } });
  const view = contextContentView(value);
  expect(view.findings).toEqual(["第一条结论", "补充结论"]);
  expect(view.narrative).toEqual(["已有回答正文"]);
  expect(view.literature[0].title).toBe("衍射方法文献");
  expect(view.actions).toEqual(["回答问题", "运行分析"]);
  expect(view.factGroups).toHaveLength(2);
  expect(view.factGroups.every((group) => group.title === "")).toBe(true);
});

it("does not report empty input when only tool choices were saved", () => {
  render(<ResearchContextContents manifest={manifest({ included_items: [], serialized_input: { candidates: [{ capability_id: "diffraction.theoretical_xrd" }] } })} manifests={[]} projectId="p" toolLabel={toolLabel} />);
  expect(screen.getByText("提供给模型的工具选项 · 1")).toBeVisible();
  expect(screen.queryByText("这条记录没有保存可展示的输入内容。")).not.toBeInTheDocument();
});
