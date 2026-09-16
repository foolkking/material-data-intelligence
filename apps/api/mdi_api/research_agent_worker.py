"""RQ-compatible top-level Agent2 orchestration entrypoint.

RQ resolves dotted callables by walking package attributes. Keeping this
identity-only shim directly under ``mdi_api`` avoids relying on nested package
attribute discovery in fresh workers while preserving the existing processor.
"""

from __future__ import annotations

import logging
from uuid import UUID


logger = logging.getLogger(__name__)


def _persist_worker_boundary_failure(turn_id: str, error: BaseException) -> None:
    """Persist a terminal Research failure before allowing RQ to fail the job."""

    try:
        from mdi_api.bootstrap.repository_factory import create_repository_factory
        from mdi_api.research_agent.service import ResearchTurnService

        ResearchTurnService(create_repository_factory()).fail_if_active(
            UUID(str(turn_id)),
            "WORKER_BOUNDARY_FAILURE",
            f"{type(error).__name__}: {error}",
        )
    except Exception:
        # Preserve the original worker exception/RQ failure.  A persistence
        # failure must be visible in worker logs rather than masking the
        # original boundary error.
        logger.exception(
            "research_turn_worker_failure_persistence_failed",
            extra={"turn_id": str(turn_id)},
        )


def run_queued_turn(turn_id: str):
    """Resolve and execute one turn with durable boundary-failure handling.

    RQ imports this shim in a fresh worker process.  Keep the orchestration
    import lazy, but make both import-time and unexpected handler failures
    terminalize the durable Turn before re-raising so RQ retains its normal
    failure semantics without orphaning the product lifecycle.
    """

    try:
        from mdi_api.research_agent.orchestration.worker import run_queued_turn as handler

        return handler(turn_id)
    except BaseException as error:
        _persist_worker_boundary_failure(turn_id, error)
        raise

__all__ = ["run_queued_turn"]
