from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from mdi_api.config import load_settings
from mdi_api.phase1_demo import stream_phase1_job_events, submit_analysis_request_stub
from mdi_api.phase2_runtime import (
    create_phase2_dataset_profile,
    create_phase2_demo_dataset,
    create_phase2_job,
    create_phase2_project,
    get_phase2_artifact,
    get_phase2_artifact_download,
    get_phase2_dataset,
    get_phase2_dataset_profile,
    get_phase2_job,
    get_phase2_job_artifacts,
    get_phase2_job_events,
    get_phase2_job_tool_calls,
    list_phase2_datasets,
    list_phase2_projects,
    stream_phase2_job_events,
    upload_phase2_dataset,
)
from mdi_api.routers.auth import CurrentUser, get_current_user_stub
from mdi_api.routers.datasets import DatasetSummary, create_upload_session_stub
from mdi_api.routers.health import health, runtime_health
from mdi_api.routers.planner import (
    PlannerIntentClarificationRequest,
    PlannerIntentCreateRequest,
    PlannerInterpretationRequest,
    PlannerJobsRequest,
    PlannerPreviewRequest,
    PlannerValidateRequest,
    clarify_planner_intent_route,
    create_planner_intent_route,
    create_planner_job_interpretation_route,
    get_planner_analysis_plan,
    get_planner_intent_route,
    get_planner_interpretation,
    get_planner_interpretation_evidence,
    get_planner_job,
    get_planner_job_artifacts,
    get_planner_job_dependencies,
    get_planner_job_artifact_content_route,
    get_planner_job_events,
    get_planner_job_result,
    list_planner_job_interpretations,
    get_planner_job_tool_calls,
    planner_jobs_route,
    planner_preview_route,
    planner_validate_route,
    stream_planner_job_events,
)
from mdi_api.routers.planner_providers import (
    list_planner_providers,
    planner_provider_status,
    resolve_planner_provider_route,
    test_planner_provider_route,
)
from mdi_api.routers.projects import ProjectSummary
from mdi_api.routers.report_compositions import (
    export_report_composition,
    finalize_report_composition,
    get_report_composition,
    get_report_composition_recipe,
    get_report_composition_sources,
    list_report_compositions,
    preview_report_composition,
)
from mdi_api.routers.secrets import (
    CreateSecretRequest,
    SecretSummary,
    create_secret,
    delete_secret,
    list_secrets,
)
from mdi_api.routers.tools import list_mvp_tools, list_tools
from mdi_api.routers.workspaces import (
    create_workspace,
    get_workspace,
    get_workspace_layout_revision,
    get_workspace_panel,
    list_analysis_jobs,
    list_project_workspaces,
    list_workspace_layout_revisions,
    list_workspace_panels,
    patch_workspace,
)


@dataclass(frozen=True)
class RouteSpec:
    path: str
    endpoint: Callable[..., Any]
    methods: tuple[str, ...]
    tags: tuple[str, ...]
    response_model: Any | None = None


@dataclass(frozen=True)
class AppSpec:
    title: str
    version: str
    routes: tuple[RouteSpec, ...]


