from __future__ import annotations

import base64
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from pymatgen.core import Structure
from mdi_artifact_core import validate_viewer_scene, validate_viewer_scene_manifest

from mdi_adapters import (
    BasicMetricsAdapter,
    ChemSysSunburstAdapter,
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
    FormulaStatisticsAdapter,
    Structure3DAdapter,
    StructureViewer3DAdapter,
    ToolExecutionContext,
)
from mdi_adapters.errors import ToolExecutionError
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


def read_artifact_json(tmp_path, artifacts, artifact_type: ArtifactType):
    artifact = next(item for item in artifacts if item.type == artifact_type)
    return json.loads((tmp_path / "artifacts" / artifact.storageKey).read_text(encoding="utf-8"))


def composition_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "composition": ["Fe2O3", "LiFePO4", "Si", "not_a_formula"],
            "group": ["oxide", "phosphate", "element", "bad"],
        }
    )


def test_ptable_heatmap_generates_plotly_artifacts(tmp_path):
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_ptable",
        toolId="composition.ptable_heatmap",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"formulaColumn": "composition", "countMode": "occurrence", "colorScale": "viridis", "title": "Composition overview"},
        artifactTypes=["plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = PTableHeatmapAdapter().execute(
        make_context(tmp_path, "composition.ptable_heatmap", {"ml_table": composition_frame()}, "call_ptable"),
        request,
    )

    assert artifact_types(artifacts) == {
        ArtifactType.plotly_json,
        ArtifactType.plotly_html,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
    assert all((tmp_path / "artifacts" / artifact.storageKey).exists() for artifact in artifacts)
    payload = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)
    assert payload["artifactType"] == "composition.ptable_heatmap"
    assert payload["chartType"] == "periodic_table_heatmap"
    assert payload["formulaColumn"] == "composition"
    assert {"Fe", "O"}.issubset(payload["elementValues"])
    assert {artifact.name for artifact in artifacts} >= {"ptable_heatmap.json", "ptable_heatmap.html", "summary.md", "recipe.json"}


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


def test_structure_viewer_3d_generates_canonical_inert_scene_artifacts(tmp_path, repo_root):
    structure = Structure.from_file(repo_root / "tests" / "fixtures" / "structures" / "si.cif")
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_viewer",
        toolId="structure.viewer_3d",
        inputRefs=[{"refType": "normalized_object", "ref": "si_structure", "objectType": "Structure"}],
        params={"include_bonds": True, "max_sites": 256, "max_bonds": 2048},
        artifactTypes=["structure_json", "table_json", "summary_md", "recipe_json"],
    )

    artifacts = StructureViewer3DAdapter().execute(
        make_context(tmp_path, "structure.viewer_3d", {"si_structure": structure}, "call_viewer"),
        request,
    )

    assert artifact_types(artifacts) == {
        ArtifactType.structure_json,
        ArtifactType.table_json,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
    assert {artifact.name for artifact in artifacts} == {"viewer_scene.json", "viewer_scene_manifest.json", "summary.md", "recipe.json"}
    scene = read_artifact_json(tmp_path, artifacts, ArtifactType.structure_json)
    manifest = read_artifact_json(tmp_path, artifacts, ArtifactType.table_json)
    assert validate_viewer_scene(scene).valid is True
    assert validate_viewer_scene_manifest(manifest).valid is True
    assert scene["provenance"]["tool_id"] == "structure.viewer_3d"
    assert manifest["tool_id"] == "structure.viewer_3d"
    assert all(artifact.type != ArtifactType.matterviz_html for artifact in artifacts)


def test_elements_hist_generates_plotly_artifacts(tmp_path):
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_elements",
        toolId="composition.elements_hist",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"countMode": "stoichiometric", "topN": 5},
        artifactTypes=["plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = ElementsHistAdapter().execute(
        make_context(tmp_path, "composition.elements_hist", {"ml_table": composition_frame()}, "call_elements"),
        request,
    )

    assert artifact_types(artifacts) == {
        ArtifactType.plotly_json,
        ArtifactType.plotly_html,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
    payload = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)
    assert payload["artifactType"] == "composition.elements_hist"
    assert payload["chartType"] == "bar"
    assert payload["countMode"] == "stoichiometric"
    assert payload["bars"]
    assert payload["warnings"]


