from __future__ import annotations

from typing import Any, Mapping, Sequence
from uuid import UUID


SOURCE_RESOURCE_INDEX_KEY = "__mdi_source_resources__"


def canonical_profile_resource_ref(
    *,
    object_store: Mapping[str, Any],
    runtime_ref: str,
    profile_resources: Sequence[Any],
) -> str:
    """Bridge an exact-version runtime ref to its immutable Profile resource.

    Agent2 binds an exact ScientificObjectVersion UUID for historical fidelity.
    Data Profile 2.x names the parser-owned canonical resource ID.  The worker
    hydrator records their authoritative hash/alias relationship in the source
    index; this helper resolves only that persisted relationship and never
    guesses by filename, display name, row order, or latest version.
    """

    source_index = object_store.get(SOURCE_RESOURCE_INDEX_KEY, {})
    identity = (
        source_index.get(runtime_ref)
        if isinstance(source_index, Mapping)
        else None
    )
    profile_object_ids = {
        str(getattr(item, "objectId", "")) for item in profile_resources
    }
    exact_version_ref = _looks_like_uuid(runtime_ref)
    if exact_version_ref and isinstance(identity, Mapping) and identity.get("profileObjectId") in profile_object_ids:
        return str(identity["profileObjectId"])
    if exact_version_ref and isinstance(source_index, Mapping):
        canonical_aliases = [
            str(candidate_ref)
            for candidate_ref, candidate_identity in source_index.items()
            if str(candidate_ref) in profile_object_ids
            and isinstance(candidate_identity, Mapping)
            and str(candidate_identity.get("canonicalObjectId") or "")
            == runtime_ref
        ]
        if len(canonical_aliases) == 1:
            return canonical_aliases[0]
    canonical_ref = (
        str(identity.get("canonicalObjectId"))
        if exact_version_ref
        and isinstance(identity, Mapping)
        and identity.get("canonicalObjectId")
        and str(identity.get("canonicalObjectId")) in profile_object_ids
        else runtime_ref
    )
    if (
        exact_version_ref
        and canonical_ref == runtime_ref
        and isinstance(identity, Mapping)
        and identity.get("objectHash")
    ):
        matching_resources = [
            item
            for item in profile_resources
            if str(getattr(item, "objectHash", ""))
            == str(identity["objectHash"])
        ]
        if len(matching_resources) == 1:
            canonical_ref = str(matching_resources[0].objectId)
    return canonical_ref


def _looks_like_uuid(value: str) -> bool:
    try:
        UUID(value)
    except (TypeError, ValueError):
        return False
    return True
