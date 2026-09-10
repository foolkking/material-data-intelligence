"""Small, deterministic provenance policy for Agent context.

This module deliberately contains policy and read-only projections only.  The
durable scientific authorities remain ScientificObjectVersion, Artifact and
ScientificResult; a context candidate or memory record never becomes a new
authority by passing through these helpers.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Iterable, Mapping


class ContextSourceClass(StrEnum):
    CURRENT_USER_REQUEST = "CURRENT_USER_REQUEST"
    EXPLICIT_UI_SELECTION = "EXPLICIT_UI_SELECTION"
    EXACT_SCIENTIFIC_OBJECT_VERSION = "EXACT_SCIENTIFIC_OBJECT_VERSION"
    SCIENTIFIC_RESULT = "SCIENTIFIC_RESULT"
    SCIENTIFIC_EVIDENCE = "SCIENTIFIC_EVIDENCE"
    PREVIOUS_RESEARCH_TURN = "PREVIOUS_RESEARCH_TURN"
    RESEARCH_MEMORY = "RESEARCH_MEMORY"
    PROJECT_HISTORY = "PROJECT_HISTORY"
    PRESENTATION_PROJECTION = "PRESENTATION_PROJECTION"


class ContextAuthorityClass(StrEnum):
    USER_INTENT = "USER_INTENT"
    SCIENTIFIC_INPUT = "SCIENTIFIC_INPUT"
    SCIENTIFIC_KNOWLEDGE = "SCIENTIFIC_KNOWLEDGE"
    SCIENTIFIC_EVIDENCE = "SCIENTIFIC_EVIDENCE"
    EXECUTION_OUTPUT = "EXECUTION_OUTPUT"
    HISTORICAL_CONTEXT = "HISTORICAL_CONTEXT"
    PRESENTATION = "PRESENTATION"
    MEMORY = "MEMORY"


class ContextFreshness(StrEnum):
    CURRENT = "CURRENT"
    HISTORICAL_VALID = "HISTORICAL_VALID"
    STALE = "STALE"
    INVALIDATED = "INVALIDATED"
    SOURCE_MISSING = "SOURCE_MISSING"
    UNKNOWN = "UNKNOWN"


class MemoryEpistemicStatus(StrEnum):
    CONSTRAINT = "CONSTRAINT"
    DECISION = "DECISION"
    OBSERVED = "OBSERVED"
    COMPUTED = "COMPUTED"
    INTERPRETED = "INTERPRETED"
    HYPOTHESIS = "HYPOTHESIS"
    USER_ASSERTED = "USER_ASSERTED"


_SOURCE_CLASS_BY_LEGACY_SOURCE = {
    "EXPLICIT_REFERENCE": ContextSourceClass.EXPLICIT_UI_SELECTION,
    "UI_SELECTION": ContextSourceClass.EXPLICIT_UI_SELECTION,
    "CURRENT_SCOPE": ContextSourceClass.EXACT_SCIENTIFIC_OBJECT_VERSION,
    "PREVIOUS_TURN_RESULT": ContextSourceClass.SCIENTIFIC_RESULT,
    "PREVIOUS_TURN": ContextSourceClass.PREVIOUS_RESEARCH_TURN,
    "PINNED_CONTEXT": ContextSourceClass.RESEARCH_MEMORY,
    "RECENT_CONTEXT": ContextSourceClass.PREVIOUS_RESEARCH_TURN,
    "LONG_SESSION_RETRIEVAL": ContextSourceClass.PROJECT_HISTORY,
}


def source_class_for_candidate(source: Any, ref_type: str | None = None) -> ContextSourceClass:
    """Map existing candidate origins to one inspectable vocabulary."""

    # Candidate origin (for example PINNED_CONTEXT) controls retrieval
    # priority, but it must not replace the scientific source class. A pinned
    # Result remains a ScientificResult and a pinned object remains an exact
    # ScientificObjectVersion.
    value = getattr(source, "value", source)
    if ref_type == "SCIENTIFIC_OBJECT":
        return (
            ContextSourceClass.EXPLICIT_UI_SELECTION
            if str(value) in {"EXPLICIT_REFERENCE", "UI_SELECTION"}
            else ContextSourceClass.EXACT_SCIENTIFIC_OBJECT_VERSION
        )
    if ref_type == "SCIENTIFIC_RESULT":
        return ContextSourceClass.SCIENTIFIC_RESULT
    if ref_type == "SCIENTIFIC_FINDING":
        return ContextSourceClass.SCIENTIFIC_EVIDENCE
    mapped = _SOURCE_CLASS_BY_LEGACY_SOURCE.get(str(value))
    if mapped is not None:
        return mapped
    return ContextSourceClass.EXACT_SCIENTIFIC_OBJECT_VERSION


def authority_for_candidate(ref_type: str, source: Any) -> ContextAuthorityClass:
    if ref_type == "SCIENTIFIC_OBJECT":
        return ContextAuthorityClass.SCIENTIFIC_INPUT
    if ref_type == "SCIENTIFIC_RESULT":
        return ContextAuthorityClass.SCIENTIFIC_KNOWLEDGE
    if ref_type == "SCIENTIFIC_FINDING":
        return ContextAuthorityClass.SCIENTIFIC_EVIDENCE
    return (
        ContextAuthorityClass.MEMORY
        if source_class_for_candidate(source, ref_type) == ContextSourceClass.RESEARCH_MEMORY
        else ContextAuthorityClass.HISTORICAL_CONTEXT
    )


def freshness_for_source(
    *,
    stale: bool = False,
    availability_status: str | None = None,
    relevance_status: str | None = None,
    source_exists: bool = True,
    invalidated: bool = False,
    superseded: bool = False,
) -> ContextFreshness:
    """Classify freshness without equating age with invalidity."""

    if invalidated:
        return ContextFreshness.INVALIDATED
    if not source_exists:
        return ContextFreshness.SOURCE_MISSING
    availability = str(availability_status or "").upper()
    relevance = str(relevance_status or "").upper()
    if availability in {"INVALID", "INVALIDATED"} or relevance in {"INVALID", "INVALIDATED"}:
        return ContextFreshness.INVALIDATED
    if availability in {"SOURCE_MISSING", "MISSING", "UNAVAILABLE"}:
        return ContextFreshness.SOURCE_MISSING
    if stale or superseded or relevance in {"STALE", "SUPERSEDED"}:
        return ContextFreshness.STALE
    if relevance in {"HISTORICAL_VALID", "HISTORICAL"}:
        return ContextFreshness.HISTORICAL_VALID
    if availability or relevance:
        return ContextFreshness.CURRENT
    return ContextFreshness.UNKNOWN


def candidate_source_ref(candidate: Mapping[str, Any]) -> str | None:
    """Return a stable source reference suitable for provenance metadata."""

    if candidate.get("source_ref"):
        return str(candidate["source_ref"])
    object_ref = candidate.get("object_ref")
    if object_ref is not None:
        object_id = getattr(object_ref, "object_id", None) or object_ref.get("object_id")
        version_id = getattr(object_ref, "version_id", None) or object_ref.get("version_id")
        if object_id and version_id:
            return f"{object_id}:{version_id}"
    object_id = candidate.get("object_id") or candidate.get("exact_object_id")
    version_id = candidate.get("version_id") or candidate.get("exact_object_version_id")
    if object_id and version_id:
        return f"{object_id}:{version_id}"
    for key in (
        "result_id",
        "result_ref",
        "finding_ref",
        "turn_id",
        "candidate_id",
    ):
        if candidate.get(key) is not None:
            return str(candidate[key])
    return None


def provenance_key(candidate: Mapping[str, Any]) -> tuple[str, str, str]:
    """Key equivalent source material while preserving semantic item kind."""

    kind = str(candidate.get("ref_type") or candidate.get("kind") or "")
    return (
        kind,
        str(candidate.get("source_class") or candidate.get("source") or ""),
        str(
            candidate_source_ref(candidate)
            or candidate.get("item_id")
            or candidate.get("candidate_key")
            or ""
        ),
    )


def deduplicate_provenance_items(
    items: Iterable[Mapping[str, Any]],
) -> tuple[list[Mapping[str, Any]], list[str]]:
    """Keep the first deterministic representation and report suppressed IDs."""

    selected: list[Mapping[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    suppressed: list[str] = []
    for item in items:
        key = provenance_key(item)
        if key in seen:
            item_id = item.get("item_id") or item.get("candidate_key")
            if item_id:
                suppressed.append(str(item_id))
            continue
        seen.add(key)
        selected.append(item)
    return selected, suppressed


@dataclass(frozen=True)
class SourceConflict:
    source_refs: tuple[str, ...]
    winner: str | None
    reason: str


def resolve_source_conflict(items: Iterable[Mapping[str, Any]]) -> SourceConflict | None:
    """Resolve only the deterministic authority ordering, never content."""

    rows = [item for item in items if candidate_source_ref(item)]
    refs = tuple(sorted({str(candidate_source_ref(item)) for item in rows}))
    if len(refs) < 2:
        return None
    authority_rank = {
        ContextAuthorityClass.SCIENTIFIC_INPUT.value: 0,
        ContextAuthorityClass.SCIENTIFIC_KNOWLEDGE.value: 1,
        ContextAuthorityClass.SCIENTIFIC_EVIDENCE.value: 2,
        ContextAuthorityClass.EXECUTION_OUTPUT.value: 3,
        ContextAuthorityClass.USER_INTENT.value: 4,
        ContextAuthorityClass.HISTORICAL_CONTEXT.value: 5,
        ContextAuthorityClass.MEMORY.value: 6,
        ContextAuthorityClass.PRESENTATION.value: 7,
    }
    winner = min(
        rows,
        key=lambda item: (
            authority_rank.get(str(item.get("authority_class") or ""), 99),
            0 if str(item.get("freshness") or "") == ContextFreshness.CURRENT.value else 1,
            str(candidate_source_ref(item)),
        ),
    )
    return SourceConflict(
        source_refs=refs,
        winner=str(candidate_source_ref(winner)),
        reason="higher-authority current source wins; lower-authority sources remain inspectable",
    )


def context_provenance_summary(
    *,
    snapshot: Mapping[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a bounded operator-facing summary from existing snapshot/manifest data."""

    snapshot = snapshot or {}
    manifest = manifest or {}
    included = list(manifest.get("included_items") or [])
    excluded = list(manifest.get("excluded_items") or [])
    categories = Counter(
        str(item.get("kind") or "UNKNOWN")
        for item in included
        if isinstance(item, Mapping)
    )
    stale = sum(
        1
        for item in included
        if isinstance(item, Mapping)
        and str(item.get("superseded_state") or "NONE") in {"STALE", "INVALIDATED"}
    )
    memory_count = sum(
        1
        for item in included
        if isinstance(item, Mapping)
        and str(item.get("authority_class") or "") == ContextAuthorityClass.MEMORY.value
    )
    return {
        "candidate_count": sum(
            len(snapshot.get(key) or [])
            for key in (
                "active_scope_refs_json",
                "selection_refs_json",
                "scientific_selections_json",
                "resolved_references_json",
                "referenced_result_refs_json",
                "relevant_finding_refs_json",
            )
        ),
        "selected_count": len(included),
        "excluded_count": len(excluded),
        "memory_candidate_count": memory_count,
        "selected_memory_count": memory_count,
        "stale_candidate_count": stale,
        "freshness_warnings": stale,
        "source_categories": dict(sorted(categories.items())),
        "budget": {
            "estimated_input_tokens": manifest.get("estimated_input_tokens"),
            "input_budget": manifest.get("input_budget"),
            "compaction_state": manifest.get("compaction_state", "UNKNOWN"),
            "truncation_state": manifest.get("truncation_state", "UNKNOWN"),
        },
        "degraded": bool(excluded)
        or str(manifest.get("compaction_state") or "NONE") != "NONE"
        or str(manifest.get("truncation_state") or "NONE") != "NONE",
    }


__all__ = [
    "ContextAuthorityClass",
    "ContextFreshness",
    "ContextSourceClass",
    "MemoryEpistemicStatus",
    "SourceConflict",
    "candidate_source_ref",
    "context_provenance_summary",
    "deduplicate_provenance_items",
    "freshness_for_source",
    "provenance_key",
    "resolve_source_conflict",
    "source_class_for_candidate",
    "authority_for_candidate",
]
