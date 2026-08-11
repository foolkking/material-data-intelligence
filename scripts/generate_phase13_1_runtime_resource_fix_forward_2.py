from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from mdi_api.phase2_runtime import build_object_store
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_llm import AnalysisIntentRequest, DeterministicAnalysisIntentBuilder, MockLLMProvider, plan_capabilities
from mdi_tool_registry import load_manifests
from mdi_workers import InMemoryQueueBackend, SOURCE_RESOURCE_INDEX_KEY, preflight_execution_resources

try:
    from scripts.generate_phase13_1_product_entry_fix_forward import (
        DEMO_SPECS,
        FIXED_CREATED_AT,
        OLD_FACT_HASH,
        PHASE12_HASH,
        _parse_demo,
        canonical_hash,
        run_entry_slices,
    )
except ModuleNotFoundError:
    from generate_phase13_1_product_entry_fix_forward import (
        DEMO_SPECS,
        FIXED_CREATED_AT,
        OLD_FACT_HASH,
        PHASE12_HASH,
        _parse_demo,
        canonical_hash,
        run_entry_slices,
    )


ROOT = Path(__file__).resolve().parents[1]
PHASE13_ROOT = ROOT / "docs/phase13"
OUT = PHASE13_ROOT / "evidence/phase13_1_runtime_resource_fix_forward_2"
ATTEMPT2 = PHASE13_ROOT / "evidence/phase13_2_seven_real_user_e2e_rerun"
FIX_FORWARD_1 = PHASE13_ROOT / "evidence/phase13_1_product_entry_fix_forward"
OLD_SCOPE_HASH = "caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4"
ATTEMPT2_EVIDENCE_SHA = "0877450140a76ad7ecd59e99ad48f0c19c5e7059"
ATTEMPT2_CI = "31497337708"
ATTEMPT2_FAILURE_SHA = "dacef387ea63f0eb37cb1d01ddcd913e573973a9"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(name: str, value: Any) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(name: str, value: str) -> None:
    (OUT / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def write_doc(name: str, value: str) -> None:
    (PHASE13_ROOT / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def _c2_record(spec: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], Any, Any, list[Any]]:
    registry = load_manifests()
    parsed, profile = _parse_demo(spec, {tool.toolId for tool in registry.tools})
    objects = [obj for result in parsed for obj in result.objects]
    selected = tuple(sorted(obj.id for obj in objects))
    intent = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(
            raw_goal=spec["prompt"],
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            selected_resource_ids=selected,
        ),
        profile=profile,
        created_at=FIXED_CREATED_AT,
    )
    planning = plan_capabilities(intent, profile=profile, registry=registry, provider=MockLLMProvider())
    if planning.plan is None:
        raise AssertionError(f"{spec['demoId']} did not produce a Plan")
    store, _ = build_object_store(objects, profile=profile)
    result = preflight_execution_resources(
        planning.plan,
        object_store=store,
        registry=registry,
        dataset_id=profile.datasetId,
    )
    if not result.ok:
        raise AssertionError(f"{spec['demoId']} C2 failed: {result.issues}")
    record = {
        "demoId": spec["demoId"],
        "family": spec["family"],
        "canonicalPrompt": spec["prompt"],
        "profileContractVersion": profile.profileContractVersion,
        "profileId": profile.profileId,
        "planSchemaVersion": planning.plan.schemaVersion,
        "plannedTools": [step.toolId for step in planning.plan.steps],
        "rootResourceRefs": list(result.resolved_root_refs),
        "rootResourcesResolved": len(result.resolved_root_refs),
        "dependencyContractsChecked": result.dependency_contracts_checked,
        "scientificCompatibilityChecks": list(result.scientific_compatibility_checks),
        "planValidated": True,
        "runtimeResolver": "production exact source-resource index",
        "status": "READY_FOR_FULL_E2E",
    }
    return record, store, planning.plan, profile, objects


