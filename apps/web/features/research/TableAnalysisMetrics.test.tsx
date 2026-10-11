import React from "react";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import { compileScientificPresentation, type ScientificPresentationBlock } from "../../app/lib/scientific-presentation";
import { groupTableAnalysisMetrics } from "./table-analysis-metrics";
import { TableAnalysisMetrics } from "./TableAnalysisMetrics";
import { ScientificPresentationBlocks } from "./ScientificPresentationBlocks";

function facts(subject: string, values: Record<string, unknown>, prefix = "correlation", artifact = "matrix"): Agent2ScientificFact[] {
  return Object.entries(values).map(([key, value]) => ({ fact_id: `${artifact}:${subject}:${key}`, subject_ref: subject,
    predicate: `${prefix}.${key}`, value, unit: /(?:count|missing)$/u.test(key) ? "count" : null, source: { artifact_id: artifact } }));
}
function presentation(items: Agent2ScientificFact[], resultId = "result") {
  return compileScientificPresentation({resultId, facts: items.map(f => ({factId:f.fact_id,predicate:f.predicate,subjectRef:f.subject_ref,
    value:f.value,unit:f.unit,source:{artifactId:f.source.artifact_id,toolCallId:f.source.tool_call_id}}))});
}
function metrics(items: Agent2ScientificFact[]) { return presentation(items).blocks.filter((b): b is Extract<ScientificPresentationBlock,{type:"metric"}> => b.type === "metric"); }
function pairs(count = 12) { return Array.from({length:count}, (_,i) => facts(`pair-${i}`,{left_column:`energy_${i}`,right_column:"gap",coefficient:i === 0 ? 0 : -0.234567890123})).flat(); }

describe("saved table statistics", () => {
  it("shows one row per exact pair, keeps zero and full precision, and labels cited facts", () => {
    const items = pairs(2), content = presentation(items);
    render(<ScientificPresentationBlocks presentation={content} resultFacts={items} />);
    const table = screen.getByRole("table");
    expect(within(table).getAllByRole("row")).toHaveLength(3);
    expect(within(table).getByText("0")).toHaveAttribute("data-exact-value", "0");
    expect(table.querySelector('[data-exact-value="-0.234567890123"]')).not.toBeNull();
    expect(screen.queryByText("correlation.coefficient")).toBeNull();
    expect(content.blocks.find(b => b.type === "metric" && b.source.factId === "matrix:pair-0:coefficient")?.title).toBe("energy_0 ↔ gap · 相关系数");
    expect(screen.queryByText("指标")).toBeNull();
  });

  it("paginates all pairs, searches complete names, and handles an empty search without navigation", async () => {
    const user = userEvent.setup(), items = pairs(), grouped = groupTableAnalysisMetrics(metrics(items), items);
    render(<TableAnalysisMetrics groups={grouped.groups} artifacts={[]} />);
    expect(screen.getByText("1–10 / 12")).toBeVisible();
    await user.click(screen.getByRole("button", {name:"变量相关性下一页"}));
    expect(screen.getByText("11–12 / 12")).toBeVisible();
    expect(screen.getByText("energy_11")).toBeVisible();
    await user.type(screen.getByRole("searchbox"), "energy_0");
    expect(screen.getByText("1–1 / 1")).toBeVisible();
    expect(screen.getByRole("button", {name:"变量相关性上一页"})).toBeDisabled();
    await user.clear(screen.getByRole("searchbox"));
    await user.type(screen.getByRole("searchbox"), "missing");
    expect(screen.getByText("没有匹配的变量")).toBeVisible();
    expect(screen.getByRole("button", {name:"变量相关性下一页"})).toBeDisabled();
  });

  it("resets search and pagination for another exact result", async () => {
    const user = userEvent.setup(), items = pairs();
    const view = render(<ScientificPresentationBlocks presentation={presentation(items)} resultFacts={items} />);
    await user.type(screen.getByRole("searchbox"), "energy_11");
    view.rerender(<ScientificPresentationBlocks presentation={presentation(items,"another-result")} resultFacts={items} />);
    expect(screen.getByRole("searchbox")).toHaveValue("");
    expect(screen.getByText("1–10 / 12")).toBeVisible();
  });

  it.each(["artifact", "subject", "result", "version", "value", "unit", "duplicate-id", "duplicate-predicate", "nonfinite"])("does not join %s conflicts", invalid => {
    const items = pairs(1), blocks = metrics(items);
    if (invalid === "artifact") blocks[0].source.artifactId = "foreign";
    if (invalid === "subject") items[0].subject_ref = "foreign";
    if (invalid === "result") blocks[0].source.resultId = "foreign";
    if (invalid === "version") blocks[0].source.versionId = "foreign";
    if (invalid === "value") blocks[0].value = "other-name";
    if (invalid === "unit") {items[2].unit="eV"; blocks[2].unit="eV";}
    if (invalid === "duplicate-id") items.push({...items[0]});
    if (invalid === "duplicate-predicate") {items.push({...items[0],fact_id:"other"}); blocks.push({...blocks[0],id:"other",source:{...blocks[0].source,factId:"other"}});}
    if (invalid === "nonfinite") {items[2].value=Infinity; blocks[2].value="Infinity";}
    const result = groupTableAnalysisMetrics(blocks, items);
    expect(result.groups).toHaveLength(0);
    expect(result.remaining).toHaveLength(blocks.length);
  });

  it("keeps separate artifacts with identical column names and exposes extended statistics", async () => {
    const user = userEvent.setup();
    const items = [...facts("column",{column:"energy/eV",count:4,missing:0,mean:2.5,std:1.2,min:1,median:2.5,max:4},"table.numeric","a"),
      ...facts("column",{column:"energy/eV",count:4,missing:0,mean:25,std:12,min:10,median:25,max:40},"table.numeric","b")];
    const grouped = groupTableAnalysisMetrics(metrics(items), items);
    expect(grouped.groups).toHaveLength(2);
    expect(grouped.remaining).toHaveLength(0);
    render(<TableAnalysisMetrics groups={grouped.groups} artifacts={[]} />);
    const tables = screen.getAllByRole("table");
    expect(tables[0].querySelector('[data-fact-id="a:column:mean"]')).toHaveTextContent("2.5");
    expect(within(tables[1]).queryByText("2.5")).toBeNull();
    expect(within(tables[0]).queryByRole("columnheader",{name:"最大值"})).toBeNull();
    await user.click(screen.getAllByRole("button",{name:"全部统计"})[0]);
    expect(within(tables[0]).getByRole("columnheader",{name:"最大值"})).toBeVisible();
  });

  it("preserves extra groups behind an explicit disclosure and exact source links", async () => {
    const user = userEvent.setup();
    const items = [...pairs(1),...facts("n",{column:"energy",mean:2},"table.numeric","summary"),
      ...facts("h",{column:"energy",mean:2},"histogram","histogram")];
    const grouped = groupTableAnalysisMetrics(metrics(items),items);
    render(<TableAnalysisMetrics groups={grouped.groups} artifacts={[{artifactId:"matrix",jobId:"job",type:"table_json"}]} />);
    expect(screen.getByRole("link",{name:"来源数据"})).toHaveAttribute("href","/api/planner/jobs/job/artifacts/matrix/content");
    expect(screen.getByRole("heading",{name:"直方图统计"})).not.toBeVisible();
    await user.click(screen.getByText("更多统计 · 1 组"));
    expect(screen.getByRole("heading",{name:"直方图统计"})).toBeVisible();
  });
});
