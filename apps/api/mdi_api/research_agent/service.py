from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import logging
import threading
from typing import Any, Iterator
from uuid import UUID, uuid4

from mdi_api.access import require_project_access
from mdi_api.agent2_errors import (
    ConcurrentTurnModification,
    InvalidResearchTurnTransition,
    ResearchSessionProjectMismatch,
    UnauthorizedScientificObjectReference,
)
from mdi_api.research_agent.schemas import (
    CreateResearchTurnRequest,
    CreateResearchTurnResponse,
    ResolvedResearchContext,
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
from mdi_api.routers.auth import CurrentUser
from mdi_api.unit_of_work import RepositoryFactory


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
    def __init__(self, repository_factory: RepositoryFactory) -> None:
        self.repository_factory = repository_factory

    def receive_turn(
        self,
        *,
        project_id: str,
        session_id: str,
        request: CreateResearchTurnRequest,
        current_user: CurrentUser,
    ) -> CreateResearchTurnResponse:
        """Persist one user message, one RECEIVED turn, and one event atomically."""

        with _keyed_lock(_session_locks, session_id):
            with self.repository_factory.unit_of_work() as unit:
                require_project_access(unit.connection, project_id, current_user, write=True)
                session = unit.agent2.research_turns.lock_session(session_id)
                if session is None or str(session["project_id"]) != project_id:
                    raise ResearchSessionProjectMismatch(session_id)
                parent_turn_id = request.reply_to_turn_id
                if parent_turn_id is not None:
                    parent = unit.agent2.research_turns.get(parent_turn_id)
                    if parent["project_id"] != project_id or parent["research_session_id"] != session_id:
                        raise ResearchSessionProjectMismatch("reply_to_turn_id is outside the Research Session")
                    if parent["status"] != ResearchTurnStatus.NEEDS_CLARIFICATION.value:
                        raise InvalidResearchTurnTransition("reply_to_turn_id must reference NEEDS_CLARIFICATION")
                self._authorize_ui_context(unit, project_id, request)
                now = datetime.now(timezone.utc)
                message_id = f"message_{uuid4().hex}"
                ui_context = request.ui_context.model_dump(mode="json") if request.ui_context else None
                message = unit.agent2.research_turns.add_message({
                    "id": message_id,
                    "session_id": session_id,
                    "role": "user",
                    "content_summary": request.message,
                    "payload_json": {
                        "source": "agent2_research_turn",
                        "uiContext": ui_context,
                        "replyToTurnId": str(parent_turn_id) if parent_turn_id else None,
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
                turn_id = uuid4()
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
                    {"status": ResearchTurnStatus.RECEIVED.value, "ui_context": ui_context},
                    created_at=now,
                )
        self._log_lifecycle(turn, ResearchTurnEventType.TURN_RECEIVED)
        return CreateResearchTurnResponse(
            turn_id=turn_id,
            research_session_id=session_id,
            project_id=project_id,
            sequence_no=int(turn["sequence_no"]),
            status=ResearchTurnStatus.RECEIVED,
            user_message=ResearchTurnMessageDTO(id=message_id, role="USER", content=str(message["content_summary"])),
            created_at=turn["created_at"],
        )

    def get_turn(self, turn_id: UUID, current_user: CurrentUser) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user)
            return self._turn_view(session, turn)

    def list_session_turns(
        self,
        *,
        project_id: str,
        session_id: str,
        current_user: CurrentUser,
        cursor: int | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        with self.repository_factory.session() as session:
            require_project_access(session.connection, project_id, current_user)
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
            )

        estimated = sum(item.estimated_tokens for item in items)
        budget_policy = context_budget_policy(ContextOperation.ORCHESTRATOR)
        return ContextManifest(
            context_manifest_id=uuid4(),
            operation="ORCHESTRATOR",
            project_id=context.project_id,
            research_session_id=context.research_session_id,
            research_turn_id=turn_id,
            policy_version="agent2.context-policy/2.0",
            included_items=items,
            excluded_items=[],
            estimated_input_tokens=estimated,
            input_budget=budget_policy.effective_input_budget,
            reserved_output_tokens=budget_policy.reserved_output_tokens,
            repair_margin=budget_policy.repair_margin,
            compaction_state="NONE",
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

    def cancel_turn(self, turn_id: UUID, current_user: CurrentUser) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user, write=True)
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

    def list_events(self, turn_id: UUID, current_user: CurrentUser, *, after_sequence: int = 0) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            require_project_access(session.connection, str(turn["project_id"]), current_user)
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
