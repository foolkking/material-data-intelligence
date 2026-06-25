from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Protocol
from urllib.parse import quote


@dataclass(frozen=True)
class ArtifactStorageMetadata:
    storage_key: str
    content_type: str
    sha256: str
    size_bytes: int
    preview_key: str | None = None
    storage_provider: str = "local"
    bucket: str | None = None
    endpoint_url: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    backend: str = "local"

    def __post_init__(self) -> None:
        if self.storage_provider == "local" and self.backend != "local":
            object.__setattr__(self, "storage_provider", self.backend)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ArtifactSignedUrl:
    storage_key: str
    url: str
    method: str = "GET"
    expires_in_sec: int = 900
    status: str = "ok"
    content_type: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ArtifactStorage(Protocol):
    def put_bytes(
        self,
        storage_key: str,
        content: bytes,
        *,
        content_type: str,
        preview_key: str | None = None,
    ) -> ArtifactStorageMetadata:
        ...

    def get_bytes(self, storage_key: str) -> bytes:
        ...

    def put_text(
        self,
        storage_key: str,
        content: str,
        *,
        content_type: str = "text/plain",
        preview_key: str | None = None,
    ) -> ArtifactStorageMetadata:
        ...

    def get_text(self, storage_key: str) -> str:
        ...

    def put_json(
        self,
        storage_key: str,
        content: Any,
        *,
        preview_key: str | None = None,
    ) -> ArtifactStorageMetadata:
        ...

    def get_json(self, storage_key: str) -> Any:
        ...

    def exists(self, storage_key: str) -> bool:
        ...

    def signed_url(
        self,
        storage_key: str,
        *,
        expires_in_sec: int = 900,
        content_type: str | None = None,
    ) -> ArtifactSignedUrl:
        ...


