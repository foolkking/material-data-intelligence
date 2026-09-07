from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import logging
import re
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select

from mdi_api.config import ApiSettings, load_settings
from mdi_api.database import create_repository_factory
from mdi_api.db import projects, research_turns
from mdi_api.interpretation.reconciler import ScientificInterpretationReconciler
from mdi_api.research_agent.execution.reconciler import ResearchExecutionReconciler
from mdi_api.research_agent.orchestration.queue import RedisRQAgentTurnQueue
from mdi_api.research_agent.planning.queue import RedisRQCapabilityPlanningQueue
from mdi_api.research_agent.schemas import (
    ResearchAction,
    ResearchTurnEventType,
    ResearchTurnStatus,
)
from mdi_api.scientific_results.queue import result_projection_queue_from_settings
from mdi_api.scientific_results.reconciler import ScientificResultReconciler


logger = logging.getLogger(__name__)

_ACTIVE_STATUSES = frozenset({
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
})
_PHASE_OWNER = re.compile(r"^agent2-phase[0-9]+-owner-[0-9a-f]+$")
_AGENT2_OWNER = re.compile(r"^agent2-owner-[0-9a-f]+$")
_CI_ACTOR = re.compile(r"^phase[0-9]+[a-z0-9_-]*_ci$")


def is_qualification_project(*, project_id: str, created_by: str) -> bool:
    """Classify retained qualification identities without hiding user data.

    Both the bounded actor convention and the matching project convention are
    required for generated Agent2 fixtures.  Generic ``user_local`` projects,
    including authenticated browser qualification projects, remain product
    data and are never suppressed by this classifier.
    """

    if created_by == "test_user":
        return project_id.startswith(("proj_", "project_phase", "project_"))
    if _CI_ACTOR.fullmatch(created_by):
        return project_id.startswith("project_")
    if _PHASE_OWNER.fullmatch(created_by):
        return project_id.startswith("agent2-phase")
    if _AGENT2_OWNER.fullmatch(created_by):
        return project_id.startswith("agent2-project-")
    return False


@dataclass(frozen=True)
class RecoveryOutcome:
    turn_id: UUID
    previous_status: str
    action: str
    accepted: bool
    detail: str


