from __future__ import annotations

import hashlib
import json
from typing import Any
from uuid import UUID

from botocore.exceptions import ClientError

from mdi_api.artifact_storage import ArtifactStorage
from mdi_api.scientific_viewers.registry import ScientificViewerRegistry
from mdi_api.scientific_viewers.schemas import ScientificViewerProjection
from mdi_api.unit_of_work import RepositoryFactory


class ScientificViewerProjectionError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class ScientificViewerProjectionService:
    """Read-only, exact-version projection for product scientific viewers."""

    TABLE_ROW_LIMIT = 500
    TRAJECTORY_FRAME_LIMIT = 256
    VOLUMETRIC_VALUE_LIMIT = 262_144

    def __init__(self, repository_factory: RepositoryFactory, storage: ArtifactStorage, registry: ScientificViewerRegistry) -> None:
        self.repository_factory = repository_factory
        self.storage = storage
        self.registry = registry

    def project(self, object_id: UUID, version_id: UUID) -> ScientificViewerProjection:
        with self.repository_factory.session() as session:
            logical = session.agent2.scientific_objects.get_object(object_id)
            version = session.agent2.scientific_objects.get_version(version_id)
        if version["scientific_object_id"] != logical["id"]:
            raise ScientificViewerProjectionError("VIEWER_VERSION_MISMATCH", "The requested version does not belong to this scientific object.")

        descriptor = self.registry.resolve(str(version["object_type"]))
        availability = str(version["availability_status"])
        payload: Any | None = None
        payload_bytes: int | None = None
        omitted = 0
        limitations: list[str] = []
        payload_status = "READY"
        if availability == "SOURCE_MISSING":
            payload_status = "SOURCE_MISSING"
            limitations.append("The exact source payload is currently unavailable; metadata remains readable.")
        elif availability == "INVALID":
            payload_status = "INVALIDATED"
            limitations.append("This historical object version is invalidated and must not be treated as current scientific evidence.")
        else:
            ref = dict(version["normalized_payload_ref_json"] or {})
            declared_size = ref.get("byte_size")
            if isinstance(declared_size, int) and declared_size > descriptor.maximum_payload_bytes:
                payload_status = "METADATA_ONLY"
                limitations.append("The scientific payload exceeds the bounded interactive preview limit; metadata and authorized download remain available.")
            else:
                try:
                    raw = self.storage.get_bytes_bounded(str(ref.get("object_key") or ""), max_bytes=descriptor.maximum_payload_bytes)
                except FileNotFoundError:
                    payload_status = "SOURCE_MISSING"
                    limitations.append("The exact source payload is no longer available; metadata remains readable and no replacement version was selected.")
                    raw = None
                except ClientError as exc:
                    error_code = str((exc.response or {}).get("Error", {}).get("Code", ""))
                    if error_code in {"NoSuchKey", "NoSuchBucket", "NotFound", "404"}:
                        payload_status = "SOURCE_MISSING"
                        limitations.append("The exact source payload is no longer available in artifact storage; metadata remains readable and no replacement version was selected.")
                        raw = None
                    else:
                        raise
                if raw is None:
                    return ScientificViewerProjection(
                        project_id=str(logical["project_id"]),
                        object_id=logical["id"],
                        version_id=version["id"],
                        object_type=str(version["object_type"]),
                        object_schema_version=str(version["object_schema_version"]),
                        display_name=str(logical["display_name"]),
                        version_no=int(version["version_no"]),
                        is_current_version=logical.get("current_version_id") == version["id"],
                        availability_status=availability,
                        viewer=descriptor,
                        payload_status=payload_status,
                        payload=None,
                        canonical_metadata=dict(version["canonical_metadata_json"] or {}),
                        source_resource_refs=list(version["source_resource_refs_json"] or []),
                        content_hash=str(version["content_hash"]),
                        semantic_hash=str(version["semantic_hash"]),
                        payload_bytes=None,
                        omitted_item_count=omitted,
                        limitations=limitations,
                    )
                payload_bytes = len(raw)
                checksum = hashlib.sha256(raw).hexdigest()
                expected = str(ref.get("checksum") or version["content_hash"])
                if expected and expected != checksum:
                    raise ScientificViewerProjectionError("VIEWER_SOURCE_CHECKSUM_MISMATCH", "The exact source payload failed integrity validation.", 409)
                try:
                    decoded = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ScientificViewerProjectionError("VIEWER_SOURCE_NOT_JSON", "This source requires the safe generic-file fallback.") from exc
                payload, omitted, projection_limitations = self._bounded_projection(str(version["object_type"]), decoded)
                limitations.extend(projection_limitations)

        return ScientificViewerProjection(
            project_id=str(logical["project_id"]),
            object_id=logical["id"],
            version_id=version["id"],
            object_type=str(version["object_type"]),
            object_schema_version=str(version["object_schema_version"]),
            display_name=str(logical["display_name"]),
            version_no=int(version["version_no"]),
            is_current_version=logical.get("current_version_id") == version["id"],
            availability_status=availability,
            viewer=descriptor,
            payload_status=payload_status,
            payload=payload,
            canonical_metadata=dict(version["canonical_metadata_json"] or {}),
            source_resource_refs=list(version["source_resource_refs_json"] or []),
            content_hash=str(version["content_hash"]),
            semantic_hash=str(version["semantic_hash"]),
            payload_bytes=payload_bytes,
            omitted_item_count=omitted,
            limitations=limitations,
        )

    def _bounded_projection(self, object_type: str, payload: Any) -> tuple[Any, int, list[str]]:
        if object_type in {"materials.dataset", "materials.table"}:
            return self._bounded_rows(payload)
        if object_type == "trajectory.atomic":
            return self._bounded_frames(payload)
        if object_type in {"volumetric.field", "volumetric.charge_density"}:
            return self._bounded_volume(payload)
        return payload, 0, []

    def _bounded_rows(self, payload: Any) -> tuple[Any, int, list[str]]:
        rows = payload if isinstance(payload, list) else payload.get("rows") if isinstance(payload, dict) else None
        if not isinstance(rows, list) or len(rows) <= self.TABLE_ROW_LIMIT:
            return payload, 0, []
        omitted = len(rows) - self.TABLE_ROW_LIMIT
        limited = rows[: self.TABLE_ROW_LIMIT]
        projected = {**payload, "rows": limited} if isinstance(payload, dict) else limited
        return projected, omitted, [f"Interactive table preview is limited to {self.TABLE_ROW_LIMIT} rows; {omitted} rows are omitted from this view."]

    def _bounded_frames(self, payload: Any) -> tuple[Any, int, list[str]]:
        if not isinstance(payload, dict) or not isinstance(payload.get("frames"), list) or len(payload["frames"]) <= self.TRAJECTORY_FRAME_LIMIT:
            return payload, 0, []
        omitted = len(payload["frames"]) - self.TRAJECTORY_FRAME_LIMIT
        return {**payload, "frames": payload["frames"][: self.TRAJECTORY_FRAME_LIMIT], "total_frames": len(payload["frames"])}, omitted, [f"Interactive trajectory preview is limited to {self.TRAJECTORY_FRAME_LIMIT} frames; the exact source remains unchanged."]

    def _bounded_volume(self, payload: Any) -> tuple[Any, int, list[str]]:
        if not isinstance(payload, dict):
            return payload, 0, []
        key = next((item for item in ("values", "data", "grid_values") if isinstance(payload.get(item), list)), None)
        if key is None or len(payload[key]) <= self.VOLUMETRIC_VALUE_LIMIT:
            return payload, 0, []
        omitted = len(payload[key])
        projected = {name: value for name, value in payload.items() if name != key}
        projected["value_count"] = omitted
        return projected, omitted, ["The volumetric scalar array is not serialized into the JSON viewer projection; use the bounded field renderer or authorized source stream."]


__all__ = ["ScientificViewerProjectionError", "ScientificViewerProjectionService"]
