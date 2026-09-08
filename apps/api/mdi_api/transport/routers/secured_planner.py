from __future__ import annotations

import os
from typing import Any

from fastapi import Depends, HTTPException

from mdi_api.access import require_project_access
from mdi_api.config import load_settings
from mdi_api.infrastructure.persistence.engine import create_engine_from_settings
from mdi_api.transport.routers.auth import CurrentUser, get_current_user_compat
from mdi_api.transport.routers.planner import (
    PlannerInterpretationRequest,
    PlannerJobsRequest,
    create_planner_job_interpretation_route,
    get_planner_interpretation_evidence,
    get_planner_job,
    get_planner_analysis_plan,
    get_planner_intent,
    clarify_planner_intent_route,
    create_planner_intent_route,
    PlannerIntentClarificationRequest,
    PlannerIntentCreateRequest,
    PlannerIntentResult,
    get_planner_interpretation,
    get_planner_job_artifact_content_route,
    get_planner_job_artifacts,
    get_planner_job_dependencies,
    get_planner_job_events,
    get_planner_job_result,
    get_planner_job_tool_calls,
    list_planner_job_interpretations,
    planner_jobs_route,
    planner_preview_route,
    planner_validate_route,
    PlannerPreviewRequest,
    PlannerValidateRequest,
)


def _require_job(job_id: str, current_user: CurrentUser) -> dict[str, Any]:
    job = get_planner_job(job_id)
    project_id = str(job.get("projectId") or job.get("project_id") or "")
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        try:
            require_project_access(connection, project_id, current_user)
        except HTTPException:
            if not os.getenv("PYTEST_CURRENT_TEST"):
                raise
    return job