def test_elements_hist_saved_categories_match_counts_and_log_scale(tmp_path):
    frame = pd.DataFrame({"composition": ["Fe2O3"] * 12 + ["Si"] * 3 + ["Cu"]})
    request = ToolExecutionRequest(
        jobId="job_adapter", stepId="step_elements", toolId="composition.elements_hist",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"formulaColumn": "composition", "countMode": "occurrence", "logY": True},
        artifactTypes=["plotly_json"],
    )
    artifacts = ElementsHistAdapter().execute(
        make_context(tmp_path, "composition.elements_hist", {"ml_table": frame}, "call_elements_log"), request,
    )
    figure = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)["plotlyFigure"]
    trace = figure["data"][0]
    assert isinstance(trace["x"], list)
    counts = trace["y"]
    if isinstance(counts, dict):
        counts = np.frombuffer(base64.b64decode(counts["bdata"]), dtype=counts["dtype"]).tolist()
    assert dict(zip(trace["x"], counts, strict=True)) == {"O": 12, "Fe": 12, "Si": 3, "Cu": 1}
    assert trace["width"] == 0.7
    assert figure["layout"]["yaxis"]["type"] == "log"


def test_chem_sys_treemap_generates_plotly_artifacts(tmp_path):
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_chem_sys",
        toolId="composition.chem_sys_treemap",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"groupMode": "chem_sys", "showCounts": "value"},
        artifactTypes=["plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = ChemSysTreemapAdapter().execute(
        make_context(tmp_path, "composition.chem_sys_treemap", {"ml_table": composition_frame()}, "call_chem_sys"),
        request,
    )

    assert ArtifactType.plotly_json in artifact_types(artifacts)
    assert ArtifactType.plotly_html in artifact_types(artifacts)
    assert ArtifactType.recipe_json in artifact_types(artifacts)
    payload = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)
    assert payload["artifactType"] == "composition.chem_sys_treemap"
    assert payload["chartType"] == "treemap"
    assert any(group["label"] == "Fe-O" for group in payload["groups"])


def test_formula_statistics_generates_table_summary_and_recipe(tmp_path):
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_formula_stats",
        toolId="composition.formula_statistics",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"maxExamples": 5},
        artifactTypes=["table_json", "summary_md", "recipe_json"],
    )

    artifacts = FormulaStatisticsAdapter().execute(
        make_context(tmp_path, "composition.formula_statistics", {"ml_table": composition_frame()}, "call_formula_stats"),
        request,
    )

    assert artifact_types(artifacts) == {ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json}
    payload = read_artifact_json(tmp_path, artifacts, ArtifactType.table_json)
    assert payload["artifactType"] == "composition.formula_statistics"
    assert payload["formulaColumn"] == "composition"
    assert payload["parsedFormulaCount"] == 3
    assert payload["failedFormulaCount"] == 1
    assert {"Fe", "O"}.issubset(payload["elements"])


def test_chem_sys_sunburst_generates_plotly_artifacts(tmp_path):
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_sunburst",
        toolId="composition.chem_sys_sunburst",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"hierarchy": ["arity", "chem_sys", "reduced_formula"], "maxLeafNodes": 10},
        artifactTypes=["plotly_json", "plotly_html", "summary_md", "recipe_json"],
    )

    artifacts = ChemSysSunburstAdapter().execute(
        make_context(tmp_path, "composition.chem_sys_sunburst", {"ml_table": composition_frame()}, "call_sunburst"),
        request,
    )

    assert artifact_types(artifacts) == {
        ArtifactType.plotly_json,
        ArtifactType.plotly_html,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
    payload = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)
    assert payload["artifactType"] == "composition.chem_sys_sunburst"
    assert payload["chartType"] == "sunburst"
    assert payload["nodes"]
    assert payload["warnings"]


