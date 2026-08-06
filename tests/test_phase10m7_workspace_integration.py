from __future__ import annotations

import json
from pathlib import Path

from mdi_api.report_composition import ReportCompositionService
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.workspaces import WorkspaceProjectionService
from mdi_schemas import DataProfile, ReportCompositionRequest


ROOT = Path(__file__).resolve().parents[1]
LIVE_CASE = ROOT / "docs/phase10l/evidence/phase10l5_natural_language_closure/deepseek_live/case_04_phonon.json"


def _load_live_case() -> dict:
    return json.loads(LIVE_CASE.read_text(encoding="utf-8"))


def _replay_persisted_authorities(case: dict) -> InMemoryRepositoryBundle:
    repos = InMemoryRepositoryBundle.create()
    project_id = case["job"]["projectId"]
    dataset_id = case["profile"]["datasetId"]
    repos.projects.save({"projectId": project_id, "name": "Retained DeepSeek evidence", "createdBy": "user_local"})
    repos.datasets.save({"datasetId": dataset_id, "projectId": project_id, "name": "Retained phonon source", "createdBy": "user_local"})
    repos.data_profiles.save(DataProfile.model_validate(case["profile"]))
    repos.analysis_intents.save_intent({"projectId": project_id, "analysisIntent": case["intent"], "createdBy": "user_local"})
    repos.capability_planning.save_resolution({"eligibilityResolution": case["eligibilityResolution"], "createdBy": "user_local"})
    repos.capability_planning.save_decision({"capabilityDecision": case["capabilityDecision"], "createdBy": "user_local"})
    repos.analysis_plans.save_plan(case["analysisPlan"])
    repos.jobs.save(case["job"])
    repos.analysis_intents.attach_execution(case["intent"]["intentId"], case["planId"], case["jobId"])
    repos.capability_planning.attach_execution(
        case["capabilityDecision"]["decisionId"],
        case["intent"]["intentId"],
        case["planId"],
        case["jobId"],
    )

    dependencies = case["dependencies"]
    repos.dependency_execution.save_plan_bindings(
        case["planId"], case["planHash"], case["graphHash"], dependencies["dependencyBindings"]
    )
    for record in dependencies["bindingResolutions"]:
        repos.dependency_execution.save_binding_resolution(record)
    repos.dependency_execution.save_execution(dependencies["execution"])
    for record in dependencies["artifactLineage"]:
        repos.dependency_execution.save_lineage(record)
    for record in case["toolCalls"]:
        repos.tool_calls.save(record)
    for record in case["artifacts"]:
        replay_record = {
            **record,
            "storageKey": f"retained-evidence/{record['id']}",
            "storageProvider": "local",
        }
        repos.artifacts.save(replay_record)
    repos.interpretations.save_interpretation(
        case["evidenceBundle"],
        case["interpretation"]["interpretation"],
        case["interpretation"]["execution"],
    )
    return repos


def test_retained_real_deepseek_chain_projects_saves_and_composes_without_provider_calls() -> None:
    case = _load_live_case()
    assert case["provider"] == "deepseek"
    assert case["verdict"] == "PASS"
    assert case["invariants"]["providerIsDeepSeek"] is True
    assert case["invariants"]["noFallback"] is True
    assert case["invariants"]["persistedChainComplete"] is True
    assert case["invariants"]["providerVisibleEqualsEligible"] is True
    assert case["planSchemaVersion"] == "0.2"
    assert len(case["dependencies"]["dependencyBindings"]) == 2

    repos = _replay_persisted_authorities(case)
    workspace_service = WorkspaceProjectionService(repos)
    snapshot, created = workspace_service.project_job(
        source_job_id=case["jobId"],
        created_by="user_local",
        title="Verified DeepSeek phonon Workspace",
    )
    workspace = snapshot.body["workspace"]
    assert created is True
    assert workspace["projectId"] == case["job"]["projectId"]
    assert workspace["datasetId"] == case["profile"]["datasetId"]
    assert workspace["profileId"] == case["profile"]["profileId"]
    assert workspace["profileSemanticHash"] == case["profile"]["semanticHash"]
    assert workspace["intentId"] == case["intent"]["intentId"]
    assert workspace["intentSemanticHash"] == case["intent"]["intentHash"]
    assert workspace["planId"] == case["planId"]
    assert workspace["planHash"] == case["planHash"]
    assert workspace["planSchemaVersion"] == "0.2"
    assert workspace["artifactCount"] == len(case["artifacts"])
    assert workspace["interpretationCount"] == 1

    saved = workspace_service.patch_workspace(
        workspace_id=workspace["workspaceId"],
        expected_revision=workspace["revision"],
        changes={"title": "Saved verified DeepSeek phonon Workspace"},
        updated_by="user_local",
    )
    assert saved.body["workspace"]["revision"] == workspace["revision"] + 1
    reopened = workspace_service.get_snapshot(workspace["workspaceId"])
    assert reopened.body["workspace"]["title"] == "Saved verified DeepSeek phonon Workspace"
    assert reopened.body["workspace"]["planHash"] == case["planHash"]

    report_service = ReportCompositionService(repos)
    inventory = report_service.source_inventory(workspace["workspaceId"])
    eligible_artifact = next(
        item for item in inventory["sources"]
        if item["sourceKind"] == "ARTIFACT" and item["state"] in {"ELIGIBLE", "METADATA_ONLY"}
    )
    eligible_claims = [
        item["sourceId"] for item in inventory["sources"]
        if item["sourceKind"] == "SCIENTIFIC_CLAIM" and item["state"] == "ELIGIBLE"
    ]
    request = ReportCompositionRequest(
        workspaceId=workspace["workspaceId"],
        expectedWorkspaceRevision=reopened.body["workspace"]["revision"],
        title="Verified DeepSeek phonon delivery",
        selectedArtifactIds=(eligible_artifact["sourceId"],),
        selectedClaimIds=tuple(eligible_claims[:1]),
        itemOrder=(eligible_artifact["sourceId"], *eligible_claims[:1]),
    )
    counts_before = (len(repos.reports.list_for_job(case["jobId"])), len(repos.recipes.list_for_job(case["jobId"])))
    preview = report_service.preview(request)
    assert preview.report.reportId.startswith("report_preview_")
    assert counts_before == (len(repos.reports.list_for_job(case["jobId"])), len(repos.recipes.list_for_job(case["jobId"])))

    finalized = report_service.finalize(request, idempotency_key="m7-retained-deepseek", created_by="user_local")
    replayed = report_service.finalize(request, idempotency_key="m7-retained-deepseek", created_by="user_local")
    assert finalized["reportId"] == replayed["reportId"]
    assert finalized["recipeId"] == replayed["recipeId"]
    assert replayed["idempotentReplay"] is True
    assert len(report_service.list_history(workspace["workspaceId"])["items"]) == 1
    recipe = report_service.get_recipe(workspace["workspaceId"], finalized["reportId"])["recipe"]
    assert recipe["analysisPlanId"] == case["planId"]
    assert recipe["analysisPlanHash"] == case["planHash"]
    assert recipe["planSchemaVersion"] == "0.2"
    assert len(recipe["dependencyBindings"]) == 2
    assert recipe["executionAuthorized"] is False
    assert recipe["planCreated"] is False
    assert recipe["jobCreated"] is False
    assert recipe["queueMessageCreated"] is False
