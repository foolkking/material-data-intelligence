from datetime import datetime, timedelta, timezone
from uuid import uuid4

from mdi_api.research_agent.lifecycle import (
    LifecycleFailureCategory,
    build_lifecycle_projection,
    classify_failure,
    is_stale_active_turn,
    recovery_action,
)


def test_failure_classification_distinguishes_terminal_retryable_recoverable_and_cancelled():
    assert classify_failure("FAILED", "INVALID_AUTHORIZED_SOURCE") == LifecycleFailureCategory.TERMINAL
    assert classify_failure("FAILED", "QUEUE_PUBLISH_FAILED") == LifecycleFailureCategory.RETRYABLE
    assert classify_failure("RUNNING", stale=True) == LifecycleFailureCategory.RECOVERABLE
    assert classify_failure("CANCELED") == LifecycleFailureCategory.CANCELLED


def test_recovery_action_restarts_from_the_latest_durable_boundary():
    assert recovery_action("RESULT_PENDING", LifecycleFailureCategory.RECOVERABLE) == (
        "republish_result_projection_identity"
    )
    assert recovery_action("INTERPRETING", LifecycleFailureCategory.RECOVERABLE) == (
        "retry_interpretation_from_result"
    )
    assert recovery_action("FAILED", LifecycleFailureCategory.TERMINAL) == "manual_review_or_new_turn"


def test_stale_detection_only_marks_active_turns_for_recovery_observation():
    now = datetime(2026, 9, 9, tzinfo=timezone.utc)
    assert is_stale_active_turn(
        {"status": "RUNNING", "updated_at": now - timedelta(minutes=16)},
        now=now,
        stale_after_seconds=900,
    )
    assert not is_stale_active_turn(
        {"status": "COMPLETED", "updated_at": now - timedelta(days=1)},
        now=now,
        stale_after_seconds=900,
    )


def test_lifecycle_projection_is_bounded_and_includes_context_stage_and_safe_event_data():
    now = datetime.now(timezone.utc)
    turn_id = uuid4()
    projection = build_lifecycle_projection(
        {
            "id": turn_id,
            "status": "RESULT_PENDING",
            "created_at": now - timedelta(seconds=4),
            "started_at": now - timedelta(seconds=3),
            "updated_at": now - timedelta(seconds=1),
            "completed_at": now,
            "job_id": "job-1",
            "analysis_plan_id": "plan-1",
        },
        events=[
            {
                "event_type": "RESULT_PENDING",
                "sequence_no": 4,
                "created_at": now - timedelta(seconds=1),
                "payload_json": {
                    "status": "RESULT_PENDING",
                    "attempt": 2,
                    "queue_name": "must-be-bounded",
                    "secret": "must-not-leak",
                },
            }
        ],
        context_snapshot={
            "id": uuid4(),
            "context_fingerprint": "f" * 64,
            "active_scope_refs_json": [{"object_id": "o1"}],
            "selection_refs_json": [{"object_id": "o2"}],
            "scientific_selections_json": [],
            "resolved_references_json": [{"phrase": "sample"}],
            "referenced_result_refs_json": [],
            "unresolved_questions_json": [],
            "truncation_state": "NONE",
            "compaction_state": "NONE",
        },
        tool_calls=[{"id": "call-1", "attempt": 2}],
        stale=True,
    )

    assert projection["stage"] == {
        "name": "RESULT_PENDING",
        "owner": "result_projection",
        "entered_at": (now - timedelta(seconds=1)).isoformat(),
        "duration_ms": 1000,
    }
    assert projection["context"]["active_object_count"] == 1
    assert projection["context"]["selection_count"] == 1
    assert projection["attempt"] == 2
    assert projection["recovery"]["failure_category"] == "RECOVERABLE"
    assert projection["recovery"]["recommended_action"] == "republish_result_projection_identity"
    assert projection["latency"]["queue_wait_ms"] is None
    assert projection["latest_event"]["payload"] == {
        "attempt": 2,
        "queue_name": "must-be-bounded",
        "status": "RESULT_PENDING",
    }
    assert "secret" not in str(projection)
