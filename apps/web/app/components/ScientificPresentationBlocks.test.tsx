import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ScientificPresentationBlocks } from "./ScientificPresentationBlocks";
import { compileScientificPresentation } from "../lib/scientific-presentation";

const mocks = vi.hoisted(() => ({
  getPlannerInterpretationEvidence: vi.fn(),
}));

vi.mock("../lib/planner-api", () => ({
  getPlannerInterpretationEvidence: mocks.getPlannerInterpretationEvidence,
}));

vi.mock("../../scientific-viewers/ScientificViewerAdapter", () => ({
  ScientificResultViewer: ({ jobId, selected }: { jobId: string; selected: { artifactId?: string; id?: string } }) => (
    <div data-testid="inline-scientific-result-viewer">
      {jobId} · {selected.artifactId || selected.id}
    </div>
  ),
}));

const presentation = {
  schemaVersion: "1.0" as const,
  exactSourceRefs: [{ objectId: "object-1", versionId: "version-2", versionNo: 2, objectType: "structure.crystal", displayName: "Silicon" }],
  blocks: [{
    id: "evidence-1",
    type: "evidence_reference" as const,
    title: "证据",
    label: "band_gap = 2.5",
    source: {
      resultId: "result-1",
      interpretationId: "interpretation-1",
      evidenceId: "evidence-1",
      artifactId: "artifact-1",
      jobId: "job-1",
      toolCallId: "call-1",
      objectId: "object-1",
      versionId: "version-2",
      versionNo: 2,
    },
  }],
};

