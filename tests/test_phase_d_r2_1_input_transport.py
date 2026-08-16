from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import zipfile

from fastapi.testclient import TestClient

from mdi_api.input_transport import (
    INPUT_TRANSPORT_SCHEMA_VERSION,
    MAX_FILES_PER_UPLOAD,
    MAX_FILE_BYTES,
    MAX_TOTAL_UPLOAD_BYTES,
    input_transport_capability_contract,
)
from mdi_api.main import create_app
from mdi_api.phase2_runtime import get_phase2_runtime, reset_phase2_runtime
from mdi_artifact_core.electronic_contract import electronic_resource_hash


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _session(client: TestClient, project_id: str, files: list[tuple[str, bytes]], *, group: str | None = None) -> dict:
    response = client.post(
        f"/projects/{project_id}/upload-sessions",
        json={
            "datasetName": "transport regression",
            "files": [
                {
                    "clientFileId": f"client_{index}",
                    "fileName": name,
                    "byteSize": len(data),
                    "sha256": _sha(data),
                    "companionGroupId": group,
                }
                for index, (name, data) in enumerate(files, start=1)
            ],
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def _project(client: TestClient) -> str:
    response = client.post("/projects", json={"name": "Input transport regression"})
    assert response.status_code == 200, response.text
    return response.json()["id"]


def _upload(client: TestClient, session: dict, client_id: str, data: bytes) -> dict:
    file_record = next(item for item in session["files"] if item["clientFileId"] == client_id)
    response = client.put(
        f"/upload-sessions/{session['uploadSessionId']}/files/{file_record['fileId']}",
        content=data,
        headers={"Content-Type": "application/octet-stream"},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _client(tmp_path: Path) -> TestClient:
    reset_phase2_runtime(tmp_path / "artifacts")
    return TestClient(create_app())


def _electronic_resources() -> tuple[bytes, bytes]:
    band = {
        "schemaVersion": "phase10n5.electronic_band_resource.v1",
        "resourceId": "band_transport",
        "resourceVersion": "1",
        "resourceHash": "0" * 64,
        "calculationIdentity": "calc_transport",
        "sourceMetadata": {"code": "source", "method": "retained"},
        "structureIdentity": {"structureId": "structure_transport", "structureHash": "1" * 64},
        "energyUnit": "eV",
        "energyReference": "source_absolute",
        "fermiEnergyEv": 0.0,
        "spinMode": "non_spin_polarized",
        "reciprocalCoordinates": "fractional_reciprocal",
        "kpoints": [
            {"kpointId": "g", "fractionalCoordinates": [0, 0, 0], "pathDistance": 0.0, "segmentId": "s", "label": "G"},
            {"kpointId": "x", "fractionalCoordinates": [0.5, 0, 0], "pathDistance": 1.0, "segmentId": "s", "label": "X"},
        ],
        "pathSegments": [{"segmentId": "s", "startKpointId": "g", "endKpointId": "x", "breakAfter": False}],
        "bands": [
            {"bandId": "v", "spinChannel": "none", "energiesEv": [-1.0, -0.2], "occupations": [1, 1]},
            {"bandId": "c", "spinChannel": "none", "energiesEv": [0.8, 0.4], "occupations": [0, 0]},
        ],
    }
    dos = {
        "schemaVersion": "phase10n5.electronic_dos_resource.v1",
        "resourceId": "dos_transport",
        "resourceVersion": "1",
        "resourceHash": "0" * 64,
        "calculationIdentity": "calc_transport",
        "sourceMetadata": {"code": "source", "method": "retained"},
        "structureIdentity": {"structureId": "structure_transport", "structureHash": "1" * 64},
        "energyUnit": "eV",
        "energyReference": "source_absolute",
        "fermiEnergyEv": 0.0,
        "spinMode": "non_spin_polarized",
        "dosUnitSemantic": "states_per_ev_cell",
        "energiesEv": [-1.0, 0.0, 1.0],
        "totalDos": [{"channelId": "total", "spinChannel": "none", "values": [1.0, 0.1, 2.0]}],
        "projections": [],
        "projectionCompleteness": "UNKNOWN",
    }
    for value in (band, dos):
        value["resourceHash"] = electronic_resource_hash(value)
    return (
        json.dumps(band, sort_keys=True, separators=(",", ":")).encode(),
        json.dumps(dos, sort_keys=True, separators=(",", ":")).encode(),
    )


def test_binary_zip_bytes_survive_browser_api_materialization(tmp_path: Path) -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("materials.csv", "formula,value\nSi,1\n")
    payload = buffer.getvalue()
    client = _client(tmp_path)
    project_id = _project(client)
    session = _session(client, project_id, [("materials.zip", payload)])

    receipt = _upload(client, session, "client_1", payload)
    assert receipt == {
        "schemaVersion": "UploadSession/1.0",
        "uploadSessionId": session["uploadSessionId"],
        "fileId": session["files"][0]["fileId"],
        "clientFileId": "client_1",
        "status": "received",
        "byteSize": len(payload),
        "sha256": _sha(payload),
    }
    completed = client.post(f"/upload-sessions/{session['uploadSessionId']}/complete")
    assert completed.status_code == 200, completed.text
    dataset = completed.json()
    stored = get_phase2_runtime().artifact_storage.get_bytes(dataset["files"][0]["storageKey"])
    assert stored == payload
    assert dataset["files"][0]["sha256"] == _sha(payload)
    assert dataset["files"][0]["byteSize"] == len(payload)


def test_single_text_upload_remains_compatible(tmp_path: Path) -> None:
    payload = b"formula,target,prediction\nSi,1.0,1.1\n"
    client = _client(tmp_path)
    project_id = _project(client)
    session = _session(client, project_id, [("materials.csv", payload)])
    _upload(client, session, "client_1", payload)
    response = client.post(f"/upload-sessions/{session['uploadSessionId']}/complete")
    assert response.status_code == 200, response.text
    assert response.json()["fileCount"] == 1


def test_electronic_companions_are_order_independent_and_same_dataset(tmp_path: Path) -> None:
    band, dos = _electronic_resources()
    client = _client(tmp_path)
    project_id = _project(client)
    session = _session(client, project_id, [("band.json", band), ("dos.json", dos)], group="electronic_pair")

    _upload(client, session, "client_2", dos)
    _upload(client, session, "client_1", band)
    response = client.post(f"/upload-sessions/{session['uploadSessionId']}/complete")
    assert response.status_code == 200, response.text
    transport = response.json()["inputTransport"]
    assert transport["sameDatasetBinding"] is True
    assert transport["fileOrderIsSemanticAuthority"] is False
    assert transport["companionGroupIds"] == ["electronic_pair"]
    assert transport["objectKinds"] == ["ElectronicBand", "ElectronicDos"]


def test_cuka_xrd_and_structure_can_publish_in_one_dataset(tmp_path: Path, repo_root: Path) -> None:
    structure = (repo_root / "tests" / "fixtures" / "structures" / "simple_cubic.cif").read_bytes()
    resource = json.loads((repo_root / "tests" / "fixtures" / "experimental_xrd" / "phase13_demo3_xrd.json").read_text(encoding="utf-8"))
    xrd = json.dumps(resource, sort_keys=True, separators=(",", ":")).encode()
    client = _client(tmp_path)
    project_id = _project(client)
    session = _session(client, project_id, [("structure.cif", structure), ("xrd.json", xrd)], group="xrd_pair")
    _upload(client, session, "client_2", xrd)
    _upload(client, session, "client_1", structure)
    response = client.post(f"/upload-sessions/{session['uploadSessionId']}/complete")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["inputTransport"]["sameDatasetBinding"] is True
    assert "Structure" in payload["inputTransport"]["objectKinds"]
    assert payload["profile"]["experimentalXrdReadiness"]["resources"][0]["wavelengthUnit"] == "angstrom"


def test_partial_multi_resource_failure_does_not_publish_dataset(tmp_path: Path, repo_root: Path) -> None:
    structure = (repo_root / "tests" / "fixtures" / "structures" / "simple_cubic.cif").read_bytes()
    invalid = b'{"schemaVersion":"phase10n5.electronic_dos_resource.v1"}'
    client = _client(tmp_path)
    project_id = _project(client)
    session = _session(client, project_id, [("structure.cif", structure), ("invalid.json", invalid)], group="invalid_pair")
    _upload(client, session, "client_1", structure)
    _upload(client, session, "client_2", invalid)
    response = client.post(f"/upload-sessions/{session['uploadSessionId']}/complete")
    assert response.status_code == 400
    assert get_phase2_runtime().list_datasets() == []


def test_input_transport_contract_is_bounded_and_order_independent() -> None:
    contract = input_transport_capability_contract()
    assert contract["schemaVersion"] == INPUT_TRANSPORT_SCHEMA_VERSION
    assert contract["maxFilesPerSubmission"] == MAX_FILES_PER_UPLOAD
    assert contract["perFileByteCap"] == MAX_FILE_BYTES
    assert contract["totalByteCap"] == MAX_TOTAL_UPLOAD_BYTES
    assert contract["supportsBinaryBytes"] is True
    assert contract["supportsMultipleResources"] is True
    assert contract["fileOrderIsSemanticAuthority"] is False
    assert contract["partialFailurePolicy"] == "NO_DATASET_PUBLICATION_UNTIL_COMPLETE_BUNDLE_VALIDATES"
    assert len(str(contract["semanticHash"])) == 64


def test_upload_limits_hash_retry_and_content_type_are_enforced(tmp_path: Path) -> None:
    payload = b"formula,value\nSi,1\n"
    client = _client(tmp_path)
    project_id = _project(client)
    too_large = client.post(
        f"/projects/{project_id}/upload-sessions",
        json={
            "datasetName": "too large",
            "files": [{
                "clientFileId": "large",
                "fileName": "large.bin",
                "byteSize": MAX_FILE_BYTES + 1,
                "sha256": "0" * 64,
            }],
        },
    )
    assert too_large.status_code == 422

    session = _session(client, project_id, [("retry.csv", payload)])
    file_id = session["files"][0]["fileId"]
    wrong_type = client.put(
        f"/upload-sessions/{session['uploadSessionId']}/files/{file_id}",
        content=payload,
        headers={"Content-Type": "text/plain"},
    )
    assert wrong_type.status_code == 400
    wrong_bytes = client.put(
        f"/upload-sessions/{session['uploadSessionId']}/files/{file_id}",
        content=b"x" * len(payload),
        headers={"Content-Type": "application/octet-stream"},
    )
    assert wrong_bytes.status_code == 400
    _upload(client, session, "client_1", payload)
    completed = client.post(f"/upload-sessions/{session['uploadSessionId']}/complete")
    assert completed.status_code == 200, completed.text
