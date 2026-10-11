from __future__ import annotations

from dataclasses import dataclass
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import asyncio
import logging
import re
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import or_, select

from mdi_api.config import ApiSettings, load_settings
from mdi_api.bootstrap.repository_factory import create_repository_factory
from mdi_api.db import agent2_scientific_report_generations, jobs, projects, research_turn_events, research_turns
from mdi_api.infrastructure.interpretation.reconciler import ScientificInterpretationReconciler
from mdi_api.infrastructure.scientific_results.queue import result_projection_queue_from_settings
from mdi_api.infrastructure.scientific_results.reconciler import ScientificResultReconciler
from mdi_api.research_agent.execution.reconciler import ResearchExecutionReconciler
from mdi_api.research_agent.execution.supervisor import ResearchExecutionSupervisor
from mdi_api.research_agent.orchestration.queue import RedisRQAgentTurnQueue
from mdi_api.research_agent.planning.queue import RedisRQCapabilityPlanningQueue
from mdi_api.research_agent.schemas import (
    ResearchAction,
    ResearchTurnEventType,
    ResearchTurnStatus,
)
from mdi_api.research_agent.lifecycle import (
    LifecycleFailureCategory,
    classify_failure,
    recovery_action,
    is_stale_active_turn,
)
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.research_agent.turns.state_machine import ensure_transition


logger = logging.getLogger(__name__)

