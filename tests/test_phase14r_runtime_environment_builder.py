from __future__ import annotations

import os
from pathlib import Path

from mdi_api.config import load_settings
from mdi_api.routers.health import _check_redis
from mdi_workers.worker_entrypoint import resolve_redis_url
from scripts.phase14r_operations_snapshot import _configure_same_stack
from scripts.phase14r_runtime_environment import (
    build_same_stack_environment,
    resolve_same_stack_topology,
)


ROOT = Path(__file__).resolve().parents[1]


def test_shared_builder_emits_consistent_aliases() -> None:
    values = build_same_stack_environment()

    assert values["DATABASE_URL"] == values["MDI_DATABASE_URL"]
    assert values["POSTGRES_HOST"] == values["MDI_POSTGRES_HOST"]
    assert values["POSTGRES_PORT"] == values["MDI_POSTGRES_PORT"]
    assert values["REDIS_URL"] == values["MDI_REDIS_URL"]
    assert values["MINIO_ENDPOINT"] == values["MDI_S3_ENDPOINT_URL"]
    assert values["MINIO_BUCKET"] == values["MDI_S3_BUCKET"]
    assert values["MDI_RUNTIME_PROFILE"] == "same-stack"


def test_one_redis_override_reaches_api_worker_and_operations(
    monkeypatch,
) -> None:
    custom_url = "redis://127.0.0.1:6388/12"
    seen: list[str] = []

    class Client:
        def ping(self) -> None:
            return None

        def info(self, *, section: str) -> dict[str, str]:
            assert section == "server"
            return {"run_id": "test-run", "redis_version": "test-version"}

    def from_url(url: str, **_kwargs: object) -> Client:
        seen.append(url)
        return Client()

    monkeypatch.setenv("MDI_PHASE14R_REDIS_URL", custom_url)
    monkeypatch.setattr("redis.Redis.from_url", from_url)

    _configure_same_stack()
    settings = load_settings()
    health = _check_redis(settings)

    assert settings.redis_url == custom_url
    assert resolve_redis_url() == custom_url
    assert os.environ["MDI_REDIS_URL"] == custom_url
    assert health["status"] == "ok"
    assert seen == [custom_url]


def test_builder_rejects_invalid_qualification_port() -> None:
    try:
        resolve_same_stack_topology({"MDI_PHASE14R_POSTGRES_PORT": "70000"})
    except ValueError as exc:
        assert str(exc) == "MDI_PHASE14R_POSTGRES_PORT_INVALID"
    else:
        raise AssertionError("invalid same-stack port must fail closed")


def test_launchers_and_operations_use_the_shared_builder() -> None:
    api = (ROOT / "scripts" / "phase14r_start_api.ps1").read_text(
        encoding="utf-8"
    )
    workers = (ROOT / "scripts" / "phase14r_start_workers.ps1").read_text(
        encoding="utf-8"
    )
    operations = (
        ROOT / "scripts" / "phase14r_operations_snapshot.py"
    ).read_text(encoding="utf-8")

    assert "phase14r_runtime_environment.py" in api
    assert "phase14r_runtime_environment.py" in workers
    assert "scripts.phase14r_runtime_environment import" in operations
    for source in (api, workers, operations):
        assert 'redis://127.0.0.1:6379/13' not in source
