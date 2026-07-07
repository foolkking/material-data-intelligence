from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import (
    LatticeSummaryAdapter,
    SpacegroupSummaryAdapter,
    StructureCompositionAdapter,
    StructurePreviewMetadataAdapter,
    StructureSummaryAdapter,
)
from mdi_adapters.context import ToolExecutionContext
from mdi_adapters.errors import ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import AnalysisPlan, ArtifactType, DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


def test_fixture_cif_poscar_and_normalized_structure_parse(repo_root: Path) -> None:
    fixture_dir = repo_root / "tests" / "fixtures" / "structures"

    cif_structure = Structure.from_file(fixture_dir / "simple_cubic.cif")
    poscar_text = (fixture_dir / "nacl.poscar").read_text(encoding="utf-8")
    poscar_artifacts = _execute_adapter(
        StructureSummaryAdapter(),
        "structure.summary",
        object_store={"structures": poscar_text},
        artifact_types=[ArtifactType.structure_json, ArtifactType.summary_md, ArtifactType.recipe_json],
    )
    normalized = json.loads((fixture_dir / "structure_collection.json").read_text(encoding="utf-8"))
    normalized_artifacts = _execute_adapter(
        StructureSummaryAdapter(),
        "structure.summary",
        object_store={"structures": normalized},
        artifact_types=[ArtifactType.structure_json, ArtifactType.summary_md, ArtifactType.recipe_json],
    )

    assert cif_structure.composition.reduced_formula == "Si"
    assert _artifact_payload(poscar_artifacts, "structure_summary.json")["structures"][0]["reducedFormula"] == "NaCl"
    assert _artifact_payload(normalized_artifacts, "structure_summary.json")["structures"][0]["formula"] == "Si1"


def test_malformed_cif_parse_failure(repo_root: Path) -> None:
    fixture = repo_root / "tests" / "fixtures" / "structures" / "malformed.cif"

    with pytest.raises(Exception):
        Structure.from_file(fixture)


def test_structure_summary_generates_json_summary_and_recipe() -> None:
    artifacts = _execute_adapter(
        StructureSummaryAdapter(),
        "structure.summary",
        object_store={"structures": [_simple_structure()]},
        params={"includeSitesPreview": True, "maxPreviewSites": 1},
        artifact_types=[ArtifactType.structure_json, ArtifactType.summary_md, ArtifactType.recipe_json],
    )

    payload = _artifact_payload(artifacts, "structure_summary.json")
    assert {artifact.type for artifact in artifacts["artifacts"]} == {"structure_json", "summary_md", "recipe_json"}
    assert payload["artifactType"] == "structure.summary"
    assert payload["structureCount"] == 1
    assert payload["structures"][0]["numSites"] == 2
    assert payload["structures"][0]["lattice"]["a"] == 5.64
    assert len(payload["structures"][0]["sitesPreview"]) == 1


def test_lattice_summary_generates_deterministic_stats() -> None:
    artifacts = _execute_adapter(
        LatticeSummaryAdapter(),
        "structure.lattice_summary",
        object_store={"structures": [_simple_structure(), _silicon_structure()]},
        artifact_types=[ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json],
    )

    payload = _artifact_payload(artifacts, "lattice_summary.json")
    second = _artifact_payload(
        _execute_adapter(
            LatticeSummaryAdapter(),
            "structure.lattice_summary",
            object_store={"structures": [_simple_structure(), _silicon_structure()]},
            artifact_types=[ArtifactType.table_json],
        ),
        "lattice_summary.json",
    )
    assert payload == second
    assert payload["artifactType"] == "structure.lattice_summary"
    assert payload["structureCount"] == 2
    assert payload["latticeStats"]["volume"]["min"] > 0


def test_spacegroup_summary_detects_real_symmetry() -> None:
    artifacts = _execute_adapter(
        SpacegroupSummaryAdapter(),
        "structure.spacegroup_summary",
        object_store={"structures": [_simple_structure()]},
        params={"symprec": 0.01, "angleTolerance": 5},
        artifact_types=[ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json],
    )

    payload = _artifact_payload(artifacts, "spacegroup_summary.json")
    assert payload["artifactType"] == "structure.spacegroup_summary"
    assert payload["symmetryEngine"] == "pymatgen/spglib"
    assert payload["spacegroups"]
    assert payload["spacegroups"][0]["number"] > 0
    assert payload["crystalSystemCounts"]


