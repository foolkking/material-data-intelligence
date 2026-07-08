from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import XrdPatternAdapter
from mdi_adapters.context import ToolExecutionContext
from mdi_adapters.errors import ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import AnalysisPlan, ArtifactType, DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


def test_xrd_generates_numeric_json_plot_summary_and_recipe() -> None:
    artifacts = _execute_adapter(object_store={"structures": [_si_structure()]}, params={})

    payload = _artifact_payload(artifacts, "xrd_pattern.json")
    plot = _artifact_payload(artifacts, "xrd_plot.json")
    summary = _artifact_text(artifacts, "summary.md")
    recipe = _artifact_payload(artifacts, "recipe.json")

    assert {artifact.name for artifact in artifacts["artifacts"]} == {
        "xrd_pattern.json",
        "xrd_plot.json",
        "summary.md",
        "recipe.json",
    }
    assert payload["artifactType"] == "structure.xrd"
    assert payload["schema_version"] == "phase10e4.xrd_pattern.v1"
    assert payload["tool_id"] == "structure.xrd"
    assert payload["parameters"]["radiation"] == "CuKa"
    assert payload["parameters"]["two_theta_min"] == 0.0
    assert payload["parameters"]["two_theta_max"] == 90.0
    assert payload["pattern"]["peak_count"] >= 1
    assert payload["pattern"]["intensity_scale"] == "relative_100"
    assert payload["pattern"]["peaks"] == sorted(payload["pattern"]["peaks"], key=lambda item: item["two_theta_deg"])
    assert payload["security"] == {
        "contains_javascript": False,
        "external_urls": [],
        "external_urls_allowed": False,
    }
    assert plot["schema_version"] == "phase10e4.static_chart.v1"
    assert plot["chart_type"] == "stem"
    assert plot["tool_id"] == "structure.xrd"
    assert plot["series"][0]["x"] == plot["x_axis"]["values"]
    assert plot["series"][0]["y"] == plot["y_axis"]["values"]
    assert "no full 3D viewer" in summary
    assert "XRD_NO_RIETVELD_REFINEMENT" in summary
    assert recipe["schema_version"] == "phase10e4.recipe.v1"
    assert recipe["deterministic"] is True
    assert recipe["dependencies"]["new_dependencies_added"] is False


def test_xrd_is_deterministic() -> None:
    first = _artifact_payload(_execute_adapter(object_store={"structures": [_si_structure()]}, params={}), "xrd_pattern.json")
    second = _artifact_payload(_execute_adapter(object_store={"structures": [_si_structure()]}, params={}), "xrd_pattern.json")

    assert first == second


def test_xrd_filtering_threshold_max_peaks_and_hkl_toggle() -> None:
    payload = _artifact_payload(
        _execute_adapter(
            object_store={"structures": [_si_structure()]},
            params={"intensity_threshold": 1.0, "max_peaks": 2, "include_hkl": False},
        ),
        "xrd_pattern.json",
    )

    assert payload["pattern"]["peak_count"] <= 2
    assert payload["limits"]["max_peaks"] == 2
    assert all("hkls" not in peak for peak in payload["pattern"]["peaks"])
    assert all(float(peak["intensity"]) >= 1.0 for peak in payload["pattern"]["peaks"])


def test_xrd_supports_cif_poscar_and_structure_dict(repo_root: Path) -> None:
    fixture_dir = repo_root / "tests" / "fixtures" / "structures"
    cif_text = (fixture_dir / "simple_cubic.cif").read_text(encoding="utf-8")
    poscar_text = (fixture_dir / "nacl.poscar").read_text(encoding="utf-8")
    structure_dict = _si_structure().as_dict()

    for raw in (cif_text, poscar_text, structure_dict):
        payload = _artifact_payload(_execute_adapter(object_store={"structures": raw}, params={}), "xrd_pattern.json")
        assert payload["pattern"]["peak_count"] >= 1
        assert payload["structure"]["site_count"] >= 1


def test_xrd_rejects_invalid_params_and_malformed_input() -> None:
    with pytest.raises(ToolExecutionError) as range_error:
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"two_theta_min": 90.0, "two_theta_max": 10.0})

    assert range_error.value.details["errorType"] == "XRD_INVALID_PARAMS"

    with pytest.raises(ToolExecutionError) as radiation_error:
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"radiation": "MoKa"})

    assert radiation_error.value.details["errorType"] == "XRD_INVALID_PARAMS"

    with pytest.raises(ToolExecutionError) as parse_error:
        _execute_adapter(object_store={"structures": "not a structure"}, params={})

    assert parse_error.value.details["errorType"] == "unsupported_structure_format"


