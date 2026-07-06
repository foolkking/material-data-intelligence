from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from pymatgen.core import Structure

from mdi_adapters import (
    BasicMetricsAdapter,
    ChemSysTreemapAdapter,
    CompositionSummaryAdapter,
    CorrelationAdapter,
    CoordinationHistAdapter,
    DensityScatterAdapter,
    DistributionSummaryAdapter,
    ElementsHistAdapter,
    ErrorDistributionAdapter,
    HistogramAdapter,
    NumericSummaryAdapter,
    OutlierTableAdapter,
    PTableHeatmapAdapter,
    ScatterAdapter,
    Structure3DAdapter,
    StructureViewer3DAdapter,
    ToolExecutionContext,
)
from mdi_schemas import ArtifactType, ToolExecutionRequest
from mdi_tool_registry import load_manifests


def make_context(tmp_path, tool_id: str, object_store: dict, tool_call_id: str) -> ToolExecutionContext:
    tool = load_manifests().get_tool_by_id(tool_id)
    return ToolExecutionContext(
        job_id="job_adapter",
        project_id="project_adapter",
        dataset_id="dataset_adapter",
        tool_id=tool_id,
        tool_version=tool.version,
        adapter_version="0.1.0",
        registry_version="0.1.0",
        artifact_root=tmp_path / "artifacts",
        tool_call_id=tool_call_id,
        object_store=object_store,
        resource_limits=tool.resourceLimits,
    )


def artifact_types(artifacts):
    return {artifact.type for artifact in artifacts}


