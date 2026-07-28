from __future__ import annotations

import json
import socket
import urllib.error
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from mdi_artifact_core import LocalArtifactExporter
from mdi_api.db import metadata
from mdi_api.main import create_app
from mdi_api.repositories import InMemoryRepositoryBundle, SqlAlchemyRepositoryBundle
from mdi_api.phase2_runtime import reset_phase2_runtime
from mdi_api.routers.planner import (
    PlannerJobsRequest,
    get_planner_job,
    get_planner_job_artifacts,
    get_planner_job_events,
    get_planner_job_result,
    get_planner_job_tool_calls,
    planner_jobs,
    reset_planner_runtime,
)
from mdi_api.routers.planner_providers import (
    ProviderResolveRequest,
    ProviderTestRequest,
    resolve_planner_provider,
    test_planner_provider as run_provider_test,
)
from mdi_llm import MockLLMProvider
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import run_queued_job


def _valid_plan() -> dict[str, object]:
    registry = load_manifests()
    return {
        "schemaVersion": "0.1",
        "goal": "test provider",
        "datasetId": "dataset_demo",
        "profileId": "profile_demo",
        "toolRegistryVersion": registry.version,
        "assumptions": [],
        "warnings": [],
        "steps": [
            {
                "stepId": "llm_step_1",
                "toolId": "ml.basic_metrics",
                "purpose": "Compute basic metrics",
                "reason": "The dataset has y_true and y_pred columns.",
                "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
                "params": {"targetColumn": "y_true", "predictionColumn": "y_pred"},
                "output": {"artifactTypes": ["metrics_json"]},
            }
        ],
        "expectedArtifacts": [{"name": "metrics.json", "type": "metrics_json", "fromStepId": "llm_step_1"}],
    }


def _valid_metrics_plan(dataset_id: str, profile_id: str) -> dict[str, object]:
    plan = _valid_plan()
    plan["datasetId"] = dataset_id
    plan["profileId"] = profile_id
    plan["steps"][0]["params"] = {"targetColumn": "y_true", "predictionColumn": "y_pred"}  # type: ignore[index]
    return plan


def test_runtime_health_endpoint_reports_workspace_dependencies() -> None:
    client = TestClient(create_app())

    response = client.get("/health/runtime")

    assert response.status_code == 200
    body = response.json()
    assert body["api"]["status"] == "ok"
    assert {"database", "redis", "artifactStorage", "worker", "llmProvider"}.issubset(body)


def test_runtime_health_sqlite_missing_db_is_unknown_without_creating_file(monkeypatch, tmp_path: Path) -> None:
    missing_db = tmp_path / "not_initialized.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{missing_db.as_posix()}")
    client = TestClient(create_app())

    response = client.get("/health/runtime")

    assert response.status_code == 200
    body = response.json()
    assert body["database"]["status"] == "unknown"
    assert body["database"]["reason"] == "not initialized"
    assert not missing_db.exists()


