from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from typing import Any


DEFAULT_QUEUE_NAME = "mdi-jobs"
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
) -> Any:
    from redis import Redis

    connection = Redis.from_url(redis_url)
    connection.ping()
    worker_class = resolve_worker_class(platform_name=platform_name)
    return worker_class(list(queue_names), connection=connection, name=name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Start the Material Data Intelligence RQ worker.")
    parser.add_argument("queues", nargs="*", default=[DEFAULT_QUEUE_NAME])
    parser.add_argument("--url", dest="redis_url")
    parser.add_argument("--name")
    parser.add_argument("--burst", action="store_true")
    parser.add_argument("--max-jobs", type=int)
    parser.add_argument("--max-idle-time", type=int)
    parser.add_argument("--logging-level", default="INFO")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    worker = create_worker(
        redis_url=resolve_redis_url(args.redis_url),
        queue_names=args.queues,
        name=args.name,
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