def test_xrd_artifacts_do_not_contain_js_or_external_urls() -> None:
    artifacts = _execute_adapter(object_store={"structures": [_si_structure()]}, params={})
    combined = "\n".join(
        (artifacts["root"] / artifact.storageKey).read_text(encoding="utf-8")
        for artifact in artifacts["artifacts"]
    ).lower()

    assert "<script" not in combined
    assert "javascript:" not in combined
    assert "http://" not in combined
    assert "https://" not in combined
    assert "three.js" not in combined
    assert "<canvas" not in combined


def test_xrd_registered_with_strict_schema_and_static_artifacts() -> None:
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.xrd")

    assert tool in registry.list_mvp_tools()
    assert tool.domain == "structure"
    assert tool.paramsSchema["additionalProperties"] is False
    assert set(tool.paramsSchema["properties"]) >= {
        "radiation",
        "two_theta_min",
        "two_theta_max",
        "intensity_threshold",
        "peak_merge_tolerance",
        "max_peaks",
        "include_hkl",
        "plot_kind",
    }
    assert tool.artifactTypes == [
        ArtifactType.table_json,
        ArtifactType.plotly_json,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    ]
    description = tool.description.lower()
    assert "rdf" not in description
    assert "phonon" not in description
    assert "3d viewer" not in description
    assert "experimental fitting" in description
    assert "rietveld refinement" in description



@pytest.mark.parametrize(
    "prompt",
    [
        "Generate an XRD pattern for this crystal structure",
        "Calculate an XRD pattern",
        "Simulate powder XRD",
        "Create an XRD pattern for this structure",
        "Generate a powder XRD pattern",
        "Show diffraction peaks for this crystal",
        "Plot X-ray diffraction peaks",
    ],
)
def test_mock_planner_routes_xrd_prompts(prompt: str) -> None:
    plan = _mock_plan(prompt)

    assert plan["steps"][0]["toolId"] == "structure.xrd"
    assert plan["steps"][0]["params"]["radiation"] == "CuKa"
    assert plan["expectedArtifacts"][0]["name"] == "xrd_pattern.json"
    assert any(item["name"] == "xrd_plot.json" for item in plan["expectedArtifacts"])


@pytest.mark.parametrize(
    "prompt",
    [
        "Generate radial distribution function",
        "Create a coordination histogram for this structure",
        "Count neighbors and plot coordination histogram",
        "Open an interactive 3D viewer",
        "Use WebGL to display this crystal",
        "Generate Brillouin zone 3D",
        "Plot phonon bands",
        "Plot phonon DOS",
        "do Rietveld refinement",
        "fit experimental XRD data",
        "do peak broadening and profile fitting",
    ],
)
def test_mock_planner_does_not_route_deferred_or_existing_tools_to_xrd(prompt: str) -> None:
    plan = _mock_plan(prompt)

    assert plan["steps"][0]["toolId"] != "structure.xrd"
    if "coordination" in prompt.lower():
        assert plan["steps"][0]["toolId"] == "structure.coordination_hist"


def test_persisted_xrd_plan_executes_exactly_one_tool_call(tmp_path: Path) -> None:
    repos = InMemoryRepositoryBundle.create()
    plan = _valid_xrd_plan()
    provider = MockLLMProvider(fixed_plan=plan.model_dump(mode="json"))
    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Create an XRD pattern for this structure.",
            projectId="project_10e4",
            datasetId="dataset_structure",
            profileId="profile_structure",
            enqueue=True,
        ),
        provider=provider,
        repositories=repos,
        queue_runtime=QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path / "artifacts"),
        registry=load_manifests(),
    )

    assert result.ok
    runtime = QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path / "artifacts")
    worker_result = runtime.handle_job(result.job_id or "", object_store={"structures": [_si_structure()]})

    tool_calls = repos.tool_calls.list_for_job(result.job_id or "")
    artifacts = repos.artifacts.list_for_job(result.job_id or "")
    assert worker_result.status == "completed"
    assert worker_result.tool_call_count == 1
    assert tool_calls[0]["toolId"] == "structure.xrd"
    assert {artifact["name"] for artifact in artifacts} >= {
        "xrd_pattern.json",
        "xrd_plot.json",
        "summary.md",
        "recipe.json",
    }


