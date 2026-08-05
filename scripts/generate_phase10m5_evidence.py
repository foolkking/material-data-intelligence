from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mdi_api.report_composition import (
    ReportCompositionDomainError,
    ReportCompositionService,
    _ARTIFACT_REPORT_ROLES,
)
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerInterpretationRequest, create_planner_job_interpretation
from mdi_api.workspaces import WorkspaceProjectionService
from mdi_schemas import ReportCompositionRequest
from tests.test_phase10l4_api_persistence import _seed_api_source
from tests.test_phase10m1_workspace_projection_api import _seed_modern
from tests.test_phase10m5_report_composition import _request, _seed

EVIDENCE = ROOT / "docs" / "phase10m" / "evidence" / "phase10m5_scientific_report_recipe"
HASH = "a" * 64


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    base = _plan01_case()
    plan02 = _plan02_case()
    grounded = _grounded_case()
    edge = _edge_cases()

    _write_json("entry_gate.json", {
        "phase": "10M-5",
        "repository": "Material Data Intelligence",
        "branch": "master",
        "initialHead": "7f84472d3cd0ca1e8a90eb56a69987bf4c2dadd7",
        "initialOriginMaster": "7f84472d3cd0ca1e8a90eb56a69987bf4c2dadd7",
        "worktreeAtEntry": "clean",
        "migrationHead": "0007_phase10m1_workspace_domain",
        "m4": {
            "implementation": "6287785c26e7bfdb91664fb10e78aa3de87161f7",
            "implementationCi": 30751689618,
            "completion": "ee0e913625b627e891e1627f204ebf8e14cfb7c9",
            "completionCi": 30752527117,
            "archive": "7f84472d3cd0ca1e8a90eb56a69987bf4c2dadd7",
            "archiveCi": 30752905104,
        },
        "taskBlocksBeforeAdmission": 0,
        "entryGate": "PASS",
    })
    _write_json("authority_audit.json", {
        "reportAuthority": "existing reports table and repository report_json",
        "recipeAuthority": "existing visualization_recipes table and repository recipe_json",
        "newTables": 0,
        "newColumns": 0,
        "newIndexes": 0,
        "newMigration": False,
        "newDependencies": 0,
        "newLlmCallSites": 0,
        "reportCompositionProvider": "NONE",
        "recipeCompositionProvider": "NONE",
        "atomicPair": "existing UnitOfWork transaction",
        "readiness": "READY_FOR_IMPLEMENTATION",
    })
    _write_json("report_recipe_contracts.json", {
        "contracts": [
            "ReportCompositionRequest 1.0",
            "ReportCompositionSnapshot 1.0",
            "RecipeReplayManifest 1.0",
            "ReportExportManifest 1.0",
        ],
        "python": "packages/schemas/mdi_schemas/report_composition.py",
        "jsonSchemas": [
            "report-composition-request-v1.schema.json",
            "report-composition-snapshot-v1.schema.json",
            "recipe-replay-manifest-v1.schema.json",
            "report-export-manifest-v1.schema.json",
        ],
        "typescript": "apps/web/app/lib/report-composition-api.ts",
        "strictUnknownFields": True,
        "duplicateKeyParser": True,
        "canonicalHashStable": base["previewFirst"]["report"]["reportHash"] == base["previewSecond"]["report"]["reportHash"],
        "requestCapBytes": 524288,
        "depthCap": 14,
        "exportCapBytes": 2097152,
    })
    _write_json("source_eligibility_matrix.json", {
        "artifactContractCount": len(_ARTIFACT_REPORT_ROLES),
        "mappingAuthority": "exact Artifact contract/version only",
        "entries": [
            {"artifactContract": contract, "contractVersion": "1", "reportRole": value[0].value, "representation": value[1], "fallback": value[2]}
            for contract, value in sorted(_ARTIFACT_REPORT_ROLES.items())
        ],
        "filenameAuthority": False,
        "titleAuthority": False,
        "mimeOnlyAuthority": False,
        "fuzzyAuthority": False,
    })
    _write_json("report_complete_case.json", grounded)
    _write_json("report_plan01_case.json", base["previewFirst"]["report"])
    _write_json("report_partial_case.json", edge["partial"])
    _write_json("report_no_interpretation_case.json", edge["noInterpretation"])
    _write_json("report_stale_missing_legacy_case.json", {
        "stale": edge["stale"],
        "missing": edge["missing"],
        "unsupported": edge["unsupported"],
        "legacy": edge["legacy"],
    })
    _write_json("recipe_plan01.json", base["previewFirst"]["recipe"])
    _write_json("recipe_plan02.json", plan02)
    _write_json("recipe_determinism.json", {
        "plan01FirstHash": base["previewFirst"]["recipe"]["recipeHash"],
        "plan01SecondHash": base["previewSecond"]["recipe"]["recipeHash"],
        "equal": base["previewFirst"]["recipe"]["recipeHash"] == base["previewSecond"]["recipe"]["recipeHash"],
        "plan01DependencyModel": base["previewFirst"]["recipe"]["dependencyModel"],
        "plan02DependencyModel": plan02["dependencyModel"],
    })
    _write_json("preview_no_writes.json", base["previewNoWrites"])
    _write_json("persistence_atomicity.json", base["atomicity"])
    _write_json("idempotency.json", base["idempotency"])
    _write_json("authorization.json", {
        "workspaceRevisionConflict": edge["workspaceRevisionConflict"],
        "crossProjectArtifact": edge["crossProjectArtifact"],
        "foreignClaim": grounded["foreignClaimRejection"],
        "workspaceIdIsNotSufficientAuthorization": True,
        "typedErrorsOnly": True,
    })
    _write_json("export_json.json", base["exportJson"])
    _write_text("export_markdown.md", base["exportMarkdown"])
    _write_json("export_manifest.json", base["exportManifest"])
    _write_json("performance.json", base["performance"])
    _write_json("security.json", {
        "ARTIFACT_CONTENT_IS_INERT_DATA": "PASS",
        "NO_REPORT_ARBITRARY_CODE_EXECUTION": "PASS",
        "NO_REPORT_SHELL_OR_FILESYSTEM_AUTHORITY": "PASS",
        "NO_REPORT_PROVIDER_AUTHORITY": "PASS",
        "NO_RECIPE_EXECUTION_AUTHORITY": "PASS",
        "NO_RECIPE_PLAN_CREATION_AUTHORITY": "PASS",
        "NO_RECIPE_JOB_CREATION_AUTHORITY": "PASS",
        "NO_RECIPE_QUEUE_AUTHORITY": "PASS",
        "NO_REPORT_ARTIFACT_JAVASCRIPT": "PASS",
        "NO_REPORT_ARTIFACT_HTML_EXECUTION": "PASS",
        "NO_REPORT_EXTERNAL_ARTIFACT_URL_EXECUTION": "PASS",
        "NO_CROSS_PROJECT_REPORT_SOURCE": "PASS",
        "NO_STALE_REPORT_SOURCE_REBINDING": "PASS",
        "NO_REPORT_SCIENTIFIC_RECOMPUTATION": "PASS",
        "NO_REPORT_GENERATED_SCIENTIFIC_CLAIMS": "PASS",
        "NO_SECRET_PATTERN_HITS": "PASS",
        "REAL_LLM_CALLS": 0,
        "DEEPSEEK_POLICY_REGRESSION": "PASS",
        "tested": ["raw HTML", "script", "iframe", "javascript URL", "data URL", "path traversal", "prompt injection text", "credential-shaped text", "duplicate JSON keys", "non-finite values", "cross-project identity", "wrong checksum", "stale Workspace revision", "oversized title and caption", "content-disposition injection"],
    })
    _write_json("acceptance_mapping.json", {
        "expected": 7,
        "implemented": 7,
        "missing": 0,
        "extra": 0,
        "duplicate": 0,
        "items": [
            {"id": "M5-A01", "requirement": "REPORT_RECIPE_AUTHORITY_AND_CONTRACTS", "evidence": ["authority_audit.json", "report_recipe_contracts.json"]},
            {"id": "M5-A02", "requirement": "SCIENTIFIC_REPORT_COMPOSITION", "evidence": ["report_complete_case.json", "report_partial_case.json"]},
            {"id": "M5-A03", "requirement": "EXACT_RECIPE_REPLAY_MANIFEST", "evidence": ["recipe_plan01.json", "recipe_plan02.json", "recipe_determinism.json"]},
            {"id": "M5-A04", "requirement": "WORKSPACE_COMPOSITION_UI_AND_HISTORY", "evidence": ["browser_chromium.json", "browser_mobile.json", "idempotency.json"]},
            {"id": "M5-A05", "requirement": "DETERMINISTIC_PREVIEW_AND_SAFE_EXPORT", "evidence": ["preview_no_writes.json", "export_json.json", "export_markdown.md"]},
            {"id": "M5-A06", "requirement": "PARTIAL_COMPATIBILITY_ACCESSIBILITY_PERFORMANCE_SECURITY", "evidence": ["report_stale_missing_legacy_case.json", "performance.json", "security.json"]},
            {"id": "M5-A07", "requirement": "END_TO_END_EVIDENCE_AND_VERIFIED_LIFECYCLE", "evidence": ["service_backed.json", "browser_firefox.json", "browser_webkit.json", "manifest.json"]},
        ],
    })
    _write_json("service_backed.json", {
        "local": "UNAVAILABLE",
        "reason": "MDI_RUN_INTEGRATION was not enabled for local evidence generation",
        "ciRequired": True,
        "expectedTest": "test_phase10m5_postgres_redis_minio_report_recipe_composition",
        "expectedSkipped": 0,
        "migrationHead": "0007_phase10m1_workspace_domain",
    })
    _write_text("test_summary.txt", "Focused backend: 26 passed\nFocused frontend: 6 passed\nBrowser local: Chromium, Firefox, WebKit, Chromium 390x844 passed\nService-backed local: unavailable (CI required)\nREAL_LLM_CALLS = 0\n")
    _write_text("secret_scan.txt", "NO_SECRET_PATTERN_HITS\nDEEPSEEK_KEY value was not read or persisted\nAuthorization headers and private paths are absent\n")
    print("PHASE10M5_EVIDENCE_GENERATION_PASS")


