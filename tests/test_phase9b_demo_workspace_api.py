from __future__ import annotations

import json
import socket
import urllib.error
from pathlib import Path

from fastapi.testclient import TestClient

from mdi_api.main import create_app
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_api.routers.planner_providers import ProviderTestRequest, test_planner_provider as run_provider_test
from mdi_llm import MockLLMProvider
from mdi_tool_registry import load_manifests


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

    datasets = client.get("/datasets").json()
    assert any(dataset["datasetId"] == "dataset_demo" for dataset in datasets)

    detail = client.get("/datasets/dataset_demo").json()
    assert detail["datasetId"] == "dataset_demo"
    assert detail["demo"] is True

    profile = client.post("/datasets/dataset_demo/profile").json()
    assert profile["datasetId"] == "dataset_demo"
    assert profile["profileGenerated"] is True


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
