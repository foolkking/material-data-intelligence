from __future__ import annotations

import json
from typing import Any, Callable

from mdi_api.research_agent.context.fingerprint import context_fingerprint
from mdi_api.research_agent.context.schemas import (
    CompactObjectSummary,
    CompactFindingSummary,
    CompactResearchContext,
    CompactScientificSelection,
    CompactResultSummary,
    ReferenceCandidateSource,
    ResearchContextCandidateBundle,
)


COMPILER_VERSION = "agent2.context-compiler/1.2"


class ResearchContextCompiler:
    def compile(
        self,
        *,
        turn: dict[str, Any],
        candidates: ResearchContextCandidateBundle,
        token_budget: int = 12_000,
        input_payload: Callable[[CompactResearchContext], dict[str, Any]] | None = None,
    ) -> CompactResearchContext:
        if token_budget < 256:
            raise ValueError("token_budget must be at least 256")
        object_keys = {
            (item.object_ref.object_id, item.object_ref.version_id): item.candidate_key
            for item in candidates.active_object_candidates
        }
        selections = [CompactScientificSelection(
            ref_key=object_keys[(item.object_ref.object_id, item.object_ref.version_id)],
            selection_type=item.selection_type,
            semantic_locator=item.semantic_locator,
        ) for item in candidates.scientific_selections]
        required_object_keys = {item.ref_key for item in selections} | {
            item.candidate_key for item in candidates.active_object_candidates
            if item.source in {ReferenceCandidateSource.UI_SELECTION, ReferenceCandidateSource.EXPLICIT_REFERENCE}
        }
        object_summaries = [CompactObjectSummary(
            ref_key=item.candidate_key,
            object_type=item.object_ref.object_type,
            display_name=item.display_label,
            availability_status="STALE" if item.stale else "AVAILABLE",
            version_label="exact_version",
            summary={
                "semantic_summary": item.semantic_summary,
                "source": item.source.value,
                "source_class": item.source_class.value if item.source_class else None,
                "authority_class": item.authority_class.value if item.authority_class else None,
                "freshness": item.freshness.value if item.freshness else "UNKNOWN",
                "epistemic_status": item.epistemic_status.value if item.epistemic_status else "OBSERVED",
                "source_ref": item.source_ref,
            },
            context_role="SUBJECT",
            support_eligible=False,
        ) for item in candidates.active_object_candidates]
        result_summaries = [CompactResultSummary(
            ref_key=item.candidate_key,
            result_id=item.result_id,
            research_question=item.display_label,
            execution_status="HISTORICAL",
            relevance_status="STALE" if item.stale else "CURRENT",
            summary=(
                f"{item.semantic_summary or 'Persisted scientific result snapshot'} "
                f"[source={item.source_ref or item.result_id}; "
                f"freshness={item.freshness.value if item.freshness else 'UNKNOWN'}]"
            ),
            context_role="EVIDENCE",
            support_eligible=item.support_eligible,
        ) for item in candidates.result_candidates]
        required_result_keys = {
            item.candidate_key for item in candidates.result_candidates
            if item.result_id in candidates.pinned_result_ids
            or item.source in {
                ReferenceCandidateSource.EXPLICIT_REFERENCE,
                ReferenceCandidateSource.UI_SELECTION,
                ReferenceCandidateSource.PINNED_CONTEXT,
                ReferenceCandidateSource.PREVIOUS_TURN_RESULT,
            }
        }
        finding_summaries = [CompactFindingSummary(
            ref_key=item.candidate_key,
            display_label=item.display_label,
            summary=item.semantic_summary or "Persisted finding reference",
            relevance_status=item.freshness.value if item.freshness else ("STALE" if item.stale else "CURRENT"),
            context_role="EVIDENCE",
            support_eligible=item.support_eligible,
        ) for item in candidates.finding_candidates]
        fingerprint_payload = {
            "project_id": candidates.project_id,
            "turn_id": str(candidates.research_turn_id),
            "current_user_message": candidates.current_user_message,
            "current_goal": candidates.current_research_goal,
            "objects": [
                [item.candidate_key, str(item.object_ref.object_id), str(item.object_ref.version_id)]
                for item in candidates.active_object_candidates
            ],
            "results": [
                [item.candidate_key, str(item.result_id), "STALE" if item.stale else "CURRENT"]
                for item in candidates.result_candidates
            ],
            "scientific_selections": [item.model_dump(mode="json") for item in selections],
            "constraints": candidates.explicit_constraints,
            "pinned_result_ids": [str(item) for item in candidates.pinned_result_ids],
            "resolved_references": [],
            "recent_turn_ids": [str(item) for item in candidates.recent_turn_ids],
            "compiler_version": COMPILER_VERSION,
        }
        fingerprint = context_fingerprint(fingerprint_payload)
        messages = list(candidates.recent_messages)
        unresolved = list(candidates.unresolved_questions)
        objects = object_summaries
        results = result_summaries
        findings = finding_summaries
        max_bytes = token_budget * 4

        while True:
            compact = CompactResearchContext(
                project_summary="Authorized material-research project context",
                current_goal=candidates.current_research_goal,
                current_user_message=candidates.current_user_message,
                objects=objects,
                scientific_selections=selections,
                results=results,
                relevant_findings=findings,
                pinned_results=[item for item in results if item.result_id in set(candidates.pinned_result_ids)],
                relevant_prior_turns=[
                    f"prior_turn_{index}"
                    for index, _turn_id in enumerate(candidates.recent_turn_ids, start=1)
                ],
                explicit_constraints=candidates.explicit_constraints,
                unresolved_questions=unresolved,
                recent_conversation=messages,
                omitted_supporting_items=list(candidates.omitted_supporting_items),
                context_fingerprint=fingerprint,
            )
            # Use the same JSON representation as the actual-input manifest.
            # The orchestrator supplies its complete envelope, including the
            # current question, requirement schemas and permitted actions.
            payload = input_payload(compact) if input_payload else compact.model_dump(mode="json")
            encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
            if len(encoded.encode("utf-8")) <= max_bytes:
                return compact
            if messages:
                messages = messages[1:]
            elif unresolved:
                unresolved = unresolved[1:]
            elif findings:
                findings = findings[:-1]
            elif len(results) > 1:
                # Preserve pinned and explicitly referenced candidates; trim
                # only lower-priority historical candidates.
                removable = next((i for i in range(len(results) - 1, -1, -1) if results[i].ref_key not in required_result_keys), None)
                if removable is None:
                    raise ValueError("Selected scientific context cannot fit within token_budget")
                results.pop(removable)
            elif len(objects) > 1:
                removable = next((i for i in range(len(objects) - 1, 0, -1)
                                  if objects[i].ref_key not in required_object_keys), None)
                if removable is None:
                    raise ValueError("Selected scientific context cannot fit within token_budget")
                objects = objects[:removable] + objects[removable + 1:]
            else:
                raise ValueError("Research context cannot fit within token_budget")
