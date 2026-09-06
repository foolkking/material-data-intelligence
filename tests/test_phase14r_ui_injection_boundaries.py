from __future__ import annotations

import pytest
from pydantic import ValidationError

from mdi_api.agent2_errors import RegistryValidationError
from mdi_api.research_agent.capabilities.packs import (
    CapabilityExtensionRegistry,
    build_phase11_packs,
    make_pack_capability,
)
from mdi_api.research_agent.registry_validation import build_default_agent2_registries
from mdi_api.scientific_viewers.schemas import ScientificViewerDescriptor


@pytest.mark.parametrize(
    "binding",
    [
        "https://plugins.invalid/viewer.js",
        "remote_component",
        "dynamic-import",
        "<script>alert(1)</script>",
        "javascript:alert(1)",
    ],
)
def test_capability_pack_rejects_executable_viewer_bindings_atomically(
    binding: str,
) -> None:
    default_pack = build_phase11_packs(
        build_default_agent2_registries().capabilities.list_all()
    )[0]
    original = default_pack.capabilities[0].manifest
    unsafe = original.model_copy(update={"viewer_bindings": [binding]})
    pack = default_pack.model_copy(
        update={
            "pack_id": "core.unsafe-ui",
            "capabilities": [make_pack_capability(unsafe)],
        }
    )
    registry = CapabilityExtensionRegistry()

    with pytest.raises(
        RegistryValidationError,
        match="EXECUTABLE_VIEWER_BINDING_FORBIDDEN",
    ):
        registry.register_pack(pack)

    assert registry.list_packs() == []
    assert registry.list_capabilities() == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("renderer_key", "https://plugins.invalid/renderer.js"),
        ("renderer_key", "remote/component"),
        ("object_type", "<script>structure.crystal</script>"),
    ],
)
def test_viewer_descriptor_rejects_remote_or_executable_registry_values(
    field: str,
    value: str,
) -> None:
    payload = {
        "viewer_id": "scientific.structure-3d",
        "object_type": "structure.crystal",
        "renderer_key": "structure-3d",
        "support": "PROFESSIONAL",
        "interaction_capabilities": ["rotate", "zoom"],
        "selection_capabilities": ["STRUCTURE_SITE"],
        "maximum_payload_bytes": 1024,
        "fallback_policy": "SCIENTIFIC_METADATA_THEN_SAFE_DOWNLOAD",
        field: value,
    }

    with pytest.raises(ValidationError):
        ScientificViewerDescriptor.model_validate(payload)


def test_viewer_descriptor_rejects_executable_capability_strings() -> None:
    with pytest.raises(ValidationError):
        ScientificViewerDescriptor(
            viewer_id="scientific.structure-3d",
            object_type="structure.crystal",
            renderer_key="structure-3d",
            support="PROFESSIONAL",
            interaction_capabilities=["rotate", "import(https://plugins.invalid)"],
            selection_capabilities=["STRUCTURE_SITE"],
            maximum_payload_bytes=1024,
            fallback_policy="SCIENTIFIC_METADATA_THEN_SAFE_DOWNLOAD",
        )
