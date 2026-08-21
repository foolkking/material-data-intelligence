import { describe, expect, it } from "vitest";
import type { Artifact } from "./planner-api";
import { projectScientificArtifacts, scientificResultTitle } from "./scientific-result-projection";

describe("scientific result projection", () => {
  it("assigns semantic primary and supporting roles without exposing technical outputs", () => {
    const result = projectScientificArtifacts([
      { id: "plot", type: "plotly_json", name: "formation-energy-band-gap" },
      { id: "table", type: "table_json", name: "summary" },
      { id: "recipe", type: "recipe_json", name: "recipe.json" },
    ]);
    expect(result.map((item) => item.resultRole)).toEqual(["PRIMARY_FIGURE", "SUPPORTING_TABLE"]);
    expect(result[0].resultTitle).toBe("formation-energy-band-gap");
  });

  it("uses the scientific question as the stable result title", () => {
    expect(scientificResultTitle("比较 formation energy 与 band gap", [])).toBe("比较 formation energy 与 band gap");
  });

  it("projects known structure composition outputs into a scientific title", () => {
    expect(projectScientificArtifacts([{ id: "composition", type: "table_json", name: "structure_composition.json" }])[0].resultTitle).toBe("结构组成概览");
  });

  it("names validated three-dimensional structure output from its tool identity", () => {
    expect(projectScientificArtifacts([{
      id: "structure-3d",
      type: "plotly_json",
      name: "figure.json",
      metadata: { toolId: "structure.structure_3d" },
    }])[0].resultTitle).toBe("晶体结构三维视图");
  });
});

it("prefers a specific scientific artifact title over a raw foreign-language question", () => {
  expect(scientificResultTitle(
    "Compare the supplied experimental XRD peaks with the theoretical pattern for this structure.",
    [{ id: "a", type: "plotly_json", name: "experimental_xrd_comparison_plot.json" } as Artifact],
)).toBe("实验与理论 XRD 对比图");
});

it("humanizes grounded correlation scopes in result titles", () => {
  expect(scientificResultTitle(null, [], {
    claims: [{ claimType: "OBSERVATION", scope: "correlation:formation_energy:band_gap" }],
  } as never)).toBe("formation_energy 与 band_gap 的相关关系");
});

it("maps internal correlation artifact names to scientific product titles", () => {
  expect(projectScientificArtifacts([
    { id: "heatmap", type: "plotly_json", name: "correlation_heatmap" } as Artifact,
  ])[0].resultTitle).toBe("形成能与带隙的相关关系");
});

it("keeps a specific composition-space title ahead of a generic interpretation scope", () => {
  const artifacts = [
    { id: "composition", type: "plotly_json", name: "composition_space_plot.json" } as Artifact,
  ];
  expect(projectScientificArtifacts(artifacts)[0].resultTitle).toBe("材料组成空间");
  expect(scientificResultTitle("Map the composition space.", artifacts, {
    claims: [{ claimType: "OBSERVATION", renderedText: "已生成组成空间。", scope: "dataset" }],
  } as never)).toBe("材料组成空间");
});

it("projects a scientific composite before bundle internals", () => {
  const result = projectScientificArtifacts([
    { id: "manifest", type: "phonon_manifest_json", name: "phonon_band_dos_manifest.json" } as Artifact,
    { id: "band", type: "phonon_band_json", name: "phonon_band.json" } as Artifact,
    { id: "combined", type: "phonon_band_dos_json", name: "phonon_band_dos.json" } as Artifact,
    { id: "compatibility", type: "phonon_compatibility_json", name: "phonon_band_dos_compatibility_report.json" } as Artifact,
    { id: "bz", type: "brillouin_zone_json", name: "brillouin_zone.json" } as Artifact,
  ]);
  expect(result.map((item) => item.id)).toEqual(["combined", "band", "bz"]);
  expect(result[0]).toMatchObject({ resultRole: "PRIMARY_FIGURE", resultTitle: "声子色散与态密度" });
});

it("keeps a phonon composite as the single primary scientific output", () => {
  const result = projectScientificArtifacts([
    { id: "combined", type: "phonon_band_dos_json", name: "phonon_band_dos.json" } as Artifact,
    { id: "plot", type: "plotly_json", name: "phonon_band_dos_plot.json" } as Artifact,
    { id: "band-plot", type: "plotly_json", name: "phonon_band_plot.json" } as Artifact,
    { id: "dos-table", type: "table_json", name: "phonon_dos_table.json" } as Artifact,
    { id: "bz", type: "brillouin_zone_json", name: "brillouin_zone.json" } as Artifact,
  ]);
  expect(result.map((item) => item.id)).toEqual(["combined", "bz"]);
});

it("uses a composite scientific title when electronic band and DOS outputs coexist", () => {
  expect(scientificResultTitle("plot the electronic structure", [
    { id: "band", type: "electronic_band_json", name: "electronic_band.json" } as Artifact,
    { id: "dos", type: "electronic_dos_json", name: "electronic_dos.json" } as Artifact,
  ])).toBe("电子能带与态密度");
});