def test_structure_composition_from_structure_recommends_composition_tools() -> None:
    artifacts = _execute_adapter(
        StructureCompositionAdapter(),
        "structure.composition_from_structure",
        object_store={"structures": [_simple_structure()]},
        artifact_types=[ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json],
    )

    payload = _artifact_payload(artifacts, "structure_composition.json")
    assert payload["artifactType"] == "structure.composition_from_structure"
    assert payload["formulaCount"] == 1
    assert payload["elementCounts"] == {"Cl": 1.0, "Na": 1.0}
    assert "composition.elements_hist" in payload["recommendedNextTools"]


def test_structure_preview_metadata_truncates_sites() -> None:
    artifacts = _execute_adapter(
        StructurePreviewMetadataAdapter(),
        "structure.preview_metadata",
        object_store={"structures": [_simple_structure()]},
        params={"maxPreviewSites": 1, "includeCartesian": True, "includeFractional": True},
        artifact_types=[ArtifactType.structure_json, ArtifactType.summary_md, ArtifactType.recipe_json],
    )

    payload = _artifact_payload(artifacts, "structure_preview_metadata.json")
    assert payload["artifactType"] == "structure.preview_metadata"
    assert payload["numSites"] == 2
    assert payload["truncated"] is True
    assert len(payload["sitesPreview"]) == 1
    assert payload["boundingBox"]["x"][1] > 0


def test_structure_adapters_reject_missing_or_malformed_input() -> None:
    with pytest.raises(ToolExecutionError) as exc_info:
        _execute_adapter(
            StructureSummaryAdapter(),
            "structure.summary",
            object_store={"structures": "not a structure"},
            artifact_types=[ArtifactType.structure_json],
        )

    assert exc_info.value.details["errorType"] == "unsupported_structure_format"


def test_structure_tools_are_registered_with_strict_params() -> None:
    registry = load_manifests()
    tool_ids = {
        "structure.summary",
        "structure.lattice_summary",
        "structure.spacegroup_summary",
        "structure.composition_from_structure",
        "structure.preview_metadata",
    }

    for tool_id in tool_ids:
        tool = registry.get_tool_by_id(tool_id)
        assert tool.domain == "structure"
        assert tool.paramsSchema["additionalProperties"] is False
        assert tool.adapter.endswith("Adapter")


@pytest.mark.parametrize(
    ("prompt", "expected_tool"),
    [
        ("Please summarize this CIF structure, atom count, and lattice parameters.", "structure.summary"),
        ("请分析晶格参数和晶胞体积。", "structure.lattice_summary"),
        ("Please identify the space group and crystal system.", "structure.spacegroup_summary"),
        ("请从结构文件中提取 composition 并统计元素组成。", "structure.composition_from_structure"),
        ("请生成结构预览 metadata 和坐标范围。", "structure.preview_metadata"),
    ],
)
def test_mock_planner_routes_structure_prompts(prompt: str, expected_tool: str) -> None:
    plan = _mock_plan(prompt, _structure_profile())

    assert plan["steps"][0]["toolId"] == expected_tool


def test_mock_planner_does_not_claim_3d_viewer_support() -> None:
    plan = _mock_plan("Please render a 3D structure viewer.", _structure_profile())

    assert plan["steps"][0]["toolId"] == "structure.preview_metadata"
    assert plan["steps"][0]["toolId"] != "structure.viewer_3d"
    assert "future scope" in plan["steps"][0]["reason"].lower()


def test_structure_prompt_not_routed_to_composition_or_histogram() -> None:
    plan = _mock_plan("请总结结构的元素组成、原子数和晶格参数。", _structure_profile())

    assert plan["steps"][0]["toolId"].startswith("structure.")
    assert not plan["steps"][0]["toolId"].startswith("composition.")
    assert plan["steps"][0]["toolId"] != "viz.histogram"


def test_persisted_structure_plan_executes_exactly_one_tool_call(tmp_path: Path) -> None:
    repos = InMemoryRepositoryBundle.create()
    plan = _valid_structure_plan("structure.preview_metadata")
    provider = MockLLMProvider(fixed_plan=plan.model_dump(mode="json"))
    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Please prepare structure preview metadata.",
            projectId="project_10c1",
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
    worker_result = runtime.handle_job(result.job_id or "", object_store={"structures": [_simple_structure()]})

    tool_calls = repos.tool_calls.list_for_job(result.job_id or "")
    artifacts = repos.artifacts.list_for_job(result.job_id or "")
    assert worker_result.status == "completed"
    assert worker_result.tool_call_count == 1
    assert tool_calls[0]["toolId"] == "structure.preview_metadata"
    assert {artifact["type"] for artifact in artifacts} >= {"structure_json", "summary_md", "recipe_json"}


