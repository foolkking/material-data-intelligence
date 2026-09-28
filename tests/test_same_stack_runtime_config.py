from __future__ import annotations

import pytest

from mdi_api.config import (
    RuntimeConfigurationError,
    database_configuration_declared,
    load_settings,
)
from mdi_workers import worker_entrypoint


RUNTIME_ENV_KEYS = (
    "MDI_RUNTIME_PROFILE",
    "MDI_RUNTIME_BACKEND",
    "DATABASE_URL",
    "MDI_DATABASE_URL",
    "POSTGRES_HOST",
    "MDI_POSTGRES_HOST",
    "MDI_QUEUE_BACKEND",
    "REDIS_URL",
    "MDI_REDIS_URL",
    "MDI_ARTIFACT_BACKEND",
    "MINIO_ENDPOINT",
    "MDI_S3_ENDPOINT_URL",
    "S3_ENDPOINT_URL",
    "MINIO_ACCESS_KEY",
    "MINIO_ROOT_USER",
    "AWS_ACCESS_KEY_ID",
    "MINIO_SECRET_KEY",
    "MINIO_ROOT_PASSWORD",
    "AWS_SECRET_ACCESS_KEY",
    "MINIO_BUCKET",
    "MDI_S3_BUCKET",
    "S3_BUCKET",
    "MINIO_SECURE",
    "MDI_AGENT2_ORCHESTRATION_ENABLED",
    "MDI_AGENT2_QUEUE_NAME",
    "MDI_AGENT2_PLANNING_QUEUE_NAME",
    "MDI_AGENT2_EXECUTION_QUEUE_NAME",
    "MDI_AGENT2_RESULT_QUEUE_NAME",
    "MDI_AGENT2_INTERPRETATION_QUEUE_NAME",
    "MDI_AGENT2_REPORT_QUEUE_NAME",
)


def _same_stack(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in RUNTIME_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    values = {
        "MDI_RUNTIME_PROFILE": "same-stack",
        "MDI_RUNTIME_BACKEND": "postgresql",
        "DATABASE_URL": "postgresql+psycopg://mdi@127.0.0.1:55434/mdi",
        "MDI_QUEUE_BACKEND": "redis",
        "REDIS_URL": "redis://127.0.0.1:6380/0",
        "MDI_ARTIFACT_BACKEND": "minio",
        "MINIO_ENDPOINT": "http://127.0.0.1:9000",
        "MINIO_ACCESS_KEY": "mdi-local",
        "MINIO_SECRET_KEY": "mdi-local-dev",
        "MINIO_BUCKET": "mdi-artifacts",
        "MDI_AGENT2_ORCHESTRATION_ENABLED": "true",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)


def test_same_stack_schema_accepts_one_consistent_explicit_topology(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _same_stack(monkeypatch)

    settings = load_settings()

    assert settings.runtime_profile == "same-stack"
    assert settings.runtime_backend == "postgresql"
    assert settings.queue_backend == "redis"
    assert settings.artifact_backend == "minio"


def test_mdi_postgres_alias_counts_as_explicit_database_authority() -> None:
    assert database_configuration_declared(
        {"MDI_POSTGRES_HOST": "127.0.0.1"}
    )
    assert not database_configuration_declared({})


@pytest.mark.parametrize(
    ("missing", "error"),
    [
        ("DATABASE_URL", "SAME_STACK_POSTGRES_CONFIGURATION_REQUIRED"),
        ("REDIS_URL", "SAME_STACK_REDIS_URL_REQUIRED"),
        ("MINIO_ENDPOINT", "SAME_STACK_MINIO_ENDPOINT_REQUIRED"),
        ("MINIO_ACCESS_KEY", "SAME_STACK_MINIO_ACCESS_KEY_REQUIRED"),
        ("MINIO_SECRET_KEY", "SAME_STACK_MINIO_SECRET_KEY_REQUIRED"),
        ("MINIO_BUCKET", "SAME_STACK_MINIO_BUCKET_REQUIRED"),
    ],
)
def test_same_stack_schema_fails_before_serving_when_authority_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    missing: str,
    error: str,
) -> None:
    _same_stack(monkeypatch)
    monkeypatch.delenv(missing)

    with pytest.raises(RuntimeConfigurationError) as exc:
        load_settings()

    assert error in exc.value.errors


def test_same_stack_schema_rejects_backend_and_alias_conflicts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _same_stack(monkeypatch)
    monkeypatch.setenv("MDI_DATABASE_URL", "sqlite:///wrong.db")
    monkeypatch.setenv("POSTGRES_HOST", "postgres.internal")
    monkeypatch.setenv("MDI_POSTGRES_HOST", "127.0.0.1")
    monkeypatch.setenv("MDI_QUEUE_BACKEND", "local")
    monkeypatch.setenv("MDI_REDIS_URL", "redis://127.0.0.1:6379/0")
    monkeypatch.setenv("MINIO_ROOT_USER", "different-access-key")
    monkeypatch.setenv("MINIO_SECURE", "true")

    with pytest.raises(RuntimeConfigurationError) as exc:
        load_settings()

    assert {
        "DATABASE_URL_CONFLICT",
        "POSTGRES_HOST_CONFLICT",
        "REDIS_URL_CONFLICT",
        "MINIO_ACCESS_KEY_CONFLICT",
        "SAME_STACK_QUEUE_BACKEND_MUST_BE_REDIS",
        "SAME_STACK_MINIO_SECURE_ENDPOINT_CONFLICT",
    }.issubset(exc.value.errors)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("MDI_RUNTIME_PROFILE", "production-ish"),
        ("MDI_RUNTIME_BACKEND", "postgres"),
        ("MDI_QUEUE_BACKEND", "rq"),
        ("MDI_ARTIFACT_BACKEND", "s3-ish"),
    ],
)
def test_typed_backend_choices_reject_unknown_values(
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    value: str,
) -> None:
    for key in RUNTIME_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv(name, value)

    with pytest.raises(RuntimeConfigurationError, match=f"{name}_INVALID"):
        load_settings()


