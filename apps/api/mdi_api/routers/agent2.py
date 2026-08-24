from __future__ import annotations

import json
import logging
from typing import Any, Iterator
from uuid import UUID

from fastapi import Body, Depends, Header, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

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
    ScientificResultNotReady,
    ScientificResultProjectionConflict,
    ScientificResultProjectionFailed,
)
from mdi_api.database import create_repository_factory
from mdi_api.config import load_settings
from mdi_api.research_agent.orchestration.queue import (
    AgentTurnQueue,
    DisabledAgentTurnQueue,
    RedisRQAgentTurnQueue,
)
from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES
from mdi_api.research_agent.schemas import CreateResearchTurnRequest, ResearchAction, ResearchTurnStatus, TERMINAL_TURN_STATUSES
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.execution.supervisor import ResearchExecutionSupervisor
from mdi_api.research_agent.execution.errors import (
    ExecutionCancelRequestFailed,
    ExecutionPlanIdentityMismatch,
    ExecutionPlanNotReady,
    ExecutionQueuePublishFailed,
    ExecutionSourceUnavailable,
    ExecutionSummaryConflict,
)
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.research_agent.memory.service import ResearchSessionMemoryService
from mdi_api.research_agent.memory.schemas import PinObjectRequest
from mdi_api.routers.auth import CurrentUser, get_current_user
from mdi_api.scientific_objects.schemas import ScientificObjectKind, ScientificObjectLifecycle
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.scientific_viewers import (
    ScientificViewerProjectionError,
    ScientificViewerProjectionService,
    build_scientific_viewer_registry,
)
from mdi_api.scientific_results.schemas import ScientificResultBundle
from mdi_api.scientific_results.relevance import ScientificResultRelevanceEvaluator
from mdi_api.scientific_results.service import ScientificResultProjectionService
from mdi_api.artifact_storage import create_artifact_storage_from_settings
from mdi_api.interpretation.service import InterpretationFailure
from mdi_api.interpretation.queue import RedisRQInterpretationQueue


logger = logging.getLogger(__name__)


class PromoteDatasetTableRequest(BaseModel):
    resource_id: str | None = Field(default=None, min_length=1, max_length=256)
    display_name: str | None = Field(default=None, min_length=1, max_length=512)


def get_research_turn_service() -> ResearchTurnService:
    return ResearchTurnService(create_repository_factory())


def get_scientific_object_service() -> ScientificObjectService:
    return ScientificObjectService(create_repository_factory(), DEFAULT_AGENT2_REGISTRIES.object_types)


