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
from mdi_artifact_core.phonon_contract import (
    PHONON_BAND_SCHEMA_VERSION,
    PHONON_DOS_SCHEMA_VERSION,
)
from scripts.phase13_current_demo_contracts import CURRENT_DEMO_SPECS
from scripts.run_phase13_2_attempt5 import (
    _artifact_record,
    _durable_exports,
    _normalized_exports,
    _require,
)
from tests.integration.test_phase10m1_workspace_service_backed import (
    _required_postgres_url,
    _schema_database_url,
)


def _upload_files(index: int, spec: dict[str, Any]) -> dict[str, Any]:
    if index != 5:
        return {"filePaths": [fixture[1] for fixture in spec["fixtures"]]}
    files = []
    declarations = {
        "typed_phonon_band_import": ("phonon_band", PHONON_BAND_SCHEMA_VERSION),
        "typed_phonon_dos_import": ("phonon_dos", PHONON_DOS_SCHEMA_VERSION),
    }
    for _, relative, mode in spec["fixtures"]:
        path = ROOT / relative
        item: dict[str, Any] = {
            "fileName": path.name,
            "content": path.read_text(encoding="utf-8"),
        }
        if mode in declarations:
            item["importKind"], item["contractVersion"] = declarations[mode]
        files.append(item)
    return {"files": files}


