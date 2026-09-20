from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path

import pytest
from starlette.requests import ClientDisconnect

from mdi_api.infrastructure.phase2.runtime import Phase2ProductRuntime


def test_interrupted_upload_cleans_staging_and_terminally_closes_session(
    tmp_path: Path,
) -> None:
    runtime = Phase2ProductRuntime(tmp_path / "artifacts")
    runtime.ensure_project("project_f13")
    payload = b"a" * (2 * 1024 * 1024)
    created = runtime.create_upload_session(
        "project_f13",
        {
            "datasetName": "F13 interrupted upload",
            "files": [
                {
                    "clientFileId": "client-1",
                    "fileName": "large.bin",
                    "byteSize": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
            ],
        },
    )
    session_id = created["uploadSessionId"]
    file_id = created["files"][0]["fileId"]

    async def interrupted_body():
        yield payload[: 1024 * 1024]
        raise ClientDisconnect()

    with pytest.raises(ClientDisconnect):
        asyncio.run(
            runtime.put_upload_session_file(
                session_id,
                file_id,
                content_type="application/octet-stream",
                chunks=interrupted_body(),
            )
        )

    session = runtime.upload_sessions[session_id]
    assert session.status == "failed"
    assert {item.status for item in session.files.values()} == {"failed"}
    assert not (runtime.artifact_root / "upload_sessions" / session_id).exists()
    assert list(runtime.artifact_root.rglob("*.part")) == []
    assert runtime.datasets == {}


def test_one_failed_member_invalidates_atomic_multi_file_upload(
    tmp_path: Path,
) -> None:
    runtime = Phase2ProductRuntime(tmp_path / "artifacts")
    runtime.ensure_project("project_f13")
    first = b"formula,value\nSi,1\n"
    second = b"formula,value\nGe,2\n"
    created = runtime.create_upload_session(
        "project_f13",
        {
            "datasetName": "F13 atomic bundle",
            "files": [
                {
                    "clientFileId": "client-1",
                    "fileName": "first.csv",
                    "byteSize": len(first),
                    "sha256": hashlib.sha256(first).hexdigest(),
                },
                {
                    "clientFileId": "client-2",
                    "fileName": "second.csv",
                    "byteSize": len(second),
                    "sha256": hashlib.sha256(second).hexdigest(),
                },
            ],
        },
    )
    session_id = created["uploadSessionId"]
    first_id, second_id = [item["fileId"] for item in created["files"]]

    async def complete_body():
        yield first

    asyncio.run(
        runtime.put_upload_session_file(
            session_id,
            first_id,
            content_type="application/octet-stream",
            chunks=complete_body(),
        )
    )

    async def interrupted_body():
        yield second[:4]
        raise ClientDisconnect()

    with pytest.raises(ClientDisconnect):
        asyncio.run(
            runtime.put_upload_session_file(
                session_id,
                second_id,
                content_type="application/octet-stream",
                chunks=interrupted_body(),
            )
        )

    session = runtime.upload_sessions[session_id]
    assert session.status == "failed"
    assert {item.status for item in session.files.values()} == {"failed"}
    with pytest.raises(ValueError, match="UPLOAD_SESSION_NOT_WRITABLE"):
        runtime.complete_upload_session(session_id)
    assert not (runtime.artifact_root / "upload_sessions" / session_id).exists()
    assert runtime.datasets == {}
