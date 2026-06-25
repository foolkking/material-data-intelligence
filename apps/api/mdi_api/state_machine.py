from __future__ import annotations

from dataclasses import dataclass
from typing import Any


JOB_STATUS_VALUES = {
    "created",
    "queued",
    "running",
    "partial_success",
    "completed",
    "failed",
    "cancel_requested",
    "cancelled",
}

TOOL_CALL_STATUS_VALUES = {
    "planned",
    "running",
    "completed",
    "failed",
    "skipped",
}

JOB_TRANSITIONS: dict[str, set[str]] = {
    "created": {"queued", "running"},
    "queued": {"running", "cancel_requested", "failed"},
    "running": {"partial_success", "completed", "failed", "cancel_requested"},
    "partial_success": {"completed", "failed"},
    "failed": {"queued"},
    "cancel_requested": {"cancelled"},
    "completed": set(),
    "cancelled": set(),
}

TOOL_CALL_TRANSITIONS: dict[str, set[str]] = {
    "planned": {"running", "skipped", "failed"},
    "running": {"completed", "failed", "skipped"},
    "failed": {"planned", "running"},
    "completed": set(),
    "skipped": set(),
}


@dataclass(slots=True)
class InvalidStatusTransition(ValueError):
    entity: str
    current: str
    next: str

    def __str__(self) -> str:
        return f"Invalid {self.entity} status transition: {self.current} -> {self.next}"


def normalize_tool_call_status(value: Any) -> str:
    status = _status_value(value)
    if status == "created":
        return "planned"
    return status


def validate_job_status(value: Any) -> str:
    status = _status_value(value)
    if status not in JOB_STATUS_VALUES:
        raise ValueError(f"Unknown job status: {status}")
    return status


def validate_tool_call_status(value: Any) -> str:
    status = normalize_tool_call_status(value)
    if status not in TOOL_CALL_STATUS_VALUES:
        raise ValueError(f"Unknown tool call status: {status}")
    return status


def validate_job_transition(current: Any, next_status: Any) -> str:
    current_status = validate_job_status(current)
    next_value = validate_job_status(next_status)
    if current_status == next_value:
        return next_value
    if next_value not in JOB_TRANSITIONS[current_status]:
        raise InvalidStatusTransition("job", current_status, next_value)
    return next_value


def validate_tool_call_transition(current: Any, next_status: Any) -> str:
    current_status = validate_tool_call_status(current)
    next_value = validate_tool_call_status(next_status)
    if current_status == next_value:
        return next_value
    if next_value not in TOOL_CALL_TRANSITIONS[current_status]:
        raise InvalidStatusTransition("tool_call", current_status, next_value)
    return next_value


def _status_value(value: Any) -> str:
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)
