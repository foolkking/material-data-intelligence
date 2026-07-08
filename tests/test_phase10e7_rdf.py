from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import RdfAdapter
from mdi_adapters.context import ToolExecutionContext
from mdi_adapters.errors import ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import AnalysisPlan, ArtifactType, DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


def test_rdf_generates_numeric_json_plot_summary_and_recipe() -> None:
    artifacts = _execute_adapter(
        object_store={"structures": [_si_structure()]},
        params={"r_max_angstrom": 4.0, "bin_width_angstrom": 0.5},
    )

    payload = _artifact_payload(artifacts, "rdf.json")
    plot = _artifact_payload(artifacts, "rdf_plot.json")
    summary = _artifact_text(artifacts, "summary.md")
    recipe = _artifact_payload(artifacts, "recipe.json")

    assert {artifact.name for artifact in artifacts["artifacts"]} == {
        "rdf.json",
        "rdf_plot.json",
        "summary.md",
        "recipe.json",
    }
    assert payload["artifactType"] == "structure.rdf"
    assert payload["schema_version"] == "phase10e7.rdf.v1"
    assert payload["tool_id"] == "structure.rdf"
    assert payload["parameters"]["normalization"] == "number_density"
    assert payload["parameters"]["r_max_angstrom"] == 4.0
    assert payload["parameters"]["bin_width_angstrom"] == 0.5
    assert payload["structure"]["site_count"] == 2
    assert payload["structure"]["pbc"] == [True, True, True]
    assert payload["rdf"]["normalization"]["method"] == "number_density"
    assert len(payload["rdf"]["r_angstrom"]) == 8
    assert len(payload["rdf"]["bin_edges_angstrom"]) == 9
    assert payload["rdf"]["counts"] == [int(item) for item in payload["rdf"]["counts"]]
    assert payload["partial_rdf"][0]["center_element"] == "Si"
    assert payload["partial_rdf"][0]["neighbor_element"] == "Si"
    assert payload["limits"]["bin_count"] == 8
    assert payload["limits"]["truncated"] is False
    assert payload["security"] == {
        "contains_javascript": False,
        "external_urls": [],
        "external_urls_allowed": False,
    }
    assert "RDF_NORMALIZATION_NUMBER_DENSITY_ONLY" in payload["warnings"]
    assert plot["schema_version"] == "phase10e7.static_chart.v1"
    assert plot["chart_type"] == "line"
    assert plot["tool_id"] == "structure.rdf"
    assert plot["series"][0]["name"] == "All pairs"
    assert plot["series"][0]["x"] == plot["x_axis"]["values"]
    assert plot["series"][0]["y"] == plot["y_axis"]["values"]
    assert "no full 3D viewer" in summary
    assert "experimental PDF fitting" not in summary
    assert recipe["schema_version"] == "phase10e7.recipe.v1"
    assert recipe["deterministic"] is True
    assert recipe["dependencies"]["new_dependencies_added"] is False


def test_rdf_is_deterministic() -> None:
    first = _artifact_payload(
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"r_max_angstrom": 4.0, "bin_width_angstrom": 0.5}),
        "rdf.json",
    )
    second = _artifact_payload(
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"r_max_angstrom": 4.0, "bin_width_angstrom": 0.5}),
        "rdf.json",
    )

    assert first == second


def test_rdf_r_max_and_bin_width_affect_output() -> None:
    coarse = _artifact_payload(
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"r_max_angstrom": 4.0, "bin_width_angstrom": 1.0}),
        "rdf.json",
    )
    fine = _artifact_payload(
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"r_max_angstrom": 4.0, "bin_width_angstrom": 0.5}),
        "rdf.json",
    )

    assert coarse["limits"]["bin_count"] == 4
    assert fine["limits"]["bin_count"] == 8
    assert coarse["rdf"]["r_angstrom"] != fine["rdf"]["r_angstrom"]


def test_rdf_partial_pairs_can_be_disabled_and_are_ordered() -> None:
    enabled = _artifact_payload(
        _execute_adapter(object_store={"structures": [_nacl_structure()]}, params={"r_max_angstrom": 4.0, "bin_width_angstrom": 0.5}),
        "rdf.json",
    )
    disabled = _artifact_payload(
        _execute_adapter(
            object_store={"structures": [_nacl_structure()]},
            params={"r_max_angstrom": 4.0, "bin_width_angstrom": 0.5, "include_partial_pairs": False},
        ),
        "rdf.json",
    )

    pairs = [(item["center_element"], item["neighbor_element"]) for item in enabled["partial_rdf"]]
    assert pairs == sorted(pairs)
    assert ("Cl", "Na") in pairs
    assert ("Na", "Cl") in pairs
    assert disabled["partial_rdf"] == []
    assert disabled["limits"]["partial_pair_count"] == 0