@pytest.mark.parametrize("group_mode,expected", [
    ("arity", {"binary": 3, "unary": 1}),
    ("reduced_formula", {"Fe2O3": 2, "FeO": 1, "Cu": 1}),
])
def test_treemap_honors_requested_grouping_in_saved_plot(tmp_path, group_mode, expected):
    frame = pd.DataFrame({"composition": ["Fe2O3", "Fe4O6", "FeO", "Cu"]})
    request = ToolExecutionRequest(jobId="job_adapter", stepId="grouping", toolId="composition.chem_sys_treemap",
        inputRefs=[{"refType": "normalized_object", "ref": "table", "objectType": "DataFrame"}],
        params={"groupMode": group_mode}, artifactTypes=["plotly_json"])
    artifacts = ChemSysTreemapAdapter().execute(make_context(tmp_path, request.toolId, {"table": frame}, "grouping"), request)
    data = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)
    assert {row["label"]: row["count"] for row in data["groups"]} == expected
    assert _saved_hierarchy_leaves(data["plotlyFigure"]) == expected


def _saved_hierarchy_leaves(figure):
    trace = figure["data"][0]
    values = trace["values"]
    if isinstance(values, dict):
        values = np.frombuffer(base64.b64decode(values["bdata"]), dtype=values["dtype"]).tolist()
    ids = trace.get("ids", trace["labels"])
    parents = set(trace["parents"]) - {""}
    return {label: value for node, label, value in zip(ids, trace["labels"], values, strict=True) if node not in parents}


@pytest.mark.parametrize("hierarchy,roots", [
    (["chem_sys", "reduced_formula"], {"Fe-O", "Cu"}),
    (["reduced_formula", "arity"], {"Fe2O3", "FeO", "Cu"}),
    (["arity"], {"binary", "unary"}),
])
def test_sunburst_honors_exact_hierarchy_order(tmp_path, hierarchy, roots):
    frame = pd.DataFrame({"composition": ["Fe2O3", "FeO", "Cu"]})
    request = ToolExecutionRequest(jobId="job_adapter", stepId="hierarchy", toolId="composition.chem_sys_sunburst",
        inputRefs=[{"refType": "normalized_object", "ref": "table", "objectType": "DataFrame"}],
        params={"hierarchy": hierarchy}, artifactTypes=["plotly_json"])
    artifacts = ChemSysSunburstAdapter().execute(make_context(tmp_path, request.toolId, {"table": frame}, "hierarchy"), request)
    trace = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)["plotlyFigure"]["data"][0]
    assert {label for label, parent in zip(trace["labels"], trace["parents"], strict=True) if not parent} == roots
    parents = dict(zip(trace["ids"], trace["parents"], strict=True))
    depths = []
    for node in parents:
        depth = 0
        while node:
            depth += 1
            assert depth <= len(hierarchy)
            node = parents[node]
        depths.append(depth)
    assert max(depths) == len(hierarchy)


@pytest.mark.parametrize("adapter,params,cap", [
    (ChemSysTreemapAdapter, {"maxGroups": 1}, 1),
    (ChemSysSunburstAdapter, {"maxLeafNodes": 1}, 1),
])
def test_hierarchy_plot_caps_match_saved_records(tmp_path, adapter, params, cap):
    frame = pd.DataFrame({"composition": ["Fe2O3"] * 3 + ["FeO", "Cu", "Si"]})
    tool = adapter()
    request = ToolExecutionRequest(jobId="job_adapter", stepId="cap", toolId=tool.tool_id,
        inputRefs=[{"refType": "normalized_object", "ref": "table", "objectType": "DataFrame"}],
        params=params, artifactTypes=["plotly_json"])
    artifacts = tool.execute(make_context(tmp_path, request.toolId, {"table": frame}, "cap"), request)
    data = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)
    leaves = _saved_hierarchy_leaves(data["plotlyFigure"])
    assert len(leaves) == cap
    assert next(iter(leaves.values())) >= 3
    assert any("too_many" in warning for warning in data["warnings"])


