from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScientificObjectKind(str, Enum):
    DATASET = "DATASET"
    TABLE = "TABLE"
    COMPOSITION = "COMPOSITION"
    STRUCTURE = "STRUCTURE"
    TRAJECTORY = "TRAJECTORY"
    DIFFRACTION = "DIFFRACTION"
    ELECTRONIC = "ELECTRONIC"
    PHONON = "PHONON"
    VOLUMETRIC = "VOLUMETRIC"
    MODEL_RESULT = "MODEL_RESULT"
    PROPERTY_DATA = "PROPERTY_DATA"
    GENERIC = "GENERIC"


class ScientificObjectAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    PARTIALLY_AVAILABLE = "PARTIALLY_AVAILABLE"
    SOURCE_MISSING = "SOURCE_MISSING"
    INVALID = "INVALID"


class ScientificObjectLifecycle(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    INVALIDATED = "INVALIDATED"


class ScientificObjectRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: UUID
    version_id: UUID
    project_id: str = Field(min_length=1, max_length=64)
    object_type: str = Field(min_length=3, max_length=128)
    display_name: str | None = Field(default=None, max_length=512)


class ScientificObjectVersionRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: UUID
    version_id: UUID
    project_id: str = Field(min_length=1, max_length=64)
    object_type: str = Field(min_length=3, max_length=128)


class StorageRef(BaseModel):
    """Metadata-only reference compatible with existing ArtifactStorage keys."""

    model_config = ConfigDict(extra="forbid")

    storage_backend: str = Field(min_length=1, max_length=32)
    object_key: str = Field(min_length=1, max_length=2048)
    checksum: str = Field(min_length=1, max_length=128)
    media_type: str | None = Field(default=None, max_length=160)
    byte_size: int | None = Field(default=None, ge=0)


class ScientificDatasetFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    operator: Literal["eq", "gt", "gte", "lt", "lte", "in"] = "eq"
    value: Any


class ScientificDatasetQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: list[ScientificDatasetFilter] = Field(default_factory=list, max_length=8)
    sort_by: str | None = Field(default=None, max_length=128, pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    descending: bool = False
    columns: list[str] | None = Field(default=None, max_length=64)
    limit: int = Field(default=100, ge=1, le=500)


class ScientificObjectAdmissionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(min_length=1, max_length=128)
    resource_id: str = Field(min_length=1, max_length=128)
    display_name: str | None = Field(default=None, min_length=1, max_length=512)


class ScientificObjectVersionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(min_length=1, max_length=128)
    resource_id: str = Field(min_length=1, max_length=128)


class ObjectTypeManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    object_type: str = Field(pattern=r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$", max_length=128)
    kind: ScientificObjectKind
    display_name: str = Field(min_length=1, max_length=160)
    schema_versions: list[str] = Field(min_length=1)

    @field_validator("schema_versions")
    @classmethod
    def unique_schema_versions(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("schema_versions must be unique")
        return values


class ScientificObjectVersionContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    scientific_object_id: UUID
    version_no: int = Field(ge=1)
    object_type: str = Field(min_length=3, max_length=128)
    object_schema_version: str = Field(min_length=1, max_length=32)
    source_resource_refs: list[dict[str, Any]]
    parent_object_version_refs: list[ScientificObjectVersionRef]
    semantic_profile_ref: dict[str, Any] | None = None
    normalized_payload_ref: StorageRef
    content_hash: str = Field(min_length=1, max_length=128)
    semantic_hash: str = Field(min_length=1, max_length=128)
    canonical_metadata: dict[str, Any]
    availability_status: ScientificObjectAvailability
    created_at: datetime
