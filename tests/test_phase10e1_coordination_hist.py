from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import CoordinationHistAdapter
from mdi_adapters.context import ToolExecutionContext
from mdi_adapters.errors import ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import AnalysisPlan, ArtifactType, DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


def test_coordination_hist_generates_numeric_json_plot_summary_and_recipe() -> None:
    artifacts = _execute_adapter(
        object_store={"structures": [_chain_structure()]},
        params={"neighbor_policy": "distance_cutoff", "cutoff_angstrom": 2.1},
    )

    payload = _artifact_payload(artifacts, "coordination_hist.json")
    plot = _artifact_payload(artifacts, "coordination_hist_plot.json")
    summary = _artifact_text(artifacts, "summary.md")
    recipe = _artifact_payload(artifacts, "recipe.json")

    assert {artifact.name for artifact in artifacts["artifacts"]} == {
        "coordination_hist.json",
        "coordination_hist_plot.json",
        "summary.md",
        "recipe.json",
    }
    assert payload["artifactType"] == "structure.coordination_hist"
    assert payload["schema_version"] == "phase10e1.coordination_hist.v1"
    assert payload["tool_id"] == "structure.coordination_hist"
    assert payload["parameters"]["neighbor_policy"] == "distance_cutoff"
    assert payload["parameters"]["cutoff_angstrom"] == 2.1
    assert payload["histogram"]["total_sites"] == 3
    assert payload["histogram"]["bins"] == [
        {"coordination_number": 1, "count": 2, "fraction": 0.666667},
        {"coordination_number": 2, "count": 1, "fraction": 0.333333},
    ]
    assert payload["by_element"][0]["element"] == "Si"
    assert payload["pair_counts"] == [{"center_element": "Si", "neighbor_element": "Si", "count": 4}]
    assert payload["site_details"][1]["coordination_number"] == 2
    assert payload["limits"]["truncated"] is False
    assert payload["security"] == {
        "contains_javascript": False,
        "external_urls": [],
        "external_urls_allowed": False,
    }
    assert plot["schema_version"] == "phase10e1.static_chart.v1"
    assert plot["chart_type"] == "bar"
    assert plot["series"][0] == {"name": "All sites", "x": [1, 2], "y": [2, 1]}
    assert "no full 3D viewer" in summary
    assert recipe["schema_version"] == "phase10e1.recipe.v1"
    assert recipe["deterministic"] is True
    assert recipe["dependencies"]["new_dependencies_added"] is False


def test_coordination_hist_is_deterministic() -> None:
    first = _artifact_payload(
        _execute_adapter(object_store={"structures": [_chain_structure()]}, params={"cutoff_angstrom": 2.1}),
        "coordination_hist.json",
    )
    second = _artifact_payload(
        _execute_adapter(object_store={"structures": [_chain_structure()]}, params={"cutoff_angstrom": 2.1}),
        "coordination_hist.json",
    )

    assert first == second


def test_coordination_hist_cutoff_affects_counts() -> None:
    small = _artifact_payload(
        _execute_adapter(object_store={"structures": [_chain_structure()]}, params={"cutoff_angstrom": 1.0}),
        "coordination_hist.json",
    )
    larger = _artifact_payload(
        _execute_adapter(object_store={"structures": [_chain_structure()]}, params={"cutoff_angstrom": 2.1}),
        "coordination_hist.json",
    )

    assert small["histogram"]["bins"] == [{"coordination_number": 0, "count": 3, "fraction": 1.0}]
    assert larger["histogram"]["bins"] != small["histogram"]["bins"]


def test_coordination_hist_supports_cif_poscar_and_structure_dict(repo_root: Path) -> None:
    fixture_dir = repo_root / "tests" / "fixtures" / "structures"
    cif_text = (fixture_dir / "simple_cubic.cif").read_text(encoding="utf-8")
    poscar_text = (fixture_dir / "nacl.poscar").read_text(encoding="utf-8")
    structure_dict = _chain_structure().as_dict()

    for raw in (cif_text, poscar_text, structure_dict):
        payload = _artifact_payload(
            _execute_adapter(object_store={"structures": raw}, params={"cutoff_angstrom": 3.0}),
            "coordination_hist.json",
        )
        assert payload["histogram"]["total_sites"] >= 1
        assert payload["structure"]["site_count"] >= 1


