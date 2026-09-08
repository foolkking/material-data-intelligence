from __future__ import annotations

import hashlib
import json
from typing import Any

from mdi_api.domain.scientific_results.relevance import ScientificResultRelevanceEvaluator
from mdi_api.domain.scientific_results.contracts import ScientificResultBundle

from mdi_api.domain.interpretation.contracts import InterpretationInputEnvelope


class InterpreterInputAssembler:
    """Build a bounded provider envelope from a persisted Result snapshot."""

    version = "agent2.interpreter-input/1.0"

    def assemble(self, *, bundle: ScientificResultBundle, question: str, relevance_status: str, prior_goal: str | None = None) -> tuple[InterpretationInputEnvelope, str]:
        result = bundle.model_dump(mode="json")
        result["relevance_status"] = relevance_status
        omitted: list[str] = []
        # Preserve semantic objects and summary facts, never raw Artifact bytes.
        result["facts"] = self._bounded(result.get("facts", []), 64, "fact", omitted)
        result["result_items"] = self._bounded(result.get("result_items", []), 24, "result_item", omitted)
        result["figures"] = [self._compact_visual(item) for item in self._bounded(result.get("figures", []), 16, "figure", omitted)]
        result["tables"] = [self._compact_visual(item) for item in self._bounded(result.get("tables", []), 16, "table", omitted)]
        result["methods"] = self._bounded(result.get("methods", []), 16, "method", omitted)
        result["limitations"] = self._bounded(result.get("limitations", []), 16, "limitation", omitted)
        result["warnings"] = self._bounded(result.get("warnings", []), 16, "warning", omitted)
        evidence = self._bounded(result.pop("evidence", []), 64, "evidence", omitted)
        envelope = InterpretationInputEnvelope(
            contract_version="1.0",
            research_question=question[:16000],
            result=result,
            evidence=evidence,
            conversation_context={"user_question": question[:4000], "relevant_prior_goal": prior_goal},
            omitted_supporting_items=omitted,
        )
        fingerprint = hashlib.sha256(json.dumps(envelope.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        return envelope, fingerprint

    @staticmethod
    def _compact_visual(item: dict[str, Any]) -> dict[str, Any]:
        return {key: item.get(key) for key in ("figure_id", "figure_type", "table_id", "table_type", "role", "title", "fact_refs", "evidence_refs") if key in item}

    @staticmethod
    def _bounded(items: list[Any], limit: int, label: str, omitted: list[str]) -> list[Any]:
        for index, item in enumerate(items[limit:], start=limit):
            if isinstance(item, dict):
                identity = next((item.get(key) for key in ("fact_id", "id", "evidence_id", "figure_id", "table_id", "method_id", "limitation_id", "warning_id") if item.get(key)), index)
            else:
                identity = index
            omitted.append(f"{label}:{identity}")
        return items[:limit]


def effective_relevance(bundle: ScientificResultBundle, *, objects: dict[str, dict[str, Any]], versions: dict[str, dict[str, Any]]) -> str:
    return ScientificResultRelevanceEvaluator().evaluate(bundle.source_object_refs, objects=objects, versions=versions).value


__all__ = ["InterpreterInputAssembler", "effective_relevance"]
