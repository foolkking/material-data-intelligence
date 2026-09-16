from __future__ import annotations

import hashlib
import json
import re
from pathlib import PurePath
from typing import Literal

from pydantic import BaseModel, Field, model_validator


INPUT_TRANSPORT_SCHEMA_VERSION = "NormalUserInputTransport/1.0"
UPLOAD_SESSION_SCHEMA_VERSION = "UploadSession/1.0"
MAX_FILES_PER_UPLOAD = 8
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_UPLOAD_BYTES = 128 * 1024 * 1024
MAX_FILENAME_LENGTH = 240
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class UploadFileDeclaration(BaseModel):
    clientFileId: str = Field(min_length=1, max_length=128)
    fileName: str = Field(min_length=1, max_length=MAX_FILENAME_LENGTH)
    byteSize: int = Field(ge=1, le=MAX_FILE_BYTES)
    sha256: str
    importKind: Literal["phonon_band", "phonon_dos"] | None = None
    contractVersion: str | None = Field(default=None, min_length=1, max_length=128)
    companionGroupId: str | None = Field(default=None, min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_declaration(self) -> "UploadFileDeclaration":
        if not SHA256_PATTERN.fullmatch(self.sha256):
            raise ValueError("UPLOAD_SHA256_INVALID")
        if PurePath(self.fileName).name != self.fileName or "/" in self.fileName or "\\" in self.fileName:
            raise ValueError("UPLOAD_FILENAME_PATH_AUTHORITY_FORBIDDEN")
        if self.contractVersion is not None and self.importKind is None:
            raise ValueError("TYPED_IMPORT_KIND_REQUIRED")
        return self


class CreateUploadSessionRequest(BaseModel):
    datasetName: str = Field(default="Uploaded materials dataset", min_length=1, max_length=160)
    files: list[UploadFileDeclaration] = Field(min_length=1, max_length=MAX_FILES_PER_UPLOAD)

    @model_validator(mode="after")
    def validate_bundle(self) -> "CreateUploadSessionRequest":
        client_ids = [item.clientFileId for item in self.files]
        if len(client_ids) != len(set(client_ids)):
            raise ValueError("UPLOAD_CLIENT_FILE_ID_DUPLICATE")
        total_bytes = sum(item.byteSize for item in self.files)
        if total_bytes > MAX_TOTAL_UPLOAD_BYTES:
            raise ValueError("UPLOAD_TOTAL_BYTE_CAP_EXCEEDED")
        return self


def input_transport_capability_contract() -> dict[str, object]:
    contract: dict[str, object] = {
        "schemaVersion": INPUT_TRANSPORT_SCHEMA_VERSION,
        "entryPathId": "planner_workbench.upload_session",
        "requestContract": UPLOAD_SESSION_SCHEMA_VERSION,
        "supportsTextBytes": True,
        "supportsBinaryBytes": True,
        "supportsMultipleResources": True,
        "maxFilesPerSubmission": MAX_FILES_PER_UPLOAD,
        "perFileByteCap": MAX_FILE_BYTES,
        "totalByteCap": MAX_TOTAL_UPLOAD_BYTES,
        "sameDatasetCompanionPolicy": "ATOMIC_SINGLE_UPLOAD_SESSION",
        "roleBindingPolicy": "PARSER_CONTRACT_OR_EXPLICIT_TYPED_IMPORT_ONLY",
        "fileOrderIsSemanticAuthority": False,
        "partialFailurePolicy": "ADMIT_INDEPENDENT_VALID_MEMBERS_AND_DISCLOSE_PARTIAL_ERRORS",
        "supportedImportModes": ["generic_parser", "typed_phonon_band", "typed_phonon_dos"],
        "transport": {
            "declaration": "application/json",
            "fileBody": "application/octet-stream",
            "bytePreservation": "EXACT_SHA256_AND_BYTE_SIZE",
            "filenameAuthority": "METADATA_ONLY",
        },
        "security": {
            "pathTraversalAllowed": False,
            "archiveExecutionAllowed": False,
            "scriptExecutionAllowed": False,
            "clientFilesystemPathAuthority": False,
        },
    }
    encoded = json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {**contract, "semanticHash": hashlib.sha256(encoded).hexdigest()}
