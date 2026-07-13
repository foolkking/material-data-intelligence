from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mdi_adapters import ToolExecutionContext
from mdi_adapters.errors import ToolExecutionError
from mdi_adapters.platform_builtin import TrajectoryImportAdapter
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import validate_trajectory, validate_trajectory_manifest, validate_trajectory_summary
from mdi_material_parsers import (
    TrajectoryParseError,
    detect_trajectory_format,
    parse_file,
    parse_trajectory_file,
)
from mdi_schemas import ArtifactType, DataProfile, MaterialObjectType, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10g" / "fixtures" / "trajectory_import"
CONTRACT_FIXTURES = ROOT / "docs" / "phase10g" / "fixtures" / "trajectory_v1"
ARTIFACT_TYPES = [
    "trajectory_json",
    "trajectory_summary_json",
    "trajectory_report_json",
    "trajectory_manifest_json",
]


def test_format_detection_is_content_bounded_and_allowlisted(tmp_path: Path) -> None:
    assert detect_trajectory_format(FIXTURES / "fixed_lattice_md.extxyz") == "extxyz"
    canonical = tmp_path / "trajectory.json"
    canonical.write_text((CONTRACT_FIXTURES / "fixed_lattice_md.json").read_text(encoding="utf-8"), encoding="utf-8")
    assert detect_trajectory_format(canonical) == "canonical_json"
    misleading = tmp_path / "trajectory.extxyz"
    misleading.write_text("not a frame\nProperties=species:S:1:pos:R:3\n", encoding="utf-8")
    with pytest.raises(TrajectoryParseError, match="atom-count") as error:
        detect_trajectory_format(misleading)
    assert error.value.code == "TRAJECTORY_FRAME_HEADER_INVALID"
    plain = tmp_path / "plain.xyz"
    plain.write_text("1\nplain\nH 0 0 0\n", encoding="utf-8")
    with pytest.raises(TrajectoryParseError) as error:
        detect_trajectory_format(plain)
    assert error.value.code == "TRAJECTORY_FORMAT_UNSUPPORTED"


@pytest.mark.parametrize(
    ("name", "kind", "frames", "lattice_mode"),
    (
        ("fixed_lattice_md.extxyz", "molecular_dynamics", 3, "fixed"),
        ("variable_lattice_relaxation.extxyz", "geometry_optimization", 3, "variable"),
        ("triclinic_reordered.extxyz", "structure_sequence", 2, "fixed"),
    ),
)
def test_extxyz_fixtures_normalize_to_contract(name: str, kind: str, frames: int, lattice_mode: str) -> None:
    parsed = parse_trajectory_file(FIXTURES / name)
    assert validate_trajectory(parsed.trajectory).valid
    assert parsed.trajectory["kind"] == kind
    assert len(parsed.trajectory["frames"]) == frames
    assert parsed.trajectory["lattice_mode"] == lattice_mode
    assert parsed.report["detected_format"] == "extxyz"
    assert parsed.report["input_sha256"] == parsed.trajectory["provenance"]["input_sha256"]


def test_stable_source_ids_reorder_without_changing_identity() -> None:
    parsed = parse_trajectory_file(FIXTURES / "triclinic_reordered.extxyz")
    assert parsed.report["reordered_by_atom_id"] is True
    assert parsed.report["warnings"] == ["TRAJECTORY_ATOMS_REORDERED_BY_ID"]
    assert [item["species"] for item in parsed.trajectory["atoms"]["records"]] == ["Li", "F"]
    assert parsed.trajectory["frames"][1]["positions"] == [[0.2, 0.2, 0.3], [2.1, 1.9, 2.1]]


