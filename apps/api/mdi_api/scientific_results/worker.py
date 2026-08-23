from __future__ import annotations

import hashlib
import os
from uuid import UUID

from mdi_api.artifact_storage import create_artifact_storage_from_settings
from mdi_api.config import load_settings
from mdi_api.database import create_repository_factory
from mdi_api.scientific_results.service import ScientificResultProjectionService


def run_queued_result_projection(turn_id: str) -> dict:
    """Fresh-process RQ entry point. PostgreSQL and object storage are authority."""

    settings = load_settings()
    storage = create_artifact_storage_from_settings(settings)

    def load_artifact(artifact: dict) -> object | None:
        content_type = str(artifact.get("contentType") or artifact.get("content_type") or "")
        if content_type != "application/json":
            return None
        key = str(artifact.get("storageKey") or artifact.get("storage_key") or "")
        raw = storage.get_bytes(key)
        expected = str(artifact.get("sha256") or artifact.get("contentHash") or "")
        if expected and hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError("committed Artifact checksum does not match object storage")
        import json

        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            # Legacy runtime rows can carry a broad application/json media type
            # for markdown/recipe outputs. They remain committed artifacts, but
            # are not machine-readable projector inputs and must be ignored.
            return None

    row = ScientificResultProjectionService(
        create_repository_factory(settings),
        artifact_loader=load_artifact,
    ).project_turn(UUID(turn_id))
    return {
        "turn_id": turn_id,
        "snapshot_id": str(row["id"]),
        "status": "RESULT_READY",
        "process_id": os.getpid(),
    }
