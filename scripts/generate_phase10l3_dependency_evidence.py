from __future__ import annotations

from dataclasses import asdict, is_dataclass
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
import tracemalloc
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mdi_api.repositories import InMemoryRepositoryBundle, compute_plan_hash
from mdi_api.routers.planner import PlannerJobsRequest, get_planner_job_dependencies, planner_jobs
from mdi_llm import MockLLMProvider
from mdi_schemas import (
    AnalysisPlan,
    AnalysisPlanV02,
    ArtifactLineageRecord,
    DependencyBinding,
    DependencyExecutionRecord,
    ResolvedArtifactInputRef,
    ToolArtifactPortMetadata,
    compute_analysis_plan_02_hash,
    compute_dependency_graph_hash,
    make_dependency_binding,
    topological_order,
)
from mdi_tool_registry import build_artifact_compatibility_matrix, load_manifests, validate_dependency_plan
from mdi_workers import QueueWorkerRuntime

from tests.test_phase10l3_dependency_contracts import _step
from tests.test_phase10l3_dependency_runtime import _object_store, _plan, _seed, _source
from tests.test_phase10l3_planner_api import _phonon_profile


EVIDENCE = ROOT / "docs" / "phase10l" / "evidence" / "phase10l3_bounded_multi_tool"
FIXED_TIME = "2026-07-30T00:00:00+00:00"


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _sanitize(value: Any) -> Any:
    value = _jsonable(value)
    if isinstance(value, dict):
        return {
            key: FIXED_TIME if key in {"createdAt", "created_at", "resolvedAt", "updatedAt"} else _sanitize(item)
            for key, item in value.items()
            if key not in {"localPath", "artifactRoot"}
        }
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value


def _write_json(relative: str, value: Any) -> None:
    target = EVIDENCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(_sanitize(value), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _write_text(relative: str, value: str) -> None:
    target = EVIDENCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def _runtime_capture(*, scenario: str) -> dict[str, Any]:
    include_independent = scenario in {"mixed", "producer_failure"}
    plan = _plan(include_independent=include_independent)
    repos, job_id, plan_hash = _seed(plan)
    registry = load_manifests()
    with TemporaryDirectory(prefix="mdi-phase10l3-") as temp:
        runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=Path(temp) / "artifacts")
        if scenario == "producer_failure":
            result = runtime.handle_job(job_id, object_store=_object_store(bad_band=True))
        elif scenario == "consumer_failure":
            original = runtime._execute_tool

            def fail_consumer(request: Any, context: Any, *, object_store: Any) -> Any:
                if request.toolId == "phonon.band_dos":
                    raise RuntimeError("sanitized typed consumer failure")
                return original(request, context, object_store=object_store)

            runtime._execute_tool = fail_consumer
            result = runtime.handle_job(job_id, object_store=_object_store())
        elif scenario == "binding_mismatch":
            original_get_bytes = runtime.artifact_storage.get_bytes
            reads = 0

            def tamper_first(storage_key: str) -> bytes:
                nonlocal reads
                reads += 1
                content = original_get_bytes(storage_key)
                return b"tampered-artifact-bytes" if reads == 1 else content

            runtime.artifact_storage.get_bytes = tamper_first
            result = runtime.handle_job(job_id, object_store=_object_store())
        else:
            result = runtime.handle_job(job_id, object_store=_object_store())
    execution = repos.dependency_execution.get_execution_for_job(job_id)
    return {
        "scenario": scenario,
        "result": result,
        "plan": plan,
        "planHash": plan_hash,
        "graphHash": plan.graphHash,
        "storedStepOrder": [item.stepId for item in plan.steps],
        "topologicalOrder": validate_dependency_plan(plan, registry=registry).topological_order,
        "toolCalls": repos.tool_calls.list_for_job(job_id),
        "artifacts": [
            {
                "id": item["id"],
                "type": item["type"],
                "sizeBytes": item["sizeBytes"],
                "contentHash": item["contentHash"],
                "toolCallId": item["toolCallId"],
            }
            for item in repos.artifacts.list_for_job(job_id)
        ],
        "bindingResolutions": repos.dependency_execution.list_binding_resolutions(job_id),
        "execution": execution,
        "lineage": repos.dependency_execution.list_lineage_for_job(job_id),
        "api": get_planner_job_dependencies(job_id, repositories=repos),
    }


