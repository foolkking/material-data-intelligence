from __future__ import annotations

from mdi_api.agent2_errors import InvalidResearchTurnTransition
from mdi_api.research_agent.schemas import ResearchTurnStatus


_FAILED = ResearchTurnStatus.FAILED
_CANCELED = ResearchTurnStatus.CANCELED

ALLOWED_TRANSITIONS: dict[ResearchTurnStatus, frozenset[ResearchTurnStatus]] = {
    ResearchTurnStatus.RECEIVED: frozenset({ResearchTurnStatus.RESOLVING_CONTEXT, _FAILED, _CANCELED}),
    ResearchTurnStatus.RESOLVING_CONTEXT: frozenset({ResearchTurnStatus.ORCHESTRATING, _FAILED, _CANCELED}),
    ResearchTurnStatus.ORCHESTRATING: frozenset({
        ResearchTurnStatus.NEEDS_CLARIFICATION,
        ResearchTurnStatus.ANSWERED,
        ResearchTurnStatus.UNSUPPORTED,
        ResearchTurnStatus.READY_TO_PLAN,
        ResearchTurnStatus.INTERPRETING,
        _FAILED,
        _CANCELED,
    }),
    ResearchTurnStatus.READY_TO_PLAN: frozenset({ResearchTurnStatus.PLANNING, _FAILED, _CANCELED}),
    ResearchTurnStatus.PLANNING: frozenset({ResearchTurnStatus.PLAN_READY, ResearchTurnStatus.PLAN_REJECTED, ResearchTurnStatus.UNSUPPORTED, _FAILED, _CANCELED}),
    ResearchTurnStatus.PLAN_READY: frozenset({ResearchTurnStatus.QUEUED, _FAILED, _CANCELED}),
    ResearchTurnStatus.QUEUED: frozenset({ResearchTurnStatus.RUNNING, ResearchTurnStatus.RESULT_PENDING, ResearchTurnStatus.CANCELING, _FAILED}),
    ResearchTurnStatus.RUNNING: frozenset({ResearchTurnStatus.RESULT_PENDING, ResearchTurnStatus.CANCELING, ResearchTurnStatus.INTERPRETING, _FAILED}),
    ResearchTurnStatus.CANCELING: frozenset({_CANCELED, ResearchTurnStatus.RESULT_PENDING, _FAILED}),
    ResearchTurnStatus.RESULT_PENDING: frozenset({ResearchTurnStatus.RESULT_READY, _FAILED}),
    ResearchTurnStatus.RESULT_READY: frozenset({ResearchTurnStatus.INTERPRETING, _FAILED}),
    ResearchTurnStatus.INTERPRETING: frozenset({ResearchTurnStatus.COMPLETED, ResearchTurnStatus.PARTIAL, _FAILED, _CANCELED}),
    # M2 narrow recovery: a failed Interpretation may reclaim only the
    # Interpretation boundary when an immutable ScientificResult already
    # exists.  The service enforces that predicate before this transition.
    ResearchTurnStatus.FAILED: frozenset({ResearchTurnStatus.INTERPRETING}),
}


def ensure_transition(current: ResearchTurnStatus, target: ResearchTurnStatus) -> None:
    if target not in ALLOWED_TRANSITIONS.get(current, frozenset()):
        raise InvalidResearchTurnTransition(f"{current.value} -> {target.value}")