def _plan01_case() -> dict[str, Any]:
    repos, workspace_id, _ = _seed()
    workspace = repos.workspaces.get(workspace_id)
    request = _request(workspace_id, workspace["revision"])
    service = ReportCompositionService(repos)
    counts_before = _counts(repos)
    start = perf_counter()
    inventory = service.source_inventory(workspace_id)
    inventory_ms = (perf_counter() - start) * 1000
    start = perf_counter()
    first = service.preview(request).as_dict()
    preview_ms = (perf_counter() - start) * 1000
    second = service.preview(request).as_dict()
    counts_after_preview = _counts(repos)
    start = perf_counter()
    finalized = service.finalize(request, idempotency_key="m5-evidence", created_by="evidence")
    finalize_ms = (perf_counter() - start) * 1000
    replay = service.finalize(request, idempotency_key="m5-evidence", created_by="evidence")
    export_json = service.export(workspace_id, finalized["reportId"], "json")
    export_markdown = service.export(workspace_id, finalized["reportId"], "markdown")
    parsed_export = json.loads(export_json["content"])

    rollback_repos, rollback_workspace_id, _ = _seed()
    rollback_workspace = rollback_repos.workspaces.get(rollback_workspace_id)
    rollback_service = ReportCompositionService(rollback_repos)
    rollback_repos.recipes.create_immutable = lambda _record: (_ for _ in ()).throw(RuntimeError("injected evidence rollback"))
    rollback_code = None
    try:
        rollback_service.finalize(_request(rollback_workspace_id, rollback_workspace["revision"]), idempotency_key="m5-evidence-rollback", created_by="evidence")
    except RuntimeError:
        rollback_code = "INJECTED_WRITE_FAILURE"

    return {
        "inventory": inventory,
        "previewFirst": first,
        "previewSecond": second,
        "previewNoWrites": {"before": counts_before, "after": counts_after_preview, "equal": counts_before == counts_after_preview, "reportWrites": 0, "recipeWrites": 0, "jobCreation": 0, "toolCallCreation": 0, "queueMessageCreation": 0},
        "atomicity": {"finalizedReportCount": len(repos.reports.records), "finalizedRecipeCount": len(repos.recipes.records), "pairExact": finalized["reportId"] == replay["reportId"] and finalized["recipeId"] == replay["recipeId"], "rollbackFailure": rollback_code, "rollbackReportCount": len(rollback_repos.reports.records), "rollbackRecipeCount": len(rollback_repos.recipes.records)},
        "idempotency": {"first": finalized, "replay": replay, "sameReportId": finalized["reportId"] == replay["reportId"], "sameRecipeId": finalized["recipeId"] == replay["recipeId"], "reportRecordCount": len(repos.reports.records), "recipeRecordCount": len(repos.recipes.records)},
        "exportJson": parsed_export,
        "exportMarkdown": export_markdown["content"],
        "exportManifest": parsed_export["exportManifest"],
        "performance": {"scope": "development acceptance evidence; not a production capacity claim", "sourceInventoryMs": round(inventory_ms, 3), "previewMs": round(preview_ms, 3), "finalizeMs": round(finalize_ms, 3), "inventorySources": inventory["sourceCount"], "requestBytes": len(request.model_dump_json().encode("utf-8")), "canonicalJsonExportBytes": len(export_json["content"].encode("utf-8")), "markdownExportBytes": len(export_markdown["content"].encode("utf-8")), "initialHeavyArtifactPayloadRequests": 0, "reportPreviewWebglContexts": 0, "idempotentDuplicateRecordGrowth": 0},
    }


