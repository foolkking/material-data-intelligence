from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import logging
import threading
from typing import Any, Iterator
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from mdi_api.application.research.ports import (
    ResearchActor,
    ResearchRepositoryFactoryPort,
)
from mdi_api.agent2_errors import (
    ConcurrentTurnModification,
    InvalidResearchTurnTransition,
    ResearchResourceLimitExceeded,
    ResearchSessionProjectMismatch,
    ResearchTurnAdmissionConflict,
    UnauthorizedScientificObjectReference,
)
from mdi_api.research_agent.schemas import (
    AutonomyMode,
    CreateResearchTurnRequest,
    CreateResearchTurnResponse,
    ResolvedResearchContext,
    ResearchTurnUIContext,
    ScientificSelectionContext,
    ResearchTurnEventType,
    ResearchTurnMessageDTO,
    ResearchTurnStatus,
    TERMINAL_TURN_STATUSES,
)
from mdi_api.research_agent.context.schemas import ContextManifest, ContextManifestItem
from mdi_api.research_agent.context.policy import ContextOperation, context_budget_policy
from mdi_api.research_agent.turns.state_machine import ensure_transition
from mdi_api.research_agent.memory.service import ResearchSessionMemoryService


logger = logging.getLogger(__name__)
_locks_guard = threading.Lock()
_session_locks: dict[str, threading.Lock] = {}
_turn_locks: dict[str, threading.Lock] = {}


@contextmanager
def _keyed_lock(registry: dict[str, threading.Lock], key: str) -> Iterator[None]:
    with _locks_guard:
        lock = registry.setdefault(key, threading.Lock())
    with lock:
        yield


_STATUS_EVENTS = {
    ResearchTurnStatus.RESOLVING_CONTEXT: ResearchTurnEventType.CONTEXT_RESOLUTION_STARTED,
    ResearchTurnStatus.ORCHESTRATING: ResearchTurnEventType.CONTEXT_RESOLVED,
    ResearchTurnStatus.NEEDS_CLARIFICATION: ResearchTurnEventType.CLARIFICATION_REQUESTED,
    ResearchTurnStatus.ANSWERED: ResearchTurnEventType.DIRECT_ANSWER_READY,
    ResearchTurnStatus.UNSUPPORTED: ResearchTurnEventType.TURN_UNSUPPORTED,
    ResearchTurnStatus.READY_TO_PLAN: ResearchTurnEventType.PLAN_REQUESTED,
    ResearchTurnStatus.PLANNING: ResearchTurnEventType.CAPABILITY_PLANNING_STARTED,
    ResearchTurnStatus.PLAN_READY: ResearchTurnEventType.PLAN_READY,
    ResearchTurnStatus.PLAN_REJECTED: ResearchTurnEventType.PLAN_REJECTED,
    ResearchTurnStatus.RUNNING: ResearchTurnEventType.JOB_STARTED,
    ResearchTurnStatus.INTERPRETING: ResearchTurnEventType.INTERPRETATION_STARTED,
    ResearchTurnStatus.COMPLETED: ResearchTurnEventType.TURN_COMPLETED,
    ResearchTurnStatus.PARTIAL: ResearchTurnEventType.TURN_PARTIAL,
    ResearchTurnStatus.FAILED: ResearchTurnEventType.TURN_FAILED,
    ResearchTurnStatus.CANCELED: ResearchTurnEventType.TURN_CANCELED,
}