_PRE_EXECUTION_STAGES = frozenset({
    ResearchTurnStatus.RESOLVING_CONTEXT,
    ResearchTurnStatus.ORCHESTRATING,
    ResearchTurnStatus.PLANNING,
})
_WAITING_PRE_EXECUTION_STAGES = frozenset({
    ResearchTurnStatus.RECEIVED,
    ResearchTurnStatus.READY_TO_PLAN,
    ResearchTurnStatus.PLAN_READY,
})
_EXECUTION_STAGES = frozenset({
    ResearchTurnStatus.QUEUED, ResearchTurnStatus.RUNNING, ResearchTurnStatus.CANCELING,
})
_RESULT_STAGES = frozenset({
    ResearchTurnStatus.RESULT_PENDING, ResearchTurnStatus.RESULT_READY, ResearchTurnStatus.INTERPRETING,
})

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

    @property
    def failure_category(self) -> str:
        if self.action in {"STALLED_STAGE_TERMINALIZED", "ABANDONED_EXECUTION_TERMINALIZED"}:
            return LifecycleFailureCategory.RETRYABLE.value
        if self.action == "QUEUE_UNAVAILABLE":
            return LifecycleFailureCategory.RETRYABLE.value
        if self.action == "LEGACY_QUERY_DATA_TERMINALIZED":
            return LifecycleFailureCategory.NONE.value
        if self.accepted:
            return LifecycleFailureCategory.RECOVERABLE.value
        return classify_failure(self.previous_status).value

    @property
    def recommended_action(self) -> str:
        if self.action == "QUEUE_UNAVAILABLE":
            return "retry_same_stage_with_existing_identity"
        return recovery_action(
            self.previous_status,
            LifecycleFailureCategory(self.failure_category),
        )


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
        statuses: frozenset[ResearchTurnStatus] = _ACTIVE_STATUSES,
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
                    research_turns.c.row_version,
                    projects.c.created_by,
                )
                .join(projects, projects.c.id == research_turns.c.project_id)
                .where(
                    research_turns.c.status.in_([item.value for item in statuses]),
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

    def expire_stalled_pre_execution(self) -> int:
        """Bound only pre-scientific stages; running Jobs retain lease authority."""
        candidates, _qualification = self.list_stale(
            stale_minutes=max(5, self.settings.agent2_startup_recovery_stale_minutes),
            limit=self.settings.agent2_startup_recovery_limit,
            statuses=_PRE_EXECUTION_STAGES | _WAITING_PRE_EXECUTION_STAGES,
        )
        count = 0
        for candidate in candidates[:self.settings.agent2_startup_recovery_limit]:
            try:
                with self.repository_factory.session() as session:
                    turn = session.agent2.research_turns.get(UUID(str(candidate["id"])))
                if turn["status"] != candidate["status"] or turn["row_version"] != candidate["row_version"]:
                    continue
                outcome = self._expire_stalled_stage(turn)
                count += int(outcome is not None and outcome.accepted)
            except Exception as exc:
                # One damaged historical row must not starve later messages.
                logger.warning("research_stage_watchdog_item_failed", extra={"error_type": type(exc).__name__})
        return count

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
                    "failureCategory": item.failure_category,
                    "recommendedAction": item.recommended_action,
                }
                for item in outcomes
            ],
        }

    def expire_stalled_results(self) -> int:
        """End inactive result/interpretation work without replaying science or providers."""
        enabled_stages = set()
        if self.settings.agent2_result_projection_enabled:
            enabled_stages.add(ResearchTurnStatus.RESULT_PENDING)
        if self.settings.agent2_interpretation_enabled:
            enabled_stages.update({ResearchTurnStatus.RESULT_READY, ResearchTurnStatus.INTERPRETING, ResearchTurnStatus.ORCHESTRATING})
        if not enabled_stages:
            return 0
        candidates, _qualification = self.list_stale(
            stale_minutes=max(5, self.settings.agent2_startup_recovery_stale_minutes),
            limit=self.settings.agent2_startup_recovery_limit,
            statuses=frozenset(enabled_stages),
        )
        candidates = [candidate for candidate in candidates if
            candidate["status"] != ResearchTurnStatus.ORCHESTRATING.value
            or candidate.get("action_type") == ResearchAction.INTERPRET_RESULT.value]
        count = 0
        for candidate in candidates[:self.settings.agent2_startup_recovery_limit]:
            try:
                with self.repository_factory.session() as session:
                    turn = session.agent2.research_turns.get(UUID(str(candidate["id"])))
                status = ResearchTurnStatus(str(turn["status"]))
                interpretation_handoff = (
                    status == ResearchTurnStatus.ORCHESTRATING
                    and str(turn.get("action_type") or "") == ResearchAction.INTERPRET_RESULT.value
                )
                if status not in _RESULT_STAGES and not interpretation_handoff:
                    continue
                projection = status == ResearchTurnStatus.RESULT_PENDING
                if not (self.settings.agent2_result_projection_enabled if projection else self.settings.agent2_interpretation_enabled):
                    continue
                if not is_stale_active_turn(
                    turn, stale_after_seconds=max(300, self.settings.agent2_startup_recovery_stale_minutes * 60),
                ):
                    continue
                updated = ResearchTurnService(self.repository_factory).fail_if_active(
                    UUID(str(turn["id"])),
                    "RESULT_PROJECTION_TIMEOUT" if projection else "INTERPRETATION_STAGE_TIMEOUT",
                    "Result processing exceeded its recovery deadline; saved scientific outputs are retained.",
                    expected_statuses=frozenset({status}),
                    expected_version=int(turn["row_version"]),
                )
                count += int(updated is not None)
            except Exception as exc:
                logger.warning("research_result_watchdog_item_failed", extra={"error_type": type(exc).__name__})
        return count

    def expire_stalled_reports(self) -> int:
        """Bound lost report work while retaining its completed research/results."""
        if not self.settings.agent2_report_enabled:
            return 0
        table = agent2_scientific_report_generations
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=max(5, self.settings.agent2_startup_recovery_stale_minutes))
        with self.repository_factory.session() as session:
            rows = session.connection.execute(
                select(table, projects.c.created_by)
                .join(projects, projects.c.id == table.c.project_id)
                .where(table.c.status.in_(["REQUESTED", "COMPOSING"]), table.c.updated_at < cutoff)
                .order_by(table.c.updated_at, table.c.id)
                .limit(max(1000, self.settings.agent2_startup_recovery_limit * 10))
            ).mappings().all()
        count = processed = 0
        for row in rows:
            if is_qualification_project(project_id=str(row["project_id"]), created_by=str(row["created_by"])):
                continue
            if processed >= self.settings.agent2_startup_recovery_limit:
                break
            processed += 1
            try:
                with self.repository_factory.unit_of_work() as unit:
                    report = unit.agent2.scientific_reports.get_for_turn(row["research_turn_id"])
                    ready = report is not None and report["project_id"] == row["project_id"]
                    updated = unit.agent2.scientific_report_generations.compare_status(
                        row["id"], "READY" if ready else "FAILED",
                        expected_status=row["status"], expected_attempt=row["attempt_count"],
                        expected_updated_at=row["updated_at"],
                        error_code=None if ready else "REPORT_QUEUE_TIMEOUT" if row["status"] == "REQUESTED" else "REPORT_STAGE_TIMEOUT",
                        error_summary=None if ready else "报告生成超过恢复时限，可重试生成；已保存的科学结果保留。",
                        # Consume the unclaimed attempt so its delayed queue
                        # message cannot claim a later explicit retry.
                        increment_attempt=not ready and row["status"] == "REQUESTED",
                    )
                    count += int(updated is not None)
            except Exception as exc:
                logger.warning("report_watchdog_item_failed", extra={"error_type": type(exc).__name__})
        return count

    def expire_stalled_execution(self) -> int:
        """Find inactive execution Jobs without allowing live leases to crowd them out."""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=max(5, self.settings.agent2_startup_recovery_stale_minutes))
        with self.repository_factory.session() as session:
            rows = session.connection.execute(
                select(research_turns.c.id, research_turns.c.project_id, projects.c.created_by)
                .join(projects, projects.c.id == research_turns.c.project_id)
                .join(jobs, jobs.c.id == research_turns.c.job_id)
                .where(
                    research_turns.c.status.in_([status.value for status in _EXECUTION_STAGES]),
                    jobs.c.status.in_(["created", "queued", "running", "cancel_requested"]),
                    jobs.c.updated_at < cutoff,
                    or_(jobs.c.lease_expires_at.is_(None), jobs.c.lease_expires_at <= now),
                )
                .order_by(jobs.c.updated_at.asc(), research_turns.c.id)
                .limit(max(1000, self.settings.agent2_startup_recovery_limit * 10))
            ).mappings().all()
        count = processed = 0
        for row in rows:
            if is_qualification_project(project_id=str(row["project_id"]), created_by=str(row["created_by"])):
                continue
            if processed >= self.settings.agent2_startup_recovery_limit:
                break
            processed += 1
            try:
                count += int(self._expire_execution_turn(UUID(str(row["id"]))))
            except Exception as exc:
                logger.warning("research_execution_watchdog_item_failed", extra={"error_type": type(exc).__name__})
        return count

    def reconcile_finished_execution(self) -> int:
        """Repair the commit/sync gap using saved execution outputs only."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=1)
        with self.repository_factory.session() as session:
            rows = session.connection.execute(
                select(research_turns.c.job_id, research_turns.c.project_id, projects.c.created_by)
                .join(projects, projects.c.id == research_turns.c.project_id)
                .join(jobs, jobs.c.id == research_turns.c.job_id)
                .where(
                    research_turns.c.status.in_([status.value for status in _EXECUTION_STAGES]),
                    jobs.c.status.in_(["completed", "partial_success", "failed", "cancelled"]),
                    jobs.c.project_id == research_turns.c.project_id,
                    jobs.c.updated_at < cutoff,
                )
                .order_by(jobs.c.updated_at, research_turns.c.id)
                .limit(max(1000, self.settings.agent2_startup_recovery_limit * 10))
            ).mappings().all()
        count = processed = 0
        for row in rows:
            if is_qualification_project(project_id=str(row["project_id"]), created_by=str(row["created_by"])):
                continue
            if processed >= self.settings.agent2_startup_recovery_limit:
                break
            processed += 1
            try:
                view = ResearchExecutionSupervisor(self.repository_factory).sync_for_job(
                    str(row["job_id"]), recover_terminal_only=True,
                )
                count += int(view is not None)
            except Exception as exc:
                logger.warning("research_execution_handoff_failed", extra={"error_type": type(exc).__name__})
        return count

    def republish_unstarted_results(self) -> int:
        """Retry missed result wakeups without renewing their inactivity deadline."""
        if not self.settings.agent2_result_projection_enabled or (
            self.result_queue is None and self.settings.queue_backend != "redis"
        ):
            return 0
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=max(5, self.settings.agent2_startup_recovery_stale_minutes))
        with self.repository_factory.session() as session:
            rows = session.connection.execute(
                select(research_turns.c.id, research_turns.c.project_id, projects.c.created_by)
                .join(projects, projects.c.id == research_turns.c.project_id)
                .join(jobs, jobs.c.id == research_turns.c.job_id)
                .where(
                    research_turns.c.status == ResearchTurnStatus.RESULT_PENDING.value,
                    research_turns.c.updated_at >= cutoff,
                    research_turns.c.updated_at < now - timedelta(minutes=1),
                    jobs.c.project_id == research_turns.c.project_id,
                    jobs.c.status.in_(["completed", "partial_success", "failed"]),
                    ~select(research_turn_events.c.id).where(
                        research_turn_events.c.turn_id == research_turns.c.id,
                        research_turn_events.c.event_type == "RESULT_PROJECTION_STARTED",
                    ).exists(),
                )
                .order_by(research_turns.c.updated_at, research_turns.c.id)
                .limit(max(1000, self.settings.agent2_startup_recovery_limit * 10))
            ).mappings().all()
        queue = self.result_queue or result_projection_queue_from_settings(self.settings)
        count = processed = 0
        for row in rows:
            if is_qualification_project(project_id=str(row["project_id"]), created_by=str(row["created_by"])):
                continue
            if processed >= self.settings.agent2_startup_recovery_limit:
                break
            processed += 1
            try:
                result = ScientificResultReconciler(self.repository_factory, queue).reconcile_turn(UUID(str(row["id"])))
                count += int(result is not None and result.enqueued)
            except Exception as exc:
                logger.warning("research_result_handoff_failed", extra={"error_type": type(exc).__name__})
                # A bounded Redis timeout must not be multiplied by the batch.
                break
        return count

    def _expire_execution_turn(self, turn_id: UUID) -> bool:
        # Use the same Turn -> Job lock order as normal progress publication.
        # Job, unfinished calls, Turn and events commit or roll back together.
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            status = ResearchTurnStatus(str(turn["status"]))
            job_id = str(turn.get("job_id") or "")
            if status not in _EXECUTION_STAGES or not job_id:
                return False
            job = unit.repositories.jobs.get(job_id)
            if str(job["projectId"]) != str(turn["project_id"]):
                return False
            waiting = job["status"] in {"created", "queued"}
            error_code = "EXECUTION_QUEUE_TIMEOUT" if waiting else "EXECUTION_WORKER_LOST"
            reason = "Scientific queue wait exceeded its recovery deadline." if waiting else "Execution lease expired without further activity."
            expired = unit.repositories.jobs.expire_abandoned_execution(
                job_id,
                stale_after_seconds=max(300, self.settings.agent2_startup_recovery_stale_minutes * 60),
                cancel_requested=status == ResearchTurnStatus.CANCELING,
            )
            if expired is None:
                return False
            cancelled = expired["status"] == "cancelled"
            for call in unit.repositories.tool_calls.list_for_job(job_id):
                if int(call.get("attempt") or 0) != int(expired.get("executionAttempt") or 0):
                    continue
                if call["status"] in {"planned", "running"}:
                    unit.repositories.tool_calls.save({
                        **call, "status": "skipped" if cancelled else "failed",
                        "error": {"code": error_code, "message": reason},
                    })
            target = ResearchTurnStatus.CANCELED if cancelled else ResearchTurnStatus.FAILED
            if cancelled and status != ResearchTurnStatus.CANCELING:
                ensure_transition(status, ResearchTurnStatus.CANCELING)
                turn = unit.agent2.research_turns.compare_and_set_status(
                    turn_id, expected_status=status.value, expected_version=int(turn["row_version"]),
                    target_status=ResearchTurnStatus.CANCELING.value,
                )
                status = ResearchTurnStatus.CANCELING
                self._append_event(unit, turn_id, ResearchTurnEventType.CANCELLATION_REQUESTED, {"status": status.value})
            ensure_transition(status, target)
            unit.agent2.research_turns.compare_and_set_status(
                turn_id, expected_status=status.value, expected_version=int(turn["row_version"]),
                target_status=target.value, completed_at=datetime.now(timezone.utc),
                error_code=None if cancelled else error_code,
                error_summary=None if cancelled else f"{reason} Saved outputs are retained.",
            )
            self._append_event(
                unit, turn_id,
                ResearchTurnEventType.EXECUTION_CANCELED if cancelled else ResearchTurnEventType.TURN_FAILED,
                {"status": target.value, "error_code": None if cancelled else error_code},
            )
            unit.repositories.job_events.append_event(
                job_id, event_type="job.abandoned_execution_ended", status="warning" if cancelled else "error",
                message=reason,
                payload={"executionAttempt": expired.get("executionAttempt"), "cancelled": cancelled},
            )
        return True

    def reconcile_turn(self, turn_id: UUID) -> RecoveryOutcome:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            status = ResearchTurnStatus(str(turn["status"]))

        if status in _EXECUTION_STAGES and turn.get("job_id"):
            view = ResearchExecutionSupervisor(self.repository_factory).sync_for_job(
                str(turn["job_id"]), recover_terminal_only=True,
            )
            if view is not None:
                if view.status == ResearchTurnStatus.RESULT_PENDING and self.settings.agent2_result_projection_enabled:
                    queue = self.result_queue or result_projection_queue_from_settings(self.settings)
                    try:
                        ScientificResultReconciler(self.repository_factory, queue).reconcile_turn(turn_id)
                    except Exception as exc:
                        return self._queue_unavailable(turn_id, status, "RESULT_PROJECTION_REPUBLISH", exc)
                return RecoveryOutcome(turn_id, status.value, "EXECUTION_HANDOFF_RECONCILED", True, "saved execution outcome synchronized")

        if status in _EXECUTION_STAGES and self._expire_execution_turn(turn_id):
            return RecoveryOutcome(
                turn_id, status.value, "ABANDONED_EXECUTION_TERMINALIZED", True,
                "expired execution ended; saved outputs retained",
            )

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

        expired = self._expire_stalled_stage(turn)
        if expired is not None:
            return expired

        return RecoveryOutcome(
            turn_id,
            status.value,
            "MANUAL_ATTENTION_REQUIRED",
            False,
            "state cannot be replayed without risking duplicate or unauthorized scientific work",
        )

    def _expire_stalled_stage(self, turn: dict[str, Any]) -> RecoveryOutcome | None:
        status = ResearchTurnStatus(str(turn["status"]))
        turn_id = UUID(str(turn["id"]))
        waiting = status in _WAITING_PRE_EXECUTION_STAGES
        if (
            status in _PRE_EXECUTION_STAGES | _WAITING_PRE_EXECUTION_STAGES
            and not turn.get("job_id")
            and (waiting or str(turn.get("action_type") or "") not in {
                ResearchAction.INTERPRET_RESULT.value, ResearchAction.QUERY_DATA.value,
            })
            and is_stale_active_turn(
                turn,
                stale_after_seconds=max(300, self.settings.agent2_startup_recovery_stale_minutes * 60),
            )
        ):
            updated = ResearchTurnService(self.repository_factory).fail_if_active(
                turn_id,
                "RESEARCH_QUEUE_TIMEOUT" if waiting else "RESEARCH_STAGE_TIMEOUT",
                "Research queue wait exceeded its recovery deadline; no scientific job was started" if waiting
                else "Research preparation exceeded its recovery deadline; no scientific job was started",
                expected_statuses=frozenset({status}),
                expected_version=int(turn["row_version"]),
            )
            return RecoveryOutcome(
                turn_id, status.value, "STALLED_STAGE_TERMINALIZED", updated is not None,
                "stalled preparation ended with retry feedback" if updated else "newer durable state preserved",
            )

        return None

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


def _watchdog_cycle(settings: ApiSettings) -> int:
    service = StaleResearchRecoveryService(
        create_repository_factory(settings), settings=settings,
    )
    return (
        service.expire_stalled_pre_execution() + service.expire_stalled_execution()
        + service.expire_stalled_results() + service.reconcile_finished_execution()
        + service.republish_unstarted_results() + service.expire_stalled_reports()
    )


@asynccontextmanager
async def research_stage_watchdog(settings: ApiSettings, *, interval_seconds: float = 60.0):
    """Check preparation/result deadlines and abandoned execution leases.

    The loop never reruns scientific execution. It synchronizes saved outcomes
    and republishes only unstarted result projection identities, with bounded
    queue I/O. Its cycles never overlap.
    """
    if not (
        settings.agent2_startup_recovery_enabled
        and "postgres" in settings.database_url
        and settings.queue_backend == "redis"
        and (settings.agent2_orchestration_enabled or settings.agent2_report_enabled)
    ):
        yield
        return
    stopped = asyncio.Event()
    logger.info("research_stage_watchdog_started interval_seconds=%s stale_minutes=%s", interval_seconds, max(5, settings.agent2_startup_recovery_stale_minutes))

    async def maintain():
        while not stopped.is_set():
            try:
                expired = await asyncio.to_thread(_watchdog_cycle, settings)
                if expired:
                    logger.info("research_stage_watchdog_recovered count=%s", expired)
            except Exception as exc:
                logger.warning("research_stage_watchdog_failed", extra={"error_type": type(exc).__name__})
            try:
                await asyncio.wait_for(stopped.wait(), timeout=max(0.01, interval_seconds))
            except asyncio.TimeoutError:
                pass

    task = asyncio.create_task(maintain(), name="research-stage-watchdog")
    try:
        yield
    finally:
        stopped.set()
        await task


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