def test_rdf_partial_pair_cap_warns_and_truncates() -> None:
    payload = _artifact_payload(
        _execute_adapter(
            object_store={"structures": [_nacl_structure()]},
            params={"r_max_angstrom": 4.0, "bin_width_angstrom": 0.5, "max_partial_pairs": 1},
        ),
        "rdf.json",
    )

    assert payload["limits"]["partial_pair_count"] == 1
    assert payload["limits"]["partial_pair_count_before_limit"] == 4
    assert payload["limits"]["truncated"] is True
    assert any("RDF_PARTIAL_PAIRS_TRUNCATED" in warning for warning in payload["warnings"])


def test_rdf_supports_cif_poscar_and_structure_dict(repo_root: Path) -> None:
    fixture_dir = repo_root / "tests" / "fixtures" / "structures"
    cif_text = (fixture_dir / "simple_cubic.cif").read_text(encoding="utf-8")
    poscar_text = (fixture_dir / "nacl.poscar").read_text(encoding="utf-8")
    structure_dict = _si_structure().as_dict()

    for raw in (cif_text, poscar_text, structure_dict):
        payload = _artifact_payload(
            _execute_adapter(object_store={"structures": raw}, params={"r_max_angstrom": 4.0, "bin_width_angstrom": 0.5}),
            "rdf.json",
        )
        assert payload["structure"]["site_count"] >= 1
        assert payload["limits"]["bin_count"] == 8


def test_rdf_rejects_invalid_params_and_malformed_input() -> None:
    with pytest.raises(ToolExecutionError) as r_max_error:
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"r_max_angstrom": 0.1})

    assert r_max_error.value.details["errorType"] == "RDF_INVALID_PARAMS"

    with pytest.raises(ToolExecutionError) as bin_error:
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"r_max_angstrom": 4.0, "bin_width_angstrom": 0.5, "max_bins": 2})

    assert bin_error.value.details["errorType"] == "RDF_BIN_LIMIT_EXCEEDED"

    with pytest.raises(ToolExecutionError) as unknown_error:
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"sigma": 0.1})

    assert unknown_error.value.details["errorType"] == "RDF_INVALID_PARAMS"

    with pytest.raises(ToolExecutionError) as parse_error:
        _execute_adapter(object_store={"structures": "not a structure"}, params={})

    assert parse_error.value.details["errorType"] == "unsupported_structure_format"


def test_rdf_rejects_non_periodic_and_resource_limit_excesses() -> None:
    non_periodic = _si_structure()
    non_periodic._lattice.pbc = (False, False, False)
    with pytest.raises(ToolExecutionError) as pbc_error:
        _execute_adapter(object_store={"structures": [non_periodic]}, params={"r_max_angstrom": 4.0, "bin_width_angstrom": 0.5})

    assert pbc_error.value.details["errorType"] == "RDF_NON_PERIODIC_STRUCTURE"

    with pytest.raises(ToolExecutionError) as site_error:
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"max_sites": 1})

    assert site_error.value.details["errorType"] == "RDF_SITE_LIMIT_EXCEEDED"

    with pytest.raises(ToolExecutionError) as neighbor_error:
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"r_max_angstrom": 4.0, "bin_width_angstrom": 0.5, "max_neighbors_total": 1})

    assert neighbor_error.value.details["errorType"] == "RDF_NEIGHBOR_LIMIT_EXCEEDED"


def test_rdf_artifacts_do_not_contain_js_or_external_urls() -> None:
    artifacts = _execute_adapter(object_store={"structures": [_si_structure()]}, params={"r_max_angstrom": 4.0, "bin_width_angstrom": 0.5})
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


def test_rdf_registered_with_strict_schema_and_static_artifacts() -> None:
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.rdf")

    assert tool in registry.list_mvp_tools()
    assert tool.domain == "structure"
    assert tool.paramsSchema["additionalProperties"] is False
    assert set(tool.paramsSchema["properties"]) >= {
        "r_max_angstrom",
        "bin_width_angstrom",
        "normalization",
        "include_partial_pairs",
        "max_partial_pairs",
        "max_sites",
        "max_bins",
        "max_neighbors_total",
        "plot_kind",
    }
    assert tool.artifactTypes == [
        ArtifactType.table_json,
        ArtifactType.plotly_json,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    ]
    description = tool.description.lower()
    assert "radial distribution function" in description
    assert "periodic crystalline" in description
    assert "experimental pdf fitting" in description
    assert "phonon dos" in description
    assert "3d viewer" in description
    assert "local environment classification" in description


@pytest.mark.parametrize(
    "prompt",
    [
        "计算 RDF",
        "生成 RDF",
        "计算径向分布函数",
        "生成径向分布函数",
        "Generate radial distribution function",
        "Create an RDF plot for this structure",
        "Compute pair distribution g(r)",
        "Show radial distribution g(r)",
    ],
)
def test_mock_planner_routes_rdf_prompts(prompt: str) -> None:
    plan = _mock_plan(prompt)

    assert plan["steps"][0]["toolId"] == "structure.rdf"
    assert plan["steps"][0]["params"]["normalization"] == "number_density"
    assert plan["expectedArtifacts"][0]["name"] == "rdf.json"
    assert any(item["name"] == "rdf_plot.json" for item in plan["expectedArtifacts"])


