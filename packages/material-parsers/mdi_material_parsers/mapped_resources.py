from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mdi_artifact_core import (
    PHONON_BAND_SCHEMA_VERSION,
    PHONON_DOS_SCHEMA_VERSION,
    content_hash,
    stable_json_dumps,
    validate_phonon_band,
    validate_phonon_dos,
)
from mdi_schemas import MaterialObjectType

from .models import DetectedFormat, NormalizedObjectDraft, ParseResult


_MAX_MAPPED_PHONON_BYTES = 32_000_000


def map_normalized_phonon_resource(
    path: str | Path,
    *,
    dataset_id: str,
    file_id: str,
    declared_kind: str | None = None,
    declared_contract_version: str | None = None,
) -> ParseResult:
    """Map an explicitly declared canonical phonon resource."""

    file_path = Path(path)
    raw = file_path.read_bytes()
    if not raw or len(raw) > _MAX_MAPPED_PHONON_BYTES:
        raise ValueError("Normalized phonon resource exceeds the approved byte limit.")
    payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    if not isinstance(payload, dict):
        raise ValueError("Normalized phonon resource must be one JSON object.")

    schema_version = payload.get("schema_version")
    if schema_version == PHONON_BAND_SCHEMA_VERSION:
        if declared_kind not in {None, "phonon_band"}:
            raise ValueError("TYPED_PHONON_IMPORT_KIND_MISMATCH")
        validation = validate_phonon_band(payload, raw_size_bytes=len(raw))
        object_type = MaterialObjectType.PhononBand
        kind = "band"
        metadata = {
            "qPointCount": len(payload.get("qpoints", [])),
            "imaginaryFrequencyCount": sum(
                1
                for branch in payload.get("branches", [])
                for value in branch.get("frequencies", [])
                if isinstance(value, (int, float)) and not isinstance(value, bool) and value < 0
            ),
        }
    elif schema_version == PHONON_DOS_SCHEMA_VERSION:
        if declared_kind not in {None, "phonon_dos"}:
            raise ValueError("TYPED_PHONON_IMPORT_KIND_MISMATCH")
        validation = validate_phonon_dos(payload, raw_size_bytes=len(raw))
        object_type = MaterialObjectType.PhononDos
        kind = "dos"
        metadata = {
            "frequencyCount": len(payload.get("frequencies", [])),
            "projected": bool(payload.get("projected_dos")),
        }
    else:
        raise ValueError("Normalized phonon resource schema is not approved.")
    if declared_contract_version is not None and declared_contract_version != schema_version:
        raise ValueError("TYPED_PHONON_IMPORT_CONTRACT_VERSION_MISMATCH")
    if not validation.valid:
        raise ValueError(
            "Normalized phonon resource validation failed: "
            + ", ".join(validation.errors)
        )

    digest = content_hash(stable_json_dumps(payload))
    object_id = f"obj_phonon_{kind}_{digest[:12]}"
    obj = NormalizedObjectDraft(
        id=object_id,
        dataset_id=dataset_id,
        object_type=object_type,
        source_file_ids=[file_id],
        storage_key=f"normalized/{object_id}/phonon.json",
        metadata={
            "detectedFormat": "typed_phonon_import" if declared_kind else "normalized_mapping",
            "declaredImportKind": declared_kind,
            "schemaVersion": schema_version,
            **metadata,
        },
        hash=digest,
        payload=payload,
    )
    return ParseResult(
        file_id=file_id,
        file_path=file_path,
        detected_format=DetectedFormat.json_limited,
        parse_status="success",
        objects=[obj],
    )


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key is not allowed: {key}")
        if key in {"__proto__", "prototype", "constructor"}:
            raise ValueError("Prototype-shaped JSON keys are not allowed.")
        result[key] = value
    return result
