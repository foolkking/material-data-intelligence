from __future__ import annotations

import json

from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
    ReadTimeoutError,
)
from redis.exceptions import AuthenticationError as RedisAuthenticationError
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError
from sqlalchemy.exc import OperationalError

from mdi_api import operations
from mdi_api.config import ApiSettings
from mdi_api.routers import health
from mdi_api.service_failures import classify_service_failure


class _PostgresAuthenticationFailure(Exception):
    pgcode = "28P01"


def test_database_failures_are_typed_without_exception_details() -> None:
    authentication = OperationalError(
        "postgresql://user:db-secret@private-db/mdi",
        {},
        _PostgresAuthenticationFailure("password authentication failed"),
    )
    timeout = OperationalError(
        "postgresql://user:db-secret@private-db/mdi",
        {},
        TimeoutError("private-db timed out"),
    )

    auth_failure = classify_service_failure("database", authentication)
    timeout_failure = classify_service_failure("database", timeout)

    assert auth_failure.as_dict() == {
        "component": "database",
        "code": "DATABASE_AUTHENTICATION",
        "category": "AUTHENTICATION",
        "retryable": False,
        "schemaVersion": "ServiceFailure/1.0",
    }
    assert timeout_failure.code == "DATABASE_TIMEOUT"
    assert timeout_failure.retryable is True
    serialized = json.dumps(
        (auth_failure.as_dict(), timeout_failure.as_dict())
    ).lower()
    assert "secret" not in serialized
    assert "private-db" not in serialized


def test_redis_failures_distinguish_auth_timeout_and_connection() -> None:
    cases = (
        (
            RedisAuthenticationError("redis://:redis-secret@private-cache"),
            "REDIS_AUTHENTICATION",
            False,
        ),
        (
            RedisTimeoutError("private-cache timeout"),
            "REDIS_TIMEOUT",
            True,
        ),
        (
            RedisConnectionError("private-cache unavailable"),
            "REDIS_UNAVAILABLE",
            True,
        ),
    )

    for error, expected_code, expected_retryable in cases:
        failure = classify_service_failure("redis", error)
        assert failure.code == expected_code
        assert failure.retryable is expected_retryable
        assert "private-cache" not in json.dumps(failure.as_dict())


def test_artifact_storage_failures_use_protocol_codes_not_messages() -> None:
    access_denied = ClientError(
        {
            "Error": {
                "Code": "AccessDenied",
                "Message": "minio-secret at private-storage",
            }
        },
        "HeadBucket",
    )
    missing = ClientError(
        {"Error": {"Code": "NoSuchBucket", "Message": "private-bucket"}},
        "HeadBucket",
    )
    cases = (
        (access_denied, "ARTIFACT_STORAGE_AUTHENTICATION", False),
        (missing, "ARTIFACT_STORAGE_NOT_FOUND", False),
        (
            EndpointConnectionError(endpoint_url="http://private-storage"),
            "ARTIFACT_STORAGE_UNAVAILABLE",
            True,
        ),
        (
            ReadTimeoutError(
                endpoint_url="http://private-storage",
                error=TimeoutError("minio-secret"),
            ),
            "ARTIFACT_STORAGE_TIMEOUT",
            True,
        ),
        (
            NoCredentialsError(),
            "ARTIFACT_STORAGE_CONFIGURATION",
            False,
        ),
    )

    failures = []
    for error, expected_code, expected_retryable in cases:
        failure = classify_service_failure("artifactStorage", error)
        assert failure.code == expected_code
        assert failure.retryable is expected_retryable
        failures.append(failure.as_dict())
    serialized = json.dumps(failures).lower()
    assert "secret" not in serialized
    assert "private-storage" not in serialized
    assert "private-bucket" not in serialized


def test_health_and_operations_share_database_failure_projection(
    monkeypatch,
) -> None:
    failure = OperationalError(
        "postgresql://user:db-secret@private-db/mdi",
        {},
        TimeoutError("private-db timed out"),
    )

    def raise_failure(*_args, **_kwargs):
        raise failure

    monkeypatch.setattr(health, "create_engine_from_settings", raise_failure)
    monkeypatch.setattr(operations, "create_engine_from_settings", raise_failure)
    settings = ApiSettings(
        database_url="postgresql+psycopg://user:db-secret@private-db/mdi"
    )

    health_snapshot = health._check_database(settings)
    operations_snapshot = operations._database_snapshot(
        settings,
        operations.OperationsThresholds(),
    )

    assert health_snapshot["reason"] == operations_snapshot["reason"] == (
        "DATABASE_TIMEOUT"
    )
    assert health_snapshot["failure"] == operations_snapshot["failure"]
    serialized = json.dumps((health_snapshot, operations_snapshot)).lower()
    assert "db-secret" not in serialized
    assert "private-db" not in serialized


def test_health_and_operations_share_redis_failure_projection(
    monkeypatch,
) -> None:
    import redis

    def raise_failure(*_args, **_kwargs):
        raise RedisAuthenticationError(
            "redis://:redis-secret@private-cache"
        )

    monkeypatch.setattr(redis.Redis, "from_url", raise_failure)
    settings = ApiSettings(
        queue_backend="redis",
        redis_url="redis://:redis-secret@private-cache/0",
    )

    health_snapshot = health._check_redis(settings)
    operations_snapshot = operations._redis_snapshot(
        settings,
        operations.OperationsThresholds(),
    )

    assert health_snapshot["reason"] == operations_snapshot["reason"] == (
        "REDIS_AUTHENTICATION"
    )
    assert health_snapshot["failure"] == operations_snapshot["failure"]


def test_health_and_operations_share_minio_failure_projection(
    monkeypatch,
) -> None:
    import boto3

    def raise_failure(*_args, **_kwargs):
        raise ClientError(
            {
                "Error": {
                    "Code": "AccessDenied",
                    "Message": "minio-secret at private-storage",
                }
            },
            "HeadBucket",
        )

    monkeypatch.setattr(boto3, "client", raise_failure)
    settings = ApiSettings(
        artifact_backend="minio",
        minio_endpoint="http://private-storage",
        minio_access_key="minio-access",
        minio_secret_key="minio-secret",
    )

    health_snapshot = health._check_artifact_storage(settings)
    operations_snapshot = operations._minio_snapshot(settings)

    assert health_snapshot["reason"] == operations_snapshot["reason"] == (
        "ARTIFACT_STORAGE_AUTHENTICATION"
    )
    assert health_snapshot["failure"] == operations_snapshot["failure"]
