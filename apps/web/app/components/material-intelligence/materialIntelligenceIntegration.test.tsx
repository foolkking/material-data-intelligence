import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import { compositionSpaceArtifact, compositionSpacePayload } from "../composition-space/testFixtures";
import { MaterialIntelligenceIntegrationPanel, assessMaterialIntelligenceProducts } from "./MaterialIntelligenceIntegrationPanel";
import { canonicalSampleKey, inspectMaterialIntelligenceArtifacts } from "./materialIntelligenceIntegration";

const binding = {
  datasetId: "materials",
  datasetVersion: "1",
  profileId: "profile_materials_v2",
  profileContractVersion: "2.0",
  semanticHash: "a".repeat(64),
  datasetContentHash: "b".repeat(64),
  resourceBindings: [{ objectId: "obj_table", objectType: "table", objectHash: "c".repeat(64) }],
};
const security = { artifactJavaScript: false, externalUrls: false, externalAssets: false, executableContent: false };

function artifact(name: string, content: unknown): Artifact {
  return { artifactId: name, id: name, name, type: "table_json", content };
}

function explorerPayload() {
  return {
    schemaVersion: "phase10k2.dataset_materials_explorer.v1",
    artifactType: "dataset.materials_explorer",
    dataset: { ...binding, datasetType: "materials_table" },
    overview: {
      sampleCount: 3,
      tableCount: 1,
      structureCount: 0,
      propertyCount: 1,
      availableAnalyses: ["dataset_materials_explorer", "composition_space", "regression_evaluation"],
      unavailableAnalyses: ["uncertainty_evaluation", "classification_evaluation"],
    },
    composition: { status: "READY", elements: [], chemicalSystems: [], duplicateReducedFormulaGroups: [] },
    structures: { status: "UNAVAILABLE", records: [] },
    properties: { status: "READY", properties: [] },
    quality: { columnIssues: [], duplicateSampleIdentityValues: [] },
    comparison: { status: "NOT_REQUESTED", propertyComparison: [] },
    sampleIndex: [],
    warnings: [],
    security,
  };
}

function regressionPayload() {
  return {
    schemaVersion: "phase10k3.materials_ml_regression.v1",
    artifactType: "ml.regression_evaluation",
    dataset: { ...binding },
    residualConvention: "prediction_minus_target",
    evaluations: [{
      taskId: "regression:model",
      coverage: { totalSamples: 1, evaluatedSamples: 1 },
      metrics: { mae: 0.1, rmse: 0.1, r2: null, meanSignedError: 0.1 },
      parityPoints: [{ sampleKey: "obj:s1", sampleRef: "s1", objectId: "obj", rowIndex: 0, target: 1, prediction: 1.1, residual: 0.1, absoluteError: 0.1 }],
      highErrorSamples: [],
      chemistryConditioned: { byElement: [], byChemicalSystem: [] },
      residualHistogram: { counts: [1] },
      warnings: [],
    }],
    security,
  };
}

function integratedArtifacts(): Artifact[] {
  const composition = compositionSpacePayload();
  composition.dataset = { ...binding };
  return [
    artifact("dataset_materials_explorer.json", explorerPayload()),
    artifact("materials_ml_regression.json", regressionPayload()),
    compositionSpaceArtifact(composition),
  ];
}

describe("materialIntelligenceIntegration", () => {
  it("binds produced products and keeps Profile-ready products distinct from unavailable data", () => {
    const result = assessMaterialIntelligenceProducts(integratedArtifacts());
    expect(result.authority?.binding?.datasetId).toBe("materials");
    expect(result.products.find((item) => item.id === "composition_space")?.state).toBe("PRODUCED");
    expect(result.products.find((item) => item.id === "regression")?.state).toBe("PRODUCED");
    expect(result.products.find((item) => item.id === "uncertainty")?.state).toBe("UNAVAILABLE");
    expect(result.hasCompatibleEmbeddedCompositionSpace).toBe(true);
  });

  it("quarantines stale semantic/content revisions without hiding valid siblings", () => {
    const artifacts = integratedArtifacts();
    const stale = compositionSpacePayload();
    stale.dataset = { ...binding, semanticHash: "c".repeat(64) };
    artifacts[2] = compositionSpaceArtifact(stale);
    const result = assessMaterialIntelligenceProducts(artifacts);
    expect(result.products.find((item) => item.id === "composition_space")).toMatchObject({
      state: "STALE",
      reason: "MATERIAL_INTELLIGENCE_SEMANTIC_HASH_MISMATCH",
    });
    expect(result.products.find((item) => item.id === "regression")?.state).toBe("PRODUCED");
    expect(result.hasCompatibleEmbeddedCompositionSpace).toBe(false);
  });

  it("does not enable a product from its filename alone", () => {
    const result = inspectMaterialIntelligenceArtifacts([
      artifact("dataset_materials_explorer.json", explorerPayload()),
      artifact("composition_space.json", { schemaVersion: "unknown", artifactType: "dataset.composition_space" }),
    ]);
    expect(result.products.find((item) => item.id === "composition_space")).toMatchObject({ state: "REJECTED", reason: "MATERIAL_INTELLIGENCE_PRODUCT_SCHEMA_INVALID" });
  });

  it("renders typed product states from the same integration assessment", () => {
    render(<MaterialIntelligenceIntegrationPanel artifacts={integratedArtifacts()} />);
    expect(screen.getByTestId("material-intelligence-integration")).toHaveTextContent("Profile-authoritative product surface");
    expect(screen.getByTestId("material-product-composition_space")).toHaveTextContent("PRODUCED");
    expect(screen.getByTestId("material-product-uncertainty")).toHaveTextContent("UNAVAILABLE");
    expect(screen.getByText(/filename alone never enables/)).toBeTruthy();
  });

  it("derives object-qualified identity and preserves an explicit legacy key", () => {
    expect(canonicalSampleKey({ objectId: "obj_b", sampleRef: "shared", rowIndex: 4 })).toBe("obj_b:shared");
    expect(canonicalSampleKey({ sampleKey: "legacy:stable", sampleRef: "shared" })).toBe("legacy:stable");
  });
});
