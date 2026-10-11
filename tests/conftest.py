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


def _pytest_scratch_paths(root: Path, local_root: str | None, configured: str | None, temp_root: str | None = None) -> tuple[Path, Path | None]:
    root = root.resolve()
    local = Path(local_root).resolve() if local_root else root.with_name(f"{root.name}.local")
    temporary = Path(temp_root).resolve() if temp_root else local / "tmp"
    scratch = (temporary / "pytest").resolve()
    if scratch.is_relative_to(root) or (not temp_root and not scratch.is_relative_to(local)):
        raise pytest.UsageError("MDI_PYTEST_SCRATCH_MUST_BE_OUTSIDE_REPOSITORY")
    if not configured:
        return scratch, None
    candidate = Path(configured)
    if not candidate.is_absolute():
        candidate = scratch / candidate
    candidate = candidate.resolve()
    # pytest clears an explicit basetemp recursively. Only a strict child of
    # dedicated scratch space is eligible, never the data root or scratch root.
    if candidate == scratch or not candidate.is_relative_to(scratch):
        raise pytest.UsageError("MDI_PYTEST_BASETEMP_MUST_BE_SCRATCH_CHILD")
    return scratch, candidate


def pytest_configure(config: pytest.Config) -> None:
    """Keep temporary test artifacts outside source and persistent service data."""
    scratch, candidate = _pytest_scratch_paths(
        Path(__file__).resolve().parents[1], os.getenv("MDI_LOCAL_ROOT"),
        config.option.basetemp or os.getenv("MDI_PYTEST_CACHE_DIR"),
        os.getenv("MDI_TEMP_ROOT"),
    )
    scratch.mkdir(parents=True, exist_ok=True)
    if candidate is None:
        # Retain pytest's numbered directories, concurrent-run isolation and
        # retention policy instead of reusing one destructively cleared folder.
        os.environ["PYTEST_DEBUG_TEMPROOT"] = str(scratch)
    else:
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

