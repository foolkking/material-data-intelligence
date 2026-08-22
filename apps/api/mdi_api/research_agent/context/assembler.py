from __future__ import annotations

from datetime import datetime
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
        ui_context = ((received or {}).get("payload_json") or {}).get("ui_context") or {}
        selection_refs = list(ui_context.get("selection_refs") or [])
        active_refs = list(ui_context.get("active_object_refs") or [])
        previous_turns = unit.agent2.research_turns.list_recent_before(session_id, current_sequence, limit=6)

        raw_objects: list[tuple[ReferenceCandidateSource, int, dict[str, Any]]] = []
        raw_objects.extend((ReferenceCandidateSource.UI_SELECTION, 0, item) for item in selection_refs)
        raw_objects.extend((ReferenceCandidateSource.CURRENT_SCOPE, 0, item) for item in active_refs)
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
        result_rows = unit.agent2.scientific_result_snapshots.list_recent_for_session(
            session_id, before_sequence=current_sequence, limit=6,
        )
        results = []
        for index, row in enumerate(result_rows, start=1):
            bundle = dict(row.get("bundle_json") or {})
            results.append(ReferenceCandidate(
                candidate_key=f"result_{index}",
                ref_type="SCIENTIFIC_RESULT",
                result_id=row["id"],
                source=ReferenceCandidateSource.PREVIOUS_TURN_RESULT,
                display_label=str(bundle.get("research_question") or f"Previous result {index}")[:512],
                semantic_summary=self._bounded_summary(bundle),
                recency_rank=index - 1,
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
            finding_candidates=[],
            explicit_constraints=list((latest_snapshot or {}).get("effective_constraints_json") or []),
            current_research_goal=(latest_snapshot or {}).get("research_goal"),
            unresolved_questions=list((latest_snapshot or {}).get("unresolved_questions_json") or []),
            recent_messages=messages[-12:],
            recent_turn_ids=[item["id"] for item in reversed(previous_turns)],
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