def test_invalid_structure_plan_params_rejected_before_persistence() -> None:
    repos = InMemoryRepositoryBundle.create()
    bad_plan = _valid_structure_plan("structure.summary").model_dump(mode="json")
    bad_plan["steps"][0]["params"]["unexpected"] = True
    provider = MockLLMProvider(fixed_plan=bad_plan)

    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="bad structure plan",
            projectId="project_10c1",
            datasetId="dataset_structure",
            profileId="profile_structure",
        ),
        provider=provider,
        repositories=repos,
        registry=load_manifests(),
    )

    assert result.ok is False
    assert result.job_id is None
    assert result.plan_id is None
    assert repos.jobs.records == {}
    assert repos.analysis_plans.records == {}


def _execute_adapter(
    adapter: Any,
    tool_id: str,
    *,
    object_store: dict[str, Any],
    params: dict[str, Any] | None = None,
    artifact_types: list[ArtifactType],
) -> dict[str, Any]:
    artifact_root = Path(tempfile.mkdtemp(prefix="mdi_phase10c1_artifacts_"))
    context = ToolExecutionContext(
        job_id="job_10c1",
        project_id="project_10c1",
        dataset_id="dataset_structure",
        tool_id=tool_id,
        tool_version="0.1.0",
        adapter_version="0.1.0",
        registry_version=load_manifests().version,
        artifact_root=artifact_root,
        object_store=object_store,
        resource_limits={"maxAtomsPerStructure": 1000, "maxStructures": 100},
    )
    request = {
        "jobId": "job_10c1",
        "stepId": "step_001",
        "toolId": tool_id,
        "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
        "params": params or {},
        "artifactTypes": [artifact_type.value for artifact_type in artifact_types],
    }
    return {"root": artifact_root, "artifacts": adapter.execute(context, request)}


def _artifact_payload(result: dict[str, Any], name: str) -> dict[str, Any]:
    artifact = next(item for item in result["artifacts"] if item.name == name)
    return json.loads((result["root"] / artifact.storageKey).read_text(encoding="utf-8"))


def _mock_plan(prompt: str, profile: DataProfile) -> dict[str, Any]:
    response = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt=prompt,
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            tool_registry_version=load_manifests().version,
        ),
        tools=load_manifests().list_mvp_tools(),
        data_profile=profile,
    )
    assert response.raw_json is not None
    return response.raw_json


def _valid_structure_plan(tool_id: str) -> AnalysisPlan:
    artifact_name = {
        "structure.summary": "structure_summary.json",
        "structure.lattice_summary": "lattice_summary.json",
        "structure.spacegroup_summary": "spacegroup_summary.json",
        "structure.composition_from_structure": "structure_composition.json",
        "structure.preview_metadata": "structure_preview_metadata.json",
    }[tool_id]
    artifact_type = "structure_json" if tool_id in {"structure.summary", "structure.preview_metadata"} else "table_json"
    return AnalysisPlan.model_validate(
        {
            "schemaVersion": "0.1",
            "goal": "structure",
            "datasetId": "dataset_structure",
            "profileId": "profile_structure",
            "toolRegistryVersion": load_manifests().version,
            "assumptions": [],
            "warnings": [],
            "steps": [
                {
                    "stepId": "step_001",
                    "toolId": tool_id,
                    "purpose": "structure",
                    "reason": "test",
                    "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
                    "params": _valid_params(tool_id),
                    "output": {"artifactTypes": [artifact_type, "summary_md", "recipe_json"]},
                }
            ],
            "expectedArtifacts": [
                {"name": artifact_name, "type": artifact_type, "fromStepId": "step_001"},
                {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
                {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
            ],
        }
    )


def _valid_params(tool_id: str) -> dict[str, Any]:
    return {
        "structure.summary": {"maxStructures": 50, "includeSitesPreview": True, "maxPreviewSites": 20},
        "structure.lattice_summary": {"maxStructures": 100, "detectOutliers": True},
        "structure.spacegroup_summary": {"symprec": 0.01, "angleTolerance": 5, "maxStructures": 50},
        "structure.composition_from_structure": {"maxStructures": 100, "includeRecommendedTools": True},
        "structure.preview_metadata": {"maxPreviewSites": 100, "includeCartesian": True, "includeFractional": True},
    }[tool_id]


def _simple_structure() -> Structure:
    return Structure(Lattice.cubic(5.64), ["Na", "Cl"], [[0, 0, 0], [0.5, 0.5, 0.5]])


def _silicon_structure() -> Structure:
    return Structure(Lattice.cubic(3.0), ["Si"], [[0, 0, 0]])


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
                "elements": ["Na", "Cl"],
                "formulaStats": {"total": 1, "uniqueCount": 1},
            },
            "qualityIssues": [],
            "recommendedTasks": [],
            "createdAt": "2026-07-06T00:00:00+00:00",
        }
    )
