"""Bounded public reference provenance from the immutable Result snapshot."""
from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from mdi_schemas.project_planning import PlatformReferenceDescription
from mdi_schemas.parameter_values import ParameterValue
from .contracts import ScientificResultBundle


_ORIGINS = {"PLATFORM_REFERENCE", "USER_PARAMETERS", "USER_TEXT_DATA", "IDEAL_MODEL"}


class ParameterInputRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tool_call_id: str = Field(min_length=1, max_length=128)
    tool_id: str = Field(min_length=1, max_length=128)
    input_origin: Literal["USER_PARAMETERS", "USER_TEXT_DATA", "IDEAL_MODEL"]
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    resolved_parameters: dict[Annotated[str, Field(max_length=128)], ParameterValue] = Field(max_length=64)


def project_reference_context(bundle: ScientificResultBundle) -> dict[str, Any] | None:
    provenance = bundle.provenance.model_dump(mode="json")
    origin = provenance.get("input_origin")
    if not provenance.get("reference_sources") and origin not in _ORIGINS | {"MIXED"}:
        return None
    if (provenance.get("execution_scope") != "PROJECT"
            or origin not in _ORIGINS | {"MIXED"}
            or bundle.source_object_refs or provenance.get("source_object_version_ids")):
        raise ValueError("Reference provenance cannot claim sample authority.")
    raw = provenance.get("reference_sources", [])
    if not isinstance(raw, list) or len(raw) > 8:
        raise ValueError("Reference provenance exceeds its declared bound.")
    sources = [PlatformReferenceDescription.model_validate(item) for item in raw]
    identities = [source.referenceId for source in sources]
    if identities != sorted(set(identities)):
        raise ValueError("Reference provenance identities must be unique and sorted.")
    origins = provenance.get("input_origins", [origin])
    if (not isinstance(origins, list) or not origins or len(origins) > 4
            or any(item not in _ORIGINS for item in origins) or origins != sorted(set(origins))
            or (origin == "MIXED") != (len(origins) > 1)
            or (origin != "MIXED" and origins != [origin])):
        raise ValueError("Project input origins are inconsistent.")
    raw_parameters = provenance.get("parameter_inputs", [])
    if not isinstance(raw_parameters, list) or len(raw_parameters) > 8:
        raise ValueError("Parameter input provenance exceeds its bound.")
    parameters = [ParameterInputRecord.model_validate(item) for item in raw_parameters]
    calls = [item.tool_call_id for item in parameters]
    if len(calls) != len(set(calls)) or any(item.tool_call_id not in bundle.provenance.tool_call_ids or item.input_origin not in origins for item in parameters):
        raise ValueError("Parameter inputs do not match their result calls and origins.")
    # Read the saved description, never the latest installed reference version.
    return {"execution_scope": "PROJECT", "input_origin": origin,
            "input_origins": origins,
            "reference_sources": [source.model_dump(mode="json", exclude_none=True) for source in sources],
            **({"parameter_inputs": [item.model_dump(mode="json") for item in parameters]} if parameters else {})}
