from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any
import uuid

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from redis import Redis
from rq import Queue
from sqlalchemy import create_engine, text
from sqlalchemy.schema import CreateSchema, DropSchema

from mdi_api.main import create_app
from mdi_api.phase2_runtime import get_phase2_runtime, reset_phase2_runtime
from mdi_api.routers.planner import _planner_repositories_and_runtime
from tests.integration.test_phase10m1_workspace_service_backed import (
    _minio_client,
    _required_postgres_url,
    _schema_database_url,
)
from scripts.generate_phase13_1_product_entry_fix_forward import DEMO_SPECS


def _require(response: Any, stage: str, expected: tuple[int, ...] = (200,)) -> dict[str, Any]:
    if response.status_code not in expected:
        raise RuntimeError(
            f"{stage} failed: HTTP {response.status_code}: "
            f"{json.dumps(response.json(), indent=2, sort_keys=True)}"
        )
    return response.json()


def run_demo_1() -> dict[str, Any]:
    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase13a4_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    queue = Queue("mdi-jobs", connection=Redis.from_url(os.environ["REDIS_URL"]))
    queued_job_id: str | None = None
    engine = None
    try:
        with base_engine.begin() as connection:
            connection.execute(CreateSchema(schema_name))
        config = AlembicConfig("apps/api/alembic.ini")
        config.set_main_option("script_location", "apps/api/alembic")
        os.environ["DATABASE_URL"] = schema_url
        alembic_upgrade(config, "head")
        engine = create_engine(schema_url, future=True)
        with engine.begin() as connection:
            connection.execute(text(
                "CREATE TABLE IF NOT EXISTS organizations (id VARCHAR(64) PRIMARY KEY, "
                "name VARCHAR(160) NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT "
                "CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            ))
            connection.execute(text(
                "CREATE TABLE IF NOT EXISTS users (id VARCHAR(64) PRIMARY KEY, "
                "email VARCHAR(320) NOT NULL UNIQUE, display_name VARCHAR(160) NOT NULL, "
                "is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP NOT NULL "
                "DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            ))

        os.environ["MDI_RUNTIME_BACKEND"] = "postgresql"
        os.environ["MDI_QUEUE_BACKEND"] = "redis"
        os.environ["MDI_ARTIFACT_BACKEND"] = "minio"
        os.environ["MDI_ALLOW_TEST_PROVIDERS"] = "1"
        minio, bucket = _minio_client()
        minio.head_bucket(Bucket=bucket)
        assert queue.connection.ping() is True

        reset_phase2_runtime(ROOT / ".pytest_tmp" / f"attempt4-upload-{suffix}")
        with TestClient(create_app()) as client:
            project = _require(
                client.post("/projects", json={"name": f"Attempt 4 Demo 1 {suffix}"}),
                "project creation",
            )
            spec = DEMO_SPECS[0]
            upload = _require(
                client.post(
                    "/datasets/upload",
                    json={
                        "projectId": project["id"],
                        "datasetName": f"Attempt 4 {spec['demoId']}",
                        "filePaths": [item[1] for item in spec["fixtures"]],
                    },
                ),
                "dataset upload",
            )
            profile = upload["profile"]
            selected_ids = sorted(
                item["resourceId"]
                for item in profile["resourceSemantics"]
                if item.get("resourceId")
            )
            planned = _require(
                client.post(
                    "/planner/jobs",
                    json={
                        "projectId": project["id"],
                        "datasetId": upload["id"],
                        "profileId": profile["profileId"],
                        "userPrompt": spec["prompt"],
                        "intentSchemaVersion": "1.0",
                        "selectedResourceIds": selected_ids,
                        "provider": "mock",
                        "enqueue": True,
                    },
                ),
                "planner job",
            )
            if not planned.get("ok") or not planned.get("enqueued"):
                raise RuntimeError(f"planner did not create an executable job: {planned}")
            queued_job_id = planned["job_id"]
            planned_tools = [
                step["toolId"] for step in (planned.get("plan") or {}).get("steps", [])
            ]
            if queue.fetch_job(queued_job_id) is None:
                raise RuntimeError("Redis queue does not contain the planned job")

            upload_exports = {
                item["objectId"]: (item["storageKey"], item["contentHash"])
                for item in get_phase2_runtime().datasets[upload["id"]].normalized_exports
            }
            reset_phase2_runtime(ROOT / ".pytest_tmp" / f"attempt4-fresh-{suffix}")
            repositories, worker = _planner_repositories_and_runtime(
                repositories=None,
                queue_runtime=None,
            )
            persisted = repositories.datasets.get(upload["id"])
            durable_exports = {
                item["objectId"]: (item["storageKey"], item["contentHash"])
                for item in persisted["metadata"]["normalizedExports"]
            }
            if upload_exports != durable_exports or get_phase2_runtime().datasets:
                raise RuntimeError("fresh worker source identity does not match durable upload identity")

            worker_result = worker.handle_job(queued_job_id)
            tool_calls = repositories.tool_calls.list_for_job(queued_job_id)
            artifacts = repositories.artifacts.list_for_job(queued_job_id)
            if worker_result.status not in {"completed", "partial_success"}:
                raise RuntimeError(f"worker failed: {worker_result.status}: {worker_result.message}")
            if not tool_calls or not artifacts:
                raise RuntimeError("worker produced no ToolCalls or Artifacts")

            workspace_response = client.post(
                "/workspaces",
                headers={"Idempotency-Key": f"attempt4-workspace-{suffix}"},
                json={"sourceJobId": queued_job_id, "title": "Attempt 4 Demo 1"},
            )
            workspace = _require(workspace_response, "workspace creation", (200, 201))
            workspace_id = workspace["workspace"]["workspaceId"]
            inventory = _require(
                client.get(f"/workspaces/{workspace_id}/report-composition/sources"),
                "report source inventory",
            )
            artifact_ids = [item["id"] for item in artifacts]
            report_request = {
                "schemaVersion": "1.0",
                "workspaceId": workspace_id,
                "expectedWorkspaceRevision": workspace["workspace"]["revision"],
                "title": "Attempt 4 Demo 1 Report",
                "selectedPanelIds": [],
                "selectedArtifactIds": artifact_ids,
                "selectedClaimIds": [],
                "selectedEvidenceItemIds": [],
                "itemOrder": artifact_ids,
                "captions": [],
                "exportFormats": ["json", "markdown"],
            }
            preview = _require(
                client.post(
                    f"/workspaces/{workspace_id}/report-compositions/preview",
                    json=report_request,
                ),
                "report preview",
            )
            finalized = _require(
                client.post(
                    f"/workspaces/{workspace_id}/report-compositions",
                    headers={"Idempotency-Key": f"attempt4-report-{suffix}"},
                    json=report_request,
                ),
                "report finalize",
                (200, 201),
            )
            recipe = _require(
                client.get(
                    f"/workspaces/{workspace_id}/report-compositions/"
                    f"{finalized['reportId']}/recipe"
                ),
                "recipe read",
            )
            return {
                "demoId": spec["demoId"],
                "status": "PASS",
                "projectId": project["id"],
                "datasetId": upload["id"],
                "profileId": profile["profileId"],
                "selectedResourceIds": selected_ids,
                "durableSourceIdentityExact": upload_exports == durable_exports,
                "jobId": queued_job_id,
                "workerStatus": worker_result.status,
                "plannedTools": planned_tools,
                "toolCallCount": len(tool_calls),
                "executedTools": [item["toolId"] for item in tool_calls],
                "artifactCount": len(artifacts),
                "artifactIds": artifact_ids,
                "artifactTypes": [item["type"] for item in artifacts],
                "workspaceId": workspace_id,
                "workspaceStatus": workspace["workspace"]["projectedStatus"],
                "workspaceReadOnly": workspace["workspace"]["readOnly"],
                "reportSourceCount": inventory["sourceCount"],
                "reportPreviewPersisted": preview["persisted"],
                "reportId": finalized["reportId"],
                "recipeId": finalized["recipeId"],
                "recipeExecutionAuthorized": recipe["recipe"]["executionAuthorized"],
            }
    finally:
        if queued_job_id:
            queued = queue.fetch_job(queued_job_id)
            if queued is not None:
                queued.delete()
        reset_phase2_runtime()
        if engine is not None:
            engine.dispose()
        try:
            with base_engine.begin() as connection:
                connection.execute(DropSchema(schema_name, cascade=True))
        finally:
            base_engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", choices=("1",), default="1")
    args = parser.parse_args()
    if args.demo == "1":
        print(json.dumps(run_demo_1(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
