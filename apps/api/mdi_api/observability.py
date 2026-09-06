from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Mapping
from uuid import uuid4

from mdi_llm import redact_sensitive_payload


OBSERVABILITY_EVENT_VERSION = "OperationalExceptionEvent/1.0"
LOCAL_RELEASE = "LOCAL_WORKTREE"
_RELEASE_SHA = re.compile(r"^[0-9a-f]{7,64}$", re.IGNORECASE)
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_CORRELATION_FIELDS = {
    "requestId",
    "projectId",
    "researchSessionId",
    "researchTurnId",
    "jobId",
    "contextManifestId",
    "resultId",
    "reportId",
    "reportGenerationId",
}
_PATH_PARAM_FIELDS = {
    "project_id": "projectId",
    "session_id": "researchSessionId",
    "turn_id": "researchTurnId",
    "job_id": "jobId",
    "context_manifest_id": "contextManifestId",
    "result_id": "resultId",
    "report_id": "reportId",
    "generation_id": "reportGenerationId",
}


def release_sha(environ: Mapping[str, str] | None = None) -> str:
    source = os.environ if environ is None else environ
    for key in ("MDI_RELEASE_SHA", "GITHUB_SHA"):
        candidate = str(source.get(key) or "").strip()
        if _RELEASE_SHA.fullmatch(candidate):
            return candidate.lower()
    return LOCAL_RELEASE


def bounded_identifier(value: object) -> str | None:
    candidate = str(value or "").strip()
    return candidate if _SAFE_ID.fullmatch(candidate) else None


def request_id(value: object | None = None) -> str:
    return bounded_identifier(value) or uuid4().hex


def bounded_correlation(values: Mapping[str, object]) -> dict[str, str]:
    correlation: dict[str, str] = {}
    for key in _CORRELATION_FIELDS:
        safe = bounded_identifier(values.get(key))
        if safe is not None:
            correlation[key] = safe
    return dict(sorted(correlation.items()))


def request_correlation(request: Any) -> dict[str, str]:
    state = getattr(request, "state", None)
    values: dict[str, object] = {
        "requestId": getattr(state, "request_id", None),
        "contextManifestId": (
            getattr(state, "context_manifest_id", None)
            or request.headers.get("x-mdi-context-manifest-id")
        ),
    }
    for source_name, target_name in _PATH_PARAM_FIELDS.items():
        path_value = request.path_params.get(source_name)
        if path_value is not None:
            values[target_name] = path_value
    return bounded_correlation(values)


def exception_event(
    *,
    component: str,
    error: BaseException,
    correlation: Mapping[str, object] | None = None,
    source: str = "unhandled_exception",
    release: str | None = None,
) -> dict[str, object]:
    safe_component = bounded_identifier(component) or "unknown"
    safe_source = bounded_identifier(source) or "unhandled_exception"
    safe_error_type = bounded_identifier(type(error).__name__) or "Exception"
    payload = {
        "schemaVersion": OBSERVABILITY_EVENT_VERSION,
        "source": safe_source,
        "component": safe_component,
        "releaseSha": (
            release.lower()
            if release is not None and _RELEASE_SHA.fullmatch(release)
            else release_sha()
        ),
        "errorType": safe_error_type,
        "correlation": bounded_correlation(correlation or {}),
        "sanitized": True,
    }
    return redact_sensitive_payload(payload)


def log_exception_event(
    logger: logging.Logger,
    *,
    component: str,
    error: BaseException,
    correlation: Mapping[str, object] | None = None,
    source: str = "unhandled_exception",
) -> dict[str, object]:
    payload = exception_event(
        component=component,
        error=error,
        correlation=correlation,
        source=source,
    )
    logger.error(
        "operational_exception %s",
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
    )
    return payload


__all__ = [
    "LOCAL_RELEASE",
    "OBSERVABILITY_EVENT_VERSION",
    "bounded_correlation",
    "bounded_identifier",
    "exception_event",
    "log_exception_event",
    "release_sha",
    "request_correlation",
    "request_id",
]