class LocalFileArtifactStorage:
    """Filesystem-backed artifact object storage for local development."""

    def __init__(self, root_dir: str | Path, *, public_base_url: str = "/artifacts/storage") -> None:
        self.root_dir = Path(root_dir)
        self.public_base_url = public_base_url.rstrip("/")

    def put_bytes(
        self,
        storage_key: str,
        content: bytes,
        *,
        content_type: str,
        preview_key: str | None = None,
    ) -> ArtifactStorageMetadata:
        target = self._resolve(storage_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return ArtifactStorageMetadata(
            storage_key=storage_key,
            content_type=content_type,
            sha256=_sha256(content),
            size_bytes=len(content),
            preview_key=preview_key,
            storage_provider="local",
            backend="local",
        )

    def get_bytes(self, storage_key: str) -> bytes:
        return self._resolve(storage_key).read_bytes()

    def put_text(
        self,
        storage_key: str,
        content: str,
        *,
        content_type: str = "text/plain",
        preview_key: str | None = None,
    ) -> ArtifactStorageMetadata:
        return self.put_bytes(
            storage_key,
            content.encode("utf-8"),
            content_type=content_type,
            preview_key=preview_key,
        )

    def get_text(self, storage_key: str) -> str:
        return self.get_bytes(storage_key).decode("utf-8")

    def put_json(
        self,
        storage_key: str,
        content: Any,
        *,
        preview_key: str | None = None,
    ) -> ArtifactStorageMetadata:
        return self.put_text(
            storage_key,
            json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            content_type="application/json",
            preview_key=preview_key,
        )

    def get_json(self, storage_key: str) -> Any:
        return json.loads(self.get_text(storage_key))

    def exists(self, storage_key: str) -> bool:
        return self._resolve(storage_key).exists()

    def describe_existing(
        self,
        storage_key: str,
        *,
        content_type: str,
        preview_key: str | None = None,
    ) -> ArtifactStorageMetadata:
        content = self.get_bytes(storage_key)
        return ArtifactStorageMetadata(
            storage_key=storage_key,
            content_type=content_type,
            sha256=_sha256(content),
            size_bytes=len(content),
            preview_key=preview_key,
            storage_provider="local",
            backend="local",
        )

    def signed_url(
        self,
        storage_key: str,
        *,
        expires_in_sec: int = 900,
        content_type: str | None = None,
    ) -> ArtifactSignedUrl:
        self._validate_key(storage_key)
        encoded_key = quote(storage_key.replace("\\", "/"), safe="/")
        return ArtifactSignedUrl(
            storage_key=storage_key,
            url=f"{self.public_base_url}/{encoded_key}",
            expires_in_sec=expires_in_sec,
            status="local",
            content_type=content_type,
        )

    def _resolve(self, storage_key: str) -> Path:
        self._validate_key(storage_key)
        root = self.root_dir.resolve()
        target = (root / Path(storage_key)).resolve()
        if root != target and root not in target.parents:
            raise ValueError(f"Storage key escapes artifact root: {storage_key}")
        return target

    @staticmethod
    def _validate_key(storage_key: str) -> None:
        key = PurePosixPath(storage_key.replace("\\", "/"))
        if key.is_absolute() or ".." in key.parts:
            raise ValueError(f"Invalid artifact storage key: {storage_key}")


class S3CompatibleArtifactStorage:
    """S3/MinIO-oriented mapping layer without a network client dependency."""

    def __init__(
        self,
        *,
        bucket: str,
        endpoint_url: str | None = None,
        prefix: str = "",
    ) -> None:
        self.bucket = bucket
        self.endpoint_url = endpoint_url
        self.prefix = prefix.strip("/")

    def put_bytes(
        self,
        storage_key: str,
        content: bytes,
        *,
        content_type: str,
        preview_key: str | None = None,
    ) -> ArtifactStorageMetadata:
        raise NotImplementedError("S3/MinIO writes require a configured object-storage client.")

    def get_bytes(self, storage_key: str) -> bytes:
        raise NotImplementedError("S3/MinIO reads require a configured object-storage client.")

    def put_text(
        self,
        storage_key: str,
        content: str,
        *,
        content_type: str = "text/plain",
        preview_key: str | None = None,
    ) -> ArtifactStorageMetadata:
        return self.put_bytes(
            storage_key,
            content.encode("utf-8"),
            content_type=content_type,
            preview_key=preview_key,
        )

    def get_text(self, storage_key: str) -> str:
        return self.get_bytes(storage_key).decode("utf-8")

    def put_json(
        self,
        storage_key: str,
        content: Any,
        *,
        preview_key: str | None = None,
    ) -> ArtifactStorageMetadata:
        return self.put_text(
            storage_key,
            json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            content_type="application/json",
            preview_key=preview_key,
        )

    def get_json(self, storage_key: str) -> Any:
        return json.loads(self.get_text(storage_key))

    def exists(self, storage_key: str) -> bool:
        raise NotImplementedError("S3/MinIO existence checks require a configured object-storage client.")

    def map_object(
        self,
        storage_key: str,
        *,
        content_type: str,
        sha256: str,
        size_bytes: int,
        preview_key: str | None = None,
    ) -> ArtifactStorageMetadata:
        return ArtifactStorageMetadata(
            storage_key=self._full_key(storage_key),
            content_type=content_type,
            sha256=sha256,
            size_bytes=size_bytes,
            preview_key=self._full_key(preview_key) if preview_key else None,
            storage_provider="s3",
            backend="s3",
            bucket=self.bucket,
            endpoint_url=self.endpoint_url,
        )

    def signed_url(
        self,
        storage_key: str,
        *,
        expires_in_sec: int = 900,
        content_type: str | None = None,
    ) -> ArtifactSignedUrl:
        key = self._full_key(storage_key)
        return ArtifactSignedUrl(
            storage_key=key,
            url=f"s3://{self.bucket}/{key}",
            expires_in_sec=expires_in_sec,
            status="not_implemented",
            content_type=content_type,
        )

    def _full_key(self, storage_key: str | None) -> str:
        if storage_key is None:
            raise ValueError("storage_key is required")
        LocalFileArtifactStorage._validate_key(storage_key)
        return f"{self.prefix}/{storage_key}".strip("/")


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
