"""Create the Phase 9 report acceptance fixture through the Phase 8 worker path."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import UUID, uuid4

from redis import Redis
from rq import Queue

from mdi_api.database import create_repository_factory
from mdi_api.scientific_reports.grounded import DeterministicScientificReportComposer
from mdi_api.scientific_reports.queue import RedisRQReportQueue
from mdi_api.scientific_reports.requests import ScientificReportRequestService
from mdi_api.scientific_results.schemas import ScientificResultBundle


ROOT = Path(__file__).resolve().parents[1]
TURN_ID = "9d000082-4a7d-45c1-a929-18d8d9d4988d"
REQUESTED_BY = "user_product_acceptance"


def main() -> None:
    redis_url = os.environ.get("MDI_REDIS_URL", "redis://127.0.0.1:56380/0")
    queue_name = f"mdi-agent2-phase9-reports-{uuid4().hex[:10]}"
    factory = create_repository_factory()
    with factory.session() as session:
        turn_uuid = UUID(TURN_ID)
        turn = session.agent2.research_turns.get(turn_uuid)
        interpretation = session.agent2.interpretations.get_for_turn(turn_uuid)
        result = session.agent2.scientific_result_snapshots.get_latest_for_turn(turn_uuid)
    if not turn or not interpretation or not result:
        raise RuntimeError("canonical RDF turn must have a persisted result and interpretation")
    report = DeterministicScientificReportComposer().compose(
        bundle=ScientificResultBundle.model_validate(result["bundle_json"]),
        interpretation=interpretation["output_json"],
        relevance_status=str(result["relevance_status"]),
    ).model_dump(mode="json")
    for figure in report["primary_figures"]:
        figure["caption"] = "Validated RDF scientific figure"
    previous = {"MDI_ENV": os.environ.get("MDI_ENV"), "MDI_AGENT2_REPORT_FIXTURE_JSON": os.environ.get("MDI_AGENT2_REPORT_FIXTURE_JSON"), "MDI_QUEUE_BACKEND": os.environ.get("MDI_QUEUE_BACKEND"), "MDI_AGENT2_REPORT_QUEUE_NAME": os.environ.get("MDI_AGENT2_REPORT_QUEUE_NAME")}
    try:
        os.environ.update({"MDI_ENV": "ci", "MDI_QUEUE_BACKEND": "redis", "MDI_REDIS_URL": redis_url, "MDI_AGENT2_REPORT_QUEUE_NAME": queue_name, "MDI_AGENT2_REPORT_FIXTURE_JSON": json.dumps(report, ensure_ascii=False)})
        request = ScientificReportRequestService(
            factory,
            queue=RedisRQReportQueue(redis_url=redis_url, queue_name=queue_name),
        ).request(turn_uuid, requested_by=REQUESTED_BY)
        worker_env = os.environ.copy()
        worker_env["PYTHONPATH"] = os.pathsep.join(
            str(ROOT / item)
            for item in ("apps/api", "packages/schemas", "services/workers", "services/llm", "packages/adapters", "packages/tool-registry", "packages/artifact-core", "packages/material-parsers")
        )
        worker = subprocess.run(
            [sys.executable, "-m", "mdi_workers.worker_entrypoint", queue_name, "--url", redis_url, "--burst", "--max-jobs", "1", "--name", "phase9-report-fixture"],
            cwd=ROOT,
            env=worker_env,
            capture_output=True,
            text=True,
            timeout=240,
        )
        if worker.returncode:
            raise RuntimeError(worker.stderr[-6000:])
        job = Queue(queue_name, connection=Redis.from_url(redis_url)).fetch_job(f"mdi-agent2-report-{request['generation_id']}")
        if job is None or not job.is_finished:
            raise RuntimeError(f"report worker did not finish: {request}")
        print(json.dumps({"request": request, "worker": job.return_value(), "turn_id": TURN_ID, "result_id": str(result["id"])}, ensure_ascii=False, default=str))
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    main()
