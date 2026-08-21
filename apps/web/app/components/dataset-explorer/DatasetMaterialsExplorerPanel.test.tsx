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
    dataset: { datasetId: "dataset_demo", datasetVersion: "2", profileId: "profile_demo", profileContractVersion: "2.0", semanticHash: "a".repeat(64), datasetContentHash: "b".repeat(64), resourceBindings: [{ objectId: "obj_table", objectType: "table", objectHash: "c".repeat(64) }], datasetType: "mixed_material_dataset" },
    overview: { sampleCount: 4, tableCount: 1, structureCount: 2, propertyCount: 2, availableAnalyses: ["dataset_materials_explorer", "composition_summary"], unavailableAnalyses: ["regression_evaluation"] },
    composition: { status: "READY", formulaColumn: "formula", uniqueFormulaCount: 3, uniqueReducedFormulaCount: 2, elements: [{ element: "Si", materialsContainingElement: 2 }, { element: "Na", materialsContainingElement: 1 }], chemicalSystems: [{ chemicalSystem: "Si", count: 2 }, { chemicalSystem: "Cl-Na", count: 1 }] },
    structures: { status: "READY", structureCount: 1, records: [{ objectId: "obj_si", formula: "Si", siteCount: 2, volumeAngstrom3: 40.1, densityGramCm3: 2.33, spacegroup: "Fd-3m", crystalSystem: "cubic" }] },
    properties: { status: "READY", properties: [
      { column: "band_gap", unit: "eV", count: 4, missingCount: 0, nonFiniteCount: 0, statistics: { min: 1, q1: 1.1, median: 2, q3: 4, max: 6, mean: 2.5, std: 1.2 }, histogram: { counts: [1, 2, 1] } },
      { column: "density", unit: "g/cm^3", count: 3, missingCount: 1, nonFiniteCount: 0, statistics: { min: 2, q1: 2.1, median: 2.3, q3: 2.4, max: 2.5, mean: 2.3, std: 0.2 }, histogram: { counts: [1, 1, 1] } },
    ] },
    quality: { invalidFormulaCount: 1, sampleLinksMaterialized: 2, nearDuplicateAnalysis: "NOT_IMPLEMENTED_BY_DESIGN", columnIssues: [{ column: "density", missingCount: 1, nonFiniteCount: 0, ambiguities: [] }], duplicateSampleIdentityValues: [] },
    comparison: { status: "READY", mode: "group", binding: { groupColumn: "split", groupA: "train", groupB: "test" }, elementOverlap: { shared: ["Si"], leftOnly: ["Na"], rightOnly: ["Li"] }, propertyComparison: [{ column: "band_gap", unit: "eV", comparable: true, left: { median: 2 }, right: { median: 3 } }], semantics: "explicitly bound groups/resources; no row-order inference" },
    sampleIndex: [{ sampleKey: "obj_table:sample-1", sampleRef: "sample-1", objectId: "obj_table", rowIndex: 0, formula: "Si", reducedFormula: "Si" }, { sampleKey: "obj_table:sample-2", sampleRef: "sample-2", objectId: "obj_table", rowIndex: 1, formula: "NaCl", reducedFormula: "NaCl" }],
    security: { artifactJavaScript: false, externalUrls: false, externalAssets: false, executableContent: false },
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
    expect(overview).toHaveTextContent("样本");
    expect(overview).toHaveTextContent("材料数据浏览");
    expect(overview).toHaveTextContent("部分化学式无法解析");
  });

  it("supports composition, property and stable sample inspection without executing code", async () => {
    const user = userEvent.setup();
    const { container } = render(<DatasetMaterialsExplorerPanel artifacts={[artifact()]} />);
    await user.click(screen.getByRole("tab", { name: "组成" }));
    expect(screen.getByTestId("dataset-element-bars")).toHaveTextContent("Si");
    expect(screen.getByTestId("dataset-explorer-composition")).toHaveTextContent("Cl-Na");

    await user.click(screen.getByRole("tab", { name: "性质" }));
    await user.selectOptions(screen.getByRole("combobox", { name: "性质" }), "density");
    expect(screen.getByTestId("dataset-explorer-properties")).toHaveTextContent("g/cm^3");
    expect(screen.getByTestId("dataset-property-histogram").children).toHaveLength(3);

    await user.click(screen.getByRole("tab", { name: "样本" }));
    await user.click(screen.getByRole("button", { name: "sample-2 from obj_table" }));
    expect(screen.getByTestId("dataset-sample-inspector")).toHaveTextContent("NaCl");
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
    expect(container.querySelector("canvas")).toBeNull();
  });

  it("shows explicit comparison provenance", async () => {
    const user = userEvent.setup();
    render(<DatasetMaterialsExplorerPanel artifacts={[artifact()]} />);
    await user.click(screen.getByRole("tab", { name: "比较" }));
    const view = screen.getByTestId("dataset-explorer-comparison");
    expect(view).toHaveTextContent("split");
    expect(view).toHaveTextContent("no row-order inference");
    expect(view).toHaveTextContent("左侧中位数");
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
    expect(screen.getByLabelText("材料数据浏览器")).toBeTruthy();
    expect(screen.getAllByRole("tab")).toHaveLength(8);
    await user.click(screen.getByRole("tab", { name: "组成" }));
    expect(screen.getByText("当前数据没有可用的化学式语义。")).toBeTruthy();
    await user.click(screen.getByRole("tab", { name: "结构" }));
    expect(screen.getByText("当前数据没有绑定可展示的标准结构。")).toBeTruthy();
    await user.click(screen.getByRole("tab", { name: "性质" }));
    expect(screen.getByText("当前数据没有可展示的材料性质字段。")).toBeTruthy();
    await user.click(screen.getByRole("tab", { name: "比较" }));
    expect(screen.getByText("当前没有请求数据集比较。")).toBeTruthy();
    await user.click(screen.getByRole("tab", { name: "模型评估" }));
    expect(screen.getByText("当前数据没有检测到模型结果语义。")).toBeTruthy();
  });

  it("links Profile-ready model semantics to the Materials ML product", async () => {
    const user = userEvent.setup();
    const ready = payload();
    ready.overview.availableAnalyses.push("regression_evaluation", "uncertainty_evaluation");
    render(<DatasetMaterialsExplorerPanel artifacts={[artifact(ready)]} />);
    await user.click(screen.getByRole("tab", { name: "模型评估" }));
    const view = screen.getByTestId("dataset-explorer-model-evaluation");
    expect(view).toHaveTextContent("回归评估");
    expect(view).toHaveTextContent("不确定性评估");
    expect(view).toHaveTextContent("稳定材料样本");
  });

  it("integrates Composition Space as a dataset tab when both artifacts are present", async () => {
    const user = userEvent.setup();
    const explorer = payload();
    explorer.dataset = { ...explorer.dataset, datasetId: "materials", datasetVersion: "1", profileId: "profile_materials_v2", semanticHash: "a".repeat(64), datasetContentHash: "b".repeat(64) };
    explorer.overview.availableAnalyses.push("composition_space");
    render(<DatasetMaterialsExplorerPanel artifacts={[artifact(explorer), compositionSpaceArtifact()]} />);
    expect(screen.getAllByRole("tab")).toHaveLength(9);
    await user.click(screen.getByRole("tab", { name: "组成空间" }));
    expect(screen.getByRole("tabpanel")).toHaveTextContent("Backend-computed atomic-fraction PCA");
    expect(screen.getByRole("img", { name: "PCA composition scatter colored by cluster" })).toBeTruthy();
  });

  it("keeps duplicate sample references object-qualified", async () => {
    const user = userEvent.setup();
    const duplicate = payload();
    duplicate.sampleIndex = [
      { sampleKey: "obj_a:shared", sampleRef: "shared", objectId: "obj_a", rowIndex: 0, formula: "Si", reducedFormula: "Si" },
      { sampleKey: "obj_b:shared", sampleRef: "shared", objectId: "obj_b", rowIndex: 0, formula: "NaCl", reducedFormula: "NaCl" },
    ];
    render(<DatasetMaterialsExplorerPanel artifacts={[artifact(duplicate)]} />);
    await user.click(screen.getByRole("tab", { name: "样本" }));
    await user.click(screen.getByRole("button", { name: "shared from obj_b" }));
    expect(screen.getByTestId("dataset-sample-inspector")).toHaveTextContent("obj_b:shared");
    expect(screen.getByTestId("dataset-sample-inspector")).toHaveTextContent("NaCl");
  });

  it("renders malicious labels as inert text", async () => {
    const user = userEvent.setup();
    const malicious = payload();
    malicious.composition.elements[0].element = "<img src=x onerror=alert(1)>";
    const { container } = render(<DatasetMaterialsExplorerPanel artifacts={[artifact(malicious)]} />);
    await user.click(screen.getByRole("tab", { name: "组成" }));
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
      sampleKey: `obj_materials:sample-${index}`,
      sampleRef: `sample-${index}`,
      objectId: "obj_materials",
      rowIndex: index,
      formula: "Si",
      reducedFormula: "Si",
    }));
    rerender(<DatasetMaterialsExplorerPanel artifacts={[artifact(overCap)]} />);
    const fallback = screen.getByTestId("dataset-materials-explorer-invalid");
    expect(fallback).toHaveTextContent("DATASET_EXPLORER_PREVIEW_CAP_EXCEEDED");
    expect(within(fallback).getByText("技术详情")).toBeTruthy();
  });
});
