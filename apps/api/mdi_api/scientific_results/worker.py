from __future__ import annotations

import os

from mdi_api.application.scientific_results import project_queued_result
from mdi_api.artifact_storage import create_artifact_storage_from_settings
from mdi_api.config import load_settings
from mdi_api.bootstrap.repository_factory import create_repository_factory
from mdi_api.infrastructure.scientific_results.artifact_loader import load_committed_json_artifact
from mdi_api.infrastructure.scientific_results.service import ScientificResultProjectionService


def run_queued_result_projection(turn_id: str) -> dict:
    """Fresh-process RQ entry point. PostgreSQL and object storage are authority."""

    settings = load_settings()
    storage = create_artifact_storage_from_settings(settings)

    projector = ScientificResultProjectionService(
        create_repository_factory(settings),
        artifact_loader=lambda artifact: load_committed_json_artifact(
            storage, artifact
        ),
    )
    return {
        **project_queued_result(turn_id, projector=projector),
        "process_id": os.getpid(),
    }