@pytest.mark.parametrize(
    ("prompt", "expected_tool"),
    [
        ("Generate XRD pattern", "structure.xrd"),
        ("Create a coordination number histogram for this structure", "structure.coordination_hist"),
    ],
)
def test_mock_planner_routes_existing_physics_tools_without_rdf_regression(prompt: str, expected_tool: str) -> None:
    plan = _mock_plan(prompt)

    assert plan["steps"][0]["toolId"] == expected_tool


@pytest.mark.parametrize(
    "prompt",
    [
        "Open an interactive 3D viewer",
        "Use WebGL to display this crystal",
        "Generate Brillouin zone 3D",
        "Plot phonon bands",
        "Plot phonon DOS",
        "experimental PDF fitting",
        "neutron scattering refinement",
        "Rietveld refinement",
    ],
)
def test_mock_planner_does_not_route_deferred_prompts_to_rdf(prompt: str) -> None:
    plan = _mock_plan(prompt)

    assert plan["steps"][0]["toolId"] != "structure.rdf"


def test_persisted_rdf_plan_executes_exactly_one_tool_call(tmp_path: Path) -> None:
    repos = InMemoryRepositoryBundle.create()
    plan = _valid_rdf_plan()
    provider = MockLLMProvider(fixed_plan=plan.model_dump(mode="json"))
    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Create an RDF plot for this structure.",
            projectId="project_10e7",
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
    assert tool_calls[0]["toolId"] == "structure.rdf"
    assert {artifact["name"] for artifact in artifacts} >= {
        "rdf.json",
        "rdf_plot.json",
        "summary.md",
        "recipe.json",
    }


def _execute_adapter(
    *,
    object_store: dict[str, Any],
    params: dict[str, Any] | None = None,
    artifact_types: list[ArtifactType] | None = None,
) -> dict[str, Any]:
    artifact_root = Path(tempfile.mkdtemp(prefix="mdi_phase10e7_artifacts_"))
    context = ToolExecutionContext(
        job_id="job_10e7",
        project_id="project_10e7",
        dataset_id="dataset_structure",
        tool_id="structure.rdf",
        tool_version="0.1.0",
        adapter_version="0.1.0",
        registry_version=load_manifests().version,
        artifact_root=artifact_root,
        object_store=object_store,
        resource_limits={
            "maxAtomsPerStructure": 1000,
            "maxStructures": 100,
            "maxSites": 5000,
            "maxBins": 5000,
            "maxNeighborsTotal": 2000000,
            "maxPartialPairs": 256,
        },
    )
    request = {
        "jobId": "job_10e7",
        "stepId": "step_001",
        "toolId": "structure.rdf",
        "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
        "params": params or {},
        "artifactTypes": [artifact_type.value for artifact_type in (artifact_types or [
            ArtifactType.table_json,
            ArtifactType.plotly_json,
            ArtifactType.summary_md,
            ArtifactType.recipe_json,
        ])],
    }
    return {"root": artifact_root, "artifacts": RdfAdapter().execute(context, request)}


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


def _valid_rdf_plan() -> AnalysisPlan:
    return AnalysisPlan.model_validate(
        {
            "schemaVersion": "0.1",
            "goal": "rdf",
            "datasetId": "dataset_structure",
            "profileId": "profile_structure",
            "toolRegistryVersion": load_manifests().version,
            "assumptions": [],
            "warnings": [],
            "steps": [
                {
                    "stepId": "step_001",
                    "toolId": "structure.rdf",
                    "purpose": "rdf",
                    "reason": "test",
                    "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
                    "params": {
                        "r_max_angstrom": 4.0,
                        "bin_width_angstrom": 0.5,
                        "normalization": "number_density",
                        "include_partial_pairs": True,
                        "max_partial_pairs": 64,
                        "max_sites": 500,
                        "max_bins": 1000,
                        "max_neighbors_total": 200000,
                        "plot_kind": "line",
                    },
                    "output": {"artifactTypes": ["table_json", "plotly_json", "summary_md", "recipe_json"]},
                }
            ],
            "expectedArtifacts": [
                {"name": "rdf.json", "type": "table_json", "fromStepId": "step_001"},
                {"name": "rdf_plot.json", "type": "plotly_json", "fromStepId": "step_001"},
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


def _nacl_structure() -> Structure:
    return Structure(
        Lattice.cubic(5.64),
        ["Na", "Cl"],
        [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
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
            "createdAt": "2026-07-09T00:00:00+00:00",
        }
    )
