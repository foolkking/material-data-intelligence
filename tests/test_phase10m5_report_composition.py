from __future__ import annotations

import hashlib
import json

import pytest
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select

from mdi_api.main import create_app
from mdi_api.report_composition import ReportCompositionDomainError, ReportCompositionService
from mdi_api.db import organizations, reports as reports_table, users, visualization_recipes
from mdi_api.repositories import InMemoryRepositoryBundle, SqlAlchemyRecipeRepository, SqlAlchemyRepositoryBundle, compute_plan_hash
from mdi_api.routers import planner
from mdi_api.workspaces import WorkspaceProjectionService
from mdi_schemas import ReportCompositionRequest


def _plan_01() -> dict:
    return {
        "schemaVersion": "0.1",
        "goal": "Summarize exact dataset statistics.",
        "datasetId": "dataset_m5",
        "profileId": "profile_m5",
        "toolRegistryVersion": "1.0",
        "assumptions": [],
        "warnings": [],
        "steps": [{
            "stepId": "step_summary",
            "toolId": "table.numeric_summary",
            "purpose": "Compute persisted statistics.",
            "reason": "Requested exact dataset statistics.",
            "inputRefs": [{
                "refType": "normalized_object",
                "ref": "table_m5",
                "datasetId": "dataset_m5",
                "objectId": "table_m5",
                "objectType": "DataFrame",
            }],
            "params": {"columns": ["formation_energy"]},
            "output": {"artifactTypes": ["table_json"]},
        }],
        "expectedArtifacts": [{"name": "summary", "type": "table_json", "fromStepId": "step_summary"}],
    }


def _seed(*, status: str = "completed", repos: InMemoryRepositoryBundle | None = None) -> tuple[InMemoryRepositoryBundle, str, str]:
    repos = repos or InMemoryRepositoryBundle.create()
    plan = _plan_01()
    plan_hash = compute_plan_hash(plan)
    repos.projects.save({"projectId": "project_m5", "name": "M5", "createdBy": "user_local"})
    repos.datasets.save({"datasetId": "dataset_m5", "projectId": "project_m5", "name": "Dataset", "createdBy": "user_local"})
    repos.analysis_plans.save_plan({
        "id": "plan_m5", "projectId": "project_m5", "datasetId": "dataset_m5",
        "profileId": "profile_m5", "analysisPlan": plan, "planHash": plan_hash,
        "validationStatus": "validated", "createdBy": "user_local",
    })
    repos.jobs.save({
        "id": "job_m5", "projectId": "project_m5", "datasetId": "dataset_m5",
        "planId": "plan_m5", "status": status, "createdBy": "user_local",
    })
    repos.tool_calls.save({
        "id": "call_m5", "jobId": "job_m5", "stepId": "step_summary",
        "toolId": "table.numeric_summary", "status": "completed", "params": {"columns": ["formation_energy"]},
    })
    repos.artifacts.save({
        "id": "artifact_m5", "projectId": "project_m5", "datasetId": "dataset_m5",
        "jobId": "job_m5", "toolCallId": "call_m5", "type": "table_json", "version": "1",
        "name": "malicious filename ignored.html", "storageKey": "opaque_m5_key", "storageProvider": "local",
        "sizeBytes": 123, "contentType": "application/json", "contentHash": "a" * 64, "sha256": "a" * 64,
        "metadata": {"toolId": "table.numeric_summary", "toolVersion": "1.0", "adapterVersion": "1.0", "rawPayload": "not report authority"},
    })
    snapshot, created = WorkspaceProjectionService(repos).project_job(source_job_id="job_m5", created_by="user_local", title="Workspace")
    assert created
    return repos, snapshot.body["workspace"]["workspaceId"], plan_hash


def _request(workspace_id: str, revision: int, *, title: str = "Exact scientific report") -> ReportCompositionRequest:
    return ReportCompositionRequest(
        workspaceId=workspace_id,
        expectedWorkspaceRevision=revision,
        title=title,
        selectedArtifactIds=("artifact_m5",),
        itemOrder=("artifact_m5",),
    )


