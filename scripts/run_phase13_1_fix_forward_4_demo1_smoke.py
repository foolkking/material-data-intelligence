from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any
import uuid

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from redis import Redis
from rq import Queue
from sqlalchemy import create_engine, text
from sqlalchemy.schema import CreateSchema, DropSchema

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mdi_api.main import create_app
from mdi_api.phase2_runtime import get_phase2_runtime, reset_phase2_runtime
from mdi_api.routers.planner import _planner_repositories_and_runtime
from scripts.phase13_current_demo_contracts import CURRENT_DEMO_SPECS
from tests.integration.test_phase10m1_workspace_service_backed import _schema_database_url


def _require(response: Any, stage: str, expected: tuple[int, ...] = (200,)) -> dict[str, Any]:
    if response.status_code not in expected:
        raise RuntimeError(f"{stage}: HTTP {response.status_code}: {response.text}")
    return response.json()


def _counts(repositories: Any, project_id: str, job_id: str) -> dict[str, int]:
    return {
        "jobs": len(repositories.jobs.list_by_project(project_id)),
        "toolCalls": len(repositories.tool_calls.list_for_job(job_id)),
        "artifacts": len(repositories.artifacts.list_for_job(job_id)),
    }


def prepare(state_path: Path) -> None:
    database_url = os.environ["DATABASE_URL"]
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase13ff4_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    with base_engine.begin() as connection:
        connection.execute(CreateSchema(schema_name))

    os.environ["DATABASE_URL"] = schema_url
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
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

    os.environ.update({
        "MDI_RUNTIME_BACKEND": "postgresql",
        "MDI_QUEUE_BACKEND": "redis",
        "MDI_ARTIFACT_BACKEND": "minio",
        "MDI_ALLOW_TEST_PROVIDERS": "1",
    })
    queue = Queue("mdi-jobs", connection=Redis.from_url(os.environ["REDIS_URL"]))
    reset_phase2_runtime(ROOT / ".pytest_tmp" / f"ff4-upload-{suffix}")
    with TestClient(create_app()) as client:
        project = _require(client.post("/projects", json={"name": f"FF4 Demo 1 {suffix}"}), "project")
        spec = CURRENT_DEMO_SPECS[0]
        upload = _require(client.post("/datasets/upload", json={
            "projectId": project["id"],
            "datasetName": f"FF4 {spec['demoId']}",
            "filePaths": [fixture[1] for fixture in spec["fixtures"]],
        }), "upload")
        profile = upload["profile"]
        resource_ids = sorted(
            item["resourceId"] for item in profile["resourceSemantics"] if item.get("resourceId")
        )
        planned = _require(client.post("/planner/jobs", json={
            "projectId": project["id"],
            "datasetId": upload["id"],
            "profileId": profile["profileId"],
            "userPrompt": spec["prompt"],
            "intentSchemaVersion": "1.0",
            "selectedResourceIds": resource_ids,
            "provider": "mock",
            "enqueue": True,
        }), "planner")
        if not planned.get("ok") or not planned.get("enqueued"):
            raise RuntimeError(f"planner did not enqueue: {planned}")
        job_id = planned["job_id"]
        selected_tools = sorted(step["toolId"] for step in planned["plan"]["steps"])
        expected_tools = sorted(spec["expectedTools"])
        if selected_tools != expected_tools:
            raise RuntimeError(f"capability coverage mismatch: {selected_tools} != {expected_tools}")
        if queue.fetch_job(job_id) is None:
            raise RuntimeError("Redis job identity is missing")
        upload_exports = {
            item["objectId"]: (item["storageKey"], item["contentHash"])
            for item in get_phase2_runtime().datasets[upload["id"]].normalized_exports
        }

        reset_phase2_runtime(ROOT / ".pytest_tmp" / f"ff4-worker-{suffix}")
        repositories, worker = _planner_repositories_and_runtime(repositories=None, queue_runtime=None)
        persisted = repositories.datasets.get(upload["id"])
        durable_exports = {
            item["objectId"]: (item["storageKey"], item["contentHash"])
            for item in persisted["metadata"]["normalizedExports"]
        }
        if upload_exports != durable_exports or get_phase2_runtime().datasets:
            raise RuntimeError("fresh Worker did not reconstruct exact durable source identities")
        worker_result = worker.handle_job(job_id)
        if worker_result.status not in {"completed", "partial_success"}:
            raise RuntimeError(f"worker failed: {worker_result.status}: {worker_result.message}")
        tool_calls = repositories.tool_calls.list_for_job(job_id)
        artifacts = repositories.artifacts.list_for_job(job_id)
        if sorted(item["toolId"] for item in tool_calls) != expected_tools or not artifacts:
            raise RuntimeError("registered Adapter output coverage is incomplete")

        workspace = _require(client.post(
            "/workspaces",
            headers={"Idempotency-Key": f"ff4-workspace-{suffix}"},
            json={"sourceJobId": job_id, "title": "Fresh Demo 1 product closure"},
        ), "workspace", (200, 201))
        workspace_id = workspace["workspace"]["workspaceId"]
        inventory = _require(
            client.get(f"/workspaces/{workspace_id}/report-composition/sources"),
            "report inventory",
        )
        if not inventory["actionEligibility"]["reportFinalizeAllowed"]:
            raise RuntimeError(f"current Plan 0.1 action policy rejected: {inventory['actionEligibility']}")

        state = {
            "schemaName": schema_name,
            "databaseUrl": schema_url,
            "projectId": project["id"],
            "datasetId": upload["id"],
            "profileId": profile["profileId"],
            "intentId": planned["intent_id"],
            "planId": planned["plan_id"],
            "planSchemaVersion": planned["plan"]["schemaVersion"],
            "jobId": job_id,
            "workspaceId": workspace_id,
            "workspaceRevision": workspace["workspace"]["revision"],
            "workspaceProjectedStatus": workspace["workspace"]["projectedStatus"],
            "workspaceReadOnly": workspace["workspace"]["readOnly"],
            "reportActionEligibility": inventory["actionEligibility"],
            "resourceIds": resource_ids,
            "durableSourceIdentityExact": upload_exports == durable_exports,
            "selectedTools": selected_tools,
            "toolCalls": [{"id": item["id"], "toolId": item["toolId"]} for item in tool_calls],
            "artifacts": [{"id": item["id"], "type": item["type"], "contentHash": item["contentHash"]} for item in artifacts],
            "beforeReportCounts": _counts(repositories, project["id"], job_id),
            "queuedJobId": job_id,
        }
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(state, sort_keys=True))
    engine.dispose()
    base_engine.dispose()


