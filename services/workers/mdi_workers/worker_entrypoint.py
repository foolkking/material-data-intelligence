from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from typing import Any

from mdi_schemas.worker_queues import worker_queue_definition


DEFAULT_QUEUE_NAME = worker_queue_definition("execution").default_name
DEFAULT_REDIS_URL = "redis://localhost:6379/0"


def resolve_worker_class(*, platform_name: str | None = None) -> type[Any]:
    """Return the RQ worker implementation supported by the host platform."""
    from rq import SimpleWorker, Worker

    return SimpleWorker if (platform_name or os.name) == "nt" else Worker


def resolve_redis_url(explicit_url: str | None = None) -> str:
    return (
        explicit_url
        or os.getenv("REDIS_URL")
        or os.getenv("MDI_REDIS_URL")
        or DEFAULT_REDIS_URL
    )


def create_worker(
    *,
    redis_url: str,
    queue_names: Sequence[str],
    name: str | None = None,
    platform_name: str | None = None,
    local_control: bool = False,
) -> Any:
    from redis import Redis

    connection = Redis.from_url(redis_url)
    connection.ping()
    worker_class = resolve_worker_class(platform_name=platform_name)
    from mdi_workers.observability import rq_exception_handler

    extra: dict[str, Any] = {}
    if local_control:
        if not name:
            raise ValueError("Local worker control requires an explicit name")
        from mdi_workers.local_control import LocalControlMixin, local_control_queue
        extra["queue_class"] = local_control_queue(name)
        # A short dequeue interval lets an idle worker observe a drain without
        # signals, forceful termination or a synthetic application job.
        worker_class = type("LocalControlledWorker", (LocalControlMixin, worker_class), {})

    return worker_class(
        list(queue_names),
        connection=connection,
        name=name,
        exception_handlers=[rq_exception_handler],
        **extra,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Start the Material Data Intelligence RQ worker.")
    parser.add_argument("queues", nargs="*", default=[DEFAULT_QUEUE_NAME])
    parser.add_argument("--url", dest="redis_url")
    parser.add_argument("--name")
    parser.add_argument("--burst", action="store_true")
    parser.add_argument("--max-jobs", type=int)
    parser.add_argument("--max-idle-time", type=int)
    parser.add_argument("--logging-level", default="INFO")
    parser.add_argument("--local-control", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    redis_url = resolve_redis_url(args.redis_url)
    if os.getenv("MDI_RUNTIME_PROFILE", "local").strip().lower() == "same-stack":
        from mdi_api.config import load_settings, validate_runtime_settings
        from mdi_api.migration_head import validate_database_migration_head

        settings = load_settings()
        validate_runtime_settings(
            settings,
            process_role="worker",
            worker_redis_url=redis_url,
            worker_queue_names=tuple(args.queues),
        )
        validate_database_migration_head(settings)
    worker = create_worker(
        redis_url=redis_url,
        queue_names=args.queues,
        name=args.name,
        local_control=args.local_control,
    )
    worker.work(
        burst=args.burst,
        logging_level=args.logging_level,
        max_jobs=args.max_jobs,
        max_idle_time=args.max_idle_time,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