def test_source_inventory_is_metadata_only_and_uses_all_42_contract_roles() -> None:
    repos, workspace_id, _ = _seed()
    inventory = ReportCompositionService(repos).source_inventory(workspace_id)

    assert inventory["artifactContractInventoryCount"] == 42
    assert inventory["metadataOnly"] is True
    assert inventory["heavyArtifactPayloadRequests"] == 0
    assert inventory["webglContexts"] == 0
    artifact = next(item for item in inventory["sources"] if item["sourceId"] == "artifact_m5")
    assert artifact["role"] == "REPORT_TABLE_SOURCE"
    serialized = json.dumps(inventory, sort_keys=True)
    assert "opaque_m5_key" not in serialized
    assert "rawPayload" not in serialized
    assert "malicious filename" not in serialized


def test_preview_is_deterministic_and_has_no_writes_or_execution() -> None:
    repos, workspace_id, _ = _seed()
    workspace = repos.workspaces.get(workspace_id)
    request = _request(workspace_id, workspace["revision"])
    service = ReportCompositionService(repos)
    before = (len(repos.reports.records), len(repos.recipes.records), len(repos.jobs.records), len(repos.tool_calls.records), len(repos.artifacts.records))

    first = service.preview(request).as_dict()
    second = service.preview(request).as_dict()

    assert first == second
    assert first["report"]["outcome"] == "REPORT_PREVIEW_READY"
    assert first["predictedOutcome"] == "REPORT_READY_WITH_LIMITS"
    assert first["recipe"]["planSchemaVersion"] == "0.1"
    assert first["recipe"]["dependencyModel"] == "NONE_OR_SEQUENTIAL_INDEPENDENT"
    assert first["recipe"]["dependencyBindings"] == []
    assert first["noExecution"] == {"planCreated": False, "jobCreated": False, "toolCallCreated": False, "queueMessageCreated": False}
    assert before == (len(repos.reports.records), len(repos.recipes.records), len(repos.jobs.records), len(repos.tool_calls.records), len(repos.artifacts.records))


def test_finalize_creates_exact_immutable_pair_and_is_idempotent() -> None:
    repos, workspace_id, plan_hash = _seed()
    workspace = repos.workspaces.get(workspace_id)
    request = _request(workspace_id, workspace["revision"])
    service = ReportCompositionService(repos)

    first = service.finalize(request, idempotency_key="m5-finalize", created_by="user_local")
    second = service.finalize(request, idempotency_key="m5-finalize", created_by="user_local")

    assert first["reportId"] == second["reportId"]
    assert first["recipeId"] == second["recipeId"]
    assert first["idempotentReplay"] is False and second["idempotentReplay"] is True
    assert len(repos.reports.records) == len(repos.recipes.records) == 1
    report = repos.reports.get(first["reportId"])
    recipe = repos.recipes.get(first["recipeId"])
    assert report["recipeId"] == recipe["recipeId"]
    assert recipe["reportId"] == report["reportId"]
    assert report["compositionHash"] == recipe["compositionHash"]
    assert report["reportHash"] == recipe["reportHash"]
    assert recipe["manifest"]["analysisPlanHash"] == plan_hash
    assert recipe["manifest"]["executionAuthorized"] is False
    assert recipe["manifest"]["planCreated"] is False
    assert recipe["manifest"]["jobCreated"] is False
    assert recipe["manifest"]["queueMessageCreated"] is False
    assert recipe["manifest"]["automaticReplay"] is False

    conflicting = _request(workspace_id, workspace["revision"], title="Different report")
    with pytest.raises(ReportCompositionDomainError) as captured:
        service.finalize(conflicting, idempotency_key="m5-finalize", created_by="user_local")
    assert captured.value.code == "REPORT_IDEMPOTENCY_CONFLICT"
    assert len(repos.reports.records) == len(repos.recipes.records) == 1