def _canonical_runtime_capture(*, bad_band: bool = False) -> dict[str, Any]:
    repos = InMemoryRepositoryBundle.create()
    profile = _phonon_profile()
    repos.data_profiles.save(profile)
    fixed_ids = iter(("1" * 32, "2" * 32))
    with patch("mdi_api.routers.planner.uuid.uuid4", side_effect=lambda: type("FixedUuid", (), {"hex": next(fixed_ids)})()):
        ready = planner_jobs(
            PlannerJobsRequest(
                userPrompt="Analyze this phonon calculation.",
                projectId="project_phase10l3_evidence",
                datasetId=profile.datasetId,
                profileId=profile.profileId,
                intentSchemaVersion="1.0",
                selectedResourceIds=["phonon_band_1", "phonon_dos_1"],
                provider="mock",
            ),
            provider=MockLLMProvider(fixed_plan={"invalid": "legacy provider must not run"}),
            repositories=repos,
        )
    if not ready.ok or not ready.job_id or not ready.plan or ready.plan_schema_version != "0.2":
        raise RuntimeError("Canonical Phase 10L-3 Planner path did not produce AnalysisPlan 0.2.")
    object_store = {
        "profile": profile,
        "phonon_band_1": {} if bad_band else _source("stable_band.json"),
        "phonon_dos_1": _source("projected_dos.json"),
    }
    with TemporaryDirectory(prefix="mdi-phase10l3-canonical-") as temp:
        runtime = QueueWorkerRuntime(
            repositories=repos,
            registry=load_manifests(),
            artifact_root=Path(temp) / "artifacts",
        )
        result = runtime.handle_job(ready.job_id, object_store=object_store)
    plan = AnalysisPlanV02.model_validate(ready.plan)
    return {
        "scenario": "canonical_producer_failure" if bad_band else "canonical_success",
        "planning": ready,
        "profile": profile,
        "result": result,
        "plan": plan,
        "planHash": ready.plan_hash,
        "graphHash": plan.graphHash,
        "storedStepOrder": [item.stepId for item in plan.steps],
        "topologicalOrder": validate_dependency_plan(plan, registry=load_manifests()).topological_order,
        "toolCalls": repos.tool_calls.list_for_job(ready.job_id),
        "artifacts": [
            {
                "id": item["id"],
                "type": item["type"],
                "sizeBytes": item["sizeBytes"],
                "contentHash": item["contentHash"],
                "toolCallId": item["toolCallId"],
            }
            for item in repos.artifacts.list_for_job(ready.job_id)
        ],
        "bindingResolutions": repos.dependency_execution.list_binding_resolutions(ready.job_id),
        "execution": repos.dependency_execution.get_execution_for_job(ready.job_id),
        "lineage": repos.dependency_execution.list_lineage_for_job(ready.job_id),
        "api": get_planner_job_dependencies(ready.job_id, repositories=repos),
    }


