"""RQ-compatible top-level planning entrypoint.

RQ workers resolve dotted callables more reliably when the callable lives in a
top-level module.  Keep the import of the planning implementation lazy so the
queue boundary remains lightweight in fresh worker processes.
"""

from __future__ import annotations

import logging
from uuid import UUID


logger = logging.getLogger(__name__)


def _persist_worker_boundary_failure(turn_id: str, error: BaseException) -> None:
    try:
        from mdi_api.bootstrap.repository_factory import create_repository_factory
        from mdi_api.research_agent.service import ResearchTurnService

        ResearchTurnService(create_repository_factory()).fail_if_active(
            UUID(str(turn_id)),
            "PLANNING_WORKER_BOUNDARY_FAILURE",
            f"{type(error).__name__}: {error}",
        )
    except Exception:
        logger.exception(
            "research_planning_worker_failure_persistence_failed",
            extra={"turn_id": str(turn_id)},
        )


def run_queued_planning(turn_id: str):
    try:
        from mdi_api.research_agent.planning.worker import run_queued_planning as handler

        return handler(turn_id)
    except BaseException as error:
        _persist_worker_boundary_failure(turn_id, error)
        raise


__all__ = ["run_queued_planning"]
