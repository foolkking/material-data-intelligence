from __future__ import annotations

import importlib


def test_planning_queue_uses_top_level_rq_entrypoint() -> None:
    module = importlib.import_module("mdi_api.research_agent_planning_worker")
    assert callable(module.run_queued_planning)
