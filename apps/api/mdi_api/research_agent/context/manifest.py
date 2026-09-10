"""Deterministic operation-level ContextManifest construction.

The manifest is an audit projection of provider input.  It contains no
provider secrets and does not introduce scientific authority.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import UUID, uuid4

from .provenance import deduplicate_provenance_items
from .policy import ContextOperation, context_budget_policy
from .schemas import ContextManifest, ContextManifestItem


def _default_provenance(kind: str) -> tuple[str, str, str, str]:
    """Return source/authority/freshness defaults for existing manifest kinds."""

    return {
        "SCIENTIFIC_OBJECT": (
            "EXACT_SCIENTIFIC_OBJECT_VERSION",
            "SCIENTIFIC_INPUT",
            "CURRENT",
            "OBSERVED",
        ),
        "SCIENTIFIC_SELECTION": (
            "EXPLICIT_UI_SELECTION",
            "SCIENTIFIC_INPUT",
            "CURRENT",
            "OBSERVED",
        ),
        "SCIENTIFIC_RESULT": (
            "SCIENTIFIC_RESULT",
            "SCIENTIFIC_KNOWLEDGE",
            "HISTORICAL_VALID",
            "COMPUTED",
        ),
        "SCIENTIFIC_EVIDENCE": (
            "SCIENTIFIC_EVIDENCE",
            "SCIENTIFIC_EVIDENCE",
            "CURRENT",
            "COMPUTED",
        ),
        "USER_CONSTRAINT": (
            "CURRENT_USER_REQUEST",
            "USER_INTENT",
            "CURRENT",
            "CONSTRAINT",
        ),
        "RESEARCH_GOAL": (
            "CURRENT_USER_REQUEST",
            "USER_INTENT",
            "CURRENT",
            "CONSTRAINT",
        ),
        "CAPABILITY_CANDIDATE": (
            "CURRENT_USER_REQUEST",
            "HISTORICAL_CONTEXT",
            "CURRENT",
            "OBSERVED",
        ),
    }.get(kind, ("UNKNOWN", "HISTORICAL_CONTEXT", "UNKNOWN", "OBSERVED"))


def build_operation_manifest(
    *,
    operation: ContextOperation,
    project_id: str,
    research_session_id: str,
    research_turn_id: UUID,
    context_fingerprint: str,
    items: Iterable[dict[str, Any]],
    excluded_items: Iterable[str] = (),
) -> ContextManifest:
    """Build a bounded, immutable manifest for one provider operation."""
    policy = context_budget_policy(operation)
    normalized: list[ContextManifestItem] = []
    unique_items, duplicate_item_ids = deduplicate_provenance_items(list(items))
    for index, raw in enumerate(unique_items, start=1):
        kind = str(raw["kind"])
        default_source, default_authority, default_freshness, default_epistemic = _default_provenance(kind)
        if raw.get("authorization_checked", True) is not True:
            raise ValueError(f"unauthorized context item: {raw.get('item_id') or index}")
        content = raw.get("content", {})
        encoded = json.dumps(content, sort_keys=True, separators=(",", ":"), default=str)
        normalized.append(
            ContextManifestItem(
                item_id=str(raw.get("item_id") or f"{operation.value.lower()}_{index}"),
                kind=kind,
                authority_class=str(raw["authority_class"]),
                server_side_source_identity=str(raw.get("source_identity") or raw["item_id"]),
                provider_opaque_ref=str(raw.get("opaque_ref") or raw["item_id"]),
                exact_object_id=raw.get("object_id"),
                exact_object_version_id=raw.get("version_id"),
                result_ref=raw.get("result_ref"),
                inclusion_reason=str(raw.get("inclusion_reason") or "operation input"),
                selection_mode=str(raw.get("selection_mode") or "RETRIEVED"),
                authorization_checked=bool(raw.get("authorization_checked", True)),
                content_fingerprint=hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
                estimated_tokens=max(1, len(encoded.encode("utf-8")) // 4),
                source_class=str(raw.get("source_class") or default_source),
                freshness=str(raw.get("freshness") or default_freshness),
                epistemic_status=str(raw.get("epistemic_status") or default_epistemic),
                was_compacted=bool(raw.get("was_compacted", False)),
                was_truncated=bool(raw.get("was_truncated", False)),
                superseded_state=str(raw.get("superseded_state") or "NONE"),
            )
        )
    critical_kinds = {"SCIENTIFIC_OBJECT", "SCIENTIFIC_SELECTION", "SCIENTIFIC_RESULT", "SCIENTIFIC_EVIDENCE"}
    included: list[ContextManifestItem] = []
    excluded = [*excluded_items, *duplicate_item_ids]
    estimated = 0
    for item in normalized:
        if estimated + item.estimated_tokens <= policy.effective_input_budget:
            included.append(item)
            estimated += item.estimated_tokens
        elif item.kind in critical_kinds:
            raise ValueError(f"critical {operation.value} context exceeds the operation budget")
        else:
            excluded.append(item.item_id)
    return ContextManifest(
        context_manifest_id=uuid4(),
        operation=operation.value,
        project_id=project_id,
        research_session_id=research_session_id,
        research_turn_id=research_turn_id,
        policy_version="agent2.context-policy/2.0",
        included_items=included,
        excluded_items=excluded[:64],
        estimated_input_tokens=estimated,
        input_budget=policy.effective_input_budget,
        reserved_output_tokens=policy.reserved_output_tokens,
        repair_margin=policy.repair_margin,
        compaction_state="COMPACTED" if excluded else "NONE",
        truncation_state="TRUNCATED" if any(item.was_truncated for item in included) else "NONE",
        context_fingerprint=context_fingerprint,
        created_at=datetime.now(timezone.utc),
    )


__all__ = ["build_operation_manifest"]
