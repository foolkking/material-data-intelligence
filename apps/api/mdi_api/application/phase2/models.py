from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from mdi_api.input_transport import (
    MAX_FILES_PER_UPLOAD,
    MAX_FILE_BYTES,
    MAX_TOTAL_UPLOAD_BYTES,
    UploadFileDeclaration,
)
from mdi_material_parsers import NormalizedObjectDraft, ParseResult
from mdi_schemas import AnalysisPlan, DataProfile


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    projectType: str = "mixed_material_dataset"
    defaultUnits: dict[str, str] = Field(default_factory=dict)
    defaultDownloadFormats: list[str] = Field(default_factory=lambda: ["html", "json", "png", "markdown"])
    llmConfigRef: str | None = None


class InlineUploadFile(BaseModel):
    fileName: str = Field(min_length=1, max_length=240)
    content: str
    importKind: Literal["phonon_band", "phonon_dos"] | None = None
    contractVersion: str | None = Field(default=None, min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_typed_import_declaration(self) -> "InlineUploadFile":
        if self.contractVersion is not None and self.importKind is None:
            raise ValueError("TYPED_PHONON_IMPORT_KIND_REQUIRED")
        return self


class DatasetUploadRequest(BaseModel):
    projectId: str
    datasetName: str = Field(default="Uploaded materials dataset", min_length=1, max_length=160)
    filePaths: list[str] = Field(default_factory=list)
    files: list[InlineUploadFile] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_files(self) -> "DatasetUploadRequest":
        if not self.filePaths and not self.files:
            raise ValueError("filePaths or files must contain at least one file.")
        if len(self.filePaths) + len(self.files) > MAX_FILES_PER_UPLOAD:
            raise ValueError("UPLOAD_FILE_COUNT_CAP_EXCEEDED")
        inline_sizes = [len(item.content.encode("utf-8")) for item in self.files]
        if any(size > MAX_FILE_BYTES for size in inline_sizes):
            raise ValueError("UPLOAD_PER_FILE_BYTE_CAP_EXCEEDED")
        if sum(inline_sizes) > MAX_TOTAL_UPLOAD_BYTES:
            raise ValueError("UPLOAD_TOTAL_BYTE_CAP_EXCEEDED")
        return self


class CreateJobRequest(BaseModel):
    projectId: str
    datasetId: str
    userPrompt: str = "Analyze this materials dataset."
    mode: str = "auto"


@dataclass
class ProjectRecord:
    id: str
    name: str
    project_type: str
    default_units: dict[str, str]
    default_download_formats: list[str]
    llm_config_ref: str | None
    created_at: str = field(default_factory=lambda: _utc_now())

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "projectId": self.id,
            "name": self.name,
            "role": "owner",
            "projectType": self.project_type,
            "defaultUnits": self.default_units,
            "defaultDownloadFormats": self.default_download_formats,
            "llmConfigRef": self.llm_config_ref,
            "status": "created",
            "createdAt": self.created_at,
        }


@dataclass
class DatasetRecord:
    id: str
    project_id: str
    name: str
    files: list[dict[str, Any]]
    parse_results: list[ParseResult]
    objects: list[NormalizedObjectDraft]
    profile: DataProfile
    object_store: dict[str, Any]
    object_refs: dict[str, str]
    normalized_exports: list[dict[str, str]]
    input_transport: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: _utc_now())
    status: str = "profile_ready"

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "datasetId": self.id,
            "projectId": self.project_id,
            "name": self.name,
            "status": self.status,
            "fileCount": len(self.files),
            "objectCount": len(self.objects),
            "profileId": self.profile.profileId,
            "normalizedExports": self.normalized_exports,
            "inputTransport": self.input_transport,
            "createdAt": self.created_at,
        }


@dataclass(frozen=True)
class MaterializedUpload:
    file_id: str
    path: Path
    storage_key: str
    byte_size: int
    sha256: str
    import_kind: Literal["phonon_band", "phonon_dos"] | None = None
    contract_version: str | None = None
    companion_group_id: str | None = None


@dataclass
class UploadSessionFileRecord:
    file_id: str
    declaration: UploadFileDeclaration
    path: Path
    status: str = "declared"


@dataclass
class UploadSessionRecord:
    id: str
    project_id: str
    dataset_name: str
    files: dict[str, UploadSessionFileRecord]
    status: str = "created"
    dataset_id: str | None = None
    created_at: str = field(default_factory=lambda: _utc_now())


@dataclass
class JobRunRecord:
    id: str
    project_id: str
    dataset_id: str
    prompt: str
    plan: AnalysisPlan
    plan_summary: dict[str, Any]
    artifact_ids: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: _utc_now())
    updated_at: str = field(default_factory=lambda: _utc_now())


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = [
    "CreateProjectRequest",
    "InlineUploadFile",
    "DatasetUploadRequest",
    "CreateJobRequest",
    "ProjectRecord",
    "DatasetRecord",
    "MaterializedUpload",
    "UploadSessionFileRecord",
    "UploadSessionRecord",
    "JobRunRecord",
]
