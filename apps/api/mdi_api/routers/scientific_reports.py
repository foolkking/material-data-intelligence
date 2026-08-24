from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from mdi_api.access import require_project_access
from mdi_api.config import load_settings
from mdi_api.database import create_repository_factory
from mdi_api.routers.auth import CurrentUser, get_current_user
from mdi_api.scientific_reports.queue import DisabledReportQueue, RedisRQReportQueue
from mdi_api.scientific_reports.requests import ScientificReportRequestService
from mdi_api.scientific_reports.service import ScientificReportError, ScientificReportService


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


__all__ = ["generate_scientific_report", "get_scientific_report", "get_scientific_report_by_id", "list_scientific_reports"]
