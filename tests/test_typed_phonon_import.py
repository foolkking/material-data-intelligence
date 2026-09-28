from __future__ import annotations

import asyncio
import copy
import hashlib
import json
from pathlib import Path

import pytest

from mdi_api.phase2_runtime import Phase2ProductRuntime
from mdi_artifact_core import PHONON_BAND_SCHEMA_VERSION, PHONON_DOS_SCHEMA_VERSION
from mdi_material_parsers import map_normalized_phonon_resource


ROOT = Path(__file__).resolve().parents[1]
BAND_PATH = ROOT / "tests/fixtures/phonon_contract/stable_band.json"
DOS_PATH = ROOT / "tests/fixtures/phonon_contract/total_dos.json"
STRUCTURE_PATH = ROOT / "tests/fixtures/structures/POSCAR"


def _file(path: Path, *, kind: str | None = None, version: str | None = None) -> dict[str, str]:
    value = {"fileName": path.name, "content": path.read_text(encoding="utf-8")}
    if kind is not None:
        value["importKind"] = kind
    if version is not None:
        value["contractVersion"] = version
    return value


def _runtime(tmp_path: Path) -> Phase2ProductRuntime:
    runtime = Phase2ProductRuntime(tmp_path / "artifacts")
    runtime.ensure_project("project_a")
    runtime.ensure_project("project_b")
    return runtime


def test_explicit_typed_import_projects_existing_phonon_resources_into_profile(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    result = runtime.upload_dataset({
        "projectId": "project_a",
        "datasetName": "typed phonon",
        "files": [
            _file(BAND_PATH, kind="phonon_band", version=PHONON_BAND_SCHEMA_VERSION),
            _file(DOS_PATH, kind="phonon_dos", version=PHONON_DOS_SCHEMA_VERSION),
            _file(STRUCTURE_PATH),
        ],
    })

    profile = result["profile"]
    assert {item["objectType"] for item in profile["objects"]} == {"PhononBand", "PhononDos", "Structure"}
    assert profile["phononSummary"]["resourceKinds"] == ["PhononBand", "PhononDos"]
    phonon_resources = [item for item in profile["resourceSemantics"] if item["objectType"].startswith("Phonon")]
    assert [item["objectType"] for item in phonon_resources] == ["PhononBand", "PhononDos"]
    assert all(item["capabilities"] == ["phonon"] for item in phonon_resources)
    assert set(profile["phononSummary"]["resourceIds"]) == {item["objectId"] for item in phonon_resources}
    assert len(result["normalizedExports"]) == 3


def test_generic_json_upload_remains_mapping_only(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    result = runtime.upload_dataset({
        "projectId": "project_a",
        "datasetName": "generic JSON",
        "files": [_file(BAND_PATH)],
    })
    assert result["profile"]["objects"] == []
    assert result["profile"]["phononSummary"] is None
    assert result["files"][0]["status"] == "unsupported"


@pytest.mark.parametrize(
    ("path", "kind", "version", "code"),
    [
        (BAND_PATH, "phonon_dos", PHONON_BAND_SCHEMA_VERSION, "TYPED_PHONON_IMPORT_KIND_MISMATCH"),
        (DOS_PATH, "phonon_band", PHONON_DOS_SCHEMA_VERSION, "TYPED_PHONON_IMPORT_KIND_MISMATCH"),
        (BAND_PATH, "phonon_band", "unknown.v1", "TYPED_PHONON_IMPORT_CONTRACT_VERSION_MISMATCH"),
    ],
)
def test_declared_kind_and_version_must_match_exact_contract(
    tmp_path: Path, path: Path, kind: str, version: str, code: str,
) -> None:
    runtime = _runtime(tmp_path)
    with pytest.raises(ValueError, match=code):
        runtime.upload_dataset({
            "projectId": "project_a",
            "datasetName": "invalid typed import",
            "files": [_file(path, kind=kind, version=version)],
        })


def test_duplicate_and_prototype_keys_are_rejected_before_resource_creation(tmp_path: Path) -> None:
    original = BAND_PATH.read_text(encoding="utf-8")
    duplicate = original.replace(
        '"schema_version": "phase10h.phonon_band.v1"',
        '"schema_version": "phase10h.phonon_band.v1", "schema_version": "phase10h.phonon_band.v1"',
        1,
    )
    prototype = original.replace(
        '"schema_version": "phase10h.phonon_band.v1"',
        '"__proto__": {}, "schema_version": "phase10h.phonon_band.v1"',
        1,
    )
    for name, content, code in (
        ("duplicate.json", duplicate, "Duplicate JSON key"),
        ("prototype.json", prototype, "Prototype-shaped JSON keys"),
    ):
        path = tmp_path / name
        path.write_text(content, encoding="utf-8")
        with pytest.raises(ValueError, match=code):
            map_normalized_phonon_resource(
                path, dataset_id="dataset_a", file_id="file_001",
                declared_kind="phonon_band", declared_contract_version=PHONON_BAND_SCHEMA_VERSION,
            )


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda payload: payload["branches"][0]["frequencies"].__setitem__(0, float("nan")), "PHONON_FREQUENCY_NONFINITE"),
        (lambda payload: payload["source"].__setitem__("producer", "https://untrusted.invalid"), "PHONON_EXTERNAL_REFERENCE_FORBIDDEN"),
        (lambda payload: payload.__setitem__("unexpected", {"nested": {"too": {"deep": {"value": {"x": {"y": {"z": {"a": {"b": {"c": 1}}}}}}}}}}), "PHONON_CAP_EXCEEDED"),
    ],
)
def test_nonfinite_external_and_overdepth_payloads_are_inertly_rejected(
    tmp_path: Path, mutation: object, expected: str,
) -> None:
    payload = copy.deepcopy(json.loads(BAND_PATH.read_text(encoding="utf-8")))
    mutation(payload)  # type: ignore[operator]
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(payload, allow_nan=True), encoding="utf-8")
    with pytest.raises(ValueError, match=expected):
        map_normalized_phonon_resource(
            path, dataset_id="dataset_a", file_id="file_001",
            declared_kind="phonon_band", declared_contract_version=PHONON_BAND_SCHEMA_VERSION,
        )


