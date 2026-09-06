from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


ServiceComponent = Literal["database", "redis", "artifactStorage"]
FailureCategory = Literal[
    "AUTHENTICATION",
    "CONFIGURATION",
    "NOT_FOUND",
    "TIMEOUT",
    "UNAVAILABLE",
    "UNKNOWN",
]


@dataclass(frozen=True)
class ServiceFailure:
    component: ServiceComponent
    code: str
    category: FailureCategory
    retryable: bool
    schemaVersion: str = "ServiceFailure/1.0"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


_PREFIX = {
    "database": "DATABASE",
    "redis": "REDIS",
    "artifactStorage": "ARTIFACT_STORAGE",
}
_AUTH_SQLSTATES = {"28000", "28P01"}
_AUTH_STORAGE_CODES = {
    "AccessDenied",
    "AccessDeniedException",
    "AllAccessDisabled",
    "AuthorizationHeaderMalformed",
    "ExpiredToken",
    "InvalidAccessKeyId",
    "InvalidToken",
    "SignatureDoesNotMatch",
    "TokenRefreshRequired",
    "401",
    "403",
}
_MISSING_STORAGE_CODES = {
    "NoSuchBucket",
    "NoSuchKey",
    "NotFound",
    "404",
}
_TRANSIENT_STORAGE_CODES = {
    "InternalError",
    "RequestTimeout",
    "RequestTimeoutException",
    "ServiceUnavailable",
    "SlowDown",
    "Throttling",
    "ThrottlingException",
    "500",
    "502",
    "503",
    "504",
}


def classify_service_failure(
    component: ServiceComponent,
    exc: BaseException,
) -> ServiceFailure:
    """Classify infrastructure failures without serializing exception details.

    Exception messages can contain connection URLs, credentials, bucket names,
    filesystem paths, or provider payloads. This projection intentionally uses
    only exception types and bounded protocol error codes.
    """

    if component == "database":
        return _classify_database_failure(exc)
    if component == "redis":
        return _classify_redis_failure(exc)
    return _classify_artifact_storage_failure(exc)


def configuration_service_failure(
    component: ServiceComponent,
) -> ServiceFailure:
    return _failure(component, "CONFIGURATION", retryable=False)


def _classify_database_failure(exc: BaseException) -> ServiceFailure:
    if _contains_timeout(exc):
        return _failure("database", "TIMEOUT", retryable=True)
    sqlstate = _sqlstate(exc)
    if sqlstate in _AUTH_SQLSTATES:
        return _failure("database", "AUTHENTICATION", retryable=False)
    if _contains_connection_failure(exc) or _is_sqlalchemy_operational_error(exc):
        return _failure("database", "UNAVAILABLE", retryable=True)
    return _failure("database", "UNKNOWN", retryable=False)


def _classify_redis_failure(exc: BaseException) -> ServiceFailure:
    try:
        from redis import exceptions as redis_exceptions
    except Exception:  # pragma: no cover - dependency import fallback
        redis_exceptions = None
    if redis_exceptions is not None and isinstance(
        exc,
        (
            redis_exceptions.AuthenticationError,
            redis_exceptions.AuthorizationError,
        ),
    ):
        return _failure("redis", "AUTHENTICATION", retryable=False)
    if _contains_timeout(exc):
        return _failure("redis", "TIMEOUT", retryable=True)
    if (
        redis_exceptions is not None
        and isinstance(exc, redis_exceptions.ConnectionError)
    ) or _contains_connection_failure(exc):
        return _failure("redis", "UNAVAILABLE", retryable=True)
    return _failure("redis", "UNKNOWN", retryable=False)


def _classify_artifact_storage_failure(exc: BaseException) -> ServiceFailure:
    try:
        from botocore.exceptions import (
            ClientError,
            ConnectTimeoutError,
            EndpointConnectionError,
            NoCredentialsError,
            PartialCredentialsError,
            ReadTimeoutError,
        )
    except Exception:  # pragma: no cover - dependency import fallback
        ClientError = ()  # type: ignore[assignment,misc]
        ConnectTimeoutError = ()  # type: ignore[assignment,misc]
        EndpointConnectionError = ()  # type: ignore[assignment,misc]
        NoCredentialsError = ()  # type: ignore[assignment,misc]
        PartialCredentialsError = ()  # type: ignore[assignment,misc]
        ReadTimeoutError = ()  # type: ignore[assignment,misc]

    if isinstance(exc, (NoCredentialsError, PartialCredentialsError)):
        return _failure("artifactStorage", "CONFIGURATION", retryable=False)
    if isinstance(exc, ClientError):
        error = getattr(exc, "response", {}).get("Error", {})
        code = str(error.get("Code") or "")
        if code in _AUTH_STORAGE_CODES:
            return _failure(
                "artifactStorage",
                "AUTHENTICATION",
                retryable=False,
            )
        if code in _MISSING_STORAGE_CODES:
            return _failure("artifactStorage", "NOT_FOUND", retryable=False)
        if code in _TRANSIENT_STORAGE_CODES:
            category: FailureCategory = (
                "TIMEOUT" if "Timeout" in code else "UNAVAILABLE"
            )
            return _failure("artifactStorage", category, retryable=True)
    if isinstance(exc, (ConnectTimeoutError, ReadTimeoutError)):
        return _failure("artifactStorage", "TIMEOUT", retryable=True)
    if isinstance(exc, EndpointConnectionError) or _contains_connection_failure(
        exc
    ):
        return _failure("artifactStorage", "UNAVAILABLE", retryable=True)
    if _contains_timeout(exc):
        return _failure("artifactStorage", "TIMEOUT", retryable=True)
    return _failure("artifactStorage", "UNKNOWN", retryable=False)


def _failure(
    component: ServiceComponent,
    category: FailureCategory,
    *,
    retryable: bool,
) -> ServiceFailure:
    return ServiceFailure(
        component=component,
        code=f"{_PREFIX[component]}_{category}",
        category=category,
        retryable=retryable,
    )


def _exception_chain(exc: BaseException) -> tuple[BaseException, ...]:
    chain: list[BaseException] = []
    current: BaseException | None = exc
    seen: set[int] = set()
    while current is not None and id(current) not in seen and len(chain) < 8:
        chain.append(current)
        seen.add(id(current))
        original = getattr(current, "orig", None)
        current = (
            original
            if isinstance(original, BaseException)
            else current.__cause__ or current.__context__
        )
    return tuple(chain)


def _contains_timeout(exc: BaseException) -> bool:
    for item in _exception_chain(exc):
        if isinstance(item, TimeoutError) or "timeout" in item.__class__.__name__.lower():
            return True
    return False


def _contains_connection_failure(exc: BaseException) -> bool:
    return any(
        isinstance(item, ConnectionError)
        or "connectionerror" in item.__class__.__name__.lower()
        for item in _exception_chain(exc)
    )


def _sqlstate(exc: BaseException) -> str | None:
    for item in _exception_chain(exc):
        value = getattr(item, "sqlstate", None) or getattr(item, "pgcode", None)
        if value:
            return str(value)
    return None


def _is_sqlalchemy_operational_error(exc: BaseException) -> bool:
    try:
        from sqlalchemy.exc import OperationalError
    except Exception:  # pragma: no cover - dependency import fallback
        return False
    return isinstance(exc, OperationalError)
