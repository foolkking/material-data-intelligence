from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Iterator
from uuid import UUID, NAMESPACE_URL, uuid5

from fastapi import Body, Depends, Header, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from mdi_api.access import require_project_access
from mdi_api.application.research.ports import (
    ProjectAccessDenied,
    ProjectAccessNotFound,
    ResearchActorContext,
)
from mdi_api.agent2_errors import (
    ConcurrentTurnModification,
    InvalidResearchTurnTransition,
    InvalidScientificObjectVersion,
    ResearchResourceLimitExceeded,
    ResearchSessionProjectMismatch,
    ResearchTurnNotFound,
    ResearchTurnAdmissionConflict,
    ScientificObjectNotFound,
    ScientificObjectVersionNotFound,
    UnauthorizedScientificObjectReference,
    ScientificResultNotReady,
    ScientificResultSnapshotNotFound,
    ScientificResultProjectionConflict,
    ScientificResultProjectionFailed,
)
from mdi_api.bootstrap.repository_factory import create_repository_factory
from mdi_api.config import load_settings
from mdi_api.research_agent.orchestration.queue import (
    AgentTurnQueue,
    DisabledAgentTurnQueue,
    RedisRQAgentTurnQueue,
)
from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES
from mdi_api.research_agent.schemas import (
    CreateResearchTurnRequest,
    ResearchAction,
    ResearchTurnEventType,
    ResearchTurnStatus,
    TERMINAL_TURN_STATUSES,
)
from mdi_api.research_agent.lifecycle import (
    build_autonomy_projection,
    build_lifecycle_projection,
    is_stale_active_turn,
)
from mdi_api.research_agent.execution.dispatcher import (
    DisabledExecutionQueue,
    ExecutionQueue,
    ResearchExecutionDispatcher,
)
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
from mdi_api.research_agent.context.policy import ContextOperation, context_budget_policy
from mdi_api.research_agent.context.schemas import ContextManifest, ContextManifestItem
from mdi_api.research_agent.memory.service import ResearchSessionMemoryService
from mdi_api.research_agent.memory.schemas import PinObjectRequest
from mdi_api.transport.routers.auth import CurrentUser, get_current_user
from mdi_api.domain.scientific_objects.contracts import (
    ScientificDatasetQueryRequest,
    ScientificObjectAdmissionRequest,
    ScientificObjectKind,
    ScientificObjectLifecycle,
    ScientificObjectVersionCreateRequest,
)
from mdi_api.infrastructure.scientific_objects.service import ScientificObjectService
from mdi_api.scientific_viewers import (
    ScientificViewerProjectionError,
    ScientificViewerProjectionService,
    build_scientific_viewer_registry,
)
from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.domain.scientific_results.relevance import ScientificResultRelevanceEvaluator
from mdi_api.infrastructure.scientific_results.artifact_loader import load_committed_json_artifact
from mdi_api.infrastructure.scientific_results.service import ScientificResultProjectionService
from mdi_api.artifact_storage import create_artifact_storage_from_settings
from mdi_api.infrastructure.interpretation.service import InterpretationFailure
from mdi_api.infrastructure.interpretation.queue import RedisRQInterpretationQueue


logger = logging.getLogger(__name__)


class PromoteDatasetTableRequest(BaseModel):
    resource_id: str | None = Field(default=None, min_length=1, max_length=256)
    display_name: str | None = Field(default=None, min_length=1, max_length=512)


class ScientificObjectMetadataUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=512)
    archived: bool | None = None
    lifecycle: ScientificObjectLifecycle | None = None


class ScientificObjectBulkLifecycleRequest(BaseModel):
    object_ids: list[UUID] = Field(min_length=1, max_length=100)
    lifecycle: ScientificObjectLifecycle


def get_research_turn_service() -> ResearchTurnService:
    settings = load_settings()
    return ResearchTurnService(
        create_repository_factory(),
        max_active_turns_per_project=settings.agent2_max_active_turns_per_project,
    )


def _research_actor(current_user: CurrentUser) -> ResearchActorContext:
    return ResearchActorContext(id=current_user.id)


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


def _research_execution_queue() -> ExecutionQueue:
    settings = load_settings()
    if settings.queue_backend == "redis":
        from mdi_workers.queue_runtime import RedisRQQueueBackend

        return RedisRQQueueBackend(
            redis_url=settings.redis_url,
            queue_name=settings.agent2_execution_queue_name,
        )
    return DisabledExecutionQueue()


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
            current_user=_research_actor(current_user),
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
        return get_research_turn_service().get_turn(turn_id, _research_actor(current_user))
    except Exception as exc:
        raise _http_error(exc) from exc


