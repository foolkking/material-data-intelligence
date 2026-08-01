from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import uuid

import pytest
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine

from mdi_api.db import metadata
from mdi_api.repositories import SqlAlchemyRepositoryBundle
from mdi_api.routers.planner import (
    PlannerInterpretationRequest,
    PlannerJobsRequest,
    create_planner_job_interpretation,
    get_planner_interpretation_evidence,
    planner_jobs,
)
from mdi_llm import DeepSeekProvider, MockLLMProvider
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime
from scripts.generate_phase10l5_natural_language_closure_evidence import _inputs, _sanitize, case_specs
from tests.integration.test_phase10l3_dependency_service_backed import (
    _minio_storage,
    _postgres_url,
    _redis_backend,
)


CASE_IDS = ("dataset", "structure", "materials_ml", "phonon", "volumetric")


@pytest.mark.integration
@pytest.mark.parametrize("case_index", range(5), ids=CASE_IDS)
def test_phase10l5_postgres_redis_minio_natural_language_closure(
    case_index: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")
    live_deepseek = os.getenv("MDI_LIVE_DEEPSEEK") == "1"
    if live_deepseek:
        if not os.getenv("DEEPSEEK_KEY"):
            raise RuntimeError("DEEPSEEK_KEY is required for the explicit live service-backed gate")
        provider_impl = DeepSeekProvider()
        provider_name = "deepseek"
    else:
        monkeypatch.delenv("DEEPSEEK_KEY", raising=False)
        monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)
        provider_impl = MockLLMProvider(fixed_plan={"invalid": "legacy planner path must not execute"})
        provider_name = "mock"

    database_url = _postgres_url()
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", database_url)
    alembic_upgrade(config, "head")
    engine = create_engine(database_url, future=True)
    # The historical baseline migration predates auth/organization support;
    # service fixtures create those pre-migration foundation tables explicitly.
    metadata.create_all(engine)

    spec = case_specs()[case_index]
    profile, object_store, selected_resources = _inputs(spec.title)
    suffix = uuid.uuid4().hex[:12]
    project_id = f"project_l5_{CASE_IDS[case_index]}_{suffix}"
    dataset_id = f"dataset_l5_{CASE_IDS[case_index]}_{suffix}"
    profile_id = f"profile_l5_{CASE_IDS[case_index]}_{suffix}"
    profile_payload = profile.model_dump(mode="json")
    profile_payload["datasetId"] = dataset_id
    profile_payload["profileId"] = profile_id
    if profile_payload["sampleIdentity"] is not None:
        profile_payload["sampleIdentity"]["datasetVersion"] = profile_payload["version"]
    semantic_payload = {
        "datasetId": dataset_id,
        "datasetVersion": profile_payload["version"],
        "semanticRulesVersion": profile_payload["semanticRulesVersion"],
        "objectHashes": sorted(item.get("hash") or item["objectHash"] for item in profile_payload["objects"]),
        "semanticColumns": profile_payload["semanticColumns"],
        "semanticGroups": profile_payload["semanticGroups"],
        "resourceSemantics": profile_payload["resourceSemantics"],
        "analysisReadiness": profile_payload["analysisReadiness"],
        "sampleIdentity": profile_payload["sampleIdentity"],
        "profileCoverage": profile_payload["profileCoverage"],
    }
    expected_semantic_hash = sha256(
        json.dumps(
            semantic_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()
    profile_payload["semanticHash"] = expected_semantic_hash
    exact_profile = DataProfile.model_validate(profile_payload)
    assert exact_profile.semanticHash == expected_semantic_hash
    object_store["profile"] = exact_profile

    repos = SqlAlchemyRepositoryBundle.create(engine)
    repos.projects.save({"id": project_id, "name": project_id, "createdBy": "phase10l5_ci"})
    repos.datasets.save({
        "id": dataset_id,
        "projectId": project_id,
        "name": dataset_id,
        "createdBy": "phase10l5_ci",
    })
    repos.data_profiles.save(exact_profile)

    queue_backend, redis_queue = _redis_backend(queue_name=f"mdi-test-phase10l5-{CASE_IDS[case_index]}-{suffix}")
    storage = _minio_storage(prefix=f"phase10l5-{CASE_IDS[case_index]}-{suffix}")
    registry = load_manifests()
    runtime = QueueWorkerRuntime(
        repositories=repos,
        queue_backend=queue_backend,
        artifact_storage=storage,
        registry=registry,
    )
    planned = planner_jobs(
        PlannerJobsRequest(
            userPrompt=spec.userText,
            projectId=project_id,
            datasetId=dataset_id,
            profileId=profile_id,
            intentSchemaVersion="1.0",
            selectedResourceIds=selected_resources,
            provider=provider_name,
            enqueue=True,
        ),
        provider=provider_impl,
        repositories=repos,
        queue_runtime=runtime,
        registry=registry,
    )
    assert planned.ok and planned.job_id and planned.plan_id and planned.plan_hash and planned.plan
    assert planned.enqueued is True
    assert planned.intent and planned.intent["rawGoal"] == spec.userText
    assert planned.intent["outcome"] == "READY"
    assert planned.capability_outcome == "PLAN_READY"
    selected_tools = {step["toolId"] for step in planned.plan["steps"]}
    assert selected_tools.issubset(set(spec.acceptableToolIds))
    assert selected_tools.isdisjoint(set(spec.forbiddenFallbacks))
    eligible_tools = set(planned.eligibility_resolution["eligibleToolIds"])
    assert set(planned.provider_visible_tool_ids) == eligible_tools
    assert selected_tools.issubset(eligible_tools)
    assert planned.plan_schema_version == ("0.2" if spec.requiresDependencyPlan else "0.1")
    assert redis_queue.fetch_job(planned.job_id) is not None

    executed = runtime.handle_job(planned.job_id, object_store=object_store)
    assert executed.status == "completed"
    tool_calls = repos.tool_calls.list_for_job(planned.job_id)
    artifacts = repos.artifacts.list_for_job(planned.job_id)
    assert tool_calls and artifacts
    assert {item["toolId"] for item in tool_calls} == selected_tools
    for artifact in artifacts:
        assert artifact["storageProvider"] == "s3"
        assert storage.exists(artifact["storageKey"])
        content = storage.get_bytes(artifact["storageKey"])
        assert sha256(content).hexdigest() == (artifact.get("contentHash") or artifact["sha256"])

    if spec.requiresDependencyPlan:
        execution = repos.dependency_execution.get_execution_for_job(planned.job_id)
        assert execution and execution["outcome"] == "ALL_SUCCEEDED"
        assert repos.dependency_execution.list_lineage_for_job(planned.job_id)

    counts_before = (
        len(repos.jobs.list_by_project(project_id)),
        len(tool_calls),
        len(artifacts),
    )
    interpretation_request = PlannerInterpretationRequest(
        mode="STRICT_PROVIDER" if live_deepseek else "DETERMINISTIC",
        expectedPlanHash=planned.plan_hash,
        idempotencyKey=f"phase10l5-service-{spec.caseSpecHash[:24]}",
        provider="deepseek" if live_deepseek else None,
    )
    interpreted = create_planner_job_interpretation(
        planned.job_id,
        interpretation_request,
        repositories=repos,
        queue_runtime=runtime,
        provider=provider_impl if live_deepseek else None,
    )
    assert interpreted["outcome"] in {"INTERPRETATION_READY", "INTERPRETATION_READY_WITH_LIMITS"}
    assert interpreted["claims"]
    assert interpreted["noExecution"] == {
        "toolCallCreated": False,
        "planCreated": False,
        "jobCreated": False,
        "enqueued": False,
        "recommendationExecutionAuthorized": False,
    }
    evidence = get_planner_interpretation_evidence(interpreted["interpretationId"], repositories=repos)
    evidence_ids = {item["evidenceItemId"] for item in evidence["evidenceItems"]}
    assert evidence_ids
    assert all(set(claim["supportingEvidenceIds"]).issubset(evidence_ids) for claim in interpreted["claims"])
    replay = create_planner_job_interpretation(
        planned.job_id,
        interpretation_request,
        repositories=repos,
        queue_runtime=runtime,
        provider=provider_impl if live_deepseek else None,
    )
    assert replay["interpretationId"] == interpreted["interpretationId"]
    assert counts_before == (
        len(repos.jobs.list_by_project(project_id)),
        len(repos.tool_calls.list_for_job(planned.job_id)),
        len(repos.artifacts.list_for_job(planned.job_id)),
    )
    assert len(repos.interpretations.list_for_job(planned.job_id)) == 1
    assert len(repos.interpretations.list_runs_for_job(planned.job_id)) == 1

    if live_deepseek:
        call_audit = list(provider_impl.call_audit)
        assert call_audit
        assert all(item["realCall"] is True and item["outcome"] == "SUCCESS" for item in call_audit)
        evidence_dir = os.getenv("PHASE10L5_SERVICE_EVIDENCE_DIR")
        if evidence_dir:
            target = Path(evidence_dir) / f"case_{case_index + 1}_{CASE_IDS[case_index]}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(
                    _sanitize(
                        {
                            "schemaVersion": "1.0",
                            "mode": "REAL_DEEPSEEK_POSTGRES_REDIS_MINIO",
                            "caseSpecId": spec.caseSpecId,
                            "caseSpecHash": spec.caseSpecHash,
                            "userText": spec.userText,
                            "profile": {
                                "profileId": exact_profile.profileId,
                                "semanticHash": exact_profile.semanticHash,
                                "contractVersion": exact_profile.profileContractVersion,
                            },
                            "intent": planned.intent,
                            "eligibilityResolution": planned.eligibility_resolution,
                            "capabilityDecision": planned.capability_decision,
                            "providerVisibleToolIds": planned.provider_visible_tool_ids,
                            "selectedToolIds": sorted(selected_tools),
                            "plan": planned.plan,
                            "planId": planned.plan_id,
                            "planHash": planned.plan_hash,
                            "jobId": planned.job_id,
                            "jobStatus": executed.status,
                            "enqueued": planned.enqueued,
                            "toolCalls": tool_calls,
                            "artifacts": [
                                {
                                    "id": item["id"],
                                    "type": item["type"],
                                    "contentHash": item.get("contentHash") or item["sha256"],
                                    "sizeBytes": item["sizeBytes"],
                                    "storageProvider": item["storageProvider"],
                                }
                                for item in artifacts
                            ],
                            "dependencyExecution": (
                                repos.dependency_execution.get_execution_for_job(planned.job_id)
                                if spec.requiresDependencyPlan
                                else None
                            ),
                            "artifactLineage": (
                                repos.dependency_execution.list_lineage_for_job(planned.job_id)
                                if spec.requiresDependencyPlan
                                else []
                            ),
                            "interpretation": interpreted,
                            "evidenceItemCount": len(evidence_ids),
                            "providerCallAudit": call_audit,
                            "realLlmCalls": len(call_audit),
                            "otherRealProviderCalls": 0,
                            "verdict": "PASS",
                        }
                    ),
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                    allow_nan=False,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
    engine.dispose()
