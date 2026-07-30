from __future__ import annotations

import os
import uuid

import pytest
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine

from mdi_api.repositories import SqlAlchemyRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import AnalysisIntentRequest, DeterministicAnalysisIntentBuilder, MockLLMProvider
from mdi_schemas import (
    AnalysisIntent,
    CapabilityNeed,
    DesiredOutput,
    ScientificIntent,
    compute_analysis_intent_hash,
    deterministic_intent_id,
    DataProfile,
)


def _service_profile(*, dataset_id: str, profile_id: str) -> DataProfile:
    return DataProfile.model_validate(
        {
            "profileId": profile_id,
            "datasetId": dataset_id,
            "version": "2",
            "datasetType": "tabular",
            "profileContractVersion": "2.0",
            "semanticRulesVersion": "phase10k1.material_profile_semantics.v1",
            "semanticHash": "a" * 64,
            "semanticColumns": [
                {
                    "objectId": "table_1",
                    "column": "formula",
                    "dtype": "string",
                    "roles": [{"role": "material_formula", "authority": "canonical_name"}],
                },
                {
                    "objectId": "table_1",
                    "column": "formation_energy",
                    "dtype": "float64",
                    "unit": "eV",
                    "roles": [{"role": "material_property", "authority": "explicit_metadata"}],
                },
            ],
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


def test_service_profile_fixture_is_a_ready_exact_profile() -> None:
    profile = _service_profile(dataset_id="dataset_fixture", profile_id="profile_fixture")
    intent = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(
            raw_goal="Analyze this dataset composition distribution and anomaly candidates.",
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
        ),
        profile=profile,
    )
    assert intent.outcome.value == "READY"


@pytest.mark.integration
def test_capability_planner_postgres_ready_and_non_ready_persistence() -> None:
    url = os.environ.get("DATABASE_URL") or os.environ.get("MDI_DATABASE_URL")
    if not url or "postgres" not in url:
        pytest.skip("No PostgreSQL DATABASE_URL configured")
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", url)
    alembic_upgrade(config, "head")

    suffix = uuid.uuid4().hex[:12]
    project_id = f"project_capability_{suffix}"
    dataset_id = f"dataset_capability_{suffix}"
    profile_id = f"profile_capability_{suffix}"
    profile = _service_profile(dataset_id=dataset_id, profile_id=profile_id)
    engine = create_engine(url, future=True)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    repos.projects.save({"projectId": project_id, "name": project_id, "createdBy": "user_local"})
    repos.datasets.save(
        {"datasetId": dataset_id, "projectId": project_id, "name": dataset_id, "createdBy": "user_local"}
    )
    repos.data_profiles.save(profile)
    persisted_profile = DataProfile.model_validate(repos.data_profiles.get(profile_id))
    assert persisted_profile == profile
    persisted_intent = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(
            raw_goal="Analyze this dataset composition distribution and anomaly candidates.",
            dataset_id=dataset_id,
            profile_id=profile_id,
        ),
        profile=persisted_profile,
    )
    assert persisted_intent.outcome.value == "READY"

    ready = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Analyze this dataset composition distribution and anomaly candidates.",
            projectId=project_id,
            datasetId=dataset_id,
            profileId=profile_id,
            intentSchemaVersion="1.0",
            provider="mock",
        ),
        provider=MockLLMProvider(fixed_plan={"invalid": "legacy provider must not be called"}),
        repositories=repos,
    )
    assert ready.ok is True
    assert ready.capability_outcome == "PLAN_READY"
    assert ready.plan and ready.plan["schemaVersion"] == "0.1"
    assert ready.job_id and ready.plan_id and ready.capability_decision and ready.eligibility_resolution
    binding = repos.capability_planning.get_execution_for_job(ready.job_id)
    assert binding and binding["decisionId"] == ready.capability_decision["decisionId"]

    source = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(
            raw_goal="Analyze this dataset composition distribution.",
            dataset_id=dataset_id,
            profile_id=profile_id,
        ),
        profile=profile,
    )
    payload = source.model_dump(mode="json")
    payload["scientificIntents"] = [ScientificIntent.report_or_export.value]
    payload["desiredOutputs"] = [DesiredOutput.report.value]
    payload["requiredCapabilityNeeds"] = [CapabilityNeed.tabular_data.value]
    payload["optionalCapabilityNeeds"] = []
    payload["intentHash"] = compute_analysis_intent_hash(payload)
    payload["intentId"] = deterministic_intent_id(payload["intentHash"])
    unsupported = AnalysisIntent.model_validate(payload)
    repos.analysis_intents.save_intent(
        {"projectId": project_id, "analysisIntent": unsupported.model_dump(mode="json"), "createdBy": "user_local"}
    )
    blocked = planner_jobs(
        PlannerJobsRequest(
            userPrompt=unsupported.rawGoal,
            projectId=project_id,
            datasetId=dataset_id,
            profileId=profile_id,
            intentSchemaVersion="1.0",
            intentId=unsupported.intentId,
            provider="mock",
            enqueue=True,
        ),
        repositories=repos,
    )
    assert blocked.ok is False
    assert blocked.capability_outcome == "CAPABILITY_MISMATCH"
    assert blocked.plan_id is None and blocked.job_id is None and blocked.enqueued is False
    assert repos.analysis_intents.get_execution(unsupported.intentId) is None
    engine.dispose()