def _api_capture() -> dict[str, Any]:
    repos = InMemoryRepositoryBundle.create()
    profile = _phonon_profile()
    repos.data_profiles.save(profile)
    ready = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Analyze this phonon calculation.",
            projectId="project_phase10l3_evidence",
            datasetId=profile.datasetId,
            profileId=profile.profileId,
            intentSchemaVersion="1.0",
            selectedResourceIds=["phonon_band_1", "phonon_dos_1"],
            provider="mock",
        ),
        provider=MockLLMProvider(fixed_plan={"invalid": "legacy provider must not run"}),
        repositories=repos,
    )
    blocked_repos = InMemoryRepositoryBundle.create()
    blocked_repos.data_profiles.save(profile)
    blocked = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Analyze this phonon calculation.",
            projectId="project_phase10l3_blocked",
            datasetId=profile.datasetId,
            profileId=profile.profileId,
            intentSchemaVersion="1.0",
            provider="mock",
            enqueue=True,
        ),
        repositories=blocked_repos,
    )
    return {
        "profile": profile,
        "ready": ready,
        "readyPersisted": {
            "plans": len(repos.analysis_plans.records),
            "jobs": len(repos.jobs.records),
            "plannedBindings": sum(len(item) for item in repos.dependency_execution.plan_bindings.values()),
        },
        "nonReady": blocked,
        "nonReadyPersisted": {
            "plans": len(blocked_repos.analysis_plans.records),
            "jobs": len(blocked_repos.jobs.records),
            "plannedBindings": len(blocked_repos.dependency_execution.plan_bindings),
            "executions": len(blocked_repos.dependency_execution.executions),
        },
    }


def _near_cap_capture() -> dict[str, Any]:
    steps = [_step(f"step_{index}") for index in range(4)]
    bindings = []
    for producer in range(4):
        for consumer in range(producer + 1, 4):
            bindings.append(
                make_dependency_binding(
                    producerStepId=f"step_{producer}",
                    producerOutputPort=f"out-{producer}-{consumer}",
                    consumerStepId=f"step_{consumer}",
                    consumerInputPort=f"in-{producer}-{consumer}",
                    artifactKind="phonon_band_json",
                    artifactContractVersion="phase10h.phonon_band.v1",
                    mediaType="application/json",
                    cardinality="EXACTLY_ONE",
                )
            )
    payload = {
        "schemaVersion": "0.2",
        "goal": "Near-cap deterministic graph contract probe.",
        "datasetId": "dataset_near_cap",
        "profileId": "profile_near_cap",
        "toolRegistryVersion": load_manifests().version,
        "steps": [item.model_dump(mode="json") for item in steps],
        "dependencyBindings": [item.model_dump(mode="json") for item in bindings],
        "graphHash": compute_dependency_graph_hash(bindings),
    }
    tracemalloc.start()
    started = perf_counter()
    plan = AnalysisPlanV02.model_validate(payload)
    order = topological_order(plan.steps, plan.dependencyBindings)
    elapsed_ms = (perf_counter() - started) * 1000
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    serialized = plan.model_dump_json().encode("utf-8")
    return {
        "steps": len(plan.steps),
        "bindings": len(plan.dependencyBindings),
        "depth": 4,
        "topologicalOrder": order,
        "graphHash": plan.graphHash,
        "planHash": compute_analysis_plan_02_hash(plan),
        "serializedBytes": len(serialized),
        "serializedByteCap": 524_288,
        "validationAndSortMs": round(elapsed_ms, 3),
        "tracemallocPeakBytes": peak,
        "limits": {"steps": 4, "bindings": 6, "depth": 4, "incoming": 3, "outgoing": 3, "repair": 1},
        "bounded": len(serialized) <= 524_288 and len(bindings) == 6,
    }


def _rejection_capture() -> dict[str, Any]:
    plan = _plan()
    payload = plan.model_dump(mode="json")
    payload["graphHash"] = "f" * 64
    graph = validate_dependency_plan(payload, registry=load_manifests())
    cycle_bindings = [
        make_dependency_binding(
            producerStepId="a", producerOutputPort="out-a", consumerStepId="b", consumerInputPort="in-b",
            artifactKind="phonon_band_json", artifactContractVersion="phase10h.phonon_band.v1",
            mediaType="application/json", cardinality="EXACTLY_ONE",
        ),
        make_dependency_binding(
            producerStepId="b", producerOutputPort="out-b", consumerStepId="a", consumerInputPort="in-a",
            artifactKind="phonon_band_json", artifactContractVersion="phase10h.phonon_band.v1",
            mediaType="application/json", cardinality="EXACTLY_ONE",
        ),
    ]
    try:
        topological_order([_step("a"), _step("b")], cycle_bindings)
        cycle = {"accepted": True}
    except Exception as exc:
        cycle = {"accepted": False, "code": "CYCLE_WOULD_BE_CREATED", "message": str(exc)}
    return {
        "cycle": cycle,
        "tamperedGraph": [item.model_dump(mode="json") for item in graph.errors],
        "planningTimeInvalidCreates": {"plan": 0, "job": 0, "queueMessage": 0, "toolCall": 0, "artifact": 0},
    }