def test_coordination_hist_rejects_invalid_params_and_malformed_input() -> None:
    with pytest.raises(ToolExecutionError) as cutoff_error:
        _execute_adapter(object_store={"structures": [_chain_structure()]}, params={"cutoff_angstrom": 0.0})

    assert cutoff_error.value.details["errorType"] == "COORDINATION_HIST_INVALID_PARAMS"

    with pytest.raises(ToolExecutionError) as parse_error:
        _execute_adapter(object_store={"structures": "not a structure"}, params={"cutoff_angstrom": 3.0})

    assert parse_error.value.details["errorType"] == "unsupported_structure_format"


def test_coordination_hist_limits_and_warnings() -> None:
    payload = _artifact_payload(
        _execute_adapter(
            object_store={"structures": [_chain_structure()]},
            params={"cutoff_angstrom": 3.0, "max_sites": 2, "max_neighbors_per_site": 1},
        ),
        "coordination_hist.json",
    )

    assert payload["limits"]["truncated"] is True
    assert payload["histogram"]["total_sites"] == 2
    assert any("COORDINATION_SITES_TRUNCATED" in warning for warning in payload["warnings"])
    assert any("COORDINATION_NEIGHBORS_TRUNCATED" in warning for warning in payload["warnings"])


def test_coordination_hist_artifacts_do_not_contain_js_or_external_urls() -> None:
    artifacts = _execute_adapter(object_store={"structures": [_chain_structure()]}, params={"cutoff_angstrom": 2.1})
    combined = "\n".join(
        (artifacts["root"] / artifact.storageKey).read_text(encoding="utf-8")
        for artifact in artifacts["artifacts"]
    ).lower()

    assert "<script" not in combined
    assert "javascript:" not in combined
    assert "http://" not in combined
    assert "https://" not in combined


def test_coordination_hist_registered_with_strict_schema_and_static_artifacts() -> None:
    tool = load_manifests().get_tool_by_id("structure.coordination_hist")

    assert tool.domain == "structure"
    assert tool.paramsSchema["additionalProperties"] is False
    assert set(tool.paramsSchema["properties"]) >= {
        "neighbor_policy",
        "cutoff_angstrom",
        "max_sites",
        "max_neighbors_per_site",
        "include_site_details",
        "group_by_element",
        "include_pair_counts",
        "plot_kind",
    }
    assert tool.artifactTypes == [
        ArtifactType.table_json,
        ArtifactType.plotly_json,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    ]
    description = tool.description.lower()
    assert "xrd" not in description
    assert "rdf" not in description
    assert "phonon" not in description
    assert "3d viewer" not in description
    assert "advanced local-environment classifier" in description


@pytest.mark.parametrize(
    "prompt",
    [
        "生成这个结构的 coordination histogram",
        "计算配位数直方图",
        "统计每个原子的配位数",
        "Create a coordination number histogram for this structure",
        "Count neighbors and plot coordination histogram",
        "Show coordination distribution using a fixed cutoff",
    ],
)
def test_mock_planner_routes_coordination_prompts(prompt: str) -> None:
    plan = _mock_plan(prompt)

    assert plan["steps"][0]["toolId"] == "structure.coordination_hist"
    assert plan["steps"][0]["params"]["neighbor_policy"] == "distance_cutoff"
    assert plan["expectedArtifacts"][0]["name"] == "coordination_hist.json"
    assert any(item["name"] == "coordination_hist_plot.json" for item in plan["expectedArtifacts"])


@pytest.mark.parametrize(
    "prompt",
    [
        "计算 XRD 图谱",
        "Generate XRD pattern",
        "计算 RDF",
        "Generate radial distribution function",
        "打开交互式 3D viewer",
        "用 WebGL 显示这个晶体",
        "生成 Brillouin zone 3D",
        "画 phonon bands",
        "画 phonon DOS",
        "做 Voronoi local environment analysis",
        "做 CrystalNN chemical environment classification",
    ],
)
def test_mock_planner_does_not_route_deferred_physics_to_coordination(prompt: str) -> None:
    plan = _mock_plan(prompt)

    assert plan["steps"][0]["toolId"] != "structure.coordination_hist"
    assert plan["steps"][0]["toolId"] not in {
        "structure.xrd",
        "structure.rdf",
        "structure.viewer_3d",
        "structure.brillouin_zone_3d",
        "phonon.bands",
        "phonon.dos",
    }