class ResearchTurnService:
    def __init__(
        self,
        repository_factory: ResearchRepositoryFactoryPort,
        *,
        max_active_turns_per_project: int | None = None,
    ) -> None:
        self.repository_factory = repository_factory
        self.max_active_turns_per_project = max_active_turns_per_project

    def receive_turn(
        self,
        *,
        project_id: str,
        session_id: str,
        request: CreateResearchTurnRequest,
        current_user: ResearchActor,
    ) -> CreateResearchTurnResponse:
        """Persist one user message, one RECEIVED turn, and one event atomically."""

        with _keyed_lock(_session_locks, session_id):
            with self.repository_factory.unit_of_work() as unit:
                self.repository_factory.project_access.require(
                    unit.connection,
                    project_id,
                    current_user,
                    write=True,
                )
                session = unit.agent2.research_turns.lock_session(session_id)
                if session is None or str(session["project_id"]) != project_id:
                    raise ResearchSessionProjectMismatch(session_id)
                admission_fingerprint = self._admission_fingerprint(request)
                turn_id, message_id = self._admission_ids(
                    project_id=project_id,
                    session_id=session_id,
                    current_user_id=current_user.id,
                    admission_key=request.admission_key,
                )
                if request.admission_key:
                    existing = unit.agent2.research_turns.get_optional(turn_id)
                    if existing is not None:
                        existing_message = unit.agent2.research_turns.get_message(
                            str(existing["user_message_id"])
                        )
                        self._verify_admission_replay(
                            existing=existing,
                            existing_message=existing_message,
                            request=request,
                            admission_fingerprint=admission_fingerprint,
                            project_id=project_id,
                            session_id=session_id,
                        )
                        return self._turn_response(
                            turn=existing,
                            message=existing_message,
                            project_id=project_id,
                            session_id=session_id,
                            idempotent_replay=True,
                        )
                if str(session.get("status") or "active").lower() != "active":
                    raise InvalidResearchTurnTransition(
                        "Archived or trashed Research Sessions must be restored before new research."
                    )
                if self.max_active_turns_per_project is not None:
                    # Lock the Project row in this transaction before counting
                    # active Turns. Concurrent sessions therefore cannot both
                    # pass the limit check and over-admit work.
                    unit.agent2.research_turns.lock_project_for_turn_admission(project_id)
                    active_turns = unit.agent2.research_turns.count_active_for_project(project_id)
                    if active_turns >= self.max_active_turns_per_project:
                        raise ResearchResourceLimitExceeded(
                            "当前项目已有过多进行中的研究。请等待现有研究完成或先停止不再需要的任务。",
                            limit=self.max_active_turns_per_project,
                            active=active_turns,
                        )
                parent_turn_id = request.reply_to_turn_id
                if parent_turn_id is not None:
                    parent = unit.agent2.research_turns.get(parent_turn_id)
                    if parent["project_id"] != project_id or parent["research_session_id"] != session_id:
                        raise ResearchSessionProjectMismatch("reply_to_turn_id is outside the Research Session")
                    if parent["status"] not in {status.value for status in TERMINAL_TURN_STATUSES}:
                        raise InvalidResearchTurnTransition(
                            "reply_to_turn_id must reference a terminal ResearchTurn"
                        )
                self._authorize_ui_context(unit, project_id, request)
                now = datetime.now(timezone.utc)
                ui_context = request.ui_context.model_dump(mode="json") if request.ui_context else None
                autonomy = self._root_autonomy_payload(
                    mode=request.autonomy_mode,
                    root_turn_id=turn_id,
                )
                message = unit.agent2.research_turns.add_message({
                    "id": message_id,
                    "session_id": session_id,
                    "role": "user",
                    "content_summary": request.message,
                    "payload_json": {
                        "source": "agent2_research_turn",
                        "uiContext": ui_context,
                        "replyToTurnId": str(parent_turn_id) if parent_turn_id else None,
                        "autonomy": autonomy,
                        "_mdi_admission": {
                            "key_hash": (
                                hashlib.sha256(request.admission_key.encode("utf-8")).hexdigest()
                                if request.admission_key
                                else None
                            ),
                            "fingerprint": admission_fingerprint,
                        },
                    },
                    "created_at": now,
                })
                # Session-level memory is updated in the same transaction as
                # the user message, so context snapshots can only observe
                # committed, auditable state. Turn-only parameters remain in
                # the request/context snapshot and are not persisted here.
                ResearchSessionMemoryService().apply_user_message(
                    unit, session_id=session_id, project_id=project_id,
                    message=request.message, message_id=message_id,
                )
                turn = unit.agent2.research_turns.add({
                    "id": turn_id,
                    "project_id": project_id,
                    "research_session_id": session_id,
                    "sequence_no": unit.agent2.research_turns.allocate_sequence(session_id),
                    "parent_turn_id": parent_turn_id,
                    "continuation_of_turn_id": None,
                    "user_message_id": message_id,
                    "action_type": None,
                    "status": ResearchTurnStatus.RECEIVED.value,
                    "row_version": 1,
                    "created_at": now,
                    "updated_at": now,
                })
                self._append_event(
                    unit,
                    turn_id,
                    ResearchTurnEventType.TURN_RECEIVED,
                    {
                        "status": ResearchTurnStatus.RECEIVED.value,
                        "ui_context": ui_context,
                        "autonomy": autonomy,
                    },
                    created_at=now,
                )
                if request.autonomy_mode == AutonomyMode.BOUNDED_AUTONOMOUS:
                    self._append_event(
                        unit,
                        turn_id,
                        ResearchTurnEventType.AUTONOMY_CYCLE_CREATED,
                        autonomy,
                        created_at=now,
                    )
        self._log_lifecycle(turn, ResearchTurnEventType.TURN_RECEIVED)
        return self._turn_response(
            turn=turn,
            message=message,
            project_id=project_id,
            session_id=session_id,
        )

    @staticmethod
    def _admission_fingerprint(request: CreateResearchTurnRequest) -> str:
        payload = {
            "message": request.message,
            "ui_context": (
                request.ui_context.model_dump(mode="json")
                if request.ui_context is not None
                else None
            ),
            "reply_to_turn_id": (
                str(request.reply_to_turn_id) if request.reply_to_turn_id else None
            ),
            "autonomy_mode": request.autonomy_mode.value,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _admission_ids(
        *,
        project_id: str,
        session_id: str,
        current_user_id: str,
        admission_key: str | None,
    ) -> tuple[UUID, str]:
        if not admission_key:
            turn_id = uuid4()
            return turn_id, f"message_{uuid4().hex}"
        scope = f"{current_user_id}:{project_id}:{session_id}:{admission_key}"
        turn_id = uuid5(NAMESPACE_URL, f"mdi:research-turn-admission:{scope}")
        message_digest = hashlib.sha256(
            f"mdi:research-message-admission:{scope}".encode("utf-8")
        ).hexdigest()
        return turn_id, f"message_{message_digest[:56]}"

    @staticmethod
    def _verify_admission_replay(
        *,
        existing: dict[str, Any],
        existing_message: dict[str, Any],
        request: CreateResearchTurnRequest,
        admission_fingerprint: str,
        project_id: str,
        session_id: str,
    ) -> None:
        if (
            str(existing["project_id"]) != project_id
            or str(existing["research_session_id"]) != session_id
        ):
            raise ResearchTurnAdmissionConflict(
                "admission_key is already bound to another Research Session"
            )
        payload = existing_message.get("payload_json") or {}
        stored = payload.get("_mdi_admission") if isinstance(payload, dict) else None
        if (
            not isinstance(stored, dict)
            or stored.get("fingerprint") != admission_fingerprint
            or str(existing_message.get("content_summary") or "") != request.message
        ):
            raise ResearchTurnAdmissionConflict(
                "admission_key was already used for a different Research request"
            )

    @staticmethod
    def _turn_response(
        *,
        turn: dict[str, Any],
        message: dict[str, Any],
        project_id: str,
        session_id: str,
        idempotent_replay: bool = False,
    ) -> CreateResearchTurnResponse:
        return CreateResearchTurnResponse(
            turn_id=turn["id"],
            research_session_id=session_id,
            project_id=project_id,
            sequence_no=int(turn["sequence_no"]),
            status=ResearchTurnStatus(str(turn["status"])),
            user_message=ResearchTurnMessageDTO(
                id=str(message["id"]),
                role="USER",
                content=str(message["content_summary"]),
            ),
            created_at=turn["created_at"],
            idempotent_replay=idempotent_replay,
        )

    def receive_autonomous_turn(
        self,
        *,
        project_id: str,
        session_id: str,
        parent_turn_id: UUID,
        message: str,
        ui_context: ResearchTurnUIContext,
        autonomy: dict[str, Any],
    ) -> CreateResearchTurnResponse:
        """Create one durable internal continuation without mutating user memory.

        The parent Turn is the authorization and lineage authority. The
        generated message is deliberately marked as an autonomous subgoal and
        never passed through the user-memory writer.
        """

        assessment_signature = str(autonomy.get("assessment_signature") or "")
        if not assessment_signature:
            raise ValueError("autonomous turn requires assessment_signature")
        with _keyed_lock(_session_locks, session_id):
            with self.repository_factory.unit_of_work() as unit:
                session = unit.agent2.research_turns.lock_session(session_id)
                if session is None or str(session["project_id"]) != project_id:
                    raise ResearchSessionProjectMismatch(session_id)
                parent = unit.agent2.research_turns.get_for_update(parent_turn_id)
                if (
                    str(parent["project_id"]) != project_id
                    or str(parent["research_session_id"]) != session_id
                ):
                    raise ResearchSessionProjectMismatch(
                        "autonomy parent is outside the Research Session"
                    )
                if parent["status"] not in {
                    status.value for status in TERMINAL_TURN_STATUSES
                }:
                    raise InvalidResearchTurnTransition(
                        "autonomy parent must be terminal"
                    )
                for event in unit.agent2.research_turn_events.list_for_turn(
                    parent_turn_id
                ):
                    payload = event.get("payload_json") or {}
                    if (
                        event["event_type"]
                        == ResearchTurnEventType.AUTONOMY_CHILD_TURN_CREATED.value
                        and payload.get("assessment_signature")
                        == assessment_signature
                        and payload.get("child_turn_id")
                    ):
                        existing = unit.agent2.research_turns.get(
                            UUID(str(payload["child_turn_id"]))
                        )
                        existing_message = unit.agent2.research_turns.get_message(
                            str(existing["user_message_id"])
                        )
                        return CreateResearchTurnResponse(
                            turn_id=existing["id"],
                            research_session_id=session_id,
                            project_id=project_id,
                            sequence_no=int(existing["sequence_no"]),
                            status=ResearchTurnStatus(str(existing["status"])),
                            user_message=ResearchTurnMessageDTO(
                                id=str(existing["user_message_id"]),
                                role="USER",
                                content=str(existing_message["content_summary"]),
                            ),
                            created_at=existing["created_at"],
                        )
                self._authorize_context_refs(
                    unit,
                    project_id,
                    [
                        *ui_context.active_object_refs,
                        *ui_context.selection_refs,
                        *(item.object_ref for item in ui_context.scientific_selections),
                        *ui_context.explicit_object_refs,
                    ],
                )
                for result_id in ui_context.explicit_result_ids:
                    result = unit.agent2.scientific_result_snapshots.get(result_id)
                    source_turn = unit.agent2.research_turns.get(
                        result["research_turn_id"]
                    )
                    if (
                        str(result["project_id"]) != project_id
                        or str(source_turn["research_session_id"]) != session_id
                    ):
                        raise UnauthorizedScientificObjectReference(
                            "autonomous Result is outside the Research Session"
                        )
                now = datetime.now(timezone.utc)
                child_turn_id = uuid4()
                message_id = f"message_{uuid4().hex}"
                ui_payload = ui_context.model_dump(mode="json")
                generated_message = unit.agent2.research_turns.add_message(
                    {
                        "id": message_id,
                        "session_id": session_id,
                        "role": "user",
                        "content_summary": message.strip()[:16_000],
                        "payload_json": {
                            "source": "agent2_bounded_autonomy",
                            "generatedByAutonomy": True,
                            "uiContext": ui_payload,
                            "replyToTurnId": str(parent_turn_id),
                            "autonomy": autonomy,
                        },
                        "created_at": now,
                    }
                )
                turn = unit.agent2.research_turns.add(
                    {
                        "id": child_turn_id,
                        "project_id": project_id,
                        "research_session_id": session_id,
                        "sequence_no": unit.agent2.research_turns.allocate_sequence(
                            session_id
                        ),
                        "parent_turn_id": parent_turn_id,
                        "continuation_of_turn_id": parent_turn_id,
                        "user_message_id": message_id,
                        "action_type": None,
                        "status": ResearchTurnStatus.RECEIVED.value,
                        "row_version": 1,
                        "created_at": now,
                        "updated_at": now,
                    }
                )
                received_payload = {
                    "status": ResearchTurnStatus.RECEIVED.value,
                    "ui_context": ui_payload,
                    "autonomy": autonomy,
                }
                self._append_event(
                    unit,
                    child_turn_id,
                    ResearchTurnEventType.TURN_RECEIVED,
                    received_payload,
                    created_at=now,
                )
                self._append_event(
                    unit,
                    child_turn_id,
                    ResearchTurnEventType.AUTONOMY_CYCLE_CREATED,
                    autonomy,
                    created_at=now,
                )
                self._append_event(
                    unit,
                    parent_turn_id,
                    ResearchTurnEventType.AUTONOMY_CHILD_TURN_CREATED,
                    {
                        "child_turn_id": str(child_turn_id),
                        "cycle_index": autonomy.get("cycle_index"),
                        "assessment_signature": assessment_signature,
                    },
                    created_at=now,
                )
        self._log_lifecycle(turn, ResearchTurnEventType.AUTONOMY_CYCLE_CREATED)
        return CreateResearchTurnResponse(
            turn_id=child_turn_id,
            research_session_id=session_id,
            project_id=project_id,
            sequence_no=int(turn["sequence_no"]),
            status=ResearchTurnStatus.RECEIVED,
            user_message=ResearchTurnMessageDTO(
                id=message_id,
                role="USER",
                content=str(generated_message["content_summary"]),
            ),
            created_at=turn["created_at"],
        )

    def get_turn(self, turn_id: UUID, current_user: ResearchActor) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            self.repository_factory.project_access.require(
                session.connection,
                str(turn["project_id"]),
                current_user,
            )
            return self._turn_view(session, turn)

    def list_session_turns(
        self,
        *,
        project_id: str,
        session_id: str,
        current_user: ResearchActor,
        cursor: int | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        with self.repository_factory.session() as session:
            self.repository_factory.project_access.require(
                session.connection,
                project_id,
                current_user,
            )
            research_session = session.agent2.research_turns.lock_session(session_id)
            if research_session is None or str(research_session["project_id"]) != project_id:
                raise ResearchSessionProjectMismatch(session_id)
            return [self._turn_view(session, row) for row in session.agent2.research_turns.list_for_session(session_id, cursor=cursor, limit=limit)]

    def transition(
        self,
        *,
        turn_id: UUID,
        expected_status: ResearchTurnStatus,
        expected_version: int,
        target_status: ResearchTurnStatus,
        error_code: str | None = None,
        error_summary: str | None = None,
    ) -> dict[str, Any]:
        with _keyed_lock(_turn_locks, str(turn_id)):
            with self.repository_factory.unit_of_work() as unit:
                current = unit.agent2.research_turns.get_for_update(turn_id)
                if current["status"] != expected_status.value or int(current["row_version"]) != expected_version:
                    raise ConcurrentTurnModification(str(turn_id))
                ensure_transition(expected_status, target_status)
                completed_at = datetime.now(timezone.utc) if target_status in TERMINAL_TURN_STATUSES else None
                updated = unit.agent2.research_turns.compare_and_set_status(
                    turn_id,
                    expected_status=expected_status.value,
                    expected_version=expected_version,
                    target_status=target_status.value,
                    completed_at=completed_at,
                    error_code=error_code,
                    error_summary=error_summary,
                )
                event_type = _STATUS_EVENTS.get(target_status)
                if event_type:
                    self._append_event(unit, turn_id, event_type, {"status": target_status.value})
        if event_type:
            self._log_lifecycle(updated, event_type, previous_status=expected_status)
        return updated

    def fail_if_active(
        self,
        turn_id: UUID,
        code: str,
        summary: str,
    ) -> dict[str, Any] | None:
        """Terminalize an active turn after a worker-boundary failure.

        Queue workers resolve the dotted callable lazily.  Therefore an
        import/configuration failure can happen before ``AgentTurnProcessor``
        exists and before its normal exception handling is available.  This
        small lifecycle operation reuses the authoritative turn state machine
        and compare-and-set write so those failures cannot leave a durable
        RECEIVED/active turn behind a failed RQ job.
        """

        with _keyed_lock(_turn_locks, str(turn_id)):
            with self.repository_factory.unit_of_work() as unit:
                turn = unit.agent2.research_turns.get_for_update(turn_id)
                status = ResearchTurnStatus(str(turn["status"]))
                if status in TERMINAL_TURN_STATUSES:
                    return None
                if status not in {
                    ResearchTurnStatus.RECEIVED,
                    ResearchTurnStatus.RESOLVING_CONTEXT,
                    ResearchTurnStatus.ORCHESTRATING,
                    ResearchTurnStatus.READY_TO_PLAN,
                    ResearchTurnStatus.PLANNING,
                    ResearchTurnStatus.PLAN_READY,
                    ResearchTurnStatus.QUEUED,
                    ResearchTurnStatus.RUNNING,
                    ResearchTurnStatus.CANCELING,
                    ResearchTurnStatus.RESULT_PENDING,
                    ResearchTurnStatus.RESULT_READY,
                    ResearchTurnStatus.INTERPRETING,
                }:
                    return None
                ensure_transition(status, ResearchTurnStatus.FAILED)
                updated = unit.agent2.research_turns.compare_and_set_status(
                    turn_id,
                    expected_status=status.value,
                    expected_version=int(turn["row_version"]),
                    target_status=ResearchTurnStatus.FAILED.value,
                    completed_at=datetime.now(timezone.utc),
                    error_code=code,
                    error_summary=str(summary)[:1000],
                )
                self._append_event(unit, turn_id, ResearchTurnEventType.TURN_FAILED, {
                    "status": updated["status"],
                    "error_code": code,
                })
        self._log_lifecycle(updated, ResearchTurnEventType.TURN_FAILED, previous_status=status)
        return updated

    def create_context_snapshot(self, turn_id: UUID, context: ResolvedResearchContext) -> dict[str, Any]:
        with _keyed_lock(_turn_locks, str(turn_id)):
            with self.repository_factory.unit_of_work() as unit:
                turn = unit.agent2.research_turns.get_for_update(turn_id)
                if turn["status"] != ResearchTurnStatus.RESOLVING_CONTEXT.value:
                    raise InvalidResearchTurnTransition("context snapshot requires RESOLVING_CONTEXT")
                if turn["project_id"] != context.project_id or turn["research_session_id"] != context.research_session_id:
                    raise ResearchSessionProjectMismatch("context scope does not match ResearchTurn")
                resolved_refs = [
                    item.selected_ref
                    for item in context.resolved_references
                    if item.selected_ref is not None
                ]
                self._authorize_context_refs(
                    unit,
                    context.project_id,
                    [
                        *context.active_objects,
                        *context.selection_refs,
                        *(item.object_ref for item in context.scientific_selections),
                        *resolved_refs,
                    ],
                )
                payload = context.model_dump(mode="json")
                fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
                snapshot_id = uuid4()
                snapshot = unit.agent2.research_context_snapshots.add({
                    "id": snapshot_id,
                    "project_id": context.project_id,
                    "research_session_id": context.research_session_id,
                    "research_turn_id": turn_id,
                    "snapshot_schema_version": "1.1",
                    "active_scope_refs_json": payload["active_objects"],
                    "selection_refs_json": payload["selection_refs"],
                    "scientific_selections_json": payload["scientific_selections"],
                    "resolved_references_json": payload["resolved_references"],
                    "referenced_result_refs_json": payload["referenced_result_ids"],
                    "relevant_finding_refs_json": [],
                    "effective_constraints_json": payload["user_constraints"],
                    "research_goal": context.research_goal,
                    "unresolved_questions_json": context.unresolved_questions,
                    "context_fingerprint": fingerprint,
                    "compiler_version": "agent2.explicit-ui-context/1.0",
                })
                manifest = self._build_context_manifest(
                    turn_id=turn_id,
                    context=context,
                    context_fingerprint=fingerprint,
                )
                updated = unit.agent2.research_turns.attach_context_snapshot(turn_id, snapshot_id)
                updated = unit.agent2.research_turns.compare_and_set_status(
                    turn_id,
                    expected_status=ResearchTurnStatus.RESOLVING_CONTEXT.value,
                    expected_version=int(updated["row_version"]),
                    target_status=ResearchTurnStatus.ORCHESTRATING.value,
                )
                self._append_event(
                    unit,
                    turn_id,
                    ResearchTurnEventType.CONTEXT_RESOLVED,
                    {
                        "status": ResearchTurnStatus.ORCHESTRATING.value,
                        "context_snapshot_id": str(snapshot_id),
                        "context_manifest": manifest.model_dump(mode="json"),
                    },
                )
        self._log_lifecycle(updated, ResearchTurnEventType.CONTEXT_RESOLVED, previous_status=ResearchTurnStatus.RESOLVING_CONTEXT)
        return snapshot

    @staticmethod
    def _build_context_manifest(
        *,
        turn_id: UUID,
        context: ResolvedResearchContext,
        context_fingerprint: str,
        serialized_input: dict[str, Any] | None = None,
        input_state: str = "PROSPECTIVE",
        invocation_role: str | None = None,
        prompt_template_version: str | None = None,
        serialized_input_version: str | None = None,
    ) -> ContextManifest:
        """Create a bounded immutable manifest for the resolved turn context."""

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
            superseded_state: str = "NONE",
            source_class: str = "UNKNOWN",
            freshness: str = "CURRENT",
            epistemic_status: str = "OBSERVED",
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
                    representation_type="BOUNDED_JSON",
                    representation_version="1.0",
                    serialized_representation=content,
                    lineage_refs=[source_identity],
                    estimated_tokens=max(1, len(encoded.encode("utf-8")) // 4),
                    source_class=source_class,
                    freshness=freshness,
                    epistemic_status=epistemic_status,
                    superseded_state=superseded_state,
                )
            )

        for index, ref in enumerate(context.active_objects, start=1):
            add_item(
                item_id=f"object_{index}",
                kind="SCIENTIFIC_OBJECT",
                authority_class="SCIENTIFIC_DATA",
                source_identity=f"{ref.object_id}:{ref.version_id}",
                opaque_ref=f"object_{index}",
                content=ref.model_dump(mode="json"),
                inclusion_reason="active scientific scope",
                selection_mode="CURRENT",
                object_id=str(ref.object_id),
                version_id=str(ref.version_id),
                source_class="EXACT_SCIENTIFIC_OBJECT_VERSION",
                freshness="CURRENT",
                epistemic_status="OBSERVED",
            )
        for index, ref in enumerate(context.selection_refs, start=1):
            add_item(
                item_id=f"selection_{index}",
                kind="SCIENTIFIC_SELECTION",
                authority_class="SCIENTIFIC_DATA",
                source_identity=f"{ref.object_id}:{ref.version_id}",
                opaque_ref=f"selection_{index}",
                content=ref.model_dump(mode="json"),
                inclusion_reason="explicit UI scientific selection",
                selection_mode="UI_SELECTION",
                object_id=str(ref.object_id),
                version_id=str(ref.version_id),
                source_class="EXPLICIT_UI_SELECTION",
                freshness="CURRENT",
                epistemic_status="OBSERVED",
            )
        for index, selection in enumerate(context.scientific_selections, start=1):
            ref = selection.object_ref
            add_item(
                item_id=f"scientific_selection_{index}",
                kind="SCIENTIFIC_SELECTION",
                authority_class="SCIENTIFIC_DATA",
                source_identity=f"{ref.object_id}:{ref.version_id}",
                opaque_ref=f"scientific_selection_{index}",
                content=selection.model_dump(mode="json"),
                inclusion_reason="semantic UI selection",
                selection_mode="EXPLICIT",
                object_id=str(ref.object_id),
                version_id=str(ref.version_id),
                source_class="EXPLICIT_UI_SELECTION",
                freshness="CURRENT",
                epistemic_status="OBSERVED",
            )
        for index, result_id in enumerate(context.referenced_result_ids, start=1):
            add_item(
                item_id=f"result_{index}",
                kind="SCIENTIFIC_RESULT",
                authority_class="SCIENTIFIC_RESULT",
                source_identity=str(result_id),
                opaque_ref=f"result_{index}",
                content={"result_id": str(result_id)},
                inclusion_reason="explicit referenced prior Result",
                selection_mode="CONTINUATION",
                result_ref=str(result_id),
                source_class="SCIENTIFIC_RESULT",
                freshness="HISTORICAL_VALID",
                epistemic_status="COMPUTED",
            )
        for index, constraint in enumerate(context.user_constraints, start=1):
            add_item(
                item_id=f"constraint_{index}",
                kind="USER_CONSTRAINT",
                authority_class="USER_CONSTRAINT",
                source_identity=f"{context.research_session_id}:constraint:{index}",
                opaque_ref=f"constraint_{index}",
                content=constraint,
                inclusion_reason="session/user constraint",
                selection_mode="EXPLICIT",
                source_class="CURRENT_USER_REQUEST",
                freshness="CURRENT",
                epistemic_status="CONSTRAINT",
            )
        if context.research_goal:
            add_item(
                item_id="goal_1",
                kind="RESEARCH_GOAL",
                authority_class="CONVERSATIONAL_NARRATIVE",
                source_identity=f"{context.research_session_id}:goal",
                opaque_ref="goal_1",
                content=context.research_goal,
                inclusion_reason="active research goal",
                selection_mode="CURRENT",
                source_class="CURRENT_USER_REQUEST",
                freshness="CURRENT",
                epistemic_status="CONSTRAINT",
            )

        budget_policy = context_budget_policy(ContextOperation.ORCHESTRATOR)
        budget = budget_policy.effective_input_budget
        priority = {
            "SCIENTIFIC_OBJECT": 0,
            "SCIENTIFIC_SELECTION": 0,
            "SCIENTIFIC_RESULT": 1,
            "USER_CONSTRAINT": 2,
            "RESEARCH_GOAL": 3,
        }
        ordered = sorted(enumerate(items), key=lambda pair: (priority[pair[1].kind], pair[0]))
        included: list[ContextManifestItem] = []
        excluded: list[str] = []
        estimated = 0
        for index, item in ordered:
            critical = item.kind in {"SCIENTIFIC_OBJECT", "SCIENTIFIC_SELECTION", "SCIENTIFIC_RESULT"}
            if estimated + item.estimated_tokens <= budget:
                included.append(item)
                estimated += item.estimated_tokens
            elif critical:
                raise ValueError("critical scientific context exceeds the operation budget")
            else:
                excluded.append(item.item_id)
        over_budget = bool(excluded)
        serialized_input_fingerprint = None
        serialized_input_tokens = None
        if serialized_input is not None:
            serialized = json.dumps(
                serialized_input,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            )
            serialized_input_fingerprint = hashlib.sha256(
                serialized.encode("utf-8")
            ).hexdigest()
            serialized_input_tokens = max(
                1, len(serialized.encode("utf-8")) // 4
            )
            if serialized_input_tokens > budget:
                raise ValueError(
                    "actual ORCHESTRATOR serialized input exceeds the operation budget"
                )
        return ContextManifest(
            context_manifest_id=uuid4(),
            operation="ORCHESTRATOR",
            project_id=context.project_id,
            research_session_id=context.research_session_id,
            research_turn_id=turn_id,
            policy_version="agent2.context-policy/2.0",
            input_state=input_state,
            invocation_role=invocation_role,
            prompt_template_version=prompt_template_version,
            serialized_input_version=serialized_input_version,
            serialized_input=serialized_input,
            serialized_input_fingerprint=serialized_input_fingerprint,
            included_items=included,
            excluded_items=excluded,
            excluded_item_details=[
                {
                    "item_id": item_id,
                    "reason": "BUDGET",
                    "detail": (
                        "The bounded operation budget could not include this "
                        "non-critical item."
                    ),
                }
                for item_id in excluded
            ],
            estimated_input_tokens=(
                serialized_input_tokens
                if serialized_input_tokens is not None
                else estimated
            ),
            input_budget=budget_policy.effective_input_budget,
            reserved_output_tokens=budget_policy.reserved_output_tokens,
            repair_margin=budget_policy.repair_margin,
            compaction_state="COMPACTED" if over_budget else "NONE",
            truncation_state="NONE",
            context_fingerprint=context_fingerprint,
            created_at=datetime.now(timezone.utc),
        )

    def resolve_turn_context_stub(self, turn_id: UUID) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            events = session.agent2.research_turn_events.list_for_turn(turn_id)
        received = next((event for event in events if event["event_type"] == ResearchTurnEventType.TURN_RECEIVED.value), None)
        ui_context = (received or {}).get("payload_json", {}).get("ui_context") or {}
        active = ui_context.get("active_object_refs") or []
        selected = ui_context.get("selection_refs") or []
        # Normalize the persisted event payload at the worker boundary. This
        # keeps semantic selections intact across a fresh process and prevents
        # an untyped JSON list from being silently reduced to the default []
        # when the immutable snapshot is assembled.
        scientific_selections = [
            ScientificSelectionContext.model_validate(item).model_dump(mode="json")
            for item in (ui_context.get("scientific_selections") or [])
        ]
        memory_state = None
        with self.repository_factory.session() as memory_session:
            memory_state = memory_session.agent2.research_session_memory.get_state(str(turn["research_session_id"]))
        resolving = self.transition(
            turn_id=turn_id,
            expected_status=ResearchTurnStatus.RECEIVED,
            expected_version=int(turn["row_version"]),
            target_status=ResearchTurnStatus.RESOLVING_CONTEXT,
        )
        context = ResolvedResearchContext(
            project_id=str(turn["project_id"]),
            research_session_id=str(turn["research_session_id"]),
            active_objects=active,
            selection_refs=selected,
            scientific_selections=scientific_selections,
            resolved_references=[],
            referenced_result_ids=[],
            research_goal=(memory_state or {}).get("active_research_goal"),
            user_constraints=list((memory_state or {}).get("session_constraints_json") or []),
            unresolved_questions=[],
            requires_clarification=False,
        )
        snapshot = self.create_context_snapshot(turn_id, context)
        return {"turn_id": turn_id, "from_version": resolving["row_version"], "snapshot": snapshot, "status": ResearchTurnStatus.ORCHESTRATING.value}

    def cancel_turn(self, turn_id: UUID, current_user: ResearchActor) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            self.repository_factory.project_access.require(
                session.connection,
                str(turn["project_id"]),
                current_user,
                write=True,
            )
        status = ResearchTurnStatus(str(turn["status"]))
        if status in TERMINAL_TURN_STATUSES or status == ResearchTurnStatus.RESULT_PENDING:
            raise InvalidResearchTurnTransition("TURN_TERMINAL")
        if turn.get("job_id"):
            from mdi_api.research_agent.execution.supervisor import ResearchExecutionSupervisor
            return ResearchExecutionSupervisor(self.repository_factory).request_cancel(turn_id)
        return self.transition(
            turn_id=turn_id,
            expected_status=status,
            expected_version=int(turn["row_version"]),
            target_status=ResearchTurnStatus.CANCELED,
        )

    def list_events(self, turn_id: UUID, current_user: ResearchActor, *, after_sequence: int = 0) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            self.repository_factory.project_access.require(
                session.connection,
                str(turn["project_id"]),
                current_user,
            )
            return turn, session.agent2.research_turn_events.list_for_turn(turn_id, after_sequence=after_sequence)

    @staticmethod
    def _append_event(unit: Any, turn_id: UUID, event_type: ResearchTurnEventType, payload: dict[str, Any], *, created_at: datetime | None = None) -> dict[str, Any]:
        return unit.agent2.research_turn_events.append_turn_event({
            "id": uuid4(),
            "turn_id": turn_id,
            "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
            "event_type": event_type.value,
            "payload_json": payload,
            "created_at": created_at or datetime.now(timezone.utc),
        })

    @staticmethod
    def _authorize_ui_context(unit: Any, project_id: str, request: CreateResearchTurnRequest) -> None:
        if request.ui_context:
            ResearchTurnService._authorize_context_refs(
                unit,
                project_id,
                [
                    *request.ui_context.active_object_refs,
                    *request.ui_context.selection_refs,
                    *(item.object_ref for item in request.ui_context.scientific_selections),
                    # Explicit object refs are accepted only after the same
                    # project/version authorization as UI selection.
                    *request.ui_context.explicit_object_refs,
                ],
            )

    @staticmethod
    def _root_autonomy_payload(
        *, mode: AutonomyMode, root_turn_id: UUID
    ) -> dict[str, Any]:
        if mode == AutonomyMode.STANDARD:
            return {"mode": mode.value}
        from mdi_api.research_agent.autonomy.policy import DEFAULT_AUTONOMY_POLICY

        return {
            "mode": mode.value,
            "root_turn_id": str(root_turn_id),
            "cycle_index": 1,
            "policy": DEFAULT_AUTONOMY_POLICY.model_dump(
                mode="json", exclude={"fingerprint"}
            ),
            "policy_version": DEFAULT_AUTONOMY_POLICY.version,
            "policy_fingerprint": DEFAULT_AUTONOMY_POLICY.fingerprint,
        }

    @staticmethod
    def _authorize_context_refs(unit: Any, project_id: str, refs: list[Any]) -> None:
        for ref in refs:
            logical = unit.agent2.scientific_objects.get_object(ref.object_id)
            version = unit.agent2.scientific_objects.get_version(ref.version_id)
            if (
                str(logical["project_id"]) != project_id
                or ref.project_id != project_id
                or version["scientific_object_id"] != logical["id"]
                or str(logical["object_type"]) != ref.object_type
                or str(version["object_type"]) != ref.object_type
            ):
                raise UnauthorizedScientificObjectReference("ScientificObjectRef failed server-side project/version authorization")

    @staticmethod
    def _turn_view(session: Any, turn: dict[str, Any]) -> dict[str, Any]:
        message_rows = session.agent2.research_turns.referenced_messages(turn)
        messages_view = [{
            "id": row["id"],
            "role": "ASSISTANT" if row["role"] == "agent" else str(row["role"]).upper(),
            "content": row["content_summary"],
            "created_at": row["created_at"],
        } for row in message_rows]
        snapshot = session.agent2.research_context_snapshots.get_for_turn(turn["id"])
        decision = session.agent2.research_turn_decisions.get_for_turn(turn["id"])
        capability_resolution = session.agent2.research_capability_resolutions.get_for_turn(turn["id"])
        capability_plan = session.agent2.research_capability_plans.get_for_turn(turn["id"])
        execution_summary = session.agent2.research_execution_summaries.get_for_turn(turn["id"])
        interpretation = session.agent2.interpretations.get_for_turn(turn["id"])
        summary = None if snapshot is None else {
            "id": snapshot["id"],
            "schema_version": snapshot["snapshot_schema_version"],
            "active_object_count": len(snapshot["active_scope_refs_json"] or []),
            "selection_count": len(snapshot["selection_refs_json"] or []),
            "requires_clarification": bool(snapshot["unresolved_questions_json"]),
            "context_fingerprint": snapshot["context_fingerprint"],
        }
        return {
            "id": turn["id"],
            "project_id": turn["project_id"],
            "research_session_id": turn["research_session_id"],
            "sequence_no": turn["sequence_no"],
            "parent_turn_id": (
                str(turn["parent_turn_id"]) if turn.get("parent_turn_id") else None
            ),
            "action": turn["action_type"],
            "status": turn["status"],
            "messages": messages_view,
            "context_snapshot_summary": summary,
            "context": None if snapshot is None else {
                "scope": snapshot["active_scope_refs_json"] or [],
                "selection": snapshot["selection_refs_json"] or [],
                "scientific_selection": snapshot["scientific_selections_json"] or [],
            },
            "orchestration": {
                "decision_available": decision is not None,
                "action_dispatch_status": None if decision is None else decision["action_dispatch_status"],
            },
            "planning": {
                "status": turn["status"],
                "plan_available": turn["status"] in {
                    ResearchTurnStatus.PLAN_READY.value,
                    ResearchTurnStatus.QUEUED.value,
                    ResearchTurnStatus.RUNNING.value,
                    ResearchTurnStatus.CANCELING.value,
                    ResearchTurnStatus.RESULT_PENDING.value,
                    ResearchTurnStatus.RESULT_READY.value,
                    ResearchTurnStatus.INTERPRETING.value,
                    ResearchTurnStatus.COMPLETED.value,
                    ResearchTurnStatus.PARTIAL.value,
                } and turn.get("analysis_plan_id") is not None,
                "resolution_available": capability_resolution is not None,
                "capability_plan_available": capability_plan is not None,
            },
            "execution": {
                "job_attached": turn.get("job_id") is not None,
                "progress_available": turn.get("job_id") is not None,
                "outcome": None if execution_summary is None else execution_summary.get("execution_outcome"),
            },
            "result_available": session.agent2.scientific_result_snapshots.exists_for_turn(turn["id"]),
            "interpretation": {
                "available": interpretation is not None,
                "grounding_status": None if interpretation is None else interpretation.get("grounding_status"),
            },
            "created_at": turn["created_at"],
            "updated_at": turn["updated_at"],
            "completed_at": turn["completed_at"],
            "row_version": turn["row_version"],
        }

    @staticmethod
    def _log_lifecycle(turn: dict[str, Any], event_type: ResearchTurnEventType, *, previous_status: ResearchTurnStatus | None = None) -> None:
        logger.info(
            "research_turn_lifecycle",
            extra={
                "turn_id": str(turn["id"]),
                "session_id": str(turn["research_session_id"]),
                "project_id": str(turn["project_id"]),
                "previous_status": previous_status.value if previous_status else None,
                "status": str(turn["status"]),
                "event_type": event_type.value,
            },
        )
