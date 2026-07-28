import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import { compositionSpaceArtifact } from "../composition-space/testFixtures";
import { DatasetMaterialsExplorerPanel } from "./DatasetMaterialsExplorerPanel";

function payload() {
  return {
    schemaVersion: "phase10k2.dataset_materials_explorer.v1",
    artifactType: "dataset.materials_explorer",
    dataset: { datasetId: "dataset_demo", profileId: "profile_demo", profileContractVersion: "2.0", semanticHash: "a".repeat(64), datasetType: "mixed_material_dataset" },
    overview: { sampleCount: 4, tableCount: 1, structureCount: 2, propertyCount: 2, availableAnalyses: ["dataset_materials_explorer", "composition_summary"], unavailableAnalyses: ["regression_evaluation"] },
    composition: { status: "READY", formulaColumn: "formula", uniqueFormulaCount: 3, uniqueReducedFormulaCount: 2, elements: [{ element: "Si", materialsContainingElement: 2 }, { element: "Na", materialsContainingElement: 1 }], chemicalSystems: [{ chemicalSystem: "Si", count: 2 }, { chemicalSystem: "Cl-Na", count: 1 }] },
    structures: { status: "READY", structureCount: 1, records: [{ objectId: "obj_si", formula: "Si", siteCount: 2, volumeAngstrom3: 40.1, densityGramCm3: 2.33, spacegroup: "Fd-3m", crystalSystem: "cubic" }] },
    properties: { status: "READY", properties: [
      { column: "band_gap", unit: "eV", count: 4, missingCount: 0, nonFiniteCount: 0, statistics: { min: 1, q1: 1.1, median: 2, q3: 4, max: 6, mean: 2.5, std: 1.2 }, histogram: { counts: [1, 2, 1] } },
      { column: "density", unit: "g/cm^3", count: 3, missingCount: 1, nonFiniteCount: 0, statistics: { min: 2, q1: 2.1, median: 2.3, q3: 2.4, max: 2.5, mean: 2.3, std: 0.2 }, histogram: { counts: [1, 1, 1] } },
    ] },
    quality: { invalidFormulaCount: 1, sampleLinksMaterialized: 2, nearDuplicateAnalysis: "NOT_IMPLEMENTED_BY_DESIGN", columnIssues: [{ column: "density", missingCount: 1, nonFiniteCount: 0, ambiguities: [] }], duplicateSampleIdentityValues: [] },
    comparison: { status: "READY", mode: "group", binding: { groupColumn: "split", groupA: "train", groupB: "test" }, elementOverlap: { shared: ["Si"], leftOnly: ["Na"], rightOnly: ["Li"] }, propertyComparison: [{ column: "band_gap", unit: "eV", comparable: true, left: { median: 2 }, right: { median: 3 } }], semantics: "explicitly bound groups/resources; no row-order inference" },
    sampleIndex: [{ sampleRef: "sample-1", objectId: "obj_table", rowIndex: 0, formula: "Si", reducedFormula: "Si" }, { sampleRef: "sample-2", objectId: "obj_table", rowIndex: 1, formula: "NaCl", reducedFormula: "NaCl" }],
    warnings: ["FORMULA_VALUES_PARTIALLY_INVALID"],
  };
}

function artifact(content: unknown = payload()): Artifact {
  return { artifactId: "artifact_explorer", id: "artifact_explorer", name: "dataset_materials_explorer.json", type: "table_json", content };
}

