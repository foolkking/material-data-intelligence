from __future__ import annotations

import re
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


ViewerSupport = Literal["PROFESSIONAL", "SUPPORTED", "FALLBACK", "NOT_CURRENTLY_SUPPORTED"]
ViewerPayloadStatus = Literal["READY", "METADATA_ONLY", "SOURCE_MISSING", "INVALIDATED"]


class ScientificViewerDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    viewer_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]+$")
    viewer_version: Literal["1.0"] = "1.0"
    object_type: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
    renderer_key: str = Field(pattern=r"^[a-z][a-z0-9_.-]{1,127}$")
    support: ViewerSupport
    interaction_capabilities: list[str]
    selection_capabilities: list[str]
    maximum_payload_bytes: int = Field(ge=1)
    fallback_policy: str

    @field_validator(
        "interaction_capabilities",
        "selection_capabilities",
        mode="after",
    )
    @classmethod
    def declarative_capabilities_only(cls, value: list[str]) -> list[str]:
        pattern = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
        if any(not pattern.fullmatch(item) for item in value):
            raise ValueError("viewer capabilities must be bounded declarative identifiers")
        return value


class ScientificViewerProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: Literal["1.0"] = "1.0"
    project_id: str
    object_id: UUID
    version_id: UUID
    object_type: str
    object_schema_version: str
    display_name: str
    version_no: int = Field(ge=1)
    is_current_version: bool
    availability_status: str
    viewer: ScientificViewerDescriptor
    payload_status: ViewerPayloadStatus
    payload: Any | None
    canonical_metadata: dict[str, Any]
    source_resource_refs: list[dict[str, Any]]
    content_hash: str
    semantic_hash: str
    payload_bytes: int | None = Field(default=None, ge=0)
    omitted_item_count: int = Field(default=0, ge=0)
    limitations: list[str]
