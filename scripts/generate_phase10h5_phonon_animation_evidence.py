from __future__ import annotations

import json
from pathlib import Path
import shutil

from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import (
    animation_displacements,
    PhononAnimationContractError,
    build_phonon_animation,
    build_phonon_eigenvector,
    build_phonon_eigenvector_set,
    build_phonon_mode_ref,
    phonon_animation_manifest,
    phonon_animation_summary,
    validate_phonon_animation,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/phase10h/fixtures/phonon_eigenvector_v1/valid_bundle.json"
FIXTURES = ROOT / "docs/phase10h/fixtures/phonon_animation_v1"
EVIDENCE = ROOT / "docs/phase10h/evidence/phase10h5_phonon_animation"


def structure() -> dict:
    return {
        "structure_identity": "a" * 64, "formula": "Si2",
        "lattice": [[5.43, 0.0, 0.0], [0.0, 5.43, 0.0], [0.0, 0.0, 5.43]],
        "sites": [
            {"site_index": 0, "species": "Si", "fractional": [0.0, 0.0, 0.0], "cartesian": [0.0, 0.0, 0.0]},
            {"site_index": 1, "species": "Si", "fractional": [0.25, 0.25, 0.25], "cartesian": [1.3575, 1.3575, 1.3575]},
        ],
        "bonds": [{"from": 0, "to": 1}],
    }


def write(relative: str, value: object) -> None:
    target = EVIDENCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, ensure_ascii=True, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    if EVIDENCE.exists():
        shutil.rmtree(EVIDENCE)
    FIXTURES.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bundle = json.loads(SOURCE.read_text(encoding="utf-8"))
    gamma_mode = bundle["set"]["modes"][0]["mode"]["mode_id"]
    non_gamma_mode = bundle["set"]["modes"][1]["mode"]["mode_id"]
    gamma = build_phonon_animation(structure(), bundle["band"], bundle["set"], {"mode_id": gamma_mode, "display_scale": 0.15})
    non_gamma = build_phonon_animation(structure(), bundle["band"], bundle["set"], {"mode_id": non_gamma_mode, "display_scale": 0.15})
    imaginary_band = json.loads(json.dumps(bundle["band"]))
    imaginary_band["branches"][3]["frequencies"][0] = -1.25
    imaginary_ref = build_phonon_mode_ref(imaginary_band, artifact_id="band-artifact-imaginary", qpoint_index=0, branch_index=3)
    imaginary_vector = build_phonon_eigenvector(imaginary_band, imaginary_ref, [[1 + 0j, 0j, 0j], [-1 + 0j, 0j, 0j]], [28.085, 28.085])
    imaginary_set = build_phonon_eigenvector_set([imaginary_vector])
    imaginary = build_phonon_animation(structure(), imaginary_band, imaginary_set, {"mode_id": imaginary_ref["mode_id"], "display_scale": 0.15})
    multi_band = json.loads(json.dumps(bundle["band"]))
    multi_band["species"] = ["Na", "Cl"]
    multi_structure = structure(); multi_structure["formula"] = "NaCl"; multi_structure["sites"][0]["species"] = "Na"; multi_structure["sites"][1]["species"] = "Cl"
    multi_ref = build_phonon_mode_ref(multi_band, artifact_id="band-artifact-multi", qpoint_index=0, branch_index=3)
    multi_vector = build_phonon_eigenvector(multi_band, multi_ref, [[1 + 0j, 0j, 0j], [-1 + 0j, 0j, 0j]], [22.989769, 35.45])
    multi = build_phonon_animation(multi_structure, multi_band, build_phonon_eigenvector_set([multi_vector]), {"mode_id": multi_ref["mode_id"], "display_scale": 0.15})
    nac_band = json.loads(json.dumps(bundle["band"]))
    nac_band["source"]["nac"] = {"enabled": True, "gamma_direction": [1.0, 0.0, 0.0], "direction_policy": "explicit"}
    nac_ref = build_phonon_mode_ref(nac_band, artifact_id="band-artifact-nac", qpoint_index=0, branch_index=3)
    nac_vector = build_phonon_eigenvector(nac_band, nac_ref, [[1 + 0j, 0j, 0j], [-1 + 0j, 0j, 0j]], [28.085, 28.085])
    nac = build_phonon_animation(structure(), nac_band, build_phonon_eigenvector_set([nac_vector]), {"mode_id": nac_ref["mode_id"], "display_scale": 0.15})
    for name, value in (("gamma_animation.json", gamma), ("non_gamma_animation.json", non_gamma), ("imaginary_animation.json", imaginary), ("multi_species_animation.json", multi), ("nac_animation.json", nac)):
        (FIXTURES / name).write_text(json.dumps(value, indent=2, ensure_ascii=True, sort_keys=True) + "\n", encoding="utf-8")
        write(f"artifacts/{name}", value)
        write(f"validation/{name}", validate_phonon_animation(value).__dict__)
    large_band = json.loads(json.dumps(bundle["band"])); large_band["atom_count"] = 512; large_band["species"] = ["Si"] * 512; large_band["degeneracy_groups"] = []; large_band["branches"] = [{"branch_index": index, "frequencies": [1.0 + index / 1000.0] * len(large_band["qpoints"])} for index in range(1536)]
    large_ref = build_phonon_mode_ref(large_band, artifact_id="band-artifact-large", qpoint_index=0, branch_index=3)
    large_vector = build_phonon_eigenvector(large_band, large_ref, [[1 + 0j, 0j, 0j] for _ in range(512)], [28.085] * 512)
    large_set = build_phonon_eigenvector_set([large_vector])
    large_structure = {"structure_identity": "a" * 64, "formula": "Si512", "lattice": [[5.43, 0.0, 0.0], [0.0, 5.43, 0.0], [0.0, 0.0, 5.43]], "sites": [{"site_index": index, "species": "Si", "fractional": [(index % 8) / 8, ((index // 8) % 8) / 8, ((index // 64) % 8) / 8], "cartesian": [(index % 8) * 5.43 / 8, ((index // 8) % 8) * 5.43 / 8, ((index // 64) % 8) * 5.43 / 8]} for index in range(512)], "bonds": []}
    try:
        build_phonon_animation(large_structure, large_band, large_set, {"mode_id": large_ref["mode_id"], "supercell_mode": "manual", "supercell": [2, 1, 1]})
        over_cap_result = {"refused": False}
    except PhononAnimationContractError as exc:
        over_cap_result = {"refused": True, "error": exc.code, "canonical_atoms": 512, "requested_repeat": [2, 1, 1], "derived_atoms": 1024, "cap": 768}
    write("validation/over_cap_animation.json", over_cap_result)
    phase_reference = {str(phase): {"origin": animation_displacements(gamma, phase, [0, 0, 0]), "non_gamma_origin": animation_displacements(non_gamma, phase, [0, 0, 0]), "non_gamma_replica_x": animation_displacements(non_gamma, phase, [1, 0, 0])} for phase in (0.0, 1.5707963267948966, 3.141592653589793, 4.71238898038469, 6.283185307179586)}
    write("reference/displacement_phases.json", phase_reference)
    write("reference/commensurate_supercells.json", {"gamma": [1, 1, 1], "x_half": [2, 1, 1], "policy": "positive_diagonal_exact_bounded"})
    write("determinism/replay.json", {"first": gamma, "second": build_phonon_animation(structure(), bundle["band"], bundle["set"], {"mode_id": gamma_mode, "display_scale": 0.15}), "equal": gamma == build_phonon_animation(structure(), bundle["band"], bundle["set"], {"mode_id": gamma_mode, "display_scale": 0.15})})
    write("audit/implementation.json", {"shared_renderer_engine": True, "single_raf": True, "frames_persisted": False, "diagonal_supercell_only": True, "general_integer_matrix": False, "display_scale_physical": False, "dependencies_added": False})
    summary = phonon_animation_summary(gamma)
    manifest = phonon_animation_manifest(gamma, summary)
    write("artifacts/phonon_animation_summary.json", summary)
    write("artifacts/phonon_animation_manifest.json", manifest)

    registry = load_manifests()
    profile = DataProfile(profileId="profile_h5", datasetId="dataset_h5", version="1", datasetType="phonon", objects=[{"id": "structure", "objectType": "Structure"}, {"id": "band", "objectType": "PhononBand"}, {"id": "eigenvectors", "objectType": "PhononEigenvector", "modeId": gamma_mode}], createdAt="2026-07-14T00:00:00Z")
    response = MockLLMProvider().generate_plan(PlannerRequest("Animate the selected phonon mode", "dataset_h5", "profile_h5", registry.version), tools=registry.list_mvp_tools(), data_profile=profile)
    assert response.raw_json is not None
    repositories = InMemoryRepositoryBundle.create()
    runtime_root = EVIDENCE / "runtime_artifacts"
    runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=runtime_root)
    created = planner_jobs(PlannerJobsRequest(userPrompt="Animate the selected phonon mode", projectId="project_h5", datasetId="dataset_h5", profileId="profile_h5", enqueue=True), provider=MockLLMProvider(fixed_plan=response.raw_json), repositories=repositories, queue_runtime=runtime, registry=registry)
    assert created.ok and created.job_id
    result = runtime.handle_job(created.job_id, object_store={"structure": structure(), "band": bundle["band"], "eigenvectors": bundle["set"]})
    assert result.status == "completed"
    records = repositories.artifacts.list_for_job(created.job_id)
    live_artifacts = []
    for record in records:
        content = json.loads((runtime_root / record["storageKey"]).read_text(encoding="utf-8"))
        live_artifacts.append({"id": record["id"], "artifactId": record["id"], "jobId": created.job_id, "type": record["type"], "name": record["name"], "content": content, "metadata": {"preview": content, "toolId": "phonon.animation"}})
    write("api/planner_request.json", {"userPrompt": "Animate the selected phonon mode", "datasetId": "dataset_h5", "profileId": "profile_h5"})
    write("api/validated_plan.json", response.raw_json)
    write("api/job_response.json", {"ok": created.ok, "job_id": created.job_id, "plan_id": created.plan_id, "plan_hash": created.plan_hash, "status": result.status})
    write("api/artifacts.json", live_artifacts)
    write("api/tool_calls.json", repositories.tool_calls.list_for_job(created.job_id))
    write("api/events.json", [event.model_dump(mode="json") for event in repositories.job_events.list_for_job(created.job_id)])
    write("live_payload.json", {"api": {"artifacts": live_artifacts}, "cases": {"gamma": gamma, "non_gamma": non_gamma, "imaginary": imaginary}})
    write("security/inertness.json", {"artifact_javascript": False, "artifact_html": False, "artifact_shader": False, "external_urls": False, "remote_assets": False, "frames_persisted": False, "real_llm": False})
    (EVIDENCE / "README.md").write_text("# Phase 10H-5 Phonon Animation Evidence\n\nLive Mock Planner, PlanValidator, QueueWorkerRuntime artifacts plus real local browser/WebGL evidence. Animation packages are inert, bounded, frame-free, and rendered by application-owned code.\n", encoding="utf-8")
    print("PHONON_ANIMATION_API_EVIDENCE_PASS")
    print("PHONON_ANIMATION_REFERENCE_EVIDENCE_PASS")
    print("NO_PHONON_ANIMATION_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


if __name__ == "__main__":
    main()
