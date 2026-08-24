"""RQ-compatible top-level Agent2 orchestration entrypoint.

RQ resolves dotted callables by walking package attributes. Keeping this
identity-only shim directly under ``mdi_api`` avoids relying on nested package
attribute discovery in fresh workers while preserving the existing processor.
"""

from __future__ import annotations

def run_queued_turn(turn_id: str):
    """Resolve the orchestration implementation only when a job executes."""
    from mdi_api.research_agent.orchestration.worker import run_queued_turn as handler

    return handler(turn_id)

__all__ = ["run_queued_turn"]
