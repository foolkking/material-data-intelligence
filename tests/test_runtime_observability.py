from __future__ import annotations

import json
import logging
from types import SimpleNamespace

from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from mdi_api.main import create_app
from mdi_api.observability import (
    LOCAL_RELEASE,
    bounded_correlation,
    exception_event,
    release_sha,
)
from mdi_api.routers.observability import ClientExceptionEvent
from mdi_api.routers.auth import CurrentUser, get_current_user
from mdi_workers.observability import rq_exception_correlation, rq_exception_handler


def test_release_sha_and_correlation_are_bounded() -> None:
    assert release_sha({"MDI_RELEASE_SHA": "A" * 40}) == "a" * 40
    assert release_sha({"MDI_RELEASE_SHA": "not-a-sha"}) == LOCAL_RELEASE
    assert bounded_correlation(
        {
            "requestId": "request-1",
            "researchTurnId": "turn-1",
            "unknown": "not-included",
            "jobId": "password=do-not-log",
        }
    ) == {
        "requestId": "request-1",
        "researchTurnId": "turn-1",
    }


def test_exception_event_never_serializes_message_trace_or_private_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MDI_RELEASE_SHA", "b" * 40)
    error = RuntimeError(
        "password=LocalAcceptance-2026! C:\\Users\\private\\provider-payload.json"
    )

    event = exception_event(
        component="api",
        error=error,
        correlation={
            "requestId": "request-2",
            "contextManifestId": "manifest-2",
            "prompt": "must-not-appear",
        },
    )
    serialized = json.dumps(event)

    assert event["releaseSha"] == "b" * 40
    assert event["errorType"] == "RuntimeError"
    assert event["correlation"] == {
        "contextManifestId": "manifest-2",
        "requestId": "request-2",
    }
    for forbidden in (
        "LocalAcceptance",
        "provider-payload",
        "password",
        "prompt",
        "Users",
        "traceback",
    ):
        assert forbidden not in serialized


def test_api_unhandled_exception_returns_request_id_and_logs_safe_correlation(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("MDI_RELEASE_SHA", "c" * 40)
    app = create_app()

    @app.get("/api/research/turns/{turn_id}/observability-test")
    def explode(turn_id: str) -> None:
        del turn_id
        raise RuntimeError(
            "Bearer secret C:\\private\\provider-payload.json"
        )

    client = TestClient(app, raise_server_exceptions=False)
    with caplog.at_level(logging.ERROR, logger="uvicorn.error"):
        response = client.get(
            "/api/research/turns/turn-safe/observability-test",
            headers={
                "X-Request-ID": "request-safe",
                "X-MDI-Context-Manifest-ID": "manifest-safe",
            },
        )

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "request-safe"
    assert response.json() == {
        "detail": "请求处理失败。",
        "requestId": "request-safe",
    }
    log_text = caplog.text
    assert '"releaseSha":"cccccccccccccccccccccccccccccccccccccccc"' in log_text
    assert '"requestId":"request-safe"' in log_text
    assert '"researchTurnId":"turn-safe"' in log_text
    assert '"contextManifestId":"manifest-safe"' in log_text
    assert "secret" not in log_text
    assert "provider-payload" not in log_text


def test_client_exception_contract_rejects_path_query_and_extra_payload() -> None:
    with pytest.raises(ValidationError):
        ClientExceptionEvent.model_validate(
            {
                "schemaVersion": "ClientExceptionEvent/1.0",
                "source": "unhandledrejection",
                "releaseSha": "d" * 40,
                "route": "/projects/project?token=secret",
                "errorType": "Error",
                "clientEventId": "client-1",
                "correlation": {},
                "message": "must not be accepted",
            }
        )


def test_authenticated_client_exception_is_captured_without_client_message(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("MDI_RELEASE_SHA", "d" * 40)
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="observer",
        email="observer@example.invalid",
        displayName="Observer",
        roles=["viewer"],
    )
    client = TestClient(app)
    with caplog.at_level(logging.ERROR, logger="mdi_api.routers.observability"):
        response = client.post(
            "/api/observability/client-exceptions",
            headers={"X-Request-ID": "client-event-1"},
            json={
                "schemaVersion": "ClientExceptionEvent/1.0",
                "source": "unhandledrejection",
                "releaseSha": "f" * 40,
                "route": "/tasks",
                "errorType": "TypeError",
                "clientEventId": "client-event-1",
                "correlation": {"researchTurnId": "turn-safe"},
            },
        )

    assert response.status_code == 202
    assert response.headers["X-Request-ID"] == "client-event-1"
    assert '"component":"frontend"' in caplog.text
    assert '"frontendReleaseSha":"ffffffffffffffffffffffffffffffffffffffff"' in caplog.text
    assert '"researchTurnId":"turn-safe"' in caplog.text
    assert "message" not in caplog.text


def test_worker_exception_handler_logs_only_bounded_lineage(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("MDI_RELEASE_SHA", "e" * 40)
    job = SimpleNamespace(
        id="rq-job-1",
        func_name="mdi_api.research_agent_worker.run_queued_turn",
        args=("turn-1", "raw prompt must not be inspected"),
    )

    assert rq_exception_correlation(job) == {
        "jobId": "rq-job-1",
        "researchTurnId": "turn-1",
    }
    with caplog.at_level(logging.ERROR, logger="mdi.worker"):
        assert rq_exception_handler(
            job,
            RuntimeError,
            RuntimeError(
                "redis://user:secret@localhost/0 C:\\private\\worker.py"
            ),
            None,
        )

    assert '"jobId":"rq-job-1"' in caplog.text
    assert '"researchTurnId":"turn-1"' in caplog.text
    assert '"releaseSha":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"' in caplog.text
    assert "redis://" not in caplog.text
    assert "worker.py" not in caplog.text
    assert "raw prompt" not in caplog.text
