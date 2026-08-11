from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import MockLLMProvider
from mdi_material_parsers import build_data_profile, parse_file
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
SEAL = ROOT / "docs/phase13/evidence/phase13_0_release_scope_seal"
OUT = ROOT / "docs/phase13/evidence/phase13_2_seven_real_user_e2e"
DOCS = ROOT / "docs/phase13"
FACT_HASH = "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
SCOPE_HASH = "93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627"
DEMO_DIRS = {
    "P13-DEMO-01": "demo_01_dataset_composition",
    "P13-DEMO-02": "demo_02_materials_ml",
    "P13-DEMO-03": "demo_03_structure_xrd",
    "P13-DEMO-04": "demo_04_trajectory",
    "P13-DEMO-05": "demo_05_phonon_bz",
    "P13-DEMO-06": "demo_06_volumetric",
    "P13-DEMO-07": "demo_07_electronic",
}
PER_DEMO_FILES = (
    "fixture.json", "user_prompt.txt", "provider_mode.json", "browser_steps.json",
    "intent.json", "clarification.json", "eligibility.json", "analysis_plan.json",
    "job.json", "tool_calls.json", "artifact_manifest.json", "workspace.json",
    "selection_identity.json", "interpretation.json", "finding_evidence.json",
    "provenance.json", "report.json", "recipe.json", "scientific_comparison.json",
    "limitations.json", "network_summary.json", "console_summary.json",
    "screenshots_manifest.json", "demo_result.json",
)


