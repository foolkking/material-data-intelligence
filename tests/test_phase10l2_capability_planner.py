from __future__ import annotations

import json
from pathlib import Path

import pytest
from alembic.command import downgrade as alembic_downgrade
from alembic.command import stamp as alembic_stamp
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect, text

from mdi_api.db import metadata
from mdi_api.repositories import InMemoryRepositoryBundle, SqlAlchemyRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, get_planner_job, planner_jobs
from mdi_llm import (
    AnalysisIntentRequest,
    CapabilityContextValidator,
    CapabilityPlanningError,
    ClarificationSubmission,
    DeterministicAnalysisIntentBuilder,
    MockLLMProvider,
    OpenAICompatibleProvider,
    plan_capabilities,
)
from mdi_schemas import (
    AnalysisIntent,
    CapabilityNeed,
    ClarificationAnswer,
    DesiredOutput,
    EligibilityResolution,
    ScientificIntent,
    compute_analysis_intent_hash,
    deterministic_intent_id,
)
from mdi_tool_registry import build_registry_snapshot, load_manifests

from tests.test_phase10l1_analysis_intent import _profile, _request


def _ready_target_intent(target: str) -> tuple[AnalysisIntent, object]:
    profile = _profile(targets=("formation_energy", "band_gap"))
    builder = DeterministicAnalysisIntentBuilder()
    parent = builder.build(_request("Analyze where the regression model predictions are wrong."), profile=profile)
    question = parent.clarification.questions[0]
    option = next(item for item in question.options if target in item.value)
    intent = builder.clarify(
        parent,
        ClarificationSubmission(
            intent_id=parent.intentId,
            expected_profile_semantic_hash=profile.semanticHash or "",
            answers=(ClarificationAnswer(questionId=question.questionId, selectedValues=[option.value]),),
        ),
        profile=profile,
    )
    return intent, profile


def _report_only_intent() -> tuple[AnalysisIntent, object]:
    profile = _profile()
    source = DeterministicAnalysisIntentBuilder().build(
        _request("Analyze this dataset composition distribution."),
        profile=profile,
    )
    payload = source.model_dump(mode="json")
    payload["scientificIntents"] = [ScientificIntent.report_or_export.value]
    payload["desiredOutputs"] = [DesiredOutput.report.value]
    payload["requiredCapabilityNeeds"] = [CapabilityNeed.tabular_data.value]
    payload["optionalCapabilityNeeds"] = []
    payload["intentHash"] = compute_analysis_intent_hash(payload)
    payload["intentId"] = deterministic_intent_id(payload["intentHash"])
    return AnalysisIntent.model_validate(payload), profile


def _resource_profile(*, object_id: str, object_type: str, kind: str, capabilities: list[str]) -> object:
    return _profile(
        resources=[
            {
                "objectId": object_id,
                "objectType": object_type,
                "objectHash": "c" * 64,
                "kind": kind,
                "capabilities": capabilities,
            }
        ]
    )


def test_registry_planner_metadata_covers_actual_registry_deterministically() -> None:
    registry = load_manifests()
    first, metadata_by_id = build_registry_snapshot(registry)
    second, second_metadata = build_registry_snapshot(registry)
    assert len(first.tools) == len(registry.tools) == 53
    assert first == second
    assert set(metadata_by_id) == set(second_metadata) == {item.toolId for item in registry.tools}
    assert first.tools == sorted(first.tools, key=lambda item: (item.toolId, item.toolVersion))
    assert metadata_by_id["structure.brillouin_zone"].capabilityNeeds == [
        CapabilityNeed.reciprocal_space_resource,
        CapabilityNeed.structure_resource,
    ]
    assert DesiredOutput.plot not in metadata_by_id["ml.uncertainty_evaluation"].desiredOutputs
    assert metadata_by_id["structure.viewer_scene_metadata"].availability.value == "DEPLOYMENT_UNAVAILABLE"
    assert metadata_by_id["ml.uncertainty_calibration"].availability.value != "AVAILABLE"


def test_checked_in_capability_schema_and_typescript_match_contract() -> None:
    from mdi_schemas import CapabilityPlanningDecision, EligibilityResolution, ToolPlannerMetadata

    checked_in = json.loads(Path("packages/schemas/json/capability-planning-v1.schema.json").read_text(encoding="utf-8"))
    assert checked_in == {
        "eligibilityResolution": EligibilityResolution.model_json_schema(),
        "planningDecision": CapabilityPlanningDecision.model_json_schema(),
        "toolPlannerMetadata": ToolPlannerMetadata.model_json_schema(),
    }
    source = Path("packages/schemas/src/index.ts").read_text(encoding="utf-8")
    for field in EligibilityResolution.model_fields:
        assert f"{field}:" in source
    for field in CapabilityPlanningDecision.model_fields:
        assert f"{field}:" in source


