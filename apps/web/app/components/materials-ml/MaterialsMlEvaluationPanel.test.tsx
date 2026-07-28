import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import { MaterialsMlEvaluationPanel } from "./MaterialsMlEvaluationPanel";

const dataset = { datasetId: "materials", datasetVersion: "2", profileId: "profile_materials_v2", profileContractVersion: "2.0", semanticHash: "a".repeat(64), datasetContentHash: "b".repeat(64), resourceBindings: [{ objectId: "obj_table", objectType: "table", objectHash: "c".repeat(64) }] };
const security = { artifactJavaScript: false, externalUrls: false, externalAssets: false, executableContent: false };

function artifact(name: string, content: unknown): Artifact {
  return { artifactId: name, id: name, name, type: "table_json", content };
}

function regression() {
  return {
    schemaVersion: "phase10k3.materials_ml_regression.v1",
    artifactType: "ml.regression_evaluation",
    dataset,
    residualConvention: "prediction_minus_target",
    evaluations: [{
      taskId: "regression:model_a", groupId: "regression", seriesId: "model_a", targetColumn: "y_true", predictionColumn: "model_a_pred", unit: "eV",
      coverage: { totalSamples: 3, evaluatedSamples: 3 },
      metrics: { mae: 0.2, rmse: 0.25, r2: 0.9, meanSignedError: 0.05 },
      parityPoints: [
        { sampleKey: "obj_table:s1", sampleRef: "s1", objectId: "obj_table", rowIndex: 0, formula: "Si", chemicalSystem: "Si", target: 1, prediction: 1.1, residual: 0.1, absoluteError: 0.1 },
        { sampleKey: "obj_table:s2", sampleRef: "s2", objectId: "obj_table", rowIndex: 1, formula: "NaCl", chemicalSystem: "Cl-Na", target: 2, prediction: 2.5, residual: 0.5, absoluteError: 0.5 },
      ],
      residualHistogram: { counts: [1, 2, 1], edges: [-1, 0, 1, 2] },
      highErrorSamples: [{ sampleKey: "obj_table:s2", sampleRef: "s2", objectId: "obj_table", rowIndex: 1, formula: "NaCl", chemicalSystem: "Cl-Na", target: 2, prediction: 2.5, residual: 0.5, absoluteError: 0.5 }],
      chemistryConditioned: { byElement: [{ group: "Na", sampleCount: 1, mae: 0.5, rmse: 0.5 }], byChemicalSystem: [{ group: "Cl-Na", sampleCount: 1, mae: 0.5, rmse: 0.5 }] },
      warnings: [],
    }],
    modelComparisons: [{ targetColumn: "y_true", commonSampleCount: 3, policy: "common_valid_samples", models: [{ seriesId: "model_a" }, { seriesId: "model_b" }] }],
    security: { ...security },
  };
}

function uncertainty() {
  return {
    schemaVersion: "phase10k3.materials_ml_uncertainty.v1", artifactType: "ml.uncertainty_evaluation", dataset,
    evaluations: [{ taskId: "uncertainty:model_a", uncertaintyKind: "source_defined_uncertainty", coverage: { totalSamples: 3, evaluatedSamples: 3 }, association: { pearson: 0.8, spearman: 1 }, uncertaintyErrorPoints: [{ sampleKey: "obj_table:s1", sampleRef: "s1", objectId: "obj_table", rowIndex: 0, uncertainty: 0.1, absoluteError: 0.05 }, { sampleKey: "obj_table:s2", sampleRef: "s2", objectId: "obj_table", rowIndex: 1, uncertainty: 0.5, absoluteError: 0.4 }], reliability: { bins: [{ bin: 0, sampleCount: 2, meanUncertainty: 0.15, meanAbsoluteError: 0.1 }] }, errorDecay: { points: [{ retainedFraction: 1, mae: 0.2 }, { retainedFraction: 0.5, mae: 0.1 }] }, highUncertaintySamples: [{ sampleKey: "obj_table:s2", sampleRef: "s2", objectId: "obj_table", rowIndex: 1, formula: "NaCl", uncertainty: 0.5, absoluteError: 0.4 }], warnings: ["UNCERTAINTY_DIAGNOSTIC_NOT_CALIBRATION_AUTHORITY"] }],
    security: { ...security },
  };
}

