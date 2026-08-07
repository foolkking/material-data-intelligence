from __future__ import annotations

from dataclasses import dataclass, field
import math
from pathlib import Path
from typing import Any, Mapping

from mdi_artifact_core import content_hash, stable_json_dumps


def _input_ref_value(input_ref: Any, field: str) -> Any:
    if hasattr(input_ref, field):
        return getattr(input_ref, field)
    return input_ref[field]


def hashable_material(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return {"nonFiniteFloat": "nan" if math.isnan(value) else ("positive_infinity" if value > 0 else "negative_infinity")}
    object_type = getattr(getattr(value, "object_type", None), "value", getattr(value, "object_type", None))
    if object_type == "VolumetricData" and isinstance(getattr(value, "hash", None), str):
        return {"objectType": "VolumetricData", "contentHash": value.hash}
    if hasattr(value, "model_dump"):
        return hashable_material(value.model_dump(mode="json"))
    if hasattr(value, "as_dict"):
        return hashable_material(value.as_dict())
    if _is_dataframe(value):
        return {
            "kind": "pandas.DataFrame",
            "columns": [str(column) for column in value.columns.tolist()],
            "dtypes": [str(dtype) for dtype in value.dtypes.tolist()],
            "index": hashable_material(value.index.tolist()),
            "values": hashable_material(value.to_numpy(dtype=object).tolist()),
        }
    if _is_series(value):
        return {
            "kind": "pandas.Series",
            "name": None if value.name is None else str(value.name),
            "dtype": str(value.dtype),
            "index": hashable_material(value.index.tolist()),
            "values": hashable_material(value.tolist()),
        }
    if isinstance(value, dict):
        return {str(key): hashable_material(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [hashable_material(item) for item in value]
    if hasattr(value, "tolist"):
        return value.tolist()
    return value


def _is_dataframe(value: Any) -> bool:
    value_type = type(value)
    return value_type.__name__ == "DataFrame" and value_type.__module__.startswith("pandas.")


def _is_series(value: Any) -> bool:
    value_type = type(value)
    return value_type.__name__ == "Series" and value_type.__module__.startswith("pandas.")


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
    plan_id: str | None = None
    plan_version: str | None = None
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

