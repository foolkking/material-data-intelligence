from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mdi_api.phase2_runtime import Phase2ProductRuntime
from mdi_artifact_core import PHONON_BAND_SCHEMA_VERSION, PHONON_DOS_SCHEMA_VERSION
from mdi_material_parsers import map_normalized_phonon_resource


ROOT = Path(__file__).resolve().parents[1]
BAND_PATH = ROOT / "docs/phase10h/fixtures/phonon_contract/stable_band.json"
DOS_PATH = ROOT / "docs/phase10h/fixtures/phonon_contract/total_dos.json"
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
    assert first["profile"]["phononSummary"]["resourceIds"] == second["profile"]["phononSummary"]["resourceIds"]
    assert all("projects/project_a/" in item["storageKey"] for item in first["normalizedExports"])
    assert all("projects/project_b/" in item["storageKey"] for item in second["normalizedExports"])