def test_worker_rejects_a_different_redis_namespace_before_consuming(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _same_stack(monkeypatch)
    called = False

    def unexpected_create_worker(**_kwargs: object) -> object:
        nonlocal called
        called = True
        raise AssertionError("worker creation must not be reached")

    monkeypatch.setattr(worker_entrypoint, "create_worker", unexpected_create_worker)

    with pytest.raises(
        RuntimeConfigurationError,
        match="SAME_STACK_WORKER_REDIS_URL_CONFLICT",
    ):
        worker_entrypoint.main(
            ["mdi-jobs", "--url", "redis://127.0.0.1:6379/0", "--burst"]
        )

    assert called is False


def test_worker_accepts_the_same_typed_topology(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _same_stack(monkeypatch)
    monkeypatch.setattr(
        "mdi_api.migration_head.validate_database_migration_head",
        lambda _settings: None,
    )

    class Worker:
        def work(self, **kwargs: object) -> None:
            assert kwargs["burst"] is True

    monkeypatch.setattr(
        worker_entrypoint,
        "create_worker",
        lambda **kwargs: (
            Worker()
            if kwargs["redis_url"] == "redis://127.0.0.1:6380/0"
            and kwargs["queue_names"] == ["mdi-jobs"]
            else (_ for _ in ()).throw(AssertionError("unexpected worker topology"))
        ),
    )

    assert worker_entrypoint.main(
        [
            "mdi-jobs",
            "--url",
            "redis://127.0.0.1:6380/0",
            "--burst",
            "--max-jobs",
            "1",
        ]
    ) == 0


def test_same_stack_worker_rejects_queue_outside_configured_manifest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _same_stack(monkeypatch)
    monkeypatch.setattr(
        worker_entrypoint,
        "create_worker",
        lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("worker creation must not be reached")
        ),
    )

    with pytest.raises(
        RuntimeConfigurationError,
        match="SAME_STACK_WORKER_QUEUE_NOT_IN_MANIFEST",
    ):
        worker_entrypoint.main(
            [
                "mdi-unconfigured-queue",
                "--url",
                "redis://127.0.0.1:6379/13",
                "--burst",
            ]
        )


def test_same_stack_queue_overrides_apply_to_api_and_worker_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _same_stack(monkeypatch)
    monkeypatch.setenv("MDI_AGENT2_EXECUTION_QUEUE_NAME", "mdi-custom-execution")

    settings = load_settings()

    assert settings.agent2_execution_queue_name == "mdi-custom-execution"
