from __future__ import annotations

import os
from uuid import UUID

from mdi_api.artifact_storage import create_artifact_storage_from_settings
from mdi_api.config import load_settings
from mdi_api.database import create_repository_factory
from mdi_api.scientific_results.artifact_loader import load_committed_json_artifact
from mdi_api.scientific_results.service import ScientificResultProjectionService


def run_queued_result_projection(turn_id: str) -> dict:
    """Fresh-process RQ entry point. PostgreSQL and object storage are authority."""

    settings = load_settings()
    storage = create_artifact_storage_from_settings(settings)

    row = ScientificResultProjectionService(
        create_repository_factory(settings),
        artifact_loader=lambda artifact: load_committed_json_artifact(
            storage, artifact
        ),
    ).project_turn(UUID(turn_id))
    return {
        "turn_id": turn_id,
        "snapshot_id": str(row["id"]),
        "status": "RESULT_READY",
        "process_id": os.getpid(),
    }
