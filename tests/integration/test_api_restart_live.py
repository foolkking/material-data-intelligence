from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen
from uuid import UUID

from sqlalchemy import create_engine, func, select

from mdi_api.db import (
    messages,
    metadata,
    research_turn_events,
    research_turns,
)


ROOT = Path(__file__).resolve().parents[2]


def _free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _json_request(url: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    with urlopen(
        Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"} if body is not None else {},
            method="POST" if body is not None else "GET",
        ),
        timeout=5,
    ) as response:
        return json.load(response)


def _wait_health(port: int, process: subprocess.Popen, timeout: float = 40) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AssertionError(f"task-owned API exited unexpectedly: {process.returncode}")
        try:
            _json_request(f"http://127.0.0.1:{port}/health")
            return
        except (OSError, URLError):
            time.sleep(0.1)
    raise AssertionError("task-owned API did not become healthy")


def _start_api(port: int, environment: dict[str, str], log_path: Path) -> subprocess.Popen:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "mdi_api.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ]
    with log_path.open("ab") as log:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    _wait_health(port, process)
    return process


def _stop_owned_api(process: subprocess.Popen, port: int) -> None:
    assert process.args[0] == sys.executable
    assert process.args[1:4] == ["-m", "uvicorn", "mdi_api.main:app"]
    assert process.args[-1] == str(port)
    assert process.poll() is None
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)
    assert process.poll() is not None


def test_f11_a_real_api_process_restart_replays_one_durable_admission(
    tmp_path: Path,
) -> None:
    """The first HTTP response may be discarded; the new API replays one Turn."""

    database_path = tmp_path / "m4-01-api-restart.db"
    database_url = f"sqlite:///{database_path.as_posix()}"
    engine = create_engine(database_url, future=True)
    metadata.create_all(engine)
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in {
            "DATABASE_URL", "MDI_DATABASE_URL", "MDI_TEST_DATABASE_URL",
            "MDI_RUNTIME_PROFILE", "MDI_RUNTIME_BACKEND", "MDI_QUEUE_BACKEND",
            "REDIS_URL", "MDI_REDIS_URL", "MINIO_BUCKET", "MINIO_ENDPOINT",
            "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY",
        }
    }
    environment.update({
        "DATABASE_URL": database_url,
        "MDI_RUNTIME_BACKEND": "local",
        "MDI_QUEUE_BACKEND": "local",
        "MDI_ARTIFACT_BACKEND": "local",
        "MDI_ARTIFACT_ROOT": str(tmp_path / "artifacts"),
        "MDI_AUTH_REQUIRED": "false",
        "MDI_AGENT2_ORCHESTRATION_ENABLED": "false",
        "MDI_AGENT2_STARTUP_RECOVERY_ENABLED": "false",
        "PYTHONPATH": os.pathsep.join(
            str(ROOT / item)
            for item in (
                "apps/api",
                "packages/schemas",
                "packages/tool-registry",
                "packages/adapters",
                "packages/artifact-core",
                "packages/material-parsers",
                "services/workers",
                "services/llm",
            )
        ),
    })
    port = _free_port()
    base = f"http://127.0.0.1:{port}"
    process = None
    log_path = tmp_path / "api-process.log"
    try:
        process = _start_api(port, environment, log_path)
        project = _json_request(f"{base}/projects", {"name": "M4-01 API restart"})
        session = _json_request(
            f"{base}/projects/{project['id']}/research-sessions",
            {"title": "F11 admitted turn"},
        )
        endpoint = (
            f"{base}/api/projects/{project['id']}/research/sessions/"
            f"{session['id']}/turns"
        )
        request = {
            "message": "Analyze the current saved research data",
            "admission_key": "m4-01-live-process-restart",
        }
        admitted = _json_request(endpoint, request)
        first_pid = process.pid
        # Simulate the browser never receiving the 202: discard the response
        # and restart only this test-owned API process.
        _stop_owned_api(process, port)
        process = _start_api(port, environment, log_path)
        recovered = _json_request(endpoint, request)
        turn = _json_request(f"{base}/api/research/turns/{admitted['turn_id']}")
        listed = _json_request(endpoint)

        assert process.pid != first_pid
        assert recovered["turn_id"] == admitted["turn_id"] == str(turn["id"])
        assert recovered["user_message"]["id"] == admitted["user_message"]["id"]
        assert recovered["idempotent_replay"] is True
        assert [item["id"] for item in listed["items"]] == [admitted["turn_id"]]
        with engine.connect() as connection:
            assert connection.execute(
                select(func.count()).select_from(research_turns)
            ).scalar_one() == 1
            assert connection.execute(
                select(func.count()).select_from(messages)
                .where(messages.c.id == admitted["user_message"]["id"])
            ).scalar_one() == 1
            assert connection.execute(
                select(func.count()).select_from(research_turn_events)
                .where(research_turn_events.c.turn_id == UUID(admitted["turn_id"]))
            ).scalar_one() == 1
    finally:
        if process is not None and process.poll() is None:
            _stop_owned_api(process, port)
        engine.dispose()