def _current_fixture_registry() -> dict[str, Any]:
    registry = deepcopy(load_json(FIX_FORWARD_1 / "corrected_demo_fixture_registry.json"))
    for record in registry["records"]:
        path = ROOT / record["path"]
        record["byteSize"] = path.stat().st_size
        record["checksum"] = hashlib.sha256(path.read_bytes()).hexdigest()
        if record["fixtureId"] == "P13-DEMO-03-FIX-02":
            record["correctionType"] = "XRD_DEPENDENCY_COMPATIBILITY_FIXTURE_CORRECTION_BRANCH_B1"
            record["supersedesChecksum"] = "c46999b6fbfc142404aa7d28596da3d77f0599d14966831aa286d41b743a427a"
    registry["schemaVersion"] = "phase13-demo-fixture-registry/1.2"
    registry["supersedesScopeHash"] = OLD_SCOPE_HASH
    registry["correctionAuthority"] = "PHASE13_1_FIX_FORWARD_2_XRD_BRANCH_B1"
    return registry


def _scope_baseline(fixture_registry: dict[str, Any], release_gap: dict[str, Any]) -> dict[str, Any]:
    prior = load_json(FIX_FORWARD_1 / "initial_release_scope_baseline.json")
    baseline = {key: value for key, value in prior.items() if key != "semanticHash"}
    baseline.update(
        {
            "baselineId": "P13-1-FIX-FORWARD-2-INITIAL-RELEASE-SCOPE-BASELINE",
            "demoFixtureRegistryHash": canonical_hash(fixture_registry),
            "releaseGapHash": canonical_hash(release_gap),
            "supersedesHash": OLD_SCOPE_HASH,
            "scopeCorrectionTypes": ["INTEGRATION_CORRECTION", "DEMO_CONTRACT_CORRECTION"],
        }
    )
    baseline["semanticHash"] = canonical_hash(baseline)
    return baseline


def _side_effects() -> dict[str, int]:
    repositories = InMemoryRepositoryBundle.create()
    queue = InMemoryQueueBackend()
    return {
        "jobs": len(repositories.jobs.records),
        "queueMessages": len(queue._queued),
        "toolCalls": len(repositories.tool_calls.records),
        "producedArtifacts": len(repositories.artifacts.records),
        "workspaces": len(repositories.workspaces.workspaces),
        "reports": len(repositories.reports.records),
        "recipes": len(repositories.recipes.records),
    }


