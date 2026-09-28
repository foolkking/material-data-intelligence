from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from mdi_api.config import ApiSettings
from mdi_api.interpretation.queue import RedisRQInterpretationQueue
from mdi_api.research_agent.orchestration.queue import RedisRQAgentTurnQueue
from mdi_api.research_agent.planning.queue import RedisRQCapabilityPlanningQueue
from mdi_api.scientific_reports.queue import RedisRQReportQueue
from mdi_api.scientific_results.queue import RedisRQResultProjectionQueue
from mdi_workers.queue_runtime import RedisRQQueueBackend
from mdi_schemas.worker_queues import (
    WORKER_QUEUE_MANIFEST,
    WORKER_QUEUE_MANIFEST_VERSION,
    configured_worker_queue_names,
    worker_queue_manifest_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_worker_queue_manifest_is_complete_unique_and_settings_backed() -> None:
    payload = worker_queue_manifest_payload(ApiSettings())

    assert payload["schemaVersion"] == WORKER_QUEUE_MANIFEST_VERSION
    assert [item["role"] for item in payload["queues"]] == [
        "orchestration",
        "planning",
        "execution",
        "result_projection",
        "interpretation",
        "report",
    ]
    assert len({item["name"] for item in payload["queues"]}) == len(
        WORKER_QUEUE_MANIFEST
    )
    assert all(item["handler"] for item in payload["queues"])


def test_worker_queue_manifest_resolves_environment_overrides() -> None:
    environment = {
        definition.environment_variable: f"custom-{definition.role}"
        for definition in WORKER_QUEUE_MANIFEST
    }

    assert configured_worker_queue_names(environ=environment) == tuple(
        f"custom-{definition.role}"
        for definition in WORKER_QUEUE_MANIFEST
    )


def test_all_queue_producers_default_to_the_manifest_names() -> None:
    redis_url = "redis://example.invalid/0"
    producers = (
        RedisRQAgentTurnQueue(redis_url=redis_url),
        RedisRQCapabilityPlanningQueue(redis_url=redis_url),
        RedisRQQueueBackend(redis_url=redis_url),
        RedisRQResultProjectionQueue(redis_url=redis_url),
        RedisRQInterpretationQueue(redis_url=redis_url),
        RedisRQReportQueue(redis_url=redis_url),
    )

    assert tuple(producer.queue_name for producer in producers) == tuple(
        definition.default_name for definition in WORKER_QUEUE_MANIFEST
    )


def test_worker_queue_manifest_cli_is_launcher_readable() -> None:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT / "packages" / "schemas")
    completed = subprocess.run(
        [sys.executable, "-m", "mdi_schemas.worker_queues"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["schemaVersion"] == WORKER_QUEUE_MANIFEST_VERSION


def test_dev_controller_runs_one_worker_for_all_current_queues() -> None:
    launcher = (ROOT / "scripts" / "dev.ps1").read_text(encoding="utf-8")

    assert 'Start-OwnedProcess "worker"' in launcher
    assert '"mdi-dev-multiqueue"' in launcher
    for definition in WORKER_QUEUE_MANIFEST:
        assert f'"{definition.default_name}"' in launcher
    assert launcher.count('Start-OwnedProcess "worker"') == 1