def promote_dataset_table(
    project_id: str,
    dataset_id: str,
    request: PromoteDatasetTableRequest = Body(default=PromoteDatasetTableRequest()),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Promote a persisted parsed table resource into a versioned Agent2 object."""
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            require_project_access(session.connection, project_id, current_user, write=True)
            dataset = session.repositories.datasets.get(dataset_id)
            if str(dataset.get("projectId")) != project_id:
                raise UnauthorizedScientificObjectReference("source dataset is outside the project")
        settings = load_settings()
        logical, version = get_scientific_object_service().create_table_from_dataset(
            project_id=project_id,
            dataset_id=dataset_id,
            storage=create_artifact_storage_from_settings(settings),
            resource_id=request.resource_id,
            display_name=request.display_name,
            created_by_user_id=current_user.id,
        )
        return jsonable_encoder({"object": logical, "version": version})
    except Exception as exc:
        raise _http_error(exc) from exc


def get_agent_turn_queue() -> AgentTurnQueue:
    settings = load_settings()
    if settings.agent2_orchestration_enabled and settings.queue_backend == "redis":
        return RedisRQAgentTurnQueue(redis_url=settings.redis_url, queue_name=settings.agent2_queue_name)
    return DisabledAgentTurnQueue()


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
        try:
            queued = get_agent_turn_queue().enqueue_turn(result.turn_id)
            logger.info("research_turn_wakeup", extra={
                "turn_id": str(result.turn_id),
                "backend": queued.backend,
                "enqueued": queued.enqueued,
            })
        except Exception as queue_error:
            logger.warning("research_turn_wakeup_failed", extra={
                "turn_id": str(result.turn_id),
                "error_type": type(queue_error).__name__,
            })
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


def get_research_session_memory(
    project_id: str,
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            require_project_access(session.connection, project_id, current_user)
            state = ResearchSessionMemoryService().get_state(session, session_id=session_id, project_id=project_id)
            return jsonable_encoder(state.model_dump(mode="json"))
    except Exception as exc:
        raise _http_error(exc) from exc


def pin_research_result(
    project_id: str,
    session_id: str,
    result_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.unit_of_work() as unit:
            require_project_access(unit.connection, project_id, current_user, write=True)
            state = ResearchSessionMemoryService().pin_result(unit, session_id=session_id, project_id=project_id, result_id=result_id)
            return jsonable_encoder(state.model_dump(mode="json"))
    except Exception as exc:
        raise _http_error(exc) from exc


def unpin_research_result(
    project_id: str,
    session_id: str,
    result_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.unit_of_work() as unit:
            require_project_access(unit.connection, project_id, current_user, write=True)
            state = ResearchSessionMemoryService().unpin_result(unit, session_id=session_id, project_id=project_id, result_id=result_id)
            return jsonable_encoder(state.model_dump(mode="json"))
    except Exception as exc:
        raise _http_error(exc) from exc


def pin_research_object(
    project_id: str,
    session_id: str,
    request: PinObjectRequest = Body(...),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.unit_of_work() as unit:
            require_project_access(unit.connection, project_id, current_user, write=True)
            state = ResearchSessionMemoryService().pin_object(unit, session_id=session_id, project_id=project_id, object_ref=request.object_ref)
            return jsonable_encoder(state.model_dump(mode="json"))
    except Exception as exc:
        raise _http_error(exc) from exc


def unpin_research_object(
    project_id: str,
    session_id: str,
    request: PinObjectRequest = Body(...),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.unit_of_work() as unit:
            require_project_access(unit.connection, project_id, current_user, write=True)
            state = ResearchSessionMemoryService().unpin_object(unit, session_id=session_id, project_id=project_id, object_ref=request.object_ref)
            return jsonable_encoder(state.model_dump(mode="json"))
    except Exception as exc:
        raise _http_error(exc) from exc


def cancel_research_turn(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    try:
        turn = get_research_turn_service().cancel_turn(turn_id, current_user)
        return {"turn_id": turn["id"], "status": turn["status"], "updated_at": turn["updated_at"]}
    except Exception as exc:
        raise _http_error(exc) from exc


def dispatch_research_turn(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> JSONResponse:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user, write=True)
        result = ResearchExecutionDispatcher(factory).dispatch_turn(turn_id)
        return JSONResponse(status_code=202, content=jsonable_encoder({
            "turn_id": str(result.turn_id), "job_attached": True, "status": "QUEUED",
            "queue_backend": result.queue_backend, "queued": result.queued,
        }))
    except Exception as exc:
        raise _http_error(exc) from exc


def get_research_turn_progress(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user)
            job_id = str(turn.get("job_id") or "")
        if not job_id:
            return {
                "contract_version": "1.0", "turn_id": str(turn_id), "status": turn["status"],
                "plan_title": None, "steps": [], "active_step_ids": [], "completed_step_count": 0,
                "total_step_count": 0, "incremental_outputs": [], "warnings": [],
                "execution_outcome": None, "result_projection_pending": False,
            }
        view = ResearchExecutionSupervisor(factory).sync_for_job(job_id)
        return jsonable_encoder(view.model_dump(mode="json") if hasattr(view, "model_dump") else view)
    except Exception as exc:
        raise _http_error(exc) from exc


def get_research_turn_result(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user)
            if str(turn["status"]) not in {
                ResearchTurnStatus.RESULT_READY.value,
                ResearchTurnStatus.INTERPRETING.value,
                ResearchTurnStatus.COMPLETED.value,
                ResearchTurnStatus.PARTIAL.value,
            }:
                raise ScientificResultNotReady(str(turn_id))
            row = session.agent2.scientific_result_snapshots.get_latest_for_turn(turn_id)
            bundle = ScientificResultBundle.model_validate(row["bundle_json"])
            objects: dict[str, dict[str, Any]] = {}
            versions: dict[str, dict[str, Any]] = {}
            for ref in bundle.source_object_refs:
                try:
                    objects[str(ref.object_id)] = session.agent2.scientific_objects.get_object(ref.object_id)
                    versions[str(ref.version_id)] = session.agent2.scientific_objects.get_version(ref.version_id)
                except Exception:
                    pass
            relevance = ScientificResultRelevanceEvaluator().evaluate(bundle.source_object_refs, objects=objects, versions=versions)
            return {
                "result_id": str(bundle.result_id), "research_turn_id": str(bundle.research_turn_id),
                "research_question": bundle.research_question, "execution_status": bundle.execution_status.value,
                "relevance_status": relevance.value, "result_items": [item.model_dump(mode="json") for item in bundle.result_items],
                "figures": [item.model_dump(mode="json") for item in bundle.figures],
                "tables": [item.model_dump(mode="json") for item in bundle.tables],
                "limitations": [item.model_dump(mode="json") for item in bundle.limitations],
                "warnings": [item.model_dump(mode="json") for item in bundle.warnings],
            }
    except Exception as exc:
        raise _http_error(exc) from exc


def project_research_turn_result(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> JSONResponse:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user, write=True)
        storage = create_artifact_storage_from_settings(load_settings())
        def load_payload(artifact: dict[str, Any]) -> Any:
            media_type = str(artifact.get("contentType") or artifact.get("mediaType") or "")
            artifact_type = str(artifact.get("type") or "")
            if "json" not in media_type.lower() and "json" not in artifact_type.lower():
                return None
            return storage.get_json(str(artifact.get("storageKey") or artifact.get("storage_key")))
        service = ScientificResultProjectionService(
            factory,
            artifact_loader=load_payload,
        )
        row = service.project_turn(turn_id)
        return JSONResponse(status_code=200, content=jsonable_encoder({"turn_id": str(turn_id), "status": "RESULT_READY", "snapshot_id": str(row["id"])}))
    except Exception as exc:
        raise _http_error(exc) from exc


def interpret_research_turn(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> JSONResponse:
    """Authorized recovery hook; normal RESULT_READY turns are auto-queued."""
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user, write=True)
            status = str(turn["status"])
            existing_result_handoff = (
                status == ResearchTurnStatus.ORCHESTRATING.value
                and str(turn.get("action_type") or "") == ResearchAction.INTERPRET_RESULT.value
            )
            if status not in {ResearchTurnStatus.RESULT_READY.value, ResearchTurnStatus.INTERPRETING.value} and not existing_result_handoff:
                raise InterpretationFailure("INTERPRETATION_NOT_READY", f"turn status {status} cannot be interpreted")
        settings = load_settings()
        if not settings.agent2_interpretation_enabled or settings.queue_backend != "redis":
            raise InterpretationFailure("INTERPRETATION_QUEUE_DISABLED", "interpretation recovery queue is unavailable")
        queued = RedisRQInterpretationQueue(
            redis_url=settings.redis_url,
            queue_name=settings.agent2_interpretation_queue_name,
        ).enqueue_turn(turn_id)
        return JSONResponse(status_code=202, content=jsonable_encoder({
            "turn_id": str(turn_id),
            "status": status,
            "accepted": queued.enqueued or queued.message == "turn already queued",
        }))
    except Exception as exc:
        raise _http_error(exc) from exc


def get_research_turn_interpretation(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user)
            row = session.agent2.interpretations.get_for_turn(turn_id)
            if row is None:
                raise ScientificResultNotReady(str(turn_id))
            payload = dict(row["output_json"] or {})
            return {"interpretation_id": str(row["id"]), "research_turn_id": str(turn_id), "status": row["grounding_status"], "title": (payload.get("interpretation") or {}).get("title"), "message": payload.get("message"), "execution_status": payload.get("execution_status")}
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


def get_scientific_object_viewer(
    object_id: UUID,
    version_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        service = get_scientific_object_service()
        item = service.get_object(object_id)
        _authorize_object_project(service, str(item["project_id"]), current_user)
        projection = ScientificViewerProjectionService(
            service.repository_factory,
            create_artifact_storage_from_settings(load_settings()),
            build_scientific_viewer_registry(),
        ).project(object_id, version_id)
        return jsonable_encoder(projection.model_dump(mode="json"))
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
        "CONTEXT_RESOLUTION_STARTED": "context.resolving",
        "CONTEXT_RESOLVED": "context.ready",
        "CONTEXT_AMBIGUOUS": "assistant.preparing",
        "ORCHESTRATION_STARTED": "assistant.preparing",
        "DIRECT_ANSWER_READY": "assistant.message",
        "CLARIFICATION_REQUESTED": "assistant.clarification",
        "PLAN_REQUESTED": "analysis.ready_to_plan",
        "CAPABILITY_PLANNING_STARTED": "analysis.planning",
        "CAPABILITY_RESOLUTION_STARTED": "analysis.planning",
        "CAPABILITY_RESOLUTION_COMPLETED": "analysis.planning",
        "CAPABILITY_UNSUPPORTED": "analysis.unsupported",
        "CAPABILITY_PLAN_REJECTED": "analysis.plan.failed",
        "ANALYSIS_PLAN_BOUND": "analysis.plan.ready",
        "PLAN_READY": "analysis.plan.ready",
        "TURN_COMPLETED": "turn.answered",
        "TURN_CANCELED": "turn.canceled",
        "TURN_FAILED": "turn.failed",
        "EXECUTION_DISPATCH_STARTED": "analysis.queued",
        "JOB_ATTACHED": "analysis.queued",
        "JOB_QUEUE_PUBLISHED": "analysis.queued",
        "JOB_STARTED": "analysis.started",
        "EXECUTION_STEP_STARTED": "analysis.step.started",
        "EXECUTION_STEP_COMPLETED": "analysis.step.completed",
        "EXECUTION_STEP_FAILED": "analysis.step.failed",
        "EXECUTION_STEP_SKIPPED": "analysis.step.failed",
        "EXECUTION_OUTPUT_AVAILABLE": "analysis.output.available",
        "CANCELLATION_REQUESTED": "analysis.canceling",
        "EXECUTION_CANCELED": "analysis.canceled",
        "EXECUTION_SUCCEEDED": "analysis.execution.completed",
        "EXECUTION_PARTIAL": "analysis.execution.partial",
        "EXECUTION_FAILED": "analysis.failed",
        "RESULT_PENDING": "result.pending",
        "RESULT_PROJECTION_STARTED": "result.projecting",
        "RESULT_PROJECTION_FAILED": "result.failed",
        "RESULT_PROJECTED": "result.projecting",
        "RESULT_READY": "result.ready",
        "INTERPRETATION_STARTED": "assistant.interpreting",
        "INTERPRETATION_READY": "assistant.message",
        "TURN_PARTIAL": "turn.partial",
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
    if isinstance(exc, ScientificViewerProjectionError):
        return HTTPException(status_code=exc.status_code, detail={"code": exc.code, "summary": str(exc)})
    if isinstance(exc, ScientificResultNotReady):
        return HTTPException(status_code=409, detail={"code": "SCIENTIFIC_RESULT_NOT_READY", "summary": str(exc)})
    if isinstance(exc, InterpretationFailure):
        return HTTPException(status_code=409, detail={"code": exc.code, "summary": str(exc)})
    if isinstance(exc, (ScientificResultProjectionConflict, ScientificResultProjectionFailed)):
        return HTTPException(status_code=409, detail={"code": getattr(exc, "code", "RESULT_PROJECTION_FAILED"), "summary": str(exc)})
    execution_codes = {
        ExecutionPlanNotReady: "EXECUTION_PLAN_NOT_READY",
        ExecutionPlanIdentityMismatch: "EXECUTION_PLAN_IDENTITY_MISMATCH",
        ExecutionSourceUnavailable: "EXECUTION_SOURCE_UNAVAILABLE",
        ExecutionSummaryConflict: "EXECUTION_SUMMARY_CONFLICT",
    }
    for error_type, code in execution_codes.items():
        if isinstance(exc, error_type):
            return HTTPException(status_code=409, detail={"code": code, "summary": str(exc)})
    if isinstance(exc, ExecutionQueuePublishFailed):
        return HTTPException(status_code=503, detail={"code": "EXECUTION_QUEUE_PUBLISH_FAILED", "summary": str(exc)})
    if isinstance(exc, ExecutionCancelRequestFailed):
        return HTTPException(status_code=503, detail={"code": "EXECUTION_CANCEL_REQUEST_FAILED", "summary": str(exc)})
    return HTTPException(status_code=500, detail="Agent 2.0 请求处理失败。")
