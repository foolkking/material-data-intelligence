from __future__ import annotations

from typing import Any

from mdi_api.research_agent.schemas import RequirementOrigin
from mdi_schemas import ParameterProvenance


_ADVANCED_PREFIXES = (
    "minimum_",
    "maximum_",
    "alpha_",
    "origin_",
    "max_origins",
)
_SYSTEM_ONLY_PARAMETERS = frozenset(
    {"batch_size", "chunk_size", "worker_count", "retry_count", "timeout", "timeout_sec"}
)


def parameter_unit(parameter: str) -> str | None:
    if parameter.endswith("_angstrom"):
        return "angstrom"
    if parameter.endswith("_time_ps") or parameter.endswith("_duration_ps"):
        return "picosecond"
    if parameter.endswith("_fs"):
        return "femtosecond"
    if parameter.endswith("_ev"):
        return "electron_volt"
    return None


def parameter_authority(parameter: str, origin: str) -> str:
    if parameter in _SYSTEM_ONLY_PARAMETERS:
        return "SYSTEM_ONLY"
    if origin == RequirementOrigin.CONTEXT_RESOLVED.value:
        return "SOURCE_LOCKED"
    if origin == RequirementOrigin.AGENT_DERIVED.value:
        return "AUTO_DERIVED"
    if parameter.startswith(_ADVANCED_PREFIXES):
        return "ADVANCED_EDITABLE"
    return "USER_EDITABLE"


def parameter_origin(origin: str) -> str:
    return {
        RequirementOrigin.USER_EXPLICIT.value: "USER_SPECIFIED",
        RequirementOrigin.CONTEXT_RESOLVED.value: "SOURCE_FACT",
        RequirementOrigin.AGENT_DERIVED.value: "DETERMINISTIC_DERIVATION",
        "TOOL_DEFAULT": "TOOL_DEFAULT",
        "SCIENTIFIC_PRESET": "SCIENTIFIC_PRESET",
        "SYSTEM_POLICY": "SYSTEM_POLICY",
    }[origin]


def resolved_parameter_provenance(
    *,
    tool_id: str,
    tool_version: str,
    parameter: str,
    value: Any,
    source_origin: str,
    source_identity: str,
) -> ParameterProvenance:
    return ParameterProvenance(
        parameter=parameter,
        resolvedValue=value,
        unit=parameter_unit(parameter),
        origin=parameter_origin(source_origin),
        authority=parameter_authority(parameter, source_origin),
        changeEffect="RECOMPUTE",
        sourceIdentity=source_identity
        or f"tool:{tool_id}@{tool_version}:parameter:{parameter}",
    )


def tool_defaults(tool: Any) -> dict[str, Any]:
    properties = dict((tool.paramsSchema or {}).get("properties") or {})
    return {
        str(name): schema["default"]
        for name, schema in properties.items()
        if isinstance(schema, dict) and "default" in schema
    }


__all__ = [
    "parameter_authority",
    "parameter_origin",
    "parameter_unit",
    "resolved_parameter_provenance",
    "tool_defaults",
]
