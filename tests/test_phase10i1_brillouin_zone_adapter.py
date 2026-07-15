from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import numpy as np
import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import BrillouinZoneAdapter, ToolExecutionContext, ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import (
    BRILLOUIN_TOLERANCES,
    BRILLOUIN_ZONE_MANIFEST_SCHEMA_VERSION,
    BRILLOUIN_ZONE_SCHEMA_VERSION,
    KPATH_SCHEMA_VERSION,
    RECIPROCAL_LATTICE_SCHEMA_VERSION,
    stable_brillouin_json,
    validate_brillouin_zone,
    validate_brillouin_zone_manifest,
    validate_kpath,
    validate_reciprocal_lattice,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "phase10i" / "evidence" / "phase10i1_brillouin_zone_adapter"
ARTIFACT_TYPES = [
    "reciprocal_lattice_json",
    "brillouin_zone_json",
    "kpath_json",
    "brillouin_zone_manifest_json",
    "summary_md",
    "recipe_json",
]
DEFAULT_PARAMS = {
    "include_reciprocal_lattice": True,
    "include_brillouin_zone": True,
    "include_kpath": True,
    "standardization": "contract_default",
    "kpath_provider": "contract_default",
    "time_reversal": True,
    "symmetry_tolerance_angstrom": 1e-5,
    "angle_tolerance_degrees": 5.0,
    "include_alternative_path_variants": False,
}


def _profile() -> DataProfile:
    return DataProfile.model_validate(
        {
            "schemaVersion": "0.1",
            "profileId": "profile_bz",
            "datasetId": "dataset_bz",
            "version": "1",
            "datasetType": "structure_collection",
            "objects": [{"objectType": "Structure", "count": 1, "source": "crystal.cif"}],
            "structureSummary": {
                "nStructures": 1,
                "elements": ["Si"],
                "formulaStats": {"total": 1, "uniqueCount": 1},
            },
            "qualityIssues": [],
            "recommendedTasks": [],
            "createdAt": "2026-07-14T00:00:00Z",
        }
    )


def _context(root: Path, source: object) -> ToolExecutionContext:
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.brillouin_zone")
    return ToolExecutionContext(
        job_id="job_bz",
        project_id="project_bz",
        dataset_id="dataset_bz",
        tool_id=tool.toolId,
        tool_version=tool.version,
        adapter_version="1.0.0",
        registry_version=registry.version,
        artifact_root=root,
        tool_call_id="call_bz",
        object_store={"structures": source},
        resource_limits=tool.resourceLimits,
    )


def _request(params: dict | None = None) -> ToolExecutionRequest:
    return ToolExecutionRequest(
        jobId="job_bz",
        stepId="step_001",
        toolId="structure.brillouin_zone",
        inputRefs=[{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
        params=DEFAULT_PARAMS if params is None else params,
        artifactTypes=ARTIFACT_TYPES,
    )


def _execute(root: Path, structure: object, params: dict | None = None) -> tuple[list, dict[str, object]]:
    artifacts = BrillouinZoneAdapter().execute(_context(root, structure), _request(params))
    payloads: dict[str, object] = {}
    for artifact in artifacts:
        text = (root / artifact.storageKey).read_text(encoding="utf-8")
        payloads[artifact.name] = json.loads(text) if artifact.name.endswith(".json") else text
    return artifacts, payloads


def _plan(prompt: str) -> dict:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(prompt, "dataset_bz", "profile_bz", registry.version),
        tools=registry.list_mvp_tools(),
        data_profile=_profile(),
    )
    assert response.raw_json is not None
    return response.raw_json


def _sc() -> Structure:
    return Structure(Lattice.cubic(4.0), ["Si"], [[0, 0, 0]])


def _bcc_conventional() -> Structure:
    return Structure(Lattice.cubic(4.0), ["Fe", "Fe"], [[0, 0, 0], [0.5, 0.5, 0.5]])


def _bcc_primitive() -> Structure:
    a = 4.0
    lattice = Lattice([[-a / 2, a / 2, a / 2], [a / 2, -a / 2, a / 2], [a / 2, a / 2, -a / 2]])
    return Structure(lattice, ["Fe"], [[0, 0, 0]])


def _fcc() -> Structure:
    return Structure(
        Lattice.cubic(4.0),
        ["Al"] * 4,
        [[0, 0, 0], [0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]],
    )


def _hexagonal() -> Structure:
    return Structure(Lattice.hexagonal(3.0, 5.2), ["Mg"], [[0, 0, 0]])


def _triclinic() -> Structure:
    return Structure(Lattice([[3.1, 0.2, 0.1], [0.7, 4.0, 0.3], [0.4, 0.8, 5.1]]), ["Si"], [[0.137, 0.271, 0.419]])


def test_registry_declares_one_strict_json_only_brillouin_tool() -> None:
    registry = load_manifests()
    matches = [tool for tool in registry.tools if tool.toolId == "structure.brillouin_zone"]
    assert len(matches) == 1
    tool = matches[0]
    assert tool.adapter == "BrillouinZoneAdapter"
    assert [item.value for item in tool.artifactTypes] == ARTIFACT_TYPES
    assert tool.inputSchema.periodicity == "periodic_required"
    assert tool.inputSchema.inputOptions[0].requiredObjectTypes == ["Structure"]
    assert tool.paramsSchema["additionalProperties"] is False
    assert tool.paramsSchema["properties"]["time_reversal"] == {"const": True}
    assert tool.resourceLimits["maxCandidatePlanes"] == 728
    description = tool.description.lower()
    assert "renderer" in description and "no renderer" in description
    assert "external assets" in description and "network" in description
    assert "interactive" in description and "electronic bands" in description


@pytest.mark.parametrize(
    "prompt",
    (
        "计算这个晶体的第一布里渊区",
        "生成倒易晶格和高对称路径",
        "导出这个结构的Brillouin zone数据",
        "计算这个晶体的k路径",
        "Generate first Brillouin zone data",
        "Export the reciprocal lattice and high-symmetry path",
        "Build a Brillouin zone JSON artifact",
        "Compute the standardized k-path for this crystal",
        "打开交互式布里渊区3D viewer",
        "显示可旋转的第一布里渊区",
        "Open an interactive Brillouin zone viewer",
        "Show the first Brillouin zone in 3D",
    ),
)
def test_planner_routes_approved_data_generation_prompts(prompt: str) -> None:
    plan = _plan(prompt)
    assert plan["steps"][0]["toolId"] == "structure.brillouin_zone"
    assert plan["steps"][0]["params"] == DEFAULT_PARAMS
    assert validate_plan(plan, registry=load_manifests()).ok
    assert [item["name"] for item in plan["expectedArtifacts"]] == [
        "reciprocal_lattice.json",
        "brillouin_zone.json",
        "kpath.json",
        "brillouin_zone_manifest.json",
        "summary.md",
        "recipe.json",
    ]


@pytest.mark.parametrize(
    "prompt",
    (
        "计算电子能带",
        "计算声子",
        "播放声子模式",
        "显示MD trajectory",
        "生成Fermi surface",
        "计算Monkhorst-Pack mesh",
        "显示charge density",
        "生成XRD",
        "做CrystalNN",
        "编辑结构",
        "运行DFT",
        "显示 magnetic Brillouin zone",
        "显示 surface BZ",
    ),
)
def test_planner_negative_domains_never_route_to_brillouin_adapter(prompt: str) -> None:
    assert _plan(prompt)["steps"][0]["toolId"] != "structure.brillouin_zone"


def test_valid_simple_cubic_emits_six_valid_inert_artifacts(tmp_path: Path) -> None:
    artifacts, payloads = _execute(tmp_path, _sc())
    assert [artifact.type.value for artifact in artifacts] == ARTIFACT_TYPES
    assert [artifact.name for artifact in artifacts] == [
        "reciprocal_lattice.json",
        "brillouin_zone.json",
        "kpath.json",
        "brillouin_zone_manifest.json",
        "summary.md",
        "recipe.json",
    ]
    reciprocal = payloads["reciprocal_lattice.json"]
    zone = payloads["brillouin_zone.json"]
    kpath = payloads["kpath.json"]
    manifest = payloads["brillouin_zone_manifest.json"]
    assert reciprocal["schema_version"] == RECIPROCAL_LATTICE_SCHEMA_VERSION
    assert zone["schema_version"] == BRILLOUIN_ZONE_SCHEMA_VERSION
    assert kpath["schema_version"] == KPATH_SCHEMA_VERSION
    assert manifest["schema_version"] == BRILLOUIN_ZONE_MANIFEST_SCHEMA_VERSION
    assert validate_reciprocal_lattice(reciprocal).valid
    assert validate_brillouin_zone(zone, reciprocal).valid
    assert validate_kpath(kpath, reciprocal).valid
    assert validate_brillouin_zone_manifest(manifest, reciprocal, zone, kpath).valid
    assert reciprocal["provider"]["warnings"] == []
    assert kpath["provider"]["warnings"] == []
    assert zone["topology"] == {
        "vertex_count": 8,
        "edge_count": 12,
        "face_count": 6,
        "euler_characteristic": 2,
        "closed": True,
        "convex": True,
        "manifold": True,
        "connected": True,
        "centrally_symmetric": True,
    }
    expected_matrix = 2 * np.pi * np.linalg.inv(np.asarray(_sc().lattice.matrix)).T
    assert np.allclose(reciprocal["matrix"], expected_matrix, atol=1e-11)
    assert math.isclose(zone["volume"], abs(float(np.linalg.det(expected_matrix))), rel_tol=1e-8)
    assert manifest["capabilities"]["preview_mode"] == "json_only"
    assert manifest["capabilities"]["renderer_included"] is False
    assert "renderer not included" in payloads["summary.md"]
    assert payloads["recipe.json"]["scientificContract"]["externalNetwork"] is False


@pytest.mark.parametrize(
    ("structure", "topology"),
    (
        (_bcc_conventional(), (14, 24, 12)),
        (_fcc(), (24, 36, 14)),
        (_hexagonal(), (12, 18, 8)),
    ),
    ids=("bcc", "fcc", "hexagonal"),
)
def test_known_lattice_topologies_match_phase10i_references(
    tmp_path: Path,
    structure: Structure,
    topology: tuple[int, int, int],
) -> None:
    _, payloads = _execute(tmp_path, structure)
    actual = payloads["brillouin_zone.json"]["topology"]
    assert (actual["vertex_count"], actual["edge_count"], actual["face_count"]) == topology
    assert actual["euler_characteristic"] == 2


@pytest.mark.parametrize(
    "structure",
    (
        Structure(Lattice.tetragonal(3.2, 5.1), ["Si"], [[0, 0, 0]]),
        Structure(Lattice.orthorhombic(3.1, 4.2, 5.3), ["Si"], [[0, 0, 0]]),
        Structure(Lattice.monoclinic(3.1, 4.2, 5.3, 103), ["Si"], [[0, 0, 0]]),
        _triclinic(),
    ),
    ids=("tetragonal", "orthorhombic", "monoclinic", "triclinic"),
)
def test_lower_symmetry_lattices_validate_with_nonempty_paths(tmp_path: Path, structure: Structure) -> None:
    _, payloads = _execute(tmp_path, structure)
    reciprocal = payloads["reciprocal_lattice.json"]
    zone = payloads["brillouin_zone.json"]
    kpath = payloads["kpath.json"]
    assert validate_reciprocal_lattice(reciprocal).valid
    assert validate_brillouin_zone(zone, reciprocal).valid
    assert validate_kpath(kpath, reciprocal).valid
    assert kpath["points"] and kpath["segments"]


def test_conventional_and_primitive_bcc_share_standardized_primitive_identity(tmp_path: Path) -> None:
    _, conventional = _execute(tmp_path / "conventional", _bcc_conventional())
    _, primitive = _execute(tmp_path / "primitive", _bcc_primitive())
    left = conventional["reciprocal_lattice.json"]
    right = primitive["reciprocal_lattice.json"]
    assert left["real_lattice_binding"]["primitive_lattice_sha256"] == right["real_lattice_binding"]["primitive_lattice_sha256"]
    assert np.allclose(left["matrix"], right["matrix"], atol=1e-11)
    assert conventional["brillouin_zone.json"]["topology"] == primitive["brillouin_zone.json"]["topology"]


def test_scientific_artifacts_replay_deterministically_without_input_mutation(tmp_path: Path) -> None:
    source = _triclinic()
    original = copy.deepcopy(source.as_dict())
    _, first = _execute(tmp_path / "first", source)
    _, second = _execute(tmp_path / "second", source)
    assert source.as_dict() == original
    for name in (
        "reciprocal_lattice.json",
        "brillouin_zone.json",
        "kpath.json",
        "brillouin_zone_manifest.json",
    ):
        assert stable_brillouin_json(first[name]) == stable_brillouin_json(second[name])


@pytest.mark.parametrize(
    ("source", "error_type"),
    (
        ([_sc(), _sc()], "multiple_structures_unsupported"),
        (Structure(Lattice.cubic(4), [{"Si": 0.5, "Ge": 0.5}], [[0, 0, 0]]), "partial_occupancy_unsupported"),
        (Structure(Lattice.cubic(4), ["Fe"], [[0, 0, 0]], site_properties={"magmom": [1.0]}), "magnetic_structure_unsupported"),
        ("not a periodic structure", "unsupported_structure_format"),
    ),
)
def test_unsupported_inputs_fail_before_artifact_export(
    tmp_path: Path,
    source: object,
    error_type: str,
) -> None:
    with pytest.raises(ToolExecutionError) as exc:
        _execute(tmp_path, source)
    assert exc.value.details["errorType"] == error_type
    assert list(tmp_path.rglob("*")) == []


def test_dimensionality_singular_and_ill_conditioned_inputs_are_typed(tmp_path: Path) -> None:
    two_dimensional = _sc()
    two_dimensional.properties["periodic_dimension"] = 2
    singular = Structure(Lattice([[1, 0, 0], [2, 0, 0], [0, 0, 1]]), ["Si"], [[0, 0, 0]])
    ill_conditioned = Structure(Lattice([[1, 0, 0], [0, 1, 0], [0, 0, 1e-9]]), ["Si"], [[0, 0, 0]])
    for name, source, error_type in (
        ("2d", two_dimensional, "unsupported_dimensionality"),
        ("singular", singular, "singular_lattice"),
        ("condition", ill_conditioned, "ill_conditioned_lattice"),
    ):
        with pytest.raises(ToolExecutionError) as exc:
            _execute(tmp_path / name, source)
        assert exc.value.details["errorType"] == error_type


def test_params_and_plan_validator_reject_unapproved_variants() -> None:
    plan = _plan("Generate first Brillouin zone data")
    registry = load_manifests()
    for key, value in (
        ("unknown", True),
        ("time_reversal", False),
        ("symmetry_tolerance_angstrom", 0.0),
        ("kpath_provider", "seekpath"),
    ):
        invalid = copy.deepcopy(plan)
        invalid["steps"][0]["params"][key] = value
        result = validate_plan(invalid, registry=registry)
        assert not result.ok


def test_adapter_rejects_partial_artifact_package_requests(tmp_path: Path) -> None:
    request = _request()
    request.artifactTypes = request.artifactTypes[:-1]
    with pytest.raises(ToolExecutionError) as exc:
        BrillouinZoneAdapter().execute(_context(tmp_path, _sc()), request)
    assert exc.value.details["errorType"] == "artifact_request_mismatch"
    assert list(tmp_path.rglob("*")) == []


def test_planner_job_runtime_persists_six_artifacts_and_replays(tmp_path: Path) -> None:
    registry = load_manifests()
    plan = _plan("Generate first Brillouin zone data")
    captures: list[dict[str, str]] = []
    for suffix in ("first", "second"):
        repositories = InMemoryRepositoryBundle.create()
        root = tmp_path / suffix
        runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=root)
        created = planner_jobs(
            PlannerJobsRequest(
                userPrompt="Generate first Brillouin zone data",
                projectId="project_bz",
                datasetId="dataset_bz",
                profileId="profile_bz",
                enqueue=True,
            ),
            provider=MockLLMProvider(fixed_plan=plan),
            repositories=repositories,
            queue_runtime=runtime,
            registry=registry,
        )
        assert created.ok and created.job_id and created.enqueued
        result = runtime.handle_job(created.job_id, object_store={"structures": [_sc()]})
        assert result.status == "completed"
        calls = repositories.tool_calls.list_for_job(created.job_id)
        records = repositories.artifacts.list_for_job(created.job_id)
        assert len(calls) == 1 and calls[0]["toolId"] == "structure.brillouin_zone"
        assert calls[0]["status"] == "completed"
        assert [record["name"] for record in records] == [
            "reciprocal_lattice.json",
            "brillouin_zone.json",
            "kpath.json",
            "brillouin_zone_manifest.json",
            "summary.md",
            "recipe.json",
        ]
        captures.append(
            {
                record["name"]: (root / record["storageKey"]).read_text(encoding="utf-8")
                for record in records
                if record["name"] not in {"summary.md", "recipe.json"}
            }
        )
    assert captures[0] == captures[1]


def test_contract_tolerances_remain_unchanged() -> None:
    assert BRILLOUIN_TOLERANCES["symmetry_symprec_angstrom"] == 1e-5
    assert BRILLOUIN_TOLERANCES["symmetry_angle_tolerance_degrees"] == 5.0


def test_evidence_bundle_records_runtime_validation_replay_and_security() -> None:
    manifest = json.loads((EVIDENCE / "evidence_manifest.json").read_text(encoding="utf-8"))
    runtime = json.loads((EVIDENCE / "api" / "runtime_cases.json").read_text(encoding="utf-8"))
    validations = json.loads((EVIDENCE / "validation" / "canonical_validation.json").read_text(encoding="utf-8"))
    security = json.loads((EVIDENCE / "security" / "security_audit.json").read_text(encoding="utf-8"))
    assert manifest["toolId"] == "structure.brillouin_zone"
    assert manifest["rendererIncluded"] is False
    assert manifest["externalNetworkRequests"] == 0
    assert manifest["secretPatternHits"] == 0
    assert set(manifest["completedCases"]) == {
        "simple_cubic",
        "hexagonal",
        "triclinic",
        "bcc_conventional",
        "bcc_primitive",
    }
    assert set(manifest["failedAsExpectedCases"]) == {"singular_lattice", "non_periodic"}
    assert all(value["valid"] for value in validations.values())
    assert all(runtime[name]["artifactCount"] == 6 for name in manifest["completedCases"])
    assert all(runtime[name]["artifactCount"] == 0 for name in manifest["failedAsExpectedCases"])
    assert security["noExternalNetworkRequests"] is True
    assert security["noSecretPatternHits"] is True
