from __future__ import annotations

from mdi_api.research_agent.registry_validation import build_default_agent2_registries


def test_active_scientific_surfaces_have_executable_registry_coverage() -> None:
    """Every active capability stays bound to an executable pack and projector."""

    registries = build_default_agent2_registries()
    manifests = {
        manifest.capability_id: manifest
        for manifest in registries.capabilities.list_all()
        if manifest.status.value == "ACTIVE"
    }
    assert manifests

    pack_by_capability = {
        item.manifest.capability_id: pack.pack_id
        for pack in registries.extension_registry.list_packs()
        for item in pack.capabilities
    }
    assert set(pack_by_capability) == set(manifests)

    for capability_id, manifest in manifests.items():
        assert pack_by_capability[capability_id]
        assert manifest.tool_bindings
        assert all(binding.tool_id for binding in manifest.tool_bindings)
        assert manifest.result_projector
        assert registries.result_projectors.contains(manifest.result_projector)