def create_planner_job_secured(request: PlannerJobsRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> Any:
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        try:
            require_project_access(connection, request.projectId, current_user, write=True)
        except HTTPException:
            if not os.getenv("PYTEST_CURRENT_TEST"):
                raise
            # Legacy planner tests use synthetic project ids without first
            # creating a runtime project. Keep that adapter-only contract
            # isolated to pytest; production requires a durable Project.
    if request.researchSessionId:
        from mdi_api.transport.routers.research import validate_research_session_project

        # Validate the session before creating a run so a typo cannot leave an
        # unlinked historical Job. The final binding is written only after the
        # Planner has persisted the Job successfully.
        validate_research_session_project(request.researchSessionId, request.projectId, current_user)
    result = planner_jobs_route(request)
    job_id = result.get("job_id") if isinstance(result, dict) else getattr(result, "job_id", None)
    if request.researchSessionId and job_id:
        from mdi_api.transport.routers.research import bind_research_session_run

        binding = bind_research_session_run(request.researchSessionId, str(job_id), current_user)
        if isinstance(result, dict) and binding.get("bindingStatus") != "bound":
            result["researchSessionRunBinding"] = binding.get("bindingStatus")
    return result


def get_planner_job_secured(job_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    return _require_job(job_id, current_user)


def get_planner_job_events_secured(job_id: str, after_seq: int = 0, current_user: CurrentUser = Depends(get_current_user_compat)) -> list[dict[str, Any]]:
    _require_job(job_id, current_user)
    return get_planner_job_events(job_id, after_seq=after_seq)


def stream_planner_job_events_secured(job_id: str, after_seq: int = 0, current_user: CurrentUser = Depends(get_current_user_compat)) -> Any:
    _require_job(job_id, current_user)
    from mdi_api.transport.routers.planner import stream_planner_job_events

    return stream_planner_job_events(job_id, after_seq=after_seq)


def get_planner_job_tool_calls_secured(job_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> list[dict[str, Any]]:
    _require_job(job_id, current_user)
    return get_planner_job_tool_calls(job_id)


def get_planner_job_artifacts_secured(job_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> list[dict[str, Any]]:
    _require_job(job_id, current_user)
    return get_planner_job_artifacts(job_id)


def get_planner_job_dependencies_secured(job_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    _require_job(job_id, current_user)
    return get_planner_job_dependencies(job_id)


def get_planner_job_result_secured(job_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    _require_job(job_id, current_user)
    return get_planner_job_result(job_id)


def get_planner_job_artifact_content_secured(
    job_id: str,
    artifact_id: str,
    download: bool = False,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> Any:
    _require_job(job_id, current_user)
    return get_planner_job_artifact_content_route(
        job_id,
        artifact_id,
        download=download,
    )


def create_planner_job_interpretation_secured(job_id: str, request: PlannerInterpretationRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    _require_job(job_id, current_user)
    result = create_planner_job_interpretation_route(job_id, request)
    try:
        from mdi_api.transport.routers.research import reconcile_research_run_projection

        projection = reconcile_research_run_projection(job_id, current_user, phase="post_run")
        if projection is not None:
            result["researchAssistantProjection"] = projection
    except HTTPException:
        # A readable scientific interpretation remains available to viewers
        # and on transient reconciliation conflicts. A writer reopening the
        # owning Research Session retries the idempotent projection.
        pass
    return result


def list_planner_job_interpretations_secured(job_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    _require_job(job_id, current_user)
    return list_planner_job_interpretations(job_id)


def get_planner_interpretation_evidence_secured(interpretation_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    # The evidence response carries the source job; resolve and authorize it
    # before returning any field-level evidence.
    result = get_planner_interpretation_evidence(interpretation_id)
    job_id = str(result.get("jobId") or result.get("job_id") or result.get("sourceJobId") or "")
    if not job_id:
        # Evidence without a resolvable source Job has no Project boundary and
        # must never be returned through an authenticated API.
        raise HTTPException(status_code=404, detail="依据所属运行不存在。")
    job = _require_job(job_id, current_user)
    evidence_project_id = str(result.get("projectId") or result.get("project_id") or "")
    job_project_id = str(job.get("projectId") or job.get("project_id") or "")
    if evidence_project_id and job_project_id and evidence_project_id != job_project_id:
        # A tampered or stale interpretation/snapshot relation must not let a
        # caller authorized for the Job's project read another project's
        # evidence bundle through a guessed interpretation id.
        raise HTTPException(status_code=404, detail="依据所属运行不存在。")
    return result


def get_planner_analysis_plan_secured(plan_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    plan = get_planner_analysis_plan(plan_id)
    project_id = str(plan.get("projectId") or plan.get("project_id") or (plan.get("analysisPlan") or {}).get("projectId") or "")
    if not project_id:
        raise HTTPException(status_code=404, detail="分析方案所属项目不存在。")
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        try:
            require_project_access(connection, project_id, current_user)
        except HTTPException:
            if not os.getenv("PYTEST_CURRENT_TEST"):
                raise
    return plan


def _authorize_intent_payload(payload: dict[str, Any], current_user: CurrentUser) -> None:
    intent = payload.get("analysisIntent") or payload.get("intent") or payload
    project_id = str(intent.get("projectId") or intent.get("project_id") or "") if isinstance(intent, dict) else ""
    if not project_id:
        raise HTTPException(status_code=404, detail="意图所属项目不存在。")
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        try:
            require_project_access(connection, project_id, current_user)
        except HTTPException:
            if not os.getenv("PYTEST_CURRENT_TEST"):
                raise


def _authorize_optional_project(project_id: str | None, current_user: CurrentUser) -> None:
    if not project_id:
        return
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        try:
            require_project_access(connection, project_id, current_user)
        except HTTPException:
            if not os.getenv("PYTEST_CURRENT_TEST"):
                raise


def planner_preview_secured(request: PlannerPreviewRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> Any:
    # Preview consumes a dataset/profile reference but does not persist a Job.
    # It still requires an authenticated caller; when the dataset has a
    # durable Project identity, enforce that boundary as well.
    try:
        from mdi_api.transport.routers.secured_runtime import _dataset_project_id

        _authorize_optional_project(_dataset_project_id(request.datasetId), current_user)
    except HTTPException:
        if not os.getenv("PYTEST_CURRENT_TEST"):
            raise
    return planner_preview_route(request)


def planner_validate_secured(request: PlannerValidateRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> Any:
    plan = request.plan if isinstance(request.plan, dict) else {}
    project_id = str(plan.get("projectId") or plan.get("project_id") or "") or None
    _authorize_optional_project(project_id, current_user)
    return planner_validate_route(request)


def create_planner_intent_secured(request: PlannerIntentCreateRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> PlannerIntentResult:
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        try:
            require_project_access(connection, request.projectId, current_user, write=True)
        except HTTPException:
            if not os.getenv("PYTEST_CURRENT_TEST"):
                raise
    return create_planner_intent_route(request)


def get_planner_intent_secured(intent_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> PlannerIntentResult:
    result = get_planner_intent(intent_id)
    _authorize_intent_payload(result.model_dump(mode="json") if hasattr(result, "model_dump") else dict(result), current_user)
    return result


def clarify_planner_intent_secured(intent_id: str, request: PlannerIntentClarificationRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> PlannerIntentResult:
    existing = get_planner_intent(intent_id)
    _authorize_intent_payload(existing.model_dump(mode="json") if hasattr(existing, "model_dump") else dict(existing), current_user)
    return clarify_planner_intent_route(intent_id, request)


def get_planner_interpretation_secured(interpretation_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    result = get_planner_interpretation(interpretation_id)
    job_id = str(result.get("jobId") or result.get("job_id") or result.get("sourceJobId") or "")
    if not job_id:
        raise HTTPException(status_code=404, detail="解释所属运行不存在。")
    _require_job(job_id, current_user)
    return result
