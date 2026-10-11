from __future__ import annotations

import hashlib
import json
from typing import Any
from mdi_api.application.scientific_reasoning.follow_ups import project_follow_up_suggestions, report_next_steps_text
from mdi_api.application.interpretation.assembler import InterpreterInputAssembler

from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.domain.scientific_results.reference_sources import project_reference_context
from mdi_api.domain.scientific_reports.contracts import REPORT_COMPOSER_VERSION, ReportContextBundle


class ReportComposerInputAssembler:
    """Build bounded, opaque-reference-only report input from persisted contracts."""

    version = REPORT_COMPOSER_VERSION

    def assemble(
        self,
        *,
        bundle: ScientificResultBundle,
        interpretation: dict[str, Any],
        relevance_status: str,
        literature_evidence: list[dict[str, Any]] | None = None,
    ) -> tuple[dict[str, Any], str]:
        result = bundle.model_dump(mode="json")
        result["relevance_status"] = relevance_status
        omitted: list[str] = []
        facts = InterpreterInputAssembler._compact_facts(
            InterpreterInputAssembler._select_representative_facts(result["facts"], omitted))
        payload = {
            "contract_version": "2.0",
            "research_question": bundle.research_question,
            "result": {
                "execution_status": bundle.execution_status.value,
                "relevance_status": relevance_status,
                "result_items": [self._result_item(item.model_dump(mode="json")) for item in bundle.result_items[:24]],
                "facts": facts,
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
                "findings": [self._finding(item) for item in (interpretation.get("interpretation") or {}).get("primary_findings", [])[:8]],
                "supporting_findings": [self._finding(item) for item in (interpretation.get("interpretation") or {}).get("supporting_findings", [])[:16]],
                "limitations": (interpretation.get("interpretation") or {}).get("limitations", [])[:16],
                "follow_up_suggestions": project_follow_up_suggestions(
                    (interpretation.get("interpretation") or {}).get("follow_up_suggestions"), bundle,
                ),
                "report_next_steps_text": report_next_steps_text(interpretation, bundle),
            },
            "evidence": [self._evidence(item.model_dump(mode="json")) for item in bundle.evidence[:64]],
            "literature_evidence": list(literature_evidence or [])[:24],
            "opaque_refs": {
                "result_items": [item.id for item in bundle.result_items[:24]],
                "figures": [item.figure_id for item in bundle.figures[:16]],
                "facts": [item["fact_id"] for item in facts],
                "evidence": [item.evidence_id for item in bundle.evidence[:64]],
                "literature_evidence": [
                    str(item.get("evidence_ref"))
                    for item in (literature_evidence or [])[:24]
                ],
                "limitations": [item.limitation_id for item in bundle.limitations[:32]],
                "findings": [str(item.get("finding_id")) for item in [*((interpretation.get("interpretation") or {}).get("primary_findings") or []), *((interpretation.get("interpretation") or {}).get("supporting_findings") or [])] if item.get("finding_id")],
            },
            "omitted_supporting_items": InterpreterInputAssembler._compact_omissions(omitted, limit=64),
        }
        fact_ids = set(payload["opaque_refs"]["facts"])
        for item in [*payload["result"]["result_items"], *payload["result"]["figures"],
                     *payload["result"]["tables"], *payload["evidence"]]:
            for key in ("fact_refs", "supports_fact_refs"):
                if key in item:
                    item[key] = InterpreterInputAssembler._bounded_fact_refs(
                        [ref for ref in item[key] or [] if ref in fact_ids], facts=facts, limit=32)
        # Raw provenance IDs are useful for persistence, never for provider prose.
        payload["result"]["provenance"] = {"source_object_version_ids": [f"source_{i + 1}" for i, _ in enumerate(bundle.source_object_refs)]}
        reference_context = project_reference_context(bundle)
        if reference_context is not None:
            payload["result"]["provenance"].update(reference_context)
        # Validate the complete bounded report context before it crosses the
        # provider boundary. This prevents accidental addition of raw
        # conversation/tool payloads without changing the persisted Result
        # authority or the existing wire shape.
        ReportContextBundle.model_validate(payload)
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
        return payload, fingerprint

    @staticmethod
    def _finding(item: dict[str, Any]) -> dict[str, Any]:
        compact = {key: value for key, value in item.items() if key != "reasoning_assessment"}
        assessment = item.get("reasoning_assessment")
        if isinstance(assessment, dict):
            # Keep scientific qualifications, but not duplicated claim fields or
            # assessor-local supporting aliases that the composer cannot cite.
            # The complete assessment remains in the immutable interpretation.
            compact["reasoning_assessment"] = {
                key: assessment[key]
                for key in (
                    "outcome", "accepted", "required_qualifiers", "method_context",
                    "limitations", "reason_codes", "defects", "severity",
                    "independent_evidence_groups", "contradicting_refs",
                )
                if key in assessment
            }
        return compact

    @staticmethod
    def _compact_visual(item: dict[str, Any]) -> dict[str, Any]:
        return {key: item.get(key) for key in ("figure_id", "figure_type", "table_id", "table_type", "role", "title", "fact_refs", "evidence_refs") if key in item}

    @staticmethod
    def _result_item(item: dict[str, Any]) -> dict[str, Any]:
        return {key: item.get(key) for key in ("id", "result_type", "role", "title", "fact_refs", "evidence_refs", "viewer_binding")}

    @staticmethod
    def _evidence(item: dict[str, Any]) -> dict[str, Any]:
        return {key: item.get(key) for key in ("evidence_id", "evidence_type", "supports_fact_refs", "supports_result_item_refs")}

    @staticmethod
    def _method(item: dict[str, Any]) -> dict[str, Any]:
        return {key: item.get(key) for key in ("method_id", "capability_id", "capability_version", "tool_id", "tool_version", "parameters")}


__all__ = ["ReportComposerInputAssembler"]
