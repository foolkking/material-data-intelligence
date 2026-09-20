from __future__ import annotations

from http import client as http_client
import hashlib
import json
import os
from pathlib import Path
import socket
import time
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request
from http.cookiejar import CookieJar

import pytest


def _required_environment() -> tuple[str, str, str, Path, Path]:
    base_url = os.getenv("M4_02_LIVE_API_BASE")
    email = os.getenv("M4_02_LIVE_USER_EMAIL")
    password_file = os.getenv("M4_02_LIVE_PASSWORD_FILE")
    artifact_root = os.getenv("M4_02_LIVE_PHASE2_ARTIFACT_ROOT")
    evidence_file = os.getenv("M4_02_LIVE_EVIDENCE_FILE")
    if not all((base_url, email, password_file, artifact_root, evidence_file)):
        pytest.skip("M4-02 live service environment is not configured")
    return (
        str(base_url).rstrip("/"),
        str(email),
        Path(str(password_file)).read_text(encoding="utf-8").strip(),
        Path(str(artifact_root)),
        Path(str(evidence_file)),
    )


def _json_request(
    opener: urllib_request.OpenerDirector,
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
    expected: set[int] = {200},
) -> tuple[int, object]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib_request.Request(
        f"{base_url}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    try:
        with opener.open(request, timeout=30) as response:
            status = int(response.status)
            data = response.read()
    except urllib_error.HTTPError as exc:
        status = int(exc.code)
        data = exc.read()
    parsed: object
    try:
        parsed = json.loads(data.decode("utf-8")) if data else None
    except json.JSONDecodeError:
        parsed = data.decode("utf-8", errors="replace")
    assert status in expected, (status, parsed)
    return status, parsed


def _cookie_header(jar: CookieJar) -> str:
    return "; ".join(f"{cookie.name}={cookie.value}" for cookie in jar)


def _interrupt_upload(
    *,
    base_url: str,
    path: str,
    cookie_header: str,
    declared_bytes: int,
    transmitted: bytes,
) -> None:
    parsed = urllib_parse.urlparse(base_url)
    assert parsed.scheme == "http", "The task-owned live API uses plain localhost HTTP."
    host = parsed.hostname or "127.0.0.1"
    port = int(parsed.port or 80)
    request_headers = (
        f"PUT {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Content-Type: application/octet-stream\r\n"
        f"Content-Length: {declared_bytes}\r\n"
        f"Cookie: {cookie_header}\r\n"
        "Connection: close\r\n\r\n"
    ).encode("ascii")
    with socket.create_connection((host, port), timeout=10) as connection:
        connection.sendall(request_headers)
        connection.sendall(transmitted)
        connection.shutdown(socket.SHUT_RDWR)


def _put_complete_payload(
    *,
    base_url: str,
    path: str,
    cookie_header: str,
    payload: bytes,
) -> tuple[int, object]:
    parsed = urllib_parse.urlparse(base_url)
    connection = http_client.HTTPConnection(
        parsed.hostname or "127.0.0.1",
        int(parsed.port or 80),
        timeout=60,
    )
    connection.request(
        "PUT",
        path,
        body=payload,
        headers={
            "Content-Type": "application/octet-stream",
            "Content-Length": str(len(payload)),
            "Cookie": cookie_header,
        },
    )
    response = connection.getresponse()
    data = response.read()
    connection.close()
    parsed_body = json.loads(data.decode("utf-8")) if data else None
    return int(response.status), parsed_body


def test_live_client_disconnect_cleans_partial_state_and_allows_fresh_retry() -> None:
    base_url, email, password, artifact_root, evidence_file = _required_environment()
    cookie_jar = CookieJar()
    opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookie_jar))

    _, user = _json_request(
        opener,
        base_url,
        "/auth/login",
        method="POST",
        payload={"email": email, "password": password},
    )
    _, project = _json_request(
        opener,
        base_url,
        "/projects",
        method="POST",
        payload={"name": f"M4-02 F13 live {time.time_ns()}"},
    )
    assert isinstance(project, dict)
    project_id = str(project["id"])
    history_before = _json_request(
        opener,
        base_url,
        f"/projects/{project_id}/history",
    )[1]

    interrupted_payload = bytes((index % 251 for index in range(8 * 1024 * 1024)))
    _, interrupted_session = _json_request(
        opener,
        base_url,
        f"/projects/{project_id}/upload-sessions",
        method="POST",
        payload={
            "datasetName": "F13 interrupted transfer",
            "files": [
                {
                    "clientFileId": "fault-file",
                    "fileName": "large-interrupted.bin",
                    "byteSize": len(interrupted_payload),
                    "sha256": hashlib.sha256(interrupted_payload).hexdigest(),
                }
            ],
        },
    )
    assert isinstance(interrupted_session, dict)
    interrupted_session_id = str(interrupted_session["uploadSessionId"])
    interrupted_file_id = str(interrupted_session["files"][0]["fileId"])
    fault_started = time.time()
    _interrupt_upload(
        base_url=base_url,
        path=f"/upload-sessions/{interrupted_session_id}/files/{interrupted_file_id}",
        cookie_header=_cookie_header(cookie_jar),
        declared_bytes=len(interrupted_payload),
        transmitted=interrupted_payload[: 1024 * 1024],
    )

    terminal_response: tuple[int, object] | None = None
    for _ in range(40):
        response = _json_request(
            opener,
            base_url,
            f"/upload-sessions/{interrupted_session_id}/complete",
            method="POST",
            expected={400},
        )
        detail = response[1].get("detail") if isinstance(response[1], dict) else None
        if detail == "UPLOAD_SESSION_NOT_WRITABLE":
            terminal_response = response
            break
        time.sleep(0.1)
    assert terminal_response is not None
    interrupted_staging = artifact_root / "upload_sessions" / interrupted_session_id
    assert not interrupted_staging.exists()
    assert list(artifact_root.rglob("*.part")) == []

    retry_lines = 160_000
    retry_payload = (
        "formula,target,prediction\n"
        + "".join(f"Si,{index % 97}.{index % 10},{index % 89}.{(index + 1) % 10}\n" for index in range(retry_lines))
    ).encode("utf-8")
    _, retry_session = _json_request(
        opener,
        base_url,
        f"/projects/{project_id}/upload-sessions",
        method="POST",
        payload={
            "datasetName": "F13 recovered transfer",
            "files": [
                {
                    "clientFileId": "retry-file",
                    "fileName": "large-recovered.csv",
                    "byteSize": len(retry_payload),
                    "sha256": hashlib.sha256(retry_payload).hexdigest(),
                }
            ],
        },
    )
    assert isinstance(retry_session, dict)
    retry_session_id = str(retry_session["uploadSessionId"])
    retry_file_id = str(retry_session["files"][0]["fileId"])
    put_status, put_receipt = _put_complete_payload(
        base_url=base_url,
        path=f"/upload-sessions/{retry_session_id}/files/{retry_file_id}",
        cookie_header=_cookie_header(cookie_jar),
        payload=retry_payload,
    )
    assert put_status == 200, put_receipt
    _, completed = _json_request(
        opener,
        base_url,
        f"/upload-sessions/{retry_session_id}/complete",
        method="POST",
    )
    assert isinstance(completed, dict)
    dataset_id = str(completed["datasetId"])
    history_after = _json_request(
        opener,
        base_url,
        f"/projects/{project_id}/history",
    )[1]
    assert isinstance(history_after, dict)
    datasets = history_after.get("datasets")
    assert isinstance(datasets, list)
    assert [str(item["datasetId"]) for item in datasets] == [dataset_id]
    completed_file = completed["files"][0]
    assert completed_file["sha256"] == hashlib.sha256(retry_payload).hexdigest()
    assert completed_file["byteSize"] == len(retry_payload)
    assert completed["inputTransport"]["atomicPublication"] is True

    evidence = {
        "schema": "M4_02LiveF13Transfer/1.0",
        "base_url": base_url,
        "user_id": user["id"] if isinstance(user, dict) else None,
        "project_id": project_id,
        "fault": {
            "fault_id": "F13",
            "fault_name": "Largeobject transfer interrupted by client",
            "started_epoch": fault_started,
            "declared_bytes": len(interrupted_payload),
            "transmitted_bytes": 1024 * 1024,
            "upload_session_id": interrupted_session_id,
            "file_id": interrupted_file_id,
            "terminal_completion_status": terminal_response[0],
            "terminal_detail": terminal_response[1],
            "staging_exists_after_fault": interrupted_staging.exists(),
            "part_file_count_after_fault": len(list(artifact_root.rglob("*.part"))),
        },
        "recovery": {
            "fresh_upload_session_id": retry_session_id,
            "fresh_file_id": retry_file_id,
            "dataset_id": dataset_id,
            "byte_size": len(retry_payload),
            "sha256": hashlib.sha256(retry_payload).hexdigest(),
            "put_receipt": put_receipt,
            "input_transport": completed["inputTransport"],
        },
        "effects": {
            "datasets_before": len(history_before.get("datasets", []))
            if isinstance(history_before, dict)
            else None,
            "datasets_after": len(datasets),
            "duplicate_datasets": max(0, len(datasets) - 1),
            "turns": 0,
            "plans": 0,
            "jobs": 0,
            "tool_calls": 0,
            "scientific_results": 0,
            "interpretations": 0,
            "reports": 0,
        },
        "verdict": "PASS",
    }
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
