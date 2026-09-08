from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field
from uuid import UUID

from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from mdi_api.access import require_project_access
from mdi_api.config import load_settings
from mdi_api.bootstrap.repository_factory import create_repository_factory
from mdi_api.transport.routers.auth import CurrentUser, get_current_user
from mdi_api.infrastructure.scientific_reports.queue import DisabledReportQueue, RedisRQReportQueue
from mdi_api.infrastructure.scientific_reports.requests import ScientificReportRequestService
from mdi_api.infrastructure.scientific_reports.service import ScientificReportError, ScientificReportService


class ScientificReportLifecycleRequest(BaseModel):
    lifecycle: Literal["ACTIVE", "ARCHIVED", "TRASHED"]


class ScientificReportOrganizationRequest(BaseModel):
    title: str | None = Field(default=None, max_length=256)
    pinned: bool | None = None


class ScientificReportRevisionRequest(BaseModel):
    reason: Literal["USER_REVISION", "DUPLICATE"] = "USER_REVISION"
    title: str | None = Field(default=None, max_length=256)


class ScientificReportBulkLifecycleRequest(BaseModel):
    reportIds: list[str] = Field(min_length=1, max_length=100)
    lifecycle: Literal["ACTIVE", "ARCHIVED"]


def _error(exc: Exception) -> Exception:
    if isinstance(exc, ScientificReportError):
        from fastapi import HTTPException
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from None
    return exc


def generate_scientific_report(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> JSONResponse:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user, write=True)
        settings = load_settings()
        queue = RedisRQReportQueue(redis_url=settings.redis_url, queue_name=settings.agent2_report_queue_name) if settings.agent2_report_enabled and settings.queue_backend == "redis" else DisabledReportQueue()
        request = ScientificReportRequestService(factory, queue=queue).request(turn_id, requested_by=current_user.id)
        return JSONResponse(status_code=202, content=jsonable_encoder(request))
    except Exception as exc:
        _error(exc)
        raise


def get_scientific_report(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user)
        return ScientificReportService(factory).get_for_turn(turn_id)
    except Exception as exc:
        _error(exc)
        raise


def get_scientific_report_status(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user)
        return ScientificReportService(factory).status_for_turn(turn_id)
    except Exception as exc:
        _error(exc)
        raise


def get_scientific_report_by_id(report_id: str, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        service = ScientificReportService(factory)
        report = service.get_by_report_id(report_id)
        with factory.session() as session:
            require_project_access(session.connection, str(report["project_id"]), current_user)
        return report
    except Exception as exc:
        _error(exc)
        raise


def list_scientific_reports(project_id: str, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            require_project_access(session.connection, project_id, current_user)
        return ScientificReportService(factory).list_project(project_id)
    except Exception as exc:
        _error(exc)
        raise


def update_scientific_report_lifecycle(
    report_id: str,
    request: ScientificReportLifecycleRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        service = ScientificReportService(factory)
        report = service.get_by_report_id(report_id)
        with factory.session() as session:
            require_project_access(session.connection, str(report["project_id"]), current_user, write=True)
        return service.set_lifecycle(report_id, request.lifecycle)
    except Exception as exc:
        _error(exc)
        raise


def bulk_update_scientific_report_lifecycle(
    project_id: str,
    request: ScientificReportBulkLifecycleRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            require_project_access(
                session.connection,
                project_id,
                current_user,
                write=True,
            )
        return ScientificReportService(factory).bulk_set_lifecycle(
            project_id,
            request.reportIds,
            request.lifecycle,
        )
    except Exception as exc:
        _error(exc)
        raise


def update_scientific_report_organization(
    report_id: str,
    request: ScientificReportOrganizationRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Update bounded navigation metadata without mutating the Report snapshot."""
    try:
        factory = create_repository_factory()
        service = ScientificReportService(factory)
        report = service.get_by_report_id(report_id)
        with factory.session() as session:
            require_project_access(session.connection, str(report["project_id"]), current_user, write=True)
        return service.set_organization(
            report_id,
            request.model_dump(exclude_unset=True),
        )
    except Exception as exc:
        _error(exc)
        raise


def get_scientific_report_dependency_impact(
    report_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Return a bounded, authorized dependency preview before report trashing."""
    try:
        factory = create_repository_factory()
        service = ScientificReportService(factory)
        report = service.get_by_report_id(report_id)
        with factory.session() as session:
            require_project_access(session.connection, str(report["project_id"]), current_user)
        return service.dependency_impact(report_id)
    except Exception as exc:
        _error(exc)
        raise


def create_scientific_report_revision(
    report_id: str,
    request: ScientificReportRevisionRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        service = ScientificReportService(factory)
        report = service.get_by_report_id(report_id)
        with factory.session() as session:
            require_project_access(
                session.connection,
                str(report["project_id"]),
                current_user,
                write=True,
            )
        return service.create_revision(
            report_id,
            created_by=current_user.id,
            reason=request.reason,
            title=request.title,
        )
    except Exception as exc:
        _error(exc)
        raise


def list_scientific_report_revisions(
    report_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        service = ScientificReportService(factory)
        report = service.get_by_report_id(report_id)
        with factory.session() as session:
            require_project_access(
                session.connection,
                str(report["project_id"]),
                current_user,
            )
        return service.list_revisions(report_id)
    except Exception as exc:
        _error(exc)
        raise


def compare_scientific_report_revisions(
    report_id: str,
    base_report_id: str | None = None,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        service = ScientificReportService(factory)
        report = service.get_by_report_id(report_id)
        with factory.session() as session:
            require_project_access(
                session.connection,
                str(report["project_id"]),
                current_user,
            )
        return service.compare_revisions(
            report_id,
            base_report_id=base_report_id,
        )
    except Exception as exc:
        _error(exc)
        raise


__all__ = [
    "bulk_update_scientific_report_lifecycle",
    "compare_scientific_report_revisions",
    "create_scientific_report_revision",
    "generate_scientific_report",
    "get_scientific_report",
    "get_scientific_report_status",
    "get_scientific_report_by_id",
    "get_scientific_report_dependency_impact",
    "list_scientific_report_revisions",
    "list_scientific_reports",
    "update_scientific_report_lifecycle",
    "update_scientific_report_organization",
]