def test_runtime_health_probe_failures_are_redacted(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://mdi:db-secret@127.0.0.1:9/mdi")
    monkeypatch.setenv("MDI_QUEUE_BACKEND", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://:redis-secret@127.0.0.1:9/0")
    monkeypatch.setenv("MDI_ARTIFACT_BACKEND", "minio")
    monkeypatch.setenv("MINIO_ENDPOINT", "http://127.0.0.1:9")
    monkeypatch.setenv("MINIO_ACCESS_KEY", "minio-access")
    monkeypatch.setenv("MINIO_SECRET_KEY", "minio-secret")
    client = TestClient(create_app())

    response = client.get("/health/runtime")

    assert response.status_code == 200
    body = response.json()
    assert body["database"]["status"] == "unknown"
    assert body["redis"]["status"] == "unknown"
    assert body["artifactStorage"]["status"] == "unknown"
    dumped = json.dumps(body, ensure_ascii=False)
    assert "db-secret" not in dumped
    assert "redis-secret" not in dumped
    assert "minio-secret" not in dumped
    assert "minio-access" not in dumped


def test_browser_cors_preflight_allows_planner_workspace_routes() -> None:
    client = TestClient(create_app())
    routes = [
        ("/health/runtime", "GET"),
        ("/planner/providers", "GET"),
        ("/datasets", "GET"),
        ("/planner/providers/status", "GET"),
        ("/me/secrets", "POST"),
        ("/datasets/demo", "POST"),
        ("/planner/providers/test", "POST"),
    ]

    for path, method in routes:
        response = client.options(
            path,
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": method,
                "Access-Control-Request-Headers": "content-type",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_demo_dataset_detail_and_profile_are_backend_generated() -> None:
    client = TestClient(create_app())

    demo = client.post("/datasets/demo")
    assert demo.status_code == 200
    demo_body = demo.json()
    assert demo_body["datasetId"] == "dataset_demo"
    assert demo_body["demo"] is True
    assert demo_body["profile"]["datasetId"] == "dataset_demo"
    assert demo_body["profile"]["tableSummary"]["nRows"] >= 1
    assert demo_body["profile"]["profileContractVersion"] == "2.0"
    assert demo_body["profile"]["semanticHash"]
    assert any(column["column"] == "y_true" for column in demo_body["profile"]["semanticColumns"])
    readiness = {item["capability"]: item for item in demo_body["profile"]["analysisReadiness"]}
    assert readiness["regression_evaluation"]["dataStatus"] == "READY"
    assert readiness["regression_evaluation"]["platformStatus"] == "NOT_IMPLEMENTED"
    assert readiness["uncertainty_evaluation"]["platformStatus"] == "NOT_IMPLEMENTED"

    datasets = client.get("/datasets").json()
    assert any(dataset["datasetId"] == "dataset_demo" for dataset in datasets)

    detail = client.get("/datasets/dataset_demo").json()
    assert detail["datasetId"] == "dataset_demo"
    assert detail["demo"] is True

    profile = client.post("/datasets/dataset_demo/profile").json()
    assert profile["datasetId"] == "dataset_demo"
    assert profile["profileGenerated"] is True
    assert profile["profileContractVersion"] == "2.0"
    assert profile["semanticHash"] == demo_body["profile"]["semanticHash"]


def test_provider_catalog_status_and_mock_test_endpoint() -> None:
    client = TestClient(create_app())

    catalog = client.get("/planner/providers").json()
    provider_ids = {provider["id"] for provider in catalog["providers"]}
    assert {"mock", "openai", "deepseek", "custom"}.issubset(provider_ids)

    status = client.get("/planner/providers/status").json()
    assert status["provider"] in {"mock", "openai_compatible"}
    assert "api" not in json.dumps(status).lower()

    result = client.post("/planner/providers/test", json={"provider": "mock"}).json()
    assert result["ok"] is True
    assert result["validated"] is True


def test_provider_resolve_reflects_current_ui_config_without_network() -> None:
    client = TestClient(create_app())
    secret_value = "sk-provider-resolve"

    mock_result = client.post("/planner/providers/resolve", json={"provider": "mock"}).json()
    assert mock_result["ok"] is True
    assert mock_result["provider"] == "mock"
    assert mock_result["willUseLiveProvider"] is False

    live_result = resolve_planner_provider(
        ProviderResolveRequest(
            provider="openai_compatible",
            baseUrl="https://api.deepseek.com/v1",
            model="deepseek-chat",
            secretId="secret_resolve",
        ),
        secret_resolver=lambda secret_id: secret_value if secret_id == "secret_resolve" else None,
    )
    assert live_result["ok"] is True
    assert live_result["provider"] == "openai_compatible"
    assert live_result["model"] == "deepseek-chat"
    assert live_result["willUseLiveProvider"] is True
    assert live_result["secretConfigured"] is True
    assert live_result["source"] == "secret"
    assert secret_value not in json.dumps(live_result, ensure_ascii=False)

    missing = resolve_planner_provider(
        ProviderResolveRequest(provider="openai_compatible", model="deepseek-chat", secretId="missing"),
        secret_resolver=lambda _: None,
    )
    assert missing["ok"] is False
    assert missing["status"] == "not_configured"
    assert missing["willUseLiveProvider"] is False
    assert missing["redacted"] is True


def test_secret_list_never_returns_plaintext_key() -> None:
    client = TestClient(create_app())
    secret_value = "sk-phase9b-secret"

    created = client.post(
        "/me/secrets",
        json={"provider": "deepseek", "alias": "Demo DeepSeek", "value": secret_value},
    ).json()
    listed = client.get("/me/secrets").json()

    body = json.dumps({"created": created, "listed": listed}, ensure_ascii=False)
    assert secret_value not in body
    assert created["alias"] == "Demo DeepSeek"
    assert created["maskedPreview"] == "••••••••"
    assert created["status"] == "active"


def test_openai_compatible_provider_test_fake_success_and_redaction() -> None:
    secret_value = "sk-provider-success"

    def fake_transport(**_: object) -> dict[str, object]:
        return {"choices": [{"message": {"content": json.dumps(_valid_plan())}, "finish_reason": "stop"}]}

    result = run_provider_test(
        ProviderTestRequest(
            provider="openai_compatible",
            baseUrl="https://api.deepseek.com/v1",
            model="deepseek-chat",
            secretId="secret_success",
        ),
        transport=fake_transport,
        secret_resolver=lambda secret_id: secret_value if secret_id == "secret_success" else None,
    )

    assert result["ok"] is True
    assert result["validated"] is True
    assert secret_value not in json.dumps(result, ensure_ascii=False)


def test_provider_test_failures_are_safe_and_redacted() -> None:
    secret_value = "sk-provider-error"

    def non_json_transport(**_: object) -> dict[str, object]:
        return {"choices": [{"message": {"content": "not json"}, "finish_reason": "stop"}]}

    non_json = run_provider_test(
        ProviderTestRequest(provider="openai_compatible", secretId="secret_error"),
        transport=non_json_transport,
        secret_resolver=lambda _: secret_value,
    )
    assert non_json["ok"] is False
    assert non_json["errorType"] == "provider_response_invalid"
    assert secret_value not in json.dumps(non_json, ensure_ascii=False)

    def auth_failed_transport(**_: object) -> dict[str, object]:
        raise urllib.error.HTTPError("https://provider.test", 401, "Unauthorized", {}, None)

    auth_failed = run_provider_test(
        ProviderTestRequest(provider="openai_compatible", secretId="secret_error"),
        transport=auth_failed_transport,
        secret_resolver=lambda _: secret_value,
    )
    assert auth_failed["ok"] is False
    assert auth_failed["errorType"] == "provider_auth_failed"
    assert secret_value not in json.dumps(auth_failed, ensure_ascii=False)

    def timeout_transport(**_: object) -> dict[str, object]:
        raise socket.timeout()

    timeout = run_provider_test(
        ProviderTestRequest(provider="openai_compatible", secretId="secret_error"),
        transport=timeout_transport,
        secret_resolver=lambda _: secret_value,
    )
    assert timeout["ok"] is False
    assert timeout["errorType"] == "provider_timeout"
    assert secret_value not in json.dumps(timeout, ensure_ascii=False)


def test_validation_failure_still_persists_no_plan_job_or_enqueue() -> None:
    repos = InMemoryRepositoryBundle.create()
    bad_plan = _valid_plan()
    bad_plan["steps"][0]["params"]["api_key"] = "sk-must-not-persist"  # type: ignore[index]

    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="run invalid plan",
            projectId="project_9b",
            datasetId="dataset_9b",
            enqueue=True,
        ),
        provider=MockLLMProvider(fixed_plan=bad_plan),
        repositories=repos,
        registry=load_manifests(),
    )

    assert result.ok is False
    assert result.job_id is None
    assert result.plan_id is None
    assert result.plan is None
    assert "sk-must-not-persist" not in json.dumps(result.__dict__, ensure_ascii=False)
    assert repos.jobs.records == {}
    assert repos.analysis_plans.records == {}


def test_local_planner_enqueue_executes_uploaded_dataset_through_worker(tmp_path: Path) -> None:
    phase2 = reset_phase2_runtime(tmp_path / "phase2")
    phase2.ensure_project("project_local")
    uploaded = phase2.upload_dataset(
        {
            "projectId": "project_local",
            "datasetName": "Uploaded metrics",
            "files": [
                {
                    "fileName": "metrics.csv",
                    "content": "formula,y_true,y_pred\nSiO2,2.1,2.0\nAl2O3,3.4,3.5\nCaO,1.8,1.9\n",
                }
            ],
        }
    )
    dataset_id = uploaded["datasetId"]
    profile_id = uploaded["profile"]["profileId"]
    reset_planner_runtime()

    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="run uploaded metrics",
            projectId="project_local",
            datasetId=dataset_id,
            profileId=profile_id,
            enqueue=True,
        ),
        provider=MockLLMProvider(fixed_plan=_valid_metrics_plan(dataset_id, profile_id)),
        registry=load_manifests(),
    )

    assert result.ok is True
    assert result.enqueued is True
    assert result.executed is True
    assert result.job_id is not None
    job = get_planner_job(result.job_id)
    events = get_planner_job_events(result.job_id)
    tool_calls = get_planner_job_tool_calls(result.job_id)
    artifacts = get_planner_job_artifacts(result.job_id)
    summary = get_planner_job_result(result.job_id)

    assert job["status"] == "completed"
    assert job["toolCallCount"] == 1
    assert tool_calls[0]["toolId"] == "ml.basic_metrics"
    assert tool_calls[0]["stepId"] == "llm_step_1"
    assert {event["eventType"] for event in events} >= {"data.loaded", "plan.loaded", "tool.completed", "job.completed"}
    assert any(artifact["type"] == "metrics_json" for artifact in artifacts)
    assert summary["status"] == "completed"
    assert summary["artifactCount"] >= 1


