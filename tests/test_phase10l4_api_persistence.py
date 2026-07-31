from __future__ import annotations

import hashlib
import json
from pathlib import Path
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from pydantic import ValidationError
from sqlalchemy import create_engine, inspect

from mdi_api.artifact_storage import LocalFileArtifactStorage, S3CompatibleArtifactStorage
from mdi_api.db import metadata
from mdi_api.repositories import InMemoryRepositoryBundle, SqlAlchemyRepositoryBundle, compute_plan_hash
from mdi_api.routers.planner import (
    PlannerJobsRequest,
    PlannerInterpretationRequest,
    create_planner_job_interpretation,
    get_planner_interpretation,
    get_planner_interpretation_evidence,
    list_planner_job_interpretations,
    planner_jobs,
)
from mdi_llm import MockLLMProvider
from mdi_tool_registry import load_manifests
from mdi_workers import InMemoryQueueBackend, QueueWorkerRuntime
import mdi_api.routers.planner as planner_router


def _plan() -> dict:
    return {
        "schemaVersion": "0.1",
        "goal": "Summarize exact dataset statistics.",
        "datasetId": "dataset_l4_api",
        "profileId": "profile_l4_api",
        "toolRegistryVersion": "1.0",
        "assumptions": [],
        "warnings": [],
        "steps": [{
            "stepId": "step_summary",
            "toolId": "table.numeric_summary",
            "purpose": "Compute bounded numeric statistics.",
            "reason": "The intent requests dataset statistics.",
            "inputRefs": [{
                "refType": "normalized_object",
                "ref": "table_l4",
                "datasetId": "dataset_l4_api",
                "objectId": "table_l4",
                "objectType": "DataFrame",
            }],
            "params": {},
            "output": {"artifactTypes": ["table_json"]},
        }],
        "expectedArtifacts": [{"name": "numeric-summary", "type": "table_json", "fromStepId": "step_summary"}],
    }


def _seed_api_source(tmp_path: Path, *, status: str = "completed", artifact_type: str = "table_json"):
    repos = InMemoryRepositoryBundle.create()
    storage = LocalFileArtifactStorage(tmp_path / "artifacts")
    runtime = QueueWorkerRuntime(
        repositories=repos,
        artifact_storage=storage,
        queue_backend=InMemoryQueueBackend(),
        artifact_root=tmp_path / "artifacts",
    )
    plan = _plan()
    plan_hash = compute_plan_hash(plan)
    repos.analysis_plans.save_plan({
        "id": "plan_l4_api",
        "projectId": "project_l4_api",
        "datasetId": "dataset_l4_api",
        "profileId": "profile_l4_api",
        "jobId": "job_l4_api",
        "analysisPlan": plan,
        "planHash": plan_hash,
        "validationStatus": "validated",
    })
    repos.jobs.save({
        "id": "job_l4_api",
        "jobId": "job_l4_api",
        "projectId": "project_l4_api",
        "datasetId": "dataset_l4_api",
        "planId": "plan_l4_api",
        "status": status,
    })
    repos.tool_calls.save({
        "id": "tool_call_l4_api",
        "jobId": "job_l4_api",
        "stepId": "step_summary",
        "toolId": "table.numeric_summary",
        "status": "completed",
        "params": {},
        "artifactIds": ["artifact_l4_api"],
    })
    payload = {
        "rowCount": 4,
        "columns": [{"name": "formation_energy", "dtype": "float64", "missingCount": 1, "nonNullCount": 3}],
        "numericColumns": {
            "formation_energy": {"count": 3, "mean": -1.1, "std": 0.2, "min": -1.3, "median": -1.1, "max": -0.9}
        },
        "categoricalColumns": {},
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    stored = storage.put_bytes("jobs/job_l4_api/numeric-summary.json", raw, content_type="application/json")
    repos.artifacts.save({
        "id": "artifact_l4_api",
        "artifactId": "artifact_l4_api",
        "projectId": "project_l4_api",
        "datasetId": "dataset_l4_api",
        "jobId": "job_l4_api",
        "toolCallId": "tool_call_l4_api",
        "type": artifact_type,
        "name": "numeric-summary",
        "version": "1",
        "storageKey": stored.storage_key,
        "storageProvider": "local",
        "sizeBytes": stored.size_bytes,
        "contentType": stored.content_type,
        "contentHash": stored.sha256,
        "sha256": stored.sha256,
        "metadata": {
            "toolId": "table.numeric_summary",
            "toolVersion": "0.1.0",
            "adapterVersion": "0.1.0",
            "inputHashes": [],
            "createdAt": "2026-07-30T00:00:00Z",
            "provenance": {"planId": "plan_l4_api", "planHash": plan_hash},
        },
    })
    return repos, runtime, plan_hash


def _seed_dependency_source(tmp_path: Path):
    from tests.test_phase10l3_dependency_runtime import _source
    from tests.test_phase10l3_planner_api import _phonon_profile

    repos = InMemoryRepositoryBundle.create()
    profile = _phonon_profile()
    repos.data_profiles.save(profile)
    planned = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Analyze this phonon calculation.",
            projectId="project_l4_dependency_api",
            datasetId=profile.datasetId,
            profileId=profile.profileId,
            intentSchemaVersion="1.0",
            selectedResourceIds=["phonon_band_1", "phonon_dos_1"],
            provider="mock",
        ),
        provider=MockLLMProvider(fixed_plan={"invalid": "legacy path must not run"}),
        repositories=repos,
    )
    assert planned.ok and planned.job_id and planned.plan_hash
    runtime = QueueWorkerRuntime(
        repositories=repos,
        registry=load_manifests(),
        artifact_root=tmp_path / "artifacts",
    )
    result = runtime.handle_job(
        planned.job_id,
        object_store={
            "phonon_band_1": _source("stable_band.json"),
            "phonon_dos_1": _source("projected_dos.json"),
        },
    )
    assert result.status == "completed"
    return repos, runtime, planned.job_id, planned.plan_hash