describe("DatasetMaterialsExplorerPanel", () => {
  it("renders the bounded overview and semantic identity", () => {
    render(<DatasetMaterialsExplorerPanel artifacts={[artifact()]} />);
    expect(screen.getByTestId("dataset-materials-explorer")).toBeTruthy();
    expect(screen.getByTestId("dataset-explorer-dataset-id")).toHaveTextContent("dataset_demo");
    const overview = screen.getByTestId("dataset-explorer-overview");
    expect(overview).toHaveTextContent("Samples");
    expect(overview).toHaveTextContent("dataset_materials_explorer");
    expect(overview).toHaveTextContent("FORMULA_VALUES_PARTIALLY_INVALID");
  });

  it("supports composition, property and stable sample inspection without executing code", async () => {
    const user = userEvent.setup();
    const { container } = render(<DatasetMaterialsExplorerPanel artifacts={[artifact()]} />);
    await user.click(screen.getByRole("tab", { name: "Composition" }));
    expect(screen.getByTestId("dataset-element-bars")).toHaveTextContent("Si");
    expect(screen.getByTestId("dataset-explorer-composition")).toHaveTextContent("Cl-Na");

    await user.click(screen.getByRole("tab", { name: "Properties" }));
    await user.selectOptions(screen.getByRole("combobox", { name: "Property" }), "density");
    expect(screen.getByTestId("dataset-explorer-properties")).toHaveTextContent("g/cm^3");
    expect(screen.getByTestId("dataset-property-histogram").children).toHaveLength(3);

    await user.click(screen.getByRole("tab", { name: "Samples" }));
    await user.click(screen.getByRole("button", { name: "sample-2" }));
    expect(screen.getByTestId("dataset-sample-inspector")).toHaveTextContent("NaCl");
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
    expect(container.querySelector("canvas")).toBeNull();
  });

  it("shows explicit comparison provenance", async () => {
    const user = userEvent.setup();
    render(<DatasetMaterialsExplorerPanel artifacts={[artifact()]} />);
    await user.click(screen.getByRole("tab", { name: "Comparison" }));
    const view = screen.getByTestId("dataset-explorer-comparison");
    expect(view).toHaveTextContent("split");
    expect(view).toHaveTextContent("no row-order inference");
    expect(view).toHaveTextContent("Left median");
  });

  it("keeps partial and empty capabilities explicit and accessible", async () => {
    const user = userEvent.setup();
    const partial = payload();
    partial.composition = { ...partial.composition, status: "UNAVAILABLE", elements: [], chemicalSystems: [] };
    partial.structures = { ...partial.structures, status: "UNAVAILABLE", structureCount: 0, records: [] };
    partial.properties = { status: "UNAVAILABLE", properties: [] };
    partial.quality = { ...partial.quality, columnIssues: [], duplicateSampleIdentityValues: [] };
    partial.comparison = { ...partial.comparison, status: "NOT_REQUESTED", mode: "none" };
    partial.sampleIndex = [];
    render(<DatasetMaterialsExplorerPanel artifacts={[artifact(partial)]} />);
    expect(screen.getByLabelText("Dataset Materials Explorer")).toBeTruthy();
    expect(screen.getAllByRole("tab")).toHaveLength(8);
    await user.click(screen.getByRole("tab", { name: "Composition" }));
    expect(screen.getByText("Formula semantics are unavailable.")).toBeTruthy();
    await user.click(screen.getByRole("tab", { name: "Structures" }));
    expect(screen.getByText("No canonical structures were bound.")).toBeTruthy();
    await user.click(screen.getByRole("tab", { name: "Properties" }));
    expect(screen.getByText("No Profile 2.0 material-property roles are available.")).toBeTruthy();
    await user.click(screen.getByRole("tab", { name: "Comparison" }));
    expect(screen.getByText("No explicit dataset comparison was requested.")).toBeTruthy();
    await user.click(screen.getByRole("tab", { name: "Model evaluation" }));
    expect(screen.getByText("No model-result semantics detected.")).toBeTruthy();
  });

  it("links Profile-ready model semantics to the Materials ML product", async () => {
    const user = userEvent.setup();
    const ready = payload();
    ready.overview.availableAnalyses.push("regression_evaluation", "uncertainty_evaluation");
    render(<DatasetMaterialsExplorerPanel artifacts={[artifact(ready)]} />);
    await user.click(screen.getByRole("tab", { name: "Model evaluation" }));
    const view = screen.getByTestId("dataset-explorer-model-evaluation");
    expect(view).toHaveTextContent("regression_evaluation");
    expect(view).toHaveTextContent("uncertainty_evaluation");
    expect(view).toHaveTextContent("stable material samples");
  });

  it("integrates Composition Space as a dataset tab when both artifacts are present", async () => {
    const user = userEvent.setup();
    render(<DatasetMaterialsExplorerPanel artifacts={[artifact(), compositionSpaceArtifact()]} />);
    expect(screen.getAllByRole("tab")).toHaveLength(9);
    await user.click(screen.getByRole("tab", { name: "Composition space" }));
    expect(screen.getByRole("tabpanel")).toHaveTextContent("Backend-computed atomic-fraction PCA");
    expect(screen.getByRole("img", { name: "PCA composition scatter colored by cluster" })).toBeTruthy();
  });

  it("renders malicious labels as inert text", async () => {
    const user = userEvent.setup();
    const malicious = payload();
    malicious.composition.elements[0].element = "<img src=x onerror=alert(1)>";
    const { container } = render(<DatasetMaterialsExplorerPanel artifacts={[artifact(malicious)]} />);
    await user.click(screen.getByRole("tab", { name: "Composition" }));
    expect(screen.getByTestId("dataset-element-bars")).toHaveTextContent("<img src=x onerror=alert(1)>");
    expect(container.querySelector("img")).toBeNull();
  });

  it("rejects unknown schemas and over-cap preview arrays before product rendering", () => {
    const invalid = payload();
    invalid.schemaVersion = "unknown";
    const { rerender } = render(<DatasetMaterialsExplorerPanel artifacts={[artifact(invalid)]} />);
    expect(screen.getByTestId("dataset-materials-explorer-invalid")).toHaveTextContent("DATASET_EXPLORER_SCHEMA_UNSUPPORTED");

    const overCap = payload();
    overCap.sampleIndex = Array.from({ length: 201 }, (_, index) => ({
      sampleRef: `sample-${index}`,
      objectId: "obj_materials",
      rowIndex: index,
      formula: "Si",
      reducedFormula: "Si",
    }));
    rerender(<DatasetMaterialsExplorerPanel artifacts={[artifact(overCap)]} />);
    const fallback = screen.getByTestId("dataset-materials-explorer-invalid");
    expect(fallback).toHaveTextContent("DATASET_EXPLORER_PREVIEW_CAP_EXCEEDED");
    expect(within(fallback).getByText("Artifact JSON")).toBeTruthy();
  });
});