function classification() {
  return {
    schemaVersion: "phase10k3.materials_ml_classification.v1", artifactType: "ml.classification_evaluation", dataset,
    evaluations: [{ taskId: "classification:default", coverage: { totalSamples: 4, evaluatedSamples: 4 }, metrics: { accuracy: 0.75, macroPrecision: 0.83, macroRecall: 0.75, macroF1: 0.73, confusionMatrix: { labels: ["a", "b"], values: [[1, 1], [0, 2]] }, perClass: [{ class: "a", support: 2, precision: 1, recall: 0.5, f1: 0.67 }, { class: "b", support: 2, precision: 0.67, recall: 1, f1: 0.8 }] }, curves: { status: "READY", positiveClass: "b", roc: { auc: 0.9, points: [{ fpr: 0, tpr: 0 }, { fpr: 0, tpr: 1 }, { fpr: 1, tpr: 1 }] }, precisionRecall: { averagePrecision: 0.88, points: [{ recall: 0, precision: 1 }, { recall: 1, precision: 0.5 }] } }, misclassifiedSamples: [{ sampleKey: "obj_table:s2", sampleRef: "s2", objectId: "obj_table", rowIndex: 1, formula: "NaCl", actualClass: "a", predictedClass: "b" }], sampleRows: [], warnings: ["CLASSIFICATION_PERFORMANCE_NOT_SCIENTIFIC_VALIDITY"] }],
    security: { ...security },
  };
}

