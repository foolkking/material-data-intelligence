from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from mdi_adapters import create_adapter
from mdi_adapters.context import ToolExecutionContext
from mdi_artifact_core import canonical_trajectory_id
from mdi_llm.grounded_interpretation import (
    ArtifactProjectionInput,
    InterpretationSource,
    project_artifact,
)
from mdi_llm.providers import LLMProviderError, MockLLMProvider, PlannerRequest
from mdi_material_parsers.trajectory import parse_trajectory_file
from mdi_schemas import DataProfile
from mdi_tool_registry import build_artifact_compatibility_matrix, load_manifests
from mdi_adapters.platform_builtin.trajectory_analytics import _minimum_image, _pair_distances


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/phase10g/fixtures/trajectory_v1/fixed_lattice_md.json"
DIFFUSION_FIXTURE = ROOT / "tests/fixtures/trajectory/phase14r_diffusion_unwrapped.extxyz"


def _trajectory() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _context(tmp_path: Path, tool_id: str, store: dict, bindings: dict | None = None) -> ToolExecutionContext:
    return ToolExecutionContext(job_id="job_n4", project_id="project_n4", dataset_id="dataset_n4", tool_id=tool_id, tool_version="0.1.0", adapter_version="0.1.0", registry_version="0.1.0", artifact_root=tmp_path, tool_call_id=f"call_{tool_id.replace('.', '_')}", plan_id="plan_n4", plan_version="0.2", object_store=store, artifact_bindings=bindings or {})


def _execute(tmp_path: Path, tool_id: str, payload: dict, params: dict, bindings: dict | None = None):
    adapter = create_adapter({"trajectory.rdf": "TrajectoryRdfAdapter", "trajectory.msd": "TrajectoryMsdAdapter", "trajectory.diffusion": "TrajectoryDiffusionAdapter"}[tool_id])
    return adapter.execute(_context(tmp_path, tool_id, {"input": payload}, bindings), {"toolId": tool_id, "inputRefs": [{"ref": "input"}], "params": params, "artifactTypes": ["table_json"]})


def _payload(root: Path, artifact) -> dict:
    return json.loads((root / artifact.storageKey).read_text(encoding="utf-8"))


def test_registry_and_exact_msd_dependency() -> None:
    registry = load_manifests()
    assert len(registry.tools) == 62
    for tool_id in ("trajectory.rdf", "trajectory.msd", "trajectory.diffusion"):
        tool = registry.get_tool_by_id(tool_id)
        assert tool.version == "0.1.0"
        assert tool.resourceLimits["maxFrames"] == 200
        assert tool.resourceLimits["maxAtoms"] == 5000
        assert tool.resourceLimits["maxRdfPairs"] == 2_000_000
    matrix = build_artifact_compatibility_matrix(registry, selected_tool_ids=["trajectory.diffusion", "trajectory.msd"])
    pair = next(item for item in matrix.pairs if item.producerToolId == "trajectory.msd")
    assert pair.compatible and pair.artifactContractVersion == "phase10n4.trajectory_msd.v1"


def test_mock_planner_routes_n4_and_requires_explicit_diffusion_window() -> None:
    registry = load_manifests()
    profile = DataProfile(profileId="profile_n4", datasetId="dataset_n4", version="2.3", datasetType="trajectory", objects=[{"id": "trajectory", "objectType": "Trajectory"}], trajectorySummary={"frames": 20, "atoms": 2}, createdAt="2026-08-09T00:00:00Z")
    response = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt="estimate Li diffusion from 2 ps to 8 ps", dataset_id=profile.datasetId, profile_id=profile.profileId, tool_registry_version=registry.version),
        tools=registry.list_mvp_tools(),
        data_profile=profile,
    )
    assert [step["toolId"] for step in response.raw_json["steps"]] == ["trajectory.msd", "trajectory.diffusion"]
    assert response.raw_json["steps"][1]["params"]["fit_start_time_ps"] == 2.0
    with pytest.raises(LLMProviderError, match="explicit fit"):
        MockLLMProvider().generate_plan(
            PlannerRequest(user_prompt="estimate Li diffusion", dataset_id=profile.datasetId, profile_id=profile.profileId, tool_registry_version=registry.version),
            tools=registry.list_mvp_tools(),
            data_profile=profile,
        )


