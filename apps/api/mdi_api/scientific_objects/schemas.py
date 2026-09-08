"""Compatibility facade for scientific-object contracts."""

from mdi_api.domain.scientific_objects.contracts import (
    ObjectTypeManifest,
    ScientificDatasetFilter,
    ScientificDatasetQueryRequest,
    ScientificObjectAdmissionRequest,
    ScientificObjectAvailability,
    ScientificObjectKind,
    ScientificObjectLifecycle,
    ScientificObjectRef,
    ScientificObjectVersionContract,
    ScientificObjectVersionCreateRequest,
    ScientificObjectVersionRef,
    StorageRef,
)

__all__ = [
    "ObjectTypeManifest",
    "ScientificDatasetFilter",
    "ScientificDatasetQueryRequest",
    "ScientificObjectAdmissionRequest",
    "ScientificObjectAvailability",
    "ScientificObjectKind",
    "ScientificObjectLifecycle",
    "ScientificObjectRef",
    "ScientificObjectVersionContract",
    "ScientificObjectVersionCreateRequest",
    "ScientificObjectVersionRef",
    "StorageRef",
]