ROUTES: tuple[RouteSpec, ...] = (
    RouteSpec("/health", health, ("GET",), ("health",)),
    RouteSpec("/health/runtime", runtime_health, ("GET",), ("health",)),
    RouteSpec("/auth/me", get_current_user_stub, ("GET",), ("auth",), CurrentUser),
    RouteSpec("/projects", list_phase2_projects, ("GET",), ("projects",), list[ProjectSummary]),
    RouteSpec("/projects", create_phase2_project, ("POST",), ("projects",)),
    RouteSpec("/datasets", list_phase2_datasets, ("GET",), ("datasets",), list[DatasetSummary]),
    RouteSpec("/datasets/demo", create_phase2_demo_dataset, ("POST",), ("datasets",)),
    RouteSpec("/datasets/upload", upload_phase2_dataset, ("POST",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}", get_phase2_dataset, ("GET",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}/profile", get_phase2_dataset_profile, ("GET",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}/profile", create_phase2_dataset_profile, ("POST",), ("datasets",)),
    RouteSpec("/projects/{project_id}/upload-sessions", create_upload_session_stub, ("POST",), ("datasets",)),
    RouteSpec("/analysis-requests", submit_analysis_request_stub, ("POST",), ("analysis",)),
    RouteSpec("/jobs", create_phase2_job, ("POST",), ("jobs",)),
    RouteSpec("/jobs/{job_id}", get_phase2_job, ("GET",), ("jobs",)),
    RouteSpec("/jobs/{job_id}/events", get_phase2_job_events, ("GET",), ("jobs",)),
    RouteSpec("/jobs/{job_id}/events/stream", stream_phase1_job_events, ("GET",), ("jobs",)),
    RouteSpec("/jobs/{job_id}/stream", stream_phase2_job_events, ("GET",), ("jobs",)),
    RouteSpec("/jobs/{job_id}/tool-calls", get_phase2_job_tool_calls, ("GET",), ("jobs",)),
    RouteSpec("/jobs/{job_id}/artifacts", get_phase2_job_artifacts, ("GET",), ("jobs",)),
    RouteSpec("/artifacts/{artifact_id}", get_phase2_artifact, ("GET",), ("artifacts",)),
    RouteSpec("/artifacts/{artifact_id}/download", get_phase2_artifact_download, ("GET",), ("artifacts",)),
    RouteSpec("/tools", list_tools, ("GET",), ("tools",)),
    RouteSpec("/tools/mvp", list_mvp_tools, ("GET",), ("tools",)),
    # Phase 7: Planner API
    RouteSpec("/planner/preview", planner_preview_route, ("POST",), ("planner",)),
    RouteSpec("/planner/validate", planner_validate_route, ("POST",), ("planner",)),
    RouteSpec("/planner/intents", create_planner_intent_route, ("POST",), ("planner",)),
    RouteSpec("/planner/intents/{intent_id}", get_planner_intent_route, ("GET",), ("planner",)),
    RouteSpec("/planner/intents/{intent_id}/clarification", clarify_planner_intent_route, ("POST",), ("planner",)),
    RouteSpec("/planner/jobs", planner_jobs_route, ("POST",), ("planner",)),
    RouteSpec("/planner/providers", list_planner_providers, ("GET",), ("planner",)),
    RouteSpec("/planner/providers/status", planner_provider_status, ("GET",), ("planner",)),
    RouteSpec("/planner/providers/resolve", resolve_planner_provider_route, ("POST",), ("planner",)),
    RouteSpec("/planner/providers/test", test_planner_provider_route, ("POST",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}", get_planner_job, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/events", get_planner_job_events, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/events/stream", stream_planner_job_events, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/tool-calls", get_planner_job_tool_calls, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/artifacts", get_planner_job_artifacts, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/dependencies", get_planner_job_dependencies, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/artifacts/{artifact_id}/content", get_planner_job_artifact_content_route, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/result", get_planner_job_result, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/interpretations", create_planner_job_interpretation_route, ("POST",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/interpretations", list_planner_job_interpretations, ("GET",), ("planner",)),
    RouteSpec("/planner/interpretations/{interpretation_id}", get_planner_interpretation, ("GET",), ("planner",)),
    RouteSpec("/planner/interpretations/{interpretation_id}/evidence", get_planner_interpretation_evidence, ("GET",), ("planner",)),
    RouteSpec("/planner/analysis-plans/{plan_id}", get_planner_analysis_plan, ("GET",), ("planner",)),
    # Phase 10M-1: metadata-only Scientific Workspace API
    RouteSpec("/workspaces", create_workspace, ("POST",), ("workspaces",)),
    RouteSpec("/workspaces/{workspace_id}", get_workspace, ("GET",), ("workspaces",)),
    RouteSpec("/workspaces/{workspace_id}", patch_workspace, ("PATCH",), ("workspaces",)),
    RouteSpec("/projects/{project_id}/workspaces", list_project_workspaces, ("GET",), ("workspaces",)),
    RouteSpec("/projects/{project_id}/analysis-jobs", list_analysis_jobs, ("GET",), ("workspaces",)),
    RouteSpec("/workspaces/{workspace_id}/panels", list_workspace_panels, ("GET",), ("workspaces",)),
    RouteSpec("/workspaces/{workspace_id}/panels/{panel_id}", get_workspace_panel, ("GET",), ("workspaces",)),
    RouteSpec(
        "/workspaces/{workspace_id}/layout-revisions",
        list_workspace_layout_revisions,
        ("GET",),
        ("workspaces",),
    ),
    RouteSpec(
        "/workspaces/{workspace_id}/layout-revisions/{revision}",
        get_workspace_layout_revision,
        ("GET",),
        ("workspaces",),
    ),
    # Phase 10M-5: deterministic Report/Recipe composition over exact Workspace sources
    RouteSpec("/workspaces/{workspace_id}/report-composition/sources", get_report_composition_sources, ("GET",), ("workspaces", "reports")),
    RouteSpec("/workspaces/{workspace_id}/report-compositions/preview", preview_report_composition, ("POST",), ("workspaces", "reports")),
    RouteSpec("/workspaces/{workspace_id}/report-compositions", finalize_report_composition, ("POST",), ("workspaces", "reports")),
    RouteSpec("/workspaces/{workspace_id}/report-compositions", list_report_compositions, ("GET",), ("workspaces", "reports")),
    RouteSpec("/workspaces/{workspace_id}/report-compositions/{report_id}", get_report_composition, ("GET",), ("workspaces", "reports")),
    RouteSpec("/workspaces/{workspace_id}/report-compositions/{report_id}/recipe", get_report_composition_recipe, ("GET",), ("workspaces", "reports")),
    RouteSpec("/workspaces/{workspace_id}/report-compositions/{report_id}/exports/{format}", export_report_composition, ("GET",), ("workspaces", "reports")),
    # Phase 7: Secrets API
    RouteSpec("/me/secrets", create_secret, ("POST",), ("secrets",)),
    RouteSpec("/me/secrets", list_secrets, ("GET",), ("secrets",), list[SecretSummary]),
    RouteSpec("/me/secrets/{secret_id}", delete_secret, ("DELETE",), ("secrets",)),
)


def create_app() -> Any:
    settings = load_settings()
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        app = FastAPI(
            title=settings.app_name,
            version="0.1.0",
            description="Controlled API boundary for material data intelligence workflows.",
        )
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(settings.cors_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["ETag", "X-Idempotent-Replay"],
        )
        for route in ROUTES:
            app.add_api_route(
                route.path,
                route.endpoint,
                methods=list(route.methods),
                tags=list(route.tags),
                response_model=route.response_model,
            )
        return app
    except Exception:
        return AppSpec(title=settings.app_name, version="0.1.0", routes=ROUTES)


app = create_app()
