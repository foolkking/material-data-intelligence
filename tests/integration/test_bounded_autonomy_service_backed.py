from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from uuid import uuid4

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from mdi_artifact_core import canonical_trajectory_id
import pytest
from redis import Redis
from rq import Queue
from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.schema import CreateSchema, DropSchema

from mdi_api.db import (
    data_profiles,
    datasets,
    organizations,
    projects,
    research_turn_events,
    research_turns,
    sessions,
    users,
)
from mdi_api.domain.scientific_results.contracts import (
    FactSourceLocator,
    MethodRecord,
    ProvenanceRecord,
    ResultExecutionStatus,
    ResultRelevanceStatus,
    ScientificFact,
    ScientificLimitation,
    ScientificResultBundle,
    ScientificResultItem,
    ScientificResultRole,
)
from mdi_api.infrastructure.interpretation.queue import RedisRQInterpretationQueue
from mdi_api.research_agent.autonomy.service import BoundedAutonomyService
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.orchestration.queue import RedisRQAgentTurnQueue
from mdi_api.research_agent.schemas import (
    AutonomyMode,
    CreateResearchTurnRequest,
    ResearchTurnUIContext,
)
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import (
    ScientificObjectKind,
    ScientificObjectRef,
    StorageRef,
)
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.unit_of_work import RepositoryFactory
from mdi_api.repositories import SqlAlchemyRepositoryBundle
from mdi_workers.queue_runtime import RedisRQQueueBackend
from tests.integration.test_agent2_phase4_service_backed import (
    _minio_storage,
    _worker_environment,
)
from tests.integration.test_phase10m1_workspace_service_backed import (
    _schema_database_url,
)
from tests.integration.test_phase10_product_closure import _materials_ml_profile
from tests.test_phase10n4_trajectory_analytics import _execute, _trajectory


ROOT = Path(__file__).resolve().parents[2]


def _autonomy_trajectory() -> dict:
    """Extend the small canonical fixture to a valid seven-lag fit domain."""

    payload = _trajectory()
    template = payload["frames"][0]
    payload["frames"] = [
        {
            **template,
            "frame_index": index,
            "step": index * 5,
            "time": float(index * 2),
            "positions": [
                [index * 0.01, 0.0, 0.0],
                [0.25 + index * 0.01, 0.25, 0.25],
            ],
        }
        for index in range(8)
    ]
    payload["trajectory_id"] = canonical_trajectory_id(payload)
    return payload


def _run_worker(
    queue_name: str,
    *,
    redis_url: str,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mdi_workers.worker_entrypoint",
            queue_name,
            "--url",
            redis_url,
            "--burst",
            "--max-jobs",
            "1",
            "--name",
            f"workstream-e-{queue_name}-{uuid4().hex[:8]}",
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=240,
    )
    assert result.returncode == 0, result.stderr[-8000:]
    return result


def _interpretation_fixture(
    *,
    result_item_id: str,
    fact_id: str,
    statement: str,
) -> str:
    return json.dumps(
        {
            "contract_version": "1.0",
            "title": "Qualified scientific evidence",
            "answer_lead": statement,
            "primary_findings": [
                {
                    "finding_id": "finding-1",
                    "statement": statement,
                    "importance": "HIGH",
                    "confidence": "HIGH",
                    "fact_refs": [fact_id],
                    "evidence_refs": [],
                    "result_item_refs": [result_item_id],
                }
            ],
            "supporting_findings": [],
            "limitations": [],
            "primary_result_refs": [result_item_id],
            "supporting_result_refs": [],
            "follow_up_suggestions": [],
        }
    )


