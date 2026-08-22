from __future__ import annotations

from dataclasses import dataclass

from mdi_api.research_agent.context.schemas import ReferenceCandidate, ReferenceCandidateSource, ResearchContextCandidateBundle


_SOURCE_PRIORITY = {
    ReferenceCandidateSource.EXPLICIT_REFERENCE: 0,
    ReferenceCandidateSource.UI_SELECTION: 1,
    ReferenceCandidateSource.CURRENT_SCOPE: 2,
    ReferenceCandidateSource.PREVIOUS_TURN_RESULT: 3,
    ReferenceCandidateSource.PINNED_CONTEXT: 4,
    ReferenceCandidateSource.RECENT_CONTEXT: 5,
}


def candidate_source_priority(source: ReferenceCandidateSource) -> int:
    return _SOURCE_PRIORITY[source]


@dataclass(frozen=True)
class ReferenceResolution:
    selected_object_keys: tuple[str, ...]
    ambiguous_object_keys: tuple[str, ...]

    @property
    def requires_clarification(self) -> bool:
        return bool(self.ambiguous_object_keys)


class DeterministicReferenceResolver:
    def resolve(self, bundle: ResearchContextCandidateBundle) -> ReferenceResolution:
        objects = bundle.active_object_candidates
        if not objects:
            return ReferenceResolution((), ())
        best_priority = min(candidate_source_priority(item.source) for item in objects)
        best = [item for item in objects if candidate_source_priority(item.source) == best_priority]
        if len(best) == 1:
            return ReferenceResolution((best[0].candidate_key,), ())
        # Multiple exact UI selections are an explicit bounded scope, not a
        # natural-language guess between equally ranked candidates.
        if all(item.source == ReferenceCandidateSource.UI_SELECTION for item in best):
            return ReferenceResolution(tuple(item.candidate_key for item in best), ())
        return ReferenceResolution((), tuple(item.candidate_key for item in best))
