from __future__ import annotations

from typing import Any
from uuid import UUID

from mdi_api.research_agent.context.schemas import (
    CompactMessage,
    ReferenceCandidate,
    ReferenceCandidateSource,
    ResearchContextCandidateBundle,
)
from mdi_api.scientific_objects.schemas import ScientificObjectRef


_MAX_MESSAGE_CHARS = 4000
_MAX_OBJECT_CANDIDATES = 80
_TRUNCATION_MARKER = "\n[deterministically truncated]"


class ResearchContextCandidateAssembler:
    """Build a bounded, authorized candidate set from database-owned state."""

    def assemble(self, unit: Any, turn: dict[str, Any]) -> ResearchContextCandidateBundle:
        project_id = str(turn["project_id"])
        session_id = str(turn["research_session_id"])
        current_sequence = int(turn["sequence_no"])
        received = next(
            (event for event in unit.agent2.research_turn_events.list_for_turn(turn["id"])
             if event["event_type"] == "TURN_RECEIVED"),
            None,
        )
        current_messages = unit.agent2.research_turns.referenced_messages(turn)
        current_user_message = next((str(row["content_summary"]) for row in current_messages if row["role"] == "user"), None)
        ui_context = ((received or {}).get("payload_json") or {}).get("ui_context") or {}
        selection_refs = list(ui_context.get("selection_refs") or [])
        scientific_selections = list(ui_context.get("scientific_selections") or [])
        selection_refs.extend(
            item["object_ref"]
            for item in scientific_selections
            if isinstance(item, dict) and isinstance(item.get("object_ref"), dict)
        )
        active_refs = list(ui_context.get("active_object_refs") or [])
        explicit_refs = list(ui_context.get("explicit_object_refs") or [])
        previous_turns = unit.agent2.research_turns.list_recent_before(session_id, current_sequence, limit=6)
        long_turns = unit.agent2.research_turns.list_all_before(session_id, current_sequence, limit=500)
        memory_state = unit.agent2.research_session_memory.get_state(session_id)

        raw_objects: list[tuple[ReferenceCandidateSource, int, dict[str, Any]]] = []
        raw_objects.extend((ReferenceCandidateSource.EXPLICIT_REFERENCE, 0, item) for item in explicit_refs)
        raw_objects.extend((ReferenceCandidateSource.UI_SELECTION, 0, item) for item in selection_refs)
        raw_objects.extend((ReferenceCandidateSource.CURRENT_SCOPE, 0, item) for item in active_refs)
        if memory_state:
            raw_objects.extend((ReferenceCandidateSource.PINNED_CONTEXT, 0, item) for item in (memory_state.get("active_scope_refs_json") or []))
            raw_objects.extend((ReferenceCandidateSource.PINNED_CONTEXT, 0, item) for item in (memory_state.get("pinned_object_refs_json") or []))
        if turn.get("parent_turn_id"):
            parent_snapshot = unit.agent2.research_context_snapshots.get_for_turn(turn["parent_turn_id"])
            parent_refs = []
            for item in (parent_snapshot or {}).get("resolved_references_json") or []:
                raw = item.get("object_ref") if isinstance(item, dict) else None
                if raw:
                    parent_refs.append((item, raw))
            lexical_matches = [raw for item, raw in parent_refs if str(item.get("display_label") or "").lower() in (current_user_message or "").lower()]
            if len(lexical_matches) == 1:
                raw_objects.append((ReferenceCandidateSource.EXPLICIT_REFERENCE, 0, lexical_matches[0]))
            else:
                raw_objects.extend((ReferenceCandidateSource.CURRENT_SCOPE, 0, raw) for _, raw in parent_refs)
        for recency, previous in enumerate(previous_turns, start=1):
            snapshot = unit.agent2.research_context_snapshots.get_for_turn(previous["id"])
            if snapshot is None:
                continue
            raw_objects.extend(
                (ReferenceCandidateSource.RECENT_CONTEXT, recency, item)
                for item in (snapshot["selection_refs_json"] or [])
            )
            raw_objects.extend(
                (ReferenceCandidateSource.RECENT_CONTEXT, recency, item)
                for item in (snapshot["active_scope_refs_json"] or [])
            )

        objects = self._object_candidates(unit, project_id, raw_objects)
        result_rows: list[tuple[ReferenceCandidateSource, int, dict[str, Any]]] = []
        # An explicit result selection is an authoritative user/UI binding.
        # Do not mix it with recency-derived historical candidates: doing so
        # lets the provider select a lower-priority result and then correctly
        # fail deterministic reference validation, even though the requested
        # result itself is authorized. Supporting results can still be
        # selected explicitly by supplying multiple snapshot IDs.
        explicit_result_ids = {str(x) for x in (ui_context.get("explicit_result_ids") or [])}
        pinned_ids = [str(x) for x in ((memory_state or {}).get("pinned_result_refs_json") or [])]
        # Child turns represent an explicit new branch (edit/rerun/retry)
        # unless they bind a result directly.  Do not silently inject
        # recency-based result candidates into those branches: doing so can
        # make the router choose INTERPRET_RESULT for a newly edited question
        # and mix unrelated historical results into grounding.
        if not explicit_result_ids and not turn.get("parent_turn_id"):
            for recency, previous in enumerate(long_turns, start=1):
                snapshot = unit.agent2.scientific_result_snapshots.get_latest_for_turn(previous["id"]) if unit.agent2.scientific_result_snapshots.exists_for_turn(previous["id"]) else None
                if snapshot is None:
                    continue
                source = ReferenceCandidateSource.PINNED_CONTEXT if str(snapshot["id"]) in pinned_ids else (
                    ReferenceCandidateSource.PREVIOUS_TURN_RESULT if recency == 1 else (
                        ReferenceCandidateSource.RECENT_CONTEXT if recency <= 6 else ReferenceCandidateSource.LONG_SESSION_RETRIEVAL
                    )
                )
                result_rows.append((source, 0 if source == ReferenceCandidateSource.PINNED_CONTEXT else recency, snapshot))
        # Explicit lexical references are resolved only when exactly one
        # authorized persisted result matches a registered scientific-family
        # token. This deterministic elevation supports non-adjacent references
        # without letting the model invent identities.
        message_lower = (current_user_message or "").lower()
        family_tokens = ("rdf", "xrd", "msd", "diffusion", "phonon", "regression", "回归", "声子", "扩散")
        for token in family_tokens:
            if token not in message_lower:
                continue
            matches = []
            for _, _, row in result_rows:
                bundle = dict(row.get("bundle_json") or {})
                searchable = " ".join([
                    str(bundle.get("research_question") or ""),
                    *(str(item.get("result_type") or "") for item in (bundle.get("result_items") or []) if isinstance(item, dict)),
                ]).lower()
                if token in searchable:
                    matches.append(row)
            unique = {str(item["id"]): item for item in matches}
            if len(unique) == 1:
                result_rows.append((ReferenceCandidateSource.EXPLICIT_REFERENCE, 0, next(iter(unique.values()))))
        for result_id in explicit_result_ids:
            row = unit.agent2.scientific_result_snapshots.get(UUID(result_id))
            if str(row["project_id"]) != project_id or row["research_turn_id"] not in {item["id"] for item in long_turns}:
                raise ValueError("Unauthorized explicit scientific result reference")
            result_rows.append((ReferenceCandidateSource.EXPLICIT_REFERENCE, 0, row))
        dedup_results: dict[str, tuple[ReferenceCandidateSource, int, dict[str, Any]]] = {}
        priority = {
            ReferenceCandidateSource.EXPLICIT_REFERENCE: 0,
            ReferenceCandidateSource.UI_SELECTION: 1,
            ReferenceCandidateSource.CURRENT_SCOPE: 2,
            ReferenceCandidateSource.PREVIOUS_TURN_RESULT: 3,
            ReferenceCandidateSource.PREVIOUS_TURN: 3,
            ReferenceCandidateSource.PINNED_CONTEXT: 4,
            ReferenceCandidateSource.RECENT_CONTEXT: 5,
            ReferenceCandidateSource.LONG_SESSION_RETRIEVAL: 6,
        }
        for source, recency, row in result_rows:
            key = str(row["id"])
            current = dedup_results.get(key)
            if current is None or (priority[source], recency) < (priority[current[0]], current[1]):
                dedup_results[key] = (source, recency, row)
        ordered_results = sorted(dedup_results.values(), key=lambda item: (priority[item[0]], item[1], str(item[2]["id"])))[:16]
        results = []
        finding_rows: list[ReferenceCandidate] = []
        for index, (source, recency, row) in enumerate(ordered_results, start=1):
            bundle = dict(row.get("bundle_json") or {})
            results.append(ReferenceCandidate(
                candidate_key=f"result_{index}",
                ref_type="SCIENTIFIC_RESULT",
                result_id=row["id"],
                source=source,
                display_label=str(bundle.get("research_question") or f"Previous result {index}")[:512],
                semantic_summary=self._bounded_summary(bundle),
                recency_rank=recency,
                stale=str(row["relevance_status"]) != "CURRENT",
            ))
            for fact in (bundle.get("facts") or [])[:4]:
                if not isinstance(fact, dict) or not fact.get("fact_id"):
                    continue
                finding_rows.append(ReferenceCandidate(
                    candidate_key=f"finding_{len(finding_rows) + 1}",
                    ref_type="SCIENTIFIC_FINDING", finding_ref=str(fact["fact_id"]),
                    source=source, display_label=str(fact.get("predicate") or fact["fact_id"])[:512],
                    semantic_summary=str(fact.get("value") or "")[:2000], recency_rank=recency,
                    stale=str(row["relevance_status"]) != "CURRENT",
                ))

        messages: list[CompactMessage] = []
        for previous in reversed(previous_turns):
            for row in unit.agent2.research_turns.referenced_messages(previous):
                content = str(row["content_summary"] or "").strip()
                if not content:
                    continue
                messages.append(CompactMessage(
                    role="ASSISTANT" if row["role"] == "agent" else "USER",
                    turn_sequence_no=int(previous["sequence_no"]),
                    content=self._truncate(content),
                    created_at=row["created_at"],
                ))
        latest_snapshot = None
        for item in previous_turns:
            latest_snapshot = unit.agent2.research_context_snapshots.get_for_turn(item["id"])
            if latest_snapshot is not None:
                break
        return ResearchContextCandidateBundle(
            project_id=project_id,
            research_session_id=session_id,
            research_turn_id=turn["id"],
            active_object_candidates=objects,
            result_candidates=results,
            finding_candidates=finding_rows[:16],
            explicit_constraints=list((memory_state or {}).get("session_constraints_json") or []) or list((latest_snapshot or {}).get("effective_constraints_json") or []),
            current_research_goal=(memory_state or {}).get("active_research_goal") or (latest_snapshot or {}).get("research_goal"),
            unresolved_questions=list((latest_snapshot or {}).get("unresolved_questions_json") or []),
            recent_messages=messages[-12:],
            recent_turn_ids=[item["id"] for item in reversed(previous_turns)],
            pinned_result_ids=[UUID(str(x)) for x in pinned_ids[:64]],
            omitted_supporting_items=[] if len(ordered_results) <= 16 else ["additional historical results omitted by candidate budget"],
            current_user_message=current_user_message,
        )

    @staticmethod
    def _object_candidates(
        unit: Any,
        project_id: str,
        rows: list[tuple[ReferenceCandidateSource, int, dict[str, Any]]],
    ) -> list[ReferenceCandidate]:
        deduplicated: dict[tuple[str, str], tuple[ReferenceCandidateSource, int, ScientificObjectRef, dict[str, Any], dict[str, Any]]] = {}
        priority = {
            ReferenceCandidateSource.EXPLICIT_REFERENCE: 0,
            ReferenceCandidateSource.UI_SELECTION: 1,
            ReferenceCandidateSource.CURRENT_SCOPE: 2,
            ReferenceCandidateSource.PREVIOUS_TURN_RESULT: 3,
            ReferenceCandidateSource.PREVIOUS_TURN: 3,
            ReferenceCandidateSource.PINNED_CONTEXT: 4,
            ReferenceCandidateSource.RECENT_CONTEXT: 5,
        }
        for source, recency, raw in rows:
            ref = ScientificObjectRef.model_validate(raw)
            logical = unit.agent2.scientific_objects.get_object(ref.object_id)
            version = unit.agent2.scientific_objects.get_version(ref.version_id)
            if (
                str(logical["project_id"]) != project_id
                or str(ref.project_id) != project_id
                or version["scientific_object_id"] != ref.object_id
                or str(logical["object_type"]) != ref.object_type
                or str(version["object_type"]) != ref.object_type
            ):
                raise ValueError("Unauthorized scientific context reference")
            identity = (str(ref.object_id), str(ref.version_id))
            current = deduplicated.get(identity)
            if current is None or (priority[source], recency) < (priority[current[0]], current[1]):
                deduplicated[identity] = (source, recency, ref, logical, version)
        ordered = sorted(
            deduplicated.values(),
            key=lambda item: (priority[item[0]], item[1], str(item[2].object_id), str(item[2].version_id)),
        )[:_MAX_OBJECT_CANDIDATES]
        # Once an exact UI/deep-link reference exists, lower-priority project
        # history is not an alternative scope. Keeping it in the LLM candidate
        # set lets a provider manufacture a clarification despite the frozen
        # explicit-reference precedence rule. Retain all candidates only when
        # they share the same effective priority (for example, a bounded set of
        # explicitly selected sites).
        if ordered:
            best_priority = priority[ordered[0][0]]
            ordered = [item for item in ordered if priority[item[0]] == best_priority]
        return [ReferenceCandidate(
            candidate_key=f"obj_{index}",
            ref_type="SCIENTIFIC_OBJECT",
            object_ref=ref,
            source=source,
            display_label=str(ref.display_name or logical["display_name"]),
            semantic_summary=str((version.get("canonical_metadata_json") or {}).get("summary") or ref.object_type)[:2000],
            recency_rank=recency,
            stale=str(version.get("availability_status")) != "AVAILABLE",
        ) for index, (source, recency, ref, logical, version) in enumerate(ordered, start=1)]

    @staticmethod
    def _truncate(content: str) -> str:
        if len(content) <= _MAX_MESSAGE_CHARS:
            return content
        return content[: _MAX_MESSAGE_CHARS - len(_TRUNCATION_MARKER)] + _TRUNCATION_MARKER

    @staticmethod
    def _bounded_summary(bundle: dict[str, Any]) -> str:
        items = bundle.get("result_items") or []
        titles = [str(item.get("title")) for item in items[:3] if isinstance(item, dict) and item.get("title")]
        value = "; ".join(titles) or "Persisted scientific result snapshot"
        return value[:2000]
