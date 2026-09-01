from __future__ import annotations

import hashlib
import json
from typing import Any

from mdi_api.scientific_results.schemas import ScientificResultBundle
from .schemas import REPORT_COMPOSER_VERSION, ReportContextBundle


class ReportComposerInputAssembler:
    """Build bounded, opaque-reference-only report input from persisted contracts."""

    version = REPORT_COMPOSER_VERSION

    def assemble(self, *, bundle: ScientificResultBundle, interpretation: dict[str, Any], relevance_status: str) -> tuple[dict[str, Any], str]:
        result = bundle.model_dump(mode="json")
        result["relevance_status"] = relevance_status
        payload = {
            "contract_version": "2.0",
            "research_question": bundle.research_question,
            "result": {
                "execution_status": bundle.execution_status.value,
                "relevance_status": relevance_status,
                "result_items": [self._result_item(item.model_dump(mode="json")) for item in bundle.result_items[:24]],
                "facts": [self._fact(item.model_dump(mode="json")) for item in bundle.facts[:64]],
                "figures": [self._compact_visual(item.model_dump(mode="json")) for item in bundle.figures[:16]],
                "tables": [self._compact_visual(item.model_dump(mode="json")) for item in bundle.tables[:16]],
                "methods": [self._method(item.model_dump(mode="json")) for item in bundle.methods[:16]],
                "limitations": [
                    {
                        "limitation_id": item.limitation_id,
                        "code": item.code,
                        "message": item.message,
                    }
                    for item in bundle.limitations[:32]
                ],
                "warnings": [item.model_dump(mode="json") for item in bundle.warnings[:32]],
            },
            "interpretation": {
                "title": (interpretation.get("interpretation") or {}).get("title"),
                "answer_lead": (interpretation.get("interpretation") or {}).get("answer_lead"),
                "discussion": (interpretation.get("interpretation") or {}).get("discussion"),
                "conclusion": (interpretation.get("interpretation") or {}).get("conclusion"),
                "findings": (interpretation.get("interpretation") or {}).get("primary_findings", [])[:8],
                "supporting_findings": (interpretation.get("interpretation") or {}).get("supporting_findings", [])[:16],
                "limitations": (interpretation.get("interpretation") or {}).get("limitations", [])[:16],
                "follow_up_suggestions": (interpretation.get("interpretation") or {}).get("follow_up_suggestions", [])[:8],
            },
            "evidence": [self._evidence(item.model_dump(mode="json")) for item in bundle.evidence[:64]],
            "opaque_refs": {
                "result_items": [item.id for item in bundle.result_items[:24]],
                "figures": [item.figure_id for item in bundle.figures[:16]],
                "facts": [item.fact_id for item in bundle.facts[:64]],
                "evidence": [item.evidence_id for item in bundle.evidence[:64]],
                "limitations": [item.limitation_id for item in bundle.limitations[:32]],
                "findings": [str(item.get("finding_id")) for item in [*((interpretation.get("interpretation") or {}).get("primary_findings") or []), *((interpretation.get("interpretation") or {}).get("supporting_findings") or [])] if item.get("finding_id")],
            },
            "omitted_supporting_items": [],
        }
        # Raw provenance IDs are useful for persistence, never for provider prose.
        payload["result"]["provenance"] = {"source_object_version_ids": [f"source_{i + 1}" for i, _ in enumerate(bundle.source_object_refs)]}
        # Validate the complete bounded report context before it crosses the
        # provider boundary. This prevents accidental addition of raw
        # conversation/tool payloads without changing the persisted Result
        # authority or the existing wire shape.
        ReportContextBundle.model_validate(payload)
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
        return payload, fingerprint

    @staticmethod
    def _compact_visual(item: dict[str, Any]) -> dict[str, Any]:
        return {key: item.get(key) for key in ("figure_id", "figure_type", "table_id", "table_type", "role", "title", "fact_refs", "evidence_refs") if key in item}

    @staticmethod
    def _result_item(item: dict[str, Any]) -> dict[str, Any]:
        return {key: item.get(key) for key in ("id", "result_type", "role", "title", "fact_refs", "evidence_refs", "viewer_binding")}

    @staticmethod
    def _fact(item: dict[str, Any]) -> dict[str, Any]:
        return {key: item.get(key) for key in ("fact_id", "predicate", "value", "unit", "uncertainty")}

    @staticmethod
    def _evidence(item: dict[str, Any]) -> dict[str, Any]:
        return {key: item.get(key) for key in ("evidence_id", "evidence_type", "supports_fact_refs", "supports_result_item_refs")}

    @staticmethod
    def _method(item: dict[str, Any]) -> dict[str, Any]:
        return {key: item.get(key) for key in ("method_id", "capability_id", "capability_version", "tool_id", "tool_version", "parameters")}


__all__ = ["ReportComposerInputAssembler"]