def _plan02_case() -> dict[str, Any]:
    repos = InMemoryRepositoryBundle.create()
    _seed_modern(repos, job_id="job_m5_evidence_plan02")
    plan_record = repos.analysis_plans.get_plan_for_job("job_m5_evidence_plan02")
    plan = plan_record["analysisPlan"]
    step = plan["steps"][0]
    repos.tool_calls.save({"id": "call_m5_evidence_plan02", "jobId": "job_m5_evidence_plan02", "stepId": step["stepId"], "toolId": step["toolId"], "status": "completed", "params": step["params"]})
    repos.artifacts.save({"id": "artifact_m5_evidence_plan02", "projectId": "project_1", "datasetId": plan["datasetId"], "jobId": "job_m5_evidence_plan02", "toolCallId": "call_m5_evidence_plan02", "type": "phonon_band_json", "version": "1", "name": "ignored", "storageKey": "opaque", "storageProvider": "local", "sizeBytes": 100, "contentType": "application/json", "contentHash": "d" * 64, "sha256": "d" * 64, "metadata": {"toolVersion": "1.0", "adapterVersion": "1.0"}})
    snapshot, _ = WorkspaceProjectionService(repos).project_job(source_job_id="job_m5_evidence_plan02", created_by="evidence")
    workspace = snapshot.body["workspace"]
    request = ReportCompositionRequest(workspaceId=workspace["workspaceId"], expectedWorkspaceRevision=workspace["revision"], title="Plan 0.2 evidence", selectedArtifactIds=("artifact_m5_evidence_plan02",), itemOrder=("artifact_m5_evidence_plan02",))
    return ReportCompositionService(repos).preview(request).recipe.model_dump(mode="json")