def test_composition_adapters_reject_missing_formula_column(tmp_path):
    dataframe = pd.DataFrame({"value": [1, 2, 3]})
    adapters = [
        ("composition.formula_statistics", FormulaStatisticsAdapter(), ArtifactType.table_json),
        ("composition.elements_hist", ElementsHistAdapter(), ArtifactType.plotly_json),
        ("composition.ptable_heatmap", PTableHeatmapAdapter(), ArtifactType.plotly_json),
        ("composition.chem_sys_treemap", ChemSysTreemapAdapter(), ArtifactType.plotly_json),
        ("composition.chem_sys_sunburst", ChemSysSunburstAdapter(), ArtifactType.plotly_json),
    ]

    for tool_id, adapter, artifact_type in adapters:
        request = ToolExecutionRequest(
            jobId="job_adapter",
            stepId=f"step_{tool_id}",
            toolId=tool_id,
            inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
            params={},
            artifactTypes=[artifact_type],
        )
        try:
            adapter.execute(make_context(tmp_path, tool_id, {"ml_table": dataframe}, f"call_{tool_id}"), request)
        except ToolExecutionError as exc:
            assert exc.details["errorType"] == "missing_formula_column"
        else:
            raise AssertionError(f"{tool_id} accepted a table without formula/composition column")


def test_coordination_hist_generates_static_physics_artifacts(tmp_path, repo_root):
    structure = Structure.from_file(repo_root / "tests" / "fixtures" / "structures" / "si.cif")
    request = ToolExecutionRequest(
        jobId="job_adapter",
        stepId="step_coordination",
        toolId="structure.coordination_hist",
        inputRefs=[{"refType": "normalized_object", "ref": "si_structure", "objectType": "Structure"}],
        params={"neighbor_policy": "distance_cutoff", "cutoff_angstrom": 3.0},
        artifactTypes=["table_json", "plotly_json", "summary_md", "recipe_json"],
    )

    artifacts = CoordinationHistAdapter().execute(
        make_context(tmp_path, "structure.coordination_hist", {"si_structure": structure}, "call_coordination"),
        request,
    )

    assert artifact_types(artifacts) == {
        ArtifactType.table_json,
        ArtifactType.plotly_json,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
    assert {artifact.name for artifact in artifacts} == {
        "coordination_hist.json",
        "coordination_hist_plot.json",
        "summary.md",
        "recipe.json",
    }
    payload = read_artifact_json(tmp_path, artifacts, ArtifactType.table_json)
    plot_payload = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)
    assert payload["artifactType"] == "structure.coordination_hist"
    assert payload["schema_version"] == "phase10e1.coordination_hist.v1"
    assert payload["parameters"]["neighbor_policy"] == "distance_cutoff"
    assert payload["histogram"]["bins"]
    assert payload["security"]["contains_javascript"] is False
    assert payload["security"]["external_urls"] == []
    assert plot_payload["schema_version"] == "phase10e1.static_chart.v1"
    assert plot_payload["chart_type"] == "bar"


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


@pytest.mark.parametrize(("target", "prediction"), [
    ([2.0, 2.0], [1.0, 3.0]),
    ([0.1, 0.1, 0.1], [0.1, 0.1, 0.1]),
    ([2.0], [3.0]),
])
@pytest.mark.parametrize("adapter_class", [BasicMetricsAdapter, ErrorDistributionAdapter])
def test_saved_metrics_do_not_claim_perfect_r2_for_constant_targets(tmp_path, target, prediction, adapter_class):
    frame = pd.DataFrame({"target": target, "prediction": prediction})
    adapter = adapter_class()
    request = ToolExecutionRequest(
        jobId="job_adapter", stepId="constant", toolId=adapter.tool_id,
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={}, artifactTypes=["metrics_json", "summary_md", "recipe_json"],
    )
    artifacts = adapter.execute(make_context(tmp_path, adapter.tool_id, {"ml_table": frame}, "constant"), request)
    metrics = read_artifact_json(tmp_path, artifacts, ArtifactType.metrics_json)["metrics"]
    assert metrics["r2"] is None
    assert metrics["r2Status"] == "undefined_constant_target"
    assert metrics["mae"] == pytest.approx(sum(abs(a - b) for a, b in zip(target, prediction)) / len(target))