def test_persisted_coordination_plan_executes_exactly_one_tool_call(tmp_path: Path) -> None:
    repos = InMemoryRepositoryBundle.create()
    plan = _valid_coordination_plan()
    provider = MockLLMProvider(fixed_plan=plan.model_dump(mode="json"))
    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Create a coordination number histogram for this structure.",
            projectId="project_10e1",
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
    worker_result = runtime.handle_job(result.job_id or "", object_store={"structures": [_chain_structure()]})

    tool_calls = repos.tool_calls.list_for_job(result.job_id or "")
    artifacts = repos.artifacts.list_for_job(result.job_id or "")
    assert worker_result.status == "completed"
    assert worker_result.tool_call_count == 1
    assert tool_calls[0]["toolId"] == "structure.coordination_hist"
    assert {artifact["name"] for artifact in artifacts} >= {
        "coordination_hist.json",
        "coordination_hist_plot.json",
        "summary.md",
        "recipe.json",
    }


def _execute_adapter(
    *,
    object_store: dict[str, Any],
    params: dict[str, Any] | None = None,
    artifact_types: list[ArtifactType] | None = None,
) -> dict[str, Any]:
    artifact_root = Path(tempfile.mkdtemp(prefix="mdi_phase10e1_artifacts_"))
    context = ToolExecutionContext(
        job_id="job_10e1",
        project_id="project_10e1",
        dataset_id="dataset_structure",
        tool_id="structure.coordination_hist",
        tool_version="0.1.0",
        adapter_version="0.1.0",
        registry_version=load_manifests().version,
        artifact_root=artifact_root,
        object_store=object_store,
        resource_limits={"maxAtomsPerStructure": 1000, "maxStructures": 100, "maxSites": 5000, "maxNeighborsPerSite": 1000},
    )
    request = {
        "jobId": "job_10e1",
        "stepId": "step_001",
        "toolId": "structure.coordination_hist",
        "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
        "params": params or {},
        "artifactTypes": [artifact_type.value for artifact_type in (artifact_types or [
            ArtifactType.table_json,
            ArtifactType.plotly_json,
            ArtifactType.summary_md,
            ArtifactType.recipe_json,
        ])],
    }
    return {"root": artifact_root, "artifacts": CoordinationHistAdapter().execute(context, request)}


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


def _valid_coordination_plan() -> AnalysisPlan:
    return AnalysisPlan.model_validate(
        {
            "schemaVersion": "0.1",
            "goal": "coordination histogram",
            "datasetId": "dataset_structure",
            "profileId": "profile_structure",
            "toolRegistryVersion": load_manifests().version,
            "assumptions": [],
            "warnings": [],
            "steps": [
                {
                    "stepId": "step_001",
                    "toolId": "structure.coordination_hist",
                    "purpose": "coordination histogram",
                    "reason": "test",
                    "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
                    "params": {
                        "neighbor_policy": "distance_cutoff",
                        "cutoff_angstrom": 2.1,
                        "max_sites": 500,
                        "max_neighbors_per_site": 128,
                        "include_site_details": True,
                        "group_by_element": True,
                        "include_pair_counts": True,
                        "plot_kind": "bar",
                    },
                    "output": {"artifactTypes": ["table_json", "plotly_json", "summary_md", "recipe_json"]},
                }
            ],
            "expectedArtifacts": [
                {"name": "coordination_hist.json", "type": "table_json", "fromStepId": "step_001"},
                {"name": "coordination_hist_plot.json", "type": "plotly_json", "fromStepId": "step_001"},
                {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
                {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
            ],
        }
    )


def _chain_structure() -> Structure:
    return Structure(
        Lattice.cubic(10.0),
        ["Si", "Si", "Si"],
        [[0.1, 0.1, 0.1], [0.3, 0.1, 0.1], [0.5, 0.1, 0.1]],
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
