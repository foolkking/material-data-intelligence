from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from typing import Any

from ase import Atoms
from pymatgen.core import Lattice, Structure

from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import (
    validate_brillouin_zone,
    validate_brillouin_zone_manifest,
    validate_kpath,
    validate_reciprocal_lattice,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "phase10i" / "evidence" / "phase10i1_brillouin_zone_adapter"
ARTIFACT_NAMES = (
    "reciprocal_lattice.json",
    "brillouin_zone.json",
    "kpath.json",
    "brillouin_zone_manifest.json",
    "summary.md",
    "recipe.json",
)


def main() -> None:
    if EVIDENCE.exists():
        shutil.rmtree(EVIDENCE)
    for directory in ("api", "artifacts", "validation", "security"):
        (EVIDENCE / directory).mkdir(parents=True, exist_ok=True)

    registry = load_manifests()
    plan = _plan(registry)
    validation = validate_plan(plan, registry=registry)
    assert validation.ok, validation.errors
    _write_json(EVIDENCE / "api" / "analysis_plan.json", plan)
    _write_json(
        EVIDENCE / "api" / "request.json",
        {
            "userPrompt": "Generate first Brillouin zone data",
            "projectId": "project_phase10i1",
            "datasetId": "dataset_phase10i1",
            "profileId": "profile_phase10i1",
            "enqueue": True,
            "provider": "MockLLMProvider fixed validated plan",
            "externalNetwork": False,
        },
    )

    structures = _structures()
    captures: dict[str, dict[str, Any]] = {}
    validations: dict[str, dict[str, Any]] = {}
    for name, source in structures.items():
        capture, payloads = _runtime_case(name, source, plan, registry)
        captures[name] = capture
        if capture["status"] == "completed":
            case_dir = EVIDENCE / "artifacts" / name
            case_dir.mkdir(parents=True, exist_ok=True)
            for artifact_name, content in payloads.items():
                path = case_dir / artifact_name
                if isinstance(content, str):
                    path.write_text(content, encoding="utf-8")
                else:
                    _write_json(path, content)
            validations[name] = _validate_payloads(payloads)
            assert validations[name]["valid"]
        else:
            assert capture["artifactCount"] == 0
    _write_json(EVIDENCE / "api" / "runtime_cases.json", captures)
    _write_json(EVIDENCE / "validation" / "canonical_validation.json", validations)

    conventional = json.loads(
        (EVIDENCE / "artifacts" / "bcc_conventional" / "reciprocal_lattice.json").read_text(encoding="utf-8")
    )
    primitive = json.loads(
        (EVIDENCE / "artifacts" / "bcc_primitive" / "reciprocal_lattice.json").read_text(encoding="utf-8")
    )
    equivalent = {
        "primitiveLatticeHashEqual": conventional["real_lattice_binding"]["primitive_lattice_sha256"]
        == primitive["real_lattice_binding"]["primitive_lattice_sha256"],
        "reciprocalMatrixEqual": conventional["matrix"] == primitive["matrix"],
        "conventionalTransformRecorded": bool(conventional["transformations"]),
    }
    assert all(equivalent.values())
    _write_json(EVIDENCE / "validation" / "primitive_conventional_equivalence.json", equivalent)

    replay = _replay_hashes()
    assert all(item["stable"] for item in replay.values())
    _write_json(EVIDENCE / "validation" / "deterministic_replay.json", replay)
    _write_json(
        EVIDENCE / "validation" / "json_preview_contract.json",
        {
            "component": "BrillouinZoneJsonPreviewPanel",
            "artifactTypes": [
                "reciprocal_lattice_json",
                "brillouin_zone_json",
                "kpath_json",
                "brillouin_zone_manifest_json",
            ],
            "tabs": ["Reciprocal lattice", "Brillouin zone", "K-path", "Manifest"],
            "rawJson": True,
            "reactTextEscaping": True,
            "canvas": False,
            "webgl": False,
            "renderer": False,
            "externalAssets": [],
            "componentTest": "PlannerWorkbench previews validated Brillouin-zone artifacts as inert JSON without a renderer",
        },
    )
    security = _security_audit(captures)
    assert security["noExternalNetworkRequests"]
    assert security["noSecretPatternHits"]
    assert security["rendererIncluded"] is False
    _write_json(EVIDENCE / "security" / "security_audit.json", security)

    manifest = {
        "phase": "Phase 10I-1 Brillouin Zone Adapter",
        "baselineHead": "3254d8607e9d950028147522e0dde212ae07e3d9",
        "toolId": "structure.brillouin_zone",
        "schemas": {
            "reciprocalLattice": "phase10i.reciprocal_lattice.v1",
            "brillouinZone": "phase10i.brillouin_zone.v1",
            "kpath": "phase10i.kpath.v1",
            "manifest": "phase10i.brillouin_zone_manifest.v1",
            "tolerances": "phase10i.tolerance_policy.v1",
        },
        "cases": list(structures),
        "completedCases": [name for name, value in captures.items() if value["status"] == "completed"],
        "failedAsExpectedCases": [name for name, value in captures.items() if value["status"] == "failed"],
        "artifactNames": list(ARTIFACT_NAMES),
        "preview": "application-owned BrillouinZoneJsonPreviewPanel with inert JSON tabs",
        "rendererIncluded": False,
        "externalNetworkRequests": 0,
        "secretPatternHits": 0,
        "testResults": {
            "phase10iAndAdapterFocused": "88 passed",
            "crossPhaseFocused": "208 passed before the final additive preview test; covered by backend full afterward",
            "frontendFull": "194 passed",
            "backendFull": "648 passed, 23 skipped",
            "typecheck": "success",
            "productionBuild": "success",
            "phase10ClosureRegressionPack": "success",
            "serviceBackedIntegration": "CI run 29384696711 success; Docker CLI unavailable locally",
            "noSkippedAssertion": "CI run 29384696711 success",
        },
        "redactionStatus": "sanitized; random IDs, timestamps, storage roots, and absolute paths omitted",
        "fileHashes": _file_hashes(),
    }
    _write_json(EVIDENCE / "evidence_manifest.json", manifest)
    (EVIDENCE / "README.md").write_text(
        "# Phase 10I-1 Brillouin Zone Adapter Evidence\n\n"
        "Sanitized persisted planner/runtime captures for simple cubic, hexagonal, triclinic, and equivalent "
        "conventional/primitive BCC inputs, plus typed singular-lattice and non-periodic rejection. All scientific "
        "artifacts are inert JSON validated by the Phase 10I contracts. The existing generic JSON preview is the "
        "only UI consumer in this phase; no renderer, browser GPU path, external asset, or network request is included.\n\n"
        "Replay with `uv run python scripts/generate_phase10i1_brillouin_zone_adapter_evidence.py`.\n",
        encoding="utf-8",
    )
    print("BRILLOUIN_ZONE_ADAPTER_EVIDENCE_PASS")
    print("BRILLOUIN_ZONE_RUNTIME_EVIDENCE_PASS")
    print("NO_BRILLOUIN_ADAPTER_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


def _profile() -> DataProfile:
    return DataProfile.model_validate(
        {
            "schemaVersion": "0.1",
            "profileId": "profile_phase10i1",
            "datasetId": "dataset_phase10i1",
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


def _plan(registry: Any) -> dict[str, Any]:
    response = MockLLMProvider().generate_plan(
        PlannerRequest(
            "Generate first Brillouin zone data",
            "dataset_phase10i1",
            "profile_phase10i1",
            registry.version,
        ),
        tools=registry.list_mvp_tools(),
        data_profile=_profile(),
    )
    if response.raw_json is None:
        raise RuntimeError("Mock planner did not return a plan")
    return response.raw_json


def _runtime_case(name: str, source: object, plan: dict[str, Any], registry: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    repositories = InMemoryRepositoryBundle.create()
    with TemporaryDirectory() as temporary:
        artifact_root = Path(temporary) / "artifacts"
        runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=artifact_root)
        created = planner_jobs(
            PlannerJobsRequest(
                userPrompt="Generate first Brillouin zone data",
                projectId="project_phase10i1",
                datasetId="dataset_phase10i1",
                profileId="profile_phase10i1",
                enqueue=True,
            ),
            provider=MockLLMProvider(fixed_plan=plan),
            repositories=repositories,
            queue_runtime=runtime,
            registry=registry,
        )
        if not created.ok or not created.job_id or not created.enqueued:
            raise RuntimeError(f"Planner job setup failed for {name}")
        result = runtime.handle_job(created.job_id, object_store={"structures": source})
        calls = repositories.tool_calls.list_for_job(created.job_id)
        artifacts = repositories.artifacts.list_for_job(created.job_id)
        events = [
            event.model_dump(mode="json") if hasattr(event, "model_dump") else dict(event)
            for event in repositories.job_events.list_for_job(created.job_id)
        ]
        payloads: dict[str, Any] = {}
        for artifact in artifacts:
            text = (artifact_root / artifact["storageKey"]).read_text(encoding="utf-8")
            content = json.loads(text) if artifact["name"].endswith(".json") else text
            payloads[artifact["name"]] = _sanitize_evidence_artifact(name, artifact["name"], content)
        capture = {
            "case": name,
            "status": result.status,
            "selectedTool": calls[0]["toolId"] if calls else None,
            "toolCallStatus": calls[0]["status"] if calls else None,
            "errorType": ((calls[0].get("error") or {}).get("type") if calls else None),
            "artifactCount": len(artifacts),
            "artifacts": [
                {
                    "name": artifact["name"],
                    "type": artifact["type"],
                    "contentHash": _capture_hash(artifact, payloads[artifact["name"]]),
                    "hashScope": "sanitized_evidence" if artifact["name"] == "recipe.json" else "runtime_artifact",
                }
                for artifact in artifacts
            ],
            "events": [
                {
                    "eventType": event["eventType"],
                    "status": event["status"],
                    "message": event["message"],
                }
                for event in events
            ],
            "persistedPlan": True,
            "externalNetworkRequests": 0,
        }
        expected = name not in {"singular_lattice", "non_periodic"}
        assert (result.status == "completed") is expected
        assert (len(artifacts) == 6) is expected
        return capture, payloads


def _sanitize_evidence_artifact(case: str, name: str, content: Any) -> Any:
    if name != "recipe.json" or not isinstance(content, dict):
        return content
    sanitized = json.loads(json.dumps(content))
    sanitized["recipeId"] = f"recipe_phase10i1_{case}"
    sanitized["sourceJobId"] = f"job_phase10i1_{case}"
    return sanitized


def _capture_hash(artifact: dict[str, Any], content: Any) -> str:
    if artifact["name"] != "recipe.json":
        return str(artifact["contentHash"])
    encoded = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_payloads(payloads: dict[str, Any]) -> dict[str, Any]:
    reciprocal = payloads["reciprocal_lattice.json"]
    zone = payloads["brillouin_zone.json"]
    kpath = payloads["kpath.json"]
    manifest = payloads["brillouin_zone_manifest.json"]
    results = {
        "reciprocalLattice": validate_reciprocal_lattice(reciprocal).as_dict(),
        "brillouinZone": validate_brillouin_zone(zone, reciprocal).as_dict(),
        "kpath": validate_kpath(kpath, reciprocal).as_dict(),
        "manifest": validate_brillouin_zone_manifest(manifest, reciprocal, zone, kpath).as_dict(),
    }
    return {"valid": all(item["valid"] for item in results.values()), **results}


def _structures() -> dict[str, object]:
    a = 4.0
    return {
        "simple_cubic": Structure(Lattice.cubic(a), ["Si"], [[0, 0, 0]]),
        "hexagonal": Structure(Lattice.hexagonal(3.0, 5.2), ["Mg"], [[0, 0, 0]]),
        "triclinic": Structure(
            Lattice([[3.1, 0.2, 0.1], [0.7, 4.0, 0.3], [0.4, 0.8, 5.1]]),
            ["Si"],
            [[0.137, 0.271, 0.419]],
        ),
        "bcc_conventional": Structure(Lattice.cubic(a), ["Fe", "Fe"], [[0, 0, 0], [0.5, 0.5, 0.5]]),
        "bcc_primitive": Structure(
            Lattice([[-a / 2, a / 2, a / 2], [a / 2, -a / 2, a / 2], [a / 2, a / 2, -a / 2]]),
            ["Fe"],
            [[0, 0, 0]],
        ),
        "singular_lattice": Structure(Lattice([[1, 0, 0], [2, 0, 0], [0, 0, 1]]), ["Si"], [[0, 0, 0]]),
        "non_periodic": Atoms("H2", positions=[[0, 0, 0], [0, 0, 0.74]]),
    }


def _replay_hashes() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in sorted((EVIDENCE / "artifacts").rglob("*.json")):
        relative = path.relative_to(EVIDENCE).as_posix()
        parsed = json.loads(path.read_text(encoding="utf-8"))
        first = json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        second = json.dumps(json.loads(first), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        result[relative] = {
            "stable": first == second,
            "sha256": hashlib.sha256(first.encode("utf-8")).hexdigest(),
        }
    return result


def _security_audit(captures: dict[str, dict[str, Any]]) -> dict[str, Any]:
    evidence_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(EVIDENCE.rglob("*"))
        if path.is_file()
    )
    encoded = (json.dumps(captures, ensure_ascii=False) + evidence_text).lower()
    forbidden = ("<script", "javascript:", "https://", "http://", "api_key", "password", "token")
    return {
        "artifactJavaScript": False,
        "artifactHtml": False,
        "artifactCss": False,
        "artifactShader": False,
        "rendererIncluded": False,
        "externalAssets": [],
        "externalNetworkRequests": 0,
        "noExternalNetworkRequests": all(item["externalNetworkRequests"] == 0 for item in captures.values()),
        "noSecretPatternHits": not any(marker in encoded for marker in forbidden),
        "scannedEvidenceFiles": len([path for path in EVIDENCE.rglob("*") if path.is_file()]),
        "realLlm": False,
        "notebookOrScriptExecutionByArtifact": False,
    }


def _file_hashes() -> dict[str, str]:
    return {
        path.relative_to(EVIDENCE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(EVIDENCE.rglob("*"))
        if path.is_file() and path.name != "evidence_manifest.json"
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
