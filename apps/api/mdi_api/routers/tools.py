from __future__ import annotations

from mdi_tool_registry import load_manifests


def list_tools() -> dict[str, object]:
    registry = load_manifests()
    return {
        "version": registry.version,
        "tools": [tool.model_dump(mode="json") for tool in registry.list_tools()],
    }


def list_mvp_tools() -> dict[str, object]:
    registry = load_manifests()
    return {
        "version": registry.version,
        "tools": [tool.model_dump(mode="json") for tool in registry.list_mvp_tools()],
    }