def test_unit_conversion_table_is_applied_and_recorded(tmp_path: Path) -> None:
    source = tmp_path / "units.extxyz"
    source.write_text(
        "1\nLattice=\"1 0 0 0 1 0 0 0 1\" Properties=species:S:1:id:I:1:pos:R:3:vel:R:3:forces:R:3 pbc=\"T T T\" Time=0.002 time_unit=picosecond position_unit=nanometer velocity_unit=nanometer_per_picosecond force_unit=hartree_per_bohr trajectory_kind=molecular_dynamics\n"
        "H 4 0.1 0 0 0.2 0 0 0.01 0 0\n"
        "1\nLattice=\"1 0 0 0 1 0 0 0 1\" Properties=species:S:1:id:I:1:pos:R:3:vel:R:3:forces:R:3 pbc=\"T T T\" Time=0.003 time_unit=picosecond position_unit=nanometer velocity_unit=nanometer_per_picosecond force_unit=hartree_per_bohr trajectory_kind=molecular_dynamics\n"
        "H 4 0.2 0 0 0.2 0 0 0.01 0 0\n",
        encoding="utf-8",
    )
    parsed = parse_trajectory_file(source)
    assert parsed.trajectory["frames"][0]["positions"][0][0] == 1.0
    assert parsed.trajectory["frames"][0]["time"] == 2.0
    assert parsed.trajectory["frames"][0]["velocities"][0][0] == 0.002
    assert len(parsed.report["unit_conversions"]) == 4


@pytest.mark.parametrize(
    ("body", "code"),
    (
        ("0\ncomment\n", "TRAJECTORY_FRAME_HEADER_INVALID"),
        ("1.5\ncomment\n", "TRAJECTORY_FRAME_HEADER_INVALID"),
        ("1\nLattice=\"1 0 0 0 1 0 0 0 1\" Properties=species:S:1 pbc=\"T T T\"\nH\n", "TRAJECTORY_PROPERTIES_DESCRIPTOR_INVALID"),
        ("1\nLattice=\"1 0 0 0 1 0 0 0 1\" Properties=species:S:1:pos:R:3 pbc=\"T T T\"\nH nan 0 0\n", "TRAJECTORY_ATOM_ROW_INVALID"),
        ("1\nLattice=\"1 0 0 0 1 0 0 0 1\" Properties=species:S:1:id:I:1:pos:R:3 pbc=\"T T T\"\nH 1 0 0 0\n1\nLattice=\"1 0 0 0 1 0 0 0 1\" Properties=species:S:1:id:I:1:pos:R:3 pbc=\"T T T\"\nH 2 0 0 0\n", "TRAJECTORY_ATOM_ID_SET_MISMATCH"),
    ),
)
def test_invalid_extxyz_cases_are_typed(tmp_path: Path, body: str, code: str) -> None:
    path = tmp_path / "bad.extxyz"
    path.write_text(body, encoding="utf-8")
    with pytest.raises(TrajectoryParseError) as error:
        parse_trajectory_file(path)
    assert error.value.code == code


def test_truncated_invalid_encoding_line_cap_and_cancellation(tmp_path: Path) -> None:
    with pytest.raises(TrajectoryParseError) as error:
        parse_trajectory_file(FIXTURES / "invalid_truncated.extxyz")
    assert error.value.code == "TRAJECTORY_FRAME_TRUNCATED"
    invalid = tmp_path / "invalid.extxyz"
    invalid.write_bytes(b"1\n\xff\nH 0 0 0\n")
    with pytest.raises(TrajectoryParseError) as error:
        parse_trajectory_file(invalid)
    assert error.value.code == "TRAJECTORY_TEXT_ENCODING_INVALID"
    long_line = tmp_path / "long.extxyz"
    long_line.write_text(
        "1\nLattice=\"1 0 0 0 1 0 0 0 1\" Properties=species:S:1:pos:R:3 pbc=\"T T T\" note=" + "x" * 9000 + "\nH 0 0 0\n",
        encoding="utf-8",
    )
    with pytest.raises(TrajectoryParseError) as error:
        parse_trajectory_file(long_line)
    assert error.value.code in {"TRAJECTORY_LINE_TOO_LONG", "TRAJECTORY_COMMENT_METADATA_INVALID"}
    with pytest.raises(TrajectoryParseError) as error:
        parse_trajectory_file(FIXTURES / "fixed_lattice_md.extxyz", cancel_check=lambda: True)
    assert error.value.code == "TRAJECTORY_PARSE_CANCELLED"


def test_native_canonical_json_is_passed_through_without_semantic_mutation(tmp_path: Path) -> None:
    source = CONTRACT_FIXTURES / "fixed_lattice_md.json"
    target = tmp_path / "trajectory.json"
    target.write_bytes(source.read_bytes())
    parsed = parse_trajectory_file(target)
    original = json.loads(source.read_text(encoding="utf-8"))
    assert parsed.trajectory == original
    assert parsed.report["detected_format"] == "canonical_json"


