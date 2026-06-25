from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from mdi_artifact_core import content_hash, stable_json_dumps


def _input_ref_value(input_ref: Any, field: str) -> Any:
    if hasattr(input_ref, field):
        return getattr(input_ref, field)
    return input_ref[field]


def hashable_material(value: Any) -> Any:
    if hasattr(value, "as_dict"):
        return value.as_dict()
    if isinstance(value, dict):
        return {str(key): hashable_material(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [hashable_material(item) for item in value]
    if hasattr(value, "tolist"):
        return value.tolist()
    return value


@dataclass
class ToolExecutionContext:
    job_id: str
    project_id: str
    dataset_id: str
    tool_id: str
    tool_version: str
    adapter_version: str
    registry_version: str
    artifact_root: Path
    tool_call_id: str = "tool_call_local"
    object_store: Mapping[str, Any] = field(default_factory=dict)
    resource_limits: dict[str, int] = field(default_factory=dict)

    def resolve_input_refs(self, input_refs: list[Any]) -> list[Any]:
        values: list[Any] = []
        for input_ref in input_refs:
            ref = _input_ref_value(input_ref, "ref")
            if ref not in self.object_store:
                raise KeyError(f"Unknown input ref: {ref}")
            values.append(self.object_store[ref])
        return values

    def input_hashes(self, values: list[Any]) -> list[str]:
        return [content_hash(stable_json_dumps(hashable_material(value))) for value in values]