def test_interpretation_api_create_read_is_idempotent_and_read_only(tmp_path: Path) -> None:
    repos, runtime, plan_hash = _seed_api_source(tmp_path)
    before = (len(repos.jobs.records), len(repos.tool_calls.records), len(repos.artifacts.records))
    request = PlannerInterpretationRequest(mode="DETERMINISTIC", expectedPlanHash=plan_hash, idempotencyKey="l4-api")

    first = create_planner_job_interpretation("job_l4_api", request, repositories=repos, queue_runtime=runtime)
    second = create_planner_job_interpretation("job_l4_api", request, repositories=repos, queue_runtime=runtime)

    assert first["outcome"] == "INTERPRETATION_READY"
    assert first["interpretationId"] == second["interpretationId"]
    assert first["claims"] and all(claim["supportingEvidenceIds"] for claim in first["claims"])
    assert first["noExecution"] == {
        "toolCallCreated": False,
        "planCreated": False,
        "jobCreated": False,
        "enqueued": False,
        "recommendationExecutionAuthorized": False,
    }
    assert before == (len(repos.jobs.records), len(repos.tool_calls.records), len(repos.artifacts.records))
    stored = get_planner_interpretation(first["interpretationId"], repositories=repos)
    evidence = get_planner_interpretation_evidence(first["interpretationId"], repositories=repos)
    listed = list_planner_job_interpretations("job_l4_api", repositories=repos)
    assert stored["interpretation"]["interpretationHash"] == first["interpretation"]["interpretationHash"]
    assert evidence["bundleHash"] == first["bundleHash"]
    assert listed["count"] == 1


def test_concurrent_idempotent_requests_execute_interpreter_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repos, runtime, plan_hash = _seed_api_source(tmp_path / "concurrent")
    request = PlannerInterpretationRequest(
        mode="DETERMINISTIC",
        expectedPlanHash=plan_hash,
        idempotencyKey="concurrent-l4-api",
    )
    real_interpret = planner_router.deterministic_interpret
    calls = 0
    calls_lock = threading.Lock()

    def delayed_interpret(*args: object, **kwargs: object):
        nonlocal calls
        with calls_lock:
            calls += 1
        time.sleep(0.05)
        return real_interpret(*args, **kwargs)

    monkeypatch.setattr(planner_router, "deterministic_interpret", delayed_interpret)
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(
            lambda _index: create_planner_job_interpretation(
                "job_l4_api",
                request,
                repositories=repos,
                queue_runtime=runtime,
            ),
            range(2),
        ))

    assert calls == 1
    assert responses[0]["interpretationId"] == responses[1]["interpretationId"]
    assert len(repos.interpretations.list_for_job("job_l4_api")) == 1
    assert len(repos.interpretations.list_runs_for_job("job_l4_api")) == 1