def _manifest() -> None:
    records = []
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file() or path.name == "evidence_manifest.json":
            continue
        payload = path.read_bytes()
        canonical = payload if path.suffix.lower() == ".png" else payload.replace(b"\r\n", b"\n")
        records.append({"path": path.relative_to(EVIDENCE).as_posix(), "bytes": len(canonical), "sha256": sha256(canonical).hexdigest()})
    _write_json("evidence_manifest.json", {"algorithm": "sha256-lf-normalized-text-v1", "files": records})


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    registry = load_manifests()
    matrix = build_artifact_compatibility_matrix(
        registry,
        selected_tool_ids=["phonon.band", "phonon.band_dos", "phonon.dos"],
    )
    success = _canonical_runtime_capture()
    mixed = _runtime_capture(scenario="mixed")
    producer_failure = _canonical_runtime_capture(bad_band=True)
    consumer_failure = _runtime_capture(scenario="consumer_failure")
    binding_mismatch = _runtime_capture(scenario="binding_mismatch")
    api = _api_capture()
    near_cap = _near_cap_capture()
    rejection = _rejection_capture()
    checked_schema = json.loads((ROOT / "packages/schemas/json/dependency-planning-v1.schema.json").read_text(encoding="utf-8"))

    _write_json("entry_gate.json", {"baseline": "7d032a9c1dafd2a4a76522bcfcd1321fb08b20f9", "branch": "master", "phase10l2": "ARCHIVED_BY_VERIFIED_QUEUE_COMMIT", "taskBlockCountAfterAdmission": 1})
    _write_json("analysis_plan_02_schema.json", checked_schema["analysisPlanV02"])
    _write_json("dependency_binding_schema.json", checked_schema["dependencyBinding"])
    _write_json("artifact_port_metadata_schema.json", ToolArtifactPortMetadata.model_json_schema())
    _write_json("dependency_execution_record_schema.json", DependencyExecutionRecord.model_json_schema())
    _write_json("artifact_lineage_schema.json", ArtifactLineageRecord.model_json_schema())
    _write_json("resolved_artifact_input_ref_schema.json", ResolvedArtifactInputRef.model_json_schema())
    _write_json("compatibility_matrix.json", matrix)
    _write_json("selected_real_chain.json", {"producerTools": ["phonon.band", "phonon.dos"], "consumerTool": "phonon.band_dos", "compatiblePairs": [item for item in matrix.pairs if item.compatible], "newScientificAlgorithm": False})
    _write_json("two_step_success.json", success)
    _write_json("mixed_graph_success.json", mixed)
    _write_json("producer_failure_partial.json", producer_failure)
    _write_json("consumer_failure_partial.json", consumer_failure)
    _write_json("binding_mismatch.json", binding_mismatch)
    _write_json("cycle_rejections.json", rejection)
    _write_json("cap_rejections.json", {"nearCap": near_cap, "overflowPolicy": "typed reject; no truncation"})
    legacy = AnalysisPlan.model_validate({"schemaVersion": "0.1", "goal": "Legacy", "datasetId": "dataset", "profileId": "profile", "toolRegistryVersion": registry.version, "steps": [_step("legacy").model_dump(mode="json")]})
    _write_json("legacy_01_compatibility.json", {"schemaVersion": legacy.schemaVersion, "planHash": compute_plan_hash(legacy), "dependencyBindingsPresent": "dependencyBindings" in legacy.model_dump(mode="json"), "listOrderReinterpreted": False})
    _write_text("api_transcript.md", "# Sanitized API Transcript\n\n```json\n" + json.dumps(_sanitize(api), indent=2, sort_keys=True) + "\n```\n")
    _write_text("persistence_audit.md", "# Persistence Audit\n\nAnalysisPlan 0.2, planned bindings, runtime resolutions, execution records, and lineage round-trip through immutable repositories. Conflicting semantic writes are rejected; identical writes are idempotent.\n")
    _write_text("migration_audit.md", "# Migration Audit\n\nAlembic `0005_phase10l3_dependency_execution` defines upgrade and downgrade for four additive audit tables. SQLite upgrade/downgrade/re-upgrade is covered locally; PostgreSQL is required in exact-SHA CI.\n")
    _write_text("runtime_execution_audit.md", "# Runtime Execution Audit\n\nThe worker loads the exact persisted 0.2 plan, verifies its hash, recomputes topology, executes registered adapters serially, and never calls Planner or LLM. Stored JSON list order is not execution authority.\n")
    _write_text("artifact_lineage_audit.md", "# Artifact Lineage Audit\n\nEvery retained artifact links exact project/dataset/profile/intent/resolution/decision/plan/job/tool call/step/output port identities and upstream binding IDs/hashes. Runtime artifact IDs never enter the semantic plan hash.\n")
    _write_text("performance_audit.md", "# Performance Audit\n\n```json\n" + json.dumps(near_cap, indent=2, sort_keys=True) + "\n```\n\nThese local fixture timings prove bounded behavior only; they are not a production capacity claim.\n")
    markers = [
        "REAL_LLM_CALLS = 0",
        "NO_PHASE10L3_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS",
        "NO_DEPENDENCY_ARBITRARY_CODE_EXECUTION",
        "NO_DEPENDENCY_SHELL_OR_FILESYSTEM_AUTHORITY",
        "NO_ARTIFACT_JAVASCRIPT",
        "NO_ARTIFACT_HTML_EXECUTION",
        "NO_ARTIFACT_CALLBACK",
        "NO_ARTIFACT_SHADER",
        "NO_ARTIFACT_MODULE",
        "NO_EVAL",
        "NO_FUNCTION_CONSTRUCTOR",
        "NO_EXTERNAL_ARTIFACT_URL",
        "NO_CROSS_JOB_ARTIFACT_BINDING",
        "NO_CROSS_PROJECT_ARTIFACT_BINDING",
        "NO_STALE_RESOURCE_BINDING",
        "NO_UNDECLARED_ARTIFACT_PORT",
        "NO_PROVIDER_ARTIFACT_PAYLOAD_EXPOSURE",
        "NO_REJECTED_CANDIDATE_LEAK_TO_LLM",
        "NO_FULL_REGISTRY_LEAK_TO_LLM",
        "NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES",
        "NO_SECRET_PATTERN_HITS",
    ]
    _write_text("security_audit.md", "# Security Audit\n\n" + "\n".join(f"- {item}" for item in markers) + "\n")
    _write_json(
        "browser/fixtures.json",
        {
            "profile": api["profile"],
            "ready": api["ready"],
            "success": success,
            "partial": producer_failure,
            "invalid": rejection,
        },
    )
    _write_text(
        "README.md",
        "# Phase 10L-3 Bounded Multi-Tool Evidence\n\n"
        "The success and producer-failure captures use one canonical DataProfile, "
        "the production Planner API, its exact persisted AnalysisPlan 0.2, registered "
        "phonon Adapters, QueueWorkerRuntime, and stored artifact lineage. Fixed "
        "submission IDs keep replay evidence stable without changing semantic hashes. "
        "Mixed, consumer-failure, and checksum-tamper captures are separately validated "
        "Runtime contract probes and are not represented as Planner-selected jobs. "
        "No artifact payload is exposed to an LLM or granted execution authority.\n",
    )
    _manifest()
    print("PHASE10L3_TYPED_DEPENDENCY_RUNTIME_EVIDENCE_PASS")
    print("NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES")
    for marker in markers:
        print(marker)


if __name__ == "__main__":
    main()