def test_ptable_heatmap_generates_plotly_artifacts(tmp_path):
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_ptable",
        toolId="composition.ptable_heatmap",
        inputRefs=[{"refType": "normalized_object", "ref": "formulas", "objectType": "Composition"}],
        params={"colorScale": "viridis", "title": "Composition overview"},
        artifactTypes=["plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = PTableHeatmapAdapter().execute(
        make_context(tmp_path, "composition.ptable_heatmap", {"formulas": ["Fe2O3", "LiFePO4", "Si"]}, "call_ptable"),
        request,
    )

    assert artifact_types(artifacts) == {
        ArtifactType.plotly_json,
        ArtifactType.plotly_html,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
    assert all((tmp_path / "artifacts" / artifact.storageKey).exists() for artifact in artifacts)


def test_structure_3d_generates_plotly_artifacts_from_cif_fixture(tmp_path, repo_root):
    structure = Structure.from_file(repo_root / "tests" / "fixtures" / "structures" / "si.cif")
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_structure",
        toolId="structure.structure_3d",
        inputRefs=[{"refType": "normalized_object", "ref": "si_structure", "objectType": "Structure"}],
        params={"showCell": True, "showBonds": False, "maxStructures": 1},
        artifactTypes=["plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = Structure3DAdapter().execute(
        make_context(tmp_path, "structure.structure_3d", {"si_structure": structure}, "call_structure"),
        request,
    )

    assert ArtifactType.plotly_json in artifact_types(artifacts)
    assert ArtifactType.plotly_html in artifact_types(artifacts)
    assert ArtifactType.recipe_json in artifact_types(artifacts)


def test_structure_viewer_3d_generates_viewer_or_graceful_fallback(tmp_path, repo_root):
    structure = Structure.from_file(repo_root / "tests" / "fixtures" / "structures" / "si.cif")
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_viewer",
        toolId="structure.viewer_3d",
        inputRefs=[{"refType": "normalized_object", "ref": "si_structure", "objectType": "Structure"}],
        params={"showCell": True, "showBonds": "auto"},
        artifactTypes=["matterviz_html", "structure_json", "summary_md", "recipe_json"],
    )

    artifacts = StructureViewer3DAdapter().execute(
        make_context(tmp_path, "structure.viewer_3d", {"si_structure": structure}, "call_viewer"),
        request,
    )

    assert artifact_types(artifacts) == {
        ArtifactType.matterviz_html,
        ArtifactType.structure_json,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
    viewer = next(artifact for artifact in artifacts if artifact.type == ArtifactType.matterviz_html)
    assert (tmp_path / "artifacts" / viewer.storageKey).read_text(encoding="utf-8").startswith("<!DOCTYPE html>")


def test_elements_hist_generates_plotly_artifacts(tmp_path):
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_elements",
        toolId="composition.elements_hist",
        inputRefs=[{"refType": "normalized_object", "ref": "formulas", "objectType": "Composition"}],
        params={"countMode": "composition"},
        artifactTypes=["plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = ElementsHistAdapter().execute(
        make_context(tmp_path, "composition.elements_hist", {"formulas": ["Fe2O3", "LiFePO4", "Si"]}, "call_elements"),
        request,
    )

    assert artifact_types(artifacts) == {
        ArtifactType.plotly_json,
        ArtifactType.plotly_html,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }


def test_chem_sys_treemap_generates_plotly_artifacts(tmp_path):
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_chem_sys",
        toolId="composition.chem_sys_treemap",
        inputRefs=[{"refType": "normalized_object", "ref": "formulas", "objectType": "Composition"}],
        params={"showCounts": "value"},
        artifactTypes=["plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = ChemSysTreemapAdapter().execute(
        make_context(tmp_path, "composition.chem_sys_treemap", {"formulas": ["Fe2O3", "LiFePO4", "Si"]}, "call_chem_sys"),
        request,
    )

    assert ArtifactType.plotly_json in artifact_types(artifacts)
    assert ArtifactType.plotly_html in artifact_types(artifacts)
    assert ArtifactType.recipe_json in artifact_types(artifacts)


def test_coordination_hist_generates_plotly_artifacts(tmp_path, repo_root):
    structure = Structure.from_file(repo_root / "tests" / "fixtures" / "structures" / "si.cif")
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_coordination",
        toolId="structure.coordination_hist",
        inputRefs=[{"refType": "normalized_object", "ref": "si_structure", "objectType": "Structure"}],
        params={"cutoff": 3.0, "splitMode": "by element"},
        artifactTypes=["plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = CoordinationHistAdapter().execute(
        make_context(tmp_path, "structure.coordination_hist", {"si_structure": structure}, "call_coordination"),
        request,
    )

    assert ArtifactType.plotly_json in artifact_types(artifacts)
    assert ArtifactType.plotly_html in artifact_types(artifacts)
    assert ArtifactType.recipe_json in artifact_types(artifacts)


def test_density_scatter_generates_plotly_artifacts(tmp_path):
    dataframe = pd.DataFrame({"formula": ["Si", "Fe2O3", "LiFePO4"], "y_true": [1.0, 2.0, 3.0], "y_pred": [1.1, 1.8, 3.2]})
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_density",
        toolId="ml.density_scatter",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"nBins": False},
        artifactTypes=["plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = DensityScatterAdapter().execute(
        make_context(tmp_path, "ml.density_scatter", {"ml_table": dataframe}, "call_density"),
        request,
    )

    assert ArtifactType.plotly_json in artifact_types(artifacts)
    assert ArtifactType.plotly_html in artifact_types(artifacts)
    assert ArtifactType.recipe_json in artifact_types(artifacts)


def test_error_distribution_generates_plotly_metrics_and_table_artifacts(tmp_path):
    dataframe = pd.DataFrame({"y_true": [1.0, 2.0, 3.0], "y_pred": [1.1, 1.8, 3.2]})
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_errors",
        toolId="ml.error_distribution",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"nBins": 5, "topK": 2},
        artifactTypes=["plotly_json", "plotly_html", "metrics_json", "table_json", "summary_md", "recipe_json"],
    )

    artifacts = ErrorDistributionAdapter().execute(
        make_context(tmp_path, "ml.error_distribution", {"ml_table": dataframe}, "call_errors"),
        request,
    )

    assert artifact_types(artifacts) == {
        ArtifactType.plotly_json,
        ArtifactType.plotly_html,
        ArtifactType.metrics_json,
        ArtifactType.table_json,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }


