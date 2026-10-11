from __future__ import annotations

from dataclasses import is_dataclass
from typing import Literal

from pydantic import BaseModel, Field, model_validator
from starlette.requests import Request

from mdi_api.input_transport import CreateUploadSessionRequest, input_transport_capability_contract
from mdi_material_parsers import stable_sample_reference
from mdi_api.scientific_viewers.structure_preview import source_structure_preview


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
    lifecycle: Literal["ACTIVE", "ARCHIVED", "TRASHED"] | None = None

    @model_validator(mode="after")
    def require_change(self) -> "UpdateDatasetRequest":
        if self.name is None and self.archived is None and self.lifecycle is None:
            raise ValueError("At least one Dataset field is required.")
        if self.archived is not None and self.lifecycle is not None:
            raise ValueError("Use either archived compatibility input or lifecycle, not both.")
        if self.name is not None:
            self.name = self.name.strip()
            if not self.name:
                raise ValueError("Dataset name cannot be blank.")
        return self


class BulkDatasetActionRequest(BaseModel):
    datasetIds: list[str] = Field(min_length=1, max_length=100)
    action: Literal["archive", "trash", "restore"]

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
    from mdi_api.infrastructure.phase2.runtime import (
        get_phase2_dataset_object_store,
        get_phase2_dataset_profile,
    )

    store = get_phase2_dataset_object_store(dataset_id)
    dataset_version: str | None = None
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
        value = _canonical_source_payload(store.get(canonical_id))
        object_hash = str(identity.get("objectHash") or "")
        payload = _json_safe_resource(value)
        if identity.get("objectType") == "DataFrame":
            if dataset_version is None:
                dataset_version = str(
                    get_phase2_dataset_profile(dataset_id).get("version") or "unknown"
                )
            payload = _project_dataset_row_identities(
                payload,
                dataset_id=dataset_id,
                dataset_version=dataset_version,
                object_id=canonical_id,
                object_hash=object_hash,
            )
        preview = source_structure_preview(
            payload, object_type=str(identity.get("objectType") or ""), object_id=canonical_id,
            source_hash=object_hash, dataset_id=str(identity.get("datasetId") or dataset_id),
        )
        resources.append({
            "objectId": canonical_id,
            "objectType": identity.get("objectType"),
            "objectHash": object_hash,
            "datasetId": identity.get("datasetId") or dataset_id,
            "payload": payload,
            **({"viewerScene": preview.scene} if preview.scene is not None else {}),
            **({"viewerSceneIssue": preview.issue} if preview.issue else {}),
        })
        seen.add(canonical_id)
    return {"datasetId": dataset_id, "resources": resources}


def _project_dataset_row_identities(
    payload: object,
    *,
    dataset_id: str,
    dataset_version: str,
    object_id: str,
    object_hash: str,
) -> object:
    """Project the Data Profile's durable sample identity into Viewer rows.

    This adds provenance metadata only. Source scientific values remain
    unchanged, while sorting and filtering can preserve exact row identity
    without treating the visual row position as scientific authority.
    """

    if not isinstance(payload, list) or not object_hash:
        return payload
    projected: list[object] = []
    for row_index, item in enumerate(payload):
        if not isinstance(item, dict):
            projected.append(item)
            continue
        row = dict(item)
        explicit = next(
            (
                str(row[key]).strip()
                for key in ("sampleRef", "sample_id", "id")
                if row.get(key) is not None and str(row[key]).strip()
            ),
            None,
        )
        sample_ref = explicit or stable_sample_reference(
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            object_hash=object_hash,
            row_index=row_index,
        )
        row["objectId"] = object_id
        row["sampleRef"] = sample_ref
        row["sampleKey"] = f"{object_id}:{sample_ref}"
        projected.append(row)
    return projected


def _canonical_source_payload(value: object) -> object:
    """Project an execution wrapper to the scientific payload used by viewers.

    Trajectory and volumetric execution stores retain a frozen
    ``NormalizedObjectDraft`` so workers can inspect parser metadata.  That
    wrapper is not the Viewer contract: the browser needs its canonical
    ``payload`` field.  Restrict unwrapping to dataclasses so arbitrary runtime
    mappings cannot smuggle a second payload authority into the response.
    """

    if is_dataclass(value) and hasattr(value, "payload"):
        return getattr(value, "payload")
    return value


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
    from mdi_api.infrastructure.phase2.runtime import create_phase2_upload_session

    return create_phase2_upload_session(project_id, request)


async def put_upload_session_file(session_id: str, file_id: str, request: Request) -> dict[str, object]:
    from mdi_api.infrastructure.phase2.runtime import put_phase2_upload_session_file

    return await put_phase2_upload_session_file(
        session_id,
        file_id,
        content_type=request.headers.get("content-type", ""),
        chunks=request.stream(),
    )


def complete_upload_session(session_id: str) -> dict[str, object]:
    from mdi_api.infrastructure.phase2.runtime import complete_phase2_upload_session

    return complete_phase2_upload_session(session_id)


def cancel_upload_session(session_id: str) -> dict[str, object]:
    from mdi_api.infrastructure.phase2.runtime import cancel_phase2_upload_session

    return cancel_phase2_upload_session(session_id)
