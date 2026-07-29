from __future__ import annotations

import os
import uuid

import pytest
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine

from mdi_api.repositories import SqlAlchemyRepositoryBundle, compute_plan_hash
from mdi_llm import AnalysisIntentRequest, DeterministicAnalysisIntentBuilder
from mdi_schemas import AnalysisPlan, DataProfile


@pytest.mark.integration
def test_analysis_intent_postgres_persistence_and_plan_job_association() -> None:
    url = os.environ.get("DATABASE_URL") or os.environ.get("MDI_DATABASE_URL")
    if not url or "postgres" not in url:
        pytest.skip("No PostgreSQL DATABASE_URL configured")
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", url)
    alembic_upgrade(config, "head")

    suffix = uuid.uuid4().hex[:12]
    project_id = f"project_intent_{suffix}"
    dataset_id = f"dataset_intent_{suffix}"
    profile_id = f"profile_intent_{suffix}"
    plan_id = f"plan_intent_{suffix}"
    job_id = f"job_intent_{suffix}"
    profile = DataProfile.model_validate(
        {
            "profileId": profile_id,
            "datasetId": dataset_id,
            "version": "2",
            "datasetType": "tabular",
            "profileContractVersion": "2.0",
            "semanticRulesVersion": "phase10k1.material_profile_semantics.v1",
            "semanticHash": "a" * 64,
            "resourceSemantics": [
                {
                    "objectId": "table_1",
                    "objectType": "DataFrame",
                    "objectHash": "b" * 64,
                    "kind": "dataframe",
                    "capabilities": ["table", "composition"],
                }
            ],
            "sampleIdentity": {
                "policy": "object_hash_row_index",
                "datasetVersion": "dataset_version_2",
                "objectIds": ["table_1"],
            },
            "createdAt": "2026-07-29T00:00:00+00:00",
        }
    )
    intent = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(
            raw_goal="Analyze this dataset composition distribution.",
            dataset_id=dataset_id,
            profile_id=profile_id,
        ),
        profile=profile,
    )
    plan = AnalysisPlan.model_validate(
        {
            "schemaVersion": "0.1",
            "goal": intent.rawGoal,
            "datasetId": dataset_id,
            "profileId": profile_id,
            "toolRegistryVersion": "0.1.0",
            "steps": [
                {
                    "stepId": "step_1",
                    "toolId": "ml.basic_metrics",
                    "purpose": "Regression metrics",
                    "reason": "Service-backed association fixture.",
                    "inputRefs": [],
                    "params": {},
                    "output": {"artifactTypes": ["metrics_json"]},
                }
            ],
        }
    )

    engine = create_engine(url, future=True)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    repos.projects.save({"projectId": project_id, "name": project_id, "createdBy": "user_local"})
    repos.datasets.save({"datasetId": dataset_id, "projectId": project_id, "name": dataset_id, "createdBy": "user_local"})
    repos.data_profiles.save(profile)
    repos.analysis_intents.save_intent(
        {"projectId": project_id, "analysisIntent": intent.model_dump(mode="json"), "createdBy": "user_local"}
    )
    repos.analysis_plans.save_plan(
        {
            "planId": plan_id,
            "projectId": project_id,
            "datasetId": dataset_id,
            "profileId": profile_id,
            "analysisPlan": plan.model_dump(mode="json"),
            "planHash": compute_plan_hash(plan),
            "validationStatus": "validated",
            "createdBy": "user_local",
        }
    )
    repos.jobs.save(
        {
            "jobId": job_id,
            "projectId": project_id,
            "datasetId": dataset_id,
            "planId": plan_id,
            "status": "created",
            "createdBy": "user_local",
        }
    )
    repos.analysis_intents.attach_execution(intent.intentId, plan_id, job_id)

    stored = repos.analysis_intents.get_intent(intent.intentId)
    binding = repos.analysis_intents.get_execution(intent.intentId)
    assert stored["intentHash"] == intent.intentHash
    assert binding is not None
    assert binding["planId"] == plan_id
    assert binding["jobId"] == job_id
