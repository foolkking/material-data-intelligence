import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { compileScientificPresentation, type ScientificPresentationBlock } from "../../app/lib/scientific-presentation";
import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import { ScientificPresentationBlocks } from "./ScientificPresentationBlocks";
import { groupXrdPeakMetrics } from "./XrdPeakMetrics";

function factsForPeak(subject: string, angle: number, artifact = "artifact-1"): Agent2ScientificFact[] {
  return [
    ["two_theta", angle, "degree"], ["intensity", 75.000168, null], ["d_spacing", 4.063143, "angstrom"],
    ["structure", "LiPO2", null], ["hkl_0.component_0", 0, null], ["hkl_0.component_1", 1, null], ["hkl_0.component_2", -1, null],
  ].map(([predicate, value, unit]) => ({ fact_id: `${artifact}-${subject}-${predicate}`, predicate: `xrd.peak.${predicate}`, subject_ref: subject, value, unit: unit as string | null, source: { artifact_id: artifact } }));
}
function presentationFor(facts: Agent2ScientificFact[]) {
  return compileScientificPresentation({ resultId: "result-1", facts: facts.map(fact => ({
    factId: fact.fact_id, predicate: fact.predicate, subjectRef: fact.subject_ref, value: fact.value, unit: fact.unit,
    source: { artifactId: fact.source.artifact_id },
  })) });
}
function metricsFor(facts: Agent2ScientificFact[]) { return presentationFor(facts).blocks.filter((block): block is Extract<ScientificPresentationBlock, { type: "metric" }> => block.type === "metric"); }

describe("XRD peak correspondence", () => {
  it("shows one row per saved peak while keeping global facts and exact precision", () => {
    const facts = [...factsForPeak("peak-a", 20.498535), ...factsForPeak("peak-b", 21.874628),
      { fact_id: "wavelength", subject_ref: "artifact-1", predicate: "xrd.wavelength", value: 1.54184, unit: "angstrom", source: { artifact_id: "artifact-1" } }];
    render(<ScientificPresentationBlocks presentation={presentationFor(facts)} resultFacts={facts} />);
    const table = screen.getByRole("table");
    expect(within(table).getAllByRole("row")).toHaveLength(3);
    expect(within(table).getAllByText("(0, 1, -1)")).toHaveLength(2);
    expect(within(table).getByText("20.49854")).toHaveAttribute("data-exact-value", "20.498535");
    expect(screen.getByText("X 射线波长")).toBeInTheDocument();
    expect(screen.queryByText(/更多指标/)).toBeNull();
    expect(screen.queryByText(/xrd\.peak\.hkl/)).toBeNull();
    expect(screen.getByRole("region", { name: "主要衍射峰数据，可横向滚动" })).toHaveAttribute("tabindex", "0");
  });

  it("never combines complementary partial facts across artifacts or subjects", () => {
    const facts = [...factsForPeak("same-subject", 1, "artifact-a").slice(0, 2), ...factsForPeak("same-subject", 2, "artifact-b").slice(2)];
    const grouped = groupXrdPeakMetrics(metricsFor(facts), facts);
    expect(grouped.rows).toHaveLength(0);
    expect(grouped.remaining).toHaveLength(facts.length);
  });

  it.each(["incomplete-hkl", "conflict", "wrong-source", "wrong-unit"])("retains individual metrics when correspondence is %s", (failure) => {
    let facts = factsForPeak("peak-a", 20.498535);
    if (failure === "incomplete-hkl") facts = facts.slice(0, -1);
    if (failure === "conflict") facts.push({ ...facts[0], fact_id: "conflicting", value: 30 });
    if (failure === "wrong-unit") facts[0].unit = "radian";
    const metrics = metricsFor(facts);
    if (failure === "wrong-source") metrics[0].source.artifactId = "other-artifact";
    const grouped = groupXrdPeakMetrics(metrics, facts);
    expect(grouped.rows).toHaveLength(0);
    expect(grouped.remaining).toHaveLength(metrics.length);
  });
});