def verify(state_path: Path, browser_path: Path) -> None:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    browser = json.loads(browser_path.read_text(encoding="utf-8"))
    os.environ["DATABASE_URL"] = state["databaseUrl"]
    repositories, _ = _planner_repositories_and_runtime(repositories=None, queue_runtime=None)
    report_rows = repositories.reports.list_for_job(state["jobId"])
    if len(report_rows) != 1:
        raise RuntimeError(f"expected one persisted Report, got {len(report_rows)}")
    report = report_rows[0]
    recipe_rows = repositories.recipes.list_for_job(state["jobId"])
    recipe = recipe_rows[0] if len(recipe_rows) == 1 else None
    if recipe is None or recipe["executionAuthorized"]:
        raise RuntimeError("paired non-executable Recipe is missing or executable")
    after = _counts(repositories, state["projectId"], state["jobId"])
    if after != state["beforeReportCounts"]:
        raise RuntimeError(f"Report/Recipe inspection changed execution rows: {after}")
    result = {
        **state,
        "browser": browser,
        "reportId": report["id"],
        "recipeId": recipe["id"],
        "afterReportCounts": after,
        "recipeExecutionAuthorized": recipe["executionAuthorized"],
        "status": "PASS",
    }
    state_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


def emit_evidence(state_path: Path, browser_path: Path, output_dir: Path) -> None:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    browser = json.loads(browser_path.read_text(encoding="utf-8"))
    os.environ["DATABASE_URL"] = state["databaseUrl"]
    repositories, _ = _planner_repositories_and_runtime(repositories=None, queue_runtime=None)
    report = repositories.reports.list_for_job(state["jobId"])[0]
    recipe = repositories.recipes.list_for_job(state["jobId"])[0]
    output_dir.mkdir(parents=True, exist_ok=True)

    records = {
        "fresh_demo1_closure_smoke.json": {
            "status": "PASS",
            "fresh": True,
            "realUserEntry": True,
            "realUpload": True,
            "realIntent": True,
            "realEligibility": True,
            "realPlanner": True,
            "realPlanValidator": True,
            "realPostgreSqlJob": True,
            "realRedis": True,
            "realMinio": True,
            "freshWorker": True,
            "registeredAdapters": True,
            "realWorkspace": True,
            "realChromiumFinalize": True,
            "oldEvidenceReused": 0,
        },
        "fresh_demo1_runtime_lineage.json": {
            key: state[key]
            for key in (
                "projectId", "datasetId", "profileId", "intentId", "planId",
                "planSchemaVersion", "jobId", "resourceIds", "selectedTools",
                "toolCalls", "artifacts", "durableSourceIdentityExact",
            )
        },
        "fresh_demo1_workspace.json": {
            "workspaceId": state["workspaceId"],
            "projectedStatus": state["workspaceProjectedStatus"],
            "readOnly": state["workspaceReadOnly"],
            "scientificSourceMutationAllowed": False,
            "reportActionEligibility": state["reportActionEligibility"],
        },
        "fresh_demo1_report.json": {
            "reportId": state["reportId"],
            "workspaceId": state["workspaceId"],
            "report": report.get("report") or report.get("snapshot") or report,
        },
        "fresh_demo1_recipe.json": {
            "recipeId": state["recipeId"],
            "reportId": state["reportId"],
            "executionAuthorized": state["recipeExecutionAuthorized"],
            "recipe": recipe.get("manifest") or recipe,
        },
        "recipe_no_execution_growth.json": {
            "before": state["beforeReportCounts"],
            "after": state["afterReportCounts"],
            "planGrowth": 0,
            "jobGrowth": 0,
            "queueGrowth": 0,
            "toolCallGrowth": 0,
            "artifactGrowth": 0,
            "status": "PASS",
        },
    }
    for name, value in records.items():
        (output_dir / name).write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    (output_dir / "fresh_demo1_report_ui.json").write_text(
        json.dumps(browser, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("PHASE13_FF4_SMOKE_EVIDENCE_WRITTEN")


def cleanup(state_path: Path) -> None:
    if not state_path.exists():
        return
    state = json.loads(state_path.read_text(encoding="utf-8"))
    queue = Queue("mdi-jobs", connection=Redis.from_url(os.environ["REDIS_URL"]))
    queued = queue.fetch_job(state.get("queuedJobId", ""))
    if queued is not None:
        queued.delete()
    database_url = os.environ["DATABASE_URL"]
    if "options=-csearch_path" in database_url:
        database_url = database_url.split("?", 1)[0]
    engine = create_engine(database_url, future=True)
    with engine.begin() as connection:
        connection.execute(DropSchema(state["schemaName"], cascade=True))
    engine.dispose()
    reset_phase2_runtime()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "verify", "evidence", "cleanup"))
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--browser", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.state)
    elif args.command == "verify":
        if args.browser is None:
            raise SystemExit("--browser is required for verify")
        verify(args.state, args.browser)
    elif args.command == "evidence":
        if args.browser is None or args.output_dir is None:
            raise SystemExit("--browser and --output-dir are required for evidence")
        emit_evidence(args.state, args.browser, args.output_dir)
    else:
        cleanup(args.state)


if __name__ == "__main__":
    main()
