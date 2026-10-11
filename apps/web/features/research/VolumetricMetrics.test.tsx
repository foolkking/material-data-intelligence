import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import { compileScientificPresentation, type ScientificPresentationBlock } from "../../app/lib/scientific-presentation";
import { ScientificPresentationBlocks } from "./ScientificPresentationBlocks";
import { groupVolumetricMetrics } from "./VolumetricMetrics";

function fieldFacts(artifact = "partial", quantity = "orbital_density", unit = "electron/angstrom^3", integralUnit = "electron"): Agent2ScientificFact[] {
  return [
    ["field_name", "total", null], ["quantity", quantity, null], ["canonical_unit", unit, null],
    ["unit_conversion_applied", true, null], ["unit_conversion_factor", 0.125, null],
    ["statistics_authority", "computed_from_payload", null], ["minimum", 0.5, unit], ["maximum", 4, unit],
    ["mean", 2.250000123, unit], [integralUnit === "electron" ? "integral" : "volume_integral", 18, integralUnit],
  ].map(([predicate, value, factUnit]) => ({fact_id: `${artifact}-${predicate}`, predicate: `volumetric.${predicate}`, subject_ref: artifact,
    value, unit: factUnit as string | null, source: {artifact_id: artifact}}));
}
function presentation(facts: Agent2ScientificFact[], resultId = "result") {
  return compileScientificPresentation({resultId, facts: facts.map(fact => ({factId: fact.fact_id, predicate: fact.predicate,
    subjectRef: fact.subject_ref, value: fact.value, unit: fact.unit, source: {artifactId: fact.source.artifact_id}}))});
}
function metrics(facts: Agent2ScientificFact[], resultId = "result") {
  return presentation(facts, resultId).blocks.filter((block): block is Extract<ScientificPresentationBlock, {type:"metric"}> => block.type === "metric");
}

