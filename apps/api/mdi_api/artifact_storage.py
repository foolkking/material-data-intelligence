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

    def get_bytes_bounded(self, storage_key: str, *, max_bytes: int) -> bytes:
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

    def get_bytes_bounded(self, storage_key: str, *, max_bytes: int) -> bytes:
        if max_bytes < 0:
            raise ValueError("max_bytes must be non-negative")
        target = self._resolve(storage_key)
        if target.stat().st_size > max_bytes:
            raise ValueError("Artifact exceeds the bounded read limit")
        with target.open("rb") as handle:
            data = handle.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError("Artifact exceeds the bounded read limit")
        return data

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
        region_name: str = "us-east-1",
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
        secure: bool = False,
        client: Any | None = None,
    ) -> None:
        self.bucket = bucket
        self.endpoint_url = endpoint_url
        self.prefix = prefix.strip("/")
        self.region_name = region_name
        self.secure = secure
        self._client = client
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key

    def put_bytes(
        self,
        storage_key: str,
        content: bytes,
        *,
        content_type: str,
        preview_key: str | None = None,
    ) -> ArtifactStorageMetadata:
        client = self._require_client()
        key = self._full_key(storage_key)
        client.put_object(Bucket=self.bucket, Key=key, Body=content, ContentType=content_type)
        return ArtifactStorageMetadata(
            storage_key=key,
            content_type=content_type,
            sha256=_sha256(content),
            size_bytes=len(content),
            preview_key=self._full_key(preview_key) if preview_key else None,
            storage_provider="s3",
            backend="s3",
            bucket=self.bucket,
            endpoint_url=self.endpoint_url,
        )

    def get_bytes(self, storage_key: str) -> bytes:
        client = self._require_client()
        response = client.get_object(Bucket=self.bucket, Key=self._full_key(storage_key))
        body = response["Body"]
        data = body.read()
        return data if isinstance(data, bytes) else bytes(data)

    def get_bytes_bounded(self, storage_key: str, *, max_bytes: int) -> bytes:
        if max_bytes < 0:
            raise ValueError("max_bytes must be non-negative")
        client = self._require_client()
        response = client.get_object(Bucket=self.bucket, Key=self._full_key(storage_key))
        content_length = response.get("ContentLength")
        if isinstance(content_length, int) and content_length > max_bytes:
            body = response.get("Body")
            if hasattr(body, "close"):
                body.close()
            raise ValueError("Artifact exceeds the bounded read limit")
        body = response["Body"]
        try:
            data = body.read(max_bytes + 1)
        finally:
            if hasattr(body, "close"):
                body.close()
        bounded = data if isinstance(data, bytes) else bytes(data)
        if len(bounded) > max_bytes:
            raise ValueError("Artifact exceeds the bounded read limit")
        return bounded

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
        client = self._client
        if client is None and self._can_create_client():
            client = self._require_client()
        if client is None:
            raise NotImplementedError("S3/MinIO existence checks require a configured object-storage client.")
        try:
            client.head_object(Bucket=self.bucket, Key=self._full_key(storage_key))
        except Exception:
            return False
        return True

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
        client = self._client
        if client is None and self._can_create_client():
            client = self._require_client()
        if client is not None:
            url = client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in_sec,
                HttpMethod="GET",
            )
            return ArtifactSignedUrl(
                storage_key=key,
                url=str(url),
                expires_in_sec=expires_in_sec,
                status="ok",
                content_type=content_type,
            )
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
        if self.prefix and (storage_key == self.prefix or storage_key.startswith(f"{self.prefix}/")):
            return storage_key
        return f"{self.prefix}/{storage_key}".strip("/")

    def _can_create_client(self) -> bool:
        return bool(self._access_key_id and self._secret_access_key)

    def _require_client(self) -> Any:
        if self._client is None and self._can_create_client():
            try:
                import boto3
            except ImportError as exc:
                raise NotImplementedError("S3/MinIO live storage requires boto3 to be installed.") from exc
            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self._access_key_id,
                aws_secret_access_key=self._secret_access_key,
                region_name=self.region_name,
                use_ssl=self.secure,
            )
        if self._client is None:
            raise NotImplementedError("S3/MinIO operations require a configured object-storage client.")
        return self._client


def create_minio_artifact_storage_from_settings(settings: Any, *, client: Any | None = None, prefix: str = "") -> S3CompatibleArtifactStorage:
    return S3CompatibleArtifactStorage(
        bucket=settings.minio_bucket,
        endpoint_url=settings.minio_endpoint,
        prefix=prefix,
        region_name=getattr(settings, "s3_region", "us-east-1"),
        access_key_id=settings.minio_access_key,
        secret_access_key=settings.minio_secret_key,
        secure=settings.minio_secure,
        client=client,
    )


def create_artifact_storage_from_settings(settings: Any, *, client: Any | None = None, prefix: str = "") -> ArtifactStorage:
    backend = str(getattr(settings, "artifact_backend", "local") or "local").lower()
    if backend == "minio":
        return create_minio_artifact_storage_from_settings(settings, client=client, prefix=prefix)
    return LocalFileArtifactStorage(getattr(settings, "artifact_root", ".artifacts/phase2"))


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
