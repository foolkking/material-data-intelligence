from __future__ import annotations

import json
import logging
from typing import Literal

from fastapi import Depends, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from mdi_api.access import require_project_access
from mdi_api.bootstrap.repository_factory import create_repository_factory
from mdi_api.observability import (
    OBSERVABILITY_EVENT_VERSION,
    bounded_correlation,
    release_sha,
    request_id,
)
from mdi_api.transport.routers.auth import CurrentUser, get_current_user


logger = logging.getLogger(__name__)


class ClientCorrelation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    projectId: str | None = Field(
        default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
    )
    researchTurnId: str | None = Field(
        default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
    )
    jobId: str | None = Field(
        default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
    )
    contextManifestId: str | None = Field(
        default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
    )


class ClientExceptionEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schemaVersion: Literal["ClientExceptionEvent/1.0"]
    source: Literal["window.error", "unhandledrejection"]
    releaseSha: str = Field(
        min_length=7,
        max_length=64,
        pattern=r"^(?:[0-9a-fA-F]{7,64}|LOCAL_WORKTREE)$",
    )
    route: Literal[
        "/account",
        "/admin",
        "/analysis",
        "/console",
        "/notifications",
        "/other",
        "/projects/:projectId",
        "/projects/:projectId/data",
        "/projects/:projectId/history",
        "/projects/:projectId/reports",
        "/projects/:projectId/research",
        "/settings",
        "/tasks",
        "/trash",
    ]
    errorType: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z_$][A-Za-z0-9_$.-]*$",
    )
    clientEventId: str = Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$",
    )
    correlation: ClientCorrelation = Field(default_factory=ClientCorrelation)


def capture_client_exception(
    event: ClientExceptionEvent,
    request: Request,
    _current_user: CurrentUser = Depends(get_current_user),
) -> Response:
    project_id = event.correlation.projectId
    if project_id is not None:
        with create_repository_factory().session() as session:
            require_project_access(session.connection, project_id, _current_user)
    correlation = bounded_correlation(
        {
            "requestId": getattr(request.state, "request_id", None),
            **event.correlation.model_dump(exclude_none=True),
        }
    )
    payload = {
        "schemaVersion": OBSERVABILITY_EVENT_VERSION,
        "source": event.source,
        "component": "frontend",
        "releaseSha": release_sha(),
        "frontendReleaseSha": (
            event.releaseSha.lower()
            if event.releaseSha != "LOCAL_WORKTREE"
            else "LOCAL_WORKTREE"
        ),
        "route": event.route,
        "errorType": event.errorType,
        "clientEventId": event.clientEventId,
        "correlation": correlation,
        "sanitized": True,
    }
    logger.error(
        "operational_exception %s",
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
    )
    return Response(
        status_code=202,
        headers={"X-Request-ID": request_id(getattr(request.state, "request_id", None))},
    )


__all__ = ["ClientExceptionEvent", "capture_client_exception"]
