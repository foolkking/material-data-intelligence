from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from alembic.command import downgrade as alembic_downgrade
from alembic.command import stamp as alembic_stamp
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect

from mdi_api.db import metadata
from mdi_api.repositories import InMemoryRepositoryBundle, SqlAlchemyRepositoryBundle, compute_plan_hash
from mdi_schemas import (
    AnalysisPlan,
    AnalysisPlanV02,
    ArtifactLineageRecord,
    DependencyExecutionRecord,
    ResolvedArtifactInputRef,
    dependency_semantic_hash,
    deterministic_dependency_id,
    compute_dependency_graph_hash,
    make_dependency_binding,
)


HASH_A = "a" * 64
HASH_B = "b" * 64


def _step(step_id: str, tool_id: str) -> dict[str, object]:
    artifact = "phonon_dos_json" if tool_id == "phonon.dos" else "phonon_band_json"
    return {
        "stepId": step_id,
        "toolId": tool_id,
        "purpose": f"Execute {tool_id}",
        "reason": "Typed dependency persistence fixture",
        "inputRefs": [
            {
                "refType": "normalized_object",
                "ref": f"resource_{step_id}",
                "objectType": "PhononDos" if tool_id == "phonon.dos" else "PhononBand",
            }
        ],
        "params": {},
        "output": {"artifactTypes": [artifact], "displayTarget": "phonon"},
    }


def _plan() -> AnalysisPlanV02:
    binding = make_dependency_binding(
        producerStepId="band",
        producerOutputPort="canonical-band",
        consumerStepId="combined",
        consumerInputPort="band",
        artifactKind="phonon_band_json",
        artifactContractVersion="phase10h.phonon_band.v1",
        mediaType="application/json",
        cardinality="EXACTLY_ONE",
    )
    return AnalysisPlanV02.model_validate(
        {
            "schemaVersion": "0.2",
            "goal": "Compose persisted typed phonon artifacts.",
            "datasetId": "dataset_l3",
            "profileId": "profile_l3",
            "toolRegistryVersion": "1.0",
            "graphHash": compute_dependency_graph_hash([binding]),
            "steps": [_step("band", "phonon.band"), _step("combined", "phonon.band_dos")],
            "dependencyBindings": [binding.model_dump(mode="json")],
        }
    )


def _legacy_plan() -> dict[str, object]:
    return {
        "schemaVersion": "0.1",
        "goal": "Historical plan hash fixture.",
        "datasetId": "dataset_l3",
        "profileId": "profile_l3",
        "toolRegistryVersion": "1.0",
        "steps": [_step("band", "phonon.band")],
    }


def _seed_sql(repos: SqlAlchemyRepositoryBundle, plan: AnalysisPlanV02) -> tuple[str, str]:
    repos.projects.save({"projectId": "project_l3", "name": "Phase 10L-3", "createdBy": "user_l3"})
    repos.datasets.save(
        {"datasetId": plan.datasetId, "projectId": "project_l3", "name": "Phonon", "createdBy": "user_l3"}
    )
    plan_hash = compute_plan_hash(plan)
    repos.analysis_plans.save_plan(
        {
            "id": "plan_l3",
            "projectId": "project_l3",
            "datasetId": plan.datasetId,
            "profileId": plan.profileId,
            "analysisPlan": plan.model_dump(mode="json"),
            "planHash": plan_hash,
            "planSource": "capability_planner",
            "createdBy": "user_l3",
        }
    )
    repos.jobs.save(
        {
            "id": "job_l3",
            "projectId": "project_l3",
            "datasetId": plan.datasetId,
            "planId": "plan_l3",
            "status": "created",
            "createdBy": "user_l3",
        }
    )
    repos.tool_calls.save(
        {"id": "call_band", "jobId": "job_l3", "stepId": "band", "toolId": "phonon.band", "status": "completed"}
    )
    repos.tool_calls.save(
        {
            "id": "call_combined",
            "jobId": "job_l3",
            "stepId": "combined",
            "toolId": "phonon.band_dos",
            "status": "planned",
        }
    )
    repos.artifacts.save(
        {
            "id": "artifact_band",
            "projectId": "project_l3",
            "datasetId": plan.datasetId,
            "jobId": "job_l3",
            "toolCallId": "call_band",
            "type": "phonon_band_json",
            "name": "phonon_band.json",
            "storageKey": "projects/project_l3/jobs/job_l3/tool_calls/call_band/phonon_band.json",
            "sizeBytes": 512,
            "contentType": "application/json",
            "contentHash": HASH_A,
            "sha256": HASH_A,
            "metadata": {"provenance": {}},
        }
    )
    return "plan_l3", plan_hash