def test_atomic_in_memory_pair_rolls_back_when_recipe_write_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    repos, workspace_id, _ = _seed()
    workspace = repos.workspaces.get(workspace_id)
    service = ReportCompositionService(repos)

    def fail(_record):
        raise RuntimeError("injected safe failure")

    monkeypatch.setattr(repos.recipes, "create_immutable", fail)
    with pytest.raises(RuntimeError, match="injected safe failure"):
        service.finalize(_request(workspace_id, workspace["revision"]), idempotency_key="m5-rollback", created_by="user_local")
    assert repos.reports.records == {}
    assert repos.recipes.records == {}


def test_history_recipe_and_exports_are_exact_and_deterministic() -> None:
    repos, workspace_id, _ = _seed()
    workspace = repos.workspaces.get(workspace_id)
    service = ReportCompositionService(repos)
    finalized = service.finalize(_request(workspace_id, workspace["revision"]), idempotency_key="m5-export", created_by="user_local")

    history = service.list_history(workspace_id)
    assert history["count"] == 1 and history["items"][0]["legacyReadOnly"] is False
    recipe = service.get_recipe(workspace_id, finalized["reportId"])["recipe"]
    assert recipe["sourceReportId"] == finalized["reportId"]
    first_json = service.export(workspace_id, finalized["reportId"], "json")
    second_json = service.export(workspace_id, finalized["reportId"], "json")
    markdown = service.export(workspace_id, finalized["reportId"], "markdown")
    assert first_json == second_json
    assert first_json["content"].endswith("\n")
    parsed = json.loads(first_json["content"])
    assert parsed["report"]["reportId"] == finalized["reportId"]
    assert parsed["recipe"]["executionAuthorized"] is False
    assert parsed["exportManifest"]["contentChecksum"] == hashlib.sha256(
        (json.dumps({"recipe": parsed["recipe"], "report": parsed["report"]}, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    ).hexdigest()
    assert "<script" not in markdown["content"].lower()
    assert "Recipe execution authorization: `false`" in markdown["content"]


def test_revision_integrity_and_inert_text_fail_without_writes() -> None:
    repos, workspace_id, _ = _seed()
    workspace = repos.workspaces.get(workspace_id)
    service = ReportCompositionService(repos)
    stale = _request(workspace_id, workspace["revision"] + 1)
    with pytest.raises(ReportCompositionDomainError) as captured:
        service.finalize(stale, idempotency_key="m5-stale", created_by="user_local")
    assert captured.value.code == "WORKSPACE_REVISION_CONFLICT"
    with pytest.raises(Exception):
        _request(workspace_id, workspace["revision"], title="<script>alert(1)</script>")
    assert repos.reports.records == {} and repos.recipes.records == {}


def test_unknown_artifact_contract_is_inert_and_cannot_be_selected() -> None:
    repos, workspace_id, _ = _seed()
    repos.artifacts.records["artifact_m5"]["type"] = "unknown_contract"
    inventory = ReportCompositionService(repos).source_inventory(workspace_id)
    source = next(item for item in inventory["sources"] if item["sourceId"] == "artifact_m5")
    assert source["role"] == "REPORT_UNSUPPORTED"
    with pytest.raises(ReportCompositionDomainError) as captured:
        ReportCompositionService(repos).preview(_request(workspace_id, repos.workspaces.get(workspace_id)["revision"]))
    assert captured.value.code == "REPORT_SELECTION_UNSUPPORTED"


def test_metadata_only_viewer_fallback_is_composable_without_payload_or_canvas() -> None:
    repos, workspace_id, _ = _seed()
    repos.artifacts.records["artifact_m5"]["type"] = "structure_json"
    service = ReportCompositionService(repos)
    inventory = service.source_inventory(workspace_id)
    source = next(item for item in inventory["sources"] if item["sourceId"] == "artifact_m5")
    assert source["role"] == "REPORT_METADATA_ONLY"
    assert source["state"] == "METADATA_ONLY"
    assert source["representation"] == "METADATA"
    assert "WebGL canvas is not authority" in source["fallback"]
    preview = service.preview(_request(workspace_id, repos.workspaces.get(workspace_id)["revision"]))
    selected = preview.report.selectedSources[0]
    assert selected.artifactId == "artifact_m5"
    assert selected.artifactChecksum == "a" * 64
    assert preview.as_dict()["noExecution"]["jobCreated"] is False


def test_all_failed_partial_and_no_interpretation_outcomes_remain_explicit() -> None:
    failed_repos, failed_workspace, _ = _seed(status="failed")
    failed_revision = failed_repos.workspaces.get(failed_workspace)["revision"]
    failed_request = ReportCompositionRequest(
        workspaceId=failed_workspace,
        expectedWorkspaceRevision=failed_revision,
        title="Failed execution record",
    )
    failed_preview = ReportCompositionService(failed_repos).preview(failed_request)
    assert failed_preview.predicted_outcome.value == "REPORT_NO_SCIENTIFIC_RESULTS"
    assert failed_preview.report.sections[6].status == "UNAVAILABLE"
    assert "GROUNDED_FINDINGS_UNAVAILABLE" in failed_preview.report.sections[6].items

    partial_repos, partial_workspace, _ = _seed(status="partial_success")
    partial_revision = partial_repos.workspaces.get(partial_workspace)["revision"]
    partial_preview = ReportCompositionService(partial_repos).preview(
        _request(partial_workspace, partial_revision)
    )
    assert partial_preview.predicted_outcome.value == "REPORT_READY_WITH_LIMITS"
    disclosures = [item.fallback for item in partial_preview.report.mandatoryDisclosures]
    assert any("partial_success" in (item or "") for item in disclosures)
    assert any("No validated grounded interpretation" in (item or "") for item in disclosures)
    assert partial_preview.recipe.executionOutcome == "partial_success"


@pytest.mark.parametrize(
    ("mutation", "reason", "expected_code"),
    [
        (lambda artifact: artifact.update({"version": "2"}), "ARTIFACT_CONTRACT_VERSION_UNSUPPORTED", "REPORT_SELECTION_UNSUPPORTED"),
        (lambda artifact: artifact.update({"sha256": "invalid", "contentHash": "invalid"}), None, "REPORT_SOURCE_INTEGRITY_FAILED"),
        (lambda artifact: artifact.update({"projectId": "project_foreign"}), "ARTIFACT_SCOPE_MISMATCH", "REPORT_SOURCE_INTEGRITY_FAILED"),
        (lambda artifact: artifact.update({"jobId": "job_foreign"}), None, "REPORT_SOURCE_NOT_FOUND"),
    ],
)
def test_artifact_version_checksum_and_scope_fail_closed(mutation, reason: str | None, expected_code: str) -> None:
    repos, workspace_id, _ = _seed()
    mutation(repos.artifacts.records["artifact_m5"])
    service = ReportCompositionService(repos)
    inventory = service.source_inventory(workspace_id)
    source = next((item for item in inventory["sources"] if item["sourceId"] == "artifact_m5"), None)
    if expected_code == "REPORT_SOURCE_NOT_FOUND":
        assert source is None
    else:
        assert source is not None
        assert source["state"] in {"UNSUPPORTED", "SOURCE_INTEGRITY_FAILED"}
        if reason is not None:
            assert source["reason"] == reason
    with pytest.raises(ReportCompositionDomainError) as captured:
        service.preview(_request(workspace_id, repos.workspaces.get(workspace_id)["revision"]))
    assert captured.value.code == expected_code
    assert repos.reports.records == {} and repos.recipes.records == {}


def test_stale_workspace_sources_are_disclosed_without_latest_rebinding() -> None:
    from tests.test_phase10m1_workspace_projection_api import _seed_modern

    repos = InMemoryRepositoryBundle.create()
    _seed_modern(repos, job_id="job_m5_stale")
    plan = repos.analysis_plans.get_plan_for_job("job_m5_stale")["analysisPlan"]
    repos.artifacts.save({
        "id": "artifact_m5_stale", "projectId": "project_1", "datasetId": plan["datasetId"],
        "jobId": "job_m5_stale", "toolCallId": "call_stale", "type": "phonon_band_json", "version": "1",
        "name": "band", "storageKey": "opaque", "storageProvider": "local", "sizeBytes": 1,
        "contentType": "application/json", "contentHash": "d" * 64, "sha256": "d" * 64, "metadata": {},
    })
    snapshot, _ = WorkspaceProjectionService(repos).project_job(source_job_id="job_m5_stale", created_by="user_local")
    workspace_id = snapshot.body["workspace"]["workspaceId"]
    profile_id = snapshot.body["workspace"]["profileId"]
    repos.data_profiles.records[profile_id]["datasetId"] = "dataset_foreign"
    inventory = ReportCompositionService(repos).source_inventory(workspace_id)
    source = next(item for item in inventory["sources"] if item["sourceId"] == "artifact_m5_stale")
    assert source["state"] == "STALE"
    assert source["artifactId"] == "artifact_m5_stale"
    assert any(item["state"] == "STALE" for item in inventory["mandatoryDisclosures"])
    with pytest.raises(ReportCompositionDomainError) as captured:
        ReportCompositionService(repos).preview(ReportCompositionRequest(
            workspaceId=workspace_id,
            expectedWorkspaceRevision=snapshot.body["workspace"]["revision"],
            title="Stale report",
            selectedArtifactIds=("artifact_m5_stale",),
            itemOrder=("artifact_m5_stale",),
        ))
    assert captured.value.code == "REPORT_SOURCE_STALE"


def test_legacy_report_is_read_only_and_has_no_inferred_recipe_pair() -> None:
    repos, workspace_id, _ = _seed()
    repos.reports.save({
        "reportId": "report_legacy", "projectId": "project_m5", "jobId": "job_m5",
        "title": "Historical report", "version": "legacy", "createdAt": "2026-01-01T00:00:00Z",
    })
    service = ReportCompositionService(repos)
    history = service.list_history(workspace_id)
    assert history["items"][0]["legacyReadOnly"] is True
    detail = service.get_report(workspace_id, "report_legacy")
    assert detail["legacyReadOnly"] is True
    assert detail["report"]["state"] == "LEGACY_READ_ONLY"
    with pytest.raises(ReportCompositionDomainError) as captured:
        service.get_recipe(workspace_id, "report_legacy")
    assert captured.value.code == "LEGACY_REPORT_READ_ONLY"
    with pytest.raises(ReportCompositionDomainError) as unsupported:
        service.export(workspace_id, "report_legacy", "pdf")
    assert unsupported.value.code == "EXPORT_FORMAT_UNSUPPORTED"


def test_plan_02_recipe_preserves_exact_graph_and_dependency_bindings() -> None:
    from tests.test_phase10m1_workspace_projection_api import _seed_modern

    repos = InMemoryRepositoryBundle.create()
    _seed_modern(repos, job_id="job_m5_plan02")
    plan_record = repos.analysis_plans.get_plan_for_job("job_m5_plan02")
    plan = plan_record["analysisPlan"]
    first_step = plan["steps"][0]
    repos.tool_calls.save({
        "id": "call_m5_plan02", "jobId": "job_m5_plan02", "stepId": first_step["stepId"],
        "toolId": first_step["toolId"], "status": "completed", "params": first_step["params"],
    })
    repos.artifacts.save({
        "id": "artifact_m5_plan02", "projectId": "project_1", "datasetId": plan["datasetId"],
        "jobId": "job_m5_plan02", "toolCallId": "call_m5_plan02", "type": "phonon_band_json", "version": "1",
        "name": "band", "storageKey": "opaque_plan02", "storageProvider": "local", "sizeBytes": 100,
        "contentType": "application/json", "contentHash": "d" * 64, "sha256": "d" * 64,
        "metadata": {"toolVersion": "1.0", "adapterVersion": "1.0"},
    })
    snapshot, _ = WorkspaceProjectionService(repos).project_job(source_job_id="job_m5_plan02", created_by="user_local")
    workspace = snapshot.body["workspace"]
    request = ReportCompositionRequest(
        workspaceId=workspace["workspaceId"], expectedWorkspaceRevision=workspace["revision"],
        title="Plan 0.2 report", selectedArtifactIds=("artifact_m5_plan02",), itemOrder=("artifact_m5_plan02",),
    )
    recipe = ReportCompositionService(repos).preview(request).recipe
    assert recipe.planSchemaVersion == "0.2"
    assert recipe.graphHash == plan["graphHash"]
    assert list(recipe.dependencyBindings) == plan["dependencyBindings"]
    assert [step.stepId for step in recipe.steps] == [step["stepId"] for step in plan["steps"]]
    assert recipe.dependencyModel == "TYPED_ARTIFACT_BINDINGS"


def test_grounded_claim_and_evidence_membership_is_exact_and_cross_job_injection_fails(tmp_path) -> None:
    from mdi_api.routers.planner import PlannerInterpretationRequest, create_planner_job_interpretation
    from tests.test_phase10l4_api_persistence import _seed_api_source

    repos, runtime, plan_hash = _seed_api_source(tmp_path)
    repos.projects.save({"id": "project_l4_api", "name": "Grounded M5", "createdBy": "user_local"})
    repos.datasets.save({
        "id": "dataset_l4_api",
        "projectId": "project_l4_api",
        "name": "Grounded dataset",
        "version": "legacy-plan:plan_l4_api",
        "createdBy": "user_local",
    })
    interpreted = create_planner_job_interpretation(
        "job_l4_api",
        PlannerInterpretationRequest(mode="DETERMINISTIC", expectedPlanHash=plan_hash),
        repositories=repos,
        queue_runtime=runtime,
    )
    snapshot, _ = WorkspaceProjectionService(repos).project_job(
        source_job_id="job_l4_api",
        created_by="user_local",
        title="Grounded report Workspace",
    )
    workspace = snapshot.body["workspace"]
    service = ReportCompositionService(repos)
    inventory = service.source_inventory(workspace["workspaceId"])
    claim = next(item for item in inventory["sources"] if item["sourceKind"] == "SCIENTIFIC_CLAIM")
    evidence = next(item for item in inventory["sources"] if item["sourceKind"] == "EVIDENCE_ITEM")
    assert claim["interpretationId"] == interpreted["interpretationId"]
    assert evidence["interpretationId"] == interpreted["interpretationId"]

    request = ReportCompositionRequest(
        workspaceId=workspace["workspaceId"],
        expectedWorkspaceRevision=workspace["revision"],
        title="Grounded exact report",
        selectedArtifactIds=("artifact_l4_api",),
        selectedClaimIds=(claim["sourceId"],),
        selectedEvidenceItemIds=(evidence["sourceId"],),
        itemOrder=("artifact_l4_api", claim["sourceId"], evidence["sourceId"]),
    )
    preview = service.preview(request)
    finding_section = next(section for section in preview.report.sections if section.sectionId == "GROUNDED_FINDINGS")
    selected_claim = next(item for item in interpreted["claims"] if item["claimId"] == claim["sourceId"])
    assert selected_claim["renderedText"] in finding_section.items
    assert {item.sourceId for item in preview.report.selectedSources}.issuperset({claim["sourceId"], evidence["sourceId"]})

    injected = request.model_copy(update={
        "selectedClaimIds": ("claim_foreign_job",),
        "itemOrder": ("artifact_l4_api", "claim_foreign_job", evidence["sourceId"]),
    })
    with pytest.raises(ReportCompositionDomainError) as captured:
        service.preview(injected)
    assert captured.value.code == "REPORT_SOURCE_NOT_FOUND"
    assert repos.reports.records == {} and repos.recipes.records == {}


def test_workspace_scoped_api_preview_finalize_history_recipe_and_export() -> None:
    planner.reset_planner_runtime()
    repos = planner._IN_MEMORY_REPOSITORIES
    _, workspace_id, _ = _seed(repos=repos)
    revision = repos.workspaces.get(workspace_id)["revision"]
    body = _request(workspace_id, revision).model_dump(mode="json")
    client = TestClient(create_app())
    try:
        sources = client.get(f"/workspaces/{workspace_id}/report-composition/sources")
        assert sources.status_code == 200
        assert sources.json()["heavyArtifactPayloadRequests"] == 0

        duplicate = client.post(
            f"/workspaces/{workspace_id}/report-compositions/preview",
            headers={"Content-Type": "application/json"},
            content=json.dumps(body)[:-1] + ',"title":"duplicate"}',
        )
        assert duplicate.status_code == 400

        preview = client.post(f"/workspaces/{workspace_id}/report-compositions/preview", json=body)
        assert preview.status_code == 200 and preview.json()["persisted"] is False
        assert repos.reports.records == {} and repos.recipes.records == {}

        created = client.post(
            f"/workspaces/{workspace_id}/report-compositions",
            headers={"Idempotency-Key": "api-m5"},
            json=body,
        )
        assert created.status_code == 201
        report_id = created.json()["reportId"]
        replay = client.post(
            f"/workspaces/{workspace_id}/report-compositions",
            headers={"Idempotency-Key": "api-m5"},
            json=body,
        )
        assert replay.status_code == 200 and replay.headers["x-idempotent-replay"] == "true"

        history = client.get(f"/workspaces/{workspace_id}/report-compositions")
        detail = client.get(f"/workspaces/{workspace_id}/report-compositions/{report_id}")
        recipe = client.get(f"/workspaces/{workspace_id}/report-compositions/{report_id}/recipe")
        export_json = client.get(f"/workspaces/{workspace_id}/report-compositions/{report_id}/exports/json")
        export_md = client.get(f"/workspaces/{workspace_id}/report-compositions/{report_id}/exports/markdown")
        assert history.status_code == detail.status_code == recipe.status_code == 200
        assert export_json.status_code == export_md.status_code == 200
        assert history.json()["count"] == 1
        assert recipe.json()["recipe"]["automaticReplay"] is False
        assert export_json.headers["content-disposition"].startswith('attachment; filename="scientific-report-')
        assert export_md.headers["content-type"].startswith("text/markdown")

        stale = {**body, "expectedWorkspaceRevision": revision + 1}
        conflict = client.post(
            f"/workspaces/{workspace_id}/report-compositions",
            headers={"Idempotency-Key": "api-stale"},
            json=stale,
        )
        assert conflict.status_code == 409
        assert conflict.json()["detail"]["code"] == "WORKSPACE_REVISION_CONFLICT"
        assert "Traceback" not in conflict.text and "E:\\" not in conflict.text
    finally:
        client.close()
        planner.reset_planner_runtime()


def test_sqlalchemy_finalize_uses_one_transaction_and_existing_tables(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    database_path = tmp_path / "m5.sqlite"
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.as_posix()}")
    alembic_command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database_path.as_posix()}", future=True)
    # These identity tables are deployment prerequisites outside the Phase 4-10 migration chain.
    users.create(engine, checkfirst=True)
    organizations.create(engine, checkfirst=True)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    _, workspace_id, _ = _seed(repos=repos)  # type: ignore[arg-type]
    workspace = repos.workspaces.get(workspace_id)
    service = ReportCompositionService(repos)

    created = service.finalize(
        _request(workspace_id, workspace["revision"]),
        idempotency_key="sql-m5",
        created_by="user_local",
    )
    replay = service.finalize(
        _request(workspace_id, workspace["revision"]),
        idempotency_key="sql-m5",
        created_by="user_local",
    )
    assert created["reportId"] == replay["reportId"]
    assert replay["idempotentReplay"] is True
    with engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(reports_table)) == 1
        assert connection.scalar(select(func.count()).select_from(visualization_recipes)) == 1

    def fail_recipe(_self, _record):
        raise RuntimeError("injected SQL pair failure")

    monkeypatch.setattr(SqlAlchemyRecipeRepository, "create_immutable", fail_recipe)
    with pytest.raises(RuntimeError, match="injected SQL pair failure"):
        service.finalize(
            _request(workspace_id, workspace["revision"], title="Second snapshot"),
            idempotency_key="sql-m5-rollback",
            created_by="user_local",
        )
    with engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(reports_table)) == 1
        assert connection.scalar(select(func.count()).select_from(visualization_recipes)) == 1
    engine.dispose()
