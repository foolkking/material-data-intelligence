from __future__ import annotations

import importlib.util
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase14r_worker_registration.py"
SPEC = importlib.util.spec_from_file_location("phase14r_worker_registration", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _worker(
    *,
    name: str = "phase14r-mdi-jobs-next",
    queues: tuple[str, ...] = ("mdi-jobs",),
    state: str = "idle",
    heartbeat: datetime | None = None,
):
    return SimpleNamespace(
        name=name,
        state=state,
        last_heartbeat=heartbeat,
        queue_names=lambda: list(queues),
    )


def test_registration_accepts_exact_queue_and_fresh_heartbeat() -> None:
    now = datetime(2026, 9, 6, 2, 0, tzinfo=UTC)
    result = MODULE.inspect_worker_registration(
        [_worker(heartbeat=now - timedelta(seconds=5))],
        worker_name="phase14r-mdi-jobs-next",
        queue_name="mdi-jobs",
        maximum_heartbeat_age_seconds=90,
        now=now,
    )

    assert result == {
        "schemaVersion": "phase14r-worker-registration/1.0",
        "healthy": True,
        "reason": "WORKER_REGISTRATION_HEALTHY",
        "workerName": "phase14r-mdi-jobs-next",
        "expectedQueue": "mdi-jobs",
        "registeredQueues": ["mdi-jobs"],
        "state": "idle",
        "heartbeatAgeSeconds": 5.0,
        "redacted": True,
    }


def test_registration_fails_closed_for_missing_duplicate_and_wrong_queue() -> None:
    missing = MODULE.inspect_worker_registration(
        [],
        worker_name="phase14r-mdi-jobs-next",
        queue_name="mdi-jobs",
        maximum_heartbeat_age_seconds=90,
    )
    duplicate = MODULE.inspect_worker_registration(
        [_worker(), _worker()],
        worker_name="phase14r-mdi-jobs-next",
        queue_name="mdi-jobs",
        maximum_heartbeat_age_seconds=90,
    )
    wrong_queue = MODULE.inspect_worker_registration(
        [_worker(queues=("mdi-agent-results",))],
        worker_name="phase14r-mdi-jobs-next",
        queue_name="mdi-jobs",
        maximum_heartbeat_age_seconds=90,
    )

    assert missing["reason"] == "WORKER_REGISTRATION_MISSING"
    assert duplicate["reason"] == "WORKER_REGISTRATION_DUPLICATE"
    assert wrong_queue["reason"] == "WORKER_REGISTRATION_QUEUE_MISMATCH"
    assert not missing["healthy"] and not duplicate["healthy"]
    assert wrong_queue["healthy"] is False


def test_registration_rejects_unhealthy_state_and_stale_heartbeat() -> None:
    now = datetime(2026, 9, 6, 2, 0, tzinfo=UTC)
    suspended = MODULE.inspect_worker_registration(
        [_worker(state="suspended", heartbeat=now)],
        worker_name="phase14r-mdi-jobs-next",
        queue_name="mdi-jobs",
        maximum_heartbeat_age_seconds=90,
        now=now,
    )
    stale = MODULE.inspect_worker_registration(
        [_worker(heartbeat=now - timedelta(seconds=91))],
        worker_name="phase14r-mdi-jobs-next",
        queue_name="mdi-jobs",
        maximum_heartbeat_age_seconds=90,
        now=now,
    )

    assert suspended["reason"] == "WORKER_REGISTRATION_STATE_UNHEALTHY"
    assert stale["reason"] == "WORKER_REGISTRATION_HEARTBEAT_STALE"
    assert stale["heartbeatAgeSeconds"] == 91.0


def test_registration_projection_never_contains_connection_identity() -> None:
    result = MODULE.inspect_worker_registration(
        [_worker()],
        worker_name="phase14r-mdi-jobs-next",
        queue_name="mdi-jobs",
        maximum_heartbeat_age_seconds=90,
    )

    serialized = str(result).lower()
    assert "redis" not in serialized
    assert "password" not in serialized
    assert "url" not in serialized


def test_unregister_is_exact_queue_bound_and_invokes_registration_death() -> None:
    calls: list[str] = []
    worker = _worker()
    worker.register_death = lambda: calls.append("death")

    result = MODULE.unregister_worker_registration(
        [worker],
        worker_name="phase14r-mdi-jobs-next",
        queue_name="mdi-jobs",
    )
    wrong_queue = MODULE.unregister_worker_registration(
        [_worker(queues=("mdi-agent-results",))],
        worker_name="phase14r-mdi-jobs-next",
        queue_name="mdi-jobs",
    )

    assert result["reason"] == "WORKER_REGISTRATION_UNREGISTERED"
    assert result["healthy"] is True
    assert calls == ["death"]
    assert wrong_queue["reason"] == "WORKER_REGISTRATION_QUEUE_MISMATCH"