def test_whole_and_species_pair_rdf(tmp_path: Path) -> None:
    result = _payload(tmp_path, _execute(tmp_path, "trajectory.rdf", _trajectory(), {"r_max_angstrom": 2.0, "bin_count": 20, "species_a": "Si", "species_b": "Si"})[0])
    assert result["schema_version"] == "phase10n4.trajectory_rdf.v1"
    assert {key: result["speciesPair"][key] for key in ("speciesA", "speciesB", "ordered")} == {"speciesA": "Si", "speciesB": "Si", "ordered": False}
    assert result["speciesPair"]["pairId"].startswith("rdf-pair:")
    assert result["coverage"]["includedFrames"] == 4
    assert len(result["gR"]) == 20
    assert result["runtimeDiagnostics"]["staticRdfAuthorityReused"] is False


def test_boundary_crossing_msd_uses_unwrapped_positions(tmp_path: Path) -> None:
    trajectory = _trajectory()
    for index, x in enumerate((0.90, 0.95, 0.00, 0.05)):
        trajectory["frames"][index]["positions"][0][0] = x
        trajectory["frames"][index]["positions"][1][0] = (x + 0.25) % 1.0
    trajectory["trajectory_id"] = canonical_trajectory_id(trajectory)
    result = _payload(tmp_path, _execute(tmp_path, "trajectory.msd", trajectory, {"max_lag_count": 3})[0])
    assert result["unwrapping"]["serverSide"] is True
    assert result["unwrapping"]["wrappedCoordinateDirectUse"] is False
    assert result["totalMsdAngstrom2"] == pytest.approx([0.0625, 0.25, 0.5625])
    assert result["originCounts"] == [3, 2, 1]


def test_triclinic_rdf_uses_ase_geometric_minimum_image() -> None:
    cell = [[4.0, 0.0, 0.0], [3.2, 4.0, 0.0], [0.0, 0.0, 5.0]]
    delta = [-5.04, -2.8, 0.0]  # fractional delta [-0.7, -0.7, 0]
    result = _minimum_image(delta, cell, (True, True, True))
    assert result == pytest.approx([-1.84, 1.2, 0.0])


def test_rdf_batch_pair_distances_match_scalar_minimum_image() -> None:
    cell = np.asarray([[4.0, 0.0, 0.0], [3.2, 4.0, 0.0], [0.0, 0.0, 5.0]])
    deltas = np.asarray([[-5.04, -2.8, 0.0], [5.04, 2.8, 0.0], [1.0, 0.5, 2.0]])
    expected = np.asarray([np.linalg.norm(_minimum_image(delta, cell, (True, True, True))) for delta in deltas])
    assert _pair_distances(deltas, cell, (True, True, True)) == pytest.approx(expected)


def test_msd_triclinic_partial_pbc_and_ambiguous_steps(tmp_path: Path) -> None:
    trajectory = _trajectory()
    trajectory["fixed_lattice"] = [[4.0, 0.0, 0.0], [1.0, 4.0, 0.0], [0.0, 0.0, 5.0]]
    trajectory["periodic_boundary"] = [True, False, True]
    for index, (x, y) in enumerate(((0.90, 0.10), (0.95, 0.20), (0.00, 0.30), (0.05, 0.40))):
        trajectory["frames"][index]["positions"][0][:2] = [x, y]
        trajectory["frames"][index]["positions"][1][:2] = [(x + 0.25) % 1.0, y + 0.20]
    trajectory["trajectory_id"] = canonical_trajectory_id(trajectory)
    result = _payload(tmp_path, _execute(tmp_path, "trajectory.msd", trajectory, {"max_lag_count": 1})[0])
    assert result["unwrapping"]["pbcAxes"] == [True, False, True]
    assert result["directionalMsdAngstrom2"]["y"][0] > 0.0

    trajectory["frames"][1]["positions"][0][0] = 0.40
    trajectory["trajectory_id"] = canonical_trajectory_id(trajectory)
    with pytest.raises(Exception, match="not uniquely bounded"):
        _execute(tmp_path / "ambiguous", "trajectory.msd", trajectory, {"max_lag_count": 1})


