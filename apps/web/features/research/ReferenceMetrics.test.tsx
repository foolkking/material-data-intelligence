import React from "react";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import { compileScientificPresentation, type ScientificPresentationBlock } from "../../app/lib/scientific-presentation";
import { groupReferenceMetrics } from "./ReferenceMetrics";
import { ScientificPresentationBlocks } from "./ScientificPresentationBlocks";

function referenceFacts(): Agent2ScientificFact[] {
  return [["Si", 1.11], ["Cu", 1.32]].flatMap(([symbol, value]) => [
    {fact_id:`${symbol}:symbol`, subject_ref:`element:${symbol}`, predicate:"reference.element.symbol", value:symbol, unit:null, source:{artifact_id:"reference",tool_call_id:"call"}},
    {fact_id:`${symbol}:value`, subject_ref:`element:${symbol}`, predicate:"reference.element.covalent_radius", value, unit:"angstrom", source:{artifact_id:"reference",tool_call_id:"call"}},
  ]);
}
function presentation(items: Agent2ScientificFact[], resultId = "result") {
  return compileScientificPresentation({resultId, facts:items.map(fact => ({factId:fact.fact_id,subjectRef:fact.subject_ref,
    predicate:fact.predicate,value:fact.value,unit:fact.unit,source:{artifactId:fact.source.artifact_id,toolCallId:fact.source.tool_call_id}}))});
}
function metrics(items: Agent2ScientificFact[]) {
  return presentation(items).blocks.filter((block): block is Extract<ScientificPresentationBlock,{type:"metric"}> => block.type === "metric");
}

describe("reference result values", () => {
  it("starts folded and exposes exact symbol/value pairs with the reference unit", async () => {
    const user = userEvent.setup(), facts = referenceFacts();
    render(<ScientificPresentationBlocks presentation={presentation(facts)} resultFacts={facts} />);
    expect(screen.getByRole("table")).not.toBeVisible();
    expect(screen.queryByText("指标")).toBeNull();
    await user.click(screen.getByText("参考数值 · 2 种元素"));
    const table = screen.getByRole("table",{name:"元素参考数值"});
    expect(within(table).getByRole("columnheader",{name:"参考共价半径（Å）"})).toBeVisible();
    expect(within(table).getAllByRole("row")).toHaveLength(3);
    expect(within(table).getByText("1.11")).toHaveAttribute("data-exact-value","1.11");
    expect(within(table).getByText("Cu")).toHaveAttribute("data-fact-id","Cu:symbol");
  });

  it.each(["artifact","producer","subject","result","material","value","unit","duplicate-id","duplicate-predicate"])("keeps a %s conflict ungrouped", fault => {
    const facts = referenceFacts().slice(0,2), blocks = metrics(facts);
    if (fault === "artifact") blocks[0].source.artifactId = "foreign";
    if (fault === "producer") blocks[0].source.toolCallId = "foreign";
    if (fault === "subject") facts[0].subject_ref = "other-element";
    if (fault === "result") blocks[0].source.resultId = "foreign";
    if (fault === "material") blocks[0].source.objectId = "unrelated-material";
    if (fault === "value") blocks[1].value = "999";
    if (fault === "unit") { facts[1].unit = "nm"; blocks[1].unit = "nm"; }
    if (fault === "duplicate-id") facts.push({...facts[0]});
    if (fault === "duplicate-predicate") { facts.push({...facts[0],fact_id:"duplicate"}); blocks.push({...blocks[0],id:"duplicate",source:{...blocks[0].source,factId:"duplicate"}}); }
    const result = groupReferenceMetrics(blocks, facts);
    expect(result.groups).toHaveLength(0);
    expect(result.remaining).toEqual(blocks);
  });
});