@pytest.mark.integration
def test_bounded_autonomy_persists_cross_family_ml_to_composition_strategy(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A durable ML Result may justify one qualified composition-space cycle."""

    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip(
            "Set MDI_RUN_INTEGRATION=1 with PostgreSQL and Redis running"
        )
    base_url = os.environ["MDI_TEST_DATABASE_URL"]
    suffix = uuid4().hex[:12]
    schema_name = f"strategy_f_{suffix}"
    database_url = _schema_database_url(base_url, schema_name)
    redis_url = os.getenv("MDI_REDIS_URL") or os.getenv("REDIS_URL")
    assert redis_url
    queue_names = {
        "turn": f"mdi-f-turn-{suffix}",
        "plan": f"mdi-f-plan-{suffix}",
    }
    base_engine = create_engine(base_url, future=True)
    engine = None
    redis = Redis.from_url(redis_url)
    try:
        with base_engine.begin() as connection:
            connection.execute(CreateSchema(schema_name))
        monkeypatch.setenv("DATABASE_URL", database_url)
        monkeypatch.setenv("MDI_DATABASE_URL", database_url)
        config = AlembicConfig("apps/api/alembic.ini")
        config.set_main_option("script_location", "apps/api/alembic")
        config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
        alembic_command.upgrade(config, "head")
        engine = create_engine(database_url, future=True, pool_pre_ping=True)

        owner = CurrentUser(
            id=f"strategy-owner-{suffix}",
            email=f"strategy-{suffix}@example.invalid",
            displayName="Workstream F qualification",
            roles=[],
        )
        project_id = f"strategy-project-{suffix}"
        session_id = f"strategy-session-{suffix}"
        dataset_id = f"strategy-dataset-{suffix}"
        profile, _objects = _materials_ml_profile(tmp_path, dataset_id)
        with engine.begin() as connection:
            connection.execute(
                insert(users),
                {
                    "id": owner.id,
                    "email": owner.email,
                    "display_name": owner.displayName,
                    "is_active": True,
                },
            )
            connection.execute(
                insert(organizations),
                {"id": f"strategy-org-{suffix}", "name": "Workstream F"},
            )
            connection.execute(
                insert(projects),
                {
                    "id": project_id,
                    "organization_id": f"strategy-org-{suffix}",
                    "name": "Workstream F qualification",
                    "created_by": owner.id,
                },
            )
            connection.execute(
                insert(datasets),
                {
                    "id": dataset_id,
                    "project_id": project_id,
                    "name": "Qualification materials dataset",
                    "status": "profile_ready",
                    "metadata_json": {},
                    "created_by": owner.id,
                },
            )
            connection.execute(
                insert(data_profiles),
                {
                    "id": profile.profileId,
                    "dataset_id": dataset_id,
                    "version": profile.version,
                    "profile_json": profile.model_dump(mode="json"),
                },
            )
            connection.execute(
                insert(sessions),
                {
                    "id": session_id,
                    "project_id": project_id,
                    "dataset_id": dataset_id,
                    "mode": "project",
                    "status": "active",
                    "created_by": owner.id,
                },
            )

        factory = RepositoryFactory(engine)
        objects = ScientificObjectService(
            factory, build_default_object_type_registry()
        )
        logical = objects.create_object(
            project_id=project_id,
            kind=ScientificObjectKind.DATASET,
            object_type="materials.dataset",
            display_name="Qualification materials dataset",
            created_by_user_id=owner.id,
        )
        version = objects.create_version(
            logical["id"],
            object_type="materials.dataset",
            object_schema_version="1.0",
            source_resource_refs=[
                {"project_id": project_id, "dataset_id": dataset_id}
            ],
            parent_object_version_refs=[],
            normalized_payload_ref=StorageRef(
                storage_backend="minio",
                object_key=f"workstream-f/{suffix}/materials.json",
                checksum=f"strategy-materials-{suffix}",
                media_type="application/json",
            ),
            content_hash=f"strategy-content-{suffix}",
            semantic_hash=f"strategy-semantic-{suffix}",
            canonical_metadata={
                "row_count": 4,
                "semantic_roles": [
                    "material_formula",
                    "regression_target",
                    "regression_prediction",
                ],
            },
            created_by_user_id=owner.id,
        )
        source_ref = ScientificObjectRef(
            object_id=logical["id"],
            version_id=version["id"],
            project_id=project_id,
            object_type="materials.dataset",
            display_name=logical["display_name"],
        )
        objective = (
            "Investigate where this model performs poorly and whether the "
            "errors have a meaningful materials chemistry pattern."
        )
        root = ResearchTurnService(factory).receive_turn(
            project_id=project_id,
            session_id=session_id,
            current_user=owner,
            request=CreateResearchTurnRequest(
                message=objective,
                autonomy_mode=AutonomyMode.BOUNDED_AUTONOMOUS,
                ui_context=ResearchTurnUIContext(
                    active_object_refs=[source_ref],
                    selection_refs=[source_ref],
                    explicit_object_refs=[source_ref],
                ),
            ),
        )
        result_snapshot_id = uuid4()
        result_item_id = "ml.regression.evaluation"
        fact_id = "ml.rmse"
        bundle = ScientificResultBundle(
            schema_version="1.0",
            result_id=uuid4(),
            project_id=project_id,
            research_session_id=session_id,
            research_turn_id=root.turn_id,
            research_question=objective,
            source_object_refs=[source_ref],
            execution_status=ResultExecutionStatus.SUCCESS,
            relevance_status=ResultRelevanceStatus.CURRENT,
            result_items=[
                ScientificResultItem(
                    id=result_item_id,
                    result_type=result_item_id,
                    role=ScientificResultRole.PRIMARY,
                    title="Regression evaluation",
                    artifact_ids=[],
                    scientific_object_refs=[],
                    fact_refs=[fact_id],
                    evidence_refs=[],
                )
            ],
            facts=[
                ScientificFact(
                    fact_id=fact_id,
                    predicate="ml.regression.rmse",
                    subject_ref=str(source_ref.version_id),
                    value=0.22,
                    unit="eV",
                    source=FactSourceLocator(artifact_locator="/metrics/rmse"),
                )
            ],
            figures=[],
            tables=[],
            output_object_refs=[],
            evidence=[],
            methods=[
                MethodRecord(
                    method_id="method:ml.regression_evaluation",
                    capability_id="ml.regression_evaluation",
                    capability_version="1.0",
                    tool_id="ml.regression_evaluation",
                    tool_version="0.1.0",
                    source_object_refs=[source_ref],
                )
            ],
            limitations=[
                ScientificLimitation(
                    limitation_id="ml.global-metrics-not-causal",
                    code="DESCRIPTIVE_NOT_CAUSAL",
                    message=(
                        "Global regression metrics do not establish a "
                        "chemistry-conditioned error mechanism."
                    ),
                    source_ref=f"result:{result_snapshot_id}",
                )
            ],
            warnings=[],
            provenance=ProvenanceRecord(
                research_turn_id=root.turn_id,
                source_object_version_ids=[source_ref.version_id],
            ),
            projection_version="workstream-f-ml/1.0",
        )
        now = datetime.now(timezone.utc)
        with factory.unit_of_work() as unit:
            unit.connection.execute(
                update(research_turns)
                .where(research_turns.c.id == root.turn_id)
                .values(
                    status="COMPLETED",
                    action_type="ANALYZE",
                    completed_at=now,
                    updated_at=now,
                )
            )
            unit.agent2.research_context_snapshots.add(
                {
                    "id": uuid4(),
                    "project_id": project_id,
                    "research_session_id": session_id,
                    "research_turn_id": root.turn_id,
                    "snapshot_schema_version": "1.1",
                    "active_scope_refs_json": [
                        source_ref.model_dump(mode="json")
                    ],
                    "selection_refs_json": [
                        source_ref.model_dump(mode="json")
                    ],
                    "scientific_selections_json": [],
                    "resolved_references_json": [],
                    "referenced_result_refs_json": [],
                    "relevant_finding_refs_json": [],
                    "effective_constraints_json": [],
                    "research_goal": objective,
                    "unresolved_questions_json": [],
                    "context_fingerprint": "f" * 64,
                    "compiler_version": "workstream-f-service-fixture/1.0",
                }
            )
            unit.agent2.scientific_result_snapshots.add(
                {
                    "id": result_snapshot_id,
                    "project_id": project_id,
                    "research_turn_id": root.turn_id,
                    "job_id": None,
                    "schema_version": "1.0",
                    "projection_version": bundle.projection_version,
                    "execution_status": "SUCCESS",
                    "relevance_status": "CURRENT",
                    "source_fingerprint": "e" * 64,
                    "bundle_json": bundle.model_dump(mode="json"),
                    "created_at": now,
                }
            )
            unit.agent2.interpretations.add(
                {
                    "id": uuid4(),
                    "research_turn_id": root.turn_id,
                    "result_snapshot_id": result_snapshot_id,
                    "project_id": project_id,
                    "contract_version": "1.0",
                    "prompt_version": "workstream-f-fixture/1.0",
                    "provider": "fixture",
                    "model": "fixture",
                    "provider_request_id": None,
                    "repair_attempted": False,
                    "input_fingerprint": "d" * 64,
                    "grounding_status": "VALID",
                    "output_json": {
                        "summary": "Model error evidence is available."
                    },
                    "created_at": now,
                }
            )

        advanced = BoundedAutonomyService(
            factory,
            queue=RedisRQAgentTurnQueue(
                redis_url=redis_url,
                queue_name=queue_names["turn"],
            ),
        ).advance_after_interpretation(root.turn_id)
        assert advanced is not None
        assert advanced.enqueued is True
        assert advanced.assessment.selected_capability_id == (
            "data.composition_space"
        )
        assert advanced.assessment.unresolved_requirement_id == (
            "data.explore_composition_space"
        )
        assert advanced.assessment.context_snapshot_fingerprint == "f" * 64
        assert advanced.assessment.strategy_decision is not None
        assert advanced.assessment.strategy_decision.action.value == "COMPARE"

        environment = _worker_environment(database_url)
        environment.update(
            {
                "MDI_ENV": "ci",
                "MDI_QUEUE_BACKEND": "redis",
                "REDIS_URL": redis_url,
                "MDI_REDIS_URL": redis_url,
                "MDI_AGENT2_ORCHESTRATION_ENABLED": "1",
                "MDI_AGENT2_QUEUE_NAME": queue_names["turn"],
                "MDI_AGENT2_PLANNING_QUEUE_NAME": queue_names["plan"],
            }
        )
        _run_worker(
            queue_names["turn"],
            redis_url=redis_url,
            environment=environment,
        )
        _run_worker(
            queue_names["plan"],
            redis_url=redis_url,
            environment=environment,
        )
        with factory.session() as session:
            child = session.agent2.research_turns.get(advanced.child_turn_id)
            child_snapshot = (
                session.agent2.research_context_snapshots.get_for_turn(
                    advanced.child_turn_id
                )
            )
            child_plan = session.agent2.research_capability_plans.get_for_turn(
                advanced.child_turn_id
            )
            analysis_plan = session.repositories.analysis_plans.get_plan(
                str(child["analysis_plan_id"])
            )
        assert child["status"] == "PLAN_READY"
        assert child_snapshot["context_fingerprint"]
        selected_versions = {
            item["version_id"]
            for item in [
                *child_snapshot["selection_refs_json"],
                *child_snapshot["active_scope_refs_json"],
            ]
        }
        assert selected_versions == {str(source_ref.version_id)}
        assert child_plan["plan_json"]["steps"][0]["capability_ref_key"]
        assert analysis_plan["analysisPlan"]["steps"][0]["toolId"] == (
            "dataset.composition_space"
        )
    finally:
        for queue_name in queue_names.values():
            try:
                Queue(queue_name, connection=redis).delete(delete_jobs=True)
            except Exception:
                pass
        if engine is not None:
            engine.dispose()
        try:
            with base_engine.begin() as connection:
                connection.execute(DropSchema(schema_name, cascade=True))
        finally:
            base_engine.dispose()


@pytest.mark.integration
def test_bounded_autonomy_reuses_msd_and_completes_diffusion_in_fresh_workers(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip(
            "Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running"
        )
    base_url = os.environ["MDI_TEST_DATABASE_URL"]
    suffix = uuid4().hex[:12]
    schema_name = f"autonomy_e_{suffix}"
    database_url = _schema_database_url(base_url, schema_name)
    redis_url = os.getenv("MDI_REDIS_URL") or os.getenv("REDIS_URL")
    assert redis_url
    queue_names = {
        "turn": f"mdi-e-turn-{suffix}",
        "plan": f"mdi-e-plan-{suffix}",
        "job": f"mdi-e-job-{suffix}",
        "result": f"mdi-e-result-{suffix}",
        "interpretation": f"mdi-e-interpretation-{suffix}",
    }
    base_engine = create_engine(base_url, future=True)
    engine = None
    storage = None
    storage_keys: list[str] = []
    redis = Redis.from_url(redis_url)
    try:
        with base_engine.begin() as connection:
            connection.execute(CreateSchema(schema_name))
        monkeypatch.setenv("DATABASE_URL", database_url)
        monkeypatch.setenv("MDI_DATABASE_URL", database_url)
        config = AlembicConfig("apps/api/alembic.ini")
        config.set_main_option("script_location", "apps/api/alembic")
        config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
        alembic_command.upgrade(config, "head")
        engine = create_engine(database_url, future=True, pool_pre_ping=True)

        owner = CurrentUser(
            id=f"autonomy-owner-{suffix}",
            email=f"autonomy-{suffix}@example.invalid",
            displayName="Workstream E qualification",
            roles=[],
        )
        project_id = f"autonomy-project-{suffix}"
        session_id = f"autonomy-session-{suffix}"
        dataset_id = f"autonomy-dataset-{suffix}"
        profile_id = f"autonomy-profile-{suffix}"
        with engine.begin() as connection:
            connection.execute(
                insert(users),
                {
                    "id": owner.id,
                    "email": owner.email,
                    "display_name": owner.displayName,
                    "is_active": True,
                },
            )
            connection.execute(
                insert(organizations),
                {"id": f"autonomy-org-{suffix}", "name": "Workstream E"},
            )
            connection.execute(
                insert(projects),
                {
                    "id": project_id,
                    "organization_id": f"autonomy-org-{suffix}",
                    "name": "Workstream E qualification",
                    "created_by": owner.id,
                },
            )
            connection.execute(
                insert(datasets),
                {
                    "id": dataset_id,
                    "project_id": project_id,
                    "name": "Qualification trajectory",
                    "status": "profile_ready",
                    "metadata_json": {},
                    "created_by": owner.id,
                },
            )
            connection.execute(
                insert(data_profiles),
                {
                    "id": profile_id,
                    "dataset_id": dataset_id,
                    "version": "2.4",
                    "profile_json": {
                        "id": profile_id,
                        "datasetId": dataset_id,
                        "datasetType": "trajectory",
                    },
                },
            )
            connection.execute(
                insert(sessions),
                {
                    "id": session_id,
                    "project_id": project_id,
                    "dataset_id": dataset_id,
                    "mode": "project",
                    "status": "active",
                    "created_by": owner.id,
                },
            )

        storage = _minio_storage()
        trajectory_payload = _autonomy_trajectory()
        source_stored = storage.put_json(
            f"workstream-e/{suffix}/trajectory.json", trajectory_payload
        )
        storage_keys.append(source_stored.storage_key)
        factory = RepositoryFactory(engine)
        objects = ScientificObjectService(
            factory, build_default_object_type_registry()
        )
        logical = objects.create_object(
            project_id=project_id,
            kind=ScientificObjectKind.TRAJECTORY,
            object_type="trajectory.atomic",
            display_name="Workstream E trajectory",
            created_by_user_id=owner.id,
        )
        version = objects.create_version(
            logical["id"],
            object_type="trajectory.atomic",
            object_schema_version="1.0",
            source_resource_refs=[
                {"project_id": project_id, "dataset_id": dataset_id}
            ],
            parent_object_version_refs=[],
            normalized_payload_ref=StorageRef(
                storage_backend="minio",
                object_key=source_stored.storage_key,
                checksum=source_stored.sha256,
                media_type="application/json",
                byte_size=source_stored.size_bytes,
            ),
            content_hash=source_stored.sha256,
            semantic_hash=f"autonomy-trajectory-{suffix}",
            canonical_metadata={"frame_count": 8, "timestep_fs": 1000.0},
            created_by_user_id=owner.id,
        )
        source_ref = ScientificObjectRef(
            object_id=logical["id"],
            version_id=version["id"],
            project_id=project_id,
            object_type="trajectory.atomic",
            display_name=logical["display_name"],
        )
        root = ResearchTurnService(factory).receive_turn(
            project_id=project_id,
            session_id=session_id,
            current_user=owner,
            request=CreateResearchTurnRequest(
                message="Analyze the diffusion behavior in this trajectory.",
                autonomy_mode=AutonomyMode.BOUNDED_AUTONOMOUS,
                ui_context=ResearchTurnUIContext(
                    active_object_refs=[source_ref],
                    selection_refs=[source_ref],
                    explicit_object_refs=[source_ref],
                ),
            ),
        )

        msd_root = tmp_path / "msd"
        msd_output = _execute(
            msd_root,
            "trajectory.msd",
            trajectory_payload,
            {"max_lag_count": 7},
        )[0]
        msd_bytes = (msd_root / msd_output.storageKey).read_bytes()
        msd_key = f"workstream-e/{suffix}/msd.json"
        msd_stored = storage.put_bytes(
            msd_key, msd_bytes, content_type="application/json"
        )
        storage_keys.append(msd_stored.storage_key)
        msd_payload = json.loads(msd_bytes)
        parent_job_id = f"job-autonomy-msd-{suffix}"
        parent_call_id = f"call-autonomy-msd-{suffix}"
        parent_artifact_id = f"artifact-autonomy-msd-{suffix}"
        repos = SqlAlchemyRepositoryBundle.create(engine)
        repos.jobs.save(
            {
                "id": parent_job_id,
                "projectId": project_id,
                "datasetId": dataset_id,
                "status": "completed",
                "createdBy": owner.id,
            }
        )
        repos.tool_calls.save(
            {
                "id": parent_call_id,
                "jobId": parent_job_id,
                "stepId": "step_msd",
                "toolId": "trajectory.msd",
                "status": "completed",
                "params": {"max_lag_count": 7},
            }
        )
        repos.artifacts.save(
            {
                "id": parent_artifact_id,
                "projectId": project_id,
                "datasetId": dataset_id,
                "jobId": parent_job_id,
                "toolCallId": parent_call_id,
                "type": "table_json",
                "version": msd_output.version,
                "name": "trajectory_msd.json",
                "storageKey": msd_stored.storage_key,
                "storageProvider": "minio",
                "bucket": os.getenv("MINIO_BUCKET", "mdi-artifacts"),
                "sizeBytes": msd_stored.size_bytes,
                "contentType": "application/json",
                "contentHash": msd_stored.sha256,
                "sha256": msd_stored.sha256,
                "metadata": {
                    "provenance": {
                        "schemaVersion": "phase10n4.trajectory_msd.v1"
                    }
                },
            }
        )
        fact_id = "trajectory.msd.final"
        lag_count_fact_id = "trajectory.msd.lag-count"
        first_lag_fact_id = "trajectory.msd.first-lag"
        last_lag_fact_id = "trajectory.msd.last-lag"
        result_item_id = "trajectory.msd"
        bundle = ScientificResultBundle(
            schema_version="1.0",
            result_id=uuid4(),
            project_id=project_id,
            research_session_id=session_id,
            research_turn_id=root.turn_id,
            research_question="Analyze the diffusion behavior in this trajectory.",
            source_object_refs=[source_ref],
            execution_status=ResultExecutionStatus.SUCCESS,
            relevance_status=ResultRelevanceStatus.CURRENT,
            result_items=[
                ScientificResultItem(
                    id=result_item_id,
                    result_type="trajectory.msd",
                    role=ScientificResultRole.PRIMARY,
                    title="Mean squared displacement",
                    artifact_ids=[parent_artifact_id],
                    scientific_object_refs=[],
                    fact_refs=[
                        fact_id,
                        lag_count_fact_id,
                        first_lag_fact_id,
                        last_lag_fact_id,
                    ],
                    evidence_refs=[],
                )
            ],
            facts=[
                ScientificFact(
                    fact_id=fact_id,
                    predicate="trajectory.msd.final",
                    subject_ref=str(source_ref.version_id),
                    value=msd_payload["totalMsdAngstrom2"][-1],
                    unit="angstrom^2",
                    source=FactSourceLocator(
                        tool_call_id=parent_call_id,
                        artifact_id=parent_artifact_id,
                        artifact_locator=(
                            f"/totalMsdAngstrom2/"
                            f"{len(msd_payload['totalMsdAngstrom2']) - 1}"
                        ),
                    ),
                ),
                ScientificFact(
                    fact_id=lag_count_fact_id,
                    predicate="trajectory.msd_lag_count",
                    subject_ref=str(source_ref.version_id),
                    value=len(msd_payload["lagTimesPs"]),
                    unit="count",
                    source=FactSourceLocator(
                        tool_call_id=parent_call_id,
                        artifact_id=parent_artifact_id,
                        artifact_locator="/coverage/validLags",
                    ),
                ),
                ScientificFact(
                    fact_id=first_lag_fact_id,
                    predicate="trajectory.msd_first_lag_time",
                    subject_ref=str(source_ref.version_id),
                    value=msd_payload["lagTimesPs"][0],
                    unit="picosecond",
                    source=FactSourceLocator(
                        tool_call_id=parent_call_id,
                        artifact_id=parent_artifact_id,
                        artifact_locator="/lagTimesPs/0",
                    ),
                ),
                ScientificFact(
                    fact_id=last_lag_fact_id,
                    predicate="trajectory.msd_last_lag_time",
                    subject_ref=str(source_ref.version_id),
                    value=msd_payload["lagTimesPs"][-1],
                    unit="picosecond",
                    source=FactSourceLocator(
                        tool_call_id=parent_call_id,
                        artifact_id=parent_artifact_id,
                        artifact_locator=f"/lagTimesPs/{len(msd_payload['lagTimesPs']) - 1}",
                    ),
                ),
            ],
            figures=[],
            tables=[],
            output_object_refs=[],
            evidence=[],
            methods=[
                MethodRecord(
                    method_id="method:trajectory.msd",
                    capability_id="trajectory.msd",
                    capability_version="1.0",
                    tool_id="trajectory.msd",
                    tool_version="0.1.0",
                    parameters={"max_lag_count": 7},
                    source_object_refs=[source_ref],
                )
            ],
            limitations=[],
            warnings=[],
            provenance=ProvenanceRecord(
                research_turn_id=root.turn_id,
                job_id=parent_job_id,
                source_object_version_ids=[source_ref.version_id],
                tool_call_ids=[parent_call_id],
                artifact_ids=[parent_artifact_id],
                projector_ids=["qualification.seeded-real-msd"],
            ),
            projection_version="workstream-e-msd/1.0",
        )
        snapshot_id = uuid4()
        with factory.unit_of_work() as unit:
            unit.connection.execute(
                update(research_turns)
                .where(research_turns.c.id == root.turn_id)
                .values(
                    status="RESULT_READY",
                    action_type="ANALYZE",
                    job_id=parent_job_id,
                )
            )
            unit.agent2.scientific_result_snapshots.add(
                {
                    "id": snapshot_id,
                    "project_id": project_id,
                    "research_turn_id": root.turn_id,
                    "job_id": parent_job_id,
                    "schema_version": "1.0",
                    "projection_version": bundle.projection_version,
                    "execution_status": "SUCCESS",
                    "relevance_status": "CURRENT",
                    "source_fingerprint": msd_stored.sha256,
                    "bundle_json": bundle.model_dump(mode="json"),
                }
            )

        environment = _worker_environment(database_url)
        environment.update(
            {
                "MDI_ENV": "ci",
                "MDI_QUEUE_BACKEND": "redis",
                "REDIS_URL": redis_url,
                "MDI_REDIS_URL": redis_url,
                "MDI_AGENT2_ORCHESTRATION_ENABLED": "1",
                "MDI_AGENT2_QUEUE_NAME": queue_names["turn"],
                "MDI_AGENT2_PLANNING_QUEUE_NAME": queue_names["plan"],
                "MDI_AGENT2_EXECUTION_QUEUE_NAME": queue_names["job"],
                "MDI_AGENT2_RESULT_PROJECTION_ENABLED": "1",
                "MDI_AGENT2_RESULT_QUEUE_NAME": queue_names["result"],
                "MDI_AGENT2_INTERPRETATION_ENABLED": "1",
                "MDI_AGENT2_INTERPRETATION_QUEUE_NAME": queue_names[
                    "interpretation"
                ],
                "MDI_AGENT2_INTERPRETATION_FIXTURE_JSON": (
                    _interpretation_fixture(
                        result_item_id=result_item_id,
                        fact_id=fact_id,
                        statement="MSD evidence supports a bounded diffusion follow-up.",
                    )
                ),
            }
        )
        RedisRQInterpretationQueue(
            redis_url=redis_url, queue_name=queue_names["interpretation"]
        ).enqueue_turn(root.turn_id)
        # Simulate an interpretation process that durably creates the next
        # cycle but cannot publish it. A fresh canonical process then resumes
        # from the persisted Result/assessment/child Turn without rerunning MSD.
        environment["MDI_AGENT2_ORCHESTRATION_ENABLED"] = "0"
        _run_worker(
            queue_names["interpretation"],
            redis_url=redis_url,
            environment=environment,
        )

        with factory.session() as session:
            turns = session.agent2.research_turns.list_for_session(
                session_id, limit=20
            )
        child = next(item for item in turns if item["id"] != root.turn_id)
        assert child["status"] == "RECEIVED"
        recovered = BoundedAutonomyService(
            factory,
            queue=RedisRQAgentTurnQueue(
                redis_url=redis_url,
                queue_name=queue_names["turn"],
            ),
        ).advance_after_interpretation(root.turn_id)
        assert recovered is not None
        assert recovered.child_turn_id == child["id"]
        assert recovered.enqueued is True
        environment["MDI_AGENT2_ORCHESTRATION_ENABLED"] = "1"
        turn_worker = _run_worker(
            queue_names["turn"], redis_url=redis_url, environment=environment
        )
        plan_worker = _run_worker(
            queue_names["plan"], redis_url=redis_url, environment=environment
        )
        with factory.session() as session:
            planned_child = session.agent2.research_turns.get(child["id"])
            planned_decision = (
                session.agent2.research_turn_decisions.get_for_turn(child["id"])
            )
            planned_resolution = (
                session.agent2.research_capability_resolutions.get_for_turn(
                    child["id"]
                )
            )
        assert planned_child["status"] == "PLAN_READY", (
            planned_child.get("error_code"),
            planned_child.get("error_summary"),
            planned_decision,
            planned_resolution,
            turn_worker.stderr[-4000:],
            plan_worker.stderr[-4000:],
        )
        dispatch = ResearchExecutionDispatcher(
            factory,
            queue=RedisRQQueueBackend(
                redis_url=redis_url, queue_name=queue_names["job"]
            ),
        ).dispatch_turn(child["id"])
        assert dispatch.queued is True
        _run_worker(
            queue_names["job"], redis_url=redis_url, environment=environment
        )
        _run_worker(
            queue_names["result"], redis_url=redis_url, environment=environment
        )

        with factory.session() as session:
            diffusion_result = (
                session.agent2.scientific_result_snapshots.get_latest_for_turn(
                    child["id"]
                )
            )
        diffusion_bundle = ScientificResultBundle.model_validate(
            diffusion_result["bundle_json"]
        )
        diffusion_fact = diffusion_bundle.facts[0]
        environment["MDI_AGENT2_INTERPRETATION_FIXTURE_JSON"] = (
            _interpretation_fixture(
                result_item_id=diffusion_bundle.result_items[0].id,
                fact_id=diffusion_fact.fact_id,
                statement="The fitted MSD window provides a qualified diffusion estimate.",
            )
        )
        _run_worker(
            queue_names["interpretation"],
            redis_url=redis_url,
            environment=environment,
        )

        with factory.session() as session:
            final_child = session.agent2.research_turns.get(child["id"])
            child_events = session.agent2.research_turn_events.list_for_turn(
                child["id"]
            )
            child_calls = session.repositories.tool_calls.list_for_job(
                str(final_child["job_id"])
            )
            child_artifacts = session.repositories.artifacts.list_for_job(
                str(final_child["job_id"])
            )
            lineage = session.agent2.research_turns.list_for_session(
                session_id, limit=20
            )
        assert final_child["status"] == "COMPLETED"
        assert [item["toolId"] for item in child_calls] == [
            "trajectory.diffusion"
        ]
        assert len(lineage) == 2
        assert any(
            item["event_type"] == "AUTONOMY_STOPPED" for item in child_events
        )
        diffusion_artifact = child_artifacts[0]
        storage_keys.append(str(diffusion_artifact["storageKey"]))
        diffusion_payload = storage.get_json(
            str(diffusion_artifact["storageKey"])
        )
        assert diffusion_payload["sourceMsd"]["artifactId"] == parent_artifact_id
        assert diffusion_payload["runtimeDiagnostics"]["msdRecomputation"] is False
        assert diffusion_payload["fitWindow"]["startPs"] == msd_payload["lagTimesPs"][0]
        assert diffusion_payload["fitWindow"]["endPs"] == msd_payload["lagTimesPs"][-1]
        assert str(source_ref.version_id) in {
            str(value)
            for value in diffusion_bundle.provenance.source_object_version_ids
        }
        with engine.connect() as connection:
            stop = connection.execute(
                select(research_turn_events)
                .where(
                    research_turn_events.c.turn_id == child["id"],
                    research_turn_events.c.event_type == "AUTONOMY_STOPPED",
                )
            ).mappings().one()
        assert stop["payload_json"]["stop_reason"] == "GOAL_SATISFIED"
    finally:
        for queue_name in queue_names.values():
            try:
                Queue(queue_name, connection=redis).delete(delete_jobs=True)
            except Exception:
                pass
        if storage is not None:
            for key in sorted(set(storage_keys)):
                try:
                    storage.client.delete_object(
                        Bucket=storage.bucket, Key=key
                    )
                except Exception:
                    pass
        if engine is not None:
            engine.dispose()
        try:
            with base_engine.begin() as connection:
                connection.execute(DropSchema(schema_name, cascade=True))
        finally:
            base_engine.dispose()