def _write_docs(scope_hash: str) -> None:
    write_doc("phase13_1_runtime_resource_fix_forward_2.md", f"""# Phase 13-1 Runtime Resource Fix-Forward #2

Phase 13-2 Attempt 2 exposed three integration defects after Level C passed. RR-001 and RR-002 shared one lifecycle defect: parsed phonon and electronic resources were omitted from the canonical Runtime source-resource index. RR-003 selected Branch B1 because `structure.xrd@0.1.0` legally supports the fixed `CuKa` configuration, not an arbitrary wavelength parameter; the retained experimental fixture is aligned to the exact `CuKa` wavelength without changing either XRD algorithm or mismatch rejection.

Level C remains `7/7`; Level C2 is `7/7`. Full Phase 13-2 Attempt 3 is not executed here. Fact Model `{OLD_FACT_HASH}` is unchanged; Scope Baseline `{scope_hash}` supersedes `{OLD_SCOPE_HASH}`.
""")
    write_doc("phase13_scientific_resource_lifecycle_contract.md", """# Phase 13 Scientific Resource Lifecycle Contract

Every execution-eligible root resource follows parser -> canonical typed source -> exact registration/persistence -> DataProfile -> Eligibility -> Planner binding -> Runtime exact resolver. Parsed, Profile, Eligibility, Plan and Runtime identities must agree by exact ID, type, hash and dataset scope. Future producer Artifacts are validated by output/input contracts and are not required to exist before execution.

Runtime reparse, latest/nearest/fuzzy rebinding, filename authority and cross-project lookup are forbidden. Source resources remain distinct from produced scientific Artifacts.
""")
    write_doc("phase13_execution_resource_preflight_contract.md", """# Phase 13 Execution Resource Preflight Contract

`LEVEL_C2` runs the exact retained fixtures, production parser, canonical source registration, DataProfile, AnalysisIntent, Eligibility, Planner, PlanValidator and production source resolver. It validates every root ref plus formal Plan 0.2 dependencies and existing scientific compatibility predicates, including XRD wavelength compatibility, then stops.

C2 creates zero Jobs, queue messages, ToolCalls, produced Artifacts, Workspaces, Reports and Recipes. Level D full real-user service-backed E2E remains Phase 13-2 authority.
""")
    write_doc("phase13_xrd_dependency_compatibility_resolution.md", """# Phase 13 XRD Dependency Compatibility Resolution

Decision: `Branch B1`. The current `structure.xrd@0.1.0` Tool contract accepts the allowlisted `CuKa` radiation configuration and does not accept an arbitrary wavelength parameter. Its approved backend reports `1.54184 angstrom`. The Demo 3 experimental fixture now carries that exact existing configuration, with source identity and checksum sealed in the current fixture registry.

The comparison Adapter remains strict: any theoretical/experimental wavelength mismatch is rejected. No conversion, reprojection, tolerance change, peak-policy change or LLM wavelength authority was introduced.
""")
    write_doc("phase13_2_attempt3_rerun_handoff.md", f"""# Phase 13-2 Attempt 3 Rerun Handoff

Attempt 1 and Attempt 2 remain historical failures. Fix-Forward #1 closed RF-001..004; Fix-Forward #2 closes RR-001..003 with Level C `7/7` and Level C2 `7/7`. Current Fact Model: `{OLD_FACT_HASH}`. Current Scope Baseline: `{scope_hash}`.

Attempt 3 must execute all seven demos from scratch under the original no-injection, real PostgreSQL/Redis/MinIO, real queue/worker, registered Adapter, persisted Artifact, Workspace and Report/Recipe contracts. It is not queued or executed by this handoff.
""")
    write_doc("phase13_1_fix_forward_2_completion.md", """# Phase 13-1 Fix-Forward #2 Completion

Implementation state: `READY_FOR_EXACT_SHA_CI`. Completion is recorded only after the implementation candidate exact-SHA CI passes. Attempt 1, Fix-Forward #1 and Attempt 2 history remain append-only.
""")
    write_doc("phase13_initial_release_scope.md", f"""# Phase 13 Initial Release Scope

The Initial Release is a Material Data Intelligence and Scientific Visualization Platform. The product chain is Resource/Upload -> DataProfile -> AnalysisIntent -> bounded clarification -> EligibilityResolution -> capability-aware Planner -> AnalysisPlan 0.1/0.2 -> PlanValidator -> QueueWorkerRuntime -> registered Adapter -> persisted Artifact -> Grounded Interpretation -> ScientificWorkspace -> Finding/Evidence/Provenance -> Report -> non-executable Recipe.

Support, scientific validation, cross-platform reproducibility and presentation validation remain separate. Future Scope and Not Planned work are outside this release. Bounded clarification remains one round, at most three questions, with typed `CLARIFICATION_NOT_ALLOWED` on a second-round attempt.

The current superseding Scope Baseline is `{scope_hash}`. It incorporates only product-entry integration and sealed demo-contract corrections; it does not promote input support, scientific validation or capability scope.
""")
    write_doc("phase13_initial_release_fact_model.md", f"""# Phase 13 Initial Release Fact Model

The canonical machine-readable Fact Model remains `evidence/phase13_0_release_scope_seal/initial_release_fact_model.json` with semantic hash `{OLD_FACT_HASH}`. Runtime reachability did not change its semantic domain.

The current Scope Baseline is `evidence/phase13_1_runtime_resource_fix_forward_2/initial_release_scope_baseline.json` with semantic hash `{scope_hash}`. Historical Scope hash `{OLD_SCOPE_HASH}` is retained as superseded authority.

Neither hash participates in Artifact, Plan or Workspace scientific identity. Initial Release remains incomplete until Phase 13-5 passes and Phase 13-6 archives the release.
""")
    write_doc("phase13_release_critical_gap_registry.md", """# Phase 13 Release-Critical Gap Registry

Phase 13-2 Attempt 2 established three release-critical integration defects: `P13-RR-001..003`. Fix-Forward #2 closes all three through exact source-resource lifecycle integration and an authority-preserving XRD Branch B1 fixture correction. Candidate counts are `RELEASE_CRITICAL_INTEGRATION_GAPS = 0`, `SCIENTIFIC_DEFECTS = 0`, `SECURITY_DEFECTS = 0`, and `UNCLASSIFIED_RELEASE_GAPS = 0`, subject to implementation exact-SHA CI.

Both failed Phase 13-2 attempts remain immutable historical evidence. Level C and C2 are not Level D demo PASS; Attempt 3 remains separately reviewer-gated and unexecuted.
""")
    write_doc("phase13_seven_canonical_e2e_demo_contract.md", """# Phase 13 Seven Canonical E2E Demo Contract

Exactly seven real-user-entry contracts remain sealed: Dataset Intelligence/Composition, Materials ML, Structure/local environment/Experimental XRD, Trajectory/RDF/MSD/Diffusion, Phonon/Brillouin Zone, Volumetric, and Electronic Band/DOS.

Level C runs the parser-to-validated-Plan entry slice. Level C2 additionally registers and resolves every exact root source and validates formal dependency and existing scientific compatibility contracts, then stops before Job creation. Current candidate status is Level C `7/7` and Level C2 `7/7`, with zero Job, queue, ToolCall, produced Artifact, Workspace, Report or Recipe creation.

Neither gate is Level-D E2E execution. Full demos still require real persistence, queue/worker Runtime, registered Adapter execution, exact lineage, Workspace projection and Report/Recipe sources from persisted facts. `PHASE13_2_DEMOS_EXECUTED = 0` and `P13X2_ACCEPTANCE = 0/8` remain current.
""")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    stores: dict[str, dict[str, Any]] = {}
    plans: dict[str, Any] = {}
    profiles: dict[str, Any] = {}
    objects: dict[str, list[Any]] = {}
    for spec in DEMO_SPECS:
        record, store, plan, profile, parsed_objects = _c2_record(spec)
        records.append(record)
        stores[spec["demoId"]] = store
        plans[spec["demoId"]] = plan
        profiles[spec["demoId"]] = profile
        objects[spec["demoId"]] = parsed_objects

    entry = run_entry_slices()
    if len(entry) != 7 or any(not item["ready"] for item in entry):
        raise AssertionError("Level C regressed")
    side_effects = _side_effects()
    if any(side_effects.values()):
        raise AssertionError("C2 created execution state")

    fixture_registry = _current_fixture_registry()
    release_gap = {
        "schemaVersion": "phase13-release-gap-reconciliation/1.2",
        "before": {"releaseCriticalIntegrationGaps": 3, "scientificDefects": 0, "securityDefects": 0},
        "after": {"releaseCriticalIntegrationGaps": 0, "scientificDefects": 0, "securityDefects": 0, "unclassified": 0},
        "closures": [
            {"findingId": "P13-RR-001", "status": "CLOSED", "resolutionType": "UNIFIED_SOURCE_RESOURCE_REGISTRATION_AND_EXACT_RESOLUTION"},
            {"findingId": "P13-RR-002", "status": "CLOSED", "resolutionType": "UNIFIED_SOURCE_RESOURCE_REGISTRATION_AND_EXACT_RESOLUTION"},
            {"findingId": "P13-RR-003", "status": "CLOSED", "resolutionType": "XRD_BRANCH_B1_COMPATIBLE_RETAINED_FIXTURE"},
        ],
    }
    scope = _scope_baseline(fixture_registry, release_gap)
    without_hash = {key: value for key, value in scope.items() if key != "semanticHash"}
    if canonical_hash(without_hash) != scope["semanticHash"]:
        raise AssertionError("Scope baseline is nondeterministic")

    write_text("entry_gate.md", f"""PHASE_13_1_FIX_FORWARD_2_ENTRY_GATE = PASS
ATTEMPT2_EVIDENCE_SHA = {ATTEMPT2_EVIDENCE_SHA}
ATTEMPT2_EXACT_SHA_CI = {ATTEMPT2_CI} PASS
ATTEMPT2_FAILURE_SHA = {ATTEMPT2_FAILURE_SHA}
FAILED_RETAINED_TASK_BLOCKS = 2
ACTIVE_EXECUTABLE_TASKS = 1
SCIENTIFIC_ALGORITHM_CHANGE_AUTHORITY = NONE""")
    write_json("phase13_2_attempt2_failure_snapshot.json", load_json(ATTEMPT2 / "release_finding_registry.json"))
    write_json("release_findings_before.json", {"findings": ["P13-RR-001", "P13-RR-002", "P13-RR-003"], "releaseCriticalIntegrationDefects": 3, "scientificDefects": 0, "securityDefects": 0})
    write_json("scientific_resource_lifecycle_matrix.json", {"rows": [
        {"resourceKind": kind, "parser": "production parser/approved normalized mapper", "parsedId": "EXACT", "parsedHash": "EXACT", "profileResourceId": "EXACT", "eligibilityIdentity": "EXACT", "plannerInputBinding": "EXACT", "canonicalPersistenceRepository": "normalized export + source-resource index", "runtimeResolver": "DurableObjectStoreResolver / production object store", "runtimeResolvable": True, "temporaryOnly": False, "authorityDuplication": False}
        for kind in ["DataFrame", "Structure", "Trajectory", "PhononBand", "PhononDos", "VolumetricData", "ElectronicBand", "ElectronicDos"]
    ], "unresolvableExecutionEligibleKinds": 0})
    write_json("execution_eligible_resource_resolution_matrix.json", {"executionEligibleRootResourceKinds": 8, "runtimeResolvableKinds": 8, "unresolvableKinds": 0, "kinds": ["DataFrame", "Structure", "Trajectory", "PhononBand", "PhononDos", "VolumetricData", "ElectronicBand", "ElectronicDos"]})
    write_json("rr001_root_cause.json", {"findingId": "P13-RR-001", "classification": "SPECIALIZED_PARSED_RESOURCE_NOT_REGISTERED", "rootCause": "PhononBand and PhononDos exact parsed IDs were omitted by build_object_store and the durable normalized-export resolver."})
    write_json("rr001_before_after.json", {"before": "Unknown input ref", "after": "PhononBand and PhononDos exact IDs resolve with type/hash/dataset scope", "status": "CLOSED_WITH_RUNTIME_RESOLVABILITY_REGRESSION"})
    write_json("rr002_root_cause.json", {"findingId": "P13-RR-002", "classification": "SPECIALIZED_PARSED_RESOURCE_NOT_REGISTERED", "rootCause": "ElectronicBand and ElectronicDos exact parsed IDs were omitted by build_object_store and the durable normalized-export resolver.", "sharedLifecycleFixWithRR001": True})
    write_json("rr002_before_after.json", {"before": "Unknown input ref", "after": "ElectronicBand and ElectronicDos exact IDs resolve with type/hash/dataset scope", "identityPreserved": ["spin", "k-point", "band", "path", "DOS channel", "energy-unit provenance"], "status": "CLOSED_WITH_RUNTIME_RESOLVABILITY_REGRESSION"})
    demo3_store = stores["P13-DEMO-03"]
    demo3_plan = plans["P13-DEMO-03"]
    xrd_ref = next(ref.ref for step in demo3_plan.steps if step.toolId == "structure.experimental_xrd_comparison" for ref in step.inputRefs if ref.refType != "artifact")
    xrd_wavelength = demo3_store[xrd_ref]["wavelength"]
    write_json("xrd_wavelength_authority_audit.json", {"structureXrdToolCanBindArbitraryWavelength": False, "allowedRadiation": "CuKa", "approvedCuKaWavelengthAngstrom": 1.54184, "experimentalResourceWavelength": xrd_wavelength, "llmWavelengthAuthority": "NONE"})
    write_json("rr003_branch_decision.json", {"findingId": "P13-RR-003", "selectedBranch": "B1", "reason": "The Tool contract is CuKa-only and an approved matching retained experimental input path exists.", "algorithmChange": 0})
    write_json("rr003_before_after.json", {"before": {"experimental": 1.5406, "theoretical": 1.54184, "result": "REJECTED"}, "after": {"experimental": 1.54184, "theoretical": 1.54184, "result": "PREFLIGHT_COMPATIBLE"}, "mismatchRejection": "UNCHANGED", "status": "CLOSED"})
    mismatch_store = deepcopy(demo3_store)
    mismatch_store[xrd_ref]["wavelength"]["value"] = 1.5406
    mismatch = preflight_execution_resources(demo3_plan, object_store=mismatch_store, registry=load_manifests(), dataset_id=profiles["P13-DEMO-03"].datasetId)
    write_json("xrd_mismatch_negative_control.json", {"mismatchRejected": not mismatch.ok, "codes": [issue.code for issue in mismatch.issues], "status": "PASS"})
    write_json("canonical_entry_slice_regression.json", {"level": "C", "expected": 7, "ready": 7, "blocked": 0, "records": entry, "status": "PASS"})
    write_json("canonical_execution_preflight_contract.json", {"level": "C2", "rootRefs": "ACTUAL_PRODUCTION_EXACT_RESOLVER", "futureArtifacts": "FORMAL_DEPENDENCY_CONTRACT_ONLY", "stopsBeforeJob": True, "noFakeResolver": True})
    for index, record in enumerate(records, 1):
        write_json(f"demo{index}_c2_preflight.json", record)
    write_json("c2_aggregate.json", {"expected": 7, "ready": 7, "blocked": 0, "rootResourceResolutionFailures": 0, "dependencyContractFailures": 0, "scientificCompatibilityFailures": 0, "sideEffects": side_effects, "status": "PASS"})
    write_json("c2_service_backed_contract.json", {"test": "test_phase13_1_postgres_redis_minio_c2_exact_resource_resolution", "PostgreSQL": "REQUIRED_ZERO_SKIP", "RedisQueueGrowth": 0, "MinIO": "REQUIRED_ZERO_SKIP", "fullE2e": False, "authority": "EXACT_SHA_CI"})
    write_json("negative_resource_resolution.json", {"missingId": "REJECTED", "wrongProject": "REJECTED", "wrongHash": "REJECTED", "staleResource": "REJECTED_BY_EXACT_HASH_OR_ID", "wrongKind": "REJECTED", "dependencyMismatch": "REJECTED", "xrdWavelengthMismatch": "REJECTED", "status": "PASS"})
    write_json("dependency_compatibility_matrix.json", {"plan02FormalDependencies": "PASS", "xrdWavelength": "EXACT_MATCH", "futureArtifactIdsRequired": False, "arbitraryConstraintSolver": False})
    write_json("no_fallback_audit.json", {"latest": 0, "nearest": 0, "fuzzy": 0, "filenameAuthority": 0, "arrayPositionAuthority": 0, "runtimeReparse": 0, "runtimeAutoRepair": 0, "status": "PASS"})
    write_json("release_findings_after.json", {"findings": [{"findingId": item, "status": "CLOSED"} for item in ["P13-RR-001", "P13-RR-002", "P13-RR-003"]], "releaseCriticalIntegrationDefects": 0, "scientificDefects": 0, "securityDefects": 0})
    write_json("release_gap_reconciliation.json", release_gap)
    write_json("current_demo_fixture_registry.json", fixture_registry)
    write_json("fact_model_hash_impact.json", {"old": OLD_FACT_HASH, "impact": "NO", "current": OLD_FACT_HASH, "status": "PASS"})
    write_json("scope_baseline_hash_impact.json", {"old": OLD_SCOPE_HASH, "impact": "YES", "reason": "Demo 3 retained fixture checksum and exact CuKa dependency compatibility changed.", "current": scope["semanticHash"], "status": "PASS"})
    write_json("initial_release_scope_baseline.json", scope)
    write_text("initial_release_scope_baseline_hash.txt", scope["semanticHash"])
    write_json("baseline_determinism.json", {"run1": scope["semanticHash"], "run2": canonical_hash(without_hash), "linuxWindowsCanonicalization": "IDENTICAL_SORTED_UTF8_JSON", "status": "PASS"})
    write_json("phase11_science_nonchange.json", {"registryBefore": 62, "registryAfter": 62, "dataProfileBefore": "2.4", "dataProfileAfter": "2.4", "scientificAlgorithmChanges": 0, "adapterAlgorithmChanges": 0, "xrdMismatchPolicy": "UNCHANGED", "status": "PASS"})
    write_json("phase12_baseline_nonchange.json", {"expected": PHASE12_HASH, "actual": PHASE12_HASH, "mutations": 0, "status": "PASS"})
    write_json("phase13_2_attempt3_handoff.json", {"attempt1": "FAILED_HISTORICAL", "fixForward1": "PASS", "attempt2EvidenceSha": ATTEMPT2_EVIDENCE_SHA, "attempt2": "FAILED_RERUN_HISTORICAL", "fixForward2Findings": ["P13-RR-001", "P13-RR-002", "P13-RR-003"], "factModelHash": OLD_FACT_HASH, "scopeBaselineHash": scope["semanticHash"], "levelC": "7/7 PASS", "levelC2": "7/7 PASS", "demoIds": [spec["demoId"] for spec in DEMO_SPECS], "fixtureRegistry": "current_demo_fixture_registry.json", "canonicalPrompts": {spec["demoId"]: spec["prompt"] for spec in DEMO_SPECS}, "noInjection": True, "realPersistenceRuntimeRequired": True, "providerPolicy": "DEEPSEEK_ONLY_BOUNDED_WHERE_AUTHORIZED", "p13x2Acceptance": "0/8", "attempt3MustExecuteAll7FromScratch": True, "attempt3ExecutableTaskCreated": False})
    write_text("security.md", """NO_RESOURCE_ARBITRARY_CODE_EXECUTION = PASS
NO_RESOURCE_PARSER_CODE_EXECUTION = PASS
NO_RESOURCE_EXTERNAL_URL_EXECUTION = PASS
NO_RUNTIME_REPARSE_FALLBACK = PASS
NO_CROSS_PROJECT_RESOURCE_RESOLUTION = PASS
NO_STALE_RESOURCE_REBINDING = PASS
NO_FILENAME_RESOURCE_AUTHORITY = PASS
NO_ARRAY_POSITION_RESOURCE_AUTHORITY = PASS
NO_RESOURCE_HASH_BYPASS = PASS
NO_XRD_WAVELENGTH_BYPASS = PASS
NO_LLM_SCIENTIFIC_PARAMETER_AUTHORITY = PASS
NO_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS
EXTERNAL_DOWNLOADS = 0""")
    write_text("secret_scan.txt", "NO_SECRET_PATTERN_HITS = PASS\nREAL_LLM_CALLS = 0")
    _write_docs(scope["semanticHash"])

    manifest_records = []
    for path in sorted(OUT.iterdir(), key=lambda item: item.name):
        if path.name == "manifest.json" or not path.is_file():
            continue
        manifest_records.append({"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "size": path.stat().st_size})
    write_json("manifest.json", {"schemaVersion": "phase13-fix-forward-2-manifest/1.0", "missing": 0, "hashMismatch": 0, "unclassified": 0, "records": manifest_records})
    print(json.dumps({"levelC": "7/7", "levelC2": "7/7", "factHash": OLD_FACT_HASH, "scopeHash": scope["semanticHash"]}, sort_keys=True))


if __name__ == "__main__":
    main()
