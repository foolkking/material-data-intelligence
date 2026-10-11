// @vitest-environment node
import { describe, expect, it } from "vitest";
import { tableRows } from "./scientific-report-table-data";
import { readReportTablePreview, renderReportTableHtml, renderReportTableMarkdown } from "./scientific-report-table-export";

const structure = () => ({
  artifactType: "structure.rdf", schema_version: "phase10e7.rdf.v1",
  rdf: { r_angstrom: [0.05, 0.15], g_r: [0, 0.12345678901234568], counts: [0, 24] },
  partial_rdf: [
    { center_element: "Na", neighbor_element: "Cl", r_angstrom: [0.05, 0.15], g_r: [0, 2.3], counts: [0, 12] },
    { center_element: "Cl", neighbor_element: "Na", r_angstrom: [0.05, 0.15], g_r: [0, 4.6], counts: [0, 12] },
  ],
});
const trajectory = () => ({
  artifactType: "trajectory.rdf", schema_version: "phase10n4.trajectory_rdf.v1",
  units: { r: "angstrom", gR: "dimensionless" }, speciesPair: { speciesA: "Li", speciesB: "O", ordered: false },
  binCentersAngstrom: [0.1, 0.3], gR: [0, 12.123456789012345], pairCounts: [0, 44],
});

describe("saved RDF report tables", () => {
  it("preserves global and both directed partial distributions at saved precision", () => {
    const payload = structure(), before = JSON.stringify(payload);
    expect(tableRows(payload)).toEqual([
      { "中心 → 邻居": "全部原子对", "距离 r (Å)": 0.05, "g(r)": 0, "计数": 0 },
      { "中心 → 邻居": "全部原子对", "距离 r (Å)": 0.15, "g(r)": 0.12345678901234568, "计数": 24 },
      { "中心 → 邻居": "Na → Cl", "距离 r (Å)": 0.05, "g(r)": 0, "计数": 0 },
      { "中心 → 邻居": "Na → Cl", "距离 r (Å)": 0.15, "g(r)": 2.3, "计数": 12 },
      { "中心 → 邻居": "Cl → Na", "距离 r (Å)": 0.05, "g(r)": 0, "计数": 0 },
      { "中心 → 邻居": "Cl → Na", "距离 r (Å)": 0.15, "g(r)": 4.6, "计数": 12 },
    ]);
    expect(JSON.stringify(payload)).toBe(before);
    const preview = readReportTablePreview(payload)!;
    expect(preview.numericColumns).toEqual([false, true, true, true]);
    expect(renderReportTableHtml(preview, "RDF")).toContain('class="table-number">0.12345678901234568</td>');
    expect(renderReportTableMarkdown(preview)).toContain("| Cl → Na | 0.15 | 4.6 | 12 |");
  });

  it("supports global-only results and keeps frame-averaged trajectory pairs unordered", () => {
    expect(tableRows({ ...structure(), partial_rdf: [] })).toHaveLength(2);
    const payload = trajectory(), before = JSON.stringify(payload);
    expect(tableRows(payload)).toEqual([
      { "原子对": "Li – O", "距离 r (Å)": 0.1, "g(r)": 0, "计数": 0 },
      { "原子对": "Li – O", "距离 r (Å)": 0.3, "g(r)": 12.123456789012345, "计数": 44 },
    ]);
    expect(JSON.stringify(payload)).toBe(before);
  });

  it.each([
    { ...structure(), schema_version: "unknown" },
    { ...structure(), partial_rdf: null },
    { ...structure(), partial_rdf: [structure().partial_rdf[0], structure().partial_rdf[0]] },
    { ...structure(), partial_rdf: [{ ...structure().partial_rdf[0], r_angstrom: [0.05, 0.25] }] },
    { ...structure(), partial_rdf: [{ ...structure().partial_rdf[0], neighbor_element: "" }] },
    { ...structure(), rdf: { ...structure().rdf, counts: [0] } },
    { ...structure(), rdf: { ...structure().rdf, counts: [0, -1] } },
    { ...structure(), rdf: { ...structure().rdf, counts: [0, 1.5] } },
    { ...structure(), rdf: { ...structure().rdf, g_r: [0, null] } },
    { ...structure(), rdf: { ...structure().rdf, g_r: [0, "2.3"] } },
    { ...structure(), rdf: { ...structure().rdf, g_r: [0, Infinity] } },
    { ...structure(), rdf: { ...structure().rdf, r_angstrom: [0.15, 0.05] } },
    { ...trajectory(), units: { r: "nanometer", gR: "dimensionless" } },
    { ...trajectory(), speciesPair: { ...trajectory().speciesPair, ordered: true } },
    { ...trajectory(), pairCounts: [0, true] },
  ])("rejects incomplete, inconsistent or unsupported RDF instead of guessing or falling back", payload => {
    const value = { ...payload, rows: [{ invented: 42 }] };
    expect(tableRows(value)).toEqual([]);
    expect(readReportTablePreview(value)).toBeNull();
  });

  it("retains all saved rows online while disclosing the bounded export preview", () => {
    const payload = { ...structure(), rdf: {
      r_angstrom: Array.from({ length: 100 }, (_, i) => i + 0.5),
      g_r: Array.from({ length: 100 }, (_, i) => i), counts: Array.from({ length: 100 }, (_, i) => i * 2),
    }, partial_rdf: [] };
    expect(tableRows(payload)).toHaveLength(100);
    const preview = readReportTablePreview(payload)!;
    expect(preview.rows).toHaveLength(80);
    expect(preview.totalRows).toBe(100);
    expect(preview.notes).toContain("预览 80 / 100 行、4 / 4 列；完整数据见原始数据表。");
  });
});
