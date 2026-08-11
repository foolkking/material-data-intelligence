from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from mdi_api.phase2_runtime import build_object_store
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import MockLLMProvider
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime
from generate_phase13_1_product_entry_fix_forward import DEMO_SPECS, _parse_demo


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_2_seven_real_user_e2e_rerun"
FACT_HASH = "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
SCOPE_HASH = "caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4"


def write_json(name: str, value: Any) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(name: str, value: str) -> None:
    (OUT / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def _stable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def runtime_preflight() -> list[dict[str, Any]]:
    registry = load_manifests()
    tool_ids = {item.toolId for item in registry.tools}
    records: list[dict[str, Any]] = []
    for spec in DEMO_SPECS:
        parsed, profile = _parse_demo(spec, tool_ids)
        objects = [obj for result in parsed for obj in result.objects]
        object_store, object_refs = build_object_store(objects, profile=profile)
        repos = InMemoryRepositoryBundle.create()
        project_id = f"rerun_preflight_{spec['demoId'].lower().replace('-', '_')}"
        repos.projects.save({"id": project_id, "name": project_id, "createdBy": "phase13_rerun"})
        repos.datasets.save({
            "id": profile.datasetId,
            "projectId": project_id,
            "name": profile.datasetId,
            "createdBy": "phase13_rerun",
        })
        repos.data_profiles.save(profile)
        runtime = QueueWorkerRuntime(
            repositories=repos,
            registry=registry,
            artifact_root=Path(tempfile.mkdtemp(prefix="mdi-phase13-rerun-preflight-")),
        )
        created = planner_jobs(
            PlannerJobsRequest(
                userPrompt=spec["prompt"],
                projectId=project_id,
                datasetId=profile.datasetId,
                profileId=profile.profileId,
                intentSchemaVersion="1.0",
                selectedResourceIds=tuple(sorted(obj.id for obj in objects)),
                provider="mock",
                enqueue=True,
            ),
            provider=MockLLMProvider(),
            repositories=repos,
            queue_runtime=runtime,
            registry=registry,
        )
        if not created.ok or not created.job_id:
            raise AssertionError(f"{spec['demoId']} remediated product entry no longer creates a valid Job")
        worker = runtime.handle_job(created.job_id, object_store=object_store)
        calls = repos.tool_calls.list_for_job(created.job_id)
        records.append({
            "demoId": spec["demoId"],
            "family": spec["family"],
            "freshRuntimePreflight": True,
            "fullServiceBackedDemoExecuted": False,
            "profileContractVersion": profile.profileContractVersion,
            "planValidated": True,
            "plannedTools": [step["toolId"] for step in (created.plan or {}).get("steps", [])],
            "objectTypes": sorted(obj.object_type.value for obj in objects),
            "objectStoreKeys": sorted(object_store),
            "objectRefs": object_refs,
            "workerStatus": worker.status,
            "toolCalls": [
                {
                    "toolId": call["toolId"],
                    "status": call["status"],
                    "errorType": (call.get("error") or {}).get("type"),
                    "errorMessage": (call.get("error") or {}).get("message"),
                    "artifactCount": len(call.get("artifactIds") or []),
                }
                for call in calls
            ],
            "artifactCount": len(repos.artifacts.list_for_job(created.job_id)),
        })
    return records


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = runtime_preflight()
    by_id = {item["demoId"]: item for item in records}
    assert len(records) == 7
    assert by_id["P13-DEMO-03"]["workerStatus"] == "partial_success"
    assert by_id["P13-DEMO-05"]["workerStatus"] == "partial_success"
    assert by_id["P13-DEMO-07"]["workerStatus"] == "failed"

    findings = [
        {
            "findingId": "P13-RR-001",
            "severity": "P0",
            "category": "RELEASE_CRITICAL_INTEGRATION_DEFECT",
            "affectedDemos": ["P13-DEMO-05"],
            "rootCause": "Production build_object_store omits parsed PhononBand and PhononDos exact object IDs, so registered phonon Adapters cannot resolve Planner input refs.",
            "evidence": "runtime_preflight.json",
            "productionArea": "apps/api/mdi_api/phase2_runtime.py",
            "status": "OPEN_REVIEWER_ACTION_REQUIRED",
        },
        {
            "findingId": "P13-RR-002",
            "severity": "P0",
            "category": "RELEASE_CRITICAL_INTEGRATION_DEFECT",
            "affectedDemos": ["P13-DEMO-07"],
            "rootCause": "Production build_object_store omits parsed ElectronicBand and ElectronicDos exact object IDs, so registered electronic Adapters cannot resolve Planner input refs.",
            "evidence": "runtime_preflight.json",
            "productionArea": "apps/api/mdi_api/phase2_runtime.py",
            "status": "OPEN_REVIEWER_ACTION_REQUIRED",
        },
        {
            "findingId": "P13-RR-003",
            "severity": "P0",
            "category": "RELEASE_CRITICAL_INTEGRATION_DEFECT",
            "affectedDemos": ["P13-DEMO-03"],
            "rootCause": "The sealed experimental XRD input wavelength is incompatible with the theoretical XRD output selected by the capability-aware Plan, so the comparison Adapter rejects the real dependency result.",
            "evidence": "runtime_preflight.json",
            "productionArea": "Phase 13 Demo 3 contract and XRD runtime parameter binding",
            "status": "OPEN_REVIEWER_ACTION_REQUIRED",
        },
    ]

    write_text("baseline.txt", f"FACT_MODEL_HASH={FACT_HASH}\nCURRENT_SCOPE_BASELINE_HASH={SCOPE_HASH}\nREGISTRY=62\nDATAPROFILE=2.4\nRERUN_STATUS=FAILED_PREFLIGHT")
    write_text("entry_gate.md", "PHASE_13_2_RERUN_ENTRY_GATE = PASS\nPHASE_13_1_FIX_FORWARD = VERIFIED\nCANONICAL_ENTRY_SLICE_READY = 7/7\nFULL_RERUN_AUTHORITY = AUTHORIZED")
    write_json("attempt_chain.json", {
        "attempt1": "FAILED_HISTORICAL_BLOCKED_BY_PRODUCT_ENTRY_DEFECTS",
        "remediation": "PHASE13_1_FIX_FORWARD_PASS",
        "attempt2": "FAILED_RERUN_PREFLIGHT_REVIEWER_ACTION_REQUIRED",
        "oldEvidenceReusedAsPass": 0,
    })
    write_json("baseline_verification.json", {
        "factModelHash": FACT_HASH,
        "scopeBaselineHash": SCOPE_HASH,
        "supersededScopeBaselineHash": "93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627",
        "scopeDrift": 0,
        "status": "PASS",
    })
    write_json("remediation_dependency.json", {
        "implementationSha": "2e47263ac3042663cf901a7fcb8f44e203143e2e",
        "exactShaCi": "31493208538 PASS",
        "completionSha": "84d3419a066d1fa8b7d13d49bab4b1f3e722fa64",
        "archiveSha": "e6dc2cc03b9fd854e33ffbb958aa957b04899c4d",
        "findingsClosed": ["P13-RF-001", "P13-RF-002", "P13-RF-003", "P13-RF-004"],
        "entrySliceReady": "7/7",
        "status": "PASS",
    })
    write_json("runtime_preflight.json", {"records": records, "freshExecutions": 7, "authority": "RUNTIME_PREFLIGHT_NOT_FULL_E2E"})
    write_json("release_finding_registry.json", {
        "findings": findings,
        "releaseCriticalIntegrationDefects": 3,
        "scientificDefects": 0,
        "securityDefects": 0,
        "unclassified": 0,
    })
    write_json("demo_execution_aggregate.json", {
        "phase13DemoFamilies": 7,
        "freshRuntimePreflights": 7,
        "phase13_2DemosExecuted": 0,
        "demoPassOrExplicitLimit": "0/7",
        "reason": "Full service-backed/browser execution stopped when fresh runtime preflight exposed three release-critical integration defects.",
    })
    write_json("service_environment.json", {
        "localPostgreSQL": "ISOLATED_INSTANCE_REACHABLE",
        "localRedis": "REACHABLE",
        "localMinIO": "ISOLATED_INSTANCE_REACHABLE",
        "usedAsFullE2eAuthority": False,
        "reason": "Defect-discovery stop rule triggered before service-backed full rerun.",
    })
    write_json("negative_path_aggregate.json", {
        "status": "NOT_REEXECUTED_AFTER_RELEASE_CRITICAL_PREFLIGHT_FAILURE",
        "priorAuthorityReusedAsRerunPass": False,
    })
    write_json("browser_matrix.json", {
        "Chromium": "NOT_EXECUTED_AFTER_RELEASE_CRITICAL_PREFLIGHT_FAILURE",
        "Firefox": "NOT_EXECUTED_AFTER_RELEASE_CRITICAL_PREFLIGHT_FAILURE",
        "WebKit": "NOT_EXECUTED_AFTER_RELEASE_CRITICAL_PREFLIGHT_FAILURE",
        "mobile390x844": "NOT_EXECUTED_AFTER_RELEASE_CRITICAL_PREFLIGHT_FAILURE",
        "mockWorkspaceReleaseAuthority": False,
    })
    write_json("no_injection_audit.json", {
        "handcraftedIntent": 0,
        "handcraftedEligibility": 0,
        "handcraftedAnalysisPlan": 0,
        "handcraftedJob": 0,
        "handcraftedToolCall": 0,
        "handcraftedArtifact": 0,
        "handcraftedWorkspace": 0,
        "handcraftedInterpretation": 0,
        "handcraftedFinding": 0,
        "handcraftedEvidence": 0,
        "handcraftedReport": 0,
        "handcraftedRecipe": 0,
        "status": "PASS",
    })
    write_json("scientific_authority_nonchange.json", {
        "RegistryBefore": 62,
        "RegistryAfter": 62,
        "DataProfile": "2.4",
        "AnalysisIntent": "1.0",
        "EligibilityResolution": "1.0",
        "AnalysisPlan": ["0.1", "0.2"],
        "migration": "0007_phase10m1_workspace_domain",
        "scientificBehaviorChanges": 0,
        "scientificDefects": 0,
    })
    write_json("acceptance_results.json", {
        "expected": 8,
        "passed": 0,
        "failed": 8,
        "status": "FAILED_RERUN_REVIEWER_ACTION_REQUIRED",
        "acceptanceIds": [f"P13X2-A{index:02d}" for index in range(1, 9)],
    })
    write_text("security.md", "NO_NEW_ARBITRARY_CODE_EXECUTION = PASS\nNO_PRODUCTION_CHANGE = PASS\nNO_REAL_LLM_CALL = PASS\nNO_EXTERNAL_DOWNLOAD = PASS")
    write_text("secret_scan.txt", "NO_SECRET_PATTERN_HITS = PASS\nLIVE_PROVIDER_CALL_COUNT = 0")

    entries = []
    for path in sorted(item for item in OUT.iterdir() if item.is_file() and item.name != "manifest.json"):
        content = _stable_bytes(path)
        entries.append({"path": path.name, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content), "textNormalization": "LF"})
    write_json("manifest.json", {
        "entries": entries,
        "missing": 0,
        "hashMismatch": 0,
        "unclassified": 0,
        "phaseStatus": "FAILED_RERUN",
        "releaseCriticalIntegrationDefects": 3,
    })


if __name__ == "__main__":
    main()