def _msd_payload(values: list[float]) -> dict:
    return {
        "artifactType": "trajectory.msd", "schema_version": "phase10n4.trajectory_msd.v1",
        "trajectory": {"resourceId": "sha256:" + "1" * 64, "trajectoryHash": "sha256:" + "1" * 64, "contractVersion": "phase10g.trajectory.v1", "frameCount": 20, "atomCount": 4},
        "parameterHash": "2" * 64, "lagTimesPs": [float(i) for i in range(1, len(values) + 1)],
        "totalMsdAngstrom2": values, "directionalMsdAngstrom2": {"x": [value / 3 for value in values], "y": [value / 3 for value in values], "z": [value / 3 for value in values]},
        "originCounts": list(range(20, 20 - len(values), -1)),
    }


def test_diffusion_accepts_linear_msd_and_rejects_ballistic(tmp_path: Path) -> None:
    params = {"fit_start_time_ps": 1.0, "fit_end_time_ps": 8.0, "minimum_fit_points": 5, "minimum_fit_duration_ps": 1.0, "minimum_r_squared": 0.9}
    binding = {"input": {"artifactId": "artifact_msd", "checksum": "3" * 64}}
    linear_root = tmp_path / "linear"
    linear = _payload(linear_root, _execute(linear_root, "trajectory.diffusion", _msd_payload([0.6 * i for i in range(1, 9)]), params, binding)[0])
    assert linear["regimeDiagnostic"]["status"] == "DIFFUSIVE_WINDOW_ACCEPTED"
    assert linear["diffusionEstimate"]["value"] == pytest.approx(0.1)
    ballistic_root = tmp_path / "ballistic"
    ballistic = _payload(ballistic_root, _execute(ballistic_root, "trajectory.diffusion", _msd_payload([0.06 * i * i for i in range(1, 9)]), params, binding)[0])
    assert ballistic["regimeDiagnostic"]["status"] == "BALLISTIC_LIKE_WINDOW"
    assert ballistic["diffusionEstimate"]["available"] is False


def test_real_unwrapped_extxyz_closes_msd_to_diffusion_dependency(tmp_path: Path) -> None:
    trajectory = parse_trajectory_file(DIFFUSION_FIXTURE).trajectory
    assert trajectory["position_wrapping"] == "unwrapped"
    assert trajectory["time"]["unit"] == "femtosecond"
    assert trajectory["frames"][-1]["time"] == 11_500.0
    assert len(trajectory["frames"]) == 24

    msd_root = tmp_path / "msd"
    msd_artifact = _execute(
        msd_root,
        "trajectory.msd",
        trajectory,
        {"max_lag_count": 16, "origin_stride": 1, "max_origins_per_lag": 4096},
    )[0]
    msd = _payload(msd_root, msd_artifact)

    diffusion_root = tmp_path / "diffusion"
    diffusion = _payload(
        diffusion_root,
        _execute(
            diffusion_root,
            "trajectory.diffusion",
            msd,
            {
                "fit_start_time_ps": 1.0,
                "fit_end_time_ps": 6.0,
                "direction": "total",
                "minimum_fit_points": 5,
                "minimum_fit_duration_ps": 1.0,
                "minimum_origin_coverage": 0.2,
                "minimum_r_squared": 0.9,
                "alpha_min": 0.8,
                "alpha_max": 1.2,
            },
            {"input": {"artifactId": msd_artifact.id, "checksum": msd_artifact.contentHash}},
        )[0],
    )

    assert diffusion["sourceMsd"]["artifactId"] == msd_artifact.id
    assert diffusion["regimeDiagnostic"]["status"] == "DIFFUSIVE_WINDOW_ACCEPTED"
    assert diffusion["diffusionEstimate"] == {
        "available": True,
        "value": pytest.approx(0.038618, abs=1e-6),
        "unit": "angstrom^2/picosecond",
        "qualifiedOverSelectedWindow": True,
    }
    assert diffusion["fit"]["rSquared"] >= 0.9
    assert diffusion["regimeDiagnostic"]["alpha"] == pytest.approx(0.924031, abs=1e-5)
    assert diffusion["runtimeDiagnostics"] == {
        "rawTrajectoryReads": False,
        "msdRecomputation": False,
        "frontendFit": False,
        "automaticWindowOptimization": False,
    }