class StaleResearchRecoveryService:
    """Republish recoverable durable work after API/queue interruption.

    The service never deletes scientific state and never reruns a completed
    Result.  It wakes only the existing identity-specific orchestration,
    planning, execution, Result or interpretation boundary.  States that
    cannot be replayed safely remain visible as attention items.
    """

    def __init__(
        self,
        repository_factory: Any | None = None,
        *,
        settings: ApiSettings | None = None,
        orchestration_queue: Any | None = None,
        planning_queue: Any | None = None,
        execution_queue: Any | None = None,
        result_queue: Any | None = None,
        interpretation_queue: Any | None = None,
    ) -> None:
        self.repository_factory = repository_factory or create_repository_factory()
        self.settings = settings or load_settings()
        # Queue adapters are injectable for deterministic outage/recovery
        # qualification.  Production keeps the existing settings-backed
        # adapters; the durable PostgreSQL identities remain authoritative.
        self.orchestration_queue = orchestration_queue
        self.planning_queue = planning_queue
        self.execution_queue = execution_queue
        self.result_queue = result_queue
        self.interpretation_queue = interpretation_queue

    def list_stale(
        self,
        *,
        stale_minutes: int = 15,
        limit: int = 200,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=max(1, stale_minutes))
        with self.repository_factory.session() as session:
            rows = session.connection.execute(
                select(
                    research_turns.c.id,
                    research_turns.c.project_id,
                    research_turns.c.status,
                    research_turns.c.action_type,
                    research_turns.c.updated_at,
                    projects.c.created_by,
                )
                .join(projects, projects.c.id == research_turns.c.project_id)
                .where(
                    research_turns.c.status.in_([item.value for item in _ACTIVE_STATUSES]),
                    research_turns.c.updated_at < cutoff,
                )
                .order_by(research_turns.c.updated_at.asc())
                # Qualification campaigns intentionally retain many
                # intermediate Turns.  Scan a bounded but substantially larger
                # window before classification so those rows cannot crowd
                # real product work out of the recovery candidate set.
                .limit(max(1000, max(1, limit) * 10))
            ).mappings().all()
        product: list[dict[str, Any]] = []
        qualification: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            target = qualification if is_qualification_project(
                project_id=str(item["project_id"]),
                created_by=str(item["created_by"]),
            ) else product
            target.append(item)
        return product, qualification

    def reconcile_stale(
        self,
        *,
        stale_minutes: int = 15,
        limit: int = 50,
    ) -> dict[str, Any]:
        product, qualification = self.list_stale(
            stale_minutes=stale_minutes,
            limit=max(limit * 4, limit),
        )
        outcomes = [self.reconcile_turn(UUID(str(item["id"]))) for item in product[:limit]]
        return {
            "productCandidates": len(product),
            "qualificationRetained": len(qualification),
            "accepted": sum(1 for item in outcomes if item.accepted),
            "attention": sum(1 for item in outcomes if not item.accepted),
            "items": [
                {
                    "turnId": str(item.turn_id),
                    "previousStatus": item.previous_status,
                    "action": item.action,
                    "accepted": item.accepted,
                    "detail": item.detail,
                }
                for item in outcomes
            ],
        }

    def reconcile_turn(self, turn_id: UUID) -> RecoveryOutcome:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            status = ResearchTurnStatus(str(turn["status"]))

        if status == ResearchTurnStatus.RECEIVED:
            queue = self.orchestration_queue or RedisRQAgentTurnQueue(
                redis_url=self.settings.redis_url,
                queue_name=self.settings.agent2_queue_name,
            )
            try:
                queued = queue.enqueue_turn(turn_id)
            except Exception as exc:
                return self._queue_unavailable(turn_id, status, "ORCHESTRATION_REPUBLISH", exc)
            return RecoveryOutcome(turn_id, status.value, "ORCHESTRATION_REPUBLISHED", True, queued.message)

        if status == ResearchTurnStatus.READY_TO_PLAN:
            queue = self.planning_queue or RedisRQCapabilityPlanningQueue(
                redis_url=self.settings.redis_url,
                queue_name=self.settings.agent2_planning_queue_name,
            )
            try:
                queued = queue.enqueue_turn(turn_id)
            except Exception as exc:
                return self._queue_unavailable(turn_id, status, "PLANNING_REPUBLISH", exc)
            return RecoveryOutcome(turn_id, status.value, "PLANNING_REPUBLISHED", True, queued.message)

        if status in {ResearchTurnStatus.PLAN_READY, ResearchTurnStatus.QUEUED}:
            try:
                result = ResearchExecutionReconciler(
                    self.repository_factory,
                    queue=self.execution_queue,
                ).reconcile_turn(turn_id)
            except Exception as exc:
                return self._queue_unavailable(turn_id, status, "EXECUTION_RECONCILE", exc)
            return RecoveryOutcome(
                turn_id,
                status.value,
                "EXECUTION_RECONCILED",
                result is not None,
                "existing execution identity republished" if result is not None else "no execution action",
            )

        if status == ResearchTurnStatus.RESULT_PENDING:
            queue = self.result_queue or result_projection_queue_from_settings(self.settings)
            try:
                result = ScientificResultReconciler(
                    self.repository_factory,
                    queue,
                ).reconcile_turn(turn_id)
            except Exception as exc:
                return self._queue_unavailable(turn_id, status, "RESULT_PROJECTION_REPUBLISH", exc)
            return RecoveryOutcome(
                turn_id,
                status.value,
                "RESULT_PROJECTION_REPUBLISHED",
                result is not None,
                "existing Result projection identity republished" if result is not None else "no Result action",
            )

        if status in {ResearchTurnStatus.RESULT_READY, ResearchTurnStatus.INTERPRETING}:
            try:
                result = ScientificInterpretationReconciler(
                    self.repository_factory,
                    queue=self.interpretation_queue,
                ).reconcile_turn(turn_id)
            except Exception as exc:
                return self._queue_unavailable(turn_id, status, "INTERPRETATION_RECONCILE", exc)
            accepted = bool(result and (result.get("republished") or result.get("reason") == "not_result_ready"))
            return RecoveryOutcome(
                turn_id,
                status.value,
                "INTERPRETATION_RECONCILED",
                accepted,
                str((result or {}).get("reason") or (result or {}).get("backend") or "no interpretation action"),
            )

        if status == ResearchTurnStatus.ORCHESTRATING and str(turn.get("action_type") or "") == ResearchAction.QUERY_DATA.value:
            repaired = self._finalize_legacy_query_data(turn_id)
            return RecoveryOutcome(
                turn_id,
                status.value,
                "LEGACY_QUERY_DATA_TERMINALIZED",
                repaired,
                "query-only Turn completed without scientific execution",
            )

        return RecoveryOutcome(
            turn_id,
            status.value,
            "MANUAL_ATTENTION_REQUIRED",
            False,
            "state cannot be replayed without risking duplicate or unauthorized scientific work",
        )

    @staticmethod
    def _queue_unavailable(
        turn_id: UUID,
        status: ResearchTurnStatus,
        operation: str,
        error: Exception,
    ) -> RecoveryOutcome:
        logger.warning(
            "research_recovery_queue_unavailable",
            extra={
                "turn_id": str(turn_id),
                "status": status.value,
                "operation": operation,
                "error_type": type(error).__name__,
            },
        )
        return RecoveryOutcome(
            turn_id,
            status.value,
            "QUEUE_UNAVAILABLE",
            False,
            "queue backend unavailable; durable state remains retryable",
        )

    def _finalize_legacy_query_data(self, turn_id: UUID) -> bool:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            decision = unit.agent2.research_turn_decisions.get_for_turn(turn_id)
            if (
                str(turn["status"]) != ResearchTurnStatus.ORCHESTRATING.value
                or str(turn.get("action_type") or "") != ResearchAction.QUERY_DATA.value
                or decision is None
                or str(decision.get("action") or "") != ResearchAction.QUERY_DATA.value
            ):
                return False
            decision_json = dict(decision.get("decision_json") or {})
            assistant_content = str(
                decision_json.get("assistant_message")
                or "已识别为数据查询请求。请在数据平台查看或调整筛选条件；本次未创建科学分析运行。"
            )
            message_id = f"message_recovery_{turn_id.hex}"
            unit.agent2.research_turns.add_message({
                "id": message_id,
                "session_id": turn["research_session_id"],
                "role": "agent",
                "content_summary": assistant_content,
                "payload_json": {
                    "source": "agent2_research_recovery",
                    "messageKind": "QUERY_DATA_ACK",
                    "turnId": str(turn_id),
                    "legacyProjectionRepair": True,
                },
                "created_at": datetime.now(timezone.utc),
            })
            completed = unit.agent2.research_turns.compare_and_set_status(
                turn_id,
                expected_status=ResearchTurnStatus.ORCHESTRATING.value,
                expected_version=int(turn["row_version"]),
                target_status=ResearchTurnStatus.ANSWERED.value,
                completed_at=datetime.now(timezone.utc),
            )
            unit.agent2.research_turns.attach_message_refs(
                turn_id,
                assistant_final_message_id=message_id,
            )
            unit.agent2.research_turn_decisions.complete_legacy_dispatch(turn_id)
            self._append_event(
                unit,
                turn_id,
                ResearchTurnEventType.DIRECT_ANSWER_READY,
                {
                    "message_id": message_id,
                    "content": assistant_content,
                    "status": ResearchTurnStatus.ANSWERED.value,
                    "recovered": True,
                },
            )
            self._append_event(
                unit,
                turn_id,
                ResearchTurnEventType.TURN_COMPLETED,
                {"status": ResearchTurnStatus.ANSWERED.value, "recovered": True},
            )
            logger.info(
                "legacy_query_data_turn_recovered",
                extra={
                    "turn_id": str(turn_id),
                    "project_id": str(completed["project_id"]),
                },
            )
        return True

    @staticmethod
    def _append_event(
        unit: Any,
        turn_id: UUID,
        event_type: ResearchTurnEventType,
        payload: dict[str, Any],
    ) -> None:
        unit.agent2.research_turn_events.append_turn_event({
            "id": uuid4(),
            "turn_id": turn_id,
            "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
            "event_type": event_type.value,
            "payload_json": payload,
            "created_at": datetime.now(timezone.utc),
        })


def run_startup_recovery(
    settings: ApiSettings | None = None,
    *,
    stale_minutes: int = 15,
    limit: int = 50,
) -> dict[str, Any]:
    active = settings or load_settings()
    if (
        "postgres" not in active.database_url
        or active.queue_backend != "redis"
        or not active.agent2_orchestration_enabled
    ):
        return {
            "productCandidates": 0,
            "qualificationRetained": 0,
            "accepted": 0,
            "attention": 0,
            "items": [],
            "disabled": True,
        }
    from mdi_workers.queue_runtime import RedisRQQueueBackend

    return StaleResearchRecoveryService(
        repository_factory=create_repository_factory(active),
        settings=active,
        execution_queue=RedisRQQueueBackend(
            redis_url=active.redis_url,
            queue_name=active.agent2_execution_queue_name,
        ),
    ).reconcile_stale(
        stale_minutes=stale_minutes,
        limit=limit,
    )


__all__ = [
    "RecoveryOutcome",
    "StaleResearchRecoveryService",
    "is_qualification_project",
    "run_startup_recovery",
]
