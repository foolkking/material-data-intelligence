from __future__ import annotations

from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import (
    PlannerJobsRequest,
    get_planner_job_dependencies,
    planner_jobs,
)
from mdi_llm import MockLLMProvider

from tests.test_phase10l1_analysis_intent import _profile


def _phonon_profile():
    return _profile(
        resources=[
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
        targets=(),
        uncertainty=False,
    )


def test_canonical_intent_path_persists_analysis_plan_02_and_dependency_audit() -> None:
    repos = InMemoryRepositoryBundle.create()
    profile = _phonon_profile()
    repos.data_profiles.save(profile)

    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Analyze this phonon calculation.",
            projectId="project_l3",
            datasetId=profile.datasetId,
            profileId=profile.profileId,
            intentSchemaVersion="1.0",
            selectedResourceIds=["phonon_band_1", "phonon_dos_1"],
            provider="mock",
        ),
        provider=MockLLMProvider(fixed_plan={"invalid": "legacy path must not run"}),
        repositories=repos,
    )

    assert result.ok is True
    assert result.capability_outcome == "PLAN_READY"
    assert result.plan_schema_version == "0.2"
    assert result.plan and result.plan["schemaVersion"] == "0.2"
    assert [step["toolId"] for step in result.plan["steps"]] == [
        "phonon.band",
        "phonon.band_dos",
        "phonon.dos",
    ]
    assert len(result.dependency_bindings) == 2
    assert result.graph_hash == result.plan["graphHash"]
    assert set(result.topological_order) == {step["stepId"] for step in result.plan["steps"]}
    assert result.enqueued is False

    audit = get_planner_job_dependencies(result.job_id or "", repositories=repos)
    assert audit["planSchemaVersion"] == "0.2"
    assert audit["graphHash"] == result.graph_hash
    assert audit["dependencyBindings"] == result.dependency_bindings
    assert len(audit["plannedBindingRecords"]) == 2
    assert audit["execution"] is None
    assert audit["bindingResolutions"] == []
    assert audit["artifactLineage"] == []


def test_unselected_multi_resource_intent_creates_no_plan_job_or_queue_message() -> None:
    repos = InMemoryRepositoryBundle.create()
    profile = _phonon_profile()
    repos.data_profiles.save(profile)

    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Analyze this phonon calculation.",
            projectId="project_l3",
            datasetId=profile.datasetId,
            profileId=profile.profileId,
            intentSchemaVersion="1.0",
            provider="mock",
            enqueue=True,
        ),
        repositories=repos,
    )

    assert result.ok is False
    assert result.intent_outcome == "NEEDS_CLARIFICATION"
    assert result.error_code == "INTENT_CLARIFICATION_REQUIRED"
    assert result.plan_id is None
    assert result.job_id is None
    assert result.plan is None
    assert result.enqueued is False
    assert repos.analysis_plans.records == {}
    assert repos.jobs.records == {}
    assert repos.dependency_execution.plan_bindings == {}
    assert repos.dependency_execution.executions == {}