def _resolved_ref(plan: AnalysisPlanV02, plan_hash: str) -> ResolvedArtifactInputRef:
    binding = plan.dependencyBindings[0]
    return ResolvedArtifactInputRef.model_validate(
        {
            "bindingId": binding.bindingId,
            "planId": "plan_l3",
            "planHash": plan_hash,
            "jobId": "job_l3",
            "producerStepId": "band",
            "producerToolCallId": "call_band",
            "artifactId": "artifact_band",
            "artifactKind": "phonon_band_json",
            "artifactContractVersion": "phase10h.phonon_band.v1",
            "mediaType": "application/json",
            "sizeBytes": 512,
            "checksum": HASH_A,
            "consumerStepId": "combined",
            "consumerInputPort": "band",
            "materializedObjectRef": "resolved:job_l3:band",
        }
    )


def _execution(plan: AnalysisPlanV02, plan_hash: str, *, runtime_version: str = "10l3-test") -> DependencyExecutionRecord:
    draft = {
        "schemaVersion": "1.0",
        "executionId": "pending",
        "executionHash": HASH_A,
        "planId": "plan_l3",
        "planHash": plan_hash,
        "jobId": "job_l3",
        "graphHash": plan.graphHash,
        "topologicalOrder": ["band", "combined"],
        "steps": [
            {"stepId": "band", "toolId": "phonon.band", "state": "SUCCEEDED", "toolCallId": "call_band", "artifactIds": ["artifact_band"]},
            {"stepId": "combined", "toolId": "phonon.band_dos", "state": "SUCCEEDED", "toolCallId": "call_combined"},
        ],
        "bindings": [
            {
                "bindingId": plan.dependencyBindings[0].bindingId,
                "state": "RESOLVED",
                "producerToolCallId": "call_band",
                "artifactId": "artifact_band",
                "artifactChecksum": HASH_A,
                "consumerToolCallId": "call_combined",
            }
        ],
        "succeededCount": 2,
        "failedCount": 0,
        "blockedCount": 0,
        "notStartedCount": 0,
        "partialArtifactIds": ["artifact_band"],
        "outcome": "ALL_SUCCEEDED",
        "runtimeVersion": runtime_version,
        "createdAt": "2026-07-30T00:00:00+00:00",
        "updatedAt": "2026-07-30T00:01:00+00:00",
    }
    semantic_hash = dependency_semantic_hash(
        DependencyExecutionRecord.model_validate(draft).model_dump(mode="json"),
        identity_fields=("executionId", "executionHash", "createdAt", "updatedAt"),
    )
    draft["executionHash"] = semantic_hash
    draft["executionId"] = deterministic_dependency_id("execution", semantic_hash)
    return DependencyExecutionRecord.model_validate(draft)


def _lineage(plan: AnalysisPlanV02, plan_hash: str, *, runtime_version: str = "10l3-test") -> ArtifactLineageRecord:
    draft = {
        "schemaVersion": "1.0",
        "lineageId": "pending",
        "lineageHash": HASH_A,
        "projectId": "project_l3",
        "datasetId": plan.datasetId,
        "profileId": plan.profileId,
        "planId": "plan_l3",
        "planHash": plan_hash,
        "graphHash": plan.graphHash,
        "jobId": "job_l3",
        "producerStepId": "band",
        "producerToolCallId": "call_band",
        "producerToolId": "phonon.band",
        "producerToolVersion": "1.0.0",
        "outputPort": "canonical-band",
        "artifactId": "artifact_band",
        "artifactKind": "phonon_band_json",
        "artifactContractVersion": "phase10h.phonon_band.v1",
        "mediaType": "application/json",
        "contentHash": HASH_A,
        "runtimeVersion": runtime_version,
        "createdAt": "2026-07-30T00:00:30+00:00",
    }
    semantic_hash = dependency_semantic_hash(
        ArtifactLineageRecord.model_validate(draft).model_dump(mode="json"),
        identity_fields=("lineageId", "lineageHash", "createdAt"),
    )
    draft["lineageHash"] = semantic_hash
    draft["lineageId"] = deterministic_dependency_id("lineage", semantic_hash)
    return ArtifactLineageRecord.model_validate(draft)


