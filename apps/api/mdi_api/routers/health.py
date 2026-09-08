from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from mdi_api.config import load_settings
from mdi_api.infrastructure.persistence.engine import create_engine_from_settings
from mdi_api.service_failures import (
    classify_service_failure,
    configuration_service_failure,
)
from mdi_llm import DEEPSEEK_ALLOWED_MODELS, DEEPSEEK_DEFAULT_MODEL
from mdi_schemas.worker_queues import (
    WORKER_QUEUE_MANIFEST_VERSION,
    configured_worker_queue_names,
)

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
    worker = _component(
        "ok" if settings.queue_backend == "local" or redis["status"] == "ok" else "unknown",
        backend=settings.queue_backend,
        queueManifestVersion=WORKER_QUEUE_MANIFEST_VERSION,
        queues=list(configured_worker_queue_names(settings)),
        reason=None if settings.queue_backend == "local" or redis["status"] == "ok" else "queue backend not reachable",
    )
    llm_provider = _component(
        "ok" if llm_configured else "unknown",
        provider=provider,
        model=model,
        configured=llm_configured,
        reason=None if llm_configured else (
            "DEEPSEEK_MODEL_NOT_ALLOWED" if not model_allowed else "DEEPSEEK_NOT_CONFIGURED"
        ),
    )
    runtime_configuration = _runtime_configuration_fingerprint(
        settings,
        database=database,
        redis=redis,
        artifact_storage=artifact_storage,
        worker=worker,
        llm_provider=llm_provider,
    )
    return {
        "api": _component("ok", service="api", environment=settings.environment),
        "database": database,
        "redis": redis,
        "artifactStorage": artifact_storage,
        "worker": worker,
        "llmProvider": llm_provider,
        "runtimeConfiguration": runtime_configuration,
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
                if text is not None and backend == "postgresql":
                    identity = connection.execute(
                        text("SELECT current_database(), current_user")
                    ).one()
                    probe_identity = {
                        "backend": backend,
                        "database": str(identity[0]),
                        "principal": str(identity[1]),
                    }
                elif text is not None:
                    sqlite_version = connection.execute(
                        text("SELECT sqlite_version()")
                    ).scalar_one()
                    probe_identity = {
                        "backend": backend,
                        "version": str(sqlite_version),
                    }
                else:
                    connection.exec_driver_sql("SELECT 1")
                    probe_identity = {"backend": backend}
        finally:
            engine.dispose()
        return _component(
            "ok",
            backend=backend,
            connectionFingerprint=_fingerprint(probe_identity),
        )
    except Exception as exc:
        failure = classify_service_failure("database", exc)
        return _component(
            "unknown",
            backend=backend,
            reason=failure.code,
            failure=failure.as_dict(),
        )


def _check_redis(settings: Any) -> dict[str, Any]:
    configured = settings.queue_backend == "redis" or bool(os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL"))
    if not configured:
        return _component("unknown", backend=settings.queue_backend, reason="not configured")
    try:
        import redis

        client = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)
        client.ping()
        probe_identity: dict[str, Any] = {
            "backend": "redis",
            "target": _safe_url_identity(settings.redis_url),
        }
        try:
            server = client.info(section="server")
            probe_identity.update(
                {
                    "runId": str(server.get("run_id") or ""),
                    "version": str(server.get("redis_version") or ""),
                }
            )
        except Exception:
            # PING is the availability authority. Some production Redis ACLs
            # intentionally deny INFO; the connection remains healthy and the
            # redacted target identity still distinguishes the configured
            # backend without exposing credentials.
            pass
        return _component(
            "ok",
            backend="redis",
            connectionFingerprint=_fingerprint(probe_identity),
        )
    except Exception as exc:
        failure = classify_service_failure("redis", exc)
        return _component(
            "unknown",
            backend="redis",
            reason=failure.code,
            failure=failure.as_dict(),
        )


def _check_artifact_storage(settings: Any) -> dict[str, Any]:
    if settings.artifact_backend == "local":
        return _component("ok", backend="local")
    if settings.artifact_backend != "minio":
        return _component("unknown", backend=settings.artifact_backend, reason="not configured")
    if not settings.minio_access_key or not settings.minio_secret_key:
        failure = configuration_service_failure("artifactStorage")
        return _component(
            "unknown",
            backend="minio",
            bucket=settings.minio_bucket,
            reason=failure.code,
            failure=failure.as_dict(),
        )
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
        return _component(
            "ok",
            backend="minio",
            bucket=settings.minio_bucket,
            connectionFingerprint=_fingerprint(
                {
                    "backend": "minio",
                    "target": _safe_url_identity(settings.minio_endpoint),
                    "bucket": settings.minio_bucket,
                }
            ),
        )
    except Exception as exc:
        failure = classify_service_failure("artifactStorage", exc)
        return _component(
            "unknown",
            backend="minio",
            bucket=settings.minio_bucket,
            reason=failure.code,
            failure=failure.as_dict(),
        )


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


def _runtime_configuration_fingerprint(
    settings: Any,
    *,
    database: dict[str, Any],
    redis: dict[str, Any],
    artifact_storage: dict[str, Any],
    worker: dict[str, Any],
    llm_provider: dict[str, Any],
) -> dict[str, Any]:
    """Return a comparable topology identity without serializing credentials.

    The fingerprint covers both the declared redacted topology and successful
    connection proofs. A changed backend/target therefore changes identity,
    while rotating a password for the same topology does not expose or encode
    that secret into a comparison oracle.
    """

    component_proofs = {
        "database": database.get("connectionFingerprint"),
        "redis": redis.get("connectionFingerprint"),
        "artifactStorage": artifact_storage.get("connectionFingerprint"),
    }
    topology = {
        "schemaVersion": "RuntimeConfigurationFingerprint/1.0",
        "environment": settings.environment,
        "runtimeProfile": settings.runtime_profile,
        "database": {
            "backend": settings.runtime_backend,
            "target": _safe_database_identity(settings.database_url),
        },
        "queue": {
            "backend": settings.queue_backend,
            "target": _safe_url_identity(settings.redis_url),
            "manifestVersion": WORKER_QUEUE_MANIFEST_VERSION,
            "queues": sorted(configured_worker_queue_names(settings)),
        },
        "artifactStorage": {
            "backend": settings.artifact_backend,
            "target": _safe_url_identity(settings.minio_endpoint),
            "bucket": settings.minio_bucket,
        },
        "provider": {
            "provider": llm_provider.get("provider"),
            "model": llm_provider.get("model"),
            "configured": bool(llm_provider.get("configured")),
        },
        "probes": {
            "database": {
                "status": database.get("status"),
                "proof": component_proofs["database"],
            },
            "redis": {
                "status": redis.get("status"),
                "proof": component_proofs["redis"],
            },
            "artifactStorage": {
                "status": artifact_storage.get("status"),
                "proof": component_proofs["artifactStorage"],
            },
            "worker": {
                "status": worker.get("status"),
                "backend": worker.get("backend"),
            },
        },
    }
    return {
        "schemaVersion": "RuntimeConfigurationFingerprint/1.0",
        "fingerprint": _fingerprint(topology),
        "redacted": True,
        "connectionBound": {
            name: bool(component_proofs[name])
            for name in ("database", "redis", "artifactStorage")
        },
    }


def _safe_database_identity(database_url: str) -> dict[str, Any]:
    if make_url is None:
        return {"driver": "unknown"}
    try:
        url = make_url(database_url)
    except Exception:
        return {"driver": "invalid"}
    return {
        "driver": url.drivername,
        "host": url.host or "",
        "port": url.port,
        "database": url.database or "",
        "username": url.username or "",
    }


def _safe_url_identity(value: str) -> dict[str, Any]:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return {"scheme": "invalid"}
    return {
        "scheme": parsed.scheme.lower(),
        "host": parsed.hostname or "",
        "port": parsed.port,
        "path": parsed.path or "",
    }


def _fingerprint(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
