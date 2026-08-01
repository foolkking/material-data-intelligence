"""Secret value redaction helpers.

Used by the planner layer and logging to ensure secret values never appear
in plaintext in logs, JobEvents, Artifact metadata, or API responses.
"""

from __future__ import annotations

import os
import re

_CREDENTIAL_KEYS = re.compile(
    r"(api[_-]?key|token|password|secret|credential|authorization)",
    re.IGNORECASE,
)

_CREDENTIAL_VALUE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "sk-***REDACTED***"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]+", re.IGNORECASE), "Bearer ***REDACTED***"),
    (
        re.compile(
            r"(?P<key>api[_-]?key|apikey|deepseek_key|token|password|secret|credential|authorization)"
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


def redact_params_for_log(params: dict[str, object]) -> dict[str, object]:
    """Return a shallow copy of *params* with credential values redacted."""
    safe: dict[str, object] = {}
    for key, value in params.items():
        if is_credential_key(key):
            safe[key] = "***REDACTED***"
        else:
            safe[key] = value
    return safe