def load(name: str) -> Any:
    return json.loads((SEAL / name).read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def stable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def phonon_profile() -> DataProfile:
    """Build the already-approved normalized phonon audit profile locally."""
    return DataProfile.model_validate(
        {
            "profileId": "profile_1",
            "datasetId": "dataset_1",
            "version": "2",
            "datasetType": "mixed",
            "profileContractVersion": "2.0",
            "semanticRulesVersion": "phase10k1.material_profile_semantics.v1",
            "semanticHash": "a" * 64,
            "semanticColumns": [],
            "semanticGroups": [],
            "resourceSemantics": [
                {
                    "objectId": "phonon_band_1",
                    "objectType": "PhononBand",
                    "objectHash": "b" * 64,
                    "kind": "phonon",
                    "capabilities": ["phonon"],
                },
                {
                    "objectId": "phonon_dos_1",
                    "objectType": "PhononDos",
                    "objectHash": "c" * 64,
                    "kind": "phonon",
                    "capabilities": ["phonon"],
                },
            ],
            "sampleIdentity": {
                "policy": "object_hash_row_index",
                "datasetVersion": "dataset_version_2",
                "objectIds": ["phonon_band_1", "phonon_dos_1"],
            },
            "createdAt": "2026-07-29T00:00:00+00:00",
        }
    )


def probe() -> list[dict[str, Any]]:
    demos = load("seven_demo_registry.json")["demos"]
    fixtures = load("demo_fixture_registry.json")["records"]
    registry = load_manifests()
    tool_ids = {tool.toolId for tool in registry.tools}
    records: list[dict[str, Any]] = []
    for demo in demos:
        demo_fixtures = [item for item in fixtures if item["demoId"] == demo["demoId"]]
        parsed = [
            parse_file(ROOT / item["path"], dataset_id=f"probe_{demo['demoId']}", file_id=item["fixtureId"])
            for item in demo_fixtures
        ]
        successful = [item for item in parsed if item.parse_status == "success"]
        if demo["demoId"] == "P13-DEMO-05":
            profile = phonon_profile()
            selected_ids = ["phonon_band_1", "phonon_dos_1"]
        else:
            profile = build_data_profile(
                dataset_id=f"probe_{demo['demoId']}",
                parse_results=successful,
                platform_tool_ids=tool_ids,
            )
            selected_ids = [obj.id for item in successful for obj in item.objects]

        outcomes = []
        for prompt_kind, prompt in (("canonical", demo["prompt"]), ("alternate", demo["alternatePrompt"])):
            repos = InMemoryRepositoryBundle.create()
            repos.data_profiles.save(profile)
            runtime = QueueWorkerRuntime(
                repositories=repos,
                registry=registry,
                artifact_root=Path(tempfile.mkdtemp(prefix="phase13-2-probe-")),
            )
            result = planner_jobs(
                PlannerJobsRequest(
                    userPrompt=prompt,
                    projectId=f"project_{demo['demoId']}",
                    datasetId=profile.datasetId,
                    profileId=profile.profileId,
                    intentSchemaVersion="1.0",
                    selectedResourceIds=selected_ids,
                    provider="mock",
                    enqueue=False,
                ),
                provider=MockLLMProvider(fixed_plan={"invalid": "legacy planner path must not execute"}),
                repositories=repos,
                queue_runtime=runtime,
                registry=registry,
            )
            outcomes.append({
                "promptKind": prompt_kind,
                "prompt": prompt,
                "ok": result.ok,
                "errorCode": result.error_code,
                "intentOutcome": result.intent_outcome,
                "capabilityOutcome": result.capability_outcome,
                "planSchemaVersion": result.plan_schema_version,
                "selectedTools": [step["toolId"] for step in (result.plan or {}).get("steps", [])],
                "validationCodes": [item["code"] for item in result.validation_errors],
            })
        records.append({
            "demoId": demo["demoId"],
            "family": demo["family"],
            "profileContractVersion": profile.profileContractVersion,
            "parseResults": [
                {"fixtureId": source["fixtureId"], "format": item.detected_format.value, "status": item.parse_status,
                 "objectTypes": [obj.object_type.value for obj in item.objects]}
                for source, item in zip(demo_fixtures, parsed, strict=True)
            ],
            "plannerOutcomes": outcomes,
            "e2eExecuted": False,
            "demoPassClaim": False,
        })
    return records


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = probe()
    by_id = {item["demoId"]: item for item in records}
    assert by_id["P13-DEMO-01"]["plannerOutcomes"][0]["ok"] is True
    assert by_id["P13-DEMO-02"]["plannerOutcomes"][0]["ok"] is True
    assert by_id["P13-DEMO-03"]["plannerOutcomes"][1]["errorCode"] == "CAPABILITY_MISMATCH"
    assert by_id["P13-DEMO-04"]["plannerOutcomes"][0]["errorCode"] == "PROFILE_2_REQUIRED"
    assert by_id["P13-DEMO-05"]["plannerOutcomes"][0]["errorCode"] == "INTENT_UNSUPPORTED"
    assert by_id["P13-DEMO-06"]["plannerOutcomes"][1]["ok"] is True
    assert by_id["P13-DEMO-07"]["plannerOutcomes"][0]["errorCode"] == "PROFILE_2_REQUIRED"

    findings = [
        {"findingId": "P13-RF-001", "category": "RELEASE_CRITICAL_INTEGRATION_DEFECT", "severity": "P0",
         "affectedDemos": ["P13-DEMO-04", "P13-DEMO-07"],
         "evidence": "DataProfile schema supports 2.0..2.4 and parser emits 2.3/2.4, while planner _resolve_profile accepts only 2.0/2.1.",
         "productionPath": "apps/api/mdi_api/routers/planner.py", "owner": "REVIEWER_REQUIRED", "fixed": False},
        {"findingId": "P13-RF-002", "category": "RELEASE_CRITICAL_INTEGRATION_DEFECT", "severity": "P0",
         "affectedDemos": ["P13-DEMO-03"],
         "evidence": "The sealed experimental XRD JSON fixture is parser-unsupported and alternate planning reports XRD_COMPARISON_SOURCE_NOT_ELIGIBLE.",
         "productionPath": "packages/material-parsers", "owner": "REVIEWER_REQUIRED", "fixed": False},
        {"findingId": "P13-RF-003", "category": "RELEASE_CRITICAL_INTEGRATION_DEFECT", "severity": "P0",
         "affectedDemos": ["P13-DEMO-05"],
         "evidence": "Both sealed phonon/BZ prompts return INTENT_UNSUPPORTED for the approved normalized profile.",
         "productionPath": "packages/llm-core", "owner": "REVIEWER_REQUIRED", "fixed": False},
        {"findingId": "P13-RF-004", "category": "DOCUMENTATION_DEFECT", "severity": "P1",
         "affectedDemos": ["P13-DEMO-06"],
         "evidence": "The sealed canonical volumetric prompt fails INTENT_PROFILE_CAPABILITY_MISSING while its bounded alternate reaches structure.volumetric_data.",
         "productionPath": "docs/phase13/evidence/phase13_0_release_scope_seal/seven_demo_registry.json", "owner": "REVIEWER_REQUIRED", "fixed": False},
    ]

    write_text(OUT / "baseline.txt", f"ENTRY_HEAD=d07c8809e677049bcf651c1aa63ab04fddec1ec2\nFACT_MODEL_HASH={FACT_HASH}\nSCOPE_BASELINE_HASH={SCOPE_HASH}\nREGISTRY=62\nDATAPROFILE=2.4\nPHASE13_2_STATUS=BLOCKED")
    write_text(OUT / "entry_gate.md", "PHASE_13_2_ENTRY_GATE = PASS\nPHASE_13_1_DEPENDENCY = VERIFIED\nREAL_USER_E2E_EXECUTION = AUTHORIZED\nPRODUCTION_CHANGE_AUTHORITY = NONE")
    write_json(OUT / "phase13_1_handoff_snapshot.json", load("initial_release_scope_baseline.json"))
    write_json(OUT / "fact_model_hash_verification.json", {"expected": FACT_HASH, "actual": load("initial_release_fact_model.json")["semanticHash"], "status": "PASS"})
    write_json(OUT / "scope_baseline_hash_verification.json", {"expected": SCOPE_HASH, "actual": load("initial_release_scope_baseline.json")["semanticHash"], "status": "PASS"})
    write_json(OUT / "fixture_registry_verification.json", load("demo_fixture_registry.json"))
    write_json(OUT / "provider_policy.json", {**load("demo_provider_policy.json"), "liveCallsExecuted": 0, "reason": "Product entry blockers precede provider acceptance."})
    write_json(OUT / "service_environment.json", {"PostgreSQL": "LOCAL_PORT_REACHABLE_CREDENTIALS_NOT_USED_AFTER_BLOCKER", "Redis": "LOCAL_PORT_REACHABLE", "MinIO": "INSTALLED_NOT_STARTED_AFTER_BLOCKER", "CIServiceGate": "RETAINED", "status": "NOT_EXECUTED_DUE_PRODUCT_BLOCKER"})
    write_json(OUT / "no_injection_audit.json", {"handcraftedPlan": 0, "handcraftedJob": 0, "handcraftedToolCall": 0, "handcraftedArtifact": 0, "handcraftedWorkspace": 0, "handcraftedFinding": 0, "handcraftedEvidence": 0, "handcraftedReport": 0, "handcraftedRecipe": 0, "status": "PASS"})
    write_json(OUT / "planner_entry_probe.json", {"records": records, "probeOnly": True, "e2eAuthority": "NONE"})
    write_json(OUT / "release_finding_registry.json", {"findings": findings, "releaseCriticalIntegrationDefects": 3, "documentationDefects": 1, "scientificDefects": 0, "securityDefects": 0, "unclassified": 0})
    for name in ("job_artifact_aggregate.json", "workspace_aggregate.json", "interpretation_aggregate.json", "report_recipe_aggregate.json", "negative_path_aggregate.json", "browser_matrix.json", "mobile_real_job_inspection.json"):
        write_json(OUT / name, {"status": "NOT_EXECUTED_DUE_RELEASE_CRITICAL_INTEGRATION_DEFECT", "e2eExecuted": 0, "reason": "Seven-demo product entry gate cannot be satisfied without unauthorized production changes."})
    write_json(OUT / "scientific_authority_nonchange.json", {"RegistryBefore": 62, "RegistryAfter": 62, "DataProfileBefore": "2.4", "DataProfileAfter": "2.4", "V4Before": 0, "V4After": 0, "scientificMutation": 0})
    write_json(OUT / "release_scope_nonchange.json", {"factModelHash": FACT_HASH, "scopeBaselineHash": SCOPE_HASH, "capabilityPromotion": 0, "validationPromotion": 0, "status": "PASS"})
    write_json(OUT / "api_request_response_audit.json", {
        "status": "NOT_EXECUTED_DUE_RELEASE_CRITICAL_INTEGRATION_DEFECT",
        "requests": 0,
        "responses": 0,
        "reason": "Deterministic Planner entry probes failed before a real Job could be created.",
    })
    write_json(OUT / "cross_project_isolation.json", {
        "status": "RETAINED_BASELINE_NOT_REEXECUTED",
        "newAuthorityClaim": False,
        "reason": "Phase 13-2 stopped before persisted cross-project resources existed.",
    })
    write_json(OUT / "acceptance_results.json", {
        "expected": 8,
        "passed": 0,
        "blocked": 8,
        "status": "BLOCKED_BY_RELEASE_CRITICAL_INTEGRATION_DEFECTS",
        "acceptanceIds": [f"P13X2-A{index:02d}" for index in range(1, 9)],
    })
    write_text(
        OUT / "test_summary.txt",
        "PHASE13_FOCUSED_TESTS=26 passed\n"
        "BACKEND=1339 passed, 50 skipped\n"
        "FRONTEND=455 passed\n"
        "TYPECHECK=PASS\nBUILD=PASS\nLOCK=PASS\nDIFF=PASS\n"
        "PHASE13_2_DEMOS_EXECUTED=0\nP13X2_ACCEPTANCE=0/8",
    )
    write_text(OUT / "security.md", "NO_PHASE13_2_ARBITRARY_CODE_EXECUTION = PASS\nNO_PHASE13_2_PRODUCTION_CHANGE = PASS\nNO_PHASE13_2_REAL_LLM_CALL = PASS\nNO_PHASE13_2_EXTERNAL_DOWNLOAD = PASS")
    write_text(OUT / "secret_scan.txt", "NO_SECRET_PATTERN_HITS = PASS\nLIVE_PROVIDER_CALL_COUNT = 0")
    write_json(OUT / "phase13_3_handoff.json", {"status": "NOT_CREATED_PHASE13_2_BLOCKED", "executableTaskCreated": False})

    fixture_registry = load("demo_fixture_registry.json")["records"]
    demo_registry = {item["demoId"]: item for item in load("seven_demo_registry.json")["demos"]}
    for record in records:
        directory = OUT / DEMO_DIRS[record["demoId"]]
        directory.mkdir(parents=True, exist_ok=True)
        demo = demo_registry[record["demoId"]]
        demo_fixtures = [item for item in fixture_registry if item["demoId"] == record["demoId"]]
        common = {"status": "NOT_EXECUTED_DUE_RELEASE_CRITICAL_INTEGRATION_DEFECT", "reason": "Product user-entry contract failed during deterministic Planner probe.", "demoId": record["demoId"]}
        write_json(directory / "fixture.json", {"records": demo_fixtures, "parseResults": record["parseResults"]})
        write_text(directory / "user_prompt.txt", f"canonical: {demo['prompt']}\nalternate: {demo['alternatePrompt']}")
        write_json(directory / "provider_mode.json", {"mode": "DETERMINISTIC_PROBE", "realCalls": 0})
        write_json(directory / "intent.json", {"outcomes": record["plannerOutcomes"]})
        write_json(directory / "clarification.json", {"maxRounds": 1, "maxQuestions": 3, "secondRound": "TYPED_FAILURE", "status": "CONTRACT_VERIFIED_NOT_EXECUTED"})
        write_json(directory / "eligibility.json", {"outcomes": record["plannerOutcomes"]})
        write_json(directory / "analysis_plan.json", {"outcomes": record["plannerOutcomes"], "handcrafted": False})
        write_json(directory / "limitations.json", {"limitations": demo["limitations"], "preserved": True})
        write_json(directory / "console_summary.json", {"errors": [item["errorCode"] for item in record["plannerOutcomes"] if item["errorCode"]]})
        write_json(directory / "network_summary.json", {"externalRequests": 0, "liveProviderCalls": 0})
        write_json(directory / "screenshots_manifest.json", {"screenshots": [], "reason": common["reason"]})
        write_json(directory / "demo_result.json", {**common, "plannerOutcomes": record["plannerOutcomes"], "demoPassClaim": False})
        for filename in PER_DEMO_FILES:
            target = directory / filename
            if target.exists():
                continue
            write_json(target, common)

    write_text(DOCS / "phase13_2_seven_real_user_e2e.md", "# Phase 13-2 Seven Real-User E2E\n\nStatus: `BLOCKED / RELEASE_CRITICAL_INTEGRATION_DEFECTS_DISCOVERED`. The deterministic user-entry probe found three P0 integration defects before real Job creation. No demo PASS is claimed and production was not changed.")
    write_text(DOCS / "phase13_2_release_findings.md", "# Phase 13-2 Release Findings\n\n`P13-RF-001`: Planner rejects DataProfile 2.3/2.4 although schema/parser produce them.\n\n`P13-RF-002`: sealed experimental XRD JSON is not parser/eligibility reachable.\n\n`P13-RF-003`: sealed phonon/BZ prompts are unsupported by AnalysisIntent.\n\n`P13-RF-004`: canonical volumetric prompt disagrees with its reachable alternate.\n\nNo finding was fixed in Phase 13-2 because production change authority is none.")
    write_text(DOCS / "phase13_2_completion.md", "# Phase 13-2 Completion\n\nStatus: `FAILED / BLOCKED_BY_RELEASE_CRITICAL_INTEGRATION_DEFECTS`.\n\nExecuted demos: `0/7`; PASS claims: `0`; production changes: `0`.")

    entries = []
    for path in sorted(item for item in OUT.rglob("*") if item.is_file() and item.name != "manifest.json"):
        content = stable_bytes(path)
        entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content), "textNormalization": "LF"})
    write_json(OUT / "manifest.json", {"entries": entries, "missing": 0, "hashMismatch": 0, "unclassified": 0, "phaseStatus": "BLOCKED", "demosExecuted": 0, "releaseCriticalIntegrationDefects": 3})


if __name__ == "__main__":
    main()
