from __future__ import annotations

import os
from typing import Any

from mdi_api.config import load_settings


def health() -> dict[str, str]:
    settings = load_settings()
    return {
        "status": "ok",
        "service": "api",
        "environment": settings.environment,
    }


def runtime_health() -> dict[str, Any]:
    settings = load_settings()
    provider = (os.getenv("MDI_LLM_PROVIDER") or "mock").strip().lower() or "mock"
    return {
        "api": _component("ok", service="api", environment=settings.environment),
        "database": _component(
            "ok" if settings.database_url else "unknown",
            backend="postgresql" if "postgres" in settings.database_url else "sqlite",
            reason=None if settings.database_url else "not configured",
        ),
        "redis": _component(
            "ok"
            if settings.queue_backend == "redis" or bool(os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL"))
            else "unknown",
            backend=settings.queue_backend,
            reason=None if settings.queue_backend == "redis" else "not configured",
        ),
        "artifactStorage": _component(
            "ok",
            backend=settings.artifact_backend,
            bucket=settings.minio_bucket if settings.artifact_backend == "minio" else None,
        ),
        "worker": _component(
            "ok" if settings.queue_backend in {"local", "redis"} else "unknown",
            backend=settings.queue_backend,
            reason=None if settings.queue_backend in {"local", "redis"} else "not configured",
        ),
        "llmProvider": _component(
            "ok" if provider in {"mock", "mock_llm", "deterministic", "safe_mock"} else "unknown",
            provider=provider,
            model=os.getenv("MDI_LLM_MODEL") or os.getenv("OPENAI_MODEL") or ("mock" if provider.startswith("mock") else None),
            reason=None if provider.startswith("mock") else "configured provider requires explicit connection test",
        ),
    }


def _component(status: str, **payload: Any) -> dict[str, Any]:
    result = {"status": status}
    for key, value in payload.items():
        if value is not None:
            result[key] = value
    return result
