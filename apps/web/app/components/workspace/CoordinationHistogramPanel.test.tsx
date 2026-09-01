import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import { CoordinationHistogramPanel, inspectCoordinationHistogram } from "./CoordinationHistogramPanel";

describe("CoordinationHistogramPanel", () => {
  it("renders authoritative all-site and element distributions without recomputation", () => {
    render(<CoordinationHistogramPanel artifacts={artifacts()} />);

    expect(screen.getByRole("heading", { name: "配位数分布" })).toBeInTheDocument();
    expect(screen.getByText("2.1 Å")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "全部位点配位数分布，共 3 个位点" })).toBeInTheDocument();
    const table = screen.getByRole("table", { name: "配位数分布数值表" });
    expect(within(table).getByRole("row", { name: "1 2 66.67%" })).toBeInTheDocument();

    fireEvent.change(screen.getByRole("combobox", { name: "选择配位分布范围" }), { target: { value: "element:Si" } });
    expect(screen.getByRole("img", { name: "Si 位点配位数分布，共 3 个位点" })).toBeInTheDocument();
    expect(screen.getByText("固定距离截断邻居统计，不等同于 CrystalNN、VoronoiNN 或化学键级判断。", { exact: false })).toBeInTheDocument();
  });

  it("rejects executable or inconsistent histogram payloads", () => {
    const unsafe = artifacts();
    (unsafe[0].content as Record<string, any>).security.contains_javascript = true;
    expect(inspectCoordinationHistogram(unsafe)).toEqual({ ok: false, reason: "COORDINATION_HISTOGRAM_SECURITY_INVALID" });

    const inconsistent = artifacts();
    (inconsistent[0].content as Record<string, any>).histogram.total_sites = 99;
    render(<CoordinationHistogramPanel artifacts={inconsistent} />);
    expect(screen.getByTestId("coordination-histogram-invalid")).toHaveTextContent("COORDINATION_HISTOGRAM_BINS_INVALID");
  });
});

function artifacts(): Artifact[] {
  return [
    {
      id: "artifact-hist",
      artifactId: "artifact-hist",
      jobId: "job-hist",
      type: "table_json",
      name: "coordination_hist.json",
      content: {
        artifactType: "structure.coordination_hist",
        schema_version: "phase10e1.coordination_hist.v1",
        structureCount: 1,
        structure: { formula: "Si3", site_count: 3, species: ["Si"], pbc: [true, true, true] },
        parameters: { neighbor_policy: "distance_cutoff", cutoff_angstrom: 2.1 },
        histogram: {
          total_sites: 3,
          bins: [
            { coordination_number: 1, count: 2, fraction: 0.666667 },
            { coordination_number: 2, count: 1, fraction: 0.333333 },
          ],
        },
        by_element: [{
          element: "Si",
          total_sites: 3,
          bins: [
            { coordination_number: 1, count: 2, fraction: 0.666667 },
            { coordination_number: 2, count: 1, fraction: 0.333333 },
          ],
        }],
        pair_counts: [{ center_element: "Si", neighbor_element: "Si", count: 4 }],
        limits: { max_sites: 500, max_neighbors_per_site: 128, site_count_before_truncation: 3, truncated: false },
        warnings: ["COORDINATION_CUTOFF_SENSITIVE"],
        security: { contains_javascript: false, external_urls: [], external_urls_allowed: false },
      },
    } as Artifact,
    {
      id: "artifact-plot",
      artifactId: "artifact-plot",
      jobId: "job-hist",
      type: "plotly_json",
      name: "coordination_hist_plot.json",
      content: {
        artifactType: "structure.coordination_hist_plot",
        schema_version: "phase10e1.static_chart.v1",
        title: "Coordination Number Histogram",
        x_axis: { label: "Coordination Number" },
        y_axis: { label: "Site Count" },
      },
    } as Artifact,
  ];
}
