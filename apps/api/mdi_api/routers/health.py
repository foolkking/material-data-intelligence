from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mdi_api.config import load_settings
from mdi_api.database import create_engine_from_settings
from mdi_llm import DEEPSEEK_ALLOWED_MODELS, DEEPSEEK_DEFAULT_MODEL

try:
    from sqlalchemy import text
    from sqlalchemy.engine import make_url
except Exception:  # pragma: no cover - import fallback for route listing without deps
    text = None  # type: ignore[assignment]
    make_url = None  # type: ignore[assignment]


def health() -> dict[str, str]:
    settings = load_settings()
    return {
        "status": "ok",
        "service": "api",
        "environment": settings.environment,
    }


def runtime_health() -> dict[str, Any]:
    settings = load_settings()
    provider = "deepseek"
    model = os.getenv("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL
    model_allowed = model in DEEPSEEK_ALLOWED_MODELS
    llm_configured = bool(os.getenv("DEEPSEEK_KEY")) and model_allowed
    database = _check_database(settings)
    redis = _check_redis(settings)
    artifact_storage = _check_artifact_storage(settings)
    return {
        "api": _component("ok", service="api", environment=settings.environment),
        "database": database,
        "redis": redis,
        "artifactStorage": artifact_storage,
        "worker": _component(
            "ok" if settings.queue_backend == "local" or redis["status"] == "ok" else "unknown",
            backend=settings.queue_backend,
            reason=None if settings.queue_backend == "local" or redis["status"] == "ok" else "queue backend not reachable",
        ),
        "llmProvider": _component(
            "ok" if llm_configured else "unknown",
            provider=provider,
            model=model,
            configured=llm_configured,
            reason=None if llm_configured else (
                "DEEPSEEK_MODEL_NOT_ALLOWED" if not model_allowed else "DEEPSEEK_NOT_CONFIGURED"
            ),
        ),
    }


def _check_database(settings: Any) -> dict[str, Any]:
    if not settings.database_url:
        return _component("unknown", backend="unknown", reason="not configured")
    backend = "postgresql" if "postgres" in settings.database_url else "sqlite"
    if backend == "sqlite" and not _sqlite_database_exists(settings.database_url):
        return _component("unknown", backend=backend, reason="not initialized")
    try:
        connect_kwargs: dict[str, Any] = {}
        if backend == "postgresql":
            connect_kwargs["connect_args"] = {"connect_timeout": 2}
        engine = create_engine_from_settings(settings, **connect_kwargs)
        try:
            with engine.connect() as connection:
                if text is not None:
                    connection.execute(text("SELECT 1"))
                else:
                    connection.exec_driver_sql("SELECT 1")
        finally:
            engine.dispose()
        return _component("ok", backend=backend)
    except Exception as exc:
        return _component("unknown", backend=backend, reason=_safe_reason(exc))


def _check_redis(settings: Any) -> dict[str, Any]:
    configured = settings.queue_backend == "redis" or bool(os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL"))
    if not configured:
        return _component("unknown", backend=settings.queue_backend, reason="not configured")
    try:
        import redis

        client = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)
        client.ping()
        return _component("ok", backend="redis")
    except Exception as exc:
        return _component("unknown", backend="redis", reason=_safe_reason(exc))


def _check_artifact_storage(settings: Any) -> dict[str, Any]:
    if settings.artifact_backend == "local":
        return _component("ok", backend="local")
    if settings.artifact_backend != "minio":
        return _component("unknown", backend=settings.artifact_backend, reason="not configured")
    if not settings.minio_access_key or not settings.minio_secret_key:
        return _component("unknown", backend="minio", bucket=settings.minio_bucket, reason="not configured")
    try:
        import boto3
        from botocore.config import Config

        client = boto3.client(
            "s3",
            endpoint_url=settings.minio_endpoint,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            region_name=getattr(settings, "s3_region", "us-east-1"),
            use_ssl=settings.minio_secure,
            config=Config(connect_timeout=2, read_timeout=2, retries={"max_attempts": 0}),
        )
        client.head_bucket(Bucket=settings.minio_bucket)
        return _component("ok", backend="minio", bucket=settings.minio_bucket)
    except Exception as exc:
        return _component("unknown", backend="minio", bucket=settings.minio_bucket, reason=_safe_reason(exc))


def _sqlite_database_exists(database_url: str) -> bool:
    if make_url is None:
        return True
    try:
        url = make_url(database_url)
    except Exception:
        return True
    if url.database in {None, "", ":memory:"}:
        return True
    return Path(str(url.database)).exists()


def _component(status: str, **payload: Any) -> dict[str, Any]:
    result = {"status": status}
    for key, value in payload.items():
        if value is not None:
            result[key] = value
    return result


def _safe_reason(exc: Exception) -> str:
    return exc.__class__.__name__