def run_demo(index: int, state_path: Path) -> dict[str, Any]:
    spec = CURRENT_DEMO_SPECS[index - 1]
    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase13a6d{index}_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    queue = Queue("mdi-jobs", connection=Redis.from_url(os.environ["REDIS_URL"]))
    with base_engine.begin() as connection:
        connection.execute(CreateSchema(schema_name))
    try:
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
        reset_phase2_runtime(ROOT / ".pytest_tmp" / f"attempt6-d{index}-upload-{suffix}")
        with TestClient(create_app()) as client:
            project = _require(
                client.post("/projects", json={"name": f"Attempt 6 Demo {index} {suffix}"}),
                "project creation",
            )
            upload = _require(
                client.post("/datasets/upload", json={
                    "projectId": project["id"],
                    "datasetName": f"Attempt 6 {spec['demoId']}",
                    **_upload_files(index, spec),
                }),
                "real typed dataset upload" if index == 5 else "real dataset upload",
            )
            profile = upload["profile"]
            resource_ids = sorted(
                str(item.get("resourceId") or item.get("objectId"))
                for item in profile["resourceSemantics"]
                if item.get("resourceId") or item.get("objectId")
            )
            kinds = sorted(item["objectType"] for item in profile["resourceSemantics"])
            if index == 5 and not {"PhononBand", "PhononDos", "Structure"}.issubset(kinds):
                raise RuntimeError(f"typed phonon Profile projection is incomplete: {kinds}")
            upload_exports = _normalized_exports(get_phase2_runtime().datasets[upload["id"]])
            planned = _require(
                client.post("/planner/jobs", json={
                    "projectId": project["id"],
                    "datasetId": upload["id"],
                    "profileId": profile["profileId"],
                    "userPrompt": spec["prompt"],
                    "intentSchemaVersion": "1.0",
                    "selectedResourceIds": resource_ids,
                    "provider": "mock",
                    "enqueue": True,
                }),
                "natural-language planner job",
            )
            if not planned.get("ok") or not planned.get("enqueued"):
                raise RuntimeError(f"planner did not enqueue: {planned}")
            selected_tools = sorted(step["toolId"] for step in planned["plan"]["steps"])
            expected_tools = sorted(spec["expectedTools"])
            if selected_tools != expected_tools:
                raise RuntimeError(f"capability mismatch: {selected_tools} != {expected_tools}")
            job_id = planned["job_id"]
            if queue.fetch_job(job_id) is None:
                raise RuntimeError("Redis does not contain the persisted Job identity")

            reset_phase2_runtime(ROOT / ".pytest_tmp" / f"attempt6-d{index}-worker-{suffix}")
            repositories, worker = _planner_repositories_and_runtime(
                repositories=None,
                queue_runtime=None,
            )
            persisted_dataset = repositories.datasets.get(upload["id"])
            durable_exports = _durable_exports(persisted_dataset)
            if upload_exports != durable_exports or get_phase2_runtime().datasets:
                raise RuntimeError("fresh Worker durable source reconstruction is not exact")
            worker_result = worker.handle_job(job_id)
            if worker_result.status not in {"completed", "partial_success"}:
                raise RuntimeError(f"Worker failed: {worker_result.status}: {worker_result.message}")
            tool_calls = repositories.tool_calls.list_for_job(job_id)
            artifacts = repositories.artifacts.list_for_job(job_id)
            if sorted(item["toolId"] for item in tool_calls) != expected_tools or not artifacts:
                raise RuntimeError("registered Adapter execution coverage is incomplete")
            if index == 5 and any("Unknown input ref" in str(item) for item in tool_calls):
                raise RuntimeError("typed phonon Runtime resolution produced Unknown input ref")

            workspace = _require(
                client.post(
                    "/workspaces",
                    headers={"Idempotency-Key": f"attempt6-d{index}-workspace-{suffix}"},
                    json={"sourceJobId": job_id, "title": f"Attempt 6 Demo {index}"},
                ),
                "workspace creation",
                (200, 201),
            )["workspace"]
            inventory = _require(
                client.get(f"/workspaces/{workspace['workspaceId']}/report-composition/sources"),
                "report source inventory",
            )
            action = inventory["actionEligibility"]
            required_actions = (
                "reportCompositionAllowed", "reportPreviewAllowed",
                "reportFinalizeAllowed", "recipeInspectionAllowed",
            )
            if not all(action[key] for key in required_actions):
                raise RuntimeError(f"report action eligibility rejected: {action}")

            result = {
                "status": "PREPARED_FOR_REAL_UI_FINALIZE",
                "fresh": True,
                "demoId": spec["demoId"],
                "family": spec["family"],
                "fixtureIds": [fixture[0] for fixture in spec["fixtures"]],
                "fixturePaths": [fixture[1] for fixture in spec["fixtures"]],
                "fixtureEntryModes": [fixture[2] for fixture in spec["fixtures"]],
                "userPrompt": spec["prompt"],
                "schemaName": schema_name,
                "databaseUrl": schema_url,
                "projectId": project["id"],
                "datasetId": upload["id"],
                "profileId": profile["profileId"],
                "profileResourceKinds": kinds,
                "intentId": planned["intent_id"],
                "intent": planned.get("intent"),
                "eligibility": planned.get("eligibility_resolution"),
                "planId": planned["plan_id"],
                "plan": planned["plan"],
                "planValidation": {"ok": planned["ok"], "errors": planned.get("errors", [])},
                "jobId": job_id,
                "redisEnqueued": True,
                "workerStatus": worker_result.status,
                "uploadExports": upload_exports,
                "durableExports": durable_exports,
                "durableSourceIdentityExact": upload_exports == durable_exports,
                "resourceIds": resource_ids,
                "expectedTools": expected_tools,
                "selectedTools": selected_tools,
                "toolCalls": tool_calls,
                "artifacts": [_artifact_record(item) for item in artifacts],
                "workspace": workspace,
                "workspaceId": workspace["workspaceId"],
                "reportActionEligibility": action,
                "reportSourceCount": inventory["sourceCount"],
                "beforeReportCounts": {
                    "jobs": len(repositories.jobs.list_by_project(project["id"])),
                    "toolCalls": len(tool_calls),
                    "artifacts": len(artifacts),
                },
                "oldEvidenceReusedAsPass": 0,
                "handcraftedInjections": 0,
                "manualPhononResourceInjection": 0,
                "manualPhononProfileInjection": 0,
            }
            state_path.parent.mkdir(parents=True, exist_ok=True)
            state_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(json.dumps({"demoId": spec["demoId"], "status": result["status"], "workspaceId": result["workspaceId"], "tools": selected_tools}, sort_keys=True))
            return result
    except Exception as error:
        state_path.with_suffix(".failure.json").write_text(json.dumps({
            "demoId": spec["demoId"], "schemaName": schema_name,
            "databaseUrl": schema_url, "status": "FAIL_PRODUCT_INTEGRATION",
            "error": str(error),
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        raise
    finally:
        reset_phase2_runtime()
        if engine is not None:
            engine.dispose()
        base_engine.dispose()


def verify_ui_finalize(state_path: Path, browser_path: Path) -> None:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    browser = json.loads(browser_path.read_text(encoding="utf-8"))
    if browser.get("status") != "PASS" or browser.get("workspaceId") != state["workspaceId"]:
        raise RuntimeError("Chromium evidence does not match the exact Workspace")
    os.environ["DATABASE_URL"] = state["databaseUrl"]
    repositories, _ = _planner_repositories_and_runtime(
        repositories=None,
        queue_runtime=None,
    )
    reports = repositories.reports.list_for_job(state["jobId"])
    recipes = repositories.recipes.list_for_job(state["jobId"])
    if len(reports) != 1 or len(recipes) != 1 or recipes[0].get("executionAuthorized"):
        raise RuntimeError("expected one inert persisted Report/Recipe pair")
    after = {
        "jobs": len(repositories.jobs.list_by_project(state["projectId"])),
        "toolCalls": len(repositories.tool_calls.list_for_job(state["jobId"])),
        "artifacts": len(repositories.artifacts.list_for_job(state["jobId"])),
    }
    if after != state["beforeReportCounts"]:
        raise RuntimeError(f"Report/Recipe inspection changed execution rows: {after}")
    state.update({
        "status": "PASS", "browser": browser,
        "reportId": reports[0]["id"], "recipeId": recipes[0]["id"],
        "recipeExecutionAuthorized": False, "afterReportCounts": after,
    })
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"demoId": state["demoId"], "status": "PASS", "reportId": state["reportId"], "recipeId": state["recipeId"]}, sort_keys=True))


def cleanup(state_path: Path) -> None:
    if not state_path.exists():
        return
    state = json.loads(state_path.read_text(encoding="utf-8"))
    queued = Queue("mdi-jobs", connection=Redis.from_url(os.environ["REDIS_URL"])).fetch_job(state.get("jobId", ""))
    if queued is not None:
        queued.delete()
    engine = create_engine(os.environ["MDI_TEST_DATABASE_URL"], future=True)
    with engine.begin() as connection:
        connection.execute(DropSchema(state["schemaName"], cascade=True))
    engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "verify-ui", "cleanup"))
    parser.add_argument("--demo", type=int, choices=range(1, 8), required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--browser", type=Path)
    args = parser.parse_args()
    if args.command == "run":
        run_demo(args.demo, args.state)
    elif args.command == "verify-ui":
        if args.browser is None:
            raise SystemExit("--browser is required")
        verify_ui_finalize(args.state, args.browser)
    else:
        cleanup(args.state)


if __name__ == "__main__":
    main()
