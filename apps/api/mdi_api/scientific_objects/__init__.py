"""Scientific Object domain compatibility package."""

from .registry import (
    InMemoryObjectTypeRegistry,
    ObjectTypeRegistry,
    build_default_object_type_registry,
)
from .schemas import (
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
from .service import ScientificObjectService

__all__ = [
    "InMemoryObjectTypeRegistry",
    "ObjectTypeManifest",
    "ObjectTypeRegistry",
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
    "ScientificObjectService",
    "StorageRef",
    "build_default_object_type_registry",
]
