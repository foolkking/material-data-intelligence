from __future__ import annotations

from pydantic import BaseModel, Field


class DatasetSummary(BaseModel):
    id: str
    datasetId: str | None = None
    projectId: str
    name: str
    status: str
    fileCount: int | None = None
    objectCount: int | None = None
    profileId: str | None = None


class UploadSessionRequest(BaseModel):
    datasetName: str = Field(default="Uploaded materials dataset", min_length=1, max_length=160)
    fileNames: list[str] = Field(default_factory=list)


def list_datasets_stub() -> list[DatasetSummary]:
    return []


def create_upload_session_stub(project_id: str, request: UploadSessionRequest) -> dict[str, object]:
    return {
        "id": "upload_session_local",
        "projectId": project_id,
        "datasetId": "dataset_local",
        "datasetName": request.datasetName,
        "status": "created",
        "files": [
            {"fileId": f"file_{idx + 1:03d}", "name": name, "status": "created"}
            for idx, name in enumerate(request.fileNames)
        ],
    }