@pytest.mark.parametrize(("target", "prediction"), [
    ([2.0, 2.0], [1.0, 3.0]),
    ([0.1, 0.1, 0.1], [0.1, 0.1, 0.1]),
    ([2.0], [3.0]),
    ([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]),
])
def test_singular_density_defaults_to_saved_raw_points_without_inventing_density(tmp_path, target, prediction):
    frame = pd.DataFrame({"target": target, "prediction": prediction})
    request = ToolExecutionRequest(
        jobId="job_adapter", stepId="constant", toolId="ml.density_scatter",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={}, artifactTypes=["plotly_json", "summary_md", "recipe_json"],
    )
    artifacts = DensityScatterAdapter().execute(make_context(tmp_path, request.toolId, {"ml_table": frame}, "constant"), request)
    plot = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)
    assert plot["data"][0]["x"] == target
    assert plot["data"][0]["y"] == prediction
    assert "coloraxis" not in plot["data"][0]["marker"]
    assert "coloraxis" not in plot["layout"]
    assert plot["layout"]["meta"] == {"schemaVersion": "mdi.raw-parity-scatter/1.0"}
    notes = " ".join(item["text"] for item in plot["layout"]["annotations"])
    assert "核密度未估计" in notes
    assert "nan" not in notes.lower()
    if len(set(target)) == 1:
        assert "R² 未定义" in notes
        assert "LS fit" not in notes
        assert len(plot["layout"].get("shapes", [])) <= 1


def test_explicit_kde_request_reports_inapplicability_instead_of_switching_method(tmp_path):
    frame = pd.DataFrame({"target": [2.0, 2.0], "prediction": [1.0, 3.0]})
    request = ToolExecutionRequest(
        jobId="job_adapter", stepId="constant", toolId="ml.density_scatter",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"density": "kde"}, artifactTypes=["plotly_json"],
    )
    with pytest.raises(ToolExecutionError, match="核密度"):
        DensityScatterAdapter().execute(make_context(tmp_path, request.toolId, {"ml_table": frame}, "constant"), request)


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


@pytest.mark.parametrize(("errors", "counts", "edges"), [
    ([-2, -1, 0, 1, 2], [2, 3], [-2, 0, 2]),
    ([0, 0, 0], [0, 3], [-0.5, 0, 0.5]),
])
def test_error_distribution_saves_exact_bins_and_all_residuals(tmp_path, errors, counts, edges):
    frame = pd.DataFrame({"y_true": [0.0] * len(errors), "y_pred": errors})
    request = ToolExecutionRequest(
        jobId="job_adapter", stepId="step_errors", toolId="ml.error_distribution",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"nBins": 2}, artifactTypes=["plotly_json", "recipe_json"],
    )
    artifacts = ErrorDistributionAdapter().execute(make_context(tmp_path, request.toolId, {"ml_table": frame}, "call_bins"), request)
    plot = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)
    histogram = plot["layout"]["meta"]["histogram"]
    assert histogram["counts"] == counts
    assert histogram["edges"] == edges
    assert histogram["residuals"] == errors
    assert histogram["sampleCount"] == sum(counts) == len(errors)
    assert histogram["residualConvention"] == "prediction - target"
    trace = plot["data"][0]
    assert trace["type"] == "bar"
    assert trace["y"] == counts
    assert trace["x"] == [(a + b) / 2 for a, b in zip(edges, edges[1:])]
    assert trace["width"] == [b - a for a, b in zip(edges, edges[1:])]
    assert trace["customdata"] == [[a, b] for a, b in zip(edges, edges[1:])]
    assert "nbinsx" not in trace


@pytest.mark.parametrize("bins", [True, 0, 4097, 1.5])
def test_error_distribution_rejects_unbounded_or_invalid_bin_counts(tmp_path, bins):
    frame = pd.DataFrame({"y_true": [1.0], "y_pred": [1.5]})
    request = ToolExecutionRequest(
        jobId="job_adapter", stepId="step_errors", toolId="ml.error_distribution",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"nBins": bins}, artifactTypes=["plotly_json"],
    )
    with pytest.raises(ToolExecutionError, match="nBins"):
        ErrorDistributionAdapter().execute(make_context(tmp_path, request.toolId, {"ml_table": frame}, "call_bins"), request)


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
    assert payload["figure"]["data"][0]["type"] == "bar"
    assert payload["figure"]["data"][0]["y"] == payload["binCounts"] == [1, 1, 2]
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


