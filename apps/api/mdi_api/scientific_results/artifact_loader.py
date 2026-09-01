from __future__ import annotations

import hashlib
import json
from typing import Any


def load_committed_json_artifact(storage: Any, artifact: dict[str, Any]) -> Any | None:
    """Load only machine-readable committed JSON without trusting media labels alone."""

    content_type = str(
        artifact.get("contentType") or artifact.get("content_type") or ""
    ).lower()
    artifact_type = str(artifact.get("type") or "").lower()
    if artifact_type and "json" not in artifact_type:
        return None
    if "json" not in content_type and "json" not in artifact_type:
        return None

    key = str(artifact.get("storageKey") or artifact.get("storage_key") or "")
    raw = storage.get_bytes(key)
    expected = str(artifact.get("sha256") or artifact.get("contentHash") or "")
    if expected and hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("committed Artifact checksum does not match object storage")
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        # Historical runtime rows can carry a broad application/json media
        # type for markdown. They remain committed evidence but are not
        # projector inputs.
        return None
