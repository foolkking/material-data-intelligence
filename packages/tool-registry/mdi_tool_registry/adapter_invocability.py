"""Abstract adapter-invocability contract required by planner metadata.

Planner metadata validation must confirm that a selectable Tool is actually
invocable, which is knowledge owned by the Adapter package. The Tool Registry
therefore declares only the narrow contract it needs and never imports the
concrete Adapter Registry, so `mdi_tool_registry` does not depend on
`mdi_adapters`.

The concrete implementation is supplied in the allowed direction: the Adapter
package registers itself against this contract on import, and composition may
also pass an explicit port per call. This is a single named contract, not a
general service locator: only adapter-name invocability can be registered here,
and the Tool Registry gains no adapter execution authority.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = [
    "AdapterInvocabilityPort",
    "AdapterNameInvocability",
    "clear_adapter_invocability",
    "register_adapter_invocability",
    "resolve_adapter_invocability",
]


@runtime_checkable
class AdapterInvocabilityPort(Protocol):
    """Answers whether a registered adapter name can actually be invoked."""

    def is_invocable(self, adapter_name: str) -> bool:  # pragma: no cover - protocol
        ...


class AdapterNameInvocability:
    """Port implementation backed by an adapter-name collection."""

    def __init__(self, adapter_names: object) -> None:
        self._adapter_names = adapter_names

    def is_invocable(self, adapter_name: str) -> bool:
        return adapter_name in self._adapter_names  # type: ignore[operator]


_PORT: AdapterInvocabilityPort | None = None


def register_adapter_invocability(port: AdapterInvocabilityPort | None) -> None:
    """Register the process-wide adapter-invocability implementation."""

    global _PORT
    _PORT = port


def resolve_adapter_invocability() -> AdapterInvocabilityPort | None:
    """Return the registered implementation, or None when adapters are absent."""

    return _PORT


def clear_adapter_invocability() -> None:
    """Remove the registered implementation. Intended for focused tests."""

    global _PORT
    _PORT = None