@pytest.mark.parametrize("explicit", [False, True])
def test_correlation_rejects_excess_columns_without_returning_a_subset(explicit):
    frame = pd.DataFrame({f"column_{i}": [1, 2 + i, 4 + i] for i in range(31)})
    params = {"numericColumns": list(frame.columns)} if explicit else {}
    with pytest.raises(ToolExecutionError) as exc:
        CorrelationAdapter().run(frame, params)
    assert exc.value.code == ("TOOL_PARAM_INVALID" if explicit else "TOOL_INPUT_INVALID")
    assert exc.value.details["errorType"] == ("CORRELATION_PARAMS_INVALID" if explicit else "CORRELATION_COLUMN_LIMIT_EXCEEDED")
    assert "30" in exc.value.message


@pytest.mark.parametrize("columns", [["a", "a"], ["a"], [], "a", ["a", {}]])
def test_correlation_rejects_ambiguous_column_parameters(columns):
    with pytest.raises(ToolExecutionError) as exc:
        CorrelationAdapter().run(pd.DataFrame({"a": [1, 2, 3], "b": [2, 1, 4]}), {"numericColumns": columns})
    assert exc.value.code == "TOOL_PARAM_INVALID"


def test_correlation_keeps_all_explicit_columns_in_order_and_preserves_null_correlations(tmp_path):
    frame = pd.DataFrame({f"column_{i}": [1, 2 + i, 4 + i] for i in range(31)})
    frame["constant"] = [1, 1, 1]
    selected = ["column_30", *[f"column_{i}" for i in range(28)], "constant"]
    before = frame.copy(deep=True)
    request = ToolExecutionRequest(jobId="job_adapter", stepId="step_correlation", toolId="viz.correlation",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"numericColumns": selected}, artifactTypes=["table_json", "plotly_json"])
    artifacts = CorrelationAdapter().execute(make_context(tmp_path, "viz.correlation", {"ml_table": frame}, "columns"), request)
    table = read_artifact_json(tmp_path, artifacts, ArtifactType.table_json)
    plot = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)
    assert table["columns"] == plot["data"][0]["x"] == plot["data"][0]["y"] == selected
    assert len(table["matrix"]) == 30 and all(len(row) == 30 for row in table["matrix"])
    assert table["matrix"][-1] == [None] * 30
    assert all(row[-1] is None for row in table["matrix"])
    assert plot["data"][0]["z"] == table["matrix"]
    assert plot["data"][0]["zmin"] == -1 and plot["data"][0]["zmax"] == 1
    assert table["validPairCount"] == 29 * 28 // 2
    assert table["missingPairCount"] == 29
    pd.testing.assert_frame_equal(frame, before)


@pytest.mark.parametrize("params,reason", [({}, "CORRELATION_COLUMN_LIMIT_EXCEEDED"), ({"numericColumns": ["column_0", "column_0"]}, "CORRELATION_PARAMS_INVALID")])
def test_correlation_worker_failure_emits_a_reviewed_actionable_reason(tmp_path, params, reason):
    from mdi_workers.runtime import WorkerToolExecutionError, run_tool_call_job
    from mdi_api.research_agent.execution.diagnostics import execution_warnings

    frame = pd.DataFrame({f"column_{i}": [1, 2 + i, 4 + i] for i in range(31)})
    context = make_context(tmp_path, "viz.correlation", {"ml_table": frame}, "failed_correlation")
    request = ToolExecutionRequest(jobId="job_adapter", stepId="step_correlation", toolId="viz.correlation",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}], params=params, artifactTypes=["plotly_json"])
    with pytest.raises(WorkerToolExecutionError) as exc:
        run_tool_call_job(context, request)
    assert exc.value.job.status.value == "failed"
    events = [event.model_dump(mode="json") for event in exc.value.events]
    assert any(event["eventType"] == "tool.failed" for event in events)
    warnings = execution_warnings({"status": "failed"}, events)
    assert [warning.code for warning in warnings] == [reason]
    assert "30" in warnings[0].message and "重试" in warnings[0].message
    assert not list(tmp_path.rglob("*.json"))


