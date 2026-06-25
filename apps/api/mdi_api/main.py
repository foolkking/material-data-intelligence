from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from mdi_api.config import load_settings
from mdi_api.phase1_demo import (
    get_phase1_job_artifacts,
    get_phase1_job_events,
    stream_phase1_job_events,
    submit_analysis_request_stub,
)
from mdi_api.routers.auth import CurrentUser, get_current_user_stub
from mdi_api.routers.datasets import DatasetSummary, create_upload_session_stub, list_datasets_stub
from mdi_api.routers.health import health
from mdi_api.routers.projects import ProjectSummary, create_project_stub, list_projects_stub
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
    RouteSpec("/auth/me", get_current_user_stub, ("GET",), ("auth",), CurrentUser),
    RouteSpec("/projects", list_projects_stub, ("GET",), ("projects",), list[ProjectSummary]),
    RouteSpec("/projects", create_project_stub, ("POST",), ("projects",)),
    RouteSpec("/datasets", list_datasets_stub, ("GET",), ("datasets",), list[DatasetSummary]),
    RouteSpec("/projects/{project_id}/upload-sessions", create_upload_session_stub, ("POST",), ("datasets",)),
    RouteSpec("/analysis-requests", submit_analysis_request_stub, ("POST",), ("analysis",)),
    RouteSpec("/jobs/{job_id}/events", get_phase1_job_events, ("GET",), ("jobs",)),
    RouteSpec("/jobs/{job_id}/events/stream", stream_phase1_job_events, ("GET",), ("jobs",)),
    RouteSpec("/jobs/{job_id}/artifacts", get_phase1_job_artifacts, ("GET",), ("jobs",)),
    RouteSpec("/tools", list_tools, ("GET",), ("tools",)),
    RouteSpec("/tools/mvp", list_mvp_tools, ("GET",), ("tools",)),
)


def create_app() -> Any:
    settings = load_settings()
    try:
        from fastapi import FastAPI

        app = FastAPI(
            title=settings.app_name,
            version="0.1.0",
            description="Controlled API boundary for material data intelligence workflows.",
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
