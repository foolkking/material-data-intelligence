"""Adapter-side implementation of the Tool Registry invocability contract.

The Adapter package owns adapter identity, so it is the correct side to answer
whether a Tool's declared adapter is invocable. Registering here keeps the
package dependency single-directional: `mdi_adapters` imports
`mdi_tool_registry`, never the reverse.

Registration happens on package import and reads the existing `ADAPTER_CLASSES`
mapping directly, so no second registry authority or duplicated adapter
metadata is introduced.
"""

from __future__ import annotations

from mdi_tool_registry.adapter_invocability import (
    AdapterNameInvocability,
    register_adapter_invocability,
)

from .registry import ADAPTER_CLASSES

__all__ = ["ADAPTER_INVOCABILITY", "register_adapter_invocability_port"]


# Reads the single ADAPTER_CLASSES authority; holds no copy of its contents.
ADAPTER_INVOCABILITY = AdapterNameInvocability(ADAPTER_CLASSES)


def register_adapter_invocability_port() -> None:
    """Publish the adapter-backed invocability port to the Tool Registry."""

    register_adapter_invocability(ADAPTER_INVOCABILITY)
