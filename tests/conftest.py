from __future__ import annotations

import os
from pathlib import Path

import pytest


_SERVICE_RUNTIME_ENVIRONMENT = (
    "MDI_RUNTIME_PROFILE",
    "MDI_RUNTIME_BACKEND",
    "MDI_QUEUE_BACKEND",
    "MDI_ARTIFACT_BACKEND",
    "DATABASE_URL",
    "MDI_DATABASE_URL",
    "MDI_TEST_DATABASE_URL",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "MDI_POSTGRES_HOST",
    "MDI_POSTGRES_PORT",
    "MDI_POSTGRES_DB",
    "MDI_POSTGRES_USER",
    "MDI_POSTGRES_PASSWORD",
    "REDIS_URL",
    "MDI_REDIS_URL",
    "MINIO_ENDPOINT",
    "MINIO_ACCESS_KEY",
    "MINIO_SECRET_KEY",
    "MINIO_BUCKET",
    "MINIO_SECURE",
    "MINIO_ROOT_USER",
    "MINIO_ROOT_PASSWORD",
    "S3_ENDPOINT_URL",
    "S3_BUCKET",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
)


def pytest_configure(config: pytest.Config) -> None:
    """Keep pytest scratch data in a configurable workspace-local directory."""

    root = Path(__file__).resolve().parents[1]
    configured = config.option.basetemp or os.getenv(
        "MDI_PYTEST_CACHE_DIR", ".cache/tooling/pytest"
    )
    candidate = Path(configured)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise pytest.UsageError(
            "MDI_PYTEST_CACHE_OUTSIDE_REPOSITORY"
        ) from exc
    candidate.mkdir(parents=True, exist_ok=True)
    config.option.basetemp = str(candidate)


@pytest.fixture(autouse=True)
def isolate_unit_runtime_environment(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Keep local unit tests independent from a concurrently running stack.

    Service-backed and qualification tests retain the caller-provided real
    topology. Ordinary unit tests start from explicit local defaults and may
    opt into any environment values they need through their own monkeypatch.
    """

    if request.node.get_closest_marker("integration") is not None:
        return
    if request.node.get_closest_marker("qualification") is not None:
        return
    for name in _SERVICE_RUNTIME_ENVIRONMENT:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

