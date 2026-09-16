from __future__ import annotations

from typing import Protocol

from mdi_api.agent2_errors import ScientificObjectTypeNotRegistered
from mdi_api.domain.scientific_objects.contracts import ObjectTypeManifest, ScientificObjectKind


class ObjectTypeRegistry(Protocol):
    def register(self, manifest: ObjectTypeManifest) -> None: ...
    def require(self, object_type: str) -> ObjectTypeManifest: ...
    def get(self, object_type: str) -> ObjectTypeManifest | None: ...
    def list_for_kind(self, kind: ScientificObjectKind) -> list[ObjectTypeManifest]: ...


class InMemoryObjectTypeRegistry:
    def __init__(self) -> None:
        self._manifests: dict[str, ObjectTypeManifest] = {}

    def register(self, manifest: ObjectTypeManifest) -> None:
        if manifest.object_type in self._manifests:
            raise ValueError(f"Duplicate object type: {manifest.object_type}")
        self._manifests[manifest.object_type] = manifest

    def require(self, object_type: str) -> ObjectTypeManifest:
        manifest = self.get(object_type)
        if manifest is None:
            raise ScientificObjectTypeNotRegistered(object_type)
        return manifest

    def get(self, object_type: str) -> ObjectTypeManifest | None:
        return self._manifests.get(object_type)

    def list_for_kind(self, kind: ScientificObjectKind) -> list[ObjectTypeManifest]:
        return sorted((item for item in self._manifests.values() if item.kind == kind), key=lambda item: item.object_type)


def build_default_object_type_registry() -> InMemoryObjectTypeRegistry:
    registry = InMemoryObjectTypeRegistry()
    for object_type, kind, display_name in (
        ("materials.dataset", ScientificObjectKind.DATASET, "Materials dataset"),
        ("materials.table", ScientificObjectKind.TABLE, "Scientific materials table"),
        ("structure.crystal", ScientificObjectKind.STRUCTURE, "Crystal structure"),
        ("trajectory.atomic", ScientificObjectKind.TRAJECTORY, "Atomic trajectory"),
        ("diffraction.xrd.experimental", ScientificObjectKind.DIFFRACTION, "Experimental XRD"),
        ("diffraction.xrd.theoretical", ScientificObjectKind.DIFFRACTION, "Theoretical XRD"),
        ("electronic.band_structure", ScientificObjectKind.ELECTRONIC, "Electronic band structure"),
        ("electronic.dos", ScientificObjectKind.ELECTRONIC, "Electronic density of states"),
        ("phonon.band_structure", ScientificObjectKind.PHONON, "Phonon band structure"),
        ("phonon.dos", ScientificObjectKind.PHONON, "Phonon density of states"),
        ("volumetric.field", ScientificObjectKind.VOLUMETRIC, "Volumetric scientific field"),
        ("volumetric.charge_density", ScientificObjectKind.VOLUMETRIC, "Charge density"),
    ):
        registry.register(ObjectTypeManifest(object_type=object_type, kind=kind, display_name=display_name, schema_versions=["1.0"]))
    return registry
