from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from mdi_schemas import MaterialObjectType


class DetectedFormat(str, Enum):
    cif = "cif"
    poscar = "poscar"
    xyz = "xyz"
    extxyz = "extxyz"
    vasp_volumetric = "vasp_volumetric"
    gaussian_cube = "gaussian_cube"
    csv = "csv"
    json_limited = "json_limited"
    archive = "archive"
    unknown = "unknown"


@dataclass(frozen=True)
class NormalizedObjectDraft:
    id: str
    dataset_id: str
    object_type: MaterialObjectType
    source_file_ids: list[str]
    storage_key: str
    metadata: dict[str, Any]
    hash: str
    payload: Any


@dataclass(frozen=True)
class ParseResult:
    file_id: str
    file_path: Path
    detected_format: DetectedFormat
    parse_status: str
    objects: list[NormalizedObjectDraft] = field(default_factory=list)
    error_code: str | None = None
    error_message: str | None = None

    def file_profile(self) -> dict[str, Any]:
        profile = {
            "fileId": self.file_id,
            "fileName": self.file_path.name,
            "detectedFormat": self.detected_format.value,
            "parseStatus": self.parse_status,
        }
        if self.error_code:
            profile["errorCode"] = self.error_code
        if self.error_message:
            profile["errorMessage"] = self.error_message
        return profile