def test_resource_ids_are_content_stable_and_project_scoped_storage_isolated(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    request_files = [
        _file(BAND_PATH, kind="phonon_band", version=PHONON_BAND_SCHEMA_VERSION),
        _file(DOS_PATH, kind="phonon_dos", version=PHONON_DOS_SCHEMA_VERSION),
    ]
    first = runtime.upload_dataset({"projectId": "project_a", "datasetName": "first", "files": request_files})
    second = runtime.upload_dataset({"projectId": "project_b", "datasetName": "second", "files": request_files})
    first_ids = first["profile"]["phononSummary"]["resourceIds"]
    second_ids = second["profile"]["phononSummary"]["resourceIds"]
    assert [item.split(":", 1)[1] for item in first_ids] == [item.split(":", 1)[1] for item in second_ids]
    assert all(item.startswith("dataset_0001_") for item in first_ids)
    assert all(item.startswith("dataset_0002_") for item in second_ids)
    assert all("projects/project_a/" in item["storageKey"] for item in first["normalizedExports"])
    assert all("projects/project_b/" in item["storageKey"] for item in second["normalizedExports"])


def test_typed_bundle_normalizes_source_order_only_after_matching_structure_proof(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path)
    band = json.loads(BAND_PATH.read_text(encoding="utf-8"))
    dos = json.loads(DOS_PATH.read_text(encoding="utf-8"))
    band["atom_ordering"] = "source_order"
    dos["atom_ordering"] = "source_order"
    payloads = [
        (
            "structure.vasp",
            b"""Si typed phonon companion
1.0
3.0 0.0 0.0
0.0 3.0 0.0
0.0 0.0 3.0
Si
2
Direct
0.0 0.0 0.0
0.25 0.25 0.25
""",
            None,
            None,
        ),
        (
            "band.json",
            json.dumps(band, separators=(",", ":")).encode(),
            "phonon_band",
            PHONON_BAND_SCHEMA_VERSION,
        ),
        (
            "dos.json",
            json.dumps(dos, separators=(",", ":")).encode(),
            "phonon_dos",
            PHONON_DOS_SCHEMA_VERSION,
        ),
    ]
    session = runtime.create_upload_session(
        "project_a",
        {
            "datasetName": "source-order typed phonon",
            "files": [
                {
                    "clientFileId": f"client-{index}",
                    "fileName": name,
                    "byteSize": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "importKind": kind,
                    "contractVersion": version,
                    "companionGroupId": "phonon_bundle",
                }
                for index, (name, payload, kind, version) in enumerate(payloads, start=1)
            ],
        },
    )

    async def upload() -> None:
        for file_record, (_, payload, _, _) in zip(
            session["files"], payloads, strict=True
        ):
            async def chunks(value: bytes = payload):
                yield value

            await runtime.put_upload_session_file(
                session["uploadSessionId"],
                file_record["fileId"],
                content_type="application/octet-stream",
                chunks=chunks(),
            )

    asyncio.run(upload())
    result = runtime.complete_upload_session(session["uploadSessionId"])
    assert result["inputTransport"]["scientificAdmissionStatus"] == "READY"
    assert result["inputTransport"]["objectKinds"] == [
        "PhononBand",
        "PhononDos",
        "Structure",
    ]
    phonon_exports = [
        item
        for item in result["normalizedExports"]
        if "obj_phonon_" in item["objectId"]
    ]
    assert len(phonon_exports) == 2
    normalized = [
        json.loads(runtime.artifact_storage.get_bytes(item["storageKey"]))
        for item in phonon_exports
    ]
    assert all(
        item["atom_ordering"] == "canonical_structure_order"
        for item in normalized
    )


def test_source_order_normalization_rejects_companion_species_mismatch(
    tmp_path: Path,
) -> None:
    payload = json.loads(BAND_PATH.read_text(encoding="utf-8"))
    payload["atom_ordering"] = "source_order"
    path = tmp_path / "source_order_band.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="PHONON_COMPANION_SPECIES_ORDER_MISMATCH"):
        map_normalized_phonon_resource(
            path,
            dataset_id="dataset_a",
            file_id="file_001",
            declared_kind="phonon_band",
            declared_contract_version=PHONON_BAND_SCHEMA_VERSION,
            canonical_species_order=["Na", "Na"],
        )