def test_analysis_plan_01_hash_bytes_are_unchanged() -> None:
    plan = _legacy_plan()
    parsed = AnalysisPlan.model_validate(plan)
    legacy_payload = json.dumps(parsed.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    expected = hashlib.sha256(legacy_payload.encode("utf-8")).hexdigest()
    assert compute_plan_hash(plan) == expected
    assert compute_plan_hash(plan) == "3556e661c55c202233e9bf5c481353a62abaf058267ab78fbaaa11ce66a8acda"


@pytest.mark.parametrize("backend", ["memory", "sqlite"])
def test_plan_02_and_dependency_audit_records_round_trip_immutably(tmp_path: Path, backend: str) -> None:
    plan = _plan()
    if backend == "memory":
        repos = InMemoryRepositoryBundle.create()
        plan_hash = compute_plan_hash(plan)
        repos.analysis_plans.save_plan(
            {"id": "plan_l3", "projectId": "project_l3", "analysisPlan": plan.model_dump(mode="json"), "planHash": plan_hash}
        )
    else:
        engine = create_engine(f"sqlite:///{(tmp_path / 'phase10l3.sqlite').as_posix()}", future=True)
        metadata.create_all(engine)
        repos = SqlAlchemyRepositoryBundle.create(engine)
        _, plan_hash = _seed_sql(repos, plan)

    stored_plan = repos.analysis_plans.get_plan("plan_l3")
    assert stored_plan["analysisPlan"]["schemaVersion"] == "0.2"
    assert stored_plan["planHash"] == plan_hash
    bindings = repos.dependency_execution.save_plan_bindings(
        "plan_l3", plan_hash, plan.graphHash, plan.dependencyBindings
    )
    assert repos.dependency_execution.save_plan_bindings(
        "plan_l3", plan_hash, plan.graphHash, plan.dependencyBindings
    ) == bindings
    assert bindings[0]["dependencyBinding"]["bindingId"] == plan.dependencyBindings[0].bindingId

    resolved = _resolved_ref(plan, plan_hash)
    resolution = repos.dependency_execution.save_binding_resolution(
        {"resolvedArtifactInputRef": resolved.model_dump(mode="json"), "validationOutcome": "RESOLVED"}
    )
    assert repos.dependency_execution.save_binding_resolution(
        {"resolvedArtifactInputRef": resolved.model_dump(mode="json"), "validationOutcome": "RESOLVED"}
    )["recordHash"] == resolution["recordHash"]
    assert repos.dependency_execution.list_binding_resolutions("job_l3")[0]["artifactId"] == "artifact_band"

    execution = _execution(plan, plan_hash)
    assert repos.dependency_execution.save_execution(execution)["executionHash"] == execution.executionHash
    assert repos.dependency_execution.get_execution_for_job("job_l3")["outcome"] == "ALL_SUCCEEDED"
    with pytest.raises(ValueError, match="immutable"):
        repos.dependency_execution.save_execution(_execution(plan, plan_hash, runtime_version="changed"))

    lineage = _lineage(plan, plan_hash)
    assert repos.dependency_execution.save_lineage(lineage)["lineageHash"] == lineage.lineageHash
    assert repos.dependency_execution.get_lineage_for_artifact("artifact_band")["outputPort"] == "canonical-band"
    assert len(repos.dependency_execution.list_lineage_for_job("job_l3")) == 1
    with pytest.raises(ValueError, match="immutable"):
        repos.dependency_execution.save_lineage(_lineage(plan, plan_hash, runtime_version="changed"))

    changed_plan = plan.model_copy(update={"goal": "Changed semantic plan"})
    with pytest.raises(ValueError, match="immutable"):
        repos.analysis_plans.save_plan(
            {"id": "plan_l3", "projectId": "project_l3", "analysisPlan": changed_plan.model_dump(mode="json")}
        )
    if backend == "sqlite":
        engine.dispose()


def test_binding_resolution_conflict_is_rejected(tmp_path: Path) -> None:
    plan = _plan()
    engine = create_engine(f"sqlite:///{(tmp_path / 'binding-conflict.sqlite').as_posix()}", future=True)
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    _, plan_hash = _seed_sql(repos, plan)
    resolved = _resolved_ref(plan, plan_hash)
    repos.dependency_execution.save_binding_resolution(
        {"resolvedArtifactInputRef": resolved.model_dump(mode="json"), "validationOutcome": "RESOLVED"}
    )
    with pytest.raises(ValueError, match="immutable"):
        repos.dependency_execution.save_binding_resolution(
            {
                "resolvedArtifactInputRef": resolved.model_dump(mode="json"),
                "validationOutcome": "CONTRACT_MISMATCH",
                "errorCode": "CONTRACT_VERSION_MISMATCH",
            }
        )
    engine.dispose()


def test_phase10l3_migration_upgrades_downgrades_and_reupgrades(tmp_path: Path) -> None:
    database = tmp_path / "phase10l3-migration.sqlite"
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")
    engine = create_engine(f"sqlite:///{database.as_posix()}", future=True)
    expected = {
        "plan_dependency_bindings",
        "runtime_artifact_binding_resolutions",
        "dependency_execution_records",
        "artifact_lineage_records",
    }
    with engine.begin() as connection:
        for table in ("analysis_intents", "analysis_plans", "jobs", "tool_calls", "artifacts"):
            id_type = "VARCHAR(96)" if table in {"analysis_intents", "analysis_plans", "artifacts"} else "VARCHAR(64)"
            connection.exec_driver_sql(f"CREATE TABLE {table} (id {id_type} PRIMARY KEY)")
    alembic_stamp(config, "0003_phase10l1_intents")
    alembic_upgrade(config, "head")
    assert expected.issubset(inspect(engine).get_table_names())
    alembic_downgrade(config, "0004_phase10l2_capability")
    assert expected.isdisjoint(inspect(engine).get_table_names())
    alembic_upgrade(config, "head")
    assert expected.issubset(inspect(engine).get_table_names())
    engine.dispose()