def test_interpretation_api_terminal_integrity_and_unsupported_gates(tmp_path: Path) -> None:
    repos, runtime, plan_hash = _seed_api_source(tmp_path / "running", status="running")
    result = create_planner_job_interpretation(
        "job_l4_api", PlannerInterpretationRequest(expectedPlanHash=plan_hash), repositories=repos, queue_runtime=runtime
    )
    assert result["outcome"] == "SOURCE_NOT_TERMINAL"
    assert repos.interpretations.records == {}

    repos, runtime, plan_hash = _seed_api_source(tmp_path / "integrity")
    result = create_planner_job_interpretation(
        "job_l4_api", PlannerInterpretationRequest(expectedPlanHash="0" * 64), repositories=repos, queue_runtime=runtime
    )
    assert result["outcome"] == "SOURCE_INTEGRITY_FAILED"
    assert result["claims"] == []

    repos, runtime, plan_hash = _seed_api_source(tmp_path / "legacy-failed", status="failed")
    partial = create_planner_job_interpretation(
        "job_l4_api", PlannerInterpretationRequest(expectedPlanHash=plan_hash), repositories=repos, queue_runtime=runtime
    )
    assert partial["outcome"] == "INTERPRETATION_READY_WITH_LIMITS"
    assert partial["partialResultState"] is True
    assert partial["limitations"]


def test_strict_provider_selection_failure_is_persisted_and_idempotent(tmp_path: Path) -> None:
    repos, runtime, plan_hash = _seed_api_source(tmp_path / "provider-failure")
    request = PlannerInterpretationRequest(
        mode="STRICT_PROVIDER",
        expectedPlanHash=plan_hash,
        idempotencyKey="provider-failure-key",
        provider="unsupported-provider",
        model="bounded-test-model",
    )

    first = create_planner_job_interpretation(
        "job_l4_api", request, repositories=repos, queue_runtime=runtime, provider=object()
    )
    second = create_planner_job_interpretation(
        "job_l4_api", request, repositories=repos, queue_runtime=runtime, provider=object()
    )

    assert first["outcome"] == "PROVIDER_FAILED"
    assert first["execution"] is not None
    assert first["execution"]["outcome"] == "PROVIDER_FAILED"
    assert first["execution"]["provider"] == "openai_compatible"
    assert first["execution"]["providerConfigHash"]
    assert first["execution"]["idempotencyKeyHash"] == hashlib.sha256(b"provider-failure-key").hexdigest()
    assert first["execution"]["executionRecordId"] == second["execution"]["executionRecordId"]
    assert len(repos.interpretations.list_runs_for_job("job_l4_api")) == 1
    serialized = json.dumps(first, sort_keys=True)
    assert "provider-failure-key" not in serialized
    assert "api_key" not in serialized.lower()


def test_analysis_plan_02_requires_dependency_execution_and_exact_lineage(tmp_path: Path) -> None:
    repos, runtime, job_id, plan_hash = _seed_dependency_source(tmp_path / "missing-execution")
    repos.dependency_execution.executions.clear()
    missing_execution = create_planner_job_interpretation(
        job_id,
        PlannerInterpretationRequest(expectedPlanHash=plan_hash),
        repositories=repos,
        queue_runtime=runtime,
    )
    assert missing_execution["outcome"] == "SOURCE_INTEGRITY_FAILED"
    assert repos.interpretations.list_runs_for_job(job_id) == []

    repos, runtime, job_id, plan_hash = _seed_dependency_source(tmp_path / "missing-lineage")
    repos.dependency_execution.lineage.clear()
    missing_lineage = create_planner_job_interpretation(
        job_id,
        PlannerInterpretationRequest(expectedPlanHash=plan_hash),
        repositories=repos,
        queue_runtime=runtime,
    )
    assert missing_lineage["outcome"] == "SOURCE_INTEGRITY_FAILED"
    assert repos.interpretations.list_runs_for_job(job_id) == []

    repos, runtime, job_id, plan_hash = _seed_dependency_source(tmp_path / "missing-intent-association")
    repos.analysis_intents.executions.clear()
    missing_intent = create_planner_job_interpretation(
        job_id,
        PlannerInterpretationRequest(expectedPlanHash=plan_hash),
        repositories=repos,
        queue_runtime=runtime,
    )
    assert missing_intent["outcome"] == "SOURCE_INTEGRITY_FAILED"
    assert repos.interpretations.list_runs_for_job(job_id) == []

    repos, runtime, job_id, plan_hash = _seed_dependency_source(tmp_path / "missing-capability-association")
    repos.capability_planning.executions.clear()
    missing_capability = create_planner_job_interpretation(
        job_id,
        PlannerInterpretationRequest(expectedPlanHash=plan_hash),
        repositories=repos,
        queue_runtime=runtime,
    )
    assert missing_capability["outcome"] == "SOURCE_INTEGRITY_FAILED"
    assert repos.interpretations.list_runs_for_job(job_id) == []