def test_deterministic_resolution_selection_and_provider_isolation() -> None:
    profile = _profile()
    intent = DeterministicAnalysisIntentBuilder().build(
        _request("Analyze this dataset composition distribution and anomaly candidates."),
        profile=profile,
    )
    first = plan_capabilities(intent, profile=profile, registry=load_manifests(), provider=MockLLMProvider())
    second = plan_capabilities(intent, profile=profile, registry=load_manifests(), provider=MockLLMProvider())
    assert first.outcome.value == "PLAN_READY"
    assert first.resolution == second.resolution
    assert first.decision == second.decision
    assert list(first.provider_visible_tool_ids) == first.resolution.eligibleToolIds
    assert set(first.provider_visible_tool_ids).isdisjoint(first.resolution.rejectedToolIds)
    assert {item.toolId for item in first.decision.selections}.issubset(first.provider_visible_tool_ids)
    assert first.plan is not None and first.plan.schemaVersion == "0.1"


def test_formation_energy_and_band_gap_bind_exact_distinct_groups() -> None:
    registry = load_manifests()
    formation_intent, profile = _ready_target_intent("formation_energy")
    band_gap_intent, _ = _ready_target_intent("band_gap")
    formation = plan_capabilities(formation_intent, profile=profile, registry=registry, provider=MockLLMProvider())
    band_gap = plan_capabilities(band_gap_intent, profile=profile, registry=registry, provider=MockLLMProvider())
    assert formation.outcome.value == band_gap.outcome.value == "PLAN_READY"
    assert formation.decision.selections[0].toolId == band_gap.decision.selections[0].toolId == "ml.regression_evaluation"
    formation_groups = next(item.value for item in formation.decision.selections[0].boundParameters if item.parameter == "groupIds")
    band_gap_groups = next(item.value for item in band_gap.decision.selections[0].boundParameters if item.parameter == "groupIds")
    assert formation_groups == ["regression_0"]
    assert band_gap_groups == ["regression_1"]
    assert formation_groups != band_gap_groups


def test_uncertainty_selects_only_explicit_uncertainty_capability() -> None:
    profile = _profile()
    intent = DeterministicAnalysisIntentBuilder().build(
        _request("Analyze model prediction errors and whether uncertainty is trustworthy."),
        profile=profile,
    )
    result = plan_capabilities(intent, profile=profile, registry=load_manifests(), provider=MockLLMProvider())
    assert result.outcome.value == "PLAN_READY"
    assert [item.toolId for item in result.decision.selections] == ["ml.uncertainty_evaluation"]
    assert "ml.basic_metrics" in result.resolution.rejectedToolIds


def test_prediction_request_uses_registered_evaluation_not_basic_metrics_or_registry_order() -> None:
    intent, profile = _ready_target_intent("formation_energy")
    result = plan_capabilities(intent, profile=profile, registry=load_manifests(), provider=MockLLMProvider())
    assert result.outcome.value == "PLAN_READY"
    assert [item.toolId for item in result.decision.selections] == ["ml.regression_evaluation"]
    assert result.decision.selections[0].toolId != load_manifests().tools[0].toolId
    assert "ml.basic_metrics" in result.resolution.rejectedToolIds


def test_phonon_request_never_falls_through_to_ml_table_or_generic_visualization() -> None:
    profile = _resource_profile(
        object_id="phonon_band_1", object_type="PhononBand", kind="phonon", capabilities=["phonon"]
    )
    intent = DeterministicAnalysisIntentBuilder().build(
        _request("Analyze this phonon calculation."), profile=profile
    )
    result = plan_capabilities(intent, profile=profile, registry=load_manifests(), provider=MockLLMProvider())
    assert result.outcome.value == "PLAN_READY"
    assert [item.toolId for item in result.decision.selections] == ["phonon.band"]
    selected = set(result.resolution.eligibleToolIds)
    assert selected and all(tool_id.startswith("phonon.") for tool_id in selected)
    assert {"ml.basic_metrics", "table.numeric_summary", "viz.scatter"}.issubset(result.resolution.rejectedToolIds)


