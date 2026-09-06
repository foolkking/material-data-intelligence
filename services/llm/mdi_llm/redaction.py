"""Secret value redaction helpers.

Used by the planner layer and logging to ensure secret values never appear
in plaintext in logs, JobEvents, Artifact metadata, or API responses.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from typing import Any

_CREDENTIAL_KEYS = re.compile(
    r"(api[_-]?key|access[_-]?key|token|password|secret|credential|authorization|"
    r"session[_-]?token|client[_-]?secret|private[_-]?key)",
    re.IGNORECASE,
)

_CREDENTIAL_VALUE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "sk-***REDACTED***"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]+", re.IGNORECASE), "Bearer ***REDACTED***"),
    (
        re.compile(
            r"(?P<key>api[_-]?key|apikey|deepseek_key|access[_-]?key|token|password|secret|"
            r"credential|authorization|session[_-]?token|client[_-]?secret|private[_-]?key)"
            r"(?P<separator>\s*[:=]\s*)"
            r"(?P<value>\"[^\"\r\n]*\"|'[^'\r\n]*'|[^\s,;\r\n]+)",
            re.IGNORECASE,
        ),
        r"\g<key>\g<separator>***REDACTED***",
    ),
]

_SECRET_ENV_NAMES = (
    "DEEPSEEK_KEY",
    "OPENAI_API_KEY",
    "MDI_LLM_API_KEY",
    "ANTHROPIC_API_KEY",
)

_PRIVATE_PATH = re.compile(
    r"(?:[A-Za-z]:[\\/][^\r\n\"'<>]+|/(?:home|Users|var|tmp|etc|root|opt|mnt|private|workspace|app)/[^\r\n\"'<>]+)"
)
_STORAGE_URL = re.compile(
    r"(?:\bredis(?:s)?://[^\s\"'<>]+|\b(?:s3|https?)://[^\s\"'<>]*(?:minio|amazonaws\.com|[./]s3[./])[^\s\"'<>]*)",
    re.IGNORECASE,
)
_LABELED_STORAGE_URL = re.compile(
    r"(?P<label>\b(?:minio|s3)[_\s-]*(?:endpoint|url)?\s*[:=]?\s*)"
    r"(?P<url>https?://[^\s\"'<>]+)",
    re.IGNORECASE,
)
_STORAGE_AUTHORITY_KEYS = re.compile(
    r"(?:redis[_-]?(?:url|dsn)|minio[_-]?(?:endpoint|url|host|bucket)|"
    r"s3[_-]?(?:endpoint|url|bucket))",
    re.IGNORECASE,
)
_REDACTION_MARKERS = (
    "***REDACTED***",
    "***REDACTED_PATH***",
    "***REDACTED_STORAGE_URL***",
)


def is_credential_key(name: str) -> bool:
    """Return True if the parameter name looks like a credential field."""
    return bool(_CREDENTIAL_KEYS.search(name))


def redact_credential_values(text: str) -> str:
    """Replace known credential patterns in *text* with placeholders."""
    result = text
    for env_name in _SECRET_ENV_NAMES:
        secret = os.environ.get(env_name)
        if secret and len(secret) >= 8:
            result = result.replace(secret, "***REDACTED***")
    for pattern, replacement in _CREDENTIAL_VALUE_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def redact_sensitive_text(text: str) -> str:
    """Redact credentials, storage authorities, and machine-local paths.

    This is intentionally a transport/logging helper.  It does not alter
    scientific numbers, units, identifiers, or evidence references.
    """

    result = redact_credential_values(text)
    result = _LABELED_STORAGE_URL.sub(
        r"\g<label>***REDACTED_STORAGE_URL***",
        result,
    )
    result = _STORAGE_URL.sub("***REDACTED_STORAGE_URL***", result)
    return _PRIVATE_PATH.sub("***REDACTED_PATH***", result)


def redact_sensitive_payload(value: Any, *, key: str | None = None) -> Any:
    """Recursively sanitize a payload before it enters logs or evidence.

    Mapping keys that identify credentials are replaced wholesale; ordinary
    scientific payload fields are retained and string values are sanitized for
    embedded secrets, storage URLs, and local paths.
    """

    if key is not None and (
        is_credential_key(key) or _STORAGE_AUTHORITY_KEYS.search(key)
    ):
        return "***REDACTED***"
    if isinstance(value, Mapping):
        return {
            str(nested_key): redact_sensitive_payload(nested, key=str(nested_key))
            for nested_key, nested in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact_sensitive_payload(item) for item in value]
    if isinstance(value, str):
        return redact_sensitive_text(value)
    return value


def find_sensitive_sentinels(value: Any) -> tuple[str, ...]:
    """Return categories of unredacted sensitive values found in a payload.

    This small sentinel scanner is intended for deterministic tests and
    evidence audits.  Redaction markers are explicitly ignored.
    """

    hits: set[str] = set()

    def visit(item: Any) -> None:
        if isinstance(item, Mapping):
            for nested_key, nested in item.items():
                if is_credential_key(str(nested_key)) and not (
                    isinstance(nested, str) and nested in _REDACTION_MARKERS
                ):
                    hits.add("credential_field")
                if _STORAGE_AUTHORITY_KEYS.search(str(nested_key)) and not (
                    isinstance(nested, str) and nested in _REDACTION_MARKERS
                ):
                    hits.add("storage_authority_field")
                visit(nested)
            return
        if isinstance(item, (list, tuple)):
            for nested in item:
                visit(nested)
            return
        if not isinstance(item, str):
            return
        if _PRIVATE_PATH.search(item):
            hits.add("absolute_path")
        if _STORAGE_URL.search(item):
            hits.add("storage_url")
        if _LABELED_STORAGE_URL.search(item):
            hits.add("storage_url")
        for pattern, _replacement in _CREDENTIAL_VALUE_PATTERNS:
            match = pattern.search(item)
            if match and not any(marker in item for marker in _REDACTION_MARKERS):
                hits.add("credential_value")
                break

    visit(value)
    return tuple(sorted(hits))


def redact_params_for_log(params: dict[str, object]) -> dict[str, object]:
    """Return a shallow copy of *params* with credential values redacted."""
    safe: dict[str, object] = {}
    for key, value in params.items():
        safe[key] = redact_sensitive_payload(value, key=key)
    return safe
