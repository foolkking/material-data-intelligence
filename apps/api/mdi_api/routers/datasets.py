from __future__ import annotations

from pydantic import BaseModel
from starlette.requests import Request

from mdi_api.input_transport import CreateUploadSessionRequest, input_transport_capability_contract


class DatasetSummary(BaseModel):
    id: str
    datasetId: str | None = None
    projectId: str
    name: str
    status: str
    fileCount: int | None = None
    objectCount: int | None = None
    profileId: str | None = None
    createdAt: str | None = None
    updatedAt: str | None = None


def list_datasets_stub() -> list[DatasetSummary]:
    return []


def get_upload_capabilities() -> dict[str, object]:
    return input_transport_capability_contract()


def create_upload_session(project_id: str, request: CreateUploadSessionRequest) -> dict[str, object]:
    from mdi_api.phase2_runtime import create_phase2_upload_session

    return create_phase2_upload_session(project_id, request)


async def put_upload_session_file(session_id: str, file_id: str, request: Request) -> dict[str, object]:
    from mdi_api.phase2_runtime import put_phase2_upload_session_file

    return await put_phase2_upload_session_file(
        session_id,
        file_id,
        content_type=request.headers.get("content-type", ""),
        chunks=request.stream(),
    )


def complete_upload_session(session_id: str) -> dict[str, object]:
    from mdi_api.phase2_runtime import complete_phase2_upload_session

    return complete_phase2_upload_session(session_id)


def cancel_upload_session(session_id: str) -> dict[str, object]:
    from mdi_api.phase2_runtime import cancel_phase2_upload_session

    return cancel_phase2_upload_session(session_id)
