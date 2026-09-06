from __future__ import annotations

import argparse
import json
import os
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any


SCHEMA_VERSION = "phase14r-worker-registration/1.0"
HEALTHY_STATES = frozenset({"idle", "busy"})


def inspect_worker_registration(
    workers: Iterable[Any],
    *,
    worker_name: str,
    queue_name: str,
    maximum_heartbeat_age_seconds: int,
    now: datetime | None = None,
) -> dict[str, object]:
    observed_at = now or datetime.now(UTC)
    matches = [worker for worker in workers if str(worker.name) == worker_name]
    if len(matches) != 1:
        return _result(
            worker_name=worker_name,
            queue_name=queue_name,
            healthy=False,
            reason=(
                "WORKER_REGISTRATION_MISSING"
                if not matches
                else "WORKER_REGISTRATION_DUPLICATE"
            ),
        )

    worker = matches[0]
    state = str(getattr(worker, "state", None) or "unknown").lower()
    queues = tuple(str(item) for item in worker.queue_names())
    if queues != (queue_name,):
        return _result(
            worker_name=worker_name,
            queue_name=queue_name,
            healthy=False,
            reason="WORKER_REGISTRATION_QUEUE_MISMATCH",
            state=state,
            registered_queues=queues,
        )
    if state not in HEALTHY_STATES:
        return _result(
            worker_name=worker_name,
            queue_name=queue_name,
            healthy=False,
            reason="WORKER_REGISTRATION_STATE_UNHEALTHY",
            state=state,
            registered_queues=queues,
        )

    heartbeat = getattr(worker, "last_heartbeat", None)
    heartbeat_age: float | None = None
    if isinstance(heartbeat, datetime):
        normalized = heartbeat.replace(tzinfo=UTC) if heartbeat.tzinfo is None else heartbeat.astimezone(UTC)
        heartbeat_age = max(0.0, (observed_at - normalized).total_seconds())
        if heartbeat_age > maximum_heartbeat_age_seconds:
            return _result(
                worker_name=worker_name,
                queue_name=queue_name,
                healthy=False,
                reason="WORKER_REGISTRATION_HEARTBEAT_STALE",
                state=state,
                registered_queues=queues,
                heartbeat_age_seconds=heartbeat_age,
            )

    return _result(
        worker_name=worker_name,
        queue_name=queue_name,
        healthy=True,
        reason="WORKER_REGISTRATION_HEALTHY",
        state=state,
        registered_queues=queues,
        heartbeat_age_seconds=heartbeat_age,
    )


def unregister_worker_registration(
    workers: Iterable[Any],
    *,
    worker_name: str,
    queue_name: str,
) -> dict[str, object]:
    matches = [worker for worker in workers if str(worker.name) == worker_name]
    if len(matches) != 1:
        return _result(
            worker_name=worker_name,
            queue_name=queue_name,
            healthy=False,
            reason=(
                "WORKER_REGISTRATION_ALREADY_ABSENT"
                if not matches
                else "WORKER_REGISTRATION_DUPLICATE"
            ),
        )
    worker = matches[0]
    queues = tuple(str(item) for item in worker.queue_names())
    if queues != (queue_name,):
        return _result(
            worker_name=worker_name,
            queue_name=queue_name,
            healthy=False,
            reason="WORKER_REGISTRATION_QUEUE_MISMATCH",
            state=str(getattr(worker, "state", None) or "unknown").lower(),
            registered_queues=queues,
        )
    worker.register_death()
    return _result(
        worker_name=worker_name,
        queue_name=queue_name,
        healthy=True,
        reason="WORKER_REGISTRATION_UNREGISTERED",
        state="dead",
        registered_queues=queues,
    )


def _result(
    *,
    worker_name: str,
    queue_name: str,
    healthy: bool,
    reason: str,
    state: str | None = None,
    registered_queues: tuple[str, ...] = (),
    heartbeat_age_seconds: float | None = None,
) -> dict[str, object]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "healthy": healthy,
        "reason": reason,
        "workerName": worker_name,
        "expectedQueue": queue_name,
        "registeredQueues": list(registered_queues),
        "state": state,
        "heartbeatAgeSeconds": (
            round(heartbeat_age_seconds, 3)
            if heartbeat_age_seconds is not None
            else None
        ),
        "redacted": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker-name", required=True)
    parser.add_argument("--queue", required=True)
    parser.add_argument("--maximum-heartbeat-age-seconds", type=int, default=900)
    parser.add_argument("--unregister", action="store_true")
    args = parser.parse_args(argv)
    if args.maximum_heartbeat_age_seconds < 1:
        parser.error("--maximum-heartbeat-age-seconds must be positive")

    redis_url = os.getenv("MDI_WORKER_REGISTRATION_REDIS_URL", "")
    if not redis_url:
        print(
            json.dumps(
                _result(
                    worker_name=args.worker_name,
                    queue_name=args.queue,
                    healthy=False,
                    reason="WORKER_REGISTRATION_REDIS_URL_REQUIRED",
                ),
                separators=(",", ":"),
            )
        )
        return 2

    from redis import Redis
    from rq import Worker

    connection = Redis.from_url(
        redis_url,
        socket_connect_timeout=2,
        socket_timeout=2,
    )
    workers = Worker.all(connection=connection)
    if args.unregister:
        result = unregister_worker_registration(
            workers,
            worker_name=args.worker_name,
            queue_name=args.queue,
        )
    else:
        result = inspect_worker_registration(
            workers,
            worker_name=args.worker_name,
            queue_name=args.queue,
            maximum_heartbeat_age_seconds=args.maximum_heartbeat_age_seconds,
        )
    print(json.dumps(result, separators=(",", ":")))
    return 0 if result["healthy"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