def test_mock_planner_binds_numeric_profile_columns_for_official_matpes_csv(tmp_path: Path) -> None:
    phase2 = reset_phase2_runtime(tmp_path / "phase2")
    phase2.ensure_project("project_local")
    uploaded = phase2.upload_dataset(
        {
            "projectId": "project_local",
            "datasetName": "MatPES atomic energies",
            "files": [
                {
                    "fileName": "matpes_atomic_energies.csv",
                    "content": (
                        "element,PBE,r2SCAN\n"
                        "Ac,-0.24210133,-65.08565284\n"
                        "Ag,-0.19840574,-18.47864697\n"
                        "Al,-0.18845328,-2.33409173\n"
                    ),
                }
            ],
        }
    )
    dataset_id = uploaded["datasetId"]
    profile_id = uploaded["profile"]["profileId"]
    reset_planner_runtime()

    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="请基于当前数据表计算基础统计或误差指标，并生成结果摘要。",
            projectId="project_local",
            datasetId=dataset_id,
            profileId=profile_id,
            enqueue=True,
        ),
        provider=MockLLMProvider(),
        registry=load_manifests(),
    )

    assert result.ok is True
    assert result.enqueued is True
    assert result.executed is True
    assert result.job_id is not None
    assert result.plan is not None
    params = result.plan["steps"][0]["params"]  # type: ignore[index]
    assert params == {"targetColumn": "PBE", "predictionColumn": "r2SCAN"}

    job = get_planner_job(result.job_id)
    events = get_planner_job_events(result.job_id)
    tool_calls = get_planner_job_tool_calls(result.job_id)
    artifacts = get_planner_job_artifacts(result.job_id)
    summary = get_planner_job_result(result.job_id)

    assert job["status"] == "completed"
    assert tool_calls[0]["status"] == "completed"
    assert tool_calls[0]["params"] == {"targetColumn": "PBE", "predictionColumn": "r2SCAN"}
    assert {event["eventType"] for event in events} >= {"data.loaded", "plan.loaded", "tool.completed", "job.completed"}
    assert any(artifact["type"] == "metrics_json" for artifact in artifacts)
    assert summary["status"] == "completed"
    assert summary["artifactCount"] >= 1


