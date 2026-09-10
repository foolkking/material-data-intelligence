"""Read-only ResearchTurn lifecycle projection and failure classification.

The persisted ResearchTurn/Job/ToolCall/Event records remain authoritative.
This module deliberately contains no writes and no second state machine.  It
maps the existing statuses and events into a bounded operational view that is
safe for progress, correlation, and recovery tooling to consume.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable, Mapping

from mdi_api.research_agent.context.provenance import context_provenance_summary
from mdi_api.research_agent.schemas import ResearchTurnStatus


class LifecycleFailureCategory(str, Enum):
    NONE = "NONE"
    TERMINAL = "TERMINAL"
    RETRYABLE = "RETRYABLE"
    RECOVERABLE = "RECOVERABLE"
    CANCELLED = "CANCELLED"


_STAGE_BY_STATUS: dict[str, tuple[str, str]] = {
    ResearchTurnStatus.RECEIVED.value: ("RECEIVED", "orchestration"),
    ResearchTurnStatus.RESOLVING_CONTEXT.value: ("CONTEXT", "orchestration"),
    ResearchTurnStatus.ORCHESTRATING.value: ("DECISION", "orchestration"),
    ResearchTurnStatus.NEEDS_CLARIFICATION.value: ("CLARIFICATION", "orchestration"),
    ResearchTurnStatus.ANSWERED.value: ("ANSWERED", "orchestration"),
    ResearchTurnStatus.UNSUPPORTED.value: ("UNSUPPORTED", "orchestration"),
    ResearchTurnStatus.READY_TO_PLAN.value: ("READY_TO_PLAN", "planning"),
    ResearchTurnStatus.PLANNING.value: ("PLANNING", "planning"),
    ResearchTurnStatus.PLAN_READY.value: ("PLAN_READY", "planning"),
    ResearchTurnStatus.PLAN_REJECTED.value: ("PLAN_REJECTED", "planning"),
    ResearchTurnStatus.QUEUED.value: ("QUEUED", "execution"),
    ResearchTurnStatus.RUNNING.value: ("RUNNING", "execution"),
    ResearchTurnStatus.CANCELING.value: ("CANCELING", "execution"),
    ResearchTurnStatus.RESULT_PENDING.value: ("RESULT_PENDING", "result_projection"),
    ResearchTurnStatus.RESULT_READY.value: ("RESULT_READY", "interpretation"),
    ResearchTurnStatus.INTERPRETING.value: ("INTERPRETING", "interpretation"),
    ResearchTurnStatus.COMPLETED.value: ("COMPLETED", "terminal"),
    ResearchTurnStatus.PARTIAL.value: ("PARTIAL", "terminal"),
    ResearchTurnStatus.FAILED.value: ("FAILED", "terminal"),
    ResearchTurnStatus.CANCELED.value: ("CANCELED", "terminal"),
}

_STAGE_EVENTS: dict[str, frozenset[str]] = {
    "RECEIVED": frozenset({"TURN_RECEIVED"}),
    "CONTEXT": frozenset({"CONTEXT_RESOLUTION_STARTED", "CONTEXT_RESOLVED"}),
    "DECISION": frozenset({"ORCHESTRATION_STARTED", "ORCHESTRATION_COMPLETED"}),
    "READY_TO_PLAN": frozenset({"PLAN_REQUESTED"}),
    "PLANNING": frozenset({"CAPABILITY_RESOLUTION_STARTED", "CAPABILITY_PLANNING_STARTED"}),
    "PLAN_READY": frozenset({"ANALYSIS_PLAN_BOUND", "PLAN_READY"}),
    "QUEUED": frozenset({"EXECUTION_DISPATCH_STARTED", "JOB_QUEUE_PUBLISHED"}),
    "RUNNING": frozenset({"JOB_STARTED", "EXECUTION_STEP_STARTED"}),
    "CANCELING": frozenset({"CANCELLATION_REQUESTED"}),
    "RESULT_PENDING": frozenset({"RESULT_PENDING", "JOB_TERMINAL"}),
    "RESULT_READY": frozenset({"RESULT_READY", "RESULT_PROJECTED"}),
    "INTERPRETING": frozenset({"INTERPRETATION_STARTED"}),
    "COMPLETED": frozenset({"TURN_COMPLETED"}),
    "PARTIAL": frozenset({"TURN_PARTIAL"}),
    "FAILED": frozenset({"TURN_FAILED"}),
    "CANCELED": frozenset({"TURN_CANCELED"}),
    "CLARIFICATION": frozenset({"CLARIFICATION_REQUESTED"}),
    "ANSWERED": frozenset({"DIRECT_ANSWER_READY"}),
    "UNSUPPORTED": frozenset({"CAPABILITY_UNSUPPORTED", "TURN_UNSUPPORTED"}),
    "PLAN_REJECTED": frozenset({"CAPABILITY_PLAN_REJECTED", "PLAN_REJECTED"}),
}

_SAFE_EVENT_PAYLOAD_KEYS = frozenset({
    "attempt",
    "failure_category",
    "queue_name",
    "recovery_reason",
    "recovered",
    "result_snapshot_id",
    "status",
})

_RETRYABLE_ERROR_MARKERS = (
    "TIMEOUT",
    "UNAVAILABLE",
    "QUEUE",
    "PUBLISH",
    "REDIS",
    "MINIO",
    "OBJECT_STORE",
    "PROVIDER",
    "TRANSIENT",
    "WORKER",
    "RATE_LIMIT",
    "TEMPORARY",
)


def _as_datetime(value: Any) -> datetime | None:
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _iso(value: Any) -> str | None:
    parsed = _as_datetime(value)
    return parsed.isoformat() if parsed is not None else None


def _duration_ms(start: Any, end: Any) -> int | None:
    start_dt = _as_datetime(start)
    end_dt = _as_datetime(end)
    if start_dt is None or end_dt is None:
        return None
    return max(0, int((end_dt - start_dt).total_seconds() * 1000))


def is_stale_active_turn(
    turn: Mapping[str, Any],
    *,
    now: datetime | None = None,
    stale_after_seconds: int = 900,
) -> bool:
    """Return whether an active Turn has exceeded the recovery observation window."""

    status = str(turn.get("status") or "")
    if status not in {
        item.value
        for item in (
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
        )
    }:
        return False
    updated_at = _as_datetime(turn.get("updated_at"))
    if updated_at is None:
        return False
    observed_at = _as_datetime(now) or datetime.now(timezone.utc)
    return (observed_at - updated_at).total_seconds() >= max(1, stale_after_seconds)


def classify_failure(
    status: str | ResearchTurnStatus,
    error_code: str | None = None,
    *,
    stale: bool = False,
) -> LifecycleFailureCategory:
    """Classify a failure without changing the persisted status machine."""

    value = status.value if isinstance(status, ResearchTurnStatus) else str(status)
    if value == ResearchTurnStatus.CANCELED.value:
        return LifecycleFailureCategory.CANCELLED
    if stale and value in {
        item.value
        for item in (
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
        )
    }:
        return LifecycleFailureCategory.RECOVERABLE
    code = str(error_code or "").upper()
    if any(marker in code for marker in _RETRYABLE_ERROR_MARKERS):
        return LifecycleFailureCategory.RETRYABLE
    if value in {
        ResearchTurnStatus.FAILED.value,
        ResearchTurnStatus.PLAN_REJECTED.value,
        ResearchTurnStatus.UNSUPPORTED.value,
    }:
        return LifecycleFailureCategory.TERMINAL
    return LifecycleFailureCategory.NONE


def recovery_action(
    status: str | ResearchTurnStatus,
    category: LifecycleFailureCategory,
) -> str:
    value = status.value if isinstance(status, ResearchTurnStatus) else str(status)
    if category == LifecycleFailureCategory.CANCELLED:
        return "preserve_completed_authority_and_stop_downstream_work"
    if category == LifecycleFailureCategory.RECOVERABLE:
        return {
            ResearchTurnStatus.RECEIVED.value: "republish_orchestration_identity",
            ResearchTurnStatus.READY_TO_PLAN.value: "republish_planning_identity",
            ResearchTurnStatus.PLAN_READY.value: "reconcile_existing_job_identity",
            ResearchTurnStatus.QUEUED.value: "reconcile_existing_job_identity",
            ResearchTurnStatus.RESULT_PENDING.value: "republish_result_projection_identity",
            ResearchTurnStatus.RESULT_READY.value: "republish_interpretation_identity",
            ResearchTurnStatus.INTERPRETING.value: "retry_interpretation_from_result",
        }.get(value, "reconcile_from_latest_durable_boundary")
    if category == LifecycleFailureCategory.RETRYABLE:
        return "retry_same_stage_with_existing_identity"
    if category == LifecycleFailureCategory.TERMINAL:
        return "manual_review_or_new_turn"
    return "await_current_stage_owner"


def _latest_stage_event(
    stage: str,
    events: Iterable[Mapping[str, Any]],
) -> Mapping[str, Any] | None:
    accepted = _STAGE_EVENTS.get(stage, frozenset())
    latest: Mapping[str, Any] | None = None
    for event in events:
        if str(event.get("event_type") or event.get("eventType") or "") not in accepted:
            continue
        if latest is None or int(event.get("sequence_no") or event.get("sequenceNo") or 0) >= int(
            latest.get("sequence_no") or latest.get("sequenceNo") or 0
        ):
            latest = event
    return latest


def _first_event_time(events: Iterable[Mapping[str, Any]], *event_types: str) -> datetime | None:
    accepted = set(event_types)
    candidates = [
        _as_datetime(item.get("created_at") or item.get("createdAt"))
        for item in events
        if str(item.get("event_type") or item.get("eventType") or "") in accepted
    ]
    candidates = [item for item in candidates if item is not None]
    return max(candidates) if candidates else None


def _safe_event(event: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if event is None:
        return None
    payload = event.get("payload_json") or event.get("payload") or {}
    return {
        "event_type": str(event.get("event_type") or event.get("eventType") or ""),
        "sequence_no": int(event.get("sequence_no") or event.get("sequenceNo") or 0),
        "created_at": _iso(event.get("created_at") or event.get("createdAt")),
        "payload": {
            key: payload[key]
            for key in sorted(_SAFE_EVENT_PAYLOAD_KEYS)
            if isinstance(payload, Mapping) and key in payload
        },
    }


def build_lifecycle_projection(
    turn: Mapping[str, Any],
    *,
    events: Iterable[Mapping[str, Any]] = (),
    context_snapshot: Mapping[str, Any] | None = None,
    decision: Mapping[str, Any] | None = None,
    resolution: Mapping[str, Any] | None = None,
    capability_plan: Mapping[str, Any] | None = None,
    execution_summary: Mapping[str, Any] | None = None,
    job: Mapping[str, Any] | None = None,
    tool_calls: Iterable[Mapping[str, Any]] = (),
    interpretation: Mapping[str, Any] | None = None,
    report: Mapping[str, Any] | None = None,
    report_generation: Mapping[str, Any] | None = None,
    result_snapshot: Mapping[str, Any] | None = None,
    stale: bool = False,
) -> dict[str, Any]:
    """Build a bounded, secret-free operational view from existing records."""

    event_rows = list(events)
    status = str(turn.get("status") or "UNKNOWN")
    stage, owner = _STAGE_BY_STATUS.get(status, ("UNKNOWN", "unknown"))
    stage_event = _latest_stage_event(stage, event_rows)
    stage_started = (
        stage_event.get("created_at") or stage_event.get("createdAt")
        if stage_event is not None
        else turn.get("updated_at")
    )
    completed_at = turn.get("completed_at") or (
        execution_summary or {}
    ).get("terminal_at")
    category = classify_failure(
        status,
        str(turn.get("error_code") or "") or None,
        stale=stale,
    )
    calls = list(tool_calls)
    attempts = [
        int(item.get("attempt") or 0)
        for item in calls
        if str(item.get("attempt") or "").isdigit()
    ]
    context = None
    if context_snapshot is not None:
        context_manifest = None
        for event in event_rows:
            payload = event.get("payload_json") or event.get("payload") or {}
            candidate = payload.get("context_manifest")
            if isinstance(candidate, Mapping):
                context_manifest = candidate
        context = {
            "snapshot_id": str(context_snapshot.get("id") or ""),
            "fingerprint": context_snapshot.get("context_fingerprint"),
            "active_object_count": len(context_snapshot.get("active_scope_refs_json") or []),
            "selection_count": len(context_snapshot.get("selection_refs_json") or []),
            "scientific_selection_count": len(
                context_snapshot.get("scientific_selections_json") or []
            ),
            "resolved_reference_count": len(
                context_snapshot.get("resolved_references_json") or []
            ),
            "referenced_result_count": len(
                context_snapshot.get("referenced_result_refs_json") or []
            ),
            "unresolved_question_count": len(
                context_snapshot.get("unresolved_questions_json") or []
            ),
            "truncation_state": context_snapshot.get("truncation_state") or "UNKNOWN",
            "compaction_state": context_snapshot.get("compaction_state") or "UNKNOWN",
        }
        context.update(
            context_provenance_summary(
                snapshot=context_snapshot,
                manifest=context_manifest,
            )
        )
    latest_event = max(
        event_rows,
        key=lambda item: int(item.get("sequence_no") or item.get("sequenceNo") or 0),
        default=None,
    )
    queue_published_at = _first_event_time(event_rows, "JOB_QUEUE_PUBLISHED")
    execution_started_at = _first_event_time(
        event_rows,
        "JOB_STARTED",
        "EXECUTION_STEP_STARTED",
    )
    execution_completed_at = _first_event_time(
        event_rows,
        "EXECUTION_SUCCEEDED",
        "EXECUTION_PARTIAL",
        "EXECUTION_FAILED",
        "EXECUTION_CANCELED",
        "JOB_TERMINAL",
    )
    result_ready_at = _first_event_time(
        event_rows,
        "RESULT_READY",
        "RESULT_PROJECTED",
    )
    interpretation_started_at = _first_event_time(event_rows, "INTERPRETATION_STARTED")
    interpretation_ready_at = _first_event_time(event_rows, "INTERPRETATION_READY")
    result_id = result_snapshot.get("id") if result_snapshot is not None else None
    return {
        "status": status,
        "stage": {
            "name": stage,
            "owner": owner,
            "entered_at": _iso(stage_started),
            "duration_ms": _duration_ms(stage_started, completed_at or datetime.now(timezone.utc)),
        },
        "timestamps": {
            "created_at": _iso(turn.get("created_at")),
            "started_at": _iso(turn.get("started_at")),
            "updated_at": _iso(turn.get("updated_at")),
            "completed_at": _iso(completed_at),
            "total_duration_ms": _duration_ms(
                turn.get("created_at"),
                completed_at or datetime.now(timezone.utc),
            ),
        },
        "latency": {
            "queue_wait_ms": _duration_ms(queue_published_at, execution_started_at),
            "execution_ms": _duration_ms(execution_started_at, execution_completed_at),
            "result_projection_ms": _duration_ms(execution_completed_at, result_ready_at),
            "interpretation_ms": _duration_ms(
                interpretation_started_at,
                interpretation_ready_at,
            ),
        },
        "attempt": max(attempts or [1]),
        "context": context,
        "decision": {
            "available": decision is not None,
            "id": str(decision.get("id")) if decision and decision.get("id") else None,
        },
        "resolution": {
            "available": resolution is not None,
            "id": str(resolution.get("id")) if resolution and resolution.get("id") else None,
        },
        "plan": {
            "available": capability_plan is not None or bool(turn.get("analysis_plan_id")),
            "analysis_plan_id": (
                str(turn["analysis_plan_id"]) if turn.get("analysis_plan_id") else None
            ),
            "capability_plan_id": (
                str(capability_plan.get("id"))
                if capability_plan and capability_plan.get("id")
                else None
            ),
        },
        "execution": {
            "job_id": str(job.get("id")) if job and job.get("id") else (
                str(turn.get("job_id")) if turn.get("job_id") else None
            ),
            "job_status": str(job.get("status")) if job and job.get("status") else None,
            "tool_call_count": len(calls),
            "tool_call_attempt_max": max(attempts or [0]),
            "artifact_count": len((execution_summary or {}).get("artifact_refs") or []),
            "result_snapshot_id": str(result_id) if result_id else None,
        },
        "interpretation": {
            "available": interpretation is not None,
            "id": str(interpretation.get("id"))
            if interpretation and interpretation.get("id")
            else None,
            "grounding_status": (
                str(interpretation.get("grounding_status"))
                if interpretation and interpretation.get("grounding_status")
                else None
            ),
        },
        "report": {
            "available": report is not None,
            "id": str(report.get("id")) if report and report.get("id") else None,
            "generation_status": (
                str(report_generation.get("status"))
                if report_generation and report_generation.get("status")
                else None
            ),
            "attempt": int(report_generation.get("attempt_count") or 0)
            if report_generation
            else 0,
        },
        "recovery": {
            "failure_category": category.value,
            "retryable": category
            in {LifecycleFailureCategory.RETRYABLE, LifecycleFailureCategory.RECOVERABLE},
            "recoverable": category == LifecycleFailureCategory.RECOVERABLE,
            "recommended_action": recovery_action(status, category),
            "error_code": str(turn.get("error_code"))
            if turn.get("error_code")
            else None,
            "error_summary_present": bool(turn.get("error_summary")),
            "stale": bool(stale),
        },
        "latest_event": _safe_event(latest_event),
    }


__all__ = [
    "LifecycleFailureCategory",
    "build_lifecycle_projection",
    "classify_failure",
    "is_stale_active_turn",
    "recovery_action",
]
