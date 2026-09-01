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

from .policy import ContextOperation, context_budget_policy
from .schemas import ContextManifest, ContextManifestItem


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
    for index, raw in enumerate(items, start=1):
        content = raw.get("content", {})
        encoded = json.dumps(content, sort_keys=True, separators=(",", ":"), default=str)
        normalized.append(
            ContextManifestItem(
                item_id=str(raw.get("item_id") or f"{operation.value.lower()}_{index}"),
                kind=str(raw["kind"]),
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
                was_compacted=bool(raw.get("was_compacted", False)),
                was_truncated=bool(raw.get("was_truncated", False)),
                superseded_state=str(raw.get("superseded_state") or "NONE"),
            )
        )
    critical_kinds = {"SCIENTIFIC_OBJECT", "SCIENTIFIC_SELECTION", "SCIENTIFIC_RESULT", "SCIENTIFIC_EVIDENCE"}
    included: list[ContextManifestItem] = []
    excluded = list(excluded_items)
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