def get_research_turn_context_manifest(
    turn_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Return the bounded immutable context manifest for a ResearchTurn."""
    try:
        turn, events = get_research_turn_service().list_events(
            turn_id,
            _research_actor(current_user),
        )
        context_event = next(
            (
                event
                for event in events
                if event["event_type"] == "CONTEXT_RESOLVED"
            ),
            None,
        )
        if context_event is None:
            raise ScientificResultNotReady(f"context manifest unavailable for {turn_id}")
        manifest = (context_event.get("payload_json") or {}).get("context_manifest")
        if not isinstance(manifest, dict):
            # Older completed turns persisted the immutable context snapshot
            # reference but predated the embedded manifest contract.  Build a
            # deterministic, bounded read-model from that snapshot so history
            # remains auditable without mutating the event or introducing a
            # second context authority.
            factory = create_repository_factory()
            with factory.session() as session:
                snapshot = session.agent2.research_context_snapshots.get_for_turn(turn_id)
            if snapshot is None:
                raise ScientificResultNotReady(f"context manifest unavailable for {turn_id}")
            manifest = _compat_context_manifest_from_snapshot(turn, snapshot)
        operation_manifests: list[dict[str, Any]] = []
        for event in events:
            payload = event.get("payload_json") or {}
            candidate = payload.get("context_manifest")
            if not isinstance(candidate, dict):
                continue
            operation = str(payload.get("operation") or candidate.get("operation") or "ORCHESTRATOR")
            operation_manifests.append({
                "operation": operation,
                "manifest": candidate,
                "event_id": str(event.get("id")) if event.get("id") is not None else None,
                "sequence_no": event.get("sequence_no"),
            })
        if not operation_manifests:
            operation_manifests = [{
                "operation": str(manifest.get("operation") or "ORCHESTRATOR"),
                "manifest": manifest,
                "event_id": str(context_event.get("id")) if context_event.get("id") is not None else None,
                "sequence_no": context_event.get("sequence_no"),
            }]
        return jsonable_encoder({
            "turn_id": str(turn_id),
            # Backward-compatible primary manifest for existing clients.
            "manifest": manifest,
            "manifests": operation_manifests,
        })
    except ScientificResultNotReady as exc:
        # This is an expected transitional state while a new Turn is still
        # resolving context. Return the typed 409 without emitting a false
        # server-error traceback on every UI poll.
        raise _http_error(exc) from exc
    except Exception as exc:
        logger.exception("context_manifest_projection_failed", extra={"turn_id": str(turn_id)})
        raise _http_error(exc) from exc


def _compat_context_manifest_from_snapshot(
    turn: dict[str, Any],
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Project legacy immutable context snapshots into ContextManifest 2.0.

    This is intentionally a read-only compatibility projection.  Exact
    scientific object/version and Result references come only from the
    persisted snapshot; the provider receives bounded opaque refs.
    """

    items: list[ContextManifestItem] = []

    def add_item(
        *,
        item_id: str,
        kind: str,
        authority_class: str,
        source_identity: str,
        opaque_ref: str,
        content: Any,
        inclusion_reason: str,
        selection_mode: str,
        object_id: str | None = None,
        version_id: str | None = None,
        result_ref: str | None = None,
    ) -> None:
        encoded = json.dumps(content, sort_keys=True, separators=(",", ":"), default=str)
        items.append(
            ContextManifestItem(
                item_id=item_id,
                kind=kind,
                authority_class=authority_class,
                server_side_source_identity=source_identity,
                provider_opaque_ref=opaque_ref,
                exact_object_id=object_id,
                exact_object_version_id=version_id,
                result_ref=result_ref,
                inclusion_reason=inclusion_reason,
                selection_mode=selection_mode,
                authorization_checked=True,
                content_fingerprint=hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
                estimated_tokens=max(1, len(encoded.encode("utf-8")) // 4),
            )
        )

    for index, ref in enumerate(snapshot.get("active_scope_refs_json") or [], start=1):
        if not isinstance(ref, dict) or not ref.get("object_id") or not ref.get("version_id"):
            continue
        object_id = str(ref["object_id"])
        version_id = str(ref["version_id"])
        add_item(
            item_id=f"object_{index}",
            kind="SCIENTIFIC_OBJECT",
            authority_class="SCIENTIFIC_DATA",
            source_identity=f"{object_id}:{version_id}",
            opaque_ref=f"object_{index}",
            content=ref,
            inclusion_reason="persisted active scientific scope",
            selection_mode="CURRENT",
            object_id=object_id,
            version_id=version_id,
        )

    for index, ref in enumerate(snapshot.get("selection_refs_json") or [], start=1):
        if not isinstance(ref, dict) or not ref.get("object_id") or not ref.get("version_id"):
            continue
        object_id = str(ref["object_id"])
        version_id = str(ref["version_id"])
        add_item(
            item_id=f"selection_{index}",
            kind="SCIENTIFIC_SELECTION",
            authority_class="SCIENTIFIC_DATA",
            source_identity=f"{object_id}:{version_id}",
            opaque_ref=f"selection_{index}",
            content=ref,
            inclusion_reason="persisted UI scientific selection",
            selection_mode="UI_SELECTION",
            object_id=object_id,
            version_id=version_id,
        )

    for index, selection in enumerate(snapshot.get("scientific_selections_json") or [], start=1):
        if not isinstance(selection, dict):
            continue
        ref = selection.get("object_ref") or selection.get("objectRef") or {}
        if not isinstance(ref, dict) or not ref.get("object_id") or not ref.get("version_id"):
            continue
        object_id = str(ref["object_id"])
        version_id = str(ref["version_id"])
        add_item(
            item_id=f"scientific_selection_{index}",
            kind="SCIENTIFIC_SELECTION",
            authority_class="SCIENTIFIC_DATA",
            source_identity=f"{object_id}:{version_id}",
            opaque_ref=f"scientific_selection_{index}",
            content=selection,
            inclusion_reason="persisted semantic UI selection",
            selection_mode="EXPLICIT",
            object_id=object_id,
            version_id=version_id,
        )

    for index, result in enumerate(snapshot.get("referenced_result_refs_json") or [], start=1):
        result_id = result.get("result_id") if isinstance(result, dict) else result
        if not result_id:
            continue
        result_id = str(result_id)
        add_item(
            item_id=f"result_{index}",
            kind="SCIENTIFIC_RESULT",
            authority_class="SCIENTIFIC_RESULT",
            source_identity=result_id,
            opaque_ref=f"result_{index}",
            content={"result_id": result_id},
            inclusion_reason="persisted referenced Result",
            selection_mode="CONTINUATION",
            result_ref=result_id,
        )

    session_id = str(turn.get("research_session_id") or snapshot.get("research_session_id") or "session")
    for index, constraint in enumerate(snapshot.get("effective_constraints_json") or [], start=1):
        add_item(
            item_id=f"constraint_{index}",
            kind="USER_CONSTRAINT",
            authority_class="USER_CONSTRAINT",
            source_identity=f"{session_id}:constraint:{index}",
            opaque_ref=f"constraint_{index}",
            content=constraint,
            inclusion_reason="persisted user constraint",
            selection_mode="EXPLICIT",
        )

    if snapshot.get("research_goal"):
        add_item(
            item_id="goal_1",
            kind="RESEARCH_GOAL",
            authority_class="CONVERSATIONAL_NARRATIVE",
            source_identity=f"{session_id}:goal",
            opaque_ref="goal_1",
            content=str(snapshot["research_goal"]),
            inclusion_reason="persisted research goal",
            selection_mode="CURRENT",
        )

    fingerprint = str(snapshot.get("context_fingerprint") or "")
    if len(fingerprint) != 64 or any(char not in "0123456789abcdef" for char in fingerprint.lower()):
        fingerprint = hashlib.sha256(
            json.dumps(snapshot, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        ).hexdigest()
    policy = context_budget_policy(ContextOperation.ORCHESTRATOR)
    priority = {
        "SCIENTIFIC_OBJECT": 0,
        "SCIENTIFIC_SELECTION": 0,
        "SCIENTIFIC_RESULT": 1,
        "SCIENTIFIC_EVIDENCE": 1,
        "USER_CONSTRAINT": 2,
        "RESEARCH_GOAL": 3,
    }
    critical_kinds = {"SCIENTIFIC_OBJECT", "SCIENTIFIC_SELECTION", "SCIENTIFIC_RESULT", "SCIENTIFIC_EVIDENCE"}
    ordered = sorted(
        enumerate(items),
        key=lambda pair: (priority.get(pair[1].kind, 99), pair[0]),
    )
    included: list[ContextManifestItem] = []
    excluded: list[str] = []
    estimated = 0
    for index, item in ordered:
        exceeds_budget = estimated + item.estimated_tokens > policy.effective_input_budget
        exceeds_item_limit = len(included) >= 128
        if not exceeds_budget and not exceeds_item_limit:
            included.append(item)
            estimated += item.estimated_tokens
            continue
        if item.kind in critical_kinds:
            raise ValueError("critical scientific context exceeds the operation budget")
        excluded.append(item.item_id)
    over_budget = bool(excluded)
    created_at = snapshot.get("created_at") or datetime.now(timezone.utc)
    manifest = ContextManifest(
        context_manifest_id=uuid5(
            NAMESPACE_URL,
            f"mdi:compat-context-manifest:{turn['id']}:{snapshot['id']}",
        ),
        operation="ORCHESTRATOR",
        project_id=str(turn.get("project_id") or snapshot["project_id"]),
        research_session_id=session_id,
        research_turn_id=UUID(str(turn["id"])),
        policy_version="agent2.context-compat/1.0",
        included_items=included,
        excluded_items=excluded[:64],
        estimated_input_tokens=estimated,
        input_budget=policy.effective_input_budget,
        reserved_output_tokens=policy.reserved_output_tokens,
        repair_margin=policy.repair_margin,
        compaction_state="COMPACTED" if over_budget else "NONE",
        truncation_state="NONE",
        context_fingerprint=fingerprint.lower(),
        created_at=created_at,
    )
    return manifest.model_dump(mode="json")


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
            current_user=_research_actor(current_user),
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
        turn = get_research_turn_service().cancel_turn(
            turn_id,
            _research_actor(current_user),
        )
        return {"turn_id": turn["id"], "status": turn["status"], "updated_at": turn["updated_at"]}
    except Exception as exc:
        raise _http_error(exc) from exc


def dispatch_research_turn(turn_id: UUID, current_user: CurrentUser = Depends(get_current_user)) -> JSONResponse:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user, write=True)
        result = ResearchExecutionDispatcher(
            factory,
            queue=_research_execution_queue(),
        ).dispatch_turn(turn_id)
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
            decision = session.agent2.research_turn_decisions.get_for_turn(turn_id)
            turn_events = session.agent2.research_turn_events.list_for_turn(turn_id)
            autonomy = build_autonomy_projection(turn_events)
            interpretation_retry_warning = _interpretation_retry_warning(
                turn,
                turn_events,
            )
        if not job_id:
            payload = {
                "contract_version": "1.0", "turn_id": str(turn_id), "status": turn["status"],
                "response_kind": _research_progress_response_kind(turn, decision),
                "plan_title": None, "steps": [], "active_step_ids": [], "completed_step_count": 0,
                "total_step_count": 0, "incremental_outputs": [], "warnings": [],
                "execution_outcome": None, "result_projection_pending": False,
            }
            if interpretation_retry_warning is not None:
                payload["warnings"].append(interpretation_retry_warning)
            if autonomy["enabled"]:
                payload["autonomy"] = autonomy
            return payload
        try:
            view = ResearchExecutionSupervisor(factory).sync_for_job(job_id)
        except ValueError as exc:
            # A small number of pre-contract local history fixtures have an
            # exact terminal Result but no parseable AnalysisPlan payload. A
            # progress read must not turn that immutable Result into a 500 or
            # attempt to reconstruct/re-execute it. This fallback is limited
            # to terminal historical turns and exposes the missing process
            # detail explicitly.
            if (
                "missing analysis_plan_json" in str(exc)
                and ResearchTurnStatus(str(turn["status"])) in TERMINAL_TURN_STATUSES
            ):
                return _historical_terminal_progress(turn_id, str(turn["status"]))
            raise
        payload = jsonable_encoder(
            view.model_dump(mode="json") if hasattr(view, "model_dump") else view
        )
        if interpretation_retry_warning is not None:
            payload.setdefault("warnings", []).append(interpretation_retry_warning)
        if autonomy["enabled"]:
            payload["autonomy"] = autonomy
        return payload
    except Exception as exc:
        raise _http_error(exc) from exc


def research_turn_correlation_payload(
    session: Any,
    turn: dict[str, Any],
) -> dict[str, Any]:
    """Project a bounded, non-secret operational lineage for one exact Turn.

    The repositories remain authoritative. This view exposes only stable
    identities and lifecycle states required to correlate a user-visible
    ResearchTurn with persisted execution and communication records.
    """

    turn_id = UUID(str(turn["id"]))
    project_id = str(turn["project_id"])
    job_id = str(turn.get("job_id") or "") or None
    warnings: list[str] = []
    job: dict[str, Any] | None = None
    tool_call_rows: list[dict[str, Any]] = []
    if job_id:
        try:
            stored_job = session.repositories.jobs.get(job_id)
            job = {
                "job_id": job_id,
                "status": str(stored_job.get("status") or "unknown"),
            }
        except (LookupError, KeyError):
            job = {"job_id": job_id, "status": "missing"}
            warnings.append("JOB_RECORD_MISSING")
        tool_call_rows = list(session.repositories.tool_calls.list_for_job(job_id))

    tool_calls = [
        {
            "tool_call_id": str(item.get("id") or ""),
            "step_id": str(item.get("stepId") or item.get("step_id") or ""),
            "status": str(item.get("status") or "unknown"),
        }
        for item in tool_call_rows[:64]
        if item.get("id")
    ]

    scientific_result: dict[str, Any] | None = None
    try:
        result_row = session.agent2.scientific_result_snapshots.get_latest_for_turn(
            turn_id,
        )
    except ScientificResultSnapshotNotFound:
        result_row = None
    if result_row is not None:
        bundle = dict(result_row.get("bundle_json") or {})
        if str(result_row.get("project_id")) != project_id:
            warnings.append("RESULT_PROJECT_MISMATCH")
        else:
            scientific_result = {
                "result_snapshot_id": str(result_row["id"]),
                "result_id": (
                    str(bundle["result_id"]) if bundle.get("result_id") else None
                ),
                "execution_status": str(
                    result_row.get("execution_status") or "unknown"
                ),
                "job_id": (
                    str(result_row["job_id"])
                    if result_row.get("job_id")
                    else None
                ),
            }

    report_row = session.agent2.scientific_reports.get_for_turn(turn_id)
    report: dict[str, Any] | None = None
    if report_row is not None:
        if str(report_row.get("project_id")) != project_id:
            warnings.append("REPORT_PROJECT_MISMATCH")
        elif (
            scientific_result is not None
            and str(report_row.get("scientific_result_snapshot_id"))
            != scientific_result["result_snapshot_id"]
        ):
            warnings.append("REPORT_RESULT_MISMATCH")
        else:
            report = {
                "report_id": str(report_row["report_id"]),
                "report_snapshot_id": str(report_row["id"]),
                "grounding_status": str(
                    report_row.get("grounding_status") or "unknown"
                ),
            }

    # The correlation response remains a bounded read model. Lifecycle
    # details are derived from existing authoritative records; this does not
    # create a second state machine or expose raw tool payloads.
    event_repo = getattr(session.agent2, "research_turn_events", None)
    events = (
        event_repo.list_for_turn(turn_id)
        if event_repo is not None and hasattr(event_repo, "list_for_turn")
        else []
    )
    context_repo = getattr(session.agent2, "research_context_snapshots", None)
    context_snapshot = (
        context_repo.get_for_turn(turn_id)
        if context_repo is not None and hasattr(context_repo, "get_for_turn")
        else None
    )
    decisions = getattr(session.agent2, "research_turn_decisions", None)
    decision = (
        decisions.get_for_turn(turn_id)
        if decisions is not None and hasattr(decisions, "get_for_turn")
        else None
    )
    resolutions = getattr(session.agent2, "research_capability_resolutions", None)
    resolution = (
        resolutions.get_for_turn(turn_id)
        if resolutions is not None and hasattr(resolutions, "get_for_turn")
        else None
    )
    capability_plans = getattr(session.agent2, "research_capability_plans", None)
    capability_plan = (
        capability_plans.get_for_turn(turn_id)
        if capability_plans is not None and hasattr(capability_plans, "get_for_turn")
        else None
    )
    summaries = getattr(session.agent2, "research_execution_summaries", None)
    execution_summary = (
        summaries.get_for_turn(turn_id)
        if summaries is not None and hasattr(summaries, "get_for_turn")
        else None
    )
    interpretations = getattr(session.agent2, "interpretations", None)
    interpretation = (
        interpretations.get_for_turn(turn_id)
        if interpretations is not None and hasattr(interpretations, "get_for_turn")
        else None
    )
    report_generations = getattr(session.agent2, "scientific_report_generations", None)
    report_generation = (
        report_generations.get_for_turn(turn_id)
        if report_generations is not None and hasattr(report_generations, "get_for_turn")
        else None
    )
    job_row = None
    if job_id and hasattr(session.repositories.jobs, "get"):
        try:
            job_row = session.repositories.jobs.get(job_id)
        except (LookupError, KeyError):
            job_row = None
    lifecycle = build_lifecycle_projection(
        turn,
        events=events,
        context_snapshot=context_snapshot,
        decision=decision,
        resolution=resolution,
        capability_plan=capability_plan,
        execution_summary=execution_summary,
        job=job_row,
        tool_calls=tool_call_rows,
        interpretation=interpretation,
        report=report_row,
        report_generation=report_generation,
        result_snapshot=result_row,
        stale=is_stale_active_turn(
            turn,
            stale_after_seconds=max(
                1,
                int(getattr(load_settings(), "agent2_startup_recovery_stale_minutes", 15))
                * 60,
            ),
        ),
    )

    return {
        "contract_version": "1.0",
        "project_id": project_id,
        "research_session_id": str(turn["research_session_id"]),
        "research_turn_id": str(turn_id),
        "job": job,
        "tool_calls": tool_calls,
        "tool_calls_truncated": len(tool_call_rows) > 64,
        "scientific_result": scientific_result,
        "report": report,
        "lifecycle": lifecycle,
        "integrity_warnings": sorted(set(warnings)),
    }


def get_research_turn_correlation(
    turn_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        factory = create_repository_factory()
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(
                session.connection,
                str(turn["project_id"]),
                current_user,
            )
            return research_turn_correlation_payload(session, turn)
    except Exception as exc:
        raise _http_error(exc) from exc


def _historical_terminal_progress(turn_id: UUID, status: str) -> dict[str, Any]:
    outcome = (
        "SUCCESS"
        if status == ResearchTurnStatus.COMPLETED.value
        else "PARTIAL"
        if status == ResearchTurnStatus.PARTIAL.value
        else "FAILED"
    )
    return {
        "contract_version": "1.0",
        "turn_id": str(turn_id),
        "status": status,
        "response_kind": "SCIENTIFIC_EXECUTION",
        "plan_title": "Historical completed analysis",
        "steps": [],
        "active_step_ids": [],
        "completed_step_count": 0,
        "total_step_count": 0,
        "incremental_outputs": [],
        "warnings": ["HISTORICAL_ANALYSIS_PLAN_PAYLOAD_UNAVAILABLE"],
        "execution_outcome": outcome,
        "result_projection_pending": False,
    }


def _research_progress_response_kind(
    turn: dict[str, Any],
    decision: dict[str, Any] | None,
) -> str | None:
    if str(turn.get("status") or "") != ResearchTurnStatus.ANSWERED.value:
        return None
    action = str(turn.get("action_type") or "")
    if action == ResearchAction.QUERY_DATA.value:
        return "DATA_QUERY"
    if action == ResearchAction.ANSWER.value:
        reusable = (
            ((decision or {}).get("decision_json") or {}).get(
                "reusable_result_ref_keys"
            )
            or []
        )
        return "RESULT_REUSE" if reusable else "CONVERSATIONAL"
    return "CONVERSATIONAL"


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
                # Interpretation/provider failure must not hide an already
                # authoritative ScientificResult.  The result endpoint still
                # requires a persisted snapshot below, so this does not turn
                # a failed scientific execution into a false result.
                ResearchTurnStatus.FAILED.value,
            }:
                raise ScientificResultNotReady(str(turn_id))
            try:
                row = session.agent2.scientific_result_snapshots.get_latest_for_turn(turn_id)
            except ScientificResultSnapshotNotFound:
                # INTERPRET_RESULT creates a new conversational Turn but
                # intentionally does not duplicate the immutable scientific
                # snapshot. Resolve the explicitly reused snapshot through the
                # persisted context/decision relation instead of treating the
                # current Turn as if it owned a new Result.
                if str(turn.get("action_type") or "") != ResearchAction.INTERPRET_RESULT.value:
                    raise
                decision = session.agent2.research_turn_decisions.get_for_turn(turn_id)
                context = session.agent2.research_context_snapshots.get_for_turn(turn_id)
                requested = set(
                    str(item)
                    for item in ((decision or {}).get("decision_json") or {}).get("reusable_result_ref_keys") or []
                )
                candidates = (context or {}).get("referenced_result_refs_json") or []
                row = None
                for candidate in candidates:
                    if not isinstance(candidate, dict):
                        continue
                    if requested and str(candidate.get("candidate_key")) not in requested:
                        continue
                    snapshot_id = candidate.get("result_id")
                    if not snapshot_id:
                        continue
                    candidate_row = session.agent2.scientific_result_snapshots.get(UUID(str(snapshot_id)))
                    if str(candidate_row["project_id"]) != str(turn["project_id"]):
                        raise UnauthorizedScientificObjectReference("reused result is outside the project")
                    row = candidate_row
                    break
                if row is None:
                    raise ScientificResultNotReady(str(turn_id))
            bundle = ScientificResultBundle.model_validate(row["bundle_json"])
            # Artifacts remain authoritative in the existing Job/artifact
            # repository.  Expose only the bounded descriptors needed by the
            # presentation compiler; payload bytes stay behind the existing
            # artifact routes.
            artifacts = []
            if row.get("job_id"):
                artifacts = session.repositories.artifacts.list_for_job(str(row["job_id"]))[:64]
            snapshot = session.agent2.research_context_snapshots.get_for_turn(turn_id)
            if snapshot is None and str(bundle.research_turn_id) != str(turn_id):
                snapshot = session.agent2.research_context_snapshots.get_for_turn(bundle.research_turn_id)
            objects: dict[str, dict[str, Any]] = {}
            versions: dict[str, dict[str, Any]] = {}
            for ref in bundle.source_object_refs:
                try:
                    objects[str(ref.object_id)] = session.agent2.scientific_objects.get_object(ref.object_id)
                    versions[str(ref.version_id)] = session.agent2.scientific_objects.get_version(ref.version_id)
                except Exception:
                    pass
            relevance = ScientificResultRelevanceEvaluator().evaluate(bundle.source_object_refs, objects=objects, versions=versions)
            source_object_refs = []
            for item in bundle.source_object_refs:
                source = item.model_dump(mode="json")
                display_name = item.display_name or (
                    objects.get(str(item.object_id)) or {}
                ).get("display_name")
                version_no = (
                    versions.get(str(item.version_id)) or {}
                ).get("version_no")
                if display_name:
                    source["display_name"] = display_name
                if version_no is not None:
                    source["version_no"] = int(version_no)
                source_object_refs.append(source)
            return {
                # `result_id` is the immutable logical result identity carried
                # by the bundle.  Context/memory APIs address the persisted
                # ScientificResultSnapshot row, so expose that identity
                # explicitly instead of making clients guess or conflate the
                # two UUIDs.
                "result_id": str(bundle.result_id),
                "result_snapshot_id": str(row["id"]),
                "research_turn_id": str(bundle.research_turn_id),
                "research_question": bundle.research_question, "execution_status": bundle.execution_status.value,
                "relevance_status": relevance.value, "result_items": [item.model_dump(mode="json") for item in bundle.result_items],
                "source_object_refs": source_object_refs,
                "facts": [item.model_dump(mode="json") for item in bundle.facts],
                "figures": [item.model_dump(mode="json") for item in bundle.figures],
                "tables": [item.model_dump(mode="json") for item in bundle.tables],
                "evidence": [item.model_dump(mode="json") for item in bundle.evidence[:64]],
                "artifacts": artifacts,
                "limitations": [item.model_dump(mode="json") for item in bundle.limitations],
                "warnings": [item.model_dump(mode="json") for item in bundle.warnings],
                # A bounded immutable selection is interaction provenance, not a
                # second fact source. Presentation uses it only to prioritize
                # already-authoritative facts for the selected semantic subject.
                "scientific_selections": [] if snapshot is None else (snapshot["scientific_selections_json"] or []),
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
        service = ScientificResultProjectionService(
            factory,
            artifact_loader=lambda artifact: load_committed_json_artifact(
                storage, artifact
            ),
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
            return {
                "interpretation_id": str(row["id"]),
                "research_turn_id": str(turn_id),
                "status": row["grounding_status"],
                "title": (payload.get("interpretation") or {}).get("title"),
                "message": payload.get("message"),
                "execution_status": payload.get("execution_status"),
                # The full object is already validated and persisted by the
                # interpretation service.  Returning it here lets the
                # deterministic presentation compiler render claim-level
                # provenance without treating assistant text as authority.
                "interpretation": payload.get("interpretation"),
            }
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
        turn, events = get_research_turn_service().list_events(
            turn_id,
            _research_actor(current_user),
            after_sequence=after_sequence,
        )
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


def bulk_update_scientific_objects(
    project_id: str,
    request: ScientificObjectBulkLifecycleRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    service = get_scientific_object_service()
    try:
        _authorize_object_project(service, project_id, current_user, write=True)
        items = service.bulk_update_lifecycle(
            request.object_ids,
            project_id=project_id,
            lifecycle=request.lifecycle,
        )
        return jsonable_encoder(
            {
                "project_id": project_id,
                "lifecycle": request.lifecycle.value,
                "count": len(items),
                "items": items,
            }
        )
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


def get_scientific_object_dependency_impact(
    object_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    service = get_scientific_object_service()
    try:
        item = service.get_object(object_id)
        _authorize_object_project(service, str(item["project_id"]), current_user, write=True)
        return jsonable_encoder(service.dependency_impact(object_id))
    except Exception as exc:
        raise _http_error(exc) from exc


def admit_scientific_object(
    project_id: str,
    request: ScientificObjectAdmissionRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    service = get_scientific_object_service()
    try:
        _authorize_object_project(service, project_id, current_user, write=True)
        logical, version = service.admit_dataset_resource(
            project_id=project_id,
            dataset_id=request.dataset_id,
            resource_id=request.resource_id,
            storage=create_artifact_storage_from_settings(load_settings()),
            display_name=request.display_name,
            created_by_user_id=current_user.id,
        )
        return jsonable_encoder({"object": logical, "version": version})
    except Exception as exc:
        raise _http_error(exc) from exc


def update_scientific_object(
    object_id: UUID,
    request: ScientificObjectMetadataUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    service = get_scientific_object_service()
    try:
        item = service.get_object(object_id)
        _authorize_object_project(service, str(item["project_id"]), current_user, write=True)
        updated = service.update_metadata(
            object_id,
            display_name=request.display_name,
            archived=request.archived,
            lifecycle=request.lifecycle,
        )
        return jsonable_encoder(updated)
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


def create_scientific_object_version(
    object_id: UUID,
    request: ScientificObjectVersionCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    service = get_scientific_object_service()
    try:
        item = service.get_object(object_id)
        _authorize_object_project(service, str(item["project_id"]), current_user, write=True)
        version = service.create_version_from_dataset_resource(
            object_id,
            dataset_id=request.dataset_id,
            resource_id=request.resource_id,
            storage=create_artifact_storage_from_settings(load_settings()),
            created_by_user_id=current_user.id,
        )
        return jsonable_encoder(version)
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


def query_scientific_dataset(
    object_id: UUID,
    version_id: UUID,
    request: ScientificDatasetQueryRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    service = get_scientific_object_service()
    try:
        item = service.get_object(object_id)
        _authorize_object_project(service, str(item["project_id"]), current_user)
        return service.query_dataset_version(
            object_id,
            version_id,
            storage=create_artifact_storage_from_settings(load_settings()),
            request=request,
        )
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


def _authorize_object_project(
    service: ScientificObjectService,
    project_id: str,
    current_user: CurrentUser,
    *,
    write: bool = False,
) -> None:
    with service.repository_factory.session() as session:
        require_project_access(session.connection, project_id, current_user, write=write)


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
        "INTERPRETATION_RETRY_SCHEDULED": "assistant.retrying",
        "INTERPRETATION_READY": "assistant.message",
        "TURN_PARTIAL": "turn.partial",
    }.get(event_type, "turn.status.changed")


def _interpretation_retry_warning(
    turn: dict[str, Any],
    events: list[dict[str, Any]],
) -> dict[str, str] | None:
    """Project a simple user-facing retry state from durable turn events."""

    if str(turn.get("status")) != ResearchTurnStatus.INTERPRETING.value:
        return None
    latest_start = -1
    latest_retry: dict[str, Any] | None = None
    latest_retry_sequence = -1
    for event in events:
        sequence = int(event.get("sequence_no") or 0)
        event_type = str(event.get("event_type") or "")
        if event_type == ResearchTurnEventType.INTERPRETATION_STARTED.value:
            latest_start = max(latest_start, sequence)
        elif (
            event_type
            == ResearchTurnEventType.INTERPRETATION_RETRY_SCHEDULED.value
            and sequence > latest_retry_sequence
        ):
            latest_retry_sequence = sequence
            latest_retry = event
    if latest_retry is None or latest_retry_sequence < latest_start:
        return None
    return {
        "code": "INTERPRETATION_RETRYING",
        "message": (
            "解释服务暂时繁忙，正在按有界策略重试；"
            "已完成的科学结果仍然保留。"
        ),
    }


def _http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, ProjectAccessNotFound):
        return HTTPException(status_code=404, detail="项目不存在。")
    if isinstance(exc, ProjectAccessDenied):
        return HTTPException(status_code=403, detail="当前用户无权访问此项目。")
    if isinstance(
        exc,
        (
            ResearchTurnNotFound,
            ScientificObjectNotFound,
            ScientificObjectVersionNotFound,
            ScientificResultSnapshotNotFound,
            ResearchSessionProjectMismatch,
        ),
    ):
        return HTTPException(status_code=404, detail="请求的 Agent 2.0 资源不存在。")
    if isinstance(exc, UnauthorizedScientificObjectReference):
        return HTTPException(status_code=403, detail="科研对象引用不属于当前项目。")
    if isinstance(exc, (ConcurrentTurnModification, InvalidResearchTurnTransition)):
        code = "TURN_TERMINAL" if str(exc) == "TURN_TERMINAL" else "TURN_CONFLICT"
        return HTTPException(status_code=409, detail={"code": code, "summary": str(exc)})
    if isinstance(exc, ResearchTurnAdmissionConflict):
        return HTTPException(
            status_code=409,
            detail={"code": "RESEARCH_TURN_ADMISSION_CONFLICT", "summary": str(exc)},
        )
    if isinstance(exc, ResearchResourceLimitExceeded):
        return HTTPException(
            status_code=429,
            headers={"Retry-After": "5"},
            detail={
                "code": "PROJECT_ACTIVE_RESEARCH_LIMIT",
                "summary": str(exc),
                "limit": exc.limit,
                "active": exc.active,
            },
        )
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