def test_mock_planner_generates_numeric_summary_for_ward_csv(tmp_path: Path) -> None:
    phase2 = reset_phase2_runtime(tmp_path / "phase2")
    phase2.ensure_project("project_local")
    uploaded = phase2.upload_dataset(
        {
            "projectId": "project_local",
            "datasetName": "Ward metallic glasses",
            "files": [
                {
                    "fileName": "ward_metallic_glasses.csv",
                    "content": (
                        "material_id,composition,gfa_type,D_max,dTx,Unnamed: 4,comment\n"
                        "ward-1,Ag20Al25La55,Ribbon,0.2,,,\n"
                        "ward-2,Ag15Al10Mg75,Ribbon,0.2,,,\n"
                        "ward-3,Ag10Al20La70,Bulk,2.0,40.0,,\n"
                        "ward-4,Cu50Zr50,Bulk,5.0,55.5,,\n"
                        "ward-5,Zr60Cu30Al10,Bulk,8.0,75.0,,\n"
                    ),
                }
            ],
        }
    )
    dataset_id = uploaded["datasetId"]
    profile_id = uploaded["profile"]["profileId"]
    columns = {column["name"]: column for column in uploaded["profile"]["tableSummary"]["columns"]}
    assert columns["dTx"]["dtype"] == "number"
    reset_planner_runtime()

    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Please summarize Ward metallic glasses numeric columns, composition fields, and categorical fields.",
            projectId="project_local",
            datasetId=dataset_id,
            profileId=profile_id,
            enqueue=True,
        ),
        provider=MockLLMProvider(),
        registry=load_manifests(),
    )

    assert result.ok is True
    assert result.executed is True
    assert result.plan is not None
    step = result.plan["steps"][0]  # type: ignore[index]
    assert step["toolId"] == "table.numeric_summary"
    params = step["params"]
    assert "D_max" in params["numericColumns"]
    assert "dTx" in params["numericColumns"]
    assert "gfa_type" in params["categoricalColumns"]

    assert result.job_id is not None
    job = get_planner_job(result.job_id)
    tool_calls = get_planner_job_tool_calls(result.job_id)
    artifacts = get_planner_job_artifacts(result.job_id)
    assert job["status"] == "completed"
    assert tool_calls[0]["status"] == "completed"
    assert tool_calls[0]["toolId"] == "table.numeric_summary"
    assert tool_calls[0]["params"] == params
    assert any(artifact["type"] == "table_json" and artifact["name"] == "numeric_summary.json" for artifact in artifacts)


