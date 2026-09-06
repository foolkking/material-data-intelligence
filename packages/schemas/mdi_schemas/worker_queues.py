from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Mapping


WORKER_QUEUE_MANIFEST_VERSION = "WorkerQueueManifest/1.0"


@dataclass(frozen=True)
class WorkerQueueDefinition:
    role: str
    default_name: str
    environment_variable: str
    settings_attribute: str
    handler: str


WORKER_QUEUE_MANIFEST: tuple[WorkerQueueDefinition, ...] = (
    WorkerQueueDefinition(
        role="orchestration",
        default_name="mdi-agent-turns",
        environment_variable="MDI_AGENT2_QUEUE_NAME",
        settings_attribute="agent2_queue_name",
        handler="mdi_api.research_agent_worker.run_queued_turn",
    ),
    WorkerQueueDefinition(
        role="planning",
        default_name="mdi-agent-plans",
        environment_variable="MDI_AGENT2_PLANNING_QUEUE_NAME",
        settings_attribute="agent2_planning_queue_name",
        handler="mdi_api.research_agent_planning_worker.run_queued_planning",
    ),
    WorkerQueueDefinition(
        role="execution",
        default_name="mdi-jobs",
        environment_variable="MDI_AGENT2_EXECUTION_QUEUE_NAME",
        settings_attribute="agent2_execution_queue_name",
        handler="mdi_workers.queue_runtime.run_queued_job",
    ),
    WorkerQueueDefinition(
        role="result_projection",
        default_name="mdi-agent-results",
        environment_variable="MDI_AGENT2_RESULT_QUEUE_NAME",
        settings_attribute="agent2_result_queue_name",
        handler="mdi_api.scientific_results.worker.run_queued_result_projection",
    ),
    WorkerQueueDefinition(
        role="interpretation",
        default_name="mdi-agent-interpretations",
        environment_variable="MDI_AGENT2_INTERPRETATION_QUEUE_NAME",
        settings_attribute="agent2_interpretation_queue_name",
        handler="mdi_workers.interpretation_worker.run_queued_interpretation",
    ),
    WorkerQueueDefinition(
        role="report",
        default_name="mdi-agent-reports",
        environment_variable="MDI_AGENT2_REPORT_QUEUE_NAME",
        settings_attribute="agent2_report_queue_name",
        handler="mdi_workers.report_worker.run_queued_report_generation",
    ),
)


def worker_queue_definition(role: str) -> WorkerQueueDefinition:
    for definition in WORKER_QUEUE_MANIFEST:
        if definition.role == role:
            return definition
    raise KeyError(f"Unknown worker queue role: {role}")


def configured_worker_queue_names(
    settings: object | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> tuple[str, ...]:
    """Resolve the canonical queue topology for API, workers, and launchers."""

    source = os.environ if environ is None else environ
    names: list[str] = []
    for definition in WORKER_QUEUE_MANIFEST:
        if settings is not None:
            value = getattr(
                settings,
                definition.settings_attribute,
                definition.default_name,
            )
        else:
            value = source.get(definition.environment_variable, definition.default_name)
        names.append(str(value).strip())
    return tuple(names)


def worker_queue_manifest_payload(
    settings: object | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> dict[str, object]:
    names = configured_worker_queue_names(settings, environ=environ)
    return {
        "schemaVersion": WORKER_QUEUE_MANIFEST_VERSION,
        "queues": [
            {
                "role": definition.role,
                "name": name,
                "environmentVariable": definition.environment_variable,
                "settingsAttribute": definition.settings_attribute,
                "handler": definition.handler,
            }
            for definition, name in zip(WORKER_QUEUE_MANIFEST, names, strict=True)
        ],
    }


def main() -> int:
    print(json.dumps(worker_queue_manifest_payload(), separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