describe("MaterialsMlEvaluationPanel", () => {
  it("renders regression metrics, charts, chemistry and linked high-error samples", () => {
    render(<MaterialsMlEvaluationPanel artifacts={[artifact("materials_ml_regression.json", regression())]} />);
    const panel = screen.getByTestId("materials-ml-regression");
    expect(panel).toHaveTextContent("MAE");
    expect(screen.getByTestId("materials-ml-evaluation")).toHaveTextContent("prediction_minus_target");
    expect(screen.getByRole("img", { name: "target versus prediction" })).toBeTruthy();
    expect(screen.getByRole("img", { name: "target versus residual" })).toBeTruthy();
    expect(screen.getByTestId("materials-ml-high-error-table")).toHaveTextContent("s2");
    expect(panel).toHaveTextContent("Element groups overlap");
    expect(screen.getByTestId("materials-ml-model-comparison")).toHaveTextContent("common_valid_samples");
  });

  it("switches between available bounded products and preserves explicit uncertainty policy", async () => {
    const user = userEvent.setup();
    render(<MaterialsMlEvaluationPanel artifacts={[artifact("materials_ml_regression.json", regression()), artifact("materials_ml_uncertainty.json", uncertainty())]} />);
    await user.selectOptions(screen.getByRole("combobox", { name: "Product" }), "materials_ml_uncertainty.json");
    expect(screen.getByTestId("materials-ml-uncertainty")).toHaveTextContent("source_defined_uncertainty");
    expect(screen.getByTestId("materials-ml-reliability-table")).toHaveTextContent("Mean uncertainty");
    expect(screen.getByTestId("materials-ml-high-uncertainty-table")).toHaveTextContent("s2");
  });

  it("renders raw classification counts, per-class metrics and explicit-positive-class curves", () => {
    render(<MaterialsMlEvaluationPanel artifacts={[artifact("materials_ml_classification.json", classification())]} />);
    expect(screen.getByTestId("materials-ml-confusion-matrix")).toHaveTextContent("Actual / predicted");
    expect(screen.getByTestId("materials-ml-class-metrics")).toHaveTextContent("Support");
    expect(screen.getByRole("img", { name: "tpr by fpr" })).toBeTruthy();
    expect(screen.getByTestId("materials-ml-misclassified-table")).toHaveTextContent("NaCl");
  });

  it("keeps classification metrics usable while clearly withholding ROC/PR without probabilities", () => {
    const payload: unknown = classification();
    const mutable = payload as { evaluations: Array<{ curves: { status: string; positiveClass: string; roc: unknown; precisionRecall: unknown } }> };
    mutable.evaluations[0].curves = { status: "UNAVAILABLE_CLASS_PROBABILITY_MISSING", positiveClass: "b", roc: null, precisionRecall: null };
    render(<MaterialsMlEvaluationPanel artifacts={[artifact("materials_ml_classification.json", payload)]} />);
    expect(screen.getByTestId("materials-ml-confusion-matrix")).toBeTruthy();
    expect(screen.getByTestId("materials-ml-curves-unavailable")).toHaveTextContent("UNAVAILABLE_CLASS_PROBABILITY_MISSING");
  });

  it("renders malicious labels as text and never creates executable surfaces", () => {
    const payload = classification();
    payload.evaluations[0].misclassifiedSamples[0].formula = "<img src=x onerror=alert(1)>";
    const { container } = render(<MaterialsMlEvaluationPanel artifacts={[artifact("materials_ml_classification.json", payload)]} />);
    expect(screen.getByTestId("materials-ml-misclassified-table")).toHaveTextContent("<img src=x onerror=alert(1)>");
    expect(container.querySelector("img, script, iframe, canvas")).toBeNull();
  });

  it("rejects unknown schemas, executable declarations and over-cap arrays", () => {
    const invalid = regression();
    invalid.schemaVersion = "unknown";
    const { rerender } = render(<MaterialsMlEvaluationPanel artifacts={[artifact("materials_ml_regression.json", invalid)]} />);
    expect(screen.getByTestId("materials-ml-invalid")).toHaveTextContent("MATERIALS_ML_SCHEMA_UNSUPPORTED");

    const unsafe = regression();
    unsafe.security.artifactJavaScript = true;
    rerender(<MaterialsMlEvaluationPanel artifacts={[artifact("materials_ml_regression.json", unsafe)]} />);
    expect(screen.getByTestId("materials-ml-invalid")).toHaveTextContent("MATERIALS_ML_SECURITY_DECLARATION_INVALID");

    const overCap = regression();
    overCap.evaluations[0].highErrorSamples = Array.from({ length: 201 }, (_, index) => ({
      sampleKey: `obj_table:s${index}`,
      sampleRef: `s${index}`,
      objectId: "obj_table",
      rowIndex: index,
      formula: "Si",
      chemicalSystem: "Si",
      target: 1,
      prediction: 1,
      residual: 0,
      absoluteError: 0,
    }));
    rerender(<MaterialsMlEvaluationPanel artifacts={[artifact("materials_ml_regression.json", overCap)]} />);
    expect(screen.getByTestId("materials-ml-invalid")).toHaveTextContent("MATERIALS_ML_PREVIEW_CAP_EXCEEDED");
  });

  it("defaults to the first valid sibling and keeps a rejected product selectable", async () => {
    const user = userEvent.setup();
    const invalid = regression();
    invalid.schemaVersion = "unknown";
    render(<MaterialsMlEvaluationPanel artifacts={[
      artifact("materials_ml_regression.json", invalid),
      artifact("materials_ml_uncertainty.json", uncertainty()),
    ]} />);
    expect(screen.getByTestId("materials-ml-uncertainty")).toBeTruthy();
    await user.selectOptions(screen.getByRole("combobox", { name: "Product" }), "materials_ml_regression.json");
    expect(screen.getByTestId("materials-ml-invalid")).toHaveTextContent("MATERIALS_ML_SCHEMA_UNSUPPORTED");
  });
});
