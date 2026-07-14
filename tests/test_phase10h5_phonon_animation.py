from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from mdi_adapters import PhononAnimationAdapter, ToolExecutionContext, ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import (
    PHONON_ANIMATION_SCHEMA_VERSION,
    PhononAnimationContractError,
    animation_displacements,
    build_phonon_eigenvector,
    build_phonon_eigenvector_set,
    build_phonon_mode_ref,
    build_phonon_animation,
    commensurate_diagonal_supercell,
    validate_phonon_animation,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs" / "phase10h" / "fixtures" / "phonon_eigenvector_v1" / "valid_bundle.json"
ARTIFACT_TYPES = ["phonon_animation_json", "phonon_animation_summary_json", "phonon_animation_manifest_json", "recipe_json"]


def _bundle() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _structure() -> dict:
    return {
        "structure_identity": "a" * 64,
        "formula": "Si2",
        "lattice": [[5.43, 0.0, 0.0], [0.0, 5.43, 0.0], [0.0, 0.0, 5.43]],
        "sites": [
            {"site_index": 0, "species": "Si", "fractional": [0.0, 0.0, 0.0], "cartesian": [0.0, 0.0, 0.0]},
            {"site_index": 1, "species": "Si", "fractional": [0.25, 0.25, 0.25], "cartesian": [1.3575, 1.3575, 1.3575]},
        ],
        "bonds": [],
    }


def _params(mode_index: int = 0, **updates: object) -> dict:
    params = {"mode_id": _bundle()["set"]["modes"][mode_index]["mode"]["mode_id"]}
    params.update(updates)
    return params


def _package(mode_index: int = 0, **updates: object) -> dict:
    bundle = _bundle()
    return build_phonon_animation(_structure(), bundle["band"], bundle["set"], _params(mode_index, **updates))


def test_gamma_package_is_declarative_paused_and_valid() -> None:
    package = _package()
    assert package["schema_version"] == PHONON_ANIMATION_SCHEMA_VERSION
    assert package["supercell"] == {"mode": "auto", "repeat": [1, 1, 1], "displayed_atom_count": 2, "commensurate": True, "renderer_local": True}
    assert package["playback"]["default_state"] == "paused"
    assert package["provenance"]["frames_persisted"] is False
    assert validate_phonon_animation(package).valid


def test_non_gamma_auto_supercell_and_replica_phase() -> None:
    package = _package(1)
    assert package["supercell"]["repeat"] == [2, 1, 1]
    origin = animation_displacements(package, 0.0, [0, 0, 0])
    replica = animation_displacements(package, 0.0, [1, 0, 0])
    assert replica[0][0] == pytest.approx(-origin[0][0])


def test_phase_periodicity_and_quarter_cycle() -> None:
    package = _package()
    zero = animation_displacements(package, 0.0, [0, 0, 0])
    full = animation_displacements(package, 2 * math.pi, [0, 0, 0])
    assert [item for vector in full for item in vector] == pytest.approx([item for vector in zero for item in vector])
    quarter = animation_displacements(package, math.pi / 2, [0, 0, 0])
    assert max(abs(item) for vector in quarter for item in vector) == pytest.approx(0.0, abs=1e-12)


@pytest.mark.parametrize(
    ("qpoint", "expected"),
    [([0, 0, 0], [1, 1, 1]), ([0.5, 0, 0], [2, 1, 1]), ([1 / 3, 0.5, 0], [3, 2, 1])],
)
def test_bounded_commensurate_solver(qpoint: list[float], expected: list[int]) -> None:
    assert commensurate_diagonal_supercell(qpoint) == expected


def test_noncommensurate_and_manual_mismatch_are_typed() -> None:
    with pytest.raises(PhononAnimationContractError, match="bounded diagonal"):
        commensurate_diagonal_supercell([0.2, 0, 0])
    with pytest.raises(PhononAnimationContractError) as exc:
        commensurate_diagonal_supercell([0.5, 0, 0], [1, 1, 1])
    assert exc.value.code == "PHONON_ANIMATION_NONCOMMENSURATE"
    forged = _package(1)
    forged["supercell"]["displayed_atom_count"] = 999
    assert "PHONON_ANIMATION_SUPERCELL_INVALID" in validate_phonon_animation(forged).errors


def test_structure_identity_and_atom_order_must_match() -> None:
    bundle = _bundle()
    bad_identity = _structure()
    bad_identity["structure_identity"] = "f" * 64
    with pytest.raises(PhononAnimationContractError) as exc:
        build_phonon_animation(bad_identity, bundle["band"], bundle["set"], _params())
    assert exc.value.code == "PHONON_ANIMATION_STRUCTURE_MISMATCH"
    bad_order = _structure()
    bad_order["sites"][1]["species"] = "Ge"
    with pytest.raises(PhononAnimationContractError) as exc:
        build_phonon_animation(bad_order, bundle["band"], bundle["set"], _params())
    assert exc.value.code == "PHONON_ANIMATION_ATOM_ORDER_MISMATCH"


def test_unknown_params_and_executable_content_are_rejected() -> None:
    with pytest.raises(PhononAnimationContractError) as exc:
        _package(callback="alert(1)")
    assert exc.value.code == "PHONON_ANIMATION_PARAM_INVALID"
    package = _package()
    package["structure"]["formula"] = "<script>alert(1)</script>"
    result = validate_phonon_animation(package)
    assert "PHONON_ANIMATION_EXTERNAL_CONTENT_FORBIDDEN" in result.errors


def test_imaginary_and_degenerate_warnings_are_stable() -> None:
    bundle = _bundle()
    bundle["band"]["branches"][3]["frequencies"][0] = -4.0
    mode_ref = build_phonon_mode_ref(bundle["band"], artifact_id="band-artifact", qpoint_index=0, branch_index=3)
    eigenvector = build_phonon_eigenvector(bundle["band"], mode_ref, [[1 + 0j, 0j, 0j], [-1 + 0j, 0j, 0j]], [28.085, 28.085])
    eigenvector_set = build_phonon_eigenvector_set([eigenvector])
    package = build_phonon_animation(_structure(), bundle["band"], eigenvector_set, {"mode_id": mode_ref["mode_id"]})
    assert package["warnings"] == ["PHONON_ANIMATION_IMAGINARY_MODE_STATIC_DIRECTION", "PHONON_ANIMATION_DEGENERATE_BASIS_ARBITRARY"]


def test_adapter_exports_four_inert_artifacts(tmp_path: Path) -> None:
    bundle = _bundle()
    registry = load_manifests()
    tool = registry.get_tool_by_id("phonon.animation")
    context = ToolExecutionContext(
        job_id="job_h5", project_id="project_h5", dataset_id="dataset_h5", tool_id=tool.toolId,
        tool_version=tool.version, adapter_version="0.1.0", registry_version=registry.version,
        artifact_root=tmp_path / "artifacts", tool_call_id="call_h5",
        object_store={"structure": _structure(), "band": bundle["band"], "eigenvectors": bundle["set"]},
        resource_limits=tool.resourceLimits,
    )
    request = ToolExecutionRequest(
        jobId="job_h5", stepId="step_001", toolId="phonon.animation",
        inputRefs=[
            {"refType": "normalized_object", "ref": "structure", "fieldRole": "structure", "objectType": "Structure"},
            {"refType": "artifact", "ref": "band", "fieldRole": "band", "objectType": "PhononBand"},
            {"refType": "artifact", "ref": "eigenvectors", "fieldRole": "eigenvectors", "objectType": "PhononEigenvector"},
        ],
        params=_params(), artifactTypes=ARTIFACT_TYPES,
    )
    artifacts = PhononAnimationAdapter().execute(context, request)
    assert [artifact.name for artifact in artifacts] == ["phonon_animation.json", "phonon_animation_summary.json", "phonon_animation_manifest.json", "recipe.json"]
    package = json.loads((tmp_path / "artifacts" / artifacts[0].storageKey).read_text(encoding="utf-8"))
    assert validate_phonon_animation(package).valid
    assert package["security"]["external_assets"] == []


def test_adapter_rejects_role_confusion_before_output(tmp_path: Path) -> None:
    bundle = _bundle()
    registry = load_manifests()
    tool = registry.get_tool_by_id("phonon.animation")
    context = ToolExecutionContext(job_id="job", project_id="project", dataset_id="dataset", tool_id=tool.toolId, tool_version=tool.version, adapter_version="0.1.0", registry_version=registry.version, artifact_root=tmp_path / "artifacts", object_store={"structure": _structure(), "band": bundle["band"], "eigenvectors": bundle["set"]})
    request = {"jobId": "job", "stepId": "step", "toolId": "phonon.animation", "inputRefs": [{"refType": "artifact", "ref": "structure", "fieldRole": "band", "objectType": "Structure"}, {"refType": "artifact", "ref": "band", "fieldRole": "structure", "objectType": "PhononBand"}, {"refType": "artifact", "ref": "eigenvectors", "fieldRole": "eigenvectors", "objectType": "PhononEigenvector"}], "params": _params(), "artifactTypes": ARTIFACT_TYPES}
    with pytest.raises(ToolExecutionError) as exc:
        PhononAnimationAdapter().execute(context, request)
    assert exc.value.details["errorType"] == "PHONON_ANIMATION_INPUT_BINDING_INVALID"
    assert not (tmp_path / "artifacts").exists()


def test_registry_and_plan_validator_require_canonical_mode() -> None:
    registry = load_manifests()
    tool = registry.get_tool_by_id("phonon.animation")
    assert tool.adapter == "PhononAnimationAdapter"
    assert tool.paramsSchema["additionalProperties"] is False
    assert tool.resourceLimits["maxDisplayedAtoms"] == 768
    plan = {
        "schemaVersion": "0.1", "goal": "Animate the selected phonon mode", "datasetId": "dataset", "profileId": "profile", "toolRegistryVersion": registry.version,
        "steps": [{"stepId": "step_001", "toolId": "phonon.animation", "purpose": "Animate validated eigenmode", "reason": "Requested", "inputRefs": [{"refType": "normalized_object", "ref": "structure", "fieldRole": "structure", "objectType": "Structure"}, {"refType": "artifact", "ref": "band", "fieldRole": "band", "objectType": "PhononBand"}, {"refType": "artifact", "ref": "eigenvectors", "fieldRole": "eigenvectors", "objectType": "PhononEigenvector"}], "params": _params(), "output": {"artifactTypes": ARTIFACT_TYPES}}],
        "expectedArtifacts": [{"name": "phonon_animation.json", "type": "phonon_animation_json", "fromStepId": "step_001"}],
        "assumptions": [], "warnings": [],
    }
    assert validate_plan(plan, registry=registry).ok
    plan["steps"][0]["params"]["shader"] = "evil"
    assert not validate_plan(plan, registry=registry).ok


def _profile(include_mode: bool = True) -> DataProfile:
    mode_id = _params()["mode_id"]
    objects = [
        {"id": "structure", "objectType": "Structure"},
        {"id": "band", "objectType": "PhononBand"},
        {"id": "eigenvectors", "objectType": "PhononEigenvector", **({"modeId": mode_id} if include_mode else {})},
    ]
    return DataProfile(profileId="profile_h5", datasetId="dataset_h5", version="1", datasetType="phonon", objects=objects, createdAt="2026-07-14T00:00:00Z")


def _planned(prompt: str, include_mode: bool = True) -> dict:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(PlannerRequest(prompt, "dataset_h5", "profile_h5", registry.version), tools=registry.list_mvp_tools(), data_profile=_profile(include_mode))
    assert response.raw_json is not None
    return response.raw_json


@pytest.mark.parametrize("prompt", ["Animate the selected phonon mode", "Visualize this phonon eigenmode", "播放这个声子模式", "动画展示这个虚频模式"])
def test_planner_routes_explicit_animation_intent(prompt: str) -> None:
    plan = _planned(prompt)
    assert plan["steps"][0]["toolId"] == "phonon.animation"
    assert [ref["fieldRole"] for ref in plan["steps"][0]["inputRefs"]] == ["structure", "band", "eigenvectors"]
    assert validate_plan(plan, registry=load_manifests()).ok


@pytest.mark.parametrize("prompt", ["Run phonopy and calculate phonon modes", "Play this MD trajectory", "Compute phonon heat capacity", "Generate a Brillouin zone", "Export this mode as MP4"])
def test_planner_does_not_confuse_unsupported_domains(prompt: str) -> None:
    assert _planned(prompt)["steps"][0]["toolId"] != "phonon.animation"


def test_planner_requires_explicit_canonical_mode_identity() -> None:
    assert _planned("Animate the selected phonon mode", include_mode=False)["steps"][0]["toolId"] != "phonon.animation"


def test_queue_runtime_persists_deterministic_animation_artifacts(tmp_path: Path) -> None:
    registry = load_manifests()
    plan = _planned("Animate the selected phonon mode")
    bundle = _bundle()
    outputs: list[dict[str, object]] = []
    for suffix in ("first", "second"):
        repositories = InMemoryRepositoryBundle.create()
        root = tmp_path / suffix
        runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=root)
        created = planner_jobs(PlannerJobsRequest(userPrompt="Animate the selected phonon mode", projectId="project_h5", datasetId="dataset_h5", profileId="profile_h5", enqueue=True), provider=MockLLMProvider(fixed_plan=plan), repositories=repositories, queue_runtime=runtime, registry=registry)
        assert created.ok and created.job_id and created.enqueued
        result = runtime.handle_job(created.job_id, object_store={"structure": _structure(), "band": bundle["band"], "eigenvectors": bundle["set"]})
        assert result.status == "completed"
        records = repositories.artifacts.list_for_job(created.job_id)
        assert [record["name"] for record in records] == ["phonon_animation.json", "phonon_animation_summary.json", "phonon_animation_manifest.json", "recipe.json"]
        assert all(record["metadata"]["provenance"]["toolId"] == "phonon.animation" for record in records)
        outputs.append({record["name"]: json.loads((root / record["storageKey"]).read_text(encoding="utf-8")) for record in records})
    assert outputs[0] == outputs[1]
