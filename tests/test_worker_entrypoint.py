from __future__ import annotations

from rq import SimpleWorker, Worker

from mdi_workers.worker_entrypoint import (
    DEFAULT_QUEUE_NAME,
    build_parser,
    resolve_redis_url,
    resolve_worker_class,
)


def test_worker_class_uses_simple_worker_on_windows() -> None:
    assert resolve_worker_class(platform_name="nt") is SimpleWorker


def test_worker_class_preserves_isolated_worker_on_posix() -> None:
    assert resolve_worker_class(platform_name="posix") is Worker


def test_redis_url_resolution_matches_runtime_precedence(monkeypatch) -> None:
    monkeypatch.setenv("REDIS_URL", "redis://primary/0")
    monkeypatch.setenv("MDI_REDIS_URL", "redis://fallback/0")

    assert resolve_redis_url() == "redis://primary/0"
    assert resolve_redis_url("redis://explicit/0") == "redis://explicit/0"


def test_cli_defaults_to_canonical_queue() -> None:
    args = build_parser().parse_args([])

    assert args.queues == [DEFAULT_QUEUE_NAME]
    assert args.burst is False