def test_correlation_rejects_duplicate_source_headers_only_when_they_are_selected():
    frame = pd.DataFrame([[1, 2, 3, 4], [2, 3, 4, 6], [3, 4, 5, 9]], columns=["a", "a", "b", "c"])
    for params in ({}, {"numericColumns": ["a", "b"]}):
        with pytest.raises(ToolExecutionError) as exc:
            CorrelationAdapter().run(frame, params)
        assert exc.value.details["errorType"] == "CORRELATION_COLUMN_IDENTITY_INVALID"
    assert CorrelationAdapter().run(frame, {"numericColumns": ["b", "c"]}).metadata["columns"] == ["b", "c"]


@pytest.mark.parametrize("method", ["pearson", "spearman"])
@pytest.mark.parametrize("data,min_samples", [
    ({"A": [1, 1, 1], "B": [2, 2, 2]}, 2),
    ({"A": [1], "B": [2]}, 1),
    ({"A": [1, 2, None, None], "B": [None, None, 1, 2]}, 2),
    ({"A": [1, 2, 3], "B": [1, 1, 1]}, 2),
    ({"A": [1, 2, 3], "B": [3, 2, 1]}, 4),
])
def test_correlation_without_a_valid_cross_column_pair_fails_without_artifacts(tmp_path, method, data, min_samples):
    frame = pd.DataFrame(data)
    before = frame.copy(deep=True)
    request = ToolExecutionRequest(jobId="job_adapter", stepId="step_correlation", toolId="viz.correlation",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"method": method, "minNonNullCount": min_samples}, artifactTypes=["table_json", "plotly_json"])
    with pytest.raises(ToolExecutionError) as exc:
        CorrelationAdapter().execute(make_context(tmp_path, "viz.correlation", {"ml_table": frame}, "no_pairs"), request)
    assert exc.value.code == "TOOL_INPUT_INVALID"
    assert exc.value.details == {"errorType": "CORRELATION_NO_VALID_PAIRS"}
    assert not list(tmp_path.rglob("*.json"))
    pd.testing.assert_frame_equal(frame, before)


@pytest.mark.parametrize("method", ["pearson", "spearman"])
def test_correlation_retains_zero_coefficients_and_discloses_partially_missing_pairs(method):
    frame = pd.DataFrame({"A": [-1, 0, 1], "B": [1, -2, 1], "constant": [1, 1, 1]})
    result = CorrelationAdapter().run(frame, {"method": method})
    assert result.metadata["matrix"][0][1] == pytest.approx(0)
    assert result.metadata["matrix"][-1] == [None] * 3
    assert result.metadata["pairCount"] == 3
    assert result.metadata["validPairCount"] == 1
    assert result.metadata["missingPairCount"] == 2
    assert result.metadata["minNonNullCount"] == 2
    assert result.metadata["warnings"]


def test_correlation_exports_numeric_column_names_as_ordered_categories(tmp_path):
    frame = pd.DataFrame({"1": [1, 2, 3], "10": [2, 4, 5], "100": [2, 1, 4]})
    selected = ["100", "1", "10"]
    request = ToolExecutionRequest(jobId="job_adapter", stepId="step_correlation", toolId="viz.correlation",
        inputRefs=[{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        params={"numericColumns": selected}, artifactTypes=["plotly_json", "table_json", "summary_md"])
    artifacts = CorrelationAdapter().execute(make_context(tmp_path, "viz.correlation", {"ml_table": frame}, "named_columns"), request)
    plot = read_artifact_json(tmp_path, artifacts, ArtifactType.plotly_json)
    table = read_artifact_json(tmp_path, artifacts, ArtifactType.table_json)
    for axis in ["xaxis", "yaxis"]:
        assert plot["layout"][axis] == {"type": "category", "categoryorder": "array", "categoryarray": selected}
    assert plot["data"][0]["x"] == plot["data"][0]["y"] == table["columns"] == selected
    assert table["validPairCount"] == table["pairCount"] == 3
    assert table["missingPairCount"] == 0
    assert table["warnings"] == []
    summary = next(a for a in artifacts if a.type == ArtifactType.summary_md)
    assert "validPairCount: 3" in (tmp_path / "artifacts" / summary.storageKey).read_text(encoding="utf-8")


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
