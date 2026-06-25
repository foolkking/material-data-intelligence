from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mdi_schemas import Artifact, ArtifactMetadata, ArtifactType


def stable_json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def content_hash(data: bytes | str | Any) -> str:
    if isinstance(data, bytes):
        raw = data
    elif isinstance(data, str):
        raw = data.encode("utf-8")
    else:
        raw = stable_json_dumps(data).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class ArtifactPayload:
    artifact_type: ArtifactType
    file_name: str
    content: bytes | str | Any
    media_type: str


@dataclass(frozen=True)
class NormalizedObjectExport:
    object_id: str
    storage_key: str
    metadata_key: str
    content_hash: str


class LocalArtifactExporter:
    """Filesystem-backed Artifact exporter for Milestone 0/1.

    The object key is deterministic within a tool call so smoke tests and future
    cache keys can rely on stable paths. Production storage can replace this
    class with S3/MinIO while preserving Artifact metadata shape.
    """

    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)

    def export_payloads(
        self,
        *,
        payloads: list[ArtifactPayload],
        project_id: str,
        dataset_id: str | None,
        job_id: str,
        tool_call_id: str,
        tool_id: str,
        tool_version: str,
        adapter_version: str,
        input_hashes: list[str],
        params_hash: str,
        provenance: dict[str, Any],
    ) -> list[Artifact]:
        artifacts: list[Artifact] = []
        base_dir = self.root_dir / "projects" / project_id / "jobs" / job_id / "tool_calls" / tool_call_id
        base_dir.mkdir(parents=True, exist_ok=True)

        for payload in payloads:
            content_bytes = self._to_bytes(payload.content)
            artifact_id = f"{tool_call_id}-{payload.artifact_type.value}"
            path = base_dir / payload.file_name
            path.write_bytes(content_bytes)
            rel_key = path.relative_to(self.root_dir).as_posix()
            created_at = datetime.now(timezone.utc).isoformat()
            artifact_hash = content_hash(content_bytes)
            artifact = Artifact(
                id=artifact_id,
                projectId=project_id,
                datasetId=dataset_id,
                jobId=job_id,
                toolCallId=tool_call_id,
                type=payload.artifact_type,
                name=payload.file_name,
                version="1",
                storageKey=rel_key,
                sizeBytes=len(content_bytes),
                contentHash=artifact_hash,
                metadata=ArtifactMetadata(
                    toolId=tool_id,
                    toolVersion=tool_version,
                    adapterVersion=adapter_version,
                    inputHashes=input_hashes,
                    paramsHash=params_hash,
                    createdAt=created_at,
                    provenance={**provenance, "mediaType": payload.media_type},
                ),
            )
            artifacts.append(artifact)

        return artifacts

    def export_normalized_object(
        self,
        *,
        object_id: str,
        storage_key: str,
        payload: bytes | str | Any,
        metadata: dict[str, Any],
        project_id: str,
        dataset_id: str,
        provenance: dict[str, Any] | None = None,
    ) -> NormalizedObjectExport:
        base_dir = self.root_dir / "projects" / project_id / "datasets" / dataset_id
        data_path = base_dir / storage_key
        data_path.parent.mkdir(parents=True, exist_ok=True)

        content_bytes = self._to_bytes(payload)
        data_path.write_bytes(content_bytes)
        data_hash = content_hash(content_bytes)

        metadata_path = data_path.parent / "metadata.json"
        metadata_payload = {
            "objectId": object_id,
            "storageKey": data_path.relative_to(self.root_dir).as_posix(),
            "contentHash": data_hash,
            "metadata": metadata,
            "provenance": provenance or {},
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        metadata_path.write_text(stable_json_dumps(metadata_payload), encoding="utf-8")

        return NormalizedObjectExport(
            object_id=object_id,
            storage_key=data_path.relative_to(self.root_dir).as_posix(),
            metadata_key=metadata_path.relative_to(self.root_dir).as_posix(),
            content_hash=data_hash,
        )

    @staticmethod
    def _to_bytes(content: bytes | str | Any) -> bytes:
        if isinstance(content, bytes):
            return content
        if isinstance(content, str):
            return content.encode("utf-8")
        return json.dumps(content, ensure_ascii=False, indent=2, sort_keys=True, default=str).encode("utf-8")
