from __future__ import annotations

import importlib


def test_rq_planning_entrypoint_is_resolvable_in_fresh_worker_import() -> None:
    package = importlib.import_module("mdi_api.research_agent.planning")
    worker = importlib.import_module("mdi_api.research_agent.planning.worker")

    assert getattr(package, "worker") is worker
    assert callable(worker.run_queued_planning)
