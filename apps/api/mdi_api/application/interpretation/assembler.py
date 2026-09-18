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
    provider_reference_limit = 32

    def assemble(self, *, bundle: ScientificResultBundle, question: str, relevance_status: str, prior_goal: str | None = None) -> tuple[InterpretationInputEnvelope, str]:
        result = bundle.model_dump(mode="json")
        result["relevance_status"] = relevance_status
        omitted: list[str] = []
        # Preserve semantic objects and summary facts, never raw Artifact bytes.
        result["facts"] = self._compact_facts(
            self._select_representative_facts(
                result.get("facts", []),
                omitted,
            )
        )
        result["result_items"] = self._bounded(result.get("result_items", []), 24, "result_item", omitted)
        result.pop("reference_aliases", None)
        result["figures"] = [self._compact_visual(item) for item in self._bounded(result.get("figures", []), 16, "figure", omitted)]
        result["tables"] = [self._compact_visual(item) for item in self._bounded(result.get("tables", []), 16, "table", omitted)]
        result["methods"] = [
            self._compact_method(item)
            for item in self._bounded(result.get("methods", []), 16, "method", omitted)
        ]
        result["limitations"] = [
            self._compact_message(item)
            for item in self._bounded(result.get("limitations", []), 16, "limitation", omitted)
        ]
        result["warnings"] = [
            self._compact_message(item)
            for item in self._bounded(result.get("warnings", []), 16, "warning", omitted)
        ]
        evidence = self._bounded(result.pop("evidence", []), 64, "evidence", omitted)
        result = self._provider_result_projection(result)
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
        fact_group_by_identity = {
            id(facts[index]): key
            for index, key in cls._fact_group_keys(facts).items()
        }
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
                        facts=facts,
                        allowed_fact_ids=allowed_fact_ids,
                        allowed_result_ids=allowed_result_ids,
                        allowed_evidence_ids=allowed_evidence_ids,
                        item_kind="result_item",
                    )
                    for item in result_items
                ],
                "reference_aliases": cls._reference_aliases(
                    facts=facts,
                    evidence=evidence_items,
                    result_items=result_items,
                ),
            }
            represented_evidence = [
                cls._compact_support_edges(
                    item,
                    facts=facts,
                    allowed_fact_ids=allowed_fact_ids,
                    allowed_result_ids=allowed_result_ids,
                    allowed_evidence_ids=allowed_evidence_ids,
                    item_kind="evidence",
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
            removable_group = (
                fact_group_by_identity.get(id(facts[-1]))
                if facts
                else None
            )
            if removable_group is not None:
                removed_items = [
                    item
                    for item in facts
                    if fact_group_by_identity.get(id(item)) == removable_group
                ]
                facts = [
                    item
                    for item in facts
                    if fact_group_by_identity.get(id(item)) != removable_group
                ]
            else:
                removed_items = [facts.pop()]
            for removed in removed_items:
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
        facts: list[Any],
        allowed_fact_ids: set[str],
        allowed_result_ids: set[str],
        allowed_evidence_ids: set[str],
        item_kind: str,
    ) -> dict[str, Any]:
        if item_kind == "result_item":
            represented = {
                key: item.get(key)
                for key in (
                    "id",
                    "result_type",
                    "role",
                    "fact_refs",
                    "evidence_refs",
                )
                if key in item
            }
        elif item_kind == "evidence":
            represented = {
                key: item.get(key)
                for key in (
                    "evidence_id",
                    "evidence_type",
                    "supports_fact_refs",
                    "supports_result_item_refs",
                )
                if key in item
            }
        else:
            raise ValueError(f"unsupported provider item kind: {item_kind}")
        for key, allowed in (
            ("fact_refs", allowed_fact_ids),
            ("supports_fact_refs", allowed_fact_ids),
            ("result_item_refs", allowed_result_ids),
            ("supports_result_item_refs", allowed_result_ids),
            ("evidence_refs", allowed_evidence_ids),
        ):
            if key in represented:
                filtered = [
                    value
                    for value in represented.get(key) or []
                    if str(value) in allowed
                ]
                if key in {"fact_refs", "supports_fact_refs"}:
                    filtered = InterpreterInputAssembler._bounded_fact_refs(
                        filtered,
                        facts=facts,
                        limit=InterpreterInputAssembler.provider_reference_limit,
                    )
                else:
                    filtered = filtered[
                        : InterpreterInputAssembler.provider_reference_limit
                    ]
                represented[key] = filtered
        return represented

    @staticmethod
    def _bounded_fact_refs(
        values: list[Any],
        *,
        facts: list[Any],
        limit: int,
    ) -> list[Any]:
        """Bound provider support edges without splitting a subject group."""

        ordered_values = list(dict.fromkeys(values))
        facts_by_id = {
            str(item.get("fact_id")): item
            for item in facts
            if isinstance(item, dict) and item.get("fact_id")
        }
        group_members: dict[str, list[Any]] = {}
        group_for_value: dict[str, str] = {}
        for value in ordered_values:
            identity = str(value)
            fact = facts_by_id.get(identity)
            subject = (
                str(fact.get("subject_ref") or "")
                if isinstance(fact, dict)
                else ""
            )
            group = f"subject:{subject}" if subject else f"fact:{identity}"
            group_for_value[identity] = group
            group_members.setdefault(group, []).append(value)

        selected: list[Any] = []
        visited: set[str] = set()
        for value in ordered_values:
            group = group_for_value[str(value)]
            if group in visited:
                continue
            visited.add(group)
            members = group_members[group]
            if len(selected) + len(members) <= limit:
                selected.extend(members)
        return selected

    @staticmethod
    def _reference_aliases(
        *,
        facts: list[Any],
        evidence: list[Any],
        result_items: list[Any],
    ) -> dict[str, str]:
        """Expose bounded, deterministic aliases for provider citations.

        Database-generated result-item identifiers are intentionally opaque and
        can be too cumbersome for a model to reproduce reliably.  The aliases
        are only a provider-facing convenience; the interpretation service
        resolves them back to the exact persisted identifiers before grounding
        validation and persistence.
        """

        aliases: dict[str, str] = {}
        for prefix, items, identity_key in (
            ("fact", facts, "fact_id"),
            ("evidence", evidence, "evidence_id"),
            ("result", result_items, "id"),
        ):
            for index, item in enumerate(items, start=1):
                if isinstance(item, dict) and item.get(identity_key):
                    aliases[
                        f"{prefix}_{InterpreterInputAssembler._alphabetic_index(index)}"
                    ] = str(item[identity_key])
        return aliases

    @staticmethod
    def _alphabetic_index(index: int) -> str:
        """Return a stable lowercase alphabetic ordinal without digits."""

        if index < 1:
            raise ValueError("reference alias index must be positive")
        rendered = ""
        value = index
        while value:
            value, remainder = divmod(value - 1, 26)
            rendered = chr(ord("a") + remainder) + rendered
        return rendered

    @classmethod
    def _compact_facts(cls, items: list[Any]) -> list[Any]:
        """Remove source/display identifiers while preserving scientific facts."""

        subject_aliases: dict[str, str] = {}
        represented: list[Any] = []
        for item in items:
            if not isinstance(item, dict):
                represented.append(item)
                continue
            subject = str(item.get("subject_ref") or "")
            if subject and subject not in subject_aliases:
                subject_aliases[subject] = (
                    f"subject_{cls._alphabetic_index(len(subject_aliases) + 1)}"
                )
            represented.append(
                {
                    key: value
                    for key, value in (
                        ("fact_id", item.get("fact_id")),
                        ("predicate", item.get("predicate")),
                        ("subject_ref", subject_aliases.get(subject)),
                        ("value", item.get("value")),
                        ("unit", item.get("unit")),
                        ("uncertainty", item.get("uncertainty")),
                    )
                    if value is not None
                }
            )
        return represented

    @staticmethod
    def _compact_method(item: dict[str, Any]) -> dict[str, Any]:
        return {
            key: item.get(key)
            for key in ("capability_id", "capability_version", "parameters")
            if key in item
        }

    @staticmethod
    def _compact_message(item: dict[str, Any]) -> dict[str, Any]:
        return {
            key: item.get(key)
            for key in ("code", "message")
            if key in item
        }

    @staticmethod
    def _provider_result_projection(result: dict[str, Any]) -> dict[str, Any]:
        """Expose only scientific interpretation fields to the provider."""

        return {
            key: result.get(key)
            for key in (
                "schema_version",
                "research_question",
                "execution_status",
                "relevance_status",
                "result_items",
                "facts",
                "figures",
                "tables",
                "methods",
                "limitations",
                "warnings",
            )
            if key in result
        }

    @staticmethod
    def _compact_visual(item: dict[str, Any]) -> dict[str, Any]:
        return {
            key: item.get(key)
            for key in (
                "figure_type",
                "table_type",
                "role",
                "fact_refs",
                "evidence_refs",
            )
            if key in item
        }

    @classmethod
    def _select_representative_facts(
        cls,
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
        group_keys = cls._fact_group_keys(items, predicate_counts)
        summary_indices = [
            index
            for index, item in enumerate(items)
            if not isinstance(item, dict)
            or predicate_counts[str(item.get("predicate") or "")] <= 8
        ]
        selected_indices = summary_indices[:limit]
        selected_index_set = set(selected_indices)
        if len(selected_indices) < limit:
            groups: dict[str, list[int]] = {}
            for index, key in group_keys.items():
                groups.setdefault(key, []).append(index)
            for key in sorted(groups, key=lambda value: min(groups[value])):
                members = groups[key]
                if len(selected_indices) + len(members) > limit:
                    continue
                selected_indices.extend(members)
                selected_index_set.update(members)
        if not selected_indices:
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

    @classmethod
    def _fact_group_keys(
        cls,
        items: list[Any],
        predicate_counts: Counter[str] | None = None,
    ) -> dict[int, str]:
        """Identify bounded complete detail groups without naming a Tool.

        Result projectors may emit a compact summary followed by repeated rows.
        Preserving complete subject groups keeps related observations together
        for grounding (for example target/prediction/residual) without widening
        the provider input beyond the existing fact limit.
        """

        counts = predicate_counts or Counter(
            str(item.get("predicate") or "")
            for item in items
            if isinstance(item, dict)
        )
        subjects = Counter(
            str(item.get("subject_ref") or "")
            for item in items
            if isinstance(item, dict) and item.get("subject_ref")
        )
        distinct_subjects = {subject for subject in subjects if subject}
        if len(distinct_subjects) < 2:
            return {}
        grouped_subjects = {
            subject for subject, count in subjects.items() if count >= 2
        }
        # Row-level dataset projections commonly pair an identity and a
        # display label (for example ``sample_id`` + ``formula``) under one
        # subject.  Those pairs are useful for a table viewer, but are not
        # scientific evidence for a general interpretation and can cause a
        # provider to enumerate row identifiers as if they were measurements.
        # Keep complete groups only when they contain at least one
        # non-identity/detail predicate.
        identity_only_suffixes = {
            "id",
            "sample_id",
            "row_id",
            "frame_id",
            "index",
            "sample_index",
            "formula",
            "name",
            "label",
        }
        group_predicates: dict[str, set[str]] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            subject = str(item.get("subject_ref") or "")
            if subject in grouped_subjects:
                predicate = str(item.get("predicate") or "").rsplit(".", 1)[-1]
                group_predicates.setdefault(subject, set()).add(predicate)
        scientific_groups = {
            subject
            for subject, predicates in group_predicates.items()
            if any(
                predicate not in identity_only_suffixes
                for predicate in predicates
            )
        }
        return {
            index: subject
            for index, item in enumerate(items)
            if isinstance(item, dict)
            and (subject := str(item.get("subject_ref") or "")) in grouped_subjects
            and subject in scientific_groups
            and counts[str(item.get("predicate") or "")] > 8
        }

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