describe("volumetric result statistics", () => {
  it("shows saved statistics first with exact values, units and source, keeping definitions on demand", async () => {
    const facts = fieldFacts();
    const original = JSON.stringify(facts);
    const content = presentation(facts);
    const originalPresentation = JSON.stringify(content);
    const user = userEvent.setup();
    render(<ScientificPresentationBlocks layout="research" presentation={content} resultFacts={facts} artifactCatalog={[{artifactId:"partial",jobId:"job"}]} />);
    const summary = screen.getByRole("region", {name:"部分电荷密度统计"});
    expect(within(summary).getByText("均值")).toBeVisible();
    expect(within(summary).getByText("2.25")).toHaveAttribute("data-exact-value", "2.250000123");
    expect(within(summary).getByText("2.25")).toHaveAttribute("data-unit", "electron/angstrom^3");
    expect(within(summary).getByText("整胞积分")).toBeVisible();
    expect(within(summary).getByText("18")).toHaveAttribute("data-unit", "electron");
    expect(within(summary).getByRole("link", {name:"来源数据"})).toHaveAttribute("href", "/api/planner/jobs/job/artifacts/partial/content");
    const details = screen.getByText(/数据定义与网格/).closest("details")!;
    expect(details).not.toHaveAttribute("open");
    await user.click(within(details).getByText(/数据定义与网格/));
    expect(details).toHaveAttribute("open");
    expect(within(details).getByText("是")).toHaveAttribute("data-exact-value", "true");
    expect(within(details).getByText("由保存的场数据计算")).toHaveAttribute("data-exact-value", "computed_from_payload");
    expect(screen.queryByRole("heading", {name:"指标", exact:true})).toBeNull();
    expect(JSON.stringify(facts)).toBe(original);
    expect(JSON.stringify(content)).toBe(originalPresentation);
  });

  it.each([
    ["electron_localization_function", "dimensionless", "angstrom^3", "电子局域函数（ELF）统计", "Å³"],
    ["local_potential", "electronvolt", "electronvolt*angstrom^3", "局域势统计", "eV·Å³"],
  ])("retains the saved integral semantics for %s", (quantity, unit, integralUnit, name, renderedUnit) => {
    const facts = fieldFacts("field", quantity, unit, integralUnit);
    render(<ScientificPresentationBlocks presentation={presentation(facts)} resultFacts={facts} />);
    const summary = screen.getByRole("region", {name});
    expect(within(summary).getByText("整胞体积分")).toBeVisible();
    expect(within(summary).getByText("18")).toHaveAttribute("data-unit", integralUnit);
    expect(within(summary).getByText(renderedUnit)).toBeVisible();
    expect(within(summary).queryByText("电子")).toBeNull();
  });

  it.each(["artifact", "subject", "result"])("does not combine complementary statistics across a different %s", difference => {
    const facts = fieldFacts();
    if (difference === "artifact") facts[7].source.artifact_id = "another";
    if (difference === "subject") facts[7].subject_ref = "another";
    const blocks = metrics(facts);
    if (difference === "result") blocks[7].source.resultId = "another";
    const result = groupVolumetricMetrics(blocks, facts);
    expect(result.groups).toHaveLength(0);
    expect(result.remaining).toEqual(blocks);
  });

  it.each(["duplicate-id", "conflicting-predicate", "nonfinite", "unit", "value", "missing-source"])("keeps original metrics when correspondence is %s", failure => {
    const facts = fieldFacts();
    if (failure === "duplicate-id") facts.push({...facts[7]});
    if (failure === "conflicting-predicate") facts.push({...facts[7],fact_id:"conflict",value:900});
    if (failure === "nonfinite") facts[7].value = Infinity;
    if (failure === "unit") facts[7].unit = "volt";
    const blocks = metrics(facts);
    if (failure === "value") blocks[7].value = "900";
    if (failure === "missing-source") blocks[7].source.artifactId = null;
    const result = groupVolumetricMetrics(blocks, facts);
    expect(result.groups).toHaveLength(0);
    expect(result.remaining).toEqual(blocks);
  });

  it("retains separate identical-looking fields and does not invent missing means or integrals", () => {
    const first = fieldFacts("first").filter(fact => !["volumetric.mean","volumetric.integral"].includes(fact.predicate));
    const second = fieldFacts("second");
    const result = groupVolumetricMetrics(metrics([...first,...second]), [...first,...second]);
    expect(result.groups).toHaveLength(2);
    expect(result.groups[0].values.map(value=>value.label)).toEqual(["最小值","最大值"]);
    expect(result.groups[1].values.map(value=>value.label)).toEqual(["最小值","最大值","均值","整胞积分"]);
  });

  it("keeps the potential reference next to its saved statistics without inferring a zero shift", () => {
    const facts = [...fieldFacts("potential", "local_potential", "electronvolt", "electronvolt*angstrom^3"),
      {fact_id:"reference",predicate:"volumetric.potential_reference",subject_ref:"potential",value:"source_defined",source:{artifact_id:"potential"}},
      {fact_id:"shift",predicate:"volumetric.potential_shift",subject_ref:"potential",value:0,unit:"electronvolt",source:{artifact_id:"potential"}},
    ];
    const view = render(<ScientificPresentationBlocks presentation={presentation(facts)} resultFacts={facts} />);
    expect(screen.getByText("参考零点：源数据定义")).toHaveAttribute("data-exact-value", "source_defined");
    expect(screen.getByText("已保存平移：0 eV")).toBeVisible();
    expect(screen.queryByRole("heading", {name:"指标",exact:true})).toBeNull();
    const withoutShift = facts.filter(fact => fact.fact_id !== "shift");
    view.rerender(<ScientificPresentationBlocks presentation={presentation(withoutShift)} resultFacts={withoutShift} />);
    expect(screen.queryByText(/已保存平移/)).toBeNull();
    expect(screen.getByText("参考零点：源数据定义")).toBeVisible();
  });
});
