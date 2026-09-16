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
        "INTERPRETATION": (
            "PRESENTATION_PROJECTION",
            "DERIVED_SUMMARY",
            "HISTORICAL_VALID",
            "INTERPRETED",
        ),
        "SCIENTIFIC_EVIDENCE": (
            "SCIENTIFIC_EVIDENCE",
            "SCIENTIFIC_EVIDENCE",
            "CURRENT",
            "COMPUTED",
        ),
        "LITERATURE_EVIDENCE": (
            "LITERATURE_EVIDENCE",
            "SCIENTIFIC_EVIDENCE",
            "HISTORICAL_VALID",
            "REPORTED",
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
    serialized_input: dict[str, Any] | None = None,
    serialized_input_version: str | None = None,
    invocation_role: str | None = None,
    prompt_template_version: str | None = None,
    input_state: str = "ACTUAL",
) -> ContextManifest:
    """Build a bounded, immutable manifest for one provider operation."""
    policy = context_budget_policy(operation)
    normalized: list[ContextManifestItem] = []
    unique_items, duplicate_item_ids = deduplicate_provenance_items(list(items))
    for index, raw in enumerate(unique_items, start=1):
        kind = str(raw["kind"])
        default_source, default_authority, default_freshness, default_epistemic = _default_provenance(kind)
        authority = str(raw.get("authority_class") or default_authority)
        if kind == "INTERPRETATION" and authority in {
            "SCIENTIFIC_RESULT",
            "SCIENTIFIC_EVIDENCE",
        }:
            raise ValueError("interpretation context cannot be marked as scientific evidence")
        if authority == "SCIENTIFIC_RESULT" and kind != "SCIENTIFIC_RESULT":
            raise ValueError("only ScientificResult context may use SCIENTIFIC_RESULT authority")
        if authority == "SCIENTIFIC_EVIDENCE" and kind not in {
            "SCIENTIFIC_EVIDENCE",
            "LITERATURE_EVIDENCE",
        }:
            raise ValueError(
                "only validated scientific or literature evidence may use "
                "SCIENTIFIC_EVIDENCE authority"
            )
        if raw.get("authorization_checked", True) is not True:
            raise ValueError(f"unauthorized context item: {raw.get('item_id') or index}")
        content = raw.get("content", {})
        encoded = json.dumps(content, sort_keys=True, separators=(",", ":"), default=str)
        normalized.append(
            ContextManifestItem(
                item_id=str(raw.get("item_id") or f"{operation.value.lower()}_{index}"),
                kind=kind,
                authority_class=authority,
                server_side_source_identity=str(raw.get("source_identity") or raw["item_id"]),
                provider_opaque_ref=str(raw.get("opaque_ref") or raw["item_id"]),
                exact_object_id=raw.get("object_id"),
                exact_object_version_id=raw.get("version_id"),
                result_ref=raw.get("result_ref"),
                inclusion_reason=str(raw.get("inclusion_reason") or "operation input"),
                selection_mode=str(raw.get("selection_mode") or "RETRIEVED"),
                authorization_checked=bool(raw.get("authorization_checked", True)),
                content_fingerprint=hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
                representation_type=str(
                    raw.get("representation_type") or "BOUNDED_JSON"
                ),
                representation_version=str(
                    raw.get("representation_version") or "1.0"
                ),
                serialized_representation=content,
                lineage_refs=[
                    str(value)
                    for value in (
                        raw.get("lineage_refs")
                        or [raw.get("source_identity") or raw.get("item_id")]
                    )
                    if value
                ][:16],
                estimated_tokens=max(1, len(encoded.encode("utf-8")) // 4),
                source_class=str(raw.get("source_class") or default_source),
                freshness=str(raw.get("freshness") or default_freshness),
                epistemic_status=str(raw.get("epistemic_status") or default_epistemic),
                was_compacted=bool(raw.get("was_compacted", False)),
                was_truncated=bool(raw.get("was_truncated", False)),
                superseded_state=str(raw.get("superseded_state") or "NONE"),
            )
        )
    critical_kinds = {
        "SCIENTIFIC_OBJECT",
        "SCIENTIFIC_SELECTION",
        "SCIENTIFIC_RESULT",
        "INTERPRETATION",
        "SCIENTIFIC_EVIDENCE",
        "LITERATURE_EVIDENCE",
    }
    included: list[ContextManifestItem] = []
    explicit_excluded = [str(value) for value in excluded_items]
    excluded = [*explicit_excluded, *duplicate_item_ids]
    exclusion_reasons = {
        item_id: ("UNKNOWN", "Excluded before operation context selection.")
        for item_id in explicit_excluded
    }
    exclusion_reasons.update(
        {
            item_id: (
                "DUPLICATE",
                "Duplicate representation of the same authoritative source.",
            )
            for item_id in duplicate_item_ids
        }
    )
    estimated = 0
    for item in normalized:
        if estimated + item.estimated_tokens <= policy.effective_input_budget:
            included.append(item)
            estimated += item.estimated_tokens
        elif item.kind in critical_kinds:
            raise ValueError(f"critical {operation.value} context exceeds the operation budget")
        else:
            excluded.append(item.item_id)
            exclusion_reasons[item.item_id] = (
                "BUDGET",
                "The bounded operation budget could not include this non-critical item.",
            )
    serialized_input_fingerprint = None
    serialized_input_tokens = None
    if serialized_input is not None:
        serialized = json.dumps(
            serialized_input,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        serialized_input_fingerprint = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()
        serialized_input_tokens = max(1, len(serialized.encode("utf-8")) // 4)
        if serialized_input_tokens > policy.effective_input_budget:
            raise ValueError(
                f"actual {operation.value} serialized input exceeds the operation budget"
            )
    return ContextManifest(
        context_manifest_id=uuid4(),
        operation=operation.value,
        project_id=project_id,
        research_session_id=research_session_id,
        research_turn_id=research_turn_id,
        policy_version="agent2.context-policy/2.0",
        input_state=input_state,
        invocation_role=invocation_role,
        prompt_template_version=prompt_template_version,
        serialized_input_version=serialized_input_version,
        serialized_input=serialized_input,
        serialized_input_fingerprint=serialized_input_fingerprint,
        included_items=included,
        excluded_items=excluded[:64],
        excluded_item_details=[
            {
                "item_id": item_id,
                "reason": exclusion_reasons.get(item_id, ("UNKNOWN", ""))[0],
                "detail": exclusion_reasons.get(
                    item_id,
                    ("UNKNOWN", "Excluded by the bounded context selector."),
                )[1],
            }
            for item_id in excluded[:64]
        ],
        estimated_input_tokens=(
            serialized_input_tokens
            if serialized_input_tokens is not None
            else estimated
        ),
        input_budget=policy.effective_input_budget,
        reserved_output_tokens=policy.reserved_output_tokens,
        repair_margin=policy.repair_margin,
        compaction_state="COMPACTED" if excluded else "NONE",
        truncation_state="TRUNCATED" if any(item.was_truncated for item in included) else "NONE",
        context_fingerprint=context_fingerprint,
        created_at=datetime.now(timezone.utc),
    )


__all__ = ["build_operation_manifest"]