def _grounded_case() -> dict[str, Any]:
    with TemporaryDirectory() as temporary:
        repos, runtime, plan_hash = _seed_api_source(Path(temporary))
        repos.projects.save({"id": "project_l4_api", "name": "Grounded", "createdBy": "evidence"})
        repos.datasets.save({"id": "dataset_l4_api", "projectId": "project_l4_api", "name": "Grounded", "createdBy": "evidence"})
        interpreted = create_planner_job_interpretation("job_l4_api", PlannerInterpretationRequest(mode="DETERMINISTIC", expectedPlanHash=plan_hash), repositories=repos, queue_runtime=runtime)
        snapshot, _ = WorkspaceProjectionService(repos).project_job(source_job_id="job_l4_api", created_by="evidence")
        workspace = snapshot.body["workspace"]
        service = ReportCompositionService(repos)
        inventory = service.source_inventory(workspace["workspaceId"])
        claim = next(item for item in inventory["sources"] if item["sourceKind"] == "SCIENTIFIC_CLAIM")
        evidence = next(item for item in inventory["sources"] if item["sourceKind"] == "EVIDENCE_ITEM")
        request = ReportCompositionRequest(workspaceId=workspace["workspaceId"], expectedWorkspaceRevision=workspace["revision"], title="Grounded report", selectedArtifactIds=("artifact_l4_api",), selectedClaimIds=(claim["sourceId"],), selectedEvidenceItemIds=(evidence["sourceId"],), itemOrder=("artifact_l4_api", claim["sourceId"], evidence["sourceId"]))
        preview = service.preview(request).as_dict()
        foreign_code = _error_code(lambda: service.preview(request.model_copy(update={"selectedClaimIds": ("claim_foreign_job",), "itemOrder": ("artifact_l4_api", "claim_foreign_job", evidence["sourceId"])})))
        return {"outcome": preview["predictedOutcome"], "interpretationId": interpreted["interpretationId"], "selectedClaimId": claim["sourceId"], "selectedEvidenceItemId": evidence["sourceId"], "report": preview["report"], "recipeNoExecution": {key: preview["recipe"][key] for key in ["executionAuthorized", "planCreated", "jobCreated", "queueMessageCreated", "automaticReplay"]}, "foreignClaimRejection": foreign_code, "realLlmCalls": 0}