def test_basic_metrics_generates_metrics_artifact(tmp_path):
    dataframe = pd.DataFrame({"target": [1.0, 2.0, 3.0], "prediction": [1.1, 1.8, 3.2]})
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_metrics",
        toolId="ml.basic_metrics",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={},
        artifactTypes=["metrics_json", "summary_md", "recipe_json"],
    )

    artifacts = BasicMetricsAdapter().execute(
        make_context(tmp_path, "ml.basic_metrics", {"ml_table": dataframe}, "call_metrics"),
        request,
    )

    assert artifact_types(artifacts) == {ArtifactType.metrics_json, ArtifactType.summary_md, ArtifactType.recipe_json}


def test_numeric_summary_generates_table_summary_artifact(tmp_path):
    dataframe = pd.DataFrame(
        {
            "composition": ["Ag20Al25La55", "Cu50Zr50", "Zr60Cu30Al10"],
            "gfa_type": ["Ribbon", "Bulk", "Bulk"],
            "D_max": [0.2, 5.0, 8.0],
            "dTx": [None, 55.5, 75.0],
        }
    )
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_summary",
        toolId="table.numeric_summary",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"numericColumns": ["D_max", "dTx"], "categoricalColumns": ["gfa_type"], "maxCategories": 5},
        artifactTypes=["table_json", "summary_md", "recipe_json"],
    )

    artifacts = NumericSummaryAdapter().execute(
        make_context(tmp_path, "table.numeric_summary", {"ml_table": dataframe}, "call_summary"),
        request,
    )

    assert artifact_types(artifacts) == {ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json}
    table_artifact = next(artifact for artifact in artifacts if artifact.type == ArtifactType.table_json)
    payload = (tmp_path / "artifacts" / table_artifact.storageKey).read_text(encoding="utf-8")
    assert '"D_max"' in payload
    assert '"dTx"' in payload
    assert '"gfa_type"' in payload


def test_distribution_summary_generates_distribution_artifacts(tmp_path):
    dataframe = pd.DataFrame(
        {
            "composition": ["Ag20Al25La55", "Cu50Zr50", "Zr60Cu30Al10"],
            "gfa_type": ["Ribbon", "Bulk", "Bulk"],
            "D_max": [0.2, 5.0, 8.0],
            "dTx": [None, 55.5, 75.0],
        }
    )
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_distribution",
        toolId="table.distribution_summary",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"numericColumns": ["D_max", "dTx"], "categoricalColumns": ["gfa_type"], "maxCategories": 5},
        artifactTypes=["table_json", "summary_md", "recipe_json"],
    )

    artifacts = DistributionSummaryAdapter().execute(
        make_context(tmp_path, "table.distribution_summary", {"ml_table": dataframe}, "call_distribution"),
        request,
    )

    assert artifact_types(artifacts) == {ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json}
    table_artifact = next(artifact for artifact in artifacts if artifact.type == ArtifactType.table_json)
    payload = (tmp_path / "artifacts" / table_artifact.storageKey).read_text(encoding="utf-8")
    assert '"recommendedVisualizations"' in payload
    assert '"p25"' in payload
    assert '"topValues"' in payload


