"""Agent 2.0 capability planning and binding boundary."""

# RQ resolves dotted callables by first importing the package portion and then
# walking its attributes.  Expose the worker module explicitly so the durable
# ``mdi_api.research_agent.planning.worker.run_queued_planning`` entry point
# remains importable in a fresh worker process.
from . import worker

__all__ = ["worker"]
