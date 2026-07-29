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
    PlannerJobsRequest,
    PlannerPreviewRequest,
    PlannerValidateRequest,
    clarify_planner_intent_route,
    create_planner_intent_route,
    get_planner_analysis_plan,
    get_planner_intent_route,
    get_planner_job,
    get_planner_job_artifacts,
    get_planner_job_artifact_content_route,
    get_planner_job_events,
    get_planner_job_result,
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
from mdi_api.routers.secrets import (
    CreateSecretRequest,
    SecretSummary,
    create_secret,
    delete_secret,
    list_secrets,
)
from mdi_api.routers.tools import list_mvp_tools, list_tools


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
    RouteSpec("/planner/jobs/{job_id}/artifacts/{artifact_id}/content", get_planner_job_artifact_content_route, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/result", get_planner_job_result, ("GET",), ("planner",)),
    RouteSpec("/planner/analysis-plans/{plan_id}", get_planner_analysis_plan, ("GET",), ("planner",)),
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
            allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
            allow_headers=["*"],
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