def test_scatter_generates_named_plotly_artifacts(tmp_path):
    dataframe = pd.DataFrame({"element": ["Li", "Na", "K"], "PBE": [1.0, 2.0, 3.0], "r2SCAN": [1.1, 1.9, 3.2]})
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_scatter",
        toolId="viz.scatter",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"xColumn": "PBE", "yColumn": "r2SCAN"},
        artifactTypes=["plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = ScatterAdapter().execute(
        make_context(tmp_path, "viz.scatter", {"ml_table": dataframe}, "call_scatter"),
        request,
    )

    assert artifact_types(artifacts) == {
        ArtifactType.plotly_json,
        ArtifactType.plotly_html,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
    plot = next(artifact for artifact in artifacts if artifact.type == ArtifactType.plotly_json)
    assert plot.name == "scatter.json"
    payload = json.loads((tmp_path / "artifacts" / plot.storageKey).read_text(encoding="utf-8"))
    assert payload["chartType"] == "scatter"
    assert payload["xColumn"] == "PBE"
    assert payload["yColumn"] == "r2SCAN"
    assert payload["pointCount"] == 3
    assert payload["figure"]["data"][0]["type"] == "scatter"


def test_histogram_generates_named_plotly_artifacts(tmp_path):
    dataframe = pd.DataFrame({"PBE": [1.0, 2.0, 3.0, 4.0]})
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_histogram",
        toolId="viz.histogram",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"column": "PBE", "bins": 3},
        artifactTypes=["plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = HistogramAdapter().execute(
        make_context(tmp_path, "viz.histogram", {"ml_table": dataframe}, "call_histogram"),
        request,
    )

    plot = next(artifact for artifact in artifacts if artifact.type == ArtifactType.plotly_json)
    assert plot.name == "histogram.json"
    payload = json.loads((tmp_path / "artifacts" / plot.storageKey).read_text(encoding="utf-8"))
    assert payload["chartType"] == "histogram"
    assert payload["column"] == "PBE"
    assert payload["count"] == 4
    assert payload["bins"] == 3
    assert len(payload["binCounts"]) == 3
    assert payload["figure"]["data"][0]["type"] == "histogram"
    assert ArtifactType.summary_md in artifact_types(artifacts)


def test_correlation_generates_matrix_and_heatmap_artifacts(tmp_path):
    dataframe = pd.DataFrame({"D_max": [0.2, 5.0, 8.0], "dTx": [40.0, 55.5, 75.0], "Tg": [350, 420, 510]})
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_correlation",
        toolId="viz.correlation",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"numericColumns": ["D_max", "dTx", "Tg"], "method": "pearson"},
        artifactTypes=["table_json", "plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = CorrelationAdapter().execute(
        make_context(tmp_path, "viz.correlation", {"ml_table": dataframe}, "call_correlation"),
        request,
    )

    assert artifact_types(artifacts) == {
        ArtifactType.table_json,
        ArtifactType.plotly_json,
        ArtifactType.plotly_html,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
    table = next(artifact for artifact in artifacts if artifact.type == ArtifactType.table_json)
    assert table.name == "correlation_matrix.json"
    plot = next(artifact for artifact in artifacts if artifact.type == ArtifactType.plotly_json)
    assert plot.name == "correlation_heatmap.json"


def test_composition_summary_generates_composition_artifacts(tmp_path):
    dataframe = pd.DataFrame({"composition": ["Ag20Al25La55", "Cu50Zr50", "Zr60Cu30Al10"]})
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_composition",
        toolId="composition.summary",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"compositionColumn": "composition"},
        artifactTypes=["table_json", "summary_md", "recipe_json"],
    )

    artifacts = CompositionSummaryAdapter().execute(
        make_context(tmp_path, "composition.summary", {"ml_table": dataframe}, "call_composition_summary"),
        request,
    )

    assert artifact_types(artifacts) == {ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json}
    table = next(artifact for artifact in artifacts if artifact.type == ArtifactType.table_json)
    payload = (tmp_path / "artifacts" / table.storageKey).read_text(encoding="utf-8")
    assert '"elementCounts"' in payload
    assert '"Ag"' in payload


def test_outlier_table_generates_table_artifacts(tmp_path):
    dataframe = pd.DataFrame({"target": [1.0, 2.0, 3.0], "prediction": [1.1, 1.8, 3.2]})
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_outliers",
        toolId="ml.outlier_table",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"topK": 2},
        artifactTypes=["table_json", "table_csv", "summary_md", "recipe_json"],
    )

    artifacts = OutlierTableAdapter().execute(
        make_context(tmp_path, "ml.outlier_table", {"ml_table": dataframe}, "call_outliers"),
        request,
    )

    assert artifact_types(artifacts) == {
        ArtifactType.table_json,
        ArtifactType.table_csv,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