describe("ScientificPresentationBlocks evidence inspector", () => {
  it("keeps exact coordination values available in a collapsed group beside the geometry", async () => {
    const facts = [
      { fact_id: "neighbors", predicate: "structure.coordination.neighbor_count", subject_ref: "site:0", value: 4, source: { artifact_id: "n1", tool_call_id: "call-n1" } },
      { fact_id: "volume", predicate: "structure.local_environment.volume", subject_ref: "site:0", value: 6.670958625, unit: "angstrom^3", source: { artifact_id: "n2", tool_call_id: "call-n2" } },
    ];
    const content = compileScientificPresentation({ resultId: "polyhedron", facts: facts.map(fact => ({
      factId: fact.fact_id, predicate: fact.predicate, subjectRef: fact.subject_ref, value: fact.value, unit: fact.unit,
      source: { artifactId: fact.source.artifact_id },
    })) });
    render(<ScientificPresentationBlocks presentation={content} layout="research" resultFacts={facts} />);
    const summary = screen.getByText("配位数值 · 2 项");
    expect(summary.closest("details")).not.toHaveAttribute("open");
    expect(screen.getByTitle("精确值：6.670958625")).not.toBeVisible();
    await userEvent.click(summary);
    expect(screen.getByTitle("精确值：6.670958625")).toBeVisible();
    expect(screen.getByTitle("精确值：6.670958625")).toHaveAttribute("data-exact-value", "6.670958625");
  });

  it("keeps parameter metrics compact and discloses their exact source with the result", async () => {
    const content = compileScientificPresentation({ resultId: "parameters", facts: [
      { factId: "output", predicate: "calculation.output_value", subjectRef: "value-0", value: 50, unit: "angstrom", source: { artifactId: "units-table" } },
    ] });
    render(<ScientificPresentationBlocks presentation={content} layout="research" inputProvenance={{
      execution_scope: "PROJECT", input_origin: "USER_PARAMETERS", parameter_inputs: [{
        tool_id: "reference.convert_units", tool_call_id: "units", input_origin: "USER_PARAMETERS", content_hash: "a".repeat(64),
        resolved_parameters: { values: [5], from_unit: "nm", to_unit: "angstrom" },
      }],
    }} />);
    expect(screen.getByText("计算数值 · 1 项").closest("details")).not.toHaveAttribute("open");
    await userEvent.click(screen.getByText("计算数值 · 1 项"));
    expect(screen.getByText("换算结果")).toBeVisible();
    expect(screen.getByText("50")).toHaveAttribute("data-exact-value", "50");
    expect(within(screen.getByText("50").parentElement!).getByText("Å")).toBeVisible();
    await userEvent.click(screen.getByText("输入参数与原始数据"));
    expect(screen.getByText("单位换算 · 输入参数")).toBeVisible();
    expect(screen.getByText("nm")).toBeVisible();
  });

  it("shows the saved constant-target R² status as readable text while retaining its exact source", () => {
    const facts = [{ factId: "r2-status", predicate: "ml.r2_status", subjectRef: "evaluation", value: "undefined_constant_target", source: { artifactId: "metrics" } }];
    const original = JSON.stringify(facts);
    const content = compileScientificPresentation({ resultId: "result", facts });
    render(<ScientificPresentationBlocks presentation={content} layout="research" />);
    expect(screen.getByText("R² 适用性")).toBeVisible();
    expect(screen.getByText("未定义（目标值为常量）")).toHaveAttribute("data-exact-value", "undefined_constant_target");
    expect(content.blocks.find(block => block.type === "metric")?.source.factId).toBe("r2-status");
    expect(JSON.stringify(facts)).toBe(original);
  });

  it("places the exact saved research plot before findings and keeps source-only outputs reachable", async () => {
    const content = { schemaVersion: "1.0" as const, exactSourceRefs: [], blocks: [
      { id: "finding", type: "finding" as const, title: "发现", text: "已保存的发现", confidence: "DIRECT" as const, evidenceIds: [], source: { resultId: "r1" } },
      { id: "plot", type: "figure" as const, title: "结果图谱", artifactId: "plot", source: { resultId: "r1", jobId: "j1", artifactId: "plot" } },
      { id: "missing", type: "table" as const, title: "来源数据", artifactId: "missing", source: { resultId: "r1", jobId: "j1", artifactId: "missing" } },
    ] };
    const view = render(<ScientificPresentationBlocks layout="research" projectId="p1" presentation={content}
      artifactCatalog={[{ artifactId: "plot", jobId: "j1", type: "plotly_json" }]} />);
    expect(await screen.findByTestId("inline-scientific-result-viewer")).toHaveTextContent("j1 · plot");
    const visual = screen.getByRole("region", { name: "图表与数据" });
    expect(visual.compareDocumentPosition(screen.getByRole("heading", { name: "关键发现" })) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(screen.getByText("来源数据").parentElement?.querySelector("a")).toHaveAttribute("href", "/api/planner/jobs/j1/artifacts/missing/content");
    view.rerender(<ScientificPresentationBlocks projectId="p1" presentation={content}
      artifactCatalog={[{ artifactId: "plot", jobId: "j1", type: "plotly_json" }]} />);
    expect(screen.queryByTestId("inline-scientific-result-viewer")).toBeNull();
    expect(screen.getByRole("button", { name: "在页内查看" })).toBeVisible();
  });

  it("omits only a verbatim repeated research summary and keeps qualified findings", () => {
    const content = {
      schemaVersion: "1.0" as const, exactSourceRefs: [], blocks: [
        { id: "lead", type: "narrative" as const, text: "第一条发现。 第二条发现。", source: { resultId: "result-1" } },
        { id: "a", type: "finding" as const, title: "发现", text: "第一条发现。", confidence: "DIRECT" as const, evidenceIds: [], source: { resultId: "result-1" } },
        { id: "b", type: "finding" as const, title: "发现", text: "第二条发现。", confidence: "QUALIFIED" as const, evidenceIds: [], source: { resultId: "result-1" } },
      ],
    };
    const view = render(<ScientificPresentationBlocks presentation={content} layout="research" />);
    expect(screen.queryByText("第一条发现。 第二条发现。")).toBeNull();
    expect(screen.getByText("第一条发现。")).toBeVisible();
    expect(screen.getByText("第二条发现。")).toBeVisible();
    expect(screen.getByText("限定结论")).toBeVisible();
    expect(screen.queryByText("直接证据")).toBeNull();
    view.rerender(<ScientificPresentationBlocks layout="research" presentation={{ ...content, blocks: [
      { ...content.blocks[0], text: "概述中的独有信息。" }, ...content.blocks.slice(1),
    ] }} />);
    expect(screen.getByText("概述中的独有信息。")).toBeVisible();
    view.rerender(<ScientificPresentationBlocks layout="research" presentation={{ ...content, blocks: [
      { ...content.blocks[0], source: { resultId: "another-result" } }, ...content.blocks.slice(1),
    ] }} />);
    expect(screen.getByText("第一条发现。 第二条发现。")).toBeVisible();
    view.rerender(<ScientificPresentationBlocks presentation={content} />);
    expect(screen.getByText("第一条发现。 第二条发现。")).toBeVisible();
    expect(screen.getByText("直接证据")).toBeVisible();
  });

  it("opens each finding's exact facts without counting a shared artifact as another fact", async () => {
    const user = userEvent.setup();
    const content = compileScientificPresentation({
      resultId: "result-peaks",
      facts: [
        { factId: "angle-first", predicate: "xrd.peak.two_theta", subjectRef: "peak-1", value: 20.498535, unit: "degree" },
        { factId: "angle-second", predicate: "xrd.peak.two_theta", subjectRef: "peak-2", value: 21.874628, unit: "degree" },
      ],
      persistedInterpretation: {
        contract_version: "1.0", title: "XRD", answer_lead: "主要衍射峰", limitations: [],
        primary_result_refs: [], supporting_result_refs: [], follow_up_suggestions: [], supporting_findings: [],
        primary_findings: ["first", "second"].map(name => ({
          finding_id: name, statement: `${name} peak`, importance: "HIGH", confidence: "HIGH",
          fact_refs: [`angle-${name}`], evidence_refs: ["shared-table"], result_item_refs: [],
        })),
      },
    });
    const view = render(<ScientificPresentationBlocks presentation={content} executionProcess={<p>Saved tool execution</p>} />);
    expect(screen.queryByText(/项证据/)).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "查看证据链" })).not.toBeInTheDocument();
    const first = screen.getByText("first peak").closest("article")!;
    const second = screen.getByText("second peak").closest("article")!;
    await user.click(within(first).getByText("查看引用事实 · 1 项"));
    expect(first.querySelector("details")).toHaveAttribute("open");
    expect(second.querySelector("details")).not.toHaveAttribute("open");
    expect(within(first).getByText("20.498535 degree")).toHaveAttribute("data-exact-value", "20.498535");
    expect(within(first).queryByText("21.874628 degree")).not.toBeInTheDocument();
    await user.click(within(second).getByText("查看引用事实 · 1 项"));
    expect(within(second).getByText("21.874628 degree")).toBeVisible();
    expect(screen.getAllByText("工具调用过程")).toHaveLength(1);
    const replacement = { ...content, blocks: content.blocks.map(block => ({ ...block, source: { ...block.source, resultId: "replacement" } })) };
    view.rerender(<ScientificPresentationBlocks presentation={replacement} />);
    expect(screen.getByText("first peak").closest("article")?.querySelector("details")).not.toHaveAttribute("open");
  });

  it("does not substitute facts from another result or choose an ambiguous duplicate", async () => {
    const user = userEvent.setup();
    render(<ScientificPresentationBlocks presentation={{ schemaVersion: "1.0", exactSourceRefs: [], blocks: [
      { id: "finding", type: "finding", title: "发现", text: "需核对的结论", confidence: "DIRECT", source: { resultId: "current" }, factIds: ["absent", "ambiguous"], evidenceIds: [] },
      { id: "foreign", type: "metric", title: "foreign metric", value: "999", source: { resultId: "other", factId: "absent" } },
      { id: "duplicate-1", type: "metric", title: "duplicate", value: "111", source: { resultId: "current", factId: "ambiguous" } },
      { id: "duplicate-2", type: "metric", title: "duplicate", value: "222", source: { resultId: "current", factId: "ambiguous" } },
    ] }} />);
    await user.click(screen.getByText("查看引用事实 · 2 项"));
    const finding = screen.getByText("需核对的结论").closest("article")!;
    expect(within(finding).getByRole("status")).toHaveTextContent("2 项引用事实暂未提供可展示的数值");
    expect(finding.querySelectorAll("dd")).toHaveLength(0);
  });

  it("keeps facts beyond the first twelve reachable with exact values and resets disclosure for a new result", async () => {
    const user = userEvent.setup();
    const facts = Array.from({ length: 16 }, (_, index) => ({
      factId: `fact-${index}`, predicate: index === 15 ? "volumetric.maximum" : `volumetric.test_${index}`,
      subjectRef: "field", value: index === 15 ? 0.00092615445 : index, unit: "dimensionless",
    }));
    const make = (resultId: string) => compileScientificPresentation({ resultId, facts });
    const view = render(<ScientificPresentationBlocks presentation={make("first")} />);
    const summary = screen.getByText("更多指标 · 4 项");
    expect(summary.closest("details")).not.toHaveAttribute("open");
    expect(screen.getByText("源数值最大值").closest("details")).toBe(summary.closest("details"));
    await user.click(summary);
    expect(summary.closest("details")).toHaveAttribute("open");
    expect(screen.getByText("0.0009261545")).toHaveAttribute("data-exact-value", "0.00092615445");
    view.rerender(<ScientificPresentationBlocks presentation={make("second")} />);
    expect(screen.getByText("更多指标 · 4 项").closest("details")).not.toHaveAttribute("open");
  });

  it("shows scientist-facing version context without exposing raw identities by default", () => {
    render(<ScientificPresentationBlocks presentation={presentation} projectId="project-1" />);
    expect(screen.getByText("来源版本 2")).toBeInTheDocument();
    expect(screen.getByText("已绑定科学结果与证据")).toBeInTheDocument();
    expect(screen.queryByText(/result-1|evidence-1|version-2/)).toBeNull();
  });

  it("renders bounded metric precision while retaining the exact source value", () => {
    render(<ScientificPresentationBlocks presentation={{
      schemaVersion: "1.0",
      exactSourceRefs: [],
      blocks: [{
        id: "metric-rmse",
        type: "metric",
        title: "RMSE",
        value: "0.21602468994692867",
        source: { resultId: "result-1", factId: "fact-rmse" },
      }],
    }} />);
    const value = screen.getByText("0.2160247");
    expect(value).toHaveAttribute("data-exact-value", "0.21602468994692867");
    expect(value).toHaveAttribute("title", "精确值：0.21602468994692867");
    expect(screen.getByText("精确值 0.21602468994692867")).toHaveClass("sr-only");
  });

  it("renders canonical system limitations in product language without changing their scientific meaning", () => {
    render(<ScientificPresentationBlocks presentation={{
      schemaVersion: "1.0",
      exactSourceRefs: [],
      blocks: [{
        id: "limitation-1",
        type: "limitation",
        text: "The current DOS Artifact does not provide eigenvectors or animation authority.",
        source: {},
      }],
    }} />);
    expect(screen.getByText("当前声子态密度 Artifact 不包含特征向量，因此不提供模式动画依据。")).toBeInTheDocument();
  });

  it("shows repeated result qualifications once while retaining distinct caveats and saved blocks", () => {
    const blocks = [
      { id: "one", type: "limitation" as const, text: "仅根据输入参数计算。", source: { artifactId: "table" } },
      { id: "two", type: "limitation" as const, text: " 仅根据输入参数计算。 ", source: { artifactId: "recipe" } },
      { id: "three", type: "warning" as const, text: "仅根据输入参数计算。", source: {} },
      { id: "four", type: "warning" as const, text: "未验证样品性质。", source: {} },
    ];
    const before = JSON.stringify(blocks);
    render(<ScientificPresentationBlocks presentation={{ schemaVersion: "1.0", exactSourceRefs: [], blocks }} />);
    expect(screen.getAllByText("仅根据输入参数计算。")).toHaveLength(1);
    expect(screen.getByText("未验证样品性质。")).toBeInTheDocument();
    expect(JSON.stringify(blocks)).toBe(before);
  });

  it("keeps an exact repeated finding with its qualification and preserves its facts and confidence", async () => {
    const qualification = "这是理想模型，不代表样品测量结果。";
    const distinct = "这是理想模型，但不能据此确认稳定相。";
    const source = { resultId: "ideal", interpretationId: "interpretation" };
    const content = { schemaVersion: "1.0" as const, exactSourceRefs: [], blocks: [
      { id: "lead", type: "narrative" as const, text: qualification, source },
      { id: "duplicate", type: "finding" as const, title: "发现", text: qualification, confidence: "QUALIFIED" as const, factIds: ["model"], evidenceIds: [], source },
      { id: "distinct", type: "finding" as const, title: "发现", text: distinct, confidence: "DIRECT" as const, factIds: [], evidenceIds: [], source },
      { id: "model", type: "metric" as const, title: "模型类型", value: "ideal_crystal", source: { ...source, factId: "model" } },
      { id: "limit", type: "limitation" as const, text: qualification, source },
    ] };
    const before = JSON.stringify(content);
    const view = render(<ScientificPresentationBlocks presentation={content} layout="research" />);
    expect(screen.getAllByText(qualification)).toHaveLength(1);
    expect(screen.getByText(distinct).closest("article")).not.toBeNull();
    const limit = screen.getByText(qualification).closest("li")!;
    expect(within(limit).getByText("限定结论")).toBeVisible();
    await userEvent.click(within(limit).getByText("查看引用事实 · 1 项"));
    expect(within(limit).getByText("ideal_crystal")).toHaveAttribute("data-exact-value", "ideal_crystal");
    expect(JSON.stringify(content)).toBe(before);
    view.rerender(<ScientificPresentationBlocks presentation={content} />);
    expect(screen.getAllByText(qualification)).toHaveLength(3);
    expect(screen.getByText("查看引用事实 · 1 项").closest("article")).not.toBeNull();
  });

  it.each(["resultId", "interpretationId", "objectId", "versionId", "unknown"])("keeps repeated findings separate for different or unknown %s ownership", (key) => {
    const source = { resultId: "result", interpretationId: "interpretation", objectId: "object", versionId: "version" };
    const findingSource = key === "unknown" ? {} : { ...source, [key]: "another" };
    render(<ScientificPresentationBlocks layout="research" presentation={{ schemaVersion: "1.0", exactSourceRefs: [], blocks: [
      { id: "finding", type: "finding", title: "发现", text: "仅为理想模型。", confidence: "DIRECT", factIds: [], evidenceIds: [], source: findingSource },
      { id: "limitation", type: "limitation", text: "仅为理想模型。", source },
    ] }} />);
    expect(screen.getAllByText("仅为理想模型。")).toHaveLength(2);
    expect(screen.getByRole("heading", { name: "关键发现" })).toBeVisible();
  });

  it("assigns unique accessible ids and relationships to repeated presentation instances", async () => {
    const user = userEvent.setup();
    const { container } = render(
      <>
        <ScientificPresentationBlocks presentation={presentation} projectId="project-1" />
        <ScientificPresentationBlocks presentation={presentation} projectId="project-1" />
      </>,
    );
    for (const trigger of container.querySelectorAll<HTMLButtonElement>("button[aria-controls]")) {
      await user.click(trigger);
    }
    const sections = [...container.querySelectorAll<HTMLElement>("section.scientific-presentation")];
    const ids = sections.map((section) => section.getAttribute("aria-labelledby"));
    expect(ids).toHaveLength(2);
    expect(ids[0]).toBeTruthy();
    expect(ids[0]).not.toBe(ids[1]);
    expect(ids.every((id) => id && document.getElementById(id)?.tagName === "H3")).toBe(true);
    const allIds = [...container.querySelectorAll<HTMLElement>("[id]")].map((node) => node.id);
    expect(new Set(allIds).size).toBe(allIds.length);

    const evidenceItems = [...container.querySelectorAll<HTMLElement>(".scientific-presentation-evidence-item")];
    expect(evidenceItems).toHaveLength(2);
    expect(evidenceItems[0].id).not.toBe(evidenceItems[1].id);
    const inspectorIds = evidenceItems.map((item) =>
      item.querySelector<HTMLButtonElement>("button[aria-controls]")?.getAttribute("aria-controls"),
    );
    expect(inspectorIds.every(Boolean)).toBe(true);
    expect(new Set(inspectorIds).size).toBe(inspectorIds.length);
    inspectorIds.forEach((id) => expect(document.getElementById(id!)).not.toBeNull());
  });

  it("opens a bounded exact source chain without exposing raw infrastructure details", async () => {
    mocks.getPlannerInterpretationEvidence.mockResolvedValue({
      interpretationId: "interpretation-1",
      bundleId: "bundle-1",
      bundleHash: "a".repeat(64),
      jobId: "job-1",
      planId: "plan-1",
      evidenceItems: [{
        schemaVersion: "1.0",
        evidenceItemId: "evidence-1",
        semanticRole: "band_gap",
        evidenceKind: "SCALAR",
        subjectId: "mat-2",
        displayValue: "2.5",
        unit: "eV",
        sourceArtifactId: "artifact-1",
        sourceArtifactChecksum: "b".repeat(64),
        artifactContract: "dataset.table",
        artifactContractVersion: "1.0",
        sourceToolId: "data.materials_explorer",
        sourceToolVersion: "1.0",
        fieldLocator: { fieldId: "band_gap", entityId: "mat-2" },
        warnings: [],
        limitations: [],
      }],
      sourceArtifactIds: ["artifact-1"],
      sourceObjectRefs: [{ objectId: "object-1", versionId: "version-2", objectType: "dataset", displayName: "Dataset" }],
      artifacts: [{ artifactId: "artifact-1", jobId: "job-1", contentHash: "c".repeat(64) }],
      toolCalls: [{ id: "call-1", toolId: "data.materials_explorer", status: "completed" }],
      bundleWarnings: [],
      bundleLimitations: [],
    });

    const user = userEvent.setup();
    render(<ScientificPresentationBlocks presentation={presentation} projectId="project-1" instanceId="turn-1" />);
    await user.click(screen.getByRole("button", { name: "检查证据链" }));

    expect(await screen.findByRole("region", { name: "证据链 evidence-1" })).toHaveTextContent("version-2");
    expect(screen.getByRole("region", { name: "证据链 evidence-1" })).toHaveTextContent("data.materials_explorer");
    expect(screen.getByRole("region", { name: "证据链 evidence-1" })).toHaveTextContent("band_gap · 2.5 eV");
    const evidenceTrigger = screen.getByRole("button", { name: "收起证据链" });
    expect(evidenceTrigger).toHaveAttribute("aria-controls", "scientific-evidence-inspector-turn-1-evidence-1");
    expect(document.activeElement).toBe(screen.getByRole("region", { name: "证据链 evidence-1" }));
    expect(screen.getByRole("region", { name: "证据链 evidence-1" })).not.toHaveTextContent("redis://");
    expect(screen.getByRole("link", { name: "打开权威 Artifact" })).toHaveAttribute("href", "/api/planner/jobs/job-1/artifacts/artifact-1/content");
    await user.click(evidenceTrigger);
    expect(document.activeElement).toBe(screen.getByRole("button", { name: "检查证据链" }));
    await waitFor(() => expect(mocks.getPlannerInterpretationEvidence).toHaveBeenCalledWith("interpretation-1"));
  });

  it.each([false, true])("lets a finding open its exact linked evidence chain when moved to limitations: %s", async (inLimitations) => {
    mocks.getPlannerInterpretationEvidence.mockResolvedValue({
      interpretationId: "interpretation-finding",
      bundleId: "bundle-finding",
      jobId: "job-finding",
      planId: "plan-finding",
      evidenceItems: [{
        schemaVersion: "1.0",
        evidenceItemId: "evidence-finding",
        semanticRole: "coordination_number",
        subjectId: "site-14",
        displayValue: "4",
        unit: null,
        sourceArtifactId: "artifact-finding",
        sourceToolId: "core.structure",
        fieldLocator: { fieldId: "coordination_number", entityId: "site-14" },
        warnings: [],
        limitations: [],
      }],
      sourceArtifactIds: ["artifact-finding"],
      sourceObjectRefs: [{ objectId: "object-finding", versionId: "version-1", objectType: "structure.crystal" }],
      artifacts: [{ artifactId: "artifact-finding", jobId: "job-finding" }],
      toolCalls: [{ id: "call-finding", toolId: "core.structure", status: "completed" }],
      bundleWarnings: [],
      bundleLimitations: [],
    });
    const user = userEvent.setup();
    render(<ScientificPresentationBlocks
      projectId="project-finding"
      layout={inLimitations ? "research" : "document"}
      presentation={{
        schemaVersion: "1.0",
        exactSourceRefs: [{ objectId: "object-finding", versionId: "version-1" }],
        blocks: [
          ...(inLimitations ? [{ id: "same-limitation", type: "limitation" as const, text: "site-14 has four nearest neighbours.", source: {
            resultId: "result-finding", interpretationId: "interpretation-finding", objectId: "object-finding", versionId: "version-1",
          } }] : []),
          {
            id: "finding-1",
            type: "finding",
            title: "配位发现",
            text: "site-14 has four nearest neighbours.",
            confidence: "DIRECT",
            source: {
              resultId: "result-finding",
              interpretationId: "interpretation-finding",
              evidenceId: "evidence-finding",
              objectId: "object-finding",
              versionId: "version-1",
            },
            evidenceIds: ["evidence-finding"],
          },
          {
            id: "evidence-finding",
            type: "evidence_reference",
            title: "证据",
            label: "coordination_number = 4",
            source: {
              resultId: "result-finding",
              interpretationId: "interpretation-finding",
              evidenceId: "evidence-finding",
              artifactId: "artifact-finding",
              jobId: "job-finding",
              toolCallId: "call-finding",
              objectId: "object-finding",
              versionId: "version-1",
            },
          },
        ],
      }}
    />);

    const link = screen.getByRole("link", { name: "查看证据链" });
    const evidenceTarget = document.querySelector<HTMLElement>(".scientific-presentation-evidence-item");
    expect(evidenceTarget).not.toBeNull();
    expect(link).toHaveAttribute("href", `#${evidenceTarget!.id}`);
    expect(link).toHaveAttribute("aria-controls", evidenceTarget!.id);
    await user.click(link);
    expect(await screen.findByRole("region", { name: "证据链 evidence-finding" })).toHaveTextContent("version-1");
    expect(mocks.getPlannerInterpretationEvidence).toHaveBeenCalledWith("interpretation-finding");
  });

  it("opens one persisted Figure or Table through the existing scientific renderer without leaving Research", async () => {
    const user = userEvent.setup();
    render(<ScientificPresentationBlocks
      projectId="project-1"
      instanceId="turn-figure"
      presentation={{
        schemaVersion: "1.0",
        exactSourceRefs: [{ objectId: "object-1", versionId: "version-2" }],
        blocks: [{
          id: "figure-1",
          type: "figure",
          title: "配位数直方图",
          artifactId: "artifact-plot",
          source: {
            jobId: "job-1",
            artifactId: "artifact-plot",
            objectId: "object-1",
            versionId: "version-2",
          },
        }],
      }}
      artifactCatalog={[{
        artifactId: "artifact-plot",
        jobId: "job-1",
        type: "plotly_json",
        name: "coordination_hist_plot.json",
      }]}
    />);

    expect(screen.queryByTestId("inline-scientific-result-viewer")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "在页内查看" }));
    expect(screen.getByRole("region", { name: "图形：配位数直方图" })).toBeInTheDocument();
    expect(screen.getByTestId("inline-scientific-result-viewer")).toHaveTextContent("job-1 · artifact-plot");
    expect(screen.getByRole("link", { name: "查看源文件" })).toHaveAttribute(
      "href",
      "/api/planner/jobs/job-1/artifacts/artifact-plot/content",
    );
    expect(screen.getByRole("link", { name: "下载" })).toHaveAttribute(
      "download",
      "figure-1.figure.json",
    );
    await user.click(screen.getByRole("button", { name: "关闭预览" }));
    expect(screen.queryByTestId("inline-scientific-result-viewer")).not.toBeInTheDocument();
  });

  it("surfaces a bounded status when an unknown runtime block is rejected", () => {
    render(<ScientificPresentationBlocks
      projectId="project-1"
      instanceId="turn-unsafe"
      presentation={{
        schemaVersion: "1.0",
        exactSourceRefs: [],
        blocks: [{
          id: "unknown",
          type: "remote_component",
          label: "<script>blocked</script>",
        } as never],
      }}
    />);

    expect(screen.getByRole("status")).toHaveTextContent("1 个呈现块未通过安全校验");
    expect(screen.queryByText("<script>blocked</script>")).not.toBeInTheDocument();
  });
});
