from __future__ import annotations

import json
from typing import Any, Iterator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse

from mdi_api.access import require_project_access
from mdi_api.agent2_errors import (
    ConcurrentTurnModification,
    InvalidResearchTurnTransition,
    InvalidScientificObjectVersion,
    ResearchSessionProjectMismatch,
    ResearchTurnNotFound,
    ScientificObjectNotFound,
    ScientificObjectVersionNotFound,
    UnauthorizedScientificObjectReference,
)
from mdi_api.database import create_repository_factory
from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES
from mdi_api.research_agent.schemas import CreateResearchTurnRequest, ResearchTurnStatus, TERMINAL_TURN_STATUSES
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser, get_current_user
from mdi_api.scientific_objects.schemas import ScientificObjectKind, ScientificObjectLifecycle
from mdi_api.scientific_objects.service import ScientificObjectService


def get_research_turn_service() -> ResearchTurnService:
    return ResearchTurnService(create_repository_factory())


def get_scientific_object_service() -> ScientificObjectService:
    return ScientificObjectService(create_repository_factory(), DEFAULT_AGENT2_REGISTRIES.object_types)


def create_research_turn(
    project_id: str,
    session_id: str,
    request: CreateResearchTurnRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> JSONResponse:
    try:
        result = get_research_turn_service().receive_turn(
            project_id=project_id,
            session_id=session_id,
            request=request,
            current_user=current_user,
        )
        return JSONResponse(status_code=202, content=jsonable_encoder(result))
    except Exception as exc:
        raise _http_error(exc) from exc


def get_research_turn(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    try:
        return get_research_turn_service().get_turn(turn_id, current_user)
    except Exception as exc:
        raise _http_error(exc) from exc


def list_research_turns(
    project_id: str,
    session_id: str,
    cursor: int | None = Query(default=None, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        items = get_research_turn_service().list_session_turns(
            project_id=project_id,
            session_id=session_id,
            current_user=current_user,
            cursor=cursor,
            limit=limit,
        )
        return {"items": items, "next_cursor": items[-1]["sequence_no"] if len(items) == limit else None}
    except Exception as exc:
        raise _http_error(exc) from exc


def cancel_research_turn(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    try:
        turn = get_research_turn_service().cancel_turn(turn_id, current_user)
        return {"turn_id": turn["id"], "status": turn["status"], "updated_at": turn["updated_at"]}
    except Exception as exc:
        raise _http_error(exc) from exc


def stream_research_turn_events(
    turn_id: UUID,
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    current_user: CurrentUser = Depends(get_current_user),
) -> StreamingResponse:
    try:
        after_sequence = max(0, int(last_event_id or "0"))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Last-Event-ID 必须是非负整数。") from exc
    try:
        turn, events = get_research_turn_service().list_events(turn_id, current_user, after_sequence=after_sequence)
    except Exception as exc:
        raise _http_error(exc) from exc

    def generate() -> Iterator[str]:
        for event in events:
            event_name = _sse_event_name(str(event["event_type"]))
            body = {
                "id": int(event["sequence_no"]),
                "type": event_name,
                "turn_id": str(turn_id),
                "timestamp": event["created_at"].isoformat(),
                "payload": event["payload_json"] or {},
            }
            yield f"id: {event['sequence_no']}\nevent: {event_name}\ndata: {json.dumps(body, ensure_ascii=True, separators=(',', ':'))}\n\n"
        if ResearchTurnStatus(str(turn["status"])) not in TERMINAL_TURN_STATUSES:
            yield ": snapshot-complete\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def list_scientific_objects(
    project_id: str,
    kind: ScientificObjectKind | None = None,
    object_type: str | None = Query(default=None, max_length=128),
    lifecycle_status: ScientificObjectLifecycle | None = None,
    search: str | None = Query(default=None, max_length=512),
    limit: int = Query(default=50, ge=1, le=100),
    cursor: UUID | None = None,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    service = get_scientific_object_service()
    try:
        with service.repository_factory.session() as session:
            require_project_access(session.connection, project_id, current_user)
        items = service.list_project_objects(
            project_id,
            kind=kind.value if kind else None,
            object_type=object_type,
            lifecycle_status=lifecycle_status.value if lifecycle_status else None,
            search=search,
            cursor=cursor,
            limit=limit,
        )
        return {"items": items, "next_cursor": items[-1]["id"] if len(items) == limit else None}
    except Exception as exc:
        raise _http_error(exc) from exc


def get_scientific_object(object_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    service = get_scientific_object_service()
    try:
        item = service.get_object(object_id)
        _authorize_object_project(service, str(item["project_id"]), current_user)
        return item
    except Exception as exc:
        raise _http_error(exc) from exc


def list_scientific_object_versions(object_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    service = get_scientific_object_service()
    try:
        item = service.get_object(object_id)
        _authorize_object_project(service, str(item["project_id"]), current_user)
        return {"items": service.list_versions(object_id)}
    except Exception as exc:
        raise _http_error(exc) from exc


def get_scientific_object_version(object_id: UUID, version_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    service = get_scientific_object_service()
    try:
        item = service.get_object(object_id)
        _authorize_object_project(service, str(item["project_id"]), current_user)
        return service.get_version(object_id, version_id)
    except Exception as exc:
        raise _http_error(exc) from exc


def list_scientific_object_relationships(object_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    service = get_scientific_object_service()
    try:
        item = service.get_object(object_id)
        _authorize_object_project(service, str(item["project_id"]), current_user)
        return {"items": service.list_relationships(object_id)}
    except Exception as exc:
        raise _http_error(exc) from exc


def _authorize_object_project(service: ScientificObjectService, project_id: str, current_user: CurrentUser) -> None:
    with service.repository_factory.session() as session:
        require_project_access(session.connection, project_id, current_user)


def _sse_event_name(event_type: str) -> str:
    return {
        "TURN_RECEIVED": "turn.accepted",
        "CONTEXT_RESOLUTION_STARTED": "context.resolution.started",
        "CONTEXT_RESOLVED": "context.ready",
        "TURN_CANCELED": "turn.canceled",
        "TURN_FAILED": "turn.failed",
    }.get(event_type, "turn.status.changed")


def _http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, (ResearchTurnNotFound, ScientificObjectNotFound, ScientificObjectVersionNotFound, ResearchSessionProjectMismatch)):
        return HTTPException(status_code=404, detail="请求的 Agent 2.0 资源不存在。")
    if isinstance(exc, UnauthorizedScientificObjectReference):
        return HTTPException(status_code=403, detail="科研对象引用不属于当前项目。")
    if isinstance(exc, (ConcurrentTurnModification, InvalidResearchTurnTransition)):
        code = "TURN_TERMINAL" if str(exc) == "TURN_TERMINAL" else "TURN_CONFLICT"
        return HTTPException(status_code=409, detail={"code": code, "summary": str(exc)})
    if isinstance(exc, InvalidScientificObjectVersion):
        return HTTPException(status_code=422, detail=str(exc))
    return HTTPException(status_code=500, detail="Agent 2.0 请求处理失败。")