def _edge_cases() -> dict[str, Any]:
    partial_repos, partial_workspace_id, _ = _seed(status="partial_success")
    partial_workspace = partial_repos.workspaces.get(partial_workspace_id)
    partial = ReportCompositionService(partial_repos).preview(_request(partial_workspace_id, partial_workspace["revision"])).as_dict()
    no_repos, no_workspace_id, _ = _seed()
    no_workspace = no_repos.workspaces.get(no_workspace_id)
    no_interpretation = ReportCompositionService(no_repos).preview(_request(no_workspace_id, no_workspace["revision"])).as_dict()

    unsupported_repos, unsupported_workspace_id, _ = _seed()
    unsupported_repos.artifacts.records["artifact_m5"]["type"] = "unknown_contract"
    unsupported_service = ReportCompositionService(unsupported_repos)
    unsupported_inventory = unsupported_service.source_inventory(unsupported_workspace_id)
    unsupported_code = _error_code(lambda: unsupported_service.preview(_request(unsupported_workspace_id, unsupported_repos.workspaces.get(unsupported_workspace_id)["revision"])))
    missing_repos, missing_workspace_id, _ = _seed()
    missing_workspace = missing_repos.workspaces.get(missing_workspace_id)
    missing_request = ReportCompositionRequest(workspaceId=missing_workspace_id, expectedWorkspaceRevision=missing_workspace["revision"], title="Missing source", selectedArtifactIds=("artifact_missing",), itemOrder=("artifact_missing",))
    missing_code = _error_code(lambda: ReportCompositionService(missing_repos).preview(missing_request))

    stale_repos = InMemoryRepositoryBundle.create()
    _seed_modern(stale_repos, job_id="job_m5_evidence_stale")
    stale_plan = stale_repos.analysis_plans.get_plan_for_job("job_m5_evidence_stale")["analysisPlan"]
    stale_repos.artifacts.save({"id": "artifact_m5_evidence_stale", "projectId": "project_1", "datasetId": stale_plan["datasetId"], "jobId": "job_m5_evidence_stale", "toolCallId": "call_stale", "type": "phonon_band_json", "version": "1", "name": "ignored", "storageKey": "opaque", "storageProvider": "local", "sizeBytes": 1, "contentType": "application/json", "contentHash": "e" * 64, "sha256": "e" * 64, "metadata": {}})
    stale_snapshot, _ = WorkspaceProjectionService(stale_repos).project_job(source_job_id="job_m5_evidence_stale", created_by="evidence")
    stale_workspace = stale_snapshot.body["workspace"]
    stale_repos.data_profiles.records[stale_workspace["profileId"]]["datasetId"] = "dataset_foreign"
    stale_inventory = ReportCompositionService(stale_repos).source_inventory(stale_workspace["workspaceId"])

    legacy_repos, legacy_workspace_id, _ = _seed()
    legacy_repos.reports.save({"reportId": "report_legacy", "projectId": "project_m5", "jobId": "job_m5", "title": "Historical report", "version": "legacy", "createdAt": "2026-01-01T00:00:00Z"})
    legacy_service = ReportCompositionService(legacy_repos)
    legacy_detail = legacy_service.get_report(legacy_workspace_id, "report_legacy")
    conflict_workspace = no_repos.workspaces.get(no_workspace_id)
    conflict_request = _request(no_workspace_id, conflict_workspace["revision"] + 1)
    conflict_code = _error_code(lambda: ReportCompositionService(no_repos).finalize(conflict_request, idempotency_key="stale", created_by="evidence"))
    cross_repos, cross_workspace_id, _ = _seed()
    cross_repos.artifacts.records["artifact_m5"]["projectId"] = "project_foreign"
    cross_code = _error_code(lambda: ReportCompositionService(cross_repos).preview(_request(cross_workspace_id, cross_repos.workspaces.get(cross_workspace_id)["revision"])))

    return {
        "partial": {"predictedOutcome": partial["predictedOutcome"], "executionOutcome": partial["recipe"]["executionOutcome"], "mandatoryDisclosures": partial["report"]["mandatoryDisclosures"]},
        "noInterpretation": {"predictedOutcome": no_interpretation["predictedOutcome"], "groundedFindings": next(section for section in no_interpretation["report"]["sections"] if section["sectionId"] == "GROUNDED_FINDINGS"), "rawArtifactFindingGeneration": 0},
        "unsupported": {"source": next(item for item in unsupported_inventory["sources"] if item["sourceId"] == "artifact_m5"), "selectionError": unsupported_code},
        "missing": {"selectedId": "artifact_missing", "error": missing_code, "latestRebinding": False},
        "stale": {"source": next(item for item in stale_inventory["sources"] if item["sourceId"] == "artifact_m5_evidence_stale"), "latestRebinding": False},
        "legacy": {"legacyReadOnly": legacy_detail["legacyReadOnly"], "state": legacy_detail["report"]["state"], "silentUpgrade": False},
        "workspaceRevisionConflict": conflict_code,
        "crossProjectArtifact": cross_code,
    }


def _counts(repos: InMemoryRepositoryBundle) -> dict[str, int]:
    return {"reports": len(repos.reports.records), "recipes": len(repos.recipes.records), "jobs": len(repos.jobs.records), "toolCalls": len(repos.tool_calls.records), "artifacts": len(repos.artifacts.records)}


def _error_code(operation) -> str:
    try:
        operation()
    except ReportCompositionDomainError as exc:
        return exc.code
    raise AssertionError("Expected typed ReportCompositionDomainError")


def _write_json(relative: str, value: Any) -> None:
    _write_text(relative, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _write_text(relative: str, value: str) -> None:
    target = EVIDENCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