def test_resource_kinds_are_not_interchangeable() -> None:
    profile = _resource_profile(
        object_id="structure_1", object_type="Structure", kind="structure", capabilities=["structure"]
    )
    intent = DeterministicAnalysisIntentBuilder().build(
        _request("Analyze this crystal structure."), profile=profile
    )
    result = plan_capabilities(intent, profile=profile, registry=load_manifests(), provider=MockLLMProvider())
    assert result.outcome.value == "PLAN_READY"
    assert result.decision.selections
    assert all(item.toolId.startswith("structure.") for item in result.decision.selections)
    assert {"ml.regression_evaluation", "phonon.band", "table.numeric_summary"}.issubset(
        result.resolution.rejectedToolIds
    )
    rejection = next(
        item for item in result.resolution.evaluatedCandidates if item.toolId == "phonon.band"
    )
    assert "RESOURCE_KIND_MISMATCH" in {reason.code for reason in rejection.reasons}


def test_broad_dataset_analysis_uses_structured_baseline_not_first_registry_tool() -> None:
    profile = _profile()
    intent = DeterministicAnalysisIntentBuilder().build(_request("Analyze this dataset."), profile=profile)
    result = plan_capabilities(intent, profile=profile, registry=load_manifests(), provider=MockLLMProvider())
    assert result.outcome.value == "PLAN_READY"
    assert [item.toolId for item in result.decision.selections] == ["dataset.materials_explorer"]
    assert result.decision.selections[0].toolId != load_manifests().tools[0].toolId


def test_strict_llm_candidate_isolation_and_one_repair() -> None:
    profile = _profile()
    intent = DeterministicAnalysisIntentBuilder().build(
        _request("Analyze this dataset composition distribution and anomaly candidates."),
        profile=profile,
    )
    calls: list[dict[str, object]] = []

    def transport(**kwargs: object) -> dict[str, object]:
        calls.append(kwargs)
        messages = kwargs["messages"]
        context = json.loads(messages[-1]["content"])
        selected = "dataset.composition_space" if len(calls) == 1 else "dataset.materials_explorer"
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "schemaVersion": "1.0",
                                "resolutionId": context["eligibleCandidates"]["resolutionId"],
                                "selectedToolIds": [selected],
                            },
                            separators=(",", ":"),
                        )
                    },
                    "finish_reason": "stop",
                }
            ]
        }

    result = plan_capabilities(
        intent,
        profile=profile,
        registry=load_manifests(),
        provider=OpenAICompatibleProvider(transport=transport),
    )
    assert result.outcome.value == "PLAN_READY"
    assert result.decision.provenance.repairCount == 1
    assert len(calls) == 2
    for call in calls:
        context = json.loads(call["messages"][-1]["content"])
        exposed = {item["toolId"] for item in context["eligibleCandidates"]["candidates"]}
        assert exposed == set(result.resolution.eligibleToolIds)
        assert exposed.isdisjoint(result.resolution.rejectedToolIds)


def test_llm_invented_candidate_fails_without_mock_fallback() -> None:
    profile = _profile()
    intent = DeterministicAnalysisIntentBuilder().build(
        _request("Analyze this dataset composition distribution."),
        profile=profile,
    )

    def transport(**kwargs: object) -> dict[str, object]:
        context = json.loads(kwargs["messages"][-1]["content"])
        payload = {
            "schemaVersion": "1.0",
            "resolutionId": context["eligibleCandidates"]["resolutionId"],
            "selectedToolIds": ["invented.tool"],
        }
        return {"choices": [{"message": {"content": json.dumps(payload)}, "finish_reason": "stop"}]}

    result = plan_capabilities(
        intent,
        profile=profile,
        registry=load_manifests(),
        provider=OpenAICompatibleProvider(transport=transport),
    )
    assert result.outcome.value == "VALIDATION_FAILED"
    assert result.plan is None
    assert result.decision.provenance.provider == "openai_compatible"
    assert result.decision.provenance.repairCount == 0
    assert result.decision.diagnostics[0].code == "CAPABILITY_LLM_CANDIDATE_INVALID"


@pytest.mark.parametrize(
    "raw",
    [
        '```json\n{"schemaVersion":"1.0"}\n```',
        '{"schemaVersion":"1.0","schemaVersion":"1.0"}',
        'selection: {"schemaVersion":"1.0"}',
        '[]',
        '{"schemaVersion":"1.0","resolutionId":"invented","selectedToolIds":[],"unknown":true}',
    ],
)
def test_llm_strict_json_rejects_wrappers_duplicates_unknown_fields_and_non_objects(raw: str) -> None:
    profile = _profile()
    intent = DeterministicAnalysisIntentBuilder().build(
        _request("Analyze this dataset composition distribution."), profile=profile
    )

    def transport(**_kwargs: object) -> dict[str, object]:
        return {"choices": [{"message": {"content": raw}, "finish_reason": "stop"}]}

    result = plan_capabilities(
        intent, profile=profile, registry=load_manifests(),
        provider=OpenAICompatibleProvider(transport=transport),
    )
    assert result.outcome.value == "VALIDATION_FAILED"
    assert result.plan is None
    assert result.decision.provenance.provider == "openai_compatible"
    assert result.decision.provenance.repairCount == 0


