from __future__ import annotations

from typing import Any

from mdi_api.research_agent.context.fingerprint import context_fingerprint
from mdi_api.research_agent.context.schemas import (
    CompactObjectSummary,
    CompactResearchContext,
    CompactResultSummary,
    ResearchContextCandidateBundle,
)


COMPILER_VERSION = "agent2.context-compiler/1.0"


class ResearchContextCompiler:
    def compile(
        self,
        *,
        turn: dict[str, Any],
        candidates: ResearchContextCandidateBundle,
        token_budget: int = 12_000,
    ) -> CompactResearchContext:
        if token_budget < 256:
            raise ValueError("token_budget must be at least 256")
        object_summaries = [CompactObjectSummary(
            ref_key=item.candidate_key,
            object_type=item.object_ref.object_type,
            display_name=item.display_label,
            availability_status="STALE" if item.stale else "AVAILABLE",
            version_label=str(item.object_ref.version_id),
            summary={"semantic_summary": item.semantic_summary, "source": item.source.value},
        ) for item in candidates.active_object_candidates]
        result_summaries = [CompactResultSummary(
            ref_key=item.candidate_key,
            result_id=item.result_id,
            research_question=item.display_label,
            execution_status="HISTORICAL",
            relevance_status="STALE" if item.stale else "CURRENT",
            summary=item.semantic_summary or "Persisted scientific result snapshot",
        ) for item in candidates.result_candidates]
        fingerprint_payload = {
            "project_id": candidates.project_id,
            "turn_id": str(candidates.research_turn_id),
            "objects": [
                [item.candidate_key, str(item.object_ref.object_id), str(item.object_ref.version_id)]
                for item in candidates.active_object_candidates
            ],
            "results": [
                [item.candidate_key, str(item.result_id), "STALE" if item.stale else "CURRENT"]
                for item in candidates.result_candidates
            ],
            "constraints": candidates.explicit_constraints,
            "recent_turn_ids": [str(item) for item in candidates.recent_turn_ids],
            "compiler_version": COMPILER_VERSION,
        }
        fingerprint = context_fingerprint(fingerprint_payload)
        messages = list(candidates.recent_messages)
        unresolved = list(candidates.unresolved_questions)
        objects = object_summaries
        results = result_summaries
        max_bytes = token_budget * 4

        while True:
            compact = CompactResearchContext(
                project_summary="Authorized material-research project context",
                current_goal=candidates.current_research_goal,
                objects=objects,
                results=results,
                explicit_constraints=candidates.explicit_constraints,
                unresolved_questions=unresolved,
                recent_conversation=messages,
                context_fingerprint=fingerprint,
            )
            if len(compact.model_dump_json().encode("utf-8")) <= max_bytes:
                return compact
            if messages:
                messages = messages[1:]
            elif unresolved:
                unresolved = unresolved[1:]
            elif len(objects) > 1:
                objects = objects[:-1]
            elif len(results) > 1:
                results = results[:-1]
            else:
                raise ValueError("Research context cannot fit within token_budget")