def _execute_adapter(
    *,
    object_store: dict[str, Any],
    params: dict[str, Any] | None = None,
    artifact_types: list[ArtifactType] | None = None,
) -> dict[str, Any]:
    artifact_root = Path(tempfile.mkdtemp(prefix="mdi_phase10e4_artifacts_"))
    context = ToolExecutionContext(
        job_id="job_10e4",
        project_id="project_10e4",
        dataset_id="dataset_structure",
        tool_id="structure.xrd",
        tool_version="0.1.0",
        adapter_version="0.1.0",
        registry_version=load_manifests().version,
        artifact_root=artifact_root,
        object_store=object_store,
        resource_limits={"maxAtomsPerStructure": 1000, "maxStructures": 100, "maxPeaks": 5000},
    )
    request = {
        "jobId": "job_10e4",
        "stepId": "step_001",
        "toolId": "structure.xrd",
        "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
        "params": params or {},
        "artifactTypes": [artifact_type.value for artifact_type in (artifact_types or [
            ArtifactType.table_json,
            ArtifactType.plotly_json,
            ArtifactType.summary_md,
            ArtifactType.recipe_json,
        ])],
    }
    return {"root": artifact_root, "artifacts": XrdPatternAdapter().execute(context, request)}


def _artifact_payload(result: dict[str, Any], name: str) -> dict[str, Any]:
    artifact = next(item for item in result["artifacts"] if item.name == name)
    return json.loads((result["root"] / artifact.storageKey).read_text(encoding="utf-8"))


def _artifact_text(result: dict[str, Any], name: str) -> str:
    artifact = next(item for item in result["artifacts"] if item.name == name)
    return (result["root"] / artifact.storageKey).read_text(encoding="utf-8")


def _mock_plan(prompt: str) -> dict[str, Any]:
    response = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt=prompt,
            dataset_id="dataset_structure",
            profile_id="profile_structure",
            tool_registry_version=load_manifests().version,
        ),
        tools=load_manifests().list_mvp_tools(),
        data_profile=_structure_profile(),
    )
    assert response.raw_json is not None
    return response.raw_json


def _valid_xrd_plan() -> AnalysisPlan:
    return AnalysisPlan.model_validate(
        {
            "schemaVersion": "0.1",
            "goal": "xrd pattern",
            "datasetId": "dataset_structure",
            "profileId": "profile_structure",
            "toolRegistryVersion": load_manifests().version,
            "assumptions": [],
            "warnings": [],
            "steps": [
                {
                    "stepId": "step_001",
                    "toolId": "structure.xrd",
                    "purpose": "xrd pattern",
                    "reason": "test",
                    "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
                    "params": {
                        "radiation": "CuKa",
                        "two_theta_min": 0.0,
                        "two_theta_max": 90.0,
                        "intensity_threshold": 0.0,
                        "peak_merge_tolerance": 0.05,
                        "max_peaks": 500,
                        "include_hkl": True,
                        "plot_kind": "stem",
                    },
                    "output": {"artifactTypes": ["table_json", "plotly_json", "summary_md", "recipe_json"]},
                }
            ],
            "expectedArtifacts": [
                {"name": "xrd_pattern.json", "type": "table_json", "fromStepId": "step_001"},
                {"name": "xrd_plot.json", "type": "plotly_json", "fromStepId": "step_001"},
                {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
                {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
            ],
        }
    )


def _si_structure() -> Structure:
    return Structure(
        Lattice.cubic(5.43),
        ["Si", "Si"],
        [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]],
    )


def _structure_profile() -> DataProfile:
    return DataProfile.model_validate(
        {
            "schemaVersion": "0.1",
            "profileId": "profile_structure",
            "datasetId": "dataset_structure",
            "version": "1",
            "datasetType": "structure_collection",
            "files": [{"path": "simple_cubic.cif", "format": "cif", "sizeBytes": 512}],
            "objects": [{"objectType": "Structure", "count": 1, "source": "simple_cubic.cif"}],
            "structureSummary": {
                "nStructures": 1,
                "elements": ["Si"],
                "formulaStats": {"total": 1, "uniqueCount": 1},
            },
            "qualityIssues": [],
            "recommendedTasks": [],
            "createdAt": "2026-07-08T00:00:00+00:00",
        }
    )
