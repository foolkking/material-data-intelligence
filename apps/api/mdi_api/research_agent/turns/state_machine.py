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
        _FAILED,
        _CANCELED,
    }),
    ResearchTurnStatus.READY_TO_PLAN: frozenset({ResearchTurnStatus.PLANNING, _FAILED, _CANCELED}),
    ResearchTurnStatus.PLANNING: frozenset({ResearchTurnStatus.PLAN_REJECTED, ResearchTurnStatus.QUEUED, _FAILED, _CANCELED}),
    ResearchTurnStatus.QUEUED: frozenset({ResearchTurnStatus.RUNNING, _CANCELED}),
    ResearchTurnStatus.RUNNING: frozenset({ResearchTurnStatus.INTERPRETING, _FAILED, _CANCELED}),
    ResearchTurnStatus.INTERPRETING: frozenset({ResearchTurnStatus.COMPLETED, ResearchTurnStatus.PARTIAL, _FAILED, _CANCELED}),
}


def ensure_transition(current: ResearchTurnStatus, target: ResearchTurnStatus) -> None:
    if target not in ALLOWED_TRANSITIONS.get(current, frozenset()):
        raise InvalidResearchTurnTransition(f"{current.value} -> {target.value}")
