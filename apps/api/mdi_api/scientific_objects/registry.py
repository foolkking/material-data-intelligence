"""Compatibility facade for the scientific-object type registry."""

from mdi_api.infrastructure.scientific_objects.registry import (
    InMemoryObjectTypeRegistry,
    ObjectTypeRegistry,
    build_default_object_type_registry,
)

__all__ = [
    "InMemoryObjectTypeRegistry",
    "ObjectTypeRegistry",
    "build_default_object_type_registry",
]