def test_llm_repair_exhaustion_records_one_attempt_and_never_falls_back() -> None:
    profile = _profile()
    intent = DeterministicAnalysisIntentBuilder().build(
        _request("Analyze this dataset composition distribution and anomaly candidates."), profile=profile
    )
    calls = 0

    def transport(**kwargs: object) -> dict[str, object]:
        nonlocal calls
        calls += 1
        context = json.loads(kwargs["messages"][-1]["content"])
        payload = {
            "schemaVersion": "1.0",
            "resolutionId": context["eligibleCandidates"]["resolutionId"],
            "selectedToolIds": ["dataset.composition_space"],
        }
        return {"choices": [{"message": {"content": json.dumps(payload)}, "finish_reason": "stop"}]}

    result = plan_capabilities(
        intent, profile=profile, registry=load_manifests(),
        provider=OpenAICompatibleProvider(transport=transport),
    )
    assert calls == 2
    assert result.outcome.value == "VALIDATION_FAILED"
    assert result.plan is None
    assert result.decision.provenance.repairCount == 1
    assert result.decision.provenance.initialDecisionHash
    assert len(result.decision.provenance.repairDiagnostics) == 2


def test_llm_invalid_repair_output_preserves_consumed_repair_budget() -> None:
    profile = _profile()
    intent = DeterministicAnalysisIntentBuilder().build(
        _request("Analyze this dataset composition distribution and anomaly candidates."), profile=profile
    )
    calls = 0

    def transport(**kwargs: object) -> dict[str, object]:
        nonlocal calls
        calls += 1
        context = json.loads(kwargs["messages"][-1]["content"])
        content = (
            json.dumps({
                "schemaVersion": "1.0",
                "resolutionId": context["eligibleCandidates"]["resolutionId"],
                "selectedToolIds": ["dataset.composition_space"],
            })
            if calls == 1 else "```json\n{}\n```"
        )
        return {"choices": [{"message": {"content": content}, "finish_reason": "stop"}]}

    result = plan_capabilities(
        intent, profile=profile, registry=load_manifests(),
        provider=OpenAICompatibleProvider(transport=transport),
    )
    assert calls == 2
    assert result.outcome.value == "VALIDATION_FAILED"
    assert result.plan is None
    assert result.decision.provenance.repairCount == 1
    assert result.decision.provenance.repairDiagnostics[-1].code == "CAPABILITY_LLM_JSON_INVALID"


def test_context_validator_rejects_tampered_resolution_and_plan() -> None:
    profile = _profile()
    intent = DeterministicAnalysisIntentBuilder().build(
        _request("Analyze this dataset composition distribution."), profile=profile
    )
    registry = load_manifests()
    result = plan_capabilities(intent, profile=profile, registry=registry, provider=MockLLMProvider())
    assert result.plan is not None
    tampered_candidate = result.resolution.evaluatedCandidates[0].model_copy(update={"rankFacts": ["tampered"]})
    tampered = result.resolution.model_copy(
        update={"evaluatedCandidates": [tampered_candidate, *result.resolution.evaluatedCandidates[1:]]}
    )
    with pytest.raises(CapabilityPlanningError, match="current facts"):
        CapabilityContextValidator().validate(
            intent=intent, profile=profile, registry=registry, resolution=tampered,
            decision=result.decision, plan=result.plan,
        )
    invalid_plan = result.plan.model_copy(update={"goal": "different goal"})
    with pytest.raises(CapabilityPlanningError, match="selection identity"):
        CapabilityContextValidator().validate(
            intent=intent, profile=profile, registry=registry, resolution=result.resolution,
            decision=result.decision, plan=invalid_plan,
        )


