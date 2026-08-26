"""RQ-compatible top-level planning entrypoint.

RQ workers resolve dotted callables more reliably when the callable lives in a
top-level module.  Keep the import of the planning implementation lazy so the
queue boundary remains lightweight in fresh worker processes.
"""

from __future__ import annotations


def run_queued_planning(turn_id: str):
    from mdi_api.research_agent.planning.worker import run_queued_planning as handler

    return handler(turn_id)


__all__ = ["run_queued_planning"]
