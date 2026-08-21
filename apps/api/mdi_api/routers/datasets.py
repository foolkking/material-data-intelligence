from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator
from starlette.requests import Request

from mdi_api.input_transport import CreateUploadSessionRequest, input_transport_capability_contract


_DEFAULT_JSON_LIST_LIMIT = 100_000
_VOLUMETRIC_SOURCE_VALUE_LIMIT = 2_097_152


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


class UpdateDatasetRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    archived: bool | None = None

    @model_validator(mode="after")
    def require_change(self) -> "UpdateDatasetRequest":
        if self.name is None and self.archived is None:
            raise ValueError("At least one Dataset field is required.")
        if self.name is not None:
            self.name = self.name.strip()
            if not self.name:
                raise ValueError("Dataset name cannot be blank.")
        return self


class BulkDatasetActionRequest(BaseModel):
    datasetIds: list[str] = Field(min_length=1, max_length=100)
    action: Literal["archive", "restore"]

    @model_validator(mode="after")
    def unique_datasets(self) -> "BulkDatasetActionRequest":
        self.datasetIds = list(dict.fromkeys(item.strip() for item in self.datasetIds if item.strip()))
        if not self.datasetIds:
            raise ValueError("At least one Dataset is required.")
        return self


def list_datasets_stub() -> list[DatasetSummary]:
    return []


def get_dataset_object_store(dataset_id: str) -> dict[str, object]:
    """Expose canonical parsed source resources for the scientific viewer.

    The runtime object store is an internal execution structure and may contain
    pandas/numpy/Pydantic values. This endpoint deliberately projects only
    canonical, identity-bearing resources into bounded JSON; aliases and
    execution-only helper keys are omitted.
    """
    from mdi_api.phase2_runtime import get_phase2_dataset_object_store

    store = get_phase2_dataset_object_store(dataset_id)
    index = store.get("__mdi_source_resources__") if isinstance(store, dict) else {}
    if not isinstance(index, dict):
        return {"datasetId": dataset_id, "resources": []}
    resources: list[dict[str, object]] = []
    seen: set[str] = set()
    for object_id, identity in index.items():
        if not isinstance(identity, dict):
            continue
        if identity.get("objectType") in {"DataProfile", "Profile"}:
            continue
        canonical_id = str(identity.get("canonicalObjectId") or object_id)
        if canonical_id in seen or identity.get("alias"):
            continue
        value = store.get(canonical_id)
        resources.append({
            "objectId": canonical_id,
            "objectType": identity.get("objectType"),
            "objectHash": identity.get("objectHash"),
            "datasetId": identity.get("datasetId") or dataset_id,
            "payload": _json_safe_resource(value),
        })
        seen.add(canonical_id)
    return {"datasetId": dataset_id, "resources": resources}


def _json_safe_resource(value: object) -> object:
    if hasattr(value, "model_dump"):
        return _json_safe_resource(value.model_dump(mode="json"))
    if hasattr(value, "to_dict") and callable(value.to_dict):
        try:
            return _json_safe_resource(value.to_dict(orient="records"))
        except TypeError:
            return _json_safe_resource(value.to_dict())
    if hasattr(value, "tolist") and callable(value.tolist):
        return _json_safe_resource(value.tolist())
    if isinstance(value, dict):
        is_volumetric_channel = (
            isinstance(value.get("values"), (list, tuple))
            and isinstance(value.get("name"), str)
            and isinstance(value.get("quantity"), str)
        )
        projected: dict[str, object] = {}
        for key, item in list(value.items())[:10000]:
            if key == "values" and is_volumetric_channel:
                projected[str(key)] = _json_safe_resource_list(item, _VOLUMETRIC_SOURCE_VALUE_LIMIT)
            else:
                projected[str(key)] = _json_safe_resource(item)
        return projected
    if isinstance(value, (list, tuple)):
        return _json_safe_resource_list(value, _DEFAULT_JSON_LIST_LIMIT)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _json_safe_resource_list(value: object, limit: int) -> list[object]:
    if not isinstance(value, (list, tuple)):
        return []
    return [_json_safe_resource(item) for item in list(value)[:limit]]


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