def test_capability_records_are_immutable_and_idempotent() -> None:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    profile = _profile()
    repos.projects.save({"projectId": "project_1", "name": "Project", "createdBy": "user_1"})
    repos.datasets.save({"datasetId": profile.datasetId, "projectId": "project_1", "name": "Dataset", "createdBy": "user_1"})
    intent = DeterministicAnalysisIntentBuilder().build(
        _request("Analyze this dataset composition distribution."),
        profile=profile,
    )
    repos.analysis_intents.save_intent({"projectId": "project_1", "analysisIntent": intent.model_dump(mode="json"), "createdBy": "user_1"})
    result = plan_capabilities(intent, profile=profile, registry=load_manifests(), provider=MockLLMProvider())
    resolution_record = {"eligibilityResolution": result.resolution.model_dump(mode="json"), "createdBy": "user_1"}
    decision_record = {"capabilityDecision": result.decision.model_dump(mode="json"), "createdBy": "user_1"}
    assert repos.capability_planning.save_resolution(resolution_record)["resolutionHash"] == result.resolution.resolutionHash
    assert repos.capability_planning.save_resolution(resolution_record)["resolutionHash"] == result.resolution.resolutionHash
    assert repos.capability_planning.save_decision(decision_record)["decisionHash"] == result.decision.decisionHash
    assert repos.capability_planning.save_decision(decision_record)["decisionHash"] == result.decision.decisionHash


def test_phase10l2_migration_upgrades_downgrades_and_reupgrades(tmp_path: Path) -> None:
    database = tmp_path / "phase10l2-migration.sqlite"
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    expected = {
        "capability_eligibility_resolutions",
        "capability_planning_decisions",
        "capability_planning_executions",
    }
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE analysis_intents (id VARCHAR(96) PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE analysis_plans (id VARCHAR(96) PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE jobs (id VARCHAR(64) PRIMARY KEY)"))
    alembic_stamp(config, "0003_phase10l1_intents")
    alembic_upgrade(config, "head")
    assert expected.issubset(inspect(engine).get_table_names())
    alembic_downgrade(config, "0003_phase10l1_intents")
    assert expected.isdisjoint(inspect(engine).get_table_names())
    alembic_upgrade(config, "head")
    assert expected.issubset(inspect(engine).get_table_names())
    engine.dispose()


def test_canonical_api_uses_capability_path_and_non_ready_creates_no_job() -> None:
    repos = InMemoryRepositoryBundle.create()
    ready_profile = _profile()
    repos.data_profiles.save(ready_profile)
    ready = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Analyze this dataset composition distribution and anomaly candidates.",
            projectId="project_1",
            datasetId=ready_profile.datasetId,
            profileId=ready_profile.profileId,
            intentSchemaVersion="1.0",
            provider="mock",
        ),
        provider=MockLLMProvider(fixed_plan={"invalid": "legacy provider must not be called"}),
        repositories=repos,
    )
    assert ready.ok is True
    assert ready.capability_outcome == "PLAN_READY"
    assert ready.plan_source == "capability_planner"
    assert ready.plan and ready.plan["schemaVersion"] == "0.1"
    assert len(repos.capability_planning.resolutions) == 1
    assert len(repos.capability_planning.decisions) == 1
    assert len(repos.capability_planning.executions) == 1
    detail = get_planner_job(ready.job_id or "", repositories=repos)
    assert detail["capabilityPlanningOutcome"] == "PLAN_READY"

    non_ready_repos = InMemoryRepositoryBundle.create()
    report_intent, report_profile = _report_only_intent()
    non_ready_repos.data_profiles.save(report_profile)
    non_ready_repos.projects.save({"projectId": "project_1", "name": "Project", "createdBy": "user_1"})
    non_ready_repos.datasets.save({"datasetId": report_profile.datasetId, "projectId": "project_1", "name": "Dataset", "createdBy": "user_1"})
    non_ready_repos.analysis_intents.save_intent(
        {"projectId": "project_1", "analysisIntent": report_intent.model_dump(mode="json"), "createdBy": "user_1"}
    )
    blocked = planner_jobs(
        PlannerJobsRequest(
            userPrompt=report_intent.rawGoal,
            projectId="project_1",
            datasetId=report_profile.datasetId,
            profileId=report_profile.profileId,
            intentSchemaVersion="1.0",
            intentId=report_intent.intentId,
            provider="mock",
            enqueue=True,
        ),
        repositories=non_ready_repos,
    )
    assert blocked.ok is False
    assert blocked.capability_outcome == "CAPABILITY_MISMATCH"
    assert blocked.plan_id is blocked.job_id is None
    assert blocked.enqueued is False
    assert non_ready_repos.analysis_plans.records == {}
    assert non_ready_repos.jobs.records == {}
    assert len(non_ready_repos.capability_planning.resolutions) == 1
    assert len(non_ready_repos.capability_planning.decisions) == 1
    assert non_ready_repos.capability_planning.executions == {}