def test_parse_file_emits_trajectory_object_but_preserves_single_frame_static_extxyz() -> None:
    result = parse_file(FIXTURES / "fixed_lattice_md.extxyz", dataset_id="dataset", file_id="trajectory")
    assert result.parse_status == "success"
    assert result.objects[0].object_type == MaterialObjectType.Trajectory
    assert result.objects[0].metadata["trajectorySummary"]["frameCount"] == 3
    static = parse_file(ROOT / "tests" / "fixtures" / "structures" / "si_lattice.extxyz", dataset_id="dataset", file_id="static")
    assert static.parse_status == "success"
    assert static.objects[0].object_type == MaterialObjectType.Structure


def test_registry_entry_is_internal_strict_and_trajectory_typed() -> None:
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.trajectory_import")
    assert [item.value for item in tool.artifactTypes] == ARTIFACT_TYPES
    assert tool.category.value == "parser"
    assert tool.outputSchema.displayTarget.value == "trajectory"
    assert tool.paramsSchema == {"type": "object", "additionalProperties": False, "properties": {}}
    assert tool.inputSchema.inputOptions[0].requiredObjectTypes == [MaterialObjectType.Trajectory]
    assert "planner-hidden" in tool.description.lower()


def _context(tmp_path: Path, object_store: dict[str, object]) -> ToolExecutionContext:
    tool = load_manifests().get_tool_by_id("structure.trajectory_import")
    return ToolExecutionContext(
        job_id="job_trajectory",
        project_id="project_trajectory",
        dataset_id="dataset_trajectory",
        tool_id=tool.toolId,
        tool_version=tool.version,
        adapter_version="1.0.0",
        registry_version=load_manifests().version,
        artifact_root=tmp_path / "artifacts",
        tool_call_id="call_trajectory",
        object_store=object_store,
        resource_limits=tool.resourceLimits,
    )


def _request(params: dict | None = None) -> ToolExecutionRequest:
    return ToolExecutionRequest(
        jobId="job_trajectory",
        stepId="step_trajectory",
        toolId="structure.trajectory_import",
        inputRefs=[{"refType": "normalized_object", "ref": "trajectory", "objectType": "Trajectory"}],
        params=params or {},
        artifactTypes=ARTIFACT_TYPES,
    )


def _read(tmp_path: Path, artifacts: list, name: str) -> dict:
    artifact = next(item for item in artifacts if item.name == name)
    return json.loads((tmp_path / "artifacts" / artifact.storageKey).read_text(encoding="utf-8"))


def test_adapter_emits_complete_valid_deterministic_artifact_set(tmp_path: Path) -> None:
    parsed_object = parse_file(FIXTURES / "fixed_lattice_md.extxyz", dataset_id="dataset", file_id="file").objects[0]
    artifacts = TrajectoryImportAdapter().execute(_context(tmp_path, {"trajectory": parsed_object}), _request())
    assert [artifact.type.value for artifact in artifacts] == ARTIFACT_TYPES
    assert [artifact.name for artifact in artifacts] == ["trajectory.json", "trajectory_summary.json", "trajectory_parse_report.json", "trajectory_manifest.json"]
    trajectory = _read(tmp_path, artifacts, "trajectory.json")
    summary = _read(tmp_path, artifacts, "trajectory_summary.json")
    manifest = _read(tmp_path, artifacts, "trajectory_manifest.json")
    report = _read(tmp_path, artifacts, "trajectory_parse_report.json")
    assert validate_trajectory(trajectory).valid
    assert validate_trajectory_summary(summary).valid
    assert validate_trajectory_manifest(manifest).valid
    assert report["schema_version"] == "phase10g.trajectory_parse_report.v1"
    assert all(artifact.metadata.provenance["rendererIncluded"] is False for artifact in artifacts)
    for entry in manifest["artifacts"]:
        stored = next(item for item in artifacts if item.name == entry["name"])
        raw = (tmp_path / "artifacts" / stored.storageKey).read_bytes()
        assert len(raw) == entry["bytes"]
        assert stored.contentHash == entry["sha256"]


