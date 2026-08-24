"""Create the Phase 9 acceptance table through the normal upload authority path."""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

from mdi_api.artifact_storage import create_artifact_storage_from_settings
from mdi_api.config import load_settings
from mdi_api.database import create_repository_factory
from mdi_api.input_transport import CreateUploadSessionRequest, UploadFileDeclaration
from mdi_api.phase2_runtime import (
    CreateProjectRequest,
    complete_phase2_upload_session,
    create_phase2_project,
    create_phase2_upload_session,
    put_phase2_upload_session_file,
    reset_phase2_runtime,
)
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.service import ScientificObjectService


PROJECT_NAME = "Agent2 Phase 9 Table Acceptance (Product)"
ACCEPTANCE_USER_ID = "user_product_acceptance"


async def _put(session: dict[str, object], content: bytes) -> None:
    async def chunks():
        yield content

    await put_phase2_upload_session_file(
        str(session["uploadSessionId"]),
        str((session.get("files") or [{}])[0].get("fileId")),
        content_type="application/octet-stream",
        chunks=chunks(),
    )


def main() -> None:
    content = (Path(__file__).parents[1] / "tests" / "fixtures" / "tables" / "ml_results.csv").read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    factory = create_repository_factory()
    project_id = next(
        (
            str(item.get("id") or item.get("projectId"))
            for item in factory.create_repositories().projects.list()
            if item.get("name") == PROJECT_NAME
        ),
        None,
    )
    if not project_id:
        project = create_phase2_project(
            CreateProjectRequest(name=PROJECT_NAME),
            created_by=ACCEPTANCE_USER_ID,
        )
        project_id = str(project.get("projectId") or project.get("id"))
    existing = next(
        (
            item
            for item in factory.create_repositories().datasets.list_for_project(project_id)
            if item.get("name") == "Phase 9 canonical materials table"
        ),
        None,
    )
    if existing is not None:
        dataset = existing
    else:
        runtime = reset_phase2_runtime()
        runtime.ensure_project(project_id, name=PROJECT_NAME)
        session = create_phase2_upload_session(
            project_id,
            CreateUploadSessionRequest(
                datasetName="Phase 9 canonical materials table",
                files=[UploadFileDeclaration(
                    clientFileId="phase9-table",
                    fileName="materials_table.csv",
                    byteSize=len(content),
                    sha256=digest,
                )],
            ),
        )
        asyncio.run(_put(session, content))
        dataset = complete_phase2_upload_session(str(session["uploadSessionId"]))
    service = ScientificObjectService(factory, build_default_object_type_registry())
    logical, version = service.create_table_from_dataset(
        project_id=project_id,
        dataset_id=str(dataset["datasetId"]),
        storage=create_artifact_storage_from_settings(load_settings()),
        display_name="Phase 9 canonical materials table",
        created_by_user_id=ACCEPTANCE_USER_ID,
    )
    print(json.dumps({"projectId": project_id, "dataset": dataset, "object": logical, "version": version}, default=str))


if __name__ == "__main__":
    main()
