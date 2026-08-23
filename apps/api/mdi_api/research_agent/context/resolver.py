from __future__ import annotations

from dataclasses import dataclass

from mdi_api.research_agent.context.schemas import ReferenceCandidateSource, ResearchContextCandidateBundle


_SOURCE_PRIORITY = {
    ReferenceCandidateSource.EXPLICIT_REFERENCE: 0,
    ReferenceCandidateSource.UI_SELECTION: 1,
    ReferenceCandidateSource.CURRENT_SCOPE: 2,
    ReferenceCandidateSource.PREVIOUS_TURN_RESULT: 3,
    ReferenceCandidateSource.PREVIOUS_TURN: 3,
    ReferenceCandidateSource.PINNED_CONTEXT: 4,
    ReferenceCandidateSource.RECENT_CONTEXT: 5,
    ReferenceCandidateSource.LONG_SESSION_RETRIEVAL: 6,
}


def candidate_source_priority(source: ReferenceCandidateSource) -> int:
    return _SOURCE_PRIORITY[source]


@dataclass(frozen=True)
class ReferenceResolution:
    selected_object_keys: tuple[str, ...]
    ambiguous_object_keys: tuple[str, ...]
    selected_result_keys: tuple[str, ...] = ()
    ambiguous_result_keys: tuple[str, ...] = ()

    @property
    def requires_clarification(self) -> bool:
        return bool(self.ambiguous_object_keys or self.ambiguous_result_keys)


class DeterministicReferenceResolver:
    def resolve(self, bundle: ResearchContextCandidateBundle) -> ReferenceResolution:
        objects = bundle.active_object_candidates
        results = bundle.result_candidates
        if not objects and not results:
            return ReferenceResolution((), ())

        object_priority = min(
            (candidate_source_priority(item.source) for item in objects),
            default=None,
        )
        result_priority = min(
            (candidate_source_priority(item.source) for item in results),
            default=None,
        )
        if result_priority is not None and (
            object_priority is None or result_priority < object_priority
        ):
            best_results = [
                item
                for item in results
                if candidate_source_priority(item.source) == result_priority
            ]
            if len(best_results) == 1:
                return ReferenceResolution(
                    (), (), (best_results[0].candidate_key,), ()
                )
            return ReferenceResolution(
                (), (), (), tuple(item.candidate_key for item in best_results)
            )

        assert object_priority is not None
        best = [
            item
            for item in objects
            if candidate_source_priority(item.source) == object_priority
        ]
        if len(best) == 1:
            return ReferenceResolution((best[0].candidate_key,), ())
        # Multiple exact UI selections are an explicit bounded scope, not a
        # natural-language guess between equally ranked candidates.
        if all(item.source == ReferenceCandidateSource.UI_SELECTION for item in best):
            return ReferenceResolution(tuple(item.candidate_key for item in best), ())
        return ReferenceResolution((), tuple(item.candidate_key for item in best))