def test_diffusion_projects_the_exact_authoritative_fit_window(tmp_path: Path) -> None:
    trajectory = parse_trajectory_file(DIFFUSION_FIXTURE).trajectory
    msd_root = tmp_path / "msd"
    msd_artifact = _execute(
        msd_root,
        "trajectory.msd",
        trajectory,
        {"max_lag_count": 16, "origin_stride": 1, "max_origins_per_lag": 4096},
    )[0]
    msd = _payload(msd_root, msd_artifact)
    diffusion_root = tmp_path / "diffusion"
    diffusion_artifact = _execute(
        diffusion_root,
        "trajectory.diffusion",
        msd,
        {
            "fit_start_time_ps": 1.0,
            "fit_end_time_ps": 6.0,
            "direction": "total",
            "minimum_fit_points": 5,
            "minimum_fit_duration_ps": 1.0,
            "minimum_origin_coverage": 0.2,
            "minimum_r_squared": 0.9,
            "alpha_min": 0.8,
            "alpha_max": 1.2,
        },
        {"input": {"artifactId": msd_artifact.id, "checksum": msd_artifact.contentHash}},
    )[0]
    diffusion = _payload(diffusion_root, diffusion_artifact)
    raw = json.dumps(
        diffusion,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
    checksum = hashlib.sha256(raw).hexdigest()
    source = InterpretationSource(
        project_id="project_n4",
        dataset_id="dataset_n4",
        dataset_version="2.0",
        profile_id="profile_n4",
        profile_semantic_hash="p" * 64,
        intent_id="intent_n4",
        intent_hash="i" * 64,
        resolution_id="resolution_n4",
        resolution_hash="r" * 64,
        decision_id="decision_n4",
        decision_hash="d" * 64,
        plan_id="plan_n4",
        plan_hash="a" * 64,
        plan_schema_version="0.2",
        graph_hash=None,
        job_id="job_n4",
        job_status="completed",
        execution_outcome="ALL_SUCCEEDED",
        failed_step_count=0,
        blocked_step_count=0,
    )
    candidate = ArtifactProjectionInput(
        artifact={
            "id": diffusion_artifact.id,
            "artifactId": diffusion_artifact.id,
            "projectId": "project_n4",
            "datasetId": "dataset_n4",
            "jobId": "job_n4",
            "toolCallId": "call_trajectory_diffusion",
            "type": "table_json",
            "version": "1",
            "sizeBytes": len(raw),
            "sha256": checksum,
            "contentHash": checksum,
        },
        payload=diffusion,
        tool_call={
            "id": "call_trajectory_diffusion",
            "toolId": "trajectory.diffusion",
            "stepId": "step_diffusion",
            "status": "completed",
        },
        lineage={"producerToolVersion": "0.1.0"},
        raw_checksum=checksum,
        raw_size_bytes=len(raw),
    )

    roles = {item.semanticRole: item for item in project_artifact(source, candidate)}
    assert roles["trajectory.diffusion.fit_start"].displayValue == "1 picosecond"
    assert roles["trajectory.diffusion.fit_end"].displayValue == "6 picosecond"
    assert roles["trajectory.diffusion.fit_points"].displayValue == "11"
    assert roles["trajectory.diffusion.estimate"].displayValue == (
        "0.0386181 angstrom^2/picosecond"
    )
    assert roles["trajectory.diffusion.status"].displayValue == (
        "DIFFUSIVE_WINDOW_ACCEPTED"
    )


def test_diffusion_requires_explicit_window_and_persisted_checksum(tmp_path: Path) -> None:
    with pytest.raises(Exception, match="explicit diffusion fit window"):
        _execute(tmp_path, "trajectory.diffusion", _msd_payload([1, 2, 3]), {}, {"input": {"artifactId": "a", "checksum": "3" * 64}})
    with pytest.raises(Exception, match="checksum"):
        _execute(tmp_path, "trajectory.diffusion", _msd_payload([1, 2, 3]), {"fit_start_time_ps": 1, "fit_end_time_ps": 3})
