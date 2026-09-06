from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID, uuid4

from mdi_api.research_agent.schemas import ResearchAction, ResearchTurnEventType, ResearchTurnStatus
from mdi_api.research_agent.turns.state_machine import ensure_transition
from mdi_api.research_agent.execution.errors import ExecutionPlanNotReady, ExecutionQueuePublishFailed, ExecutionSourceUnavailable


logger = logging.getLogger(__name__)


class ExecutionQueue(Protocol):
    def enqueue_job(self, job_id: str) -> Any: ...


@dataclass(frozen=True)
class DispatchResult:
    turn_id: UUID
    job_id: str
    queued: bool
    queue_backend: str
    message: str


class DisabledExecutionQueue:
    def enqueue_job(self, job_id: str) -> dict[str, Any]:
        return {"job_id": job_id, "enqueued": False, "backend": "disabled", "message": "execution queue is disabled"}


class ResearchExecutionDispatcher:
    """Attach one persisted AnalysisPlan to one existing Job, then wake a Worker."""

    def __init__(self, repository_factory: Any, *, queue: ExecutionQueue | None = None) -> None:
        self.repository_factory = repository_factory
        self.queue = queue or self._default_queue()

    @staticmethod
    def _default_queue() -> ExecutionQueue:
        from mdi_api.config import load_settings
        settings = load_settings()
        if settings.queue_backend == "redis":
            from mdi_workers.queue_runtime import RedisRQQueueBackend
            return RedisRQQueueBackend(
                redis_url=settings.redis_url,
                queue_name=settings.agent2_execution_queue_name,
            )
        return DisabledExecutionQueue()

    def dispatch_turn(self, turn_id: UUID) -> DispatchResult:
        job_id: str
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            action = str(turn.get("action_type") or "")
            if action not in {ResearchAction.ANALYZE.value, ResearchAction.CONTINUE_ANALYSIS.value}:
                raise ExecutionPlanNotReady("only ANALYZE and CONTINUE_ANALYSIS turns can execute")
            status = ResearchTurnStatus(str(turn["status"]))
            if status not in {ResearchTurnStatus.PLAN_READY, ResearchTurnStatus.QUEUED}:
                if turn.get("job_id"):
                    job_id = str(turn["job_id"])
                else:
                    raise ExecutionPlanNotReady(f"turn is not PLAN_READY: {status.value}")
            else:
                if not turn.get("analysis_plan_id"):
                    raise ExecutionPlanNotReady("PLAN_READY turn has no persisted AnalysisPlan")
                if unit.agent2.research_capability_plans.get_for_turn(turn_id) is None:
                    raise ExecutionPlanNotReady("PLAN_READY turn has no immutable CapabilityPlan")
                snapshot = unit.agent2.research_context_snapshots.get_for_turn(turn_id)
                if snapshot is None:
                    raise ExecutionPlanNotReady("PLAN_READY turn has no immutable ResearchContextSnapshot")
                self._verify_exact_sources(unit, turn, snapshot)
                # The Turn is the durable idempotency key; retrying after a
                # commit/publish split must address the same Job identity.
                job_id = str(turn.get("job_id") or f"job_agent2_{str(turn_id).replace('-', '')}")
                existing_job = None
                try:
                    existing_job = unit.repositories.jobs.get(job_id) if turn.get("job_id") else None
                except Exception:
                    existing_job = None
                if existing_job is None:
                    plan = unit.repositories.analysis_plans.get_plan(str(turn["analysis_plan_id"]))
                    research_session = unit.agent2.research_turns.get_session(str(turn["research_session_id"]))
                    if research_session is None:
                        raise ExecutionPlanNotReady("Research Session no longer exists")
                    unit.repositories.jobs.create({
                        "jobId": job_id,
                        "projectId": str(turn["project_id"]),
                        "datasetId": plan.get("datasetId"),
                        "planId": str(turn["analysis_plan_id"]),
                        "kind": "analysis",
                        "status": "created",
                        "createdBy": str(research_session["created_by"]),
                    })
                    unit.repositories.analysis_plans.attach_plan_to_job(str(turn["analysis_plan_id"]), job_id)
                    updated = unit.agent2.research_turns.attach_job(turn_id, job_id)
                else:
                    updated = turn
                if str(unit.repositories.jobs.get(job_id).get("status")) == "created":
                    unit.repositories.jobs.set_status(job_id, "queued")
                if ResearchTurnStatus(str(updated["status"])) == ResearchTurnStatus.PLAN_READY:
                    ensure_transition(ResearchTurnStatus.PLAN_READY, ResearchTurnStatus.QUEUED)
                    unit.agent2.research_turns.compare_and_set_status(
                        turn_id,
                        expected_status=ResearchTurnStatus.PLAN_READY.value,
                        expected_version=int(updated["row_version"]),
                        target_status=ResearchTurnStatus.QUEUED.value,
                    )
                self._event(unit, turn_id, ResearchTurnEventType.EXECUTION_DISPATCH_STARTED, {"status": ResearchTurnStatus.QUEUED.value})
                self._event(unit, turn_id, ResearchTurnEventType.JOB_ATTACHED, {"status": ResearchTurnStatus.QUEUED.value})

        try:
            queued = self.queue.enqueue_job(job_id)
        except Exception as exc:
            logger.warning("agent2_execution_queue_publish_failed", extra={"turn_id": str(turn_id), "job_id": job_id, "error_type": type(exc).__name__})
            raise ExecutionQueuePublishFailed("execution queue publish failed; the same Job remains recoverable") from exc
        backend = str(getattr(queued, "backend", None) or (queued.get("backend") if isinstance(queued, dict) else "unknown"))
        enqueued = bool(getattr(queued, "enqueued", None) if not isinstance(queued, dict) else queued.get("enqueued"))
        message = str(getattr(queued, "message", None) or (queued.get("message") if isinstance(queued, dict) else "queued"))
        if enqueued:
            with self.repository_factory.unit_of_work() as unit:
                self._event(unit, turn_id, ResearchTurnEventType.JOB_QUEUE_PUBLISHED, {"status": ResearchTurnStatus.QUEUED.value})
        return DispatchResult(turn_id=turn_id, job_id=job_id, queued=enqueued, queue_backend=backend, message=message)

    @staticmethod
    def _verify_exact_sources(unit: Any, turn: dict[str, Any], snapshot: dict[str, Any]) -> None:
        for ref in [*(snapshot.get("active_scope_refs_json") or []), *(snapshot.get("selection_refs_json") or [])]:
            try:
                version = unit.agent2.scientific_objects.get_version(UUID(str(ref["version_id"])))
                logical = unit.agent2.scientific_objects.get_object(UUID(str(ref["object_id"])))
            except Exception as exc:
                raise ExecutionSourceUnavailable("an exact source version is unavailable before dispatch") from exc
            if (
                str(logical["project_id"]) != str(turn["project_id"])
                or str(version["scientific_object_id"]) != str(logical["id"])
                or str(version.get("availability_status")) in {"SOURCE_MISSING", "INVALID"}
            ):
                raise ExecutionSourceUnavailable("an exact source version is unavailable before dispatch")

    @staticmethod
    def _event(unit: Any, turn_id: UUID, event_type: ResearchTurnEventType, payload: dict[str, Any]) -> None:
        existing = unit.agent2.research_turn_events.list_for_turn(turn_id)
        if any(item["event_type"] == event_type.value and (item.get("payload_json") or {}).get("status") == payload.get("status") for item in existing):
            return
        unit.agent2.research_turn_events.append_turn_event({
            "id": uuid4(),
            "turn_id": turn_id,
            "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
            "event_type": event_type.value,
            "payload_json": payload,
        })