def test_structured_artifact_media_type_and_depth_are_strict(tmp_path: Path) -> None:
    repos, runtime, plan_hash = _seed_api_source(tmp_path / "media")
    repos.artifacts.records["artifact_l4_api"]["contentType"] = "text/html"
    wrong_media = create_planner_job_interpretation(
        "job_l4_api",
        PlannerInterpretationRequest(expectedPlanHash=plan_hash),
        repositories=repos,
        queue_runtime=runtime,
    )
    assert wrong_media["outcome"] == "SOURCE_INTEGRITY_FAILED"

    repos, runtime, plan_hash = _seed_api_source(tmp_path / "depth")
    nested: dict[str, object] = {"value": 1}
    for _ in range(20):
        nested = {"nested": nested}
    raw = json.dumps(nested, separators=(",", ":")).encode("utf-8")
    artifact = repos.artifacts.records["artifact_l4_api"]
    stored = runtime.artifact_storage.put_bytes(
        artifact["storageKey"], raw, content_type="application/json"
    )
    artifact.update({
        "sizeBytes": stored.size_bytes,
        "contentType": stored.content_type,
        "contentHash": stored.sha256,
        "sha256": stored.sha256,
    })
    too_deep = create_planner_job_interpretation(
        "job_l4_api",
        PlannerInterpretationRequest(expectedPlanHash=plan_hash),
        repositories=repos,
        queue_runtime=runtime,
    )
    assert too_deep["outcome"] == "SOURCE_INTEGRITY_FAILED"

    repos, runtime, plan_hash = _seed_api_source(tmp_path / "unsupported", artifact_type="report_md")
    result = create_planner_job_interpretation(
        "job_l4_api", PlannerInterpretationRequest(expectedPlanHash=plan_hash), repositories=repos, queue_runtime=runtime
    )
    assert result["outcome"] == "NO_SUPPORTED_EVIDENCE"
    assert result["claims"] == []


def test_interpretation_request_caps_and_bounded_storage_reads(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        PlannerInterpretationRequest(
            mode="STRICT_PROVIDER",
            expectedPlanHash="a" * 64,
            provider="provider with spaces",
            timeoutSeconds=121,
        )

    local = LocalFileArtifactStorage(tmp_path / "bounded")
    local.put_bytes("large.json", b"x" * 32, content_type="application/json")
    with pytest.raises(ValueError, match="bounded read limit"):
        local.get_bytes_bounded("large.json", max_bytes=16)

    class Body:
        def __init__(self) -> None:
            self.read_called = False
            self.closed = False

        def read(self, _size: int | None = None) -> bytes:
            self.read_called = True
            return b"x" * 32

        def close(self) -> None:
            self.closed = True

    class Client:
        def __init__(self, body: Body) -> None:
            self.body = body

        def get_object(self, **_kwargs: object) -> dict[str, object]:
            return {"Body": self.body, "ContentLength": 32}

    body = Body()
    remote = S3CompatibleArtifactStorage(bucket="bounded", client=Client(body))
    with pytest.raises(ValueError, match="bounded read limit"):
        remote.get_bytes_bounded("large.json", max_bytes=16)
    assert body.read_called is False
    assert body.closed is True


def test_sqlite_interpretation_round_trip_and_conflict(tmp_path: Path) -> None:
    from tests.test_phase10l4_grounded_interpretation import _numeric_candidate, _source
    from mdi_llm import build_scientific_evidence_bundle, deterministic_interpret

    engine = create_engine(f"sqlite:///{(tmp_path / 'phase10l4.sqlite').as_posix()}", future=True)
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    bundle = build_scientific_evidence_bundle(_source(), [_numeric_candidate()])
    result = deterministic_interpret(bundle)
    assert result.interpretation is not None and result.execution_record is not None
    first = repos.interpretations.save_interpretation(bundle, result.interpretation, result.execution_record)
    second = repos.interpretations.save_interpretation(bundle, result.interpretation, result.execution_record)
    assert first == second
    assert repos.interpretations.get_bundle(bundle.bundleId)["bundleHash"] == bundle.bundleHash
    assert len(repos.interpretations.list_for_job(bundle.jobId)) == 1
    engine.dispose()


def test_phase10l4_migration_upgrades_downgrades_and_reupgrades(tmp_path: Path) -> None:
    database = tmp_path / "phase10l4-migration.sqlite"
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")
    expected = {
        "scientific_evidence_bundles",
        "scientific_interpretation_runs",
        "scientific_interpretations",
        "scientific_interpretation_claims",
        "scientific_interpretation_evidence_links",
    }
    alembic_command.stamp(config, "0005_phase10l3_dependency")
    alembic_command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database.as_posix()}", future=True)
    assert expected.issubset(inspect(engine).get_table_names())
    alembic_command.downgrade(config, "0005_phase10l3_dependency")
    assert expected.isdisjoint(inspect(engine).get_table_names())
    alembic_command.upgrade(config, "head")
    assert expected.issubset(inspect(engine).get_table_names())
    engine.dispose()
