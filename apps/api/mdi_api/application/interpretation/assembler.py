from __future__ import annotations

import hashlib
import json
from collections import Counter
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
        result["facts"] = self._select_representative_facts(
            result.get("facts", []),
            omitted,
        )
        result["result_items"] = self._bounded(result.get("result_items", []), 24, "result_item", omitted)
        result["figures"] = [self._compact_visual(item) for item in self._bounded(result.get("figures", []), 16, "figure", omitted)]
        result["tables"] = [self._compact_visual(item) for item in self._bounded(result.get("tables", []), 16, "table", omitted)]
        result["methods"] = self._bounded(result.get("methods", []), 16, "method", omitted)
        result["limitations"] = self._bounded(result.get("limitations", []), 16, "limitation", omitted)
        result["warnings"] = self._bounded(result.get("warnings", []), 16, "warning", omitted)
        evidence = self._bounded(result.pop("evidence", []), 64, "evidence", omitted)
        envelope = self._fit_operation_budget(
            result=result,
            evidence=evidence,
            question=question,
            prior_goal=prior_goal,
            omitted=omitted,
        )
        fingerprint = hashlib.sha256(json.dumps(envelope.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        return envelope, fingerprint

    @classmethod
    def _fit_operation_budget(
        cls,
        *,
        result: dict[str, Any],
        evidence: list[dict[str, Any]],
        question: str,
        prior_goal: str | None,
        omitted: list[str],
    ) -> InterpretationInputEnvelope:
        """Fit the actual provider representation without hiding omissions."""

        facts = list(result.get("facts") or [])
        result_items = list(result.get("result_items") or [])
        evidence_items = list(evidence)
        # Import lazily because the repository factory imports interpretation
        # ports while the Research package initializes its persistence layer.
        # A module-level dependency here creates a production-only circular
        # import even though isolated interpretation tests can mask it.
        from mdi_api.research_agent.context.policy import (
            ContextOperation,
            context_budget_policy,
        )

        budget = context_budget_policy(
            ContextOperation.INTERPRETER
        ).effective_input_budget

        while True:
            allowed_fact_ids = {
                str(item.get("fact_id"))
                for item in facts
                if isinstance(item, dict) and item.get("fact_id")
            }
            allowed_result_ids = {
                str(item.get("id"))
                for item in result_items
                if isinstance(item, dict) and item.get("id")
            }
            allowed_evidence_ids = {
                str(item.get("evidence_id"))
                for item in evidence_items
                if isinstance(item, dict) and item.get("evidence_id")
            }
            represented_result = {
                **result,
                "facts": facts,
                "result_items": [
                    cls._compact_support_edges(
                        item,
                        allowed_fact_ids=allowed_fact_ids,
                        allowed_result_ids=allowed_result_ids,
                        allowed_evidence_ids=allowed_evidence_ids,
                    )
                    for item in result_items
                ],
            }
            represented_evidence = [
                cls._compact_support_edges(
                    item,
                    allowed_fact_ids=allowed_fact_ids,
                    allowed_result_ids=allowed_result_ids,
                    allowed_evidence_ids=allowed_evidence_ids,
                )
                for item in evidence_items
            ]
            envelope = InterpretationInputEnvelope(
                contract_version="1.0",
                research_question=question[:16000],
                result=represented_result,
                evidence=represented_evidence,
                conversation_context={
                    "user_question": question[:4000],
                    "relevant_prior_goal": prior_goal,
                },
                omitted_supporting_items=omitted,
            )
            encoded = json.dumps(
                envelope.model_dump(mode="json"),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            if max(1, len(encoded) // 4) <= budget:
                return envelope
            if len(facts) <= 1:
                raise ValueError(
                    "bounded interpreter representation cannot fit the operation budget"
                )
            removed = facts.pop()
            identity = (
                removed.get("fact_id")
                if isinstance(removed, dict)
                else len(facts)
            )
            omitted.append(f"fact:{identity}")

    @staticmethod
    def _compact_support_edges(
        item: dict[str, Any],
        *,
        allowed_fact_ids: set[str],
        allowed_result_ids: set[str],
        allowed_evidence_ids: set[str],
    ) -> dict[str, Any]:
        represented = dict(item)
        for key, allowed in (
            ("fact_refs", allowed_fact_ids),
            ("supports_fact_refs", allowed_fact_ids),
            ("result_item_refs", allowed_result_ids),
            ("supports_result_item_refs", allowed_result_ids),
            ("evidence_refs", allowed_evidence_ids),
        ):
            if key in represented:
                represented[key] = [
                    value
                    for value in represented.get(key) or []
                    if str(value) in allowed
                ]
        return represented

    @staticmethod
    def _compact_visual(item: dict[str, Any]) -> dict[str, Any]:
        return {key: item.get(key) for key in ("figure_id", "figure_type", "table_id", "table_type", "role", "title", "fact_refs", "evidence_refs") if key in item}

    @staticmethod
    def _select_representative_facts(
        items: list[Any],
        omitted: list[str],
        *,
        limit: int = 64,
    ) -> list[Any]:
        """Prefer summary predicates over repetitive row/atom/frame details.

        Canonical Results may contain hundreds of exact per-item facts. Sending
        the first 64 can accidentally turn a dataset overview into a list of
        sample identifiers and formulas while excluding the more useful
        aggregate scientific boundary. The full Result remains authoritative;
        this is only a deterministic, omission-accounted model
        representation.
        """

        if len(items) <= limit:
            return list(items)
        predicate_counts = Counter(
            str(item.get("predicate") or "")
            for item in items
            if isinstance(item, dict)
        )
        summary_indices = [
            index
            for index, item in enumerate(items)
            if not isinstance(item, dict)
            or predicate_counts[str(item.get("predicate") or "")] <= 8
        ]
        if summary_indices:
            selected_indices = summary_indices[:limit]
        else:
            # A Result containing only repeated detail predicates still gets a
            # small deterministic sample, with the full omission ledger and
            # canonical counts retained elsewhere in the Result.
            selected_indices = list(range(min(limit, 16)))
        selected_index_set = set(selected_indices)
        for index, item in enumerate(items):
            if index in selected_index_set:
                continue
            identity = (
                next(
                    (
                        item.get(key)
                        for key in ("fact_id", "id")
                        if item.get(key)
                    ),
                    index,
                )
                if isinstance(item, dict)
                else index
            )
            omitted.append(f"fact:{identity}")
        return [items[index] for index in selected_indices]

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
