from __future__ import annotations

from mdi_api.config import load_settings


def health() -> dict[str, str]:
    settings = load_settings()
    return {
        "status": "ok",
        "service": "api",
        "environment": settings.environment,
    }
