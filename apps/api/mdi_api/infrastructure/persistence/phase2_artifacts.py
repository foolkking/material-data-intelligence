from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from mdi_schemas import Artifact, ArtifactType


class LocalFileArtifactStore:
    """Small local artifact index over LocalArtifactExporter output."""

    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)
        self.artifacts: dict[str, Artifact] = {}

    def register(self, artifacts: Iterable[Artifact]) -> None:
        for artifact in artifacts:
            self.artifacts[artifact.id] = artifact

    def list_for_job(self, job_id: str) -> list[Artifact]:
        return [artifact for artifact in self.artifacts.values() if artifact.jobId == job_id]

    def get(self, artifact_id: str) -> Artifact:
        try:
            return self.artifacts[artifact_id]
        except KeyError as exc:
            raise LookupError(f"Unknown artifact_id: {artifact_id}") from exc

    def detail(self, artifact_id: str) -> dict[str, Any]:
        artifact = self.get(artifact_id)
        path = self.root_dir / artifact.storageKey
        payload = artifact.model_dump(mode="json")
        payload["artifactId"] = artifact.id
        payload["downloadUrl"] = f"/artifacts/{artifact.id}/download"
        payload["storageProvider"] = payload.get("storageProvider") or "local"
        payload["contentType"] = payload.get("contentType") or artifact.metadata.provenance.get("mediaType") or content_type_for_name(artifact.name)
        payload["sha256"] = payload.get("sha256") or artifact.contentHash
        payload["createdAt"] = payload.get("createdAt") or artifact.metadata.createdAt
        payload["exists"] = path.exists()
        payload["contentEncoding"] = "missing"
        if path.exists():
            content = path.read_bytes()
            if artifact.type == ArtifactType.preview_png:
                payload["contentEncoding"] = "binary"
            else:
                text = content.decode("utf-8")
                if artifact.name.endswith(".json"):
                    payload["content"] = json.loads(text)
                    payload["contentEncoding"] = "json"
                else:
                    payload["content"] = text
                    payload["contentEncoding"] = "text"
        return payload


def content_type_for_name(name: str) -> str:
    if name.endswith(".json"):
        return "application/json"
    if name.endswith(".html"):
        return "text/html"
    if name.endswith(".md"):
        return "text/markdown"
    if name.endswith(".png"):
        return "image/png"
    if name.endswith(".csv"):
        return "text/csv"
    if name.endswith(".svg"):
        return "image/svg+xml"
    return "application/octet-stream"


__all__ = ["LocalFileArtifactStore", "content_type_for_name"]