def test_adapter_rejects_invalid_params_and_payload_without_partial_artifacts(tmp_path: Path) -> None:
    payload = parse_trajectory_file(FIXTURES / "fixed_lattice_md.extxyz").trajectory
    with pytest.raises(ToolExecutionError) as error:
        TrajectoryImportAdapter().execute(_context(tmp_path, {"trajectory": payload}), _request({"time_unit": "second"}))
    assert error.value.code == "TOOL_PARAM_INVALID"
    assert not (tmp_path / "artifacts").exists()
    invalid = copy.deepcopy(payload)
    invalid["frames"][1]["atom_ids"] = [1, 0]
    with pytest.raises(ToolExecutionError) as error:
        TrajectoryImportAdapter().execute(_context(tmp_path, {"trajectory": invalid}), _request())
    assert error.value.details["errorType"] == "trajectory_contract_invalid"
    assert not (tmp_path / "artifacts").exists()


def _plan() -> dict:
    return {
        "schemaVersion": "0.1",
        "goal": "Normalize the uploaded trajectory into inert canonical artifacts.",
        "datasetId": "dataset_trajectory",
        "profileId": "profile_trajectory",
        "toolRegistryVersion": load_manifests().version,
        "assumptions": ["Input was bounded and normalized by the approved parser."],
        "warnings": ["Trajectory viewer and playback are not included."],
        "steps": [{
            "stepId": "step_trajectory_import",
            "toolId": "structure.trajectory_import",
            "purpose": "Emit validated trajectory artifacts.",
            "reason": "The input object is a canonical trajectory.",
            "inputRefs": [{"refType": "normalized_object", "ref": "trajectory", "objectType": "Trajectory"}],
            "params": {},
            "output": {"artifactTypes": ARTIFACT_TYPES},
            "constraints": {"noExternalNetwork": True},
        }],
        "expectedArtifacts": [
            {"name": "trajectory.json", "type": "trajectory_json", "fromStepId": "step_trajectory_import"},
            {"name": "trajectory_summary.json", "type": "trajectory_summary_json", "fromStepId": "step_trajectory_import"},
            {"name": "trajectory_parse_report.json", "type": "trajectory_report_json", "fromStepId": "step_trajectory_import"},
            {"name": "trajectory_manifest.json", "type": "trajectory_manifest_json", "fromStepId": "step_trajectory_import"},
        ],
    }


def test_plan_validator_and_persisted_runtime_execute_internal_import(tmp_path: Path) -> None:
    registry = load_manifests()
    plan = _plan()
    assert validate_plan(plan, registry=registry).ok
    parsed = parse_file(FIXTURES / "fixed_lattice_md.extxyz", dataset_id="dataset_trajectory", file_id="file").objects[0]
    repos = InMemoryRepositoryBundle.create()
    runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=tmp_path / "runtime")
    created = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Normalize this uploaded trajectory.",
            projectId="project_trajectory",
            datasetId="dataset_trajectory",
            profileId="profile_trajectory",
            enqueue=True,
        ),
        provider=MockLLMProvider(fixed_plan=plan),
        repositories=repos,
        queue_runtime=runtime,
        registry=registry,
    )
    assert created.ok and created.job_id
    result = runtime.handle_job(created.job_id, object_store={"trajectory": parsed})
    artifacts = repos.artifacts.list_for_job(created.job_id)
    calls = repos.tool_calls.list_for_job(created.job_id)
    assert result.status == "completed"
    assert len(calls) == 1 and calls[0]["toolId"] == "structure.trajectory_import"
    assert [item["name"] for item in artifacts] == ["trajectory.json", "trajectory_summary.json", "trajectory_parse_report.json", "trajectory_manifest.json"]


def test_mock_planner_does_not_expose_internal_import_tool() -> None:
    provider = MockLLMProvider()
    profile = DataProfile(
        profileId="profile_trajectory",
        datasetId="dataset_trajectory",
        version="1",
        datasetType="trajectory",
        objects=[{"id": "trajectory", "objectType": "Trajectory"}],
        trajectorySummary={"frames": 3, "atoms": 2},
        createdAt="2026-07-13T00:00:00Z",
    )
    for prompt in ("Import this molecular dynamics trajectory", "Play this trajectory", "Calculate trajectory RDF"):
        response = provider.generate_plan(
            PlannerRequest(
                user_prompt=prompt,
                dataset_id="dataset_trajectory",
                profile_id="profile_trajectory",
                tool_registry_version=load_manifests().version,
            ),
            tools=load_manifests().list_tools(),
            data_profile=profile,
        )
        assert response.raw_json is not None
        assert response.raw_json["steps"][0]["toolId"] != "structure.trajectory_import"