def test_uploaded_dataset_plan_with_missing_input_refs_is_rejected_before_persistence(tmp_path: Path) -> None:
    phase2 = reset_phase2_runtime(tmp_path / "phase2")
    phase2.ensure_project("project_local")
    uploaded = phase2.upload_dataset(
        {
            "projectId": "project_local",
            "datasetName": "Uploaded metrics",
            "files": [{"fileName": "metrics.csv", "content": "formula,y_true,y_pred\nSiO2,2.1,2.0\n"}],
        }
    )
    dataset_id = uploaded["datasetId"]
    profile_id = uploaded["profile"]["profileId"]
    reset_planner_runtime()
    bad_plan = _valid_metrics_plan(dataset_id, profile_id)
    bad_plan["steps"][0]["inputRefs"] = []  # type: ignore[index]

    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="run uploaded metrics",
            projectId="project_local",
            datasetId=dataset_id,
            profileId=profile_id,
            enqueue=True,
        ),
        provider=MockLLMProvider(fixed_plan=bad_plan),
        registry=load_manifests(),
    )

    assert result.ok is False
    assert result.job_id is None
    assert result.plan_id is None
    assert result.enqueued is False
    assert any(error["code"] == "INPUT_REF_MISSING" for error in result.validation_errors)


def test_run_queued_job_rebuilds_object_store_from_persisted_normalized_exports(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "worker.sqlite"
    artifact_root = tmp_path / "artifacts"
    engine = create_engine(f"sqlite:///{db_path.as_posix()}", future=True, connect_args={"check_same_thread": False})
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)

    exported = LocalArtifactExporter(artifact_root).export_normalized_object(
        object_id="obj_dataframe_metrics",
        storage_key="normalized/obj_dataframe_metrics/data.json",
        payload=[
            {"formula": "LiFePO4", "y_true": 3.45, "y_pred": 3.40},
            {"formula": "NaCl", "y_true": 1.20, "y_pred": 1.25},
            {"formula": "SiO2", "y_true": 2.10, "y_pred": 2.00},
        ],
        metadata={
            "nRows": 3,
            "nColumns": 3,
            "columns": [
                {"name": "formula", "dtype": "string", "inferredRole": "formula"},
                {"name": "y_true", "dtype": "number", "inferredRole": "target"},
                {"name": "y_pred", "dtype": "number", "inferredRole": "prediction"},
            ],
        },
        project_id="project_worker",
        dataset_id="dataset_worker",
        provenance={"phase": "test", "objectType": "DataFrame"},
    )
    normalized_exports = [
        {
            "objectId": exported.object_id,
            "storageKey": exported.storage_key,
            "metadataKey": exported.metadata_key,
            "contentHash": exported.content_hash,
        }
    ]

    repos.projects.save({"id": "project_worker", "name": "Worker Project"})
    repos.datasets.save(
        {
            "id": "dataset_worker",
            "projectId": "project_worker",
            "name": "Persisted Dataset",
            "status": "profile_ready",
            "metadata": {"normalizedExports": normalized_exports},
        }
    )
    repos.data_profiles.save(
        DataProfile(
            profileId="profile_worker",
            datasetId="dataset_worker",
            version="1",
            datasetType="ml_results",
            files=[],
            objects=[],
            tableSummary={"nRows": 3, "columns": [{"name": "y_true"}, {"name": "y_pred"}]},
            structureSummary={"nStructures": 0},
            qualityIssues=[],
            createdAt="2026-07-04T00:00:00Z",
        )
    )
    repos.analysis_plans.save_plan(
        {
            "id": "plan_worker",
            "projectId": "project_worker",
            "datasetId": "dataset_worker",
            "profileId": "profile_worker",
            "planSource": "mock",
            "plannerProvider": "mock",
            "analysisPlan": _valid_metrics_plan("dataset_worker", "profile_worker"),
            "validationStatus": "validated",
            "createdBy": "user_local",
        }
    )
    repos.jobs.save(
        {
            "id": "job_worker",
            "projectId": "project_worker",
            "datasetId": "dataset_worker",
            "planId": "plan_worker",
            "kind": "planner",
            "status": "queued",
        }
    )
    repos.analysis_plans.attach_plan_to_job("plan_worker", "job_worker")
    engine.dispose()

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("MDI_ARTIFACT_BACKEND", "local")
    monkeypatch.setenv("MDI_ARTIFACT_ROOT", str(artifact_root))

    result = run_queued_job("job_worker")

    verify_engine = create_engine(f"sqlite:///{db_path.as_posix()}", future=True, connect_args={"check_same_thread": False})
    verification_repos = SqlAlchemyRepositoryBundle.create(verify_engine)
    events = verification_repos.job_events.list_for_job("job_worker")
    tool_calls = verification_repos.tool_calls.list_for_job("job_worker")
    artifacts = verification_repos.artifacts.list_for_job("job_worker")
    job = verification_repos.jobs.get("job_worker")

    assert result.status == "completed"
    assert job["status"] == "completed"
    assert [event.eventType for event in events] == [
        "job.running",
        "plan.loaded",
        "data.loaded",
        "tool.started",
        "artifact.ready",
        "tool.completed",
        "job.completed",
    ]
    assert len(tool_calls) == 1
    assert tool_calls[0]["toolId"] == "ml.basic_metrics"
    assert tool_calls[0]["stepId"] == "llm_step_1"
    assert len(artifacts) == 1
    assert artifacts[0]["type"] == "metrics_json"
    verify_engine.dispose()
