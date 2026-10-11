"""Parameter records preserve structured inputs without accepting unbounded JSON."""
from copy import deepcopy
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from mdi_schemas import CAPABILITY_PLANNING_MAX_REGISTRY_TOOLS, ParameterProvenance
from mdi_tool_registry import build_registry_snapshot, load_manifests


def _record(value):
    return {"parameter": "functions", "resolvedValue": value, "origin": "USER_SPECIFIED",
            "authority": "USER_EDITABLE", "changeEffect": "RECOMPUTE", "sourceIdentity": "current-question"}


@pytest.mark.parametrize("value", [
    [1, 1.0, -2.5], ["Si", "Cu"], True, None,
    [{"kind": "polynomial", "coefficients": [-1, 0, 1.0]}, {"kind": "gaussian", "sigma": 0.5}],
    {"text": "x,y\n0,0\n1,2", "options": {"enabled": False, "missing": None}},
])
def test_parameter_json_roundtrips_without_stringification_or_type_coercion(value):
    original = deepcopy(value)
    record = ParameterProvenance.model_validate(_record(value))
    restored = ParameterProvenance.model_validate_json(record.model_dump_json())
    assert value == original
    assert restored.resolvedValue == original
    Draft202012Validator(ParameterProvenance.model_json_schema()).validate(record.model_dump(mode="json"))
    if value == [1, 1.0, -2.5]:
        assert [type(item) for item in restored.resolvedValue] == [int, float, float]


@pytest.mark.parametrize("value", [
    [[[[[0]]]]], list(range(129)), {str(index): 0 for index in range(65)},
    "x" * 16385, {"x" * 129: 0}, float("nan"), float("inf"), 10**101,
    {1: "non-string-key"}, (1, 2), {1, 2}, b"not-json",
    [[0] * 128 for _ in range(5)], ["数" * 10000] * 3,
])
def test_parameter_json_rejects_invalid_types_depth_and_resource_limits(value):
    with pytest.raises(ValidationError):
        ParameterProvenance.model_validate(_record(value))


@pytest.mark.parametrize("value", [[[[[[0]]]]], list(range(129)), "x" * 16385])
def test_checked_schema_also_rejects_excessive_depth_arrays_and_text(value):
    assert not Draft202012Validator(ParameterProvenance.model_json_schema()).is_valid(_record(value))


def test_registry_limit_is_shared_by_metadata_and_snapshot_contract():
    registry = load_manifests()
    assert len(registry.tools) <= CAPABILITY_PLANNING_MAX_REGISTRY_TOOLS
    oversized = SimpleNamespace(tools=[registry.tools[0]] * (CAPABILITY_PLANNING_MAX_REGISTRY_TOOLS + 1))
    with pytest.raises(ValueError, match="candidate cap"):
        build_registry_snapshot(oversized)
