"""Batch 0-2: Tool Registry / Adapter Registry dependency boundary.

Covers the contract that replaced the former
`mdi_tool_registry.planner_metadata -> mdi_adapters.registry` import:

* the Tool Registry package must not import the concrete Adapter Registry;
* the adapter-backed port must still enforce selectable-tool invocability;
* the port must read the single `ADAPTER_CLASSES` authority, not a copy;
* every selectable Tool must remain invocable, which the removed inline
  import previously guaranteed implicitly.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

import mdi_adapters
from mdi_adapters.invocability import ADAPTER_INVOCABILITY
from mdi_adapters.registry import ADAPTER_CLASSES
from mdi_schemas import PlannerAvailability
from mdi_tool_registry import (
    AdapterNameInvocability,
    build_registry_snapshot,
    build_tool_planner_metadata,
    load_manifests,
    planner_visible_tools,
    validate_tool_planner_metadata,
)
from mdi_tool_registry.adapter_invocability import (
    register_adapter_invocability,
    resolve_adapter_invocability,
)

_TOOL_REGISTRY_PACKAGE = pathlib.Path(__file__).resolve().parents[1] / "packages" / "tool-registry" / "mdi_tool_registry"


def _imported_modules(path: pathlib.Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            modules.append(node.module or "")
        elif isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.Call):
            function = node.func
            name = getattr(function, "attr", None) or getattr(function, "id", None)
            if name in {"import_module", "__import__"}:
                modules.extend(
                    argument.value
                    for argument in node.args
                    if isinstance(argument, ast.Constant) and isinstance(argument.value, str)
                )
    return modules


def test_tool_registry_never_imports_the_concrete_adapter_package() -> None:
    offenders = [
        (str(path), module)
        for path in _TOOL_REGISTRY_PACKAGE.rglob("*.py")
        for module in _imported_modules(path)
        if module.startswith("mdi_adapters")
    ]

    assert offenders == []


def test_selectable_tools_remain_invocable_through_the_adapter_port() -> None:
    registry = load_manifests()
    _snapshot, metadata = build_registry_snapshot(registry)

    unavailable = [
        tool.toolId
        for tool in registry.tools
        if metadata[tool.toolId].availability is PlannerAvailability.available
        and not ADAPTER_INVOCABILITY.is_invocable(tool.adapter)
    ]

    assert unavailable == []
    assert planner_visible_tools(registry)


def test_registered_port_rejects_a_selectable_tool_without_an_adapter() -> None:
    registry = load_manifests()
    tool = next(item for item in registry.tools if item.stage == "mvp")
    metadata = build_tool_planner_metadata(tool)

    with pytest.raises(ValueError) as error:
        validate_tool_planner_metadata(tool, metadata, adapter_invocability=AdapterNameInvocability(set()))

    assert str(error.value) == f"Selectable planner tool is not invocable: {tool.toolId}"


def test_adapter_package_registers_the_port_on_import() -> None:
    assert mdi_adapters.ADAPTER_CLASSES is ADAPTER_CLASSES
    assert resolve_adapter_invocability() is not None


def test_port_reads_the_single_adapter_authority_without_copying_it() -> None:
    probe = "Batch02ProbeAdapter"
    assert ADAPTER_INVOCABILITY.is_invocable(probe) is False

    ADAPTER_CLASSES[probe] = object
    try:
        assert ADAPTER_INVOCABILITY.is_invocable(probe) is True
    finally:
        del ADAPTER_CLASSES[probe]

    assert ADAPTER_INVOCABILITY.is_invocable(probe) is False


def test_explicit_port_argument_overrides_the_registered_port() -> None:
    registry = load_manifests()
    previous = resolve_adapter_invocability()
    register_adapter_invocability(AdapterNameInvocability(set()))
    try:
        with pytest.raises(ValueError):
            build_registry_snapshot(registry)
        snapshot, _metadata = build_registry_snapshot(registry, adapter_invocability=ADAPTER_INVOCABILITY)
        assert snapshot.snapshotId
    finally:
        register_adapter_invocability(previous)
